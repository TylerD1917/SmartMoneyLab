---
category: "le-basi"
title: "Sharpe, Sortino e Calmar: giudicare un portafoglio (e i loro limiti)"
description: "Dodicesimo episodio delle basi: come si costruiscono gli indicatori aggiustati per il rischio, cosa guarda ciascuno al denominatore e come si leggono i loro valori."
pubDate: 2026-10-15
tags: ["le-basi", "sharpe", "sortino", "calmar", "rischio", "rendimento", "principianti"]
author: "SmartMoneyLab"
series: "le-basi"
seriesOrder: 12
simulationSlug: "sharpe-sortino-calmar"
seoImage: "/charts/sharpe-sortino-calmar/01_tre_denominatori.png"
faq:
  - q: "Cos'è l'indice di Sharpe?"
    a: |-
      È il rendimento in eccesso rispetto al tasso privo di rischio, diviso la volatilità. Risponde alla domanda "quanto premio ho ottenuto per ogni unità di oscillazione". Sull'S&P 500 fra il 2002 e il 2026, con un rendimento in eccesso del 10,02% annuo e una volatilità del 14,72%, lo Sharpe è 0,68.
  - q: "Che differenza c'è fra Sharpe e Sortino?"
    a: |-
      Cambia solo il denominatore. Lo Sharpe divide per la volatilità, che misura tutta la dispersione dei rendimenti, comprese le sorprese positive. Il Sortino divide per la semideviazione, che considera solo i mesi in perdita. Per come è costruito, il Sortino dello stesso investimento è quasi sempre più alto dello Sharpe: sull'S&P 500 sono 1,05 contro 0,68.
  - q: "Cos'è l'indice di Calmar?"
    a: |-
      È il rendimento annuo composto diviso il massimo drawdown, cioè la perdita più profonda subita dal picco precedente. Giudica l'investimento dal suo caso peggiore effettivamente accaduto invece che dalla sua oscillazione media. Sull'S&P 500 è 0,22, perché a un rendimento dell'11,28% annuo corrisponde una caduta massima del 50,8%.
  - q: "Qual è un buon valore dell'indice di Sharpe?"
    a: |-
      Non esiste una soglia valida sempre, perché il valore dipende dal periodo osservato. Come riferimento empirico, sulle ventidue asset class misurate in questo articolo su ventiquattro anni lo Sharpe va da 0,17 a 0,80, con una mediana di 0,45. Un numero va sempre letto accanto al periodo e a un termine di paragone calcolato sullo stesso periodo.
  - q: "Perché lo stesso investimento ha indici di Sharpe diversi?"
    a: |-
      Perché l'indicatore descrive un periodo, non una proprietà permanente dell'investimento. L'oro ha uno Sharpe di 0,96 fra il 2003 e il 2007 e di meno 0,07 fra il 2013 e il 2019. I Treasury americani a lunga scadenza passano da più 0,39 fra il 2013 e il 2019 a meno 0,52 dal 2020. Senza il periodo accanto, il numero non è un dato.
draft: false
---

## In breve

Negli ultimi due episodi hai imparato a misurare separatamente le due cose che contano: il **rendimento**, con il CAGR e l'XIRR, e il **rischio**, con volatilità, drawdown e tempo di recupero.

Tenerle separate funziona finché i casi sono pochi. Appena devi confrontare quattro o cinque alternative, guardare due numeri alla volta diventa scomodo, e la domanda diventa un'altra: **quanto rendimento ho ottenuto per ogni unità di rischio che ho preso?**

È la domanda a cui rispondono Sharpe, Sortino e Calmar. Questo episodio spiega come sono fatti e come si leggono.

Tre cose da portarsi via:

1. **Sono la stessa frazione.** Rendimento in eccesso sopra, misura di rischio sotto. Cambia solo cosa metti al denominatore.
2. **Le tre scale non si confrontano fra loro.** Un Sortino è quasi sempre più alto dello Sharpe dello stesso investimento, per costruzione, non perché l'investimento sia migliore visto in quel modo.
3. **Descrivono un periodo, non un investimento.** L'oro ha uno Sharpe di 0,96 in un quinquennio e di meno 0,07 in un altro.

