# Carosello Instagram — Prestito per investire vs PAC

**Account**: @smartmoneylab_it
**Slide**: 9 (Cover + 7 contenuto + CTA)
**Formato**: 1080×1350 px (4:5)
**Palette**: navy (#1e3a8a) + ambra (#d97706); il navy resta brand "rigore", l'ambra è "lump sum finanziato"

---

## Slide 1 — COVER

**Background**: navy scuro pieno (#1e3a8a)
**Testo principale (centrato, bianco, 60pt bold)**:

> Conviene prendere
> un prestito
> per investire?

**Sottotitolo (28pt, slate-200)**:

> $250/mese: PAC tradizionale o trasformarli nella rata di un prestito e investire $20k subito?
>
> 50 anni di dati su NASDAQ e SP500.
> Risposta più netta del previsto.

**Footer (18pt, slate-300)**: smartmoneylab.pages.dev

---

## Slide 2 — LA DOMANDA, IN 4 RIGHE

**Background**: bianco sporco (#f8fafc)
**Titolo (36pt, navy)**: La domanda

**Corpo (22pt, slate-700)**:

> Cash flow disponibile: $250/mese.
>
> Opzione A — **PAC**: ogni mese $250 sull'indice.
>
> Opzione B — **Lump sum finanziato**: la banca eroga ~$20.000 oggi, tu paghi $250/mese di rata per 10 anni.
>
> Stesso cash flow personale, distribuzione temporale opposta.

---

## Slide 3 — IL SETUP

**Background**: navy chiaro (#dbeafe)
**Titolo (36pt, navy)**: La simulazione, in dettaglio

**Corpo (22pt)**:

> ⬛ Periodo: 1976–2025 (50 anni)
> ⬛ Indici: NASDAQ + S&P 500 separatamente
> ⬛ Durata: 10 anni / 20 anni (doppio prestito)
> ⬛ TAEG testati: 6% ottimistico, 8% realistico
> ⬛ Rolling windows step 3 mesi
> ⬛ ~140 finestre indipendenti per scenario

> Capitali derivati: $22.518 (6%) / $20.605 (8%)

---

## Slide 4 — IL RISULTATO

**Background**: navy scuro (#1e3a8a), testo bianco
**Titolo (40pt bianco bold)**: Win rate del lump sum vs PAC

**Tabella centrale (24pt bianco)**:

> **S&P 500**
> 6% / 10y → 75.2%
> 6% / 20y → **81.0%**
> 8% / 10y → 72.0%
> 8% / 20y → 72.7%
>
> **NASDAQ**
> 6% / 10y → 73.9%
> 6% / 20y → **81.8%**
> 8% / 10y → 67.1%
> 8% / 20y → 65.3%

**Riquadro highlight (sfondo blu chiaro, bianco bold)**:
> In tutti gli 8 scenari il lump finanziato batte il PAC nella maggior parte delle finestre storiche.

---

## Slide 5 — IL DATO ESTREMO

**Background**: ambra chiaro (#fef3c7)
**Titolo (40pt, ambra scuro #92400e bold)**: SP500 20 anni, TAEG 0%

**Mega numero centrale (110pt ambra scuro bold)**:
> 121/121

**Sotto (24pt, slate-800)**:
> finestre rolling vinte dal lump sum.
>
> Il 100%.

**Riquadro highlight (sfondo navy chiaro)**:
> In 50 anni di storia non esiste UNA finestra 20Y in cui un PAC su S&P 500 abbia chiuso sopra un lump sum a costo del prestito ≈ 0%.
>
> La regola del "tempo nel mercato" portata all'estremo.

---

## Slide 6 — IL PUNTO DI ROTTURA

**Background**: bianco
**Titolo (36pt, navy)**: Quando il PAC torna a vincere

**Tabella (22pt)**:

> Win rate lump al variare del TAEG (media SP500 + NASDAQ, 10y):
>
> ⬛ TAEG 4% → ~82%
> ⬛ TAEG 6% → ~75%
> ⬛ TAEG 8% → ~70%
> ⬛ TAEG 10% → ~63%
> ⬛ TAEG 12% → **~50% (break-even)**
> ⬛ TAEG 14% → ~31%

**Riquadro highlight (sfondo ambra chiaro)**:
> Sotto TAEG ~11-12% → lump vince statisticamente.
> Sopra → il PAC torna ad essere la scelta migliore.
>
> Il mercato italiano del prestito personale 2026 si muove tra 6% e 12% TAEG. La maggior parte dei clienti è in zona favorevole al lump.

---

## Slide 7 — IL PREZZO NASCOSTO

**Background**: navy scuro (#1e3a8a), testo bianco
**Titolo (40pt bianco bold)**: Il drawdown

**Tabella (24pt bianco)**:

> MDD mediano del portafoglio, finestre 20 anni:
>
> SP500: lump **−55%** vs PAC −46%
> NASDAQ: lump **−76%** vs PAC −65%

**Riquadro highlight (sfondo blu chiaro, bianco bold)**:
> Hai $20.000 esposti al mercato dal giorno uno.
>
> Il primo crash fa molto più male di un PAC dove il portafoglio è ancora piccolo. Su orizzonti lunghi viene recuperato — ma chi non sopporta il MDD emotivamente capitola, e tutto il vantaggio statistico evapora con la prima vendita in fondo al drawdown.

---

## Slide 8 — IL RISCHIO CHE I DATI NON VEDONO

**Background**: bianco
**Titolo (36pt, navy)**: Il prestito ti vincola

**Corpo (24pt slate-700)**:

> Il PAC è interrompibile senza conseguenze.
>
> Il prestito introduce un'obbligazione legale a pagare $250/mese per 10 o 20 anni.

**Riquadro highlight (sfondo ambra chiaro, slate-800)**:
> Se perdi il lavoro a metà strada:
>
> ⬛ Col PAC → sospendi i versamenti
> ⬛ Col prestito → vai in default
>
> Su 10-20 anni la probabilità di un periodo difficile non è zero. È il vero peso da mettere sul piatto del PAC.

---

## Slide 9 — CTA

**Background**: navy scuro (#1e3a8a)
**Titolo (40pt bianco bold)**:

> Sul blog: simulatore live

**Corpo (24pt bianco)**:

> + Analisi completa con percentili p5/p50/p95
> + Tabelle CAGR e MDD per ogni scenario
> + Curva di break-even del TAEG
> + Simulatore interattivo dove muovi
>   TAEG e capitale e vedi cosa cambia
> + Codice Python riproducibile

**Mega CTA (36pt bianco bold underline)**:
> smartmoneylab.pages.dev
> @smartmoneylab_it

**Footer (18pt slate-300)**: SmartMoneyLab — Finanza personale e analisi quantitativa

---

## Note operative

- **Palette intenzionale**: il navy è il PAC (brand "rigore", scelta tradizionale), l'ambra è il lump finanziato (la scelta "leverage"). La slide 5 (l'ambra dominante) è il momento "ribaltone" del carosello: il dato del 100% sui 20 anni a costo zero.
- **Ritmo sfondi**: 1 dark / 2 light / 3 light / 4 dark / 5 ambra / 6 light / 7 dark / 8 light / 9 dark. Pivot visivo su slide 5.
- **Mega numeri**: 121/121 (slide 5 — il dato estremo), break-even ~50% (slide 6 — il punto di rottura). Sono i due momenti "wow" del carosello.
- **Tono**: questo NON è un test di strategia con verdetto, è un'esplorazione data-driven di una domanda concreta. Il carosello chiude su una decisione *personale* (slide 8-9), non su "questa strategia funziona". Mantenere quel registro nelle risposte ai commenti.
- Hashtag in primo commento.
