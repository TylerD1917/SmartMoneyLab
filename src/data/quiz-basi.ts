/**
 * Domande del quiz "Da dove parto?" della home.
 *
 * Non e' un test di cultura finanziaria: serve a instradare chi arriva sul
 * sito verso la collana o verso gli studi. Da cui tre regole, da rispettare
 * se un giorno si aggiungono domande:
 *
 *  1. Si misura il GIUDIZIO, non la memoria. Chi ha capito risponde anche
 *     senza ricordare i numeri; chi ha solo letto titoli altrove sbaglia.
 *  2. Ogni domanda ha un distrattore che e' l'equivoco piu' comune, non una
 *     risposta a caso: e' quello che rende diagnostico il risultato.
 *  3. Ogni domanda punta agli episodi che la coprono. Il valore del quiz sta
 *     li': dire "ti manca il 5", non "rileggi tutto".
 */

export interface QuizEpisodio {
  n: number;
  slug: string;
  titolo: string;
}

export interface QuizDomanda {
  id: string;
  testo: string;
  opzioni: string[];
  corretta: number; // indice in `opzioni`
  spiegazione: string;
  episodi: number[]; // numeri di episodio, vedi EPISODI
}

export const EPISODI: QuizEpisodio[] = [
  { n: 1, slug: "perche-investire-inflazione", titolo: "Perché investire: cosa fa l'inflazione ai tuoi risparmi" },
  { n: 2, slug: "prima-di-investire-fondo-emergenza", titolo: "Prima di investire: fondo di emergenza, debiti e orizzonte temporale" },
  { n: 3, slug: "spese-previste-obbligazioni-scadenza", titolo: "Le spese che sai già di dover affrontare: il terzo livello" },
  { n: 4, slug: "cosa-sono-le-azioni", titolo: "Cosa sono le azioni, e come si legge il prezzo di una società" },
  { n: 5, slug: "come-funzionano-le-obbligazioni", titolo: "Cosa sono le obbligazioni, e perché il prezzo scende quando i tassi salgono" },
  { n: 6, slug: "materie-prime-e-oro", titolo: "Materie prime e oro: gli asset che non producono nulla" },
  { n: 7, slug: "cosa-e-un-etf", titolo: "Cos'è un ETF e come funziona davvero" },
  { n: 8, slug: "quale-etf-indici-settori-fattori", titolo: "Quale ETF: indici globali, paesi, settori e fattori" },
  { n: 9, slug: "quanto-costa-investire-ter-commissioni", titolo: "Quanto costa investire: TER, spread, commissioni e bollo" },
  { n: 10, slug: "rischio-volatilita-diversificazione", titolo: "Rischio, volatilità e diversificazione: cosa misura cosa" },
  { n: 11, slug: "pac-pic-cagr-xirr", titolo: "PAC o PIC, CAGR e XIRR: come si misura davvero un rendimento" },
  { n: 12, slug: "sharpe-sortino-calmar", titolo: "Sharpe, Sortino e Calmar: giudicare un portafoglio (e i loro limiti)" },
  { n: 13, slug: "costo-del-denaro-tassi-mercati", titolo: "Il costo del denaro: come i tassi muovono tutto" },
];

