"""
SmartMoneyLab — Quale segmento del mercato azionario e' il migliore?
====================================================================

Confronto su finestre rolling tra i principali segmenti azionari globali:
  - MSCI World (developed, 23 paesi)
  - MSCI USA (proxy S&P 500)
  - MSCI Europe
  - MSCI Japan
  - MSCI Emerging Markets (EM)
  - MSCI EM Asia (sotto-segmento Asia di EM)
  - MSCI World Small Cap
  - NASDAQ Composite (price-only via yfinance, TR ricostruito con dividend
    yield costante ~0.8%/anno)

Periodo: dicembre 2000 → ultimo mese MSCI disponibile (~25 anni).
Frequenza: monthly end-of-month.
Index level: Gross (dividendi reinvestiti, pre-withholding-tax). Coerente
con S&P 500 TR Shiller usato negli articoli precedenti.

Output:
- public/charts/qual-e-il-miglior-segmento-azionario/
    01_boxplot_cagr_5y.png
    02_boxplot_cagr_10y.png
    03_equity_curves.png
    04_drawdown_distribution_10y.png
    05_leadership_rotation_10y.png   (heatmap del "winner" per finestra)
- summary.json, data.csv

Riproducibilita': i CSV MSCI vanno scaricati manualmente in data/raw/
(vedi note di accompagnamento). NASDAQ scaricato automaticamente.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -------------------------------------------------------------------- #
# Setup percorsi                                                       #
# -------------------------------------------------------------------- #
SLUG = "qual-e-il-miglior-segmento-azionario"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Accetta sia data/raw che data/row (typo possibile)
RAW_CANDIDATES = [REPO_ROOT / "data" / "raw", REPO_ROOT / "data" / "row"]
RAW_DIR = next((p for p in RAW_CANDIDATES if p.exists()), RAW_CANDIDATES[0])

CACHE_DIR = REPO_ROOT / "data" / "cache"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Periodo di analisi: tutti gli MSCI partono Dec 2000
START_DATE = "2001-01-01"  # primo dato utile post-baseline
END_DATE = "2025-12-31"

# Parametri rolling
WINDOWS_MONTHS = {"5y": 60, "10y": 120}
STEP_MONTHS = 6

# Mappatura indici da CSV MSCI a label leggibili
MSCI_FILES = {
    "msci_world.csv":            "World",
    "msci_usa.csv":               "USA",
    "msci_europe.csv":            "Europe",
    "msci_japan.csv":             "Japan",
    "msci_em.csv":                "EM",
    "msci_em_asia.csv":           "EM Asia",
    "msci_world_smallcap.csv":    "World Small Cap",
    # Esclusi: msci_world_withusa (ridondante con World), msci_world_information_technology (parte 2013)
}

# NASDAQ Composite via yfinance (price-only, TR ricostruito)
NASDAQ_TICKER = "^IXIC"
NASDAQ_DIVIDEND_YIELD_ANNUAL = 0.008  # ~0.8% storica del Nasdaq Composite

# Palette: 8 colori distinguibili anche per daltonici, gradiente da
# navy (USA) a ambra (EM) per coerenza con gli altri articoli del blog
COLORS = {
    "World":            "#1e3a8a",   # navy intenso
    "USA":              "#3b82f6",   # blu medio
    "NASDAQ":           "#0ea5e9",   # ciano
    "Europe":           "#10b981",   # verde
    "Japan":            "#dc2626",   # rosso (bandiera)
    "EM":               "#f59e0b",   # ambra
    "EM Asia":          "#d97706",   # ambra scuro
    "World Small Cap":  "#8b5cf6",   # viola
}


# -------------------------------------------------------------------- #
# Parser CSV MSCI                                                      #
# -------------------------------------------------------------------- #

def parse_msci_csv(path: Path) -> pd.Series:
    """
    Parser robusto per i CSV scaricabili da msci.com/end-of-day-data-search.

    Struttura tipica:
      Riga 1-6:   metadata ("Index Level: Gross", "Currency: USD", ecc.)
      Riga 7:     header "Date" + nome indice
      Riga 8+:    dati: "Mon DD, YYYY","X,XXX.XXX"
      Coda:       footer con disclaimer legale (varie righe non parsabili)

    Date in formato "Mon DD, YYYY" (es. "Dec 29, 2000").
    Valori con virgola separatore migliaia.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Trova la riga "Date","..."
    header_idx = None
    for i, line in enumerate(lines):
        if line.lower().startswith('"date"'):
            header_idx = i
            break
    if header_idx is None:
        raise RuntimeError(f"Header 'Date' non trovato in {path.name}")

    # Da header_idx+1 in poi, parsa le righe di dati finche' la prima
    # colonna e' parsabile come data MSCI
    dates, values = [], []
    date_pat = re.compile(r'^"([A-Z][a-z]{2} \d{1,2}, \d{4})","([\d,\.]+)"\s*$')
    for line in lines[header_idx + 1:]:
        m = date_pat.match(line)
        if not m:
            # Probabile inizio del footer disclaimer
            break
        try:
            d = pd.to_datetime(m.group(1), format="%b %d, %Y")
            v = float(m.group(2).replace(",", ""))
        except Exception:
            break
        dates.append(d)
        values.append(v)

    if not dates:
        raise RuntimeError(f"Nessuna riga dati parsata da {path.name}")

    s = pd.Series(values, index=pd.DatetimeIndex(dates))
    s = s.sort_index()
    # Normalizzo l'index al primo del mese (i dati MSCI sono end-of-month
    # ma con data variabile: usiamo il period mensile come chiave)
    s.index = s.index.to_period("M").to_timestamp()
    s.name = path.stem
    return s


