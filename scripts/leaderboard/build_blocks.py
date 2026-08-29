"""
Leaderboard — Step 1b: assembla TUTTI i mattoncini come TR mensile IN EURO.
Blocchi USD (equity/oro/BTC/US bond/World2x) -> convertiti in EUR via EURUSD.
Blocchi EUR nativi (CMOD, BTP) -> usati come sono.
Output: data/processed/leaderboard_blocks_eur.csv (indici TR base 100, mensili, 2018+).
"""
import os, numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..","..")
RAW=os.path.join(ROOT,"data","raw"); CACHE=os.path.join(ROOT,"data","cache"); PROC=os.path.join(ROOT,"data","processed")
START="2017-12-31"

def m_last(df, datecol, valcol):
    df=df.copy(); df[datecol]=pd.to_datetime(df[datecol]); df[valcol]=pd.to_numeric(df[valcol],errors="coerce")
    return df.dropna(subset=[valcol]).set_index(datecol)[valcol].resample("ME").last()

# EURUSD (USD per EUR), mensile
eur=pd.read_csv(os.path.join(RAW,"Eurusd.csv")); eurusd=m_last(eur,"Date","Close")

def corr_usd(name):  # serie mensile adjclose in USD -> price EUR
    d=pd.read_csv(os.path.join(CACHE,f"{name}.csv")); d.columns=["date","v"]
    s=m_last(d,"date","v"); return s/eurusd.reindex(s.index)   # EUR = USD / (USD per EUR)

def eur_native(path):  # serie giornaliera/mensile EUR -> mensile
    d=pd.read_csv(path)
    dcol=d.columns[0]; vcol="Close" if "Close" in d.columns else d.columns[1]
    return m_last(d,dcol,vcol)

# ---- equity/oro/BTC (USD -> EUR) ----
blocks={}
usd_equity={"WORLD":"corr_world_etf","ALLWORLD":"corr_acwi_etf","SP500":"corr_usa",
    "NASDAQ":"corr_nasdaq","ENERGY":"corr_energy","HEALTH":"corr_health","EM":"corr_em",
    "SMALLCAP":"corr_smallcap","GOLD":"corr_gold","BTC":"corr_btc"}
for k,src in usd_equity.items(): blocks[k]=corr_usd(src)

# ---- commodity CMOD (EUR nativo) ----
blocks["COMMODITY"]=eur_native(os.path.join(RAW,"CMOD.csv"))

# ---- bond: US (USD->EUR), EUR (nativi) ----
bonds=pd.read_csv(os.path.join(PROC,"leaderboard_bonds.csv")); bonds["date"]=pd.to_datetime(bonds["date"])
bonds=bonds.set_index("date")
for k in ["us_20y","us_10y","us_2y"]:
    s=bonds[k].dropna(); blocks[k.upper()]=s/eurusd.reindex(s.index)
for k in ["eu_30y","eu_10y","eu_3y"]:
    blocks[k.upper()]=bonds[k].dropna()

# ---- World 2x sintetico (2x daily del World USD -> EUR) ----
def load_daily_price(path):
    d=pd.read_csv(path)
    dcol=d.columns[0]
    for c in ["Adj Close","adjclose","Close","close"]:
        if c in d.columns: vcol=c; break
    else: vcol=d.columns[1]
    d[dcol]=pd.to_datetime(d[dcol],errors="coerce"); d[vcol]=pd.to_numeric(d[vcol],errors="coerce")
    return d.dropna(subset=[vcol]).set_index(dcol)[vcol].sort_index()
swda=load_daily_price(os.path.join(CACHE,"yf_ucits_swda_ishares_world.csv"))
rd=swda.pct_change().dropna()
nav2x=(1+2*rd).cumprod()                     # 2x giornaliero, USD
nav2x_m=nav2x.resample("ME").last()
blocks["WORLD2X"]=nav2x_m/eurusd.reindex(nav2x_m.index)

# ---- normalizza a TR base 100 dal 2018, griglia mensile comune ----
panel=pd.DataFrame(blocks)
panel=panel[panel.index>=START]
panel=panel/panel.bfill().iloc[0]*100          # base 100 al primo mese
panel.index.name="date"
panel.to_csv(os.path.join(PROC,"leaderboard_blocks_eur.csv"))

# ---- sanity ----
def cagr(s):
    s=s.dropna();
    if len(s)<13: return np.nan
    yrs=(s.index[-1]-s.index[0]).days/365.25; return (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
print(f"EURUSD: {eurusd.index[0].date()}→{eurusd.index[-1].date()}  ultimo {eurusd.iloc[-1]:.3f}")
print(f"\nPanel EUR: {panel.index[0].date()} → {panel.index[-1].date()}  ({len(panel)} mesi)")
print(f"{'blocco':10s} {'primo':>10s} {'ultimo':>10s} {'CAGR EUR':>9s}")
for c in panel.columns:
    s=panel[c].dropna()
    print(f"  {c:10s} {str(s.index[0].date()):>10s} {str(s.index[-1].date()):>10s} {cagr(s)*100:7.1f}%")
