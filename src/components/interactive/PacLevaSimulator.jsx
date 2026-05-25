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
 * PacLevaSimulator — ricalcola in browser la DCA con leva tattica.
 *
 * L'utente regola:
 *   - soglia di drawdown che attiva la leva 2x (per indice, calcolata su 1x)
 *   - contribuzione annuale totale (split 30% NASDAQ + 70% SP500)
 *
 * I dati di mercato (NAV 1x e 2x mensili + drawdown 1x per NASDAQ
 * e SP500 dal 1976 al 2025) sono pre-calcolati dallo script Python e
 * caricati da `/charts/pac-leva-tattica/sim_data.json`.
 *
 * La logica di simulazione e' la stessa di `simulate_pac` in Python:
 * ogni mese, se DD dell'indice 1x < -soglia => nuova contribuzione su
 * sleeve 2x; altrimenti su 1x. Le posizioni esistenti non si toccano.
 */

const DATA_URL = "/charts/pac-leva-tattica/sim_data.json";

const COLORS = {
  tactical: "#d97706", // ambra SmartMoneyLab
  buyhold: "#1e3a8a", // navy SmartMoneyLab
  contrib: "#94a3b8",
};

const usd = (n) =>
  n.toLocaleString("it-IT", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

const pct = (n) =>
  (n * 100).toLocaleString("it-IT", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }) + "%";

// -------- Algoritmo di simulazione -------- //

/**
 * Esegue una DCA mensile con regola tattica indipendente per indice.
 * Ritorna serie portafoglio mensile (in dollari) + statistiche.
 *
 * @param {Object} data   payload da sim_data.json
 * @param {number} ddThr  soglia drawdown positiva (es. 0.20 = -20%)
 * @param {number} dcaM   contribuzione mensile in USD
 * @param {boolean} tactical  se false: buy & hold, sempre 1x
 */
function simulate(data, ddThr, dcaM, tactical) {
  const n = data.dates.length;
  const wN = data.meta.w_nasdaq;
  const wS = data.meta.w_sp500;
  const contribN = dcaM * wN;
  const contribS = dcaM * wS;

  // Quote in unita' di NAV (NAV iniziale = 1 → 1 unita' = $1 al t=0,
  // ma contribuiamo a NAV correnti, quindi $1 ora compra meno di
  // 1 unita' man mano che le NAV crescono).
  let uN1 = 0, uN2 = 0, uS1 = 0, uS2 = 0;
  let totalContrib = 0;
  let months2xN = 0, months2xS = 0;

  const portfolio = new Array(n);

  for (let i = 0; i < n; i++) {
    const ndx1 = data.ndx_1x[i];
    const ndx2 = data.ndx_2x[i];
    const sp1 = data.sp_1x[i];
    const sp2 = data.sp_2x[i];
    const ddN = data.ndx_dd[i];
    const ddS = data.sp_dd[i];

    const use2xN = tactical && ddN < -ddThr;
    const use2xS = tactical && ddS < -ddThr;

    if (use2xN) {
      uN2 += contribN / ndx2;
      months2xN++;
    } else {
      uN1 += contribN / ndx1;
    }
    if (use2xS) {
      uS2 += contribS / sp2;
      months2xS++;
    } else {
      uS1 += contribS / sp1;
    }
    totalContrib += dcaM;

    portfolio[i] = uN1 * ndx1 + uN2 * ndx2 + uS1 * sp1 + uS2 * sp2;
  }

  // Valore finale: rivaluto sulle NAV finali (poco oltre l'ultimo
  // contributo, per coerenza con la simulazione Python).
  const f = data.final;
  const finalValue = uN1 * f.ndx_1x + uN2 * f.ndx_2x + uS1 * f.sp_1x + uS2 * f.sp_2x;

  return {
    portfolio,
    finalValue,
    totalContrib,
    months2xN,
    months2xS,
    monthsTotal: n,
  };
}

// -------- Component -------- //

