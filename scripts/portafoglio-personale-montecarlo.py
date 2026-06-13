"""
SmartMoneyLab — Portafoglio personale: simulazione Monte Carlo
==============================================================

Bootstrap a blocchi mensili dei rendimenti storici del portafoglio (13 asset)
per stimare la distribuzione del NAV futuro a 10/20/30 anni di orizzonte.

Metodologia:
- Input: monthly_returns.csv prodotto dal backtest (rendimenti mensili
  storici dei 13 proxy + benchmark).
- Block bootstrap: campiono blocchi contigui di B = 3 mesi (preserva
  autocorrelazione di breve periodo e correlazioni cross-asset).
- Per ogni traiettoria, ricostruisco T mesi di rendimenti, simulo
  due scenari:
    A) Lump sum: 10.000 EUR investiti il giorno 0, pesi target.
    B) PAC: 200 EUR/mese versati ad ogni fine mese ai pesi target.
- N = 10.000 traiettorie per ciascun orizzonte (10/20/30 anni).
- Output: percentili p5/p25/p50/p75/p95 del NAV finale, equity curves
  esemplificative, distribuzione del MDD.

Bootstrap a blocchi e non IID single-month: senza i blocchi spezzeremmo
la struttura di vol clustering e correlazioni tra asset (l'oro sale
quando le azioni scendono, ecc.). Con blocchi di 3 mesi catturiamo
l'effetto senza essere troppo rigidi.

Stesso esercizio per i due benchmark (SP500 TR e MSCI World TR) per
poter confrontare le distribuzioni di esito.

Dipendenze: pandas, numpy, matplotlib.

Esecuzione:
  Prima esegui portafoglio-personale-backtest.py (genera monthly_returns.csv).
  Poi:
  python scripts/portafoglio-personale-montecarlo.py

Tempo: ~30-60 secondi.

Output in public/charts/portafoglio-personale-montecarlo/:
  - 01_distribuzione_nav_lump.png   (boxplot NAV finale 10/20/30y, lump)
  - 02_distribuzione_nav_pac.png    (boxplot NAV finale 10/20/30y, PAC)
  - 03_fan_chart_lump.png           (percentili nel tempo, lump 30y)
  - 04_fan_chart_pac.png            (percentili nel tempo, PAC 30y)
  - 05_proba_outperformance.png     (P[port > sp500] e P[port > world])
  - 06_distribuzione_mdd.png        (drawdown atteso)
  - summary_mc.json

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SLUG = "portafoglio-personale-montecarlo"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKTEST_OUT = REPO_ROOT / "public" / "charts" / "portafoglio-personale-backtest"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Stessi pesi del backtest
WEIGHTS = {
    "usa": 0.16, "globale": 0.08, "em": 0.12, "oro": 0.07,
    "smallcap": 0.07, "nasdaq": 0.16, "btc_bets": 0.05,
    "healthcare": 0.07, "europa": 0.06, "asia": 0.07,
    "energy": 0.03, "clean": 0.03, "nuclear": 0.03,
}

INITIAL_CAPITAL = 10_000.0
PAC_MONTHLY = 200.0

BLOCK_SIZE = 3            # mesi
N_PATHS = 10_000
HORIZONS_YEARS = [10, 20, 30]
HORIZONS_MONTHS = {f"{y}y": y * 12 for y in HORIZONS_YEARS}

# Colori
COLOR_PORT = "#1e3a8a"
COLOR_SP500 = "#d97706"
COLOR_WORLD = "#059669"
COLOR_NEUTRAL = "#6b7280"


# -------------------------------------------------------------------- #
# Caricamento dati                                                     #
# -------------------------------------------------------------------- #
def load_monthly_returns() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carica i rendimenti mensili del portafoglio (asset) e dei benchmark."""
    asset_path = BACKTEST_OUT / "monthly_returns.csv"
    if not asset_path.exists():
        raise FileNotFoundError(
            f"{asset_path} non trovato. Esegui prima "
            f"portafoglio-personale-backtest.py.")
    asset_rets = pd.read_csv(asset_path, parse_dates=[0], index_col=0)
    asset_rets = asset_rets.dropna()

    # Per i benchmark estraggo dai prezzi salvati nel backtest
    eq_path = BACKTEST_OUT / "equity_curves_monthly.csv"
    eq = pd.read_csv(eq_path, parse_dates=[0], index_col=0)
    sp500_nav_lump = eq["sp500_lump"]
    world_nav_lump = eq["world_lump"]
    sp500_ret = sp500_nav_lump.pct_change().dropna()
    world_ret = world_nav_lump.pct_change().dropna()
    common = asset_rets.index.intersection(sp500_ret.index)
    asset_rets = asset_rets.loc[common]
    bench_rets = pd.DataFrame({
        "sp500": sp500_ret.loc[common],
        "world": world_ret.loc[common],
    })
    return asset_rets, bench_rets


