# Thread X — PAC con leva tattica: ne vale la pena?

**Account**: @smartmoneylabIT
**Lunghezza**: 9 post (1 hook + 7 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i PNG in `public/charts/pac-leva-tattica/`

---

## 1/9 — Hook

> Una strategia FinTwit ricorrente: PAC normale + quando il mercato perde il 20% dai massimi, la nuova contribuzione va su un ETF 2x. Quando torna sui massimi, di nuovo 1x.
>
> "Potenzio il rendimento quando serve, senza correre rischio strutturalmente in più."
>
> L'ho testata su 50 anni. Risposta più sfumata di quanto pensassi.
>
> Thread 👇

*Allegare grafico: 01_equity_curves.png*

---

## 2/9 — La regola, in due righe

> $300/mese, 30% NASDAQ + 70% SP500.
>
> Drawdown calcolato separatamente sui due indici (un crash NDX puro non deve trascinare la quota SP500 in leva, e viceversa).
>
> Quando DD < −20% sull'indice → la nuova quota di quel mese va su ETF 2x daily-rebalanced. Quando il DD si riassorbe → si torna in 1x.
>
> Le posizioni 1x già accumulate non si toccano. Solo i nuovi contributi cambiano sleeve.

---

## 3/9 — Gli ETF 2x sono sintetici ma realistici

> Niente trucchi: il 2x non è un "raddoppio magico" del rendimento.
>
> Ho calibrato il funding cost su 17.5 anni di SSO/SPY e 19.5 anni di QLD/QQQ → 1.85%/anno su SP500, 2.18%/anno su NASDAQ.
>
> Drag totale UCITS applicato: SP500 2x = 2.45%/anno, NASDAQ 2x = 2.78%/anno.
>
> Il "raddoppio" è ridotto da volatility drag e costi reali. Numeri onesti.

*Allegare grafico: 06_calibration.png*

---

## 4/9 — Primo verdetto (severo)

> Framework SmartMoneyLab 6+1 metriche (CAGR, win rate, vol, MDD, Sharpe, Sortino, Calmar). Soglia: la tattica deve battere il B&H su almeno 4 metriche su 7.
>
> Risultato:
> • Finestre 15Y → 3/7 passate
> • Finestre 20Y → 2/7
> • Finestre 25Y → 2/7
>
> Verdetto framework: NON VINCE.
>
> CAGR e win rate vincono, ma vol/MDD/Sharpe sono sistematicamente peggiori.

*Allegare grafico: 05_scorecard.png*

---

## 5/9 — Secondo verdetto (opposto)

> Cambia metrica: rapporto valore-finale-tattica / valore-finale-B&H. Money-in-the-bank, non rischio-percepito.
>
> Su finestre 25Y (101 osservazioni rolling):
> • p5: +0.8%
> • Mediana: +8.0%
> • p95: **+71.7%**
> • Win rate finale: **96.0%**
>
> Nelle peggiori finestre 25Y della storia, la tattica PAREGGIA il passivo. Nelle migliori, lascia il PAC passivo indietro del 72%.

*Allegare grafico: 08_asymmetry.png*

---

## 6/9 — L'asimmetria si rafforza con l'orizzonte

> Differenza CAGR tattica − B&H, p5 della distribuzione rolling:
>
> • 15Y: −0.99 pp
> • 20Y: −0.35 pp
> • 25Y: **+0.05 pp**
>
> A 15 anni esiste una vera coda di "perdita relativa" (in alcune finestre brevi la tattica chiude sotto al passivo di ~1 pp/anno).
>
> A 25 anni quella coda scompare. La probabilità di sotto-performare il passivo nel quarto di secolo è virtualmente zero, secondo 50 anni di dati storici.

*Allegare grafico: 07_cagr_percentiles.png*

---

## 7/9 — Il prezzo da pagare (che NESSUNO racconta)

> La narrativa "uso la leva solo quando serve" è in parte fuorviante.
>
> Frazione di tempo passata in 2x sul full period 50Y:
> • NASDAQ: **33.8%** dei mesi
> • SP500: 12.2% dei mesi
>
> Sulle finestre 25Y il dato sale al 44% per NASDAQ. La "tattica" non è chirurgica. È un'esposizione a leva semi-strutturale condizionata ai drawdown.
>
> È proprio per questo che produce extra-rendimento. Non c'è free lunch.

---

## 8/9 — Il numero finale

> 50 anni, $180.000 contribuiti totali ($300/mese × 600 mesi):
>
> • PAC buy & hold: ~$8.18M
> • PAC con leva tattica: **~$9.82M**
>
> Differenza: +$1.64M, +20%.
>
> La tattica produce un capitale finale superiore al passivo nel 96% delle finestre 25Y storiche, con una coda negativa di rendimento composto praticamente azzerata.
>
> Ma il prezzo è un MDD percentuale del portafoglio molto peggiore. Se non lo sopporti emotivamente, capitoli prima del rebound e tutto il vantaggio evapora.

---

## 9/9 — CTA

> Conclusione netta, perché un articolo del genere se la merita:
>
> Misurata col framework 6+1 → NON VINCE.
> Misurata sul payoff finale del PAC → VINCE in modo strutturale e asimmetrico.
>
> Quale dei due verdetti è "quello giusto" dipende da cosa stai facendo e che tipo di investitore sei. L'errore è scegliere uno e fingere che l'altro non esista.
>
> Sul blog: analisi completa + simulatore live in cui muovi soglia e contribuzione e vedi cosa cambia.
>
> [link al post]
>
> #ETF #PAC #Leva #Investimenti

---

## Note operative

- **Quote tweet utili a 24-48h**:
  - "Sul full period la tattica chiude a +20% sul B&H. Sul win rate finale a 25 anni: 96%. Sulla coda di rendimento composto a 25 anni: praticamente zero downside. Ma se guardi MDD percentuale e Sharpe è peggio. Due framework, due verdetti opposti."
  - "Frazione di tempo in 2x su NASDAQ sulle finestre 25Y: 44%. La 'leva tattica' è quasi metà del tempo in leverage. Non è chirurgica, è semi-strutturale condizionata ai drawdown — e funziona proprio per questo."

- **Pushback prevedibili**:
  - "Ma con la leva il MDD esplode!" → vero, MDD% sale fino al −80%. In $$$ veri di un PAC giovane fa molto meno male di quanto il numero suggerisca, perché il MDD si applica a un portafoglio piccolo. L'articolo lo spiega esplicitamente.
  - "Sì ma il volatility drag distrugge il 2x sul lungo!" → calibrato sui dati: drag totale 2.45% (SP500) e 2.78% (NASDAQ)/anno. È sostanziale ma non distrugge. I numeri sono al netto del drag, non al lordo.
  - "Hai usato ETF UCITS o americani?" → simulato con TER UCITS (più conservativo, 0.60% NDX e 0.60% SP500). Articolo lo discute.
  - "Bias di sopravvivenza sull'indice?" → indice usato direttamente, non basket di titoli. NASDAQ Composite e SP500 TR sono indici totali, no survivorship bias.

- **Conversion goal**: portare al simulatore. Il simulatore è il vero hook del post, perché trasforma la lettura passiva in esplorazione attiva.
