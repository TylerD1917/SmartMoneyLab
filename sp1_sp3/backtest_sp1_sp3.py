"""
SP1 / SP3 vs S&P 500 — backtest a rebalancing annuale.
Da lanciare in LOCALE (yfinance ha bisogno di rete verso Yahoo, bloccata nel sandbox Cowork).

    pip install yfinance pandas numpy matplotlib
    python backtest_sp1_sp3.py

Logica:
- Ogni 1 gennaio (primo giorno di borsa) leggo dal ranking chi era #1 (SP1) e #1-#3 (SP3, equal weight).
- Tengo per l'anno, poi ribilancio. Total return = Adj Close (auto_adjust=True), quindi dividendi reinvestiti.
- Baseline lorda (no costi, no tasse) coerente con la metodologia SmartMoneyLab.
"""
import pandas as pd, numpy as np, yfinance as yf
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).parent
RANK = pd.read_csv(HERE / "ranking_megacap_usa.csv")

START_YEAR = 1990      # alza a 2005 per evitare le zone "confidence media" e i buchi storici
END_YEAR   = 2025
BENCH      = "SPY"      # oppure "^SP500TR" (indice total return, storia piu' breve su Yahoo)

# --- ticker necessari ---
cols = ["ticker1", "ticker2", "ticker3"]
tickers = sorted(set(RANK.loc[(RANK.year>=START_YEAR)&(RANK.year<=END_YEAR), cols]
                     .stack().dropna().unique().tolist() + [BENCH]))
print("Scarico:", tickers)

px = yf.download(tickers, start=f"{START_YEAR-1}-06-01",
                 end=f"{END_YEAR+1}-01-15", auto_adjust=True, progress=False)["Close"]
px = px.sort_index().ffill()

# --- copertura dati: fin dove indietro arriva ogni serie ---
print("\nCopertura per ticker:")
for t in tickers:
    s = px[t].dropna()
    print(f"  {t:6s} {s.index[0].date()} -> {s.index[-1].date()}")

def first_trading_day(year):
    idx = px.index[(px.index >= f"{year}-01-01") & (px.index < f"{year}-02-01")]
    return idx[0] if len(idx) else None

def yearly_return(ticker, y0, y1):
    if ticker not in px or pd.isna(px[ticker].get(y0)) or pd.isna(px[ticker].get(y1)):
        return None
    return px[ticker].loc[y1] / px[ticker].loc[y0] - 1

rows = []
for year in range(START_YEAR, END_YEAR + 1):
    d0, d1 = first_trading_day(year), first_trading_day(year + 1)
    if d0 is None or d1 is None:
        continue
    r = RANK[RANK.year == year].iloc[0]
    sp1_t = [r.ticker1]
    sp3_t = [r.ticker1, r.ticker2, r.ticker3]
    sp1 = np.nanmean([yr for t in sp1_t if (yr:=yearly_return(t, d0, d1)) is not None])
    sp3 = np.nanmean([yr for t in sp3_t if (yr:=yearly_return(t, d0, d1)) is not None])
    bmk = yearly_return(BENCH, d0, d1)
    rows.append(dict(year=year, SP1=sp1, SP3=sp3, BENCH=bmk,
                     holdings=";".join(sp3_t)))

res = pd.DataFrame(rows).set_index("year")
print("\nRendimenti annui:\n", res.round(3))

def stats(series):
    g = (1 + series).prod()
    n = series.notna().sum()
    cagr = g ** (1 / n) - 1
    vol = series.std()
    cum = (1 + series).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    return dict(CAGR=cagr, Vol=vol, MaxDD=dd, Multiplo=g)

print("\nStatistiche (", START_YEAR, "-", END_YEAR, "):")
for c in ["SP1", "SP3", "BENCH"]:
    s = stats(res[c].dropna())
    print(f"  {c:5s} CAGR {s['CAGR']*100:5.1f}%  Vol {s['Vol']*100:5.1f}%  "
          f"MaxDD {s['MaxDD']*100:6.1f}%  x{s['Multiplo']:.1f}")

# --- grafico equity (log) ---
eq = (1 + res[["SP1", "SP3", "BENCH"]]).cumprod()
eq.plot(logy=True, figsize=(10, 6))
plt.title(f"SP1 / SP3 vs S&P 500 ({START_YEAR}-{END_YEAR}) — total return, rebal. annuale")
plt.ylabel("Crescita di 1$ (scala log)"); plt.grid(True, alpha=.3)
plt.tight_layout(); plt.savefig(HERE / "equity_sp1_sp3.png", dpi=130)
print("\nGrafico salvato: equity_sp1_sp3.png")
