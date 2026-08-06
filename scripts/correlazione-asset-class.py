"""
SmartMoneyLab - Studio sulle correlazioni tra asset class (USD, mensile)
=========================================================================

Universo (31 asset, prezzi mensili USD in data/cache/correlation_universe_monthly.csv):
  - Beni rifugio / materie prime: Bitcoin, Oro, Argento, Rame, Petrolio, Treasury 20+
  - Settoriali (10): Nasdaq, Energy, Healthcare, Financials, Value, Staples,
                     Small Cap, REIT, Difesa, Semiconduttori
  - Geografici (10): USA, MSCI World, ACWI, Emergenti, Europa, Germania, UK,
                     Cina, Giappone, America Latina
  - Bonus (5): Corea, Australia, India, Canada, Taiwan

MSCI World: sostituito con la serie MSCI World Gross USD (data/raw/msci_world.csv,
dal 2000) perche' l'ETF URTH parte solo dal 2012. ACWI ETF (2008) e' escluso
dalla matrice principale (quasi identico a World; gli Emergenti sono gia'
separati) ma resta nella matrice pairwise a storia piena.

MATRICI PRODOTTE
  1. PRINCIPALE - finestra comune ~2006-2026 (>=20 anni), senza Bitcoin/India/ACWI.
     E' il cuore dello studio.
  2. PAIRWISE   - tutti i 31 asset, ogni coppia sulla sua storia comune massima.
     Per la heatmap interattiva e per parlare di India.
  3. SECONDARIA (tips) - con Bitcoin, finestra ~2014-2026.

Inoltre:
  - correlazione media azionario-vs-azionario e azionario-vs-rifugi
  - coppie piu'/meno correlate
  - correlazione azionaria nei crolli (2008, 2020, 2022) vs periodo calmo
  - portafoglio a 5 asset a MINIMA correlazione (brute force), backtest vs SPY
    2006-2026, rolling 10y, metriche.

OUTPUT in public/charts/correlazione-asset-class/
  01_heatmap_principale.png
  02_heatmap_pairwise_full.png
  03_corr_azionario_nel_tempo.png       (corr media azionaria rolling 12m)
  04_diversificatori_ranking.png        (corr media di ogni asset vs blocco azionario)
  05_portafoglio_mincorr_vs_mercato.png (equity curve)
  06_scatter_corr_vs_crisi.png          (corr calma vs crisi)
  summary.json, corr_matrix_principale.csv, corr_matrix_pairwise.csv,
  corr_lookup.json (per componente interattivo),
  equity_mincorr_vs_market.csv (per reel)

Uso: python scripts/correlazione-asset-class.py
Autore: SmartMoneyLab - 2026.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SLUG = "correlazione-asset-class"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CACHE = ROOT / "data" / "cache"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "public" / "charts" / SLUG
OUT.mkdir(parents=True, exist_ok=True)
LOOKUP_DIR = ROOT / "public" / "tools"
LOOKUP_DIR.mkdir(parents=True, exist_ok=True)

# categorie per raggruppare nella heatmap e nell'analisi
CATEGORY = {
    "Bitcoin": "rifugio", "Oro": "rifugio", "Argento": "rifugio",
    "Rame": "rifugio", "Petrolio (WTI)": "rifugio", "Treasury USA 20+": "rifugio",
    "Nasdaq 100": "settore", "Energy": "settore", "Healthcare": "settore",
    "Financials": "settore", "Value (S&P500)": "settore", "Consumer Staples": "settore",
    "Small Cap (Russell 2000)": "settore", "Real Estate (REIT)": "settore",
    "Difesa & Aerospazio": "settore", "Semiconduttori": "settore",
    "USA (S&P 500)": "geo", "MSCI World": "geo", "ACWI (ETF)": "geo",
    "Mercati Emergenti": "geo", "Europa": "geo", "Germania": "geo",
    "Regno Unito": "geo", "Cina": "geo", "Giappone": "geo", "America Latina": "geo",
    "Corea del Sud": "bonus", "Australia": "bonus", "India": "bonus",
    "Canada": "bonus", "Taiwan": "bonus",
}
# blocco "azionario" = settore + geo + bonus (tutto tranne i rifugi non-azionari)
EQUITY_LIKE = [a for a, c in CATEGORY.items()
               if c in ("settore", "geo", "bonus") and a != "Bitcoin"]
NON_EQUITY = ["Oro", "Argento", "Rame", "Petrolio (WTI)", "Treasury USA 20+"]

MAIN_START = "2006-06-30"   # dopo l'inizio di Difesa (ITA, 2006-05)
EXCLUDE_MAIN = ["Bitcoin", "India", "ACWI (ETF)", "MSCI World (ETF)"]
CRISES = {
    "GFC 2008": ("2007-10-31", "2009-03-31"),
    "COVID 2020": ("2020-01-31", "2020-04-30"),
    "Orso 2022": ("2022-01-31", "2022-10-31"),
}
RF = 0.02


# --------------------------------------------------------------------- #
def load_prices() -> pd.DataFrame:
    df = pd.read_csv(CACHE / "correlation_universe_monthly.csv",
                     parse_dates=["date"]).set_index("date").sort_index()
    # sostituisci MSCI World con la serie gross USD lunga
    if (RAW / "msci_world.csv").exists():
        m = pd.read_csv(RAW / "msci_world.csv", skiprows=6)
        m.columns = ["date", "val"]
        m["date"] = pd.to_datetime(m["date"], format="%b %d, %Y", errors="coerce")
        m["val"] = m["val"].astype(str).str.replace(",", "").astype(float)
        m = m.dropna().set_index("date").sort_index()
        m.index = m.index + pd.offsets.MonthEnd(0)
        df = df.drop(columns=["MSCI World (ETF)"], errors="ignore")
        df["MSCI World"] = m["val"].reindex(df.index).ffill(limit=1)
        df.loc[df.index < m.index.min(), "MSCI World"] = np.nan
    return df


def monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change()


# --------------------------------------------------------------------- #
# Heatmap                                                               #
# --------------------------------------------------------------------- #
def order_by_category(assets: list[str]) -> list[str]:
    order = {"geo": 0, "settore": 1, "bonus": 2, "rifugio": 3}
    return sorted(assets, key=lambda a: (order.get(CATEGORY.get(a, "geo"), 9), a))


def plot_heatmap(corr: pd.DataFrame, title: str, out: Path):
    assets = order_by_category(list(corr.columns))
    c = corr.loc[assets, assets]
    n = len(assets)
    fig, ax = plt.subplots(figsize=(max(9, n * 0.42), max(8, n * 0.42)))
    im = ax.imshow(c.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(assets, rotation=90, fontsize=7)
    ax.set_yticklabels(assets, fontsize=7)
    # annota i valori se la matrice non e' enorme
    if n <= 30:
        for i in range(n):
            for j in range(n):
                v = c.values[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                            fontsize=5.5,
                            color="white" if abs(v) > 0.6 else "black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("correlazione")
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=170); plt.close(fig)


def plot_diversifier_ranking(rets: pd.DataFrame, equity_block: list[str], out: Path):
    """Per ogni asset: correlazione media con il blocco azionario."""
    avg = {}
    for a in rets.columns:
        others = [e for e in equity_block if e != a and e in rets.columns]
        pair = rets[[a] + others].dropna()
        if len(pair) < 24:
            continue
        cors = [pair[a].corr(pair[e]) for e in others]
        avg[a] = np.nanmean(cors)
    s = pd.Series(avg).sort_values()
    colors = ["#059669" if v < 0.3 else ("#d97706" if v < 0.6 else "#dc2626")
              for v in s.values]
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(range(len(s)), s.values, color=colors)
    ax.set_yticks(range(len(s))); ax.set_yticklabels(s.index, fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Correlazione media con il blocco azionario globale")
    ax.set_title("Chi diversifica davvero? (piu' a sinistra = piu' scorrelato)",
                 fontweight="bold")
    for i, v in enumerate(s.values):
        ax.text(v + (0.01 if v >= 0 else -0.01), i, f"{v:.2f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=7)
    fig.tight_layout(); fig.savefig(out, dpi=170); plt.close(fig)
    return s


def plot_rolling_equity_corr(rets: pd.DataFrame, equity_block: list[str], out: Path):
    """Correlazione media pairwise del blocco azionario, rolling 12m."""
    block = rets[[e for e in equity_block if e in rets.columns]]
    dates, vals = [], []
    idx = block.index
    for i in range(12, len(block)):
        w = block.iloc[i - 12:i].dropna(axis=1, how="any")
        if w.shape[1] < 4:
            continue
        c = w.corr().values
        iu = np.triu_indices_from(c, k=1)
        dates.append(idx[i]); vals.append(np.nanmean(c[iu]))
    s = pd.Series(vals, index=dates)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(s.index, s.values, color="#1e3a8a", lw=1.4)
    ax.axhline(s.mean(), color="#dc2626", lw=1.0, linestyle=":",
               label=f"media {s.mean():.2f}")
    for name, (a, b) in CRISES.items():
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color="#fca5a5", alpha=0.25)
    ax.set_ylabel("Correlazione media azionaria (rolling 12m)")
    ax.set_title("La correlazione azionaria globale si impenna nei crolli",
                 fontweight="bold")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=170); plt.close(fig)
    return s


# --------------------------------------------------------------------- #
# Portafoglio min-correlazione                                          #
# --------------------------------------------------------------------- #
def min_corr_portfolio(corr: pd.DataFrame, k: int = 5) -> tuple[list[str], float]:
    """Brute force: sottoinsieme di k asset con minima correlazione media pairwise."""
    assets = list(corr.columns)
    best, best_avg = None, np.inf
    for combo in combinations(assets, k):
        sub = corr.loc[list(combo), list(combo)].values
        iu = np.triu_indices_from(sub, k=1)
        avg = np.nanmean(sub[iu])
        if avg < best_avg:
            best_avg, best = avg, combo
    return list(best), float(best_avg)


def backtest_buyhold(rets: pd.DataFrame, assets: list[str]) -> pd.Series:
    """Equal weight buy&hold (pesi driftano), NAV mensile base 1."""
    r = rets[assets].dropna()
    w0 = np.repeat(1 / len(assets), len(assets))
    navs = (1 + r).cumprod()
    port = (navs * w0).sum(axis=1)
    return port / port.iloc[0]


def metrics(nav: pd.Series) -> dict:
    r = nav.pct_change().dropna()
    n_years = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / n_years) - 1
    vol = r.std() * np.sqrt(12)
    dd = (nav / nav.cummax() - 1).min()
    sharpe = (cagr - RF) / vol if vol > 0 else np.nan
    downside = r[r < 0].std() * np.sqrt(12)
    sortino = (cagr - RF) / downside if downside > 0 else np.nan
    calmar = cagr / abs(dd) if dd != 0 else np.nan
    return {"cagr": float(cagr), "vol": float(vol), "mdd": float(dd),
            "sharpe": float(sharpe), "sortino": float(sortino),
            "calmar": float(calmar), "multiplo": float(nav.iloc[-1])}


def rolling_winrate(port: pd.Series, market: pd.Series, years: int = 10) -> dict:
    m = years * 12
    both = pd.concat([port.rename("p"), market.rename("m")], axis=1).dropna()
    wins = tot = 0
    for i in range(len(both) - m):
        pr = both["p"].iloc[i + m] / both["p"].iloc[i] - 1
        mr = both["m"].iloc[i + m] / both["m"].iloc[i] - 1
        tot += 1
        if pr > mr:
            wins += 1
    return {"n": tot, "win_rate": wins / tot if tot else float("nan")}


# --------------------------------------------------------------------- #
def main():
    prices = load_prices()
    rets = monthly_returns(prices)
    print(f"[dati] {prices.shape[1]} asset, {prices.index[0].date()} -> {prices.index[-1].date()}")

    # ---- Matrice principale (finestra comune ~2006-2026) ----
    main_assets = [a for a in prices.columns if a not in EXCLUDE_MAIN]
    main_rets = rets.loc[MAIN_START:, main_assets].dropna(axis=0, how="any")
    # tieni solo asset con storia piena sulla finestra
    keep = [a for a in main_assets if rets.loc[MAIN_START:, a].notna().all()]
    main_rets = rets.loc[MAIN_START:, keep].dropna()
    corr_main = main_rets.corr()
    print(f"[principale] {len(keep)} asset, {main_rets.index[0].date()} -> {main_rets.index[-1].date()} ({len(main_rets)} mesi)")
    plot_heatmap(corr_main, f"Correlazioni tra asset class - finestra comune {main_rets.index[0].date()} / {main_rets.index[-1].date()}",
                 OUT / "01_heatmap_principale.png")

    # ---- Matrice pairwise (tutti, storia massima per coppia) ----
    corr_pairwise = rets.corr(min_periods=36)
    plot_heatmap(corr_pairwise, "Correlazioni pairwise - storia massima per coppia (tutti gli asset)",
                 OUT / "02_heatmap_pairwise_full.png")

    # ---- Matrice secondaria con Bitcoin ----
    sec_assets = keep + ["Bitcoin", "India"]
    sec_rets = rets[sec_assets].dropna()
    corr_sec = sec_rets.corr() if len(sec_rets) > 24 else pd.DataFrame()
    print(f"[secondaria+BTC] {sec_rets.index[0].date() if len(sec_rets) else '-'} -> {sec_rets.index[-1].date() if len(sec_rets) else '-'} ({len(sec_rets)} mesi)")

    # ---- Statistiche descrittive ----
    def avg_block(corr, block_a, block_b=None):
        block_b = block_b or block_a
        a = [x for x in block_a if x in corr.columns]
        b = [x for x in block_b if x in corr.columns]
        sub = corr.loc[a, b].values
        if block_b == block_a:
            iu = np.triu_indices_from(sub, k=1)
            return float(np.nanmean(sub[iu]))
        return float(np.nanmean(sub))

    eq = [e for e in EQUITY_LIKE if e in corr_main.columns]
    nq = [e for e in NON_EQUITY if e in corr_main.columns]
    stat = {
        "corr_media_totale": avg_block(corr_main, list(corr_main.columns)),
        "corr_media_azionario_azionario": avg_block(corr_main, eq),
        "corr_media_azionario_rifugi": avg_block(corr_main, eq, nq),
        "corr_media_tra_rifugi": avg_block(corr_main, nq),
    }
    # coppie estreme (solo matrice principale)
    cm = corr_main.copy()
    pairs = []
    for i, a in enumerate(cm.columns):
        for b in cm.columns[i + 1:]:
            pairs.append((a, b, float(cm.loc[a, b])))
    pairs.sort(key=lambda x: x[2])
    most_neg = pairs[:6]
    most_pos = pairs[-6:][::-1]

    # ---- diversificatori + rolling equity corr + crisi ----
    div_rank = plot_diversifier_ranking(main_rets, eq, OUT / "04_diversificatori_ranking.png")
    roll = plot_rolling_equity_corr(main_rets, eq, OUT / "03_corr_azionario_nel_tempo.png")
    # correlazione azionaria media nei periodi di crisi vs calma
    crisis_corr = {}
    for name, (a, b) in CRISES.items():
        w = main_rets.loc[a:b, eq].dropna(axis=1, how="any")
        if w.shape[1] >= 4 and len(w) >= 3:
            c = w.corr().values
            iu = np.triu_indices_from(c, k=1)
            crisis_corr[name] = float(np.nanmean(c[iu]))
    calm_corr = avg_block(corr_main, eq)

    # ---- Portafoglio min-correlazione ----
    port_assets, port_avg_corr = min_corr_portfolio(corr_main, k=5)
    print(f"[min-corr] portafoglio: {port_assets}  (corr media {port_avg_corr:.3f})")
    port_nav = backtest_buyhold(main_rets, port_assets)
    mkt_nav = backtest_buyhold(main_rets, ["USA (S&P 500)"])
    m_port, m_mkt = metrics(port_nav), metrics(mkt_nav)
    wr = rolling_winrate(port_nav, mkt_nav, 10)

    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.plot(port_nav.index, (port_nav.values - 1) * 100, color="#d97706", lw=2.2,
            label=f"Portafoglio min-correlazione (5 asset)")
    ax.plot(mkt_nav.index, (mkt_nav.values - 1) * 100, color="#1e3a8a", lw=2.0,
            label="S&P 500 (mercato)")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("Variazione % (base 0)")
    ax.set_title("Portafoglio a minima correlazione vs mercato", fontweight="bold")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "05_portafoglio_mincorr_vs_mercato.png", dpi=170); plt.close(fig)

    # scatter calma vs crisi
    fig, ax = plt.subplots(figsize=(8, 6))
    names = list(crisis_corr.keys()); yv = list(crisis_corr.values())
    ax.bar(range(len(names)), yv, color="#dc2626", alpha=0.75, label="durante la crisi")
    ax.axhline(calm_corr, color="#1e3a8a", lw=1.6, linestyle="--",
               label=f"media periodo pieno {calm_corr:.2f}")
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names)
    ax.set_ylabel("Correlazione media azionaria")
    ax.set_title("La diversificazione svanisce nei crolli", fontweight="bold")
    for i, v in enumerate(yv): ax.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=10)
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "06_scatter_corr_vs_crisi.png", dpi=170); plt.close(fig)

    # ---- salvataggi ----
    corr_main.to_csv(OUT / "corr_matrix_principale.csv")
    corr_pairwise.to_csv(OUT / "corr_matrix_pairwise.csv")
    pd.DataFrame({"port_mincorr": port_nav, "sp500": mkt_nav}).to_csv(
        OUT / "equity_mincorr_vs_market.csv", index_label="date")

    # lookup per heatmap interattiva (matrice principale)
    lookup = {
        "meta": {
            "source_article": f"/posts/{SLUG}",
            "window_start": str(main_rets.index[0].date()),
            "window_end": str(main_rets.index[-1].date()),
            "n_months": int(len(main_rets)),
            "assets_order": order_by_category(list(corr_main.columns)),
            "categories": {a: CATEGORY.get(a, "geo") for a in corr_main.columns},
        },
        "matrix": {a: {b: round(float(corr_main.loc[a, b]), 3) for b in corr_main.columns}
                   for a in corr_main.columns},
    }
    with open(LOOKUP_DIR / "corr-lookup.json", "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2, ensure_ascii=False)

    summary = {
        "slug": SLUG,
        "finestra_principale": {"start": str(main_rets.index[0].date()),
                                 "end": str(main_rets.index[-1].date()),
                                 "mesi": int(len(main_rets)),
                                 "n_asset": len(keep),
                                 "asset": keep},
        "statistiche": stat,
        "coppie_piu_correlate": [{"a": a, "b": b, "corr": c} for a, b, c in most_pos],
        "coppie_meno_correlate": [{"a": a, "b": b, "corr": c} for a, b, c in most_neg],
        "diversificatori_vs_azionario": {k: float(v) for k, v in div_rank.items()},
        "corr_azionaria_crisi": crisis_corr,
        "corr_azionaria_calma": calm_corr,
        "portafoglio_min_corr": {
            "asset": port_assets, "corr_media": port_avg_corr,
            "metriche": m_port, "rolling10y_winrate_vs_mercato": wr,
        },
        "mercato_sp500": {"metriche": m_mkt},
        "bitcoin_secondaria": (
            {b: round(float(corr_sec.loc["Bitcoin", b]), 3)
             for b in corr_sec.columns if b != "Bitcoin"}
            if len(corr_sec) else {}),
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)

    print(f"\n[done] Output in {OUT}")
    print(f"  corr media azionario-azionario: {stat['corr_media_azionario_azionario']:.3f}")
    print(f"  corr media azionario-rifugi:    {stat['corr_media_azionario_rifugi']:.3f}")
    print(f"  portafoglio min-corr CAGR {m_port['cagr']*100:.1f}% vs SP500 {m_mkt['cagr']*100:.1f}%")
    print(f"  MDD {m_port['mdd']*100:.0f}% vs {m_mkt['mdd']*100:.0f}%, Sharpe {m_port['sharpe']:.2f} vs {m_mkt['sharpe']:.2f}")


if __name__ == "__main__":
    main()
