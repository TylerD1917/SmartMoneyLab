"""
Leaderboard — Step 1a: serie TOTAL RETURN dei bond a maturità costante (CMT).
Ricostruisce il rendimento total-return mensile di un titolo "benchmark" a
maturità fissa a partire dal solo rendimento a scadenza, rivalutando ogni mese
un titolo alla pari (par bond) che invecchia di 1/12 di anno e viene riprezzato
al nuovo rendimento. Cattura carry + effetto prezzo (duration+convessità).

Bucket:
  US  20y / 10y / 2y   da FRED DGS20, DGS10 (cache), DGS2   (USD, dal 2016)
  EUR 30y / 10y / 3y   da REPORT_BancaItalia.xlsx (BTP benchmark, dal 1988)

Output: data/processed/leaderboard_bonds.csv  (indici TR base 100, valuta locale, mensili)
"""
import os
import numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..","..")
RAW=os.path.join(ROOT,"data","raw"); CACHE=os.path.join(ROOT,"data","cache")
OUTDIR=os.path.join(ROOT,"data","processed"); os.makedirs(OUTDIR,exist_ok=True)

def month_tr(y0, y1, M):
    """Return mensile di un par bond M-anni: emesso alla pari (cedola annua = y0),
    dopo 1 mese ha M-1/12 anni residui e viene riprezzato a y1."""
    dt=1/12; c=y0*100.0
    pv=sum(c*(1+y1)**(-(k-dt)) for k in range(1,M+1)) + 100.0*(1+y1)**(-(M-dt))
    return pv/100.0 - 1.0

def tr_index(yields_pct, M):
    """yields_pct: Series mensile (percentuale) indicizzata per data. -> indice TR base 100."""
    y=yields_pct.dropna().astype(float)/100.0
    idx=[100.0]; dts=[y.index[0]]
    for i in range(1,len(y)):
        r=month_tr(y.iloc[i-1], y.iloc[i], M)
        idx.append(idx[-1]*(1+r)); dts.append(y.index[i])
    return pd.Series(idx, index=pd.DatetimeIndex(dts))

# ---------- US: da DGS (daily -> month-end) ----------
def load_dgs(path, col):
    d=pd.read_csv(path); d.columns=["date",col]
    d["date"]=pd.to_datetime(d["date"]); d[col]=pd.to_numeric(d[col],errors="coerce")
    return d.dropna().set_index("date")[col].resample("ME").last()
us20=load_dgs(os.path.join(RAW,"DGS20.csv"),"DGS20")
us10=load_dgs(os.path.join(CACHE,"fred_dgs10.csv"),"DGS10")
us2 =load_dgs(os.path.join(RAW,"DGS2.csv"),"DGS2")

# ---------- EUR: da REPORT_BancaItalia.xlsx ----------
import openpyxl
wb=openpyxl.load_workbook(os.path.join(RAW,"REPORT_BancaItalia.xlsx"),data_only=True)
ws=wb["Prospetto"]; rows=list(ws.iter_rows(values_only=True))
MESI={"gen":1,"feb":2,"mar":3,"apr":4,"mag":5,"giu":6,"lug":7,"ago":8,"set":9,"ott":10,"nov":11,"dic":12}
rec=[]
for r in rows[3:]:
    a=r[0]
    if not a or "-" not in str(a): continue
    parts=str(a).strip().split("-")
    if len(parts)!=2: continue
    yy,mm=parts
    if not yy.isdigit() or mm not in MESI: continue
    dt=pd.Timestamp(int(yy),MESI[mm],1)+pd.offsets.MonthEnd(0)
    rec.append((dt, r[2], r[4], r[5]))   # C=3y, E=10y, F=30y
btp=pd.DataFrame(rec,columns=["date","y3","y10","y30"]).set_index("date").sort_index()
for c in ["y3","y10","y30"]: btp[c]=pd.to_numeric(btp[c],errors="coerce")

# ---------- costruisci indici TR ----------
series={
 "us_20y":tr_index(us20,20), "us_10y":tr_index(us10,10), "us_2y":tr_index(us2,2),
 "eu_30y":tr_index(btp["y30"],30), "eu_10y":tr_index(btp["y10"],10), "eu_3y":tr_index(btp["y3"],3),
}
out=pd.DataFrame(series)
out.index.name="date"
out.to_csv(os.path.join(OUTDIR,"leaderboard_bonds.csv"))

# ---------- sanity ----------
def cagr(s,start="2018-12-31"):
    s=s.dropna(); s=s[s.index>=start]
    if len(s)<13: return np.nan
    yrs=(s.index[-1]-s.index[0]).days/365.25
    return (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
def mdd(s):
    s=s.dropna(); s=s[s.index>=pd.Timestamp("2018-01-01")]
    return (s/s.cummax()-1).min()
print("bucket    inizio      fine        CAGR(2019-26)  MDD(2018+)")
for k,s in series.items():
    print(f"  {k:7s} {s.index[0].date()} {s.index[-1].date()}   {cagr(s)*100:6.2f}%      {mdd(s)*100:7.1f}%")
# check: US 20y vs TLT (corr_tlt) direzione
tlt=pd.read_csv(os.path.join(CACHE,"corr_tlt.csv")); tlt.columns=["date","v"]
tlt["date"]=pd.to_datetime(tlt["date"]); tlt=tlt.set_index("date")["v"].resample("ME").last()
j=pd.concat([series["us_20y"].pct_change(),tlt.pct_change()],axis=1).dropna()
print(f"\ncorr(mensile) US_20y_sintetico vs ETF TLT: {j.iloc[:,0].corr(j.iloc[:,1]):.3f}  (atteso alto, >0.9)")
print("2022 (anno del crollo obbligazionario) — rendimento annuo:")
for k in ["us_20y","eu_30y","us_2y","eu_3y"]:
    s=series[k]; y22=s[(s.index>="2021-12-31")&(s.index<="2022-12-31")]
    print(f"  {k}: {(y22.iloc[-1]/y22.iloc[0]-1)*100:+.1f}%")
print("\nOK ->", os.path.join(OUTDIR,"leaderboard_bonds.csv"))
