---
title: "Il CAPE funziona anche fuori dagli USA? 24 mercati, 25 anni di dati"
description: "Il CAPE predice i rendimenti dei mercati non-USA (Europa, Giappone, emergenti)? Sì, ma solo confrontando ogni mercato con la propria storia, non con gli altri. E comprare i più economici perde contro l'indice."
pubDate: 2026-08-09
tags: ["cape", "valutazioni", "internazionale", "paesi-emergenti", "msci", "rendimenti-attesi", "pe10", "backtest", "asset-allocation"]
author: "SmartMoneyLab"
simulationSlug: "cape-internazionale-predice-rendimenti"
draft: false
---

## In breve

In un [articolo precedente](/posts/shiller-cape-predice-rendimenti/) ho verificato che lo **Shiller CAPE** predice i rendimenti futuri dell'S&P 500. Domanda naturale: vale anche fuori dagli Stati Uniti? Ho costruito un panel di **24 mercati** (Europa paese per paese, Giappone, Australia, Canada, più i grandi emergenti — Cina, India, Brasile, Corea, Taiwan, Sudafrica) con il CAPE per ogni mercato dal 1998 e i rendimenti MSCI in dollari, e ho misurato quanto ha reso ciascuno nei 5 e 10 anni successivi a ogni livello di valutazione. Cinque conclusioni, una controintuitiva.

1. **Confrontare il CAPE _tra_ paesi non funziona.** "Compra i paesi col CAPE più basso" è la strategia che quasi tutti immaginano. Sui dati non predice quasi nulla: il CAPE assoluto spiega lo **0.8%** della variabilità del rendimento a 10 anni (R² = 0.008). Un mercato a CAPE 12 non è un affare solo perché un altro sta a 25.

2. **Confrontare il CAPE di un mercato con la _propria_ storia funziona.** Rapportando il CAPE alla mediana storica di quello stesso mercato, il potere predittivo si moltiplica per sei (R² = 0.052 a 10 anni). Comprare un mercato quando è sotto il 70% della sua valutazione tipica ha reso in mediana **+7.7% annuo** nel decennio successivo, con **zero** periodi negativi; comprarlo quando è oltre il 130% ha reso **+3.5%**, con il 17% dei periodi in perdita.

3. **Il paese conta enormemente.** Il CAPE spiega il 64% dei rendimenti futuri in Giappone, il 63% in India, il 59% negli USA — ma praticamente zero in Australia, Canada, Spagna e Sudafrica. Non esiste una regola universale: esistono mercati in cui la valutazione conta e mercati in cui non ha contato.

4. **Giocare un paese contro gli USA non paga.** Ho testato l'idea più furba — comprare un mercato quando è economico rispetto agli USA più del solito. Nel periodo 2001-2026 quasi tutto ha perso contro gli USA a prescindere dalla valutazione: è l'era dell'eccezionalismo americano, che sommerge il segnale.

5. **Il portafoglio "compra i più economici" perde contro l'indice.** Un portafoglio attivo che ogni 2.5 anni compra i 4 mercati più a sconto rispetto alla loro storia rende **7.9% annuo** contro il **9.4%** di un semplice ACWI, con più rischio (drawdown −63% contro −55%). Il segnale è reale, ma nella sua versione concentrata non si trasforma in soldi.

6. **Per gli indici ampi che compri davvero, il segnale è persino più forte.** Sul MSCI World il CAPE ha spiegato il **77%** del rendimento a 10 anni. E oggi World, emergenti ed Europa sono tutti sopra la loro valutazione storica tipica: aspettarsi da qui rendimenti sotto la media è ragionevole.

## La domanda

Il CAPE — il rapporto prezzo/utili corretto per il ciclo, cioè il prezzo diviso la media decennale degli utili reali — è l'indicatore di valutazione più solido della letteratura: sull'S&P 500 predice davvero i rendimenti a lungo termine. Ma quasi tutta l'evidenza che il risparmiatore italiano incontra riguarda gli Stati Uniti. La domanda pratica è un'altra: se ho in portafoglio Europa, Giappone, emergenti, il CAPE mi dice qualcosa sui loro rendimenti attesi? E soprattutto: mi aiuta a decidere *dove* pesare di più?

