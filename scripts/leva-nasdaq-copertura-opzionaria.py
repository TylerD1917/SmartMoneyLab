"""
Quanto rende un portafoglio a leva sul Nasdaq con copertura tattica opzionaria?
STRATEGIA PROTAGONISTA (2x cash 2x):
  - 95% ETF 2x sintetico sul Nasdaq (Composite dal 1975; in pratica ETF a leva sul Nasdaq-100).
  - 5% put OTM 1y (strike 0.875*spot).
  - Trigger: se la put vale >= 2x il premio -> vendo, PROVENTI IN LIQUIDITA' (de-risking), ricopro.
  - Roll annuale alla scadenza.
Ipotesi PRUDENTI: IV = vol realizzata 252g + 5pp; slippage 3% sulle opzioni;
  ETF: TER 0.95% + finanziamento su (leva-1) a (FEDFUNDS + 0.5%). Lordo + Netto Italia 26%.
Confronti: 2x+put hold, 3x cash 2x, 2x nudo, Nasdaq 1x TR. Rolling 10/15/20 anni step 6 mesi.
Output: public/charts/leva-nasdaq-copertura-opzionaria/*.png + summary.json + equity_full.csv
"""
import os, math, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","leva-nasdaq-copertura-opzionaria"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

DAYS=252; Q_DIV=0.006; TAX=0.26
STRIKE_OTM=0.125; IV_PREM=0.05; SLIP=0.03; TER=0.0095; FIN_SPREAD=0.005

def Ncdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def bs_put(s,k,r,q,sig,T):
    if T<=1e-6 or sig<=1e-6: return max(k-s,0.0)
    srt=sig*math.sqrt(T); d1=(math.log(s/k)+(r-q+0.5*sig*sig)*T)/srt; d2=d1-srt
    return k*math.exp(-r*T)*Ncdf(-d2)-s*math.exp(-q*T)*Ncdf(-d1)

def load(path, lev):
    df=pd.read_csv(path); dcol=[c for c in df.columns if c.lower() in("date","observation_date")][0]
    ccol=[c for c in df.columns if c.lower()=="close"][0]
    df=df[[dcol,ccol]].rename(columns={dcol:"date",ccol:"S"}).dropna()
    df["date"]=pd.to_datetime(df["date"]); df=df.sort_values("date").reset_index(drop=True)
    ff=pd.read_csv(os.path.join(ROOT,"data","cache","FEDFUNDS.csv"),parse_dates=["observation_date"])
    ff.columns=["date","ff"]; df=pd.merge_asof(df,ff.sort_values("date"),on="date")
    S=df.S.values; rate=(df.ff/100).values
    ret=np.zeros(len(S)); ret[1:]=S[1:]/S[:-1]-1; tr=ret+Q_DIV/DAYS
    logr=np.zeros(len(S)); logr[1:]=np.log(S[1:]/S[:-1])
    rv=pd.Series(logr).rolling(DAYS,min_periods=60).std().values*math.sqrt(DAYS)
    rv=pd.Series(rv).bfill().fillna(0.30).values
    etf=1+lev*tr-(lev-1)*(rate+FIN_SPREAD)/DAYS-TER/DAYS; etf[0]=1.0
    return dict(S=S,rate=rate,rv=rv,tr=tr,etf=etf,date=df.date.values)

