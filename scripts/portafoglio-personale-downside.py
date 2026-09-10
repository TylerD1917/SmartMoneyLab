"""
Analisi del rischio di coda del portafoglio (revisione 2026).
Legge monthly_returns.csv prodotto dal backtest (Portafoglio + 3 benchmark).

Risponde alla domanda: la diversificazione limita davvero lo scenario PEGGIORE
rispetto ai benchmark? Per ogni finestra mobile di 5 e 10 anni calcola:
  - il rendimento annualizzato della finestra PEGGIORE (worst case),
  - il 5° percentile (p5) dei rendimenti annualizzati,
  - la mediana,
  - il max drawdown peggiore vissuto DENTRO una finestra.

Output: public/charts/portafoglio-personale-backtest/07_worst_windows.png
        + aggiorna la sezione 'downside' in summary.json
"""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "public", "charts", "portafoglio-personale-backtest")
NAVY = "#1e3a8a"; GOLD = "#f59e0b"; GREY = "#94a3b8"; GREEN = "#059669"; INK = "#0f172a"
plt.rcParams.update({"font.size": 12, "axes.grid": True, "grid.color": "#e2e8f0",
    "figure.dpi": 160, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False})

def it(x, d=1): return f"{x:.{d}f}".replace(".", ",")

df = pd.read_csv(os.path.join(OUT, "monthly_returns.csv"), index_col=0, parse_dates=True)
cols = list(df.columns)                 # ["Portafoglio","S&P 500 TR","MSCI World TR","MSCI ACWI IMI TR"]
COLORMAP = {cols[0]: NAVY, cols[1]: GOLD, cols[2]: GREY, cols[3]: GREEN}

def roll_cagr(series, k):
    lp = np.log1p(series.values); out = []; idx = []
    for i in range(len(lp) - k + 1):
        out.append(np.expm1(lp[i:i + k].sum() * 12.0 / k)); idx.append(series.index[i])
    return pd.Series(out, index=idx)

def roll_maxdd(series, k):
    r = series.values; out = []
    for i in range(len(r) - k + 1):
        nav = np.cumprod(1 + r[i:i + k]); dd = (nav / np.maximum.accumulate(nav) - 1).min()
        out.append(dd)
    return np.array(out)

HOR = {"5 anni": 60, "10 anni": 120}
stats = {}
for lbl, k in HOR.items():
    stats[lbl] = {}
    for c in cols:
        rc = roll_cagr(df[c], k); dd = roll_maxdd(df[c], k)
        stats[lbl][c] = {"worst": float(rc.min()), "worst_start": rc.idxmin().strftime("%Y-%m"),
                         "p5": float(rc.quantile(0.05)), "median": float(rc.median()),
                         "worst_maxdd": float(dd.min()), "n": int(len(rc))}

# ---------------- grafico: CAGR della finestra peggiore, 5y e 10y, 4 serie
fig, axes = plt.subplots(1, 2, figsize=(11, 5.6), sharey=True)
for ax, (lbl, k) in zip(axes, HOR.items()):
    vals = [stats[lbl][c]["worst"] for c in cols]
    xs = np.arange(len(cols))
    bars = ax.bar(xs, [v * 100 for v in vals],
                  color=[COLORMAP[c] for c in cols], width=0.62, zorder=3)
    ax.axhline(0, color=INK, lw=1.1, zorder=4)
    for b, v in zip(bars, vals):
        va = "bottom" if v >= 0 else "top"
        off = 0.25 if v >= 0 else -0.25
        ax.text(b.get_x() + b.get_width() / 2, v * 100 + off, f"{it(v*100)}%",
                ha="center", va=va, fontsize=12, fontweight="bold",
                color=INK)
    ax.set_title(f"Finestre mobili di {lbl}", fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels(["Portafoglio", "S&P 500", "MSCI World", "MSCI ACWI"],
                                          rotation=18, ha="right", fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
axes[0].set_ylabel("Rendimento annualizzato\nnella finestra peggiore")
fig.suptitle("Lo scenario peggiore: quanto rende (all'anno) chi entra nel momento sbagliato",
             fontweight="bold", fontsize=14, y=1.02)
handles = [Patch(facecolor=COLORMAP[c], label=lbl2) for c, lbl2 in
           zip(cols, ["Portafoglio", "S&P 500 TR", "MSCI World TR", "MSCI ACWI IMI TR"])]
axes[1].legend(handles=handles, frameon=False, fontsize=9, loc="lower right")
fig.savefig(os.path.join(OUT, "07_worst_windows.png")); plt.close(fig)

# ---------------- aggiorna summary.json
sp = os.path.join(OUT, "summary.json")
summary = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
summary["downside"] = {lbl: {c: {k2: (round(v, 4) if isinstance(v, float) else v)
                                 for k2, v in stats[lbl][c].items()} for c in cols}
                       for lbl in HOR}
json.dump(summary, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("Downside OK")
for lbl in HOR:
    print(f"\n[{lbl}]  ({stats[lbl][cols[0]]['n']} finestre)")
    for c in cols:
        s = stats[lbl][c]
        print(f"  {c:<18} worst {s['worst']*100:>6.1f}% (da {s['worst_start']})  "
              f"p5 {s['p5']*100:>6.1f}%  mediana {s['median']*100:>5.1f}%  maxDD {s['worst_maxdd']*100:>6.1f}%")
