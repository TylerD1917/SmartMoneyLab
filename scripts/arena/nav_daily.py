#!/usr/bin/env python3
"""Motore NAV giornaliero dell'AI Investing Arena.

Che cosa calcola
----------------
Il NAV di ogni giorno di borsa di ogni partecipante, dalle chiusure ufficiali:

    NAV(d) = cassa(d) + Somma(qty_i * chiusura_i(d))

con la cassa che evolve per due voci:
  - dividendi, accreditati sulle posizioni long e addebitati sulle short alla
    data di stacco (senza, i modelli avrebbero un handicap sistematico rispetto
    ai benchmark, che usano prezzi total return);
  - costo di prestito sugli short, pro-rata die.

Si usano chiusure GREZZE (auto_adjust=False): i prezzi aggiustati vengono
riscalati a ogni nuovo dividendo, quindi una curva costruita su di essi
cambierebbe da sola nel tempo. Cosi' il passato resta fermo.

La regola che tiene insieme tutto
---------------------------------
QUESTO MODULO E' UNA FUNZIONE PURA DEGLI SNAPSHOT DI ALLOCAZIONE.

L'unico stato durevole dell'arena sono gli snapshot in state/positions/: una
fotografia di cassa e quantita' scritta da settle.py subito dopo ogni
riallocazione, mai piu' riscritta. Tutto il resto (le serie NAV, arena.json, il
CSV pubblico) e' ricalcolato da zero a ogni esecuzione e non viene mai riletto
come input.

La versione precedente violava questa regola in tre punti, ed e' il motivo per
cui il 2026-10-06 la classifica si e' azzerata:

  1. scartava gli snapshot marcati "_bootstrap", cioe' proprio quelli del primo
     segmento: dopo la seconda riallocazione restava un segmento solo e la
     storia precedente spariva;
  2. faceva partire la curva dalla data dell'ultimo settle. Quando quella data
     non ha ancora una sessione chiusa (il pacchetto del 2026-10-06 girava
     prima della chiusura di quel giorno) la serie usciva VUOTA;
  3. riscriveva pf["cash"] nello stato a ogni ricostruzione, rendendo il
     risultato dipendente da quante volte lo script era girato in passato.

Qui il segmento attivo viene scelto per ogni singola data di borsa ("l'ultimo
snapshot con data <= d"). Uno snapshot datato nel futuro, o in un giorno non
ancora chiuso, semplicemente non e' ancora attivo: il segmento precedente
continua fino in fondo e la curva non si interrompe.

Uso
---
  python scripts/arena/nav_daily.py            # ricostruisce tutte le serie
  python scripts/arena/nav_daily.py --dry-run  # calcola e stampa, non scrive
"""
from __future__ import annotations

import os
import sys
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

SNAP_DIR = "positions"          # state/positions/positions_{mid}_{YYYY-MM-DD}.json
ORE_CHIUSURA = 22               # UTC: dopo le 22 la sessione americana e' chiusa
                                # sia in ora legale (20:00) sia in ora solare (21:00)


