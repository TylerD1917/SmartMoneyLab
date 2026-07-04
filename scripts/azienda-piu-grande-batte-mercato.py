"""
SmartMoneyLab — Investire solo nell'azienda piu' grande batte il mercato?
==========================================================================

Backtest di due strategie meccaniche vs S&P 500 (ETF ad accumulo tassazione IT):

  SP1 — al primo giorno di borsa di ogni anno, 100% sull'azienda USA #1
         per capitalizzazione. Rotazione annuale sul nuovo leader.
  SP3 — al primo giorno di borsa di ogni anno, equal weight sulle prime 3
         per capitalizzazione. Rotazione + ribilanciamento annuali.

Periodo: 1995-01-01 -> 2025-12-31 (31 anni). Inizio SPY nato 1993.

METODO
------
- Prezzi e dividendi daily via yfinance (auto_adjust=False, actions=True).
- Motore fiscale italiano (26%):
    * Plusvalenze da PREZZO delle azioni singole: tassate SOLO alla vendita
      (rotazione, alleggerimento in SP3, o liquidazione finale).
      Compensabili con lo "zainetto" minusvalenze — finestra: anno di
      realizzo + 4 successivi. Le posizioni mantenute non pagano tasse
      finche' non ruotano (differimento).
    * Dividendi: 26% ogni anno alla percezione, NON compensabili. Netto
      reinvestito.
    * Benchmark = ETF armonizzato ad accumulo: dividendi reinvestiti dentro
      il fondo (nessuna tassazione annuale), 26% sull'intera plusvalenza
      SOLO alla vendita finale.
- Rolling windows: coorti annuali (step 1 anno) su 5y e 10y, sul NETTO.
- Framework SmartMoneyLab a 7 criteri (vedi funzione scorecard).
- Metriche di rischio (vol, Sharpe, Sortino, MDD, Calmar) calcolate sui
  NAV daily LORDI — separare il profilo rischio/rendimento dallo scudo
  fiscale del wrapper.

OUTPUT in public/charts/azienda-piu-grande-batte-mercato/
--------------------------------------------------------
  01_equity_fullperiod.png       equity 1EUR, log, SP1/SP3/S&P500
  02_scorecard.png               scorecard 7 criteri SP1 e SP3
  03_gross_vs_net_tax.png        CAGR lordo vs netto + tax drag
  04_annual_returns.png          barre rendimenti annuali affiancati
  05_drawdown_curves.png         drawdown daily delle 3 strategie
  06_net_cagr_rolling_box.png    boxplot CAGR netto rolling 10y coorti
  07_net_cagr_rolling_5y_box.png boxplot CAGR netto rolling 5y coorti
  summary.json                   tutti i numeri usati nell'articolo
  rolling_windows.csv            long-format coorti 5y e 10y netto
  equity_curves_full.csv         NAV daily gross per il reel social

Uso locale:
    pip install yfinance pandas numpy matplotlib
    python scripts/azienda-piu-grande-batte-mercato.py

Il primo run scarica ~30 anni di dati (18 ticker) via Yahoo — 20-40 sec.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# yfinance ha bisogno di connessione internet (bloccata nel sandbox
# Cowork). Import lazy per non far crashare l'import del modulo in ambienti
# in cui non e' installato.
try:
    import yfinance as yf
except ImportError as e:
    raise SystemExit(
        "yfinance non installato. Esegui: pip install yfinance"
    ) from e

# --------------------------------------------------------------------- #
# Path e parametri                                                      #
# --------------------------------------------------------------------- #
SLUG = "azienda-piu-grande-batte-mercato"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
RANK_PATH = REPO_ROOT / "sp1_sp3" / "ranking_megacap_usa.csv"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

START_YEAR = 1995
END_YEAR = 2025
BENCH = "SPY"
TAX = 0.26
CARRY = 4  # anni utilizzo minusvalenze pregresse (realizzo + 4)
RF = 0.02  # risk-free annuo per Sharpe/Sortino
ROLL_WINS_YEARS = [5, 10]  # rolling coorti annuali (netto)

# Palette coerente con lo stile SML (navy per benchmark, ambra strategia)
COLOR_SP1 = "#dc2626"   # rosso mattone (concentrazione = rischio)
COLOR_SP3 = "#d97706"   # ambra (strategia protagonist)
COLOR_BENCH = "#1e3a8a"  # navy (benchmark ETF)


# --------------------------------------------------------------------- #
# Ranking + universo ticker                                             #
# --------------------------------------------------------------------- #
RANK = pd.read_csv(RANK_PATH)
RANK = RANK[(RANK.year >= START_YEAR) & (RANK.year <= END_YEAR)].copy()

TICKER_COLS = ["ticker1", "ticker2", "ticker3"]
UNIVERSE = sorted(set(RANK[TICKER_COLS].stack().dropna().unique().tolist() + [BENCH]))


# --------------------------------------------------------------------- #
# Download dati                                                         #
# --------------------------------------------------------------------- #
def download_prices() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ritorna (close, dividendi) daily forward-filled per l'universo."""
    print(f"[dati] scarico {len(UNIVERSE)} ticker da Yahoo Finance...")
    raw = yf.download(
        UNIVERSE,
        start=f"{START_YEAR - 1}-06-01",
        end=f"{END_YEAR + 1}-01-31",
        auto_adjust=False,
        actions=True,
        progress=False,
        group_by="column",
    )
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].sort_index().ffill()
        divs = raw["Dividends"].sort_index().fillna(0.0)
    else:
        # caso singolo ticker (non dovrebbe accadere qui)
        close = raw[["Close"]].rename(columns={"Close": UNIVERSE[0]})
        divs = raw[["Dividends"]].rename(columns={"Dividends": UNIVERSE[0]}).fillna(0.0)
    # copertura serie
    print("[dati] copertura:")
    for t in UNIVERSE:
        s = close[t].dropna()
        if len(s):
            print(f"       {t:6s} {s.index[0].date()} -> {s.index[-1].date()}")
        else:
            print(f"       {t:6s} NESSUN DATO")
    return close, divs


