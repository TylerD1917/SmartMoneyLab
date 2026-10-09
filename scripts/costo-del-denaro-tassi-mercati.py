# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 13: il costo del denaro
================================================================================

Ultimo episodio della collana. Non e' un nuovo studio sui tassi: quello esiste
gia' (regimi-tassi-sp500-nasdaq) e questo episodio lo linka. Qui si spiega il
MECCANISMO che collega un solo numero a tutto il resto, cioe' il valore attuale,
e si mostra che otto episodi precedenti descrivevano lo stesso fenomeno.

1. IL VALORE ATTUALE. Quanto vale oggi una promessa di cento euro, al variare
   della distanza nel tempo e del tasso. E' il grafico didattico che regge
   l'articolo: la distanza nel tempo e' il moltiplicatore dell'effetto.

2. IL 2022 COME ESPERIMENTO NATURALE. Il rendimento del ventennale americano e'
   passato dall'1,94% al 4,14% in un anno. Gli asset ordinati per quanto sono
   lontani i loro flussi, e il risultato che ne segue. Con l'energia lasciata
   nel grafico come controesempio: il meccanismo spiega molto, non tutto.

3. SETTANT'ANNI DI COSTO DEL DENARO. Il ventennale di mercato dal 1962 con
   sotto il tasso di policy, cosi' lo stesso grafico mostra anche che la banca
   centrale fissa solo il brevissimo termine e il resto lo decide il mercato.

BASE DEI DATI
-------------
data/Bonds/DGS20_fred_1962.csv  rendimento del Treasury a 20 anni, giornaliero
data/Bonds/FEDFUNDS.csv         tasso sui federal funds, medie mensili
data/cache/correlation_universe_monthly.csv  per il 2022

OUTPUT in public/charts/costo-del-denaro-tassi-mercati/
-------------------------------------------------------
  01_valore_attuale.png   quanto vale oggi una promessa futura
  02_shock_2022.png       chi ha pagato lo shock dei tassi, e perche'
  03_settant_anni.png     il costo del denaro dal 1962
  summary.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "charts" / "costo-del-denaro-tassi-mercati"
DGS20 = ROOT / "data" / "Bonds" / "DGS20_fred_1962.csv"
FEDFUNDS = ROOT / "data" / "Bonds" / "FEDFUNDS.csv"
UNIVERSO = ROOT / "data" / "cache" / "correlation_universe_monthly.csv"

TASSI = (0.01, 0.03, 0.05, 0.07)
ANNI_MAX = 30
SHOCK_DA, SHOCK_A = "2021-12-31", "2022-12-31"

# gli asset del 2022, raggruppati per quanto sono lontani i flussi che promettono
GRUPPI = [
    ("flussi molto lontani", "#1e3a8a",
     ["Semiconduttori", "Nasdaq 100", "Treasury USA 20+", "Real Estate (REIT)"]),
    ("mercato nel suo insieme", "#64748b", ["USA (S&P 500)"]),
    ("flussi vicini", "#047857",
     ["Value (S&P500)", "Healthcare", "Consumer Staples"]),
    ("nessun flusso, o altra storia", "#d97706", ["Oro", "Energy"]),
]
IT = {"Semiconduttori": "Semiconduttori", "Nasdaq 100": "Nasdaq 100",
      "Treasury USA 20+": "Treasury USA 20+", "Real Estate (REIT)": "Immobiliare (REIT)",
      "USA (S&P 500)": "USA (S&P 500)", "Value (S&P500)": "Value (USA)",
      "Healthcare": "Sanità", "Consumer Staples": "Beni di consumo",
      "Oro": "Oro", "Energy": "Energia"}

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#047857"
GRIGIO = "#64748b"


def it(x: float, d: int = 1) -> str:
    """Virgola decimale. Si applica SOLO al numero, mai a una frase."""
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# -------------------------------------------------------------------- dati
def valore_attuale(cento: float = 100.0) -> dict:
    """Quanto vale oggi la promessa di `cento` euro fra n anni, a vari tassi."""
    anni = np.arange(0, ANNI_MAX + 1)
    return {r: cento / (1 + r) ** anni for r in TASSI}