def run(D,i0,i1,*,trigger,reinvest,tax_on,cash_yield=0.025,C0=10000.0):
    # cash_yield: tasso annuo sulla liquidita' in eccesso. Base = 2.5% fisso (prudenziale/plausibile).
    #             Passa None per usare il tasso a breve reale (FEDFUNDS).
    S,rate,rv,etf3x=D["S"],D["rate"],D["rv"],D["etf"]
    etf=0.95*C0; basis=0.95*C0; cash=0.0; loss=[0.0]
    def realize(g):
        nonlocal cash
        if not tax_on: return
        if g>=0:
            t=max(0.0,g-loss[0]); loss[0]=max(0.0,loss[0]-g); cash-=TAX*t
        else: loss[0]+=-g
    def openput(budget,i):
        pp=bs_put(S[i],(1-STRIKE_OTM)*S[i],rate[i],Q_DIV,rv[i]+IV_PREM,1.0)
        return {"u":budget/(pp*(1+SLIP)),"K":(1-STRIKE_OTM)*S[i],"prem":budget,"exp":i+DAYS}
    put=openput(0.05*C0,i0); vals=[etf+put["prem"]]
    for i in range(i0+1,i1+1):
        cy=rate[i] if cash_yield is None else cash_yield
        etf*=etf3x[i]; cash*=(1+cy/DAYS)
        Trem=(put["exp"]-i)/DAYS
        pmtm=put["u"]*bs_put(S[i],put["K"],rate[i],Q_DIV,rv[i]+IV_PREM,max(Trem,0.0))
        payoff=None; kind=None
        if i>=put["exp"]: payoff=put["u"]*max(put["K"]-S[i],0.0); kind="exp"
        elif trigger and pmtm>=trigger*put["prem"]: kind="trig"
        if kind:
            if payoff is not None: cash+=payoff; realize(payoff-put["prem"])
            else: proc=pmtm*(1-SLIP); cash+=proc; realize(proc-put["prem"])
            total=etf+cash
            if kind=="trig" and reinvest=="cash":
                b=min(cash,0.05*total); cash-=b; put=openput(b,i); put["prem"]=b
            else:
                tgt=0.95*total
                if etf<tgt: a=tgt-etf; cash-=a; etf+=a; basis+=a
                else: a=etf-tgt; f=a/etf; realize(f*(etf-basis)); basis-=f*basis; etf-=a; cash+=a
                b=min(cash,0.05*total); cash-=b; put=openput(b,i); put["prem"]=b
            pmtm=put["prem"]
        vals.append(etf+pmtm+cash)
    if tax_on:
        realize(etf-basis); Trem=(put["exp"]-i1)/DAYS
        pend=put["u"]*bs_put(S[i1],put["K"],rate[i1],Q_DIV,rv[i1]+IV_PREM,max(Trem,0.0))*(1-SLIP)
        realize(pend-put["prem"]); vals[-1]=etf+pend+cash
    return np.array(vals)

def bh(D,i0,i1,lev_series,tax_on,C0=10000.0):
    r=D["etf"] if lev_series else (1+D["tr"])
    v=C0*np.cumprod(np.concatenate([[1.0],r[i0+1:i1+1]]))
    if tax_on and v[-1]>C0: v=v.copy(); v[-1]=C0+(v[-1]-C0)*(1-TAX)
    return v

def metrics(v,rf):
    n=len(v)-1; yrs=n/DAYS; cg=(v[-1]/v[0])**(1/yrs)-1
    r=v[1:]/v[:-1]-1; vol=np.std(r)*math.sqrt(DAYS)
    md=float(np.min(v/np.maximum.accumulate(v)-1))
    exc=np.mean(r)*DAYS-rf
    dd=np.std(np.minimum(r,0))*math.sqrt(DAYS)
    return dict(cagr=cg,vol=vol,mdd=md,sharpe=exc/vol if vol>0 else 0,
                calmar=cg/abs(md) if md<0 else 0,sortino=exc/dd if dd>0 else 0,mult=v[-1]/v[0])

CMP2=load(os.path.join(ROOT,"data","raw","Nasdaq_historical.csv"),2)
CMP3=load(os.path.join(ROOT,"data","raw","Nasdaq_historical.csv"),3)
i0=int(np.argmax(CMP2["rv"]>0)); iN=len(CMP2["S"])-1
rf_all=float(np.mean(CMP2["rate"][i0:iN]))
print(f"Periodo: {pd.Timestamp(CMP2['date'][i0]).date()} -> {pd.Timestamp(CMP2['date'][iN]).date()}  ({(iN-i0)/DAYS:.0f} anni)")

