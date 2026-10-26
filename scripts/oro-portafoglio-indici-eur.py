"""
SmartMoneyLab - Oro in portafoglio, visto da un investitore in euro
===================================================================

Estensione di `ha-senso-oro-portafoglio.py`, che misura tutto in dollari
sull'S&P 500. Qui le stesse quattro allocazioni buy & hold (100% azionario,
90/10, 75/25, 50/50) sono misurate in EURO su due azionari globali, che
sono i portafogli realmente diffusi fra i risparmiatori italiani:

  - MSCI World total return in euro, da gennaio 1976
  - MSCI ACWI IMI total return in euro, da giugno 1994 (prima non esiste)

L'oro e' convertito in euro: per chi investe in euro il metallo e' anche
una posizione in dollari, e ignorarlo falserebbe il risultato.

Cambio EUR/USD mensile:
  - dal gennaio 1999: BCE via FRED (DEXUSEU), ultima quotazione del mese
  - prima: marco tedesco per dollaro (FRED EXGEUS) convertito al tasso
    irrevocabile 1 EUR = 1,95583 DEM. E' la prassi standard per
    ricostruire serie in euro prima dell'unione monetaria.

Metodologia identica all'articolo principale, da cui importiamo le
funzioni: buy & hold puro senza ribilanciamento, finestre mobili a 5, 10 e
20 anni con passo trimestrale, rendimenti nominali e lordi.

OUTPUT in public/charts/ha-senso-oro-portafoglio/
  06_eur_ventagli_10y.png   distribuzione dei rendimenti decennali
  07_eur_costo_protezione.png  quanto costa l'oro e quanto protegge
  08_eur_sensibilita.png    quanto cambia il risultato al variare della
                            data di partenza (il controllo piu' importante)
  summary_eur.json

USO: python scripts/oro-portafoglio-indici-eur.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
OUT = ROOT / "public" / "charts" / "ha-senso-oro-portafoglio"
OUT.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location(
    "motore_oro", HERE / "ha-senso-oro-portafoglio.py")
M = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = M   # serve alle dataclass del modulo importato
_spec.loader.exec_module(M)

INIZIO = pd.Timestamp("1976-01-01")
FINE = pd.Timestamp("2026-06-30")
DEM_PER_EURO = 1.95583
PORTAFOGLI = M.PORTFOLIOS
COLORI = M.COLORS
FINESTRE = {"5y": 60, "10y": 120, "20y": 240}
PASSO = 3


# ------------------------------------------------------------------ dati
def _indice_mensile(path: Path, colonna: str) -> pd.Series:
    """CSV MSCI in formato 'MM/AAAA, livello'. Ritorna il livello mensile."""
    d = pd.read_csv(path)
    d["dt"] = pd.to_datetime(d["Data"], format="%m/%Y")
    return pd.to_numeric(d.set_index("dt").sort_index()[colonna],
                         errors="coerce").dropna()


def cambio_usd_per_euro() -> pd.Series:
    """Dollari per un euro, mensile, dal 1971. Marco fino al 1998."""
    dem = pd.read_csv(DATA / "Valute" / "DEM_USD_1971_2001.csv")
    dem["dt"] = pd.to_datetime(dem["observation_date"])
    marco = pd.to_numeric(dem.set_index("dt").sort_index()["EXGEUS"],
                          errors="coerce").dropna()
    prima = (DEM_PER_EURO / marco)
    prima = prima[prima.index < pd.Timestamp("1999-01-01")]

    dx = pd.read_csv(DATA / "Valute" / "DEXUSEU.csv")
    dx["dt"] = pd.to_datetime(dx["observation_date"])
    dopo = pd.to_numeric(dx.set_index("dt").sort_index()["DEXUSEU"],
                         errors="coerce").dropna().resample("ME").last()
    dopo.index = dopo.index.to_period("M").to_timestamp()

    fx = pd.concat([prima, dopo]).sort_index()
    salto = abs(fx.loc["1999-01-01"] / fx.loc["1998-12-01"] - 1)
    if salto > 0.05:
        raise RuntimeError(f"giuntura del cambio sospetta: {salto:.2%}")
    print(f"[check] giuntura cambio marco/euro al 1999: {salto:+.2%}")
    return fx


def oro_in_euro() -> pd.Series:
    """Rendimenti mensili dell'oro per chi misura in euro."""
    prezzo_usd = M.load_gold_monthly_price()
    fx = cambio_usd_per_euro()
    comune = prezzo_usd.index.intersection(fx.index)
    return (prezzo_usd.loc[comune] / fx.loc[comune]).pct_change().dropna()


