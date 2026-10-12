---
title: "Quanto rendono gli ETF obbligazionari? 64 anni di finestre mobili"
description: "Gli ETF obbligazionari esistono da vent'anni, troppo pochi per giudicarli. Li ho ricostruiti dal 1962 con i rendimenti dei titoli di Stato: su finestre di 15 e 20 anni non c'è una sola finestra in perdita."
pubDate: 2026-10-20
tags: ["etf-obbligazionari", "obbligazioni", "duration", "treasury", "btp", "finestre-mobili", "tassi", "reddito-fisso"]
author: "SmartMoneyLab"
category: "approfondimenti"
simulationSlug: "quanto-rendono-etf-obbligazionari"
seoImage: "/charts/quanto-rendono-etf-obbligazionari/02_ventagli.png"
draft: false
faq:
  - q: "Quanto rendono storicamente gli ETF obbligazionari?"
    a: |-
      Dipende dall'orizzonte molto più che dalla gamba. Ricostruendo quattro ETF a duration costante su 46-64 anni di dati, la mediana delle finestre di vent'anni va dal 7,9% annuo dei Treasury 7-10 al 10,4% dei titoli di Stato italiani a lunga scadenza. Su finestre di cinque anni le mediane sono simili ma fra il 6% e il 13% delle finestre chiude in perdita.
  - q: "Un ETF obbligazionario può andare in perdita?"
    a: |-
      Sì, e sulle scadenze lunghe anche parecchio: nel 2022 l'indice che replica i Treasury oltre i vent'anni ha perso il 29,3% e quello sui titoli italiani a lunga scadenza il 38,0%. Ma su finestre di quindici e venti anni, su tutta la storia disponibile dal 1962, non esiste una sola finestra chiusa in perdita su nessuna delle quattro gambe studiate.
  - q: "Perché si dice che gli ETF obbligazionari non funzionano?"
    a: |-
      Perché l'opinione corrente si è formata sul peggior tratto della storia disponibile. Le finestre decennali peggiori di tutte e quattro le gambe cominciano fra il gennaio 2015 e il luglio 2021: chi ha comprato in quegli anni ha vissuto il caso peggiore di sessant'anni, e lo sta raccontando come se fosse la norma.
  - q: "Come si può sapere quanto renderà un ETF obbligazionario?"
    a: |-
      Guardando il rendimento a scadenza del portafoglio nel giorno in cui compri. Su tutte le finestre storiche quel numero spiega fra il 74% e il 90% del rendimento ottenuto nei dieci anni successivi, con una relazione quasi uno a uno. Ai livelli di oggi la stima è intorno al 5,9% annuo per i Treasury 7-10, al 3,4% per i governativi euro e al 5,2% per i titoli italiani lunghi.
  - q: "Gli ETF obbligazionari battono l'inflazione?"
    a: |-
      Sull'Italia dal 1980, al netto dell'inflazione, la mediana delle finestre ventennali dell'indice a lunga scadenza è del 7,7% annuo reale e nessuna finestra di quindici o vent'anni ha perso potere d'acquisto. Su cinque anni invece il 12,4% delle finestre lo ha perso: l'orizzonte conta più dello strumento.
  - q: "Perché un ETF obbligazionario può scendere sotto il prezzo di acquisto?"
    a: |-
      Perché non ha una scadenza: vende i titoli che invecchiano e ne compra di nuovi per tenere la duration costante, quindi resta esposto ai tassi per sempre e il suo prezzo non converge mai a un valore di rimborso. È una differenza sostanziale rispetto a un'obbligazione tenuta a scadenza, trattata in un altro studio di questo sito.
---

## In breve

Gli ETF obbligazionari a duration costante sono fra i prodotti più discussi e meno amati dal risparmiatore italiano, per una ragione comprensibile: si comportano come obbligazioni ma non scadono mai, quindi il loro prezzo può restare sotto quello di acquisto a tempo indeterminato. Peccato imperdonabile, per uno strumento che tutti chiamano prudente.

Il problema di giudicarli è che esistono da troppo poco. Il più vecchio dei quattro che ho preso come riferimento parte dal 2002, gli europei dal 2008 e dal 2009. Vent'anni scarsi, e per giunta vent'anni molto particolari.

Li ho quindi **ricostruiti dall'origine dei dati sui rendimenti dei titoli di Stato**, ottenendo fra i 46 e i 64 anni di storia, e verificando che gli indici sintetici replichino gli ETF veri nel periodo in cui coesistono.

