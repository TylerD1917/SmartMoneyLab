---
title: "Tracker investimenti — un foglio Excel semplice per il tuo portafoglio"
description: "Un foglio Excel a due sheet per tenere traccia dei tuoi titoli, monitorare il valore del portafoglio, e capire quando ribilanciare. Gratis, senza registrazione, modificabile."
pubDate: 2026-05-04
tags: ["tracker", "excel", "asset-allocation", "rebalancing", "portafoglio"]
author: "SmartMoneyLab"
toolType: "excel"
downloadUrl: "/tools/tracker-investimenti.xlsx"
downloadFilename: "tracker-investimenti.xlsx"
downloadSize: "9 kB"
tier: "free"
draft: false
---

## Cosa fa

È un **foglio Excel a due sheet** per tenere traccia degli investimenti, con la sola informazione che serve davvero: *come è composto il tuo portafoglio oggi rispetto a come vorresti che fosse, e in quanto ti scosti dai target*. Niente API, niente connessione live, niente macro VBA: i prezzi li aggiorni manualmente quando vuoi farne il check (mensile, trimestrale, semestrale — sta a te).

Il foglio risponde a quattro domande basilari ogni volta che lo apri:

1. Qual è il valore totale del mio portafoglio adesso?
2. Quanto ho guadagnato o perso rispetto a quanto ho versato?
3. Come sono ripartiti i miei soldi tra le diverse classi di asset (USA, Globale, EM, oro, small cap, tech, ecc.)?
4. C'è qualche asset class che è scesa o salita troppo rispetto al target — è il momento di ribilanciare?

L'unico mestiere che ti chiede è quello di **inserire i tuoi titoli** e **aggiornare i prezzi di mercato** quando vuoi vedere lo stato aggiornato. Il resto sono SUMIF, SUM e qualche IF.

## La struttura: due fogli

### Sheet "Data" — la lista dei titoli

Contiene una riga per ciascun titolo che possiedi. Le colonne sono pensate per essere autoesplicative:

- **Titolo, Tipo Asset, ISIN, Simbolo, Mercato, Strumento, Valuta** — anagrafica del titolo. Il campo *Tipo Asset* è quello che fa il legame con la dashboard del foglio Portafoglio: deve coincidere con una delle categorie elencate lì (es. "Azionario USA", "Mercati emergenti", "Oro", ecc.).
- **Quantità, P.zo medio di carico, Cambio di carico** — quante quote hai, prezzo medio a cui le hai comprate, cambio applicato all'acquisto (1.0 se hai comprato in EUR un ETF UCITS).
- **P.zo di mercato, Cambio di mercato** — gli unici due campi che devi aggiornare manualmente quando vuoi vedere lo stato del portafoglio. Per ETF UCITS in EUR, *Cambio di mercato* resta 1.0.
- **Valore di carico, Valore di mercato €** — calcolati automaticamente: `quantità × prezzo × cambio`.
- **Broker** — opzionale ma utile se hai conti su più piattaforme (Fineco, Scalable, Revolut, ecc.).

In riga 12 c'è il totale automatico delle colonne *Valore di carico* e *Valore di mercato €*.

### Sheet "Portafoglio" — la dashboard di rebalancing

Qui c'è il cuore del foglio. Una tabella aggregata che, per ogni asset class:

- Calcola il **valore aggregato** sommando tutti i titoli del foglio Data che appartengono a quella categoria (`SUMIF` sul campo *Tipo Asset*).
- Calcola il **peso attuale** della categoria nel portafoglio (valore aggregato ÷ totale).
- Lo confronta con il **target** che imposti tu nella colonna D (la somma dei target deve fare 100%, default sei su una composizione 30% USA / 10% Globale / 10% EM / 6% Oro / 10% Small Cap / 10% Nasdaq / 5% Crypto / 2% Liquidità / 7% Healthcare / 10% Europa).
- Calcola la **deviazione %** (peso attuale − target) e il **differenziale in €** (quanto ti manca o ti avanza in valore assoluto rispetto all'allocazione teorica).
- In colonna H mostra un'**azione suggerita**: se la deviazione è inferiore a −5% suggerisce **COMPRA**, se superiore a +5% suggerisce **RIDUCI**, altrimenti **OK**. È la classica banda di rebalancing del 5%, semplice e operativa.
- Calcola il **rendimento %** della classe rispetto al valore di carico cumulato (`(valore di mercato − valore di carico) / valore di carico`).

A destra c'è un piccolo **cruscotto di riepilogo**: Totale investito, Valore portafoglio, Rendimento complessivo, P&L in €. Sono i quattro numeri che vuoi vedere quando apri il file.

## Come si usa, in 5 step

1. **Sostituisci le righe di esempio nel foglio Data** con i tuoi titoli reali. Per ognuno: titolo, tipo asset (deve coincidere con una delle categorie del foglio Portafoglio), ISIN/simbolo se ti serve riferimento, quantità, prezzo medio di carico, cambio (1.0 se hai comprato in EUR), broker.
2. **Aggiorna i prezzi di mercato e i cambi**. Le colonne L (P.zo di mercato) e M (Cambio di mercato) sono le uniche due da inserire ogni volta che fai il check del portafoglio. Per gli ETF UCITS in EUR il cambio resta 1.0; per ETF in USD inseriscilo (vedi google "EUR USD oggi" o il tasso del tuo broker).
3. **Personalizza i target nel foglio Portafoglio** (colonna D, righe 2-11). Imposta le percentuali secondo la tua strategia di asset allocation. Verifica che la somma dei target faccia 100% (la cella D12 te lo conferma).
4. **Inserisci la liquidità** manualmente nella cella B9 (non viene aggregata dal foglio Data). Sono i soldi sul conto corrente o sul conto deposito che fanno parte del portafoglio.
5. **Leggi il cruscotto** e la colonna *Azione*. Le righe in **COMPRA** sono quelle dove sei sotto il target di oltre il 5% — candidato naturale per il prossimo PIC trimestrale. Le righe in **RIDUCI** sono quelle dove sei sopra il target di oltre il 5% — se vuoi ribilanciare, è da lì che vendere.

## Cosa NON fa (e perché va bene così)

Tre limiti onesti, di cui sono perfettamente consapevole:

- **Non aggiorna i prezzi automaticamente**. Avrei potuto usare `STOCKHISTORY()` (richiede Excel 365 con abbonamento) o `GOOGLEFINANCE()` (funziona solo in Google Sheets). Entrambe rendono il file dipendente da una piattaforma specifica e fragili nel tempo. Aggiornare manualmente 8-10 prezzi al mese richiede 2 minuti e funziona ovunque (Excel, LibreOffice, Numbers, Google Sheets).
- **Non gestisce le tasse**. Il rendimento mostrato è lordo di capital gain tax e bollo. Per una stima netta puoi sottrarre approssimativamente 26% sui guadagni realizzati e 0.20% annuo del valore del portafoglio per il bollo (regime amministrato). Le tasse non sono un dato di portafoglio — sono un evento puntuale al momento della vendita.
- **Non fa benchmarking**. Non confronta il tuo rendimento con un indice (MSCI World, S&P 500). Aggiungerlo richiederebbe ulteriori formule e una serie storica esterna. È il candidato naturale per la versione Pro futura, insieme al fattore time-weighted vs money-weighted return e al confronto con benchmark.

## Personalizzazione

Il foglio è progettato per essere modificato. Le cose che probabilmente vorrai cambiare:

- **Le categorie di asset class** nel foglio Portafoglio (colonna A). Se hai un'allocazione diversa dalla mia (es. niente crypto, niente oro), elimina le righe corrispondenti. Se vuoi categorie diverse (es. "Obbligazioni IG", "Obbligazioni HY", "REIT") aggiungile e usa lo stesso nome esatto nel campo *Tipo Asset* del foglio Data.
- **La banda di rebalancing**. È fissata a ±5% nella formula della colonna H del foglio Portafoglio. Per cambiarla a ±3% o ±10% modifica le due soglie nella formula `=IF(F2<-0.05,"COMPRA",IF(F2>0.05,"RIDUCI","OK"))`.
- **Aggiungere righe titoli**. Il foglio Data ha 9 righe di esempio (righe 2-10). Per aggiungere il decimo titolo o successivi, ricordati di estendere i range delle SUMIF/SUM nel foglio Portafoglio (Data!$N:$N e Data!$K:$K usano l'intera colonna, quindi vanno automaticamente, ma il totale in riga 12 di Data è fissato a `=SUM(K2:K10)` — cambialo a K100 o oltre se aggiungi righe).

## Roadmap (ovvero: arriverà una versione Pro?)

Probabilmente sì, e probabilmente non gratis. Quello che ho in mente di aggiungere a una **versione Pro** futura:

- Aggiornamento prezzi automatico via Power Query (Excel 365) o Apps Script (Google Sheets).
- Storico mensile dei valori del portafoglio + grafico equity curve cumulata.
- Calcolo time-weighted return (TWR) per il confronto pulito con benchmark (gli investimenti retail con flussi non costanti distorcono il money-weighted return).
- Confronto vs MSCI World e altri 2-3 benchmark configurabili.
- Tracking del cumulato delle imposte sul capital gain e sul bollo, per stima fiscale annua.
- Integrazione con calcoli di "drift naturale" tra rebalancing per stimare il costo opportunità.

Quando sarà pronta la annuncio sul blog, nei social, nella newsletter (quando esisterà). La versione **base che scarichi qui resterà gratis** sempre — è il livello di funzionalità che a un investitore retail buy & hold serve davvero.

---

## Hai un suggerimento? Una richiesta?

Se hai una richiesta concreta su cosa aggiungere, una bug-segnalazione (es. "la formula della cella X è rotta sul tuo file"), o una domanda su come adattarlo al tuo caso specifico — scrivimi. Tutti i feedback alla mail [smartmoneylab@proton.me](mailto:smartmoneylab@proton.me) o nei commenti qui sotto sono benvenuti, e i suggerimenti più validi finiscono nelle versioni successive con citazione esplicita.