export const DOMANDE: QuizDomanda[] = [
  {
    id: "orizzonte",
    testo:
      "Fra tre anni devi versare un anticipo già promesso per una casa. Quei soldi, oggi, dove stanno meglio?",
    opzioni: [
      "Su un ETF azionario globale, che in media sale",
      "Su obbligazioni con scadenza coordinata alla data della spesa",
      "Metà azionario e metà liquidità, per bilanciare",
      "Su un fondo bilanciato, che è gestito da professionisti",
    ],
    corretta: 1,
    spiegazione:
      "La data in cui ti servono i soldi non ha alcun rapporto con quello che farà il mercato. Su tre anni l'azionario mondiale ha chiuso in perdita nel 21% delle finestre storiche, e una spesa già promessa non si può rimandare.",
    episodi: [2, 3],
  },
  {
    id: "flussi",
    testo:
      "Dal punto di vista di chi investe, qual è la differenza di fondo fra un'azione e un lingotto d'oro?",
    opzioni: [
      "L'oro è meno rischioso",
      "L'oro protegge dall'inflazione, l'azione no",
      "L'azione è una quota di un'attività che produce flussi di cassa, l'oro no",
      "Nessuna sostanziale, sono entrambi beni reali",
    ],
    corretta: 2,
    spiegazione:
      "È la distinzione che separa le asset class. Il valore di un'azione nasce dagli utili futuri dell'azienda; l'oro rende solo se qualcuno te lo paga più di quanto l'hai pagato tu.",
    episodi: [4, 6],
  },
  {
    id: "ter",
    testo: "Il TER di un ETF, dove lo paghi?",
    opzioni: [
      "Viene prelevato ogni giorno dal patrimonio del fondo e non lo vedi da nessuna parte",
      "Te lo addebitano una volta l'anno sul conto",
      "Lo paghi solo quando vendi",
      "È compreso nella commissione dell'intermediario",
    ],
    corretta: 0,
    spiegazione:
      "I costi che non compaiono su nessun estratto conto sono quelli che paghi più a lungo. Chi cerca il TER fra i movimenti del conto non lo troverà mai: è già dentro il prezzo.",
    episodi: [7, 9],
  },
  {
    id: "volatilita",
    testo:
      "Un fondo ha avuto una volatilità molto bassa negli ultimi cinque anni. Cosa puoi concludere?",
    opzioni: [
      "Che è un investimento prudente",
      "Che difficilmente può perdere molto",
      "Che va bene per qualsiasi orizzonte",
      "Poco: la volatilità non dice quanto può cadere, né quanto ci metterà a tornare in pari",
    ],
    corretta: 3,
    spiegazione:
      "I Treasury americani a lunga scadenza hanno la seconda volatilità più bassa fra ventidue asset class e hanno perso il 47,6% dal massimo del 2020, che a oggi non hanno ancora recuperato.",
    episodi: [10],
  },
  {
    id: "backtest",
    testo:
      'Leggi: "questa strategia ha reso il 12% annuo dal 2010 a oggi". Qual è la prima cosa da chiedersi?',
    opzioni: [
      "Quale ETF la replica",
      "Se il 12% ha battuto l'inflazione",
      "Come cambia il risultato partendo da un'altra data",
      "Chi ha fatto il backtest",
    ],
    corretta: 2,
    spiegazione:
      "Un backtest con una sola data di partenza misura la data, non la strategia. Sul mercato mondiale il miglior ventennio ha reso il 17,5% annuo e il peggiore il 2,5%: stesso indice, cambia solo il mese di ingresso.",
    episodi: [11],
  },
  {
    id: "tassi",
    testo:
      "Nel 2022 le azioni tecnologiche e le obbligazioni a lunga scadenza sono scese insieme di circa un terzo. Com'è possibile, visto che sono agli opposti per rischio?",
    opzioni: [
      "È stata una coincidenza, due crisi diverse nello stesso anno",
      "Perché entrambe promettono incassi lontani nel tempo, e il costo del denaro è raddoppiato",
      "Perché la diversificazione in realtà non funziona",
      "Per la guerra e il prezzo dell'energia",
    ],
    corretta: 1,
    spiegazione:
      "Un rialzo dei tassi toglie poco a chi incassa presto e moltissimo a chi incassa tardi, qualunque etichetta abbia lo strumento. È lo stesso meccanismo che fa scendere il prezzo di un'obbligazione lunga.",
    episodi: [13, 5],
  },
];

export interface QuizStudio {
  slug: string;
  titolo: string;
  perche: string;
}

/** Dove mandare chi le basi le ha gia'. */
export const STUDI: QuizStudio[] = [
  {
    slug: "correlazione-asset-class",
    titolo: "La diversificazione è un'illusione?",
    perche: "Correlazioni fra 31 asset class su vent'anni, e cosa succede nelle crisi.",
  },
  {
    slug: "quanto-rende-azionario-netto-tasse-costi",
    titolo: "Quanto rende davvero l'azionario al netto di tasse e costi",
    perche: "Il conto completo su 440 finestre ventennali, non su una sola.",
  },
  {
    slug: "shiller-cape-predice-rendimenti",
    titolo: "Lo Shiller CAPE predice i rendimenti del mercato?",
    perche: "Centoquarantacinque anni di dati per una domanda su cui quasi tutti barano.",
  },
];

export function episodio(n: number): QuizEpisodio {
  const e = EPISODI.find((x) => x.n === n);
  if (!e) throw new Error(`Episodio ${n} non in registro`);
  return e;
}
