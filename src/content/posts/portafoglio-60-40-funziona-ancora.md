---
category: "strategie"
title: "Il portafoglio 60/40 non è morto, anzi, è vivo e lotta assieme a noi"
description: "Portafoglio 60/40 e 80/20 conviene ancora? 55 anni di dati in euro, finestre mobili a 5, 10 e 20 anni, Sharpe e Sortino: rende quasi come il 100% azionario con metà della perdita massima."
pubDate: 2026-11-25
tags: ["portafoglio-60-40", "80-20", "obbligazioni", "asset-allocation", "rolling-windows", "backtest", "msci-world", "sp500", "btp"]
author: "SmartMoneyLab"
simulationSlug: "portafoglio-60-40-ancora-valido"
seoImage: "/charts/portafoglio-60-40-ancora-valido/03_quante_volte_batte.png"
faq:
  - q: "Il portafoglio 60/40 conviene ancora?"
    a: "Sui dati in euro dal 1971 al 2025 un 60/40 MSCI World e titoli di Stato dell'area euro, ribilanciato ogni anno, ha reso l'8,39% annuo contro l'8,49% del 100% azionario, con una perdita massima del 32,7% contro il 55,7%. Su tutte le finestre di 10 anni non ha mai chiuso in perdita e ha avuto uno Sharpe migliore del 100% azionario nel 90% dei casi."
  - q: "Meglio il 60/40 o l'80/20?"
    a: "L'80/20 tiene un po' più di rendimento ma perde gran parte della protezione: nel 46% delle finestre di 10 anni ha subito almeno una perdita oltre il 30% dal massimo, contro il 5% del 60/40. Entrambi battono il 100% azionario per rendimento corretto per il rischio in circa nove finestre di 10 anni su dieci."
  - q: "Per un italiano è meglio usare obbligazioni europee o Treasury americani?"
    a: "Sui dati, obbligazioni in euro oppure Treasury coperti dal cambio. I Treasury in dollari senza copertura, abbinati all'S&P 500, hanno battuto il 100% S&P per Sharpe solo nel 66% delle finestre di 10 anni: per un europeo azioni e obbligazioni americane portano entrambe il rischio dollaro. Con la copertura del cambio la correlazione con le azioni scende da 0,34 a quasi zero."
  - q: "Perché sembra che il 60/40 sia morto?"
    a: "Perché dal 2010 il 100% MSCI World ha reso il 12,11% annuo contro l'8,34% del 60/40, e nel 2022 azioni e obbligazioni sono scese insieme. Ma dal 2010 lo Sharpe dei due portafogli è praticamente uguale (0,93 contro 0,95): il 60/40 ha reso meno perché ha preso meno rischio, non perché ha smesso di funzionare."
draft: false
---

## In breve

Negli ultimi quindici anni l'azionario, soprattutto americano, ha corso così tanto che tenere obbligazioni in portafoglio è passato di moda. Il **portafoglio 60/40** (60% azioni, 40% obbligazioni) viene dato per morto almeno una volta all'anno. Ho voluto verificarlo con i dati, dal punto di vista di un investitore italiano: tutto in euro, dal gennaio 1971 al dicembre 2025, su tutte le finestre mobili di 5, 10 e 20 anni e non su un singolo periodo scelto a posteriori. Ho testato il 60/40 e il fratello più aggressivo, l'**80/20**, con tre gambe obbligazionarie diverse (titoli di Stato dell'area euro, BTP, Treasury americani) e li ho confrontati con il 100% MSCI World e il 100% S&P 500. Cinque risultati:

