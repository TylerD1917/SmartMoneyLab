---
title: "Esiste un rendimento obbligazionario così alto da battere le azioni?"
description: "Comprare un ETF obbligazionario a rendimento alto protegge di più, ed è aritmetica. Ma su un secolo e mezzo di dati americani la variabile che decide chi vince fra azioni e obbligazioni è un'altra, e oggi segna 40,6."
pubDate: 2026-10-22
tags: ["etf-obbligazionari", "premio-al-rischio", "cape", "shiller", "obbligazioni", "azioni", "duration", "inflazione", "asset-allocation"]
author: "SmartMoneyLab"
category: "approfondimenti"
simulationSlug: "convessita-ytm-premio-azionario"
seoImage: "/charts/convessita-ytm-premio-azionario/05_cape.png"
draft: false
faq:
  - q: "Conviene comprare obbligazioni quando i rendimenti sono alti?"
    a: |-
      In termini nominali sì, e si può calcolare: con un rendimento a scadenza dell'1% bastano 0,11 punti di rialzo dei tassi per azzerare il risultato dell'anno, con un rendimento dell'8% ne servono 1,29. Il cuscinetto cresce più che proporzionalmente perché la cedola sale mentre la duration scende. In termini reali però la protezione svanisce: i cinque decenni peggiori di un secolo e mezzo sono stati comprati tutti fra il 5,8% e il 6,6%, fra l'aprile 1971 e il gennaio 1972, e sono stati distrutti dall'inflazione che seguì.
  - q: "Il rendimento a scadenza predice il rendimento futuro di un ETF obbligazionario?"
    a: |-
      Quello nominale sì, e molto bene: su 1.713 mesi di acquisto dal 1871 la relazione con il rendimento dei dieci anni successivi ha pendenza 1,11 e R² 0,91, e il risultato è finito entro due punti dal rendimento di partenza nel 96% dei casi. Quello reale no: la stessa relazione ha R² 0,22 e il risultato è finito entro due punti solo nel 25% dei casi. La differenza è l'inflazione, che il rendimento di partenza prevede male (R² 0,07).
  - q: "Esiste un livello di rendimento obbligazionario che azzera il premio al rischio delle azioni?"
    a: |-
      Non da solo. Nei dati dal 1881 il rendimento del decennale spiega appena il 6% della variabilità del premio decennale delle azioni, e il suo effetto va nella direzione sbagliata rispetto all'intuizione: nei mesi in cui il decennale rendeva oltre l'8%, le azioni hanno comunque vinto nel 99% dei casi. Nel settembre 1981, col decennale al 15,32%, le azioni hanno reso il 12,65% reale annuo nei dieci anni successivi contro il 10,70% delle obbligazioni.
  - q: "Quando le obbligazioni hanno battuto le azioni?"
    a: |-
      Quando le azioni erano care, non quando le obbligazioni rendevano tanto. Dividendo i 1.593 mesi di acquisto dal 1881 per livello di CAPE, il premio mediano delle azioni resta fra +2,1 e +5,2 punti l'anno in tutti i secchi fino a CAPE 30, e crolla a −4,23 sopra quella soglia, dove le azioni hanno vinto solo nel 9% dei casi. Quei mesi però sono soltanto 57, concentrati in due episodi: il 1929 e il periodo 1997-2002.
  - q: "Che cos'è il modello della Fed e funziona?"
    a: |-
      È il confronto fra l'earnings yield azionario e il rendimento dei titoli di Stato. Misurato dal 1881, il premio decennale delle azioni cresce di 0,75 punti per ogni punto di quello spread, con R² 0,26, e il pareggio cade a uno spread di −3,64 punti. Direzionalmente funziona, numericamente no: la frontiera stimata sulla prima metà del campione e quella stimata sulla seconda distano tre punti di rendimento obbligazionario.
  - q: "Oggi conviene di più l'azionario o l'obbligazionario?"
    a: |-
      Con il decennale americano al 5,29% e il CAPE a 40,57, il modello stimato su tutto il campione dà un premio atteso di +0,59 punti l'anno a favore delle azioni e quello stimato sul dopoguerra di −0,79 a favore delle obbligazioni. Lo scarto tipico dei residui è di oltre tre punti l'anno: la stima centrale è dentro il rumore, e chiunque dia un numero preciso sta vendendo una certezza che i dati non contengono.
