---
title: "Il mio portafoglio nel 2024: che ritorno possiamo aspettarci? 22 anni di backtest e Monte Carlo"
description: "Backtest su 22 anni del mio portafoglio reale (13 asset) contro S&P 500 e MSCI World, più Monte Carlo a 10/20/30 anni. CAGR +2,9pp sopra S&P, ma c'è un bias del backtest da dichiarare."
pubDate: 2026-06-13
tags: ["portafoglio", "backtest", "monte-carlo", "rolling-windows", "pac", "asset-allocation", "etf"]
author: "SmartMoneyLab"
simulationSlug: "portafoglio-personale-backtest"
draft: false
---

## In breve

Inauguro una nuova famiglia editoriale del blog — "test di portafogli reali". Il primo soggetto è il mio: 13 asset (S&P, Nasdaq, MSCI World, EM, Asia, Europa, oro, small cap, healthcare, energia tradizionale + clean + nucleare, Bitcoin + tematici tech) con allocazione target che ho disegnato a novembre 2024 per intercettare cinque-dieci anni di trend di mercato. Capitale iniziale 10.000 € o, in alternativa, PAC da 200 €/mese. L'ho testato su 22 anni di dati storici (aprile 2003 – dicembre 2025) e proiettato a 10, 20 e 30 anni con una simulazione Monte Carlo a 10.000 traiettorie. I numeri principali in apertura:

1. **Sul backtest lungo (22 anni) il portafoglio batte i benchmark di una distanza significativa**. CAGR del portafoglio 14,30% contro 11,36% dell'S&P 500 TR e 9,45% del MSCI World TR. Su 10.000 € investiti in lump sum nel 2003, alla fine del 2025 il portafoglio chiude a **204.776 €**, l'S&P a 113.674 €, il MSCI World a 76.771 €. Il PAC da 200 €/mese (54.400 € versati in tutto) finisce a **396.541 €** per il portafoglio, 273.178 € per l'S&P, 199.526 € per il MSCI World.

2. **Non è leva, è diversificazione che funziona**. A differenza della strategia LEAPS che ho testato [nell'articolo precedente](/posts/strategia-leaps-vs-buy-and-hold), dove la "vittoria" sul CAGR era pagata da una proporzionale punizione sul drawdown (Calmar identici), qui il drawdown massimo del portafoglio è **leggermente migliore** dei benchmark (-49,5% contro -50,8%) nonostante una volatilità più alta di 2,8 punti. Il Calmar (CAGR/|MDD|) del portafoglio è 0,289 contro 0,224 dell'S&P e 0,186 del MSCI World. C'è alfa genuino, non solo leva.

3. **Il Monte Carlo a 20 anni dice 71% di probabilità di battere l'S&P, 82% di battere il MSCI World**. Mediana del NAV finale a 20 anni partendo da 10.000 €: portafoglio **147.630 €**, S&P 84.769 €, MSCI World 60.444 €. Coda destra (p95) del portafoglio: 696.748 €, contro 239.679 € dell'S&P. Coda sinistra (p5): 40.571 € contro 28.784 € dell'S&P. L'asimmetria del payoff è favorevole sia nella coda sinistra che nella coda destra.

4. **Il caveat metodologico è enorme e va sopra a tutto**. Il portafoglio è stato disegnato nel 2024 conoscendo già i trend che hanno premiato gli ultimi 22 anni (super-cycle tech, boom EM dei primi 2000, oro come bene rifugio, healthcare come settore difensivo). Il backtest dimostra "se i prossimi 22 anni assomigliano agli ultimi 22, vinci". Non dimostra "vincerai i prossimi 22 anni". È una **scommessa strutturata sul fatto che il regime regga**, non una garanzia.

Tre parti nell'articolo: presentazione del portafoglio (cosa c'è e perché), backtest sui dati reali (cosa è successo dal 2003), simulazione Monte Carlo (cosa potremmo aspettarci dai prossimi 20 anni). La pipeline metodologica di SmartMoneyLab (rolling windows, total return, lordo come baseline) è sempre quella.

## Una premessa di trasparenza

Questo è il **mio portafoglio reale**. Ho cominciato a costruirlo il 7 novembre 2024. Il PAC mensile è di 200 €. La composizione che vedi qui sotto è quella target dichiarata; nella pratica i pesi driftano leggermente in base ai movimenti di mercato fra un versamento e l'altro, e periodicamente li riporto a target con il versamento successivo (il "rebalancing implicito" del PAC).

