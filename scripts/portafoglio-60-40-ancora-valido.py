"""
Il portafoglio 60/40 (e l'80/20) funziona ancora?

Investitore italiano, tutto in euro, rendimenti lordi total return mensili a fine mese.
Coppie testate:
  Euro    MSCI World + obbligazioni governative a duration costante area euro 7-10 (dal 1971)
          MSCI World + BTP 7-10 (dal 1980)
  USA     S&P 500 + Treasury USA 7-10, entrambi convertiti in euro senza copertura (dal 1971)
Benchmark: 100% MSCI World e 100% S&P 500, in euro.
Ogni misto in due versioni: buy & hold puro (i pesi derivano) e ribilanciamento ogni 12 mesi
(lordo di costi e tasse del ribilanciamento, quindi un po' ottimistico).
Finestre mobili di 5, 10 e 20 anni con passo di 3 mesi, piu' l'intero periodo.
Tasso privo di rischio per Sharpe e Sortino: interbancario tedesco a 3 mesi (FRED
IR3TIB01DEM156N), di fatto l'Euribor dopo il 1999.

    python scripts/portafoglio-60-40-ancora-valido.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SLUG = "portafoglio-60-40-ancora-valido"
OUT = ROOT / "public" / "charts" / SLUG
OUT.mkdir(parents=True, exist_ok=True)

START, END = "1971-01", "2025-12"
WINDOWS = {"5y": 60, "10y": 120, "20y": 240}
STEP = 3


# ------------------------------------------------------------------ dati
def _yahoo_eom(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    s = pd.to_numeric(df["Close"], errors="coerce").dropna().sort_index()
    s = s.resample("ME").last()
    s.index = s.index.to_period("M")
    return s


def _msci(path: Path) -> pd.Series:
    d = pd.read_csv(path)
    d.columns = ["d", "v"]
    s = pd.Series(d["v"].astype(float).values, index=pd.PeriodIndex(pd.to_datetime(d["d"], format="%m/%Y"), freq="M"))
    return s


def carica() -> tuple[pd.DataFrame, dict]:
    chk = {}
    w_usd = _msci(DATA / "Msci_world" / "MSCI_world_historical1969.csv")
    w_eur = _msci(DATA / "Msci_world" / "Msci_world_1969_EUR.csv")
    # cambio implicito: rapporto fra le due versioni valutarie dello stesso indice MSCI (fine mese)
    ratio = (w_eur / w_usd).dropna()
    fx_ret = ratio.pct_change()  # >0 = il dollaro si rafforza contro l'euro

    # controllo: dal 1999 il cambio implicito deve seguire il cambio BCE a fine mese
    ecb = pd.read_csv(DATA / "Valute" / "DEXUSEU.csv", parse_dates=["observation_date"], na_values=".")
    ecb = ecb.set_index("observation_date")["DEXUSEU"].dropna().resample("ME").last()
    ecb.index = ecb.index.to_period("M")
    usd_per_eur_ret = (1 / ecb).pct_change()
    j = pd.concat([fx_ret, usd_per_eur_ret], axis=1).dropna().loc["1999-02":]
    chk["corr_cambio_implicito_vs_bce"] = float(j.corr().iloc[0, 1])
    chk["scarto_medio_cambio_pp"] = float((j.iloc[:, 0] - j.iloc[:, 1]).abs().mean() * 100)

    # S&P 500 total return a fine mese, in dollari
    tr = _yahoo_eom(DATA / "Sp500" / "Sp500_TotalReturn1988_USD.csv")
    # ^GSPC giornaliero: il file "1927" in realta' parte dal 1975, la parte precedente e' in un file a parte
    px = pd.concat([_yahoo_eom(DATA / "Sp500" / "Sp500_daily_1928_1974_GSPC.csv"),
                    _yahoo_eom(DATA / "Sp500" / "Sp500_daily_1927_GSPC.csv")])
    px = px[~px.index.duplicated(keep="last")].sort_index()
    sh = pd.read_csv(DATA / "Sp500" / "shiller_mirror.csv", parse_dates=["Date"]).set_index("Date")
    div = pd.to_numeric(sh["Dividend"], errors="coerce")
    yld = (div / 12 / pd.to_numeric(sh["SP500"], errors="coerce")).where(div > 0)
    yld.index = yld.index.to_period("M")
    r_pre = px.pct_change() + yld.shift(1).reindex(px.index)
    r_post = tr.pct_change()
    # controllo d'incollatura sul periodo comune
    comune = pd.concat([r_pre, r_post], axis=1).dropna()
    cagr = lambda r: float((1 + r).prod() ** (12 / len(r)) - 1)
    chk["sp500_cagr_tr_ufficiale"] = cagr(comune.iloc[:, 1])
    chk["sp500_cagr_ricostruito"] = cagr(comune.iloc[:, 0])
    assert abs(chk["sp500_cagr_tr_ufficiale"] - chk["sp500_cagr_ricostruito"]) < 0.0025, "incollatura S&P oltre 0,25 pp"
    sp_usd = pd.concat([r_pre.loc[:"1988-01"], r_post.loc["1988-02":]])

    # obbligazioni a duration costante (base 100 alla prima data di ciascuna colonna)
    b = pd.read_csv(DATA / "Bonds" / "indici_duration_costante" / "nav_duration_costante.csv")
    b.index = pd.PeriodIndex(b.pop("mese"), freq="M")
    bret = b.pct_change()

    # tasso privo di rischio in euro
    rf = pd.read_csv(DATA / "Bonds" / "IR3TIB01DEM156N_Germania3M_fred_1960.csv", parse_dates=["observation_date"])
    rf = rf.set_index("observation_date").iloc[:, 0].astype(float) / 100
    rf.index = rf.index.to_period("M")
    rf_m = ((1 + rf) ** (1 / 12) - 1).shift(1)  # tasso noto a inizio mese

    to_eur = lambda r_usd: (1 + r_usd) * (1 + fx_ret) - 1

    # BTP: prima del 1999 l'indice e' in lire. Va portato nella stessa unita' dell'MSCI World in
    # euro, che prima del 1999 e' un euro sintetico (si deprezza contro il dollaro molto meno del
    # marco: e' un paniere, non il marco). Unita' euro-MSCI per lira = rapporto implicito / lire per
    # dollaro. Senza questa conversione il BTP degli anni '80 incasserebbe le cedole alte della lira
    # senza pagarne la svalutazione. Dal 1999 la lira e' fissa e il BTP e' gia' in euro.
    itl = pd.read_csv(DATA / "Valute" / "EXITUS_lira_usd_fred_1971.csv", parse_dates=["observation_date"])
    itl = itl.set_index("observation_date").iloc[:, 0].astype(float)
    itl.index = itl.index.to_period("M")
    eur_per_itl = (ratio / itl).dropna()
    btp = bret["Italia 7-10"].copy()
    pre = btp.index < pd.Period("1999-01", "M")
    btp[pre] = (1 + btp[pre]) * (1 + eur_per_itl.pct_change().reindex(btp.index[pre])) - 1
    chk["btp_cagr_lire_1980_1998"] = float((1 + bret["Italia 7-10"].loc["1980-04":"1998-12"]).prod() ** (12 / 225) - 1)
    chk["btp_cagr_euro_1980_1998"] = float((1 + btp.loc["1980-04":"1998-12"]).prod() ** (12 / 225) - 1)
    # Treasury coperto dal cambio: rendimento in dollari piu' il differenziale fra tasso a 3 mesi
    # in euro e in dollari (e' cio' che guadagna o paga un ETF EUR hedged rinnovando i forward)
    us = pd.read_csv(DATA / "Bonds" / "IR3TIB01USM156N_USA3M_fred_1964.csv", parse_dates=["observation_date"])
    us = us.set_index("observation_date").iloc[:, 0].astype(float).interpolate() / 100  # aprile 2020 manca in FRED
    us.index = us.index.to_period("M")
    rf_us_m = ((1 + us) ** (1 / 12) - 1).shift(1)
    ust_hedged = (1 + bret["USA 7-10"]) * (1 + rf_m - rf_us_m) - 1

    df = pd.DataFrame({
        "world": w_eur.pct_change(),
        "sp500": to_eur(sp_usd),
        "bund_ez": bret["Area euro 7-10"],
        "btp": btp,
        "ust": to_eur(bret["USA 7-10"]),
        "ust_h": ust_hedged,
        "rf": rf_m,
    }).loc[START:END]
    chk["periodo"] = f"{df.index[0]} - {df.index[-1]}"
    chk["mesi_mancanti"] = {c: int(df[c].isna().sum()) for c in df}
    return df, chk


# ------------------------------------------------------------------ motore
def nav(r_eq: np.ndarray, r_bd: np.ndarray | None, w: float, ribilancia: bool) -> np.ndarray:
    """Valore del portafoglio a fine di ogni mese, partenza 1. Ribilanciamento ogni 12 mesi."""
    if r_bd is None or w == 1.0:
        return np.cumprod(1 + r_eq)
    n = len(r_eq)
    out = np.empty(n)
    a, b = w, 1 - w
    for i in range(n):
        a *= 1 + r_eq[i]; b *= 1 + r_bd[i]
        out[i] = a + b
        if ribilancia and (i + 1) % 12 == 0:
            a, b = w * out[i], (1 - w) * out[i]
    return out


def metriche(v: np.ndarray, rf: np.ndarray) -> dict:
    r = np.diff(np.concatenate([[1.0], v])) / np.concatenate([[1.0], v[:-1]])
    n = len(r)
    ex = r - rf
    dd = v / np.maximum.accumulate(np.concatenate([[1.0], v]))[1:] - 1
    cagr = v[-1] ** (12 / n) - 1
    vol = r.std(ddof=1) * np.sqrt(12)
    down = np.sqrt(np.mean(np.minimum(ex, 0) ** 2)) * np.sqrt(12)
    mdd = dd.min()
    return {"cagr": cagr, "vol": vol, "mdd": mdd,
            "sharpe": ex.mean() * 12 / (ex.std(ddof=1) * np.sqrt(12)),
            "sortino": ex.mean() * 12 / down if down > 0 else np.nan,
            "calmar": cagr / abs(mdd) if mdd < 0 else np.nan,
            "rf_cagr": float(np.prod(1 + rf) ** (12 / n) - 1)}


def portafogli(df: pd.DataFrame) -> dict:
    """nome -> (gamba azionaria, gamba obbligazionaria, peso azioni, ribilancia, inizio)."""
    P = {"100% MSCI World": ("world", None, 1.0, False, START),
         "100% S&P 500": ("sp500", None, 1.0, False, START)}
    for w in (0.6, 0.8):
        lab = f"{int(w * 100)}/{int(round((1 - w) * 100))}"
        for bd, nome, start, eq in (("bund_ez", "World + gov. euro", START, "world"),
                                    ("btp", "World + BTP", "1980-04", "world"),
                                    ("ust", "S&P + Treasury", START, "sp500"),
                                    ("ust_h", "S&P + Treasury coperto", START, "sp500")):
            for reb in (False, True):
                P[f"{lab} {nome} ({'ribil.' if reb else 'B&H'})"] = (eq, bd, w, reb, start)
    return P


def analisi(df: pd.DataFrame) -> dict:
    P = portafogli(df)
    res = {"intero": {}, "rolling": {}, "start_sens": {}, "rolling_raw": {}}
    # intero periodo (dal proprio inizio) + versione 1980 comune a tutti
    for nome, (eq, bd, w, reb, st) in P.items():
        for etichetta, s0 in (("proprio", st), ("dal_1980", "1980-04")):
            d = df.loc[s0:]
            v = nav(d[eq].values, d[bd].values if bd else None, w, reb)
            res["intero"].setdefault(nome, {})[etichetta] = metriche(v, d["rf"].values) | {"inizio": str(d.index[0])}
    # finestre mobili
    for win, m in WINDOWS.items():
        for nome, (eq, bd, w, reb, st) in P.items():
            d = df.loc[st:]
            E, B, RF = d[eq].values, (d[bd].values if bd else None), d["rf"].values
            rows = []
            for s in range(0, len(d) - m + 1, STEP):
                v = nav(E[s:s + m], B[s:s + m] if B is not None else None, w, reb)
                rows.append({"inizio": str(d.index[s])} | metriche(v, RF[s:s + m]))
            res["rolling_raw"].setdefault(win, {})[nome] = pd.DataFrame(rows)
    # sensibilita' alla data di partenza (intero periodo fino a END)
    for s0 in ("1971-01", "1980-04", "1990-01", "2000-01", "2010-01"):
        for nome, (eq, bd, w, reb, st) in P.items():
            if pd.Period(s0) < pd.Period(st):
                continue
            d = df.loc[s0:]
            v = nav(d[eq].values, d[bd].values if bd else None, w, reb)
            mt = metriche(v, d["rf"].values)
            res["start_sens"].setdefault(nome, {})[s0] = {k: mt[k] for k in ("cagr", "sharpe", "sortino", "mdd")}
    return res


def riassunto_rolling(res: dict) -> dict:
    out = {}
    for win, tabs in res["rolling_raw"].items():
        for nome, t in tabs.items():
            q = lambda c, p: float(np.nanpercentile(t[c], p))
            bench = "100% S&P 500" if nome.startswith(("60/40 S&P", "80/20 S&P")) else "100% MSCI World"
            b = tabs[bench].set_index("inizio")
            tt = t.set_index("inizio")
            comuni = tt.index.intersection(b.index)
            out.setdefault(win, {})[nome] = {
                "n": len(t),
                "cagr_mediana": q("cagr", 50), "cagr_media": float(t["cagr"].mean()),
                "cagr_p5": q("cagr", 5), "cagr_p10": q("cagr", 10), "cagr_min": float(t["cagr"].min()),
                "quota_negative": float((t["cagr"] < 0).mean()),
                "vol_mediana": q("vol", 50),
                "mdd_mediana": q("mdd", 50), "mdd_peggiore": float(t["mdd"].min()),
                "quota_mdd_oltre_30": float((t["mdd"] < -0.30).mean()),
                "sharpe_mediana": q("sharpe", 50), "sortino_mediana": q("sortino", 50),
                "calmar_mediana": q("calmar", 50),
                "benchmark": bench,
                "batte_bench_cagr": float((tt.loc[comuni, "cagr"] > b.loc[comuni, "cagr"]).mean()) if nome != bench else None,
                "batte_bench_sharpe": float((tt.loc[comuni, "sharpe"] > b.loc[comuni, "sharpe"]).mean()) if nome != bench else None,
                "batte_bench_sortino": float((tt.loc[comuni, "sortino"] > b.loc[comuni, "sortino"]).mean()) if nome != bench else None,
                "batte_world_cagr": float((tt.loc[tt.index.intersection(tabs["100% MSCI World"].set_index("inizio").index), "cagr"]
                                           > tabs["100% MSCI World"].set_index("inizio").loc[tt.index.intersection(tabs["100% MSCI World"].set_index("inizio").index), "cagr"]).mean()),
            }
    return out


def correlazioni(df: pd.DataFrame) -> dict:
    out = {}
    for eq, bd in (("world", "bund_ez"), ("world", "btp"), ("sp500", "ust"), ("sp500", "ust_h")):
        d = df[[eq, bd]].dropna()
        roll = d[eq].rolling(36).corr(d[bd])
        out[f"{eq}-{bd}"] = {"intero": float(d.corr().iloc[0, 1]),
                             "per_decennio": {str(y): float(d.loc[f"{y}-01":f"{y + 9}-12"].corr().iloc[0, 1])
                                              for y in range(1971 if bd != "btp" else 1980, 2021, 10)},
                             "rolling36_min": float(roll.min()), "rolling36_max": float(roll.max()),
                             "rolling36_ultimo": float(roll.dropna().iloc[-1])}
    return out


# ------------------------------------------------------------------ grafici
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt

NAVY, AZZ, ORO, ROSSO, VERDE, GRIGIO, NERO = "#1e3a8a", "#7b93d1", "#d97706", "#dc2626", "#047857", "#94a3b8", "#334155"
PRINCIPALI = {  # etichetta nel grafico -> (portafoglio, colore, stile)
    "100% MSCI World": ("100% MSCI World", NERO, "-"),
    "100% S&P 500": ("100% S&P 500", GRIGIO, "--"),
    "60/40 World + titoli di Stato euro": ("60/40 World + gov. euro (ribil.)", NAVY, "-"),
    "80/20 World + titoli di Stato euro": ("80/20 World + gov. euro (ribil.)", AZZ, "-"),
    "60/40 World + BTP": ("60/40 World + BTP (ribil.)", VERDE, "-"),
    "60/40 S&P + Treasury in dollari": ("60/40 S&P + Treasury (ribil.)", ROSSO, "-"),
    "60/40 S&P + Treasury coperto": ("60/40 S&P + Treasury coperto (ribil.)", ORO, "-"),
}


def it(x, d=1):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def _stile(ax, titolo, ylab=""):
    ax.set_title(titolo, fontsize=13, fontweight="bold", color="#0f172a", loc="left", pad=12)
    ax.set_ylabel(ylab, fontsize=10, color="#475569")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#e2e8f0", lw=0.8)
    ax.tick_params(labelsize=9, colors="#475569")


def _fonte(fig, testo="Elaborazione SmartMoneyLab su dati MSCI, S&P, OCSE, FRED. Rendimenti lordi total return in euro."):
    fig.text(0.01, 0.01, testo, fontsize=7.5, color="#94a3b8")


def grafici(df, res, summary):
    P = portafogli(df)
    # 1) crescita di 1 euro dal 1971 (scala log)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    finali = []
    for lab, (nome, col, ls) in PRINCIPALI.items():
        eq, bd, w, reb, st = P[nome]
        if st != START:  # il 60/40 con BTP parte nel 1980: non sta su questo grafico
            continue
        d = df.loc[st:]
        v = nav(d[eq].values, d[bd].values if bd else None, w, reb)
        x = d.index.to_timestamp()
        ax.plot(x, v, color=col, ls=ls, lw=2.2 if "60/40 World + t" in lab else 1.5, label=lab)
        finali.append((np.log(v[-1]), v[-1], col))
    # etichette finali distanziate in scala logaritmica
    finali.sort(); pos, ult = [], -9
    for ly, val, col in finali:
        ly2 = max(ly, ult + 0.13); pos.append((ly2, val, col)); ult = ly2
    for ly2, val, col in pos:
        ax.annotate(f"{it(val, 0)} €", (x[-1], np.exp(ly2)), xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=col, va="center")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda y, _: f"{it(y, 0)} €"))
    _stile(ax, "Crescita di 1 euro, gennaio 1971 - dicembre 2025 (ribilanciati ogni anno, scala logaritmica)")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    _fonte(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "01_crescita_1971.png", dpi=160); plt.close(fig)

    # 2) distribuzione del rendimento annuo sulle finestre di 10 e 20 anni
    for win in ("10y", "20y"):
        fig, ax = plt.subplots(figsize=(11, 5.6))
        labs = list(PRINCIPALI)
        dati = [res["rolling_raw"][win][PRINCIPALI[l][0]]["cagr"].values * 100 for l in labs]
        bp = ax.boxplot(dati, whis=(5, 95), showfliers=False, patch_artist=True, widths=0.55,
                        medianprops=dict(color="white", lw=2))
        for b, l in zip(bp["boxes"], labs):
            b.set_facecolor(PRINCIPALI[l][1]); b.set_edgecolor(PRINCIPALI[l][1])
        for i, dd in enumerate(dati, 1):
            ax.text(i, np.percentile(dd, 50), it(np.percentile(dd, 50)) + "%", ha="center", va="bottom",
                    fontsize=8, color="#0f172a", fontweight="bold")
        ax.axhline(0, color="#475569", lw=0.8)
        ax.set_xticks(range(1, len(labs) + 1))
        ax.set_xticklabels([l.replace(" + ", "\n+ ") for l in labs], fontsize=8)
        ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda y, _: f"{it(y, 0)}%"))
        anni = win[:-1]
        _stile(ax, f"Rendimento annuo composto su tutte le finestre di {anni} anni (box 25-75%, baffi 5-95%)")
        _fonte(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / f"02_rendimenti_{win}.png", dpi=160); plt.close(fig)

    # 3) quante finestre battono il benchmark: rendimento contro Sharpe
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.4), sharey=True)
    coppie = [("60/40 titoli euro", "60/40 World + gov. euro (ribil.)"), ("80/20 titoli euro", "80/20 World + gov. euro (ribil.)"),
              ("60/40 BTP", "60/40 World + BTP (ribil.)"), ("60/40 Treasury $", "60/40 S&P + Treasury (ribil.)"),
              ("60/40 Treasury coperto", "60/40 S&P + Treasury coperto (ribil.)")]
    for ax, win in zip(axs, ("10y", "20y")):
        R = summary["rolling"][win]
        x = np.arange(len(coppie)); w = 0.38
        a = [R[n]["batte_bench_cagr"] * 100 for _, n in coppie]
        b = [R[n]["batte_bench_sharpe"] * 100 for _, n in coppie]
        ax.bar(x - w / 2, a, w, color=GRIGIO, label="rende di più")
        ax.bar(x + w / 2, b, w, color=NAVY, label="Sharpe migliore")
        for xi, (va, vb) in enumerate(zip(a, b)):
            ax.text(xi - w / 2, va + 1, f"{va:.0f}%", ha="center", fontsize=8)
            ax.text(xi + w / 2, vb + 1, f"{vb:.0f}%", ha="center", fontsize=8, color=NAVY, fontweight="bold")
        ax.axhline(50, color="#475569", lw=0.8, ls=":")
        ax.set_xticks(x); ax.set_xticklabels([c[0].replace(" ", "\n", 1) for c in coppie], fontsize=8)
        ax.set_ylim(0, 110)
        _stile(ax, f"Finestre di {win[:-1]} anni")
    axs[0].set_ylabel("% di finestre in cui il misto batte il 100% azionario", fontsize=9, color="#475569")
    axs[0].legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.suptitle("Quante volte il misto batte il 100% azionario (World per le coppie euro, S&P 500 per quelle USA)",
                 fontsize=12.5, fontweight="bold", x=0.01, ha="left", color="#0f172a")
    _fonte(fig); fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig(OUT / "03_quante_volte_batte.png", dpi=160); plt.close(fig)

    # 4) quota di finestre di 10 anni con perdita massima oltre il 30%, B&H contro ribilanciato
    fig, ax = plt.subplots(figsize=(11, 5))
    voci = [("100% World", "100% MSCI World", None), ("100% S&P 500", "100% S&P 500", None),
            ("60/40 titoli euro", "60/40 World + gov. euro (B&H)", "60/40 World + gov. euro (ribil.)"),
            ("80/20 titoli euro", "80/20 World + gov. euro (B&H)", "80/20 World + gov. euro (ribil.)"),
            ("60/40 BTP", "60/40 World + BTP (B&H)", "60/40 World + BTP (ribil.)"),
            ("60/40 Treasury $", "60/40 S&P + Treasury (B&H)", "60/40 S&P + Treasury (ribil.)"),
            ("60/40 Treasury coperto", "60/40 S&P + Treasury coperto (B&H)", "60/40 S&P + Treasury coperto (ribil.)")]
    R = summary["rolling"]["10y"]; x = np.arange(len(voci)); w = 0.38
    for i, (lab, bh, rb) in enumerate(voci):
        v1 = R[bh]["quota_mdd_oltre_30"] * 100
        if rb is None:
            ax.bar(i, v1, 0.5, color=NERO); ax.text(i, v1 + 1.5, f"{v1:.0f}%", ha="center", fontsize=8.5)
        else:
            v2 = R[rb]["quota_mdd_oltre_30"] * 100
            ax.bar(i - w / 2, v1, w, color=GRIGIO, label="buy & hold" if i == 2 else None)
            ax.bar(i + w / 2, v2, w, color=NAVY, label="ribilanciato ogni anno" if i == 2 else None)
            ax.text(i - w / 2, v1 + 1.5, f"{v1:.0f}%", ha="center", fontsize=8.5)
            ax.text(i + w / 2, v2 + 1.5, f"{v2:.0f}%", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([v[0] for v in voci], fontsize=8.5); ax.set_ylim(0, 80)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    _stile(ax, "Finestre di 10 anni in cui il portafoglio ha perso più del 30% dal massimo, almeno una volta")
    ax.legend(fontsize=8.5, frameon=False)
    _fonte(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "04_perdite_oltre_30.png", dpi=160); plt.close(fig)

    # 5) quanto pesa l'anno di partenza
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
    starts = ["1971-01", "1980-04", "1990-01", "2000-01", "2010-01"]
    lab_st = ["dal 1971", "dal 1980", "dal 1990", "dal 2000", "dal 2010"]
    serie = [("100% MSCI World", NERO), ("60/40 World + gov. euro (ribil.)", NAVY), ("80/20 World + gov. euro (ribil.)", AZZ)]
    for ax, met, tit in ((axs[0], "cagr", "Rendimento annuo fino a fine 2025"), (axs[1], "sharpe", "Indice di Sharpe")):
        x = np.arange(len(starts)); w = 0.26
        for k, (nome, col) in enumerate(serie):
            vals = [summary["start_sens"][nome][s][met] * (100 if met == "cagr" else 1) for s in starts]
            ax.bar(x + (k - 1) * w, vals, w, color=col, label=nome.replace(" (ribil.)", "").replace("gov. euro", "titoli di Stato euro"))
            for xi, v in zip(x, vals):
                ax.text(xi + (k - 1) * w, v + (0.15 if met == "cagr" else 0.015), it(v, 1 if met == "cagr" else 2),
                        ha="center", fontsize=7, color=col)
        ax.set_xticks(x); ax.set_xticklabels(lab_st, fontsize=9)
        _stile(ax, tit)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=8.5, frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.04))
    _fonte(fig); fig.tight_layout(rect=(0, 0.1, 1, 1)); fig.savefig(OUT / "05_anno_di_partenza.png", dpi=160); plt.close(fig)

    # 6) correlazione mobile a 36 mesi fra azioni e obbligazioni
    fig, ax = plt.subplots(figsize=(11, 5))
    for eq, bd, lab, col in (("world", "bund_ez", "MSCI World e titoli di Stato euro", NAVY),
                             ("sp500", "ust", "S&P 500 e Treasury in dollari (visti in euro)", ROSSO),
                             ("sp500", "ust_h", "S&P 500 e Treasury coperto", ORO)):
        c = df[eq].rolling(36).corr(df[bd]).dropna()
        ax.plot(c.index.to_timestamp(), c.values, color=col, lw=1.6, label=lab)
    ax.axhline(0, color="#475569", lw=0.8)
    ax.set_ylim(-0.8, 0.9)
    _stile(ax, "Correlazione mobile a 36 mesi fra la gamba azionaria e quella obbligazionaria")
    ax.legend(fontsize=8.5, frameon=False, loc="lower left")
    _fonte(fig); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "06_correlazione.png", dpi=160); plt.close(fig)


def main():
    df, chk = carica()
    res = analisi(df)
    summary = {"controlli": chk, "intero": res["intero"], "start_sens": res["start_sens"],
               "rolling": riassunto_rolling(res), "correlazioni": correlazioni(df),
               "cagr_gambe": {c: float((1 + df[c].dropna()).prod() ** (12 / df[c].notna().sum()) - 1) for c in df}}
    # rendimento nelle crisi citate nell'articolo (ribilanciati, e singole gambe)
    P = portafogli(df); crisi = {}
    periodi = {"2000-2002": ("1999-12", "2002-12"), "2008": ("2007-12", "2008-12"), "2022": ("2021-12", "2022-12")}
    for nome, (eq, bd, w, reb, st) in P.items():
        d = df.loc[st:]
        v = pd.Series(nav(d[eq].values, d[bd].values if bd else None, w, reb), index=d.index)
        crisi[nome] = {k: float(v[pd.Period(b)] / v[pd.Period(a)] - 1) for k, (a, b) in periodi.items()
                       if pd.Period(a) in v.index}
    for c in ("world", "sp500", "bund_ez", "btp", "ust", "ust_h"):
        v = (1 + df[c].fillna(0)).cumprod()
        crisi[c] = {k: float(v[pd.Period(b)] / v[pd.Period(a)] - 1) for k, (a, b) in periodi.items()}
    summary["crisi"] = crisi
    for win, tabs in res["rolling_raw"].items():
        pd.concat({k: v.set_index("inizio") for k, v in tabs.items()}, axis=1).to_csv(OUT / f"rolling_{win}.csv")
    df.to_csv(OUT / "rendimenti_mensili_eur.csv")
    grafici(df, res, summary)
    json.dump(summary, open(OUT / "summary.json", "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(chk, indent=1))
    return summary, res, df


if __name__ == "__main__":
    main()
