# -*- coding: utf-8 -*-
"""
Serie "battere il mercato?" #6 — Portafoglio a massima decorrelazione (investibile).
5 asset: Oro, Treasury USA 20+, Financials, Nasdaq, Energia (S&P500 Energy).
Schema principale: EQUAL WEIGHT (20% ciascuno). Approfondimento: risk parity/ERC walk-forward.
Ribilancio annuale. Benchmark: S&P 500 TR + MSCI World TR. USD, total return, lordo.
Finestra: dal 1998-12 (vincolo Financials/Energia), ~27 anni: include dot-com, 2008, 2020, 2022.
Fonti (serie lunghe):
  Oro       = data/Gold/Gold_montly_historical1985.csv (prezzo mensile = TR, oro non rende cedole)
  Treasury  = TR ricostruito a maturita' costante 20y da FRED DGS20 (data/Bonds/DGS20_fred_1962.csv)
  Nasdaq    = Nasdaq Composite (data/Nasdaq/Nasdaq_composite1971.csv) + 0,75%/anno dividendo figurato
  Financials= corr_financial (ETF XLF, TR)   Energia = corr_energy (ETF XLE, TR)
  S&P500    = corr_usa (TR)                    MSCI World = serie lunga TR
Rolling 5/10/20y (step 3m) + periodo intero (6+1). Monte Carlo block bootstrap 3m, 10k, 10/20/30y.
Output: public/charts/portafoglio-decorrelato-batte-mercato/*.png + summary.json
"""
import os, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
COR=os.path.join(ROOT,"data","Correlazioni"); MW=os.path.join(ROOT,"data","Msci_world")
GOLD_D=os.path.join(ROOT,"data","Gold"); NAS=os.path.join(ROOT,"data","Nasdaq"); BON=os.path.join(ROOT,"data","Bonds")
OUT=os.path.join(ROOT,"public","charts","portafoglio-decorrelato-batte-mercato"); os.makedirs(OUT,exist_ok=True)
np.random.seed(42)
NAVY="#1e3a8a"; GOLD="#d4a017"; TEAL="#0f766e"; GREY="#64748b"; RED="#b91c1c"
plt.rcParams.update({"figure.dpi":130,"font.size":11,"axes.grid":True,"grid.alpha":.25,
                     "axes.spines.top":False,"axes.spines.right":False})

def m_last(s): return s.dropna().resample("ME").last()
def corr_lvl(n):
    d=pd.read_csv(os.path.join(COR,f"{n}.csv")); d.columns=["date","v"]; d["date"]=pd.to_datetime(d["date"])
    return m_last(pd.Series(pd.to_numeric(d["v"],errors="coerce").values,index=d["date"]))
def load_gold():
    d=pd.read_csv(os.path.join(GOLD_D,"Gold_montly_historical1985.csv")); d.columns=["date","p"]
    d["date"]=pd.to_datetime(d["date"],errors="coerce")
    d["p"]=pd.to_numeric(d["p"].astype(str).str.replace(r"[$,]","",regex=True),errors="coerce")
    return m_last(pd.Series(d["p"].values,index=d["date"]).sort_index())   # prezzo = TR
def load_nasdaq(div_ann=0.0075):
    d=pd.read_csv(os.path.join(NAS,"Nasdaq_composite1971.csv")); d["Date"]=pd.to_datetime(d["Date"],errors="coerce")
    p=m_last(pd.Series(pd.to_numeric(d["Close"],errors="coerce").values,index=d["Date"]).sort_index())
    r=p.pct_change().dropna(); rtr=(1+r)*(1+div_ann)**(1/12)-1           # aggiungi dividendo figurato
    return (1+rtr).cumprod()*100.0
