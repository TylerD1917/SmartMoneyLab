# Indici obbligazionari a duration costante

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
| USA 7-10 | 1969-07 | 2026-09 | 687 | 6.38% | 34.4x |
| USA 20+ | 1962-01 | 2026-10 | 778 | 5.69% | 36.0x |
| Area euro 7-10 | 1970-01 | 2026-01 | 673 | 7.06% | 45.7x |
| Italia 15+ | 1980-01 | 2026-08 | 560 | 9.46% | 67.4x |
| Italia 7-10 | 1980-01 | 2026-08 | 560 | 8.73% | 49.4x |
| Italia 15+ (dal 1993) | 1993-11 | 2026-08 | 394 | 6.15% | 7.1x |
