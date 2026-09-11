---
category: "strategie"
title: "Il mio portafoglio reale: 31 anni di backtest e Monte Carlo"
description: "Il mio portafoglio reale in 7 classi ad ampia storia, testato su 31 anni (1995-2026): eguaglia l'S&P 500 con meno rischio, batte MSCI World e ACWI, e nel peggior decennio resta l'unico in positivo."
pubDate: 2026-09-09
tags: ["portafoglio", "backtest", "monte-carlo", "rolling-windows", "pac", "asset-allocation", "momentum", "mean-reversion"]
author: "SmartMoneyLab"
simulationSlug: "portafoglio-personale-backtest"
seoImage: "/charts/portafoglio-personale-backtest/02_equity_lump.png"
draft: false
faq:
  - q: "Questo portafoglio batte l'S&P 500?"
    a: |-
      No, e non è il suo scopo. Su 31 anni (1995-2026) lo eguaglia: CAGR 10,83% contro 10,69%, con un drawdown massimo migliore (−48,4% contro −50,8%) ma una volatilità leggermente più alta. Il confronto giusto per un portafoglio diversificato a livello globale sono MSCI World e ACWI, e lì il vantaggio è netto: +2,4 e +2,6 punti di CAGR all'anno, con drawdown più basso. Nel Monte Carlo a 20 anni il portafoglio batte il World nel 98% degli scenari e l'ACWI nel 100%, mentre contro l'S&P 500 resta un sostanziale pareggio (55%).
  - q: "Che rendimento posso aspettarmi da questo portafoglio?"
    a: |-
      Nessuno lo sa: il passato non è una garanzia. Come stima, la simulazione Monte Carlo (10.000 traiettorie bootstrap sui rendimenti storici) dà, partendo da 10.000 €, una mediana di circa 78.000 € a 20 anni e 220.000 € a 30 anni, con un intervallo molto ampio: a 20 anni dal 5° al 95° percentile si va da ~23.000 € a ~257.000 €. Sono ipotesi statistiche sotto l'assunzione che i prossimi decenni assomiglino statisticamente agli ultimi 31 anni, non previsioni.
  - q: "E se entro nel momento peggiore?"
    a: |-
      È la prova più severa, e il portafoglio la supera bene. Guardando tutte le finestre mobili dei 31 anni, la *peggiore* finestra di 10 anni ha comunque reso +3,1% all'anno per il portafoglio — l'unico dei quattro a non perdere (S&P −3,4%, World −2,5%, ACWI −1,3%). Sulla peggiore finestra di 5 anni fa −2,3% contro il −5/−7% dei benchmark, e il suo 5° percentile resta positivo. Un caveat però: questo *non* vuol dire che non crolli. Il drawdown massimo resta intorno al −48%, come per qualsiasi portafoglio azionario; ciò che la diversificazione e la sleeve oro+energia comprano è un recupero più rapido, cioè un risultato finale meno rovinato per chi resta investito 5-10 anni.
  - q: "Perché Europa Momentum invece dell'Europa classica?"
    a: |-
      Perché sui dati la versione momentum dell'indice europeo ha reso di più e con un profilo di rischio migliore: dal 1994 al 2026 la MSCI Europe Momentum ha fatto circa l'11,0% annuo contro il 9,1% della MSCI Europe classica, con Sharpe e Sortino superiori — e proprio in un periodo, il 2000-2020, che per l'azionario europeo è stato difficile e laterale. Il momentum non è una scommessa esotica: è un fattore documentato da decenni di letteratura accademica.
  - q: "Perché il portafoglio non ha obbligazioni?"
    a: |-
      È una scelta legata all'orizzonte. Su 20-30 anni l'effetto del compounding sull'azionario tende a dominare il beneficio di stabilizzazione delle obbligazioni. La stabilità nei crolli qui è affidata a una sleeve difensiva di attivi reali — oro ed energia — che storicamente proteggono nei regimi di inflazione e di stress dei mercati, proprio quando l'azionario soffre. Ne parlo più a fondo nell'analisi sul senso delle obbligazioni in portafoglio.
  - q: "Cos'è la 'sleeve difensiva' di oro ed energia?"
    a: |-
      È il 17% del portafoglio (8% oro + 9% energia): due attivi reali che tendono a muoversi diversamente dall'azionario tradizionale e a difendere nei regimi in cui questo va peggio — inflazione, shock geopolitici, mercati laterali. Costano qualcosa negli anni di corsa dei mercati (non partecipano al rialzo tecnologico), ma sono ciò che, nei numeri, compra al portafoglio il drawdown più basso di tutti i benchmark.
  - q: "Qual è il limite principale di questo backtest?"
    a: |-
      Il bias di selezione retrospettiva: il portafoglio è disegnato conoscendo la storia. Usa però classi ampie e non settori di nicchia scelti perché hanno già vinto — e il fatto stesso che non stravinca l'S&P 500 è un segnale che non è sovra-ottimizzato. Ma resta: il backtest dimostra "se i prossimi 31 anni assomigliano agli ultimi 31, funziona", non "funzionerà". Secondariamente, due serie (Nasdaq ed Energia) sono a prezzo e vi ho aggiunto un dividendo figurato dichiarato.