Non sto presentando questo articolo come consiglio. Sto presentando un esperimento di trasparenza: prendo il mio portafoglio reale, lo metto sotto la stessa lente con cui ho fatto a pezzi la strategia LEAPS e gli ETF a leva 3x negli articoli precedenti della serie, e accetto in anticipo l'esito — qualunque esso sia. Il bias del fatto che sono io a giudicare il portafoglio che io stesso ho costruito esiste, lo dichiaro, e lo prendo in carico nella sezione dei limiti.

Inauguro così una nuova famiglia editoriale del blog: **test di portafogli reali**. Il primo soggetto sono io. Sarò felice di testare anche portafogli di lettori che me li manderanno (anonimi o nominati, come preferiscono). La distinzione editoriale con la serie "Strategie per battere il mercato?" è netta: lì confrontiamo strategie attive contro un benchmark passivo applicando un framework standardizzato; qui osserviamo cosa è successo, e cosa potrebbe succedere, a un'allocazione concreta. Niente verdict, niente framework 6+1, chiusura aperta — i numeri parlano, il lettore decide.

## Parte 1 — Cosa c'è nel portafoglio

L'allocazione target è la seguente:

| Asset | Peso | ETF UCITS reale nel portafoglio (Borsa Italiana / XETRA) |
|---|---|---|
| Azionario USA | 16% | Amundi IS S&P 500 Swap (A500) |
| Nasdaq 100 | 16% | Amundi Core Nasdaq-100 Swap (LYMS) |
| Mercati Emergenti | 12% | Xtrackers MSCI EM (XMME) |
| Azionario Globale | 8% | iShares Core MSCI World (SWDA) |
| Healthcare | 7% | Xtrackers MSCI World Health Care (XDWH) |
| Small Cap | 7% | iShares MSCI World Small Cap ESG (CBUG) |
| Asia ex Japan | 7% | Amundi IS MSCI EM Asia (AASI) |
| Oro | 7% | iShares Physical Gold ETC (PPFB) |
| Europa | 6% | Xtrackers MSCI Europe (XMEU) |
| Bitcoin + Tematici Tech | 5% | Fidelity Physical Bitcoin (FBTC, 2%) + Amundi MSCI Disruptive Tech (UNIC, 2%) + iShares Automation & Robotics (RBOT, 1%) |
| Energia tradizionale | 3% | Xtrackers MSCI World Energy (XDW0) |
| Clean Energy | 3% | Fineco AM MarketVector Clean Energy (EMOVE) |
| Nucleare | 3% | VanEck Uranium and Nuclear (NUCL) |
| **Totale** | **100%** | |

Visivamente:

![Composizione target del portafoglio](/charts/portafoglio-personale-backtest/01_composizione_donut.png)

### Lettura per macro-area

Per cogliere la struttura conviene leggerla per macro-area invece che per singolo bucket:

- **Azionario mondiale broad** (USA + Globale + Europa) = **30%**. È la base passiva del portafoglio.
- **Tematico tech e disruption** (Nasdaq + Bitcoin + Bets) = **21%**. È la scommessa concentrata sui trend di lunga durata sull'innovazione.
- **Geografia emergente** (Mercati Emergenti + Asia ex Japan) = **19%**. È la scommessa demografica e sul rebalance economico mondiale verso est.
- **Settoriale difensivo o ad asimmetria favorevole** (Healthcare 7% + Small Cap 7% + Oro 7%) = **21%**. Healthcare ha bassa correlazione coi cicli, small cap è dove storicamente si trova il premio per la dimensione, oro è il bene rifugio del decennio attuale.
- **Energia** (tradizionale + clean + nucleare) = **9%**. Tre sotto-settori bilanciati per non scommettere su una transizione energetica "vinta" da una singola tecnologia.

