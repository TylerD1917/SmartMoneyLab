import { useEffect, useMemo, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
  CartesianGrid, ReferenceLine,
} from "recharts";

/**
 * PrestitoInvestimentoSimulator — conviene un prestito a rate per investire?
 *
 * Confronta due strade che costano a chi le percorre lo STESSO esborso mensile:
 *   A) prendo il prestito, investo subito tutto il capitale erogato, e pago le
 *      rate di tasca mia per tutta la durata;
 *   B) non prendo il prestito e investo ogni mese quella stessa rata (PAC).
 * A fine orizzonte si confrontano i due patrimoni al netto del 26%.
 *
 * Il confronto e' simmetrico per costruzione: in entrambi i casi dalle tasche
 * dell'investitore escono rata x mesi. Cio' che cambia e' che B investe tutto
 * quel denaro (rata x mesi), mentre A investe solo il capitale erogato e la
 * differenza e' il costo del prestito.
 *
 * PER AGGIUNGERE UN PORTAFOGLIO: basta una riga in PORTAFOGLI qui sotto, con i
 * pesi sui mattoni presenti nel JSON delle serie. Nessun'altra modifica.
 */

const DATA_URL = "/tools/prestito-investimento-serie.json";
const ALIQUOTA = 0.26;

// ---------------------------------------------------------------- registro
// I pesi si riferiscono alle chiavi delle serie in prestito-investimento-serie.json
// (world, acwi, sp500, nasdaq, bond, oro). Devono sommare a 1.
const PORTAFOGLI = [
  { id: "sp500",      label: "100% S&P 500",                      pesi: { sp500: 1 } },
  { id: "world",      label: "100% MSCI World",                   pesi: { world: 1 } },
  { id: "acwi",       label: "100% MSCI ACWI IMI",                pesi: { acwi: 1 } },
  { id: "nasdaq",     label: "100% Nasdaq Composite",             pesi: { nasdaq: 1 } },
  { id: "w80b20",     label: "80% World / 20% obbligazionario",   pesi: { world: 0.8, bond: 0.2 } },
  { id: "w60b40",     label: "60% World / 40% obbligazionario",   pesi: { world: 0.6, bond: 0.4 } },
  { id: "w40b60",     label: "40% World / 60% obbligazionario",   pesi: { world: 0.4, bond: 0.6 } },
  { id: "w50b40o10",  label: "50% World / 40% obblig. / 10% oro", pesi: { world: 0.5, bond: 0.4, oro: 0.1 } },
];

const EROSIONI = [
  { v: 0.0050, label: "0,50% — ottimistico" },
  { v: 0.0075, label: "0,75% — realistico" },
  { v: 0.0100, label: "1,00% — pessimistico" },
];

const NOMI = {
  world: "MSCI World", acwi: "MSCI ACWI IMI", sp500: "S&P 500",
  nasdaq: "Nasdaq Composite", bond: "Treasury 10Y", oro: "Oro",
};

const C = { lump: "#d97706", pac: "#1e3a8a", mute: "#64748b", bad: "#e11d48", ok: "#059669" };

// ---------------------------------------------------------------- motore
/** Rata di un prestito amortizing. Il TAEG e' un tasso annuo EFFETTIVO,
 *  quindi il tasso mensile equivalente e' la radice dodicesima, non TAEG/12. */
export function rataDaTaeg(capitale, taeg, mesi) {
  if (mesi <= 0) return 0;
  const i = Math.pow(1 + taeg, 1 / 12) - 1;
  if (i <= 1e-12) return capitale / mesi;
  return (capitale * i) / (1 - Math.pow(1 + i, -mesi));
}

/** Allinea i mattoni del portafoglio sul periodo in comune.
 *  Ritorna { chiavi, pesi, M (mesi x asset), inizio, fine }. */
function allinea(serie, pesi) {
  const chiavi = Object.keys(pesi).filter((k) => serie[k]);
  if (!chiavi.length) return null;
  const mese = (s) => { const [a, m] = s.split("-").map(Number); return a * 12 + (m - 1); };
  const inizio = Math.max(...chiavi.map((k) => mese(serie[k].inizio)));
  const fine = Math.min(...chiavi.map((k) => mese(serie[k].inizio) + serie[k].n - 1));
  const n = fine - inizio + 1;
  if (n < 24) return null;
  const M = chiavi.map((k) => {
    const off = inizio - mese(serie[k].inizio);
    return Float64Array.from(serie[k].r.slice(off, off + n));
  });
  const et = (x) => `${Math.floor(x / 12)}-${String((x % 12) + 1).padStart(2, "0")}`;
  return { chiavi, pesi: chiavi.map((k) => pesi[k]), M, n, inizio: et(inizio), fine: et(fine) };
}