def load_all_msci() -> dict[str, pd.Series]:
    """Carica tutti i CSV MSCI elencati in MSCI_FILES."""
    out = {}
    print(f"Caricamento dati MSCI da {RAW_DIR}…")
    for fname, label in MSCI_FILES.items():
        path = RAW_DIR / fname
        if not path.exists():
            print(f"  [skip] {fname} non trovato — escluso dall'analisi")
            continue
        s = parse_msci_csv(path)
        out[label] = s
        print(f"  [ok]   {label:18s}  {s.index.min().date()} -> {s.index.max().date()}  "
              f"({len(s)} mesi)")
    return out


# -------------------------------------------------------------------- #
# NASDAQ via yfinance                                                  #
# -------------------------------------------------------------------- #

def load_nasdaq_monthly_tr() -> pd.Series:
    """
    NASDAQ Composite mensile end-of-month con TR ricostruito.

    yfinance restituisce solo Price Index per ^IXIC. Il dividend yield
    medio storico del NASDAQ Composite e' ~0.8%/anno (molto sotto S&P
    perche' tech ha basso payout). Lo aggiungiamo come correzione TR
    costante: r_tr_t ≈ r_price_t + 0.008/12.
    """
    cache_path = CACHE_DIR / "yahoo_nasdaq_monthly.csv"
    if cache_path.exists():
        print(f"[cache] {cache_path.name}")
        df = pd.read_csv(cache_path, parse_dates=["Date"]).set_index("Date")
        price = pd.to_numeric(df["Close"], errors="coerce").dropna()
    else:
        try:
            import yfinance as yf
        except ImportError:
            raise RuntimeError(
                "yfinance non installato. Esegui: pip install yfinance"
            )
        print("[yfinance] downloading ^IXIC monthly…")
        data = yf.Ticker(NASDAQ_TICKER).history(
            start=START_DATE, end=END_DATE, interval="1mo", auto_adjust=False
        )
        if data.empty:
            raise RuntimeError("yfinance ha restituito dati vuoti per ^IXIC")
        data.index = pd.DatetimeIndex(data.index).tz_localize(None)
        out = pd.DataFrame({"Close": data["Close"]})
        out.index.name = "Date"
        out.to_csv(cache_path)
        price = out["Close"]

    # Normalizzo l'index al primo del mese
    price.index = pd.DatetimeIndex(price.index).to_period("M").to_timestamp()
    price = price.groupby(price.index).last().sort_index()
    price.name = "nasdaq_close"
    return price


def nasdaq_to_tr_series(price: pd.Series, dividend_yield_annual: float) -> pd.Series:
    """
    Da price daily a NAV TR ricostruito mensile, sommando il dividend
    yield mensile costante ai rendimenti price.
    """
    monthly_div_factor = (1 + dividend_yield_annual) ** (1 / 12) - 1
    price_returns = price.pct_change().dropna()
    tr_returns = price_returns + monthly_div_factor
    nav = (1 + tr_returns).cumprod()
    nav.iloc[0] = 1.0  # baseline
    nav = pd.concat([pd.Series([1.0], index=[price.index[0]]), nav]).sort_index()
    nav = nav[~nav.index.duplicated(keep="first")]
    nav.name = "NASDAQ"
    return nav