1. **Il 60/40 in euro rende quasi come il 100% azionario, con metà del rischio.** MSCI World più titoli di Stato dell'area euro, ribilanciato ogni anno: 8,39% annuo contro 8,49% del 100% World, volatilità 9,2% contro 14,7%, perdita massima −32,7% contro −55,7%. Lo Sharpe sale da 0,36 a 0,48, il Sortino da 0,50 a 0,71.
2. **Sui dieci anni non ha mai chiuso in perdita.** Su 181 finestre di 10 anni il rendimento minimo è stato +0,09% annuo, mentre il 100% World ha chiuso in rosso nel 7,2% dei casi. Lo Sharpe del 60/40 è migliore nel 90% delle finestre. Sui vent'anni il 60/40 ha reso *di più* del 100% World nel 70% dei casi.
3. **Il vero errore, per un italiano, è usare obbligazioni in dollari senza copertura.** Abbinati all'S&P 500, i Treasury convertiti in euro battono il 100% S&P per Sharpe solo nel 66% delle finestre di 10 anni: azioni e obbligazioni americane portano entrambe il rischio dollaro. Coperti dal cambio, la correlazione con le azioni crolla da 0,34 a 0,01 e lo Sharpe del misto supera quello dell'S&P nel 96% delle finestre di 20 anni.
4. **Il ribilanciamento conta più di quanto sembri.** Nel 60/40 euro le finestre di 10 anni con una perdita oltre il 30% passano dal 22% in buy & hold al 5% ribilanciando una volta l'anno.
5. **"Il 60/40 è morto" è un'impressione degli ultimi quindici anni.** Dal 2010 il 100% World ha reso il 12,11% annuo contro l'8,34% del 60/40, ma lo Sharpe è identico (0,93 contro 0,95). Il 60/40 ha reso meno perché ha rischiato meno, non perché ha smesso di funzionare.

Tutti i numeri sono **lordi**: niente costi degli ETF, niente imposte, niente costi del ribilanciamento. Vale per tutti i portafogli allo stesso modo, ma il ribilanciamento annuale, che nella realtà genera plusvalenze tassate e commissioni, ne esce leggermente favorito.

## La domanda: il portafoglio 60/40 funziona ancora?

Il 60/40 è stato per decenni il portafoglio "di default" di consulenti e manuali. La logica è semplice: le azioni fanno crescere il capitale, le obbligazioni lo stabilizzano quando le azioni crollano. Due fatti recenti l'hanno messo in discussione. Il primo è il rendimento eccezionale dell'azionario americano dopo il 2009, che ha fatto sembrare ogni euro tenuto in obbligazioni un euro sprecato. Il secondo è il 2022, quando azioni e obbligazioni sono scese insieme per la prima volta da decenni e la "stabilizzazione" non è arrivata.

In un [articolo di aprile](/posts/ha-senso-obbligazioni-portafoglio) avevo già affrontato il tema con 25 anni di dati americani. Questo pezzo lo supera su quattro fronti: **55 anni invece di 25**, **tutto in euro** come lo vive un investitore italiano, **finestre di 20 anni** oltre a quelle di 5 e 10, e **metriche corrette per il rischio** (Sharpe e Sortino) invece del solo rendimento. Le domande sono tre:

1. Quanto rende, in media e negli scenari sfortunati, un portafoglio misto azioni e obbligazioni?
2. Corretti per il rischio, il 60/40 e l'80/20 sono ancora validi rispetto al 100% azionario?
3. Che ETF obbligazionari dovrebbe usare un italiano?

## Il metodo

**I portafogli.** Ho costruito quattro famiglie, ognuna in versione 60/40 e 80/20:

| Coppia | Azioni | Obbligazioni | Dati da |
|---|---|---|---|
| Euro | MSCI World | titoli di Stato area euro, scadenza 7-10 anni | 1971 |
| Italia | MSCI World | BTP, scadenza 7-10 anni | 1980 |
| USA in dollari | S&P 500 | Treasury USA 7-10 anni, senza copertura del cambio | 1971 |
| USA coperta | S&P 500 | Treasury USA 7-10 anni, coperti dal cambio | 1971 |

Le coppie Euro e Italia si confrontano con il 100% MSCI World, quelle americane con il 100% S&P 500 (e, per completezza, anche con il World).

**Le obbligazioni.** Gli ETF obbligazionari esistono da una ventina d'anni, troppo pochi per un test su mezzo secolo. Uso quindi gli indici a duration costante che avevo ricostruito nell'[articolo sul rendimento degli ETF obbligazionari](/posts/quanto-rendono-etf-obbligazionari): simulano un ETF che tiene ferma la scadenza media a 8,5 anni, ricomprando ogni mese titoli nuovi con i rendimenti di mercato. Sono l'equivalente sintetico di prodotti che oggi si comprano davvero, come l'iShares Euro Government Bond 7-10yr o l'Amundi Italy BTP Government Bond 10Y, ma senza i loro costi.