/** Esito di una singola traiettoria di `mesi` mesi, buy & hold senza
 *  ribilanciamento: ogni tranche versata compra i pesi obiettivo e poi resta.
 *    lump = P * Somma_i w_i * prod_t (1+r_it)
 *    pac  = R * Somma_i w_i * Somma_m prod_{t>=m} (1+r_it)
 */
function esito(M, pesi, da, mesi, erosioneMensile) {
  const A = M.length;
  let lumpMult = 0, pacFattore = 0;
  const cresciteFinali = new Array(A);
  for (let a = 0; a < A; a++) {
    const r = M[a];
    // cum[m] = prodotto dei fattori da m fino a mesi-1, calcolato a ritroso
    let acc = 1, somma = 0;
    for (let m = mesi - 1; m >= 0; m--) {
      acc *= (1 + r[da + m]) * erosioneMensile;
      somma += acc;                 // acc = cum[m]
    }
    cresciteFinali[a] = acc;        // crescita totale dell'asset sulla finestra
    lumpMult += pesi[a] * acc;
    pacFattore += pesi[a] * somma;
  }
  return { lumpMult, pacFattore, cresciteFinali };
}

const netto = (V, base) => (V > base ? base + (V - base) * (1 - ALIQUOTA) : V);

/** PRNG con seme: lo strumento deve dare lo stesso risultato a parita' di input. */
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Bootstrap a blocchi, CONGIUNTO fra asset: si ricampionano blocchi di mesi
 *  consecutivi prendendo la stessa finestra temporale per tutte le asset class,
 *  altrimenti si distrugge la correlazione che giustifica un 60/40. */
function bootstrap(M, pesi, mesi, erosioneMensile, nPercorsi, blocco, seed) {
  const N = M[0].length, A = M.length;
  const rnd = mulberry32(seed);
  const lump = new Float64Array(nPercorsi), pac = new Float64Array(nPercorsi);
  const idx = new Int32Array(mesi);
  const sim = Array.from({ length: A }, () => new Float64Array(mesi));
  for (let p = 0; p < nPercorsi; p++) {
    let m = 0;
    while (m < mesi) {
      const start = Math.floor(rnd() * N);
      const len = Math.min(blocco, mesi - m);
      for (let k = 0; k < len; k++) idx[m + k] = (start + k) % N;   // avvolgimento
      m += len;
    }
    for (let a = 0; a < A; a++) for (let t = 0; t < mesi; t++) sim[a][t] = M[a][idx[t]];
    const e = esito(sim, pesi, 0, mesi, erosioneMensile);
    lump[p] = e.lumpMult; pac[p] = e.pacFattore;
  }
  return { lump, pac };
}

const minimo = (a) => { let m = Infinity; for (let i = 0; i < a.length; i++) if (a[i] < m) m = a[i]; return m; };
const massimo = (a) => { let m = -Infinity; for (let i = 0; i < a.length; i++) if (a[i] > m) m = a[i]; return m; };