Tre risultati:

1. **Su finestre di quindici e vent'anni non esiste una sola finestra chiusa in perdita.** Su nessuna delle quattro gambe, su tutta la storia disponibile. La peggiore in assoluto è un +1,73% annuo.
2. **Le finestre peggiori cominciano tutte fra il 2015 e il 2021.** Chi oggi racconta che gli ETF obbligazionari non funzionano sta generalizzando dal peggior tratto di sessant'anni.
3. **Il rendimento a scadenza del giorno in cui compri predice quello che otterrai**, con un R² fra 0,74 e 0,90 sui dieci anni successivi. Ai livelli attuali vuol dire circa 5,9% annuo sui Treasury 7-10, 3,4% sui governativi euro, 5,2% sui titoli italiani lunghi.

## Il problema di partenza

Un ETF obbligazionario a duration costante non è un'obbligazione. Ogni mese vende i titoli che si sono accorciati e ne compra di nuovi, per mantenere ferma la scadenza media del portafoglio. Il risultato è che **non scade mai**, quindi non esiste nessuna data alla quale il prezzo torna per forza al valore di rimborso. Se i tassi salgono dopo che hai comprato, perdi, e nessun meccanismo ti garantisce di recuperare entro una data certa. Questa è la ragione vera del sospetto, ed è fondata.

Il confronto diretto fra questi strumenti e le obbligazioni tenute a scadenza l'ho già fatto in uno [studio dedicato](/posts/etf-obbligazionari-o-obbligazioni). Qui la domanda è un'altra e più semplice: **quanto hanno reso, storicamente, su orizzonti lunghi?**

La risposta non si può dare con i dati degli ETF veri, perché la loro storia è corta e coincide quasi per intero con due fasi estreme e opposte: il lungo calo dei tassi fino al 2020 e la risalita violenta del 2022. Qualunque statistica su quei vent'anni dice più del periodo che dello strumento.

## Come ho ricostruito quarantasei-sessantaquattro anni

Un indice a duration costante si ricostruisce esattamente come lavora: ogni mese si compra un titolo alla pari con scadenza M anni, cedola pari al rendimento di mercato del momento. Un mese dopo lo si rivaluta al nuovo rendimento, con scadenza residua di un dodicesimo di anno in meno, e poi lo si rinnova a M. La duration resta ferma, il rendimento mensile è quello che risulta.

Quattro "finti ETF", scelte per corrispondere ad altrettanti ETF che un investitore europeo può comprare davvero, oggi:

| ETF sintetico | ETF di riferimento | dal | anni |
|---|---|---|---|
| Treasury USA 7-10 anni | IEF, SXRM | luglio 1969 | 57 |
| Treasury USA oltre 20 anni | TLT | gennaio 1962 | 64 |
| Governativi area euro 7-10 anni | SXRQ | gennaio 1970 | 56 |
| Titoli di Stato italiani oltre 15 anni | nessuno diretto | gennaio 1980 | 46 |

**La verifica che tiene in piedi tutto il resto** è il confronto con gli ETF veri nel periodo di sovrapposizione. Il sintetico dei Treasury 7-10 rende **0,05 punti l'anno meno di IEF**, con correlazione mensile 0,993. Quello sui Treasury lunghi rende **0,16 punti più di TLT**: ed è il risultato corretto, perché 0,15 punti sono il costo di gestione dichiarato di TLT, che un indice lordo non paga. Il sintetico euro rende **0,01 punti meno di SXRQ**.

Una cosa l'ho imparata per strada e vale la pena dirla, perché è la differenza fra un indice che funziona e uno che sbaglia di mezzo punto l'anno. Un indice vero guadagna anche **scivolando lungo la curva**: un titolo comprato a dieci anni e rivenduto a sette si rivaluta a un rendimento più basso, se la curva è inclinata, e quel guadagno è reale. Senza modellarlo, la gamba americana 7-10 restava indietro di **0,74 punti l'anno** rispetto a IEF. Modellandolo, interpolando fra il rendimento a sette e quello a dieci anni, lo scarto crolla a 0,05.

<figure>
  <img src="/charts/quanto-rendono-etf-obbligazionari/01_curve.png" alt="Quattro curve di crescita in scala logaritmica dal 1962 al 2026: Treasury USA 7-10 a 34 volte il capitale, Treasury USA 20+ a 36 volte, governativi area euro a 46 volte, titoli italiani lunghi a 67 volte. Il tratto italiano anteriore al 1993 è punteggiato." width="2120" height="1280" decoding="async" />
  <figcaption>I quattro indici ricostruiti, ciascuno con base 100 alla propria partenza. Scala logaritmica.</figcaption>
