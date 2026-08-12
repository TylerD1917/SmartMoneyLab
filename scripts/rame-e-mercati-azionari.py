"""
Rame (Dr. Copper) e mercati azionari — il crollo del rame anticipa i crolli di Borsa?
Event-study + analisi continua. S&P 500 in Total Return (ricostruito da Shiller).
Dati: rame FRED mensile PCOPPUSDM (1992-2026); Shiller monthly per S&P TR.
Output: public/charts/rame-e-mercati-azionari/*.png + summary JSON.
"""
import pandas as pd, numpy as np, os, json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","rame-e-mercati-azionari"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

# ---- S&P 500 Total Return mensile da Shiller ----
sh=pd.read_csv(os.path.join(ROOT,"data","cache","shiller_mirror.csv"),parse_dates=["Date"])
sh=sh[["Date","SP500","Dividend"]].rename(columns={"Date":"date","SP500":"p","Dividend":"dv"}).sort_values("date").reset_index(drop=True)
tr=[1.0]; last_dy=None
for t in range(1,len(sh)):
    p0,p1=sh["p"][t-1],sh["p"][t]; d0=sh["dv"][t-1]
    dy=(d0/12)/p0 if d0>0 else (last_dy if last_dy else 0.0)
    if d0>0: last_dy=(d0/12)/p0
    tr.append(tr[-1]*(p1/p0+dy))
sh["tr"]=tr
sp=sh[["date","tr"]].copy()
def sp_on(dt):
    x=sp[sp.date<=dt]; return x.tr.iloc[-1] if len(x) else np.nan
def sp_fwd(dt,m):
    a=sp_on(dt); b=sp_on(dt+pd.DateOffset(months=m)); return (b/a-1) if a==a and b==b else np.nan

# ---- Rame mensile FRED ----
cu=pd.read_csv(os.path.join(ROOT,"data","raw","CopperHistorical.csv"),parse_dates=["observation_date"])
cu.columns=["date","price"]; cu=cu.sort_values("date").reset_index(drop=True)
cu["chg3"]=cu.price/cu.price.shift(3)-1
cu["chg6"]=cu.price/cu.price.shift(6)-1

# ---- baseline S&P TR forward (tutti i mesi del periodo rame) ----
base={}
for m in (3,6,12):
    vals=[sp_fwd(d,m) for d in cu.date]; base[m]=np.nanmean(vals)
print("BASELINE S&P TR (1992-2026):", {f"{m}m":round(base[m]*100,1) for m in (3,6,12)})

# ---- EVENT STUDY ----
def events(thr,win,cooldown=12):
    p=cu.price.values; d=cu.date.values; ev=[]; last=-999
    for i in range(win,len(p)):
        if p[i]/p[i-win]-1<=-thr and (i-last)>cooldown:
            ev.append(pd.Timestamp(d[i])); last=i
    return ev
summary={"baseline_sp_tr":{f"{m}m":base[m] for m in (3,6,12)},"events":{}}
defs=[("−20% in 3 mesi",0.20,3),("−20% in 6 mesi",0.20,6),("−25% in 3 mesi",0.25,3)]
for label,thr,win in defs:
    ev=events(thr,win); rows=[]
    for dt in ev:
        rows.append({"date":str(dt.date()),"sp3":sp_fwd(dt,3),"sp6":sp_fwd(dt,6),"sp12":sp_fwd(dt,12)})
    arr=lambda k:np.array([r[k] for r in rows],dtype=float)
    no08=[r for r in rows if not r["date"].startswith("2008")]
    summary["events"][label]={"n":len(rows),"detail":rows,
        "mean":{m:float(np.nanmean(arr(f"sp{m}"))) for m in(3,6,12)},
        "mean_ex2008":{m:float(np.nanmean([r[f"sp{m}"] for r in no08])) for m in(3,6,12)}}
    print(f"\n[{label}] n={len(rows)}")
    for r in rows: print(f"  {r['date']}  S&P +3m {r['sp3']*100:+.1f}  +6m {r['sp6']*100:+.1f}  +12m {r['sp12']*100:+.1f}")
    m=summary["events"][label]["mean"]; mx=summary["events"][label]["mean_ex2008"]
    print(f"  MEDIA      +3m {m[3]*100:+.1f}  +6m {m[6]*100:+.1f}  +12m {m[12]*100:+.1f}")
    print(f"  MEDIA ex-2008 +3m {mx[3]*100:+.1f}  +6m {mx[6]*100:+.1f}  +12m {mx[12]*100:+.1f}")

