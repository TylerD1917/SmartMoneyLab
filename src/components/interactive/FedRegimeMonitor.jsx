/**
 * FedRegimeMonitor.jsx
 *
 * Strumento live SmartMoneyLab: diagnostica il regime attuale della Fed
 * (livello FFR nominale + reale, direzione trailing 12m) usando dati
 * pubblici FRED e mostra, per il bucket in cui ci troviamo oggi, il
 * range storico dei rendimenti S&P 500 total return e NASDAQ Composite
 * (proxy TR) su 55 anni (1971-2026, panel del backtest sorgente).
 *
 * Framing editoriale (coerente con l'articolo sorgente):
 *   NON è un previsore. È un "posizionatore storico".
 *   Il numero mostrato è: "nei periodi storici classificati nello stesso
 *   bucket, la mediana e i percentili dei rendimenti sono stati X."
 *   La correlazione lineare bucket-vs-rendimento è essenzialmente zero.
 *   Questo range descrive il bucket, non predice il futuro.
 *
 * Fetch strategy:
 *   1. Fetch client-side FRED CSV pubblici (FEDFUNDS + CPIAUCSL)
 *      - endpoint: https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>
 *   2. Se il fetch fallisce (CORS, rete, altro):
 *      - fallback a lookup statico: usa panel_end come "as-of" dei dati
 *      - banner esplicito "dati non live, snapshot del backtest"
 *
 * Lookup dei rendimenti per bucket:
 *   fetch('/tools/monitor-regime-fed-lookup.json')
 *   generato da scripts/regimi-tassi-sp500-nasdaq.py + estrazione JSON.
 *
 * Autore: SmartMoneyLab — 2026.
 */

import { useState, useEffect, useMemo } from "react";

// ------------------------------------------------------------------ //
// Endpoints e costanti                                                //
// ------------------------------------------------------------------ //
const FRED_FFR_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS";
const FRED_CPI_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL";
const LOOKUP_URL = "/tools/monitor-regime-fed-lookup.json";

const DIR_THRESHOLD_PP = 1.0; // coerente col backtest sorgente
const REAL_BINS = [
  { label: "<0% (accomodante)", min: -Infinity, max: 0 },
  { label: "0-2%",              min: 0,         max: 2 },
  { label: "2-4%",              min: 2,         max: 4 },
  { label: ">4% (restrittivo)", min: 4,         max: Infinity },
];

// ------------------------------------------------------------------ //
// Utility                                                             //
// ------------------------------------------------------------------ //
function parseFredCsv(csv) {
  // formato: "observation_date,FEDFUNDS\n1954-07-01,0.80\n..."
  // ritorna array [{date: Date, value: number}] ordinato asc
  const lines = csv.trim().split(/\r?\n/);
  const out = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const parts = line.split(",");
    if (parts.length < 2) continue;
    const date = new Date(parts[0]);
    const value = parseFloat(parts[1]);
    if (!isNaN(date.getTime()) && !isNaN(value)) {
      out.push({ date, value });
    }
  }
  return out.sort((a, b) => a.date - b.date);
}

function fmtPct(x, digits = 2) {
  if (x === null || x === undefined || isNaN(x)) return "—";
  return `${(x * 100).toFixed(digits)}%`;
}

function fmtNum(x, digits = 2) {
  if (x === null || x === undefined || isNaN(x)) return "—";
  return x.toFixed(digits);
}

function fmtDate(d) {
  if (!d) return "—";
  const months = ["gen", "feb", "mar", "apr", "mag", "giu",
                  "lug", "ago", "set", "ott", "nov", "dic"];
  return `${months[d.getMonth()]} ${d.getFullYear()}`;
}

function classifyDirection(deltaPp) {
  if (deltaPp === null || isNaN(deltaPp)) return null;
  if (deltaPp >= DIR_THRESHOLD_PP) return "Rialzo (≥+1pp)";
  if (deltaPp <= -DIR_THRESHOLD_PP) return "Discesa (≤−1pp)";
  return "Stabile (−1÷+1pp)";
}

function classifyRealLevel(realPp) {
  if (realPp === null || isNaN(realPp)) return null;
  for (const b of REAL_BINS) {
    if (realPp >= b.min && realPp < b.max) return b.label;
  }
  return null;
}

