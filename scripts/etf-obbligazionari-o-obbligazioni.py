"""
ETF obbligazionari (duration COSTANTE) vs obbligazioni singole tenute a scadenza.
Domanda: cambia qualcosa? convergono? in quanto tempo?

Confronto a DURATION ALLINEATA (nodo sollevato correttamente: un 10Y appena emesso ha
duration ~8, l'ETF IEF ~6,9; confrontarli mescola 'meccanismo' e 'duration'). Quindi il
confronto principale usa un titolo con duration pari a quella dell'ETF: maturity 8 anni
(duration ~6,8 ≈ 6,9 dell'IEF). Il 10Y resta come CONTRASTO didattico.

Costruzione (tutto da CSV locali + IEF scaricato):
- Tasso 10Y mensile: Shiller "Long Interest Rate" (1871+) fino al 2000, poi DGS10 (FRED) al 2026.
- Tasso breve mensile: FEDFUNDS (1954+), per reinvestire le cedole. Finestra dal 1962.
- GAMBA ETF = indice Total Return a DURATION COSTANTE (maturity M): ogni mese un titolo par a
  M anni (cedola=yield precedente), valutato al nuovo yield, poi rinnovato a M (duration ferma).
  Rendimento mensile = carry + effetto prezzo (duration+convexity esatte sul par bond).
- GAMBA OBBLIGAZIONI = compra un titolo par a M anni, TENUTO A SCADENZA, cedole reinvestite al
  tasso breve; a scadenza rinnova; all'orizzonte del lettore (10/20 anni) liquida a mercato il
  titolo residuo (chi ha un orizzonte, a quella data incassa quel che ha).
- Ancora reale: ETF IEF (iShares 7-10Y, 2002+) in data/Bonds/IEF.csv (Date,Close auto-adjusted).

Baseline LORDA; il TER dell'ETF discusso a parte (unica differenza che non converge).
"""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

SLUG = "etf-obbligazionari-o-obbligazioni"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "public", "charts", SLUG); os.makedirs(OUT, exist_ok=True)
SHILLER = os.path.join(ROOT,"data","Sp500","shiller_mirror.csv")
DGS10   = os.path.join(ROOT,"data","Bonds","fred_dgs10.csv")
FEDF    = os.path.join(ROOT,"data","Bonds","FEDFUNDS.csv")
IEF     = os.path.join(ROOT,"data","Bonds","IEF.csv")

NAVY="#1e3a8a"; GOLD="#f59e0b"; GREY="#94a3b8"; GREEN="#059669"; RED="#e11d48"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
def it(x,d=1): return f"{x:.{d}f}".replace(".",",")

START="1962-01"; FREQ=2
M_MAIN=8            # maturity/duration del confronto principale (~ duration IEF 6,9)
M_CONTRAST=[7,8,10] # sweep didattico

# ---------------- dati ----------------
sh=pd.read_csv(SHILLER); sh["m"]=pd.PeriodIndex(pd.to_datetime(sh["Date"]),freq="M")
sh=sh[["m","Long Interest Rate"]].rename(columns={"Long Interest Rate":"y10"}); sh=sh[sh["y10"]>0]
d10=pd.read_csv(DGS10); d10["m"]=pd.PeriodIndex(pd.to_datetime(d10["observation_date"]),freq="M")
d10["y10"]=pd.to_numeric(d10["DGS10"],errors="coerce")
d10=d10.dropna(subset=["y10"]).groupby("m")["y10"].last().reset_index()
cut=pd.Period("2001-01","M")
sh=pd.concat([sh[sh["m"]<cut], d10[d10["m"]>=cut]], ignore_index=True).sort_values("m")
ff=pd.read_csv(FEDF); ff["m"]=pd.PeriodIndex(pd.to_datetime(ff["observation_date"]),freq="M")
ff=ff[["m","FEDFUNDS"]].rename(columns={"FEDFUNDS":"s"})
df=pd.merge(sh,ff,on="m",how="inner").sort_values("m").reset_index(drop=True)
df=df[df["m"]>=pd.Period(START,"M")].reset_index(drop=True)
df["y10"]/=100.0; df["s"]/=100.0
y=df["y10"].to_numpy(); s=df["s"].to_numpy(); T=len(df)
print(f"Dati mensili: {df['m'].iloc[0]} -> {df['m'].iloc[-1]}  ({T} mesi)")

