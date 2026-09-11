---
title: "ETF obbligazionario o obbligazioni tenute a scadenza? 64 anni di dati"
description: "A parità di duration, un ETF obbligazionario e le obbligazioni tenute a scadenza rendono uguale? 64 anni di Treasury: non sono equivalenti, l'ETF rende un filo di più ma è esposizione permanente ai tassi."
pubDate: 2026-09-11
tags: ["obbligazioni", "etf-obbligazionari", "duration", "treasury", "tenere-a-scadenza", "tassi", "reddito-fisso", "finanza-personale"]
author: "SmartMoneyLab"
category: "finanza-personale"
simulationSlug: "etf-obbligazionari-o-obbligazioni"
seoImage: "/charts/etf-obbligazionari-o-obbligazioni/04_regimi.png"
draft: false
faq:
  - q: "A parità di duration, ETF obbligazionario e obbligazioni tenute a scadenza rendono uguale?"
    a: |-
      Quasi, ma non del tutto. Su 64 anni di Treasury (1962-2026), confrontando un ETF a duration costante con obbligazioni di pari duration (~8 anni) tenute a scadenza, l'ETF ha reso in mediana +0,62% all'anno in più sulle finestre di 10 anni e +0,73% su quelle di 20. Un margine piccolo ma sistematico: non convergono a zero.
  - q: "Perché l'ETF rende un po' di più?"
    a: |-
      Per un motivo strutturale: l'ETF mantiene la duration costante (vende i titoli che invecchiano e ne compra di nuovi), quindi resta sempre pienamente esposto ai tassi e reinveste tutto al rendimento pieno. Un'obbligazione tenuta a scadenza, invece, ha una duration che si scioglie verso zero man mano che si avvicina la scadenza, e le sue cedole vanno reinvestite (spesso a tassi più bassi). In un lungo periodo di tassi calanti come il 1981-2020 questo ha premiato l'ETF.
  - q: "Allora conviene sempre l'ETF?"
    a: |-
      No. Dipende da cosa fanno i tassi durante il tuo periodo. In un ventennio di tassi in salita vince chi tiene le obbligazioni a scadenza (l'ETF subisce le perdite di prezzo, il titolo a scadenza incassa comunque il rendimento pattuito): è successo, per esempio, nel 2022. La mediana pende verso l'ETF solo perché gli ultimi 40 anni sono stati dominati dal calo dei tassi — un vento in poppa che oggi, con i rendimenti tornati intorno al 4%, è in gran parte esaurito.
  - q: "Qual è la differenza pratica tra i due?"
    a: |-
      L'obbligazione tenuta a scadenza ti dà certezza: sai quanto incassi e quando, e le oscillazioni di prezzo nel mezzo non ti toccano se aspetti la scadenza. L'ETF ti dà esposizione costante, diversificazione, reinvestimento automatico e comodità, ma il suo prezzo oscilla sempre e non "scade" mai. In cambio paga un piccolo costo di gestione (TER, ~0,15% per un ETF come IEF) che il titolo comprato in proprio non ha.
  - q: "Attenzione a confrontare la stessa duration?"
    a: |-
      Sì, è l'errore più comune. Un Treasury a 10 anni appena emesso ha una duration di ~8, mentre un ETF "7-10 anni" come IEF ha duration ~7. Confrontarli fa sembrare l'ETF più generoso di ~1% all'anno, ma un terzo di quel vantaggio è solo il fatto che il 10Y è più lungo. Allineando la duration (un titolo con ~8 anni di vita residua) il vantaggio scende a ~+0,6%.
  - q: "Nel caso peggiore, quanto rischio con l'uno o con l'altro?"
    a: |-
      Guardando la finestra storica peggiore su 64 anni: chi ha comprato l'ETF poco prima di una lunga risalita dei tassi (ingresso 1973) ha reso a 10 anni ~3,7 punti l'anno in meno di chi teneva le obbligazioni a scadenza (−29% sul montante). Specularmente, chi ha comprato Treasury al picco dei tassi (ingresso 1978-79), poco prima del crollo, ha lasciato sul tavolo fino a ~2-2,7 punti l'anno rispetto all'ETF (fino a +44% sul montante su 20 anni). Gli estremi sono di dimensione simile e opposti: perdite da risalita dei tassi con l'ETF, mancato guadagno da calo dei tassi con le obbligazioni a scadenza.
  - q: "Vale lo stesso per i BTP?"
    a: |-
      La meccanica è identica: un ETF di BTP tiene la duration costante, un BTP singolo comprato e tenuto a scadenza la lascia decadere e ti blocca il rendimento. Le stesse conclusioni valgono, con in più il fatto che sul BTP tenuto a scadenza conosci con precisione il flusso di cedole e il rimborso a 100 — è il motivo per cui molti risparmiatori italiani preferiscono i singoli titoli.
---

> **Disclaimer.** Contenuto informativo, non consulenza né una raccomandazione su singoli strumenti. Le simulazioni usano dati reali e ipotesi dichiarate, non sono previsioni. I rendimenti passati non garantiscono quelli futuri.

## In breve

È una delle domande che tornano più spesso: per la parte obbligazionaria conviene **un ETF** o **comprare le obbligazioni e tenerle fino a scadenza**? L'idea diffusa è che, a parità di durata, sia la stessa cosa — che i rendimenti "convergano" e quindi cambi poco. Ho provato a rispondere coi numeri: 64 anni di Treasury americani (1962-2026), un ETF a duration costante contro obbligazioni di **pari duration** tenute a scadenza. La risposta è più interessante del previsto.

1. **"Stessa duration" e "tenuto a scadenza" sono in tensione.** Un ETF obbligazionario tiene la duration *costante* (vende in continuazione i titoli che invecchiano e ne compra di nuovi). Un'obbligazione singola, se la tieni a scadenza, ha una duration che **si scioglie verso zero**. Quindi non possono essere davvero "la stessa cosa" nel tempo: l'ETF è un'esposizione **permanente** ai tassi, il titolo a scadenza te la **spegne**.

2. **A duration allineata, l'ETF ha reso un filo di più.** Confrontando l'ETF con obbligazioni di **pari duration** (~8 anni, come un ETF 7-10 anni tipo IEF), il fondo ha reso in mediana **+0,62% all'anno** sulle finestre di 10 anni e **+0,73%** su quelle di 20. Un margine piccolo ma **sistematico**.

3. **Occhio al confronto ingenuo.** Se confronti l'ETF con un Treasury a **10 anni** appena emesso (che è più lungo, duration ~8), il vantaggio apparente sale a ~+1%. Ma **un terzo di quel numero è solo il disallineamento di duration**, non un vero vantaggio: il 10Y è più lungo dell'ETF. Confronta sempre la stessa duration.

4. **Chi vince dipende dai tassi.** In un ventennio di tassi **in salita** vince chi tiene le obbligazioni a scadenza; in uno di tassi **in calo** vince l'ETF. La mediana pende verso l'ETF solo perché gli ultimi 40 anni sono stati un lungo calo dei rendimenti — un vento in poppa oggi in gran parte esaurito (rendimenti tornati intorno al 4%).

5. **Non convergono a zero.** La differenza si **riduce** allungando l'orizzonte (da ~1,1 punti a 10 anni a ~0,9 a 20), ma il divario mediano **resta**: non esiste un orizzonte oltre il quale i due diventano identici.

6. **I costi.** L'ETF paga un TER (~0,15% per IEF): l'unico svantaggio *permanente* rispetto al titolo comprato in proprio. Ma l'ETF reale ha anche un piccolo vantaggio che la ricostruzione storica non cattura (il *roll-down*): nei dati veri l'IEF ha reso ~0,5% all'anno **più** del nostro indice sintetico.

Niente verdetto secco: espongo i numeri, dichiaro i limiti, la scelta la fa il lettore in base a cosa gli serve — **certezza** o **esposizione**.

## La tensione nascosta nella domanda

La domanda sembra innocente — "stessa duration, cambia qualcosa?" — ma contiene una contraddizione che è il cuore di tutto.

Un **ETF obbligazionario** con target, poniamo, "7-10 anni" mantiene la sua duration **costante**: ogni volta che un titolo scende sotto i 7 anni di vita residua lo vende e ne compra uno nuovo più lungo. La duration del fondo resta lì, ferma, per sempre. È un'**esposizione permanente** al rischio tassi: se i tassi salgono il prezzo scende (e non "recupera" aspettando una scadenza, perché una scadenza non arriva mai), se scendono il prezzo sale.

Un'**obbligazione singola tenuta a scadenza** fa l'opposto: la sua duration **decade** verso zero man mano che si avvicina la scadenza. Un titolo a 8 anni di vita residua ha duration ~7; lo stesso titolo, tre anni dopo, ha 5 anni di vita e duration ~4,5; e così via fino a zero il giorno del rimborso. Alla fine incassi **100** qualunque cosa abbiano fatto i tassi nel frattempo: hai **bloccato** il tuo rendimento all'acquisto.

Ecco perché "stessa duration" e "tenuto a scadenza" non stanno insieme più di un istante: puoi avere l'una o l'altra cosa, non entrambe in modo continuativo. E questa, come vedremo, non è una sottigliezza: è ciò che genera tutta la differenza.

## Come li ho confrontati

Sessantaquattro anni, dal gennaio 1962 all'aprile 2026. Il tasso del Treasury a 10 anni viene dai dati storici di Shiller fino al 2000 e dalla serie FRED (DGS10) fino ad oggi; il tasso a breve, per reinvestire le cedole, dai Fed Funds. Due "gambe", costruite dagli stessi tassi così che l'unica differenza sia il **meccanismo**:

- **La gamba ETF** è un indice Total Return a **duration costante**: ogni mese si tiene un titolo alla pari, lo si rivaluta al nuovo rendimento e lo si rinnova alla stessa scadenza, tenendo la duration ferma.
- **La gamba "obbligazioni a scadenza"** compra un titolo alla pari, lo **tiene fino a scadenza** reinvestendo le cedole al tasso a breve, e poi lo rinnova; all'orizzonte del lettore (10 o 20 anni) liquida a mercato l'ultimo titolo non ancora scaduto.

Il punto cruciale, che rende il confronto onesto: **allineo la duration**. Un Treasury a 10 anni appena emesso ha duration ~8, mentre un ETF reale "7-10 anni" come **IEF** (iShares 7-10 Year Treasury) ha duration ~6,9 e vita media ~8,5 anni. Quindi la controparte corretta dell'ETF non è il 10Y, ma un titolo con **~8 anni** di vita (duration ~6,8, praticamente identica a quella dell'IEF). Lavoriamo in **Total Return lordo** (cedole reinvestite, al lordo di costi e tasse); il TER lo trattiamo a parte.