## Perché mettere rendimento e rischio in una frazione

Immagina due fondi: il primo ha reso il 9% annuo, il secondo il 12%. Il secondo è migliore?

Senza sapere altro, non si può dire. Se il primo ha oscillato del 6% all'anno e il secondo del 25%, il secondo ha chiesto molto di più a chi lo teneva per ottenere tre punti in più. Qualcuno li considererà ben spesi, qualcuno no, ma la domanda è legittima e ha bisogno di un numero.

L'idea degli indicatori aggiustati per il rischio è semplice: **dividere il rendimento per il rischio**, così da ottenere una misura di "quanto rende la sofferenza". La frazione risultante non dice se un investimento è buono, dice **quanto rendimento è stato prodotto per unità di rischio** in quel periodo, che è una cosa più modesta e più utile.

Tutti e tre gli indicatori di questo episodio hanno la stessa forma:

```
indicatore = rendimento in eccesso / misura di rischio
```

Il numeratore è quasi sempre lo stesso. **È il denominatore che cambia**, ed è l'unica cosa che distingue Sharpe, Sortino e Calmar.

## Il numeratore: il rendimento in eccesso

Al numeratore non va il rendimento, ma il **rendimento in eccesso** rispetto al tasso privo di rischio, cioè quello che si ottiene prestando denaro a brevissimo termine a chi non fallisce.

Il motivo è intuitivo. Se i titoli di Stato a breve rendono il 4% senza oscillare, un investimento che rende il 4% ballando non ha prodotto niente che valga il disturbo: lo stesso risultato era disponibile stando fermi. Quello che si vuole misurare è **il premio per aver corso un rischio**, non il rendimento totale.

Nell'esempio che useremo per tutto l'episodio, l'S&P 500 fra agosto 2002 e agosto 2026, il rendimento annuo composto è stato l'**11,28%** e il tasso privo di rischio medio del periodo l'**1,81%**. Il rendimento in eccesso, calcolato mese per mese e poi annualizzato, è il **10,02%** annuo. È questo il numero che sta sopra la linea di frazione.

Il Calmar fa eccezione: per convenzione usa il rendimento pieno, non quello in eccesso. È una differenza di convenzione, non di sostanza, ma va saputa quando si confrontano numeri presi da fonti diverse.

## Il denominatore: tre modi di misurare il rischio

Qui sta tutto l'episodio. Prendiamo la stessa identica serie di rendimenti mensili e guardiamola tre volte.

<figure>
  <img src="/charts/sharpe-sortino-calmar/01_tre_denominatori.png" alt="Tre pannelli affiancati sugli stessi rendimenti mensili dell'S&P 500 dal 2002 al 2026. A sinistra tutte le barre con la banda della volatilità al 14,7%. Al centro le stesse barre con i soli mesi negativi evidenziati in rosso e la semideviazione al 9,6%. A destra la curva del valore in scala logaritmica con evidenziata la caduta del 50,8% fra il 2007 e il 2009." width="2520" height="1080" decoding="async" />
  <figcaption>Gli stessi ventiquattro anni dell'S&P 500. Ogni indicatore guarda una porzione diversa della stessa storia.</figcaption>
</figure>

### Sharpe: tutta la dispersione

L'**indice di Sharpe** mette al denominatore la **volatilità**, cioè la deviazione standard dei rendimenti annualizzata. Guarda quanto i rendimenti mensili si allontanano dalla loro media, **in entrambe le direzioni**.

Sull'S&P 500 la volatilità del periodo è il **14,72%**. Quindi:

```
Sharpe = 10,02 / 14,72 = 0,68
```

Si legge così: per ogni punto di oscillazione sopportata, l'investimento ha prodotto 0,68 punti di premio sopra il tasso privo di rischio.

