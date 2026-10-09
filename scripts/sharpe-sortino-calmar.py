# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 12: Sharpe, Sortino e Calmar
================================================================================

Episodio espositivo: cosa sono gli indicatori aggiustati per il rischio, come
si costruiscono e come si leggono. NON e' un confronto fra indicatori e NON
valuta la loro capacita' predittiva: sono tre strumenti di descrizione, e
l'articolo li spiega uno per uno sullo stesso esempio.

L'impianto: tutti e tre sono la stessa frazione. Sopra il rendimento in
eccesso sul tasso privo di rischio, sotto una misura di rischio. Cambia solo
il denominatore.

  Sharpe   = eccesso annuo / volatilita' annualizzata
  Sortino  = eccesso annuo / semideviazione annualizzata (solo i mesi negativi)
  Calmar   = rendimento annuo composto / massimo drawdown

1. COSA GUARDA OGNI DENOMINATORE. Tre pannelli sulla stessa serie di
   rendimenti mensili dell'S&P 500: tutta la dispersione, la sola dispersione
   verso il basso, la caduta piu' profonda. E' il grafico didattico che
   l'episodio richiede.

2. I TRE INDICATORI SU SEI ASSET NOTI. Esempi di lettura, non una graduatoria:
   le tre scale non sono confrontabili fra loro e il grafico lo dichiara.

3. LO STESSO INDICATORE SU QUATTRO SOTTOPERIODI. Illustra la cosa piu'
   importante da sapere prima di usarli: descrivono un periodo, non un asset.

BASE DEI DATI
-------------
data/cache/correlation_universe_monthly.csv, chiusure mensili aggiustate per i
dividendi in dollari, finestra comune agosto 2002 - agosto 2026, la stessa
dell'episodio 10 per coerenza.
data/Bonds/FEDFUNDS.csv per il tasso privo di rischio, mensile.

OUTPUT in public/charts/sharpe-sortino-calmar/
----------------------------------------------
  01_tre_denominatori.png  cosa guarda ciascuna misura di rischio
  02_sei_asset.png         i tre indicatori su sei asset noti
  03_sottoperiodi.png      lo stesso indicatore cambia col periodo
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
OUT = ROOT / "public" / "charts" / "sharpe-sortino-calmar"
UNIVERSO = ROOT / "data" / "cache" / "correlation_universe_monthly.csv"
FEDFUNDS = ROOT / "data" / "Bonds" / "FEDFUNDS.csv"

INIZIO, FINE = "2002-08-01", "2026-08-31"
SOGLIA = "2002-09-30"
ESEMPIO = "USA (S&P 500)"
SEI = ["USA (S&P 500)", "Nasdaq 100", "Consumer Staples", "Oro", "Giappone",
       "Treasury USA 20+"]
QUATTRO = ["USA (S&P 500)", "Nasdaq 100", "Oro", "Treasury USA 20+"]
PERIODI = [("2003-01", "2007-12"), ("2008-01", "2012-12"),
           ("2013-01", "2019-12"), ("2020-01", "2026-08")]

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#047857"
GRIGIO = "#64748b"
CHIARO = "#cbd5e1"

IT = {"USA (S&P 500)": "USA (S&P 500)", "Nasdaq 100": "Nasdaq 100",
      "Consumer Staples": "Beni di consumo", "Oro": "Oro", "Giappone": "Giappone",
      "Treasury USA 20+": "Treasury USA 20+", "Healthcare": "Sanità",
      "Financials": "Banche e finanza", "Energy": "Energia",
      "Semiconduttori": "Semiconduttori", "Value (S&P500)": "Value (USA)",
      "Small Cap (Russell 2000)": "Small cap (USA)", "Petrolio (WTI)": "Petrolio",
      "Argento": "Argento", "Rame": "Rame", "Germania": "Germania",
      "Regno Unito": "Regno Unito", "Australia": "Australia", "Canada": "Canada",
      "Corea del Sud": "Corea del Sud", "Taiwan": "Taiwan",
      "America Latina": "America Latina"}


