# -*- coding: utf-8 -*-
"""
STUDIO (fase risultati, non articolo): fondo pensione vs ETF quando si incorpora
il RECUPERO DELLE DETRAZIONI (dipendente + cuneo fiscale) nel beneficio in entrata.
Solo caso TRATTENUTA in busta paga (art.51: la quota aderente e' esclusa alla fonte
dal reddito di lavoro -> abbassa il reddito complessivo su cui si calcolano le detrazioni).
Nessun contributo datoriale. Parametri fiscali 2026. Addizionali generiche.
"""
import numpy as np, pandas as pd, os, json

# ---------------- parametri fiscali 2026
INPS      = 0.0949
INPS_SOG  = 55448.0            # soglia 1% aggiuntivo (valore 2025, generico)
ADD_REG   = 0.015             # addizionale regionale generica (media IT)
ADD_COM   = 0.007             # addizionale comunale generica (media IT)
CAP       = 5300.0            # tetto deducibilita' 2026

def irpef_lorda(imp):
    s=0.0
    for lim,al in [(28000,0.23),(50000,0.33),(1e18,0.43)]:
        if imp>lim: s+=(lim- (0 if lim==28000 else (28000 if lim==50000 else 0)))*0  # placeholder
    # calcolo progressivo pulito
    s=0.0; prev=0.0
    for lim,al in [(28000,0.23),(50000,0.33),(1e18,0.43)]:
        if imp>lim: s+=(lim-prev)*al; prev=lim
        else: s+=(imp-prev)*al; break
    return s

def detr_dip(rc):
    if rc<=15000: return 1955.0
    if rc<=28000: return 1910.0+1190.0*(28000-rc)/13000.0
    if rc<=50000: return 1910.0*(50000-rc)/22000.0
    return 0.0

def ulteriori(rc):
    return 65.0 if 25000<rc<=35000 else 0.0

def cuneo(rc):
    """ritorna (somma_esente, detrazione). rc = reddito complessivo = reddito lavoro (no altri redditi)."""
    if rc<=20000:
        if rc<=8500: p=0.071
        elif rc<=15000: p=0.053
        else: p=0.048
        return rc*p, 0.0
    if rc<=32000: return 0.0, 1000.0
    if rc<=40000: return 0.0, 1000.0*(40000-rc)/8000.0
    return 0.0, 0.0

def take_home(ral, quota, trattenuta=True):
    inps=ral*INPS; inps_agg=max(0.0,ral-INPS_SOG)*0.01
    if trattenuta:
        rc = ral-inps-inps_agg-quota      # art.51: quota fuori dal reddito lavoro
        imp = rc
    else:                                 # bonifico: art.10 onere deducibile
        rc = ral-inps-inps_agg
        imp = rc-quota
    irpef=irpef_lorda(imp)
    d_dip=detr_dip(rc); d_ult=ulteriori(rc); somma,d_cun=cuneo(rc)
    irpef_netta=max(0.0, irpef-d_dip-d_ult-d_cun)
    return ral-inps-inps_agg-quota-irpef_netta-imp*ADD_REG-imp*ADD_COM+somma

def marginale_nominale(ral):
    inps=ral*INPS; imp=ral-inps
    return 0.23 if imp<=28000 else (0.33 if imp<=50000 else 0.43)

# ---------------- validazione contro il quaderno (componenti rate-independent)
rc=33500.20
assert abs(detr_dip(rc)-1432.48)<0.02, detr_dip(rc)
assert ulteriori(rc)==65.0
assert abs(cuneo(rc)[1]-812.48)<0.02, cuneo(rc)
assert abs(detr_dip(38014.20)-1040.59)<0.02
assert abs(cuneo(38014.20)[1]-248.23)<0.02
print("[ok] validazione componenti quaderno superata\n")

# ---------------- motore ETF (identico all'articolo)
ROOT="."; panel=pd.read_csv(os.path.join(ROOT,"data","processed","returns_panel_wide.csv"))
col="Developed Markets Large"; WIN=120; WHT=0.0040
v=panel[["month",col]].dropna()[col].values
cagr=np.array([(v[i+WIN]/v[i])**(12/WIN)-1 for i in range(len(v)-WIN)])
R_BASE=float(np.median(cagr))-WHT
TER=0.0020; BOLLO=0.0020; CG=0.26; N=30; FUND_NET=0.050; AL_USCITA=0.105
def acc(C,g,n=N):
    x=0.0
    for _ in range(n): x=x*(1+g)+C
    return x
def netto_etf(C): 
    x=acc(C,R_BASE-TER-BOLLO); return x-CG*max(x-C*N,0)
FP_NETTO=acc(CAP,FUND_NET)-AL_USCITA*CAP*N
FP_LORDO=acc(CAP,FUND_NET)
print(f"ETF MSCI World rolling 10y: mediana netta {R_BASE*100:.2f}%  |  Fondo 5% netto")
print(f"FP netto a 30 anni: {FP_NETTO:,.0f} EUR (lordo {FP_LORDO:,.0f}, versato {CAP*N:,.0f})\n")

