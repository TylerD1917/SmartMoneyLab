---
title: "Qual è il miglior segmento del mercato azionario? Il dato che disinnesca il bias pro-USA"
description: "Otto segmenti azionari (MSCI World, USA, Europe, Japan, EM, Small Cap, NASDAQ) su 25 anni: chi vince davvero, perché 'USA' è recency bias, perché Europe e Japan non hanno mai vinto una finestra 10y."
pubDate: 2026-05-02
tags: ["asset-allocation", "diversificazione-geografica", "msci", "rolling-windows", "backtest", "sp500", "nasdaq", "emerging-markets"]
author: "SmartMoneyLab"
simulationSlug: "qual-e-il-miglior-segmento-azionario"
draft: false
---

## In breve

Ho confrontato 8 segmenti del mercato azionario globale su 25 anni di dati MSCI Gross Returns USD (gennaio 2001 – dicembre 2025), su finestre rolling 5 e 10 anni con step di 6 mesi. Tre risultati centrali:

1. **Sui 25 anni full-sample il "winner" non è l'S&P 500**. Il ranking CAGR è: NASDAQ (9.77%) > World Small Cap (9.25%) > EM Asia (8.86%) > **USA (8.71%, quarto)** > EM (8.34%) > MSCI World (7.71%) > Europe (6.07%) > Japan (4.60%). L'investitore italiano che pensa "metto tutto su S&P 500 perché è il migliore" si è perso il sub-segmento tech (NASDAQ) e i piccoli ad alta capitalizzazione globale (Small Cap), entrambi sopra di un punto percentuale.
2. **Solo 3 segmenti hanno mai vinto una finestra 10Y**: NASDAQ in 21 finestre su 30, EM in 7, EM Asia in 2. **MSCI World, USA, Europe, Japan e World Small Cap non hanno MAI vinto una finestra 10Y in 25 anni** (nemmeno una). Il "dominio USA" che la narrativa retail propaga è in realtà *dominio NASDAQ* — il sotto-segmento tech, non l'azionario USA generico.
3. **Nelle finestre 10Y peggiori (5° percentile) il segmento più resiliente non è il NASDAQ**, è **World Small Cap** (CAGR p5 = 6.32%), seguito da EM Asia (4.47%) e NASDAQ (4.26%). USA è solo quinto (3.10%). Nelle code i "segmenti minori" hanno protetto meglio dei big.

Il dato che riassume tutto: **non esiste un segmento "migliore in assoluto"**. C'è una rotazione di leadership che cambia ogni decennio, e i due decenni inclusi nel dataset (2001-2010 e 2010-2025) hanno avuto winner radicalmente diversi (EM e EM Asia il primo, NASDAQ il secondo). Chi sceglie ex-ante il "winner del prossimo decennio" è essenzialmente fortunato se ci azzecca.

## La domanda

Il retail italiano medio, quando pensa "investire in azioni", pensa in pratica a tre cose: S&P 500, NASDAQ, e magari MSCI World. Europe è "ferma da anni", Japan è "il caso perso", Emerging Markets sono "rischiosi". Small Cap non li conosce nemmeno.

L'angle che voglio testare sui dati è il seguente: *negli ultimi 10-15 anni gli USA hanno effettivamente sovraperformato gli altri segmenti, ma questo è un fenomeno specifico di un certo regime macro (tassi a zero, dominio tech, dollaro forte), non una proprietà intrinseca del mercato USA*. In altri decenni lo scenario è stato diverso. E lo sarà di nuovo.

Vediamo se i dati lo confermano.

## Il metodo

