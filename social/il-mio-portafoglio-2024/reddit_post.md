# Bozza post Reddit — Il mio portafoglio, 31 anni di backtest

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: valore nel post, link soft in fondo, niente self-promo secca.

---

## Titolo (scegline uno)

- Ho semplificato il mio portafoglio in 7 classi e l'ho testato su 31 anni: pareggia l'S&P 500 (non lo batte) ma stacca l'MSCI World, e nel decennio peggiore è l'unico rimasto in positivo
- 31 anni di backtest sul mio portafoglio reale: la diversificazione geografica non batte l'America, ma protegge il caso peggiore molto meglio degli indici

---

## Corpo del post

Premessa: è il mio portafoglio reale, lo faccio per curiosità e per falsificarlo, dati e codice open, linko in fondo.

Un anno fa avevo pubblicato il backtest del mio portafoglio, ma era fatto di 13 asset con molte serie corte (testabile solo dal 2003). L'ho semplificato in 7 classi ad ampia storia, così da testarlo su una finestra più lunga e severa: **luglio 1995 – luglio 2026, 31 anni**, che include dot-com, 2008, il decennio perso di Europa ed emergenti, il 2022.

Allocazione: **USA 20% · Emergenti 20% · Nasdaq/Tech 25% · Smallcap 10% · Europa Momentum 8% · Oro 8% · Energia 9%**. Equity-only, ribilanciata a target ogni gennaio. Total return lordo; due serie a prezzo (Nasdaq, energia) con dividendo figurato dichiarato.

**1. Contro l'S&P 500 è un pareggio, non una vittoria.** CAGR 10,83% vs 10,69%, drawdown massimo migliore (−48% vs −51%) ma volatilità un filo più alta: sul rischio corretto sono pari. Lo dico subito perché è la parte scomoda — chi si aspetta di "battere l'America" diversificando resta deluso: sui questi 31 anni l'S&P è il benchmark più duro.

**2. Contro MSCI World e ACWI, invece, vince netto.** Ed è il confronto giusto per un portafoglio diversificato nel mondo. +2,4 e +2,6 punti di CAGR l'anno; su 10.000€ chiude a 244.706€ contro i ~123.000€ del World e ~116.000€ dell'ACWI. Sulle finestre mobili di 10 anni batte il World nel 98% dei casi e l'ACWI nel 100%; contro l'S&P siamo al 53% (testa o croce).

**3. La parte più interessante è il rischio di coda.** Ho preso, su tutte le finestre mobili, il caso peggiore e il 5° percentile. Nella **peggiore finestra di 10 anni** dei 31 (ingresso marzo 1999, pre-bolla) il portafoglio ha reso **+3,1% annuo: l'unico dei quattro a non perdere** (S&P −3,4%, World −2,5%, ACWI −1,3%). Il 5° percentile a 10 anni è +4,7% per il portafoglio, intorno a zero/negativo per i benchmark. Su nessuna finestra decennale dei 31 avrei chiuso in perdita; per gli indici sì.

**Un caveat onesto su questo punto:** non significa che il portafoglio non crolli. Il max drawdown *dentro* le finestre resta pieno (~−48%): è tutto azionario e nei crolli scende come gli altri. Ciò che la sleeve difensiva reale (oro + energia, al posto delle obbligazioni) e la diversificazione geografica comprano è un **recupero più rapido**, cioè un risultato molto meno rovinato per chi resta 5-10 anni. È il motivo per cui il 1999-2009, disastroso per USA e mercati sviluppati, è stato tollerabile con emergenti, oro ed energia in portafoglio.

**Monte Carlo (10.000 traiettorie, block bootstrap 3 mesi):** a 20 anni la mediana del portafoglio partendo da 10.000€ è ~78k (World ~50k, ACWI ~48k), batte il World nel 98% e l'ACWI nel 100% degli scenari; contro l'S&P resta un pareggio (55%).

**Il limite principale, dichiarato:** bias di selezione retrospettiva — il portafoglio è disegnato oggi conoscendo la storia. È molto più leggero che in passato (classi ampie, non settori di nicchia scelti perché avevano già vinto), e il fatto stesso che non stravinca l'S&P è un segnale che non è sovra-ottimizzato. Ma il backtest dimostra "se i prossimi 31 anni assomigliano agli ultimi 31, funziona", non "funzionerà".

Metodo completo, grafici (incluso il caso peggiore per finestra) e codice qui: [link articolo]. Critiche al metodo e ai dati molto ben accette — in particolare sull'ipotesi dei dividendi figurati e sulla scelta Europa momentum.