Prima di fidarci del modello, l'ho validato contro il mondo reale: il nostro indice sintetico a duration allineata segue l'IEF con una **correlazione mensile del 0,99**.

<figure>
  <img src="/charts/etf-obbligazionari-o-obbligazioni/05_ief_vs_sintetico.png" alt="Rendimento cumulato dell'IEF reale e dell'indice sintetico a duration allineata dal 2002: quasi sovrapposti, con l'IEF leggermente sopra." />
  <figcaption>L'indice sintetico traccia l'ETF reale quasi perfettamente. Rende ~0,5%/anno in meno perché la ricostruzione lunga non cattura il "roll-down"; ci torniamo alla fine.</figcaption>
</figure>

## Il confronto onesto: a parità di duration

Immagina di ripetere il confronto partendo da ogni possibile mese dei 64 anni, e di misurare il rendimento annualizzato di ciascuna strada su finestre di 10 e di 20 anni. Ogni punto del grafico è una di queste finestre: sopra la diagonale ha vinto l'ETF, sotto ha vinto il titolo a scadenza.

<figure>
  <img src="/charts/etf-obbligazionari-o-obbligazioni/01_scatter_10_20.png" alt="Due grafici a dispersione (10 e 20 anni) del rendimento annuo dell'ETF contro quello delle obbligazioni a scadenza, a pari duration: i punti stanno leggermente sopra la diagonale." />
  <figcaption>Stessa duration (~6,8 anni). I punti stanno in prevalenza appena sopra la diagonale: l'ETF ha reso un filo di più, con una nuvola più stretta sui 20 anni.</figcaption>
