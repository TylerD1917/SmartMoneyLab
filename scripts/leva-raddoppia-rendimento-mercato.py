"""
SmartMoneyLab — La leva 2x raddoppia il rendimento? La 3x lo triplica?
======================================================================

Confronto tra tre portafogli buy & hold tutti investiti al 100% in S&P 500
Total Return, con tre livelli di leva DAILY (rebalancing giornaliero, come
fanno gli ETF a leva reali tipo SSO, UPRO, TQQQ):

  - Leva 1x (baseline, S&P 500 TR puro)
  - Leva 2x daily
  - Leva 3x daily

Gli "ETF" a leva sono sintetici, costruiti applicando la leva al
rendimento daily del sottostante: r_lev_t = L * r_daily_t (NB: questo
puo' produrre NAV negativi solo se r_daily < -1/L; in pratica con S&P
non e' mai successo nemmeno il Black Monday del 19/10/1987 che fece
-22.6% — i risultati sono validi).

Asset:
- S&P 500 daily price index: Yahoo Finance via libreria yfinance (^GSPC,
  dati 1927+). Fallback: Stooq ^SPX se yfinance fallisce.
- Total Return daily ricostruito: aggiungiamo ai rendimenti price daily
  i dividendi mensili Shiller distribuiti uniformemente sui giorni di
  trading del mese (approssimazione standard).

Dipendenze: pandas, numpy, matplotlib, requests, yfinance.
Installazione: pip install yfinance pandas numpy matplotlib requests

Metodologia:
- Buy & hold puro su tutti e tre i livelli di leva.
- LORDO: niente TER, niente costi di financing della leva, niente tasse.
  ATTENZIONE: gli ETF a leva reali hanno TER 0.85-1.0% (vs 0.03-0.10%
  degli unleveraged) e costi impliciti di funding della leva (swap
  o futures). Quindi questa simulazione e' A VANTAGGIO delle leve
  rispetto alla realta'. Da dichiarare esplicitamente nell'articolo.
- Rolling windows 5y / 10y / 20y, step 3 mesi (misurato in mesi pieni).

Output:
- public/charts/leva-raddoppia-rendimento-mercato/01..05_*.png
- public/charts/leva-raddoppia-rendimento-mercato/summary.json
- public/charts/leva-raddoppia-rendimento-mercato/data.csv

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
SLUG = "leva-raddoppia-rendimento-mercato"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo dell'analisi
START_DATE = "1976-01-01"
END_DATE = "2025-12-31"

# Livelli di leva da testare
LEVERAGES = [1, 2, 3]

# Parametri rolling — espressi in MESI di calendario (sui dati daily
# campioniamo il primo giorno di ogni mese)
WINDOWS_MONTHS = {"5y": 60, "10y": 120, "20y": 240}
STEP_MONTHS = 3

# -------------------------------------------------------------------- #
# Calibrazione "costi reali" da ProShares Ultra S&P 500 (SSO),         #
# l'ETF a leva 2x piu' antico disponibile (dal 2006). Il prezzo SSO    #
# riflette gia' tutti i costi reali: TER + funding swap + tracking     #
# error.                                                                #
#                                                                       #
# Confrontando SSO vs una 2x sintetica calcolata sui daily SPY (entrambi #
# in USD, no effetto cambio), isoliamo il drag totale empirico annuale, #
# e poi lo decomponiamo in:                                              #
#                                                                        #
#   drag_total_2x = TER_SSO + funding_cost_per_unit_leva                 #
#                                                                        #
# Il funding_cost_per_unit_leva e' il costo del "dollaro preso a         #
# prestito" per ogni unita' di leva sopra 1x. Lo applichiamo poi:         #
#                                                                        #
#   drag_total_3x = TER_UPRO_o_UCITS_3x + 2 * funding_cost_per_unit       #
#                                                                        #
# perche' la 3x prende a prestito 2× il NAV (vs 1× della 2x).            #
# -------------------------------------------------------------------- #

# Path al CSV di confronto SSO vs synthetic 2x (input manuale di Tyler)
SSO_CSV_PATH = REPO_ROOT / "data" / "cache" / "confronto_leva_spy_sso.csv"

# TER (Total Expense Ratio) annuo dei vari ETF di riferimento
TER_SSO_PROSHARES = 0.0089   # ProShares Ultra S&P 500 (US, USD)
TER_UPRO_PROSHARES = 0.0091  # ProShares UltraPro S&P 500 (US, USD, 3x)
# UCITS (quelli che il retail italiano puo' comprare in EUR su Borsa)
TER_UCITS = {
    1: 0.0005,  # WisdomTree S&P 500
    2: 0.0060,  # Xtrackers S&P 500 2x Leveraged Daily Swap UCITS
    3: 0.0075,  # WisdomTree S&P 500 3x Daily Leveraged
}

# Palette: navy intenso → ambra (intensita' crescente con leva)
COLORS = {
    1: "#1e3a8a",   # navy
    2: "#3b82f6",   # blu
    3: "#d97706",   # ambra
}


# -------------------------------------------------------------------- #
# Download fonti                                                       #
# -------------------------------------------------------------------- #

STOOQ_SPX_URLS = [
    "https://stooq.com/q/d/l/?s=^spx&i=d",
    "https://stooq.com/q/d/l/?s=%5Espx&i=d",
]
SHILLER_CSV_MIRROR = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
)

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _download(urls, cache_name: str, retries: int = 3) -> bytes:
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        print(f"[cache] {cache_name}")
        return cache_path.read_bytes()
    if isinstance(urls, str):
        urls = [urls]
    headers = {"User-Agent": _BROWSER_UA}
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
                    time.sleep(2 ** attempt)
    raise RuntimeError(
        f"Download failed for {cache_name}: {last_err}\n"
        f"FALLBACK MANUALE: vedi note in fondo allo script."
    )


def _looks_like_csv(text: str) -> bool:
    """Heuristic: e' una risposta CSV valida o un HTML/error?"""
    if len(text) < 1000:
        return False
    head = text[:300].lower()
    if "<html" in head or "<!doctype" in head:
        return False
    # un CSV valido ha "date" o "close" nelle prime righe
    if "date" not in head and "close" not in head:
        return False
    return True


