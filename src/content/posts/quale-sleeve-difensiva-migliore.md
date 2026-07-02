---
title: "Quale settore difensivo aggiungere a un portafoglio azionario? 27 anni di dati, 5 candidati, un vincitore chiaro"
description: "5 settori difensivi contro l'S&P 500 su 27 anni di dati. Utilities vince su ogni criterio. Quality è un paradosso: il retail la considera difensiva ma i dati la smentiscono."
pubDate: 2026-06-15
tags: ["portafoglio", "difensiva", "utilities", "healthcare", "quality", "settoriale", "backtest", "sp500"]
author: "SmartMoneyLab"
simulationSlug: "sleeve-difensiva-migliore"
draft: false
---

## In breve

Se hai un portafoglio azionario US puro (100% S&P 500) e vuoi aggiungere una componente difensiva senza toccare l'esposizione al reddito fisso o all'oro (che ho già trattato in [articoli precedenti](/posts/ha-senso-obbligazioni-portafoglio)), quale settore azionario "difensivo" ti dà la migliore protezione? Ho confrontato cinque candidati — **Healthcare (XLV), Consumer Staples (XLP), Utilities (XLU), Min Volatility (USMV), Quality (QUAL)** — su 27 anni di dati storici (1998-2025) contro l'S&P 500 puro, con la componente difensiva testata a tre pesi diversi (10%, 15%, 20%). I quattro risultati principali:

1. **Utilities vince su ogni criterio significativo, su entrambi i periodi testati**. Sui 27 anni (1998-2025) e sui 12 anni recenti (2013-2025) l'aggiunta del 20% di Utilities al portafoglio ha prodotto lo Sharpe più alto, il Calmar più alto, la volatilità più bassa e — sui rolling ventennali — un tasso di successo del 100% contro il puro S&P 500. Sorpresa relativa: il settore che il mercato considera "in declino strutturale" per via della transizione energetica è quello che ha protetto meglio negli ultimi tre decenni.

2. **Healthcare è il "pranzo davvero gratis"**. Aggiungendo Healthcare a qualsiasi peso fino al 20%, il CAGR del portafoglio **resta praticamente identico** all'S&P 500 puro (8,45% invariato a tre cifre decimali), mentre il max drawdown si riduce di **3,4 punti percentuali** e la volatilità di quasi 1 punto. La ragione: Healthcare ha avuto rendimenti storici molto simili all'S&P (che significa "non paghi con CAGR minore") ma correlazione più bassa (che significa "guadagni protezione"). È il pranzo gratis di Markowitz nella sua forma più pulita.

3. **Quality NON è una sleeve difensiva**, contrariamente a quanto crede il retail italiano. Sui dati 2013-2025, aggiungere Quality a un portafoglio S&P 500 **peggiora tutte le metriche di rischio**: max drawdown, Sharpe, Calmar. E l'effetto peggiora al crescere del peso: al 20% di Quality, il Sharpe scende a 0,978 (contro 0,985 del puro S&P), il Calmar cala a 0,560 (contro 0,582), il max drawdown va a -24,7% (contro -23,9%). Quality è, sui numeri, **anti-difensiva**. Il motivo è meccanico ed è raccontato nella terza parte dell'articolo.

4. **Il peso conta, ma non quanto ci si aspetterebbe**. Aumentare la componente difensiva dal 10% al 20% raddoppia i benefici in termini di protezione dal max drawdown — Utilities passa da -49,1% a -47,5% di MDD full period — ma il costo in CAGR è piccolo (Utilities perde 0,16 punti annui). La "dose sweet spot" per un portafoglio full azionario che vuole aggiungere protezione mirata sembra essere intorno al **15-20%**, non il 10% che spesso si legge come standard nella letteratura retail.

L'articolo è strutturato in cinque parti: cosa è una sleeve difensiva, come ho scelto i cinque candidati, il verdetto storico su 27 anni (Livello A), il verdetto sul periodo recente con i due factor Min Vol e Quality (Livello B), il paradosso di Quality raccontato nel dettaglio, e la classifica finale.

