---
category: "approfondimenti"
title: "Ha senso inserire oro in portafoglio?"
description: "Quattro portafogli a confronto (100% azionario, 90/10, 75/25, 50/50 oro) su mezzo secolo di dati, in dollari sull'S&P 500 e in euro su MSCI World e ACWI. Cosa dicono i numeri."
pubDate: 2026-04-29
updatedDate: 2026-10-26
tags: ["oro", "asset-allocation", "diversificazione", "rolling-windows", "backtest"]
author: "SmartMoneyLab"
simulationSlug: "ha-senso-oro-portafoglio"
draft: false
---

## In breve

Su mezzo secolo di dati (gennaio 1976, giugno 2026) confronto quattro portafogli comprati e mai più toccati, 100% azionario, 90/10, 75/25 e 50/50 fra azioni e oro, su tutte le finestre mobili a 5, 10 e 20 anni con step trimestrale. Dai numeri escono tre risultati centrali:

1. **L'oro è empiricamente decorrelato dall'azionario.** La correlazione mensile fra S&P 500 total return e oro LBMA sul periodo è **−0,039**: praticamente zero. Non è un argomento teorico, sono 606 mesi di osservazione in cui i due asset si sono mossi in modo sostanzialmente indipendente.
2. **Il costo in rendimento è basso.** Il 50/50 rende il 10,75% annuo composto sull'intero periodo contro il 12,08% del 100% azionario: 133 punti base in meno. Il 90/10 ne perde appena 21. Una geometria completamente diversa rispetto alle obbligazioni, dove il 60/40 perdeva quasi 240 punti base nel periodo equivalente.
3. **La protezione negli scenari decennali peggiori è netta.** Nel 5% delle finestre decennali andate peggio il 100% azionario chiude all'1,54% annualizzato, il 50/50 al 6,37%. *Ogni* allocazione con oro batte il portafoglio tutto azionario nei casi peggiori a dieci anni.

C'è poi un dato che smonta un mito diffuso: **a vent'anni nessun portafoglio ha evitato i drawdown profondi.** Nel 100% azionario *tutte* le 123 finestre ventennali hanno visto almeno un calo del 20% dal massimo, e l'81,3% ha visto un calo del 30% o peggio. Anche il 50/50 ha superato il 20% in tutte le finestre. Sul lungo periodo non si scappa dalla volatilità con solo oro, si scappa solo dalle perdite definitive a parità di tempo.

Infine, la parte che riguarda più da vicino chi investe dall'Italia: rifatto lo stesso test **in euro su MSCI World e MSCI ACWI IMI**, il quadro migliora sensibilmente. Sull'ACWI, l'oro costa 18 punti base in trentadue anni e in cambio azzera le finestre decennali in perdita. 

## La domanda

L'oro è probabilmente l'asset più chiacchierato della finanza retail italiana. Lo sento citare in due modi inconciliabili:

- *Bene rifugio*, lo strumento contro l'inflazione, l'unica vera riserva di valore.
- *Asset speculativo* per definizione, qualcosa che non produce niente, che vale solo quello che il prossimo è disposto a pagare.

Entrambe le posizioni hanno argomenti validi. Quello che manca, quasi sempre, è una verifica seria sui dati. Voglio rispondere a tre domande in sequenza:

1. **Ha senso** inserire oro in portafoglio?
2. **Quando** ha senso?
3. **Quanto**?

## Il metodo: finestre mobili e nessun ribilanciamento

Confermo l'impianto metodologico stabilito col primo articolo del blog, il modello che useremo in tutti i confronti fra allocazioni:

- Costruisco le serie mensili di rendimenti totali per i quattro portafogli su tutto il periodo **gennaio 1976, giugno 2026** (606 mesi, poco più di mezzo secolo).
- Per ogni portafoglio calcolo le metriche su **tutte le finestre a 5 anni** (60 mesi), **10 anni** (120 mesi) e **20 anni** (240 mesi), con **passo di 3 mesi**. In totale 183 finestre quinquennali, 163 decennali e 123 ventennali per ciascun portafoglio.
- I rendimenti sono **lordi**, senza costi degli ETF e senza tasse. Lo scopo è isolare la tesi sull'allocazione dal rumore dei costi.
- **Total return**: i rendimenti dell'azionario includono i dividendi reinvestiti. L'oro non genera flussi (niente cedole, niente dividendi), quindi il suo total return coincide con la variazione di prezzo.
- In questo caso, **nessun ribilanciamento**, in nessuno dei quattro portafogli. Compri all'inizio con i pesi scelti e lasci stare. Per le finestre mobili ogni finestra riparte dai pesi iniziali, perché è il modo in cui ragiona chi investe davvero: *"se compro oggi un 90/10 e lo tengo dieci anni senza toccarlo, cosa mi aspetto?"*

