"""
SmartMoneyLab — Decumulo, FIRE e Safe Withdrawal Rate
======================================================

Test della Safe Withdrawal Rate (SWR) sul S&P 500 Total Return reale (1871-2025),
con due metodologie complementari:
  1. Rolling windows storici — Bengen/Trinity Study classico
  2. Block bootstrap a 2 anni — stress test su sequenze ipotetiche, 10.000 traiettorie

Per ogni combinazione di:
  - Orizzonte di decumulo: 20, 30, 40 anni
  - Tasso di prelievo: 2.5%, 3.0%, 3.5%, 4.0%, 4.5%, 5.0%

calcola:
  - Success rate A: capitale > 0 fino all'orizzonte (sopravvivenza)
  - Success rate B: capitale finale ≥ 50% del capitale iniziale REALE (eredità)
  - Capitale finale mediano (in % del capitale iniziale, reale)
  - Anni medi di sopravvivenza nei fallimenti

Plus: tabella del capitale necessario per FIRE rivalutato all'inflazione,
con sensitivity inflazione = 2% (target BCE) e 3% (più conservativo).

Assunzioni:
  - Spesa target 30.000 €/anno (oggi, valore reale)
  - Prelievo rivalutato all'inflazione storica anno per anno
    (modello lavora interamente in EUR REALI per eliminare la variabilita'
    dell'inflazione futura)
  - Asset sottostante: S&P 500 Total Return ricostruito dal dataset Shiller
    (P + D/12 per ogni mese, deflazionato per CPI Shiller)
  - Nessun costo, nessuna tassazione (lordo come baseline SMLab)
  - Modello discreto annuale (Bengen-style): prelievo a inizio anno,
    capitale residuo rende per i restanti 12 mesi.

Dati richiesti in data/cache/:
  - shiller_mirror.csv (SP500, Dividend, Consumer Price Index dal 1871)

Output in public/charts/decumulo-fire-swr/:
  - 01_heatmap_success_rate_A.png       (sopravvivenza capitale > 0)
  - 02_heatmap_success_rate_B.png       (eredita ≥ 50% reale)
  - 03_capitale_necessario_fire.png     (capitale per FIRE per anno di delay)
  - 04_fan_chart_decumulo_4pct_30y.png  (caso "tipo": 4% / 30 anni)
  - 05_wall_of_failure.png              (anni storici peggiori di start)
  - 06_distribuzione_capitale_finale.png (boxplot terminal balance)
  - 07_confronto_bootstrap_vs_storico.png
  - summary.json
  - rolling_results.csv
  - bootstrap_results.csv

Dipendenze: pandas, numpy, matplotlib.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

SLUG = "decumulo-fire-swr"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------- #
# Parametri                                                            #
# -------------------------------------------------------------------- #
BASE_ANNUAL_SPEND = 30_000.0
LIFE_EXPECTANCY = 80
FIRE_DELAY_YEARS = [0, 10, 20, 25, 30]
INFLATION_SCENARIOS = {"base 2%": 0.02, "alta 3%": 0.03}

WITHDRAWAL_RATES = [0.025, 0.030, 0.035, 0.040, 0.045, 0.050]
HORIZONS_YEARS = [20, 30, 40]

N_BOOTSTRAP_PATHS = 10_000
BLOCK_SIZE_YEARS = 2
SUCCESS_THRESHOLD_PCT = 0.50  # caso B: capitale finale >= 50% iniziale (reale)
SEED = 42

# Fiscalita' italiana — Approccio A (stima statica)
TAX_RATE = 0.26              # capital gain ETF UCITS armonizzati
BOLLO_ANNUO = 0.002          # imposta di bollo 0.2% sul controvalore
# Quota di plusvalenza nel capitale al momento del decumulo, in funzione
# degli anni di accumulo (PAC). Piu' lungo il PAC, piu' bassa la quota
# del prezzo di carico medio, piu' alta la quota plusvalenza.
CAPITAL_GAIN_PCT_BY_DELAY = {0: 0.50, 10: 0.55, 20: 0.65, 25: 0.70, 30: 0.75}

# Palette
COLOR_PORT = "#1e3a8a"
COLOR_ACCENT = "#d97706"
COLOR_GOOD = "#059669"
COLOR_BAD = "#dc2626"
COLOR_NEUTRAL = "#6b7280"


# -------------------------------------------------------------------- #
# Caricamento dati                                                     #
# -------------------------------------------------------------------- #
def load_sp500_real_returns_annual() -> pd.Series:
    """
    Carica Shiller monthly e costruisce la serie dei rendimenti annuali
    REALI del S&P 500 Total Return.

    Logica:
      - r_nom_mensile = (P_t + D_{t-1}/12) / P_{t-1} - 1
      - r_inflazione_mensile = CPI_t / CPI_{t-1} - 1
      - r_real_mensile = (1+r_nom) / (1+infl) - 1
      - r_real_annuale = prod(1+r_real_mensile su 12 mesi) - 1

    Restituisce una Series indicizzata per anno calendario.
    """
    path = CACHE_DIR / "shiller_mirror.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["Date"]).dt.to_period("M").dt.to_timestamp()
    df = df.set_index("date").sort_index()
    P = pd.to_numeric(df["SP500"], errors="coerce")
    D = pd.to_numeric(df["Dividend"], errors="coerce")  # dividendo annualizzato
    CPI = pd.to_numeric(df["Consumer Price Index"], errors="coerce")
    panel = pd.DataFrame({"P": P, "D": D, "CPI": CPI}).dropna()
    # FIX: il mirror Shiller usa 0.0 come sentinella di "dato mancante"
    # da meta' 2023 in poi (Dividend e CPI = 0). Filtro per evitare
    # divisioni per zero che generano Infinity nei rendimenti reali.
    panel = panel[(panel["D"] > 0) & (panel["CPI"] > 0)]

    # Rendimento nominale mensile TR
    r_nom = (panel["P"] + panel["D"].shift(1) / 12.0) / panel["P"].shift(1) - 1
    # Inflazione mensile
    infl_m = panel["CPI"] / panel["CPI"].shift(1) - 1
    # Reale
    r_real = (1 + r_nom) / (1 + infl_m) - 1
    r_real = r_real.dropna()

    # Annualizza: prodotto dei (1+r) mensili per ogni anno calendario.
    # Tengo solo anni con 12 mesi pieni di dati validi.
    months_per_year = r_real.groupby(r_real.index.year).size()
    full_years = months_per_year[months_per_year == 12].index
    annual = (1 + r_real).groupby(r_real.index.year).prod() - 1
    annual = annual.loc[annual.index.intersection(full_years)]
    annual = annual.replace([np.inf, -np.inf], np.nan).dropna()
    annual.name = "sp500_real_return"
    return annual


# -------------------------------------------------------------------- #
# Simulazione del decumulo                                             #
# -------------------------------------------------------------------- #
def simulate_decumulo(initial_capital: float, withdrawal_rate: float,
                       real_returns: np.ndarray, horizon: int) -> np.ndarray:
    """
    Simula il decumulo discreto annuale (modello Bengen).

    Convenzione:
      anno 1: prelevo W = withdrawal_rate * initial_capital all'inizio.
              Capitale residuo (C - W) rende r_real_1 per il resto dell'anno.
      anno t (t>1): prelevo W reale costante (cioe' lo stesso valore W in
              euro reali ogni anno; nel modello in reali e' davvero costante).
              Capitale residuo rende r_real_t.

    Restituisce array (horizon+1,) con il capitale a fine di ogni anno
    (indice 0 = capitale iniziale prima del primo prelievo).
    Se in qualche anno il capitale scende sotto 0, viene clippato a 0
    e ci resta.
    """
    W = withdrawal_rate * initial_capital  # prelievo annuo costante in reali
    nav = np.empty(horizon + 1)
    nav[0] = initial_capital
    capital = initial_capital
    for t in range(horizon):
        # Prelievo a inizio anno
        capital = capital - W
        if capital <= 0:
            capital = 0.0
        else:
            # Rendimento reale sul residuo
            r = real_returns[t]
            capital = capital * (1 + r)
        nav[t + 1] = capital
    return nav


def evaluate_paths(paths: np.ndarray, initial_capital: float) -> dict:
    """Calcola metriche aggregate su una matrice (n_paths, horizon+1)."""
    final = paths[:, -1]
    survived_a = (paths > 0).all(axis=1)
    survived_b = (final >= SUCCESS_THRESHOLD_PCT * initial_capital) & survived_a
    failure_years = np.array([
        np.argmax(p <= 0) if (p <= 0).any() else len(p)
        for p in paths
    ]) - 1  # primo anno di esaurimento (-1 = sopravvissuto fino in fondo)
    return {
        "success_rate_A": float(survived_a.mean()),
        "success_rate_B": float(survived_b.mean()),
        "median_terminal_pct": float(np.median(final) / initial_capital),
        "p5_terminal_pct": float(np.percentile(final, 5) / initial_capital),
        "p95_terminal_pct": float(np.percentile(final, 95) / initial_capital),
        "mean_failure_year": (
            float(failure_years[~survived_a].mean()) if (~survived_a).any() else None
        ),
    }


# -------------------------------------------------------------------- #
# Rolling windows storici                                              #
# -------------------------------------------------------------------- #
def rolling_windows_decumulo(real_returns: pd.Series, withdrawal_rate: float,
                              horizon: int, initial_capital: float = 1.0
                              ) -> tuple[np.ndarray, list[int]]:
    """
    Per ogni anno di partenza storico, simula il decumulo a `withdrawal_rate`
    su `horizon` anni. Restituisce (paths, start_years).
    """
    years = real_returns.index.values
    returns = real_returns.values
    paths = []
    start_years = []
    for i in range(len(returns) - horizon + 1):
        sub = returns[i:i + horizon]
        nav = simulate_decumulo(initial_capital, withdrawal_rate, sub, horizon)
        paths.append(nav)
        start_years.append(int(years[i]))
    return np.array(paths), start_years


# -------------------------------------------------------------------- #
# Block bootstrap                                                      #
# -------------------------------------------------------------------- #
def block_bootstrap_decumulo(real_returns: pd.Series, withdrawal_rate: float,
                              horizon: int, n_paths: int, block: int,
                              rng: np.random.Generator,
                              initial_capital: float = 1.0) -> np.ndarray:
    """
    Block bootstrap dei rendimenti annuali. Per ogni traiettoria, genera
    una sequenza di `horizon` anni campionando blocchi contigui dai
    rendimenti storici, poi simula il decumulo.
    """
    returns = real_returns.values
    n_source = len(returns)
    paths = np.empty((n_paths, horizon + 1))
    n_blocks_needed = int(np.ceil(horizon / block))
    for p in range(n_paths):
        starts = rng.integers(0, n_source - block + 1, size=n_blocks_needed)
        sample = np.concatenate([returns[s:s + block] for s in starts])[:horizon]
        paths[p] = simulate_decumulo(initial_capital, withdrawal_rate, sample, horizon)
    return paths


# -------------------------------------------------------------------- #
# Capitale necessario per FIRE                                         #
# -------------------------------------------------------------------- #
def capital_for_fire(spend_today: float, years_delay: int,
                      withdrawal_rate: float, inflation: float) -> float:
    """Capitale necessario al FIRE = spesa_target_futura / withdrawal_rate."""
    spend_future = spend_today * ((1 + inflation) ** years_delay)
    return spend_future / withdrawal_rate


# -------------------------------------------------------------------- #
# Fiscalita' Italia — Approccio A                                      #
# -------------------------------------------------------------------- #
def effective_gross_wr(net_wr: float, tax_rate: float, cg_pct: float) -> float:
    """
    Tasso di prelievo LORDO necessario per ottenere un dato tasso NETTO
    Italia, data la quota di plusvalenza presente nel capitale.

    Per portare a casa W € netti devi vendere W / (1 - tax × cg_pct) € lordi,
    perche' tax × cg_pct è la frazione della vendita che lo Stato preleva.
    """
    return net_wr / (1.0 - tax_rate * cg_pct)


def apply_bollo_to_returns(real_returns: pd.Series, bollo: float) -> pd.Series:
    """
    Applica il drag del bollo annuale ai rendimenti reali. Modello:
      r_net_bollo = (1 + r_real) * (1 - bollo) - 1
    Approssimazione standard di un'imposta sul controvalore a fine anno.
    """
    out = (1 + real_returns) * (1 - bollo) - 1
    out.name = f"{real_returns.name}_post_bollo"
    return out


def cg_pct_for_delay(delay: int) -> float:
    """Lookup nella tabella; interpola se delay non e' una chiave esatta."""
    if delay in CAPITAL_GAIN_PCT_BY_DELAY:
        return CAPITAL_GAIN_PCT_BY_DELAY[delay]
    # interpolazione lineare fra chiavi adiacenti
    keys = sorted(CAPITAL_GAIN_PCT_BY_DELAY)
    if delay < keys[0]:
        return CAPITAL_GAIN_PCT_BY_DELAY[keys[0]]
    if delay > keys[-1]:
        return CAPITAL_GAIN_PCT_BY_DELAY[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= delay <= keys[i + 1]:
            frac = (delay - keys[i]) / (keys[i + 1] - keys[i])
            return (CAPITAL_GAIN_PCT_BY_DELAY[keys[i]] * (1 - frac)
                     + CAPITAL_GAIN_PCT_BY_DELAY[keys[i + 1]] * frac)
    return 0.65  # fallback


# -------------------------------------------------------------------- #
# Plot                                                                 #
# -------------------------------------------------------------------- #
def _set_style():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200,
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_heatmap(matrix: np.ndarray, withdrawal_rates: list[float],
                  horizons: list[int], title: str, out_path: Path,
                  vmin: float = 0.0, vmax: float = 1.0, fmt: str = ".0%"):
    """Heatmap success rate per (withdrawal_rate, horizon)."""
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    cmap = LinearSegmentedColormap.from_list(
        "swr", ["#dc2626", "#facc15", "#059669"], N=256)
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax,
                    origin="lower")
    ax.set_xticks(range(len(horizons)))
    ax.set_xticklabels([f"{h} anni" for h in horizons])
    ax.set_yticks(range(len(withdrawal_rates)))
    ax.set_yticklabels([f"{w*100:.1f}%" for w in withdrawal_rates])
    ax.set_xlabel("Orizzonte di decumulo")
    ax.set_ylabel("Tasso di prelievo")
    for i in range(len(withdrawal_rates)):
        for j in range(len(horizons)):
            val = matrix[i, j]
            color = "white" if val < 0.5 else "black"
            ax.text(j, i, format(val, fmt), ha="center", va="center",
                     color=color, fontsize=12, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("Success rate")
    ax.set_title(title)
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_capital_for_fire(out_path: Path):
    """Capitale necessario al FIRE per anno di delay × tasso di prelievo
    × scenario inflazione."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for ax, (label, infl) in zip(axes, INFLATION_SCENARIOS.items()):
        for wr in [0.025, 0.035, 0.040, 0.050]:
            vals = [capital_for_fire(BASE_ANNUAL_SPEND, d, wr, infl)
                    for d in FIRE_DELAY_YEARS]
            ax.plot(FIRE_DELAY_YEARS, vals, "-o", lw=2.0, ms=8,
                    label=f"Prelievo {wr*100:.1f}%")
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"€{v/1000:.0f}k"
                              if v < 1_000_000 else f"€{v/1_000_000:.1f}M"))
        ax.set_xlabel("Anni di delay al FIRE")
        ax.set_title(f"Inflazione {label}")
        ax.legend(loc="upper left", frameon=False)
    axes[0].set_ylabel("Capitale necessario (€ nominali)")
    fig.suptitle("Capitale necessario al FIRE — Spesa target 30.000 €/anno (oggi)")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_fan_chart_decumulo(paths: np.ndarray, withdrawal_rate: float,
                              horizon: int, out_path: Path):
    """Fan chart del capitale residuo (% del capitale iniziale)."""
    years = np.arange(horizon + 1)
    pct_curves = paths / paths[:, 0:1]  # normalizza a 1
    p5 = np.percentile(pct_curves, 5, axis=0)
    p25 = np.percentile(pct_curves, 25, axis=0)
    p50 = np.percentile(pct_curves, 50, axis=0)
    p75 = np.percentile(pct_curves, 75, axis=0)
    p95 = np.percentile(pct_curves, 95, axis=0)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.fill_between(years, p5, p95, color=COLOR_PORT, alpha=0.15,
                    label="p5–p95")
    ax.fill_between(years, p25, p75, color=COLOR_PORT, alpha=0.30,
                    label="p25–p75")
    ax.plot(years, p50, color=COLOR_PORT, lw=2.4, label="Mediana")
    ax.axhline(1.0, color="black", lw=0.7, ls=":", alpha=0.6)
    ax.axhline(SUCCESS_THRESHOLD_PCT, color=COLOR_BAD, lw=0.9, ls="--",
                label=f"Soglia eredità ({SUCCESS_THRESHOLD_PCT*100:.0f}%)")
    ax.axhline(0, color=COLOR_BAD, lw=1.2, alpha=0.8)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
    ax.set_xlabel("Anni di decumulo")
    ax.set_ylabel("Capitale residuo (% del capitale iniziale, reale)")
    ax.set_title(
        f"Fan chart decumulo — prelievo {withdrawal_rate*100:.1f}%, "
        f"orizzonte {horizon} anni\n"
        f"Block bootstrap S&P 500 reale, 10.000 traiettorie")
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_wall_of_failure(real_returns: pd.Series, out_path: Path):
    """Le sequenze storiche peggiori per il decumulo al 4% / 30 anni.
    Mostra l'equity curve di ogni "start year" colorando di rosso quelli
    falliti e di verde quelli sopravvissuti."""
    paths, start_years = rolling_windows_decumulo(
        real_returns, 0.04, 30, initial_capital=1.0)
    survived = (paths > 0).all(axis=1)
    years = np.arange(31)
    fig, ax = plt.subplots(figsize=(11, 6))
    # Tracciare prima i sopravvissuti (verde tenue)
    for i in np.where(survived)[0]:
        ax.plot(years, paths[i], color=COLOR_GOOD, lw=0.6, alpha=0.25)
    # Sopra, i falliti in rosso
    for i in np.where(~survived)[0]:
        ax.plot(years, paths[i], color=COLOR_BAD, lw=1.4, alpha=0.85,
                label=f"Start {start_years[i]}")
    ax.axhline(1.0, color="black", lw=0.7, ls=":", alpha=0.6)
    ax.axhline(0, color="black", lw=0.8)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
    ax.set_xlabel("Anni di decumulo")
    ax.set_ylabel("Capitale residuo (% del capitale iniziale, reale)")
    n_failed = (~survived).sum()
    n_total = len(survived)
    ax.set_title(
        f"Wall of failure — prelievo 4%, orizzonte 30 anni\n"
        f"{n_failed}/{n_total} finestre storiche fallite "
        f"({n_failed/n_total*100:.0f}%)")
    if n_failed > 0:
        ax.legend(loc="upper right", frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_distribuzione_capitale_finale(results_boot: dict, out_path: Path):
    """Boxplot capitale finale (% del capitale iniziale) per (withdrawal, horizon)."""
    fig, ax = plt.subplots(figsize=(12, 6))
    data = []
    labels = []
    for h in HORIZONS_YEARS:
        for w in WITHDRAWAL_RATES:
            key = (w, h)
            paths = results_boot[key]["paths"]
            final = paths[:, -1] / paths[:, 0]
            data.append(np.clip(final, 0, None))
            labels.append(f"{w*100:.1f}%\n{h}y")
    bp = ax.boxplot(data, patch_artist=True, showfliers=False, whis=(5, 95))
    palette = [COLOR_PORT, COLOR_PORT, COLOR_ACCENT, COLOR_ACCENT,
               COLOR_BAD, COLOR_BAD] * len(HORIZONS_YEARS)
    for box, c in zip(bp["boxes"], palette):
        box.set(facecolor=c, alpha=0.55)
    ax.axhline(1.0, color="black", lw=0.7, ls=":", alpha=0.6)
    ax.axhline(SUCCESS_THRESHOLD_PCT, color=COLOR_BAD, lw=0.9, ls="--",
               label=f"Soglia eredità {SUCCESS_THRESHOLD_PCT*100:.0f}%")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Capitale finale (% del capitale iniziale, reale)")
    ax.set_title("Distribuzione del capitale finale — block bootstrap")
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_lordo_vs_netto_italia(matrix_boot_A: np.ndarray,
                                 results_boot_net: dict,
                                 withdrawal_rates: list[float],
                                 fire_delay: int, horizon: int,
                                 out_path: Path):
    """
    Confronto LORDO (modello base) vs NETTO Italia per un dato delay FIRE
    e un dato orizzonte di decumulo. Doppia barra per ciascun tasso di
    prelievo, con i valori success rate sopra.
    """
    cg_pct = cg_pct_for_delay(fire_delay)
    h_idx = HORIZONS_YEARS.index(horizon)
    lordo = matrix_boot_A[:, h_idx] * 100
    netto = np.array([
        results_boot_net[(fire_delay, wr, horizon)]["success_rate_A"]
        for wr in withdrawal_rates
    ]) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(withdrawal_rates))
    width = 0.35
    ax.bar(x - width / 2, lordo, width, color=COLOR_PORT, alpha=0.85,
           label="LORDO (modello base, no tasse)")
    ax.bar(x + width / 2, netto, width, color=COLOR_ACCENT, alpha=0.85,
           label=f"NETTO Italia (26% cg su {cg_pct*100:.0f}% + bollo 0,2%/y)")
    for k in range(len(withdrawal_rates)):
        ax.text(x[k] - width / 2, lordo[k] + 1, f"{lordo[k]:.0f}%",
                ha="center", fontsize=10, color=COLOR_PORT, fontweight="bold")
        ax.text(x[k] + width / 2, netto[k] + 1, f"{netto[k]:.0f}%",
                ha="center", fontsize=10, color=COLOR_ACCENT, fontweight="bold")
        # Delta
        delta = netto[k] - lordo[k]
        ax.text(x[k], min(lordo[k], netto[k]) - 5, f"{delta:+.0f}pp",
                ha="center", fontsize=9, color=COLOR_BAD if delta < 0 else COLOR_GOOD)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{w*100:.1f}%" for w in withdrawal_rates])
    ax.set_xlabel("Tasso di prelievo NETTO (cioe' € reali in mano)")
    ax.set_ylabel("Success rate — capitale > 0 (%)")
    ax.set_ylim(0, 115)
    ax.set_title(
        f"Lordo vs Netto Italia — FIRE +{fire_delay} anni di PAC, "
        f"orizzonte decumulo {horizon} anni\n"
        f"Quota plusvalenza ipotizzata: {cg_pct*100:.0f}%")
    ax.legend(loc="lower left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_capitale_vs_success_rate(matrix_boot_A: np.ndarray,
                                    withdrawal_rates: list[float],
                                    horizons: list[int],
                                    out_path: Path):
    """
    Il grafico chiave dell'articolo: quanto capitale serve per andare in FIRE
    OGGI a 30k €/anno di spesa, con il success rate associato per ciascun
    tasso di prelievo e ciascun orizzonte di decumulo.

    Asse X = capitale richiesto (€), asse Y = success rate %.
    Tre linee, una per ciascun orizzonte (20/30/40 anni).
    Annoto ciascun punto col tasso di prelievo corrispondente.
    """
    fig, ax = plt.subplots(figsize=(11.5, 6))
    colors = [COLOR_GOOD, COLOR_PORT, COLOR_BAD]
    markers = ["o", "s", "D"]
    for k, h in enumerate(horizons):
        caps = [BASE_ANNUAL_SPEND / w for w in withdrawal_rates]
        srs = matrix_boot_A[:, k] * 100
        ax.plot(caps, srs, "-", color=colors[k], lw=2.5,
                marker=markers[k], ms=11, mec="white", mew=1.5,
                label=f"Orizzonte {h} anni")
        for w, c, s in zip(withdrawal_rates, caps, srs):
            ax.annotate(f"{w*100:.1f}%", (c, s),
                         xytext=(8, 8), textcoords="offset points",
                         fontsize=9, color=colors[k], fontweight="bold")

    ax.axhline(95, color=COLOR_GOOD, lw=0.8, ls=":", alpha=0.6)
    ax.text(ax.get_xlim()[1] * 0.98, 95.3, "95% success rate",
            ha="right", fontsize=9, color=COLOR_GOOD)
    ax.axhline(90, color=COLOR_ACCENT, lw=0.8, ls=":", alpha=0.6)
    ax.text(ax.get_xlim()[1] * 0.98, 90.3, "90% success rate",
            ha="right", fontsize=9, color=COLOR_ACCENT)
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"€{v/1000:.0f}k"
                          if v < 1_000_000 else f"€{v/1_000_000:.1f}M"))
    ax.set_xlabel(f"Capitale necessario al FIRE (per spesa {BASE_ANNUAL_SPEND:,.0f} €/anno OGGI)")
    ax.set_ylabel("Success rate — capitale > 0 (%)")
    ax.set_title(
        "Quanto capitale serve per andare in FIRE oggi?\n"
        "Trade-off capitale richiesto vs probabilità di sopravvivenza")
    ax.legend(loc="lower right", frameon=False)
    ax.set_ylim(70, 105)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_confronto_bootstrap_vs_storico(matrix_boot: np.ndarray,
                                         matrix_rolling: np.ndarray,
                                         withdrawal_rates: list[float],
                                         horizons: list[int],
                                         out_path: Path):
    """Confronto visuale tra success rate A (bootstrap vs rolling storici)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    x = np.arange(len(withdrawal_rates))
    width = 0.35
    for ax, h, j in zip(axes, horizons, range(len(horizons))):
        boot = matrix_boot[:, j]
        roll = matrix_rolling[:, j]
        ax.bar(x - width / 2, boot * 100, width, color=COLOR_PORT,
               alpha=0.85, label="Block bootstrap")
        ax.bar(x + width / 2, roll * 100, width, color=COLOR_ACCENT,
               alpha=0.85, label="Rolling storici")
        for k, (b, r) in enumerate(zip(boot, roll)):
            ax.text(k - width / 2, b * 100 + 1, f"{b*100:.0f}%",
                    ha="center", fontsize=9)
            ax.text(k + width / 2, r * 100 + 1, f"{r*100:.0f}%",
                    ha="center", fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{w*100:.1f}%" for w in withdrawal_rates])
        ax.set_title(f"Orizzonte {h} anni")
        ax.set_xlabel("Tasso di prelievo")
        ax.set_ylim(0, 115)
        ax.legend(loc="lower left", frameon=False)
    axes[0].set_ylabel("Success rate A — capitale > 0 (%)")
    fig.suptitle("Block bootstrap vs Rolling storici — coerenza delle metodologie")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path)
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #
def main():
    _set_style()
    print(f"\n=== {SLUG} ===\n")

    print("[1/5] Caricamento rendimenti reali S&P 500 dal dataset Shiller...")
    real_returns = load_sp500_real_returns_annual()
    print(f"      {len(real_returns)} anni di dati: "
          f"{real_returns.index[0]} -> {real_returns.index[-1]}")
    print(f"      Rendimento reale medio annuo: {real_returns.mean()*100:.2f}%")
    print(f"      Vol annua: {real_returns.std()*100:.2f}%")
    print(f"      Peggior anno: {real_returns.min()*100:.1f}% "
          f"({real_returns.idxmin()})")
    print(f"      Miglior anno: {real_returns.max()*100:.1f}% "
          f"({real_returns.idxmax()})")

    print("\n[2/5] Rolling windows storici...")
    rng = np.random.default_rng(SEED)
    results_rolling = {}
    matrix_rolling_A = np.zeros((len(WITHDRAWAL_RATES), len(HORIZONS_YEARS)))
    matrix_rolling_B = np.zeros((len(WITHDRAWAL_RATES), len(HORIZONS_YEARS)))
    for i, wr in enumerate(WITHDRAWAL_RATES):
        for j, h in enumerate(HORIZONS_YEARS):
            paths, starts = rolling_windows_decumulo(real_returns, wr, h,
                                                      initial_capital=1.0)
            metrics = evaluate_paths(paths, initial_capital=1.0)
            results_rolling[(wr, h)] = {
                "paths": paths, "start_years": starts, **metrics
            }
            matrix_rolling_A[i, j] = metrics["success_rate_A"]
            matrix_rolling_B[i, j] = metrics["success_rate_B"]
            print(f"      WR {wr*100:4.1f}% / {h:2d}y: "
                  f"{len(paths)} finestre, "
                  f"survA {metrics['success_rate_A']*100:5.1f}%, "
                  f"survB {metrics['success_rate_B']*100:5.1f}%, "
                  f"mediana finale {metrics['median_terminal_pct']*100:6.1f}%")

    print("\n[3/5] Block bootstrap (10.000 traiettorie ciascuna combo)...")
    results_boot = {}
    matrix_boot_A = np.zeros((len(WITHDRAWAL_RATES), len(HORIZONS_YEARS)))
    matrix_boot_B = np.zeros((len(WITHDRAWAL_RATES), len(HORIZONS_YEARS)))
    for i, wr in enumerate(WITHDRAWAL_RATES):
        for j, h in enumerate(HORIZONS_YEARS):
            paths = block_bootstrap_decumulo(real_returns, wr, h,
                                              N_BOOTSTRAP_PATHS,
                                              BLOCK_SIZE_YEARS, rng,
                                              initial_capital=1.0)
            metrics = evaluate_paths(paths, initial_capital=1.0)
            results_boot[(wr, h)] = {"paths": paths, **metrics}
            matrix_boot_A[i, j] = metrics["success_rate_A"]
            matrix_boot_B[i, j] = metrics["success_rate_B"]
            print(f"      WR {wr*100:4.1f}% / {h:2d}y: "
                  f"survA {metrics['success_rate_A']*100:5.1f}%, "
                  f"survB {metrics['success_rate_B']*100:5.1f}%, "
                  f"mediana finale {metrics['median_terminal_pct']*100:6.1f}%, "
                  f"p5 {metrics['p5_terminal_pct']*100:6.1f}%")

    # ---------------------------------------------------------------- #
    # FISCALITA' ITALIA — Approccio A                                  #
    # ---------------------------------------------------------------- #
    print("\n[3b/5] Bootstrap NETTO Italia (26% cg + bollo 0.2%/anno)...")
    # Applico drag del bollo ai rendimenti reali
    real_returns_net = apply_bollo_to_returns(real_returns, BOLLO_ANNUO)
    # Per ogni delay FIRE, calcolo i success rate ai WR effettivi lordi
    # corrispondenti al WR netto target (= elemento di WITHDRAWAL_RATES)
    results_boot_net_italia = {}
    for delay in FIRE_DELAY_YEARS:
        cg_pct = cg_pct_for_delay(delay)
        for wr_net in WITHDRAWAL_RATES:
            wr_gross = effective_gross_wr(wr_net, TAX_RATE, cg_pct)
            for h in HORIZONS_YEARS:
                paths = block_bootstrap_decumulo(
                    real_returns_net, wr_gross, h,
                    N_BOOTSTRAP_PATHS, BLOCK_SIZE_YEARS, rng,
                    initial_capital=1.0)
                metrics = evaluate_paths(paths, initial_capital=1.0)
                results_boot_net_italia[(delay, wr_net, h)] = {
                    "cg_pct": cg_pct,
                    "wr_net": wr_net,
                    "wr_gross_effective": wr_gross,
                    **metrics,
                }
        print(f"      delay {delay:2d}y (cg {cg_pct*100:.0f}%): "
              f"calcolati {len(WITHDRAWAL_RATES)*len(HORIZONS_YEARS)} scenari")

    print("\n[4/5] Plot...")
    plot_heatmap(matrix_boot_A, WITHDRAWAL_RATES, HORIZONS_YEARS,
                  "Success rate A — capitale > 0 (block bootstrap S&P 500 reale)",
                  OUT_DIR / "01_heatmap_success_rate_A.png")
    plot_heatmap(matrix_boot_B, WITHDRAWAL_RATES, HORIZONS_YEARS,
                  "Success rate B — eredità ≥ 50% reale (block bootstrap)",
                  OUT_DIR / "02_heatmap_success_rate_B.png")
    plot_capital_for_fire(OUT_DIR / "03_capitale_necessario_fire.png")
    plot_fan_chart_decumulo(results_boot[(0.04, 30)]["paths"], 0.04, 30,
                              OUT_DIR / "04_fan_chart_decumulo_4pct_30y.png")
    plot_wall_of_failure(real_returns, OUT_DIR / "05_wall_of_failure.png")
    plot_distribuzione_capitale_finale(results_boot,
                                        OUT_DIR / "06_distribuzione_capitale_finale.png")
    plot_confronto_bootstrap_vs_storico(matrix_boot_A, matrix_rolling_A,
                                          WITHDRAWAL_RATES, HORIZONS_YEARS,
                                          OUT_DIR / "07_confronto_bootstrap_vs_storico.png")
    plot_capitale_vs_success_rate(matrix_boot_A, WITHDRAWAL_RATES, HORIZONS_YEARS,
                                    OUT_DIR / "08_capitale_vs_success_rate.png")
    # Plot fiscalita' Italia per i due scenari piu' significativi:
    # FIRE oggi (delay=0, cg=50%) e FIRE +20y dopo PAC ventennale (cg=65%)
    plot_lordo_vs_netto_italia(matrix_boot_A, results_boot_net_italia,
                                 WITHDRAWAL_RATES, fire_delay=0, horizon=30,
                                 out_path=OUT_DIR / "09_lordo_vs_netto_fire_oggi.png")
    plot_lordo_vs_netto_italia(matrix_boot_A, results_boot_net_italia,
                                 WITHDRAWAL_RATES, fire_delay=20, horizon=30,
                                 out_path=OUT_DIR / "10_lordo_vs_netto_fire_dopo_20y_pac.png")

    print("\n[5/5] CSV e JSON...")
    # CSV rolling
    rolling_rows = []
    for (wr, h), v in results_rolling.items():
        rolling_rows.append({
            "withdrawal_rate": wr, "horizon": h,
            "n_windows": len(v["paths"]),
            "success_rate_A": v["success_rate_A"],
            "success_rate_B": v["success_rate_B"],
            "median_terminal_pct": v["median_terminal_pct"],
            "p5_terminal_pct": v["p5_terminal_pct"],
            "p95_terminal_pct": v["p95_terminal_pct"],
        })
    pd.DataFrame(rolling_rows).to_csv(OUT_DIR / "rolling_results.csv", index=False)
    # CSV bootstrap
    boot_rows = []
    for (wr, h), v in results_boot.items():
        boot_rows.append({
            "withdrawal_rate": wr, "horizon": h,
            "n_paths": N_BOOTSTRAP_PATHS,
            "success_rate_A": v["success_rate_A"],
            "success_rate_B": v["success_rate_B"],
            "median_terminal_pct": v["median_terminal_pct"],
            "p5_terminal_pct": v["p5_terminal_pct"],
            "p95_terminal_pct": v["p95_terminal_pct"],
        })
    pd.DataFrame(boot_rows).to_csv(OUT_DIR / "bootstrap_results.csv", index=False)

    # Capitale FIRE come tabella
    fire_table = []
    for label, infl in INFLATION_SCENARIOS.items():
        for wr in WITHDRAWAL_RATES:
            for d in FIRE_DELAY_YEARS:
                fire_table.append({
                    "inflation_scenario": label,
                    "withdrawal_rate": wr,
                    "years_to_fire": d,
                    "spend_today": BASE_ANNUAL_SPEND,
                    "spend_at_fire_nominal": BASE_ANNUAL_SPEND * ((1+infl)**d),
                    "capital_required_at_fire": capital_for_fire(
                        BASE_ANNUAL_SPEND, d, wr, infl),
                })
    pd.DataFrame(fire_table).to_csv(OUT_DIR / "capital_required_fire.csv", index=False)

    # CSV per il reel animato: traiettorie mediane del bootstrap per tre
    # tassi di prelievo (3%, 3.5%, 4%) sui 30 anni di decumulo.
    # Capitale iniziale 1.000.000 €, prelievo netto Italia (cg 50%).
    # Il reel mostrera' "capitale residuo nel tempo" anno per anno.
    reel_years = np.arange(31)
    reel_data = {"anno": reel_years}
    for wr in [0.03, 0.035, 0.04]:
        # Uso il bootstrap LORDO base x 30 anni
        paths = results_boot[(wr, 30)]["paths"] * 1_000_000  # scala a 1M €
        median = np.median(paths, axis=0)
        reel_data[f"prelievo_{int(wr*1000)/10}pct"] = median
    pd.DataFrame(reel_data).to_csv(OUT_DIR / "equity_curves_for_reel.csv",
                                     index=False)

    summary = {
        "slug": SLUG,
        "parametri": {
            "spesa_target_oggi": BASE_ANNUAL_SPEND,
            "withdrawal_rates": WITHDRAWAL_RATES,
            "horizons_anni": HORIZONS_YEARS,
            "fire_delay_anni": FIRE_DELAY_YEARS,
            "inflazione_scenari": INFLATION_SCENARIOS,
            "n_bootstrap_paths": N_BOOTSTRAP_PATHS,
            "block_size_anni": BLOCK_SIZE_YEARS,
            "soglia_eredita_pct": SUCCESS_THRESHOLD_PCT,
            "seed": SEED,
        },
        "storia_input": {
            "primo_anno": int(real_returns.index[0]),
            "ultimo_anno": int(real_returns.index[-1]),
            "n_anni": len(real_returns),
            "rendimento_reale_medio": float(real_returns.mean()),
            "vol_annua": float(real_returns.std()),
            "peggior_anno": {
                "anno": int(real_returns.idxmin()),
                "rendimento": float(real_returns.min()),
            },
            "miglior_anno": {
                "anno": int(real_returns.idxmax()),
                "rendimento": float(real_returns.max()),
            },
        },
        "bootstrap_success_rate_A": {
            f"{w*100:.1f}%": {f"{h}y": float(matrix_boot_A[i, j])
                                for j, h in enumerate(HORIZONS_YEARS)}
            for i, w in enumerate(WITHDRAWAL_RATES)
        },
        "bootstrap_success_rate_B": {
            f"{w*100:.1f}%": {f"{h}y": float(matrix_boot_B[i, j])
                                for j, h in enumerate(HORIZONS_YEARS)}
            for i, w in enumerate(WITHDRAWAL_RATES)
        },
        "rolling_success_rate_A": {
            f"{w*100:.1f}%": {f"{h}y": float(matrix_rolling_A[i, j])
                                for j, h in enumerate(HORIZONS_YEARS)}
            for i, w in enumerate(WITHDRAWAL_RATES)
        },
        "rolling_success_rate_B": {
            f"{w*100:.1f}%": {f"{h}y": float(matrix_rolling_B[i, j])
                                for j, h in enumerate(HORIZONS_YEARS)}
            for i, w in enumerate(WITHDRAWAL_RATES)
        },
        "fiscalita_italia": {
            "approccio": (
                "Approccio A: stima statica della quota plusvalenza. "
                "Il WR netto target è convertito in un WR lordo effettivo via "
                "WR_lordo = WR_netto / (1 - tax × cg_pct). Il bollo 0.2%/anno "
                "è applicato come drag sul rendimento reale."
            ),
            "tax_rate": TAX_RATE,
            "bollo_annuo": BOLLO_ANNUO,
            "quota_plusvalenza_per_delay": {
                f"FIRE_+{d}y": cg_pct_for_delay(d)
                for d in FIRE_DELAY_YEARS
            },
            "success_rate_netto_per_delay": {
                f"FIRE_+{d}y": {
                    f"{w*100:.1f}%_netto": {
                        f"{h}y": float(results_boot_net_italia[(d, w, h)]["success_rate_A"])
                        for h in HORIZONS_YEARS
                    }
                    for w in WITHDRAWAL_RATES
                }
                for d in FIRE_DELAY_YEARS
            },
            "wr_lordo_effettivo_per_delay": {
                f"FIRE_+{d}y": {
                    f"{w*100:.1f}%_netto": effective_gross_wr(
                        w, TAX_RATE, cg_pct_for_delay(d))
                    for w in WITHDRAWAL_RATES
                }
                for d in FIRE_DELAY_YEARS
            },
        },
        "capitale_richiesto_fire": {
            "spesa_oggi_eur": BASE_ANNUAL_SPEND,
            "nota": (
                "Capitale richiesto = spesa target / tasso di prelievo. "
                "Per FIRE OGGI il capitale e' in euro di oggi. "
                "Per FIRE futuri il capitale 'in euro nominali al momento del FIRE' "
                "tiene conto dell'inflazione (target spesa rivalutata)."
            ),
            "fire_oggi_capitale_eur": {
                f"{w*100:.1f}%": {
                    "capitale_eur": BASE_ANNUAL_SPEND / w,
                    "success_rate_20y_A": float(matrix_boot_A[i, 0]),
                    "success_rate_30y_A": float(matrix_boot_A[i, 1]),
                    "success_rate_40y_A": float(matrix_boot_A[i, 2]),
                    "success_rate_20y_B": float(matrix_boot_B[i, 0]),
                    "success_rate_30y_B": float(matrix_boot_B[i, 1]),
                    "success_rate_40y_B": float(matrix_boot_B[i, 2]),
                }
                for i, w in enumerate(WITHDRAWAL_RATES)
            },
            "fire_futuri_capitale_nominale_eur": {
                "inflazione_2pct": {
                    f"{w*100:.1f}%": {
                        f"FIRE_+{d}y": capital_for_fire(
                            BASE_ANNUAL_SPEND, d, w, 0.02)
                        for d in FIRE_DELAY_YEARS
                    }
                    for w in WITHDRAWAL_RATES
                },
                "inflazione_3pct": {
                    f"{w*100:.1f}%": {
                        f"FIRE_+{d}y": capital_for_fire(
                            BASE_ANNUAL_SPEND, d, w, 0.03)
                        for d in FIRE_DELAY_YEARS
                    }
                    for w in WITHDRAWAL_RATES
                },
            },
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print(f"\n      Output in: {OUT_DIR}")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"        - {p.name}")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