// ------------------------------------------------------------------ //
// Componente                                                          //
// ------------------------------------------------------------------ //
export default function FedRegimeMonitor() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState("live"); // "live" | "snapshot"
  const [ffrCurrent, setFfrCurrent] = useState(null);
  const [ffr12mAgo, setFfr12mAgo] = useState(null);
  const [cpiYoY, setCpiYoY] = useState(null);
  const [asOfDate, setAsOfDate] = useState(null);
  const [lookup, setLookup] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchAll() {
      try {
        // Lookup e' obbligatorio (statico, servito dallo stesso origin)
        const lookupResp = await fetch(LOOKUP_URL);
        if (!lookupResp.ok) throw new Error("Lookup non caricato");
        const lookupJson = await lookupResp.json();
        if (cancelled) return;
        setLookup(lookupJson);

        // Prova fetch FRED
        let ffrData = null;
        let cpiData = null;
        try {
          const [ffrResp, cpiResp] = await Promise.all([
            fetch(FRED_FFR_URL),
            fetch(FRED_CPI_URL),
          ]);
          if (!ffrResp.ok || !cpiResp.ok) throw new Error("FRED HTTP error");
          const [ffrCsv, cpiCsv] = await Promise.all([
            ffrResp.text(),
            cpiResp.text(),
          ]);
          ffrData = parseFredCsv(ffrCsv);
          cpiData = parseFredCsv(cpiCsv);
          if (ffrData.length === 0 || cpiData.length === 0) {
            throw new Error("FRED CSV vuoto");
          }
        } catch (fredErr) {
          console.warn("Fetch FRED fallito, uso snapshot statico:", fredErr);
          if (cancelled) return;
          setDataSource("snapshot");
          // fallback: usa i dati as-of dal panel_end del backtest
          // (posso solo mostrare i bucket e le date, non i valori esatti FFR/CPI attuali)
          setAsOfDate(new Date(lookupJson.meta.panel_end));
          setLoading(false);
          return;
        }

        // Estraggo osservazioni: ultima + 12 mesi prima
        const lastFfr = ffrData[ffrData.length - 1];
        const target12mAgo = new Date(lastFfr.date);
        target12mAgo.setMonth(target12mAgo.getMonth() - 12);
        // trovo la piu' vicina precedente
        let ffr12m = null;
        for (let i = ffrData.length - 1; i >= 0; i--) {
          if (ffrData[i].date <= target12mAgo) {
            ffr12m = ffrData[i];
            break;
          }
        }
        const lastCpi = cpiData[cpiData.length - 1];
        let cpi12m = null;
        const cpiTarget = new Date(lastCpi.date);
        cpiTarget.setMonth(cpiTarget.getMonth() - 12);
        for (let i = cpiData.length - 1; i >= 0; i--) {
          if (cpiData[i].date <= cpiTarget) {
            cpi12m = cpiData[i];
            break;
          }
        }

        if (cancelled) return;
        setFfrCurrent(lastFfr);
        setFfr12mAgo(ffr12m);
        if (cpi12m && cpi12m.value > 0) {
          setCpiYoY(((lastCpi.value / cpi12m.value) - 1) * 100);
        }
        setAsOfDate(lastFfr.date);
        setLoading(false);
      } catch (e) {
        if (cancelled) return;
        console.error("Errore caricamento monitor:", e);
        setError(e.message || String(e));
        setLoading(false);
      }
    }

    fetchAll();
    return () => { cancelled = true; };
  }, []);

  // Calcoli derivati
  const derived = useMemo(() => {
    if (!ffrCurrent || !ffr12mAgo || cpiYoY === null) return null;
    const deltaFFR = ffrCurrent.value - ffr12mAgo.value;
    const ffrReal = ffrCurrent.value - cpiYoY;
    return {
      deltaFFR,
      ffrReal,
      directionBucket: classifyDirection(deltaFFR),
      realBucket: classifyRealLevel(ffrReal),
    };
  }, [ffrCurrent, ffr12mAgo, cpiYoY]);

  // ------------ Rendering ------------ //
  if (loading) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        Caricamento dati FRED (Fed Funds + CPI)…
      </div>
    );
  }

  if (error) {
    return (
      <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
        <strong>Errore caricamento dati:</strong> {error}
        <p className="mt-2 text-sm">
          Ricarica la pagina; se il problema persiste, i dati storici del backtest sono comunque consultabili nell'articolo di riferimento.
        </p>
      </div>
    );
  }

  return (
    <div className="not-prose my-8 space-y-6">

      {/* FRAMING CARD — sempre visibile in alto */}
      <div className="rounded-2xl border-2 border-amber-400 bg-amber-50 p-5 dark:border-amber-600 dark:bg-amber-950/40">
        <div className="flex items-start gap-3">
          <div className="text-2xl leading-none">⚠</div>
          <div>
            <h3 className="mb-1 text-base font-bold text-amber-900 dark:text-amber-200">
              Questo strumento NON è un previsore
            </h3>
            <p className="text-sm text-amber-900 dark:text-amber-100">
              I range che vedi sotto descrivono cosa è successo <em>storicamente</em> in periodi
              classificati nello stesso bucket di regime. La correlazione lineare fra livello o
              direzione FFR e rendimenti azionari, su 55 anni di dati, è essenzialmente zero
              ({fmtNum(lookup?.meta?.correlations?.ffr_vs_sp500_forward12m, 3) ?? "—"} per S&amp;P 500
              forward 12m). Il valore di questo tool è capire il quadrante macro attuale, non predire
              il prossimo movimento del mercato.
            </p>
          </div>
        </div>
      </div>

      {/* SNAPSHOT BANNER — solo se fallback */}
      {dataSource === "snapshot" && (
        <div className="rounded-xl border border-blue-300 bg-blue-50 p-4 text-sm text-blue-900 dark:border-blue-700 dark:bg-blue-950 dark:text-blue-200">
          <strong>Dati non live.</strong> Non è stato possibile scaricare i dati FRED in tempo reale
          dal tuo browser (probabile blocco CORS). Sto usando l'ultimo snapshot del backtest
          ({asOfDate ? fmtDate(asOfDate) : "—"}). Il bucket attuale potrebbe differire dal presente
          effettivo.
        </div>
      )}

      {/* KPI ATTUALI */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-4 flex items-baseline justify-between">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
            Regime attuale
          </h3>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {dataSource === "live" ? "dati live FRED" : "snapshot backtest"} • as of {fmtDate(asOfDate)}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <KpiCell label="FFR" value={ffrCurrent ? `${fmtNum(ffrCurrent.value)}%` : "—"} />
          <KpiCell label="Variazione 12m" value={derived ? `${derived.deltaFFR >= 0 ? "+" : ""}${fmtNum(derived.deltaFFR)}pp` : "—"} />
          <KpiCell label="CPI YoY" value={cpiYoY !== null ? `${fmtNum(cpiYoY)}%` : "—"} />
          <KpiCell label="FFR reale" value={derived ? `${fmtNum(derived.ffrReal)}%` : "—"} accent />
        </div>
      </div>

      {/* BUCKET B — DIREZIONE */}
      {derived && lookup && derived.directionBucket && (
        <BucketCard
          title="Regime di direzione (trailing 12 mesi)"
          bucketLabel={derived.directionBucket}
          sp500Stats={lookup.direction.SP500[derived.directionBucket]}
          nasdaqStats={lookup.direction.NASDAQ[derived.directionBucket]}
          allBuckets={lookup.meta.dir_labels}
          sp500All={lookup.direction.SP500}
          nasdaqAll={lookup.direction.NASDAQ}
        />
      )}

      {/* BUCKET C — LIVELLO REALE */}
      {derived && lookup && derived.realBucket && (
        <BucketCard
          title="Regime di livello reale (FFR − CPI YoY)"
          bucketLabel={derived.realBucket}
          sp500Stats={lookup.real_level.SP500[derived.realBucket]}
          nasdaqStats={lookup.real_level.NASDAQ[derived.realBucket]}
          allBuckets={lookup.meta.real_bins_labels}
          sp500All={lookup.real_level.SP500}
          nasdaqAll={lookup.real_level.NASDAQ}
        />
      )}

      {/* Snapshot: nessun bucket, mostro comunque i lookup */}
      {dataSource === "snapshot" && !derived && lookup && (
        <>
          <StaticTable
            title="Regime di direzione — range storici tutti i bucket"
            allBuckets={lookup.meta.dir_labels}
            sp500All={lookup.direction.SP500}
            nasdaqAll={lookup.direction.NASDAQ}
          />
          <StaticTable
            title="Regime di livello reale — range storici tutti i bucket"
            allBuckets={lookup.meta.real_bins_labels}
            sp500All={lookup.real_level.SP500}
            nasdaqAll={lookup.real_level.NASDAQ}
          />
        </>
      )}

      {/* Fonte */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        <strong>Fonti dati.</strong> Fed Funds Rate e CPI: FRED (Federal Reserve Bank of St. Louis),
        endpoint pubblici <code className="rounded bg-slate-200 px-1 dark:bg-slate-800">FEDFUNDS</code> e <code className="rounded bg-slate-200 px-1 dark:bg-slate-800">CPIAUCSL</code>.
        Range storici: backtest 1971-2026 su S&amp;P 500 total return (Shiller ricostruito) e NASDAQ
        Composite (price return + 0.75% div/y). Panel: {lookup?.meta?.panel_months ?? "—"} osservazioni mensili.
        Metodologia completa: <a href="/posts/regimi-tassi-sp500-nasdaq" className="text-blue-700 underline hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">articolo di riferimento</a>.
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ //
// Sotto-componenti                                                    //
// ------------------------------------------------------------------ //
function KpiCell({ label, value, accent }) {
  return (
    <div className={`rounded-xl border p-4 ${accent
      ? "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-950"
      : "border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950"}`}>
      <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div className={`mt-1 text-2xl font-bold ${accent
        ? "text-blue-800 dark:text-blue-300"
        : "text-slate-900 dark:text-slate-100"}`}>
        {value}
      </div>
    </div>
  );
}

function BucketCard({ title, bucketLabel, sp500Stats, nasdaqStats, allBuckets, sp500All, nasdaqAll }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
      <div className="mb-2 flex items-baseline justify-between flex-wrap gap-2">
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
          {title}
        </h3>
        <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-900 dark:bg-blue-900 dark:text-blue-100">
          Oggi: {bucketLabel}
        </span>
      </div>
      <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
        Rendimenti storici osservati nei periodi classificati nello stesso bucket ({sp500Stats?.n ?? "—"} mesi). Contemporaneo = rendimento durante il regime; forward 12m/24m = rendimento cumulato nei mesi successivi. Le mediane sono <em>annualizzate</em>.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <th className="py-2 pr-4">Bucket</th>
              <th className="py-2 pr-3 text-right">S&amp;P 500 contemp.</th>
              <th className="py-2 pr-3 text-right">S&amp;P 500 fwd 12m</th>
              <th className="py-2 pr-3 text-right">S&amp;P 500 fwd 24m</th>
              <th className="py-2 pr-3 text-right">NASDAQ contemp.</th>
              <th className="py-2 pr-3 text-right">NASDAQ fwd 12m</th>
              <th className="py-2 pr-3 text-right">NASDAQ fwd 24m</th>
              <th className="py-2 pl-3 text-right">n mesi</th>
            </tr>
          </thead>
          <tbody>
            {allBuckets.map(b => {
              const sp = sp500All[b];
              const nd = nasdaqAll[b];
              const isCurrent = b === bucketLabel;
              return (
                <tr key={b} className={`border-b border-slate-100 dark:border-slate-800 ${
                  isCurrent ? "bg-blue-50 font-semibold dark:bg-blue-950" : ""
                }`}>
                  <td className="py-2 pr-4 text-slate-800 dark:text-slate-200">
                    {isCurrent && <span className="mr-1 text-blue-700 dark:text-blue-400">▶</span>}
                    {b}
                  </td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.contemp_ann_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.fwd12_cagr_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.fwd24_cagr_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(nd?.contemp_ann_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(nd?.fwd12_cagr_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(nd?.fwd24_cagr_median)}</td>
                  <td className="py-2 pl-3 text-right text-xs text-slate-500 tabular-nums">{sp?.n ?? "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {sp500Stats && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
          <strong>Range nel bucket attuale (fwd 12m):</strong>{" "}
          S&amp;P 500 dal {fmtPct(sp500Stats.fwd12_p5)} (p5) al {fmtPct(sp500Stats.fwd12_p95)} (p95),
          hit rate positivo {fmtPct(sp500Stats.fwd12_hit_rate, 0)}.{" "}
          NASDAQ dal {fmtPct(nasdaqStats?.fwd12_p5)} al {fmtPct(nasdaqStats?.fwd12_p95)},
          hit rate {fmtPct(nasdaqStats?.fwd12_hit_rate, 0)}. La mediana è indicativa; la dispersione tra p5 e p95 è la vera storia.
        </div>
      )}
    </div>
  );
}

function StaticTable({ title, allBuckets, sp500All, nasdaqAll }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
      <h3 className="mb-4 text-lg font-bold text-slate-900 dark:text-slate-100">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <th className="py-2 pr-4">Bucket</th>
              <th className="py-2 pr-3 text-right">S&amp;P contemp.</th>
              <th className="py-2 pr-3 text-right">S&amp;P fwd 12m</th>
              <th className="py-2 pr-3 text-right">S&amp;P fwd 24m</th>
              <th className="py-2 pr-3 text-right">NASDAQ contemp.</th>
              <th className="py-2 pr-3 text-right">NASDAQ fwd 12m</th>
              <th className="py-2 pl-3 text-right">n</th>
            </tr>
          </thead>
          <tbody>
            {allBuckets.map(b => {
              const sp = sp500All[b];
              const nd = nasdaqAll[b];
              return (
                <tr key={b} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-2 pr-4 text-slate-800 dark:text-slate-200">{b}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.contemp_ann_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.fwd12_cagr_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(sp?.fwd24_cagr_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(nd?.contemp_ann_median)}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">{fmtPct(nd?.fwd12_cagr_median)}</td>
                  <td className="py-2 pl-3 text-right text-xs text-slate-500 tabular-nums">{sp?.n ?? "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
