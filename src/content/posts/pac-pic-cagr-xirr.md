---
category: "le-basi"
title: "PAC o PIC, CAGR e XIRR: come si misura davvero un rendimento"
description: "Undicesimo episodio delle basi: cosa sono PIC e PAC, perché il CAGR non funziona sui versamenti periodici, e perché un backtest che parte da una sola data non dimostra niente."
pubDate: 2026-10-14
tags: ["le-basi", "pac", "pic", "cagr", "xirr", "rendimento", "backtest", "principianti"]
author: "SmartMoneyLab"
series: "le-basi"
seriesOrder: 11
simulationSlug: "pac-pic-cagr-xirr"
seoImage: "/charts/pac-pic-cagr-xirr/01_pic_pac.png"
faq:
  - q: "Qual è la differenza fra PIC e PAC?"
    a: |-
      Il PIC, o lump sum, è un versamento unico: metti una cifra sul mercato in un colpo solo. Il PAC, piano di accumulo, è una serie di versamenti ripetuti nel tempo, per esempio cento euro al mese. Non sono due strumenti diversi: è lo stesso investimento, con il denaro che entra in due modi diversi, e per questo si misurano con formule diverse.
  - q: "Cos'è il CAGR?"
    a: |-
      È il rendimento annuo composto: il tasso costante che, applicato ogni anno, porta dal valore iniziale a quello finale. Serve a rendere confrontabili periodi di lunghezza diversa. Funziona bene su un versamento unico e non funziona su un piano di accumulo, perché presuppone che tutto il denaro sia entrato il primo giorno.
  - q: "Perché serve l'XIRR per un piano di accumulo?"
    a: |-
      Perché in un PAC ogni euro resta investito per un tempo diverso: quello del primo mese lavora per tutta la durata, quello dell'ultimo per nulla. L'XIRR è il tasso annuo che tiene conto della data di ogni versamento. Su un PAC da cento euro al mese per vent'anni sul mercato mondiale, l'XIRR è l'11,85% annuo, mentre dividere il guadagno per gli anni darebbe il 13,70% e applicare la formula del CAGR al totale versato darebbe il 6,83%.
  - q: "Meglio media o mediana per leggere un backtest?"
    a: |-
      La mediana, quasi sempre. La media si lascia spostare dai casi estremi, la mediana no: è il risultato che divide a metà i casi, metà sopra e metà sotto. Meglio ancora è guardarle insieme ai percentili, perché la distanza fra il 5° e il 95° dice quanto il risultato dipende dalla fortuna.
  - q: "Cosa sono le finestre mobili in un backtest?"
    a: |-
      Sono tutti i periodi possibili di una certa durata dentro la storia disponibile, non solo uno. Sul mercato mondiale esistono 440 finestre di vent'anni: la migliore ha reso il 17,5% annuo, la peggiore il 2,5%. Un backtest che ne sceglie una sola misura la data di partenza, non la strategia.
draft: false
---

## In breve

Con l'episodio 10 si chiude la parte su cosa comprare e quanto rischio si prende. Il blocco D riguarda **come si leggono i numeri**, i nostri compresi, e comincia da quello che sembra il più semplice di tutti: **il rendimento**.

Sembra semplice finché i soldi entrano una volta sola. Appena entrano un po' per volta, cioè nel modo in cui investe la maggioranza delle persone, la domanda "quanto ho guadagnato all'anno" smette di avere una risposta ovvia, e tre formule plausibili danno tre numeri molto diversi.

Tre cose che il resto dell'episodio mostra sui dati:

1. **Lo stesso identico piano di accumulo può essere descritto come un 6,83%, un 11,85% o un 13,70% annuo.** Due di questi numeri sono sbagliati, e sono quelli che si leggono più spesso.
2. **Il miglior ventennio del mercato mondiale ha reso il 17,5% annuo, il peggiore il 2,5%.** Diecimila euro diventano 249.923 euro nel primo caso e 16.432 nel secondo. Stesso indice: cambia solo il mese in cui entri.
3. **Su finestre di un anno il 26% dei casi chiude in perdita, su finestre di vent'anni nessuno.** È la stessa serie storica, letta su orizzonti diversi.