## Cosa significa "componente difensiva"

Un portafoglio azionario 100% investito in un indice ampio come l'S&P 500 ha un profilo di rischio ben noto: rendimento composto annuo storico dell'8-10% reale sui periodi lunghi, volatilità intorno al 15% annualizzata, drawdown massimo del -50% nei crash sistemici come 2008. È una scommessa che ha pagato benissimo su orizzonti lunghi ma richiede sopportare cadute violente.

Molti investitori vogliono ridurre l'intensità di queste cadute senza rinunciare troppo al rendimento composto. Le opzioni classiche sono tre:

1. **Aggiungere obbligazioni** (il tradizionale 60/40) — riduce vol e drawdown ma taglia significativamente il CAGR di lungo periodo. Ne ho parlato [qui](/posts/ha-senso-obbligazioni-portafoglio).
2. **Aggiungere oro** — riduce il drawdown nei crash sistemici ma ha rendimento composto reale storicamente basso. Ne ho parlato [qui](/posts/ha-senso-oro-portafoglio).
3. **Aggiungere un settore azionario "difensivo"** — mantiene il portafoglio 100% equity ma sostituisce una parte dell'esposizione al mercato ampio con settori che storicamente hanno beta più bassa e correlazione più bassa con l'S&P 500.

Questa terza strada è quella che testo qui. La domanda operativa è: quale settore azionario difensivo ha davvero funzionato come tale?

## I cinque candidati

Ho scelto cinque settori/factor che la letteratura e il retail italiano considerano "difensivi", ciascuno con un proxy ETF reale che ha storia lunga e liquidità reale. Ecco la tabella dei candidati con i motivi della selezione:

| Sleeve | Proxy ETF | Perché è considerata difensiva | Storia disponibile |
|---|---|---|---|
| **Healthcare** | XLV (Health Care Select Sector SPDR) | Domanda anelastica, poco ciclica; farmaceutica e insurance | 1998+ (27 anni) |
| **Consumer Staples** | XLP (Consumer Staples Select Sector SPDR) | Beni di consumo essenziali (Coca-Cola, P&G, Walmart) | 1998+ (27 anni) |
| **Utilities** | XLU (Utilities Select Sector SPDR) | Servizi pubblici, alta dividend yield, bassa beta | 1998+ (27 anni) |
| **Min Volatility** | USMV (iShares MSCI USA Min Volatility) | Factor moderno: seleziona azioni a bassa volatilità realizzata | 2011+ (14 anni) |
| **Quality** | QUAL (iShares MSCI USA Quality Factor) | Factor moderno: seleziona per ROE alto, debito basso, earnings stabili | 2013+ (12 anni) |

Escludo obbligazioni e oro perché ne ho già scritto in articoli dedicati. Escludo anche settori "controciclici" come Materials o Financials — non sono considerati difensivi dalla maggior parte della letteratura. Includo esplicitamente **Quality** perché è la scelta che il retail italiano fa più spesso quando si parla di "aggiungere protezione al portafoglio", spesso pescando fondi UCITS come iShares Edge MSCI World Quality (IWQU) o Xtrackers MSCI World Quality (XDEQ) — proxy dell'indice MSCI Quality che sui dati testeremo qui.

I tre settori SPDR (XLV, XLP, XLU) hanno storia più lunga e permettono un backtest su 27 anni che include due crash sistemici (2008, 2020) e un decennio di stagflazione lite (anni 2000). I due factor (USMV, QUAL) hanno storia più breve e permettono un backtest solo sui 12 anni recenti (2013-2025), che include il crollo COVID 2020 e il bear market 2022 ma **non** il 2008.

## Il metodo

Confronto quattro configurazioni di portafoglio per ogni sleeve:

- **100% S&P 500** (benchmark, tramite SPY total return)
- **90% SPY + 10% sleeve** (peso "tilt classico" della letteratura)
- **85% SPY + 15% sleeve** (peso intermedio)
- **80% SPY + 20% sleeve** (peso "vera allocazione")

