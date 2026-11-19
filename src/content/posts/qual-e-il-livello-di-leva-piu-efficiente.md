---
category: "strategie"
title: "Esiste un livello di leva efficiente? Nove gradazioni fra 1x e 2x su 51 anni e tre indici"
description: "Fra l'ETF normale e il 2x ci sono nove gradazioni. Su 51 anni e tre indici la leva paga solo oltre i vent'anni, e il livello che conviene scende al crescere della volatilità."
pubDate: 2026-11-19
tags: ["leva", "etf", "asset-allocation", "rolling-windows", "backtest", "sp500", "nasdaq", "msci-world"]
author: "SmartMoneyLab"
simulationSlug: "qual-e-il-livello-di-leva-piu-efficiente"
seoImage: "/charts/qual-e-il-livello-di-leva-piu-efficiente/13_p5_per_orizzonte.png"
draft: false
---

## In breve

In un [articolo precedente](/posts/leva-raddoppia-rendimento-mercato) avevo visto che sui periodi lunghi la leva 3x sottoperforma la 2x su quasi ogni metrica. Restava aperta la domanda opposta: nella regione *sotto* il 2x, dove nessun ETF esiste, c'è un livello di leva che conviene davvero? Ho testato nove gradazioni (1,00, 1,10, 1,25, 1,40, 1,50, 1,60, 1,75, 1,90, 2,00) su S&P 500, Nasdaq Composite e MSCI World, dal gennaio 1975 al luglio 2026, con il costo del prestito agganciato ai tassi di mercato invece che fissato a tavolino. Quattro risultati:

1. **L'orizzonte conta più del livello.** Sulle finestre mobili a dieci anni la leva non migliora mai lo scenario sfortunato: il quinto percentile del rendimento annuo è massimo a leva 1,00 su tutti e tre gli indici e cala senza eccezioni. Sulle finestre a vent'anni si ribalta, e una leva moderata migliora insieme la mediana e il rendimento del 5% di ingressi più sfortunati.
2. **Il livello che conviene scende al crescere della volatilità.** A vent'anni il quinto percentile è massimo a leva 1,40 sull'S&P 500, 1,25 sul Nasdaq, 1,10 su MSCI World. Non è un numero universale, è una funzione di quanto balla l'indice sotto.
3. **Senza ribilanciamento la domanda non ha nemmeno senso.** Un mix comprato al 50% di ETF 2x e lasciato stare non resta a leva 1,50: arriva a 1,82. Peggio, la leva effettiva tocca il massimo il 23 marzo 2000 e il 19 febbraio 2020, cioè nei giorni esatti dei massimi di mercato, e il minimo il 9 marzo 2009, il giorno esatto del minimo.
4. **Lo Sharpe che usiamo di solito, su questa domanda, non misura niente.** Senza sottrarre il tasso a breve cala con la leva per pura algebra, qualunque dato gli si dia. Sottraendolo, la curva diventa quasi piatta: sull'S&P passa da 0,488 a 0,460 su tutto l'intervallo, e sul Nasdaq ha un massimo interno a 1,25.

Tutto quanto segue è **al lordo delle imposte italiane sulle plusvalenze e dei costi di transazione**, che il ribilanciamento annuale genera davvero. I numeri vanno letti come un tetto superiore.

## La domanda

L'offerta di ETF a leva è discreta, non continua: esiste l'1x, esiste il 2x, esiste il 3x. Non esiste un 1,40x. Ma un portafoglio sì: se metto il 40% in un ETF 2x e il 60% in un ETF normale, il primo giorno la mia esposizione al mercato è esattamente 1,40 volte il capitale.

La domanda che mi interessa è se in quella regione intermedia esista un punto in cui la leva "conviene", nel senso delle metriche con cui giudichiamo i portafogli e non solo del rendimento composto. Perché il risultato dell'articolo sulla 3x suggeriva una curva con un massimo da qualche parte: se la 3x è peggio della 2x, e la 2x costa cara rispetto all'1x, il massimo potrebbe stare in mezzo.

## Come si costruisce una leva 1,40

Ogni livello è un portafoglio di due strumenti realmente acquistabili in Europa:

`leva L = (L-1) in ETF 2x daily + (2-L) in ETF 1x`