## Cos'è un rendimento, e perché la domanda non è banale

Un rendimento mette in rapporto due cose: **quanto hai messo** e **quanto ti sei ritrovato**. Se metti 1.000 euro e dopo un anno ne hai 1.100, hai guadagnato il 10%, e non serve altro.

Le complicazioni arrivano tutte insieme appena si esce da questo caso.

**La prima è il tempo.** Un più 50% non si giudica senza sapere in quanti anni. Serve un modo di esprimere il risultato **per anno**, e serve che tenga conto del fatto che i guadagni si reinvestono.

**La seconda è che il denaro entra in momenti diversi.** Se versi ogni mese, non esiste un "quanto hai messo" unico: ci sono quaranta, cento, duecento versamenti, ciascuno rimasto investito per un tempo diverso.

Le due complicazioni hanno due soluzioni diverse, e usare quella sbagliata è l'errore più comune che si incontra nei post sugli investimenti.

## PIC e PAC: due modi in cui il denaro entra

**PIC** sta per Piano di Investimento di Capitale, in inglese *lump sum*: un versamento unico. Hai una cifra, la metti sul mercato, la lasci lì.

**PAC** sta per Piano di Accumulo del Capitale: versamenti ripetuti a intervalli regolari, tipicamente ogni mese. È il modo in cui investe chi mette da parte una quota dello stipendio, e corrisponde alla situazione descritta nell'episodio 2, dove il denaro da investire è quello che avanza dopo il fondo di emergenza e le spese già previste.

Non sono due strumenti né due strategie diverse: **è lo stesso investimento, con il denaro che entra in due modi diversi**. La differenza che conta per questo episodio è una sola: nel PIC tutto il capitale resta investito per tutto il periodo, nel PAC ogni euro resta investito per un tempo diverso.

## Il CAGR: trasformare un percorso in un tasso

Il **CAGR**, rendimento annuo composto, è il tasso costante che, applicato anno dopo anno, porta dal valore iniziale a quello finale. Se 10.000 euro diventano 20.000 in dieci anni, il CAGR non è il 10% annuo, cioè il 100% diviso dieci: è il **7,18%**, perché ogni anno il guadagno si somma al capitale e l'anno dopo rende anche lui.

Serve a una cosa sola, e la fa bene: **rendere confrontabili periodi di lunghezza diversa**. Senza il CAGR non si può dire se un più 80% in sei anni sia meglio o peggio di un più 120% in dieci.

Ha però un limite che vale la pena dire subito, perché è lo stesso dell'episodio precedente: **il CAGR non dice niente del percorso**. Due investimenti con lo stesso CAGR possono aver avuto storie opposte, uno in salita regolare e l'altro con un meno 50% nel mezzo. Il CAGR è il punto di arrivo diviso il punto di partenza, e tutto quello che è successo in mezzo sparisce. È il motivo per cui l'[episodio 10](/posts/rischio-volatilita-diversificazione) esiste.

## Il PAC rompe il CAGR, e serve l'XIRR

Qui arriva l'errore vero. Prendiamo un caso concreto: **cento euro al mese per vent'anni sul mercato mondiale**, da agosto 2006 a luglio 2026. Versati 24.000 euro, ritrovati **89.499 euro**.

Il guadagno sul versato è del **272,9%**. E ora, quanto fa all'anno?

**Primo tentativo: dividere per gli anni.** 272,9 diviso 20 fa 13,70% all'anno. È il conto che si vede più spesso, e **è sbagliato due volte**: ignora che i guadagni si compongono, e soprattutto tratta i 24.000 euro come se fossero stati tutti sul mercato per vent'anni, quando l'ultimo versamento ci è stato per un mese.

**Secondo tentativo: applicare la formula del CAGR al totale versato.** Il risultato è 6,83% all'anno. Anche questo è sbagliato, e nella direzione opposta: la formula presuppone che i 24.000 euro fossero sul mercato dal primo giorno, quindi attribuisce a vent'anni di lavoro un capitale che in media c'è stato per metà del tempo. Il rendimento risulta molto più basso del vero.

