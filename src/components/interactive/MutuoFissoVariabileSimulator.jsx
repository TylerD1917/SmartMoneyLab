/**
 * MutuoFissoVariabileSimulator.jsx
 *
 * Simulatore interattivo "Mutuo fisso o variabile" per /strumenti, collegato
 * all'articolo /posts/mutuo-fisso-o-variabile.
 *
 * L'utente imposta capitale, durata, tasso fisso e variabile di partenza, e uno
 * scenario di stress sull'Euribor (di quanto si muove e in quanti anni). Toggle
 * "surroga": rifinanzia il fisso a un fisso più basso quando i tassi scendono.
 * Calcolo deterministico (ammortamento francese), mensile.
 *
 * Prefill dei tassi correnti da /tools/mutuo-rates.json (aggiornato dall'API BCE
 * gratuita via scripts/tools/update_mutuo_rates.py). Fallback a valori statici.
 *
 * Autore: SmartMoneyLab - 2026.
 */
import { useState, useEffect, useMemo } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine,
} from "recharts";

const LOOKUP_URL = "/tools/mutuo-rates.json";
const LOOKUP_PROB = "/tools/mutuo-prob.json";
const NAVY = "#1e3a8a", GOLD = "#f59e0b", GREEN = "#059669", INK = "#0f172a", GREY = "#94a3b8";

// interpolazione lineare (come np.interp) con clamp agli estremi
function interp(xs, ys, x) {
  if (!xs || !xs.length) return null;
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  for (let i = 1; i < xs.length; i++) {
    if (x <= xs[i]) {
      const t = (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
      return ys[i - 1] + t * (ys[i] - ys[i - 1]);
    }
  }
  return ys[ys.length - 1];
}

// fallback se il JSON non carica
const FALLBACK = { fisso: 3.56, variabile: 2.99, euribor: 2.51, spread_variabile: 0.48, period: "2026-07" };
const SURROGA_THR = 0.5;   // conviene surrogare se il nuovo fisso è >= 0,5pp sotto (attrito)
const SURROGA_EVERY = 12;  // si valuta una volta l'anno

const it = (x, d = 0) => x.toLocaleString("it-IT", { minimumFractionDigits: d, maximumFractionDigits: d });
const eur = (x) => "€" + it(Math.round(x));
const pct = (x, d = 2) => it(x, d).replace(".", ",") + "%";

function annuity(bal, rm, k) {
  if (k <= 0) return bal;
  if (Math.abs(rm) < 1e-12) return bal / k;
  return (bal * rm) / (1 - Math.pow(1 + rm, -k));
}

// ratePath: (t)=>tasso ANNUO %; refinance: opzionale (t, currentAnnual)=>nuovoAnnual|null
function amortize(L, N, ratePath, resetM, refinance) {
  let bal = L, pay = null, cur = ratePath(0), tot = 0, peak = 0, nSur = 0;
  const pays = new Array(N);
  for (let t = 0; t < N; t++) {
    if (refinance) {
      if (t > 0 && t % SURROGA_EVERY === 0) {
        const nw = refinance(t, cur);
        if (nw != null) { cur = nw; pay = annuity(bal, cur / 1200, N - t); nSur++; }
      }
    } else {
      cur = ratePath(t);
      if (t % resetM === 0 || pay == null) pay = annuity(bal, cur / 1200, N - t);
    }
    if (pay == null) pay = annuity(bal, cur / 1200, N - t);
    const rm = cur / 1200;
    const interest = bal * rm;
    let principal = pay - interest;
    if (t === N - 1 || principal > bal) { principal = bal; pay = interest + principal; }
    bal -= principal; tot += interest; pays[t] = pay; if (pay > peak) peak = pay;
    if (bal <= 1e-6) break;
  }
  return { pays, totInterest: tot, peak, nSur };
}

const PRESETS = [
  { key: "stabile", label: "Stabile", delta: 0, anni: 2 },
  { key: "shock", label: "Rialzo shock (+3pp)", delta: 3, anni: 2 },
  { key: "salita", label: "Salita lenta (+1,5pp)", delta: 1.5, anni: 6 },
  { key: "discesa", label: "Discesa (−2pp)", delta: -2, anni: 3 },
];

function Slider({ label, value, min, max, step, onChange, fmt }) {
  return (
    <label style={{ display: "block", marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, marginBottom: 4 }}>
        <span style={{ color: "#334155" }}>{label}</span>
        <strong style={{ color: NAVY }}>{fmt(value)}</strong>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ width: "100%", accentColor: NAVY }} />
    </label>
  );
}

function Card({ label, value, color }) {
  return (
    <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 12, padding: "12px 14px", flex: "1 1 140px" }}>
      <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: color || INK }}>{value}</div>
    </div>
  );
}

