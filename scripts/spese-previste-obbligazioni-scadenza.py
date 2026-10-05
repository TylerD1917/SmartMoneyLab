# -*- coding: utf-8 -*-
"""
SmartMoneyLab — Le basi, episodio 3: le spese importanti che sai gia' di dover fare
===================================================================================

Il terzo livello della scala della liquidita': non il fondo di emergenza (imprevisto)
e non il capitale a mercato (lungo termine), ma il denaro destinato a una spesa
RILEVANTE, PREVISTA e DATATA. La tesi: si copre con un titolo obbligazionario la cui
scadenza coincide con la data della spesa, e la sua necessita' decresce man mano che
il capitale investito cresce.

DUE CONTI, DUE GRAFICI
----------------------
1. Il meccanismo del "pull to par". Un'obbligazione singola tenuta a scadenza
   restituisce il nominale alla data, qualunque cosa facciano i tassi nel frattempo:
   il prezzo scende se i tassi salgono, ma risale verso 100 avvicinandosi alla
   scadenza. Qui e' simulato in modo esatto, non stimato: prezzo = valore attuale
   delle cedole residue piu' il nominale.
   ATTENZIONE: non significa che un fondo obbligazionario "non recuperi mai". Un
   fondo a duration costante recupera, su un orizzonte vicino alla sua duration,
   grazie al reinvestimento a tassi piu' alti. La differenza non e' il recupero,
   e' la CERTEZZA DELL'IMPORTO A UNA DATA: il titolo singolo ce l'ha, il fondo no.

2. Quanto costa vendere a mercato depresso, in funzione di quanto e' grande il
   portafoglio. Se servono X euro e il mercato e' a -35%, si liquidano quote che
   al picco valevano X/0,65: la differenza e' capitale ceduto per sempre. Espressa
   in quota del portafoglio, quella perdita si riduce al crescere del capitale,
   ed e' la ragione quantitativa per cui il terzo livello serve meno a chi ha gia'
   un patrimonio grande.

DATI
----
- Modello duration sul Treasury decennale, serie mensile da
  `public/tools/prestito-investimento-serie.json` (`bond_usd` = pura reazione ai
  tassi in dollari, `bond` = la stessa convertita in euro e non coperta).

OUTPUT in public/charts/spese-previste-obbligazioni-scadenza/
-------------------------------------------------------------
  01_pull_to_par.png      il prezzo che torna a 100 alla scadenza, e il 2022 reale
  02_costo_vendere.png    capitale bruciato vendendo a -35%, per dimensione
  summary.json
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
OUT = ROOT / "public" / "charts" / "spese-previste-obbligazioni-scadenza"

NAVY = "#1e3a8a"
GOLD = "#d97706"
ROSSO = "#dc2626"
GRIGIO = "#64748b"

# il titolo di esempio
ANNI, CEDOLA, NOMINALE = 5, 0.03, 100.0
TASSO_NUOVO = 0.06
CALO = 0.35          # quanto e' sceso il mercato azionario quando serve il denaro
SPESA = 20000.0


# ----------------------------------------------------------------- conti
def prezzo(n_anni_residui: int, y: float) -> float:
    """Valore attuale di un titolo con cedola annua, n anni alla scadenza."""
    if n_anni_residui == 0:
        return NOMINALE
    v = sum(CEDOLA * NOMINALE / (1 + y) ** k for k in range(1, n_anni_residui + 1))
    return v + NOMINALE / (1 + y) ** n_anni_residui


def pull_to_par():
    """Prezzo anno per anno dopo un rialzo immediato dei tassi dal 3% al 6%."""
    anni = list(range(ANNI + 1))
    invariato = [prezzo(ANNI - t, CEDOLA) for t in anni]
    salito = [prezzo(ANNI - t, TASSO_NUOVO) for t in anni]
    return anni, invariato, salito


def bond_reale():
    """La serie storica del modello duration: il 2022 e il tempo di recupero."""
    d = json.loads(SERIE.read_text(encoding="utf-8"))
    out = {}
    for chiave in ("bond_usd", "bond"):
        s = d["serie"][chiave]
        a, m = (int(x) for x in s["inizio"].split("-"))
        date, nav, dd = [], [], []
        v, picco = 1.0, 1.0
        anni: dict[int, list[float]] = {}
        for r in s["r"]:
            anni.setdefault(a, []).append(r)
            v *= 1 + r
            picco = max(picco, v)
            date.append(a + (m - 1) / 12)
            nav.append(v)
            dd.append(v / picco - 1)
            m += 1
            if m > 12:
                m, a = 1, a + 1
        def comp(xs):
            p = 1.0
            for x in xs:
                p *= 1 + x
            return p - 1
        out[chiave] = {
            "date": date, "dd": dd,
            "2022": comp(anni[2022]) if len(anni.get(2022, [])) == 12 else None,
            "dd_min": min(dd),
        }
    return out


def costo_vendere(dimensioni: list[float]) -> list[dict]:
    """Capitale ceduto per sempre vendendo SPESA euro con il mercato a -CALO."""
    righe = []
    for picco in dimensioni:
        liquidato_al_picco = SPESA / (1 - CALO)
        bruciato = liquidato_al_picco - SPESA
        righe.append({
            "portafoglio_al_picco": picco,
            "spesa_su_portafoglio": SPESA / picco,
            "capitale_bruciato": bruciato,
            "bruciato_su_portafoglio": bruciato / picco,
            "sostenibile": SPESA / (1 - CALO) <= picco * (1 - CALO),
        })
    return righe


# ----------------------------------------------------------------- grafici
def _stile():
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 12.5, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--",
    })


def plot_pull_to_par(anni, invariato, salito, reale, out: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    ax1.plot(anni, invariato, color=GRIGIO, lw=1.6, ls="--", label="se i tassi non si muovono")
    ax1.plot(anni, salito, color=NAVY, lw=2.6, marker="o", ms=5,
             label="dopo un rialzo dei tassi dal 3% al 6%")
    ax1.axhline(NOMINALE, color=GRIGIO, lw=0.9, alpha=0.6)
    ax1.annotate(f"{salito[0]:.0f}", xy=(0, salito[0]), xytext=(6, -14),
                 textcoords="offset points", color=NAVY, fontweight="bold")
    ax1.annotate("100 alla scadenza,\nqualunque cosa\nfacciano i tassi nel frattempo",
                 xy=(ANNI, NOMINALE), xytext=(-30, -112), textcoords="offset points",
                 ha="right", color=NAVY, fontweight="bold", fontsize=10, linespacing=1.35,
                 arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2,
                                 connectionstyle="arc3,rad=-0.2"))
    ax1.set_title("Un titolo singolo tenuto fino alla scadenza")
    ax1.set_xlabel("anni alla scadenza")
    ax1.set_ylabel("prezzo di mercato")
    ax1.set_xticks(anni)
    ax1.set_xticklabels([str(ANNI - t) for t in anni])
    ax1.set_ylim(80, 104)
    ax1.legend(frameon=False, fontsize=9.5, loc="lower left")

    b = reale["bond_usd"]
    da = [(x, y) for x, y in zip(b["date"], b["dd"]) if 2019 <= x <= 2026.8]
    ax2.fill_between([x for x, _ in da], [y * 100 for _, y in da], 0,
                     color=ROSSO, alpha=0.3, lw=0)
    ax2.plot([x for x, _ in da], [y * 100 for _, y in da], color=ROSSO, lw=1.6)
    peggio = min(y for _, y in da)
    ax2.annotate(f"{peggio*100:.0f}%", xy=(2022.8, peggio * 100), xytext=(10, 10),
                 textcoords="offset points", color=ROSSO, fontweight="bold")
    ax2.set_title("Un indice obbligazionario, che scadenza non ne ha")
    ax2.set_ylabel("distanza dal massimo precedente")
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_costo(righe, out: Path):
    def etichetta(v: float) -> str:
        return "1 mln" if v >= 1_000_000 else f"{int(v/1000)}k"
    etich = [etichetta(r["portafoglio_al_picco"]) for r in righe]
    quota = [r["bruciato_su_portafoglio"] * 100 for r in righe]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    barre = ax.bar(etich, quota, color=[ROSSO if q > 5 else (GOLD if q > 2 else NAVY) for q in quota])
    for b, r in zip(barre, righe):
        ax.annotate(f"{b.get_height():.1f}%".replace(".", ","),
                    xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=10, color=GRIGIO)
    spesa_it = f"{SPESA:,.0f}".replace(",", ".")   # solo il numero, non tutta la frase
    ax.set_title(f"Vendere {spesa_it} € di azionario con il mercato a −{CALO*100:.0f}%:\n"
                 "quanto capitale cedi per sempre, secondo quanto è grande il portafoglio")
    ax.set_xlabel("valore del portafoglio prima del calo")
    ax.set_ylabel("capitale ceduto, in quota del portafoglio")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _stile()
    anni, invariato, salito = pull_to_par()
    reale = bond_reale()
    dimensioni = [25000, 50000, 100000, 250000, 500000, 1000000]
    righe = costo_vendere(dimensioni)

    plot_pull_to_par(anni, invariato, salito, reale, OUT / "01_pull_to_par.png")
    plot_costo(righe, OUT / "02_costo_vendere.png")

    sommario = {
        "titolo_esempio": {
            "anni": ANNI, "cedola": CEDOLA, "tasso_iniziale": CEDOLA,
            "tasso_dopo_rialzo": TASSO_NUOVO,
            "prezzo_subito_dopo_il_rialzo": round(salito[0], 2),
            "perdita_immediata_pct": round((salito[0] / NOMINALE - 1) * 100, 1),
            "prezzo_a_scadenza": NOMINALE,
            "prezzi_anno_per_anno": [round(x, 2) for x in salito],
        },
        "indice_obbligazionario": {
            "fonte": "modello duration sul Treasury decennale",
            "2022_in_dollari_pct": round(reale["bond_usd"]["2022"] * 100, 1),
            "2022_in_euro_pct": round(reale["bond"]["2022"] * 100, 1),
            "drawdown_massimo_dollari_pct": round(reale["bond_usd"]["dd_min"] * 100, 1),
            "nota": "in euro il 2022 e' meno negativo perche' il dollaro si e' rafforzato",
        },
        "costo_di_vendere": {
            "spesa": SPESA, "calo_mercato": CALO,
            "liquidato_a_valori_di_picco": round(SPESA / (1 - CALO), 0),
            "capitale_bruciato": round(SPESA / (1 - CALO) - SPESA, 0),
            "per_dimensione": [
                {"portafoglio": r["portafoglio_al_picco"],
                 "spesa_su_portafoglio_pct": round(r["spesa_su_portafoglio"] * 100, 1),
                 "bruciato_su_portafoglio_pct": round(r["bruciato_su_portafoglio"] * 100, 2)}
                for r in righe],
        },
    }
    (OUT / "summary.json").write_text(json.dumps(sommario, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(f"[ok] 2 grafici + summary.json in {OUT}\n")
    t = sommario["titolo_esempio"]
    print(f"titolo {ANNI} anni cedola 3%, tassi al 6%: prezzo subito {t['prezzo_subito_dopo_il_rialzo']} "
          f"({t['perdita_immediata_pct']}%), poi {' -> '.join(str(x) for x in t['prezzi_anno_per_anno'][1:])}")
    i = sommario["indice_obbligazionario"]
    print(f"indice obbligazionario 2022: {i['2022_in_dollari_pct']}% in dollari, "
          f"{i['2022_in_euro_pct']}% in euro; drawdown massimo {i['drawdown_massimo_dollari_pct']}%")
    c = sommario["costo_di_vendere"]
    print(f"vendere {SPESA:.0f} a -{CALO*100:.0f}%: si liquidano {c['liquidato_a_valori_di_picco']:.0f} "
          f"di valore al picco, {c['capitale_bruciato']:.0f} ceduti per sempre")
    for r in sommario["costo_di_vendere"]["per_dimensione"]:
        print(f"   portafoglio {r['portafoglio']:>9,.0f}: spesa {r['spesa_su_portafoglio_pct']:>5}% "
              f"del portafoglio, bruciato {r['bruciato_su_portafoglio_pct']:>5}%")


if __name__ == "__main__":
    main()
