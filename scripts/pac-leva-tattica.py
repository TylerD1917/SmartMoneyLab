"""
SmartMoneyLab — PAC con leva tattica: potenziare i rendimenti senza
                peggiorare il profilo di rischio?
====================================================================

Articolo della serie "Battere il mercato?".

Domanda fondamentale:
  E' possibile usare la leva 2x in modo SELETTIVO per potenziare i
  rendimenti di un piano di accumulo senza peggiorarne il profilo di
  rischio?

Strategia testata ("PAC leva tattica"):
  - Contribuzione: $300/mese (DCA classico)
  - Split fisso: 30% NASDAQ + 70% SP500 (su ogni contribuzione)
  - Regola di switch (calcolata SEPARATAMENTE su ogni indice ad ogni
    contribuzione):
      * Se drawdown NASDAQ < 20% dai massimi: $90 in NASDAQ 1x
      * Se drawdown NASDAQ > 20% dai massimi: $90 in NASDAQ 2x
      * Se drawdown SP500  < 20% dai massimi: $210 in SP500 1x
      * Se drawdown SP500  > 20% dai massimi: $210 in SP500 2x
    Lo switch riguarda SOLO le nuove contribuzioni; le posizioni 1x
    esistenti non vengono mai mosse in 2x (e viceversa).
  - Modalita' 2x persiste finche' il drawdown non viene completamente
    riassorbito (nuovo ATH = DD ~ 0).

Benchmark:
  - Buy & hold puro: stesso DCA $300/mese, sempre 30/70 NASDAQ 1x +
    SP500 1x, nessuno switch.

Asset:
  - SP500: yahoo_gspc_daily.csv (^GSPC daily, 1976+) → Total Return
           ricostruito via dividendi Shiller (come negli articoli
           precedenti della serie).
  - NASDAQ: NASDAQCOM.csv (Composite daily, 1971+) → price-only.
           Il dividend yield storico del Composite e' ~1% (vs ~2%
           SP500); usiamo il prezzo nudo. Disclaimer esplicito
           nell'articolo. La comparazione strategia-vs-benchmark
           resta corretta perche' ENTRAMBI usano la stessa serie.

Costruzione ETF sintetici 2x (1976 in avanti):
  - SP500 2x: calibrato in confronto_leva_spy_sso.csv (SSO real vs
              synthetic, 2006+). Drag totale = TER_UCITS_2x + funding.
  - NASDAQ 2x: calibrato a parita' di funding cost (mercato del
               funding e' lo stesso: LIBOR/SOFR overnight). TER UCITS
               leverage Nasdaq-100 = 0.60% (Xtrackers Nasdaq-100 2x).
               In aggiunta tentiamo download QLD via yfinance per
               validazione del funding cost su QQQ vs QLD (2006+).

Daily reset:
  r_2x_t = 2 * r_1x_t - drag_per_day
  drag_per_day = (TER + funding) / 252

Volatility drag: intrinseco al daily reset, NON sottratto
artificialmente. La simulazione lo cattura naturalmente.

Rolling windows: 15y, 20y, 25y. Step: 3 mesi.

Framework 6+1 (come gli altri articoli della serie):
  1. CAGR mediano >= benchmark
  2. Win rate (% finestre con CAGR_strat > CAGR_bench) >= 60%
  3. Volatilita' annualizzata <= benchmark * 1.10
  4. Max Drawdown mediano peggiore <= benchmark * 1.10 (tolleranza 10%)
  5. Sharpe ratio >= benchmark
  6. Calmar ratio (CAGR / |MDD|) >= benchmark
  7. Sortino ratio >= benchmark

Verdict: VINCE 7/7, PARZIALE 4-6/7, NON VINCE <=3/7.

Output:
  public/charts/pac-leva-tattica/
    01_equity_curves.png    — equity curve strategia vs benchmark
    02_cagr_box.png         — distribuzione CAGR rolling per finestra
    03_mdd_box.png          — distribuzione Max DD per finestra
    04_switch_timeline.png  — quando la strategia e' stata in 2x
    05_scorecard.png        — scorecard verdict 6+1
    06_calibration.png      — calibrazione QQQ/QLD e SPY/SSO
    summary.json            — tutti i numeri strutturati
    data.csv                — serie giornaliere per il componente React

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
SLUG = "pac-leva-tattica"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo dell'analisi
START_DATE = "1976-01-01"   # vincolato dall'inizio SP500 daily
END_DATE = "2025-12-31"

# Strategia
DCA_AMOUNT = 300.0          # contribuzione mensile in USD
W_NASDAQ = 0.30             # quota NASDAQ
W_SP500 = 0.70              # quota SP500
DD_THRESHOLD = 0.20         # soglia drawdown per attivare 2x

# Rolling windows
WINDOWS_MONTHS = {"15y": 180, "20y": 240, "25y": 300}
STEP_MONTHS = 3

# Risk-free per Sharpe / Sortino (coerente con resto della serie)
RISK_FREE_ANNUAL = 0.02

# Costi 2x (UCITS, retail italiano)
TER_SSO_PROSHARES = 0.0089  # ProShares Ultra SP500 (US) — per calibrare
TER_QLD_PROSHARES = 0.0095  # ProShares Ultra QQQ (US) — per calibrare
TER_UCITS_SP500_2X = 0.0060   # Xtrackers SP500 2x Leveraged Daily Swap
TER_UCITS_NDX_2X = 0.0060     # Xtrackers Nasdaq-100 2x Leveraged Daily Swap

# Palette articolo (coerente con resto del blog)
COLOR_STRAT = "#d97706"   # ambra — strategia tattica
COLOR_BENCH = "#1e3a8a"   # navy  — buy & hold benchmark
COLOR_NDX = "#3b82f6"     # blu chiaro — NASDAQ
COLOR_SP = "#0f172a"      # quasi-nero — SP500
COLOR_GREY = "#94a3b8"

SHILLER_CSV_MIRROR = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
)

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# -------------------------------------------------------------------- #
# Download utility                                                     #
# -------------------------------------------------------------------- #

def _download(url: str, cache_name: str, retries: int = 3) -> bytes:
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        print(f"[cache] {cache_name}")
        return cache_path.read_bytes()
    headers = {"User-Agent": _BROWSER_UA}
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            print(f"[download {attempt}/{retries}] {url}")
            resp = requests.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            cache_path.write_bytes(resp.content)
            return resp.content
        except Exception as exc:
            last_err = exc
            print(f"  -> failed: {exc}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Download fallito per {cache_name}: {last_err}")


# -------------------------------------------------------------------- #
# Caricamento prezzi                                                   #
# -------------------------------------------------------------------- #

def load_sp500_daily_price() -> pd.Series:
    """Daily close S&P 500 dal cache file gia' esistente."""
    csv_path = CACHE_DIR / "yahoo_gspc_daily.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Manca {csv_path}")
    df = pd.read_csv(csv_path, parse_dates=["Date"]).set_index("Date").sort_index()
    s = pd.to_numeric(df["Close"], errors="coerce").dropna()
    s.name = "sp500_close"
    print(f"[loaded] SP500 daily: {len(s)} righe, "
          f"{s.index[0].date()} -> {s.index[-1].date()}")
    return s


def load_nasdaq_daily_price() -> pd.Series:
    """Daily close NASDAQ Composite dal cache file fornito da Tyler."""
    csv_path = CACHE_DIR / "NASDAQCOM.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Manca {csv_path}")
    df = pd.read_csv(csv_path)
    # Detect colonne (observation_date,NASDAQCOM)
    date_col = next(c for c in df.columns if "date" in c.lower())
    val_col = next(c for c in df.columns if c != date_col)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    s = pd.to_numeric(df[val_col], errors="coerce").dropna()
    s.name = "nasdaq_close"
    print(f"[loaded] NASDAQ daily: {len(s)} righe, "
          f"{s.index[0].date()} -> {s.index[-1].date()}")
    return s


