# -*- coding: utf-8 -*-
"""
SmartMoneyLab — La regola del doppio della duration, messa alla prova
=====================================================================

Leibowitz e co-autori, e poi Lozada (2016, "Constant-Duration Bond Portfolios'
Initial (Rolling) Yield Forecasts Return Best at Twice Duration"), dimostrano
che per un portafoglio obbligazionario a DURATION COSTANTE il rendimento medio
su un orizzonte di 2D-1 periodi coincide con il rendimento a scadenza iniziale.

LA TEORIA IN TRE RIGHE
  Rendimento del periodo:  R_t ≈ Y_t - (D-1)·ΔY_t            (Proposizione 1)
  Con un sentiero dei tassi lineare, Y_t = Y_1 + (t-1)·ΔY, la media aritmetica
  dei primi N rendimenti vale  Y_1 + ΔY·((N+1)/2 - D), che si annulla per
      N = 2D - 1
  qualunque sia la pendenza ΔY, che infatti non si conosce in anticipo. Il "-1"
  è UN periodo di turnover: con ribilanciamento mensile vale 1/12 di anno,
  quindi l'orizzonte è praticamente 2D.

COSA AGGIUNGIAMO NOI
  Lozada verifica su rendimenti USA a breve, media e lunga scadenza. Noi
  abbiamo quattro indici a duration costante ricostruiti mese per mese dal 1962
  (USA 7-10 e 20+, area euro, Italia lunga), quindi possiamo:
    1. misurare l'orizzonte in cui l'errore di previsione è minimo e
       confrontarlo con 2D-1, gamba per gamba;
    2. usare la duration VERA del mese di acquisto invece di una media: la
       duration di un titolo alla pari cambia molto col livello dei tassi
       (un ventennale al 15% ha duration 6,5, al 4% ne ha 15), quindi anche
       l'orizzonte previsto si muove nel tempo;
    3. separare la media aritmetica dei rendimenti continui, su cui vale il
       teorema, dal rendimento composto che l'investitore porta a casa.

Uso:  python scripts/regola-2x-duration.py
Out:  public/charts/regola-2x-duration/sintesi.json + stampa
"""
from __future__ import annotations

import os
import json
import importlib.util
import datetime as dt

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STUDIO = os.path.join(HERE, "quanto-rendono-etf-obbligazionari.py")
OUT = os.path.join(ROOT, "public", "charts", "regola-2x-duration")

SCADENZE = {"USA 7-10": 8.5, "USA 20+": 24.0, "Area euro 7-10": 8.5, "Italia 15+": 20.0}
ORIZZONTI = list(range(2, 29))          # anni, per la curva dell'errore


def it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def duration_modificata(M, y):
    """-dP/dy / P del titolo alla pari comprato a quel rendimento.

    Non e' un dettaglio: la duration di un titolo alla pari dipende dal livello
    dei tassi, quindi 2D-1 e' un orizzonte che si muove nel tempo e non una
    costante della gamba."""
    h = 1e-5
    p = lambda yy: B.prezzo(yy, y, M)
    return (p(y - h) - p(y + h)) / (2 * h) / p(y)


def errori(nav, logret, y, mesi_h):
    """Errore di previsione a orizzonte dato, mese per mese.

    Ritorna due serie allineate ai mesi di acquisto:
      geo  = rendimento annuo composto ottenuto meno rendimento a scadenza
      cc   = media aritmetica dei rendimenti continui meno ln(1+Y), che e'
             la grandezza su cui il teorema di Lozada e' esatto
    """
    anni = mesi_h / 12
    fine = nav.shift(-mesi_h)
    geo = ((fine / nav) ** (1 / anni) - 1) * 100 - y
    # media dei log-rendimenti sui mesi_h mesi successivi, annualizzata
    somma = logret[::-1].rolling(mesi_h).sum()[::-1].shift(-1)
    cc = somma / anni * 100 - np.log1p(y / 100) * 100
    return geo.dropna(), cc.dropna()


