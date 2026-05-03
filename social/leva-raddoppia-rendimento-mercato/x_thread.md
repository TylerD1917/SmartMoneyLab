# Thread X — La leva 2x raddoppia? La 3x triplica?

**Account**: @smartmoneylabIT
**Lunghezza**: 9 post (1 hook + 7 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i 3 PNG realistici in `public/charts/leva-raddoppia-rendimento-mercato/`

---

## 1/9 — Hook

> "Compro un ETF S&P 500 a leva 3x e tengo 20 anni: triplicherò il rendimento del mercato."
>
> No.
>
> Ho fatto girare 50 anni di S&P 500 con leva matematica 1x, 2x e 3x daily. Calibrato i costi reali su un ETF vero (ProShares SSO).
>
> La 3x perde il 91% del suo valore "miracolo" solo per il drag dei costi. E nei peggiori 20 anni storici è inferiore alla 1x.
>
> Thread 👇

*Allegare grafico: 06_equity_curves_realistic.png*

---

## 2/9 — Il drag matematico

> Il volatility drag è il prezzo della leva, anche senza nessun costo. Esempio canonico:
>
> Mercato: −10% → +10%. Sottostante chiude a 99 (perde 1%).
> Leva 2x: −20% → +20%. Chiude a 96 (perde 4%).
>
> Quattro volte il drag del lineare, su due giorni. Su 252 giorni si accumula molto.

---

## 3/9 — La formula del drag

> Drag annualizzato ≈ ½ × L × (L−1) × σ²
>
> Con vol S&P storica 17.4%:
> • Leva 2x: drag teorico **3%/anno**
> • Leva 3x: drag teorico **9%/anno**
>
> Cioè il "3× lineare" perde 9 punti percentuali all'anno *prima ancora* di pagare TER e funding cost.

---

## 4/9 — Calibrazione su un ETF vero

> Per i costi reali ho usato ProShares SSO (2x, lancio 2006).
>
> Confronto SSO reale vs 2x sintetica matematica, 17.5 anni:
> • CAGR 2x sintetica: +16.31%
> • CAGR SSO reale: +13.17%
> • Drag totale empirico: **2.74%/anno**
>
> Decomposto: TER 0.89% + funding cost ~1.85%/anno.

---

## 5/9 — Il "miracolo" che si dissolve

> 1$ investito a inizio 1976, 50 anni di buy & hold:
>
> Lordo (matematica pura):
> • 1x → $228
> • 2x → $14.490
> • 3x → $167.810
>
> Realistico (con costi UCITS):
> • 1x → $222 (−3%)
> • 2x → $3.873 (−73%)
> • 3x → $14.943 (**−91%**)
>
> Il 91% del valore "miracolo" della 3x è drag dei costi.

---

## 6/9 — Il moltiplicatore implicito

> Sul CAGR realistico full-sample:
> • 1x: 11.78%
> • 2x: 18.32% → moltiplicatore 1.55× (vs nominale 2×)
> • 3x: 21.70% → moltiplicatore **1.84×** (vs nominale 3×)
>
> Triplicare la leva nominal NON triplica il rendimento. Lo amplifica del 1.84×.

---

## 7/9 — La convergenza a 20 anni che disinnesca la 3x

> Rolling 20Y, scenario realistico, 121 finestre:
> • 1x: CAGR p50 9.89%
> • 2x: CAGR p50 13.82%
> • 3x: CAGR p50 **13.87%**
>
> A 20 anni 2x e 3x sono PRATICAMENTE IDENTICHE in mediana. Tutto il drag aggiuntivo della 3x cancella il vantaggio teorico della leva extra.
>
> E nei p5 (peggior 5%): 1x = 6.24%, 3x = **2.44%**. La 3x perde anche contro la 1x.

*Allegare grafico: 08_boxplot_cagr_20y_realistic.png*

---

## 8/9 — Il drawdown è strutturale

> Nel 100% delle finestre 20Y la 3x ha visto un drawdown peggiore del −75%.
>
> Non l'80%, non il 99%. **Il 100%**.
>
> Su 121 finestre osservate, IN TUTTE la 3x è scesa almeno del 75% in qualche momento. Chiunque l'abbia tenuta 20 anni ha vissuto almeno un −75% lungo il viaggio.

---

## 9/9 — CTA

> Per chi può avere senso (forse): posizioni piccole, brevi, con conviction.
> Per chi compone come "azionario + di più" su 10-20 anni: NO. I dati dicono no.
>
> Sul blog l'analisi completa: due scenari (lordo + realistico calibrato), 3 orizzonti rolling, codice Python, ETF UCITS reali.
>
> [link al post]
>
> #ETF #Leva #Investimenti

---

## Note operative

- **Quote tweet utili a 24-48h**:
  - "Il drag dei costi reali (calibrato su SSO ProShares) erode il 91% del 'miracolo' della 3x sulla S&P, su 50 anni. Nessun TER stimato, nessuna assunzione: confronto diretto con un ETF vero."
  - "Sui peggiori 20 anni storici 1976-2025 la 3x sull'S&P fa CAGR del 2.44%. La 1x ne fa 6.24%. La leva nelle code è controproducente."

- **Pushback prevedibili**:
  - "Hai usato la 3x come buy & hold di lungo periodo, è stupido!" → vero, ed è proprio quello che l'articolo dimostra. Niente ad hominem: è proprio il caso che molti retail considerano (vedi popolarità di TQQQ).
  - "TQQQ ha fatto +X% negli ultimi 10 anni!" → vero, ma è artefatto di un decennio post-GFC con bull market lineare e tassi a zero (funding cost minimo). Su 50 anni i numeri cambiano. L'articolo lo discute.
  - "Il funding cost non è 1.85%, è più alto/più basso!" → vero, varia con i tassi. È una media di 17.5 anni di SSO. Il messaggio strutturale regge.