</figure>

## Il risultato principale

Ecco la distribuzione dei rendimenti su **tutte** le finestre mobili disponibili, a passo trimestrale, per quattro orizzonti.

<figure>
  <img src="/charts/quanto-rendono-etf-obbligazionari/02_ventagli.png" alt="Cinque pannelli con la distribuzione dei rendimenti annui composti su finestre di 5, 10, 15 e 20 anni. In tutti i pannelli il ventaglio si stringe con l'orizzonte e la quota di finestre in perdita va a zero a quindici e vent'anni." width="3160" height="1120" decoding="async" />
  <figcaption>Per ogni gamba e ogni orizzonte: banda chiara dal 5° al 95° percentile, banda scura dal 25° al 75°, linea la mediana. Sotto, in rosso, la quota di finestre chiuse in perdita.</figcaption>
</figure>

Il numero che conta è quello scritto in basso in ciascun pannello. **A quindici e a vent'anni è zero ovunque.** Non una finestra negativa su nessuna gamba, su tutta la storia disponibile, comprese le due crisi dei tassi.

| peggior finestra | 5 anni | 10 anni | 15 anni | 20 anni |
|---|---|---|---|---|
| Treasury USA 7-10 | −2,65% | +0,43% | +1,89% | **+3,09%** |
| Treasury USA 20+ | −9,92% | −2,79% | +0,32% | **+1,73%** |
| Governativi euro 7-10 | −2,88% | −0,36% | +2,03% | **+2,51%** |
| Italia oltre 15 anni | −6,71% | −1,92% | +2,61% | **+2,73%** |

E le mediane, che sono il caso tipico:

| mediana | 5 anni | 10 anni | 15 anni | 20 anni |
|---|---|---|---|---|
| Treasury USA 7-10 | 6,61% | 6,95% | 7,61% | 7,87% |
| Treasury USA 20+ | 6,42% | 7,42% | 8,03% | 8,20% |
| Governativi euro 7-10 | 7,06% | 7,67% | 9,47% | 8,36% |
| Italia oltre 15 anni | 9,04% | 8,83% | 9,14% | 10,39% |

A cinque anni il rischio è invece concreto e va detto: fra il 5,7% e il 12,9% delle finestre chiude in perdita a seconda della gamba, e sulle duration lunghe la perdita può arrivare a quasi dieci punti l'anno per cinque anni di fila.

## Perché tutti dicono il contrario

Questa è la parte che spiega lo scarto fra i dati e l'opinione corrente.

<figure>
  <img src="/charts/quanto-rendono-etf-obbligazionari/03_peggiori.png" alt="Quattro linee che mostrano il rendimento dei dieci anni successivi a ciascun mese di acquisto, dal 1962 al 2016. Tutte le curve crollano sotto zero all'estremità destra, e i punti rossi che segnano i minimi cadono fra il 2015 e il 2016." width="2160" height="1240" decoding="async" />
  <figcaption>Il rendimento dei dieci anni successivi, in funzione del mese di acquisto. I punti rossi sono i minimi di ciascuna serie.</figcaption>
</figure>

I minimi delle quattro serie cadono nel **gennaio 2015, luglio 2016, aprile 2015 e luglio 2016**. Allargando agli altri orizzonti, le finestre peggiori a cinque anni partono dal **luglio 2020, gennaio 2021 e luglio 2021**.

Tutte le peggiori finestre di sessant'anni di storia cominciano negli ultimi dieci. Non è un caso e non è un mistero: chi ha comprato obbligazioni fra il 2015 e il 2021 ha comprato ai rendimenti più bassi mai registrati, in alcuni casi negativi, e si è poi preso la risalita dei tassi più rapida da quarant'anni.

Il punto non è che quelle persone abbiano torto sui fatti. **È che stanno descrivendo il caso peggiore di sessant'anni e lo stanno raccontando come se fosse la norma dello strumento.** È esattamente l'errore di guardare una finestra sola, con l'aggravante che quella finestra è l'estremo negativo della distribuzione.

## Il 2022, senza addolcirlo

