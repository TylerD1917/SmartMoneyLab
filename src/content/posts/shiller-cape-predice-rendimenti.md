---
title: "Lo Shiller CAPE predice i rendimenti del mercato? 145 anni di dati"
description: "Il CAPE di Shiller predice davvero i rendimenti dell'S&P 500 a 5, 10 e 20 anni? Analisi 1881-2026, reale e nominale, con il caveat che nessuno racconta: comprare caro non ti rovina, ti dimezza."
pubDate: 2026-07-16
tags: ["cape", "shiller", "valutazioni", "sp500", "rendimenti-attesi", "pe10", "lungo-periodo", "backtest"]
author: "SmartMoneyLab"
simulationSlug: "shiller-cape-predice-rendimenti"
draft: false
---

## In breve

Il rapporto prezzo/utili corretto per il ciclo — lo **Shiller CAPE** (o PE10: prezzo diviso la media decennale degli utili reali) — è la metrica di valutazione più citata quando qualcuno vuole dire che "il mercato è caro". Ma è davvero utile? Predice i rendimenti futuri, o è solo un numero che fa scena? L'ho testato su **145 anni di dati** (1881-2026), misurando quanto ha reso l'S&P 500 nei 5, 10 e 20 anni successivi a ogni livello di CAPE, sia in termini reali sia nominali. Quattro conclusioni.

1. **Il CAPE predice, e il segnale si rafforza con l'orizzonte.** La correlazione con il rendimento reale successivo è −0.35 a 5 anni, −0.49 a 10 anni, **−0.57 a 20 anni**. A vent'anni, il livello di CAPE da cui parti "spiega" circa un terzo della variabilità del rendimento reale (R² = 0.32). Per una singola metrica è molto.

2. **Le fasce raccontano una storia quasi monotòna.** Comprare a CAPE sotto 15 (economico) ha reso storicamente **+9.5% reale annuo** nei 10 anni successivi. Comprare a CAPE sopra 40 (carissimo) ha reso **−3.5% reale annuo**, con il 100% dei periodi a 10 anni in territorio negativo. Sono oltre 13 punti percentuali di differenza l'anno, per un decennio.

3. **Ma il tempo cambia le carte.** A 20 anni, perfino chi ha comprato a CAPE sopra 40 è tornato in positivo reale (+3.7% annuo, zero periodi negativi). L'orizzonte lungo ha salvato tutti. **Solo che non gratis**: +3.7% reale contro +8.6% di chi ha comprato economico significa, su vent'anni composti, arrivare a **meno della metà** del capitale reale. Il CAPE alto non decide *se* guadagni sul lunghissimo periodo, decide *quanto*.

4. **Il CAPE non è market timing.** Predice l'*ordine di grandezza* dei rendimenti su orizzonti lunghi, non *quando* arriva l'eventuale calo. Il mercato è "caro" per il CAPE da anni e ha continuato a salire. Chi lo usa per uscire dal mercato lo usa male.

## La domanda

Molte metriche promettono di anticipare i rendimenti del mercato, e la maggior parte offre segnali deboli o nulli. Il CAPE è tra le poche che, nella letteratura accademica, mostra un potere predittivo statisticamente robusto — almeno sugli orizzonti lunghi. È l'indicatore reso celebre da Robert Shiller, premio Nobel, e usato per argomentare la sopravvalutazione del mercato prima del crollo del 2000.

L'idea è semplice: invece di dividere il prezzo per gli utili dell'ultimo anno (che oscillano molto col ciclo economico), lo si divide per la **media decennale degli utili reali**. Questo "liscia" il denominatore e restituisce una misura di valutazione più stabile. La tesi è che quando il CAPE è alto — cioè paghi molto per ogni dollaro di utili normalizzati — i rendimenti futuri tendono a essere bassi, e viceversa.

Non l'ho mai verificato in prima persona sui dati. Questo articolo lo fa, con la massima trasparenza possibile: tutti i numeri, reali e nominali, su tutti e tre gli orizzonti.

## Dati e metodo

