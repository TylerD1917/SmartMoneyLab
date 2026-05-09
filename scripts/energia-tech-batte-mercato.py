"""
SmartMoneyLab — Mix Nasdaq + Energia: batte il mercato?
========================================================

Primo articolo della serie "Strategie per battere il mercato?".
Framework di valutazione a 6+1 metriche applicato a una strategia di mix
70/30 QQQ-XLE proposta su X, contro il benchmark S&P 500.

Portafogli testati (tutti buy & hold, no rebalancing):
  1. 100% SPY (S&P 500 ETF) — il benchmark "il mercato"
  2. 70/30 QQQ-XLE — la strategia da testare (Nasdaq + Energia USA)
  3. 50/50 QQQ-XLE — variante piu' aggressiva sull'energy
  4. 100% QQQ — confronto puro Nasdaq

Asset:
- SPY  (SPDR S&P 500 ETF Trust, dal 1993)
- QQQ  (Invesco Nasdaq-100 Trust, dal 1999) — vincolo del periodo
- XLE  (Energy Select Sector SPDR, dal 1998)

Tutti scaricati via yfinance con auto_adjust=True: i prezzi 'Close'
restituiti riflettono gia' dividendi reinvestiti e split. Di fatto
Total Return.

Periodo effettivo: 1999-03-10 (lancio QQQ) -> 2025-12-XX. ~26 anni.

Framework di valutazione (6+1 metriche):
  1. CAGR mediano rolling >= benchmark
  2. Win rate (% finestre vs benchmark) >= 60%
  3. Volatilita' annualizzata <= benchmark * 1.10
  4. Max Drawdown mediano <= benchmark * 1.10 (meno negativo o pari a
     +10% di tolleranza)
  5. Sharpe ratio >= benchmark
  6. Calmar ratio (CAGR/|MDD|) >= benchmark
  7. Sortino ratio >= benchmark (variante di Sharpe sulla downside vol)

Risk-free rate per Sharpe/Sortino: 2% annuo costante (proxy storica
T-bill 3M sul lungo periodo). E' una semplificazione esplicitata.

Verdict:
  - VINCE       se soddisfa TUTTI e 7 i criteri
  - PARZIALE    se ne soddisfa 4-6 su 7
  - NON VINCE   se ne soddisfa <= 3 su 7

Output:
- public/charts/energia-tech-batte-mercato/01..05_*.png
- summary.json (con scorecard strutturata)
- data.csv

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -------------------------------------------------------------------- #
# Setup percorsi                                                       #
# -------------------------------------------------------------------- #
SLUG = "energia-tech-batte-mercato"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Tickers
TICKERS = ["SPY", "QQQ", "XLE"]
START_DATE = "1999-03-10"  # lancio QQQ
END_DATE = "2025-12-31"

# Portafogli da testare (allocazione iniziale, buy & hold)
PORTFOLIOS = {
    "SPY 100%":         {"SPY": 1.0, "QQQ": 0.0, "XLE": 0.0},
    "QQQ 70 / XLE 30":  {"SPY": 0.0, "QQQ": 0.70, "XLE": 0.30},
    "QQQ 50 / XLE 50":  {"SPY": 0.0, "QQQ": 0.50, "XLE": 0.50},
    "QQQ 100%":         {"SPY": 0.0, "QQQ": 1.0, "XLE": 0.0},
}
BENCHMARK_NAME = "SPY 100%"  # il portafoglio contro cui si misura "il mercato"
STRATEGY_NAME = "QQQ 70 / XLE 30"  # la strategia di interesse

# Parametri rolling
WINDOWS_MONTHS = {"5y": 60, "10y": 120}
STEP_MONTHS = 6

# Risk-free per Sharpe/Sortino
RISK_FREE_ANNUAL = 0.02

# Soglie del framework di valutazione
WIN_RATE_THRESHOLD = 0.60
VOL_TOLERANCE = 1.10  # vol_strategia <= vol_benchmark * 1.10
MDD_TOLERANCE = 1.10  # |MDD_strategia| <= |MDD_benchmark| * 1.10

# Palette
COLORS = {
    "SPY 100%":         "#1e3a8a",   # navy (benchmark)
    "QQQ 70 / XLE 30":  "#d97706",   # ambra (strategia)
    "QQQ 50 / XLE 50":  "#f59e0b",   # ambra chiaro
    "QQQ 100%":         "#3b82f6",   # blu medio
}


# -------------------------------------------------------------------- #
# Download via yfinance                                                #
# -------------------------------------------------------------------- #

def load_etf_daily(tickers: list[str]) -> pd.DataFrame:
    """
    Scarica i prezzi daily adjusted (TR) di una lista di tickers.
    Cache su disco per non riscaricare ad ogni run.
    """
    cache_path = CACHE_DIR / f"yfinance_etf_{'_'.join(tickers)}.csv"
    if cache_path.exists():
        print(f"[cache] {cache_path.name}")
        df = pd.read_csv(cache_path, parse_dates=["Date"]).set_index("Date")
        return df

    try:
        import yfinance as yf
    except ImportError:
        raise RuntimeError(
            "yfinance non installato. Esegui: pip install yfinance"
        )

    print(f"[yfinance] downloading {tickers} daily…")
    out = {}
    for t in tickers:
        ticker = yf.Ticker(t)
        data = ticker.history(start=START_DATE, end=END_DATE,
                              interval="1d", auto_adjust=True)
        if data.empty:
            raise RuntimeError(f"yfinance: nessun dato per {t}")
        data.index = pd.DatetimeIndex(data.index).tz_localize(None)
        out[t] = data["Close"]

    df = pd.DataFrame(out).dropna()
    df.index.name = "Date"
    df.to_csv(cache_path)
    print(f"  -> {len(df)} righe daily, dal {df.index.min().date()} al {df.index.max().date()}")
    return df


# -------------------------------------------------------------------- #
# Costruzione NAV portafogli buy & hold                                #
# -------------------------------------------------------------------- #

def build_buy_and_hold_nav(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """
    NAV cumulato di un portafoglio buy & hold con pesi iniziali.
    Niente rebalancing — i pesi driftano coi rendimenti relativi.
    NAV(0) = 1.

    Implementazione: traduco i pesi in numero di "quote" iniziali
    dato un capitale 1 USD, poi al tempo t il NAV e' la somma di
    quote * prezzo_t per ogni asset.
    """
    p0 = prices.iloc[0]
    used_assets = [a for a, w in weights.items() if w > 0]
    if not used_assets:
        raise ValueError(f"Nessun asset con peso > 0 in {weights}")
    quote_iniziali = {a: weights[a] / p0[a] for a in used_assets}
    nav = sum(quote_iniziali[a] * prices[a] for a in used_assets)
    return nav


def daily_returns_from_nav(nav: pd.Series) -> pd.Series:
    return nav.pct_change().dropna()


# -------------------------------------------------------------------- #
# Metriche di rischio/rendimento                                       #
# -------------------------------------------------------------------- #

def cagr_from_nav(nav: pd.Series) -> float:
    n_days = len(nav)
    growth = nav.iloc[-1] / nav.iloc[0]
    if growth <= 0:
        return float("nan")
    years = n_days / 252.0
    return float(growth ** (1 / years) - 1)


def max_drawdown_from_nav(nav: pd.Series) -> float:
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def annual_vol(daily_returns: pd.Series) -> float:
    return float(daily_returns.std() * np.sqrt(252))


def sharpe_ratio(daily_returns: pd.Series, rf_annual: float) -> float:
    excess_daily = daily_returns - rf_annual / 252
    vol = daily_returns.std() * np.sqrt(252)
    if vol == 0 or np.isnan(vol):
        return float("nan")
    return float((excess_daily.mean() * 252) / vol)


def sortino_ratio(daily_returns: pd.Series, rf_annual: float) -> float:
    rf_daily = rf_annual / 252
    excess = daily_returns - rf_daily
    downside = excess.copy()
    downside[downside > 0] = 0
    downside_vol = np.sqrt((downside ** 2).mean()) * np.sqrt(252)
    if downside_vol == 0 or np.isnan(downside_vol):
        return float("nan")
    return float((excess.mean() * 252) / downside_vol)


def calmar_ratio(nav: pd.Series) -> float:
    cagr = cagr_from_nav(nav)
    mdd = max_drawdown_from_nav(nav)
    if mdd == 0 or np.isnan(mdd):
        return float("nan")
    return float(cagr / abs(mdd))


# -------------------------------------------------------------------- #
# Rolling windows                                                      #
# -------------------------------------------------------------------- #

@dataclass
class WindowMetrics:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr: float
    mdd: float
    vol: float
    sharpe: float
    sortino: float
    calmar: float


def rolling_metrics(daily_returns: pd.Series, nav: pd.Series,
                    window_months: int, step_months: int,
                    rf_annual: float) -> list[WindowMetrics]:
    """
    Per ogni finestra rolling calcola TUTTE le metriche di interesse.
    Il NAV della finestra viene ricostruito normalizzato a 1 al primo
    giorno della finestra (cosi' MDD e Calmar sono coerenti).
    """
    monthly_starts = pd.Series(daily_returns.index).groupby(
        daily_returns.index.to_period("M")
    ).min().values
    monthly_starts = pd.DatetimeIndex(monthly_starts)
    n_months = len(monthly_starts)

    out = []
    i = 0
    while i + window_months <= n_months:
        start_date = monthly_starts[i]
        end_month_idx = i + window_months - 1
        if end_month_idx + 1 < n_months:
            end_date = monthly_starts[end_month_idx + 1] - pd.Timedelta(days=1)
        else:
            end_date = daily_returns.index[-1]
        chunk_ret = daily_returns.loc[start_date:end_date]
        chunk_nav = (1 + chunk_ret).cumprod()
        if len(chunk_ret) < 50:
            i += step_months
            continue
        out.append(WindowMetrics(
            start=chunk_ret.index[0],
            end=chunk_ret.index[-1],
            cagr=cagr_from_nav(chunk_nav),
            mdd=max_drawdown_from_nav(chunk_nav),
            vol=annual_vol(chunk_ret),
            sharpe=sharpe_ratio(chunk_ret, rf_annual),
            sortino=sortino_ratio(chunk_ret, rf_annual),
            calmar=calmar_ratio(chunk_nav),
        ))
        i += step_months
    return out


def metrics_to_df(metrics: list[WindowMetrics]) -> pd.DataFrame:
    return pd.DataFrame({
        "start": [m.start for m in metrics],
        "end": [m.end for m in metrics],
        "cagr": [m.cagr for m in metrics],
        "mdd": [m.mdd for m in metrics],
        "vol": [m.vol for m in metrics],
        "sharpe": [m.sharpe for m in metrics],
        "sortino": [m.sortino for m in metrics],
        "calmar": [m.calmar for m in metrics],
    })


def percentiles(s: pd.Series, qs=(0.05, 0.25, 0.50, 0.75, 0.95)) -> dict:
    return {f"p{int(q*100)}": float(s.quantile(q)) for q in qs}


# -------------------------------------------------------------------- #
# Framework di valutazione "Batte il mercato?"                          #
# -------------------------------------------------------------------- #

def score_strategy(strategy_metrics: dict, benchmark_metrics: dict,
                   strategy_rolling: pd.DataFrame, benchmark_rolling: pd.DataFrame,
                   window_label: str) -> dict:
    """
    Applica il framework a 6+1 metriche per uno specifico orizzonte.
    Restituisce dict con: criterion -> {pass: bool, strategy_value, benchmark_value, note}.
    """
    s = strategy_metrics
    b = benchmark_metrics

    # 1. CAGR mediano rolling >= benchmark
    s_cagr = float(strategy_rolling["cagr"].median())
    b_cagr = float(benchmark_rolling["cagr"].median())
    cagr_pass = s_cagr >= b_cagr

    # 2. Win rate (% finestre in cui la strategia supera il benchmark per CAGR)
    n = min(len(strategy_rolling), len(benchmark_rolling))
    win_rate = float((strategy_rolling["cagr"].values[:n]
                      > benchmark_rolling["cagr"].values[:n]).mean())
    win_rate_pass = win_rate >= WIN_RATE_THRESHOLD

    # 3. Volatilita' annualizzata <= benchmark * 1.10 (full sample)
    s_vol = s["vol_annual_full"]
    b_vol = b["vol_annual_full"]
    vol_pass = s_vol <= b_vol * VOL_TOLERANCE

    # 4. MDD mediano rolling <= benchmark mediano (entro tolleranza)
    s_mdd_med = float(strategy_rolling["mdd"].median())
    b_mdd_med = float(benchmark_rolling["mdd"].median())
    # MDD sono numeri negativi: confronto |s| <= |b| * 1.10
    mdd_pass = abs(s_mdd_med) <= abs(b_mdd_med) * MDD_TOLERANCE

    # 5. Sharpe (full sample) >= benchmark
    s_sharpe = s["sharpe_full"]
    b_sharpe = b["sharpe_full"]
    sharpe_pass = s_sharpe >= b_sharpe

    # 6. Calmar (full sample) >= benchmark
    s_calmar = s["calmar_full"]
    b_calmar = b["calmar_full"]
    calmar_pass = s_calmar >= b_calmar

    # 7. Sortino (full sample) >= benchmark
    s_sortino = s["sortino_full"]
    b_sortino = b["sortino_full"]
    sortino_pass = s_sortino >= b_sortino

    return {
        "window": window_label,
        "criteria": {
            "cagr_mediano": {
                "pass": cagr_pass,
                "strategy": s_cagr,
                "benchmark": b_cagr,
                "rule": "CAGR mediano rolling >= benchmark",
            },
            "win_rate": {
                "pass": win_rate_pass,
                "strategy": win_rate,
                "benchmark": WIN_RATE_THRESHOLD,
                "rule": f"Win rate >= {WIN_RATE_THRESHOLD*100:.0f}%",
            },
            "volatility": {
                "pass": vol_pass,
                "strategy": s_vol,
                "benchmark": b_vol,
                "rule": f"Volatilita' <= benchmark x {VOL_TOLERANCE}",
            },
            "max_drawdown": {
                "pass": mdd_pass,
                "strategy": s_mdd_med,
                "benchmark": b_mdd_med,
                "rule": f"|MDD mediano| <= |benchmark| x {MDD_TOLERANCE}",
            },
            "sharpe": {
                "pass": sharpe_pass,
                "strategy": s_sharpe,
                "benchmark": b_sharpe,
                "rule": "Sharpe >= benchmark",
            },
            "calmar": {
                "pass": calmar_pass,
                "strategy": s_calmar,
                "benchmark": b_calmar,
                "rule": "Calmar >= benchmark",
            },
            "sortino": {
                "pass": sortino_pass,
                "strategy": s_sortino,
                "benchmark": b_sortino,
                "rule": "Sortino >= benchmark",
            },
        },
    }


def overall_verdict(scorecard: dict) -> str:
    """Vince/parziale/non-vince in base ai criteri passati."""
    n_pass = sum(1 for c in scorecard["criteria"].values() if c["pass"])
    if n_pass == 7:
        return "vince"
    if n_pass >= 4:
        return "parziale"
    return "non-vince"


# -------------------------------------------------------------------- #
# Grafici                                                              #
# -------------------------------------------------------------------- #

def _style_axes(ax, title: str, ylabel: str, xlabel: str = ""):
    ax.set_title(title, fontsize=14, fontweight="semibold", color="#0f172a", pad=14)
    ax.set_ylabel(ylabel, fontsize=11, color="#334155")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color="#334155")
    ax.tick_params(colors="#475569", labelsize=10)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#cbd5e1")
    ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.7)
    ax.set_axisbelow(True)


def plot_equity_curves(navs: dict, fname: Path):
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
    for label, nav in navs.items():
        ax.plot(nav.index, nav.values, color=COLORS.get(label, "#94a3b8"),
                linewidth=2.0, label=label)
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    _style_axes(
        ax,
        title="Crescita di 1 USD investito a marzo 1999 (scala log)",
        ylabel="NAV cumulato (scala log)",
    )
    ax.text(0.99, -0.13,
            "Fonte: yfinance (SPY/QQQ/XLE adjusted close). Buy & hold, no rebalancing.",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_boxplot_metric(rolling_per_port: dict, metric: str, ylabel: str,
                        scale: float, window_label: str, fname: Path,
                        center_zero: bool = False):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
    labels = list(rolling_per_port.keys())
    data = [rolling_per_port[k][metric].values * scale for k in labels]
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        widths=0.55,
        medianprops=dict(color="#0f172a", linewidth=2),
        whiskerprops=dict(color="#475569"),
        capprops=dict(color="#475569"),
        flierprops=dict(marker="o", markerfacecolor="#94a3b8",
                        markeredgecolor="none", markersize=4, alpha=0.5),
    )
    for patch, label in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS.get(label, "#94a3b8"))
        patch.set_alpha(0.85)
        patch.set_edgecolor("#0f172a")
    if center_zero:
        ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    _style_axes(
        ax,
        title=f"{ylabel} su finestre rolling {window_label}",
        ylabel=ylabel,
    )
    ax.text(0.99, -0.18,
            "Fonte: yfinance. Buy & hold. Step 6 mesi.",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_scorecard(scorecards_by_window: dict, fname: Path):
    """
    Heatmap-tabella con i 7 criteri (righe) per i due orizzonti (colonne),
    cella verde se passa, rossa se fallisce.
    """
    criteria_order = ["cagr_mediano", "win_rate", "volatility", "max_drawdown",
                      "sharpe", "calmar", "sortino"]
    criteria_labels = {
        "cagr_mediano": "CAGR mediano",
        "win_rate": "Win rate ≥ 60%",
        "volatility": "Volatilità ≤ 1.10×",
        "max_drawdown": "Max DD ≤ 1.10×",
        "sharpe": "Sharpe",
        "calmar": "Calmar",
        "sortino": "Sortino",
    }
    windows = list(scorecards_by_window.keys())
    n_rows = len(criteria_order)
    n_cols = len(windows)
    # Celle piu' larghe + altezza modesta -> meno overlap dei titoli colonna
    cell_w, cell_h = 1.8, 0.85
    fig_w = 4.0 + cell_w * n_cols
    fig_h = 1.5 + cell_h * n_rows
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    for j, win_label in enumerate(windows):
        criteria_data = scorecards_by_window[win_label]["criteria"]
        for i, crit in enumerate(criteria_order):
            passed = criteria_data[crit]["pass"]
            color = "#10b981" if passed else "#ef4444"
            symbol = "✓" if passed else "✗"
            rect = plt.Rectangle((j * cell_w, (n_rows - 1 - i) * cell_h),
                                 cell_w * 0.92, cell_h * 0.85,
                                 facecolor=color, alpha=0.88,
                                 edgecolor="white", linewidth=1.5)
            ax.add_patch(rect)
            ax.text(j * cell_w + cell_w * 0.46,
                    (n_rows - 1 - i) * cell_h + cell_h * 0.42,
                    symbol, ha="center", va="center",
                    fontsize=24, fontweight="bold", color="white")
    # Etichette righe (a sinistra)
    for i, crit in enumerate(criteria_order):
        ax.text(-0.15, (n_rows - 1 - i) * cell_h + cell_h * 0.42,
                criteria_labels[crit], ha="right", va="center",
                fontsize=11, color="#0f172a")
    # Etichette colonne (orizzonti) — splittate su 3 righe per evitare overlap
    for j, win_label in enumerate(windows):
        verdict = scorecards_by_window[win_label]["verdict"]
        n_pass = sum(1 for c in scorecards_by_window[win_label]["criteria"].values()
                     if c["pass"])
        verdict_color = {
            "vince": "#047857",
            "parziale": "#b45309",
            "non-vince": "#b91c1c",
        }.get(verdict, "#0f172a")
        x_center = j * cell_w + cell_w * 0.46
        # Riga 1: orizzonte
        ax.text(x_center, n_rows * cell_h + 0.55,
                f"Rolling {win_label}",
                ha="center", va="bottom",
                fontsize=12, fontweight="bold", color="#0f172a")
        # Riga 2: punteggio
        ax.text(x_center, n_rows * cell_h + 0.28,
                f"{n_pass}/7",
                ha="center", va="bottom",
                fontsize=11, fontweight="semibold", color="#475569")
        # Riga 3: verdetto
        ax.text(x_center, n_rows * cell_h + 0.05,
                verdict.upper(),
                ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=verdict_color)
    ax.set_xlim(-2.4, n_cols * cell_w + 0.3)
    ax.set_ylim(-0.4, n_rows * cell_h + 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"Scorecard — {STRATEGY_NAME} vs {BENCHMARK_NAME}",
        fontsize=15, fontweight="semibold", color="#0f172a", pad=18,
        loc="left", x=-0.05,
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def main():
    print("=" * 64)
    print("SmartMoneyLab — Mix Energy + Tech batte il mercato?")
    print("=" * 64)

    # 1. Carica prezzi
    prices = load_etf_daily(TICKERS)
    prices = prices.loc[START_DATE:END_DATE]
    print(f"Periodo effettivo: {prices.index.min().date()} -> {prices.index.max().date()}  "
          f"({len(prices)} giorni)")

    # 2. Costruisci NAV per ciascun portafoglio
    navs = {}
    daily_rets = {}
    for name, w in PORTFOLIOS.items():
        nav = build_buy_and_hold_nav(prices, w)
        navs[name] = nav
        daily_rets[name] = daily_returns_from_nav(nav)

    # 3. Statistiche full-sample
    print("\nStatistiche full-sample (buy & hold, no rebalancing):")
    full_metrics = {}
    for name, nav in navs.items():
        ret = daily_rets[name]
        m = {
            "cagr_full": cagr_from_nav(nav),
            "mdd_full": max_drawdown_from_nav(nav),
            "vol_annual_full": annual_vol(ret),
            "sharpe_full": sharpe_ratio(ret, RISK_FREE_ANNUAL),
            "sortino_full": sortino_ratio(ret, RISK_FREE_ANNUAL),
            "calmar_full": calmar_ratio(nav),
        }
        full_metrics[name] = m
        print(f"  {name:20s}  CAGR={m['cagr_full']*100:6.2f}%  "
              f"MDD={m['mdd_full']*100:7.2f}%  VOL={m['vol_annual_full']*100:5.2f}%  "
              f"Sharpe={m['sharpe_full']:5.2f}  Sortino={m['sortino_full']:5.2f}  "
              f"Calmar={m['calmar_full']:5.2f}")

    # 4. Rolling metrics per ogni portafoglio e finestra
    rolling_per_port = {wl: {} for wl in WINDOWS_MONTHS}
    for win_label, win_months in WINDOWS_MONTHS.items():
        print(f"\nRolling {win_label} (step {STEP_MONTHS}m):")
        for name in PORTFOLIOS:
            metrics = rolling_metrics(daily_rets[name], navs[name],
                                      win_months, STEP_MONTHS, RISK_FREE_ANNUAL)
            df = metrics_to_df(metrics)
            rolling_per_port[win_label][name] = df
            print(f"  {name:20s}: CAGR p50={df['cagr'].median()*100:5.2f}%  "
                  f"MDD p50={df['mdd'].median()*100:6.2f}%  "
                  f"Sharpe p50={df['sharpe'].median():4.2f}  "
                  f"({len(df)} finestre)")

    # 5. Scorecard del framework "Batte il mercato?"
    print(f"\n=== SCORECARD: {STRATEGY_NAME} vs {BENCHMARK_NAME} ===")
    scorecards = {}
    for win_label in WINDOWS_MONTHS:
        scorecard = score_strategy(
            full_metrics[STRATEGY_NAME],
            full_metrics[BENCHMARK_NAME],
            rolling_per_port[win_label][STRATEGY_NAME],
            rolling_per_port[win_label][BENCHMARK_NAME],
            win_label,
        )
        scorecard["verdict"] = overall_verdict(scorecard)
        scorecards[win_label] = scorecard
        print(f"\nFinestra {win_label}:")
        for crit_name, crit in scorecard["criteria"].items():
            mark = "✓" if crit["pass"] else "✗"
            s = crit["strategy"]
            b = crit["benchmark"]
            if isinstance(s, float) and abs(s) < 10:
                s_fmt = f"{s:7.4f}" if abs(s) < 1 else f"{s:7.2f}"
                b_fmt = f"{b:7.4f}" if abs(b) < 1 else f"{b:7.2f}"
            else:
                s_fmt = f"{s*100:6.2f}%" if isinstance(s, float) else str(s)
                b_fmt = f"{b*100:6.2f}%" if isinstance(b, float) else str(b)
            print(f"  [{mark}] {crit_name:15s}  strategy={s_fmt}  benchmark={b_fmt}  ({crit['rule']})")
        print(f"  -> VERDICT: {scorecard['verdict'].upper()}")

    # 6. Verdict aggregato (peggior caso tra orizzonti)
    verdicts_list = [s["verdict"] for s in scorecards.values()]
    if "non-vince" in verdicts_list:
        overall = "non-vince"
    elif "parziale" in verdicts_list:
        overall = "parziale"
    else:
        overall = "vince"
    print(f"\nVERDICT AGGREGATO (peggior caso): {overall.upper()}")

    # 7. Grafici
    print("\nGenerazione grafici…")
    plot_equity_curves(navs, OUT_DIR / "01_equity_curves.png")
    plot_boxplot_metric(rolling_per_port["10y"], "cagr",
                        "CAGR annualizzato (%)", 100, "10 anni",
                        OUT_DIR / "02_cagr_10y.png", center_zero=True)
    plot_boxplot_metric(rolling_per_port["5y"], "cagr",
                        "CAGR annualizzato (%)", 100, "5 anni",
                        OUT_DIR / "03_cagr_5y.png", center_zero=True)
    plot_boxplot_metric(rolling_per_port["10y"], "sharpe",
                        "Sharpe ratio", 1.0, "10 anni",
                        OUT_DIR / "04_sharpe_10y.png", center_zero=True)
    plot_scorecard(scorecards, OUT_DIR / "05_scorecard.png")

    # 8. Salva summary
    pct_results = {wl: {} for wl in WINDOWS_MONTHS}
    for wl in WINDOWS_MONTHS:
        for name, df in rolling_per_port[wl].items():
            pct_results[wl][name] = {
                "n_windows": int(len(df)),
                "cagr": percentiles(df["cagr"]),
                "mdd": percentiles(df["mdd"]),
                "sharpe": percentiles(df["sharpe"]),
                "sortino": percentiles(df["sortino"]),
                "calmar": percentiles(df["calmar"]),
            }

    summary = {
        "slug": SLUG,
        "title": "Mix Energy + Tech batte il mercato?",
        "strategy_name": STRATEGY_NAME,
        "benchmark_name": BENCHMARK_NAME,
        "period": {
            "start": str(prices.index.min().date()),
            "end": str(prices.index.max().date()),
            "n_days": int(len(prices)),
        },
        "params": {
            "tickers": TICKERS,
            "portfolios": PORTFOLIOS,
            "rolling_step_months": STEP_MONTHS,
            "windows_months": WINDOWS_MONTHS,
            "rebalancing": "none (buy & hold puro)",
            "risk_free_annual": RISK_FREE_ANNUAL,
            "win_rate_threshold": WIN_RATE_THRESHOLD,
            "vol_tolerance": VOL_TOLERANCE,
            "mdd_tolerance": MDD_TOLERANCE,
        },
        "full_sample": full_metrics,
        "rolling_percentiles": pct_results,
        "scorecards": scorecards,
        "overall_verdict": overall,
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    csv_df = pd.DataFrame(navs)
    csv_df = csv_df.resample("ME").last()
    csv_df.index.name = "date"
    csv_df.to_csv(OUT_DIR / "data.csv", float_format="%.6f")

    print(f"\nOutput salvati in: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
