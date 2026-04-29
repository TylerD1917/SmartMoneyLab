---
title: "Ha senso inserire oro in portafoglio?"
description: "Quattro portafogli buy & hold a confronto (100% azionario, 90/10, 75/25, 50/50 oro) su 50 anni di dati S&P 500 e LBMA Gold. Cosa dicono i numeri sull'asset più chiacchierato della finanza retail."
pubDate: 2026-04-29
tags: ["oro", "asset-allocation", "diversificazione", "rolling-windows", "backtest"]
author: "SmartMoneyLab"
simulationSlug: "ha-senso-oro-portafoglio"
draft: false
---

## In breve

Su 50 anni di dati (gennaio 1976 – dicembre 2025), confronto quattro portafogli **buy & hold** — 100% azionario, 90/10, 75/25, 50/50 (azioni / oro) — su tutte le finestre rolling a 5, 10 e 20 anni con step di 3 mesi. Tre risultati centrali emergono dai numeri:

1. **L'oro è empiricamente decorrelato dall'azionario** sul periodo: la correlazione mensile tra S&P 500 Total Return e LBMA Gold è **0.0085**. Praticamente zero. Non è un argomento teorico — sono 600 mesi di osservazione in cui i due asset si sono mossi in modo sostanzialmente indipendente.
2. **Il costo in rendimento è bassissimo**: il 50/50 ha un CAGR full-sample di 10.60% contro 11.90% del pure-equity. Solo 130 punti base in meno. Il 90/10 perde appena 20 punti base (11.70%). Una geometria completamente diversa rispetto alle obbligazioni, dove il 60/40 perdeva quasi 250 punti base nel periodo equivalente.
3. **La protezione nei peggiori scenari decennali è netta e robusta**: nel 5% delle finestre 10 anni andate peggio, il 100% azionario chiude col 1.18% annualizzato; il 50/50 col 6.43%. *Ogni* allocazione con oro batte il pure-equity nei worst case 10Y.

C'è anche un dato che disinnesca un mito che molti investitori si raccontano: **a 20 anni nessun portafoglio buy & hold ha evitato i drawdown profondi**. Nel 100% azionario *tutte* le 121 finestre 20Y hanno visto almeno un drawdown del −20%, e il 78.5% ha visto un drawdown del −30% o peggio. Anche il 50/50 oro: il 99% delle finestre ha drawdown ≥ −20%. Sul lungo periodo non si scappa dalla volatilità — si scappa solo dalle perdite definitive a parità di tempo.

## La domanda

L'oro è probabilmente l'asset più chiacchierato della finanza retail italiana. Lo sento citare in due modi inconciliabili:

- *Bene rifugio*, lo strumento contro l'inflazione, l'unico vero "store of value".
- *Asset speculativo* per definizione, qualcosa che non produce niente, che vale solo quello che il prossimo è disposto a pagare.

Entrambe le posizioni hanno argomenti validi. Quello che manca, quasi sempre, è una verifica seria sui dati. Voglio rispondere a tre domande in sequenza:

1. **Ha senso** inserire oro in portafoglio?
2. **Quando** ha senso?
3. **Quanto**?

L'angolo che voglio testare è il seguente: *probabilmente l'oro ha senso in portafoglio, nonostante sia per eccellenza un asset speculativo che non produce valore come le azioni.* Se è così, lo deve dimostrare l'evidenza empirica — non il marketing dei broker che vendono ETC sull'oro né l'aneddotica del cugino.

## Il metodo: rolling windows e buy & hold puro

Confermo l'impianto metodologico stabilito col primo articolo del blog — è il pattern che useremo in tutti i confronti tra asset allocation:

- Costruisco le serie mensili di rendimenti totali per i quattro portafogli su tutto il periodo **gennaio 1976 – dicembre 2025** (600 mesi, ovvero 50 anni pieni).
- Per ogni portafoglio, calcolo le metriche su **tutte le finestre 5Y** (60 mesi), **10Y** (120 mesi) e **20Y** (240 mesi), con uno **step di 3 mesi**. In totale ottengo 181 finestre 5Y, 161 finestre 10Y e 121 finestre 20Y per ciascun portafoglio.
- I rendimenti sono **lordi** (no costi degli ETF, no tasse). Lo scopo è isolare la tesi sull'allocazione dal rumore dei costi.
- **Total Return**: i rendimenti dell'azionario includono i dividendi reinvestiti — formula standard `r_t = (P_t + D_{t-1}/12) / P_{t-1} - 1` ricostruita dal dataset Shiller. L'oro non genera flussi (no cedole, no dividendi), quindi il suo "total return" coincide col price return.
- **Buy & hold puro**: nessun rebalancing in nessuno dei quattro portafogli. Compri all'inizio coi pesi target, lasci stare. Per le finestre rolling ogni finestra parte fresh dai pesi iniziali, è il framing del lettore retail (*"se compro oggi un 90/10 e lo tengo 10 anni senza toccarlo, cosa mi aspetto?"*).

