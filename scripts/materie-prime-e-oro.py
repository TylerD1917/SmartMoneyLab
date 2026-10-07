# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 6: materie prime e oro
=========================================================

Il filo conduttore dell'episodio e' che questi asset non producono flussi di
cassa. I tre grafici servono a mostrare cosa comporta, senza prediche.

1. L'ORO IN TERMINI REALI. Il prezzo nominale dell'oro racconta una storia
   falsa: sale sempre, come tutto cio' che si misura in dollari che perdono
   valore. Deflazionato per il CPI americano, il grafico mostra il picco del
   gennaio 1980 e quanti anni ci sono voluti per tornare in pari.

2. MILLE DOLLARI dal 1988 in oro e nell'S&P 500 total return. Non e' una gara
   truccata a favore delle azioni: il periodo comprende il decennio d'oro
   dell'oro (2001-2011) e la corsa del 2024-2026.

3. LE MATERIE PRIME VERE, via DBC, contro lo stesso S&P 500. Vent'anni che
   mostrano il problema del paniere di futures.

NOTA SULLE DATE DI PARTENZA
---------------------------
Fino all'agosto 1971 il prezzo dell'oro era fissato per legge: 20,67 dollari
l'oncia fino al 1933, 35 dollari dopo. Un "rendimento" calcolato dentro quel
regime non misura un mercato, misura due decisioni politiche. Per questo lo
script riporta il rendimento reale da quattro date diverse: il lettore vede
quanto la scelta della data cambi la risposta, invece di riceverne una sola
presentata come la verita'.

OUTPUT in public/charts/materie-prime-e-oro/
--------------------------------------------
  01_oro_reale.png      il prezzo dell'oro in dollari di oggi
  02_mille_dollari.png  1.000 $ dal 1988: oro contro azioni
  03_materie_prime.png  un paniere di materie prime contro le azioni
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
OUT = ROOT / "public" / "charts" / "materie-prime-e-oro"

ORO = ROOT / "data" / "Gold" / "gold_monthly.csv"
CPI = ROOT / "data" / "Valute" / "CPIAUCSL_USA.csv"
SP = ROOT / "data" / "Sp500" / "Sp500_TotalReturn1988_USD.csv"
DBC = ROOT / "data" / "Materie_prime" / "dbc_monthly.csv"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

PARTENZE = ["1947-01", "1971-08", "1975-01", "1980-01"]
NOTE_PARTENZE = {
    "1947-01": "inizio della serie CPI mensile",
    "1971-08": "fine della convertibilita' in oro del dollaro",
    "1975-01": "ritorno alla detenzione legale per i privati americani",
    "1980-01": "massimo della bolla",
}


# ----------------------------------------------------------------- dati
def _num(x: str) -> float | None:
    x = (x or "").strip().replace("$", "").replace(",", "")
    try:
        return float(x)
    except ValueError:
        return None


def mensile(path: Path, col_data: str, col_valore: str) -> dict[str, float]:
    """Ultimo valore disponibile di ogni mese, chiave AAAA-MM."""
    out: dict[str, float] = {}
    for riga in csv.DictReader(open(path, encoding="utf-8-sig")):
        v = _num(riga.get(col_valore, ""))
        d = (riga.get(col_data) or "").strip()
        if v is not None and len(d) >= 7:
            out[d[:7]] = v          # le serie sono in ordine crescente
    return out


def oro() -> dict[str, float]:
    out = {}
    for r in csv.reader(open(ORO, encoding="utf-8-sig")):
        if r and r[0] != "Date" and len(r) > 1:
            v = _num(r[1])
            if v is not None:
                out[r[0][:7]] = v
    return out


# ----------------------------------------------------------------- conti
def mesi(a: str, b: str) -> int:
    return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])


def cagr(a: float, b: float, anni: float) -> float:
    return (b / a) ** (1 / anni) - 1


def crescita(serie: dict[str, float], iniziale: float = 1000.0):
    d = sorted(serie)
    a, b = d[0], d[-1]
    anni = mesi(a, b) / 12
    return {"da": a, "a": b, "anni": anni,
            "finale": iniziale * serie[b] / serie[a],
            "cagr": cagr(serie[a], serie[b], anni)}


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def _x(d: str) -> float:
    return int(d[:4]) + (int(d[5:7]) - 1) / 12