</figure>

I numeri: sulle finestre di **10 anni** l'ETF ha reso in mediana **+0,62% all'anno** in più (6,1% contro 5,9%); su quelle di **20 anni**, **+0,73%** (7,5% contro 6,8%). Non è tanto, ma è **persistente**: non è rumore attorno allo zero, è uno scarto che si ripresenta.

<figure>
  <img src="/charts/etf-obbligazionari-o-obbligazioni/02_distribuzione_diff.png" alt="Boxplot della differenza di rendimento ETF meno obbligazioni a scadenza a 10 e 20 anni: mediana positiva (~+0,6% e +0,7%), la scatola si restringe a 20 anni." />
  <figcaption>La differenza (ETF − obbligazioni a scadenza). La mediana è positiva a entrambi gli orizzonti; la dispersione si stringe passando da 10 a 20 anni, ma il centro non scende a zero.</figcaption>
</figure>

Da dove viene questo margine? Da tre effetti che tirano tutti nella stessa direzione: l'ETF resta **sempre pienamente esposto** (mentre la duration del titolo a scadenza si spegne), reinveste **tutto** al rendimento pieno del tratto lungo (mentre le cedole del titolo singolo finiscono reinvestite al tasso a breve, di solito più basso), e cavalca in continuazione la curva dei rendimenti. È il prezzo, in positivo, di non "scadere" mai.

