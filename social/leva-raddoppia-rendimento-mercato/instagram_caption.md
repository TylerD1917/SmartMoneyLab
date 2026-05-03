# Caption Instagram — La leva raddoppia/triplica?

**Account**: @smartmoneylab_it
**Lunghezza target**: ~1900 caratteri

---

## Caption proposta

"Compro un ETF S&P 500 a leva 3x e tengo 20 anni: triplicherò il rendimento del mercato." Sembra ovvio, intuitivo, quasi un teorema. È sbagliato per due motivi indipendenti, e i numeri lo dimostrano in modo netto.

Sul blog ho confrontato tre portafogli sull'S&P 500 (leva 1x, 2x, 3x daily-rebalanced) su 50 anni di dati 1976-2025. Per i costi reali ho usato il prezzo giornaliero del ProShares Ultra S&P 500 (SSO), l'ETF a leva 2x più antico (lancio 2006). Calibrazione empirica, niente stime: il drag totale di SSO sui 17.5 anni è 2.74%/anno, decomposto in 0.89% di TER e 1.85% di funding cost. Da lì proietto i costi reali per gli ETF UCITS (Xtrackers 2x, WisdomTree 3x) che il retail italiano effettivamente compra.

Tre risultati centrali:

• La leva 2x non raddoppia. La 3x non triplica. Sui 50 anni del dataset il moltiplicatore implicito è 1.55× per la 2x e 1.84× per la 3x — lontano dal nominale.

• L'erosione cumulata è devastante. 1$ investito nel 1976 con buy & hold daily diventa: $222 con la 1x, $3.873 con la 2x, $14.943 con la 3x. Ma il "miracolo lordo" (matematica pura senza costi) sarebbe stato $228, $14.490 e $167.810. Cioè il 91% del valore "miracolo" della 3x si dissolve solo per i costi reali. Niente survivorship bias, niente cherry-picking — confronto diretto con un ETF vero.

• A 20 anni la 3x non offre nessun vantaggio mediano sulla 2x (CAGR mediano: 13.87% vs 13.82%, identici). E nei peggiori 5% delle finestre 20Y, la 3x fa CAGR del 2.44%, contro il 6.24% della semplice 1x. Nelle code la leva non amplifica: danneggia.

Bonus drammatico: nel 100% delle finestre 20Y la 3x ha visto un drawdown peggiore del −75%. Su 121 finestre osservate, IN TUTTE. Non è rischio raro — è il funzionamento normale.

L'analisi completa, con i due scenari (lordo e realistico), 3 orizzonti rolling, codice Python e calibrazione SSO, è sul blog → link in bio.

—
SmartMoneyLab — Finanza personale e analisi quantitativa.
Disclaimer: contenuto informativo, non consulenza.

---

## Hashtag (15 — mix high/medium/low volume)

#etf #leva #investimenti #investireinitalia #azioni #portafoglio #sp500 #tqqq #upro #leveragedetf #educazionefinanziaria #culturafinanziaria #fintwit #investitoreretail #volatility

---

## Note operative

- Hashtag in primo commento, non in caption.
- Aggiornare temporaneamente il "link in bio" col link diretto al post per i 7-10 giorni post-pubblicazione.
- Tono: NON dire "chi usa la leva è stupido". L'articolo dice che esiste un caso d'uso (posizioni piccole, brevi, con conviction). Mantieni un tono che invita all'analisi, non al disprezzo.
- Risposte ai commenti: aspettati polarizzazione ("ma TQQQ ha fatto +500%!" "è ovvio, la leva fa drag"). Per i pro-leva: "vero ma negli ultimi 10 anni di bull market lineare. Su 50 anni i numeri cambiano". Per gli anti-leva: "esiste un caso d'uso ristretto (vedi articolo)".
