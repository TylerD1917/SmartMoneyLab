"""
SmartMoneyLab - Qual e' il livello di leva piu' efficiente?
===========================================================

Sequel di `leva-raddoppia-rendimento-mercato`. Li' avevamo visto che la 3x
sottoperforma la 2x sulle metriche di lungo periodo. Qui esploriamo la
regione INTERMEDIA: fra 1x e 2x esiste un livello di leva "efficiente"?

Scala testata: 1.00, 1.10, 1.25, 1.40, 1.50, 1.60, 1.75, 1.90, 2.00.

Ogni livello e' realizzato come un PORTAFOGLIO di due ETF realmente
acquistabili, non come un ETF a leva frazionaria (che non esiste):

    leva L  ->  (L-1) in ETF 2x daily  +  (2-L) in ETF 1x

Esempio: leva 1.40 = 40% ETF 2x + 60% ETF 1x.

Due varianti di gestione, entrambe presentate:
  A) BUY & HOLD puro: pesi fissati il primo giorno e lasciati driftare.
     Coerente con la metodologia standard del blog, ma mostra che la leva
     NON resta quella scelta (il comparto 2x si mangia il portafoglio).
  B) RIBILANCIAMENTO ANNUALE: pesi riportati al target ogni 1 gennaio.
     E' l'unico modo per parlare davvero di "livello di leva". I rendimenti
     sono SOVRASTIMATI perche' non modelliamo imposte sulle plusvalenze
     realizzate al ribilanciamento ne' costi di transazione.

Indici (tutti in TOTAL RETURN, dividendi reinvestiti), pari dignita':
  - S&P 500      : TR daily (^SP500TR dal 1988; prima ^GSPC + dividendi Shiller)
  - Nasdaq Comp. : prezzo daily + dividendo figurato 0.75%/anno (convenzione blog)
  - MSCI World   : prezzo daily + dividendo implicito ricavato dalla serie TR
                   mensile MSCI (media 2.07%/anno, ma 3.16% negli anni 70)

COSTO DELLA LEVA - differenza metodologica rispetto all'articolo #1.
Li' usavamo un drag di funding COSTANTE (1.853%/anno per unita' di leva),
calibrato sui prezzi del ProShares Ultra S&P 500 (SSO) 2006-2023. Ma in
quella finestra i Fed Funds hanno fatto in media 1.41%, contro il 4.67%
del periodo 1975-2026 (9.01% nel 1975-89, 0.52% nel 2009-21). Un drag
costante regala alla leva ~3 punti/anno negli anni Ottanta.
Qui il funding e' VARIABILE:

    funding_t = FedFunds_t + spread

con lo spread calibrato sui dati SSO: cerchiamo lo spread che fa coincidere
il CAGR della 2x sintetica (con funding variabile) con quello dell'SSO reale
sulla sua intera storia disponibile.

Costi applicati ai due comparti (TER UCITS, quelli comprabili in Europa):
    1x : TER_1X/anno
    2x : TER_2X/anno + 1 x funding_t  (prende a prestito 1x il NAV)

LORDO DI IMPOSTE. Niente tassazione italiana (26% capital gain + bollo),
niente costi di transazione, niente spread bid/ask.

Output:
  public/charts/qual-e-il-livello-di-leva-piu-efficiente/*.png
  public/charts/qual-e-il-livello-di-leva-piu-efficiente/summary.json
  public/charts/qual-e-il-livello-di-leva-piu-efficiente/*.csv

Autore: SmartMoneyLab - 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------------------------------------------ #
# Percorsi e parametri                                               #
# ------------------------------------------------------------------ #
SLUG = "qual-e-il-livello-di-leva-piu-efficiente"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
DATA = REPO / "data"
OUT = REPO / "public" / "charts" / SLUG
OUT.mkdir(parents=True, exist_ok=True)

START = "1975-01-02"

# Scala di leva richiesta
LEVELS = [1.00, 1.10, 1.25, 1.40, 1.50, 1.60, 1.75, 1.90, 2.00]

# TER UCITS annui (prodotti realmente acquistabili in Europa)
TER_1X = 0.0005   # ETF indice classico (0.05%)
TER_2X = 0.0060   # ETF 2x daily leveraged swap UCITS (0.60%)

# TER del prodotto usato per la calibrazione (US, ProShares)
TER_SSO = 0.0089

# Dividendo figurato Nasdaq Composite (convenzione del blog)
NASDAQ_DIV_YIELD = 0.0075

TRADING_DAYS = 252

WINDOWS_MONTHS = {"5y": 60, "10y": 120, "20y": 240}
STEP_MONTHS = 3

COLORS = {
    "S&P 500": "#1e3a8a",
    "Nasdaq": "#d97706",
    "MSCI World": "#0f766e",
}


# ------------------------------------------------------------------ #
# Loader                                                             #
# ------------------------------------------------------------------ #
def _read_yahoo_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    s = pd.to_numeric(df["Close"], errors="coerce").dropna()
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s.sort_index()


def load_fedfunds_daily(index: pd.DatetimeIndex) -> pd.Series:
    """Fed Funds effective rate mensile (FRED) riportato su calendario daily."""
    ff = pd.read_csv(DATA / "Bonds" / "FEDFUNDS.csv", parse_dates=["observation_date"])
    ff = ff.set_index("observation_date")["FEDFUNDS"].astype(float) / 100.0
    out = ff.reindex(ff.index.union(index)).ffill().reindex(index)
    return out.ffill().bfill().rename("ffr")


def load_sp500_tr_daily() -> pd.Series:
    """
    Rendimenti daily total return S&P 500.
      - dal 1988-01-04: indice ^SP500TR (fonte canonica, fine giornata)
      - prima: prezzo ^GSPC + dividendi mensili Shiller distribuiti
        uniformemente sui giorni di trading del mese
    """
    px = _read_yahoo_csv(DATA / "Sp500" / "Sp500_daily_1927_GSPC.csv")
    tr = _read_yahoo_csv(DATA / "Sp500" / "Sp500_TotalReturn1988_USD.csv")

    sh = pd.read_csv(DATA / "Sp500" / "shiller_mirror.csv", parse_dates=["Date"])
    sh = sh.set_index("Date")
    div_annual = pd.to_numeric(sh["Dividend"], errors="coerce")
    price_m = pd.to_numeric(sh["SP500"], errors="coerce")
    # il mirror Shiller mette 0 dove il dividendo non e' piu' riportato
    yld_m = (div_annual / 12.0 / price_m).replace([np.inf, -np.inf], np.nan)
    yld_m = yld_m.where(div_annual > 0)

    r_px = px.pct_change().dropna()
    # yield mensile -> quota giornaliera, divisa per i giorni di trading del mese
    key = r_px.index.to_period("M")
    ndays = r_px.groupby(key).transform("size")
    ym = pd.Series(yld_m.values, index=yld_m.index.to_period("M"))
    daily_div = pd.Series(key.map(ym).astype(float), index=r_px.index) / ndays
    daily_div = daily_div.fillna(0.0)

    r_pre = (r_px + daily_div).loc[:"1987-12-31"]
    r_post = tr.pct_change().dropna().loc["1988-01-04":]
    r = pd.concat([r_pre, r_post]).sort_index()
    r = r[~r.index.duplicated(keep="last")]
    return r.loc[START:].rename("sp500")


def load_nasdaq_tr_daily() -> pd.Series:
    px = _read_yahoo_csv(DATA / "Nasdaq" / "Nasdaq_composite1971.csv")
    r = px.pct_change().dropna() + NASDAQ_DIV_YIELD / TRADING_DAYS
    return r.loc[START:].rename("nasdaq")


def load_msci_world_tr_daily() -> tuple[pd.Series, pd.Series]:
    """
    Prezzo daily MSCI World + dividendo implicito ricavato confrontando la
    serie TR mensile MSCI col prezzo di fine mese. Lo yield mensile e'
    lisciato con una media mobile a 12 mesi (le due serie hanno convenzioni
    di data leggermente diverse e il grezzo e' rumoroso) e vincolato >= 0.
    Ritorna (rendimenti daily TR, yield annuo implicito mensile).
    """
    px = _read_yahoo_csv(DATA / "Msci_world" / "MSCI WORLD_USD_daily_1972.csv")

    tr_m = pd.read_csv(DATA / "Msci_world" / "MSCI_world_historical1969.csv")
    tr_m.columns = ["d", "v"]
    tr_m["d"] = pd.to_datetime(tr_m["d"], format="%m/%Y")
    tr_m = tr_m.set_index("d")["v"].astype(float)

    px_m = px.resample("ME").last()
    px_m.index = px_m.index.to_period("M").to_timestamp()

    j = pd.concat([tr_m.rename("tr"), px_m.rename("px")], axis=1).dropna()
    raw = (j["tr"].pct_change() - j["px"].pct_change()).dropna()
    smooth = raw.rolling(12, min_periods=3).mean().clip(lower=0.0)
    smooth = smooth.bfill()

    r_px = px.pct_change().dropna()
    key = r_px.index.to_period("M")
    ndays = r_px.groupby(key).transform("size")
    sm = pd.Series(smooth.values, index=smooth.index.to_period("M"))
    daily_div = pd.Series(key.map(sm).astype(float), index=r_px.index) / ndays
    daily_div = daily_div.fillna(0.0)

    r = (r_px + daily_div).loc[START:].rename("world")
    return r, (smooth * 12.0)


# ------------------------------------------------------------------ #
# Calibrazione del costo di funding sui dati SSO                     #
# ------------------------------------------------------------------ #
def calibrate_funding_spread() -> dict:
    """
    Cerca lo spread `s` tale che una 2x sintetica con drag giornaliero
        (TER_SSO + FedFunds_t + s) / 252
    replichi il CAGR realizzato dal ProShares Ultra S&P 500 (SSO) reale
    sulla sua intera storia nel CSV di confronto (2006-06 -> 2023-12).

    Confronto a parita' di sottostante: i rendimenti daily sono quelli del
    SPY contenuto nello stesso file, quindi nessun effetto cambio e nessuna
    differenza di calendario.
    """
    df = pd.read_csv(DATA / "cache" / "confronto_leva_spy_sso.csv", parse_dates=["Date"])
    df = df.set_index("Date").sort_index()
    spy = pd.to_numeric(df["Price_SPY_1x"], errors="coerce").dropna()
    sso = pd.to_numeric(df["Price_SSO_Real_2x"], errors="coerce").dropna()
    idx = spy.index.intersection(sso.index)
    spy, sso = spy.loc[idx], sso.loc[idx]

    r = spy.pct_change().dropna()
    ffr = load_fedfunds_daily(r.index)
    years = (r.index[-1] - r.index[0]).days / 365.25
    cagr_real = (sso.loc[r.index[-1]] / sso.loc[r.index[0]]) ** (1 / years) - 1

    def cagr_synth(s: float) -> float:
        drag = (TER_SSO + ffr + s) / TRADING_DAYS
        nav = float(np.prod(1.0 + (2.0 * r - drag).values))
        return nav ** (1 / years) - 1

    lo, hi = -0.05, 0.20
    for _ in range(200):
        mid = (lo + hi) / 2
        if cagr_synth(mid) > cagr_real:
            lo = mid           # drag troppo basso, alzo lo spread
        else:
            hi = mid
    spread = (lo + hi) / 2

    # confronto con il modello a drag costante dell'articolo #1
    drag_const = None
    nav_synth_nocost = float(np.prod(1.0 + (2.0 * r).values))
    drag_const = (np.log(nav_synth_nocost) - np.log(float(sso.iloc[-1] / sso.iloc[0]))) / years

    res = {
        "fonte": "ProShares Ultra S&P 500 (SSO) vs 2x sintetica su SPY",
        "periodo": {"start": str(r.index[0].date()), "end": str(r.index[-1].date())},
        "anni": float(years),
        "cagr_sso_reale": float(cagr_real),
        "cagr_2x_sintetica_lorda": float(nav_synth_nocost ** (1 / years) - 1),
        "ter_sso": TER_SSO,
        "ffr_medio_finestra": float(ffr.mean()),
        "spread_funding_calibrato": float(spread),
        "funding_medio_implicito_finestra": float(ffr.mean() + spread),
        "drag_totale_costante_articolo_1": float(drag_const),
        "funding_costante_articolo_1": float(drag_const - TER_SSO),
        "cagr_sintetica_calibrata": float(cagr_synth(spread)),
    }
    return res


# ------------------------------------------------------------------ #
# Motore di portafoglio                                              #
# ------------------------------------------------------------------ #
def sleeve_returns(r: pd.Series, ffr: pd.Series, spread: float) -> tuple[np.ndarray, np.ndarray]:
    """Rendimenti daily netti dei due comparti realmente acquistabili."""
    r1 = (r - TER_1X / TRADING_DAYS).values
    funding = (ffr + spread).values
    r2 = (2.0 * r.values) - (TER_2X + funding) / TRADING_DAYS
    return r1, r2


def nav_buy_hold(r1: np.ndarray, r2: np.ndarray, w2: float) -> np.ndarray:
    """Pesi fissati il primo giorno, poi drift libero."""
    g1 = np.cumprod(1.0 + r1)
    g2 = np.cumprod(1.0 + r2)
    return (1.0 - w2) * g1 + w2 * g2


def nav_rebalanced(r1: np.ndarray, r2: np.ndarray, w2: float, year_starts: np.ndarray) -> np.ndarray:
    """
    Ribilanciamento ai pesi target a ogni inizio anno solare.
    `year_starts` = indici posizionali dei giorni che aprono un nuovo anno.
    """
    n = len(r1)
    nav = np.empty(n)
    v1 = (1.0 - w2)
    v2 = w2
    for i in range(n):
        if i in year_starts and i > 0:
            tot = v1 + v2
            v1, v2 = (1.0 - w2) * tot, w2 * tot
        v1 *= (1.0 + r1[i])
        v2 *= (1.0 + r2[i])
        nav[i] = v1 + v2
    return nav


def nav_rebalanced_fast(r1: np.ndarray, r2: np.ndarray, w2: float, bounds: list[tuple[int, int]]) -> np.ndarray:
    """Versione vettorizzata a blocchi annuali del ribilanciamento."""
    nav = np.empty(len(r1))
    tot = 1.0
    for a, b in bounds:
        g1 = np.cumprod(1.0 + r1[a:b])
        g2 = np.cumprod(1.0 + r2[a:b])
        seg = tot * ((1.0 - w2) * g1 + w2 * g2)
        nav[a:b] = seg
        tot = seg[-1]
    return nav


def effective_leverage_bh(r1: np.ndarray, r2: np.ndarray, w2: float) -> np.ndarray:
    """Leva effettiva nel tempo di un mix buy & hold."""
    g1 = np.cumprod(1.0 + r1)
    g2 = np.cumprod(1.0 + r2)
    v1 = (1.0 - w2) * g1
    v2 = w2 * g2
    return (v1 * 1.0 + v2 * 2.0) / (v1 + v2)


def year_bounds(index: pd.DatetimeIndex) -> list[tuple[int, int]]:
    years = index.year.values
    bounds, start = [], 0
    for i in range(1, len(years)):
        if years[i] != years[i - 1]:
            bounds.append((start, i))
            start = i
    bounds.append((start, len(years)))
    return bounds


# ------------------------------------------------------------------ #
# Metriche (convenzione 6+1 del blog, su base daily)                 #
# ------------------------------------------------------------------ #
def metrics_from_nav(nav: np.ndarray, rf: np.ndarray | None = None) -> dict:
    """
    `rf` = rendimento giornaliero privo di rischio allineato a nav[1:].
    Serve per le versioni in eccesso di Sharpe e Sortino: sono le uniche
    corrette per confrontare livelli di leva diversi, perche' la leva e'
    letteralmente denaro preso a prestito a un tasso vicino al monetario.
    Nella convenzione grezza (senza sottrarre il monetario) lo Sharpe cala
    con la leva per pura costruzione algebrica, qualunque siano i dati.
    """
    rr = nav[1:] / nav[:-1] - 1.0
    n = len(nav)
    years = n / TRADING_DAYS
    cagr = nav[-1] ** (1 / years) - 1
    vol = rr.std(ddof=1) * np.sqrt(TRADING_DAYS)
    peak = np.maximum.accumulate(nav)
    mdd = float((nav / peak - 1.0).min())
    sharpe = (rr.mean() * TRADING_DAYS) / vol if vol > 0 else np.nan
    neg = rr[rr < 0]
    dvol = neg.std(ddof=1) * np.sqrt(TRADING_DAYS) if len(neg) > 2 else np.nan
    sortino = (rr.mean() * TRADING_DAYS) / dvol if dvol and dvol > 0 else np.nan
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan
    out = {
        "cagr": float(cagr), "vol": float(vol), "mdd": mdd,
        "sharpe": float(sharpe), "sortino": float(sortino), "calmar": float(calmar),
        "multiplo": float(nav[-1]),
    }
    if rf is not None:
        ex = rr - rf
        dneg = ex[ex < 0]
        dv = dneg.std(ddof=1) * np.sqrt(TRADING_DAYS) if len(dneg) > 2 else np.nan
        out["sharpe_ex"] = float((ex.mean() * TRADING_DAYS) / vol) if vol > 0 else np.nan
        out["sortino_ex"] = float((ex.mean() * TRADING_DAYS) / dv) if dv and dv > 0 else np.nan
        out["rf_medio"] = float(rf.mean() * TRADING_DAYS)
    return out


# ------------------------------------------------------------------ #
# Analisi rolling                                                    #
# ------------------------------------------------------------------ #
def month_start_positions(index: pd.DatetimeIndex) -> np.ndarray:
    per = index.to_period("M")
    first = ~pd.Series(per).duplicated().values
    return np.flatnonzero(first)


def rolling_table(r1: np.ndarray, r2: np.ndarray, index: pd.DatetimeIndex,
                  win_months: int, step: int, mode: str,
                  rf: np.ndarray | None = None) -> pd.DataFrame:
    """
    Per ogni finestra e ogni livello di leva, metriche della finestra.
    I pesi ripartono dal target all'inizio di ogni finestra.
    """
    ms = month_start_positions(index)
    rows = []
    for i in range(0, len(ms) - win_months, step):
        a, b = ms[i], ms[i + win_months]
        s1, s2 = r1[a:b], r2[a:b]
        srf = rf[a + 1:b] if rf is not None else None
        bounds = year_bounds(index[a:b]) if mode == "reb" else None
        rec = {"start": index[a], "end": index[b - 1], "rf_medio": float(srf.mean() * TRADING_DAYS) if srf is not None else np.nan}
        for L in LEVELS:
            w = L - 1.0
            nav = nav_buy_hold(s1, s2, w) if mode == "bh" else nav_rebalanced_fast(s1, s2, w, bounds)
            m = metrics_from_nav(nav, srf)
            for k in ("cagr", "vol", "mdd", "sharpe", "calmar", "sortino", "sharpe_ex", "sortino_ex"):
                rec[f"{k}_{L:.2f}"] = m[k]
        rows.append(rec)
    return pd.DataFrame(rows)


def optimal_leverage_by_window(tab: pd.DataFrame, metric: str) -> pd.Series:
    cols = [f"{metric}_{L:.2f}" for L in LEVELS]
    sub = tab[cols]
    arg = sub.values.argmax(axis=1)
    return pd.Series([LEVELS[i] for i in arg], index=tab["start"])


# ------------------------------------------------------------------ #
# Grafici                                                            #
# ------------------------------------------------------------------ #
def _style(ax, title, ylabel, xlabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=10)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)


def chart_efficiency_curves(full: dict, metric: str, label: str, fname: Path,
                            pct: bool = True, note: str = ""):
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, per_lev in full.items():
        y = [per_lev[f"{L:.2f}"][metric] * (100 if pct else 1) for L in LEVELS]
        ax.plot(LEVELS, y, marker="o", lw=2.2, color=COLORS[name], label=name)
        best = int(np.argmax(y)) if metric != "mdd" else int(np.argmax(y))
        ax.scatter([LEVELS[best]], [y[best]], s=160, facecolors="none",
                   edgecolors=COLORS[name], lw=2.2, zorder=5)
    _style(ax, f"{label} al variare della leva", label, "Livello di leva")
    ax.set_xticks(LEVELS)
    ax.set_xticklabels([f"{L:.2f}" for L in LEVELS])
    ax.legend(frameon=False, fontsize=10)
    if note:
        fig.text(0.5, 0.01, note, ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_drift(levs: dict, index: pd.DatetimeIndex, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = plt.get_cmap("viridis")
    show = [1.10, 1.25, 1.50, 1.75, 1.90]
    for k, L in enumerate(show):
        ax.plot(index, levs[f"{L:.2f}"], lw=1.8, color=cmap(k / max(1, len(show) - 1)),
                label=f"leva iniziale {L:.2f}")
    ax.axhline(2.0, color="#991b1b", ls="--", lw=1.2)
    ax.text(index[int(len(index) * 0.02)], 1.98, "leva 2x", color="#991b1b", fontsize=9, va="top")
    _style(ax, "Buy & hold: la leva che compri non e' quella che tieni",
           "Leva effettiva del portafoglio", "")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.text(0.5, 0.01, "S&P 500 total return. Mix 1x/2x senza ribilanciamento: il comparto 2x cresce di piu' e satura il portafoglio.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_rolling_box(tabs: dict, metric: str, label: str, win: str, fname: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)
    for ax, (name, tab) in zip(axes, tabs.items()):
        data = [tab[f"{metric}_{L:.2f}"].dropna().values * 100 for L in LEVELS]
        bp = ax.boxplot(data, patch_artist=True, widths=0.6,
                        medianprops=dict(color="#111", lw=1.6), showfliers=False)
        for patch in bp["boxes"]:
            patch.set_facecolor(COLORS[name])
            patch.set_alpha(0.35)
            patch.set_edgecolor(COLORS[name])
        ax.set_xticks(range(1, len(LEVELS) + 1))
        ax.set_xticklabels([f"{L:.2f}" for L in LEVELS], rotation=45, fontsize=8)
        ax.axhline(0, color="#999", lw=0.8)
        _style(ax, name, label if ax is axes[0] else "", "Livello di leva")
    fig.suptitle(f"Distribuzione del {label.lower()} sulle finestre mobili a {win}",
                 fontsize=14, fontweight="bold")
    fig.text(0.5, 0.01, "Finestre mobili con passo trimestrale, ribilanciamento annuale ai pesi target. Lordo di imposte e costi di transazione.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_equity(navs: dict, index: pd.DatetimeIndex, name: str, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = plt.get_cmap("viridis")
    for k, L in enumerate(LEVELS):
        ax.plot(index, navs[f"{L:.2f}"], lw=1.6,
                color=cmap(k / (len(LEVELS) - 1)), label=f"{L:.2f}x")
    ax.set_yscale("log")
    _style(ax, f"{name}: crescita di 1 dollaro per livello di leva", "NAV (scala logaritmica)")
    ax.legend(frameon=False, fontsize=8, ncol=3)
    fig.text(0.5, 0.01, "Ribilanciamento annuale ai pesi target. Lordo di imposte e costi di transazione.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_orizzonti(summary_idx: dict, stat: str, label: str, fname: Path):
    """Mediana (o media, o p5) del CAGR rolling per livello di leva, un pannello
    per indice e una curva per orizzonte."""
    styles = {"5y": ("#94a3b8", "5 anni", ":"), "10y": ("#3b82f6", "10 anni", "--"),
              "20y": ("#1e3a8a", "20 anni", "-")}
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    for ax, name in zip(axes, summary_idx.keys()):
        for wl, (col, lab, ls) in styles.items():
            y = [summary_idx[name]["rolling_percentili"][wl][f"{L:.2f}"][stat] * 100 for L in LEVELS]
            ax.plot(LEVELS, y, marker="o", ms=4, lw=2, ls=ls, color=col, label=lab)
            b = int(np.argmax(y))
            ax.scatter([LEVELS[b]], [y[b]], s=130, facecolors="none", edgecolors=col, lw=2, zorder=5)
        ax.set_xticks(LEVELS)
        ax.set_xticklabels([f"{L:.2f}" for L in LEVELS], rotation=45, fontsize=8)
        _style(ax, name, f"{label} (%)" if ax is axes[0] else "", "Livello di leva")
        ax.legend(frameon=False, fontsize=9, title="orizzonte", title_fontsize=8)
    fig.suptitle(f"{label} del CAGR sulle finestre mobili, per livello di leva e orizzonte",
                 fontsize=14, fontweight="bold")
    fig.text(0.5, 0.01, "Cerchio vuoto = livello di leva migliore per quell'orizzonte. Ribilanciamento annuale, lordo di imposte e costi di transazione.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_opt_vs_rates(points: list, fname: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, x, y in points:
        jitter = (np.random.default_rng(7).random(len(y)) - 0.5) * 0.04
        ax.scatter(np.array(x) * 100, np.array(y) + jitter, s=28, alpha=0.6,
                   color=COLORS[name], label=name)
    _style(ax, "La leva piu' efficiente dipende dal costo del denaro",
           "Leva con il CAGR migliore nella finestra", "Fed Funds medi della finestra (%)")
    ax.legend(frameon=False, fontsize=10)
    fig.text(0.5, 0.01, "Una osservazione per ogni finestra mobile a 10 anni, passo trimestrale. Punti dispersi verticalmente per leggibilita'.",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


def chart_bh_vs_reb(full_bh: dict, full_reb: dict, fname: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)
    for ax, name in zip(axes, full_bh.keys()):
        y_bh = [full_bh[name][f"{L:.2f}"]["cagr"] * 100 for L in LEVELS]
        y_rb = [full_reb[name][f"{L:.2f}"]["cagr"] * 100 for L in LEVELS]
        ax.plot(LEVELS, y_bh, marker="s", lw=2, color="#94a3b8", label="buy & hold")
        ax.plot(LEVELS, y_rb, marker="o", lw=2.2, color=COLORS[name], label="ribilanciato")
        ax.set_xticks(LEVELS)
        ax.set_xticklabels([f"{L:.2f}" for L in LEVELS], rotation=45, fontsize=8)
        _style(ax, name, "CAGR (%)" if ax is axes[0] else "", "Livello di leva iniziale")
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle("Senza ribilanciamento i livelli di leva collassano l'uno sull'altro",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(fname, dpi=160)
    plt.close(fig)


# ------------------------------------------------------------------ #
# Main                                                               #
# ------------------------------------------------------------------ #
def main():
    print("=" * 74)
    print("SmartMoneyLab - Qual e' il livello di leva piu' efficiente?")
    print("=" * 74)

    r_sp = load_sp500_tr_daily()
    r_nq = load_nasdaq_tr_daily()
    r_wd, wd_yield = load_msci_world_tr_daily()
    series = {"S&P 500": r_sp, "Nasdaq": r_nq, "MSCI World": r_wd}

    lo = max(s.index[0] for s in series.values())
    hi = min(s.index[-1] for s in series.values())
    series = {k: v.loc[lo:hi] for k, v in series.items()}
    print(f"\nPeriodo comune: {lo.date()} -> {hi.date()}")
    for k, v in series.items():
        print(f"  {k:<11} {len(v):>6} giorni  CAGR lordo indice "
              f"{((1+v).prod()**(252/len(v))-1)*100:5.2f}%  "
              f"vol {v.std()*np.sqrt(252)*100:5.2f}%")

    cal = calibrate_funding_spread()
    print("\n--- Calibrazione del costo della leva (ProShares SSO) ---")
    print(f"  finestra            : {cal['periodo']['start']} -> {cal['periodo']['end']} "
          f"({cal['anni']:.1f} anni)")
    print(f"  CAGR SSO reale      : {cal['cagr_sso_reale']*100:6.2f}%")
    print(f"  CAGR 2x sintetica   : {cal['cagr_2x_sintetica_lorda']*100:6.2f}%  (lorda, senza costi)")
    print(f"  Fed Funds medi      : {cal['ffr_medio_finestra']*100:6.2f}%")
    print(f"  spread calibrato    : {cal['spread_funding_calibrato']*100:+6.2f}%")
    print(f"  funding medio impl. : {cal['funding_medio_implicito_finestra']*100:6.2f}%")
    print(f"  [articolo #1] funding costante: {cal['funding_costante_articolo_1']*100:6.2f}%")
    spread = cal["spread_funding_calibrato"]

    full_bh, full_reb, rolling, opt_points = {}, {}, {}, []
    navs_store, drift_store = {}, {}
    summary_idx = {}

    for name, r in series.items():
        ffr = load_fedfunds_daily(r.index)
        r1, r2 = sleeve_returns(r, ffr, spread)
        rf_d = (ffr / TRADING_DAYS).values
        bounds = year_bounds(r.index)

        full_bh[name], full_reb[name] = {}, {}
        navs, drifts = {}, {}
        for L in LEVELS:
            w = L - 1.0
            nav_b = nav_buy_hold(r1, r2, w)
            nav_r = nav_rebalanced_fast(r1, r2, w, bounds)
            full_bh[name][f"{L:.2f}"] = metrics_from_nav(nav_b, rf_d[1:])
            full_reb[name][f"{L:.2f}"] = metrics_from_nav(nav_r, rf_d[1:])
            full_bh[name][f"{L:.2f}"]["leva_finale"] = float(effective_leverage_bh(r1, r2, w)[-1])
            navs[f"{L:.2f}"] = nav_r
            drifts[f"{L:.2f}"] = effective_leverage_bh(r1, r2, w)
        navs_store[name] = (navs, r.index)
        drift_store[name] = (drifts, r.index)

        rolling[name] = {}
        for wl, wm in WINDOWS_MONTHS.items():
            rolling[name][wl] = rolling_table(r1, r2, r.index, wm, STEP_MONTHS, "reb", rf_d)

        t10 = rolling[name]["10y"]
        ffr_m = pd.Series(ffr.values, index=ffr.index)
        avg_r = [float(ffr_m.loc[a:b].mean()) for a, b in zip(t10["start"], t10["end"])]
        opt_points.append((name, avg_r, list(optimal_leverage_by_window(t10, "cagr").values)))

        summary_idx[name] = {
            "periodo": {"start": str(r.index[0].date()), "end": str(r.index[-1].date()),
                        "giorni": int(len(r))},
            "indice_cagr_lordo": float((1 + r).prod() ** (252 / len(r)) - 1),
            "indice_vol": float(r.std() * np.sqrt(252)),
            "full_period_ribilanciato": full_reb[name],
            "full_period_buy_and_hold": full_bh[name],
        }

    # win rate e percentili rolling
    for name in series:
        wr = {}
        for wl in WINDOWS_MONTHS:
            tab = rolling[name][wl]
            base = tab["cagr_1.00"]
            wr[wl] = {f"{L:.2f}": float((tab[f"cagr_{L:.2f}"] > base).mean()) for L in LEVELS}
        pct = {}
        for wl in WINDOWS_MONTHS:
            tab = rolling[name][wl]
            pct[wl] = {}
            for L in LEVELS:
                s = tab[f"cagr_{L:.2f}"]
                pct[wl][f"{L:.2f}"] = {
                    "media": float(s.mean()), "dev_std": float(s.std()),
                    "minimo": float(s.min()), "massimo": float(s.max()),
                    "p5": float(s.quantile(.05)), "p10": float(s.quantile(.10)),
                    "p25": float(s.quantile(.25)),
                    "p50": float(s.quantile(.50)), "p75": float(s.quantile(.75)),
                    "p95": float(s.quantile(.95)), "n": int(s.notna().sum()),
                    "mdd_p50": float(rolling[name][wl][f"mdd_{L:.2f}"].quantile(.50)),
                    "sharpe_p50": float(rolling[name][wl][f"sharpe_{L:.2f}"].quantile(.50)),
                    "calmar_p50": float(rolling[name][wl][f"calmar_{L:.2f}"].quantile(.50)),
                }
        summary_idx[name]["rolling_win_rate_vs_1x"] = wr
        summary_idx[name]["rolling_percentili"] = pct

    # ---------------- report a video ---------------- #
    for name in series:
        print(f"\n{'='*74}\n{name} - periodo intero, RIBILANCIATO ogni anno\n{'='*74}")
        print(f"{'leva':>5} {'CAGR':>8} {'vol':>7} {'MDD':>8} {'Sharpe':>7} {'Sh.ecc':>7} "
              f"{'Sortino':>8} {'So.ecc':>7} {'Calmar':>7} {'multiplo':>10}")
        for L in LEVELS:
            m = full_reb[name][f"{L:.2f}"]
            print(f"{L:5.2f} {m['cagr']*100:7.2f}% {m['vol']*100:6.2f}% {m['mdd']*100:7.1f}% "
                  f"{m['sharpe']:7.3f} {m['sharpe_ex']:7.3f} {m['sortino']:8.3f} "
                  f"{m['sortino_ex']:7.3f} {m['calmar']:7.3f} {m['multiplo']:9.1f}x")
        for met, lbl in [("cagr", "CAGR"), ("sharpe", "Sharpe"), ("sharpe_ex", "Sharpe ecc"),
                         ("calmar", "Calmar"), ("sortino_ex", "Sortino ecc")]:
            vals = [full_reb[name][f"{L:.2f}"][met] for L in LEVELS]
            print(f"  -> leva migliore per {lbl:<8}: {LEVELS[int(np.argmax(vals))]:.2f}")

    print(f"\n{'='*74}\nBUY & HOLD: leva effettiva a fine periodo\n{'='*74}")
    for name in series:
        row = "  ".join(f"{L:.2f}->{full_bh[name][f'{L:.2f}']['leva_finale']:.2f}" for L in LEVELS[1:])
        print(f"{name:<12} {row}")

    print(f"\n{'='*74}\nWin rate vs 1x (finestre mobili a 10 anni)\n{'='*74}")
    for name in series:
        wr = summary_idx[name]["rolling_win_rate_vs_1x"]["10y"]
        print(f"{name:<12} " + "  ".join(f"{L:.2f}:{wr[f'{L:.2f}']*100:5.1f}%" for L in LEVELS[1:]))

    for wl in ("5y", "10y", "20y"):
        print(f"\n{'='*86}\nFinestre mobili a {wl}: CAGR media / mediana / percentili\n{'='*86}")
        for name in series:
            pct = summary_idx[name]["rolling_percentili"][wl]
            wr = summary_idx[name]["rolling_win_rate_vs_1x"][wl]
            print(f"\n{name}  (n = {pct['1.00']['n']} finestre)")
            print(f"{'leva':>5} {'media':>8} {'mediana':>9} {'dev.std':>8} {'p5':>8} {'p25':>8} "
                  f"{'p75':>8} {'p95':>8} {'MDD p50':>9} {'win vs 1x':>10}")
            for L in LEVELS:
                d = pct[f"{L:.2f}"]
                w = "" if L == 1.0 else f"{wr[f'{L:.2f}']*100:9.1f}%"
                print(f"{L:5.2f} {d['media']*100:7.2f}% {d['p50']*100:8.2f}% {d['dev_std']*100:7.2f}% "
                      f"{d['p5']*100:7.2f}% {d['p25']*100:7.2f}% {d['p75']*100:7.2f}% "
                      f"{d['p95']*100:7.2f}% {d['mdd_p50']*100:8.1f}% {w:>10}")
            vals_med = [pct[f"{L:.2f}"]["p50"] for L in LEVELS]
            vals_avg = [pct[f"{L:.2f}"]["media"] for L in LEVELS]
            vals_p5 = [pct[f"{L:.2f}"]["p5"] for L in LEVELS]
            print(f"  -> leva migliore: mediana {LEVELS[int(np.argmax(vals_med))]:.2f} | "
                  f"media {LEVELS[int(np.argmax(vals_avg))]:.2f} | "
                  f"p5 {LEVELS[int(np.argmax(vals_p5))]:.2f}")

    print(f"\n{'='*74}\nPrezzo della leva: quanto CAGR compri per ogni punto di perdita massima\n{'='*74}")
    for name in series:
        base = full_reb[name]["1.00"]
        print(f"\n{name}")
        for L in LEVELS[1:]:
            m = full_reb[name][f"{L:.2f}"]
            d_cagr = (m["cagr"] - base["cagr"]) * 100
            d_mdd = (abs(m["mdd"]) - abs(base["mdd"])) * 100
            print(f"  {L:.2f}: CAGR {d_cagr:+5.2f}pp   MDD {d_mdd:+5.1f}pp   "
                  f"rapporto {d_cagr/d_mdd if d_mdd else float('nan'):.3f} pp di CAGR per pp di perdita")

    print(f"\n{'='*74}\nLeva con il CAGR migliore nelle finestre 10 anni, per regime di tassi\n{'='*74}")
    for name, xs, ys in opt_points:
        df = pd.DataFrame({"ffr": xs, "opt": ys})
        lo_r = df[df.ffr < df.ffr.median()]
        hi_r = df[df.ffr >= df.ffr.median()]
        corr = df["ffr"].corr(df["opt"])
        print(f"{name:<12} leva ottima media: tassi bassi {lo_r.opt.mean():.2f} "
              f"(FF medi {lo_r.ffr.mean()*100:.2f}%) | tassi alti {hi_r.opt.mean():.2f} "
              f"(FF medi {hi_r.ffr.mean()*100:.2f}%) | correlazione {corr:+.2f}")
        q = (df.opt >= 1.9).mean()
        print(f"{'':<12} finestre in cui la leva massima e' la migliore: {q*100:.1f}%  |  "
              f"finestre in cui vince 1.00: {(df.opt == 1.0).mean()*100:.1f}%")

    # ---------------- grafici ---------------- #
    note = "Mix di ETF 1x e 2x daily, ribilanciato ogni anno. Costi: TER UCITS + funding a Fed Funds + spread calibrato su SSO. Lordo di imposte."
    chart_efficiency_curves(full_reb, "cagr", "CAGR (%)", OUT / "01_cagr_vs_leva.png", note=note)
    chart_efficiency_curves(full_reb, "sharpe", "Sharpe", OUT / "02_sharpe_vs_leva.png", pct=False, note=note)
    chart_efficiency_curves(full_reb, "sharpe_ex", "Sharpe in eccesso sul monetario",
                            OUT / "02b_sharpe_eccesso_vs_leva.png", pct=False, note=note)
    chart_efficiency_curves(full_reb, "calmar", "Calmar", OUT / "03_calmar_vs_leva.png", pct=False, note=note)
    chart_efficiency_curves(full_reb, "mdd", "Massima perdita (%)", OUT / "04_mdd_vs_leva.png", note=note)
    chart_drift(drift_store["S&P 500"][0], drift_store["S&P 500"][1], OUT / "05_drift_leva_buy_and_hold.png")
    chart_bh_vs_reb(full_bh, full_reb, OUT / "06_buy_and_hold_vs_ribilanciato.png")
    chart_rolling_box({k: rolling[k]["10y"] for k in series}, "cagr", "CAGR", "10 anni",
                      OUT / "07_rolling_10y_cagr.png")
    chart_rolling_box({k: rolling[k]["20y"] for k in series}, "cagr", "CAGR", "20 anni",
                      OUT / "08_rolling_20y_cagr.png")
    for name in series:
        slug = {"S&P 500": "sp500", "Nasdaq": "nasdaq", "MSCI World": "world"}[name]
        chart_equity(navs_store[name][0], navs_store[name][1], name, OUT / f"09_equity_{slug}.png")
    chart_opt_vs_rates(opt_points, OUT / "10_leva_ottima_vs_tassi.png")
    chart_orizzonti(summary_idx, "p50", "Mediana", OUT / "11_mediana_per_orizzonte.png")
    chart_orizzonti(summary_idx, "media", "Media", OUT / "12_media_per_orizzonte.png")
    chart_orizzonti(summary_idx, "p5", "Quinto percentile", OUT / "13_p5_per_orizzonte.png")

    # ---------------- export ---------------- #
    for name in series:
        slug = {"S&P 500": "sp500", "Nasdaq": "nasdaq", "MSCI World": "world"}[name]
        pd.DataFrame(full_reb[name]).T.to_csv(OUT / f"full_period_{slug}.csv")
        rolling[name]["10y"].to_csv(OUT / f"rolling_10y_{slug}.csv", index=False)

    summary = {
        "slug": SLUG,
        "periodo_comune": {"start": str(lo.date()), "end": str(hi.date())},
        "livelli_leva": LEVELS,
        "costruzione": "leva L = (L-1) in ETF 2x daily + (2-L) in ETF 1x",
        "costi": {"ter_1x": TER_1X, "ter_2x": TER_2X,
                  "funding": "Fed Funds effective mensile + spread calibrato",
                  "spread_calibrato": spread,
                  "lordo_di": "imposte italiane, costi di transazione, spread bid/ask"},
        "calibrazione": cal,
        "dividendo_world_implicito_medio": float(wd_yield.mean()),
        "parametri_rolling": {"finestre_mesi": WINDOWS_MONTHS, "passo_mesi": STEP_MONTHS},
        "indici": summary_idx,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nScritti grafici e summary.json in {OUT}")


if __name__ == "__main__":
    main()
