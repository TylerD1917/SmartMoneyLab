"""
Portafoglio attivo 'value relativo': ogni R mesi seleziona i 4 mercati del pool
piu' economici RISPETTO ALLA PROPRIA MEDIANA STORICA (CAPE/mediana espansiva, solo
dati passati => niente lookahead), 25% ciascuno, buy&hold fino al ribilancio.
Benchmark: ACWI Gross TR. Lordo, no tasse. Rendimenti MSCI Gross TR USD mensili.
Output: data/processed/port_equity_{R}m.csv  + metriche a video.
"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); PROC=os.path.join(HERE,"..","data","processed")

capeL=pd.read_csv(os.path.join(PROC,"cape_panel_long.csv"))      # date(YYYY-MM),market,cape
retW=pd.read_csv(os.path.join(PROC,"returns_panel_wide.csv"))    # month,<markets>
retW=retW.set_index("month")
months=list(retW.index)

UNIV=["Japan","Germany","France","Switzerland","Australia","Canada","Italy","Spain",
      "Netherlands","Denmark","Finland","Norway","Sweden","Belgium","Austria","Brazil",
      "China","India","South Africa","South Korea","Taiwan","Indonesia","Thailand"]
BENCH="ACWI"

# CAPE per (market) come lista ordinata (date,val)
capeL=capeL.sort_values("date")
cape_hist={m:list(zip(g.date,g.cape)) for m,g in capeL.groupby("market")}

def cape_rel_at(mkt, month):
    """CAPE/mediana-espansiva usando solo osservazioni CAPE con date<=month. Serve >=6 storiche."""
    h=cape_hist.get(mkt,[])
    past=[v for d,v in h if d<=month and pd.notna(v)]
    if len(past)<6: return None
    return past[-1]/np.median(past)

def ret_month(mkt, m):
    try:
        a=retW.at[m,mkt];
        return float(a) if pd.notna(a) else None
    except KeyError: return None

def backtest(step):
    start=months.index("2004-06")
    # date di ribilancio
    rebs=list(range(start,len(months)-1,step))
    port=[1.0]; dates=[months[start]]
    holdings={}  # mkt->weight
    def pick(m):
        cand=[]
        for mk in UNIV:
            if ret_month(mk,m) is None: continue
            cr=cape_rel_at(mk,m)
            if cr is not None: cand.append((cr,mk))
        cand.sort()
        return {mk:0.25 for _,mk in cand[:4]}
    holdings=pick(months[start])
    picks_log=[(months[start], list(holdings))]
    for i in range(start, len(months)-1):
        m_next=months[i+1]
        # rendimento del mese (da m a m_next) usando livelli
        gross=0.0; wsum=0.0
        neww={}
        for mk,w in holdings.items():
            l0=retW.at[months[i],mk] if mk in retW.columns else None
            l1=retW.at[m_next,mk] if mk in retW.columns else None
            if pd.notna(l0) and pd.notna(l1):
                r=float(l1)/float(l0)
                gross+=w*r; neww[mk]=w*r; wsum+=w
        if wsum>0:
            port.append(port[-1]*(gross/wsum)); dates.append(m_next)
            # drift dei pesi
            tot=sum(neww.values()); holdings={k:v/tot for k,v in neww.items()}
        else:
            port.append(port[-1]); dates.append(m_next)
        # ribilancio a fine mese se i+1 e' data di reb
        if (i+1) in rebs:
            holdings=pick(m_next); picks_log.append((m_next,list(holdings)))
    return pd.Series(port,index=dates), picks_log

def bench_curve(start_month):
    idx=months.index(start_month); vals=[1.0]; dts=[months[idx]]
    for i in range(idx,len(months)-1):
        l0=retW.at[months[i],BENCH]; l1=retW.at[months[i+1],BENCH]
        if pd.notna(l0) and pd.notna(l1):
            vals.append(vals[-1]*float(l1)/float(l0)); dts.append(months[i+1])
    return pd.Series(vals,index=dts)

def metrics(eq):
    n=len(eq)-1; yrs=n/12
    cagr=eq.iloc[-1]**(1/yrs)-1
    rets=eq.pct_change().dropna()
    vol=rets.std()*np.sqrt(12)
    mdd=((eq/eq.cummax())-1).min()
    sharpe=(rets.mean()*12)/vol
    return cagr,vol,mdd,cagr/abs(mdd),sharpe,eq.iloc[-1]

for step,lab in [(30,"2.5 anni"),(60,"5 anni")]:
    eq,log=backtest(step)
    bench=bench_curve(eq.index[0]).reindex(eq.index)
    eq.to_frame("portfolio").assign(acwi=bench).to_csv(os.path.join(PROC,f"port_equity_{step}m.csv"))
    cP=metrics(eq); cB=metrics(bench.dropna())
    print("="*66)
    print(f"RIBILANCIO OGNI {lab}  ({eq.index[0]} -> {eq.index[-1]})")
    print("="*66)
    print(f"  {'':12s}{'CAGR':>8s}{'Vol':>8s}{'MDD':>8s}{'Calmar':>8s}{'Sharpe':>8s}{'x cap':>8s}")
    print(f"  {'Portfolio':12s}{cP[0]*100:7.1f}%{cP[1]*100:7.1f}%{cP[2]*100:7.1f}%{cP[3]:8.2f}{cP[4]:8.2f}{cP[5]:7.2f}x")
    print(f"  {'ACWI':12s}{cB[0]*100:7.1f}%{cB[1]*100:7.1f}%{cB[2]*100:7.1f}%{cB[3]:8.2f}{cB[4]:8.2f}{cB[5]:7.2f}x")
    print("  Selezioni nel tempo:")
    for d,ps in log: print(f"    {d}: {', '.join(ps)}")
