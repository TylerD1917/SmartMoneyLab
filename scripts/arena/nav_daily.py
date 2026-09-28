#!/usr/bin/env python3
"""Motore NAV giornaliero dell'AI Investing Arena.

Perche' esiste
--------------
Fino al 2026-09-28 il NAV veniva marcato una volta a settimana chiamando
yf_prices(), che restituisce l'ULTIMO prezzo disponibile: se la Action girava a
mercato aperto, il valore salvato era uno snapshot intraday. Verificato sul mark
del 2026-09-21: il NAV pubblicato (97.980,96 per claude) corrisponde ai prezzi
delle 18:00 UTC, mentre la chiusura ufficiale dello stesso giorno dava
97.674,45. Un numero del genere non e' riproducibile da un lettore.

Questo modulo ricostruisce il NAV di OGNI giorno di borsa dalle chiusure
ufficiali, in modo deterministico e ripetibile:

  NAV(d) = cassa(d) + Somma(qty_i * chiusura_i(d))

con la cassa che evolve per due voci che prima venivano ignorate o approssimate:
  - dividendi: accreditati sulle posizioni long e addebitati sulle short alla
    data di stacco. Prima non venivano contati affatto, mentre i benchmark
    usavano prezzi aggiustati (quindi total return): i modelli partivano con un
    handicap sistematico pari al dividend yield del loro portafoglio.
  - costo di prestito sugli short: pro-rata die invece che a blocchi settimanali.

Usiamo chiusure GREZZE (auto_adjust=False) e non aggiustate: i prezzi aggiustati
vengono riscalati a ogni nuovo dividendo, quindi una curva storica costruita su
di essi cambierebbe da sola nel tempo. Cosi' il passato resta fermo.

Uso
---
  python scripts/arena/nav_daily.py rebuild    # ricostruisce tutta la storia
  python scripts/arena/nav_daily.py extend     # aggiorna fino all'ultima chiusura
"""
import os, sys, json, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

SNAP_DIR = "positions"          # state/positions/positions_{mid}_{YYYY-MM-DD}.json


# ---------------------------------------------------------------- prezzi
def _download(tickers, start, end):
    """Chiusure grezze + dividendi per data. Ritorna (close_df, dividends_dict)."""
    import yfinance as yf
    import pandas as pd

    tickers = sorted(set(tickers))
    if not tickers:
        return None, {}
    raw = yf.download(tickers, start=start, end=end, interval="1d",
                      auto_adjust=False, actions=False,
                      progress=False, threads=False)
    close = raw["Close"] if "Close" in raw else raw
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    close = close.dropna(how="all")

    missing = [t for t in tickers if t not in close.columns]
    if missing:
        raise SystemExit(f"[nav_daily] ERRORE: nessun prezzo per {missing}. "
                         "Non ricostruisco una curva con buchi silenziosi.")

    divs = {}
    for t in tickers:
        try:
            s = yf.Ticker(t).dividends
        except Exception:
            s = None
        if s is None or len(s) == 0:
            continue
        for ts, v in s.items():
            d = ts.date().isoformat()
            if start <= d <= end:
                divs.setdefault(t, {})[d] = float(v)
    return close, divs


# ---------------------------------------------------------------- snapshot
def snap_path(cfg, mid, date):
    return ac.state_path(cfg, SNAP_DIR, f"positions_{mid}_{date}.json")


def write_snapshot(cfg, mid, date, pf):
    """Fotografia di cassa e posizioni all'apertura di un segmento (dopo il settle)."""
    ac.write_json(snap_path(cfg, mid, date), {
        "date": date, "cash": float(pf["cash"]),
        "positions": {t: {"qty": p["qty"], "avg_price": p.get("avg_price")}
                      for t, p in pf["positions"].items()}})


def read_snapshots(cfg, mid):
    """Snapshot di posizioni ordinati per data (inizio di ogni segmento)."""
    d = os.path.join(cfg["_root"], cfg["state_dir"], SNAP_DIR)
    if not os.path.isdir(d):
        return []
    out = []
    pre = f"positions_{mid}_"
    for fn in sorted(os.listdir(d)):
        if fn.startswith(pre) and fn.endswith(".json"):
            snap = ac.read_json(os.path.join(d, fn))
            if snap:
                out.append(snap)
    out.sort(key=lambda s: s["date"])
    return out


