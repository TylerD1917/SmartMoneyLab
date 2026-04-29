"""
SmartMoneyLab — Ha senso inserire oro in portafoglio?
=====================================================

Confronto tra quattro portafogli buy & hold:
  - 100% azionario
  - 90% azionario / 10% oro
  - 75% azionario / 25% oro
  - 50% azionario / 50% oro

su rolling windows a 5 e 10 anni con step di 3 mesi.

Asset:
- Azionario:  S&P 500 Total Return (mensile, mirror dataset Shiller).
              I rendimenti azionari sono SEMPRE in Total Return (dividendi
              reinvestiti). Regola permanente del blog.
- Oro:        Gold Price LBMA in USD/oz, mensile, mirror GitHub
              datasets/gold-prices (porting fedele dei dati LBMA originali).
              FRED non distribuisce piu' i dati LBMA dal 2022 (decisione
              di ICE Benchmark Administration), quindi non possiamo usare
              GOLDPMGBD228NLBM come prima.
              L'oro non genera flussi: il rendimento mensile e' la
              variazione percentuale del prezzo spot end-of-month
              (price return = total return per un asset senza cash flow).

Metodologia:
- BUY & HOLD puro (nessun rebalancing). Per le rolling windows ogni
  finestra parte dai pesi target e i pesi driftano per la durata
  della finestra. Decisione metodologica permanente del blog: evita
  di modellare costi di transazione che il 100% azionario buy & hold
  non avrebbe.
- Rolling windows 5y (60 mesi) e 10y (120 mesi), step 3 mesi.
- Tutti i rendimenti sono nominali e LORDI di costi/tasse.
- L'oro non genera flussi di cassa (no cedole, no dividendi): il
  rendimento mensile e' semplicemente la variazione percentuale del
  prezzo spot end-of-month.

Fonti:
- S&P 500: Shiller / mirror GitHub `datasets/s-and-p-500`.
- Oro:     mirror GitHub `datasets/gold-prices/main/data/monthly.csv`
           (porting LBMA mensile dal 1950).
           Fallback: Stooq CSV (XAUUSD monthly).

Output:
- public/charts/ha-senso-oro-portafoglio/01..04_*.png
- public/charts/ha-senso-oro-portafoglio/summary.json
- public/charts/ha-senso-oro-portafoglio/data.csv

Riproducibilità:
- Le fonti vengono cachate in data/cache/ alla prima esecuzione.
- Eseguire da repository root o da scripts/ — i path sono relativi.
- Dipendenze: pandas, numpy, matplotlib, requests.

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
SLUG = "ha-senso-oro-portafoglio"
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
WINDOWS_MONTHS = {"5y": 60, "10y": 120, "20y": 240}
STEP_MONTHS = 3

# Allocazioni dei portafogli (BUY & HOLD: pesi iniziali, poi drift libero)
PORTFOLIOS = {
    "100E":  {"equity": 1.00, "gold": 0.00},
    "90/10": {"equity": 0.90, "gold": 0.10},
    "75/25": {"equity": 0.75, "gold": 0.25},
    "50/50": {"equity": 0.50, "gold": 0.50},
}

# Palette: navy/blu per i portafogli più azionari, ambra per il piu' oro-heavy
COLORS = {
    "100E":  "#1e3a8a",  # navy intenso
    "90/10": "#3b82f6",  # blu medio
    "75/25": "#93c5fd",  # blu chiaro
    "50/50": "#d97706",  # ambra (sussurro tematico)
}


# -------------------------------------------------------------------- #
# Download e parsing fonti                                             #
# -------------------------------------------------------------------- #

SHILLER_CSV_MIRROR = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
)
SHILLER_XLS_URLS = [
    "https://shillerdata.com/wp-content/uploads/ie_data.xls",
    "http://www.econ.yale.edu/~shiller/data/ie_data.xls",
]
# Fonti oro (in ordine di preferenza, retry automatico tra di loro):
#   1) GitHub mirror del dataset LBMA monthly — formato Date,Price; dati dal 1950.
#   2) Stooq XAU/USD monthly — CSV con OHLCV; dati dal 1968 circa.
# FRED ha rimosso i dati LBMA dal 2022 (ICE Benchmark Administration ha
# revocato la licenza a FRED) — non e' piu' utilizzabile.
GOLD_PRICE_URLS = [
    "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv",
    "https://stooq.com/q/d/l/?s=xauusd&i=m",
]

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _download(urls, cache_name: str, retries: int = 3, backoff: float = 2.0) -> bytes:
    """
    Scarica una risorsa con fallback su piu' URL e retry con backoff
    esponenziale. Se cached, ritorna immediatamente la cache.
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
    Costruisce la serie mensile del total return S&P 500 dal mirror CSV
    GitHub `datasets/s-and-p-500` (porting fedele del dataset Shiller).

    P = price index, D = dividendo annualizzato corrente.
    r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1
    """
    raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
    m = pd.read_csv(io.StringIO(raw))
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
    m = m.set_index("date").sort_index()
    p = pd.to_numeric(m["SP500"], errors="coerce")
    d = pd.to_numeric(m["Dividend"], errors="coerce")
    monthly_div = d.shift(1) / 12
    total_return = (p + monthly_div) / p.shift(1) - 1
    total_return.name = "sp500_tr_monthly"
    return total_return.dropna()


def load_gold_monthly_price() -> pd.Series:
    """
    Prezzo dell'oro mensile in USD/oz.

    Tenta due fonti in cascata:
      1) GitHub `datasets/gold-prices` — colonne Date,Price (LBMA monthly).
      2) Stooq XAU/USD — CSV con OHLCV monthly (Close come prezzo).

    L'oro non genera flussi (no cedole, no dividendi): il rendimento
    mensile e' semplicemente la variazione percentuale del prezzo
    end-of-month, r_t = P_t / P_{t-1} - 1.
    """
    raw = _download(GOLD_PRICE_URLS, "gold_monthly.csv").decode("utf-8")
    # Decidiamo quale parser usare in base alle colonne presenti
    df = pd.read_csv(io.StringIO(raw))
    df.columns = [c.strip() for c in df.columns]
    cols_lower = [c.lower() for c in df.columns]

    if "price" in cols_lower:
        # Formato GitHub mirror: Date, Price
        date_col = df.columns[cols_lower.index("date")]
        price_col = df.columns[cols_lower.index("price")]
        df["date"] = pd.to_datetime(df[date_col])
        df["price"] = pd.to_numeric(df[price_col], errors="coerce")
    elif "close" in cols_lower:
        # Formato Stooq: Date, Open, High, Low, Close, Volume
        date_col = df.columns[cols_lower.index("date")]
        close_col = df.columns[cols_lower.index("close")]
        df["date"] = pd.to_datetime(df[date_col])
        df["price"] = pd.to_numeric(df[close_col], errors="coerce")
    else:
        raise RuntimeError(
            f"Formato CSV oro non riconosciuto. Colonne trovate: {list(df.columns)}. "
            f"Vedi note di fallback manuale in fondo allo script."
        )

    # Normalizza al primo giorno del mese e prendi end-of-month
    df = df.dropna(subset=["price"]).sort_values("date")
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df = df.set_index("date")
    # Se la serie e' giornaliera o ha duplicati per mese, prendiamo l'ultimo valore del mese
    eom = df["price"].groupby(df.index).last()
    eom.name = "gold_usd_oz"
    return eom


def gold_monthly_returns(price: pd.Series) -> pd.Series:
    """Variazione percentuale mensile del prezzo dell'oro."""
    r = price.pct_change().dropna()
    r.name = "gold_return_monthly"
    return r


