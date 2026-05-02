"""
SmartMoneyLab — E' davvero possibile comprare ai minimi?
========================================================

Confronto tra due strategie di accumulo a flusso trimestrale:

  Strategy A (Passive PIC): 100% del flusso trimestrale -> S&P 500 TR.

  Strategy B (Active Timing):
    Ogni trimestre calcolo il drawdown end-of-month dal massimo storico
    assoluto dell'S&P 500 TR.
    - Se DD < 25%: 90% flusso -> S&P 500 TR, 10% -> cassetto (CD al 2%
      lordo annuo, capitalizzazione mensile).
    - Se DD >= 25%:
        * cassetto > 0 -> svuoto tutto il cassetto su S&P 500 +
          100% del flusso del trimestre su S&P 500
        * cassetto = 0 -> 100% del flusso su S&P 500, niente accantonamento
    - Quando DD rientra sotto 25%, riprendo il pattern 90/10.

Confronto:
  - Rolling windows 10y (120 mesi) e 20y (240 mesi), step 3 mesi.
  - Metrica chiave: valore finale del portafoglio dopo N anni di contributi
    (i flussi esterni sono uguali nelle due strategie -> confronto pulito).
  - % finestre in cui Strategy B batte Strategy A.
  - Distribuzione dell'excess value (B - A).

Asset:
  - S&P 500 Total Return mensile (Shiller mirror).

Parametri tasso CD:
  - 2% lordo annuo, fisso. Modello conservativo: sopravvaluta gli anni 2010-2020
    (tassi reali sotto l'1%) e sottovaluta gli anni '80 (tassi 8-12%).
    Bilancio netto su 50 anni: leggermente sfavorevole alla strategia attiva
    (i drawdown grossi del periodo cadono in epoche a tassi alti).

Periodo: 1976-01 -> 2025-12.

Riproducibilita': Shiller mirror in cache. Dipendenze: pandas, numpy,
matplotlib, requests.

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
SLUG = "comprare-ai-minimi-market-timing"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo
START_DATE = "1976-01-01"
END_DATE = "2025-12-31"

# Parametri di simulazione
QUARTERLY_FLOW = 1000.0        # USD per trimestre
SAVINGS_PCT = 0.10             # 10% accantonamento
DRAWDOWN_TRIGGER = 0.25        # 25% drawdown trigger
CD_ANNUAL_RATE = 0.02          # 2% lordo annuo fisso
CD_MONTHLY_RATE = (1 + CD_ANNUAL_RATE) ** (1 / 12) - 1

# Parametri rolling
WINDOWS_MONTHS = {"10y": 120, "20y": 240}
STEP_MONTHS = 3

# Palette
COLORS = {
    "A_passive": "#1e3a8a",   # navy intenso — passive PIC
    "B_timing":  "#d97706",   # ambra — active timing
}


# -------------------------------------------------------------------- #
# Download S&P 500                                                     #
# -------------------------------------------------------------------- #

SHILLER_CSV_MIRROR = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
)
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _download(url: str, cache_name: str, retries: int = 3) -> bytes:
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        print(f"[cache] {cache_name}")
        return cache_path.read_bytes()
    headers = {"User-Agent": _BROWSER_UA}
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            print(f"[download] {url}")
            resp = requests.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            cache_path.write_bytes(resp.content)
            return resp.content
        except Exception as exc:
            last_err = exc
            print(f"  -> failed: {exc}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Download failed for {cache_name}: {last_err}")


def load_sp500_tr_monthly() -> pd.Series:
    """S&P 500 Total Return mensile, ricostruito dal mirror Shiller."""
    raw = _download(SHILLER_CSV_MIRROR, "shiller_mirror.csv").decode("utf-8")
    m = pd.read_csv(io.StringIO(raw))
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["Date"]).dt.to_period("M").dt.to_timestamp()
    m = m.set_index("date").sort_index()
    p = pd.to_numeric(m["SP500"], errors="coerce")
    d = pd.to_numeric(m["Dividend"], errors="coerce")
    monthly_div = d.shift(1) / 12
    tr = (p + monthly_div) / p.shift(1) - 1
    tr.name = "sp500_tr"
    return tr.dropna()


# -------------------------------------------------------------------- #
# Utility: NAV cumulato + drawdown                                     #
# -------------------------------------------------------------------- #

def cumulative_nav(returns: pd.Series) -> pd.Series:
    """NAV cumulato a partire da rendimenti mensili (NAV_0 = 1)."""
    return (1 + returns).cumprod()


def drawdown_from_peak(nav: pd.Series) -> pd.Series:
    """Drawdown dal massimo storico (negativo: -0.25 = -25%)."""
    return nav / nav.cummax() - 1


# -------------------------------------------------------------------- #
# Simulazione: due strategie di accumulo                               #
# -------------------------------------------------------------------- #

@dataclass
class SimResult:
    """Risultato di una simulazione di accumulo su un periodo."""
    portfolio_value: pd.Series   # valore totale del portafoglio mese per mese
    deploy_dates: list           # mesi in cui Strategy B ha scaricato il cassetto
    total_invested: float        # cash totale immesso (uguale per A e B)


def simulate_strategy_A(returns: pd.Series, quarterly_flow: float) -> SimResult:
    """
    Passive PIC trimestrale: ogni trimestre 100% del flusso entra in S&P 500.

    Convenzione: il flusso entra al PRIMO mese di ogni trimestre (es. gennaio,
    aprile, luglio, ottobre) — coerente con un PAC reale che parte a inizio
    trimestre.
    """
    dates = returns.index
    portfolio = 0.0   # valore in USD
    invested = 0.0
    values = []
    for date, r in returns.items():
        # Applica il rendimento del mese al portafoglio gia' presente
        portfolio *= (1 + r)
        # Se siamo a inizio trimestre, entra il flusso (mese 1, 4, 7, 10)
        if date.month in (1, 4, 7, 10):
            portfolio += quarterly_flow
            invested += quarterly_flow
        values.append((date, portfolio))
    s = pd.Series(dict(values), name="A_passive")
    s.index.name = "date"
    return SimResult(portfolio_value=s, deploy_dates=[], total_invested=invested)


def simulate_strategy_B(
    returns: pd.Series,
    quarterly_flow: float,
    savings_pct: float,
    drawdown_trigger: float,
    cd_monthly_rate: float,
) -> SimResult:
    """
    Active Timing: 90/10 normalmente, deploy del cassetto + 100% flusso quando
    drawdown >= trigger. Il drawdown e' calcolato dal massimo storico
    end-of-month dell'S&P 500 TR cumulato dall'inizio del periodo.

    Nota implementativa: il drawdown e' tracciato sul NAV dell'S&P 500 TR
    (non sul valore del portafoglio dell'investitore), perche' il "minimo di
    mercato" e' una proprieta' dell'asset, non del singolo conto.
    """
    sp500_nav = cumulative_nav(returns)
    sp500_dd = drawdown_from_peak(sp500_nav)

    portfolio_eq = 0.0   # quota S&P 500 in USD
    cassetto = 0.0       # quota CD in USD
    invested = 0.0
    deploys = []
    values = []

    for date, r in returns.items():
        # 1) Capitalizza il portafoglio S&P
        portfolio_eq *= (1 + r)
        # 2) Capitalizza il cassetto al CD (mensile)
        cassetto *= (1 + cd_monthly_rate)

        # 3) Se siamo a inizio trimestre, decisione di allocazione
        if date.month in (1, 4, 7, 10):
            current_dd = sp500_dd.loc[date]
            if current_dd <= -drawdown_trigger:
                # Drawdown attivato: deploy cassetto + 100% flusso su S&P
                deploy_amount = cassetto
                cassetto = 0.0
                portfolio_eq += deploy_amount + quarterly_flow
                invested += quarterly_flow
                if deploy_amount > 0:
                    deploys.append((date, deploy_amount))
            else:
                # Stato normale: 90/10
                portfolio_eq += quarterly_flow * (1 - savings_pct)
                cassetto += quarterly_flow * savings_pct
                invested += quarterly_flow

        values.append((date, portfolio_eq + cassetto))

    s = pd.Series(dict(values), name="B_timing")
    s.index.name = "date"
    return SimResult(portfolio_value=s, deploy_dates=deploys, total_invested=invested)


# -------------------------------------------------------------------- #
# Rolling windows: confronto sui valori finali                         #
# -------------------------------------------------------------------- #

@dataclass
class WindowResult:
    start: pd.Timestamp
    end: pd.Timestamp
    final_A: float
    final_B: float
    excess: float          # B - A
    excess_pct: float      # (B - A) / A
    n_deploys_in_window: int


def rolling_window_compare(
    returns: pd.Series,
    window_months: int,
    step_months: int,
    quarterly_flow: float,
    savings_pct: float,
    drawdown_trigger: float,
    cd_monthly_rate: float,
) -> list[WindowResult]:
    """
    Per ogni finestra rolling: simula entrambe le strategie da zero
    sul sotto-periodo, calcola i valori finali e confronta.

    Il drawdown viene RICALCOLATO da zero ad ogni finestra, perche'
    l'investitore che entra in quella finestra non vede i massimi
    precedenti. Coerente con la metodologia delle finestre rolling
    "ogni finestra parte fresh".
    """
    n = len(returns)
    out = []
    i = 0
    while i + window_months <= n:
        chunk = returns.iloc[i : i + window_months]
        sim_A = simulate_strategy_A(chunk, quarterly_flow)
        sim_B = simulate_strategy_B(
            chunk, quarterly_flow, savings_pct, drawdown_trigger, cd_monthly_rate
        )
        final_A = float(sim_A.portfolio_value.iloc[-1])
        final_B = float(sim_B.portfolio_value.iloc[-1])
        excess = final_B - final_A
        excess_pct = excess / final_A if final_A > 0 else float("nan")
        out.append(
            WindowResult(
                start=chunk.index[0],
                end=chunk.index[-1],
                final_A=final_A,
                final_B=final_B,
                excess=excess,
                excess_pct=excess_pct,
                n_deploys_in_window=len(sim_B.deploy_dates),
            )
        )
        i += step_months
    return out


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


def plot_excess_distribution(rolling_per_win: dict, fname: Path):
    """
    Boxplot: distribuzione dell'excess return percentuale (B vs A) per
    finestra 10y e 20y.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    labels = list(rolling_per_win.keys())
    data = [
        np.array([w.excess_pct * 100 for w in rolling_per_win[k]])
        for k in labels
    ]
    bp = ax.boxplot(
        data,
        tick_labels=[f"Rolling {k}" for k in labels],
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color="#0f172a", linewidth=2),
        whiskerprops=dict(color="#475569"),
        capprops=dict(color="#475569"),
        flierprops=dict(
            marker="o", markerfacecolor="#94a3b8", markeredgecolor="none", markersize=4, alpha=0.5
        ),
    )
    for patch in bp["boxes"]:
        patch.set_facecolor("#d97706")
        patch.set_alpha(0.85)
        patch.set_edgecolor("#0f172a")
    ax.axhline(0, color="#0f172a", linewidth=1.0, linestyle="--")
    _style_axes(
        ax,
        title="Strategy B − Strategy A: distribuzione dell'extra-rendimento (%)",
        ylabel="(Valore finale B − Valore finale A) / A, in %",
    )
    ax.text(
        0.99,
        -0.13,
        "Fonte: Shiller (S&P 500 TR). Flusso 1000$/trim. CD 2% lordo. Deploy a -25% drawdown.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_winrate_bar(rolling_per_win: dict, fname: Path):
    """Bar chart: % finestre in cui B batte A, per orizzonte."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    labels = list(rolling_per_win.keys())
    win_rates = [
        100 * np.mean([w.excess > 0 for w in rolling_per_win[k]])
        for k in labels
    ]
    bars = ax.bar(
        [f"Rolling {k}" for k in labels],
        win_rates,
        color="#d97706",
        alpha=0.85,
        edgecolor="#0f172a",
        width=0.5,
    )
    for bar, rate in zip(bars, win_rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            rate + 1,
            f"{rate:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="semibold",
            color="#0f172a",
        )
    ax.axhline(50, color="#94a3b8", linewidth=0.8, linestyle="--")
    ax.set_ylim(0, 100)
    _style_axes(
        ax,
        title="% finestre in cui la strategia attiva batte il PIC passivo",
        ylabel="% di finestre con valore finale B > A",
    )
    ax.text(
        0.99,
        -0.15,
        "Linea tratteggiata = 50% (parita'). Fonte: Shiller (S&P 500 TR), 1976-2025.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_full_period_curves(sim_A: SimResult, sim_B: SimResult, fname: Path):
    """Equity curves cumulate full-period delle due strategie."""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=200)
    ax.plot(
        sim_A.portfolio_value.index,
        sim_A.portfolio_value.values,
        color=COLORS["A_passive"],
        linewidth=2.0,
        label="Strategy A (PIC passivo)",
    )
    ax.plot(
        sim_B.portfolio_value.index,
        sim_B.portfolio_value.values,
        color=COLORS["B_timing"],
        linewidth=2.0,
        label="Strategy B (timing attivo)",
    )
    # Marker dei deploy del cassetto
    for date, amount in sim_B.deploy_dates:
        ax.axvline(date, color="#94a3b8", linewidth=0.6, alpha=0.5)
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    _style_axes(
        ax,
        title="Crescita del portafoglio: PIC passivo vs Timing attivo (1976-2025)",
        ylabel="Valore portafoglio (USD)",
        xlabel="",
    )
    ax.text(
        0.99,
        -0.13,
        "Flusso 1000$ ogni trimestre. CD al 2% lordo. Linee verticali grigie = deploy del cassetto.",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_final_values_box(rolling_per_win: dict, fname: Path):
    """
    Boxplot dei valori finali assoluti (USD) per A e B, sui due orizzonti.
    Doppia coppia di box affiancata.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=200, sharey=False)
    for ax, (win_label, results) in zip(axes, rolling_per_win.items()):
        finals_A = np.array([w.final_A for w in results])
        finals_B = np.array([w.final_B for w in results])
        bp = ax.boxplot(
            [finals_A, finals_B],
            tick_labels=["Passive", "Timing"],
            patch_artist=True,
            widths=0.55,
            medianprops=dict(color="#0f172a", linewidth=2),
            whiskerprops=dict(color="#475569"),
            capprops=dict(color="#475569"),
            flierprops=dict(
                marker="o", markerfacecolor="#94a3b8", markeredgecolor="none",
                markersize=4, alpha=0.5
            ),
        )
        for patch, color in zip(bp["boxes"], [COLORS["A_passive"], COLORS["B_timing"]]):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
            patch.set_edgecolor("#0f172a")
        _style_axes(
            ax,
            title=f"Valori finali — finestre rolling {win_label}",
            ylabel="Valore finale portafoglio (USD)",
        )
    fig.suptitle(
        "Distribuzione del valore finale del portafoglio per orizzonte",
        fontsize=15, fontweight="semibold", color="#0f172a", y=1.02,
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def main():
    print("=" * 64)
    print("SmartMoneyLab — E' davvero possibile comprare ai minimi?")
    print("=" * 64)

    # 1. Carica S&P 500
    sp500_tr = load_sp500_tr_monthly()
    sp500_tr = sp500_tr.loc[pd.Timestamp(START_DATE):pd.Timestamp(END_DATE)]
    print(f"Periodo: {sp500_tr.index.min().date()} -> {sp500_tr.index.max().date()}")
    print(f"Mesi disponibili: {len(sp500_tr)}")

    # 2. Simulazioni full-period (per equity curve illustrativa)
    print("\nSimulazione full-period (1976-2025)…")
    sim_A_full = simulate_strategy_A(sp500_tr, QUARTERLY_FLOW)
    sim_B_full = simulate_strategy_B(
        sp500_tr,
        QUARTERLY_FLOW,
        SAVINGS_PCT,
        DRAWDOWN_TRIGGER,
        CD_MONTHLY_RATE,
    )
    print(f"  Strategy A (Passive)  -> ${sim_A_full.portfolio_value.iloc[-1]:>12,.0f}  "
          f"(invested ${sim_A_full.total_invested:,.0f})")
    print(f"  Strategy B (Timing)   -> ${sim_B_full.portfolio_value.iloc[-1]:>12,.0f}  "
          f"(invested ${sim_B_full.total_invested:,.0f})")
    print(f"  N. deploy cassetto attivati: {len(sim_B_full.deploy_dates)}")
    if sim_B_full.deploy_dates:
        print("  Date dei deploy: " + ", ".join(
            d.strftime("%Y-%m") for d, _ in sim_B_full.deploy_dates
        ))

    # 3. Rolling windows
    rolling = {}
    pct = {}
    for win_label, win_months in WINDOWS_MONTHS.items():
        results = rolling_window_compare(
            sp500_tr, win_months, STEP_MONTHS,
            QUARTERLY_FLOW, SAVINGS_PCT, DRAWDOWN_TRIGGER, CD_MONTHLY_RATE,
        )
        rolling[win_label] = results
        excess_arr = pd.Series([w.excess for w in results])
        excess_pct_arr = pd.Series([w.excess_pct for w in results])
        win_rate = float(np.mean([w.excess > 0 for w in results]))
        deploys_per_win = pd.Series([w.n_deploys_in_window for w in results])
        pct[win_label] = {
            "n_windows": int(len(results)),
            "win_rate_B_beats_A": win_rate,
            "excess_usd": percentiles(excess_arr),
            "excess_pct": percentiles(excess_pct_arr),
            "deploys_per_window": {
                "mean": float(deploys_per_win.mean()),
                "max": int(deploys_per_win.max()),
                "share_zero_deploy": float((deploys_per_win == 0).mean()),
            },
        }
        print(f"\nRolling {win_label} ({len(results)} finestre):")
        print(f"  Win rate B vs A:          {win_rate*100:5.1f}%")
        print(f"  Excess pct mediano (B-A): {pct[win_label]['excess_pct']['p50']*100:+5.2f}%")
        print(f"  Excess pct p5:            {pct[win_label]['excess_pct']['p5']*100:+5.2f}%")
        print(f"  Excess pct p95:           {pct[win_label]['excess_pct']['p95']*100:+5.2f}%")
        print(f"  Deploy medi per finestra: {deploys_per_win.mean():.2f}")

    # 4. Grafici
    print("\nGenerazione grafici…")
    plot_full_period_curves(sim_A_full, sim_B_full, OUT_DIR / "01_equity_curves_fullperiod.png")
    plot_winrate_bar(rolling, OUT_DIR / "02_winrate_bar.png")
    plot_excess_distribution(rolling, OUT_DIR / "03_excess_distribution.png")
    plot_final_values_box(rolling, OUT_DIR / "04_final_values_box.png")

    # 5. Salva summary JSON
    summary = {
        "slug": SLUG,
        "period": {
            "start": str(sp500_tr.index.min().date()),
            "end": str(sp500_tr.index.max().date()),
            "n_months": int(len(sp500_tr)),
        },
        "params": {
            "quarterly_flow_usd": QUARTERLY_FLOW,
            "savings_pct": SAVINGS_PCT,
            "drawdown_trigger": DRAWDOWN_TRIGGER,
            "cd_annual_rate": CD_ANNUAL_RATE,
            "rolling_step_months": STEP_MONTHS,
            "windows_months": WINDOWS_MONTHS,
        },
        "full_sample": {
            "A_passive_final_usd": float(sim_A_full.portfolio_value.iloc[-1]),
            "B_timing_final_usd": float(sim_B_full.portfolio_value.iloc[-1]),
            "total_invested_usd": float(sim_A_full.total_invested),
            "deploys_count": len(sim_B_full.deploy_dates),
            "deploys_dates": [d.strftime("%Y-%m") for d, _ in sim_B_full.deploy_dates],
        },
        "rolling": pct,
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    # CSV per audit
    csv_df = pd.DataFrame({
        "A_passive_value": sim_A_full.portfolio_value,
        "B_timing_value": sim_B_full.portfolio_value,
    })
    csv_df.index.name = "date"
    csv_df.to_csv(OUT_DIR / "data.csv", float_format="%.2f")

    # Esporta anche i rendimenti S&P 500 mensili per il componente interattivo
    interactive_data = {
        "dates": [d.strftime("%Y-%m-%d") for d in sp500_tr.index],
        "returns": [float(r) for r in sp500_tr.values],
    }
    (OUT_DIR / "sp500_monthly_returns.json").write_text(
        json.dumps(interactive_data)
    )

    print(f"\nOutput salvati in: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()


# ====================================================================
# Note di lettura
# ====================================================================
#
# - "Win rate" = % di finestre in cui Strategy B (timing) ha valore finale
#   superiore a Strategy A (passive PIC). Se vicino al 50% le due strategie
#   sono indifferenti su questo dataset; sotto il 50% la passiva domina.
#
# - "Excess pct" = differenza percentuale tra valore finale B e A.
#   Mediana negativa significa che mediamente la strategia attiva perde.
#
# - "Deploy" = trimestre in cui Strategy B ha scaricato il cassetto su S&P 500
#   perche' il drawdown era >= 25%. Le date sono nel summary.json full_sample.
#
# - I dati S&P 500 mensili vengono esportati in JSON (`sp500_monthly_returns.json`)
#   per essere riutilizzati dal componente interattivo React MarketTimingSimulator.
# ====================================================================
# end of file