def euro(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}".replace(",", ".")))


def plot_oro_reale(reale, picco, fondo, recupero, base, out: Path):
    d = sorted(reale)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot([_x(k) for k in d], [reale[k] for k in d], color=GOLD, lw=2.0)
    ax.fill_between([_x(k) for k in d], [reale[k] for k in d], 0, color=GOLD, alpha=0.10)

    ax.annotate(f"gennaio 1980\n{reale[picco]:,.0f} $".replace(",", "."),
                xy=(_x(picco), reale[picco]), xytext=(-95, 18),
                textcoords="offset points", color=ROSSO, fontweight="bold",
                fontsize=10, ha="left",
                arrowprops=dict(arrowstyle="->", color=ROSSO, lw=1.2))
    ax.annotate(f"aprile 2001\n{reale[fondo]:,.0f} $".replace(",", "."),
                xy=(_x(fondo), reale[fondo]), xytext=(-18, 62),
                textcoords="offset points", color=GRIGIO, fontsize=10, ha="center",
                arrowprops=dict(arrowstyle="->", color=GRIGIO, lw=1.2))
    if recupero:
        ax.annotate(f"in pari dopo {mesi(picco, recupero) / 12:.0f} anni",
                    xy=(_x(recupero), reale[recupero]), xytext=(-150, 22),
                    textcoords="offset points", color=NAVY, fontweight="bold",
                    fontsize=10, ha="left",
                    arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))
        ax.plot([_x(picco), _x(recupero)], [reale[picco]] * 2,
                color=ROSSO, ls=":", lw=1.3)

    ax.set_title(f"Il prezzo dell'oro in dollari di oggi, {d[0][:4]}-{d[-1][:4]}")
    ax.set_ylabel(f"dollari del {base[:4]} per oncia")
    ax.set_ylim(0, max(reale.values()) * 1.18)
    euro(ax)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_confronto(serie: dict[str, dict], titolo: str, sottotitolo: str,
                   colori: dict[str, str], out: Path):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for nome, s in serie.items():
        d = sorted(s)
        base = s[d[0]]
        ax.plot([_x(k) for k in d], [1000 * s[k] / base for k in d],
                color=colori[nome], lw=2.0, label=nome)
        fin = 1000 * s[d[-1]] / base
        ax.annotate(f"{fin:,.0f} $".replace(",", "."), xy=(_x(d[-1]), fin),
                    xytext=(6, -4), textcoords="offset points",
                    color=colori[nome], fontweight="bold", fontsize=10)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.set_title(titolo)
    ax.set_ylabel(sottotitolo)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}".replace(",", ".")))
    ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    ax.margins(x=0.08)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()

    g = oro()
    cpi = mensile(CPI, "observation_date", "CPIAUCSL")
    sp = mensile(SP, "Date", "Close")
    dbc = mensile(DBC, "Date", "adjclose")

    comuni = sorted(set(g) & set(cpi))
    base = comuni[-1]
    reale = {d: g[d] * cpi[base] / cpi[d] for d in comuni}

    picco = max((d for d in reale if d.startswith("1980")), key=lambda d: reale[d])
    dopo = [d for d in comuni if d > picco and reale[d] >= reale[picco]]
    recupero = dopo[0] if dopo else None
    fondo = min((d for d in comuni if picco < d < "2005-01"), key=lambda d: reale[d])

    oro_sp = {d: g[d] for d in sorted(set(g) & set(sp))}
    sp_oro = {d: sp[d] for d in oro_sp}
    dbc_sp = {d: dbc[d] for d in sorted(set(dbc) & set(sp))}
    sp_dbc = {d: sp[d] for d in dbc_sp}

    plot_oro_reale(reale, picco, fondo, recupero, base, OUT / "01_oro_reale.png")
    plot_confronto({"oro": oro_sp, "azioni (S&P 500 total return)": sp_oro},
                   f"1.000 dollari dal {sorted(oro_sp)[0][:4]}: oro e azioni a confronto",
                   "valore, scala logaritmica",
                   {"oro": GOLD, "azioni (S&P 500 total return)": NAVY},
                   OUT / "02_mille_dollari.png")
    plot_confronto({"materie prime (paniere di futures)": dbc_sp,
                    "azioni (S&P 500 total return)": sp_dbc},
                   f"1.000 dollari dal {sorted(dbc_sp)[0][:4]}: materie prime e azioni",
                   "valore, scala logaritmica",
                   {"materie prime (paniere di futures)": ROSSO,
                    "azioni (S&P 500 total return)": NAVY},
                   OUT / "03_materie_prime.png")

    mx_dbc = max((d for d in dbc_sp if d <= min(dbc_sp, key=dbc_sp.get)),
                 key=lambda d: dbc_sp[d])
    mn_dbc = min(dbc_sp, key=dbc_sp.get)

    sommario = {
        "oro_reale": {
            "fonte_prezzo": "data/Gold/gold_monthly.csv, prezzo mensile in dollari per oncia",
            "fonte_cpi": "FRED CPIAUCSL, indice dei prezzi al consumo USA, in data/Valute/",
            "dollari_del": base,
            "rendimenti_per_data_di_partenza": {
                p: {"nota": NOTE_PARTENZE[p],
                    "anni": round(mesi(p, base) / 12, 1),
                    "nominale_da": g[p], "nominale_a": g[base],
                    "cagr_nominale": cagr(g[p], g[base], mesi(p, base) / 12),
                    "reale_da": reale[p], "reale_a": reale[base],
                    "cagr_reale": cagr(reale[p], reale[base], mesi(p, base) / 12)}
                for p in PARTENZE if p in reale},
            "picco_1980": {"mese": picco, "nominale": g[picco], "reale": reale[picco]},
            "minimo_successivo": {"mese": fondo, "reale": reale[fondo],
                                  "caduta_dal_picco": reale[fondo] / reale[picco] - 1},
            "recupero_del_picco": {"mese": recupero,
                                   "anni": round(mesi(picco, recupero) / 12, 1)} if recupero else None,
        },
        "oro_vs_azioni": {"oro": crescita(oro_sp), "azioni": crescita(sp_oro)},
        "materie_prime_vs_azioni": {
            "materie_prime": crescita(dbc_sp), "azioni": crescita(sp_dbc),
            "fonte": "DBC, paniere di futures su materie prime, prezzo mensile aggiustato",
            "caduta": {"da": mx_dbc, "a": mn_dbc,
                       "variazione": dbc_sp[mn_dbc] / dbc_sp[mx_dbc] - 1},
        },
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 3 grafici + summary.json in {OUT}\n")
    print(f"ORO REALE (dollari di {base})")
    for p in PARTENZE:
        v = sommario["oro_reale"]["rendimenti_per_data_di_partenza"][p]
        print(f"  da {p} ({v['anni']:>4.1f} anni, {NOTE_PARTENZE[p]})")
        print(f"      nominale {v['cagr_nominale']:+6.2%}   reale {v['cagr_reale']:+6.2%}"
              f"   {v['reale_da']:>8,.0f} -> {v['reale_a']:>8,.0f} $")
    print(f"  picco {picco}: {reale[picco]:,.0f} $  ->  minimo {fondo}: {reale[fondo]:,.0f} $ "
          f"({reale[fondo] / reale[picco] - 1:+.0%})  ->  in pari {recupero} "
          f"({mesi(picco, recupero) / 12:.1f} anni)")
    for nome, blocco in (("ORO vs AZIONI", "oro_vs_azioni"),
                         ("MATERIE PRIME vs AZIONI", "materie_prime_vs_azioni")):
        print(f"\n{nome}")
        for k in list(sommario[blocco])[:2]:
            v = sommario[blocco][k]
            print(f"  {k:>14}: {v['da']} -> {v['a']} ({v['anni']:.1f} anni)  "
                  f"1.000 $ -> {v['finale']:>9,.0f} $   CAGR {v['cagr']:+.2%}")
    c = sommario["materie_prime_vs_azioni"]["caduta"]
    print(f"  caduta DBC: {c['da']} -> {c['a']}  {c['variazione']:+.0%}")


if __name__ == "__main__":
    main()
