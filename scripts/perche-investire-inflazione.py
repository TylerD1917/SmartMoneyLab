# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 1: cosa fa l'inflazione ai tuoi risparmi
===========================================================================

Primo episodio della collana "Le basi". Niente strategie: un solo concetto,
misurato sui dati italiani veri.

DATI
----
- Inflazione italiana annua 1960-2025: `data/Valute/FPCPITOTLZGITA.csv`
  (FRED, "Inflation, consumer prices for Italy", variazione % annua media).
- MSCI World total return in EURO, rendimenti mensili: si legge direttamente
  `public/tools/prestito-investimento-serie.json`, lo stesso file che
  alimenta il simulatore prestito-vs-investimento. Cosi' i due contenuti
  non possono divergere: se un giorno si corregge la serie, si correggono
  insieme.

SCELTE DICHIARATE
-----------------
- La finestra di confronto parte dal 2000, cioe' dal picco della bolla
  dot-com: e' il punto di partenza PIU' SFAVOREVOLE all'investimento fra
  quelli recenti, e serve proprio a non vendere un'illusione.
- Tutto al LORDO di tasse e costi. L'episodio insegna un concetto, non
  simula un portafoglio: l'erosione da inflazione agisce comunque su
  entrambi i lati, e il netto arriva nell'episodio 8.
- L'inflazione e' quella ITALIANA, l'indice azionario e' in EURO. Un
  lettore italiano subisce entrambe le cose.

OUTPUT in public/charts/perche-investire-inflazione/
----------------------------------------------------
  01_potere_acquisto.png    1.000 EUR fermi sul conto, potere d'acquisto
  02_inflazione_storica.png inflazione italiana anno per anno, 1960-2025
  03_liquido_vs_investito.png  1.000 EUR dal 2000: conto vs MSCI World, reale
  summary.json              tutti i numeri citati nell'articolo
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
CPI = ROOT / "data" / "Valute" / "FPCPITOTLZGITA.csv"
SERIE = ROOT / "public" / "tools" / "prestito-investimento-serie.json"
OUT = ROOT / "public" / "charts" / "perche-investire-inflazione"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

ANNO_START = 2000          # picco dot-com: la partenza peggiore recente
CAPITALE = 1000.0


# ----------------------------------------------------------------- dati
def inflazione_annua() -> dict[int, float]:
    """{anno: variazione % annua} dal CSV FRED."""
    out: dict[int, float] = {}
    with CPI.open(encoding="utf-8-sig") as fh:
        next(fh)
        for riga in fh:
            parti = riga.strip().split(",")
            if len(parti) < 2 or parti[1] in ("", "."):
                continue
            out[int(parti[0][:4])] = float(parti[1])
    return out


def world_annuo() -> dict[int, float]:
    """{anno: rendimento % annuo} del MSCI World total return in EUR,
    composto dai rendimenti mensili. Solo gli anni CIVILI COMPLETI: un anno
    con undici mesi non e' un rendimento annuo e non va confrontato."""
    d = json.loads(SERIE.read_text(encoding="utf-8"))
    s = d["serie"]["world"]
    a0, m0 = (int(x) for x in s["inizio"].split("-"))
    mesi: dict[int, list[float]] = {}
    anno, mese = a0, m0
    for r in s["r"]:
        mesi.setdefault(anno, []).append(r)
        mese += 1
        if mese > 12:
            mese, anno = 1, anno + 1
    return {a: (_composto(v) * 100) for a, v in mesi.items() if len(v) == 12}


def _composto(rendimenti: list[float]) -> float:
    p = 1.0
    for r in rendimenti:
        p *= 1 + r
    return p - 1


# ----------------------------------------------------------------- conti
def serie_confronto(infl: dict[int, float], world: dict[int, float]):
    """Dal 2000 all'ultimo anno completo disponibile per entrambe le serie.
    Ritorna anni, liquido nominale, liquido reale, investito reale."""
    fine = min(max(infl), max(world))
    anni = [ANNO_START]
    liquido_reale = [CAPITALE]
    investito_reale = [CAPITALE]
    prezzi = 1.0            # indice dei prezzi, base 1 nel 2000
    investito = CAPITALE
    for a in range(ANNO_START + 1, fine + 1):
        prezzi *= 1 + infl[a] / 100
        investito *= 1 + world[a] / 100
        anni.append(a)
        liquido_reale.append(CAPITALE / prezzi)
        investito_reale.append(investito / prezzi)
    return anni, [CAPITALE] * len(anni), liquido_reale, investito_reale, prezzi


def cumulata(infl: dict[int, float], da: int, a: int) -> float:
    """Di quanto sono saliti i prezzi fra due anni (fattore)."""
    p = 1.0
    for anno in range(da + 1, a + 1):
        p *= 1 + infl[anno] / 100
    return p


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
        lambda v, _: f"{v:,.0f} €".replace(",", ".")))