Il limite è quello già visto nell'[episodio 10](/posts/rischio-volatilita-diversificazione): un mese a più 8% pesa sul denominatore esattamente quanto un mese a meno 8%, e un investimento che sale a scatti viene penalizzato come uno che scende a scatti. Nel pannello di sinistra del grafico, la banda azzurra comprende sia le barre sopra lo zero sia quelle sotto.

### Sortino: solo i mesi in perdita

L'**indice di Sortino** nasce esattamente da questa obiezione. Al denominatore mette la **semideviazione**, che si calcola come la volatilità ma **considerando solo i rendimenti negativi**: i mesi positivi entrano nel conto come zeri.

Sull'S&P 500 la semideviazione è il **9,56%**, nettamente più bassa della volatilità perché i mesi positivi, che erano più della metà, smettono di contare come rischio. Quindi:

```
Sortino = 10,02 / 9,56 = 1,05
```

Da qui una conseguenza importante e spesso fraintesa: **il Sortino di un investimento è quasi sempre più alto del suo Sharpe**. Non perché l'investimento sia migliore secondo Sortino, ma perché il denominatore è più piccolo per costruzione. Confrontare lo Sharpe di un fondo con il Sortino di un altro non significa niente.

### Calmar: la caduta più profonda

L'**indice di Calmar** cambia prospettiva. Al denominatore non mette una misura di oscillazione ma il **massimo drawdown**, cioè la perdita più grande subita rispetto al massimo precedente. Al numeratore, per convenzione, il rendimento annuo composto pieno.

Sull'S&P 500 il massimo drawdown del periodo è stato il **50,78%**, fra l'ottobre 2007 e il febbraio 2009. Quindi:

```
Calmar = 11,28 / 50,78 = 0,22
```

La differenza concettuale è che Sharpe e Sortino descrivono **come è stato il viaggio in media**, mentre il Calmar descrive **quanto è stato brutto il momento peggiore**. Due investimenti con la stessa volatilità possono avere Calmar molto diversi se uno dei due ha avuto una singola caduta rovinosa.

Nel pannello di destra del grafico il tratto verde è l'unica cosa che il Calmar guarda: tutto il resto dei ventiquattro anni, per lui, non esiste.

## Gli stessi tre indicatori su sei asset

Ecco i tre numeri calcolati su sei investimenti noti, sullo stesso periodo.

<figure>
  <img src="/charts/sharpe-sortino-calmar/02_sei_asset.png" alt="Grafico a barre raggruppate con Sharpe, Sortino e Calmar per S&P 500, Nasdaq 100, beni di consumo, oro, Giappone e Treasury USA 20+. In ogni gruppo la barra del Sortino è la più alta e quella del Calmar la più bassa." width="2120" height="1200" decoding="async" />
  <figcaption>I tre indicatori su sei asset, agosto 2002 - agosto 2026. Le tre barre di ogni gruppo non vanno confrontate fra loro: sono tre scale diverse.</figcaption>
</figure>

La cosa da notare non è chi vince. È che **in ogni gruppo le tre barre hanno sempre lo stesso ordine di grandezza relativo**: il Sortino è il più alto, lo Sharpe sta in mezzo, il Calmar è il più basso. Non è una proprietà di quegli investimenti, è una conseguenza di come sono costruiti i tre denominatori, e vale praticamente sempre.

Questo è il motivo pratico per cui il confronto va fatto **sempre fra lo stesso indicatore**: Sharpe con Sharpe, Calmar con Calmar, e sullo stesso periodo.

## Come si leggono i valori

Qui la divulgazione finanziaria è poco utile, perché ripete soglie ("sopra 1 è buono") che non dicono rispetto a cosa.

Un riferimento empirico onesto è questo. Sulle **ventidue asset class** misurate in questo articolo, sugli stessi ventiquattro anni:

- l'**indice di Sharpe** va da **0,17** (Treasury USA a lunga scadenza) a **0,80** (Nasdaq 100), con mediana **0,45**;
- l'**indice di Sortino** va da **0,28** a **1,31**, con mediana **0,71**;
- l'**indice di Calmar** va da **0,05** (petrolio) a **0,32** (Nasdaq 100), con mediana **0,17**.

