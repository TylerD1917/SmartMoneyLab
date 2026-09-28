#!/usr/bin/env python3
"""Curva giornaliera dell'esperimento Reddit Retail Sentiment.

Perche' esiste
--------------
La pipeline settimanale salvava un punto per run, prendendo "l'ultimo prezzo
disponibile". Girando il lunedi' alle 06:00 UTC (mercato USA ancora chiuso),
quell'ultimo prezzo era la chiusura del VENERDI' precedente, salvata pero' con la
data del lunedi'. Verificato: il punto datato 2026-09-07 riproduce al centesimo
(94,30) le chiusure del 2026-09-04. Quindi le date erano spostate fino a 3 giorni
e la curva aveva 4 punti al mese, cioe' segmenti a pendenza costante.

Qui il valore viene ricalcolato per OGNI giorno di borsa dalle chiusure
ufficiali, concatenando i mesi:

    port(d) = port_al_ribilancio * Somma( w_i * TR_i(d) )
    TR_i(d) = (chiusura_i(d) + dividendi_i incassati dal ribilancio) / base_i

Total return su entrambi i lati: i 5 titoli incassano i dividendi, e il
benchmark usa IVV (ETF sull'S&P 500) invece di ^GSPC, che e' un indice di soli
prezzi e sottostimerebbe l'S&P di circa 1,2 punti l'anno.

Uso:  python scripts/lab/nav_daily_reddit.py [percorso json]
"""
import os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "public", "tools", "reddit-sentiment.json")
BENCH_TICKER = "IVV"


def last_complete_session(index):
    """Ultima sessione USA chiusa. La borsa chiude alle 20:00 UTC (ora legale) o
    21:00 (solare): prima di allora il prezzo del giorno e' un valore intraday."""
    now = dt.datetime.utcnow()
    ok = [d for d in index
          if now >= dt.datetime.fromisoformat(d.date().isoformat()) + dt.timedelta(hours=22)]
    return ok[-1] if ok else None


def download(tickers, start, end):
    import yfinance as yf
    import pandas as pd
    tickers = sorted(set(tickers))
    raw = yf.download(tickers, start=start, end=end, interval="1d",
                      auto_adjust=False, actions=False, progress=False, threads=False)
    close = raw["Close"] if "Close" in raw else raw
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    close = close.dropna(how="all")
    missing = [t for t in tickers if t not in close.columns]
    if missing:
        raise SystemExit(f"[nav_daily_reddit] ERRORE: nessun prezzo per {missing}.")
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


def segments(data):
    """Segmenti a squadra costante, uno per ribilancio, dal piu' vecchio.

    Ogni voce di history scritta da qui in avanti porta la data e i prezzi base.
    Per il primo mese (scritto prima di questa modifica) li ricaviamo dagli
    holdings correnti e dal primo punto NAV, che e' il ribilancio di quel mese.
    """
    pf = data["portfolio"]
    hist = pf.get("history", [])
    nav = pf.get("nav", [])
    out, salti = [], []
    for i, h in enumerate(hist):
        ultimo = (i == len(hist) - 1)
        if h.get("as_of") and h.get("basis"):
            out.append({"date": h["as_of"], "basis": h["basis"],
                        "bench_basis": h.get("bench_basis"),
                        "weights": h.get("weights") or {t: 1.0 / len(h["tickers"]) for t in h["tickers"]},
                        "_hist": i})
        elif ultimo and pf.get("holdings"):
            first = nav[0]["d"] if nav else None
            if not first:
                salti.append(h["month"]); continue
            out.append({"date": first,
                        "basis": {x["ticker"]: x["basis_price"] for x in pf["holdings"]},
                        "bench_basis": None,   # ricalcolato sulla chiusura di quella data
                        "weights": {x["ticker"]: x["weight"] for x in pf["holdings"]},
                        "_hist": i})
        else:
            salti.append(h["month"])
    if salti:
        print(f"[nav_daily_reddit] mesi senza prezzi base salvati, non ricostruibili: {salti}")
    return out


