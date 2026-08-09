"""
Studio panel: CAPE (RA, semestrale) -> rendimenti forward 5y e 10y (MSCI Gross TR USD).
Output:
  data/processed/cape_forward_dataset.csv   (market, date, cape, fwd5_ann, fwd10_ann)
  stampa: correlazioni pooled, regressioni, bucket, R2 per paese, versione CAPE-relativo.
Nota: rendimenti in USD nominali gross TR. La pendenza CAPE->rendimento e' robusta al
nominale (l'inflazione USA 2001-26 e' comune a tutti i mercati in USD).
"""
import pandas as pd, numpy as np, os

HERE = os.path.dirname(__file__)
PROC = os.path.join(HERE, "..", "data", "processed")

cape = pd.read_csv(os.path.join(PROC, "cape_panel_long.csv"))          # date(YYYY-MM), market, cape
ret  = pd.read_csv(os.path.join(PROC, "returns_panel_wide.csv"))        # month, <markets>
retL = ret.melt(id_vars="month", var_name="market", value_name="level").dropna()
lvl = {(r.market, r.month): r.level for r in retL.itertuples()}

def addyears(ym, y):
    a, m = ym.split("-"); return f"{int(a)+y}-{m}"

POOLED = ["US Large","Japan","Germany","France","Switzerland","Australia","Canada","Italy",
          "Spain","Netherlands","Denmark","Finland","Norway","Sweden","Belgium","Austria",
          "Brazil","China","India","South Africa","South Korea","Taiwan","Indonesia","Thailand"]
AGG = ["Europe","Emerging Markets","Asia ex Japan","Developed Markets Large"]

recs = []
for r in cape.itertuples():
    d, mk, cv = r.date, r.market, r.cape
    if (mk, d) not in lvl:      # serve il livello di partenza
        continue
    row = {"market": mk, "date": d, "cape": cv}
    for h in (5, 10):
        dh = addyears(d, h)
        if (mk, dh) in lvl:
            row[f"fwd{h}_ann"] = (lvl[(mk, dh)] / lvl[(mk, d)]) ** (1/h) - 1
    recs.append(row)
ds = pd.DataFrame(recs)
ds.to_csv(os.path.join(PROC, "cape_forward_dataset.csv"), index=False)

def stats(df, xcol, ycol):
    d = df[[xcol, ycol]].dropna()
    if len(d) < 20: return None
    x, y = d[xcol].values, d[ycol].values
    r = np.corrcoef(x, y)[0, 1]
    b, a = np.polyfit(x, y, 1)
    return len(d), r, r**2, a, b

print("="*70)
print("PANEL POOLED (24 paesi individuali) — CAPE assoluto")
print("="*70)
for h in (5, 10):
    d = ds[ds.market.isin(POOLED)]
    n, r, r2, a, b = stats(d, "cape", f"fwd{h}_ann")
    print(f"  fwd{h}y: n={n}  corr={r:+.3f}  R2={r2:.3f}  slope={b*100:+.3f}pp/CAPE  intercetta={a*100:.1f}%")
    # earnings yield (1/CAPE)
    d2 = d.assign(ey=1/d.cape)
    n2, r2c, r2b, a2, b2 = stats(d2, "ey", f"fwd{h}_ann")
    print(f"         earnings yield 1/CAPE: corr={r2c:+.3f}  R2={r2b:.3f}")

print("\n" + "="*70)
print("BUCKET CAPE -> rendimento forward (pooled 24 paesi)")
print("="*70)
bins = [0,10,15,20,25,30,40,999]; labels=["<10","10-15","15-20","20-25","25-30","30-40",">40"]
d = ds[ds.market.isin(POOLED)].copy()
d["bucket"] = pd.cut(d.cape, bins=bins, labels=labels)
for h in (5,10):
    print(f"\n  -- forward {h}y annualizzato --")
    g = d.dropna(subset=[f"fwd{h}_ann"]).groupby("bucket", observed=True)[f"fwd{h}_ann"]
    for bk in labels:
        if bk in g.groups:
            s = g.get_group(bk)
            print(f"    CAPE {bk:6s}: n={len(s):4d}  mediana={s.median()*100:+5.1f}%  media={s.mean()*100:+5.1f}%  %neg={100*(s<0).mean():4.0f}%")

print("\n" + "="*70)
print("R2 PER PAESE (fwd10y ~ CAPE) — eterogeneita' stile Keimling")
print("="*70)
rows=[]
for mk in POOLED+AGG:
    s = stats(ds[ds.market==mk], "cape", "fwd10_ann")
    if s: rows.append((mk, s[0], s[1], s[2], s[4]*100))
for mk,n,r,r2,b in sorted(rows, key=lambda x:-x[3]):
    tag = "" if mk in POOLED else " [agg]"
    print(f"  {mk:24s}{tag:6s} n={n:3d}  corr={r:+.2f}  R2={r2:.2f}")

print("\n" + "="*70)
print("CAPE RELATIVO alla propria mediana storica (risponde al caveat 'confronta col proprio passato')")
print("="*70)
med = ds.groupby("market").cape.transform("median")   # mediana full-sample own-country (in-sample)
ds["cape_rel"] = ds.cape / med
for h in (5,10):
    d = ds[ds.market.isin(POOLED)]
    n,r,r2,a,b = stats(d, "cape_rel", f"fwd{h}_ann")
    print(f"  fwd{h}y ~ CAPE/mediana_paese: n={n}  corr={r:+.3f}  R2={r2:.3f}")
# confronto diretto assoluto vs relativo a 10y
print("\n  Confronto potenza esplicativa a 10y:")
for lab,col in [("CAPE assoluto","cape"),("CAPE relativo","cape_rel"),("earnings yield","ey")]:
    dd = ds[ds.market.isin(POOLED)].copy()
    if col=="ey": dd["ey"]=1/dd.cape
    s = stats(dd, col, "fwd10_ann")
    if s: print(f"    {lab:16s} R2={s[2]:.3f}  corr={s[1]:+.3f}")
