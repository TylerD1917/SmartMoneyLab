# Bozza post r/ItaliaPersonalFinance

**Titolo:** Ho testato nove livelli di leva fra 1x e 2x su 51 anni e tre indici. La leva conviene solo se hai vent'anni davanti, e il livello giusto dipende dall'indice

---

Gli ETF a leva esistono solo a 2x e 3x, ma una leva intermedia te la puoi costruire con un portafoglio: 40% in un ETF 2x e 60% in uno normale fa 1,40 il primo giorno. Mi sono chiesto se in quella regione esista un livello che conviene davvero, e ho testato 1,00 / 1,10 / 1,25 / 1,40 / 1,50 / 1,60 / 1,75 / 1,90 / 2,00 su S&P 500, Nasdaq Composite e MSCI World dal gennaio 1975 al luglio 2026.

**Due scelte metodologiche che cambiano il risultato**

Il costo del prestito non è fisso ma agganciato ai Fed Funds del mese più uno spread dello 0,48%, calibrato sui prezzi reali del ProShares Ultra S&P 500. Serve perché fra il 1975 e il 1989 i Fed Funds hanno fatto il 9,01% medio e fra il 2009 e il 2021 lo 0,52%: un costo unico per cinquant'anni regala alla leva tre punti all'anno nel periodo sbagliato.

E il mix va ribilanciato, altrimenti la domanda non ha senso. Senza ribilanciare, un portafoglio partito a leva 1,50 arriva a 1,82 perché il comparto a leva cresce di più e prende il sopravvento. La cosa peggiore non è la deriva ma la sua forma: la leva effettiva tocca il massimo il 23 marzo 2000 e il 19 febbraio 2020, nei giorni esatti dei massimi di mercato, e il minimo il 9 marzo 2009, il giorno esatto del minimo del bear.

**Il risultato**

Su finestre mobili di dieci anni la leva non migliora mai lo scenario sfortunato. Il rendimento annuo del 5% di ingressi peggiori è massimo a leva 1,00 su tutti e tre gli indici e cala senza eccezioni: sull'S&P va da +1,76% senza leva a -4,40% a leva 2,00.

Su finestre di vent'anni si ribalta. Il quinto percentile è massimo a leva 1,40 sull'S&P (6,72% contro 6,32% senza leva), 1,25 sul Nasdaq, 1,10 su MSCI World. Più l'indice è volatile rispetto a quanto rende, meno leva tollera.

Una cosa che mi ha sorpreso: più a fondo si guarda nella coda cattiva, meno leva si vuole. Sull'S&P a vent'anni il minimo assoluto è massimizzato a leva 1,10, il quinto percentile a 1,40, il primo quartile a 1,50, la mediana a 2,00. Nella singola finestra peggiore del campione anche la 1,40 perde contro l'assenza di leva.

Avevo anche un'ipotesi che i dati hanno smentito: pensavo che la leva conveniente scendesse quando i tassi sono alti. La correlazione fra tassi medi della finestra e leva migliore è praticamente zero (+0,05 sull'S&P), perché i decenni di tassi alti sono stati anche decenni di premi al rischio generosi.

**Limiti**

Tutto lordo: niente 26% sulle plusvalenze realizzate dal ribilanciamento annuale, niente bollo, niente commissioni. Sono un tetto superiore. Lo spread di funding è calibrato su un prodotto del periodo 2006-2023 e applicato anche agli anni Settanta, che è l'ipotesi più fragile del lavoro. E le finestre ventennali si sovrappongono quasi tutte, quindi il quinto percentile poggia su 127 finestre che condividono gran parte della stessa storia.

Script Python e serie storiche sono nel repo, se qualcuno vuole rifare i conti o cambiare le ipotesi.

[link all'articolo]
