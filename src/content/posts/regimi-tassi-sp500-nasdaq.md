---
title: "Regimi di tassi Fed e mercati azionari USA (1971-2026)"
description: "55 anni di dati sul rapporto tra tassi Fed e rendimenti di S&P 500 e NASDAQ. Analisi contemporanea e forward, tre definizioni di regime, event study sui pivot Fed."
pubDate: 2026-07-12
tags: ["tassi", "fed", "sp500", "nasdaq", "regimi", "policy-monetaria", "backtest", "rolling-windows"]
author: "SmartMoneyLab"
simulationSlug: "regimi-tassi-sp500-nasdaq"
draft: false
---

## In breve

Ad ogni riunione della Federal Reserve la stampa finanziaria e una parte non piccola dei creator sui social costruiscono un intero racconto attorno alla scelta di alzare, tenere fermi o tagliare i tassi. Il sottinteso condiviso è quasi sempre lo stesso: **tassi bassi favoriscono l'azionario, tassi alti lo penalizzano**. Ho testato l'affermazione su 55 anni di dati (1971-2026), applicando tre definizioni diverse di "regime dei tassi" in parallelo e confrontando sia i rendimenti contemporanei sia quelli forward a 12 e 24 mesi. Cinque conclusioni.

1. **La correlazione lineare tra livello dei Fed Funds e rendimenti azionari è statisticamente nulla**. FFR contro rendimento contemporaneo S&P 500: −0.03. Contro rendimento forward 12 mesi: +0.05. Sono zero. Il livello dei tassi non "spiega" i rendimenti in nessuna direzione.

2. **Il regime di tassi storicamente più redditizio per l'S&P 500 non è quello a tassi bassi**: è la fascia FFR nominale 4-6% (rendimento contemporaneo mediano 18.1% annualizzato). La fascia peggiore è 2-4%. Il pattern non è monotono in nessun senso.

3. **La direzione dei tassi conta più del livello, ma nel verso opposto a quello atteso**. Quando la Fed sta alzando (variazione trailing +1pp o più) il rendimento contemporaneo del S&P scende al 4.5% annualizzato (dal 14% dei periodi stabili) e il NASDAQ diventa negativo (−2.8%). Ma il forward 12 mesi migliora, non peggiora: 15.5% per l'S&P contro 12.8% dei periodi stabili.

