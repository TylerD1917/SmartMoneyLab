/**
 * CapePredictor.jsx
 *
 * Strumento predittivo: dato il CAPE attuale di 6 mercati (World, Europa, Emergenti,
 * Cina, India, Giappone), stima il rendimento annualizzato atteso a 5 e 10 anni usando
 * la relazione storica di ciascun mercato (regressione forward ~ CAPE dal 2001).
 *
 * Il CAPE corrente e' "cablato" nel lookup (aggiornato periodicamente da snapshot RA):
 * l'utente non deve cercarlo. La data di rilevazione e' mostrata in evidenza.
 * Uno slider permette comunque di esplorare altri livelli di CAPE.
 *
 * Framing (coerente con l'articolo): descrittivo, NON market timing. Il segnale e'
 * debole/rumoroso su alcuni mercati (affidabilita' segnalata via R²).
 *
 * Dati: /tools/cape-predictor-lookup.json (generato da scripts/build_cape_predictor.py).
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useEffect, useMemo } from "react";

const LOOKUP_URL = "/tools/cape-predictor-lookup.json";
const ORDER = ["Developed Markets Large", "Europe", "Emerging Markets", "China", "India", "Japan"];
const MESI = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
  "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"];

function asOfLabel(s) {
  if (!s) return "—";
  const [y, m] = s.split("-");
  return `${MESI[parseInt(m, 10)]} ${y}`;
}
function fmtPct(x, d = 1) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  const s = x >= 0 ? "+" : "";
  return `${s}${(x * 100).toFixed(d)}%`;
}
function predict(h, cape) {
  const p = h.intercept + h.slope * cape;
  return { mid: p, lo: p - h.rmse, hi: p + h.rmse };
}
function reliability(r2) {
  if (r2 >= 0.4) return { label: "alta", cls: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-100" };
  if (r2 >= 0.2) return { label: "media", cls: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100" };
  return { label: "bassa", cls: "bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-100" };
}
function valTag(ratio) {
  if (ratio <= 0.85) return { label: "economico vs la sua storia", cls: "text-emerald-700 dark:text-emerald-400" };
  if (ratio < 1.15) return { label: "in linea con la sua storia", cls: "text-slate-600 dark:text-slate-300" };
  return { label: "caro vs la sua storia", cls: "text-rose-700 dark:text-rose-400" };
}

export default function CapePredictor() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lookup, setLookup] = useState(null);
  const [sel, setSel] = useState("Developed Markets Large");
  const [override, setOverride] = useState(null); // CAPE esplorativo; null = usa cape_now

  useEffect(() => {
    fetch(LOOKUP_URL)
      .then(r => r.ok ? r.json() : Promise.reject("Lookup non caricato"))
      .then(j => { setLookup(j); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const m = lookup?.markets?.[sel];
  const capeUsed = override ?? m?.cape_now;

  useEffect(() => { setOverride(null); }, [sel]); // reset slider al cambio mercato

  if (loading) return <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">Caricamento dei dati…</div>;
  if (error) return <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"><strong>Errore:</strong> {error}</div>;

  const asOf = asOfLabel(lookup.meta.as_of);
  const rel = reliability(m.h10.r2);
  const vt = valTag(capeUsed / m.hist_median);
  const p5 = predict(m.h5, capeUsed);
  const p10 = predict(m.h10, capeUsed);
  const clip = x => Math.max(-0.10, Math.min(0.25, x));

  const ranked = ORDER
    .map(k => ({ k, mm: lookup.markets[k], ratio: lookup.markets[k].cape_now / lookup.markets[k].hist_median }))
    .sort((a, b) => a.ratio - b.ratio);
  const under = ranked.slice(0, 3);
  const over = ranked.slice(-3).reverse();

  return (
    <div className="not-prose my-8 space-y-6">

      {/* AS-OF + FRAMING */}
      <div className="rounded-2xl border-2 border-amber-400 bg-amber-50 p-5 dark:border-amber-600 dark:bg-amber-950/40">
        <div className="flex items-start gap-3">
          <div className="text-2xl leading-none">⚠</div>
          <div>
            <h3 className="mb-1 text-base font-bold text-amber-900 dark:text-amber-200">Come leggere queste stime</h3>
            <p className="text-sm text-amber-900 dark:text-amber-100">
              Sono <em>proiezioni statistiche</em> basate sulla relazione storica tra il CAPE di ciascun
              mercato e il suo rendimento nei 5-10 anni successivi (dal 2001). Non sono previsioni certe né
              market timing: indicano l'<em>ordine di grandezza</em> atteso e vanno lette con la loro banda di
              incertezza e con l'<strong>affidabilità</strong> del segnale (l'R² storico del mercato). Su alcuni
              mercati il CAPE ha predetto poco: lì l'affidabilità è bassa.
            </p>
          </div>
        </div>
      </div>

      {/* CLASSIFICA VALUTAZIONE OGGI */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-3 flex items-baseline justify-between flex-wrap gap-2">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Valutazione oggi rispetto alla propria storia</h3>
          <span className="text-xs text-slate-500 dark:text-slate-400">tra i sei mercati · {asOf}</span>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-950/40">
            <div className="mb-2 text-sm font-semibold text-emerald-800 dark:text-emerald-200">I 3 più sottovalutati</div>
            <ul className="space-y-1">
              {under.map(({ k, mm, ratio }) => (
                <li key={k} className="flex justify-between text-sm">
                  <span className="text-slate-800 dark:text-slate-200">{mm.label}</span>
                  <span className="font-semibold tabular-nums text-emerald-700 dark:text-emerald-400">{ratio.toFixed(2)}×</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 dark:border-rose-800 dark:bg-rose-950/40">
            <div className="mb-2 text-sm font-semibold text-rose-800 dark:text-rose-200">I 3 più sopravvalutati</div>
            <ul className="space-y-1">
              {over.map(({ k, mm, ratio }) => (
                <li key={k} className="flex justify-between text-sm">
                  <span className="text-slate-800 dark:text-slate-200">{mm.label}</span>
                  <span className="font-semibold tabular-nums text-rose-700 dark:text-rose-400">{ratio.toFixed(2)}×</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
          Rapporto tra il CAPE attuale e la mediana storica del mercato: sotto 1 = più economico del suo tipico, sopra 1 = più caro. Il segnale conta <em>dentro</em> un mercato, non per confrontare mercati diversi.
        </p>
      </div>

      {/* TABELLA RIEPILOGO 6 MERCATI */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-1 flex items-baseline justify-between flex-wrap gap-2">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Rendimento atteso per mercato</h3>
          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-900 dark:bg-blue-900 dark:text-blue-100">
            CAPE rilevati a {asOf}
          </span>
        </div>
        <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
          Stima centrale del rendimento annualizzato (USD, lordo) al livello di CAPE attuale di ciascun mercato.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
                <th className="py-2 pr-3">Mercato</th>
                <th className="py-2 pr-3 text-right">CAPE oggi</th>
                <th className="py-2 pr-3 text-right">vs sua mediana</th>
                <th className="py-2 pr-3 text-right">Attesa 5 anni</th>
                <th className="py-2 pr-3 text-right">Attesa 10 anni</th>
                <th className="py-2 pl-3 text-right">Affidabilità</th>
              </tr>
            </thead>
            <tbody>
              {ORDER.map(k => {
                const mm = lookup.markets[k]; if (!mm) return null;
                const r = reliability(mm.h10.r2);
                const rr = mm.cape_now / mm.hist_median;
                const a5 = mm.h5.intercept + mm.h5.slope * mm.cape_now;
                const a10 = mm.h10.intercept + mm.h10.slope * mm.cape_now;
                return (
                  <tr key={k} onClick={() => setSel(k)}
                    className={`cursor-pointer border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 ${sel === k ? "bg-blue-50 dark:bg-blue-950" : ""}`}>
                    <td className="py-2 pr-3 font-medium text-slate-800 dark:text-slate-200">{mm.label}</td>
                    <td className="py-2 pr-3 text-right tabular-nums">{mm.cape_now.toFixed(1)}</td>
                    <td className="py-2 pr-3 text-right tabular-nums">{rr.toFixed(2)}×</td>
                    <td className="py-2 pr-3 text-right tabular-nums font-semibold">{fmtPct(a5)}</td>
                    <td className="py-2 pr-3 text-right tabular-nums font-semibold">{fmtPct(a10)}</td>
                    <td className="py-2 pl-3 text-right"><span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${r.cls}`}>{r.label}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">Clicca una riga per il dettaglio e per esplorare altri livelli di CAPE.</p>
      </div>

      {/* DETTAGLIO MERCATO SELEZIONATO */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-3 flex items-baseline justify-between flex-wrap gap-2">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{m.label}</h3>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${rel.cls}`}>affidabilità {rel.label} · R² {m.h10.r2.toFixed(2)}</span>
        </div>

        <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-950">
          CAPE {override !== null ? "impostato" : `a ${asOf}`}: <strong className="tabular-nums">{capeUsed.toFixed(1)}</strong>
          {" "}(mediana storica {m.hist_median.toFixed(1)}) — <span className={vt.cls}>{vt.label}</span>.
        </div>

        {/* PREVISIONI */}
        <div className="grid gap-4 sm:grid-cols-2">
          {[["5 anni", p5], ["10 anni", p10]].map(([lab, p]) => (
            <div key={lab} className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
              <div className="text-xs uppercase text-slate-500 dark:text-slate-400">Rendimento annualizzato atteso · {lab}</div>
              <div className="mt-1 text-3xl font-bold text-blue-700 dark:text-blue-400 tabular-nums">{fmtPct(clip(p.mid))}</div>
              <div className="mt-1 text-sm text-slate-500 dark:text-slate-400 tabular-nums">banda {fmtPct(clip(p.lo))} → {fmtPct(clip(p.hi))}</div>
            </div>
          ))}
        </div>

        {m.h10.r2 < 0.2 && (
          <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-200">
            Su questo mercato il CAPE ha storicamente predetto molto poco (R² {m.h10.r2.toFixed(2)}): la stima
            centrale è poco informativa, conta soprattutto la banda. Prendila come contesto, non come previsione.
          </div>
        )}

        {/* SLIDER ESPLORATIVO */}
        <div className="mt-5">
          <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
            <span>Esplora un altro livello di CAPE</span>
            <span className="font-bold text-blue-700 dark:text-blue-400 tabular-nums">{capeUsed.toFixed(0)}</span>
          </label>
          <input type="range" min={m.slider_min} max={m.slider_max} step="1"
            value={Math.round(capeUsed)}
            onChange={e => setOverride(Number(e.target.value))}
            className="mt-1 w-full accent-blue-700" />
          <div className="mt-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>{m.slider_min}</span>
            <span>mediana {m.hist_median.toFixed(0)}</span>
            <span>{m.slider_max}</span>
          </div>
          {override !== null && (
            <button onClick={() => setOverride(null)}
              className="mt-2 rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800">
              Torna al CAPE attuale ({m.cape_now.toFixed(1)})
            </button>
          )}
        </div>
      </div>

      {/* FONTE */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Metodo.</strong> Regressione lineare del rendimento MSCI Gross TR (USD) forward a 5 e 10 anni
        sul CAPE del mercato, dal 2001. Banda = ±1 errore standard della regressione. CAPE da{" "}
        <a href="https://interactive.researchaffiliates.com/asset-allocation" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400">Research Affiliates</a>,
        rilevati a {asOf}. Finestre sovrapposte, stime indicative. Metodologia e limiti completi:{" "}
        <a href="/posts/cape-internazionale-predice-rendimenti" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400">articolo di riferimento</a>.
      </div>
    </div>
  );
}
