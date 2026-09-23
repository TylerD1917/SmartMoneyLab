# -*- coding: utf-8 -*-
"""
SmartMoneyLab - Studio: quanto rendono gli indici azionari piu' famosi
al NETTO di TER, tracking difference, bollo titoli e tassazione italiana.

Domanda: rendimento netto su finestre rolling di 1/3/5/10/15/20 anni.
Angle: meno di quanto si legge online.

Metodo
------
- Tutti gli indici in TOTAL RETURN (dividendi reinvestiti), mensile, in EURO.
- MSCI World e MSCI ACWI IMI: serie gia' in EUR dal provider (pre-1999 il
  provider usa il basket ECU/DEM, quindi il "marco come euro sintetico" e'
  gia' incorporato).
- S&P 500, Nasdaq Composite, Russell 2000: serie in USD convertite in EUR con
  un cambio EUR/USD ricostruito e concatenato:
    * 1971-01 .. 1998-12  -> DEM/USD (FRED EXGEUS) invertito a 1.95583 DEM = 1 EUR
    * 1999-01 .. 2003-11  -> EUR/USD ufficiale (FRED DEXUSEU o BCE)
    * 2003-12 .. oggi     -> EURUSD.csv daily (ultimo del mese)
  Il raccordo e' fatto CONCATENANDO I RENDIMENTI mensili e riancorando al
  livello della serie piu' recente, cosi' non si creano salti artificiali.
- Nasdaq Composite e' un indice di PREZZO: dividendo figurato 0.75%/anno
  (stessa convenzione degli articoli "regimi-tassi-sp500-nasdaq" e
  "petrolio-e-mercati-azionari").
- Su ogni indice si costruisce un ETF FINTO: costo annuo continuo =
  TER + tracking difference da ritenuta estera sui dividendi (gli indici sono
  GROSS) + bollo titoli 0.2%/anno, piu' un rumore di tracking error.
- Tassazione: 26% sulla plusvalenza al riscatto finale della finestra.
  Se la finestra chiude in perdita non si paga nulla e la minusvalenza NON
  viene compensata (ipotesi conservativa e realistica per chi ha un solo ETF).
- Finestre rolling a passo MENSILE (sovrapposte), niente rebalancing.

Output in public/charts/rendimenti-netti-indici-azionari/
"""

from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- percorsi
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public" / "charts" / "rendimenti-netti-indici-azionari"
OUT.mkdir(parents=True, exist_ok=True)

DEM_FIX = 1.95583          # DEM per 1 EUR, tasso di conversione irrevocabile
ALIQUOTA = 0.26            # capital gain Italia su ETF armonizzati
BOLLO = 0.0020             # imposta di bollo 0.2%/anno sul controvalore
NASDAQ_DIV = 0.0075        # dividendo figurato Nasdaq Composite
SEED = 20260923
MC_PATHS = 200        # traiettorie per il robustness check sul tracking error

HORIZONS = [1, 3, 5, 10, 15, 20]

# ------------------------------------------------------- definizione ETF
# ter / wht = tracking difference strutturale da ritenuta sui dividendi esteri
# te = tracking error residuo (rumore), deviazione standard annua
ETF = {
    "MSCI World": dict(ter=0.0020, wht=0.0025, te=0.0015),
    "MSCI ACWI IMI": dict(ter=0.0020, wht=0.0025, te=0.0020),
    "S&P 500": dict(ter=0.0007, wht=0.0030, te=0.0010),
    "Nasdaq Composite": dict(ter=0.0030, wht=0.0030, te=0.0020),
    "Russell 2000": dict(ter=0.0030, wht=0.0025, te=0.0025),
}

# ------------------------------------------------------------ utility I/O
def _to_month(idx: pd.Index) -> pd.PeriodIndex:
    return pd.PeriodIndex(pd.to_datetime(idx), freq="M")


