"""
Leaderboard — Step 2+3: config allocazioni + motore di composizione.
Legge i blocchi EUR (leaderboard_blocks_eur.csv), compone i portafogli con
ribilanciamento annuale (1° gennaio), calcola metriche YTD/1a/3a/5a/7a e
scrive public/leaderboard.json (NAV mensile base 100 al 2017-12 + metriche).
"""
import os, json
import numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..","..")
PROC=os.path.join(ROOT,"data","processed")
OUTJSON=os.path.join(ROOT,"public","tools","leaderboard.json")

panel=pd.read_csv(os.path.join(PROC,"leaderboard_blocks_eur.csv"),parse_dates=["date"]).set_index("date")
rets=panel.pct_change(fill_method=None)

# ---------------- CONFIG: 11 portafogli + 4 benchmark ----------------
# pesi in frazione; le chiavi sono i nomi dei blocchi in panel
PORTAFOGLI=[
 # id, nome, variante, categoria, allocazione
 ("bench-world","MSCI World","","benchmark",{"WORLD":1.0}),
 ("bench-allworld","FTSE All-World","","benchmark",{"ALLWORLD":1.0}),
 ("bench-sp500","S&P 500","","benchmark",{"SP500":1.0}),
 ("bench-nasdaq","Nasdaq 100","","benchmark",{"NASDAQ":1.0}),
 ("6040-orig","60/40","Treasury USA (€)","classico",{"WORLD":.60,"US_10Y":.40}),
 ("6040-eur","60/40","BTP (€/IT)","classico",{"WORLD":.60,"EU_10Y":.40}),
 ("allweather-orig","All Weather","Treasury USA (€)","classico",{"WORLD":.30,"US_20Y":.40,"US_10Y":.15,"GOLD":.075,"COMMODITY":.075}),
 ("allweather-eur","All Weather","BTP (€/IT)","classico",{"WORLD":.30,"EU_30Y":.40,"EU_10Y":.15,"GOLD":.075,"COMMODITY":.075}),
 ("goldenbutterfly-orig","Golden Butterfly","Treasury USA (€)","classico",{"WORLD":.20,"SMALLCAP":.20,"US_20Y":.20,"US_2Y":.20,"GOLD":.20}),
 ("goldenbutterfly-eur","Golden Butterfly","BTP (€/IT)","classico",{"WORLD":.20,"SMALLCAP":.20,"EU_30Y":.20,"EU_3Y":.20,"GOLD":.20}),
 ("9010-buffett","90/10 Buffett","","classico",{"SP500":.90,"US_2Y":.10}),
 ("nasdaq-energy","Nasdaq + Energy","","autore",{"NASDAQ":.80,"ENERGY":.15,"GOLD":.05}),
 ("allweather-aggressive","All Weather Aggressive","SmartMoneyLab","autore",{"NASDAQ":.25,"EM":.20,"WORLD":.25,"GOLD":.10,"SMALLCAP":.10,"BTC":.05,"HEALTH":.05}),
 ("effective-leverage","Effective Leverage","SmartMoneyLab","autore",{"ALLWORLD":.75,"WORLD2X":.25}),
]

def nav_portafoglio(alloc):
    cols=list(alloc); r=rets[cols].dropna(how="any")
    if len(r)<13: return None
    w0=np.array([alloc[c] for c in cols])
    dates=r.index; vals=[]; v=100.0; w=w0.copy()
    # valori per-blocco, ribilanciati ogni 1° gennaio
    comp=w0*100.0
    nav=[]; navdates=[]
    prev_year=None
    # inizializza al mese precedente il primo return (base 100)
    start=panel.loc[:r.index[0]].index[-2] if len(panel.loc[:r.index[0]])>=2 else r.index[0]
    nav.append(100.0); navdates.append(start); comp=w0*100.0
    for dt in dates:
        comp=comp*(1+r.loc[dt,cols].values)      # crescita mensile per blocco
        tot=comp.sum(); nav.append(tot); navdates.append(dt)
        if dt.month==12:                          # ribilancio a fine anno (=inizio anno succ.)
            comp=w0*tot
    return pd.Series(nav,index=pd.DatetimeIndex(navdates))

def metriche(nav):
    nav=nav.dropna(); last=nav.index[-1]; out={}
    def ret_n(months):
        past=last-pd.DateOffset(months=months)
        s=nav[nav.index<=past]
        if len(s)==0: return None
        base=s.iloc[-1]; yrs=months/12
        tot=nav.iloc[-1]/base
        return tot-1 if months<=12 else tot**(1/yrs)-1
    # YTD: da fine anno precedente
    decprev=nav[nav.index<=pd.Timestamp(last.year-1,12,31)]
    out["ytd"]=(nav.iloc[-1]/decprev.iloc[-1]-1) if len(decprev) else None
    out["y1"]=ret_n(12); out["y3"]=ret_n(36); out["y5"]=ret_n(60); out["y7"]=ret_n(84)
    out["as_of"]=str(last.date())
    return out

result=[]
for pid,nome,variante,cat,alloc in PORTAFOGLI:
    nav=nav_portafoglio(alloc)
    if nav is None: print("SKIP",pid); continue
    m=metriche(nav)
    navpts=[{"d":str(d.date()),"v":round(float(v),2)} for d,v in nav.items()]
    result.append({"id":pid,"name":nome,"variant":variante,"category":cat,
        "allocation":[{"asset":k,"w":round(v,4)} for k,v in alloc.items()],
        "metrics":{k:(round(m[k],4) if isinstance(m[k],float) else m[k]) for k in ["ytd","y1","y3","y5","y7","as_of"]},
        "nav":navpts})

os.makedirs(os.path.dirname(OUTJSON),exist_ok=True)
json.dump({"generated":str(pd.Timestamp.now().date()),"base_currency":"EUR",
    "base":"100 al 2017-12","rebalance":"annuale (1° gennaio)","portfolios":result},
    open(OUTJSON,"w"),ensure_ascii=False,indent=1)

# ---- stampa leaderboard ordinata per 5 anni ----
def pct(x): return f"{x*100:5.1f}%" if isinstance(x,float) else "  n/d"
rows=sorted(result,key=lambda p: (p["metrics"]["y5"] if isinstance(p["metrics"]["y5"],float) else -9))
print(f"{'Portafoglio':34s} {'YTD':>6s} {'1a':>6s} {'3a':>6s} {'5a':>6s} {'7a':>6s}  as_of")
for p in rows:
    m=p["metrics"]; nm=(p['name']+(' · '+p['variant'] if p['variant'] else ''))[:33]
    tag="•" if p["category"]=="benchmark" else " "
    print(f"{tag}{nm:33s} {pct(m['ytd'])} {pct(m['y1'])} {pct(m['y3'])} {pct(m['y5'])} {pct(m['y7'])}  {m['as_of']}")
print(f"\n[ok] {len(result)} portafogli -> {OUTJSON}")
