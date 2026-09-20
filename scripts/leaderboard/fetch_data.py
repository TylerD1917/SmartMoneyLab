"""
Leaderboard — Step 5a: scarica i dati FRESCHI (gira sul runner GitHub, non nel
sandbox dove yfinance e' bloccato). Rigenera esattamente gli input che i build
script si aspettano, con gli stessi ticker gia' validati.

Scarica anche gli ETF governativi euro (IBGS/IBGZ/IBGL) per la gamba bond EUR:
sostituiscono la vecchia curva BTP sintetica da REPORT_BancaItalia.xlsx (export
manuale). Ora tutta la pipeline si aggiorna da sola, senza input a mano.

Fonti: yfinance (equity/oro/BTC/EURUSD/CMOD/World daily) + FRED (Treasury USA).
"""
import os, sys, io
import pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..","..")
RAW=os.path.join(ROOT,"data","raw"); CACHE=os.path.join(ROOT,"data","cache")
os.makedirs(RAW,exist_ok=True); os.makedirs(CACHE,exist_ok=True)

try:
    import yfinance as yf
except ImportError:
    sys.exit("Manca yfinance: pip install --upgrade yfinance")

def _close(df):
    """Estrae la serie Close da un download yfinance (gestisce MultiIndex)."""
    if df is None or len(df)==0: return None
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy(); df.columns = df.columns.get_level_values(0)
    col = "Close" if "Close" in df.columns else ("Adj Close" if "Adj Close" in df.columns else None)
    if col is None: return None
    s = pd.to_numeric(df[col], errors="coerce").dropna(); s.index = pd.to_datetime(s.index); return s

def dl(ticker, **kw):
    return yf.download(ticker, auto_adjust=True, progress=False, **kw)

# ---- 1) equity/oro/BTC: monthly TR (auto_adjust), stesso formato dei corr_* ----
EQ = {"URTH":"world_etf","ACWI":"acwi_etf","SPY":"usa","QQQ":"nasdaq","XLE":"energy",
      "XLV":"health","EEM":"em","IWM":"smallcap","GC=F":"gold","BTC-USD":"btc"}
failed=[]
for tk, slug in EQ.items():
    s=_close(dl(tk, period="max"))
    if s is None: failed.append(tk); print(f"  [X] {tk}"); continue
    m=s.resample("ME").last(); m.index.name="Date"
    m.to_csv(os.path.join(CACHE,f"corr_{slug}.csv"), header=["adjclose"])
    print(f"  [ok] corr_{slug:10s} {m.index[0].date()} -> {m.index[-1].date()} ({len(m)})")

# ---- 2) EURUSD, CMOD (EUR), SWDA daily (per il World 2x): daily ----
def save_daily(ticker, path, cols_like_ohlc=True):
    df=dl(ticker, period="max")
    s=_close(df)
    if s is None: failed.append(ticker); print(f"  [X] {ticker}"); return
    out=pd.DataFrame({"Date":s.index.date,"Close":s.values})
    out.to_csv(path, index=False)
    print(f"  [ok] {os.path.basename(path):32s} {out.Date.iloc[0]} -> {out.Date.iloc[-1]} ({len(out)})")
save_daily("EURUSD=X", os.path.join(RAW,"Eurusd.csv"))
save_daily("CMOD.MI",  os.path.join(RAW,"CMOD.csv"))
save_daily("SWDA.L",   os.path.join(CACHE,"yf_ucits_swda_ishares_world.csv"))

# ---- 3) Treasury USA: rendimenti a maturita' costante da FRED (CSV pubblico) ----
FRED="https://fred.stlouisfed.org/graph/fredgraph.csv?id="
def fred(sid, path):
    try:
        d=pd.read_csv(FRED+sid)
        d.to_csv(path, index=False)
        print(f"  [ok] {sid:8s} -> {os.path.basename(path)} ({len(d)})")
    except Exception as e:
        failed.append(sid); print(f"  [X] {sid}: {e}")
fred("DGS20", os.path.join(RAW,"DGS20.csv"))
fred("DGS2",  os.path.join(RAW,"DGS2.csv"))
fred("DGS10", os.path.join(CACHE,"fred_dgs10.csv"))

# ---- 4) ETF governativi euro (gamba bond EUR): TR mensile in EUR nativo ----
#   auto_adjust=True -> il prezzo e' gia' total return (cedole reinvestite).
#   IBGS 1-3yr -> EU_3Y | IBGZ 10-15yr -> EU_10Y | IBGL 15-30yr -> EU_30Y
EU_GOVT={"IBGS":"eu_govt_1_3","IBGZ":"eu_govt_10_15","IBGL":"eu_govt_15_30"}
EU_SUFFIXES=[".MI",".AS",".L",".DE"]   # prova piu' listini, tieni il primo con storico pre-2018
for base,slug in EU_GOVT.items():
    picked=None
    for suf in EU_SUFFIXES:
        s_etf=_close(dl(base+suf, period="max"))
        if s_etf is not None and len(s_etf) and s_etf.index.min()<=pd.Timestamp("2017-06-30"):
            picked=(base+suf, s_etf); break
    if picked is None:
        failed.append(base); print(f"  [X] {base} (nessun listino con storico pre-2018)"); continue
    tk,s_etf=picked
    m=s_etf.resample("ME").last(); m.index.name="Date"
    m.to_csv(os.path.join(CACHE,f"{slug}.csv"), header=["adjclose"])
    print(f"  [ok] {slug:14s} <- {tk:10s} {m.index[0].date()} -> {m.index[-1].date()} ({len(m)})")


# ---- 5) MSCI World Financials (blocco FINANCIALS leaderboard): XDWF.MI, EUR nativo, TR mensile ----
try:
    s_fin=_close(dl("XDWF.MI", period="max"))
    if s_fin is not None and len(s_fin):
        mfin=s_fin.resample("ME").last(); mfin.index.name="Date"
        mfin.to_csv(os.path.join(CACHE,"financials_world_eur.csv"), header=["adjclose"])
        print(f"  [ok] financials_world_eur <- XDWF.MI {mfin.index[0].date()} -> {mfin.index[-1].date()} ({len(mfin)})")
    else:
        failed.append("XDWF.MI"); print("  [X] XDWF.MI")
except Exception as e:
    failed.append("XDWF.MI"); print("  [X] XDWF.MI", repr(e)[:80])

if failed:
    print(f"\n[!] ticker/serie falliti: {', '.join(failed)}")
    # se manca un mattoncino CRITICO il build successivo fallira' (visibile nel log)
print("\n[ok] fetch completato.")
