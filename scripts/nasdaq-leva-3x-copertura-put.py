"""
Portafoglio a leva 3x sul Nasdaq-100 con copertura tattica opzionaria (put OTM 1y).
Strategia: 95% ETF 3x sintetico (NDX) + 5% put OTM (strike 0.875*spot, T=1y).
- Trigger: se la put vale >= 3x il premio pagato -> vendo, reinvesto in ETF, ricopro (reset).
- Roll annuale: alla scadenza rinnovo la put (vendo ~5% per finanziarla).
Scelte PRUDENTI (penalizzano la strategia, niente vantaggi gratis):
- IV per pricing e MTM = vol realizzata 252g + 5pp (put costose; realizzata ritarda nei crolli).
- Slippage 3% su acquisto/vendita opzioni.
- ETF 3x: TER 0.95%/anno + costo finanziamento su 2x a (FEDFUNDS + 0.5%).
Output: lordo + netto Italia 26% (con carry perdite). Benchmark: 3x nudo, NDX 1x TR.
Rolling 10 e 15 anni, step 6 mesi. Framework 6+1.

DATI (locali): data/cache/yf_proxy_ndx_nasdaq100.csv (NDX daily 1990-2025), data/cache/FEDFUNDS.csv
Esegui: python scripts/nasdaq-leva-3x-copertura-put.py
"""
import os, json, math
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","nasdaq-leva-3x-copertura-put"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"

# ---------------- Parametri ----------------
TER=0.0095; FIN_SPREAD=0.005; LEV=3.0
Q_DIV=0.006            # dividend yield NDX ~0.6%
IV_PREMIUM=0.05        # +5pp sulla vol realizzata (prudente)
SLIP=0.03              # slippage opzioni (3%)
STRIKE_K=0.875         # put OTM: strike = 0.875*spot
TRIG_MULT=3.0          # vendi la put a >=3x il premio
TAX=0.26; DAYS=252

# ---------------- Dati ----------------
ndx=pd.read_csv(os.path.join(ROOT,"data","cache","yf_proxy_ndx_nasdaq100.csv"),parse_dates=["Date"])
ndx=ndx[["Date","Close"]].rename(columns={"Date":"date","Close":"S"}).dropna().sort_values("date").reset_index(drop=True)
ff=pd.read_csv(os.path.join(ROOT,"data","cache","FEDFUNDS.csv"),parse_dates=["observation_date"])
ff.columns=["date","ff"];
ndx=pd.merge_asof(ndx,ff.sort_values("date"),on="date")   # forward-fill tasso mensile su daily
ndx["r"]=ndx.ff/100.0
S=ndx.S.values; rate=ndx.r.values; dates=ndx.date.values
ret=np.zeros(len(S)); ret[1:]=S[1:]/S[:-1]-1               # price return giornaliero NDX
tr=ret+Q_DIV/DAYS                                          # total return giornaliero (approx dividendi)
# vol realizzata 252g annualizzata
logr=np.zeros(len(S)); logr[1:]=np.log(S[1:]/S[:-1])
rv=pd.Series(logr).rolling(DAYS,min_periods=60).std().values*math.sqrt(DAYS)
rv=np.nan_to_num(rv,nan=0.30)
# ETF 3x sintetico: ratio giornaliero
etf3x_ratio=1+LEV*tr-(LEV-1)*(rate+FIN_SPREAD)/DAYS-TER/DAYS
etf3x_ratio[0]=1.0

