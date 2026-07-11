"""
SmartMoneyLab — Regimi di tassi Fed e rendimenti S&P 500 / NASDAQ
=================================================================

Domanda: come varia il rendimento contemporaneo e forward dell'S&P 500
(Total Return) e del NASDAQ Composite (Price Return + dividendo conservativo)
al variare del regime dei tassi Fed Funds?

Tre definizioni di "regime" applicate in parallelo:
  A. LIVELLO NOMINALE — 5 bucket assoluti (<2%, 2-4%, 4-6%, 6-8%, >8%)
  B. DIREZIONE — variazione FFR trailing 12m (rialzo, stabile, discesa)
  C. LIVELLO REALE — FFR - CPI YoY, 4 bucket

Per ogni regime si calcolano:
  * rendimenti mensili contemporanei (dei mesi in quel regime)
  * rendimenti cumulati forward 12m e 24m
  * media, mediana, deviazione standard, Sharpe annualizzati

Event study aggiuntivo: inizio ciclo di HIKING (primo aumento >= +0.5pp
dopo >= 12 mesi di stabilita' o taglio) e inizio ciclo di CUTTING
(specularmente). Curve cumulate +/-24m attorno a t=0.

DATI (tutti in data/cache/)
---------------------------
  FEDFUNDS.csv         — Fed Funds monthly 1954-2026 (FRED)
  shiller_mirror.csv   — SP500 monthly + Dividend + CPI (Shiller). Dividend
                         copre 1871-2023-06; CPI copre 1871-2023-09.
                         Post-2023 il dividendo viene estrapolato al
                         DIV_YIELD_APPROX (yield conservativo annualizzato).
  NASDAQCOM.csv        — NASDAQ Composite daily 1971-2026 (FRED)

METODOLOGIA
-----------
  * S&P 500 TR ricostruito con formula Shiller: r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1
  * NASDAQ TR-proxy: rendimento mensile del NASDAQCOM + NASDAQ_DIV_MONTHLY
    (0.75%/12 = 0.0625% mensile costante — approssimazione conservativa
    rispetto al div yield storico di ~1%/y del Composite negli ultimi 20y).
  * FFR mensile: media del mese direttamente da FRED.
  * CPI YoY: variation percentuale a 12m di 'Consumer Price Index' Shiller.
  * Tasso reale: FFR - CPI_YoY (analisi C limitata al 2023-09).
  * Rendimenti forward: 12m = prod(1+r) su 12 mesi successivi.

OUTPUT in public/charts/regimi-tassi-sp500-nasdaq/
--------------------------------------------------
  01_context_timeline.png             FFR + S&P + NASDAQ log nel tempo
  02_regime_A_livello_boxplot.png     rendimenti mensili per livello nominale
  03_regime_A_forward12m.png          rendimenti forward 12m per livello
  04_regime_B_direzione_boxplot.png   rendimenti per direzione trailing
  05_regime_B_forward12m.png          forward 12m per direzione
  06_regime_C_reale_boxplot.png       rendimenti per livello reale
  07_regime_C_forward12m.png          forward 12m per livello reale
  08_event_hiking_cycles.png          event study inizio cicli rialzo +/-24m
  09_event_cutting_cycles.png         event study inizio cicli taglio +/-24m
  10_scatter_ffr_vs_forward12m.png    correlazione + retta OLS
  11_forward_horizons_by_regime.png   panel 12m/24m per regime A

  summary.json                        tutti i numeri per l'articolo
  monthly_panel.csv                   panel mensile completo
  regime_stats_long.csv               statistiche per bucket in long format
  pivot_dates.csv                     date dei pivot Fed identificati
  equity_curves_full.csv              per il reel (S&P TR + NASDAQ curves)

Uso locale (nessuna dipendenza da rete — solo CSV in cache):
    python scripts/regimi-tassi-sp500-nasdaq.py

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------- #
# Path e parametri                                                      #
# --------------------------------------------------------------------- #
SLUG = "regimi-tassi-sp500-nasdaq"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Dividendo NASDAQ Composite: approssimazione conservativa 0.75%/anno
# (media storica ~1% negli ultimi 20 anni, <0.5% negli anni tech-boom).
NASDAQ_DIV_ANNUAL = 0.0075
NASDAQ_DIV_MONTHLY = (1 + NASDAQ_DIV_ANNUAL) ** (1 / 12) - 1

# Yield SP500 per estrapolazione post-Shiller (2023-07 → 2026)
# Media dividend yield SP500 ultimi 5 anni ~1.4%
SP500_DIV_YIELD_APPROX_ANNUAL = 0.014

# Risk-free per Sharpe: 2% costante (coerente altri articoli)
RF = 0.02

# Regime A — livello nominale FFR
LEVEL_BINS = [-0.01, 2.0, 4.0, 6.0, 8.0, 100.0]
LEVEL_LABELS = ["<2%", "2-4%", "4-6%", "6-8%", ">8%"]

# Regime B — direzione: variazione FFR sui 12 mesi trailing
DIR_THRESHOLD = 1.0  # pp
DIR_LABELS = ["Discesa (≤−1pp)", "Stabile (−1÷+1pp)", "Rialzo (≥+1pp)"]

# Regime C — livello reale FFR-CPI YoY
REAL_BINS = [-100.0, 0.0, 2.0, 4.0, 100.0]
REAL_LABELS = ["<0% (accomodante)", "0-2%", "2-4%", ">4% (restrittivo)"]

# Event study — parametri stretti per catturare veri "inizio ciclo" Fed
# Con soglia +/-1.5pp su 6 mesi e 24 mesi di quiete, otteniamo ~6-8 cicli
# per direzione — coerente con la storiografia Fed (Volcker, Greenspan,
# Bernanke, Yellen, Powell).
EVENT_WINDOW_MONTHS = 24
HIKING_THRESHOLD_PP = 1.5   # aumento cumulato 6m che identifica start ciclo
CUTTING_THRESHOLD_PP = -1.5
DELTA_WINDOW_MONTHS = 6
QUIET_MONTHS = 24  # mesi di quiete prima del pivot per considerarlo "inizio"

# Palette SML — coerente con altri articoli SML
COLOR_SP500 = "#1e3a8a"      # navy (baseline)
COLOR_NASDAQ = "#d97706"     # ambra (protagonista tech)
COLOR_FFR = "#dc2626"        # rosso mattone per tassi
COLOR_NEUTRAL = "#6b7280"
COLOR_UP = "#059669"         # verde per numeri positivi
COLOR_DOWN = "#dc2626"


# --------------------------------------------------------------------- #
# Loading                                                               #
# --------------------------------------------------------------------- #
def load_fedfunds() -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / "FEDFUNDS.csv", parse_dates=["observation_date"])
    df = df.rename(columns={"observation_date": "date", "FEDFUNDS": "ffr"})
    df["date"] = df["date"] + pd.offsets.MonthEnd(0)
    return df.set_index("date").sort_index()


def load_sp500_tr_and_cpi() -> tuple[pd.Series, pd.Series]:
    """S&P 500 TR mensile ricostruito con formula Shiller. Post 2023-06
    (dividendo non disponibile) estrapola con yield costante conservativo.
    Ritorna anche CPI Shiller (per calcolare tasso reale)."""
    s = pd.read_csv(CACHE_DIR / "shiller_mirror.csv", parse_dates=["Date"])
    s = s.rename(columns={"Date": "date", "SP500": "price",
                          "Dividend": "dividend",
                          "Consumer Price Index": "cpi"})
    s["date"] = s["date"] + pd.offsets.MonthEnd(0)
    s = s.set_index("date").sort_index()

    # Estrapola dividendo per il periodo mancante con yield costante
    div_yield_monthly = (SP500_DIV_YIELD_APPROX_ANNUAL / 12)
    missing = s["dividend"] == 0
    s.loc[missing, "dividend"] = s.loc[missing, "price"] * div_yield_monthly * 12

    # Formula TR Shiller: r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1
    prev_price = s["price"].shift(1)
    prev_div_mo = s["dividend"].shift(1) / 12
    tr = (s["price"] + prev_div_mo) / prev_price - 1
    tr.name = "sp500_ret"

    # CPI: manteniamo la serie originale, gli 0 diventano NaN
    cpi = s["cpi"].replace(0, np.nan)
    cpi.name = "cpi"
    return tr.dropna(), cpi.dropna()


def load_nasdaq_tr_proxy() -> pd.Series:
    """NASDAQCOM daily → EoM → rendimento mensile + dividendo costante 0.0625%/m."""
    df = pd.read_csv(CACHE_DIR / "NASDAQCOM.csv", parse_dates=["observation_date"])
    df = df.rename(columns={"observation_date": "date", "NASDAQCOM": "price"})
    df = df.set_index("date").sort_index()
    monthly = df["price"].resample("ME").last().dropna()
    pr = monthly.pct_change()
    tr = pr + NASDAQ_DIV_MONTHLY
    tr.name = "nasdaq_ret"
    return tr.dropna()


def build_monthly_panel() -> pd.DataFrame:
    ffr = load_fedfunds()
    sp500, cpi = load_sp500_tr_and_cpi()
    nasdaq = load_nasdaq_tr_proxy()

    panel = ffr.join([sp500, nasdaq, cpi], how="outer").sort_index()
    # CPI YoY (annualizzato)
    panel["cpi_yoy"] = panel["cpi"].pct_change(12) * 100  # in %
    panel["ffr_real"] = panel["ffr"] - panel["cpi_yoy"]

    # Direzione FFR trailing 12m (variazione in pp)
    panel["ffr_trailing_change"] = panel["ffr"] - panel["ffr"].shift(12)

    # Rendimenti forward
    for col in ["sp500_ret", "nasdaq_ret"]:
        panel[f"{col}_fwd12m"] = (
            (1 + panel[col]).rolling(12).apply(np.prod, raw=True).shift(-12) - 1
        )
        panel[f"{col}_fwd24m"] = (
            (1 + panel[col]).rolling(24).apply(np.prod, raw=True).shift(-24) - 1
        )

    # Filtro: parto da quando ho TUTTI i dati chiave (FFR + SP500 + NASDAQ)
    panel = panel[panel[["ffr", "sp500_ret", "nasdaq_ret"]].notna().all(axis=1)]
    return panel


# --------------------------------------------------------------------- #
# Classificazioni regime                                                #
# --------------------------------------------------------------------- #
def classify_all(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["regime_A"] = pd.cut(p["ffr"], bins=LEVEL_BINS, labels=LEVEL_LABELS,
                           include_lowest=True)
    # B: direzione
    def _dir(x):
        if pd.isna(x):
            return None
        if x <= -DIR_THRESHOLD:
            return DIR_LABELS[0]
        if x >= DIR_THRESHOLD:
            return DIR_LABELS[2]
        return DIR_LABELS[1]
    p["regime_B"] = p["ffr_trailing_change"].apply(_dir)
    # C: livello reale
    p["regime_C"] = pd.cut(p["ffr_real"], bins=REAL_BINS, labels=REAL_LABELS,
                           include_lowest=True)
    return p


# --------------------------------------------------------------------- #
# Statistiche per bucket                                                #
# --------------------------------------------------------------------- #
def annualize_ret(mean_m: float) -> float:
    return (1 + mean_m) ** 12 - 1


def stats_for_series(rets: pd.Series) -> dict:
    r = rets.dropna()
    if len(r) < 3:
        return {"n": len(r), "mean_m": np.nan, "mean_ann": np.nan,
                "median_ann": np.nan, "std_ann": np.nan, "sharpe": np.nan,
                "p5_ann": np.nan, "p95_ann": np.nan, "hit_rate": np.nan}
    mean_m = r.mean()
    std_ann = r.std() * np.sqrt(12)
    mean_ann = annualize_ret(mean_m)
    ex = mean_ann - RF
    sharpe = ex / std_ann if std_ann > 0 else np.nan
    return {
        "n": int(len(r)),
        "mean_m": float(mean_m),
        "mean_ann": float(mean_ann),
        "median_ann": float(annualize_ret(float(r.median()))),
        "std_ann": float(std_ann),
        "sharpe": float(sharpe),
        "p5_ann": float(annualize_ret(float(r.quantile(0.05)))),
        "p95_ann": float(annualize_ret(float(r.quantile(0.95)))),
        "hit_rate": float((r > 0).mean()),
    }


def stats_for_forward(fwd: pd.Series, horizon_months: int) -> dict:
    r = fwd.dropna()
    if len(r) < 3:
        return {"n": len(r), "median": np.nan, "mean": np.nan,
                "p5": np.nan, "p95": np.nan, "hit_rate": np.nan,
                "cagr_median": np.nan}
    return {
        "n": int(len(r)),
        "median": float(r.median()),
        "mean": float(r.mean()),
        "p5": float(r.quantile(0.05)),
        "p95": float(r.quantile(0.95)),
        "hit_rate": float((r > 0).mean()),
        "cagr_median": float((1 + float(r.median())) ** (12 / horizon_months) - 1),
    }


def build_regime_stats(p: pd.DataFrame, regime_col: str,
                       labels: list[str]) -> pd.DataFrame:
    rows = []
    for lab in labels:
        mask = p[regime_col] == lab
        for asset, retcol, fwd12, fwd24 in [
            ("SP500", "sp500_ret", "sp500_ret_fwd12m", "sp500_ret_fwd24m"),
            ("NASDAQ", "nasdaq_ret", "nasdaq_ret_fwd12m", "nasdaq_ret_fwd24m"),
        ]:
            sc = stats_for_series(p.loc[mask, retcol])
            f12 = stats_for_forward(p.loc[mask, fwd12], 12)
            f24 = stats_for_forward(p.loc[mask, fwd24], 24)
            rows.append({
                "regime": regime_col,
                "bucket": lab,
                "asset": asset,
                **{f"cont_{k}": v for k, v in sc.items()},
                **{f"fwd12_{k}": v for k, v in f12.items()},
                **{f"fwd24_{k}": v for k, v in f24.items()},
            })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------- #
# Event study                                                           #
# --------------------------------------------------------------------- #
def find_pivots(p: pd.DataFrame, direction: str) -> list[pd.Timestamp]:
    """
    direction = 'hiking': primo mese in cui FFR sale >= HIKING_THRESHOLD_PP
                          rispetto a 3m prima, dopo almeno QUIET_MONTHS
                          senza pivot precedenti.
    direction = 'cutting': speculare.
    """
    ffr = p["ffr"].dropna()
    delta = ffr - ffr.shift(DELTA_WINDOW_MONTHS)
    if direction == "hiking":
        triggers = delta >= HIKING_THRESHOLD_PP
    else:
        triggers = delta <= CUTTING_THRESHOLD_PP
    pivots = []
    last_pivot = None
    for t in ffr.index:
        if not triggers.get(t, False):
            continue
        # differenza in mesi calendario (piu' robusta di timedelta64('M'))
        if last_pivot is None:
            months_since = QUIET_MONTHS  # forza accettazione primo pivot
        else:
            months_since = (t.year - last_pivot.year) * 12 + (t.month - last_pivot.month)
        if months_since >= QUIET_MONTHS:
            pivots.append(t)
            last_pivot = t
    return pivots


def event_study_matrix(p: pd.DataFrame, pivots: list[pd.Timestamp],
                       ret_col: str) -> pd.DataFrame:
    """Ritorna matrix (event × k) di rendimenti cumulati normalizzati
    a 1.0 a t=0, con k in [-W, +W]."""
    W = EVENT_WINDOW_MONTHS
    rows = {}
    idx = p.index
    for t in pivots:
        if t not in idx:
            continue
        i0 = idx.get_loc(t)
        i_lo, i_hi = i0 - W, i0 + W
        if i_lo < 0 or i_hi >= len(idx):
            continue
        window = p.iloc[i_lo:i_hi + 1][ret_col]
        cum = (1 + window).cumprod()
        cum = cum / cum.iloc[W]  # normalizza a 1.0 a t=0
        rows[t] = cum.reset_index(drop=True).values
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).T  # eventi come righe
    df.columns = list(range(-W, W + 1))
    return df


# --------------------------------------------------------------------- #
# Plots                                                                 #
# --------------------------------------------------------------------- #
def _style():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200,
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_context_timeline(panel: pd.DataFrame, out: Path):
    fig, ax1 = plt.subplots(figsize=(12, 6.5))
    # equity curves cumulate normalizzate
    sp = (1 + panel["sp500_ret"]).cumprod()
    nd = (1 + panel["nasdaq_ret"]).cumprod()
    ax1.plot(sp.index, sp.values / sp.iloc[0], color=COLOR_SP500,
             lw=1.8, label="S&P 500 TR")
    ax1.plot(nd.index, nd.values / nd.iloc[0], color=COLOR_NASDAQ,
             lw=1.8, label="NASDAQ Composite (TR proxy)")
    ax1.set_yscale("log")
    ax1.set_ylabel("Crescita di 1$ (log)")
    ax1.legend(loc="upper left", frameon=False)
    # FFR sul secondario
    ax2 = ax1.twinx()
    ax2.plot(panel.index, panel["ffr"].values, color=COLOR_FFR, lw=1.2, alpha=0.9,
             label="Fed Funds Rate")
    ax2.set_ylabel("Fed Funds Rate (%)", color=COLOR_FFR)
    ax2.tick_params(axis="y", labelcolor=COLOR_FFR)
    ax2.grid(False)
    ax2.spines["top"].set_visible(False)
    ax1.set_title(f"Contesto: FFR e mercati azionari USA, {panel.index[0].date()} → {panel.index[-1].date()}")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_boxplot_returns(p: pd.DataFrame, regime_col: str, labels: list[str],
                          title: str, out: Path):
    fig, ax = plt.subplots(figsize=(10.5, 6))
    positions_sp = np.arange(len(labels)) * 3
    positions_nd = positions_sp + 1
    data_sp = [p.loc[p[regime_col] == lab, "sp500_ret"].dropna() * 100 for lab in labels]
    data_nd = [p.loc[p[regime_col] == lab, "nasdaq_ret"].dropna() * 100 for lab in labels]
    bp1 = ax.boxplot(data_sp, positions=positions_sp, widths=0.85,
                     patch_artist=True, showfliers=False)
    bp2 = ax.boxplot(data_nd, positions=positions_nd, widths=0.85,
                     patch_artist=True, showfliers=False)
    for b in bp1["boxes"]: b.set(facecolor=COLOR_SP500, alpha=0.55)
    for b in bp2["boxes"]: b.set(facecolor=COLOR_NASDAQ, alpha=0.55)
    ax.set_xticks(positions_sp + 0.5)
    ax.set_xticklabels(labels, fontsize=10)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("Rendimento mensile (%)")
    ax.set_title(title)
    # legend
    from matplotlib.patches import Patch
    handles = [Patch(color=COLOR_SP500, alpha=0.55, label="S&P 500 TR"),
               Patch(color=COLOR_NASDAQ, alpha=0.55, label="NASDAQ")]
    ax.legend(handles=handles, loc="upper right", frameon=False)
    for i, (lab, arr_sp) in enumerate(zip(labels, data_sp)):
        n = len(arr_sp)
        ax.text(positions_sp[i] + 0.5, ax.get_ylim()[0] * 0.98, f"n={n}",
                ha="center", va="bottom", fontsize=9, color=COLOR_NEUTRAL)
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_forward_bars(stats_df: pd.DataFrame, regime_col: str, labels: list[str],
                        horizon: str, title: str, out: Path):
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    x = np.arange(len(labels))
    w = 0.36
    sp_vals = [stats_df[(stats_df.bucket == lab) & (stats_df.asset == "SP500")]
                  [f"{horizon}_cagr_median" if horizon.startswith("fwd") else "median"].iloc[0] * 100
               for lab in labels]
    nd_vals = [stats_df[(stats_df.bucket == lab) & (stats_df.asset == "NASDAQ")]
                  [f"{horizon}_cagr_median" if horizon.startswith("fwd") else "median"].iloc[0] * 100
               for lab in labels]
    ax.bar(x - w / 2, sp_vals, width=w, color=COLOR_SP500, label="S&P 500 TR")
    ax.bar(x + w / 2, nd_vals, width=w, color=COLOR_NASDAQ, label="NASDAQ")
    for xi, v in zip(x, sp_vals):
        ax.text(xi - w / 2, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)
    for xi, v in zip(x, nd_vals):
        ax.text(xi + w / 2, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("CAGR mediano (%)")
    ax.set_title(title)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_event_study(mat_sp: pd.DataFrame, mat_nd: pd.DataFrame,
                       n_events: int, title: str, out: Path):
    W = EVENT_WINDOW_MONTHS
    x = np.arange(-W, W + 1)
    fig, ax = plt.subplots(figsize=(11, 6))
    for mat, color, label in [(mat_sp, COLOR_SP500, "S&P 500 TR"),
                                (mat_nd, COLOR_NASDAQ, "NASDAQ")]:
        if mat.empty:
            continue
        # spaghetti sottili
        for _, row in mat.iterrows():
            ax.plot(x, row.values * 100 - 100, color=color, alpha=0.12, lw=0.9)
        med = mat.median(axis=0).values * 100 - 100
        ax.plot(x, med, color=color, lw=3.2, label=f"{label} (mediana)")
    ax.axvline(0, color="black", lw=0.9, linestyle="--")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlabel("Mesi da t=0 (pivot Fed)")
    ax.set_ylabel("Rendimento cumulato (%, base 100 a t=0)")
    ax.set_title(f"{title} — {n_events} eventi identificati")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_scatter_ffr_fwd(panel: pd.DataFrame, out: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for ax, retcol, label, color in [
        (axes[0], "sp500_ret_fwd12m", "S&P 500 TR", COLOR_SP500),
        (axes[1], "nasdaq_ret_fwd12m", "NASDAQ", COLOR_NASDAQ),
    ]:
        d = panel[["ffr", retcol]].dropna()
        ax.scatter(d["ffr"].values, d[retcol].values * 100,
                    color=color, alpha=0.3, s=14)
        # OLS
        x = d["ffr"].values
        y = d[retcol].values * 100
        m, b = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, m * xs + b, color="black", lw=1.8, linestyle="--",
                 label=f"OLS: slope {m:.2f}%/pp, intercetta {b:.1f}%")
        # correlazione
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.02, 0.98, f"n={len(d)}\ncorr={corr:.2f}",
                 transform=ax.transAxes, va="top", ha="left", fontsize=10,
                 bbox=dict(facecolor="white", edgecolor=COLOR_NEUTRAL, alpha=0.85))
        ax.axhline(0, color="black", lw=0.5)
        ax.set_title(f"{label}: FFR vs rendimento forward 12m")
        ax.set_xlabel("Fed Funds Rate (%)")
        ax.legend(loc="lower left", frameon=False, fontsize=9)
    axes[0].set_ylabel("Rendimento cumulato forward 12m (%)")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_forward_horizons_panel(stats_A: pd.DataFrame, out: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for ax, horizon, label in [(axes[0], "fwd12", "Forward 12 mesi"),
                                (axes[1], "fwd24", "Forward 24 mesi")]:
        x = np.arange(len(LEVEL_LABELS))
        w = 0.36
        sp = [stats_A[(stats_A.bucket == b) & (stats_A.asset == "SP500")]
                  [f"{horizon}_cagr_median"].iloc[0] * 100 for b in LEVEL_LABELS]
        nd = [stats_A[(stats_A.bucket == b) & (stats_A.asset == "NASDAQ")]
                  [f"{horizon}_cagr_median"].iloc[0] * 100 for b in LEVEL_LABELS]
        ax.bar(x - w / 2, sp, width=w, color=COLOR_SP500, label="S&P 500 TR")
        ax.bar(x + w / 2, nd, width=w, color=COLOR_NASDAQ, label="NASDAQ")
        for xi, v in zip(x, sp): ax.text(xi - w / 2, v + 0.3, f"{v:.1f}", ha="center", fontsize=9)
        for xi, v in zip(x, nd): ax.text(xi + w / 2, v + 0.3, f"{v:.1f}", ha="center", fontsize=9)
        ax.set_xticks(x); ax.set_xticklabels(LEVEL_LABELS)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_ylabel("CAGR mediano (%)")
        ax.set_title(label)
        ax.legend(frameon=False)
    fig.suptitle("Forward return per livello FFR — 12m vs 24m", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #
def main():
    _style()
    print("[1/6] Load + panel...")
    panel = build_monthly_panel()
    p = classify_all(panel)
    print(f"      Panel: {p.index[0].date()} → {p.index[-1].date()}, {len(p)} mesi")
    print(f"      Copertura CPI (per tasso reale): fino a {p['cpi_yoy'].last_valid_index().date()}")

    print("\n[2/6] Statistiche per regime...")
    stats_A = build_regime_stats(p, "regime_A", LEVEL_LABELS)
    stats_B = build_regime_stats(p, "regime_B", DIR_LABELS)
    p_C = p[p["cpi_yoy"].notna()].copy()  # regime reale limitato a periodo CPI
    stats_C = build_regime_stats(p_C, "regime_C", REAL_LABELS)
    print(f"      Regime A (livello nominale): {len(stats_A)} righe")
    print(f"      Regime B (direzione):        {len(stats_B)} righe")
    print(f"      Regime C (livello reale):    {len(stats_C)} righe ({len(p_C)} mesi con CPI)")

    print("\n[3/6] Event study pivot Fed...")
    hiking = find_pivots(p, "hiking")
    cutting = find_pivots(p, "cutting")
    print(f"      Hiking pivots: {len(hiking)}")
    for t in hiking: print(f"        {t.date()}")
    print(f"      Cutting pivots: {len(cutting)}")
    for t in cutting: print(f"        {t.date()}")
    mat_h_sp = event_study_matrix(p, hiking, "sp500_ret")
    mat_h_nd = event_study_matrix(p, hiking, "nasdaq_ret")
    mat_c_sp = event_study_matrix(p, cutting, "sp500_ret")
    mat_c_nd = event_study_matrix(p, cutting, "nasdaq_ret")

    print("\n[4/6] Plots...")
    plot_context_timeline(p, OUT_DIR / "01_context_timeline.png")
    plot_boxplot_returns(p, "regime_A", LEVEL_LABELS,
        "Rendimenti mensili per livello FFR (nominale)",
        OUT_DIR / "02_regime_A_livello_boxplot.png")
    plot_forward_bars(stats_A, "regime_A", LEVEL_LABELS, "fwd12",
        "Rendimento forward 12m per livello FFR (mediana annualizzata)",
        OUT_DIR / "03_regime_A_forward12m.png")
    plot_boxplot_returns(p, "regime_B", DIR_LABELS,
        "Rendimenti mensili per direzione FFR (trailing 12m)",
        OUT_DIR / "04_regime_B_direzione_boxplot.png")
    plot_forward_bars(stats_B, "regime_B", DIR_LABELS, "fwd12",
        "Rendimento forward 12m per direzione FFR",
        OUT_DIR / "05_regime_B_forward12m.png")
    plot_boxplot_returns(p_C, "regime_C", REAL_LABELS,
        "Rendimenti mensili per FFR reale (FFR − CPI YoY)",
        OUT_DIR / "06_regime_C_reale_boxplot.png")
    plot_forward_bars(stats_C, "regime_C", REAL_LABELS, "fwd12",
        "Rendimento forward 12m per FFR reale",
        OUT_DIR / "07_regime_C_forward12m.png")
    plot_event_study(mat_h_sp, mat_h_nd, len(hiking),
        "Event study: inizio cicli di RIALZO Fed",
        OUT_DIR / "08_event_hiking_cycles.png")
    plot_event_study(mat_c_sp, mat_c_nd, len(cutting),
        "Event study: inizio cicli di TAGLIO Fed",
        OUT_DIR / "09_event_cutting_cycles.png")
    plot_scatter_ffr_fwd(p, OUT_DIR / "10_scatter_ffr_vs_forward12m.png")
    plot_forward_horizons_panel(stats_A,
        OUT_DIR / "11_forward_horizons_by_regime.png")

    print("\n[5/6] CSV/JSON output...")
    p.to_csv(OUT_DIR / "monthly_panel.csv", index_label="date")
    stats_long = pd.concat([stats_A, stats_B, stats_C], ignore_index=True)
    stats_long.to_csv(OUT_DIR / "regime_stats_long.csv", index=False)
    pd.DataFrame({"kind": ["hiking"] * len(hiking) + ["cutting"] * len(cutting),
                   "date": [str(t.date()) for t in hiking + cutting]}
                 ).to_csv(OUT_DIR / "pivot_dates.csv", index=False)

    # Equity curves per il reel (S&P TR + NASDAQ) normalizzate a 1.0
    sp_cum = (1 + p["sp500_ret"]).cumprod()
    nd_cum = (1 + p["nasdaq_ret"]).cumprod()
    eq = pd.DataFrame({
        "sp500_nav": sp_cum / sp_cum.iloc[0],
        "nasdaq_nav": nd_cum / nd_cum.iloc[0],
    }).dropna()
    eq.to_csv(OUT_DIR / "equity_curves_full.csv", index_label="date")

    # Correlazioni chiave per il summary
    def _corr(x, y):
        d = pd.concat([x, y], axis=1).dropna()
        if len(d) < 5:
            return float("nan")
        return float(d.iloc[:, 0].corr(d.iloc[:, 1]))

    summary = {
        "slug": SLUG,
        "parametri": {
            "nasdaq_div_annual": NASDAQ_DIV_ANNUAL,
            "sp500_div_yield_extrap": SP500_DIV_YIELD_APPROX_ANNUAL,
            "level_bins": LEVEL_LABELS,
            "dir_labels": DIR_LABELS,
            "real_bins": REAL_LABELS,
            "event_window_months": EVENT_WINDOW_MONTHS,
            "hiking_threshold_pp": HIKING_THRESHOLD_PP,
            "cutting_threshold_pp": CUTTING_THRESHOLD_PP,
            "quiet_months": QUIET_MONTHS,
            "rf": RF,
        },
        "panel": {
            "start": str(p.index[0].date()),
            "end": str(p.index[-1].date()),
            "months": int(len(p)),
        },
        "correlations": {
            "ffr_vs_sp500_contemporaneous": _corr(p["ffr"], p["sp500_ret"]),
            "ffr_vs_sp500_forward12m": _corr(p["ffr"], p["sp500_ret_fwd12m"]),
            "ffr_vs_sp500_forward24m": _corr(p["ffr"], p["sp500_ret_fwd24m"]),
            "ffr_vs_nasdaq_contemporaneous": _corr(p["ffr"], p["nasdaq_ret"]),
            "ffr_vs_nasdaq_forward12m": _corr(p["ffr"], p["nasdaq_ret_fwd12m"]),
            "ffr_vs_nasdaq_forward24m": _corr(p["ffr"], p["nasdaq_ret_fwd24m"]),
        },
        "regime_A_stats": stats_A.to_dict(orient="records"),
        "regime_B_stats": stats_B.to_dict(orient="records"),
        "regime_C_stats": stats_C.to_dict(orient="records"),
        "pivot_dates": {
            "hiking": [str(t.date()) for t in hiking],
            "cutting": [str(t.date()) for t in cutting],
        },
        "event_study_medians": {
            "hiking_sp500_t12": float(mat_h_sp.iloc[:, EVENT_WINDOW_MONTHS + 12].median() - 1) if not mat_h_sp.empty else None,
            "hiking_sp500_t24": float(mat_h_sp.iloc[:, EVENT_WINDOW_MONTHS + 24].median() - 1) if not mat_h_sp.empty else None,
            "hiking_nasdaq_t12": float(mat_h_nd.iloc[:, EVENT_WINDOW_MONTHS + 12].median() - 1) if not mat_h_nd.empty else None,
            "hiking_nasdaq_t24": float(mat_h_nd.iloc[:, EVENT_WINDOW_MONTHS + 24].median() - 1) if not mat_h_nd.empty else None,
            "cutting_sp500_t12": float(mat_c_sp.iloc[:, EVENT_WINDOW_MONTHS + 12].median() - 1) if not mat_c_sp.empty else None,
            "cutting_sp500_t24": float(mat_c_sp.iloc[:, EVENT_WINDOW_MONTHS + 24].median() - 1) if not mat_c_sp.empty else None,
            "cutting_nasdaq_t12": float(mat_c_nd.iloc[:, EVENT_WINDOW_MONTHS + 12].median() - 1) if not mat_c_nd.empty else None,
            "cutting_nasdaq_t24": float(mat_c_nd.iloc[:, EVENT_WINDOW_MONTHS + 24].median() - 1) if not mat_c_nd.empty else None,
        },
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)

    print(f"\n[6/6] OK. Output in: {OUT_DIR}")
    print(f"      Correlazione FFR vs SP500 fwd12m:  {summary['correlations']['ffr_vs_sp500_forward12m']:.3f}")
    print(f"      Correlazione FFR vs NASDAQ fwd12m: {summary['correlations']['ffr_vs_nasdaq_forward12m']:.3f}")


if __name__ == '__main__':
    main()