Quindi leva 1,10 significa 10% in 2x e 90% in 1x; leva 1,75 significa 75% e 25%. I due comparti pagano costi diversi: all'1x applico un TER dello 0,05% annuo, al 2x un TER dello 0,60% (quelli tipici dei prodotti UCITS) più il costo del denaro preso a prestito, perché un 2x per ogni euro di capitale ne prende a prestito un altro.

C'è una proprietà matematica che vale la pena enunciare perché rende il test pulito: **un mix 1x/2x ribilanciato ogni giorno è identico, euro per euro, a un ETF a leva frazionaria che non esiste**. L'ho verificato numericamente sul periodo intero e i due montanti coincidono a tutte le cifre. Quindi quando parlo di "leva 1,40" non sto approssimando qualcosa, sto costruendo esattamente la cosa di cui parlo.

## Il costo del prestito: dove questo articolo si stacca dal precedente

Nell'articolo sulla 2x e 3x avevo calibrato il costo della leva sui prezzi reali del ProShares Ultra S&P 500 (SSO), l'ETF 2x più antico disponibile, ottenendo un drag di funding dell'1,85% annuo per unità di leva. Quel numero è corretto, ma è corretto *per la finestra in cui l'ho misurato*: 2006-2023, un periodo in cui i Fed Funds hanno fatto in media l'1,32%.

Sul periodo di questo articolo la media dei Fed Funds è il **4,68%**, con il 9,01% fra il 1975 e il 1989 e un picco del 19,10% nel giugno 1981, contro lo 0,52% fra il 2009 e il 2021. Applicare un costo fisso dell'1,85% a cinquant'anni significa regalare alla leva tre punti all'anno negli anni Ottanta, e dato che la domanda dell'articolo è proprio quanto costa prendere a prestito, sarebbe stato un errore che decide il risultato.

Qui il funding è variabile: `Fed Funds del mese + spread`. Lo spread l'ho calibrato cercando il valore che fa coincidere il rendimento composto di una 2x sintetica con quello dell'SSO reale su tutta la sua storia. Viene **0,48%**. Due controlli dicono che il modello è sano:

- sulla finestra di calibrazione produce un funding medio dell'1,80%, cioè praticamente l'1,85% costante del vecchio articolo. Il modello nuovo riproduce il vecchio dove il vecchio era stato tarato;
- sulla stessa finestra l'SSO reale ha reso il 13,24% annuo contro il 16,32% di una 2x sintetica senza costi: tre punti all'anno di differenza, che è esattamente ciò che il modello deve spiegare.

Sul periodo intero il funding medio implicito diventa il **5,15%** annuo per unità di leva. È la differenza fra le due impostazioni, ed è grande.

### Le serie e il total return

Tutti e tre gli indici sono in total return con dividendi reinvestiti, come da regola fissa del blog. L'S&P 500 usa l'indice total return giornaliero dal 1988 e prima il prezzo più i dividendi mensili Shiller distribuiti sui giorni di contrattazione: sulla sovrapposizione fra le due fonti il rendimento composto differisce di 0,049 punti, dentro la tolleranza che ci siamo dati. Il Nasdaq Composite è un indice di prezzo e usa il dividendo figurato dello 0,75% annuo che adottiamo da sempre. Per MSCI World, che pure è di prezzo, non ho usato un numero a occhio: ho ricavato il dividendo confrontando la serie total return mensile MSCI con il prezzo di fine mese, ottenendo il **2,08%** annuo medio, che però vale il 3,16% negli anni Settanta e l'1,61% nel decennio in corso.

## Prima scoperta: senza ribilanciamento la domanda si dissolve

La metodologia standard di questo blog è buy and hold puro, senza ribilanciamenti. Qui ho dovuto derogare, e il motivo è il grafico seguente.

![Leva effettiva di un mix buy and hold](/charts/qual-e-il-livello-di-leva-piu-efficiente/05_drift_leva_buy_and_hold.png)

Il comparto 2x cresce più in fretta dell'1x, quindi il suo peso nel portafoglio aumenta da solo e con esso la leva. Un mix comprato a leva 1,25 sull'S&P 500 chiude il periodo a 1,60. Uno comprato a 1,50 chiude a 1,82. Uno comprato a 1,75 chiude a 1,93. Dopo qualche decennio tutte le gradazioni tendono allo stesso punto, e "leva 1,25" diventa un'etichetta valida solo il giorno dell'acquisto.