# --------------------------------------------------------------------- #
# Utility date                                                          #
# --------------------------------------------------------------------- #
def first_trading_day(close: pd.DataFrame, year: int):
    idx = close.index[(close.index >= f"{year}-01-01") & (close.index < f"{year}-02-01")]
    return idx[0] if len(idx) else None


def price_return(close: pd.Series, d0, d1) -> float:
    c0, c1 = close.get(d0), close.get(d1)
    if pd.isna(c0) or pd.isna(c1) or c0 <= 0:
        return float("nan")
    return c1 / c0 - 1


def div_yield(divs: pd.Series, close: pd.Series, d0, d1) -> float:
    c0 = close.get(d0)
    if pd.isna(c0) or c0 <= 0:
        return float("nan")
    mask = (divs.index >= d0) & (divs.index < d1)
    return float(divs.loc[mask].sum() / c0)


# --------------------------------------------------------------------- #
# Motore fiscale italiano — versione annuale su NAV                     #
# --------------------------------------------------------------------- #
class MinusBucket:
    """'Zainetto' minusvalenze IT: realizzo + 4 anni successivi."""

    def __init__(self, carry: int) -> None:
        self.carry = carry
        self.items: list[list[float]] = []  # [year, residuo]

    def purge(self, y: int) -> None:
        self.items = [x for x in self.items if x[0] >= y - self.carry]

    def offset(self, gain: float, y: int) -> float:
        """Compensa una plusvalenza positiva; ritorna imponibile residuo."""
        self.purge(y)
        for it in sorted(self.items, key=lambda z: z[0]):
            if gain <= 0:
                break
            u = min(gain, it[1])
            it[1] -= u
            gain -= u
        self.items = [x for x in self.items if x[1] > 1e-12]
        return gain

    def add_loss(self, loss: float, y: int) -> None:
        if loss > 0:
            self.items.append([y, loss])


def simulate_stock_strategy(
    close: pd.DataFrame,
    divs: pd.DataFrame,
    holdings_by_year: dict[int, list[str]],
    years: list[int],
    apply_tax: bool = True,
) -> tuple[pd.Series, pd.Series, list[dict]]:
    """Ritorna (nav_net_annual, nav_gross_annual, detail)."""
    port: dict[str, dict[str, float]] = {}
    bucket = MinusBucket(CARRY)
    wealth_net = 1.0
    gross = 1.0
    eqn, eqg, detail = [], [], []

    for i, y in enumerate(years):
        d0 = first_trading_day(close, y)
        d1 = first_trading_day(close, y + 1)
        if d0 is None or d1 is None:
            eqn.append(wealth_net)
            eqg.append(gross)
            continue

        tgt = holdings_by_year[y]
        # allocazione iniziale al primo anno
        if not port:
            equal_w = wealth_net / len(tgt)
            port = {t: {"val": equal_w, "basis": equal_w} for t in tgt}

        div_tax_y = 0.0
        # 1) crescita infra-annuale — prezzo + dividendo netto reinvestito
        for t, pos in port.items():
            p = price_return(close[t], d0, d1)
            dy = div_yield(divs[t], close[t], d0, d1)
            if pd.isna(p):
                p = 0.0
            if pd.isna(dy):
                dy = 0.0
            div_cash = pos["val"] * dy
            dtax = div_cash * TAX if apply_tax else 0.0
            div_tax_y += dtax
            pos["val"] = pos["val"] * (1 + p) + div_cash - dtax
            pos["basis"] += div_cash - dtax

        # gross tracking equal-weight sul target dell'anno (baseline lorda)
        rets_gross = []
        for t in tgt:
            p = price_return(close[t], d0, d1)
            dy = div_yield(divs[t], close[t], d0, d1)
            if not (pd.isna(p) or pd.isna(dy)):
                rets_gross.append(p + dy)
        if rets_gross:
            gross *= 1 + np.mean(rets_gross)

        V = sum(p["val"] for p in port.values())
        final = i == len(years) - 1
        nxt = None if final else holdings_by_year[years[i + 1]]
        realized = 0.0

        # 2) ribilanciamento / liquidazione
        if final:
            for t, pos in port.items():
                realized += pos["val"] - pos["basis"]
            newport = {}
        else:
            tv = V / len(nxt)
            newport = {}
            for t, pos in port.items():
                if t not in nxt:  # esco: vendo tutto
                    realized += pos["val"] - pos["basis"]
                elif pos["val"] > tv:  # alleggerisco
                    fs = (pos["val"] - tv) / pos["val"]
                    realized += (pos["val"] - pos["basis"]) * fs
                    newport[t] = {"val": tv, "basis": pos["basis"] * (1 - fs)}
                else:
                    newport[t] = {"val": pos["val"], "basis": pos["basis"]}
            for t in nxt:  # entro o rimpolpo
                if t not in newport:
                    newport[t] = {"val": tv, "basis": tv}
                elif newport[t]["val"] < tv:
                    add = tv - newport[t]["val"]
                    newport[t]["val"] += add
                    newport[t]["basis"] += add

        # 3) tassa su plusvalenze da prezzo
        if apply_tax:
            if realized >= 0:
                taxable = bucket.offset(realized, y)
                gain_tax = taxable * TAX
            else:
                gain_tax = 0.0
                bucket.add_loss(-realized, y)
        else:
            gain_tax = 0.0

        tax_tot = gain_tax
        Vpost = V - tax_tot
        if not final:
            k = Vpost / V if V > 0 else 1.0
            for t in newport:
                newport[t]["val"] *= k
                newport[t]["basis"] *= k
            port = newport
        wealth_net = Vpost
        eqn.append(Vpost)
        eqg.append(gross)
        detail.append(
            dict(
                anno=y,
                div_tax=div_tax_y,
                plus_realizz=realized,
                tax_plus=gain_tax,
                ricchezza_netta=Vpost,
                lordo=gross,
            )
        )
    return (
        pd.Series(eqn, index=years, name="net"),
        pd.Series(eqg, index=years, name="gross"),
        detail,
    )


