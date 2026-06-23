/**
 * FireDecumuloSimulator.jsx
 *
 * Calcolatore interattivo del decumulo / indipendenza finanziaria per
 * il retail italiano. Personalizzabile con:
 *   - età corrente
 *   - età FIRE target (= età a cui smetto di lavorare)
 *   - età di morte assunta (default 80)
 *   - spesa annua attuale (€ reali di oggi)
 *   - tasso di prelievo netto target
 *   - scenario inflazione (2% o 3%)
 *
 * Output:
 *   - Anni di decumulo (= morte - FIRE) e anni di accumulo (= FIRE - oggi)
 *   - Quota plusvalenza stimata (in base agli anni di accumulo)
 *   - Tasso di prelievo lordo effettivo
 *   - Capitale richiesto al momento del FIRE (in € nominali)
 *   - Capitale richiesto oggi (in € reali, deflazionato)
 *   - Success rate netto Italia su 20, 30, 40 anni di decumulo
 *
 * I success rate sono pescati dalla tabella esportata in
 * public/charts/decumulo-fire-swr/summary.json (sezione fiscalita_italia).
 * Tutti gli scenari numerici provengono dal backtest reale sull'S&P 500
 * 1872-2022 con block bootstrap a 10.000 traiettorie.
 *
 * Autore: SmartMoneyLab — 2026.
 */

import { useState, useMemo } from "react";

// ------------------------------------------------------------------ //
// Tabelle dei risultati (estratte dal summary.json del backtest)     //
// ------------------------------------------------------------------ //

// Tasso di prelievo netto -> success rate per orizzonte, suddiviso
// per delay del FIRE (cioe' anni di accumulo prima dello smetto).
// Source: bootstrap a 10.000 traiettorie, S&P 500 reale 1872-2022,
// fiscalita' italiana 26% capital gain + bollo 0.2%/anno, quota
// plusvalenza dipendente dal delay.
const SUCCESS_NETTO = {
  0: {  // FIRE oggi col patrimonio attuale (cg 50%)
    2.5: { 20: 99.0, 30: 96.4, 40: 93.8 },
    3.0: { 20: 97.7, 30: 92.9, 40: 88.8 },
    3.5: { 20: 95.5, 30: 88.2, 40: 83.3 },
    4.0: { 20: 93.1, 30: 83.1, 40: 77.5 },
    4.5: { 20: 88.1, 30: 76.7, 40: 68.9 },
    5.0: { 20: 83.0, 30: 69.7, 40: 62.1 },
  },
  10: {  // FIRE dopo PAC decennale (cg 55%)
    2.5: { 20: 99.1, 30: 96.0, 40: 93.1 },
    3.0: { 20: 97.5, 30: 92.2, 40: 88.6 },
    3.5: { 20: 95.4, 30: 87.9, 40: 82.3 },
    4.0: { 20: 92.1, 30: 82.1, 40: 75.6 },
    4.5: { 20: 87.8, 30: 75.0, 40: 67.6 },
    5.0: { 20: 82.2, 30: 68.5, 40: 59.6 },
  },
  20: {  // FIRE dopo PAC ventennale (cg 65%)
    2.5: { 20: 98.7, 30: 95.9, 40: 93.4 },
    3.0: { 20: 97.5, 30: 92.4, 40: 87.4 },
    3.5: { 20: 94.7, 30: 86.4, 40: 82.2 },
    4.0: { 20: 91.6, 30: 80.6, 40: 75.4 },
    4.5: { 20: 86.2, 30: 73.3, 40: 65.5 },
    5.0: { 20: 81.0, 30: 65.7, 40: 58.3 },
  },
  25: {  // FIRE dopo PAC 25 anni (cg 70%)
    2.5: { 20: 98.8, 30: 95.5, 40: 92.4 },
    3.0: { 20: 97.0, 30: 91.5, 40: 87.0 },
    3.5: { 20: 94.4, 30: 86.7, 40: 80.5 },
    4.0: { 20: 90.3, 30: 80.1, 40: 73.2 },
    4.5: { 20: 85.9, 30: 72.0, 40: 64.7 },
    5.0: { 20: 79.9, 30: 64.5, 40: 57.0 },
  },
  30: {  // FIRE dopo PAC trentennale (cg 75%)
    2.5: { 20: 98.7, 30: 95.4, 40: 91.9 },
    3.0: { 20: 96.7, 30: 91.1, 40: 86.8 },
    3.5: { 20: 93.8, 30: 86.1, 40: 80.4 },
    4.0: { 20: 90.0, 30: 79.0, 40: 71.6 },
    4.5: { 20: 85.2, 30: 71.0, 40: 63.3 },
    5.0: { 20: 79.7, 30: 62.9, 40: 54.9 },
  },
};

