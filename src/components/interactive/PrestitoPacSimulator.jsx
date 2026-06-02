import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/**
 * PrestitoPacSimulator — ricalcola in browser il confronto Lump Sum
 * finanziato (prestito a tasso fisso) vs PAC tradizionale.
 *
 * L'utente regola:
 *   - TAEG del prestito (0% → 15%)
 *   - capitale ricevuto dal prestito (es. $5k → $40k)
 *   - indice di riferimento (NASDAQ / SP500)
 *   - durata del confronto (10 anni / 20 anni con secondo prestito)
 *
 * La rata mensile e' DERIVATA dalla formula del prestito amortizing:
 *   M = C * r * (1+r)^n / ((1+r)^n - 1),  r = TAEG/12, n = 120
 *
 * Il PAC equivalente investe quella stessa rata mese per mese.
 *
 * Dati: `/charts/prestito-vs-pac/sim_data.json` (NAV mensili 1976-2025
 * di NASDAQ Composite e S&P 500 TR).
 */

const DATA_URL = "/charts/prestito-vs-pac/sim_data.json";
const LOAN_DURATION_M = 120; // costante: prestito decennale
const STEP_M = 3;            // rolling step di 3 mesi
const EXAMPLE_START_OFFSET_20Y = 360; // mese di inizio finestra esempio 20y
                                       // (~mese 360 = 2006-01, attraversa GFC + Covid + rally 2020-2025)

const COLORS = {
  lump: "#d97706",
  pac: "#1e3a8a",
  contrib: "#94a3b8",
};

const usd = (n) =>
  n.toLocaleString("it-IT", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

const usdFine = (n) =>
  n.toLocaleString("it-IT", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });

const pct = (n, digits = 1) =>
  (n * 100).toLocaleString("it-IT", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }) + "%";

const ratioLabel = (r) => {
  const delta = (r - 1) * 100;
  const sign = delta >= 0 ? "+" : "";
  return `${r.toFixed(2)}× (${sign}${delta.toFixed(1)}%)`;
};

// -------- Matematica del prestito -------- //

function loanMonthlyPayment(capital, taegAnnual, nMonths) {
  if (taegAnnual === 0) return capital / nMonths;
  const r = taegAnnual / 12;
  return (capital * r * Math.pow(1 + r, nMonths)) / (Math.pow(1 + r, nMonths) - 1);
}

// -------- Backtest simulation -------- //

/**
 * Per ogni finestra rolling, simula LUMP e PAC e ritorna la
 * distribuzione del ratio finalValueLump / finalValuePac.
 */
function simulateAllWindows(navArr, capital, monthlyPayment, windowMonths) {
  const n = navArr.length;
  const ratios = [];
  const finalsLump = [];
  const finalsPac = [];

  for (let i = 0; i + windowMonths <= n; i += STEP_M) {
    const navStart = navArr[i];
    const navEnd = navArr[i + windowMonths - 1];

    // LUMP: deposito C a t=i (e a t=i+120 se windowMonths === 240)
    let unitsLump = capital / navStart;
    if (windowMonths === 240 && i + 120 < n) {
      unitsLump += capital / navArr[i + 120];
    }
    const finalLump = unitsLump * navEnd;

    // PAC: deposito M a ogni mese da i a i+windowMonths-1
    let unitsPac = 0;
    for (let j = 0; j < windowMonths; j++) {
      unitsPac += monthlyPayment / navArr[i + j];
    }
    const finalPac = unitsPac * navEnd;

    finalsLump.push(finalLump);
    finalsPac.push(finalPac);
    ratios.push(finalLump / finalPac);
  }
  return { ratios, finalsLump, finalsPac, nWindows: ratios.length };
}

/**
 * Esempio di equity curve mensile: una finestra fissa, mostrata
 * per LUMP e PAC contemporaneamente.
 */
