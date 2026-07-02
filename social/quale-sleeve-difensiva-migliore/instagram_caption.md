# Caption Instagram (carosello) — Quale sleeve difensiva è la migliore?

**Account**: @smartmoneylab_it
**Asset**: `instagram_carousel.md`
**Lunghezza target**: ~2100 caratteri

---

## Caption proposta

Se hai un portafoglio 100% S&P 500 e vuoi aggiungere un settore difensivo per proteggerti dai drawdown senza toccare bond o oro, quale scegli? Il retail italiano tipicamente sceglie Quality o Healthcare. Ho testato 5 candidati contro l'S&P puro su 27 anni di dati storici (1998-2025) e la risposta è controintuitiva.

I candidati testati come proxy: Healthcare (XLV), Consumer Staples (XLP), Utilities (XLU), Min Volatility (USMV), Quality (QUAL). Ognuno aggiunto al portafoglio a tre pesi diversi (10%, 15%, 20%) contro il benchmark 100% S&P 500. Quattro risultati centrali:

• Utilities vince su ogni criterio significativo. Sui 27 anni con la sleeve al 20% ha il miglior Sharpe (0,657 contro 0,616 dell'S&P puro), il miglior Calmar, la volatilità più bassa (13,57%) e riduce il max drawdown da -50,8% a -47,5%. Sui rolling ventennali batte l'S&P puro nel 100% delle finestre. Sorpresa relativa: il settore che il mercato considera "in declino" (transizione energetica, tassi alti) è quello che ha protetto meglio negli ultimi tre decenni.

• Healthcare è il pranzo davvero gratis. Aggiungendo Healthcare al 20% il CAGR del portafoglio resta invariato a 3 cifre decimali (8,45% identico al puro S&P) ma il MDD si riduce di 3,4 punti e la volatilità di quasi un punto. La ragione: Healthcare ha rendimenti storici quasi uguali all'S&P ma correlazione più bassa. Il pranzo gratis di Markowitz nella sua forma più pulita.

• Quality NON è una sleeve difensiva. Sui dati 2013-2025 aggiungere Quality al portafoglio peggiora tutte le metriche di rischio. Ogni 5 punti di Quality aggiunti fanno peggio: il max drawdown va da -23,9% (puro S&P) a -24,7% (con 20% di Quality), lo Sharpe scende, il Calmar cala. La ragione è meccanica: l'indice MSCI Quality seleziona le stesse mega-cap tech che dominano già l'S&P 500, quindi non diversifica, concentra.

• Il peso conta. Al 10% l'effetto è visibile ma modesto. Al 20% le differenze diventano nitide e il costo in CAGR resta piccolo (0,15-0,33 punti annui). La dose sweet spot è 15-20%, non il 10% standard.

Analisi completa, codice Python, caveat metodologici e grafici trade-off sul blog → link in bio.

—
SmartMoneyLab — Finanza personale e analisi quantitativa.
Disclaimer: contenuto informativo, non consulenza finanziaria.

---

## Hashtag (primo commento, 15 mix di volumi)

#portafoglio #utilities #healthcare #consumerstaples #minvolatility #quality #sp500 #ETF #investimenti #investireinitalia #finanzapersonale #educazionefinanziaria #culturafinanziaria #investitoreretail #assetallocation

---

## Note operative

- Hashtag in primo commento, non in caption.
- Tono: chirurgico sulle metriche. Il colpo di scena Quality è il gancio narrativo.
- Risposte ai commenti probabili:
  - "Ma Quality nel 2008 avrebbe funzionato!" → "Possibile. Il periodo testato per Quality è 2013-2025 (l'ETF QUAL parte da luglio 2013). Sui dati disponibili, la conclusione è netta. Se in futuro Quality torna a comportarsi come 'vera' difensiva la rivediamo."
  - "Utilities morirà per la transizione energetica!" → "Le stesse argomentazioni si sentivano 15 anni fa e Utilities ha continuato a proteggere. I dati non fanno previsioni, dicono cosa è successo."
  - "Manca il TER" → "Vero, i numeri sono lordi. TER medio 0,15-0,30% erode il 5-8% del capitale su 27 anni. Non trascurabile ma piccolo rispetto ai numeri del trade-off."
