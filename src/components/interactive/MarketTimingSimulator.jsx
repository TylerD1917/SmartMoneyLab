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
  ReferenceLine,
} from "recharts";

/**
 * MarketTimingSimulator — replica in JS l'algoritmo dello script Python
 * `comprare-ai-minimi-market-timing.py`, permettendo all'utente di variare
 * tre parametri chiave e vedere il risultato live sull'equity curve.
 *
 * Dati: carica `/charts/comprare-ai-minimi-market-timing/sp500_monthly_returns.json`
 * (esportato dallo script). Il JSON contiene la serie mensile dei rendimenti
 * S&P 500 TR dal 1976 al 2025.
 */

const QUARTERLY_FLOW = 1000;
const DATA_URL =
  "/charts/comprare-ai-minimi-market-timing/sp500_monthly_returns.json";

const COLORS = {
  passive: "#1e3a8a",
  timing: "#d97706",
  reference: "#94a3b8",
};

const eur = (n) =>
  n.toLocaleString("it-IT", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

const pct = (n) =>
  (n * 100).toLocaleString("it-IT", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }) + "%";

// -------- Algoritmo di simulazione (porting da Python) -------- //

function simulatePassive(returns, dates) {
  let portfolio = 0;
  const out = [];
  for (let i = 0; i < returns.length; i++) {
    const d = new Date(dates[i]);
    portfolio *= 1 + returns[i];
    if ([0, 3, 6, 9].includes(d.getMonth())) {
      portfolio += QUARTERLY_FLOW;
    }
    out.push(portfolio);
  }
  return out;
}

function simulateTiming(returns, dates, savingsPct, drawdownTrigger, cdAnnual) {
  const cdMonthly = Math.pow(1 + cdAnnual, 1 / 12) - 1;
  // NAV S&P 500 + drawdown
  const navs = [];
  let nav = 1;
  for (const r of returns) {
    nav *= 1 + r;
    navs.push(nav);
  }
  const peaks = [];
  let peak = 0;
  for (const v of navs) {
    if (v > peak) peak = v;
    peaks.push(peak);
  }
  const dd = navs.map((v, i) => v / peaks[i] - 1);

  let eq = 0;
  let cassetto = 0;
  const out = [];
  const deploys = [];
  for (let i = 0; i < returns.length; i++) {
    const d = new Date(dates[i]);
    eq *= 1 + returns[i];
    cassetto *= 1 + cdMonthly;
    if ([0, 3, 6, 9].includes(d.getMonth())) {
      const currentDD = dd[i];
      if (currentDD <= -drawdownTrigger) {
        const deployAmount = cassetto;
        cassetto = 0;
        eq += deployAmount + QUARTERLY_FLOW;
        if (deployAmount > 0) deploys.push({ date: dates[i], amount: deployAmount });
      } else {
        eq += QUARTERLY_FLOW * (1 - savingsPct);
        cassetto += QUARTERLY_FLOW * savingsPct;
      }
    }
    out.push(eq + cassetto);
  }
  return { values: out, deploys };
}

// -------- Component -------- //