def load_shiller_monthly() -> pd.DataFrame:
    """Shiller monthly: prezzo e dividendi SP500 (per ricostruire TR)."""
    raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
    m = pd.read_csv(io.StringIO(raw))
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
    m = m.set_index("date").sort_index()
    p = pd.to_numeric(m["SP500"], errors="coerce")
    d = pd.to_numeric(m["Dividend"], errors="coerce")
    return pd.DataFrame({"P": p, "D": d}).dropna()


# -------------------------------------------------------------------- #
# Costruzione rendimenti                                               #
# -------------------------------------------------------------------- #

def build_sp500_tr_daily(price: pd.Series, shiller: pd.DataFrame) -> pd.Series:
    """
    SP500 Total Return daily.
    Approccio: per ogni giorno t nel mese m,
        daily_div = D_m / 252 (D_m = dividendo annuale Shiller)
        tr_t = (P_t + daily_div) / P_{t-1} - 1
    """
    shiller = shiller.copy()
    shiller.index = shiller.index.to_period("M").to_timestamp()
    monthly_div = shiller["D"]
    monthly_keys = price.index.to_period("M").to_timestamp()
    daily_div_annual = pd.Series(
        monthly_div.reindex(monthly_keys).values, index=price.index
    )
    daily_div = daily_div_annual / 252.0
    tr = (price + daily_div) / price.shift(1) - 1
    tr = tr.dropna()
    tr.name = "sp500_tr_daily"
    return tr


def build_nasdaq_daily_returns(price: pd.Series) -> pd.Series:
    """
    NASDAQ Composite price-only daily returns.
    NOTA METODOLOGICA: Composite e' un indice di prezzo (no dividendi).
    Dividend yield storico ~1% — uso il prezzo nudo per non introdurre
    stime arbitrarie. La comparazione strategia/benchmark e' invariante
    a questa scelta perche' entrambi usano la stessa serie.
    """
    r = price.pct_change().dropna()
    r.name = "nasdaq_daily"
    return r


def levered_returns(r1x: pd.Series, leverage: float, annual_drag: float) -> pd.Series:
    """
    Rendimenti daily di un ETF a leva con daily reset:
        r_Lx_t = L * r_1x_t - daily_drag
    """
    daily_drag = annual_drag / 252.0
    return leverage * r1x - daily_drag


def nav_from_returns(returns: pd.Series) -> pd.Series:
    """NAV cumulato, NAV(0) = 1."""
    nav = (1.0 + returns).cumprod()
    return nav.clip(lower=1e-12)


# -------------------------------------------------------------------- #
# Calibrazione synthetic 2x                                            #
# -------------------------------------------------------------------- #

def calibrate_sp500_funding() -> dict:
    """
    Funding cost del SP500 2x da SSO vs synthetic 2x sui daily SPY.
    Drag totale = TER_SSO + funding. Estraiamo il funding.
    """
    csv_path = CACHE_DIR / "confronto_leva_spy_sso.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Manca {csv_path}")
    df = pd.read_csv(csv_path, parse_dates=["Date"]).sort_values("Date")
    df = df[df["Price_SSO_Real_2x"].notna() & df["Price_Synthetic_2x"].notna()]
    years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
    real_growth = df["Price_SSO_Real_2x"].iloc[-1] / df["Price_SSO_Real_2x"].iloc[0]
    synth_growth = df["Price_Synthetic_2x"].iloc[-1] / df["Price_Synthetic_2x"].iloc[0]
    drag_total = (np.log(synth_growth) - np.log(real_growth)) / years
    funding = drag_total - TER_SSO_PROSHARES
    info = {
        "source": "confronto_leva_spy_sso.csv",
        "start": str(df["Date"].iloc[0].date()),
        "end": str(df["Date"].iloc[-1].date()),
        "years": float(years),
        "drag_total_sso": float(drag_total),
        "ter_sso": TER_SSO_PROSHARES,
        "funding_cost": float(funding),
    }
    print(f"\n[calibrazione SP500 2x]")
    print(f"  Periodo: {info['start']} -> {info['end']} ({years:.2f} anni)")
    print(f"  Drag totale SSO empirico:  {drag_total*100:+5.2f}%/anno")
    print(f"  TER SSO:                   {TER_SSO_PROSHARES*100:5.2f}%")
    print(f"  Funding cost stimato:      {funding*100:+5.2f}%/anno")
    return info


def calibrate_nasdaq_funding(qqq_qld_csv: Path | None) -> dict:
    """
    Stesso esercizio per QLD vs synthetic 2x su QQQ — se i dati esistono.
    Altrimenti riusiamo il funding cost SP500 (i mercati di funding sono
    gli stessi: LIBOR/SOFR overnight).
    """
    if qqq_qld_csv is None or not qqq_qld_csv.exists():
        print(f"\n[calibrazione NASDAQ 2x] — file QLD non disponibile.")
        print(f"  Riuso del funding cost SP500 (LIBOR/SOFR e' lo stesso).")
        return {"source": "fallback_sp500_funding"}

    df = pd.read_csv(qqq_qld_csv, parse_dates=["Date"]).sort_values("Date")
    # Sintetica 2x da QQQ daily
    df["r_qqq"] = df["QQQ"].pct_change()
    df["synth_2x"] = (1 + 2 * df["r_qqq"] - TER_QLD_PROSHARES / 252).cumprod()
    df = df.dropna(subset=["QLD", "synth_2x"])
    years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
    real_growth = df["QLD"].iloc[-1] / df["QLD"].iloc[0]
    synth_growth = df["synth_2x"].iloc[-1] / df["synth_2x"].iloc[0]
    drag_total = (np.log(synth_growth) - np.log(real_growth)) / years
    # synth_2x include gia' TER_QLD: il drag residuo e' il funding
    funding = drag_total
    info = {
        "source": qqq_qld_csv.name,
        "start": str(df["Date"].iloc[0].date()),
        "end": str(df["Date"].iloc[-1].date()),
        "years": float(years),
        "drag_residual_qld": float(drag_total),
        "ter_qld": TER_QLD_PROSHARES,
        "funding_cost": float(funding),
    }
    print(f"\n[calibrazione NASDAQ 2x]")
    print(f"  Periodo: {info['start']} -> {info['end']} ({years:.2f} anni)")
    print(f"  Drag residuo QLD (post-TER): {drag_total*100:+5.2f}%/anno")
    return info


def try_download_qld_qqq() -> Path | None:
    """
    Prova a scaricare QQQ + QLD via yfinance per validare il funding.
    Salva un CSV in cache. Restituisce il path se ce la fa, altrimenti
    None.
    """
    csv_path = CACHE_DIR / "qqq_qld_daily.csv"
    if csv_path.exists():
        print(f"[cache] qqq_qld_daily.csv")
        return csv_path
    try:
        import yfinance as yf
    except ImportError:
        print("[info] yfinance non installato → salto download QLD/QQQ.")
        return None
    try:
        print("[yfinance] download QQQ + QLD (2006-06-21 →)…")
        data = yf.download(
            ["QQQ", "QLD"],
            start="2006-06-21",
            end=END_DATE,
            interval="1d",
            auto_adjust=True,
            progress=False,
            group_by="ticker",
        )
        if data is None or data.empty:
            print("[yfinance] dati vuoti.")
            return None
        # Estrai Close adjusted di entrambi
        try:
            qqq = data["QQQ"]["Close"]
            qld = data["QLD"]["Close"]
        except Exception:
            # fallback singolo livello
            qqq = data["Close"]["QQQ"] if "QQQ" in data["Close"] else None
            qld = data["Close"]["QLD"] if "QLD" in data["Close"] else None
            if qqq is None or qld is None:
                return None
        out = pd.DataFrame({"QQQ": qqq, "QLD": qld}).dropna()
        out.index.name = "Date"
        out.to_csv(csv_path)
        print(f"[yfinance] salvato {csv_path.name} ({len(out)} righe)")
        return csv_path
    except Exception as exc:
        print(f"[yfinance] fallito: {exc}")
        return None


