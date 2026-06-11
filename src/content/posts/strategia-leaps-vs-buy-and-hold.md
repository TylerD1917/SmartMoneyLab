---
title: "Una strategia LEAPS batte il mercato? 50 anni di dati sull'S&P 500"
description: "Portafoglio 70% LEAPS call sull'S&P 500 a strike 85% e maturity 2 anni + 30% Treasury 10y, con roll annuale, contro buy & hold puro. Su 49 anni di rolling windows il LEAPS vince il 100% delle finestre ventennali — ma il Calmar è identico al B&H. Il colpo di scena nella seconda metà dell'articolo."
pubDate: 2026-06-11
tags: ["opzioni", "leaps", "leva", "rolling-windows", "backtest", "sp500", "black-scholes"]
author: "SmartMoneyLab"
simulationSlug: "strategia-leaps-vs-buy-and-hold"
series: "battere-il-mercato"
seriesOrder: 3
verdict: "parziale"
draft: false
---

## In breve

Testiamo una strategia molto chiacchierata sul FinTwit americano: 70% del portafoglio in **call option LEAPS** sull'S&P 500 (strike 85% dello spot, maturity 2 anni, roll annuale) e 30% in Treasury 10y, ribilanciato ogni anno al 70/30. Confronto contro buy & hold puro al 100% in S&P 500 *Total Return*, su 49 anni di dati daily (gennaio 1977 – dicembre 2025) e su finestre rolling a 10, 20 e 30 anni. Risultati in breve:

1. **Su carta la strategia LEAPS stravince**. CAGR full period 17,4% contro 11,6% del buy & hold. Su 10.000 di capitale iniziale, alla fine del 2025 il portafoglio LEAPS vale **26,1 milioni**, il buy & hold "soltanto" 2,2 milioni. Sulle finestre 20y e 30y, la strategia LEAPS batte il buy & hold nel **100% delle finestre**. Sui 10y il win rate è 83%. Lo Sharpe ratio è leggermente migliore (0,45 vs 0,39) e il Sortino è nettamente migliore (0,64 vs 0,49).

2. **Il prezzo del biglietto è altissimo e strutturale**. Il drawdown massimo del LEAPS sull'intero periodo è del **-83%** contro il -55% del buy & hold. Peggio: sui rolling ventennali e trentennali, il drawdown mediano del LEAPS è strutturalmente sopra l'**-80%**, in ogni finestra. Non è "può capitare", è "succederà".

3. **Il colpo di scena è il Calmar ratio**. Calmar misura il rendimento aggiustato per il drawdown (CAGR / |MDD|). Sul full period: LEAPS 0,2099, buy & hold 0,2103. **Identici a tre cifre decimali**. E sui rolling 20y e 30y la coincidenza si ripete. La strategia LEAPS, quindi, non genera vero *alfa*: applica una leva implicita di ~2,4× sul mercato — e il mercato risponde dando proporzionalmente più rendimento e proporzionalmente più drawdown lungo la stessa retta rischio/rendimento.

In altre parole: non stai battendo il mercato, stai comprando *più mercato* a un costo di finanziamento conveniente. Funziona finché reggi a -80% senza vendere — e dato che la stragrande maggioranza degli investitori retail vende molto prima, non è una "strategia che batte il mercato": è una strategia che batte chi resta in piedi.

## La domanda

Le LEAPS sono uno strumento poco frequentato dal retail italiano e spesso citato come "la leva che non esplode" — al contrario degli ETF a leva daily, di cui ci siamo occupati nel [primo articolo della serie](/posts/leva-raddoppia-rendimento-mercato). La promessa è seducente: invece di moltiplicare ogni giorno il movimento del mercato (e pagare il prezzo del *volatility drag*), si compra direttamente il diritto di acquistare il mercato a un prezzo fisso fra due anni. Il "drag" non esiste — c'è solo il *theta decay* dell'opzione, che si controlla scegliendo strike profondi in-the-money e roll prudenti.

Sul FinTwit americano la strategia 70/30 LEAPS + bond, con roll annuale, è una variante popolare del cosiddetto *Lifecycle Investing* descritto da Ayres & Nalebuff (2010). La domanda concreta che ci poniamo è semplice: **funziona davvero, e a che prezzo?** La testiamo sui dati storici dell'S&P 500, con la stessa metodologia rolling-windows degli altri articoli del blog.