# ---------------- bond pricing ----------------
def bond_price(ytm,coupon,n_years,face=100.0,freq=FREQ):
    n=int(round(n_years*freq)); c=coupon/freq*face; r=ytm/freq
    if n<=0: return face
    k=np.arange(1,n+1); return float((c/(1+r)**k).sum()+face/(1+r)**n)
def dur_conv(yld,M,h=1e-4):
    P0=bond_price(yld,yld,M); Pu=bond_price(yld+h,yld,M); Pd=bond_price(yld-h,yld,M)
    return -(Pu-Pd)/(2*h*P0), (Pu+Pd-2*P0)/(h*h*P0)

# ---------------- indice ETF a duration costante (maturity M) ----------------
def cm_index(M):
    cm=np.empty(T); cm[0]=100.0
    for t in range(1,T):
        y0=y[t-1]; dy=y[t]-y[t-1]; Dm,C=dur_conv(y0,M)
        cm[t]=cm[t-1]*(1+y0/12.0-Dm*dy+0.5*C*dy*dy)
    return cm

# ---------------- gamba obbligazioni tenute a scadenza (maturity M) ----------------
def htm_factor(t0,months,M):
    matm=int(round(M*12)); Fval=100.0; cpn=y[t0]; CA=0.0; mib=0; idx=t0
    for k in range(months):
        idx=t0+k; CA=CA*(1+s[idx]/12.0)+Fval*cpn/12.0; mib+=1
        if mib==matm:
            Fval=Fval+CA; cpn=(y[idx+1] if idx+1<T else y[idx]); CA=0.0; mib=0
    if mib==0: val=Fval
    else:
        rem=(matm-mib)/12.0; val=Fval*(bond_price(y[idx],cpn,rem)/100.0)+CA
    return val/100.0
def ann(f,yr): return f**(1.0/yr)-1.0

# ---------------- confronto principale a duration allineata (M_MAIN) ----------------
cm=cm_index(M_MAIN); cm_ser=pd.Series(cm,index=df["m"])
res={}
for H in (10,20):
    m=H*12; e=[]; h=[]; st=[]
    for t0 in range(0,T-m):
        e.append(ann(cm[t0+m]/cm[t0],H)); h.append(ann(htm_factor(t0,m,M_MAIN),H)); st.append(df["m"].iloc[t0])
    e=np.array(e); h=np.array(h); d=e-h
    res[H]={"etf":e,"htm":h,"diff":d,"start":st,"n":len(e),
        "diff_med":float(np.median(d)),"diff_p5":float(np.percentile(d,5)),"diff_p95":float(np.percentile(d,95)),
        "diff_std":float(d.std()),"diff_mae":float(np.abs(d).mean()),
        "etf_med":float(np.median(e)),"htm_med":float(np.median(h))}
    print(f"[{H}a M{M_MAIN}] mediana ETF-HTM {np.median(d)*100:+.2f}%/anno  p5..p95 {np.percentile(d,5)*100:+.2f}..{np.percentile(d,95)*100:+.2f}  |d|med {np.abs(d).mean()*100:.2f}")
dur_main,_=dur_conv(y[-1],M_MAIN)

# ---------------- contrasto didattico: vantaggio ETF per duration ----------------
contrast={}
for M in M_CONTRAST:
    cmx=cm_index(M); med={}
    for H in (10,20):
        m=H*12; d=[ann(cmx[t0+m]/cmx[t0],H)-ann(htm_factor(t0,m,M),H) for t0 in range(0,T-m)]
        med[H]=float(np.median(d))
    contrast[M]={"dur":float(dur_conv(0.04,M)[0]),"med10":med[10],"med20":med[20]}
    print(f"  contrasto M{M} (dur@4% {contrast[M]['dur']:.1f}): 10a {med[10]*100:+.2f}%  20a {med[20]*100:+.2f}%")