def riassunto(e):
    return {"n": int(len(e)), "medio": float(e.mean()), "mae": float(e.abs().mean()),
            "rmse": float(np.sqrt((e ** 2).mean())),
            "entro1": float(100 * (e.abs() <= 1).mean()),
            "entro2": float(100 * (e.abs() <= 2).mean())}



def curvatura(y, pos, mesi):
    """Quanto il sentiero dei tassi sta in media SOPRA la retta che unisce i
    suoi estremi, in punti: positiva se il sentiero e' concavo (tassi tenuti
    alti e poi scesi), negativa se e' convesso.

    E' la grandezza della Sezione 2 di Lozada, col segno girato per leggerla
    meglio: scomponendo il sentiero in una parte lineare, che a 2D-1 restituisce
    esattamente il rendimento iniziale, e in uno scarto, il residuo del teorema
    e' la media di quello scarto. Quindi lo scarto fra rendimento realizzato e
    rendimento iniziale dovrebbe valere la curvatura stessa, con pendenza +1 e
    non "una correlazione".
    """
    seg = y.iloc[pos:pos + mesi + 1].to_numpy(float)
    retta = np.linspace(seg[0], seg[-1], len(seg))
    return float(seg.mean() - retta.mean())


def test_convessita(nome, nav, y, D, logret):
    """Regressione dello scarto a 2D sulla curvatura del sentiero dei tassi."""
    righe = []
    for t in y.index:
        m = int(round((2 * D[t] - 1 / 12) * 12))
        pos = y.index.get_loc(t)
        if m < 24 or pos + m >= len(nav):
            continue
        r_mensili = nav.iloc[pos:pos + m + 1].pct_change().dropna()
        gap = float(r_mensili.mean() * 12 * 100 - y[t])      # media aritmetica, come il teorema
        righe.append((curvatura(y, pos, m), gap))
    if len(righe) < 60:
        return None
    x = np.array([a for a, _ in righe]); g = np.array([b for _, b in righe])
    b, a = np.polyfit(x, g, 1)
    r = float(np.corrcoef(x, g)[0, 1])
    print(f"    {nome:16s} n={len(righe):4d}  curvatura media {x.mean():+6.2f}  "
          f"scarto medio {g.mean():+6.2f}  pendenza {b:+5.2f} (attesa +1,00)  "
          f"R2 {r*r:4.2f}  residuo {float(g.mean() - x.mean()):+5.2f}")
    PUNTI[nome] = righe
    return {"n": len(righe), "curvatura_media": float(x.mean()), "scarto_medio": float(g.mean()),
            "pendenza": float(b), "intercetta": float(a), "r2": float(r * r),
            "residuo_medio": float(g.mean() - x.mean())}


def test_rolldown(gambe_senza, rendimenti, ris):
    """La gamba USA 7-10 modella il roll-down, le altre no. Ricostruendola
    senza, lo stesso scarto a 2D si misura due volte sulla stessa serie di
    tassi: la differenza e' il contributo del roll-down."""
    print(f"\n{'='*78}\n  D. QUANTO PESA IL ROLL-DOWN (USA 7-10, stessa curva, due indici)\n{'='*78}")
    out = {}
    for et, nav in gambe_senza.items():
        y = rendimenti["USA 7-10"]
        k = nav.index.intersection(y.index)
        nav, yy = nav[k], y[k]
        D = pd.Series([duration_modificata(8.5, v / 100) for v in yy], index=yy.index)
        vals = []
        for t in yy.index:
            m = int(round((2 * D[t] - 1 / 12) * 12))
            pos = nav.index.get_loc(t)
            if m < 24 or pos + m >= len(nav):
                continue
            geo = (nav.iloc[pos + m] / nav.iloc[pos]) ** (12 / m) - 1
            vals.append(geo * 100 - yy[t])
        e = pd.Series(vals)
        out[et] = riassunto(e)
        print(f"    {et:28s} n={len(e):4d}  scarto medio {e.mean():+5.2f}  "
              f"MAE {e.abs().mean():4.2f}  entro1 {100*(e.abs()<=1).mean():4.1f}%")
    if len(out) == 2:
        a, b = list(out.values())
        print(f"    -> il roll-down vale {a['medio'] - b['medio']:+.2f} punti di scarto medio")
    ris["rolldown"] = out