function simulateExampleEquity(navArr, dates, capital, monthlyPayment,
                               windowMonths, startOffset) {
  const i0 = Math.min(Math.max(0, startOffset), navArr.length - windowMonths);
  // LUMP units (aggiunti progressivamente se 2° prestito a metà finestra)
  let unitsLumpFirst = capital / navArr[i0];
  let unitsLumpSecond = 0;
  const secondLoanIdx = windowMonths === 240 ? i0 + 120 : -1;

  let unitsPac = 0;
  const points = [];

  for (let j = 0; j < windowMonths; j++) {
    const idx = i0 + j;
    const nav = navArr[idx];

    // Add second loan units when reached
    if (idx === secondLoanIdx) {
      unitsLumpSecond = capital / nav;
    }

    // PAC accumulates monthly
    unitsPac += monthlyPayment / nav;

    const lumpValue = (unitsLumpFirst + unitsLumpSecond) * nav;
    const pacValue = unitsPac * nav;
    const contrib = monthlyPayment * (j + 1);

    points.push({
      date: dates[idx].slice(0, 7),
      Lump: lumpValue,
      PAC: pacValue,
      Versato: contrib,
    });
  }
  return points;
}

function percentile(arr, q) {
  if (arr.length === 0) return NaN;
  const sorted = arr.slice().sort((a, b) => a - b);
  const idx = (sorted.length - 1) * q;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  return sorted[lo] * (hi - idx) + sorted[hi] * (idx - lo);
}

// -------- Component -------- //