Per non raccontarla meglio di com'è. Nel solo 2022 i quattro indici hanno perso il **14,6%**, il **29,3%**, il **17,9%** e il **38,0%**. Misurando dal massimo del 2020 al minimo dell'ottobre 2023 le perdite arrivano al **22,4%**, al **47,4%**, al **22,4%** e al **45,4%**.

E non è finita: oggi l'indice sui Treasury oltre i vent'anni è ancora **40,3% sotto il suo massimo**, quello sui titoli italiani lunghi il 32,1% sotto. Chi ha comprato nel 2020 è ancora lì ad aspettare, e nessuna statistica di lungo periodo gli toglie quel fatto.

La tesi di questo studio non è che il crollo non sia successo. È che **le finestre lunghe che lo contengono restano comunque positive**, perché dentro una finestra di vent'anni c'è anche il rendimento incassato per i restanti quindici.

## Quanto renderanno da qui: la cosa più utile dei dati

C'è una proprietà delle obbligazioni che le azioni non hanno: **il rendimento futuro è in buona parte scritto nel prezzo di oggi**. Lo si può verificare.

<figure>
  <img src="/charts/quanto-rendono-etf-obbligazionari/04_predittivita.png" alt="Quattro grafici a dispersione che mettono il rendimento a scadenza all'acquisto contro il rendimento annuo ottenuto nei dieci anni successivi. I punti si dispongono lungo la bisettrice con R² fra 0,74 e 0,90, e un rombo rosso segna il livello di oggi e la stima." width="2640" height="919" decoding="async" />
  <figcaption>Ogni punto è un mese di acquisto. In rosso la retta stimata, tratteggiata la bisettrice, il rombo è il livello di oggi con la stima che ne deriva.</figcaption>
</figure>

Il rendimento a scadenza del portafoglio nel giorno dell'acquisto spiega l'**86%** della variabilità del risultato a dieci anni sui Treasury 7-10, il **90%** sui governativi euro, l'**83%** sui titoli italiani lunghi e il **74%** sui Treasury oltre i vent'anni. La pendenza è vicina a uno: il rendimento ottenuto finisce dove stava quello di partenza, più qualche decimo.

Applicato ai livelli attuali:

| gamba | rendimento oggi | stima a 10 anni |
|---|---|---|
| Treasury USA 7-10 | 5,24% | **5,9% annuo** |
| Treasury USA 20+ | 5,28% | **5,1% annuo** |
| Governativi euro 7-10 | 3,22% | **3,4% annuo** |
| Italia oltre 15 anni | 3,99% | **5,2% annuo** |

Due avvertenze. La prima è che questa è una **relazione statistica su finestre sovrapposte**, non una promessa: il 10-26% di variabilità che resta non spiegato è esattamente la parte che non si può sapere. La seconda è che **sulle duration lunghe la relazione è molto più lasca**: sui Treasury 7-10 il risultato a dieci anni è finito entro due punti dal rendimento iniziale nell'85,5% dei casi, sui Treasury oltre i vent'anni solo nel 49,4%. Più allunghi la duration, meno il prezzo di oggi ti dice cosa otterrai.

## Il caso italiano, al netto dell'inflazione

I numeri italiani nominali di questo studio sono spettacolari e, da soli, fuorvianti. Fra il 1980 e il 2025 l'inflazione italiana ha viaggiato a una media del **4,54% annuo** e i prezzi si sono moltiplicati per **6,40**, con gli anni Ottanta a una media dell'11,22% e un picco del 22,03%. Un 9% nominale in quel contesto è un'altra cosa rispetto a un 9% di oggi.

<figure>
  <img src="/charts/quanto-rendono-etf-obbligazionari/05_reale_italia.png" alt="Grafico a barre che confronta, per orizzonti di 5, 10, 15 e 20 anni, la mediana nominale dell'indice italiano a lunga scadenza con quella al netto dell'inflazione: 9,3 contro 6,0 a cinque anni, 10,9 contro 7,7 a venti." width="2039" height="1160" decoding="async" />
  <figcaption>Indice italiano oltre i 15 anni, dal 1980: mediana nominale e mediana al netto dell'inflazione, con la quota di finestre che hanno perso potere d'acquisto.</figcaption>
</figure>

Anche deflazionate, le mediane restano alte: **5,97% reale a cinque anni, 6,89% a dieci, 6,82% a quindici, 7,73% a venti.** E il risultato strutturale tiene: **nessuna finestra di quindici o vent'anni ha perso potere d'acquisto**, con minimi del +0,77% e +0,76% reale. A cinque anni invece il **12,4%** delle finestre lo ha perso, e a dieci il 4,3%.

