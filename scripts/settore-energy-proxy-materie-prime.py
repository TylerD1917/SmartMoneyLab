# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Il settore energy e' un proxy delle materie prime, con un premio?
=================================================================================

Tre domande, tre finestre: a ciascuna i dati piu' lunghi che la reggono davvero.

  1. PROXY     1986-2026   il settore energy segue il petrolio? quanta beta al
                           greggio resta dopo aver tolto il fattore mercato?
  2. PREMIO    1926-2026   rende piu' del mercato? piu' delle materie prime?
  3. PORTAF.   2005-2026   sostituire la sleeve commodity con l'energy in un
                           60/40 da' la stessa protezione?

FONTI
  Settore energy   Ken French, 12 Industry Portfolios, industria "Enrgy",
                   value-weighted TOTAL RETURN (dividendi inclusi), dal 1926-07.
                   Il nostro sp500energy1993.csv e' di soli PREZZI: su un articolo
                   che parla di premio di rendimento appiattire il dividendo del
                   settore col dividendo piu' alto del mercato deciderebbe meta'
                   della risposta a tavolino. Resta come controprova.
  Mercato e RF     Ken French, 3 fattori: mercato TR = (Mkt-RF) + RF.
  Petrolio         WTI e Brent spot giornalieri, FRED. E' un PREZZO, non un
                   rendimento investibile: nessuno puo' detenere barili.
  Commodity        BCOM (nostro file) + collaterale T-bill = total return
                   investibile. ATTENZIONE: il file BCOM NON e' total return.
                   Sulla finestra comune con DBC rende +1,06%/anno contro +2,61%:
                   quel punto e mezzo e' il collaterale. Confrontarlo cosi' com'e'
                   contro un settore azionario in TR regalerebbe alla tesi un
                   punto e mezzo all'anno. DBC fa da controprova.
  Obbligazioni     indice a duration costante sul decennale USA, lo stesso motore
                   validato in quanto-rendono-etf-obbligazionari.py.
  Inflazione       CPI USA, FRED.

METODO (standard del blog)
  Tutto in total return, finestre mobili 5 e 10 anni a passo trimestrale,
  buy & hold senza ribilanciamento, lordo di costi e imposte.

