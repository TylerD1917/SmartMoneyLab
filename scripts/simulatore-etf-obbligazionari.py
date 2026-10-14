# -*- coding: utf-8 -*-
"""
SmartMoneyLab — motore del simulatore "quanto rende un ETF obbligazionario"
===========================================================================

Precalcola, per ciascuna gamba sintetica dello studio
`quanto-rendono-etf-obbligazionari` e per ogni orizzonte da 5 a 20 anni, la
relazione fra il RENDIMENTO A SCADENZA DEL GIORNO IN CUI COMPRI e il rendimento
annuo effettivamente ottenuto dopo.

PERCHE' NON BASTA UN NUMERO
---------------------------
La relazione non e' "il rendimento di oggi predice i dieci anni dopo". E':
predice quello che otterrai SE TIENI ABBASTANZA A LUNGO, e "abbastanza" dipende
dalla duration. Sui Treasury 7-10 (duration ~6,8) il risultato a dieci anni
finisce entro due punti dal rendimento iniziale nell'86% dei casi; sui Treasury
20+ (duration ~13,5) solo nel 49%, ma a vent'anni si risale all'83%. Il punto di
svolta cade intorno al doppio della duration, che e' il comportamento atteso di
un fondo a duration costante. Il simulatore esiste per mostrare QUESTO, non per
sparare una previsione.

COSA SCRIVE
-----------
public/tools/etf-obbligazionari-rendimenti.json
  gambe[].orizzonti[]  n, pendenza, intercetta, r2, quantili dei residui,
                       quota entro 1 e 2 punti dal rendimento iniziale
  gambe[].rendimento   valore di riferimento di oggi, con data, fonte e link
  gambe[].campo_x      minimo e massimo del rendimento storico: fuori da li'
                       la retta estrapola e il front-end deve dirlo

I rendimenti di riferimento si scaricano da FRED (Treasury, giornalieri) e dalla
BCE (area euro e Italia). Con --offline si riusa quanto gia' presente nel JSON:
le statistiche storiche non dipendono dalla rete, solo i valori di oggi.

Uso:  python scripts/simulatore-etf-obbligazionari.py [--offline]
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import argparse
import subprocess
import tempfile
import datetime as dt
import importlib.util

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STUDIO = os.path.join(HERE, "quanto-rendono-etf-obbligazionari.py")
OUT = os.path.join(ROOT, "public", "tools", "etf-obbligazionari-rendimenti.json")

ORIZZONTI = list(range(5, 21))
SOGLIA_SUFFICIENTE = 75.0          # quota entro 2 punti che consideriamo "ci siamo"

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
BCE = ("https://data-api.ecb.europa.eu/service/data/{}"
       "?lastNObservations=1&format=csvdata")

# Ogni gamba: come si chiama nello studio, cosa replica, dove si legge il
# rendimento di oggi e quali ETF reali le somigliano. I link sono alla SERIE
# ufficiale, non a una pagina commerciale che cambia indirizzo ogni anno.
GAMBE = [
    {
        "id": "usa-7-10",
        "nome": "Treasury USA 7-10 anni",
        "gamba": "USA 7-10",
        "valuta": "USD",
        "descrizione": "Titoli di Stato americani a media scadenza.",
        "etf": [{"ticker": "IEF", "nome": "iShares 7-10 Year Treasury Bond ETF", "ter": 0.15},
                {"ticker": "SXRM", "nome": "iShares $ Treasury Bond 7-10yr UCITS ETF", "ter": 0.07}],
        "fonte": {"nome": "Treasury constant maturity 7 e 10 anni, FRED",
                  "link": "https://fred.stlouisfed.org/series/DGS10"},
    },
    {
        "id": "usa-20",
        "nome": "Treasury USA oltre 20 anni",
        "gamba": "USA 20+",
        "valuta": "USD",
        "descrizione": "Titoli di Stato americani lunghissimi.",
        "etf": [{"ticker": "TLT", "nome": "iShares 20+ Year Treasury Bond ETF", "ter": 0.15}],
        "fonte": {"nome": "Treasury constant maturity 20 anni, FRED",
                  "link": "https://fred.stlouisfed.org/series/DGS20"},
    },
    {
        "id": "euro-7-10",
        "nome": "Governativi area euro 7-10 anni",
        "gamba": "Area euro 7-10",
        "valuta": "EUR",
        "descrizione": "Titoli di Stato dell'area euro a media scadenza.",
        "etf": [{"ticker": "SXRQ", "nome": "iShares Euro Government Bond 7-10yr UCITS ETF", "ter": 0.20}],
        "fonte": {"nome": "Curva dei rendimenti area euro, tutti gli emittenti, 10 anni, BCE",
                  "link": "https://data.ecb.europa.eu/data/datasets/YC"},
    },
    {
        "id": "italia-15",
        "nome": "Titoli di Stato italiani oltre 15 anni",
        "gamba": "Italia 15+",
        "valuta": "EUR",
        "descrizione": "BTP lunghi. La gamba piu' fragile dello studio: prima del "
                       "novembre 1993 descrive uno strumento che in Italia non esisteva.",
        "etf": [{"ticker": "IBGL", "nome": "iShares € Govt Bond 15-30yr UCITS ETF", "ter": 0.15}],
        "fonte": {"nome": "Tasso d'interesse a lungo termine per l'Italia, BCE",
                  "link": "https://data.ecb.europa.eu/data/datasets/IRS"},
    },
]


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ------------------------------------------------------------- rendimenti oggi
def _scarica(url):
    """Scarica con curl, non con pandas.

    Il proxy di rete risponde 500 alla richiesta che urllib manda per conto di
    pandas, mentre curl passa: tanto vale usare lui e leggere il file da disco.
    """
    if not shutil.which("curl"):
        raise SystemExit("[sim] serve curl per scaricare i rendimenti, oppure usa --offline")
    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    f.close()
    r = subprocess.run(["curl", "-sS", "--fail", "-m", "40", "-o", f.name, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        os.unlink(f.name)
        raise SystemExit(f"[sim] download fallito: {url}\n       {r.stderr.strip()}\n"
                         "       con --offline si riusano i valori gia' nel JSON")
    return f.name


def _fred(serie):
    tmp = _scarica(FRED.format(serie))
    d = pd.read_csv(tmp); os.unlink(tmp)
    d.columns = ["data", "v"]
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    d = d.dropna()
    return float(d["v"].iloc[-1]), str(d["data"].iloc[-1])[:10]


def _bce(chiave):
    tmp = _scarica(BCE.format(chiave))
    d = pd.read_csv(tmp, low_memory=False); os.unlink(tmp)
    return float(d["OBS_VALUE"].iloc[-1]), str(d["TIME_PERIOD"].iloc[-1])


def rendimenti_oggi():
    """Rendimento di riferimento per gamba, il piu' fresco disponibile.

    La gamba USA 7-10 vale un titolo a 8,5 anni: si interpola fra il settennale
    e il decennale, come fa lo studio. Per l'area euro la serie storica e' OCSE
    (media mensile) mentre qui si usa la curva BCE, piu' fresca: sulla
    sovrapposizione 2015-2026 le due differiscono in media di 0,07 punti, sotto
    la risoluzione di tutto il resto, quindi non si corregge nulla e lo scarto
    resta scritto nel JSON. Per l'Italia le due serie coincidono (scarto 0,000).
    """
    d7, g7 = _fred("DGS7")
    d10, g10 = _fred("DGS10")
    d20, g20 = _fred("DGS20")
    ez, gez = _bce("YC/B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y")
    itl, git = _bce("IRS/M.IT.L.L40.CI.0000.EUR.N.Z")
    return {
        "usa-7-10": {"valore": round(d7 + (d10 - d7) * (8.5 - 7) / 3, 2),
                     "data": max(g7, g10), "scarto_vs_serie_storica": 0.0},
        "usa-20": {"valore": round(d20, 2), "data": g20, "scarto_vs_serie_storica": 0.0},
        "euro-7-10": {"valore": round(ez, 2), "data": gez, "scarto_vs_serie_storica": 0.07},
        "italia-15": {"valore": round(itl, 2), "data": git, "scarto_vs_serie_storica": 0.0},
    }


# ------------------------------------------------------------------ statistica
def statistiche(serie_nav, rendimento, h):
    """Regressione del rendimento annuo a h anni sul rendimento a scadenza di
    partenza, piu' la dispersione storica intorno alla retta."""
    fut = M.finestre(serie_nav, h, passo=1)
    k = fut.index.intersection(rendimento.index)
    if len(k) < 40:
        return None
    x, z = rendimento[k].to_numpy(float), fut[k].to_numpy(float)
    b, a = np.polyfit(x, z, 1)
    r = float(np.corrcoef(x, z)[0, 1])
    res = z - (a + b * x)
    q = np.percentile(res, [10, 25, 50, 75, 90])
    return {
        "anni": h, "n": int(len(k)),
        "pendenza": round(float(b), 3), "intercetta": round(float(a), 3),
        "r2": round(r * r, 3),
        "residui": {"p10": round(float(q[0]), 2), "p25": round(float(q[1]), 2),
                    "p50": round(float(q[2]), 2), "p75": round(float(q[3]), 2),
                    "p90": round(float(q[4]), 2)},
        "entro1": round(100 * float(np.mean(np.abs(z - x) <= 1)), 1),
        "entro2": round(100 * float(np.mean(np.abs(z - x) <= 2)), 1),
        "da": str(k.min()), "a": str(k.max()),
    }