Tutti i portafogli sono **buy & hold puro senza ribilanciamento**, coerentemente con la metodologia standard del blog. I pesi driftano nel tempo (un asset che cresce di più peserà di più alla fine). L'orizzonte del backtest è mensile.

Due livelli di analisi paralleli:

- **Livello A — 1998-2025 (27 anni, 325 osservazioni mensili)**: solo Healthcare, Consumer Staples e Utilities (le tre sleeve con storia lunga). Include finestre rolling 5y, 10y e 20y.
- **Livello B — 2013-2025 (12 anni, 150 osservazioni mensili)**: tutte e cinque le sleeve, incluso Min Vol e Quality. Solo finestre rolling 5y (per USMV avremmo potuto anche 10y ma per QUAL no, e volevo un confronto omogeneo).

Tutti i prezzi sono **Total Return** (dividendi reinvestiti). I dati sono **lordi** — niente TER degli ETF, niente costi di transazione, niente tasse. È la convenzione del blog, e va tenuta a mente quando traduci i numeri in attesa pratica: sui 27 anni un TER medio di 0,3% annuo eroderebbe circa il 10% del capitale finale.

## Livello A — Il verdetto storico su 27 anni

Le equity curves con la sleeve al 10% (peso "tilt classico"):

![Equity curves Livello A](/charts/sleeve-difensiva-migliore/01_equity_curves_livello_A.png)

Difficile distinguerle a occhio nudo. Su 27 anni il 10% di sleeve difensiva sposta il NAV finale di frazioni di punto percentuale. Le vere differenze sono nelle metriche di rischio aggiustato per il rendimento. Ecco i numeri full period con la sleeve al 20% (dove le differenze si vedono meglio):

| Portafoglio | NAV finale | CAGR | Volatilità | Max drawdown | Sharpe | Calmar |
|---|---|---|---|---|---|---|
| 100% S&P 500 | 89.393 $ | 8,45% | 15,06% | **-50,8%** | 0,616 | 0,166 |
| 80% SPY + 20% Healthcare | 89.295 $ | **8,45%** | 14,21% | -47,4% | 0,644 | **0,178** |
| 80% SPY + 20% Consumer Staples | 82.359 $ | 8,12% | 13,73% | -46,5% | 0,640 | 0,175 |
| 80% SPY + 20% Utilities | 85.947 $ | 8,29% | **13,57%** | **-47,5%** | **0,657** | 0,174 |

Quattro cose da leggere in questa tabella.

**Healthcare è matematicamente sorprendente**. Sostituire il 20% di S&P 500 con Healthcare non cambia praticamente niente sul NAV finale — 89.295 dollari contro 89.393 del puro S&P su un capitale iniziale di 10.000 $ investito nel 1998 — ma riduce il max drawdown del 3,4% e la volatilità del 5,7%. È un pranzo davvero gratis perché il rendimento composto di lungo periodo di Healthcare (8,7% circa) è stato quasi identico all'S&P 500, quindi sostituirlo non taglia il CAGR; ma la correlazione fra Healthcare e S&P è stata "solo" 0,75-0,80 in periodi normali e molto più bassa nei crash, quindi la combinazione diversifica.

**Utilities ha il miglior rapporto rendimento-rischio in assoluto**. Sharpe 0,657 contro 0,616 dell'S&P puro (+6,6%). Volatilità 13,57% contro 15,06% (-10%). E il max drawdown è ridotto di 3,3 punti percentuali. Il prezzo è modesto: 0,16 punti annui di CAGR in meno, che su 27 anni cumula a un patrimonio finale del 3,9% più piccolo.

**Consumer Staples sacrifica un po' di più**. CAGR -0,33 punti annui, ma miglior Calmar (0,175) e volatilità bassa. È il difensivo "canonico" che paga con un po' di rendimento la protezione ottenuta.

