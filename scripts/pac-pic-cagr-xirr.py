# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 11: PAC o PIC, CAGR e XIRR
================================================================================

L'episodio che insegna a leggere i numeri del resto del sito. Tre conti.

1. PIC E PAC SULLO STESSO MERCATO. Ventiquattromila euro versati in una volta
   contro cento euro al mese per vent'anni. Serve a mostrare due cose insieme:
   che i due montanti finali NON sono confrontabili (nel PAC il denaro resta
   investito in media meta' del tempo) e che il PAC ha bisogno di un'altra
   misura di rendimento, perche' le formule del PIC applicate al PAC danno
   numeri sbagliati in entrambe le direzioni.

2. IL CAGR A VENT'ANNI IN FUNZIONE DEL MESE DI PARTENZA. Quattrocentoquaranta
   finestre ventennali sullo stesso indice. E' la dimostrazione che un backtest
   a partenza unica non misura una strategia: misura una data.

3. I PERCENTILI PER ORIZZONTE. La dispersione dei risultati a 1, 3, 5, 10, 20 e
   30 anni. Mostra perche' media e mediana non bastano e perche' l'orizzonte
   cambia la natura della domanda, non solo la risposta.

NOTA SUL PERIMETRO
------------------
L'episodio e' DEFINITORIO: cosa sono PIC e PAC, come si misura il rendimento di
ciascuno. NON risponde a "conviene il PAC o il PIC", che dipende dal periodo e
ha il suo studio dedicato. Il confronto qui serve solo a far vedere perche' le
due cose non si misurano con lo stesso strumento.

BASE DEI DATI
-------------
data/Msci_world/Msci_world_1969_EUR.csv: MSCI World in euro, mensile, da
dicembre 1969 a luglio 2026. Serie total return, dividendi reinvestiti, al
lordo di costi e imposte: i costi sono l'episodio 9, le imposte hanno il loro
pilastro. Qui interessa la MISURA, non il netto.

OUTPUT in public/charts/pac-pic-cagr-xirr/
------------------------------------------
  01_pic_pac.png        due modi di entrare, e tre modi di misurare il PAC
  02_finestre_mobili.png il rendimento a vent'anni dipende dal mese di partenza
  03_percentili.png     quanto si stringe la dispersione con l'orizzonte
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
OUT = ROOT / "public" / "charts" / "pac-pic-cagr-xirr"
SERIE = ROOT / "data" / "Msci_world" / "Msci_world_1969_EUR.csv"

DA, A = "2006-08-01", "2026-07-01"     # vent'anni esatti, 240 mesi
RATA = 100.0
ORIZZONTI = (1, 3, 5, 10, 20, 30)

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#047857"
GRIGIO = "#64748b"


def it(x: float, d: int = 1) -> str:
    """Virgola decimale. Si applica SOLO al numero formattato, mai a una frase."""
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# -------------------------------------------------------------------- dati
def carica() -> pd.Series:
    df = pd.read_csv(SERIE)
    df.columns = ["data", "idx"]
    df["data"] = pd.to_datetime(df["data"], format="%m/%Y")
    return df.set_index("data")["idx"].astype(float).sort_index()


def irr_mensile(rate: list[float], finale: float) -> float:
    """Tasso mensile che porta i versamenti al montante finale. Bisezione: non
    serve scipy e su flussi tutti dello stesso segno la soluzione e' unica."""
    n = len(rate)

    def scarto(r: float) -> float:
        return sum(c * (1 + r) ** (n - 1 - i) for i, c in enumerate(rate)) - finale

    lo, hi = -0.99, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if scarto(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def confronto(s: pd.Series) -> dict:
    w = s.loc[DA:A]
    n = len(w)
    anni = (n - 1) / 12

    quote = (RATA / w).cumsum()           # quote comprate mese per mese
    valore_pac = quote * w
    versato = pd.Series(np.arange(1, n + 1) * RATA, index=w.index)
    tot = float(versato.iloc[-1])
    fin_pac = float(valore_pac.iloc[-1])

    r_m = irr_mensile([RATA] * n, fin_pac)
    xirr = (1 + r_m) ** 12 - 1

    fin_pic = tot * float(w.iloc[-1] / w.iloc[0])
    cagr_pic = float(w.iloc[-1] / w.iloc[0]) ** (1 / anni) - 1
    valore_pic = tot * w / float(w.iloc[0])

    return {
        "da": w.index[0].strftime("%Y-%m"), "a": w.index[-1].strftime("%Y-%m"),
        "mesi": n, "anni": anni, "rata": RATA, "versato": tot,
        "pac": {"finale": fin_pac, "sul_versato": fin_pac / tot - 1, "xirr": xirr,
                "cagr_applicato_male": (fin_pac / tot) ** (1 / anni) - 1,
                "diviso_per_gli_anni": (fin_pac / tot - 1) / anni},
        "pic": {"finale": fin_pic, "totale": fin_pic / tot - 1, "cagr": cagr_pic},
        "_serie": {"versato": versato, "valore_pac": valore_pac, "valore_pic": valore_pic},
    }


def finestre(s: pd.Series, anni: int) -> pd.Series:
    m = anni * 12
    return ((s.shift(-m) / s) ** (1 / anni) - 1).dropna() * 100


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_pic_pac(c: dict, out: Path):
    ser = c["_serie"]
    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(10.2, 8.4), gridspec_kw={"height_ratios": [2.3, 1]})

    ax.plot(ser["valore_pic"].index, ser["valore_pic"].values, lw=2.2, color=NAVY,
            label=f"PIC: {it(c['versato'], 0)} € una volta sola")
    ax.plot(ser["valore_pac"].index, ser["valore_pac"].values, lw=2.2, color=GOLD,
            label=f"PAC: {it(RATA, 0)} € al mese")
    ax.fill_between(ser["versato"].index, ser["versato"].values, 0,
                    color=GRIGIO, alpha=0.18, label="versato dal PAC, mese per mese")

    for nome, serie, colore in (("pic", ser["valore_pic"], NAVY),
                                ("pac", ser["valore_pac"], GOLD)):
        fine = serie.iloc[-1]
        ax.annotate(f"{it(fine, 0)} €", xy=(serie.index[-1], fine), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=10.5,
                    fontweight="bold", color=colore)

    ax.set_title("Stesso mercato, stessi 24.000 euro, due modi di entrare")
    ax.set_ylabel("valore del portafoglio")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: it(v / 1000, 0) + "k €"))
    ax.set_xlim(ser["versato"].index[0], ser["versato"].index[-1])
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.grid(axis="x", visible=False)

    # i tre modi di misurare il rendimento del PAC
    p = c["pac"]
    # etichette corte: una riga lunga sull'asse y schiaccia il pannello di sopra
    voci = [("diviso per gli anni", p["diviso_per_gli_anni"] * 100, ROSSO, "sbagliato"),
            ("formula del CAGR\nsul versato", p["cagr_applicato_male"] * 100, ROSSO,
             "sbagliato"),
            ("XIRR", p["xirr"] * 100, VERDE, "corretto")]
    nomi = [v[0] for v in voci]
    vals = [v[1] for v in voci]
    ax2.barh(nomi, vals, color=[v[2] for v in voci], alpha=0.85, height=0.58)
    for i, v in enumerate(vals):
        ax2.annotate(it(v, 2) + "%", xy=(v, i), xytext=(7, 0),
                     textcoords="offset points", va="center",
                     fontsize=11, fontweight="bold", color=voci[i][2])
        ax2.annotate(voci[i][3], xy=(v, i), xytext=(64, 0),
                     textcoords="offset points", va="center", fontsize=9.5,
                     color=voci[i][2], style="italic")
    ax2.set_title("Lo stesso PAC, tre numeri diversi spacciati per \"rendimento annuo\"",
                  fontsize=12)
    ax2.set_xlim(0, max(vals) * 1.35)
    ax2.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax2.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax2.tick_params(axis="y", labelsize=10)
    ax2.grid(axis="y", visible=False)

    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_finestre(c20: pd.Series, out: Path):
    q = np.percentile(c20.values, [5, 50, 95])
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    ax.plot(c20.index, c20.values, lw=1.8, color=NAVY)
    ax.fill_between(c20.index, c20.values, 0, color=NAVY, alpha=0.10)

    ax.axhline(q[1], color=GOLD, lw=1.8, ls="--")
    ax.annotate(f"mediana {it(q[1], 1)}%",
                xy=(c20.index[len(c20) // 2], q[1]), xytext=(0, 9),
                textcoords="offset points", ha="center", fontsize=10,
                fontweight="bold", color=GOLD)

    # l'etichetta del minimo va a sinistra: il punto e' vicino al bordo destro
    for etichetta, data, valore, dx, dy, ha in (
            ("peggior partenza", c20.idxmin(), c20.min(), -12, -20, "right"),
            ("miglior partenza", c20.idxmax(), c20.max(), 0, 15, "center")):
        ax.scatter([data], [valore], s=90, color=ROSSO, zorder=4,
                   edgecolor="white", linewidth=0.9)
        ax.annotate(f"{etichetta}: {data.strftime('%m/%Y')}, {it(valore, 1)}%",
                    xy=(data, valore), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, fontsize=10, fontweight="bold", color=ROSSO)

    ax.set_title("Lo stesso indice, lo stesso orizzonte: cambia solo il mese in cui entri")
    ax.set_ylabel("rendimento annuo composto dei vent'anni successivi")
    ax.set_xlabel("mese di partenza")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.set_ylim(0, 20)
    ax.set_xlim(c20.index[0], c20.index[-1])
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_percentili(perc: dict, out: Path):
    x = list(range(len(ORIZZONTI)))
    p05 = [perc[a]["p5"] for a in ORIZZONTI]
    p25 = [perc[a]["p25"] for a in ORIZZONTI]
    p50 = [perc[a]["mediana"] for a in ORIZZONTI]
    p75 = [perc[a]["p75"] for a in ORIZZONTI]
    p95 = [perc[a]["p95"] for a in ORIZZONTI]
    media = [perc[a]["media"] for a in ORIZZONTI]

    fig, ax = plt.subplots(figsize=(10.2, 6.4))
    ax.fill_between(x, p05, p95, color=NAVY, alpha=0.14,
                    label="dal 5° al 95° percentile")
    ax.fill_between(x, p25, p75, color=NAVY, alpha=0.26,
                    label="dal 25° al 75° percentile")
    ax.plot(x, p50, lw=2.4, color=NAVY, marker="o", markersize=7,
            markeredgecolor="white", label="mediana")
    ax.plot(x, media, lw=1.6, ls="--", color=GOLD, marker="s", markersize=5,
            label="media")
    ax.axhline(0, color=ROSSO, lw=1.2)

    for i, a in enumerate(ORIZZONTI):
        ax.annotate(it(p05[i], 1) + "%", xy=(i, p05[i]), xytext=(0, -16),
                    textcoords="offset points", ha="center", fontsize=9, color=GRIGIO)
        ax.annotate(it(p95[i], 1) + "%", xy=(i, p95[i]), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=9, color=GRIGIO)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{a} anno" if a == 1 else f"{a} anni" for a in ORIZZONTI],
                       fontsize=11)
    ax.set_title("Quanto si stringe il ventaglio dei risultati con l'orizzonte")
    ax.set_ylabel("rendimento annuo composto")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(-32, 48)
    ax.legend(loc="upper right", frameon=False, fontsize=10)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    s = carica()
    c = confronto(s)

    perc = {}
    for a in ORIZZONTI:
        f = finestre(s, a)
        q = np.percentile(f.values, [5, 25, 50, 75, 95])
        perc[a] = {"n": int(len(f)), "media": float(f.mean()), "p5": float(q[0]),
                   "p25": float(q[1]), "mediana": float(q[2]), "p75": float(q[3]),
                   "p95": float(q[4]), "min": float(f.min()), "max": float(f.max()),
                   "quota_negative": float((f < 0).mean())}

    c20 = finestre(s, 20)

    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    plot_pic_pac(c, OUT / "01_pic_pac.png")
    plot_finestre(c20, OUT / "02_finestre_mobili.png")
    plot_percentili(perc, OUT / "03_percentili.png")

    # controlli: l'articolo afferma queste tre cose, se cadono va riscritto
    assert c["pac"]["cagr_applicato_male"] < c["pac"]["xirr"] < c["pac"]["diviso_per_gli_anni"], \
        "l'ordine dei tre modi di misurare il PAC e' cambiato"
    assert perc[20]["quota_negative"] == 0.0, "esistono finestre ventennali negative"
    assert perc[1]["p95"] - perc[1]["p5"] > perc[20]["p95"] - perc[20]["p5"], \
        "la dispersione non si stringe con l'orizzonte"

    peggio, meglio = c20.idxmin(), c20.idxmax()
    summary = {
        "serie": {"file": str(SERIE.relative_to(ROOT)), "dal": s.index[0].strftime("%Y-%m"),
                  "al": s.index[-1].strftime("%Y-%m"), "mesi": int(len(s))},
        "confronto": {k: v for k, v in c.items() if k != "_serie"},
        "percentili": perc,
        "ventennio": {
            "peggiore": {"da": peggio.strftime("%Y-%m"), "cagr": float(c20.min()),
                         "montante_10k": round(10000 * (1 + c20.min() / 100) ** 20)},
            "migliore": {"da": meglio.strftime("%Y-%m"), "cagr": float(c20.max()),
                         "montante_10k": round(10000 * (1 + c20.max() / 100) ** 20)},
            "finestre": int(len(c20))},
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    p = c["pac"]
    print(f"PAC {it(RATA,0)} €/mese dal {c['da']} al {c['a']}: versati "
          f"{it(c['versato'],0)} €, finale {it(p['finale'],0)} €")
    print(f"  diviso per gli anni {it(p['diviso_per_gli_anni']*100,2)}%  "
          f"CAGR applicato male {it(p['cagr_applicato_male']*100,2)}%  "
          f"XIRR {it(p['xirr']*100,2)}%")
    print(f"PIC stessa cifra: finale {it(c['pic']['finale'],0)} €, "
          f"CAGR {it(c['pic']['cagr']*100,2)}%")
    for a in ORIZZONTI:
        q = perc[a]
        print(f"  {a:2d} anni n={q['n']:4d} media {it(q['media'],2):>6}  "
              f"mediana {it(q['mediana'],2):>6}  p5 {it(q['p5'],2):>7}  "
              f"p95 {it(q['p95'],2):>6}  negative {it(q['quota_negative']*100,1)}%")
    print(f"ventennio peggiore dal {peggio.strftime('%m/%Y')} "
          f"({it(c20.min(),2)}%), migliore dal {meglio.strftime('%m/%Y')} "
          f"({it(c20.max(),2)}%)")
    print(f"grafici in {OUT}")


if __name__ == "__main__":
    main()
