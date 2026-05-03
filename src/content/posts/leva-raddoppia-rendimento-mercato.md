---
title: "La leva 2x raddoppia il rendimento del mercato? La 3x lo triplica?"
description: "Tre portafogli buy & hold sull'S&P 500 con leva 1x, 2x e 3x daily, su 50 anni di dati. Il volatility drag, i costi reali calibrati su un ETF vero (ProShares SSO), e il prezzo che paghi per voler 'amplificare' il mercato."
pubDate: 2026-05-01
tags: ["leva", "etf", "volatility-drag", "rolling-windows", "backtest", "sp500"]
author: "SmartMoneyLab"
simulationSlug: "leva-raddoppia-rendimento-mercato"
draft: false
---

## In breve

Confronto tra tre portafogli buy & hold sull'S&P 500 — leva 1x, 2x daily-rebalanced, 3x daily-rebalanced — su 50 anni di dati daily (gennaio 1976 – dicembre 2025). Il drag dei costi reali è stato **calibrato empiricamente** dai prezzi giornalieri del **ProShares Ultra S&P 500 (SSO)**, l'ETF a leva 2x più antico disponibile (lancio 2006, oltre 17 anni di storia). Risultati in breve:

1. **Il "moltiplicatore" della leva non funziona linearmente**, mai. Su 50 anni la 1x ha dato CAGR 11.78%. Una "2x lineare ideale" produrrebbe 23.56%. La 2x daily-rebalanced reale produce **18.32%**. La 3x ne produrrebbe 35.34% lineari, ne produce **21.70%** reali. Il moltiplicatore implicito non è 2x né 3x — è circa 1.55x e 1.84x.
2. **Cumulata su 50 anni l'erosione è devastante**. 1$ investito a inizio 1976 diventa $222 con la 1x, $3.873 con la 2x, **$14.943 con la 3x** (versione realistica con costi reali UCITS). Il "miracolo lordo" della 3x sarebbe stato $167.810 — ma il **91% si dissolve in volatility drag e costi**. La 2x perde il **73%** del valore "lordo".
3. **A 20 anni la 3x non offre nessun vantaggio sulla 2x** (CAGR mediano realistico: 13.87% vs 13.82%, identici). E il 5° percentile della 3x a 20Y (2.44%) è **inferiore** a quello della 1x (6.24%): nelle peggiori finestre ventennali la 3x perde anche contro chi non ha leva affatto.

A questo si aggiunge il dato visivo più drammatico: **nel 100% delle finestre 20Y la 3x ha visto un drawdown ≥ −75%**. Non l'80%, non il 95% — il 100%. È il prezzo strutturale di moltiplicare la volatilità per 3.

## La domanda

Sembra ovvia, e per molti retail italiani lo è: *se la leva 2x raddoppia ogni giorno il movimento del mercato, su un anno positivo per l'S&P 500 dovrei guadagnare più o meno il doppio. Su 10 anni di bull market mi aspetto un rendimento composto vicino a 2× quello del mercato. Giusto?*

Sbagliato. E lo è in modo non banale, perché le ragioni del fallimento di questa intuizione sono **due distinte**:

1. Una matematica, intrinseca al meccanismo del rebalancing daily della leva — il famoso **volatility drag**.
2. Una operativa, dovuta al fatto che gli ETF a leva veri pagano TER e costi di funding del prestito implicito — il **drag dei costi**.

Le testiamo entrambe sui dati storici dell'S&P 500 dal 1976 al 2025, costruendo due scenari paralleli (uno "lordo" matematicamente puro, uno "realistico" calibrato su un ETF reale), e vediamo *quanto* del rendimento "atteso" sopravvive lungo il percorso.

## Il volatility drag in 30 secondi

Considera un mercato che oscilla. Giorno 1 fa −10%, giorno 2 fa +10%. Cosa succede al sottostante e al suo "fratello a leva 2x"?

**Sottostante 1x**: parte da 100 → giorno 1: 100 × 0.90 = 90 → giorno 2: 90 × 1.10 = 99. Ha perso 1%.

**ETF 2x daily-rebalanced**: parte da 100 → giorno 1: 100 × (1 − 2×0.10) = 80 → giorno 2: 80 × (1 + 2×0.10) = 96. Ha perso 4%.