**La misura corretta è l'XIRR**, il tasso interno di rendimento con flussi datati: il tasso annuo che, applicato a **ogni versamento a partire dalla sua data**, porta esattamente al montante finale. Pesa ogni euro per il tempo in cui è stato davvero investito. Su questo PAC l'XIRR è l'**11,85% annuo**.

<figure>
  <img src="/charts/pac-pic-cagr-xirr/01_pic_pac.png" alt="Due pannelli. In alto le curve di valore di un PIC da 24.000 euro e di un PAC da 100 euro al mese dal 2006 al 2026, con l'area grigia del versato cumulato: il PIC arriva a 138.621 euro, il PAC a 89.499. In basso tre barre orizzontali con i tre modi di misurare il rendimento dello stesso PAC: 13,70% e 6,83% in rosso, 11,85% in verde." width="2039" height="1680" decoding="async" />
  <figcaption>Stesso mercato e stessi 24.000 euro, due modi di entrare. In basso, lo stesso PAC misurato in tre modi: due sbagliati e uno corretto.</figcaption>
</figure>

In pratica l'XIRR si calcola con una funzione di foglio di calcolo che si chiama proprio così, `XIRR` in inglese e `TIR.X` in italiano: le si dà la lista dei versamenti con le rispettive date, più il valore finale con segno opposto, e restituisce il tasso annuo. Chi ha un PAC può misurarne il rendimento vero in cinque minuti, ed è un esercizio che consiglio, perché quasi sempre il numero è diverso da quello che l'applicazione dell'intermediario mostra in home page.

## Attenzione: non è una gara

Nel grafico il PIC arriva a 138.621 euro e il PAC a 89.499. **Questo non dimostra che il PIC sia meglio**, e vale la pena fermarsi un attimo, perché è esattamente il genere di confronto che viene usato male.

I due numeri non sono confrontabili per una ragione banale: nel PIC i 24.000 euro sono stati investiti per vent'anni, nel PAC in media per circa dieci. Con metà del tempo a disposizione, un montante più basso è matematica, non un verdetto.

E infatti, guardando i tassi invece dei montanti, la classifica si rovescia: l'XIRR del PAC è l'**11,85%**, il CAGR del PIC il **9,20%**. In questo periodo specifico i versamenti mensili hanno comprato a prezzi mediamente più bassi di quello di agosto 2006, perché subito dopo è arrivato il 2008. **Anche questo non è un verdetto**: in un periodo che parte da un minimo, il risultato si ribalta di nuovo.

La domanda "conviene il PAC o il PIC" dipende dal periodo, dall'orizzonte e da quanto denaro si ha già disponibile, e merita uno studio con i dati su tutte le finestre storiche, non un esempio. Qui serviva solo mostrare **perché le due cose non si misurano con lo stesso strumento**.

## Media, mediana, percentili

Fin qui abbiamo misurato un singolo percorso. Quando invece se ne misurano centinaia, come fa ogni backtest serio, serve un modo di riassumerli.

**La media** è la somma divisa per il numero di casi. Ha un difetto noto: si lascia spostare dagli estremi. Pochi casi eccezionali in una direzione la trascinano, e il numero smette di descrivere il caso tipico.

**La mediana** è il valore che divide i casi a metà: metà sopra, metà sotto. Non le importa di quanto siano estremi gli estremi, solo di quanti siano. Per descrivere "cosa è successo di solito" è quasi sempre la misura giusta, ed è quella che questo sito usa come riferimento.

Che le due non coincidano, e in che direzione, dice già qualcosa. Sul mercato mondiale, sulle finestre di **tre anni** la media è il 9,01% e la mediana il **10,70%**: la media sta più in basso, trascinata da pochi triennî molto negativi. Sulle finestre di **vent'anni** si inverte, media 8,62% e mediana 7,96%: qui sono pochi ventennî eccezionalmente buoni a tirare su la media.

**I percentili** completano il quadro, e sono il motivo per cui su questo sito trovi scritto p5 o p95. Il 5° percentile è il valore sotto il quale cade solo il 5% dei casi, il 95° quello sopra il quale ne cade il 5%. Letti insieme dicono **quanto il risultato dipende dalla fortuna**: una mediana del 10% con il 5° percentile al 9% e una mediana del 10% con il 5° percentile al meno 20% descrivono due investimenti che non hanno niente in comune.

