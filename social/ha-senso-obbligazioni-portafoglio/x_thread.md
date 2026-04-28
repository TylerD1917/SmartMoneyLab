# Thread X — Ha ancora senso inserire obbligazioni in portafoglio?

**Account**: @smartmoneylabIT
**Lunghezza**: 7 post (1 hook + 5 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30 (orari di picco FinTwit IT)
**Asset visivi**: i 4 PNG in `public/charts/ha-senso-obbligazioni-portafoglio/`

---

## 1/7 — Hook

> Le obbligazioni servono in portafoglio?
>
> La risposta della banca: "il 60/40 è la regola d'oro".
> La risposta dei dati: dipende da una variabile che il consulente quasi mai ti chiede.
>
> Ho fatto girare 25 anni di S&P 500 e Treasury 10Y su tutte le finestre rolling 5y e 10y. Buy & hold puro, niente rebalancing.
>
> Risultato in 6 post 👇

*Allegare grafico: 01_boxplot_cagr_10y.png*

---

## 2/7 — Setup metodologico

> Per filtrare i seri dai bot, ecco il setup:
>
> • S&P 500 Total Return + UST 10Y Constant Maturity, 2001-2025
> • Tre portafogli buy & hold: 100% azionario, 60/40, 40/60
> • Niente rebalancing (per non dover stimare costi di transazione che il pure-equity non ha)
> • Rolling windows 5y e 10y, step 3 mesi → 80 finestre 5y, 60 finestre 10y
> • Tutto LORDO
>
> Codice riproducibile linkato in fondo.

---

## 3/7 — Risultati su 10 anni

> CAGR mediano su finestre rolling a 10 anni:
>
> • 100% E: 10.09%
> • 60/40: 7.73%
> • 40/60: 6.24%
>
> Spread di ~2.4 punti l'anno tra 100E e 60/40. Su 30 anni di accumulo: 1€ → 17.7€ col 100E, 9.3€ col 60/40. Il 60/40 finisce con circa metà del capitale.

*Allegare grafico: 01_boxplot_cagr_10y.png*

---

## 4/7 — La sorpresa: p5 a 10 anni

> Aspetta. Guardando le 10y peggiori il quadro si capovolge:
>
> • p5 100% E: 3.10%
> • p5 60/40: 4.05%
> • p5 40/60: 4.50%
>
> Nelle peggiori finestre 10y l'obbligazionario ha effettivamente VINTO l'azionario in CAGR. Sono le 10y che includono dot-com + GFC ravvicinati.

---

## 5/7 — Drawdown: il vero campo di battaglia

> % di finestre 10y con drawdown peggiore di -30%:
>
> • 100% E: 51.7% (più della metà!)
> • 60/40: 0%
> • 40/60: 0%
>
> Mediana del drawdown a 10y nel 100E: -42%.
> Tradotto: la metà degli investitori 100% azionario nel periodo ha vissuto un -42% lungo il percorso. Per molti = differenza tra restare investiti e capitolare al peggio.

*Allegare grafico: 03_drawdown_distribution_5y.png*

---

## 6/7 — Quando hanno senso davvero

> Le obbligazioni nei dati 2001-2025 NON sono uno strumento di rendimento.
> Sono uno strumento di copertura sul percorso.
>
> Hanno senso quando:
> • il capitale ti serve presto (5-7 anni)
> • stai per iniziare il decumulo (sequence-of-returns risk)
> • un drawdown del -40% comprometterebbe il piano
>
> A 15+ anni dall'obiettivo, soprattutto se versi regolarmente, sono in larga parte costo opportunità.

---

## 7/7 — CTA al post completo

> Il punto centrale è il glide path: l'allocazione obbligazionaria non è una costante, è una funzione del tempo che ti separa dall'obiettivo.
>
> Sul blog l'analisi completa, con tabelle dei percentili, codice Python che produce i grafici, e il modello di ricostruzione del UST 10Y total return.
>
> [link al post]
>
> #ETF #Investimenti #Finanza

---

## Note operative

- **Lingua**: italiano. Termini tecnici tenuti in inglese se consolidati (drawdown, rolling, CAGR, buy & hold).
- **Quote tweet utile**: dopo aver postato il thread, considerare un quote tweet del primo post 24-48h dopo, con un singolo numero d'effetto. Esempi: "Nel 51.7% delle finestre 10y, l'investitore 100% azionario ha vissuto un drawdown peggiore del -30%. Lo dicono i dati 2001-2025." — oppure: "Il 60/40 a 30 anni dalla pensione costa quasi metà del capitale finale rispetto al full-equity. Lordo, niente rebalancing, 25 anni di dati."
- **Risposte**: aspettati pushback su (1) "ma in EUR cambia tutto" — risposta: "Hai ragione, l'analisi è USA-centric. La replica con MSCI World + Euro Agg Bond è il prossimo articolo. La metodologia rolling è la stessa." (2) "perché niente rebalancing" — risposta: "Per non penalizzare i portafogli misti con costi di transazione che il 100% azionario buy & hold non avrebbe. Articolo specifico sul rebalancing in coda." Niente difensivismo — riconosci il limite, prometti il follow-up.