# -------------------------------------------------------------------- #
# Simulazione DCA con switch tattico                                   #
# -------------------------------------------------------------------- #

@dataclass
class SimResult:
    """Output di una simulazione DCA."""
    dates: pd.DatetimeIndex            # date daily della simulazione
    portfolio_value: pd.Series         # valore portafoglio giornaliero
    monthly_dates: list                # date in cui si contribuisce
    in_2x_ndx: list                    # bool: NDX in 2x a quella data
    in_2x_sp: list                     # bool: SP500 in 2x a quella data
    dd_ndx_at_contrib: list            # DD NDX al momento contribuzione
    dd_sp_at_contrib: list             # DD SP500 al momento contribuzione
    total_contributed: float
    final_value: float


def _monthly_contribution_dates(idx: pd.DatetimeIndex) -> list:
    """Primo giorno di trading di ogni mese nell'indice."""
    by_month = pd.Series(idx).groupby(idx.to_period("M"))
    return [g.min() for _, g in by_month]


def simulate_pac(
    ndx_1x_nav: pd.Series,
    ndx_2x_nav: pd.Series,
    sp_1x_nav: pd.Series,
    sp_2x_nav: pd.Series,
    *,
    tactical: bool,
    dd_threshold: float = DD_THRESHOLD,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> SimResult:
    """
    Simula un DCA $300/mese (90 NDX + 210 SP500) su un periodo.

    `tactical=True`:  switch a 2x quando DD>20% (separato per indice).
                      Solo nuove contribuzioni passano a 2x.
    `tactical=False`: buy & hold puro, sempre 1x 1x.

    Drawdown:
      - calcolato sulla serie 1x dell'indice corrispondente
      - dai massimi raggiunti dall'inizio della finestra simulata
        (rolling max within window)
    """
    # Allineo le 4 NAV su un indice comune
    all_idx = (
        ndx_1x_nav.index
        .intersection(ndx_2x_nav.index)
        .intersection(sp_1x_nav.index)
        .intersection(sp_2x_nav.index)
    )
    if start is not None:
        all_idx = all_idx[all_idx >= start]
    if end is not None:
        all_idx = all_idx[all_idx <= end]
    if len(all_idx) < 252:
        raise ValueError("Periodo troppo corto per la simulazione.")

    ndx1 = ndx_1x_nav.reindex(all_idx).ffill()
    ndx2 = ndx_2x_nav.reindex(all_idx).ffill()
    sp1 = sp_1x_nav.reindex(all_idx).ffill()
    sp2 = sp_2x_nav.reindex(all_idx).ffill()

    # Drawdown reference: indice 1x dell'indice corrispondente.
    # I massimi sono "cumulati DALL'INIZIO DELLA FINESTRA" (non assoluti
    # dal 1976) — ogni finestra rolling vede solo il proprio passato.
    ndx_peak = ndx1.cummax()
    sp_peak = sp1.cummax()
    ndx_dd = ndx1 / ndx_peak - 1.0
    sp_dd = sp1 / sp_peak - 1.0

    # Quote possedute (in unita' di NAV, NAV(0)=1 → 1 unita' = $1
    # iniziale, ma qui contribuiamo a NAV correnti). Manteniamo 4
    # accumulator separati.
    units_ndx1 = 0.0
    units_ndx2 = 0.0
    units_sp1 = 0.0
    units_sp2 = 0.0

    monthly_dates = _monthly_contribution_dates(all_idx)
    in_2x_ndx_hist, in_2x_sp_hist = [], []
    dd_ndx_hist, dd_sp_hist = [], []

    total_contrib = 0.0
    contrib_ndx = DCA_AMOUNT * W_NASDAQ
    contrib_sp = DCA_AMOUNT * W_SP500

    for d in monthly_dates:
        dd_n = float(ndx_dd.loc[d])
        dd_s = float(sp_dd.loc[d])
        # NB: drawdown e' negativo (es. -0.25 = -25%). Soglia 20% =>
        # confronto su |dd| > 0.20 oppure dd < -0.20.
        use_2x_ndx = tactical and (dd_n < -dd_threshold)
        use_2x_sp = tactical and (dd_s < -dd_threshold)

        if use_2x_ndx:
            units_ndx2 += contrib_ndx / float(ndx2.loc[d])
        else:
            units_ndx1 += contrib_ndx / float(ndx1.loc[d])

        if use_2x_sp:
            units_sp2 += contrib_sp / float(sp2.loc[d])
        else:
            units_sp1 += contrib_sp / float(sp1.loc[d])

        total_contrib += DCA_AMOUNT
        in_2x_ndx_hist.append(bool(use_2x_ndx))
        in_2x_sp_hist.append(bool(use_2x_sp))
        dd_ndx_hist.append(dd_n)
        dd_sp_hist.append(dd_s)

    # Valore portafoglio daily (somma dei 4 sleeve)
    pv = (
        units_ndx1 * ndx1
        + units_ndx2 * ndx2
        + units_sp1 * sp1
        + units_sp2 * sp2
    )
    pv.name = "portfolio_value"

    return SimResult(
        dates=all_idx,
        portfolio_value=pv,
        monthly_dates=monthly_dates,
        in_2x_ndx=in_2x_ndx_hist,
        in_2x_sp=in_2x_sp_hist,
        dd_ndx_at_contrib=dd_ndx_hist,
        dd_sp_at_contrib=dd_sp_hist,
        total_contributed=total_contrib,
        final_value=float(pv.iloc[-1]),
    )


# -------------------------------------------------------------------- #
# Metriche                                                             #
# -------------------------------------------------------------------- #

def dca_cagr_irr(monthly_dates: list, total_contrib: float,
                 final_value: float, n_years: float) -> float:
    """
    CAGR equivalente per un DCA: tasso che porta la somma dei
    contributi (al loro valore originale) a coincidere con il
    valore finale, su un periodo medio "duration".

    Approssimazione semplice: money-weighted IRR su flussi mensili
    costanti negativi piu' un flusso positivo finale.

    Risolto via Newton con bracket.
    """
    if final_value <= 0:
        return float("nan")
    # Costruisci flussi: t = mesi da inizio
    n_months = len(monthly_dates)
    if n_months < 2:
        return float("nan")
    cashflows = np.array([-DCA_AMOUNT] * n_months + [final_value])
    # tempi in anni: 0, 1/12, 2/12, ..., n_months/12 (final value alla fine)
    t = np.append(np.arange(n_months) / 12.0, n_years)

    def npv(r):
        return float(np.sum(cashflows / (1 + r) ** t))

    # Bracket
    lo, hi = -0.99, 5.0
    if npv(lo) * npv(hi) > 0:
        # Se la soluzione non e' nel bracket standard, ritorna NaN
        return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        v = npv(mid)
        if abs(v) < 1e-6:
            return float(mid)
        if v > 0:
            lo = mid
        else:
            hi = mid
    return float((lo + hi) / 2)


def max_drawdown(series: pd.Series) -> float:
    peak = series.cummax()
    return float((series / peak - 1).min())


def daily_returns_from_pv(pv: pd.Series) -> pd.Series:
    """Rendimenti daily di un portafoglio DCA: pv_t / pv_{t-1} - 1
    NON e' rendimento "puro" perche' include i versamenti, ma e'
    sufficiente per Sharpe/Sortino su una proxy di volatilita'.
    Per il calcolo accurato di Sharpe sui DCA, usiamo IRR-based CAGR
    e volatilita' sui returns daily della parte "equity" (vedi sotto)."""
    return pv.pct_change().dropna()


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(252))


