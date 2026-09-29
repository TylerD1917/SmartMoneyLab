# Bozza post r/ItaliaPersonalFinance

**Stato**: bozza, non pubblicata
**Strategia**: metodo nel corpo, il difetto dichiarato prima che lo trovino loro, link soft in fondo, domanda finale aperta
**Quando**: prima del 5 ottobre, quando la squadra cambia

---

## Titolo

Sto seguendo in pubblico un portafoglio costruito sui 5 titoli più discussi su r/wallstreetbets: come funziona la selezione e cosa non mi torna del metodo

---

## Corpo

Da anni si legge che il sentiment del retail su r/wallstreetbets sia un indicatore: per alcuni momentum da seguire, per altri il segnale contrarian perfetto. Non ho trovato nessuna verifica fatta su dati pubblici e in avanti, senza scegliere il periodo dopo, quindi ho messo su un esperimento e lo sto pubblicando mese per mese.

**Metodo.** Ogni mese raccolgo le discussioni del subreddit da due fonti pubbliche gratuite (ApeWisdom per menzioni, upvote e crescita, Tradestie per sentiment e commenti) e costruisco un punteggio composito: sentiment 30%, menzioni 25%, commenti 20%, crescita delle menzioni 15%, upvote 10%. Su ogni criterio i titoli vengono messi in classifica e il punteggio è la media pesata dei percentili, non dei valori assoluti, così un titolo con numeri enormi su un solo criterio non domina.

Filtri: fuori ETF e indici (SPY e QQQ sono sempre in alto e comprare l'S&P 500 per poi confrontarsi con l'S&P 500 non direbbe nulla), fuori chi ha sentiment negativo, fuori chi sta sotto le 10 menzioni. I primi cinque entrano equipesati al 20% e restano per tutto il mese. Il valore si ricalcola ogni giorno di borsa sulle chiusure ufficiali, dividendi accreditati su entrambi i lati del confronto, benchmark S&P 500 total return.

**Settembre 2026.** Squadra: LULU, AVGO, SNOW, MSTR, PLTR, comprati il 3 settembre alla chiusura.

La cosa che non mi aspettavo è che il più citato non vinca. AVGO aveva 568 menzioni contro le 79 di LULU, ma le menzioni pesano solo un quarto: LULU aveva il sentiment più alto del pool e la crescita di menzioni più forte, AVGO su entrambi era dietro.

**Il difetto che vedo nel mio stesso metodo.** La crescita delle menzioni di LULU e MSTR è calcolata su una base di **una** menzione il giorno precedente: +7.800% e +4.000% partendo da uno. Con denominatori così un criterio che pesa il 15% può decidere la classifica su rumore puro. Sto valutando di mettere una soglia minima sul denominatore o di sostituire la crescita con una media a più giorni, ma non voglio cambiare la regola a metà corsa dopo aver visto i risultati, quindi per ora resta così, dichiarata. Se qualcuno ha un'idea migliore su come normalizzarla, la ascolto: è il punto più debole della cosa.

**Come è andato il mese.** Al 25 settembre il portafoglio era a -2,0% e l'S&P 500 praticamente fermo. Sono tre settimane su un portafoglio di 5 titoli: non dimostra assolutamente nulla, lo scrivo solo perché i numeri sono pubblici e chiunque può ricontrollarli. Il senso dell'esperimento è accumulare mesi, non commentare il primo.

Zero backtest retroattivi: parte dal 3 settembre 2026 e va avanti anche quando i numeri saranno brutti.

Pagina con la classifica scomposta titolo per titolo, la curva giornaliera e la serie completa in CSV: smartmoneylab.it/lab/reddit-retail-sentiment (è il mio sito, nessuna registrazione né newsletter obbligatoria).

Non è un consiglio di investimento, è un esperimento.

**La domanda che mi interessa:** secondo voi il sentiment retail, se misurato in modo disciplinato, è momentum o contrarian? E su che orizzonte lo misurereste, dato che un mese è chiaramente troppo poco?

---

## Note operative

- Il difetto dichiarato in mezzo al post fa da parafulmine e in più è una vera richiesta di aiuto tecnico: su quel subreddit è il tipo di apertura che genera discussione utile invece di accuse di spam.
- Il link va in fondo e dichiarato come proprio. Niente hashtag, niente emoji.
- Se chiedono i dati grezzi: la serie completa è in `/tools/reddit-sentiment-nav.csv` e il JSON con punteggi e componenti è in `/tools/reddit-sentiment.json`, entrambi linkabili direttamente.