**Valuta e dati.** Tutto è in euro e in **total return**: dividendi e cedole reinvestiti. MSCI World è la versione ufficiale in euro di MSCI. L'S&P 500 è l'indice total return a fine mese, ricostruito prima del 1988 dal prezzo di fine mese più i dividendi di Shiller, e convertito in euro con lo stesso cambio implicito nelle due versioni valutarie del World. Prima del 1999 l'euro non esisteva: MSCI e l'OCSE usano un euro sintetico, e i BTP, che allora erano in lire, li ho convertiti nella stessa unità. Senza questa conversione i BTP degli anni '80 avrebbero incassato le cedole altissime della lira senza pagarne la svalutazione: il loro rendimento 1980-1998 passa dal 16,9% annuo in lire al 13,8% in euro.

**Il Treasury coperto.** Un ETF "EUR hedged" rinnova ogni mese un contratto a termine sul cambio: elimina le oscillazioni euro-dollaro ma incassa o paga la differenza fra i tassi a breve dei due paesi. L'ho modellato esattamente così: rendimento in dollari più la differenza fra tasso interbancario a 3 mesi tedesco e americano.

**Ribilanciamento.** Ogni portafoglio mix stoks / bonds esiste in due versioni: **buy & hold** (compro 60/40 e non tocco più nulla, i pesi derivano con i mercati) e **ribilanciato ogni 12 mesi**, riportando i pesi a quelli di partenza. Senza ribilanciamento, dopo vent'anni di buon mercato azionario un 60/40 diventa di fatto un 80/20.

**Finestre mobili.** Per ogni portafoglio calcolo tutte le finestre di 5, 10 e 20 anni con partenze ogni tre mesi: 201 finestre a 5 anni, 181 a 10, 141 a 20 (meno per i BTP, che partono nel 1980). Per ognuna misuro rendimento annuo composto, volatilità, max drowdown, indice di Sharpe e di Sortino. Sharpe e Sortino sono calcolati sul rendimento in eccesso rispetto al tasso a 3 mesi tedesco, che dal 1999 coincide di fatto con l'Euribor: in 55 anni ha reso il 4,07% annuo, e un portafoglio rischioso deve essere giudicato su quanto fa meglio di quel minimo.

Prima di arrivare ai portafogli, il punto di partenza: le singole gambe, dal 1971 al 2025.

| Gamba, in euro | Rendimento annuo |
|---|---|
| MSCI World | 8,49% |
| S&P 500 | 10,14% |
| Titoli di Stato area euro 7-10 anni | 7,10% |
| BTP 7-10 anni (dal 1980) | 7,67% |
| Treasury USA 7-10 anni, senza copertura | 5,52% |
| Treasury USA 7-10 anni, coperto | 5,67% |
| Tasso a 3 mesi | 4,07% |

## Il risultato principale: stesso rendimento, metà del rischio

![Crescita di 1 euro dal 1971 per 100% MSCI World, 100% S&P 500 e i portafogli misti ribilanciati](/charts/portafoglio-60-40-ancora-valido/01_crescita_1971.png)

Sull'intero periodo, un euro investito nel gennaio 1971 è diventato 88 euro nel 100% MSCI World e 84 euro nel 60/40 euro ribilanciato. Una differenza quasi invisibile su 55 anni. Il grafico però mostra dove sta la differenza vera: nelle discese del 1973-74, del 2000-2002 e del 2008 la linea del 60/40 scende molto meno.

