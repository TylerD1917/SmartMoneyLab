---
title: "Nasdaq a leva 2x con copertura in opzioni: batte il mercato? 50 anni di dati"
description: "Una strategia a leva 2x sul Nasdaq con copertura tattica in put batte il mercato su 50 anni: Sharpe, Calmar e rendimento più alti. Ma a prezzo di drawdown fino al −94%."
pubDate: 2026-08-11
tags: ["leva", "nasdaq", "opzioni", "put", "copertura", "black-scholes", "backtest", "battere-il-mercato", "etf-a-leva"]
author: "SmartMoneyLab"
series: "battere-il-mercato"
seriesOrder: 5
verdict: "vince"
simulationSlug: "leva-nasdaq-copertura-opzionaria"
draft: false
---

## In breve

La leva amplifica i rendimenti ma anche i disastri: un ETF 3x sul Nasdaq, da solo, si azzera nei grandi crolli. La domanda di questo articolo è se una **copertura tattica in opzioni** possa domare la leva abbastanza da battere il mercato in modo consistente. Ho testato una strategia precisa — 95% in un ETF a leva 2x sul Nasdaq, 5% in una put annuale, con una regola per monetizzare la protezione — su **50 anni di dati (1975-2026)**, in Total Return, al lordo e al netto delle tasse italiane, su finestre mobili a 10, 15 e 20 anni. Cinque risultati.

1. **La strategia batte il Nasdaq.** Rendimento annuo mediano netto: **15.0% a 10 anni, 12.4% a 15 anni, 10.8% a 20 anni**, contro 10.3% / 9.9% / 9.4% del Nasdaq semplice. E vince nel **66-72% di tutte le finestre**.

2. **Non è solo leva: è alfa vero.** Batte il Nasdaq anche sulle metriche corrette per il rischio — **Sharpe** (0.40 vs 0.32 a 10 anni), **Calmar** e **Sortino**. La copertura aggiunge valore, non solo rischio.

3. **Il prezzo è brutale.** I drawdown vanno da **−60% (10 anni) a −94% (20 anni)**, contro −36% / −78% del Nasdaq. La strategia funziona sui numeri, ma quasi nessuno la reggerebbe emotivamente.

4. **Il 2x è lo sweet spot.** Il 3x fa più rendimento ma con drawdown del −98% e rischio/rendimento peggiore. Due volte la leva è il punto di equilibrio; tre volte è troppo fragile.

5. **La leva richiede tempo.** A 10 anni l'11% delle finestre chiude comunque in negativo; a 20 anni nessuna. La leva coperta premia chi ha orizzonte lungo e stomaco fortissimo.

Verdetto: **vince** — ma con il caveat più grande della serie.

## La strategia, nel dettaglio

Su un capitale iniziale (poniamo 10.000$):

- **95% in un ETF a leva 2x sul Nasdaq.** Nel backtest è un ETF *sintetico*: ogni giorno replica due volte il rendimento del Nasdaq, meno i costi (spese di gestione e finanziamento della leva). Nella realtà si implementa con un ETF a leva 2x sul Nasdaq-100 (es. QLD).
- **5% in una put OTM a 1 anno**, con strike il 12.5% sotto il prezzo attuale. È un'assicurazione contro i cali profondi del Nasdaq.

Poi, due regole:

- **Monetizzazione tattica.** Se durante l'anno la put si apprezza fino a valere **almeno il doppio del premio pagato** (perché il mercato scende o la volatilità esplode), la si vende. L'incasso **resta in liquidità** e si compra subito una nuova put con una piccola parte di quell'incasso. L'ETF non viene toccato: il resto della liquidità fa da cuscinetto. È un **de-risking**: dopo il trigger sei meno esposto alla leva e più in cassa.
- **Rinnovo annuale.** A ogni anniversario la put scade e se ne compra una nuova, riportando il portafoglio a 95/5. Qui, se necessario, si vende una piccola parte dell'ETF per finanziare la put — realizzando la plusvalenza (che nel calcolo netto viene tassata).

