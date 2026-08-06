/**
 * CorrelationHeatmap.jsx
 *
 * Heatmap interattiva della matrice di correlazione tra asset class
 * (28 asset, 2006-2026). L'utente passa sopra una cella e legge la
 * correlazione esatta + la coppia; puo' filtrare per categoria.
 *
 * Dati: fetch /tools/corr-lookup.json (generato dallo script backtest).
 *
 * Autore: SmartMoneyLab - 2026.
 */

import { useState, useEffect, useMemo } from "react";

const LOOKUP_URL = "/tools/corr-lookup.json";

const CAT_LABELS = {
  geo: "Geografici",
  settore: "Settoriali",
  bonus: "Bonus geo",
  rifugio: "Rifugio / materie prime",
};

// colore diverging blu(-1) -> bianco(0) -> rosso(+1)
function corrColor(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "#e2e8f0";
  // v in [-1,1]
  if (v >= 0) {
    // bianco -> rosso
    const t = v; // 0..1
    const r = 255;
    const g = Math.round(255 - t * 190);
    const b = Math.round(255 - t * 190);
    return `rgb(${r},${g},${b})`;
  } else {
    const t = -v;
    const r = Math.round(255 - t * 190);
    const g = Math.round(255 - t * 120);
    const b = 255;
    return `rgb(${r},${g},${b})`;
  }
}

export default function CorrelationHeatmap() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [hover, setHover] = useState(null); // {a, b, v}
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetch(LOOKUP_URL)
      .then(r => r.ok ? r.json() : Promise.reject("Lookup non caricato"))
      .then(j => { setData(j); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const assets = useMemo(() => {
    if (!data) return [];
    const all = data.meta.assets_order;
    if (filter === "all") return all;
    return all.filter(a => data.meta.categories[a] === filter);
  }, [data, filter]);

  if (loading) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        Caricamento della matrice…
      </div>
    );
  }
  if (error) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
        <strong>Errore caricamento:</strong> {error}
      </div>
    );
  }

  const n = assets.length;
  const cell = n > 20 ? 22 : 30;

  return (
    <div className="not-prose my-8 space-y-4">
      {/* Controlli + lettura */}
      <div className="flex flex-wrap items-center gap-2">
        {["all", "geo", "settore", "bonus", "rifugio"].map(f => (
          <button key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              filter === f
                ? "bg-blue-700 text-white"
                : "border border-slate-300 text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
            }`}>
            {f === "all" ? "Tutti" : CAT_LABELS[f]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm dark:border-slate-700 dark:bg-slate-900">
        {hover ? (
          <span className="text-slate-800 dark:text-slate-200">
            <strong>{hover.a}</strong> — <strong>{hover.b}</strong>:{" "}
            <span className="font-mono font-bold" style={{ color: hover.v >= 0.5 ? "#b91c1c" : hover.v < 0 ? "#1d4ed8" : "#334155" }}>
              {hover.v >= 0 ? "+" : ""}{hover.v.toFixed(2)}
            </span>
            {hover.v >= 0.85 ? " — quasi lo stesso trade" : hover.v < 0 ? " — si muovono all'opposto (diversificatore vero)" : ""}
          </span>
        ) : (
          <span className="text-slate-500 dark:text-slate-400">Passa sopra una cella per leggere la correlazione esatta.</span>
        )}
      </div>

      {/* Heatmap */}
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <table className="border-collapse" style={{ tableLayout: "fixed" }}>
          <tbody>
            {assets.map((rowA, i) => (
              <tr key={rowA}>
                <td className="pr-2 text-right align-middle text-[10px] text-slate-600 dark:text-slate-300"
                    style={{ whiteSpace: "nowrap", maxWidth: 130, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {rowA}
                </td>
                {assets.map(colB => {
                  const v = data.matrix[rowA]?.[colB];
                  const isDiag = rowA === colB;
                  return (
                    <td key={colB}
                      onMouseEnter={() => !isDiag && setHover({ a: rowA, b: colB, v })}
                      onMouseLeave={() => setHover(null)}
                      title={`${rowA} / ${colB}: ${v?.toFixed?.(2)}`}
                      style={{
                        width: cell, height: cell,
                        background: isDiag ? "#334155" : corrColor(v),
                        cursor: isDiag ? "default" : "pointer",
                        border: hover && ((hover.a === rowA && hover.b === colB) || (hover.a === colB && hover.b === rowA))
                          ? "2px solid #111" : "1px solid rgba(0,0,0,0.05)",
                      }}>
                    </td>
                  );
                })}
              </tr>
            ))}
            {/* etichette colonna (ruotate) */}
            <tr>
              <td></td>
              {assets.map(colB => (
                <td key={colB} className="align-top text-[9px] text-slate-500 dark:text-slate-400"
                    style={{ height: 90 }}>
                  <div style={{ writingMode: "vertical-rl", transform: "rotate(180deg)", whiteSpace: "nowrap", maxHeight: 88, overflow: "hidden" }}>
                    {colB}
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Legenda colore */}
      <div className="flex items-center gap-3 text-xs text-slate-600 dark:text-slate-400">
        <span>−1</span>
        <div className="h-3 flex-1 rounded" style={{ background: "linear-gradient(to right, rgb(65,135,255), white, rgb(255,65,65))" }}></div>
        <span>+1</span>
        <span className="ml-2">blu = scorrelati · rosso = si muovono insieme</span>
      </div>

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Finestra:</strong> {data.meta.window_start} → {data.meta.window_end} ({data.meta.n_months} mesi),
        {" "}{data.meta.assets_order.length} asset, rendimenti mensili in USD.
        Metodologia completa: <a href="/posts/correlazione-asset-class" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">articolo di riferimento</a>.
      </div>
    </div>
  );
}