# ---------------- curva 'in quanto tempo' (M_MAIN) ----------------
horizons=list(range(1,26)); mae=[]
for H in horizons:
    m=H*12; d=np.array([ann(cm[t0+m]/cm[t0],H)-ann(htm_factor(t0,m,M_MAIN),H) for t0 in range(0,T-m)])
    mae.append(float(np.abs(d).mean()*100))

# ---------------- validazione IEF ----------------
ief_info=None
if os.path.exists(IEF):
    ie=pd.read_csv(IEF); dcol=[c for c in ie.columns if c.lower() in ("date","observation_date")][0]
    acol=[c for c in ie.columns if "adj" in c.lower()] or [c for c in ie.columns if c.lower()=="close"] or [c for c in ie.columns if "close" in c.lower()]
    ie["m"]=pd.PeriodIndex(pd.to_datetime(ie[dcol]),freq="M"); ies=ie.groupby("m")[acol[0]].last()
    ov=pd.DataFrame({"ief":ies,"cm":cm_ser}).dropna(); ov=ov[ov.index>=ies.index.min()]
    ief_n=ov["ief"]/ov["ief"].iloc[0]; cm_n=ov["cm"]/ov["cm"].iloc[0]
    yrs=(ov.index[-1]-ov.index[0]).n/12.0
    cagr_ief=ief_n.iloc[-1]**(1/yrs)-1; cagr_cm=cm_n.iloc[-1]**(1/yrs)-1
    corr=np.corrcoef(ief_n.pct_change().dropna(),cm_n.pct_change().dropna())[0,1]
    ief_info={"start":str(ov.index[0]),"end":str(ov.index[-1]),"years":round(yrs,1),
        "cagr_ief":float(cagr_ief),"cagr_cm":float(cagr_cm),"gap_annuo":float(cagr_cm-cagr_ief),
        "corr_mensile":float(corr),"_ief":ief_n,"_cm":cm_n}
    print(f"[IEF] {ov.index[0]}..{ov.index[-1]} CAGR IEF {cagr_ief*100:.2f}% vs sint {cagr_cm*100:.2f}% (gap {(cagr_cm-cagr_ief)*100:+.2f}%/a) corr {corr:.3f}")

# =========================================================================
FMTp=FuncFormatter(lambda v,_:f"{v:+.1f}%"); FMT=FuncFormatter(lambda v,_:f"{v:.0f}%")
# 01 — scatter 10/20 anni (duration allineata)
fig,axes=plt.subplots(1,2,figsize=(11,5.4),sharex=True,sharey=True)
for ax,H,col in zip(axes,(10,20),(NAVY,GREEN)):
    e=res[H]["etf"]*100; h=res[H]["htm"]*100; lim=[min(e.min(),h.min())-0.5,max(e.max(),h.max())+0.5]
    ax.plot(lim,lim,color=INK,lw=1,ls="--",zorder=1); ax.scatter(h,e,s=10,color=col,alpha=0.5,zorder=2)
    ax.set_title(f"Orizzonte {H} anni",fontweight="bold"); ax.set_xlabel("Obbligazioni a scadenza (annuo)")
    ax.xaxis.set_major_formatter(FMT); ax.yaxis.set_major_formatter(FMT)
axes[0].set_ylabel("ETF a duration costante (annuo)")
fig.suptitle(f"Stessa duration (~{it(dur_main)} anni). Ogni punto = una finestra storica",fontweight="bold",y=1.02)
fig.savefig(os.path.join(OUT,"01_scatter_10_20.png")); plt.close(fig)

