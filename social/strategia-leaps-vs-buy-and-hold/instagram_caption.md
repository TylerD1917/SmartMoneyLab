# Caption Instagram — Una strategia LEAPS batte il mercato?

**Account**: @smartmoneylab_it
**Lunghezza target**: ~2000 caratteri

---

## Caption proposta

70% del capitale in call LEAPS sull'S&P 500 + 30% in Treasury 10y, roll annuale, rebalancing al 70/30. È una strategia popolare sul FinTwit americano, una variante del Lifecycle Investing di Ayres & Nalebuff. La promessa è "leva pulita senza il volatility drag degli ETF a leva daily". Funziona davvero?

Sul blog ho fatto girare 49 anni di dati S&P 500 (1977-2025), pricing delle opzioni con Black-Scholes, volatilità implicita stimata come realized 252d + 3 punti di vol risk premium, risk-free dalla FRED + dataset Shiller per il periodo pre-2001. Tutto coerente con la nostra metodologia rolling-windows: nessun cherry-picking sul punto di partenza, 10y/20y/30y in parallelo, step 3 mesi.

I tre risultati centrali:

• Su carta la strategia stravince. CAGR 17,4% vs 11,6% del buy & hold puro. Su 10.000 di capitale iniziale il portafoglio LEAPS chiude a 26 milioni, il buy & hold a 2,2 milioni. Sui rolling ventennali e trentennali, vince nel 100% delle finestre. Sui 10y il win rate è 83%.

• Il prezzo del biglietto è strutturale. Drawdown massimo full period -83% vs -55% del buy & hold. Sui rolling 20y e 30y il drawdown mediano è -83% — non un'eventualità rara, è capitato in più della metà delle finestre lunghe. Il portafoglio LEAPS, prima o poi, perde quattro quinti del valore di picco.

• Il colpo di scena è il Calmar ratio. Calmar = CAGR / |MDD| misura quanto rendimento ottieni per ogni punto di drawdown sopportato. Full period LEAPS: 0,2099. Full period B&H: 0,2103. Identici a tre cifre decimali. La coincidenza si ripete sui rolling 30y. È la firma matematica della leva pura senza alfa: la strategia LEAPS applica una leva implicita di ~2,4× sull'S&P, e il mercato risponde proporzionalmente sia in rendimento che in rischio. Non c'è skill, non c'è premio nascosto.

In altre parole: non stai battendo il mercato. Stai comprando più mercato a un costo di finanziamento implicito conveniente. Verdict SmartMoneyLab: parziale.

Funziona finché reggi -80% senza vendere. Dato che la stragrande maggioranza dei retail vende molto prima, è "una strategia che batte chi resta in piedi" più che "una strategia che batte il mercato".

L'analisi completa, codice Python, caveat metodologici sul vol risk premium, modello bond Constant Maturity Treasury → link in bio.

—
SmartMoneyLab — Finanza personale e analisi quantitativa.
Disclaimer: contenuto informativo, non consulenza finanziaria.

---

## Hashtag (15 — mix high/medium/low volume)

#opzioni #leaps #investimenti #investireinitalia #sp500 #portafoglio #leva #fintwit #blackscholes #educazionefinanziaria #culturafinanziaria #azioni #investitoreretail #backtest #quantfinance

---

## Note operative

- Hashtag in primo commento, non in caption.
- "Link in bio" aggiornato al post per i 7-10 giorni post-pubblicazione.
- Tono: niente toni da "ho scoperto il santo graal" e niente toni da "ti dicono falsità". L'analisi è onesta — la strategia vince e perde insieme. Lascia parlare il Calmar.
- Risposte ai commenti probabili:
  - "Ma il vol risk premium di 3pp è troppo basso!" → "vero, è il caveat principale dichiarato nell'articolo. Con +5pp il win rate 10y scende dall'83 al ~75%, ma la conclusione sul Calmar regge".
  - "-80% di drawdown lo reggo, sono diamond hands" → "il backtest assume zero vendite per 49 anni, incluso Lehman e COVID. La storia dei retail dice che quasi nessuno regge davvero".
  - "Posso replicarla in Italia?" → "non con broker italiani mainstream. Servono IBKR o Tastytrade, e fiscalità delle opzioni in dichiarazione (sezione II del 770). Articolo dedicato in lavorazione".
