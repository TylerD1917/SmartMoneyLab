# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 2: prima di investire
========================================================

L'episodio risponde a "con quali soldi". La parte misurabile e' una sola, ed
e' quella che giustifica la regola sull'orizzonte temporale: quanto spesso un
indice azionario mondiale chiude in perdita, in funzione di quanti anni lo si
tiene, e quanto tempo ha richiesto storicamente tornare in pari dopo un calo.

DATI
----
- MSCI World total return in EURO, rendimenti mensili: letti da
  `public/tools/prestito-investimento-serie.json`, la stessa serie che
  alimenta il simulatore prestito-vs-investimento e l'episodio 1.
- Inflazione italiana annua: `data/Valute/FPCPITOTLZGITA.csv` (FRED).

SCELTE DICHIARATE
-----------------
- Due misure affiancate: NOMINALE (sui dati mensili, molte finestre) e REALE
  al netto dell'inflazione italiana (sui dati annuali, perche' la serie CPI
  e' annuale). Il nominale da' solo meta' della risposta: un capitale che
  torna uguale dopo cinque anni ha perso potere d'acquisto.
- Finestre mobili sovrapposte a passo mensile (nominale) e annuale (reale).
  Si sovrappongono, quindi non sono osservazioni indipendenti: servono a
  descrivere cosa e' accaduto, non a stimare una probabilita' futura.
- Tutto al lordo di costi e imposte, come l'episodio 1.

OUTPUT in public/charts/prima-di-investire-fondo-emergenza/
-----------------------------------------------------------
  01_perdita_per_orizzonte.png  % di finestre chiuse in perdita, per orizzonte
  02_sotto_acqua.png            la curva sott'acqua e il recupero piu' lungo
  summary.json                  tutti i numeri citati nell'articolo
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[1]
SERIE = ROOT / "public" / "tools" / "prestito-investimento-serie.json"
CPI = ROOT / "data" / "Valute" / "FPCPITOTLZGITA.csv"
OUT = ROOT / "public" / "charts" / "prima-di-investire-fondo-emergenza"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

ORIZZONTI = [1, 2, 3, 5, 7, 10, 15, 20]


# ----------------------------------------------------------------- dati
def world_mensile() -> tuple[list[float], str, str]:
    d = json.loads(SERIE.read_text(encoding="utf-8"))
    s = d["serie"]["world"]
    return s["r"], s["inizio"], s["fine"]


def inflazione_annua() -> dict[int, float]:
    out: dict[int, float] = {}
    with CPI.open(encoding="utf-8-sig") as fh:
        next(fh)
        for riga in fh:
            p = riga.strip().split(",")
            if len(p) >= 2 and p[1] not in ("", "."):
                out[int(p[0][:4])] = float(p[1])
    return out


def world_annuo(r: list[float], inizio: str) -> dict[int, float]:
    """Solo anni civili completi: dodici mesi, altrimenti non e' un anno."""
    a, m = (int(x) for x in inizio.split("-"))
    mesi: dict[int, list[float]] = {}
    for x in r:
        mesi.setdefault(a, []).append(x)
        m += 1
        if m > 12:
            m, a = 1, a + 1
    out = {}
    for anno, v in mesi.items():
        if len(v) == 12:
            p = 1.0
            for x in v:
                p *= 1 + x
            out[anno] = p - 1
    return out