def simulate_etf_accumulo(
    close: pd.DataFrame, divs: pd.DataFrame, years: list[int]
) -> tuple[pd.Series, pd.Series]:
    """ETF ad accumulo: dividendi reinvestiti dentro il fondo senza tax
    annuale (approssimato: azzero div-tax annua, capitalizzo TR); 26%
    sull'intera plusvalenza SOLO alla vendita finale, no compensazione."""
    val = 1.0
    basis = 1.0
    gross = 1.0
    eqn = []
    for i, y in enumerate(years):
        d0 = first_trading_day(close, y)
        d1 = first_trading_day(close, y + 1)
        p = 0.0 if d0 is None or d1 is None else price_return(close[BENCH], d0, d1)
        dy = 0.0 if d0 is None or d1 is None else div_yield(divs[BENCH], close[BENCH], d0, d1)
        p = 0.0 if pd.isna(p) else p
        dy = 0.0 if pd.isna(dy) else dy
        # ETF accumulo: TR pieno, senza tax annua sui dividendi
        val *= 1 + p + dy
        gross *= 1 + p + dy
        # basis non cambia mai (dividendi accumulati dentro il fondo)
        if i == len(years) - 1:
            gain = max(val - basis, 0.0)
            val -= gain * TAX
        eqn.append(val)
    return pd.Series(eqn, index=years, name="net"), pd.Series(
        [gross] * len(years), index=years, name="gross"
    )


# --------------------------------------------------------------------- #
# NAV daily (per metriche di rischio e drawdown)                        #
# --------------------------------------------------------------------- #
def build_daily_gross_nav(
    close: pd.DataFrame,
    divs: pd.DataFrame,
    holdings_by_year: dict[int, list[str]],
    years: list[int],
) -> pd.Series:
    """
    NAV daily lordo per un basket con rotazione annuale al primo trading
    day di ogni anno. Total return = prezzo + dividendo cash reinvestito
    prorata (ogni giorno di ex-div il dividendo viene aggiunto al NAV).
    Nessuna tassa: e' la baseline per vol / Sharpe / MDD.
    """
    all_days = close.index
    d_first = first_trading_day(close, years[0])
    d_last_end = first_trading_day(close, years[-1] + 1) or close.index[-1]
    mask = (all_days >= d_first) & (all_days <= d_last_end)
    days = all_days[mask]

    nav = pd.Series(index=days, dtype=float)
    holdings_now: list[str] = []
    units: dict[str, float] = {}
    current_nav = 1.0

    year_starts = {years[0]: d_first}
    for y in years[1:] + [years[-1] + 1]:
        d = first_trading_day(close, y)
        if d is not None:
            year_starts[y] = d

    def allocate(day, tickers: list[str], starting_value: float):
        weight = starting_value / len(tickers)
        return {t: weight / close[t].loc[day] for t in tickers if not pd.isna(close[t].loc[day])}

    holdings_now = holdings_by_year[years[0]]
    units = allocate(d_first, holdings_now, current_nav)

    prev_day = None
    year_boundaries = sorted(set(year_starts.values()))
    boundaries_set = set(year_boundaries)

    for day in days:
        # se giorno = start di un nuovo anno di rotazione, ribilancia
        if day != d_first and day in boundaries_set:
            # calcolo NAV corrente al prezzo di apertura di quel giorno
            current_nav = float(sum(u * close[t].loc[day] for t, u in units.items() if not pd.isna(close[t].loc[day])))
            # trova l'anno di questa data
            y_new = day.year
            if y_new in holdings_by_year:
                holdings_now = holdings_by_year[y_new]
                units = allocate(day, holdings_now, current_nav)
        # aggiungi dividendi cash: reinvestiti nello stesso titolo (units += cash/price)
        for t, u in list(units.items()):
            d_amount = divs[t].loc[day] if day in divs.index else 0.0
            if pd.notna(d_amount) and d_amount > 0:
                # dividendo cash sulle unita' correnti -> reinvesto in unita' dello stesso ticker
                cash = u * d_amount
                px = close[t].loc[day]
                if not pd.isna(px) and px > 0:
                    units[t] = u + cash / px
        # NAV di chiusura del giorno
        nav_today = float(sum(u * close[t].loc[day] for t, u in units.items() if not pd.isna(close[t].loc[day])))
        nav.loc[day] = nav_today
        prev_day = day

    return nav.dropna()