# -------------------------------------------------------------------- #
# Costruzione portafogli                                               #
# -------------------------------------------------------------------- #

def simulate_buy_and_hold(
    equity: pd.Series,
    gold: pd.Series,
    weights: dict[str, float],
) -> pd.Series:
    """
    Serie di rendimenti mensili di un portafoglio BUY & HOLD: pesi iniziali
    pari a `weights`, poi drift libero, nessun rebalancing.
    """
    df = pd.concat([equity.rename("e"), gold.rename("g")], axis=1).dropna()
    we, wg = weights["equity"], weights["gold"]
    out = []
    cur_we, cur_wg = we, wg

    for date, row in df.iterrows():
        re_, rg_ = row["e"], row["g"]
        port_r = cur_we * re_ + cur_wg * rg_
        out.append((date, port_r))
        new_e_val = cur_we * (1 + re_)
        new_g_val = cur_wg * (1 + rg_)
        tot = new_e_val + new_g_val
        if tot > 0:
            cur_we, cur_wg = new_e_val / tot, new_g_val / tot

    s = pd.Series(dict(out), name="portfolio_return")
    s.index.name = "date"
    return s


# -------------------------------------------------------------------- #
# Metriche su rolling windows                                          #
# -------------------------------------------------------------------- #

def cagr(returns: pd.Series) -> float:
    n_months = len(returns)
    growth = (1 + returns).prod()
    if growth <= 0:
        return float("nan")
    return float(growth ** (12 / n_months) - 1)