| 1971-2025, ribilanciati | Rend. annuo | Volatilità | Perdita max | Sharpe | Sortino |
|---|---|---|---|---|---|
| 100% MSCI World | 8,49% | 14,7% | −55,7% | 0,36 | 0,50 |
| 60/40 World + titoli euro | 8,39% | 9,2% | −32,7% | 0,48 | 0,71 |
| 80/20 World + titoli euro | 8,52% | 11,9% | −42,5% | 0,41 | 0,59 |
| 100% S&P 500 | 10,14% | 16,3% | −60,2% | 0,43 | 0,62 |
| 60/40 S&P + Treasury in dollari | 8,72% | 12,1% | −39,3% | 0,42 | 0,62 |
| 60/40 S&P + Treasury coperto | 8,99% | 10,3% | −32,0% | 0,50 | 0,75 |

Il 60/40 Euro cede un decimo di punto di rendimento annuo e in cambio taglia la volatilità di oltre un terzo e la perdita massima di 23 punti. Lo Sharpe, che misura quanto rendimento in più si ottiene per ogni unità di rischio, sale di un terzo. Il Sortino, che penalizza solo le oscillazioni verso il basso, sale ancora di più: da 0,50 a 0,71. In due delle crisi peggiori del periodo il 60/40 ha perso meno della metà dell'azionario: −20,9% contro −44,6% fra il 2000 e il 2002, −19,1% contro −37,3% nel 2008, l'anno in cui i titoli di Stato dell'area euro hanno guadagnato l'8,1%.

L'80/20 sta in mezzo e sull'intero periodo ha reso addirittura un soffio più del World (8,52% contro 8,49%), con una perdita massima ridotta a −42,5%.

## Le finestre mobili: il 60/40 non chiude mai un decennio in perdita

Un singolo periodo di 55 anni dice poco a chi investe per 10 o 20. Le finestre mobili rispondono alla domanda giusta: comprando in un momento qualsiasi, cosa sarebbe successo?

![Rendimento annuo su tutte le finestre di 10 anni, box dal 25° al 75° percentile e baffi dal 5° al 95°](/charts/portafoglio-60-40-ancora-valido/02_rendimenti_10y.png)

| Finestre di 10 anni, ribilanciati | Mediana | 5° percentile | Peggiore | In perdita |
|---|---|---|---|---|
| 100% MSCI World | 9,53% | −1,33% | −4,31% | 7,2% |
| 60/40 World + titoli euro | 8,95% | 1,97% | 0,09% | 0,0% |
| 80/20 World + titoli euro | 9,33% | 0,47% | −1,84% | 4,4% |
| 60/40 World + BTP | 8,76% | 1,51% | 0,10% | 0,0% |
| 100% S&P 500 | 12,66% | −2,19% | −5,24% | 8,8% |
| 60/40 S&P + Treasury in dollari | 10,51% | 0,62% | −1,28% | 3,9% |
| 60/40 S&P + Treasury coperto | 10,27% | 2,33% | 0,14% | 0,0% |

Il quadro è coerente: il 60/40 perde poco più di mezzo punto di rendimento mediano, ma **sposta verso l'alto tutta la coda sfortunata della distribuzione**. Il 5% peggiore dei decenni del 100% World chiude sotto −1,33% annuo, quello del 60/40 euro sopra +1,97%. Il peggior decennio possibile del 60/40 è stato un pareggio, quello del World una perdita del 4,31% all'anno, cioè circa un terzo del capitale in dieci anni.

A cinque anni l'azionario puro chiude in perdita una volta su cinque (20,9% delle finestre del World), il 60/40 euro una volta su venti (5,5%). A vent'anni nessun portafoglio ha mai perso soldi, e la mediana del 60/40 ribilanciato (8,06%) supera quella del 100% World (7,95%).

### Quante volte il misto batte il 100% azionario

Questa è la domanda centrale dell'articolo, e la risposta cambia molto secondo il criterio:

![Quota di finestre di 10 e 20 anni in cui il misto batte il 100% azionario per rendimento e per Sharpe](/charts/portafoglio-60-40-ancora-valido/03_quante_volte_batte.png)

| % di finestre in cui il misto batte il 100% azionario | 10 anni, rendimento | 10 anni, Sharpe | 20 anni, rendimento | 20 anni, Sharpe |
|---|---|---|---|---|
| 60/40 World + titoli euro | 55% | 90% | 70% | 100% |
| 80/20 World + titoli euro | 60% | 92% | 72% | 100% |
| 60/40 World + BTP | 64% | 93% | 79% | 100% |
| 60/40 S&P + Treasury in dollari | 20% | 66% | 21% | 71% |
| 60/40 S&P + Treasury coperto | 30% | 72% | 37% | 96% |

