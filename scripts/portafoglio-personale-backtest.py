"""
Il mio portafoglio (revisione 2026): backtest ~31 anni + export per Monte Carlo.

Portafoglio equity-only, 7 sleeve, allocazione target:
  Azionario USA 20 · Mercati Emergenti 20 · Nasdaq/Tech 25 · Smallcap 10 ·
  Europa Momentum 8 · Oro 8 · Energia 9

Ribilanciamento ANNUALE (1° gennaio) — coerente con la leaderboard del sito e
appropriato per un'allocazione target su orizzonte lungo (a differenza del
buy&hold, che su 31 anni lascerebbe il Nasdaq dominare l'intero portafoglio).

Total Return, gross (lordo) come baseline. Dividendi sintetici dove la serie e'
a prezzo: Nasdaq Composite +0,75%/anno, S&P 500 Energy +2,9%/anno (settore ad
alto dividendo). Tutte le altre serie sono gia' TR.

Benchmark (tutti TR): S&P 500 (SPY), MSCI World, MSCI ACWI IMI.
Finestra comune: da luglio 1995 (vincolo = Russell 2000 TR dal 06/1995).

Output: public/charts/portafoglio-personale-backtest/*.png + summary.json
        + monthly_returns.csv (input del Monte Carlo).
"""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
RAW=os.path.join(ROOT,"data","raw"); CACHE=os.path.join(ROOT,"data","cache")
OUT=os.path.join(ROOT,"public","charts","portafoglio-personale-backtest"); os.makedirs(OUT,exist_ok=True)

NAVY="#1e3a8a"; GOLD="#f59e0b"; GREY="#94a3b8"; GREEN="#059669"; RED="#e11d48"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
def it(x,d=1): return f"{x:.{d}f}".replace(".",",")
def eur(v,_=None): return f"{v/1000:.0f}k€" if abs(v)>=1000 else f"{v:.0f}€"
def pctf(v,_=None): return f"{v:.0f}%"

# ---------------------------------------------------------------- loaders -> serie mensile TR (indice)
def _daily_close(path,col="Close"):
    d=pd.read_csv(path); d["Date"]=pd.to_datetime(d["Date"])
    s=pd.Series(pd.to_numeric(d[col],errors="coerce").values,index=d["Date"]).dropna().sort_index()
    return s.resample("ME").last()
def _mensile_it(path,col):
    d=pd.read_csv(path); d["Data"]=pd.to_datetime(d["Data"],format="%m/%Y")
    s=pd.Series(pd.to_numeric(d[col],errors="coerce").values,index=d["Data"]).dropna().sort_index()
    return s.resample("ME").last()
def _corr_usa():
    d=pd.read_csv(os.path.join(CACHE,"corr_usa.csv")); d["Date"]=pd.to_datetime(d["Date"])
    s=pd.Series(pd.to_numeric(d["adjclose"],errors="coerce").values,index=d["Date"]).dropna().sort_index()
    return s.resample("ME").last()
def _gold():
    d=pd.read_csv(os.path.join(RAW,"Gold_montly_historical1985 - Foglio1.csv")); d["DATE"]=pd.to_datetime(d["DATE"])
    v=d["PRICE"].astype(str).str.replace("$","",regex=False).str.replace(",","",regex=False).astype(float)
    return pd.Series(v.values,index=d["DATE"]).dropna().sort_index().resample("ME").last()

def to_ret(idx): return idx.pct_change().dropna()
def add_div(ret,ann):  # aggiunge dividendo sintetico annuo a una serie di rendimenti prezzo
    dm=(1+ann)**(1/12)-1; return (1+ret)*(1+dm)-1

# indici prezzo/TR
usa   = _corr_usa()                                                  # SPY adj close = TR
em    = _mensile_it(os.path.join(RAW,"Msci_EM_histhorical_1987.csv"),"MSCI Emerging Markets")  # TR
nas_p = _daily_close(os.path.join(RAW,"Nasdaq_historical.csv"))       # Composite prezzo
smc   = _daily_close(os.path.join(RAW,"Russel2000.csv"))              # Russell 2000 TR (dal 1995)
eurm  = _mensile_it(os.path.join(RAW,"MSCI_Euro_Momentum1994.csv"),"MSCI Europe Momentum")     # TR
oro   = _gold()                                                      # prezzo=TR (no cedole)
ene_p = _daily_close(os.path.join(RAW,"sp500energy1993.csv"))         # S&P Energy prezzo
world = _mensile_it(os.path.join(RAW,"MSCI_world_historical1969.csv"),"MSCI World")            # TR bench
acwi  = _mensile_it(os.path.join(RAW,"MSCI_ACWI_IMI1994.csv"),"MSCI ACWI IMI")                 # TR bench

