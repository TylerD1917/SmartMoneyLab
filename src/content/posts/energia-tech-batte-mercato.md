---
title: "Mix Nasdaq + Energia batte il mercato? Test su 26 anni di QQQ 70 / XLE 30"
description: "Una strategia trovata su X: 70% Nasdaq + 30% Energy USA, buy & hold. Test su 26 anni di dati daily contro l'S&P 500 con il framework SmartMoneyLab a 6+1 metriche. Verdict, scorecard, trade-off."
pubDate: 2026-05-05
tags: ["strategie", "nasdaq", "energy", "qqq", "xle", "rolling-windows", "backtest", "diversificazione"]
author: "SmartMoneyLab"
simulationSlug: "energia-tech-batte-mercato"
series: "battere-il-mercato"
seriesOrder: 1
verdict: "parziale"
draft: false
---

## In breve

Su 26 anni di dati daily (marzo 1999 – dicembre 2025) ho testato una strategia trovata in un thread X: **70% Nasdaq (QQQ) + 30% Energy USA (XLE)**, buy & hold senza rebalancing, contro il classico **S&P 500 (SPY)** come "il mercato". L'idea macro è la decorrelazione strutturale tra tech e energy: in regimi inflazionistici il tech soffre e l'energy esplode; in regimi disinflazionistici è il contrario. Mixarli a 70/30 dovrebbe — secondo la tesi — produrre un portafoglio con upside del Nasdaq e cuscinetto in caso di shock energetici.

Applicando il **framework SmartMoneyLab a 6+1 metriche** che inauguriamo qui (CAGR mediano, win rate, volatilità, max drawdown, Sharpe, Calmar, Sortino), il verdetto è **PARZIALE: 4/7 criteri soddisfatti** sia su finestre 5Y che 10Y. La strategia *batte* il mercato in alcune dimensioni, *non lo batte* in altre — esattamente il tipo di trade-off che vale la pena raccontare.

I tre risultati centrali:

1. **A 10 anni la strategia vince in CAGR mediano** in modo netto: 11.53% contro 8.24% del benchmark (+3.29 punti percentuali all'anno). Ma **a 5 anni il vantaggio scompare**: 10.03% vs 10.56% (−0.5pp).
2. **Il decoupling tech/energy ha funzionato — ma solo parzialmente**. L'aggiunta del 30% di XLE riduce il drawdown massimo da −83% del 100% Nasdaq a −72% della 70/30: differenza enorme. Ma resta lontano dal −55% del semplice SPY.
3. **La strategia paga sempre +27% di volatilità** rispetto al benchmark (24.5% vs 19.3% annualizzata). Lo Sharpe ratio batte di pochissimo (0.423 vs 0.408), il Calmar perde (0.14 vs 0.15) per via del drawdown profondo. Sortino batte ma marginalmente.

Detto in modo netto: la strategia **non è "miracolosa"**, ma **nemmeno è una bocciatura totale**. È un caso da manuale di trade-off con vincitori e vinti su dimensioni diverse — proprio quello che il framework esiste per identificare.

## La strategia "wow" trovata su X

L'idea originale arriva da un post di X (autore non rintracciabile, ma il pattern è ricorrente nel FinTwit americano): **investire al 70% in QQQ (Invesco Nasdaq-100 Trust) e al 30% in XLE (Energy Select Sector SPDR Fund)**, buy & hold puro, senza rebalancing, e tenere per anni.

Il razionale macro è elegante:

- In **regimi inflazionistici**, il settore growth/tech è stato storicamente penalizzato dall'innalzamento dei tassi reali (i flussi di cassa lontani nel tempo si scontano di più), mentre il settore energetico ha beneficiato dell'aumento dei prezzi delle materie prime.
- In **regimi disinflazionistici**, il pattern si rovescia: tassi bassi sostengono i multipli del growth, mentre l'energy resta compresso dal calo dei prezzi del petrolio.
- Mixando i due, in teoria, si ottiene un portafoglio con **bassa correlazione interna** tra le due gambe, e quindi un profilo di rischio/rendimento migliore rispetto a un puro Nasdaq.

Sembra logico. È testabile. E proprio per questo è perfetto come *primo articolo della serie* "Strategie per battere il mercato?": dobbiamo verificare se la logica regge sui dati o se è un narrative che funziona meglio in spiegazione che nei numeri.

## Il framework "battere il mercato?" — 6+1 metriche

Visto che è il primo articolo della serie, fisso il framework di valutazione che useremo da qui in avanti per tutte le strategie. Non basta avere "rendimenti più alti" per dire che una strategia batte il mercato: bisogna guardare anche al rischio sopportato e all'efficienza con cui quel rendimento è stato prodotto.

Una strategia **batte il mercato** su un orizzonte H se, su tutte le finestre rolling di durata H (con step 6 mesi) sul periodo storico disponibile, soddisfa **tutti e sette** questi criteri:

| # | Criterio | Definizione | Cosa misura |
|---|---|---|---|
| 1 | **CAGR mediano** | Mediana CAGR rolling ≥ benchmark | Rendimento centrale |
| 2 | **Win rate** | % finestre rolling vincenti vs benchmark ≥ 60% | Frequenza di vittoria |
| 3 | **Volatilità** | Vol annualizzata ≤ benchmark × 1.10 | Rischio totale |
| 4 | **Max Drawdown** | \|MDD mediano\| ≤ \|benchmark\| × 1.10 | Profondità delle cadute |
| 5 | **Sharpe** | Sharpe ≥ benchmark | Efficienza vs volatilità totale |
| 6 | **Calmar** | CAGR / \|MDD\| ≥ benchmark | Efficienza vs drawdown peggiore |
| 7 | **Sortino** | Sortino ≥ benchmark | Efficienza vs solo volatilità "cattiva" |

Le tolleranze del 10% in volatilità e MDD sono pensate per non bocciare strategie che producono rendimento simile al benchmark con rischio leggermente diverso — una strategia che ti dà 100 bps di CAGR in più ma a costo del 30% in più di vol non sta "battendo il mercato", sta semplicemente prendendo più rischio.

In base a quanti criteri passano, classifichiamo il verdetto:

- **Vince** → tutti e 7 soddisfatti. È la barra alta, e quasi nessuna strategia *davvero* la passa nei dati.
- **Parziale** → 4-6 su 7. La strategia ha vincitori e vinti su dimensioni diverse: l'articolo discute il trade-off.
- **Non vince** → ≤3 su 7. La strategia ha un caso d'uso ridotto o nullo rispetto al semplice benchmark.

Per Sharpe, Calmar e Sortino il risk-free rate è fissato al 2% annuo costante (proxy storica del T-bill 3M sul lungo periodo).

## Il metodo

- **Periodo**: 10 marzo 1999 → 30 dicembre 2025 (~26.7 anni, 6.745 giorni di trading). Il vincolo è il lancio di QQQ (lancio originale: 10/03/1999).
- **Asset**: SPY (SPDR S&P 500 ETF), QQQ (Invesco Nasdaq-100), XLE (Energy Select Sector SPDR), tutti scaricati via yfinance con `auto_adjust=True` — i prezzi `Close` riflettono già dividendi reinvestiti e split, quindi sono di fatto Total Return.
- **Portafogli testati**: 4 in tutto, tutti buy & hold puro:
  - **SPY 100%** — il benchmark, "il mercato"
  - **QQQ 70 / XLE 30** — la strategia da testare
  - **QQQ 50 / XLE 50** — variante più aggressiva sull'energy (per controllare se più XLE migliora il quadro)
  - **QQQ 100%** — confronto puro Nasdaq (per isolare l'effetto specifico dell'aggiunta di XLE)
- **No rebalancing** in nessuno dei portafogli. È coerente col framework SmartMoneyLab già stabilito negli articoli precedenti, e con la richiesta della tesi originale (buy & hold).
- **Rolling**: 5Y (60 mesi) e 10Y (120 mesi), step 6 mesi. 44 finestre 5Y e 34 finestre 10Y.

Lo script Python che produce tutto è in [`scripts/energia-tech-batte-mercato.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/energia-tech-batte-mercato.py).

## Risultati full-sample: i 26 anni in tabella

Tutte le metriche di rischio/rendimento sui 26.7 anni di dataset:

| Portafoglio          | CAGR    | Volatilità | Max DD    | Sharpe | Sortino | Calmar |
|----------------------|---------|------------|-----------|--------|---------|--------|
| **SPY 100%**         | 8.34%   | 19.34%     | −55.19%   | 0.408  | 0.575   | 0.151  |
| **QQQ 70 / XLE 30**  | **9.83%** | 24.55%   | −72.34%   | 0.423  | 0.597   | 0.136  |
| QQQ 50 / XLE 50      | 9.34%   | 24.40%     | −62.97%   | 0.407  | 0.569   | 0.148  |
| QQQ 100%             | 10.47%  | 27.05%     | **−82.96%** | 0.429 | 0.615   | 0.126  |

Cinque cose vanno notate prima di passare alla scorecard:

- **La strategia 70/30 ha CAGR superiore al benchmark di 1.49 punti percentuali all'anno** (9.83% vs 8.34%). Su 26 anni capitalizzati, $1 → $12.32 con la strategia vs $8.42 con SPY. Differenza significativa.
- **Ma paga +27% di volatilità annualizzata** (24.55% vs 19.34%). Il rischio totale non è "comparabile" al benchmark: è strutturalmente più alto.
- **Il drawdown massimo full-sample è −72%** vs −55% del benchmark. Significa che chi ha tenuto la strategia attraverso il dot-com bottom 2002 ha visto il NAV scendere a meno di un terzo del valore iniziale. Stratosfericamente diverso da SPY.
- **Il decoupling tech/energy ha effettivamente funzionato — ma solo rispetto al 100% Nasdaq**: la 70/30 ha drawdown −72% contro −83% del puro Nasdaq, cioè 11 punti percentuali di "scudo" tramite l'aggiunta XLE. Quindi la tesi macro non è falsa, ma il punto di partenza (Nasdaq puro) è troppo penalizzato per essere battuto da un benchmark conservativo come SPY.
- **La 50/50 perde su quasi tutto rispetto alla 70/30**: stessa volatilità, drawdown meno profondo (−63%) ma CAGR inferiore. Il "punto dolce" del mix tech/energy nei dati 1999-2025 sta sopra al 50% di tech, non sotto.

## Risultati su rolling 10 anni: il caso più favorevole alla strategia

A 10 anni la strategia ha lo scenario più favorevole. Su 34 finestre rolling con step 6 mesi:

<figure>
  <img src="/charts/energia-tech-batte-mercato/02_cagr_10y.png" alt="Boxplot del CAGR su finestre rolling 10 anni per i 4 portafogli (SPY 100%, QQQ 70 / XLE 30, QQQ 50 / XLE 50, QQQ 100%)." />
  <figcaption>Distribuzione del CAGR rolling 10Y per i 4 portafogli, step 6 mesi.</figcaption>
</figure>

| Portafoglio          | CAGR p5 | CAGR p25 | **CAGR mediano** | CAGR p75 | CAGR p95 |
|----------------------|---------|----------|-------------------|----------|----------|
| SPY 100%             | −1.29%  | 6.87%    | **8.24%**         | 12.87%   | 15.40%   |
| **QQQ 70 / XLE 30**  | −0.94%  | 7.92%    | **11.53%**        | 12.92%   | 14.86%   |
| QQQ 50 / XLE 50      | 1.93%   | 6.57%    | **9.19%**         | 10.50%   | 13.73%   |
| QQQ 100%             | −6.58%  | 10.20%   | **12.61%**        | 18.08%   | 21.91%   |

Tre osservazioni:

- **La strategia 70/30 ha CAGR mediano 10Y di 11.53% — sopra al benchmark di 3.29 punti percentuali**. È un vantaggio sostanziale sul lungo periodo. ✓ Primo criterio soddisfatto.
- **Il p5 della 70/30 (−0.94%) è simile al p5 del benchmark (−1.29%) e drammaticamente migliore del p5 del 100% Nasdaq (−6.58%)**. Cioè nelle finestre 10Y peggiori, l'aggiunta del 30% di XLE evita gli "lost decade" che il puro Nasdaq ha vissuto (quello che inizia al 2000 chiudeva a −6.58% annualizzato dopo 10 anni).
- **Win rate vs benchmark**: 55.88% (sotto la soglia 60%). ❌ Quindi nella maggioranza assoluta delle finestre 10Y la strategia ha battuto SPY, ma non con la frequenza che il framework richiede per chiamarla "vittoria". 19 finestre vinte su 34, 15 perse.

## Risultati su rolling 5 anni: il caso più sfavorevole

A 5 anni la storia è meno benevola:

<figure>
  <img src="/charts/energia-tech-batte-mercato/03_cagr_5y.png" alt="Boxplot del CAGR su finestre rolling 5 anni per i 4 portafogli." />
  <figcaption>Distribuzione del CAGR rolling 5Y per i 4 portafogli, step 6 mesi.</figcaption>
</figure>

| Portafoglio          | CAGR p5 | CAGR p25 | **CAGR mediano** | CAGR p75 | CAGR p95 |
|----------------------|---------|----------|-------------------|----------|----------|
| SPY 100%             | −2.17%  | 2.07%    | **10.56%**        | 14.63%   | 17.12%   |
| **QQQ 70 / XLE 30**  | −4.84%  | 5.58%    | **10.03%**        | 16.28%   | 21.29%   |
| QQQ 50 / XLE 50      | −1.45%  | 3.89%    | **8.37%**         | 13.51%   | 22.16%   |
| QQQ 100%             | −10.16% | 6.18%    | **14.48%**        | 19.98%   | 25.37%   |

Punti rilevanti:

- **A 5 anni la 70/30 perde di poco sul CAGR mediano**: 10.03% vs 10.56% (−0.5pp). ❌ Secondo criterio fallito su questo orizzonte.
- **Win rate vs benchmark**: 65.91% (29 vittorie su 44 finestre). ✓ Soglia superata.
- **Il p5 della 70/30 (−4.84%) è peggiore del p5 di SPY (−2.17%)**: nei peggiori 5y la strategia ha perso più del benchmark. Coerente con il fatto che porta più volatilità e drawdown più profondi.
- Il p95 della 70/30 (21.29%) è più alto del p95 di SPY (17.12%): nei migliori 5y, la strategia ha vinto largo. Quindi è una distribuzione *più larga* del benchmark — è proprio la caratteristica che il criterio "Volatilità" cattura, e che è il suo punto debole.

## Sharpe, Sortino e Calmar: l'efficienza relativa

<figure>
  <img src="/charts/energia-tech-batte-mercato/04_sharpe_10y.png" alt="Boxplot dello Sharpe ratio su finestre rolling 10 anni per i 4 portafogli." />
  <figcaption>Distribuzione dello Sharpe ratio rolling 10Y per i 4 portafogli.</figcaption>
</figure>

Sui valori full-sample:

- **Sharpe**: 0.423 vs 0.408. ✓ La strategia produce *quantitativamente* poco più rendimento per unità di volatilità totale del benchmark. Il vantaggio è marginale (≈4% di gap), ma esiste.
- **Sortino**: 0.597 vs 0.575. ✓ Stessa storia col downside-only — la strategia è marginalmente più "buona" della SPY anche guardando solo le perdite.
- **Calmar**: 0.136 vs 0.151. ❌ Qui si rompe il quadro: il drawdown peggiore della strategia è così profondo (−72%) da peggiorare il rapporto CAGR/|MDD| rispetto al benchmark, nonostante il CAGR sia più alto. È la metrica che disinnesca il "ma vince in CAGR" più chiaramente.

In altre parole, **la strategia produce poco più rendimento per unità di volatilità ma molto meno rendimento per unità di drawdown peggiore**. Le due metriche di efficienza danno verdetti opposti perché misurano cose diverse: Sharpe pesa la volatilità totale (incluse le oscillazioni che recuperano), Calmar pesa solo il "punto peggiore mai raggiunto". Una strategia che ha pochi crash devastanti ma molte oscillazioni minori vince Sharpe e perde Calmar — è esattamente il caso 70/30.

## La scorecard finale

<figure>
  <img src="/charts/energia-tech-batte-mercato/05_scorecard.png" alt="Scorecard del framework 'battere il mercato' per la strategia QQQ 70 / XLE 30 vs SPY 100%, su finestre rolling 5Y e 10Y, con i 7 criteri valutati come ✓ o ✗." />
  <figcaption>Scorecard finale della strategia QQQ 70 / XLE 30 vs SPY 100%. 4/7 criteri soddisfatti su entrambi gli orizzonti — verdetto PARZIALE.</figcaption>
</figure>

Riassumendo nelle due colonne 5Y / 10Y:

| Criterio | 5Y | 10Y | Note |
|---|---|---|---|
| CAGR mediano | ❌ 10.03% < 10.56% | ✓ 11.53% > 8.24% | Vince a 10Y, perde a 5Y |
| Win rate ≥ 60% | ✓ 65.9% | ❌ 55.9% | Più vittorie a 5Y nonostante CAGR mediano leggermente inferiore |
| Volatilità ≤ 1.10× | ❌ 24.5% > 21.3% | ❌ idem | Strutturalmente più volatile, +27% in entrambi gli orizzonti |
| Max DD ≤ 1.10× | ✓ −34% vs −34% | ✓ −53% vs −53% | MDD mediano rolling sostanzialmente in linea |
| Sharpe | ✓ 0.42 > 0.41 | ✓ idem | Vincita marginale |
| Calmar | ❌ 0.14 < 0.15 | ❌ idem | Il drawdown peggiore costa caro |
| Sortino | ✓ 0.60 > 0.58 | ✓ idem | Vincita marginale |
| **Totale** | **4/7** | **4/7** | **Parziale, parziale** |

**Verdetto aggregato: PARZIALE**. La strategia non è bocciata, ma neanche promossa. Soddisfa metà più una delle metriche.

## Cosa significa, in pratica

Il fatto che la strategia perda esattamente in **volatilità + Calmar** (e parzialmente in CAGR mediano e win rate a seconda dell'orizzonte) racconta una storia coerente: **la 70/30 ti dà più rendimento atteso, ma con un viaggio molto più volatile e con drawdown peggiori**. Non è "battere il mercato": è *prendere più rischio per più rendimento*, in proporzione che è *circa* coerente — Sharpe e Sortino sono solo marginalmente migliori, non drammaticamente.

Detto in altro modo: chi ha tenuto la 70/30 dal 1999 ha portato a casa $12.32 per ogni dollaro investito, contro gli $8.42 di SPY. **Sono $3.90 in più ogni dollaro**. Ma per arrivarci ha dovuto sopportare:
- Un drawdown peggiore di 17 punti percentuali rispetto a SPY (−72% vs −55%): in un solo punto della storia, il portafoglio era ridotto a circa un quarto del massimo precedente.
- Una volatilità annualizzata del 24.5% vs 19.3%: oscillazioni molto più ampie giorno per giorno, settimana per settimana.

Per molti investitori reali, non è un trade-off accettabile. Il rischio di "uscire al peggio" durante un drawdown del −72% è molto reale: nessun retail medio tiene un portafoglio attraverso un crollo simile senza vendere.

## Per chi può avere senso?

In coerenza con i nostri framework precedenti del blog (vedi articolo sulla [leva ETF 2x/3x](/posts/leva-raddoppia-rendimento-mercato)), la strategia 70/30 QQQ-XLE ha senso solo per:

1. **Investitore con orizzonte ≥10 anni**, perché lì il vantaggio in CAGR mediano si manifesta (+3.29pp). Su orizzonti più corti il trade-off è meno favorevole.
2. **Capacità psicologica di tenere attraverso un −70%**. Senza questa, la strategia *teoricamente* batte ma *praticamente* viene venduta al peggio.
3. **Asset allocation di una porzione del portafoglio, non del totale**. Una possibile lettura sensata: tenere il 70-80% del portafoglio in qualcosa di più diversificato (MSCI World), e usare la 70/30 QQQ-XLE come "tilt aggressivo" sul 20-30% restante. Questo limita l'impatto del −72% a livello di portafoglio totale.
4. **Conviction sulla logica macro**. La tesi originale è che il mix funzioni *per via della decorrelazione tech/energy in regimi macro diversi*. Se non sei convinto del razionale, sei una cosa sola con un investitore che alloca il 30% del portafoglio in un settore poco diversificato (l'energy USA è un settore — non un asset class) per ragioni che non capisce. Brutta posizione.

Per **chi è in fase di accumulo e cerca semplicità**, MSCI World resta la scelta più solida — non vince questa scorecard, ma non perde mai catastroficamente.

## Takeaway

1. **La strategia QQQ 70 / XLE 30 ha verdetto PARZIALE**: 4/7 criteri soddisfatti su entrambi gli orizzonti 5Y e 10Y.
2. **Vince in CAGR mediano a 10Y (+3.29pp/anno)** ma perde a 5Y (−0.5pp). Il vantaggio di rendimento è specifico al lungo periodo.
3. **Vince marginalmente in Sharpe e Sortino** (~3-4% di gap), ma perde nettamente in **Calmar** per via del drawdown peggiore (−72% vs −55%).
4. **La logica macro tech/energy ha funzionato — ma solo rispetto al 100% Nasdaq**: la 70/30 dimezza il drawdown del puro Nasdaq, ma non basta a battere SPY. La diversificazione c'è, ma non è sufficiente a compensare il maggior rischio strutturale.
5. **Il vincolo principale è la volatilità**: 24.5% vs 19.3% del benchmark, +27% in entrambi gli orizzonti. Senza tolleranza per quella oscillazione, la strategia non è una scelta sensata.
6. **Il framework "Battere il mercato?" funziona come pensato**: classifica strategie con vincitori e vinti su dimensioni diverse, evita di chiamare "vittoria" un più alto CAGR pagato con rischio molto più elevato.

L'idea seducente che "mixare due settori decorrelati produce un portafoglio strutturalmente migliore del benchmark" si rivela *parzialmente vera*: la decorrelazione c'è e genera valore, ma non abbastanza per superare un benchmark veramente diversificato come l'S&P 500. È un risultato che probabilmente i fan FinTwit della strategia non si aspettano, ma è quello che dicono i numeri.

Nel prossimo articolo della serie testeremo un'altra strategia — proposta da un lettore o trovata online — col solito framework. Stay tuned.

---

### Fonti e riproducibilità

- Prezzi daily ETF (SPY, QQQ, XLE): [Yahoo Finance](https://finance.yahoo.com/) via libreria `yfinance`, con `auto_adjust=True` per riflettere dividendi reinvestiti e split (Total Return).
- Periodo: 10 marzo 1999 → 30 dicembre 2025 (limite imposto dal lancio di QQQ).
- Risk-free rate per Sharpe/Sortino: 2% annuo costante (proxy storica T-bill 3M).
- Codice della simulazione: [`scripts/energia-tech-batte-mercato.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/energia-tech-batte-mercato.py).
- Summary numerico completo: [`/charts/energia-tech-batte-mercato/summary.json`](/charts/energia-tech-batte-mercato/summary.json).
- Letteratura accademica di riferimento sulla decorrelazione settoriale: Asness, C., Frazzini, A., & Pedersen, L. (2019), *"Quality minus Junk"*; Erb, C. & Harvey, C. (2006), *"The strategic and tactical value of commodity futures"*, Financial Analysts Journal.

> Nota: la strategia originale era stata proposta su X — l'autore non è rintracciabile nei thread che ho potuto consultare, quindi non posso citarlo. Se sei l'autore o conosci la fonte, fammelo sapere così ti accredito esplicitamente nell'articolo.

> Hai un'idea per una strategia da testare? Mandamela: se i dati sono accessibili e l'idea è ben articolata, finisce in un articolo della serie con citazione esplicita.