def universi() -> dict[str, tuple[pd.Series, pd.Series]]:
    oro = oro_in_euro()
    out = {}
    for nome, path, col in [
        ("MSCI World", DATA / "Msci_world" / "Msci_world_1969_EUR.csv", "MSCI World"),
        ("MSCI ACWI IMI", DATA / "Msci_ACWI_FTSE_all_world" / "Msci_ACWI_IMI_1993_EUR.csv",
         "MSCI ACWI IMI"),
    ]:
        az = _indice_mensile(path, col).pct_change().dropna()
        k = az.index.intersection(oro.index)
        k = k[(k >= INIZIO) & (k <= FINE)]
        out[nome] = (az.loc[k], oro.loc[k])
    return out


# ----------------------------------------------------------------- stime
def riepilogo(az: pd.Series, oro: pd.Series) -> dict:
    r = {"mesi": len(az), "da": str(az.index.min().date()),
         "a": str(az.index.max().date()),
         "correlazione": float(np.corrcoef(az, oro)[0, 1]),
         "portafogli": {}}
    for nome, pesi in PORTAFOGLI.items():
        serie = M.simulate_buy_and_hold(az, oro, pesi)
        voce = {"cagr": M.cagr(serie), "mdd": M.max_drawdown(serie),
                "vol": M.volatility_annualized(serie), "finestre": {}}
        for et, mesi in FINESTRE.items():
            if len(az) < mesi:
                continue
            st = M.rolling_window_stats_buy_and_hold(az, oro, pesi, mesi, PASSO)
            c = np.array([s.cagr for s in st])
            voce["finestre"][et] = {
                "n": len(c), "p5": float(np.percentile(c, 5)),
                "p50": float(np.median(c)), "p95": float(np.percentile(c, 95)),
                "quota_negative": float((c < 0).mean()),
            }
        r["portafogli"][nome] = voce
    return r


def sensibilita(partenze=("1971-02", "1976-01", "1980-01", "1990-01", "2000-01")) -> dict:
    """Quanto il risultato dipende dalla data di partenza. Gli anni Settanta
    contengono la riprezzatura dell'oro dopo la fine di Bretton Woods: senza
    questo controllo il lettore non puo' giudicare quanto pesa."""
    oro = oro_in_euro()
    az = _indice_mensile(DATA / "Msci_world" / "Msci_world_1969_EUR.csv",
                         "MSCI World").pct_change().dropna()
    fuori = {}
    for p in partenze:
        k = az.index.intersection(oro.index)
        k = k[(k >= pd.Timestamp(p)) & (k <= FINE)]
        if len(k) < 240:
            continue
        fuori[p] = {n: M.cagr(M.simulate_buy_and_hold(az.loc[k], oro.loc[k], w))
                    for n, w in PORTAFOGLI.items()}
        fuori[p]["mesi"] = len(k)
    return fuori


# --------------------------------------------------------------- grafici
def _stile(ax, titolo, ylabel, xlabel=""):
    M._style_axes(ax, titolo, ylabel, xlabel)


