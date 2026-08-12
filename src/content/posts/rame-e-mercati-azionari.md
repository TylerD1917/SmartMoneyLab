---
title: "Il rame (Dr. Copper) anticipa i crolli di Borsa? 34 anni di dati"
description: "Si dice che quando il prezzo del rame crolla, il mercato azionario stia per crollare. L'ho verificato sull'S&P 500 dal 1992 al 2026: il mito regge quasi solo sul 2008."
pubDate: 2026-08-10
tags: ["rame", "dr-copper", "materie-prime", "commodity", "sp500", "mercati-azionari", "recessione", "indicatori-anticipatori", "event-study"]
author: "SmartMoneyLab"
simulationSlug: "rame-e-mercati-azionari"
draft: false
---

## In breve

Il rame è soprannominato **"Dr. Copper"**, il metallo con "un dottorato in economia": siccome serve in edilizia, industria ed elettronica, si dice che il suo prezzo senta la salute dell'economia prima di tutti — e che un suo crollo anticipi un crollo dei mercati azionari. L'ho verificato sui dati: prezzo del rame (serie mensile 1992-2026) contro l'S&P 500 in total return. Tre risultati.

1. **I crolli del rame sono rari.** Con la soglia "−20% in 3 mesi" ci sono stati **5 episodi** in 34 anni (1996, 2007, 2008, 2011, 2022). Con "−25% in 3 mesi", solo due: 2008 e 2022.

2. **Dopo un crollo del rame, il mercato è salito più della media.** Nei 12 mesi successivi l'S&P 500 ha reso in media **+19.5%**, contro un +11.6% di un mese qualsiasi. Togliendo il 2008, ha battuto la media a ogni orizzonte, anche a 3 mesi. Storicamente il rame che crolla è stato più vicino a un minimo d'acquisto che a un allarme.

3. **Su tutti i 411 mesi, il rame non predice nulla.** La correlazione tra la variazione del rame (a 3 o 6 mesi) e il rendimento azionario successivo è vicina a **zero** (R² sotto 0.01). L'unico caso in cui rame e Borsa sono crollati insieme è il 2008 — ma insieme, non uno prima dell'altro.

## La leggenda di "Dr. Copper"

L'idea è intuitiva e per questo circola da decenni: il rame è ovunque nell'economia reale — cavi, motori, case, auto elettriche, data center. Se la domanda di rame cala, forse è perché l'economia sta rallentando, e quindi il suo prezzo sarebbe un **indicatore anticipatore** dei mercati azionari. Da qui il soprannome "Dr. Copper" e la frase ricorrente: *"quando il rame crolla, scappa dalla Borsa"*.

È una di quelle affermazioni che suonano sagge e non vengono quasi mai verificate. Facciamolo.

## Dati e metodo

