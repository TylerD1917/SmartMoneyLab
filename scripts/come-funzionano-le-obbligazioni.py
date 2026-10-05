# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 5: come funzionano le obbligazioni
=====================================================================

Tre conti, tre grafici. L'episodio 3 ha gia' usato il pull to par e il 2022:
qui si va piu' a fondo, su duration, curva dei rendimenti e caso italiano.

1. LA DURATION AL LAVORO. Prezzo esatto (valore attuale dei flussi) di titoli
   a 2, 5, 10 e 30 anni quando i tassi si muovono. Lo script confronta anche
   la variazione VERA con quella stimata dalla regola pratica
   "duration x variazione dei tassi": lo scarto e' la convessita', e dirlo
   evita di spacciare un'approssimazione per una legge.

2. LA CURVA DEI RENDIMENTI americana a tre date: la piu' inclinata e la piu'
   invertita del campione, e l'ultima disponibile. Serie FRED da 3 mesi a 30
   anni in `data/Bonds/`.

3. IL DECENNALE ITALIANO dal 2016, che e' il grafico che spiega a un lettore
   italiano perche' chi ha comprato nel 2021 ha perso e chi compra oggi
   incassa.

NOTA SULLE FONTI DGS
--------------------
`DGS10.csv` arriva piu' avanti di `fred_dgs10.csv`: per il decennale si usa
il primo. Caricarli in ordine alfabetico farebbe vincere il secondo e
accorcerebbe di quattro mesi tutte le curve, senza che nessuno se ne accorga.

OUTPUT in public/charts/come-funzionano-le-obbligazioni/
--------------------------------------------------------
  01_duration.png     quanto scende il prezzo per ogni punto di tassi
  02_curva.png        la curva dei rendimenti in tre momenti
  03_btp_decennale.png il rendimento del decennale italiano dal 2016
  summary.json
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
BONDS = ROOT / "data" / "Bonds"
OUT = ROOT / "public" / "charts" / "come-funzionano-le-obbligazioni"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

SCADENZE = [2, 5, 10, 30]
TASSO_BASE = 0.035          # cedola e rendimento di partenza: titolo alla pari
MOSSE = [-0.02, -0.01, 0.01, 0.02]
TENORI = [("DGS3MO", 0.25, "3m"), ("DGS1", 1, "1a"), ("DGS2", 2, "2a"),
          ("DGS5", 5, "5a"), ("DGS10", 10, "10a"), ("DGS20", 20, "20a"),
          ("DGS30", 30, "30a")]


# ----------------------------------------------------------------- dati
def leggi(nome: str) -> dict[str, float]:
    with io.open(BONDS / nome, encoding="utf-8-sig") as fh:
        righe = list(csv.reader(fh))
    return {r[0]: float(r[1]) for r in righe[1:] if len(r) > 1 and r[1] not in ("", ".")}


def curve() -> tuple[dict[str, dict[str, float]], list[str]]:
    s = {}
    for chiave, _, _ in TENORI:
        # per il decennale la serie lunga, non quella che si ferma prima
        s[chiave] = leggi("DGS10.csv" if chiave == "DGS10" else f"{chiave}.csv")
    comuni = set(s[TENORI[0][0]])
    for chiave, _, _ in TENORI[1:]:
        comuni &= set(s[chiave])
    return s, sorted(comuni)


# ----------------------------------------------------------------- conti
def prezzo(anni: int, cedola: float, rendimento: float, nominale: float = 100.0) -> float:
    c = cedola * nominale
    v = sum(c / (1 + rendimento) ** k for k in range(1, anni + 1))
    return v + nominale / (1 + rendimento) ** anni


def duration_macaulay(anni: int, cedola: float, rendimento: float) -> float:
    c = cedola * 100.0
    p = prezzo(anni, cedola, rendimento)
    num = sum(k * c / (1 + rendimento) ** k for k in range(1, anni + 1))
    num += anni * 100.0 / (1 + rendimento) ** anni
    return num / p


def tabella_duration() -> list[dict]:
    righe = []
    for anni in SCADENZE:
        p0 = prezzo(anni, TASSO_BASE, TASSO_BASE)       # alla pari: 100
        dmac = duration_macaulay(anni, TASSO_BASE, TASSO_BASE)
        dmod = dmac / (1 + TASSO_BASE)
        voce = {"anni": anni, "prezzo_iniziale": p0,
                "duration_macaulay": dmac, "duration_modificata": dmod, "mosse": {}}
        for m in MOSSE:
            p1 = prezzo(anni, TASSO_BASE, TASSO_BASE + m)
            vera = p1 / p0 - 1
            stimata = -dmod * m          # la regola pratica
            voce["mosse"][f"{m:+.2f}"] = {
                "prezzo": p1, "variazione_vera": vera, "variazione_stimata": stimata,
                "scarto_punti": (vera - stimata) * 100}
        righe.append(voce)
    return righe