def load_treasury20():
    d=pd.read_csv(os.path.join(BON,"DGS20_fred_1962.csv")); d.columns=["date","y"]
    d["date"]=pd.to_datetime(d["date"],errors="coerce"); y=m_last(pd.Series(pd.to_numeric(d["y"],errors="coerce").values,index=d["date"]))/100.0
    y=y.dropna(); y=y[y.index>=pd.Timestamp("1993-02-28")]   # salta il buco 1987-1993, periodo continuo
    idx=[100.0]; dts=[y.index[0]]; M=20; dt=1/12
    for i in range(1,len(y)):
        y0,y1=y.iloc[i-1],y.iloc[i]; c=y0*100.0
        pv=sum(c*(1+y1)**(-(k-dt)) for k in range(1,M+1))+100.0*(1+y1)**(-(M-dt))
        idx.append(idx[-1]*(pv/100.0)); dts.append(y.index[i])
    return pd.Series(idx,index=pd.DatetimeIndex(dts))
def load_world():
    d=pd.read_csv(os.path.join(MW,"MSCI_world_historical1969.csv")); d.columns=["date","v"]
    d["date"]=pd.to_datetime(d["date"],format="%m/%Y")+pd.offsets.MonthEnd(0)
    return m_last(pd.Series(pd.to_numeric(d["v"],errors="coerce").values,index=d["date"]))

ASSETS=["Oro","Treasury 20+","Financials","Nasdaq","Energia"]
lvl={"Oro":load_gold(),"Treasury 20+":load_treasury20(),"Financials":corr_lvl("corr_financial"),
     "Nasdaq":load_nasdaq(),"Energia":corr_lvl("corr_energy")}
spx=corr_lvl("corr_usa").pct_change().dropna(); wld=load_world().pct_change().dropna()
rf=pd.DataFrame({a:lvl[a] for a in ASSETS}).dropna().pct_change().dropna()

def erc_weights(cov, iters=100000, tol=1e-13):
    n=cov.shape[0]; b=1.0/n; x=1.0/np.sqrt(np.diag(cov))
    for _ in range(iters):
        x0=x.copy()
        for i in range(n):
            a=cov[i,i]; beta=cov[i,:]@x-x[i]*a; x[i]=(-beta+np.sqrt(beta*beta+4*a*b))/(2*a)
        if np.max(np.abs(x-x0))<tol: break
    return x/x.sum()
def bt_fixed(rets,w):
    idx=rets.index; w0=np.array(w,float); comp=w0*100.0; out=[]; dts=[]
    for dt in idx:
        comp=comp*(1+rets.loc[dt].values); out.append(comp.sum()); dts.append(dt)
        if dt.month==12: comp=w0*out[-1]
    return pd.Series(out,index=pd.DatetimeIndex(dts)).pct_change().dropna()
def bt_erc(rets,minobs=36):
    idx=rets.index; port=[];pi=[];w=None
    for i,dt in enumerate(idx):
        if w is None or dt.month==1:
            past=rets.iloc[:i]
            if len(past)>=minobs: w=erc_weights(np.cov(past.values.T))
            else: w=None; continue
        if w is None: continue
        port.append(float(rets.loc[dt].values@w)); pi.append(dt); w=w*(1+rets.loc[dt].values); w=w/w.sum()
    return pd.Series(port,index=pd.DatetimeIndex(pi))
def nav(r): return (1+r).cumprod()
def cagr(r): return nav(r).iloc[-1]**(12/len(r))-1
def vol(r): return r.std()*np.sqrt(12)
def mdd(r): n=nav(r); return (n/n.cummax()-1).min()
def sharpe(r): return r.mean()*12/(r.std()*np.sqrt(12))
def sortino(r): d=r[r<0].std()*np.sqrt(12); return r.mean()*12/d
def calmar(r): return cagr(r)/abs(mdd(r))
def metrics(r): return {"cagr":cagr(r),"vol":vol(r),"mdd":mdd(r),"sharpe":sharpe(r),
    "sortino":sortino(r),"calmar":calmar(r),"mult":float(nav(r).iloc[-1]),"n_mesi":len(r),
    "start":str(r.index[0].date()),"end":str(r.index[-1].date())}
