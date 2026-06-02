# Thread X — Prestito per investire vs PAC

**Account**: @smartmoneylabIT
**Lunghezza**: 9 post (1 hook + 7 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i PNG in `public/charts/prestito-vs-pac/`

---

## 1/9 — Hook

> Hai $250/mese di cash flow disponibile.
>
> Hai due strade:
> A — versarli ogni mese in un PAC sull'indice
> B — trasformarli nella rata di un prestito personale, ricevere ~$20k subito e investirli tutti in lump sum
>
> Quale produce più capitale a fine corsa? Su 50 anni di dati la risposta è netta.
>
> Thread 👇

*Allegare grafico: 03_winrate_bar.png*

---

## 2/9 — Il setup

> Simulazione su 50 anni (1976–2025), NASDAQ e S&P 500 separatamente.
>
> Rata $250/mese, durata prestito 10 anni → capitale derivato:
> ⬛ TAEG 6% (ottimistico) → $22.518
> ⬛ TAEG 8% (realistico per IT 2026) → $20.605
>
> Rolling windows 10y e 20y (in 20y, 2 prestiti consecutivi). Step 3 mesi.
> 161 finestre 10y + 121 finestre 20y per scenario.

---

## 3/9 — Il risultato che pesa

> Win rate del LUMP SUM finanziato vs PAC tradizionale:
>
> S&P 500 → 72.0% a 10y / 81.0% a 20y (TAEG 6%)
> S&P 500 → 72.0% a 10y / 72.7% a 20y (TAEG 8%)
> NASDAQ → 73.9% a 10y / 81.8% a 20y (TAEG 6%)
> NASDAQ → 67.1% a 10y / 65.3% a 20y (TAEG 8%)
>
> In TUTTI gli 8 scenari il lump finanziato batte il PAC nella maggior parte delle finestre storiche.

---

## 4/9 — Il payoff

> Rapporto valore finale lump / valore finale PAC, percentili:
>
> Caso favorevole (p95): tra +33% e +60%
> Mediana (p50): tra +10% e +30%
> Caso sfavorevole (p5): tra −10% e −36%
>
> Mediana sempre positiva. Upside sostanzioso. Ma quando il lump perde, perde forte.

*Allegare grafico: 04_excess_distribution.png*

---

## 5/9 — Il punto di rottura

> Win rate del lump al variare del TAEG:
>
> TAEG 0% → 94-100% (sull'SP500 20y: 121 finestre su 121)
> TAEG 4% → ~83-93%
> TAEG 8% → ~65-72%
> TAEG 12% → ~31-51% (break-even)
> TAEG 14% → ~10-33%
>
> Il break-even sta tra TAEG 11% e 12%. Sopra, il PAC torna a vincere.

*Allegare grafico: 06_taeg_breakeven.png*

---

## 6/9 — Perché funziona

> Tre meccanismi che si rinforzano:
>
> 1) Il mercato sale in media → stare nel mercato dal giorno uno cattura più compounding del distribuire l'esposizione nel tempo.
>
> 2) Il TAEG è una tassa fissa sul vantaggio del lump. Finché TAEG < rendimento medio del mercato (~10%), il lump è in zona favorevole.
>
> 3) È esattamente il classico "lump vs DCA" della letteratura — con il TAEG come zavorra.

---

## 7/9 — Il prezzo (vero) del lump sum

> Il MDD percentuale del portafoglio è SISTEMATICAMENTE peggiore col lump.
>
> ⬛ SP500 20y: lump −55% mediano vs PAC −46%
> ⬛ NASDAQ 20y: lump −76% mediano vs PAC −65%
>
> Hai $20k esposti al mercato dal giorno uno: il primo crash fa molto più male di un PAC dove il portafoglio è ancora piccolo.

*Allegare grafico: 01_equity_example.png*

---

## 8/9 — Il rischio che NON è nel backtest

> Il prestito introduce un'obbligazione legale: $250/mese per 10 o 20 anni, niente sospensioni.
>
> Il PAC è interrompibile senza conseguenze.
>
> Se perdi il lavoro a metà strada:
> ⬛ Col PAC: salti i versamenti
> ⬛ Col prestito: vai in default
>
> Su orizzonti decennali questo rischio non è zero. Va pesato.

---

## 9/9 — CTA

> Riassunto secco, perché un articolo del genere se lo merita:
>
> ⬛ I numeri storici dicono: a TAEG realistici (6-8%) il lump finanziato batte il PAC nella stragrande maggioranza delle finestre. È un effetto robusto.
>
> ⬛ Il prezzo è un drawdown peggiore + il rischio operativo del prestito.
>
> ⬛ Decisione personale: dipende dal tuo TAEG, dalla tua tolleranza al MDD, dal tuo cash flow di sicurezza.
>
> Sul blog l'analisi completa + un simulatore live in cui muovi TAEG e capitale e vedi cosa cambia.
>
> [link al post]
>
> #ETF #PAC #Prestito #Investimenti #DCA #LumpSum

---

## Note operative

- **Quote tweet utili a 24-48h**:
  - "S&P 500 su finestre 20Y con TAEG 0-2%: il lump sum finanziato vince in 121 finestre rolling su 121. Il 100%. La regola del 'tempo nel mercato' portata all'estremo: con costo del finanziamento nullo, non c'è uno scenario storico in cui distribuire l'esposizione su 20 anni batta concentrare tutto subito."
  - "Break-even del TAEG: ~11-12%. Per il mercato italiano del prestito personale 2026 (TAEG retail tra 6% e 12%), questo significa che la maggior parte dei clienti è in zona favorevole al lump finanziato — sui dati storici."

- **Pushback prevedibili**:
  - "Eh ma il MDD!" → vero, peggiora di 5-11 pp. È esattamente il prezzo da pagare. L'articolo lo discute esplicitamente come "il prezzo del lump sum".
  - "Eh ma il prestito introduce rischio di default!" → vero, è il punto chiave non-quantificabile dal backtest. È il pezzo 8/9 del thread. È la vera ragione per non farlo, se non hai cash flow di sicurezza.
  - "Hai considerato le tasse al 26%?" → al lordo, ma la differenza percentuale resta uguale. In $$$ assoluti i numeri vanno scalati.
  - "Un prestito personale per investire è da pazzi" → la letteratura classica (lump vs DCA, Vanguard 2012, "Dollar-Cost Averaging Just Means Taking Risk Later") dice esattamente che il lump batte il DCA in ~67% dei casi. Qui aggiungiamo il TAEG come zavorra. L'analisi è una replica rigorosa, non una scommessa.

- **Conversion goal**: portare al simulatore. Il vero motore di engagement è "puoi cambiare il TUO TAEG e vedere se la cosa funziona per te". Statistica generale → curiosità personale.
