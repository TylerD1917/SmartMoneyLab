"""
SmartMoneyLab — Una strategia LEAPS batte il mercato?
=====================================================

Confronto tra:

  (A) STRATEGIA LEAPS 70/30
      - 70% del capitale in Call Option LEAPS sull'S&P 500
        Strike: 85% dello spot all'apertura/roll (ITM, delta alto)
        Maturity: T = 2.0 anni all'apertura/roll
      - 30% del capitale in Treasury 10y total return (proxy duration-based)
      - Roll annuale dell'opzione: ogni 12 mesi liquidiamo a
        mark-to-market, riapriamo nuova LEAPS con strike 85% del nuovo
        spot, T = 2.0
      - Ribilanciamento annuale al 70/30 in coincidenza del roll
        ("valore" = premio mark-to-market dell'opzione, non nozionale
        delta-adjusted)
      - Pricing Black-Scholes europea con dividend yield continuo q

  (B) BUY & HOLD PURO 100% S&P 500 Total Return
      - Baseline, dividendi reinvestiti, niente leva, niente roll

Capitale iniziale: 10.000 €/$ (irrelevante per CAGR/MDD/Sharpe, conta
solo per gli importi nominali).

Volatilita' usata in BS: realized 252d annualizzata + spread +3 punti
percentuali (proxy del vol risk premium reale che il mercato delle
opzioni richiede sopra la realized vol). Decisione esplicita: senza
questo spread la strategia esce sovrastimata perche' BS con sola
realized vol regala il vol risk premium al compratore di opzioni.

Risk-free rate r:
  - DGS10 (FRED) dal 2001-01-02 in avanti
  - Shiller "Long Interest Rate" mensile, forward-filled, per il
    periodo pre-2001 (la serie Shiller e' un proxy del 10y Treasury
    yield, mensile dal 1871)

Dividend yield q: ricostruito da Shiller (Dividend annualizzato /
SP500), mensile -> forward-filled a daily.

Treasury 10y total return daily: approssimato col modello
duration-based standard:
  r_TR_t = y_{t-1}/252  -  D * (y_t - y_{t-1})
con D = 8.5 (duration tipica di un par-bond 10y). Termine di convexity
omesso (impatto < 5 bps/anno su un backtest di 50 anni).

Dati richiesti in data/cache/:
  - yahoo_gspc_daily.csv   (S&P 500 daily 1976+)
  - fred_dgs10.csv         (10y Treasury yield daily 2001+)
  - shiller_mirror.csv     (Shiller monthly: SP500, Dividend, Long Rate
                            dal 1871)

Rolling windows: 10y, 20y, 30y, step 3 mesi.

Output in public/charts/strategia-leaps-vs-buy-and-hold/:
  - 01_equity_curve_esempio.png
  - 02_cagr_boxplot_rolling.png
  - 03_maxdd_boxplot_rolling.png
  - 04_win_rate_per_finestra.png
  - 05_sharpe_calmar_boxplot.png
  - 06_distribuzione_outperformance.png
  - summary.json
  - rolling_windows.csv
  - equity_curve_full.csv

Dipendenze: pandas, numpy, matplotlib, scipy.
Installazione: pip install pandas numpy matplotlib scipy

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

# -------------------------------------------------------------------- #
# Setup percorsi                                                       #
# -------------------------------------------------------------------- #
SLUG = "strategia-leaps-vs-buy-and-hold"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------- #
# Parametri strategia                                                  #
# -------------------------------------------------------------------- #
INITIAL_CAPITAL = 10_000.0
WEIGHT_OPTIONS = 0.70
WEIGHT_BONDS = 0.30

LEAPS_MATURITY_YEARS = 2.0           # T iniziale di ogni nuova opzione
ROLL_INTERVAL_DAYS = 252             # ~12 mesi di trading
STRIKE_MONEYNESS = 0.85              # K = 0.85 * S al roll (ITM)

VOL_WINDOW_DAYS = 252                # finestra realized vol
VOL_PREMIUM = 0.03                   # +3pp sopra realized vol (vol risk premium)

BOND_DURATION = 8.5                  # duration del par 10y bond

# Rolling windows (in giorni di trading, ~252/anno)
WINDOWS = {"10y": 10 * 252, "20y": 20 * 252, "30y": 30 * 252}
STEP_DAYS = 63                       # ~3 mesi di trading

# Risk-free rate "default" per Sharpe (CAGR del 10y Treasury sul periodo)
# Calcolato dinamicamente dai dati: media del DGS10 sul periodo della finestra.

# Palette SmartMoneyLab (navy, ambra, grigio)
COLOR_LEAPS = "#d97706"     # ambra (strategia attiva)
COLOR_BH = "#1e3a8a"        # navy (baseline)
COLOR_NEUTRAL = "#6b7280"   # grigio


# -------------------------------------------------------------------- #
# Caricamento dati                                                     #
# -------------------------------------------------------------------- #
def load_sp500_price() -> pd.Series:
    path = CACHE_DIR / "yahoo_gspc_daily.csv"
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
    s = pd.to_numeric(df["Close"], errors="coerce").dropna()
    s.name = "sp500"
    return s


def load_fred_dgs10() -> pd.Series:
    path = CACHE_DIR / "fred_dgs10.csv"
    df = pd.read_csv(path, parse_dates=["observation_date"])
    df = df.set_index("observation_date").sort_index()
    s = pd.to_numeric(df["DGS10"], errors="coerce").dropna() / 100.0
    s.name = "dgs10"
    return s


def load_shiller_monthly() -> pd.DataFrame:
    """
    Shiller monthly. Restituisce DataFrame con:
      - sp500_price (SP500 column)
      - dividend_annual (Dividend column, dividendo annualizzato per share)
      - long_rate (Long Interest Rate column, in decimale: 5.32 -> 0.0532)
    Indicizzato al primo del mese.
    """
    path = CACHE_DIR / "shiller_mirror.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["Date"]).dt.to_period("M").dt.to_timestamp()
    df = df.set_index("date").sort_index()
    out = pd.DataFrame({
        "sp500_price": pd.to_numeric(df["SP500"], errors="coerce"),
        "dividend_annual": pd.to_numeric(df["Dividend"], errors="coerce"),
        "long_rate": pd.to_numeric(df["Long Interest Rate"], errors="coerce") / 100.0,
    }).dropna()
    return out


# -------------------------------------------------------------------- #
# Costruzione serie daily                                              #
# -------------------------------------------------------------------- #
def build_daily_panel() -> pd.DataFrame:
    """
    Pannello daily con:
      - sp500           : prezzo daily S&P 500 (Yahoo)
      - sp500_tr_daily  : rendimento daily total return S&P
      - sp500_tr_nav    : NAV cumulato S&P TR (parte da 1)
      - div_yield       : dividend yield S&P (continuo) — forward fill da Shiller
      - rf              : risk-free rate daily (DGS10 da 2001, Shiller pre-2001)
      - real_vol_252d   : volatilita' realized annualizzata su 252d
      - bond_yield      : yield 10y per costruzione Treasury TR (= rf)
      - bond_tr_daily   : rendimento daily Treasury 10y TR (duration model)
      - bond_tr_nav     : NAV cumulato Treasury TR
    """
    price = load_sp500_price()
    dgs10 = load_fred_dgs10()
    shiller = load_shiller_monthly()

    # Universo daily = giorni di trading di S&P
    daily_idx = price.index

    # ---- Dividend yield continuo q ---- #
    # Shiller "Dividend" e' il dividendo annualizzato per share del mese.
    # Yield continuo q = ln(1 + D/P).
    div_yield_monthly = np.log(1.0 + shiller["dividend_annual"] / shiller["sp500_price"])
    # forward fill a daily
    div_yield_daily = div_yield_monthly.reindex(
        daily_idx.union(div_yield_monthly.index)
    ).sort_index().ffill().reindex(daily_idx)

    # ---- Risk-free rate r daily ---- #
    # DGS10 quando disponibile, altrimenti Shiller long_rate mensile ffill
    shiller_rate_daily = shiller["long_rate"].reindex(
        daily_idx.union(shiller["long_rate"].index)
    ).sort_index().ffill().reindex(daily_idx)
    dgs10_daily = dgs10.reindex(daily_idx).ffill()
    rf = dgs10_daily.where(dgs10_daily.notna(), shiller_rate_daily)
    rf = rf.ffill().bfill()

    # ---- S&P 500 TR daily ---- #
    # Approx: rendimento daily TR = (P_t + D_t/252) / P_{t-1} - 1
    # con D_t = dividendo annualizzato Shiller del mese di t.
    div_amount_annual = (shiller["dividend_annual"].reindex(
        daily_idx.union(shiller.index)
    ).sort_index().ffill().reindex(daily_idx))
    # Ratio dividendo Shiller / SP500 Shiller mantiene proporzioni anche su
    # livelli Yahoo (Shiller usa indice ricostruito vs Yahoo divisor). Quindi
    # usiamo dividend YIELD per costruire il TR, piu' robusto:
    daily_yield = div_yield_daily / 252.0  # quota daily del dividend yield
    sp500_tr_daily = (price / price.shift(1) - 1) + daily_yield
    sp500_tr_daily = sp500_tr_daily.dropna()
    sp500_tr_nav = (1 + sp500_tr_daily).cumprod()
    sp500_tr_nav.iloc[0] = 1.0  # forza partenza a 1

    # ---- Realized vol 252d ---- #
    log_ret = np.log(price / price.shift(1)).dropna()
    real_vol = log_ret.rolling(VOL_WINDOW_DAYS).std() * np.sqrt(252)
    real_vol = real_vol.reindex(daily_idx).ffill()

    # ---- Treasury 10y TR daily (duration model) ---- #
    # Convenzione: y in decimale. r_TR_t = y_{t-1}/252 - D * (y_t - y_{t-1}).
    y = rf.copy()
    bond_tr_daily = (y.shift(1) / 252.0) - BOND_DURATION * (y - y.shift(1))
    bond_tr_daily = bond_tr_daily.dropna()
    bond_tr_nav = (1 + bond_tr_daily).cumprod()

    panel = pd.DataFrame({
        "sp500": price,
        "sp500_tr_daily": sp500_tr_daily,
        "sp500_tr_nav": sp500_tr_nav,
        "div_yield": div_yield_daily,
        "rf": rf,
        "real_vol_252d": real_vol,
        "bond_tr_daily": bond_tr_daily,
        "bond_tr_nav": bond_tr_nav,
    })
    panel = panel.dropna(subset=["sp500", "rf", "div_yield", "real_vol_252d",
                                  "bond_tr_daily"])
    return panel


# -------------------------------------------------------------------- #
# Black-Scholes europea con dividend yield continuo                    #
# -------------------------------------------------------------------- #
def bs_call_price(S: float, K: float, T: float, r: float, q: float,
                  sigma: float) -> float:
    """Prezzo BS di una call europea con dividend yield continuo."""
    if T <= 0:
        return max(S - K, 0.0)
    if sigma <= 0:
        return max(S * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


# -------------------------------------------------------------------- #
# Simulazione strategia LEAPS                                          #
# -------------------------------------------------------------------- #
@dataclass
class LeapsOutput:
    nav: pd.Series              # NAV totale del portafoglio
    options_value: pd.Series    # valore della parte opzioni nel tempo
    bond_value: pd.Series       # valore della parte bond nel tempo
    rolls: list                 # lista (data, S_roll, K_new, premio_new)


def simulate_leaps_strategy(panel: pd.DataFrame) -> LeapsOutput:
    """
    Simulazione daily della strategia LEAPS 70/30 con roll annuale.

    Logica:
      t=0:  S_0, q_0, r_0, sigma_0 = realized + premium
            K = STRIKE_MONEYNESS * S_0
            T = 2.0
            premio_0 = BS_call(S_0, K, T, r_0, q_0, sigma_0)
            n_contracts = (WEIGHT_OPTIONS * capital) / premio_0
            bond_value = WEIGHT_BONDS * capital
            time_to_roll = ROLL_INTERVAL_DAYS

      t=k:  S_k, q_k, r_k, sigma_k
            T_residual = T - dt_dal_open_anni
            premio_k = BS_call(S_k, K, T_residual, r_k, q_k, sigma_k)
            options_value = n_contracts * premio_k
            bond_value *= (1 + bond_tr_daily[k])
            portfolio_value = options_value + bond_value

      Roll (ogni ROLL_INTERVAL_DAYS):
            options_proceeds = n_contracts * premio_k_pre_roll
            total = options_proceeds + bond_value
            bond_value = WEIGHT_BONDS * total                  (ribilanciamento)
            target_options_cash = WEIGHT_OPTIONS * total
            K_new = STRIKE_MONEYNESS * S_k
            premio_new = BS_call(S_k, K_new, 2.0, r_k, q_k, sigma_k)
            n_contracts_new = target_options_cash / premio_new
            tempo dell'opzione resettato a T = 2.0
    """
    idx = panel.index
    n = len(idx)

    # Stato iniziale
    capital = INITIAL_CAPITAL
    S0 = panel["sp500"].iloc[0]
    q0 = panel["div_yield"].iloc[0]
    r0 = panel["rf"].iloc[0]
    sigma0 = panel["real_vol_252d"].iloc[0] + VOL_PREMIUM

    K = STRIKE_MONEYNESS * S0
    T_total = LEAPS_MATURITY_YEARS
    open_idx = 0                                           # indice giorno apertura attuale
    premio_open = bs_call_price(S0, K, T_total, r0, q0, sigma0)
    n_contracts = (WEIGHT_OPTIONS * capital) / premio_open
    bond_value = WEIGHT_BONDS * capital

    rolls = [(idx[0], float(S0), float(K), float(premio_open),
              float(sigma0), float(r0), float(q0))]

    nav_arr = np.zeros(n)
    opt_arr = np.zeros(n)
    bond_arr = np.zeros(n)

    nav_arr[0] = capital
    opt_arr[0] = WEIGHT_OPTIONS * capital
    bond_arr[0] = bond_value

    for k in range(1, n):
        # 1) bond accrual giornaliero
        bond_value = bond_value * (1 + panel["bond_tr_daily"].iloc[k])

        # 2) mark-to-market opzione
        S_k = panel["sp500"].iloc[k]
        q_k = panel["div_yield"].iloc[k]
        r_k = panel["rf"].iloc[k]
        sigma_k = panel["real_vol_252d"].iloc[k] + VOL_PREMIUM
        days_since_open = k - open_idx
        T_residual = max(T_total - days_since_open / 252.0, 1e-6)
        premio_k = bs_call_price(S_k, K, T_residual, r_k, q_k, sigma_k)
        options_value = n_contracts * premio_k

        portfolio_value = options_value + bond_value
        nav_arr[k] = portfolio_value
        opt_arr[k] = options_value
        bond_arr[k] = bond_value

        # 3) roll annuale
        if days_since_open >= ROLL_INTERVAL_DAYS:
            options_proceeds = options_value
            total = options_proceeds + bond_value
            bond_value = WEIGHT_BONDS * total
            target_opt_cash = WEIGHT_OPTIONS * total
            K = STRIKE_MONEYNESS * S_k
            premio_open = bs_call_price(S_k, K, LEAPS_MATURITY_YEARS, r_k, q_k, sigma_k)
            n_contracts = target_opt_cash / premio_open
            open_idx = k
            rolls.append((idx[k], float(S_k), float(K), float(premio_open),
                          float(sigma_k), float(r_k), float(q_k)))

    nav = pd.Series(nav_arr, index=idx, name="leaps_nav")
    opt = pd.Series(opt_arr, index=idx, name="leaps_options_value")
    bnd = pd.Series(bond_arr, index=idx, name="leaps_bond_value")
    return LeapsOutput(nav=nav, options_value=opt, bond_value=bnd, rolls=rolls)


def simulate_bh_strategy(panel: pd.DataFrame) -> pd.Series:
    """Buy & hold puro 100% S&P TR. Capitale iniziale identico."""
    tr_nav = panel["sp500_tr_nav"]
    nav = INITIAL_CAPITAL * tr_nav / tr_nav.iloc[0]
    nav.name = "bh_nav"
    return nav


# -------------------------------------------------------------------- #
# Metriche su NAV                                                      #
# -------------------------------------------------------------------- #
def cagr_from_nav(nav: pd.Series) -> float:
    if len(nav) < 2 or nav.iloc[0] <= 0 or nav.iloc[-1] <= 0:
        return float("nan")
    growth = nav.iloc[-1] / nav.iloc[0]
    years = len(nav) / 252.0
    if growth <= 0:
        return float("nan")
    return float(growth ** (1.0 / years) - 1)


def max_drawdown(nav: pd.Series) -> float:
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def annual_vol(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    return float(rets.std() * np.sqrt(252))


def sharpe_ratio(nav: pd.Series, rf_series: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    rf_daily = rf_series.reindex(rets.index).ffill() / 252.0
    excess = rets - rf_daily
    if excess.std() == 0:
        return float("nan")
    return float(excess.mean() / excess.std() * np.sqrt(252))


def sortino_ratio(nav: pd.Series, rf_series: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    rf_daily = rf_series.reindex(rets.index).ffill() / 252.0
    excess = rets - rf_daily
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("nan")
    return float(excess.mean() / downside.std() * np.sqrt(252))


def calmar_ratio(nav: pd.Series) -> float:
    mdd = abs(max_drawdown(nav))
    if mdd == 0:
        return float("nan")
    return cagr_from_nav(nav) / mdd


@dataclass
class WindowMetrics:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr_leaps: float
    cagr_bh: float
    mdd_leaps: float
    mdd_bh: float
    vol_leaps: float
    vol_bh: float
    sharpe_leaps: float
    sharpe_bh: float
    sortino_leaps: float
    sortino_bh: float
    calmar_leaps: float
    calmar_bh: float


# -------------------------------------------------------------------- #
# Rolling windows                                                      #
# -------------------------------------------------------------------- #
def rolling_windows_analysis(panel: pd.DataFrame, window_label: str,
                              window_days: int) -> list[WindowMetrics]:
    """
    Per ogni finestra rolling di lunghezza `window_days` giorni di
    trading, step `STEP_DAYS`, ricostruisce da zero LEAPS e B&H e
    calcola tutte le metriche.
    """
    n = len(panel)
    out: list[WindowMetrics] = []
    i = 0
    while i + window_days <= n:
        sub = panel.iloc[i:i + window_days].copy()
        # Rebuild NAV bond e SP_TR partendo da 1 in questa finestra
        sub["sp500_tr_nav"] = (1 + sub["sp500_tr_daily"]).cumprod()
        sub.loc[sub.index[0], "sp500_tr_nav"] = 1.0
        sub["bond_tr_nav"] = (1 + sub["bond_tr_daily"]).cumprod()
        sub.loc[sub.index[0], "bond_tr_nav"] = 1.0

        leaps = simulate_leaps_strategy(sub)
        bh = simulate_bh_strategy(sub)

        wm = WindowMetrics(
            start=sub.index[0], end=sub.index[-1],
            cagr_leaps=cagr_from_nav(leaps.nav),
            cagr_bh=cagr_from_nav(bh),
            mdd_leaps=max_drawdown(leaps.nav),
            mdd_bh=max_drawdown(bh),
            vol_leaps=annual_vol(leaps.nav),
            vol_bh=annual_vol(bh),
            sharpe_leaps=sharpe_ratio(leaps.nav, sub["rf"]),
            sharpe_bh=sharpe_ratio(bh, sub["rf"]),
            sortino_leaps=sortino_ratio(leaps.nav, sub["rf"]),
            sortino_bh=sortino_ratio(bh, sub["rf"]),
            calmar_leaps=calmar_ratio(leaps.nav),
            calmar_bh=calmar_ratio(bh),
        )
        out.append(wm)
        i += STEP_DAYS

    print(f"  [{window_label}] {len(out)} finestre rolling")
    return out


# -------------------------------------------------------------------- #
# Plot                                                                 #
# -------------------------------------------------------------------- #
def _set_style():
    plt.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })


def plot_equity_curve(panel: pd.DataFrame, leaps: LeapsOutput,
                       bh: pd.Series, out_path: Path):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(bh.index, bh.values, color=COLOR_BH, lw=1.8,
            label="Buy & Hold S&P 500 TR")
    ax.plot(leaps.nav.index, leaps.nav.values, color=COLOR_LEAPS, lw=1.8,
            label="Strategia LEAPS 70/30")
    ax.set_yscale("log")
    ax.set_title("NAV cumulato — periodo completo (scala log)")
    ax.set_ylabel("NAV (capitale iniziale = 10.000)")
    ax.set_xlabel("")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_cagr_boxplot(results: dict[str, list[WindowMetrics]], out_path: Path):
    labels = list(results.keys())
    data_leaps = [[w.cagr_leaps for w in results[l] if not np.isnan(w.cagr_leaps)]
                  for l in labels]
    data_bh = [[w.cagr_bh for w in results[l] if not np.isnan(w.cagr_bh)]
               for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    positions_leaps = np.arange(len(labels)) - 0.2
    positions_bh = np.arange(len(labels)) + 0.2
    bp1 = ax.boxplot(data_leaps, positions=positions_leaps, widths=0.35,
                     patch_artist=True, showfliers=True)
    bp2 = ax.boxplot(data_bh, positions=positions_bh, widths=0.35,
                     patch_artist=True, showfliers=True)
    for box in bp1["boxes"]:
        box.set(facecolor=COLOR_LEAPS, alpha=0.6)
    for box in bp2["boxes"]:
        box.set(facecolor=COLOR_BH, alpha=0.6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("CAGR")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
    ax.set_title("Distribuzione CAGR su finestre rolling")
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOR_LEAPS, alpha=0.6),
               plt.Rectangle((0, 0), 1, 1, color=COLOR_BH, alpha=0.6)]
    ax.legend(handles, ["LEAPS 70/30", "B&H S&P TR"], loc="upper right",
              frameon=False)
    ax.axhline(0, color="black", lw=0.6)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_mdd_boxplot(results: dict[str, list[WindowMetrics]], out_path: Path):
    labels = list(results.keys())
    data_leaps = [[w.mdd_leaps for w in results[l] if not np.isnan(w.mdd_leaps)]
                  for l in labels]
    data_bh = [[w.mdd_bh for w in results[l] if not np.isnan(w.mdd_bh)]
               for l in labels]
    fig, ax = plt.subplots(figsize=(10, 6))
    positions_leaps = np.arange(len(labels)) - 0.2
    positions_bh = np.arange(len(labels)) + 0.2
    bp1 = ax.boxplot(data_leaps, positions=positions_leaps, widths=0.35,
                     patch_artist=True, showfliers=True)
    bp2 = ax.boxplot(data_bh, positions=positions_bh, widths=0.35,
                     patch_artist=True, showfliers=True)
    for box in bp1["boxes"]:
        box.set(facecolor=COLOR_LEAPS, alpha=0.6)
    for box in bp2["boxes"]:
        box.set(facecolor=COLOR_BH, alpha=0.6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Max drawdown")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
    ax.set_title("Max drawdown su finestre rolling")
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOR_LEAPS, alpha=0.6),
               plt.Rectangle((0, 0), 1, 1, color=COLOR_BH, alpha=0.6)]
    ax.legend(handles, ["LEAPS 70/30", "B&H S&P TR"], loc="lower right",
              frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_win_rate(results: dict[str, list[WindowMetrics]], out_path: Path):
    labels = list(results.keys())
    win_rates = []
    avg_outperf = []
    for l in labels:
        diff = [w.cagr_leaps - w.cagr_bh for w in results[l]
                if not np.isnan(w.cagr_leaps) and not np.isnan(w.cagr_bh)]
        wr = sum(1 for d in diff if d > 0) / len(diff) if diff else float("nan")
        win_rates.append(wr)
        avg_outperf.append(np.mean(diff) if diff else float("nan"))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, [wr * 100 for wr in win_rates],
                  color=COLOR_LEAPS, alpha=0.8)
    for bar, wr, op in zip(bars, win_rates, avg_outperf):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1,
                f"{wr*100:.0f}%\n(media Δ {op*100:+.1f}pp)",
                ha="center", va="bottom", fontsize=10)
    ax.axhline(50, color="black", lw=0.6, ls="--")
    ax.set_ylabel("Win rate LEAPS vs B&H (%)")
    ax.set_title("Quota di finestre rolling in cui LEAPS batte B&H (CAGR)")
    ax.set_ylim(0, max([wr * 100 for wr in win_rates]) * 1.25 + 10)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_sharpe_calmar(results: dict[str, list[WindowMetrics]], out_path: Path):
    labels = list(results.keys())
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, metric, title in zip(
        axes, ["sharpe", "calmar"], ["Sharpe ratio", "Calmar ratio"]
    ):
        data_leaps = [[getattr(w, f"{metric}_leaps") for w in results[l]
                       if not np.isnan(getattr(w, f"{metric}_leaps"))]
                      for l in labels]
        data_bh = [[getattr(w, f"{metric}_bh") for w in results[l]
                    if not np.isnan(getattr(w, f"{metric}_bh"))]
                   for l in labels]
        positions_leaps = np.arange(len(labels)) - 0.2
        positions_bh = np.arange(len(labels)) + 0.2
        bp1 = ax.boxplot(data_leaps, positions=positions_leaps, widths=0.35,
                         patch_artist=True, showfliers=True)
        bp2 = ax.boxplot(data_bh, positions=positions_bh, widths=0.35,
                         patch_artist=True, showfliers=True)
        for box in bp1["boxes"]:
            box.set(facecolor=COLOR_LEAPS, alpha=0.6)
        for box in bp2["boxes"]:
            box.set(facecolor=COLOR_BH, alpha=0.6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_title(title)
        ax.axhline(0, color="black", lw=0.6)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOR_LEAPS, alpha=0.6),
               plt.Rectangle((0, 0), 1, 1, color=COLOR_BH, alpha=0.6)]
    fig.legend(handles, ["LEAPS 70/30", "B&H S&P TR"], loc="upper center",
               ncol=2, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path)
    plt.close(fig)


def plot_outperformance_distribution(results: dict[str, list[WindowMetrics]],
                                       out_path: Path):
    labels = list(results.keys())
    fig, axes = plt.subplots(1, len(labels), figsize=(5 * len(labels), 5),
                              sharey=True)
    if len(labels) == 1:
        axes = [axes]
    for ax, l in zip(axes, labels):
        diff = [(w.cagr_leaps - w.cagr_bh) * 100 for w in results[l]
                if not np.isnan(w.cagr_leaps) and not np.isnan(w.cagr_bh)]
        ax.hist(diff, bins=20, color=COLOR_LEAPS, alpha=0.7, edgecolor="white")
        ax.axvline(0, color="black", lw=1.2)
        ax.axvline(np.mean(diff), color=COLOR_BH, lw=1.5, ls="--",
                   label=f"media {np.mean(diff):+.1f}pp")
        ax.set_title(f"Rolling {l}")
        ax.set_xlabel("Δ CAGR LEAPS − B&H (pp)")
        ax.legend(loc="upper right", frameon=False)
    axes[0].set_ylabel("Numero di finestre")
    fig.suptitle("Distribuzione dell'outperformance LEAPS sui rolling rispetto a B&H")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #
def main():
    _set_style()
    print(f"\n=== {SLUG} ===\n")

    print("[1/5] Caricamento dati...")
    panel = build_daily_panel()
    print(f"      Panel daily: {panel.index[0].date()} -> {panel.index[-1].date()} "
          f"({len(panel)} giorni)")

    print("\n[2/5] Simulazione strategia LEAPS sull'intero periodo...")
    leaps_full = simulate_leaps_strategy(panel)
    bh_full = simulate_bh_strategy(panel)
    print(f"      LEAPS NAV finale: {leaps_full.nav.iloc[-1]:,.0f}")
    print(f"      B&H   NAV finale: {bh_full.iloc[-1]:,.0f}")
    print(f"      LEAPS CAGR: {cagr_from_nav(leaps_full.nav)*100:+.2f}%   "
          f"MDD: {max_drawdown(leaps_full.nav)*100:+.1f}%")
    print(f"      B&H   CAGR: {cagr_from_nav(bh_full)*100:+.2f}%   "
          f"MDD: {max_drawdown(bh_full)*100:+.1f}%")
    print(f"      N. roll annuali eseguiti: {len(leaps_full.rolls)}")

    print("\n[3/5] Rolling windows analysis...")
    results: dict[str, list[WindowMetrics]] = {}
    for label, win in WINDOWS.items():
        if win > len(panel):
            print(f"      [{label}] saltata, dati insufficienti")
            continue
        results[label] = rolling_windows_analysis(panel, label, win)

    print("\n[4/5] Plot...")
    plot_equity_curve(panel, leaps_full, bh_full,
                      OUT_DIR / "01_equity_curve_esempio.png")
    plot_cagr_boxplot(results, OUT_DIR / "02_cagr_boxplot_rolling.png")
    plot_mdd_boxplot(results, OUT_DIR / "03_maxdd_boxplot_rolling.png")
    plot_win_rate(results, OUT_DIR / "04_win_rate_per_finestra.png")
    plot_sharpe_calmar(results, OUT_DIR / "05_sharpe_calmar_boxplot.png")
    plot_outperformance_distribution(
        results, OUT_DIR / "06_distribuzione_outperformance.png")

    print("\n[5/5] Salvataggio CSV e JSON...")
    # CSV per finestra
    rows = []
    for label, lst in results.items():
        for w in lst:
            r = asdict(w)
            r["window"] = label
            r["start"] = str(w.start.date())
            r["end"] = str(w.end.date())
            rows.append(r)
    pd.DataFrame(rows).to_csv(OUT_DIR / "rolling_windows.csv", index=False)

    # Equity curve completa
    pd.DataFrame({
        "leaps_nav": leaps_full.nav,
        "leaps_options_value": leaps_full.options_value,
        "leaps_bond_value": leaps_full.bond_value,
        "bh_nav": bh_full,
    }).to_csv(OUT_DIR / "equity_curve_full.csv")

    # Summary JSON
    def _q(arr, qs=(5, 25, 50, 75, 95)):
        if not arr:
            return {}
        return {f"p{q}": float(np.percentile(arr, q)) for q in qs}

    summary = {
        "slug": SLUG,
        "periodo": {
            "inizio": str(panel.index[0].date()),
            "fine": str(panel.index[-1].date()),
            "giorni_trading": int(len(panel)),
        },
        "parametri": {
            "capitale_iniziale": INITIAL_CAPITAL,
            "peso_opzioni": WEIGHT_OPTIONS,
            "peso_bond": WEIGHT_BONDS,
            "maturity_leaps_anni": LEAPS_MATURITY_YEARS,
            "strike_moneyness": STRIKE_MONEYNESS,
            "roll_interval_giorni": ROLL_INTERVAL_DAYS,
            "vol_window_giorni": VOL_WINDOW_DAYS,
            "vol_premium_pp": VOL_PREMIUM,
            "bond_duration": BOND_DURATION,
            "step_days": STEP_DAYS,
        },
        "full_period": {
            "leaps_nav_finale": float(leaps_full.nav.iloc[-1]),
            "bh_nav_finale": float(bh_full.iloc[-1]),
            "leaps_cagr": cagr_from_nav(leaps_full.nav),
            "bh_cagr": cagr_from_nav(bh_full),
            "leaps_mdd": max_drawdown(leaps_full.nav),
            "bh_mdd": max_drawdown(bh_full),
            "leaps_vol": annual_vol(leaps_full.nav),
            "bh_vol": annual_vol(bh_full),
            "leaps_sharpe": sharpe_ratio(leaps_full.nav, panel["rf"]),
            "bh_sharpe": sharpe_ratio(bh_full, panel["rf"]),
            "leaps_sortino": sortino_ratio(leaps_full.nav, panel["rf"]),
            "bh_sortino": sortino_ratio(bh_full, panel["rf"]),
            "leaps_calmar": calmar_ratio(leaps_full.nav),
            "bh_calmar": calmar_ratio(bh_full),
            "n_rolls": len(leaps_full.rolls),
        },
        "rolling": {},
    }
    for label, lst in results.items():
        diffs = [w.cagr_leaps - w.cagr_bh for w in lst
                 if not np.isnan(w.cagr_leaps) and not np.isnan(w.cagr_bh)]
        win_rate = sum(1 for d in diffs if d > 0) / len(diffs) if diffs else None
        summary["rolling"][label] = {
            "n_finestre": len(lst),
            "leaps_cagr_percentili": _q([w.cagr_leaps for w in lst
                                         if not np.isnan(w.cagr_leaps)]),
            "bh_cagr_percentili": _q([w.cagr_bh for w in lst
                                      if not np.isnan(w.cagr_bh)]),
            "leaps_mdd_percentili": _q([w.mdd_leaps for w in lst
                                        if not np.isnan(w.mdd_leaps)]),
            "bh_mdd_percentili": _q([w.mdd_bh for w in lst
                                     if not np.isnan(w.mdd_bh)]),
            "leaps_sharpe_percentili": _q([w.sharpe_leaps for w in lst
                                            if not np.isnan(w.sharpe_leaps)]),
            "bh_sharpe_percentili": _q([w.sharpe_bh for w in lst
                                        if not np.isnan(w.sharpe_bh)]),
            "win_rate_leaps_vs_bh": win_rate,
            "outperformance_media_pp": float(np.mean(diffs) * 100) if diffs else None,
        }

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print(f"\n      Output in: {OUT_DIR}")
    print("      File generati:")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"        - {p.name}")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