Sul rendimento puro, il 60/40 euro batte il World poco più di una volta su due a dieci anni. Sul rendimento corretto per il rischio lo batte nove volte su dieci, e a vent'anni sempre. Il Sortino dà risultati praticamente identici (91% a dieci anni, 100% a venti).

Il dato a vent'anni sul rendimento puro sorprende: in sette finestre su dieci il 60/40 ha reso *più* del 100% azionario. Non è una magia delle obbligazioni, è la combinazione di due cose. La prima sono i lunghi periodi in cui l'azionario globale è andato male, a partire dal decennio perso dopo il 2000. La seconda è il ribilanciamento, che per forza di cosa finisce per vendere le azioni quando sono salite e le ricompra quando sono scese.

## Il 60/40 o l'80/20?

L'80/20 tiene più rendimento nelle fasi buone ma rinuncia a gran parte della protezione:

![Quota di finestre di 10 anni con una perdita oltre il 30% dal massimo, buy & hold contro ribilanciato](/charts/portafoglio-60-40-ancora-valido/04_perdite_oltre_30.png)

Nel 100% World due decenni su tre (66%) contengono almeno un crollo oltre il 30%. Nell'80/20 ribilanciato quasi uno su due (46%). Nel 60/40 ribilanciato uno su venti (5%), e con i BTP nessuno. La perdita massima mediana dentro un decennio è −36,9% per il World, −29,9% per l'80/20 e −22,6% per il 60/40.

Sul rendimento corretto per il rischio, a dieci anni l'80/20 batte il World nel 92% delle finestre, quasi come il 60/40. La differenza vera fra i due non è nell'efficienza ma nella **profondità delle discese**: l'80/20 è un portafoglio azionario un po' smussato, il 60/40 un portafoglio che cambia davvero natura nei crolli. Quale sia il più adatto dipende da quanto si è disposti a vedere il capitale scendere, non da quale renda di più.

## Ribilanciare o no?

Il grafico precedente mostra anche l'effetto del ribilanciamento, ed è il risultato più netto di tutto il test, ha stupito anche me che da grande fan del Prof. Coletti sono poco incline al ribilanciamento. Nel 60/40 euro la quota di decenni con un crollo oltre il 30% scende dal 22% al 5% solo ribilanciando una volta l'anno. Con i BTP dal 16% a zero, con i Treasury coperti dal 14% al 5%.

La ragione è meccanica. Senza ribilanciamento, dopo un lungo rialzo un 60/40 è diventato un 75/25 o un 80/20 proprio nel momento in cui arriva il crollo: si presenta alla discesa con più azioni di quante ne volesse. Ribilanciare tiene il rischio dove lo si era deciso.

Sul rendimento l'effetto è piccolo e di segno variabile: sull'intero periodo il 60/40 euro ribilanciato fa l'8,39% contro l'8,04% in buy & hold, mentre nella coppia americana in dollari il buy & hold rende di più (9,24% contro 8,72%) perché lascia correre l'S&P. Ricordo che il ribilanciamento qui è gratuito: nella realtà vendere le azioni salite genera plusvalenze tassate al 26%, quindi il vantaggio va ridimensionato, soprattutto in un conto amministrato. Ribilanciare con i nuovi versamenti invece che vendendo riduce di molto questo costo. Vero è che ultimamente stanno uscendo ETF 60/40 in cui ribilanciamento lo fanno loro e tu non paghi nulla.

## Che obbligazioni usare: il caso dei Treasury in dollari

La coppia americana in dollari è quella che funziona peggio come diversificazione: rende più dell'S&P puro solo nel 20% dei decenni e ha uno Sharpe migliore solo nel 66%. Il motivo non sono i Treasury in sé, ma il cambio.

![Correlazione mobile a 36 mesi fra gamba azionaria e obbligazionaria](/charts/portafoglio-60-40-ancora-valido/06_correlazione.png)