# 02 — distribuzione della differenza (boxplot) 10/20
fig,ax=plt.subplots(figsize=(8.5,5.4))
bp=ax.boxplot([res[10]["diff"]*100,res[20]["diff"]*100],tick_labels=["10 anni","20 anni"],
    widths=0.5,patch_artist=True,whis=(5,95),showfliers=False)
for p,c in zip(bp["boxes"],[NAVY,GREEN]): p.set_facecolor(c); p.set_alpha(0.65)
for md in bp["medians"]: md.set_color(INK); md.set_linewidth(2)
ax.axhline(0,color=INK,lw=1); ax.set_ylabel("ETF − obbligazioni a scadenza (punti % annui)")
ax.yaxis.set_major_formatter(FMTp)
ax.set_title("A duration uguale, l'ETF ha un margine piccolo ma persistente",fontweight="bold")
fig.savefig(os.path.join(OUT,"02_distribuzione_diff.png")); plt.close(fig)

# 03 — contrasto duration: perche' bisogna confrontare la stessa duration
fig,ax=plt.subplots(figsize=(9,5.4))
xs=np.arange(len(M_CONTRAST)); w=0.38
v10=[contrast[M]["med10"]*100 for M in M_CONTRAST]; v20=[contrast[M]["med20"]*100 for M in M_CONTRAST]
ax.bar(xs-w/2,v10,w,color=NAVY,label="Orizzonte 10 anni"); ax.bar(xs+w/2,v20,w,color=GREEN,label="Orizzonte 20 anni")
for i,M in enumerate(M_CONTRAST):
    ax.text(i-w/2,v10[i]+0.02,f"+{it(v10[i],2)}",ha="center",va="bottom",fontsize=9)
    ax.text(i+w/2,v20[i]+0.02,f"+{it(v20[i],2)}",ha="center",va="bottom",fontsize=9)
ax.set_xticks(xs); ax.set_xticklabels([f"{M} anni\n(dur {it(contrast[M]['dur'])})" for M in M_CONTRAST])
ax.axvspan(0.5,1.5,color=GOLD,alpha=0.10)  # evidenzia M=8 (match IEF)
ax.set_ylabel("Vantaggio annuo dell'ETF (mediana)"); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"+{v:.1f}%"))
ax.set_title("Confronta la stessa duration: il vantaggio 'ingenuo' del 10Y si sgonfia",fontweight="bold")
ax.legend(frameon=False,fontsize=10)
fig.savefig(os.path.join(OUT,"03_contrasto_duration.png")); plt.close(fig)

# 04 — contrasto di regime: dipende da cosa fanno i tassi nel ventennio
diff20=res[20]["diff"]; starts20=res[20]["start"]
t_rise=int(np.argmin(diff20))   # tassi in salita: vince chi tiene a scadenza
t_fall=int(np.argmax(diff20))   # tassi in calo: vince l'ETF
def path(t0):
    se=cm[t0:t0+240]/cm[t0]*100; hh=np.array([htm_factor(t0,k+1,M_MAIN) for k in range(240)])*100
    ix=pd.period_range(df["m"].iloc[t0],periods=240,freq="M").to_timestamp(); return ix,se,hh
fig,axes=plt.subplots(1,2,figsize=(11.5,5.4),sharey=True)
for ax,t0,sub in zip(axes,(t_rise,t_fall),("Tassi in salita: vince chi tiene a scadenza","Tassi in calo: vince l'ETF")):
    ix,se,hh=path(t0)
    ax.plot(ix,se,color=NAVY,lw=2.2,label="ETF a duration costante")
    ax.plot(ix,hh,color=GOLD,lw=2.2,label="Obbligazioni tenute a scadenza")
    ax.set_title(f"Dal {starts20[t0]} — {sub}",fontweight="bold",fontsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}"))