def rebuild(path=OUT, write=True):
    data = json.load(open(path, encoding="utf-8"))
    segs = segments(data)
    if not segs:
        raise SystemExit("[nav_daily_reddit] nessun segmento ricostruibile.")

    tick = {BENCH_TICKER}
    for s in segs:
        tick |= set(s["basis"])
    start = segs[0]["date"]
    end = (dt.date.today() + dt.timedelta(days=1)).isoformat()
    close, divs = download(tick, start, end)

    last = last_complete_session(close.index)
    if last is None:
        raise SystemExit("[nav_daily_reddit] nessuna sessione chiusa nel periodo.")
    close = close[close.index <= last]
    dates = [d.date().isoformat() for d in close.index]

    def tr(t, base, d0, d):
        """Fattore total return di t dalla data d0 alla data d."""
        px = float(close.loc[d, t])
        inc = sum(v for dd, v in divs.get(t, {}).items() if d0 < dd <= d)
        return (px + inc) / base

    port_ref, bench_ref = 100.0, 100.0
    serie = []
    for i, s in enumerate(segs):
        d0 = s["date"]
        # Il giorno del ribilancio il portafoglio detiene ancora la squadra
        # PRECEDENTE fino alla chiusura: quel punto lo emette il segmento vecchio,
        # e la squadra nuova parte dal giorno dopo. Trattare d0 come primo giorno
        # del nuovo segmento (rapporto 1) butterebbe via il rendimento fra
        # l'ultima chiusura precedente e il ribilancio.
        nxt = segs[i + 1]["date"] if i + 1 < len(segs) else None
        bb = s["bench_basis"] or float(close.loc[d0, BENCH_TICKER])
        # Ricuce nello storico i riferimenti del segmento ricavati dagli holdings
        # correnti. Senza questo, al ribilancio successivo quel mese non sarebbe
        # piu' l'ultimo e la sua parte di curva diventerebbe irrecuperabile.
        if write and s.get("_hist") is not None:
            h = data["portfolio"]["history"][s["_hist"]]
            h.setdefault("as_of", d0)
            h.setdefault("basis", s["basis"])
            h.setdefault("weights", s["weights"])
            if not h.get("bench_basis") or h.get("bench_basis_ticker") != BENCH_TICKER:
                h["bench_basis"] = bb
                h["bench_basis_ticker"] = BENCH_TICKER
        seg_dates = [d for d in dates
                     if (d >= d0 if i == 0 else d > d0) and (nxt is None or d <= nxt)]
        p_last = b_last = None
        for d in seg_dates:
            r = sum(w * tr(t, s["basis"][t], d0, d) for t, w in s["weights"].items())
            p_last = port_ref * r
            b_last = bench_ref * tr(BENCH_TICKER, bb, d0, d)
            serie.append({"d": d, "port": round(p_last, 2), "bench": round(b_last, 2)})
        if p_last is not None:
            # si concatena sui valori NON arrotondati: con un ribilancio al mese
            # l'arrotondamento a due decimali si accumulerebbe di segmento in segmento
            port_ref, bench_ref = p_last, b_last

    vecchio = {p["d"]: p for p in data["portfolio"].get("nav", [])}
    print(f"[nav_daily_reddit] {len(serie)} giorni dal {serie[0]['d']} al {serie[-1]['d']} "
          f"(prima: {len(vecchio)} punti settimanali)")
    print("[nav_daily_reddit] riconciliazione sui punti gia' pubblicati:")
    for d, p in sorted(vecchio.items()):
        n = next((x for x in serie if x["d"] == d), None)
        if n:
            print(f"    {d}  port {p['port']:7.2f} -> {n['port']:7.2f}   "
                  f"bench {p['bench']:7.2f} -> {n['bench']:7.2f}")
        else:
            print(f"    {d}  (non e' un giorno di borsa: punto eliminato)")

    if write:
        data["portfolio"]["nav"] = serie
        data["portfolio"]["nav_frequenza"] = "giornaliera (chiusure ufficiali)"
        data["benchmark_ticker"] = BENCH_TICKER
        data["rendimento"] = "total return (dividendi reinvestiti su entrambi i lati)"
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[nav_daily_reddit] scritto {path}")
    return serie


if __name__ == "__main__":
    rebuild(sys.argv[1] if len(sys.argv) > 1 else OUT, write=True)