def rolling_cagr(r,years,step=3):
    L=years*12; out={}
    for i in range(0,len(r)-L+1,step): out[r.index[i]]=(1+r.iloc[i:i+L]).prod()**(12/L)-1
    return pd.Series(out)
def winrate(rp,rb,years,step=3):
    L=years*12; wins=tot=0
    for i in range(0,len(rp)-L+1,step):
        s=rb.reindex(rp.index).iloc[i:i+L]
        if s.isna().any(): continue
        wins+=(1+rp.iloc[i:i+L]).prod()>(1+s).prod(); tot+=1
    return (wins/tot if tot else float("nan")), tot
def montecarlo(r,horizons=(10,20,30),n=10000,block=3):
    v=r.values; N=len(v); res={}
    for H in horizons:
        M=H*12; term=np.empty(n)
        for p in range(n):
            seq=[]
            while len(seq)<M:
                st=np.random.randint(0,N-block); seq.extend(v[st:st+block])
            term[p]=np.prod(1+np.array(seq[:M]))
        ann=term**(1/H)-1
        res[H]={"mult_p5":float(np.percentile(term,5)),"mult_med":float(np.percentile(term,50)),
                "mult_p95":float(np.percentile(term,95)),"ann_med":float(np.percentile(ann,50)),
                "p_loss":float((term<1).mean())}
    return res

ew=bt_fixed(rf,[.2]*5); erc=bt_erc(rf)
# finestra principale EW = tutto (dal 1998-12); benchmark allineati
ewC=ew.index.intersection(spx.index).intersection(wld.index)
EW=ew.reindex(ewC).dropna(); SPX=spx.reindex(ewC).dropna(); WLD=wld.reindex(ewC).dropna()
# finestra comune per confronto EW vs ERC (ERC parte 36m dopo)
ercC=erc.index.intersection(ew.index).intersection(spx.index).intersection(wld.index)
EWc=ew.reindex(ercC).dropna(); ERCc=erc.reindex(ercC).dropna()
erc_w=erc_weights(np.cov(rf.values.T))

summary={"meta":{"assets":ASSETS,"currency":"USD","return":"total return lordo","rebalance":"annuale",
  "window_ew":f"{str(EW.index.min().date())} -> {str(EW.index.max().date())}",
  "window_erc":f"{str(ERCc.index.min().date())} -> {str(ERCc.index.max().date())}",
  "fonti":"oro mensile 1985, Treasury20 TR sintetico da FRED DGS20, Nasdaq Composite+0.75%/anno, XLF, XLE"},
 "weights":{"equal":[0.2]*5,"erc":[round(float(x),3) for x in erc_w]},
 "full_period":{"equal_weight":metrics(EW),"sp500":metrics(SPX),"msci_world":metrics(WLD)},
 "ew_vs_erc":{"equal_weight":metrics(EWc),"risk_parity":metrics(ERCc)},
 "rolling":{},"montecarlo":{"equal_weight":montecarlo(EW),"sp500":montecarlo(SPX)}}
for yr in [5,10,20]:
    ws,ns=winrate(EW,SPX,yr); ww,nw=winrate(EW,WLD,yr); rc=rolling_cagr(EW,yr)
    summary["rolling"][f"{yr}y"]={"ew_win_sp":ws,"ew_win_world":ww,"n":ns,
        "cagr_med":float(rc.median()),"cagr_p5":float(rc.quantile(.05)),"cagr_p95":float(rc.quantile(.95))}
# --- 6+1 metriche su FINESTRE MOBILI (base del verdetto) ---
def rolling_metrics(r,years,step=3):
    L=years*12; rows={}
    for i in range(0,len(r)-L+1,step):
        seg=r.iloc[i:i+L]
        rows[r.index[i]]={"cagr":cagr(seg),"vol":vol(seg),"mdd":mdd(seg),"sharpe":sharpe(seg),
                          "sortino":sortino(seg),"calmar":calmar(seg)}
    return pd.DataFrame(rows).T
