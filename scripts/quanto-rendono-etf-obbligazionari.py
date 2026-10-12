# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Quanto rendono gli ETF obbligazionari su finestre di 5, 10, 15 e 20 anni
=========================================================================================

Gli ETF obbligazionari a duration costante esistono da troppo poco per un'analisi
seria su finestre lunghe: TLT dal 2002, i due europei dal 2008-2009. Qui si
ricostruisce l'indice che quegli ETF replicano, a partire dai rendimenti dei
titoli di Stato, per avere 46-64 anni di storia invece di 17-24.

COME SI COSTRUISCE UNA GAMBA
----------------------------
Ogni mese si compra un titolo alla pari con scadenza M anni (cedola = rendimento
del momento). Un mese dopo lo si rivaluta al nuovo rendimento con scadenza
residua M-1/12, e si rinnova a M. La duration resta ferma: e' esattamente quello
che fa un ETF a duration costante. Il prezzo e' il valore attuale SPORCO dei
flussi residui, quindi il rateo e' dentro e non va sommato (sommarlo raddoppia
il carry: errore trovato e corretto in fase di validazione).

ROLL-DOWN. Un indice vero guadagna anche scivolando lungo la curva: un titolo
comprato a 10 anni e venduto a 7 si rivaluta a un rendimento piu' basso se la
curva e' inclinata. Dove ho due nodi di curva (USA 7-10, via DGS7 e DGS10) il
roll-down e' modellato interpolando. Dove ho un solo nodo (area euro, Italia)
non lo e', e l'indice risulta prudente.

VALIDAZIONE CONTRO GLI ETF VERI (periodo di sovrapposizione)
  IEF  (USA 7-10, 2002-2026)  scarto -0,05 punti/anno, tracking 0,81%, corr 0,993
  TLT  (USA 20+,  2002-2026)  scarto +0,16 punti/anno, tracking 1,73%, corr 0,992
                              (+0,16 e' il TER di TLT: e' il risultato atteso)
  SXRQ (euro 7-10, 2009-2026) scarto -0,01 punti/anno, corr 0,600
La correlazione bassa su SXRQ non e' un errore: i rendimenti europei OCSE sono
MEDIE MENSILI e non valori di fine mese, quindi il mese singolo e' sfasato. Sul
livello di lungo periodo non cambia niente (misurato sugli USA: +0,06 punti di
CAGR, 0,03 sulle mediane delle finestre), ma vieta statistiche mensili sulle
gambe europee.

I LIMITI, TUTTI MISURATI
  1. La gamba Italia 15+ prezza un ventennale col rendimento a DIECI anni,
     perche' una curva italiana lunga con quarant'anni di storia non esiste.
     Costo misurato sulla curva BCE 2004-2026: -0,72 punti/anno. E' una
     SOTTOSTIMA, quindi jugando a favore della tesi dell'articolo.
  2. Prima del novembre 1993 quella gamba descrive uno strumento che in Italia
     non c'era: nel 1993 la vita media del debito pubblico era 3,3 anni e la
     duration 1,6, col 65% in BOT e CCT (fonte MEF). Nei grafici il tratto
     ante-1993 e' TRATTEGGIATO e le statistiche sono date in doppia versione.
  3. Prima del 1999 l'Italia e' in lire.
  4. Tutto LORDO di costi e imposte.
  5. Le finestre mobili si sovrappongono: descrivono il passato, non sono
     probabilita'.

DATI (scaricati da scripts/data/scarica_dati_bond.py)
  DGS7, DGS10, DGS20, DGS30   Treasury constant maturity, FRED
  IRLTLT01EZM156N             area euro, rendimento governativo lungo, OCSE
  INTGSBITM193N + IRLTLT01ITM156N   Italia, FMI fino al 1991 poi OCSE
  ITACPIALLMINMEI             prezzi al consumo Italia, OCSE (si ferma a 03/2025)
  TLT, IEF, SXRQ, IBGL        ETF reali, Yahoo, prezzi aggiustati

OUTPUT in public/charts/quanto-rendono-etf-obbligazionari/
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
B = os.path.join(ROOT, "data", "Bonds")
SLUG = "quanto-rendono-etf-obbligazionari"
OUT = os.path.join(ROOT, "public", "charts", SLUG)

FREQ = 2
ORIZZONTI = (5, 10, 15, 20)
PASSO = 3                      # finestre mobili a passo trimestrale
ITA_VERA = pd.Period("1993-11", "M")   # da qui i BTP lunghi esistono davvero