## Il tranello: confronta sempre la stessa duration

Qui c'è l'errore in cui casca quasi chiunque faccia questo confronto, ed è bene renderlo esplicito. Se invece di allineare la duration si confronta l'ETF con un Treasury a **10 anni** appena emesso — che è **più lungo** (duration ~8) — il vantaggio dell'ETF sembra molto più grande, intorno a **+1% all'anno**. Ma buona parte di quel numero non è un vantaggio del *meccanismo*: è solo il fatto che stai confrontando due durate diverse.

<figure>
  <img src="/charts/etf-obbligazionari-o-obbligazioni/03_contrasto_duration.png" alt="Barre del vantaggio annuo dell'ETF per tre durate del titolo: 7 anni +0,5%, 8 anni +0,6-0,7%, 10 anni +1,0%. Evidenziata la colonna a 8 anni, pari alla duration dell'IEF." />
  <figcaption>Più allunghi la durata del titolo di confronto, più "gonfi" il vantaggio dell'ETF. La colonna giusta è quella a ~8 anni (stessa duration dell'IEF): +0,6-0,7%, non +1%.</figcaption>
</figure>

Tradotto: **circa un terzo del "+1%" era un'illusione ottica di duration**. Il vantaggio vero, a parità di rischio tassi, è più modesto — intorno a mezzo punto, tre quarti di punto l'anno.

## Chi vince dipende da cosa fanno i tassi

La mediana nasconde una verità più sfumata: nei singoli ventenni il vincitore **cambia** a seconda del regime dei tassi. Ecco due epoche opposte, stesso confronto.