def shock_2022() -> pd.Series:
    df = pd.read_csv(UNIVERSO, parse_dates=["date"]).set_index("date").sort_index()
    w = df.loc[SHOCK_DA:SHOCK_A]
    return ((w.iloc[-1] / w.iloc[0]) - 1) * 100


def tassi() -> tuple[pd.Series, pd.Series]:
    d = pd.read_csv(DGS20, parse_dates=["observation_date"]) \
        .set_index("observation_date")["DGS20"].dropna().sort_index()
    # il Treasury a 20 anni non e' stato emesso fra il 1987 e il 1993: senza un
    # buco esplicito matplotlib unirebbe i due tratti con una retta inventata
    buco = d.index.to_series().diff() > pd.Timedelta(days=40)
    for data in d.index[buco]:
        d.loc[data - pd.Timedelta(days=1)] = np.nan
    d = d.sort_index()
    f = pd.read_csv(FEDFUNDS, parse_dates=["observation_date"]) \
        .set_index("observation_date")["FEDFUNDS"].dropna().sort_index()
    return d, f


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_valore_attuale(va: dict, out: Path):
    anni = np.arange(0, ANNI_MAX + 1)
    colori = {0.01: "#93c5fd", 0.03: "#3b82f6", 0.05: NAVY, 0.07: "#0f172a"}
    fig, ax = plt.subplots(figsize=(10.2, 6.2))
    for r in TASSI:
        v = va[r]
        ax.plot(anni, v, lw=2.3, color=colori[r], label=f"tasso {it(r * 100, 0)}%")
        ax.annotate(f"{it(v[-1], 0)} €", xy=(anni[-1], v[-1]), xytext=(9, 0),
                    textcoords="offset points", va="center", fontsize=10.5,
                    fontweight="bold", color=colori[r])

    ax.set_title("Quanto vale oggi la promessa di cento euro fra N anni")
    ax.set_xlabel("anni di distanza del pagamento")
    ax.set_ylabel("valore oggi")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} €"))
    ax.set_xlim(0, ANNI_MAX + 2.6)
    ax.set_ylim(0, 105)
    ax.legend(loc="lower left", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_shock(r: pd.Series, out: Path):
    righe = []
    for etichetta, colore, nomi in GRUPPI:
        for n in nomi:
            righe.append((IT.get(n, n), float(r[n]), colore, etichetta))
    righe.sort(key=lambda x: x[1])
    nomi = [x[0] for x in righe]
    vals = [x[1] for x in righe]
    colori = [x[2] for x in righe]

    fig, ax = plt.subplots(figsize=(10.4, 6.8))
    ax.barh(nomi, vals, color=colori, alpha=0.88, height=0.68)
    for i, v in enumerate(vals):
        ax.annotate(it(v, 1) + "%", xy=(v, i),
                    xytext=(6 if v >= 0 else -6, 0), textcoords="offset points",
                    va="center", ha="left" if v >= 0 else "right",
                    fontsize=10, fontweight="bold", color=colori[i])
    ax.axvline(0, color="#334155", lw=1.1)

    visti, handles = set(), []
    for etichetta, colore, _ in GRUPPI:
        if etichetta in visti:
            continue
        visti.add(etichetta)
        handles.append(plt.Rectangle((0, 0), 1, 1, color=colore, alpha=0.88,
                                     label=etichetta))
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=10,
              title="distanza dei flussi promessi", title_fontsize=10)

    ax.set_title("Il 2022, quando il costo del denaro è raddoppiato in un anno")
    ax.set_xlabel("rendimento dell'anno 2022, in dollari")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_xlim(-45, 78)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_settant_anni(d: pd.Series, f: pd.Series, out: Path):
    fig, ax = plt.subplots(figsize=(10.6, 6.2))
    ax.plot(f.index, f.values, lw=1.2, color=GOLD, alpha=0.85,
            label="tasso di policy (federal funds)")
    ax.plot(d.index, d.values, lw=1.8, color=NAVY,
            label="tasso di mercato (Treasury 20 anni)")

    ax.axvspan(pd.Timestamp("2009-01-01"), pd.Timestamp("2021-12-31"),
               color=GRIGIO, alpha=0.13, zorder=0)
    ax.annotate("l'epoca in cui ha imparato\na investire quasi tutto il pubblico\ndi oggi",
                xy=(pd.Timestamp("2015-01-01"), 13.2), ha="center", fontsize=9.5,
                color=GRIGIO, style="italic")

    for testo, data, valore, dx, dy, ha in (
            (f"massimo del ventennale: {it(d.max(), 2)}%", d.idxmax(), d.max(), 10, 6, "left"),
            (f"minimo: {it(d.min(), 2)}%", d.idxmin(), d.min(), 0, -19, "center"),
            (f"oggi: {it(d.iloc[-1], 2)}%", d.index[-1], d.iloc[-1], -6, 16, "right")):
        ax.scatter([data], [valore], s=70, color=ROSSO, zorder=5,
                   edgecolor="white", linewidth=0.9)
        ax.annotate(testo, xy=(data, valore), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, fontsize=10,
                    fontweight="bold", color=ROSSO)

    ax.set_title("Settant'anni di costo del denaro negli Stati Uniti")
    ax.set_ylabel("rendimento annuo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(-1.1, 20)
    ax.set_xlim(pd.Timestamp("1954-01-01"), pd.Timestamp("2028-06-30"))
    ax.legend(loc="upper right", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    va = valore_attuale()
    r22 = shock_2022()
    d, f = tassi()

    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    plot_valore_attuale(va, OUT / "01_valore_attuale.png")
    plot_shock(r22, OUT / "02_shock_2022.png")
    plot_settant_anni(d, f, OUT / "03_settant_anni.png")

    dgs_da = float(d.loc[:SHOCK_DA].iloc[-1])
    dgs_a = float(d.loc[:SHOCK_A].iloc[-1])

    # controlli: se cadono, l'articolo afferma cose false
    assert dgs_a > 2 * dgs_da - 0.3, "il ventennale non e' quasi raddoppiato nel 2022"
    assert r22["Treasury USA 20+"] < r22["USA (S&P 500)"] < r22["Consumer Staples"], \
        "l'ordine per distanza dei flussi non regge nel 2022"
    assert va[0.05][30] < va[0.01][30] / 2, \
        "il valore attuale a trent'anni non si dimezza fra l'1% e il 5%"

    decenni = d.resample("ME").last().groupby(lambda x: (x.year // 10) * 10).mean()
    summary = {
        "valore_attuale": {f"{int(r*100)}%": {str(n): round(float(va[r][n]), 2)
                                              for n in (1, 5, 10, 20, 30)}
                           for r in TASSI},
        "shock_2022": {"dgs20_inizio": dgs_da, "dgs20_fine": dgs_a,
                       "rendimenti": {IT.get(n, n): round(float(r22[n]), 1)
                                      for _, _, nomi in GRUPPI for n in nomi}},
        "storia": {"dal": str(d.index[0].date()), "al": str(d.index[-1].date()),
                   "max": float(d.max()), "max_data": str(d.idxmax().date()),
                   "min": float(d.min()), "min_data": str(d.idxmin().date()),
                   "oggi": float(d.iloc[-1]),
                   "medie_decennio": {str(k): round(float(v), 2)
                                      for k, v in decenni.items()},
                   "fedfunds_max": float(f.max()), "fedfunds_min": float(f.min())},
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("valore attuale di 100 euro:")
    print("  anni " + "".join(f"{int(r*100):>8}%" for r in TASSI))
    for n in (1, 5, 10, 20, 30):
        print(f"  {n:>4} " + "".join(f"{it(va[r][n], 1):>9}" for r in TASSI))
    print(f"\nventennale: {it(dgs_da, 2)}% -> {it(dgs_a, 2)}% nel 2022")
    for _, _, nomi in GRUPPI:
        for n in nomi:
            print(f"  {IT.get(n, n):22s} {it(r22[n], 1):>7}%")
    print(f"\nstoria {d.index[0].date()} -> {d.index[-1].date()}: max {it(d.max(), 2)}% "
          f"({d.idxmax().date()}), min {it(d.min(), 2)}% ({d.idxmin().date()}), "
          f"oggi {it(d.iloc[-1], 2)}%")
    print("  medie per decennio: " + ", ".join(f"{k} {it(v, 2)}%" for k, v in decenni.items()))
    print(f"grafici in {OUT}")


if __name__ == "__main__":
    main()