export default function PacLevaSimulator() {
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);

  // Slider state (con default = parametri dell'articolo)
  const [ddThrPct, setDdThrPct] = useState(20); // %
  const [dcaAnnual, setDcaAnnual] = useState(3600); // USD/anno (= $300/mese)

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
    const dcaMonthly = dcaAnnual / 12;
    const ddThr = ddThrPct / 100;
    const tactical = simulate(data, ddThr, dcaMonthly, true);
    const buyhold = simulate(data, ddThr, dcaMonthly, false);

    // Per il chart riduco a ~240 punti (1 ogni ~2.5 mesi). Su 600
    // mesi di dati 240 punti sono piu' che sufficienti per una
    // curva liscia.
    const n = data.dates.length;
    const stride = Math.max(1, Math.floor(n / 240));
    const chart = [];
    for (let i = 0; i < n; i += stride) {
      chart.push({
        date: data.dates[i].slice(0, 7),
        Tattica: tactical.portfolio[i],
        BuyHold: buyhold.portfolio[i],
        Versato: (i + 1) * dcaMonthly,
      });
    }
    // Punto finale sempre presente
    chart.push({
      date: data.dates[n - 1].slice(0, 7),
      Tattica: tactical.finalValue,
      BuyHold: buyhold.finalValue,
      Versato: n * dcaMonthly,
    });

    const excess = tactical.finalValue - buyhold.finalValue;
    const excessPct =
      buyhold.finalValue > 0 ? excess / buyhold.finalValue : 0;
    const fracMonths2xN = tactical.months2xN / tactical.monthsTotal;
    const fracMonths2xS = tactical.months2xS / tactical.monthsTotal;

    return {
      chart,
      finalTactical: tactical.finalValue,
      finalBuyHold: buyhold.finalValue,
      totalContrib: tactical.totalContrib,
      excess,
      excessPct,
      fracMonths2xN,
      fracMonths2xS,
    };
  }, [data, ddThrPct, dcaAnnual]);

  if (loadError) {
    return (
      <div className="not-prose my-8 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
        Impossibile caricare i dati per il simulatore ({loadError}). Verifica
        che il file <code>sim_data.json</code> sia presente in{" "}
        <code>public/charts/pac-leva-tattica/</code>.
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

  const periodLabel = `${data.meta.start.slice(0, 4)}–${data.meta.end.slice(0, 4)}`;

  return (
    <div className="not-prose my-10 rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6">
      <header className="mb-5 border-b border-slate-200 pb-4 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
          Simulatore: PAC con leva tattica vs PAC buy &amp; hold
        </h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Modifica la soglia di drawdown che attiva la leva e la cifra
          versata ogni anno. Il calcolo gira su 50 anni di dati reali
          ({periodLabel}, split 30% NASDAQ + 70% S&amp;P 500).
        </p>
      </header>

      {/* Sliders */}
      <div className="mb-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <SliderControl
          label="Soglia drawdown"
          value={ddThrPct}
          onChange={setDdThrPct}
          min={5}
          max={50}
          step={1}
          format={(v) => `−${v}%`}
          hint="drawdown su 1x che attiva la leva 2x sulla quota di quell'indice"
        />
        <SliderControl
          label="Contribuzione annuale"
          value={dcaAnnual}
          onChange={setDcaAnnual}
          min={1200}
          max={24000}
          step={600}
          format={(v) => `$${v.toLocaleString("it-IT")}/anno`}
          hint={`pari a ${usd(dcaAnnual / 12)}/mese, ripartiti 30/70 tra NASDAQ e S&P 500`}
        />
      </div>

      {/* KPI cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KPI
          label="Versato totale"
          value={usd(sim.totalContrib)}
          color="#475569"
        />
        <KPI
          label="Buy &amp; Hold"
          value={usd(sim.finalBuyHold)}
          color={COLORS.buyhold}
        />
        <KPI
          label="Leva tattica"
          value={usd(sim.finalTactical)}
          color={COLORS.tactical}
        />
        <KPI
          label="Differenza (tattica − B&amp;H)"
          value={`${sim.excess >= 0 ? "+" : ""}${usd(sim.excess)} (${sim.excessPct >= 0 ? "+" : ""}${pct(sim.excessPct)})`}
          color={sim.excess >= 0 ? "#15803d" : "#b91c1c"}
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
              tickFormatter={(v) =>
                v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : `${(v / 1e3).toFixed(0)}k`
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
              name="Versato cumulato"
            />
            <Line
              type="monotone"
              dataKey="BuyHold"
              stroke={COLORS.buyhold}
              strokeWidth={2}
              dot={false}
              name="Buy & Hold 1x"
            />
            <Line
              type="monotone"
              dataKey="Tattica"
              stroke={COLORS.tactical}
              strokeWidth={2}
              dot={false}
              name="Leva tattica"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Info leva */}
      <div className="mt-5 rounded-md bg-slate-50 px-4 py-3 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
        <strong className="font-semibold text-slate-800 dark:text-slate-100">
          Tempo passato in leva 2x:
        </strong>{" "}
        NASDAQ {pct(sim.fracMonths2xN)} dei mesi
        {" · "}
        S&amp;P 500 {pct(sim.fracMonths2xS)} dei mesi.
        {sim.fracMonths2xN === 0 && sim.fracMonths2xS === 0 ? (
          <>
            {" "}
            Con questa soglia il drawdown non e' mai stato abbastanza profondo
            da attivare la leva: la curva tattica coincide con buy &amp; hold.
          </>
        ) : null}
      </div>

      <p className="mt-4 text-xs italic text-slate-400 dark:text-slate-500">
        Drag sintetico ETF 2x calibrato su QQQ/QLD e SPY/SSO: NASDAQ 2x{" "}
        {(data.meta.drag_nq_2x_annual * 100).toFixed(2)}%/anno, S&amp;P 500 2x{" "}
        {(data.meta.drag_sp_2x_annual * 100).toFixed(2)}%/anno. Valori lordi di
        tasse, in USD nominali. Dati storici, non garanzia di risultati futuri.
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
