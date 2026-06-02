# Caption Instagram — PAC con leva tattica

**Account**: @smartmoneylab_it
**Lunghezza target**: ~1900 caratteri

---

## Caption proposta

Una strategia ricorrente nel FinTwit: PAC normale ($300/mese su NASDAQ + SP500), ma quando un indice perde il 20% dai massimi la nuova contribuzione va su ETF 2x daily-rebalanced. Quando torna sui massimi, di nuovo 1x. Switch separato sui due indici. Le posizioni 1x già accumulate non si toccano.

Promessa: potenzio il rendimento quando il mercato è scontato, senza correre strutturalmente più rischio. Ho testato la versione meccanica su 50 anni di dati (1976-2025) con ETF 2x sintetici calibrati su 17.5 anni di SSO/SPY e 19.5 anni di QLD/QQQ. Risposta: due verdetti opposti, entrambi corretti.

Framework rigoroso a 6+1 metriche (CAGR, win rate, vol, MDD, Sharpe, Sortino, Calmar): la tattica vince su CAGR e win rate ma perde sistematicamente su volatilità, MDD e Sharpe. Su 25 anni passa solo 2 criteri su 7. Verdetto: NON VINCE.

Payoff finale del PAC su 25 anni (101 finestre rolling):
• p5: +0.8% — anche nel peggior caso storico, pareggia
• Mediana: +8.0%
• p95: +71.7% — nel miglior caso, +72% di capitale
• Win rate finale: 96%

Sul full period 50Y, $180.000 contribuiti diventano $9.82M con la tattica vs $8.18M con il B&H: +$1.64M, +20%.

Il prezzo c'è. Il MDD percentuale del portafoglio peggiora sensibilmente (fino a -80%). Se non lo sopporti emotivamente, capitoli prima del rebound e tutto il vantaggio evapora. E la "tattica" non è chirurgica: passa il 33.8% del tempo in leva su NASDAQ (44% sulle finestre 25Y). È un'esposizione semi-strutturale al 2x condizionata ai drawdown.

Quale verdetto è "quello giusto" dipende da cosa stai facendo e da chi sei. L'errore è sceglierne uno e fingere che l'altro non esista.

Analisi completa, tabelle CAGR percentili e simulatore interattivo dove muovi soglia e contribuzione → link in bio.

—
SmartMoneyLab — Finanza personale e analisi quantitativa.
Disclaimer: contenuto informativo, non consulenza.

---

## Hashtag (15 — mix)

#etf #pic #pac #investimenti #investireinitalia #leva #leverage #portafoglio #educazionefinanziaria #culturafinanziaria #fintwit #buyandhold #dca #sp500 #nasdaq

---

## Note operative

- Hashtag in **primo commento**, non in caption.
- Aggiornare temporaneamente "link in bio" col link diretto al post per i 7-10 giorni post-pubblicazione.
- Risposte ai commenti previsti:
  - "Ma il MDD a −80% è da pazzi" → percentuale, non assoluto. In $$$ veri il MDD% si applica al portafoglio attuale, quindi nei primi anni del PAC è una frazione piccola del capitale. L'articolo lo spiega esplicitamente.
  - "Sì ma se la borsa va male a fine 25 anni?" → considerata: nelle 101 finestre 25Y storiche, in 4 finestre la tattica ha chiuso in pareggio col passivo (mai persa significativamente). Il 5° percentile è +0.8%.
  - "Hai usato ETF americani non disponibili in UE" → ho usato ETF sintetici con TER UCITS conservativi e funding reale calibrato sui dati. I numeri valgono per chi compra il 2x UCITS in Europa.
  - "La leva è sempre rischio" → in termini di volatilità sì. In termini di money-in-the-bank a fine corsa su orizzonte 25Y, no, secondo 50 anni di dati. Sono due metriche diverse — il punto dell'articolo è esattamente questo.
- Tono: l'articolo è esplicitamente *due verdetti opposti*. La caption mantiene la stessa onestà: niente "questa strategia batte il mercato!" né "le strategie a leva sono per pazzi". Centro della comunicazione = la tensione tra i due framework.
