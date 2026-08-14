"""
Confronto varianti strategia 3x Nasdaq + copertura put + riconciliazione col setup originale di Tyler.
Motore parametrico: trigger (o hold-to-expiry), reinvest proventi (etf3x vs cash), IV, strike, costi.
"""
import os, math
import numpy as np, pandas as pd
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
DAYS=252; Q_DIV=0.006; TAX=0.26

def N(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def bs_put(s,k,r,q,sig,T):
    if T<=1e-6 or sig<=1e-6: return max(k-s,0.0)
    srt=sig*math.sqrt(T); d1=(math.log(s/k)+(r-q+0.5*sig*sig)*T)/srt; d2=d1-srt
    return k*math.exp(-r*T)*N(-d2)-s*math.exp(-q*T)*N(-d1)

def load(path, close_col, rate_const=None, ter=0.0095, borrow=None, fin_spread=0.005, lev=3):
    df=pd.read_csv(path);
    dcol=[c for c in df.columns if c.lower() in ("date","observation_date")][0]
    df=df[[dcol,close_col]].rename(columns={dcol:"date",close_col:"S"}).dropna()
    df["date"]=pd.to_datetime(df["date"]); df=df.sort_values("date").reset_index(drop=True)
    S=df.S.values; ret=np.zeros(len(S)); ret[1:]=S[1:]/S[:-1]-1
    if rate_const is not None:
        rate=np.full(len(S),rate_const)
    else:
        ff=pd.read_csv(os.path.join(ROOT,"data","cache","FEDFUNDS.csv"),parse_dates=["observation_date"])
        ff.columns=["date","ff"]; df=pd.merge_asof(df,ff.sort_values("date"),on="date"); rate=(df.ff/100).values
    logr=np.zeros(len(S)); logr[1:]=np.log(S[1:]/S[:-1])
    rv=pd.Series(logr).rolling(DAYS,min_periods=60).std().values*math.sqrt(DAYS)
    rv=pd.Series(rv).bfill().fillna(0.30).values
    tr=ret+Q_DIV/DAYS
    b=borrow if borrow is not None else None
    if b is not None: etf=1+lev*tr-(lev-1)*(b/DAYS)-ter/DAYS
    else: etf=1+lev*tr-(lev-1)*(rate+fin_spread)/DAYS-ter/DAYS
    etf[0]=1.0
    return dict(S=S,rate=rate,rv=rv,tr=tr,etf=etf,date=df.date.values)

def run(D,i0,i1,*,strike_otm,iv_prem,slip,trigger,reinvest,tax_on,r_fixed=None,C0=10000.0):
    S,rate,rv,etf3x=D["S"],D["rate"],D["rv"],D["etf"]
    def rr(i): return r_fixed if r_fixed is not None else rate[i]
    etf=0.95*C0; basis=0.95*C0; cash=0.0; loss=[0.0]
    def realize(g):
        if not tax_on: return
        if g>=0:
            t=max(0.0,g-loss[0]); loss[0]=max(0.0,loss[0]-g);
            nonlocal_sub(t*TAX)
        else: loss[0]+=-g
    def nonlocal_sub(x):
        nonlocal cash; cash-=x
    def openput(budget,i):
        pp=bs_put(S[i],(1-strike_otm)*S[i],rr(i),Q_DIV,rv[i]+iv_prem,1.0)
        return {"u":budget/(pp*(1+slip)),"K":(1-strike_otm)*S[i],"prem":budget,"exp":i+DAYS}
    put=openput(0.05*C0,i0); vals=[etf+put["prem"]]
    for i in range(i0+1,i1+1):
        etf*=etf3x[i]; cash*=(1+rr(i)/DAYS)
        Trem=(put["exp"]-i)/DAYS
        pmtm=put["u"]*bs_put(S[i],put["K"],rr(i),Q_DIV,rv[i]+iv_prem,max(Trem,0.0))
        payoff=None; kind=None
        if i>=put["exp"]: payoff=put["u"]*max(put["K"]-S[i],0.0); kind="exp"
        elif trigger and pmtm>=trigger*put["prem"]: kind="trig"
        if kind:
            if payoff is not None: cash+=payoff; realize(payoff-put["prem"])
            else: proc=pmtm*(1-slip); cash+=proc; realize(proc-put["prem"])
            if kind=="trig" and reinvest=="cash":
                total=etf+cash; b=min(cash,0.05*total); cash-=b; put=openput(b,i); put["prem"]=b
            else:
                total=etf+cash; tgt=0.95*total
                if etf<tgt: a=tgt-etf; cash-=a; etf+=a; basis+=a
                else: a=etf-tgt; f=a/etf; realize(f*(etf-basis)); basis-=f*basis; etf-=a; cash+=a
                b=min(cash,0.05*total); cash-=b; put=openput(b,i); put["prem"]=b
            pmtm=put["prem"]
        vals.append(etf+pmtm+cash)
    if tax_on:
        realize(etf-basis)
        Trem=(put["exp"]-i1)/DAYS
        pend=put["u"]*bs_put(S[i1],put["K"],rr(i1),Q_DIV,rv[i1]+iv_prem,max(Trem,0.0))*(1-slip)
        realize(pend-put["prem"]); vals[-1]=etf+pend+cash
    return np.array(vals)

def bh(D,i0,i1,which,tax_on,C0=10000.0):
    r=D["etf"] if which=="3x" else (1+D["tr"])
    v=C0*np.cumprod(np.concatenate([[1.0],r[i0+1:i1+1]]))
    if tax_on and v[-1]>C0: v=v.copy(); v[-1]=C0+(v[-1]-C0)*(1-TAX)
    return v

def cagr(v,n=None):
    n=n or (len(v)-1); return (v[-1]/v[0])**(DAYS/n)-1
def mdd(v): return float(np.min(v/np.maximum.accumulate(v)-1))
def idx(D,ds): t=pd.Timestamp(ds); return int(np.argmin(np.abs(pd.to_datetime(D["date"])-t)))

# ---------- 1) RICONCILIAZIONE setup Tyler (Composite 1975, hold, IV realized, borrow 3.5% fisso, strike -15%) ----------
CMP=load(os.path.join(ROOT,"data","raw","Nasdaq_historical.csv"),"Close",rate_const=0.035,ter=0.009,borrow=0.035)
print("=== RICONCILIAZIONE setup originale (Composite, hold-to-expiry, IV=realized, -15%, no tax) ===")
res=[]
y0=pd.Timestamp(CMP["date"][0]).year; yN=pd.Timestamp(CMP["date"][-1]).year
for y in range(y0, yN-14):
    a=idx(CMP,f"{y}-01-01"); b=idx(CMP,f"{y+15}-01-01")
    if b-a < 14*DAYS: continue
    v=run(CMP,a,b,strike_otm=0.15,iv_prem=0.0,slip=0.0,trigger=None,reinvest="etf3x",tax_on=False,r_fixed=0.035)
    res.append(cagr(v,b-a))
print(f"  finestre 15y: {len(res)}  |  CAGR medio: {np.mean(res)*100:.1f}%  mediano: {np.median(res)*100:.1f}%")

# ---------- 2) CONFRONTO LEVA 2x vs 3x — variante 'cash' (proventi in liquidita') ----------
NDXf="data/raw/Nasdaq_historical.csv"   # Nasdaq Composite dal 1975 (storia piu' lunga)
NDX2=load(os.path.join(ROOT,NDXf),"Close",lev=2)
NDX3=load(os.path.join(ROOT,NDXf),"Close",lev=3)
i0=int(np.argmax(NDX3["rv"]>0)); iN=len(NDX3["S"])-1
base=dict(strike_otm=0.125,iv_prem=0.05,slip=0.03)
cashv={"cash 2x":dict(trigger=2.0,reinvest="cash"),"cash 3x":dict(trigger=3.0,reinvest="cash"),"cash 4x":dict(trigger=4.0,reinvest="cash"),"hold":dict(trigger=None,reinvest="cash")}

print("\n=== FULL PERIOD Nasdaq-100 1990-2025 (lordo) — LEVA 2x vs 3x ===")
print(f"  {'':22s}{'CAGR':>8s}{'MDD':>9s}{'x cap':>9s}")
for tag,D in [("2x",NDX2),("3x",NDX3)]:
    for name,p in cashv.items():
        v=run(D,i0,iN,**base,tax_on=False,**p); print(f"  {tag+' '+name:22s}{cagr(v)*100:7.1f}%{mdd(v)*100:8.1f}%{v[-1]/v[0]:8.1f}x")
    nu=bh(D,i0,iN,'3x',False); print(f"  {tag+' nudo':22s}{cagr(nu)*100:7.1f}%{mdd(nu)*100:8.1f}%{nu[-1]/nu[0]:8.1f}x")
o=bh(NDX3,i0,iN,'1x',False); print(f"  {'Nasdaq 1x TR':22s}{cagr(o)*100:7.1f}%{mdd(o)*100:8.1f}%{o[-1]/o[0]:8.1f}x")

print("\n=== DOT-COM 2000->2010 (CAGR / MDD) — 2x vs 3x, cash 2x ===")
a,b=idx(NDX3,"2000-01-01"),idx(NDX3,"2010-01-01")
for tag,D in [("2x",NDX2),("3x",NDX3)]:
    v=run(D,a,b,**base,tax_on=False,trigger=2.0,reinvest="cash"); nu=bh(D,a,b,'3x',False)
    print(f"  {tag} cash 2x: {cagr(v,b-a)*100:6.1f}% / {mdd(v)*100:6.1f}%   |   {tag} nudo: {cagr(nu,b-a)*100:6.1f}% / {mdd(nu)*100:6.1f}%")

print("\n=== ROLLING NETTO Italia (mediana CAGR / mediana MDD / Calmar) ===")
for W_years in (10,15,20):
    W=W_years*DAYS; step=DAYS//2; starts=list(range(i0,iN-W,step))
    print(f"-- finestre {W_years} anni (n={len(starts)}) --")
    for tag,D in [("2x",NDX2),("3x",NDX3)]:
        for name,p in cashv.items():
            cs=[];ms=[]
            for s in starts:
                v=run(D,s,s+W,**base,tax_on=True,**p); cs.append(cagr(v,W)); ms.append(mdd(v))
            cc=np.median(cs); mm=np.median(ms)
            print(f"   {tag+' '+name:14s} CAGR {cc*100:6.1f}%  MDD {mm*100:7.1f}%  Calmar {cc/abs(mm):.2f}")
    one=[cagr(bh(NDX3,s,s+W,'1x',True),W) for s in starts]; onm=[mdd(bh(NDX3,s,s+W,'1x',True)) for s in starts]
    cc=np.median(one);mm=np.median(onm); print(f"   {'Nasdaq 1x TR':14s} CAGR {cc*100:6.1f}%  MDD {mm*100:7.1f}%  Calmar {cc/abs(mm):.2f}")