L'1x ha perso 1%, il "2x lineare" ne perderebbe 2%. Ma il 2x daily ne perde **4**. È il quadruplo del lineare, su due soli giorni. Su 252 giorni di trading all'anno, l'effetto si accumula in modo non trascurabile.

Formalmente, il drag annualizzato del rebalancing daily si approssima con:

> drag ≈ ½ · L · (L − 1) · σ²

dove L è la leva e σ è la volatilità annualizzata del sottostante. Con la volatilità storica dell'S&P 500 (~17.4% sui 50 anni del nostro dataset):

- **Drag teorico 2x**: ½ · 2 · 1 · 0.174² ≈ **3.0%/anno**
- **Drag teorico 3x**: ½ · 3 · 2 · 0.174² ≈ **9.1%/anno**

Cioè anche **senza nessun costo**, semplicemente per come funziona la leva daily, il "2× lineare" perde 3 punti percentuali all'anno. Il "3× lineare" ne perde 9. Su decenni, capitalizzato, è enorme.

E questo è il *minimo* matematico. La realtà degli ETF pagamenti reali aggiunge altri costi sopra.

## Il metodo

Il setup ricalca i tre articoli precedenti del blog, con le particolarità del caso "leva":

- **Periodo**: gennaio 1976 – dicembre 2025 (50 anni, ~12.600 giorni di trading).
- **Asset sottostante**: S&P 500 *Total Return* (con dividendi reinvestiti). Daily price index dal Yahoo Finance, dividendi mensili dal dataset Shiller, distribuiti uniformemente sui 252 giorni di trading dell'anno.
- **Leve sintetiche**: niente uso di ETF reali sul backtest, costruisco le serie giornaliere di una "1x daily", "2x daily" e "3x daily" applicando ogni giorno `r_lev_t = L × r_t (− daily_drag, nello scenario realistico)`.
- **Buy & hold puro**, niente rebalancing dell'allocazione (perché l'allocazione è 100% S&P comunque per tutte e tre le leve — quello che si rebalancia è la *posizione a leva*, daily).
- **Rolling windows**: 5 anni, 10 anni e 20 anni, step 3 mesi.

### I due scenari: Lordo e Realistico

Costruisco **due famiglie parallele** di NAV per ciascuna leva:

- **Lordo**: applica esattamente `L × r_daily`. Niente TER, niente funding cost. È il "mondo ideale" di chi pensa che gli ETF a leva siano semplicemente "leva matematica".
- **Realistico**: applica `L × r_daily − drag_daily`, dove `drag_daily` è calibrato sui costi reali di un ETF a leva esistente (vedi sotto). Riflette ciò che un investitore retail italiano *effettivamente* incontrerebbe comprando un ETF UCITS a leva sul S&P 500.

I rendimenti che guidano l'articolo da qui in poi sono **quelli realistici** — l'unica cosa che il lettore può davvero osservare nella pratica.

### La calibrazione: ProShares SSO come ground truth

Per stimare il drag reale di un ETF a leva 2x, uso il prezzo giornaliero del **ProShares Ultra S&P 500 (SSO)**, l'ETF a leva 2x più antico disponibile (lancio 21 giugno 2006, oltre 17 anni di storia). SSO è in USD, listato negli USA: niente effetto cambio rispetto al sottostante, calibrazione pulita.

Confronto SSO reale vs una "2x sintetica matematicamente pura" calcolata sui daily SPY (1x ETF) sullo stesso periodo:

| Metrica                        | Valore                |
|--------------------------------|-----------------------|
| Periodo di calibrazione        | 21/06/2006 – 29/12/2023 (17.5 anni) |
| Crescita 2x sintetica (matematica) | 14.14× → CAGR **+16.31%** |
| Crescita SSO reale (2x)        | 8.74× → CAGR **+13.17%**  |
| **Drag totale empirico (2x)**  | **~2.74%/anno** (log-space) |

Decompongo questo drag totale nelle sue due componenti:

- **TER ProShares SSO**: 0.89%/anno (è il TER ufficiale dichiarato dal fondo)
- **Funding cost residuo**: 2.74% − 0.89% = **~1.85%/anno**

Il *funding cost* è il costo di "prendere a prestito" 1× del NAV per produrre la leva 2x (la 2x equivale a 1× capitale proprio + 1× preso a prestito). Sui 17 anni di SSO, in media questo costo è stato ~1.85%/anno, simile al risk-free rate medio del periodo + uno spread di intermediazione modesto.

