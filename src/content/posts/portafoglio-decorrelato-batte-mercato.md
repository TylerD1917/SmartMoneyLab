---
category: "strategie"
title: "Il portafoglio più decorrelato batte il mercato? 27 anni di backtest"
description: "Backtest dal 1999 del portafoglio più decorrelato (oro, Treasury 20+, Nasdaq, financials, energia), equal weight. Su finestre mobili di 10 anni batte l'S&P 500 in 5 metriche su 6 e l'MSCI World in tutte, con metà del drawdown. Verdetto e dati."
pubDate: 2026-09-19
tags: ["portafogli", "decorrelazione", "diversificazione", "risk-parity", "asset-allocation", "backtest", "oro", "treasury", "rolling-windows", "monte-carlo"]
author: "SmartMoneyLab"
simulationSlug: "portafoglio-decorrelato-batte-mercato"
series: "battere-il-mercato"
seriesOrder: 6
verdict: "parziale"
seoImage: "/charts/portafoglio-decorrelato-batte-mercato/04_drawdown.png"
draft: false
faq:
  - q: "Cos'è un portafoglio decorrelato?"
    a: |-
      È un portafoglio che mette insieme asset che tendono a non muoversi nella stessa direzione: quando uno scende, un altro tiene o sale. L'obiettivo non è massimizzare il rendimento, ma ridurre le oscillazioni e le perdite nei periodi difficili. Nel nostro test: oro, Treasury USA a lunga scadenza, Nasdaq, settore finanziario ed energia.
  - q: "Un portafoglio molto diversificato batte l'S&P 500?"
    a: |-
      Nei nostri dati (1999-2026), sulle finestre mobili di 10 anni, il portafoglio batte l'S&P 500 in cinque metriche su sei (volatilità, drawdown, Sharpe, Sortino, Calmar) ma pareggia sul rendimento puro: lo supera solo nel 42% delle finestre. Contro l'MSCI World invece vince su tutte e sei le metriche, sempre. In sintesi: stesso rendimento del mercato con circa metà del rischio.
  - q: "Meglio pesare gli asset in modo uguale o con il risk parity?"
    a: |-
      L'equal weight (20% a testa) è semplice e ha reso di più (10,1% contro 8,8% sul periodo comune). Il risk parity dà più peso agli asset stabili (Treasury e oro) e taglia il drawdown dal -32% al -19%, a costo di poco più di un punto di rendimento l'anno. È una manopola tra rendimento e sicurezza.
  - q: "Quali ETF servono per replicare questo portafoglio?"
    a: |-
      Cinque mattoncini in dollari: oro, un ETF sul Treasury USA 20+ anni, il Nasdaq, il settore finanziario USA e il settore energia USA, tutti replicabili con ETF molto liquidi. È un test storico divulgativo, non una raccomandazione: costi reali e tasse italiane cambiano i numeri.
---

> **Disclaimer.** Contenuto informativo, **non è consulenza finanziaria**. I rendimenti passati non predicono quelli futuri. Le simulazioni usano ipotesi dichiarate e semplificate.

## In breve

Nel nostro [studio sulla correlazione tra asset class](/posts/correlazione-asset-class/) avevamo cercato, con una ricerca su decine di migliaia di combinazioni, il portafoglio storicamente **più decorrelato** — quello i cui pezzi si muovono meno all'unisono. Ne era uscito un quintetto insolito: oro, petrolio, Treasury USA a lunga scadenza, settore finanziario e semiconduttori. Qui lo rendiamo **investibile** (semiconduttori → Nasdaq, petrolio → settore energia), lo pesiamo nel modo più semplice possibile (**pesi uguali, 20% a testa**) e lo testiamo su **27 anni** di dati (dal 1999) per rispondere alla domanda della serie: **batte il mercato?**

1. **Contro l'S&P 500 è un pari sul rendimento, una vittoria sul rischio.** Su finestre mobili di 10 anni il portafoglio rende in mediana l'**8,6%** contro l'**8,2%** dell'indice USA, ma lo supera solo nel **42%** delle finestre: sul rendimento puro è testa o croce. Sulle altre cinque metriche però vince quasi sempre.

