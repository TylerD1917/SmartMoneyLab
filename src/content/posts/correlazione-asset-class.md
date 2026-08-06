---
title: "La diversificazione è un'illusione? Correlazioni tra 31 asset class su 20 anni"
description: "Uno studio sulle correlazioni tra 31 asset class in dollari (2006-2026): l'azionario globale è quasi un unico trade, i veri diversificatori sono pochi, e nei crolli spariscono."
pubDate: 2026-08-06
tags: ["correlazioni", "diversificazione", "asset-allocation", "portafoglio", "materie-prime", "obbligazioni", "studio", "backtest"]
author: "SmartMoneyLab"
simulationSlug: "correlazione-asset-class"
draft: false
---

## In breve

"Diversifica" è il primo comandamento della finanza personale. Ma diversificare tra cosa, di preciso? Ho misurato la correlazione reciproca tra **31 asset class** — sei tra materie prime e beni rifugio, dieci indici settoriali, quindici indici geografici — su **vent'anni di dati mensili in dollari (2006-2026)**. Quattro conclusioni.

1. **La diversificazione geografica dentro l'azionario è in gran parte un'illusione.** La correlazione media tra le asset class azionarie è **0.67**, e le coppie più correlate sfiorano l'1: USA e MSCI World correlano a **0.97**, Europa e Germania a 0.95. Comprare "il mondo" invece del solo S&P 500 è, in dollari, quasi lo stesso investimento.

2. **I veri diversificatori non sono azionari.** L'unica asset class con correlazione *negativa* rispetto al blocco azionario sono le **obbligazioni a lungo termine** (Treasury USA 20+, −0.06). Poi oro (+0.15), argento e petrolio. La correlazione media tra azionario e beni rifugio è **0.23**, contro lo 0.67 interno all'azionario.

3. **La diversificazione svanisce proprio quando servirebbe.** Nei crolli la correlazione azionaria media sale: **0.77 nella crisi 2008, 0.89 nel COVID del 2020**. Quando il panico colpisce, tutto l'azionario mondiale cade insieme.

4. **Un portafoglio costruito solo per minima correlazione ha eguagliato il mercato dimezzando il rischio.** Cinque asset scelti unicamente perché scorrelati tra loro (oro, petrolio, Treasury, finanziari, semiconduttori) hanno reso l'11.5% annuo contro l'11.3% dell'S&P 500, ma con un drawdown massimo del **−32% contro −51%**. Stesso rendimento, metà del dolore.

## La domanda

Tutti ripetono "diversifica", ma la diversificazione funziona solo se gli asset che metti in portafoglio si muovono *diversamente* l'uno dall'altro. Due asset che salgono e scendono insieme, per quanto diversi sulla carta, non ti proteggono da niente: nel momento sbagliato crollano in coppia. La misura che cattura questo "muoversi insieme" è la **correlazione**: va da +1 (si muovono identici) a −1 (si muovono all'opposto), passando per 0 (indipendenti).

La domanda di questo studio è semplice e verificabile: **quanto sono correlate, davvero, le principali asset class del mercato?** E soprattutto: la diversificazione che il retail dà per scontata — comprare settori diversi, paesi diversi — riduce sul serio il rischio, o è in gran parte apparenza?

## Dati e metodo

**Universo (31 asset)**. Sei beni rifugio / materie prime (Bitcoin, oro, argento, rame, petrolio, Treasury USA 20+ anni); dieci settori (Nasdaq 100, Energy, Healthcare, Financials, Value, Consumer Staples, Small Cap, Real Estate, Difesa, Semiconduttori); dieci indici geografici (USA, MSCI World, ACWI, Emergenti, Europa, Germania, UK, Cina, Giappone, America Latina); cinque bonus (Corea, Australia, India, Canada, Taiwan).

**Tutto in dollari, total return, dati mensili.** Ogni asset è rappresentato da un ETF quotato negli Stati Uniti (Adj Close, quindi con dividendi e cedole reinvestiti), così la valuta è uniforme e il confronto onesto. Le materie prime fisiche (oro, argento, rame, petrolio) sono il future front-month in dollari. Bitcoin è lo spot BTC-USD. MSCI World usa la serie MSCI World Gross USD (dal 2000) perché l'ETF equivalente parte solo dal 2012.

**La matrice principale**. Finestra comune **giugno 2006 - agosto 2026** (243 mesi, ~20 anni), 28 asset. Sono esclusi da questa matrice Bitcoin (dati solo dal 2014), India e l'ETF ACWI (troppo recenti per i vent'anni comuni). Bitcoin è trattato a parte, come approfondimento.