4. **In termini reali (FFR meno inflazione) il pattern è inverso a quello narrativo**: il regime "restrittivo" (FFR reale sopra il 4%) è storicamente il **più** redditizio, con un rendimento contemporaneo del 19.9% annualizzato e un forward 12 mesi del 19.5%. La fascia peggiore è "0-2% reale" (l'era ZIRP 2009-2015 con recovery lenta).

5. **Event study sui pivot Fed**: dopo l'inizio di un ciclo di rialzo, il rendimento mediano dell'S&P a 24 mesi è **+46%**. Dopo l'inizio di un ciclo di taglio, "solo" +25%. La "Fed put" è reale ma inefficiente: il taglio arriva dopo un crollo già in corso, il rialzo intercetta un'economia che sta accelerando.

## Perché scriverlo

L'idea di questo articolo nasce osservando quanta parte del contenuto finanziario italiano — sui social, in TV, nei report bancari retail — costruisca un intero storytelling attorno a poche righe di comunicato della Fed. "La Fed alza, tempo di uscire dall'equity". "La Fed taglia, tempo di comprare Nasdaq". Il ragionamento è quasi sempre implicito, di rado esplicitato, e ancor meno spesso testato sui dati. La domanda che pongo è la più semplice possibile: **su 55 anni di dati storici, la relazione fra livello o direzione dei Fed Funds e rendimenti azionari USA è quella che il consenso retail dà per scontato?**

L'obiettivo di questo pezzo non è avanzare una strategia, tantomeno predire il prossimo movimento della Fed. È esclusivamente **descrittivo**: mostrare cosa dicono i dati, sotto tre definizioni diverse di regime, e lasciare al lettore il compito di aggiornare le proprie convinzioni.

## Dati e metodo

**Fonti**. Fed Funds Rate mensile dal 1954 (FRED, serie `FEDFUNDS`). S&P 500 total return mensile ricostruito dal dataset Shiller con formula `r_t = (P_t + D_(t-1)/12) / P_(t-1) − 1`, con dividendo estrapolato al div-yield medio 1.4% annuo per il periodo 2023-07 in poi (che nella cache Shiller ha `Dividend = 0`). NASDAQ Composite daily dal 1971 (FRED, `NASDAQCOM`), aggregato a fine mese e arricchito con un dividendo costante di 0.75% annuo — approssimazione conservativa rispetto al div yield storico effettivo del Composite (circa 1% negli ultimi 20 anni, meno negli anni tech-boom). Consumer Price Index dal dataset Shiller per il calcolo del tasso reale.

**Panel**. Il campione utile parte da aprile 1971 (inizio serie NASDAQCOM) e arriva ad aprile 2026, per un totale di 661 osservazioni mensili. Copre 11 presidenti della Fed, l'intera transizione dallo stagflation degli anni Settanta all'era ZIRP fino al ciclo restrittivo 2022-2024. Non c'è un altro dataset azionario liquido con questa profondità storica.

**Rendimenti**. Sono usati tanto i rendimenti mensili contemporanei (ossia: nei mesi con FFR nella fascia X, quanto ha reso l'S&P?) sia i rendimenti cumulati forward a 12 e 24 mesi (nei mesi con FFR nella fascia X, quanto ha reso l'S&P nei 12 e 24 mesi successivi?). Le due sono domande completamente diverse: la prima è correlazionale, la seconda ha una struttura predittiva.

**Tre definizioni di regime, in parallelo**.

- *Livello nominale (A)*: FFR in cinque fasce assolute — sotto 2%, 2-4%, 4-6%, 6-8%, sopra 8%. Semplice, immediatamente interpretabile. Il difetto è di confondere periodi macro molto diversi: FFR al 2% nel 2003 non è la stessa cosa di FFR al 2% nel 2022.
- *Direzione (B)*: variazione FFR nei 12 mesi trailing — discesa (meno 1pp o più), stabile, rialzo (più 1pp o più). Coglie il regime di policy in atto (hawkish, dovish, holding).
- *Livello reale (C)*: FFR meno CPI YoY, in quattro fasce (accomodante sotto 0%, 0-2%, 2-4%, restrittivo sopra 4%). Distingue "tassi nominalmente alti ma reali negativi" (2022) da "tassi nominalmente moderati ma reali molto restrittivi" (1997).

**Event study**. Ho identificato i "pivot Fed" come mesi in cui la variazione cumulata dei Fed Funds sui 6 mesi precedenti supera in valore assoluto 1.5 punti percentuali, richiedendo almeno 24 mesi di quiete dal pivot precedente. Il criterio restituisce **8 cicli di rialzo** (1972, 1974, 1977, 1979, 1982, 1984, 1988, 2022) e **9 cicli di taglio** (1972, 1974, 1980, 1982, 1984, 1991, 2001, 2008, 2020) — coerenti con la storiografia macro consolidata (Volcker, Greenspan, Bernanke, Yellen, Powell). Attorno ad ogni pivot ho estratto una finestra di 24 mesi prima e 24 mesi dopo, e ho calcolato la mediana cross-sezionale dei rendimenti cumulati normalizzati a 100 al mese del pivot.

**Total Return vs Price Return**. L'S&P 500 è sempre in total return (Shiller ricostruito). Il NASDAQ è total return solo in senso approssimato: il Composite in serie storica lunga è disponibile solo in price return via FRED, quindi ho aggiunto un dividendo costante 0.75% annuo. È dichiarato apertamente come limite: la differenza cumulata su 55 anni tra il "vero" TR NASDAQ e il PR-più-0.75% è probabilmente dell'ordine del 20-30% del capitale finale — non trascurabile, ma non tale da invertire il segno dei confronti relativi.

Lo script completo è nel repository ([`scripts/regimi-tassi-sp500-nasdaq.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/regimi-tassi-sp500-nasdaq.py)); il panel mensile completo, le statistiche per bucket, le date dei pivot e le curve equity sono in [`/charts/regimi-tassi-sp500-nasdaq/`](/charts/regimi-tassi-sp500-nasdaq/).

## Il contesto — cosa vediamo prima di segmentare

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/01_context_timeline.png" alt="Grafico che sovrappone la crescita cumulata di S&P 500 total return e NASDAQ Composite sul periodo 1971-2026, con Fed Funds Rate sul secondo asse. NASDAQ termina significativamente sopra S&P 500, e i due picchi FFR degli anni Ottanta e del 2022-2024 sono visibili." />
  <figcaption>Crescita di 1$ investito in S&P 500 total return e NASDAQ Composite (scala log) sovrapposta al livello dei Fed Funds. Il picco Volcker del 1981 e il ciclo restrittivo 2022-2024 sono le due fasi di tassi assoluti più alte del campione.</figcaption>
</figure>

A occhio, è difficile riconoscere una regola. Il picco Volcker del 1981 (FFR sopra il 15%) è seguito da uno dei mercati azionari più forti della storia moderna. L'era ZIRP 2009-2015 (FFR quasi zero) è associata a un mercato che sale, ma anche a una decade "persa" precedente. Il ciclo restrittivo 2022-2024 ha coinciso con un bear market breve seguito da uno dei rally più veloci mai visti. Prima di forzare una narrazione, segmentiamo.

## Sezione A — Livello nominale dei Fed Funds

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/02_regime_A_livello_boxplot.png" alt="Boxplot dei rendimenti mensili di S&P 500 e NASDAQ per cinque fasce di Fed Funds nominali. Le distribuzioni sono ampiamente sovrapposte, senza un ordinamento monotono." />
  <figcaption>Distribuzione dei rendimenti mensili di S&P 500 e NASDAQ per fascia di FFR nominale. Le mediane si assomigliano, nessuna fascia domina o è dominata in modo netto.</figcaption>
</figure>

Rendimenti contemporanei annualizzati per fascia FFR — S&P 500 total return e NASDAQ:

| Fascia FFR | n mesi | S&P 500 contemp. | NASDAQ contemp. | Hit rate SP fwd12m |
|---|---|---|---|---|
| sotto 2% | 194 | 10.3% | 14.0% | 84.5% |
| 2-4% | 74 | 2.3% | 4.8% | 80.9% |
| 4-6% | 193 | **18.1%** | **25.9%** | 80.7% |
| 6-8% | 70 | 13.4% | 6.7% | 67.1% |
| sopra 8% | 130 | 9.4% | 5.2% | 75.4% |

Due osservazioni. Primo: il rendimento contemporaneo migliore, sia per S&P che per NASDAQ, si registra nella fascia 4-6%, non nella fascia più bassa. Secondo: il pattern non è monotono. Se il consenso retail avesse ragione ("tassi bassi = più rendimenti"), dovremmo vedere una discesa continua da sinistra verso destra. Non c'è.

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/11_forward_horizons_by_regime.png" alt="Panel con due bar chart affiancati: forward 12 mesi e forward 24 mesi di S&P 500 e NASDAQ per fascia di FFR nominale. Il forward 24m migliore per l'S&P è nella fascia sopra 8%." />
  <figcaption>CAGR mediano forward 12 mesi (sinistra) e 24 mesi (destra) per fascia FFR nominale. Nel forward 24m, il migliore rendimento S&P è nella fascia sopra 8% (14.6%): l'eredità di Volcker, che ha lasciato uno dei mercati azionari più forti del secolo.</figcaption>
</figure>

Il forward 24 mesi cambia parzialmente il quadro. Il rendimento migliore per l'S&P (14.6% CAGR mediano) si osserva nella fascia sopra 8%, storicamente concentrata nei tardi anni Settanta e primi Ottanta — quando l'era Volcker stava terminando e preparando la disinflazione. Non è "i tassi alti fanno bene all'azionario": è un artefatto del regime specifico che ha caratterizzato quella fascia (fine di un ciclo restrittivo, inizio di una lunga espansione multipla).

## Sezione B — Direzione dei Fed Funds (regime di policy)

Definisco "direzione" la variazione dei Fed Funds nei 12 mesi trailing. Discesa = meno 1pp o più; rialzo = più 1pp o più; stabile = tutto il resto. Il campione si divide in 161 mesi di discesa, 341 di stabilità, 159 di rialzo.

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/04_regime_B_direzione_boxplot.png" alt="Boxplot dei rendimenti mensili di S&P 500 e NASDAQ per direzione FFR (discesa, stabile, rialzo). Il bucket 'rialzo' ha mediana visibilmente più bassa." />
  <figcaption>Rendimenti mensili per direzione FFR trailing 12m. Il regime 'rialzo' abbassa la mediana contemporanea in modo netto, specialmente per il NASDAQ.</figcaption>
</figure>

Contemporaneo, annualizzato:

| Direzione FFR | n mesi | S&P 500 | NASDAQ |
|---|---|---|---|
| Discesa (≤ −1pp) | 161 | 13.9% | 19.4% |
| Stabile (−1pp ÷ +1pp) | 341 | 14.2% | 19.4% |
| **Rialzo (≥ +1pp)** | 159 | **4.5%** | **−2.8%** |

Il rialzo penalizza il rendimento contemporaneo — specialmente il NASDAQ, che con una direzione hawkish della Fed passa in territorio negativo (−2.8% annualizzato mediano). Questo è coerente con la storia degli ultimi anni: 2022 in particolare è stato un anno pessimo per il tech mentre Powell alzava.

Ma il quadro cambia quando si guarda al forward:

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/05_regime_B_forward12m.png" alt="Bar chart che confronta il forward 12 mesi di S&P 500 e NASDAQ per le tre direzioni FFR. Il bucket 'rialzo' non è il peggiore forward — anzi." />
  <figcaption>CAGR mediano forward 12 mesi per direzione FFR. Nei 12 mesi successivi a un regime di rialzo, l'S&P rende il 15.5% mediano — la fascia migliore delle tre.</figcaption>
</figure>

| Direzione FFR | S&P forward 12m | NASDAQ forward 12m |
|---|---|---|
| Discesa | 14.6% | 17.2% |
| Stabile | 12.8% | 14.4% |
| **Rialzo** | **15.5%** | 15.1% |

Il pattern si ribalta. **Nei 12 mesi successivi a un regime di rialzo, l'S&P rende più che nei periodi stabili o di discesa.** Non è controintuitivo se si tiene presente la dinamica: la Fed alza quando l'economia è forte e i multipli si comprimono per il de-rating; ma la crescita degli utili nei trimestri seguenti continua, e i multipli tornano a espandersi. Il "male" del rialzo è compresso nel presente; il "bene" arriva dopo.

## Sezione C — Livello reale dei Fed Funds

Definisco tasso reale come `FFR meno CPI YoY`. È la variabile che il macro accademico considera più significativa: distingue la stance restrittiva effettiva della politica monetaria dai livelli nominali.

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/06_regime_C_reale_boxplot.png" alt="Boxplot dei rendimenti mensili di S&P 500 e NASDAQ per quattro fasce di FFR reale. Il bucket 'restrittivo' non è il peggiore, anzi ha mediana alta." />
  <figcaption>Rendimenti mensili per FFR reale. Il bucket 'accomodante sotto 0%' non è il migliore; il bucket 'restrittivo sopra 4%' non è il peggiore.</figcaption>
</figure>

| Fascia FFR reale | n mesi | S&P contemp. | S&P fwd 12m | NASDAQ contemp. |
|---|---|---|---|---|
| sotto 0% (accomodante) | 252 | 11.7% | 13.8% | 16.1% |
| 0-2% | 152 | 6.5% | 10.8% | 7.2% |
| 2-4% | 148 | 11.5% | 15.3% | 11.3% |
| **sopra 4% (restrittivo)** | 109 | **19.9%** | **19.5%** | **20.7%** |

Questo è il pattern più netto e forse più controintuitivo del pezzo. **Il regime "restrittivo in termini reali" — Fed Funds meno CPI sopra il 4% — è storicamente il più redditizio in assoluto per l'S&P e per il NASDAQ**, sia in termini contemporanei che forward. La fascia peggiore è "0-2% reale", che corrisponde in larga parte al periodo 2009-2015 (post-GFC, ZIRP, tassi bassi ma inflazione appena positiva → politica solo lievemente accomodante, recovery lenta).

L'interpretazione più semplice è: **quando la Fed è visibilmente restrittiva in termini reali, di solito ha già vinto la battaglia sull'inflazione, i multipli sono stati re-rated verso il basso, e da lì la strada più probabile è verso il basso per l'inflazione e verso l'alto per l'equity**. La fascia "restrittiva" del campione include il 1994-1995 (soft landing Greenspan), il 1997-2000 (fine ciclo Clinton), pezzi del 2006-2007 e (in parte) il 2023-2024 post-picco Powell.

## Sezione D — Event study sui pivot Fed

Otto cicli di rialzo, nove cicli di taglio, finestra ±24 mesi attorno al pivot, rendimenti cumulati normalizzati a 100 al mese del pivot.

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/08_event_hiking_cycles.png" alt="Grafico spaghetti + mediana: rendimenti cumulati di S&P 500 e NASDAQ nei 24 mesi prima e dopo l'inizio di un ciclo di rialzo Fed. La mediana sale in modo netto dopo il pivot." />
  <figcaption>Event study: inizio ciclo di rialzo Fed (8 eventi). La mediana cumulata S&P 500 è a +29% dopo 12 mesi e +46% dopo 24 mesi.</figcaption>
</figure>

<figure>
  <img src="/charts/regimi-tassi-sp500-nasdaq/09_event_cutting_cycles.png" alt="Grafico spaghetti + mediana: rendimenti cumulati di S&P 500 e NASDAQ nei 24 mesi prima e dopo l'inizio di un ciclo di taglio Fed. La mediana sale ma più lentamente." />
  <figcaption>Event study: inizio ciclo di taglio Fed (9 eventi). Il rimbalzo è più veloce sul NASDAQ (+37% a 12m) ma si ridimensiona a 24m (+31%).</figcaption>
</figure>

| Eventi | S&P a +12m | S&P a +24m | NASDAQ a +12m | NASDAQ a +24m |
|---|---|---|---|---|
| Pivot rialzo (n=8) | +28.9% | **+45.9%** | +23.8% | +44.2% |
| Pivot taglio (n=9) | +22.9% | +24.6% | +36.6% | +30.6% |

Due letture. Primo, il pivot di rialzo è associato a un rendimento a 24 mesi più alto del pivot di taglio, sia sull'S&P che sul NASDAQ. Coerente con l'analisi B: il rialzo intercetta un'economia in espansione, il taglio arriva in emergenza dopo un crollo già iniziato. Secondo, il NASDAQ mostra un pattern asimmetrico sui tagli: rimbalza in fretta (+36.6% a 12 mesi) e poi si ridimensiona a 24 mesi (+30.6%), tipico degli episodi 2001, 2008 e 2020.

Va detto con onestà: **8-9 eventi non sono un campione statisticamente robusto**. La distribuzione degli spaghetti nelle figure mostra chiaramente che ogni ciclo ha traiettorie molto diverse dalla mediana. L'event study è utile come "impressione centrale", non come previsione affidabile.

## Correlazione lineare

Come controllo di sanità, la correlazione lineare Pearson fra livello FFR e rendimenti:

| Coppia | Corr |
|---|---|
| FFR vs S&P 500 contemp. | −0.030 |
| FFR vs S&P 500 fwd 12m | +0.045 |
| FFR vs S&P 500 fwd 24m | +0.097 |
| FFR vs NASDAQ contemp. | −0.053 |
| FFR vs NASDAQ fwd 12m | −0.028 |
| FFR vs NASDAQ fwd 24m | −0.024 |

Tutti valori compresi tra −0.10 e +0.10. **Non c'è nessuna relazione lineare misurabile**. Chi costruisce una narrazione binaria "tassi bassi = rendimenti alti" o viceversa sta descrivendo un rapporto che nei dati non esiste.

## Limiti

**Endogeneity Fed-economia.** La Fed non muove i tassi a caso. Alza quando l'economia è forte e l'inflazione minaccia, taglia in emergenza. Qualunque correlazione tra livello o direzione FFR e rendimenti è confusa da questa endogeneity — separare "effetto tassi" da "effetto ciclo economico" richiede identificazione strutturale (VAR, shock monetari alla Romer-Romer o Bernanke-Kuttner) che è fuori scope per un pezzo divulgativo. Le medie condizionali che presento vanno lette come descrittive, non causali.

**Sample size sull'event study.** 8 pivot di rialzo e 9 di taglio in 55 anni sono pochi per generalizzare. L'ampia dispersione tra eventi lo mostra visivamente. Il valore mediano è indicativo, non predittivo.

**Total Return del NASDAQ.** Il NASDAQ è stato ricostruito come price return più dividendo costante 0.75% annuo, per assenza di una serie storica lunga di NASDAQ Composite in total return. È una scelta conservativa (sottostima il TR vero) coerente in tutti i confronti relativi, ma implica che i multipli finali NASDAQ nel grafico contesto sono sottostimati.

**Panel non allineato al lettore italiano.** L'analisi è sui rendimenti in dollari lordi, senza cambio euro-dollaro e senza tassazione italiana. Sono scelte metodologiche standard per la letteratura macro-finanziaria; il lettore italiano deve tenere a mente che tra dollaro forte-debole e 26% capital gains + bollo 0.2% i rendimenti nominali sopra vanno letti come "riferimento accademico", non come "ciò che è entrato in tasca al retail italiano". Il pattern *relativo* tra regimi è però invariante ai due filtri.

**"Regime" non è dato**. Le fasce che ho usato sono ragionevoli ma arbitrarie. Ho verificato che spostare le soglie di ±1pp non cambia la sostanza dei risultati, ma cambia i valori puntuali. Il codice permette di rifare l'analisi con altre soglie.

## Conclusioni

I dati raccontano tre cose ragionevolmente stabili sotto le tre definizioni di regime testate.

**Prima.** Il livello dei Fed Funds — nominale o reale — non è un predittore lineare dei rendimenti azionari USA. Su 55 anni la correlazione è zero. Ogni tentativo di costruire una regola operativa del tipo "quando FFR è sopra/sotto X compra/vendi" non trova supporto nei dati.

**Seconda.** La fase peggiore del ciclo non è "tassi alti", è "Fed che sta salendo". Il contemporaneo penalizza soprattutto il NASDAQ (mediana annualizzata negativa). Ma è una fase transitoria: nei 12 mesi successivi il rendimento mediano diventa il più alto delle tre direzioni.

**Terza, la più controintuitiva.** Il regime **restrittivo in termini reali** (FFR meno inflazione sopra il 4%) è storicamente il più redditizio per l'equity USA, sia contemporaneo che forward. Non perché "l'equity ama i tassi alti", ma perché il regime restrittivo tende a coincidere con periodi di disinflazione, re-rating dei multipli e riaccelerazione futura degli utili.

Nessuna di queste è una raccomandazione operativa. Sono descrizioni di come si sono comportate storicamente due asset class specifiche (S&P 500 e NASDAQ Composite) sotto tre segmentazioni ragionevoli del contesto monetario. Il valore aggiunto rispetto alla narrativa mediatica standard è precisamente questo: **il consenso "tassi bassi buoni, tassi alti cattivi" non è supportato dai dati**, in nessuna delle tre segmentazioni. Chi vuole prendere decisioni di portafoglio a partire dalla Fed dovrebbe come minimo confrontarle con questo pattern storico prima di sposarne la lettura semplicistica.

---

### Fonti e riproducibilità

- Fed Funds Rate mensile: [FRED serie FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS).
- S&P 500 total return: ricostruito da [dataset Shiller](http://www.econ.yale.edu/~shiller/data.htm), formula standard TR con dividendo mensile ricostruito prorata dal dividendo annuo. Estrapolazione post-2023-06 al div-yield medio 1.4% annuo.
- NASDAQ Composite daily: [FRED serie NASDAQCOM](https://fred.stlouisfed.org/series/NASDAQCOM). Total return proxy = price return + dividendo costante 0.75% annuo.
- Consumer Price Index: dataset Shiller.
- Codice completo della simulazione: [`scripts/regimi-tassi-sp500-nasdaq.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/regimi-tassi-sp500-nasdaq.py).
- Output numerico dettagliato (statistiche per bucket, date dei pivot, panel mensile): [`/charts/regimi-tassi-sp500-nasdaq/`](/charts/regimi-tassi-sp500-nasdaq/).
- Letteratura di riferimento sull'endogeneity Fed-mercati: Bernanke & Kuttner (2005), "What Explains the Stock Market's Reaction to Federal Reserve Policy?", Journal of Finance. Romer & Romer (2004) su identificazione shock monetari.

> Nota metodologica: la scelta di aggregare i rendimenti in medie condizionali per bucket ha il pregio della semplicità interpretativa, ma nasconde la dispersione intra-bucket, che è ampia. Il codice permette di ottenere direttamente boxplot, deviazioni standard e Sharpe per ogni bucket, oltre alle sole mediane riportate nel testo.

> Disclaimer: contenuto informativo ed educativo, non consulenza finanziaria. Le performance passate non sono indicative di quelle future. Le analisi presentate sono esercizi quantitativi descrittivi, non raccomandazioni operative. La segmentazione in "regimi" è una scelta metodologica soggettiva; risultati diversi possono emergere sotto altre segmentazioni ragionevoli.
