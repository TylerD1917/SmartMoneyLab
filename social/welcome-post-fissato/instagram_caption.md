# Caption Instagram: post fissato di presentazione

**Account**: @smartmoneylab_it
**Asset**: `carosello/01.png` … `10.png` (10 slide)
**Uso**: sostituisce il post fissato "Cosa troverai in questa pagina?" (11 slide, cartella `social/Welcome-post/Post Fissato`)
**Struttura**: 3 slide di presentazione → 4 di dimostrazione del metodo su un caso concreto → 2 su cosa c'è → 1 di chiusura

---

## Caption proposta

Benvenuto. Questa è una pagina di analisi quantitativa sulla finanza personale, scritta in italiano, e il patto è semplice: dietro ogni numero che leggi qui c'è una serie storica, uno script Python e un metodo spiegato per esteso. Niente segnali, niente corsi, niente opinioni vendute come dati.

Non sono un consulente finanziario. Sono uno che investe come te e che non si accontenta delle risposte tanto al chilo. Mi faccio le domande che mi farei comunque, e invece di rispondere a intuito vado a vedere cosa dicono i dati. Poi pubblico anche il codice, così non devi fidarti di me: puoi ricontrollare.

Ti faccio un esempio di cosa intendo, perché è più utile di qualsiasi presentazione.

"Quanto rende l'S&P 500 in dieci anni?" Sembra una domanda da una riga. Ho preso la serie total return degli ultimi 25 anni e ho calcolato il rendimento di tutte le finestre di dieci anni possibili, una per ogni singolo giorno di borsa: sono 3.774. Chi è entrato il 9 marzo 2009, il giorno esatto del minimo della crisi, ha portato a casa il 17,6% all'anno per dieci anni. Chi è entrato il 7 agosto 2001 ha fatto l'1,2%. Stesso indice, stessa durata, sedici punti e mezzo di differenza ogni anno, per dieci anni. L'unica variabile è il giorno in cui hai premuto "compra".

Ecco perché quando qualcuno ti risponde con un numero solo, non ti sta mentendo: ti sta mostrando una di quelle 3.774 finestre e tacendo sulle altre 3.773. Di solito la più bella. E tanto per dare le misure: la mediana è 11,7% all'anno, ma il 14% di quelle finestre sta sotto il 7% che trovi in ogni manuale.

Le tre regole che mi sono dato nascono da qui. Si calcolano tutte le finestre, non quella che fa comodo a cose fatte. Il codice esce insieme allo studio. E non si scelgono mai le date di partenza dopo aver visto il risultato.

Sul blog trovi gli studi spiegati passo per passo, i simulatori interattivi da usare sul tuo caso, i template Excel, il codice Python e le serie storiche in CSV.

E ci sono due esperimenti che girano da soli, in pubblico. Nel primo quattro intelligenze artificiali gestiscono 100.000 dollari a testa e vengono confrontate con il mercato e con un portafoglio estratto a caso. Nel secondo, ogni mese, compriamo i cinque titoli più discussi su r/wallstreetbets per vedere se l'entusiasmo della folla vale qualcosa. Si aggiornano automaticamente e sbagliano in pubblico, che è esattamente il punto.

Se c'è una domanda sui numeri a cui non trovi risposta, scrivila nei commenti: le idee per i prossimi studi arrivano quasi tutte da lì.

Tutto è su smartmoneylab.it, link in bio.

---

## Hashtag (primo commento, 15, mix di volumi)

#finanzapersonale #investimenti #educazionefinanziaria #culturafinanziaria #sp500 #etf #borsa #analisiquantitativa #python #rendimenti #interessecomposto #investireinitalia #mercatifinanziari #finanzaindipendente #dataanalysis

---

## Da dove vengono i numeri

Serie S&P 500 **total return** (`data/Sp500/Sp500_TotalReturn1988_USD.csv`), dati fino all'8 luglio 2026. Finestra considerata: gli ultimi 25 anni, dal 9 luglio 2001. Per ogni seduta si calcola il rendimento annualizzato dei dieci anni di calendario successivi.

- finestre possibili: **3.774**
- peggiore: **1,20%** annuo, partenza 7 agosto 2001
- migliore: **17,63%** annuo, partenza 9 marzo 2009
- mediana **11,69%**, media 10,58%, 5° percentile 4,18%, 95° percentile 15,62%
- finestre sotto il 7%: **14%**

Rigenerando le slide fra qualche mese i numeri si spostano di poco, ma vale la pena rifare il conto prima di ripubblicare.

---

## Note operative

- **Da fissare in evidenza** al posto del post attuale. Chi arriva da un reel trova qui il patto e il metodo.
- Le prime tre slide sono presentazione pura: cosa è, cosa non è, chi scrive. La dimostrazione comincia alla quarta, che è anche la copertina migliore se vuoi usarne una come anteprima.
- La slide 4 (17,6 contro 1,2) è il frame che regge da solo. Se un giorno ne ricavi un reel, parti da lì.
- L'ultima slide chiede di salvare il post: sui contenuti di riferimento i salvataggi contano più dei like, e tu i salvataggi li avevi già alti sul carosello del portafoglio decorrelato.

---

## Cosa cambia rispetto al post attuale

- **Da 11 slide dense a 10 leggere**, una sola idea per slide. La versione attuale ha sei schermate da 150-180 parole: su Instagram la lettura si interrompe fra la terza e la quarta.
- **Presentazione davanti, dimostrazione subito dopo.** Il vecchio post arrivava all'argomento forte alla settima slide.
- **Numeri nostri e verificabili**: il vecchio citava 13,75% e 3.781 senza dire da dove venissero. Questi sono ricalcolati sulla serie nel repo, con la provenienza qui sopra.
- **Dominio aggiornato**: il footer attuale dice ancora `smartmoneylab.pages.dev`.
- **Aggiunti i due esperimenti del /lab**, che quando hai fatto il post non esistevano.
- **Refusi del post attuale, da non riportare**: "CARG" invece di CAGR (due volte), "perchè", "10 anni fà", "Templete Excel", "finaziari", "obbiettivo", "volgiamo".
