"""
SmartMoneyLab — Lump sum finanziato (prestito) vs PAC tradizionale
====================================================================

Articolo della serie "Battere il mercato?".

Domanda fondamentale:
  Se ho un flusso di cassa periodico di $250/mese, conviene di piu'
  trasformarlo nella rata di un prestito a tasso fisso e investire
  subito il capitale ottenuto in lump sum, o conviene continuare con
  un PAC classico versando $250 al mese?

Strategia testata ("LUMP SUM finanziato"):
  - Cash flow disponibile: $250/mese
  - Prestito personale a tasso fisso TAEG X%, durata 120 mesi.
    Capitale derivato dalla formula del prestito:
        C = M * (1 - (1+r)^-n) / r,   r = TAEG/12, n = 120
  - A t=0 il capitale C viene investito INTEGRALMENTE sull'indice 1x.
  - Le rate da $250/mese vengono pagate con il cash flow personale
    (= non si tocca l'investimento). L'investimento cresce con il
    mercato senza prelievi.

  Modalita' 10y (1 prestito): si fotografa la situazione a t=120m.
  Modalita' 20y (2 prestiti consecutivi): a t=120m il primo prestito
    e' estinto, se ne accende un secondo identico → un nuovo capitale C
    viene investito (sommato all'investimento esistente), rate per
    altri 120 mesi. Foto a t=240m.

Benchmark ("PAC"):
  - Stesso flusso $250/mese investiti puntualmente all'inizio di ogni
    mese sull'indice 1x. Niente prestito, niente lump sum.
  - Modalita' 10y: 120 versamenti, foto a t=120m.
  - Modalita' 20y: 240 versamenti, foto a t=240m.

Scenari TAEG:
  - Ottimistico:  6.00% (capitale derivato ~$22.518)
  - Realistico:   8.00% (capitale derivato ~$20.605)

Asset (1976-2025):
  - SP500 daily Total Return (ricostruito via dividendi Shiller)
  - NASDAQ Composite daily price-only (no TR disponibile per il periodo)

Rolling windows: 10y (120m) e 20y (240m). Step: 3 mesi.

Framework 6+1 (come gli altri articoli della serie):
  1. CAGR mediano (lump) >= benchmark (pac)
  2. Win rate (% finestre con CAGR_lump > CAGR_pac) >= 60%
  3. Volatilita' annualizzata <= benchmark * 1.10
  4. Max Drawdown mediano peggiore <= benchmark * 1.10 (tolleranza 10%)
  5. Sharpe ratio >= benchmark
  6. Calmar ratio (CAGR / |MDD|) >= benchmark
  7. Sortino ratio >= benchmark

Verdict: VINCE 7/7, PARZIALE 4-6/7, NON VINCE <=3/7.

Output:
  public/charts/prestito-vs-pac/
    01_equity_example.png   — equity curve di una finestra rappresentativa
    02_cagr_box.png         — distribuzione CAGR rolling per scenario
    03_winrate_bar.png      — win rate LUMP vs PAC per scenario
    04_excess_distribution.png — distribuzione excess CAGR / payoff
    05_scorecard.png        — scorecard verdict 6+1
    06_taeg_breakeven.png   — curva di break-even TAEG
    summary.json            — tutti i numeri strutturati
    rolling_*.csv           — finestre rolling per debug
    sim_data.json           — dati monthly per il simulatore React

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
SLUG = "prestito-vs-pac"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo dell'analisi
START_DATE = "1976-01-01"
END_DATE = "2025-12-31"

# Strategia
MONTHLY_PAYMENT = 250.0       # cash flow disponibile / rata fissa USD
LOAN_DURATION_M = 120         # durata del singolo prestito (mesi)

# Scenari TAEG da testare nell'articolo
TAEG_SCENARIOS = {
    "ottimistico_6":  0.06,
    "realistico_8":   0.08,
}

# Griglia di TAEG per la curva di break-even (grafico 06)
TAEG_GRID = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14]

# Indici testati separatamente
INDICES = ("nasdaq", "sp500")

# Rolling windows: 10y (un prestito) e 20y (due prestiti consecutivi)
WINDOWS_MONTHS = {"10y": 120, "20y": 240}
STEP_MONTHS = 3

# Risk-free per Sharpe / Sortino (coerente con resto della serie)
RISK_FREE_ANNUAL = 0.02

# Palette articolo (coerente con resto del blog)
COLOR_LUMP = "#d97706"   # ambra — lump sum finanziato
COLOR_PAC = "#1e3a8a"    # navy  — PAC tradizionale
COLOR_NDX = "#3b82f6"
COLOR_SP = "#0f172a"
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
# Loader dati (identici al resto della serie)                          #
# -------------------------------------------------------------------- #

def _download(url: str, cache_name: str, retries: int = 3) -> bytes:
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        return cache_path.read_bytes()
    headers = {"User-Agent": _BROWSER_UA}
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            cache_path.write_bytes(r.content)
            return r.content
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"Fallito download {url}: {last_err}")


def load_sp500_daily_price() -> pd.Series:
    """Daily close S&P 500 dal cache file gia' esistente.
    Formato: Date,Close (header standard del Yahoo CSV gia' usato dagli
    altri script della serie)."""
    csv_path = CACHE_DIR / "yahoo_gspc_daily.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Manca {csv_path}. Lancia prima uno script della serie che "
            "scarica/popola il cache (es. pac-leva-tattica.py)."
        )
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date").set_index("Date")
    s = pd.to_numeric(df["Close"], errors="coerce").dropna()
    s.name = "sp500_close"
    print(f"[loaded] SP500 daily: {len(s)} righe, "
          f"{s.index[0].date()} -> {s.index[-1].date()}")
    return s


def load_nasdaq_daily_price() -> pd.Series:
    """Daily close NASDAQ Composite dal cache file.
    Tolerant ai due formati FRED che girano (observation_date / DATE)."""
    csv_path = CACHE_DIR / "NASDAQCOM.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Manca {csv_path}")
    df = pd.read_csv(csv_path)
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
    """Shiller monthly: prezzo e dividendi SP500 (per ricostruire TR).
    Pattern identico a pac-leva-tattica.py: detection robusta di colonne
    'Date', 'SP500', 'Dividend'."""
    raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
    m = pd.read_csv(io.StringIO(raw))
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
    m = m.set_index("date").sort_index()
    p = pd.to_numeric(m["SP500"], errors="coerce")
    d = pd.to_numeric(m["Dividend"], errors="coerce")
    return pd.DataFrame({"P": p, "D": d}).dropna()


def build_sp500_tr_daily(price: pd.Series, shiller: pd.DataFrame) -> pd.Series:
    """SP500 Total Return daily returns. Per ogni giorno t nel mese m,
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
    """NASDAQ Composite price-only daily returns. Yield storico ~1% non
    incluso (no TR disponibile per 1976-1999); il confronto LUMP/PAC e'
    invariante perche' entrambi usano la stessa serie."""
    r = price.pct_change().dropna()
    r.name = "nasdaq_daily"
    return r