Ora applico questo *funding cost empirico* agli ETF UCITS che il retail italiano effettivamente compra:

| ETF di riferimento (UCITS)             | Leva | TER     | Drag totale stimato        |
|----------------------------------------|------|---------|----------------------------|
| WisdomTree S&P 500                     | 1x   | 0.05%   | **0.05%/anno**             |
| Xtrackers S&P 500 2x Leveraged Daily Swap | 2x   | 0.60%   | 0.60% + 1.85% = **2.45%/anno** |
| WisdomTree S&P 500 3x Daily Leveraged  | 3x   | 0.75%   | 0.75% + 2 × 1.85% = **4.45%/anno** |

La 3x prende a prestito 2× il NAV (vs 1× della 2x), quindi il funding cost si moltiplica per 2. Questi sono i numeri che applico alle simulazioni "realistiche" sui 50 anni.

> **Caveat onesto**: il funding cost non è costante nel tempo — segue i tassi di mercato. Negli anni '80 era probabilmente più alto, nel 2010-2020 più basso, dal 2022 in su di nuovo medio-alto. Modellarlo time-varying renderebbe l'analisi più complessa e i risultati lievemente diversi nei singoli decenni, ma il messaggio strutturale sui 50 anni rimane lo stesso. Il dato del 1.85% medio storico calibrato su SSO è una proxy ragionevole per un investitore di lungo periodo.

## Risultati full-sample: il "miracolo" della leva eroso

Su 50 anni di S&P 500 (1976-2025), simulazione realistica con i drag calibrati:

| Leva | CAGR Lordo | CAGR Realistico | $1 finale Lordo | $1 finale Realistico | Volatilità annualizzata | Max drawdown periodo |
|------|------------|-----------------|------------------|----------------------|--------------------------|----------------------|
| 1x   | 11.84%     | **11.78%**      | $228             | **$222**             | 17.4%                    | −55.3%               |
| 2x   | 21.26%     | **18.32%**      | $14.490          | **$3.873**           | 34.8%                    | −86.1%               |
| 3x   | 27.24%     | **21.70%**      | $167.810         | **$14.943**          | 52.2%                    | −97.5%               |

Tre cose vanno notate:

**1. Il moltiplicatore implicito non è 2 né 3.** Calcolato sul CAGR realistico full-sample:
- 2x effettivo: 18.32% / 11.78% = **1.55× moltiplicatore implicito** (vs nominale 2)
- 3x effettivo: 21.70% / 11.78% = **1.84× moltiplicatore implicito** (vs nominale 3)

Cioè la 3x è meno "leva" della 2x rispetto al loro nominal: il drag della 3x mangia in proporzione più rendimento.

**2. L'erosione cumulata sul capitale finale è enorme.** Confronto $1 → finale, lordo vs realistico:
- 1x: −3% (impatto del solo TER 0.05%)
- 2x: **−73%** (da $14.490 a $3.873)
- 3x: **−91%** (da $167.810 a $14.943)

Il "miracolo" che molti retail immaginano guardando il rendimento di TQQQ negli ultimi 10 anni è in larga parte un artefatto di un decennio insolitamente favorevole alla leva (basso tasso di interesse + bull market lineare con bassa volatilità). Esteso a 50 anni e calibrato sui costi reali, il vantaggio della 3x sulla 1x rimane (~67× il capitale finale, in valore assoluto), ma è frutto di:

- 50 anni di tempo di compounding
- Volatilità del 52% annualizzata
- Drawdown del 97% durante la GFC
- Comportamento da rivedere ogni 10 anni perché — come vedremo nelle rolling — i p5 a 20Y sono *inferiori* a quelli della 1x

**3. Il drawdown è il prezzo strutturale.** Il MDD full-sample della 3x realistic è −97.5% — cioè in qualche momento del periodo 1976-2025 il NAV è sceso a circa $0.025 sul dollaro investito iniziale. Ci ha messo ~15 anni di bull market post-2009 per ricostruirsi, e il dataset arriva al 2025. Se il dataset finisse al 2010, la 3x non sarebbe ancora tornata in pari rispetto al 1976.

## Risultati su finestre rolling 10 anni

Per non basarsi su un singolo punto di partenza, ricalcolo la simulazione su tutte le finestre 10Y disponibili (161 finestre, step 3 mesi):

