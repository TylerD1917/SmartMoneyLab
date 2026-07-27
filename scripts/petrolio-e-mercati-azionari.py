"""
SmartMoneyLab - Petrolio e mercati azionari globali (2000-2026)
================================================================

Domanda: come varia il rendimento (contemporaneo + forward 6m/12m/24m)
di 7 indici azionari globali al variare del regime del prezzo del petrolio?

Universo indici (7):
  S&P 500 (TR ricostruito Shiller), NASDAQ Composite (PR + 0.75%/y div),
  MSCI ACWI (PR + 1.9%/y div), DAX (TR nativo), FTSE 100 (PR + 3.5%/y div),
  Nikkei (PR + 1.8%/y div), MSCI EM (TR Gross monthly USD).

Due definizioni di regime, in parallelo:
  A. LIVELLO REALE del WTI - 4 bucket ($ costanti oggi):
     <40, 40-70, 70-100, >100
  B. VARIAZIONE TRAILING 3m del WTI reale:
     crollo (<=-30%), stabile (-30 +30), impennata (>=+30%)

Rendimenti forward: 6m, 12m, 24m (cumulati).

Event study aggiuntivo: shock petrolio estremi con soglia +/-50% su 3m
(minimo 12 mesi di quiete). Curve mediane +/-24m attorno al pivot.

Dati (tutti locali - nessuna rete):
  data/cache/CrudeOil_historical.csv    - WTI daily (yfinance), 2000-08+
  data/cache/shiller_mirror.csv         - SP500 monthly + Dividend + CPI (Shiller)
  data/cache/NASDAQCOM.csv              - NASDAQ Composite daily (FRED)
  data/raw/ACWI_historical.csv          - ACWI daily (yfinance PR)
  data/raw/DAX_historical.csv           - DAX daily (yfinance TR nativo)
  data/raw/FTSE100_historical.csv       - FTSE 100 daily (yfinance PR)
  data/raw/nikkei_historical.csv        - Nikkei daily (yfinance PR)
  data/raw/msci_em.csv                  - MSCI EM monthly Gross USD

Output in public/charts/petrolio-e-mercati-azionari/
  01_context_timeline.png               WTI reale + 7 indici log nel tempo
  02_regime_A_livello_boxplot.png       rendimenti mensili per livello reale WTI
  03_regime_A_forward12m.png            forward 12m per livello (7 indici)
  04_regime_B_variazione_boxplot.png    rendimenti per variazione trailing 3m
  05_regime_B_forward12m.png            forward 12m per variazione
  06_event_bull_shocks.png              event study impennate +/-24m
  07_event_bear_shocks.png              event study crolli +/-24m
  08_scatter_wti_vs_forward12m.png      correlazione livello WTI reale vs fwd12m
  09_forward_horizons_by_regime_A.png   panel 6m/12m/24m per livello reale
  10_forward_horizons_by_regime_B.png   panel 6m/12m/24m per variazione

  summary.json, monthly_panel.csv, regime_stats_long.csv,
  pivot_dates.csv, equity_curves_full.csv (per reel),
  lookup_oil_regime.json (per componente interattivo)

Uso locale:
    python scripts/petrolio-e-mercati-azionari.py

Autore: SmartMoneyLab - 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------- #
# Path e parametri                                                      #
# --------------------------------------------------------------------- #
SLUG = "petrolio-e-mercati-azionari"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOOKUP_DIR = REPO_ROOT / "public" / "tools"
LOOKUP_DIR.mkdir(parents=True, exist_ok=True)

# Dividendi annui aggiunti al PR degli indici per approssimare il TR
# (dichiarati esplicitamente nell'articolo come limite metodologico)
DIV_ANNUAL = {
    "SP500":   None,      # Shiller TR ricostruito
    "NASDAQ":  0.0075,    # ~1% Composite, 0.75% conservativo
    "ACWI":    0.0190,    # dividend yield medio storico
    "DAX":     None,      # TR nativo, non aggiungere dividendo
    "FTSE100": 0.0350,    # UK dividend-heavy
    "NIKKEI":  0.0180,    # Nikkei 225
    "MSCI_EM": None,      # Gross TR gia' nel dato
}

def monthly_div(annual):
    if annual is None:
        return 0.0
    return (1 + annual) ** (1 / 12) - 1

# Regime A - livello WTI in dollari reali (base = ultimo CPI del panel)
LEVEL_BINS = [-0.01, 40.0, 70.0, 100.0, 500.0]
LEVEL_LABELS = ["<$40 (basso)", "$40-70 (normale)",
                "$70-100 (elevato)", ">$100 (shock)"]

# Regime B - variazione trailing 3m del WTI reale
CHANGE_WINDOW_MONTHS = 3
CHANGE_THRESHOLD_PCT = 0.30
DIR_LABELS = ["Crollo (<=-30%)", "Stabile (-30 +30)", "Impennata (>=+30%)"]

# Forward horizons
FWD_MONTHS = [6, 12, 24]

# Event study parametri
EVENT_WINDOW_MONTHS = 24
SHOCK_THRESHOLD = 0.50   # +/-50% su 3m
SHOCK_QUIET_MONTHS = 12  # mesi di quiete prima del pivot per considerarlo "shock"

# Palette SML - 7 indici + petrolio, coerente col resto del blog
COLOR_OIL = "#0f172a"          # slate-900 (petrolio nero)
COLOR_SP500 = "#1e3a8a"        # navy
COLOR_NASDAQ = "#d97706"       # ambra
COLOR_ACWI = "#059669"         # verde
COLOR_DAX = "#7c3aed"          # viola
COLOR_FTSE = "#dc2626"         # rosso mattone
COLOR_NIKKEI = "#0891b2"       # ciano
COLOR_EM = "#c2410c"           # arancione bruciato

INDEX_COLORS = {
    "SP500": COLOR_SP500,
    "NASDAQ": COLOR_NASDAQ,
    "ACWI": COLOR_ACWI,
    "DAX": COLOR_DAX,
    "FTSE100": COLOR_FTSE,
    "NIKKEI": COLOR_NIKKEI,
    "MSCI_EM": COLOR_EM,
}

INDEX_LABELS = {
    "SP500": "S&P 500 (TR Shiller)",
    "NASDAQ": "NASDAQ (PR + 0.75%/y)",
    "ACWI": "MSCI ACWI (PR + 1.9%/y)",
    "DAX": "DAX (TR nativo)",
    "FTSE100": "FTSE 100 (PR + 3.5%/y)",
    "NIKKEI": "Nikkei (PR + 1.8%/y)",
    "MSCI_EM": "MSCI EM (TR Gross USD)",
}


# --------------------------------------------------------------------- #
# Loading                                                               #
# --------------------------------------------------------------------- #
def load_wti_monthly() -> pd.Series:
    df = pd.read_csv(CACHE_DIR / "CrudeOil_historical.csv", parse_dates=["Date"])
    df = df.set_index("Date").sort_index()
    monthly = df["Close"].resample("ME").last().dropna()
    monthly.name = "wti"
    return monthly


def load_sp500_cpi() -> tuple[pd.Series, pd.Series]:
    """SP500 TR mensile Shiller + CPI mensile.
    CPI estrapolato oltre 2023-09 al tasso mensile medio degli ultimi 24 mesi
    (approssimazione dichiarata nell'articolo)."""
    s = pd.read_csv(CACHE_DIR / "shiller_mirror.csv", parse_dates=["Date"])
    s = s.rename(columns={"Date": "date", "SP500": "price",
                          "Dividend": "dividend",
                          "Consumer Price Index": "cpi"})
    s["date"] = s["date"] + pd.offsets.MonthEnd(0)
    s = s.set_index("date").sort_index()
    # Estrapola dividendo (post 2023-06 il campo e' 0)
    missing = s["dividend"] == 0
    s.loc[missing, "dividend"] = s.loc[missing, "price"] * 0.014
    prev_price = s["price"].shift(1)
    prev_div_mo = s["dividend"].shift(1) / 12
    tr = ((s["price"] + prev_div_mo) / prev_price - 1).dropna()
    tr.name = "SP500_ret"

    # CPI: estrapola oltre l'ultimo dato (2023-09) con inflazione target Fed
    # 2.5%/y - piu' difendibile che riproiettare i picchi 2022-23 in avanti.
    # L'articolo dichiara esplicitamente questa approssimazione.
    cpi_raw = s["cpi"].replace(0, np.nan)
    last_valid = cpi_raw.last_valid_index()
    ANNUAL_RATE_EXTRAP = 0.025
    monthly_rate = (1 + ANNUAL_RATE_EXTRAP) ** (1 / 12) - 1
    cpi = cpi_raw.copy()
    missing_after = cpi.index > last_valid
    if missing_after.any():
        n_months = np.arange(1, missing_after.sum() + 1)
        extrapolated = cpi.loc[last_valid] * (1 + monthly_rate) ** n_months
        cpi.loc[missing_after] = extrapolated
    cpi = cpi.dropna()
    cpi.name = "cpi"
    print(f"       [CPI] estrapolato oltre {last_valid.date()} con {ANNUAL_RATE_EXTRAP*100:.1f}%/y (target Fed)")
    return tr, cpi


def load_index_daily_pr(path: Path, name: str, add_div_annual: float | None) -> pd.Series:
    """Load daily price return CSV yfinance-like (Date,Close,...), resample monthly."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.set_index("Date").sort_index()
    monthly = df["Close"].resample("ME").last().dropna()
    pr = monthly.pct_change()
    div_mo = monthly_div(add_div_annual) if add_div_annual else 0.0
    tr = (pr + div_mo).dropna()
    tr.name = f"{name}_ret"
    return tr


def load_msci_em_monthly() -> pd.Series:
    """MSCI EM Gross TR mensile USD. Header proprietary in cima."""
    df = pd.read_csv(RAW_DIR / "msci_em.csv", skiprows=6)
    df.columns = ["date", "price"]
    df["date"] = pd.to_datetime(df["date"], format="%b %d, %Y", errors="coerce")
    df["price"] = df["price"].astype(str).str.replace(",", "").astype(float)
    df = df.dropna().set_index("date").sort_index()
    # date sono end-of-month gia'
    df.index = df.index + pd.offsets.MonthEnd(0)
    tr = df["price"].pct_change().dropna()
    tr.name = "MSCI_EM_ret"
    return tr


def build_monthly_panel() -> pd.DataFrame:
    print("[dati] Caricamento serie mensili...")
    wti = load_wti_monthly()
    sp500, cpi = load_sp500_cpi()
    # NASDAQCOM ha colonne diverse: observation_date, NASDAQCOM
    df_n = pd.read_csv(CACHE_DIR / "NASDAQCOM.csv", parse_dates=["observation_date"])
    df_n = df_n.rename(columns={"observation_date": "Date", "NASDAQCOM": "Close"})
    df_n = df_n.set_index("Date").sort_index()
    monthly_n = df_n["Close"].resample("ME").last().dropna()
    nasdaq = (monthly_n.pct_change() + monthly_div(DIV_ANNUAL["NASDAQ"])).dropna()
    nasdaq.name = "NASDAQ_ret"

    acwi = load_index_daily_pr(RAW_DIR / "ACWI_historical.csv", "ACWI", DIV_ANNUAL["ACWI"])
    dax = load_index_daily_pr(RAW_DIR / "DAX_historical.csv", "DAX", DIV_ANNUAL["DAX"])
    ftse = load_index_daily_pr(RAW_DIR / "FTSE100_historical.csv", "FTSE100", DIV_ANNUAL["FTSE100"])
    nikkei = load_index_daily_pr(RAW_DIR / "nikkei_historical.csv", "NIKKEI", DIV_ANNUAL["NIKKEI"])
    em = load_msci_em_monthly()

    print(f"       WTI:      {wti.index[0].date()} -> {wti.index[-1].date()}, {len(wti)} mesi")
    print(f"       SP500:    {sp500.index[0].date()} -> {sp500.index[-1].date()}, {len(sp500)} mesi")
    print(f"       NASDAQ:   {nasdaq.index[0].date()} -> {nasdaq.index[-1].date()}, {len(nasdaq)} mesi")
    print(f"       ACWI:     {acwi.index[0].date()} -> {acwi.index[-1].date()}, {len(acwi)} mesi")
    print(f"       DAX:      {dax.index[0].date()} -> {dax.index[-1].date()}, {len(dax)} mesi")
    print(f"       FTSE100:  {ftse.index[0].date()} -> {ftse.index[-1].date()}, {len(ftse)} mesi")
    print(f"       Nikkei:   {nikkei.index[0].date()} -> {nikkei.index[-1].date()}, {len(nikkei)} mesi")
    print(f"       MSCI EM:  {em.index[0].date()} -> {em.index[-1].date()}, {len(em)} mesi")
    print(f"       CPI:      {cpi.index[0].date()} -> {cpi.index[-1].date()}, {len(cpi)} mesi")

    panel = pd.concat([wti, cpi, sp500, nasdaq, acwi, dax, ftse, nikkei, em],
                      axis=1).sort_index()

    # Deflaziono il petrolio: prezzo reale ai $ dell'ULTIMO CPI disponibile
    cpi_last = panel["cpi"].dropna().iloc[-1]
    panel["wti_real"] = panel["wti"] * (cpi_last / panel["cpi"])
    # Variazione trailing 3m del prezzo REALE
    panel["wti_real_ch3m"] = panel["wti_real"].pct_change(CHANGE_WINDOW_MONTHS)

    # Forward returns per ogni indice
    for asset in ["SP500", "NASDAQ", "ACWI", "DAX", "FTSE100", "NIKKEI", "MSCI_EM"]:
        for h in FWD_MONTHS:
            panel[f"{asset}_ret_fwd{h}m"] = (
                (1 + panel[f"{asset}_ret"]).rolling(h).apply(np.prod, raw=True).shift(-h) - 1
            )

    # Filtro: parto da quando ho tutti i core
    core = ["wti_real", "SP500_ret", "NASDAQ_ret"]
    panel = panel[panel[core].notna().all(axis=1)]
    return panel


# --------------------------------------------------------------------- #
# Classificazione regime                                                #
# --------------------------------------------------------------------- #
def classify_all(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["regime_A"] = pd.cut(p["wti_real"], bins=LEVEL_BINS,
                            labels=LEVEL_LABELS, include_lowest=True)
    def _dir(x):
        if pd.isna(x):
            return None
        if x <= -CHANGE_THRESHOLD_PCT:
            return DIR_LABELS[0]
        if x >= CHANGE_THRESHOLD_PCT:
            return DIR_LABELS[2]
        return DIR_LABELS[1]
    p["regime_B"] = p["wti_real_ch3m"].apply(_dir)
    return p


# --------------------------------------------------------------------- #
# Statistiche per bucket                                                #
# --------------------------------------------------------------------- #
def annualize_ret(mean_m: float) -> float:
    return (1 + mean_m) ** 12 - 1


def stats_contemp(rets: pd.Series) -> dict:
    r = rets.dropna()
    if len(r) < 3:
        return {"n": len(r), "mean_ann": np.nan, "median_ann": np.nan,
                "std_ann": np.nan, "p5_ann": np.nan, "p95_ann": np.nan,
                "hit_rate": np.nan}
    mean_m = r.mean()
    return {
        "n": int(len(r)),
        "mean_ann": float(annualize_ret(mean_m)),
        "median_ann": float(annualize_ret(float(r.median()))),
        "std_ann": float(r.std() * np.sqrt(12)),
        "p5_ann": float(annualize_ret(float(r.quantile(0.05)))),
        "p95_ann": float(annualize_ret(float(r.quantile(0.95)))),
        "hit_rate": float((r > 0).mean()),
    }


def stats_fwd(fwd: pd.Series, horizon: int) -> dict:
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
        "cagr_median": float((1 + float(r.median())) ** (12 / horizon) - 1),
    }


ASSETS = ["SP500", "NASDAQ", "ACWI", "DAX", "FTSE100", "NIKKEI", "MSCI_EM"]


def build_regime_stats(p: pd.DataFrame, regime_col: str,
                        labels: list[str]) -> pd.DataFrame:
    rows = []
    for lab in labels:
        mask = p[regime_col] == lab
        for asset in ASSETS:
            sc = stats_contemp(p.loc[mask, f"{asset}_ret"])
            entry = {
                "regime": regime_col,
                "bucket": lab,
                "asset": asset,
                "n_bucket": int(mask.sum()),
                **{f"cont_{k}": v for k, v in sc.items()},
            }
            for h in FWD_MONTHS:
                fwd = stats_fwd(p.loc[mask, f"{asset}_ret_fwd{h}m"], h)
                for k, v in fwd.items():
                    entry[f"fwd{h}_{k}"] = v
            rows.append(entry)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------- #
# Event study                                                           #
# --------------------------------------------------------------------- #
def find_shocks(p: pd.DataFrame, direction: str) -> list[pd.Timestamp]:
    wti_ch = p["wti_real_ch3m"].dropna()
    if direction == "bull":
        triggers = wti_ch >= SHOCK_THRESHOLD
    else:
        triggers = wti_ch <= -SHOCK_THRESHOLD
    shocks = []
    last = None
    for t in wti_ch.index:
        if not triggers.get(t, False):
            continue
        if last is None:
            months = SHOCK_QUIET_MONTHS
        else:
            months = (t.year - last.year) * 12 + (t.month - last.month)
        if months >= SHOCK_QUIET_MONTHS:
            shocks.append(t)
            last = t
    return shocks


def event_matrix(p: pd.DataFrame, pivots: list[pd.Timestamp],
                  ret_col: str) -> pd.DataFrame:
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
        cum = cum / cum.iloc[W]
        rows[t] = cum.reset_index(drop=True).values
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).T
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


def plot_context_timeline(p: pd.DataFrame, out: Path):
    fig, ax1 = plt.subplots(figsize=(12, 6.5))
    # 7 indici, log
    for asset in ASSETS:
        cum = (1 + p[f"{asset}_ret"]).cumprod().dropna()
        if cum.empty:
            continue
        ax1.plot(cum.index, cum.values / cum.iloc[0],
                 color=INDEX_COLORS[asset], lw=1.4, alpha=0.85,
                 label=INDEX_LABELS[asset])
    ax1.set_yscale("log")
    ax1.set_ylabel("Crescita di 1$ (log)")
    ax1.legend(loc="upper left", frameon=False, fontsize=8, ncol=2)
    ax2 = ax1.twinx()
    ax2.plot(p.index, p["wti_real"].values, color=COLOR_OIL, lw=1.6, alpha=0.9)
    ax2.set_ylabel("WTI reale ($ costanti oggi)", color=COLOR_OIL)
    ax2.tick_params(axis="y", labelcolor=COLOR_OIL)
    ax2.grid(False)
    ax2.spines["top"].set_visible(False)
    ax1.set_title(f"Contesto: WTI reale e 7 indici azionari globali, {p.index[0].date()} -> {p.index[-1].date()}")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_boxplot_returns(p: pd.DataFrame, regime_col: str, labels: list[str],
                          title: str, out: Path, assets_subset: list[str] = None):
    assets = assets_subset or ASSETS
    fig, ax = plt.subplots(figsize=(13, 6.5))
    n_assets = len(assets)
    width_group = 0.8 / n_assets
    for j, asset in enumerate(assets):
        data = [p.loc[p[regime_col] == lab, f"{asset}_ret"].dropna() * 100
                for lab in labels]
        positions = [i + (j - (n_assets - 1) / 2) * width_group
                     for i in range(len(labels))]
        bp = ax.boxplot(data, positions=positions, widths=width_group * 0.85,
                         patch_artist=True, showfliers=False)
        for b in bp["boxes"]: b.set(facecolor=INDEX_COLORS[asset], alpha=0.55)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("Rendimento mensile (%)")
    ax.set_title(title)
    from matplotlib.patches import Patch
    handles = [Patch(color=INDEX_COLORS[a], alpha=0.55, label=INDEX_LABELS[a]) for a in assets]
    ax.legend(handles=handles, loc="best", frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_forward_bars(stats_df: pd.DataFrame, labels: list[str], horizon: int,
                       title: str, out: Path):
    fig, ax = plt.subplots(figsize=(13, 6.5))
    x = np.arange(len(labels))
    n_assets = len(ASSETS)
    w = 0.85 / n_assets
    for j, asset in enumerate(ASSETS):
        vals = [stats_df[(stats_df.bucket == b) & (stats_df.asset == asset)]
                     [f"fwd{horizon}_cagr_median"].iloc[0] * 100
                for b in labels]
        positions = x + (j - (n_assets - 1) / 2) * w
        ax.bar(positions, vals, width=w * 0.9, color=INDEX_COLORS[asset],
                label=INDEX_LABELS[asset])
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel(f"CAGR mediano forward {horizon}m (%)")
    ax.set_title(title)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_event_study(matrices: dict[str, pd.DataFrame], n_events: int,
                       title: str, out: Path):
    W = EVENT_WINDOW_MONTHS
    x = np.arange(-W, W + 1)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for asset, mat in matrices.items():
        if mat.empty:
            continue
        med = mat.median(axis=0).values * 100 - 100
        ax.plot(x, med, color=INDEX_COLORS[asset], lw=2.4,
                label=INDEX_LABELS[asset])
    ax.axvline(0, color="black", lw=0.9, linestyle="--")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlabel("Mesi da t=0 (shock petrolio)")
    ax.set_ylabel("Rendimento cumulato mediano (%, base 100 a t=0)")
    ax.set_title(f"{title} - {n_events} eventi identificati")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_scatter_wti_vs_fwd12(p: pd.DataFrame, out: Path):
    """Panel 2x4 con scatter WTI reale vs fwd12m per ognuno dei 7 indici."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    for i, asset in enumerate(ASSETS):
        ax = axes[i]
        d = p[["wti_real", f"{asset}_ret_fwd12m"]].dropna()
        if len(d) < 5:
            ax.set_visible(False); continue
        ax.scatter(d["wti_real"].values, d[f"{asset}_ret_fwd12m"].values * 100,
                    color=INDEX_COLORS[asset], alpha=0.35, s=12)
        x = d["wti_real"].values; y = d[f"{asset}_ret_fwd12m"].values * 100
        m, b = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, m * xs + b, color="black", lw=1.5, linestyle="--")
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.02, 0.98, f"corr={corr:.2f}", transform=ax.transAxes,
                 va="top", ha="left", fontsize=10,
                 bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))
        ax.axhline(0, color="black", lw=0.4)
        ax.set_title(INDEX_LABELS[asset], fontsize=10)
    # ottava sottotrama vuota
    axes[-1].set_visible(False)
    fig.suptitle("WTI reale vs rendimento forward 12m per indice",
                  fontweight="bold")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_forward_horizons_panel_A(stats_A: pd.DataFrame, out: Path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    for ax, h in zip(axes, FWD_MONTHS):
        x = np.arange(len(LEVEL_LABELS))
        n_assets = len(ASSETS)
        w = 0.85 / n_assets
        for j, asset in enumerate(ASSETS):
            vals = [stats_A[(stats_A.bucket == b) & (stats_A.asset == asset)]
                        [f"fwd{h}_cagr_median"].iloc[0] * 100
                    for b in LEVEL_LABELS]
            positions = x + (j - (n_assets - 1) / 2) * w
            ax.bar(positions, vals, width=w * 0.9, color=INDEX_COLORS[asset],
                    label=INDEX_LABELS[asset])
        ax.set_xticks(x); ax.set_xticklabels(LEVEL_LABELS, fontsize=9, rotation=15)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(f"Forward {h}m")
        if h == FWD_MONTHS[0]:
            ax.set_ylabel("CAGR mediano (%)")
    axes[0].legend(frameon=False, fontsize=7, ncol=2, loc="best")
    fig.suptitle("Forward return per livello WTI reale - 6/12/24m",
                  fontweight="bold")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def plot_forward_horizons_panel_B(stats_B: pd.DataFrame, out: Path):
    fig, axes = plt.subplots(1, 3, figsize=(17, 6), sharey=True)
    for ax, h in zip(axes, FWD_MONTHS):
        x = np.arange(len(DIR_LABELS))
        n_assets = len(ASSETS)
        w = 0.85 / n_assets
        for j, asset in enumerate(ASSETS):
            vals = [stats_B[(stats_B.bucket == b) & (stats_B.asset == asset)]
                        [f"fwd{h}_cagr_median"].iloc[0] * 100
                    for b in DIR_LABELS]
            positions = x + (j - (n_assets - 1) / 2) * w
            ax.bar(positions, vals, width=w * 0.9, color=INDEX_COLORS[asset],
                    label=INDEX_LABELS[asset])
        ax.set_xticks(x); ax.set_xticklabels(DIR_LABELS, fontsize=9)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(f"Forward {h}m")
        if h == FWD_MONTHS[0]:
            ax.set_ylabel("CAGR mediano (%)")
    axes[0].legend(frameon=False, fontsize=7, ncol=2, loc="best")
    fig.suptitle("Forward return per variazione trailing 3m del WTI reale",
                  fontweight="bold")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #
def main():
    _style()
    panel = build_monthly_panel()
    p = classify_all(panel)
    print(f"\n[panel] {p.index[0].date()} -> {p.index[-1].date()}, {len(p)} mesi")

    print("\n[stats] Regime A (livello reale) e B (variazione 3m)...")
    stats_A = build_regime_stats(p, "regime_A", LEVEL_LABELS)
    stats_B = build_regime_stats(p, "regime_B", DIR_LABELS)
    for lab in LEVEL_LABELS:
        n = int((p["regime_A"] == lab).sum())
        print(f"    A - {lab}: {n} mesi")
    for lab in DIR_LABELS:
        n = int((p["regime_B"] == lab).sum())
        print(f"    B - {lab}: {n} mesi")

    print("\n[event] shock petrolio +/-50% su 3m...")
    bulls = find_shocks(p, "bull")
    bears = find_shocks(p, "bear")
    print(f"    Bull shocks: {len(bulls)}")
    for t in bulls: print(f"      {t.date()}")
    print(f"    Bear shocks: {len(bears)}")
    for t in bears: print(f"      {t.date()}")

    matrices_bull = {a: event_matrix(p, bulls, f"{a}_ret") for a in ASSETS}
    matrices_bear = {a: event_matrix(p, bears, f"{a}_ret") for a in ASSETS}

    print("\n[plot]")
    plot_context_timeline(p, OUT_DIR / "01_context_timeline.png")
    plot_boxplot_returns(p, "regime_A", LEVEL_LABELS,
        "Rendimenti mensili per livello WTI reale",
        OUT_DIR / "02_regime_A_livello_boxplot.png")
    plot_forward_bars(stats_A, LEVEL_LABELS, 12,
        "Forward 12m per livello WTI reale (7 indici)",
        OUT_DIR / "03_regime_A_forward12m.png")
    plot_boxplot_returns(p, "regime_B", DIR_LABELS,
        "Rendimenti mensili per variazione trailing 3m del WTI reale",
        OUT_DIR / "04_regime_B_variazione_boxplot.png")
    plot_forward_bars(stats_B, DIR_LABELS, 12,
        "Forward 12m per variazione WTI reale (7 indici)",
        OUT_DIR / "05_regime_B_forward12m.png")
    plot_event_study(matrices_bull, len(bulls),
        "Event study: impennate WTI (>= +50% su 3m)",
        OUT_DIR / "06_event_bull_shocks.png")
    plot_event_study(matrices_bear, len(bears),
        "Event study: crolli WTI (<= -50% su 3m)",
        OUT_DIR / "07_event_bear_shocks.png")
    plot_scatter_wti_vs_fwd12(p, OUT_DIR / "08_scatter_wti_vs_forward12m.png")
    plot_forward_horizons_panel_A(stats_A,
        OUT_DIR / "09_forward_horizons_by_regime_A.png")
    plot_forward_horizons_panel_B(stats_B,
        OUT_DIR / "10_forward_horizons_by_regime_B.png")

    print("\n[csv/json]")
    p.to_csv(OUT_DIR / "monthly_panel.csv", index_label="date")
    pd.concat([stats_A, stats_B], ignore_index=True).to_csv(
        OUT_DIR / "regime_stats_long.csv", index=False)
    pd.DataFrame({
        "kind": ["bull"] * len(bulls) + ["bear"] * len(bears),
        "date": [str(t.date()) for t in bulls + bears],
    }).to_csv(OUT_DIR / "pivot_dates.csv", index=False)

    # Equity curves per reel
    equity = {}
    for asset in ASSETS:
        cum = (1 + p[f"{asset}_ret"]).cumprod().dropna()
        equity[f"{asset}_nav"] = cum / cum.iloc[0]
    equity["wti_real_norm"] = p["wti_real"] / p["wti_real"].dropna().iloc[0]
    pd.DataFrame(equity).to_csv(OUT_DIR / "equity_curves_full.csv",
                                  index_label="date")

    def _corr(x, y):
        d = pd.concat([x, y], axis=1).dropna()
        if len(d) < 5:
            return float("nan")
        return float(d.iloc[:, 0].corr(d.iloc[:, 1]))

    correlations = {"level_vs_": {}, "change3m_vs_": {}}
    for asset in ASSETS:
        for h in FWD_MONTHS:
            correlations["level_vs_"][f"{asset}_fwd{h}m"] = _corr(
                p["wti_real"], p[f"{asset}_ret_fwd{h}m"])
            correlations["change3m_vs_"][f"{asset}_fwd{h}m"] = _corr(
                p["wti_real_ch3m"], p[f"{asset}_ret_fwd{h}m"])
        correlations["level_vs_"][f"{asset}_contemp"] = _corr(
            p["wti_real"], p[f"{asset}_ret"])
        correlations["change3m_vs_"][f"{asset}_contemp"] = _corr(
            p["wti_real_ch3m"], p[f"{asset}_ret"])

    event_medians = {}
    for asset in ASSETS:
        for kind, matrices in [("bull", matrices_bull), ("bear", matrices_bear)]:
            mat = matrices[asset]
            if mat.empty:
                continue
            for h in [6, 12, 24]:
                col_idx = EVENT_WINDOW_MONTHS + h
                event_medians[f"{kind}_{asset}_t{h}"] = float(
                    mat.iloc[:, col_idx].median() - 1)

    summary = {
        "slug": SLUG,
        "parametri": {
            "start": str(p.index[0].date()),
            "end": str(p.index[-1].date()),
            "months": int(len(p)),
            "level_bins": LEVEL_LABELS,
            "dir_labels": DIR_LABELS,
            "change_window_months": CHANGE_WINDOW_MONTHS,
            "change_threshold_pct": CHANGE_THRESHOLD_PCT,
            "shock_threshold": SHOCK_THRESHOLD,
            "shock_quiet_months": SHOCK_QUIET_MONTHS,
            "event_window_months": EVENT_WINDOW_MONTHS,
            "div_annual_added": DIV_ANNUAL,
            "cpi_base_date": str(p["cpi"].dropna().index[-1].date()) if p["cpi"].notna().any() else None,
        },
        "correlations": correlations,
        "regime_A_stats": stats_A.to_dict(orient="records"),
        "regime_B_stats": stats_B.to_dict(orient="records"),
        "pivot_dates": {
            "bulls": [str(t.date()) for t in bulls],
            "bears": [str(t.date()) for t in bears],
        },
        "event_study_medians": event_medians,
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)

    print(f"\n[done] Output in: {OUT_DIR}")


if __name__ == "__main__":
    main()
