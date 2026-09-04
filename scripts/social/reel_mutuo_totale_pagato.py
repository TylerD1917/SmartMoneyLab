"""Reel mutuo: totale pagato (capitale+interessi) a passi di 6 mesi, per una coorte
di accensione. Tre curve: variabile, fisso, fisso-con-surroga (surroga contro il
tasso fisso di mercato REALE: scatta solo se in quella finestra c'era l'occasione).
Riusa ingest/amortize/annuity dall'articolo."""
import sys, argparse, importlib.util
import numpy as np, pandas as pd
spec = importlib.util.spec_from_file_location("mfv", "scripts/mutuo-fisso-o-variabile.py")
mfv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mfv)
L, N, RESET_M = mfv.L, mfv.N, mfv.RESET_M
SUR_THR, SUR_EVERY = 0.0075, 12

def surroga_pays(eur, fis, t0, fixed0, h):
    """paga contro il fisso di MERCATO reale (serie MIR fisso). Ritorna pays[h], n_sur."""
    bal=L; cur=fixed0; pay=mfv.annuity(bal, cur/12, N); pays=np.zeros(h); n=0
    fseries = fis.loc[t0:].iloc[:h].values
    for t in range(h):
        if t>0 and t%SUR_EVERY==0 and not np.isnan(fseries[t]):
            if fseries[t] <= cur - SUR_THR:
                cur=fseries[t]; pay=mfv.annuity(bal, cur/12, N-t); n+=1
        r=cur/12; interest=bal*r; principal=pay-interest
        if t==N-1 or principal>bal: principal=bal; pay=interest+principal
        bal-=principal; pays[t]=pay
        if bal<=1e-6: break
    return pays, n

def build(df, orig):
    e,f,v = df["euribor3m"], df["fisso"], df["variabile"]
    t0=pd.Timestamp(orig)
    fixed=f.loc[t0]; spread_v=v.loc[t0]-e.loc[t0]
    fut=e.loc[t0:].iloc[:N]; h=len(fut)
    var_path=fut.values+spread_v
    _,pv,_,_=mfv.amortize(var_path, reset_m=RESET_M, term=N)
    pay_f=mfv.annuity(L,fixed/12,N); pf=np.full(h,pay_f)
    ps,nsur=surroga_pays(e,f,t0,fixed,h)
    cum=lambda p: np.cumsum(p[:h])
    return t0,fixed,v.loc[t0],h,nsur,cum(pv),cum(pf),cum(ps)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scan",action="store_true")
    ap.add_argument("--orig",default="2008-10-01")
    ap.add_argument("--out",default="public/charts/mutuo-fisso-o-variabile/reel_totale_pagato.csv")
    a=ap.parse_args()
    df=mfv.ingest()
    if a.scan:
        for o in ["2008-01-01","2008-10-01","2011-07-01","2011-11-01","2012-01-01","2015-01-01"]:
            t0,fx,vr,h,ns,cv,cf,cs=build(df,o)
            print(f"{o}  premio {(fx-vr)*100:+.2f}pp  mesi {h}  surroghe {ns}  "
                  f"tot fine: var {cv[-1]/1000:.0f}k  fisso {cf[-1]/1000:.0f}k  surroga {cs[-1]/1000:.0f}k")
    else:
        t0,fx,vr,h,ns,cv,cf,cs=build(df,a.orig)
        idx=list(range(5,h,6))                     # ogni 6 mesi (fine semestre)
        dates=[(t0+pd.DateOffset(months=k+1)).strftime("%Y-%m-%d") for k in idx]
        pd.DataFrame({"date":dates,
                      "Variabile":np.round(cv[idx],0),
                      "Fisso":np.round(cf[idx],0),
                      "Fisso con surroga":np.round(cs[idx],0)}).to_csv(a.out,index=False)
        print(f"orig {a.orig} premio {(fx-vr)*100:+.2f}pp surroghe {ns} punti {len(idx)} -> {a.out}")
        print(f"tot fine: var {cv[-1]:.0f}  fisso {cf[-1]:.0f}  surroga {cs[-1]:.0f}")