Vale la pena fermarsi su cosa significa: su orizzonti brevi un'obbligazione lunga non è uno strumento di protezione del potere d'acquisto, su orizzonti lunghi lo è stato sempre. Sempre.

## Quanto pesa la data di partenza

L'ultimo pannello del grafico dei ventagli è il più importante dal punto di vista metodologico, ed è il motivo per cui l'ho messo.

L'ETF fittizio che replica un portafoglio di titoli di stato italiani a 15+ anni, comprato nel 1980, ha un rendimento composto del **9,46% annuo**. Comprato nel novembre 1993 ne ha **6,15%**. Le mediane a dieci anni passano dall'8,83% al 6,44%, e la quota di finestre quinquennali in perdita dal 12,0% al 17,0%.

Stesso strumento, stesso codice, stessi dati: cambia solo dove comincia la serie. Questa è la ragione per cui questo sito non pubblica mai un backtest a partenza unica, e qui si vede applicata a sé stesso.

**Perché due versioni?** Perché prima del novembre 1993 un ETF sui titoli di Stato italiani a lunga scadenza non avrebbe avuto titoli da comprare. Secondo il Dipartimento del Tesoro, nel 1993 la vita media residua di tutto il debito pubblico italiano era di **3,3 anni** e la duration finanziaria di **1,6 anni**, con il **65% del debito in BOT e CCT**. A quei livelli di inflazione nessuno comprava carta a tasso fisso trentennale, e infatti lo Stato non la emetteva. La versione dal 1993 è quella da prendere sul serio; quella dal 1980 è un esercizio, ed è punteggiata nel grafico delle curve per ricordarlo.

Nemmeno nella versione severa, però, compaiono finestre negative a quindici e vent'anni: i minimi sono **+2,79%** e **+2,87%** annuo.

## I limiti di questo studio

Sono parecchi e li elenco tutti, con la misura di quanto pesano dove sono riuscito a misurarla.

**L'ETF fittizio che replica un portafoglio di titoli di stato italiani a 15+ anni prezza un titolo a vent'anni usando il rendimento a dieci.** Una curva dei rendimenti italiana che arrivi alle scadenze lunghe e abbia quarant'anni di storia non esiste in forma pubblica: la Banca d'Italia pubblica il Rendistato per fasce di vita residua ma solo come PDF annuali dal 2017, e la curva della BCE parte dal 2004. Ho misurato quanto costa l'approssimazione usando proprio quella curva BCE, dove ho sia il nodo a dieci sia quello a venti anni: **0,72 punti l'anno di sottostima**, perché la curva euro fra i due nodi è mediamente inclinata di 0,55 punti. È una sottostima, quindi i numeri veri della gamba italiana sarebbero migliori di quelli pubblicati qui, non peggiori.
Questo paese comunque ha un problema enorme con i dati open source e con i dati in generale. 

**Il roll-down è modellato solo sulla gamba americana 7-10**, l'unica per cui ho due nodi di curva con storia lunga. Le gambe europee e quella americana lunga ne sono prive, e sono quindi prudenti nella stessa direzione. Sull'estremità lunga della curva il roll-down vale poco (misurato: 0,06 punti l'anno sui Treasury oltre i vent'anni), sulle scadenze intermedie parecchio.

**I rendimenti europei e italiani sono medie mensili, non valori di fine mese.** È il formato delle serie OCSE. Misurato sugli Stati Uniti, dove ho entrambi i formati, sposta il rendimento composto di 0,06 punti l'anno e le mediane delle finestre di 0,03: irrilevante su questi orizzonti. Ma disallinea il singolo mese, ed è il motivo per cui la correlazione mensile con SXRQ è 0,60 mentre quella con IEF è 0,993. **Su queste gambe non vanno lette statistiche mensili.**

**Prima del 1999 l'Italia è in lire**, e l'area euro è un aggregato di paesi con valute diverse. Sono rendimenti corretti per chi investiva in quelle valute, non rendimenti in euro.

**Tutto è al lordo di costi e imposte.** Il costo di gestione (TER) si può stimare dallo scarto misurato contro TLT, cioè circa 0,15 punti l'anno per un ETF di quel tipo, e va sottratto. Poi vanno sottratte le ritenute alla fonte le tasse della [fiscalità italiana](/posts/tassazione-etf-italia).