# -------------------------------------------------------------------- #
# Conversione livelli indice -> NAV cumulato a base 1                  #
# -------------------------------------------------------------------- #

def index_to_nav(level: pd.Series) -> pd.Series:
    """Normalizza la serie (livello indice) a NAV cumulato base 1 al primo
    valore."""
    nav = level / level.iloc[0]
    nav.name = level.name
    return nav


def index_to_monthly_returns(level: pd.Series) -> pd.Series:
    return level.pct_change().dropna()


# -------------------------------------------------------------------- #
# Metriche                                                             #
# -------------------------------------------------------------------- #

def cagr_from_returns(returns: pd.Series) -> float:
    n = len(returns)
    growth = (1 + returns).prod()
    if growth <= 0:
        return float("nan")
    return float(growth ** (12 / n) - 1)


def max_drawdown_from_returns(returns: pd.Series) -> float:
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


def rolling_window_stats(
    returns: pd.Series, window_months: int, step_months: int
) -> list[WindowStats]:
    out = []
    n = len(returns)
    i = 0
    while i + window_months <= n:
        chunk = returns.iloc[i : i + window_months]
        out.append(
            WindowStats(
                start=chunk.index[0],
                end=chunk.index[-1],
                cagr=cagr_from_returns(chunk),
                mdd=max_drawdown_from_returns(chunk),
                vol=volatility_annualized(chunk),
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


def plot_boxplot_cagr(stats_per_segment: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
    labels = list(stats_per_segment.keys())
    data = [stats_per_segment[k]["cagr"] * 100 for k in labels]
    bp = ax.boxplot(
        data,
        tick_labels=labels,
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
    for patch, label in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS.get(label, "#94a3b8"))
        patch.set_alpha(0.85)
        patch.set_edgecolor("#0f172a")
    ax.axhline(0, color="#94a3b8", linewidth=0.8, linestyle="--")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    _style_axes(
        ax,
        title=f"CAGR su finestre rolling {window_label} — confronto segmenti",
        ylabel="CAGR annualizzato (%)",
    )
    ax.text(
        0.99, -0.18,
        "Fonte: MSCI (Gross, USD) + NASDAQ via yfinance. Step 6 mesi. Lordo.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_drawdown_distribution(stats_per_segment: dict, window_label: str, fname: Path):
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
    for label, df in stats_per_segment.items():
        sorted_dd = np.sort(df["mdd"].values * 100)
        cdf = np.arange(1, len(sorted_dd) + 1) / len(sorted_dd)
        ax.plot(sorted_dd, cdf * 100, color=COLORS.get(label, "#94a3b8"),
                linewidth=2.2, label=label)
    ax.legend(frameon=False, fontsize=10, loc="lower right", ncol=2)
    _style_axes(
        ax,
        title=f"Distribuzione del max drawdown — finestre rolling {window_label}",
        ylabel="% di finestre con drawdown ≤ x",
        xlabel="Max drawdown nella finestra (%)",
    )
    ax.text(
        0.99, -0.13,
        "Fonte: MSCI (Gross, USD) + NASDAQ via yfinance.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_equity_curves(navs: dict, fname: Path):
    fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
    for label, nav in navs.items():
        ax.plot(nav.index, nav.values, color=COLORS.get(label, "#94a3b8"),
                linewidth=1.8, label=label)
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=10, loc="upper left", ncol=2)
    _style_axes(
        ax,
        title="Crescita di 1 USD investito a inizio 2001 (scala log)",
        ylabel="NAV cumulato (scala log)",
    )
    ax.text(
        0.99, -0.13,
        "Fonte: MSCI (Gross, USD) + NASDAQ via yfinance. Buy & hold. Lordo.",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_leadership_heatmap(stats_per_segment: dict, window_label: str, fname: Path):
    """
    Per ciascuna finestra rolling, identifica il segmento col CAGR piu' alto
    e visualizza chi vinceva quando come una "striscia" temporale colorata.
    """
    # Estrae le finestre da uno qualunque dei segmenti (tutti hanno stesse date)
    segments = list(stats_per_segment.keys())
    ref = stats_per_segment[segments[0]]
    n_windows = len(ref)

    # Per ogni finestra, calcola CAGR di ciascun segmento e trova il vincitore
    winners = []
    win_dates = []
    for i in range(n_windows):
        cagrs = {seg: stats_per_segment[seg]["cagr"].iloc[i] for seg in segments}
        winner = max(cagrs, key=cagrs.get)
        winners.append(winner)
        win_dates.append(ref["start"].iloc[i])

    # Conteggio per segmento
    counts = pd.Series(winners).value_counts()
    print(f"\nWinner count su finestre {window_label} (rotation of leadership):")
    for seg, n in counts.items():
        share = n / n_windows * 100
        print(f"  {seg:18s}  {n:3d} finestre  ({share:.1f}%)")

    # Plot: striscia orizzontale colorata per data di start finestra
    fig, ax = plt.subplots(figsize=(13, 4), dpi=200)
    seg_to_idx = {seg: i for i, seg in enumerate(segments)}
    for i, (date, winner) in enumerate(zip(win_dates, winners)):
        ax.barh(0, width=180, left=date, height=0.6,
                color=COLORS.get(winner, "#94a3b8"),
                edgecolor="white", linewidth=0.5)
    ax.set_yticks([])
    ax.set_xlim(min(win_dates), max(win_dates) + pd.Timedelta(days=300))
    ax.set_title(
        f"Chi vinceva quando — segmento col CAGR piu' alto in ogni finestra {window_label}",
        fontsize=14, fontweight="semibold", color="#0f172a", pad=14
    )
    ax.tick_params(colors="#475569", labelsize=10)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    # Legenda
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS.get(seg, "#94a3b8"))
               for seg in counts.index]
    labels = [f"{seg} ({counts[seg]})" for seg in counts.index]
    ax.legend(handles, labels, frameon=False, fontsize=10, loc="upper center",
              bbox_to_anchor=(0.5, -0.15), ncol=min(4, len(labels)))
    ax.text(
        0.99, 1.05,
        f"Tot. {n_windows} finestre rolling, step 6 mesi.",
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=10, color="#94a3b8",
    )
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return dict(counts)


# -------------------------------------------------------------------- #
# Main                                                                 #
# -------------------------------------------------------------------- #

def main():
    print("=" * 64)
    print("SmartMoneyLab — Quale segmento del mercato azionario e' il migliore?")
    print("=" * 64)

    # 1. Carica MSCI
    msci_levels = load_all_msci()
    if not msci_levels:
        raise RuntimeError(f"Nessun CSV MSCI trovato in {RAW_DIR}")

    # 2. Carica NASDAQ e ricostruisci TR
    nas_price = load_nasdaq_monthly_tr()
    nas_nav = nasdaq_to_tr_series(nas_price, NASDAQ_DIVIDEND_YIELD_ANNUAL)
    print(f"  [ok]   {'NASDAQ':18s}  {nas_nav.index.min().date()} -> "
          f"{nas_nav.index.max().date()}  ({len(nas_nav)} mesi, TR ricostruito)")

    # 3. Allinea tutto al periodo comune
    all_levels = {}
    for label, level in msci_levels.items():
        all_levels[label] = level
    # Per NASDAQ uso il NAV gia' come "level"
    all_levels["NASDAQ"] = nas_nav

    # Periodo comune: max degli start, min degli end
    start_max = max(s.index.min() for s in all_levels.values())
    end_min = min(s.index.max() for s in all_levels.values())
    start_max = max(start_max, pd.Timestamp(START_DATE))
    end_min = min(end_min, pd.Timestamp(END_DATE))
    print(f"\nPeriodo comune: {start_max.date()} -> {end_min.date()}")

    aligned_returns = {}
    aligned_navs = {}
    for label, level in all_levels.items():
        sl = level.loc[start_max:end_min]
        ret = index_to_monthly_returns(sl)
        nav = (1 + ret).cumprod()
        # Anchor: primo NAV = 1.0
        nav = pd.concat([pd.Series([1.0], index=[ret.index[0] - pd.offsets.MonthBegin()]),
                         nav]).sort_index()
        nav = nav[~nav.index.duplicated(keep="first")]
        aligned_returns[label] = ret
        aligned_navs[label] = nav

    n_months = len(aligned_returns[list(aligned_returns)[0]])
    print(f"Mesi di overlap: {n_months}")

    # 4. Statistiche full-sample
    print(f"\nStatistiche full-sample ({start_max.date()} -> {end_min.date()}):")
    full_summary = {}
    for label, ret in aligned_returns.items():
        c = cagr_from_returns(ret)
        m = max_drawdown_from_returns(ret)
        v = volatility_annualized(ret)
        full_summary[label] = {"cagr": c, "mdd": m, "vol": v}
        print(f"  {label:18s}  CAGR={c*100:6.2f}%  MDD={m*100:7.2f}%  VOL={v*100:5.2f}%")

    # 5. Rolling stats
    rolling_results = {}
    pct_results = {}
    for win_label, win_months in WINDOWS_MONTHS.items():
        rolling_results[win_label] = {}
        pct_results[win_label] = {}
        print(f"\nRolling {win_label} (step {STEP_MONTHS}m):")
        for label, ret in aligned_returns.items():
            stats = rolling_window_stats(ret, win_months, STEP_MONTHS)
            df = pd.DataFrame({
                "start": [s.start for s in stats],
                "end": [s.end for s in stats],
                "cagr": [s.cagr for s in stats],
                "mdd": [s.mdd for s in stats],
                "vol": [s.vol for s in stats],
            })
            rolling_results[win_label][label] = df
            pct_results[win_label][label] = {
                "cagr": percentiles(df["cagr"]),
                "mdd": percentiles(df["mdd"]),
                "n_windows": int(len(df)),
                "share_negative_cagr": float((df["cagr"] < 0).mean()),
            }
            p = pct_results[win_label][label]["cagr"]
            print(f"  {label:18s}: p5={p['p5']*100:6.2f}%  p50={p['p50']*100:6.2f}%  "
                  f"p95={p['p95']*100:6.2f}%  ({pct_results[win_label][label]['n_windows']} fin)")

    # 6. Grafici
    print("\nGenerazione grafici…")
    plot_boxplot_cagr(rolling_results["5y"], "5 anni",
                      OUT_DIR / "01_boxplot_cagr_5y.png")
    plot_boxplot_cagr(rolling_results["10y"], "10 anni",
                      OUT_DIR / "02_boxplot_cagr_10y.png")
    plot_equity_curves(aligned_navs, OUT_DIR / "03_equity_curves.png")
    plot_drawdown_distribution(rolling_results["10y"], "10 anni",
                               OUT_DIR / "04_drawdown_distribution_10y.png")
    leadership_counts_10y = plot_leadership_heatmap(
        rolling_results["10y"], "10 anni",
        OUT_DIR / "05_leadership_rotation_10y.png"
    )
    leadership_counts_5y = plot_leadership_heatmap(
        rolling_results["5y"], "5 anni",
        OUT_DIR / "06_leadership_rotation_5y.png"
    )

    # 7. Salva summary
    summary = {
        "slug": SLUG,
        "period": {
            "start": str(start_max.date()),
            "end": str(end_min.date()),
            "n_months": int(n_months),
        },
        "params": {
            "rolling_step_months": STEP_MONTHS,
            "windows_months": WINDOWS_MONTHS,
            "msci_index_level": "Gross",
            "msci_currency": "USD",
            "nasdaq_source": "yfinance ^IXIC (price-only) + dividend yield "
                             f"{NASDAQ_DIVIDEND_YIELD_ANNUAL*100:.2f}%/anno per TR ricostruito",
        },
        "segments": list(aligned_returns.keys()),
        "full_sample": full_summary,
        "rolling_percentiles": pct_results,
        "leadership_counts": {
            "10y": leadership_counts_10y,
            "5y": leadership_counts_5y,
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    # CSV con i NAV aligned (utile per audit)
    csv_df = pd.DataFrame(aligned_navs)
    csv_df.index.name = "date"
    csv_df.to_csv(OUT_DIR / "data.csv", float_format="%.6f")

    print(f"\nOutput salvati in: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()


# ====================================================================
# NOTE OPERATIVE
# ====================================================================
#
# I CSV MSCI vanno scaricati manualmente da
#   https://www.msci.com/end-of-day-data-search
# con: Currency=USD, Index Level=Gross, Size=Standard (eccetto Small Cap).
#
# Salva i file in data/raw/ con i nomi:
#   msci_world.csv
#   msci_usa.csv
#   msci_europe.csv
#   msci_japan.csv
#   msci_em.csv
#   msci_em_asia.csv
#   msci_world_smallcap.csv
#
# NASDAQ Composite viene scaricato automaticamente via yfinance (^IXIC).
# Se yfinance non e' installato: pip install yfinance
# ====================================================================
# end of file