### Le scelte tecniche

- **Azionario USA**: indice S&P 500 Total Return (chiusura dell'ultima seduta di ogni mese) da febbraio 1988; prima, prezzo S&P 500 di fine mese più il dividendo annualizzato del dataset Shiller, con la formula standard `r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1`. 
- **Azionario globale** (ultima sezione): MSCI World total return in euro da gennaio 1976 e MSCI ACWI IMI total return in euro da giugno 1994, che è la sua prima data disponibile.
- **Oro**: prezzo LBMA mensile in dollari per oncia, dalla serie storica pubblica che riporta fedelmente i dati LBMA (la stessa che FRED ha smesso di distribuire da gennaio 2022, dopo la revoca della licenza da parte di ICE Benchmark Administration). Per le gambe in euro il prezzo è convertito al cambio di fine mese.
- **Cambio EUR/USD**: quotazione BCE di fine mese dal gennaio 1999; prima, marco tedesco per dollaro convertito al tasso irrevocabile di 1,95583 marchi per euro, che è la prassi standard per ricostruire serie in euro anteriori all'unione monetaria.

Gli script Python che producono tutte le serie e i grafici sono [`scripts/ha-senso-oro-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-oro-portafoglio.py) e [`scripts/oro-portafoglio-indici-eur.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/oro-portafoglio-indici-eur.py), riga per riga, riproducibili.

## L'oro come asset speculativo: vale davvero il suo prezzo?

Prima di guardare i dati conviene affrontare l'argomento che *non* si può ignorare. Warren Buffett, Charlie Munger e una lunga tradizione di investitori value lo ripetono da decenni: **l'oro non produce nulla**. Non genera utili come un'azione, non paga cedole come un'obbligazione, non sforna affitti come un immobile. Buffett, in una lettera famosa agli azionisti del 2011, fa il calcolo: tutto l'oro estratto nella storia formerebbe un cubo di circa 21 metri di lato, e il valore di quel cubo è confrontabile con quello dell'intero S&P 500. La differenza è che il cubo continuerà a essere un cubo, mentre l'S&P 500 produce ogni anno utili e dividendi reinvestibili.

L'argomento è solido e non si smonta con la retorica. **L'oro non ha un valore intrinseco calcolabile** nel senso classico: non puoi attualizzare flussi futuri perché non ce ne sono. Vale quello che il prossimo compratore è disposto a pagare. È, in senso tecnico, un asset speculativo.

I controargomenti a favore dell'oro non sono di tipo finanziario tradizionale, sono di tipo strutturale:

- **Riserva di valore su orizzonti lunghissimi.** Nei millenni l'oro ha mantenuto un potere d'acquisto comparabile. Le valute a corso legale si svalutano per costruzione; l'oro no, perché la quantità globale cresce dell'1 o 2% l'anno per estrazione, contro una massa monetaria che nei periodi inflazionistici cresce anche del 5 o 10%.
- **Decorrelazione strutturale dalle valute e dai mercati.** Quando le banche centrali stampano per finanziare deficit l'oro tende a salire, perché è la moneta residuale del sistema. Quando la fiducia istituzionale cala (guerra, sanzioni, congelamento di asset) l'oro è uno dei pochi beni fuori dal perimetro del sistema bancario.
- **Copertura contro i rischi di coda:** il motivo per cui le banche centrali ne tengono migliaia di tonnellate nelle riserve.

Tutti argomenti plausibili sul piano narrativo. Ma quello che interessa su questo blog è la verifica empirica. La domanda diventa quindi: **nei dati dal 1976 a oggi, l'oro si è davvero comportato da diversificatore?**

La risposta è **sì, in modo più netto di quanto mi aspettassi.** La correlazione mensile fra S&P 500 total return e oro LBMA sull'intero periodo è **−0,039**, sostanzialmente zero. Significa che su 606 mesi di osservazione il movimento di un asset non ha praticamente alcuna capacità di prevedere il movimento dell'altro. Per dare una scala: la correlazione fra azioni e titoli di Stato americani si è mossa storicamente fra +0,3 (anni Ottanta) e −0,4 (dopo la crisi del 2008). Le obbligazioni *correlano* con l'azionario, anche se in modo variabile. **L'oro proprio no.**

Questo è già un primo punto: **sul piano statistico l'oro è un diversificatore vero**, non un diversificatore di facciata. Indipendentemente dalla critica filosofica sull'assenza di valore intrinseco, *empiricamente* aggiungere oro a un portafoglio azionario riduce il rischio senza una contropartita equivalente in rendimento, almeno fino a un certo punto, come vedremo. Resta da capire quanto questa decorrelazione si traduca in vantaggio reale, e a quale prezzo.

## Risultati su finestre di 10 anni

Partiamo dall'orizzonte intermedio, dove il premio al rischio azionario comincia a manifestarsi ma non è ancora saturo:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/01_boxplot_cagr_10y.png" alt="Distribuzione del rendimento annuo composto su finestre mobili di 10 anni per i portafogli 100% azionario, 90/10, 75/25 e 50/50 oro, S&P 500 total return e oro LBMA, 1976-2026." />
  <figcaption>Distribuzione del rendimento annuo composto su finestre di 10 anni, passo 3 mesi. 163 finestre per portafoglio. Box centrale: dal 25° al 75° percentile. Linea: mediana. Baffi: dal 5° al 95° percentile.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | 5° perc. | 25° perc. | **Mediana** | 75° perc. | 95° perc. |
|---|---|---|---|---|---|
| 100% azionario | 1,54% | 8,16% | **13,24%** | 15,24% | 18,20% |
| 90/10 | 4,14% | 8,26% | **12,50%** | 14,53% | 17,41% |
| 75/25 | 5,87% | 8,62% | **11,50%** | 13,52% | 15,79% |
| 50/50 | 6,37% | 7,98% | **9,63%** | 11,49% | 13,98% |

Come si legge:

- **Sui valori mediani l'azionario domina**, ma il margine è molto più ridotto rispetto al confronto fra azioni e obbligazioni: 13,24% del tutto azionario contro 12,50% del 90/10 (appena 74 punti base) e 9,63% del 50/50 (3,6 punti percentuali, contro i circa 2,4 che il 60/40 perdeva nell'articolo sulle obbligazioni).
- **Negli scenari peggiori l'oro vince nettamente.** Il 100% azionario ha un 5° percentile all'1,54%, un decennio di fatto perduto in termini reali una volta tolta l'inflazione. Il 50/50 sta al 6,37%, quasi cinque punti sopra. Ma anche il 90/10, che aggiunge solo un decimo di oro, porta il 5° percentile al 4,14%: protezione moderata, non simbolica.
- **Sulla frequenza di decenni chiusi in perdita**: il tutto azionario perde nel 4,9% delle finestre (8 su 163). Il 75/25 e il 50/50 mai. Il 90/10 una sola volta su 163.