def nav_from_returns(returns: pd.Series) -> pd.Series:
    """NAV cumulato, NAV(0)=1."""
    nav = (1.0 + returns).cumprod()
    return nav.clip(lower=1e-12)


# -------------------------------------------------------------------- #
# Matematica del prestito                                              #
# -------------------------------------------------------------------- #

def loan_capital_from_payment(monthly_payment: float, taeg_annual: float,
                              n_months: int) -> float:
    """Capitale di un prestito amortizing dato pagamento mensile, TAEG
    e durata. Formula: C = M * (1 - (1+r)^-n) / r, r = TAEG/12."""
    r = taeg_annual / 12.0
    if r == 0:
        return monthly_payment * n_months
    return monthly_payment * (1 - (1 + r) ** (-n_months)) / r


def loan_payment_from_capital(capital: float, taeg_annual: float,
                              n_months: int) -> float:
    """Rata mensile di un prestito amortizing dato capitale, TAEG, durata.
    Formula: M = C * r * (1+r)^n / ((1+r)^n - 1)."""
    r = taeg_annual / 12.0
    if r == 0:
        return capital / n_months
    return capital * r * (1 + r) ** n_months / ((1 + r) ** n_months - 1)


# -------------------------------------------------------------------- #
# Simulazione                                                          #
# -------------------------------------------------------------------- #

@dataclass
class SimResult:
    dates: pd.DatetimeIndex
    portfolio_value: pd.Series
    monthly_dates: list                # date di flusso (rate o versamenti PAC)
    total_contributed: float           # quanto e' uscito dal cash flow
    invested_principal: float          # quanto e' entrato sull'indice
    final_value: float


def _monthly_contribution_dates(idx: pd.DatetimeIndex) -> list:
    """Prima data di trading di ogni mese nella finestra."""
    df = pd.DataFrame({"d": idx}, index=idx)
    df["ym"] = df["d"].dt.to_period("M")
    first = df.groupby("ym").first()["d"].sort_values().tolist()
    return first