---

## In breve

Nei due studi precedenti abbiamo visto che il rendimento a scadenza di un ETF obbligazionario [predice bene il risultato](/posts/quanto-rendono-etf-obbligazionari/) e che per realizzarsi chiede un tempo pari al [doppio della duration](/posts/regola-2x-duration/). Restava una domanda naturale: se comprare a rendimento alto è meglio, quanto è meglio, e c'è un livello così alto da rendere le obbligazioni preferibili alle azioni?

Per rispondere servivano dati che il nostro campione non ha. Gli indici ricostruiti negli studi precedenti partono dal 1962, e il tratto 1962-2020 contiene una sola grande discesa dei tassi: qualunque affermazione su cosa succede dopo un certo livello di rendimento sarebbe stata imparata da un episodio solo. Questo studio usa quindi il dataset di Robert Shiller, che parte dal **gennaio 1871** e contiene anche il 1941-1981, quarant'anni di tassi in salita.

Tre risultati:

1. **Il cuscinetto esiste e si calcola.** Con un rendimento a scadenza dell'1%, bastano 0,11 punti di rialzo dei tassi per azzerare il risultato dell'anno. Con l'8% ne servono 1,29. Alzare il prezzo d'ingresso non migliora quasi per niente lo scenario buono: cancella quello cattivo.
2. **Ma è un cuscinetto nominale.** Il rendimento di partenza spiega il 91% del risultato nominale a dieci anni e solo il 22% di quello reale. I cinque decenni peggiori dal 1871 sono stati comprati tutti fra il 5,8% e il 6,6%.
3. **Non esiste un rendimento obbligazionario che da solo batta le azioni.** Nel settembre 1981, col decennale al 15,32%, le azioni hanno comunque vinto il decennio successivo. L'unica cosa che ha davvero azzerato il premio è stata la valutazione azionaria: con CAPE sopra 30 le obbligazioni hanno vinto nel 91% dei mesi. Oggi il CAPE è 40,57.

## Il cuscinetto: l'aritmetica dà ragione all'intuizione

Partiamo dall'idea di base. Compri un ETF obbligazionario e i tassi salgono: perdi. Ma quanto perdi dipende da due cose, e vanno nella stessa direzione. La prima è la cedola che stai incassando, che compensa parte della perdita. La seconda è meno ovvia: **la duration di un titolo alla pari dipende dal livello dei tassi**. Un decennale comprato all'1% ha duration modificata 9,5, lo stesso titolo comprato all'8% ce l'ha 6,8. Rendimento alto vuol dire più cedola *e* meno sensibilità.

Ecco cosa succede a un indice a duration costante sul decennale quando il rendimento si muove di due punti nell'arco di dodici mesi, a seconda del prezzo a cui sei entrato.

| ingresso | duration | rialzo assorbibile in un anno | se scendono 2pp | fermi | se salgono 2pp |
|---|---|---|---|---|---|
| 1% | 9,49 | 0,11 punti | +21,96% | +1,00% | **−14,82%** |
| 2% | 9,02 | 0,24 punti | +21,95% | +2,01% | −13,21% |
| 3% | 8,58 | 0,37 punti | +22,02% | +3,02% | −11,63% |
| 4% | 8,18 | 0,52 punti | +22,17% | +4,04% | −10,07% |
| 5% | 7,79 | 0,69 punti | +22,38% | +5,06% | −8,54% |
| 6% | 7,44 | 0,87 punti | +22,65% | +6,09% | −7,03% |
| 8% | 6,80 | 1,29 punti | +23,35% | +8,16% | **−4,07%** |
| 10% | 6,23 | 1,77 punti | +24,25% | +10,25% | −1,18% |