def rolling_6plus1(rp,rbS,rbW,years):
    P=rolling_metrics(rp,years); S=rolling_metrics(rbS.reindex(rp.index).dropna(),years); W=rolling_metrics(rbW.reindex(rp.index).dropna(),years)
    idx=P.index.intersection(S.index).intersection(W.index); P,S,W=P.loc[idx],S.loc[idx],W.loc[idx]
    better={"cagr":1,"sharpe":1,"sortino":1,"calmar":1,"vol":-1,"mdd":1}  # mdd: piu' alto (meno negativo)=meglio
    out={"n":int(len(idx)),"median":{},"win_vs_sp":{},"win_vs_world":{}}
    for m,dirn in better.items():
        out["median"][m]={"port":float(P[m].median()),"sp500":float(S[m].median()),"world":float(W[m].median())}
        if dirn>0:
            out["win_vs_sp"][m]=float((P[m]>S[m]).mean()); out["win_vs_world"][m]=float((P[m]>W[m]).mean())
        else:
            out["win_vs_sp"][m]=float((P[m]<S[m]).mean()); out["win_vs_world"][m]=float((P[m]<W[m]).mean())
    return out
summary["rolling6plus1"]={f"{yr}y":rolling_6plus1(EW,spx,wld,yr) for yr in [5,10]}
json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)

# ===== GRAFICI =====
def savefig(fig,name): fig.tight_layout(); fig.savefig(os.path.join(OUT,name)); plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,4.6)); x=np.arange(5)
ax.bar(x-0.2,[0.2]*5,0.4,label="Equal weight (principale)",color=TEAL)
ax.bar(x+0.2,erc_w,0.4,label="Risk parity (approfondimento)",color=NAVY)
ax.set_xticks(x); ax.set_xticklabels(ASSETS,rotation=20,ha="right"); ax.set_ylabel("peso")
ax.set_title("Come pesare i 5 asset: equal weight vs risk parity",fontweight="bold"); ax.legend(fontsize=9); savefig(fig,"01_pesi.png")

fig,ax=plt.subplots(figsize=(10,5.2))
for r,lab,c in [(EW,"Portafoglio decorrelato (equal weight)",TEAL),(SPX,"S&P 500",GOLD),(WLD,"MSCI World",GREY)]:
    n=nav(r); ax.plot(n.index,n.values,label=lab,color=c,lw=2)
ax.set_yscale("log"); ax.set_title("Crescita di 1$ dal 1999 (scala log, USD total return)",fontweight="bold")
ax.legend(fontsize=9); savefig(fig,"02_equity_curve.png")

fig,ax=plt.subplots(figsize=(9,5)); data=[rolling_cagr(r,10).values*100 for r in [EW,SPX,WLD]]
bp=ax.boxplot(data,tick_labels=["Portafoglio","S&P 500","MSCI World"],patch_artist=True)
for patch,c in zip(bp["boxes"],[TEAL,GOLD,GREY]): patch.set_facecolor(c); patch.set_alpha(.7)
ax.axhline(0,color=RED,lw=.8,ls="--"); ax.set_ylabel("CAGR rolling 10 anni (%)")
ax.set_title("Rendimento annualizzato — finestre mobili di 10 anni",fontweight="bold"); savefig(fig,"03_rolling10y.png")

fig,ax=plt.subplots(figsize=(10,4.6))
for r,lab,c in [(EW,"Portafoglio decorrelato",TEAL),(SPX,"S&P 500",GOLD),(WLD,"MSCI World",GREY)]:
    n=nav(r); dd=(n/n.cummax()-1)*100; ax.plot(dd.index,dd.values,label=lab,color=c,lw=1.4)
ax.set_ylabel("drawdown (%)"); ax.set_title("Perdite dai massimi dal 1999 (underwater)",fontweight="bold")
ax.legend(fontsize=9); savefig(fig,"04_drawdown.png")

