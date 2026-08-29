/**
 * PortfolioLeaderboard — leaderboard dei portafogli celebri.
 * Dati: fetch /tools/leaderboard.json (generato da scripts/leaderboard/build_leaderboard.py,
 * aggiornato settimanalmente dalla GitHub Action). Tutto in EUR, ribilanciamento annuale.
 */
import { useState, useEffect, useMemo } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";

const LOOKUP_URL = "/tools/leaderboard.json";

const ASSET = {
  WORLD: "MSCI World", ALLWORLD: "FTSE All-World", SP500: "S&P 500", NASDAQ: "Nasdaq 100",
  ENERGY: "MSCI Energy", HEALTH: "MSCI Healthcare", EM: "Mercati emergenti", SMALLCAP: "Small cap",
  GOLD: "Oro", BTC: "Bitcoin", COMMODITY: "Commodity", WORLD2X: "MSCI World 2x",
  US_20Y: "Treasury USA 20a", US_10Y: "Treasury USA 10a", US_2Y: "Treasury USA 2a",
  EU_30Y: "BTP 30a", EU_10Y: "BTP 10a", EU_3Y: "BTP 3a",
};
// colore per asset nella barra di composizione (azioni=blu/viola, oro=oro, bond=teal/verde, commodity=bronzo, btc=arancio)
const ASSET_COL = {
  WORLD: "#1e3a8a", ALLWORLD: "#2563eb", SP500: "#3b82f6", NASDAQ: "#6d28d9", WORLD2X: "#4338ca",
  ENERGY: "#ea580c", HEALTH: "#0891b2", EM: "#0ea5e9", SMALLCAP: "#7c3aed",
  GOLD: "#fbbf24", BTC: "#f97316", COMMODITY: "#a16207",
  US_20Y: "#065f46", US_10Y: "#059669", US_2Y: "#34d399", EU_30Y: "#0f766e", EU_10Y: "#14b8a6", EU_3Y: "#5eead4",
};
const LINE_COLORS = ["#1e3a8a","#fbbf24","#e11d48","#059669","#7c3aed","#0891b2","#ea580c","#4d7c0f",
  "#be185d","#0f766e","#a16207","#6d28d9","#b91c1c","#1d4ed8"];
const METRICS = [["ytd","YTD"],["y1","1 anno"],["y3","3 anni"],["y5","5 anni"],["y7","7 anni"]];

const fmtPct = (x) => x == null ? "—" : `${x >= 0 ? "+" : "−"}${Math.abs(x*100).toFixed(1).replace(".", ",")}%`;
const shortDate = (s) => { if(!s) return ""; const [y,m]=s.split("-"); return `${m}/${y.slice(2)}`; };

// gradiente: verde crescente col guadagno (cap 25%), rosso con la perdita (cap 15%)
function heat(x) {
  if (x == null) return {};
  const pos = x >= 0, cap = pos ? 0.25 : 0.15;
  const a = Math.min(Math.abs(x) / cap, 1);
  const alpha = 0.10 + a * 0.80;
  const rgb = pos ? "16,185,129" : "244,63,94";
  return { backgroundColor: `rgba(${rgb},${alpha})`, color: a > 0.55 ? "#ffffff" : "#0f172a" };
}

