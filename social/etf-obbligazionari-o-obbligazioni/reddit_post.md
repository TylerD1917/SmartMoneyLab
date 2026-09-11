# Bozza post Reddit — ETF obbligazionario o obbligazioni a scadenza

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: valore nel post, link soft in fondo, niente self-promo secca.

---

## Titolo (scegline uno)

- ETF obbligazionario o comprare le obbligazioni e tenerle a scadenza? 64 anni di dati: a parità di duration NON sono la stessa cosa (e il perché non è quello che pensate)
- "Tanto a parità di duration convergono": ho testato ETF a duration costante vs obbligazioni tenute a scadenza su 64 anni. Non convergono a zero, e conta il regime dei tassi

---

## Corpo del post

Premessa: lo faccio per curiosità e per falsificare un luogo comune, dati e codice open, linko in fondo.

"Meglio un ETF obbligazionario o comprare i titoli e tenerli a scadenza?" La risposta che si legge di solito è: "a parità di duration è la stessa cosa, i rendimenti convergono". Ho provato a verificarlo coi numeri: 64 anni di Treasury USA (1962-2026), tasso 10Y (Shiller+FRED) e tasso a breve (Fed Funds) per le cedole. Due gambe costruite dagli stessi tassi, così l'unica differenza è il **meccanismo**: un indice a **duration costante** (l'ETF, che rinnova di continuo e non porta mai a scadenza) contro un **titolo par tenuto a scadenza**, cedole reinvestite al breve, rinnovato. Confronto a **duration allineata** (~8 anni, ≈ la duration di un ETF 7-10 anni come IEF: 6,9), validato contro l'IEF reale (correlazione mensile 0,99).

**1. Non sono la stessa cosa, e non per caso.** L'ETF tiene la duration **costante** → esposizione ai tassi permanente. Il titolo singolo, tenuto a scadenza, ha una duration che **decade verso zero** → ti blocca il rendimento all'acquisto. "Stessa duration" e "tenuto a scadenza" non stanno insieme più di un istante.

**2. A parità di duration, l'ETF ha reso un filo di più:** mediana **+0,62%/anno** sulle finestre di 10 anni, **+0,73%** su quelle di 20. Piccolo ma sistematico. La dispersione si restringe allungando l'orizzonte, ma il divario mediano **non va a zero**.

**3. Il tranello della duration.** Se confrontate l'ETF con un Treasury a **10 anni** (duration ~8, più lungo dell'ETF) il vantaggio sembra ~+1%. Ma **un terzo di quel numero è solo il disallineamento di duration**, non un vero vantaggio. È l'errore più comune in questi confronti.

**4. Chi vince dipende dai tassi.** In un ventennio di tassi **in salita** vince chi tiene a scadenza (l'ETF incassa le perdite di prezzo: è successo nel **2022**, IEF ~−15%); in uno di tassi **in calo** vince l'ETF. La mediana pro-ETF è figlia dei 40 anni di tassi calanti (1981-2020), un vento in poppa oggi in gran parte esaurito.

**5. Il caso peggiore, simmetrico.** Comprando nel momento storico peggiore: chi ha preso l'ETF poco prima di una risalita (ingresso 1973) ha reso a 10 anni ~3,7 punti/anno in meno della scadenza (−29% sul montante); chi ha preso i titoli sul picco dei tassi (1978-79) si è lasciato sfuggire fino a ~2-2,7 punti/anno (fino a +44% sul montante a 20 anni). Il tempo attenua il divario **annuo**, ma lo **amplifica** in euro (si compone più a lungo).

**Un paio di caveat onesti.** Baseline lorda: il TER dell'ETF (~0,15% per IEF) è l'unico svantaggio permanente, e va aggiunto a parte. Dall'altro lato, la ricostruzione lunga **sottostima** l'ETF reale di ~0,5%/anno perché non cattura il roll-down (curva a un solo punto): quindi il piccolo vantaggio dell'ETF, se mai, è prudente.

**E i BTP?** La meccanica è identica: un ETF di BTP tiene la duration costante, un BTP singolo tenuto a scadenza la lascia decadere e ti blocca cedole e rimborso a 100. È il motivo per cui molti qui preferiscono i singoli titoli: comprano **certezza**, non rendimento atteso.

Morale: la scelta non è "quale rende di più", ma **certezza** (titolo/BTP a scadenza) contro **esposizione costante + comodità** (ETF). Metodo completo, grafici e codice qui: [link articolo]. Critiche al metodo molto ben accette — in particolare sull'ipotesi di reinvestimento delle cedole al tasso a breve e sulla ricostruzione del 10Y lungo.