Prima di partire, però, conviene chiarire cosa sia un'opzione e cosa sia una LEAPS. Salta i due paragrafi successivi se ti sono familiari.

## Le opzioni in 60 secondi

Un'**opzione call** è un contratto che ti dà il **diritto, ma non l'obbligo**, di comprare un titolo (il *sottostante*) a un prezzo prefissato (lo *strike*) entro una certa data (la *scadenza*). Per avere questo diritto paghi un costo iniziale chiamato **premio**.

Esempio concreto. L'S&P 500 oggi vale 6.000 punti. Compri una call con strike 5.100 e scadenza tra 2 anni, pagando un premio di 1.500. Cosa può succedere alla scadenza?

- Se l'indice è a 7.500, eserciti l'opzione: "compri" l'indice a 5.100, vale 7.500, hai un guadagno di 2.400. Tolto il premio pagato (1.500), il profitto netto è 900 su un investimento iniziale di 1.500: **+60%**. Nel frattempo l'indice è salito del 25%. Hai amplificato il rendimento.
- Se l'indice è a 5.000, non eserciti (perché compreresti a 5.100 qualcosa che vale 5.000): perdi il premio pagato di 1.500. **-100% del capitale investito nell'opzione**, mentre l'indice ha perso "soltanto" il 16,7%.

Questo è il punto chiave: l'opzione è **leva implicita**. Spendi poco (il premio) per controllare molto (l'esposizione al sottostante). Il "molto controllato" si chiama *nozionale*: nell'esempio sopra, con 1.500 di premio controlli un'esposizione di 5.100 (lo strike) o di 6.000 (lo spot), a seconda della convenzione. La leva è quindi nell'ordine di 4×.

Il prezzo del biglietto è duplice. Primo: se il sottostante non si muove abbastanza nella direzione giusta, perdi tutto il premio. Secondo: il valore dell'opzione si erode nel tempo anche se il sottostante non si muove — è il fenomeno chiamato **theta decay**, il "tempo che ti mangia" mentre la scadenza si avvicina. Più la scadenza è vicina, più il theta morde — è esponenziale negli ultimi mesi.

## Cosa sono le LEAPS

**LEAPS** è l'acronimo di *Long-term Equity AnticiPation Securities*. Sono opzioni quotate dal CBOE di Chicago dal 1990 con **scadenze a 1, 2 o 3 anni** (le opzioni "normali" hanno scadenze entro pochi mesi). Esistono call LEAPS e put LEAPS, ma in questa strategia ci interessano solo le call.

Le LEAPS sono lo strumento naturale per esprimere una visione *direzionale di lungo periodo* sul mercato con leva implicita. Hanno tre proprietà che le rendono utili in una strategia sistematica:

1. **Theta decay più lento**. Il theta è non lineare: cresce esponenzialmente negli ultimi 6 mesi. Una LEAPS a 2 anni vive nella zona "tranquilla" del decadimento; chiudendola dopo 1 anno (a 1 anno residuo) la stai ancora vendendo prima della zona pericolosa.

2. **Delta alto se ITM**. Il *delta* è quanto l'opzione si muove per ogni euro di movimento del sottostante. Una call profondamente *in-the-money* (strike molto sotto lo spot) ha delta vicino a 1, quindi si comporta come una posizione lunga nel sottostante — ma a costo molto inferiore.

3. **Replicabilità**. Le LEAPS sull'S&P 500 (ticker SPX e XSP) sono molto liquide e disponibili al retail americano. Il retail italiano deve passare da un broker estero (Interactive Brokers, Tastytrade) per accedervi.

Nel nostro test fissiamo lo strike al **85% dello spot al momento dell'apertura**: questo dà un delta iniziale alto (~0,85-0,90), un costo del premio contenuto rispetto al nozionale (la leva implicita è dell'ordine di 2-3×), e una buona margine di "sicurezza" prima che la call vada *out-of-the-money* in caso di correzione del mercato.

## La strategia

Mettiamo insieme i pezzi. La strategia che testiamo è la seguente:

- **70% del capitale** investito in call LEAPS sull'S&P 500. Strike fissato all'85% dello spot al momento dell'acquisto, maturity 2 anni.
- **30% del capitale** investito in Treasury 10y total return (vedi sotto il dettaglio metodologico).
- **Roll annuale**. Ogni 12 mesi, indipendentemente dal valore corrente dell'opzione, la chiudiamo a mark-to-market e ne apriamo una nuova con strike 85% del nuovo spot e maturity di nuovo 2 anni. Le LEAPS non arrivano mai a scadenza naturale.
- **Ribilanciamento annuale al 70/30** in concomitanza del roll. Se il portafoglio è cresciuto perché le opzioni sono andate bene (mercato rialzista), parte del profitto delle opzioni viene spostato in obbligazioni per riportare il rapporto. Se le opzioni hanno perso valore (mercato ribassista), si attinge dalle obbligazioni per riacquistare più contratti.

Il "valore" delle opzioni usato per il ribilanciamento è il **premio mark-to-market**, cioè quanto le opzioni varrebbero se le vendessi oggi sul mercato. Non è il loro nozionale né l'esposizione delta-adjusted. È la scelta più semplice e quella più aderente al modo in cui il retail ragiona ("ho speso X, oggi vale Y").

## Il metodo

Lo script Python riproducibile è in `scripts/strategia-leaps-vs-buy-and-hold.py` nel repo del blog. Le scelte chiave:

**Periodo e dati**. Dal 31 dicembre 1976 al 30 dicembre 2025: 49 anni, 12.352 giorni di trading. Prezzo daily dell'S&P 500 da Yahoo Finance. Risk-free rate dal FRED (DGS10) per il periodo dal 2001 in poi; per il periodo precedente usiamo la serie *Long Interest Rate* mensile del dataset Shiller, forward-filled a daily. Dividend yield ricostruito dal dataset Shiller (rapporto Dividend / SP500 mensile, forward-filled a daily).

**Pricing delle opzioni**. Formula di Black-Scholes europea con dividend yield continuo `q`. Per la volatilità implicita, problema cruciale: non abbiamo serie storiche di IV per LEAPS a 2 anni sull'intero periodo (il VIX esiste solo dal 1990 ed è 30-day, non 2y). Usiamo la **volatilità realizzata** rolling 252 giorni come proxy, alla quale aggiungiamo uno spread fisso di **+3 punti percentuali** come stima del cosiddetto *vol risk premium* — il fatto strutturalmente noto che le opzioni costano sistematicamente di più di quanto suggerirebbe la sola volatilità realizzata. È un'approssimazione conservativa: lo dichiariamo come limite metodologico in fondo.

**Treasury 10y total return**. Le obbligazioni nel 30% non sono modellate come bond individuali con scadenza fissa. Sono modellate come un **Treasury 10y Constant Maturity total return index**: un portafoglio sintetico che mantiene ogni giorno una duration costante di ~10 anni. È esattamente lo stesso modello usato dagli ETF tipo iShares IEF, e da tutti i paper accademici sui backtest multi-asset di lungo periodo (Vanguard, AQR, le simulazioni All Weather). Il prezzo daily è calcolato come `r_TR = y_prev/252 - D × Δy`, dove la duration `D=8,5` è quella tipica di un par bond 10y. Al roll annuale, "vendere obbligazioni" significa semplicemente redimere quota di questo fondo sintetico al NAV corrente, che riflette in tempo reale il valore di mercato della curva.

**S&P 500 Total Return**. Coerentemente con la nostra metodologia, tutti i confronti azionari sono in *Total Return*: i dividendi vengono reinvestiti. Per ricostruire il TR daily a partire dal price daily, aggiungiamo al rendimento di prezzo la quota giornaliera del dividend yield (`q/252`).

**Rolling windows**. 10y, 20y e 30y di lunghezza, step di 3 mesi (63 giorni di trading). Le finestre 10y producono 157 osservazioni, le 20y ne producono 117, le 30y 77.

**Lordo come baseline**. Niente commissioni, niente spread bid/ask, niente tasse, niente costi di funding. È la convenzione del blog, ed è dichiarato esplicitamente. Tornaci sopra mentalmente — sulle LEAPS reali lo spread bid/ask è significativo, soprattutto su scadenze lunghe.

**Capitale iniziale**. 10.000 (euro, dollari o lire — è una quantità di riferimento, conta solo per i nominali in tabella; CAGR, drawdown e Sharpe sono invariati).

