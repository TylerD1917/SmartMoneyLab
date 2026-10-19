# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Il rendimento a scadenza come prezzo d'ingresso:
cuscinetto, asimmetria e premio al rischio azionario (1871-2026)
=================================================================

PERCHE' SHILLER E NON LE NOSTRE GAMBE
  Gli indici ricostruiti negli studi precedenti partono dal 1962, e il 1962-2020
  contiene UNA SOLA grande discesa dei tassi. Qualunque affermazione del tipo
  "dopo un rendimento alto succede X" imparata li' dentro e' imparata da un
  episodio solo. Il dataset di Robert Shiller parte dal gennaio 1871 e contiene
  anche il 1941-1981, quarant'anni di tassi in salita: e' l'unico test contrario
  disponibile.

COSA COSTRUISCE
  1. indice azionario total return dell'S&P (prezzo + dividendi reinvestiti)
  2. indice obbligazionario a duration costante sul decennale, con lo stesso
     motore degli altri studi del sito (titolo alla pari comprato ogni mese)
  3. entrambi anche in termini reali, deflazionati col CPI
  4. CAPE e il suo inverso, l'earnings yield, come misura di valutazione azionaria

DUE DOMANDE
  A. il cuscinetto: al crescere del rendimento a scadenza d'ingresso, di quanto
     migliorano lo scenario buono e quello cattivo? (l'ipotesi e' che migliori
     molto piu' il cattivo)
  B. la frontiera: a quale combinazione di rendimento obbligazionario ed
     earnings yield azionario il premio al rischio delle azioni si azzera?

NOTE SUI DATI, da riportare nell'articolo
  - prima del 1953 i valori mensili di Shiller sono interpolati da dati annuali
    e il prezzo e' una media mensile, non una chiusura: volatilita' e drawdown
    dei primi ottant'anni risultano piu' lisci del vero
  - con un solo nodo di curva non modelliamo il roll-down, che sulle scadenze
    intermedie vale circa 0,42 punti l'anno (misurato in regola-2x-duration.py):
    l'indice e' prudente di quella quantita'
  - il file si ferma a settembre 2023; con orizzonte decennale l'ultimo mese di
    acquisto utile e' comunque il 2013

Uso:  python scripts/convessita-ytm-premio-azionario.py
"""
from __future__ import annotations

import os
import json
import datetime as dt
import importlib.util

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STUDIO = os.path.join(HERE, "quanto-rendono-etf-obbligazionari.py")
SHILLER = os.path.join(ROOT, "data", "Sp500", "shiller_ie_data.xls")

OUT = os.path.join(ROOT, "public", "charts", "convessita-ytm-premio-azionario")
M_BOND = 10.0          # scadenza del titolo alla pari: il decennale di Shiller


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def carica_shiller():
    d = pd.read_excel(SHILLER, sheet_name="Data", header=7)
    d = d[pd.to_numeric(d["Date"], errors="coerce").notna()].copy()
    anno = d["Date"].astype(float).astype(int)
    mese = ((d["Date"].astype(float) - anno) * 100).round().astype(int)
    d.index = pd.PeriodIndex(year=anno, month=mese, freq="M")
    out = pd.DataFrame({
        "P": pd.to_numeric(d["P"], errors="coerce"),
        "D": pd.to_numeric(d["D"], errors="coerce"),
        "E": pd.to_numeric(d["E"], errors="coerce"),
        "CPI": pd.to_numeric(d["CPI"], errors="coerce"),
        "y10": pd.to_numeric(d["Rate GS10"], errors="coerce"),
        "CAPE": pd.to_numeric(d["CAPE"], errors="coerce"),
    })
    return out.dropna(subset=["P", "CPI", "y10"])


def tr_azionario(d):
    """Total return dell'S&P: prezzo piu' un dodicesimo del dividendo annuo,
    reinvestito ogni mese. E' la costruzione standard su dati Shiller."""
    p, div = d["P"], d["D"].ffill()
    r = (p + div / 12) / p.shift(1) - 1
    return (1 + r.fillna(0)).cumprod()


# ------------------------------------------------------------------ utili
def ann(s, pos, mesi):
    """Rendimento annuo composto fra due punti della serie."""
    if pos + mesi >= len(s):
        return np.nan
    return ((s.iloc[pos + mesi] / s.iloc[pos]) ** (12 / mesi) - 1) * 100


def caduta(s, pos, mesi):
    """Massima perdita dal picco nei 'mesi' successivi all'acquisto."""
    if pos + mesi >= len(s):
        return np.nan
    seg = s.iloc[pos:pos + mesi + 1]
    return float((seg / seg.cummax() - 1).min() * 100)


def duration_modificata(Mm, yy, h=1e-5):
    p = lambda z: B.prezzo(z, yy, Mm)
    return (p(yy - h) - p(yy + h)) / (2 * h) / p(yy)


def convessita(Mm, yy, h=1e-4):
    """Curvatura della relazione prezzo-rendimento. Contrariamente
    all'intuizione e' massima quando i rendimenti sono bassi."""
    p = lambda z: B.prezzo(z, yy, Mm)
    return (p(yy + h) - 2 * p(yy) + p(yy - h)) / (h * h) / p(yy)


def anno_con_shock(Mm, y0, dy, mesi=12):
    """Rendimento di dodici mesi se il tasso passa linearmente da y0 a y0+dy."""
    path = np.linspace(y0, y0 + dy, mesi + 1)
    v = 100.0
    for t in range(1, mesi + 1):
        v *= B.prezzo(path[t], path[t - 1], Mm - 1 / 12) / 100
    return v / 100 - 1


def pareggio(Mm, y0):
    """Di quanto possono salire i tassi in un anno prima di andare in perdita."""
    lo, hi = 0.0, 0.40
    for _ in range(50):
        mid = (lo + hi) / 2
        if anno_con_shock(Mm, y0, mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def ols(X, z):
    c, *_ = np.linalg.lstsq(X, z, rcond=None)
    res = z - X @ c
    r2 = 1 - (res ** 2).sum() / ((z - z.mean()) ** 2).sum()
    return c, r2, res.std(ddof=X.shape[1])


# ---------------------------------------------------------------- grafici
NAVY = "#1e3a8a"; NERO = "#0f172a"; VERDE = "#047857"; GOLD = "#d97706"
ROSSO = "#dc2626"; GRIGIO = "#64748b"; CHIARO = "#cbd5e1"


def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_cuscinetto(tab, out):
    ys = [r["y"] * 100 for r in tab]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.8))
    ax.plot(ys, [r["giu"] * 100 for r in tab], lw=2.4, color=VERDE, marker="o", ms=5,
            label="i tassi scendono di 2 punti")
    ax.plot(ys, [r["fermi"] * 100 for r in tab], lw=2.4, color=GRIGIO, marker="o", ms=5,
            label="i tassi restano fermi")
    ax.plot(ys, [r["su"] * 100 for r in tab], lw=2.4, color=ROSSO, marker="o", ms=5,
            label="i tassi salgono di 2 punti")
    ax.axhline(0, color=NERO, lw=1.2)
    ax.set_xlabel("rendimento a scadenza il giorno dell'acquisto")
    ax.set_ylabel("rendimento dei 12 mesi successivi")
    ax.set_title("Lo stesso shock, prezzi d'ingresso diversi")
    ax.legend(frameon=False, fontsize=10, loc="center left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    a, b = tab[0], tab[-1]
    ax.annotate(f"lo scenario cattivo migliora di {it((b['su']-a['su'])*100,1)} punti,\n"
                f"quello buono solo di {it((b['giu']-a['giu'])*100,1)}",
                xy=(0.03, 0.06), xycoords="axes fraction", fontsize=9.5,
                color=GRIGIO, style="italic")

    ax2.plot(ys, [r["pareggio"] * 100 for r in tab], lw=2.6, color=NAVY, marker="o", ms=5)
    ax2.set_xlabel("rendimento a scadenza il giorno dell'acquisto")
    ax2.set_ylabel("punti di rialzo assorbibili in un anno")
    ax2.set_title("Quanto possono salire i tassi prima che tu perda")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}"))
    ax2.annotate("cresce più che proporzionalmente:\nla cedola sale e la duration scende",
                 xy=(0.03, 0.86), xycoords="axes fraction", va="top", fontsize=9.5,
                 color=GRIGIO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_nominale_reale(Y, NOM, REA, out):
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.0), sharex=True, sharey=True)
    for ax, z, tit, col in ((axes[0], NOM, "In termini nominali", NAVY),
                            (axes[1], REA, "In termini reali", GOLD)):
        ax.scatter(Y, z, s=9, alpha=0.3, color=col, edgecolor="none")
        xx = np.linspace(Y.min(), Y.max(), 50)
        b, a = np.polyfit(Y, z, 1)
        r2 = np.corrcoef(Y, z)[0, 1] ** 2
        ax.plot(xx, xx, lw=1.6, ls="--", color=GRIGIO, label="bisettrice")
        ax.plot(xx, a + b * xx, lw=2.4, color=col,
                label=f"osservata: pendenza {it(b)}, R² {it(r2)}")
        ax.axhline(0, color=NERO, lw=1)
        ax.set_title(tit)
        ax.set_xlabel("rendimento a scadenza all'acquisto")
        ax.legend(frameon=False, fontsize=9.5, loc="upper left")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
    axes[0].set_ylabel("rendimento annuo dei 10 anni successivi")
    fig.suptitle("Il prezzo d'ingresso predice quasi tutto del nominale e poco del reale",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out); plt.close(fig)


