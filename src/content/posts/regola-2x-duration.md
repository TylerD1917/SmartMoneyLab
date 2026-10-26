---
title: "La regola del 2x duration, messa alla prova su 64 anni di dati"
description: "Per quanti anni va tenuto un ETF obbligazionario perché renda davvero il rendimento a scadenza che leggi oggi? La teoria dice il doppio della duration. L'ho verificata su quattro indici ricostruiti dal 1962."
pubDate: 2026-10-21
tags: ["etf-obbligazionari", "duration", "rendimento-a-scadenza", "obbligazioni", "treasury", "btp", "tassi", "reddito-fisso"]
author: "SmartMoneyLab"
category: "approfondimenti"
simulationSlug: "regola-2x-duration"
seoImage: "/charts/regola-2x-duration/01_meccanismo.png"
draft: false
faq:
  - q: "Per quanto tempo bisogna tenere un ETF obbligazionario?"
    a: |-
      Per un tempo pari a circa due volte la duration del fondo, se l'obiettivo è ottenere il rendimento a scadenza che il fondo mostrava il giorno dell'acquisto. Su quattro indici ricostruiti dal 1962 la regola regge bene sulle scadenze intermedie (duration vicina a 6,6, quindi tredici anni) e regge in modo più approssimativo sulle scadenze lunghe, dove l'errore minimo si misura intorno ai venti anni contro i venticinque previsti.
  - q: "Che cos'è la regola del 2x duration?"
    a: |-
      È il risultato, dimostrato da Leibowitz e co-autori e poi da Lozada nel 2016, secondo cui per un portafoglio obbligazionario a duration costante il rendimento medio ottenuto su un orizzonte di 2D − 1 periodi coincide con il rendimento a scadenza del momento dell'acquisto, qualunque cosa facciano i tassi nel frattempo. D è la duration modificata e il "meno uno" è un periodo di ribilanciamento.
  - q: "Perché due volte la duration e non una?"
    a: |-
      Perché un fondo a duration costante non invecchia. Un'obbligazione singola tenuta per un tempo pari alla sua duration compensa la perdita di prezzo con il maggior reddito da reinvestimento, e lì il conto si chiude. Un fondo invece ricompra duration ogni mese, quindi continua a incassare colpi di prezzo, e la compensazione completa arriva al doppio del tempo. Nei nostri dati la regola della sola duration è la peggiore delle cinque testate.
  - q: "Il rendimento a scadenza di un ETF obbligazionario è garantito?"
    a: |-
      No. Non è garantito a nessun orizzonte e non esiste una data alla quale il prezzo torna per forza a un valore di rimborso, perché il fondo non scade mai. A due volte la duration, sugli indici con duration vicina a sei anni e mezzo, il risultato è finito entro un punto dal rendimento iniziale nel 59-65% dei casi storici ed entro due punti nell'89%.
  - q: "Che cosa succede se vendo prima di due volte la duration?"
    a: |-
      Il risultato dipende molto di più dal prezzo di vendita che dalle cedole incassate, quindi dai tassi di quel giorno, che oggi nessuno conosce. Sui Treasury oltre i vent'anni l'errore medio a cinque anni di detenzione è di 3,4 punti l'anno, a dieci anni di 2,2, a venti di 1,2.
  - q: "Perché la regola funziona anche se i tassi salgono o scendono?"
    a: |-
      Perché a 2D − 1 periodi la parte rettilinea del percorso dei tassi si annulla da sola, con qualunque inclinazione. Quello che resta è solo la curvatura del percorso, cioè quanto i tassi sono stati sopra o sotto la linea retta che unisce il punto di partenza a quello di arrivo. Nei nostri dati questa sola variabile spiega fra l'83% e il 98% dello scarto osservato.
---

## In breve

Nello [studio sugli ETF obbligazionari](/posts/quanto-rendono-etf-obbligazionari/) avevo trovato che il rendimento a scadenza del giorno dell'acquisto predice bene il risultato successivo, ma solo su orizzonti lunghi, e che la soglia sembrava cadere intorno al doppio della duration. Era un'osservazione empirica, trovata guardando i numeri.

