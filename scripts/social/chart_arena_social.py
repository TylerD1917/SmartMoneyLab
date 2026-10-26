# -*- coding: utf-8 -*-
"""Grafico statico dell'AI Investing Arena per il carosello Instagram.

Legge la serie NAV giornaliera pubblicata dal motore dell'arena e disegna le
curve in percentuale dal capitale iniziale. Serve al carosello, che ha bisogno
di un PNG: la pagina del sito usa un grafico React che qui non si puo' riusare.

Uso:  python scripts/social/chart_arena_social.py --csv <file> --out <png>
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

NAVY = "#1e3a8a"; NERO = "#0f172a"; VERDE = "#047857"; GOLD = "#d97706"
ROSSO = "#dc2626"; GRIGIO = "#64748b"; VIOLA = "#7c3aed"

SERIE = [
    ("gpt", "ChatGPT", GOLD, 2.8),
    ("gemini", "Gemini", VERDE, 2.2),
    ("SP500", "S&P 500", NERO, 1.8),
    ("kimi", "Kimi", VIOLA, 1.8),
    ("random", "A caso", GRIGIO, 1.8),
    ("claude", "Claude", ROSSO, 2.2),
]
MESI = {9: "set", 10: "ott", 11: "nov", 12: "dic", 1: "gen", 2: "feb", 3: "mar",
        4: "apr", 5: "mag", 6: "giu", 7: "lug", 8: "ago"}


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    d = pd.read_csv(a.csv, parse_dates=["date"]).set_index("date")
    pct = (d / d.iloc[0] - 1) * 100

    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 15,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })
    # proporzioni quasi quadrate: il grafico finisce dentro la scheda del
    # carosello, che e' 1080x1080, e in formato largo lascerebbe meta' card vuota
    fig, ax = plt.subplots(figsize=(9.6, 8.0))

    # le etichette finali non devono accavallarsi: le distanzio tenendo i
    # valori veri sulle curve
    fini = sorted(((pct[c].iloc[-1], c, et, col) for c, et, col, _ in SERIE), reverse=True)
    gap = (max(f[0] for f in fini) - min(f[0] for f in fini)) * 0.085
    ys, prec = {}, None
    for v, c, et, col in fini:
        y = v if prec is None else min(v, prec - gap)
        ys[c] = y; prec = y

    for col_name, etichetta, colore, spessore in SERIE:
        ax.plot(pct.index, pct[col_name], lw=spessore, color=colore)
        v = pct[col_name].iloc[-1]
        ax.annotate(f"{etichetta}  {'+' if v >= 0 else '−'}{it(abs(v))}%",
                    xy=(pct.index[-1], ys[col_name]), xytext=(10, 0),
                    textcoords="offset points", va="center", fontsize=15,
                    fontweight="bold", color=colore)

    ax.axhline(0, color=NERO, lw=1.2)
    ax.set_ylabel("variazione dal capitale iniziale")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"{matplotlib.dates.num2date(v).day} "
                                           f"{MESI[matplotlib.dates.num2date(v).month]}"))
    # spazio a destra per le etichette, ma le tacche si fermano all'ultimo
    # giorno con dati: proseguire darebbe l'idea di una serie piu' lunga
    ax.set_xlim(pct.index[0], pct.index[-1] + pd.Timedelta(days=9))
    tacche = pd.date_range(pct.index[1], pct.index[-1], freq="4D")
    ax.set_xticks(tacche)
    ax.grid(axis="x", visible=False)
    # il primo punto della serie e' la riga di innesco a 100.000: la data da
    # mostrare e' quella del primo giorno vero di contrattazione
    ax.set_title(f"100.000 dollari a testa, dal {pct.index[1].day} "
                 f"{MESI[pct.index[1].month]} al {pct.index[-1].day} "
                 f"{MESI[pct.index[-1].month]} 2026",
                 fontsize=17, fontweight="bold", loc="left")
    fig.tight_layout()
    fig.savefig(a.out)
    print(f"[arena] {a.out}")
    for v, c, et, _ in fini:
        print(f"    {et:10s} {v:+6.2f}%")


if __name__ == "__main__":
    main()
