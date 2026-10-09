/**
 * QuizBasi.jsx
 *
 * Sei domande per capire se conviene partire dalla collana "Le basi" o se si
 * puo' andare dritti agli studi. Non e' un esame e non e' un gate: niente
 * email, niente registrazione, niente punteggio che scorre mentre rispondi.
 *
 * Scelte di impianto, volute:
 *  - nessun riscontro dopo la singola risposta: sei tocchi veloci e poi una
 *    schermata di risultato che mostra tutto insieme. Il valore sta li';
 *  - nessun contatore di giuste durante il quiz: scoraggia e fa abbandonare;
 *  - il risultato non e' un voto ma un percorso, e indica SOLO gli episodi
 *    delle domande sbagliate. E' la cosa che un riquadro statico non sa fare.
 *
 * Dati in src/data/quiz-basi.ts.
 *
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useMemo } from "react";
import { DOMANDE, STUDI, episodio } from "../../data/quiz-basi.ts";

const LETTERE = ["A", "B", "C", "D"];

function LinkEpisodio({ n }) {
  const e = episodio(n);
  return (
    <a
      href={`/posts/${e.slug}`}
      className="inline-flex items-baseline gap-1.5 rounded-lg border border-blue-200 bg-blue-50 px-2.5 py-1 text-sm text-blue-900 hover:bg-blue-100"
    >
      <span className="font-mono text-xs text-blue-500">#{e.n}</span>
      <span className="font-medium">{e.titolo}</span>
    </a>
  );
}

function Esito({ risposte, onRicomincia }) {
  const sbagliate = DOMANDE.filter((d, i) => risposte[i] !== d.corretta);
  const giuste = DOMANDE.length - sbagliate.length;

  // gli episodi da ripassare, in ordine, senza ripetizioni
  const daRipassare = [];
  for (const d of sbagliate) {
    for (const n of d.episodi) if (!daRipassare.includes(n)) daRipassare.push(n);
  }
  daRipassare.sort((a, b) => a - b);

  const livello = giuste >= 5 ? "alto" : giuste >= 3 ? "medio" : "base";

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {giuste} risposte giuste su {DOMANDE.length}
        </p>

        {livello === "alto" && (
          <>
            <h3 className="mt-2 text-2xl font-semibold text-slate-900">
              Le basi le hai: vai pure agli studi
            </h3>
            <p className="mt-2 text-slate-600">
              Non ti serve partire dalla collana. Gli articoli con i backtest e i
              dati sono scritti per chi sa già quello che sai tu. Tre da cui
              cominciare:
            </p>
            <ul className="mt-4 space-y-3">
              {STUDI.map((s) => (
                <li key={s.slug}>
                  <a
                    href={`/posts/${s.slug}`}
                    className="font-medium text-blue-900 underline decoration-blue-300 underline-offset-4 hover:decoration-blue-900"
                  >
                    {s.titolo}
                  </a>
                  <p className="text-sm text-slate-500">{s.perche}</p>
                </li>
              ))}
            </ul>
          </>
        )}

        {livello === "medio" && (
          <>
            <h3 className="mt-2 text-2xl font-semibold text-slate-900">
              Hai le basi, ti manca qualche tassello
            </h3>
            <p className="mt-2 text-slate-600">
              Non serve leggere tutta la collana. Questi sono gli unici episodi
              che coprono le cose su cui hai sbagliato, poi sei a posto per gli
              studi.
            </p>
          </>
        )}

        {livello === "base" && (
          <>
            <h3 className="mt-2 text-2xl font-semibold text-slate-900">
              Conviene partire dall'inizio
            </h3>
            <p className="mt-2 text-slate-600">
              Niente di grave: è esattamente il motivo per cui la collana esiste.
              Sono tredici letture brevi in ordine, e dopo il resto del sito si
              legge senza prendere niente per buono.
            </p>
            <p className="mt-4">
              <a
                href="/serie/le-basi"
                className="inline-block rounded-xl bg-blue-900 px-4 py-2.5 font-semibold text-white hover:bg-blue-800"
              >
                Vai al percorso completo
              </a>
            </p>
          </>
        )}

        {livello !== "base" && daRipassare.length > 0 && (
          <div className="mt-5 border-t border-slate-100 pt-4">
            <p className="text-sm font-semibold text-slate-700">
              {livello === "alto" ? "Se vuoi colmare il buco:" : "Da leggere:"}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {daRipassare.map((n) => (
                <LinkEpisodio key={n} n={n} />
              ))}
            </div>
          </div>
        )}

        {daRipassare.length === 0 && (
          <p className="mt-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">
            Sei su sei. Non hai niente da ripassare.
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Le risposte, una per una
        </h3>
        <ol className="mt-4 space-y-5">
          {DOMANDE.map((d, i) => {
            const giusta = risposte[i] === d.corretta;
            return (
              <li key={d.id} className="border-t border-slate-100 pt-4 first:border-0 first:pt-0">
                <p className="font-medium text-slate-900">
                  <span className="mr-2 text-slate-400">{i + 1}.</span>
                  {d.testo}
                </p>
                <p className={`mt-2 text-sm ${giusta ? "text-emerald-700" : "text-rose-700"}`}>
                  {giusta ? "Giusto: " : "Hai risposto: "}
                  {d.opzioni[risposte[i]]}
                </p>
                {!giusta && (
                  <p className="mt-1 text-sm text-emerald-700">
                    Risposta corretta: {d.opzioni[d.corretta]}
                  </p>
                )}
                <p className="mt-2 text-sm text-slate-600">{d.spiegazione}</p>
                {/* i link all'episodio solo dove serve: su una risposta giusta
                    sarebbero rumore, e contraddirebbero la promessa di
                    indicare soltanto quello che manca */}
                {!giusta && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {d.episodi.map((n) => (
                      <LinkEpisodio key={n} n={n} />
                    ))}
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </div>

      <button
        type="button"
        onClick={onRicomincia}
        className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
      >
        Rifai il quiz
      </button>
    </div>
  );
}

