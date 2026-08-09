"""Genera le tabelle illustrative dell'articolo in data/processed/article_tables.md"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); PROC=os.path.join(HERE,"..","data","processed")
ds=pd.read_csv(os.path.join(PROC,"cape_forward_dataset.csv"))
POOLED=["Japan","Germany","France","Switzerland","Australia","Canada","Italy","Spain",
        "Netherlands","Denmark","Finland","Norway","Sweden","Belgium","Austria","Brazil",
        "China","India","South Africa","South Korea","Taiwan","Indonesia","Thailand","US Large"]
d=ds[ds.market.isin(POOLED)].copy()
d["cape_rel"]=d.cape/d.groupby("market").cape.transform("median")

out=[]
def w(s): out.append(s)

# T2 centerpiece: CAPE vs propria mediana -> fwd
w("### Tabella A — CAPE rispetto alla propria mediana storica → rendimento forward\n")
w("Pool di 24 mercati. Fasce del rapporto CAPE/mediana-del-paese (1.00 = valutazione tipica del mercato).\n")
bins=[0,0.7,0.85,1.0,1.15,1.3,9]; labs=["<0.70 (molto economico)","0.70-0.85","0.85-1.00","1.00-1.15","1.15-1.30",">1.30 (molto caro)"]
d["rb"]=pd.cut(d.cape_rel,bins=bins,labels=labs)
for h in (5,10):
    w(f"\n**Forward {h} anni (annualizzato, USD gross TR):**\n")
    w("| CAPE / mediana paese | n | mediana | media | % periodi negativi |")
    w("|---|---:|---:|---:|---:|")
    g=d.dropna(subset=[f"fwd{h}_ann"]).groupby("rb",observed=True)[f"fwd{h}_ann"]
    for bk in labs:
        if bk in g.groups:
            s=g.get_group(bk)
            w(f"| {bk} | {len(s)} | {s.median()*100:+.1f}% | {s.mean()*100:+.1f}% | {100*(s<0).mean():.0f}% |")

# T1 absolute
w("\n\n### Tabella B — CAPE assoluto → rendimento forward (lo screening cross-country che NON funziona)\n")
b2=[0,10,15,20,25,30,40,999]; l2=["<10","10-15","15-20","20-25","25-30","30-40",">40"]
d["ab"]=pd.cut(d.cape,bins=b2,labels=l2)
for h in (5,10):
    w(f"\n**Forward {h} anni:**\n")
    w("| CAPE assoluto | n | mediana | media | % negativi |")
    w("|---|---:|---:|---:|---:|")
    g=d.dropna(subset=[f"fwd{h}_ann"]).groupby("ab",observed=True)[f"fwd{h}_ann"]
    for bk in l2:
        if bk in g.groups:
            s=g.get_group(bk)
            w(f"| {bk} | {len(s)} | {s.median()*100:+.1f}% | {s.mean()*100:+.1f}% | {100*(s<0).mean():.0f}% |")

# T3 per-country R2
w("\n\n### Tabella C — Potere predittivo per paese (fwd 10 anni ~ CAPE)\n")
w("| Mercato | n | corr | R² |")
w("|---|---:|---:|---:|")
rows=[]
for mk in POOLED:
    dd=ds[ds.market==mk][["cape","fwd10_ann"]].dropna()
    if len(dd)>=18:
        r=np.corrcoef(dd.cape,dd.fwd10_ann)[0,1]; rows.append((mk,len(dd),r,r*r))
for mk,n,r,r2 in sorted(rows,key=lambda x:-x[3]):
    w(f"| {mk} | {n} | {r:+.2f} | {r2:.2f} |")

# correlation summary
w("\n\n### Tabella D — Potenza del segnale a confronto (pooled, fwd 10 anni)\n")
w("| Segnale | corr | R² |")
w("|---|---:|---:|")
def cr(x,y):
    dd=d[[x,y]].dropna(); r=np.corrcoef(dd[x],dd[y])[0,1]; return r,r*r
d["ey"]=1/d.cape
for lab,col in [("CAPE assoluto","cape"),("CAPE / mediana paese","cape_rel"),("Earnings yield (1/CAPE)","ey")]:
    r,r2=cr(col,"fwd10_ann"); w(f"| {lab} | {r:+.3f} | {r2:.3f} |")

open(os.path.join(PROC,"article_tables.md"),"w").write("\n".join(out))
print("\n".join(out))
