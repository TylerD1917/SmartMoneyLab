"""
SP1 / SP3 vs S&P 500 — versione con TASSAZIONE ITALIANA.
Da lanciare in LOCALE (yfinance).

    pip install yfinance pandas numpy matplotlib
    python backtest_sp1_sp3_tax.py

Regole fiscali modellate (Italia):
- Aliquota 26% su redditi finanziari.
- PLUSVALENZE DA PREZZO (azioni singole) = redditi diversi: tassate SOLO alla vendita
  (quindi ai ribilanciamenti annuali; le posizioni che restano NON vengono tassate -> differimento).
  Compensabili con lo "zainetto" minusvalenze pregresse, finestra = anno di realizzo + 4 successivi.
- DIVIDENDI = redditi di capitale: tassati 26% ogni anno alla percezione, NON compensabili con minus.
  Il netto viene reinvestito nella stessa posizione.
- BENCHMARK S&P 500 trattato come ETF armonizzato: dividendi 26%/anno (redditi di capitale),
  plusvalenza da prezzo tassata 26% alla liquidazione finale, NON compensabile con minus.
- A fine periodo si liquida tutto (si paga la tassa sul non realizzato) per confrontare la ricchezza netta.

Approssimazione dichiarata: nel rebalancing equal-weight di SP3, la tassa dell'anno viene dedotta
dalla ricchezza e i pesi target riscalati proporzionalmente (effetto di secondo ordine).
"""
import pandas as pd, numpy as np, yfinance as yf
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).parent
RANK = pd.read_csv(HERE / "ranking_megacap_usa.csv")

START_YEAR = 2005      # zona confidence alta; alza/abbassa a piacere
END_YEAR   = 2025
BENCH      = "SPY"
TAX        = 0.26
CARRY      = 4         # minus utilizzabili nell'anno di realizzo + 4 successivi

# ---------------------------------------------------------------- dati
cols = ["ticker1", "ticker2", "ticker3"]
tickers = sorted(set(RANK.loc[(RANK.year>=START_YEAR)&(RANK.year<=END_YEAR), cols]
                     .stack().dropna().unique().tolist() + [BENCH]))
print("Scarico (prezzo grezzo + dividendi):", tickers)

raw = yf.download(tickers, start=f"{START_YEAR-1}-06-01", end=f"{END_YEAR+1}-01-20",
                  auto_adjust=False, actions=True, progress=False)
close = raw["Close"].sort_index().ffill()
divs  = raw["Dividends"].sort_index().fillna(0.0)

def ftd(year):
    idx = close.index[(close.index >= f"{year}-01-01") & (close.index < f"{year}-02-01")]
    return idx[0] if len(idx) else None

# tabelle annuali: rendimento da prezzo P[year,tk] e dividend-yield DY[year,tk]
years = list(range(START_YEAR, END_YEAR + 1))
P  = pd.DataFrame(index=years, columns=tickers, dtype=float)
DY = pd.DataFrame(index=years, columns=tickers, dtype=float)
for y in years:
    d0, d1 = ftd(y), ftd(y + 1)
    if d0 is None or d1 is None:
        continue
    for t in tickers:
        c0, c1 = close[t].get(d0), close[t].get(d1)
        if pd.isna(c0) or pd.isna(c1):
            continue
        P.loc[y, t]  = c1 / c0 - 1
        DY.loc[y, t] = float(divs[t].loc[(divs.index >= d0) & (divs.index < d1)].sum()) / c0

print("\nCopertura dati:")
for t in tickers:
    s = close[t].dropna()
    print(f"  {t:6s} {s.index[0].date()} -> {s.index[-1].date()}")

# ---------------------------------------------------------------- motore fiscale
class MinusBucket:
    def __init__(self, carry): self.carry = carry; self.items = []  # [vintage, amount]
    def purge(self, y):        self.items = [x for x in self.items if x[0] >= y - self.carry]
    def offset(self, gain, y):
        """compensa una plusvalenza netta positiva con le minus disponibili; ritorna imponibile residuo"""
        self.purge(y)
        for it in sorted(self.items, key=lambda z: z[0]):
            if gain <= 0: break
            u = min(gain, it[1]); it[1] -= u; gain -= u
        self.items = [x for x in self.items if x[1] > 1e-12]
        return gain
    def add_loss(self, loss, y):
        if loss > 0: self.items.append([y, loss])