def _load_via_yfinance() -> pd.Series:
    """Daily close S&P 500 via libreria yfinance (Yahoo Finance)."""
    import yfinance as yf  # import lazy: solo se davvero serve

    cache_path = CACHE_DIR / "yahoo_gspc_daily.csv"
    if cache_path.exists():
        print("[cache] yahoo_gspc_daily.csv")
        df = pd.read_csv(cache_path, parse_dates=["Date"]).set_index("Date")
        return pd.to_numeric(df["Close"], errors="coerce").dropna().rename("sp500_close")

    print("[yfinance] downloading ^GSPC daily…")
    ticker = yf.Ticker("^GSPC")
    data = ticker.history(start=START_DATE, end=END_DATE, interval="1d", auto_adjust=False)
    if data.empty or "Close" not in data.columns:
        raise RuntimeError("yfinance ha restituito dati vuoti o senza colonna Close")

    # Rimuovo timezone (yfinance restituisce date tz-aware)
    data.index = pd.DatetimeIndex(data.index).tz_localize(None)
    out = pd.DataFrame({"Close": data["Close"]})
    out.index.name = "Date"
    out.to_csv(cache_path)
    return out["Close"].rename("sp500_close")


def _load_via_stooq() -> pd.Series:
    """Daily close S&P 500 da Stooq (fallback)."""
    raw = _download(STOOQ_SPX_URLS, "stooq_spx_daily.csv").decode("utf-8", errors="replace")
    if not _looks_like_csv(raw):
        raise RuntimeError(
            f"Stooq response non sembra un CSV valido (len={len(raw)}, "
            f"first 80 chars: {raw[:80]!r}). "
            f"Probabile blocco / pagina HTML — cancella il file in cache."
        )
    df = pd.read_csv(io.StringIO(raw))
    df.columns = [c.strip() for c in df.columns]
    date_col = next(c for c in df.columns if c.lower() == "date")
    close_col = next(c for c in df.columns if c.lower() == "close")
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    price = pd.to_numeric(df[close_col], errors="coerce").dropna()
    price.name = "sp500_close"
    return price


