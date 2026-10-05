# Caption Instagram: la prima allocazione dell'AI Investing Arena

**Account**: @smartmoneylab_it
**Asset**: `carosello/01.png` … `06.png` (6 slide)
**Uso**: secondo post dell'arena, dopo il carosello di lancio fissato in evidenza. Da pubblicare **prima del 5 ottobre**, quando i modelli riallocano.

---

## Caption proposta

Quattro intelligenze artificiali hanno letto lo stesso identico quadro di mercato e ne hanno tirato fuori quattro portafogli opposti.

Il quadro è questo, e lo citano tutte e quattro nella tesi che hanno scritto: Fed che alza i tassi per la prima volta in tre anni, decennale americano al 5,01%, petrolio sopra i 100 dollari. Stessa diagnosi, parola per parola. Poi le prescrizioni divergono in modo clamoroso.

Gemini si è presa tutto il mercato: dieci titoli, 10% ciascuno, zero cassa e zero posizioni corte. Esposizione netta 100%. Energia, banche, big tech, oro, difesa, in parti uguali.

Kimi ha fatto l'opposto: quattro posizioni corte e un'esposizione netta del 37%. Corta su semiconduttori, Treasury lunghi, small cap e costruzioni residenziali. È la scommessa più aggressiva del gruppo, solo che è aggressiva al ribasso.

In mezzo, GPT con un quarto del capitale parcheggiato in liquidità remunerata, difensivi di qualità e un solo short su Tesla. E Claude con energia, oro e materie prime, esposizione netta al 73%.

Una nota tecnica che vale la pena fare, perché è il tipo di dettaglio che fa sbagliare le letture: la cassa da sola inganna. Kimi risulta al 63% di liquidità, ma vendere allo scoperto accredita denaro sul conto, quindi quel 63% non è prudenza, è il residuo contabile di trenta punti di posizioni corte. Il numero da guardare è l'esposizione netta.

Su 28 titoli diversi in tutto, solo tre sono stati scelti da tre modelli su quattro: Berkshire Hathaway, un ETF monetario a tasso variabile e il Russell 1000 Value. Nessuno dei tre è una scommessa sull'intelligenza artificiale. Le IA, messe a investire, hanno comprato valore, liquidità e assicurazioni.

C'è un ultimo dato che mi ha colpito. Tre modelli su quattro tengono una fetta del capitale in un ETF monetario a tasso variabile: il modo più noioso che esiste di stare sui mercati. GPT ci mette un quarto di tutto. Gemini è l'unica che non ha un solo dollaro di obbligazionario. Con il decennale al 5%, la scelta più condivisa fra quattro intelligenze artificiali è stata la liquidità remunerata.

I modelli riallocano il 5 ottobre. Tesi complete, posizioni e classifica giornaliera sul blog, link in bio.

È un esperimento pubblico, non un consiglio di investimento.

---

## Hashtag (primo commento, 15, mix di volumi)

#intelligenzaartificiale #ai #chatgpt #gemini #claude #investimenti #borsa #azioni #assetallocation #finanzapersonale #educazionefinanziaria #mercatifinanziari #culturafinanziaria #esperimento #investireinitalia

---

## Note operative

- La slide forte è la 3 (100% contro 37%): stesso giorno, stessi dati, esposizione al mercato quasi tripla. È il gancio e la copertina migliore.
- La slide 5 (tre titoli in comune su 28, nessuno legato all'IA) è il contenuto che differenzia: richiede di aver guardato i dati grezzi e non si copia da un comunicato.
- Numeri citati, tutti verificabili in `public/tools/arena/arena.json`: esposizione netta Gemini 100%, GPT 85%, Claude 73%, Kimi 37%; Kimi 4 short e 63% di cassa contabile; GPT 25% in USFR e un solo short (TSLA); 28 titoli distinti; BRK-B, USFR e IWD scelti da 3 modelli su 4.
- USFR (monetario a tasso variabile): Claude 10%, GPT 25%, Kimi 15%, Gemini zero obbligazionario. Verificato sui campi `side`/`target_weight` in `state/decisions/` del 17/09.
- Non trasformarlo in un post contro l'IA. Il taglio è "guarda cosa hanno scelto e perché", non "ecco quanto sono scarse": con un ciclo solo di dati qualunque verdetto sarebbe indifendibile.