**Il MDD di tutti e tre è vincolato al 2008**. Il peggior drawdown storico del portafoglio S&P 500 è il -50,8% del 2007-2009. Le tre sleeve difensive lo riducono di 3-4 punti (a -47/-49%), ma non lo evitano. Chi cerca protezione contro un evento tipo Lehman deve andare su asset molto diversi dall'azionario (oro, bond long duration, opzioni put — nessuno dei quali gratis).

### Rolling windows Livello A — la vera prova

Il rischio del "full period" è dipendere troppo dal punto di partenza. Le finestre rolling esplorano tutti i possibili inizi. Distribuzione del CAGR:

![Boxplot CAGR rolling Livello A](/charts/sleeve-difensiva-migliore/03_boxplot_cagr_rolling_A.png)

Tre osservazioni sui percentili delle finestre 5 anni e 10 anni con sleeve al 20%:

**Il peggior caso a 5 anni migliora con la sleeve difensiva**. Il 5° percentile del CAGR rolling 5y del puro S&P 500 è -2,5% annui — cioè nel 5% peggiore delle finestre quinquennali storiche, l'S&P ha reso in media -2,5% l'anno per cinque anni consecutivi. Con Utilities al 20% questo peggior caso migliora a -1,7%, con Healthcare a -2,0%, con Consumer Staples a -1,8%. Non è una piccola differenza per chi ha investito il grosso del capitale in una data sfortunata.

**Sui 10 anni il peggior caso si dimezza quasi**. Il 5° percentile 10y del puro S&P è -1,3% annui; con la sleeve difensiva scende a -0,7/-0,9%. Chi ha investito 10.000 dollari nel S&P 500 nel 1998 e li aveva ancora nel 2008 aveva un patrimonio di poco sotto i 10.000 dollari — la sleeve difensiva avrebbe alzato il valore finale a 9.500-9.700 dollari. Non trasforma un decennio negativo in positivo, ma alleggerisce il peggio.

**Sui 20 anni il peggior caso è positivo per tutti**. Il 5° percentile ventennale del puro S&P 500 è +5,6% annui. Con Utilities al 20% sale a +5,9%. Il "20 anni di S&P che fanno male" non esiste nei dati 1998-2025.

### Win rate Sharpe delle sleeve vs 100% SPY

La metrica più pesante di tutto l'articolo, e la ragione per cui Utilities è dichiarato vincitore:

![Win rate per sleeve](/charts/sleeve-difensiva-migliore/08_win_rate_per_sleeve.png)

| Sleeve al 20% | Win rate Sharpe 5y | Win rate 10y | Win rate 20y |
|---|---|---|---|
| Healthcare | 75% | 93% | **100%** |
| Consumer Staples | 69% | 97% | **100%** |
| Utilities | **88%** | **100%** | **100%** |

**Su tutte le finestre ventennali storiche, aggiungere il 20% di sleeve difensiva ha migliorato lo Sharpe ratio del puro S&P 500 nel 100% dei casi**. Non una singola finestra di 20 anni in cui l'S&P puro ha battuto la versione diversificata sul rapporto rendimento-rischio. È un risultato molto forte.

Sui 10 anni Utilities batte l'S&P puro nel 100% delle finestre — un risultato che nessun'altra sleeve raggiunge. Consumer Staples è al 97%, Healthcare al 93%.

## Livello B — Il paradosso Quality (2013-2025)

Il periodo breve include Min Vol e Quality — i due factor "difensivi moderni" che il retail italiano ha imparato a scegliere per proteggere il portafoglio. I risultati sul full period (12 anni) con le sleeve al 20%:

| Portafoglio | CAGR | Max drawdown | Sharpe | Calmar |
|---|---|---|---|---|
| 100% S&P 500 | 13,93% | -23,9% | 0,985 | 0,582 |
| 80/20 SPY+Utilities | 13,27% | **-21,2%** | **1,016** | **0,626** |
| 80/20 SPY+Healthcare | 13,44% | -21,8% | 0,996 | 0,616 |
| 80/20 SPY+Min Vol | 13,38% | -22,8% | 0,995 | 0,588 |
| 80/20 SPY+Consumer Staples | 13,01% | -22,1% | 0,982 | 0,588 |
| **80/20 SPY+Quality** | **13,84%** | **-24,7%** | **0,978** | **0,560** |