Ho scoperto grazie ai ragazzi di IPF che quella soglia ha un nome e un teorema dietro. La regola é: **"2 × duration − 1"** e ha una dimostrazione formale, che ho applicato ai nostri quattro indici ricostruiti dal 1962.

Tre risultati:

1. **La regola è solida, e il suo "meno uno" è quasi sempre frainteso.** Il "−1" è un periodo di ribilanciamento, non un anno: per un ETF che ruota il portafoglio ogni mese vale un dodicesimo di anno. Infatti nei nostri dati la versione mensile batte la versione annuale su tre gambe su quattro.
2. **Quello che rende la regola utile non è la precisione, è l'immunità.** A quel preciso orizzonte l'inclinazione del percorso dei tassi si cancella da sola: non serve prevedere se i tassi saliranno o scenderanno, che è esattamente la cosa che nessuno sa fare.
3. **Lo scarto che resta ha una sola causa, e si misura.** È la curvatura del percorso dei tassi, e da sola spiega fra l'83% e il 98% dell'errore osservato, con il coefficiente previsto dalla teoria.

## Da dove viene la regola

In italiano questa regola l'ho trovata ben formalizzata in un [articolo di Dedalo Invest](https://www.dedaloinvest.com/education/didattica-analisi/la-regola-del-2x-duration) che racconta la regola in forma divulgativa: per avere ragionevole certezza di ottenere il rendimento a scadenza con cui hai comprato un fondo obbligazionario, devi tenerlo per un tempo pari al doppio della sua duration, meno uno.

La dimostrazione formale più pulita che ho trovato è di **Carlos Lozada**, *Constant-Duration Bond Portfolios' Initial (Rolling) Yield Forecasts Return Best at Twice Duration* (2016), che generalizza un risultato di Martin Leibowitz e co-autori degli anni Ottanta e lo verifica su dati americani. Il paper è la fonte di tutto quello che segue: io ci ho messo i nostri dati, quattro indici a duration costante ricostruiti mese per mese dal 1962, che coprono anche l'Europa e l'Italia.

## La matematica, in quattro righe

Chiamiamo Y il rendimento a scadenza del fondo e D la sua duration modificata. La **Proposizione 1** del paper dice che il rendimento di un singolo periodo vale, in buona approssimazione:

**R = Y − (D − 1) × ΔY**

Incassi il rendimento corrente e subisci (o guadagni) la variazione dei tassi moltiplicata per la duration, meno un periodo, perché nel frattempo il titolo è invecchiato di un periodo prima di essere rinnovato.

Ora supponi che i tassi si muovano in **linea retta**, di una quantità ΔY uguale ogni periodo. Fai la media dei primi N rendimenti e viene:

**media = Y₁ + ΔY × ((N + 1) / 2 − D)**

Il termine fra parentesi si annulla quando **N = 2D − 1**. E qui c'è tutta la forza del risultato: si annulla **qualunque sia ΔY**. Che i tassi salgano di due punti o scendano di tre, a quell'orizzonte preciso il loro effetto sparisce dalla media, e quello che resta è Y₁, cioè il rendimento a scadenza del giorno in cui hai comprato.

### Il "meno uno" non è un anno

 **N = 2D − 1 è espresso in periodi di ribilanciamento**, non in anni. Se il fondo rinnova il portafoglio una volta l'anno, il periodo è un anno e con duration 5 l'orizzonte è di 9 anni. Ma un ETF obbligazionario vero rotola il portafoglio ogni mese, come il nostro indice: lì il periodo è un dodicesimo d'anno, il "meno uno" vale 0,08 anni e l'orizzonte è **praticamente 2D**.

Non è una pignoleria: i nostri dati distinguono le due versioni, e danno ragione alla teoria. Sui Treasury 7-10 la regola "2D meno un mese" sbaglia in media di **0,95 punti** l'anno, la versione "2D meno un anno" di **1,02**. Sull'area euro 0,99 contro 1,02. Sull'Italia 1,60 contro 1,72. Vince la versione calibrata sulla frequenza con cui lo strumento ruota davvero.

## Perché funziona: la pendenza non conta, la curvatura sì