<figure>
  <img src="/charts/etf-obbligazionari-o-obbligazioni/04_regimi.png" alt="Due pannelli: dal 1962 (tassi in salita) le obbligazioni a scadenza battono l'ETF; dal 1978 (tassi in calo) l'ETF stacca nettamente le obbligazioni a scadenza." />
  <figcaption>A sinistra, un ventennio di tassi in salita: vince chi tiene a scadenza. A destra, uno di tassi in calo: vince l'ETF. Lo stesso confronto, esito opposto.</figcaption>
</figure>

Quando i tassi **salgono**, l'ETF subisce le perdite di prezzo mese dopo mese (compra di continuo titoli che poi valgono meno), mentre chi tiene l'obbligazione a scadenza **ignora** le oscillazioni e incassa il rendimento pattuito: è esattamente quello che è successo nel **2022**, quando un ETF come IEF ha perso circa il 15% e chi aveva i suoi titoli in mano, aspettando la scadenza, no. Quando i tassi **scendono**, la parte si ribalta: l'ETF accumula guadagni in conto capitale che il titolo a scadenza non vede.

La mediana pende verso l'ETF per una ragione storica precisa: gli ultimi **40 anni** sono stati un lunghissimo calo dei rendimenti (dal ~14% del 1981 al ~1% del 2020). Quel vento in poppa ha gonfiato la gamba ETF. Oggi, con i rendimenti tornati intorno al 4%, quella spinta è in gran parte **esaurita** — un motivo per non estrapolare meccanicamente il passato.

## Il caso peggiore, dai due lati — e il tempo aiuta?

Le medie rassicurano; gli estremi dicono la verità sul rischio. Ho preso, su tutti i 64 anni, la finestra **peggiore** per ciascuna delle due strade, a 10 e a 20 anni. Sono quasi speculari: chi compra l'ETF rischia di farlo poco prima di una risalita dei tassi (e incassa le perdite di prezzo); chi compra i Treasury rischia di farlo sul picco dei tassi (e si lascia sfuggire i guadagni del calo che segue).

| Caso peggiore su 64 anni | Ingresso | Divario annuo* | 10.000 € → ETF / a scadenza |
|---|---|---|---|
| Compri l'ETF prima di una risalita dei tassi — **10 anni** | ago 1973 | **−3,7 pt** | 20.200 / 28.300 |
| Compri l'ETF prima di una risalita dei tassi — **20 anni** | gen 1962 | **−1,9 pt** | 22.100 / 31.900 |
| Compri i Treasury sul picco dei tassi — **10 anni** | gen 1979 | **+2,7 pt** | 28.600 / 22.300 |
| Compri i Treasury sul picco dei tassi — **20 anni** | set 1978 | **+2,0 pt** | 71.900 / 49.900 |

<small>*rendimento annuo dell'ETF meno quello delle obbligazioni a scadenza: negativo = l'ETF ha fatto peggio; positivo = quanto ha lasciato sul tavolo chi ha tenuto a scadenza.</small>

Il tempo **aiuta e non aiuta**, ed è il punto interessante. Sul **rendimento annuo** il caso peggiore si **attenua** allungando l'orizzonte — da −3,7 a −1,9 punti per l'ETF, da +2,7 a +2,0 per chi tiene a scadenza — coerente col fatto che la dispersione si stringe. Ma sul **montante** il divario **cresce**: un margine anche più piccolo, composto per vent'anni invece che dieci, pesa di più in euro (nel caso peggiore della scadenza comprata sul picco del 1978, l'ETF avrebbe dato ~72.000 € contro ~50.000, **+44%**). Morale: più tempo rende il caso peggiore meno drammatico anno per anno, ma non cancella — anzi ingrandisce in valore assoluto — la scommessa implicita sul regime dei tassi. È la stessa medaglia, vista dalle due facce.

## Convergono? E in quanto tempo?

Torniamo alla domanda di partenza. La risposta, sui dati, è: **si avvicinano ma non convergono a un unico numero**. Allungando l'orizzonte la *dispersione* si restringe — la differenza media tra le due strade passa da ~1,1 punti l'anno sulle finestre di 10 anni a ~0,9 su quelle di 20 — ma il **divario mediano non svanisce**: non c'è un orizzonte oltre il quale ETF e obbligazioni a scadenza diventano la stessa cosa. È logico, visto da dove nasce la differenza: finché l'ETF tiene la duration costante e il titolo la lascia decadere, i due **non sono lo stesso strumento**, per quanto a lungo aspetti.

