# Thread X — È davvero possibile comprare ai minimi?

**Account**: @smartmoneylabIT
**Lunghezza**: 8 post (1 hook + 6 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i 4 PNG in `public/charts/comprare-ai-minimi-market-timing/`

---

## 1/8 — Hook

> "Tengo un po' di liquidità da parte e quando il mercato crolla compro a sconto."
>
> Sembra furbo. È il tipo di strategia che hai mentalmente accarezzato.
>
> Ho testato la versione meccanica più semplice (90/10, deploy a -25% drawdown) su 50 anni di S&P 500. Ecco cosa dicono i numeri.
>
> Thread 👇

*Allegare grafico: 02_winrate_bar.png*

---

## 2/8 — La strategia

> Strategy A (pigro): 100% del flusso trimestrale → S&P 500. Subito. Sempre.
>
> Strategy B (pensante): 90% → S&P 500, 10% → conto deposito al 2% lordo. Quando drawdown ≥ 25%, svuoto cassetto + 100% flusso → S&P 500.
>
> Sembra ragionevole. Sembra prudente. Vediamo se vince.

---

## 3/8 — Il risultato che spazza via il framing

> Win rate Strategy B vs A:
>
> • Finestre 10 anni: 24.8%
> • Finestre 20 anni: **14.9%**
>
> A 20 anni il timing perde 6 volte su 7. E il dato peggiora ALLUNGANDO l'orizzonte, non migliora.
>
> Più tempo = più trimestri normali in cui il cassetto sta fermo a basso rendimento.

*Allegare grafico: 02_winrate_bar.png*

---

## 4/8 — L'asimmetria che uccide

> Excess % (B - A) sui 20 anni:
>
> • p5 (peggior caso): -8.43%
> • Mediana: -2.77%
> • p95 (miglior caso): **+0.38%**
>
> Hai 8 punti percentuali da perdere e 0.4 da guadagnare. Asimmetria devastante.
>
> Anche nei migliori scenari il vantaggio è meno del TER che paghi all'ETF.

*Allegare grafico: 03_excess_distribution.png*

---

## 5/8 — Il dato che fa male

> In 50 anni di mercato, il cassetto si è scaricato **4 volte**.
>
> Date: ottobre 2001, luglio 2002, ottobre 2008, luglio 2010.
>
> 4 trimestri su 200. Il 2% del tempo.
>
> Per il restante 98% dei trimestri il "trader furbo" ha tenuto soldi al 2% mentre il mercato saliva del 10-12% annualizzato.

---

## 6/8 — Il timing del deploy è impossibile

> Dei 4 deploy automatici:
>
> • Ottobre 2008: deploy a -25%. Minimo vero del mercato: marzo 2009 (a -50%).
>
> Il "compro a sconto" è scattato a metà discesa, non al bottom. La storia mostra che questo è la norma, non l'eccezione.
>
> Una regola meccanica non può prevedere il bottom. Punto.

*Allegare grafico: 01_equity_curves_fullperiod.png*

---

## 7/8 — Il costo cumulato in 50 anni

> 200.000 USD investiti totali, 50 anni di accumulo:
>
> • Strategy A (passivo): valore finale ~$9.06 milioni
> • Strategy B (timing): valore finale ~$8.33 milioni
>
> Differenza: -$733.704
>
> Il "trader pensante" ha lasciato sul tavolo 3.7 volte tutto il capitale investito. È il prezzo di voler essere più furbi del mercato.

---

## 8/8 — CTA

> Sui dati la cosa che funziona meglio è quella che a tanti sembra banale: mettere i soldi sul mercato il prima possibile, ignorare i giornali, non guardare il portafoglio.
>
> Sul blog l'analisi completa + un simulatore in cui puoi cambiare i parametri della strategia (% accantonamento, soglia drawdown, tasso CD) e vedere cosa succede live.
>
> [link al post]
>
> #ETF #PIC #Investimenti

---

## Note operative

- **Quote tweet utili a 24-48h**:
  - "In 50 anni di mercato il cassetto si è scaricato 4 volte. Quattro. La frequenza dei crash >25% è bassa, e tenere soldi parcheggiati per accumulare 'munizioni' costa molto più di quanto puoi recuperare con i deploy."
  - "Il p95 dell'excess a 20 anni del market timing meccanico è +0.38%. Cioè anche nei migliori scenari il timing batte la passiva di 0.38 punti percentuali. È meno del TER che paghi all'ETF."

- **Pushback prevedibili**:
  - "Ma il 2% del CD è basso!" → vero, è generoso anche. Storicamente i tassi medi reali sono stati sotto. Articolo lo discute esplicitamente.
  - "Hai considerato il cambio EUR/USD?" → su 20 anni di acquisti ricorrenti il rischio cambio si annulla. Articolo lo discute.
  - "Una strategia con SMA-200 funzionerebbe!" → letteratura accademica (Sharpe 1975) dice che servirebbe accuracy >70% per battere PIC, e nessuna regola meccanica raggiunge quel risultato consistentemente. Risposta: "Articolo specifico in coda."