Prima di guardare i dati storici conviene vedere il meccanismo in laboratorio. Ho preso il motore che costruisce i nostri indici, l'ho fatto girare su percorsi dei tassi **inventati** e ho misurato lo scarto fra il rendimento ottenuto e quello di partenza. Acquisto al 5%, duration 6,9, quindi detenzione di 13,7 anni.

<figure>
  <img src="/charts/regola-2x-duration/01_meccanismo.png" alt="Due pannelli. A sinistra tre percorsi rettilinei dei tassi che partono dal 5% e arrivano all'1%, al 5% e al 9%: lo scarto finale è +0,16, −0,05 e +0,05 punti. A destra tre percorsi con gli stessi estremi, 5% e 3%, uno rettilineo, uno concavo e uno convesso: gli scarti sono +0,01, +1,14 e −1,12 punti." width="2680" height="1120" decoding="async" />
  <figcaption>Sentieri dei tassi sintetici dati in pasto al motore degli indici. A sinistra cambia l'inclinazione, a destra la curvatura. Lo scarto è sulla media aritmetica dei rendimenti mensili, la grandezza su cui il teorema è esatto.</figcaption>
</figure>

Nel pannello di sinistra ci sono tre mondi opposti: i tassi crollano dal 5% all'1%, restano fermi, salgono al 9%. Tre destini completamente diversi per chi ha comprato quel fondo, e a 2 × duration **lo scarto è fra −0,05 e +0,16 punti in tutti e tre i casi**. Questa è l'immunità alla pendenza: il motivo per cui la regola è utile a qualcuno che non sa prevedere i tassi, cioè a chiunque.

Nel pannello di destra i tre percorsi partono dal 5% e arrivano al 3%, stessi estremi, ma ci arrivano per strade diverse. Il verde resta alto a lungo e poi scende: sta **sopra** la retta che unisce gli estremi, è concavo, e chi lo ha vissuto ha incassato cedole alte per più tempo. Risultato: **+1,14 punti sopra il rendimento di partenza**. Il rosso fa il contrario, crolla subito e risale alla fine: sta sotto la retta, è convesso, e chi lo ha vissuto ha passato la detenzione a incassare poco. Risultato: **−1,12 punti**.

Questa è la curvatura del sentiero dei tassi, e conviene chiarire subito un equivoco di nomi. **Non è la curva dei tassi.** La curva dei tassi è una fotografia: i rendimenti di scadenze diverse nello stesso istante, il due anni, il cinque, il dieci, il trenta di oggi. Il sentiero dei tassi è un film: il rendimento di una sola scadenza che cambia nel tempo. La regola del doppio della duration parla del film.

## La prova sui dati: dove cade davvero il minimo

Passiamo alla storia vera. Per ogni mese di acquisto dal 1962 a oggi, e per ogni orizzonte da 2 a 28 anni, ho calcolato il rendimento annuo effettivamente ottenuto e l'ho confrontato con il rendimento a scadenza di quel mese. L'errore assoluto medio di quel confronto, orizzonte per orizzonte, disegna una curva a U: il fondo della U è l'orizzonte in cui il prezzo di acquisto ha indovinato meglio.

<figure>
  <img src="/charts/regola-2x-duration/02_curva_errore.png" alt="Quattro pannelli con l'errore medio di previsione in funzione degli anni di detenzione, da 2 a 28. Ogni curva scende ripida, tocca un minimo e risale. I minimi cadono a 14 anni per i Treasury 7-10, 21 per i Treasury 20+, 12 per l'area euro e 20 per l'Italia; la banda colorata segna l'intervallo di 2 x duration osservato." width="2520" height="1680" decoding="async" />
  <figcaption>Errore assoluto medio fra rendimento a scadenza all'acquisto e rendimento annuo composto ottenuto. La riga tratteggiata è 2 × duration calcolato sulla duration mediana della gamba, la banda colorata è l'intervallo fra il minimo e il massimo storico dello stesso valore.</figcaption>
</figure>

| gamba | duration mediana | orizzonte previsto | minimo osservato | errore al minimo |
|---|---|---|---|---|
| Treasury USA 7-10 | 6,6 | 13,2 anni | **14 anni** | 0,96 punti |
| Area euro 7-10 | 6,7 | 13,3 anni | **12 anni** | 0,99 punti |
| Treasury USA 20+ | 13,1 | 26,0 anni | **21 anni** | 1,21 punti |
| Italia 15+ | 12,7 | 25,3 anni | **20 anni** | 1,24 punti |