**Il colpo di scena**: al 20% di Quality nel portafoglio, il max drawdown **peggiora** rispetto al puro S&P 500 (-24,7% contro -23,9%), lo Sharpe **peggiora** (0,978 contro 0,985), il Calmar **peggiora** (0,560 contro 0,582). Non è un'oscillazione statistica: guardando i dati progressivi, ogni 5 punti di Quality aggiunti al portafoglio peggiorano tutte e tre le metriche di rischio.

| Peso Quality | Max drawdown | Sharpe | Calmar |
|---|---|---|---|
| 0% (100% SPY) | -23,9% | 0,985 | 0,582 |
| 10% | -24,3% | 0,982 | 0,571 |
| 15% | -24,5% | 0,980 | 0,566 |
| **20%** | **-24,7%** | **0,978** | **0,560** |

Su tutti e tre gli assi del rischio, Quality **amplifica** il problema invece di alleviarlo. È quantitativamente il contrario di una sleeve difensiva.

### Perché Quality è anti-difensiva sui dati recenti

La ragione è meccanica e riguarda la composizione dell'indice MSCI USA Quality. Il metodo di selezione MSCI Quality pesa le azioni per tre parametri fondamentali: ROE alto, leverage basso, earnings stability. Sui dati 2020-2025 questo criterio ha selezionato le stesse mega-cap tech (Apple, Microsoft, Nvidia, Visa, Mastercard, Alphabet) che sono anche le top holding dell'S&P 500 — ma con un peso molto maggiore.

Il portafoglio 80% S&P 500 + 20% Quality diventa quindi, in pratica, **un S&P 500 con sovrappeso sulle stesse 10-15 mega-cap tech**. Non diversifica, concentra. Quando le mega-cap tech soffrono (bear market 2022, dove Meta ha perso il 65% e Amazon il 50%), il portafoglio Quality soffre più del mercato ampio perché la sua concentrazione lo amplifica.

Il paradosso è che Quality funziona teoricamente su un ciclo di mercato di lungo periodo — le aziende di qualità storicamente sopravvivono meglio ai crash duraturi. Ma sui 12 anni 2013-2025 il ciclo dominante è stato "mega-cap tech vs resto" più che "qualità vs qualità bassa", e il factor Quality è stato meccanicamente incapsulato nel primo. Il caveat epistemico è importante: se in futuro il ciclo di mercato cambia (deconcentrazione delle mega-cap, ritorno del value, transizione settoriale), Quality potrebbe tornare a comportarsi come "vera" sleeve difensiva. I dati di oggi non lo confermano.

### Correlazione delle sleeve con l'S&P 500

La lettura complementare del paradosso Quality: la correlazione rolling 36 mesi con l'S&P 500 delle cinque sleeve nel periodo 2013-2025:

![Correlazione con SPY](/charts/sleeve-difensiva-migliore/09_correlazione_con_spy.png)

Quality ha la correlazione più alta di tutte (0,90-0,95 continuativa). Utilities è la più bassa (0,55-0,70). Min Vol sta nel mezzo (0,80-0,85). Healthcare e Consumer Staples oscillano tra 0,75 e 0,85. La correlazione di Quality con l'S&P 500 è così alta che matematicamente **Quality non può diversificare** in modo significativo — se il coefficiente è 0,95, il 95% del movimento di Quality è già spiegato dal movimento dell'S&P 500. Sostituire il 20% di S&P con Quality è come sostituire il 20% di S&P con... un altro 20% di S&P.

## Il trade-off al variare del peso

Il grafico che sintetizza tutta l'analisi in un colpo d'occhio è la relazione CAGR-MDD per ogni sleeve al variare del peso.

![Trade-off CAGR vs MDD Livello A](/charts/sleeve-difensiva-migliore/10_tradeoff_cagr_vs_mdd_A.png)