<figure>
  <img src="/charts/convessita-ytm-premio-azionario/01_cuscinetto.png" alt="Due pannelli. A sinistra il rendimento dei dodici mesi successivi all'acquisto per tre scenari di tasso (meno due punti, fermi, più due punti) in funzione del rendimento d'ingresso: la linea dello scenario cattivo sale ripida, quella dello scenario buono è quasi piatta. A destra i punti di rialzo assorbibili in un anno, che crescono da 0,11 a 1,77 passando dall'1% al 10%." width="2640" height="1160" decoding="async" />
  <figcaption>Indice a duration costante sul decennale, shock distribuito linearmente sui dodici mesi. Lo scenario favorevole migliora di 2,3 punti passando dall'1% al 10% di rendimento d'ingresso, quello sfavorevole di 13,6.</figcaption>
</figure>

Il punto da portare a casa è nell'ultima colonna. Passando dall'1% al 10% di rendimento d'ingresso, lo scenario favorevole migliora di 2,3 punti e quello sfavorevole di 13,6. **Alzare il prezzo d'ingresso è quasi tutto protezione, quasi niente guadagno aggiuntivo.**

Vale la pena chiarire un equivoco di termini, perché la spiegazione naturale è sbagliata. Questa asimmetria non è la convessità. La convessità, cioè la curvatura della relazione fra prezzo e rendimento, è **massima quando i rendimenti sono bassi**: sul nostro decennale vale 97,6 all'1% e 60,2 all'8%. Quello che crea il cuscinetto è il livello della cedola, aiutato dal calo della duration. Sono due effetti banali che si moltiplicano, non un terzo effetto esotico.

E c'è una regola pratica che il lettore può applicare stasera sulla scheda del suo fondo: **il rialzo dei tassi che azzera un anno di rendimento è circa il rendimento a scadenza diviso la duration.** Al 5% con duration 7,8 fa 0,64 punti, contro i 0,69 del conto esatto.

## Poi però arrivano un secolo e mezzo di dati

Fin qui è aritmetica, e l'aritmetica non sbaglia mai. La domanda vera è un'altra: nella storia, chi ha comprato a rendimento alto si è trovato bene?

Per ogni mese dal gennaio 1871 ho calcolato il rendimento annuo composto dei dieci anni successivi dell'indice obbligazionario, in termini nominali e in termini reali, e l'ho confrontato con il rendimento a scadenza del giorno dell'acquisto. Sono 1.713 mesi di acquisto.

| il rendimento d'ingresso predice... | pendenza | R² | risultato entro 2 punti |
|---|---|---|---|
| il rendimento **nominale** a 10 anni | +1,11 | **0,91** | nel 96% dei casi |
| il rendimento **reale** a 10 anni | +0,73 | **0,22** | nel 25% dei casi |
| l'inflazione dei 10 anni successivi | +0,34 | 0,07 | |

<figure>
  <img src="/charts/convessita-ytm-premio-azionario/02_nominale_reale.png" alt="Due grafici a dispersione affiancati. A sinistra il rendimento nominale a dieci anni contro il rendimento a scadenza all'acquisto: i punti stanno quasi tutti sulla bisettrice, R² 0,91. A destra lo stesso contro il rendimento reale: la nuvola è larga e informe, R² 0,22." width="2640" height="1200" decoding="async" />
  <figcaption>Ogni punto è un mese di acquisto fra il gennaio 1871 e il settembre 2013. A sinistra la promessa viene mantenuta, a destra no.</figcaption>
</figure>

Il pannello di sinistra è una delle relazioni più pulite che si trovino in finanza: il prezzo a cui compri ti dice quasi esattamente quanti dollari incasserai. Il pannello di destra dice che quei dollari **non sai quanto varranno**.

Guardando per livello d'ingresso, in termini reali, la monotonia sparisce:

| ingresso | mesi | p10 | mediana | p90 | finestre in perdita reale |
|---|---|---|---|---|---|
| sotto il 3% | 299 | −3,06% | −0,96% | +0,91% | 62,2% |
| 3-4% | 605 | −0,22% | +1,62% | +6,32% | 13,1% |
| 4-5% | 329 | −1,32% | +2,84% | +7,26% | 32,8% |
| 5-6% | 145 | −1,10% | +4,28% | +8,94% | 20,0% |
| **6-8%** | 179 | **−3,16%** | +3,68% | +5,32% | **35,2%** |
| oltre l'8% | 156 | +4,07% | +6,75% | +9,44% | 1,3% |