def it(x: float, d: int = 2) -> str:
    """Virgola decimale. Si applica SOLO al numero, mai a una frase."""
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# -------------------------------------------------------------------- dati
def carica():
    df = pd.read_csv(UNIVERSO, parse_dates=["date"]).set_index("date").sort_index()
    ff = pd.read_csv(FEDFUNDS, parse_dates=["observation_date"]) \
        .set_index("observation_date")["FEDFUNDS"] / 100.0
    # il Fed funds e' una media mensile datata al primo del mese: la riporto a
    # fine mese per allinearla alle chiusure del panel
    rf = ff.reindex(pd.date_range(ff.index[0], "2026-09-01", freq="MS")).ffill()
    rf.index = rf.index + pd.offsets.MonthEnd(0)
    return df, rf


def semideviazione(r: pd.Series) -> float:
    """Radice della media dei quadrati dei soli rendimenti negativi, annualizzata.
    I mesi positivi entrano nella media come zero: non sono un rischio, ma
    fanno parte del campione."""
    return float(np.sqrt((r.clip(upper=0) ** 2).mean()) * np.sqrt(12))


def indicatori(s: pd.Series, rf: pd.Series) -> dict:
    s = s.dropna()
    r = s.pct_change().dropna()
    rfm = rf.reindex(r.index).ffill() / 12.0
    eccesso = float((r - rfm).mean() * 12)
    vol = float(r.std(ddof=1) * np.sqrt(12))
    semi = semideviazione(r)
    maxdd = float((s / s.cummax() - 1).min())
    anni = (len(s) - 1) / 12
    cagr = float(s.iloc[-1] / s.iloc[0]) ** (1 / anni) - 1
    return {"cagr": cagr, "eccesso": eccesso, "vol": vol, "semi": semi,
            "maxdd": maxdd, "sharpe": eccesso / vol, "sortino": eccesso / semi,
            "calmar": cagr / abs(maxdd), "mesi": int(len(s)),
            "rf_medio": float(rfm.mean() * 12)}


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 12.5, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_denominatori(s: pd.Series, m: dict, out: Path):
    """Stessa serie, tre inquadrature: e' il grafico che spiega l'episodio."""
    s = s.dropna()
    r = s.pct_change().dropna() * 100
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 5.4))

    # --- 1. volatilita': tutta la dispersione
    ax = axes[0]
    ax.bar(r.index, r.values, width=24, color=NAVY, alpha=0.55)
    sd = r.std(ddof=1)
    ax.axhline(r.mean(), color="#334155", lw=1.1)
    ax.axhspan(r.mean() - sd, r.mean() + sd, color=NAVY, alpha=0.16, zorder=0)
    ax.set_title("Sharpe guarda\ntutta la dispersione")
    ax.annotate(f"volatilità annua\n{it(m['vol'] * 100, 1)}%",
                xy=(0.04, 0.05), xycoords="axes fraction", fontsize=10.5,
                fontweight="bold", color=NAVY)

    # --- 2. semideviazione: solo i mesi negativi
    ax = axes[1]
    neg = r.where(r < 0, 0.0)
    pos = r.where(r >= 0, 0.0)
    ax.bar(r.index, pos.values, width=24, color=CHIARO, alpha=0.9)
    ax.bar(r.index, neg.values, width=24, color=ROSSO, alpha=0.75)
    ax.axhline(0, color="#334155", lw=1.1)
    ax.set_title("Sortino guarda\nsolo i mesi in perdita")
    ax.annotate(f"semideviazione annua\n{it(m['semi'] * 100, 1)}%",
                xy=(0.04, 0.05), xycoords="axes fraction", fontsize=10.5,
                fontweight="bold", color=ROSSO)

    for ax in axes[:2]:
        ax.set_ylim(-18, 14)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("rendimento del mese")

    # --- 3. drawdown: la caduta piu' profonda
    ax = axes[2]
    base = s / s.iloc[0] * 100
    ax.plot(base.index, base.values, lw=1.6, color=GRIGIO)
    dd = s / s.cummax() - 1
    fondo = dd.idxmin()
    picco = s.loc[:fondo].idxmax()
    dopo = s.loc[fondo:]
    tornato = dopo[dopo >= s.loc[picco]]
    fine = tornato.index[0] if len(tornato) else s.index[-1]
    ax.axvspan(picco, fine, color=VERDE, alpha=0.12, zorder=0)
    tratto = base.loc[picco:fondo]
    ax.plot(tratto.index, tratto.values, lw=2.6, color=VERDE)
    ax.scatter([picco, fondo], [base.loc[picco], base.loc[fondo]], s=55,
               color=VERDE, zorder=4, edgecolor="white", linewidth=0.8)
    ax.set_title("Calmar guarda\nla caduta più profonda")
    ax.annotate(f"massimo drawdown\n{it(m['maxdd'] * 100, 1)}%",
                xy=(0.04, 0.82), xycoords="axes fraction", fontsize=10.5,
                fontweight="bold", color=VERDE)
    # scala logaritmica: su scala lineare una caduta del 50% avvenuta nel 2008,
    # quando l'indice valeva 180, sembra un graffio accanto ai valori di oggi
    ax.set_yscale("log")
    ax.set_yticks([100, 200, 400, 800, 1600])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_ylabel("valore, base 100 (scala logaritmica)")
    ax.grid(axis="x", visible=False)

    fig.suptitle("Gli stessi ventiquattro anni dell'S&P 500, tre modi di misurare il rischio",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out)
    plt.close(fig)