export default function MarketTimingSimulator() {
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);

  // Parametri user-controlled
  const [savingsPct, setSavingsPct] = useState(10); // %
  const [ddTrigger, setDdTrigger] = useState(25); // %
  const [cdRate, setCdRate] = useState(2); // % annuo

  useEffect(() => {
    fetch(DATA_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => setData(d))
      .catch((e) => setLoadError(e.message));
  }, []);

  const sim = useMemo(() => {
    if (!data) return null;
    const passive = simulatePassive(data.returns, data.dates);
    const timing = simulateTiming(
      data.returns,
      data.dates,
      savingsPct / 100,
      ddTrigger / 100,
      cdRate / 100,
    );
    // Sample ~120 punti per la chart (uno ogni ~5 mesi su 600) per fluidità
    const stride = Math.max(1, Math.floor(data.returns.length / 240));
    const chart = [];
    for (let i = 0; i < data.returns.length; i += stride) {
      chart.push({
        date: data.dates[i].slice(0, 7),
        Passivo: passive[i],
        Attivo: timing.values[i],
      });
    }
    // Aggiungi sempre l'ultimo punto
    const last = data.returns.length - 1;
    chart.push({
      date: data.dates[last].slice(0, 7),
      Passivo: passive[last],
      Attivo: timing.values[last],
    });
    const finalA = passive[last];
    const finalB = timing.values[last];
    return {
      chart,
      finalA,
      finalB,
      excess: finalB - finalA,
      excessPct: (finalB - finalA) / finalA,
      deployCount: timing.deploys.length,
      deployDates: timing.deploys.map((d) => d.date.slice(0, 7)),
    };
  }, [data, savingsPct, ddTrigger, cdRate]);

  if (loadError) {
    return (
      <div className="not-prose my-8 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
        Impossibile caricare i dati per il simulatore ({loadError}). Verifica
        che il file <code>sp500_monthly_returns.json</code> sia presente in{" "}
        <code>public/charts/comprare-ai-minimi-market-timing/</code>.
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

  return (
    <div className="not-prose my-10 rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6">
      <header className="mb-5 border-b border-slate-200 pb-4 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
          Simulatore: timing attivo vs PIC passivo
        </h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Cambia i parametri della strategia attiva e osserva come si comporta
          rispetto al PIC passivo su 50 anni di S&amp;P 500 (1976–2025), con un
          flusso fisso di 1.000$ ogni trimestre.
        </p>
      </header>

      {/* Sliders */}
      <div className="mb-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <SliderControl
          label="Accantonamento"
          value={savingsPct}
          onChange={setSavingsPct}
          min={0}
          max={30}
          step={1}
          format={(v) => `${v}%`}
          hint="quota del flusso messa in conto deposito ogni trimestre normale"
        />
        <SliderControl
          label="Soglia drawdown"
          value={ddTrigger}
          onChange={setDdTrigger}
          min={5}
          max={50}
          step={1}
          format={(v) => `−${v}%`}
          hint="drawdown dal massimo che attiva il deploy del cassetto"
        />
        <SliderControl
          label="Tasso CD"
          value={cdRate}
          onChange={setCdRate}
          min={0}
          max={8}
          step={0.5}
          format={(v) => `${v}% lordo`}
          hint="rendimento annuo del cassetto"
        />
      </div>

      {/* KPI cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KPI
          label="Valore finale Passivo"
          value={eur(sim.finalA)}
          color={COLORS.passive}
        />
        <KPI
          label="Valore finale Attivo"
          value={eur(sim.finalB)}
          color={COLORS.timing}
        />
        <KPI
          label="Differenza (Attivo − Passivo)"
          value={`${sim.excess >= 0 ? "+" : ""}${eur(sim.excess)}`}
          color={sim.excess >= 0 ? "#15803d" : "#b91c1c"}
        />
        <KPI
          label="Differenza in %"
          value={`${sim.excessPct >= 0 ? "+" : ""}${pct(sim.excessPct)}`}
          color={sim.excessPct >= 0 ? "#15803d" : "#b91c1c"}
        />
      </div>

      {/* Chart */}
      <div className="h-80 w-full">
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
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              width={60}
            />
            <Tooltip
              formatter={(v) => eur(v)}
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
              dataKey="Passivo"
              stroke={COLORS.passive}
              strokeWidth={2}
              dot={false}
              name="PIC passivo (Strategy A)"
            />
            <Line
              type="monotone"
              dataKey="Attivo"
              stroke={COLORS.timing}
              strokeWidth={2}
              dot={false}
              name="Timing attivo (Strategy B)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Deploy info */}
      <div className="mt-5 rounded-md bg-slate-50 px-4 py-3 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
        <strong className="font-semibold text-slate-800 dark:text-slate-100">
          Deploy del cassetto in questa configurazione:
        </strong>{" "}
        {sim.deployCount === 0 ? (
          <>nessuno. Il cassetto non si è mai scaricato in 50 anni — i soldi
          accantonati sono rimasti in CD per tutto il periodo.</>
        ) : (
          <>{sim.deployCount} volta{sim.deployCount > 1 ? "/e" : ""} ({sim.deployDates.join(", ")}).</>
        )}
      </div>

      <p className="mt-4 text-xs italic text-slate-400 dark:text-slate-500">
        Total invested in entrambe le strategie: {eur(QUARTERLY_FLOW * 4 * 50)} su 50 anni.
        Tutti i valori sono lordi di costi e tasse, in USD nominali.
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
        className="w-full accent-blue-900 dark:accent-blue-400"
      />
      <p className="mt-1 text-[11px] leading-snug text-slate-500 dark:text-slate-400">
        {hint}
      </p>
    </label>
  );
}

function KPI({ label, value, color }) {
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
    </div>
  );
}
