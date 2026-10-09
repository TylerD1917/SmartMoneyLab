# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 10: rischio, volatilita' e diversificazione
================================================================================

La tesi dell'episodio e' una sola e i tre grafici la dimostrano: le misure del
rischio ORDINANO GLI ASSET IN MODO DIVERSO, quindi dire "quanto rischia" senza
dire "misurato come" non significa niente.

1. VOLATILITA' CONTRO MASSIMO DRAWDOWN. Scatter su ventidue asset class. Le due
   misure vanno insieme, ma non coincidono, e gli scostamenti sono la lezione:
   i Treasury americani a lungo termine hanno la seconda volatilita' piu' bassa
   del campione e un drawdown vicino a quello dell'azionario americano.

2. LE CURVE SOTT'ACQUA. Tre asset con drawdown massimo simile e tre esperienze
   diverse: S&P 500 (profondo e recuperato in fretta), Giappone (profondo e
   dieci anni per tornare in pari), Treasury 20+ (meno profondo e ancora
   sott'acqua oggi). E' la misura che corrisponde a cosa si sente a tenerli.

3. LE TRE CLASSIFICHE. Gli stessi dieci asset ordinati per volatilita', per
   drawdown e per mesi sott'acqua. Le linee si incrociano: e' il riassunto
   visivo dell'intero episodio.

FINESTRA COMUNE
---------------
Agosto 2002 - agosto 2026, ventiquattro anni, imposta a tutti. Confrontare un
drawdown misurato su trent'anni con uno misurato su dieci e' scorretto: chi ha
piu' storia ha piu' probabilita' di avere incontrato una crisi. La finestra
parte dal luglio 2002 perche' e' l'inizio della serie dei Treasury 20+, e
include la crisi del 2008, il COVID e il crollo obbligazionario del 2022.
Restano fuori gli asset nati dopo (Bitcoin, REIT, Cina, Europa, India, difesa,
emergenti, gli ETF MSCI World e ACWI): si dichiara, non si aggira.

Il grafico 2 usa invece la storia piena di ciascuna delle tre serie, perche' una
curva sott'acqua racconta un percorso e non pretende di essere una classifica.

BASE DEI DATI
-------------
data/cache/correlation_universe_monthly.csv: chiusure mensili aggiustate per i
dividendi, in dollari, il panel costruito per l'articolo sulle correlazioni.
Total return su entrambi i lati di ogni confronto.

OUTPUT in public/charts/rischio-volatilita-diversificazione/
------------------------------------------------------------
  01_volatilita_drawdown.png   le due misure non dicono la stessa cosa
  02_sottacqua.png             tre drawdown simili, tre attese diverse
  03_tre_classifiche.png       l'ordine cambia con la misura
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
OUT = ROOT / "public" / "charts" / "rischio-volatilita-diversificazione"
UNIVERSO = ROOT / "data" / "cache" / "correlation_universe_monthly.csv"

INIZIO = "2002-08-01"          # inizio della finestra comune
SOGLIA_INGRESSO = "2002-09-30"  # chi parte dopo questa data resta fuori

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#047857"
GRIGIO = "#64748b"

IT = {"USA (S&P 500)": "USA (S&P 500)", "Treasury USA 20+": "Treasury USA 20+",
      "Consumer Staples": "Beni di consumo", "Healthcare": "Sanità",
      "Financials": "Banche e finanza", "Energy": "Energia",
      "Semiconduttori": "Semiconduttori", "Nasdaq 100": "Nasdaq 100",
      "Value (S&P500)": "Value (USA)", "Small Cap (Russell 2000)": "Small cap (USA)",
      "Petrolio (WTI)": "Petrolio", "Oro": "Oro", "Argento": "Argento",
      "Rame": "Rame", "Giappone": "Giappone", "Germania": "Germania",
      "Regno Unito": "Regno Unito", "Australia": "Australia", "Canada": "Canada",
      "Corea del Sud": "Corea del Sud", "Taiwan": "Taiwan",
      "America Latina": "America Latina"}

# i dieci del grafico delle tre classifiche: scelti per coprire tutto l'arco
# da "tutte le misure concordano" a "le misure si contraddicono"
DIECI = ["Consumer Staples", "Treasury USA 20+", "USA (S&P 500)", "Giappone",
         "Nasdaq 100", "Oro", "Financials", "Corea del Sud", "America Latina",
         "Petrolio (WTI)"]
EVIDENZA = {"Treasury USA 20+": ROSSO, "Nasdaq 100": NAVY,
            "Giappone": GOLD, "Consumer Staples": VERDE}


def it(x: float, d: int = 1) -> str:
    """Numero con la virgola decimale. Si applica SOLO al numero, mai a una frase."""
    return f"{x:.{d}f}".replace(".", ",")


# ------------------------------------------------------------------ misure
def carica() -> pd.DataFrame:
    df = pd.read_csv(UNIVERSO, parse_dates=["date"]).set_index("date")
    return df.sort_index()


def sottacqua(s: pd.Series) -> pd.Series:
    """Distanza dal massimo precedente, mese per mese. Zero quando e' in cima."""
    return s / s.cummax() - 1.0


def streak_piu_lungo(dd: pd.Series) -> tuple[int, bool]:
    """Mesi consecutivi sotto il massimo precedente, e se la serie piu' lunga
    e' quella ancora aperta all'ultimo mese disponibile."""
    sotto = (dd < -1e-9)
    best = cur = 0
    fine = None
    for data, v in sotto.items():
        cur = cur + 1 if v else 0
        if cur > best:
            best, fine = cur, data
    in_corso = bool(sotto.iloc[-1]) and fine == sotto.index[-1]
    return best, in_corso


def misure(s: pd.Series) -> dict:
    s = s.dropna()
    r = s.pct_change().dropna()
    dd = sottacqua(s)
    fondo = dd.idxmin()
    picco = s.loc[:fondo].idxmax()
    dopo = s.loc[fondo:]
    tornato = dopo[dopo >= s.loc[picco]]
    mesi, in_corso = streak_piu_lungo(dd)
    return {
        "vol": float(r.std(ddof=1) * np.sqrt(12)),
        "maxdd": float(dd.min()),
        "mesi_sottacqua": int(mesi),
        "sottacqua_ora": float(dd.iloc[-1]),
        "streak_in_corso": in_corso,
        "picco": picco.strftime("%Y-%m"),
        "fondo": fondo.strftime("%Y-%m"),
        "recuperato": (tornato.index[0].strftime("%Y-%m") if len(tornato) else None),
        "cagr": float((s.iloc[-1] / s.iloc[0]) ** (12 / (len(s) - 1)) - 1),
        "dal": s.index[0].strftime("%Y-%m"), "al": s.index[-1].strftime("%Y-%m"),
        "mesi_totali": int(len(s)),
    }


def spearman(a: pd.Series, b: pd.Series) -> float:
    """Correlazione di rango: Pearson sui ranghi, senza dipendere da scipy."""
    return float(a.rank().corr(b.rank()))


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


# posizione dell'etichetta rispetto al punto: (dx, dy, allineamento).
# Fatta a mano perche' nello scatter i punti si addensano e un posizionamento
# automatico a destra produceva quattro sovrapposizioni illeggibili.
ETICHETTE = {
    "Consumer Staples": (12, 0, "left"), "Healthcare": (-11, 0, "right"),
    "Treasury USA 20+": (-13, 0, "right"), "USA (S&P 500)": (-11, -7, "right"),
    "Value (S&P500)": (-11, 0, "right"), "Giappone": (0, 15, "center"),
    "Oro": (11, 0, "left"), "Regno Unito": (-11, 0, "right"),
    "Nasdaq 100": (13, 0, "left"), "Small Cap (Russell 2000)": (11, 0, "left"),
    "Canada": (11, 0, "left"), "Financials": (-11, 0, "right"),
    "Australia": (-11, 0, "right"), "Taiwan": (11, 3, "left"),
    "Germania": (11, -3, "left"), "Energy": (11, 6, "left"),
    "Rame": (-11, -4, "right"), "America Latina": (8, 16, "left"),
    "Semiconduttori": (11, 0, "left"), "Corea del Sud": (-11, 0, "right"),
    "Argento": (11, 0, "left"), "Petrolio (WTI)": (-11, 0, "right"),
}


def plot_scatter(t, out: Path):
    fig, ax = plt.subplots(figsize=(10.2, 7.0))
    x = t["vol"] * 100
    y = t["maxdd"] * 100

    # retta ai minimi quadrati: serve a far vedere che le due misure vanno
    # insieme, e quindi a far risaltare chi sta lontano dalla retta
    m, q = np.polyfit(x.values, y.values, 1)
    xs = np.array([x.min() - 1.5, x.max() + 1.5])
    ax.plot(xs, m * xs + q, lw=1.2, ls="--", color="#94a3b8", zorder=1)
    xa = 35.0                      # tratto libero della retta, lontano dai punti
    ax.annotate("andamento medio", xy=(xa, m * xa + q), xytext=(0, 12),
                textcoords="offset points", ha="center", fontsize=9,
                color="#94a3b8", style="italic")

    for nome in t.index:
        colore = EVIDENZA.get(nome, GRIGIO)
        grande = nome in EVIDENZA
        ax.scatter(x[nome], y[nome], s=136 if grande else 58, color=colore,
                   alpha=1.0 if grande else 0.5, zorder=4 if grande else 3,
                   edgecolor="white", linewidth=0.8)
        dx, dy, ha = ETICHETTE.get(nome, (11, 0, "left"))
        ax.annotate(IT.get(nome, nome), xy=(x[nome], y[nome]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va="center",
                    fontsize=9.8 if grande else 8.6,
                    fontweight="bold" if grande else "normal",
                    color=colore, zorder=5)

    ax.set_title("Due misure dello stesso rischio, e non dicono la stessa cosa")
    ax.set_xlabel("volatilità annualizzata")
    ax.set_ylabel("perdita massima dal picco precedente")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_xlim(8.5, 43)
    ax.set_ylim(-92, -20)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def periodo_piu_lungo(dd: pd.Series):
    """(inizio, fine, mesi, ancora_in_corso) del tratto sott'acqua piu' lungo."""
    sotto = (dd < -1e-9)
    best = cur = 0
    inizio_cur = inizio_best = fine_best = None
    for data, v in sotto.items():
        if v:
            if cur == 0:
                inizio_cur = data
            cur += 1
            if cur > best:
                best, inizio_best, fine_best = cur, inizio_cur, data
        else:
            cur = 0
    in_corso = bool(sotto.iloc[-1]) and fine_best == sotto.index[-1]
    return inizio_best, fine_best, best, in_corso


def plot_sottacqua(serie: dict, out: Path):
    """Un pannello per asset: tre curve sovrapposte erano illeggibili, e qui
    la cosa da vedere non e' il confronto istante per istante ma la LARGHEZZA
    del tratto sotto lo zero."""
    colori = {"USA (S&P 500)": NAVY, "Giappone": GOLD, "Treasury USA 20+": ROSSO}
    nomi = list(serie)
    fig, axes = plt.subplots(len(nomi), 1, figsize=(10.4, 7.8), sharex=True)

    x_min = min(s.dropna().index[0] for s in serie.values())
    x_max = max(s.dropna().index[-1] for s in serie.values())

    for ax, nome in zip(axes, nomi):
        s = serie[nome].dropna()
        dd = sottacqua(s) * 100
        colore = colori[nome]
        ax.plot(dd.index, dd.values, lw=1.5, color=colore)
        ax.fill_between(dd.index, dd.values, 0, color=colore, alpha=0.16)

        da, a, mesi, in_corso = periodo_piu_lungo(sottacqua(s))
        ax.axvspan(da, a, color=colore, alpha=0.10, zorder=0)
        anni, resto = mesi // 12, mesi % 12
        coda = f"{anni} anno" if anni == 1 else f"{anni} anni"
        if resto:
            coda += f" e {resto} mese" if resto == 1 else f" e {resto} mesi"
        testo = (f"{mesi} mesi sotto il massimo, {coda}"
                 + (", e non è ancora finito" if in_corso
                    else f": da {da.strftime('%m/%Y')} a {a.strftime('%m/%Y')}"))
        ax.annotate(testo, xy=(0.015, 0.045), xycoords="axes fraction",
                    fontsize=9.5, color=colore, fontweight="bold")

        ax.axhline(0, color="#334155", lw=0.9)
        ax.set_ylabel(IT.get(nome, nome), fontsize=10.5, fontweight="bold",
                      color=colore)
        ax.set_ylim(-69, 7)
        ax.set_yticks([0, -20, -40, -60])
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
        ax.set_xlim(x_min, x_max)
        ax.grid(axis="x", visible=False)

    axes[0].set_title("Quanto tempo si passa sotto il proprio massimo")
    fig.supylabel("distanza dal massimo precedente", fontsize=10.5, x=0.012)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_tre_classifiche(t: pd.DataFrame, out: Path):
    """Slope chart: la posizione dei dieci asset secondo le tre misure."""
    sel = t.loc[DIECI]
    colonne = [("volatilità", sel["vol"]),
               ("perdita massima", -sel["maxdd"]),
               ("mesi sott'acqua", sel["mesi_sottacqua"].astype(float))]
    # rango 1 = il piu' rischioso secondo quella misura
    classifiche = [v.rank(ascending=False, method="first") for _, v in colonne]
    n = len(sel)

    fig, ax = plt.subplots(figsize=(10.2, 6.6))
    for nome in sel.index:
        y = [float(c[nome]) for c in classifiche]
        colore = EVIDENZA.get(nome, GRIGIO)
        evidenziato = nome in EVIDENZA
        ax.plot([0, 1, 2], y, lw=2.4 if evidenziato else 1.2, color=colore,
                alpha=1.0 if evidenziato else 0.45, zorder=3 if evidenziato else 2,
                marker="o", markersize=7 if evidenziato else 5,
                markeredgecolor="white", markeredgewidth=0.8)
        ax.annotate(IT.get(nome, nome), xy=(0, y[0]), xytext=(-12, 0),
                    textcoords="offset points", ha="right", va="center",
                    fontsize=9.5 if evidenziato else 8.8,
                    fontweight="bold" if evidenziato else "normal", color=colore)
        ax.annotate(IT.get(nome, nome), xy=(2, y[2]), xytext=(12, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=9.5 if evidenziato else 8.8,
                    fontweight="bold" if evidenziato else "normal", color=colore)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([c[0] for c in colonne], fontsize=11, fontweight="bold")
    ax.set_xlim(-0.72, 2.72)
    ax.set_ylim(n + 0.6, 0.4)
    ax.set_yticks(range(1, n + 1))
    ax.set_ylabel("posizione, dal più rischioso al meno")
    ax.set_title("Dieci asset, tre misure del rischio, tre classifiche diverse")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    df = carica()
    fin = df.loc[INIZIO:]
    ammessi = [c for c in fin.columns
               if not fin[c].dropna().empty
               and fin[c].dropna().index[0] <= pd.Timestamp(SOGLIA_INGRESSO)]
    esclusi = [c for c in fin.columns if c not in ammessi]

    t = pd.DataFrame({c: misure(fin[c]) for c in ammessi}).T
    for col in ("vol", "maxdd", "sottacqua_ora", "cagr"):
        t[col] = t[col].astype(float)
    t["mesi_sottacqua"] = t["mesi_sottacqua"].astype(int)
    t = t.sort_values("vol", ascending=False)

    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    plot_scatter(t, OUT / "01_volatilita_drawdown.png")
    plot_sottacqua({n: df[n] for n in ("USA (S&P 500)", "Giappone", "Treasury USA 20+")},
                   OUT / "02_sottacqua.png")
    plot_tre_classifiche(t, OUT / "03_tre_classifiche.png")

    rank = {
        "vol_vs_drawdown": spearman(t["vol"], -t["maxdd"]),
        "vol_vs_mesi": spearman(t["vol"], t["mesi_sottacqua"].astype(float)),
        "drawdown_vs_mesi": spearman(-t["maxdd"], t["mesi_sottacqua"].astype(float)),
    }

    # controllo: la tesi dell'articolo regge solo se le classifiche differiscono
    assert rank["vol_vs_drawdown"] < 0.95, "le due misure coincidono: tesi da rivedere"
    assert rank["vol_vs_mesi"] < 0.8, "volatilita' e mesi sott'acqua coincidono"

    piena = {n: misure(df[n]) for n in ("USA (S&P 500)", "Giappone",
                                        "Treasury USA 20+", "America Latina",
                                        "Petrolio (WTI)", "Nasdaq 100")}

    summary = {
        "finestra": {"dal": t["dal"].iloc[0], "al": t["al"].iloc[0],
                     "mesi": int(t["mesi_totali"].iloc[0]),
                     "asset": len(ammessi), "esclusi": esclusi},
        "correlazione_di_rango": rank,
        "finestra_comune": {n: {k: v for k, v in t.loc[n].items()} for n in t.index},
        "storia_piena": piena,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"finestra comune {summary['finestra']['dal']} -> {summary['finestra']['al']}, "
          f"{len(ammessi)} asset, esclusi {len(esclusi)}")
    print("correlazione di rango: vol~drawdown %s, vol~mesi %s, drawdown~mesi %s"
          % (it(rank['vol_vs_drawdown'], 2), it(rank['vol_vs_mesi'], 2),
             it(rank['drawdown_vs_mesi'], 2)))
    for n in t.index:
        r = t.loc[n]
        print(f"  {n:26s} vol {it(r['vol']*100)}%  dd {it(r['maxdd']*100)}%  "
              f"{r['mesi_sottacqua']:3d} mesi  oggi {it(r['sottacqua_ora']*100)}%")
    print(f"grafici in {OUT}")


if __name__ == "__main__":
    main()
