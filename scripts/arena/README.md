# AI Investing Arena — motore

Esperimento forward, pre-registrato: 4 modelli LLM competono nello stock-picking con lo STESSO pacchetto
di dati/notizie, tutte le posizioni dichiarate, dati e codice trasparenti. Output pubblicato in /lab.
Specifica completa: `SPEC.md`. Universo: `universe.json`.

## Come gira (principio)
Ogni periodo il motore costruisce UN pacchetto informativo identico e lo passa a tutti i modelli.
I modelli **non chiamano API**: ragionano e restituiscono un JSON di decisioni. Questo garantisce parità,
riproducibilità (pacchetto/decisioni archiviati) e semplicità.

## Requisiti
- Python 3 con `yfinance`, `pandas`, `numpy`.
- Chiavi modelli come **variabili d'ambiente / secret** (mai nel repo): `OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `ANTHROPIC_API_KEY`, `MOONSHOT_API_KEY`. Senza una chiave, quel modello va in **STUB** (nessuna operazione),
  così la pipeline gira comunque (utile per testare).
- yfinance è bloccato nel sandbox cloud: il motore gira su **GitHub Action** o sulla macchina di Tyler.

## Comandi
```bash
python scripts/arena/run_period.py init       # una volta: crea i portafogli (100k ciascuno)
python scripts/arena/run_period.py auto        # da schedulare OGNI settimana: decide da solo
python scripts/arena/run_period.py decision    # forza un periodo di decisione (build->agents->settle->publish)
python scripts/arena/run_period.py weekly      # forza solo mark-to-market + publish
```
`auto` guarda l'ultima decisione: se sono passati >= `decision_days` (14) fa un periodo di **decisione**,
altrimenti solo **mark** settimanale. Così basta un unico cron settimanale.

## Flusso di un periodo di decisione
1. `build_packet.py` → dati yfinance (prezzi, rendimenti, 52w, PE/yield), macro, digest notizie (RSS curati + yfinance) → `state/packets/packet_<date>.json`.
2. `run_agents.py` → per ogni modello: prompt (pacchetto + suo portafoglio) → chiamata API → JSON decisione validato → `state/decisions/`, transcript in `state/transcripts/`.
3. `settle.py` → applica le decisioni ai prezzi del pacchetto, addebita costi (commissione+spread; prestito short), aggiorna `state/portfolio_<id>.json`, registra la NAV. Include il **portafoglio di controllo casuale**.
4. `publish.py` → `public/tools/arena/arena.json` (classifica, posizioni, NAV, decisioni, benchmark ACWI+S&P 500).

## Regole (in `config.json`)
100k virtuali · max 10 posizioni · cap per posizione libero · long/short su stocks/ETF/ETN/ETC ·
niente leva (esposizione lorda ≤ 100%) · costi 0,05% commissione + 0,05% spread + 0,3%/anno prestito short ·
decisioni ogni 14 giorni, NAV/classifica ogni 7. Vincoli applicati in automatico: oltre 10 posizioni → decisione
rifiutata (portafoglio invariato); esposizione lorda oltre il cap → scalata proporzionalmente.

## Modelli
In `config.json`: id, provider (openai/google/anthropic/moonshot), nome modello (flagship di settembre 2026, pinnati),
env della chiave. Verifica la stringa esatta sui doc ufficiali del provider quando generi la chiave.

## GitHub Action
Vedi `arena_workflow_example.yml` (da mettere in `.github/workflows/arena.yml`, aggiungendolo a mano perché i
file workflow non sono scrivibili dagli strumenti remoti). Cron settimanale → `run_period.py auto`. Chiavi come secret.
Committa lo stato aggiornato (`state/`, `public/tools/arena/arena.json`) come fa il bot della leaderboard.

## Coerenza delle decisioni