2. **Contro l'MSCI World vince su tutta la linea.** In ogni singola finestra a 10 anni batte l'indice mondiale su **tutte e sei le metriche**: rendimento, volatilità, drawdown, Sharpe, Sortino e Calmar.

3. **Il vantaggio vero è il rischio.** Volatilità e drawdown sono più bassi nel **100%** delle finestre: la volatilità mediana è dell'**11%** contro il 15% degli indici, e il peggior crollo è stato del **-32%** contro il **-51%** dell'S&P 500 e il **-54%** del World. Nel 2008 e nel 2000-2002, mentre le borse si dimezzavano, questo portafoglio perdeva un terzo.

4. **Il verdetto è parziale, ma a taglio positivo.** Non è una macchina per battere l'S&P 500 sul rendimento — su quello è alla pari. È una macchina per ottenere **lo stesso rendimento del mercato correndo molto meno rischio**, e per battere nettamente il mercato mondiale. Chi vuole spingere ancora sulla sicurezza può usare il *risk parity*, che vediamo alla fine.

## Da dove nasce l'idea

Nell'articolo sulle [correlazioni tra asset class](/posts/correlazione-asset-class/) avevamo passato al setaccio 31 asset alla ricerca della combinazione di cinque che, storicamente, oscillavano meno insieme. Ne era uscito un quintetto controintuitivo: **oro, petrolio, Treasury 20+, financials e semiconduttori**. Controintuitivo perché mette due settori azionari molto ciclici (banche e chip) accanto a tre rifugi/materie che con le azioni c'entrano poco: l'idea è che, se i pezzi zigzagano in momenti diversi, l'insieme oscilla meno di ognuno di loro. Puoi vedere quanto ogni coppia di asset si muove insieme nel nostro strumento interattivo, la [mappa delle correlazioni](/strumenti/mappa-correlazioni).

Restava un problema pratico: quel portafoglio era **teorico**. Il petrolio "puro" (il future) non si compra e si tiene — si paga il costo di rinnovo dei contratti — e i semiconduttori come classe a sé sono un'esposizione molto specifica. Così lo rendiamo concreto con due sostituzioni ragionevoli:

- **Semiconduttori → Nasdaq**, per mantenere l'anima tech/crescita con uno strumento che chiunque possiede.
- **Petrolio → settore energia** (S&P 500 Energy): azionario, liquido, investibile con un normale ETF e legato positivamente al prezzo dell'energia.

Le altre tre gambe restano quelle dello studio: **oro, Treasury USA 20+ anni e settore finanziario**.

## Parte 1 — Il portafoglio: cosa c'è dentro

Cinque mattoncini, tutti in *Total Return* (dividendi e cedole reinvestiti) e in dollari:

- **Oro** — bene rifugio, storicamente poco correlato alle azioni.
- **Treasury USA 20+** — titoli di Stato americani a lunga scadenza: la gamba difensiva classica, quella che sale quando le borse crollano per fuga verso la sicurezza.
- **Financials** — settore finanziario USA (banche e assicurazioni), molto ciclico.
- **Nasdaq** — azionario tech/crescita: alto rendimento e alta volatilità.
- **Energia** — settore energia dell'S&P 500, legato al prezzo di petrolio e gas.

**Come è distribuito.** Geograficamente è **quasi tutto USA** (azioni e Treasury americani; oro ed energia sono globali per natura). A livello settoriale è volutamente **sbilanciato verso i ciclici** (finanza, tech, energia) e bilanciato dai due rifugi (oro e Treasury). Non è un portafoglio "geografico" come un MSCI World: è costruito **per comportamento**, perché i pezzi reagiscano in modo diverso agli stessi shock.

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/07_correlazioni.png" alt="Matrice di correlazione dei cinque asset (oro, Treasury 20+, financials, Nasdaq, energia) sui rendimenti mensili: oro e Treasury poco o negativamente correlati alle azioni." />
  <figcaption>La logica del portafoglio in una figura: Treasury e oro hanno correlazione bassa o negativa con le gambe azionarie. Sono loro a fare da ammortizzatore.</figcaption>
</figure>