Ma la cosa interessante non è la deriva verso l'alto, è la sua **forma**. La leva effettiva non sale in modo regolare: sale nei bull e scende nei bear, cioè è al massimo quando il mercato è caro e al minimo quando è a sconto. Sul mix partito da 1,50:

| data | leva effettiva | cosa succedeva |
|---|---|---|
| 23 marzo 2000 | 1,768 | massimo della bolla dot-com |
| 20 dicembre 2000 | 1,716 | nove mesi dopo, mercato già giù |
| 13 luglio 2007 | 1,690 | massimo pre crisi finanziaria |
| 9 marzo 2009 | 1,434 | minimo assoluto del bear |
| 19 febbraio 2020 | 1,756 | ultimo giorno prima del crollo covid |
| 23 marzo 2020 | 1,656 | minimo covid |

Il portafoglio raggiunge la massima esposizione nel giorno esatto del massimo di mercato e la minima nel giorno esatto del minimo. Non è market timing al contrario per scelta, è una conseguenza meccanica di non ribilanciare: è esattamente il profilo di chi compra alto e vende basso, ottenuto senza fare nulla.

![Buy and hold contro ribilanciamento annuale](/charts/qual-e-il-livello-di-leva-piu-efficiente/06_buy_and_hold_vs_ribilanciato.png)

Sul rendimento composto il buy and hold sembra perfino vincere (a leva iniziale 1,25 rende il 13,70% contro il 13,47% del ribilanciato), ma è un'illusione contabile: rende di più perché passa gran parte del tempo a una leva più alta di quella dichiarata, e infatti la perdita massima peggiora da -64,1% a -69,1%. Non sta battendo il ribilanciamento, sta correndo un rischio diverso.

Da qui in avanti tutti i numeri sono con **ribilanciamento ai pesi obiettivo ogni primo gennaio**.

## Il periodo intero: il rendimento sale, tutto il resto scende

![CAGR al variare della leva](/charts/qual-e-il-livello-di-leva-piu-efficiente/01_cagr_vs_leva.png)

Su 51 anni e mezzo, S&P 500:

| leva | CAGR | volatilità | perdita massima | Calmar | 1$ diventa |
|---|---|---|---|---|---|
| 1,00 | 12,34% | 17,33% | -55,3% | 0,223 | 401$ |
| 1,10 | 12,81% | 18,95% | -58,9% | 0,217 | 498$ |
| 1,25 | 13,47% | 21,42% | -64,1% | 0,210 | 672$ |
| 1,40 | 14,06% | 23,93% | -68,9% | 0,204 | 878$ |
| 1,50 | 14,41% | 25,63% | -72,5% | 0,199 | 1.030$ |
| 1,60 | 14,73% | 27,36% | -76,2% | 0,193 | 1.189$ |
| 1,75 | 15,15% | 30,01% | -81,3% | 0,186 | 1.433$ |
| 1,90 | 15,48% | 32,76% | -85,5% | 0,181 | 1.660$ |
| 2,00 | 15,65% | 34,66% | -88,0% | 0,178 | 1.790$ |

Gli altri due indici raccontano la stessa storia con intensità diverse. MSCI World va dal 10,35% al 12,61%, con la perdita massima che passa da -57,9% a -85,6%. Il Nasdaq è l'unico dei tre in cui il rendimento composto **smette di crescere**: tocca il massimo a leva 1,90 con il 16,25% e scende al 16,16% a leva 2,00. È il primo segnale che da qualche parte la curva gira, e gira prima dove la volatilità è più alta.

![Perdita massima al variare della leva](/charts/qual-e-il-livello-di-leva-piu-efficiente/04_mdd_vs_leva.png)

Un modo compatto di leggere lo scambio: quanti punti di rendimento annuo compri per ogni punto di perdita massima in più. Sull'S&P 500 il rapporto vale 0,130 passando da 1,00 a 1,10, resta a 0,127 fino a 1,40, poi scivola a 0,101 a leva 2,00. Su MSCI World va da 0,109 a 0,082, sul Nasdaq da 0,180 a 0,142. **Il ginocchio della curva sta fra 1,40 e 1,50 su tutti e tre.**

## Una parentesi onesta sullo Sharpe

Il framework che usiamo di solito calcola lo Sharpe come rendimento diviso volatilità, senza sottrarre il tasso privo di rischio. Su quasi tutte le domande è una semplificazione innocua. Su questa no.