def load_sp500_daily_price() -> pd.Series:
    """
    Tenta in cascata: yfinance -> Stooq -> errore con istruzioni manuali.
    """
    errors = []
    try:
        return _load_via_yfinance()
    except Exception as exc:
        errors.append(f"yfinance: {exc}")
        print(f"[yfinance] failed -> {exc}")

    try:
        return _load_via_stooq()
    except Exception as exc:
        errors.append(f"stooq: {exc}")
        print(f"[stooq] failed -> {exc}")

    raise RuntimeError(
        "Tutte le fonti del prezzo daily S&P 500 sono fallite:\n  - "
        + "\n  - ".join(errors)
        + "\nVedi le note in fondo allo script per il fallback manuale."
    )


def load_shiller_monthly_dividend_yield() -> pd.Series:
    """
    Monthly trailing-12-month annualized dividend (D from Shiller).
    Restituisce una Series indicizzata a fine mese, in USD per share.
    """
    raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
    m = pd.read_csv(io.StringIO(raw))
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
    m = m.set_index("date").sort_index()
    p = pd.to_numeric(m["SP500"], errors="coerce")
    d = pd.to_numeric(m["Dividend"], errors="coerce")
    out = pd.DataFrame({"P": p, "D": d}).dropna()
    return out


def build_sp500_total_return_daily(
    price: pd.Series, shiller_pd: pd.DataFrame
) -> pd.Series:
    """
    Costruisce la serie giornaliera dei rendimenti TR del S&P 500.

    Logica:
      Per ogni giorno t in mese m:
         daily_div_amount = D_m / 252
            (D_m = dividendo annualizzato Shiller del mese m)
         tr_daily(t) = (P_t + daily_div_amount) / P_{t-1} - 1

    L'approssimazione "dividendo annualizzato / 252" e' equivalente a
    distribuire uniformemente i dividendi sui giorni di trading.
    Errore sul TR cumulato di lungo termine: trascurabile.
    """
    # Allinea date Shiller al timestamp del primo del mese
    shiller_pd = shiller_pd.copy()
    shiller_pd.index = shiller_pd.index.to_period("M").to_timestamp()

    # Per ogni giorno, trova il dividendo annualizzato del mese di
    # appartenenza
    price = price.sort_index()
    monthly_div = pd.Series(
        {d.to_period("M").to_timestamp(): d_val for d, d_val in shiller_pd["D"].items()}
    )

    # Map ogni timestamp daily al primo del suo mese
    monthly_keys = price.index.to_period("M").to_timestamp()
    daily_div_annualized = pd.Series(
        monthly_div.reindex(monthly_keys).values, index=price.index
    )
    daily_div_per_day = daily_div_annualized / 252.0

    # Rendimento TR daily approssimato
    tr_daily = (price + daily_div_per_day) / price.shift(1) - 1
    tr_daily = tr_daily.dropna()
    tr_daily.name = "sp500_tr_daily"
    return tr_daily


# -------------------------------------------------------------------- #
# Costruzione NAV a leva                                               #
# -------------------------------------------------------------------- #

def levered_nav(
    daily_returns: pd.Series, leverage: int, daily_drag: float = 0.0
) -> pd.Series:
    """
    NAV cumulato di un 'ETF a leva' che replica daily il L*r_t del
    sottostante, meno un drag deterministico per giorno. NAV iniziale = 1.

    daily_drag = costo annualizzato totale (TER + funding) / 252.
    Per leva 1x daily_drag = TER/252 (es. 0.05%/252 = ~0.0002 bps daily).
    Per leve 2x e 3x daily_drag include TER + funding (calibrato dai
    rendimenti reali di ETF UCITS — vedi calibrate_drag).
    """
    levered = leverage * daily_returns - daily_drag
    nav = (1 + levered).cumprod()
    nav = nav.clip(lower=1e-9)
    nav.name = f"NAV_{leverage}x"
    return nav


def calendar_year_return(nav: pd.Series, year: int) -> float:
    """Rendimento del NAV nel calendar year specificato."""
    period = nav.loc[f"{year}-01-01":f"{year}-12-31"]
    if len(period) < 100:
        return float("nan")
    return float(period.iloc[-1] / period.iloc[0] - 1)