---

> **Disclaimer.** Questo è il mio portafoglio reale, non un consiglio. Le cifre sono backtest e simulazioni con ipotesi dichiarate, non previsioni. Nessun rendimento passato garantisce quelli futuri.

## In breve

Questo è il portafoglio reale con cui gestisco la mia componente azionaria di lungo periodo: **7 classi ad ampia storia**, scelte anche perché mi permettono di testarlo su una finestra lunga e severa — **31 anni, dal luglio 1995 al luglio 2026** — che comprende la bolla dot-com e il suo crollo, la crisi del 2008, il decennio perso di Europa ed emergenti, il boom e il crollo dell'energia, il COVID e l'orso del 2022. L'allocazione target è: **Azionario USA 20% · Mercati Emergenti 20% · Nasdaq/Tech 25% · Smallcap 10% · Europa Momentum 8% · Oro 8% · Energia 9%**. Equity-only, ribilanciata una volta l'anno. I numeri principali:

1. **Contro l'S&P 500 è un pareggio, non una vittoria.** CAGR 10,83% contro 10,69%, con un drawdown massimo *migliore* (−48,4% contro −50,8%) ma volatilità un filo più alta. Su 10.000 € investiti nel 1995, il portafoglio chiude a **244.706 €**, l'S&P a 235.053 €. È importante dirlo subito: questo portafoglio **non pretende di battere l'S&P 500**, il benchmark più difficile di questi 31 anni. Lo eguaglia, prendendosi meno rischio nei crolli.

2. **Contro MSCI World e ACWI, invece, vince nettamente.** Ed è il confronto giusto per un portafoglio diversificato geograficamente. CAGR 8,42% del World e 8,20% dell'ACWI IMI: il portafoglio fa **+2,4 e +2,6 punti all'anno**, con anche un drawdown più basso (−48% contro −54% e −55%). Su 10.000 €, chiude a 244.706 € contro i 123.386 € del World e i 115.757 € dell'ACWI: **il doppio**.

3. **Sulle finestre mobili, il pattern è coerente.** Su tutte le finestre di 10 anni dal 1995, il portafoglio batte il World nel **98%** dei casi e l'ACWI nel **100%**; contro l'S&P 500 vince nel 53% (in sostanza testa o croce, che sale al 64% sulle finestre di 15 anni). Non batte quasi mai l'S&P, batte quasi sempre il resto del mondo.

