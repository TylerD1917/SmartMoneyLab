"""
SmartMoneyLab — Ha ancora senso inserire obbligazioni in portafoglio?
====================================================================

Confronto tra tre portafogli (100% azionario, 60/40, 40/60) su rolling
windows a 5 e 10 anni con step di 3 mesi, dati 1976-2025.

Asset:
- Azionario:    S&P 500 Total Return (mensile, ricostruito dai dati Shiller)
- Obbligazion.: UST 10Y constant maturity, total return ricostruito dai
                yield mensili FRED (modello duration-based standard).

Metodologia:
- BUY & HOLD puro: nessun rebalancing. Per le rolling windows ogni
  finestra parte dai pesi target (es. 60/40) e i pesi driftano
  liberamente per la durata della finestra. Decisione metodologica
  per evitare di modellare costi di transazione variabili che il
  100% azionario buy & hold non avrebbe.
- Rolling windows 5y (60 mesi) e 10y (120 mesi), step 3 mesi.
- Tutti i rendimenti sono nominali e LORDI di costi/tasse.

Fonti:
- Shiller Online Data: http://www.econ.yale.edu/~shiller/data.htm
- FRED DGS10 (10-Year Treasury Constant Maturity Rate):
  https://fred.stlouisfed.org/series/DGS10

Output:
- public/charts/ha-senso-obbligazioni-portafoglio/01..04_*.png
- public/charts/ha-senso-obbligazioni-portafoglio/summary.json
- public/charts/ha-senso-obbligazioni-portafoglio/data.csv

Riproducibilità:
- Le fonti vengono cachate in data/cache/ alla prima esecuzione.
- Eseguire da repository root o da scripts/ — i path sono relativi.
- Dipendenze: pandas, numpy, matplotlib, requests, openpyxl.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import io
import json
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# -------------------------------------------------------------------- #
# Setup percorsi                                                       #
# -------------------------------------------------------------------- #
SLUG = "ha-senso-obbligazioni-portafoglio"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo dell'analisi
START_DATE = "1976-01-01"
END_DATE = "2025-12-31"

# Parametri rolling
WINDOWS_MONTHS = {"5y": 60, "10y": 120}
STEP_MONTHS = 3

# Allocazioni dei tre portafogli (BUY & HOLD: i pesi sono iniziali,
# poi driftano liberamente — nessun rebalancing).
PORTFOLIOS = {
    "100E": {"equity": 1.00, "bonds": 0.00},
    "60/40": {"equity": 0.60, "bonds": 0.40},
    "40/60": {"equity": 0.40, "bonds": 0.60},
}

# Palette finance-clean
COLORS = {
    "100E": "#1e3a8a",   # navy intenso
    "60/40": "#3b82f6",  # blu medio
    "40/60": "#93c5fd",  # blu chiaro
}


# -------------------------------------------------------------------- #
# Download e parsing fonti                                             #
# -------------------------------------------------------------------- #

# Fonti dati. Mirror GitHub come PRIMARIO per S&P (CSV semplice, niente
# dipendenze su xlrd/openpyxl), Shiller .xls come fallback. Per FRED
# proviamo l'URL graph CSV con retry e poi un endpoint alternativo.
SHILLER_CSV_MIRROR = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
)
SHILLER_XLS_URLS = [
    "https://shillerdata.com/wp-content/uploads/ie_data.xls",
    "http://www.econ.yale.edu/~shiller/data/ie_data.xls",
]
FRED_URLS = [
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
    "https://fred.stlouisfed.org/series/DGS10/downloaddata/DGS10.csv",
]

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _download(urls, cache_name: str, retries: int = 3, backoff: float = 2.0) -> bytes:
    """
    Scarica una risorsa con fallback su piu' URL e retry con backoff
    esponenziale. `urls` puo' essere una stringa o una lista; ogni URL
    viene riprovato fino a `retries` volte prima di passare al successivo.
    """
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        print(f"[cache] {cache_name}")
        return cache_path.read_bytes()

    if isinstance(urls, str):
        urls = [urls]

    headers = {"User-Agent": _BROWSER_UA, "Accept": "*/*"}
    last_err = None
    for url in urls:
        for attempt in range(1, retries + 1):
            try:
                if attempt == 1:
                    print(f"[download] {url}")
                else:
                    print(f"[download retry {attempt}/{retries}] {url}")
                resp = requests.get(url, headers=headers, timeout=60)
                resp.raise_for_status()
                cache_path.write_bytes(resp.content)
                return resp.content
            except Exception as exc:
                last_err = exc
                print(f"  -> failed: {exc}")
                if attempt < retries:
                    sleep_for = backoff ** attempt
                    print(f"  -> retrying in {sleep_for:.1f}s…")
                    time.sleep(sleep_for)
    raise RuntimeError(
        f"All download attempts failed for {cache_name}: {last_err}\n"
        f"FALLBACK MANUALE: scarica i dati a mano e salvali in "
        f"{cache_path}. Vedi le note in fondo allo script."
    )


def load_shiller_sp500_total_return() -> pd.Series:
    """
    Costruisce la serie mensile del total return S&P 500 dai dati Shiller.

    Per semplicità e robustezza usiamo come fonte primaria il mirror CSV
    su GitHub (`datasets/s-and-p-500`), che è un porting fedele dello
    stesso dataset, aggiornato regolarmente e leggibile senza dipendenze
    su xlrd/openpyxl. Se il mirror è irraggiungibile, ripieghiamo sul
    file .xls ufficiale.

    Il dataset espone P (price index, mensile) e D (dividendo annualizzato
    corrente). Il total return mensile è approssimato come:

        r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1

    cioè price return + 1/12 del dividendo annualizzato lo scorso mese.
    """
    df = None
    try:
        raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
        m = pd.read_csv(io.StringIO(raw))
        m.columns = [c.strip() for c in m.columns]
        # Mirror columns: Date, SP500, Dividend, Earnings, ...
        m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
        m = m.set_index("date").sort_index()
        df = pd.DataFrame(
            {
                "P": pd.to_numeric(m["SP500"], errors="coerce"),
                "D": pd.to_numeric(m["Dividend"], errors="coerce"),
            }
        )
    except Exception as exc:
        print(f"[shiller-csv] fallback to .xls — reason: {exc}")

    if df is None:
        # Fallback al .xls ufficiale (richiede openpyxl/xlrd)
        raw = _download(SHILLER_XLS_URLS, "shiller_ie_data.xls")
        xl = pd.ExcelFile(io.BytesIO(raw))
        sheet = "Data" if "Data" in xl.sheet_names else xl.sheet_names[0]
        tmp = pd.read_excel(xl, sheet_name=sheet, header=None)
        header_row = tmp.index[
            tmp.iloc[:, 0].astype(str).str.strip().str.lower().eq("date")
        ][0]
        df_xls = pd.read_excel(xl, sheet_name=sheet, header=header_row)
        df_xls = df_xls.rename(columns=lambda c: str(c).strip())

        def _shiller_date_to_period(x):
            if pd.isna(x):
                return pd.NaT
            s = f"{float(x):.2f}"
            year, month = s.split(".")
            month = month.zfill(2)
            if month == "00":
                month = "12"
                year = str(int(year) - 1)
            return pd.Timestamp(year=int(year), month=int(month), day=1)

        df_xls = df_xls[df_xls["Date"].notna()].copy()
        df_xls["date"] = df_xls["Date"].apply(_shiller_date_to_period)
        df_xls = df_xls.dropna(subset=["date"]).set_index("date")
        df = df_xls[["P", "D"]].apply(pd.to_numeric, errors="coerce")

    p = df["P"]
    d = df["D"]
    monthly_div = d.shift(1) / 12
    total_return = (p + monthly_div) / p.shift(1) - 1
    total_return.name = "sp500_tr_monthly"
    return total_return.dropna()


def load_fred_dgs10() -> pd.Series:
    """
    Yield mensile end-of-month del Treasury 10Y (constant maturity, %).

    FRED DGS10 e' giornaliero — campioniamo la fine di ogni mese.
    """
    raw = _download(FRED_URLS, "fred_dgs10.csv").decode("utf-8")
    df = pd.read_csv(io.StringIO(raw))
    df.columns = [c.strip() for c in df.columns]
    # Colonne: DATE, DGS10 (recenti) oppure observation_date, DGS10 (vecchio formato)
    date_col = "DATE" if "DATE" in df.columns else "observation_date"
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    yield_daily = pd.to_numeric(df["DGS10"], errors="coerce") / 100.0
    yield_eom = yield_daily.resample("ME").last()
    yield_eom.index = yield_eom.index.to_period("M").to_timestamp()
    yield_eom.name = "ust10y_yield"
    return yield_eom.dropna()


def reconstruct_ust10y_total_return(yields: pd.Series) -> pd.Series:
    """
    Ricostruisce il total return mensile del UST 10Y constant maturity da
    una serie di yield mensili.

    Modello duration-based standard (es. Swinkels 2019, "Treasury Bond
    Returns Without Bond Prices"). Per un bond a 10 anni con cedola al
    yield corrente:

        D_mod_t ≈ (1/y_t) * (1 - 1/(1+y_t)^10)
        r_t ≈ y_{t-1}/12 - D_mod_{t-1} * (y_t - y_{t-1})

    Il primo termine e' lo yield carry mensile, il secondo il P&L da
    movimento dello yield (positivo se il yield scende).

    L'approssimazione ignora la convexity (effetto di secondo ordine) ed
    e' adeguata per analisi rolling pluriennali.
    """
    y = yields.copy()
    y_prev = y.shift(1)
    # Duration modificata su 10 anni, dipendente dallo yield precedente.
    # Per yield bassi (vicini a zero) D_mod tende a 10 da sotto.
    n = 10
    d_mod = (1 / y_prev) * (1 - 1 / (1 + y_prev) ** n)
    # Caso limite: se y_prev ~ 0, l'espressione 1/y_prev diverge ma il
    # prodotto tende a n. Lo gestiamo numericamente.
    d_mod = d_mod.where(y_prev.abs() > 1e-6, other=float(n))

    carry = y_prev / 12
    capital = -d_mod * (y - y_prev)
    tr = carry + capital
    tr.name = "ust10y_tr_monthly"
    return tr.dropna()


# -------------------------------------------------------------------- #
# Costruzione portafogli                                               #
# -------------------------------------------------------------------- #

def simulate_buy_and_hold(
    equity: pd.Series,
    bonds: pd.Series,
    weights: dict[str, float],
) -> pd.Series:
    """
    Calcola la serie di rendimenti mensili di un portafoglio BUY & HOLD:
    pesi iniziali = `weights`, poi i pesi driftano coi rendimenti relativi
    di azionario e obbligazionario, SENZA alcun rebalancing.

    E' la simulazione del lettore retail che compra una volta una certa
    allocazione e poi non tocca piu' il portafoglio.
    """
    df = pd.concat([equity.rename("e"), bonds.rename("b")], axis=1).dropna()
    we, wb = weights["equity"], weights["bonds"]
    out = []
    cur_we, cur_wb = we, wb

    for date, row in df.iterrows():
        re_, rb_ = row["e"], row["b"]
        # Rendimento del portafoglio nel mese
        port_r = cur_we * re_ + cur_wb * rb_
        out.append((date, port_r))
        # Aggiorna i pesi dopo il rendimento (drift) — niente rebalancing
        new_e_val = cur_we * (1 + re_)
        new_b_val = cur_wb * (1 + rb_)
        tot = new_e_val + new_b_val
        if tot > 0:
            cur_we, cur_wb = new_e_val / tot, new_b_val / tot

    s = pd.Series(dict(out), name="portfolio_return")
    s.index.name = "date"
    return s


# -------------------------------------------------------------------- #
# Metriche su rolling windows                                          #
# -------------------------------------------------------------------- #

def cagr(returns: pd.Series) -> float:
    """CAGR annualizzato a partire da una serie di rendimenti mensili."""
    n_months = len(returns)
    growth = (1 + returns).prod()
    if growth <= 0:
        return float("nan")
    return float(growth ** (12 / n_months) - 1)


def max_drawdown(returns: pd.Series) -> float:
    """Massimo drawdown da picco a valle, espresso in % negativa."""
    nav = (1 + returns).cumprod()
    peak = nav.cummax()
    dd = nav / peak - 1
    return float(dd.min())


def volatility_annualized(returns: pd.Series) -> float:
    """Deviazione standard annualizzata dai rendimenti mensili."""
    return float(returns.std() * np.sqrt(12))


@dataclass
class WindowStats:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr: float
    mdd: float
    vol: float


def rolling_window_stats(
    returns: pd.Series, window_months: int, step_months: int
) -> list[WindowStats]:
    """Lista di WindowStats per ogni finestra rolling su una serie di
    rendimenti gia' calcolata (utile per le full-sample stats sul
    portafoglio buy & hold dall'inizio del periodo)."""
    out = []
    n = len(returns)
    i = 0
    while i + window_months <= n:
        chunk = returns.iloc[i : i + window_months]
        out.append(
            WindowStats(
                start=chunk.index[0],
                end=chunk.index[-1],
                cagr=cagr(chunk),
                mdd=max_drawdown(chunk),
                vol=volatility_annualized(chunk),
            )
        )
        i += step_months
    return out


def rolling_window_stats_buy_and_hold(
    equity: pd.Series,
    bonds: pd.Series,
    weights: dict[str, float],
    window_months: int,
    step_months: int,
) -> list[WindowStats]:
    """
    Lista di WindowStats per finestre rolling, dove OGNI finestra simula
    un investitore che entra all'inizio della finestra coi pesi target
    `weights` e tiene buy & hold per la durata della finestra (i pesi
    driftano dentro la finestra, ma ogni finestra parte fresh).

    Questa e' la metodologia corretta per rispondere alla domanda:
    "se compro oggi un 60/40 e lo tengo N anni senza toccarlo, cosa mi
    aspetto?"
    """
    df = pd.concat([equity.rename("e"), bonds.rename("b")], axis=1).dropna()
    n = len(df)
    out = []
    i = 0
    while i + window_months <= n:
        eq_chunk = df["e"].iloc[i : i + window_months]
        b_chunk = df["b"].iloc[i : i + window_months]
        port = simulate_buy_and_hold(eq_chunk, b_chunk, weights)
        out.append(
            WindowStats(
                start=port.index[0],
                end=port.index[-1],
                cagr=cagr(port),
                mdd=max_drawdown(port),
                vol=volatility_annualized(port),
            )
        )
        i += step_months
    return out


def stats_to_df(stats: list[WindowStats]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start": [s.start for s in stats],
            "end": [s.end for s in stats],
            "cagr": [s.cagr for s in stats],
            "mdd": [s.mdd for s in stats],
            "vol": [s.vol for s in stats],
        }
    )


