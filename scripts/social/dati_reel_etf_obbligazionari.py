# -*- coding: utf-8 -*-
"""Dati per il reel 'quando compri' sugli ETF obbligazionari.

Per ogni mese di acquisto calcola il rendimento annuo composto dei DIECI anni
successivi, su ciascuna gamba sintetica dello studio. L'asse del tempo del reel
non e' la detenzione ma la DATA DI ACQUISTO: e' la stessa serie del grafico
03_peggiori.png dell'articolo.

Uso:  python scripts/social/dati_reel_etf_obbligazionari.py
Out:  social/quanto-rendono-etf-obbligazionari/reel_quando_compri.csv
"""
from __future__ import annotations

import importlib.util
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STUDIO = os.path.join(ROOT, "scripts", "quanto-rendono-etf-obbligazionari.py")
OUT = os.path.join(ROOT, "social", "quanto-rendono-etf-obbligazionari",
                   "reel_quando_compri.csv")

spec = importlib.util.spec_from_file_location("studio", STUDIO)
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)

ORIZZONTE = 10


def main():
    gambe, _extra, _rend = studio.costruisci()
    col = {n: studio.finestre(s, ORIZZONTE, passo=1) for n, s in gambe.items()}
    df = pd.DataFrame(col)

    print("copertura per gamba (mese di acquisto):")
    for n, s in col.items():
        print(f"  {n:16s} {s.index[0]} -> {s.index[-1]}  n={len(s):4d}  "
              f"min {s.min():6.2f}% ({s.idxmin()})  max {s.max():6.2f}% ({s.idxmax()})")

    pieno = df.dropna()
    print(f"\nfinestra comune a tutte: {pieno.index[0]} -> {pieno.index[-1]} "
          f"({len(pieno)} mesi)")
    for n in pieno:
        s = pieno[n]
        print(f"  {n:16s} min {s.min():6.2f}% ({s.idxmin()})  "
              f"max {s.max():6.2f}% ({s.idxmax()})  ultimo {s.iloc[-1]:6.2f}%")

    out = pieno.copy()
    out.index = out.index.to_timestamp()
    out.index.name = "Date"
    out.round(3).to_csv(OUT)
    print(f"\nscritto {OUT}")


if __name__ == "__main__":
    main()