Il secchio 6-8%, cioè quello dei rendimenti che un risparmiatore chiamerebbe senz'altro generosi, ha il decimo percentile **peggiore** del secchio 3-4%. Non è un errore di calcolo, è una data: quei 179 mesi di acquisto cominciano nel dicembre 1968, e in più di un terzo dei casi l'inflazione dei dieci anni successivi si è mangiata per intero il rendimento nominale incassato. La mediana dell'inflazione su quelle finestre è del 6,46% all'anno.

## Settembre 1971 contro settembre 1981

Le code lo dicono meglio di qualunque statistica. Questi sono i tre decenni reali peggiori e i tre migliori dal 1871, con il rendimento a cui si era comprato:

| | acquisto | ingresso | nominale ottenuto | inflazione | **reale ottenuto** |
|---|---|---|---|---|---|
| peggiori | set 1971 | 6,14% | +2,64% | +8,61% | **−5,50%** |
| | ott 1971 | 5,93% | +2,65% | +8,61% | −5,49% |
| | gen 1972 | 5,95% | +3,14% | +8,66% | −5,08% |
| migliori | set 1981 | 15,32% | +15,07% | +3,94% | **+10,70%** |
| | ott 1981 | 15,15% | +15,00% | +3,94% | +10,64% |
| | gen 1982 | 14,59% | +14,90% | +3,89% | +10,60% |

<figure>
  <img src="/charts/convessita-ytm-premio-azionario/03_due_coorti.png" alt="Due curve di potere d'acquisto a base 100 nei dieci anni dopo l'acquisto. Chi ha comprato nel settembre 1971 scende fino a circa 57, chi ha comprato nel settembre 1981 sale fino a 276." width="2200" height="1200" decoding="async" />
  <figcaption>Lo stesso strumento, due date di acquisto, entrambe a rendimenti che all'epoca sembravano alti. In dieci anni uno ha perso il 43% del potere d'acquisto, l'altro lo ha quasi triplicato.</figcaption>
</figure>

Chi comprava nel 1971 vedeva un decennale al 6,14% con l'inflazione all'epoca intorno al 4%: sulla carta, due punti di rendimento reale. Quello che non poteva vedere era che l'inflazione dei dieci anni seguenti sarebbe stata dell'8,61%.

**Il cuscinetto protegge dal rialzo dei tassi. Non protegge da ciò che quasi sempre lo provoca.** Questa è la prima conclusione dello studio, e spiega perché la domanda di partenza, "a quale rendimento conviene comprare", sia mal posta se la si pone in termini assoluti.

## Allora cambiamo domanda

Se il problema è che non sappiamo quanto varranno i soldi che incasseremo, confrontiamo le obbligazioni con qualcosa che subisce la stessa inflazione. Il premio al rischio azionario, cioè quanto le azioni rendono in più delle obbligazioni, ha una proprietà comoda: siccome è una differenza fra due rendimenti deflazionati con lo stesso indice dei prezzi, **l'inflazione si semplifica quasi del tutto.** Nei nostri dati il premio calcolato sui rendimenti reali e quello calcolato sui nominali differiscono in media di 0,16 punti.

Su 1.593 mesi di acquisto dal gennaio 1881, confrontando il rendimento reale a dieci anni dell'S&P total return con quello del nostro indice obbligazionario:

- premio **medio +4,57 punti l'anno**, mediano +3,89
- negativo nel **14,9% dei mesi**

### Il modello, spiegato

Il premio non è una costante: dipende dal prezzo a cui compri le due cose. Il modello che ho usato è volutamente il più semplice possibile, e l'ho fissato prima di guardare i risultati:

**premio = a + b × (rendimento del decennale) + c × (earnings yield azionario)**