## Le finestre mobili, e perché sono l'unico modo onesto

Veniamo alla tecnica che sta sotto quasi tutti gli articoli quantitativi di questo sito.

Un backtest consiste nell'applicare una regola ai dati del passato e guardare cosa sarebbe successo. Il problema è che **deve cominciare in un giorno preciso**, e quel giorno viene scelto da chi scrive. Chi sceglie la data sceglie, in larga misura, il risultato.

Non è un sospetto, è una cosa che si misura. Ecco il rendimento annuo composto dei **vent'anni successivi** a ciascun mese di partenza, su tutta la storia disponibile del mercato mondiale.

<figure>
  <img src="/charts/pac-pic-cagr-xirr/02_finestre_mobili.png" alt="Grafico a linea del rendimento annuo composto dei vent'anni successivi in funzione del mese di partenza, dal 1969 al 2006. La curva oscilla fra il 2,5% e il 17,5%, con il massimo a marzo 1980 e il minimo a marzo 2000. Una linea tratteggiata segna la mediana all'8,0%." width="2080" height="1240" decoding="async" />
  <figcaption>Rendimento annuo composto dei vent'anni successivi a ciascun mese di partenza, MSCI World in euro. Ogni punto è un investitore che è entrato in un mese diverso.</figcaption>
</figure>

Lo stesso indice, lo stesso orizzonte di vent'anni, nessuna strategia, nessuna scelta di titoli. **Chi è entrato a marzo 1980 ha ottenuto il 17,5% annuo. Chi è entrato a marzo 2000 ha ottenuto il 2,5%.** Su 10.000 euro sono 249.923 euro contro 16.432.

Un articolo che scegliesse marzo 1980 come data di inizio potrebbe dimostrare quasi qualunque cosa, e il lettore non avrebbe modo di accorgersene. È per questo che la regola metodologica di questo sito è una sola: **non si usa una finestra, si usano tutte**. Nel mercato mondiale ci sono **440 finestre ventennali** distinte, e il risultato che pubblichiamo è la loro distribuzione, non il risultato di una di esse.

È anche il motivo per cui le conclusioni qui sono meno nette di quelle che si leggono altrove. Una distribuzione dice "nella metà dei casi è andata così, nel 5% peggiore così", e non si presta a un titolo entusiasta. In compenso è vera.

## Quanto si stringe il ventaglio con l'orizzonte

Un'ultima cosa, che collega questo episodio a tutti i precedenti: la dispersione dei risultati **dipende dall'orizzonte in modo drastico**.

<figure>
  <img src="/charts/pac-pic-cagr-xirr/03_percentili.png" alt="Grafico a ventaglio con il rendimento annuo composto per orizzonti di 1, 3, 5, 10, 20 e 30 anni. La banda dal 5° al 95° percentile va da meno 25,1% a più 40,4% a un anno e si restringe fino a 6,8%-10,8% a trent'anni. Media e mediana restano intorno al 9%." width="2039" height="1280" decoding="async" />
  <figcaption>Percentili del rendimento annuo composto per orizzonte, su tutte le finestre mobili disponibili. La mediana si muove poco, il ventaglio si chiude.</figcaption>
</figure>

**A un anno** il 5° percentile è meno 25,1% e il 95° più 40,4%: un ventaglio di sessantacinque punti, e il **26% delle finestre chiude in perdita**. Su un anno il mercato azionario non è un investimento, è un lancio di dadi con un'inclinazione favorevole.

**A dieci anni** il ventaglio è meno 1,3% / più 18,6%, e le finestre in perdita sono il 7,3%.

**A vent'anni** il peggior caso su venti è un più 4,1% annuo, e **nessuna finestra chiude in perdita**.

**A trent'anni** il ventaglio è fra il 6,8% e il 10,8%, cioè quattro punti in tutto.

Nota che **la mediana si muove pochissimo**, fra il 7,96% e il 10,70% a seconda dell'orizzonte. Quello che cambia radicalmente non è quanto ci si può aspettare: è **quanto ci si può fidare dell'aspettativa**. Ed è la traduzione quantitativa della cosa che gli episodi 2 e 3 dicevano a parole: l'orizzonte non cambia il rendimento atteso, cambia la probabilità di incassarlo.