Il quadro qualitativo somiglia a quello delle obbligazioni, l'azionario domina in mediana e l'asset di diversificazione protegge nelle code, ma il bilancio è molto più favorevole all'oro: paga molto meno in rendimento mediano e protegge molto di più nei casi peggiori.

## Risultati su finestre di 5 anni

A cinque anni le code si allargano e l'azionario comincia a sbattere contro periodi in cui non c'è stato tempo di recuperare:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/02_boxplot_cagr_5y.png" alt="Distribuzione del rendimento annuo composto su finestre mobili di 5 anni per i quattro portafogli, S&P 500 total return e oro LBMA, 1976-2026." />
  <figcaption>Distribuzione del rendimento annuo composto su finestre di 5 anni, passo 3 mesi. 183 finestre per portafoglio.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | 5° perc. | 25° perc. | **Mediana** | 75° perc. | 95° perc. | finestre in perdita |
|---|---|---|---|---|---|---|
| 100% azionario | −1,60% | 8,19% | **13,78%** | 16,37% | 23,73% | **9,8%** |
| 90/10 | −0,20% | 8,54% | **12,96%** | 15,57% | 21,83% | 6,0% |
| 75/25 | 1,51% | 8,39% | **11,30%** | 14,71% | 19,04% | 1,6% |
| 50/50 | 3,41% | 6,91% | **9,87%** | 13,05% | 17,70% | 1,1% |

Cosa salta all'occhio:

- **A cinque anni il 100% azionario chiude in perdita nel 9,8% delle finestre**, 18 su 183. Sono i quinquenni che contengono il pieno dello scoppio della bolla internet o il pieno della crisi del 2008.
- **Il 50/50 chiude in perdita nell'1,1% delle finestre**, 2 su 183, e il 75/25 nell'1,6%. Il rischio di chiudere un quinquennio in rosso è sostanzialmente eliminato.
- **Il 5° percentile del 50/50 (3,41%) sta cinque punti sopra quello del tutto azionario (−1,60%).**

A cinque anni l'oro compra tranquillità in modo efficiente: paga circa quattro punti sulla mediana, ma elimina il rischio di chiusura negativa.

## Risultati su finestre di 20 anni: la convergenza

Con mezzo secolo di dati possiamo guardare anche le finestre ventennali, l'orizzonte consigliabile per un piano di accumulo:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/05_boxplot_cagr_20y.png" alt="Distribuzione del rendimento annuo composto su finestre mobili di 20 anni per i quattro portafogli, S&P 500 total return e oro LBMA, 1976-2026." />
  <figcaption>Distribuzione del rendimento annuo composto su finestre di 20 anni, passo 3 mesi. 123 finestre per portafoglio.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | 5° perc. | 25° perc. | **Mediana** | 75° perc. | 95° perc. |
|---|---|---|---|---|---|
| 100% azionario | 6,34% | 8,38% | **10,15%** | 13,07% | 17,35% |
| 90/10 | 6,60% | 8,27% | **10,02%** | 12,52% | 16,77% |
| 75/25 | 6,82% | 8,23% | **9,57%** | 11,59% | 15,79% |
| 50/50 | 6,91% | 7,83% | **8,94%** | 10,82% | 13,68% |

Su vent'anni i quattro portafogli **convergono in modo impressionante**:

- Le mediane vanno dal 10,15% del tutto azionario all'8,94% del 50/50: 121 punti base di distanza.
- I 5° percentili sono quasi identici, fra 6,34% e 6,91%: 57 punti base.
- **Nessuna finestra ventennale in perdita, per nessun portafoglio.**

Il dato è interessante perché ribalta l'impostazione abituale: a cinque e dieci anni l'oro vince chiaramente negli scenari peggiori, a venti la differenza si appiattisce. Il tempo lavora per l'azionario, perché dato abbastanza tempo anche il peggior decennio viene assorbito dal decennio successivo di recupero.

> Detto diversamente: **se hai davvero vent'anni davanti, la scelta fra 100% azionario e 90/10 è quasi indifferente sul rendimento finale, ma l'oro ti ha protetto lungo la strada.** È una decisione di tolleranza psicologica al calo, non di rendimento atteso.

## I drawdown: cosa succede lungo il percorso

Il rendimento finale è solo metà della storia. Il **drawdown massimo**, cioè il peggior calo subito dal portafoglio fra un picco e il minimo successivo, racconta cosa hai dovuto sopportare per arrivarci.

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/03_drawdown_distribution_5y.png" alt="Distribuzione cumulata del drawdown massimo osservato dentro ogni finestra di 5 anni, per i quattro portafogli." />
  <figcaption>Distribuzione cumulata del drawdown massimo osservato dentro ogni finestra di 5 anni. Più la curva è spostata a destra, verso cali meno profondi, meglio è.</figcaption>
</figure>

Frequenza dei cali profondi:

| Portafoglio | 5a ≤ −20% | 5a ≤ −30% | 10a ≤ −20% | 10a ≤ −30% | 20a ≤ −20% | 20a ≤ −30% |
|---|---|---|---|---|---|---|
| 100% azionario | 44,3% | 21,3% | 77,3% | 41,7% | **100%** | **81,3%** |
| 90/10 | 49,2% | 18,6% | 81,6% | 39,9% | **100%** | 81,3% |
| 75/25 | 48,6% | 13,7% | 81,6% | 33,1% | **100%** | 72,4% |
| 50/50 | 27,3% | 9,3% | 62,6% | 22,7% | **100%** | 63,4% |

Tre cose vanno notate:

- **Il 90/10 protegge poco dai cali.** Aggiungere un decimo di oro abbassa pochissimo la frequenza dei drawdown profondi, e sulla soglia del 20% è perfino leggermente peggio del tutto azionario, perché il 10% non basta a fare massa. La protezione vera arriva dal 25% in su.
- **Il 50/50 più che dimezza i cali gravi a cinque anni**, dal 21,3% al 9,3% delle finestre sotto il 30%.
- **A vent'anni nessuno sfugge a drowdown anche profondi.** Nel 100% delle finestre, per tutti e quattro i portafogli, c'è stato almeno un momento con un calo del 20% dal massimo. La probabilità di vedere un calo del 30% va dall'81,3% del tutto azionario al 63,4% del 50/50. Tradotto: se investi per vent'anni e la tua testa non regge un −40% lungo il tragitto, devi abbassare la quota azionaria *molto*, non basta diversificare con un 10 o 25% di oro. Altrimenti, devi accettare che quel brutto momento arriverà e che terrai duro.

## La curva del capitale

Per vedere il compromesso in forma cumulata, il grafico più parlante è il valore di un dollaro investito a inizio 1976:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/04_equity_curve.png" alt="Curva del capitale dei quattro portafogli dal 1976 al 2026, scala logaritmica: crescita di 1 dollaro investito a gennaio 1976 senza mai ribilanciare." />
  <figcaption>Crescita di 1 dollaro investito a gennaio 1976 con i pesi iniziali scelti, senza mai ribilanciare. Scala logaritmica.</figcaption>
</figure>

> **Come si legge questo grafico, è importante.** Come nell'articolo precedente, **questa è una sola simulazione, non una statistica.** Letteralmente: prendo 1 dollaro a gennaio 1976, lo divido secondo i pesi scelti, e non tocco più niente fino a giugno 2026. È *un* percorso possibile, *uno* specifico investitore che ha avuto la sorte (o la sfortuna) di cominciare proprio in quel mese. Le statistiche robuste stanno nelle finestre mobili qui sopra, 183 più 163 più 123, ognuna con il proprio punto di partenza. La curva del capitale serve a vedere cosa succede lungo un percorso reale: è didattica, non predittiva.

Riepilogo sull'intero periodo (gennaio 1976, giugno 2026):

| Portafoglio | Rendimento annuo composto | Volatilità annua | Drawdown massimo |
|---|---|---|---|
| 100% azionario | 12,08% | 15,01% | −50,95% |
| 90/10 | 11,87% | 14,57% | −49,96% |
| 75/25 | 11,51% | 14,24% | −48,07% |
| 50/50 | 10,75% | 14,04% | −42,92% |

Un dollaro investito nel gennaio 1976 diventa, dopo mezzo secolo:

- circa 317 dollari col 100% azionario
- circa 289 dollari col 90/10
- circa 246 dollari col 75/25
- circa 174 dollari col 50/50

Sembra una differenza enorme, ed è il risultato della capitalizzazione su cinquant'anni. Il montante finale del 50/50 è inferiore del 45% a quello del tutto azionario, meno di quanto suggerirebbe l'occhio guardando il solo rendimento annuo. Ciò è coerente con la decorrelazione: quando azioni e oro si muovono in modo indipendente, la combinazione compensa parte del rendimento perduto con la stabilità guadagnata.

> **Un dettaglio sulla volatilità.** La volatilità scende all'aumentare della quota di oro, ma pochissimo: dal 15,01% del tutto azionario al 14,04% del 50/50, meno di un punto per metà portafoglio spostato. Con correlazione praticamente nulla ci si aspetterebbe un calo molto più marcato. Il motivo è che l'oro porta con sé una volatilità propria del **16,18% annuo**, più alta di quella dell'azionario, e con un peso del 50% quel contributo pesa quanto il beneficio della decorrelazione. Chi aggiunge oro per "ridurre la volatilità" sta comprando la cosa sbagliata: quello che si compra è la protezione nelle code, non una curva più liscia.

## Lo stesso test visto da un portafoglio in euro

Tutto quello che precede è misurato in dollari su un indice americano, ed è il modo in cui questa domanda viene studiata quasi sempre, perché le serie storiche lunghe sono americane. Ma non è il portafoglio di chi investe dall'Italia, per due motivi che si sommano: l'azionario di riferimento è globale, non solo americano, e soprattutto la valuta di misura è l'euro.

Entrambi i punti contano, e vanno trattati insieme: il metallo è quotato in dollari, quindi **per chi misura in euro l'oro è anche una posizione in dollari**, e misurare un azionario globale in euro contro un oro in dollari sarebbe semplicemente sbagliato.