# ----------------------------------------------------------------- conti
def perdita_nominale(r: list[float]) -> dict[int, dict]:
    """Per ogni orizzonte: quante finestre mobili mensili chiudono sotto il
    capitale iniziale, e la mediana del moltiplicatore."""
    res = {}
    for anni in ORIZZONTI:
        h = anni * 12
        if h >= len(r):
            continue
        molt = []
        for i in range(len(r) - h + 1):
            p = 1.0
            for x in r[i:i + h]:
                p *= 1 + x
            molt.append(p)
        molt_ord = sorted(molt)
        res[anni] = {
            "finestre": len(molt),
            "in_perdita": sum(1 for m in molt if m < 1),
            "quota_perdita": round(sum(1 for m in molt if m < 1) / len(molt) * 100, 1),
            "mediana_moltiplicatore": round(molt_ord[len(molt_ord) // 2], 3),
            "peggiore_moltiplicatore": round(molt_ord[0], 3),
        }
    return res


def perdita_reale(wa: dict[int, float], infl: dict[int, float]) -> dict[int, dict]:
    """Stessa cosa sui dati annuali, deflazionando per l'inflazione italiana."""
    anni_ok = sorted(a for a in wa if a in infl)
    reali = {a: (1 + wa[a]) / (1 + infl[a] / 100) - 1 for a in anni_ok}
    seq = [reali[a] for a in anni_ok]
    res = {}
    for anni in ORIZZONTI:
        if anni >= len(seq):
            continue
        molt = []
        for i in range(len(seq) - anni + 1):
            p = 1.0
            for x in seq[i:i + anni]:
                p *= 1 + x
            molt.append(p)
        molt_ord = sorted(molt)
        res[anni] = {
            "finestre": len(molt),
            "quota_perdita": round(sum(1 for m in molt if m < 1) / len(molt) * 100, 1),
            "mediana_moltiplicatore": round(molt_ord[len(molt_ord) // 2], 3),
            "peggiore_moltiplicatore": round(molt_ord[0], 3),
        }
    return res, anni_ok[0], anni_ok[-1]


def sotto_acqua(r: list[float], inizio: str):
    """Curva del drawdown mensile e durata degli episodi sott'acqua."""
    a, m = (int(x) for x in inizio.split("-"))
    date, nav, dd = [], [], []
    v, picco = 1.0, 1.0
    for x in r:
        v *= 1 + x
        picco = max(picco, v)
        date.append(a + (m - 1) / 12)
        nav.append(v)
        dd.append(v / picco - 1)
        m += 1
        if m > 12:
            m, a = 1, a + 1
    episodi, start = [], None
    for i, d in enumerate(dd):
        if d < -1e-9 and start is None:
            start = i
        elif d >= -1e-9 and start is not None:
            episodi.append((start, i, min(dd[start:i])))
            start = None
    if start is not None:
        episodi.append((start, len(dd) - 1, min(dd[start:])))
    return date, dd, episodi


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_perdita(nom: dict, reale: dict, out: Path):
    anni = [a for a in ORIZZONTI if a in nom and a in reale]
    x = range(len(anni))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9.5, 5))
    b1 = ax.bar([i - w / 2 for i in x], [nom[a]["quota_perdita"] for a in anni],
                width=w, color=NAVY, label="In perdita in euro (nominale)")
    b2 = ax.bar([i + w / 2 for i in x], [reale[a]["quota_perdita"] for a in anni],
                width=w, color=ROSSO, label="In perdita di potere d'acquisto (reale)")
    # Lo zero va etichettato: una barra che non si vede sembra un dato mancante,
    # e invece e' il risultato piu' interessante del grafico.
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.annotate(f"{h:.0f}%", xy=(b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9.5,
                    color=GRIGIO if h > 0.05 else NAVY,
                    fontweight="normal" if h > 0.05 else "bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{a} anno" if a == 1 else f"{a} anni" for a in anni])
    ax.set_title("Quanto spesso l'azionario mondiale ha chiuso in perdita,\nin funzione di quanti anni lo si è tenuto")
    ax.set_ylabel("Quota delle finestre mobili")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_sotto_acqua(date, dd, episodi, out: Path):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.fill_between(date, [d * 100 for d in dd], 0, color=ROSSO, alpha=0.35, lw=0)
    ax.plot(date, [d * 100 for d in dd], color=ROSSO, lw=1.0)
    piu_lungo = max(episodi, key=lambda e: e[1] - e[0])
    i0, i1, minimo = piu_lungo
    mesi = i1 - i0
    ax.axvspan(date[i0], date[i1], color=NAVY, alpha=0.10)
    ax.annotate(f"il recupero più lungo: {mesi} mesi\n({mesi // 12} anni e {mesi % 12} mesi)",
                xy=(date[(i0 + i1) // 2], minimo * 100), xytext=(0, 26),
                textcoords="offset points", ha="center", fontweight="bold",
                color=NAVY, fontsize=10.5, linespacing=1.3)
    ax.set_title("Quanto tempo è servito per tornare al massimo precedente")
    ax.set_ylabel("Distanza dal massimo precedente")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    r, inizio, fine = world_mensile()
    infl = inflazione_annua()
    wa = world_annuo(r, inizio)
    nom = perdita_nominale(r)
    reale, anno0, anno1 = perdita_reale(wa, infl)
    date, dd, episodi = sotto_acqua(r, inizio)

    plot_perdita(nom, reale, OUT / "01_perdita_per_orizzonte.png")
    plot_sotto_acqua(date, dd, episodi, OUT / "02_sotto_acqua.png")

    piu_lungo = max(episodi, key=lambda e: e[1] - e[0])
    mesi_lungo = piu_lungo[1] - piu_lungo[0]
    lunghi = sorted((e[1] - e[0] for e in episodi), reverse=True)
    sommario = {
        "serie": {"fonte": "MSCI World total return in EUR, prestito-investimento-serie.json",
                  "inizio": inizio, "fine": fine, "mesi": len(r)},
        "inflazione": {"fonte": "FRED FPCPITOTLZGITA", "anni_reale": [anno0, anno1]},
        "nominale": nom,
        "reale": reale,
        "sotto_acqua": {
            "episodi": len(episodi),
            "recupero_piu_lungo_mesi": mesi_lungo,
            "recupero_piu_lungo_anni": round(mesi_lungo / 12, 1),
            "drawdown_peggiore_pct": round(min(dd) * 100, 1),
            "episodi_oltre_3_anni": sum(1 for x in lunghi if x > 36),
            "episodi_oltre_5_anni": sum(1 for x in lunghi if x > 60),
            "mesi_sotto_acqua_su_totale_pct": round(sum(1 for d in dd if d < -1e-9) / len(dd) * 100, 1),
        },
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(f"[ok] 2 grafici + summary.json in {OUT}\n")
    print(f"serie: {inizio} -> {fine} ({len(r)} mesi); reale su anni {anno0}-{anno1}")
    print(f"{'orizzonte':>10} | {'finestre':>8} | {'perdita nom':>11} | {'perdita reale':>13} | {'mediana nom':>11}")
    for a in ORIZZONTI:
        if a in nom and a in reale:
            print(f"{a:>7} anni | {nom[a]['finestre']:>8} | {nom[a]['quota_perdita']:>10}% |"
                  f" {reale[a]['quota_perdita']:>12}% | {nom[a]['mediana_moltiplicatore']:>11}")
    sa = sommario["sotto_acqua"]
    print(f"\nsott'acqua: {sa['mesi_sotto_acqua_su_totale_pct']}% dei mesi; peggior calo {sa['drawdown_peggiore_pct']}%; "
          f"recupero piu' lungo {sa['recupero_piu_lungo_mesi']} mesi ({sa['recupero_piu_lungo_anni']} anni); "
          f"episodi oltre 3 anni: {sa['episodi_oltre_3_anni']}, oltre 5: {sa['episodi_oltre_5_anni']}")


if __name__ == "__main__":
    main()