def duration(gamba_m, y):
    """Duration modificata del titolo alla pari che la gamba compra ogni mese."""
    p = lambda yy: M.prezzo(yy, y, gamba_m)
    return (p(y - 1e-4) - p(y + 1e-4)) / (2e-4) / p(y)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true",
                    help="Non scarica i rendimenti di oggi: riusa quelli gia' nel JSON.")
    args = ap.parse_args()

    gambe_nav, _extra, rendimenti = M.costruisci()
    durate = {"USA 7-10": 8.5, "USA 20+": 24.0, "Area euro 7-10": 8.5, "Italia 15+": 20.0}

    if args.offline and os.path.exists(OUT):
        vecchio = json.load(open(OUT, encoding="utf-8"))
        oggi = {g["id"]: g["rendimento"] for g in vecchio["gambe"]}
        print("[sim] --offline: rendimenti di riferimento riusati dal JSON precedente")
    else:
        oggi = rendimenti_oggi()

    out = {
        "generato": dt.date.today().isoformat(),
        "articolo": "/posts/quanto-rendono-etf-obbligazionari/",
        "orizzonti": ORIZZONTI,
        "nota": "Rendimenti lordi di costi e imposte, indici ricostruiti dai "
                "rendimenti dei titoli di Stato. Le finestre si sovrappongono: "
                "descrivono il passato, non sono probabilita'.",
        "gambe": [],
    }

    for g in GAMBE:
        nav, y = gambe_nav[g["gamba"]], rendimenti[g["gamba"]]
        r_oggi = oggi[g["id"]]
        oriz = [s for s in (statistiche(nav, y, h) for h in ORIZZONTI) if s]
        if not oriz:
            sys.exit(f"[sim] ERRORE: nessun orizzonte calcolabile per {g['gamba']}")

        migliore = max(oriz, key=lambda s: s["entro2"])
        sufficienti = [s["anni"] for s in oriz if s["entro2"] >= SOGLIA_SUFFICIENTE]
        d = duration(durate[g["gamba"]], float(y.iloc[-1]) / 100)

        out["gambe"].append({
            **{k: g[k] for k in ("id", "nome", "valuta", "descrizione", "etf", "fonte")},
            "serie": g["gamba"],
            "duration": round(d, 1),
            "scadenza_modellata": durate[g["gamba"]],
            "storia_da": str(y.index[0]),
            "campo_x": {"min": round(float(y.min()), 2), "max": round(float(y.max()), 2)},
            "rendimento": {**r_oggi, "fonte": g["fonte"]["nome"], "link": g["fonte"]["link"]},
            "orizzonte_migliore": migliore["anni"],
            "orizzonte_sufficiente": (min(sufficienti) if sufficienti else None),
            "orizzonti": oriz,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    testo = json.dumps(out, ensure_ascii=False, indent=1, allow_nan=False)
    open(OUT, "w", encoding="utf-8").write(testo)
    json.loads(testo, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))

    print(f"[sim] scritto {OUT}")
    for g in out["gambe"]:
        s10 = next(s for s in g["orizzonti"] if s["anni"] == 10)
        s20 = next(s for s in g["orizzonti"] if s["anni"] == 20)
        print(f"  {g['nome']:38s} dur {g['duration']:4.1f}  "
              f"oggi {it(g['rendimento']['valore'], 2)}% ({g['rendimento']['data']})  "
              f"entro2: 10a {s10['entro2']:4.1f}%  20a {s20['entro2']:4.1f}%  "
              f"meglio a {g['orizzonte_migliore']}a  "
              f"ok da {g['orizzonte_sufficiente']}a")


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("studio", STUDIO)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    main()
