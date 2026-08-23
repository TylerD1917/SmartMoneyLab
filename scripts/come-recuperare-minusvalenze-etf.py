"""
Come recuperare le minusvalenze da ETF — grafici per l'articolo SEO.
Caso concreto: minusvalenza da recuperare 900,22€ (broker Fineco).
Strumenti compensabili reali (ETC su materie prime), rendimento YTD 2026 preciso
dal 31/12/2025 all'ultimo dato disponibile (fonte: serie prezzi spot in data/cache).
Output: public/charts/come-recuperare-minusvalenze-etf/*.png
"""
import os, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","come-recuperare-minusvalenze-etf"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

MINUS=900.22
def ytd(path):
    d=pd.read_csv(path); d.columns=["date","v"]; d["date"]=pd.to_datetime(d["date"]); d=d.sort_values("date")
    base=d[d.date<="2025-12-31"].v.iloc[-1]; last=d.iloc[-1]
    return last.v/base-1, last.date.date()
series={"Rame (ETC)":"data/cache/corr_copper.csv","Oro (ETC)":"data/cache/corr_gold.csv","Argento (ETC)":"data/cache/corr_silver.csv"}
rets={}; asof=None
for k,p in series.items():
    r,d=ytd(os.path.join(ROOT,p)); rets[k]=r; asof=d
json.dump({"minus":MINUS,"asof":str(asof),"rendimenti_ytd":rets},open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)
for k,r in rets.items(): print(f"{k:14s} YTD {r*100:+5.1f}%")

# ---- Chart 1: stessa scommessa, tre esiti fiscali diversi ----
# Investo l'importo che sul RAME azzera i 900,22€ (~4.713€) nei tre strumenti: cosa realizzo?
A=MINUS/rets["Rame (ETC)"]
names=list(series); outcomes=[A*rets[k] for k in names]
colors=[GREEN if o>0 else RED for o in outcomes]
fig,ax=plt.subplots(figsize=(9.5,5.4))
bars=ax.bar(names,outcomes,color=colors,width=0.55)
ax.axhline(0,color=INK,lw=1)
ax.axhline(MINUS,color=NAVY,lw=1.6,ls="--")
ax.text(2.42,MINUS,f"  soglia recupero pieno\n  ({MINUS:.0f}€)",color=NAVY,va="center",fontsize=10,weight="bold")
for b,o,k in zip(bars,outcomes,names):
    ax.text(b.get_x()+b.get_width()/2, o+(35 if o>0 else -35), f"{o:+,.0f}€".replace(",","."),
            ha="center", va="bottom" if o>0 else "top", fontsize=11, weight="bold",
            color=GREEN if o>0 else RED)
    r=rets[k]; ax.text(b.get_x()+b.get_width()/2, 60 if o<0 else -60, f"{r*100:+.1f}%", ha="center",
            va="top" if o<0 else "bottom", fontsize=10, color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:+,.0f}€".replace(",",".")))
ax.set_ylabel("Plus/minusvalenza realizzata")
ax.set_title(f"Stessa cifra investita (~{A:,.0f}€) — tre esiti opposti".replace(",",".")+
    f"\nrendimento reale 31/12/2025 → {asof}",fontsize=12.5,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_tre_esiti.png")); plt.close(fig)

# ---- Chart 2: quanto investire per recuperare, in funzione del rendimento ----
fig,ax=plt.subplots(figsize=(9.5,5.2))
rr=np.linspace(0.02,0.40,200); need=MINUS/rr
ax.plot(rr*100, need, color=NAVY, lw=2.4)
for r,lab in [(rets["Rame (ETC)"],"Rame +19%")]:
    ax.scatter([r*100],[MINUS/r],color=GOLD,zorder=5,s=70,edgecolor=INK,lw=1)
    ax.annotate(f"{lab}: servono {MINUS/r:,.0f}€".replace(",","."),(r*100,MINUS/r),
        textcoords="offset points",xytext=(12,14),fontsize=10.5,weight="bold",color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v/1000:.0f}k€"))
ax.set_xlabel("Rendimento realizzato dallo strumento (%)"); ax.set_ylabel("Capitale da investire e vendere")
ax.set_title(f"Per generare {MINUS:.0f}€ di plusvalenza e azzerare la minus\nquanto capitale serve, al variare del rendimento",fontsize=12.5,weight="bold")
ax.set_xlim(2,40); ax.set_ylim(0, MINUS/0.02)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_quanto_investire.png")); plt.close(fig)

# ---- Chart 3: certificato leva fissa 5x su Ferrari — stesso strumento, due date d'ingresso ----
d=pd.read_csv(os.path.join(ROOT,"data/raw/ferrari_mi_race.csv"),skiprows=3,header=None,usecols=[0,1],names=["date","close"])
d["date"]=pd.to_datetime(d["date"]); d=d.dropna().sort_values("date")
scen=[("2025-12-31","1 gennaio 2026 — mercato nervoso"),("2026-04-01","1 aprile 2026 — trend pulito")]
leva={}
fig,axes=plt.subplots(1,2,figsize=(12.5,5.3),sharey=False)
for ax,(start,titolo) in zip(axes,scen):
    w=d[d.date>=start].reset_index(drop=True); dr=w.close.pct_change().fillna(0)
    und=100*(1+dr).cumprod(); cert=100*(1+5*dr).cumprod()
    ur=und.iloc[-1]/100-1; cr=cert.iloc[-1]/100-1; leva[start]={"und":float(ur),"cert":float(cr)}
    ax.plot(w.date,und,color=RED,lw=2.3,label=f"Ferrari  {ur:+.0%}".replace("%","%"))
    ax.plot(w.date,cert,color=(GREEN if cr>ur else NAVY),lw=2.3,label=f"Cert. leva 5x  {cr:+.0%}")
    ax.axhline(100,color=GREY,lw=1,ls=":")
    ax.set_title(titolo,fontsize=11.5,weight="bold"); ax.legend(fontsize=10.5,loc="upper left")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}"))
axes[0].set_ylabel("Base 100 all'acquisto")
fig.suptitle("Stesso certificato leva 5x su Ferrari, due esiti opposti a seconda di QUANDO entri",fontsize=13,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_leva_ferrari.png")); plt.close(fig)
json.dump({"minus":MINUS,**{s:{**v,"cap_con_leva":(MINUS/v["cert"] if v["cert"]>0 else None),
    "cap_senza_leva":(MINUS/v["und"] if v["und"]>0 else None)} for s,v in leva.items()}},
    open(os.path.join(OUT,"leva.json"),"w"),indent=2,ensure_ascii=False)
for s,v in leva.items(): print(f"da {s}: Ferrari {v['und']:+.1%} cert5x {v['cert']:+.1%}")
print("OK charts ->", OUT)