Sommando i blocchi: 30 di base + 21 di tematico + 19 di geografia + 21 di settoriale + 9 di energia = 100%. È un portafoglio **equity-only** (niente obbligazioni, niente liquidità) costruito su un orizzonte di 10-20+ anni e con un PAC come strumento di entrata. Sulla scelta di non includere obbligazioni, il ragionamento è coerente con [l'articolo sul senso delle obbligazioni nel portafoglio](/posts/ha-senso-obbligazioni-portafoglio): nell'orizzonte temporale di un investitore retail di 35-40 anni, l'effetto compounding sull'equity tende a dominare il beneficio della stabilizzazione obbligazionaria.

### Il problema della storicità

Ogni asset del portafoglio ha un ETF UCITS reale che lo replica, ma quasi tutti questi ETF sono troppo giovani per un backtest serio. A500 esiste dal 2017, LYMS dal 2018, CBUG dal 2023, FBTC dal 2022, NUCL dal 2023, EMOVE è ancora più recente. Per fare un test su orizzonti decennali serve passare a **proxy a lungo storico** sugli stessi indici sottostanti — indici S&P, MSCI ed ETF americani con storia che parte dai primi anni 2000.

Il proxy storico usato per ogni asset, con la sua data di partenza:

![Storicità degli asset](/charts/portafoglio-personale-backtest/02_storicita_asset.png)

Periodo comune in cui tutti i 13 asset hanno un proxy disponibile: **dal 30 aprile 2003 al 31 dicembre 2025**, 22 anni e 8 mesi, 272 osservazioni mensili. Quello sotto i 22 anni va riempito con backfill da proxy ancora più antichi (per esempio: per il bucket "Bitcoin + Bets" usiamo Nasdaq 100 prima del 2014, dato che Bitcoin esisteva ma con dati di qualità solo da metà 2014; per il bucket "Clean Energy" usiamo XLE prima del 2008). Tutti i backfill sono documentati nel commento dello script in `scripts/portafoglio-personale-backtest.py`.

Il dato di lavoro è **mensile** (fine mese). Tutti i prezzi sono **Total Return** — i dividendi sono reinvestiti, come è obbligatorio quando si confronta equity di lungo periodo. Tutti i numeri sono **lordi** (niente TER degli ETF, niente bid/ask, niente fiscalità italiana) — la convenzione standard del blog, da dichiarare e tenere a mente quando il lettore traduce i numeri in attesa pratica.

## Parte 2 — Il backtest sui 22 anni di dati reali

### Lump sum: investi 10.000 € il 30 aprile 2003 e non tocchi più

Lo scenario più semplice. Investi i 10.000 € il 30 aprile 2003 ripartiti secondo i pesi target, e li lasci lavorare per 22 anni e 8 mesi senza ribilanciare nulla. I pesi driftano liberamente; un asset che cresce di più peserà di più alla fine, uno che crolla peserà di meno. La curva NAV cumulata in scala logaritmica:

![Equity curve lump sum vs benchmark](/charts/portafoglio-personale-backtest/03_equity_lumpsum_vs_benchmark.png)

E le metriche:

| Metrica | Portafoglio | S&P 500 TR | MSCI World TR |
|---|---|---|---|
| NAV finale (su 10.000 €) | **204.776 €** | 113.674 € | 76.771 € |
| CAGR | **+14,30%** | +11,36% | +9,45% |
| Volatilità annualizzata | 17,2% | 14,4% | 14,4% |
| Max drawdown | **-49,5%** | -50,8% | -50,8% |
| Sharpe ratio | **0,87** | 0,82 | 0,70 |
| Sortino ratio | **1,24** | — | — |
| Calmar ratio | **0,289** | 0,224 | 0,186 |

L'outperformance è netta. Il portafoglio supera l'S&P 500 di **+2,9 punti percentuali di CAGR all'anno**, e il MSCI World di **+4,9 punti**. In termini di moltiplicatore del capitale, il portafoglio chiude a **1,8 volte** l'S&P e **2,7 volte** il MSCI World.

Tre osservazioni che ci servono per capire bene:

**1. Il drawdown è uguale ai benchmark, non peggiore**. Questo è il fatto più sorprendente. Il portafoglio contiene asset individualmente molto più volatili dell'S&P 500 — Bitcoin, Nasdaq, emerging markets, small cap, energia — eppure il drawdown massimo realizzato è leggermente migliore del benchmark (-49,5% contro -50,8%). È il "pranzo gratis" della diversificazione di Markowitz nella sua forma più pulita: combinazioni di asset correlati imperfettamente possono dare meno rischio del singolo asset più sicuro nel portafoglio. Nel marzo 2009 (il bottom del 2008), l'oro era a +25% sull'anno mentre l'S&P era a -50% — e questa correlazione negativa ha smorzato il drawdown del portafoglio diversificato.

**2. La volatilità è più alta ma il Sharpe e il Sortino sono migliori**. Vol del portafoglio 17,2% contro 14,4% del benchmark — quasi 3 punti in più. Però lo Sharpe (eccesso di rendimento per unità di volatilità) e il Sortino (eccesso di rendimento per unità di volatilità *negativa*) sono entrambi migliori. Quindi: il portafoglio "balla di più" ma il bilanciamento fra rendimento e rischio è strutturalmente migliore.

**3. Il Calmar racconta la storia chiave**. Il Calmar del portafoglio è 0,289, quello dell'S&P è 0,224, quello del MSCI World è 0,186. Questa è la differenza fondamentale rispetto alla [strategia LEAPS](/posts/strategia-leaps-vs-buy-and-hold) testata nell'articolo precedente: lì il Calmar era identico (0,2099 vs 0,2103), segno che l'extra-CAGR era pagato con extra-drawdown lungo la stessa retta rischio/rendimento. Qui no. Qui il rapporto rendimento/drawdown è migliore del benchmark del 30%. C'è alfa genuino, non leva.

### PAC: 200 €/mese per 22 anni e 8 mesi

Ora lo scenario più realistico per un retail: invece di mettere 10.000 € tutti in una volta, versi 200 € al mese ogni fine mese, allocati ai pesi target. È esattamente quello che faccio io, solo proiettato indietro nel tempo. Su 272 mesi di backtest, i contributi totali sono 54.400 €.

![Equity curve PAC vs benchmark](/charts/portafoglio-personale-backtest/04_equity_pac_vs_benchmark.png)

| | Portafoglio | S&P 500 | MSCI World |
|---|---|---|---|
| Contributi totali | 54.400 € | 54.400 € | 54.400 € |
| NAV finale | **396.541 €** | 273.178 € | 199.526 € |
| Moltiplicatore sui contributi | **7,3×** | 5,0× | 3,7× |

Il PAC amplifica l'outperformance del portafoglio: il moltiplicatore finale è del 46% superiore a quello dell'S&P (7,3× contro 5,0×). La ragione meccanica è la stessa che premia il dollar cost averaging in generale: i versamenti durante i drawdown comprano più quote. Quando questi acquisti "in saldo" si fanno su asset volatili che poi recuperano violentemente (Nasdaq 2009, EM 2003-2007, oro 2008-2011), il PAC raccoglie più rendimento del lump sum equivalente.

### I rolling windows

Il rischio dei numeri full period è dipendere troppo dal punto di partenza. Per questo SmartMoneyLab usa sempre **finestre rolling** che esplorano tutti i possibili punti di entrata. Con 22 anni di dati, possiamo fare finestre da 5, 10 e 15 anni con step di 3 mesi.

![Distribuzione del CAGR su finestre rolling](/charts/portafoglio-personale-backtest/05_cagr_boxplot_rolling.png)

Distribuzione del CAGR per orizzonte e benchmark:

| | Portafoglio | S&P 500 | MSCI World |
|---|---|---|---|
| **Rolling 5 anni (71 finestre)** | | | |
| Mediana CAGR | +11,6% | +11,7% | +8,8% |
| 5° percentile | +2,8% | -1,7% | -1,7% |
| 95° percentile | +21,1% | +17,4% | +14,9% |
| **Rolling 10 anni (51 finestre)** | | | |
| Mediana CAGR | +14,1% | +12,2% | +9,2% |
| 5° percentile | +7,0% | +6,9% | +4,7% |
| 95° percentile | +18,5% | +15,3% | +12,1% |
| **Rolling 15 anni (31 finestre)** | | | |
| Mediana CAGR | +12,2% | +9,7% | +7,5% |
| 5° percentile | +10,0% | +8,5% | +6,3% |
| 95° percentile | +17,4% | +14,5% | +11,6% |

E i win rate (quota di finestre rolling in cui il portafoglio batte il benchmark):

![Win rate per finestra rolling](/charts/portafoglio-personale-backtest/07_win_rate_per_finestra.png)

| Orizzonte | Win rate vs S&P 500 | Win rate vs MSCI World | Outperformance media vs S&P |
|---|---|---|---|
| 5 anni | 55% | 87% | +1,3 pp |
| 10 anni | **94%** | 100% | +1,7 pp |
| 15 anni | **100%** | 100% | +2,4 pp |

Tre cose dico apertamente:

**Sui 5 anni l'edge non c'è.** Win rate vs S&P 500 al 55% significa "praticamente pareggio". La mediana del CAGR a 5 anni del portafoglio è quasi identica a quella del benchmark (11,6% vs 11,7%). Il portafoglio non è uno strumento per "battere il mercato a 5 anni". Se compri questa allocazione e la vendi a 5 anni perché non si è mossa abbastanza, la statistica suggerisce che non hai dato tempo. **L'orizzonte minimo perché l'allocazione abbia senso è 10 anni**, e il sweet spot è 15+.

**Sui 10 e 15 anni il portafoglio vince quasi sempre.** Win rate del 94% sui rolling decennali, 100% sui quindicennali. È una proprietà statisticamente forte: in 22 anni di dati, su tutti i possibili punti di partenza distanziati di 3 mesi, quasi nessuna finestra decennale ha visto il benchmark battere il portafoglio.

**Il drawdown sui 10 anni è leggermente peggiore del benchmark.** Distribuzione del max drawdown:

![Max drawdown per finestra rolling](/charts/portafoglio-personale-backtest/06_maxdd_boxplot_rolling.png)

Sul rolling 10y il drawdown mediano del portafoglio è -33,9% contro -23,9% dell'S&P 500. Quindi: il portafoglio batte il benchmark sul CAGR a 10 anni nel 94% delle finestre, ma nelle stesse finestre ha drawdown medi più ampi. La compensazione si vede sul Calmar: i CAGR maggiori bilanciano i drawdown maggiori in modo che il rapporto rischio/rendimento risulta comunque favorevole, ma il "viaggio" dentro la finestra è più volatile.

### Il periodo reale dell'investimento: dal 7 novembre 2024 a oggi

Per onestà aggiungo anche il dato sul periodo *vero* del mio investimento, da novembre 2024 a fine 2025 — 14 mesi. È troppo breve per dire qualcosa di statisticamente significativo, ma serve come "snapshot reale" per il lettore.

![PAC reale: portafoglio vs benchmark dal 7 novembre 2024](/charts/portafoglio-personale-backtest/08_pac_vs_lumpsum.png)

| | PAC Portafoglio | PAC S&P 500 | PAC MSCI World |
|---|---|---|---|
| Versamenti totali | 2.800 € | 2.800 € | 2.800 € |
| NAV finale (31 dic 2025) | **3.235 €** | 3.134 € | 3.155 € |
| Rendimento sui contributi | +15,6% | +11,9% | +12,7% |

Il portafoglio sta sovraperformando entrambi i benchmark di +3,7 pp e +2,9 pp — direzionalmente coerente col CAGR di outperformance medio del backtest 22y. Ma su 14 mesi è solo un'osservazione singola, non un dato statistico. La riporto per trasparenza, non per supportare una conclusione.

## Parte 3 — La simulazione Monte Carlo

Il backtest ci dice cosa sarebbe successo *se* avessi investito nel passato. Per stimare cosa potrebbe succedere nel futuro serve uno strumento diverso. È qui che entra la simulazione **Monte Carlo**.

### Cosa è una simulazione Monte Carlo (e a cosa serve)

Una simulazione Monte Carlo è una tecnica per stimare la distribuzione di esiti futuri di un sistema complesso quando non hai una formula matematica chiusa che ti dia la risposta esatta. Il principio è semplice: invece di calcolare un singolo "esito atteso", ne simuli migliaia (o decine di migliaia) campionando casualmente gli ingredienti del sistema, e guardi come si distribuiscono i risultati.

Applicata al nostro portafoglio: invece di chiederci "quanto renderà fra 20 anni" — domanda a cui nessuno può rispondere — chiediamo "se i prossimi 20 anni saranno *statisticamente simili* agli ultimi 22, quale è la distribuzione dei NAV finali possibili?". Per rispondere, generiamo **10.000 sequenze sintetiche** di rendimenti mensili per i 20 anni a venire (ognuna lunga 240 mesi), simuliamo il portafoglio su ciascuna, e raccogliamo i 10.000 NAV finali. La distribuzione di questi 10.000 numeri è la nostra stima.

Il modo in cui generiamo le 10.000 sequenze sintetiche non è arbitrario. Usiamo una tecnica chiamata **block bootstrap**: campioniamo casualmente *blocchi* di 3 mesi consecutivi dai 22 anni di storia, e li incolliamo in sequenza fino a coprire l'orizzonte futuro. Il motivo dei blocchi è preservare due proprietà importanti della storia che andrebbero perse se campionassimo un mese alla volta in modo indipendente: la **autocorrelazione di breve periodo** (il cosiddetto *vol clustering*: dopo un mese di volatilità alta tende a venirne un altro), e le **correlazioni cross-asset** (quando l'S&P scende, l'oro spesso sale; questa relazione va mantenuta nelle 10.000 traiettorie). Tre mesi è il blocco standard in letteratura per backtest mensili di portafogli multi-asset: cattura il momentum di breve senza essere troppo rigido.

A cosa serve quindi questa simulazione? A tre cose, in ordine di importanza:

1. **Quantificare l'incertezza**. Invece di un numero singolo ("ti aspetti X% all'anno"), ottieni una distribuzione: "nel 50% dei casi il NAV finale sta fra A e B, nel 90% sta fra C e D". Questa è una rappresentazione molto più onesta di quello che la storia ci permette di dire.
2. **Confrontare strategie su basi statistiche**, non aneddotiche. La domanda "il mio portafoglio batte l'S&P?" diventa "in quale percentuale delle 10.000 traiettorie il portafoglio finisce sopra l'S&P?". Una risposta del 71% è molto diversa da una risposta del 51%: la prima è una scommessa che paga in modo strutturale, la seconda è una scommessa al limite del lancio di una moneta.
3. **Stimare le code**. La mediana ti dice il "caso tipico". Ma quello che spesso conta di più per chi pianifica un'allocazione di lungo periodo è il 5° percentile (la coda sinistra: cosa succede negli scenari sfortunati) e il 95° (la coda destra: cosa succede in quelli fortunati). Un portafoglio che ha mediana alta ma coda sinistra terribile potrebbe non essere desiderabile, anche se "in media" è migliore.

Quello che la simulazione Monte Carlo **non** fa, ed è il punto critico: non prevede il futuro. Tutto il calcolo dipende dall'ipotesi che il regime statistico futuro assomigli a quello passato — ovvero che la distribuzione dei rendimenti, le correlazioni, le volatilità e i comportamenti delle code abbiano la stessa "firma" degli ultimi 22 anni. Se il regime cambia in modo strutturale (de-globalizzazione spinta, fine del super-cycle tech, ritorno duraturo a tassi reali alti, transizione energetica accelerata o bloccata), tutti i risultati vanno presi come scenari condizionati e non come previsioni.

Per farti vedere graficamente cosa significano "10.000 traiettorie e la loro distribuzione", ecco il "fan chart" del portafoglio su 30 anni con lump sum da 10.000 €: la linea centrale è la mediana, l'area scura interna contiene il 50% delle traiettorie (dal 25° al 75° percentile), l'area chiara esterna contiene il 90% delle traiettorie (dal 5° al 95°):

![Fan chart Monte Carlo lump sum 30 anni](/charts/portafoglio-personale-montecarlo/03_fan_chart_lump.png)

### I numeri: 20 anni come orizzonte di riferimento

Il backtest aveva dimostrato che sotto i 10 anni l'edge del portafoglio non è significativo statisticamente. Per la simulazione Monte Carlo prendo come riferimento principale l'orizzonte di **20 anni**, che è il sweet spot dell'allocazione: lungo abbastanza da rendere l'edge statisticamente significativo, corto abbastanza da essere realistico per un investitore di 25-35 anni di età che vuole prepararsi alla seconda metà della carriera.

Lump sum di 10.000 € investiti il giorno zero, distribuzione dei NAV finali a 20 anni:

![Distribuzione NAV finale lump sum 10/20/30 anni](/charts/portafoglio-personale-montecarlo/01_distribuzione_nav_lump.png)

| Percentile | Portafoglio | S&P 500 | MSCI World |
|---|---|---|---|
| 5° (scenari sfortunati) | **40.571 €** | 28.784 € | 20.035 € |
| 25° | 85.660 € | 55.118 € | 38.752 € |
| 50° (mediana) | **147.630 €** | 84.769 € | 60.444 € |
| 75° | 265.329 € | 130.787 € | 92.140 € |
| 95° (scenari fortunati) | **696.748 €** | 239.679 € | 165.436 € |

Tradotto in italiano: se investi 10.000 € oggi e li lasci lavorare 20 anni, nel **50% dei casi** (cioè in metà delle 10.000 traiettorie simulate) finisci con un NAV fra **85.660 € e 265.329 €** (l'intervallo p25-p75). Nel **5% dei casi peggiori** finisci con meno di **40.571 €** (che è comunque un 4× sul capitale iniziale). Nel **5% dei casi migliori** finisci con più di **696.748 €** (un 69× sul capitale iniziale).

Confronto con l'S&P 500 sullo stesso orizzonte e nella stessa simulazione bootstrap: la mediana del portafoglio (147.630 €) è il **74% in più** della mediana dell'S&P (84.769 €). Il 5° percentile del portafoglio (40.571 €) è il **41% in più** del 5° dell'S&P (28.784 €). E il 95° percentile del portafoglio (696.748 €) è **quasi il triplo** del 95° dell'S&P (239.679 €).

Quindi l'asimmetria del payoff è favorevole **sia nella coda sinistra che nella coda destra**. Non è solo "vinco nella media": vinco anche negli scenari fortunati di molto, e perdo meno in quelli sfortunati.

La probabilità che il portafoglio finisca sopra il benchmark a 20 anni:

![Probabilità di outperformance Monte Carlo](/charts/portafoglio-personale-montecarlo/05_proba_outperformance.png)

| Orizzonte | P(Portafoglio > S&P 500) | P(Portafoglio > MSCI World) |
|---|---|---|
| 10 anni | 59% | 69% |
| 20 anni | **71%** | **82%** |
| 30 anni | **82%** | **91%** |

Le probabilità di outperformance crescono monotonicamente con l'orizzonte. È coerente con quello che il backtest ha mostrato sui rolling windows: il vantaggio strutturale del portafoglio si manifesta su orizzonti lunghi, e su orizzonti corti l'esposizione settoriale concentrata può andare male per ragioni puramente tattiche.

### E il PAC a 20 anni?

Stesso esercizio ma con il PAC di 200 €/mese (48.000 € versati totali in 20 anni):

| Percentile | Portafoglio | S&P 500 | MSCI World |
|---|---|---|---|
| 5° | 96.268 € | 80.958 € | 63.844 € |
| 50° (mediana) | **235.469 €** | 172.477 € | 135.454 € |
| 95° | 686.727 € | 361.695 € | 286.156 € |

La probabilità che il PAC sul portafoglio batta il PAC sull'S&P 500 a 20 anni è del **67%**, contro il MSCI World è del **78%**. Note che la probabilità di outperformance del PAC è leggermente inferiore a quella del lump sum (67% vs 71% sull'S&P). Il PAC riduce sia la varianza dell'esito che — un po' — l'edge atteso, perché diluisce nel tempo l'esposizione media.

### Il drawdown atteso

Anche il drawdown massimo è un risultato della simulazione: per ogni traiettoria possiamo calcolare il drawdown peggiore vissuto lungo i 240 mesi, e guardare la distribuzione.

![Distribuzione del Max Drawdown atteso](/charts/portafoglio-personale-montecarlo/06_distribuzione_mdd.png)

Mediana del MDD atteso a 20 anni: portafoglio **-32,6%**, S&P 500 **-30,8%**, MSCI World **-32,1%**. Praticamente identici. Il 5° percentile (lo scenario di drawdown peggiore) è -50,5% per il portafoglio, -49,4% per l'S&P. Anche qui: il portafoglio non è "più rischioso" del benchmark sul rischio di coda. Le code di drawdown sono sostanzialmente identiche; quello che cambia è la mediana del CAGR ottenuto.

## I limiti del modello, presi sul serio

Tre cose vanno dichiarate apertamente prima di chiudere.

**Il bias di selezione retrospettiva è enorme e dichiarato**. Ho disegnato questo portafoglio nel 2024 conoscendo già i trend degli ultimi 22 anni: che il Nasdaq ha sovraperformato l'S&P di 5 punti annui dal 2010, che l'oro ha avuto un decennio d'oro 2003-2011, che gli EM hanno avuto un boom 2003-2007 e poi sono stati stagnanti, che il settore energetico è ciclico ma con tail risks favorevoli, e così via. Costruire un'allocazione "ispirata" da questa conoscenza e poi testarla *sugli stessi dati storici* significa avere un bias matematico forte verso risultati positivi. Il portafoglio retrospettivamente vincente è sempre più facile da costruire del portafoglio prospettivamente vincente.

Quello che il backtest e il Monte Carlo dimostrano onestamente è due cose distinte. Primo: la **struttura matematica della diversificazione** funziona — combinare asset volatili con bassa correlazione produce risultati migliori del singolo asset più sicuro nel mix. Questa è una proprietà tecnica universale di Markowitz, non dipende dal regime. Secondo: **se il regime tematico che ha pagato negli ultimi 22 anni continua a pagare**, il portafoglio batterà i benchmark con alta probabilità. Quello che non dimostrano: che il regime continui a pagare.

**Lordo, niente costi**. I numeri sono tutti pre-TER, pre-bid/ask, pre-fiscalità. Il TER medio del mio mix di ETF UCITS è circa 0,35% all'anno (alcuni asset più cari come UNIC, FBTC, NUCL, EMOVE sono attorno allo 0,70%; gli ETF passivi MSCI World, S&P, EM sono attorno allo 0,12-0,20%). Sui 22 anni di backtest questo significa circa 70-80 bps annui di drag complessivo (TER + spread bid/ask al rebalancing implicito del PAC). Sull'outperformance lorda di +2,9 pp sull'S&P, il margine netto resta significativo ma non più drammatico (+2 pp circa). La fiscalità italiana (capital gain 26%, dividendi al 26% e imposta di bollo 0,2%/anno) erode altri 30-40 bps anno. Per la mia situazione personale uso il PAC senza realizzare capital gain fino al ritiro, quindi il drag fiscale è differito — ma esiste.

**Il modello Monte Carlo non cattura i cambi di regime**. Il block bootstrap campiona dalla storia passata, e quindi assume che ogni "blocco di 3 mesi" pescato dal 2003-2025 possa rappresentare un futuro blocco di 3 mesi. Funziona bene per simulare la struttura di vol e correlazioni in regime "normale". Funziona male se il futuro contiene un regime macro mai visto nei 22 anni di input (per esempio: un periodo di inflazione duratura sopra il 6% combinato con tassi reali alti, come quello vissuto negli anni '70 — periodo *non incluso* nel dataset di addestramento). Il vero rischio del Monte Carlo è essere fooled by the past, non il bootstrap in sé.

## Cosa porto a casa

1. **Sul backtest 22 anni e sulla simulazione Monte Carlo, il portafoglio batte l'S&P 500 di +2,9 pp di CAGR all'anno con drawdown leggermente migliore, e batte il MSCI World di +4,9 pp**. È un'outperformance significativa, dovuta a diversificazione strutturale che effettivamente "lavora" e non a leva. Il Calmar superiore al benchmark è la firma matematica dell'alfa genuino.

2. **L'edge esiste solo su orizzonti lunghi**. Sui 5 anni il win rate vs S&P è del 55%, praticamente pari. Sui 10 sale al 94%, sui 15 al 100%. Il portafoglio non è uno strumento "per battere il mercato a breve": è uno strumento di accumulazione lunga. L'orizzonte minimo perché abbia statisticamente senso è 10 anni; il sweet spot è 15-20.

3. **Il Monte Carlo a 20 anni stima una mediana del NAV finale a 147.630 €** (lump sum di 10k), contro 84.769 € dell'S&P 500. Coda sinistra 40.571 €, coda destra 696.748 €. Probabilità di outperformance sull'S&P: 71%; sul MSCI World: 82%. **L'asimmetria del payoff è favorevole sia nella coda sinistra che nella destra**: anche nello scenario sfortunato si fa meglio del benchmark, e nello scenario fortunato si fa molto meglio.

4. **Il bias di selezione retrospettiva è il limite epistemico principale**. Il portafoglio è stato disegnato nel 2024 conoscendo i trend che hanno premiato gli ultimi 22 anni. Il backtest dimostra "se quei trend continuano, vinci". Non dimostra "i trend continueranno". Quello che dimostra in modo universale e indipendente dal regime è solo la proprietà tecnica della diversificazione di Markowitz — combinare asset poco correlati produce rapporti rischio/rendimento migliori dei singoli asset.

5. **Il PAC è lo strumento naturale per questa allocazione**. Riduce il rischio di entry timing su un portafoglio tematico, e si vede meccanicamente nei numeri del backtest (PAC 7,3× contributi vs lump sum 6,7× iniziale). Il sweet spot pratico per un retail italiano è: PAC mensile su orizzonte 15+ anni, rebalancing implicito tramite i versamenti, fiscalità differita non realizzando capital gain prima del ritiro.

Il piano operativo del mio portafoglio è di continuare il PAC per i prossimi 15-20 anni e tornare su queste pagine fra esattamente 12 mesi a rifare l'esercizio con un anno di dati reali in più. Idealmente la nuova famiglia editoriale "test di portafogli reali" diventerà una rubrica annuale con anche i portafogli di lettori che vorranno farsi testare. La trasparenza piena è il prezzo del rigore: se i prossimi 5 anni il portafoglio sotto-performerà l'S&P del 3% all'anno, lo scriverò qui senza filtri.