**Correlazione**. Calcolata sui rendimenti mensili semplici (la convenzione standard in finanza). La correlazione tra due asset misura quanto i loro rendimenti mensili si muovono insieme nel periodo.

Lo script completo, la matrice in CSV e tutti i grafici sono in [`/charts/correlazione-asset-class/`](/charts/correlazione-asset-class/) e nel repository ([`scripts/correlazione-asset-class.py`](https://github.com/TylerD1917/smartmoneylab/blob/main/scripts/correlazione-asset-class.py)).

## La mappa delle correlazioni

<figure>
  <img src="/charts/correlazione-asset-class/01_heatmap_principale.png" alt="Heatmap delle correlazioni tra 28 asset class, 2006-2026. Il grande blocco azionario (geografici e settoriali) è rosso scuro, cioè fortemente correlato. Le obbligazioni e alcune materie prime formano una fascia blu, cioè poco o negativamente correlata." />
  <figcaption>Matrice di correlazione, 28 asset, 2006-2026. Rosso = correlazione alta, blu = bassa o negativa. Il grande blocco rosso in alto a sinistra è l'azionario mondiale: quasi tutto si muove insieme. La fascia blu in basso a destra sono i pochi veri diversificatori (obbligazioni, oro).</figcaption>
</figure>

Il colpo d'occhio dice già tutto: un enorme blocco rosso — l'azionario, geografico e settoriale — dove quasi ogni coppia è fortemente correlata, e una piccola fascia blu — le obbligazioni e l'oro — che si muove diversamente da tutto il resto.

## Sezione 1 — L'azionario globale è quasi un unico trade

La correlazione media tra tutte le asset class *azionarie* (settori + geografie) è **0.67**. Le coppie più correlate del dataset:

| Coppia | Correlazione |
|---|---|
| USA (S&P 500) — MSCI World | **0.97** |
| Europa — Regno Unito | 0.95 |
| Europa — Germania | 0.95 |
| Value — USA (S&P 500) | 0.95 |
| Value — MSCI World | 0.94 |
| Europa — MSCI World | 0.93 |

Il dato USA↔MSCI World a 0.97 è quasi tautologico (gli USA pesano ~70% dell'indice World), ma è proprio il punto: **comprare "l'azionario mondiale" per diversificare dall'S&P 500 non ti diversifica quasi per niente.** Ed Europa, Germania, Regno Unito correlano tra loro a 0.95: il "diversifica per geografia" all'interno dei mercati sviluppati sposta pochissimo. In dollari, la globalizzazione dei mercati ha reso l'azionario un unico grande fattore di rischio comune.

Anche i settori raccontano la stessa storia: pur con differenze, tendono a muoversi con il mercato. Le uniche eccezioni relative sono i settori difensivi (Consumer Staples, Healthcare), che correlano "solo" attorno a 0.56-0.58 — meno del resto, ma comunque tutt'altro che scorrelati.

## Sezione 2 — I veri diversificatori non sono azionari

Se ordiniamo ogni asset per la sua correlazione media con il blocco azionario globale, emerge chi diversifica *davvero*.

<figure>
  <img src="/charts/correlazione-asset-class/04_diversificatori_ranking.png" alt="Grafico a barre orizzontali che ordina gli asset per correlazione media con il blocco azionario. Treasury USA è l'unico negativo, seguito da oro, argento, petrolio; poi tutto l'azionario in una fascia alta." />
  <figcaption>Correlazione media di ciascun asset con il blocco azionario globale. Solo le obbligazioni lunghe sono negative; oro e materie prime sono bassi; tutto l'azionario è nella fascia alta.</figcaption>
</figure>

| Asset | Correlazione media con l'azionario |
|---|---|
| **Treasury USA 20+** | **−0.06** |
| Oro | +0.15 |
| Argento | +0.28 |
| Petrolio | +0.32 |
| Rame | +0.45 |
| ...e poi tutto l'azionario | da +0.48 a +0.97 |

La correlazione media tra azionario e beni rifugio è **0.23**, contro lo 0.67 interno all'azionario. Tradotto: **le uniche asset class che ti proteggono davvero quando l'azionario cade sono le obbligazioni a lungo termine, l'oro e, in misura minore, le materie prime.** Le coppie a correlazione più negativa dell'intero dataset sono tutte "Treasury contro qualcosa di ciclico": petrolio↔Treasury −0.33, Energy↔Treasury −0.29, rame↔Treasury −0.24.

È il motivo per cui i portafogli classici (60/40, All Weather, Permanent Portfolio) mettono le obbligazioni accanto alle azioni: non per il rendimento delle obbligazioni, ma per la loro correlazione negativa, che ammorbidisce le cadute.

## Sezione 3 — La diversificazione svanisce nei crolli

C'è un problema che i numeri "medi" nascondono: **la correlazione non è stabile nel tempo. Sale proprio nei momenti peggiori.**

<figure>
  <img src="/charts/correlazione-asset-class/03_corr_azionario_nel_tempo.png" alt="Grafico della correlazione media azionaria su finestre mobili di 12 mesi, dal 2006 al 2026, con le fasi di crisi evidenziate. La correlazione si impenna durante il 2008 e il 2020." />
  <figcaption>Correlazione media azionaria su finestre mobili di 12 mesi. Le fasce rosse sono le crisi: la correlazione si impenna quando i mercati crollano.</figcaption>
</figure>

<figure>
  <img src="/charts/correlazione-asset-class/06_scatter_corr_vs_crisi.png" alt="Grafico a barre che confronta la correlazione azionaria media durante le crisi (2008, 2020, 2022) con la media del periodo pieno. Nel 2008 e 2020 è molto più alta." />
  <figcaption>Correlazione azionaria media nelle tre crisi contro la media del periodo pieno. Nel panico del 2008 e del 2020 sale nettamente sopra la media.</figcaption>
</figure>

| Periodo | Correlazione media azionaria |
|---|---|
| Media 2006-2026 | 0.67 |
| Crisi finanziaria 2008 | **0.77** |
| COVID 2020 | **0.89** |
| Orso 2022 | 0.65 |

Nel crollo del COVID, quando ogni investitore avrebbe voluto la diversificazione, la correlazione media azionaria è schizzata a **0.89**: praticamente tutto l'azionario mondiale si muoveva all'unisono verso il basso. È il paradosso crudele della diversificazione azionaria: funziona nei mercati calmi, ti abbandona nel panico.

Interessante il contrasto del 2022 (0.65, in linea con la media): fu un calo "ordinato", guidato dalla risalita dei tassi, non un panico di liquidità. Le correlazioni esplodono nelle crisi di *paura*, non in tutti i mercati orso.

## Sezione 4 — Il portafoglio costruito solo sulla correlazione

Fin qui la teoria. Ora un esperimento pratico e volutamente ingenuo: e se costruissi un portafoglio scegliendo cinque asset **unicamente perché scorrelati tra loro**, senza guardare minimamente ai rendimenti attesi? Ho fatto cercare al computer, tra tutte le 80.000 combinazioni possibili, il gruppo di cinque asset con la minima correlazione media reciproca.

Il risultato: **Oro, Petrolio, Treasury USA 20+, Financials, Semiconduttori** — correlazione media interna di appena **0.074**. Cinque cose che si muovono quasi indipendentemente. Equal weight, comprati e tenuti per vent'anni, contro il semplice S&P 500:

<figure>
  <img src="/charts/correlazione-asset-class/05_portafoglio_mincorr_vs_mercato.png" alt="Curva di crescita percentuale del portafoglio a minima correlazione contro l'S&P 500 dal 2006 al 2026. Le due curve arrivano simili, ma il portafoglio ha cali molto meno profondi." />
  <figcaption>Crescita del portafoglio a minima correlazione contro l'S&P 500, 2006-2026. Arrivano quasi allo stesso punto, ma il portafoglio diversificato ha attraversato cali molto meno profondi.</figcaption>
</figure>

| Metrica | Portafoglio min-correlazione | S&P 500 |
|---|---|---|
| CAGR | 11.5% | 11.3% |
| Volatilità | 15.4% | 15.2% |
| **Max drawdown** | **−32%** | **−51%** |
| Sharpe | 0.62 | 0.61 |
| **Calmar** | **0.36** | **0.22** |
| Multiplo 20 anni | 9.05× | 8.73× |

**Stesso rendimento del mercato, ma con un drawdown massimo quasi dimezzato** (−32% contro −51%). Il Calmar (rendimento diviso drawdown) passa da 0.22 a 0.36: molto più rendimento per unità di dolore. E tutto questo scegliendo gli asset *senza guardare i rendimenti* — solo per bassa correlazione.

Un'onestà intellettuale importante, però: su finestre mobili di 10 anni, questo portafoglio **batte l'S&P 500 sul rendimento puro solo nell'11% dei casi**. L'S&P, negli ultimi vent'anni, ha corso moltissimo. Il valore del portafoglio diversificato non è "rende di più" — è "rende quasi uguale prendendosi molto meno rischio". Chi non sopporta un −51% e venderebbe nel panico, con un −32% ha più probabilità di restare investito e incassare quel rendimento. La diversificazione non è una macchina per battere il mercato: è una macchina per ridurre il rischio a parità di rendimento. E questi dati mostrano che, storicamente, ha funzionato.

## Approfondimento: e Bitcoin?

Bitcoin non è nella matrice principale perché ha dati solo dal 2014. Ma sulla finestra 2014-2026 la sua correlazione con l'azionario è già indicativa: **+0.34 con l'S&P 500**, +0.32 con il Nasdaq, +0.31 con i finanziari. Il "diversificatore assoluto scorrelato da tutto" della narrativa cripto non regge più: negli ultimi anni Bitcoin si è agganciato al risk-on azionario, salendo e scendendo con la tecnologia. Resta meno correlato dell'azionario-su-azionario (0.67), ma è lontano dalla scorrelazione dell'oro (0.15) o delle obbligazioni (−0.06).

## Esplora la mappa

Ho costruito una **heatmap interattiva** dove puoi passare sopra ogni coppia di asset e leggere la correlazione esatta, o filtrare per categoria. È nella sezione strumenti del sito.

<div style="margin: 1.5rem 0; padding: 1.25rem 1.5rem; border: 2px solid #1e3a8a; border-radius: 1rem; background: #dbeafe;">
  <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #1e3a8a; font-weight: 600;">Strumento correlato</div>
  <div style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-top: 0.25rem;">
    Mappa interattiva delle correlazioni
  </div>
  <div style="color: #334155; margin-top: 0.5rem; font-size: 0.95rem;">
    La matrice completa dei 28 asset, esplorabile: passa sopra ogni cella per la correlazione esatta.
  </div>
  <div style="margin-top: 0.75rem;">
    <a href="/strumenti/mappa-correlazioni" style="display: inline-block; background: #1e3a8a; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600;">
      Apri la mappa →
    </a>
  </div>
</div>

## Limiti

**Correlazione in dollari.** Tutto è misurato dalla prospettiva di un investitore in dollari. Un investitore in euro vedrebbe correlazioni un po' diverse, perché il cambio euro-dollaro aggiunge una sua struttura. Il quadro generale (azionario molto correlato, rifugi poco) regge, ma i valori puntuali cambierebbero.

**Il periodo conta.** Vent'anni (2006-2026) sono dominati da eventi specifici: la crisi 2008, il lungo mercato rialzista post-2009, il COVID, l'inflazione 2022. La correlazione tra obbligazioni e azioni, in particolare, è stata storicamente negativa in questo periodo ma è stata *positiva* in altre epoche (anni '70, e in parte il 2022). Non è una costante di natura.

**Correlazione non è causalità né rischio completo.** Due asset scorrelati possono comunque perdere entrambi allo stesso tempo per motivi diversi. E la correlazione misura solo il co-movimento lineare medio: non cattura i rischi di coda, gli eventi rari, i cambi di regime.

**Il portafoglio min-correlazione è ottimizzato sul passato.** È stato scelto conoscendo le correlazioni realizzate 2006-2026. Non è una raccomandazione: è una dimostrazione che la bassa correlazione, storicamente, ha ridotto il rischio. Le correlazioni future saranno diverse.

**Bitcoin e India** hanno storia più corta e sono trattati separatamente o esclusi dalla matrice principale.

## Conclusioni

1. **La diversificazione geografica dentro l'azionario è in gran parte un'illusione.** Con correlazioni di 0.9-0.97 tra USA, World, Europa e settori, comprare "più mercati" azionari non riduce granché il rischio. È tutto, in larga misura, lo stesso trade.

2. **I veri diversificatori sono pochi e non azionari:** obbligazioni a lungo termine (le uniche con correlazione negativa), oro, materie prime. Sono loro a cambiare il profilo di rischio di un portafoglio, non l'ennesimo indice azionario.

3. **La diversificazione azionaria svanisce nei crolli di panico**, quando la correlazione media sale verso 0.9. Proprio quando servirebbe di più.

4. **Un portafoglio costruito solo per bassa correlazione ha eguagliato il mercato con metà del drawdown.** La diversificazione non serve a battere il mercato — serve a ottenere un rendimento simile prendendosi molto meno rischio, e a restare investiti quando gli altri vendono.

La sintesi meno intuitiva e più utile: "diversifica" non significa "compra tante azioni diverse". Significa mettere accanto all'azionario le poche cose che si muovono *diversamente* da esso. E accettare che, nei momenti di panico assoluto, anche la migliore diversificazione si stringe — motivo per cui il primo diversificatore resta sempre l'orizzonte temporale.

---

### Fonti e riproducibilità

- Prezzi mensili in USD da Yahoo Finance (ETF Adj Close = total return; future front-month per le materie prime; spot per Bitcoin).
- MSCI World: serie MSCI World Gross USD dal dataset MSCI.
- Codice della simulazione: [`scripts/correlazione-asset-class.py`](https://github.com/TylerD1917/smartmoneylab/blob/main/scripts/correlazione-asset-class.py).
- Matrici di correlazione complete (CSV), curve e statistiche: [`/charts/correlazione-asset-class/`](/charts/correlazione-asset-class/).

> Nota metodologica: correlazioni sui rendimenti mensili semplici. La matrice principale usa la finestra comune giugno 2006 - agosto 2026 (243 mesi) per 28 asset con storia piena; Bitcoin e India, più recenti, sono trattati separatamente. Il portafoglio a minima correlazione è selezionato per forza bruta su tutte le combinazioni di 5 asset, equal weight buy & hold, ed è ottimizzato in-sample (sul passato): serve come illustrazione, non come strategia operativa.

> Disclaimer: contenuto informativo ed educativo, non consulenza finanziaria. Le performance passate non sono indicative di quelle future. Le correlazioni storiche non si mantengono stabili nel tempo. Il portafoglio illustrato è un esercizio quantitativo retrospettivo, non una raccomandazione di investimento.