`coherence.py` controlla che `side`, `attesa`, `thesis` e `rationale` di ogni ordine
dicano la stessa cosa, prima del settle. Se c'e' una contraddizione dimostrata,
`run_agents` la ri-sottopone una volta al modello e poi esegue qualunque cosa risponda:
nessun ordine viene mai riscritto dal codice. Dettagli in `SPEC.md` (sezione 6-bis).

    python scripts/arena/coherence.py scripts/arena/state/decisions/*.json   # audit, exit 1 se hard
    python scripts/arena/test_coherence.py                                   # 13 casi di prova

## Note
- Pre-registrare regole/universo/prompt PRIMA di iniziare (vedi SPEC).
- Caveat pubblici: vincitore a breve = fortuna; esperimento tra modelli, non consulenza.
- v2: options sentiment da Tastytrade nel pacchetto; universo a due fasi; sleeve leva.

## Memoria degli agenti
Prima di ogni decisione, ogni modello riceve la propria **memoria**: le ultime `memory.lookback` (default 4)
decisioni passate — data, tesi (`rationale`), mosse fatte — e la curva NAV (performance da inizio esperimento).
Non serve storage nuovo: la memoria e' ricostruita rileggendo `state/decisions/decision_<id>_*.json` e la NAV.
Il SYSTEM impone **coerenza** (restare fedele alla strategia, o dichiarare esplicitamente cosa e' cambiato) e
**giustificazione obbligatoria** per ogni ordine (campo `thesis` non vuoto). Cosi' ogni modello mantiene una
linea nel tempo e le sue tesi sono pubblicate in /lab.

## Modelli pinnati (settembre 2026)
gpt = gpt-5.6-sol (OpenAI) · gemini = gemini-3.1-pro (Google) · claude = claude-opus-5 (Anthropic) ·
kimi = kimi-k3 (Moonshot). Cambiando un modello, aggiorna qui la data e la stringa.

## Notizie (fonti)
Il pacchetto include fino a `news.max_headlines` (40) titoli, presi da **feed RSS curati** definiti in
`config.json` (BBC, Guardian, Al Jazeera, CNBC, Investing.com, Fed, BCE) piu' le news yfinance taggate ai
megacap. Categorie: economia, mercati, banche centrali, geopolitica. Solo titolo + breve sommario + fonte +
data + link (niente corpo, per copyright). Parser RSS/Atom in `build_packet.py` con sola stdlib: un feed
irraggiungibile viene saltato e stampato come "KO", quindi il primo run mostra i conteggi per-feed e si
potano/aggiustano le fonti morte modificando `config.json`. Le news sono identiche per tutti i modelli e
archiviate nel packet (riproducibili).

## Stato durevole e dati derivati (regola da non violare)

L'unico stato durevole dell'arena sono **gli snapshot di allocazione** in
`state/positions/positions_{modello}_{data}.json`: cassa e quantità fotografate
da `settle.py` subito dopo ogni riallocazione, mai più riscritte. Accanto a
loro restano decisioni, packet e transcript, che sono il verbale di cosa è
stato deciso e perché.

Tutto il resto è **derivato** e viene ricalcolato da zero a ogni esecuzione:
le serie in `state/nav/`, `public/tools/arena/arena.json`, `nav_daily.csv`.
Nessuno di questi file viene mai riletto come input. Chi aggiunge codice qui
non deve introdurre un secondo autore per un dato derivato, né far dipendere il
risultato da quante volte lo script è girato in passato.

Perché la regola è scritta qui: il 2026-10-06 la Action è andata a buon fine e
ha pubblicato tutti i modelli a 100.000 e +0,00%, con le curve sparite. Il
motore scartava gli snapshot del primo segmento, faceva partire la curva dalla
data dell'ultima riallocazione (che quel giorno non aveva ancora una sessione
chiusa) e riscriveva la cassa nello stato a ogni ricostruzione. Tre modi
diversi di dipendere dalla storia delle esecuzioni invece che dai dati.

Le protezioni attuali, in ordine di intervento:

1. `nav_daily.py` si ferma se un partecipante non ha snapshot o se la sua serie
   esce vuota;
2. `publish.py` si ferma se una serie è vuota, parte più tardi o ha meno giorni
   di quella già pubblicata (`verifica_regressioni`);
3. la Action esegue `test_nav_daily.py` prima di toccare qualsiasi cosa, e
   rifiuta di committare un `arena.json` con i modelli fermi al capitale
   iniziale.

Se qualcosa si rompe di nuovo, la curva è ricostruibile in un comando dai soli
snapshot: `python scripts/arena/nav_daily.py`.