def calibrate_drag_from_sso(csv_path: Path) -> dict:
    """
    Calibra empiricamente il drag della leva 2x usando il CSV di confronto
    SSO (ProShares Ultra S&P 500) vs una 2x sintetica calcolata sui daily
    SPY. Periodo di calibrazione: dal 2006 (lancio SSO) al 2023.

    Il CSV ha colonne:
      Date, Price_SPY_1x, Price_SSO_Real_2x, Price_Synthetic_2x, Difference_Real_vs_Synth

    Calcoliamo:
      drag_total_2x = ln(growth_synth) - ln(growth_real) / years
      ter_sso       = 0.89% (TER ProShares fisso)
      funding_cost  = drag_total_2x - ter_sso
                    (= costo della "dollaro a prestito" per ogni unita'
                       di leva sopra 1x)

    Da li' deriviamo i drag totali per le leve 2x e 3x in versione UCITS
    (TER piu' bassi, funding identico):
      drag_2x_ucits = TER_UCITS[2] + funding_cost
      drag_3x_ucits = TER_UCITS[3] + 2 * funding_cost

    Restituisce un dict con:
      'years'              : durata calibrazione in anni
      'cagr_synth_2x'      : CAGR della 2x sintetica
      'cagr_real_2x'       : CAGR di SSO reale
      'drag_total_2x'      : drag annualizzato totale del 2x reale (log)
      'ter_sso'            : TER usato per la decomposizione
      'funding_cost'       : funding cost per unita' di leva sopra 1x
      'drag_ucits_per_lev' : dict {L: drag_total_per_LEV_UCITS}
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV di calibrazione SSO non trovato: {csv_path}\n"
            f"Salva il file confronto_leva_spy_sso.csv in data/cache/ e rilancia."
        )

    df = pd.read_csv(csv_path, parse_dates=["Date"]).sort_values("Date")
    df = df[df["Price_SSO_Real_2x"].notna() & df["Price_Synthetic_2x"].notna()]

    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    years = (end_date - start_date).days / 365.25

    sso_real_growth = df["Price_SSO_Real_2x"].iloc[-1] / df["Price_SSO_Real_2x"].iloc[0]
    sso_synth_growth = df["Price_Synthetic_2x"].iloc[-1] / df["Price_Synthetic_2x"].iloc[0]

    cagr_real = sso_real_growth ** (1 / years) - 1
    cagr_synth = sso_synth_growth ** (1 / years) - 1

    # Drag totale annualizzato (log-space, robusto al compounding)
    drag_total_2x = (np.log(sso_synth_growth) - np.log(sso_real_growth)) / years
    funding_cost = drag_total_2x - TER_SSO_PROSHARES

    drag_ucits_per_lev = {
        1: TER_UCITS[1],
        2: TER_UCITS[2] + funding_cost,
        3: TER_UCITS[3] + 2 * funding_cost,
    }

    print(f"\nCalibrazione drag dai dati SSO ({csv_path.name}):")
    print(f"  Periodo: {start_date.date()} -> {end_date.date()}  ({years:.2f} anni)")
    print(f"  Crescita SSO reale (2x):       {sso_real_growth:.4f}x   -> CAGR {cagr_real*100:+5.2f}%")
    print(f"  Crescita 2x sintetica (math):  {sso_synth_growth:.4f}x   -> CAGR {cagr_synth*100:+5.2f}%")
    print(f"  Drag totale empirico 2x:       {drag_total_2x*100:+5.2f}%/anno (log-space)")
    print(f"  TER ProShares SSO:             {TER_SSO_PROSHARES*100:5.2f}%")
    print(f"  -> Funding cost per unita':    {funding_cost*100:+5.2f}%/anno")
    print()
    print("  Drag applicato alle simulazioni (versione UCITS, retail italiano):")
    for L, d in drag_ucits_per_lev.items():
        ter = TER_UCITS[L]
        print(f"    {L}x: TER {ter*100:5.2f}%  +  funding ({L-1}x) "
              f"{(L-1)*funding_cost*100:+5.2f}%  =  drag totale {d*100:+5.2f}%/anno")

    return {
        "years": years,
        "cagr_real_2x": float(cagr_real),
        "cagr_synth_2x": float(cagr_synth),
        "drag_total_2x": float(drag_total_2x),
        "ter_sso": TER_SSO_PROSHARES,
        "funding_cost": float(funding_cost),
        "drag_ucits_per_lev": {str(k): float(v) for k, v in drag_ucits_per_lev.items()},
        "calibration_period": {
            "start": str(start_date.date()),
            "end": str(end_date.date()),
        },
    }


# -------------------------------------------------------------------- #
# Metriche                                                             #
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


def volatility_annualized_daily(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(252))


@dataclass
class WindowStats:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr: float
    mdd: float
    vol: float


def rolling_window_stats_levered(
    daily_returns: pd.Series,
    leverage: int,
    window_months: int,
    step_months: int,
    daily_drag: float = 0.0,
) -> list[WindowStats]:
    """
    Per ogni finestra rolling (definita in mesi di calendario), calcola
    CAGR / MDD / vol del NAV a leva costruito da zero su quella finestra.
    `daily_drag` permette di applicare costi quotidiani realistici.
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
        chunk = daily_returns.loc[start_date:end_date]
        if len(chunk) < 50:
            i += step_months
            continue
        nav = levered_nav(chunk, leverage, daily_drag=daily_drag)
        out.append(
            WindowStats(
                start=chunk.index[0],
                end=chunk.index[-1],
                cagr=cagr_from_nav(nav),
                mdd=max_drawdown_from_nav(nav),
                vol=volatility_annualized_daily(leverage * chunk),
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
# Volatility drag teorico (formula analitica)                          #
# -------------------------------------------------------------------- #

def theoretical_drag(L: int, vol_annual: float) -> float:
    """
    Drag annualizzato approssimato di un ETF a leva daily-rebalanced:
        drag ≈ 0.5 * L * (L - 1) * sigma^2
    Dove sigma e' la volatilita' annualizzata del sottostante.
    """
    return 0.5 * L * (L - 1) * vol_annual ** 2


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


def plot_boxplot_cagr(stats_per_lev: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    labels = [f"{L}x" for L in stats_per_lev.keys()]
    data = [stats_per_lev[L]["cagr"] * 100 for L in stats_per_lev.keys()]
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
    for patch, L in zip(bp["boxes"], stats_per_lev.keys()):
        patch.set_facecolor(COLORS[L])
        patch.set_alpha(0.85)
        patch.set_edgecolor("#0f172a")
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    _style_axes(
        ax,
        title=f"CAGR su finestre rolling {window_label} — distribuzione",
        ylabel="CAGR annualizzato (%)",
    )
    ax.text(
        0.99, -0.13,
        "Fonte: Stooq ^SPX + Shiller. Buy & hold a leva daily. Lordo (no TER, no costi funding).",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_drawdown_distribution(stats_per_lev: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    for L, df in stats_per_lev.items():
        sorted_dd = np.sort(df["mdd"].values * 100)
        cdf = np.arange(1, len(sorted_dd) + 1) / len(sorted_dd)
        ax.plot(sorted_dd, cdf * 100, color=COLORS[L], linewidth=2.4, label=f"{L}x")
    ax.legend(frameon=False, fontsize=11, loc="lower right")
    _style_axes(
        ax,
        title=f"Distribuzione del max drawdown — finestre rolling {window_label}",
        ylabel="% di finestre con drawdown ≤ x",
        xlabel="Max drawdown nella finestra (%)",
    )
    ax.text(
        0.99, -0.13,
        "Fonte: Stooq ^SPX + Shiller. Buy & hold a leva daily. Lordo.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_equity_curves(navs_per_lev: dict, fname: Path):
    fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
    for L, nav in navs_per_lev.items():
        ax.plot(nav.index, nav.values, color=COLORS[L], linewidth=2.0, label=f"{L}x")
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    _style_axes(
        ax,
        title="Crescita di 1 USD investito a inizio 1976 (scala log)",
        ylabel="NAV cumulato (scala log)",
    )
    ax.text(
        0.99, -0.13,
        "Fonte: Stooq ^SPX + Shiller. Daily-rebalanced leverage. Buy & hold. Lordo.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_full_period_drawdown(navs_per_lev: dict, fname: Path):
    """Drawdown nel tempo per i 3 livelli di leva, full-period."""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
    for L, nav in navs_per_lev.items():
        peak = nav.cummax()
        dd = (nav / peak - 1) * 100
        ax.plot(dd.index, dd.values, color=COLORS[L], linewidth=1.6, label=f"{L}x", alpha=0.9)
    ax.legend(frameon=False, fontsize=11, loc="lower right")
    _style_axes(
        ax,
        title="Drawdown nel tempo — confronto leva 1x / 2x / 3x",
        ylabel="Drawdown dal massimo (%)",
    )
    ax.set_ylim(-100, 5)
    ax.axhline(0, color="#94a3b8", linewidth=0.8)
    ax.text(
        0.99, -0.13,
        "Fonte: Stooq ^SPX + Shiller. Daily-rebalanced leverage. Lordo.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def compute_full_sample_stats(navs: dict, tr_daily: pd.Series, drag_per_lev: dict) -> dict:
    """Statistiche full-sample per tutti i NAV passati."""
    out = {}
    vol_underlying = volatility_annualized_daily(tr_daily)
    for L, nav in navs.items():
        c = cagr_from_nav(nav)
        m = max_drawdown_from_nav(nav)
        v = volatility_annualized_daily(L * tr_daily)
        drag_theory = theoretical_drag(L, vol_underlying)
        out[str(L)] = {
            "cagr": c, "mdd": m, "vol": v,
            "theoretical_drag_annual": drag_theory,
            "applied_drag_annual": drag_per_lev.get(L, 0.0),
        }
    return out


def compute_rolling_pct(
    tr_daily: pd.Series, drag_per_lev: dict, windows: dict, step: int
) -> tuple[dict, dict]:
    rolling_results = {}
    pct_results = {}
    for win_label, win_months in windows.items():
        rolling_results[win_label] = {}
        pct_results[win_label] = {}
        for L in LEVERAGES:
            daily_drag = drag_per_lev.get(L, 0.0) / 252.0
            stats = rolling_window_stats_levered(
                tr_daily, L, win_months, step, daily_drag=daily_drag
            )
            df = stats_to_df(stats)
            rolling_results[win_label][L] = df
            pct_results[win_label][str(L)] = {
                "cagr": percentiles(df["cagr"]),
                "mdd": percentiles(df["mdd"]),
                "n_windows": int(len(df)),
                "share_negative_cagr": float((df["cagr"] < 0).mean()),
                "share_dd_worse_50pct": float((df["mdd"] < -0.50).mean()),
                "share_dd_worse_75pct": float((df["mdd"] < -0.75).mean()),
            }
    return rolling_results, pct_results


def main():
    print("=" * 64)
    print("SmartMoneyLab — La leva 2x raddoppia? La 3x triplica?")
    print("=" * 64)

    # 1. Carica dati
    price = load_sp500_daily_price()
    shiller_pd = load_shiller_monthly_dividend_yield()
    tr_daily = build_sp500_total_return_daily(price, shiller_pd)

    # 2. Filtra al periodo
    tr_daily = tr_daily.loc[pd.Timestamp(START_DATE):pd.Timestamp(END_DATE)]
    print(f"Periodo: {tr_daily.index.min().date()} -> {tr_daily.index.max().date()}")
    print(f"Giorni disponibili: {len(tr_daily)}")

    # 3. Scenario LORDO: NAV daily-rebalanced senza costi
    navs_gross = {L: levered_nav(tr_daily, L, daily_drag=0.0) for L in LEVERAGES}

    # 4. Calibrazione drag reale empirico dai dati SSO ProShares
    calibration = calibrate_drag_from_sso(SSO_CSV_PATH)
    drag_per_lev = {int(k): float(v) for k, v in calibration["drag_ucits_per_lev"].items()}

    # 5. Scenario REALISTICO: NAV con drag annualizzato applicato daily
    navs_real = {
        L: levered_nav(tr_daily, L, daily_drag=drag_per_lev[L] / 252.0)
        for L in LEVERAGES
    }

    # 6. Statistiche full-sample per ENTRAMBI gli scenari
    print("\n=== SCENARIO LORDO (no costi, no TER, no funding) ===")
    full_gross = compute_full_sample_stats(navs_gross, tr_daily, {L: 0.0 for L in LEVERAGES})
    base_cagr_gross = full_gross["1"]["cagr"]
    for L in LEVERAGES:
        s = full_gross[str(L)]
        print(f"  {L}x  CAGR={s['cagr']*100:6.2f}%  MDD={s['mdd']*100:7.2f}%  "
              f"VOL={s['vol']*100:5.2f}%  drag teorico={s['theoretical_drag_annual']*100:5.2f}%")

    print("\nConfronto CAGR atteso lineare (gross) vs reale (gross):")
    for L in LEVERAGES:
        expected = L * base_cagr_gross
        actual = full_gross[str(L)]["cagr"]
        print(f"  {L}x: atteso {expected*100:6.2f}%  reale {actual*100:6.2f}%  "
              f"gap {(expected-actual)*100:+5.2f}%")

    print("\n=== SCENARIO REALISTICO (drag calibrato da ETF UCITS) ===")
    full_real = compute_full_sample_stats(navs_real, tr_daily, drag_per_lev)
    for L in LEVERAGES:
        s = full_real[str(L)]
        print(f"  {L}x  CAGR={s['cagr']*100:6.2f}%  MDD={s['mdd']*100:7.2f}%  "
              f"VOL={s['vol']*100:5.2f}%  drag applicato={s['applied_drag_annual']*100:5.2f}%/anno")

    base_cagr_real = full_real["1"]["cagr"]
    print("\nConfronto CAGR atteso lineare (real) vs reale (real):")
    for L in LEVERAGES:
        expected = L * base_cagr_real
        actual = full_real[str(L)]["cagr"]
        print(f"  {L}x: atteso {expected*100:6.2f}%  reale {actual*100:6.2f}%  "
              f"gap {(expected-actual)*100:+5.2f}%")

    print("\nDifferenza Gross vs Realistic (CAGR full-sample):")
    for L in LEVERAGES:
        diff = full_gross[str(L)]["cagr"] - full_real[str(L)]["cagr"]
        print(f"  {L}x: gross {full_gross[str(L)]['cagr']*100:6.2f}%  "
              f"real {full_real[str(L)]['cagr']*100:6.2f}%  delta {diff*100:+5.2f}%")

    # 7. Rolling stats per entrambi gli scenari
    print("\nCalcolo rolling stats — scenario LORDO…")
    rolling_gross, pct_gross = compute_rolling_pct(
        tr_daily, {L: 0.0 for L in LEVERAGES}, WINDOWS_MONTHS, STEP_MONTHS,
    )
    print("Calcolo rolling stats — scenario REALISTICO…")
    rolling_real, pct_real = compute_rolling_pct(
        tr_daily, drag_per_lev, WINDOWS_MONTHS, STEP_MONTHS,
    )

    # Stampa breve riepilogo confronto
    for win in ["10y", "20y"]:
        print(f"\nRolling {win} — riepilogo (mediana CAGR & MDD):")
        for L in LEVERAGES:
            cg = pct_gross[win][str(L)]
            cr = pct_real[win][str(L)]
            print(f"  {L}x | gross  CAGR p50={cg['cagr']['p50']*100:6.2f}%  "
                  f"MDD p50={cg['mdd']['p50']*100:7.2f}%  "
                  f"share_neg={cg['share_negative_cagr']*100:5.1f}%")
            print(f"  {L}x | real   CAGR p50={cr['cagr']['p50']*100:6.2f}%  "
                  f"MDD p50={cr['mdd']['p50']*100:7.2f}%  "
                  f"share_neg={cr['share_negative_cagr']*100:5.1f}%")

    # 8. Grafici — manteniamo 5 grafici "gross" + aggiungiamo equity curve
    # comparativa gross vs real e una versione realistica del boxplot 10y/20y
    print("\nGenerazione grafici…")
    # GROSS scenario (default — articolo principale)
    plot_equity_curves(navs_gross, OUT_DIR / "01_equity_curves_gross.png")
    plot_boxplot_cagr(rolling_gross["10y"], "10 anni — lordo",
                      OUT_DIR / "02_boxplot_cagr_10y_gross.png")
    plot_boxplot_cagr(rolling_gross["5y"], "5 anni — lordo",
                      OUT_DIR / "03_boxplot_cagr_5y_gross.png")
    plot_boxplot_cagr(rolling_gross["20y"], "20 anni — lordo",
                      OUT_DIR / "04_boxplot_cagr_20y_gross.png")
    plot_full_period_drawdown(navs_gross, OUT_DIR / "05_drawdown_timeseries_gross.png")
    # REALISTIC scenario
    plot_equity_curves(navs_real, OUT_DIR / "06_equity_curves_realistic.png")
    plot_boxplot_cagr(rolling_real["10y"], "10 anni — realistico (drag ETF)",
                      OUT_DIR / "07_boxplot_cagr_10y_realistic.png")
    plot_boxplot_cagr(rolling_real["20y"], "20 anni — realistico (drag ETF)",
                      OUT_DIR / "08_boxplot_cagr_20y_realistic.png")

    # 9. Salva summary JSON con entrambi gli scenari
    summary = {
        "slug": SLUG,
        "period": {
            "start": str(tr_daily.index.min().date()),
            "end": str(tr_daily.index.max().date()),
            "n_days": int(len(tr_daily)),
        },
        "params": {
            "leverages": LEVERAGES,
            "rolling_step_months": STEP_MONTHS,
            "windows_months": WINDOWS_MONTHS,
            "rebalancing": "daily",
        },
        "calibration": {
            "method": "Empirical drag from ProShares SSO (real 2x ETF) vs synthetic 2x, "
                      "decomposed into TER + funding cost. Funding then applied to UCITS TERs.",
            "ter_sso_proshares": TER_SSO_PROSHARES,
            "ter_ucits": TER_UCITS,
            "sso_calibration_result": calibration,
            "applied_drag_annual_ucits": {str(L): drag_per_lev[L] for L in LEVERAGES},
        },
        "underlying_volatility_annual": volatility_annualized_daily(tr_daily),
        "scenarios": {
            "gross": {
                "description": "No TER, no funding cost — leva matematicamente pura.",
                "full_sample": full_gross,
                "rolling_percentiles": pct_gross,
            },
            "realistic": {
                "description": "Drag annualizzato calibrato da ETF UCITS reali "
                               "(WisdomTree 1x/3x, Xtrackers 2x) sui calendar year 2024-2025.",
                "full_sample": full_real,
                "rolling_percentiles": pct_real,
            },
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    # CSV per audit (campionato mensile)
    csv_df = pd.DataFrame({
        **{f"NAV_{L}x_gross": navs_gross[L] for L in LEVERAGES},
        **{f"NAV_{L}x_real": navs_real[L] for L in LEVERAGES},
    })
    csv_df = csv_df.resample("ME").last()
    csv_df.index.name = "date"
    csv_df.to_csv(OUT_DIR / "data.csv", float_format="%.6f")

    print(f"\nOutput salvati in: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()


# ====================================================================
# FALLBACK MANUALE — se yfinance e Stooq falliscono entrambi
# ====================================================================
#
# Lo script tenta in ordine: yfinance (Yahoo Finance) -> Stooq -> manuale.
# In caso entrambe le fonti automatiche falliscano:
#
# OPZIONE A — yfinance non installato:
#   pip install yfinance
#   poi rilancia lo script.
#
# OPZIONE B — Stooq blocca, yfinance bloccato dalla rete:
#   Il file di cache viene salvato comunque dal download anche se corrotto;
#   se vedi un errore di parsing, cancella PRIMA il file in cache:
#       del data\cache\stooq_spx_daily.csv
#       del data\cache\yahoo_gspc_daily.csv
#   Poi:
#   1. Vai su https://finance.yahoo.com/quote/%5EGSPC/history
#   2. Set "Time period" da 01/01/1976 a oggi.
#   3. Click "Download". Salva il file CSV.
#   4. Rinominalo in: data/cache/yahoo_gspc_daily.csv
#      (il formato standard di Yahoo: Date, Open, High, Low, Close, Adj Close, Volume).
#   5. Rilancia lo script — vedra' il file in cache e lo userà.
#
# OPZIONE C — Stooq UI:
#   1. Vai su https://stooq.com/q/d/?s=%5Espx&i=d
#   2. Click "Download data in csv" (richiede registrazione gratuita).
#   3. Salva come data/cache/stooq_spx_daily.csv
# ====================================================================
# end of file
