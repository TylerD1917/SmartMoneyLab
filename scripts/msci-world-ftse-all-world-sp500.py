"""
MSCI World vs FTSE All-World vs S&P 500 — confronto per l'articolo SEO.
Dati: returns_panel (MSCI gross TR USD mensile). Proxy: FTSE All-World≈MSCI ACWI, S&P 500≈MSCI USA.
Output: public/charts/msci-world-ftse-all-world-sp500/*.png + summary.json
"""
import os, math, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","msci-world-ftse-all-world-sp500"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

w=pd.read_csv(os.path.join(ROOT,"data","processed","returns_panel_wide.csv"))
M={"MSCI World":"Developed Markets Large","FTSE All-World":"ACWI","S&P 500":"US Large"}
sub=w[["month"]+list(M.values())].dropna().reset_index(drop=True)
DAYS=12
def cg(s): return (s[-1]/s[0])**(DAYS/(len(s)-1))-1
def mdd(s): return float((s/np.maximum.accumulate(s)-1).min())
lvl={k:sub[v].values for k,v in M.items()}
cols={"MSCI World":NAVY,"FTSE All-World":GOLD,"S&P 500":RED}

summary={"period":[sub.month.iloc[0],sub.month.iloc[-1]],"n_mesi":len(sub),"stats":{},"corr":{}}
for k,s in lvl.items():
    r=s[1:]/s[:-1]-1
    summary["stats"][k]={"cagr":cg(s),"vol":float(r.std()*math.sqrt(12)),"mdd":mdd(s),"mult":float(s[-1]/s[0])}
rets={k:lvl[k][1:]/lvl[k][:-1]-1 for k in lvl}
import itertools
for a,b in itertools.combinations(lvl,2):
    summary["corr"][f"{a} vs {b}"]=float(np.corrcoef(rets[a],rets[b])[0,1])
json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)
for k in lvl: s=summary["stats"][k]; print(f"{k:16s} CAGR {s['cagr']*100:.1f}%  vol {s['vol']*100:.1f}%  MDD {s['mdd']*100:.1f}%  10k->{10000*s['mult']:.0f}")

# 1) crescita di 10.000€
fig,ax=plt.subplots(figsize=(10,5.5)); x=pd.to_datetime(sub.month+"-01")
for k,s in lvl.items(): ax.plot(x,10000*s/s[0],color=cols[k],lw=2.2,label=k)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v/1000:.0f}k€"))
ax.set_ylabel("Valore di 10.000€ investiti"); ax.set_title("MSCI World, FTSE All-World e S&P 500 a confronto\n(2001-2026, in USD, dividendi reinvestiti)",fontsize=13,weight="bold")
ax.legend(fontsize=11); fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_crescita_10k.png")); plt.close(fig)

# 2) composizione (peso USA / altri sviluppati / emergenti) — dati attuali 2026 (fonti: MSCI, FTSE)
comp={"S&P 500":[100,0,0],"MSCI World":[72,28,0],"FTSE All-World":[62,28,10]}
labels=["USA","Altri mercati sviluppati","Mercati emergenti"]; cc=[NAVY,GREY,GOLD]
fig,ax=plt.subplots(figsize=(9,5)); names=list(comp); bottoms=[0,0,0]
for i,seg in enumerate(labels):
    vals=[comp[n][i] for n in names]
    ax.bar(names,vals,bottom=bottoms,label=seg,color=cc[i])
    bottoms=[bottoms[j]+vals[j] for j in range(len(names))]
ax.set_ylabel("Composizione (%)"); ax.set_ylim(0,100); ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_title("Sono più simili di quanto sembri: tutti dominati dagli USA\n(pesi approssimativi, 2026)",fontsize=12,weight="bold")
ax.legend(fontsize=10,loc="lower center",bbox_to_anchor=(0.5,-0.28),ncol=3)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_composizione.png")); plt.close(fig)

# 3) rolling 10y CAGR: chi ha vinto varia nel tempo
W=10*12; step=6; starts=list(range(0,len(sub)-W,step))
fig,ax=plt.subplots(figsize=(10,5.5))
for k,s in lvl.items():
    xs=[pd.to_datetime(sub.month.iloc[st]+"-01") for st in starts]
    ys=[cg(s[st:st+W+1])*100 for st in starts]
    ax.plot(xs,ys,color=cols[k],lw=2,label=k)
ax.yaxis.set_major_formatter(PercentFormatter()); ax.set_ylabel("Rendimento annuo dei 10 anni successivi")
ax.set_title("Il vincitore cambia: l'S&P 500 non ha sempre battuto il mondo\n(CAGR a 10 anni, per data di partenza)",fontsize=12,weight="bold")
ax.legend(fontsize=10); fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_rolling_10y.png")); plt.close(fig)
print("[ok] 3 grafici + summary.json in", OUT)