Per un investitore americano i Treasury sono il rifugio per eccellenza. Per un europeo che li compra in dollari, azioni e obbligazioni americane condividono lo stesso rischio, il cambio euro-dollaro, che si muove spesso più dei titoli stessi. Il risultato è una correlazione fra le due gambe di 0,34 sull'intero periodo, più del doppio di quella fra MSCI World e titoli di Stato europei (0,15).

Con la copertura del cambio la correlazione scende a 0,01, e tra il 2001 e il 2010 diventa nettamente negativa (−0,50): esattamente il comportamento che ci si aspetta da un'obbligazione in un portafoglio. Il 60/40 coperto ha uno Sharpe migliore dell'S&P nel 96% delle finestre di 20 anni contro il 71% della versione in dollari, e la sua perdita massima sull'intero periodo scende da −39,3% a −32,0%.

La conclusione pratica è semplice: **per un italiano le obbligazioni giuste sono in euro, oppure in valuta estera ma coperte dal cambio**. Fra titoli dell'area euro e BTP la differenza è piccola: dal 1980 il 60/40 con i BTP ha reso il 9,98% contro il 9,71% di quello con i titoli dell'area euro, con lo stesso Sharpe (0,66). I BTP però concentrano il rischio su un solo emittente, e nel 2022 hanno perso il 19,3% contro il 17,9% dei titoli dell'area euro.

## Perché allora sembra che il 60/40 sia morto

Tutto quanto sopra non spiega l'impressione comune, che è reale. Dipende da dove si guarda:

![Rendimento annuo e indice di Sharpe fino a fine 2025 al variare dell'anno di partenza](/charts/portafoglio-60-40-ancora-valido/05_anno_di_partenza.png)

| Partenza, fino a fine 2025 | 100% World | 60/40 euro | 80/20 euro | Sharpe World | Sharpe 60/40 |
|---|---|---|---|---|---|
| 1971 | 8,49% | 8,39% | 8,52% | 0,36 | 0,48 |
| 1980 | 10,58% | 9,71% | 10,23% | 0,52 | 0,66 |
| 1990 | 7,72% | 7,36% | 7,63% | 0,39 | 0,52 |
| 2000 | 5,71% | 5,30% | 5,60% | 0,35 | 0,45 |
| 2010 | 12,11% | 8,34% | 10,25% | 0,93 | 0,95 |

Chi ha iniziato a investire dopo il 2010 ha visto il 100% azionario rendere quasi quattro punti l'anno più del 60/40. Si tratta chiaramente di differenza enorme, soprattutto composta, nessun'altra partenza del campione la produce. Tuttavia, lo Sharpe di quei quindici anni è praticamente identico: il 60/40 non ha funzionato peggio, ha preso meno rischio in un periodo in cui il rischio è stato pagato molto bene. Nei quindici anni migliori della storia recente dell'azionario, chi teneva obbligazioni ha "perso" rendimento esattamente come previsto dalla teoria.

Il 2022 è l'altra metà dell'impressione. Quell'anno il 60/40 euro ha perso il 15,0%, più del 100% World (−13,1%), perché i titoli di Stato dell'area euro hanno perso il 17,9% nel pieno del rialzo dei tassi. La protezione non è garantita: la correlazione fra azioni e obbligazioni non è una costante e il grafico precedente lo mostra bene. Negli anni '70, '80 e '90, con l'inflazione alta, è stata quasi sempre positiva (0,24, 0,18 e 0,34 per decennio nella coppia euro). Nei due decenni successivi è stata negativa o nulla. Oggi, sugli ultimi tre anni, è risalita a 0,28.

Questo il punto vero del 60/40, da tenere a mente guardando avanti. Il 60/40 ha funzionato su 55 anni che contengono **sia** i periodi di correlazione positiva **sia** quelli di correlazione negativa: il risultato dell'intero campione non dipende dal regime favorevole degli anni 2000. Ma nei regimi di inflazione alta le obbligazioni proteggono meno, e il vantaggio del 60/40 si riduce alla sola minore volatilità.

## I limiti di questo studio

- **Rendimenti lordi.** Niente costi annui degli ETF (per l'ETF sui BTP citato sono lo 0,17%), niente imposte, niente costi del ribilanciamento. Le obbligazioni hanno un vantaggio fiscale da non trascurare (i titoli di Stato italiani ed esteri "white list" sono tassati al 12,5%), che qui non è considerato.
- **L'euro prima del 1999 è sintetico.** Sia l'MSCI World in euro sia il rendimento dei titoli dell'area euro dell'OCSE usano un paniere di valute nazionali. Il confronto è coerente perché tutte le gambe sono nella stessa unità, ma nessun italiano possedeva euro nel 1975.
- **Le obbligazioni sono indici ricostruiti**, non ETF reali: misurano bene l'effetto dei tassi ma non tracking difference e spread di negoziazione.
- **Il periodo contiene il grande rialzo obbligazionario 1981-2020**, quando i rendimenti sono scesi dai massimi storici a zero. È un evento irripetibile nella stessa forma. Partire dal 1971 include però anche gli anni '70, il periodo peggiore della storia per le obbligazioni, e il risultato sull'intero campione non cambia di segno al variare della partenza.
- **Il passato non garantisce nulla**: le finestre mobili si sovrappongono e i 55 anni contengono solo cinque decenni indipendenti.

## Cosa resta

- **Il 60/40 non è morto.** Su 55 anni di dati in euro ha reso quasi come il 100% azionario con metà della perdita massima, e il suo rendimento corretto per il rischio è stato migliore in nove decenni su dieci e in tutti i ventenni.
- **Il suo vero lavoro è eliminare gli scenari peggiori**, non battere le azioni: nessun decennio in perdita contro il 7% del 100% World, e il 5% peggiore dei decenni sopra il 2% annuo invece che sotto lo zero.
- **L'80/20 è un compromesso onesto** per chi accetta discese fino al 40%: tiene più rendimento, ma la protezione nei crolli è molto inferiore a quella del 60/40.
- **Ribilanciare una volta l'anno** è la scelta che più cambia la profondità delle perdite, meglio se lo si fa con i nuovi versamenti invece che vendendo.
- **Per un italiano le obbligazioni giuste sono in euro**, oppure coperte dal cambio. I Treasury in dollari, abbinati all'azionario americano, diversificano molto meno di quanto ci si aspetti.
- **Il rischio vero da monitorare è la correlazione**: nei periodi di inflazione alta azioni e obbligazioni tendono a muoversi insieme, come nel 2022, e il 60/40 protegge meno.

## Fonti e metodo

- MSCI World total return in euro e in dollari, mensile dal 1969: [MSCI](https://www.msci.com/end-of-day-data-search).
- S&P 500 Total Return (^SP500TR) dal 1988 e prezzo ^GSPC prima, con dividendi da [Robert Shiller](http://www.econ.yale.edu/~shiller/data.htm).
- Rendimenti dei titoli di Stato: Treasury USA a 7 e 10 anni ([FRED, DGS7 e DGS10](https://fred.stlouisfed.org/series/DGS10)), rendimento a lungo termine dell'area euro e dell'Italia ([OCSE via FRED](https://fred.stlouisfed.org/series/IRLTLT01EZM156N), FMI prima del 1991 per l'Italia). Costruzione degli indici a duration costante nell'[articolo dedicato](/posts/quanto-rendono-etf-obbligazionari).
- Tassi a 3 mesi: [Germania](https://fred.stlouisfed.org/series/IR3TIB01DEM156N) e [Stati Uniti](https://fred.stlouisfed.org/series/IR3TIB01USM156N) (OCSE via FRED). Cambio lira-dollaro: [FRED, EXITUS](https://fred.stlouisfed.org/series/EXITUS).
- ETF citati come esempio: [Amundi Italy BTP Government Bond 10Y](https://www.justetf.com/it/etf-profile.html?isin=LU1598691217) e iShares Euro Government Bond 7-10yr.
- Codice riproducibile: `scripts/portafoglio-60-40-ancora-valido.py`. Tabelle complete delle finestre mobili e rendimenti mensili in `public/charts/portafoglio-60-40-ancora-valido/`.
