"""
SmartMoneyLab — Portafoglio personale (Tipo C — test di portafogli reali)
==========================================================================

Backtest del portafoglio personale di Tyler (12 bucket, 100%) contro due
benchmark: S&P 500 TR e MSCI World TR.

Allocazione target:
  Azionario USA          16%   proxy: SPY (Adj Close = TR)
  Azionariato Globale     8%   proxy: URTH 2012+, SPY pre-2012
  Mercati Emergenti      12%   proxy: EEM 2003+
  Oro                     7%   proxy: GLD 2004+, gold_monthly.csv pre-2004
  Smallcap                7%   proxy: IWM 2000+
  Nasdaq                 16%   proxy: QQQ 1999+
  Bitcoin + Bets          5%   (2% BTC + 2% Disruptive + 1% Robotics)
                               proxy: BTC-USD 2014+ per BTC, Nasdaq100 per Disruptive+Robotics
                               pre-2014: 5% in Nasdaq100 (proxy bucket completo)
  Healthcare (US)         7%   proxy: XLV 1998+
  Europa                  6%   proxy: VGK 2005+, IEV pre-2005
  Asia ex Japan           7%   proxy: AAXJ 2008+, EEM pre-2008
  Energia tradizionale    3%   proxy: XLE 1998+
  Clean Energy            3%   proxy: ICLN 2008+, XLE pre-2008
  Nucleare                3%   proxy: URA 2010+, XLE pre-2010

Due scenari di simulazione:
  Scenario A (LUMP SUM): 10.000 EUR investiti il primo giorno con i pesi target.
                         Buy & hold puro, pesi driftano liberi (no rebalancing).
  Scenario B (PAC):      200 EUR versati ogni mese, allocati ai pesi target
                         (rebalancing implicito via PAC).

Benchmark: stessi due scenari su S&P 500 TR e su MSCI World TR.

Rolling windows: 5y, 10y, 15y, step 3 mesi.

Frequenza di lavoro: MENSILE (fine mese). L'oro storico ha solo dati mensili,
quindi anche tutti gli altri asset vengono campionati a fine mese — riduce
rumore e semplifica anche la simulazione Monte Carlo che gira in cascata.

Output in public/charts/portafoglio-personale-backtest/:
  - 01_composizione_donut.png
  - 02_storicita_asset.png
  - 03_equity_lumpsum_vs_benchmark.png
  - 04_equity_pac_vs_benchmark.png
  - 05_cagr_boxplot_rolling.png
  - 06_maxdd_boxplot_rolling.png
  - 07_win_rate_per_finestra.png
  - 08_pac_vs_lumpsum.png
  - summary.json
  - rolling_windows.csv
  - equity_curves_monthly.csv
  - monthly_returns.csv     (input per il Monte Carlo)

Dipendenze: pandas, numpy, matplotlib, scipy.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SLUG = "portafoglio-personale-backtest"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------- #
# Parametri                                                            #
# -------------------------------------------------------------------- #
INITIAL_CAPITAL = 10_000.0
PAC_MONTHLY = 200.0

WEIGHTS = {
    "usa":         0.16,
    "globale":     0.08,
    "em":          0.12,
    "oro":         0.07,
    "smallcap":    0.07,
    "nasdaq":      0.16,
    "btc_bets":    0.05,
    "healthcare":  0.07,
    "europa":      0.06,
    "asia":        0.07,
    "energy":      0.03,
    "clean":       0.03,
    "nuclear":     0.03,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Pesi devono sommare a 1"

# Mapping per il grafico torta (label leggibili in italiano)
LABELS_IT = {
    "usa":        "Azionario USA",
    "globale":    "Azionario Globale",
    "em":         "Mercati Emergenti",
    "oro":        "Oro",
    "smallcap":   "Small Cap",
    "nasdaq":     "Nasdaq 100",
    "btc_bets":   "Bitcoin + Tematici Tech",
    "healthcare": "Healthcare",
    "europa":     "Europa",
    "asia":       "Asia ex Japan",
    "energy":     "Energia Tradizionale",
    "clean":      "Energia Pulita",
    "nuclear":    "Nucleare",
}

# Palette: blu portafoglio, ambra benchmark
COLOR_PORT = "#1e3a8a"      # navy
COLOR_SP500 = "#d97706"     # ambra
COLOR_WORLD = "#059669"     # verde
COLOR_NEUTRAL = "#6b7280"

# Rolling windows in mesi
WINDOWS_MONTHS = {"5y": 60, "10y": 120, "15y": 180}
STEP_MONTHS = 3


# -------------------------------------------------------------------- #
# Caricamento e allineamento prezzi                                    #
# -------------------------------------------------------------------- #
def load_yf(slug: str) -> pd.Series:
    """Adj Close mensile (fine mese) di un ticker yfinance scaricato."""
    path = CACHE_DIR / f"yf_{slug}.csv"
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
    s = pd.to_numeric(df["AdjClose"], errors="coerce").dropna()
    # Resample a fine mese (ultimo giorno di trading del mese)
    monthly = s.resample("ME").last().dropna()
    return monthly


def load_gold_monthly() -> pd.Series:
    """gold_monthly.csv: serie LBMA mensile, dal 1968."""
    path = CACHE_DIR / "gold_monthly.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    date_col = next(c for c in df.columns if "date" in c.lower())
    price_col = next(c for c in df.columns if c.lower() in ("price", "gold", "close", "value"))
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    s = pd.to_numeric(df[price_col], errors="coerce").dropna()
    s.index = s.index.to_period("M").to_timestamp("M")
    return s


def stitch(short: pd.Series, long_proxy: pd.Series, splice_date: pd.Timestamp) -> pd.Series:
    """
    Stitch: usa `short` da splice_date in poi, `long_proxy` prima.
    Il proxy viene riscalato per allinearsi al primo valore di `short`.
    """
    short = short[short.index >= splice_date]
    proxy_pre = long_proxy[long_proxy.index < splice_date]
    if len(short) == 0 or len(proxy_pre) == 0:
        return short if len(short) > 0 else long_proxy

    # Ratio = primo valore di short / ultimo valore di proxy prima del splice
    ratio = short.iloc[0] / proxy_pre.iloc[-1]
    proxy_rescaled = proxy_pre * ratio
    return pd.concat([proxy_rescaled, short]).sort_index()


def build_asset_prices() -> pd.DataFrame:
    """
    Costruisce il pannello dei prezzi mensili per i 13 asset proxy.
    Tutti i prezzi sono Total Return (Adj Close gia' include i dividendi).
    Backfill dichiarati nei commenti del file.
    """
    # Carico tutti gli yf
    spy = load_yf("proxy_spy")
    urth = load_yf("proxy_urth_world")
    eem = load_yf("proxy_eem_em")
    gld = load_yf("proxy_gld_gold")
    gold_monthly = load_gold_monthly()
    iwm = load_yf("proxy_iwm_smallcap")
    qqq = load_yf("proxy_qqq_nasdaq100")
    btc = load_yf("proxy_btc_bitcoin")
    xlv = load_yf("proxy_xlv_healthcare")
    vgk = load_yf("proxy_vgk_europe")
    iev = load_yf("proxy_iev_europe_old")
    aaxj = load_yf("proxy_aaxj_asia_exjp")
    xle = load_yf("proxy_xle_energy")
    icln = load_yf("proxy_icln_clean")
    ura = load_yf("proxy_ura_uranium")

    # USA = SPY puro
    asset = {}
    asset["usa"] = spy.copy()

    # Globale = URTH dal 2012, SPY rescaled pre-2012
    asset["globale"] = stitch(urth, spy, pd.Timestamp("2012-01-31"))

    # EM = EEM puro
    asset["em"] = eem.copy()

    # Oro = GLD dal 2004, gold_monthly LBMA pre-2004 rescaled
    asset["oro"] = stitch(gld, gold_monthly, pd.Timestamp("2004-11-30"))

    # Smallcap = IWM puro (US small cap come proxy di MSCI World Small Cap,
    # ~60% di MSCI World Small e' US, correlazione tipica 0.85+)
    asset["smallcap"] = iwm.copy()

    # Nasdaq = QQQ puro
    asset["nasdaq"] = qqq.copy()

    # Bitcoin + Bets bucket (5% totale):
    # Costruzione: per il backtest unico tratto il bucket come una serie sintetica
    # con peso interno 2% BTC + 2% Disruptive Tech (proxy QQQ) + 1% Robotics (proxy QQQ).
    # Quindi pre-2014: 100% QQQ. Post-2014: 40% BTC + 60% QQQ (= 2%/5% BTC + 3%/5% QQQ).
    # Restituisco indice TR del bucket (cumulato da 1).
    btc_bets = build_btc_bets_bucket(btc, qqq)
    asset["btc_bets"] = btc_bets

    # Healthcare USA = XLV puro
    asset["healthcare"] = xlv.copy()

    # Europa = VGK dal 2005, IEV pre-2005 rescaled
    asset["europa"] = stitch(vgk, iev, pd.Timestamp("2005-03-31"))

    # Asia ex Japan = AAXJ dal 2008, EEM pre-2008 rescaled
    asset["asia"] = stitch(aaxj, eem, pd.Timestamp("2008-08-31"))

    # Energy = XLE puro
    asset["energy"] = xle.copy()

    # Clean Energy = ICLN dal 2008, XLE pre-2008 rescaled (proxy debole, dichiarato)
    asset["clean"] = stitch(icln, xle, pd.Timestamp("2008-06-30"))

    # Nuclear = URA dal 2010, XLE pre-2010 rescaled (proxy debole, dichiarato)
    asset["nuclear"] = stitch(ura, xle, pd.Timestamp("2010-11-30"))

    df = pd.DataFrame(asset)
    # Periodo comune: dal primo mese in cui TUTTI i 13 asset hanno un prezzo
    df = df.dropna()
    return df


def build_btc_bets_bucket(btc: pd.Series, qqq: pd.Series) -> pd.Series:
    """
    Bucket sintetico Bitcoin + Bets (5% del portafoglio).
    Composizione interna:
      2% Bitcoin (proxy BTC-USD dal 2014)
      2% MSCI Disruptive Tech (proxy QQQ)
      1% iShares Automation & Robotics (proxy QQQ)
    -> pesi interni: 40% BTC, 60% QQQ post-2014.
    Pre-2014 (BTC non esiste): 100% QQQ (proxy del bucket intero).

    Restituisce un indice di prezzo TR (base 100 al primo mese).
    """
    qqq_idx = qqq / qqq.iloc[0] * 100.0
    # Pre-BTC
    pre = qqq_idx[qqq_idx.index < btc.index[0]]
    # Post-BTC: ricostruisco da rendimenti mensili
    btc_ret = btc.pct_change().dropna()
    qqq_ret_post = qqq.pct_change().reindex(btc_ret.index).dropna()
    # Allineo
    common = btc_ret.index.intersection(qqq_ret_post.index)
    btc_ret = btc_ret.loc[common]
    qqq_ret_post = qqq_ret_post.loc[common]
    # Rendimento bucket = 0.40*BTC + 0.60*QQQ
    bucket_ret = 0.40 * btc_ret + 0.60 * qqq_ret_post
    # NAV bucket: parte dal valore di pre alla fine
    if len(pre) == 0:
        nav_start = 100.0
    else:
        nav_start = pre.iloc[-1]
    bucket_nav = (1 + bucket_ret).cumprod() * nav_start
    out = pd.concat([pre, bucket_nav]).sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out


# -------------------------------------------------------------------- #
# Costruzione benchmark                                                #
# -------------------------------------------------------------------- #
def build_benchmarks() -> pd.DataFrame:
    """SP500 TR (SPY adj close) e MSCI World TR (URTH stitched con SPY pre-2012)."""
    spy = load_yf("proxy_spy")
    urth = load_yf("proxy_urth_world")
    sp500 = spy.copy()
    msci_world = stitch(urth, spy, pd.Timestamp("2012-01-31"))
    df = pd.DataFrame({"sp500": sp500, "msci_world": msci_world}).dropna()
    return df


# -------------------------------------------------------------------- #
# Simulazione portafoglio                                              #
# -------------------------------------------------------------------- #
def simulate_lump_sum(prices: pd.DataFrame, weights: dict[str, float],
                      initial_capital: float) -> pd.Series:
    """Lump sum buy & hold, no rebalancing. Pesi driftano."""
    first = prices.iloc[0]
    units = {k: (weights[k] * initial_capital) / first[k] for k in weights}
    nav = pd.Series(0.0, index=prices.index)
    for k, u in units.items():
        nav += u * prices[k]
    nav.name = "portfolio_nav"
    return nav


def simulate_pac(prices: pd.DataFrame, weights: dict[str, float],
                 monthly: float) -> tuple[pd.Series, pd.Series]:
    """
    PAC mensile. Ogni fine mese versa `monthly`, allocato ai pesi target.
    Quindi compra `monthly * weight[k] / price[k]` quote di ciascun asset.
    Restituisce (nav_pac, contributi_cumulati).
    """
    units = {k: 0.0 for k in weights}
    nav_arr = []
    contrib_arr = []
    cumulative_contrib = 0.0
    for date, row in prices.iterrows():
        # Versamento di inizio mese (uso prezzo di fine mese stesso per
        # semplicita' — il PAC su 23 anni assorbe questa scelta)
        for k in weights:
            units[k] += (monthly * weights[k]) / row[k]
        cumulative_contrib += monthly
        nav = sum(units[k] * row[k] for k in weights)
        nav_arr.append(nav)
        contrib_arr.append(cumulative_contrib)
    nav_series = pd.Series(nav_arr, index=prices.index, name="pac_nav")
    contrib_series = pd.Series(contrib_arr, index=prices.index, name="pac_contributions")
    return nav_series, contrib_series


def simulate_benchmark_lump(bench_price: pd.Series, initial_capital: float) -> pd.Series:
    units = initial_capital / bench_price.iloc[0]
    return (bench_price * units).rename("bench_nav")


def simulate_benchmark_pac(bench_price: pd.Series, monthly: float) -> tuple[pd.Series, pd.Series]:
    units = 0.0
    nav_arr = []
    contrib_arr = []
    cum = 0.0
    for p in bench_price.values:
        units += monthly / p
        cum += monthly
        nav_arr.append(units * p)
        contrib_arr.append(cum)
    return (pd.Series(nav_arr, index=bench_price.index, name="bench_pac_nav"),
            pd.Series(contrib_arr, index=bench_price.index, name="bench_pac_contrib"))


# -------------------------------------------------------------------- #
# Metriche                                                             #
# -------------------------------------------------------------------- #
def cagr_monthly(nav: pd.Series) -> float:
    if len(nav) < 2 or nav.iloc[0] <= 0 or nav.iloc[-1] <= 0:
        return float("nan")
    n_months = len(nav) - 1
    growth = nav.iloc[-1] / nav.iloc[0]
    if growth <= 0:
        return float("nan")
    return float(growth ** (12.0 / n_months) - 1)


def max_drawdown_m(nav: pd.Series) -> float:
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def vol_annualized_m(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    return float(rets.std() * np.sqrt(12))


def sharpe_m(nav: pd.Series, rf_m_series: pd.Series | None = None) -> float:
    rets = nav.pct_change().dropna()
    if rf_m_series is not None:
        rf = rf_m_series.reindex(rets.index).ffill().fillna(0)
    else:
        rf = pd.Series(0.0, index=rets.index)
    excess = rets - rf
    if excess.std() == 0:
        return float("nan")
    return float(excess.mean() / excess.std() * np.sqrt(12))


def sortino_m(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    downside = rets[rets < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("nan")
    return float(rets.mean() / downside.std() * np.sqrt(12))


def calmar_m(nav: pd.Series) -> float:
    mdd = abs(max_drawdown_m(nav))
    if mdd == 0:
        return float("nan")
    return cagr_monthly(nav) / mdd


@dataclass
class WindowMetrics:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr_port: float
    cagr_sp500: float
    cagr_world: float
    mdd_port: float
    mdd_sp500: float
    mdd_world: float
    vol_port: float
    sharpe_port: float
    sharpe_sp500: float
    sharpe_world: float
    sortino_port: float
    calmar_port: float


# -------------------------------------------------------------------- #
# Rolling windows                                                      #
# -------------------------------------------------------------------- #
def rolling_windows(prices: pd.DataFrame, bench: pd.DataFrame,
                    window_months: int) -> list[WindowMetrics]:
    n = len(prices)
    out: list[WindowMetrics] = []
    i = 0
    while i + window_months <= n:
        sub_p = prices.iloc[i:i + window_months]
        sub_b = bench.iloc[i:i + window_months]

        port_nav = simulate_lump_sum(sub_p, WEIGHTS, 10_000)
        sp500_nav = simulate_benchmark_lump(sub_b["sp500"], 10_000)
        world_nav = simulate_benchmark_lump(sub_b["msci_world"], 10_000)

        out.append(WindowMetrics(
            start=sub_p.index[0], end=sub_p.index[-1],
            cagr_port=cagr_monthly(port_nav),
            cagr_sp500=cagr_monthly(sp500_nav),
            cagr_world=cagr_monthly(world_nav),
            mdd_port=max_drawdown_m(port_nav),
            mdd_sp500=max_drawdown_m(sp500_nav),
            mdd_world=max_drawdown_m(world_nav),
            vol_port=vol_annualized_m(port_nav),
            sharpe_port=sharpe_m(port_nav),
            sharpe_sp500=sharpe_m(sp500_nav),
            sharpe_world=sharpe_m(world_nav),
            sortino_port=sortino_m(port_nav),
            calmar_port=calmar_m(port_nav),
        ))
        i += STEP_MONTHS
    return out


# -------------------------------------------------------------------- #
# Plotting                                                             #
# -------------------------------------------------------------------- #
def _set_style():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200,
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_composition_donut(out_path: Path):
    labels = [LABELS_IT[k] for k in WEIGHTS]
    sizes = [WEIGHTS[k] * 100 for k in WEIGHTS]
    # Palette: blu→ambra→verde scuro a sezioni (13 colori)
    palette = [
        "#1e3a8a", "#3b82f6", "#60a5fa",  # blu (USA, Globale, EM)
        "#facc15",                          # giallo (oro)
        "#0d9488", "#0ea5e9",               # teal/azure (smallcap, nasdaq)
        "#d97706",                          # ambra (btc+bets)
        "#dc2626",                          # rosso (healthcare)
        "#7c3aed", "#a855f7",               # viola (europa, asia)
        "#92400e", "#22c55e", "#fbbf24",    # marrone/verde/oro (energy)
    ]
    fig, ax = plt.subplots(figsize=(9.5, 8))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=palette,
        autopct="%1.0f%%", pctdistance=0.78, startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 10},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax.set_title("Composizione target del portafoglio\n13 bucket, 100%",
                 fontsize=14, pad=20)
    # Capitale al centro
    ax.text(0, 0, "Portafoglio\npersonale", ha="center", va="center",
            fontsize=12, color=COLOR_NEUTRAL)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_asset_availability(prices_raw: dict[str, pd.Series], out_path: Path):
    """Barre orizzontali con il periodo di disponibilita' di ogni asset."""
    fig, ax = plt.subplots(figsize=(11, 6))
    items = sorted(prices_raw.items(), key=lambda x: x[1].index[0])
    for i, (k, s) in enumerate(items):
        ax.barh(i, (s.index[-1] - s.index[0]).days / 365.25,
                left=s.index[0].toordinal() / 365.25 - 1, height=0.6,
                color=COLOR_PORT, alpha=0.85)
        ax.text(s.index[0].toordinal() / 365.25 - 0.5, i,
                f"  {s.index[0].year}", va="center", fontsize=9, color="white")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([LABELS_IT[k] for k, _ in items])
    ax.set_xlabel("Anno")
    ax.set_title("Storicità degli asset (proxy a lungo storico)")

    # X axis in anni reali
    years = range(1995, 2027, 5)
    ax.set_xticks([pd.Timestamp(f"{y}-01-01").toordinal() / 365.25 - 1
                    for y in years])
    ax.set_xticklabels([str(y) for y in years])
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_equity_curves(port_nav: pd.Series, sp500_nav: pd.Series,
                        world_nav: pd.Series, title: str, out_path: Path):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(port_nav.index, port_nav.values, color=COLOR_PORT, lw=2.0,
            label="Portafoglio personale")
    ax.plot(sp500_nav.index, sp500_nav.values, color=COLOR_SP500, lw=1.6,
            label="S&P 500 TR")
    ax.plot(world_nav.index, world_nav.values, color=COLOR_WORLD, lw=1.6,
            label="MSCI World TR")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_ylabel("NAV (EUR)")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_rolling_boxplots(results: dict[str, list[WindowMetrics]],
                           metric: str, ylabel: str, title: str,
                           out_path: Path, as_pct: bool = True):
    labels = list(results.keys())
    fig, ax = plt.subplots(figsize=(11, 6))
    positions = []
    data_all = []
    colors = [COLOR_PORT, COLOR_SP500, COLOR_WORLD]
    legend_labels = ["Portafoglio", "S&P 500", "MSCI World"]
    suffixes = ["_port", "_sp500", "_world"]
    width = 0.25
    offsets = [-width, 0, width]

    for i, label in enumerate(labels):
        for j, suff in enumerate(suffixes):
            vals = [getattr(w, f"{metric}{suff}") for w in results[label]
                    if not np.isnan(getattr(w, f"{metric}{suff}"))]
            data_all.append(vals)
            positions.append(i + offsets[j])

    bps = ax.boxplot(data_all, positions=positions, widths=width * 0.9,
                     patch_artist=True, showfliers=True)
    for k, box in enumerate(bps["boxes"]):
        box.set(facecolor=colors[k % 3], alpha=0.6)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    if as_pct:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
    ax.axhline(0, color="black", lw=0.6)
    ax.set_title(title)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.6) for c in colors]
    ax.legend(handles, legend_labels, loc="best", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_win_rates(results: dict[str, list[WindowMetrics]], out_path: Path):
    labels = list(results.keys())
    wr_sp = []
    wr_w = []
    op_sp = []
    op_w = []
    for label in labels:
        ds = [w.cagr_port - w.cagr_sp500 for w in results[label]
              if not np.isnan(w.cagr_port) and not np.isnan(w.cagr_sp500)]
        dw = [w.cagr_port - w.cagr_world for w in results[label]
              if not np.isnan(w.cagr_port) and not np.isnan(w.cagr_world)]
        wr_sp.append(sum(1 for x in ds if x > 0) / len(ds) if ds else float("nan"))
        wr_w.append(sum(1 for x in dw if x > 0) / len(dw) if dw else float("nan"))
        op_sp.append(np.mean(ds) if ds else float("nan"))
        op_w.append(np.mean(dw) if dw else float("nan"))
    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(labels))
    width = 0.35
    bars1 = ax.bar(x - width / 2, [v * 100 for v in wr_sp], width,
                   color=COLOR_SP500, alpha=0.85, label="vs S&P 500")
    bars2 = ax.bar(x + width / 2, [v * 100 for v in wr_w], width,
                   color=COLOR_WORLD, alpha=0.85, label="vs MSCI World")
    for bar, wr, op in zip(bars1, wr_sp, op_sp):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{wr*100:.0f}%\n(Δ {op*100:+.1f}pp)", ha="center",
                va="bottom", fontsize=9)
    for bar, wr, op in zip(bars2, wr_w, op_w):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{wr*100:.0f}%\n(Δ {op*100:+.1f}pp)", ha="center",
                va="bottom", fontsize=9)
    ax.axhline(50, color="black", lw=0.6, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Win rate (%)")
    ax.set_title("Quota di finestre rolling in cui il portafoglio batte il benchmark")
    ax.set_ylim(0, 120)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_pac_real_vs_benchmarks(port_pac: pd.Series, sp500_pac: pd.Series,
                                  world_pac: pd.Series, contrib: pd.Series,
                                  out_path: Path, title_suffix: str = ""):
    """
    Confronto NAV di tre PAC con lo stesso versamento mensile:
      - PAC sul portafoglio personale
      - PAC sul S&P 500 TR
      - PAC sul MSCI World TR
    Tutti partono dalla stessa data (es. inception reale 2024-11-07).
    Mostra anche i contributi cumulati come baseline.
    """
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(port_pac.index, port_pac.values, color=COLOR_PORT, lw=2,
            label="PAC Portafoglio personale")
    ax.plot(sp500_pac.index, sp500_pac.values, color=COLOR_SP500, lw=1.8,
            label="PAC S&P 500 TR")
    ax.plot(world_pac.index, world_pac.values, color=COLOR_WORLD, lw=1.8,
            label="PAC MSCI World TR")
    ax.plot(contrib.index, contrib.values, color=COLOR_NEUTRAL, lw=1.4, ls="--",
            label="Contributi cumulati (200/mese)")
    # Scala log solo se il range valori lo giustifica
    all_vals = pd.concat([port_pac, sp500_pac, world_pac]).dropna()
    if len(all_vals) > 0 and all_vals.max() / max(all_vals.min(), 1) > 5:
        ax.set_yscale("log")
    title = "PAC 200€/mese — Portafoglio personale vs benchmark"
    if title_suffix:
        title += f"\n{title_suffix}"
    ax.set_title(title)
    ax.set_ylabel("NAV (EUR)")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #
def main():
    _set_style()
    print(f"\n=== {SLUG} ===\n")

    print("[1/5] Caricamento prezzi mensili...")
    prices = build_asset_prices()
    bench = build_benchmarks()
    # Allinea l'indice di tutti
    common_idx = prices.index.intersection(bench.index)
    prices = prices.loc[common_idx]
    bench = bench.loc[common_idx]
    print(f"      Periodo comune: {prices.index[0].date()} -> {prices.index[-1].date()}")
    print(f"      {len(prices)} mesi di dati")

    print("\n[2/5] Simulazione full period...")
    port_lump = simulate_lump_sum(prices, WEIGHTS, INITIAL_CAPITAL)
    sp500_lump = simulate_benchmark_lump(bench["sp500"], INITIAL_CAPITAL)
    world_lump = simulate_benchmark_lump(bench["msci_world"], INITIAL_CAPITAL)
    port_pac, port_contrib = simulate_pac(prices, WEIGHTS, PAC_MONTHLY)
    sp500_pac, _ = simulate_benchmark_pac(bench["sp500"], PAC_MONTHLY)
    world_pac, _ = simulate_benchmark_pac(bench["msci_world"], PAC_MONTHLY)

    print(f"      LUMP SUM full period:")
    print(f"        Portafoglio: NAV {port_lump.iloc[-1]:>12,.0f}   CAGR {cagr_monthly(port_lump)*100:+5.2f}%   MDD {max_drawdown_m(port_lump)*100:+5.1f}%")
    print(f"        S&P 500 TR:  NAV {sp500_lump.iloc[-1]:>12,.0f}   CAGR {cagr_monthly(sp500_lump)*100:+5.2f}%   MDD {max_drawdown_m(sp500_lump)*100:+5.1f}%")
    print(f"        MSCI World:  NAV {world_lump.iloc[-1]:>12,.0f}   CAGR {cagr_monthly(world_lump)*100:+5.2f}%   MDD {max_drawdown_m(world_lump)*100:+5.1f}%")
    print(f"      PAC full period (contributi totali: {port_contrib.iloc[-1]:,.0f}):")
    print(f"        Portafoglio: NAV {port_pac.iloc[-1]:>12,.0f}")
    print(f"        S&P 500 TR:  NAV {sp500_pac.iloc[-1]:>12,.0f}")
    print(f"        MSCI World:  NAV {world_pac.iloc[-1]:>12,.0f}")

    print("\n[3/5] Rolling windows...")
    results = {}
    for label, win in WINDOWS_MONTHS.items():
        if win <= len(prices):
            results[label] = rolling_windows(prices, bench, win)
            print(f"      [{label}] {len(results[label])} finestre")
        else:
            print(f"      [{label}] saltata, dati insufficienti")

    print("\n[4/5] Plot...")
    plot_composition_donut(OUT_DIR / "01_composizione_donut.png")
    # Per il grafico storicita uso le serie raw senza stitching
    prices_raw = {k: prices[k] for k in WEIGHTS}
    plot_asset_availability(prices_raw, OUT_DIR / "02_storicita_asset.png")
    plot_equity_curves(port_lump, sp500_lump, world_lump,
                       "NAV cumulato — Lump sum 10.000€ (scala log)",
                       OUT_DIR / "03_equity_lumpsum_vs_benchmark.png")
    plot_equity_curves(port_pac, sp500_pac, world_pac,
                       "NAV cumulato — PAC 200€/mese (scala log)",
                       OUT_DIR / "04_equity_pac_vs_benchmark.png")
    plot_rolling_boxplots(results, "cagr", "CAGR",
                          "Distribuzione del CAGR su finestre rolling (Lump sum)",
                          OUT_DIR / "05_cagr_boxplot_rolling.png")
    plot_rolling_boxplots(results, "mdd", "Max drawdown",
                          "Max drawdown su finestre rolling",
                          OUT_DIR / "06_maxdd_boxplot_rolling.png")
    plot_win_rates(results, OUT_DIR / "07_win_rate_per_finestra.png")

    # Plot 08 — confronto PAC portafoglio vs PAC S&P 500 vs PAC MSCI World
    # ristretto al periodo dell'investimento reale di Tyler
    # (inizio 7 novembre 2024). Allineato al primo fine-mese >= 2024-11-07.
    real_start = pd.Timestamp("2024-11-07")
    prices_real = prices[prices.index >= real_start]
    bench_real = bench[bench.index >= real_start]
    if len(prices_real) >= 2 and len(bench_real) >= 2:
        port_pac_real, port_contrib_real = simulate_pac(prices_real, WEIGHTS, PAC_MONTHLY)
        sp500_pac_real, _ = simulate_benchmark_pac(bench_real["sp500"], PAC_MONTHLY)
        world_pac_real, _ = simulate_benchmark_pac(bench_real["msci_world"], PAC_MONTHLY)
        title_suff = (f"Periodo reale dell'investimento: "
                       f"{prices_real.index[0].date()} → {prices_real.index[-1].date()} "
                       f"({len(prices_real)} mesi)")
        plot_pac_real_vs_benchmarks(port_pac_real, sp500_pac_real, world_pac_real,
                                     port_contrib_real,
                                     OUT_DIR / "08_pac_vs_lumpsum.png",
                                     title_suffix=title_suff)
        # Salvo anche i NAV "reali" come CSV per riferimento futuro
        pd.DataFrame({
            "port_pac_real": port_pac_real,
            "sp500_pac_real": sp500_pac_real,
            "world_pac_real": world_pac_real,
            "contributions_cumulated": port_contrib_real,
        }).to_csv(OUT_DIR / "equity_curves_real_period.csv")
        # Log a console le metriche del periodo reale
        print(f"\n      Periodo reale {prices_real.index[0].date()} -> {prices_real.index[-1].date()}:")
        print(f"        Contributi totali: {port_contrib_real.iloc[-1]:>10,.0f}")
        print(f"        PAC Portafoglio:   NAV {port_pac_real.iloc[-1]:>10,.0f}  "
              f"({(port_pac_real.iloc[-1]/port_contrib_real.iloc[-1]-1)*100:+5.1f}% sui contributi)")
        print(f"        PAC S&P 500:       NAV {sp500_pac_real.iloc[-1]:>10,.0f}  "
              f"({(sp500_pac_real.iloc[-1]/port_contrib_real.iloc[-1]-1)*100:+5.1f}% sui contributi)")
        print(f"        PAC MSCI World:    NAV {world_pac_real.iloc[-1]:>10,.0f}  "
              f"({(world_pac_real.iloc[-1]/port_contrib_real.iloc[-1]-1)*100:+5.1f}% sui contributi)")
    else:
        print(f"      [warn] Periodo post {real_start.date()} troppo breve "
               f"({len(prices_real)} mesi), salto plot 08")

    print("\n[5/5] Salvataggio CSV e JSON...")
    # CSV rolling
    rows = []
    for label, lst in results.items():
        for w in lst:
            r = asdict(w)
            r["window"] = label
            r["start"] = str(w.start.date())
            r["end"] = str(w.end.date())
            rows.append(r)
    pd.DataFrame(rows).to_csv(OUT_DIR / "rolling_windows.csv", index=False)

    # Equity curves
    pd.DataFrame({
        "port_lump": port_lump,
        "sp500_lump": sp500_lump,
        "world_lump": world_lump,
        "port_pac": port_pac,
        "port_pac_contributions": port_contrib,
        "sp500_pac": sp500_pac,
        "world_pac": world_pac,
    }).to_csv(OUT_DIR / "equity_curves_monthly.csv")

    # Monthly returns degli asset (input per Monte Carlo)
    monthly_returns = prices.pct_change().dropna()
    monthly_returns.to_csv(OUT_DIR / "monthly_returns.csv")

    # Summary JSON
    def _q(arr):
        if not arr:
            return {}
        arr = [x for x in arr if not np.isnan(x)]
        if not arr:
            return {}
        return {f"p{q}": float(np.percentile(arr, q)) for q in (5, 25, 50, 75, 95)}

    summary = {
        "slug": SLUG,
        "periodo": {
            "inizio": str(prices.index[0].date()),
            "fine": str(prices.index[-1].date()),
            "mesi": int(len(prices)),
        },
        "pesi_target": WEIGHTS,
        "parametri": {
            "capitale_iniziale": INITIAL_CAPITAL,
            "pac_mensile": PAC_MONTHLY,
            "step_months": STEP_MONTHS,
        },
        "full_period": {
            "lump": {
                "port_nav_finale": float(port_lump.iloc[-1]),
                "sp500_nav_finale": float(sp500_lump.iloc[-1]),
                "world_nav_finale": float(world_lump.iloc[-1]),
                "port_cagr": cagr_monthly(port_lump),
                "sp500_cagr": cagr_monthly(sp500_lump),
                "world_cagr": cagr_monthly(world_lump),
                "port_mdd": max_drawdown_m(port_lump),
                "sp500_mdd": max_drawdown_m(sp500_lump),
                "world_mdd": max_drawdown_m(world_lump),
                "port_vol": vol_annualized_m(port_lump),
                "sp500_vol": vol_annualized_m(sp500_lump),
                "world_vol": vol_annualized_m(world_lump),
                "port_sharpe": sharpe_m(port_lump),
                "sp500_sharpe": sharpe_m(sp500_lump),
                "world_sharpe": sharpe_m(world_lump),
                "port_sortino": sortino_m(port_lump),
                "port_calmar": calmar_m(port_lump),
            },
            "pac": {
                "contributi_totali": float(port_contrib.iloc[-1]),
                "port_nav_finale": float(port_pac.iloc[-1]),
                "sp500_nav_finale": float(sp500_pac.iloc[-1]),
                "world_nav_finale": float(world_pac.iloc[-1]),
            },
        },
        "rolling": {},
    }
    for label, lst in results.items():
        ds = [w.cagr_port - w.cagr_sp500 for w in lst
              if not np.isnan(w.cagr_port) and not np.isnan(w.cagr_sp500)]
        dw = [w.cagr_port - w.cagr_world for w in lst
              if not np.isnan(w.cagr_port) and not np.isnan(w.cagr_world)]
        summary["rolling"][label] = {
            "n_finestre": len(lst),
            "port_cagr_percentili": _q([w.cagr_port for w in lst]),
            "sp500_cagr_percentili": _q([w.cagr_sp500 for w in lst]),
            "world_cagr_percentili": _q([w.cagr_world for w in lst]),
            "port_mdd_percentili": _q([w.mdd_port for w in lst]),
            "sp500_mdd_percentili": _q([w.mdd_sp500 for w in lst]),
            "world_mdd_percentili": _q([w.mdd_world for w in lst]),
            "port_sharpe_percentili": _q([w.sharpe_port for w in lst]),
            "win_rate_vs_sp500": (sum(1 for x in ds if x > 0) / len(ds)) if ds else None,
            "win_rate_vs_world": (sum(1 for x in dw if x > 0) / len(dw)) if dw else None,
            "outperformance_media_pp_vs_sp500": (float(np.mean(ds) * 100)) if ds else None,
            "outperformance_media_pp_vs_world": (float(np.mean(dw) * 100)) if dw else None,
        }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\n      Output in: {OUT_DIR}")
    for p in sorted(OUT_DIR.iterdir()):
        print(f"        - {p.name}")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
