"""
SmartMoneyLab — Quale sleeve difensiva è la migliore?
======================================================

Test di 5 sleeve difensive azionarie (escluso bond e oro che hanno gia'
articoli dedicati) come alternativa o complemento al puro azionario
US in un portafoglio buy & hold:

  - Healthcare (XLV)           — settore difensivo classico
  - Consumer Staples (XLP)     — settore difensivo classico
  - Utilities (XLU)            — settore difensivo classico
  - Min Volatility (USMV)      — factor difensivo moderno
  - Quality (QUAL)             — factor qualita' (richiesto dal retail IT)

Confronto: portafoglio 90% SPY + 10% sleeve  vs  100% SPY puro,
buy & hold, no rebalancing, su rolling windows 5y / 10y / 20y
(20y solo per le 3 sleeve settoriali che hanno dati dal 1998;
USMV ha dati dal 2011, quindi rolling 5y / 10y limitati).

Due livelli di analisi:
  Livello A — periodo lungo 1998-2025 (27 anni): solo XLV, XLP, XLU.
              Rolling 5y / 10y / 20y. Confronto principale.
  Livello B — periodo breve 2013-2025 (12 anni): tutte e 5 le sleeve.
              Rolling 5y. Per includere USMV e QUAL nel confronto
              (USMV ha dati dal 2011, QUAL dal lug-2013; periodo comune
              determinato automaticamente da pandas dropna).

Tutti i dati sono Total Return (Adj Close yfinance = TR per US ETF).
Niente costi, niente tasse — convenzione standard del blog.

Dati richiesti in data/cache/ (scaricati da scripts/download_portfolio_data.py):
  - yf_proxy_spy.csv               (S&P 500 TR via SPY)
  - yf_proxy_xlv_healthcare.csv
  - yf_proxy_xlp_staples.csv
  - yf_proxy_xlu_utilities.csv
  - yf_proxy_usmv_minvol.csv

Output in public/charts/sleeve-difensiva-migliore/:
  - 01_equity_curves_livello_A.png  (3 sleeve + benchmark, 1998-2025)
  - 02_equity_curves_livello_B.png  (4 sleeve + benchmark, 2011-2025)
  - 03_boxplot_cagr_rolling_A.png
  - 04_boxplot_mdd_rolling_A.png
  - 05_boxplot_sharpe_rolling_A.png
  - 06_boxplot_calmar_rolling_A.png
  - 07_boxplot_cagr_rolling_B.png
  - 08_win_rate_per_sleeve.png
  - 09_correlazione_con_spy.png
  - summary.json
  - rolling_windows_A.csv
  - rolling_windows_B.csv
  - equity_curves_full.csv          (per il reel social)

Dipendenze: pandas, numpy, matplotlib.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SLUG = "sleeve-difensiva-migliore"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------- #
# Parametri                                                            #
# -------------------------------------------------------------------- #
INITIAL_CAPITAL = 10_000.0
# Test in parallelo di tre pesi della sleeve difensiva: 10%, 15%, 20%.
# Il 10% e' la dose "tilt" classica, il 20% comincia a essere una scelta
# di allocazione vera. Mostrare i tre permette di vedere il trade-off.
SLEEVE_WEIGHTS = [0.10, 0.15, 0.20]

# Sleeves del Livello A (storia lunga, 1998+)
SLEEVES_A = {
    "Healthcare": "proxy_xlv_healthcare",
    "Consumer Staples": "proxy_xlp_staples",
    "Utilities": "proxy_xlu_utilities",
}
# Sleeves aggiuntive del Livello B (storia breve)
SLEEVES_B_EXTRA = {
    "Min Vol": "proxy_usmv_minvol",       # iShares MSCI USA Min Vol, 2011
    "Quality": "proxy_qual_quality",      # iShares MSCI USA Quality Factor, 2013
}

# Rolling windows in giorni di trading (~252/anno). Mensile per coerenza
# con altri articoli — campiono ad ogni fine mese.
WINDOWS_MONTHS = {"5y": 60, "10y": 120, "20y": 240}
STEP_MONTHS = 3

# Palette: SP500 baseline, sleeve evidenziate
COLOR_SPY = "#1e3a8a"           # navy
COLOR_HEALTHCARE = "#d97706"     # ambra
COLOR_STAPLES = "#059669"        # verde
COLOR_UTILITIES = "#7c3aed"      # viola
COLOR_MINVOL = "#dc2626"         # rosso (carattere "factor")
COLOR_QUALITY = "#fb923c"        # arancione acceso (factor)
COLOR_NEUTRAL = "#6b7280"

SLEEVE_COLORS = {
    "Healthcare": COLOR_HEALTHCARE,
    "Consumer Staples": COLOR_STAPLES,
    "Utilities": COLOR_UTILITIES,
    "Min Vol": COLOR_MINVOL,
    "Quality": COLOR_QUALITY,
}


# -------------------------------------------------------------------- #
# Caricamento prezzi                                                   #
# -------------------------------------------------------------------- #
def load_yf_monthly(slug: str) -> pd.Series:
    """Adj Close mensile (fine mese) di un ticker yfinance."""
    path = CACHE_DIR / f"yf_{slug}.csv"
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
    s = pd.to_numeric(df["AdjClose"], errors="coerce").dropna()
    monthly = s.resample("ME").last().dropna()
    return monthly


def build_panel_A() -> pd.DataFrame:
    """SPY + 3 sleeve dal 1998. Periodo comune = min(start) dei 4."""
    spy = load_yf_monthly("proxy_spy").rename("SPY")
    cols = {"SPY": spy}
    for name, slug in SLEEVES_A.items():
        cols[name] = load_yf_monthly(slug).rename(name)
    df = pd.DataFrame(cols).dropna()
    return df


def build_panel_B() -> pd.DataFrame:
    """SPY + 4 sleeve (incluso USMV) dal 2011."""
    spy = load_yf_monthly("proxy_spy").rename("SPY")
    cols = {"SPY": spy}
    for name, slug in SLEEVES_A.items():
        cols[name] = load_yf_monthly(slug).rename(name)
    for name, slug in SLEEVES_B_EXTRA.items():
        cols[name] = load_yf_monthly(slug).rename(name)
    df = pd.DataFrame(cols).dropna()
    return df


# -------------------------------------------------------------------- #
# Costruzione portafogli                                               #
# -------------------------------------------------------------------- #
def simulate_buyhold(prices: pd.DataFrame, weights: dict[str, float],
                       initial_capital: float) -> pd.Series:
    """Lump sum buy & hold, no rebalancing. Pesi driftano nel tempo."""
    first = prices.iloc[0]
    units = {k: (weights[k] * initial_capital) / first[k] for k in weights}
    nav = pd.Series(0.0, index=prices.index)
    for k, u in units.items():
        nav += u * prices[k]
    return nav


# -------------------------------------------------------------------- #
# Metriche                                                             #
# -------------------------------------------------------------------- #
def cagr_m(nav: pd.Series) -> float:
    n = len(nav) - 1
    if n < 12 or nav.iloc[0] <= 0 or nav.iloc[-1] <= 0:
        return float("nan")
    growth = nav.iloc[-1] / nav.iloc[0]
    if growth <= 0:
        return float("nan")
    return float(growth ** (12.0 / n) - 1)


def mdd_m(nav: pd.Series) -> float:
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def vol_m(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    return float(rets.std() * np.sqrt(12))


def sharpe_m(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    if rets.std() == 0:
        return float("nan")
    return float(rets.mean() / rets.std() * np.sqrt(12))


def sortino_m(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    downside = rets[rets < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("nan")
    return float(rets.mean() / downside.std() * np.sqrt(12))


def calmar_m(nav: pd.Series) -> float:
    mdd_abs = abs(mdd_m(nav))
    if mdd_abs == 0:
        return float("nan")
    return cagr_m(nav) / mdd_abs


@dataclass
class WindowMetrics:
    portfolio: str
    sleeve: str
    start: pd.Timestamp
    end: pd.Timestamp
    cagr: float
    mdd: float
    vol: float
    sharpe: float
    sortino: float
    calmar: float


# -------------------------------------------------------------------- #
# Rolling windows                                                      #
# -------------------------------------------------------------------- #
def rolling_windows_for_portfolio(prices: pd.DataFrame, weights: dict[str, float],
                                    label: str, sleeve_name: str,
                                    window_months: int) -> list[WindowMetrics]:
    n = len(prices)
    out: list[WindowMetrics] = []
    i = 0
    while i + window_months <= n:
        sub = prices.iloc[i:i + window_months]
        nav = simulate_buyhold(sub, weights, INITIAL_CAPITAL)
        out.append(WindowMetrics(
            portfolio=label, sleeve=sleeve_name,
            start=sub.index[0], end=sub.index[-1],
            cagr=cagr_m(nav), mdd=mdd_m(nav), vol=vol_m(nav),
            sharpe=sharpe_m(nav), sortino=sortino_m(nav),
            calmar=calmar_m(nav),
        ))
        i += STEP_MONTHS
    return out


def all_rolling_for_level(prices: pd.DataFrame, sleeves: list[str],
                            window_months: int, level: str
                            ) -> list[WindowMetrics]:
    """
    Raccoglie rolling per benchmark (100% SPY) + ogni portafoglio
    (1-sleeve_w) SPY + sleeve_w sleeve, per ogni peso in SLEEVE_WEIGHTS.
    """
    out: list[WindowMetrics] = []
    out += rolling_windows_for_portfolio(
        prices[["SPY"]], {"SPY": 1.0}, label="100% SPY",
        sleeve_name="benchmark", window_months=window_months)
    for s in sleeves:
        if s not in prices.columns:
            continue
        for w in SLEEVE_WEIGHTS:
            pct = int(round(w * 100))
            out += rolling_windows_for_portfolio(
                prices[["SPY", s]],
                {"SPY": 1 - w, s: w},
                label=f"{100-pct}% SPY + {pct}% {s}",
                sleeve_name=s, window_months=window_months)
    return out


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


def plot_equity_curves(prices: pd.DataFrame, sleeves: list[str],
                         title: str, out_path: Path,
                         sleeve_weight: float = 0.10):
    """Equity curve a un singolo peso (default 10%, "dose classica")."""
    pct = int(round(sleeve_weight * 100))
    fig, ax = plt.subplots(figsize=(12, 6.5))
    spy_only = simulate_buyhold(prices[["SPY"]], {"SPY": 1.0}, INITIAL_CAPITAL)
    ax.plot(spy_only.index, spy_only.values, color=COLOR_SPY, lw=2.2,
            label="100% SPY (benchmark)")
    for s in sleeves:
        if s not in prices.columns:
            continue
        nav = simulate_buyhold(prices[["SPY", s]],
                                {"SPY": 1 - sleeve_weight, s: sleeve_weight},
                                INITIAL_CAPITAL)
        ax.plot(nav.index, nav.values, color=SLEEVE_COLORS[s], lw=1.8,
                label=f"{100-pct}% SPY + {pct}% {s}")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_ylabel("NAV (USD, scala log)")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_tradeoff_cagr_vs_mdd(panel: pd.DataFrame, sleeves: list[str],
                                title: str, out_path: Path):
    """
    Per ogni sleeve, traccia una linea (CAGR, MDD) al variare del peso
    della sleeve da 0% (= 100% SPY) al 20%. Mostra il trade-off del
    "quanta sleeve aggiungere e cosa ti compri".
    """
    fig, ax = plt.subplots(figsize=(11, 7))
    # Punto comune di partenza (100% SPY)
    spy_nav = simulate_buyhold(panel[["SPY"]], {"SPY": 1.0}, INITIAL_CAPITAL)
    spy_cagr = cagr_m(spy_nav)
    spy_mdd = mdd_m(spy_nav)
    ax.scatter([spy_mdd], [spy_cagr], color=COLOR_SPY, s=180,
               edgecolor="white", linewidth=2, zorder=5, label="100% SPY")
    ax.annotate("100% SPY", (spy_mdd, spy_cagr),
                 xytext=(10, 8), textcoords="offset points",
                 fontsize=10, color=COLOR_SPY, fontweight="bold")

    for s in sleeves:
        if s not in panel.columns:
            continue
        xs = [spy_mdd]
        ys = [spy_cagr]
        for w in SLEEVE_WEIGHTS:
            nav = simulate_buyhold(panel[["SPY", s]],
                                    {"SPY": 1 - w, s: w}, INITIAL_CAPITAL)
            xs.append(mdd_m(nav))
            ys.append(cagr_m(nav))
        ax.plot(xs, ys, "-o", color=SLEEVE_COLORS[s], lw=2.2, ms=10,
                mec="white", mew=1.5, label=s)
        # Annoto solo l'ultimo punto (20%)
        ax.annotate(f"{s} 20%", (xs[-1], ys[-1]),
                     xytext=(10, -5), textcoords="offset points",
                     fontsize=9, color=SLEEVE_COLORS[s])

    ax.set_xlabel("Max drawdown del portafoglio (più a destra = meno doloroso)")
    ax.set_ylabel("CAGR del portafoglio")
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v*100:.1f}%"))
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v*100:.1f}%"))
    ax.set_title(
        f"{title}\nLinee che si spostano verso ALTO-DESTRA = sleeve buone "
        "(più CAGR e meno MDD).")
    ax.legend(loc="best", frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_metric_boxplot(results: dict[str, list[WindowMetrics]],
                          metric: str, ylabel: str, title: str,
                          out_path: Path, as_pct: bool = True):
    """Boxplot di una metrica per portafoglio, raggruppati per orizzonte."""
    horizons = list(results.keys())
    portfolios = sorted({w.portfolio for h in horizons for w in results[h]})
    # Ordina: benchmark per primo
    portfolios = sorted(portfolios, key=lambda p: (0 if p == "100% SPY" else 1, p))
    n_p = len(portfolios)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    width = 0.8 / n_p
    positions = []
    data_all = []
    colors_all = []
    for i, h in enumerate(horizons):
        for j, p in enumerate(portfolios):
            vals = [getattr(w, metric) for w in results[h]
                    if w.portfolio == p and not np.isnan(getattr(w, metric))]
            data_all.append(vals if vals else [0])
            positions.append(i + (j - (n_p - 1) / 2) * width)
            sleeve = p.replace("90% SPY + 10% ", "").replace("100% SPY", "benchmark")
            colors_all.append(SLEEVE_COLORS.get(sleeve, COLOR_SPY))
    bps = ax.boxplot(data_all, positions=positions, widths=width * 0.85,
                      patch_artist=True, showfliers=True)
    for box, c in zip(bps["boxes"], colors_all):
        box.set(facecolor=c, alpha=0.6)
    ax.set_xticks(range(len(horizons)))
    ax.set_xticklabels(horizons)
    ax.set_ylabel(ylabel)
    if as_pct:
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
    ax.axhline(0, color="black", lw=0.6)
    handles = [plt.Rectangle((0, 0), 1, 1,
                              color=SLEEVE_COLORS.get(p.replace("90% SPY + 10% ", "")
                                                       .replace("100% SPY", "benchmark"),
                                                       COLOR_SPY),
                              alpha=0.6)
               for p in portfolios]
    ax.legend(handles, portfolios, loc="best", frameon=False, fontsize=9)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_win_rate(results: dict[str, list[WindowMetrics]], out_path: Path,
                   benchmark_label: str = "100% SPY"):
    """Quota di finestre in cui ogni portafoglio batte il benchmark sul Sharpe."""
    horizons = list(results.keys())
    portfolios = [p for p in sorted({w.portfolio for h in horizons
                                        for w in results[h]})
                  if p != benchmark_label]
    fig, ax = plt.subplots(figsize=(11, 6))
    width = 0.8 / len(horizons)
    for hi, h in enumerate(horizons):
        bench = [w for w in results[h] if w.portfolio == benchmark_label]
        bench_by_start = {w.start: w for w in bench}
        wrs = []
        for p in portfolios:
            p_wins = 0
            n = 0
            for w in results[h]:
                if w.portfolio != p:
                    continue
                b = bench_by_start.get(w.start)
                if b is None:
                    continue
                n += 1
                if not np.isnan(w.sharpe) and not np.isnan(b.sharpe):
                    if w.sharpe > b.sharpe:
                        p_wins += 1
            wrs.append((p_wins / n * 100) if n > 0 else 0)
        x = np.arange(len(portfolios)) + (hi - (len(horizons) - 1) / 2) * width
        sleeves_of_p = [p.replace("90% SPY + 10% ", "") for p in portfolios]
        cs = [SLEEVE_COLORS.get(s, COLOR_SPY) for s in sleeves_of_p]
        ax.bar(x, wrs, width * 0.85, color=cs, alpha=0.85,
               label=f"rolling {h}")
        for xi, wr in zip(x, wrs):
            ax.text(xi, wr + 1, f"{wr:.0f}%", ha="center", fontsize=9)
    ax.set_xticks(range(len(portfolios)))
    ax.set_xticklabels([p.replace("90% SPY + 10% ", "") for p in portfolios],
                       rotation=0)
    ax.set_ylabel("Win rate Sharpe vs 100% SPY (%)")
    ax.axhline(50, color="black", lw=0.6, ls="--")
    ax.set_ylim(0, 115)
    ax.set_title("Quota di finestre rolling in cui la sleeve migliora lo Sharpe")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_correlazione_con_spy(prices: pd.DataFrame, out_path: Path):
    """Correlazione mensile di ogni sleeve con SPY su rolling 36 mesi."""
    rets = prices.pct_change().dropna()
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in rets.columns:
        if col == "SPY":
            continue
        corr = rets[col].rolling(36).corr(rets["SPY"])
        ax.plot(corr.index, corr.values,
                color=SLEEVE_COLORS.get(col, COLOR_NEUTRAL),
                lw=1.8, label=col)
    ax.axhline(1.0, color="black", lw=0.6, ls=":", alpha=0.6)
    ax.axhline(0.0, color="black", lw=0.6)
    ax.set_ylabel("Correlazione rolling 36 mesi con SPY")
    ax.set_ylim(-0.2, 1.05)
    ax.legend(loc="lower left", frameon=False)
    ax.set_title("Correlazione delle sleeve con il S&P 500 (rolling 36 mesi)")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #
def main():
    _set_style()
    print(f"\n=== {SLUG} ===\n")

    print("[1/5] Caricamento prezzi (mensili)...")
    panel_A = build_panel_A()
    panel_B = build_panel_B()
    print(f"      Livello A (3 sleeve + SPY): "
          f"{panel_A.index[0].date()} -> {panel_A.index[-1].date()} "
          f"({len(panel_A)} mesi)")
    print(f"      Livello B (4 sleeve + SPY): "
          f"{panel_B.index[0].date()} -> {panel_B.index[-1].date()} "
          f"({len(panel_B)} mesi)")

    print("\n[2/5] Rolling windows Livello A (Healthcare, Staples, Utilities)...")
    results_A = {}
    for label, win in WINDOWS_MONTHS.items():
        if win > len(panel_A):
            print(f"      [{label}] saltata, dati insufficienti ({win}>{len(panel_A)})")
            continue
        results_A[label] = all_rolling_for_level(
            panel_A, list(SLEEVES_A.keys()), win, "A")
        n_bench = sum(1 for w in results_A[label] if w.portfolio == "100% SPY")
        print(f"      [{label}] {n_bench} finestre per portafoglio")

    print("\n[3/5] Rolling windows Livello B (con Min Vol)...")
    sleeves_all = list(SLEEVES_A.keys()) + list(SLEEVES_B_EXTRA.keys())
    results_B = {}
    for label, win in WINDOWS_MONTHS.items():
        if win > len(panel_B):
            print(f"      [{label}] saltata, dati insufficienti ({win}>{len(panel_B)})")
            continue
        results_B[label] = all_rolling_for_level(panel_B, sleeves_all, win, "B")
        n_bench = sum(1 for w in results_B[label] if w.portfolio == "100% SPY")
        print(f"      [{label}] {n_bench} finestre per portafoglio")

    print("\n[4/5] Plot...")
    plot_equity_curves(panel_A, list(SLEEVES_A.keys()),
                        "Equity curves Livello A — 1998-2025 (3 sleeve settoriali)",
                        OUT_DIR / "01_equity_curves_livello_A.png")
    plot_equity_curves(panel_B, sleeves_all,
                        "Equity curves Livello B — 2011-2025 (con Min Vol)",
                        OUT_DIR / "02_equity_curves_livello_B.png")
    plot_metric_boxplot(results_A, "cagr", "CAGR",
                         "CAGR rolling — Livello A", OUT_DIR / "03_boxplot_cagr_rolling_A.png")
    plot_metric_boxplot(results_A, "mdd", "Max drawdown",
                         "Max drawdown rolling — Livello A",
                         OUT_DIR / "04_boxplot_mdd_rolling_A.png")
    plot_metric_boxplot(results_A, "sharpe", "Sharpe ratio",
                         "Sharpe rolling — Livello A",
                         OUT_DIR / "05_boxplot_sharpe_rolling_A.png", as_pct=False)
    plot_metric_boxplot(results_A, "calmar", "Calmar ratio",
                         "Calmar rolling — Livello A",
                         OUT_DIR / "06_boxplot_calmar_rolling_A.png", as_pct=False)
    if results_B:
        plot_metric_boxplot(results_B, "cagr", "CAGR",
                             "CAGR rolling 5y — Livello B (5 sleeve, 2013-2025)",
                             OUT_DIR / "07_boxplot_cagr_rolling_B.png")
    plot_win_rate(results_A, OUT_DIR / "08_win_rate_per_sleeve.png")
    plot_correlazione_con_spy(panel_B, OUT_DIR / "09_correlazione_con_spy.png")
    plot_tradeoff_cagr_vs_mdd(
        panel_A, list(SLEEVES_A.keys()),
        "Trade-off CAGR vs MDD — Livello A (1998-2025) — pesi 10/15/20%",
        OUT_DIR / "10_tradeoff_cagr_vs_mdd_A.png")
    plot_tradeoff_cagr_vs_mdd(
        panel_B, list(SLEEVES_A.keys()) + list(SLEEVES_B_EXTRA.keys()),
        "Trade-off CAGR vs MDD — Livello B (2013-2025) — pesi 10/15/20%",
        OUT_DIR / "11_tradeoff_cagr_vs_mdd_B.png")

    print("\n[5/5] Salvataggio CSV e JSON...")
    # CSV rolling
    rows = []
    for label, lst in results_A.items():
        for w in lst:
            d = asdict(w)
            d["window"] = label
            d["level"] = "A"
            d["start"] = str(w.start.date())
            d["end"] = str(w.end.date())
            rows.append(d)
    pd.DataFrame(rows).to_csv(OUT_DIR / "rolling_windows_A.csv", index=False)
    rows_b = []
    for label, lst in results_B.items():
        for w in lst:
            d = asdict(w)
            d["window"] = label
            d["level"] = "B"
            d["start"] = str(w.start.date())
            d["end"] = str(w.end.date())
            rows_b.append(d)
    pd.DataFrame(rows_b).to_csv(OUT_DIR / "rolling_windows_B.csv", index=False)

    # Equity curves complete per il reel — usiamo il peso "tilt classico" 10%
    equity = {}
    spy_only_A = simulate_buyhold(panel_A[["SPY"]], {"SPY": 1.0}, INITIAL_CAPITAL)
    equity["100% SPY"] = spy_only_A
    REEL_WEIGHT = 0.10
    for s in SLEEVES_A.keys():
        nav = simulate_buyhold(panel_A[["SPY", s]],
                                {"SPY": 1 - REEL_WEIGHT, s: REEL_WEIGHT},
                                INITIAL_CAPITAL)
        equity[f"90/10 {s}"] = nav
    pd.DataFrame(equity).to_csv(OUT_DIR / "equity_curves_full.csv")

    # Summary
    def _q(arr):
        arr = [x for x in arr if not np.isnan(x)]
        if not arr:
            return {}
        return {f"p{q}": float(np.percentile(arr, q)) for q in (5, 25, 50, 75, 95)}

    def _summary_per_portfolio(results, metric):
        out = {}
        for h, lst in results.items():
            for p in sorted({w.portfolio for w in lst}):
                arr = [getattr(w, metric) for w in lst if w.portfolio == p]
                out.setdefault(p, {})[h] = _q(arr)
        return out

    def _metrics_for_combo(panel_used, weights_dict, cols_used):
        nav = simulate_buyhold(panel_used[cols_used], weights_dict, INITIAL_CAPITAL)
        return {
            "periodo_inizio": str(panel_used.index[0].date()),
            "periodo_fine": str(panel_used.index[-1].date()),
            "nav_finale": float(nav.iloc[-1]),
            "cagr": cagr_m(nav),
            "mdd": mdd_m(nav),
            "vol": vol_m(nav),
            "sharpe": sharpe_m(nav),
            "sortino": sortino_m(nav),
            "calmar": calmar_m(nav),
        }

    full_period_metrics = {}
    # Benchmark su entrambi i pannelli
    full_period_metrics["100% SPY [Livello A]"] = _metrics_for_combo(
        panel_A, {"SPY": 1.0}, ["SPY"])
    full_period_metrics["100% SPY [Livello B]"] = _metrics_for_combo(
        panel_B, {"SPY": 1.0}, ["SPY"])
    # Per ogni sleeve, tre pesi
    for s in SLEEVES_A.keys():
        for w in SLEEVE_WEIGHTS:
            pct = int(round(w * 100))
            full_period_metrics[f"{100-pct}/{pct} SPY+{s} [Livello A]"] = (
                _metrics_for_combo(panel_A, {"SPY": 1 - w, s: w}, ["SPY", s]))
    for s in list(SLEEVES_A.keys()) + list(SLEEVES_B_EXTRA.keys()):
        if s not in panel_B.columns:
            continue
        for w in SLEEVE_WEIGHTS:
            pct = int(round(w * 100))
            full_period_metrics[f"{100-pct}/{pct} SPY+{s} [Livello B]"] = (
                _metrics_for_combo(panel_B, {"SPY": 1 - w, s: w}, ["SPY", s]))

    summary = {
        "slug": SLUG,
        "parametri": {
            "sleeve_weights": SLEEVE_WEIGHTS,
            "initial_capital": INITIAL_CAPITAL,
            "windows_months": WINDOWS_MONTHS,
            "step_months": STEP_MONTHS,
        },
        "panel_A": {
            "inizio": str(panel_A.index[0].date()),
            "fine": str(panel_A.index[-1].date()),
            "mesi": int(len(panel_A)),
        },
        "panel_B": {
            "inizio": str(panel_B.index[0].date()),
            "fine": str(panel_B.index[-1].date()),
            "mesi": int(len(panel_B)),
        },
        "full_period": full_period_metrics,
        "rolling_A_cagr_percentili": _summary_per_portfolio(results_A, "cagr"),
        "rolling_A_mdd_percentili": _summary_per_portfolio(results_A, "mdd"),
        "rolling_A_sharpe_percentili": _summary_per_portfolio(results_A, "sharpe"),
        "rolling_A_calmar_percentili": _summary_per_portfolio(results_A, "calmar"),
        "rolling_B_cagr_percentili": _summary_per_portfolio(results_B, "cagr"),
        "rolling_B_sharpe_percentili": _summary_per_portfolio(results_B, "sharpe"),
    }

    # Win rate Sharpe vs benchmark, calcolato matchando per start
    def win_rate_vs_benchmark(results, metric):
        out = {}
        for h, lst in results.items():
            bench = {w.start: w for w in lst if w.portfolio == "100% SPY"}
            for p in sorted({w.portfolio for w in lst if w.portfolio != "100% SPY"}):
                n, wins = 0, 0
                for w in lst:
                    if w.portfolio != p:
                        continue
                    b = bench.get(w.start)
                    if b is None:
                        continue
                    a, c = getattr(w, metric), getattr(b, metric)
                    if not np.isnan(a) and not np.isnan(c):
                        n += 1
                        if a > c:
                            wins += 1
                out.setdefault(p, {})[h] = (wins / n) if n > 0 else None
        return out

    summary["win_rate_sharpe_vs_spy_A"] = win_rate_vs_benchmark(results_A, "sharpe")
    summary["win_rate_sharpe_vs_spy_B"] = win_rate_vs_benchmark(results_B, "sharpe")
    summary["win_rate_calmar_vs_spy_A"] = win_rate_vs_benchmark(results_A, "calmar")
    summary["win_rate_mdd_vs_spy_A"] = win_rate_vs_benchmark(results_A, "mdd")

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print(f"\n      Output in: {OUT_DIR}")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"        - {p.name}")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