# blocco grafici da inserire in scripts/regola-2x-duration.py
PUNTI = {}          # nome gamba -> (curvature, scarto) per il grafico 04

NAVY = "#1e3a8a"; NERO = "#0f172a"; VERDE = "#047857"; GOLD = "#d97706"
ROSSO = "#dc2626"; GRIGIO = "#64748b"; CHIARO = "#cbd5e1"
COLORI = {"USA 7-10": NAVY, "USA 20+": NERO, "Area euro 7-10": VERDE, "Italia 15+": GOLD}


def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def _n(v, d=2):
    """Numero con la virgola e il meno tipografico, per le etichette."""
    return f"{v:+.{d}f}".replace("-", "−").replace(".", ",")


def _sentiero(y0, y1, amp, mesi):
    """Sentiero dei tassi sintetico: retta fra gli estremi piu' una gobba.
    amp > 0 mette il sentiero SOPRA la corda (concavo)."""
    t = np.linspace(0, 1, mesi + 1)
    return y0 + (y1 - y0) * t + amp * np.sin(np.pi * t)


def _simula(y_arr, M):
    """Fa girare il motore degli indici su un sentiero inventato.
    Ritorna il nav e i due scarti rispetto al rendimento iniziale."""
    idx = pd.period_range("2000-01", periods=len(y_arr), freq="M")
    y = pd.Series(y_arr, index=idx)
    nav = B.indice(y, M)
    r = nav.pct_change().dropna()
    anni = (len(y_arr) - 1) / 12
    arit = float(r.mean() * 12 * 100 - y.iloc[0])
    geo = float(((nav.iloc[-1] / nav.iloc[0]) ** (1 / anni) - 1) * 100 - y.iloc[0])
    corda = np.linspace(y_arr[0], y_arr[-1], len(y_arr))
    return nav, arit, geo, float(np.mean(y_arr) - corda.mean())