def bootstrap_snapshot(cfg, mid, pf, close, write=True):
    """Crea lo snapshot del segmento corrente per un portafoglio che non ne ha.

    Le posizioni attuali valgono dall'ultimo settle in poi. La cassa attuale e'
    pero' gia' stata decurtata dai borrow fee applicati dai mark successivi:
    li ricalcoliamo sulle chiusure e li restituiamo, cosi' lo snapshot e' la
    cassa REALE subito dopo il settle.
    """
    settles = [h["date"] for h in pf.get("history", []) if h.get("action") == "settle"]
    if not settles:
        return None
    start = settles[-1]
    if len(settles) > 1:
        print(f"[nav_daily] ATTENZIONE {mid}: {len(settles)} settle in storia ma nessuno "
              f"snapshot salvato; ricostruisco solo dal {start}. I segmenti precedenti "
              f"restano quelli settimanali gia' pubblicati.")

    rate = cfg["costs"]["short_borrow_annual"]
    mark_days = cfg["cadence"]["mark_days"]
    cash = pf["cash"]
    for h in pf.get("history", []):
        if h.get("action") != "mark" or h["date"] <= start:
            continue
        d = h["date"]
        idx = close.index.astype(str)
        # se il mark cade su una sessione non ancora chiusa (esclusa sopra) usiamo
        # l'ultima disponibile: serve solo a stimare un fee di pochi centesimi
        row = close.loc[d] if d in idx else close.iloc[-1]
        fee = sum(abs(p["qty"] * float(row[t])) * rate * mark_days / 365.0
                  for t, p in pf["positions"].items() if p["qty"] < 0)
        cash += fee          # annulla il fee a blocchi: lo riapplichiamo pro-rata die
    snap = {"date": start, "cash": cash,
            "positions": {t: {"qty": p["qty"], "avg_price": p.get("avg_price")}
                          for t, p in pf["positions"].items()},
            "_bootstrap": True}
    if write:
        ac.write_json(snap_path(cfg, mid, start), snap)
    return snap


# ---------------------------------------------------------------- NAV
def nav_series(segments, close, divs, cfg, end=None):
    """NAV giornaliero concatenando i segmenti a posizioni costanti."""
    rate = cfg["costs"]["short_borrow_annual"]
    dates = [d.date().isoformat() for d in close.index]
    out = []
    for i, seg in enumerate(segments):
        start = seg["date"]
        stop = segments[i + 1]["date"] if i + 1 < len(segments) else (end or "9999-12-31")
        cash = float(seg["cash"])
        pos = seg["positions"]
        prev = None
        for d in dates:
            if d < start or d >= stop:
                continue
            row = close.loc[d]
            if prev is not None:
                days = (dt.date.fromisoformat(d) - dt.date.fromisoformat(prev)).days
                # borrow pro-rata die sul nozionale short del giorno precedente
                pr = close.loc[prev]
                fee = sum(abs(p["qty"] * float(pr[t])) * rate * days / 365.0
                          for t, p in pos.items() if p["qty"] < 0)
                cash -= fee
            # dividendi con stacco in questa data
            for t, p in pos.items():
                v = divs.get(t, {}).get(d)
                if v:
                    cash += p["qty"] * v      # qty<0 (short) -> addebito
            nav = cash + sum(p["qty"] * float(row[t]) for t, p in pos.items())
            out.append((d, nav))
            prev = d
        if segments[i:i + 1] and prev is not None:
            seg["_cash_end"] = cash
    return out


def benchmark_series(cfg, close, divs, start, capital, entry=None):
    """Benchmark trattati come i portafogli: quote comprate allo start,
    dividendi accreditati. Cosi' il confronto e' total return su entrambi i lati.

    Il prezzo di ingresso arriva dal packet del giorno di partenza, cioe' lo
    STESSO listino che i modelli hanno visto quando hanno deciso. Comprare il
    benchmark alla chiusura dello stesso giorno regalerebbe (o addebiterebbe) ai
    modelli il movimento intraday del primo giorno.
    """
    entry = entry or {}
    out, used = {}, {}
    for key, tk in cfg["benchmarks"].items():
        if tk not in close.columns:
            continue
        s = close[tk].dropna()
        s = s[s.index.astype(str) >= start]
        if s.empty:
            continue
        p0 = float(entry[tk]) if entry.get(tk) else float(s.iloc[0])
        used[key] = {"ticker": tk, "price": p0,
                     "fonte": "packet" if entry.get(tk) else "chiusura"}
        qty = capital / p0
        cash = 0.0
        ser = []
        for ts, px in s.items():
            d = ts.date().isoformat()
            v = divs.get(tk, {}).get(d)
            if v:
                cash += qty * v
            ser.append((d, cash + qty * float(px)))
        out[key] = ser
    return out, used


