/**
 * OilRegimeSimulator.jsx
 *
 * Simulatore statico del regime petrolio. L'utente inserisce due parametri:
 *   - prezzo del petrolio reale ($ costanti oggi)
 *   - variazione cumulata trailing 3 mesi (in %)
 * Il componente classifica il regime nei due bucket (livello + variazione)
 * e mostra il range storico dei rendimenti mediana + p5/p95 a 6m, 12m, 24m
 * per i 7 indici azionari del backtest.
 *
 * Framing (coerente con l'articolo sorgente):
 *   NON e' un previsore. Mostra cosa e' successo storicamente nei periodi
 *   classificati nello stesso bucket. La correlazione livello ↔ rendimenti
 *   e' negativa ma modesta e molto eterogenea per indice.
 *
 * Dati: fetch /tools/oil-regime-lookup.json (statico, generato dallo script
 * backtest scripts/petrolio-e-mercati-azionari.py).
 *
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useEffect, useMemo } from "react";

const LOOKUP_URL = "/tools/oil-regime-lookup.json";

const LEVEL_BINS = [
  { label: "sotto $40 (basso)",   min: -Infinity, max: 40 },
  { label: "$40-70 (normale)",    min: 40,        max: 70 },
  { label: "$70-100 (elevato)",   min: 70,        max: 100 },
  { label: "sopra $100 (shock)",  min: 100,       max: Infinity },
];
// Corrispondenza col label esatto usato dallo script Python (chiavi del JSON)
const LEVEL_KEY = {
  "sotto $40 (basso)":  "<$40 (basso)",
  "$40-70 (normale)":   "$40-70 (normale)",
  "$70-100 (elevato)":  "$70-100 (elevato)",
  "sopra $100 (shock)": ">$100 (shock)",
};

const CHANGE_THRESHOLD = 30; // in %

const ASSETS = ["SP500","NASDAQ","ACWI","DAX","FTSE100","NIKKEI","MSCI_EM"];
const ASSET_LABELS = {
  SP500:   "S&P 500 TR",
  NASDAQ:  "NASDAQ",
  ACWI:    "MSCI ACWI",
  DAX:     "DAX TR",
  FTSE100: "FTSE 100",
  NIKKEI:  "Nikkei",
  MSCI_EM: "MSCI EM",
};

function classifyLevel(price) {
  for (const b of LEVEL_BINS) {
    if (price >= b.min && price < b.max) return b.label;
  }
  return null;
}
function classifyChange(pct) {
  if (pct <= -CHANGE_THRESHOLD) return "Crollo (<=-30%)";
  if (pct >=  CHANGE_THRESHOLD) return "Impennata (>=+30%)";
  return "Stabile (-30 +30)";
}

function fmtPct(x, digits = 1) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return `${(x * 100).toFixed(digits)}%`;
}

export default function OilRegimeSimulator() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lookup, setLookup] = useState(null);
  // Default: prezzo attuale WTI reale ~65$, variazione recente flat.
  const [price, setPrice] = useState(65);
  const [change, setChange] = useState(0);

  useEffect(() => {
    fetch(LOOKUP_URL)
      .then(r => r.ok ? r.json() : Promise.reject("Lookup non caricato"))
      .then(j => { setLookup(j); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const derived = useMemo(() => {
    const levelHumanLabel = classifyLevel(price);
    const changeLabel = classifyChange(change);
    return {
      levelHumanLabel,
      levelKey: levelHumanLabel ? LEVEL_KEY[levelHumanLabel] : null,
      changeLabel,
    };
  }, [price, change]);

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

  const corrFwd12 = lookup?.meta?.correlations?.level_vs_?.MSCI_EM_fwd12m;

  return (
    <div className="not-prose my-8 space-y-6">

      {/* FRAMING */}
      <div className="rounded-2xl border-2 border-amber-400 bg-amber-50 p-5 dark:border-amber-600 dark:bg-amber-950/40">
        <div className="flex items-start gap-3">
          <div className="text-2xl leading-none">⚠</div>
          <div>
            <h3 className="mb-1 text-base font-bold text-amber-900 dark:text-amber-200">
              Simulatore descrittivo, NON previsivo
            </h3>
            <p className="text-sm text-amber-900 dark:text-amber-100">
              I range che vedi sotto descrivono cosa e' successo <em>storicamente</em>
              in periodi classificati nello stesso bucket. La correlazione fra livello
              di petrolio e rendimenti forward e' negativa ma modesta ed eterogenea
              per indice — massima sugli emerging ({corrFwd12 !== undefined ? corrFwd12.toFixed(2) : "—"} per MSCI EM fwd 12m), praticamente
              zero per il DAX. Non usare questo tool come indicatore operativo.
            </p>
          </div>
        </div>
      </div>

      {/* INPUT */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h3 className="mb-4 text-lg font-bold text-slate-900 dark:text-slate-100">
          Imposta il regime che vuoi esplorare
        </h3>
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Prezzo WTI reale ($ costanti oggi)</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">${price}</span>
            </label>
            <input type="range" min="20" max="160" step="1"
                    value={price}
                    onChange={e => setPrice(Number(e.target.value))}
                    className="mt-1 w-full accent-blue-700" />
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              da $20 a $160. Panel storico: min ~$20 (COVID 2020), max ~$160 (mid-2008).
            </div>
          </div>
          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Variazione trailing 3 mesi</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">
                {change >= 0 ? "+" : ""}{change}%
              </span>
            </label>
            <input type="range" min="-70" max="70" step="1"
                    value={change}
                    onChange={e => setChange(Number(e.target.value))}
                    className="mt-1 w-full accent-blue-700" />
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              da -70% a +70%. Soglie regime: crollo ≤ -30%, impennata ≥ +30%.
            </div>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-900 dark:bg-blue-900 dark:text-blue-100">
            Livello: {derived.levelHumanLabel}
          </span>
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-900 dark:bg-blue-900 dark:text-blue-100">
            Variazione: {derived.changeLabel}
          </span>
        </div>
      </div>

      {/* TABELLA per regime livello */}
      <ResultsCard
        title="Cosa e' successo storicamente per LIVELLO di petrolio reale"
        subtitle={`Bucket attivo: ${derived.levelHumanLabel}. Rendimenti forward per i 7 indici del backtest — mediana CAGR e range p5-p95.`}
        lookupSection={lookup.level}
        activeKey={derived.levelKey}
      />

      {/* TABELLA per regime variazione */}
      <ResultsCard
        title="Cosa e' successo storicamente per VARIAZIONE trailing 3 mesi"
        subtitle={`Bucket attivo: ${derived.changeLabel}. Il crollo di petrolio precede storicamente i migliori 12 mesi forward per l'equity — perche' e' sintomo di recessione in corso + Fed cutting successivo.`}
        lookupSection={lookup.change}
        activeKey={derived.changeLabel}
      />

      {/* Fonte */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Fonti dati.</strong> WTI daily da Yahoo Finance, deflazionato con CPI Shiller
        (base = ultimo mese disponibile). Indici: S&amp;P 500 TR Shiller, NASDAQ + 0.75%/y div,
        MSCI ACWI + 1.9%, DAX TR nativo, FTSE 100 + 3.5%, Nikkei + 1.8%, MSCI EM Gross TR USD.
        Panel: {lookup.meta.panel_months} osservazioni mensili ({lookup.meta.panel_start} → {lookup.meta.panel_end}).
        Metodologia completa: <a href="/posts/petrolio-e-mercati-azionari" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">articolo di riferimento</a>.
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ //
function ResultsCard({ title, subtitle, lookupSection, activeKey }) {
  const buckets = Object.keys(lookupSection.SP500 || {});
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
      <h3 className="mb-1 text-lg font-bold text-slate-900 dark:text-slate-100">
        {title}
      </h3>
      <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">{subtitle}</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <th className="py-2 pr-3">Indice</th>
              {buckets.map(b => (
                <th key={b} className={`py-2 pr-3 text-right ${b === activeKey ? "text-blue-700 dark:text-blue-400" : ""}`}>
                  {b} <span className="block font-normal normal-case text-xs">fwd12m (n={lookupSection.SP500[b]?.n})</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ASSETS.map(asset => (
              <tr key={asset} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-2 pr-3 font-medium text-slate-800 dark:text-slate-200">
                  {ASSET_LABELS[asset]}
                </td>
                {buckets.map(b => {
                  const s = lookupSection[asset]?.[b];
                  const isActive = b === activeKey;
                  return (
                    <td key={b} className={`py-2 pr-3 text-right tabular-nums ${
                      isActive ? "bg-blue-50 font-semibold text-blue-900 dark:bg-blue-950 dark:text-blue-100" : ""
                    }`}>
                      {fmtPct(s?.fwd12_cagr_median)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Riga range 6m / 24m del bucket attivo */}
      {activeKey && lookupSection.SP500[activeKey] && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
          <strong>Range forward 12m nel bucket attivo (mediana / p5 / p95 — hit rate):</strong>
          <ul className="mt-2 space-y-1">
            {ASSETS.map(asset => {
              const s = lookupSection[asset]?.[activeKey];
              if (!s) return null;
              return (
                <li key={asset}>
                  <span className="font-medium">{ASSET_LABELS[asset]}</span>:{" "}
                  mediana {fmtPct(s.fwd12_cagr_median)}, range {fmtPct(s.fwd12_p5)} → {fmtPct(s.fwd12_p95)},
                  hit rate positivo {fmtPct(s.fwd12_hit_rate, 0)}.
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
