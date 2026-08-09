"""Grafici articolo CAPE internazionale. Output PNG in public/charts/cape-internazionale-predice-rendimenti/"""
import pandas as pd, numpy as np, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
PROC=os.path.join(ROOT,"data","processed")
OUT=os.path.join(ROOT,"public","charts","cape-internazionale-predice-rendimenti")
os.makedirs(OUT,exist_ok=True)

NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.edgecolor":"#cbd5e1","axes.linewidth":1,
    "axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":170,"savefig.bbox":"tight",
    "axes.spines.top":False,"axes.spines.right":False})

ds=pd.read_csv(os.path.join(PROC,"cape_forward_dataset.csv"))
POOLED=["Japan","Germany","France","Switzerland","Australia","Canada","Italy","Spain",
        "Netherlands","Denmark","Finland","Norway","Sweden","Belgium","Austria","Brazil",
        "China","India","South Africa","South Korea","Taiwan","Indonesia","Thailand","US Large"]
d=ds[ds.market.isin(POOLED)].copy()
d["cape_rel"]=d.cape/d.groupby("market").cape.transform("median")

# ---- Chart 1: assoluto vs relativo (2 pannelli, fwd10 mediana) ----
fig,ax=plt.subplots(1,2,figsize=(11,4.6),sharey=True)
b2=[0,10,15,20,25,30,40,999]; l2=["<10","10-15","15-20","20-25","25-30","30-40",">40"]
d["ab"]=pd.cut(d.cape,bins=b2,labels=l2)
m1=d.dropna(subset=["fwd10_ann"]).groupby("ab",observed=True).fwd10_ann.median()*100
ax[0].bar(range(len(m1)),m1.values,color=GREY)
ax[0].set_xticks(range(len(m1))); ax[0].set_xticklabels(m1.index,rotation=45,ha="right",fontsize=9)
ax[0].set_title("CAPE assoluto\n(confronto tra paesi)",fontsize=12,weight="bold")
ax[0].set_ylabel("Rendimento forward 10 anni (mediana, ann.)")
ax[0].yaxis.set_major_formatter(PercentFormatter())
bins=[0,0.7,0.85,1.0,1.15,1.3,9]; labs=["<0.70","0.70-\n0.85","0.85-\n1.00","1.00-\n1.15","1.15-\n1.30",">1.30"]
d["rb"]=pd.cut(d.cape_rel,bins=bins,labels=labs)
m2=d.dropna(subset=["fwd10_ann"]).groupby("rb",observed=True).fwd10_ann.median()*100
cols=[NAVY]*len(m2); cols[0]=GOLD
ax[1].bar(range(len(m2)),m2.values,color=cols)
ax[1].set_xticks(range(len(m2))); ax[1].set_xticklabels(m2.index,fontsize=9)
ax[1].set_title("CAPE vs la PROPRIA mediana storica\n(confronto col proprio passato)",fontsize=12,weight="bold")
ax[1].yaxis.set_major_formatter(PercentFormatter())
fig.suptitle("Lo stesso indicatore, due usi opposti — solo uno funziona",fontsize=13,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_assoluto_vs_relativo.png")); plt.close(fig)

# ---- Chart 2: bucket relativo 5y e 10y affiancati ----
fig,ax=plt.subplots(figsize=(9.5,5))
labs2=["<0.70\nmolto\neconomico","0.70-\n0.85","0.85-\n1.00","1.00-\n1.15","1.15-\n1.30",">1.30\nmolto\ncaro"]
d["rb2"]=pd.cut(d.cape_rel,bins=bins,labels=labs2)
g5=d.dropna(subset=["fwd5_ann"]).groupby("rb2",observed=True).fwd5_ann.median()*100
g10=d.dropna(subset=["fwd10_ann"]).groupby("rb2",observed=True).fwd10_ann.median()*100
x=np.arange(len(labs2)); wdt=0.4
ax.bar(x-wdt/2,g5.reindex(labs2).values,wdt,label="Forward 5 anni",color=GOLD)
ax.bar(x+wdt/2,g10.reindex(labs2).values,wdt,label="Forward 10 anni",color=NAVY)
ax.set_xticks(x); ax.set_xticklabels(labs2,fontsize=9)
ax.set_ylabel("Rendimento annualizzato (mediana)"); ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_title("Più un mercato è economico rispetto alla sua storia,\npiù rende nei 5–10 anni successivi",fontsize=13,weight="bold")
ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_bucket_relativo.png")); plt.close(fig)

# ---- Chart 3: R2 per paese ----
rows=[]
for mk in POOLED:
    dd=ds[ds.market==mk][["cape","fwd10_ann"]].dropna()
    if len(dd)>=18:
        r=np.corrcoef(dd.cape,dd.fwd10_ann)[0,1]; rows.append((mk,r*r))
rows.sort(key=lambda x:x[1])
fig,ax=plt.subplots(figsize=(8,7.5))
names=[r[0] for r in rows]; vals=[r[1] for r in rows]
cols=[GOLD if v>=0.3 else NAVY for v in vals]
ax.barh(range(len(names)),vals,color=cols)
ax.set_yticks(range(len(names))); ax.set_yticklabels(names,fontsize=10)
ax.set_xlabel("R²  (fwd 10 anni spiegato dal CAPE del paese)")
ax.set_title("Il CAPE predice molto in alcuni mercati, nulla in altri\n(nessuna regola universale)",fontsize=12,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_r2_per_paese.png")); plt.close(fig)

# ---- Chart 4: relativo vs USA bucket ----
b=ds[ds.market=="US Large"].set_index("date"); bf10=b.fwd10_ann.to_dict(); bc=b.cape.to_dict()
dr=ds[ds.market.isin([m for m in POOLED if m!="US Large"])].copy()
dr["diff"]=dr.cape-dr.date.map(bc)
dr["diff_dev"]=dr["diff"]-dr.groupby("market")["diff"].transform("median")
dr["rel10"]=dr.fwd10_ann-dr.date.map(bf10)
dr=dr.dropna(subset=["rel10","diff_dev"])
dr["q"]=pd.qcut(dr["diff_dev"].rank(method="first"),5,labels=["molto più\neconomico\nvs USA","2","3\ntipico","4","molto più\ncaro\nvs USA"])
gg=dr.groupby("q",observed=True).rel10.median()*100
fig,ax=plt.subplots(figsize=(8.5,5))
cols=[GOLD]+[GREY]*4
ax.bar(range(len(gg)),gg.reindex(dr["q"].cat.categories).values,color=cols)
ax.axhline(0,color=INK,lw=1)
ax.set_xticks(range(len(gg))); ax.set_xticklabels(dr["q"].cat.categories,fontsize=9)
ax.set_ylabel("Rendimento RELATIVO vs USA (mediana, pp/anno)")
ax.set_title("Giocare un paese contro gli USA sul CAPE relativo?\nQuasi tutto perde vs USA, tranne il tail estremo (n piccolo)",fontsize=12,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"04_relativo_vs_usa.png")); plt.close(fig)

# ---- Chart 5: portafoglio vs ACWI ----
fig,ax=plt.subplots(figsize=(9.5,5))
for step,c,lab in [(30,NAVY,"Value relativo — ribil. 2.5 anni"),(60,GOLD,"Value relativo — ribil. 5 anni")]:
    e=pd.read_csv(os.path.join(PROC,f"port_equity_{step}m.csv"),index_col=0)
    ax.plot(range(len(e)),e["portfolio"].values,color=c,lw=2,label=lab)
    acwi=e["acwi"].values
ax.plot(range(len(acwi)),acwi,color=RED,lw=2.2,label="ACWI (indice globale)")
idx=pd.read_csv(os.path.join(PROC,"port_equity_30m.csv"),index_col=0).index
ticks=range(0,len(idx),36)
ax.set_xticks(list(ticks)); ax.set_xticklabels([idx[i][:4] for i in ticks])
ax.set_ylabel("Crescita di 1$ (lordo, USD)")
ax.set_title("Comprare i mercati più economici vs la loro storia\nNON batte un semplice indice globale",fontsize=13,weight="bold")
ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(OUT,"05_portafoglio_vs_acwi.png")); plt.close(fig)

print("Grafici salvati in", OUT)
print(os.listdir(OUT))
