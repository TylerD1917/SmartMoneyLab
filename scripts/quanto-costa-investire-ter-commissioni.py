# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 9: quanto costa investire
=============================================================

Tre immagini che rispondono a tre domande diverse sui costi.

1. QUANTO PESA IL TER su un orizzonte lungo, applicato a una serie di mercato
   vera e non a un rendimento inventato. Tre livelli, tutti documentati: il
   TER piu' basso oggi disponibile su un indice grande, quello tipico di un
   ETF globale, e il costo corrente medio dei fondi azionari non-ETF in
   Europa secondo ESMA.

2. QUANTO PESA LA COMMISSIONE DI NEGOZIAZIONE su chi fa un piano di accumulo.
   E' aritmetica, non backtest: una commissione fissa su un versamento piccolo
   e' una percentuale grande. E' la voce di cui si parla meno ed e' quella che
   un principiante puo' davvero ridurre.

3. DOVE FINISCE IL RENDIMENTO, dal lordo dell'indice al netto in tasca, su
   vent'anni. I valori NON sono ricalcolati qui: vengono dallo studio
   gia' pubblicato sui rendimenti netti, per non avere due numeri diversi
   sullo stesso sito.

PERCHE' NON RICALCOLO LA CASCATA
--------------------------------
Lo studio "Quanto rende davvero l'azionario al netto di tasse e costi" misura
la stessa cosa su 440 finestre mobili ventennali, con il cambio ricostruito e
l'inflazione italiana. Rifare qui un conto piu' povero su un solo percorso
produrrebbe un numero leggermente diverso, e due numeri diversi sulla stessa
domanda sono peggio di nessun numero. Questo script li rilegge e li disegna.

OUTPUT in public/charts/quanto-costa-investire-ter-commissioni/
----------------------------------------------------------------
  01_ter.png          lo stesso mercato con tre livelli di costo annuo
  02_commissioni.png  quanto pesa davvero una commissione fissa
  03_cascata.png      dal rendimento lordo a quello in tasca
  summary.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "charts" / "quanto-costa-investire-ter-commissioni"
WORLD = ROOT / "data" / "Indici_Eurozona" / ".." / "Msci_world" / "Msci_world_1969_EUR.csv"
STUDIO = ROOT / "public" / "charts" / "rendimenti-netti-indici-azionari" / "summary.json"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
VERDE = "#059669"
GRIGIO = "#64748b"

CAPITALE = 10_000
ANNI = 30

# Tutti e tre documentati, nessuno inventato (vedi "fonti" nel summary)
LIVELLI = [
    (0.0003, "0,03% all'anno", "il più economico oggi su un indice grande", VERDE),
    (0.0021, "0,21% all'anno", "ETF azionario passivo, media europea", NAVY),
    (0.0128, "1,28% all'anno", "fondo azionario attivo non-ETF, media europea", ROSSO),
]

# Forme di commissione tipiche, senza nomi: i listini dei broker cambiano,
# le forme no. Il lettore ci mette i propri numeri.
# Nota: "0,19% con minimo 3 €", la forma piu' diffusa in Italia, sotto una certa
# soglia COINCIDE con la commissione fissa (3 / 0,0019 = 1.578 €), quindi
# disegnarla darebbe due curve sovrapposte e una invisibile. Meglio mostrare le
# tre forme pure, e spiegare a testo che il listino tipico e' un ibrido.
PERCENTUALE = 0.0019
MINIMO = 3.0
STRUTTURE = [
    ("commissione fissa di 3 €", lambda x: MINIMO, ROSSO),
    ("0,19% proporzionale, senza minimo", lambda x: PERCENTUALE * x, GOLD),
    ("nessuna commissione", lambda x: 0.0, VERDE),
]
IMPORTI = list(range(50, 1051, 10))
SOGLIA = 0.005          # mezzo punto percentuale: la soglia di guardia


# ----------------------------------------------------------------- dati
def world_mensile() -> dict[str, float]:
    out = {}
    for r in csv.reader(open(WORLD, encoding="utf-8-sig")):
        if not r or r[0].strip() in ("Data", ""):
            continue
        m, a = r[0].split("/")
        out[f"{a}-{m}"] = float(r[1])
    return out


def mesi_fra(a: str, b: str) -> int:
    return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def _euro(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}".replace(",", ".")))