def downside_vol(returns: pd.Series) -> float:
    neg = returns[returns < 0]
    if len(neg) == 0:
        return 0.0
    return float(neg.std() * np.sqrt(252))


def sharpe(cagr: float, vol: float, rf: float = RISK_FREE_ANNUAL) -> float:
    if vol <= 0 or np.isnan(vol):
        return float("nan")
    return (cagr - rf) / vol


def sortino(cagr: float, dvol: float, rf: float = RISK_FREE_ANNUAL) -> float:
    if dvol <= 0 or np.isnan(dvol):
        return float("nan")
    return (cagr - rf) / dvol


def calmar(cagr: float, mdd: float) -> float:
    if mdd >= 0 or np.isnan(mdd):
        return float("nan")
    return cagr / abs(mdd)


# -------------------------------------------------------------------- #
# Rolling windows                                                      #
# -------------------------------------------------------------------- #

@dataclass
class WindowMetrics:
    start: pd.Timestamp
    end: pd.Timestamp
    cagr_strat: float
    cagr_bench: float
    mdd_strat: float
    mdd_bench: float
    vol_strat: float
    vol_bench: float
    dvol_strat: float
    dvol_bench: float
    final_strat: float
    final_bench: float
    contributed: float
    months_in_2x_ndx: int
    months_in_2x_sp: int
    months_total: int


def rolling_metrics(
    ndx1, ndx2, sp1, sp2, *,
    window_months: int, step_months: int,
) -> list[WindowMetrics]:
    """Per ogni finestra rolling, esegue strategia + benchmark e calcola
    tutte le metriche."""
    common_idx = (
        ndx1.index.intersection(ndx2.index)
        .intersection(sp1.index).intersection(sp2.index)
    )
    monthly_starts = pd.Series(common_idx).groupby(
        common_idx.to_period("M")
    ).min().values
    monthly_starts = pd.DatetimeIndex(monthly_starts).sort_values()
    n_months = len(monthly_starts)

    out = []
    i = 0
    while i + window_months <= n_months:
        s_date = monthly_starts[i]
        e_idx = i + window_months - 1
        if e_idx + 1 < n_months:
            e_date = monthly_starts[e_idx + 1] - pd.Timedelta(days=1)
        else:
            e_date = common_idx[-1]

        try:
            strat = simulate_pac(
                ndx1, ndx2, sp1, sp2,
                tactical=True, start=s_date, end=e_date,
            )
            bench = simulate_pac(
                ndx1, ndx2, sp1, sp2,
                tactical=False, start=s_date, end=e_date,
            )
        except ValueError:
            i += step_months
            continue

        n_years = window_months / 12.0
        # CAGR money-weighted
        cagr_s = dca_cagr_irr(
            strat.monthly_dates, strat.total_contributed,
            strat.final_value, n_years,
        )
        cagr_b = dca_cagr_irr(
            bench.monthly_dates, bench.total_contributed,
            bench.final_value, n_years,
        )

        ret_s = daily_returns_from_pv(strat.portfolio_value)
        ret_b = daily_returns_from_pv(bench.portfolio_value)

        out.append(WindowMetrics(
            start=s_date,
            end=e_date,
            cagr_strat=cagr_s,
            cagr_bench=cagr_b,
            mdd_strat=max_drawdown(strat.portfolio_value),
            mdd_bench=max_drawdown(bench.portfolio_value),
            vol_strat=annualized_vol(ret_s),
            vol_bench=annualized_vol(ret_b),
            dvol_strat=downside_vol(ret_s),
            dvol_bench=downside_vol(ret_b),
            final_strat=strat.final_value,
            final_bench=bench.final_value,
            contributed=strat.total_contributed,
            months_in_2x_ndx=sum(strat.in_2x_ndx),
            months_in_2x_sp=sum(strat.in_2x_sp),
            months_total=len(strat.monthly_dates),
        ))
        i += step_months
    return out


def windows_to_df(ws: list[WindowMetrics]) -> pd.DataFrame:
    return pd.DataFrame([{
        "start": w.start, "end": w.end,
        "cagr_strat": w.cagr_strat, "cagr_bench": w.cagr_bench,
        "mdd_strat": w.mdd_strat, "mdd_bench": w.mdd_bench,
        "vol_strat": w.vol_strat, "vol_bench": w.vol_bench,
        "dvol_strat": w.dvol_strat, "dvol_bench": w.dvol_bench,
        "final_strat": w.final_strat, "final_bench": w.final_bench,
        "contributed": w.contributed,
        "months_in_2x_ndx": w.months_in_2x_ndx,
        "months_in_2x_sp": w.months_in_2x_sp,
        "months_total": w.months_total,
        "frac_2x_ndx": w.months_in_2x_ndx / max(1, w.months_total),
        "frac_2x_sp": w.months_in_2x_sp / max(1, w.months_total),
    } for w in ws])


# -------------------------------------------------------------------- #
# Framework 6+1 scorecard                                              #
# -------------------------------------------------------------------- #

def scorecard_6plus1(df: pd.DataFrame) -> dict:
    """Calcola le 7 metriche del framework su una finestra rolling."""
    cagr_s_med = float(df["cagr_strat"].median())
    cagr_b_med = float(df["cagr_bench"].median())
    win_rate = float((df["cagr_strat"] > df["cagr_bench"]).mean())
    vol_s_med = float(df["vol_strat"].median())
    vol_b_med = float(df["vol_bench"].median())
    mdd_s_med = float(df["mdd_strat"].median())
    mdd_b_med = float(df["mdd_bench"].median())
    dvol_s_med = float(df["dvol_strat"].median())
    dvol_b_med = float(df["dvol_bench"].median())

    sharpe_s = sharpe(cagr_s_med, vol_s_med)
    sharpe_b = sharpe(cagr_b_med, vol_b_med)
    calmar_s = calmar(cagr_s_med, mdd_s_med)
    calmar_b = calmar(cagr_b_med, mdd_b_med)
    sortino_s = sortino(cagr_s_med, dvol_s_med)
    sortino_b = sortino(cagr_b_med, dvol_b_med)

    checks = {
        "cagr": cagr_s_med >= cagr_b_med,
        "win_rate": win_rate >= 0.60,
        "vol": vol_s_med <= vol_b_med * 1.10,
        # MDD: piu' negativo = peggio. tolleranza +10% in valore assoluto.
        "mdd": abs(mdd_s_med) <= abs(mdd_b_med) * 1.10,
        "sharpe": sharpe_s >= sharpe_b,
        "calmar": calmar_s >= calmar_b,
        "sortino": sortino_s >= sortino_b,
    }
    passed = sum(checks.values())
    if passed == 7:
        verdict = "VINCE"
    elif passed >= 4:
        verdict = "PARZIALE"
    else:
        verdict = "NON VINCE"

    return {
        "metrics": {
            "cagr_strat_med": cagr_s_med, "cagr_bench_med": cagr_b_med,
            "win_rate": win_rate,
            "vol_strat_med": vol_s_med, "vol_bench_med": vol_b_med,
            "mdd_strat_med": mdd_s_med, "mdd_bench_med": mdd_b_med,
            "sharpe_strat": sharpe_s, "sharpe_bench": sharpe_b,
            "calmar_strat": calmar_s, "calmar_bench": calmar_b,
            "sortino_strat": sortino_s, "sortino_bench": sortino_b,
        },
        "checks": {k: bool(v) for k, v in checks.items()},
        "passed": int(passed),
        "verdict": verdict,
    }