Ho quindi rifatto lo stesso test, con la stessa metodologia, su due azionari globali espressi in euro, con l'oro convertito in euro al cambio di fine mese: **MSCI World** da gennaio 1976, cioè lo stesso periodo di prima, e **MSCI ACWI IMI** da giugno 1994, che è la sua prima data disponibile.

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/06_eur_ventagli_10y.png" alt="Distribuzione del rendimento annuo composto su finestre mobili di 10 anni, in euro, per MSCI World dal 1976 e MSCI ACWI IMI dal 1994, nei quattro portafogli con oro." />
  <figcaption>Rendimento annuo composto su tutte le finestre di 10 anni, misurato in euro. A sinistra MSCI World dal 1976, a destra MSCI ACWI IMI dal 1994.</figcaption>
</figure>

**MSCI World più oro, in euro, 1976-2026**

| Portafoglio | Rendimento annuo | Volatilità | 10a 5° perc. | 10a mediana | decenni in perdita |
|---|---|---|---|---|---|
| 100% azionario | 9,84% | 14,61% | −1,40% | 10,15% | 8,0% |
| 90/10 | 9,66% | 14,19% | 1,10% | 9,87% | 4,9% |
| 75/25 | 9,34% | 13,85% | 3,12% | 8,83% | 0% |
| 50/50 | 8,69% | 13,60% | 3,93% | 7,86% | 0% |

**MSCI ACWI IMI più oro, in euro, 1994-2026**

| Portafoglio | Rendimento annuo | Volatilità | Drawdown massimo | 10a 5° perc. | decenni in perdita |
|---|---|---|---|---|---|
| 100% azionario | 8,27% | 14,47% | −53,10% | −1,86% | 11,2% |
| 90/10 | 8,24% | 13,34% | −51,16% | 0,14% | 5,6% |
| 75/25 | 8,18% | 11,90% | −47,67% | 2,86% | 0% |
| 50/50 | 8,09% | 10,41% | −39,52% | 4,94% | 0% |

Il secondo quadro è il risultato più forte di tutto l'articolo.

**Sull'ACWI in euro l'oro è quasi gratis.** Portare metà del portafoglio in oro costa **18 punti base l'anno** su trentadue anni, contro i 133 della stessa operazione sull'S&P 500 in dollari. In cambio il peggior 5% dei decenni passa da −1,86% a +4,94%, le finestre decennali chiuse in perdita passano dall'11,2% a zero, il drawdown massimo si riduce di quattordici punti e la volatilità scende di quattro punti pieni, dal 14,47% al 10,41%.

Da dove viene la differenza rispetto al caso americano? Non da un oro più generoso, come verrebbe da pensare. Negli stessi trentadue anni l'oro ha reso il **7,90% annuo in euro contro il 7,79% in dollari**: undici punti base di differenza, trascurabili. Il contributo del cambio al rendimento dell'oro, su questo periodo, è stato quasi nullo.

La differenza viene dall'altro lato del confronto, cioè da cosa stai rinunciando a tenere. L'azionario globale misurato in euro ha reso l'**8,27%** annuo, mentre l'S&P 500 misurato in dollari, negli stessi identici mesi, ha reso l'**11,16%**. Il costo di mettere oro in portafoglio dipende da quanto rende l'azionario che lasci fuori. 

Detto in modo meno tecnico: **non è che l'oro renda di più a chi vive in euro, è che il portafoglio azionario realistico di chi vive in euro ha reso molto meno dell'indice americano in dollari** che si usa di solito in questi studi. Su quel metro di paragone l'oro regge il confronto. Resta comunque vero che l'oro aggiunge esposizione al dollaro a chi misura in euro. In questi trentadue anni quell'esposizione non ha spostato il rendimento, ma chi tiene già molto azionario americano non coperto se la ritrova sommata a quella che ha già. Non è un argomento per non tenerne, è un argomento per sapere cosa si sta comprando.

### Quanto conta da dove si comincia

Questo è il controllo più importante dell'intero articolo, e serve a non prendere per legge di natura quello che è il prodotto di un periodo particolare. Gli anni Settanta contengono la fine di Bretton Woods e la riprezzatura dell'oro che ne è seguita, un evento irripetibile che non ha niente a che vedere con le proprietà di diversificazione del metallo.

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/08_eur_sensibilita.png" alt="Rendimento annuo composto fino a giugno 2026 dei quattro portafogli MSCI World più oro in euro, al variare della data di partenza fra il 1971 e il 2000." />
  <figcaption>MSCI World più oro in euro: rendimento annuo composto fino a giugno 2026 al variare del mese di partenza.</figcaption>
</figure>