# strategie
def strat_2xcash(D,a,b,tax): return run(D,a,b,trigger=2.0,reinvest="cash",tax_on=tax)
STR={"2x cash 2x (strategia)":(CMP2,lambda a,b,t:run(CMP2,a,b,trigger=2.0,reinvest="cash",tax_on=t)),
     "2x + put (hold)":(CMP2,lambda a,b,t:run(CMP2,a,b,trigger=None,reinvest="cash",tax_on=t)),
     "3x cash 2x":(CMP3,lambda a,b,t:run(CMP3,a,b,trigger=2.0,reinvest="cash",tax_on=t)),
     "Nasdaq 1x TR":(CMP2,lambda a,b,t:bh(CMP2,a,b,False,t)),
     "2x nudo":(CMP2,lambda a,b,t:bh(CMP2,a,b,True,t))}

# ---- FULL PERIOD (lordo) + equity csv ----
print("\n== FULL PERIOD (lordo) ==")
eq={}
for name,(D,fn) in STR.items():
    v=fn(i0,iN,False); eq[name]=v; m=metrics(v,rf_all)
    print(f"  {name:24s} CAGR {m['cagr']*100:6.1f}%  vol {m['vol']*100:5.1f}%  MDD {m['mdd']*100:6.1f}%  Calmar {m['calmar']:.2f}  x {m['mult']:.0f}")
pd.DataFrame({"date":pd.to_datetime(CMP2["date"][i0:iN+1]),**{k:v for k,v in eq.items()}}).to_csv(os.path.join(OUT,"equity_full.csv"),index=False)

# ---- ROLLING 6+1 (netto) ----
summary={"period":[str(pd.Timestamp(CMP2['date'][i0]).date()),str(pd.Timestamp(CMP2['date'][iN]).date())],"rolling":{}}
roll_cagr={}  # per chart
for W_years in (10,15,20):
    W=W_years*DAYS; step=DAYS//2; starts=list(range(i0,iN-W,step))
    summary["rolling"][W_years]={"n":len(starts),"metrics":{},"winrate_vs_1x":{}}
    perwin={}
    for name,(D,fn) in STR.items():
        rows=[metrics(fn(s,s+W,True),float(np.mean(D["rate"][s:s+W]))) for s in starts]
        perwin[name]=rows
        agg={k:float(np.median([r[k] for r in rows])) for k in ("cagr","vol","mdd","sharpe","calmar","sortino")}
        summary["rolling"][W_years]["metrics"][name]=agg
    base1x=[r["cagr"] for r in perwin["Nasdaq 1x TR"]]
    for name in STR:
        wr=float(np.mean([perwin[name][j]["cagr"]>base1x[j] for j in range(len(starts))]))
        summary["rolling"][W_years]["winrate_vs_1x"][name]=wr
    roll_cagr[W_years]={name:[r["cagr"] for r in perwin[name]] for name in STR}
    print(f"\n== ROLLING {W_years}y NETTO (mediana 6+1, n={len(starts)}) ==")
    print(f"  {'':24s}{'CAGR':>7s}{'vol':>7s}{'MDD':>8s}{'Sharpe':>8s}{'Calmar':>8s}{'Sortino':>8s}{'win%':>7s}")
    for name in STR:
        m=summary["rolling"][W_years]["metrics"][name]; wr=summary["rolling"][W_years]["winrate_vs_1x"][name]
        print(f"  {name:24s}{m['cagr']*100:6.1f}%{m['vol']*100:6.1f}%{m['mdd']*100:7.1f}%{m['sharpe']:8.2f}{m['calmar']:8.2f}{m['sortino']:8.2f}{wr*100:6.0f}%")

json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2,ensure_ascii=False)

# ================= GRAFICI =================
order=["Nasdaq 1x TR","2x + put (hold)","2x cash 2x (strategia)","3x cash 2x"]
cols={"Nasdaq 1x TR":GREY,"2x + put (hold)":NAVY,"2x cash 2x (strategia)":GOLD,"3x cash 2x":RED,"2x nudo":"#a3b8e0"}

# 1) equity full period (log)
fig,ax=plt.subplots(figsize=(10,5.5)); x=pd.to_datetime(CMP2["date"][i0:iN+1])
for name in ["Nasdaq 1x TR","2x nudo","2x cash 2x (strategia)","3x cash 2x"]:
    ax.plot(x,eq[name],color=cols[name],lw=2 if "strategia" in name else 1.6,label=name)