def build_daily_gross_nav_bench(close: pd.DataFrame, divs: pd.DataFrame, years: list[int]) -> pd.Series:
    """Baseline: SPY total return daily (dividendi reinvestiti, no tax)."""
    d_first = first_trading_day(close, years[0])
    d_last = first_trading_day(close, years[-1] + 1) or close.index[-1]
    mask = (close.index >= d_first) & (close.index <= d_last)
    days = close.index[mask]
    px = close[BENCH].loc[days]
    dv = divs[BENCH].loc[days] if BENCH in divs.columns else pd.Series(0.0, index=days)

    units = 1.0 / px.iloc[0]
    nav = pd.Series(index=days, dtype=float)
    for day in days:
        d_amount = dv.get(day, 0.0)
        d_amount = 0.0 if pd.isna(d_amount) else d_amount
        if d_amount > 0:
            p_today = px.loc[day]
            if not pd.isna(p_today) and p_today > 0:
                units += (units * d_amount) / p_today
        nav.loc[day] = units * px.loc[day]
    return nav.dropna()


# --------------------------------------------------------------------- #
# Metriche di rischio (su NAV daily)                                    #
# --------------------------------------------------------------------- #
TRADING_DAYS = 252


def cagr_d(nav: pd.Series) -> float:
    n_days = (nav.index[-1] - nav.index[0]).days
    if n_days <= 0 or nav.iloc[0] <= 0:
        return float("nan")
    years = n_days / 365.25
    return float((nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1)


def vol_d(nav: pd.Series) -> float:
    rets = nav.pct_change().dropna()
    return float(rets.std() * np.sqrt(TRADING_DAYS))


def mdd_d(nav: pd.Series) -> float:
    peak = nav.cummax()
    return float((nav / peak - 1).min())


def sharpe_d(nav: pd.Series, rf: float = RF) -> float:
    rets = nav.pct_change().dropna()
    if rets.std() == 0:
        return float("nan")
    ex = rets - rf / TRADING_DAYS
    return float(ex.mean() / rets.std() * np.sqrt(TRADING_DAYS))


def sortino_d(nav: pd.Series, rf: float = RF) -> float:
    rets = nav.pct_change().dropna()
    ex = rets - rf / TRADING_DAYS
    downside = ex[ex < 0]
    if len(downside) == 0 or downside.std() == 0:
        return float("nan")
    return float(ex.mean() / downside.std() * np.sqrt(TRADING_DAYS))


def calmar_d(nav: pd.Series) -> float:
    m = abs(mdd_d(nav))
    if m == 0:
        return float("nan")
    return cagr_d(nav) / m


# --------------------------------------------------------------------- #
# Rolling coorti annuali sul NETTO                                      #
# --------------------------------------------------------------------- #
def rolling_net_cohorts(
    close: pd.DataFrame,
    divs: pd.DataFrame,
    holdings_by_year: dict[int, list[str]],
    all_years: list[int],
    window_years: int,
    strategy_kind: str,  # "SP1", "SP3", "ETF"
) -> pd.DataFrame:
    """Per ogni anno di start, simula la strategia solo per window_years
    (compresa liquidazione finale netta) e ritorna CAGR netto della coorte."""
    rows = []
    for y0 in all_years:
        y1 = y0 + window_years - 1
        if y1 not in all_years:
            continue
        years_sub = list(range(y0, y1 + 1))
        h_sub = {y: holdings_by_year[y] for y in years_sub}
        if strategy_kind == "ETF":
            nn, gg = simulate_etf_accumulo(close, divs, years_sub)
        else:
            nn, gg, _ = simulate_stock_strategy(close, divs, h_sub, years_sub)
        final_net = float(nn.iloc[-1])
        cagr = final_net ** (1 / window_years) - 1
        rows.append(
            dict(
                strategy=strategy_kind,
                window_years=window_years,
                start_year=y0,
                end_year=y1,
                nav_final_net=final_net,
                cagr_net=cagr,
            )
        )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------- #
# Scorecard framework 7 criteri                                         #
# --------------------------------------------------------------------- #
def build_holdings(kind: str, years: list[int]) -> dict[int, list[str]]:
    h = {}
    for y in years:
        r = RANK[RANK.year == y].iloc[0]
        if kind == "SP1":
            h[y] = [r.ticker1]
        else:
            h[y] = [r.ticker1, r.ticker2, r.ticker3]
    return h


def scorecard(
    strat_daily: pd.Series,
    bench_daily: pd.Series,
    rolling_strat: pd.DataFrame,
    rolling_bench: pd.DataFrame,
) -> dict:
    """Applica il framework a 7 criteri per l'orizzonte di rolling passato."""
    med_strat = rolling_strat["cagr_net"].median()
    med_bench = rolling_bench["cagr_net"].median()
    # win rate cohorts
    m = rolling_strat.merge(
        rolling_bench, on="start_year", suffixes=("_s", "_b")
    )
    wins = (m["cagr_net_s"] > m["cagr_net_b"]).sum()
    win_rate = wins / len(m) if len(m) else float("nan")

    vol_s, vol_b = vol_d(strat_daily), vol_d(bench_daily)
    mdd_s, mdd_b = mdd_d(strat_daily), mdd_d(bench_daily)
    sha_s, sha_b = sharpe_d(strat_daily), sharpe_d(bench_daily)
    cal_s, cal_b = calmar_d(strat_daily), calmar_d(bench_daily)
    sor_s, sor_b = sortino_d(strat_daily), sortino_d(bench_daily)

    checks = {
        "cagr_median_ge_bench": bool(med_strat >= med_bench),
        "win_rate_ge_60": bool(win_rate >= 0.60),
        "vol_le_110": bool(vol_s <= vol_b * 1.10),
        "mdd_le_110": bool(abs(mdd_s) <= abs(mdd_b) * 1.10),
        "sharpe_ge_bench": bool(sha_s >= sha_b),
        "calmar_ge_bench": bool(cal_s >= cal_b),
        "sortino_ge_bench": bool(sor_s >= sor_b),
    }
    passed = sum(1 for v in checks.values() if v)
    verdict = "VINCE" if passed == 7 else ("PARZIALE" if passed >= 4 else "NON VINCE")
    return dict(
        checks=checks,
        passed=passed,
        total=7,
        verdict=verdict,
        medians={"strat": float(med_strat), "bench": float(med_bench)},
        win_rate=float(win_rate),
        risk={
            "vol_strat": vol_s,
            "vol_bench": vol_b,
            "mdd_strat": mdd_s,
            "mdd_bench": mdd_b,
            "sharpe_strat": sha_s,
            "sharpe_bench": sha_b,
            "sortino_strat": sor_s,
            "sortino_bench": sor_b,
            "calmar_strat": cal_s,
            "calmar_bench": cal_b,
        },
    )


# --------------------------------------------------------------------- #
# Plots                                                                 #
# --------------------------------------------------------------------- #
def _style():
    plt.rcParams.update(
        {
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
        }
    )


def plot_equity_full(nav_sp1: pd.Series, nav_sp3: pd.Series, nav_bench: pd.Series, out: Path):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(nav_sp1.index, nav_sp1.values / nav_sp1.iloc[0], color=COLOR_SP1, lw=1.8, label="SP1 (solo il numero 1)")
    ax.plot(nav_sp3.index, nav_sp3.values / nav_sp3.iloc[0], color=COLOR_SP3, lw=2.0, label="SP3 (prime 3, equal weight)")
    ax.plot(nav_bench.index, nav_bench.values / nav_bench.iloc[0], color=COLOR_BENCH, lw=1.8, label="S&P 500 (SPY total return)")
    ax.set_yscale("log")
    ax.set_ylabel("Crescita di 1 EUR (scala log)")
    ax.set_title(f"SP1 / SP3 vs S&P 500 — {START_YEAR}-{END_YEAR}, total return lordo")
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_drawdown_curves(nav_sp1, nav_sp3, nav_bench, out: Path):
    def dd(s):
        return s / s.cummax() - 1
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.fill_between(nav_sp1.index, dd(nav_sp1).values * 100, 0, color=COLOR_SP1, alpha=0.35, label="SP1")
    ax.fill_between(nav_sp3.index, dd(nav_sp3).values * 100, 0, color=COLOR_SP3, alpha=0.35, label="SP3")
    ax.plot(nav_bench.index, dd(nav_bench).values * 100, color=COLOR_BENCH, lw=1.6, label="S&P 500")
    ax.set_ylabel("Drawdown (%)")
    ax.set_title("Drawdown daily — SP1 vs SP3 vs S&P 500")
    ax.legend(loc="lower left", frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_scorecard(sc10_sp1: dict, sc10_sp3: dict, out: Path):
    labels = [
        "CAGR mediano ≥ bench",
        "Win rate ≥ 60%",
        "Vol ≤ bench × 1.10",
        "MDD ≤ bench × 1.10",
        "Sharpe ≥ bench",
        "Calmar ≥ bench",
        "Sortino ≥ bench",
    ]
    keys = [
        "cagr_median_ge_bench",
        "win_rate_ge_60",
        "vol_le_110",
        "mdd_le_110",
        "sharpe_ge_bench",
        "calmar_ge_bench",
        "sortino_ge_bench",
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, len(labels) - 0.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["SP1 (10y)", "SP3 (10y)"])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    for xi, sc in enumerate([sc10_sp1, sc10_sp3]):
        for yi, k in enumerate(keys):
            ok = sc["checks"][k]
            color = "#16a34a" if ok else "#dc2626"
            ax.add_patch(plt.Rectangle((xi - 0.42, yi - 0.42), 0.84, 0.84, color=color, alpha=0.85))
            ax.text(xi, yi, "✓" if ok else "✗", ha="center", va="center", color="white", fontweight="bold", fontsize=16)
    ax.set_title(
        f"Scorecard framework 7 criteri — orizzonte 10y\n"
        f"SP1: {sc10_sp1['passed']}/7 → {sc10_sp1['verdict']}   |   "
        f"SP3: {sc10_sp3['passed']}/7 → {sc10_sp3['verdict']}"
    )
    ax.grid(False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_gross_vs_net(rows: list[dict], out: Path):
    """rows = [{name, cagr_gross, cagr_net, tax_drag_bps, multiplo_net}, ...]"""
    names = [r["name"] for r in rows]
    gross = [r["cagr_gross"] * 100 for r in rows]
    net = [r["cagr_net"] * 100 for r in rows]
    drag = [r["tax_drag_bps"] for r in rows]
    x = np.arange(len(names))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1.4, 1]})
    w = 0.36
    ax1.bar(x - w / 2, gross, width=w, color="#94a3b8", label="Lordo")
    ax1.bar(x + w / 2, net, width=w, color=COLOR_BENCH, label="Netto")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names)
    ax1.set_ylabel("CAGR (%)")
    ax1.set_title("CAGR lordo vs netto (tassazione IT)")
    ax1.legend(frameon=False)
    for xi, g, n in zip(x, gross, net):
        ax1.text(xi - w / 2, g + 0.2, f"{g:.1f}", ha="center", fontsize=9)
        ax1.text(xi + w / 2, n + 0.2, f"{n:.1f}", ha="center", fontsize=9)

    colors = [COLOR_SP1, COLOR_SP3, COLOR_BENCH]
    ax2.bar(x, drag, color=colors[: len(x)])
    ax2.set_xticks(x)
    ax2.set_xticklabels(names)
    ax2.set_ylabel("Tax drag annuo (bps)")
    ax2.set_title("Costo fiscale annuo (bps)")
    for xi, d in zip(x, drag):
        ax2.text(xi, d + 5, f"{d:.0f}", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_rolling_box(rolls: dict[str, pd.DataFrame], window: int, out: Path):
    """rolls = {'SP1': df, 'SP3': df, 'ETF': df} — colonna cagr_net."""
    labels = list(rolls.keys())
    data = [rolls[k]["cagr_net"].dropna().values * 100 for k in labels]
    colors = {"SP1": COLOR_SP1, "SP3": COLOR_SP3, "ETF": COLOR_BENCH}
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bp = ax.boxplot(data, patch_artist=True, showfliers=True, widths=0.55)
    for box, k in zip(bp["boxes"], labels):
        box.set(facecolor=colors[k], alpha=0.55)
    for i, arr in enumerate(data, start=1):
        med = np.median(arr)
        ax.text(i, med, f" {med:.1f}%", va="center", fontsize=10, color="black", fontweight="bold")
    ax.set_xticklabels(labels)
    ax.set_ylabel("CAGR netto della coorte (%)")
    ax.set_title(f"CAGR netto — coorti annuali rolling di {window} anni")
    ax.axhline(0, color="black", lw=0.5)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_annual_returns(res: pd.DataFrame, out: Path):
    """res = DataFrame con index=anno e colonne SP1, SP3, BENCH (rendimento annuo lordo)."""
    x = np.arange(len(res))
    w = 0.28
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(x - w, res["SP1"].values * 100, width=w, color=COLOR_SP1, label="SP1")
    ax.bar(x, res["SP3"].values * 100, width=w, color=COLOR_SP3, label="SP3")
    ax.bar(x + w, res["BENCH"].values * 100, width=w, color=COLOR_BENCH, label="S&P 500")
    ax.set_xticks(x)
    ax.set_xticklabels(res.index.astype(str), rotation=90, fontsize=8)
    ax.set_ylabel("Rendimento annuo (%)")
    ax.set_title("Rendimenti annuali — SP1 vs SP3 vs S&P 500")
    ax.axhline(0, color="black", lw=0.6)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #
def main():
    _style()
    years = list(range(START_YEAR, END_YEAR + 1))
    print(f"[main] periodo {START_YEAR}-{END_YEAR}, {len(years)} anni; universo: {UNIVERSE}")

    close, divs = download_prices()

    # ----- 1) full-sample netto/lordo -----
    print("\n[1/6] Simulazione full-sample netta (motore fiscale IT)...")
    h_sp1 = build_holdings("SP1", years)
    h_sp3 = build_holdings("SP3", years)

    sp1_net, sp1_gross, sp1_detail = simulate_stock_strategy(close, divs, h_sp1, years)
    sp3_net, sp3_gross, sp3_detail = simulate_stock_strategy(close, divs, h_sp3, years)
    etf_net, etf_gross = simulate_etf_accumulo(close, divs, years)

    def _cagr_series(s: pd.Series) -> float:
        return float(s.iloc[-1] ** (1 / len(s)) - 1)

    cagr_sp1_g = _cagr_series(sp1_gross)
    cagr_sp3_g = _cagr_series(sp3_gross)
    cagr_etf_g = _cagr_series(etf_gross)
    cagr_sp1_n = _cagr_series(sp1_net)
    cagr_sp3_n = _cagr_series(sp3_net)
    cagr_etf_n = _cagr_series(etf_net)

    tax_drag = {
        "SP1": (cagr_sp1_g - cagr_sp1_n) * 10000,
        "SP3": (cagr_sp3_g - cagr_sp3_n) * 10000,
        "ETF": (cagr_etf_g - cagr_etf_n) * 10000,
    }
    print("      CAGR lordo/netto/tax drag:")
    for k, g, n, d in [
        ("SP1", cagr_sp1_g, cagr_sp1_n, tax_drag["SP1"]),
        ("SP3", cagr_sp3_g, cagr_sp3_n, tax_drag["SP3"]),
        ("ETF", cagr_etf_g, cagr_etf_n, tax_drag["ETF"]),
    ]:
        print(f"       {k}: {g*100:5.2f}% / {n*100:5.2f}% / {d:5.0f} bps")

    # ----- 2) NAV daily lordi per metriche di rischio -----
    print("\n[2/6] NAV daily lordi per metriche di rischio...")
    nav_sp1_d = build_daily_gross_nav(close, divs, h_sp1, years)
    nav_sp3_d = build_daily_gross_nav(close, divs, h_sp3, years)
    nav_bench_d = build_daily_gross_nav_bench(close, divs, years)

    risk_full = {
        "SP1": {
            "cagr": cagr_d(nav_sp1_d),
            "vol": vol_d(nav_sp1_d),
            "mdd": mdd_d(nav_sp1_d),
            "sharpe": sharpe_d(nav_sp1_d),
            "sortino": sortino_d(nav_sp1_d),
            "calmar": calmar_d(nav_sp1_d),
            "multiplo": float(nav_sp1_d.iloc[-1] / nav_sp1_d.iloc[0]),
        },
        "SP3": {
            "cagr": cagr_d(nav_sp3_d),
            "vol": vol_d(nav_sp3_d),
            "mdd": mdd_d(nav_sp3_d),
            "sharpe": sharpe_d(nav_sp3_d),
            "sortino": sortino_d(nav_sp3_d),
            "calmar": calmar_d(nav_sp3_d),
            "multiplo": float(nav_sp3_d.iloc[-1] / nav_sp3_d.iloc[0]),
        },
        "BENCH": {
            "cagr": cagr_d(nav_bench_d),
            "vol": vol_d(nav_bench_d),
            "mdd": mdd_d(nav_bench_d),
            "sharpe": sharpe_d(nav_bench_d),
            "sortino": sortino_d(nav_bench_d),
            "calmar": calmar_d(nav_bench_d),
            "multiplo": float(nav_bench_d.iloc[-1] / nav_bench_d.iloc[0]),
        },
    }
    for k, m in risk_full.items():
        print(
            f"      {k}: CAGR {m['cagr']*100:5.2f}%  Vol {m['vol']*100:5.2f}%  "
            f"MDD {m['mdd']*100:6.2f}%  Sharpe {m['sharpe']:.2f}  "
            f"Sortino {m['sortino']:.2f}  Calmar {m['calmar']:.2f}  "
            f"x{m['multiplo']:.1f}"
        )

    # ----- 3) rolling netto coorti annuali -----
    print("\n[3/6] Rolling netto coorti annuali...")
    rolling_all: dict[int, dict[str, pd.DataFrame]] = {}
    for w in ROLL_WINS_YEARS:
        rolling_all[w] = {
            "SP1": rolling_net_cohorts(close, divs, h_sp1, years, w, "SP1"),
            "SP3": rolling_net_cohorts(close, divs, h_sp3, years, w, "SP3"),
            "ETF": rolling_net_cohorts(close, divs, h_sp3, years, w, "ETF"),
        }
        for k, df in rolling_all[w].items():
            print(
                f"      [{w}y] {k}: {len(df)} coorti | mediana CAGR net {df['cagr_net'].median()*100:.2f}%"
            )

    # ----- 4) scorecard sui rolling 10y -----
    print("\n[4/6] Scorecard framework 7 criteri (rolling 10y)...")
    sc10_sp1 = scorecard(nav_sp1_d, nav_bench_d, rolling_all[10]["SP1"], rolling_all[10]["ETF"])
    sc10_sp3 = scorecard(nav_sp3_d, nav_bench_d, rolling_all[10]["SP3"], rolling_all[10]["ETF"])
    sc5_sp1 = scorecard(nav_sp1_d, nav_bench_d, rolling_all[5]["SP1"], rolling_all[5]["ETF"])
    sc5_sp3 = scorecard(nav_sp3_d, nav_bench_d, rolling_all[5]["SP3"], rolling_all[5]["ETF"])
    for label, sc in [("SP1 10y", sc10_sp1), ("SP3 10y", sc10_sp3), ("SP1 5y", sc5_sp1), ("SP3 5y", sc5_sp3)]:
        print(f"      {label}: {sc['passed']}/7 -> {sc['verdict']}")

    # ----- 5) plot -----
    print("\n[5/6] Plot...")
    plot_equity_full(nav_sp1_d, nav_sp3_d, nav_bench_d, OUT_DIR / "01_equity_fullperiod.png")
    plot_scorecard(sc10_sp1, sc10_sp3, OUT_DIR / "02_scorecard.png")

    rows_gvn = [
        {"name": "SP1", "cagr_gross": cagr_sp1_g, "cagr_net": cagr_sp1_n, "tax_drag_bps": tax_drag["SP1"], "multiplo_net": float(sp1_net.iloc[-1])},
        {"name": "SP3", "cagr_gross": cagr_sp3_g, "cagr_net": cagr_sp3_n, "tax_drag_bps": tax_drag["SP3"], "multiplo_net": float(sp3_net.iloc[-1])},
        {"name": "S&P 500 (accumulo)", "cagr_gross": cagr_etf_g, "cagr_net": cagr_etf_n, "tax_drag_bps": tax_drag["ETF"], "multiplo_net": float(etf_net.iloc[-1])},
    ]
    plot_gross_vs_net(rows_gvn, OUT_DIR / "03_gross_vs_net_tax.png")

    # rendimenti annuali lordi (annualizzato per riga)
    annual = pd.DataFrame(index=years, columns=["SP1", "SP3", "BENCH"], dtype=float)
    for y in years:
        d0 = first_trading_day(close, y)
        d1 = first_trading_day(close, y + 1)
        if d0 is None or d1 is None:
            continue
        # SP1: rendimento del ticker #1
        t1 = RANK[RANK.year == y].iloc[0].ticker1
        annual.loc[y, "SP1"] = price_return(close[t1], d0, d1) + div_yield(divs[t1], close[t1], d0, d1)
        # SP3: media EW
        rr = RANK[RANK.year == y].iloc[0]
        rets = []
        for t in [rr.ticker1, rr.ticker2, rr.ticker3]:
            p = price_return(close[t], d0, d1)
            dy = div_yield(divs[t], close[t], d0, d1)
            if not (pd.isna(p) or pd.isna(dy)):
                rets.append(p + dy)
        annual.loc[y, "SP3"] = np.mean(rets) if rets else np.nan
        annual.loc[y, "BENCH"] = price_return(close[BENCH], d0, d1) + div_yield(divs[BENCH], close[BENCH], d0, d1)
    plot_annual_returns(annual.dropna(), OUT_DIR / "04_annual_returns.png")
    plot_drawdown_curves(nav_sp1_d, nav_sp3_d, nav_bench_d, OUT_DIR / "05_drawdown_curves.png")
    plot_rolling_box(rolling_all[10], 10, OUT_DIR / "06_net_cagr_rolling_box.png")
    plot_rolling_box(rolling_all[5], 5, OUT_DIR / "07_net_cagr_rolling_5y_box.png")

    # ----- 6) salvataggio CSV/JSON -----
    print("\n[6/6] Salvataggio CSV + JSON...")
    # CSV rolling long
    rows_r = []
    for w, d in rolling_all.items():
        for k, df in d.items():
            for _, row in df.iterrows():
                rows_r.append(row.to_dict())
    pd.DataFrame(rows_r).to_csv(OUT_DIR / "rolling_windows.csv", index=False)

    # equity curves daily (per reel) — normalizzate a 1.0 al primo giorno
    equity_full = pd.DataFrame(
        {
            "sp1_nav": nav_sp1_d / nav_sp1_d.iloc[0],
            "sp3_nav": nav_sp3_d / nav_sp3_d.iloc[0],
            "bench_nav": nav_bench_d / nav_bench_d.iloc[0],
        }
    ).dropna()
    equity_full.to_csv(OUT_DIR / "equity_curves_full.csv", index_label="date")

    # win rate ETF-battente per strategia e orizzonte
    def _win_rate(strat_df: pd.DataFrame, etf_df: pd.DataFrame) -> float:
        m = strat_df.merge(etf_df, on="start_year", suffixes=("_s", "_b"))
        if not len(m):
            return float("nan")
        return float((m["cagr_net_s"] > m["cagr_net_b"]).mean())

    def _stats(df: pd.DataFrame) -> dict:
        arr = df["cagr_net"].dropna().values
        return {
            "n": int(len(arr)),
            "median": float(np.median(arr)) if len(arr) else float("nan"),
            "p5": float(np.percentile(arr, 5)) if len(arr) else float("nan"),
            "p25": float(np.percentile(arr, 25)) if len(arr) else float("nan"),
            "p75": float(np.percentile(arr, 75)) if len(arr) else float("nan"),
            "p95": float(np.percentile(arr, 95)) if len(arr) else float("nan"),
            "min": float(arr.min()) if len(arr) else float("nan"),
            "max": float(arr.max()) if len(arr) else float("nan"),
        }

    summary = {
        "slug": SLUG,
        "parametri": {
            "start_year": START_YEAR,
            "end_year": END_YEAR,
            "tax_rate": TAX,
            "carry_years": CARRY,
            "risk_free": RF,
            "benchmark": BENCH,
            "rolling_windows_years": ROLL_WINS_YEARS,
            "universo": UNIVERSE,
        },
        "full_sample_risk": risk_full,
        "full_sample_cagr_net_gross": {
            "SP1": {"gross": cagr_sp1_g, "net": cagr_sp1_n, "tax_drag_bps": tax_drag["SP1"], "multiplo_net": float(sp1_net.iloc[-1])},
            "SP3": {"gross": cagr_sp3_g, "net": cagr_sp3_n, "tax_drag_bps": tax_drag["SP3"], "multiplo_net": float(sp3_net.iloc[-1])},
            "ETF": {"gross": cagr_etf_g, "net": cagr_etf_n, "tax_drag_bps": tax_drag["ETF"], "multiplo_net": float(etf_net.iloc[-1])},
        },
        "rolling_net": {
            f"{w}y": {
                "SP1": {"stats": _stats(rolling_all[w]["SP1"]), "win_rate_vs_etf": _win_rate(rolling_all[w]["SP1"], rolling_all[w]["ETF"])},
                "SP3": {"stats": _stats(rolling_all[w]["SP3"]), "win_rate_vs_etf": _win_rate(rolling_all[w]["SP3"], rolling_all[w]["ETF"])},
                "ETF": {"stats": _stats(rolling_all[w]["ETF"])},
            }
            for w in ROLL_WINS_YEARS
        },
        "scorecard": {
            "SP1_10y": sc10_sp1,
            "SP3_10y": sc10_sp3,
            "SP1_5y": sc5_sp1,
            "SP3_5y": sc5_sp3,
        },
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)

    # dettaglio annuale (tasse pagate ogni anno)
    pd.DataFrame(sp1_detail).to_csv(OUT_DIR / "detail_sp1.csv", index=False)
    pd.DataFrame(sp3_detail).to_csv(OUT_DIR / "detail_sp3.csv", index=False)

    print(f"\nOK. Grafici + JSON + CSV in: {OUT_DIR}")
    print(f"Verdict SP1 (10y): {sc10_sp1['verdict']}")
    print(f"Verdict SP3 (10y): {sc10_sp3['verdict']}")


if __name__ == "__main__":
    main()