# -------------------------------------------------------------------- #
# Block bootstrap                                                      #
# -------------------------------------------------------------------- #
def block_bootstrap_indices(n_source: int, n_target: int, block: int,
                             rng: np.random.Generator) -> np.ndarray:
    """Genera indici (row positions) per un campionamento a blocchi."""
    n_blocks = int(np.ceil(n_target / block))
    starts = rng.integers(0, n_source - block + 1, size=n_blocks)
    idx = np.concatenate([np.arange(s, s + block) for s in starts])
    return idx[:n_target]


def simulate_paths_lump(asset_rets: np.ndarray, weights_vec: np.ndarray,
                         horizon: int, n_paths: int, block: int,
                         capital: float, rng: np.random.Generator) -> np.ndarray:
    """
    Restituisce array (n_paths, horizon+1) con NAV del portafoglio nel tempo.
    Lump sum: capitale iniziale investito a t=0, pesi target, no rebalancing.
    Asset pesi driftano liberi nel tempo.
    """
    n_source = asset_rets.shape[0]
    paths = np.empty((n_paths, horizon + 1))
    paths[:, 0] = capital
    units0 = (capital * weights_vec)  # in euro per asset, t=0

    for p in range(n_paths):
        idx = block_bootstrap_indices(n_source, horizon, block, rng)
        sample = asset_rets[idx]  # (horizon, n_assets)
        # NAV per asset nel tempo: euro_iniziali * cumprod(1+r)
        cum = np.cumprod(1 + sample, axis=0)  # (horizon, n_assets)
        nav_per_asset = units0[None, :] * cum  # (horizon, n_assets)
        paths[p, 1:] = nav_per_asset.sum(axis=1)
    return paths


def simulate_paths_pac(asset_rets: np.ndarray, weights_vec: np.ndarray,
                        horizon: int, n_paths: int, block: int,
                        monthly: float, rng: np.random.Generator) -> np.ndarray:
    """
    PAC: ogni fine mese versa `monthly` allocato ai pesi target.
    Trattiamo i versamenti come "compro X euro di ogni asset alla fine del mese"
    e poi il mese successivo applico il rendimento.
    """
    n_source = asset_rets.shape[0]
    n_assets = asset_rets.shape[1]
    paths = np.empty((n_paths, horizon + 1))
    paths[:, 0] = 0.0

    for p in range(n_paths):
        idx = block_bootstrap_indices(n_source, horizon, block, rng)
        sample = asset_rets[idx]  # (horizon, n_assets)
        # Simulazione passo per passo (vectorizzata sugli asset)
        nav_by_asset = np.zeros(n_assets)
        for t in range(horizon):
            # Apply return for the month
            nav_by_asset *= (1 + sample[t])
            # Versamento di fine mese
            nav_by_asset += monthly * weights_vec
            paths[p, t + 1] = nav_by_asset.sum()
    return paths