# ---------------------------------------------------------------- driver
def rebuild(cfg, write=True):
    import pandas as pd

    participants = [m["id"] for m in cfg["models"]] + (["random"] if cfg.get("random_control") else [])
    pfs = {}
    for mid in participants:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json"))
        if pf:
            pfs[mid] = pf
    if not pfs:
        raise SystemExit("[nav_daily] nessun portafoglio in stato: lancia prima run_period.py init")

    start = min(pf.get("created") or dt.date.today().isoformat() for pf in pfs.values())
    end = (dt.date.today() + dt.timedelta(days=1)).isoformat()

    tick = set(cfg["benchmarks"].values())
    for mid in pfs:
        for snap in read_snapshots(cfg, mid):
            tick |= set(snap["positions"])
        tick |= set(pfs[mid]["positions"])

    close, divs = _download(tick, start, end)

    # Scarta la sessione in corso: la borsa USA chiude alle 20:00 UTC (ora legale)
    # o 21:00 (ora solare). Finche' non e' chiusa, il prezzo di yfinance e' un
    # valore intraday - esattamente il difetto che questo modulo elimina.
    now = dt.datetime.utcnow()
    keep = [now >= dt.datetime.fromisoformat(d.date().isoformat()) + dt.timedelta(hours=22)
            for d in close.index]
    scartate = [d.date().isoformat() for d, k in zip(close.index, keep) if not k]
    if scartate:
        print(f"[nav_daily] sessione non ancora chiusa, esclusa: {', '.join(scartate)}")
    close = close[keep]
    if close.empty:
        raise SystemExit("[nav_daily] nessuna sessione chiusa nel periodo.")
    last_session = close.index[-1].date().isoformat()

    # segmenti: snapshot salvati, con bootstrap del segmento corrente se assenti
    series = {}
    for mid, pf in pfs.items():
        segs = [x for x in read_snapshots(cfg, mid) if not x.get("_bootstrap")]
        settles = [h["date"] for h in pf.get("history", []) if h.get("action") == "settle"]
        if settles and (not segs or segs[-1]["date"] != settles[-1]):
            s = bootstrap_snapshot(cfg, mid, pf, close, write=write)
            if s:
                segs = [x for x in segs if x["date"] != s["date"]] + [s]
                segs.sort(key=lambda x: x["date"])
        if not segs:
            print(f"[nav_daily] {mid}: nessun segmento ricostruibile, salto.")
            continue
        series[mid] = nav_series(segs, close, divs, cfg)
        # la cassa aggiornata (dividendi + borrow pro-rata die) torna nello stato
        if write and segs[-1].get("_cash_end") is not None:
            pf["cash"] = round(float(segs[-1]["_cash_end"]), 6)
            ac.write_json(ac.state_path(cfg, f"portfolio_{mid}.json"), pf)

    # prezzi di ingresso dei benchmark: lo stesso listino visto dai modelli
    pk = (ac.read_json(ac.state_path(cfg, "packets", f"packet_{start}.json"))
          or ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json")) or {})
    entry = ({i["ticker"]: i.get("price") for i in pk.get("instruments", [])}
             if pk.get("as_of") == start else {})
    bser, bused = benchmark_series(cfg, close, divs, start, cfg["capital"], entry)
    series.update(bser)

    base = {"as_of": start, "capital": cfg["capital"],
            "prices": {k: v["price"] for k, v in bused.items()},
            "ingresso": bused}
    if write:
        ac.write_json(ac.state_path(cfg, "benchmark_baseline.json"), base)

    # riconciliazione: cosa cambia rispetto a quanto era pubblicato
    print(f"\n[nav_daily] start={start}  ultima chiusura={last_session}  "
          f"giorni di borsa={len(close.index)}")
    print("[nav_daily] riconciliazione con i valori settimanali gia' pubblicati:")
    for key in sorted(series):
        old = dict(ac.read_nav(cfg, key))
        new = dict(series[key])
        rows = [(d, old[d], new[d]) for d in sorted(old) if d in new]
        if not rows:
            print(f"    {key:7s} nessun punto in comune (serie nuova, {len(new)} giorni)")
            continue
        worst = max(rows, key=lambda r: abs(r[2] - r[1]))
        print(f"    {key:7s} {len(new):3d} giorni | scostamento max il {worst[0]}: "
              f"{worst[1]:,.2f} -> {worst[2]:,.2f} ({(worst[2]/worst[1]-1)*100:+.2f}%)")

    if write:
        for key, ser in series.items():
            path = ac.nav_file(cfg, key)
            with open(path, "w", encoding="utf-8") as f:
                f.write("date,nav\n" + "\n".join(f"{d},{round(v,2)}" for d, v in ser) + "\n")
        print(f"[nav_daily] scritte {len(series)} serie in {os.path.dirname(ac.nav_file(cfg,'x'))}")
    return series


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "rebuild"
    if mode not in ("rebuild", "extend"):
        sys.exit("uso: nav_daily.py [rebuild|extend]")
    rebuild(ac.load_config(), write=True)