Se moltiplico l'esposizione per `L`, il rendimento medio diventa `L` volte quello del mercato meno il costo del prestito, e la volatilità diventa `L` volte quella del mercato. Il rapporto fra i due cala al crescere di `L` per costruzione algebrica, qualunque siano i dati: anche in un mondo dove la leva fosse gratis e perfetta, quello Sharpe scenderebbe. Misura il fatto che sto dividendo per un numero più grande, non una proprietà del mercato.

Il confronto corretto sottrae il tasso a breve, perché la leva è letteralmente denaro preso a prestito a un tasso vicino al monetario.

![Sharpe in eccesso sul monetario](/charts/qual-e-il-livello-di-leva-piu-efficiente/02b_sharpe_eccesso_vs_leva.png)

| leva | S&P 500 | Nasdaq | MSCI World |
|---|---|---|---|
| 1,00 | 0,488 | 0,480 | 0,426 |
| 1,25 | 0,479 | **0,482** | 0,420 |
| 1,50 | 0,472 | 0,477 | 0,412 |
| 1,75 | 0,465 | 0,469 | 0,403 |
| 2,00 | 0,460 | 0,456 | 0,392 |

Sull'S&P 500 l'intero intervallo da 1,00 a 2,00 costa il 5,7% di Sharpe. Sul Nasdaq c'è perfino un massimo interno a leva 1,25. Tradotto: **il mercato prezza la leva in modo quasi equo**. Il problema della leva non è che il prestito sia caro, è la forma che prende la distribuzione dei risultati, ed è lì che bisogna guardare.

Un avvertimento sul Calmar, per lo stesso motivo. Sul Nasdaq ad alta leva la perdita massima arriva a -97,9%, e un rapporto che divide per un denominatore schiacciato contro il -100% smette di distinguere alcunché: infatti il Calmar risulta "migliore" a leva 1,50, ma è un artefatto aritmetico e non un risultato. Su quell'indice, oltre 1,60, il Calmar va ignorato.

## Il cuore: a dieci anni e a vent'anni la risposta è diversa

Qui sta il risultato che non mi aspettavo. Ho ricalcolato tutto su finestre mobili con passo trimestrale, nelle tre lunghezze che usiamo di solito, facendo ripartire i pesi dall'obiettivo all'inizio di ogni finestra.

![Quinto percentile per orizzonte](/charts/qual-e-il-livello-di-leva-piu-efficiente/13_p5_per_orizzonte.png)

Il quinto percentile è il rendimento di chi è entrato nel momento peggiore del campione, e risponde alla domanda che conta davvero quando si parla di leva: cosa succede se mi va male.

**Su dieci anni, su tutti e tre gli indici, il quinto percentile è massimo a leva 1,00 e cala senza eccezioni.** Sull'S&P passa da +1,76% a -4,40%, sul Nasdaq da +1,79% a -7,57%, su MSCI World da +2,52% a -2,33%. Su un orizzonte decennale la leva, a qualsiasi dose, peggiora lo scenario sfortunato. Non esiste un livello efficiente: esiste solo un prezzo.

**Su venti anni la curva si ribalta.**

| leva | S&P 500 | Nasdaq | MSCI World |
|---|---|---|---|
| 1,00 | +6,32% | +6,52% | **+4,76%** |
| 1,10 | +6,48% | +6,68% | **+4,84%** |
| 1,25 | +6,65% | **+6,76%** | +4,75% |
| 1,40 | **+6,72%** | +6,64% | +4,54% |
| 1,50 | +6,71% | +6,46% | +4,40% |
| 1,75 | +6,44% | +5,54% | +3,74% |
| 2,00 | +5,68% | +3,43% | +2,63% |

Su venti anni una leva moderata **migliora anche il caso sfortunato**, cosa tutt'altro che scontata. E il livello in cui il massimo cade scende ordinatamente al crescere della volatilità dell'indice: 1,40 sull'S&P (volatilità 17,3%), 1,25 sul Nasdaq (20,6%), 1,10 su MSCI World.

Vale la pena essere precisi su cosa significhi "caso sfortunato", perché la risposta cambia a seconda di quanto a fondo si guarda nella coda. Sull'S&P 500, finestre ventennali:

| statistica | leva che la massimizza | valore senza leva | valore alla leva migliore |
|---|---|---|---|
| minimo assoluto | 1,10 | 4,75% | 4,76% |
| quinto percentile | 1,40 | 6,32% | 6,72% |
| decimo percentile | 1,40 | 7,28% | 7,68% |
| primo quartile | 1,50 | 8,40% | 9,06% |
| mediana | 2,00 | 10,25% | 13,04% |

**Più a fondo si guarda nella coda cattiva, meno leva si vuole.** Nella singola finestra peggiore del campione (ingresso ad aprile 2000, uscita a marzo 2020) la leva 1,40 fa peggio dell'assenza di leva, 4,53% contro 4,75%: quel ventennio contiene due crolli oltre il 50% e la leva li amplifica entrambi. Ma già allargando al 5% di ingressi più sfortunati il segno si inverte, e nelle dieci finestre ventennali peggiori per l'indice semplice la leva 1,40 lo batte comunque nove volte su dieci. Il minimo assoluto è un punto solo, e su quel punto la prudenza vince.

Il caso di MSCI World merita una riga: è l'indice meno volatile dei tre ma quello che tollera meno leva. Non è una contraddizione, è il premio al rischio: su questo periodo World ha reso il 10,41% annuo contro il 12,39% dell'S&P, quindi il margine fra quello che rende e il 5,15% che costa il prestito è più sottile, e si consuma prima.

### Media e mediana

![Mediana per orizzonte](/charts/qual-e-il-livello-di-leva-piu-efficiente/11_mediana_per_orizzonte.png)

Sulla tendenza centrale la storia è l'opposto, e serve guardarle insieme. Finestre a dieci anni, S&P 500:

| leva | media | mediana | dev. standard | p5 | p95 | finestre vinte contro 1,00 |
|---|---|---|---|---|---|---|
| 1,00 | 11,61% | 13,18% | 4,97% | +1,76% | 17,96% | |
| 1,25 | 12,62% | 14,37% | 5,93% | +0,72% | 20,24% | 85,0% |
| 1,50 | 13,45% | 15,24% | 7,03% | -0,64% | 23,46% | 85,0% |
| 1,75 | 14,08% | 15,93% | 8,26% | -2,32% | 26,45% | 83,8% |
| 1,90 | 14,36% | **16,08%** | 9,05% | -3,51% | 28,08% | 79,6% |
| 2,00 | **14,49%** | 16,06% | 9,61% | -4,40% | 29,19% | 78,4% |

Media e mediana continuano a salire quasi fino in fondo mentre il quinto percentile crolla: è la definizione operativa di una scommessa che migliora il risultato tipico e peggiora quello cattivo. Il Nasdaq è l'unico dove anche la tendenza centrale gira: media e mediana toccano il massimo a leva 1,75 (14,20% e 13,76%) e poi scendono.

Il confronto fra media e mediana dice una cosa in più sulla forma della distribuzione. Sull'S&P a dieci anni la media è sotto la mediana a ogni livello di leva (11,61% contro 13,18% senza leva): la coda sinistra è lunga, i decenni brutti pesano più di quanto la mediana lasci intuire. Sul Nasdaq **la leva ribalta l'asimmetria**: senza leva la media è sotto la mediana (11,95% contro 12,39%), a leva 2,00 è sopra (13,98% contro 13,53%). Sul Nasdaq la leva produce più decenni mediocri ma allunga la coda dei pochi decenni eccezionali, che è un modo di perdere diverso da quello dell'S&P.

Sulle finestre ventennali, infine, la quota di periodi in cui la leva batte l'assenza di leva resta altissima finché si sta bassi e crolla dopo: sull'S&P 500 è il 100% a leva 1,10 e il 96,9% a 1,50, ma scende all'81,9% a 2,00. Sul Nasdaq il crollo è brutale, dal 97,6% a leva 1,25 al 41,7% a leva 2,00: **oltre il 1,75 la 2x sul Nasdaq perde contro l'indice semplice in più di una finestra ventennale su due**.

## Un'ipotesi che i dati hanno smentito

Partendo mi aspettavo che la leva conveniente scendesse quando il denaro costa di più, perché è il costo del prestito a mangiare il vantaggio. Sembra ovvio. È falso.

![Leva migliore contro il livello dei tassi](/charts/qual-e-il-livello-di-leva-piu-efficiente/10_leva_ottima_vs_tassi.png)