Ogni linea parte dal punto "100% SPY" comune (asse Y ~8,45%, asse X ~-50,8%) e si sposta verso destra e verso il basso man mano che il peso della sleeve cresce fino al 20%. Le linee che si spostano più a destra (= migliorano il MDD) senza scendere troppo verso il basso (= senza sacrificare CAGR) sono le sleeve migliori.

- **Healthcare** traccia una linea quasi orizzontale — il CAGR resta piatto mentre il MDD migliora. È il classico pranzo gratis.
- **Utilities** si sposta di più verso destra con un CAGR che cala di poco. La linea più efficiente dopo Healthcare.
- **Consumer Staples** ha la pendenza più netta: MDD migliora sensibilmente ma il CAGR cala di più. Trade-off classico.

Per il Livello B (periodo recente, con Min Vol e Quality):

![Trade-off CAGR vs MDD Livello B](/charts/sleeve-difensiva-migliore/11_tradeoff_cagr_vs_mdd_B.png)

Quality è l'unica linea che si sposta verso **sinistra** invece che destra: MDD peggiora al crescere del peso. Immediata prova visiva del paradosso.

## I limiti dell'analisi

Cinque cose da dichiarare onestamente prima di chiudere.

**Il MDD 2008 vincola tutti**. Sui rolling ventennali del Livello A, il max drawdown mediano è -50,8% per il puro SPY e sta tra -47% e -49% per le tre sleeve settoriali. Le sleeve difensive azionarie **non salvano** da un crash sistemico tipo Lehman — lo ammorbidiscono di 2-4 punti, il che è utile ma non trasformativo. Chi cerca protezione asimmetrica contro il crash di coda deve andare su altri asset (oro, bond long duration, put), che hanno però i loro trade-off.

**Livello B copre solo un ciclo di mercato**. Il periodo 2013-2025 è stato dominato dalla leadership delle mega-cap tech USA. Le conclusioni sul Livello B — soprattutto quelle su Quality — potrebbero essere diverse in un ciclo economico differente (deglobalizzazione, ritorno del value, transizione energetica accelerata). Non sto dicendo che Quality tornerà sicuramente difensiva; sto dicendo che i dati che ho non lo escludono. Il regime testato è UN regime, non il regime.

**Dati US puri**. Ho lavorato su ETF settoriali US. Un investitore europeo potrebbe voler testare sleeve difensive globali (MSCI World Health Care, MSCI Europe Consumer Staples). Le differenze in termini di correlazione e MDD sono probabilmente contenute (i settori difensivi globali sono dominati dagli stessi nomi USA), ma il tema meriterebbe un approfondimento dedicato.

**Lordo come sempre nel blog**. Il TER medio degli ETF UCITS settoriali che il retail italiano compra è dello 0,15-0,30% annuo. Sui 27 anni questo cumula a circa 5-8% di erosione del capitale finale — non trascurabile ma piccolo rispetto ai numeri del trade-off. La fiscalità italiana (26% sui capital gain, bollo 0,2%) è più significativa ma è un tema che ho trattato altrove.

**Rolling windows non sono forward-looking**. Il fatto che Utilities abbia vinto nel 100% delle finestre ventennali del 1998-2025 non garantisce che vincerà nei prossimi 20 anni. Il regime dei tassi USA nel 1998-2025 è passato da 5% a 0% e poi a 4,5% — cambiamenti macro fortissimi che hanno influenzato in modo particolare le Utilities (sensitive ai tassi). Il futuro potrebbe portare regimi che i dati non hanno visto.

## Classifica finale e cosa porto a casa

Alla fine di questo esercizio, la classifica delle cinque sleeve difensive testate contro l'S&P 500 puro è la seguente:

**1° posto — Utilities (XLU)**. Vince Sharpe, Calmar, MDD e win rate sia sul periodo lungo (1998-2025) sia su quello breve (2013-2025). Il fatto che vinca su entrambi i periodi la rende la scelta più robusta. La ragione strutturale: la correlazione con S&P 500 di Utilities è la più bassa fra tutte (0,55-0,70), la volatilità del settore è la più bassa (12-14%), il dividend yield storico intorno al 3-4% agisce da cuscinetto nei drawdown. Peso consigliato dai dati: 15-20% del portafoglio full azionario.