def simulate_lump_loan(
    nav: pd.Series, *,
    capital: float, monthly_payment: float, n_months_total: int,
    second_loan: bool = False, start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> SimResult:
    """Lump sum finanziato: a t=0 investe capital sull'indice 1x.
    Le rate vengono pagate con cash flow personale, NON con prelievi
    dall'investimento (quindi l'investimento cresce indisturbato).

    Se second_loan=True, a t=120m (n_months_total=240) prende un secondo
    prestito identico e investe altro capital.

    monthly_payment e' usato solo per contabilita': total_contributed
    rappresenta le rate effettivamente uscite dal cash flow.
    """
    all_idx = nav.index
    if start is not None:
        all_idx = all_idx[all_idx >= start]
    if end is not None:
        all_idx = all_idx[all_idx <= end]
    if len(all_idx) < 252:
        raise ValueError("Finestra troppo corta.")

    n = nav.reindex(all_idx).ffill()
    monthly_dates = _monthly_contribution_dates(all_idx)
    if len(monthly_dates) < n_months_total:
        raise ValueError("Mesi insufficienti nella finestra.")
    monthly_dates = monthly_dates[:n_months_total]

    # Quote acquistate: capital / NAV alla data di erogazione
    nav_t0 = float(n.loc[monthly_dates[0]])
    units = capital / nav_t0
    invested = capital

    if second_loan and n_months_total >= 240:
        # Secondo prestito a t=120m: indice 121 (1-based) → 120 (0-based)
        d2 = monthly_dates[120]
        nav_t2 = float(n.loc[d2])
        units += capital / nav_t2
        invested += capital

    # Valore portafoglio daily
    pv = units * n
    # Per il secondo prestito devo "iniziare a contare" units totali
    # solo dopo d2. Quindi calcolo a strati:
    if second_loan and n_months_total >= 240:
        units1 = capital / nav_t0
        units2 = capital / float(n.loc[monthly_dates[120]])
        pv = units1 * n.copy()
        mask_after = pv.index >= monthly_dates[120]
        pv.loc[mask_after] = pv.loc[mask_after] + units2 * n.loc[mask_after]
    else:
        pv = (capital / nav_t0) * n

    pv.name = "lump_pv"
    final_value = float(pv.loc[monthly_dates[-1]])

    return SimResult(
        dates=all_idx,
        portfolio_value=pv,
        monthly_dates=monthly_dates,
        total_contributed=monthly_payment * n_months_total,
        invested_principal=invested,
        final_value=final_value,
    )


def simulate_pac(
    nav: pd.Series, *,
    monthly_amount: float, n_months_total: int,
    start: pd.Timestamp | None = None, end: pd.Timestamp | None = None,
) -> SimResult:
    """PAC classico: monthly_amount versato a inizio di ogni mese,
    n_months_total versamenti totali."""
    all_idx = nav.index
    if start is not None:
        all_idx = all_idx[all_idx >= start]
    if end is not None:
        all_idx = all_idx[all_idx <= end]
    if len(all_idx) < 252:
        raise ValueError("Finestra troppo corta.")

    n = nav.reindex(all_idx).ffill()
    monthly_dates = _monthly_contribution_dates(all_idx)
    if len(monthly_dates) < n_months_total:
        raise ValueError("Mesi insufficienti.")
    monthly_dates = monthly_dates[:n_months_total]

    # Accumulo unita' tramite versamenti progressivi
    units = 0.0
    pv = pd.Series(0.0, index=all_idx)
    contributed = 0.0
    # Ordino le date di contribuzione e calcolo il pv sezione per
    # sezione (tra una contribuzione e la successiva, units e' costante).
    md_set = set(monthly_dates)
    for d in all_idx:
        if d in md_set:
            units += monthly_amount / float(n.loc[d])
            contributed += monthly_amount
        pv.loc[d] = units * float(n.loc[d])

    pv.name = "pac_pv"
    final_value = float(pv.loc[monthly_dates[-1]])

    return SimResult(
        dates=all_idx,
        portfolio_value=pv,
        monthly_dates=monthly_dates,
        total_contributed=contributed,
        invested_principal=contributed,
        final_value=final_value,
    )


# -------------------------------------------------------------------- #
# Metriche                                                             #
# -------------------------------------------------------------------- #

def _cashflows_lump(capital: float, monthly_payment: float,
                    n_months_total: int, second_loan: bool) -> tuple:
    """Costruisce flussi di cassa per IRR. Positivo = entrata, negativo
    = uscita. Il LUMP riceve capital all'origine (entrata virtuale,
    serve a confrontare apples-to-apples col PAC), paga rate ogni
    mese, riceve capital di nuovo a t=120m se second_loan.

    Per simmetria col PAC e' meglio modellare TUTTI gli scenari sul
    flusso di cassa "personale": al netto del prestito, dal tuo
    portafoglio escono monthly_payment ogni mese per n_months_total.
    Quindi: cashflows = [-monthly_payment per ogni mese] + [final_value].

    Questo CAGR e' confrontabile direttamente col CAGR del PAC.
    """
    cfs = [-monthly_payment] * n_months_total
    return cfs


def irr_cagr(cashflows: list, final_value: float, n_years: float) -> float:
    """IRR annualizzato per una serie di cashflows mensili (negativi)
    seguiti da un valore finale (positivo). Restituisce il tasso annuo
    che azzera l'NPV."""
    if final_value <= 0:
        return float("nan")
    n_months = len(cashflows)
    cf = np.array(cashflows + [final_value], dtype=float)
    t = np.append(np.arange(n_months) / 12.0, n_years)

    def npv(r):
        return float(np.sum(cf / (1 + r) ** t))

    lo, hi = -0.99, 5.0
    if npv(lo) * npv(hi) > 0:
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
    cagr_lump: float
    cagr_pac: float
    mdd_lump: float
    mdd_pac: float
    vol_lump: float
    vol_pac: float
    dvol_lump: float
    dvol_pac: float
    final_lump: float
    final_pac: float
    contributed: float
    invested_lump: float


def rolling_metrics(
    nav: pd.Series, *,
    capital: float, monthly_payment: float,
    n_months_total: int, second_loan: bool,
    step_months: int,
) -> list[WindowMetrics]:
    """Per ogni finestra rolling, esegue LUMP e PAC e raccoglie tutte
    le metriche."""
    all_idx = nav.index
    monthly_starts = pd.Series(all_idx).groupby(
        all_idx.to_period("M")
    ).min().values
    monthly_starts = pd.DatetimeIndex(monthly_starts).sort_values()
    n_months_data = len(monthly_starts)

    out = []
    i = 0
    while i + n_months_total <= n_months_data:
        s_date = monthly_starts[i]
        # End: ultimo giorno di trading del mese che chiude la finestra
        if i + n_months_total < n_months_data:
            e_date = monthly_starts[i + n_months_total] - pd.Timedelta(days=1)
        else:
            e_date = all_idx[-1]

        try:
            lump = simulate_lump_loan(
                nav, capital=capital, monthly_payment=monthly_payment,
                n_months_total=n_months_total, second_loan=second_loan,
                start=s_date, end=e_date,
            )
            pac = simulate_pac(
                nav, monthly_amount=monthly_payment,
                n_months_total=n_months_total,
                start=s_date, end=e_date,
            )
        except ValueError:
            i += step_months
            continue

        n_years = n_months_total / 12.0
        cfs_lump = _cashflows_lump(capital, monthly_payment,
                                   n_months_total, second_loan)
        # Per il PAC, i cashflows sono identici (monthly_payment uscente
        # ogni mese), il valore finale e' diverso.
        cfs_pac = [-monthly_payment] * n_months_total

        cagr_l = irr_cagr(cfs_lump, lump.final_value, n_years)
        cagr_p = irr_cagr(cfs_pac, pac.final_value, n_years)

        ret_l = daily_returns_from_pv(lump.portfolio_value)
        ret_p = daily_returns_from_pv(pac.portfolio_value)

        out.append(WindowMetrics(
            start=s_date, end=e_date,
            cagr_lump=cagr_l, cagr_pac=cagr_p,
            mdd_lump=max_drawdown(lump.portfolio_value),
            mdd_pac=max_drawdown(pac.portfolio_value),
            vol_lump=annualized_vol(ret_l),
            vol_pac=annualized_vol(ret_p),
            dvol_lump=downside_vol(ret_l),
            dvol_pac=downside_vol(ret_p),
            final_lump=lump.final_value,
            final_pac=pac.final_value,
            contributed=monthly_payment * n_months_total,
            invested_lump=lump.invested_principal,
        ))
        i += step_months
    return out


def windows_to_df(ws: list[WindowMetrics]) -> pd.DataFrame:
    return pd.DataFrame([{
        "start": w.start, "end": w.end,
        "cagr_lump": w.cagr_lump, "cagr_pac": w.cagr_pac,
        "mdd_lump": w.mdd_lump, "mdd_pac": w.mdd_pac,
        "vol_lump": w.vol_lump, "vol_pac": w.vol_pac,
        "dvol_lump": w.dvol_lump, "dvol_pac": w.dvol_pac,
        "final_lump": w.final_lump, "final_pac": w.final_pac,
        "contributed": w.contributed,
        "invested_lump": w.invested_lump,
    } for w in ws])


# -------------------------------------------------------------------- #
# Framework 6+1 scorecard                                              #
# -------------------------------------------------------------------- #

def scorecard_6plus1(df: pd.DataFrame) -> dict:
    cagr_l_med = float(df["cagr_lump"].median())
    cagr_p_med = float(df["cagr_pac"].median())
    win_rate = float((df["cagr_lump"] > df["cagr_pac"]).mean())
    vol_l_med = float(df["vol_lump"].median())
    vol_p_med = float(df["vol_pac"].median())
    mdd_l_med = float(df["mdd_lump"].median())
    mdd_p_med = float(df["mdd_pac"].median())
    dvol_l_med = float(df["dvol_lump"].median())
    dvol_p_med = float(df["dvol_pac"].median())

    sharpe_l = sharpe(cagr_l_med, vol_l_med)
    sharpe_p = sharpe(cagr_p_med, vol_p_med)
    calmar_l = calmar(cagr_l_med, mdd_l_med)
    calmar_p = calmar(cagr_p_med, mdd_p_med)
    sortino_l = sortino(cagr_l_med, dvol_l_med)
    sortino_p = sortino(cagr_p_med, dvol_p_med)

    checks = {
        "cagr": cagr_l_med >= cagr_p_med,
        "win_rate": win_rate >= 0.60,
        "vol": vol_l_med <= vol_p_med * 1.10,
        "mdd": abs(mdd_l_med) <= abs(mdd_p_med) * 1.10,
        "sharpe": sharpe_l >= sharpe_p,
        "calmar": calmar_l >= calmar_p,
        "sortino": sortino_l >= sortino_p,
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
            "cagr_lump_med": cagr_l_med, "cagr_pac_med": cagr_p_med,
            "win_rate": win_rate,
            "vol_lump_med": vol_l_med, "vol_pac_med": vol_p_med,
            "mdd_lump_med": mdd_l_med, "mdd_pac_med": mdd_p_med,
            "sharpe_lump": sharpe_l, "sharpe_pac": sharpe_p,
            "calmar_lump": calmar_l, "calmar_pac": calmar_p,
            "sortino_lump": sortino_l, "sortino_pac": sortino_p,
        },
        "checks": {k: bool(v) for k, v in checks.items()},
        "passed": int(passed),
        "verdict": verdict,
    }