def grafico_ventagli(dati: dict, out: Path):
    fig, assi = plt.subplots(1, 2, figsize=(12.4, 6.2), sharey=True)
    for ax, (nome, (az, oro)) in zip(assi, dati.items()):
        serie = []
        for p in PORTAFOGLI:
            st = M.rolling_window_stats_buy_and_hold(az, oro, PORTAFOGLI[p], 120, PASSO)
            serie.append([s.cagr * 100 for s in st])
        bp = ax.boxplot(serie, labels=list(PORTAFOGLI), patch_artist=True,
                        widths=0.55, showfliers=False, medianprops=dict(color="white", lw=2))
        for patch, p in zip(bp["boxes"], PORTAFOGLI):
            patch.set_facecolor(COLORI[p]); patch.set_alpha(0.9); patch.set_edgecolor("none")
        ax.axhline(0, color="#64748b", lw=1, ls="--")
        periodo = f"{az.index.min():%Y}-{az.index.max():%Y}"
        _stile(ax, f"{nome} + oro, in euro ({periodo})",
               "CAGR della finestra decennale (%)" if ax is assi[0] else "")
    fig.suptitle("Rendimenti su dieci anni, in euro: tutte le finestre mobili",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def grafico_costo_protezione(ris: dict, out: Path):
    fig, assi = plt.subplots(1, 2, figsize=(12.4, 5.6))
    nomi = list(ris)
    x = np.arange(len(PORTAFOGLI)); larg = 0.38
    for i, nome in enumerate(nomi):
        c = [ris[nome]["portafogli"][p]["cagr"] * 100 for p in PORTAFOGLI]
        p5 = [ris[nome]["portafogli"][p]["finestre"]["10y"]["p5"] * 100 for p in PORTAFOGLI]
        assi[0].bar(x + (i - 0.5) * larg, c, larg, label=nome,
                    color=["#1e3a8a", "#d97706"][i], alpha=0.9)
        assi[1].bar(x + (i - 0.5) * larg, p5, larg, label=nome,
                    color=["#1e3a8a", "#d97706"][i], alpha=0.9)
    for ax, t, y in [(assi[0], "Quanto rende, tutto il periodo", "CAGR (%)"),
                     (assi[1], "Quanto protegge: peggior 5% dei dieci anni",
                      "CAGR del 5° percentile (%)")]:
        ax.set_xticks(x); ax.set_xticklabels(list(PORTAFOGLI))
        ax.axhline(0, color="#64748b", lw=1)
        _stile(ax, t, y); ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def grafico_sensibilita(sens: dict, out: Path):
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    partenze = list(sens)
    for p in PORTAFOGLI:
        ax.plot(partenze, [sens[d][p] * 100 for d in partenze], marker="o",
                lw=2.2, color=COLORI[p], label=p)
    _stile(ax, "Quanto conta da dove si comincia (MSCI World + oro, in euro)",
           "CAGR fino a giugno 2026 (%)", "primo mese del periodo")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def main():
    dati = universi()
    ris = {n: riepilogo(a, o) for n, (a, o) in dati.items()}
    sens = sensibilita()

    grafico_ventagli(dati, OUT / "06_eur_ventagli_10y.png")
    grafico_costo_protezione(ris, OUT / "07_eur_costo_protezione.png")
    grafico_sensibilita(sens, OUT / "08_eur_sensibilita.png")

    with open(OUT / "summary_eur.json", "w", encoding="utf-8") as f:
        json.dump({"universi": ris, "sensibilita_partenza": sens,
                   "passo_mesi": PASSO, "finestre": FINESTRE}, f,
                  indent=2, ensure_ascii=False)

    for nome, r in ris.items():
        print(f"\n=== {nome} + oro, in euro  {r['da']}..{r['a']}  ({r['mesi']} mesi)")
        print(f"    correlazione mensile azionario-oro: {r['correlazione']:+.4f}")
        for p, v in r["portafogli"].items():
            riga = f"    {p:6s} CAGR {v['cagr']*100:6.2f}%  MDD {v['mdd']*100:7.2f}%"
            for et, f_ in v["finestre"].items():
                riga += (f" | {et} p5 {f_['p5']*100:6.2f}% med {f_['p50']*100:6.2f}%"
                         f" neg {f_['quota_negative']*100:4.1f}%")
            print(riga)
    print("\n=== sensibilita' alla partenza (MSCI World + oro, EUR)")
    for d, v in sens.items():
        print("    da " + d + "  " + "  ".join(
            f"{p} {v[p]*100:5.2f}%" for p in PORTAFOGLI) + f"  ({v['mesi']} mesi)")
    print(f"\ngrafici e summary_eur.json in {OUT}")


if __name__ == "__main__":
    main()