NAVY = "#1e3a8a"; GOLD = "#d97706"; ROSSO = "#dc2626"
VERDE = "#047857"; GRIGIO = "#64748b"; CHIARO = "#cbd5e1"
COLORI = {"USA 7-10": NAVY, "USA 20+": "#0f172a",
          "Area euro 7-10": VERDE, "Italia 15+": GOLD}


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ------------------------------------------------------------------ motore
def prezzo(ytm, cedola, anni, face=100.0, freq=FREQ):
    """Valore attuale sporco dei flussi residui: il rateo e' gia' dentro."""
    n_tot = anni * freq
    if n_tot <= 0:
        return face
    c = cedola / freq * face
    r = ytm / freq
    k = int(np.ceil(n_tot - 1e-9))
    t = n_tot - np.arange(k - 1, -1, -1)
    return float((c / (1 + r) ** t).sum() + face / (1 + r) ** n_tot)


def indice(y_acq, M, y_val=None):
    """Indice total return a duration costante. y_val diverso da y_acq
    significa modellare il roll-down lungo la curva."""
    y_val = y_acq if y_val is None else y_val.reindex(y_acq.index)
    v = np.empty(len(y_acq)); v[0] = 100.0
    a = y_acq.to_numpy() / 100.0; b = y_val.to_numpy() / 100.0
    for t in range(1, len(a)):
        v[t] = v[t - 1] * (prezzo(b[t], a[t - 1], M - 1 / 12) / 100.0)
    return pd.Series(v, index=y_acq.index)


def mensile(f, how="last"):
    d = pd.read_csv(os.path.join(B, f)); c = d.columns
    d["m"] = pd.PeriodIndex(pd.to_datetime(d[c[0]]), freq="M")
    s = pd.to_numeric(d[c[1]], errors="coerce")
    g = pd.Series(s.values, index=d["m"]).dropna().groupby(level=0)
    return g.last() if how == "last" else g.mean()


def etf(f):
    d = pd.read_csv(os.path.join(B, f))
    d["m"] = pd.PeriodIndex(pd.to_datetime(d["Date"]), freq="M")
    return d.groupby("m")["Close"].last()


def cagr(s):
    return (s.iloc[-1] / s.iloc[0]) ** (12 / (len(s) - 1)) - 1


def interp(y_corto, y_lungo, m_corto, m_lungo, m_target):
    w = (m_target - m_corto) / (m_lungo - m_corto)
    return (1 - w) * y_corto + w * y_lungo.reindex(y_corto.index)


def finestre(s, anni, passo=PASSO):
    m = anni * 12
    return (((s.shift(-m) / s) ** (1 / anni) - 1).dropna() * 100).iloc[::passo]


def statistiche(f):
    q = np.percentile(f, [5, 25, 50, 75, 95])
    return {"n": int(len(f)), "mediana": float(q[2]), "media": float(f.mean()),
            "p5": float(q[0]), "p25": float(q[1]), "p75": float(q[3]),
            "p95": float(q[4]), "peggio": float(f.min()), "peggio_da": str(f.idxmin()),
            "meglio": float(f.max()), "meglio_da": str(f.idxmax()),
            "quota_negative": float(100 * (f < 0).mean())}