# rendimenti mensili TR degli sleeve
R={
 "usa":       to_ret(usa),
 "em":        to_ret(em),
 "nasdaq":    add_div(to_ret(nas_p), 0.0075),   # +0,75% dividendo sintetico
 "smallcap":  to_ret(smc),
 "europa_mom":to_ret(eurm),
 "oro":       to_ret(oro),
 "energy":    add_div(to_ret(ene_p), 0.029),    # +2,9% dividendo sintetico (settore alto div)
}
BENCH={"S&P 500 TR":to_ret(usa), "MSCI World TR":to_ret(world), "MSCI ACWI IMI TR":to_ret(acwi)}
W={"usa":.20,"em":.20,"nasdaq":.25,"smallcap":.10,"europa_mom":.08,"oro":.08,"energy":.09}
assert abs(sum(W.values())-1)<1e-9

# finestra comune
common=None
for s in list(R.values())+list(BENCH.values()):
    common = s.index if common is None else common.intersection(s.index)
common=common.sort_values()
R={k:v.reindex(common) for k,v in R.items()}
BENCH={k:v.reindex(common) for k,v in BENCH.items()}
retdf=pd.DataFrame(R); benchdf=pd.DataFrame(BENCH)
START,END=common[0],common[-1]

# ---------------------------------------------------------------- portafoglio, ribilanciamento annuale
def port_returns(retdf, target):
    w=dict(target); out=[]
    for dt,row in retdf.iterrows():
        if dt.month==1: w=dict(target)                 # ribilancio a gennaio
        pr=sum(w[k]*row[k] for k in target)
        out.append(pr)
        nw={k:w[k]*(1+row[k]) for k in target}; tot=sum(nw.values()); w={k:nw[k]/tot for k in target}
    return pd.Series(out,index=retdf.index)

port=port_returns(retdf,W)
allret=pd.concat([port.rename("Portafoglio"),benchdf],axis=1)   # per rolling + MC

def nav_lump(r,cap=10000.0): return cap*(1+r).cumprod()
def nav_pac(r,m=200.0):
    nav=0.0; out=[]
    for x in r: nav=nav*(1+x)+m; out.append(nav)
    return pd.Series(out,index=r.index)

lump={c:nav_lump(allret[c]) for c in allret}
pac ={c:nav_pac(allret[c]) for c in allret}
n_months=len(port); contrib_tot=200.0*n_months

# ---------------------------------------------------------------- metriche
def metrics(r):
    r=r.dropna(); yrs=len(r)/12
    cagr=(1+r).prod()**(1/yrs)-1
    vol=r.std()*np.sqrt(12)
    nav=(1+r).cumprod(); mdd=(nav/nav.cummax()-1).min()
    sharpe=(r.mean()*12)/vol if vol>0 else np.nan
    dr=r[r<0].std()*np.sqrt(12); sortino=(r.mean()*12)/dr if dr>0 else np.nan
    calmar=cagr/abs(mdd) if mdd<0 else np.nan
    return dict(cagr=cagr,vol=vol,mdd=mdd,sharpe=sharpe,sortino=sortino,calmar=calmar)
M={c:metrics(allret[c]) for c in allret}

# ---------------------------------------------------------------- rolling windows
def rolling_cagr(r,win_m):
    idx=(1+r).cumprod().values; out=[]
    for i in range(len(idx)-win_m):
        out.append((idx[i+win_m]/idx[i])**(12/win_m)-1)
    return np.array(out)
ROLL={}
for yrs in (5,10,15):
    wm=yrs*12
    if len(port)>wm+1:
        pc=rolling_cagr(allret["Portafoglio"],wm)
        row={"n":len(pc),"port_med":float(np.median(pc))}
        for b in BENCH:
            bc=rolling_cagr(allret[b],wm)
            row[f"win_vs_{b}"]=float((pc>bc).mean()); row[f"{b}_med"]=float(np.median(bc))
        ROLL[f"{yrs}y"]=row

# ---------------------------------------------------------------- export per Monte Carlo
allret.to_csv(os.path.join(OUT,"monthly_returns.csv"))

# ================================================================ GRAFICI
LAB={"usa":"USA","em":"Emergenti","nasdaq":"Nasdaq/Tech","smallcap":"Smallcap",
     "europa_mom":"Europa Momentum","oro":"Oro","energy":"Energia"}
def chart_donut():
    fig,ax=plt.subplots(figsize=(7,7))
    vals=[W[k]*100 for k in W]; labs=[f"{LAB[k]} {W[k]*100:.0f}%" for k in W]
    cols=[NAVY,"#2563eb",GOLD,"#60a5fa",GREEN,"#fbbf24",RED]
    ax.pie(vals,labels=labs,colors=cols,startangle=90,counterclock=False,
           wedgeprops={"width":.42,"edgecolor":"white","linewidth":2},textprops={"fontsize":12})
    ax.set_title("Allocazione target del portafoglio",fontweight="bold")
    fig.savefig(os.path.join(OUT,"01_composizione_donut.png")); plt.close(fig)