Sulle due gambe a scadenza intermedia la previsione teorica e il dato storico distano meno di un anno e mezzo, il che per una regola di questo tipo è notevole. Sulle due gambe lunghe il minimo arriva **quattro o cinque anni prima** di quanto previsto. È uno scostamento vero e più avanti lo spiego, ma va messo in prospettiva: la U delle gambe lunghe è molto piatta sul fondo. Sui Treasury oltre i vent'anni l'errore vale 1,31 punti a diciotto anni, 1,21 a venti e ventuno, 1,26 a ventidue, 1,38 a ventiquattro. La scelta fra venti e ventisei anni di detenzione cambia il risultato di due decimi di punto.

Quello che non è affatto piatto è il tratto prima: la stessa gamba sbaglia di **3,4 punti l'anno se la tieni cinque anni** e di 2,2 se la tieni dieci. Questo diventa fondamentale per l'acquisto di un ETF obbligazionario lungo con l'orizzonte giusto.

## L'orizzonte non è un numero fisso

C'è un dettaglio che i divulgatori saltano quasi sempre, e che sposta il risultato parecchio: **la duration di un portafoglio obbligazionario non è una costante del prodotto, dipende dal livello dei tassi.** Un titolo alla pari a vent'anni comprato con tassi al 15% ha duration modificata 6,3; lo stesso titolo comprato con tassi all'1% ha duration 18,1. Stessa scadenza, stessa struttura, duration quasi tripla.

Quindi anche la regola, se la si prende sul serio, chiede un orizzonte che si muove nel tempo.

<figure>
  <img src="/charts/regola-2x-duration/05_orizzonte.png" alt="Quattro linee dal 1962 al 2026 che mostrano gli anni di detenzione richiesti dalla regola 2 x duration. I Treasury oltre i vent'anni passano da 12 anni nel 1981 a 43 nel 2020 e tornano a 27 oggi; le gambe a scadenza intermedia oscillano fra 9 e 17 anni." width="2240" height="1200" decoding="async" />
  <figcaption>Anni di detenzione richiesti dalla regola, ricalcolati mese per mese con la duration del momento. Ai minimi dei tassi la regola chiedeva orizzonti che nessun investitore privato ha.</figcaption>
</figure>

Nel 1981, con i tassi americani oltre il 13%, la regola chiedeva **dodici anni** di detenzione sui Treasury lunghi. Nel 2020, con i tassi a zero, ne chiedeva **quarantatré**. Oggi, con i rendimenti risaliti, siamo tornati a ventisette.

Questo spiega anche una cosa che si sente dire spesso e che è vera solo a metà: "i tassi bassi rendono le obbligazioni lunghe più pericolose". Questa affermazione diventa ancor più vera e non è solo che rendono poco. Il problema maggiore è che il tempo necessario perché quel poco si realizzi si allunga più che proporzionalmente, e a un certo punto esce dall'orizzonte di vita di chi compra.

## Cinque regole a confronto

A questo punto la domanda interessante è quale regola di detenzione funzioni meglio. Le ho messe tutte alla prova nello stesso modo: per ogni mese di acquisto calcolo la duration di quel mese, da lì ricavo l'orizzonte secondo ciascuna regola, e misuro l'errore.

<figure>
  <img src="/charts/regola-2x-duration/03_regole.png" alt="Grafico a barre raggruppate con l'errore assoluto medio di cinque regole di detenzione (D, 1,5 D, 2D, 2D meno un anno, 2,5 D) sui quattro indici. La regola della sola duration è sempre la peggiore, con 3,54 punti sull'Italia; a 2D gli errori scendono a 0,95 e 0,99 punti sulle due gambe intermedie." width="2320" height="1200" decoding="async" />
  <figcaption>Errore assoluto medio in punti percentuali all'anno. L'orizzonte è ricalcolato con la duration del mese di acquisto, quindi ogni barra usa un campione leggermente diverso.</figcaption>
</figure>

