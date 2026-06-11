# Thread X — Una strategia LEAPS batte il mercato?

**Account**: @smartmoneylabIT
**Lunghezza**: 8 post (1 hook + 6 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i 6 PNG in `public/charts/strategia-leaps-vs-buy-and-hold/`

---

## 1/8 — Hook

> Una strategia popolare sul FinTwit americano:
>
> • 70% in call LEAPS sull'S&P 500 (strike 85%, 2 anni)
> • 30% Treasury 10y
> • Roll annuale, rebalancing 70/30
>
> Backtest su 49 anni: 17,4% CAGR vs 11,6% del buy & hold. Su 10k iniziali → 26 milioni vs 2,2 milioni.
>
> Sembra il santo graal. Non lo è. Thread 👇

*Allegare grafico: 01_equity_curve_esempio.png*

---

## 2/8 — Cosa sono le LEAPS in 30 secondi

> LEAPS = Long-term Equity AnticiPation Securities.
>
> Opzioni con scadenza 1, 2 o 3 anni, quotate dal CBOE dal 1990.
>
> Una call LEAPS ti dà il diritto di comprare l'indice a uno strike prefissato, anni dopo. Costo: il premio iniziale. Se l'indice sale, guadagni molto di più di chi ha comprato l'indice. Se l'indice non sale abbastanza, perdi tutto il premio.

---

## 3/8 — Il setup

> • Strike a 85% dello spot al roll → delta iniziale ~0,85-0,90 (l'opzione si muove quasi 1:1 col mercato)
> • Maturity 2 anni → vivi nella zona "tranquilla" del theta decay
> • Roll annuale → chiudi a T=1 anno residuo, riapri T=2y nuovo strike
>
> Pricing Black-Scholes europea con dividend yield. Vol = realized 252d + 3pp di vol risk premium (ipotesi conservativa).

---

## 4/8 — Sui rolling 20y e 30y il LEAPS batte B&H nel 100% delle finestre

> Dati 1977-2025, step 3 mesi:
>
> • Rolling 10y: win rate 83%
> • Rolling 20y: win rate **100%** (117 finestre)
> • Rolling 30y: win rate **100%** (77 finestre)
>
> Outperformance media: +5-6 pp di CAGR/anno.
>
> Cifra impressionante. C'è una fregatura, ed è enorme.

*Allegare grafico: 04_win_rate_per_finestra.png*

---

## 5/8 — Il prezzo del biglietto

> Drawdown massimo LEAPS sul full period: **-83%**.
>
> Peggio: sui rolling ventennali e trentennali il drawdown mediano è strutturalmente **-83%**. Non è un caso limite, è la mediana.
>
> Significa: in metà delle finestre 20y, il portafoglio LEAPS è passato da 10k a 1.700 in qualche punto del percorso.

*Allegare grafico: 03_maxdd_boxplot_rolling.png*

---

## 6/8 — Il colpo di scena: il Calmar identico

> Calmar = CAGR / |MDD|. Misura quanto rendimento ti danno per ogni punto di drawdown.
>
> • Full period LEAPS: 0,2099
> • Full period B&H:   0,2103
>
> **Identici a tre cifre decimali.**
>
> Anche sui rolling 30y la coincidenza si ripete: 0,188 vs 0,191. È la firma matematica della leva pura senza alfa.

---

## 7/8 — Non stai battendo il mercato. Stai comprando più mercato

> Il rapporto delle volatilità è 42,5% / 17,5% = 2,43. Cioè la strategia LEAPS applica una leva implicita di ~2,4× sull'S&P.
>
> Il mercato risponde dando 2,4× più rendimento *e* 2,4× più drawdown. Lungo la stessa retta rischio/rendimento.
>
> Niente skill. Niente premio nascosto. Solo "sono dentro più mercato".

---

## 8/8 — Verdict & link

> Verdict SMLab: **parziale**.
>
> Vince su CAGR e win rate. Non vince su drawdown e Calmar. Lo Sharpe migliora di 6 punti su una scala 0-1.
>
> Funziona se reggi un portafoglio a -80% senza vendere. La storia dei retail dice che quei vent'anni quasi nessuno li fa davvero.
>
> Analisi completa, dati, codice Python e caveat metodologici → smartmoneylab.pages.dev

*Allegare grafico: 02_cagr_boxplot_rolling.png*

---

## Note operative

- Numerazione "x/8" alla fine di ciascun post per chiarezza.
- Allegare le 4 PNG indicate (1, 4, 3, 2) ai post 1, 4, 5, 8 — danno il massimo impatto visivo proprio dove i numeri colpiscono.
- Tono: niente entusiasmo da "growth hacker". Il punto è che il 100% di win rate ventennale è un risultato vero ma fuorviante — il vero insegnamento è il Calmar identico. Lascia che il numero parli.
- Risposte ai commenti: aspettati "ma -80% lo reggo, sono diamond hands" (risposta: "ok, ma il backtest assume zero vendite forzate per 49 anni — incluso il 2009 dopo Lehman. Tu reggevi davvero?") e "il vol risk premium di 3pp è troppo basso" (risposta: "vero, infatti l'abbiamo dichiarato come limite — alzandolo a 5pp il win rate 10y scende ma la conclusione qualitativa regge").