def chart_lump():
    fig,ax=plt.subplots(figsize=(11,5.6))
    order=[("Portafoglio",NAVY,2.6),("S&P 500 TR",GOLD,1.8),("MSCI World TR",GREY,1.8),("MSCI ACWI IMI TR",GREEN,1.8)]
    for c,col,lw in order: ax.plot(lump[c].index,lump[c].values,color=col,lw=lw,label=c)
    ax.set_yscale("log"); ax.yaxis.set_major_formatter(FuncFormatter(eur))
    ax.set_title(f"10.000 € investiti a luglio 1995 (scala log, lordo TR)",fontweight="bold")
    ax.legend(frameon=False,fontsize=10)
    fig.savefig(os.path.join(OUT,"02_equity_lump.png")); plt.close(fig)

def chart_pac():
    fig,ax=plt.subplots(figsize=(11,5.6))
    for c,col,lw in [("Portafoglio",NAVY,2.6),("S&P 500 TR",GOLD,1.8),("MSCI World TR",GREY,1.8),("MSCI ACWI IMI TR",GREEN,1.8)]:
        ax.plot(pac[c].index,pac[c].values,color=col,lw=lw,label=c)
    ax.plot(port.index,np.arange(1,len(port)+1)*200.0,color=INK,lw=1.2,ls="--",label="Versato (200€/mese)")
    ax.yaxis.set_major_formatter(FuncFormatter(eur))
    ax.set_title("PAC da 200 €/mese dal 1995",fontweight="bold"); ax.legend(frameon=False,fontsize=10)
    fig.savefig(os.path.join(OUT,"03_equity_pac.png")); plt.close(fig)

def chart_rolling():
    wm=10*12; data=[rolling_cagr(allret[c],wm)*100 for c in allret]
    fig,ax=plt.subplots(figsize=(10,5.4))
    bp=ax.boxplot(data,vert=True,patch_artist=True,labels=list(allret.columns),showfliers=False)
    cols=[NAVY,GOLD,GREY,GREEN]
    for p,col in zip(bp["boxes"],cols): p.set_facecolor(col); p.set_alpha(.85)
    for med in bp["medians"]: med.set_color(INK)
    ax.yaxis.set_major_formatter(FuncFormatter(pctf))
    ax.set_title("Rendimento annualizzato su tutte le finestre mobili di 10 anni",fontweight="bold")
    fig.savefig(os.path.join(OUT,"04_rolling_10y.png")); plt.close(fig)

def chart_metrics():
    labels=["CAGR","Volatilità","Max drawdown","Calmar"]
    fig,axes=plt.subplots(1,4,figsize=(13,4.2))
    keys=["cagr","vol","mdd","calmar"]; cols=[NAVY,GOLD,GREY,GREEN]
    names=list(allret.columns)
    for ax,lab,key in zip(axes,labels,keys):
        vals=[M[n][key]*(100 if key!="calmar" else 1) for n in names]
        ax.bar(range(len(names)),vals,color=cols)
        ax.set_title(lab,fontsize=12,fontweight="bold"); ax.set_xticks([])
        for i,v in enumerate(vals):
            ax.text(i,v,(f"{v:.2f}" if key=="calmar" else f"{v:.1f}%"),ha="center",
                    va="bottom" if v>=0 else "top",fontsize=9)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=c,label=n) for c,n in zip(cols,names)],
               loc="lower center",ncol=4,frameon=False,fontsize=10)
    fig.suptitle("Portafoglio vs benchmark — metriche full sample (1995-2026)",fontweight="bold")
    fig.tight_layout(rect=[0,0.05,1,0.95])
    fig.savefig(os.path.join(OUT,"05_metriche.png")); plt.close(fig)

chart_donut(); chart_lump(); chart_pac(); chart_rolling(); chart_metrics()

# ================================================================ summary.json
summary={
 "finestra":[str(START.date()),str(END.date())],"n_mesi":int(n_months),
 "pesi":W,"div_sintetici":{"nasdaq":0.0075,"energy":0.029},"ribilanciamento":"annuale (gennaio)",
 "metriche":{c:{k:round(v,4) for k,v in M[c].items()} for c in M},
 "lump_10k":{c:round(float(lump[c].iloc[-1]),0) for c in lump},
 "pac":{"versato":round(contrib_tot,0),**{c:round(float(pac[c].iloc[-1]),0) for c in pac}},
 "rolling":ROLL,
}
with open(os.path.join(OUT,"summary.json"),"w",encoding="utf-8") as f:
    json.dump(summary,f,ensure_ascii=False,indent=2)

print("OK finestra",START.date(),"->",END.date(),"mesi",n_months)
for c in allret:
    print(f"  {c:18s} CAGR {M[c]['cagr']*100:5.2f}%  vol {M[c]['vol']*100:4.1f}%  MDD {M[c]['mdd']*100:6.1f}%  Calmar {M[c]['calmar']:.3f}  lump {lump[c].iloc[-1]:,.0f}")
print("rolling:",json.dumps(ROLL,ensure_ascii=False))