def plot_due_coorti(ob_r, out, a="1971-09", b="1981-09", mesi=120):
    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    for et, col in ((a, ROSSO), (b, VERDE)):
        pos = ob_r.index.get_loc(pd.Period(et, "M"))
        seg = ob_r.iloc[pos:pos + mesi + 1]
        base = seg / seg.iloc[0] * 100
        x = np.arange(len(base)) / 12
        ax.plot(x, base.values, lw=2.6, color=col)
        ax.annotate(f"acquisto {et}\n{it(base.iloc[-1] / 100, 2)}x in dieci anni",
                    xy=(x[-1], base.iloc[-1]), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=10.5, fontweight="bold", color=col)
    ax.axhline(100, color=NERO, lw=1.2)
    ax.set_xlabel("anni dall'acquisto")
    ax.set_ylabel("potere d'acquisto, base 100")
    ax.set_title("Due acquisti a rendimento alto, dieci anni di distanza")
    ax.annotate("entrambi compravano un decennale che sembrava generoso:\n"
                "il 6,14% del 1971 e il 15,32% del 1981",
                xy=(0.03, 0.9), xycoords="axes fraction", va="top", fontsize=9.5,
                color=GRIGIO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_chi_ordina(YY, EY, CA, DIF, oggi, out):
    """Il test decisivo: quale delle due valutazioni ordina davvero il premio.
    I punti con CAPE sopra 30 sono evidenziati perche' sono l'unico posto in
    cui le obbligazioni hanno davvero vinto."""
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 6.2), sharey=True)
    caro = CA > 30
    for ax, x, xo, tit, xl in (
            (axes[0], YY, oggi["y"], "Il prezzo delle obbligazioni",
             "rendimento del decennale all'acquisto"),
            (axes[1], EY, oggi["ey"], "Il prezzo delle azioni",
             "earnings yield azionario all'acquisto (1 diviso CAPE)")):
        ax.scatter(x[~caro], DIF[~caro], s=11, alpha=0.28, color=NAVY, edgecolor="none",
                   label="CAPE sotto 30")
        ax.scatter(x[caro], DIF[caro], s=22, alpha=0.85, color=ROSSO, edgecolor="none",
                   label="CAPE sopra 30")
        xx = np.linspace(x.min(), x.max(), 50)
        b, a = np.polyfit(x, DIF, 1)
        r2 = np.corrcoef(x, DIF)[0, 1] ** 2
        ax.plot(xx, a + b * xx, lw=2.6, color=NERO,
                label=f"pendenza {it(b)}, R² {it(r2, 3)}")
        ax.axhline(0, color=GRIGIO, lw=1.4)
        ax.axvline(xo, color=GOLD, lw=2.2, ls="--", label="oggi")
        ax.set_title(tit)
        ax.set_xlabel(xl)
        ax.legend(frameon=False, fontsize=9.5, loc="upper right")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    axes[0].set_ylabel("premio delle azioni nei 10 anni dopo, punti all'anno")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}"))
    fig.suptitle("Quale dei due prezzi decide chi vince nei dieci anni successivi",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(out); plt.close(fig)


def plot_secchi_cape(secchi, oggi, out):
    fig, ax = plt.subplots(figsize=(11.4, 6.4))
    et = [s["et"] for s in secchi]
    val = [s["mediana"] for s in secchi]
    col = [ROSSO if v < 0 else NAVY for v in val]
    b = ax.bar(range(len(val)), val, 0.62, color=col)
    for i, s in enumerate(secchi):
        ax.annotate(f"{it(s['mediana'])}", xy=(i, s["mediana"]),
                    xytext=(0, 6 if s["mediana"] > 0 else -18), textcoords="offset points",
                    ha="center", fontsize=11, fontweight="bold", color=col[i])
        # tutte le didascalie sulla stessa linea in basso: sopra la barra
        # rossa non ci starebbero
        ax.annotate(f"azioni avanti\nnel {s['vincono']:.0f}% dei casi\nn = {s['n']}",
                    xy=(i, min(val) * 1.62), ha="center", va="center",
                    fontsize=9, color=GRIGIO)
    ax.axhline(0, color=NERO, lw=1.2)
    ax.set_xticks(range(len(et))); ax.set_xticklabels(et)
    ax.set_xlabel("CAPE il giorno dell'acquisto")
    ax.set_ylabel("premio mediano delle azioni, punti all'anno")
    ax.set_title("Il premio al rischio azionario per livello di valutazione di partenza")
    ax.set_ylim(min(val) * 1.9, max(val) * 1.25)
    ax.grid(axis="x", visible=False)
    ax.annotate(f"oggi il CAPE è {it(oggi['cape'], 1)}", xy=(len(et) - 1, max(val) * 1.1),
                ha="center", fontsize=11, fontweight="bold", color=ROSSO)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    _stile()
    ris = {"generato": dt.date.today().isoformat()}

    d = carica_shiller()
    az_n = tr_azionario(d)
    ob_n = B.indice(d["y10"], M_BOND)
    cpi, y, cape = d["CPI"], d["y10"], d["CAPE"]
    az_r, ob_r = az_n / cpi, ob_n / cpi
    anni_tot = len(d) / 12
    print(f"Shiller {d.index.min()} -> {d.index.max()} ({len(d)} mesi)")
    cagr = lambda s: ((s.iloc[-1] / s.iloc[0]) ** (1 / anni_tot) - 1) * 100
    print(f"  azionario {cagr(az_n):.2f}% nominale / {cagr(az_r):.2f}% reale")
    print(f"  obbligazionario {cagr(ob_n):.2f}% nominale / {cagr(ob_r):.2f}% reale")
    print(f"  inflazione {cagr(cpi):.2f}%")
    ris["indici"] = {"da": str(d.index.min()), "a": str(d.index.max()),
                     "azioni_nom": cagr(az_n), "azioni_reale": cagr(az_r),
                     "bond_nom": cagr(ob_n), "bond_reale": cagr(ob_r),
                     "inflazione": cagr(cpi)}

    # ------------------------------------------------------- validazione
    print(f"\n{'='*84}\n  VALIDAZIONE\n{'='*84}")
    dgs10 = B.mensile("DGS10.csv")
    k = d.index.intersection(dgs10.index)
    sc = d.loc[k, "y10"] - dgs10[k]
    ob_fred, ob_sh = B.indice(dgs10[k], M_BOND), B.indice(d.loc[k, "y10"], M_BOND)
    a_k = len(k) / 12
    cg = lambda s: ((s.iloc[-1] / s.iloc[0]) ** (1 / a_k) - 1) * 100
    print(f"  tasso Shiller contro DGS10 ({len(k)} mesi): scarto medio {sc.mean():+.3f} punti, "
          f"massimo {sc.abs().max():.2f}, correlazione {d.loc[k,'y10'].corr(dgs10[k]):.4f}")
    print(f"  indice costruito sulle due serie: {cg(ob_sh):.2f}% contro {cg(ob_fred):.2f}% annuo "
          f"({cg(ob_sh)-cg(ob_fred):+.3f} punti)")
    gambe, _x, _r = B.costruisci()
    k2 = ob_n.index.intersection(gambe["USA 7-10"].index)
    a2 = len(k2) / 12
    c2 = lambda s: ((s[k2].iloc[-1] / s[k2].iloc[0]) ** (1 / a2) - 1) * 100
    print(f"  contro il nostro indice USA 7-10: {c2(ob_n):.2f}% contro {c2(gambe['USA 7-10']):.2f}% "
          f"({c2(ob_n)-c2(gambe['USA 7-10']):+.2f} punti, atteso negativo: niente roll-down)")
    ris["validazione"] = {"scarto_tasso": float(sc.mean()), "corr_tasso": float(d.loc[k,'y10'].corr(dgs10[k])),
                          "indice_shiller": cg(ob_sh), "indice_fred": cg(ob_fred),
                          "contro_usa710": float(c2(ob_n) - c2(gambe["USA 7-10"]))}
    assert abs(sc.mean()) < 0.05, "il tasso di Shiller non coincide con FRED"
    assert abs(cg(ob_sh) - cg(ob_fred)) < 0.25, "i due indici divergono troppo"

    # ------------------------------------------------- A1. il cuscinetto
    print(f"\n{'='*84}\n  A1. IL CUSCINETTO, ARITMETICA PURA (titolo alla pari a 10 anni)\n{'='*84}")
    print(f"  {'Y':>4} {'duration':>9} {'convessita':>11} {'pareggio 1 anno':>16} | "
          f"{'-2pp':>8} {'fermi':>8} {'+2pp':>8}")
    tab = []
    for Y in (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10):
        r = {"y": Y, "D": duration_modificata(M_BOND, Y), "C": convessita(M_BOND, Y),
             "pareggio": pareggio(M_BOND, Y),
             "giu": anno_con_shock(M_BOND, Y, -0.02), "fermi": anno_con_shock(M_BOND, Y, 0.0),
             "su": anno_con_shock(M_BOND, Y, 0.02)}
        tab.append(r)
        print(f"  {Y*100:3.0f}% {r['D']:9.2f} {r['C']:11.1f} {r['pareggio']*100:14.2f}pp | "
              f"{r['giu']*100:+7.2f}% {r['fermi']*100:+7.2f}% {r['su']*100:+7.2f}%")
    ris["cuscinetto"] = tab

    # ------------------------------- A2/A3. nominale contro reale sul vero
    idx = [i for i in range(len(y)) if i + 120 < len(y)]
    Y = y.iloc[idx].to_numpy()
    NOM = np.array([ann(ob_n, i, 120) for i in idx])
    REA = np.array([ann(ob_r, i, 120) for i in idx])
    INF = np.array([ann(cpi, i, 120) for i in idx])
    DD5 = np.array([caduta(ob_r, i, 60) for i in idx])
    date = y.index[idx]
    print(f"\n{'='*84}\n  A2. IL PREZZO D'INGRESSO PREVEDE IL NOMINALE, NON IL REALE\n"
          f"      ({len(idx)} mesi di acquisto, {date[0]} -> {date[-1]})\n{'='*84}")
    ris["predittivita"] = {}
    for nome, z in (("nominale", NOM), ("reale", REA), ("inflazione seguita", INF)):
        b, a = np.polyfit(Y, z, 1); r2 = np.corrcoef(Y, z)[0, 1] ** 2
        ent = float((np.abs(z - Y) <= 2).mean() * 100)
        ris["predittivita"][nome] = {"pendenza": b, "intercetta": a, "r2": r2, "entro2": ent}
        print(f"  {nome:20s}: pendenza {b:+.2f}  R2 {r2:.2f}" +
              (f"  entro 2 punti nel {ent:.0f}% dei casi" if nome != "inflazione seguita" else ""))

    print(f"\n  per livello d'ingresso (rendimento REALE annuo dei 10 anni dopo):")
    print(f"  {'ingresso':>10} {'n':>5} | {'p10':>7} {'mediana':>8} {'p90':>7} | {'in perdita':>11} "
          f"| {'caduta peggiore':>16}")
    ris["secchi"] = []
    for lo, hi in ((0, 3), (3, 4), (4, 5), (5, 6), (6, 8), (8, 20)):
        m = (Y >= lo) & (Y < hi)
        if m.sum() < 24:
            continue
        q = np.percentile(REA[m], [10, 50, 90])
        dm = date[m]
        riga = {"da": lo, "a": hi, "n": int(m.sum()), "p10": q[0], "mediana": q[1], "p90": q[2],
                "perdenti": float((REA[m] < 0).mean() * 100), "dd": float(np.nanmin(DD5[m])),
                "infl": float(np.median(INF[m])), "nominale": float(np.median(NOM[m])),
                "primo_acquisto": str(dm[0]), "ultimo_acquisto": str(dm[-1])}
        ris["secchi"].append(riga)
        print(f"  {lo:2.0f}-{hi:2.0f}%{'':>3} {m.sum():5d} | {q[0]:+6.2f}% {q[1]:+7.2f}% {q[2]:+6.2f}% | "
              f"{(REA[m]<0).mean()*100:10.1f}% | {np.nanmin(DD5[m]):15.1f}%")

    print("\n  i cinque decenni reali peggiori e i cinque migliori:")
    ris["estremi"] = {"peggiori": [], "migliori": []}
    for et, ordine in (("peggiori", np.argsort(REA)[:5]), ("migliori", np.argsort(REA)[-5:][::-1])):
        for i in ordine:
            v = {"data": str(date[i]), "ingresso": float(Y[i]), "reale": float(REA[i]),
                 "nominale": float(NOM[i]), "inflazione": float(INF[i])}
            ris["estremi"][et].append(v)
            print(f"    {et[:4]}  {date[i]}  ingresso {Y[i]:5.2f}%  reale {REA[i]:+6.2f}%  "
                  f"(nominale {NOM[i]:+5.2f}%, inflazione {INF[i]:+5.2f}%)")

    # ----------------------------------------------------- B. frontiera
    print(f"\n{'='*84}\n  B. LA FRONTIERA AZIONI-OBBLIGAZIONI\n{'='*84}")
    i2 = [i for i in idx if np.isfinite(cape.iloc[i]) and cape.iloc[i] > 0]
    EQ = np.array([ann(az_r, i, 120) for i in i2])
    BO = np.array([ann(ob_r, i, 120) for i in i2])
    DIF = EQ - BO
    YY = y.iloc[i2].to_numpy()
    EY = 100 / cape.iloc[i2].to_numpy()
    dd = y.index[i2]
    X = np.column_stack([np.ones(len(YY)), YY, EY])
    coef, r2, sd = ols(X, DIF)
    EQn = np.array([ann(az_n, i, 120) for i in i2])
    BOn = np.array([ann(ob_n, i, 120) for i in i2])
    scarto_rn = float(np.mean(np.abs(DIF - (EQn - BOn))))
    ris["frontiera_scarto_reale_nominale"] = scarto_rn
    print(f"  {len(DIF)} mesi di acquisto, {dd[0]} -> {dd[-1]}")
    print(f"  premio reale contro premio nominale: differenza media {scarto_rn:.3f} punti")
    print(f"  premio azioni meno obbligazioni: medio {DIF.mean():+.2f}, mediana {np.median(DIF):+.2f}, "
          f"negativo nel {(DIF<0).mean()*100:.0f}% dei mesi")
    print(f"  premio = {coef[0]:+.2f} {coef[1]:+.2f}*ytm {coef[2]:+.2f}*ey   R2 {r2:.2f}  "
          f"scarto tipico dei residui {sd:.2f}")
    print(f"  frontiera: ytm = {-coef[0]/coef[1]:.2f} + {-coef[2]/coef[1]:.2f} * ey")
    sp = EY - YY
    b1, a1 = np.polyfit(sp, DIF, 1)
    r1 = np.corrcoef(sp, DIF)[0, 1] ** 2
    print(f"  versione a una variabile (spread ey - ytm): premio = {a1:+.2f} {b1:+.2f}*spread  "
          f"R2 {r1:.2f}, pareggio a spread {-a1/b1:+.2f}")
    ris["frontiera"] = {"n": len(DIF), "da": str(dd[0]), "a": str(dd[-1]),
                        "premio_medio": float(DIF.mean()), "premio_mediano": float(np.median(DIF)),
                        "quota_negativa": float((DIF < 0).mean() * 100),
                        "coef": [float(c) for c in coef], "r2": float(r2), "sd": float(sd),
                        "spread": {"a": float(a1), "b": float(b1), "r2": float(r1),
                                   "pareggio": float(-a1 / b1)}}

    meta = {}
    print("\n  stabilita':")
    for et, lo, hi in (("1881-1944", 1881, 1945), ("1945-2013", 1945, 2017)):
        m = np.array([lo <= p.year < hi for p in dd])
        c, rr, ss = ols(X[m], DIF[m])
        meta[et] = c
        print(f"    {et} (n={m.sum():4d}, CAPE da {cape.iloc[i2][m].min():.1f} a "
              f"{cape.iloc[i2][m].max():.1f}): b {c[1]:+.2f} c {c[2]:+.2f} R2 {rr:.2f}, "
              f"pareggio a ey=4%: ytm {(-c[0]-c[2]*4)/c[1]:.2f}%")
        ris["frontiera"][et] = {"coef": [float(x) for x in c], "r2": float(rr), "sd": float(ss),
                                "n": int(m.sum()), "cape_min": float(cape.iloc[i2][m].min()),
                                "cape_max": float(cape.iloc[i2][m].max())}

    giu = (X @ coef) < 0
    print(f"\n  il modello ha previsto la vittoria delle obbligazioni in {giu.sum()} mesi su {len(DIF)}; "
          f"hanno vinto nel {(DIF[giu]<0).mean()*100:.0f}% dei casi" if giu.sum() else "")
    print(f"  accuratezza del segno {np.mean(np.sign(X@coef)==np.sign(DIF))*100:.0f}%, "
          f"contro un {max((DIF>0).mean(),(DIF<0).mean())*100:.0f}% di chi avesse sempre detto 'azioni'")
    ris["frontiera"]["previsioni_bond"] = int(giu.sum())
    ris["frontiera"]["azzeccate_bond"] = float((DIF[giu] < 0).mean() * 100) if giu.sum() else None
    ris["frontiera"]["accuratezza"] = float(np.mean(np.sign(X @ coef) == np.sign(DIF)) * 100)
    ris["frontiera"]["base_rate"] = float(max((DIF > 0).mean(), (DIF < 0).mean()) * 100)

    print("\n  chi ordina il premio, una variabile alla volta:")
    ris["ordinamento"] = {}
    for nome, x in (("rendimento del decennale", YY), ("earnings yield", EY)):
        b, a = np.polyfit(x, DIF, 1)
        rr = np.corrcoef(x, DIF)[0, 1] ** 2
        ris["ordinamento"][nome] = {"pendenza": float(b), "r2": float(rr)}
        print(f"    {nome:26s}: pendenza {b:+.2f}  R2 {rr:.3f}")

    CA = cape.iloc[i2].to_numpy()
    print("\n  premio per livello di rendimento obbligazionario:")
    ris["secchi_ytm"] = []
    for lo, hi in ((0, 3), (3, 4), (4, 5), (5, 6), (6, 8), (8, 20)):
        m = (YY >= lo) & (YY < hi)
        if m.sum() < 24:
            continue
        r = {"et": f"{lo}-{hi}%", "n": int(m.sum()), "mediana": float(np.median(DIF[m])),
             "vincono": float((DIF[m] > 0).mean() * 100)}
        ris["secchi_ytm"].append(r)
        print(f"    {r['et']:>7} n={r['n']:4d}  premio mediano {r['mediana']:+6.2f}  "
              f"azioni avanti nel {r['vincono']:3.0f}%")

    print("\n  premio per livello di CAPE:")
    ris["cape"] = []
    for lo, hi in ((0, 10), (10, 15), (15, 20), (20, 25), (25, 30), (30, 99)):
        m = (CA >= lo) & (CA < hi)
        if m.sum() < 24:
            continue
        aa = sorted(set(p.year for p in dd[m]))
        r = {"et": f"{lo}-{hi}" if hi < 99 else "oltre 30", "n": int(m.sum()),
             "mediana": float(np.median(DIF[m])), "vincono": float((DIF[m] > 0).mean() * 100),
             "anni": f"{aa[0]}-{aa[-1]}", "n_anni": len(aa)}
        ris["cape"].append(r)
        print(f"    {r['et']:>8} n={r['n']:4d}  premio mediano {r['mediana']:+6.2f}  "
              f"azioni avanti nel {r['vincono']:3.0f}%   acquisti {r['anni']} ({r['n_anni']} anni)")

    i81 = list(dd).index(pd.Period("1981-09", "M"))
    print(f"\n  il picco di 155 anni, settembre 1981: decennale {YY[i81]:.2f}%, CAPE {CA[i81]:.1f}")
    print(f"    azioni {EQ[i81]:+.2f}% reale contro obbligazioni {BO[i81]:+.2f}%: "
          f"premio {DIF[i81]:+.2f} punti, hanno vinto le azioni")
    ris["settembre1981"] = {"ytm": float(YY[i81]), "cape": float(CA[i81]),
                            "azioni": float(EQ[i81]), "bond": float(BO[i81]),
                            "premio": float(DIF[i81])}

    # ------------------------------------------------------------- oggi
    oggi_y = float(dgs10.iloc[-1])
    pe = pd.read_csv(os.path.join(ROOT, "data", "Shiller_PE", "Shiller_PE_montly.csv"))
    pe["v"] = pe["Value"].astype(str).str.replace(",", ".").astype(float)
    oggi_cape = float(pe["v"].iloc[0])
    oggi = {"y": oggi_y, "cape": oggi_cape, "ey": 100 / oggi_cape,
            "data_y": str(dgs10.index[-1]), "data_cape": str(pe["Date"].iloc[0])}
    print(f"\n  OGGI: decennale {oggi_y:.2f}% ({oggi['data_y']}), CAPE {oggi_cape:.2f} "
          f"({oggi['data_cape']}) -> earnings yield {oggi['ey']:.2f}%")
    for et, c in (("intero campione", coef), ("solo 1945-2013", meta["1945-2013"])):
        prev = c[0] + c[1] * oggi_y + c[2] * oggi["ey"]
        front = (-c[0] - c[2] * oggi["ey"]) / c[1]
        print(f"    {et:18s}: pareggio al ytm {front:.2f}%, premio previsto {prev:+.2f} punti l'anno")
        oggi[et] = {"frontiera": float(front), "premio": float(prev)}
    sp_oggi = oggi["ey"] - oggi["y"]
    oggi["spread"] = float(sp_oggi)
    oggi["percentile_spread"] = float((sp < sp_oggi).mean() * 100)
    oggi["tasso_massimo"] = {"valore": float(y.max()), "quando": str(y.idxmax())}
    print(f"    spread di oggi {sp_oggi:+.2f}: piu' basso che nel "
          f"{100 - oggi['percentile_spread']:.0f}% dei mesi dal 1881")
    print(f"    massimo storico del decennale: {y.max():.2f}% in {y.idxmax()}")
    ris["oggi"] = oggi

    # ---------------------------------------------------------- grafici
    print(f"\n{'='*84}\n  GRAFICI\n{'='*84}")
    plot_cuscinetto(tab, os.path.join(OUT, "01_cuscinetto.png"))
    plot_nominale_reale(Y, NOM, REA, os.path.join(OUT, "02_nominale_reale.png"))
    plot_due_coorti(ob_r, os.path.join(OUT, "03_due_coorti.png"))
    plot_chi_ordina(YY, EY, cape.iloc[i2].to_numpy(), DIF, oggi,
                    os.path.join(OUT, "04_chi_ordina.png"))
    plot_secchi_cape(ris["cape"], oggi, os.path.join(OUT, "05_cape.png"))
    for f in sorted(os.listdir(OUT)):
        print(f"    {f}")

    with open(os.path.join(OUT, "sintesi.json"), "w", encoding="utf-8") as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, allow_nan=False, default=float)
    print(f"\n[ok] sintesi -> {os.path.join(OUT, 'sintesi.json')}")


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("bond", STUDIO)
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)
    main()
