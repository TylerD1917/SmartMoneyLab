# Caption Instagram (carosello) — Il mio portafoglio nel 2024

**Account**: @smartmoneylab_it
**Asset**: `instagram_carousel.md`
**Lunghezza target**: ~2100 caratteri

---

## Caption proposta

Inauguro una nuova rubrica del blog: "test di portafogli reali". Il primo soggetto è il mio. 13 asset, equity-only, allocazione target che ho disegnato a novembre 2024 per intercettare cinque-dieci anni di trend di mercato. L'ho messo sotto la stessa lente con cui ho fatto a pezzi la strategia LEAPS e gli ETF a leva 3x negli articoli precedenti — accettando in anticipo l'esito.

22 anni di backtest (2003-2025) + simulazione Monte Carlo a 10.000 traiettorie su orizzonti 10/20/30 anni. Tre risultati centrali:

• Sul backtest 22 anni il portafoglio batte i benchmark di una distanza significativa. CAGR 14,30% contro 11,36% dell'S&P 500 TR e 9,45% del MSCI World TR. Su 10.000 € investiti in lump sum nel 2003, alla fine del 2025 il portafoglio chiude a 204.776 €, l'S&P a 113.674 €, il MSCI World a 76.771 €. Il PAC da 200 €/mese (54.400 € versati) finisce a 396.541 €, contro 273.178 € dell'S&P e 199.526 € del World.

• Non è leva, è diversificazione che funziona. Diversamente dalla strategia LEAPS testata nell'articolo precedente, qui il drawdown massimo è leggermente migliore dei benchmark (-49,5% vs -50,8%) nonostante una volatilità più alta di 2,8 punti. Il Calmar (CAGR/|MDD|) del portafoglio è 0,289 contro 0,224 dell'S&P. Win rate sui rolling 10y: 94% vs S&P, 100% vs MSCI World. Sui rolling 15y: 100% contro entrambi.

• Monte Carlo a 20 anni: 71% di probabilità di battere l'S&P, 82% di battere il MSCI World. Mediana del NAV finale a 20 anni partendo da 10.000 €: portafoglio 147.630 €, S&P 84.769 €, World 60.444 €. Coda destra (p95) del portafoglio 696.748 €, contro 239.679 € dell'S&P. Coda sinistra (p5) 40.571 € contro 28.784 € dell'S&P. L'asimmetria del payoff è favorevole sia nelle code basse che in quelle alte.

Il bias di selezione retrospettiva è enorme e dichiarato: ho disegnato questo portafoglio nel 2024 conoscendo i trend che hanno premiato gli ultimi 22 anni. Il backtest dimostra "se i prossimi 22 anni assomigliano agli ultimi 22, vinci". Non dimostra "vincerai i prossimi 22 anni".

Analisi completa, codice Python, caveat metodologici e Monte Carlo dettagliato sul blog → link in bio.

—
SmartMoneyLab — Finanza personale e analisi quantitativa.
Disclaimer: contenuto informativo, non consulenza finanziaria.

---

## Hashtag (primo commento, 15 mix di volumi)

#portafoglio #investimenti #assetallocation #PAC #montecarlo #investireinitalia #ETF #investimentiitalia #finanzapersonale #educazionefinanziaria #azionari #sp500 #MSCIWorld #investitoreretail #culturafinanziaria

---

## Note operative

- Hashtag in primo commento, non in caption.
- Aggiornare temporaneamente il "link in bio" col link diretto al post per i 7-10 giorni post-pubblicazione.
- Tono: trasparenza piena dichiarata (è il portafoglio di Tyler). Niente "ho scoperto la formula magica", niente "comprate questi 13 ETF". L'articolo è un esperimento di rigore aperto al pubblico, lo spirito della caption deve riflettere questo.
- Risposte ai commenti probabili:
  - "Ma è il tuo portafoglio, sei di parte!" → "Esatto, e l'ho dichiarato in apertura. Lo scopo è proprio metterlo sotto la stessa lente con cui critico gli altri. Se i prossimi 5 anni sotto-performerà, lo scriverò sul blog senza filtri."
  - "Posso copiare la composizione?" → "Sconsigliato. È un'allocazione tematica con drawdown attesi del -50%. Solo se tolleri quel rischio e con orizzonte minimo 10 anni — sotto i 10 il win rate vs S&P è solo del 55%."
  - "I costi reali quanto incidono?" → "Circa 70-80 bps annui (TER + spread) + 30-40 bps di fiscalità italiana. L'outperformance netta resta significativa ma non più drammatica (+2pp circa invece di +2,9)."
