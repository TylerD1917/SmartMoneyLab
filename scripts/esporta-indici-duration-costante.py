"""
Esporta in CSV gli indici obbligazionari a duration costante
============================================================

Il motore vive in `quanto-rendono-etf-obbligazionari.py` e finora ricostruiva
le serie in memoria a ogni esecuzione, senza salvarle. Qui le congeliamo su
disco in `data/processed/indici_duration_costante/`, cosi' sono riusabili da
altri studi senza rilanciare l'articolo.

USO:
  python scripts/esporta-indici-duration-costante.py

Output:
  nav_duration_costante.csv  NAV total return, base 100 alla prima data utile
                             di ogni serie (una colonna per gamba)
  ytm_sottostanti.csv        i rendimenti a scadenza mensili che generano le
                             gambe principali, in percentuale
  README.md                  come sono costruite le serie e cosa NON sono

Nota: ogni colonna del NAV parte da 100 alla PROPRIA prima data, quindi i
livelli non sono confrontabili fra colonne con storie diverse. Per un
confronto, ribasare entrambe sulla prima data comune.
"""
from __future__ import annotations

import importlib.util
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "data", "Bonds", "indici_duration_costante")

spec = importlib.util.spec_from_file_location(
    "motore_bond", os.path.join(HERE, "quanto-rendono-etf-obbligazionari.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def _tab(d: dict[str, pd.Series]) -> pd.DataFrame:
    df = pd.DataFrame(d)
    df.index = df.index.to_timestamp().strftime("%Y-%m")
    df.index.name = "mese"
    return df


def main():
    os.makedirs(OUT, exist_ok=True)
    gambe, extra, rendimenti = M.costruisci()

    nav = _tab({**gambe, **extra}).round(4)
    nav.to_csv(os.path.join(OUT, "nav_duration_costante.csv"))

    ytm = _tab(rendimenti).round(4)
    ytm.to_csv(os.path.join(OUT, "ytm_sottostanti.csv"))

    righe = []
    for n, s in {**gambe, **extra}.items():
        righe.append(f"| {n} | {s.index[0]} | {s.index[-1]} | {len(s)} | "
                     f"{M.cagr(s) * 100:.2f}% | {s.iloc[-1] / 100:.1f}x |")

    readme = f"""# Indici obbligazionari a duration costante

Serie generate da `scripts/esporta-indici-duration-costante.py`, che richiama
il motore di `scripts/quanto-rendono-etf-obbligazionari.py`. Rigenerale con:

    python scripts/esporta-indici-duration-costante.py

## Cosa sono

Simulano un ETF obbligazionario che tiene la duration ferma: ogni mese vende
il titolo invecchiato di un mese e ricompra alla pari sulla scadenza
obiettivo. Il prezzo e' il valore attuale sporco dei flussi residui (rateo
incluso), cedola semestrale, nessun costo e nessuna imposta. Il NAV e' total
return: le cedole sono dentro il prezzo, non staccate.

La gamba "USA 7-10" e' l'unica che modella anche il roll-down lungo la curva
(acquisto a 8,5 anni, valutazione a 8,5 anni meno un mese); le altre
rivalutano alla stessa scadenza di acquisto.

## Cosa NON sono

Non sono ETF reali: niente TER, niente spread denaro-lettera, niente
tracking difference, niente fiscalita'. Non sono indici ufficiali e non
vanno citati come tali. Servono a isolare l'effetto del livello dei tassi
sul rendimento di una strategia a duration costante.

## Scadenza obiettivo di ogni gamba

| gamba | scadenza modellata | fonte del rendimento |
|---|---|---|
| USA 7-10 | 8,5 anni | DGS7 e DGS10 interpolati (FRED) |
| USA 20+ | 24 anni | DGS20, buco 1987-1993 tappato con le variazioni di DGS30 (FRED) |
| Area euro 7-10 | 8,5 anni | rendimento a lungo termine area euro (OCSE) |
| Italia 15+ | 20 anni | BTP 10 anni, IMF fino al 1991 poi OCSE |
| Italia 7-10 | 8,5 anni | stessa fonte Italia |
| Italia 15+ (dal 1993) | 20 anni | stessa fonte, troncata a novembre 1993 |

Attenzione all'Italia: prima di novembre 1993 i BTP lunghi di fatto non
esistevano, quindi la parte precedente e' un'estrapolazione del decennale.
Nell'articolo e' disegnata punteggiata per questo motivo.

## File

- `nav_duration_costante.csv` - NAV total return mensile, base 100 alla
  prima data **di ciascuna colonna**. Storie diverse, quindi per confrontare
  due gambe vanno ribasate sulla prima data comune.
- `ytm_sottostanti.csv` - i rendimenti a scadenza mensili in percentuale che
  generano le quattro gambe principali.

## Copertura

| gamba | da | a | mesi | CAGR | crescita |
|---|---|---|---|---|---|
{chr(10).join(righe)}
"""
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"scritti in {OUT}")
    print(nav.tail(3))


if __name__ == "__main__":
    main()