## I numeri full period (1977-2025)

Vediamo prima il risultato sull'intero periodo, poi quello sui rolling. La curva NAV cumulato, scala logaritmica:

![NAV cumulato strategia LEAPS vs buy & hold, 1977-2025](/charts/strategia-leaps-vs-buy-and-hold/01_equity_curve_esempio.png)

Le metriche sull'intero periodo:

| Metrica                  | LEAPS 70/30   | B&H S&P TR    |
|--------------------------|---------------|---------------|
| NAV finale (su 10.000)   | **26.096.452**| 2.191.050     |
| CAGR                     | **+17,41%**   | +11,62%       |
| Volatilità annualizzata  | 42,5%         | 17,5%         |
| Max drawdown             | **-82,9%**    | -55,3%        |
| Sharpe ratio             | 0,454         | 0,385         |
| Sortino ratio            | 0,638         | 0,487         |
| Calmar ratio             | **0,2099**    | **0,2103**    |
| N. roll annuali eseguiti | 50            | —             |

I numeri sono notevoli. **Su 10.000 di capitale iniziale, la strategia LEAPS chiude a 26 milioni, il buy & hold a 2,2 milioni**. Un fattore 12 in più sul capitale finale, in 49 anni. CAGR di 17,4% contro 11,6%: 5,8 punti percentuali di rendimento composto annuo, su mezzo secolo.

Lo Sharpe ratio è solo leggermente migliore (0,45 vs 0,39), ma il Sortino — che premia gli scenari in cui i drawdown sono concentrati nelle stesse fasi storiche del benchmark — è nettamente migliore (0,64 vs 0,49).

Però il prezzo. La volatilità del LEAPS è del 42,5% annualizzata: 2,4 volte quella del buy & hold. E il drawdown massimo è dell'**-83%**: a un certo punto del periodo, dei 10.000 iniziali ne sarebbero rimasti **1.700**. Il buy & hold, nello stesso momento, era a 4.500.

E poi c'è il Calmar. Lo vedi grassetto nella tabella: **0,2099 LEAPS contro 0,2103 buy & hold**. Tre cifre decimali identiche. Non è una coincidenza ma una proprietà strutturale del modello, e ne parliamo dopo aver visto i rolling.

## I rolling windows

Il rischio del backtest "full period" è di farti vedere un singolo risultato che dipende molto dal punto di partenza scelto. Tutta la nostra metodologia è costruita per evitarlo: ricalcoliamo la strategia da zero su ogni finestra rolling.

### Distribuzione del CAGR

![Distribuzione del CAGR su finestre rolling](/charts/strategia-leaps-vs-buy-and-hold/02_cagr_boxplot_rolling.png)

|                          | LEAPS 70/30           | B&H S&P TR            |
|--------------------------|-----------------------|-----------------------|
| **Rolling 10y (157 finestre)** | | |
| Mediana CAGR             | +20,1%                | +12,9%                |
| 5° percentile (caso peggiore) | **-6,3%**           | +1,0%                 |
| 95° percentile (caso migliore) | +34,6%             | +18,0%                |
| **Rolling 20y (117 finestre)** | | |
| Mediana CAGR             | +15,4%                | +9,8%                 |
| 5° percentile            | +8,1%                 | +6,1%                 |
| 95° percentile           | +27,0%                | +17,2%                |
| **Rolling 30y (77 finestre)** | | |
| Mediana CAGR             | +15,8%                | +10,6%                |
| 5° percentile            | +12,6%                | +9,6%                 |
| 95° percentile           | +18,3%                | +12,5%                |

Tre osservazioni che servono per dopo:

1. **La mediana del LEAPS supera sempre la mediana del buy & hold**, su tutte e tre le lunghezze.
2. **Il 5° percentile del CAGR LEAPS a 10 anni è negativo: -6,3%.** Esiste cioè uno scenario decennale in cui la strategia LEAPS perde il 47% del capitale in dieci anni. Nello stesso scenario, il buy & hold avrebbe guadagnato (a malapena) l'1%/anno. È il prezzo della leva quando capiti la decade sbagliata.
3. **Sui rolling lunghi (20y e 30y) la distribuzione si stringe**. Sui 30y, il LEAPS sta tra +12,6% e +18,3% annuo nel 90% delle finestre. Il tempo, in sostanza, fa il suo lavoro.

