# Bozza post Reddit — Mutuo fisso o variabile

**Subreddit target**: r/ItaliaPersonalFinance (in seconda battuta r/finanzapersonale)
**Flair suggerito**: Analisi / Dati
**Regola d'oro**: valore nel post, link soft in fondo, niente self-promo secca.

---

## Titolo (scegline uno)

- Fisso o variabile? Ho simulato 10.000 mutui a 30 anni su 26 anni di dati BCE. Il variabile costa meno in 2 casi su 3, ma la surroga ribalta tutto
- Ho testato fisso vs variabile su 26 anni di tassi BCE reali: quello che decide è un solo numero (e non è quello che pensate)

---

## Corpo del post

Premessa: lo faccio per curiosità personale, dati e codice open, linko in fondo.

"Meglio fisso o variabile?" è la prima domanda di chi accende un mutuo, e di solito si risponde con un aneddoto. Ho provato a rispondere coi numeri: tassi realmente contrattati sui mutui casa in Italia (statistiche BCE, dal 2000) + Euribor 3M dal 1994, mutuo da 200.000€ a 30 anni, ammortamento francese. Due binari: replay storico delle coorti 2000-2025 e Monte Carlo su 10.000 percorsi trentennali.

**1. Sul puro costo, in media vince il variabile.** Su 30 anni completi costa meno degli interessi nel ~66% degli scenari, con un risparmio mediano di circa 34.000€. Il fisso incorpora già i rialzi attesi dal mercato più un premio per la certezza: in media parti pagando di più. Scegliere il variabile non è "scommettere che i tassi restano bassi", è scommettere che restino più bassi di quanto la curva già prevede.

**2. Ma il rischio del variabile è concreto.** Nel 74% dei percorsi la rata del variabile a un certo punto supera quella del fisso, e nel 32% la supera di oltre il 30%. Esempio reale: chi ha acceso un variabile nel 2021 (rata ~670€) si è ritrovato oltre 1.140€ nel 2022-2023, +71%. Il fisso, nella stessa casa, non si è mosso.

**3. La surroga cambia le carte, e quasi nessuno la modella.** In Italia rifinanziare il fisso con un nuovo fisso è gratis dal 2007 (Legge Bersani). È un'opzione a senso unico: se i tassi scendono ti riabbassi, se salgono tieni il tuo. Modellandola (surroga se il fisso di mercato scende di almeno 0,75pp, valutata una volta l'anno), la probabilità che il fisso costi meno del variabile passa dal 34% al 57%, e la mediana si capovolge: non è più il variabile a risparmiare 34k, è il fisso-con-surroga a risparmiarne ~9k. In media 1,5 surroghe in 30 anni.

**4. Il fattore che decide è uno solo: il premio iniziale del fisso** (quanto costa in più del variabile all'accensione). Premio negativo (curva piatta/invertita) → il fisso vince ~58% delle volte; premio +2,5pp → solo ~11%. Una curva pulita e monotona. Il replay storico ci si incastra: le coorti 2000-2015 hanno vinto col variabile (fisso partiva caro), le 2016-2022 col fisso (curva piatta, poi shock 2022).

**Dove siamo oggi (luglio 2026):** fisso ~3,56%, variabile ~2,99% → premio +0,57pp, basso. A questo livello il fisso costa meno nel 39% dei casi senza surroga, ma nel 60% con surroga. Leggermente a favore del fisso, ma dipende dalla BCE.

Caveat onesti: è un modello semplificato (surroga senza attriti di accettazione/tempi reali; fisso di mercato futuro approssimato; niente costi/fiscalità perché si eliminano nel confronto). Non è una previsione, è una distribuzione storica.

Metodo completo, grafici e codice qui: [link articolo]. Domande e critiche al metodo ben accette.