def simulate_paths_lump_single(bench_rets: np.ndarray, horizon: int,
                                 n_paths: int, block: int, capital: float,
                                 rng: np.random.Generator) -> np.ndarray:
    """Lump sum su un singolo asset (benchmark)."""
    n_source = bench_rets.shape[0]
    paths = np.empty((n_paths, horizon + 1))
    paths[:, 0] = capital
    for p in range(n_paths):
        idx = block_bootstrap_indices(n_source, horizon, block, rng)
        sample = bench_rets[idx]
        paths[p, 1:] = capital * np.cumprod(1 + sample)
    return paths


def simulate_paths_pac_single(bench_rets: np.ndarray, horizon: int,
                                n_paths: int, block: int, monthly: float,
                                rng: np.random.Generator) -> np.ndarray:
    n_source = bench_rets.shape[0]
    paths = np.empty((n_paths, horizon + 1))
    paths[:, 0] = 0.0
    for p in range(n_paths):
        idx = block_bootstrap_indices(n_source, horizon, block, rng)
        sample = bench_rets[idx]
        nav = 0.0
        for t in range(horizon):
            nav *= (1 + sample[t])
            nav += monthly
            paths[p, t + 1] = nav
    return paths


def max_drawdown_paths(paths: np.ndarray) -> np.ndarray:
    """MDD per ogni traiettoria (array N_paths,)."""
    peak = np.maximum.accumulate(paths, axis=1)
    return (paths / peak - 1).min(axis=1)


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