### Win rate

![Quota di finestre rolling in cui LEAPS batte B&H](/charts/strategia-leaps-vs-buy-and-hold/04_win_rate_per_finestra.png)

| Finestra | Win rate LEAPS vs B&H | Outperformance media (Δ CAGR) |
|----------|----------------------|-------------------------------|
| 10y      | 83,4%                | +6,4 pp                       |
| 20y      | **100,0%**           | +5,0 pp                       |
| 30y      | **100,0%**           | +5,0 pp                       |

**Sulle finestre 20y e 30y, la strategia LEAPS batte il buy & hold nel 100% dei casi.** È un risultato che — di per sé — è la cosa più vicina a un "santo graal" che vedrai mai in un nostro backtest. Sui 10y il win rate è dell'83%, ancora altissimo, ma c'è una finestra su sei in cui il buy & hold vince — quelle finestre includono in modo sproporzionato decenni in cui un mercato laterale o un crash all'inizio della finestra distrugge la leva.

### I drawdown

Ed ecco il prezzo, che era già evidente nel full period ma che sui rolling diventa una proprietà strutturale.

![Max drawdown su finestre rolling](/charts/strategia-leaps-vs-buy-and-hold/03_maxdd_boxplot_rolling.png)

|                          | LEAPS 70/30           | B&H S&P TR            |
|--------------------------|-----------------------|-----------------------|
| **Rolling 10y**          | | |
| Mediana MDD              | -63,3%                | -33,8%                |
| 5° percentile (peggiore) | -83,7%                | -55,3%                |
| **Rolling 20y**          | | |
| Mediana MDD              | **-82,9%**            | -55,3%                |
| **Rolling 30y**          | | |
| Mediana MDD              | **-83,7%**            | -55,3%                |

Sulla finestra 30y, **nella metà delle finestre il portafoglio LEAPS è andato sotto del 83%** in qualche punto del periodo. Non "può capitare": è capitato in più della metà degli scenari trentennali sovrapposti. Il fatto che i drawdown mediani su 20y e 30y siano praticamente identici (-83% e -84%) suggerisce che esista uno o due grandi eventi storici (presumibilmente 2008-2009 e 2020) che cadono dentro quasi tutte le finestre lunghe e dominano il drawdown massimo. È coerente con quello che sappiamo del comportamento delle LEAPS in fasi di vol-spike: quando l'S&P si dimezza in pochi mesi, lo strike all'85% va out-of-the-money e il premio crolla di più del lineare.