Dove *earnings yield* è semplicemente 1 diviso il CAPE, cioè gli utili degli ultimi dieci anni corretti per l'inflazione divisi per il prezzo. Uso l'inverso del CAPE e non il CAPE per due motivi: diventa una percentuale confrontabile con il rendimento obbligazionario, e rende il modello lineare in entrambe le variabili. Il [CAPE l'abbiamo già studiato altrove](/posts/cape-internazionale-predice-rendimenti/) come predittore dei rendimenti azionari: qui fa lo stesso mestiere, dal lato delle azioni.

Stimato ai minimi quadrati su tutti i 1.593 mesi:

**premio = 2,62 − 0,74 × ytm + 0,76 × ey**  con R² 0,26

I segni sono quelli attesi. Un punto in più di rendimento obbligazionario toglie 0,74 punti al vantaggio delle azioni; un punto in più di earnings yield, cioè azioni più a buon mercato, ne aggiunge 0,76.

La **frontiera** è il luogo dei punti in cui il premio atteso è zero, cioè dove le due attese si pareggiano. Si ottiene ponendo il premio uguale a zero e risolvendo per il rendimento obbligazionario:

**ytm di pareggio = 3,55 + 1,03 × earnings yield**

In parole: perché le obbligazioni pareggino le azioni, devono rendere circa **3,6 punti più dell'earnings yield azionario**. Con un CAPE di 25, cioè un earnings yield del 4%, servirebbe un decennale al 7,7%. Con un CAPE di 40 come quello di oggi basterebbe il 6,1%.

Chi conosce il **modello della Fed** avrà riconosciuto la struttura: il confronto fra earnings yield e rendimento dei titoli di Stato. L'ho verificato nella sua forma originale, con una sola variabile, lo spread fra i due. Risultato: premio = 2,73 + 0,75 × spread, con **R² 0,26**, identico a quello del modello a due variabili, e pareggio a uno spread di −3,64 punti. Le due variabili separate non aggiungono nulla alla loro differenza: il modello della Fed, misurato su un secolo e mezzo, è tutto qui.

Prima di usarlo, però, va sottoposto al controllo che conta.

## Quale dei due prezzi decide davvero

Un R² di 0,26 significa che tre quarti di quello che è successo sono altro. La domanda allora diventa: dentro quel 26%, quanto viene dalle obbligazioni e quanto dalle azioni? Si risponde facendo girare le due variabili una alla volta.

<figure>
  <img src="/charts/convessita-ytm-premio-azionario/04_chi_ordina.png" alt="Due grafici a dispersione del premio decennale delle azioni. A sinistra contro il rendimento del decennale: nuvola informe, pendenza negativa debole, R² 0,060, e i punti rossi con CAPE sopra 30 sono sparsi fra il 4% e il 7%. A destra contro l'earnings yield azionario: pendenza positiva netta, R² 0,143, e i punti rossi sono tutti raccolti all'estrema sinistra sotto lo zero." width="2680" height="1240" decoding="async" />
  <figcaption>In rosso i mesi di acquisto con CAPE sopra 30. Sul prezzo delle obbligazioni sono sparpagliati, su quello delle azioni stanno tutti nello stesso angolo.</figcaption>
</figure>

| variabile, da sola | pendenza | R² |
|---|---|---|
| rendimento del decennale | −0,53 | **0,060** |
| earnings yield azionario | +0,63 | **0,143** |

La valutazione azionaria spiega più del doppio. E guardando il premio per livello di rendimento obbligazionario si scopre che non c'è nemmeno un ordine:

| rendimento del decennale | mesi | premio mediano | azioni avanti |
|---|---|---|---|
| sotto il 3% | 299 | +12,02 | 100% |
| 3-4% | 594 | +2,95 | 81% |
| 4-5% | 270 | +2,60 | 83% |
| 5-6% | 95 | −0,85 | 44% |
| 6-8% | 179 | +2,97 | 88% |
| oltre l'8% | 156 | +4,50 | **99%** |

Il secchio dei rendimenti altissimi, oltre l'8%, è quello in cui le azioni hanno vinto **quasi sempre**. Il caso limite merita di essere scritto per esteso. **Settembre 1981: il decennale americano rendeva il 15,32%, il massimo di tutta la serie, dal 1871 a oggi.** Nei dieci anni successivi quelle obbligazioni hanno reso il 10,70% reale annuo, un risultato formidabile. Le azioni, comprate lo stesso giorno a un CAPE di 7,6, ne hanno resi il 12,65%.

Il motivo è che i due prezzi si muovono insieme: quando i tassi sono altissimi le azioni costano pochissimo, e il vantaggio relativo resta dalla loro parte. Un rendimento obbligazionario alto, da solo, non è mai stato una ragione sufficiente.

## La soglia che si vede nei dati

Ordinando per valutazione azionaria, invece, un ordine c'è, e c'è anche un punto di rottura.

<figure>
  <img src="/charts/convessita-ytm-premio-azionario/05_cape.png" alt="Grafico a barre del premio mediano delle azioni per secchio di CAPE: +4,97 sotto 10, +5,23 fra 10 e 15, +4,60 fra 15 e 20, +2,91 fra 20 e 25, +2,14 fra 25 e 30, e −4,23 sopra 30, unica barra rossa. Sotto ogni barra la quota di casi in cui le azioni hanno vinto, dal 97% al 9%." width="2280" height="1280" decoding="async" />
  <figcaption>Premio mediano delle azioni sulle obbligazioni nei dieci anni successivi all'acquisto, per livello di CAPE di partenza. Il gradino è uno solo.</figcaption>
</figure>

| CAPE all'acquisto | mesi | premio mediano | azioni avanti | acquisti |
|---|---|---|---|---|
| sotto 10 | 229 | +4,97 | 93% | 1917-1985 |
| 10-15 | 461 | +5,23 | 97% | 1882-2009 |
| 15-20 | 514 | +4,60 | 85% | 1881-2011 |
| 20-25 | 249 | +2,91 | 77% | 1898-2013 |
| 25-30 | 83 | +2,14 | 80% | 1901-2007 |
| **oltre 30** | 57 | **−4,23** | **9%** | 1929 e 1997-2002 |

Il premio si assottiglia dolcemente da CAPE 15 in su e poi, oltre 30, cambia segno. È l'unica condizione in un secolo e mezzo in cui le obbligazioni hanno battuto le azioni con regolarità.

Ed è anche il punto in cui bisogna essere onesti sulla quantità di prove. **Quei 57 mesi sono due episodi**, il 1929 e il periodo 1997-2002. Sette anni di calendario su centocinquanta. La soglia dei 30 non è una legge di natura: è quello che hanno fatto due bolle.

## Dove siamo oggi

Il decennale americano rende il **5,29%** (settembre 2026) e il CAPE vale **40,57** (28 luglio 2026), cioè un earnings yield del 2,46%. Lo spread fra i due è di −2,83 punti: più basso che nel 97% dei mesi dal 1881.

| modello stimato su... | ytm che pareggia, al CAPE di oggi | premio atteso oggi |
|---|---|---|
| tutto il campione 1881-2013 | 6,09% | **+0,59 punti l'anno** |
| solo il dopoguerra 1945-2013 | 4,78% | **−0,79 punti l'anno** |

Due modelli, stessa struttura, stessi dati fino alla data di taglio, e due risposte di segno opposto. Lo scarto tipico dei residui è di **3,1 punti l'anno** nel modello del dopoguerra e di 4,4 in quello completo: la distanza fra le due stime centrali, 1,4 punti, è una frazione del rumore che le circonda.

La stessa instabilità si vede sulla frontiera. A parità di earnings yield al 4%, il pareggio cade al **3,50%** se stimiamo sul 1881-1944 e al **6,46%** se stimiamo sul 1945-2013. Tre punti di differenza su un numero che dovrebbe essere la risposta dell'articolo.

C'è un ultimo controllo che toglie ogni tentazione di prendere il modello sul serio come strumento di previsione. In un secolo e mezzo il modello ha previsto la vittoria delle obbligazioni in **undici mesi**, e in dieci di quelli ci ha preso. Sembra un ottimo risultato finché non si guarda il confronto giusto: l'accuratezza complessiva del segno è dell'85,7%, mentre chi avesse sempre risposto "vincono le azioni", senza modello e senza dati, avrebbe azzeccato l'85,1%. **Il modello aggiunge sei decimi di punto a una monetina truccata.**

Quello che resta, e che secondo me è l'unica cosa da portare a casa, non è un numero previsto ma una posizione: oggi siamo in una delle configurazioni di prezzi relativi più estreme da quando esistono i dati, e le due volte in cui il CAPE era sopra 30 le obbligazioni hanno vinto il decennio successivo. Due volte su due, che però è un campione di due.

## Quello che questo studio non dice

**Non dice che le obbligazioni batteranno le azioni nei prossimi dieci anni.** La stima centrale è dentro il rumore, il campione utile sopra CAPE 30 è di due episodi, e il modello batte a malapena il non avere modello.

**Non dice che il CAPE a 40 è insostenibile.** Dice che le due volte in cui si è saliti sopra 30, i dieci anni dopo sono stati brutti per le azioni *rispetto alle obbligazioni*. Sul fatto che la composizione dell'indice americano di oggi sia confrontabile con quella del 1929 si può discutere a lungo, e non lo abbiamo verificato qui.

**I dati americani non sono i tuoi dati.** Tutto lo studio è su S&P 500, decennale americano e inflazione americana. Per un investitore in euro ci sono di mezzo il cambio e una curva dei rendimenti diversa, e non è detto che la frontiera si sposti di poco.

**Le finestre si sovrappongono.** 1.593 mesi di acquisto con orizzonte decennale sono circa tredici osservazioni indipendenti. Tutti gli R² e tutte le percentuali di questo articolo vanno letti con quel numero in testa.

**Nulla è al netto di costi e imposte**, e l'indice obbligazionario non modella il roll-down, che sulle scadenze intermedie abbiamo [misurato in 0,42 punti l'anno](/posts/regola-2x-duration/): i rendimenti obbligazionari qui sono prudenti di quella quantità.