**Le finestre mobili si sovrappongono quasi tutte**, quindi non sono osservazioni indipendenti. Descrivono quello che è successo, e i percentili non sono probabilità future.

**Il confronto fra gambe non è su periodo comune**, perché ciascuna parte quando partono i suoi dati. Le mediane della gamba italiana sono più alte anche perché il suo campione comincia nel 1980, vicino al picco dei tassi.

## Cosa resta

Tre cose, e nessuna delle tre è "gli ETF obbligazionari sono sicuri".

La prima è che **l'orizzonte conta più dello strumento**. Le stesse gambe che su cinque anni perdono nel 6-13% dei casi, su quindici e venti non hanno mai perso in sessant'anni di dati, neanche al netto dell'inflazione nel caso italiano. Chi compra un ETF obbligazionario lungo con tre anni davanti sta facendo una cosa diversa da chi lo compra con venti.

La seconda è che **la duration è la variabile che decide quanto sarà brutto nel mezzo**. Le mediane a vent'anni delle quattro gambe stanno in due punti e mezzo di distanza, le perdite massime del 2022 in più di venti.

La terza è che **oggi il punto di partenza è molto migliore di quello del 2015-2021**, e lo si può leggere nel prezzo invece che indovinarlo. Non è un consiglio di comprare: è la constatazione che l'argomento più ripetuto contro questi strumenti si basa sulla finestra in cui comprarli era peggio.

## Fonti e metodo

- **Rendimenti americani**: Treasury constant maturity di FRED, serie `DGS7` (dal luglio 1969), `DGS10` (dal gennaio 1962), `DGS20` (dal gennaio 1962) e `DGS30` (dal febbraio 1977). Il ventennale non è stato emesso fra il gennaio 1987 e il settembre 1993: il buco è tappato incatenando le variazioni del trentennale, così da non creare gradini artificiali ai due innesti. Nei 515 mesi di sovrapposizione le due serie differiscono in media di 0,002 punti.
- **Rendimenti area euro**: `IRLTLT01EZM156N`, OCSE, rendimento dei titoli di Stato a lungo termine, mensile dal gennaio 1970.
- **Rendimenti italiani**: `INTGSBITM193N` (FMI) dal gennaio 1980 al febbraio 1991, poi `IRLTLT01ITM156N` (OCSE). Nei 422 mesi di sovrapposizione le due serie differiscono al massimo di 0,005 punti.
- **Prezzi al consumo Italia**: `ITACPIALLMINMEI`, OCSE, mensile. La serie si ferma a marzo 2025, quindi le finestre reali finiscono lì.
- **ETF di riferimento**: prezzi aggiustati da Yahoo Finance per IEF, TLT, SXRQ e IBGL. SXRM è stato scartato come ancora perché quotato in euro, quindi la sua serie incorpora il cambio e non è confrontabile con un indice in dollari.
- **Costruzione dell'indice**: ogni mese si acquista un titolo alla pari con scadenza M anni e cedola pari al rendimento corrente, lo si rivaluta il mese successivo al nuovo rendimento con scadenza M meno un dodicesimo, e si rinnova. Il prezzo è il valore attuale dei flussi residui con cedole semestrali, quindi il rateo è incluso e non va sommato a parte. Maturity usate: 8,5 anni per le gambe 7-10, 24 anni per i Treasury oltre i venti, 20 anni per l'Italia.
- **Validazione**: scarto di rendimento composto rispetto agli ETF reali nel periodo di sovrapposizione, pari a −0,05 punti su IEF (292 mesi, correlazione 0,993), +0,16 su TLT (correlazione 0,992) e −0,01 su SXRQ.
- **Finestre mobili**: tutte quelle disponibili a 5, 10, 15 e 20 anni, con passo trimestrale, secondo la metodologia di questo sito.
- **Vita media e composizione del debito italiano nel 1993**: Dipartimento del Tesoro, *The Italian Treasury Securities Market: Overview and Recent Developments*.
- Lo script contiene controlli che fanno fallire la generazione se le affermazioni principali cadono: assenza di finestre negative a quindici e vent'anni su tutte le gambe, anche nella versione italiana dal 1993 e anche in termini reali, e R² della relazione fra rendimento iniziale e risultato a dieci anni sopra 0,7.
- Codice e dati: `scripts/quanto-rendono-etf-obbligazionari.py` e `scripts/data/scarica_dati_bond.py`, output in `public/charts/quanto-rendono-etf-obbligazionari/summary.json`.