def plot_final_nav_distribution(results: dict, scenario: str, out_path: Path):
    horizons = list(results.keys())
    fig, ax = plt.subplots(figsize=(11, 6))
    width = 0.25
    offsets = [-width, 0, width]
    colors = [COLOR_PORT, COLOR_SP500, COLOR_WORLD]
    labels_legend = ["Portafoglio", "S&P 500", "MSCI World"]

    data_all = []
    positions = []
    for i, h in enumerate(horizons):
        for j, key in enumerate(["port", "sp500", "world"]):
            final = results[h][scenario][key][:, -1]
            data_all.append(final)
            positions.append(i + offsets[j])

    bps = ax.boxplot(data_all, positions=positions, widths=width * 0.9,
                     patch_artist=True, showfliers=False, whis=(5, 95))
    for k, box in enumerate(bps["boxes"]):
        box.set(facecolor=colors[k % 3], alpha=0.6)
    ax.set_xticks(range(len(horizons)))
    ax.set_xticklabels(horizons)
    ax.set_yscale("log")
    ax.set_ylabel("NAV finale (EUR, scala log)")
    title_pre = "Lump sum 10.000€" if scenario == "lump" else f"PAC {PAC_MONTHLY:.0f}€/mese"
    ax.set_title(f"Distribuzione NAV finale Monte Carlo — {title_pre}\n"
                 f"({N_PATHS:,} traiettorie, percentili 5-25-50-75-95)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.6) for c in colors]
    ax.legend(handles, labels_legend, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_fan_chart(paths: np.ndarray, scenario: str, title: str, out_path: Path):
    horizon = paths.shape[1] - 1
    months = np.arange(horizon + 1)
    pcts = [5, 25, 50, 75, 95]
    pct_vals = np.percentile(paths, pcts, axis=0)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.fill_between(months, pct_vals[0], pct_vals[4],
                    color=COLOR_PORT, alpha=0.15, label="p5–p95")
    ax.fill_between(months, pct_vals[1], pct_vals[3],
                    color=COLOR_PORT, alpha=0.30, label="p25–p75")
    ax.plot(months, pct_vals[2], color=COLOR_PORT, lw=2, label="Mediana")
    ax.set_xlabel("Mesi di orizzonte")
    ax.set_ylabel("NAV (EUR)")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_proba_outperformance(results: dict, out_path: Path):
    horizons = list(results.keys())
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, scenario, title_suff in zip(axes, ["lump", "pac"],
                                          ["Lump sum 10.000€", f"PAC {PAC_MONTHLY:.0f}€/mese"]):
        proba_sp = []
        proba_w = []
        for h in horizons:
            port = results[h][scenario]["port"][:, -1]
            sp = results[h][scenario]["sp500"][:, -1]
            w = results[h][scenario]["world"][:, -1]
            proba_sp.append(np.mean(port > sp))
            proba_w.append(np.mean(port > w))
        x = np.arange(len(horizons))
        width = 0.35
        ax.bar(x - width / 2, [p * 100 for p in proba_sp], width,
               color=COLOR_SP500, alpha=0.85, label="vs S&P 500")
        ax.bar(x + width / 2, [p * 100 for p in proba_w], width,
               color=COLOR_WORLD, alpha=0.85, label="vs MSCI World")
        for i, (ps, pw) in enumerate(zip(proba_sp, proba_w)):
            ax.text(x[i] - width / 2, ps * 100 + 1, f"{ps*100:.0f}%",
                    ha="center", fontsize=10)
            ax.text(x[i] + width / 2, pw * 100 + 1, f"{pw*100:.0f}%",
                    ha="center", fontsize=10)
        ax.axhline(50, color="black", lw=0.6, ls="--")
        ax.set_xticks(x)
        ax.set_xticklabels(horizons)
        ax.set_ylabel("Probabilità (%)")
        ax.set_ylim(0, 110)
        ax.set_title(f"P[Portafoglio > Benchmark] — {title_suff}")
        ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_mdd_distribution(results: dict, scenario: str, out_path: Path):
    horizons = list(results.keys())
    fig, ax = plt.subplots(figsize=(11, 6))
    width = 0.25
    offsets = [-width, 0, width]
    colors = [COLOR_PORT, COLOR_SP500, COLOR_WORLD]
    labels_legend = ["Portafoglio", "S&P 500", "MSCI World"]

    data_all = []
    positions = []
    for i, h in enumerate(horizons):
        for j, key in enumerate(["port", "sp500", "world"]):
            mdd = max_drawdown_paths(results[h][scenario][key])
            data_all.append(mdd)
            positions.append(i + offsets[j])

    bps = ax.boxplot(data_all, positions=positions, widths=width * 0.9,
                     patch_artist=True, showfliers=False, whis=(5, 95))
    for k, box in enumerate(bps["boxes"]):
        box.set(facecolor=colors[k % 3], alpha=0.6)
    ax.set_xticks(range(len(horizons)))
    ax.set_xticklabels(horizons)
    ax.set_ylabel("Max drawdown")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
    title_pre = "Lump sum" if scenario == "lump" else "PAC"
    ax.set_title(f"Distribuzione del Max Drawdown atteso — {title_pre}")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.6) for c in colors]
    ax.legend(handles, labels_legend, loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #
def main():
    _set_style()
    print(f"\n=== {SLUG} ===\n")
    rng = np.random.default_rng(42)

    print("[1/4] Caricamento rendimenti mensili...")
    asset_rets, bench_rets = load_monthly_returns()
    print(f"      Storia: {asset_rets.index[0].date()} -> {asset_rets.index[-1].date()}")
    print(f"      {len(asset_rets)} mesi, {asset_rets.shape[1]} asset")

    # Allinea ordine asset ai pesi
    asset_cols = list(WEIGHTS.keys())
    asset_rets = asset_rets[asset_cols]
    asset_np = asset_rets.values
    weights_vec = np.array([WEIGHTS[k] for k in asset_cols])
    sp500_np = bench_rets["sp500"].values
    world_np = bench_rets["world"].values

    print("\n[2/4] Simulazione Monte Carlo...")
    results: dict = {}
    for label, months in HORIZONS_MONTHS.items():
        print(f"      [{label}, {months} mesi]")
        port_lump = simulate_paths_lump(asset_np, weights_vec, months,
                                          N_PATHS, BLOCK_SIZE, INITIAL_CAPITAL, rng)
        port_pac = simulate_paths_pac(asset_np, weights_vec, months,
                                        N_PATHS, BLOCK_SIZE, PAC_MONTHLY, rng)
        sp_lump = simulate_paths_lump_single(sp500_np, months, N_PATHS,
                                               BLOCK_SIZE, INITIAL_CAPITAL, rng)
        sp_pac = simulate_paths_pac_single(sp500_np, months, N_PATHS,
                                             BLOCK_SIZE, PAC_MONTHLY, rng)
        w_lump = simulate_paths_lump_single(world_np, months, N_PATHS,
                                              BLOCK_SIZE, INITIAL_CAPITAL, rng)
        w_pac = simulate_paths_pac_single(world_np, months, N_PATHS,
                                            BLOCK_SIZE, PAC_MONTHLY, rng)
        results[label] = {
            "lump": {"port": port_lump, "sp500": sp_lump, "world": w_lump},
            "pac":  {"port": port_pac,  "sp500": sp_pac,  "world": w_pac},
        }

    print("\n[3/4] Plot...")
    plot_final_nav_distribution(results, "lump",
                                 OUT_DIR / "01_distribuzione_nav_lump.png")
    plot_final_nav_distribution(results, "pac",
                                 OUT_DIR / "02_distribuzione_nav_pac.png")
    # Fan chart sull'orizzonte 30y
    h_max = list(HORIZONS_MONTHS.keys())[-1]
    plot_fan_chart(results[h_max]["lump"]["port"], "lump",
                    f"Portafoglio — Lump sum 10.000€, fan chart {h_max}",
                    OUT_DIR / "03_fan_chart_lump.png")
    plot_fan_chart(results[h_max]["pac"]["port"], "pac",
                    f"Portafoglio — PAC {PAC_MONTHLY:.0f}€/mese, fan chart {h_max}",
                    OUT_DIR / "04_fan_chart_pac.png")
    plot_proba_outperformance(results, OUT_DIR / "05_proba_outperformance.png")
    plot_mdd_distribution(results, "lump", OUT_DIR / "06_distribuzione_mdd.png")

    print("\n[4/4] Salvataggio JSON...")
    def _q(arr):
        return {f"p{q}": float(np.percentile(arr, q)) for q in (5, 25, 50, 75, 95)}

    summary: dict = {
        "slug": SLUG,
        "parametri": {
            "n_paths": N_PATHS,
            "block_size_months": BLOCK_SIZE,
            "horizons_anni": HORIZONS_YEARS,
            "capitale_iniziale": INITIAL_CAPITAL,
            "pac_mensile": PAC_MONTHLY,
            "seed": 42,
        },
        "storia_input": {
            "inizio": str(asset_rets.index[0].date()),
            "fine": str(asset_rets.index[-1].date()),
            "mesi": int(len(asset_rets)),
        },
        "risultati": {},
    }

    for h_label, h_months in HORIZONS_MONTHS.items():
        block = {}
        for scenario in ["lump", "pac"]:
            scen = {}
            for key in ["port", "sp500", "world"]:
                paths = results[h_label][scenario][key]
                final = paths[:, -1]
                mdd = max_drawdown_paths(paths)
                scen[key] = {
                    "nav_finale_percentili": _q(final),
                    "mdd_percentili": _q(mdd),
                }
            # Proba outperformance
            port_final = results[h_label][scenario]["port"][:, -1]
            sp_final = results[h_label][scenario]["sp500"][:, -1]
            w_final = results[h_label][scenario]["world"][:, -1]
            scen["proba_port_gt_sp500"] = float(np.mean(port_final > sp_final))
            scen["proba_port_gt_world"] = float(np.mean(port_final > w_final))
            block[scenario] = scen
        summary["risultati"][h_label] = block

    (OUT_DIR / "summary_mc.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\n      Output in: {OUT_DIR}")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"        - {p.name}")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