def plot_ter(serie: dict, da: str, a: str, out: Path):
    date = [d for d in sorted(serie) if da <= d <= a]
    base = serie[date[0]]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    finali = {}
    # su scala logaritmica 117.159 e 110.993 distano pochi pixel: le etichette
    # vanno scostate a mano, altrimenti si sovrappongono
    scosta = {"0,03% all'anno": 9, "0,21% all'anno": -9, "1,28% all'anno": 0}
    for ter, etichetta, nota, colore in LIVELLI:
        ys, x = [], []
        for d in date:
            n = mesi_fra(da, d)
            lordo = CAPITALE * serie[d] / base
            ys.append(lordo * (1 - ter) ** (n / 12))
            x.append(int(d[:4]) + (int(d[5:7]) - 1) / 12)
        ax.plot(x, ys, color=colore, lw=2.2, label=f"{etichetta}, {nota}")
        finali[etichetta] = ys[-1]
        ax.annotate(f"{ys[-1]:,.0f} €".replace(",", "."), xy=(x[-1], ys[-1]),
                    xytext=(8, scosta.get(etichetta, 0)), textcoords="offset points",
                    va="center", fontsize=10.5, fontweight="bold", color=colore)
    _cap = f"{CAPITALE:,.0f}".replace(",", ".")
    ax.set_title(f"{_cap} euro sullo stesso mercato, tre livelli di costo")
    ax.set_ylabel("valore")
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    _euro(ax)
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.margins(x=0.1)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return finali