**Rame**: prezzo mensile del rame dal database [FRED](https://fred.stlouisfed.org/series/PCOPPUSDM) (Federal Reserve di St. Louis), gennaio 1992 - giugno 2026, 414 osservazioni.

**Mercato azionario**: S&P 500 in **total return** (con dividendi reinvestiti), ricostruito dal dataset [Shiller](http://www.econ.yale.edu/~shiller/data.htm). Uso il total return perché è il rendimento reale che incassa un investitore; è la regola di questo blog.

**Definizione di "crollo"**: un calo del prezzo del rame di almeno il **20% in 3 mesi** (con la variante −20% in 6 mesi e −25% in 3 mesi come controllo di robustezza). Due eventi ravvicinati contano come uno solo (cooldown di 12 mesi).

**Cosa misuro**: il rendimento total return dell'S&P 500 nei **3, 6 e 12 mesi successivi** a ogni crollo del rame, confrontato con il rendimento medio a partire da un mese qualsiasi del periodo (la "baseline"). Poi, separatamente, la relazione continua tra la variazione del rame e il rendimento azionario successivo su tutti i mesi.

Lo script completo è nel repository ([`scripts/rame-e-mercati-azionari.py`](https://github.com/TylerD1917/smartmoneylab)).

## Cosa è successo dopo un crollo del rame

Ecco i cinque crolli del rame (−20% in 3 mesi) e cosa ha fatto l'S&P 500 dopo ciascuno.

| Crollo del rame | S&P 500 +3 mesi | +6 mesi | +12 mesi |
|---|---:|---:|---:|
| Luglio 1996 | +9.5% | +20.2% | +46.5% |
| Gennaio 2007 | +3.2% | +7.7% | −1.4% |
| Ottobre 2008 | −9.9% | −11.0% | +13.5% |
| Ottobre 2011 | +8.3% | +16.0% | +21.6% |
| Luglio 2022 | −4.4% | +2.1% | +17.2% |
| **Media** | **+1.3%** | **+7.0%** | **+19.5%** |
| **Media senza il 2008** | **+4.2%** | **+11.5%** | **+20.9%** |
| *Baseline (mese qualsiasi)* | *+2.7%* | *+5.6%* | *+11.6%* |

<figure>
  <img src="/charts/rame-e-mercati-azionari/01_dopo_crollo_vs_baseline.png" alt="Grafico a barre che confronta il rendimento total return dell'S&P 500 a 3, 6 e 12 mesi: mese qualsiasi, dopo un crollo del rame, e dopo un crollo del rame escludendo il 2008. Le barre 'dopo un crollo' sono uguali o superiori alla baseline a 6 e 12 mesi." />
  <figcaption>Dopo un crollo del rame, l'S&P 500 non è sceso: a 6 e 12 mesi ha reso quanto o più della media. Escludendo il 2008, ha battuto la media a ogni orizzonte.</figcaption>
</figure>

Il quadro è l'opposto della leggenda. A 12 mesi il mercato ha reso in media **+19.5%**, quasi il doppio della baseline. L'unico caso di vera debolezza azionaria è il **2008** — e solo nel breve termine (a 12 mesi anche lì l'S&P era già a +13.5%). Per giunta il rame è crollato a ottobre 2008, in piena crisi, quando l'S&P era già dentro il suo mercato orso da un anno: non ha anticipato niente, è caduto insieme a tutto il resto.

<figure>
  <img src="/charts/rame-e-mercati-azionari/02_per_evento_3m.png" alt="Grafico a barre del rendimento dell'S&P 500 nei 3 mesi dopo ciascuno dei cinque crolli del rame. Solo la barra del 2008 è nettamente negativa; le altre sono attorno o sopra la linea della baseline." />
  <figcaption>Rendimento dell'S&P 500 nei 3 mesi dopo ciascun crollo del rame. Solo il 2008 mostra una debolezza marcata; il 2022 un calo lieve, poi rimbalzato (+17% a 12 mesi).</figcaption>
</figure>

I controlli di robustezza confermano: con la soglia più severa (−25% in 3 mesi, solo 2008 e 2022) la media a 12 mesi è comunque **+15.3%**; con −20% in 6 mesi (7 eventi) è **+16.4%**. In tutti i casi, sopra la baseline.

## E se guardiamo tutti i mesi, non solo i crolli?

Cinque o sette eventi sono pochi per trarre conclusioni robuste. Allora ribalto la domanda e uso **tutti i 411 mesi**: la variazione del rame in un dato momento è legata al rendimento azionario dei mesi seguenti?

La risposta è netta: **no**. La correlazione tra la variazione del rame (a 3 o 6 mesi) e il rendimento total return dell'S&P 500 nei 3, 6 e 12 mesi successivi è sempre vicina a zero (R² tra 0.001 e 0.011). In pratica, sapere come si è mosso il rame non aiuta a prevedere dove andrà il mercato.

Se dividiamo i mesi in cinque fasce a seconda di quanto è salito o sceso il rame nei tre mesi precedenti, il rendimento azionario successivo è sostanzialmente piatto tra le fasce — e la fascia "rame in forte calo" è tra le migliori per l'azionario a 12 mesi (+13.8% mediano), non tra le peggiori.

<figure>
  <img src="/charts/rame-e-mercati-azionari/03_bucket_rame_sp.png" alt="Grafico a barre del rendimento mediano dell'S&P 500 a 12 mesi per cinque fasce di variazione del rame a 3 mesi. Le barre sono simili tra loro; la fascia 'rame in forte calo' non è più bassa delle altre." />
  <figcaption>Rendimento dell'S&P 500 a 12 mesi per fascia di variazione del rame. Piatto: il rame che scende non è seguito da un mercato più debole.</figcaption>
</figure>

## Perché il mito esiste lo stesso

Se i dati sono così chiari, perché la leggenda sopravvive? Per tre motivi.

Il primo è il **2008**. Un singolo evento drammatico, in cui rame e azioni sono crollati contemporaneamente, ha lasciato un'impressione fortissima e ha "confermato" la storia a chi già ci credeva. Ma un caso non è una regola, e in quel caso il rame non ha anticipato nulla: ha reagito alla stessa recessione.

Il secondo è la **confusione tra coincidente e anticipatore**. Il rame è davvero legato al ciclo economico: nelle recessioni la sua domanda cala e il prezzo scende. Ma questo succede *durante* la recessione, insieme al calo degli utili e delle azioni — non mesi prima. Un termometro che segna la febbre mentre hai la febbre non è una previsione.

Il terzo è che **il rame ha una vita propria**: la sua offerta dipende da miniere, scioperi, decisioni di pochi grandi produttori, scorte cinesi, speculazione. Molti dei suoi crolli non c'entrano niente con la domanda finale — sono shock di offerta o di sentiment sul metallo, che non hanno alcun motivo di anticipare l'S&P 500.

## Cosa porto a casa

1. **"Quando il rame crolla, scappa dalla Borsa" non regge ai dati.** Nei 34 anni analizzati, dopo un crollo del rame l'S&P 500 è salito più della media, non meno.

2. **Il mito vive di un solo evento, il 2008** — dove peraltro il rame è caduto *insieme* al mercato, non prima.

3. **Come indicatore anticipatore, il rame non funziona.** Su tutti i mesi la relazione con i rendimenti azionari futuri è praticamente nulla.

4. **Diffida degli indicatori "che suonano intelligenti".** Rame, prezzo del petrolio, curva dei tassi presa da sola: tante narrazioni sagge non sopravvivono a un test sui dati. È il motivo per cui vale la pena verificarle prima di lasciarle guidare le proprie scelte.

Questo non significa che il rame sia inutile da osservare — racconta molto sull'economia *in tempo reale*. Significa solo che non è la sfera di cristallo dei mercati azionari che la leggenda promette.