def plot_meccanismo(out):
    """Il grafico didattico: la pendenza del sentiero non conta, la curvatura si'."""
    M = 8.5
    y0 = 5.0
    D = duration_modificata(M, y0 / 100)
    mesi = int(round((2 * D - 1 / 12) * 12))
    anni = mesi / 12
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.6), sharey=True)
    x = np.arange(mesi + 1) / 12

    casi_a = [("i tassi crollano al 1%", 1.0, ROSSO),
              ("i tassi restano al 5%", 5.0, GRIGIO),
              ("i tassi salgono al 9%", 9.0, NAVY)]
    for et, y1, c in casi_a:
        yy = _sentiero(y0, y1, 0.0, mesi)
        _, arit, geo, curv = _simula(yy, M)
        axes[0].plot(x, yy, lw=2.2, color=c)
        axes[0].annotate(f"{et}\nscarto {_n(arit)}", xy=(x[-1], yy[-1]),
                         xytext=(-6, 12 if y1 >= 5 else 26), textcoords="offset points",
                         ha="right", fontsize=9.5, color=c, fontweight="bold")
        print(f"    [graf 1A] {et:28s} curvatura {curv:+5.2f}  "
              f"scarto aritmetico {arit:+5.2f}  composto {geo:+5.2f}")
    axes[0].set_title("La pendenza non conta")
    axes[0].annotate("tre sentieri rettilinei, tre mondi opposti:\n"
                     "a 2 × duration lo scarto è quasi zero in tutti e tre",
                     xy=(0.03, 0.97), xycoords="axes fraction", va="top", fontsize=9.5,
                     color=GRIGIO, style="italic")

    casi_b = [("sentiero rettilineo", 0.0, GRIGIO),
              ("prima alti, poi giù (concavo)", 1.8, VERDE),
              ("prima giù, poi su (convesso)", -1.8, ROSSO)]
    for et, amp, c in casi_b:
        yy = _sentiero(y0, 3.0, amp, mesi)
        _, arit, geo, curv = _simula(yy, M)
        axes[1].plot(x, yy, lw=2.2, color=c)
        j = int(mesi * 0.52)
        axes[1].annotate(f"{et}\ncurvatura {_n(curv)} → scarto {_n(arit)}",
                         xy=(x[j], yy[j]), xytext=(0, 12 if amp >= 0 else -30),
                         textcoords="offset points", ha="center", fontsize=9.5,
                         color=c, fontweight="bold")
        print(f"    [graf 1B] {et:28s} curvatura {curv:+5.2f}  "
              f"scarto aritmetico {arit:+5.2f}  composto {geo:+5.2f}")
    axes[1].set_title("La curvatura sì")
    axes[1].annotate("tre sentieri con gli stessi estremi, 5% → 3%:\n"
                     "conta solo quanto stanno sopra o sotto la retta",
                     xy=(0.03, 0.97), xycoords="axes fraction", va="top", fontsize=9.5,
                     color=GRIGIO, style="italic")

    for ax in axes:
        ax.set_xlabel("anni dall'acquisto")
        ax.set_xlim(0, anni * 1.02); ax.set_ylim(0, 10.6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    axes[0].set_ylabel("rendimento a scadenza del fondo")
    fig.suptitle(f"Perché la regola funziona: indice a duration costante, acquisto al 5%, "
                 f"detenzione {it(anni, 1)} anni (2 × duration)",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(out); plt.close(fig)


def plot_curva_errore(ris, out):
    """Dove cade davvero il minimo dell'errore, gamba per gamba."""
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 8.4))
    for ax, (nome, g) in zip(axes.ravel(), ris["gambe"].items()):
        h = sorted(int(k) for k in g["fisso"])
        mae = [g["fisso"][str(k) if str(k) in g["fisso"] else k]["mae"] for k in h]
        c = COLORI[nome]
        ax.plot(h, mae, lw=2.2, color=c)
        hb = g["orizzonte_migliore"]
        mb = g["fisso"][hb]["mae"] if hb in g["fisso"] else g["fisso"][str(hb)]["mae"]
        ax.plot([hb], [mb], "o", ms=8, color=c)
        giu = mb > 0.16 * max(mae)
        ax.annotate(f"minimo a {hb} anni", xy=(hb, mb),
                    xytext=(0, -26 if giu else 16), ha="center",
                    textcoords="offset points", fontsize=9.5, color=c, fontweight="bold")
        d = g["duration"]
        ax.axvspan(2 * d["min"] - 1 / 12, 2 * d["max"] - 1 / 12, color=c, alpha=0.08)
        ax.axvline(g["orizzonte_2d"], color=GRIGIO, lw=1.4, ls="--")
        ax.annotate(f"2 × duration\n{it(g['orizzonte_2d'], 1)} anni",
                    xy=(g["orizzonte_2d"], max(mae) * 0.93), xytext=(6, 0),
                    textcoords="offset points", fontsize=9.5, color=GRIGIO)
        ax.set_title(nome)
        ax.set_xlabel("anni di detenzione"); ax.set_ylabel("errore medio, punti")
        ax.set_ylim(0, max(mae) * 1.08); ax.set_xlim(h[0], h[-1])
    fig.suptitle("Di quanto sbaglia il rendimento a scadenza, al variare della detenzione",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out); plt.close(fig)