**Hanno abbastanza storia?** Sì, e stavolta parecchia. Per andare più indietro possibile abbiamo usato le **serie storiche lunghe** invece dei soli ETF recenti: l'oro dai prezzi mensili dal 1985 (l'oro non paga cedole, quindi il prezzo è già total return); il **Nasdaq** dall'indice Composite, con un dividendo figurato dello 0,75% l'anno per trasformarlo in total return; il **Treasury 20+** ricostruito in total return a maturità costante dai rendimenti ufficiali (FRED, serie DGS20). Il settore finanziario ed energia arrivano dagli ETF settoriali in total return dal 1998. Il vincolo più corto è proprio quello — **Financials ed Energia, fine 1998** — quindi il backtest parte dal **1999** e copre **27 anni**: dot-com (2000-2002), Grande Crisi Finanziaria (2008), COVID (2020) e lo shock tassi (2022). Un avvertimento onesto: partire dal 1999 significa partire vicino al **picco della bolla dot-com**, una condizione che favorisce i portafogli diversificati rispetto all'S&P 500. È esattamente per questo che il verdetto lo diamo sulle **finestre mobili**, non su un unico punto di partenza.

**I pesi: teniamoli semplici.** Lo schema principale è il più trasparente che esista: **20% a ciascun asset**, ribilanciato una volta l'anno per riportare i pesi al target. Nessuna ottimizzazione, nessun parametro da stimare. È anche il modo più onesto di isolare l'effetto della *decorrelazione* da quello di una particolare ricetta di pesi. (Per chi vuole spingere sulla riduzione del rischio, in fondo c'è la variante *risk parity*.)

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/01_pesi.png" alt="Pesi del portafoglio: equal weight (20% a ciascun asset) confrontato con il risk parity, che dà più peso a Treasury e oro." />
  <figcaption>Lo schema principale è l'equal weight (20% a testa). In blu, per confronto, i pesi risk parity di cui parliamo alla fine.</figcaption>
</figure>

## Parte 2 — Il backtest: quanto rende e quanto fa male

Confrontiamo il portafoglio (equal weight, ribilanciato ogni anno) con due benchmark passivi, **S&P 500** e **MSCI World**, entrambi *Total Return* in dollari, al lordo di tasse e costi. La regola metodologica del blog è che **il verdetto si dà sulle finestre mobili, non sul dato di un singolo periodo**: un unico punto di partenza può ribaltare qualunque conclusione, quindi usiamo tutte le finestre di 5, 10 e 20 anni con passo di 3 mesi.

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/02_equity_curve.png" alt="Crescita di 1 dollaro dal 1999 in scala logaritmica: il portafoglio decorrelato finisce sopra S&P 500 e MSCI World, con una curva molto più regolare." />
  <figcaption>Crescita di 1$ dal 1999. Sul periodo intero il portafoglio (verde) arriva più in alto di entrambi gli indici — ma è un effetto del punto di partenza (vicino al 2000): la vera prova sono le finestre mobili.</figcaption>
</figure>

La curva racconta il rendimento. L'altra metà della storia — quella che conta quando i mercati vanno male — è nel grafico dei drawdown:

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/04_drawdown.png" alt="Perdite dai massimi dal 1999: nel 2000-2002 e nel 2008 S&P 500 e MSCI World scendono oltre il -50%, il portafoglio decorrelato si ferma intorno al -32%." />
  <figcaption>Il cuore della tesi. Nei due grandi crolli (2000-2002 e 2008) le borse hanno perso oltre la metà; il portafoglio decorrelato si è fermato a un terzo. La linea verde resta sempre molto più vicina allo zero.</figcaption>
</figure>

Ecco il quadro con il nostro framework a **6+1 metriche**, calcolato — come da regola — sulle **finestre mobili di 10 anni** (71 finestre): per ogni metrica riportiamo la mediana e la percentuale di finestre in cui il portafoglio batte il benchmark (la "+1").

| Metrica (mediana, finestre 10 anni) | Portafoglio | S&P 500 | MSCI World | Batte S&P | Batte World |
|---|---|---|---|---|---|
| CAGR | 8,6% | 8,2% | 7,4% | 42% | 56% |
| Volatilità | **11,3%** | 15,0% | 16,0% | 100% | 100% |
| Max drawdown | **-30,8%** | -46,3% | -50,0% | 100% | 100% |
| Sharpe | **0,83** | 0,61 | 0,53 | 61% | 100% |
| Sortino | **1,05** | 0,76 | 0,63 | 55% | 100% |
| Calmar | **0,34** | 0,16 | 0,14 | 80% | 100% |

Come si legge: sul **rendimento puro** il portafoglio è alla pari con l'S&P 500 (mediana appena più alta, ma vince solo il 42% delle finestre — l'indice USA ha code migliori nei mercati bull). Ma su **volatilità e drawdown vince nel 100% delle finestre**, e sulle tre metriche di rischio/rendimento (Sharpe, Sortino, Calmar) batte l'S&P nella maggioranza dei casi. Contro l'**MSCI World** non c'è partita: vince tutte e sei le metriche in tutte le finestre.

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/03_rolling10y.png" alt="Boxplot del rendimento annualizzato su finestre mobili di 10 anni: il portafoglio ha una distribuzione più stretta e sempre positiva." />
  <figcaption>Su finestre di 10 anni il portafoglio ha reso in mediana l'8,6%, con una distribuzione stretta e mai negativa: più prevedibile degli indici.</figcaption>