Un'avvertenza doverosa su questi numeri: le finestre mobili si sovrappongono quasi tutte fra loro, quindi non sono osservazioni indipendenti, e i percentili vanno letti come descrizione di quello che è successo, non come probabilità future. La storia disponibile resta una sola.

## Come leggere i numeri di questo sito

Riassunto operativo, da tenere a mente quando leggi un qualsiasi articolo qui o altrove.

1. **Se il rendimento è annuo, chiediti se è composto.** "Più 272% in vent'anni" e "13,7% all'anno" sono lo stesso dato presentato in due modi, e il secondo è sbagliato.
2. **Se ci sono versamenti periodici, il numero giusto è l'XIRR.** Se non lo è, quasi sempre il rendimento è gonfiato.
3. **Se trovi un backtest con una sola data di partenza, trattalo come un aneddoto.** Chiedi la distribuzione.
4. **Preferisci la mediana alla media**, e cerca i percentili: senza il 5° percentile non sai cosa stai rischiando.
5. **Guarda l'orizzonte prima del rendimento.** Un numero a un anno e lo stesso numero a vent'anni dicono cose diverse.

## Quello che questo episodio non dice

**Non dice se conviene il PAC o il PIC.** Dipende dal periodo e dalla situazione di partenza, e richiede il conto su tutte le finestre storiche.

**Non mette insieme rendimento e rischio.** Sharpe, Sortino e Calmar sono l'episodio 12.

**Non parla di rendimenti netti.** Costi e imposte sono l'[episodio 9](/posts/quanto-costa-investire-ter-commissioni), e il conto completo su finestre mobili sta in [Quanto rende davvero l'azionario al netto di tasse e costi](/posts/quanto-rende-azionario-netto-tasse-costi).

**Non parla di inflazione.** I rendimenti qui sono nominali: per il potere d'acquisto vale l'[episodio 1](/posts/perche-investire-inflazione).

## Il prossimo episodio

Sai misurare un rendimento e sai misurare un rischio. L'episodio 12 li mette insieme: **Sharpe, Sortino e Calmar**, cosa dicono davvero, e perché un indicatore alto non basta a scegliere un investimento.

## Fonti e metodo

- Serie di mercato: `data/Msci_world/Msci_world_1969_EUR.csv`, MSCI World in euro, mensile, da dicembre 1969 a luglio 2026, 680 osservazioni. Serie total return, dividendi reinvestiti, al lordo di costi e imposte: qui interessa la misura, non il netto.
- Il confronto PIC e PAC usa i 240 mesi da agosto 2006 a luglio 2026, rata di 100 euro al primo valore disponibile di ogni mese, nessun costo di negoziazione. Aggiungere i costi cambierebbe entrambi i numeri nella stessa direzione e non cambierebbe il punto dell'esempio, che riguarda la formula e non il livello.
- XIRR calcolato per bisezione sul tasso mensile e poi annualizzato: con versamenti tutti dello stesso segno la soluzione è unica, quindi non serve un metodo più sofisticato.
- Finestre mobili: tutte le finestre di 1, 3, 5, 10, 20 e 30 anni disponibili nella serie, con passo di un mese. Si sovrappongono, quindi non sono osservazioni indipendenti: i percentili descrivono il passato e non sono una previsione.
- Le 440 finestre ventennali sono le stesse usate in [Quanto rende davvero l'azionario al netto di tasse e costi](/posts/quanto-rende-azionario-netto-tasse-costi) e nell'[episodio 9](/posts/quanto-costa-investire-ter-commissioni).
- Lo script contiene tre controlli che fanno fallire la generazione se le affermazioni dell'articolo cadono: l'ordine dei tre modi di misurare il PAC, l'assenza di finestre ventennali negative e il restringimento della dispersione con l'orizzonte.
- Codice che genera grafici e numeri: `scripts/pac-pic-cagr-xirr.py`, output in `public/charts/pac-pic-cagr-xirr/summary.json`.
