/**
 * RedditSentiment — esperimento "Reddit Retail Sentiment" (r/wallstreetbets).
 * Legge /tools/reddit-sentiment.json (generato mensilmente dalla GitHub Action):
 * ranking con Reddit Sentiment Score, portafoglio top-5 equipesato e curva vs S&P 500.
 */
import { useState, useEffect, useMemo } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";

const URL = "/tools/reddit-sentiment.json";
const NAVY = "#1e3a8a", GOLD = "#fbbf24";
const pct = (x, d = 1) => x == null ? "—" : `${x >= 0 ? "+" : "−"}${Math.abs(x * 100).toFixed(d).replace(".", ",")}%`;

export default function RedditSentiment() {
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    fetch(URL).then(r => r.ok ? r.json() : Promise.reject("Dati non disponibili"))
      .then(d => setState({ loading: false, d }))
      .catch(e => setState({ loading: false, error: String(e) }));
  }, []);

  const nav = state.d?.portfolio?.nav ?? [];
  const perf = useMemo(() => {
    if (nav.length === 0) return null;
    const last = nav[nav.length - 1];
    return { port: last.port / 100 - 1, bench: last.bench / 100 - 1, diff: (last.port - last.bench) / 100, n: nav.length };
  }, [nav]);
  // Serie in % (rendimento dal lancio) — mai numeri indice grezzi sull'asse.
  const chartData = useMemo(
    () => nav.map(p => ({ d: p.d, port: +(p.port - 100).toFixed(2), bench: +(p.bench - 100).toFixed(2) })),
    [nav]
  );
  const yFmt = v => `${v > 0 ? "+" : ""}${String(v).replace(".", ",")}%`;

  if (state.loading) return <Box>Caricamento dell'esperimento…</Box>;
  if (state.error) return <Box err>L'esperimento non è ancora disponibile: {state.error}</Box>;

  const d = state.d;
  const selected = new Set(d.current.selection);

  return (
    <div className="not-prose my-8 space-y-6">
      {/* Performance portafoglio vs benchmark */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-700">Il portafoglio del sentiment vs {d.benchmark}</h3>
        {perf && perf.n >= 2 ? (
          <>
            <div className="mt-1 flex flex-wrap items-baseline gap-x-6 gap-y-1">
              <Stat label="Portafoglio Reddit" value={pct(perf.port)} color={NAVY} />
              <Stat label={d.benchmark} value={pct(perf.bench)} color="#64748b" />
              <Stat label="Differenza" value={pct(perf.diff)} color={perf.diff >= 0 ? "#059669" : "#e11d48"} />
            </div>
            <div className="mt-3" style={{ width: "100%", height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={chartData} margin={{ top: 6, right: 12, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="d" tick={{ fontSize: 11 }} tickFormatter={s => s?.slice(0, 7)} minTickGap={30} />
                  <YAxis tick={{ fontSize: 11 }} width={52} domain={["auto", "auto"]} tickFormatter={yFmt} />
                  <Tooltip contentStyle={{ fontSize: 12 }} formatter={v => yFmt(v)} labelFormatter={l => l} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Line type="monotone" dataKey="port" name="Portafoglio Reddit" stroke={NAVY} strokeWidth={2.4} dot={false} isAnimationActive={false} />
                  <Line type="monotone" dataKey="bench" name={d.benchmark} stroke="#94a3b8" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <p className="mt-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
            🧪 <strong>Esperimento appena partito.</strong> Il portafoglio è stato "acquistato" ora: la curva di
            rendimento inizierà a formarsi dai prossimi aggiornamenti settimanali. Torna tra qualche giorno.
          </p>
        )}
        <p className="mt-2 text-xs text-slate-400">
          Rendimento dal lancio · valuta {d.currency} · {d.weighting} · valore aggiornato ogni settimana · ultimo: {d.updated}.
        </p>
      </div>

      {/* Selezione del mese */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-700">La squadra del mese (top 5, equipesati)</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {d.current.selection.map(tk => (
            <span key={tk} className="rounded-lg bg-blue-900 px-3 py-1.5 text-sm font-bold text-white">{tk} <span className="font-normal text-blue-200">20%</span></span>
          ))}
        </div>
      </div>

      {/* Classifica con score scomposto */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-700">Reddit Sentiment Score — i più chiacchierati del momento</h3>
        <p className="mt-1 text-xs text-slate-500">Il punteggio combina sentiment, menzioni, commenti, crescita e upvote (ciascuno in percentile). Le righe in blu sono quelle scelte per il portafoglio.</p>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 text-left text-slate-600">
                <th className="px-2 py-2 font-semibold">#</th>
                <th className="px-2 py-2 font-semibold">Ticker</th>
                <th className="px-2 py-2 font-semibold">Score</th>
                <th className="px-2 py-2 text-right font-semibold">Sentiment</th>
                <th className="px-2 py-2 text-right font-semibold">Menzioni</th>
                <th className="px-2 py-2 text-right font-semibold">Crescita</th>
                <th className="px-2 py-2 text-right font-semibold">Upvote</th>
              </tr>
            </thead>
            <tbody>
              {d.current.ranking.map(r => {
                const on = selected.has(r.ticker);
                return (
                  <tr key={r.ticker} className={`border-t border-slate-100 ${on ? "bg-blue-50/50" : ""}`}>
                    <td className="px-2 py-2 tabular-nums text-slate-400">{r.rank}</td>
                    <td className="px-2 py-2">
                      <span className="font-semibold text-slate-800" title={r.name}>{r.ticker}</span>
                      {on && <span className="ml-1 text-[11px] font-semibold uppercase text-blue-600">in portafoglio</span>}
                    </td>
                    <td className="px-2 py-2">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
                          <div className="h-full rounded-full" style={{ width: `${Math.round(r.score * 100)}%`, backgroundColor: on ? NAVY : "#cbd5e1" }} />
                        </div>
                        <span className="tabular-nums text-xs text-slate-500">{r.score.toFixed(2).replace(".", ",")}</span>
                      </div>
                    </td>
                    <td className="px-2 py-2 text-right tabular-nums" style={{ color: r.sentiment_score >= 0 ? "#059669" : "#e11d48" }}>{r.sentiment_score >= 0 ? "+" : "−"}{Math.abs(r.sentiment_score).toFixed(2).replace(".", ",")}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-600">{r.mentions.toLocaleString("it-IT")}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-600">{pct(r.growth, 0)}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-slate-600">{r.upvotes.toLocaleString("it-IT")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {d.commento && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold text-slate-700">Il commento del mese</h3>
          <p className="mt-2 text-sm text-slate-600">{d.commento}</p>
        </div>
      )}

      <p className="text-xs text-slate-400">
        Fonti dati: {d.sources?.join(" · ")} (aggregatori pubblici del sentiment su r/{d.subreddit}). Esperimento a scopo
        divulgativo: <strong>non</strong> è un segnale operativo. I rendimenti passati non predicono quelli futuri.
      </p>
    </div>
  );
}

function Box({ children, err }) {
  return <div className={`not-prose my-8 rounded-2xl border p-6 text-center text-sm ${err ? "border-amber-300 bg-amber-50 text-amber-800" : "border-slate-200 bg-slate-50 text-slate-500"}`}>{children}</div>;
}
function Stat({ label, value, color }) {
  return <div><div className="text-lg font-bold tabular-nums" style={{ color }}>{value}</div><div className="text-xs text-slate-500">{label}</div></div>;
}