Questi intervalli valgono per asset class azionarie, obbligazionarie e di materie prime tenute senza fare niente, su un periodo lungo che contiene due crisi gravi. Su periodi più corti, o su strategie con leva, o su singoli titoli, gli intervalli sono diversi.

La regola pratica che ne deriva: **un indicatore non si legge da solo, si legge contro un riferimento calcolato allo stesso modo sullo stesso periodo.** Uno Sharpe di 0,7 è ottimo se il mercato nello stesso periodo stava a 0,45 ed è deludente se stava a 1,1.

## Tre cose da sapere prima di usarli

### Descrivono un periodo, non un investimento

È la cosa più importante, e si vede meglio con un esempio che con una spiegazione.

<figure>
  <img src="/charts/sharpe-sortino-calmar/03_sottoperiodi.png" alt="Grafico a barre raggruppate con l'indice di Sharpe di S&P 500, Nasdaq 100, oro e Treasury USA 20+ calcolato su quattro sottoperiodi: 2003-2007, 2008-2012, 2013-2019 e 2020-2026. L'oro passa da 0,96 a meno 0,07, i Treasury da più 0,39 a meno 0,52." width="2080" height="1200" decoding="async" />
  <figcaption>Lo stesso indice di Sharpe, calcolato sugli stessi asset in quattro periodi diversi.</figcaption>
</figure>

L'**oro** ha uno Sharpe di **0,96** fra il 2003 e il 2007 e di **meno 0,07** fra il 2013 e il 2019. I **Treasury americani a lunga scadenza** passano da **più 0,39** fra il 2013 e il 2019 a **meno 0,52** dal 2020 in poi. Perfino l'S&P 500 oscilla fra **0,23** e **1,17** a seconda di quale quinquennio si guarda.

Nessuno di questi investimenti è cambiato. È cambiato il periodo. Di conseguenza, **un indicatore citato senza il periodo su cui è calcolato non è un dato**, ed è il motivo per cui su questo sito il periodo è sempre scritto accanto al numero.

### Dipendono dal tasso privo di rischio

Il numeratore sottrae il tasso privo di rischio, e quel tasso cambia moltissimo nel tempo. Sul periodo di questo articolo è stato in media l'**1,81%** annuo, con anni interi vicini allo zero; oggi è sopra il 4%.

Vuol dire che **lo stesso identico investimento, con lo stesso identico andamento, avrebbe uno Sharpe più basso se misurato in un'epoca di tassi alti**. Quando si confrontano indicatori presi da fonti diverse, vale la pena verificare che il tasso privo di rischio usato sia lo stesso, perché spesso non lo è e qualcuno lo pone a zero.

### Dipendono da quante osservazioni hai

Volatilità e semideviazione sono stime, e su pochi dati sono stime pessime. Su sei settimane di dati escono indici di Sharpe a doppia cifra che non significano nulla: il periodo è troppo corto perché un calo ci sia capitato dentro.

È una regola che applichiamo anche a noi stessi: nelle pagine del [`/lab`](/lab) volatilità e Sharpe annualizzati non vengono pubblicati sotto le venti osservazioni, proprio per evitare di mostrare numeri spettacolari e privi di contenuto nelle prime settimane di un esperimento.

## A cosa servono, in pratica

Riassunto operativo.

1. **Servono a confrontare alternative simili sullo stesso periodo.** Due ETF azionari globali, due versioni della stessa strategia, un portafoglio contro il suo benchmark.
2. **Non servono a dare un voto assoluto.** "Questo fondo ha Sharpe 0,9" non è un'informazione finché non si sa su quale periodo e contro cosa.
3. **Vanno letti accanto ai numeri grezzi**, cioè rendimento, volatilità e drawdown separati. Una frazione nasconde entrambi i suoi termini: un Calmar di 0,3 può nascere da un 3% di rendimento con un 10% di caduta o da un 15% con un 50%.
4. **Si confrontano solo con sé stessi**: Sharpe con Sharpe, mai Sharpe con Sortino.

