# -*- coding: utf-8 -*-
"""Versione del grafico dei moltiplicatori pensata per il carosello Instagram.

Stesso dato del grafico 05 dell'articolo, ma con meno elementi e testo molto
piu' grande: dentro una slide quadrata su telefono il grafico dell'articolo
risulta illeggibile.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "public" / "charts" / "rendimenti-netti-indici-azionari" / "rolling_netto_periodo_comune.csv"
OUT = ROOT / "social" / "quanto-rende-azionario-netto-tasse-costi" / "chart_moltiplicatori_social.png"

COL = {"MSCI World": "#2563eb", "MSCI ACWI IMI": "#0d9488", "S&P 500": "#d97706",
       "Nasdaq Composite": "#db2777", "Russell 2000": "#65a30d"}
ORDER = list(COL)
INK, INK2, SURF = "#0f172a", "#475569", "#ffffff"

d = pd.read_csv(SRC)
d = d[d.anni == 20].set_index("indice")

plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF,
                     "savefig.dpi": 200, "font.size": 19})
fig, ax = plt.subplots(figsize=(10, 7.4))
y = np.arange(len(ORDER))[::-1]
h = 0.26
for i, k in enumerate(ORDER):
    r, yy = d.loc[k], y[i]
    for off, al, val, w in [(h, 0.22, r.lordo_moltiplicatore_mediano, "normal"),
                            (0, 0.55, r.netto_moltiplicatore_mediano, "normal"),
                            (-h, 1.0, r.reale_moltiplicatore_mediano, "bold")]:
        ax.barh(yy + off, val, h * 0.9, color=COL[k], alpha=al, zorder=3,
                edgecolor=SURF, linewidth=2)
        ax.text(val + 0.12, yy + off, f"{val:.2f}x".replace(".", ","), va="center",
                fontsize=17, color=INK2, fontweight=w)
ax.axvline(1, color="#94a3b8", lw=1.5, zorder=1)
ax.set_yticks(y, ORDER, fontsize=19, color=INK)
ax.set_xticks([])
ax.set_xlim(0, 7.6)
for s in ("top", "right", "bottom"):
    ax.spines[s].set_visible(False)
ax.spines["left"].set_color("#cbd5e1")
ax.grid(False)
ax.set_title("Un euro investito per 20 anni", fontsize=24, fontweight="bold",
             color=INK, pad=22)

from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=INK2, alpha=a, label=l) for a, l in
                   [(0.22, "sulla carta"), (0.55, "dopo costi e tasse"),
                    (1.0, "dopo anche l'inflazione")]],
          ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.02),
          fontsize=15, frameon=False, handlelength=1.6, columnspacing=1.4)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("scritto", OUT)
