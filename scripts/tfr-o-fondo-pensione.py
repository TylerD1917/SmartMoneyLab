"""
TFR in azienda o fondo pensione? — grafici per l'articolo SEO #3.
Dati rendimenti: tabelle COVIP fine 2025 (FPA aperti, FPN negoziali) per categoria,
+ dato ufficiale Relazione COVIP 2025: azionari ~5% / TFR 2,5% medio annuo (2016-2025, netti).
Output: public/charts/tfr-o-fondo-pensione/*.png
"""
import os, glob, json, statistics as st
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
import openpyxl
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","tfr-o-fondo-pensione"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
DATADIR=os.path.join(ROOT,"data","Fondi pensione ita")

def cat_avg(path,sheet):
    wb=openpyxl.load_workbook(path,data_only=True); ws=wb[sheet]
    rows=list(ws.iter_rows(values_only=True))
    hi=[i for i,r in enumerate(rows) if any(c and "CATEGORIA" in str(c).upper() for c in r)][0]
    hdr=rows[hi]; catcol=[j for j,c in enumerate(hdr) if c and "CATEGORIA" in str(c).upper()][0]
    sub=rows[hi+1]; c10=[j for j,c in enumerate(sub) if c and "10 anni" in str(c)][0]
    agg={}
    for r in rows[hi+3:]:
        cat=r[catcol]
        if not cat: continue
        cat=str(cat).strip().upper()
        try: v=float(str(r[c10]).replace(",","."))
        except: continue
        if -50<v<50: agg.setdefault(cat,[]).append(v)
    return {k:st.mean(v) for k,v in agg.items()}
fpn=cat_avg(os.path.join(DATADIR,"FPN_Rendimenti_fine2025.xlsx"),"FPN")
fpa=cat_avg(os.path.join(DATADIR,"FPA_Rendimenti_fine2025.xlsx"),"FPA")

# ---- Chart 1: rendimenti netti medi 10 anni per categoria vs TFR ----
TFR10=2.5  # rivalutazione TFR media annua 2016-2025 (COVIP, netta)
cats=[("Garantito","GAR"),("Obbligazionario","OBB PURO"),("Bilanciato","BIL"),("Azionario","AZN")]
labels=[c[0] for c in cats]
neg=[fpn.get(c[1]) for c in cats]; ape=[fpa.get(c[1]) for c in cats]
x=np.arange(len(labels)); w=0.38
fig,ax=plt.subplots(figsize=(10,5.4))
b1=ax.bar(x-w/2,[v if v is not None else 0 for v in neg],w,label="Fondi negoziali",color=NAVY)
b2=ax.bar(x+w/2,[v if v is not None else 0 for v in ape],w,label="Fondi aperti",color=GOLD)
ax.axhline(TFR10,color=RED,lw=2,ls="--")
ax.text(3.35,TFR10,f"  TFR  {TFR10:.1f}%".replace(".",","),color=RED,va="center",fontsize=11,weight="bold")
for bars in (b1,b2):
    for b in bars:
        h=b.get_height()
        if h: ax.text(b.get_x()+b.get_width()/2,h+0.06,f"{h:.1f}".replace(".",","),ha="center",fontsize=9.5)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
ax.set_ylabel("Rendimento netto medio annuo")
ax.set_title("Rendimenti netti a 10 anni per comparto (2016-2025)\nsolo l'azionario stacca nettamente la rivalutazione del TFR",fontsize=12.5,weight="bold")
ax.legend(fontsize=10.5,loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_rendimenti_categoria.png")); plt.close(fig)

# ---- Chart 2: montante di 30 anni di TFR, tre destinazioni (lordo e netto) ----
RAL=30000; ANNI=30
TFR_YR=RAL/13.5*(1-0.0050/ (RAL/13.5) *RAL) if False else RAL/13.5  # quota TFR annua lorda
# nota: sul TFR c'è lo 0,50% a INPS; usiamo la quota lorda /13,5 per semplicità e la dichiariamo
scen={"TFR in azienda":(0.025,"sep"),"Fondo bilanciato":(0.030,"fp"),"Fondo azionario":(0.050,"fp")}
def montante(rate):
    v=0; path=[]
    for _ in range(ANNI):
        v=v*(1+rate)+TFR_YR; path.append(v)
    return np.array(path)
paths={k:montante(r) for k,(r,_) in scen.items()}
contrib_tot=TFR_YR*ANNI
def netto(k):
    r,tax=scen[k]; m=paths[k][-1]
    if tax=="sep":   # TFR: tassazione separata ~25% sui contributi (rivalutazione già netta)
        aliq=0.25; base=contrib_tot; return m-aliq*base, aliq
    else:            # fondo: 15% -0,3%/anno oltre il 15° -> a 30 anni 10,5% sui contributi conferiti
        aliq=max(0.09,0.15-0.003*(ANNI-15)); base=contrib_tot; return m-aliq*base, aliq
cols={"TFR in azienda":RED,"Fondo bilanciato":GOLD,"Fondo azionario":NAVY}
fig,(axL,axR)=plt.subplots(1,2,figsize=(12.5,5.3),gridspec_kw={"width_ratios":[1.5,1]})
yr=np.arange(1,ANNI+1)
for k,p in paths.items(): axL.plot(yr,p/1000,color=cols[k],lw=2.4,label=k)
axL.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k€"))
axL.set_xlabel("Anni di lavoro"); axL.set_ylabel("Montante lordo accumulato")
axL.set_title("30 anni di TFR versato (RAL 30.000€)",fontsize=11.5,weight="bold"); axL.legend(fontsize=10)
names=list(scen); netvals=[netto(k)[0] for k in names]; grossvals=[paths[k][-1] for k in names]
xb=np.arange(len(names))
axR.bar(xb,[g/1000 for g in grossvals],0.5,color=GREY,label="Lordo")
axR.bar(xb,[n/1000 for n in netvals],0.5,color=[cols[k] for k in names],label="Netto (dopo tasse)")
for i,(g,n,k) in enumerate(zip(grossvals,netvals,names)):
    axR.text(i,n/1000-4,f"{n/1000:.0f}k".replace(".",","),ha="center",va="top",color="white",fontsize=10,weight="bold")
axR.set_xticks(xb); axR.set_xticklabels([n.replace("Fondo ","Fondo\n") for n in names],fontsize=9.5)
axR.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k€"))
axR.set_title("Valore finale netto",fontsize=11.5,weight="bold")
fig.suptitle("Stesso TFR, tre destinazioni: il comparto e le tasse fanno la differenza",fontsize=13,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_montante.png")); plt.close(fig)

summary={"tfr_yr":TFR_YR,"anni":ANNI,"contrib_tot":contrib_tot,
    "cat10_negoziali":fpn,"cat10_aperti":fpa,"tfr_10y":TFR10,
    "montante_lordo":{k:float(paths[k][-1]) for k in scen},
    "montante_netto":{k:float(netto(k)[0]) for k in scen},
    "aliquota_uscita":{k:float(netto(k)[1]) for k in scen}}
json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)
print(f"TFR/anno {TFR_YR:.0f}€  contrib.tot {contrib_tot:.0f}€")
for k in scen: print(f"  {k:18s} lordo {paths[k][-1]:8.0f}€  netto {netto(k)[0]:8.0f}€  (aliq uscita {netto(k)[1]*100:.1f}%)")
print("cat10 negoziali",{k:round(v,2) for k,v in fpn.items()})
print("cat10 aperti",{k:round(v,2) for k,v in fpa.items()})
print("OK ->",OUT)
