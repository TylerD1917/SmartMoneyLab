"""
Segnale di valutazione RELATIVA vs USA (e vs World):
  spread_diff  = CAPE_x - CAPE_bench
  spread_ratio = CAPE_x / CAPE_bench
de-medianizzati sulla storia del singolo paese (deviazione dal proprio livello tipico).
Testa se predicono:
  (a) il rendimento forward del paese X
  (b) il rendimento forward RELATIVO  X - benchmark
a 5 e 10 anni, pooled sui paesi individuali.
"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); PROC=os.path.join(HERE,"..","data","processed")
ds=pd.read_csv(os.path.join(PROC,"cape_forward_dataset.csv"))

POOLED=["Japan","Germany","France","Switzerland","Australia","Canada","Italy","Spain",
        "Netherlands","Denmark","Finland","Norway","Sweden","Belgium","Austria","Brazil",
        "China","India","South Africa","South Korea","Taiwan","Indonesia","Thailand"]

def stats(df,x,y):
    d=df[[x,y]].dropna()
    if len(d)<20: return None
    xx,yy=d[x].values,d[y].values
    r=np.corrcoef(xx,yy)[0,1]; b,a=np.polyfit(xx,yy,1)
    return len(d),r,r**2,b

for BENCH,label in [("US Large","USA"),("Developed Markets Large","World")]:
    b=ds[ds.market==BENCH].set_index("date")
    bc=b.cape.to_dict(); bf5=b.fwd5_ann.to_dict(); bf10=b.fwd10_ann.to_dict()
    d=ds[ds.market.isin(POOLED)].copy()
    d["bench_cape"]=d.date.map(bc)
    d["diff"]=d.cape-d.bench_cape
    d["ratio"]=d.cape/d.bench_cape
    d["rel_fwd5"]=d.fwd5_ann-d.date.map(bf5)
    d["rel_fwd10"]=d.fwd10_ann-d.date.map(bf10)
    # de-medianizzazione sulla storia del singolo paese (in-sample)
    d["diff_dev"]=d["diff"]-d.groupby("market")["diff"].transform("median")
    d["ratio_rel"]=d["ratio"]/d.groupby("market")["ratio"].transform("median")
    print("="*72)
    print(f"BENCHMARK = {label}   (spread di CAPE del paese vs {label})")
    print("="*72)
    for h in (5,10):
        print(f"\n  --- orizzonte {h} anni ---")
        print(f"  {'segnale':22s}{'esito':16s}{'n':>5s}{'corr':>8s}{'R2':>7s}")
        combos=[
            ("diff_dev (X-bench, dev)", f"rel_fwd{h}", "REL X-bench"),
            ("ratio_rel (X/bench, dev)", f"rel_fwd{h}", "REL X-bench"),
            ("diff_dev (X-bench, dev)", f"fwd{h}_ann", "own X"),
            ("cape/own-median (ref)",   f"fwd{h}_ann", "own X"),
        ]
        if "cape_rel" not in d: d["cape_rel"]=d.cape/d.groupby("market")["cape"].transform("median")
        colmap={"diff_dev (X-bench, dev)":"diff_dev","ratio_rel (X/bench, dev)":"ratio_rel","cape/own-median (ref)":"cape_rel"}
        for sig,out,tag in combos:
            s=stats(d,colmap[sig],out)
            if s: print(f"  {sig:22s}{tag:16s}{s[0]:5d}{s[1]:+8.3f}{s[2]:7.3f}")

    # bucket: valutazione relativa vs USA -> rendimento relativo forward 10y
    if label=="USA":
        print("\n  BUCKET: quanto e' caro X vs USA rispetto al suo tipico -> REL fwd10 (X-USA)")
        d["q"]=pd.qcut(d["diff_dev"].rank(method="first"),5,labels=["1 molto piu' economico","2","3 tipico","4","5 molto piu' caro"])
        g=d.dropna(subset=["rel_fwd10"]).groupby("q",observed=True)["rel_fwd10"]
        for q in d["q"].cat.categories:
            if q in g.groups:
                s=g.get_group(q)
                print(f"    {q:24s} n={len(s):4d}  mediana REL={s.median()*100:+5.1f}pp/anno  media={s.mean()*100:+5.1f}pp")