Il cuore della strategia è la **convessità**: nei crolli la put vale molto, e monetizzarla trasforma la protezione in liquidità difensiva proprio quando serve.

## Dati e metodo

**Nasdaq**: serie storica giornaliera del Nasdaq Composite dal 1975 al 2026 (51 anni). Il Composite e il Nasdaq-100 — l'indice su cui esistono gli ETF a leva reali — sono quasi sovrapponibili come esposizione; uso il Composite per avere più storia e più finestre. I rendimenti sono in **Total Return** (con dividendi).

**ETF a leva sintetico**: ogni giorno, `2 × rendimento del Nasdaq − costo di finanziamento sulla parte a debito (tasso a breve + 0.5%) − TER 0.95%`. È la stessa costruzione usata nell'[articolo sulle leve](/posts/leva-raddoppia-rendimento-mercato/).

**Opzioni**: prezzate col modello di **Black-Scholes**, come nell'[articolo sulle LEAPS](/posts/strategia-leaps-vs-buy-and-hold/). Per non regalare nulla alla strategia, le ipotesi sono volutamente **prudenti e a suo sfavore**:

- **Volatilità implicita = volatilità realizzata a 252 giorni + 5 punti** (le put ci costano care ogni anno; e la volatilità realizzata *ritarda* nei crolli, quindi la protezione la marchiamo per meno di quanto varrebbe davvero).
- **Slippage del 3%** su ogni acquisto e vendita di opzioni.
- **Liquidità in eccesso remunerata a un prudenziale 2.5% annuo** fisso.

**Tasse**: riporto sia il **lordo** sia il **netto Italia** (26% su ogni plusvalenza realizzata — vendite di put e di ETF — con compensazione delle minusvalenze). La strategia realizza spesso, quindi il drag fiscale è modellato per intero.

**Confronto**: finestre mobili a **10, 15 e 20 anni con passo 6 mesi** (una strategia a leva va giudicata sul lungo periodo, non su un singolo punto di partenza). Applico il framework a 6+1 metriche della serie. Benchmark principale: il **Nasdaq 1x** in Total Return.