def N(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def bs_put(s,k,r,q,sig,T):
    if T<=1e-6 or sig<=1e-6: return max(k-s,0.0)
    srt=sig*math.sqrt(T)
    d1=(math.log(s/k)+(r-q+0.5*sig*sig)*T)/srt; d2=d1-srt
    return k*math.exp(-r*T)*N(-d2)-s*math.exp(-q*T)*N(-d1)

# ---------------- Simulazione strategia (una finestra) ----------------
def run(i0,i1,tax_on,trig=TRIG_MULT,C0=10000.0):
    """Ritorna la serie giornaliera del valore portafoglio (mark-to-market)."""
    etf=0.95*C0; basis=0.95*C0; cash=0.0; loss=0.0
    def realize(gain):
        nonlocal cash,loss
        if not tax_on: return
        if gain>=0:
            g=max(0.0,gain-loss); loss=max(0.0,loss-gain); cash-=TAX*g
        else:
            loss+=-gain
    # apri put
    def open_put(budget,i):
        pp=bs_put(S[i],STRIKE_K*S[i],rate[i],Q_DIV,rv[i]+IV_PREMIUM,1.0)
        units=budget/(pp*(1+SLIP)); return {"u":units,"K":STRIKE_K*S[i],"prem":budget,"exp":i+DAYS}
    put=open_put(0.05*C0,i0); cash-=0.0  # premio gia' scorporato da etf(0.95) vs C0
    # NB: 0.95 in etf + 0.05 in put = C0
    vals=[etf+put["prem"]]  # valore iniziale ~C0 (put al costo)
    for i in range(i0+1,i1+1):
        etf*=etf3x_ratio[i]
        Trem=(put["exp"]-i)/DAYS
        pmtm=put["u"]*bs_put(S[i],put["K"],rate[i],Q_DIV,rv[i]+IV_PREMIUM,max(Trem,0.0))
        roll=False; payoff=None
        if i>=put["exp"]:                    # scadenza
            payoff=put["u"]*max(put["K"]-S[i],0.0); roll=True
        elif pmtm>=trig*put["prem"]:         # trigger a 3x
            roll=True
        if roll:
            if payoff is not None:           # scadenza: incasso intrinseco
                cash+=payoff; realize(payoff-put["prem"])
            else:                            # vendita anticipata con slippage
                proceeds=pmtm*(1-SLIP); cash+=proceeds; realize(proceeds-put["prem"])
            total=etf+cash
            tgt_etf=0.95*total
            if etf<tgt_etf:                  # compro ETF con la cassa
                amt=tgt_etf-etf; cash-=amt; etf+=amt; basis+=amt
            else:                            # vendo ETF (realizzo)
                amt=etf-tgt_etf; f=amt/etf; realize(f*(etf-basis)); basis-=f*basis; etf-=amt; cash+=amt
            put=open_put(min(cash,0.05*total),i); cash-=put["prem"]
            pmtm=put["prem"]
        vals.append(etf+pmtm+cash)
    # liquidazione finale (netto: tasso su plus non realizzate)
    if tax_on:
        realize(etf-basis)                   # chiudo ETF
        Trem=(put["exp"]-i1)/DAYS
        pend=put["u"]*bs_put(S[i1],put["K"],rate[i1],Q_DIV,rv[i1]+IV_PREMIUM,max(Trem,0.0))*(1-SLIP)
        realize(pend-put["prem"])
        vals[-1]=etf+cash+pend*(0 if False else 1)  # valore netto finale
        vals[-1]=etf+ (pend) + cash                 # etf gia' al lordo; cash include tasse pagate
    return np.array(vals)

def bh(i0,i1,ratio_arr,tax_on,C0=10000.0):
    v=C0*np.cumprod(np.concatenate([[1.0],ratio_arr[i0+1:i1+1]]))
    if tax_on:
        gain=v[-1]-C0; v=v.copy(); v[-1]=C0+gain*(1-TAX) if gain>0 else v[-1]
    return v

# ---------------- Metriche ----------------
def metrics(v):
    n=len(v)-1; yrs=n/DAYS
    cagr=(v[-1]/v[0])**(1/yrs)-1
    r=v[1:]/v[:-1]-1; vol=np.std(r)*math.sqrt(DAYS)
    mdd=np.min(v/np.maximum.accumulate(v)-1)
    sharpe=(np.mean(r)*DAYS)/vol if vol>0 else 0
    downside=np.std(np.minimum(r,0))*math.sqrt(DAYS)
    sortino=(np.mean(r)*DAYS)/downside if downside>0 else 0
    return dict(cagr=cagr,vol=vol,mdd=mdd,sharpe=sharpe,calmar=cagr/abs(mdd) if mdd<0 else 0,sortino=sortino,mult=v[-1]/v[0])

# ---------------- Run full period ----------------
i0=int(np.argmax(rv>0))  # primo indice con vol definita (~day 60)
iN=len(S)-1
print(f"Periodo simulazione: {pd.Timestamp(dates[i0]).date()} -> {pd.Timestamp(dates[iN]).date()}  ({(iN-i0)/DAYS:.1f} anni)")
sg=run(i0,iN,tax_on=False); sn=run(i0,iN,tax_on=True)
nudo=bh(i0,iN,etf3x_ratio,tax_on=False); ndx1=bh(i0,iN,1+tr,tax_on=False)
print("\n== FULL PERIOD (lordo) ==")
for name,v in [("Strategia lordo",sg),("Strategia NETTO",sn),("3x nudo",nudo),("NDX 1x TR",ndx1)]:
    m=metrics(v); print(f"  {name:16s} CAGR {m['cagr']*100:6.1f}%  vol {m['vol']*100:5.1f}%  MDD {m['mdd']*100:6.1f}%  Calmar {m['calmar']:.2f}  x {m['mult']:.1f}")

# ---------------- Rolling windows ----------------
def rolling(win_years):
    W=int(win_years*DAYS); step=DAYS//2; res={"strat_net":[],"nudo":[],"ndx1":[]}
    starts=range(i0,iN-W,step)
    for s in starts:
        e=s+W
        res["strat_net"].append(metrics(run(s,e,tax_on=True)))
        res["nudo"].append(metrics(bh(s,e,etf3x_ratio,tax_on=True)))
        res["ndx1"].append(metrics(bh(s,e,1+tr,tax_on=True)))
    return res,list(starts)

summary={"full":{k:metrics(v) for k,v in [("strat_lordo",sg),("strat_netto",sn),("nudo3x",nudo),("ndx1",ndx1)]},"rolling":{}}
for wy in (10,15):
    res,starts=rolling(wy)
    def pct(key,metric):
        a=np.array([m[metric] for m in res[key]]); return {p:float(np.percentile(a,p)) for p in (5,25,50,75,95)}
    winrate=float(np.mean([res["strat_net"][j]["cagr"]>res["nudo"][j]["cagr"] for j in range(len(starts))]))
    summary["rolling"][f"{wy}y"]={"n_windows":len(starts),
        "strat_net_cagr":pct("strat_net","cagr"),"nudo_cagr":pct("nudo","cagr"),"ndx1_cagr":pct("ndx1","cagr"),
        "strat_net_mdd":pct("strat_net","mdd"),"nudo_mdd":pct("nudo","mdd"),
        "winrate_strat_vs_nudo":winrate}
    print(f"\n== ROLLING {wy}y (net, step 6m, n={len(starts)}) ==")
    print(f"  CAGR mediana: strategia {pct('strat_net','cagr')[50]*100:.1f}%  |  3x nudo {pct('nudo','cagr')[50]*100:.1f}%  |  NDX 1x {pct('ndx1','cagr')[50]*100:.1f}%")
    print(f"  MDD mediana:  strategia {pct('strat_net','mdd')[50]*100:.1f}%  |  3x nudo {pct('nudo','mdd')[50]*100:.1f}%")
    print(f"  Win rate strategia vs 3x nudo: {winrate*100:.0f}%")

# ---------------- DIAGNOSTICA per regime ----------------
def idx(datestr):
    t=pd.Timestamp(datestr); return int(np.argmin(np.abs(pd.to_datetime(dates)-t)))
print("\n== DIAGNOSTICA per periodo (CAGR / MDD) — strategia lordo vs 3x nudo vs NDX 1x ==")
for a,b in [("1990-01-01","2000-01-01"),("2000-01-01","2010-01-01"),("2010-01-01","2020-01-01"),
            ("2010-01-01","2025-12-01"),("2003-01-01","2021-01-01"),("2019-06-01","2021-06-01")]:
    s0,s1=idx(a),idx(b)
    ms=metrics(run(s0,s1,tax_on=False)); mn=metrics(bh(s0,s1,etf3x_ratio,False)); m1=metrics(bh(s0,s1,1+tr,False))
    print(f"  {a[:7]}->{b[:7]}: strat CAGR {ms['cagr']*100:6.1f}% MDD {ms['mdd']*100:6.1f}% | nudo {mn['cagr']*100:6.1f}%/{mn['mdd']*100:6.1f}% | 1x {m1['cagr']*100:5.1f}%/{m1['mdd']*100:6.1f}%")

json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),indent=2)
pd.DataFrame({"date":pd.to_datetime(dates[i0:iN+1]),"strat_lordo":sg,"strat_netto":sn,"nudo3x":nudo,"ndx1":ndx1}).to_csv(os.path.join(OUT,"equity_full.csv"),index=False)
print("\n[ok] summary.json + equity_full.csv salvati in", OUT)