axes[0].set_ylabel("Valore di 100 investiti"); axes[0].legend(frameon=False,fontsize=9)
fig.suptitle("Stesso confronto, due epoche opposte: il regime dei tassi decide chi vince",fontweight="bold",y=1.02)
fig.savefig(os.path.join(OUT,"04_regimi.png")); plt.close(fig)
# CSV per il reel: la coorte a tassi in calo (piu' dinamica, l'ETF stacca)
ix,se,hh=path(t_fall)
pd.DataFrame({"Date":ix,"ETF a duration costante":se,"Obbligazioni a scadenza":hh}
    ).to_csv(os.path.join(OUT,"equity_curves_esempio.csv"),index=False)

# 05 — validazione IEF
if ief_info:
    fig,ax=plt.subplots(figsize=(10,5.6))
    ax.plot(ief_info["_ief"].index.to_timestamp(),ief_info["_ief"].values*100-100,color=GOLD,lw=2.4,label="IEF reale (iShares 7-10Y)")
    ax.plot(ief_info["_cm"].index.to_timestamp(),ief_info["_cm"].values*100-100,color=NAVY,lw=2.0,ls="--",label="Indice sintetico (duration allineata)")
    ax.set_title(f"Il sintetico traccia il reale (corr. {it(ief_info['corr_mensile'],2)}); rende ~{it(-ief_info['gap_annuo']*100,1)}%/anno meno\nper il roll-down non catturato dalla ricostruzione lunga",fontweight="bold",fontsize=12)
    ax.set_ylabel("Rendimento cumulato"); ax.legend(frameon=False,fontsize=10)
    ax.yaxis.set_major_formatter(FMT); fig.savefig(os.path.join(OUT,"05_ief_vs_sintetico.png")); plt.close(fig)

# ---------------- caso peggiore (estremi della distribuzione, duration allineata) ----------------
worst={}
for H in (10,20):
    dd=res[H]["diff"]; e=res[H]["etf"]; h=res[H]["htm"]; st=res[H]["start"]
    iw=int(np.argmin(dd)); ib=int(np.argmax(dd))   # peggiore per ETF, peggiore per chi tiene a scadenza
    def rec(i):
        return {"start":str(st[i]),"etf_ann":round(float(e[i]),4),"htm_ann":round(float(h[i]),4),
                "gap_ann":round(float(dd[i]),4),
                "gap_tot":round(float((1+e[i])**H/(1+h[i])**H-1),4),
                "etf_10k":round(10000*(1+e[i])**H,0),"htm_10k":round(10000*(1+h[i])**H,0)}
    worst[str(H)]={"etf_peggiore":rec(iw),"htm_peggiore":rec(ib)}
    print(f"[caso peggiore {H}a] ETF: ingresso {st[iw]} gap {dd[iw]*100:+.2f}%/a ({(( 1+e[iw])**H/(1+h[iw])**H-1)*100:+.1f}% tot) | "
          f"scadenza: ingresso {st[ib]} mancato +{dd[ib]*100:.2f}%/a ({((1+e[ib])**H/(1+h[ib])**H-1)*100:+.1f}% tot)")

summary={"slug":SLUG,"periodo":f"{df['m'].iloc[0]}..{df['m'].iloc[-1]}","n_mesi":T,"caso_peggiore":worst,
    "maturity_principale":M_MAIN,"duration_principale":round(dur_main,2),
    "finestre":{str(H):{k:round(res[H][k],5) for k in("diff_med","diff_p5","diff_p95","diff_std","diff_mae","etf_med","htm_med","n")} for H in(10,20)},
    "contrasto_duration":{str(M):{k:round(v,5) for k,v in contrast[M].items()} for M in M_CONTRAST},
    "curva_orizzonte":{"anni":horizons,"mae_pct":[round(x,3) for x in mae]},
    "ief":({k:(round(v,4) if isinstance(v,float) else v) for k,v in ief_info.items() if not k.startswith("_")} if ief_info else None)}
json.dump(summary,open(os.path.join(OUT,"summary.json"),"w"),ensure_ascii=False,indent=2)
print("\n[ok] grafici + summary.json in",OUT)