## Fonti e metodo

- **Dati**: Robert Shiller, *Irrational Exuberance*, serie mensile dal gennaio 1871 con prezzo e dividendi dell'S&P, utili, indice dei prezzi al consumo, rendimento del decennale e CAPE. Il file si ferma a settembre 2023, il che non vincola lo studio: con orizzonte decennale l'ultimo mese di acquisto utilizzabile è comunque il 2013. Per la fotografia di oggi uso il CAPE aggiornato al luglio 2026 e il decennale da FRED (`DGS10`).
- **Indice azionario**: total return costruito reinvestendo ogni mese un dodicesimo del dividendo annuo. Dal 1871 al 2023 rende il 9,18% annuo nominale e il 6,91% reale.
- **Indice obbligazionario**: lo stesso motore a duration costante degli altri studi del sito, applicato al decennale di Shiller. Ogni mese si compra un titolo alla pari a dieci anni con cedola pari al rendimento corrente, lo si rivaluta il mese dopo al nuovo rendimento con scadenza ridotta di un dodicesimo, e si rinnova. Rende il 4,55% nominale e il 2,38% reale.
- **Validazione**: il tasso di Shiller contro `DGS10` di FRED sui 741 mesi comuni differisce in media di 0,003 punti, con correlazione 0,9985. L'indice costruito sulle due serie rende rispettivamente il 5,85% e il 5,75% annuo. Contro il nostro indice USA 7-10, che ha scadenza 8,5 anni e modella il roll-down, questo rende 0,16 punti in meno, il segno atteso.
- **Due avvertenze sui dati**: prima del 1953 i valori mensili di Shiller sono interpolati da fonti meno frequenti e il prezzo è una media mensile, non una chiusura, quindi la volatilità dei primi ottant'anni risulta più liscia del vero. E con un solo nodo di curva il roll-down non è modellabile.
- **Modello**: minimi quadrati ordinari del premio decennale reale su rendimento del decennale e inverso del CAPE, forma lineare fissata prima di stimare, nessuna selezione di variabili a posteriori. Stabilità verificata su 1881-1944 e 1945-2013.
- Codice e output: `scripts/convessita-ytm-premio-azionario.py`, risultati in `public/charts/convessita-ytm-premio-azionario/sintesi.json`. Lo script fallisce se la validazione contro FRED esce dalle tolleranze dichiarate.

Questo non è un consiglio di investimento.