| Partenza | 100% azionario | 90/10 | 75/25 | 50/50 |
|---|---|---|---|---|
| 1971 | 8,59% | 8,49% | 8,35% | 8,08% |
| 1976 | 9,84% | 9,66% | 9,34% | 8,69% |
| 1980 | 10,69% | 10,46% | 10,07% | 9,23% |
| 1990 | 7,97% | 7,86% | 7,68% | 7,35% |
| 2000 | 6,09% | 6,74% | 7,56% | 8,64% |

La lettura è netta. Partendo dal 1980, in piena disinflazione e con l'azionario a buon mercato, l'oro è costato 146 punti base. Partendo dal 2000, con l'azionario carissimo dopo la bolla internet, l'oro ne ha fatti guadagnare 255 e il 50/50 ha battuto il tutto azionario di due punti e mezzo l'anno per ventisei anni.

Non è un difetto dell'analisi, è la risposta alla seconda domanda che ci eravamo posti, quella sul *quando*: **l'oro paga nei periodi che cominciano con l'azionario caro e con la fiducia nelle valute in discussione, e costa negli altri.** Chi compra oro oggi sta implicitamente facendo una scommessa su quale dei due regimi somiglierà di più ai prossimi vent'anni.

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/07_eur_costo_protezione.png" alt="Confronto fra MSCI World e MSCI ACWI IMI in euro: rendimento annuo composto sull'intero periodo e rendimento del peggior 5% delle finestre decennali, per i quattro portafogli." />
  <figcaption>A sinistra quanto rende ogni allocazione sull'intero periodo, a destra quanto rende nel peggior 5% dei decenni. La distanza fra i due pannelli è il prezzo della protezione.</figcaption>
</figure>

## Quindi: ha senso? Quando? Quanto?

Riassumo i fatti che emergono dai dati:

1. **L'oro è empiricamente decorrelato dall'azionario** su mezzo secolo (correlazione mensile −0,039 in dollari, +0,018 col World in euro, −0,028 con l'ACWI in euro). Non è un argomento teorico, è un'osservazione robusta che si ripete su indici e valute diverse.
2. **Il costo in rendimento è basso**, soprattutto per quote piccole. In dollari il 90/10 perde 21 punti base l'anno e il 50/50 ne perde 133. In euro sull'ACWI il 50/50 ne perde 18.
3. **Negli scenari decennali peggiori l'oro protegge molto.** Il 5° percentile a dieci anni passa dall'1,54% al 6,37% in dollari e da −1,86% a +4,94% sull'ACWI in euro. Ogni allocazione con oro batte il tutto azionario nei casi peggiori.
4. **A vent'anni le distribuzioni convergono.** Le mediane stanno fra 8,94% e 10,15%, i 5° percentili fra 6,34% e 6,91%. Su orizzonti molto lunghi la scelta incide poco sul risultato finale.
5. **A nessun orizzonte si scappa da drowdown profondi.** A vent'anni il 100% delle finestre, per tutti i portafogli, ha visto almeno un calo del 20%, e dal 63% all'81% un calo del 30%.
6. **Il risultato dipende molto dal regime di partenza.** Dal 1980 l'oro costa, dal 2000 guadagna due punti e mezzo l'anno. Chi presenta un solo numero come "la" risposta sta nascondendo questa tabella.

**Quindi: ha senso?**

Sì, **probabilmente sì**, e in modo più netto rispetto alla quota obbligazionaria. Le ragioni:

- La decorrelazione storica è robusta e stabile, a differenza di quella fra azioni e obbligazioni, che cambia con i regimi di tasso.
- Il costo in rendimento è basso per quote piccole e medie (fino al 25%), e per chi misura in euro è quasi nullo anche a quote alte.
- La protezione nelle code è rilevante e si vede su tutti e tre gli universi testati.
- L'oro si comporta diversamente dalle obbligazioni nei regimi di inflazione alta: fra il 1976 e il 1980, e di nuovo fra il 2022 e il 2024, le obbligazioni hanno perso e l'oro ha tenuto o guadagnato. È una copertura ortogonale a quella obbligazionaria, non un suo sostituto.

**Quanto?**

I dati indicano che il punto di equilibrio sta fra il 10% e il 25%:

- **10%**: costo quasi nullo (21 punti base in dollari), protezione moderata ma reale nelle code (il 5° percentile a dieci anni sale dall'1,54% al 4,14%). È la scelta predefinita per chi vuole un pizzico di diversificazione senza pagare un costo visibile. Ma attenzione: sui drawdown non protegge quasi per niente.
- **25%**: costo contenuto (57 punti base in dollari), protezione netta nelle code (5° percentile al 5,87%, vicino al massimo ottenibile) e qui comincia anche la protezione vera sui cali. Questa allocazione, su questi dati, massimizza il rapporto fra protezione e costo opportunità.
- **50%**: protezione massima, costo alto in dollari (133 punti base) ma sorprendentemente basso in euro sull'azionario globale (18 punti base sull'ACWI). Ha senso per chi è particolarmente avverso a drowdown profondi.

**Per chi?**

**L'oro ha senso in modo più trasversale, anche in accumulo.** Una quota piccola, fra il 10 e il 25%, può restare in portafoglio per tutta la sua vita senza penalizzare in modo sensibile il rendimento atteso, e protegge dai regimi macroeconomici che azioni e obbligazioni insieme gestiscono male, cioè inflazione alta e crisi di fiducia istituzionale.

## In sintesi

1. **L'oro è un diversificatore vero**, non di facciata. La correlazione mensile con l'azionario è praticamente nulla su tutti e tre gli universi testati, e questo vale più di qualunque argomento teorico.
2. **Una quota fra il 10 e il 25% protegge le code a dieci anni a un costo ridotto.** Il 90/10 alza il 5° percentile di due punti e mezzo pagandone 21 centesimi.
3. **Chi ragiona in euro paga molto meno.** Sull'ACWI in euro metà portafoglio in oro costa 18 punti base l'anno e azzera i decenni in perdita. Non perché l'oro renda di più in euro (7,90% contro 7,79% in dollari), ma perché l'azionario globale in euro ha reso l'8,27% contro l'11,16% dell'S&P 500 in dollari: con un azionario che rende meno, l'oro costa meno.
4. **A vent'anni le distribuzioni convergono**: mediane fra 8,94% e 10,15%, 5° percentili fra 6,34% e 6,91%. Su orizzonti davvero lunghi la scelta cambia poco il risultato e molto il viaggio.
5. **A nessun orizzonte si scappa dai cali profondi.** "Sul lungo non c'è rischio" è un mito: il rischio cambia natura, diventa rischio di sopportare un calo lungo la strada invece che rischio di chiudere in perdita.
6. **Il risultato dipende dal regime di partenza**, e di parecchio: dal 1980 l'oro costa 146 punti base, dal 2000 ne fa guadagnare 255.
7. **L'oro resta un asset speculativo in senso tecnico**, senza flussi e senza valore intrinseco calcolabile, ma questa critica non cancella il fatto empirico che la sua decorrelazione è reale e persistente.
8. Una piccola quota strutturale di oro non è una scelta esotica: sui dati è una decisione metodologicamente difendibile per quasi qualunque profilo.

---

### Fonti e riproducibilità

- Dati S&P 500: indice S&P 500 Total Return per la parte dal 1988; prima, prezzo S&P 500 e dividendo mensile dal [dataset Shiller](http://www.econ.yale.edu/~shiller/data.htm) (file `ie_data.xls`, copia CSV su [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500)).
- Dati oro LBMA mensili in dollari per oncia: copia CSV su [datasets/gold-prices](https://github.com/datasets/gold-prices). FRED ha dismesso le serie LBMA da gennaio 2022, dopo la revoca della licenza da parte di ICE Benchmark Administration.
- Indici azionari globali in euro: MSCI World total return dal 1969 e MSCI ACWI IMI total return dal 1994.
- Cambio EUR/USD: BCE via FRED (serie `DEXUSEU`) dal 1999; marco tedesco per dollaro (serie `EXGEUS`) convertito a 1,95583 per il periodo precedente.
- Codice: [`scripts/ha-senso-oro-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-oro-portafoglio.py) e [`scripts/oro-portafoglio-indici-eur.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/oro-portafoglio-indici-eur.py).
- Dati grezzi dei quattro portafogli: [`/charts/ha-senso-oro-portafoglio/data.csv`](/charts/ha-senso-oro-portafoglio/data.csv).
- Riepilogo numerico completo: [`/charts/ha-senso-oro-portafoglio/summary.json`](/charts/ha-senso-oro-portafoglio/summary.json) e [`/charts/ha-senso-oro-portafoglio/summary_eur.json`](/charts/ha-senso-oro-portafoglio/summary_eur.json).