# -------------------------------------------------------------------- #
# Grafici                                                              #
# -------------------------------------------------------------------- #

def _style(ax, title: str, ylabel: str = "", xlabel: str = ""):
    ax.set_title(title, fontsize=14, fontweight="semibold",
                 color="#0f172a", pad=14)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, color="#334155")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color="#334155")
    ax.tick_params(colors="#475569", labelsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#cbd5e1")
    ax.grid(True, axis="y", color="#e2e8f0", linewidth=0.7)
    ax.set_axisbelow(True)


def plot_equity_full(strat: SimResult, bench: SimResult, fname: Path):
    fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
    ax.plot(strat.portfolio_value.index, strat.portfolio_value.values,
            color=COLOR_STRAT, linewidth=1.8, label="PAC leva tattica")
    ax.plot(bench.portfolio_value.index, bench.portfolio_value.values,
            color=COLOR_BENCH, linewidth=1.8, label="Buy & hold 30/70")
    # Linea contribuito cumulato
    cum_contrib = pd.Series(
        [DCA_AMOUNT * (i + 1) for i in range(len(strat.monthly_dates))],
        index=strat.monthly_dates,
    )
    ax.plot(cum_contrib.index, cum_contrib.values,
            color=COLOR_GREY, linewidth=1.0, linestyle="--",
            label="Contributi cumulati")
    _style(ax, f"Equity curve — DCA ${DCA_AMOUNT:.0f}/mese — "
               f"{strat.portfolio_value.index[0].year}–"
               f"{strat.portfolio_value.index[-1].year}",
           ylabel="Valore portafoglio (USD)")
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_cagr_box(windows_by_label: dict, fname: Path):
    fig, axes = plt.subplots(1, len(windows_by_label),
                             figsize=(5.5 * len(windows_by_label), 6),
                             dpi=200, sharey=True)
    if len(windows_by_label) == 1:
        axes = [axes]
    for ax, (label, df) in zip(axes, windows_by_label.items()):
        data = [df["cagr_strat"] * 100, df["cagr_bench"] * 100]
        bp = ax.boxplot(
            data, tick_labels=["Tattica", "B&H"],
            patch_artist=True, widths=0.55,
            medianprops=dict(color="#0f172a", linewidth=2),
            whiskerprops=dict(color="#475569"),
            capprops=dict(color="#475569"),
            flierprops=dict(marker="o", markerfacecolor="#94a3b8",
                            markeredgecolor="none", markersize=4, alpha=0.5),
        )
        for patch, c in zip(bp["boxes"], [COLOR_STRAT, COLOR_BENCH]):
            patch.set_facecolor(c)
            patch.set_alpha(0.85)
            patch.set_edgecolor("#0f172a")
        ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
        _style(ax, f"Finestre rolling {label}",
               ylabel="CAGR money-weighted (%)")
    fig.suptitle("Distribuzione CAGR — leva tattica vs buy & hold",
                 fontsize=15, fontweight="semibold", color="#0f172a", y=1.02)
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_mdd_box(windows_by_label: dict, fname: Path):
    fig, axes = plt.subplots(1, len(windows_by_label),
                             figsize=(5.5 * len(windows_by_label), 6),
                             dpi=200, sharey=True)
    if len(windows_by_label) == 1:
        axes = [axes]
    for ax, (label, df) in zip(axes, windows_by_label.items()):
        data = [df["mdd_strat"] * 100, df["mdd_bench"] * 100]
        bp = ax.boxplot(
            data, tick_labels=["Tattica", "B&H"],
            patch_artist=True, widths=0.55,
            medianprops=dict(color="#0f172a", linewidth=2),
            whiskerprops=dict(color="#475569"),
            capprops=dict(color="#475569"),
            flierprops=dict(marker="o", markerfacecolor="#94a3b8",
                            markeredgecolor="none", markersize=4, alpha=0.5),
        )
        for patch, c in zip(bp["boxes"], [COLOR_STRAT, COLOR_BENCH]):
            patch.set_facecolor(c)
            patch.set_alpha(0.85)
            patch.set_edgecolor("#0f172a")
        _style(ax, f"Finestre rolling {label}", ylabel="Max Drawdown (%)")
    fig.suptitle("Distribuzione Max Drawdown — leva tattica vs buy & hold",
                 fontsize=15, fontweight="semibold", color="#0f172a", y=1.02)
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_switch_timeline(strat: SimResult, fname: Path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), dpi=200,
                                    sharex=True)
    dates = pd.DatetimeIndex(strat.monthly_dates)
    ax1.fill_between(dates, 0, [1 if x else 0 for x in strat.in_2x_ndx],
                     step="post", color=COLOR_STRAT, alpha=0.85, linewidth=0)
    ax1.set_ylim(0, 1.2)
    ax1.set_yticks([])
    _style(ax1, "Quando la quota NASDAQ era in 2x")
    ax2.fill_between(dates, 0, [1 if x else 0 for x in strat.in_2x_sp],
                     step="post", color=COLOR_BENCH, alpha=0.85, linewidth=0)
    ax2.set_ylim(0, 1.2)
    ax2.set_yticks([])
    _style(ax2, "Quando la quota SP500 era in 2x")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_scorecard(scorecards: dict, fname: Path):
    """Tabella visuale dei 7 check su 15/20/25y."""
    labels = ["CAGR", "Win rate", "Vol", "Max DD", "Sharpe", "Calmar", "Sortino"]
    keys = ["cagr", "win_rate", "vol", "mdd", "sharpe", "calmar", "sortino"]
    win_labels = list(scorecards.keys())

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
    ax.set_xlim(0, len(win_labels) + 1)
    ax.set_ylim(0, len(labels) + 2)
    ax.axis("off")

    # Header
    ax.text(0.05, len(labels) + 0.6, "Criterio", fontsize=12,
            fontweight="semibold", color="#0f172a")
    for j, wl in enumerate(win_labels):
        ax.text(1 + j + 0.5, len(labels) + 0.6, wl, fontsize=12,
                fontweight="semibold", color="#0f172a", ha="center")

    for i, (lab, key) in enumerate(zip(labels, keys)):
        y = len(labels) - i - 0.5
        ax.text(0.05, y, lab, fontsize=11, color="#334155", va="center")
        for j, wl in enumerate(win_labels):
            sc = scorecards[wl]
            ok = sc["checks"][key]
            x = 1 + j + 0.5
            color = "#16a34a" if ok else "#dc2626"
            ax.scatter([x], [y], s=380, color=color, alpha=0.85,
                       edgecolors="#0f172a", linewidths=0.5)
            ax.text(x, y, "OK" if ok else "X", fontsize=10,
                    fontweight="bold", color="white", ha="center", va="center")

    # Verdict
    y_v = -0.6
    ax.text(0.05, y_v, "Verdict", fontsize=12,
            fontweight="semibold", color="#0f172a")
    verdict_color = {"VINCE": "#16a34a", "PARZIALE": "#d97706",
                     "NON VINCE": "#dc2626"}
    for j, wl in enumerate(win_labels):
        sc = scorecards[wl]
        c = verdict_color.get(sc["verdict"], "#475569")
        ax.text(1 + j + 0.5, y_v, f"{sc['verdict']}\n({sc['passed']}/7)",
                fontsize=10, fontweight="bold", color=c,
                ha="center", va="center")

    ax.text(0, len(labels) + 1.4,
            "Framework 6+1 — leva tattica vs buy & hold 30/70",
            fontsize=14, fontweight="semibold", color="#0f172a")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_percentile_fans(windows_by_label: dict, fname: Path):
    """
    Per ciascuna finestra rolling, mostra una "fan" del CAGR a percentili
    p5/p25/p50/p75/p95 per strategia e benchmark. Asimmetria del payoff
    visualizzata in un colpo d'occhio.
    """
    fig, axes = plt.subplots(1, len(windows_by_label),
                             figsize=(5.5 * len(windows_by_label), 6),
                             dpi=200, sharey=True)
    if len(windows_by_label) == 1:
        axes = [axes]
    qs = [0.05, 0.25, 0.50, 0.75, 0.95]
    q_labels = ["p5", "p25", "p50", "p75", "p95"]

    for ax, (label, df) in zip(axes, windows_by_label.items()):
        x_strat = 0.25
        x_bench = 0.75
        strat_vals = [df["cagr_strat"].quantile(q) * 100 for q in qs]
        bench_vals = [df["cagr_bench"].quantile(q) * 100 for q in qs]

        # Strategia
        ax.fill_between([x_strat - 0.18, x_strat + 0.18],
                        [strat_vals[0]] * 2, [strat_vals[4]] * 2,
                        color=COLOR_STRAT, alpha=0.15)
        ax.fill_between([x_strat - 0.18, x_strat + 0.18],
                        [strat_vals[1]] * 2, [strat_vals[3]] * 2,
                        color=COLOR_STRAT, alpha=0.45)
        ax.plot([x_strat - 0.18, x_strat + 0.18],
                [strat_vals[2]] * 2, color=COLOR_STRAT, linewidth=2.5)

        # Benchmark
        ax.fill_between([x_bench - 0.18, x_bench + 0.18],
                        [bench_vals[0]] * 2, [bench_vals[4]] * 2,
                        color=COLOR_BENCH, alpha=0.15)
        ax.fill_between([x_bench - 0.18, x_bench + 0.18],
                        [bench_vals[1]] * 2, [bench_vals[3]] * 2,
                        color=COLOR_BENCH, alpha=0.45)
        ax.plot([x_bench - 0.18, x_bench + 0.18],
                [bench_vals[2]] * 2, color=COLOR_BENCH, linewidth=2.5)

        # Etichette percentili sulla strategia
        for q_lab, v in zip(q_labels, strat_vals):
            ax.annotate(f"{q_lab}: {v:.1f}%",
                        xy=(x_strat - 0.20, v),
                        xytext=(-4, 0), textcoords="offset points",
                        fontsize=8, ha="right", va="center", color="#475569")
        # Etichette sul benchmark
        for q_lab, v in zip(q_labels, bench_vals):
            ax.annotate(f"{q_lab}: {v:.1f}%",
                        xy=(x_bench + 0.20, v),
                        xytext=(4, 0), textcoords="offset points",
                        fontsize=8, ha="left", va="center", color="#475569")

        ax.set_xlim(0, 1)
        ax.set_xticks([x_strat, x_bench])
        ax.set_xticklabels(["Tattica", "B&H"])
        ax.axhline(0, color="#94a3b8", linewidth=0.6, linestyle="--")
        _style(ax, f"Finestre rolling {label}",
               ylabel="CAGR money-weighted (%)")

    fig.suptitle("Distribuzione CAGR a percentili — leva tattica vs buy & hold",
                 fontsize=15, fontweight="semibold", color="#0f172a", y=1.02)
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_asymmetry(windows_by_label: dict, fname: Path):
    """
    Per ogni finestra, mostra la distribuzione del rapporto
    final_strat / final_bench. >1 = tattica ha vinto.
    Mette in evidenza la asimmetria del payoff: quanto puoi perdere nel
    peggior caso vs quanto puoi guadagnare nel migliore.
    """
    fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
    win_labels = list(windows_by_label.keys())
    positions = list(range(1, len(win_labels) + 1))
    data = []
    for label in win_labels:
        df = windows_by_label[label]
        ratio = df["final_strat"] / df["final_bench"]
        data.append((ratio - 1) * 100)  # eccesso in %

    bp = ax.boxplot(
        data, positions=positions, widths=0.55,
        tick_labels=win_labels,
        patch_artist=True,
        medianprops=dict(color="#0f172a", linewidth=2),
        whiskerprops=dict(color="#475569"),
        capprops=dict(color="#475569"),
        flierprops=dict(marker="o", markerfacecolor="#94a3b8",
                        markeredgecolor="none", markersize=4, alpha=0.5),
        whis=(5, 95),
    )
    for patch in bp["boxes"]:
        patch.set_facecolor(COLOR_STRAT)
        patch.set_alpha(0.8)
        patch.set_edgecolor("#0f172a")
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    ax.set_ylabel("Eccesso valore finale tattica vs B&H (%)",
                  fontsize=11, color="#334155")
    # Annotazioni p5 / p95
    for pos, label in zip(positions, win_labels):
        df = windows_by_label[label]
        ratio = df["final_strat"] / df["final_bench"]
        p5 = (ratio.quantile(0.05) - 1) * 100
        p95 = (ratio.quantile(0.95) - 1) * 100
        med = (ratio.median() - 1) * 100
        ax.annotate(f"p5  {p5:+.1f}%",
                    xy=(pos, p5), xytext=(8, -2), textcoords="offset points",
                    fontsize=9, color="#475569")
        ax.annotate(f"p50 {med:+.1f}%",
                    xy=(pos, med), xytext=(8, -2), textcoords="offset points",
                    fontsize=9, color="#0f172a", fontweight="semibold")
        ax.annotate(f"p95 {p95:+.1f}%",
                    xy=(pos, p95), xytext=(8, -2), textcoords="offset points",
                    fontsize=9, color=COLOR_STRAT, fontweight="semibold")
    _style(ax, "Asimmetria del payoff — premio relativo della tattica per finestra",
           xlabel="Finestra rolling")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_calibration(calib_sp500: dict, calib_ndx: dict | None,
                     fname: Path):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    ax.axis("off")
    txt = []
    txt.append("Calibrazione costi ETF sintetici 2x")
    txt.append("")
    txt.append("SP500 2x — da SSO (ProShares Ultra S&P 500)")
    txt.append(f"  Periodo:  {calib_sp500['start']} → {calib_sp500['end']} "
               f"({calib_sp500['years']:.1f} anni)")
    txt.append(f"  Drag totale SSO empirico: {calib_sp500['drag_total_sso']*100:+5.2f}%/anno")
    txt.append(f"  TER SSO (US):             {calib_sp500['ter_sso']*100:5.2f}%/anno")
    txt.append(f"  Funding cost stimato:     {calib_sp500['funding_cost']*100:+5.2f}%/anno")
    txt.append(f"  → Drag applicato (UCITS): "
               f"{(TER_UCITS_SP500_2X + calib_sp500['funding_cost'])*100:+5.2f}%/anno")
    txt.append(f"    (TER UCITS {TER_UCITS_SP500_2X*100:.2f}% + funding "
               f"{calib_sp500['funding_cost']*100:+.2f}%)")
    txt.append("")
    if calib_ndx and "drag_residual_qld" in calib_ndx:
        txt.append("NASDAQ 2x — da QLD (ProShares Ultra QQQ)")
        txt.append(f"  Periodo:  {calib_ndx['start']} → {calib_ndx['end']} "
                   f"({calib_ndx['years']:.1f} anni)")
        txt.append(f"  Drag residuo QLD vs synth (post-TER): "
                   f"{calib_ndx['drag_residual_qld']*100:+5.2f}%/anno")
        txt.append(f"  Funding cost (QLD):       {calib_ndx['funding_cost']*100:+5.2f}%/anno")
        txt.append(f"  → Drag applicato (UCITS): "
                   f"{(TER_UCITS_NDX_2X + calib_ndx['funding_cost'])*100:+5.2f}%/anno")
    else:
        txt.append("NASDAQ 2x — fallback")
        txt.append(f"  yfinance QLD non scaricato, riuso funding SP500.")
        txt.append(f"  → Drag applicato (UCITS): "
                   f"{(TER_UCITS_NDX_2X + calib_sp500['funding_cost'])*100:+5.2f}%/anno")
    ax.text(0.02, 0.98, "\n".join(txt), va="top", ha="left",
            family="monospace", fontsize=11, color="#0f172a")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def main() -> None:
    print("=" * 68)
    print(f"  {SLUG}")
    print("=" * 68)

    # 1. Carico prezzi
    sp_price = load_sp500_daily_price()
    nq_price = load_nasdaq_daily_price()
    shiller = load_shiller_monthly()

    # 2. Allineo periodo
    sp_price = sp_price.loc[START_DATE:END_DATE]
    nq_price = nq_price.loc[START_DATE:END_DATE]

    # 3. Calcolo rendimenti daily 1x
    sp_tr = build_sp500_tr_daily(sp_price, shiller)
    nq_r = build_nasdaq_daily_returns(nq_price)

    # Allineo indici
    common = sp_tr.index.intersection(nq_r.index)
    sp_tr = sp_tr.reindex(common)
    nq_r = nq_r.reindex(common)
    print(f"\nPeriodo comune effettivo: {common[0].date()} → {common[-1].date()} "
          f"({len(common)} giorni di trading)")

    # 4. Calibrazione synthetic 2x
    calib_sp = calibrate_sp500_funding()
    qld_path = try_download_qld_qqq()
    calib_nq = calibrate_nasdaq_funding(qld_path)

    funding_sp = calib_sp["funding_cost"]
    funding_nq = calib_nq.get("funding_cost", funding_sp)

    drag_sp_2x = TER_UCITS_SP500_2X + funding_sp
    drag_nq_2x = TER_UCITS_NDX_2X + funding_nq
    drag_1x = 0.0  # implicito nei prezzi: usiamo TER=0 per il sottostante
                   #  (la differenza con TER 0.05% e' trascurabile su 50y)

    print(f"\n[drag finali applicati alla simulazione]")
    print(f"  SP500 1x:  {drag_1x*100:5.2f}%/anno")
    print(f"  SP500 2x:  {drag_sp_2x*100:+5.2f}%/anno"
          f" (TER {TER_UCITS_SP500_2X*100:.2f}% + funding {funding_sp*100:+.2f}%)")
    print(f"  NASDAQ 1x: {drag_1x*100:5.2f}%/anno")
    print(f"  NASDAQ 2x: {drag_nq_2x*100:+5.2f}%/anno"
          f" (TER {TER_UCITS_NDX_2X*100:.2f}% + funding {funding_nq*100:+.2f}%)")

    # 5. NAV 1x e 2x per entrambi gli indici
    sp_1x_r = levered_returns(sp_tr, 1.0, drag_1x)
    sp_2x_r = levered_returns(sp_tr, 2.0, drag_sp_2x)
    nq_1x_r = levered_returns(nq_r, 1.0, drag_1x)
    nq_2x_r = levered_returns(nq_r, 2.0, drag_nq_2x)

    sp_1x_nav = nav_from_returns(sp_1x_r)
    sp_2x_nav = nav_from_returns(sp_2x_r)
    nq_1x_nav = nav_from_returns(nq_1x_r)
    nq_2x_nav = nav_from_returns(nq_2x_r)

    # 6. Simulazione full-period (1976 → 2025, ~50 anni)
    print("\n[simulazione full-period]")
    strat_full = simulate_pac(nq_1x_nav, nq_2x_nav, sp_1x_nav, sp_2x_nav,
                              tactical=True)
    bench_full = simulate_pac(nq_1x_nav, nq_2x_nav, sp_1x_nav, sp_2x_nav,
                              tactical=False)
    print(f"  Tattica  → final: ${strat_full.final_value:,.0f}  "
          f"(contrib ${strat_full.total_contributed:,.0f})")
    print(f"  Buy&Hold → final: ${bench_full.final_value:,.0f}  "
          f"(contrib ${bench_full.total_contributed:,.0f})")
    n_2x_ndx = sum(strat_full.in_2x_ndx)
    n_2x_sp = sum(strat_full.in_2x_sp)
    print(f"  Mesi in 2x NDX:    {n_2x_ndx}/{len(strat_full.monthly_dates)} "
          f"({100*n_2x_ndx/len(strat_full.monthly_dates):.1f}%)")
    print(f"  Mesi in 2x SP500:  {n_2x_sp}/{len(strat_full.monthly_dates)} "
          f"({100*n_2x_sp/len(strat_full.monthly_dates):.1f}%)")

    # 7. Rolling windows 15/20/25y
    print("\n[rolling windows]")
    windows_by_label = {}
    scorecards = {}
    for label, n_months in WINDOWS_MONTHS.items():
        print(f"  computing {label} (window={n_months}m, step={STEP_MONTHS}m)…")
        ws = rolling_metrics(
            nq_1x_nav, nq_2x_nav, sp_1x_nav, sp_2x_nav,
            window_months=n_months, step_months=STEP_MONTHS,
        )
        df = windows_to_df(ws)
        windows_by_label[label] = df
        sc = scorecard_6plus1(df)
        scorecards[label] = sc
        print(f"    n_windows={len(df)}, verdict={sc['verdict']} "
              f"({sc['passed']}/7)")

    # 8. Grafici
    print("\n[grafici]")
    plot_equity_full(strat_full, bench_full, OUT_DIR / "01_equity_curves.png")
    print(f"  → 01_equity_curves.png")
    plot_cagr_box(windows_by_label, OUT_DIR / "02_cagr_box.png")
    print(f"  → 02_cagr_box.png")
    plot_mdd_box(windows_by_label, OUT_DIR / "03_mdd_box.png")
    print(f"  → 03_mdd_box.png")
    plot_switch_timeline(strat_full, OUT_DIR / "04_switch_timeline.png")
    print(f"  → 04_switch_timeline.png")
    plot_scorecard(scorecards, OUT_DIR / "05_scorecard.png")
    print(f"  → 05_scorecard.png")
    plot_calibration(calib_sp, calib_nq, OUT_DIR / "06_calibration.png")
    print(f"  → 06_calibration.png")
    plot_percentile_fans(windows_by_label, OUT_DIR / "07_cagr_percentiles.png")
    print(f"  → 07_cagr_percentiles.png")
    plot_asymmetry(windows_by_label, OUT_DIR / "08_asymmetry.png")
    print(f"  → 08_asymmetry.png")

    # 9. Export data.csv per il componente interattivo React
    print("\n[export]")
    export_df = pd.DataFrame({
        "date": strat_full.portfolio_value.index,
        "strat": strat_full.portfolio_value.values,
        "bench": bench_full.portfolio_value.values,
    })
    # Aggiungo curve degli indici 1x e 2x (NAV normalizzati)
    export_df["sp_1x"] = sp_1x_nav.reindex(strat_full.portfolio_value.index).ffill().values
    export_df["sp_2x"] = sp_2x_nav.reindex(strat_full.portfolio_value.index).ffill().values
    export_df["nq_1x"] = nq_1x_nav.reindex(strat_full.portfolio_value.index).ffill().values
    export_df["nq_2x"] = nq_2x_nav.reindex(strat_full.portfolio_value.index).ffill().values
    # Contributi cumulati
    contrib_series = pd.Series(0.0, index=strat_full.portfolio_value.index)
    cum = 0.0
    md_set = set(strat_full.monthly_dates)
    for d in strat_full.portfolio_value.index:
        if d in md_set:
            cum += DCA_AMOUNT
        contrib_series.loc[d] = cum
    export_df["contributed"] = contrib_series.values
    # Riduco a 1 punto per settimana per limitare peso file (~2600 vs 12600)
    export_df_w = export_df.iloc[::5].copy()
    export_df_w.to_csv(OUT_DIR / "data.csv", index=False,
                       float_format="%.4f")
    print(f"  → data.csv ({len(export_df_w)} righe weekly-sampled)")

    # 10. Export switch history (per timeline interattiva)
    switch_df = pd.DataFrame({
        "date": strat_full.monthly_dates,
        "in_2x_ndx": strat_full.in_2x_ndx,
        "in_2x_sp": strat_full.in_2x_sp,
        "dd_ndx": strat_full.dd_ndx_at_contrib,
        "dd_sp": strat_full.dd_sp_at_contrib,
    })
    switch_df.to_csv(OUT_DIR / "switch_history.csv", index=False,
                     float_format="%.4f")
    print(f"  → switch_history.csv ({len(switch_df)} righe)")

    # 11. summary.json
    # Funzione helper per estrarre percentili di una colonna
    def pcts(series: pd.Series, qs=(0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)) -> dict:
        return {f"p{int(q*100):02d}": float(series.quantile(q)) for q in qs}

    summary = {
        "slug": SLUG,
        "generated_at": pd.Timestamp.now().isoformat(),
        "period": {
            "start": str(common[0].date()),
            "end": str(common[-1].date()),
            "trading_days": int(len(common)),
        },
        "strategy": {
            "dca_amount_usd": DCA_AMOUNT,
            "weights": {"nasdaq": W_NASDAQ, "sp500": W_SP500},
            "dd_threshold": DD_THRESHOLD,
            "switch_rule": "DD calcolato separatamente su NASDAQ e SP500; "
                           "switch indipendente di ciascuna quota; "
                           "solo nuove contribuzioni vanno in 2x.",
        },
        "calibration": {
            "sp500": calib_sp,
            "nasdaq": calib_nq,
            "drag_applied_per_year": {
                "sp500_1x": drag_1x,
                "sp500_2x": drag_sp_2x,
                "nasdaq_1x": drag_1x,
                "nasdaq_2x": drag_nq_2x,
            },
            "ter_ucits": {
                "sp500_2x": TER_UCITS_SP500_2X,
                "nasdaq_2x": TER_UCITS_NDX_2X,
            },
        },
        "full_period": {
            "total_contributed_usd": strat_full.total_contributed,
            "final_value_tactical_usd": strat_full.final_value,
            "final_value_buyhold_usd": bench_full.final_value,
            "tactical_vs_buyhold_pct":
                (strat_full.final_value / bench_full.final_value - 1)
                if bench_full.final_value else None,
            "months_in_2x_ndx": int(sum(strat_full.in_2x_ndx)),
            "months_in_2x_sp": int(sum(strat_full.in_2x_sp)),
            "months_total": int(len(strat_full.monthly_dates)),
        },
        "rolling": {},
    }
    for label, df in windows_by_label.items():
        # Rapporto strat / bench: misura il "premio" (>1) o lo "sconto"
        # (<1) della tattica vs buy&hold in ciascuna finestra
        ratio_final = df["final_strat"] / df["final_bench"]
        excess_cagr = df["cagr_strat"] - df["cagr_bench"]
        summary["rolling"][label] = {
            "n_windows": int(len(df)),
            "scorecard": scorecards[label],
            "cagr_strat": pcts(df["cagr_strat"]),
            "cagr_bench": pcts(df["cagr_bench"]),
            "cagr_excess_strat_minus_bench": pcts(excess_cagr),
            "mdd_strat": pcts(df["mdd_strat"]),
            "mdd_bench": pcts(df["mdd_bench"]),
            "vol_strat": pcts(df["vol_strat"]),
            "vol_bench": pcts(df["vol_bench"]),
            "final_strat": pcts(df["final_strat"]),
            "final_bench": pcts(df["final_bench"]),
            "ratio_strat_over_bench": pcts(ratio_final),
            "frac_2x_ndx_avg": float(df["frac_2x_ndx"].mean()),
            "frac_2x_sp_avg": float(df["frac_2x_sp"].mean()),
            "win_rate_final_value": float(
                (df["final_strat"] > df["final_bench"]).mean()
            ),
            "shortfall_p05_pct": float((ratio_final.quantile(0.05) - 1) * 100),
            "upside_p95_pct": float((ratio_final.quantile(0.95) - 1) * 100),
        }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  → summary.json")

    # 12. Anche rolling raw export per debug
    for label, df in windows_by_label.items():
        df.to_csv(OUT_DIR / f"rolling_{label}.csv", index=False,
                  float_format="%.5f")
    print(f"  → rolling_*.csv")

    # 13. Export dati per simulatore interattivo React
    #     Per ogni contribuzione mensile salva:
    #       - NAV 1x e 2x di entrambi gli indici (per simulare in-browser)
    #       - drawdown su 1x (per decidere se attivare la leva)
    #     Cosi' il componente puo' ricalcolare con qualsiasi soglia / cifra.
    print("\n[export simulatore]")
    md = pd.DatetimeIndex(strat_full.monthly_dates)
    ndx_peak_full = nq_1x_nav.cummax()
    sp_peak_full = sp_1x_nav.cummax()
    ndx_dd_full = nq_1x_nav / ndx_peak_full - 1.0
    sp_dd_full = sp_1x_nav / sp_peak_full - 1.0

    ndx1_m = nq_1x_nav.reindex(md).ffill()
    ndx2_m = nq_2x_nav.reindex(md).ffill()
    sp1_m = sp_1x_nav.reindex(md).ffill()
    sp2_m = sp_2x_nav.reindex(md).ffill()
    # NAV finali (al termine del dataset) per la valutazione finale
    last_d = strat_full.portfolio_value.index[-1]
    final_ndx1 = float(nq_1x_nav.loc[last_d])
    final_ndx2 = float(nq_2x_nav.loc[last_d])
    final_sp1 = float(sp_1x_nav.loc[last_d])
    final_sp2 = float(sp_2x_nav.loc[last_d])

    sim_data = {
        "meta": {
            "start": str(md[0].date()),
            "end": str(last_d.date()),
            "n_months": int(len(md)),
            "w_nasdaq": W_NASDAQ,
            "w_sp500": W_SP500,
            "drag_sp_2x_annual": drag_sp_2x,
            "drag_nq_2x_annual": drag_nq_2x,
            "default_dca_monthly": DCA_AMOUNT,
            "default_dd_threshold": DD_THRESHOLD,
        },
        "dates": [str(d.date()) for d in md],
        "ndx_1x": [round(float(v), 6) for v in ndx1_m.values],
        "ndx_2x": [round(float(v), 6) for v in ndx2_m.values],
        "sp_1x": [round(float(v), 6) for v in sp1_m.values],
        "sp_2x": [round(float(v), 6) for v in sp2_m.values],
        "ndx_dd": [round(float(v), 4) for v in ndx_dd_full.reindex(md).ffill().values],
        "sp_dd": [round(float(v), 4) for v in sp_dd_full.reindex(md).ffill().values],
        "final": {
            "date": str(last_d.date()),
            "ndx_1x": round(final_ndx1, 6),
            "ndx_2x": round(final_ndx2, 6),
            "sp_1x": round(final_sp1, 6),
            "sp_2x": round(final_sp2, 6),
        },
    }
    with open(OUT_DIR / "sim_data.json", "w", encoding="utf-8") as f:
        json.dump(sim_data, f, separators=(",", ":"))
    print(f"  → sim_data.json ({len(md)} mesi)")

    print("\nDONE.")
    print(f"Output in {OUT_DIR}\n")


if __name__ == "__main__":
    main()