# ---- ANALISI CONTINUA: variazione rame vs S&P TR forward ----
cont={}
print("\n== ANALISI CONTINUA (tutti i mesi) — corr(variazione rame, S&P TR forward) ==")
for cch in ("chg3","chg6"):
    cont[cch]={}
    for m in (3,6,12):
        d=cu[["date",cch]].dropna().copy(); d["fwd"]=[sp_fwd(x,m) for x in d.date]; d=d.dropna()
        r=np.corrcoef(d[cch],d.fwd)[0,1]
        cont[cch][f"fwd{m}"]={"corr":float(r),"r2":float(r*r),"n":int(len(d))}
        print(f"  rame {cch} vs S&P +{m}m: corr {r:+.3f}  R2 {r*r:.3f}  n={len(d)}")
summary["continuous"]=cont

# bucket copper chg3 quintili -> S&P fwd 6m e 12m
d=cu[["date","chg3"]].dropna().copy()
d["f6"]=[sp_fwd(x,6) for x in d.date]; d["f12"]=[sp_fwd(x,12) for x in d.date]; d=d.dropna()
d["q"]=pd.qcut(d.chg3,5,labels=["rame in forte calo","2","3 stabile","4","rame in forte rialzo"])
buck=d.groupby("q",observed=True)[["f6","f12"]].median()
summary["bucket_chg3"]={str(k):{"f6":float(v.f6),"f12":float(v.f12)} for k,v in buck.iterrows()}
print("\n== Bucket variazione rame 3m -> S&P TR forward (mediana) ==")
print(buck.mul(100).round(1))

json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)

# ================= GRAFICI =================
E=summary["events"]["−20% in 3 mesi"]
H=[3,6,12]; xl=["3 mesi","6 mesi","12 mesi"]

# Chart 1: dopo un crollo del rame vs baseline
fig,ax=plt.subplots(figsize=(9,5))
x=np.arange(3); w=0.26
bl=[base[m]*100 for m in H]; af=[E["mean"][m]*100 for m in H]; ax08=[E["mean_ex2008"][m]*100 for m in H]
ax.bar(x-w,bl,w,label="Mese qualsiasi (baseline)",color=GREY)
ax.bar(x,af,w,label="Dopo un crollo del rame",color=NAVY)
ax.bar(x+w,ax08,w,label="Dopo un crollo del rame (senza 2008)",color=GOLD)
ax.set_xticks(x); ax.set_xticklabels(xl); ax.set_ylabel("Rendimento S&P 500 (Total Return)")
ax.yaxis.set_major_formatter(PercentFormatter()); ax.axhline(0,color=INK,lw=1)
ax.set_title("Cosa ha fatto l'S&P 500 dopo un crollo del rame\n(rame −20% in 3 mesi, 1992-2026)",fontsize=13,weight="bold")
ax.legend(fontsize=10); fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_dopo_crollo_vs_baseline.png")); plt.close(fig)

# Chart 2: per evento, S&P a 3 mesi (2008 evidenziato)
ev=summary["events"]["−20% in 3 mesi"]["detail"]
fig,ax=plt.subplots(figsize=(9,5))
labels=[r["date"][:7] for r in ev]; vals=[r["sp3"]*100 for r in ev]
cols=[RED if r["date"].startswith("2008") else NAVY for r in ev]
ax.bar(range(len(ev)),vals,color=cols)
ax.axhline(base[3]*100,color=GOLD,lw=2,ls="--",label=f"baseline +3m ({base[3]*100:+.1f}%)")
ax.set_xticks(range(len(ev))); ax.set_xticklabels(labels)
ax.set_ylabel("S&P 500 nei 3 mesi dopo il crollo"); ax.yaxis.set_major_formatter(PercentFormatter())
ax.axhline(0,color=INK,lw=1); ax.legend()
ax.set_title("Solo nel 2008 al crollo del rame è seguito un calo azionario marcato",fontsize=13,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_per_evento_3m.png")); plt.close(fig)

# Chart 3: bucket variazione rame 3m -> S&P fwd 12m (piatto)
fig,ax=plt.subplots(figsize=(9,5))
bx=list(buck.index); bv=buck.f12.mul(100).values
cols=[GOLD if i==0 else NAVY for i in range(len(bx))]
ax.bar(range(len(bx)),bv,color=cols)
ax.axhline(base[12]*100,color=GREY,lw=2,ls="--",label=f"baseline +12m ({base[12]*100:+.1f}%)")
ax.set_xticks(range(len(bx))); ax.set_xticklabels(bx,fontsize=10)
ax.set_ylabel("S&P 500 nei 12 mesi dopo (mediana)"); ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_title("Il rame che scende non anticipa un mercato debole\nRendimento S&P a 12 mesi per fascia di variazione del rame (3 mesi)",fontsize=12,weight="bold")
ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_bucket_rame_sp.png")); plt.close(fig)

print("[ok] summary.json + 3 grafici salvati in", OUT)