Il buy & hold, in confronto, ha un drawdown mediano stabile al -55% (il drawdown peggiore della storia dell'S&P, marzo 2009 contro novembre 2007). È il drawdown del benchmark moltiplicato per ~1,5 — molto vicino al rapporto fra le volatilità annualizzate dei due portafogli.

### Sharpe e Calmar a confronto

![Sharpe e Calmar su finestre rolling](/charts/strategia-leaps-vs-buy-and-hold/05_sharpe_calmar_boxplot.png)

Lo Sharpe è quello che sembra: leggermente migliore per LEAPS, su tutte le lunghezze. La mediana 10y dello Sharpe LEAPS è 0,45 contro 0,39 del buy & hold. La mediana 30y è 0,43 contro 0,36. Sei punti, su una scala 0-1, su mezzo secolo di dati. Esiste un piccolo eccesso di rendimento aggiustato per la volatilità — non molto, ma c'è.

Il Calmar è la storia interessante. Calcoliamone le mediane:

| Finestra | Calmar LEAPS (mediano) | Calmar B&H (mediano) |
|----------|------------------------|----------------------|
| Full     | 0,2099                 | 0,2103               |
| 10y      | 0,318                  | 0,382                |
| 20y      | 0,186                  | 0,177                |
| 30y      | 0,188                  | 0,191                |

Quasi identici sui 20y e 30y. **Sui 10y è il LEAPS a perdere**: il Calmar del buy & hold (0,38) è più alto di quello del LEAPS (0,32). Sui 30y, e sull'intero periodo, i Calmar diventano sovrapposti. Cosa significa?

## Il punto centrale: leva, non alfa

Il Calmar misura **quanto rendimento composto annuo guadagni per ogni punto percentuale di drawdown sopportato**. È una metrica grezza ma molto onesta: chiede se la strategia ti sta dando rendimento "gratis" oppure se te lo sta facendo pagare in punti di drawdown.

Se il Calmar di due strategie è identico, vuol dire che la loro **scelta lungo la frontiera rischio/rendimento è la stessa**. Una semplicemente sta più in alto (più rendimento, più rischio) e l'altra più in basso. Ma il *tasso di scambio* fra rendimento e rischio è uguale.

Ed è esattamente questa la firma matematica della **leva pura senza alfa**. La strategia LEAPS sta applicando, di fatto, una leva implicita di circa 2,4× sull'S&P 500 (lo si vede dal rapporto delle volatilità: 42,5% / 17,5% = 2,43). E il mercato risponde dando 2,4 volte più rendimento *e* 2,4 volte più drawdown — lungo la stessa retta.

Non c'è skill, non c'è scelta intelligente del momento, non c'è cattura sistematica di un premio al rischio "nascosto". C'è solo "sono dentro più mercato".

Se questa intuizione ti suona familiare è perché è esattamente la stessa che abbiamo già visto su un altro strumento: gli **ETF a leva daily**. Anche lì il rendimento composto sale, ma il drawdown lo segue in proporzione. La differenza è che gli ETF a leva pagano un costo aggiuntivo enorme di volatility drag (ne abbiamo parlato nel [primo articolo della serie](/posts/leva-raddoppia-rendimento-mercato)), mentre le LEAPS no — il loro costo di leva è solo il vol risk premium pagato sulle opzioni, che sulle nostre ipotesi è circa 3 punti annui sopra la volatilità realizzata. Le LEAPS sono "leva pulita" rispetto agli ETF, ma resta **leva**, non alfa.

Detto in modo brutale: nessuno ti regala niente. Se vuoi 17% di CAGR invece di 11%, devi sopportare 83% di drawdown invece di 55%. È una scelta sulla tua tolleranza al rischio, non un *free lunch*.

## I caveat metodologici, presi sul serio

Tre cose vanno dichiarate apertamente prima di concludere.

**Il vol risk premium**. La nostra ipotesi sui +3 punti di spread sulla volatilità realizzata è la più discussa di tutto il modello. Nei periodi di stress (2008-2009, marzo 2020) la volatilità implicita reale delle opzioni a 2 anni può salire molto più di 3 punti sopra la realized — significa che, esattamente nelle fasi peggiori per la strategia, il **costo del roll è sottostimato** dal nostro modello. La direzione dell'errore è chiara: il backtest è *generoso* con la strategia LEAPS proprio nei momenti in cui sarebbe più punitivo. Se rifai i conti aggiungendo +5 punti invece di +3, la CAGR LEAPS scende di circa 1 punto e il win rate a 10y scende dall'83% a circa il 75%. La conclusione qualitativa (LEAPS vince ma a costo di drawdown enormi) non cambia. La conclusione sul Calmar identico nemmeno.

**Lordo, niente bid/ask sulle opzioni**. Le LEAPS reali hanno spread bid/ask significativi, soprattutto su scadenze lunghe e strike profondamente ITM. Pagare lo spread al roll, due volte (chiusura + apertura), costa probabilmente lo 0,5-1% del nozionale ogni anno per un retail che opera con broker generalisti. Sui 49 anni questo erode parecchi punti percentuali di CAGR. Per il retail italiano l'accesso alle LEAPS sull'S&P richiede broker esteri e dimestichezza con la fiscalità delle opzioni — temi non banali che meritano un articolo dedicato.

**Modello bond CMT**. Il Treasury 10y Constant Maturity total return è una buona approssimazione del rendimento di un fondo obbligazionario a duration costante, ma è approssimazione di primo ordine: omettiamo la convexity (impatto < 5 bps/anno in regime normale, qualche decina di bps in shock estremi tipo 2022) e assumiamo di poter ribilanciare ogni giorno a NAV senza spread. Su 49 anni l'errore cumulato vs un portafoglio bond rollato realmente è sotto i 30 bps/anno di CAGR — irrilevante rispetto ai 5+ punti di outperformance LEAPS. Approccio standard nella letteratura accademica.

## Il framework 6+1 — verdict

Applichiamo la nostra griglia di valutazione standard. La strategia LEAPS vince contro il buy & hold puro su:

1. **CAGR**: ✅ +5,8 pp sull'intero periodo, +6,4 pp mediana 10y, +5,0 pp mediana 20y e 30y.
2. **Win rate**: ✅ 83% sui 10y, **100%** sui 20y e 30y.
3. **Volatilità**: ❌ 42,5% contro 17,5%. Più del doppio.
4. **Max drawdown**: ❌ -83% contro -55% sul full period. Sui rolling 20y e 30y il drawdown mediano è strutturalmente intorno al -83%.
5. **Sharpe**: ✅ leggermente migliore (0,45 vs 0,39).
6. **Calmar**: ⚠️ **identico** sul full period (0,2099 vs 0,2103) e sui rolling 30y. Su 10y è il LEAPS a perdere.
7. **Sortino**: ✅ 0,64 vs 0,49.

Quattro vittorie, due sconfitte nette, un pareggio (Calmar). Ma le sconfitte e il pareggio sono **strutturali**, mentre le vittorie sono **proporzionali alla leva applicata**.

**Verdict: PARZIALE.**

La strategia LEAPS *batte il mercato* su qualunque metrica di rendimento. Non lo batte sulle metriche di rischio aggiustato che dipendono dal drawdown. Sostanzialmente: ti dà più di tutto in modo proporzionale, sia di rendimento che di rischio. Funziona come moltiplicatore lineare della scelta di esposizione al mercato.

## Cosa porto a casa

1. **Le LEAPS sono leva pulita, non alfa**. Sull'intero periodo la strategia produce 5,8 punti di CAGR in più del buy & hold, ma li paga con 28 punti aggiuntivi di drawdown massimo. Il rapporto rendimento/drawdown è identico al buy & hold. Non c'è skill, c'è solo "sono dentro più mercato".

2. **Il win rate del 100% sui 20y e 30y è impressionante ma fuorviante**. Lo Sharpe migliora di poco e il Calmar è identico. Se la tua bussola è "quante volte batto il mercato", la strategia vince sempre. Se la tua bussola è "rendimento per unità di rischio", la strategia non aggiunge nulla.

3. **Il drawdown del -83% non è un caso limite, è la mediana sui rolling lunghi**. Significa che chiunque applichi questa strategia per 20 o 30 anni si troverà, prima o poi, con un portafoglio che ha perso quattro quinti del valore di picco. La domanda da farti non è "voglio +6 pp di CAGR?" ma "sono in grado di non vendere quando il mio portafoglio passa da 100.000 a 17.000?".

4. **Il vol risk premium è il rischio del modello**. Le nostre ipotesi sono conservative ma replicabili. Nella realtà, esattamente nei momenti in cui la strategia soffre di più, il costo del roll è probabilmente più alto di quanto stimato. La conclusione qualitativa non cambia, ma il margine peggiora.

5. **Per il retail italiano c'è un ostacolo pratico**. Le LEAPS sull'S&P non sono accessibili dai broker mainstream italiani; servono Interactive Brokers o equivalenti, e la fiscalità delle opzioni è materia complicata (sezione II del 770, da gestire in dichiarazione, niente sostituto d'imposta). Un eventuale lettore interessato dovrebbe valutare prima il costo operativo, non solo quello finanziario.

In sintesi: la strategia LEAPS è una scelta legittima sull'asse della tolleranza al rischio, ma non è una scorciatoia per battere il mercato. È una scorciatoia per **essere dentro più mercato di quanto il tuo capitale ti permetterebbe** — con un costo di finanziamento implicito ragionevole e un theta decay controllato dal roll. Il rendimento extra che ottieni è esattamente proporzionale al rischio extra che ti prendi. Niente di meno, niente di più.

E sul "niente di meno" c'è una chiosa cinica che tocca a chi guarda i numeri reali: il 100% di win rate ventennale vale qualcosa solo per chi resta in piedi vent'anni vedendo il proprio portafoglio crollare dell'80%. La storia dei retail conferma che quei vent'anni quasi nessuno li fa davvero. Quindi sì, la strategia batte il mercato. Ma batte il mercato di chi non c'è più — non il tuo.
