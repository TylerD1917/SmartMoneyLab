# Bozza post r/ItaliaPersonalFinance

**Stato**: bozza, non pubblicata
**Strategia**: valore nel corpo, link soft in fondo, domanda finale per aprire la discussione

---

## Titolo

Ho ricalcolato il rendimento storico di 5 indici azionari al netto di TER, ritenute, bollo, 26% e inflazione italiana (fino a 56 anni di dati, in euro)

---

## Corpo

Mi sono chiesto una cosa che mi sembra poco trattata: i rendimenti storici che circolano sono quasi sempre lordi, in dollari, e senza fiscalità. Un investitore italiano però incassa altro. Ho provato a quantificare la differenza.

**Metodo.** Cinque indici in total return (MSCI World dal 1969, Nasdaq Composite dal 1975, S&P 500 dal 1988, MSCI ACWI IMI dal 1994, Russell 2000 dal 1995), tutti convertiti in euro. Su ciascuno ho simulato un ETF con TER realistico, più il drag da ritenuta estera sui dividendi (gli indici MSCI sono gross, un ETF i dividendi non li incassa interi), più il bollo dello 0,2% annuo, più il 26% sulla plusvalenza al riscatto. Poi ho deflazionato con l'indice dei prezzi italiano. Finestre mobili di 1, 3, 5, 10, 15 e 20 anni a passo mensile, quindi niente data di partenza scelta ad arte.

**Risultati principali, MSCI World, orizzonte 20 anni (440 finestre):**

* rendimento lordo dell'indice, mediana: 7,96% annuo
* al netto di costi e 26%: 6,10% annuo, cioè 1 euro diventa 3,27
* al netto anche dell'inflazione: 1,96% annuo, cioè 1,47 in potere d'acquisto
* finestre ventennali chiuse in perdita reale: 21,8%

**Tre cose che non mi aspettavo.**

1. L'erosione annualizzata *diminuisce* con l'orizzonte, da 3,28 punti percentuali a un anno a 1,87 a vent'anni. Dipende dal fatto che il capital gain si paga una volta sola al realizzo, quindi spalmato su vent'anni pesa meno per anno. La conseguenza pratica è che il vantaggio dell'accumulazione non è solo il differimento, è che il differimento vale di più quanto più aspetti.

2. Il TER è la voce minore. Su vent'anni: 0,70 punti annui per l'insieme TER più ritenuta più bollo, contro 1,16 punti di imposta. La ritenuta estera sui dividendi (circa 0,25-0,30 punti su un indice a forte peso USA) pesa più del TER di quasi tutti gli ETF larghi, e non la scegli.

3. Il 26% si paga sulla plusvalenza *nominale*, quindi si versa imposta anche sulla parte di guadagno che è solo recupero dell'inflazione. Su finestre con inflazione alta il prelievo effettivo sul guadagno reale è parecchio sopra il 26%.

**Limiti, dichiarati.** Gli ETF sono simulati e non osservati, perché in euro non ci sono serie abbastanza lunghe (il più vecchio UCITS sul World è del 2005 e darebbe una sola finestra ventennale). Il Nasdaq è approssimato con il Composite più un dividendo figurato dello 0,75% e replica il Composite, non il Nasdaq-100 che replicano gli ETF veri. Le finestre si sovrappongono, quindi le percentuali vanno lette come frequenze storiche, non come probabilità. Nessuna compensazione di minusvalenze.

Ho pubblicato metodo, tabelle complete per tutti gli orizzonti e lo script sul mio blog, se a qualcuno serve il dettaglio: smartmoneylab.it

**La domanda che lascio:** quando fate i vostri piani, che numero usate come rendimento atteso dell'azionario? Io fino a ieri usavo il 7% lordo e mi accorgo che è un'ipotesi molto più ottimista di quanto pensassi.

---

## Note operative

- NON droppare il link secco: il link sta in fondo, dopo il valore, ed è testuale.
- Rispondere ai commenti tecnici con i numeri, non con rimandi al blog.
- Il gancio competitivo per un sub italiano è "al netto della fiscalità italiana": i backtest che girano sono lordi e americani.
- Se il post va bene, il seguito naturale è un commento con la tabella completa dei cinque indici.
