# Protocollo snapshot CAPE — Research Affiliates AAI

Obiettivo: ricostruire una serie **semestrale** di CAPE per paese, dal 1998 a oggi,
da usare come gamba valutazione dello studio cross-country CAPE → rendimenti forward.

## Fonte
https://interactive.researchaffiliates.com/asset-allocation → grafico **Valuations** → **CAPE**.
(NON /aai-hub, che è un bucket S3 e dà AccessDenied.)

## Cosa catturare
Muovi il cursore sul grafico e cattura la **tabella/tooltip con TUTTI i mercati**,
il loro CAPE, e la **data** visibile. Un solo screenshot per data.
- Tutta la tabella dentro il frame, nessuna riga tagliata.
- Cifre nitide: se serve, zooma finché i decimali sono leggibili.

## Cadenza
2 punti l'anno per ogni anno dal **1998** a oggi:
- **fine dicembre** e **fine luglio** (o i due punti mensili RA più vicini).

## Impostazioni da tenere IDENTICHE su tutti gli snapshot
- Stesso grafico (Valuations/CAPE), stessa lista mercati, stessa modalità.
- Non cambiare valuta a metà lavoro. (Il CAPE è un rapporto, non dipende dalla
  valuta — ma teniamo tutto identico per sicurezza.)

## Nome file — IMPORTANTE
`AAAA-MM.png` → es: `1998-12.png`, `1999-07.png`, `1999-12.png`, … `2026-07.png`.
La data nel nome file è la mia fonte primaria per la data del punto
(così non dipendo dall'OCR per leggere la data dal grafico).

## Dopo
Quando la cartella è piena: esamino tutti gli screenshot, estraggo (data, mercato, CAPE),
costruisco `data/processed/cape_panel.csv`, e valido incrociando con il file RA e
controllando gli outlier. Poi partiamo con lo script dello studio.