def plot_commissioni(out: Path):
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for nome, f, colore in STRUTTURE:
        ys = [f(x) / x * 100 for x in IMPORTI]
        ax.plot(IMPORTI, ys, color=colore, lw=2.3, label=nome)
    ax.axhline(SOGLIA * 100, color=GRIGIO, ls="--", lw=1.3)
    ax.annotate("mezzo punto percentuale", xy=(IMPORTI[-1], SOGLIA * 100),
                xytext=(-8, 8), textcoords="offset points", ha="right",
                fontsize=10, color=GRIGIO)
    # dove la commissione fissa scende sotto la soglia
    soglia_fissa = MINIMO / SOGLIA
    ax.axvline(soglia_fissa, color=ROSSO, ls=":", lw=1.3)
    _soglia_txt = f"{soglia_fissa:,.0f}".replace(",", ".")
    ax.annotate(f"con 3 € fissi servono {_soglia_txt} €\nper restare sotto lo 0,5%",
                xy=(soglia_fissa, 3.4), xytext=(14, 0), textcoords="offset points",
                fontsize=10, color=ROSSO, fontweight="bold", va="center")
    _ibrido = f"{MINIMO / PERCENTUALE:,.0f}".replace(",", ".")
    ax.annotate("un listino «0,19% con minimo 3 €» si comporta\n"
                f"come la curva rossa fino a {_ibrido} €, poi come la gialla",
                xy=(IMPORTI[-1] * 0.50, 2.1), fontsize=9.5, color=GRIGIO, va="center")
    ax.set_title("Quanto pesa la commissione, a seconda di quanto versi")
    ax.set_xlabel("importo di ogni acquisto")
    ax.set_ylabel("costo dell'operazione")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:.1f}%".replace(".", ",")))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f} €".replace(",", ".")))
    ax.set_ylim(0, 6.3)
    ax.set_xlim(IMPORTI[0], IMPORTI[-1])
    ax.legend(frameon=False, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_cascata(lordo: float, voci: list[tuple[str, float]], netto: float, out: Path):
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    etichette = ["indice\nlordo"] + [v[0] for v in voci] + ["in tasca"]
    sinistra = lordo
    ax.bar(0, lordo, color=NAVY, width=0.62)
    ax.annotate(f"{lordo:.2f}%".replace(".", ","), xy=(0, lordo), xytext=(0, 6),
                textcoords="offset points", ha="center", fontweight="bold",
                fontsize=11, color=NAVY)
    for i, (nome, quanto) in enumerate(voci, start=1):
        ax.bar(i, quanto, bottom=sinistra - quanto, color=ROSSO, width=0.62, alpha=0.85)
        ax.annotate(f"−{quanto:.2f}".replace(".", ","),
                    xy=(i, sinistra - quanto / 2), xytext=(0, 0),
                    textcoords="offset points", ha="center", va="center",
                    fontweight="bold", fontsize=10.5, color="white")
        ax.plot([i - 0.31, i + 0.31], [sinistra - quanto] * 2, color=GRIGIO, lw=0.9)
        sinistra -= quanto
    ax.bar(len(voci) + 1, netto, color=VERDE, width=0.62)
    ax.annotate(f"{netto:.2f}%".replace(".", ","), xy=(len(voci) + 1, netto),
                xytext=(0, 6), textcoords="offset points", ha="center",
                fontweight="bold", fontsize=11, color=VERDE)
    ax.set_xticks(range(len(etichette)))
    ax.set_xticklabels(etichette, fontsize=10)
    ax.set_ylabel("rendimento annuo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(0, lordo * 1.18)
    ax.set_title("Dove finisce il rendimento, su vent'anni")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()

    serie = world_mensile()
    fine = max(serie)
    inizio = f"{int(fine[:4]) - ANNI}-{fine[5:7]}"
    finali = plot_ter(serie, inizio, fine, OUT / "01_ter.png")
    plot_commissioni(OUT / "02_commissioni.png")

    # cascata: i valori vengono dallo studio, non da un conto nuovo
    lordo, netto = 7.96, 6.10
    ricorrenti, imposta = 0.70, 1.16
    assert abs(lordo - ricorrenti - imposta - netto) < 0.02, "la cascata non chiude"
    plot_cascata(lordo, [("costi\nricorrenti", ricorrenti), ("imposta\n26%", imposta)],
                 netto, OUT / "03_cascata.png")

    te = list(csv.DictReader(open(ROOT / "public" / "charts" /
                                  "rendimenti-netti-indici-azionari" /
                                  "robustness_tracking_error.csv", encoding="utf-8-sig")))
    world_te = {int(r["anni"]): float(r["mc_dev_std_bps"]) for r in te
                if r["indice"] == "MSCI World"}
    peggiore = max(te, key=lambda r: float(r["mc_dev_std_bps"]))

    sommario = {
        "ter": {
            "capitale": CAPITALE, "anni": ANNI, "da": inizio, "a": fine,
            "serie": "data/Msci_world/Msci_world_1969_EUR.csv, MSCI World in euro, mensile",
            "livelli": [{"ter": t, "etichetta": e, "nota": n,
                         "valore_finale": round(finali[e], 2)} for t, e, n, _ in LIVELLI],
            "differenza_economico_vs_attivo": round(
                finali["0,03% all'anno"] - finali["1,28% all'anno"], 2),
            "fonti": {
                "0,03%": "TER del piu' economico fra gli ETF su S&P 500 citati in "
                         "msci-world-ftse-all-world-sp500 (2026)",
                "0,21%": "ESMA, Costs and Performance of EU Retail Investment Products, "
                         "marzo 2026: ETF azionari passivi, costi correnti 2024",
                "1,28%": "stessa fonte: fondi azionari attivi non-ETF. La media di tutti "
                         "i non-ETF azionari e' 1,32%; l'Italia e' fra i paesi piu' cari",
            },
        },
        "commissioni": {
            "nota": "aritmetica su forme di listino tipiche, senza nomi di intermediari: "
                    "i listini cambiano, le forme no",
            "soglia_di_guardia": SOGLIA,
            "importo_minimo_per_restare_sotto_soglia_con_3_euro": 3.0 / SOGLIA,
            "esempi": [{"importo": x, "fissa_3_euro_pct": MINIMO / x}
                       for x in (50, 100, 200, 500, 1000)],
            "soglia_oltre_la_quale_la_percentuale_supera_il_minimo": MINIMO / PERCENTUALE,
        },
        "cascata": {
            "fonte": "public/charts/rendimenti-netti-indici-azionari/summary.json e "
                     "l'articolo quanto-rende-azionario-netto-tasse-costi: MSCI World, "
                     "mediana di 440 finestre ventennali",
            "lordo_pct": lordo, "costi_ricorrenti_pp": ricorrenti,
            "imposta_pp": imposta, "netto_pct": netto,
        },
        "tracking_error": {
            "fonte": "robustness_tracking_error.csv dello stesso studio, 200 simulazioni",
            "msci_world_dev_std_bps_per_orizzonte": world_te,
            "scarto_massimo_bps": {"indice": peggiore["indice"], "anni": int(peggiore["anni"]),
                                   "dev_std_bps": float(peggiore["mc_dev_std_bps"])},
        },
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 3 grafici + summary.json in {OUT}\n")
    print(f"TER: {CAPITALE:,} € dal {inizio} al {fine} ({ANNI} anni) sul MSCI World in euro")
    for t, e, n, _ in LIVELLI:
        print(f"   {e:16s} -> {finali[e]:>10,.0f} €   ({n})")
    print(f"   differenza fra il piu' economico e il fondo attivo: "
          f"{sommario['ter']['differenza_economico_vs_attivo']:,.0f} €")
    print("\nCOMMISSIONE FISSA DI 3 EURO, in percentuale del versamento")
    for e in sommario["commissioni"]["esempi"]:
        print(f"   su {e['importo']:>5} € -> {e['fissa_3_euro_pct']:.2%}")
    print(f"   per restare sotto lo 0,5% servono almeno "
          f"{sommario['commissioni']['importo_minimo_per_restare_sotto_soglia_con_3_euro']:.0f} €")
    print(f"\nCASCATA a 20 anni: {lordo}% lordo − {ricorrenti} costi − {imposta} imposta "
          f"= {netto}% netto")
    print("\nTRACKING ERROR, deviazione standard del risultato (MSCI World)")
    for k in sorted(world_te):
        print(f"   {k:>2} anni: {world_te[k]:.2f} punti base")
    p = sommario["tracking_error"]["scarto_massimo_bps"]
    print(f"   massimo su tutti gli indici: {p['dev_std_bps']:.2f} punti base "
          f"({p['indice']}, {p['anni']} anno/i)")


if __name__ == "__main__":
    main()