<figure>
  <img src="/charts/leva-raddoppia-rendimento-mercato/07_boxplot_cagr_10y_realistic.png" alt="Boxplot del CAGR su finestre rolling 10 anni per le tre leve (1x, 2x, 3x), scenario realistico con drag UCITS calibrato su SSO ProShares." />
  <figcaption>Distribuzione del CAGR su finestre 10 anni, step 3 mesi, scenario realistico (con drag dei costi reali UCITS). La dispersione cresce drammaticamente con la leva.</figcaption>
</figure>

Numeri esatti, scenario realistico:

| Leva | p5     | p25   | **Mediana** | p75    | p95    | % finestre con CAGR < 0 |
|------|--------|-------|-------------|--------|--------|--------------------------|
| 1x   | +1.64% | 7.98% | **12.84%**  | 14.92% | 17.98% | 4.97%                    |
| 2x   | −3.82% | 9.16% | **20.87%**  | 25.50% | 32.95% | 8.70%                    |
| 3x   | **−12.95%** | 6.25% | **26.03%** | 33.79% | 47.60% | **11.18%**               |

Lettura del dato:

- **Sui valori mediani la leva paga**: la 2x mediana fa 20.87% (vs 12.84% della 1x), la 3x fa 26.03%. Sembra molto bene. Ma la mediana è solo la metà della distribuzione, e l'altra metà è dove la storia si fa interessante.
- **Sulle code negative la leva PERDE molto**: il p5 del 100% azionario è +1.64%. Il p5 del 2x scende a **−3.82%** (perdi terreno annualizzato in una finestra 10Y peggiore). Il p5 del 3x crolla a **−12.95%** — cioè in 8 finestre 10Y su 161 (il 5%) la 3x ha portato a casa CAGR di −13% all'anno, che capitalizzato 10 anni = NAV finale a circa il 25% del capitale iniziale.
- **% di finestre 10Y con CAGR negativo**: 4.97% per 1x, 8.70% per 2x, 11.18% per 3x. La 3x chiude in perdita più del doppio del 1x.

E sui drawdown il quadro è ancora più drammatico:

| Leva | % finestre 10Y con MDD ≤ −50% | % finestre 10Y con MDD ≤ −75% |
|------|-------------------------------|-------------------------------|
| 1x   | 23.6%                         | 0%                            |
| 2x   | 83.2%                         | 39.8%                         |
| 3x   | **97.5%**                     | **82.6%**                     |

Tradotto: se compri una 3x sull'S&P e la tieni 10 anni, hai una probabilità del 97.5% (pratica certezza) di vivere almeno un drawdown del 50%, e dell'82.6% di vivere un drawdown del 75% lungo il percorso. È quasi inevitabile.

## Risultati su finestre rolling 20 anni: la convergenza che disinnesca la leva

Sui 50 anni di dataset abbiamo 121 finestre 20Y (step 3 mesi). Qui succede il dato che merita più attenzione:

<figure>
  <img src="/charts/leva-raddoppia-rendimento-mercato/08_boxplot_cagr_20y_realistic.png" alt="Boxplot del CAGR su finestre rolling 20 anni per le tre leve, scenario realistico." />
  <figcaption>Distribuzione del CAGR su finestre 20 anni, step 3 mesi, scenario realistico. Le mediane di 2x e 3x sono praticamente identiche, e i p5 della 3x sono inferiori a quelli della 1x.</figcaption>
</figure>

Numeri:

| Leva | p5     | p25   | **Mediana** | p75    | p95    | % finestre con CAGR < 0 | % finestre 20Y con MDD ≤ −75% |
|------|--------|-------|-------------|--------|--------|--------------------------|--------------------------------|
| 1x   | +6.24% | 8.19% | **9.89%**   | 12.99% | 17.25% | 0%                       | 0%                             |
| 2x   | +6.10% | 10.17%| **13.82%**  | 21.00% | 31.11% | 0%                       | 77.7%                          |
| 3x   | +2.44% | 8.55% | **13.87%**  | 25.84% | 43.27% | 0.83%                    | **100%**                       |

Tre risultati che vanno sottolineati:

**1. Le mediane di 2x e 3x convergono.** A 20 anni, la 3x fa CAGR mediano di 13.87% — la 2x fa 13.82%. Praticamente identici. Cioè *triplicare* la leva (e i drawdown) rispetto alla 2x non porta nessun vantaggio mediano in CAGR. Tutto il drag aggiuntivo (TER più alto + funding doppio) cancella esattamente il "guadagno teorico" della leva extra. È uno dei dati più controintuitivi dell'intera analisi.