def plot_regole(ris, out):
    """Le cinque regole a confronto, con l'orizzonte ricalcolato mese per mese."""
    regole = ["D (bullet)", "1,5D", "2D - 1/12", "2D - 1", "2,5D"]
    etich = ["D", "1,5 D", "2D", "2D − 1 anno", "2,5 D"]
    nomi = list(ris["gambe"])
    fig, ax = plt.subplots(figsize=(11.6, 6.0))
    w = 0.19
    xs = np.arange(len(regole))
    for i, nome in enumerate(nomi):
        v = ris["gambe"][nome]["variabile"]
        h = [v[r]["geometrico"]["mae"] if r in v else np.nan for r in regole]
        b = ax.bar(xs + (i - 1.5) * w, h, w * 0.92, color=COLORI[nome], label=nome)
        for rect, val in zip(b, h):
            if np.isfinite(val):
                ax.annotate(it(val), xy=(rect.get_x() + rect.get_width() / 2, val),
                            xytext=(0, 3), textcoords="offset points", ha="center",
                            fontsize=8.5, color=COLORI[nome], fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels(etich)
    ax.set_ylabel("errore assoluto medio, punti all'anno")
    ax.set_title("Quanti anni tenerlo: cinque regole, quattro indici", pad=34)
    ax.set_ylim(0, 3.95)
    ax.legend(frameon=False, fontsize=10, ncol=4, loc="lower center",
              bbox_to_anchor=(0.5, 1.005))
    ax.grid(axis="x", visible=False)
    ax.annotate("l'orizzonte è ricalcolato con la duration del mese di acquisto;\n"
                "più la barra è bassa, più il rendimento a scadenza iniziale ha indovinato",
                xy=(0.985, 0.975), xycoords="axes fraction", ha="right", va="top",
                fontsize=9.5, color=GRIGIO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def plot_convessita(ris, out):
    """Lo scarto residuo contro la curvatura del sentiero: pendenza attesa -1."""
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 8.4))
    for ax, nome in zip(axes.ravel(), ris["gambe"]):
        pt = PUNTI.get(nome)
        cv = ris["gambe"][nome]["convessita"]
        if pt is None or cv is None:
            ax.set_visible(False); continue
        x = np.array([a for a, _ in pt]); g = np.array([b for _, b in pt])
        c = COLORI[nome]
        ax.scatter(x, g, s=9, color=c, alpha=0.35, edgecolor="none")
        xx = np.linspace(x.min(), x.max(), 50)
        ax.plot(xx, cv["intercetta"] + cv["pendenza"] * xx, lw=2.2, color=c,
                label=f"osservata: pendenza {it(cv['pendenza'])}, R² {it(cv['r2'])}")
        ax.plot(xx, g.mean() - x.mean() + xx, lw=1.6, ls="--", color=GRIGIO,
                label="teoria: pendenza +1,00")
        ax.axhline(0, color=CHIARO, lw=1)
        ax.set_title(f"{nome}  ({cv['n']} mesi di acquisto)")
        ax.set_xlabel("curvatura del sentiero dei tassi, punti")
        ax.set_ylabel("scarto dal rendimento iniziale, punti")
        ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle("Tolta la curvatura del sentiero dei tassi, della regola non resta quasi niente",
                 fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out); plt.close(fig)