export default function PrestitoPacSimulator() {
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);

  // Slider state
  const [taegPct, setTaegPct] = useState(8); // %
  const [capital, setCapital] = useState(20000); // USD
  const [indexKey, setIndexKey] = useState("sp500"); // "nasdaq" | "sp500"
  const [windowYears, setWindowYears] = useState(10); // 10 | 20

  useEffect(() => {
    fetch(DATA_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => setData(d))
      .catch((e) => setLoadError(e.message));
  }, []);

  const monthlyPayment = useMemo(
    () => loanMonthlyPayment(capital, taegPct / 100, LOAN_DURATION_M),
    [capital, taegPct],
  );

  const sim = useMemo(() => {
    if (!data) return null;
    const navArr =
      indexKey === "nasdaq" ? data.nasdaq_nav : data.sp500_nav;
    const windowMonths = windowYears * 12;

    const { ratios, finalsLump, finalsPac, nWindows } =
      simulateAllWindows(navArr, capital, monthlyPayment, windowMonths);

    const winRate = ratios.filter((r) => r > 1).length / ratios.length;
    const p05 = percentile(ratios, 0.05);
    const p25 = percentile(ratios, 0.25);
    const p50 = percentile(ratios, 0.50);
    const p75 = percentile(ratios, 0.75);
    const p95 = percentile(ratios, 0.95);
    const medianFinalLump = percentile(finalsLump, 0.5);
    const medianFinalPac = percentile(finalsPac, 0.5);

    // Esempio di equity curve: per la finestra 20y uso 2006-2025 (covers
    // GFC + ZIRP era + COVID). Per 10y uso ultima finestra 10y completa.
    const exampleStart = windowYears === 20
      ? EXAMPLE_START_OFFSET_20Y
      : navArr.length - windowMonths;
    const chart = simulateExampleEquity(
      navArr, data.dates, capital, monthlyPayment,
      windowMonths, exampleStart,
    );

    return {
      nWindows,
      winRate,
      p05, p25, p50, p75, p95,
      medianFinalLump, medianFinalPac,
      chart,
      exampleStartDate: data.dates[exampleStart].slice(0, 7),
      exampleEndDate: data.dates[
        Math.min(exampleStart + windowMonths - 1, data.dates.length - 1)
      ].slice(0, 7),
    };
  }, [data, capital, monthlyPayment, indexKey, windowYears]);

  if (loadError) {
    return (
      <div className="not-prose my-8 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
        Impossibile caricare i dati per il simulatore ({loadError}). Verifica
        che <code>sim_data.json</code> sia presente in{" "}
        <code>public/charts/prestito-vs-pac/</code>.
      </div>
    );
  }
  if (!data || !sim) {
    return (
      <div className="not-prose my-8 rounded-md border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        Caricamento simulatore…
      </div>
    );
  }

  const totalCashOut = monthlyPayment * windowYears * 12;

  return (
    <div className="not-prose my-10 rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6">
      <header className="mb-5 border-b border-slate-200 pb-4 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
          Simulatore: Lump sum finanziato vs PAC
        </h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Imposta TAEG e capitale del prestito. La rata mensile è derivata
          dalla formula del prestito (durata fissa 10 anni); il PAC investe
          la stessa rata mese per mese. Il backtest gira su 50 anni di
          dati storici (1976–2025).
        </p>
      </header>

      {/* Sliders */}
      <div className="mb-5 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <SliderControl
          label="TAEG del prestito"
          value={taegPct}
          onChange={setTaegPct}
          min={0}
          max={15}
          step={0.25}
          format={(v) => `${v.toFixed(2)}%`}
          hint="tasso effettivo annuo del prestito personale a tasso fisso"
        />
        <SliderControl
          label="Capitale ricevuto"
          value={capital}
          onChange={setCapital}
          min={5000}
          max={40000}
          step={500}
          format={(v) => usd(v)}
          hint={`la rata mensile è derivata: ${usdFine(monthlyPayment)}/mese`}
        />
      </div>

      {/* Toggles */}
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <ToggleGroup
          label="Indice"
          value={indexKey}
          onChange={setIndexKey}
          options={[
            { value: "sp500", label: "S&P 500" },
            { value: "nasdaq", label: "NASDAQ" },
          ]}
        />
        <ToggleGroup
          label="Durata"
          value={windowYears}
          onChange={setWindowYears}
          options={[
            { value: 10, label: "10 anni (1 prestito)" },
            { value: 20, label: "20 anni (2 prestiti)" },
          ]}
        />
      </div>

      {/* KPI cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KPI
          label="Win rate LUMP"
          value={pct(sim.winRate, 1)}
          sub={`${sim.nWindows} finestre rolling`}
          color={sim.winRate >= 0.5 ? "#15803d" : "#b91c1c"}
        />
        <KPI
          label="Ratio mediano (p50)"
          value={ratioLabel(sim.p50)}
          sub="LUMP vs PAC, valore finale"
          color={sim.p50 >= 1 ? COLORS.lump : COLORS.pac}
        />
        <KPI
          label="Caso sfavorevole (p5)"
          value={ratioLabel(sim.p05)}
          sub="5° percentile distribuzione"
          color={sim.p05 >= 1 ? "#15803d" : "#b91c1c"}
        />
        <KPI
          label="Caso favorevole (p95)"
          value={ratioLabel(sim.p95)}
          sub="95° percentile distribuzione"
          color={sim.p95 >= 1 ? "#15803d" : "#b91c1c"}
        />
      </div>

      {/* Tabella percentili dettagliata */}
      <div className="mb-6 overflow-x-auto rounded-md border border-slate-200 dark:border-slate-700">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
            <tr>
              <th className="px-3 py-2 text-left font-medium">Percentile</th>
              <th className="px-3 py-2 text-right font-medium">p5</th>
              <th className="px-3 py-2 text-right font-medium">p25</th>
              <th className="px-3 py-2 text-right font-medium">p50</th>
              <th className="px-3 py-2 text-right font-medium">p75</th>
              <th className="px-3 py-2 text-right font-medium">p95</th>
            </tr>
          </thead>
          <tbody className="text-slate-700 dark:text-slate-300">
            <tr className="border-t border-slate-200 dark:border-slate-700">
              <td className="px-3 py-2 font-medium">Ratio LUMP / PAC</td>
              <td className="px-3 py-2 text-right tabular-nums">
                {sim.p05.toFixed(2)}×
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {sim.p25.toFixed(2)}×
              </td>
              <td className="px-3 py-2 text-right tabular-nums font-semibold">
                {sim.p50.toFixed(2)}×
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {sim.p75.toFixed(2)}×
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {sim.p95.toFixed(2)}×
              </td>
            </tr>
            <tr className="border-t border-slate-200 dark:border-slate-700">
              <td className="px-3 py-2 font-medium">Vantaggio LUMP</td>
              <td className="px-3 py-2 text-right tabular-nums">
                {((sim.p05 - 1) * 100).toFixed(1)}%
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {((sim.p25 - 1) * 100).toFixed(1)}%
              </td>
              <td className="px-3 py-2 text-right tabular-nums font-semibold">
                {((sim.p50 - 1) * 100).toFixed(1)}%
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {((sim.p75 - 1) * 100).toFixed(1)}%
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {((sim.p95 - 1) * 100).toFixed(1)}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Equity curve esempio */}
      <h4 className="mb-1 text-sm font-medium text-slate-700 dark:text-slate-200">
        Esempio di finestra: {sim.exampleStartDate} → {sim.exampleEndDate}
      </h4>
      <p className="mb-3 text-xs text-slate-500 dark:text-slate-400">
        Equity curve di una finestra storica rappresentativa (LUMP vs PAC,
        con stesso cash flow uscito).
      </p>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sim.chart} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: "#64748b" }}
              tickFormatter={(s) => s.split("-")[0]}
              minTickGap={40}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#64748b" }}
              tickFormatter={(v) =>
                v >= 1e6 ? `${(v / 1e6).toFixed(1)}M`
                : v >= 1e3 ? `${(v / 1e3).toFixed(0)}k`
                : v.toFixed(0)
              }
              width={60}
            />
            <Tooltip
              formatter={(v) => usd(v)}
              labelFormatter={(l) => `Mese: ${l}`}
              contentStyle={{
                backgroundColor: "rgba(255,255,255,0.95)",
                border: "1px solid #cbd5e1",
                borderRadius: 6,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line
              type="monotone"
              dataKey="Versato"
              stroke={COLORS.contrib}
              strokeWidth={1.5}
              strokeDasharray="4 3"
              dot={false}
              name="Cash flow uscito"
            />
            <Line
              type="monotone"
              dataKey="PAC"
              stroke={COLORS.pac}
              strokeWidth={2}
              dot={false}
              name="PAC tradizionale"
            />
            <Line
              type="monotone"
              dataKey="Lump"
              stroke={COLORS.lump}
              strokeWidth={2}
              dot={false}
              name="Lump sum finanziato"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Info sotto chart */}
      <div className="mt-5 rounded-md bg-slate-50 px-4 py-3 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
        <strong className="font-semibold text-slate-800 dark:text-slate-100">
          Riassunto della configurazione attuale:
        </strong>
        {" "}
        TAEG {taegPct.toFixed(2)}%, capitale {usd(capital)}, rata derivata{" "}
        {usdFine(monthlyPayment)}/mese, indice {indexKey === "sp500" ? "S&P 500" : "NASDAQ"},
        durata {windowYears} anni
        {windowYears === 20 ? " con doppio prestito consecutivo" : ""}.
        Cash flow personale uscito totale: {usd(totalCashOut)}.
        Valore finale mediano sull'esempio: LUMP {usd(sim.medianFinalLump)}, PAC{" "}
        {usd(sim.medianFinalPac)}.
      </div>

      <p className="mt-4 text-xs italic text-slate-400 dark:text-slate-500">
        Backtest su NAV mensili 1976–2025, finestre rolling step 3 mesi.
        Valori lordi di tasse e di assicurazioni sul prestito; in USD nominali.
        Dati storici, non garanzia di risultati futuri.
      </p>
    </div>
  );
}