L'intuizione diffusa è che sì, basti guardare la classifica dei CAPE e sovrappesare i mercati più economici. La letteratura accademica che studia il CAPE internazionale — [Keimling](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2736423), [Klement](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2088140), [Shiller e Jivraj](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3258404) — è più cauta, e su un punto è netta: il CAPE va confrontato con la storia di *ciascun* mercato, non tra mercati diversi. Ho voluto verificarlo sui dati, con i miei numeri.

## Dati e metodo

**CAPE per paese.** Serie semestrale del CAPE per 48 mercati e aree geografiche da [Research Affiliates](https://interactive.researchaffiliates.com/asset-allocation) (Asset Allocation Interactive), l'unico fornitore che pubblica la propria metodologia di calcolo. Copertura dal 1998 al 2026.

**Rendimenti.** Indici **MSCI Total Return lordo (Gross), in USD, mensili**, scaricati dal tool End-of-Day di [MSCI](https://www.msci.com/end-of-day-data-search). Scelta importante: sono *total return* (dividendi reinvestiti), non prezzo puro. È coerente con la regola di questo blog e con l'universo su cui RA calcola il CAPE (indici MSCI), quindi valutazione e rendimenti parlano la stessa lingua. Tutto in dollari per avere un metro comune tra paesi.

**Metodo.** Per ogni mercato e ogni data calcolo il rendimento **annualizzato** nei 5 e 10 anni successivi. Metto in relazione il CAPE di partenza con questi rendimenti forward, in tre versioni: CAPE **assoluto** (confronto tra paesi), CAPE **relativo alla mediana storica del paese** (confronto col proprio passato), e differenziale **rispetto agli USA**. Il pool comprende 24 mercati singoli; le regressioni per paese usano ciascun mercato separatamente.

**Universo.** Tier 1 (mercati sviluppati con storia lunga): USA, Giappone, Germania, Francia, Svizzera, Italia, Spagna, Olanda, Australia, Canada, più i quattro nordici (Svezia, Danimarca, Norvegia, Finlandia), Belgio, Austria. Tier 2 (grandi emergenti): Brasile, Cina, India, Corea, Taiwan, Sudafrica, Indonesia, Thailandia. Oltre ai singoli mercati analizzo separatamente gli **indici ampi** che il retail compra davvero: World (mercati sviluppati), Emergenti, Europa, Asia ex Giappone.

**I limiti, dichiarati in apertura.** Sono importanti e vanno tenuti a mente per tutto l'articolo:

- I rendimenti MSCI scaricati partono da **dicembre 2000**, quindi lo studio forward parte dal 2001 e **non include il picco dot-com del 2000** — proprio la sopravvalutazione più estrema. Perdiamo l'episodio più ghiotto.
- **25 anni** di storia e **finestre sovrapposte**: le osservazioni forward non sono indipendenti (finestre che si accavallano condividono gli stessi mesi), quindi gli R² per singolo paese vanno letti come indicativi, non come stime di precisione. La forza del panel sta nel mettere insieme molti mercati.
- La "mediana storica" di ogni mercato è calcolata sull'intero campione (*in-sample*): nella realtà, nel 2005 non conoscevi la mediana 1998-2026. Dove serve — nel portafoglio finale — uso invece solo dati passati.
- Rendimenti in **USD nominali**. L'inflazione USA 2001-2026 è comune a tutti i mercati in dollari, quindi sposta i livelli ma non la *relazione* CAPE-rendimento, che è ciò che ci interessa.

Script e dati sono nel repository ([`scripts/`](https://github.com/TylerD1917/smartmoneylab)), con il panel CAPE ricostruito e i rendimenti MSCI in `data/processed/`.

## Uso n.1 — il CAPE assoluto tra paesi: non funziona

Partiamo dall'idea intuitiva: mettere in fila i mercati per CAPE e comprare i più economici. Se funzionasse, le fasce di CAPE assoluto dovrebbero ordinare i rendimenti futuri. Non lo fanno.

### Tabella B — CAPE assoluto → rendimento forward (pool di 24 mercati)

**Forward 10 anni (annualizzato, USD gross TR):**

| CAPE assoluto | n | mediana | media | % periodi negativi |
|---|---:|---:|---:|---:|
| ≤ 10 | 44 | +5.3% | +6.9% | 0% |
| 10-15 | 113 | +6.4% | +6.8% | 6% |
| 15-20 | 169 | +6.1% | +6.9% | 4% |
| 20-25 | 137 | +6.4% | +6.5% | 9% |
| 25-30 | 84 | +6.4% | +6.4% | 11% |
| 30-40 | 41 | +4.2% | +5.2% | 7% |
| > 40 | 38 | +4.8% | +5.1% | 11% |

Le fasce sono sostanzialmente **piatte**: dal CAPE 10 al CAPE 30 il rendimento mediano a 10 anni resta inchiodato attorno al 6%. Solo agli estremi si intravede qualcosa (le fasce più care rendono un po' meno), ma è debole e rumoroso. In termini statistici, sul pool il CAPE assoluto ha una correlazione di appena **−0.09** con il rendimento a 10 anni: **R² = 0.008**. Praticamente nulla.

La ragione è quella che la letteratura ripete da anni: i mercati hanno CAPE "normali" strutturalmente diversi. Il Giappone ha vissuto per decenni a CAPE 40+, l'Austria e i mercati dell'Est a CAPE 8-12. Un CAPE di 12 in Giappone è un'occasione storica; lo stesso 12 in Austria è la norma. Confrontarli sulla stessa scala mescola mele e pere.

## Uso n.2 — il CAPE contro la propria storia: funziona

Cambiamo metro. Invece del CAPE assoluto, usiamo il **rapporto tra il CAPE attuale e la mediana storica di quel mercato**: 1.00 significa "valutazione tipica per questo paese", 0.70 significa "il 30% più economico del suo solito", 1.30 "il 30% più caro". Ora le fasce si ordinano.

### Tabella A — CAPE rispetto alla propria mediana storica → rendimento forward

**Forward 10 anni (annualizzato):**

| CAPE / mediana del paese | n | mediana | media | % periodi negativi |
|---|---:|---:|---:|---:|
| ≤ 0.70 (molto economico) | 75 | +7.7% | +8.5% | 0% |
| 0.70 - 0.85 | 94 | +9.3% | +9.2% | 1% |
| 0.85 - 1.00 | 150 | +6.5% | +6.8% | 3% |
| 1.00 - 1.15 | 94 | +5.4% | +6.3% | 5% |
| 1.15 - 1.30 | 52 | +5.9% | +6.0% | 8% |
| > 1.30 (molto caro) | 161 | +3.5% | +4.0% | 17% |

**Forward 5 anni (annualizzato):**

| CAPE / mediana del paese | n | mediana | media | % periodi negativi |
|---|---:|---:|---:|---:|
| ≤ 0.70 (molto economico) | 81 | +9.9% | +10.6% | 9% |
| 0.70 - 0.85 | 119 | +8.8% | +9.7% | 7% |
| 0.85 - 1.00 | 260 | +6.5% | +6.9% | 12% |
| 1.00 - 1.15 | 157 | +5.0% | +6.3% | 22% |
| 1.15 - 1.30 | 79 | +4.9% | +6.2% | 27% |
| > 1.30 (molto caro) | 170 | +4.7% | +6.3% | 32% |

Qui la storia è chiara e quasi monotòna. Comprare un mercato quando è a sconto rispetto alla propria storia ha reso di più e con meno rischio: nelle fasce economiche i periodi a 10 anni chiusi in perdita sono **zero o quasi**, in quella cara salgono al **17%**. Sulla stessa scala su cui il CAPE assoluto faceva R² = 0.008, il CAPE relativo alla propria mediana fa **R² = 0.052**: sei volte tanto. Non è tantissimo in assoluto — resta un segnale rumoroso — ma è la differenza tra "non dice nulla" e "dice qualcosa".

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/01_assoluto_vs_relativo.png" alt="Due pannelli affiancati. A sinistra il rendimento forward a 10 anni per fasce di CAPE assoluto: barre grigie sostanzialmente piatte attorno al 6%. A destra il rendimento per fasce di CAPE rapportato alla mediana del paese: barre che scendono chiaramente dalle valutazioni economiche a quelle care." />
  <figcaption>Lo stesso indicatore, due usi opposti. A sinistra il CAPE confrontato tra paesi: fasce piatte, nessun ordine. A destra il CAPE confrontato con la storia di ciascun mercato: le valutazioni a sconto rendono più di quelle care.</figcaption>
</figure>

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/02_bucket_relativo.png" alt="Grafico a barre con il rendimento mediano annualizzato a 5 e 10 anni per sei fasce di CAPE relativo alla mediana del paese. Le barre scendono dalle fasce molto economiche a quelle molto care, sia a 5 sia a 10 anni." />
  <figcaption>Più un mercato è economico rispetto alla sua storia, più ha reso nei 5 e 10 anni successivi. La relazione tiene su entrambi gli orizzonti.</figcaption>
</figure>

### Tabella D — la potenza dei tre segnali a confronto (pool, forward 10 anni)

| Segnale | correlazione | R² |
|---|---:|---:|
| CAPE assoluto (tra paesi) | −0.09 | 0.008 |
| CAPE / mediana del paese | −0.23 | 0.052 |
| Earnings yield (1/CAPE) | +0.08 | 0.006 |

## Gli indici ampi che il retail compra davvero

Fin qui ho ragionato su singoli paesi, ma il risparmiatore medio non compra la Borsa spagnola o quella coreana: compra un indice ampio — MSCI World, ACWI, emergenti, Europa. La domanda pratica è quindi se il CAPE dica qualcosa sui rendimenti attesi di *questi* indici. Abbiamo CAPE e rendimenti MSCI anche per loro, quindi possiamo testarlo direttamente. Per un indice ampio "CAPE rispetto alla propria storia" e "CAPE nel tempo" coincidono: c'è una sola serie, e osservare come il suo livello di valutazione ha anticipato il rendimento successivo è proprio il segnale che ci interessa.

### Tabella E — CAPE → rendimento forward, indici ampi

| Indice | n | corr 5 anni | R² 5 anni | corr 10 anni | R² 10 anni |
|---|---:|---:|---:|---:|---:|
| World (mercati sviluppati) | 28 | −0.44 | 0.20 | −0.88 | 0.77 |
| Mercati emergenti | 27 | −0.23 | 0.05 | −0.33 | 0.11 |
| Europa | 28 | −0.10 | 0.01 | −0.46 | 0.21 |
| Asia ex Giappone | 28 | −0.52 | 0.27 | −0.54 | 0.29 |

Il risultato più forte è il **World**: il suo CAPE ha spiegato il **77%** del rendimento dei 10 anni successivi (correlazione −0.88). È il segnale più netto di tutto lo studio — e riguarda proprio l'indice più comprato dai risparmiatori. Europa e Asia ex Giappone sono nella media (R² 0.21-0.29); gli emergenti restano deboli (0.11), coerentemente col fatto che il loro "CAPE normale" è cambiato molto nel tempo. Da tenere a mente il solito caveat: sono singole serie su 25 anni con finestre sovrapposte, quindi l'R² del World a 0.77 è tanto suggestivo quanto figlio di un unico grande ciclo (valutazioni alte pre-2008, crollo, ripresa).

Mettendo insieme i quattro indici, le fasce per valutazione relativa sono ancora più pulite che sui singoli paesi:

### Tabella F — indici ampi: CAPE vs propria mediana → rendimento forward

**Forward 10 anni (annualizzato):**

| CAPE / mediana dell'indice | n | mediana | media | % periodi negativi |
|---|---:|---:|---:|---:|
| ≤ 0.85 (economico) | 33 | +9.6% | +9.0% | 0% |
| 0.85 - 1.00 | 23 | +7.0% | +7.6% | 0% |
| 1.00 - 1.15 | 22 | +5.6% | +6.8% | 0% |
| ≥ 1.15 (caro) | 33 | +4.3% | +5.2% | 0% |

**Forward 5 anni (annualizzato):**

| CAPE / mediana dell'indice | n | mediana | media | % periodi negativi |
|---|---:|---:|---:|---:|
| ≤ 0.85 (economico) | 36 | +10.2% | +10.4% | 0% |
| 0.85 - 1.00 | 48 | +6.2% | +9.1% | 0% |
| 1.00 - 1.15 | 32 | +4.5% | +5.8% | 16% |
| ≥ 1.15 (caro) | 35 | +4.0% | +5.3% | 20% |

A dieci anni la relazione è perfettamente ordinata e **nessuna fascia ha chiuso in perdita** (in dollari, lordo): comprare un indice ampio quando è sotto l'85% della sua valutazione tipica ha reso in mediana +9.6% annuo, comprarlo sopra il 115% +4.3%. Più del doppio, per un decennio.

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/06_indici_ampi.png" alt="Grafico a barre del rendimento mediano annualizzato a 5 e 10 anni per gli indici ampi (World, Emergenti, Europa, Asia), per fasce di CAPE rispetto alla propria mediana. Le barre scendono nettamente dalle valutazioni economiche a quelle care." />
  <figcaption>Anche sugli indici ampi che il retail compra davvero, più l'indice è economico rispetto alla sua storia, più ha reso nei 5 e 10 anni successivi.</figcaption>
</figure>

### Dove siamo oggi

Vale la pena chiudere la sezione con una fotografia, perché è il tipo di lettura per cui il CAPE serve davvero: non "quando crollerà", ma "con che aspettative sto comprando".

### Tabella G — CAPE di luglio 2026 rispetto alla mediana storica

| Indice | CAPE oggi | mediana storica | rapporto |
|---|---:|---:|---:|
| World (mercati sviluppati) | 33.3 | 25.4 | 1.31 |
| Mercati emergenti | 22.9 | 15.3 | 1.50 |
| Europa | 21.3 | 18.6 | 1.15 |
| Asia ex Giappone | 25.0 | 16.6 | 1.50 |

Oggi **tutti** gli indici ampi stanno sopra la loro mediana storica: il World al 131% del suo tipico, l'Europa al 115%, emergenti e Asia al 150%. Letto con la Tabella F, significa aspettarsi da qui rendimenti più contenuti della media storica — non un crollo, semplicemente la parte bassa della distribuzione. È il monito che vale la pena tenere presente quando si versa ogni mese in un World a valutazioni che, sul suo stesso metro storico, sono elevate.

> **Strumento collegato.** Il [Predittore CAPE](/strumenti/predittore-cape-mercati) traduce tutto questo in una stima concreta: il rendimento annualizzato atteso a 5 e 10 anni per World, Europa, Emergenti, Cina, India e Giappone, in base al loro CAPE attuale, con banda di incertezza e affidabilità del segnale. I livelli di CAPE sono aggiornati periodicamente.

## Quanto conta il paese: nessuna regola universale

Il potere predittivo del CAPE non è uniforme: cambia radicalmente da mercato a mercato. La tabella sotto mostra, per ogni paese, quanto il suo CAPE ha spiegato il rendimento dei 10 anni successivi.

### Tabella C — potere predittivo per paese (forward 10 anni ~ CAPE del paese)

| Mercato | n | correlazione | R² |
|---|---:|---:|---:|
| Giappone | 28 | −0.80 | 0.64 |
| India | 22 | −0.80 | 0.63 |
| USA | 28 | −0.77 | 0.59 |
| Austria | 28 | −0.68 | 0.46 |
| Francia | 28 | −0.63 | 0.40 |
| Taiwan | 20 | −0.59 | 0.35 |
| Finlandia | 28 | −0.59 | 0.35 |
| Belgio | 28 | −0.58 | 0.33 |
| Olanda | 28 | −0.57 | 0.32 |
| Svizzera | 28 | −0.56 | 0.31 |
| Italia | 28 | −0.48 | 0.23 |
| Danimarca | 28 | −0.47 | 0.22 |
| Brasile | 22 | −0.37 | 0.14 |
| Norvegia | 28 | −0.37 | 0.13 |
| Corea | 20 | −0.35 | 0.13 |
| Indonesia | 27 | −0.34 | 0.12 |
| Germania | 28 | −0.22 | 0.05 |
| Svezia | 28 | −0.20 | 0.04 |
| Cina | 20 | +0.13 | 0.02 |
| Spagna | 28 | +0.12 | 0.01 |
| Canada | 28 | +0.11 | 0.01 |
| Thailandia | 27 | +0.11 | 0.01 |
| Sudafrica | 20 | −0.06 | 0.00 |
| Australia | 28 | +0.01 | 0.00 |

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/03_r2_per_paese.png" alt="Grafico a barre orizzontali dell'R quadro del CAPE nel predire il rendimento a 10 anni, paese per paese. In alto Giappone, India, USA sopra 0.55; in basso Australia, Sudafrica, Canada, Spagna, Cina vicini a zero." />
  <figcaption>Il CAPE predice molto in Giappone, India e USA; quasi nulla in Australia, Canada, Spagna, Cina. Nessuna regola universale.</figcaption>
</figure>

È lo stesso risultato che trovò Keimling: il CAPE spiega circa il 90% dei rendimenti in alcuni mercati e quasi niente in altri (per lui, Canada ~1%). Con soli 25 anni e finestre sovrapposte questi R² sono indicativi e in parte figli del periodo (dove il CAPE era alto prima del 2008 e tutto è crollato, la correlazione risulta forte anche per pura coincidenza di regime). Ma il messaggio qualitativo è robusto: **non c'è un'unica legge del CAPE valida ovunque.**

## E se li giochiamo l'uno contro l'altro?

Domanda naturale, e che mi era stata posta esplicitamente: se storicamente il CAPE della Spagna sta, poniamo, cinque punti sotto quello degli USA, e in un certo momento lo sconto è più ampio del solito, questo mi dice qualcosa sul fatto che la Spagna batterà gli USA nei 5-10 anni dopo? Ho costruito il segnale — differenziale (e rapporto) del CAPE di ogni mercato rispetto agli USA, de-medianizzato sulla storia di quel mercato — e l'ho testato contro il rendimento *relativo* (mercato meno USA).

La risposta è netta: **no, non in modo sfruttabile.** A 10 anni la correlazione tra "quanto è economico X vs USA rispetto al solito" e il successivo rendimento relativo X−USA è praticamente **zero** (−0.01). A 5 anni il segno si rovescia addirittura (i mercati più cari del solito vs USA hanno leggermente sovraperformato nel breve): è momentum, non valore, e comunque debolissimo.

### Il perché, in una tabella

| Quanto è economico X vs USA (rispetto al suo tipico) | n | rendimento relativo X−USA a 10 anni (mediana) |
|---|---:|---:|
| Molto più economico del solito | 11 | +7.3 pp/anno |
| Poco più economico | 68 | −3.9 pp/anno |
| Tipico | 141 | −6.4 pp/anno |
| Poco più caro | 172 | −6.2 pp/anno |
| Molto più caro del solito | 206 | −4.9 pp/anno |

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/04_relativo_vs_usa.png" alt="Grafico a barre del rendimento relativo mediano rispetto agli USA a 10 anni, per quintili di quanto un mercato è economico rispetto agli USA. Solo il quintile estremo economico è nettamente positivo; gli altri quattro sono tutti attorno a meno cinque punti l'anno." />
  <figcaption>Nel 2001-2026 quasi tutti i mercati hanno perso ~5 punti l'anno contro gli USA a prescindere dalla valutazione relativa. Solo il tail estremo-economico stacca (+7 pp), ma con appena 11 osservazioni.</figcaption>
</figure>

Il dato che salta all'occhio è che **quattro quintili su cinque perdono contro gli USA di circa cinque punti l'anno**, indipendentemente da quanto siano economici. È il ritratto quantitativo dell'eccezionalismo americano dell'ultimo quarto di secolo: gli USA hanno battuto quasi tutto, a qualunque valutazione relativa di partenza. L'unico gruppo che li stacca è il tail delle dislocazioni estreme (quando un mercato è economico vs USA molto più del solito), ma sono 11 osservazioni: un aneddoto statistico, non una strategia. È esattamente la storia dell'aneddoto UK-vs-USA del 2012, quando il CAPE diceva "compra Regno Unito, vendi USA" e gli USA hanno poi stravinto per un decennio.

## Il test finale: un portafoglio che compra i più economici

Le tabelle mostrano una relazione reale. Ma una relazione statistica non è un rendimento in tasca. Ho quindi costruito il test più diretto possibile: un portafoglio attivo che ogni **2.5 anni** (e in una seconda versione ogni **5 anni**) seleziona i **4 mercati più economici rispetto alla propria mediana storica**, li compra in parti uguali (25% ciascuno) e li tiene fino al ribilancio successivo. Nessuna tassa, nessun costo — condizioni volutamente ideali. Il segnale usa solo dati passati (mediana espansiva), quindi niente lookahead. Benchmark: **ACWI**, l'indice azionario globale, anch'esso in MSCI Gross TR USD.

### Portafoglio "value relativo" contro ACWI (2004-2026, lordo)

| | CAGR | Volatilità | Max drawdown | Calmar | Capitale finale (1$) |
|---|---:|---:|---:|---:|---:|
| Value relativo — ribil. 2.5 anni | 7.9% | 19.2% | −63.2% | 0.12 | 5.21x |
| Value relativo — ribil. 5 anni | 8.9% | 18.8% | −59.2% | 0.15 | 6.43x |
| **ACWI (indice globale)** | **9.4%** | **15.4%** | **−54.6%** | **0.17** | **7.10x** |

<figure>
  <img src="/charts/cape-internazionale-predice-rendimenti/05_portafoglio_vs_acwi.png" alt="Curve di crescita di 1 dollaro dal 2004 al 2026 per il portafoglio value relativo ribilanciato ogni 2.5 e 5 anni e per l'ACWI. Le tre curve procedono insieme fino al 2016, poi l'ACWI si stacca sopra le altre due." />
  <figcaption>Le tre curve viaggiano insieme fino al 2016, poi l'ACWI si stacca. Il portafoglio value relativo arriva a 5.2-6.4 volte il capitale, l'ACWI a 7.1 — con meno rischio.</figcaption>
</figure>

Il verdetto è impietoso e istruttivo: **il portafoglio dei "più economici" perde su tutta la linea** — meno rendimento e più rischio (volatilità e drawdown peggiori). Guardando le selezioni nel tempo si capisce perché: il portafoglio non compra quasi mai gli USA (raramente sono a sconto rispetto alla propria storia) e si carica cronicamente di Austria, Italia, Giappone, mercati "perennemente economici" che sono rimasti economici proprio perché hanno reso poco. Fino al 2016 tiene il passo dell'indice; poi il dominio delle grandi tech americane — che l'indice globale cattura e il portafoglio value evita per costruzione — apre la forbice.

È la lezione che i dati continuano a ripetere anche in questo blog (l'ho vista con la [leva](/posts/leva-raddoppia-rendimento-mercato/) e con lo [stock-picking delle megacap](/posts/azienda-piu-grande-batte-mercato/)): un segnale statisticamente vero, concentrato in un portafoglio, si scontra con la concentrazione del rischio e con il fatto che "economico" spesso vuol dire "economico per un motivo".

## Cosa porto a casa

1. **Il CAPE non è un metro tra paesi, è un metro dentro un paese.** La domanda giusta non è "quale mercato ha il CAPE più basso", ma "questo mercato è caro o economico rispetto a se stesso". Nella prima versione il segnale sparisce (R² 0.008), nella seconda emerge (R² 0.052).

2. **Anche nella versione giusta, è un segnale debole.** Un R² di 0.05 a 10 anni significa che la valutazione spiega una piccola parte del rendimento futuro: aiuta a inclinare le aspettative, non a fare previsioni. Le fasce economiche hanno reso di più *in mediana*, non *sempre*.

3. **Il paese conta più del segnale.** In alcuni mercati il CAPE ha predetto molto, in altri niente. Chiunque venda "il CAPE dice di comprare il paese X" sta ignorando che in metà dei mercati, storicamente, non avrebbe funzionato.

4. **Giocare i paesi l'uno contro l'altro, o contro gli USA, non ha pagato.** Nel quarto di secolo studiato l'eccezionalismo americano ha dominato ogni segnale di valore relativo. Il tail estremo-economico ha staccato, ma su pochissimi casi.

5. **Il segnale vero non batte l'indice.** Il portafoglio che compra i mercati più a sconto rispetto alla loro storia ha reso meno di un banale ACWI, con più rischio. Come sempre, la relazione statistica e il rendimento netto in tasca sono due cose diverse — e in mezzo c'è la concentrazione del rischio.

Il modo sensato di usare tutto questo non è ruotare tra paesi a caccia del più economico, ma tenerlo come **contesto sulle aspettative**: se un mercato che hai in portafoglio è molto sopra la sua valutazione storica tipica, è ragionevole aspettarsi da lì in avanti rendimenti più contenuti — non un crollo imminente, semplicemente un decennio probabilmente più magro. È lo stesso, prudente, uso che il CAPE consente a livello di singolo mercato: [ordine di grandezza, non market timing](/posts/shiller-cape-predice-rendimenti/).