### Le scelte tecniche

- **Azionario**: S&P 500 Total Return, serie mensile ricostruita dal dataset Shiller.
- **Oro**: prezzo LBMA Gold mensile in USD/oz, serie 1950+ disponibile sul mirror GitHub `datasets/gold-prices` (la stessa serie LBMA che FRED ha smesso di distribuire da gennaio 2022, in seguito alla revoca della licenza da parte di ICE Benchmark Administration).

Lo script Python che produce tutte le serie e i grafici è in [`scripts/ha-senso-oro-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-oro-portafoglio.py) — riga per riga, riproducibile.

> **Limite onesto**: questa è un'analisi USA-centric, in dollari, sulla serie LBMA Gold (London PM Fix). Non è esattamente l'esperienza di un investitore italiano che compra ETC fisici sull'oro su Borsa Italiana (come Xetra-Gold o iShares Physical Gold), perché manca la dinamica del cambio EUR/USD. Sul lungo termine, però, l'oro tende a rivalutarsi rispetto a tutte le valute fiat in misura comparabile, quindi i risultati qualitativi dovrebbero reggere — la replica EUR-centric sarà un articolo successivo.

## L'oro come asset speculativo: vale davvero il suo prezzo?

Prima di guardare i dati conviene affrontare l'argomento che *non* si può ignorare. Warren Buffett, Charlie Munger, e una lunga tradizione di investitori value lo ripetono da decenni: **l'oro non produce nulla**. Non genera utili come un'azione, non paga cedole come un'obbligazione, non sforna affitti come un immobile. Buffett, in una lettera famosa agli azionisti del 2011, fa il calcolo: tutto l'oro estratto nella storia formerebbe un cubo di circa 21 metri di lato. A prezzi correnti, il valore di quel cubo è confrontabile con quello dell'intero S&P 500. Differenza: il cubo continuerà a essere un cubo, mentre l'S&P 500 produce ogni anno utili e dividendi reinvestibili.

L'argomento è solido e non si può smontare con la retorica. **L'oro non ha valore intrinseco calcolabile** nel senso classico: non puoi attualizzare flussi futuri perché non ci sono. Vale quello che il prossimo compratore è disposto a pagare. È, in senso tecnico, un asset speculativo.

I controargomenti a favore dell'oro non sono di tipo finanziario tradizionale, sono di tipo strutturale:

- **Store of value su orizzonti lunghissimi**. Nei millenni, l'oro ha mantenuto un potere d'acquisto comparabile (storia romana e contemporanea). Le valute fiat si svalutano per costruzione (Banca Centrale → debasement); l'oro non si svaluta perché la sua quantità globale cresce a tassi annui dello 1-2% per estrazione, contro tassi di crescita della massa monetaria fiat anche superiori al 5-10% in periodi inflazionistici.
- **Decorrelazione strutturale dalle valute e dai mercati finanziari**. Quando le banche centrali stampano per finanziare deficit, l'oro tende a salire perché è il "denaro di scarto" del sistema fiat. Quando la fiducia istituzionale cala (rischio di guerra, sanzioni, congelamento di asset), l'oro è uno dei pochi asset al di fuori del perimetro del sistema bancario.
- **Hedge contro tail risk**. È il motivo per cui le banche centrali ne tengono migliaia di tonnellate nelle riserve.

Tutti argomenti plausibili a livello narrativo. Ma quel che ci interessa, su questo blog, è la verifica empirica. Allora la domanda diventa: **nei dati 1976-2025, l'oro si è effettivamente comportato come un diversificatore vero?**

La risposta è **sì, in modo più netto di quanto mi aspettassi**. La correlazione mensile tra S&P 500 Total Return e LBMA Gold sull'intero periodo è **0.0085** — sostanzialmente zero. Significa che, su 600 mesi di osservazione, il movimento di un asset non ha praticamente alcuna capacità di prevedere il movimento dell'altro. Per metterla in prospettiva: la correlazione tipica tra azioni USA e obbligazioni governative USA si è mossa storicamente tra +0.3 (anni '80) e −0.4 (post-GFC). I bond *correlano* con l'azionario, anche se in modo variabile. **L'oro proprio no.**

Questo è già un primo punto: **a livello statistico l'oro è un diversificatore vero**, non un diversificatore "marketing". Indipendentemente dalla critica filosofica sull'assenza di valore intrinseco, *empiricamente* aggiungere oro a un portafoglio azionario riduce il rischio specifico senza contropartite di rendimento equivalenti — almeno fino a un certo punto, come vedremo. La domanda residua è quanto questa decorrelazione si traduca in vantaggio di portafoglio reale, e a quale costo. È quello che misureremo adesso.

## Risultati su finestre 10 anni

Iniziamo dall'orizzonte intermedio, dove il "premio del rischio" azionario inizia a manifestarsi ma non è ancora del tutto saturato:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/01_boxplot_cagr_10y.png" alt="Boxplot del CAGR su finestre rolling 10 anni — 100% azionario, 90/10, 75/25, 50/50 oro. Distribuzioni dei rendimenti annualizzati composti, S&P 500 Total Return + LBMA Gold, dati 1976-2025." />
  <figcaption>Distribuzione del CAGR su finestre 10 anni, step 3 mesi. 161 finestre per portafoglio. Box centrale = 25°-75° percentile. Linea nera = mediana. Baffi = 5°-95° percentile.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | p5    | p25   | **Mediana** | p75    | p95    |
|-------------|-------|-------|-------------|--------|--------|
| 100% E      | 1.18% | 7.91% | **13.18%**  | 14.99% | 18.14% |
| 90/10       | 4.31% | 8.17% | **12.60%**  | 14.37% | 17.18% |
| 75/25       | 6.19% | 8.49% | **11.38%**  | 13.40% | 15.42% |
| 50/50       | 6.43% | 7.96% | **9.58%**   | 11.42% | 13.60% |

Lettura del dato:

- **Sui valori mediani** l'azionario domina, ma il margine è molto più ridotto rispetto al confronto azioni/obbligazioni: 13.18% del 100E contro 12.60% del 90/10 (spread di soli 60 punti base) e 9.58% del 50/50 (spread di 360 punti base, contro i ~240 punti base che il 60/40 perdeva nello scorso articolo).
- **Sui peggiori scenari (p5) l'oro vince in modo netto**. Il 100% azionario ha p5 a 1.18% — una decina assolutamente "perduta" in termini reali, considerata l'inflazione media. Il 50/50 ha p5 a 6.43%, oltre 5 punti percentuali in più. Ma anche il 90/10, che aggiunge solo un 10% di oro, alza il p5 a 4.31% — protezione moderata ma non simbolica.
- **Sulla frequenza di chiusure 10y in negativo**: il 100E chiude in perdita nel 5% delle finestre (8 su 161). Il 75/25 e il 50/50 mai. Il 90/10 una sola finestra negativa su 161 — sostanzialmente eliminato.

Il quadro qualitativo è simile a quello dei bond — l'azionario domina in mediana, gli asset di diversificazione proteggono nelle code. Ma quantitativamente il trade-off è molto più favorevole all'oro: paga molto meno in rendimento mediano e protegge molto di più nei peggiori scenari.

## Risultati su finestre 5 anni

A 5 anni le code della distribuzione si allargano e l'azionario inizia a sbattere contro periodi in cui non c'è stato tempo di recuperare:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/02_boxplot_cagr_5y.png" alt="Boxplot del CAGR su finestre rolling 5 anni — 100% azionario, 90/10, 75/25, 50/50 oro. Distribuzioni dei rendimenti annualizzati, S&P 500 Total Return + LBMA Gold, dati 1976-2025." />
  <figcaption>Distribuzione del CAGR su finestre 5 anni, step 3 mesi. 181 finestre per portafoglio.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | p5      | p25   | **Mediana** | p75    | p95    | % finestre con CAGR < 0 |
|-------------|---------|-------|-------------|--------|--------|--------------------------|
| 100% E      | −1.64%  | 8.63% | **13.80%**  | 16.25% | 23.21% | **9.4%**                 |
| 90/10       | −0.21%  | 8.54% | **12.85%**  | 15.17% | 21.36% | 6.1%                     |
| 75/25       | 1.34%   | 8.31% | **11.20%**  | 14.48% | 19.08% | 1.1%                     |
| 50/50       | 3.45%   | 6.70% | **9.87%**   | 12.87% | 17.65% | 1.1%                     |

Cosa salta all'occhio:

- **A 5 anni il 100% azionario chiude in perdita nel 9.4% delle finestre**: 17 finestre su 181. Sono i quinquenni che includono il pieno del dot-com burst, o il pieno della Crisi Finanziaria 2008-2009.
- **Il 50/50 e il 75/25 chiudono in perdita nel 1.1% delle finestre**: 2 finestre su 181. Sostanzialmente eliminato il rischio di chiusura 5Y in negativo.
- **Il p5 del 50/50 (3.45%) è oltre 5 punti percentuali sopra il p5 del 100E (−1.64%)**.

A 5 anni l'oro "compra" tranquillità in modo molto efficiente: paga ~4 punti percentuali sulla mediana, ma elimina il rischio di chiusura negativa.

## Risultati su finestre 20 anni: la convergenza

Con 50 anni di dati a disposizione, possiamo guardare anche le finestre 20Y — orizzonte tipico di un piano pensionistico in fase di accumulo:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/05_boxplot_cagr_20y.png" alt="Boxplot del CAGR su finestre rolling 20 anni — 100% azionario, 90/10, 75/25, 50/50 oro. Distribuzioni dei rendimenti annualizzati, S&P 500 Total Return + LBMA Gold, dati 1976-2025." />
  <figcaption>Distribuzione del CAGR su finestre 20 anni, step 3 mesi. 121 finestre per portafoglio.</figcaption>
</figure>

Numeri esatti:

| Portafoglio | p5    | p25   | **Mediana** | p75    | p95    |
|-------------|-------|-------|-------------|--------|--------|
| 100% E      | 6.13% | 8.20% | **9.95%**   | 13.18% | 17.27% |
| 90/10       | 6.51% | 8.13% | **9.78%**   | 12.64% | 16.66% |
| 75/25       | 6.88% | 8.11% | **9.55%**   | 11.73% | 15.63% |
| 50/50       | 6.89% | 7.79% | **8.88%**   | 10.08% | 13.42% |

Su 20 anni i quattro portafogli **convergono drammaticamente**:

- Le mediane vanno da 9.95% (100E) a 8.88% (50/50). Spread di soli ~107 punti base.
- I p5 sono praticamente identici: tra 6.13% (100E) e 6.89% (50/50). Spread di 76 punti base.
- **Nessuna finestra 20Y in negativo per nessun portafoglio**.

Il dato è interessante perché ribalta il framing tipico: a 5 e 10 anni l'oro "vince" più chiaramente nei peggiori scenari, ma a 20 anni la differenza si appiattisce moltissimo. Il tempo lavora a favore dell'azionario: dato abbastanza tempo, anche le peggiori 10Y vengono assorbite dalle 10Y successive di recovery.

> Detto in altro modo: **se hai veramente 20 anni davanti, la decisione tra 100E e 90/10 è quasi indifferente in termini di rendimento finale atteso, ma l'oro ti ha protetto nei sub-periodi**. Quindi è una scelta di tolleranza psicologica al drawdown lungo il viaggio, non di rendimento finale.

## I drawdown: cosa succede lungo il percorso

Il rendimento finale è solo metà della storia. Il **max drawdown** (MDD) — il peggior calo subito dal portafoglio dal massimo al minimo successivo — racconta cosa hai dovuto sopportare per arrivarci.

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/03_drawdown_distribution_5y.png" alt="Distribuzione del max drawdown su finestre rolling 5 anni per i quattro portafogli. Curva cumulata empirica del peggior drawdown osservato dentro ciascuna finestra." />
  <figcaption>Distribuzione cumulata del max drawdown osservato all'interno di ogni finestra 5Y. Più la curva è "spostata a destra" (verso drawdown meno profondi), meglio.</figcaption>
</figure>

Tabella riassuntiva delle frequenze di drawdown profondi:

| Portafoglio | % finestre 5Y con MDD ≤ −20% | % finestre 5Y con MDD ≤ −30% | % finestre 10Y con MDD ≤ −20% | % finestre 10Y con MDD ≤ −30% | % finestre 20Y con MDD ≤ −20% | % finestre 20Y con MDD ≤ −30% |
|-------------|-------------------------------|-------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|
| 100% E      | 34.3%                         | 19.3%                         | 67.1%                          | 40.4%                          | **100%**                       | **78.5%**                      |
| 90/10       | 34.8%                         | 17.7%                         | 70.8%                          | 39.8%                          | **100%**                       | 77.7%                          |
| 75/25       | 34.3%                         | 7.2%                          | 65.2%                          | 23.0%                          | **100%**                       | 57.9%                          |
| 50/50       | 23.8%                         | 7.2%                          | 54.0%                          | 17.4%                          | **99.2%**                      | 56.2%                          |

Tre cose vanno notate:

- **Il 90/10 protegge poco dai drawdown.** Aggiungere un 10% di oro abbassa di pochissimo la frequenza di drawdown profondi (in alcune righe è addirittura leggermente peggiore del 100E nelle 10Y, perché il 10% non è abbastanza per fare massa). La protezione vera nei drawdown arriva dal 25% in su.
- **Il 50/50 dimezza il rischio nelle 5Y**, da 19.3% a 7.2% di finestre con MDD ≤ −30%. Significativo.
- **A 20 anni nessun portafoglio sfugge ai drawdown profondi**: nel 100% delle finestre il pure-equity ha visto un MDD ≥ −20% in qualche momento. Anche il 50/50 al 99.2%. La probabilità di avere drawdown ≥ −30% in una finestra 20Y va dal 78.5% (100E) al 56.2% (50/50). Tradotto: se investi per 20 anni e la tua testa non regge un −40% lungo il tragitto, devi diminuire la quota azionaria *molto* — non basta diversificare con un 10-25% di oro. O, in alternativa, devi accettare che vivrai un brutto drawdown lungo il tragitto e fare pace con la cosa adesso.

## L'equity curve: come si vede il trade-off su un caso reale

Per visualizzare il trade-off in modo cumulativo, il grafico più informativo è la curva del valore di 1 dollaro investito a inizio 1976, fino a fine 2025:

<figure>
  <img src="/charts/ha-senso-oro-portafoglio/04_equity_curve.png" alt="Equity curve dei quattro portafogli (100% azionario, 90/10, 75/25, 50/50 oro) dal 1976 al 2025, scala logaritmica. Crescita di 1 USD investito a inizio 1976 — buy & hold puro." />
  <figcaption>Crescita cumulata di 1 USD investito a gennaio 1976 con i pesi target iniziali, buy & hold puro. Scala logaritmica.</figcaption>
</figure>

> **Come si legge questo grafico — importante.** Come nell'articolo precedente, **questa è una sola simulazione, non una statistica**. Letteralmente: prendo 1 USD a gennaio 1976, lo divido secondo i pesi target (es. 50% azioni e 50% oro nel 50/50), e poi non tocco più nulla fino a dicembre 2025. È quindi *un* possibile percorso, *uno* specifico investitore che ha avuto la sorte (o sfortuna) di iniziare proprio in quel mese. Le statistiche robuste sull'allocazione sono nelle finestre rolling sopra (181 + 161 + 121 finestre, ognuna con il proprio punto di partenza). L'equity curve serve per **vedere visivamente cosa accade su un percorso reale** — è didattica, non predittiva.

Numeri di riepilogo full-sample (1976–2025, buy & hold puro):

| Portafoglio | CAGR full-sample | Volatilità annualizzata | Max drawdown |
|-------------|------------------|--------------------------|--------------|
| 100% E      | 11.90%           | 12.28%                   | −49.04%      |
| 90/10       | 11.70%           | 12.09%                   | −48.11%      |
| 75/25       | 11.34%           | 12.13%                   | −46.32%      |
| 50/50       | 10.60%           | 12.51%                   | −41.45%      |

1 USD investito nel gennaio 1976 diventa, dopo 50 anni:
- ~$282 col 100% azionario
- ~$256 col 90/10
- ~$216 col 75/25
- ~$152 col 50/50

Sembra una grande differenza, ma è il risultato della capitalizzazione su 50 anni. La differenza percentuale finale tra 100E e 50/50 è 46% — meno dell'aspettativa che si avrebbe guardando solo il CAGR. È coerente con la decorrelazione: quando azioni e oro si muovono indipendentemente, la combinazione tende a "compensare" parte della perdita di rendimento atteso con guadagno di stabilità.

> **Curiosità sulla volatilità.** Da notare un dettaglio: il 50/50 ha **volatilità annualizzata del 12.51%, leggermente più alta del 100E (12.28%)**. È un risultato controintuitivo: ti aspetteresti che diversificare riduca sempre la volatilità. Quello che succede è che l'oro porta la sua propria volatilità (~16%/anno storica), e a un peso del 50% questa volatilità contribuisce in modo non trascurabile, anche con correlazione zero. Il 90/10, invece, ha la volatilità più bassa di tutti (12.09%) — è il "punto dolce" della diversificazione su questi due asset.

## Quindi: ha senso? Quando? Quanto?

Riassumo i fatti che emergono dai dati:

1. **L'oro è empiricamente decorrelato dall'azionario** sui 50 anni analizzati (correlazione mensile 0.0085). Non è un argomento teorico: è un dato di osservazione robusto.
2. **Il costo in CAGR pagato per inserire oro è basso**, soprattutto per allocazioni piccole. Il 90/10 perde appena 20 bps annuali sul full-sample. Il 50/50 perde 130 bps.
3. **Sui peggiori scenari decennali, l'oro protegge in modo significativo**: il p5 a 10Y passa da 1.18% (100E) a 6.43% (50/50). Ogni allocazione con oro batte il pure-equity nei worst case.
4. **A 20 anni le distribuzioni convergono fortemente**. Le mediane stanno tutte tra 8.88% e 9.95%. I p5 tra 6.13% e 6.89%. Su orizzonti molto lunghi la decisione ha impatto ridotto.
5. **A nessun orizzonte gli investitori scappano dai drawdown profondi**: a 20 anni il 100% delle finestre del pure-equity vede un MDD ≥ −20%, il 78.5% un MDD ≥ −30%. Anche il 50/50 al 99% e al 56%.

**Quindi: ha senso?**

Sì, **probabilmente sì**, e in modo più netto rispetto all'allocazione obbligazionaria. Le ragioni:

- La decorrelazione storica è robusta e stabile (a differenza di quella tra azioni e bond, che cambia con i regimi di tassi).
- Il costo in CAGR è basso, soprattutto per quote piccole-medie (≤ 25%).
- La protezione nei p5 è rilevante.
- L'oro si comporta diversamente dai bond in regimi di alta inflazione: nel 1976-1980 e nel 2022-2024, periodi in cui i bond hanno perso, l'oro ha tenuto o salito. È una copertura "ortogonale" a quella obbligazionaria.

**Quanto?**

I dati suggeriscono che il "punto dolce" è da qualche parte tra il 10% e il 25%:

- **10% (90/10)**: costo praticamente nullo (20 bps di CAGR full-sample), protezione moderata nei p5 a 10Y (alza p5 da 1.18% a 4.31%). È la soluzione "default" per chi vuole una pizzica di diversificazione senza pagare un costo di rendimento atteso visibile.
- **25% (75/25)**: costo modesto (~56 bps), protezione netta nei p5 a 10Y (porta il p5 a 6.19%, vicino al massimo strutturale). Il 75/25 è l'allocazione che storicamente ha massimizzato il rapporto protezione/costo opportunità su questo dataset.
- **50% (50/50)**: costo più alto (130 bps), protezione massima ma a un prezzo significativo. Ha senso solo se l'investitore è particolarmente avverso ai drawdown grossi e accetta di rinunciare a una quota di rendimento atteso.

**Per chi?**

A differenza dei bond — che hanno senso strutturale solo nelle fasi finali del piano (decumulo, sequence-of-returns risk) — **l'oro ha senso più trasversalmente, anche in fase di accumulo**. Una piccola allocazione (10-25%) può essere mantenuta per tutta la vita del portafoglio senza penalizzare significativamente il rendimento atteso, e protegge in modo efficace dai regimi macro che azioni e bond non gestiscono bene insieme (inflazione + crisi di fiducia istituzionale, come nel 1973-1980 e a tratti dal 2022).

## Confronto con il primo articolo: oro vs obbligazioni

Vale la pena un confronto rapido con la logica del [primo articolo del blog](/posts/ha-senso-obbligazioni-portafoglio), dove avevamo guardato lo stesso schema con bond invece di oro:

| Aspetto                                | Bond (60/40 vs 100E)        | Oro (50/50 vs 100E)          |
|----------------------------------------|------------------------------|------------------------------|
| Costo in CAGR mediano 10Y              | −2.4 punti percentuali       | −3.6 punti percentuali       |
| Costo in CAGR full-sample              | n.d. (periodo diverso)       | −1.3 punti percentuali       |
| Protezione p5 a 10Y                    | da 3.10% a 4.05% (+0.95)    | da 1.18% a 6.43% (+5.25)    |
| Correlazione con azioni                | +0.3 / −0.4 (regime-dipendente) | 0.0085 (stabile)         |
| Senso strutturale                      | Solo per decumulo            | Diversificazione trasversale |

L'oro è un diversificatore *più efficiente* dei bond in questo dataset: protegge di più nei p5 a 10Y, costa meno in CAGR full-sample, e la decorrelazione è più stabile rispetto ai regimi macro.

> **Caveat metodologico**: il confronto numerico tra i due articoli non è 1:1 perché i periodi sono diversi (l'articolo bond era 2001-2025, questo è 1976-2025). Quando si analizzerà la stessa finestra temporale con i tre asset insieme (azioni / bond / oro), in un articolo successivo, vedremo se la conclusione regge anche a parità di periodo.

## Takeaway

1. **L'oro è empiricamente un diversificatore vero**, non un diversificatore "marketing". La correlazione mensile con l'S&P 500 sui 50 anni è 0.0085 — un dato che vale più di qualunque argomento teorico.
2. **Una quota piccola-media di oro (10-25%) protegge i p5 a 10 anni** con costi di rendimento atteso ridotti. Il 90/10 alza il p5 di oltre 3 punti percentuali pagando solo 20 bps di CAGR.
3. **A 20 anni le distribuzioni convergono**: i quattro portafogli finiscono con CAGR mediani tra 8.88% e 9.95%, p5 tra 6.13% e 6.89%. Su orizzonti veramente lunghi la decisione ha impatto ridotto sul risultato finale, ma cambia molto il viaggio.
4. **A nessun orizzonte si scappa dai drawdown profondi**: a 20 anni praticamente tutti i portafogli (anche il 50/50) hanno visto un drawdown ≥ −20%. Il "non c'è rischio sul lungo" è un mito; il rischio cambia natura — diventa rischio di drawdown nel viaggio, non di chiusura in perdita.
5. **L'oro è un asset speculativo nel senso tecnico** (no flussi, no valore intrinseco calcolabile), ma questa critica filosofica non cancella il fatto empirico che la sua decorrelazione è reale e robusta.
6. **Differenza strutturale rispetto ai bond**: l'oro ha senso più trasversalmente, anche in accumulo. I bond hanno senso quasi solo nella fase di decumulo. Sono due strumenti di copertura diversi, contro rischi diversi (oro: inflazione + sfiducia; bond: deflazione + recessione).
7. Una piccola allocazione strutturale all'oro (10%) non è una scelta esotica o speculativa — i numeri suggeriscono che è una decisione metodologicamente sensata per quasi qualunque profilo retail.

---

### Fonti e riproducibilità

- Dati S&P 500 mensili (price + dividendo): [Shiller dataset](http://www.econ.yale.edu/~shiller/data.htm) — file `ie_data.xls`, mirror CSV su [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500).
- Dati LBMA Gold mensili (USD/oz): mirror CSV su [datasets/gold-prices](https://github.com/datasets/gold-prices). Nota: FRED ha dismesso le serie LBMA da gennaio 2022 in seguito alla revoca della licenza da parte di ICE Benchmark Administration.
- Codice della simulazione: [`scripts/ha-senso-oro-portafoglio.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/ha-senso-oro-portafoglio.py) nel repository del blog.
- Dati grezzi (rendimenti mensili dei quattro portafogli): [`/charts/ha-senso-oro-portafoglio/data.csv`](/charts/ha-senso-oro-portafoglio/data.csv).
- Summary numerico completo: [`/charts/ha-senso-oro-portafoglio/summary.json`](/charts/ha-senso-oro-portafoglio/summary.json).

> Nota: questa analisi è limitata al periodo 1976-2025 e all'universo USA in dollari. Una replica EUR-centric (con cambio EUR/USD modellato esplicitamente) e un confronto a tre vie (azioni / bond / oro sulla stessa finestra) saranno oggetto di articoli futuri.
