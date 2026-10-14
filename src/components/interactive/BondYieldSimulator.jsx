/**
 * BondYieldSimulator.jsx
 *
 * Simulatore statico: l'utente sceglie il tipo di titoli in cui investe il suo
 * ETF obbligazionario, inserisce il rendimento a scadenza del portafoglio e un
 * orizzonte, e lo strumento mostra cosa e' successo storicamente partendo da
 * quel livello di rendimento.
 *
 * Il punto NON e' la stima centrale, che e' quasi sempre il rendimento stesso
 * (la pendenza della retta e' vicina a uno). Il punto e' QUANTO quella stima ha
 * tenuto all'orizzonte scelto: sui Treasury 7-10 il risultato a dieci anni e'
 * finito entro due punti dal rendimento iniziale nell'86% dei casi, sui
 * Treasury 20+ nel 49%, e solo allungando a vent'anni si risale all'83%. La
 * soglia sta intorno al doppio della duration. La curva di affidabilita' e' il
 * grafico centrale dello strumento per questo motivo.
 *
 * Gli ETF non governativi (corporate, aggregate, emergenti, high yield) NON
 * sono coperti: il loro rendimento a scadenza incorpora perdite attese per
 * default e la relazione non vale. In quel caso lo strumento si rifiuta di
 * rispondere invece di dare un numero sbagliato.
 *
 * Dati: fetch /tools/etf-obbligazionari-rendimenti.json
 * (generato da scripts/simulatore-etf-obbligazionari.py).
 *
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useEffect, useMemo } from "react";

const DATA_URL = "/tools/etf-obbligazionari-rendimenti.json";

const num = (x, d = 1) =>
  x === null || x === undefined || Number.isNaN(x)
    ? "—"
    : x.toFixed(d).replace(".", ",");

const pct = (x, d = 1) => {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  const segno = x >= 0 ? "+" : "−";
  return `${segno}${Math.abs(x).toFixed(d).replace(".", ",")}%`;
};

// Giudizio sull'affidabilita' all'orizzonte scelto. Le soglie non sono
// cosmetiche: sotto il 60% di casi entro due punti, il rendimento di partenza
// semplicemente non racconta cosa otterrai.
function giudizio(entro2) {
  if (entro2 >= 80) return { tono: "ok", testo: "Il prezzo di oggi dice quasi tutto" };
  if (entro2 >= 65) return { tono: "medio", testo: "Il prezzo di oggi dice parecchio" };
  if (entro2 >= 50) return { tono: "medio", testo: "Il prezzo di oggi dice qualcosa" };
  return { tono: "no", testo: "A questo orizzonte il prezzo di oggi dice poco" };
}

const TONI = {
  ok: "border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-100",
  medio: "border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100",
  no: "border-red-300 bg-red-50 text-red-900 dark:border-red-800 dark:bg-red-950/40 dark:text-red-100",
};

export default function BondYieldSimulator() {
  const [dati, setDati] = useState(null);
  const [errore, setErrore] = useState(null);
  const [gambaId, setGambaId] = useState(null);
  const [rend, setRend] = useState(5);
  const [anni, setAnni] = useState(10);
  const [ter, setTer] = useState(0.15);

  useEffect(() => {
    fetch(DATA_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject("Dati non caricati")))
      .then((j) => {
        setDati(j);
        const g = j.gambe[0];
        setGambaId(g.id);
        setRend(g.rendimento.valore);
        setTer(g.etf[0]?.ter ?? 0.15);
      })
      .catch((e) => setErrore(String(e)));
  }, []);

  const gamba = useMemo(
    () => (dati && gambaId !== "altro" ? dati.gambe.find((g) => g.id === gambaId) : null),
    [dati, gambaId]
  );

  // Cambio gamba: si riparte dal suo rendimento di riferimento e dal TER del
  // primo ETF di esempio, altrimenti restano i numeri della gamba precedente.
  function scegli(id) {
    setGambaId(id);
    const g = dati?.gambe.find((x) => x.id === id);
    if (g) {
      setRend(g.rendimento.valore);
      setTer(g.etf[0]?.ter ?? 0.15);
    }
  }

  const o = useMemo(
    () => gamba?.orizzonti.find((x) => x.anni === anni) ?? null,
    [gamba, anni]
  );

  const stima = useMemo(() => {
    if (!gamba || !o) return null;
    const lordo = o.intercetta + o.pendenza * rend;
    return {
      centro: lordo - ter,
      basso: lordo + o.residui.p10 - ter,
      alto: lordo + o.residui.p90 - ter,
      lordo,
    };
  }, [gamba, o, rend, ter]);

  const fuoriCampo =
    gamba && (rend < gamba.campo_x.min || rend > gamba.campo_x.max);

  if (errore) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
        <strong>Dati non disponibili:</strong> {errore}
      </div>
    );
  }
  if (!dati) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        Caricamento dei dati storici…
      </div>
    );
  }

  const g = giudizio(o?.entro2 ?? 0);

  return (
    <div className="not-prose my-8 space-y-6">
      {/* 1. CHE COSA HAI IN PORTAFOGLIO */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h3 className="mb-1 text-base font-bold text-slate-900 dark:text-slate-100">
          1. In che titoli investe il tuo ETF?
        </h3>
        <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
          Lo trovi nel nome del fondo o nella sua scheda, alla voce indice replicato.
        </p>
        <div className="grid gap-2 sm:grid-cols-2">
          {dati.gambe.map((x) => (
            <button
              key={x.id}
              onClick={() => scegli(x.id)}
              className={`rounded-xl border px-4 py-3 text-left text-sm transition ${
                gambaId === x.id
                  ? "border-blue-700 bg-blue-50 font-semibold text-blue-900 dark:border-blue-400 dark:bg-blue-950 dark:text-blue-100"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
              }`}
            >
              <div>{x.nome}</div>
              <div className="mt-0.5 text-xs font-normal text-slate-500 dark:text-slate-400">
                es. {x.etf.map((e) => e.ticker).join(", ")} · duration {num(x.duration)} anni
              </div>
            </button>
          ))}
          <button
            onClick={() => setGambaId("altro")}
            className={`rounded-xl border px-4 py-3 text-left text-sm transition sm:col-span-2 ${
              gambaId === "altro"
                ? "border-amber-600 bg-amber-50 font-semibold text-amber-900 dark:border-amber-500 dark:bg-amber-950 dark:text-amber-100"
                : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
            }`}
          >
            <div>Corporate, aggregate, emergenti o high yield</div>
            <div className="mt-0.5 text-xs font-normal text-slate-500 dark:text-slate-400">
              tutto quello che non è solo titoli di Stato
            </div>
          </button>
        </div>
      </div>

      {gambaId === "altro" && (
        <div className="rounded-2xl border-2 border-amber-400 bg-amber-50 p-5 text-sm text-amber-900 dark:border-amber-600 dark:bg-amber-950/40 dark:text-amber-100">
          <strong className="block text-base">Qui lo strumento si ferma.</strong>
          <p className="mt-2">
            Lo studio dietro questo simulatore ricostruisce solo indici di titoli di Stato. Su un
            ETF corporate, aggregate, emergenti o high yield il rendimento a scadenza che leggi
            nella scheda incorpora anche le <strong>perdite attese per default e downgrade</strong>:
            una parte di quel rendimento non arriverà mai a destinazione, e quanta non lo sappiamo
            dai nostri dati. Darti un numero qui sarebbe inventarlo.
          </p>
          <p className="mt-2">
            La direzione resta valida (più alto il rendimento di partenza, più alto il risultato
            atteso), la precisione no.
          </p>
        </div>
      )}

      {gamba && (
        <>
          {/* 2. RENDIMENTO A SCADENZA */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <h3 className="mb-1 text-base font-bold text-slate-900 dark:text-slate-100">
              2. Qual è il rendimento a scadenza del tuo ETF?
            </h3>
            <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
              Nella scheda del fondo si chiama <em>rendimento a scadenza</em> o{" "}
              <em>yield to maturity</em>. È il rendimento lordo del portafoglio di titoli, non la
              cedola distribuita.
            </p>

            <div className="flex flex-wrap items-end gap-4">
              <label className="text-sm text-slate-700 dark:text-slate-300">
                <span className="mb-1 block font-medium">Rendimento a scadenza</span>
                <span className="inline-flex items-center gap-1">
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="20"
                    value={rend}
                    onChange={(e) => setRend(Number(e.target.value))}
                    className="w-28 rounded-lg border border-slate-300 px-3 py-2 text-right font-bold text-blue-800 dark:border-slate-600 dark:bg-slate-800 dark:text-blue-300"
                  />
                  <span className="font-bold text-blue-800 dark:text-blue-300">%</span>
                </span>
              </label>

              <label className="text-sm text-slate-700 dark:text-slate-300">
                <span className="mb-1 block font-medium">Costo annuo dell'ETF (TER)</span>
                <span className="inline-flex items-center gap-1">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="2"
                    value={ter}
                    onChange={(e) => setTer(Number(e.target.value))}
                    className="w-24 rounded-lg border border-slate-300 px-3 py-2 text-right dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
                  />
                  <span>%</span>
                </span>
              </label>

              <button
                onClick={() => setRend(gamba.rendimento.valore)}
                className="rounded-full border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                riferimento di oggi: {num(gamba.rendimento.valore, 2)}%
              </button>
            </div>

            <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
              Il riferimento è il rendimento del mercato al {gamba.rendimento.data}, da{" "}
              <a
                href={gamba.rendimento.link}
                target="_blank"
                rel="noopener"
                className="text-blue-700 underline dark:text-blue-400"
              >
                {gamba.rendimento.fonte}
              </a>
              . Quello del tuo ETF può differire di qualche decimo: se ce l'hai, usa il suo.
            </p>

            {fuoriCampo && (
              <p className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100">
                Storicamente questa gamba non è mai stata a {num(rend, 2)}%: il campo osservato va
                dal {num(gamba.campo_x.min, 2)}% al {num(gamba.campo_x.max, 2)}%. Fuori da lì la
                retta estrapola e la stima vale molto meno.
              </p>
            )}
          </div>

          {/* 3. ORIZZONTE */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>3. Per quanti anni lo tieni?</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{anni} anni</span>
            </label>
            <input
              type="range"
              min={dati.orizzonti[0]}
              max={dati.orizzonti[dati.orizzonti.length - 1]}
              step="1"
              value={anni}
              onChange={(e) => setAnni(Number(e.target.value))}
              className="mt-2 w-full accent-blue-700"
            />
            <div className="mt-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>5 anni</span>
              <span>duration della gamba: {num(gamba.duration)} anni</span>
              <span>20 anni</span>
            </div>
          </div>

          {/* RISULTATO */}
          {stima && o && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                Comprando oggi al {num(rend, 2)}% e tenendo {anni} anni
              </h3>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Su {o.n} finestre storiche ({o.da} → {o.a}), al netto di un TER del {num(ter, 2)}%.
              </p>

              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl bg-blue-50 p-4 text-center dark:bg-blue-950/50">
                  <div className="text-xs uppercase tracking-wide text-blue-900/70 dark:text-blue-200/70">
                    stima centrale
                  </div>
                  <div className="mt-1 text-3xl font-bold text-blue-900 dark:text-blue-200">
                    {pct(stima.centro)}
                  </div>
                  <div className="text-xs text-blue-900/70 dark:text-blue-200/70">all'anno</div>
                </div>
                <div className="rounded-xl bg-slate-50 p-4 text-center dark:bg-slate-800 sm:col-span-2">
                  <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    fascia storica (8 casi su 10 sono finiti qui dentro)
                  </div>
                  <div className="mt-1 text-2xl font-bold text-slate-900 dark:text-slate-100">
                    da {pct(stima.basso)} a {pct(stima.alto)}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    all'anno, per {anni} anni
                  </div>
                </div>
              </div>

              <div className={`mt-5 rounded-xl border p-4 text-sm ${TONI[g.tono]}`}>
                <strong className="block text-base">{g.testo}</strong>
                <p className="mt-1">
                  A {anni} anni, su questa gamba, il risultato è finito entro due punti dal
                  rendimento di partenza nel <strong>{num(o.entro2)}%</strong> dei casi storici
                  (entro un punto nel {num(o.entro1)}%).{" "}
                  {gamba.orizzonte_sufficiente && anni < gamba.orizzonte_sufficiente ? (
                    <>
                      Per questa duration ({num(gamba.duration)} anni) servono almeno{" "}
                      <button
                        onClick={() => setAnni(gamba.orizzonte_sufficiente)}
                        className="underline underline-offset-2"
                      >
                        {gamba.orizzonte_sufficiente} anni
                      </button>{" "}
                      perché il rendimento iniziale diventi una guida affidabile.
                    </>
                  ) : (
                    <>Il massimo storico per questa gamba è a {gamba.orizzonte_migliore} anni.</>
                  )}
                </p>
              </div>

              <CurvaAffidabilita orizzonti={gamba.orizzonti} scelto={anni} onPick={setAnni} />

              <p className="mt-4 text-xs text-slate-500 dark:text-slate-400">
                Rendimenti in {gamba.valuta}, lordi di imposte. Le finestre si sovrappongono:
                descrivono il passato, non sono probabilità.
                {gamba.id === "italia-15" && (
                  <>
                    {" "}
                    Su questa gamba i dati prima del novembre 1993 simulano uno strumento che in
                    Italia non esisteva: i numeri a quindici e vent'anni pescano quasi tutti da lì.
                  </>
                )}
              </p>
            </div>
          )}
        </>
      )}

      {/* FONTE */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Da dove vengono questi numeri.</strong> Indici a duration costante ricostruiti dai
        rendimenti dei titoli di Stato, validati contro gli ETF reali. Metodologia completa nello
        studio{" "}
        <a
          href={dati.articolo}
          className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400"
        >
          Quanto rendono gli ETF obbligazionari
        </a>
        . Dati aggiornati al {dati.generato}. Questo non è un consiglio di investimento.
      </div>
    </div>
  );
}