const perc = (arr, q) => {
  const s = Float64Array.from(arr).sort();
  const i = (s.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? s[lo] : s[lo] + (s[hi] - s[lo]) * (i - lo);
};

/** Metriche finali a partire dai moltiplicatori delle traiettorie. */
function metriche({ lumpMult, pacFat, P, R, mesi }) {
  const n = lumpMult.length, versato = R * mesi;
  const L = new Float64Array(n), Q = new Float64Array(n);
  let battePac = 0, inUtile = 0;
  for (let k = 0; k < n; k++) {
    L[k] = netto(P * lumpMult[k], P);
    Q[k] = netto(R * pacFat[k], versato);
    if (L[k] > Q[k]) battePac++;
    if (L[k] > versato) inUtile++;
  }
  return {
    n, versato, costo: versato - P,
    lumpMediana: perc(L, 0.5), pacMediana: perc(Q, 0.5),
    lumpP5: perc(L, 0.05), lumpMin: minimo(L),
    pacP5: perc(Q, 0.05),
    battePac: battePac / n, inUtile: inUtile / n, inPerdita: 1 - inUtile / n,
    L, Q,
  };
}

// ---------------------------------------------------------------- utilita' UI
const eur = (x) =>
  new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(x);
const eur2 = (x) =>
  new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR", minimumFractionDigits: 2 }).format(x);
const pct = (x) => `${(x * 100).toFixed(0)}%`;
const pct1 = (x) => `${(x * 100).toFixed(1).replace(".", ",")}%`;
const pct2 = (x) => `${(x * 100).toFixed(2).replace(".", ",")}%`;

function istogramma(L, Q, nBin = 26) {
  const lo = Math.min(minimo(L), minimo(Q));
  const hi = Math.max(massimo(L), massimo(Q));
  const w = (hi - lo) / nBin || 1;
  const bins = Array.from({ length: nBin }, (_, i) => ({
    x: lo + w * (i + 0.5), lump: 0, pac: 0,
  }));
  const metti = (arr, campo) => {
    for (const v of arr) {
      let i = Math.floor((v - lo) / w);
      if (i < 0) i = 0; if (i >= nBin) i = nBin - 1;
      bins[i][campo]++;
    }
  };
  metti(L, "lump"); metti(Q, "pac");
  const tot = L.length;
  return bins.map((b) => ({ ...b, lump: b.lump / tot, pac: b.pac / tot }));
}

/** La categoria piu' vicina a un valore, per poterci appoggiare una ReferenceLine. */
function categoriaVicina(bins, v) {
  let best = bins[0].x, d = Infinity;
  for (const b of bins) { const dd = Math.abs(b.x - v); if (dd < d) { d = dd; best = b.x; } }
  return best;
}

function Stat({ label, value, sub, color }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-0.5 text-xl font-bold tabular-nums" style={color ? { color } : undefined}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-slate-500">{sub}</div>}
    </div>
  );
}

