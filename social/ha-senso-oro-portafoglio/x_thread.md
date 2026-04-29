# Thread X — Ha senso inserire oro in portafoglio?

**Account**: @smartmoneylabIT
**Lunghezza**: 8 post (1 hook + 6 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i 5 PNG in `public/charts/ha-senso-oro-portafoglio/`

---

## 1/8 — Hook

> Buffett dice che l'oro non vale niente — non produce flussi, non genera utili, è solo speculazione.
>
> Ha ragione filosoficamente. Ma cosa dicono i dati?
>
> Ho confrontato 4 portafogli buy & hold (100E, 90/10, 75/25, 50/50 oro) su 50 anni di S&P 500 + LBMA Gold. Niente rebalancing. Niente cherry-picking.
>
> Risultato in 7 post 👇

*Allegare grafico: 01_boxplot_cagr_10y.png*

---

## 2/8 — Il dato che cambia il framing

> Correlazione mensile S&P 500 vs Oro, 1976-2025: **0.0085**.
>
> Praticamente zero. 600 mesi di osservazione in cui i due asset si sono mossi in modo sostanzialmente indipendente.
>
> Per confronto: la correlazione tra azioni e bond USA si è mossa tra +0.3 e -0.4 a seconda del regime. L'oro proprio no.
>
> A livello statistico è un diversificatore VERO.

---

## 3/8 — Il costo è bassissimo

> CAGR full-sample 1976-2025 (buy & hold puro):
>
> • 100% E: 11.90%
> • 90/10:  11.70%
> • 75/25:  11.34%
> • 50/50:  10.60%
>
> Il 90/10 perde 20 bps. Il 50/50 perde 130 bps.
>
> Geometria completamente diversa rispetto al 60/40 obbligazionario, che perdeva 240 bps nello stesso pattern.

---

## 4/8 — La protezione nei worst case 10y

> p5 del CAGR su finestre rolling 10 anni:
>
> • 100% E: **1.18%**
> • 90/10: 4.31%
> • 75/25: 6.19%
> • 50/50: **6.43%**
>
> Nelle 10y peggiori, OGNI allocazione con oro batte il pure-equity. Il 50/50 ha p5 di oltre 5 punti percentuali sopra al 100E.

*Allegare grafico: 01_boxplot_cagr_10y.png*

---

## 5/8 — Mito che cade: a 20 anni "non c'è rischio"

> A 20 anni:
>
> • 100% E: 100% delle finestre con drawdown ≥ -20%, 78.5% ≥ -30%
> • 90/10: 100% e 77.7%
> • 75/25: 100% e 57.9%
> • 50/50: 99% e 56.2%
>
> NESSUN portafoglio sfugge ai drawdown profondi sul lungo. L'idea che "sul lungo non c'è rischio" è marketing. Il rischio c'è, è il viaggio.

*Allegare grafico: 05_boxplot_cagr_20y.png*

---

## 6/8 — La curiosità: il 50/50 ha più volatilità del 100E

> Volatilità annualizzata full-sample:
>
> • 100% E: 12.28%
> • 90/10: **12.09%** (la più bassa)
> • 75/25: 12.13%
> • 50/50: 12.51% (più alta del 100E!)
>
> L'oro è decorrelato MA porta vol propria (~16% storica). Il "punto dolce" della diversificazione è il 90/10. Risultato controintuitivo da spiegare onestamente.

---

## 7/8 — Quanto e per chi

> I dati suggeriscono il "punto dolce" tra 10% e 25%:
>
> • 90/10 → costo ~zero, protezione moderata. Default sensato per quasi tutti.
> • 75/25 → costo modesto, protezione massima. Sweet spot rapporto/protezione.
> • 50/50 → ha senso solo se sei particolarmente avverso ai drawdown.
>
> Differenza strutturale dai bond: l'oro ha senso anche in accumulo, non solo in decumulo.

---

## 8/8 — CTA

> L'oro è un asset speculativo nel senso tecnico (no flussi, no valore intrinseco). Ma empiricamente è il diversificatore più stabile che abbiamo nei 50 anni di dati.
>
> Sul blog: l'analisi completa con 3 orizzonti (5y, 10y, 20y), i 4 portafogli, il confronto coi bond, e il codice Python che produce tutti i grafici.
>
> [link al post]
>
> #ETF #Oro #Investimenti

---

## Note operative

- **Lingua**: italiano. Termini tecnici tenuti in inglese se consolidati.
- **Quote tweet utili a 24-48h**:
  - "Correlazione mensile S&P 500 vs LBMA Gold sui 50 anni 1976-2025: 0.0085. Praticamente zero. È il dato più stabile della letteratura sulla diversificazione."
  - "A 20 anni il 100% delle finestre 100% azionario ha visto un drawdown >20%. Il 78.5% >30%. Sul lungo non c'è rischio? È un mito."
- **Pushback prevedibili**:
  - "Ma in EUR è diverso!" → vero, la replica EUR-centric è il prossimo articolo. La metodologia regge.
  - "L'oro non produce niente, è una bolla" → argomento filosofico legittimo (anche Buffett la pensa così). Ma il dato empirico di decorrelazione è separato dalla critica al "valore intrinseco". L'articolo lo spiega.
  - "Hai considerato l'oro fisico vs ETC?" → questa analisi è sul prezzo spot LBMA, no costi di custodia/storage, no premium ETC. Articolo separato sui costi reali.
