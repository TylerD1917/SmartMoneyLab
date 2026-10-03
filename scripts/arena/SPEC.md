# AI Investing Arena — Specifica v1 (bozza per revisione)

Esperimento **forward** e **pre-registrato**: alcuni LLM competono nello stock-picking
con regole identiche, tutte le posizioni dichiarate, dati e codice trasparenti. Sezione /lab.
Non è consulenza: è un esperimento tra modelli.

---

## 1. Principi (non negoziabili)
- **Parità informativa**: ogni periodo *noi* costruiamo UN pacchetto dati identico e lo diamo
  a tutti i modelli. I modelli NON chiamano API: ragionano solo sul pacchetto. Elimina le
  differenze di knowledge-cutoff e i vantaggi d'accesso.
- **Riproducibilità**: pacchetto, prompt e decisioni di ogni periodo sono archiviati (JSON) e
  pubblicabili. Chiunque può rifare i conti.
- **Pre-registrazione**: regole, universo e prompt pubblicati PRIMA di iniziare. Non si toccano
  in corsa (se cambiamo qualcosa, si dichiara e si versiona).
- **Onestà statistica**: pochi modelli su pochi mesi = il vincitore a breve è in gran parte
  fortuna. Lo diciamo apertamente e mostriamo un benchmark + un controllo casuale.

## 2. Cadenza
- **Decisioni: ogni 2 settimane** (lunedì, alla chiusura del venerdì precedente come as-of).
- **Mark-to-market + classifica pubblica: ogni settimana** (NAV aggiornato anche nelle settimane
  senza decisione).
- Esecuzione delle operazioni: al **primo prezzo disponibile dopo la decisione** (open del giorno
  seguente), per evitare look-ahead.

## 3. Universo (fisso, generoso, US-listed)
~170-190 strumenti, **quotati USA** (dati yfinance puliti). File: `universe.json`.
- **~100 azioni**: componenti S&P 100 (mega/large cap USA).
- **~50-70 ETF**: broad market (SPY/VOO/QQQ/IWM…), geografici (VEA/VWO/EFA/EEM/EWJ/EWZ…),
  settoriali (SPDR XLK/XLF/XLE/XLV/XLI/XLY/XLP/XLU/XLB/XLRE/XLC), fattoriali/tematici (MTUM/VLUE/QUAL/ARKK…).
- **~10 ETC/ETN**: materie prime e metalli (GLD/SLV/PPLT/PALL/USO/UNG/DBC/CORN…) e crypto-exposure
  (es. BITO/ETHU o equivalenti spot US).
- **Escluso in v1**: ETF a leva/inversi (2x, -2x). Motivo: reset giornaliero → decadenza su orizzonti
  di settimane (rumore, non skill) e reintroduce leva/varianza. Candidati a uno sleeve v2.
- Nota: usiamo i **ticker USA** per la qualità del dato; è un esperimento sulla bravura dei modelli,
  non una lista di strumenti acquistabili in Italia. Dichiarato nelle regole.

## 4. Portafoglio e regole di trading
- Capitale iniziale virtuale: **100.000 $** per modello.
- **Max ~10 posizioni** aperte contemporaneamente.
- **Cap per singola posizione: libero** (concentrazione ammessa).
- Strumenti: **long e short** su stocks / ETF / ETN / ETC dell'universo.
- **Cash ammesso** (può restare non investito).
- **Niente leva**: esposizione **lorda** (Σ|long| + Σ|short|) ≤ 100% dell'equity. Gli short liberano
  potere d'acquisto ma dentro questo tetto.
- **Costi realistici** su ogni operazione:
  - commissione: es. 0,05% del nozionale (configurabile),
  - spread/slippage: es. 0,05% del nozionale,
  - costo prestito sugli short: es. 0,3%/anno pro-rata sul periodo di detenzione.
  (Parametri in `config.json`, dichiarati.)