**2. I p5 della 3x sono INFERIORI a quelli della 1x.** Nel 5° percentile:
- 1x: 6.24%
- 2x: 6.10% (quasi identico, marginalmente inferiore)
- 3x: **2.44%**

Nelle peggiori finestre 20Y, la 3x rende meno della metà della 1x. La leva nelle code è controproducente. Esiste anche una finestra 20Y in cui la 3x ha CAGR **negativo** (l'unico caso in 121 finestre — ma esiste, e sull'1x non esiste).

**3. Il drawdown 75%+ è praticamente certo.** Nel **100% delle finestre 20Y la 3x ha visto un drawdown peggiore del −75%**. Non l'80%, non il 99%: il 100%. Su 121 finestre osservate, in tutte la 3x è scesa almeno del 75% in qualche momento del percorso. Il 77.7% delle finestre 20Y ha visto un drawdown del 75% anche per la 2x.

> Detto in altro modo: chiunque abbia tenuto una 3x sul S&P per 20 anni, *senza alcuna eccezione storica*, ha vissuto almeno un episodio in cui il portafoglio era ridotto a un quarto del massimo precedente. Solitamente molto peggio. Il drawdown medio del 3x a 20Y è −95.5%.

## Equity curve realistic: i 50 anni in un grafico

<figure>
  <img src="/charts/leva-raddoppia-rendimento-mercato/06_equity_curves_realistic.png" alt="Equity curve dei tre portafogli (leva 1x, 2x, 3x) dal 1976 al 2025, scenario realistico con drag UCITS. Scala logaritmica." />
  <figcaption>Crescita di 1 USD investito a inizio 1976, scenario realistico con costi UCITS. Scala logaritmica per visualizzare i tassi di crescita relativi.</figcaption>
</figure>

> **Come si legge questo grafico — importante.** Come negli articoli precedenti, **questa è una sola simulazione, non una statistica robusta**. Letteralmente: 1 USD investito a gennaio 1976 con la leva indicata, daily-rebalanced, con drag dei costi UCITS applicato. È *un* possibile percorso, *uno* specifico investitore che ha avuto la sorte di iniziare nel 1976 e tenere per 50 anni *senza interruzione*. Le statistiche robuste sono nelle rolling windows sopra (181 + 161 + 121 finestre con punti di partenza diversi). L'equity curve serve per *vedere visivamente* cosa succede a lungo periodo — non per stimare il rendimento futuro di chi entra oggi.

Il grafico mostra in modo lampante perché la 3x è "tradeoff infernale" anche se il punto finale è alto:

- Le tre curve divergono fortemente nei periodi di bull market lineari (1990-1999, 2010-2025).
- Le tre curve convergono violentemente nei crash (2000-2002, 2008-2009): la 3x perde rapidamente la maggior parte del capitale, e ci mette un decennio per ricostruirla.
- Il "vantaggio finale" della 3x è il prodotto cumulativo di 50 anni di un mercato netto-positivo. In un periodo neutrale o leggermente negativo (come il decennio 2000-2010 isolato), la leva è devastante.

## Per chi (forse) può avere senso?

Date le distribuzioni dei rendimenti, la leva ha un caso molto stretto e specifico. Si può pensare di usarla *forse* in queste condizioni, e *solo* in queste:

1. **Conviction forte e short-term** sul mercato (settimane-mesi, non anni). Il volatility drag fa pochi danni su orizzonti corti, e il rendimento di una leva diventa "quasi lineare" su giorni-settimane.
2. **Quota piccola del portafoglio**, mai allocazione principale. Il classico "1-5% in 3x" come componente speculativa con cap rigido sulla perdita massima accettabile.
3. **Capacità psicologica di tenere fino al recupero** anche dopo un −90% di drawdown. Quasi nessun investitore retail ha questa capacità, e non c'è formazione finanziaria che la sostituisca.

Per chi pensa di tenere una 3x come "azionario + di più" su orizzonte 10-20 anni, i dati storici dicono qualcosa di molto chiaro: **il drag dei costi e la volatilità erodono il vantaggio mediano della leva fino a renderlo nullo (a 20Y la 2x e la 3x convergono in CAGR)**, e nei worst case scenari la leva produce CAGR *inferiori* a quelli del semplice 1x. È un trade-off perdente nelle code e neutro in mediana, *al netto* del fatto che il drawdown del 75%+ è praticamente certo.

