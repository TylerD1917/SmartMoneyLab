# Bozza post Reddit — CAPE

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: il valore sta NEL post. Il link al blog va solo in fondo, come "approfondimento + codice". Niente drop del link secco.

---

## Titolo (scegline uno)

- Ho testato su 145 anni di dati se lo Shiller CAPE predice davvero i rendimenti del mercato. Risultati (e un caveat che nessuno racconta)
- Comprare azioni quando il CAPE è "carissimo" (>40, come oggi): cosa dicono 145 anni di dati a 5, 10 e 20 anni

---

## Corpo del post

Premessa: non sono un consulente, faccio queste simulazioni per curiosità personale e le condivido. Tutti i dati e il codice sono open, linko in fondo.

Lo Shiller CAPE (prezzo diviso la media decennale degli utili reali) è la metrica più citata per dire "il mercato è caro". Ma predice davvero i rendimenti futuri? L'ho testato sull'S&P 500 dal 1881 al 2026 (dati Shiller), misurando cosa ha reso il mercato a 5, 10 e 20 anni dopo ogni livello di CAPE, in termini reali.

**Il CAPE predice, e il segnale si rafforza con l'orizzonte.** Correlazione tra CAPE e rendimento reale successivo:

- a 5 anni: −0.35
- a 10 anni: −0.49
- a 20 anni: −0.57 (R² 0.32: il CAPE iniziale "spiega" un terzo della varianza del rendimento reale a 20 anni)

**Le fasce di valutazione contano moltissimo.** Rendimento reale annualizzato mediano a 10 anni:

- CAPE <15 (economico): +9.5%
- CAPE 15-20: +6.2%
- CAPE 25-30: +5.5%
- CAPE 30-40: +0.4%
- CAPE >40 (carissimo): −3.5%, con il 100% dei periodi a 10 anni in negativo reale

**Ma a 20 anni il tempo cambia le carte.** Anche partendo da CAPE >40, a vent'anni il rendimento reale torna positivo (+3.7% annuo, nessun periodo negativo nella storia). Il lungo periodo salva. MA non gratis: +3.7% reale contro +8.6% di chi ha comprato economico significa, su 20 anni composti, arrivare a **meno della metà** del capitale reale (1€ → 2.1€ contro 5.2€). La valutazione di partenza non decide *se* guadagni sul lunghissimo periodo, decide *quanto*.

**Il punto più importante: il CAPE NON è market timing.** Predice i rendimenti medi su 10-20 anni, non *quando* arriva un eventuale calo. Il CAPE è sopra 30 dal 2017 e il mercato è raddoppiato. Chi fosse uscito "perché caro" avrebbe perso uno dei rialzi più forti di sempre. Serve a calibrare le aspettative di lungo periodo (tasso di prelievo, obiettivi), non a entrare/uscire.

Oggi il CAPE è attorno a 40 — livello toccato solo prima del 2000 e nel 2021. Non è una previsione di crollo, è un ordine di grandezza sui rendimenti reali attesi del prossimo decennio.

Caveat onesto: la fascia >40 ha solo 22 mesi di dati (2000 e 2021), quindi quel "−3.5% / 100% negativo" è robusto come direzione ma fragile come precisione. E le finestre sono sovrapposte, quindi le osservazioni sono autocorrelate.

Analisi completa con scatter, tutte le tabelle reale+nominale e il codice Python riproducibile qui: [link articolo]. C'è anche un simulatore dove imposti un CAPE e vedi i range storici.

**Domanda per voi**: usate il CAPE (o altre metriche di valutazione) per regolare le vostre aspettative di rendimento a lungo termine, o lo considerate rumore inutile per un investitore buy&hold?

---

## Note operative
- Allega 1-2 grafici (lo scatter CAPE vs fwd 10y e la tabella per fascia): i post con immagine performano meglio.
- Rispondi ai commenti nelle prime 2 ore (l'algoritmo Reddit premia l'attività iniziale).
- Se ti accusano di self-promo: il link è in fondo, il valore è nel post. Rispondi che il codice è open e possono replicare.
- NON crosspostare lo stesso testo su più sub lo stesso giorno (spam filter). Distanzia di qualche giorno.