def simulate(holdings_by_year, offset_minus=True):
    """ritorna (equity netta, equity lorda, dettaglio annuale dict)"""
    port = {}          # tk -> {'val','basis'}
    bucket = MinusBucket(CARRY)
    wealth_net = 1.0
    gross = 1.0
    eqn, eqg, detail = [], [], []
    prev = None
    for i, y in enumerate(years):
        tgt = holdings_by_year[y]
        # allocazione iniziale
        if not port:
            for t in tgt: port[t] = {"val": wealth_net/len(tgt), "basis": wealth_net/len(tgt)}
        div_tax_y = 0.0
        # 1) crescita infra-annuale: prezzo + dividendo netto reinvestito
        for t, pos in port.items():
            p  = P.loc[y, t]; dy = DY.loc[y, t]
            if pd.isna(p): p = 0.0
            if pd.isna(dy): dy = 0.0
            div_cash = pos["val"] * dy
            dtax     = div_cash * TAX
            div_tax_y += dtax
            pos["val"]   = pos["val"] * (1 + p) + div_cash - dtax
            pos["basis"] += div_cash - dtax
        # gross: total return equal weight
        gr = np.nanmean([ (P.loc[y,t] if not pd.isna(P.loc[y,t]) else 0)
                         +(DY.loc[y,t] if not pd.isna(DY.loc[y,t]) else 0) for t in tgt])
        gross *= (1 + gr)
        # 2) ribilanciamento verso l'anno successivo (o liquidazione all'ultimo anno)
        V = sum(p["val"] for p in port.values())
        final = (i == len(years) - 1)
        nxt = None if final else holdings_by_year[years[i+1]]
        realized = 0.0
        if final:
            for t, pos in port.items():
                realized += pos["val"] - pos["basis"]     # liquido tutto
        else:
            tv = V / len(nxt)
            newport = {}
            for t, pos in port.items():
                if t not in nxt:                           # esco: vendo tutto
                    realized += pos["val"] - pos["basis"]
                elif pos["val"] > tv:                      # alleggerisco
                    fs = (pos["val"] - tv) / pos["val"]
                    realized += (pos["val"] - pos["basis"]) * fs
                    newport[t] = {"val": tv, "basis": pos["basis"] * (1 - fs)}
                else:                                      # mantengo (rimpolpo dopo)
                    newport[t] = {"val": pos["val"], "basis": pos["basis"]}
            for t in nxt:                                  # entro / rimpolpo
                if t not in newport:
                    newport[t] = {"val": tv, "basis": tv}
                elif newport[t]["val"] < tv:
                    add = tv - newport[t]["val"]
                    newport[t]["val"] += add; newport[t]["basis"] += add
        # 3) imposta su plusvalenze da prezzo (redditi diversi)
        if realized >= 0:
            taxable = bucket.offset(realized, y) if offset_minus else realized
            gain_tax = taxable * TAX
        else:
            gain_tax = 0.0
            bucket.add_loss(-realized, y)
        # 4) aggiorno ricchezza: tolgo la tassa sulle plus dalla ricchezza e riscalo i pesi
        tax_tot = gain_tax                # i dividendi sono gia' stati tolti sopra
        Vpost = V - tax_tot
        if not final:
            k = Vpost / V if V > 0 else 1.0
            for t in newport:
                newport[t]["val"] *= k; newport[t]["basis"] *= k
            port = newport
        wealth_net = Vpost
        eqn.append(Vpost); eqg.append(gross)
        detail.append(dict(anno=y, div_tax=div_tax_y, plus_realizz=realized,
                           tax_plus=gain_tax, ricchezza_netta=Vpost, lordo=gross))
    return (pd.Series(eqn, index=years, name="net"),
            pd.Series(eqg, index=years, name="gross"),
            pd.DataFrame(detail).set_index("anno"))

def holdings(kind):
    h = {}
    for y in years:
        r = RANK[RANK.year == y].iloc[0]
        h[y] = [r.ticker1] if kind == "SP1" else [r.ticker1, r.ticker2, r.ticker3]
    return h

def bench_etf():
    """ETF: 1 posizione BENCH held-to-end; dividendi 26%/anno; plus finale 26% no compensazione"""
    val = basis = 1.0; gross = 1.0; eqn = []
    for i, y in enumerate(years):
        p  = P.loc[y, BENCH]; dy = DY.loc[y, BENCH]
        p  = 0.0 if pd.isna(p) else p; dy = 0.0 if pd.isna(dy) else dy
        div_cash = val * dy; dtax = div_cash * TAX
        val   = val * (1 + p) + div_cash - dtax
        basis += div_cash - dtax
        gross *= (1 + p + dy)
        if i == len(years) - 1:
            gain = max(val - basis, 0.0); val -= gain * TAX     # plus ETF, no minus
        eqn.append(val)
    return pd.Series(eqn, index=years, name="net"), pd.Series([gross]*len(years), index=years)

# ---------------------------------------------------------------- run
sp1_n, sp1_g, sp1_d = simulate(holdings("SP1"))
sp3_n, sp3_g, sp3_d = simulate(holdings("SP3"))
b_n, b_g            = bench_etf()

def cagr(series_end, n): return series_end ** (1/n) - 1
n = len(years)
def line(name, net, gross):
    cn = cagr(net.iloc[-1], n); cg = cagr(gross.iloc[-1], n)
    drag = (cg - cn) * 10000
    print(f"  {name:6s} lordo {cg*100:5.1f}%  netto {cn*100:5.1f}%  "
          f"tax drag {drag:4.0f} bps/anno  |  x{net.iloc[-1]:.1f} netto")

print(f"\n=== SP1 / SP3 vs S&P500 — {START_YEAR}-{END_YEAR}, CAGR ===")
line("SP1", sp1_n, sp1_g)
line("SP3", sp3_n, sp3_g)
line("SPX", b_n, b_g)

print("\nDettaglio annuale SP1 (tasse pagate):")
print(sp1_d[["div_tax","plus_realizz","tax_plus","ricchezza_netta"]].round(3))

eq = pd.DataFrame({"SP1 netto": sp1_n, "SP3 netto": sp3_n, "S&P500 netto": b_n})
eq.plot(logy=True, figsize=(10,6))
plt.title(f"SP1/SP3 vs S&P500 — NETTO tasse italiane ({START_YEAR}-{END_YEAR})")
plt.ylabel("Crescita di 1€ (log)"); plt.grid(True, alpha=.3); plt.tight_layout()
plt.savefig(HERE / "equity_sp1_sp3_netto.png", dpi=130)
print("\nGrafico salvato: equity_sp1_sp3_netto.png")