export default function QuizBasi() {
  const [risposte, setRisposte] = useState([]);
  const indice = risposte.length;
  const finito = indice >= DOMANDE.length;
  const domanda = useMemo(() => (finito ? null : DOMANDE[indice]), [finito, indice]);

  function rispondi(i) {
    setRisposte((r) => [...r, i]);
  }

  function indietro() {
    setRisposte((r) => r.slice(0, -1));
  }

  if (finito) {
    return (
      <div className="not-prose my-8">
        <Esito risposte={risposte} onRicomincia={() => setRisposte([])} />
      </div>
    );
  }

  return (
    <div className="not-prose my-8">
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <div className="flex items-baseline justify-between">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Domanda {indice + 1} di {DOMANDE.length}
          </p>
          {indice > 0 && (
            <button
              type="button"
              onClick={indietro}
              className="text-xs text-slate-400 underline underline-offset-2 hover:text-slate-600"
            >
              torna indietro
            </button>
          )}
        </div>

        {/* barra di avanzamento: posizione, non punteggio */}
        <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-blue-900 transition-all duration-300"
            style={{ width: `${(indice / DOMANDE.length) * 100}%` }}
          />
        </div>

        <h3 className="mt-5 text-xl font-medium leading-snug text-slate-900">
          {domanda.testo}
        </h3>

        <div className="mt-5 space-y-2.5">
          {domanda.opzioni.map((o, i) => (
            <button
              key={i}
              type="button"
              onClick={() => rispondi(i)}
              className="flex w-full items-baseline gap-3 rounded-xl border border-slate-200 px-4 py-3 text-left text-slate-700 transition-colors hover:border-blue-300 hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              <span className="font-mono text-xs text-slate-400">{LETTERE[i]}</span>
              <span>{o}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