## Dove li trovi su questo sito

Compaiono in una dozzina di articoli, ed è il motivo per cui questo episodio esiste. Qualche esempio: [Quale settore difensivo aggiungere a un portafoglio azionario](/posts/quale-sleeve-difensiva-migliore) li usa per scegliere fra cinque candidati, [Il portafoglio più decorrelato batte il mercato?](/posts/portafoglio-decorrelato-batte-mercato) mostra un Calmar che passa da 0,22 a 0,36 a parità di rendimento, e le pagine del [`/lab`](/lab) li pubblicano in continuo sugli esperimenti in corso.

## Quello che questo episodio non dice

**Non dice quale indicatore sia il migliore.** Sono tre descrizioni diverse della stessa storia, e la scelta dipende da cosa ti preoccupa: l'oscillazione, le perdite o il caso peggiore.

**Non spiega da dove vengono le misure di rischio al denominatore.** Volatilità, semideviazione e drawdown sono l'[episodio 10](/posts/rischio-volatilita-diversificazione).

**Non spiega da dove viene il rendimento al numeratore.** CAGR, XIRR e finestre mobili sono l'[episodio 11](/posts/pac-pic-cagr-xirr).

**Non li usa per scegliere un investimento.** Un indicatore descrive quello che è successo, e gli articoli di questo sito che lo usano lo fanno sempre su un periodo dichiarato, accanto ai numeri grezzi.

## Il prossimo episodio

Resta un'ultima cosa, ed è quella che muove tutte le altre. In questo episodio il tasso privo di rischio è comparso come un dettaglio tecnico al numeratore, ma è molto di più: è il prezzo del denaro, e quando cambia si muovono obbligazioni, azioni, mutui e valute insieme. L'episodio 13 chiude la collana con **il costo del denaro e come i tassi muovono tutto**.

## Fonti e metodo

- Serie di mercato: `data/cache/correlation_universe_monthly.csv`, chiusure mensili aggiustate per i dividendi in dollari. Finestra comune agosto 2002 - agosto 2026, ventidue asset class, 289 mesi: la stessa dell'[episodio 10](/posts/rischio-volatilita-diversificazione), scelta perché imporre a tutti lo stesso periodo è l'unico modo di rendere confrontabili questi numeri.
- Tasso privo di rischio: `data/Bonds/FEDFUNDS.csv`, tasso sui federal funds, media mensile, riportato a fine mese per allinearlo alle chiusure del panel. Media del periodo 1,81% annuo. È una scelta fra le tante possibili: usare i BOT a tre mesi darebbe numeri leggermente diversi, e questo è un buon esempio di perché due fonti possono pubblicare Sharpe diversi sullo stesso investimento.
- Sharpe: media dei rendimenti mensili in eccesso sul tasso privo di rischio, moltiplicata per dodici, divisa per la deviazione standard dei rendimenti mensili moltiplicata per la radice di dodici.
- Sortino: stesso numeratore dello Sharpe, diviso la semideviazione, cioè la radice della media dei quadrati dei soli rendimenti negativi, annualizzata. I mesi positivi entrano nella media come zero: è la convenzione più diffusa, ma ne esistono altre che dividono solo per il numero di mesi negativi e producono valori più alti.
- Calmar: rendimento annuo composto diviso il valore assoluto del massimo drawdown del periodo. Al numeratore, per convenzione, il rendimento pieno e non quello in eccesso.
- Drawdown calcolato su dati mensili: i minimi infra-mensili non compaiono, quindi le cadute reali sono leggermente più profonde e i Calmar reali leggermente più bassi.
- Lo script contiene tre controlli che fanno fallire la generazione se le affermazioni dell'articolo cadono: che il Sortino superi lo Sharpe su tutti gli asset, che l'oro cambi segno fra i sottoperiodi e che la frazione dello Sharpe torni.
- Codice che genera grafici e numeri: `scripts/sharpe-sortino-calmar.py`, output in `public/charts/sharpe-sortino-calmar/summary.json`.
