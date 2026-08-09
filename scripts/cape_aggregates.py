"""
Analisi CAPE -> rendimenti forward per gli INDICI AMPI che il retail compra davvero:
World (Developed Markets Large vs MSCI World), Emerging Markets, Europe, Asia ex Japan.
Ogni aggregato e' una singola serie: il suo CAPE nel tempo vs il proprio rendimento forward
= gia' il segnale "vs la propria storia".
"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); PROC=os.path.join(HERE,"..","data","processed")
ds=pd.read_csv(os.path.join(PROC,"cape_forward_dataset.csv"))

AGG={"Developed Markets Large":"World (mercati sviluppati)","Emerging Markets":"Mercati emergenti",
     "Europe":"Europa","Asia ex Japan":"Asia ex Giappone"}

def rr(df,x,y):
    d=df[[x,y]].dropna()
    if len(d)<15: return None
    r=np.corrcoef(d[x],d[y])[0,1]; return len(d),r,r*r

print("### Tabella E — CAPE -> rendimento forward, indici ampi (ogni indice vs la propria storia)\n")
print("| Indice | n | corr 5y | R² 5y | corr 10y | R² 10y |")
print("|---|--:|--:|--:|--:|--:|")
for mk,lab in AGG.items():
    d=ds[ds.market==mk]
    s5=rr(d,"cape","fwd5_ann"); s10=rr(d,"cape","fwd10_ann")
    if s10:
        print(f"| {lab} | {s10[0]} | {s5[1]:+.2f} | {s5[2]:.2f} | {s10[1]:+.2f} | {s10[2]:.2f} |")

# bucket pooled aggregati per CAPE/own-median
d=ds[ds.market.isin(AGG)].copy()
d["cape_rel"]=d.cape/d.groupby("market").cape.transform("median")
bins=[0,0.85,1.0,1.15,9]; labs=["≤0.85 (economico)","0.85-1.00","1.00-1.15","≥1.15 (caro)"]
d["rb"]=pd.cut(d.cape_rel,bins=bins,labels=labs)
print("\n### Tabella F — indici ampi: CAPE vs propria mediana -> forward (pool dei 4 aggregati)\n")
for h in (5,10):
    print(f"\n**Forward {h} anni:**\n")
    print("| CAPE / mediana indice | n | mediana | media | % neg |")
    print("|---|--:|--:|--:|--:|")
    g=d.dropna(subset=[f"fwd{h}_ann"]).groupby("rb",observed=True)[f"fwd{h}_ann"]
    for bk in labs:
        if bk in g.groups:
            s=g.get_group(bk)
            print(f"| {bk} | {len(s)} | {s.median()*100:+.1f}% | {s.mean()*100:+.1f}% | {100*(s<0).mean():.0f}% |")

# posizionamento attuale (ultimo CAPE reale lug 2026, dal panel completo)
capeL=pd.read_csv(os.path.join(PROC,"cape_panel_long.csv"))
print("\n### Dove sono oggi gli indici ampi (CAPE lug 2026 vs mediana storica)\n")
print("| Indice | CAPE oggi | mediana storica | rapporto |")
print("|---|--:|--:|--:|")
for mk,lab in AGG.items():
    dd=capeL[capeL.market==mk].sort_values("date")
    now=dd.cape.iloc[-1]; med=dd.cape.median()
    print(f"| {lab} | {now:.1f} | {med:.1f} | {now/med:.2f} |")

# --- grafico 06: bucket indici ampi ---
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
NAVY="#1e3a8a"; GOLD="#fbbf24"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0",
    "figure.dpi":170,"savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
OUT=os.path.join(HERE,"..","public","charts","cape-internazionale-predice-rendimenti")
labs2=["≤0.85\neconomico","0.85-\n1.00","1.00-\n1.15","≥1.15\ncaro"]
d["rb2"]=pd.cut(d.cape_rel,bins=bins,labels=labs2)
g5=d.dropna(subset=["fwd5_ann"]).groupby("rb2",observed=True).fwd5_ann.median()*100
g10=d.dropna(subset=["fwd10_ann"]).groupby("rb2",observed=True).fwd10_ann.median()*100
x=np.arange(len(labs2)); w=0.4
fig,ax=plt.subplots(figsize=(8.5,5))
ax.bar(x-w/2,g5.reindex(labs2).values,w,label="Forward 5 anni",color=GOLD)
ax.bar(x+w/2,g10.reindex(labs2).values,w,label="Forward 10 anni",color=NAVY)
ax.set_xticks(x); ax.set_xticklabels(labs2,fontsize=10)
ax.set_ylabel("Rendimento annualizzato (mediana)"); ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_title("Indici ampi (World, Emergenti, Europa, Asia):\nanche qui, più economico vs la propria storia = più rendimento",fontsize=12,weight="bold")
ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(OUT,"06_indici_ampi.png")); plt.close(fig)
print("\nGrafico 06 salvato.")