def plot_orizzonte(gambe, rendimenti, out):
    """L'orizzonte 2D non e' una costante: si muove col livello dei tassi."""
    fig, ax = plt.subplots(figsize=(11.2, 6.0))
    fine = {}
    for nome, M in SCADENZE.items():
        y = rendimenti[nome].dropna()
        D = pd.Series([duration_modificata(M, v / 100) for v in y], index=y.index)
        h = 2 * D - 1 / 12
        ax.plot(h.index.to_timestamp(), h.values, lw=1.9, color=COLORI[nome], label=nome)
        fine[nome] = (h.index[-1].to_timestamp(), float(h.iloc[-1]))
        if nome == "USA 20+":
            nota = (f"la duration di un titolo alla pari cresce quando i tassi scendono:\n"
                    f"nel {h.idxmin().year} il ventennale americano chiedeva {h.min():.0f} anni, "
                    f"nel {h.idxmax().year} ne chiedeva {h.max():.0f}")
    # le etichette di fine serie non devono sovrapporsi
    ordine = sorted(fine, key=lambda n: fine[n][1])
    prec = None
    for nome in ordine:
        x0, v = fine[nome]
        dy = 0.0
        if prec is not None and v - prec < 1.2:
            dy = 1.2 - (v - prec)
        prec = v + dy
        ax.annotate(f"{v:.0f}", xy=(x0, v), xytext=(6, dy * 9), textcoords="offset points",
                    va="center", fontsize=10, fontweight="bold", color=COLORI[nome])
    ax.set_ylabel("anni di detenzione richiesti (2 × duration)")
    ax.set_title("Quanto bisogna tenerlo, mese per mese")
    ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    ax.grid(axis="x", visible=False)
    ax.annotate(nota, xy=(0.985, 0.045), xycoords="axes fraction", ha="right",
                fontsize=9.5, color=GRIGIO, style="italic")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def grafici(gambe, rendimenti, ris):
    _stile()
    print(f"\n{'='*78}\n  GRAFICI\n{'='*78}")
    plot_meccanismo(os.path.join(OUT, "01_meccanismo.png"))
    plot_curva_errore(ris, os.path.join(OUT, "02_curva_errore.png"))
    plot_regole(ris, os.path.join(OUT, "03_regole.png"))
    plot_convessita(ris, os.path.join(OUT, "04_convessita.png"))
    plot_orizzonte(gambe, rendimenti, os.path.join(OUT, "05_orizzonte.png"))
    for f in sorted(os.listdir(OUT)):
        print(f"    {f}")