**CAPE**. Serie mensile del PE10 dal dataset [Shiller](http://www.econ.yale.edu/~shiller/data.htm), che parte dal 1881, estesa con la serie [multpl](https://www.multpl.com/shiller-pe/table/by-month) per i mesi più recenti (2024-2026). Le due fonti coincidono nell'intervallo di sovrapposizione.

**Rendimenti**. Total return dell'S&P 500 ricostruito dalla stessa fonte Shiller (prezzo mensile più dividendo prorata), in due versioni: **nominale** (grezzo) e **reale** (deflazionato per l'indice dei prezzi al consumo). Per i mesi più recenti, dove il dato ufficiale del dividendo non è ancora disponibile, ho esteso il dividendo con un rendimento cedolare dell'1.8% annuo e il CPI con un'inflazione del 2.5% annuo. Sono approssimazioni dichiarate e conservative, che toccano solo l'ultima coda della serie.

**Orizzonti**. Da ogni mese calcolo il rendimento **annualizzato** (CAGR) dell'S&P 500 nei 5, 10 e 20 anni successivi. Poiché servono i dati "futuri", i mesi più recenti non hanno un forward completo: l'ultimo mese con un forward a 20 anni è del 2006, quello a 10 anni del 2016.

**Fasce**. Ho diviso il CAPE in sei fasce: sotto 15 (economico), 15-20, 20-25, 25-30, 30-40, sopra 40 (carissimo). Il CAPE storico va da un minimo di 4.8 (1920) a un massimo di 44.2 (picco dot-com 1999 e picco 2021). La media storica è 17.7, la mediana 16.6.

**Periodo**. Gennaio 1881 - aprile 2026, 1744 osservazioni mensili. Copre la Grande Depressione, le due guerre, la stagflazione anni '70, le bolle del 2000 e del 2021.