# ---------------- tabella per RAL
RALS=[25000,28000,30000,32000,35000,38000,40000,42000,45000,50000,55000,60000,70000,80000]
print(f"{'RAL':>6} {'imp.noFP':>9} {'imp.FP':>8} {'b_tratt':>8} {'b_bonif':>8} {'marg':>5} "
      f"{'esbNetto':>9} {'ETFnetto':>9} {'delta':>9} {'vince':>6}")
rows=[]
for ral in RALS:
    n0=take_home(ral,0.0,True); n1=take_home(ral,CAP,True)
    cost=n0-n1; b_tr=1-cost/CAP
    nb0=take_home(ral,0.0,False); nb1=take_home(ral,CAP,False); b_bo=1-(nb0-nb1)/CAP
    esb=CAP*(1-b_tr); etf=netto_etf(esb); delta=FP_NETTO-etf
    win="FONDO" if delta>0 else "ETF"
    print(f"{ral/1000:>5.0f}k {ral-ral*INPS:>9.0f} {ral-ral*INPS-CAP:>8.0f} "
          f"{b_tr*100:>7.1f}% {b_bo*100:>7.1f}% {marginale_nominale(ral)*100:>4.0f}% "
          f"{esb:>9.0f} {etf:>9.0f} {delta:>+9.0f} {win:>6}")
    rows.append({"ral":ral,"b_trattenuta":b_tr,"b_bonifico":b_bo,
                 "esborso_netto":esb,"etf_netto":etf,"fp_netto":FP_NETTO,"delta":delta})

json.dump({"R_BASE":R_BASE,"FP_NETTO":FP_NETTO,"rows":rows},
          open("/tmp/studio_fp_detrazioni.json","w"),indent=2,default=float)
print("\n[ok] studio completato")

# ============================================================ BREAK-EVEN
# A parita' di esborso netto: quale rendimento annuo dell'ETF (stesso metro
# dell'8,29% dichiarato = netto ritenute, lordo di TER/bollo/CG) pareggia il
# fondo al 5% netto? E quindi di quanto deve battere il fondo?
def netto_etf_r(C, r):
    x=acc(C, r-TER-BOLLO); return x-CG*max(x-C*N,0)
def r_pareggio(esb):
    lo,hi=0.0,0.30
    for _ in range(100):
        mid=(lo+hi)/2
        if netto_etf_r(esb,mid) < FP_NETTO: lo=mid
        else: hi=mid
    return (lo+hi)/2
print("\n\n=== BREAK-EVEN: rendimento ETF necessario per pareggiare il fondo (5% netto) ===")
print(f"(mediana storica ETF MSCI World, stesso metro: {R_BASE*100:.2f}%)\n")
print(f"{'RAL':>6} {'b_tratt':>8} {'esbNetto':>9} {'r_pareggio':>11} {'extra vs 5%':>12} {'margine vs 8,29%':>16}")
for ral in RALS:
    n0=take_home(ral,0.0,True); n1=take_home(ral,CAP,True); b=1-(n0-n1)/CAP
    esb=CAP*(1-b); rp=r_pareggio(esb)
    extra=rp-FUND_NET; margine=rp-R_BASE
    print(f"{ral/1000:>5.0f}k {b*100:>7.1f}% {esb:>9.0f} {rp*100:>10.2f}% "
          f"{extra*100:>+11.2f}pt {margine*100:>+13.2f}pt")
print("\n[interpretazione] r_pareggio = rendimento annuo che l'ETF dovrebbe realizzare")
print("per pareggiare; 'margine' = quanto sopra la mediana storica (8,29%) deve spingersi.")
print("Se margine > 0 il fondo vince (l'ETF dovrebbe fare meglio del suo massimo tipico).")

# ============================================================ GRAFICI (scenario trattenuta)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"; VIOLET="#8b5cf6"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})
OUT="public/charts/fondo-pensione-o-etf"; import os; os.makedirs(OUT,exist_ok=True)
def it(x,d=1): return f"{x:.{d}f}".replace(".",",")

grid=np.arange(25000,80001,500)
btr=np.array([1-(take_home(r,0.,True)-take_home(r,CAP,True))/CAP for r in grid])
bbo=np.array([1-(take_home(r,0.,False)-take_home(r,CAP,False))/CAP for r in grid])
marg=np.array([marginale_nominale(r) for r in grid])
delta=np.array([FP_NETTO-netto_etf(CAP*(1-b)) for b in btr])
rpar=np.array([r_pareggio(CAP*(1-b)) for b in btr])