def max_drawdown(returns: pd.Series) -> float:
    nav = (1 + returns).cumprod()
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def volatility_annualized(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(12))


@dataclass
class WindowStats:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr: float
    mdd: float
    vol: float


def rolling_window_stats_buy_and_hold(
    equity: pd.Series,
    gold: pd.Series,
    weights: dict[str, float],
    window_months: int,
    step_months: int,
) -> list[WindowStats]:
    """
    Per ogni finestra rolling: simula buy & hold dai pesi target, calcola
    CAGR / MDD / vol. Ogni finestra parte fresh.
    """
    df = pd.concat([equity.rename("e"), gold.rename("g")], axis=1).dropna()
    n = len(df)
    out = []
    i = 0
    while i + window_months <= n:
        eq_chunk = df["e"].iloc[i : i + window_months]
        g_chunk = df["g"].iloc[i : i + window_months]
        port = simulate_buy_and_hold(eq_chunk, g_chunk, weights)
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
        tick_labels=labels,
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
        "Fonte: Shiller (S&P 500 TR), FRED Gold PM Fix. Buy & hold (no rebalancing). Lordo.",
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
        "Fonte: Shiller (S&P 500 TR), FRED Gold PM Fix. Buy & hold (no rebalancing). Lordo.",
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
        title="Crescita di 1 USD investito a inizio periodo (scala log)",
        ylabel="NAV cumulato (scala log)",
        xlabel="",
    )
    ax.text(
        0.99,
        -0.13,
        "Fonte: Shiller (S&P 500 TR), FRED Gold PM Fix. Buy & hold (no rebalancing). Lordo.",
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
    print("SmartMoneyLab — Ha senso inserire oro in portafoglio?")
    print("=" * 64)

    # 1. Carica fonti
    sp500 = load_shiller_sp500_total_return()
    gold_price = load_gold_monthly_price()
    gold = gold_monthly_returns(gold_price)

    # 2. Allinea le serie all'intervallo dell'analisi
    start, end = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
    sp500 = sp500.loc[start:end]
    gold = gold.loc[start:end]
    common = sp500.index.intersection(gold.index)
    sp500 = sp500.loc[common]
    gold = gold.loc[common]
    print(f"Periodo analizzato: {common.min().date()} — {common.max().date()}")
    print(f"Mesi disponibili: {len(common)}")

    # 3. Costruisci i portafogli buy & hold full-sample
    port_returns = {}
    for name, w in PORTFOLIOS.items():
        port_returns[name] = simulate_buy_and_hold(sp500, gold, w)

    # 4. Statistiche full-sample
    print("\nStatistiche full-sample (lordo, buy & hold):")
    full_summary = {}
    for name, r in port_returns.items():
        c = cagr(r)
        m = max_drawdown(r)
        v = volatility_annualized(r)
        full_summary[name] = {"cagr": c, "mdd": m, "vol": v}
        print(f"  {name:5s}  CAGR={c*100:5.2f}%  MDD={m*100:6.2f}%  VOL={v*100:5.2f}%")

    # 5. Rolling stats (ogni finestra ricostruisce buy & hold dai pesi target)
    rolling_results = {}
    pct_results = {}
    for win_label, win_months in WINDOWS_MONTHS.items():
        rolling_results[win_label] = {}
        pct_results[win_label] = {}
        print(f"\nRolling {win_label} (step {STEP_MONTHS}m):")
        for name, w in PORTFOLIOS.items():
            stats = rolling_window_stats_buy_and_hold(
                sp500, gold, w, win_months, STEP_MONTHS
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

    # 6. Correlazione storica oro / azionario (utile per il paragrafo extra)
    corr_full = float(sp500.corr(gold))
    print(f"\nCorrelazione mensile S&P 500 TR vs Oro: {corr_full:.3f}")

    # 7. Grafici
    print("\nGenerazione grafici…")
    plot_boxplot_cagr(rolling_results["10y"], "10 anni", OUT_DIR / "01_boxplot_cagr_10y.png")
    plot_boxplot_cagr(rolling_results["5y"], "5 anni", OUT_DIR / "02_boxplot_cagr_5y.png")
    plot_drawdown_distribution(
        rolling_results["5y"], "5 anni", OUT_DIR / "03_drawdown_distribution_5y.png"
    )
    plot_equity_curves(port_returns, OUT_DIR / "04_equity_curve.png")
    plot_boxplot_cagr(rolling_results["20y"], "20 anni", OUT_DIR / "05_boxplot_cagr_20y.png")

    # 8. Salva summary JSON e CSV
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
        "correlation_sp500_gold_monthly": corr_full,
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
# FALLBACK MANUALE — se i download del prezzo oro falliscono tutti
# ====================================================================
#
# Le fonti automatiche (GitHub mirror datasets/gold-prices, Stooq XAUUSD)
# sono normalmente affidabili. Se anche dopo i retry tutto fallisce,
# scarica i dati a mano:
#
# OPZIONE A — GitHub mirror (raccomandata, formato pulito):
# 1. Apri nel browser:
#       https://github.com/datasets/gold-prices/blob/main/data/monthly.csv
# 2. Click sul bottone "Raw" (oppure "Download raw file").
# 3. Salva il file come:
#       data/cache/gold_monthly.csv
#    (con questo nome esatto). Crea la cartella se non esiste.
# 4. Rilancia lo script: vedra' il file in cache e saltera' il download.
#
# OPZIONE B — Stooq:
# 1. Apri https://stooq.com/q/d/?s=xauusd&i=m
# 2. Click su "Download data in csv".
# 3. Salva come data/cache/gold_monthly.csv.
#
# OPZIONE C — World Gold Council (richiede registrazione):
# 1. Registrati su https://www.gold.org/goldhub/data/gold-prices
# 2. Scarica la serie monthly USD.
# 3. Salva come data/cache/gold_monthly.csv col formato Date,Price.
#
# Per Shiller — salva come data/cache/shiller_mirror.csv (CSV mirror
# GitHub, vedi script ha-senso-obbligazioni-portafoglio.py).
#
# NOTA: FRED ha rimosso i dati LBMA dal 2022 perche' ICE Benchmark
# Administration (IBA) non ha rinnovato la licenza di redistribuzione.
# Non possiamo piu' usare GOLDPMGBD228NLBM o serie LBMA su FRED.
# ====================================================================
# end of file