- **Periodo**: gennaio 2001 – dicembre 2025 (299 mesi, ~25 anni). Limite imposto dalla disponibilità dei dati MSCI scaricabili pubblicamente; i decenni '70-'90 (dove il dominio era prima USA, poi Giappone) li perdiamo, ma 25 anni includono comunque dot-com bottom 2002, GFC 2008, ZIRP 2010-2021, COVID 2020 e shock tassi 2022 — quattro regimi macro distinti.
- **Asset universe**: 8 segmenti azionari, tutti con dati monthly Gross Returns USD:
  - **MSCI World** — il benchmark "globale developed", 23 paesi
  - **MSCI USA** — proxy dell'S&P 500
  - **MSCI Europe** — Eurozona + UK + Svizzera + nordici
  - **MSCI Japan** — solo Giappone
  - **MSCI Emerging Markets (EM)** — i mercati emergenti aggregati
  - **MSCI EM Asia** — sotto-segmento Asia di EM (Cina, India, Korea, Taiwan)
  - **MSCI World Small Cap** — il segmento "size factor" globale dei sviluppati
  - **NASDAQ Composite** — proxy del segmento tech USA, scaricato da yfinance e ricostruito a Total Return aggiungendo un dividend yield costante stimato a 0.8%/anno
- **Index Level**: **Gross** (dividendi reinvestiti, prima delle withholding tax). Coerente con S&P 500 TR Shiller usato negli articoli precedenti del blog.
- **Currency**: USD per tutti i segmenti. Per un investitore italiano l'esposizione cambio EUR/USD si annulla su orizzonti lunghi (vedi articolo precedente sul market timing) e in ogni caso non altera i confronti *relativi* tra segmenti.
- **Rolling**: 5Y (60 mesi) e 10Y (120 mesi), step 6 mesi. Niente 20Y (il dataset di 25 anni produce solo 11 finestre 20Y, troppo poche per essere statistica robusta).

