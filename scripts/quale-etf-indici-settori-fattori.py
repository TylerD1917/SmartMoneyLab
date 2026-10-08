# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 8: quale ETF, fra indici globali e scommesse
================================================================================

Due conti sullo stesso panel di mercati, che rispondono alla domanda pratica
dell'episodio: quanto pesa la scelta di DOVE investire, e si puo' azzeccare?

1. LA DISPERSIONE. Rendimento annuo composto di venticinque mercati nazionali
   su venticinque anni, con l'indice globale nel mucchio. Serve a mostrare due
   cose insieme: che la scelta del paese vale moltissimo, e che l'indice
   globale finisce per costruzione a meta' classifica, mai primo e mai ultimo.

2. LA ROTAZIONE. La stessa classifica rifatta su cinque quinquenni separati.
   Il paese in cima a un quinquennio non e' quello in cima al successivo, e
   alcuni passano dal primo posto all'ultimo. E' la risposta empirica a "allora
   compro il mercato che va meglio".

BASE DEI DATI
-------------
Panel costruito per l'articolo sul CAPE internazionale: indici MSCI Total
Return lordi, in dollari, mensili, da dicembre 2000. Total return significa
dividendi reinvestiti; il dollaro come metro comune serve a confrontare paesi
fra loro, e l'articolo lo dichiara perche' per un investitore in euro il cambio
cambia i numeri.

AGGREGATI ESCLUSI dalla classifica dei paesi (ACWI, Europa, mercati emergenti e
simili): sono panieri, non paesi, e metterli in graduatoria con la Finlandia
confonderebbe la domanda. ACWI resta, segnalato, come riferimento.

3. I SETTORI. Gli stessi due concetti applicati ai comparti invece che ai
   paesi: quanto hanno reso in venticinque anni e come si ribalta la classifica
   spezzando il periodo a meta'. Il risultato e' piu' netto di quello
   geografico, perche' un settore e' molto meno diversificato di un paese.

4. I FATTORI. Ogni fattore contro il PROPRIO mercato, come rapporto fra i due.
   Il rapporto e' immune al cambio, perche' numeratore e denominatore sono
   nella stessa valuta, ed e' l'unico modo onesto di mostrare la cosa che conta
   davvero: non se il premio esista, ma per quanto tempo puo' non pagare.

OUTPUT in public/charts/quale-etf-indici-settori-fattori/
---------------------------------------------------------
  01_dispersione_paesi.png   quanto cambia il risultato a seconda del paese
  02_rotazione.png           chi comanda cambia a ogni quinquennio
  03_settori.png             il settore migliore di oggi non era quello di ieri
  04_fattori.png             quanto a lungo un fattore puo' restare indietro
  summary.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "charts" / "quale-etf-indici-settori-fattori"
PANEL = ROOT / "data" / "processed" / "returns_panel_wide.csv"
UNIVERSO = ROOT / "data" / "cache" / "correlation_universe_monthly.csv"
QUALITY = ROOT / "data" / "cache" / "yf_proxy_qual_quality.csv"
MINVOL = ROOT / "data" / "cache" / "yf_proxy_usmv_minvol.csv"
MOM_EU = ROOT / "data" / "Indici_Eurozona" / "MSCI_Euro_Momentum1994.csv"
EUROPA = ROOT / "data" / "Indici_Eurozona" / "Msci_Europe_1969_EUR.csv"

# settori: il periodo comune parte dai semiconduttori (luglio 2001)
SETTORI = {"Semiconduttori": "Semiconduttori", "Nasdaq 100": "Nasdaq 100",
           "Healthcare": "Sanità", "Energy": "Energia",
           "Consumer Staples": "Beni di consumo", "Financials": "Banche e finanza"}
MERCATO_USA = "USA (S&P 500)"
SET_INIZIO, SET_META, SET_FINE = "2001-07", "2013-12", "2026-08"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

