# Bozza post Reddit — Correlazioni tra asset class

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: valore nel post, link soft in fondo, niente self-promo secca.

---

## Titolo (scegline uno)

- Ho misurato la correlazione tra 31 asset class su 20 anni. La diversificazione geografica è quasi un'illusione (USA-MSCI World: 0.97)
- Quali asset diversificano DAVVERO? Ho calcolato la matrice di correlazione tra 31 asset class (2006-2026)

---

## Corpo del post

Premessa: lo faccio per curiosità personale, dati e codice open, linko in fondo.

"Diversifica" è il primo comandamento della finanza personale. Ma diversificare funziona solo se gli asset si muovono *diversamente*. Ho misurato la correlazione reciproca tra 31 asset class (materie prime, settori, indici geografici), su 20 anni di rendimenti mensili in dollari (2006-2026), tutto total return via ETF USA quotati.

**1. La diversificazione geografica dentro l'azionario è in gran parte un'illusione.** Correlazione media azionario-azionario: 0.67. Le coppie più correlate:

- USA (S&P 500) — MSCI World: 0.97
- Europa — Germania: 0.95
- Europa — Regno Unito: 0.95
- Value — S&P 500: 0.95

Comprare "il mondo" invece del solo S&P 500 è, in dollari, quasi lo stesso investimento. In parte è tautologico (gli USA pesano ~70% dell'MSCI World), ma è proprio il punto: la diversificazione geografica azionaria sposta molto meno di quanto si crede.

**2. I veri diversificatori non sono azionari.** Correlazione media di ogni asset con il blocco azionario:

- Treasury USA 20+ anni: −0.06 (unico negativo)
- Oro: +0.15
- Argento: +0.28
- Petrolio: +0.32
- ...poi tutto l'azionario: da +0.48 a +0.97

Correlazione media azionario-rifugi: 0.23, contro 0.67 interno all'azionario. Sono obbligazioni lunghe, oro e materie prime a cambiare il profilo di rischio, non l'ennesimo indice azionario.

**3. La diversificazione svanisce proprio nei crolli.** Correlazione azionaria media: 0.67 nel periodo pieno, ma 0.77 nel 2008 e 0.89 nel COVID 2020. Quando serve di più, tutto l'azionario mondiale cade insieme. (Curiosità: l'orso 2022 fa 0.65, in linea con la media — perché fu un calo "ordinato" da tassi, non un panico di liquidità.)

**4. Esperimento: un portafoglio scelto SOLO per bassa correlazione.** Ho cercato via brute force, tra 80.000 combinazioni, i 5 asset più scorrelati tra loro: oro, petrolio, Treasury, finanziari, semiconduttori (correlazione media interna 0.07). Equal weight, buy&hold, 2006-2026, contro l'S&P 500:

- CAGR: 11.5% vs 11.3%
- Max drawdown: −32% vs −51%
- Calmar: 0.36 vs 0.22

Stesso rendimento del mercato, con un drawdown quasi dimezzato. Scegliendo gli asset *senza guardare i rendimenti*, solo la correlazione.

Caveat onesto e importante: su finestre di 10 anni questo portafoglio batte l'S&P sul rendimento puro solo nell'11% dei casi. La diversificazione NON serve a battere il mercato — serve a ottenere un rendimento simile con molto meno rischio, e a restare investiti quando gli altri vendono nel panico. Nessun pasto gratis.

Bonus: Bitcoin, sulla finestra 2014-2026, correla +0.34 con l'S&P 500. Il "diversificatore assoluto" della narrativa cripto non regge più.

Limiti: tutto in USD (un investitore in EUR vedrebbe correlazioni un po' diverse per via del cambio); le correlazioni non sono stabili e cambiano tra le epoche (azioni-obbligazioni furono correlate positivamente negli anni '70); il portafoglio min-corr è ottimizzato in-sample, è illustrativo non operativo.

Matrice completa (CSV), heatmap interattiva e codice Python qui: [link articolo].

**Domanda per voi**: quanto peso date agli asset non-azionari (bond, oro, commodity) in portafoglio? O puntate su 100% azionario globale accettando che "diversificato per paese" nei crolli conta poco?

---

## Note operative
- Allega la heatmap (01_heatmap_principale.png) e il grafico del portafoglio min-corr: molto visivi.
- Il gancio "USA-World 0.97" nel titolo è quello che fa cliccare — tienilo.
- Preparati alla obiezione "ma io investo in EUR": è nei limiti, rispondi che il quadro generale regge, cambiano i valori puntuali.