Misurando per ogni finestra decennale la leva che avrebbe dato il rendimento migliore e confrontandola con i Fed Funds medi di quella finestra, la correlazione è +0,05 sull'S&P 500, -0,16 sul Nasdaq, +0,20 su MSCI World. Cioè nulla, e con il segno sbagliato rispetto all'ipotesi. Sull'S&P la leva migliore media 1,86 nelle finestre a tassi alti (7,03% medi) contro 1,62 in quelle a tassi bassi (1,78% medi).

La spiegazione è che il costo del prestito non va guardato da solo ma contro quello che rendono le azioni, e i decenni di tassi alti sono stati anche decenni di premi al rischio generosi. Guardare il livello dei tassi per decidere quanta leva prendere è guardare metà dell'equazione, ed è la metà che conta meno.

## I limiti

**Lordo di tutto il resto.** Niente imposte italiane sulle plusvalenze, niente bollo, nessun costo di transazione, nessuno spread denaro lettera. Il ribilanciamento annuale realizza plusvalenze vere, su cui in Italia si paga il 26%: è un prelievo che si ripete ogni anno e che riduce il montante in modo composto. I numeri qui sopra sono un tetto superiore, non una previsione.

**Prodotti che in parte non esistono.** Un ETF 2x su S&P 500 o Nasdaq è comprabile in Europa, su MSCI World l'offerta è molto più sottile. Il 2x in questo articolo è sintetico, calibrato su un prodotto americano reale e poi applicato ai tre indici con i costi tipici dei prodotti UCITS.

**Lo spread di funding è uno solo.** Lo 0,48% calibrato su un prodotto fra il 2006 e il 2023 viene applicato anche al 1975-1989, quando i mercati del credito funzionavano diversamente. È l'ipotesi più fragile del lavoro.

**Il campione è uno.** Cinquantun anni sembrano tanti, ma le finestre ventennali si sovrappongono quasi tutte e contengono due o tre crolli veri. Il quinto percentile a vent'anni è stimato su 127 finestre che condividono gran parte della stessa storia.

## Cosa porto a casa

**1. La domanda giusta non è quanta leva, è per quanto tempo.** Sotto i dieci anni non esiste un livello di leva che migliori lo scenario sfortunato, su nessuno dei tre indici. Oltre i venti sì. Chi non ha un orizzonte ventennale davvero disponibile sta comprando solo la coda cattiva.

**2. Se l'orizzonte c'è, la zona è 1,10-1,40 e dipende dall'indice.** Il quinto percentile a vent'anni è massimo a 1,40 sull'S&P 500, 1,25 sul Nasdaq, 1,10 su MSCI World. Più l'indice è volatile rispetto a quello che rende, meno leva tollera.

**3. Oltre 1,50 si paga sempre di più per sempre meno.** Il rapporto fra rendimento guadagnato e perdita massima aggiunta è stabile fino a 1,40 e poi degrada su tutti e tre gli indici. Sopra quella soglia la leva compra quasi solo volatilità.

**4. Una leva comprata e dimenticata non è la leva che credi di avere.** Senza ribilanciamento il livello sale da solo e, cosa peggiore, sale nei massimi e scende nei minimi. Se si usa la leva va tenuta al suo posto, e tenerla al suo posto costa imposte e commissioni che questo articolo non ha contato.

**5. La leva non è cara, è asimmetrica.** Al netto del tasso a breve, lo Sharpe quasi non cambia fra 1,00 e 2,00: il mercato prezza il prestito in modo onesto. Quello che cambia è la forma dei risultati possibili, che si allarga da entrambe le parti ma su un orizzonte breve si allarga più in basso che in alto. La leva non è un rendimento in più da comprare, è un tempo in più da avere.

---

**Fonti e riproducibilità.** Lo script che produce ogni numero e ogni grafico di questo articolo è `scripts/qual-e-il-livello-di-leva-piu-efficiente.py` nel repository del blog. Serie usate: S&P 500 prezzo e total return giornalieri, [dataset Shiller](http://www.econ.yale.edu/~shiller/data.htm) per i dividendi storici, Nasdaq Composite giornaliero, MSCI World prezzo giornaliero e total return mensile, [Fed Funds effective rate da FRED](https://fred.stlouisfed.org/series/FEDFUNDS). Calibrazione del costo della leva sui prezzi del [ProShares Ultra S&P 500 (SSO)](https://www.proshares.com/our-etfs/leveraged-and-inverse/sso).