def plot_potere_acquisto(anni, nominale, reale, out: Path):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(anni, nominale, color=GRIGIO, lw=1.8, ls="--",
            label="Quanto leggi sull'estratto conto")
    ax.plot(anni, reale, color=ROSSO, lw=2.4,
            label="Quanto ci compri davvero")
    ax.fill_between(anni, reale, nominale, color=ROSSO, alpha=0.12)
    ax.annotate(f"{reale[-1]:,.0f} €".replace(",", "."),
                xy=(anni[-1], reale[-1]), xytext=(-12, -22),
                textcoords="offset points", color=ROSSO, fontweight="bold")
    perso = nominale[-1] - reale[-1]
    ax.set_title(f"1.000 € lasciati sul conto dal {anni[0]}: "
                 f"{perso:,.0f} € di potere d'acquisto in fumo".replace(",", "."))
    ax.set_ylabel("Potere d'acquisto, euro del " + str(anni[0]))
    ax.set_ylim(0, CAPITALE * 1.1)
    _euro(ax)
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_inflazione_storica(infl: dict[int, float], out: Path):
    anni = sorted(infl)
    val = [infl[a] for a in anni]
    fig, ax = plt.subplots(figsize=(10, 5))
    colori = [ROSSO if v >= 4 else (GOLD if v >= 2 else NAVY) for v in val]
    ax.bar(anni, val, color=colori, width=0.8)
    # La linea del 2% vale solo da quando esiste la BCE: tracciarla sul 1960
    # sarebbe un anacronismo, e il lettore la leggerebbe come un giudizio su
    # anni in cui quell'obiettivo non esisteva.
    ax.hlines(2, 1999, max(anni) + 0.5, color=GRIGIO, lw=1.4, ls="--")
    ax.annotate("obiettivo BCE: 2%\n(dal 1999)", xy=(2014, 2), xytext=(0, 10),
                textcoords="offset points", color=GRIGIO, fontsize=9.5,
                ha="center", linespacing=1.3)
    picco = max(anni, key=lambda a: infl[a])
    ax.annotate(f"{picco}: {infl[picco]:.1f}%".replace(".", ","),
                xy=(picco, infl[picco]), xytext=(10, -4),
                textcoords="offset points", fontweight="bold", color=ROSSO)
    ax.annotate(f"2022: {infl[2022]:.1f}%".replace(".", ","),
                xy=(2022, infl[2022]), xytext=(-46, 4),
                textcoords="offset points", fontweight="bold", color=ROSSO)
    ax.set_title("L'inflazione italiana, anno per anno")
    ax.set_ylabel("Variazione annua dei prezzi al consumo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_confronto(anni, nominale, liquido, investito, out: Path):
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.plot(anni, nominale, color=GRIGIO, lw=1.6, ls="--", label="Fermo sul conto, nominale")
    ax.plot(anni, liquido, color=ROSSO, lw=2.2, label="Fermo sul conto, potere d'acquisto")
    ax.plot(anni, investito, color=NAVY, lw=2.6, label="MSCI World in euro, potere d'acquisto")
    ax.axhline(CAPITALE, color=GRIGIO, lw=0.8, alpha=0.5)
    for serie, colore in ((liquido, ROSSO), (investito, NAVY)):
        ax.annotate(f"{serie[-1]:,.0f} €".replace(",", "."),
                    xy=(anni[-1], serie[-1]), xytext=(-14, 8),
                    textcoords="offset points", color=colore, fontweight="bold")
    ax.set_title(f"1.000 € dal {anni[0]} — partendo dal picco della bolla dot-com")
    ax.set_ylabel("Potere d'acquisto, euro del " + str(anni[0]))
    _euro(ax)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    infl = inflazione_annua()
    world = world_annuo()
    anni, nominale, liquido, investito, prezzi = serie_confronto(infl, world)

    plot_potere_acquisto(anni, nominale, liquido, OUT / "01_potere_acquisto.png")
    plot_inflazione_storica(infl, OUT / "02_inflazione_storica.png")
    plot_confronto(anni, nominale, liquido, investito, OUT / "03_liquido_vs_investito.png")

    a0, a1 = anni[0], anni[-1]
    anni_cpi = sorted(infl)
    media = sum(infl.values()) / len(infl)
    sommario = {
        "fonte_inflazione": "FRED FPCPITOTLZGITA (Inflation, consumer prices for Italy), media annua",
        "fonte_azionario": "public/tools/prestito-investimento-serie.json, MSCI World total return in EUR",
        "periodo_cpi": [anni_cpi[0], anni_cpi[-1]],
        "inflazione_media_annua": round(media, 2),
        "inflazione_mediana_annua": round(sorted(infl.values())[len(infl) // 2], 2),
        "anno_peggiore": {"anno": max(infl, key=infl.get), "valore": round(max(infl.values()), 1)},
        "inflazione_2022": round(infl[2022], 1),
        "inflazione_2024": round(infl[2024], 1),
        "inflazione_2025": round(infl[2025], 1),
        "prezzi_1960_2025_fattore": round(cumulata(infl, anni_cpi[0], anni_cpi[-1]), 2),
        "confronto": {
            "da": a0, "a": a1, "capitale": CAPITALE,
            "prezzi_fattore": round(prezzi, 3),
            "inflazione_cumulata_pct": round((prezzi - 1) * 100, 1),
            "liquido_reale_finale": round(liquido[-1], 0),
            "liquido_perso": round(CAPITALE - liquido[-1], 0),
            "investito_reale_finale": round(investito[-1], 0),
            "investito_nominale_finale": round(investito[-1] * prezzi, 0),
            "rapporto_investito_su_liquido": round(investito[-1] / liquido[-1], 1),
        },
        "anni_sopra_4pct": sum(1 for v in infl.values() if v >= 4),
        "anni_totali": len(infl),
    }
    (OUT / "summary.json").write_text(
        json.dumps(sommario, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] 3 grafici + summary.json in {OUT}")
    print(json.dumps(sommario["confronto"], ensure_ascii=False, indent=2))
    print(f"inflazione media {media:.2f}%/anno su {len(infl)} anni; "
          f"prezzi {anni_cpi[0]}->{anni_cpi[-1]} x{sommario['prezzi_1960_2025_fattore']}")


if __name__ == "__main__":
    main()