# -------------------------------------------------------------------- dati
def costruisci():
    d7 = mensile("DGS7_fred_1969.csv"); d10 = mensile("DGS10.csv")
    d20g = mensile("DGS20_fred_1962.csv"); d30 = mensile("DGS30_fred_1977.csv")

    # il ventennale non e' stato emesso fra il 1987 e il 1993: il buco si tappa
    # incatenando le VARIAZIONI del trentennale, cosi' non nasce un gradino
    pieno = pd.period_range(d20g.index[0], max(d20g.index[-1], d30.index[-1]), freq="M")
    y20 = pd.Series(np.nan, index=pieno); y20.loc[d20g.index] = d20g.values
    for m in y20[y20.isna()].index:
        p = m - 1
        if p in y20.index and not np.isnan(y20[p]) and m in d30.index and p in d30.index:
            y20[m] = y20[p] + (d30[m] - d30[p])
    y20 = y20.dropna()

    itl = pd.concat([mensile("IT10Y_imf_1980.csv").loc[:pd.Period("1991-02", "M")],
                     mensile("IT10Y_oecd_1991.csv")]).groupby(level=0).last().sort_index()
    ez = mensile("EZ10Y_oecd_1970.csv")

    ya = interp(d7, d10, 7, 10, 8.5).dropna()
    yv = interp(d7, d10, 7, 10, 8.5 - 1 / 12).dropna()
    k = ya.index.intersection(yv.index)

    gambe = {
        "USA 7-10": indice(ya[k], 8.5, yv[k]),
        "USA 20+": indice(y20, 24),
        "Area euro 7-10": indice(ez, 8.5),
        "Italia 15+": indice(itl, 20),
    }
    extra = {
        "Italia 7-10": indice(itl, 8.5),
        "Italia 15+ (dal 1993)": indice(itl[itl.index >= ITA_VERA], 20),
    }
    rendimenti = {"USA 7-10": ya[k], "USA 20+": y20, "Area euro 7-10": ez, "Italia 15+": itl}
    return gambe, extra, rendimenti


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_curve(gambe, out):
    fig, ax = plt.subplots(figsize=(10.6, 6.4))
    for n, s in gambe.items():
        b = s / s.iloc[0] * 100
        if n == "Italia 15+":
            pre = b[b.index <= ITA_VERA]; post = b[b.index >= ITA_VERA]
            ax.plot(pre.index.to_timestamp(), pre.values, lw=1.6, ls=":", color=COLORI[n])
            ax.plot(post.index.to_timestamp(), post.values, lw=2.0, color=COLORI[n], label=n)
        else:
            ax.plot(b.index.to_timestamp(), b.values, lw=2.0, color=COLORI[n], label=n)
        dy = {"USA 20+": 7, "USA 7-10": -7}.get(n, 0)   # le due serie USA arrivano quasi allo stesso punto
        ax.annotate(f"{b.iloc[-1] / 100:.0f}x", xy=(b.index[-1].to_timestamp(), b.iloc[-1]),
                    xytext=(7, dy), textcoords="offset points", va="center",
                    fontsize=10, fontweight="bold", color=COLORI[n])
    ax.set_yscale("log")
    ax.set_yticks([100, 300, 1000, 3000, 10000])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_title("Quattro ETF obbligazionari ricostruiti, base 100 alla partenza")
    ax.set_ylabel("valore, scala logaritmica")
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    ax.annotate("il tratto punteggiato dell'Italia è anteriore al novembre 1993,\n"
                "quando i titoli di Stato italiani a lunga scadenza non esistevano ancora",
                xy=(0.985, 0.045), xycoords="axes fraction", ha="right", fontsize=9,
                color=GRIGIO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_ventagli(stats, out):
    """Cinque pannelli: le quattro gambe piu' la versione severa dell'Italia,
    che parte dal 1993. Metterle accanto e' il modo piu' diretto di mostrare
    quanto pesa la data di partenza."""
    pannelli = list(COLORI) + ["Italia 15+ (dal 1993)"]
    colori = dict(COLORI); colori["Italia 15+ (dal 1993)"] = "#92400e"
    fig, axes = plt.subplots(1, 5, figsize=(15.8, 5.6), sharey=True)
    for ax, n in zip(axes, pannelli):
        COLORI_LOC = colori
        x = np.arange(len(ORIZZONTI))
        p5 = [stats[(n, a)]["p5"] for a in ORIZZONTI]
        p25 = [stats[(n, a)]["p25"] for a in ORIZZONTI]
        p50 = [stats[(n, a)]["mediana"] for a in ORIZZONTI]
        p75 = [stats[(n, a)]["p75"] for a in ORIZZONTI]
        p95 = [stats[(n, a)]["p95"] for a in ORIZZONTI]
        ax.fill_between(x, p5, p95, color=COLORI_LOC[n], alpha=0.14)
        ax.fill_between(x, p25, p75, color=COLORI_LOC[n], alpha=0.28)
        ax.plot(x, p50, lw=2.2, color=COLORI_LOC[n], marker="o", markersize=6,
                markeredgecolor="white")
        ax.axhline(0, color=ROSSO, lw=1.2)
        for i, a in enumerate(ORIZZONTI):
            q = stats[(n, a)]["quota_negative"]
            ax.annotate(f"{it(q, 0)}%" if q else "0%", xy=(i, -6.4), ha="center",
                        fontsize=8.5, color=ROSSO if q else VERDE, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels([f"{a}a" for a in ORIZZONTI])
        ax.set_title(n.replace(" (dal 1993)", "\n(solo dal 1993)"), fontsize=11.5)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("rendimento annuo composto")
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    axes[0].set_ylim(-8, 28)
    fig.suptitle("Distribuzione dei rendimenti su tutte le finestre mobili disponibili",
                 fontsize=13.5, fontweight="bold")
    fig.text(0.5, 0.015, "banda chiara dal 5° al 95° percentile, banda scura dal 25° al 75°, "
             "linea la mediana. In rosso sotto: quota di finestre chiuse in perdita.",
             ha="center", fontsize=9, color=GRIGIO, style="italic")
    fig.tight_layout(rect=(0, 0.045, 1, 0.94)); fig.savefig(out); plt.close(fig)


def plot_peggiori(gambe, out):
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    for n, s in gambe.items():
        f = finestre(s, 10, passo=1)
        ax.plot(f.index.to_timestamp(), f.values, lw=1.7, color=COLORI[n], label=n)
        ax.scatter([f.idxmin().to_timestamp()], [f.min()], s=75, color=ROSSO, zorder=5,
                   edgecolor="white", linewidth=0.9)
    ax.axhline(0, color=ROSSO, lw=1.2)
    ax.set_title("Rendimento dei dieci anni successivi, secondo il mese di partenza")
    ax.set_xlabel("mese di acquisto")
    ax.set_ylabel("rendimento annuo composto dei dieci anni dopo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(loc="upper right", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    ax.annotate("i punti rossi sono i minimi di ciascuna serie:\ncadono tutti negli ultimi dieci anni",
                xy=(0.015, 0.05), xycoords="axes fraction", fontsize=9.5,
                color=ROSSO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_predittivita(gambe, rendimenti, out):
    fig, axes = plt.subplots(1, 4, figsize=(13.2, 4.6), sharey=True, sharex=True)
    rette = {}
    for ax, n in zip(axes, COLORI):
        s = gambe[n]; y = rendimenti[n]
        fut = finestre(s, 10, passo=1)
        k = fut.index.intersection(y.index)
        X = y[k].values; Z = fut[k].values
        ax.scatter(X, Z, s=7, color=COLORI[n], alpha=0.35, edgecolor="none")
        lim = np.array([0, 20]); ax.plot(lim, lim, lw=1.0, ls="--", color=GRIGIO)
        b, a0 = np.polyfit(X, Z, 1)
        ax.plot(lim, a0 + b * lim, lw=2.0, color=ROSSO)
        oggi = float(y.iloc[-1]); stima = a0 + b * oggi
        ax.scatter([oggi], [stima], s=90, color=ROSSO, marker="D", zorder=5,
                   edgecolor="white", linewidth=0.9)
        r = float(np.corrcoef(X, Z)[0, 1])
        rette[n] = {"corr": r, "r2": r * r, "pendenza": float(b), "intercetta": float(a0),
                    "rendimento_oggi": oggi, "stima_10a": float(stima), "n": int(len(k))}
        ax.set_title(f"{n}\nR² {it(r*r, 2)}", fontsize=11.5)
        ax.annotate(f"oggi {it(oggi, 1)}%\n→ {it(stima, 1)}%", xy=(oggi, stima),
                    xytext=(8, -22), textcoords="offset points", fontsize=9.5,
                    fontweight="bold", color=ROSSO)
        ax.set_xlim(0, 20); ax.set_ylim(0, 20)
    axes[0].set_ylabel("rendimento ottenuto nei 10 anni dopo")
    for ax in axes:
        ax.set_xlabel("rendimento a scadenza all'acquisto")
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    fig.suptitle("Il rendimento del giorno in cui compri predice quello che otterrai",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(out); plt.close(fig)
    return rette


def plot_reale(nom, reale, out):
    x = np.arange(len(ORIZZONTI)); larg = 0.36
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    ax.bar(x - larg/2, [nom[a]["mediana"] for a in ORIZZONTI], larg,
           label="nominale", color=CHIARO)
    ax.bar(x + larg/2, [reale[a]["mediana"] for a in ORIZZONTI], larg,
           label="al netto dell'inflazione", color=GOLD)
    for i, a in enumerate(ORIZZONTI):
        ax.annotate(it(nom[a]["mediana"], 1) + "%", xy=(i - larg/2, nom[a]["mediana"]),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    fontsize=9.5, color=GRIGIO, fontweight="bold")
        ax.annotate(it(reale[a]["mediana"], 1) + "%", xy=(i + larg/2, reale[a]["mediana"]),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    fontsize=9.5, color=GOLD, fontweight="bold")
        q = reale[a]["quota_negative"]
        ax.annotate(f"perde potere\nd'acquisto nel\n{it(q, 1)}% dei casi",
                    xy=(i, -2.1), ha="center", fontsize=8.5,
                    color=ROSSO if q else VERDE)
    ax.axhline(0, color="#334155", lw=1.0)
    ax.set_xticks(x); ax.set_xticklabels([f"{a} anni" for a in ORIZZONTI])
    ax.set_title("Italia 15+: mediana nominale e mediana reale, dal 1980")
    ax.set_ylabel("rendimento annuo composto")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(-3.6, 12.5)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    gambe, extra, rendimenti = costruisci()
    os.makedirs(OUT, exist_ok=True)
    _stile()

    stats = {}
    for n, s in {**gambe, **extra}.items():
        for a in ORIZZONTI:
            f = finestre(s, a)
            if len(f) >= 8:
                stats[(n, a)] = statistiche(f)

    # inflazione italiana e versione reale della gamba lunga
    cpi = mensile("IT_CPI_oecd_1955.csv")
    k = gambe["Italia 15+"].index.intersection(cpi.index)
    ita_reale = gambe["Italia 15+"][k] / cpi[k]
    ita_reale = ita_reale / ita_reale.iloc[0] * 100
    nom_it = {a: statistiche(finestre(gambe["Italia 15+"][k], a)) for a in ORIZZONTI}
    rea_it = {a: statistiche(finestre(ita_reale, a)) for a in ORIZZONTI}

    plot_curve(gambe, os.path.join(OUT, "01_curve.png"))
    plot_ventagli(stats, os.path.join(OUT, "02_ventagli.png"))
    plot_peggiori(gambe, os.path.join(OUT, "03_peggiori.png"))
    rette = plot_predittivita(gambe, rendimenti, os.path.join(OUT, "04_predittivita.png"))
    plot_reale(nom_it, rea_it, os.path.join(OUT, "05_reale_italia.png"))

    # controlli: se cadono, l'articolo afferma cose false
    for n in gambe:
        for a in (15, 20):
            assert stats[(n, a)]["quota_negative"] == 0, f"{n} a {a} anni ha finestre negative"
    for a in (15, 20):
        assert stats[("Italia 15+ (dal 1993)", a)]["quota_negative"] == 0, \
            "la versione severa dell'Italia ha finestre negative a 15/20 anni"
        assert rea_it[a]["quota_negative"] == 0, "finestre reali negative a 15/20 anni"
    assert all(rette[n]["r2"] > 0.7 for n in rette), "la predittivita' del rendimento iniziale e' caduta"

    infl = (cpi / cpi.shift(12) - 1).dropna() * 100
    infl80 = infl[infl.index >= pd.Period("1980-01", "M")]
    summary = {
        "costruzione": {
            "maturity": {"USA 7-10": 8.5, "USA 20+": 24, "Area euro 7-10": 8.5, "Italia 15+": 20},
            "roll_down": {"USA 7-10": "si, interpolando DGS7 e DGS10", "USA 20+": "no",
                          "Area euro 7-10": "no", "Italia 15+": "no"},
            "validazione": {"IEF": -0.05, "TLT": 0.16, "SXRQ": -0.01},
            "bias_curva_piatta_eur": -0.72, "bias_medie_mensili": 0.06,
        },
        "periodi": {n: {"dal": str(s.index[0]), "al": str(s.index[-1]),
                        "mesi": int(len(s)), "cagr": float(cagr(s) * 100),
                        "crescita": float(s.iloc[-1] / 100)}
                    for n, s in {**gambe, **extra}.items()},
        "finestre": {f"{n}|{a}": v for (n, a), v in stats.items()},
        "predittivita": rette,
        "italia_reale": {"inflazione_media_1980": float(infl80.mean()),
                         "prezzi_moltiplicati": float(cpi[k].iloc[-1] / cpi[k].iloc[0]),
                         "nominale": nom_it, "reale": rea_it},
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    print("GAMBE")
    for n, s in {**gambe, **extra}.items():
        print(f"  {n:24s} {s.index[0]}..{s.index[-1]}  CAGR {it(cagr(s)*100)}%  "
              f"crescita {s.iloc[-1]/100:6.1f}x")
    print("\nFINESTRE (mediana / quota negative)")
    for n in list(gambe) + list(extra):
        riga = " | ".join(f"{a}a {it(stats[(n,a)]['mediana'],2)}% / {it(stats[(n,a)]['quota_negative'],1)}%"
                          for a in ORIZZONTI if (n, a) in stats)
        print(f"  {n:24s} {riga}")
    print(f"\nInflazione Italia 1980-2025: media {it(infl80.mean())}%, "
          f"prezzi x{it(cpi[k].iloc[-1]/cpi[k].iloc[0])}")
    print(f"grafici in {OUT}")


if __name__ == "__main__":
    main()