GLOBALE = "ACWI"
AGGREGATI = {"ACWI", "Asia ex Japan", "EM Asia", "Emerging Markets",
             "Europe", "Nordics", "Developed Markets Large"}
IT = {"South Korea": "Corea del Sud", "Taiwan": "Taiwan", "Thailand": "Thailandia",
      "Indonesia": "Indonesia", "India": "India", "Denmark": "Danimarca",
      "South Africa": "Sudafrica", "Australia": "Australia", "Norway": "Norvegia",
      "Brazil": "Brasile", "US Large": "Stati Uniti", "Canada": "Canada",
      "Austria": "Austria", "Switzerland": "Svizzera", "Netherlands": "Paesi Bassi",
      "Sweden": "Svezia", "China": "Cina", "Spain": "Spagna", "Germany": "Germania",
      "France": "Francia", "United Kingdom": "Regno Unito", "Italy": "Italia",
      "Japan": "Giappone", "Belgium": "Belgio", "Finland": "Finlandia",
      "ACWI": "Indice globale (ACWI)"}

FINESTRE = [("2001-01", "2005-12"), ("2006-01", "2010-12"), ("2011-01", "2015-12"),
            ("2016-01", "2020-12"), ("2021-01", "2026-04")]
# paesi da evidenziare nella rotazione: quelli che cambiano piu' posizione
EVIDENZIATI = {"Indonesia": "#d97706", "Austria": "#059669", "Belgium": "#7c3aed",
               "China": "#dc2626", "US Large": "#0891b2", "Taiwan": "#be185d"}


# ----------------------------------------------------------------- dati
def panel():
    righe = list(csv.DictReader(open(PANEL, encoding="utf-8-sig")))
    per_mese = {r["month"]: r for r in righe}
    colonne = [c for c in righe[0] if c != "month"]
    return righe, per_mese, colonne


def valore(per_mese, mese, col):
    try:
        v = float(per_mese[mese][col])
        return v if v > 0 else None
    except (ValueError, TypeError, KeyError):
        return None


def anni_fra(a: str, b: str) -> float:
    return ((int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])) / 12


def cagr_periodo(per_mese, colonne, a: str, b: str) -> dict[str, float]:
    n = anni_fra(a, b)
    out = {}
    for c in colonne:
        v0, v1 = valore(per_mese, a, c), valore(per_mese, b, c)
        if v0 and v1:
            out[c] = (v1 / v0) ** (1 / n) - 1
    return out


def serie_universo(col: str) -> dict[str, float]:
    """Una colonna del panel mensile di correlazione, chiave AAAA-MM."""
    out = {}
    for r in csv.DictReader(open(UNIVERSO, encoding="utf-8-sig")):
        v = (r.get(col) or "").strip()
        if v:
            try:
                out[r["date"][:7]] = float(v)
            except ValueError:
                pass
    return out


def serie_yf(path: Path) -> dict[str, float]:
    """Chiusure aggiustate di un CSV Yahoo, ridotte a un valore per mese."""
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        v = (r.get("AdjClose") or "").strip()
        if v:
            try:
                out[r["Date"][:7]] = float(v)
            except ValueError:
                pass
    return out


def serie_msci(path: Path) -> dict[str, float]:
    """CSV MSCI con data MM/AAAA e un indice ribasato a 10.000 all'origine."""
    out = {}
    for r in csv.reader(open(path, encoding="utf-8-sig")):
        if not r or r[0].strip() in ("Data", ""):
            continue
        m, a = r[0].split("/")
        out[f"{a}-{m}"] = float(r[1])
    return out


def cagr_fra(s: dict[str, float], a: str, b: str) -> float | None:
    v0, v1 = s.get(a), s.get(b)
    if not v0 or not v1:
        return None
    return (v1 / v0) ** (1 / anni_fra(a, b)) - 1


