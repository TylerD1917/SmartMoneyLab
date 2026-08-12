# Bozza post Reddit — CAPE internazionale

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: il valore sta NEL post. Link al blog solo in fondo, come approfondimento + codice.

---

## Titolo (scegline uno)

- Ho testato su 24 mercati se il CAPE (Shiller) predice i rendimenti anche fuori dagli USA. Funziona, ma non come pensa il 99% delle persone
- Il CAPE dice davvero quali mercati compreranno di più? 24 paesi, 25 anni di dati, e un risultato controintuitivo

---

## Corpo del post

Premessa: non sono un consulente, faccio queste simulazioni per curiosità personale e le condivido. Dati e codice sono linkati in fondo.

Il CAPE (prezzo diviso la media decennale degli utili reali) predice i rendimenti dell'S&P 500. Domanda: vale anche per Europa, Giappone, emergenti? Ho costruito il CAPE per 24 mercati e i rendimenti MSCI in USD, e ho misurato quanto ha reso ciascuno nei 5 e 10 anni dopo ogni livello di valutazione (2001-2026).

**1. Confrontare il CAPE TRA paesi non funziona.** "Compra i mercati col CAPE più basso" spiega ~0% dei rendimenti a 10 anni (R² 0.008). Ogni mercato ha una sua valutazione "normale" diversa: un CAPE 12 in Giappone è un'occasione, lo stesso 12 in Austria è la norma.

**2. Confrontare il CAPE con la PROPRIA storia funziona.** Rapportandolo alla mediana storica di quel mercato, il potere predittivo si moltiplica per sei (R² 0.052 a 10 anni). Sugli indici ampi, rendimento mediano a 10 anni:

- comprato sotto 0.85 della sua valutazione tipica: +9.6% annuo (0% dei periodi in perdita)
- comprato sopra 1.15: +4.3% annuo

**3. Il paese conta più del segnale.** Il CAPE ha spiegato il 77% dei rendimenti a 10 anni del World, il 64% del Giappone, il 63% dell'India — ma ~0% di Australia, Canada, Spagna, Sudafrica. Non esiste una legge del CAPE valida ovunque.

**4. Giocare i paesi contro gli USA non ha pagato.** Il segnale "questo mercato è economico vs USA più del solito" non predice il rendimento relativo (corr ~0 a 10 anni). Nel 2001-2026 quasi tutto ha perso ~5 punti l'anno contro gli USA a prescindere dalla valutazione: eccezionalismo americano.

**5. Il test finale: un portafoglio che compra i più economici.** Ogni 2.5 anni compra i 4 mercati più a sconto rispetto alla loro storia (25% ciascuno, lordo, no tasse). Risultato vs un banale ACWI: **+7.9% annuo contro +9.4%**, con drawdown peggiore (−63% vs −55%). Il segnale è reale ma, concentrato, perde contro l'indice — perché "economico" spesso vuol dire "economico per un motivo", e la concentrazione aggiunge rischio.

**Dove siamo oggi** (CAPE vs la propria mediana storica): World 1.31×, Emergenti 1.50×, Europa 1.15×. Tutti sopra la loro valutazione tipica → aspettative di rendimento più contenute da qui, non un crollo.

**Cosa mi porto a casa.** Il CAPE non è un metro per scegliere TRA mercati, è un metro per capire se UN mercato è caro o economico rispetto a se stesso. E anche così è un segnale debole: utile per calibrare le aspettative di lungo periodo, inutile come market timing o come rotazione geografica.

Caveat: 25 anni, finestre sovrapposte (osservazioni non indipendenti), rendimenti USD nominali, dati dal 2001 (quindi senza il picco dot-com). Tutti i dettagli e i limiti nell'articolo.

Analisi completa, tabelle, grafici e codice open: [link]. Ho anche fatto un piccolo strumento che stima il rendimento atteso a 5 e 10 anni per 6 mercati in base al CAPE attuale: [link strumento].