| regola | USA 7-10 | USA 20+ | Area euro | Italia 15+ |
|---|---|---|---|---|
| tieni per la duration | 1,66 | 2,06 | 1,54 | 3,54 |
| 1,5 × duration | 1,20 | 1,49 | 1,16 | 2,13 |
| **2 × duration** | **0,95** | 1,48 | **0,99** | 1,60 |
| 2 × duration − 1 anno | 1,02 | 1,48 | 1,02 | 1,72 |
| 2,5 × duration | 1,05 | 1,55 | 1,03 | **1,19** |

Il risultato più netto non è quale regola vinca, è **quale perda**: la regola più diffusa in assoluto, quella che dice di tenere il fondo per un tempo pari alla sua duration, è la peggiore di tutte e quattro le gambe, con distacchi che arrivano a due punti l'anno sull'Italia. Chi la applica si ferma esattamente a metà strada.

Il motivo è che quella regola vale per un'obbligazione singola, non per un fondo. Un titolo che tieni per un tempo pari alla sua duration compensa la perdita di prezzo con il maggior reddito da reinvestimento, e il conto si chiude lì. Un fondo a duration costante invece **ricompra duration ogni mese**: non invecchia mai, resta esposto per sempre, e la compensazione completa arriva al doppio del tempo. È la stessa ragione per cui il suo prezzo non converge mai a un valore di rimborso, il tema che divide [ETF obbligazionari e obbligazioni singole](/posts/etf-obbligazionari-o-obbligazioni).

Sulle due gambe intermedie vince 2D, come previsto. Sulle due lunghe il quadro è più sfumato: 2D è sostanzialmente pari a 2D − 1 anno, e sull'Italia è 2,5D a fare meglio. Va anche detto che queste colonne non sono perfettamente confrontabili fra loro, perché ogni regola, chiedendo orizzonti diversi, lascia nel campione un numero diverso di mesi di acquisto: 503 per la regola 2D sull'area euro, 264 sull'Italia.

## Il meccanismo: cosa resta quando la regola ha fatto il suo lavoro

Qui arriva la parte che mi ha convinto che il teorema non sia una coincidenza statistica. Se la teoria è giusta, lo scarto che osserviamo non è rumore: deve valere **esattamente la curvatura del sentiero dei tassi**, con coefficiente uno.

Per misurarla ho preso, per ogni mese di acquisto, il sentiero dei tassi nei successivi 2D anni, ho tracciato la retta che unisce il primo punto all'ultimo e ho calcolato **di quanto il sentiero vero sta in media sopra quella retta**. Positiva vuol dire concavo, tassi tenuti alti e scesi dopo; negativa vuol dire convesso. Poi ho regredito lo scarto osservato su quella sola variabile.

<figure>
  <img src="/charts/regola-2x-duration/04_convessita.png" alt="Quattro grafici a dispersione con la curvatura del sentiero dei tassi sull'asse orizzontale e lo scarto dal rendimento iniziale su quello verticale. I punti si allineano quasi perfettamente lungo una retta di pendenza vicina a uno, con R quadro fra 0,83 e 0,98, accanto alla retta teorica tratteggiata." width="2520" height="1680" decoding="async" />
  <figcaption>Ogni punto è un mese di acquisto. La retta continua è la regressione osservata, la tratteggiata è quella prevista dal teorema: pendenza +1,00.</figcaption>
</figure>

| gamba | mesi | curvatura media | scarto medio | pendenza | R² |
|---|---|---|---|---|---|
| Treasury USA 7-10 | 505 | +0,08 | +0,68 | +0,87 | 0,93 |
| Treasury USA 20+ | 469 | +0,74 | +1,49 | +0,86 | 0,96 |
| Area euro 7-10 | 503 | +0,09 | +0,15 | +0,95 | 0,98 |
| Italia 15+ | 264 | −0,73 | +0,39 | +1,07 | 0,83 |

La teoria prevede pendenza +1,00 e troviamo fra 0,86 e 1,07, con R² fino a 0,98. **Non è una correlazione: è un'identità contabile che si verifica nei dati.** Quando il teorema sbaglia, sbaglia per una ragione sola, nota, misurabile e con il segno che ci si aspetta.

