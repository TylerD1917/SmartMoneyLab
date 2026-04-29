---
title: "Ha ancora senso inserire obbligazioni in portafoglio?"
description: "Tre portafogli a confronto (100% azionario, 60/40, 40/60) su 25 anni di dati S&P 500 e Treasury 10Y, in finestre rolling a 5 e 10 anni. La risposta dipende da una variabile che quasi nessuno ti chiede."
pubDate: 2026-04-28
tags: ["obbligazioni", "asset-allocation", "60-40", "rolling-windows", "backtest"]
author: "SmartMoneyLab"
simulationSlug: "ha-senso-obbligazioni-portafoglio"
draft: false
---

## In breve

Su 25 anni di dati S&P 500 e Treasury 10Y (febbraio 2001 – dicembre 2025), costruisco tre portafogli **buy & hold** (100% azionario, 60% azioni / 40% obbligazioni, 40% azioni / 60% obbligazioni) e li confronto su tutte le finestre temporali a 5 e a 10 anni che si possono ritagliare nel periodo, non su un singolo arco scelto a posteriori. Tre risultati centrali emergono dai numeri:

1. Nel lungo periodo l'azionario domina **in mediana**, ma nei peggiori scenari decennali i portafogli più obbligazionari hanno effettivamente protetto: nel 5% delle finestre 10 anni andate peggio, il 100% azionario chiude con un rendimento annualizzato del 3.10%, mentre il 40/60 chiude col 4.50%.
2. Il vero vantaggio dei bond è sui **drawdown** (le perdite massime lungo il percorso, picco–valle): nel 100% azionario, in più di metà delle finestre 10 anni il drawdown ha superato il −30%. Nel 60/40 questo non è mai successo. Nel 40/60 nemmeno il −20%.
3. **A 5 anni il 100% azionario chiude in perdita nel 7.5% delle finestre.** Il 60/40 e il 40/60 non chiudono mai 5 anni in negativo.

La conclusione, costruita sui dati e non scritta a tavolino, è che le obbligazioni servono molto meno di quanto le banche raccontano se hai un orizzonte lungo e contributi regolari, e molto più di quanto si dica a chi sta arrivando alla fine.

## La domanda

Le obbligazioni in portafoglio sono uno dei capisaldi del consiglio finanziario standard. Il classico **60/40** — 60% azioni, 40% obbligazioni — è stato per decenni il portafoglio "di default" del consulente medio, italiano e non. Negli ultimi anni si è alzato un coro di voci che lo dichiara morto, soprattutto dopo il 2022 (anno in cui azioni *e* obbligazioni sono scese contemporaneamente per la prima volta da decenni). Altri lo difendono ancora.

Voglio rispondere a tre domande in sequenza, sui dati:

1. **Ha ancora senso** inserire obbligazioni in portafoglio?
2. **Quando** ha senso?
3. **Per chi** ha senso?

L'angolo di fondo che voglio testare — anziché annunciare in apertura — è il seguente: **forse le obbligazioni hanno senso soprattutto per chi si avvicina alla data di disinvestimento e vuole proteggere il capitale maturato.** Vediamo se i dati lo confermano o no.

## Il metodo: finestre rolling, niente cherry-picking

La maggior parte dei "backtest" che leggi su LinkedIn o nelle slide del consulente sono costruiti su un singolo periodo storico (di solito quello più favorevole alla tesi). Questo è metodologicamente sbagliato: il punto di partenza e il punto di fine influenzano enormemente il risultato finale. Lo stesso portafoglio testato dal 2010 al 2020 sembra eccezionale; testato dal 2000 al 2010 sembra disastroso.

Per evitarlo qui uso le **finestre rolling** (in inglese *rolling windows*, da qui in poi "finestre 5 anni" o **5Y**, e "finestre 10 anni" o **10Y**, per brevità). L'idea è semplice: invece di scegliere un solo periodo, ne considero centinaia. Faccio scivolare una finestra di 5 (o 10) anni lungo tutto il dataset, calcolando le statistiche su ogni posizione possibile della finestra, e ottengo una **distribuzione di risultati** anziché un singolo numero. Concretamente:

- Costruisco le serie mensili di rendimenti totali per i tre portafogli su tutto il periodo **febbraio 2001 – dicembre 2025** (299 mesi, ovvero quasi 25 anni di dati).
- Per ogni portafoglio, calcolo le metriche su **tutte le finestre 5Y** (60 mesi) e **10Y** (120 mesi), facendole scorrere con uno **step di 3 mesi**. Ogni 3 mesi sposto in avanti il punto di partenza della finestra e ricalcolo. In totale ottengo 80 finestre 5Y e 60 finestre 10Y per ciascun portafoglio.
- I rendimenti sono **lordi** (no costi degli ETF, no tasse). Lo scopo è isolare la tesi sull'allocazione dal rumore dei costi: ogni articolo successivo che parlerà di costi/fiscalità italiana lavorerà su questi numeri come baseline.

### Buy & hold puro, niente rebalancing

Una scelta metodologica importante: **nessuno dei tre portafogli viene riequilibrato**. Compri all'inizio coi pesi target (es. 60% azioni, 40% obbligazioni), poi lasci stare. I pesi cambiano nel tempo perché azioni e obbligazioni non si muovono allo stesso modo, e dopo qualche anno di azionario forte il "60/40" iniziale è di fatto un "75/25" o un "85/15".

La ragione è di onestà di confronto: il rebalancing comporta vendite periodiche, quindi commissioni broker, spread bid/ask e tasse su capital gain realizzati. Modellare tutti questi costi richiederebbe assunzioni discutibili, e questi costi nel **portafoglio 100% azionario buy & hold non esistono affatto**. Per non penalizzare artificialmente i portafogli misti con costi che il pure-equity non avrebbe, eviterei a priori il problema: tutti e tre buy & hold puri.

Per le finestre rolling, ogni finestra parte fresh dai pesi target. È il framing che il lettore retail mette mentalmente: *"se compro oggi un 60/40 e lo tengo 5 (o 10) anni senza toccarlo, cosa mi aspetto?"*

### Le scelte tecniche

- **Azionario**: S&P 500 *Total Return* (con dividendi reinvestiti), serie mensile ricostruita dal dataset Shiller.
- **Obbligazionario**: Treasury USA 10Y *Constant Maturity*, total return mensile ricostruito dai yield FRED con il modello duration-based standard (riferimento accademico: Swinkels, 2019).