def caso_btp(btp: dict[str, float]) -> dict:
    """Chi ha comprato il decennale italiano al minimo e lo ha visto al massimo.

    Un titolo emesso alla pari con cedola pari al rendimento di allora, riprezzato
    al rendimento del massimo con la vita residua di quel momento. Il conto serve a
    dare un ordine di grandezza alla perdita di prezzo: non replica un BTP specifico
    (cedole semestrali, rateo, scadenza esatta) e non va letto come tale.
    """
    dmin, dmax = "2020-12-01", "2023-10-01"
    y0, y1 = btp[dmin] / 100, btp[dmax] / 100
    anni_passati = (int(dmax[:4]) - int(dmin[:4])) + (int(dmax[5:7]) - int(dmin[5:7])) / 12
    residua = round(10 - anni_passati)          # anni interi, il modello e' annuale
    p1 = prezzo(residua, y0, y1)
    return {"acquisto": {"data": dmin, "rendimento": btp[dmin], "prezzo": 100.0},
            "vendita": {"data": dmax, "rendimento": btp[dmax], "prezzo": p1,
                        "vita_residua_anni": residua},
            "variazione_prezzo": p1 / 100 - 1,
            "anni_trascorsi": anni_passati,
            "nota": "titolo annuale stilizzato emesso alla pari, non un BTP specifico"}


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_duration(righe, out: Path):
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    larg = 0.2
    colori = {"+0.01": GOLD, "+0.02": ROSSO, "-0.01": "#60a5fa", "-0.02": NAVY}
    ordine = ["-0.02", "-0.01", "+0.01", "+0.02"]
    etich = {"-0.02": "tassi −2 punti", "-0.01": "tassi −1 punto",
             "+0.01": "tassi +1 punto", "+0.02": "tassi +2 punti"}
    x = range(len(righe))
    for i, m in enumerate(ordine):
        vals = [r["mosse"][m]["variazione_vera"] * 100 for r in righe]
        pos = [k + (i - 1.5) * larg for k in x]
        b = ax.bar(pos, vals, width=larg, color=colori[m], label=etich[m])
        for rect, v in zip(b, vals):
            ax.annotate(f"{v:+.0f}%", xy=(rect.get_x() + rect.get_width() / 2, v),
                        xytext=(0, 3 if v >= 0 else -13), textcoords="offset points",
                        ha="center", fontsize=8.5, color=GRIGIO)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{r['anni']} anni\n(duration {r['duration_modificata']:.1f})".replace(".", ",")
                        for r in righe])
    ax.axhline(0, color=GRIGIO, lw=0.9)
    ax.set_title("Quanto si muove il prezzo di un'obbligazione quando si muovono i tassi")
    ax.set_ylabel("variazione del prezzo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(frameon=False, ncol=4, fontsize=9.5, loc="upper center")
    ax.set_ylim(-45, 75)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_curva(s, date_scelte, out: Path):
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    x = [t[1] for t in TENORI]
    MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
            "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    def ita(d):
        return f"{int(d[8:])} {MESI[int(d[5:7]) - 1]} {d[:4]}"
    stili = [(GRIGIO, "--", "o"), (ROSSO, "-", "s"), (NAVY, "-", "^")]
    for (etichetta, d), (colore, ls, mk) in zip(date_scelte, stili):
        y = [s[chiave][d] for chiave, _, _ in TENORI]
        ax.plot(x, y, color=colore, ls=ls, marker=mk, ms=5, lw=2.0,
                label=f"{etichetta}, {ita(d)}")
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([t[2] for t in TENORI])
    ax.minorticks_off()
    ax.set_title("La curva dei rendimenti: quanto rende prestare, secondo la durata")
    ax.set_xlabel("durata del prestito")
    ax.set_ylabel("rendimento annuo")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_btp(serie, out: Path):
    date = sorted(serie)
    x = [int(d[:4]) + (int(d[5:7]) - 1) / 12 for d in date]
    y = [serie[d] for d in date]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(x, y, color=NAVY, lw=2.0)
    ax.fill_between(x, y, 0, color=NAVY, alpha=0.10)
    imin = min(range(len(y)), key=lambda i: y[i])
    ax.annotate(f"minimo {y[imin]:.2f}%".replace(".", ","), xy=(x[imin], y[imin]),
                xytext=(10, -20), textcoords="offset points", color=ROSSO,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=ROSSO, lw=1.2))
    ax.annotate(f"{y[-1]:.2f}%".replace(".", ","), xy=(x[-1], y[-1]), xytext=(-6, 10),
                textcoords="offset points", color=NAVY, fontweight="bold", ha="right")
    ax.set_title(f"Il rendimento del BTP decennale, {date[0][:4]}-{date[-1][:4]}")
    ax.set_ylabel("rendimento a scadenza")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(0, max(y) * 1.25)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()

    righe = tabella_duration()
    s, comuni = curve()
    spread = {d: s["DGS10"][d] - s["DGS3MO"][d] for d in comuni}
    piu_inv = min(spread, key=spread.get)
    piu_incl = max(spread, key=spread.get)
    ultima = comuni[-1]
    date_scelte = [("curva inclinata", piu_incl), ("curva invertita", piu_inv),
                   ("ultima disponibile", ultima)]
    btp = leggi("10Y_Italy.csv")

    plot_duration(righe, OUT / "01_duration.png")
    plot_curva(s, date_scelte, OUT / "02_curva.png")
    plot_btp(btp, OUT / "03_btp_decennale.png")

    dbtp = sorted(btp)
    caso = caso_btp(btp)
    imin = min(dbtp, key=lambda d: btp[d])
    sommario = {
        "titolo_di_esempio": {"cedola": TASSO_BASE, "prezzo_iniziale": 100.0,
                              "nota": "titolo alla pari, cedola annua uguale al rendimento"},
        "duration": righe,
        "curva": {
            "fonte": "FRED, serie DGS3MO/1/2/5/10/20/30 in data/Bonds/",
            "date": {e: d for e, d in date_scelte},
            "spread_10a_meno_3m": {e: round(spread[d], 2) for e, d in date_scelte},
            "valori": {e: {t[2]: s[t[0]][d] for t in TENORI} for e, d in date_scelte},
        },
        "btp_decennale": {
            "fonte": "FRED IRLTLT01ITM156N, rendimento dei titoli di Stato italiani a lungo termine",
            "da": dbtp[0], "a": dbtp[-1],
            "minimo": {"data": imin, "valore": btp[imin]},
            "massimo": {"data": max(dbtp, key=lambda d: btp[d]),
                        "valore": max(btp.values())},
            "ultimo": {"data": dbtp[-1], "valore": btp[dbtp[-1]]},
            "caso_minimo_massimo": caso,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 3 grafici + summary.json in {OUT}\n")
    print("DURATION — titolo alla pari con cedola 3,5%")
    for r in righe:
        m = r["mosse"]["+0.01"]
        print(f"  {r['anni']:>2} anni  duration mod. {r['duration_modificata']:>5.2f}  "
              f"tassi +1 punto: prezzo {m['prezzo']:>6.2f}  vera {m['variazione_vera']:>+6.2%}  "
              f"regola pratica {m['variazione_stimata']:>+6.2%}  scarto {m['scarto_punti']:>+4.2f} punti")
    print("\nCURVA DEI RENDIMENTI")
    for e, d in date_scelte:
        print(f"  {e:20} {d}  10 anni meno 3 mesi: {spread[d]:+.2f} punti  "
              + "  ".join(f"{t[2]}:{s[t[0]][d]:.2f}" for t in TENORI))
    b = sommario["btp_decennale"]
    print(f"\nBTP DECENNALE  {b['da']} -> {b['a']}: minimo {b['minimo']['valore']:.2f}% "
          f"({b['minimo']['data']}), massimo {b['massimo']['valore']:.2f}%, "
          f"ultimo {b['ultimo']['valore']:.2f}% ({b['ultimo']['data']})")
    c = b["caso_minimo_massimo"]
    print(f"  caso stilizzato: comprato {c['acquisto']['data']} a 100 con cedola "
          f"{c['acquisto']['rendimento']:.2f}%, rivisto {c['vendita']['data']} con "
          f"rendimento {c['vendita']['rendimento']:.2f}% e {c['vendita']['vita_residua_anni']} "
          f"anni residui: prezzo {c['vendita']['prezzo']:.2f} ({c['variazione_prezzo']:+.1%})")


if __name__ == "__main__":
    main()