Due letture pratiche. La prima: la curvatura media delle due gambe intermedie è vicina a zero (+0,08 e +0,09). Su cinquecento mesi di acquisto i sentieri concavi e quelli convessi si compensano, quindi la regola **in media è centrata** e lo scarto su un singolo acquisto è imprevedibile ma simmetrico. La seconda: sui Treasury lunghi la curvatura media è +0,74, cioè su finestre di ventisei anni il sentiero dei tassi americano del dopoguerra è stato sistematicamente concavo, tassi altissimi mantenuti a lungo e poi un lungo calo. Tre quarti del generoso +1,49 di scarto medio su quella gamba sono questo, cioè un fatto di quel periodo storico, non una proprietà dello strumento.

## Il secondo pezzo: il roll-down

Resta un residuo, e ho provato a vedere quanto ne spieghi il **roll-down**, cioè il guadagno che un fondo incassa semplicemente scivolando lungo una curva dei tassi inclinata: compra a dieci anni, un mese dopo ha in pancia un titolo a nove anni e undici mesi, che se la curva sale vale un po' di più.

La gamba americana 7-10 è l'unica dei nostri indici in cui il roll-down è modellato, perché è l'unica con due nodi di curva e storia lunga. L'ho ricostruita due volte, con e senza, sullo stesso identico sentiero dei tassi:

| indice USA 7-10 | scarto medio | errore medio | entro 1 punto |
|---|---|---|---|
| con roll-down | +0,68 | 0,95 | 65,1% |
| senza roll-down | +0,26 | 0,84 | 67,7% |

**Il roll-down vale 0,42 punti l'anno** di rendimento in più rispetto a quanto la regola prevede. È il terzo canale di scostamento che Lozada elenca, i cambiamenti di pendenza della curva, e qui è isolato in modo pulito: stessa serie di tassi, due motori, una sola differenza.

Tolta la curvatura e tolto il roll-down, il residuo che rimane è questo:

| gamba | duration | residuo |
|---|---|---|
| Area euro 7-10 | 6,7 | +0,06 |
| Treasury USA 7-10 | 6,6 | +0,18 |
| Treasury USA 20+ | 13,1 | +0,76 |
| Italia 15+ | 12,7 | +1,11 |

Cresce con la duration, ed è sempre positivo: il fondo rende **più** di quanto la regola prometta. Il colpevole più probabile è la convessità del prezzo obbligazionario, il termine di secondo grado che la Proposizione 1 lascia cadere per semplificare. Su un titolo a duration sei quel termine è trascurabile, su uno a duration tredici no: i guadagni quando i tassi scendono superano le perdite quando salgono della stessa quantità, e la differenza si accumula.

È anche la spiegazione più coerente del perché, sulle gambe lunghe, l'errore minimo arrivi quattro o cinque anni **prima** di 2D. Se incassi sistematicamente qualcosa in più di quanto previsto, raggiungi il rendimento di partenza un po' prima del tempo previsto.

## Cosa me ne faccio

Tre cose concrete, in ordine di utilità.

**Il numero che devi guardare non è uno, sono due.** Il rendimento a scadenza del fondo ti dice *quanto*, la duration ti dice *per quanto*. Entrambi stanno nella scheda del prodotto, uno accanto all'altro, e vanno letti insieme: un fondo al 4% con duration 13 e uno al 4% con duration 6 non sono la stessa promessa, perché il primo te la mantiene in ventisei anni e il secondo in tredici. Nel [simulatore degli ETF obbligazionari](/strumenti/simulatore-etf-obbligazionari) ci sono entrambi.

**La regola non promette precisione, promette che non devi indovinare.** Vale la pena ripeterlo perché è la parte controintuitiva: quello che a 2D si annulla è la componente che nessuno sa prevedere, cioè la direzione dei tassi. Quello che resta è una componente che dipende dalla forma del percorso, e che nei nostri dati, sulle scadenze intermedie, è mediamente zero. Su un singolo acquisto il risultato è finito entro un punto dalla previsione nel 59-65% dei casi ed entro due punti nell'89%. Non è certezza, è un intervallo onesto.

