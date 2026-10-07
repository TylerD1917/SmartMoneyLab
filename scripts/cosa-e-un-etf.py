# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 7: cos'e' un ETF e come funziona davvero
===========================================================================

Due immagini, una disegnata e una misurata.

1. CREAZIONE E RIMBORSO. Il meccanismo per cui il prezzo di un ETF in borsa
   non si stacca dal valore di cio' che il fondo possiede. Non e' un grafico
   di dati: e' lo schema dell'arbitraggio, nei due versi. Senza questo
   meccanismo un ETF sarebbe un fondo chiuso, e i fondi chiusi scambiano a
   sconto per anni.

2. QUANTO SI SCOSTA DAVVERO UN ETF DAL SUO INDICE. SPY contro l'S&P 500 total
   return, 1993-2025. Stessa valuta, stesso sottostante, entrambi total
   return: e' l'unico confronto pulito che i dati del repo permettono.
   Confrontare un ETF UCITS quotato in dollari con l'indice in euro
   misurerebbe il cambio, non la qualita' della replica.

PERCHE' SPY E NON UN ETF EUROPEO
--------------------------------
Perche' serve l'indice e l'ETF nella STESSA valuta e sulla stessa base
(total return, cioe' con i dividendi dentro da entrambe le parti). Nel repo
questa condizione la soddisfa solo la coppia SPY / S&P 500 TR. L'articolo lo
dichiara: e' un ETF americano, e per un investitore italiano al risultato va
aggiunto il cambio.

OUTPUT in public/charts/cosa-e-un-etf/
--------------------------------------
  01_creazione_rimborso.png   come il prezzo resta agganciato al paniere
  02_scostamento.png          di quanto un ETF manca il suo indice, anno per anno
  summary.json
"""
from __future__ import annotations

import csv
import json
import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "charts" / "cosa-e-un-etf"
SPY = ROOT / "data" / "cache" / "yf_proxy_spy.csv"
IDX = ROOT / "data" / "Sp500" / "Sp500_TotalReturn1988_USD.csv"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#059669"
GRIGIO = "#64748b"
CHIARO = "#f1f5f9"

MIN_SEDUTE = 200        # un anno solare conta solo se e' sostanzialmente completo


# ----------------------------------------------------------------- dati
def serie(path: Path, col_data: str, col_valore: str) -> dict[str, float]:
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        v = (r.get(col_valore) or "").strip()
        if v:
            try:
                out[r[col_data][:10]] = float(v)
            except ValueError:
                pass
    return out


def confronto():
    etf = serie(SPY, "Date", "AdjClose")          # AdjClose = dividendi reinvestiti
    idx = serie(IDX, "Date", "Close")             # indice gia' total return
    comuni = sorted(set(etf) & set(idx))
    a, b = comuni[0], comuni[-1]
    anni = (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days / 365.25
    cagr = lambda s: (s[b] / s[a]) ** (1 / anni) - 1

    per_anno = {}
    for y in sorted({d[:4] for d in comuni}):
        gg = [d for d in comuni if d[:4] == y]
        if len(gg) < MIN_SEDUTE:
            continue
        per_anno[y] = (etf[gg[-1]] / etf[gg[0]]) - (idx[gg[-1]] / idx[gg[0]])

    return {"da": a, "a": b, "anni": anni, "sedute": len(comuni),
            "cagr_etf": cagr(etf), "cagr_indice": cagr(idx),
            "scostamento_annuo": cagr(etf) - cagr(idx),
            "mille_dollari_etf": 1000 * etf[b] / etf[a],
            "mille_dollari_indice": 1000 * idx[b] / idx[a],
            "per_anno": per_anno}


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def _scatola(ax, x, y, w, h, testo, colore, sfondo=None, fs=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.02",
                                linewidth=1.4, edgecolor=colore,
                                facecolor=sfondo or "white", zorder=2))
    ax.text(x + w / 2, y + h / 2, testo, ha="center", va="center",
            fontsize=fs, color="#0f172a", zorder=3, linespacing=1.45)


def _freccia(ax, x1, y1, x2, y2, colore):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
                                 linewidth=1.5, color=colore, zorder=1,
                                 shrinkA=0, shrinkB=0))


def plot_meccanismo(out: Path):
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)

    fig.suptitle("Perché il prezzo di un ETF in borsa non si stacca da quello che il fondo possiede",
                 fontsize=13.5, fontweight="bold", y=0.975)

    righe = [
        (0.655, ROSSO, "In borsa l'ETF costa PIÙ del paniere",
         ["un operatore\ncompra i titoli\nsul mercato",
          "li consegna\nal fondo e riceve\nquote nuove",
          "vende le quote\nin borsa, dove\ncostano di più",
          "l'offerta di quote\naumenta:\nil prezzo scende"]),
        (0.245, VERDE, "In borsa l'ETF costa MENO del paniere",
         ["un operatore\ncompra quote\nin borsa, a sconto",
          "le consegna\nal fondo e riceve\ni titoli",
          "vende i titoli\nsul mercato, dove\nvalgono di più",
          "le quote in giro\ndiminuiscono:\nil prezzo sale"]),
    ]
    w, h, x0, passo = 0.190, 0.21, 0.035, 0.2467
    for y, colore, titolo, passi in righe:
        ax.text(0.5, y + h + 0.062, titolo, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=colore)
        for i, t in enumerate(passi):
            x = x0 + i * passo
            _scatola(ax, x, y, w, h, t, colore, CHIARO if i == 3 else "white")
            if i < 3:
                _freccia(ax, x + w + 0.009, y + h / 2, x + passo - 0.009, y + h / 2, colore)

    ax.text(0.5, 0.055,
            "In entrambi i casi l'operatore guadagna sulla differenza, e proprio per questo la differenza si chiude.\n"
            "È il motivo per cui un ETF non resta scontato per anni, come invece può succedere a un fondo chiuso.",
            ha="center", va="center", fontsize=10, color=GRIGIO, linespacing=1.6)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out)
    plt.close(fig)


def plot_scostamento(d: dict, out: Path):
    anni = sorted(d["per_anno"])
    vals = [d["per_anno"][y] * 10000 for y in anni]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(anni, vals, color=[ROSSO if v < 0 else VERDE for v in vals], width=0.72)
    ax.axhline(0, color=GRIGIO, lw=0.9)
    media = d["scostamento_annuo"] * 10000
    ax.axhline(media, color=NAVY, ls="--", lw=1.4)
    i_freccia = int(len(anni) * 0.80)
    ax.annotate(f"media del periodo:\n{media:,.0f} punti base all'anno".replace(",", "."),
                xy=(i_freccia, media), xytext=(int(len(anni) * 0.52), min(vals) * 0.72),
                ha="center", va="center", color=NAVY, fontweight="bold", fontsize=10.5,
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.3,
                                connectionstyle="arc3,rad=-0.2"))
    ax.set_title("Di quanto un ETF manca il proprio indice, anno per anno")
    ax.set_ylabel("scostamento in punti base")
    ax.set_xticks(anni[::3])
    ax.tick_params(axis="x", labelrotation=0)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}"))
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    d = confronto()
    plot_meccanismo(OUT / "01_creazione_rimborso.png")
    plot_scostamento(d, OUT / "02_scostamento.png")

    decenni = {}
    for y, v in d["per_anno"].items():
        decenni.setdefault(f"{y[:3]}0", []).append(v)
    d["per_decennio"] = {k: sum(v) / len(v) for k, v in sorted(decenni.items())}
    d["fonti"] = {
        "etf": "data/cache/yf_proxy_spy.csv, SPDR S&P 500 ETF (SPY), chiusure aggiustate "
               "per i dividendi reinvestiti",
        "indice": "data/Sp500/Sp500_TotalReturn1988_USD.csv, S&P 500 total return",
        "nota": "stessa valuta e stessa base (total return) su entrambi i lati; "
                "un anno solare entra nel conto solo con almeno "
                f"{MIN_SEDUTE} sedute in comune",
    }
    (OUT / "summary.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 2 immagini + summary.json in {OUT}\n")
    print(f"SPY contro S&P 500 total return, {d['da']} -> {d['a']} "
          f"({d['anni']:.1f} anni, {d['sedute']} sedute)")
    print(f"  ETF     {d['cagr_etf']:+.4%}   1.000 $ -> {d['mille_dollari_etf']:,.0f} $")
    print(f"  indice  {d['cagr_indice']:+.4%}   1.000 $ -> {d['mille_dollari_indice']:,.0f} $")
    print(f"  scostamento: {d['scostamento_annuo'] * 10000:+.1f} punti base all'anno, "
          f"{d['mille_dollari_indice'] - d['mille_dollari_etf']:,.0f} $ di differenza finale")
    print("  media per decennio (punti base): "
          + "  ".join(f"{k} {v * 10000:+.0f}" for k, v in d["per_decennio"].items()))


if __name__ == "__main__":
    main()