# ---------------------------------------------------------------- prezzi
def scarica(tickers, start, end):
    """Chiusure grezze e dividendi per data. Ritorna (close_df, dividendi)."""
    import yfinance as yf
    import pandas as pd

    tickers = sorted(set(tickers))
    if not tickers:
        raise SystemExit("[nav] nessun ticker da scaricare")
    raw = yf.download(tickers, start=start, end=end, interval="1d",
                      auto_adjust=False, actions=False, progress=False, threads=False)
    close = raw["Close"] if "Close" in raw else raw
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    close = close.dropna(how="all")

    mancanti = [t for t in tickers if t not in close.columns]
    if mancanti:
        raise SystemExit(f"[nav] ERRORE: nessun prezzo per {mancanti}. "
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


def sessioni_chiuse(close, adesso=None):
    """Tiene solo le sessioni gia' chiuse: il prezzo del giorno in corso e' un
    valore intraday, non riproducibile da chi rifa' il conto domani."""
    adesso = adesso or dt.datetime.utcnow()
    tieni = [adesso >= dt.datetime.fromisoformat(d.date().isoformat())
             + dt.timedelta(hours=ORE_CHIUSURA) for d in close.index]
    scartate = [d.date().isoformat() for d, k in zip(close.index, tieni) if not k]
    if scartate:
        print(f"[nav] sessione non ancora chiusa, esclusa: {', '.join(scartate)}")
    return close[tieni]


# ---------------------------------------------------------------- snapshot
def snap_path(cfg, mid, date):
    return ac.state_path(cfg, SNAP_DIR, f"positions_{mid}_{date}.json")


def write_snapshot(cfg, mid, date, pf):
    """Fotografia di cassa e quantita' all'apertura di un segmento.

    La scrive settle.py subito dopo aver eseguito gli ordini. E' l'unico dato
    durevole da cui dipende tutta la ricostruzione: non va mai riscritta a
    posteriori, altrimenti il passato cambia.
    """
    ac.write_json(snap_path(cfg, mid, date), {
        "date": date,
        "cash": float(pf["cash"]),
        "positions": {t: {"qty": p["qty"], "avg_price": p.get("avg_price")}
                      for t, p in pf["positions"].items()}})


def leggi_segmenti(cfg, mid):
    """Tutti gli snapshot di un partecipante, in ordine di data.

    Nessun filtro: un segmento salvato e' un segmento, qualunque etichetta
    porti. Gli snapshot piu' vecchi possono avere il campo "_bootstrap" di una
    versione precedente dello script e vengono letti normalmente.
    """
    d = os.path.join(cfg["_root"], cfg["state_dir"], SNAP_DIR)
    if not os.path.isdir(d):
        return []
    pre = f"positions_{mid}_"
    per_data = {}
    for fn in sorted(os.listdir(d)):
        if fn.startswith(pre) and fn.endswith(".json"):
            snap = ac.read_json(os.path.join(d, fn))
            if snap and snap.get("date"):
                per_data[snap["date"]] = snap
    return [per_data[k] for k in sorted(per_data)]


# ---------------------------------------------------------------- NAV
def serie_nav(segmenti, close, divs, cfg):
    """NAV giornaliero: per ogni sessione vale l'ultimo segmento gia' aperto.

    Uno snapshot con data successiva all'ultima sessione chiusa non e' ancora
    attivo e non interrompe la curva: e' il caso di una riallocazione decisa
    prima della chiusura del giorno stesso.
    """
    if not segmenti:
        return []
    rate = cfg["costs"]["short_borrow_annual"]
    date = [d.date().isoformat() for d in close.index]
    inizio = segmenti[0]["date"]

    out = []
    i = -1                 # indice del segmento attivo
    cash = 0.0
    pos = {}
    prec = None
    for d in date:
        if d < inizio:
            continue
        # avanza al segmento piu' recente gia' aperto a questa data
        nuovo = i
        while nuovo + 1 < len(segmenti) and segmenti[nuovo + 1]["date"] <= d:
            nuovo += 1
        if nuovo != i:
            i = nuovo
            cash = float(segmenti[i]["cash"])
            pos = segmenti[i]["positions"]
            prec = None                      # il segmento riparte dalla sua cassa
        row = close.loc[d]
        if prec is not None:
            giorni = (dt.date.fromisoformat(d) - dt.date.fromisoformat(prec)).days
            pr = close.loc[prec]
            cash -= sum(abs(p["qty"] * float(pr[t])) * rate * giorni / 365.0
                        for t, p in pos.items() if p["qty"] < 0)
        for t, p in pos.items():
            v = divs.get(t, {}).get(d)
            if v:
                cash += p["qty"] * v         # qty<0 (short) -> addebito
        out.append((d, cash + sum(p["qty"] * float(row[t]) for t, p in pos.items())))
        prec = d
    return out


def serie_benchmark(cfg, close, divs, start, capitale, ingresso=None):
    """Benchmark trattati come i portafogli: quote comprate allo start, dividendi
    accreditati, cosi' il confronto e' total return su entrambi i lati.

    Il prezzo di ingresso arriva dal packet del giorno di partenza, lo stesso
    listino che i modelli hanno visto quando hanno deciso: comprare alla
    chiusura dello stesso giorno regalerebbe ai modelli il movimento intraday
    del primo giorno.
    """
    ingresso = ingresso or {}
    out, usati = {}, {}
    for key, tk in cfg["benchmarks"].items():
        if tk not in close.columns:
            continue
        s = close[tk].dropna()
        s = s[s.index.astype(str) >= start]
        if s.empty:
            continue
        p0 = float(ingresso[tk]) if ingresso.get(tk) else float(s.iloc[0])
        usati[key] = {"ticker": tk, "price": p0,
                      "fonte": "packet" if ingresso.get(tk) else "chiusura"}
        qty = capitale / p0
        cash = 0.0
        ser = []
        for ts, px in s.items():
            d = ts.date().isoformat()
            v = divs.get(tk, {}).get(d)
            if v:
                cash += qty * v
            ser.append((d, cash + qty * float(px)))
        out[key] = ser
    return out, usati


# ---------------------------------------------------------------- driver
def partecipanti(cfg):
    return [m["id"] for m in cfg["models"]] + (["random"] if cfg.get("random_control") else [])


def rebuild(cfg, write=True):
    """Ricostruisce tutte le serie. Non legge mai le serie precedenti."""
    modelli = partecipanti(cfg)
    segmenti = {mid: leggi_segmenti(cfg, mid) for mid in modelli}

    senza = [m for m, s in segmenti.items() if not s]
    if senza:
        raise SystemExit(
            f"[nav] ERRORE: nessuno snapshot di allocazione per {', '.join(senza)}.\n"
            "       Gli snapshot in state/positions/ sono l'unico stato durevole "
            "dell'arena: senza, la curva non e' ricostruibile.\n"
            "       Se e' il primo avvio: python scripts/arena/run_period.py init "
            "e poi una decisione.")

    start = min(s[0]["date"] for s in segmenti.values())
    end = (dt.date.today() + dt.timedelta(days=1)).isoformat()

    tick = set(cfg["benchmarks"].values())
    for s in segmenti.values():
        for snap in s:
            tick |= set(snap["positions"])

    close, divs = scarica(tick, start, end)
    close = sessioni_chiuse(close)
    if close.empty:
        raise SystemExit(
            f"[nav] ERRORE: nessuna sessione di borsa chiusa dal {start} a oggi.\n"
            "       Succede se il primo snapshot e' datato in un giorno non ancora "
            "chiuso: non c'e' niente da valorizzare, ma soprattutto non va "
            "pubblicata una classifica vuota al posto di quella buona.")
    ultima = close.index[-1].date().isoformat()

    serie = {mid: serie_nav(segmenti[mid], close, divs, cfg) for mid in modelli}

    # un segmento nuovo non ancora attivo e' normale; una serie vuota no
    vuote = [m for m, s in serie.items() if not s]
    if vuote:
        raise SystemExit(
            f"[nav] ERRORE: serie vuota per {', '.join(vuote)} con sessioni fino al "
            f"{ultima}.\n       Primo segmento: "
            + ", ".join(f"{m}={segmenti[m][0]['date']}" for m in vuote))

    pk = (ac.read_json(ac.state_path(cfg, "packets", f"packet_{start}.json"))
          or ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json")) or {})
    ingresso = ({i["ticker"]: i.get("price") for i in pk.get("instruments", [])}
                if pk.get("as_of") == start else {})
    bser, busati = serie_benchmark(cfg, close, divs, start, cfg["capital"], ingresso)
    serie.update(bser)

    _riepilogo(cfg, serie, segmenti, modelli, start, ultima, len(close.index))

    if write:
        ac.write_json(ac.state_path(cfg, "benchmark_baseline.json"),
                      {"as_of": start, "capital": cfg["capital"],
                       "prices": {k: v["price"] for k, v in busati.items()},
                       "ingresso": busati})
        for key, ser in serie.items():
            with open(ac.nav_file(cfg, key), "w", encoding="utf-8") as f:
                f.write("date,nav\n" + "\n".join(f"{d},{round(v, 2)}" for d, v in ser) + "\n")
        print(f"[nav] scritte {len(serie)} serie in "
              f"{os.path.dirname(ac.nav_file(cfg, 'x'))}")
    return serie


def _riepilogo(cfg, serie, segmenti, modelli, start, ultima, n_sessioni):
    print(f"\n[nav] dal {start} all'ultima chiusura {ultima}: "
          f"{n_sessioni} sessioni di borsa")
    for mid in modelli:
        date_seg = [s["date"] for s in segmenti[mid]]
        attivi = [d for d in date_seg if d <= ultima]
        futuri = [d for d in date_seg if d > ultima]
        ser = serie[mid]
        nota = f"  (snapshot non ancora attivo: {', '.join(futuri)})" if futuri else ""
        print(f"    {mid:7s} {len(ser):3d} giorni | {len(attivi)} segmenti "
              f"({', '.join(attivi)}) | {ser[0][1]:,.0f} -> {ser[-1][1]:,.0f}{nota}")
    for key in cfg["benchmarks"]:
        if key in serie and serie[key]:
            ser = serie[key]
            print(f"    {key:7s} {len(ser):3d} giorni | "
                  f"{ser[0][1]:,.0f} -> {ser[-1][1]:,.0f}")


def main():
    cfg = ac.load_config()
    args = [a for a in sys.argv[1:] if a not in ("rebuild", "extend")]   # alias storici
    rebuild(cfg, write="--dry-run" not in args)


if __name__ == "__main__":
    main()