Lo script completo è nel repository ([`scripts/shiller-cape-predice-rendimenti.py`](https://github.com/TylerD1917/smartmoneylab/blob/main/scripts/shiller-cape-predice-rendimenti.py)); panel mensile e statistiche per fascia sono in [`/charts/shiller-cape-predice-rendimenti/`](/charts/shiller-cape-predice-rendimenti/).

## Dove siamo oggi

<figure>
  <img src="/charts/shiller-cape-predice-rendimenti/01_context_cape_timeline.png" alt="Serie storica dello Shiller CAPE dal 1881 al 2026, con linee orizzontali alle soglie delle fasce e la media storica. Sono visibili i picchi del 1929, del 2000 e del 2021." />
  <figcaption>Lo Shiller CAPE dal 1881. I tre grandi picchi sono il 1929 (crollo successivo), il 2000 (dot-com) e il 2021. Oggi il CAPE è di nuovo attorno a 40, in piena zona "carissimo".</figcaption>
</figure>

Il CAPE oggi è circa 40 — un livello toccato solo altre due volte in 145 anni: alla vigilia del crollo dot-com e nel 2021. È la fascia storicamente più sfavorevole ai rendimenti futuri. Questo non è un allarme (il CAPE non fa timing, ne parlo alla fine), ma è il contesto in cui va letto tutto ciò che segue.

## Il grafico che conta: CAPE contro rendimento futuro

Questo è il cuore dell'analisi. Ogni punto è un mese: sull'asse orizzontale il CAPE al momento dell'ipotetico investimento, sull'asse verticale il rendimento reale annualizzato nei 10 anni successivi.

<figure>
  <img src="/charts/shiller-cape-predice-rendimenti/02_scatter_cape_vs_fwd10y_real.png" alt="Scatter plot con il CAPE sull'asse x e il rendimento reale annualizzato a 10 anni sull'asse y. La nuvola di punti scende chiaramente da sinistra verso destra, con una retta di regressione negativa e R quadro 0.24." />
  <figcaption>CAPE contro rendimento reale annualizzato a 10 anni, 1881-2026. La pendenza negativa è netta: più alto è il CAPE quando compri, più basso è il rendimento reale del decennio successivo. R² = 0.24.</figcaption>
</figure>

La nuvola scende da sinistra a destra. Non è una retta perfetta — c'è molta dispersione, il mercato non è deterministico — ma la tendenza è inequivocabile e la retta di regressione ha una pendenza di −0.38 punti percentuali di rendimento reale per ogni punto di CAPE in più. A 20 anni la relazione è ancora più pulita:

<figure>
  <img src="/charts/shiller-cape-predice-rendimenti/09_scatter_cape_vs_fwd20y_real.png" alt="Scatter plot del CAPE contro il rendimento reale annualizzato a 20 anni. La nuvola è più compatta attorno alla retta rispetto al grafico a 10 anni, con R quadro 0.32." />
  <figcaption>CAPE contro rendimento reale annualizzato a 20 anni. La nuvola è più stretta attorno alla retta: su orizzonte lungo il CAPE predice meglio. R² = 0.32.</figcaption>
</figure>

La correlazione cresce sistematicamente con l'orizzonte:

| Orizzonte | Correlazione (reale) | R² (reale) | Correlazione (nominale) |
|---|---|---|---|
| 5 anni | −0.35 | 0.12 | −0.40 |
| 10 anni | −0.49 | 0.24 | −0.51 |
| 20 anni | **−0.57** | **0.32** | −0.43 |

Sul reale il segnale è massimo a 20 anni. Da notare che sul nominale la correlazione a 20 anni *scende* (−0.43): su orizzonti lunghissimi le differenze di inflazione tra un'epoca e l'altra confondono la relazione nominale, mentre quella reale resta pulita. È il motivo per cui il framing "corretto" del CAPE è in termini reali.

## Le fasce: tutti i numeri, reali e nominali

Ecco il quadro completo. Prima i rendimenti **reali** annualizzati mediani, poi i **nominali**. Ho incluso il numero di mesi in ciascuna fascia e l'intervallo di CAPE coperto.

### Rendimenti reali annualizzati (mediana)

| Fascia CAPE | Mesi | 5 anni | 10 anni | 20 anni |
|---|---|---|---|---|
| <15 (economico) | 691 | +9.4% | +9.5% | +8.6% |
| 15-20 (equo-basso) | 513 | +6.5% | +6.2% | +5.3% |
| 20-25 (equo-alto) | 261 | +5.9% | +4.9% | +2.8% |
| 25-30 (caro) | 147 | +5.4% | +5.5% | +6.8% |
| 30-40 (molto caro) | 110 | +2.5% | +0.4% | +4.8% |
| >40 (carissimo) | 22 | −4.5% | −3.5% | +3.7% |

### Rendimenti nominali annualizzati (mediana)

| Fascia CAPE | Mesi | 5 anni | 10 anni | 20 anni |
|---|---|---|---|---|
| <15 (economico) | 691 | +13.3% | +13.7% | +11.6% |
| 15-20 (equo-basso) | 513 | +7.7% | +8.1% | +7.6% |
| 20-25 (equo-alto) | 261 | +8.3% | +7.5% | +8.3% |
| 25-30 (caro) | 147 | +7.6% | +7.7% | +9.4% |
| 30-40 (molto caro) | 110 | +5.1% | +3.0% | +7.1% |
| >40 (carissimo) | 22 | −2.0% | −1.0% | +5.9% |

<figure>
  <img src="/charts/shiller-cape-predice-rendimenti/05_forward_by_bucket_real.png" alt="Grafico a barre con il rendimento reale annualizzato mediano a 5 e 10 anni per ciascuna fascia CAPE. Le barre calano andando dalle fasce economiche a quelle care, con l'ultima fascia in negativo." />
  <figcaption>Rendimento reale annualizzato mediano a 5 e 10 anni per fascia CAPE. La discesa dalle fasce economiche a quelle care è netta; la fascia "carissimo" è l'unica in territorio negativo.</figcaption>
</figure>

Tre osservazioni oneste sui numeri.

**La relazione è monotòna in tendenza, non fascia per fascia.** Il bucket "25-30 (caro)" rende leggermente più del "20-25" a 10 anni (+5.5% contro +4.9%). È rumore di campione: le fasce intermedie contengono epoche eterogenee e qualche sovrapposizione. La tendenza generale (visibile nello scatter e nella regressione) è chiaramente decrescente, ma non aspettiamoci una scala perfetta gradino per gradino.

**La fascia "carissimo" ha pochi dati.** Solo 22 mesi su 145 anni hanno avuto un CAPE sopra 40, tutti concentrati attorno al picco dot-com del 1999-2000 e al picco del 2021. Il "−3.5% reale a 10 anni, 100% negativo" è vero ma è essenzialmente **un episodio** (chi comprò al top del 2000 si trovò, dieci anni dopo, con un rendimento reale negativo). Robusto come direzione, fragile come precisione puntuale.

**Il nominale non va mai negativo oltre i 10 anni.** Anche la fascia carissimo, in termini nominali, perde solo "poco" (−1.0% a 10 anni) perché l'inflazione gonfia i numeri. È il motivo per cui guardare solo il nominale inganna: ti fa credere di non aver perso, quando in potere d'acquisto stavi arretrando.

## Il tempo salva? Sì, ma guarda il prezzo

Ora la parte che risponde alla domanda più interessante: **se compri quando tutto è carissimo e poi tieni per vent'anni, il tempo ti salva?**

<figure>
  <img src="/charts/shiller-cape-predice-rendimenti/07_hitrate_negative_real.png" alt="Grafico a barre che mostra la percentuale di periodi con rendimento reale a 10 anni negativo per ciascuna fascia CAPE. La fascia carissimo è al 100%, le altre molto più basse." />
  <figcaption>Percentuale di periodi con rendimento reale a 10 anni negativo, per fascia CAPE. Comprare "carissimo" ha portato a un rendimento reale decennale negativo nel 100% dei casi storici.</figcaption>
</figure>

A 10 anni, comprare a CAPE sopra 40 ha significato un rendimento reale negativo nel 100% dei casi. Ma allungando a 20 anni, la percentuale di casi negativi crolla a **zero per ogni fascia**: nella storia dell'S&P 500, non esiste un singolo periodo di 20 anni con rendimento reale negativo, nemmeno partendo dal picco della bolla.

Il dettaglio della fascia carissimo a 20 anni: mediana +3.7% reale annuo, con un intervallo strettissimo (dal 5° al 95° percentile: da +3.1% a +4.1%). Chi comprò al culmine della bolla dot-com, vent'anni dopo, aveva un rendimento reale positivo ma modesto. Il tempo ha sanato la perdita.

**Ecco però il punto che nessuno racconta.** "Positivo" non vuol dire "uguale". Confrontiamo i due estremi su 20 anni:

- CAPE economico (<15): +8.6% reale annuo → 1 euro reale diventa **5.2 euro** in vent'anni.
- CAPE carissimo (>40): +3.7% reale annuo → 1 euro reale diventa **2.1 euro** in vent'anni.

Chi ha comprato carissimo, dopo vent'anni, si è ritrovato con **meno della metà** del capitale reale di chi ha comprato economico. Entrambi in positivo, ma su pianeti diversi. La valutazione di partenza non decide *se* fai soldi sul lunghissimo periodo — su vent'anni li hai sempre fatti — ma decide *quanti*, e la differenza è enorme.

## Attenzione: il CAPE non è market timing

Qui va detta la cosa più importante, perché è quella che rende il CAPE utile invece che pericoloso.

Il CAPE predice i rendimenti *medi su orizzonti lunghi*. Non dice *quando* arriverà l'eventuale periodo di rendimenti scarsi. La differenza è cruciale. Il CAPE dell'S&P 500 ha superato 30 nel 2017, ed è rimasto alto (con la breve parentesi del crollo COVID) fino a oggi. Chi nel 2017 avesse venduto tutto perché "il CAPE dice che è caro" avrebbe perso uno dei mercati rialzisti più forti della storia recente.

Questo si vede anche nei dati: il potere predittivo del CAPE a 5 anni è molto più debole (R² 0.12) che a 20 anni (R² 0.32). Sull'orizzonte breve il rumore domina il segnale. Il CAPE ti dice qualcosa di affidabile solo se la domanda è "quanto renderà mediamente il mercato nei prossimi 10-20 anni?", non "cosa farà l'anno prossimo?".

L'uso corretto, quindi, non è "esci quando il CAPE è alto". È **calibrare le aspettative**: se il CAPE oggi è a 40, la storia suggerisce che i rendimenti reali del prossimo decennio saranno probabilmente più bassi della media — utile per pianificare tassi di prelievo, obiettivi di risparmio, aspettative pensionistiche. Non per entrare e uscire dal mercato.

## Provalo tu

Ho costruito uno strumento interattivo dedicato: imposti un livello di CAPE e vedi i range storici dei rendimenti reali e nominali a 5, 10 e 20 anni per quella fascia. È nella sezione strumenti del sito.

<div style="margin: 1.5rem 0; padding: 1.25rem 1.5rem; border: 2px solid #1e3a8a; border-radius: 1rem; background: #dbeafe;">
  <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #1e3a8a; font-weight: 600;">Strumento correlato</div>
  <div style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-top: 0.25rem;">
    Simulatore CAPE e rendimenti attesi
  </div>
  <div style="color: #334155; margin-top: 0.5rem; font-size: 0.95rem;">
    Imposta un valore di CAPE e osserva cosa ha reso storicamente il mercato a 5, 10 e 20 anni in quella fascia, in termini reali e nominali.
  </div>
  <div style="margin-top: 0.75rem;">
    <a href="/strumenti/simulatore-cape" style="display: inline-block; background: #1e3a8a; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600;">
      Apri il simulatore →
    </a>
  </div>
</div>

## Cosa porto a casa

1. **Il CAPE predice davvero i rendimenti sul lungo periodo**, ed è tra le poche metriche a farlo in modo statisticamente robusto. Il segnale si rafforza con l'orizzonte: debole a 5 anni, moderato a 10, forte a 20 (R² 0.32).

2. **Le fasce di valutazione contano moltissimo.** Storicamente, comprare economico (CAPE <15) ha reso quasi il triplo, in termini reali decennali, di comprare carissimo (CAPE >40): +9.5% contro −3.5% annuo.

3. **Il tempo sana le perdite ma non il costo-opportunità.** A 20 anni nessuna fascia è mai andata in negativo reale, nemmeno la più cara. Ma chi ha comprato carissimo è arrivato a meno della metà del capitale reale di chi ha comprato economico. Non perdi, ma guadagni molto meno.

4. **Il CAPE non è uno strumento di market timing.** Dice quanto rende mediamente il mercato su 10-20 anni, non quando comprare o vendere. Chi lo usa per uscire dal mercato quando "è caro" rischia di perdere anni di rialzi. L'uso corretto è calibrare le aspettative di lungo periodo.

Oggi il CAPE è attorno a 40. Sui dati storici, è la zona associata ai rendimenti reali decennali più bassi (spesso negativi). Non è una previsione — è un ordine di grandezza da tenere presente quando si pianifica, senza trasformarlo nell'illusione di saper prevedere il prossimo anno.

---

### Fonti e riproducibilità

- Shiller CAPE (PE10) e serie S&P 500 total return: [dataset Robert Shiller](http://www.econ.yale.edu/~shiller/data.htm), esteso per i mesi recenti con [multpl](https://www.multpl.com/shiller-pe/table/by-month).
- Rendimenti reali deflazionati per CPI Shiller (esteso al 2.5% annuo dopo settembre 2023); dividendo esteso all'1.8% annuo dopo giugno 2023.
- Codice della simulazione: [`scripts/shiller-cape-predice-rendimenti.py`](https://github.com/TylerD1917/smartmoneylab/blob/main/scripts/shiller-cape-predice-rendimenti.py).
- Panel mensile, statistiche per fascia, regressioni: [`/charts/shiller-cape-predice-rendimenti/`](/charts/shiller-cape-predice-rendimenti/).
- Riferimenti: Campbell & Shiller (1988, 1998) sul valore predittivo dei rapporti di valutazione; Robert Shiller, *Irrational Exuberance* (2000).

> Nota metodologica: l'analisi usa mediane su finestre mobili sovrapposte, quindi le osservazioni sono fortemente autocorrelate (mesi consecutivi condividono gran parte del periodo forward). Le correlazioni e gli R² vanno letti come descrittivi della relazione storica, non come stime con errori standard indipendenti. La fascia CAPE >40 ha solo 22 osservazioni mensili, concentrate in due episodi (2000 e 2021): le sue statistiche sono indicative, non robuste.

> Disclaimer: contenuto informativo ed educativo, non consulenza finanziaria. Le performance passate non sono indicative di quelle future. Le analisi presentate sono esercizi quantitativi descrittivi, non raccomandazioni operative. Il CAPE è un indicatore di lungo periodo con potere predittivo limitato sul breve; non deve essere usato come segnale di ingresso o uscita dal mercato.
