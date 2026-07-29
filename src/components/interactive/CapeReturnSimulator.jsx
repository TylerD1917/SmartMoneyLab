/**
 * CapeReturnSimulator.jsx
 *
 * Simulatore statico: l'utente imposta un livello di Shiller CAPE, il tool
 * classifica la fascia e mostra i range storici dei rendimenti annualizzati
 * a 5, 10 e 20 anni (reale e nominale) registrati storicamente in quella
 * fascia sui 145 anni di dati (1881-2026).
 *
 * Framing (coerente con l'articolo): descrittivo, NON market timing. Il CAPE
 * predice l'ordine di grandezza dei rendimenti su orizzonti lunghi, non il
 * momento del calo.
 *
 * Dati: fetch /tools/cape-lookup.json (generato dallo script backtest).
 *
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useEffect, useMemo } from "react";

const LOOKUP_URL = "/tools/cape-lookup.json";

// Soglie coerenti col backtest (LEVEL_BINS)
const BUCKETS = [
  { key: "lt15",  label: "<15 (economico)",    min: -Infinity, max: 15 },
  { key: "15_20", label: "15-20 (equo-basso)", min: 15,        max: 20 },
  { key: "20_25", label: "20-25 (equo-alto)",  min: 20,        max: 25 },
  { key: "25_30", label: "25-30 (caro)",       min: 25,        max: 30 },
  { key: "30_40", label: "30-40 (molto caro)", min: 30,        max: 40 },
  { key: "gt40",  label: ">40 (carissimo)",    min: 40,        max: Infinity },
];

function classify(cape) {
  for (const b of BUCKETS) {
    if (cape >= b.min && cape < b.max) return b;
  }
  return null;
}

function fmtPct(x, digits = 1) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  const sign = x >= 0 ? "+" : "";
  return `${sign}${(x * 100).toFixed(digits)}%`;
}

export default function CapeReturnSimulator() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lookup, setLookup] = useState(null);
  const [cape, setCape] = useState(40);

  useEffect(() => {
    fetch(LOOKUP_URL)
      .then(r => r.ok ? r.json() : Promise.reject("Lookup non caricato"))
      .then(j => {
        setLookup(j);
        // Default: CAPE attuale dal lookup, arrotondato
        if (j?.meta?.cape_current) setCape(Math.round(j.meta.cape_current));
        setLoading(false);
      })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const bucket = useMemo(() => classify(cape), [cape]);
  const data = useMemo(() => {
    if (!lookup || !bucket) return null;
    return lookup.buckets[bucket.key];
  }, [lookup, bucket]);

  if (loading) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        Caricamento dei dati storici…
      </div>
    );
  }
  if (error) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
        <strong>Errore caricamento lookup:</strong> {error}
      </div>
    );
  }

  const corr10 = lookup?.meta?.correlations?.cape_vs_fwd10y_real;
  const capeCurrent = lookup?.meta?.cape_current;

  return (
    <div className="not-prose my-8 space-y-6">

      {/* FRAMING */}
      <div className="rounded-2xl border-2 border-amber-400 bg-amber-50 p-5 dark:border-amber-600 dark:bg-amber-950/40">
        <div className="flex items-start gap-3">
          <div className="text-2xl leading-none">⚠</div>
          <div>
            <h3 className="mb-1 text-base font-bold text-amber-900 dark:text-amber-200">
              Il CAPE non è market timing
            </h3>
            <p className="text-sm text-amber-900 dark:text-amber-100">
              I range sotto descrivono cosa è successo <em>storicamente</em> nei periodi con
              un CAPE simile a quello che imposti. Il CAPE predice l'ordine di grandezza dei
              rendimenti su orizzonti lunghi (correlazione {corr10 !== undefined ? corr10.toFixed(2) : "—"} col reale
              a 10 anni), non <em>quando</em> arriva un eventuale calo. Serve a calibrare le
              aspettative, non a decidere quando entrare o uscire dal mercato.
            </p>
          </div>
        </div>
      </div>

      {/* INPUT */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
          <span>Livello di Shiller CAPE</span>
          <span className="font-bold text-blue-700 dark:text-blue-400">{cape}</span>
        </label>
        <input type="range" min="5" max="45" step="1"
                value={cape}
                onChange={e => setCape(Number(e.target.value))}
                className="mt-1 w-full accent-blue-700" />
        <div className="mt-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>5 (minimo storico 1920)</span>
          <span>media storica {lookup?.meta?.cape_mean ? lookup.meta.cape_mean.toFixed(1) : "17.7"}</span>
          <span>45 (massimo storico)</span>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-900 dark:bg-blue-900 dark:text-blue-100">
            Fascia: {bucket?.label}
          </span>
          {capeCurrent && (
            <button
              onClick={() => setCape(Math.round(capeCurrent))}
              className="rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800">
              CAPE oggi ≈ {capeCurrent.toFixed(0)} (reimposta)
            </button>
          )}
        </div>
      </div>

      {/* RISULTATI */}
      {data && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <div className="mb-1 flex items-baseline justify-between flex-wrap gap-2">
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
              Rendimenti storici in fascia "{data.label}"
            </h3>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {data.n} mesi storici (CAPE {data.cape_min?.toFixed(1)}-{data.cape_max?.toFixed(1)})
            </span>
          </div>
          <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
            Rendimento annualizzato mediano (e range dal 5° al 95° percentile) registrato nei periodi
            storici con CAPE in questa fascia. Mediana e percentili su finestre mobili sovrapposte.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
                  <th className="py-2 pr-3">Orizzonte</th>
                  <th className="py-2 pr-3 text-right">Reale (mediana)</th>
                  <th className="py-2 pr-3 text-right">Reale (range p5-p95)</th>
                  <th className="py-2 pl-3 text-right">Nominale (mediana)</th>
                </tr>
              </thead>
              <tbody>
                <RowH label="5 anni"  med={data.fwd5y_real_median}  p5={data.fwd5y_real_p5}  p95={data.fwd5y_real_p95}  nom={data.fwd5y_nom_median} />
                <RowH label="10 anni" med={data.fwd10y_real_median} p5={data.fwd10y_real_p5} p95={data.fwd10y_real_p95} nom={data.fwd10y_nom_median} highlight />
                <RowH label="20 anni" med={data.fwd20y_real_median} p5={data.fwd20y_real_p5} p95={data.fwd20y_real_p95} nom={data.fwd20y_nom_median} />
              </tbody>
            </table>
          </div>

          {data.fwd10y_real_hit_pos !== undefined && (
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
              In questa fascia, storicamente, il <strong>{fmtPct(1 - data.fwd10y_real_hit_pos, 0)}</strong> dei
              periodi a 10 anni ha avuto un rendimento reale <strong>negativo</strong>. A 20 anni il rischio
              di rendimento reale negativo scende (nella storia dell'S&P 500 nessuna finestra di 20 anni è
              mai stata negativa in termini reali).
            </div>
          )}
        </div>
      )}

      {/* Fonte */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Fonti.</strong> Shiller CAPE (PE10) e S&amp;P 500 total return dal dataset Shiller,
        esteso con multpl. Rendimenti reali deflazionati per CPI. Panel: {lookup.meta.panel_months} mesi
        ({lookup.meta.panel_start} → {lookup.meta.panel_end}). Metodologia completa:{" "}
        <a href="/posts/shiller-cape-predice-rendimenti" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">articolo di riferimento</a>.
      </div>
    </div>
  );
}

function RowH({ label, med, p5, p95, nom, highlight }) {
  const fmt = (x) => {
    if (x === null || x === undefined || Number.isNaN(x)) return "—";
    const s = x >= 0 ? "+" : "";
    return `${s}${(x * 100).toFixed(1)}%`;
  };
  return (
    <tr className={`border-b border-slate-100 dark:border-slate-800 ${
      highlight ? "bg-blue-50 dark:bg-blue-950" : ""
    }`}>
      <td className="py-2 pr-3 font-medium text-slate-800 dark:text-slate-200">{label}</td>
      <td className="py-2 pr-3 text-right tabular-nums font-semibold">{fmt(med)}</td>
      <td className="py-2 pr-3 text-right tabular-nums text-slate-500 dark:text-slate-400">{fmt(p5)} → {fmt(p95)}</td>
      <td className="py-2 pl-3 text-right tabular-nums">{fmt(nom)}</td>
    </tr>
  );
}