export default function PortfolioLeaderboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [sort, setSort] = useState({ key: "y5", dir: -1 });
  const [selected, setSelected] = useState(() => new Set(["bench-world"]));
  const [detail, setDetail] = useState(null); // id del portafoglio di cui mostrare la composizione
  const [period, setPeriod] = useState("max"); // finestra grafico: "1","3","5","7","max"

  useEffect(() => {
    fetch(LOOKUP_URL)
      .then(r => r.ok ? r.json() : Promise.reject("Dati non caricati"))
      .then(j => { setData(j); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const rows = useMemo(() => {
    if (!data) return [];
    const arr = [...data.portfolios];
    arr.sort((a, b) => {
      if (sort.key === "name") return sort.dir * a.name.localeCompare(b.name);
      const av = a.metrics[sort.key], bv = b.metrics[sort.key];
      if (av == null) return 1; if (bv == null) return -1;
      return sort.dir * (av - bv);
    });
    return arr;
  }, [data, sort]);

  const chart = useMemo(() => {
    if (!data) return { data: [], series: [] };
    const sel = data.portfolios.filter(p => selected.has(p.id));
    if (sel.length === 0) return { data: [], series: [] };
    // data più recente tra tutti i portafogli, per la finestra temporale
    const lastStr = data.portfolios.reduce((m, p) => p.nav.length && p.nav[p.nav.length-1].d > m ? p.nav[p.nav.length-1].d : m, "0000-00-00");
    let cutoff = "0000-00-00";
    if (period !== "max") {
      const c = new Date(lastStr); c.setFullYear(c.getFullYear() - Number(period));
      cutoff = c.toISOString().slice(0, 10);
    }
    // per ogni serie: filtra alla finestra e ribasa a 100 al primo punto del periodo
    const byDate = new Map();
    sel.forEach(p => {
      const pts = p.nav.filter(pt => pt.d >= cutoff);
      if (!pts.length) return;
      const base = pts[0].v;
      pts.forEach(pt => {
        if (!byDate.has(pt.d)) byDate.set(pt.d, { d: pt.d });
        byDate.get(pt.d)[p.id] = +(pt.v / base * 100).toFixed(2);
      });
    });
    const merged = [...byDate.values()].sort((a, b) => a.d.localeCompare(b.d));
    const series = sel.map(p => ({ id: p.id, label: p.name + (p.variant ? ` · ${p.variant}` : "") }));
    return { data: merged, series };
  }, [data, selected, period]);

  const colorOf = (id) => LINE_COLORS[(data?.portfolios.findIndex(p => p.id === id) ?? 0) % LINE_COLORS.length];
  const clickRow = (id) => {
    setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
    setDetail(id);
  };
  const setHeader = (key) => setSort(s => ({ key, dir: s.key === key ? -s.dir : (key === "name" ? 1 : -1) }));

  if (loading) return <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">Caricamento della leaderboard…</div>;
  if (error) return <div className="not-prose my-8 rounded-2xl border border-red-300 bg-red-50 p-6 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"><strong>Errore:</strong> {error}</div>;

  const arrow = (key) => sort.key === key ? (sort.dir < 0 ? " ↓" : " ↑") : "";
  const detP = data.portfolios.find(p => p.id === detail);

  return (
    <div className="not-prose my-8 space-y-5">
      {/* Grafico */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">Crescita di 100€ (base 100 a inizio periodo, in euro)</h3>
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <div className="flex gap-1.5 text-xs">
            {[["1","1 anno"],["3","3 anni"],["5","5 anni"],["7","7 anni"],["max","Dal 2017"]].map(([v, lbl]) => (
              <button key={v} onClick={() => setPeriod(v)}
                className={`rounded-full px-3 py-1 font-semibold ${period === v ? "bg-blue-700 text-white" : "border border-slate-300 text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"}`}>{lbl}</button>
            ))}
          </div>
          <div className="flex gap-2 text-xs">
            <button onClick={() => setSelected(new Set(data.portfolios.map(p => p.id)))} className="rounded-full border border-slate-300 px-3 py-1 font-semibold text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800">Mostra tutti</button>
            <button onClick={() => setSelected(new Set())} className="rounded-full border border-slate-300 px-3 py-1 font-semibold text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800">Nascondi tutti</button>
          </div>
        </div>
        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chart.data} margin={{ top: 6, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="d" tick={{ fontSize: 11 }} tickFormatter={(s) => s.split("-")[0]} minTickGap={40} />
              <YAxis tick={{ fontSize: 11 }} width={44} tickFormatter={(v) => `${Math.round(v)}`} domain={["auto", "auto"]} />
              <Tooltip formatter={(v, id) => [`${Number(v).toFixed(0)}`, chart.series.find(s => s.id === id)?.label ?? id]} contentStyle={{ fontSize: 12 }} />
              {chart.series.map(s => (
                <Line key={s.id} type="monotone" dataKey={s.id} name={s.label} stroke={colorOf(s.id)} dot={false} strokeWidth={2} connectNulls isAnimationActive={false} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
        {chart.series.length === 0 && <p className="mt-1 text-center text-xs text-slate-400">Seleziona un portafoglio nella tabella per mostrarne la curva.</p>}
      </div>

      {/* Box composizione (al clic su una riga) */}
      {detP && (
        <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <h3 className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-200">
            Composizione — {detP.name}{detP.variant && <span className="ml-1 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-500 dark:bg-slate-700 dark:text-slate-300">{detP.variant}</span>}
          </h3>
          <div className="mb-3 flex h-6 w-full overflow-hidden rounded-lg">
            {detP.allocation.map((a) => (
              <div key={a.asset} style={{ width: `${a.w*100}%`, backgroundColor: ASSET_COL[a.asset] ?? "#94a3b8" }} title={`${(a.w*100).toFixed(0)}% ${ASSET[a.asset] ?? a.asset}`} />
            ))}
          </div>
          <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
            {detP.allocation.map((a) => (
              <li key={a.asset} className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <span className="inline-block h-3 w-3 flex-none rounded-sm" style={{ backgroundColor: ASSET_COL[a.asset] ?? "#94a3b8" }} />
                <span className="tabular-nums font-semibold">{(a.w*100).toFixed(0).replace(".", ",")}%</span> {ASSET[a.asset] ?? a.asset}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tabella */}
      <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-700">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 text-left dark:bg-slate-800">
              <th className="cursor-pointer px-3 py-2 font-semibold text-slate-600 dark:text-slate-300" onClick={() => setHeader("name")}>Portafoglio{arrow("name")}</th>
              {METRICS.map(([k, lbl]) => (
                <th key={k} className="cursor-pointer px-3 py-2 text-right font-semibold text-slate-600 dark:text-slate-300" onClick={() => setHeader(k)}>{lbl}{arrow(k)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => {
              const on = selected.has(p.id);
              const bench = p.category === "benchmark";
              return (
                <tr key={p.id} onClick={() => clickRow(p.id)}
                  className={`cursor-pointer border-t border-slate-100 dark:border-slate-800 ${detail===p.id ? "ring-2 ring-inset ring-blue-400" : ""} hover:bg-slate-50/60 dark:hover:bg-slate-800/50`}>
                  <td className="px-3 py-2">
                    <span className="inline-flex items-center gap-2">
                      <span className="inline-block h-3 w-3 flex-none rounded-full" style={{ backgroundColor: on ? colorOf(p.id) : "transparent", border: on ? "none" : "1.5px solid #cbd5e1" }} />
                      <span>
                        <span className={`font-medium ${bench ? "text-blue-800 dark:text-blue-300" : "text-slate-800 dark:text-slate-100"}`}>{p.name}</span>
                        {p.variant && <span className="ml-1 rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-500 dark:bg-slate-700 dark:text-slate-300">{p.variant}</span>}
                        {bench && <span className="ml-1 text-[11px] uppercase tracking-wide text-blue-500">benchmark</span>}
                        <span className="ml-1 text-[11px] text-slate-400">al {shortDate(p.metrics.as_of)}</span>
                      </span>
                    </span>
                  </td>
                  {METRICS.map(([k]) => (
                    <td key={k} className="px-3 py-2 text-right tabular-nums font-semibold" style={heat(p.metrics[k])}>{fmtPct(p.metrics[k])}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-400">Clicca una riga per vederne la composizione e accendere/spegnere la curva nel grafico. Rendimenti multi-anno annualizzati (CAGR), in euro, al lordo di tasse e costi di negoziazione. Intensità del verde/rosso proporzionale al rendimento.</p>
    </div>
  );
}