**2° posto — Healthcare (XLV)**. Il "pranzo gratis" per definizione: aggiungendo Healthcare al 20% il CAGR resta invariato e il MDD si riduce di 3,4 punti. Peso consigliato: 15-20%. Non ha lo Sharpe più alto in assoluto (perde con Utilities di poco), ma è più semplice da "vendere" al lettore perché il costo in CAGR è zero.

**3° posto ex aequo — Consumer Staples (XLP)**. Classica difensiva "che funziona": paga con un po' di CAGR una protezione discreta. Non ha nessuna dimensione dominante ma è affidabile. Peso consigliato: 15%.

**3° posto ex aequo — Min Volatility (USMV)**. Solida sul periodo recente ma la storia è troppo breve per essere certi. Se il factor Min Vol continua a comportarsi come dovrebbe, la protezione è reale. Ma i dati del 2008-2011 mancano.

**5° posto — Quality (QUAL)**. **Anti-difensiva sui dati 2013-2025**. Contrariamente alla narrativa che il retail italiano ha adottato, Quality non diversifica dall'S&P 500 perché la sua metodologia di selezione produce di fatto un sovrappeso sulle stesse mega-cap che dominano l'S&P. Se possiedi Quality nel tuo portafoglio pensando che ti dia protezione, sei fuori strada rispetto ai dati storici recenti. Peso consigliato: 0%, o comunque non pensare a Quality come sleeve difensiva.

Cinque cose da portare a casa da tutto l'esercizio:

**1. Se vuoi una sleeve difensiva azionaria, la risposta è Utilities**. Ha battuto tutte le alternative in ogni criterio significativo, su entrambi i periodi testati. Il fatto che il mercato la consideri un settore "morto" (transizione energetica, rate sensitivity) non è confermato dai dati storici — anzi, è probabilmente la ragione per cui esiste ancora un premio al rischio da estrarre.

**2. La dose sweet spot è 15-20%, non il 10% standard**. Con solo il 10% l'effetto sulla protezione è visibile ma modesto. Al 20% l'effetto è più significativo e il costo in CAGR resta contenuto (0,15-0,33 punti annui). Non tenere sotto il 15% se vuoi vedere davvero la protezione.

**3. Non usare Quality come sleeve difensiva**. Sui dati del ciclo attuale (2013-2025), l'aggiunta di Quality al portafoglio S&P 500 peggiora tutte le metriche di rischio. La narrativa retail su Quality come "settore difensivo" è quantitativamente smentita dai dati che ho analizzato.

**4. Nessuna sleeve azionaria salva dal crash tipo 2008**. Riducono il MDD di 2-4 punti percentuali, non di 20. Chi cerca protezione asimmetrica contro le code negative estreme deve andare su asset non-azionari.

**5. Il vero costo dell'aggiunta di una sleeve difensiva è minuscolo, il beneficio è modesto ma reale**. Utilities al 20% costa 0,16 punti di CAGR annui e dà 3,3 punti di MDD in meno e 6,6% di Sharpe in più. Non è un cambio radicale del profilo di portafoglio, ma è un miglioramento marginale che ha resistito a due decenni e mezzo di regimi diversi. Per un investitore che ha già il portafoglio in ordine e vuole affinarlo, è un buon uso del 15-20% del capitale.

In sintesi: se stai pensando di aggiungere protezione al tuo portafoglio azionario US puro senza toccare bond o oro, la scelta corretta secondo i dati è **Utilities al 15-20%**. Se vuoi il "pranzo gratis" perfetto (zero costo in CAGR, protezione reale), la scelta è **Healthcare al 15-20%**. Se hai Quality nel portafoglio pensando che sia difensiva, ripensa alla scelta — i dati suggeriscono che stai concentrando invece di diversificare.