// Per il lordo (modello base, no tasse). Indipendente dal delay.
const SUCCESS_LORDO = {
  2.5: { 20: 99.6, 30: 98.2, 40: 96.2 },
  3.0: { 20: 98.9, 30: 95.9, 40: 92.8 },
  3.5: { 20: 97.9, 30: 93.2, 40: 89.3 },
  4.0: { 20: 96.2, 30: 89.3, 40: 85.0 },
  4.5: { 20: 93.6, 30: 84.8, 40: 80.1 },
  5.0: { 20: 90.2, 30: 79.3, 40: 73.5 },
};

// Quota plusvalenza per anni di accumulo prima del FIRE.
const CG_PCT_BY_DELAY = { 0: 0.50, 10: 0.55, 20: 0.65, 25: 0.70, 30: 0.75 };

// ------------------------------------------------------------------ //
// Funzioni utili                                                     //
// ------------------------------------------------------------------ //

function interp(table, key) {
  const keys = Object.keys(table).map(Number).sort((a, b) => a - b);
  if (key <= keys[0]) return table[keys[0]];
  if (key >= keys[keys.length - 1]) return table[keys[keys.length - 1]];
  for (let i = 0; i < keys.length - 1; i++) {
    if (key >= keys[i] && key <= keys[i + 1]) {
      const frac = (key - keys[i]) / (keys[i + 1] - keys[i]);
      return table[keys[i]] + (table[keys[i + 1]] - table[keys[i]]) * frac;
    }
  }
  return table[keys[keys.length - 1]];
}

function cgPctForDelay(delay) {
  return interp(CG_PCT_BY_DELAY, delay);
}

function effectiveGrossWr(netWr, cgPct, taxRate = 0.26) {
  return netWr / (1 - taxRate * cgPct);
}

function lookupSuccess(table, wr, horizon) {
  // table è {2.5: {20: ..., 30: ..., 40: ...}, 3.0: {...}, ...}
  // wr arriva da slider, può essere fra i punti tabulati.
  const wrKeys = Object.keys(table).map(Number).sort((a, b) => a - b);
  const hKeys = [20, 30, 40];

  // Bound checks
  const clampedWr = Math.max(wrKeys[0], Math.min(wrKeys[wrKeys.length - 1], wr));
  const clampedH = Math.max(hKeys[0], Math.min(hKeys[hKeys.length - 1], horizon));

  // Find adjacent WR keys
  let wrLo = wrKeys[0], wrHi = wrKeys[wrKeys.length - 1];
  for (let i = 0; i < wrKeys.length - 1; i++) {
    if (clampedWr >= wrKeys[i] && clampedWr <= wrKeys[i + 1]) {
      wrLo = wrKeys[i];
      wrHi = wrKeys[i + 1];
      break;
    }
  }
  const wrFrac = wrHi === wrLo ? 0 : (clampedWr - wrLo) / (wrHi - wrLo);

  // Find adjacent horizon keys
  let hLo = hKeys[0], hHi = hKeys[hKeys.length - 1];
  for (let i = 0; i < hKeys.length - 1; i++) {
    if (clampedH >= hKeys[i] && clampedH <= hKeys[i + 1]) {
      hLo = hKeys[i];
      hHi = hKeys[i + 1];
      break;
    }
  }
  const hFrac = hHi === hLo ? 0 : (clampedH - hLo) / (hHi - hLo);

  // Bilinear interpolation
  const v00 = table[wrLo][hLo];
  const v01 = table[wrLo][hHi];
  const v10 = table[wrHi][hLo];
  const v11 = table[wrHi][hHi];
  const v0 = v00 + (v01 - v00) * hFrac;
  const v1 = v10 + (v11 - v10) * hFrac;
  return v0 + (v1 - v0) * wrFrac;
}

function lookupSuccessNetto(delay, wr, horizon) {
  const tables = SUCCESS_NETTO;
  const delayKeys = Object.keys(tables).map(Number).sort((a, b) => a - b);
  let dLo = delayKeys[0], dHi = delayKeys[delayKeys.length - 1];
  const clampedDelay = Math.max(dLo, Math.min(dHi, delay));
  for (let i = 0; i < delayKeys.length - 1; i++) {
    if (clampedDelay >= delayKeys[i] && clampedDelay <= delayKeys[i + 1]) {
      dLo = delayKeys[i];
      dHi = delayKeys[i + 1];
      break;
    }
  }
  const dFrac = dHi === dLo ? 0 : (clampedDelay - dLo) / (dHi - dLo);
  const sLo = lookupSuccess(tables[dLo], wr, horizon);
  const sHi = lookupSuccess(tables[dHi], wr, horizon);
  return sLo + (sHi - sLo) * dFrac;
}