# -------------------------------------------------------------------- #
# Grafici                                                              #
# -------------------------------------------------------------------- #

def _style(ax, title: str, ylabel: str = "", xlabel: str = ""):
    ax.set_title(title, fontsize=13, fontweight="semibold",
                 color="#0f172a", pad=12)
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


def plot_equity_example(lump_sims: dict, pac_sims: dict, fname: Path):
    """Esempio rappresentativo: una finestra 20y (es. 2000-2020) per
    NASDAQ con TAEG 8%. Mostra equity curve LUMP vs PAC + rate
    cumulate."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), dpi=160, sharex=False)
    titles = [
        ("nasdaq", "ottimistico_6", "NASDAQ — TAEG 6% (ottimistico)"),
        ("nasdaq", "realistico_8",  "NASDAQ — TAEG 8% (realistico)"),
        ("sp500",  "ottimistico_6", "SP500 — TAEG 6% (ottimistico)"),
        ("sp500",  "realistico_8",  "SP500 — TAEG 8% (realistico)"),
    ]
    for ax, (idx, taeg_key, title) in zip(axes.flat, titles):
        lump = lump_sims[(idx, taeg_key)]
        pac = pac_sims[(idx, taeg_key)]
        ax.plot(lump.portfolio_value.index, lump.portfolio_value.values,
                color=COLOR_LUMP, linewidth=1.6, label="Lump sum finanziato")
        ax.plot(pac.portfolio_value.index, pac.portfolio_value.values,
                color=COLOR_PAC, linewidth=1.6, label="PAC")
        # Linea rate cumulate (= contributi PAC cumulati: stessi cash flow)
        cum = pd.Series(
            [MONTHLY_PAYMENT * (i + 1) for i in range(len(pac.monthly_dates))],
            index=pac.monthly_dates,
        )
        ax.plot(cum.index, cum.values,
                color=COLOR_GREY, linewidth=0.9, linestyle="--",
                label="Cash flow uscito")
        _style(ax, title, ylabel="Valore portafoglio (USD)")
        ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.suptitle(
        "Esempio: finestra 20Y rappresentativa (2 prestiti consecutivi)",
        fontsize=14, fontweight="semibold", color="#0f172a", y=1.00,
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_cagr_box(scenarios: dict, fname: Path):
    """Box plot CAGR LUMP e PAC per ogni scenario (2 indici × 2 TAEG ×
    2 finestre = 8 scenari). Pannelli per finestra (10y, 20y)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=160)
    for ax, win_label in zip(axes, WINDOWS_MONTHS.keys()):
        data, labels, colors = [], [], []
        for idx in INDICES:
            for taeg_key in TAEG_SCENARIOS:
                df = scenarios[(idx, taeg_key, win_label)]["df"]
                data.append(df["cagr_lump"].dropna() * 100)
                data.append(df["cagr_pac"].dropna() * 100)
                short_taeg = taeg_key.split("_")[1]
                labels.append(f"{idx.upper()}\nT{short_taeg}\nLUMP")
                labels.append(f"{idx.upper()}\nT{short_taeg}\nPAC")
                colors.append(COLOR_LUMP)
                colors.append(COLOR_PAC)
        bp = ax.boxplot(data, patch_artist=True, widths=0.6,
                        showfliers=False)
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.55)
            patch.set_edgecolor(c)
        for med in bp["medians"]:
            med.set_color("#0f172a")
            med.set_linewidth(1.4)
        ax.set_xticklabels(labels, fontsize=8.5)
        ax.axhline(0, color="#94a3b8", linewidth=0.7, linestyle="--")
        _style(ax, f"Distribuzione CAGR — finestre {win_label}",
               ylabel="CAGR (%)")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_winrate_bar(scenarios: dict, fname: Path):
    """Win rate del LUMP vs PAC per ciascuno degli 8 scenari."""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=160)
    labels, values, colors = [], [], []
    for win_label in WINDOWS_MONTHS:
        for idx in INDICES:
            for taeg_key in TAEG_SCENARIOS:
                sc = scenarios[(idx, taeg_key, win_label)]["scorecard"]
                wr = sc["metrics"]["win_rate"] * 100
                short_taeg = taeg_key.split("_")[1]
                labels.append(f"{idx.upper()} T{short_taeg} {win_label}")
                values.append(wr)
                colors.append(COLOR_LUMP if wr >= 50 else COLOR_PAC)
    bars = ax.barh(labels, values, color=colors, alpha=0.85,
                   edgecolor=[c for c in colors])
    ax.axvline(50, color="#475569", linewidth=0.9, linestyle="--",
               label="Soglia 50% (parità)")
    ax.axvline(60, color="#15803d", linewidth=0.9, linestyle=":",
               label="Soglia framework 60%")
    for bar, v in zip(bars, values):
        ax.text(v + 0.7, bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}%", va="center", fontsize=10, color="#0f172a")
    _style(ax, "Win rate del LUMP SUM finanziato vs PAC, per scenario",
           xlabel="Win rate (% finestre in cui LUMP > PAC)")
    ax.set_xlim(0, 100)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_excess_distribution(scenarios: dict, fname: Path):
    """Excess CAGR (LUMP − PAC) per scenario."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=160)
    for ax, win_label in zip(axes, WINDOWS_MONTHS.keys()):
        data, labels, colors = [], [], []
        for idx in INDICES:
            for taeg_key in TAEG_SCENARIOS:
                df = scenarios[(idx, taeg_key, win_label)]["df"]
                excess = (df["cagr_lump"] - df["cagr_pac"]).dropna() * 100
                data.append(excess)
                short_taeg = taeg_key.split("_")[1]
                labels.append(f"{idx.upper()}\nTAEG {short_taeg}%")
                # Colore in base al p50: se >0 ambra, se <0 navy
                colors.append(COLOR_LUMP if excess.median() > 0 else COLOR_PAC)
        bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                        showfliers=False)
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.55)
            patch.set_edgecolor(c)
        for med in bp["medians"]:
            med.set_color("#0f172a")
            med.set_linewidth(1.4)
        ax.set_xticklabels(labels, fontsize=9)
        ax.axhline(0, color="#475569", linewidth=0.9, linestyle="--",
                   label="Parità (LUMP = PAC)")
        _style(ax,
               f"Excess CAGR (LUMP − PAC) — finestre {win_label}",
               ylabel="Excess CAGR (pp/anno)")
        ax.legend(frameon=False, fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_scorecard(scenarios: dict, fname: Path):
    """Tabella scorecard 6+1 per ciascun scenario."""
    cells, rowlabels = [], []
    for win_label in WINDOWS_MONTHS:
        for idx in INDICES:
            for taeg_key in TAEG_SCENARIOS:
                sc = scenarios[(idx, taeg_key, win_label)]["scorecard"]
                checks = sc["checks"]
                short_taeg = taeg_key.split("_")[1]
                rowlabels.append(
                    f"{idx.upper()} | TAEG {short_taeg}% | {win_label}"
                )
                row = []
                for k in ("cagr", "win_rate", "vol", "mdd",
                          "sharpe", "calmar", "sortino"):
                    row.append("✓" if checks[k] else "✗")
                row.append(f"{sc['passed']}/7 — {sc['verdict']}")
                cells.append(row)
    headers = ["CAGR", "Win", "Vol", "MDD",
               "Sharpe", "Calmar", "Sortino", "Verdetto"]

    fig, ax = plt.subplots(figsize=(13, 0.4 * len(cells) + 1.5), dpi=160)
    ax.axis("off")
    tbl = ax.table(cellText=cells, rowLabels=rowlabels, colLabels=headers,
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 1.4)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        if r == 0:
            cell.set_facecolor("#1e3a8a")
            cell.set_text_props(color="white", weight="bold")
        elif c < 7 and r > 0:
            txt = cells[r-1][c]
            if txt == "✓":
                cell.set_facecolor("#dcfce7")
            elif txt == "✗":
                cell.set_facecolor("#fee2e2")
        elif c == 7 and r > 0:
            verdetto = cells[r-1][c]
            if "VINCE" in verdetto and "NON" not in verdetto:
                cell.set_facecolor("#22c55e")
                cell.set_text_props(weight="bold", color="white")
            elif "PARZIALE" in verdetto:
                cell.set_facecolor("#fbbf24")
                cell.set_text_props(weight="bold")
            else:
                cell.set_facecolor("#ef4444")
                cell.set_text_props(weight="bold", color="white")
    fig.suptitle("Scorecard 6+1: LUMP SUM finanziato vs PAC",
                 fontsize=14, fontweight="semibold", y=1.0)
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_taeg_breakeven(breakeven_data: dict, fname: Path):
    """Curva di break-even: win rate LUMP vs PAC al variare del TAEG,
    per ciascun indice × finestra."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=160)
    for ax, win_label in zip(axes, WINDOWS_MONTHS.keys()):
        for idx, marker, color in [
            ("nasdaq", "o", COLOR_NDX),
            ("sp500", "s", COLOR_SP),
        ]:
            taegs = []
            winrates = []
            for taeg in TAEG_GRID:
                key = (idx, round(taeg, 4), win_label)
                if key in breakeven_data:
                    taegs.append(taeg * 100)
                    winrates.append(breakeven_data[key] * 100)
            ax.plot(taegs, winrates, marker=marker, color=color,
                    linewidth=2.0, markersize=7, label=idx.upper())
        ax.axhline(50, color="#94a3b8", linewidth=0.8, linestyle="--",
                   label="50% (parità)")
        ax.axhline(60, color="#15803d", linewidth=0.8, linestyle=":",
                   label="60% (framework)")
        _style(ax,
               f"Win rate LUMP vs PAC al variare del TAEG — {win_label}",
               xlabel="TAEG (%)",
               ylabel="Win rate LUMP (%)")
        ax.set_ylim(0, 105)
        ax.legend(frameon=False, fontsize=9, loc="lower left")
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def pcts(series: pd.Series,
         qs=(0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)) -> dict:
    return {f"p{int(q*100):02d}": float(series.quantile(q)) for q in qs}


