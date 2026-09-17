/**
 * AiArena — esperimento "AI Investing Arena".
 * Legge /tools/arena/arena.json (generato dalla GitHub Action): quattro LLM gestiscono
 * 100k virtuali con lo stesso pacchetto dati+news, contro un controllo casuale e i benchmark.
 * Mostra classifica, curve NAV, e per ogni modello la tesi del periodo + le posizioni.
 */
import { useState, useEffect, useMemo } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";

const URL = "/tools/arena/arena.json";

const META = {
  gpt:    { label: "GPT-5.6",         prov: "OpenAI",    color: "#2563eb", kind: "model" },
  gemini: { label: "Gemini 3.1 Pro",  prov: "Google",    color: "#db2777", kind: "model" },
  claude: { label: "Claude Opus 5",   prov: "Anthropic", color: "#ea580c", kind: "model" },
  kimi:   { label: "Kimi K3",         prov: "Moonshot",  color: "#16a34a", kind: "model" },
  random: { label: "Controllo casuale", prov: "baseline", color: "#94a3b8", kind: "control", dash: true },
  ACWI:   { label: "MSCI ACWI",       prov: "benchmark", color: "#64748b", kind: "bench", dash: true },
  SP500:  { label: "S&P 500",         prov: "benchmark", color: "#0f172a", kind: "bench", dash: true },
};
const MODELS = ["gpt", "gemini", "claude", "kimi"];
const ORDER  = ["gpt", "gemini", "claude", "kimi", "random", "ACWI", "SP500"];

