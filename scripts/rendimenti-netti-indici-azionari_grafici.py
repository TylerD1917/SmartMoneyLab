# -*- coding: utf-8 -*-
"""Grafici per l'articolo "Quanto rende davvero l'azionario al netto di tasse e costi?".

Legge i CSV prodotti da scripts/rendimenti-netti-indici-azionari.py.
Palette categoriale validata (lightness band, chroma floor, separazione CVD,
soglia visione normale, contrasto su superficie chiara): ogni indice ha un
colore fisso, mai ciclato. Tema chiaro only. Un solo asse per grafico.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "charts" / "rendimenti-netti-indici-azionari"

COL = {
    "MSCI World":       "#2563eb",
    "MSCI ACWI IMI":    "#0d9488",
    "S&P 500":          "#d97706",
    "Nasdaq Composite": "#db2777",
    "Russell 2000":     "#65a30d",
}
ORDER = list(COL)
INK, INK2, INK3 = "#0f172a", "#475569", "#94a3b8"
SURF = "#ffffff"
H = [1, 3, 5, 10, 15, 20]

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 200, "figure.facecolor": SURF,
    "axes.facecolor": SURF, "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.labelcolor": INK2, "axes.edgecolor": INK3, "axes.linewidth": 0.8,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "--",
    "grid.color": INK3, "legend.frameon": False,
})
PCT = FuncFormatter(lambda v, _: f"{v:.0f}%")


def _load(name):
    d = pd.read_csv(OUT / name)
    for c in d.columns:
        if c.startswith(("lordo_", "netto_p", "netto_med", "reale_", "erosione",
                         "solo_", "quota_", "inflazione")) and "moltipl" not in c:
            d[c] = d[c] * 100
    return d


def _foot(fig, txt):
    fig.text(0.008, 0.005, txt, fontsize=7.5, color=INK3, ha="left", va="bottom")


# --- 1. mediana netta per orizzonte, cinque serie ------------------------
def chart_mediana(d):
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    x = np.arange(len(H))
    ends = []
    for k in ORDER:
        s = d[d.indice == k].set_index("anni")
        y = [s.netto_mediana.get(h, np.nan) for h in H]
        ax.plot(x, y, color=COL[k], lw=2, marker="o", ms=8, zorder=3,
                markeredgecolor=SURF, markeredgewidth=2, label=k)
        ends.append([y[-1], y[-1], k])

    # separa verticalmente le etichette finali troppo vicine (min 0.42pp)
    ends.sort(key=lambda r: r[0])
    for i in range(1, len(ends)):
        if ends[i][1] - ends[i - 1][1] < 0.42:
            ends[i][1] = ends[i - 1][1] + 0.42
    shift = (sum(r[1] for r in ends) - sum(r[0] for r in ends)) / len(ends)
    for val, pos, k in ends:
        ax.annotate(f"{val:.1f}%", (x[-1], val), xycoords="data",
                    xytext=(x[-1] + 0.14, pos - shift), textcoords="data",
                    color=COL[k], fontsize=10, fontweight="bold", va="center",
                    arrowprops=dict(arrowstyle="-", color=COL[k], lw=0.8,
                                    shrinkA=3, shrinkB=1, alpha=0.6))
    ax.set_xticks(x, [f"{h} anno" if h == 1 else f"{h} anni" for h in H])
    ax.yaxis.set_major_formatter(PCT)
    ax.set_ylabel("rendimento annuo netto, mediana delle finestre")
    ax.set_title("Rendimento annuo netto mediano, per orizzonte di investimento")
    ax.set_xlim(-0.35, len(H) + 0.15)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.11), fontsize=10)
    _foot(fig, "Netto di TER, ritenuta estera sui dividendi, bollo 0,2%/anno e 26% "
               "sulla plusvalenza al riscatto. Finestre rolling a passo mensile, in euro. "
               "Massima storicità per indice.")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "01_mediana_netta_per_orizzonte.png", bbox_inches="tight")
    plt.close(fig)


# --- 2. ventaglio dei percentili, small multiples ------------------------
def chart_ventaglio(d):
    fig, axes = plt.subplots(1, 5, figsize=(15.5, 4.6), sharey=True)
    x = np.arange(len(H))
    for ax, k in zip(axes, ORDER):
        s = d[d.indice == k].set_index("anni")
        g = lambda c: np.array([s[c].get(h, np.nan) for h in H], dtype=float)
        ax.axhline(0, color=INK3, lw=1, zorder=1)
        ax.fill_between(x, g("netto_p5"), g("netto_p95"), color=COL[k],
                        alpha=0.14, lw=0, zorder=2)
        ax.fill_between(x, g("netto_p25"), g("netto_p75"), color=COL[k],
                        alpha=0.30, lw=0, zorder=3)
        ax.plot(x, g("netto_mediana"), color=COL[k], lw=2, zorder=4)
        ax.set_xticks(x, [str(h) for h in H])
        ax.set_title(k, fontsize=11)
        ax.set_xlabel("anni")
        ax.yaxis.set_major_formatter(PCT)
    axes[0].set_ylabel("rendimento annuo netto")
    axes[0].set_ylim(-32, 46)
    fig.suptitle("Dispersione del rendimento netto: mediana, quartili (p25-p75) e "
                 "coda (p5-p95)", fontsize=13, fontweight="bold", color=INK, y=1.02)
    _foot(fig, "La banda scura è metà delle finestre, quella chiara il 90%. "
               "Finestre rolling a passo mensile, in euro, netto di costi e 26%.")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "02_ventaglio_percentili.png", bbox_inches="tight")
    plt.close(fig)


# --- 3. scomposizione dell'erosione -------------------------------------
def chart_erosione(d):
    fig, axes = plt.subplots(1, 5, figsize=(15.5, 4.4), sharey=True)
    x = np.arange(len(H))
    for ax, k in zip(axes, ORDER):
        s = d[d.indice == k].set_index("anni")
        cos = np.array([s.solo_costi_pp.get(h, np.nan) for h in H], dtype=float)
        tax = np.array([s.solo_tasse_pp.get(h, np.nan) for h in H], dtype=float)
        ax.bar(x, cos, 0.68, color="#94a3b8", label="TER + ritenuta + bollo",
               zorder=3, edgecolor=SURF, linewidth=2)
        ax.bar(x, tax, 0.68, bottom=cos, color=COL[k], label="imposta 26%",
               zorder=3, edgecolor=SURF, linewidth=2)
        for xi, (c, t) in enumerate(zip(cos, tax)):
            ax.text(xi, c + t + 0.08, f"{c+t:.1f}", ha="center", va="bottom",
                    fontsize=8.5, color=INK2)
        ax.set_xticks(x, [str(h) for h in H])
        ax.set_title(k, fontsize=11)
        ax.set_xlabel("anni")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}pp"))
    axes[0].set_ylabel("rendimento annuo perso vs indice lordo")
    axes[0].set_ylim(0, 5.6)
    axes[0].legend(fontsize=9, loc="upper right")
    fig.suptitle("Di quanto costi e imposta riducono il rendimento annuo, e come si "
                 "ripartiscono", fontsize=13, fontweight="bold", color=INK, y=1.03)
    _foot(fig, "Differenza in punti percentuali tra la mediana lorda dell'indice e "
               "la mediana netta, scomposta. L'imposta si paga una volta sola al "
               "riscatto, quindi il suo peso annualizzato diminuisce con l'orizzonte.")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "03_scomposizione_erosione.png", bbox_inches="tight")
    plt.close(fig)


# --- 4. nominale vs reale ------------------------------------------------
def chart_reale(d):
    fig, axes = plt.subplots(1, 5, figsize=(15.5, 4.4), sharey=True)
    x = np.arange(len(H))
    w = 0.38
    for ax, k in zip(axes, ORDER):
        s = d[d.indice == k].set_index("anni")
        nom = [s.netto_mediana.get(h, np.nan) for h in H]
        rea = [s.reale_mediana.get(h, np.nan) for h in H]
        ax.bar(x - w/2, nom, w, color=COL[k], alpha=0.35, label="netto nominale",
               zorder=3, edgecolor=SURF, linewidth=1.5)
        ax.bar(x + w/2, rea, w, color=COL[k], label="netto reale",
               zorder=3, edgecolor=SURF, linewidth=1.5)
        for xi, v in enumerate(rea):
            ax.text(xi + w/2, v + 0.12, f"{v:.1f}", ha="center", va="bottom",
                    fontsize=8.5, color=INK2, fontweight="bold")
        ax.set_xticks(x, [str(h) for h in H])
        ax.set_title(k, fontsize=11)
        ax.set_xlabel("anni")
        ax.yaxis.set_major_formatter(PCT)
    axes[0].set_ylabel("rendimento annuo mediano")
    axes[0].set_ylim(0, 13)
    axes[0].legend(fontsize=9, loc="upper right")
    fig.suptitle("Lo stesso rendimento netto, prima e dopo l'inflazione italiana",
                 fontsize=13, fontweight="bold", color=INK, y=1.03)
    _foot(fig, "Inflazione: FRED FPCPITOTLZGITA (indice dei prezzi al consumo Italia). "
               "L'imposta del 26% si applica alla plusvalenza nominale, quindi si "
               "deflaziona dopo il prelievo. Massima storicità per indice, "
               "periodi non omogenei tra indici.")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "04_nominale_vs_reale.png", bbox_inches="tight")
    plt.close(fig)


# --- 5. moltiplicatori a 20 anni, periodo comune -------------------------
def chart_moltiplicatori(dc, start, end):
    s20 = dc[dc.anni == 20].set_index("indice")
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    y = np.arange(len(ORDER))[::-1]
    h = 0.24
    for i, k in enumerate(ORDER):
        r = s20.loc[k]
        yy = y[i]
        for off, col, al, val, lab in [
            (h, COL[k], 0.22, r.lordo_moltiplicatore_mediano, "indice lordo"),
            (0, COL[k], 0.55, r.netto_moltiplicatore_mediano, "ETF netto"),
            (-h, COL[k], 1.0, r.reale_moltiplicatore_mediano, "ETF netto reale"),
        ]:
            ax.barh(yy + off, val, h * 0.92, color=col, alpha=al, zorder=3,
                    edgecolor=SURF, linewidth=1.5)
            ax.text(val + 0.06, yy + off, f"{val:.2f}x", va="center",
                    fontsize=9.5, color=INK2,
                    fontweight="bold" if off == -h else "normal")
    ax.axvline(1, color=INK3, lw=1, zorder=1)
    ax.set_yticks(y, ORDER)
    ax.set_xlabel("quanto è diventato 1 euro dopo 20 anni, mediana delle 134 finestre")
    ax.set_xlim(0, 7.0)
    # legenda in grigio neutro: codifica l'intensita', non l'indice
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=INK2, alpha=a, label=l) for a, l in
               [(0.22, "indice lordo"), (0.55, "ETF netto"), (1.0, "ETF netto reale")]]
    ax.set_title(f"Un euro investito per vent'anni: lordo, netto, netto reale")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=handles, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), fontsize=10)
    _foot(fig, f"Periodo comune a tutti e cinque gli indici, {start} - {end}, "
               f"così gli orizzonti sono confrontabili tra loro. Netto di TER, "
               f"ritenuta, bollo e 26% sulla plusvalenza; reale al netto anche "
               f"dell'inflazione italiana.")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "05_moltiplicatori_20_anni.png", bbox_inches="tight")
    plt.close(fig)


def main():
    d = _load("rolling_netto.csv")
    dc = _load("rolling_netto_periodo_comune.csv")
    chart_mediana(d)
    chart_ventaglio(d)
    chart_erosione(d)
    chart_reale(d)
    chart_moltiplicatori(dc, "giugno 1995", "luglio 2026")
    print("grafici scritti in", OUT)
    for f in sorted(OUT.glob("*.png")):
        print(" ", f.name, f"{f.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