def load_msci_eur(path: Path, col: str) -> pd.Series:
    """CSV mensile MSCI: colonna Data in MM/YYYY, valore indice TR in EUR."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(df["Data"], format="%m/%Y")
    s = pd.Series(df[col].astype(float).values, index=pd.PeriodIndex(dates, freq="M"))
    return s.sort_index().dropna()


def load_yahoo_monthly(path: Path) -> pd.Series:
    """CSV daily stile Yahoo (Date,Close,...) -> ultimo valore del mese."""
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.dropna(subset=["Close"]).sort_values("Date")
    s = pd.Series(df["Close"].astype(float).values, index=_to_month(df["Date"]))
    return s.groupby(level=0).last().sort_index()


def load_fred_monthly(path: Path, col: str | None = None) -> pd.Series:
    """CSV FRED (observation_date|DATE, VALORE) -> serie mensile."""
    df = pd.read_csv(path)
    datecol = next(c for c in df.columns if c.lower() in ("observation_date", "date"))
    if col is None:
        col = next(c for c in df.columns if c != datecol)
    df[datecol] = pd.to_datetime(df[datecol])
    v = pd.to_numeric(df[col], errors="coerce")
    s = pd.Series(v.values, index=_to_month(df[datecol])).dropna()
    return s.groupby(level=0).last().sort_index()


# ------------------------------------------------------------ inflazione IT
def build_cpi_it() -> tuple[pd.Series, dict]:
    """Indice CPI Italia mensile da FRED FPCPITOTLZGITA (inflazione % ANNUA).

    Il dato e' annuale, quindi si compone geometricamente dentro l'anno:
    fattore mensile = (1 + a)^(1/12). Si perde la stagionalita' infra-annuale,
    irrilevante su finestre da 1 anno in su. L'ultimo anno disponibile viene
    prolungato per coprire i mesi correnti.
    """
    df = pd.read_csv(DATA / "Valute" / "FPCPITOTLZGITA.csv")
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    rates = pd.Series(pd.to_numeric(df["FPCPITOTLZGITA"], errors="coerce").values / 100.0,
                      index=df["observation_date"].dt.year.values).dropna()

    y0, y1 = int(rates.index.min()), 2027
    months, level, cur = [], [], 1.0
    for y in range(y0, y1 + 1):
        a = float(rates.get(y, rates.iloc[-1]))   # anni non coperti: ultimo noto
        f = (1.0 + a) ** (1 / 12)
        for m in range(1, 13):
            months.append(pd.Period(f"{y}-{m:02d}", freq="M"))
            level.append(cur)
            cur *= f
    cpi = pd.Series(level, index=pd.PeriodIndex(months, freq="M"))
    diag = dict(fonte="FRED FPCPITOTLZGITA (World Bank, inflazione % annua Italia)",
                anni_dato=f"{y0}-{int(rates.index.max())}",
                anni_estrapolati=f"{int(rates.index.max())+1}-{y1} "
                                 f"all'ultimo tasso noto ({rates.iloc[-1]*100:.2f}%)",
                granularita="annuale, composta dentro l'anno")
    return cpi, diag


# ------------------------------------------------------------ cambio EUR/USD
def build_eurusd() -> tuple[pd.Series, dict]:
    """USD per 1 EUR, mensile, il piu' indietro possibile.

    Concatena i rendimenti dei tre segmenti (marco sintetico, EUR/USD
    ufficiale, EURUSD daily) dando priorita' alla fonte piu' recente, poi
    riancora il livello all'ultimo valore osservato di EURUSD.csv.
    """
    segs: list[tuple[str, pd.Series]] = []

    # --- pre-1999: cambio IMPLICITO ricostruito dalle due versioni valutarie
    # della stessa serie MSCI World. Il rapporto USD/EUR di un indice identico
    # E' per costruzione il cambio che il provider ha usato, quindi pre-euro
    # restituisce il basket europeo reale (ECU) e non una sola valuta.
    # Validato nell'era euro contro DEXUSEU: errore mediano 0,00%, max 1,6%.
    # Alternativa scartata: il marco come euro sintetico. Il marco era la
    # valuta europea piu' forte, quindi sovrastima l'euro pre-1999 e
    # sottostima di ~108 bps/anno i rendimenti in euro degli indici in USD.
    w_eur = load_msci_eur(DATA / "Msci_world" / "Msci_world_1969_EUR.csv", "MSCI World")
    w_usd = load_msci_eur(DATA / "Msci_world" / "MSCI_world_historical1969.csv", "MSCI World")
    implied = (w_usd / w_eur).dropna()

    dem = load_fred_monthly(DATA / "Valute" / "DEM_USD_1971_2001.csv")
    dem_eur = DEM_FIX / dem                               # tenuto per confronto

    official = None
    for name in ("DEXUSEU.csv", "EXUSEU.csv", "EURUSD_1999.csv", "EURUSD_ECB.csv"):
        p = DATA / "Valute" / name
        if p.exists():
            official = load_fred_monthly(p)
            segs.append((f"EUR/USD ufficiale ({name})", official))
            break

    daily = load_yahoo_monthly(DATA / "Valute" / "EURUSD.csv")

    # ancoraggio del cambio implicito al livello ufficiale (mediana sull'overlap)
    ref = official if official is not None else daily
    ov = pd.concat([implied.rename("i"), ref.rename("o")], axis=1).dropna()
    k_anchor = float((ov.o / ov.i).median())
    err = (implied * k_anchor / ov.o - 1).reindex(ov.index).abs()
    segs.insert(0, ("MSCI implicito (pre-euro)", implied * k_anchor))
    segs.append(("EURUSD.csv daily", daily))

    # rendimenti mensili, priorita' alla fonte piu' recente
    ret = pd.Series(dtype=float)
    for _, s in segs:                       # ordine: piu' vecchia -> piu' recente
        r = s.pct_change().dropna()
        ret = r.combine_first(ret) if ret.empty else r.combine_first(ret)
    ret = ret.sort_index()

    # riancoraggio al livello reale della serie daily piu' recente
    anchor_period, anchor_value = daily.index[-1], float(daily.iloc[-1])
    level = pd.Series(index=ret.index.union([ret.index[0] - 1]), dtype=float).sort_index()
    cum = (1.0 + ret).cumprod()
    cum = pd.concat([pd.Series({ret.index[0] - 1: 1.0}), cum]).sort_index()
    level = cum / cum.loc[anchor_period] * anchor_value

    # diagnostica buchi
    full = pd.period_range(level.index[0], level.index[-1], freq="M")
    gaps = [str(p) for p in full.difference(level.index)]
    # se c'e' un buco, si tiene SOLO il segmento contiguo finale: una serie
    # bucata produrrebbe pct_change() che salta anni interi come un mese.
    troncata_a = None
    if gaps:
        last_gap = max(full.difference(level.index))
        level = level[level.index > last_gap]
        troncata_a = str(level.index[0])

    # bias del marco sintetico, misurato sul pre-euro
    cmp_ = pd.concat([(implied * k_anchor).rename("imp"), dem_eur.rename("dem")],
                     axis=1).dropna()
    cmp_ = cmp_[cmp_.index < pd.Period("1999-01", freq="M")]
    def _cg(x):
        return (x.iloc[-1] / x.iloc[0]) ** (12 / (len(x) - 1)) - 1

    diag = {
        "segmenti": [n for n, _ in segs],
        "ancoraggio_implicito": round(k_anchor, 6),
        "validazione_implicito_vs_ufficiale": dict(
            mesi_overlap=int(len(ov)),
            errore_mediano_pct=round(float(err.median()) * 100, 3),
            errore_max_pct=round(float(err.max()) * 100, 3)),
        "marco_scartato_bias": dict(
            periodo=f"{cmp_.index[0]} -> {cmp_.index[-1]}",
            implicito_pct_anno=round(float(_cg(cmp_.imp)) * 100, 2),
            marco_pct_anno=round(float(_cg(cmp_.dem)) * 100, 2)),
        "cambio_ufficiale_trovato": official is not None,
        "range_utilizzato": f"{level.index[0]} -> {level.index[-1]}",
        "mesi": int(len(level)),
        "mesi_mancanti": gaps,
        "troncata_dopo_il_buco_a": troncata_a,
    }
    return level.dropna(), diag


# ------------------------------------------------------------ indici in EUR
def build_indices(eurusd: pd.Series) -> dict[str, pd.Series]:
    out: dict[str, pd.Series] = {}

    out["MSCI World"] = load_msci_eur(
        DATA / "Msci_world" / "Msci_world_1969_EUR.csv", "MSCI World")
    out["MSCI ACWI IMI"] = load_msci_eur(
        DATA / "Msci_ACWI_FTSE_all_world" / "Msci_ACWI_IMI_1993_EUR.csv", "MSCI ACWI IMI")

    sp = load_yahoo_monthly(DATA / "Sp500" / "Sp500_TotalReturn1988_USD.csv")
    out["S&P 500"] = (sp / eurusd).dropna()

    # Nasdaq Composite: prezzo -> TR con dividendo figurato
    nq = load_yahoo_monthly(DATA / "Nasdaq" / "Nasdaq_composite1971.csv")
    nq_tr = (1.0 + nq.pct_change().fillna(0.0)) * (1.0 + NASDAQ_DIV) ** (1 / 12)
    nq_tr = nq_tr.cumprod() * 100.0
    out["Nasdaq Composite"] = (nq_tr / eurusd).dropna()

    ru = load_yahoo_monthly(DATA / "Smallcaps" / "Russel2000_Index_1987_$.csv")
    out["Russell 2000"] = (ru / eurusd).dropna()

    return {k: v.sort_index() for k, v in out.items()}


# ------------------------------------------------------------ layer ETF
def etf_series(index_eur: pd.Series, spec: dict, rng: np.random.Generator,
               with_noise: bool = True) -> pd.Series:
    """Dall'indice EUR al NAV dell'ETF finto, al netto dei costi (non tasse)."""
    r = index_eur.pct_change().dropna()
    cost_y = spec["ter"] + spec["wht"] + BOLLO
    drag_m = (1.0 - cost_y) ** (1 / 12)
    if with_noise and spec["te"] > 0:
        eps = rng.normal(0.0, spec["te"] / np.sqrt(12), size=len(r))
    else:
        eps = np.zeros(len(r))
    net = (1.0 + r.values) * drag_m * (1.0 + eps)
    nav = pd.Series(np.concatenate([[1.0], np.cumprod(net)]),
                    index=index_eur.index[: len(net) + 1])
    return nav


def net_after_tax(multiple: np.ndarray) -> np.ndarray:
    """26% sulla plusvalenza; nessun credito se la finestra chiude in perdita."""
    return np.where(multiple > 1.0, 1.0 + (multiple - 1.0) * (1.0 - ALIQUOTA), multiple)


# ------------------------------------------------------------ rolling
def rolling_table(index_eur: pd.Series, nav: pd.Series, label: str,
                  cpi: pd.Series | None = None) -> pd.DataFrame:
    rows = []
    for n in HORIZONS:
        k = n * 12
        if len(nav) <= k:
            continue
        gross = (index_eur.values[k:] / index_eur.values[:-k])
        etf = (nav.values[k:] / nav.values[:-k])
        netm = net_after_tax(etf)

        cagr_gross = gross ** (1 / n) - 1
        cagr_etf = etf ** (1 / n) - 1
        cagr_net = netm ** (1 / n) - 1

        # reale: la tassa del 26% si paga sulla plusvalenza NOMINALE, quindi
        # si deflaziona DOPO. Si paga l'imposta anche sull'inflazione.
        if cpi is not None:
            c = cpi.reindex(nav.index).values
            infl = c[k:] / c[:-k]
            realm = netm / infl
            cagr_real = realm ** (1 / n) - 1
            real_cols = dict(
                reale_p5=np.percentile(cagr_real, 5),
                reale_p25=np.percentile(cagr_real, 25),
                reale_mediana=np.median(cagr_real),
                reale_p75=np.percentile(cagr_real, 75),
                reale_p95=np.percentile(cagr_real, 95),
                reale_moltiplicatore_mediano=np.median(realm),
                quota_finestre_negative_reale=float((realm < 1.0).mean()),
                inflazione_mediana=np.median(infl ** (1 / n) - 1))
        else:
            real_cols = {}

        rows.append(dict(
            indice=label, anni=n, finestre=len(netm),
            da=str(nav.index[0]), a=str(nav.index[-1]),
            lordo_mediana=np.median(cagr_gross),
            netto_p5=np.percentile(cagr_net, 5),
            netto_p25=np.percentile(cagr_net, 25),
            netto_mediana=np.median(cagr_net),
            netto_p75=np.percentile(cagr_net, 75),
            netto_p95=np.percentile(cagr_net, 95),
            netto_moltiplicatore_mediano=np.median(netm),
            lordo_moltiplicatore_mediano=np.median(gross),
            erosione_pp=np.median(cagr_gross) - np.median(cagr_net),
            solo_costi_pp=np.median(cagr_gross) - np.median(cagr_etf),
            solo_tasse_pp=np.median(cagr_etf) - np.median(cagr_net),
            quota_finestre_negative_netto=float((netm < 1.0).mean()),
            **real_cols,
        ))
    return pd.DataFrame(rows)


# ------------------------------------------------------------ main
def main() -> None:
    cpi, cpi_diag = build_cpi_it()
    print("=== INFLAZIONE ITALIA ===")
    print(json.dumps(cpi_diag, indent=2, ensure_ascii=False))

    eurusd, fx_diag = build_eurusd()
    print("=== CAMBIO EUR/USD ===")
    print(json.dumps(fx_diag, indent=2, ensure_ascii=False))
    if fx_diag["mesi_mancanti"]:
        print("!! ATTENZIONE: buchi nel cambio ->", fx_diag["mesi_mancanti"][:3], "...")
    if not fx_diag["cambio_ufficiale_trovato"]:
        print("!! Manca il file EUR/USD ufficiale 1999-2003 in data/Valute/ "
              "(DEXUSEU.csv). Le serie in USD partiranno dal 2003-12.")

    indices = build_indices(eurusd)
    print("\n=== COPERTURA INDICI (EUR, TR mensile) ===")
    cov = []
    for k, v in indices.items():
        anni = len(v) / 12
        cagr = (v.iloc[-1] / v.iloc[0]) ** (1 / anni) - 1
        cov.append(dict(indice=k, da=str(v.index[0]), a=str(v.index[-1]),
                        mesi=len(v), anni=round(anni, 1),
                        cagr_lordo_eur=round(cagr * 100, 2)))
    cov_df = pd.DataFrame(cov)
    print(cov_df.to_string(index=False))

    # --- scenario base: DETERMINISTICO (TER + ritenuta + bollo, no rumore)
    tables = []
    for k, v in indices.items():
        nav = etf_series(v, ETF[k], np.random.default_rng(SEED), with_noise=False)
        tables.append(rolling_table(v, nav, k, cpi))
    res = pd.concat(tables, ignore_index=True)

    pct = ["lordo_mediana", "netto_p5", "netto_p25", "netto_mediana",
           "netto_p75", "netto_p95", "erosione_pp", "solo_costi_pp",
           "solo_tasse_pp", "quota_finestre_negative_netto",
           "reale_p5", "reale_p25", "reale_mediana", "reale_p75", "reale_p95",
           "quota_finestre_negative_reale", "inflazione_mediana"]
    show = res.copy()
    for c in pct:
        show[c] = (show[c] * 100).round(2)
    for c in ("netto_moltiplicatore_mediano", "reale_moltiplicatore_mediano"):
        show[c] = show[c].round(3)
    show["lordo_moltiplicatore_mediano"] = show["lordo_moltiplicatore_mediano"].round(3)

    print("\n=== RISULTATI (CAGR in %, finestre rolling passo mensile) ===")
    for k in indices:
        print(f"\n--- {k} ---")
        sub = show[show.indice == k][[
            "anni", "finestre", "lordo_mediana", "netto_p5", "netto_p25",
            "netto_mediana", "netto_p75", "netto_p95",
            "netto_moltiplicatore_mediano", "erosione_pp",
            "solo_costi_pp", "solo_tasse_pp", "quota_finestre_negative_netto"]]
        print(sub.to_string(index=False))

    # --- tabella B: PERIODO COMUNE a tutti e cinque gli indici.
    # Serve perche' le storie sono di lunghezza diversa: confrontare l'ACWI IMI
    # a 20 anni (finestre che partono solo 1994-2006, tutte a cavallo della
    # dotcom) con il MSCI World a 20 anni (finestre dal 1969) misura il
    # periodo, non l'indice.
    start = max(v.index[0] for v in indices.values())
    end = min(v.index[-1] for v in indices.values())
    print(f"\n=== TABELLA B: periodo comune {start} -> {end} "
          f"({(end - start).n / 12:.1f} anni) ===")
    tables_c = []
    for k, v in indices.items():
        vc = v[(v.index >= start) & (v.index <= end)]
        nav = etf_series(vc, ETF[k], np.random.default_rng(SEED), with_noise=False)
        tables_c.append(rolling_table(vc, nav, k, cpi))
    resc = pd.concat(tables_c, ignore_index=True)
    showc = resc.copy()
    for c in pct:
        showc[c] = (showc[c] * 100).round(2)
    for c in ("netto_moltiplicatore_mediano", "reale_moltiplicatore_mediano"):
        showc[c] = showc[c].round(3)
    for n in HORIZONS:
        sub = showc[showc.anni == n]
        if sub.empty:
            continue
        print(f"\n  [{n} anni, {int(sub.finestre.iloc[0])} finestre]")
        print(sub[["indice", "lordo_mediana", "netto_p5", "netto_p25",
                   "netto_mediana", "netto_p75", "netto_p95",
                   "netto_moltiplicatore_mediano", "erosione_pp"]].to_string(index=False))
    print(f"\n=== TABELLA D: REALE sul periodo comune {start} -> {end} ===")
    for n in HORIZONS:
        sub = showc[showc.anni == n]
        if sub.empty:
            continue
        print(f"\n  [{n} anni, {int(sub.finestre.iloc[0])} finestre]")
        print(sub[["indice", "netto_mediana", "reale_p5", "reale_p25",
                   "reale_mediana", "reale_p75", "reale_p95",
                   "reale_moltiplicatore_mediano",
                   "quota_finestre_negative_reale"]].to_string(index=False))
    resc.to_csv(OUT / "rolling_netto_periodo_comune.csv", index=False)

    # --- tabella C: REALE (netto di costi, tasse e inflazione italiana)
    print("\n=== TABELLA C: NETTO REALE (massima storicita' per indice) ===")
    for k in indices:
        sub = show[show.indice == k][[
            "anni", "netto_mediana", "inflazione_mediana", "reale_p5",
            "reale_p25", "reale_mediana", "reale_p75", "reale_p95",
            "reale_moltiplicatore_mediano", "quota_finestre_negative_reale"]]
        print(f"\n--- {k} ---")
        print(sub.to_string(index=False))

    # --- robustness check: tracking error casuale su N traiettorie
    mc_rows = []
    for k, v in indices.items():
        spec = ETF[k]
        rng = np.random.default_rng(SEED)
        meds = {n: [] for n in HORIZONS}
        for _ in range(MC_PATHS):
            nav = etf_series(v, spec, rng, with_noise=True)
            for n in HORIZONS:
                kk = n * 12
                if len(nav) <= kk:
                    continue
                m = net_after_tax(nav.values[kk:] / nav.values[:-kk])
                meds[n].append(np.median(m ** (1 / n) - 1))
        base = res[res.indice == k].set_index("anni")["netto_mediana"]
        for n in HORIZONS:
            if not meds[n]:
                continue
            a = np.array(meds[n])
            mc_rows.append(dict(
                indice=k, anni=n,
                base_deterministica_pct=round(float(base.loc[n]) * 100, 3),
                mc_media_pct=round(float(a.mean()) * 100, 3),
                mc_dev_std_bps=round(float(a.std(ddof=1)) * 10000, 2),
                mc_p5_pct=round(float(np.percentile(a, 5)) * 100, 3),
                mc_p95_pct=round(float(np.percentile(a, 95)) * 100, 3),
                scarto_medio_bps=round(float(a.mean() - base.loc[n]) * 10000, 2)))
    mc = pd.DataFrame(mc_rows)
    print(f"\n=== ROBUSTNESS: tracking error casuale, {MC_PATHS} traiettorie ===")
    print(mc.to_string(index=False))
    print(f"\n[sintesi] scarto medio MC vs base deterministica: "
          f"{mc.scarto_medio_bps.abs().mean():.2f} bps (max "
          f"{mc.scarto_medio_bps.abs().max():.2f}); dev.std tipica "
          f"{mc.mc_dev_std_bps.median():.2f} bps")
    mc.to_csv(OUT / "robustness_tracking_error.csv", index=False)
    delta = float(mc.scarto_medio_bps.abs().max())

    res.to_csv(OUT / "rolling_netto.csv", index=False)
    cov_df.to_csv(OUT / "copertura_serie.csv", index=False)
    eurusd.rename("EURUSD").to_frame().assign(
        mese=eurusd.index.astype(str)).to_csv(OUT / "eurusd_ricostruito.csv", index=False)

    summary = dict(
        generato=str(pd.Timestamp.today().date()),
        ipotesi=dict(aliquota=ALIQUOTA, bollo=BOLLO, nasdaq_div_figurato=NASDAQ_DIV,
                     etf=ETF, passo="mensile", horizons=HORIZONS,
                     minusvalenze_compensate=False, rebalancing=None),
        cambio=fx_diag,
        inflazione=cpi_diag,
        copertura=cov,
        tracking_error_scarto_max_bps=round(float(delta), 2),
        scenario_base="deterministico (TER + ritenuta estera + bollo), nessun rumore",
        mc_paths=MC_PATHS,
    )
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nScritti: {OUT}")


if __name__ == "__main__":
    main()