ax.set_yscale("log"); ax.set_ylabel("Crescita di 10.000$ (lordo, scala log)")
ax.set_title("Nasdaq a leva con copertura tattica vs Nasdaq semplice\n(1975-2026, lordo)",fontsize=13,weight="bold")
ax.legend(fontsize=10); fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_equity_full.png")); plt.close(fig)

# 2) CAGR mediana rolling per orizzonte (netto)
fig,ax=plt.subplots(figsize=(10,5.5)); hz=[10,15,20]; xp=np.arange(len(hz)); w=0.2
for k,name in enumerate(order):
    vals=[summary["rolling"][h]["metrics"][name]["cagr"]*100 for h in hz]
    ax.bar(xp+(k-1.5)*w,vals,w,label=name,color=cols[name])
ax.set_xticks(xp); ax.set_xticklabels([f"{h} anni" for h in hz]); ax.yaxis.set_major_formatter(PercentFormatter())
ax.set_ylabel("CAGR mediano (netto Italia)"); ax.set_title("Rendimento per orizzonte: la leva coperta batte il Nasdaq sul CAGR",fontsize=12,weight="bold")
ax.legend(fontsize=9); fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_cagr_rolling.png")); plt.close(fig)

# 3) distribuzione MDD rolling 15y: strategia vs 1x
fig,ax=plt.subplots(figsize=(9,5))
data=[np.array(roll_cagr[15]["Nasdaq 1x TR"]) , ]  # placeholder to keep var; use metrics per-window MDD instead
# ricostruisco MDD per boxplot
W=15*DAYS; step=DAYS//2; starts=list(range(i0,iN-W,step))
mdd_str=[metrics(run(CMP2,s,s+W,trigger=2.0,reinvest="cash",tax_on=True),0)["mdd"]*100 for s in starts]
mdd_1x=[metrics(bh(CMP2,s,s+W,False,True),0)["mdd"]*100 for s in starts]
ax.boxplot([mdd_1x,mdd_str],labels=["Nasdaq 1x","2x cash 2x"],vert=True,patch_artist=True,
           boxprops=dict(facecolor="#dbeafe"),medianprops=dict(color=NAVY,lw=2))
ax.set_ylabel("Max drawdown, finestre 15 anni (%)"); ax.axhline(0,color=INK,lw=0.8)
ax.set_title("Il prezzo da pagare: drawdown molto più profondi della strategia",fontsize=12,weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_mdd_box.png")); plt.close(fig)

# 4) distribuzione dei rendimenti rolling: strategia vs Nasdaq (onesta: mediana + code)
from matplotlib.patches import Patch
fig,ax=plt.subplots(figsize=(9.5,5.5)); data=[]; pos=[]; fc=[]
for k,h in enumerate((10,15,20)):
    data.append(np.array(roll_cagr[h]["Nasdaq 1x TR"])*100); pos.append(k*3+1); fc.append(GREY)
    data.append(np.array(roll_cagr[h]["2x cash 2x (strategia)"])*100); pos.append(k*3+2); fc.append(GOLD)
bp=ax.boxplot(data,positions=pos,widths=0.8,patch_artist=True,showfliers=False,medianprops=dict(color=INK,lw=2))
for patch,c in zip(bp["boxes"],fc): patch.set_facecolor(c)
ax.axhline(0,color=RED,lw=0.9,ls=":")
ax.set_xticks([1.5,4.5,7.5]); ax.set_xticklabels(["10 anni","15 anni","20 anni"])
ax.yaxis.set_major_formatter(PercentFormatter()); ax.set_ylabel("CAGR annuo (netto), finestre mobili")
ax.set_title("Distribuzione dei rendimenti: mediana più alta della strategia,\nma coda inferiore più lunga (il rischio della leva)",fontsize=12,weight="bold")
ax.legend(handles=[Patch(facecolor=GREY,label="Nasdaq 1x"),Patch(facecolor=GOLD,label="Strategia 2x + copertura")],fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"04_distribuzione_cagr.png")); plt.close(fig)

print("\n[ok] summary.json + equity_full.csv + 4 grafici in", OUT)