## Takeaway

1. **La leva 2x non raddoppia il rendimento del mercato**. Sui 50 anni 1976-2025 il moltiplicatore implicito reale è ~1.55× (vs nominale 2×). Per la 3x è ~1.84× (vs nominale 3×).
2. **Il drag ha due componenti**: il volatility drag matematico (~3%/anno per 2x, ~9% per 3x con la vol storica del S&P) + il drag dei costi reali (TER + funding). Sommati, il drag totale dei UCITS è circa **2.45%/anno per 2x** e **4.45%/anno per 3x**.
3. **L'erosione cumulata sul valore finale è devastante**: su 50 anni, la 2x perde il 73% del valore "lordo", la 3x ne perde il **91%**. Il "miracolo" della leva è in larga parte un artefatto del lordo-vs-realistico.
4. **A 20 anni, la 3x non offre alcun vantaggio mediano sulla 2x** (CAGR mediano: 13.87% vs 13.82%). La leva extra paga solo nelle code positive — ma queste sono compensate dalle code negative, dove la leva *danneggia*.
5. **Nei p5 a 20 anni la 3x è inferiore alla 1x** (2.44% vs 6.24%): nei peggiori scenari ventennali, chi non ha leva fa meglio di chi ne ha tre volte.
6. **Il drawdown del 75%+ è strutturalmente certo** sulle leve alte: il 100% delle finestre 20Y della 3x lo ha visto. Non è un "rischio statistico raro" — è il funzionamento normale di quella leva su quei tempi.
7. **La leva ha senso, forse, solo per posizioni piccole, brevi e con conviction**. Come strumento di accumulo a lungo termine sull'S&P è statisticamente perdente, sia rispetto al lineare ideale (volatility drag + costi) sia rispetto al semplice 1x nelle code.

L'idea intuitiva *"investo in 3x e tengo 20 anni: triplicherò il rendimento del mercato"* ha tre falsità incorporate: non triplica nemmeno al netto del volatility drag matematico (che è già del 9%); non si avvicina al triplicare al netto dei costi reali (che aggiungono altri 4-5%); e nei peggiori 20 anni storici la 3x ha *meno* CAGR della 1x. Il marketing degli ETF a leva la racconta come "amplificatore del rendimento". Sui dati reali è un amplificatore del *rischio* a un costo non lineare in termini di rendimento atteso.

---

### Fonti e riproducibilità

- Dati S&P 500 daily price index: [Yahoo Finance](https://finance.yahoo.com/quote/%5EGSPC), via libreria `yfinance`.
- Dividendi mensili per la ricostruzione del Total Return: [dataset Shiller](http://www.econ.yale.edu/~shiller/data.htm), mirror su [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500).
- Calibrazione costi reali: confronto giornaliero **ProShares Ultra S&P 500 (SSO)** vs 2x sintetica matematica calcolata su SPY, periodo 21/06/2006 – 29/12/2023 (17.5 anni).
- TER ETF UCITS di riferimento: WisdomTree S&P 500 (1x, 0.05%), Xtrackers S&P 500 2x Leveraged Daily Swap (2x, 0.60%), WisdomTree S&P 500 3x Daily Leveraged (3x, 0.75%).
- Codice della simulazione: [`scripts/leva-raddoppia-rendimento-mercato.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/leva-raddoppia-rendimento-mercato.py).
- Summary numerico completo: [`/charts/leva-raddoppia-rendimento-mercato/summary.json`](/charts/leva-raddoppia-rendimento-mercato/summary.json).
- Letteratura accademica di riferimento sul leveraged ETF decay: Cheng, M., & Madhavan, A. (2009), *"The Dynamics of Leveraged and Inverse Exchange-Traded Funds"*, Journal of Investment Management.

> Nota: questa analisi è limitata all'universo USA in dollari. Un investitore italiano che compra ETF UCITS è esposto al cambio EUR/USD, ma su 20+ anni di buy & hold l'effetto cambio è di secondo ordine rispetto al drag della leva (vedi articolo precedente sul market timing per la discussione del rischio cambio su orizzonti lunghi). Il funding cost storico potrebbe variare nei prossimi decenni in base all'ambiente dei tassi — al 2025 è marginalmente sopra la media storica, dato il regime "higher for longer" post-2022.