def main():
    os.makedirs(OUT, exist_ok=True)
    gambe, _extra, rendimenti = B.costruisci()
    ris = {"generato": dt.date.today().isoformat(), "gambe": {}}

    for nome, M in SCADENZE.items():
        nav, y = gambe[nome], rendimenti[nome]
        k = nav.index.intersection(y.index)
        nav, y = nav[k], y[k]
        logret = np.log(nav / nav.shift(1)).dropna()
        D = pd.Series([duration_modificata(M, v / 100) for v in y], index=y.index)
        print(f"\n{'='*78}\n{nome}  (titolo alla pari a {M} anni, {k.min()} -> {k.max()})\n{'='*78}")
        print(f"  duration modificata: mediana {D.median():.2f}, min {D.min():.2f} "
              f"({D.idxmin()}, tassi al {y[D.idxmin()]:.1f}%), max {D.max():.2f} "
              f"({D.idxmax()}, tassi al {y[D.idxmax()]:.1f}%)")
        print(f"  orizzonte previsto 2D-1/12: mediana {2*D.median()-1/12:.1f} anni, "
              f"da {2*D.min()-1/12:.1f} a {2*D.max()-1/12:.1f}")

        g = {"M": M, "duration": {"mediana": float(D.median()), "min": float(D.min()),
                                  "max": float(D.max())},
             "orizzonte_2d": float(2 * D.median() - 1 / 12),
             "fisso": {}, "variabile": {}}

        # ---- A. orizzonti fissi: dove sbaglia di meno?
        print("\n  A. orizzonte FISSO uguale per tutti i mesi di acquisto")
        print(f"     {'anni':>4s} {'n':>5s} {'medio':>7s} {'MAE':>6s} {'RMSE':>6s} "
              f"{'entro1':>7s} {'entro2':>7s}")
        migliore = None
        for h in ORIZZONTI:
            e, _ = errori(nav, logret, y, h * 12)
            if len(e) < 60:
                continue
            r = riassunto(e)
            g["fisso"][h] = r
            if migliore is None or r["mae"] < g["fisso"][migliore]["mae"]:
                migliore = h
            if h % 2 == 0 or h in (3, 5, 7, 9, 11, 13):
                print(f"     {h:4d} {r['n']:5d} {r['medio']:+7.2f} {r['mae']:6.2f} "
                      f"{r['rmse']:6.2f} {r['entro1']:6.1f}% {r['entro2']:6.1f}%")
        g["orizzonte_migliore"] = migliore
        print(f"     -> errore assoluto minimo a {migliore} anni "
              f"(MAE {g['fisso'][migliore]['mae']:.2f}), "
              f"la teoria ne prevede {2*D.median()-1/12:.1f}")

        # ---- B. orizzonte variabile, calcolato con la duration del mese
        print("\n  B. orizzonte VARIABILE, ricalcolato con la duration del mese di acquisto")
        print(f"     {'regola':>12s} {'n':>5s} {'medio':>7s} {'MAE':>6s} {'RMSE':>6s} "
              f"{'entro1':>7s} {'entro2':>7s}")
        for et, mult, meno in [("D (bullet)", 1.0, 0.0), ("1,5D", 1.5, 1/12),
                               ("2D - 1/12", 2.0, 1/12), ("2D - 1", 2.0, 1.0),
                               ("2,5D", 2.5, 1/12)]:
            vals, vals_cc = [], []
            for t in y.index:
                h = mult * D[t] - meno
                m = int(round(h * 12))
                if m < 24:
                    continue
                pos = nav.index.get_loc(t)
                if pos + m >= len(nav):
                    continue
                anni = m / 12
                geo = (nav.iloc[pos + m] / nav.iloc[pos]) ** (1 / anni) - 1
                vals.append(geo * 100 - y[t])
                seg = logret.iloc[pos:pos + m]
                vals_cc.append(seg.sum() / anni * 100 - np.log1p(y[t] / 100) * 100)
            if len(vals) < 60:
                continue
            e, ecc = pd.Series(vals), pd.Series(vals_cc)
            r, rcc = riassunto(e), riassunto(ecc)
            g["variabile"][et] = {"geometrico": r, "continuo": rcc}
            print(f"     {et:>12s} {r['n']:5d} {r['medio']:+7.2f} {r['mae']:6.2f} "
                  f"{r['rmse']:6.2f} {r['entro1']:6.1f}% {r['entro2']:6.1f}%")
        v2 = g["variabile"].get("2D - 1/12")
        if v2:
            print(f"     la stessa regola 2D sulla media dei rendimenti continui, "
                  f"che e' la grandezza del teorema: errore medio "
                  f"{v2['continuo']['medio']:+.2f}, MAE {v2['continuo']['mae']:.2f}")

        g["convessita"] = None
        ris["gambe"][nome] = g

    # ---- C. il meccanismo: la convessita' del sentiero dei tassi
    print(f"\n{'='*78}\n  C. LA CURVATURA SPIEGA LO SCARTO? (orizzonte 2D, media aritmetica)\n{'='*78}")
    for nome, M in SCADENZE.items():
        nav, y = gambe[nome], rendimenti[nome]
        k = nav.index.intersection(y.index)
        nav, y = nav[k], y[k]
        D = pd.Series([duration_modificata(M, v / 100) for v in y], index=y.index)
        ris["gambe"][nome]["convessita"] = test_convessita(
            nome, nav, y, D, np.log(nav / nav.shift(1)).dropna())

    # ---- D. roll-down si' / roll-down no, sulla stessa curva
    d7 = B.mensile("DGS7_fred_1969.csv"); d10 = B.mensile("DGS10.csv")
    ya = B.interp(d7, d10, 7, 10, 8.5).dropna()
    yv = B.interp(d7, d10, 7, 10, 8.5 - 1 / 12).dropna()
    kk = ya.index.intersection(yv.index)
    test_rolldown({"con roll-down (come lo studio)": B.indice(ya[kk], 8.5, yv[kk]),
                   "senza roll-down": B.indice(ya[kk], 8.5)}, rendimenti, ris)

    grafici(gambe, rendimenti, ris)

    with open(os.path.join(OUT, "sintesi.json"), "w", encoding="utf-8") as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, allow_nan=False)
    print(f"\n[2xD] sintesi -> {os.path.join(OUT, 'sintesi.json')}")


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("bond", STUDIO)
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)
    main()