4. **Nello scenario peggiore, la diversificazione protegge davvero.** È la parte che sorprende di più. Sulla *peggiore* finestra di 10 anni dei 31 (chi è entrato nel marzo 1999, a un passo dallo scoppio della bolla dot-com) il portafoglio ha comunque reso **+3,1% all'anno**: l'unico dei quattro a non aver perso. Nello stesso decennio l'S&P ha fatto −3,4% annuo, il World −2,5%, l'ACWI −1,3%. E sulla peggiore finestra di 5 anni fa **−2,3%** contro il −5/−7% dei benchmark. Attenzione: il crollo *dentro* la finestra resta pieno (−48%, è equity-only); a essere protetto è il risultato di chi resta investito 5-10 anni.

5. **Il Monte Carlo prospettico dice la stessa cosa.** Su 10.000 traiettorie a 20 anni, la mediana del portafoglio partendo da 10.000 € è **78.407 €** (contro 49.641 € del World e 47.796 € dell'ACWI), e batte il World nel **98%** e l'ACWI nel **100%** degli scenari. Contro l'S&P resta un pareggio (55%).

6. **Il caveat, che dichiaro apertamente.** Il portafoglio è disegnato conoscendo la storia. Usa però classi ampie e non settori di nicchia scelti perché hanno già vinto — e proprio il fatto che non stravinca l'S&P è la prova che non è sovra-ottimizzato. Il backtest dimostra "se i prossimi 31 anni assomigliano agli ultimi 31, funziona", non "funzionerà".

Come sempre nella rubrica dei portafogli reali: niente verdetto secco, niente framework a punteggio. Espongo i numeri, dichiaro i limiti, il lettore decide.

## Una premessa di trasparenza

Questo è il **mio portafoglio reale**. È fatto di classi ampie e con storia lunga per due ragioni: la prima è pratica (pochi strumenti, pochi costi, poca manutenzione); la seconda è intellettuale. Un portafoglio così si può **falsificare meglio**: testandolo su 31 anni, e su regimi molto diversi tra loro, il rischio di raccontarmi una favola cala parecchio. Se un'allocazione regge la bolla dot-com, il 2008, il decennio perso europeo e il 2022, è un'evidenza più solida di una che "funziona" solo sull'unico ciclo toro che le è stato cucito addosso.

Resta il bias di fondo, e lo prendo in carico: sono io a giudicare il portafoglio che io stesso ho costruito, oggi, conoscendo la storia. Ne parlo nei limiti. Ma anticipo un dettaglio che conta: se avessi sovra-ottimizzato, avrei "vinto" contro tutti. Invece contro l'S&P 500 pareggio. È il tipo di risultato che ci si aspetta da una scommessa strutturale onesta, non da un backtest torturato fino alla confessione.

## Parte 1 — Cosa c'è nel portafoglio, e perché

L'allocazione target, con la serie storica usata per ciascuna classe:

| Sleeve | Peso | Serie storica (proxy) |
|---|---|---|
| Azionario USA | 20% | S&P 500 Total Return (dal 1993) |
| Mercati Emergenti | 20% | MSCI Emerging Markets TR (dal 1987) |
| Nasdaq / Tech | 25% | Nasdaq Composite + dividendo figurato 0,75%/anno |
| Smallcap | 10% | Russell 2000 Total Return (dal 1995) |
| Europa Momentum | 8% | MSCI Europe Momentum TR (dal 1994) |
| Oro | 8% | Oro fisico, prezzo LBMA (dal 1985) |
| Energia | 9% | S&P 500 Energy + dividendo figurato 2,9%/anno |
| **Totale** | **100%** | |

<figure>
  <img src="/charts/portafoglio-personale-backtest/01_composizione_donut.png?v=2" alt="Grafico a ciambella dell'allocazione target: Nasdaq/Tech 25%, USA 20%, Mercati Emergenti 20%, Smallcap 10%, Energia 9%, Oro 8%, Europa Momentum 8%." />
  <figcaption>Sette classi, tutte ad ampia storia. Il portafoglio è equity-only e viene ribilanciato a target una volta l'anno.</figcaption>
</figure>

### La logica: mean reversion ciclica

L'idea che tiene insieme il portafoglio è semplice: **la leadership dei mercati ruota**. Ci sono grandi cicli in cui un settore o un'area geografica domina — gli USA e la tecnologia negli anni '90 e dal 2010, gli emergenti nei primi anni 2000, l'energia nei periodi di inflazione — e poi il testimone passa. Chi concentra tutto sul vincitore dell'ultimo ciclo rischia di comprarlo proprio prima che il ciclo giri. Questo portafoglio fa la scommessa opposta: **spalma i pesi sui protagonisti della rotazione**, e li ribilancia ogni anno, così vende meccanicamente un po' di ciò che è corso e compra un po' di ciò che è rimasto indietro.

Letta per blocchi:

- **Motore azionario di base** (USA 20%): l'ancora, il mercato più efficiente e profondo.
- **Cuore aggressivo** (Nasdaq/Tech 25%): la scommessa sulla tecnologia come motore di lungo periodo. È la fetta più grande, ed è ciò che dà al portafoglio il suo rendimento — e la sua volatilità.
- **Geografia in rotazione** (Emergenti 20% + Europa Momentum 8% = 28%): la scommessa sulla mean reversion geografica, cioè che le aree oggi indietro rispetto agli USA non lo restino per sempre.
- **Premio dimensionale** (Smallcap 10%): dove storicamente si è trovato il premio per la piccola capitalizzazione.
- **Sleeve difensiva reale** (Oro 8% + Energia 9% = 17%): due attivi reali che difendono proprio quando l'azionario soffre.

### La sleeve difensiva: oro ed energia

Molti portafogli mettono le obbligazioni come cuscinetto. Qui il cuscinetto sono **attivi reali**. La ragione è che i due grandi nemici di un portafoglio azionario di lungo periodo non sono solo i crolli di Borsa, ma l'**inflazione** e i regimi di **stress geopolitico** — ed è lì che oro ed energia storicamente brillano, mentre le obbligazioni a tasso fisso soffrono. Non è teoria: è ciò che, nei numeri della Parte 2, dà al portafoglio il drawdown più basso di tutti i benchmark, S&P 500 incluso.

### Perché la versione "Momentum" per l'Europa

Per l'Europa non uso l'indice classico ma la sua versione **momentum**. Non è un vezzo: un confronto diretto delle due serie storiche mostra una netta superiorità della momentum. Dal 1994 al 2026 la MSCI Europe Momentum ha reso circa l'**11,0% annuo** contro il **9,1%** della MSCI Europe classica, con Sharpe e Sortino migliori — e proprio in un periodo, il 2000-2020, che per l'azionario europeo è stato difficile, laterale e ricco di crisi. Il momentum è uno dei fattori più documentati della letteratura finanziaria: qui lo uso come si deve, cioè applicato in modo sistematico da un indice, non a mano.

### Una nota su metodo e dati

Lavoriamo, come sempre, in **Total Return lordo** (dividendi reinvestiti, al lordo di costi e tasse). Cinque delle sette serie sono già total return native; due sono indici a prezzo, e vi ho aggiunto un **dividendo figurato costante** dichiarato: **0,75%/anno** al Nasdaq Composite (in linea con il rendimento storico da dividendo dell'indice) e **2,9%/anno** all'energia (il settore a più alto dividendo del mercato — ignorarlo falserebbe pesantemente il risultato). È l'ipotesi più sensibile del pezzo, e la metto in chiaro. Il ribilanciamento è annuale, al 1° gennaio.

## Parte 2 — Il backtest su 31 anni

Immagina 10.000 € investiti a luglio 1995 e lasciati lavorare, con il portafoglio ribilanciato a target ogni gennaio.

<figure>
  <img src="/charts/portafoglio-personale-backtest/02_equity_lump.png" alt="Curve di crescita in scala logaritmica dal 1995 al 2026 di 10.000 € investiti: portafoglio e S&P 500 finiscono vicini e molto sopra MSCI World e ACWI IMI." />
  <figcaption>Portafoglio (blu) e S&P 500 (oro) arrivano quasi insieme e molto sopra World e ACWI. Ma il percorso racconta la storia: nella bolla dot-com il portafoglio resta indietro all'S&P, poi lo protegge meglio nei crolli.</figcaption>
</figure>

La curva è più interessante del punto d'arrivo. **Tra il 1995 e il 2000 il portafoglio resta indietro all'S&P 500**: mentre gli USA e la tecnologia corrono, la diversificazione geografica e la sleeve difensiva ti costano. Poi arriva il 2000, e la rotazione: **nel crollo dot-com e nel 2008 il portafoglio protegge meglio**, e recupera il terreno. Sul ciclo intero le due curve si riallineano. È esattamente il profilo che ci si aspetta dalla tesi della leadership ciclica: rinunci a un po' di corsa nei melt-up americani, la recuperi nei crolli e sulle rotazioni.

Le metriche sul periodo pieno:

| Metrica | Portafoglio | S&P 500 TR | MSCI World TR | MSCI ACWI IMI TR |
|---|---|---|---|---|
| CAGR | **10,83%** | 10,69% | 8,42% | 8,20% |
| Volatilità | 15,9% | 15,1% | 15,1% | 15,5% |
| Max drawdown | **−48,4%** | −50,8% | −54,0% | −55,1% |
| Sharpe | 0,73 | 0,75 | 0,61 | 0,59 |
| Sortino | 0,98 | 1,05 | 0,82 | 0,77 |
| Calmar | **0,224** | 0,211 | 0,156 | 0,149 |
| 10.000 € → | **244.706 €** | 235.053 € | 123.386 € | 115.757 € |

<figure>
  <img src="/charts/portafoglio-personale-backtest/05_metriche.png" alt="Barre di CAGR, volatilità, max drawdown e Calmar: portafoglio e S&P vicini e sopra World/ACWI, con il portafoglio che ha il drawdown più basso e il Calmar più alto." />
  <figcaption>CAGR, volatilità, max drawdown e Calmar. Il portafoglio ha il drawdown più basso di tutti e il Calmar più alto; contro l'S&P 500 la partita è alla pari.</figcaption>
</figure>

Va letta con onestà. Contro l'**S&P 500** il portafoglio ha un CAGR appena più alto e un drawdown più basso, ma una volatilità un po' maggiore: sul rischio corretto (Sharpe, Sortino) sono praticamente pari, con un lieve vantaggio del portafoglio solo sul Calmar (che pesa il drawdown). Tradotto: **è un pareggio**. Contro **World e ACWI**, invece, il vantaggio è su tutte le voci: più rendimento, meno drawdown, Sharpe e Sortino più alti.

### Le finestre mobili

Il punto d'arrivo dipende dalla data di partenza. Per questo guardiamo **tutte** le finestre mobili: ogni possibile decennio di ingresso dal 1995 a oggi.

<figure>
  <img src="/charts/portafoglio-personale-backtest/04_rolling_10y.png" alt="Boxplot dei rendimenti annualizzati su tutte le finestre mobili di 10 anni: la distribuzione del portafoglio è spostata verso l'alto rispetto a World e ACWI, in linea con l'S&P." />
  <figcaption>Rendimento annualizzato su tutte le finestre mobili di 10 anni. Il portafoglio (blu) sta con l'S&P e sopra World/ACWI, con una mediana del 10,0%.</figcaption>
</figure>

Su tutte le finestre di 10 anni, la mediana del portafoglio è **10,0%** annuo, contro l'8,1% dell'S&P nello stesso set di finestre, il 7,2% del World e il 7,5% dell'ACWI. In termini di "chi ha vinto": il portafoglio batte il **World nel 98%** delle finestre decennali e l'**ACWI nel 100%**; contro l'S&P 500 vince nel **53%** — testa o croce, che sale al **64%** sulle finestre di 15 anni. Sulle finestre di 5 anni, più rumorose, contro l'S&P scende al 43%: nel breve, quando gli USA corrono, il portafoglio più diversificato può restare indietro.

E lo stesso spirito vale col **PAC**: 200 €/mese dal 1995 (74.600 € versati in tutto) diventano **568.379 €** col portafoglio, 534.657 € con l'S&P, 366.985 € col World e 354.254 € con l'ACWI.

### Lo scenario peggiore

Medie e mediane raccontano il caso tipico. Ma il rischio vero, per chi investe, è **entrare nel momento sbagliato** — e lì i numeri sono la parte più interessante di tutto il backtest. Per ogni possibile finestra di 5 e di 10 anni dei 31 ho preso il rendimento annualizzato del **caso peggiore** e il 5° percentile.

<figure>
  <img src="/charts/portafoglio-personale-backtest/07_worst_windows.png" alt="Barre del rendimento annualizzato nella finestra peggiore, a 5 e 10 anni: il portafoglio ha la barra meno negativa a 5 anni e l'unica positiva a 10 anni, contro S&P, World e ACWI tutti in negativo." />
  <figcaption>Il rendimento annualizzato di chi entra nel momento peggiore. A 10 anni il portafoglio è l'unico dei quattro a restare in positivo.</figcaption>
</figure>

Il quadro è netto. Sulla **peggiore finestra di 10 anni** dei 31 — quella di chi ha investito nel marzo 1999, a un passo dallo scoppio della bolla dot-com — il portafoglio ha reso **+3,1% all'anno**. È l'unico dei quattro a non aver perso: nello stesso decennio maledetto l'S&P 500 ha fatto **−3,4%** annuo, il World −2,5%, l'ACWI −1,3%. E non è un episodio isolato: il **5° percentile** dei rendimenti decennali del portafoglio è +4,7% annuo, mentre per i benchmark è intorno allo zero o negativo. Su **nessuna** finestra di 10 anni dei 31 il portafoglio avrebbe lasciato l'investitore in perdita; per S&P, World e ACWI è successo.

Sulle finestre di **5 anni** vale la stessa gerarchia: il caso peggiore del portafoglio è **−2,3%** annuo, contro il −6,7% dell'S&P, il −5,7% del World e il −5,4% dell'ACWI. E il 5° percentile del portafoglio resta **positivo** (+1,4%), l'unico dei quattro.

Un chiarimento onesto, perché non sembri magia. Questa protezione **non** significa che il portafoglio non crolli: il max drawdown *dentro* le finestre resta pieno, intorno al **−48%** — è un portafoglio 100% azionario e nei crolli scende come gli altri. Ciò che la sleeve difensiva reale (oro + energia) e la diversificazione geografica comprano non è l'assenza del crollo, ma un **recupero più rapido**: chi resta investito 5-10 anni finisce con un risultato molto meno rovinato di chi ha in mano il solo indice concentrato. È esattamente il motivo per cui il decennio 1999-2009, disastroso per gli USA e per il mondo sviluppato, è stato tollerabile per un portafoglio pieno di emergenti, oro ed energia: mentre la tecnologia si sgonfiava, quelle classi vivevano il loro ciclo. La mean reversion, di nuovo.

## Parte 3 — Il Monte Carlo: cosa potremmo aspettarci

Il backtest dice cosa è successo. Per stimare cosa *potrebbe* succedere, generiamo **10.000 traiettorie** con un bootstrap a blocchi di 3 mesi sui rendimenti storici del portafoglio e dei benchmark (campionati insieme, per non spezzare il loro co-movimento), su orizzonti di 10, 20 e 30 anni, partendo da 10.000 €.

<figure>
  <img src="/charts/portafoglio-personale-backtest/06_montecarlo.png" alt="Monte Carlo: valore finale mediano del portafoglio con range 5-95 percentile a 10, 20 e 30 anni, con le mediane dei benchmark sovrapposte; il portafoglio è in linea con l'S&P e sopra World/ACWI." />
  <figcaption>Valore finale di 10.000 € nelle 10.000 traiettorie: mediana del portafoglio (barra) e range dal 5° al 95° percentile, con le mediane dei benchmark. In linea con l'S&P, sopra World e ACWI.</figcaption>
</figure>

A **20 anni**, la mediana del portafoglio è **78.407 €**, contro 76.067 € dell'S&P, 49.641 € del World e 47.796 € dell'ACWI. L'incertezza è grande, come dev'essere: dal 5° al 95° percentile si va da ~23.000 € a ~257.000 €. In termini di probabilità di battere il benchmark: il portafoglio batte il **World nel 98%** degli scenari a 20 anni, l'**ACWI nel 100%**, e l'S&P nel **55%**. A 30 anni la mediana sale a **220.468 €** e le probabilità restano le stesse: pareggio contro l'S&P, vittoria quasi certa contro i benchmark globali.

Coerente col backtest: la simulazione non conosce il futuro, ma proietta in avanti la stessa struttura — un portafoglio che compete con l'S&P 500 e stacca il resto del mondo.

## Cosa porto a casa

1. **Non batte l'S&P 500, lo eguaglia — con meno rischio nei crolli.** E va detto per primo, perché è la parte scomoda. Chi vuole "battere l'America" con la diversificazione geografica, sui dati di questi 31 anni, resta deluso: l'S&P è stato il benchmark più duro. Il portafoglio ci arriva alla pari, con il drawdown più basso.

2. **Il confronto giusto lo vince nettamente.** Un portafoglio diversificato a livello globale va confrontato con un indice globale, non solo con l'S&P: contro MSCI World e ACWI IMI il vantaggio è di 2,4-2,6 punti di CAGR all'anno, con meno drawdown, e regge nel 93-100% delle finestre e degli scenari simulati.

3. **La sleeve difensiva reale (oro + energia) è ciò che compra il vantaggio sul rischio.** Costa qualcosa negli anni tori — non partecipa ai melt-up tecnologici — ma è la ragione per cui il drawdown è il più basso del gruppo. Chi non regge di veder "fermo" un 17% del portafoglio quando la Borsa corre, difficilmente lo terrà nei momenti in cui serve.

4. **È equity-only, con volatilità piena.** Nessuna obbligazione: max drawdown storico intorno al −48%. Ha senso su un orizzonte di 15-20 anni o più, e con lo stomaco per attraversare un dimezzamento del capitale senza vendere.

5. **Il bias resta, e lo dichiaro.** Il portafoglio è disegnato conoscendo la storia. L'uso di classi ampie e il pareggio con l'S&P lo rendono molto meno sospetto di un backtest cucito sui vincitori, ma il limite epistemico è quello di sempre: il passato informa, non promette. E due dividendi (Nasdaq, energia) sono ipotesi dichiarate, non dati.

Come per tutta la rubrica: felice di passare al setaccio anche il portafoglio di un lettore. Mandami composizione e pesi, e lo testiamo con lo stesso metodo.

## Fonti e riproducibilità

- Serie storiche in Total Return: S&P 500 (SPY adj close, dal 1993), MSCI Emerging Markets (dal 1987), Nasdaq Composite (dal 1975, + dividendo figurato 0,75%/anno), Russell 2000 TR (dal 1995), MSCI Europe Momentum (dal 1994), oro fisico LBMA (dal 1985), S&P 500 Energy (dal 1993, + dividendo figurato 2,9%/anno). Benchmark: S&P 500 TR, MSCI World TR (dal 1969), MSCI ACWI IMI TR (dal 1994).
- Finestra comune del backtest: luglio 1995 – luglio 2026 (373 mesi). Ribilanciamento annuale, lordo. Monte Carlo: bootstrap a blocchi di 3 mesi, 10.000 traiettorie.
- Tutti i numeri e i grafici sono generati da `scripts/portafoglio-personale-backtest.py`, `scripts/portafoglio-personale-montecarlo.py` e `scripts/portafoglio-personale-downside.py` (analisi del caso peggiore). Le simulazioni usano ipotesi dichiarate e semplificate a scopo illustrativo e non predittivo.
