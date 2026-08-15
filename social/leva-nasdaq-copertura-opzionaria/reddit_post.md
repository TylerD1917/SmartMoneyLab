# Bozza post Reddit — Nasdaq a leva 2x con copertura opzionaria

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: il valore sta NEL post. Link al blog solo in fondo, come approfondimento + codice.

---

## Titolo (scegline uno)

- Ho testato su 50 anni una strategia a leva 2x sul Nasdaq con copertura in opzioni: batte il mercato anche corretto per il rischio (ma con drawdown del −94%)
- Nasdaq a leva 2x + put di copertura vs Nasdaq semplice: 50 anni di backtest, lordo e netto tasse

---

## Corpo del post

Premessa: non sono un consulente, faccio queste simulazioni per curiosità personale. Dati e codice sono linkati in fondo. È una strategia a LEVA: potenzialmente devastante, leggete fino ai caveat.

La leva sul Nasdaq, da sola, è fragile: un ETF 3x si azzera nei grandi crolli per via del decadimento giornaliero. La domanda: una copertura tattica in opzioni può domarla abbastanza da battere il mercato in modo consistente?

**La strategia.** 95% in un ETF a leva 2x sul Nasdaq, 5% in una put OTM annuale (strike −12,5%). Se durante l'anno la put arriva a valere il doppio del premio, la vendo e tengo l'incasso in liquidità (de-risking); ricompro una nuova put dall'incasso, senza toccare l'ETF. Rinnovo annuale.

**Metodo.** Nasdaq (Composite) dal 1975 al 2026, Total Return. ETF a leva sintetico (TER + costo di finanziamento). Opzioni prezzate con Black-Scholes, con ipotesi volutamente a sfavore della strategia: volatilità implicita = realizzata +5 punti, slippage 3%, liquidità remunerata solo 2,5%. Lordo e netto Italia 26%. Finestre mobili 10/15/20 anni.

**Risultati (CAGR mediano, netto):**

- 10 anni: strategia 15,0% vs Nasdaq 10,3%
- 15 anni: 12,4% vs 9,9%
- 20 anni: 10,8% vs 9,4%

Batte il Nasdaq anche su **Sharpe, Calmar e Sortino** (metriche corrette per il rischio) e nel **66-72% di tutte le finestre**. Quindi non è "solo leva": la copertura aggiunge un vantaggio reale. È diverso da quanto avevo trovato testando la leva pura o le LEAPS, dove leva = più rendimento e più rischio in egual misura.

**Il prezzo, enorme.** Drawdown mediani da −60% (10 anni) a −94% (20 anni), contro −36/−78% del Nasdaq. Le stesse finestre che rendono tanto hanno attraversato cadute che quasi nessuno regge emotivamente. E a 10 anni l'11% delle finestre chiude comunque in negativo (a 20 anni nessuna). La leva coperta premia orizzonti lunghi e stomaci fortissimi.

**Dettaglio interessante:** il 3x rende di più sul CAGR ma con drawdown −98% e rischio/rendimento uguale o peggiore → il 2x è lo sweet spot. E il modo di usare l'incasso della put (liquidità vs ricomprare ETF) conta meno di quanto pensassi sul 2x.

**Limiti:** ETF sintetico su indice; Black-Scholes con volatilità realizzata; 50 anni dominati da un toro tech secolare che potrebbe non ripetersi; e soprattutto serve una disciplina di esecuzione che i backtest non catturano.

Analisi completa con grafici, framework 6+1 e codice: [link]. Curioso di sapere se qualcuno l'ha mai implementata davvero e come ha gestito i drawdown.