def relativa(fattore: dict, mercato: dict, nome: str) -> dict:
    """Rapporto fra fattore e mercato, base 100, piu' il ritardo peggiore.

    Il 'ritardo' e' il drawdown del rapporto: quanto il fattore e' rimasto
    indietro rispetto al suo massimo relativo, e quanto ci ha messo a
    recuperarlo. E' il numero che conta per chi deve tenere lo strumento in
    portafoglio, molto piu' del premio medio.
    """
    comuni = sorted(set(fattore) & set(mercato))
    a, z = comuni[0], comuni[-1]
    serie = [(d, (fattore[d] / fattore[a]) / (mercato[d] / mercato[a]) * 100) for d in comuni]
    picco, quando_picco = serie[0][1], serie[0][0]
    peggio, da, fino = 0.0, serie[0][0], serie[0][0]
    # Il livello del picco DA CUI parte il ritardo peggiore va congelato: usare
    # "picco" a fine ciclo significherebbe confrontarsi con il massimo di
    # sempre, e far risultare non recuperato un ritardo colmato vent'anni fa.
    livello_picco = serie[0][1]
    for d, v in serie:
        if v > picco:
            picco, quando_picco = v, d
        if v / picco - 1 < peggio:
            peggio, da, fino, livello_picco = v / picco - 1, quando_picco, d, picco
    recupero = next((d for d, v in serie if d > fino and v >= livello_picco), None)
    return {"nome": nome, "da": a, "a": z, "anni": round(anni_fra(a, z), 1),
            "cagr_fattore": cagr_fra(fattore, a, z), "cagr_mercato": cagr_fra(mercato, a, z),
            "differenza_punti": (cagr_fra(fattore, a, z) - cagr_fra(mercato, a, z)) * 100,
            "ritardo_peggiore": peggio, "ritardo_da": da, "ritardo_fino": fino,
            "recuperato": recupero,
            "anni_per_recuperare": round(anni_fra(da, recupero), 1) if recupero else None,
            "serie": serie}


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_dispersione(paesi: dict, globale: float, a: str, b: str, out: Path):
    ordine = sorted(paesi.items(), key=lambda x: x[1])
    nomi = [IT.get(k, k) for k, _ in ordine]
    vals = [v * 100 for _, v in ordine]
    fig, ax = plt.subplots(figsize=(9.5, 8.2))
    ax.barh(nomi, vals, color=GRIGIO, alpha=0.55, height=0.72)
    ax.axvline(globale * 100, color=NAVY, lw=2.0)
    ax.annotate(f"indice globale\n{globale * 100:.1f}%".replace(".", ","),
                xy=(globale * 100, 1.2), xytext=(14, 0),
                textcoords="offset points", color=NAVY, fontweight="bold",
                fontsize=10.5, va="center")
    for i, v in enumerate(vals):
        ax.annotate(f"{v:.1f}".replace(".", ",") + "%", xy=(v, i), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=GRIGIO)
    ax.set_title(f"Quanto ha reso ogni mercato, {a[:4]}-{b[:4]}")
    ax.set_xlabel("rendimento annuo composto")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_xlim(0, max(vals) * 1.16)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_rotazione(classifiche: list[dict], out: Path):
    """Bump chart: come si muove la posizione in classifica di quinquennio in
    quinquennio. L'asse y e' rovesciato cosi' il primo posto sta in alto."""
    etichette = [f"{a[:4]}-{b[:4]}" for a, b in FINESTRE]
    n = len(classifiche[0]) - 1
    fig, ax = plt.subplots(figsize=(10, 6.2))

    for paese in classifiche[0]:
        y = [c[paese] for c in classifiche]
        colore = NAVY if paese == GLOBALE else EVIDENZIATI.get(paese)
        ev = colore is not None
        ax.plot(range(len(y)), y, color=colore or "#cbd5e1",
                lw=2.6 if ev else 1.0, alpha=1.0 if ev else 0.7,
                marker="o", ms=6 if ev else 3, zorder=3 if ev else 1)
        if ev:
            for x, lato, ha in ((0, -10, "right"), (len(y) - 1, 10, "left")):
                ax.annotate(IT.get(paese, paese), xy=(x, y[x]), xytext=(lato, 0),
                            textcoords="offset points", ha=ha, va="center",
                            fontsize=9.5, fontweight="bold", color=colore)

    ax.set_xticks(range(len(etichette)))
    ax.set_xticklabels(etichette)
    ax.set_xlim(-1.35, len(etichette) - 0.35)
    ax.set_ylim(n + 0.6, 0.4)
    ax.set_yticks([1, 5, 10, 15, 20, 25])
    ax.set_ylabel("posizione in classifica")
    ax.set_title("Il mercato migliore di un quinquennio non è quello del successivo")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def _sdoppia(valori: list[float], minimo: float) -> list[float]:
    """Posizioni verticali delle etichette, allontanate quando si toccano.

    Senza questo, settori con rendimenti vicini (sanita' 7,0 e Nasdaq 6,8)
    stampano un'etichetta sopra l'altra e diventano illeggibili entrambe.
    Le etichette si spostano, i punti sulla linea no.
    """
    ordine = sorted(range(len(valori)), key=lambda i: valori[i])
    pos = list(valori)
    for k in range(1, len(ordine)):
        i, prec = ordine[k], ordine[k - 1]
        if pos[i] - pos[prec] < minimo:
            pos[i] = pos[prec] + minimo
    return pos