Lo script Python che produce tutto è in [`scripts/qual-e-il-miglior-segmento-azionario.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/qual-e-il-miglior-segmento-azionario.py).

> **Caveat onesto sul NASDAQ**: a differenza degli MSCI, per il NASDAQ Composite non esiste una serie Total Return scaricabile gratuitamente da fonti pubbliche. Il TR è ricostruito da yfinance (price-only) aggiungendo un dividend yield costante storico stimato (0.8%/anno). L'errore atteso sui 25 anni è ~0.2-0.3 punti percentuali di CAGR — significativo ma non distrugge il messaggio. La direzione del confronto regge sicuramente.

## Risultati full-sample: la classifica sui 25 anni

| Segmento         | CAGR    | Volatilità annualizzata | Max drawdown |
|------------------|---------|--------------------------|--------------|
| **NASDAQ**       | **9.77%** | 20.33%                  | −57.14%      |
| World Small Cap  | 9.25%   | 17.99%                   | −56.17%      |
| EM Asia          | 8.86%   | 20.44%                   | −62.66%      |
| USA              | 8.71%   | 15.24%                   | −50.65%      |
| EM               | 8.34%   | 20.37%                   | −61.44%      |
| MSCI World       | 7.71%   | 15.40%                   | −53.65%      |
| Europe           | 6.07%   | 18.11%                   | −58.98%      |
| Japan            | 4.60%   | 15.32%                   | −47.10%      |

Cinque cose vanno notate:

- **NASDAQ è in cima** ma non per molto: 1 punto percentuale sopra a Small Cap, 1.5 punti sopra USA. Su 25 anni capitalizzati, queste differenze sono enormi: 1$ → $10.34 con NASDAQ, $9.04 con Small Cap, $8.06 con USA. Diventa un 28% di gap finale tra NASDAQ e USA. Significativo.
- **USA è solo quarto**, dietro Small Cap e EM Asia. La narrativa "S&P 500 è il migliore" non regge sui dati 25 anni.
- **Europe e Japan in coda**: 6.07% e 4.60% sono CAGR sotto a quelli di un buon portafoglio obbligazionario. Per gli investitori europei "puri" è stato un quarto di secolo molto duro.
- **Il rapporto rendimento/rischio migliore è di USA**: CAGR 8.71% con vol 15.24% e MDD −50.65%. Il NASDAQ paga 5 punti percentuali in più di volatilità per portare a casa 1 punto in più di CAGR. Nei portafogli "ottimi" sotto Sharpe, USA batte NASDAQ.
- **Il MSCI World si comporta come una media**: CAGR 7.71% (sopra Europe/Japan, sotto USA/NASDAQ), vol 15.40%, MDD −53.65%. È l'opzione "default sensato": non vince mai, non perde mai catastroficamente. Per un investitore retail medio è probabilmente la scelta più ragionevole *proprio perché* nessun segmento è il "winner permanente".

## Risultati su finestre rolling 10 anni

Sulle 30 finestre rolling 10Y disponibili (step 6 mesi):

<figure>
  <img src="/charts/qual-e-il-miglior-segmento-azionario/02_boxplot_cagr_10y.png" alt="Boxplot del CAGR su finestre rolling 10 anni per gli 8 segmenti azionari (World, USA, Europe, Japan, EM, EM Asia, World Small Cap, NASDAQ)." />
  <figcaption>Distribuzione del CAGR su finestre 10 anni, step 6 mesi. Le code di NASDAQ e EM/EM Asia sono molto larghe rispetto ai grandi indici.</figcaption>
</figure>

Numeri esatti:

| Segmento         | p5     | p25   | **Mediana** | p75    | p95    |
|------------------|--------|-------|-------------|--------|--------|
| **NASDAQ**       | 4.26%  | 9.34% | **13.22%**  | 16.33% | 18.40% |
| USA              | 3.10%  | 7.78% | **10.23%**  | 13.75% | 15.25% |
| World Small Cap  | 6.32%  | 8.04% | **9.49%**   | 10.28% | 12.43% |
| MSCI World       | 4.46%  | 6.69% | **8.56%**   | 10.42% | 11.92% |
| EM Asia          | 4.47%  | 5.53% | **6.48%**   | 11.24% | 14.25% |
| Europe           | 2.03%  | 5.20% | **5.91%**   | 6.87%  | 8.71%  |
| Japan            | 1.01%  | 3.28% | **5.76%**   | 6.40%  | 6.96%  |
| EM               | 2.37%  | 3.36% | **4.39%**   | 10.30% | 16.41% |

Lettura del dato:

- **NASDAQ ha la mediana più alta** (13.22%) ma anche la dispersione più alta (p5 4.26% → p95 18.40%, range di 14 punti).
- **USA è secondo in mediana** (10.23%) ma il p5 (3.10%) è inferiore a quello di Small Cap, EM Asia e MSCI World. Cioè nei peggiori 10 anni l'investitore "tutto USA" ha portato a casa meno dei segmenti meno alla moda.
- **World Small Cap ha il p5 più alto di tutti** (6.32%). Cioè nei peggiori scenari decennali, il segmento "che nessuno guarda" è quello che ha protetto meglio. Risultato controintuitivo ma robusto.
- **EM Asia ha p5 4.47%**, sopra a NASDAQ. Anche il segmento "rischioso per definizione" (Cina, India, Korea, Taiwan) ha protetto meglio del "segmento sicuro" tech USA nei peggiori scenari decennali.
- **Europe e Japan sono lo "specchio del peggio"**: mediane sotto il 6%, p5 sotto il 2%, p95 sotto il 9%. Il quarto di secolo è stato matematicamente perdente per chi ha puntato esclusivamente su questi segmenti.

## Risultati su finestre rolling 5 anni

<figure>
  <img src="/charts/qual-e-il-miglior-segmento-azionario/01_boxplot_cagr_5y.png" alt="Boxplot del CAGR su finestre rolling 5 anni per gli 8 segmenti azionari." />
  <figcaption>Distribuzione del CAGR su finestre 5 anni, step 6 mesi. La rotazione tra winner si fa più rumorosa.</figcaption>
</figure>

Senza ridicolizzare il dataset con altre tabelle, riassumo gli aspetti che cambiano rispetto alle 10Y:

- **Le code negative si allargano**: il p5 della maggior parte dei segmenti scende sotto zero. Solo Small Cap (+0.8%), USA (+0.1%), NASDAQ (+1.2%) restano al limite del positivo. Tutti gli altri possono finire 5 anni in perdita nel 5% delle finestre.
- **La % di finestre con CAGR negativo**: Japan 15%, Europe 10%, EM 10%, World 7.5%, USA / NASDAQ / Small Cap / EM Asia tra il 5% e il 7.5%.
- **NASDAQ resta in cima in mediana** (14.26%) e nei p95 (23.68%). Ma anche nei p5 (1.22%) supera USA (0.14%): il "growth premium" è strutturale anche nelle code positive.

## I drawdown: chi soffre di più?

<figure>
  <img src="/charts/qual-e-il-miglior-segmento-azionario/04_drawdown_distribution_10y.png" alt="Distribuzione cumulata del max drawdown osservato in finestre rolling 10 anni per gli 8 segmenti." />
  <figcaption>CDF del max drawdown osservato in ciascuna finestra rolling 10Y. Più la curva è "spostata a destra" (verso valori meno negativi), meglio.</figcaption>
</figure>

Il max drawdown su 10Y è dominato in larga parte dalla GFC 2008-2009 e dal dot-com 2000-2002. I numeri sintetici:

| Segmento         | MDD mediano (10Y) | MDD massimo del periodo |
|------------------|-------------------|--------------------------|
| Japan            | −38.45%           | −47.10%                  |
| USA              | −44.08%           | −50.65%                  |
| MSCI World       | −46.60%           | −53.65%                  |
| NASDAQ           | −43.29%           | −57.14%                  |
| World Small Cap  | −48.67%           | −56.17%                  |
| Europe           | −51.40%           | −58.98%                  |
| EM Asia          | −49.02%           | −62.66%                  |
| EM               | −52.54%           | −61.44%                  |

Cose da notare:

- **Japan ha il drawdown più contenuto** (−47.10% massimo). Sorprendente, ma coerente col fatto che il Giappone era già "lost decade" da prima del 2001 e quindi non ha avuto crash nella GFC paragonabili a quelli degli altri segmenti.
- **EM Asia ha il drawdown peggiore** (−62.66%). Il prezzo della volatilità.
- **NASDAQ ha drawdown medio simile a USA** (−43% vs −44%), ma con CAGR superiore. Quindi al netto del rischio (non solo della vol come misura ex-ante, ma del MDD effettivo) il NASDAQ è stato un "free lunch" sui 25 anni — ma con la postilla che la prossima decade potrebbe rivelarsi diversa.

## La rotazione di leadership: il dato che cambia il framing

Questa è la sezione centrale dell'articolo. Per ciascuna finestra rolling 10Y identifico il segmento col CAGR più alto e creo una "striscia temporale" colorata. La domanda: *chi vinceva quando?*

<figure>
  <img src="/charts/qual-e-il-miglior-segmento-azionario/05_leadership_rotation_10y.png" alt="Heatmap della rotazione di leadership su finestre rolling 10 anni: striscia temporale colorata che mostra il segmento col CAGR più alto in ciascuna finestra rolling 10 anni." />
  <figcaption>Su 30 finestre rolling 10Y, qual è il segmento col CAGR più alto in ciascuna. Ciano = NASDAQ, ambra = EM, ambra scuro = EM Asia.</figcaption>
</figure>

Il count netto delle vittorie su 30 finestre:

| Segmento vincitore | N. finestre 10Y |
|--------------------|-----------------|
| **NASDAQ**         | **21** (70%)    |
| EM                 | 7 (23%)         |
| EM Asia            | 2 (7%)          |
| MSCI World         | 0               |
| USA                | 0               |
| Europe             | 0               |
| Japan              | 0               |
| World Small Cap    | 0               |

Solo **3 segmenti** hanno mai vinto una finestra 10Y. Gli altri 5 mai, neppure una volta. Tradotto: in tutte le 30 finestre 10Y del periodo 2001-2025, nessun investitore avrebbe potuto dire ex-post "ho fatto la scelta migliore mettendo tutto su MSCI World" o "tutto su S&P 500" — c'era sempre qualcuno (NASDAQ, EM o EM Asia) che batteva.

E qui sta il punto controintuitivo: **EM ha vinto le 9 finestre 10Y di inizio periodo**, quelle che includono il 2003-2007 (boom EM con commodities forti, USD debole, Cina entrata WTO). Mentre **NASDAQ ha vinto le 21 finestre della seconda metà** (post-2010). La "leadership" è stata letteralmente divisa in due metà nette.

Su finestre rolling 5Y la rotazione è ancora più frammentata — 4 segmenti hanno vinto almeno una finestra (NASDAQ 26, EM 10, EM Asia 3, USA 1). Ma il pattern di fondo è lo stesso.

## Il bias del recency: perché ci sembra che USA sia "il migliore"

Le ragioni psicologiche per cui il retail italiano è convinto che "S&P 500 è il segmento migliore" sono ben documentate nella behavioral finance:

1. **Recency bias**. Gli ultimi 15 anni (2010-2025) sono stati un dominio chiaro USA, soprattutto NASDAQ. Il nostro cervello pesa enormemente le esperienze recenti rispetto a quelle precedenti, e proietta il pattern recente sul futuro.
2. **Availability heuristic**. I media finanziari italiani parlano molto più dell'S&P 500 e di Apple/Microsoft/Nvidia che dei mercati emergenti, di Hitachi o di Inditex. La frequenza con cui un'idea ci viene esposta condiziona la nostra valutazione del suo "valore".
3. **Survivorship bias del decennio**. Chi pensa al "lost decade" pensa a Europe o Japan post-2010. Pochi ricordano che il 2000-2010 fu il "lost decade USA": S&P 500 ha fatto −8% nominale cumulato in dieci anni, EM ha fatto +200%. Se il dataset partisse dal 2000 e finisse al 2010, avresti scritto un articolo opposto.

Il fatto stesso che 2 segmenti molto diversi tra loro (NASDAQ e EM) abbiano vinto rispettivamente la prima e la seconda metà del periodo dovrebbe far sospettare che la "logica" del winner del decennio dipende fortemente dal regime macro: tassi, dollaro, ciclo delle commodities, peso del tech sul indice. Cambiando il regime, cambia il vincitore.

## Implicazioni operative

Cosa fare di tutto questo se sei un investitore retail?

**1. Diversificazione geografica vera**. Non perché "in teoria diversificare riduce il rischio" — frase di marketing. Ma perché *non sai quale sarà il winner del prossimo decennio* e i dati storici non ti danno una guida affidabile. MSCI World è il default sensato per chi vuole esposizione globale senza dover scegliere ex-ante.

**2. ACWI o World Small Cap come tilt**. Se vuoi "fare qualcosa in più" rispetto al World, due tilt che hanno senso strutturalmente sono:
- **Aggiungere EM via MSCI ACWI** (All Country World, include EM): aumenta la copertura ai paesi che hanno vinto il primo decennio del dataset, in cui altrimenti non avresti esposizione.
- **Aggiungere World Small Cap**: ha il p5 più alto a 10Y, è il "size factor" classico, e diversifica strutturalmente il rischio del large-cap.

**3. Tilt USA o NASDAQ è una scommessa di regime**. Sovrappesare USA (o NASDAQ) rispetto a un benchmark globale equivale a scommettere che il regime macro post-2010 (tassi a zero/bassi, dominio tech, dollaro forte) continuerà nei prossimi 10 anni. Può anche essere — ma è una **scommessa di regime**, non una "scelta sicura" basata sui dati storici.

**4. Stay away from single-country bets** salvo conviction estrema. Investire 100% in Europe o 100% in Japan, sui dati 2001-2025, è stato statisticamente perdente rispetto al benchmark globale. Chi pensa di "fare il timing del decennio europeo prossimo" sta facendo market timing nascosto.

**5. La cosa più sensata, banalmente, resta MSCI World**. Non vince, ma non perde. CAGR 7.71% sui 25 anni con vol 15% e MDD −54%. È il "compromesso ragionevole" per chi vuole esposizione azionaria globale e accetta di non scegliere ex-ante il winner del prossimo decennio.

## Takeaway

1. **Sui 25 anni 2001-2025 il "winner" non è S&P 500**: NASDAQ ha CAGR 9.77%, World Small Cap 9.25%, EM Asia 8.86%, USA solo 8.71%. La narrativa pro-S&P è sui 10-15 anni recenti, non sull'intero periodo.
2. **Solo 3 segmenti hanno mai vinto una finestra 10Y**: NASDAQ (21 finestre), EM (7), EM Asia (2). Gli altri 5 (incluso USA, World, Europe, Japan, Small Cap) MAI. La leadership ruota nettamente tra decenni.
3. **Nelle finestre 10Y peggiori il segmento più resiliente è World Small Cap** (CAGR p5 = 6.32%), non USA (p5 = 3.10%). Le aspettative sui "winner permanenti" sono spesso invertite nelle code.
4. **Il bias pro-USA è recency bias**: gli ultimi 15 anni hanno avuto il dominio USA/tech, ma il decennio precedente (2001-2010) aveva visto EM dominare nettamente. Cambiando il regime cambia il vincitore.
5. **MSCI World è il default sensato** per chi non vuole scommettere il decennio. Non vince, ma non perde mai catastroficamente. CAGR 7.71%, vol 15.4%, MDD −54%.
6. **Tilt geografico = scommessa di regime**, non "scelta sicura". Vale la pena solo con conviction articolata sul perché il regime macro produrrà il regime di mercato attesi.
7. **Europe e Japan sono stati i big losers del periodo** (CAGR 6.07% e 4.60%). Investire 100% in questi segmenti su 25 anni è stato statisticamente perdente, anche prima di considerare la fiscalità italiana.

L'idea controintuitiva che vale la pena interiorizzare: **non c'è un "best segment" stabile nel tempo, e i dati lo dimostrano in modo netto**. La reazione corretta non è "faccio market timing tra segmenti" (impossibile, vedi articolo precedente sul market timing). È "diversifico e accetto di prendere la media", che è spesso una scelta migliore della "scelta migliore" tentata ex-ante.

---

### Fonti e riproducibilità

- **Indici MSCI** (Gross Returns, USD, Standard size segment): [MSCI End-of-Day Data Search](https://www.msci.com/end-of-day-data-search). World, USA, Europe, Japan, EM, EM Asia, World Small Cap.
- **NASDAQ Composite** (`^IXIC`): [Yahoo Finance](https://finance.yahoo.com/quote/%5EIXIC) via libreria `yfinance`. TR ricostruito aggiungendo dividend yield costante 0.8%/anno (stima storica del NASDAQ Composite).
- **Codice della simulazione**: [`scripts/qual-e-il-miglior-segmento-azionario.py`](https://github.com/TylerD1917/SmartMoneyLab/blob/main/scripts/qual-e-il-miglior-segmento-azionario.py).
- **Dati grezzi** (NAV cumulati mensili dei segmenti): [`/charts/qual-e-il-miglior-segmento-azionario/data.csv`](/charts/qual-e-il-miglior-segmento-azionario/data.csv).
- **Summary numerico completo**: [`/charts/qual-e-il-miglior-segmento-azionario/summary.json`](/charts/qual-e-il-miglior-segmento-azionario/summary.json).
- Letteratura accademica di riferimento sulla rotazione di leadership tra mercati: Asness, C., Frazzini, A., & Pedersen, L. (2019), *"Quality minus Junk"*, Review of Accounting Studies; e l'ampio corpus sui factor models di Fama & French.

> Nota: questa analisi è limitata al periodo 2001-2025 (25 anni), e tutti i rendimenti sono in USD. I risultati relativi tra segmenti dovrebbero essere robusti rispetto al cambio EUR/USD su orizzonti decennali, ma le code di breve periodo (5Y) potrebbero variare in modo non trascurabile per un investitore italiano. Una replica EUR-centric con cambio modellato esplicitamente sarà oggetto di un articolo futuro.