fig,ax=plt.subplots(figsize=(8.5,6))
for a in ASSETS:
    rr=lvl[a].pct_change().reindex(EW.index).dropna()
    ax.scatter(vol(rr)*100,cagr(rr)*100,color=GREY,s=70,zorder=3)
    ax.annotate(a,(vol(rr)*100,cagr(rr)*100),fontsize=8,xytext=(4,4),textcoords="offset points")
for r,lab,c in [(EW,"Portafoglio (EW)",TEAL),(ERCc,"Portafoglio (risk parity)",NAVY),(SPX,"S&P 500",GOLD),(WLD,"MSCI World","#111827")]:
    ax.scatter(vol(r)*100,cagr(r)*100,color=c,s=90,zorder=4)
    ax.annotate(lab,(vol(r)*100,cagr(r)*100),fontsize=8,fontweight="bold",xytext=(4,4),textcoords="offset points")
ax.set_xlabel("Volatilità annua (%)"); ax.set_ylabel("CAGR (%)")
ax.set_title("Rischio vs rendimento (dal 1999)",fontweight="bold"); savefig(fig,"05_risk_return.png")

fig,ax=plt.subplots(figsize=(9,5))
mcE=summary["montecarlo"]["equal_weight"][20]; mcS=summary["montecarlo"]["sp500"][20]; x=np.arange(3)
ax.bar(x-0.2,[mcE["mult_p5"],mcE["mult_med"],mcE["mult_p95"]],0.4,label="Portafoglio",color=TEAL)
ax.bar(x+0.2,[mcS["mult_p5"],mcS["mult_med"],mcS["mult_p95"]],0.4,label="S&P 500",color=GOLD)
ax.set_xticks(x); ax.set_xticklabels(["sfortuna (p5)","mediana","fortuna (p95)"]); ax.set_ylabel("multiplo del capitale (20 anni)")
ax.set_title("Monte Carlo a 20 anni: quanto diventa 1$",fontweight="bold"); ax.legend(); savefig(fig,"06_montecarlo.png")

R=pd.DataFrame({a:lvl[a].pct_change() for a in ASSETS}).dropna().corr()
fig,ax=plt.subplots(figsize=(6.2,5.2)); im=ax.imshow(R.values,cmap="RdBu_r",vmin=-1,vmax=1)
ax.set_xticks(range(5)); ax.set_xticklabels(ASSETS,rotation=35,ha="right",fontsize=9)
ax.set_yticks(range(5)); ax.set_yticklabels(ASSETS,fontsize=9)
for i in range(5):
    for j in range(5): ax.text(j,i,f"{R.values[i,j]:.2f}",ha="center",va="center",fontsize=8.5,color="white" if abs(R.values[i,j])>0.5 else "black")
ax.set_title("Correlazione tra gli asset (rendimenti mensili)",fontweight="bold"); fig.colorbar(im,fraction=0.046,pad=0.04); savefig(fig,"07_correlazioni.png")

print("FATTO. EW:",summary["meta"]["window_ew"],"| ERC:",summary["meta"]["window_erc"])
print("EW  :",{k:round(v,3) for k,v in summary["full_period"]["equal_weight"].items() if isinstance(v,float)})
print("SP500:",{k:round(v,3) for k,v in summary["full_period"]["sp500"].items() if isinstance(v,float)})
print("World:",{k:round(v,3) for k,v in summary["full_period"]["msci_world"].items() if isinstance(v,float)})
print("EWvsERC:",{kk:{k:round(v,3) for k,v in vv.items() if isinstance(v,float)} for kk,vv in summary["ew_vs_erc"].items()})
print("rolling:",json.dumps(summary["rolling"],ensure_ascii=False))
print("MC EW:",summary["montecarlo"]["equal_weight"])
print("weights ERC:",dict(zip(ASSETS,summary["weights"]["erc"])))
