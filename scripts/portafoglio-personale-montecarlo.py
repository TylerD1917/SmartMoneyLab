"""
Monte Carlo prospettico del portafoglio (revisione 2026).
Legge monthly_returns.csv prodotto dal backtest (Portafoglio + 3 benchmark).
Block bootstrap a blocchi di 3 mesi, CONGIUNTO sulle 4 colonne (stessi indici di
blocco) per preservare il co-movimento portafoglio/benchmark. 10.000 traiettorie,
orizzonti 10/20/30 anni, da 10.000 € iniziali. Riporta mediana/p5/p95 del NAV
finale del portafoglio e P(portafoglio > benchmark) a ciascun orizzonte.

Output: public/charts/portafoglio-personale-backtest/06_montecarlo.png
        + aggiorna la sezione 'montecarlo' in summary.json
"""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","portafoglio-personale-backtest")
NAVY="#1e3a8a"; GOLD="#f59e0b"; GREY="#94a3b8"; GREEN="#059669"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
def eur(v,_=None):
    return f"{v/1e6:.1f}M€" if abs(v)>=1e6 else (f"{v/1000:.0f}k€" if abs(v)>=1000 else f"{v:.0f}€")
def it(x,d=1): return f"{x:.{d}f}".replace(".",",")

df=pd.read_csv(os.path.join(OUT,"monthly_returns.csv"),index_col=0)
cols=list(df.columns)                      # ["Portafoglio","S&P 500 TR","MSCI World TR","MSCI ACWI IMI TR"]
data=df.values; T=len(data)
BLOCK=3; N_SIM=10000; CAP=10000.0; SEED=20260913
rng=np.random.default_rng(SEED)
HOR={"10 anni":120,"20 anni":240,"30 anni":360}

def sim_finals(months):
    nb=int(np.ceil(months/BLOCK)); finals=np.empty((N_SIM,len(cols)))
    for s in range(N_SIM):
        starts=rng.integers(0,T-BLOCK,size=nb)
        seq=np.vstack([data[i:i+BLOCK] for i in starts])[:months]   # (months,4) congiunto
        finals[s]=CAP*np.prod(1+seq,axis=0)
    return finals

res={}
for name,m in HOR.items():
    f=sim_finals(m); pf=f[:,0]
    row={"port_p5":float(np.percentile(pf,5)),"port_med":float(np.median(pf)),
         "port_p95":float(np.percentile(pf,95))}
    for j,c in enumerate(cols[1:],start=1):
        row[f"P(port>{c})"]=float((f[:,0]>f[:,j]).mean())
        row[f"{c}_med"]=float(np.median(f[:,j]))
    res[name]=row

# ---------------- grafico: mediana + range p5-p95 del portafoglio vs mediane benchmark
fig,ax=plt.subplots(figsize=(10,5.6))
x=np.arange(len(HOR)); names=list(HOR.keys())
med=[res[n]["port_med"] for n in names]; p5=[res[n]["port_p5"] for n in names]; p95=[res[n]["port_p95"] for n in names]
ax.bar(x,med,width=0.5,color=NAVY,label="Portafoglio (mediana)",zorder=2)
ax.errorbar(x,med,yerr=[np.array(med)-np.array(p5),np.array(p95)-np.array(med)],
            fmt="none",ecolor=INK,elinewidth=1.4,capsize=6,zorder=3,label="Range p5–p95")
for c,col,off in [("S&P 500 TR",GOLD,-0.16),("MSCI World TR",GREY,0.0),("MSCI ACWI IMI TR",GREEN,0.16)]:
    ax.scatter(x+off,[res[n][f"{c}_med"] for n in names],color=col,s=55,zorder=4,label=f"{c} (mediana)")
ax.set_yscale("log"); ax.yaxis.set_major_formatter(FuncFormatter(eur))
ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_title("Monte Carlo: valore finale di 10.000 € (10.000 traiettorie)",fontweight="bold")
ax.legend(frameon=False,fontsize=9,ncol=2)
fig.savefig(os.path.join(OUT,"06_montecarlo.png")); plt.close(fig)

# ---------------- aggiorna summary.json
sp=os.path.join(OUT,"summary.json")
summary=json.load(open(sp,encoding="utf-8")) if os.path.exists(sp) else {}
summary["montecarlo"]={"n_sim":N_SIM,"block_mesi":BLOCK,"cap":CAP,
    **{n:{k:(round(v,4) if k.startswith("P(") else round(v,0)) for k,v in res[n].items()} for n in res}}
json.dump(summary,open(sp,"w",encoding="utf-8"),ensure_ascii=False,indent=2)

print("Monte Carlo OK")
for n in names:
    r=res[n]
    print(f"  {n:8s} portafoglio med {r['port_med']:>10,.0f}  p5 {r['port_p5']:>9,.0f}  p95 {r['port_p95']:>11,.0f}  "
          f"| P>S&P {r['P(port>S&P 500 TR)']*100:.0f}%  P>World {r['P(port>MSCI World TR)']*100:.0f}%  P>ACWI {r['P(port>MSCI ACWI IMI TR)']*100:.0f}%")