## 5. Il pacchetto informativo (`packet_<date>.json`)
Identico per tutti. Point-in-time (solo dati fino all'as-of). Contenuto:
```json
{
  "as_of": "2026-09-25",
  "period": "2026-W39",
  "macro": {
    "indices": {"SPX": {"last": 0, "ret_1w": 0, "ret_1m": 0, "ret_ytd": 0}, "NDX": {}, "RUT": {}, "STOXX": {}},
    "rates": {"UST10Y": 0, "UST2Y": 0, "FEDFUNDS": 0},
    "other": {"VIX": 0, "DXY": 0, "GOLD": 0, "WTI": 0, "BTC": 0}
  },
  "instruments": [
    {"ticker": "AAPL", "class": "stock", "sector": "Tech",
     "price": 0, "ret_1w": 0, "ret_1m": 0, "ret_3m": 0, "ret_12m": 0,
     "range_52w": [0, 0], "pe": 0, "div_yield": 0, "avg_vol": 0}
  ],
  "news": [
    {"date": "2026-09-24", "source": "Reuters", "title": "…", "summary": "una riga", "url": "…", "tickers": ["AAPL"]}
  ]
}
```
- Dati strumenti/macro: **yfinance** (gira su GitHub Action; nel sandbox è bloccato).
- Notizie: digest identico per tutti — **solo titolo + una riga + fonte + link** (niente testo
  integrale, per copyright). Fonti: RSS autorevoli o news API (Finnhub/NewsAPI/GDELT; yfinance `.news`).
  Top N market-moving della settimana + eventuale sezione per-ticker.

## 6. Le decisioni (`decision_<model>_<date>.json`)
Ogni modello riceve pacchetto + il **proprio stato portafoglio** e restituisce SOLO questo JSON:
```json
{
  "as_of": "2026-09-25",
  "rationale": "tesi complessiva del periodo, max ~120 parole",
  "orders": [
    {"ticker": "XLE", "action": "open|increase|trim|close",
     "side": "long|short", "target_weight": 0.15,
     "thesis": "1-2 frasi", "target_price": null, "stop": null}
  ]
}
```
- `target_weight` = peso a mercato desiderato sul totale equity (il motore calcola il delta ordini).
- Output validato: JSON malformato o che viola i vincoli (≤10 posizioni, lordo ≤100%, universo) →
  ordine rifiutato e loggato; il portafoglio resta invariato per quell'ordine.

## 6-bis. Controllo di coerenza (dal 2026-10-03)

Una decisione puo' essere internamente contraddittoria: il 2026-09-17 un modello ha
aperto EDV (Treasury a duration lunga) con `side: long` scrivendo come tesi *"SHORT
duration lunga: ... gli zero-coupon lunghi restano il segmento piu' vulnerabile"*, e
il suo stesso rationale elencava EDV fra le coperture short. La pipeline ha eseguito
l'ordine alla lettera, perche' nessuno controllava la coerenza fra `side`, `thesis` e
`rationale`.

**Prevenzione.** Ogni ordine dichiara `attesa` (`rialzo|ribasso`): cosa il modello si
aspetta dal PREZZO dello strumento. `side` e `attesa` devono combaciare, quindi una
tesi ribassista su una posizione long diventa meccanicamente visibile. Il prompt
avverte esplicitamente sugli strumenti a relazione inversa (bond a duration lunga).

**Rilevazione** (`coherence.py`, quattro controlli, nessuna chiamata API):

| controllo | severita' | cosa guarda |
|---|---|---|
| `attesa_vs_side` | hard | `attesa` contraddice `side` |
| `rationale_vs_side` | hard | il rationale nomina il ticker con la direzione opposta, nella *sua* proposizione |
| `tesi_vs_side` | hard | la tesi apre con un marcatore di direzione opposto, o contiene SHORT/LONG in maiuscolo (le negazioni, "non shortare qui", non contano) |
| `esposizione` | soft | il gross/net dichiarato non torna con gli ordini |
| `tono_tesi` | soft | tesi interamente ribassista su una posizione long (o viceversa) |

Il controllo sull'esposizione resta un indizio e **non** sale mai a `hard`: "net" e'
ambiguo. Nel caso EDV il net dichiarato era "~70%", che con EDV long fa 73% e con EDV
short 57% — il 70% torna solo leggendo "net" come "il lato long dopo le coperture".

**Reazione.** Se la severita' finale e' `hard`, `run_agents` ri-sottopone la
contraddizione **una volta sola allo stesso modello**, citandola e senza suggerire
quale lettura sia corretta. Quello che il modello risponde la seconda volta viene
eseguito alla lettera. **Il codice non riscrive mai un ordine**: se lo facesse, la
scelta non sarebbe piu' del modello e l'esperimento non misurerebbe piu' nulla. Una
contraddizione che sopravvive alla ri-domanda viene eseguita e pubblicata con il flag
(`decisions.<model>.coherence` in `arena.json`).

Audit di file gia' scritti: `python scripts/arena/coherence.py state/decisions/*.json`
(exit 1 se trova una contraddizione `hard`). Casi di prova, inclusi i falsi positivi
da non produrre: `python scripts/arena/test_coherence.py`.

## 7. Prompt comune
Identico per tutti (cambia SOLO il modello). Contiene: ruolo, regole, universo (o riferimento),
formato JSON d'uscita, il pacchetto, lo stato del portafoglio. **Temperatura bassa, 1 sola chiamata
per modello per periodo.** Prompt + risposta grezza archiviati. Bozza in `prompt_template.md`.

## 8. Ledger e settlement
- `portfolio_<model>.json`: posizioni (ticker, side, qty, prezzo medio), cash, storico ordini.
- Settlement: applica ordini al prezzo d'esecuzione, addebita costi, aggiorna cash e posizioni.
- Mark-to-market settimanale → `nav_<model>` (serie storica) + metriche (rendimento, vol, drawdown, Sharpe).

## 9. Output pubblico (/lab)
`public/tools/arena/…json`: classifica modelli (rendimento, Sharpe, vs benchmark), posizioni correnti
di ciascuno con tesi, curve NAV, archivio decisioni/transcript. Benchmark = **ACWI o S&P 500**.
Controllo = **portafoglio casuale** (pesi random nell'universo, stessi costi) per misurare la fortuna.

## 10. Architettura tecnica (riusa l'infra esistente)
Cartelle proposte: motore in `scripts/arena/`, output in `public/tools/arena/`.
Pipeline (GitHub Action schedulata, come la leaderboard):
1. `build_packet.py` → costruisce `packet_<date>.json` (yfinance + news).
2. `run_agents.py` → per ogni modello, chiama la sua API con pacchetto + portafoglio → `decision_*.json`.
3. `settle.py` → valida, applica ordini, costi, MTM, aggiorna ledger.
4. `publish.py` → scrive i JSON pubblici per /lab.
- **Modelli v1**: Gemini, OpenAI/GPT, Kimi/Moonshot, Claude (chiavi come secret; versioni pinnate).
- Secret: chiavi dei 4 modelli + news API. yfinance non serve chiave.

## 11. Caveat pubblici (sempre)
- Il vincitore a breve è in gran parte **fortuna** (pochi modelli, poche osservazioni).
- **Esperimento tra modelli, NON consulenza** né raccomandazione dell'autore. Disclaimer visibile.

## 12. Roadmap v2 (non ora)
- Blocco **options sentiment** nel pacchetto da **Tastytrade** (IV, put/call, skew) → recupera anche l'idea #1.
- **Campo aperto a due fasi** (i modelli propongono ticker → noi recuperiamo dati identici → decidono).
- **Sleeve leva** (ETF 2x/-2x) come variante dichiarata, o regola "nozionale 2x verso il tetto".

## 13. Cosa serve da Tyler per finalizzare
- Le tue **liste ticker/ISIN** (ETF + ETC/ETN): le mappo ai corrispettivi **US-listed** e assemblo `universe.json`.
- Conferma **modelli** in gara e chi fornisce le **chiavi API** (Gemini/OpenAI/Moonshot/Anthropic + news API).
- Ok sui **parametri costi** (commissione/spread/prestito) e sul **benchmark** (ACWI vs S&P 500).

## Memoria degli agenti (v1)
Obiettivo: coerenza nel tempo e serieta' dell'esperimento.
- Ogni ordine richiede una `thesis` non vuota; l'assenza viene marcata "(nessuna giustificazione fornita)".
- Prima di decidere, il modello riceve la propria memoria: ultime N=`memory.lookback` decisioni (data, rationale,
  mosse) + curva NAV. Ricostruita da `state/decisions/` + NAV, nessuno store dedicato.
- Il prompt impone di restare coerenti con le tesi passate e di dichiarare esplicitamente i cambi di rotta.
- Le tesi/rationale sono gia' pubblicate in `arena.json` -> /lab (trasparenza pre-registrata).

## Notizie (v1)
- Fonti: feed RSS curati in `config.json` (economia, mercati, banche centrali, geopolitica) + yfinance megacap.
- Volume: fino a 40 titoli, max `per_feed` per fonte, deduplicati per titolo, ordinati per data.
- Contenuto: titolo + sommario breve + fonte + data + link (no full-text, copyright).
- Robustezza: parser RSS/Atom stdlib; feed KO saltati e loggati; conteggi per-feed a ogni run.
- Equita': news costruite una volta e incluse nel packet identico per tutti; archiviate = riproducibili.
- Upgrade possibili: digest macro sintetico via modello; API news dedicata; pesatura per rilevanza.
