# Thread X — Mix Nasdaq + Energia batte il mercato?

**Account**: @smartmoneylabIT
**Lunghezza**: 9 post (1 hook + 7 contenuto + 1 CTA)
**Pubblicazione consigliata**: martedì o giovedì 9:00 / 18:30
**Asset visivi**: i 5 PNG in `public/charts/energia-tech-batte-mercato/`. La scorecard (`05_scorecard.png`) è il visual chiave — usalo nel post 7.

---

## 1/9 — Hook

> Trovata su X una strategia "wow!": 70% Nasdaq + 30% Energy USA, buy & hold.
>
> Tesi macro: tech ed energy si decorrelano. In inflazione vince energy, in disinflazione vince tech. Mixandoli ottieni il meglio dei due mondi.
>
> Sembra logico. Ho fatto girare 26 anni di dati daily col framework SmartMoneyLab a 6+1 metriche.
>
> Verdict: 4/7 — PARZIALE. Thread 👇

*Allegare grafico: 05_scorecard.png*

---

## 2/9 — La strategia

> Setup:
> • 70% QQQ (Invesco Nasdaq-100)
> • 30% XLE (Energy Select Sector SPDR)
> • Buy & hold puro, no rebalancing
> • Periodo 1999-2025 (vincolo: lancio QQQ a marzo 1999)
>
> Benchmark: SPY 100% (l'S&P 500 ETF).
>
> Aggiungo per controllo: QQQ 50/XLE 50 e QQQ 100% per isolare l'effetto dell'aggiunta XLE.

---

## 3/9 — Il framework "Battere il mercato?"

> Inauguro qui un format ricorrente del blog. 7 criteri di validazione:
>
> 1. CAGR mediano rolling ≥ benchmark
> 2. Win rate ≥ 60%
> 3. Volatilità ≤ benchmark × 1.10
> 4. Max DD mediano ≤ benchmark × 1.10
> 5. Sharpe ≥ benchmark
> 6. Calmar ≥ benchmark
> 7. Sortino ≥ benchmark
>
> Vince = 7/7. Parziale = 4-6/7. Non vince = ≤3/7.

---

## 4/9 — Risultati full-sample

> Sui 26 anni 1999-2025:
>
> SPY 100%:        CAGR 8.34%, Vol 19.3%, MDD -55%
> QQQ 70/XLE 30:   CAGR 9.83%, Vol 24.5%, MDD -72%
> QQQ 50/XLE 50:   CAGR 9.34%, Vol 24.4%, MDD -63%
> QQQ 100%:        CAGR 10.47%, Vol 27.0%, MDD -83%
>
> La strategia BATTE in CAGR di 1.49pp/anno. Ma paga +27% di volatilità e drawdown 17pp peggiore.

*Allegare grafico: 01_equity_curves.png*

---

## 5/9 — A 10 anni la strategia vince in CAGR

> Rolling 10Y, CAGR mediano:
>
> • QQQ 70/XLE 30: 11.53%
> • SPY 100%: 8.24%
>
> Differenza: +3.29 punti percentuali all'anno.
>
> Capitalizzato su 10 anni: 1$ → 2.97$ con la strategia vs 1$ → 2.21$ con SPY. 35% di capitale in più nel mediano.

*Allegare grafico: 02_cagr_10y.png*

---

## 6/9 — Ma vince in 5/7 metriche solo

> Scorecard 10Y vs SPY:
>
> ✓ CAGR mediano (+3.29pp)
> ✓ Max DD mediano (in linea)
> ✓ Sharpe (0.42 vs 0.41)
> ✓ Sortino (0.60 vs 0.58)
> ❌ Win rate (55.9% < 60%)
> ❌ Volatilità (+27% vs benchmark)
> ❌ Calmar (0.14 < 0.15) — il drawdown -72% costa
>
> Vince 4/7. Parziale.

---

## 7/9 — La logica macro funziona ma non basta

> L'aggiunta di XLE riduce il MDD da -83% del 100% Nasdaq a -72% della 70/30. Differenza di 11 punti percentuali.
>
> Ma non basta a scendere al -55% di SPY. La diversificazione tech/energy dimezza il rischio rispetto al puro Nasdaq, ma il punto di partenza era troppo penalizzato.
>
> Il decoupling esiste — ma il livello di rischio resta strutturalmente alto.

---

## 8/9 — Per chi può avere senso

> Solo se:
>
> ✓ Orizzonte ≥10 anni (sotto, il vantaggio CAGR scompare)
> ✓ Capacità di tenere attraverso un -70% senza vendere
> ✓ Solo come tilt sul 20-30% del portafoglio, non come totale
> ✓ Conviction sulla logica macro (non un'allocazione "perché ho letto un thread su X")
>
> Per accumulo standard: MSCI World resta la scelta più solida.

---

## 9/9 — CTA

> "Mixare due settori decorrelati = batte il mercato"?
>
> Sui dati: parzialmente vero. Genera valore in alcune dimensioni, in altre no.
>
> Sul blog: l'analisi completa, la scorecard a 7 criteri, il framework che useremo per testare ogni futura strategia che mi propone qualche lettore.
>
> Hai una strategia da testare? Mandamela.
>
> [link al post]
>
> #ETF #Investimenti #Backtest

---

## Note operative

- **Il post 1 è il pilastro**: l'allegato della scorecard è quello che farà girare lo screenshot. Verifica che il PNG sia leggibile (titolo, ✓/✗ chiari).
- **Quote tweet utili a 24-48h**:
  - "La strategia 70/30 QQQ-XLE dimezza il drawdown del 100% Nasdaq (da -83% a -72%) ma resta lontana dal -55% di SPY. Decoupling tech/energy reale ma non sufficiente."
  - "Sui 26 anni 1999-2025 la strategia produce $12.32 vs $8.42 di SPY per ogni dollaro investito. Ma per arrivarci ti serve sopportare un -72% di drawdown."

- **Pushback prevedibili**:
  - "Hai testato dal 1999, hai preso il dot-com bottom!" → vero, è il vincolo dei dati QQQ. Ma gli altri 24 anni di periodo sono tutto ciò che abbiamo. Il framework sarebbe identico su altri periodi.
  - "Il rebalancing avrebbe migliorato il risultato!" → forse, ma rebalancing porta costi di transazione e tax drag che il buy & hold non ha. Articolo specifico in coda sulla questione.
  - "XLE è un settore, non un asset class!" → vero, e l'articolo lo dichiara. Aumenta il rischio specifico di un singolo settore concentrato. Non è una critica al framework — è una critica alla strategia stessa.