// ---------------------------------------------------------------- componente
export default function PrestitoInvestimentoSimulator() {
  const [dati, setDati] = useState(null);
  const [errore, setErrore] = useState(null);

  const [importo, setImporto] = useState(20000);
  const [taeg, setTaeg] = useState(8);
  const [anni, setAnni] = useState(10);
  const [erosione, setErosione] = useState(0.0075);
  const [portafoglio, setPortafoglio] = useState("world");
  const [metodo, setMetodo] = useState("storiche");

  useEffect(() => {
    fetch(DATA_URL)
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setDati)
      .catch((e) => setErrore(String(e.message || e)));
  }, []);

  const pf = PORTAFOGLI.find((p) => p.id === portafoglio) ?? PORTAFOGLI[0];

  const allineato = useMemo(
    () => (dati ? allinea(dati.serie, pf.pesi) : null),
    [dati, pf]
  );

  // orizzonte massimo: servono almeno 24 finestre storiche per dire qualcosa
  const anniMax = useMemo(() => {
    if (!allineato) return 30;
    return Math.max(5, Math.min(30, Math.floor((allineato.n - 24) / 12)));
  }, [allineato]);

  useEffect(() => { if (anni > anniMax) setAnni(anniMax); }, [anniMax]);   // eslint-disable-line

  const ris = useMemo(() => {
    if (!allineato) return null;
    const mesi = anni * 12;
    if (mesi + 12 > allineato.n) return null;
    const eM = Math.pow(1 - erosione, 1 / 12);
    const R = rataDaTaeg(importo, taeg / 100, mesi);

    let lumpMult, pacFat, nTraiettorie, cresciteFinali;
    if (metodo === "storiche") {
      const N = allineato.n - mesi + 1;
      lumpMult = new Float64Array(N); pacFat = new Float64Array(N);
      for (let w = 0; w < N; w++) {
        const e = esito(allineato.M, allineato.pesi, w, mesi, eM);
        lumpMult[w] = e.lumpMult; pacFat[w] = e.pacFattore;
        if (w === N - 1) cresciteFinali = e.cresciteFinali;
      }
      nTraiettorie = N;
    } else {
      // seme deterministico: stessi input -> stesso risultato, sempre
      const seed = (importo | 0) * 7919 + Math.round(taeg * 100) * 104729 + mesi * 1299721
                 + Math.round(erosione * 1e4) * 15485863 + pf.id.length * 31;
      const b = bootstrap(allineato.M, allineato.pesi, mesi, eM, 10000, 24, seed);
      lumpMult = b.lump; pacFat = b.pac; nTraiettorie = 10000;
      cresciteFinali = esito(allineato.M, allineato.pesi, allineato.n - mesi, mesi, eM).cresciteFinali;
    }

    const m = metriche({ lumpMult, pacFat, P: importo, R, mesi });
    // pesi finali dopo la deriva (buy & hold non ribilanciato)
    const valFin = allineato.pesi.map((w, i) => w * cresciteFinali[i]);
    const somma = valFin.reduce((a, b) => a + b, 0);
    const derivati = allineato.chiavi.map((k, i) => ({ k, w0: allineato.pesi[i], w1: valFin[i] / somma }));
    return { ...m, R, mesi, nTraiettorie, derivati };
  }, [allineato, importo, taeg, anni, erosione, metodo, pf]);

  const histo = useMemo(() => (ris ? istogramma(ris.L, ris.Q) : null), [ris]);

  if (errore)
    return <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-800">
      Non riesco a caricare le serie storiche ({errore}). Ricarica la pagina.
    </p>;
  if (!dati) return <p className="text-sm text-slate-500">Carico le serie storiche…</p>;

  return (
    <div className="not-prose my-6 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:p-5">
      {/* ---------------- controlli ---------------- */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Importo erogato</span>
          <input type="number" min={1000} max={200000} step={1000} value={importo}
            onChange={(e) => setImporto(Math.max(1000, Number(e.target.value) || 0))}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 tabular-nums" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">TAEG annuo: {taeg.toFixed(2).replace(".", ",")}%</span>
          <input type="range" min={0} max={15} step={0.25} value={taeg}
            onChange={(e) => setTaeg(Number(e.target.value))} className="mt-2 w-full" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Orizzonte: {anni} anni</span>
          <input type="range" min={5} max={anniMax} step={1} value={anni}
            onChange={(e) => setAnni(Number(e.target.value))} className="mt-2 w-full" />
          <span className="text-xs text-slate-500">massimo {anniMax} anni con questo portafoglio</span>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Portafoglio</span>
          <select value={portafoglio} onChange={(e) => setPortafoglio(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
            {PORTAFOGLI.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Erosione annua dei costi</span>
          <select value={erosione} onChange={(e) => setErosione(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
            {EROSIONI.map((o) => <option key={o.v} value={o.v}>{o.label}</option>)}
          </select>
        </label>

        <div className="block">
          <span className="text-sm font-medium text-slate-700">Metodo</span>
          <div className="mt-1 flex rounded-lg border border-slate-300 bg-white p-1 text-sm">
            {[["storiche", "Finestre storiche"], ["bootstrap", "Bootstrap a blocchi"]].map(([v, l]) => (
              <button key={v} onClick={() => setMetodo(v)} type="button"
                className={`flex-1 rounded px-2 py-1.5 ${metodo === v ? "bg-slate-900 text-white" : "text-slate-600"}`}>
                {l}
              </button>
            ))}
          </div>
        </div>
      </div>

      {!ris && (
        <p className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          Con questo portafoglio e questo orizzonte i dati non bastano. Riduci l'orizzonte.
        </p>
      )}

      {ris && (
        <>
          {/* ---------------- il prestito ---------------- */}
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <Stat label="Rata mensile" value={eur2(ris.R)} sub={`per ${ris.mesi} mesi`} />
            <Stat label="Versato in totale" value={eur(ris.versato)}
                  sub={`su ${eur(importo)} ricevuti`} />
            <Stat label="Costo del prestito" value={eur(ris.costo)} color={C.bad}
                  sub={`${pct1(ris.costo / importo)} del capitale`} />
          </div>

          {/* ---------------- il confronto ---------------- */}
          <h4 className="mt-6 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Patrimonio finale, al netto del 26%
          </h4>
          <div className="mt-2 grid gap-3 sm:grid-cols-2">
            <Stat label="Prestito investito subito — mediana" value={eur(ris.lumpMediana)} color={C.lump} />
            <Stat label="PAC delle stesse rate — mediana" value={eur(ris.pacMediana)} color={C.pac} />
          </div>

          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <Stat label="Il prestito batte il PAC" value={pct(ris.battePac)}
                  color={ris.battePac >= 0.5 ? C.ok : C.bad}
                  sub={`su ${ris.nTraiettorie.toLocaleString("it-IT")} ${metodo === "storiche" ? "finestre storiche" : "percorsi simulati"}`} />
            <Stat label="Operazione chiusa in perdita" value={pct(ris.inPerdita)}
                  color={ris.inPerdita > 0.1 ? C.bad : C.mute}
                  sub="patrimonio finale sotto il totale versato" />
          </div>

          {metodo === "storiche" && ris.nTraiettorie < 60 && (
            <p className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
              Attenzione: su questo orizzonte il portafoglio scelto offre solo{" "}
              {ris.nTraiettorie} finestre storiche, e si sovrappongono quasi tutte.
              Non sono {ris.nTraiettorie} esperimenti indipendenti, è quasi una storia
              sola letta da punti di partenza vicini: leggi queste percentuali come un
              singolo scenario, non come una probabilità. Il bootstrap a blocchi, o un
              orizzonte più corto, dicono di più.
            </p>
          )}

          {/* ---------------- il rischio ---------------- */}
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <Stat label="5° percentile del prestito" value={eur(ris.lumpP5)}
                  sub={`contro ${eur(ris.versato)} versati`} />
            <Stat label="Traiettoria peggiore" value={eur(ris.lumpMin)} color={C.bad}
                  sub={`${pct1(ris.lumpMin / ris.versato - 1)} rispetto al versato`} />
          </div>

          {/* ---------------- distribuzione ---------------- */}
          <div className="mt-6" style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={histo} margin={{ top: 6, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="x" tick={{ fontSize: 11 }}
                       tickFormatter={(v) => `${Math.round(v / 1000)}k`} minTickGap={24} />
                <YAxis tick={{ fontSize: 11 }} width={44}
                       tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ fontSize: 12 }}
                  formatter={(v, n) => [`${(v * 100).toFixed(1)}%`, n === "lump" ? "Prestito" : "PAC"]}
                  labelFormatter={(v) => eur(v)} />
                <Legend wrapperStyle={{ fontSize: 12 }}
                  formatter={(v) => (v === "lump" ? "Prestito investito subito" : "PAC delle stesse rate")} />
                <ReferenceLine x={categoriaVicina(histo, ris.versato)} stroke={C.bad} strokeDasharray="4 3" />
                <Bar dataKey="lump" fill={C.lump} />
                <Bar dataKey="pac" fill={C.pac} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">
            Distribuzione dei patrimoni finali netti. La linea tratteggiata è il totale versato:
            a sinistra di quella linea l'operazione ha perso denaro.
          </p>

          {/* ---------------- deriva dei pesi ---------------- */}
          {ris.derivati.length > 1 && (
            <div className="mt-5 rounded-lg border border-slate-200 bg-white p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Pesi dopo la deriva, senza ribilanciamento
              </div>
              <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm">
                {ris.derivati.map((d) => (
                  <span key={d.k} className="tabular-nums text-slate-700">
                    {NOMI[d.k] ?? d.k}: <strong>{pct(d.w0)} → {pct(d.w1)}</strong>
                  </span>
                ))}
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Su un orizzonte lungo un portafoglio non ribilanciato diventa un altro portafoglio.
                È la finestra più recente disponibile.
              </p>
            </div>
          )}

          <p className="mt-4 text-xs text-slate-500">
            Dati: {NOMI[allineato.chiavi[0]] ?? allineato.chiavi[0]}
            {allineato.chiavi.length > 1 ? " e altre serie" : ""}, periodo in comune {allineato.inizio} – {allineato.fine},
            total return in euro al lordo dei costi, poi eroso di {pct2(erosione)} l'anno.
            {metodo === "bootstrap"
              ? " Bootstrap a blocchi di 24 mesi, ricampionamento congiunto fra le asset class, 10.000 percorsi, seme deterministico."
              : " Tutte le finestre mobili a passo mensile."}
          </p>
        </>
      )}
    </div>
  );
}