</figure>

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/05_risk_return.png" alt="Grafico rischio-rendimento: il portafoglio equal weight sta molto a sinistra (bassa volatilità) con rendimento sopra gli indici; i singoli asset sono sparsi." />
  <figcaption>Nel piano rischio/rendimento il portafoglio (verde) sta molto più a sinistra degli indici — più rendimento, a una frazione della volatilità. Nessun singolo asset è così a sinistra: è la decorrelazione a spostarlo lì.</figcaption>
</figure>

## Parte 3 — Monte Carlo: cosa aspettarsi dal futuro

Il backtest guarda al passato — una sola realizzazione della storia. Per stimare la **forbice dei rendimenti futuri** abbiamo eseguito una simulazione **Monte Carlo** con *block bootstrap* a blocchi di 3 mesi (per conservare le sequenze di mercato), 10.000 traiettorie, su orizzonti di 10, 20 e 30 anni.

<figure>
  <img src="/charts/portafoglio-decorrelato-batte-mercato/06_montecarlo.png" alt="Monte Carlo a 20 anni: multiplo del capitale per il portafoglio e per l'S&P 500, con lo scenario sfortunato p5 più alto per il portafoglio." />
  <figcaption>A 20 anni il portafoglio ha una mediana simile all'indice ma una forbice più stretta: lo scenario sfortunato (p5) è più alto, la probabilità di perdita quasi nulla.</figcaption>
</figure>

Su **20 anni**, 1$ investito nel portafoglio diventa in mediana **6,2 volte** tanto (circa **9,6% annuo**), con una probabilità di trovarsi in perdita a 10 anni di appena lo **0,4%**. La distribuzione è più **stretta e sicura** di quella dell'indice: rinunci a un po' di coda fortunata in cambio di molta più prevedibilità.

## Approfondimento: e se pesassimo per il rischio?

L'equal weight ha un limite concettuale: dà lo stesso capitale a un Treasury che oscilla il 13% l'anno e a un settore energia che oscilla il 26%. Il rischio finisce dominato dagli asset più nervosi. Il **risk parity** (parità di contributo al rischio) corregge proprio questo: assegna i pesi in modo che **ogni asset contribuisca alla stessa quota di rischio**. In pratica alza il peso dei tranquilli (Treasury al 39%, oro al 20%) e abbassa quello dei volatili (energia al 13%).

Sul periodo comune il risultato è istruttivo:

| Metrica | Equal weight | Risk parity |
|---|---|---|
| CAGR | 10,1% | 8,8% |
| Volatilità | 11,0% | 8,8% |
| Max drawdown | -32,0% | **-18,9%** |
| Sharpe | 0,93 | **1,00** |
| Calmar | 0,32 | **0,46** |

Il risk parity **non aumenta il rendimento, compra sicurezza**: quasi dimezza il drawdown (da -32% a -19%) e migliora il rendimento aggiustato per il rischio, al costo di poco più di un punto di rendimento l'anno. È la stessa strategia vista da un'altra angolazione — la manopola tra rendimento e tranquillità.

## Il verdetto: parziale

La domanda della serie è "batte il mercato?" e la risposta dipende da quale mercato e da quale metrica. Sul **rendimento puro contro l'S&P 500** il portafoglio è **alla pari** — lo batte in poco più di quattro finestre su dieci. Chi cerca il massimo rendimento assoluto, in un'epoca di dominio della borsa americana, non lo troverà qui.