**Se l'orizzonte non c'è, cambia strumento, non aspettative.** Un ETF sui Treasury oltre i vent'anni comprato oggi chiede ventisette anni per mantenere la sua promessa. Se non li hai, non stai comprando quel rendimento a scadenza: stai facendo una scommessa sui tassi, che è una cosa legittima ma diversa, e va valutata con altri criteri, a partire dal fatto che nel 2022 quello stesso indice ha perso il 29% in un anno.

## Limiti

**Le finestre si sovrappongono quasi tutte.** Cinquecento mesi di acquisto su una gamba non sono cinquecento osservazioni indipendenti: sono un'unica storia guardata da cinquecento punti di partenza diversi. I percentili e le percentuali di successo descrivono quello che è successo, non probabilità future.

**Il periodo contiene una sola grande discesa dei tassi.** Dal 1981 al 2020 i rendimenti sono scesi quasi ininterrottamente, ed è il motivo per cui la curvatura media delle gambe lunghe è così marcata. Un secolo con la forma opposta darebbe scarti medi di segno opposto, e lo si può leggere direttamente nella regressione: basta cambiare il segno della curvatura.

**I campioni delle quattro gambe non sono confrontabili fra loro.** Ognuna parte quando partono i suoi dati, e la gamba italiana prima del novembre 1993 simula un portafoglio di BTP lunghi che in Italia non esisteva. Sui 264 mesi di acquisto usati nel test a 2D questo pesa parecchio, ed è la ragione principale per cui è la gamba con l'R² più basso.

**Tutto è al lordo di costi e imposte.** Il costo di gestione va sottratto dalla previsione: un decimo o due di punto l'anno sposta poco in valore assoluto, ma è esattamente dello stesso ordine di grandezza dei residui che abbiamo discusso sopra.

**La duration che uso è calcolata, non dichiarata.** È la duration modificata di un titolo alla pari con la scadenza dell'indice, al rendimento di quel mese. Un ETF vero detiene un paniere e la sua duration dichiarata può differire di qualche decimo. Sulla regola cambia poco, perché l'orizzonte si muove di due volte quella differenza.

## Fonti e metodo

- **Il paper**: Carlos Lozada, *Constant-Duration Bond Portfolios' Initial (Rolling) Yield Forecasts Return Best at Twice Duration*, 2016. La Proposizione 1 e la scomposizione del sentiero dei tassi in parte lineare e scarto sono sue; la Sezione 6 tratta il rolling yield e il roll-down.
- **L'articolo divulgativo** da cui sono partito: [La regola del 2x duration](https://www.dedaloinvest.com/education/didattica-analisi/la-regola-del-2x-duration), Dedalo Invest.
- **Il risultato originale** è di Martin Leibowitz e co-autori, che negli anni Ottanta mostrarono per primi che l'orizzonte di immunizzazione di un portafoglio a duration costante è circa il doppio di quello di un'obbligazione singola.
- **Indici e dati**: gli stessi quattro indici a duration costante dello [studio principale](/posts/quanto-rendono-etf-obbligazionari/), ricostruiti da Treasury constant maturity FRED (`DGS7`, `DGS10`, `DGS20`, `DGS30`), tasso a lungo termine dell'area euro e dell'Italia OCSE, validati contro IEF, TLT e SXRQ con scarti fra −0,05 e +0,16 punti l'anno.
- **Duration modificata**: derivata numericamente dal prezzo del titolo alla pari, che è il valore attuale dei flussi residui con cedole semestrali. Varia col livello dei tassi, e nel test a orizzonte variabile è ricalcolata per ogni mese di acquisto.
- **Le due grandezze che non vanno confuse**: il teorema è esatto sulla **media aritmetica** dei rendimenti di periodo, l'investitore porta a casa il **rendimento composto**. Il test della curvatura usa la prima, le tabelle di errore la seconda, che è quella che conta per chi compra. Sulla regola 2D la differenza è di circa cinque centesimi di punto sulle gambe intermedie.
- **Curvatura del sentiero**: media del sentiero dei tassi nei 2D anni successivi all'acquisto, meno la media della retta che ne unisce gli estremi, in punti percentuali.
- Codice: `scripts/regola-2x-duration.py`, che importa il motore degli indici dello studio principale; output in `public/charts/regola-2x-duration/sintesi.json`.

Questo non è un consiglio di investimento.