def percentiles(series: pd.Series, qs=(0.05, 0.25, 0.50, 0.75, 0.95)) -> dict:
    return {f"p{int(q*100)}": float(series.quantile(q)) for q in qs}


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


def plot_boxplot_cagr(stats_per_port: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    labels = list(stats_per_port.keys())
    data = [stats_per_port[k]["cagr"] * 100 for k in labels]
    bp = ax.boxplot(
        data,
        labels=labels,
        patch_artist=True,
        widths=0.55,
        medianprops=dict(color="#0f172a", linewidth=2),
        whiskerprops=dict(color="#475569"),
        capprops=dict(color="#475569"),
        flierprops=dict(
            marker="o", markerfacecolor="#94a3b8", markeredgecolor="none", markersize=4, alpha=0.5
        ),
    )
    for patch, label in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS[label])
        patch.set_alpha(0.85)
        patch.set_edgecolor("#0f172a")
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    _style_axes(
        ax,
        title=f"CAGR su finestre rolling {window_label} — distribuzione",
        ylabel="CAGR annualizzato (%)",
    )
    ax.text(
        0.99,
        -0.13,
        "Fonte: Shiller (S&P 500 TR), FRED DGS10. Lordo. Rolling step 3m.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_drawdown_distribution(stats_per_port: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    for label, df in stats_per_port.items():
        sorted_dd = np.sort(df["mdd"].values * 100)
        cdf = np.arange(1, len(sorted_dd) + 1) / len(sorted_dd)
        ax.plot(sorted_dd, cdf * 100, color=COLORS[label], linewidth=2.4, label=label)
    ax.legend(frameon=False, fontsize=11, loc="lower right")
    _style_axes(
        ax,
        title=f"Distribuzione del max drawdown — finestre rolling {window_label}",
        ylabel="% di finestre con drawdown ≤ x",
        xlabel="Max drawdown nella finestra (%)",
    )
    ax.text(
        0.99,
        -0.13,
        "Fonte: Shiller (S&P 500 TR), FRED DGS10. Lordo. Rolling step 3m.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_equity_curves(returns_per_port: dict, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    for label, r in returns_per_port.items():
        nav = (1 + r).cumprod()
        ax.plot(nav.index, nav.values, color=COLORS[label], linewidth=2.0, label=label)
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    _style_axes(
        ax,
        title="Crescita di 1 USD investito a inizio 1976 (scala log)",
        ylabel="NAV cumulato (scala log)",
        xlabel="",
    )
    ax.text(
        0.99,
        -0.13,
        "Fonte: Shiller (S&P 500 TR), FRED DGS10. Buy & hold (no rebalancing). Lordo.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def main():
    print("=" * 64)
    print("SmartMoneyLab — Ha senso inserire obbligazioni in portafoglio?")
    print("=" * 64)

    # 1. Carica fonti
    sp500 = load_shiller_sp500_total_return()
    yields = load_fred_dgs10()
    ust10y = reconstruct_ust10y_total_return(yields)

    # 2. Allinea le serie all'intervallo dell'analisi
    start, end = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
    sp500 = sp500.loc[start:end]
    ust10y = ust10y.loc[start:end]
    common = sp500.index.intersection(ust10y.index)
    sp500 = sp500.loc[common]
    ust10y = ust10y.loc[common]
    print(f"Periodo analizzato: {common.min().date()} — {common.max().date()}")
    print(f"Mesi disponibili: {len(common)}")

    # 3. Costruisci i tre portafogli — BUY & HOLD dal primo mese del
    #    periodo. Questi sono usati per la equity curve e per le statistiche
    #    full-sample. Per le rolling windows ricostruiamo il portafoglio
    #    fresh dentro ogni finestra (vedi sotto).
    port_returns = {}
    for name, w in PORTFOLIOS.items():
        port_returns[name] = simulate_buy_and_hold(sp500, ust10y, w)

    # 4. Statistiche full-sample
    print("\nStatistiche full-sample (lordo):")
    full_summary = {}
    for name, r in port_returns.items():
        c = cagr(r)
        m = max_drawdown(r)
        v = volatility_annualized(r)
        full_summary[name] = {"cagr": c, "mdd": m, "vol": v}
        print(f"  {name:5s}  CAGR={c*100:5.2f}%  MDD={m*100:6.2f}%  VOL={v*100:5.2f}%")

    # 5. Rolling stats e percentili — ogni finestra ricostruisce un buy &
    #    hold fresh dai pesi target (NON sub-slicing del portafoglio
    #    full-sample, che avrebbe pesi gia' driftati all'ingresso).
    rolling_results = {}  # window_label -> port -> DataFrame
    pct_results = {}      # window_label -> port -> {p5, p25, p50, p75, p95}
    for win_label, win_months in WINDOWS_MONTHS.items():
        rolling_results[win_label] = {}
        pct_results[win_label] = {}
        for name, w in PORTFOLIOS.items():
            stats = rolling_window_stats_buy_and_hold(
                sp500, ust10y, w, win_months, STEP_MONTHS
            )
            df = stats_to_df(stats)
            rolling_results[win_label][name] = df
            pct_results[win_label][name] = {
                "cagr": percentiles(df["cagr"]),
                "mdd": percentiles(df["mdd"]),
                "n_windows": int(len(df)),
                "share_negative_cagr": float((df["cagr"] < 0).mean()),
                "share_dd_worse_20pct": float((df["mdd"] < -0.20).mean()),
                "share_dd_worse_30pct": float((df["mdd"] < -0.30).mean()),
            }
            p = pct_results[win_label][name]["cagr"]
            print(
                f"  Rolling {win_label} — {name:5s}: "
                f"p5={p['p5']*100:5.2f}%  p50={p['p50']*100:5.2f}%  p95={p['p95']*100:5.2f}%  "
                f"({pct_results[win_label][name]['n_windows']} finestre)"
            )

    # 6. Grafici
    print("\nGenerazione grafici…")
    plot_boxplot_cagr(rolling_results["10y"], "10 anni", OUT_DIR / "01_boxplot_cagr_10y.png")
    plot_boxplot_cagr(rolling_results["5y"], "5 anni", OUT_DIR / "02_boxplot_cagr_5y.png")
    plot_drawdown_distribution(
        rolling_results["5y"], "5 anni", OUT_DIR / "03_drawdown_distribution_5y.png"
    )
    plot_equity_curves(port_returns, OUT_DIR / "04_equity_curve.png")

    # 7. Salva summary JSON e CSV
    summary = {
        "slug": SLUG,
        "period": {
            "start": str(common.min().date()),
            "end": str(common.max().date()),
            "n_months": int(len(common)),
        },
        "params": {
            "rebalancing": "none (buy & hold)",
            "rolling_step_months": STEP_MONTHS,
            "windows_months": WINDOWS_MONTHS,
        },
        "portfolios": PORTFOLIOS,
        "full_sample": full_summary,
        "rolling_percentiles": pct_results,
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    csv_df = pd.DataFrame(port_returns)
    csv_df.index.name = "date"
    csv_df.to_csv(OUT_DIR / "data.csv", float_format="%.6f")

    print(f"\nOutput salvati in: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()


# ====================================================================
# FALLBACK MANUALE — se anche dopo i retry FRED restituisce errore
# ====================================================================
#
# Il server FRED occasionalmente chiude la connessione TCP senza
# rispondere, soprattutto da reti con DPI / firewall aggressivi
# (alcune VPN, antivirus che intercettano il traffico HTTPS, reti
# aziendali). In quel caso scarica i dati a mano:
#
# 1. Apri https://fred.stlouisfed.org/series/DGS10 nel browser.
# 2. Click sul bottone arancione "Download" → seleziona "CSV (data)".
# 3. Salva il file scaricato in:
#       data/cache/fred_dgs10.csv
#    (esattamente con questo nome, nella sottocartella data/cache/
#     della repo). Se la cartella non esiste, creala.
# 4. Rilancia lo script: vedrà il file in cache e salterà il download.
#
# Stesso pattern vale per Shiller — file da salvare come
#   data/cache/shiller_mirror.csv  (versione CSV mirror GitHub)
#   oppure
#   data/cache/shiller_ie_data.xls (versione .xls ufficiale)
# ====================================================================
# end of file