Uso:  python scripts/settore-energy-proxy-materie-prime.py
Out:  public/charts/settore-energy-proxy-materie-prime/sintesi.json  + stampa
"""
from __future__ import annotations

import os
import re
import json
import zipfile
import tempfile
import subprocess
import importlib.util
import datetime as dt

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
SLUG = "settore-energy-proxy-materie-prime"
OUT = os.path.join(ROOT, "public", "charts", SLUG)
STUDIO_BOND = os.path.join(HERE, "quanto-rendono-etf-obbligazionari.py")

KF = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{}"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
PASSO = 3                      # finestre mobili a passo trimestrale


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ------------------------------------------------------------------ download
def scarica(url, suffisso=".csv"):
    """curl, non pandas: il proxy di rete risponde 500 alla richiesta di urllib."""
    f = tempfile.NamedTemporaryFile(suffix=suffisso, delete=False); f.close()
    r = subprocess.run(["curl", "-sS", "--fail", "-m", "90", "-o", f.name, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        os.unlink(f.name)
        raise SystemExit(f"[energy] download fallito: {url}\n       {r.stderr.strip()}")
    return f.name


def _tabella_french(testo, intestazione):
    """Prima tabella mensile dopo la riga di intestazione data."""
    righe = testo.splitlines()
    i = next(k for k, l in enumerate(righe) if intestazione in l)
    j = next(k for k in range(i, len(righe)) if re.match(r"^\s*\d{6}\s*,", righe[k]))
    cols = [c.strip() for c in righe[j - 1].split(",")[1:]]
    dati = []
    for l in righe[j:]:
        if not re.match(r"^\s*\d{6}\s*,", l):
            break
        p = [x.strip() for x in l.split(",")]
        dati.append([p[0]] + [float(x) for x in p[1:]])
    df = pd.DataFrame(dati, columns=["m"] + cols)
    df["m"] = pd.PeriodIndex(df["m"], freq="M")
    return df.set_index("m").replace([-99.99, -999.0], np.nan)


def dati_french():
    z = zipfile.ZipFile(scarica(KF.format("12_Industry_Portfolios_CSV.zip"), ".zip"))
    ind = _tabella_french(z.read(z.namelist()[0]).decode("latin-1"),
                          "Average Value Weighted Returns -- Monthly")
    z2 = zipfile.ZipFile(scarica(KF.format("F-F_Research_Data_Factors_CSV.zip"), ".zip"))
    fat = _tabella_french(z2.read(z2.namelist()[0]).decode("latin-1"), "Mkt-RF")
    energy = ind["Enrgy"] / 100
    rf = fat["RF"] / 100
    mkt = (fat["Mkt-RF"] + fat["RF"]) / 100
    k = energy.index.intersection(mkt.index)
    return energy[k], mkt[k], rf[k]


def fred_mensile(serie, come="last"):
    d = pd.read_csv(scarica(FRED.format(serie)))
    d.columns = ["data", "v"]
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    d = d.dropna()
    d["m"] = pd.PeriodIndex(pd.to_datetime(d["data"]), freq="M")
    g = d.groupby("m")["v"]
    return g.last() if come == "last" else g.mean()


def dati_commodity(rf):
    """BCOM (excess) + collaterale = total return investibile; DBC per controprova."""
    b = pd.read_csv(os.path.join(DATA, "Materie_prime", "BloomberCommodity_USD.csv"))
    b.columns = ["m", "v"]
    b["m"] = pd.PeriodIndex(pd.to_datetime(b["m"], format="%m/%Y"), freq="M")
    bcom_idx = b.set_index("m")["v"]
    ex = bcom_idx.pct_change().dropna()
    k = ex.index.intersection(rf.index)
    bcom_tr = ex[k] + rf[k]                      # + collaterale T-bill

    d = pd.read_csv(os.path.join(DATA, "Materie_prime", "dbc_monthly.csv"))
    d["m"] = pd.PeriodIndex(pd.to_datetime(d["Date"]), freq="M")
    dbc = d.set_index("m")["adjclose"].pct_change().dropna()
    return bcom_tr, dbc, ex


# ----------------------------------------------------------------- metriche
def metriche(r, rf=None):
    n = len(r)
    cagr = (1 + r).prod() ** (12 / n) - 1
    vol = r.std(ddof=1) * np.sqrt(12)
    nav = (1 + r).cumprod()
    mdd = (nav / nav.cummax() - 1).min()
    sharpe = None
    if rf is not None:
        ex = (r - rf.reindex(r.index)).dropna()
        sharpe = float(ex.mean() / ex.std(ddof=1) * np.sqrt(12)) if ex.std() else None
    return {"n": int(n), "cagr": float(cagr), "vol": float(vol), "mdd": float(mdd),
            "sharpe": sharpe, "multiplo": float(nav.iloc[-1])}


def cattura(r, base):
    """Quanto cattura al rialzo e al ribasso della base, mese per mese."""
    k = r.index.intersection(base.index)
    r, base = r[k], base[k]
    su, giu = base > 0, base < 0
    return {"su": float(r[su].mean() / base[su].mean()),
            "giu": float(r[giu].mean() / base[giu].mean()),
            "n_su": int(su.sum()), "n_giu": int(giu.sum())}


def finestre(r, anni, passo=PASSO):
    m = anni * 12
    nav = (1 + r).cumprod()
    out = ((nav.shift(-m) / nav) ** (1 / anni) - 1).dropna().iloc[::passo]
    return out * 100


def percentili(f):
    q = np.percentile(f, [5, 25, 50, 75, 95])
    return {"n": int(len(f)), "p5": float(q[0]), "p25": float(q[1]), "mediana": float(q[2]),
            "p75": float(q[3]), "p95": float(q[4]), "media": float(f.mean()),
            "peggio": float(f.min()), "negative": float(100 * (f < 0).mean())}


def regressione(y, *xs):
    """OLS con intercetta. Ritorna (alfa_annua, [beta...], R2)."""
    k = y.index
    for x in xs:
        k = k.intersection(x.index)
    Y = y[k].to_numpy(float)
    X = np.column_stack([np.ones(len(k))] + [x[k].to_numpy(float) for x in xs])
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ b
    r2 = 1 - res.var() / Y.var()
    return float(b[0] * 12), [float(v) for v in b[1:]], float(r2), int(len(k))



# ----------------------------------------------------------------- grafici
NAVY = "#1e3a8a"; GOLD = "#d97706"; ROSSO = "#dc2626"
VERDE = "#047857"; GRIGIO = "#64748b"; CHIARO = "#cbd5e1"
COLORI = {"mercato": GRIGIO, "energy": NAVY, "commodity": GOLD, "WTI": ROSSO, "BCOM": GOLD}


def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def g_quadranti(ris, out):
    fin = list(ris["shock"]["quadranti"])
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.8), sharey=True)
    for ax, titolo in zip(axes, fin):
        q = ris["shock"]["quadranti"][titolo]
        nomi = list(q)
        etich = [("mercato", "mercato USA"), ("energy", "settore energy")] + \
                ([("BCOM", "materie prime")] if "BCOM" in q[nomi[0]] else [])
        x = np.arange(len(nomi)); w = 0.8 / len(etich)
        for i, (et, lab) in enumerate(etich):
            v = [q[n][et] * 100 for n in nomi]
            b = ax.bar(x + (i - (len(etich) - 1) / 2) * w, v, w, color=COLORI[et], label=lab)
            ax.bar_label(b, fmt="%+.1f", fontsize=8.5, padding=2)
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x)
        ax.set_xticklabels([n.replace(", ", "\n").replace("giu", "giù") +
                            f"\n({q[n]['n']} mesi)" for n in nomi], fontsize=9)
        ax.set_title(titolo, fontsize=11.5)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
        ax.legend(frameon=False, fontsize=9.5, loc="upper left")
        ax.grid(axis="x", visible=False)
    # aria sopra: con l'asse condiviso le etichette del pannello destro
    # finivano dentro la legenda
    lo, hi = axes[0].get_ylim()
    axes[0].set_ylim(lo, hi + (hi - lo) * 0.22)
    axes[0].set_ylabel("rendimento medio mensile")
    fig.suptitle("Il quadrante che conta: quando la borsa scende e il petrolio sale",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out); plt.close(fig)


def g_decile(ris, out):
    d = ris["shock"]["decile_peggiore"]
    lunga, corta = list(d)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.6),
                                  gridspec_kw={"width_ratios": [1.3, 1]})
    nomi = list(d[corta])
    x = np.arange(len(nomi))
    etich = [("mercato", "mercato USA"), ("energy", "settore energy"), ("BCOM", "materie prime")]
    w = 0.8 / len(etich)
    for i, (et, lab) in enumerate(etich):
        v = [d[corta][n].get(et, 0) * 100 for n in nomi]
        b = ax.bar(x + (i - 1) * w, v, w, color=COLORI[et], label=lab)
        ax.bar_label(b, fmt="%+.1f", fontsize=9, padding=2)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([f"{n}\n({d[corta][n]['n']} mesi)" for n in nomi])
    ax.set_ylabel("rendimento medio mensile")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_title("Il 10% di mesi peggiori del mercato, dal 2005", fontsize=11.5)
    ax.legend(frameon=False, fontsize=9.5); ax.grid(axis="x", visible=False)

    chiavi = [k for k in d[corta][nomi[0]] if k.startswith("sleeve")]
    for i, k_ in enumerate(chiavi):
        col = GOLD if "commodity" in k_ else NAVY
        lab = "sleeve materie prime" if "commodity" in k_ else "sleeve energy"
        v = [(d[corta][n].get(k_) or 0) * 100 for n in nomi]
        b = ax2.bar(x + (i - 0.5) * 0.34, v, 0.34, color=col, label=lab)
        ax2.bar_label(b, fmt="%+.2f", fontsize=9, padding=2)
    ax2.axhline(0, color="black", lw=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{n}\n({d[corta][n].get('n_sleeve', 0)} mesi)" for n in nomi], fontsize=9.5)
    ax2.set_ylabel("punti aggiunti al 60/40, al mese")
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=1))
    ax2.set_title("Quanto ha aggiunto la sleeve del 10%", fontsize=11.5)
    ax2.legend(frameon=False, fontsize=9.5); ax2.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def g_crescita(energy, mkt, bcom, out):
    k = energy.index.intersection(mkt.index).intersection(bcom.index)
    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    for et, s_, lab in [("mercato", mkt, "mercato USA"), ("energy", energy, "settore energy"),
                        ("BCOM", bcom, "materie prime (indice + collaterale)")]:
        nav = (1 + s_[k]).cumprod()
        ax.plot(nav.index.to_timestamp(), nav.values, lw=2, color=COLORI[et],
                label=f"{lab}  ×{nav.iloc[-1]:.1f}")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}x" if v >= 1 else f"{v:.1f}x"))
    ax.set_title("Un dollaro investito nel 2005")
    ax.set_ylabel("moltiplicatore (scala logaritmica)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def g_impennate(ris, out):
    ep = [e for e in ris["shock"]["impennate"] if e.get("mesi") and e.get("mercato") is not None]
    ep = [e for e in ep if e["mercato"] < 0] + [e for e in ep if e["mercato"] >= 0]
    nomi = [f"{e['da'][:7]}" for e in ep]
    x = np.arange(len(ep)); w = 0.27
    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    for i, (et, lab) in enumerate([("mercato", "mercato USA"), ("energy", "settore energy"),
                                   ("BCOM", "materie prime")]):
        v = [(e.get(et) if e.get(et) is not None else np.nan) for e in ep]
        ax.bar(x + (i - 1) * w, [0 if np.isnan(z) else z * 100 for z in v], w,
               color=COLORI[et], label=lab)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(nomi, rotation=45, ha="right", fontsize=9.5)
    ax.set_ylabel("rendimento dell'episodio")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_title("Le impennate del greggio (+30% in tre mesi), episodio per episodio")
    ax.annotate("a sinistra gli episodi in cui il mercato ha perso", xy=(0.012, 0.045),
                xycoords="axes fraction", fontsize=9.5, color=GRIGIO, style="italic")
    ax.legend(frameon=False, ncol=3, loc="upper right"); ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def g_2026(ris, out):
    d = [r for r in ris["shock"]["2026"] if r.get("mercato") is not None]
    x = np.arange(len(d)); w = 0.21
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    for i, (et, lab) in enumerate([("WTI", "petrolio WTI"), ("mercato", "mercato USA"),
                                   ("energy", "settore energy"), ("BCOM", "materie prime")]):
        v = [(r.get(et) or 0) * 100 for r in d]
        ax.bar(x + (i - 1.5) * w, v, w, color=COLORI[et], label=lab)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([r["mese"] for r in d], fontsize=10)
    ax.set_ylabel("rendimento del mese")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_title("Il 2026, mese per mese: lo shock geopolitico in diretta")
    ax.legend(frameon=False, ncol=4, loc="upper left"); ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    energy, mkt, rf = dati_french()
    wti = fred_mensile("DCOILWTICO").pct_change().dropna()
    brent = fred_mensile("DCOILBRENTEU").pct_change().dropna()
    cpi = fred_mensile("CPIAUCSL")
    bcom, dbc, bcom_ex = dati_commodity(rf)

    spec = importlib.util.spec_from_file_location("bond", STUDIO_BOND)
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    y10 = B.mensile("DGS10.csv")
    bond = B.indice(y10, 10).pct_change().dropna()        # duration costante 10 anni

    print(f"\n{'='*78}\nDATI\n{'='*78}")
    for nome, s in [("energy (French TR)", energy), ("mercato USA (French TR)", mkt),
                    ("WTI spot", wti), ("Brent spot", brent),
                    ("BCOM + collaterale", bcom), ("DBC", dbc),
                    ("Treasury 10y (TR)", bond), ("CPI", cpi)]:
        print(f"  {nome:26s} {s.index[0]} -> {s.index[-1]}  n={len(s)}")

    ris = {"generato": dt.date.today().isoformat()}

    # ---------------------------------------------------------- 1. PROXY
    print(f"\n{'='*78}\n1. E' UN PROXY DEL PETROLIO?\n{'='*78}")
    k = energy.index.intersection(wti.index)
    print(f"finestra {k.min()} -> {k.max()} ({len(k)} mesi)")
    print(f"  correlazione mensile energy-WTI   {energy[k].corr(wti[k]):.3f}")
    print(f"  correlazione mensile energy-Brent {energy.corr(brent):.3f}")
    print(f"  correlazione mensile energy-mercato {energy[k].corr(mkt[k]):.3f}")
    print(f"  correlazione mensile WTI-mercato    {wti[k].corr(mkt[k]):.3f}")

    a1, b1, r2_1, n1 = regressione(energy, wti)
    a2, b2, r2_2, n2 = regressione(energy, mkt, wti)
    print(f"\n  energy ~ petrolio            beta {b1[0]:.3f}  R2 {r2_1:.3f}  (n={n1})")
    print(f"  energy ~ mercato + petrolio  beta mercato {b2[0]:.3f}, "
          f"beta petrolio {b2[1]:.3f}  R2 {r2_2:.3f}  alfa {a2*100:+.2f}%/anno")
    ris["proxy"] = {"corr_wti": float(energy[k].corr(wti[k])),
                    "corr_mercato": float(energy[k].corr(mkt[k])),
                    "corr_wti_mercato": float(wti[k].corr(mkt[k])),
                    "beta_wti_sola": b1[0], "r2_sola": r2_1,
                    "beta_mercato": b2[0], "beta_wti_dopo_mercato": b2[1],
                    "r2_doppia": r2_2, "alfa_annua": a2, "n": n2,
                    "da": str(k.min()), "a": str(k.max())}

    # beta rolling a 36 mesi: la relazione e' stabile?
    roll = []
    idx = sorted(k)
    for i in range(36, len(idx) + 1):
        f = idx[i-36:i]
        x = wti[f].to_numpy(float); y = energy[f].to_numpy(float)
        roll.append((idx[i-1], float(np.polyfit(x, y, 1)[0])))
    rb = pd.Series(dict(roll))
    print(f"  beta rolling 36 mesi al petrolio: mediana {rb.median():.2f}, "
          f"min {rb.min():.2f} ({rb.idxmin()}), max {rb.max():.2f} ({rb.idxmax()})")
    ris["proxy"]["beta_rolling"] = {"mediana": float(rb.median()), "min": float(rb.min()),
                                    "min_q": str(rb.idxmin()), "max": float(rb.max()),
                                    "max_q": str(rb.idxmax())}

    print("\n  cattura al rialzo e al ribasso (mese per mese):")
    for nome, base in [("WTI spot", wti), ("BCOM+collaterale", bcom)]:
        c = cattura(energy, base)
        print(f"    energy vs {nome:16s} su {c['su']*100:5.1f}% ({c['n_su']} mesi)  "
              f"giu {c['giu']*100:5.1f}% ({c['n_giu']} mesi)")
        ris.setdefault("cattura", {})[nome] = c

    # ---------------------------------------------------------- 2. PREMIO
    print(f"\n{'='*78}\n2. C'E' UN PREMIO?\n{'='*78}")
    ris["premio"] = {}
    for lab, inizio in [("1926-2026 (tutta la storia)", None),
                        ("1986-2026 (era del petrolio quotato)", "1986-02"),
                        ("2005-2026 (era delle commodity investibili)", "2005-04")]:
        print(f"\n  {lab}")
        serie = {"energy": energy, "mercato": mkt}
        if inizio and inizio >= "2005":
            serie.update({"commodity (BCOM+coll.)": bcom, "DBC": dbc})
        if inizio and inizio >= "1986":
            serie["WTI spot (non investibile)"] = wti
        for nome, s in serie.items():
            s = s if inizio is None else s[s.index >= inizio]
            if len(s) < 60:
                continue
            m = metriche(s, rf)
            sh = f"{m['sharpe']:.2f}" if m["sharpe"] is not None else "  - "
            print(f"    {nome:28s} CAGR {m['cagr']*100:6.2f}%  vol {m['vol']*100:5.1f}%  "
                  f"MDD {m['mdd']*100:6.1f}%  Sharpe {sh}  x{m['multiplo']:.1f}")
            ris["premio"].setdefault(lab, {})[nome] = m

    print("\n  finestre mobili (passo trimestrale), rendimento annuo:")
    ris["finestre"] = {}
    for anni in (5, 10):
        print(f"    --- {anni} anni")
        for nome, s, da in [("energy", energy, None), ("mercato", mkt, None),
                            ("energy (dal 2005)", energy, "2005-04"),
                            ("mercato (dal 2005)", mkt, "2005-04"),
                            ("commodity (dal 2005)", bcom, "2005-04")]:
            s = s if da is None else s[s.index >= da]
            f = finestre(s, anni)
            if len(f) < 8:
                continue
            p = percentili(f)
            print(f"      {nome:22s} n={p['n']:4d}  mediana {p['mediana']:6.2f}%  "
                  f"p5 {p['p5']:7.2f}%  p95 {p['p95']:6.2f}%  negative {p['negative']:5.1f}%")
            ris["finestre"].setdefault(f"{anni}a", {})[nome] = p

    # ---------------------------------------------------------- 3. PROTEZIONE
    print(f"\n{'='*78}\n3. PROTEGGE QUANDO SERVE?\n{'='*78}")
    infl = (cpi / cpi.shift(12) - 1).dropna() * 100
    ETICHETTE = ["molto bassa", "bassa", "media", "alta", "molto alta"]
    ris["inflazione"] = {}
    # Due pannelli, non uno. Un'unica tabella confronterebbe asset su periodi
    # diversi (il WTI quotato parte dal 1986, BCOM dal 2005): dentro la stessa
    # riga i numeri non sarebbero confrontabili fra loro.
    for titolo, attivi, inizio in [
            ("storia lunga, solo azionario", [("energy", energy), ("mercato", mkt)], None),
            ("dal 1986, con petrolio e commodity",
             [("energy", energy), ("mercato", mkt), ("WTI", wti), ("BCOM", bcom)], "1986-02")]:
        base = infl if inizio is None else infl[infl.index >= inizio]
        k = energy.index.intersection(base.index)
        q = pd.qcut(base[k], 5, labels=ETICHETTE)
        print(f"\n  rendimento annualizzato per quintile di inflazione, {titolo} "
              f"({k.min()} -> {k.max()}, {len(k)} mesi):")
        for lab in ETICHETTE:
            mesi = q[q == lab].index
            riga = {}
            for nome, s in attivi:
                kk = s.index.intersection(mesi)
                riga[nome] = (float((1 + s[kk]).prod() ** (12 / len(kk)) - 1)
                              if len(kk) >= 24 else None)
            soglia = f"{base[mesi].min():.1f}-{base[mesi].max():.1f}%"
            print(f"    {lab:12s} (CPI {soglia:14s} n={len(mesi):3d})  " +
                  "  ".join(f"{n} {v*100:+6.1f}%" if v is not None else f"{n}    n.d."
                            for n, v in riga.items()))
            ris["inflazione"].setdefault(titolo, {})[lab] = {
                "n": len(mesi), "soglia": soglia, **riga}

    # mercati orso del mercato USA: cosa ha fatto l'energy, e cosa le commodity
    nav = (1 + mkt).cumprod()
    dd = nav / nav.cummax() - 1
    orsi, in_orso = [], False
    for m_, v in dd.items():
        if not in_orso and v <= -0.20:
            in_orso = True
            picco = nav[:m_].idxmax(); fondo = m_
        elif in_orso:
            if nav[m_] > nav[picco]:
                orsi.append((picco, fondo)); in_orso = False
            elif dd[m_] < dd[fondo]:
                fondo = m_
    if in_orso:
        orsi.append((picco, fondo))
    print(f"\n  mercati orso del mercato USA (picco -> fondo, calo >= 20%): {len(orsi)}")
    ris["orsi"] = []
    for picco, fondo in orsi:
        mesi = [x for x in mkt.index if picco < x <= fondo]
        riga = {"da": str(picco), "a": str(fondo), "mesi": len(mesi)}
        for nome, s in [("mercato", mkt), ("energy", energy), ("WTI", wti), ("BCOM", bcom)]:
            kk = [x for x in mesi if x in s.index]
            riga[nome] = float((1 + s[kk]).prod() - 1) if len(kk) == len(mesi) and mesi else None
        ris["orsi"].append(riga)
        print(f"    {riga['da']} -> {riga['a']} ({riga['mesi']:3d} mesi)  " +
              "  ".join(f"{n} {riga[n]*100:+7.1f}%" if riga.get(n) is not None else f"{n}     -  "
                        for n in ("mercato", "energy", "WTI", "BCOM")))

    # ---------------------------------------------------------- 4. PORTAFOGLIO
    print(f"\n{'='*78}\n4. IN PORTAFOGLIO: COMMODITY O ENERGY?\n{'='*78}")
    k = mkt.index.intersection(bond.index).intersection(bcom.index).intersection(energy.index)
    print(f"finestra comune {k.min()} -> {k.max()} ({len(k)} mesi), buy & hold senza ribilanciamento")
    port = {
        "60/40": {"mkt": 0.60, "bond": 0.40},
        "54/36 + 10% commodity": {"mkt": 0.54, "bond": 0.36, "bcom": 0.10},
        "54/36 + 10% energy": {"mkt": 0.54, "bond": 0.36, "energy": 0.10},
    }
    comp = {"mkt": mkt[k], "bond": bond[k], "bcom": bcom[k], "energy": energy[k]}
    ris["portafogli"] = {}
    serie_port = {}
    for nome, pesi in port.items():
        # buy & hold: i pesi driftano, quindi si compone ogni gamba e si somma
        nav_tot = sum(w * (1 + comp[a]).cumprod() for a, w in pesi.items())
        r = nav_tot.pct_change().dropna()
        serie_port[nome] = r
        m = metriche(r, rf)
        f10 = percentili(finestre(r, 10))
        print(f"  {nome:24s} CAGR {m['cagr']*100:5.2f}%  vol {m['vol']*100:5.2f}%  "
              f"MDD {m['mdd']*100:6.1f}%  Sharpe {m['sharpe']:.2f}  "
              f"| 10a mediana {f10['mediana']:5.2f}%  p5 {f10['p5']:5.2f}%")
        ris["portafogli"][nome] = {**m, "finestre10": f10}


    # ------------------------------------------- 5. L'ASSICURAZIONE CONTRO LO SHOCK
    print(f"\n{'='*78}\n5. QUANDO SONO LE MATERIE PRIME A FAR SOFFRIRE LA BORSA\n{'='*78}")
    ris["shock"] = {}

    # Quadranti. Due finestre, mai mescolate: l'indice commodity investibile e i
    # portafogli esistono solo dal 2005, e una media del mercato su 487 mesi
    # accostata a una delle materie prime su 257 non e' un confronto.
    FINESTRE = [("dal 1986, mercato e settore energy", "1986-02",
                 [("mercato", mkt), ("energy", energy), ("WTI", wti)]),
                ("dal 2005, con le materie prime", "2005-04",
                 [("mercato", mkt), ("energy", energy), ("WTI", wti), ("BCOM", bcom)])]
    ris["shock"]["quadranti"] = {}
    for titolo, da, attivi in FINESTRE:
        kq = mkt.index.intersection(wti.index)
        kq = kq[kq >= da]
        for nome, s_ in attivi:
            kq = kq.intersection(s_.index)
        quad = {"mercato giu, petrolio su": (mkt[kq] < 0) & (wti[kq] > 0),
                "mercato giu, petrolio giu": (mkt[kq] < 0) & (wti[kq] <= 0),
                "mercato su, petrolio su": (mkt[kq] > 0) & (wti[kq] > 0),
                "mercato su, petrolio giu": (mkt[kq] >= 0) & (wti[kq] <= 0)}
        print(f"\n  medie mensili per quadrante, {titolo} ({kq.min()} -> {kq.max()}, {len(kq)} mesi):")
        for nome, m_ in quad.items():
            mesi = kq[m_]
            riga = {"n": int(len(mesi))}
            for et, s_ in attivi:
                riga[et] = float(s_[mesi].mean())
            print(f"    {nome:26s} n={riga['n']:3d}  " +
                  "  ".join(f"{et} {riga[et]*100:+6.2f}%" for et, _ in attivi))
            ris["shock"]["quadranti"].setdefault(titolo, {})[nome] = riga

    # Il test piu' stretto: decile peggiore del mercato, diviso per segno del
    # greggio. Stessa regola: una finestra per volta, soglia ricalcolata su
    # ciascuna, e la sleeve misurata solo dove i portafogli esistono.
    ris["shock"]["decile_peggiore"] = {}
    for titolo, da, attivi in FINESTRE:
        kq = mkt.index.intersection(wti.index)
        kq = kq[kq >= da]
        for nome, s_ in attivi:
            kq = kq.intersection(s_.index)
        soglia = float(np.percentile(mkt[kq], 10))
        peggiori = kq[mkt[kq] <= soglia]
        print(f"\n  decile peggiore del mercato, {titolo}: mesi sotto {soglia*100:.2f}%")
        for et, cond in [("petrolio in rialzo", wti[peggiori] > 0),
                         ("petrolio in calo", wti[peggiori] <= 0)]:
            mesi = peggiori[cond]
            riga = {"n": int(len(mesi))}
            for nome, s_ in attivi:
                if nome == "WTI":
                    continue
                riga[nome] = float(s_[mesi].mean())
            if da >= "2005":
                for nome, r_ in serie_port.items():
                    if nome == "60/40":
                        continue
                    kk = r_.index.intersection(mesi).intersection(serie_port["60/40"].index)
                    riga["sleeve " + nome.split("+ ")[1].strip()] = (
                        float((r_[kk] - serie_port["60/40"][kk]).mean()) if len(kk) >= 6 else None)
                    riga["n_sleeve"] = int(len(kk))
            print(f"    {et:20s} n={riga['n']:3d}  " + "  ".join(
                f"{k2} {v*100:+6.2f}%" for k2, v in riga.items()
                if k2 not in ("n", "n_sleeve") and v is not None) +
                (f"   (sleeve su {riga['n_sleeve']} mesi)" if "n_sleeve" in riga else ""))
            ris["shock"]["decile_peggiore"].setdefault(titolo, {})[et] = riga

    # Costo dell'assicurazione: la stessa differenza, su tutti gli altri mesi
    print("\n  costo della sleeve negli altri mesi (differenza media annualizzata vs 60/40):")
    base = serie_port["60/40"]
    kq = mkt.index.intersection(wti.index).intersection(bcom.index)
    peggiori = kq[mkt[kq] <= float(np.percentile(mkt[kq], 10))]
    for nome, r_ in serie_port.items():
        if nome == "60/40":
            continue
        kk = r_.index.intersection(base.index)
        normali = [x for x in kk if x not in set(peggiori)]
        d = float((r_[normali] - base[normali]).mean() * 12)
        tot = float((r_[kk] - base[kk]).mean() * 12)
        print(f"    {nome:24s} mesi normali {d*100:+5.2f}%/anno   tutti i mesi {tot*100:+5.2f}%/anno")
        ris["shock"].setdefault("costo", {})[nome] = {"mesi_normali": d, "tutti": tot}

    # Episodi di impennata del greggio (come nell'articolo petrolio-e-mercati-azionari: +30% in 3 mesi)
    liv = fred_mensile("DCOILWTICO")
    sp = (liv / liv.shift(3) - 1).dropna()
    acceso, episodi = False, []
    for m_, v in sp.items():
        if not acceso and v >= 0.30:
            acceso, inizio = True, m_
        elif acceso and v < 0.10:
            episodi.append((inizio, m_)); acceso = False
    if acceso:
        episodi.append((inizio, sp.index[-1]))
    print(f"\n  impennate del greggio (+30% in 3 mesi): {len(episodi)} episodi")
    ris["shock"]["impennate"] = []
    for a, b in episodi:
        mesi = [x for x in mkt.index if a <= x <= b]
        if not mesi:          # impennata in corso: i dati azionari arrivano a 2026-08
            print(f"    {a} -> {b}  impennata in corso, dati azionari non ancora disponibili")
            ris["shock"]["impennate"].append({"da": str(a), "a": str(b), "mesi": 0, "in_corso": True})
            continue
        riga = {"da": str(a), "a": str(b), "mesi": len(mesi)}
        for nome, s_ in [("mercato", mkt), ("energy", energy), ("WTI", wti), ("BCOM", bcom)]:
            kk = [x for x in mesi if x in s_.index]
            riga[nome] = float((1 + s_[kk]).prod() - 1) if len(kk) == len(mesi) and mesi else None
        ris["shock"]["impennate"].append(riga)
        print(f"    {riga['da']} -> {riga['a']} ({riga['mesi']:2d} mesi)  " + "  ".join(
            f"{n} {riga[n]*100:+7.1f}%" if riga.get(n) is not None else f"{n}     n.d."
            for n in ("mercato", "energy", "WTI", "BCOM")))

    # Il caso vivo: il 2026
    print("\n  il 2026 mese per mese (petrolio, mercato, energy, commodity):")
    ris["shock"]["2026"] = []
    for m_ in [x for x in mkt.index if str(x) >= "2026-01"]:
        riga = {"mese": str(m_)}
        for nome, s_ in [("WTI", wti), ("mercato", mkt), ("energy", energy), ("BCOM", bcom)]:
            riga[nome] = float(s_[m_]) if m_ in s_.index else None
        ris["shock"]["2026"].append(riga)
        print(f"    {riga['mese']}  " + "  ".join(
            f"{n} {riga[n]*100:+6.1f}%" if riga.get(n) is not None else f"{n}   n.d."
            for n in ("WTI", "mercato", "energy", "BCOM")))

    _stile()
    g_quadranti(ris, os.path.join(OUT, "01_quadranti.png"))
    g_decile(ris, os.path.join(OUT, "02_decile_peggiore.png"))
    g_crescita(energy, mkt, bcom, os.path.join(OUT, "03_crescita_1_dollaro.png"))
    g_impennate(ris, os.path.join(OUT, "04_impennate.png"))
    g_2026(ris, os.path.join(OUT, "05_2026.png"))
    print(f"\n[energy] 5 grafici -> {OUT}")

    with open(os.path.join(OUT, "sintesi.json"), "w", encoding="utf-8") as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, allow_nan=False)
    print(f"\n[energy] sintesi -> {os.path.join(OUT, 'sintesi.json')}")


if __name__ == "__main__":
    main()
