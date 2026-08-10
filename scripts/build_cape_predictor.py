"""
Costruisce il lookup per lo strumento predittivo CAPE -> rendimenti forward 5/10y,
per 6 mercati: World, Europa, Emergenti, Cina, India, Giappone.
Per ogni mercato salva i parametri della regressione storica (fwd ~ CAPE) cosi' che
il componente calcoli la previsione client-side da cape_now (che Tyler aggiorna).
Output: public/tools/cape-predictor-lookup.json
"""
import pandas as pd, numpy as np, os, json
HERE=os.path.dirname(__file__); PROC=os.path.join(HERE,"..","data","processed")
OUT=os.path.join(HERE,"..","public","tools"); os.makedirs(OUT,exist_ok=True)

ds=pd.read_csv(os.path.join(PROC,"cape_forward_dataset.csv"))
capeL=pd.read_csv(os.path.join(PROC,"cape_panel_long.csv"))

MARKETS={"Developed Markets Large":"World (mercati sviluppati)","Europe":"Europa",
         "Emerging Markets":"Mercati emergenti","China":"Cina","India":"India","Japan":"Giappone"}
AS_OF="2026-07"          # data dell'ultimo snapshot CAPE (Tyler aggiorna qui e i cape_now sotto)

def fit(df,ycol):
    d=df[["cape",ycol]].dropna()
    n=len(d); x=d.cape.values; y=d[ycol].values
    b,a=np.polyfit(x,y,1)
    yhat=a+b*x; resid=y-yhat
    ss_res=np.sum(resid**2); ss_tot=np.sum((y-y.mean())**2)
    r2=1-ss_res/ss_tot if ss_tot>0 else 0
    rmse=float(np.sqrt(ss_res/max(n-2,1)))
    return {"slope":float(b),"intercept":float(a),"rmse":rmse,"r2":float(r2),"n":int(n),
            "uncond_p25":float(np.percentile(y,25)),"uncond_median":float(np.median(y)),
            "uncond_p75":float(np.percentile(y,75))}

out={"meta":{"as_of":AS_OF,"source_article":"/posts/cape-internazionale-predice-rendimenti",
             "note":"cape_now e as_of vanno aggiornati con nuovi snapshot RA. Previsione = intercept+slope*CAPE, banda ±RMSE."},
     "markets":{}}
for mk,lab in MARKETS.items():
    hist=capeL[capeL.market==mk].sort_values("date")
    cape_now=float(hist.cape.iloc[-1]); med=float(hist.cape.median())
    cmin=float(hist.cape.min()); cmax=float(hist.cape.max())
    d=ds[ds.market==mk]
    out["markets"][mk]={
        "label":lab,"cape_now":round(cape_now,1),"hist_median":round(med,1),
        "hist_min":round(cmin,1),"hist_max":round(cmax,1),
        "slider_min":int(np.floor(cmin)),"slider_max":int(np.ceil(cmax)),
        "h5":fit(d,"fwd5_ann"),"h10":fit(d,"fwd10_ann"),
    }

# --- classifica valutazione su TUTTI i mercati dello studio (24 paesi) ---
RANK_LABELS={"Japan":"Giappone","Germany":"Germania","France":"Francia","Switzerland":"Svizzera",
    "Australia":"Australia","Canada":"Canada","Italy":"Italia","Spain":"Spagna","Netherlands":"Olanda",
    "Denmark":"Danimarca","Finland":"Finlandia","Norway":"Norvegia","Sweden":"Svezia","Belgium":"Belgio",
    "Austria":"Austria","Brazil":"Brasile","China":"Cina","India":"India","South Africa":"Sudafrica",
    "South Korea":"Corea","Taiwan":"Taiwan","Indonesia":"Indonesia","Thailand":"Thailandia","US Large":"USA"}
rank=[]
for mk,lab in RANK_LABELS.items():
    h=capeL[capeL.market==mk].sort_values("date")
    now=float(h.cape.iloc[-1]); med=float(h.cape.median())
    rank.append({"market":mk,"label":lab,"cape_now":round(now,1),"median":round(med,1),"ratio":round(now/med,2)})
rank.sort(key=lambda x:x["ratio"])
out["ranking"]={"universe_n":len(rank),"items":rank}

json.dump(out,open(os.path.join(OUT,"cape-predictor-lookup.json"),"w"),indent=2,ensure_ascii=False)
print("\nCLASSIFICA — 3 sottovalutati:", [f'{r["label"]} {r["ratio"]}x' for r in rank[:3]])
print("CLASSIFICA — 3 sopravvalutati:", [f'{r["label"]} {r["ratio"]}x' for r in rank[-3:][::-1]])

# stampa anteprima previsioni
print(f"as_of={AS_OF}\n{'mercato':28s}{'CAPE':>6s}{'vs med':>8s}{'prev5y':>10s}{'prev10y':>10s}{'R2_10':>7s}")
for mk,m in out["markets"].items():
    c=m["cape_now"]
    p5=m["h5"]["intercept"]+m["h5"]["slope"]*c
    p10=m["h10"]["intercept"]+m["h10"]["slope"]*c
    print(f"{m['label']:28s}{c:6.1f}{c/m['hist_median']:8.2f}{p5*100:9.1f}%{p10*100:9.1f}%{m['h10']['r2']:7.2f}")
