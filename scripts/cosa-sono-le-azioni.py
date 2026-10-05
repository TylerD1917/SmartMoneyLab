# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 4: cosa sono le azioni
=========================================================

Due aziende come esempio, scelte da Tyler perche' stanno agli antipodi:
Coca-Cola (il classico del value investing) e Tesla (il suo opposto).

DATI
----
- Prezzi giornalieri da `data/Single_stocks/KO.csv` e `Tesla.csv`, serie
  aggiustate per frazionamenti (e, per Coca-Cola, anche per i dividendi:
  la serie parte da 0,12 dollari nel 1975 e il CAGR del 13,4% su 51 anni e'
  coerente con un total return, non con il solo prezzo).
- I dati fondamentali (P/E, EPS, capitalizzazione, dividendo, beta) sono
  quelli di quotazione del 5 ottobre 2026 forniti da Tyler; fatturato TTM
  da stockanalysis.com.

LE TRE MISURE SI CHIUDONO FRA LORO
----------------------------------
P/E = (P/S) / margine netto. Non e' una coincidenza ed e' il controllo che
questo script esegue: se i numeri raccolti da fonti diverse non chiudono,
uno dei tre e' sbagliato.

OUTPUT in public/charts/cosa-sono-le-azioni/
--------------------------------------------
  01_mille_euro.png      1.000 euro dall'IPO di Tesla, scala logaritmica
  02_drawdown.png        la stessa storia vista dal lato delle discese
  summary.json