Ma il framework a 6+1 metriche, applicato **finestra per finestra**, dice molto di più: il portafoglio batte l'S&P 500 su **cinque categorie su sei** nella maggioranza dei casi — sempre su volatilità e drawdown, quasi sempre su Sharpe, Sortino e Calmar — e batte l'**MSCI World su tutte e sei, in ogni finestra**. Un portafoglio che nei due grandi crolli perde un terzo invece della metà è un portafoglio con cui è molto più facile *restare investiti* — e restare investiti è metà del gioco.

Da qui il verdetto **parziale, ma a taglio positivo**: non batte l'S&P 500 sul rendimento, lo pareggia; ma lo batte su tutto il resto e supera nettamente il mercato mondiale. È lo stesso messaggio dello studio sulle correlazioni, verificato ora su un portafoglio concreto e su 27 anni: **il rendimento di un indice azionario, con circa metà del rischio.**

## Cosa porto a casa

- **La decorrelazione è una macchina per ridurre il rischio.** Il rendimento è quello di un indice; il regalo è la volatilità e il drawdown dimezzati. Aspettarsi che "il portafoglio più diversificato" surclassi l'S&P 500 sul rendimento in un decennio di bull americano è il modo sbagliato di guardarlo.
- **I pesi uguali funzionano benissimo.** Non serve un'ottimizzazione sofisticata: il 20% a testa ha reso quanto il mercato con molto meno rischio. Il risk parity aggiunge sicurezza, non rendimento.
- **Il verdetto va dato sulle finestre mobili.** Sul periodo intero il portafoglio "stravince", ma è un'illusione del punto di partenza (vicino al 2000). Le finestre mobili raccontano la verità più sobria: pari con l'S&P sul rendimento, meglio su tutto il rischio.
- **Limiti dichiarati:** il portafoglio nasce da una ricerca *a posteriori* sui dati, quindi c'è un naturale bias di selezione; il Treasury e il Nasdaq sono ricostruiti in total return da serie storiche (rendimenti FRED e indice Composite più dividendo figurato). I numeri sono lordi: costi e fiscalità italiana ridurrebbero il risultato.

Presto aggiungeremo questo portafoglio, in versione equal weight, alla classifica live di [Portafogli a confronto](/portafogli/), così potrai vederlo aggiornato ogni settimana accanto ai grandi classici.

## Domande frequenti

**Cos'è un portafoglio decorrelato?** È un portafoglio che mette insieme asset che tendono a non muoversi nella stessa direzione: quando uno scende, un altro tiene o sale. L'obiettivo è ridurre le oscillazioni e le perdite, non massimizzare il rendimento.

**Un portafoglio molto diversificato batte l'S&P 500?** Sulle finestre mobili di 10 anni lo batte in cinque metriche su sei (volatilità, drawdown, Sharpe, Sortino, Calmar) ma pareggia sul rendimento puro (42% delle finestre). Contro l'MSCI World vince su tutte e sei, sempre. In sintesi: rendimento da indice con circa metà del rischio.

**Meglio pesare gli asset in modo uguale o con il risk parity?** L'equal weight è semplice e rende un po' di più; il risk parity dà più peso agli asset stabili e quasi dimezza il drawdown (dal -32% al -19%), a costo di poco più di un punto di rendimento l'anno.

**Quali ETF servono per replicarlo?** Cinque mattoncini in dollari: oro, Treasury USA 20+ anni, Nasdaq, settore finanziario USA e settore energia USA, tutti replicabili con ETF liquidi. È un test storico divulgativo, non una raccomandazione: costi e tasse italiane cambiano i numeri.

**Come sono calcolati i rendimenti?** In dollari, *Total Return* (dividendi e cedole reinvestiti), al lordo di tasse e costi, con ribilanciamento annuale, dal 1999. Serie e codice sono riproducibili.

## Approfondimenti

- Da dove nasce il portafoglio: [La correlazione tra asset class](/posts/correlazione-asset-class/).
- Esplora le correlazioni tra asset: [Mappa delle correlazioni](/strumenti/mappa-correlazioni).
- La classifica live dei portafogli famosi: [Portafogli a confronto](/portafogli/).