// -------- Sub-components -------- //

function SliderControl({ label, value, onChange, min, max, step, format, hint }) {
  return (
    <label className="block">
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
          {label}
        </span>
        <span className="font-mono text-sm font-semibold text-slate-900 dark:text-slate-50">
          {format(value)}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full accent-amber-600 dark:accent-amber-500"
      />
      <p className="mt-1 text-[11px] leading-snug text-slate-500 dark:text-slate-400">
        {hint}
      </p>
    </label>
  );
}

function ToggleGroup({ label, value, onChange, options }) {
  return (
    <div>
      <div className="mb-1 text-sm font-medium text-slate-700 dark:text-slate-200">
        {label}
      </div>
      <div className="inline-flex w-full rounded-md border border-slate-300 dark:border-slate-700">
        {options.map((opt, i) => {
          const active = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange(opt.value)}
              className={[
                "flex-1 px-3 py-1.5 text-sm transition-colors",
                i > 0 ? "border-l border-slate-300 dark:border-slate-700" : "",
                active
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                  : "bg-white text-slate-700 hover:bg-slate-50 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800",
                i === 0 ? "rounded-l-md" : "",
                i === options.length - 1 ? "rounded-r-md" : "",
              ].join(" ")}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function KPI({ label, value, sub, color }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-700 dark:bg-slate-800/60">
      <div className="text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div
        className="mt-0.5 text-base font-semibold tabular-nums"
        style={{ color }}
      >
        {value}
      </div>
      {sub ? (
        <div className="mt-0.5 text-[10px] text-slate-400 dark:text-slate-500">
          {sub}
        </div>
      ) : null}
    </div>
  );
}