def main() -> None:
    print("=" * 68)
    print(f"  {SLUG}")
    print("=" * 68)

    # 1. Carico prezzi
    sp_price = load_sp500_daily_price()
    nq_price = load_nasdaq_daily_price()
    shiller = load_shiller_monthly()

    sp_price = sp_price.loc[START_DATE:END_DATE]
    nq_price = nq_price.loc[START_DATE:END_DATE]

    # 2. Costruisco NAV per i due indici (returns daily → NAV cumulato)
    sp_ret = build_sp500_tr_daily(sp_price, shiller)
    nq_ret = build_nasdaq_daily_returns(nq_price)
    sp_nav = nav_from_returns(sp_ret)
    nq_nav = nav_from_returns(nq_ret)
    common = sp_nav.index.intersection(nq_nav.index)
    sp_nav = sp_nav.reindex(common).ffill()
    nq_nav = nq_nav.reindex(common).ffill()
    print(f"\nPeriodo: {common[0].date()} → {common[-1].date()} "
          f"({len(common)} giorni di trading)")

    navs = {"nasdaq": nq_nav, "sp500": sp_nav}

    # 3. Calcolo capitali derivati per ogni TAEG
    capitals = {
        k: loan_capital_from_payment(MONTHLY_PAYMENT, t, LOAN_DURATION_M)
        for k, t in TAEG_SCENARIOS.items()
    }
    print(f"\n[Capitali derivati per rata {MONTHLY_PAYMENT}$/mese, "
          f"{LOAN_DURATION_M}m]")
    for k, c in capitals.items():
        print(f"  {k:>18}: TAEG {TAEG_SCENARIOS[k]*100:.1f}% → "
              f"capitale ${c:,.2f}")

    # 4. Rolling per ogni scenario (indice × TAEG × finestra)
    print("\n[rolling windows]")
    scenarios = {}
    for idx in INDICES:
        for taeg_key, taeg in TAEG_SCENARIOS.items():
            C = capitals[taeg_key]
            for win_label, n_m in WINDOWS_MONTHS.items():
                second_loan = (win_label == "20y")
                print(f"  {idx:>6} | TAEG {taeg*100:.1f}% | {win_label}"
                      f" (second_loan={second_loan})... ", end="")
                ws = rolling_metrics(
                    navs[idx], capital=C, monthly_payment=MONTHLY_PAYMENT,
                    n_months_total=n_m, second_loan=second_loan,
                    step_months=STEP_MONTHS,
                )
                df = windows_to_df(ws)
                sc = scorecard_6plus1(df)
                scenarios[(idx, taeg_key, win_label)] = {
                    "df": df, "scorecard": sc,
                }
                print(f"n_w={len(df)}, win_rate="
                      f"{sc['metrics']['win_rate']*100:.1f}%, "
                      f"{sc['verdict']} ({sc['passed']}/7)")

    # 5. Curva di break-even sui TAEG (griglia)
    print("\n[break-even TAEG]")
    breakeven_data = {}
    for idx in INDICES:
        for taeg in TAEG_GRID:
            C = loan_capital_from_payment(MONTHLY_PAYMENT, taeg,
                                          LOAN_DURATION_M)
            for win_label, n_m in WINDOWS_MONTHS.items():
                second_loan = (win_label == "20y")
                ws = rolling_metrics(
                    navs[idx], capital=C, monthly_payment=MONTHLY_PAYMENT,
                    n_months_total=n_m, second_loan=second_loan,
                    step_months=STEP_MONTHS,
                )
                df = windows_to_df(ws)
                wr = float((df["cagr_lump"] > df["cagr_pac"]).mean())
                breakeven_data[(idx, round(taeg, 4), win_label)] = wr
                print(f"  {idx:>6} | TAEG {taeg*100:>5.2f}% | {win_label} "
                      f"→ win rate {wr*100:.1f}%")

    # 6. Esempio di equity curve: una finestra 20y rappresentativa
    #    Scelgo 2000-2020 perché attraversa dotcom e GFC.
    print("\n[equity example]")
    example_start = pd.Timestamp("2000-01-01")
    example_end = pd.Timestamp("2020-12-31")
    lump_sims = {}
    pac_sims = {}
    for idx in INDICES:
        for taeg_key, taeg in TAEG_SCENARIOS.items():
            C = capitals[taeg_key]
            try:
                lump = simulate_lump_loan(
                    navs[idx], capital=C, monthly_payment=MONTHLY_PAYMENT,
                    n_months_total=240, second_loan=True,
                    start=example_start, end=example_end,
                )
                pac = simulate_pac(
                    navs[idx], monthly_amount=MONTHLY_PAYMENT,
                    n_months_total=240,
                    start=example_start, end=example_end,
                )
                lump_sims[(idx, taeg_key)] = lump
                pac_sims[(idx, taeg_key)] = pac
                print(f"  {idx} {taeg_key}: LUMP ${lump.final_value:,.0f}, "
                      f"PAC ${pac.final_value:,.0f}")
            except Exception as e:
                print(f"  WARN {idx} {taeg_key}: {e}")

    # 7. Grafici
    print("\n[grafici]")
    if lump_sims and pac_sims:
        plot_equity_example(lump_sims, pac_sims,
                            OUT_DIR / "01_equity_example.png")
        print("  → 01_equity_example.png")
    plot_cagr_box(scenarios, OUT_DIR / "02_cagr_box.png")
    print("  → 02_cagr_box.png")
    plot_winrate_bar(scenarios, OUT_DIR / "03_winrate_bar.png")
    print("  → 03_winrate_bar.png")
    plot_excess_distribution(scenarios, OUT_DIR / "04_excess_distribution.png")
    print("  → 04_excess_distribution.png")
    plot_scorecard(scenarios, OUT_DIR / "05_scorecard.png")
    print("  → 05_scorecard.png")
    plot_taeg_breakeven(breakeven_data, OUT_DIR / "06_taeg_breakeven.png")
    print("  → 06_taeg_breakeven.png")

    # 8. Rolling CSVs per debug
    print("\n[csv rolling]")
    for (idx, taeg_key, win_label), bundle in scenarios.items():
        bundle["df"].to_csv(
            OUT_DIR / f"rolling_{idx}_{taeg_key}_{win_label}.csv",
            index=False, float_format="%.5f",
        )
    print(f"  → rolling_*.csv ({len(scenarios)} file)")

    # 9. summary.json
    print("\n[summary.json]")
    summary = {
        "slug": SLUG,
        "generated_at": pd.Timestamp.now().isoformat(),
        "period": {
            "start": str(common[0].date()),
            "end": str(common[-1].date()),
            "trading_days": int(len(common)),
        },
        "strategy": {
            "monthly_payment_usd": MONTHLY_PAYMENT,
            "loan_duration_months": LOAN_DURATION_M,
            "taeg_scenarios": TAEG_SCENARIOS,
            "capitals_derived_usd": capitals,
            "indices": list(INDICES),
            "windows_months": WINDOWS_MONTHS,
            "step_months": STEP_MONTHS,
        },
        "scenarios": {},
        "breakeven_curve": {},
    }
    for (idx, taeg_key, win_label), bundle in scenarios.items():
        df = bundle["df"]
        sc = bundle["scorecard"]
        ratio_final = df["final_lump"] / df["final_pac"]
        excess_cagr = df["cagr_lump"] - df["cagr_pac"]
        key = f"{idx}__{taeg_key}__{win_label}"
        summary["scenarios"][key] = {
            "n_windows": int(len(df)),
            "scorecard": sc,
            "cagr_lump":  pcts(df["cagr_lump"]),
            "cagr_pac":   pcts(df["cagr_pac"]),
            "cagr_excess_lump_minus_pac": pcts(excess_cagr),
            "mdd_lump":   pcts(df["mdd_lump"]),
            "mdd_pac":    pcts(df["mdd_pac"]),
            "vol_lump":   pcts(df["vol_lump"]),
            "vol_pac":    pcts(df["vol_pac"]),
            "final_lump": pcts(df["final_lump"]),
            "final_pac":  pcts(df["final_pac"]),
            "ratio_lump_over_pac": pcts(ratio_final),
            "win_rate_cagr": float((df["cagr_lump"] > df["cagr_pac"]).mean()),
            "win_rate_final": float((df["final_lump"] > df["final_pac"]).mean()),
            "shortfall_p05_pct": float((ratio_final.quantile(0.05) - 1) * 100),
            "upside_p95_pct": float((ratio_final.quantile(0.95) - 1) * 100),
        }
    for (idx, taeg, win_label), wr in breakeven_data.items():
        summary["breakeven_curve"][
            f"{idx}__taeg_{taeg*100:.2f}__{win_label}"
        ] = wr
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print("  → summary.json")

    # 10. sim_data.json — dati monthly per simulatore
    print("\n[sim_data.json]")
    # Prendo le NAV mensili a inizio mese
    monthly_idx = pd.Series(common).groupby(
        common.to_period("M")
    ).min().values
    monthly_idx = pd.DatetimeIndex(monthly_idx).sort_values()

    sim_data = {
        "meta": {
            "start": str(monthly_idx[0].date()),
            "end": str(monthly_idx[-1].date()),
            "n_months": int(len(monthly_idx)),
            "monthly_payment": MONTHLY_PAYMENT,
            "loan_duration_months": LOAN_DURATION_M,
        },
        "dates": [str(d.date()) for d in monthly_idx],
        "nasdaq_nav": [round(float(v), 6) for v in
                       nq_nav.reindex(monthly_idx).ffill().values],
        "sp500_nav": [round(float(v), 6) for v in
                      sp_nav.reindex(monthly_idx).ffill().values],
    }
    with open(OUT_DIR / "sim_data.json", "w", encoding="utf-8") as f:
        json.dump(sim_data, f, separators=(",", ":"))
    print(f"  → sim_data.json ({len(monthly_idx)} mesi)")

    print("\nDONE.")
    print(f"Output in {OUT_DIR}\n")


if __name__ == "__main__":
    main()