function ProbBar({ label, value, color }) {
  const p = Math.max(0, Math.min(1, value || 0));
  return (
    <div style={{ margin: "6px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 3 }}>
        <span style={{ color: "#334155" }}>{label}</span>
        <strong style={{ color }}>{Math.round(p * 100)}%</strong>
      </div>
      <div style={{ background: "#eef2f7", borderRadius: 6, height: 10, overflow: "hidden" }}>
        <div style={{ width: (p * 100) + "%", height: "100%", background: color, borderRadius: 6 }} />
      </div>
    </div>
  );
}

export default function MutuoFissoVariabileSimulator() {
  const [rates, setRates] = useState(null);
  const [prob, setProb] = useState(null);
  const [capitale, setCapitale] = useState(200000);
  const [durata, setDurata] = useState(30);
  const [fisso, setFisso] = useState(FALLBACK.fisso);
  const [variabile, setVariabile] = useState(FALLBACK.variabile);
  const [delta, setDelta] = useState(0);
  const [anniStress, setAnniStress] = useState(2);
  const [surroga, setSurroga] = useState(true);

  useEffect(() => {
    fetch(LOOKUP_URL).then(r => r.ok ? r.json() : Promise.reject())
      .then(j => {
        const f = j?.fisso?.pct ?? FALLBACK.fisso, v = j?.variabile?.pct ?? FALLBACK.variabile;
        setRates({ f, v, e: j?.euribor?.pct ?? FALLBACK.euribor, period: j?.fisso?.period ?? FALLBACK.period });
        setFisso(f); setVariabile(v);
      })
      .catch(() => setRates({ ...FALLBACK, f: FALLBACK.fisso, v: FALLBACK.variabile, e: FALLBACK.euribor }));
    fetch(LOOKUP_PROB).then(r => r.ok ? r.json() : Promise.reject())
      .then(setProb).catch(() => setProb(null));
  }, []);

  const sim = useMemo(() => {
    const N = durata * 12, L = capitale;
    const deltaAt = (t) => delta * Math.min(t / Math.max(anniStress * 12, 1), 1); // rampa lineare poi tiene
    const varPath = (t) => variabile + deltaAt(t);
    const marketFixed = (t) => fisso + deltaAt(t);
    const refi = (t, curAnnual) => {
      const m = marketFixed(t);
      return m <= curAnnual - SURROGA_THR ? m : null;
    };
    const F = amortize(L, N, () => fisso, N, null);
    const V = amortize(L, N, varPath, 3, null);
    const S = surroga ? amortize(L, N, () => fisso, N, refi) : null;

    const chart = [];
    for (let t = 0; t < N; t += 3) {
      const row = { anno: +(t / 12).toFixed(2), Fisso: Math.round(F.pays[t]), Variabile: Math.round(V.pays[t]) };
      if (S) row["Fisso con surroga"] = Math.round(S.pays[t]);
      chart.push(row);
    }
    const payF0 = F.pays[0], payV0 = V.pays[0];
    const bestVsFisso = V.totInterest - F.totInterest; // >0: variabile costa più interessi
    return { N, F, V, S, chart, payF0, payV0, bestVsFisso };
  }, [capitale, durata, fisso, variabile, delta, anniStress, surroga]);

  const applyPreset = (p) => { setDelta(p.delta); setAnniStress(p.anni); };

  const verdict = (() => {
    const gap = sim.bestVsFisso; // interessi variabile - fisso
    if (Math.abs(gap) < 500) return { t: "Sul costo, fisso e variabile quasi pari in questo scenario.", c: INK };
    if (gap > 0) return { t: `In questo scenario col fisso paghi ${eur(gap)} di interessi in meno.`, c: NAVY };
    return { t: `In questo scenario col variabile paghi ${eur(-gap)} di interessi in meno.`, c: GOLD };
  })();

  const premio = fisso - variabile;
  const pFisso = prob ? interp(prob.premio_pp, prob.p_fisso, premio) : null;
  const pSurroga = prob ? interp(prob.premio_pp, prob.p_surroga, premio) : null;
  const premioTxt = (premio >= 0 ? "+" : "") + pct(premio, 2).replace("%", " pp");

  return (
    <div className="not-prose" style={{ margin: "2rem 0", border: "1px solid #e2e8f0", borderRadius: 18, overflow: "hidden", fontFamily: "inherit" }}>
      <div style={{ background: NAVY, color: "white", padding: "14px 18px", fontWeight: 700 }}>
        Simulatore mutuo · fisso vs variabile
        {rates && <span style={{ float: "right", fontWeight: 400, fontSize: 12, opacity: 0.85 }}>tassi BCE al {rates.period}</span>}
      </div>

      <div style={{ padding: 18, display: "grid", gap: 18, gridTemplateColumns: "1fr", background: "white" }}>
        {/* Controlli */}
        <div style={{ display: "grid", gap: 20, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
          <div>
            <Slider label="Capitale" value={capitale} min={50000} max={500000} step={10000} onChange={setCapitale} fmt={eur} />
            <Slider label="Durata" value={durata} min={10} max={30} step={5} onChange={setDurata} fmt={(v) => v + " anni"} />
          </div>
          <div>
            <Slider label="Tasso fisso" value={fisso} min={1} max={7} step={0.05} onChange={setFisso} fmt={(v) => pct(v)} />
            <Slider label="Tasso variabile di partenza" value={variabile} min={0.5} max={7} step={0.05} onChange={setVariabile} fmt={(v) => pct(v)} />
          </div>
          <div>
            <Slider label="Stress Euribor (variazione)" value={delta} min={-3} max={5} step={0.25} onChange={setDelta} fmt={(v) => (v >= 0 ? "+" : "") + pct(v, 2).replace("%", " pp")} />
            <Slider label="…raggiunta in" value={anniStress} min={1} max={10} step={1} onChange={setAnniStress} fmt={(v) => v + " anni"} />
          </div>
        </div>

        {/* Preset + toggle surroga */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
          <span style={{ fontSize: 13, color: "#64748b" }}>Scenari:</span>
          {PRESETS.map((p) => (
            <button key={p.key} onClick={() => applyPreset(p)}
              style={{ fontSize: 13, padding: "5px 10px", borderRadius: 8, border: "1px solid " + NAVY, background: (delta === p.delta && anniStress === p.anni) ? NAVY : "white", color: (delta === p.delta && anniStress === p.anni) ? "white" : NAVY, cursor: "pointer" }}>
              {p.label}
            </button>
          ))}
          <label style={{ marginLeft: "auto", fontSize: 14, display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }}>
            <input type="checkbox" checked={surroga} onChange={(e) => setSurroga(e.target.checked)} style={{ accentColor: GREEN }} />
            Surroga (rifinanzia il fisso se i tassi scendono)
          </label>
        </div>

        {/* KPI */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
          <Card label="Rata iniziale fisso" value={eur(sim.payF0)} color={NAVY} />
          <Card label="Rata iniziale variabile" value={eur(sim.payV0)} color={GOLD} />
          <Card label="Rata max variabile" value={eur(sim.V.peak)} color={GOLD} />
          <Card label="Interessi totali fisso" value={eur(sim.F.totInterest)} color={NAVY} />
          <Card label="Interessi totali variabile" value={eur(sim.V.totInterest)} color={GOLD} />
          {sim.S && <Card label={`Interessi fisso + surroga (${sim.S.nSur}×)`} value={eur(sim.S.totInterest)} color={GREEN} />}
        </div>

        {/* Verdetto (un solo scenario) */}
        <div style={{ background: "#f1f5f9", borderRadius: 12, padding: "12px 14px" }}>
          <div style={{ fontWeight: 600, color: verdict.c }}>
            {verdict.t}
            {sim.S && sim.S.totInterest < Math.min(sim.F.totInterest, sim.V.totInterest) &&
              <span style={{ color: GREEN }}> Ma con la surroga il fisso costa meno di entrambi.</span>}
          </div>
          <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>
            Questo è <strong>un solo scenario</strong>, scelto da te. Nessuno conosce il percorso futuro dei tassi: qui sotto, cosa è successo in 26 anni di scenari possibili.
          </div>
        </div>

        {/* Cosa dice la storia: probabilità dallo studio (stesse cifre dell'articolo) */}
        {pFisso != null && (
          <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: "14px 16px" }}>
            <div style={{ fontWeight: 700, color: NAVY, marginBottom: 2 }}>Cosa dice la storia</div>
            <div style={{ fontSize: 13, color: "#64748b", marginBottom: 10 }}>
              Con questo premio del fisso (<strong>{premioTxt}</strong> rispetto al variabile), su 10.000 percorsi dei tassi ricostruiti da 26 anni di dati BCE, ecco in quanti scenari ciascuna strada è costata meno del variabile su 30 anni:
            </div>
            <ProbBar label="Fisso, senza surroga" value={pFisso} color={NAVY} />
            <ProbBar label="Fisso con surroga" value={pSurroga} color={GREEN} />
            <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 8 }}>
              Negli scenari restanti costa meno il variabile. La surroga alza la convenienza del fisso perché ne cattura i ribassi tenendo la protezione sui rialzi. Sopra il 50% = il fisso batte il variabile più spesso che no.
            </div>
          </div>
        )}

        {/* Grafico rata */}
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <LineChart data={sim.chart} margin={{ top: 8, right: 16, bottom: 4, left: 8 }}>
              <CartesianGrid stroke="#eef2f7" />
              <XAxis dataKey="anno" tickFormatter={(v) => v + "a"} tick={{ fontSize: 12 }} minTickGap={30} />
              <YAxis tickFormatter={(v) => "€" + it(v)} tick={{ fontSize: 12 }} width={64} />
              <Tooltip formatter={(v) => eur(v)} labelFormatter={(l) => "Anno " + Math.round(l)} />
              <Legend />
              <Line type="monotone" dataKey="Fisso" stroke={NAVY} dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="Variabile" stroke={GOLD} dot={false} strokeWidth={2} />
              {sim.S && <Line type="monotone" dataKey="Fisso con surroga" stroke={GREEN} dot={false} strokeWidth={2} />}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <p style={{ fontSize: 12, color: "#94a3b8", margin: 0 }}>
          Simulazione deterministica a scopo illustrativo, non una previsione. Ammortamento francese, il variabile si adegua ogni 3 mesi; la surroga rifinanzia il fisso quando il fisso di mercato scende di almeno 0,5 punti. Tassi di partenza dai dati BCE.
        </p>
      </div>
    </div>
  );
}