function formatEur(v) {
  if (v >= 1_000_000) return `€ ${(v / 1_000_000).toFixed(2)}M`;
  if (v >= 1_000) return `€ ${(v / 1000).toFixed(0)}k`;
  return `€ ${v.toFixed(0)}`;
}

function colorForRate(rate) {
  if (rate >= 90) return "text-emerald-600 dark:text-emerald-400";
  if (rate >= 80) return "text-amber-600 dark:text-amber-400";
  if (rate >= 70) return "text-orange-600 dark:text-orange-400";
  return "text-red-600 dark:text-red-400";
}

// ------------------------------------------------------------------ //
// Componente                                                         //
// ------------------------------------------------------------------ //

export default function FireDecumuloSimulator() {
  const [ageNow, setAgeNow] = useState(35);
  const [ageFire, setAgeFire] = useState(55);
  const [ageDeath, setAgeDeath] = useState(80);
  const [spendAnnual, setSpendAnnual] = useState(30000);
  const [withdrawalNet, setWithdrawalNet] = useState(3.5);
  const [inflation, setInflation] = useState(2.0);

  const computed = useMemo(() => {
    const yearsAccum = Math.max(0, ageFire - ageNow);
    const yearsDecum = Math.max(1, ageDeath - ageFire);

    const cgPct = cgPctForDelay(yearsAccum);
    const wrNet = withdrawalNet / 100;
    const wrGross = effectiveGrossWr(wrNet, cgPct);

    const spendAtFireReal = spendAnnual; // costante in euro reali
    const spendAtFireNominal = spendAnnual * Math.pow(1 + inflation / 100, yearsAccum);

    const capitalRequiredNominal = spendAtFireNominal / wrNet;
    const capitalRequiredReal = spendAnnual / wrNet;

    const successNetto20 = lookupSuccessNetto(yearsAccum, withdrawalNet, 20);
    const successNetto30 = lookupSuccessNetto(yearsAccum, withdrawalNet, 30);
    const successNetto40 = lookupSuccessNetto(yearsAccum, withdrawalNet, 40);

    const successLordo20 = lookupSuccess(SUCCESS_LORDO, withdrawalNet, 20);
    const successLordo30 = lookupSuccess(SUCCESS_LORDO, withdrawalNet, 30);
    const successLordo40 = lookupSuccess(SUCCESS_LORDO, withdrawalNet, 40);

    const successNettoHorizon = lookupSuccessNetto(yearsAccum, withdrawalNet, yearsDecum);
    const successLordoHorizon = lookupSuccess(SUCCESS_LORDO, withdrawalNet, yearsDecum);

    return {
      yearsAccum, yearsDecum, cgPct, wrGross,
      spendAtFireNominal, capitalRequiredNominal, capitalRequiredReal,
      successNetto20, successNetto30, successNetto40,
      successLordo20, successLordo30, successLordo40,
      successNettoHorizon, successLordoHorizon,
    };
  }, [ageNow, ageFire, ageDeath, spendAnnual, withdrawalNet, inflation]);

  return (
    <div className="not-prose my-8 rounded-2xl border border-slate-200 bg-slate-50 p-6 dark:border-slate-700 dark:bg-slate-900">
      <h3 className="mb-1 text-xl font-bold text-slate-900 dark:text-slate-100">
        Calcolatore: quanto capitale serve per smettere di lavorare?
      </h3>
      <p className="mb-6 text-sm text-slate-600 dark:text-slate-400">
        Personalizza i parametri sotto. I numeri sono pescati dal backtest sull'S&amp;P 500
        1872-2022 con simulazione Monte Carlo a 10.000 traiettorie. La fiscalità italiana
        (26% sui capital gain + bollo 0,2% annuo) è incorporata.
      </p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* INPUT */}
        <div className="space-y-4">
          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Età attuale</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{ageNow} anni</span>
            </label>
            <input type="range" min={20} max={70} step={1} value={ageNow}
              onChange={(e) => {
                const v = parseInt(e.target.value);
                setAgeNow(v);
                if (v > ageFire) setAgeFire(v);
              }}
              className="mt-1 w-full accent-blue-700" />
          </div>

          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Età FIRE target (smetto di lavorare)</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{ageFire} anni</span>
            </label>
            <input type="range" min={ageNow} max={75} step={1} value={ageFire}
              onChange={(e) => setAgeFire(parseInt(e.target.value))}
              className="mt-1 w-full accent-blue-700" />
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Anni di accumulo (PAC): <strong>{computed.yearsAccum}</strong> ·
              Anni di vita post-lavoro: <strong>{computed.yearsDecum}</strong>
            </div>
          </div>

          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Età di morte assunta</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{ageDeath} anni</span>
            </label>
            <input type="range" min={Math.max(70, ageFire + 5)} max={100} step={1} value={ageDeath}
              onChange={(e) => setAgeDeath(parseInt(e.target.value))}
              className="mt-1 w-full accent-blue-700" />
          </div>

          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Spesa annua oggi (€ reali)</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{formatEur(spendAnnual)}</span>
            </label>
            <input type="range" min={10000} max={120000} step={1000} value={spendAnnual}
              onChange={(e) => setSpendAnnual(parseInt(e.target.value))}
              className="mt-1 w-full accent-blue-700" />
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Equivalente mensile: € {(spendAnnual / 12).toFixed(0)}
            </div>
          </div>

          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Tasso di prelievo netto target</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{withdrawalNet.toFixed(1)}%</span>
            </label>
            <input type="range" min={2.5} max={5.0} step={0.1} value={withdrawalNet}
              onChange={(e) => setWithdrawalNet(parseFloat(e.target.value))}
              className="mt-1 w-full accent-blue-700" />
            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Quota plusvalenza stimata: <strong>{(computed.cgPct * 100).toFixed(0)}%</strong> ·
              Tasso lordo effettivo: <strong>{(computed.wrGross * 100).toFixed(2)}%</strong>
            </div>
          </div>

          <div>
            <label className="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-300">
              <span>Scenario inflazione annua</span>
              <span className="font-bold text-blue-700 dark:text-blue-400">{inflation.toFixed(1)}%</span>
            </label>
            <input type="range" min={1.0} max={4.0} step={0.1} value={inflation}
              onChange={(e) => setInflation(parseFloat(e.target.value))}
              className="mt-1 w-full accent-blue-700" />
          </div>
        </div>

        {/* OUTPUT */}
        <div className="space-y-4">
          <div className="rounded-xl bg-blue-900 p-5 text-white shadow-md">
            <div className="mb-1 text-xs uppercase tracking-wider opacity-80">
              Capitale richiesto al momento del FIRE
            </div>
            <div className="text-3xl font-bold">{formatEur(computed.capitalRequiredNominal)}</div>
            <div className="mt-1 text-sm opacity-90">
              in euro nominali nel {new Date().getFullYear() + computed.yearsAccum}
            </div>
            {computed.yearsAccum > 0 && (
              <div className="mt-3 text-xs opacity-80">
                Equivalente in euro di oggi:{" "}
                <strong>{formatEur(computed.capitalRequiredReal)}</strong> ·
                Spesa annua nominale al FIRE:{" "}
                <strong>{formatEur(computed.spendAtFireNominal)}</strong>
              </div>
            )}
          </div>

          <div className="rounded-xl bg-white p-5 shadow-sm dark:bg-slate-800">
            <div className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">
              Probabilità di successo netto Italia
            </div>
            <div className="space-y-3">
              <ScenarioRow label={`${computed.yearsDecum} anni (il tuo scenario)`}
                netto={computed.successNettoHorizon}
                lordo={computed.successLordoHorizon}
                highlight={true} />
              <ScenarioRow label="20 anni"
                netto={computed.successNetto20}
                lordo={computed.successLordo20} />
              <ScenarioRow label="30 anni"
                netto={computed.successNetto30}
                lordo={computed.successLordo30} />
              <ScenarioRow label="40 anni"
                netto={computed.successNetto40}
                lordo={computed.successLordo40} />
            </div>
          </div>

          <div className="rounded-xl bg-amber-50 p-4 text-xs text-amber-900 dark:bg-amber-950 dark:text-amber-200">
            <strong>Come leggere:</strong> Il "netto Italia" include la tassa del
            26% sui capital gain e il bollo 0,2% annuo. Il "lordo" è il modello base
            usato dalla letteratura americana (Trinity Study). Il giallo segnala
            scenari sopra il 80% di successo, il verde sopra il 90%.
          </div>
        </div>
      </div>
    </div>
  );
}

function ScenarioRow({ label, netto, lordo, highlight }) {
  const colorNetto = colorForRate(netto);
  const colorLordo = colorForRate(lordo);
  return (
    <div className={`flex items-center justify-between rounded-lg px-3 py-2 ${
      highlight ? "bg-blue-50 dark:bg-blue-950" : ""
    }`}>
      <span className={`text-sm ${highlight ? "font-semibold" : ""} text-slate-700 dark:text-slate-300`}>
        {label}
      </span>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-500 dark:text-slate-400">
          lordo <strong className={colorLordo}>{lordo.toFixed(0)}%</strong>
        </span>
        <span className="text-slate-700 dark:text-slate-300">
          netto Italia <strong className={`text-base ${colorNetto}`}>{netto.toFixed(0)}%</strong>
        </span>
      </div>
    </div>
  );
}