/** Quota di casi storici finiti entro due punti dal rendimento di partenza,
 *  orizzonte per orizzonte. E' il grafico che spiega lo strumento: la barra
 *  cresce con gli anni, e dove si alza il prezzo di oggi comincia a contare. */
function CurvaAffidabilita({ orizzonti, scelto, onPick }) {
  // Proporzioni pensate per il telefono: su uno schermo da 390px un grafico
  // 560x150 diventa alto 94px con etichette illeggibili. Piu' stretto e piu'
  // alto scala meglio, e sul desktop non perde nulla.
  const W = 430;
  const H = 195;
  const padL = 40;
  const padB = 30;
  const padT = 12;
  const n = orizzonti.length;
  const larg = (W - padL - 8) / n;
  const y = (v) => padT + (H - padT - padB) * (1 - v / 100);

  return (
    <div className="mt-6">
      <div className="mb-1 text-sm font-semibold text-slate-800 dark:text-slate-200">
        Quanto è affidabile, orizzonte per orizzonte
      </div>
      <div className="mb-2 text-xs text-slate-500 dark:text-slate-400">
        quota di casi storici finiti entro due punti dal rendimento di partenza
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label="Quota di casi entro due punti dal rendimento iniziale, per orizzonte di detenzione"
      >
        {[0, 50, 80, 100].map((v) => (
          <g key={v}>
            <line
              x1={padL}
              x2={W - 4}
              y1={y(v)}
              y2={y(v)}
              stroke="currentColor"
              className={v === 80 ? "text-emerald-400" : "text-slate-300 dark:text-slate-600"}
              strokeWidth="1"
              strokeDasharray={v === 80 ? "4 4" : "2 5"}
            />
            <text
              x={padL - 6}
              y={y(v) + 4}
              textAnchor="end"
              fontSize="12"
              fill="currentColor"
              className="text-slate-500 dark:text-slate-400"
            >
              {v}%
            </text>
          </g>
        ))}
        {orizzonti.map((o, i) => {
          const attivo = o.anni === scelto;
          return (
            <g key={o.anni} onClick={() => onPick(o.anni)} style={{ cursor: "pointer" }}>
              <rect
                x={padL + i * larg + 2}
                y={y(o.entro2)}
                width={larg - 4}
                height={H - padB - y(o.entro2)}
                rx="2"
                fill="currentColor"
                className={
                  attivo
                    ? "text-blue-700 dark:text-blue-400"
                    : "text-slate-300 dark:text-slate-600"
                }
              />
              {(o.anni % 5 === 0 || attivo) && (
                <text
                  x={padL + i * larg + larg / 2}
                  y={H - 9}
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight={attivo ? "700" : "400"}
                  fill="currentColor"
                  className={
                    attivo ? "text-blue-700 dark:text-blue-300" : "text-slate-500 dark:text-slate-400"
                  }
                >
                  {o.anni}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <div className="text-center text-xs text-slate-500 dark:text-slate-400">
        anni di detenzione (clicca una barra)
      </div>
    </div>
  );
}