const pct = (x, d = 2) => x == null ? "—" : `${x >= 0 ? "+" : "−"}${Math.abs(x * 100).toFixed(d).replace(".", ",")}%`;
const eur = (x) => x == null ? "—" : Math.round(x).toLocaleString("it-IT");
const wpc = (x) => x == null ? "—" : `${(x * 100).toFixed(1).replace(".", ",")}%`;
const ACT = { open: "apre", increase: "aumenta", trim: "riduce", close: "chiude" };
const isBad = (s) => !s || /^\(errore|^\(STUB|^\(parse/.test(String(s));

function Box({ children, err }) {
  return (
    <div className={`not-prose my-8 rounded-2xl border p-5 text-sm ${err ? "border-amber-200 bg-amber-50 text-amber-800" : "border-slate-200 bg-white text-slate-500"}`}>
      {children}
    </div>
  );
}

export default function AiArena() {
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    fetch(URL).then(r => r.ok ? r.json() : Promise.reject("Dati non ancora disponibili"))
      .then(d => setState({ loading: false, d }))
      .catch(e => setState({ loading: false, error: String(e) }));
  }, []);

  const d = state.d;
  const nav = d?.nav ?? {};

  const { chartData, points } = useMemo(() => {
    const cap = d?.rules?.capital || 100000;                     // rendimento sempre dal capitale iniziale (100k)
    const dates = [...new Set(Object.values(nav).flat().map(p => p[0]))].sort();
    const byDate = {};
    Object.entries(nav).forEach(([k, s]) => { if (s && s.length) byDate[k] = Object.fromEntries(s.map(p => [p[0], p[1]])); });
    const rows = dates.map(dt => {
      const row = { d: dt };
      ORDER.forEach(k => { const v = byDate[k]?.[dt]; if (v != null) row[k] = +(((v / cap) - 1) * 100).toFixed(2); });
      return row;
    });
    return { chartData: rows, points: dates.length };
  }, [d]);

  if (state.loading) return <Box>Caricamento dell'esperimento…</Box>;
  if (state.error) return <Box err>L'esperimento non è ancora disponibile: {state.error}</Box>;

  const yFmt = v => `${v > 0 ? "+" : ""}${String(v).replace(".", ",")}%`;
  const board = d.leaderboard ?? [];

  return (
    <div className="not-prose my-8 space-y-6">

      {/* CLASSIFICA */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-700">Classifica — rendimento dal lancio</h3>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 text-left text-slate-600">
                <th className="px-2 py-2 font-semibold">#</th>
                <th className="px-2 py-2 font-semibold">Partecipante</th>
                <th className="px-2 py-2 text-right font-semibold">Rendimento</th>
                <th className="px-2 py-2 text-right font-semibold">NAV</th>
                <th className="px-2 py-2 text-right font-semibold">Max DD</th>
                <th className="px-2 py-2 text-right font-semibold">Sharpe</th>
              </tr>
            </thead>
            <tbody>
              {board.map((r, i) => {
                const m = META[r.id] ?? { label: r.id, color: "#64748b", kind: "model" };
                const badge = m.kind === "model" ? "Modello" : m.kind === "control" ? "Controllo" : "Benchmark";
                return (
                  <tr key={r.id} className="border-t border-slate-100">
                    <td className="px-2 py-2 tabular-nums text-slate-400">{i + 1}</td>
                    <td className="px-2 py-2">
                      <div className="flex items-baseline gap-2">
                        <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: m.color }} />
                        <span className="font-semibold text-slate-800">{m.label}</span>
                        <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500">{badge}</span>
                      </div>
                    </td>
                    <td className={`px-2 py-2 text-right font-semibold tabular-nums ${r.ret_total > 0 ? "text-emerald-600" : r.ret_total < 0 ? "text-rose-600" : "text-slate-500"}`}>{pct(r.ret_total)}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-600">{eur(r.nav)}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-500">{r.max_dd ? pct(r.max_dd) : "—"}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-500">{r.sharpe == null ? "—" : r.sharpe.toFixed(2).replace(".", ",")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs leading-relaxed text-slate-500">
          <strong>Modelli</strong>: i quattro LLM in gara. <strong>Controllo casuale</strong>: un portafoglio che compra
          titoli a caso, con gli stessi vincoli e costi — misura quanta parte del risultato è pura fortuna (un modello che
          non lo batte non sta davvero scegliendo). <strong>Benchmark</strong>: gli indici di mercato (MSCI ACWI e S&P 500).
        </p>
        <p className="mt-2 text-xs text-slate-400">100k$ virtuali ciascuno · valore aggiornato ogni settimana · ultimo pacchetto: {d.as_of}.</p>
      </div>

      {/* CURVE NAV */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-700">Le curve di rendimento</h3>
        {points >= 2 ? (
          <div className="mt-3" style={{ width: "100%", height: 340 }}>
            <ResponsiveContainer>
              <LineChart data={chartData} margin={{ top: 6, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="d" tick={{ fontSize: 11 }} tickFormatter={s => s?.slice(5)} minTickGap={28} />
                <YAxis tick={{ fontSize: 11 }} width={52} domain={["auto", "auto"]} tickFormatter={yFmt} />
                <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v, n) => [yFmt(v), META[n]?.label ?? n]} labelFormatter={l => l} />
                <Legend wrapperStyle={{ fontSize: 12 }} formatter={(v) => META[v]?.label ?? v} />
                {ORDER.map(k => (
                  <Line key={k} type="monotone" dataKey={k} name={k} stroke={META[k].color}
                    strokeWidth={META[k].kind === "model" ? 2.4 : 1.8} strokeDasharray={META[k].dash ? "5 4" : undefined}
                    dot={false} connectNulls isAnimationActive={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="mt-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
            🧪 <strong>Esperimento appena partito.</strong> I portafogli sono stati appena "aperti": le curve di
            rendimento cominceranno a formarsi dal primo aggiornamento settimanale. Torna tra qualche giorno.
          </p>
        )}
        <p className="mt-2 text-xs text-slate-400">Rendimento % dal lancio · linee tratteggiate = controllo casuale e benchmark.</p>
      </div>

      {/* DETTAGLIO PER MODELLO: tesi + posizioni */}
      <div className="grid gap-4 sm:grid-cols-2">
        {MODELS.map(mid => {
          const m = META[mid];
          const dec = d.decisions?.[mid] ?? {};
          const pos = d.positions?.[mid];
          const bad = isBad(dec.rationale);
          const orders = (dec.orders ?? []).filter(o => o && o.ticker);
          return (
            <div key={mid} className="rounded-2xl border border-slate-200 bg-white p-5">
              <div className="flex items-baseline gap-2">
                <span className="inline-block h-3 w-3 rounded-full" style={{ background: m.color }} />
                <h3 className="text-base font-bold text-slate-900">{m.label}</h3>
                <span className="text-xs text-slate-400">{m.prov}</span>
              </div>

              {bad ? (
                <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-500">In attesa di una decisione valida per questo periodo.</p>
              ) : (
                <>
                  <p className="mt-2 text-sm leading-relaxed text-slate-700"><span className="font-semibold text-slate-500">Tesi del periodo — </span>{dec.rationale}</p>

                  {pos && pos.positions?.length > 0 && (
                    <div className="mt-3 overflow-x-auto">
                      <table className="w-full border-collapse text-sm">
                        <thead>
                          <tr className="bg-slate-50 text-left text-slate-500">
                            <th className="px-2 py-1.5 font-semibold">Titolo</th>
                            <th className="px-2 py-1.5 font-semibold">Lato</th>
                            <th className="px-2 py-1.5 text-right font-semibold">Peso</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pos.positions.slice().sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight)).map(p => (
                            <tr key={p.ticker} className="border-t border-slate-100">
                              <td className="px-2 py-1.5">
                                <span className="font-semibold text-slate-800">{p.ticker}</span>
                                {p.name ? <span className="ml-1.5 text-xs font-normal text-slate-400">{p.name}</span> : null}
                              </td>
                              <td className="px-2 py-1.5">
                                <span className={`rounded px-1.5 py-0.5 text-[11px] font-semibold uppercase ${p.side === "short" ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>{p.side}</span>
                              </td>
                              <td className="px-2 py-1.5 text-right tabular-nums text-slate-600">{wpc(p.weight)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      <p className="mt-1.5 text-xs text-slate-400">Liquidità {wpc(pos.cash / pos.equity)} · {pos.positions.length} posizioni</p>
                    </div>
                  )}

                  {orders.length > 0 && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-xs font-semibold text-blue-700">Le mosse del periodo e il perché ({orders.length})</summary>
                      <ul className="mt-2 space-y-1.5">
                        {orders.map((o, i) => (
                          <li key={i} className="text-xs leading-relaxed text-slate-600">
                            <span className="font-semibold text-slate-800">{o.ticker}</span>{o.name ? <span className="text-slate-400"> {o.name}</span> : null} — {ACT[o.action] ?? o.action} {o.side}
                            {o.thesis ? <span className="text-slate-500">: {o.thesis}</span> : null}
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* REGOLE */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-600">
        <h3 className="text-sm font-semibold text-slate-700">Le regole del gioco</h3>
        <p className="mt-2 leading-relaxed">
          Capitale <strong>{eur(d.rules?.capital)}$</strong> virtuali · massimo <strong>{d.rules?.max_positions}</strong> posizioni · long e short su azioni/ETF/ETN/ETC ·
          <strong> niente leva</strong> (esposizione lorda ≤ 100%) · costi realistici (commissione + spread {(d.rules?.costs?.commission * 100).toFixed(2).replace(".", ",")}% + {(d.rules?.costs?.spread * 100).toFixed(2).replace(".", ",")}% per operazione, prestito sugli short) ·
          decisioni ogni <strong>{d.rules?.cadence_days} giorni</strong>, valore aggiornato ogni settimana · benchmark: {(d.rules?.benchmarks ?? []).join(", ")}.
        </p>
        <p className="mt-2 text-xs text-slate-400">{d.disclaimer}</p>
      </div>

    </div>
  );
}