def plot_sei(t: pd.DataFrame, out: Path):
    nomi = [IT.get(n, n) for n in SEI]
    x = np.arange(len(SEI))
    larg = 0.26
    fig, ax = plt.subplots(figsize=(10.6, 6.0))
    for k, (col, colore, eti) in enumerate((("sharpe", NAVY, "Sharpe"),
                                            ("sortino", GOLD, "Sortino"),
                                            ("calmar", VERDE, "Calmar"))):
        v = [t.loc[n, col] for n in SEI]
        ax.bar(x + (k - 1) * larg, v, larg, label=eti, color=colore, alpha=0.88)
        for i, val in enumerate(v):
            ax.annotate(it(val, 2), xy=(x[i] + (k - 1) * larg, val),
                        xytext=(0, 4), textcoords="offset points", ha="center",
                        fontsize=8.8, color=colore, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(nomi, fontsize=10)
    ax.set_title("I tre indicatori su sei asset, agosto 2002 - agosto 2026")
    ax.set_ylabel("valore dell'indicatore")
    ax.set_ylim(0, 1.62)
    ax.legend(loc="upper right", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    ax.annotate("Le tre scale non sono confrontabili fra loro: un Sortino è quasi sempre "
                "più alto\ndello Sharpe dello stesso investimento, per come è costruito.",
                xy=(0.012, 0.90), xycoords="axes fraction", fontsize=9,
                color=GRIGIO, style="italic", va="bottom")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_sottoperiodi(sp: dict, out: Path):
    etichette = [f"{a[:4]}-{b[:4]}" for a, b in PERIODI]
    x = np.arange(len(QUATTRO))
    larg = 0.2
    colori = ["#93c5fd", "#60a5fa", "#2563eb", "#1e3a8a"]
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    for k, eti in enumerate(etichette):
        v = [sp[n][eti] for n in QUATTRO]
        ax.bar(x + (k - 1.5) * larg, v, larg, label=eti, color=colori[k])
        for i, val in enumerate(v):
            ax.annotate(it(val, 2), xy=(x[i] + (k - 1.5) * larg, val),
                        xytext=(0, 4 if val >= 0 else -13),
                        textcoords="offset points", ha="center", fontsize=8.6,
                        color=colori[k] if val >= 0 else ROSSO, fontweight="bold")
    ax.axhline(0, color="#334155", lw=1.1)
    ax.set_xticks(x)
    ax.set_xticklabels([IT.get(n, n) for n in QUATTRO], fontsize=10.5)
    ax.set_title("Lo stesso indice di Sharpe, calcolato su quattro periodi diversi")
    ax.set_ylabel("indice di Sharpe")
    ax.set_ylim(-0.85, 1.6)
    ax.legend(loc="upper right", frameon=False, fontsize=10, ncol=2)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    df, rf = carica()
    fin = df.loc[INIZIO:FINE]
    ammessi = [c for c in fin.columns
               if not fin[c].dropna().empty
               and fin[c].dropna().index[0] <= pd.Timestamp(SOGLIA)]

    t = pd.DataFrame({c: indicatori(fin[c], rf) for c in ammessi}).T.astype(float)

    sp = {}
    for n in QUATTRO:
        sp[n] = {}
        for a, b in PERIODI:
            sp[n][f"{a[:4]}-{b[:4]}"] = indicatori(df[n].loc[a:b], rf)["sharpe"]

    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    m = t.loc[ESEMPIO].to_dict()
    plot_denominatori(fin[ESEMPIO], m, OUT / "01_tre_denominatori.png")
    plot_sei(t, OUT / "02_sei_asset.png")
    plot_sottoperiodi(sp, OUT / "03_sottoperiodi.png")

    # controlli: se cadono, l'articolo afferma cose false
    assert t["sortino"].gt(t["sharpe"]).all(), \
        "il Sortino non e' piu' alto dello Sharpe su tutti gli asset"
    assert min(sp["Oro"].values()) < 0 < max(sp["Oro"].values()), \
        "l'oro non cambia segno fra i sottoperiodi"
    assert abs(m["sharpe"] * m["vol"] - m["eccesso"]) < 1e-9, \
        "la frazione dello Sharpe non torna"

    summary = {
        "finestra": {"dal": INIZIO[:7], "al": FINE[:7], "asset": len(ammessi),
                     "mesi": int(t["mesi"].iloc[0]),
                     "rf_medio_annuo": float(t["rf_medio"].iloc[0])},
        "esempio": {ESEMPIO: m},
        "indicatori": {n: t.loc[n].to_dict() for n in t.index},
        "intervalli": {k: {"min": float(t[k].min()), "mediana": float(t[k].median()),
                           "max": float(t[k].max()),
                           "chi_min": IT.get(t[k].idxmin(), t[k].idxmin()),
                           "chi_max": IT.get(t[k].idxmax(), t[k].idxmax())}
                       for k in ("sharpe", "sortino", "calmar")},
        "sottoperiodi": sp,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"finestra {INIZIO[:7]} -> {FINE[:7]}, {len(ammessi)} asset, "
          f"tasso privo di rischio medio {it(m['rf_medio'] * 100)}%")
    print(f"{ESEMPIO}: cagr {it(m['cagr']*100)}%  eccesso {it(m['eccesso']*100)}%  "
          f"vol {it(m['vol']*100)}%  semi {it(m['semi']*100)}%  "
          f"maxdd {it(m['maxdd']*100)}%")
    print(f"  Sharpe {it(m['sharpe'])}  Sortino {it(m['sortino'])}  "
          f"Calmar {it(m['calmar'])}")
    for k in ("sharpe", "sortino", "calmar"):
        q = summary["intervalli"][k]
        print(f"  {k:8s} da {it(q['min'])} ({q['chi_min']}) a {it(q['max'])} "
              f"({q['chi_max']}), mediana {it(q['mediana'])}")
    for n in QUATTRO:
        print(f"  {n:20s} " + "  ".join(f"{p} {it(v)}" for p, v in sp[n].items()))
    print(f"grafici in {OUT}")


if __name__ == "__main__":
    main()