# --- 06 beneficio in entrata per RAL: trattenuta vs bonifico vs marginale
fig,ax=plt.subplots(figsize=(11.4,5.6))
ax.fill_between(grid/1000, bbo*100, btr*100, color=NAVY, alpha=0.12, label="Recupero detrazioni (dipendente + cuneo)")
ax.plot(grid/1000, btr*100, color=NAVY, lw=2.8, label="Quota trattenuta in busta paga")
ax.plot(grid/1000, bbo*100, color=GOLD, lw=2.4, ls="--", label="Versamento con bonifico (solo marginale + addizionali)")
ax.step(grid/1000, marg*100, color=GREY, lw=1.6, where="mid", label="Aliquota marginale IRPEF nominale")
ipk=int(np.argmax(btr)); ax.scatter([grid[ipk]/1000],[btr[ipk]*100],color=RED,zorder=5,s=45)
ax.annotate(f"picco {it(btr[ipk]*100)}%  (RAL {grid[ipk]/1000:.0f}k)", xy=(grid[ipk]/1000,btr[ipk]*100),
    xytext=(grid[ipk]/1000+6,btr[ipk]*100+2), fontsize=10.5, weight="bold", color=RED,
    arrowprops=dict(arrowstyle="->",color=RED))
ax.set_xlabel("RAL (reddito annuo lordo)"); ax.set_ylabel("Beneficio fiscale sull'importo versato")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k")); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
ax.set_ylim(20,65); ax.legend(fontsize=9.3,loc="upper right")
ax.set_title("Con la quota trattenuta in busta paga il vantaggio fiscale supera di molto l'aliquota\n"
             "(perché abbassa il reddito complessivo e fa recuperare le detrazioni)", fontsize=12.5, weight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/06_beneficio_per_ral.png"); plt.close(fig)

# --- 07 delta fondo-ETF per RAL (barre)
RALS=[25000,28000,30000,32000,35000,38000,40000,42000,45000,50000,55000,60000,70000,80000]
dl=np.array([FP_NETTO-netto_etf(CAP*(1-(1-(take_home(r,0.,True)-take_home(r,CAP,True))/CAP))) for r in RALS])
fig,ax=plt.subplots(figsize=(11.6,5.4))
x=np.arange(len(RALS))
bars=ax.bar(x, dl/1000, 0.62, color=[GREEN if d>0 else RED for d in dl])
for xi,d in zip(x,dl):
    ax.text(xi, d/1000+2.5, f"+{d/1000:.0f}k", ha="center", fontsize=9.2, weight="bold", color=INK)
ax.axhline(0,color=INK,lw=1)
ax.set_xticks(x); ax.set_xticklabels([f"{r//1000}k" for r in RALS], fontsize=9.5)
ax.set_xlabel("RAL"); ax.set_ylabel("Vantaggio netto del fondo dopo 30 anni")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k€"))
ax.set_title("A parità di esborso netto e con la trattenuta, il fondo vince su tutta la fascia di reddito\n"
             f"(fondo 5% netto vs ETF MSCI World {it(R_BASE*100,2)}%; nessun contributo datoriale)", fontsize=12, weight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/07_delta_per_ral.png"); plt.close(fig)

# --- 08 break-even: rendimento ETF necessario a pareggiare
fig,ax=plt.subplots(figsize=(11.4,5.4))
ax.fill_between(grid/1000, R_BASE*100, rpar*100, where=(rpar>=R_BASE), color=GREEN, alpha=0.14)
ax.plot(grid/1000, rpar*100, color=NAVY, lw=2.8, label="Rendimento ETF necessario per pareggiare il fondo")
ax.axhline(R_BASE*100, color=RED, lw=2.0, ls="--", label=f"Mediana storica ETF MSCI World ({it(R_BASE*100,2)}%)")
ax.axhline(FUND_NET*100, color=GREY, lw=1.6, ls=":", label="Fondo pensione (5% netto)")
ipk=int(np.argmax(rpar))
ax.annotate(f"{it(rpar[ipk]*100)}%", xy=(grid[ipk]/1000,rpar[ipk]*100), xytext=(grid[ipk]/1000+5,rpar[ipk]*100+0.3),
    fontsize=11, weight="bold", color=NAVY, arrowprops=dict(arrowstyle="->",color=NAVY))
ax.set_xlabel("RAL"); ax.set_ylabel("Rendimento annuo dell'ETF")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k")); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:it(v,0)+"%"))
ax.set_ylim(4,12.5); ax.legend(fontsize=9.5, loc="center right")
ax.set_title("Quanto dovrebbe rendere l'ETF per pareggiare il fondo (scenario trattenuta)\n"
             "l'area verde è il margine che l'ETF deve strappare oltre la sua mediana storica", fontsize=12.3, weight="bold")
fig.tight_layout(); fig.savefig(f"{OUT}/08_breakeven_per_ral.png"); plt.close(fig)
print("\n[ok] 3 grafici salvati in", OUT)
