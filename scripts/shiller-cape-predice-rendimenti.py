"""
SmartMoneyLab - Lo Shiller CAPE predice i rendimenti del mercato? (1881-2026)
==============================================================================

Domanda: il livello dello Shiller CAPE (Cyclically Adjusted P/E) predice i
rendimenti forward dell'S&P 500 a 5 e 10 anni?

A differenza degli articoli su tassi Fed e petrolio (dove la correlazione con
i rendimenti era ~zero), qui ci aspettiamo un segnale forte: il CAPE alto
dovrebbe predire rendimenti reali bassi nei 10 anni successivi. Lo testiamo.

METODO
------
- CAPE: PE10 Shiller (1881-2023) esteso con serie multpl (2024-2026).
  Le due serie coincidono nell'overlap.
- Rendimenti: total return S&P 500 ricostruito dal dataset Shiller
  (prezzo + dividendo mensile prorata). Dividendo esteso post-2023-06 al
  div yield 1.8%/anno. Due versioni:
    * NOMINALE: TR grezzo.
    * REALE: TR deflazionato per CPI Shiller (esteso post-2023-09 al 2.5%/y).
- Forward: rendimento annualizzato (CAGR) a 5 e 10 anni da ogni mese.
- 6 bucket CAPE: <15, 15-20, 20-25, 25-30, 30-40, >40.
- Scatter CAPE vs forward 10y (reale e nominale) con OLS + R^2.
- Curve equity 'bucketed' per il reel (portafoglio investe solo quando il
  CAPE sta nella sua fascia). Sia reale che nominale.

DATI (locali)
  data/cache/shiller_mirror.csv    - SP500 price + Dividend + CPI + PE10
  data/raw/Shiller_PE_montly.csv   - CAPE multpl (formato IT/EN misto)

OUTPUT in public/charts/shiller-cape-predice-rendimenti/
  01_context_cape_timeline.png     CAPE nel tempo con bande fasce
  02_scatter_cape_vs_fwd10y_real.png   scatter classico + OLS + R^2 (reale)
  03_scatter_cape_vs_fwd10y_nom.png    scatter nominale
  04_scatter_cape_vs_fwd5y_real.png    scatter 5y reale
  05_forward_by_bucket_real.png    barre forward 5y/10y reale per bucket
  06_forward_by_bucket_nom.png     barre forward 5y/10y nominale per bucket
  07_hitrate_negative_real.png     % periodi con rendimento reale 10y negativo per bucket
  08_equity_bucketed_real.png      preview curve bucketed reale

  summary.json, monthly_panel.csv, regime_stats_long.csv,
  equity_curves_bucketed_real.csv, equity_curves_bucketed_nom.csv,
  lookup_cape.json (per componente interattivo)

Uso: python scripts/shiller-cape-predice-rendimenti.py

Autore: SmartMoneyLab - 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SLUG = "shiller-cape-predice-rendimenti"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "public" / "charts" / SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOOKUP_DIR = REPO_ROOT / "public" / "tools"
LOOKUP_DIR.mkdir(parents=True, exist_ok=True)

DIV_YIELD_EXTRAP = 0.018   # dividendo annuo per estendere post-2023-06
CPI_EXTRAP_ANNUAL = 0.025  # inflazione target per estendere CPI post-2023-09

FWD_YEARS = [5, 10, 20]

LEVEL_BINS = [0, 15, 20, 25, 30, 40, 200]
LEVEL_LABELS = ["<15 (economico)", "15-20 (equo-basso)", "20-25 (equo-alto)",
                "25-30 (caro)", "30-40 (molto caro)", ">40 (carissimo)"]
# chiavi "safe" per colonne CSV/JSON
LEVEL_KEYS = ["lt15", "15_20", "20_25", "25_30", "30_40", "gt40"]

# Palette per bucket (economico=verde ... carissimo=rosso mattone)
BUCKET_COLORS = {
    "<15 (economico)":    "#059669",
    "15-20 (equo-basso)": "#0891b2",
    "20-25 (equo-alto)":  "#1e3a8a",
    "25-30 (caro)":       "#d97706",
    "30-40 (molto caro)": "#c2410c",
    ">40 (carissimo)":    "#dc2626",
}
COLOR_REAL = "#1e3a8a"
COLOR_NOM = "#d97706"


# --------------------------------------------------------------------- #
# Loading                                                               #
# --------------------------------------------------------------------- #
MESI_IT = {"gen": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr",
           "mag": "May", "giu": "Jun", "lug": "Jul", "ago": "Aug",
           "set": "Sep", "ott": "Oct", "nov": "Nov", "dic": "Dec"}


def _parse_multpl_date(s: str):
    s = s.strip()
    low = s.lower()
    for it, en in MESI_IT.items():
        if low.startswith(it):
            s = en + s[len(it):]
            break
    return pd.to_datetime(s, format="%b %d, %Y", errors="coerce")


def load_cape() -> pd.Series:
    """CAPE mensile: PE10 Shiller (1881-2023) esteso con multpl (2024+)."""
    s = pd.read_csv(CACHE_DIR / "shiller_mirror.csv", parse_dates=["Date"])
    s["Date"] = s["Date"] + pd.offsets.MonthEnd(0)
    pe10 = s.set_index("Date")["PE10"].replace(0, np.nan).dropna()

    m = pd.read_csv(RAW_DIR / "Shiller_PE_montly.csv")
    m["date"] = m["Date"].apply(_parse_multpl_date)
    m["cape"] = m["Value"].astype(str).str.replace(",", ".").astype(float)
    m = m.dropna(subset=["date", "cape"])
    m["date"] = m["date"] + pd.offsets.MonthEnd(0)
    multpl = m.set_index("date")["cape"].sort_index()
    multpl = multpl[~multpl.index.duplicated(keep="last")]

    # Splice: PE10 fino alla sua ultima data, poi multpl
    last_pe10 = pe10.index.max()
    ext = multpl[multpl.index > last_pe10]
    cape = pd.concat([pe10, ext]).sort_index()
    cape = cape[~cape.index.duplicated(keep="last")]
    cape.name = "cape"
    print(f"[cape] {cape.index[0].date()} -> {cape.index[-1].date()}, n={len(cape)} "
          f"(PE10 fino {last_pe10.date()}, multpl esteso {ext.index.min().date() if len(ext) else '-'} -> {ext.index.max().date() if len(ext) else '-'})")
    return cape


def load_tr_nominal_real() -> tuple[pd.Series, pd.Series]:
    """TR nominale e reale mensili da shiller_mirror."""
    s = pd.read_csv(CACHE_DIR / "shiller_mirror.csv", parse_dates=["Date"])
    s = s.rename(columns={"Date": "date", "SP500": "price",
                          "Dividend": "dividend",
                          "Consumer Price Index": "cpi"})
    s["date"] = s["date"] + pd.offsets.MonthEnd(0)
    s = s.set_index("date").sort_index()

    # Estendi dividendo (post-2023-06) con yield costante
    div_missing = s["dividend"] == 0
    s.loc[div_missing, "dividend"] = s.loc[div_missing, "price"] * DIV_YIELD_EXTRAP

    # TR nominale: r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1
    prev_price = s["price"].shift(1)
    prev_div_mo = s["dividend"].shift(1) / 12
    tr_nom = ((s["price"] + prev_div_mo) / prev_price - 1).dropna()
    tr_nom.name = "tr_nom"

    # CPI: estendi post-ultimo-valido al 2.5%/y
    cpi = s["cpi"].replace(0, np.nan)
    last_cpi = cpi.last_valid_index()
    mrate = (1 + CPI_EXTRAP_ANNUAL) ** (1 / 12) - 1
    miss = cpi.index > last_cpi
    if miss.any():
        n = np.arange(1, miss.sum() + 1)
        cpi.loc[miss] = cpi.loc[last_cpi] * (1 + mrate) ** n
    cpi = cpi.dropna()

    # TR reale: deflaziona il TR nominale per l'inflazione mensile
    cpi_ret = cpi.pct_change().reindex(tr_nom.index)
    tr_real = ((1 + tr_nom) / (1 + cpi_ret) - 1).dropna()
    tr_real.name = "tr_real"
    print(f"[tr] nominale {tr_nom.index[0].date()} -> {tr_nom.index[-1].date()}; "
          f"CPI esteso oltre {last_cpi.date()} al {CPI_EXTRAP_ANNUAL*100:.1f}%/y")
    return tr_nom, tr_real


def build_panel() -> pd.DataFrame:
    cape = load_cape()
    tr_nom, tr_real = load_tr_nominal_real()
    panel = pd.concat([cape, tr_nom, tr_real], axis=1).sort_index()

    # Forward annualizzato (CAGR) da ogni mese
    for label, col in [("nom", "tr_nom"), ("real", "tr_real")]:
        for h in FWD_YEARS:
            months = h * 12
            growth = (1 + panel[col]).rolling(months).apply(np.prod, raw=True).shift(-months)
            panel[f"fwd{h}y_{label}"] = growth ** (1 / h) - 1

    panel = panel[panel["cape"].notna() & panel["tr_nom"].notna()]
    return panel


def classify(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["bucket"] = pd.cut(p["cape"], bins=LEVEL_BINS, labels=LEVEL_LABELS,
                          include_lowest=True)
    return p


# --------------------------------------------------------------------- #
# Stats                                                                 #
# --------------------------------------------------------------------- #
def fwd_stats(x: pd.Series) -> dict:
    r = x.dropna()
    if len(r) < 3:
        return {"n": len(r), "median": np.nan, "mean": np.nan,
                "p5": np.nan, "p95": np.nan, "hit_pos": np.nan}
    return {
        "n": int(len(r)),
        "median": float(r.median()),
        "mean": float(r.mean()),
        "p5": float(r.quantile(0.05)),
        "p95": float(r.quantile(0.95)),
        "hit_pos": float((r > 0).mean()),
    }


def build_bucket_stats(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for lab in LEVEL_LABELS:
        mask = p["bucket"] == lab
        entry = {"bucket": lab, "n_bucket": int(mask.sum()),
                 "cape_min": float(p.loc[mask, "cape"].min()) if mask.any() else np.nan,
                 "cape_max": float(p.loc[mask, "cape"].max()) if mask.any() else np.nan}
        for h in FWD_YEARS:
            for label in ["real", "nom"]:
                st = fwd_stats(p.loc[mask, f"fwd{h}y_{label}"])
                for k, v in st.items():
                    entry[f"fwd{h}y_{label}_{k}"] = v
        rows.append(entry)
    return pd.DataFrame(rows)


def ols_r2(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """ritorna slope, intercept, r, r2."""
    m, b = np.polyfit(x, y, 1)
    yhat = m * x + b
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    r = np.corrcoef(x, y)[0, 1]
    return float(m), float(b), float(r), float(r2)


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


def plot_cape_timeline(p: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(p.index, p["cape"].values, color="#1e3a8a", lw=1.4)
    for edge in [15, 20, 25, 30, 40]:
        ax.axhline(edge, color="#94a3b8", lw=0.7, linestyle="--", alpha=0.7)
    ax.axhline(p["cape"].mean(), color="#dc2626", lw=1.0, linestyle=":",
               label=f"media storica {p['cape'].mean():.1f}")
    ax.set_ylabel("Shiller CAPE (PE10)")
    ax.set_title(f"Shiller CAPE dell'S&P 500, {p.index[0].date()} -> {p.index[-1].date()}")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_scatter(p: pd.DataFrame, ycol: str, ylabel: str, title: str, out: Path,
                  color: str):
    d = p[["cape", ycol]].dropna()
    x = d["cape"].values; y = d[ycol].values * 100
    m, b, r, r2 = ols_r2(x, y)
    fig, ax = plt.subplots(figsize=(10, 6.5))
    sc = ax.scatter(x, y, c=d.index.year, cmap="viridis", alpha=0.5, s=14)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, m * xs + b, color=color, lw=2.4, linestyle="--",
            label=f"OLS: {m:.2f}%/punto CAPE\nr={r:.2f}, R²={r2:.2f}")
    ax.axhline(0, color="black", lw=0.6)
    cbar = fig.colorbar(sc, ax=ax); cbar.set_label("anno")
    ax.set_xlabel("Shiller CAPE al momento dell'investimento")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
    return {"slope": m, "intercept": b, "r": r, "r2": r2, "n": int(len(d))}


def plot_forward_by_bucket(stats: pd.DataFrame, label: str, title: str, out: Path):
    x = np.arange(len(LEVEL_LABELS))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 6))
    f5 = [stats[stats.bucket == b][f"fwd5y_{label}_median"].iloc[0] * 100 for b in LEVEL_LABELS]
    f10 = [stats[stats.bucket == b][f"fwd10y_{label}_median"].iloc[0] * 100 for b in LEVEL_LABELS]
    ax.bar(x - w/2, f5, width=w, color="#94a3b8", label="forward 5 anni")
    ax.bar(x + w/2, f10, width=w, color=COLOR_REAL if label == "real" else COLOR_NOM,
           label="forward 10 anni")
    for xi, v in zip(x, f5): ax.text(xi - w/2, v + (0.3 if v>=0 else -0.6), f"{v:.1f}", ha="center", fontsize=8)
    for xi, v in zip(x, f10): ax.text(xi + w/2, v + (0.3 if v>=0 else -0.6), f"{v:.1f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(LEVEL_LABELS, fontsize=9, rotation=12)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel(f"CAGR mediano {label} (%)")
    ax.set_title(title)
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_hitrate_negative(p: pd.DataFrame, out: Path):
    x = np.arange(len(LEVEL_LABELS))
    fig, ax = plt.subplots(figsize=(11, 6))
    vals = []
    for lab in LEVEL_LABELS:
        r = p.loc[p["bucket"] == lab, "fwd10y_real"].dropna()
        vals.append(float((r < 0).mean() * 100) if len(r) else 0.0)
    colors = [BUCKET_COLORS[b] for b in LEVEL_LABELS]
    ax.bar(x, vals, color=colors)
    for xi, v in zip(x, vals): ax.text(xi, v + 1, f"{v:.0f}%", ha="center", fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(LEVEL_LABELS, fontsize=9, rotation=12)
    ax.set_ylabel("% periodi con rendimento reale 10y NEGATIVO")
    ax.set_title("Rischio di rendimento reale negativo a 10 anni, per fascia CAPE")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_equity_bucketed(curves: pd.DataFrame, title: str, out: Path):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for col in curves.columns:
        lab = COL_TO_LABEL.get(col, col)
        ax.plot(curves.index, (curves[col].values - 1) * 100,
                color=BUCKET_COLORS.get(lab, "#333"), lw=1.8, label=lab)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("Variazione % (investe solo nella fascia)")
    ax.set_title(title)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


COL_TO_LABEL = dict(zip([f"bucket_{k}" for k in LEVEL_KEYS], LEVEL_LABELS))
LABEL_TO_COL = dict(zip(LEVEL_LABELS, [f"bucket_{k}" for k in LEVEL_KEYS]))


def build_bucketed_curves(p: pd.DataFrame, retcol: str) -> pd.DataFrame:
    """Portafoglio investe (nel TR retcol) solo nei mesi del suo bucket."""
    cols = {f"bucket_{k}": [] for k in LEVEL_KEYS}
    running = {f"bucket_{k}": 1.0 for k in LEVEL_KEYS}
    idx = []
    for date, row in p.iterrows():
        lab = row["bucket"]
        ret = row[retcol]
        target = LABEL_TO_COL.get(lab)
        if target is not None and pd.notna(ret):
            running[target] *= (1 + ret)
        idx.append(date)
        for c in cols:
            cols[c].append(running[c])
    return pd.DataFrame(cols, index=idx)


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #
def main():
    _style()
    panel = build_panel()
    p = classify(panel)
    print(f"[panel] {p.index[0].date()} -> {p.index[-1].date()}, {len(p)} mesi")
    print(f"[cape] attuale {p['cape'].iloc[-1]:.1f}, media {p['cape'].mean():.1f}, mediana {p['cape'].median():.1f}")

    stats = build_bucket_stats(p)
    print("\n[bucket] n per fascia:")
    for lab in LEVEL_LABELS:
        n = int((p["bucket"] == lab).sum())
        r10 = p.loc[p["bucket"] == lab, "fwd10y_real"].dropna()
        med = r10.median() * 100 if len(r10) else float("nan")
        print(f"    {lab:<22} {n:>4} mesi | fwd10y reale mediano {med:>+6.1f}%")

    print("\n[plot]")
    plot_cape_timeline(p, OUT_DIR / "01_context_cape_timeline.png")
    reg_10r = plot_scatter(p, "fwd10y_real", "Rendimento reale annualizzato 10y (%)",
        "CAPE vs rendimento REALE forward 10 anni", OUT_DIR / "02_scatter_cape_vs_fwd10y_real.png", COLOR_REAL)
    reg_10n = plot_scatter(p, "fwd10y_nom", "Rendimento nominale annualizzato 10y (%)",
        "CAPE vs rendimento NOMINALE forward 10 anni", OUT_DIR / "03_scatter_cape_vs_fwd10y_nom.png", COLOR_NOM)
    reg_5r = plot_scatter(p, "fwd5y_real", "Rendimento reale annualizzato 5y (%)",
        "CAPE vs rendimento REALE forward 5 anni", OUT_DIR / "04_scatter_cape_vs_fwd5y_real.png", COLOR_REAL)
    reg_20r = plot_scatter(p, "fwd20y_real", "Rendimento reale annualizzato 20y (%)",
        "CAPE vs rendimento REALE forward 20 anni", OUT_DIR / "09_scatter_cape_vs_fwd20y_real.png", COLOR_REAL)
    plot_forward_by_bucket(stats, "real", "Rendimento REALE annualizzato per fascia CAPE",
        OUT_DIR / "05_forward_by_bucket_real.png")
    plot_forward_by_bucket(stats, "nom", "Rendimento NOMINALE annualizzato per fascia CAPE",
        OUT_DIR / "06_forward_by_bucket_nom.png")
    plot_hitrate_negative(p, OUT_DIR / "07_hitrate_negative_real.png")

    curves_real = build_bucketed_curves(p, "tr_real")
    curves_nom = build_bucketed_curves(p, "tr_nom")
    plot_equity_bucketed(curves_real, "Investire nell'S&P 500 solo per fascia CAPE (reale)",
        OUT_DIR / "08_equity_bucketed_real.png")

    print("\n[csv/json]")
    p.to_csv(OUT_DIR / "monthly_panel.csv", index_label="date")
    stats.to_csv(OUT_DIR / "regime_stats_long.csv", index=False)
    curves_real.to_csv(OUT_DIR / "equity_curves_bucketed_real.csv", index_label="date")
    curves_nom.to_csv(OUT_DIR / "equity_curves_bucketed_nom.csv", index_label="date")

    def _corr(a, b_):
        d = pd.concat([a, b_], axis=1).dropna()
        return float(d.iloc[:, 0].corr(d.iloc[:, 1])) if len(d) >= 5 else float("nan")

    correlations = {}
    for h in FWD_YEARS:
        for label in ["real", "nom"]:
            correlations[f"cape_vs_fwd{h}y_{label}"] = _corr(p["cape"], p[f"fwd{h}y_{label}"])

    # Lookup per componente interattivo
    def bucket_lookup():
        out = {}
        for lab, key in zip(LEVEL_LABELS, LEVEL_KEYS):
            row = stats[stats.bucket == lab].iloc[0]
            out[key] = {
                "label": lab,
                "n": int(row["n_bucket"]),
                "cape_min": row["cape_min"], "cape_max": row["cape_max"],
                "fwd5y_real_median": row["fwd5y_real_median"],
                "fwd5y_real_p5": row["fwd5y_real_p5"], "fwd5y_real_p95": row["fwd5y_real_p95"],
                "fwd10y_real_median": row["fwd10y_real_median"],
                "fwd10y_real_p5": row["fwd10y_real_p5"], "fwd10y_real_p95": row["fwd10y_real_p95"],
                "fwd10y_real_hit_pos": row["fwd10y_real_hit_pos"],
                "fwd20y_real_median": row["fwd20y_real_median"],
                "fwd20y_real_p5": row["fwd20y_real_p5"], "fwd20y_real_p95": row["fwd20y_real_p95"],
                "fwd20y_real_hit_pos": row["fwd20y_real_hit_pos"],
                "fwd20y_nom_median": row["fwd20y_nom_median"],
                "fwd5y_nom_median": row["fwd5y_nom_median"],
                "fwd5y_nom_p5": row["fwd5y_nom_p5"], "fwd5y_nom_p95": row["fwd5y_nom_p95"],
                "fwd10y_nom_median": row["fwd10y_nom_median"],
                "fwd10y_nom_p5": row["fwd10y_nom_p5"], "fwd10y_nom_p95": row["fwd10y_nom_p95"],
            }
        return out

    lookup = {
        "meta": {
            "source_article": "/posts/shiller-cape-predice-rendimenti",
            "panel_start": str(p.index[0].date()),
            "panel_end": str(p.index[-1].date()),
            "panel_months": int(len(p)),
            "cape_current": float(p["cape"].iloc[-1]),
            "cape_mean": float(p["cape"].mean()),
            "level_bins": LEVEL_BINS,
            "level_labels": LEVEL_LABELS,
            "level_keys": LEVEL_KEYS,
            "correlations": correlations,
            "regressions": {"fwd10y_real": reg_10r, "fwd10y_nom": reg_10n, "fwd5y_real": reg_5r, "fwd20y_real": reg_20r},
        },
        "buckets": bucket_lookup(),
    }
    with open(LOOKUP_DIR / "cape-lookup.json", "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2, ensure_ascii=False, default=float)

    summary = {
        "slug": SLUG,
        "parametri": {
            "start": str(p.index[0].date()), "end": str(p.index[-1].date()),
            "months": int(len(p)), "level_labels": LEVEL_LABELS,
            "div_yield_extrap": DIV_YIELD_EXTRAP, "cpi_extrap_annual": CPI_EXTRAP_ANNUAL,
            "cape_current": float(p["cape"].iloc[-1]),
        },
        "correlations": correlations,
        "regressions": {"fwd10y_real": reg_10r, "fwd10y_nom": reg_10n, "fwd5y_real": reg_5r, "fwd20y_real": reg_20r},
        "bucket_stats": stats.to_dict(orient="records"),
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)

    print(f"\n[done] Output in {OUT_DIR}")
    print(f"    corr CAPE vs fwd10y reale: {correlations['cape_vs_fwd10y_real']:.3f}  (R²={reg_10r['r2']:.2f})")
    print(f"    corr CAPE vs fwd10y nom:   {correlations['cape_vs_fwd10y_nom']:.3f}  (R²={reg_10n['r2']:.2f})")


if __name__ == "__main__":
    main()