"""
from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
DATI = ROOT / "data" / "Single_stocks"
OUT = ROOT / "public" / "charts" / "cosa-sono-le-azioni"

NAVY = "#1e3a8a"
ROSSO = "#dc2626"
GRIGIO = "#64748b"
CAPITALE = 1000.0

# Quotazioni del 5 ottobre 2026 (fonte: scheda titolo) e fatturato TTM.
FONDAMENTALI = {
    "Coca-Cola": {"prezzo": 85.65, "pe": 25.72, "eps": 3.33, "cap_mld": 368.513,
                  "dividendo": 2.12, "beta": 0.34, "fatturato_mld": 50.13,
                  "min52": 65.84, "max52": 92.49, "target": 94.65},
    "Tesla": {"prezzo": 370.00, "pe": 343.14, "eps": 1.08, "cap_mld": 1464.0,
              "dividendo": 0.0, "beta": 1.92, "fatturato_mld": 103.62,
              "min52": 297.38, "max52": 498.83, "target": 396.41},
}


# ----------------------------------------------------------------- dati
def serie(nome_file: str) -> dict[str, float]:
    out = {}
    with io.open(DATI / nome_file, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            try:
                out[r["Date"]] = float(r["Close"])
            except (ValueError, KeyError):
                pass
    return out


def metriche(s: dict[str, float], date: list[str]) -> dict:
    v = [s[d] for d in date]
    cresc = v[-1] / v[0]
    anni = len(date) / 252
    picco, peggiore, sotto = -1e18, 0.0, 0
    for x in v:
        picco = max(picco, x)
        q = x / picco - 1
        peggiore = min(peggiore, q)
        if q < -1e-9:
            sotto += 1
    r = [v[i] / v[i - 1] - 1 for i in range(1, len(v))]
    m = sum(r) / len(r)
    vol = math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1) * 252)
    return {"crescita": cresc, "montante": CAPITALE * cresc,
            "cagr": cresc ** (1 / anni) - 1, "drawdown_peggiore": peggiore,
            "quota_sotto_il_massimo": sotto / len(v), "volatilita": vol,
            "anni": anni}


def drawdown(s: dict[str, float], date: list[str]) -> list[float]:
    out, picco = [], -1e18
    for d in date:
        picco = max(picco, s[d])
        out.append(s[d] / picco - 1)
    return out


def fondamentali_derivati() -> dict:
    out = {}
    for nome, f in FONDAMENTALI.items():
        utile = f["cap_mld"] / f["pe"]                 # utile netto implicito
        ps = f["cap_mld"] / f["fatturato_mld"]
        margine = utile / f["fatturato_mld"]
        out[nome] = {
            **f,
            "utile_netto_mld": utile,
            "price_sales": ps,
            "margine_netto": margine,
            "earnings_yield": 1 / f["pe"],
            "euro_di_utile_ogni_100_investiti": 100 / f["pe"],
            "payout": (f["dividendo"] / f["eps"]) if f["eps"] else 0.0,
            "dividend_yield": f["dividendo"] / f["prezzo"],
            # controllo di chiusura: P/E deve essere (P/S) / margine
            "pe_ricalcolato": ps / margine,
        }
    return out


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def _anni(date: list[str]) -> list[float]:
    return [int(d[:4]) + (int(d[5:7]) - 1) / 12 + (int(d[8:10]) - 1) / 365 for d in date]


def plot_mille(ko, ts, date, out: Path):
    x = _anni(date)
    k0, t0 = ko[date[0]], ts[date[0]]
    yk = [CAPITALE * ko[d] / k0 for d in date]
    yt = [CAPITALE * ts[d] / t0 for d in date]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(x, yk, color=NAVY, lw=2.0, label="Coca-Cola")
    ax.plot(x, yt, color=ROSSO, lw=2.0, label="Tesla")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f} €".replace(",", ".")))
    ax.set_yticks([1000, 3000, 10000, 30000, 100000, 300000])
    for y, colore, nome in ((yk, NAVY, "Coca-Cola"), (yt, ROSSO, "Tesla")):
        ax.annotate(f"{y[-1]:,.0f} €".replace(",", "."), xy=(x[-1], y[-1]),
                    xytext=(-8, 10), textcoords="offset points",
                    color=colore, fontweight="bold", ha="right")
    ax.set_title("1.000 € investiti il giorno della quotazione di Tesla")
    ax.set_ylabel("valore, scala logaritmica")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_drawdown(ko, ts, date, out: Path):
    x = _anni(date)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ax, s, colore, nome in ((a1, ko, NAVY, "Coca-Cola"), (a2, ts, ROSSO, "Tesla")):
        d = drawdown(s, date)
        ax.fill_between(x, [v * 100 for v in d], 0, color=colore, alpha=0.3, lw=0)
        ax.plot(x, [v * 100 for v in d], color=colore, lw=1.2)
        peggio = min(d)
        ax.annotate(f"{nome}: peggiore {peggio*100:.1f}%".replace(".", ","),
                    xy=(0.015, 0.08), xycoords="axes fraction",
                    color=colore, fontweight="bold", fontsize=11)
        ax.set_ylim(-80, 4)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    a1.set_title("La stessa storia, vista dal lato delle discese")
    a2.set_xlabel("")
    fig.supylabel("distanza dal massimo precedente", fontsize=11)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    ko, ts = serie("KO.csv"), serie("Tesla.csv")
    date = sorted(set(ko) & set(ts))
    mk, mt = metriche(ko, date), metriche(ts, date)
    fond = fondamentali_derivati()

    plot_mille(ko, ts, date, OUT / "01_mille_euro.png")
    plot_drawdown(ko, ts, date, OUT / "02_drawdown.png")

    tutte_ko = sorted(ko)
    anni_ko = len(tutte_ko) / 252
    sommario = {
        "serie": {"inizio_comune": date[0], "fine": date[-1], "sedute": len(date),
                  "ko_dal": tutte_ko[0], "nota": "prezzi aggiustati; per KO anche per i dividendi"},
        "coca_cola_lungo_periodo": {
            "da": tutte_ko[0], "a": tutte_ko[-1], "anni": round(anni_ko, 1),
            "crescita": round(ko[tutte_ko[-1]] / ko[tutte_ko[0]], 0),
            "cagr": round((ko[tutte_ko[-1]] / ko[tutte_ko[0]]) ** (1 / anni_ko) - 1, 4)},
        "dal_debutto_di_tesla": {
            "Coca-Cola": {k: round(v, 4) for k, v in mk.items()},
            "Tesla": {k: round(v, 4) for k, v in mt.items()}},
        "fondamentali_5_ottobre_2026": {
            nome: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items()}
            for nome, f in fond.items()},
        "confronti": {
            "tesla_vale_volte_coca_cola": round(fond["Tesla"]["cap_mld"] / fond["Coca-Cola"]["cap_mld"], 2),
            "coca_cola_guadagna_volte_tesla": round(fond["Coca-Cola"]["utile_netto_mld"] / fond["Tesla"]["utile_netto_mld"], 2),
            "tesla_fattura_volte_coca_cola": round(fond["Tesla"]["fatturato_mld"] / fond["Coca-Cola"]["fatturato_mld"], 2)},
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 2 grafici + summary.json in {OUT}\n")
    print(f"periodo comune {date[0]} -> {date[-1]} ({mk['anni']:.1f} anni)")
    for nome, m in (("Coca-Cola", mk), ("Tesla", mt)):
        print(f"  {nome:10} 1.000 € -> {m['montante']:>10,.0f} €  CAGR {m['cagr']:>6.1%}  "
              f"drawdown {m['drawdown_peggiore']:>6.1%}  vol {m['volatilita']:>5.1%}")
    print()
    for nome, f in fond.items():
        print(f"  {nome:10} P/E {f['pe']:>6.2f}  P/S {f['price_sales']:>5.2f}  "
              f"margine {f['margine_netto']:>5.1%}  utile {f['utile_netto_mld']:>5.1f} mld  "
              f"payout {f['payout']:>5.1%}  yield {f['dividend_yield']:>5.2%}")
        scarto = abs(f["pe_ricalcolato"] - f["pe"]) / f["pe"]
        stato = "OK" if scarto < 0.01 else f"ATTENZIONE scarto {scarto:.1%}"
        print(f"             controllo P/E = (P/S)/margine -> {f['pe_ricalcolato']:.2f}  [{stato}]")
    c = sommario["confronti"]
    print(f"\n  Tesla vale {c['tesla_vale_volte_coca_cola']}x Coca-Cola, fattura "
          f"{c['tesla_fattura_volte_coca_cola']}x, e Coca-Cola guadagna "
          f"{c['coca_cola_guadagna_volte_tesla']}x Tesla")


if __name__ == "__main__":
    main()