Lo script completo è nel repository ([`scripts/leva-nasdaq-copertura-opzionaria.py`](https://github.com/TylerD1917/smartmoneylab)).

## Il risultato: batte il Nasdaq

Ecco il framework 6+1 sulle finestre mobili, **al netto delle tasse** (valori mediani).

| Orizzonte | | CAGR | Volatilità | Max drawdown | Sharpe | Calmar | Sortino | Batte il Nasdaq |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| 10 anni | **Strategia 2x** | **15.0%** | 34% | −60% | **0.40** | **0.28** | **0.61** | **71%** |
| | Nasdaq 1x | 10.3% | 22% | −36% | 0.32 | 0.26 | 0.46 | — |
| 15 anni | **Strategia 2x** | **12.4%** | 35% | −67% | **0.41** | **0.17** | **0.63** | **72%** |
| | Nasdaq 1x | 9.9% | 23% | −55% | 0.31 | 0.16 | 0.47 | — |
| 20 anni | **Strategia 2x** | **10.8%** | 37% | −94% | **0.34** | 0.12 | **0.54** | **66%** |
| | Nasdaq 1x | 9.4% | 23% | −78% | 0.31 | 0.12 | 0.49 | — |

Il risultato è netto: la strategia batte il Nasdaq su **cinque metriche del framework su sette** — rendimento, Sharpe, Calmar, Sortino e win rate — perdendo solo su volatilità e drawdown, che sono il prezzo strutturale della leva. E vince in due terzi o più di tutte le finestre storiche.

Il punto importante è il **Calmar** e il **Sortino**: sono metriche corrette per il rischio (per il drawdown il primo, per la sola volatilità negativa il secondo). Batterle significa che la copertura non sta solo gonfiando i rendimenti con la leva — sta aggiungendo **alfa vero**. È un risultato diverso da quello che questo blog ha trovato con la [leva pura](/posts/leva-raddoppia-rendimento-mercato/) o con le [LEAPS](/posts/strategia-leaps-vs-buy-and-hold/), dove la leva alzava rendimento e rischio in egual misura senza migliorare il rapporto tra i due.

<figure>
  <img src="/charts/leva-nasdaq-copertura-opzionaria/01_equity_full.png" alt="Crescita di 10.000 dollari dal 1975 al 2026 in scala logaritmica: Nasdaq 1x, 2x nudo, strategia 2x con copertura, 3x con copertura. La strategia 2x sta sopra il Nasdaq e sopra il 2x nudo per quasi tutto il periodo." />
  <figcaption>Crescita di 10.000$ dal 1975 (scala logaritmica, lordo). Sull'intero periodo la strategia 2x coperta porta 10.000$ a circa 4.6 milioni, contro i 581.000$ del Nasdaq semplice. Il 3x fa di più, ma con cadute ancora più violente.</figcaption>
</figure>

<figure>
  <img src="/charts/leva-nasdaq-copertura-opzionaria/02_cagr_rolling.png" alt="Grafico a barre del CAGR mediano netto per orizzonte (10, 15, 20 anni) per Nasdaq 1x, 2x hold, strategia 2x cash e 3x cash. La strategia 2x supera sempre il Nasdaq 1x." />
  <figcaption>Rendimento annuo mediano per orizzonte: la strategia a leva coperta supera il Nasdaq a 10, 15 e 20 anni.</figcaption>
</figure>

## Il prezzo: drawdown mostruosi

Prima di entusiasmarsi, il caveat va urlato. Le stesse finestre che producono quei rendimenti hanno attraversato **cadute dal picco al minimo del 60%, dell'80%, fino al 94%**. Non è un dettaglio: è la vera natura della strategia.

<figure>
  <img src="/charts/leva-nasdaq-copertura-opzionaria/03_mdd_box.png" alt="Boxplot del max drawdown su finestre di 15 anni: Nasdaq 1x contro strategia 2x. La strategia ha drawdown molto più profondi, mediana attorno al −67% contro −55%." />
  <figcaption>Il prezzo da pagare: su finestre di 15 anni il drawdown della strategia è molto più profondo di quello del Nasdaq. E questi sono i cali *sopravvissuti*: chi vende nel panico non li vede mai risalire.</figcaption>
</figure>

Un drawdown del −80% significa vedere 100.000$ diventare 20.000$ e restare lì per mesi o anni. La matematica dice che poi risale; la psicologia dice che quasi nessuno resta investito per scoprirlo. La copertura tattica **attenua** i crolli — nel 2000-2010 la strategia 2x ha perso il 13% contro il 22% del 2x nudo e il 40% del 3x nudo — ma non li elimina. Con la leva, il drawdown non si annulla: si sopporta.

## La distribuzione dei rendimenti

Una domanda naturale: la strategia ha più da guadagnare o da perdere rispetto alla sua mediana? La risposta cambia con l'orizzonte.

<figure>
  <img src="/charts/leva-nasdaq-copertura-opzionaria/04_distribuzione_cagr.png" alt="Boxplot del CAGR per finestre di 10, 15 e 20 anni, strategia contro Nasdaq. La strategia ha mediana più alta e distribuzione più ampia, con coda inferiore più lunga a 10 anni." />
  <figcaption>Distribuzione dei rendimenti annui su finestre mobili. La strategia (oro) ha mediana più alta del Nasdaq (grigio) a ogni orizzonte, ma una dispersione molto più ampia — soprattutto verso il basso sul breve.</figcaption>
</figure>

A **10 anni** la distribuzione è **asimmetrica verso il basso**: la mediana è alta (15%), ma la coda sinistra è lunga — circa l'**11% delle finestre chiude in negativo** (la peggiore attorno al −15%), mentre il tetto arriva al +26%. In altre parole: il più delle volte va molto bene, ma il rischio di un decennio deludente è reale.

A **15 e 20 anni** la distribuzione si fa più simmetrica e la coda negativa si assottiglia: solo il 5% delle finestre a 15 anni è negativo, e **nessuna a 20 anni**. Il tempo, con la leva, non è un lusso: è una condizione necessaria.

## I dettagli che contano

**Perché 2x e non 3x.** Il 3x coperto fa più rendimento (CAGR mediano più alto a ogni orizzonte), ma il suo drawdown arriva al **−98%** e il rapporto rischio/rendimento (Calmar) è uguale o peggiore del 2x. La leva 3x sul Nasdaq è così fragile che nei grandi crolli il decadimento giornaliero la distrugge quasi del tutto, e nemmeno la copertura la salva. Il 2x è il punto in cui la copertura riesce davvero a fare la differenza.

**Cosa fare con l'incasso della put.** Ho testato due filosofie opposte: **reinvestire** l'incasso comprando altro ETF sul ribasso (dip-buying), oppure **tenerlo in liquidità** (de-risking). Sul 2x le due si equivalgono quasi: il dip-buying rende un filo di più sul breve, il de-risking ha drawdown meno profondi e vince sul rischio/rendimento a lungo termine. Ho scelto il de-risking perché più consistente — ma attenzione: sul fragile 3x, il dip-buying (ricomprare leva mentre tutto crolla) è pericoloso e distrugge i rendimenti. Non è una regola universale.

**Il ruolo vero della copertura.** La put non serve a "prevedere" i crolli. Serve a fornire, nei momenti di stress, un attivo che si apprezza mentre tutto il resto scende — e a trasformarlo in liquidità difensiva. È questo, più della protezione in sé, ad aggiungere valore rispetto alla leva nuda.

## I limiti (da leggere)

- **ETF a leva sintetico su indice**: nella realtà useresti un ETF a leva sul Nasdaq-100, con tracking error e costi reali che il modello approssima. Un prodotto a leva sul Composite non esiste.
- **Prezzo delle opzioni**: modellato con Black-Scholes e volatilità realizzata (+5 punti). L'IV reale nei crolli sale più di quanto catturi il modello, quindi se mai *sottostimiamo* il valore della copertura — la strategia reale potrebbe fare un po' meglio, non peggio, su questo fronte. Ma la liquidità e gli spread reali su put annuali possono essere peggiori del 3% ipotizzato.
- **Passato del Nasdaq**: 50 anni dominati da un toro tecnologico secolare. Su un indice diverso, o su un futuro diverso, la leva potrebbe non essere altrettanto premiata.
- **Disciplina ferrea**: la strategia richiede di rispettare i trigger, rinnovare le put, restare investiti attraverso cadute del −60/−90%. È il vincolo più difficile, e non è nei numeri.

## Cosa porto a casa — verdetto: vince

Sui dati, e con ipotesi volutamente severe, la strategia **batte il Nasdaq** — non solo sul rendimento, ma anche sul rischio/rendimento (Sharpe, Calmar, Sortino) e nel 66-72% delle finestre storiche. La copertura tattica in opzioni riesce dove la leva pura fallisce: aggiunge alfa, non solo rischio. Per questo il verdetto della serie è **vince**.

Ma è il "vince" più condizionato che abbia scritto. Vince **se** hai un orizzonte di 15 anni o più, **se** accetti di vedere il capitale dimezzarsi o peggio lungo il cammino, e **se** hai la disciplina di eseguire la strategia esattamente — comprare e rinnovare put, monetizzarle ai trigger, non toccare la leva nel panico. Togli anche una sola di queste condizioni e il vantaggio evapora, o diventa un disastro. La leva coperta non è una scorciatoia: è uno strumento potente per pochissimi, che paga il suo rendimento superiore con un rischio che quasi nessuno regge davvero.
