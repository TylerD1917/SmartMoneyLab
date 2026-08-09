# Bozza post Reddit — Azienda più grande / SP1-SP3

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: valore nel post, link soft in fondo. Qui il gancio "al netto delle tasse italiane" è forte per un sub italiano — sfruttalo.

---

## Titolo (scegline uno)

- Comprare ogni anno solo l'azienda più grande del mondo (o le prime 3) batte l'S&P 500? Test su 31 anni, al netto delle tasse italiane
- Ho testato "compra solo la #1 per capitalizzazione" vs un ETF S&P 500, con la fiscalità italiana modellata. Risultati controintuitivi

---

## Corpo del post

Premessa: curiosità personale, dati e codice open, link in fondo.

Gira sempre l'idea: "se avessi comprato solo Apple / solo la più grande di turno, oggi sarei ricco". L'ho testata seriamente su 31 anni (1995-2025), **al netto della tassazione italiana** (26% su plusvalenze e dividendi, compensazione minusvalenze inclusa), contro un ETF S&P 500 ad accumulo — cioè lo strumento che un retail italiano compra davvero.

Due strategie meccaniche:
- **SP1**: ogni anno tutto sull'azienda USA #1 per capitalizzazione. Rotazione annuale.
- **SP3**: ogni anno equal-weight sulle prime 3. Ribilanciamento annuale.

**Risultato 1 — SP3 (le prime 3) è quasi imbattibile, al netto.** Su finestre mobili di 10 anni ha battuto l'ETF ad accumulo in 22 coorti su 22 (100%), con CAGR netto mediano 10.3% contro 6.7% dell'ETF. Anche la peggior coorte SP3 chiude a +0.2% netto, contro −1.2% della peggior coorte ETF. Diversificare su TRE nomi soltanto ha prodotto vantaggio in ogni singolo decennio, tasse pagate.

**Risultato 2 — "solo la #1" (SP1) è la versione peggiore, non la migliore.** A 10 anni rende meno di SP3 (9.8% netto mediano), batte l'ETF solo nel 73% dei casi e sopporta un drawdown massimo dell'−81%. Il dato più eloquente: il Calmar (rendimento/drawdown) di SP1 è 0.201, quello dell'indice 0.200. Identici. Concentrarsi sul singolo colosso non produce alfa: produce leva sull'indice — più rendimento e più rischio nella stessa proporzione.

**Risultato 3 — lo stock-picking versa una fetta enorme allo Stato.** Tax drag annuo: SP1 358 bps, SP3 293 bps, ETF ad accumulo solo 102 bps. Le strategie in azioni singole perdono 3-3.6 volte più rendimento in tasse rispetto all'ETF, perché incassano dividendi tassati ogni anno e realizzano plusvalenze ad ogni rotazione, mentre l'ETF ad accumulo differisce tutto. È un punto che vale per qualunque strategia di stock-picking rispetto all'ETF pigro in Italia.

Numeri full-sample lordi (1995-2025), per contesto: SP1 CAGR 16.3% / MDD −81%; SP3 CAGR 19.1% / MDD −59%; S&P 500 CAGR 11% / MDD −55%.

Il caveat più importante: il 1995-2025 è l'era d'oro delle mega-cap USA (Apple, poi Nvidia). La ricerca accademica di lungo periodo (Dimensional, Research Affiliates) mostra l'opposto: l'azienda più grande tende a *sottoperformare* nel decennio dopo aver toccato la vetta, perché diventa #1 quando le aspettative sono massime. Questi numeri raccontano cosa è successo, non cosa succederà.

La sintesi utile: se questi dati tentano, la parte seria non è "compra la più grande", è "diversificare batte concentrare, e il wrapper fiscale conta quanto la strategia". Un ETF S&P 500 ad accumulo ha reso il 9.9% netto annuo senza farti prendere un −81% e senza dichiarazioni complicate.

Ranking storico delle top-3, motore fiscale e codice Python qui: [link articolo].

**Domanda per voi**: quanto pesa la fiscalità italiana (26% + niente compensazione sui dividendi) nelle vostre scelte tra azioni singole ed ETF ad accumulo? La usate come argomento pro-ETF?

---

## Note operative
- Il gancio fiscale ("al netto delle tasse italiane") è ORO per un sub italiano: la maggior parte dei backtest che girano sono lordi e americani. È il tuo vantaggio competitivo, mettilo nel titolo.
- Allega la scorecard o il grafico equity SP1/SP3/S&P.
- Obiezione prevedibile "survivorship/look-ahead sul ranking": rispondi che il #1 mondiale è un dato pubblico e famoso in ogni anno (nessuno dubitava che Apple fosse la più grande nel 2013), e che dichiari confidenza media sui primi anni.