## E i costi reali?

Due precisazioni oneste, che spingono in direzioni opposte.

Il **TER** dell'ETF (~0,15% l'anno per IEF) è l'unico svantaggio *permanente* rispetto al titolo comprato in proprio: un piccolo pedaggio costante, che le obbligazioni singole non pagano.

Dall'altra parte, la nostra ricostruzione lunga **sottostima** l'ETF reale: nei dati veri l'IEF ha reso ~**0,5% all'anno in più** del nostro indice sintetico (correlazione a parte), perché un fondo reale cattura il *roll-down* — il guadagno di "scivolare" lungo una curva dei rendimenti inclinata — che la ricostruzione da un solo punto di curva non modella. In altre parole, il piccolo vantaggio strutturale dell'ETF misurato qui è, semmai, prudente.

## Cosa porto a casa

1. **Non sono equivalenti**, e non per un caso statistico: l'ETF tiene la duration **costante** (esposizione permanente ai tassi), il titolo singolo la lascia **sciogliere** e ti blocca il rendimento. È una differenza di natura, non di grado.

2. **A parità di duration, l'ETF ha reso un filo di più** — circa mezzo punto, tre quarti di punto l'anno su 64 anni — grazie all'esposizione costante e al reinvestimento al rendimento pieno. Ma è un margine modesto, non il "+1%" del confronto ingenuo col 10Y.

3. **Il vincitore dipende dai tassi.** Tassi in salita → premia chi tiene a scadenza (vedi 2022). Tassi in calo → premia l'ETF. La mediana favorevole all'ETF è figlia del quarantennio di tassi calanti, oggi alle spalle.

4. **Non convergono a zero:** la dispersione si riduce con l'orizzonte, il divario mediano resta.

5. **La vera scelta è tra due cose diverse.** L'obbligazione (o il BTP) tenuta a scadenza ti compra **certezza**: sai quanto e quando incassi, e le oscillazioni nel mezzo non ti riguardano se aspetti. L'ETF ti compra **esposizione costante, diversificazione, reinvestimento automatico e comodità**, al prezzo di un piccolo TER e di un prezzo che oscilla sempre. Chi ha un obiettivo con una data (una spesa fra 8 anni) e vuole dormire tranquillo tende al titolo a scadenza; chi vuole una componente obbligazionaria "sempre accesa" dentro un portafoglio tende all'ETF. Sul ruolo delle obbligazioni in un portafoglio di lungo periodo, ne ho scritto [qui](/posts/ha-senso-obbligazioni-portafoglio).

## Fonti e riproducibilità

- Tasso Treasury 10 anni: dataset Shiller ("Long Interest Rate", 1871+) fino al 2000, poi FRED DGS10; tasso a breve per il reinvestimento delle cedole: FRED FEDFUNDS. Finestra: gennaio 1962 – aprile 2026 (772 mesi).
- ETF reale di validazione: iShares 7-10 Year Treasury Bond ETF (IEF), Total Return dal 2002 (inception 22/07/2002, effective duration ~6,9 anni, vita media ~8,5). Correlazione mensile col sintetico: 0,99.
- Metodo: indice a duration costante (carry + effetto prezzo con duration e convexity esatte sul par bond) vs titolo par tenuto a scadenza con cedole reinvestite al tasso a breve; duration allineata a quella dell'ETF (~8 anni). Total Return lordo; finestre mobili di 10 e 20 anni.
- Tutti i numeri e i grafici sono generati da `scripts/etf-obbligazionari-o-obbligazioni.py`. Le simulazioni usano ipotesi dichiarate e semplificate a scopo illustrativo e non predittivo.