Lo script Python che produce tutte le serie e i grafici è in [`scripts/ha-senso-obbligazioni-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-obbligazioni-portafoglio.py) — riga per riga, riproducibile. Se trovi un errore o una scelta che non condividi, fammelo sapere.

> **Limite onesto**: questa è un'analisi *USA-centric*, in dollari, su un orizzonte di 25 anni. Non è esattamente l'esperienza di un investitore italiano che compra ETF in euro su Borsa Italiana, perché manca tutta la dinamica del cambio EUR/USD e l'esposizione a un universo obbligazionario diverso (Bund, BTP, corporate IG europeo). Il periodo 2001–2025 include comunque tre stress severi (dot-com burst, Crisi Finanziaria 2008, COVID 2020) e il grande shock tassi del 2022 — quindi è ricco di "test reali" anche se più corto del 1976–2025 originario. La replica geo-italianizzata (MSCI World + Euro Aggregate Bond) sarà un articolo successivo.

## Risultati su finestre 10 anni: l'azionario domina (ma non sempre)

Su orizzonti lunghi i mercati azionari hanno tempo di metabolizzare i drawdown e il *premio per il rischio* si manifesta. Ecco la distribuzione del CAGR (Compound Annual Growth Rate, ovvero il rendimento annualizzato composto) per i tre portafogli, su tutte le finestre 10Y disponibili:

<figure>
  <img src="/charts/ha-senso-obbligazioni-portafoglio/01_boxplot_cagr_10y.png" alt="Boxplot del CAGR su finestre rolling 10 anni — 100% azionario, 60/40, 40/60. Distribuzioni dei rendimenti annualizzati composti, S&P 500 + UST 10Y, dati 2001-2025." />
  <figcaption>Distribuzione del CAGR su finestre 10 anni, step 3 mesi. Box centrale = 25°-75° percentile. Linea nera = mediana. Baffi = 5°-95° percentile.</figcaption>
</figure>

I numeri esatti, in tabella:

| Portafoglio | p5    | p25   | **Mediana** | p75    | p95    |
|-------------|-------|-------|-------------|--------|--------|
| 100% E      | 3.10% | 7.24% | **10.09%**  | 13.29% | 14.89% |
| 60/40       | 4.05% | 6.29% | **7.73%**   | 9.77%  | 11.43% |
| 40/60       | 4.50% | 5.76% | **6.24%**   | 7.71%  | 9.22%  |

**Come si legge questa tabella.** I numeri "p5", "p25" e così via sono **percentili**: il 5° percentile è il valore sotto cui si trova il 5% delle finestre osservate (le peggiori); la mediana (50° percentile) è il valore centrale; il 95° percentile è quello sopra cui si trova solo il 5% delle finestre (le migliori). Quindi *"p5 100% E = 3.10%"* significa: nel 5% delle finestre 10Y andate peggio per il portafoglio 100% azionario, il rendimento annualizzato finale è stato 3.10% o meno.

Lettura del dato:

- **Sul valore mediano** l'azionario stravince. 10.09% contro 7.73% del 60/40 (spread di ~2.4 punti percentuali) e 6.24% del 40/60 (spread di ~3.85 punti). Capitalizzati su 30 anni di accumulo, sono numeri spaventosi: 1€ investito al 100% in azionario diventa ~17.7€, lo stesso 1€ nel 60/40 diventa ~9.3€, nel 40/60 ~6.0€. Il 60/40 finisce con quasi metà del capitale finale rispetto al pure-equity.
- **Ma nei peggiori scenari** la cosa si capovolge in modo elegante: il p5 del 100% azionario (3.10%) è **inferiore** sia al p5 del 60/40 (4.05%) sia a quello del 40/60 (4.50%). Le 10Y peggiori nel periodo coprono la finestra 2000–2010 (dot-com + recovery + Crisi Finanziaria) — ed è proprio dove l'obbligazionario, salendo grazie alla discesa dei tassi, ha effettivamente *vinto* l'azionario in rendimento finale.
- **Nessun portafoglio ha CAGR negativo a 10 anni nel periodo**: anche nella peggior finestra il 100% azionario torna sopra il 3% annualizzato. Il famoso "non perdi mai a 10 anni" tiene, almeno per S&P 500.

> Il 60/40 non è solo un "compromesso meno rendimento, meno rischio". Nelle finestre peggiori vince in rendimento — *e* abbatte i drawdown. Doppio vantaggio relativo che però si paga sulla mediana.

## Risultati su finestre 5 anni: l'azionario può andare in rosso

Comprimere l'orizzonte a 5 anni cambia drammaticamente lo scenario. Le code della distribuzione si allargano e l'azionario inizia a sbattere contro periodi in cui non c'è stato tempo di recuperare:

<figure>
  <img src="/charts/ha-senso-obbligazioni-portafoglio/02_boxplot_cagr_5y.png" alt="Boxplot del CAGR su finestre rolling 5 anni — 100% azionario, 60/40, 40/60. Distribuzioni dei rendimenti annualizzati, S&P 500 + UST 10Y, dati 2001-2025." />
  <figcaption>Distribuzione del CAGR su finestre 5 anni, step 3 mesi. Le code sono molto più larghe rispetto alle 10Y.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | p5      | p25   | **Mediana** | p75    | p95    | % finestre con CAGR < 0 |
|-------------|---------|-------|-------------|--------|--------|--------------------------|
| 100% E      | −0.29%  | 3.66% | **11.47%**  | 14.58% | 17.40% | **7.5%**                 |
| 60/40       | 2.32%   | 4.64% | **8.39%**   | 9.82%  | 12.24% | 0%                       |
| 40/60       | 3.19%   | 4.94% | **6.04%**   | 7.62%  | 9.59%  | 0%                       |

Cosa cambia rispetto alle 10Y:

- **Il 100% azionario può finire 5 anni con rendimento annualizzato negativo**: in 6 finestre su 80 (il 7.5%) il CAGR è sotto zero. Sono le finestre che includono il pieno del dot-com burst (1999–2004) e il pieno della Crisi Finanziaria (2007–2012).
- **60/40 e 40/60: zero finestre con CAGR negativo.** L'investitore che ha inserito obbligazioni in portafoglio non ha mai chiuso i 5 anni in perdita, fatto rilevante per chi ha capitale che gli serve a 5 anni e non può permettersi di chiudere in rosso.
- I p5 dei due portafogli misti (2.32% e 3.19%) sono chiaramente positivi, contro il p5 leggermente negativo del 100% azionario (−0.29%).

A 5 anni l'azionario può ancora vincere la maggior parte delle volte (mediana 11.47% vs 8.39% del 60/40), ma la distribuzione delle code negative è sostanzialmente diversa.

## I drawdown: dove le obbligazioni guadagnano i loro galloni

Il rendimento medio è solo metà della storia. L'altra metà è la profondità delle cadute lungo il percorso. Il **max drawdown** (da ora **MDD**) è il peggior calo subito dal portafoglio dal massimo al minimo successivo, prima di tornare a fare un nuovo massimo. Tradotto: di quanto si è svuotato il portafoglio nel suo momento peggiore, dentro la finestra che stiamo guardando. Per chi sta investendo è la metrica psicologicamente decisiva: più volte determina se l'investitore *resta investito* oppure capitola al ribasso.

<figure>
  <img src="/charts/ha-senso-obbligazioni-portafoglio/03_drawdown_distribution_5y.png" alt="Distribuzione del max drawdown su finestre rolling 5 anni per i tre portafogli. Curva cumulata empirica del peggior drawdown osservato dentro ciascuna finestra." />
  <figcaption>Distribuzione cumulata del max drawdown osservato all'interno di ogni finestra 5Y. Più la curva è "spostata a destra" (verso drawdown meno profondi), meglio.</figcaption>
</figure>

Qui emerge il vero motivo per cui esistono i bond. Tabella del MDD osservato in ciascuna finestra rolling, percentili e frequenze:

| Portafoglio | MDD mediano (5Y) | % finestre 5Y con MDD ≤ −20% | % finestre 5Y con MDD ≤ −30% | MDD mediano (10Y) | % finestre 10Y con MDD ≤ −20% | % finestre 10Y con MDD ≤ −30% |
|-------------|------------------|-------------------------------|-------------------------------|--------------------|--------------------------------|--------------------------------|
| 100% E      | −18.92%          | 32.5%                         | 27.5%                         | **−42.27%**        | **51.7%**                      | **51.7%**                      |
| 60/40       | −11.67%          | 23.8%                         | 0%                            | −19.95%            | 50.0%                          | **0%**                         |
| 40/60       | −7.12%           | 0%                            | 0%                            | −11.94%            | 0%                             | 0%                             |

Cosa salta all'occhio:

- **Sul 100% azionario, in 31 finestre 10Y su 60 (il 51.7%) il drawdown ha toccato o superato il −30%**, e la mediana del drawdown a 10 anni è −42%. È il prezzo "psicologico" di avere il pure-equity nel decennio 2001–2010 e nelle finestre vicine: hai vissuto due crolli del 50%.
- **Il 60/40 dimezza il problema esatto**: in metà delle finestre 10Y c'è comunque un drawdown peggio del −20% — *ma in nessuna finestra il drawdown supera il −30%*. Il drawdown peggiore in assoluto del 60/40 nel periodo è −28%, contro il −49% del 100% azionario.
- **Il 40/60 elimina sostanzialmente i drawdown profondi**: zero finestre 5Y peggio del −20%, zero finestre 10Y peggio del −20%. Il peggio assoluto è −19%.

In termini operativi: se hai un 60/40 e il mercato azionario perde il 49% (massimo di periodo per il 100% azionario), tu sei sceso del 28%. È la differenza tra "spaventoso" e "inaccettabile". Per molti investitori reali, è la differenza tra restare investiti e vendere al peggio.

## L'equity curve: come si vede il trade-off su un caso reale

Per visualizzare il trade-off in modo cumulativo, il grafico più informativo è la curva del valore di 1 dollaro investito a inizio 2001, fino a fine 2025:

<figure>
  <img src="/charts/ha-senso-obbligazioni-portafoglio/04_equity_curve.png" alt="Equity curve dei tre portafogli (100% azionario, 60/40, 40/60) dal 2001 al 2025, scala logaritmica. Crescita di 1 USD investito a inizio 2001 — buy & hold puro." />
  <figcaption>Crescita cumulata di 1 USD investito a febbraio 2001 con i pesi target iniziali, buy & hold puro. Scala logaritmica per visualizzare i tassi di crescita relativi.</figcaption>
</figure>

> **Come si legge questo grafico — importante.** A differenza delle finestre rolling sopra, **questa è una sola simulazione, non una statistica**. Letteralmente: prendo 1 USD a febbraio 2001 (primo mese del dataset), lo divido secondo i pesi target di ciascun portafoglio (es. 60% azioni e 40% obbligazioni nel 60/40), e poi non tocco più nulla fino a dicembre 2025. È quindi *un* possibile percorso, *uno* specifico investitore che ha avuto la sorte (o sfortuna) di iniziare proprio in quel mese. Le statistiche robuste sull'allocazione sono nelle finestre rolling sopra (80 finestre 5Y, 60 finestre 10Y, ognuna con il proprio punto di partenza). L'equity curve serve per **vedere visivamente cosa accade su un percorso reale** — è didattica, non predittiva. Da nessuna parte questo grafico ti garantisce un rendimento futuro: ti mostra *un* esito storico osservato.

Numeri di riepilogo full-sample (24 anni e 10 mesi, dal febbraio 2001 al dicembre 2025):

| Portafoglio | CAGR full-sample | Volatilità annualizzata | Max drawdown |
|-------------|------------------|--------------------------|--------------|
| 100% E      | 8.60%            | 13.02%                   | −49.04%      |
| 60/40       | 7.11%            | 7.62%                    | −20.20%      |
| 40/60       | 6.13%            | 6.29%                    | −19.24%      |

1 USD investito nel febbraio 2001 diventa:
- ~$7.80 con il 100% azionario buy & hold
- ~$5.55 con il 60/40 buy & hold
- ~$4.40 con il 40/60 buy & hold

Tradotto: rispetto al 100% azionario, il 60/40 ha ottenuto il 71% del capitale finale, il 40/60 il 56%. Il 60/40 vale il 60% in volatilità (7.6% vs 13.0%) e meno della metà del drawdown peggiore (−20% vs −49%). Sta a te decidere se l'asimmetria del trade-off (perdi 29% di capitale finale per dimezzare il drawdown peggiore) è quella che vuoi sopportare.

> **Drift dei pesi**: senza rebalancing, dopo 25 anni di azionario sostanzialmente forte il 60/40 iniziale è di fatto un portafoglio molto più sbilanciato sull'azionario. Il rendimento full-sample del 60/40 buy & hold quindi non è il rendimento di un "60/40 sempre 60/40" — è il rendimento di un "60/40 lasciato vivere". È onesto guardarlo così: rappresenta l'investitore che compra una volta e non tocca mai. Nelle finestre rolling, invece, ogni finestra parte fresh dai pesi target — quindi i numeri delle tabelle sopra sono direttamente confrontabili con la tua decisione di entrare oggi su una di quelle allocazioni.

## Quindi: ha senso? Quando? Per chi?

Riassumo i fatti che emergono dai dati:

1. Su orizzonti **lunghi (10 anni)** l'azionario in mediana stravince in rendimento. Il 60/40 mediano costa 2.4 punti percentuali all'anno rispetto al 100% azionario. Quasi 4 punti il 40/60. Capitalizzati su decenni, sono numeri di tutto rispetto.
2. **Nelle peggiori 10 anni il quadro si capovolge**: il p5 del 100% azionario è inferiore ai p5 dei portafogli misti, perché la combinazione di due crolli ravvicinati con poco tempo di recovery favorisce chi aveva una quota obbligazionaria che ha tirato verso l'alto durante il crollo dei tassi.
3. Su **orizzonti brevi (5 anni)** il 100% azionario può chiudere in perdita nel 7.5% delle finestre. Il 60/40 e il 40/60 mai.
4. **Sui drawdown l'obbligazionario fa la differenza più netta**: il 100% azionario ha visto drawdown ≥ −30% nel 51.7% delle finestre 10Y. Il 60/40 mai. Il 40/60 nemmeno drawdown ≥ −20% mai.
5. **Le obbligazioni quindi non sono uno strumento di rendimento**: nei 25 anni analizzati il 60/40 batte mediamente il 100% azionario *solo* nei p5 (le code negative). Sono, propriamente, uno **strumento di copertura sul percorso**.

**Per chi ha senso, allora?**

Per chi **ha bisogno del capitale presto** — diciamo nei prossimi 5–7 anni — e non può permettersi di assorbire un −30% o −40% di drawdown senza compromettere l'obiettivo. È il caso classico:

- chi sta arrivando alla pensione e tra 3–5 anni inizierà il decumulo
- chi sta accumulando per un acquisto importante a scadenza fissa (casa, finanziamento di un progetto)
- chi ha un orizzonte mentale corto (anche se la teoria gli direbbe altrimenti) e rischia di vendere al peggio

Per **chi ha 15+ anni davanti e contributi regolari**, le obbligazioni in portafoglio sono in larga parte un costo opportunità. La cosa che protegge il piano in caso di crash non è l'allocazione obbligazionaria — è la capacità di continuare a versare *durante* il crash, comprando asset a prezzi più bassi (l'effetto del piano di accumulo regolare in fase di drawdown).

### Il sequence-of-returns risk: il vero motivo dei bond

Il punto dove l'obbligazionario diventa effettivamente decisivo è il **rischio di sequenza dei rendimenti** (in inglese *sequence-of-returns risk*): quando inizi a prelevare dal portafoglio, l'ordine in cui arrivano i rendimenti conta moltissimo. Due investitori con lo stesso rendimento medio annuo possono finire con risultati radicalmente diversi a seconda di se i drawdown arrivano *all'inizio* del decumulo o alla fine.

In fase di decumulo, un drawdown del −40% nei primi 3 anni può compromettere irreversibilmente la sostenibilità del piano (vendere asset depressi per coprire il prelievo accelera il consumo del capitale). È in questa fase — e *quasi solo* in questa fase — che la riduzione di volatilità data dalle obbligazioni vale il costo di rendimento atteso ridotto.

Da qui il concetto di **glide path** ("sentiero di discesa"): aumentare progressivamente la quota obbligazionaria avvicinandosi alla data di disinvestimento. La logica è quella di un paracadute: inutile (e costoso) nei primi 30 anni, indispensabile nell'ultimo tratto.

## Takeaway

1. **Le obbligazioni nel lungo periodo costano in rendimento mediano**, in modo significativo. Il 60/40 perde ~2.4% annualizzati al portafoglio rispetto al 100% azionario. Capitalizzato su decenni, è enorme: a 30 anni di accumulo il 100% azionario vale quasi il doppio.
2. **Ma nei peggiori scenari decennali i portafogli misti vincono anche in rendimento**, non solo in drawdown. Il p5 del 100% azionario (3.1%) è sotto il p5 del 60/40 (4.0%) e del 40/60 (4.5%).
3. **Le obbligazioni nel breve periodo riducono drasticamente la profondità dei drawdown**. Il 100% azionario ha avuto drawdown peggiori del −30% nel 51.7% delle finestre 10Y. Il 60/40 mai. Il 40/60 ha eliminato anche i drawdown peggiori del −20%.
4. La domanda *"ha senso avere obbligazioni?"* è mal posta. La domanda giusta è *"quanto manca al momento in cui mi servirà il capitale?"*. Risposta sotto i 7–10 anni → ha senso introdurre obbligazioni progressivamente. Sopra i 15 anni → probabilmente è solo un costo opportunità (con l'eccezione dei p5 menzionata sopra: una piccola assicurazione marginale, non uno strumento di rendimento).
5. **Il rischio di sequenza dei rendimenti** è il motivo strutturale per cui le obbligazioni esistono nei portafogli sensati. Non l'avversione al rischio in astratto.
6. Il consulente bancario medio italiano ti propone un 60/40 a 30 anni dalla pensione. È, statisticamente, una scelta sub-ottimale di alcune centinaia di migliaia di euro nel risultato finale.

---

### Fonti e riproducibilità

- Dati S&P 500 mensili (price + dividendo): [Shiller dataset](http://www.econ.yale.edu/~shiller/data.htm) — file `ie_data.xls`, mirror CSV su [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500).
- Yield Treasury 10Y: [FRED — DGS10](https://fred.stlouisfed.org/series/DGS10).
- Modello di ricostruzione del total return su Treasury constant maturity: Swinkels, L. (2019), *"Treasury Bond Returns Without Bond Prices"*, Robeco Quantitative Investments.
- Codice della simulazione: [`scripts/ha-senso-obbligazioni-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-obbligazioni-portafoglio.py) nel repository del blog.
- I dati grezzi (rendimenti mensili dei tre portafogli) sono salvati come CSV in [`/charts/ha-senso-obbligazioni-portafoglio/data.csv`](/charts/ha-senso-obbligazioni-portafoglio/data.csv) dopo l'esecuzione dello script.
- Il summary numerico completo (percentili, drawdown, frequenze) è in [`/charts/ha-senso-obbligazioni-portafoglio/summary.json`](/charts/ha-senso-obbligazioni-portafoglio/summary.json).

> Nota: questa analisi è limitata al periodo 2001–2025 e all'universo USA in dollari. Una replica con MSCI World + Euro Aggregate Bond, in EUR, sarà oggetto di un articolo futuro.