def plot_settori(righe: list[dict], mercato: dict, out: Path):
    """Slope chart: rendimento annuo nella prima e nella seconda meta'."""
    fig, ax = plt.subplots(figsize=(9.8, 6.4))
    x0, x1 = 0.0, 1.0
    voci = sorted(righe, key=lambda r: -r["seconda"]) + [dict(mercato, _mercato=True)]
    y0 = [r["prima"] * 100 for r in voci]
    y1 = [r["seconda"] * 100 for r in voci]
    et0, et1 = _sdoppia(y0, 1.25), _sdoppia(y1, 1.25)

    for r, a0, a1, e0, e1 in zip(voci, y0, y1, et0, et1):
        m = r.get("_mercato", False)
        colore = NAVY if m else GOLD
        ax.plot([x0, x1], [a0, a1], color=colore, lw=3.0 if m else 2.4,
                marker="o", ms=8 if m else 7, zorder=4 if m else 3)
        ax.annotate(f"{r['nome']}  {a0:.1f}%".replace(".", ","), xy=(x0, e0), xytext=(-12, 0),
                    textcoords="offset points", ha="right", va="center",
                    fontsize=10.5 if m else 10, fontweight="bold", color=colore)
        ax.annotate(f"{a1:.1f}%  {r['nome']}".replace(".", ","), xy=(x1, e1), xytext=(12, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=10.5 if m else 10, fontweight="bold", color=colore)

    ax.set_xlim(-0.72, 1.72)
    ax.set_xticks([x0, x1])
    ax.set_xticklabels([f"{SET_INIZIO[:4]}-{SET_META[:4]}", f"{SET_META[:4]}-{SET_FINE[:4]}"],
                       fontsize=11.5, fontweight="bold")
    ax.set_ylabel("rendimento annuo composto")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_title("Lo stesso settore, due mezzi periodi, due storie diverse")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_fattori(relazioni: list[dict], out: Path):
    """Ogni fattore diviso il proprio mercato, base 100 alla partenza."""
    colori = ["#d97706", "#059669", "#7c3aed", "#dc2626", "#0891b2"]
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    ax.axhline(100, color=GRIGIO, lw=1.2)
    for r, colore in zip(relazioni, colori):
        xs = [int(d[:4]) + (int(d[5:7]) - 1) / 12 for d, _ in r["serie"]]
        ys = [v for _, v in r["serie"]]
        ax.plot(xs, ys, color=colore, lw=2.0, label=r["nome"])
        ax.annotate(r["nome"], xy=(xs[-1], ys[-1]), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=9.5,
                    fontweight="bold", color=colore)
    ax.set_title("Quanto a lungo un fattore può restare indietro dal suo mercato")
    ax.set_ylabel("fattore diviso mercato, base 100 alla partenza")
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(0.5, 0.75, 1.0, 1.5, 2.0, 3.0)))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.margins(x=0.13)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    righe, per_mese, colonne = panel()
    a, b = righe[0]["month"], righe[-1]["month"]

    tutto = cagr_periodo(per_mese, colonne, a, b)
    paesi = {k: v for k, v in tutto.items() if k not in AGGREGATI}
    globale = tutto[GLOBALE]

    classifiche = []
    for fa, fb in FINESTRE:
        r = cagr_periodo(per_mese, colonne, fa, fb)
        solo = {k: v for k, v in r.items() if k not in AGGREGATI}
        ordine = sorted(solo.items(), key=lambda x: -x[1])
        cl = {k: i + 1 for i, (k, _) in enumerate(ordine)}
        # posizione che l'indice globale occuperebbe, senza togliere slot a nessuno
        cl[GLOBALE] = sum(1 for v in solo.values() if v > r[GLOBALE]) + 1
        classifiche.append(cl)

    plot_dispersione(paesi, globale, a, b, OUT / "01_dispersione_paesi.png")
    plot_rotazione(classifiche, OUT / "02_rotazione.png")

    # --- settori -------------------------------------------------------
    sp = serie_universo(MERCATO_USA)
    settori = []
    for col, nome in SETTORI.items():
        s_ = serie_universo(col)
        settori.append({"colonna": col, "nome": nome,
                        "intero": cagr_fra(s_, SET_INIZIO, SET_FINE),
                        "prima": cagr_fra(s_, SET_INIZIO, SET_META),
                        "seconda": cagr_fra(s_, SET_META, SET_FINE)})
    mercato = {"nome": "S&P 500", "intero": cagr_fra(sp, SET_INIZIO, SET_FINE),
               "prima": cagr_fra(sp, SET_INIZIO, SET_META),
               "seconda": cagr_fra(sp, SET_META, SET_FINE)}
    plot_settori(settori, mercato, OUT / "03_settori.png")

    # --- fattori -------------------------------------------------------
    relazioni = [
        relativa(serie_universo("Value (S&P500)"), sp, "Value USA"),
        relativa(serie_universo("Small Cap (Russell 2000)"), sp, "Small cap USA"),
        relativa(serie_yf(QUALITY), sp, "Quality USA"),
        relativa(serie_yf(MINVOL), sp, "Minima volatilità USA"),
        relativa(serie_msci(MOM_EU), serie_msci(EUROPA), "Momentum Europa"),
    ]
    plot_fattori(relazioni, OUT / "04_fattori.png")

    migliore = max(paesi, key=paesi.get)
    peggiore = min(paesi, key=paesi.get)
    sotto = sum(1 for v in paesi.values() if v < globale)
    sommario = {
        "fonte": "data/processed/returns_panel_wide.csv, indici MSCI Total Return "
                 "lordi in dollari, mensili (panel costruito per l'articolo sul CAPE "
                 "internazionale)",
        "periodo": {"da": a, "a": b, "anni": round(anni_fra(a, b), 1)},
        "n_paesi": len(paesi),
        "globale": {"indice": GLOBALE, "cagr": globale,
                    "paesi_sotto": sotto, "paesi_sopra": len(paesi) - sotto},
        "migliore": {"paese": migliore, "cagr": paesi[migliore]},
        "peggiore": {"paese": peggiore, "cagr": paesi[peggiore]},
        "distanza_punti": (paesi[migliore] - paesi[peggiore]) * 100,
        "classifica_completa": {k: round(v, 4) for k, v in
                                sorted(paesi.items(), key=lambda x: -x[1])},
        "quinquenni": [],
        "settori": {
            "fonte": "data/cache/correlation_universe_monthly.csv, chiusure mensili "
                     "aggiustate per i dividendi, in dollari",
            "periodo": {"da": SET_INIZIO, "meta": SET_META, "a": SET_FINE},
            "mercato": mercato,
            "voci": sorted(settori, key=lambda r: -r["intero"]),
        },
        "fattori": {
            "nota": "ogni fattore e' rapportato al PROPRIO mercato; il rapporto e' "
                    "immune al cambio perche' le due gambe sono nella stessa valuta",
            "voci": [{k: v for k, v in r.items() if k != "serie"} for r in relazioni],
        },
    }
    for (fa, fb), cl in zip(FINESTRE, classifiche):
        r = cagr_periodo(per_mese, colonne, fa, fb)
        ordine = sorted(((k, v) for k, v in r.items() if k not in AGGREGATI),
                        key=lambda x: -x[1])
        sommario["quinquenni"].append({
            "da": fa, "a": fb, "acwi": round(r[GLOBALE], 4),
            "posizione_acwi": cl[GLOBALE],
            "primi_tre": [{"paese": k, "cagr": round(v, 4)} for k, v in ordine[:3]],
            "ultimi_due": [{"paese": k, "cagr": round(v, 4)} for k, v in ordine[-2:]]})
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")

    print(f"[ok] 4 grafici + summary.json in {OUT}\n")
    print(f"{len(paesi)} mercati nazionali, {a} -> {b} ({anni_fra(a, b):.1f} anni)")
    print(f"  migliore: {IT.get(migliore, migliore)} {paesi[migliore]:+.2%}")
    print(f"  peggiore: {IT.get(peggiore, peggiore)} {paesi[peggiore]:+.2%}")
    print(f"  distanza: {sommario['distanza_punti']:.1f} punti all'anno")
    print(f"  indice globale {globale:+.2%}: {sotto} paesi sotto, "
          f"{len(paesi) - sotto} sopra")
    print("\nposizione dell'indice globale nei cinque quinquenni (su "
          f"{len(classifiche[0]) - 1} paesi):")
    for (fa, fb), q in zip(FINESTRE, sommario["quinquenni"]):
        primi = ", ".join(f"{IT.get(t['paese'], t['paese'])} {t['cagr']:+.1%}"
                          for t in q["primi_tre"])
        print(f"   {fa[:4]}-{fb[:4]}  globale {q['acwi']:+6.2%} (pos. {q['posizione_acwi']:>2})"
              f"  | migliori: {primi}")

    print(f"\nSETTORI {SET_INIZIO} -> {SET_FINE} (meta' a {SET_META})")
    print(f"   {'settore':18s} {'intero':>8s} {'prima':>9s} {'seconda':>9s}")
    for r in sommario["settori"]["voci"] + [mercato]:
        print(f"   {r['nome']:18s} {r['intero']:>+8.2%} {r['prima']:>+9.2%} {r['seconda']:>+9.2%}")

    print("\nFATTORI, ciascuno contro il proprio mercato")
    for r in relazioni:
        rec = (f"recuperato {r['recuperato']} dopo {r['anni_per_recuperare']} anni"
               if r["recuperato"] else "non ancora recuperato")
        print(f"   {r['nome']:22s} {r['da']} -> {r['a']} ({r['anni']:>4.1f}a)  "
              f"fattore {r['cagr_fattore']:+6.2%}  mercato {r['cagr_mercato']:+6.2%}  "
              f"scarto {r['differenza_punti']:+5.2f} punti")
        print(f"   {'':22s} ritardo peggiore {r['ritardo_peggiore']:+6.1%} "
              f"dal {r['ritardo_da']} al {r['ritardo_fino']}, {rec}")


if __name__ == "__main__":
    main()
