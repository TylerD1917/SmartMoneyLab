"""
Fondo pensione (contribuzione volontaria deducibile) o ETF azionario globale?
Articolo SEO pilastro #5. — REVISIONE 2026-08-27: il fondo pensione è guidato
dal RENDIMENTO NETTO REALE dei comparti azionari COVIP (~5% annuo, 2016-2025),
NON dallo stesso rendimento lordo dell'ETF globale. Coerente con l'articolo #3.

Il 5% COVIP è già netto di costi di gestione e dell'imposta annua del 20%: quindi
il montante del fondo cresce direttamente a quel tasso, e si applica solo la tassa
d'uscita (10,5% a 30 anni) sui contributi. La deduzione resta il vantaggio-chiave.

Manteniamo uno scenario secondario "a PARITÀ DI RENDIMENTO LORDO di mercato"
(il fondo riceve il gross dell'indice, poi −ISC e ×(1−20%) → ~6,2%): isola il
puro effetto del veicolo fiscale, dove il fondo torna a vincere più spesso.

  Scenario 1 (FP)  : versa il massimo deducibile (5.300 EUR/anno, L. Bilancio 2026)
  Scenario 2 (ETF) : investe l'equivalente ESBORSO NETTO, 5.300*(1-aliquota)

Output: public/charts/fondo-pensione-o-etf/*.png + summary.json
"""
import os, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "public", "charts", "fondo-pensione-o-etf"); os.makedirs(OUT, exist_ok=True)

NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

def eur(v, _=None): return f"{v/1000:.0f}k€"
def kfmt(v, _=None): return f"{v:.0f}k€"
def it(x, d=1): return f"{x:.{d}f}".replace(".", ",")

# ------------------------------------------------------------------ 1. MOTORE ETF
INDICI = {"MSCI World":"Developed Markets Large", "FTSE All-World":"ACWI", "S&P 500":"US Large"}
BASE_INDEX = "MSCI World"
WHT   = 0.0040                     # ritenute alla fonte sui dividendi (gross->net)
WIN   = 120                        # finestra mobile 10 anni

panel = pd.read_csv(os.path.join(ROOT, "data", "processed", "returns_panel_wide.csv"))
motore = {}
for nome, col in INDICI.items():
    s = panel[["month", col]].dropna().reset_index(drop=True); v = s[col].values
    cagr = np.array([(v[i+WIN]/v[i])**(12/WIN) - 1 for i in range(len(v)-WIN)])
    motore[nome] = {"col":col, "n_finestre":len(cagr), "periodo":[s.month.iloc[0], s.month.iloc[-1]],
        "cagr":cagr, "mediana":float(np.median(cagr)), "media":float(cagr.mean()),
        "min":float(cagr.min()), "max":float(cagr.max()),
        "r_netto_div":float(np.median(cagr) - WHT)}
_per = {tuple(m["periodo"]) for m in motore.values()}; _nf = {m["n_finestre"] for m in motore.values()}
assert len(_per)==1 and len(_nf)==1, "indici su periodi diversi"
R_BASE = motore[BASE_INDEX]["r_netto_div"]

# --------------------------------------------------------- 2. PARAMETRI FISCO
N          = 30
CAP        = 5300.0       # tetto deducibilità 2026 (L. Bilancio 2026)
AL_USCITA  = 0.105        # 15% - 0,3%/anno oltre il 15° -> 30 anni = 10,5%
TER_ETF    = 0.0020
BOLLO      = 0.0020
CG_ETF     = 0.26

# FONDO PENSIONE: rendimento NETTO reale dei comparti azionari (COVIP 2016-2025).
# Già netto di costi e imposta annua 20%: si usa direttamente come crescita.
FUND_NET   = 0.050
# Scenario "a parità di rendimento lordo di mercato": il fondo riceve il gross
# dell'indice, poi -ISC e ×(1-imposta annua) -> isola l'effetto del veicolo.
ISC_FP     = 0.0050
TAX_ANNUA  = 0.20
FUND_NET_EQUALGROSS = (R_BASE - ISC_FP)*(1 - TAX_ANNUA)

ALIQUOTE      = {"23%":0.23, "33%":0.33, "43%":0.43}
AL_PRINCIPALI = ["23%", "33%"]

def acc(C, g, n=N):
    v = 0.0
    for _ in range(n): v = v*(1+g) + C
    return v
def g_etf(r): return r - TER_ETF - BOLLO
def netto_etf(C, r):
    v = acc(C, g_etf(r)); return v - CG_ETF*max(v - C*N, 0.0)
def netto_fp(gnet):
    v = acc(CAP, gnet); return v - AL_USCITA*CAP*N

FP_NETTO      = netto_fp(FUND_NET)                 # non dipende dall'indice
FP_NETTO_EG   = netto_fp(FUND_NET_EQUALGROSS)      # scenario parità di lordo
FP_LORDO      = acc(CAP, FUND_NET)

# ------------------------------------------------- 3. RISULTATI PER INDICE/ALIQUOTA
risultati = {}
for nome, m in motore.items():
    r = m["r_netto_div"]; blocco = {"r":r, "per_aliquota":{}}
    for lab, t in ALIQUOTE.items():
        c_net = CAP*(1-t)
        etf_l = acc(c_net, g_etf(r)); etf_n = netto_etf(c_net, r)
        blocco["per_aliquota"][lab] = {"aliquota":t, "esborso_netto_anno":c_net,
            "esborso_netto_tot":c_net*N, "etf_lordo":etf_l, "etf_netto":etf_n,
            "etf_tassa_cg":etf_l-etf_n, "delta":FP_NETTO-etf_n,
            "delta_pct":FP_NETTO/etf_n-1, "vince":"FP" if FP_NETTO>etf_n else "ETF"}
    risultati[nome] = blocco

# aliquota di pareggio (indice base): sotto vince ETF, sopra vince FP
def _etf_at(t): return netto_etf(CAP*(1-t), R_BASE)
lo, hi = 0.10, 0.50
for _ in range(80):
    mid = (lo+hi)/2
    if _etf_at(mid) > FP_NETTO: lo = mid
    else: hi = mid
AL_PAREGGIO = (lo+hi)/2

# ------------------------------------------------- 4. HEATMAP: rendimento fondo × aliquota
gnet_grid = np.linspace(0.030, 0.080, 61)
al_grid   = np.array([0.23, 0.28, 0.33, 0.38, 0.43])
heat = np.array([[netto_fp(g) - netto_etf(CAP*(1-t), R_BASE) for g in gnet_grid] for t in al_grid])

# ---------------------------------------------------- 5. WATERFALL (base index)
def waterfall(t):
    c_net = CAP*(1-t)
    s0 = netto_etf(c_net, R_BASE)          # ETF netto (esborso netto)
    s1 = netto_etf(CAP,   R_BASE)          # + leva della deduzione (investe 5.300 pieni)
    lordo_etf = acc(CAP, g_etf(R_BASE)); cg = CG_ETF*max(lordo_etf-CAP*N,0)
    s2 = FP_LORDO - cg                     # - minor rendimento del fondo (5% vs ~7,9%)
    s3 = FP_NETTO                          # + tassa finale ridotta (10,5% vs 26%)
    return {"ETF netto":s0, "Leva della deduzione":s1-s0,
            "Minor rendimento del fondo":s2-s1, "Tassa finale 10,5% vs 26%":s3-s2,
            "Fondo pensione":s3}
wf = {lab: waterfall(ALIQUOTE[lab]) for lab in AL_PRINCIPALI}

# ================================================================= GRAFICI
COL_IDX = {"MSCI World":NAVY, "FTSE All-World":GOLD, "S&P 500":RED}

# --- 01 motore ETF (rolling 10y) con riferimento fondo pensione COVIP ---------
fig, (ax, axb) = plt.subplots(1, 2, figsize=(12.6,5.4), gridspec_kw={"width_ratios":[1.6,1]})
for nome, m in motore.items():
    ax.hist(m["cagr"]*100, bins=26, alpha=0.42, color=COL_IDX[nome], label=nome)
    ax.axvline(m["mediana"]*100, color=COL_IDX[nome], lw=2.0, ls="--")
ax.axvline(FUND_NET*100, color=GREEN, lw=2.6)
ax.text(FUND_NET*100-0.2, ax.get_ylim()[1]*0.92, "Fondo pensione\nazionario (COVIP)\n5% netto",
        color=GREEN, ha="right", va="top", fontsize=9.5, weight="bold")
ax.set_xlabel("CAGR dei 10 anni successivi (ETF, lordo di tasse)"); ax.set_ylabel("Numero di finestre")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}%"))
per = motore[BASE_INDEX]["periodo"]; nfin = motore[BASE_INDEX]["n_finestre"]
ax.set_title(f"{nfin} finestre mobili a 10 anni ({per[0]} → {per[1]})", fontsize=12, weight="bold")
ax.legend(fontsize=9.5)
nomi = list(motore); x = np.arange(len(nomi)); w = 0.55
b1 = axb.bar(x, [motore[n]["mediana"]*100 for n in nomi], w, color=[COL_IDX[n] for n in nomi])
axb.axhline(FUND_NET*100, color=GREEN, lw=2.4, ls="--")
axb.text(len(nomi)-0.5, FUND_NET*100+0.15, "fondo 5%", color=GREEN, ha="right", fontsize=9.5, weight="bold")
for b in b1: axb.text(b.get_x()+b.get_width()/2, b.get_height()+0.12, it(b.get_height()), ha="center", fontsize=9.5)
axb.set_xticks(x); axb.set_xticklabels([n.replace(" ","\n") for n in nomi], fontsize=9)
axb.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}%"))
axb.set_title("Mediana ETF vs fondo pensione", fontsize=11.5, weight="bold")
fig.suptitle("L'ETF globale ha reso di più del fondo pensione azionario reale", fontsize=13.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_rolling_10y.png")); plt.close(fig)

# --- 02 montanti a confronto, i due profili affiancati -----------------------
fig, axes = plt.subplots(1, 2, figsize=(12.8,5.6), sharey=True)
for ax, lab in zip(axes, AL_PRINCIPALI):
    d = risultati[BASE_INDEX]["per_aliquota"][lab]
    vals_l = [FP_LORDO, d["etf_lordo"]]; vals_n = [FP_NETTO, d["etf_netto"]]
    xx = np.arange(2)
    ax.bar(xx, [v/1000 for v in vals_l], 0.52, color=GREY, label="Lordo (prima delle tasse finali)")
    ax.bar(xx, [v/1000 for v in vals_n], 0.52, color=[NAVY, GOLD], label="Netto in tasca")
    for i,(l,n) in enumerate(zip(vals_l, vals_n)):
        ax.text(i, n/1000-12, eur(n), ha="center", va="top", color="white", fontsize=11.5, weight="bold")
        ax.text(i, l/1000+6, eur(l), ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(xx); ax.set_xticklabels(["Fondo pensione\n5.300€/anno",
        "ETF globale\n"+f"{d['esborso_netto_anno']:,.0f}€/anno".replace(",",".")], fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(kfmt)); ax.set_ylim(0, 480)
    ax.set_title(f"Aliquota marginale {lab}\nesborso netto identico: {d['esborso_netto_tot']/1000:.0f}k€ in 30 anni",
                 fontsize=11.5, weight="bold")
    ax.annotate(f"{'+' if d['delta']>0 else ''}{d['delta']/1000:.0f}k€  ({d['delta_pct']*100:+.0f}%)".replace(".",",")
                + ("  vince il fondo" if d['delta']>0 else "  vince l'ETF"),
                xy=(0.5, max(vals_l)/1000*0.40), ha="center", fontsize=12.5, weight="bold",
                color=GREEN if d["delta"]>0 else RED)
axes[0].set_ylabel("Valore dopo 30 anni")
axes[0].legend(fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 0.99), framealpha=0.95)
fig.suptitle("A parità di esborso netto, dopo 30 anni: fondo pensione (5% COVIP) contro ETF globale\n"
             f"(ETF: {BASE_INDEX}, {it(R_BASE*100,2)}% annuo; fondo: rendimento netto reale dei comparti azionari)",
             fontsize=12.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_montanti.png")); plt.close(fig)

# --- 03 waterfall: da dove nasce la differenza -------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13.2,5.9), sharey=True)
SHORT = {"Leva della deduzione":"Leva della\ndeduzione",
         "Minor rendimento del fondo":"Minor\nrendimento",
         "Tassa finale 10,5% vs 26%":"Tassa finale\n10,5% vs 26%"}
for ax, lab in zip(axes, AL_PRINCIPALI):
    w_ = wf[lab]; keys = list(w_); steps = keys[1:-1]
    start = w_["ETF netto"]; end = w_["Fondo pensione"]
    labels = ["ETF\nnetto"] + [SHORT[k] for k in steps] + ["Fondo\npensione"]
    run = start; xs=[0]; heights=[start/1000]; bottoms=[0]; colors=[GOLD]
    for i,k in enumerate(steps, start=1):
        v = w_[k]; bottoms.append(min(run, run+v)/1000); heights.append(abs(v)/1000)
        colors.append(GREEN if v>0 else RED); xs.append(i); run += v
    xs.append(len(steps)+1); heights.append(end/1000); bottoms.append(0); colors.append(NAVY)
    ax.bar(xs, heights, 0.6, bottom=bottoms, color=colors)
    run = start
    for i,k in enumerate(steps, start=1):
        v = w_[k]; ax.text(i, max(run, run+v)/1000+6, f"{v/1000:+.0f}k".replace(".",","),
                           ha="center", fontsize=10, weight="bold", color=GREEN if v>0 else RED); run += v
    ax.text(0, start/1000+6, eur(start), ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.text(len(steps)+1, end/1000+6, eur(end), ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(kfmt)); ax.set_ylim(0, max(heights+bottoms)*1.30)
    ax.set_title(f"Aliquota marginale {lab}", fontsize=12, weight="bold")
axes[0].set_ylabel("Valore netto dopo 30 anni")
axes[0].legend(handles=[Patch(color=GREEN,label="A favore del fondo"), Patch(color=RED,label="A sfavore del fondo")],
               fontsize=9.5, loc="upper right")
fig.suptitle("Da dove nasce la differenza: la deduzione aiuta, il minor rendimento del fondo pesa",
             fontsize=13.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_waterfall.png")); plt.close(fig)

# --- 04 heatmap rendimento del fondo × aliquota ------------------------------
fig, ax = plt.subplots(figsize=(11.4,4.9))
lim = np.abs(heat).max()/1000
im = ax.imshow(heat/1000, aspect="auto", cmap="RdYlGn", vmin=-lim, vmax=lim, origin="lower",
               extent=[gnet_grid[0]*100, gnet_grid[-1]*100, -0.5, len(al_grid)-0.5])
cs = ax.contour(gnet_grid*100, np.arange(len(al_grid)), heat/1000, levels=[0], colors=INK, linewidths=2.4)
ax.clabel(cs, fmt={0:" pareggio "}, fontsize=10)
ax.set_yticks(np.arange(len(al_grid))); ax.set_yticklabels([f"{t:.0%}" for t in al_grid])
ax.set_ylabel("Aliquota marginale IRPEF"); ax.set_xlabel("Rendimento netto annuo del fondo pensione")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: it(v,0)+"%"))
ax.grid(False)
ax.axvline(FUND_NET*100, color=INK, lw=1.4, ls=":")
ax.text(FUND_NET*100, len(al_grid)-0.42, " COVIP reale 5%", rotation=90, va="top", fontsize=9, color=INK)
ax.axvline(FUND_NET_EQUALGROSS*100, color=INK, lw=1.1, ls=":")
ax.text(FUND_NET_EQUALGROSS*100, len(al_grid)-0.42, " a parità di lordo", rotation=90, va="top", fontsize=9, color=INK)
cb = fig.colorbar(im, ax=ax); cb.set_label("Vantaggio del fondo\nsull'ETF (k€ netti)", fontsize=10)
ax.set_title("Serve rendimento O aliquota alta: col 5% reale il fondo vince solo da ~30% di aliquota\n"
             f"(ETF: {BASE_INDEX}; verde = vince il fondo, rosso = vince l'ETF)", fontsize=12.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"04_heatmap_rendimento_aliquota.png")); plt.close(fig)

# --- 05 robustezza: stesso esercizio con i tre indici ETF --------------------
fig, ax = plt.subplots(figsize=(10.6,5.2))
labs = ["23%","33%","43%"]; xx = np.arange(len(labs)); w = 0.26
for j, nome in enumerate(nomi):
    vals = [risultati[nome]["per_aliquota"][l]["delta"]/1000 for l in labs]
    b = ax.bar(xx + (j-1)*w, vals, w, color=COL_IDX[nome], label=f"{nome} ({it(motore[nome]['mediana']*100,1)}%)")
    for r_ in b:
        h=r_.get_height(); ax.text(r_.get_x()+r_.get_width()/2, h+(2 if h>=0 else -2),
            f"{h:.0f}", ha="center", va="bottom" if h>=0 else "top", fontsize=9)
ax.set_xticks(xx); ax.set_xticklabels([f"Aliquota {l}" for l in labs])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}k€"))
ax.set_ylabel("Vantaggio netto del fondo pensione"); ax.axhline(0, color=INK, lw=1)
ax.set_title("Robustezza: col fondo al 5% reale, sotto il 33% vince l'ETF su tutti gli indici\n"
             "(fondo pensione azionario COVIP 5% netto; in parentesi la mediana ETF rolling 10 anni)",
             fontsize=12, weight="bold")
ax.legend(fontsize=10, title="ETF (motore di rendimento)", title_fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"05_robustezza_indici.png")); plt.close(fig)

# ================================================================= SUMMARY
summary = {
    "metodo":{"finestra_anni":10, "indice_base_ETF":BASE_INDEX,
        "fondo_rendimento_netto_COVIP":FUND_NET, "fondo_scenario_parita_lordo":FUND_NET_EQUALGROSS,
        "impostazione":"parità di esborso netto in tasca; il 5% COVIP è già netto di costi e imposta annua",
        "aliquota_di_pareggio_base":AL_PAREGGIO},
    "parametri":{"anni":N, "tetto_deducibile":CAP, "aliquota_uscita_30anni":AL_USCITA,
        "ter_etf":TER_ETF, "bollo":BOLLO, "capital_gain_etf":CG_ETF, "aliquote":ALIQUOTE},
    "fp_netto":FP_NETTO, "fp_lordo":FP_LORDO, "fp_netto_parita_lordo":FP_NETTO_EG,
    "motore_ETF":{n:{k:(v if not isinstance(v,np.ndarray) else None) for k,v in m.items() if k!="cagr"}
                  for n,m in motore.items()},
    "risultati":risultati, "waterfall":wf}
json.dump(summary, open(os.path.join(OUT,"summary.json"),"w"), indent=2, ensure_ascii=False, default=float)

# ================================================================= STDOUT
print("="*84)
print("MOTORE ETF — mediane rolling 10 anni (netto ritenute):")
for n,m in motore.items():
    print(f"  {n:15s} mediana {m['mediana']*100:5.2f}%  netto div {m['r_netto_div']*100:5.2f}%")
print(f"\nFONDO PENSIONE: {FUND_NET*100:.1f}% netto COVIP  ->  netto finale {FP_NETTO:,.0f}€ (lordo {FP_LORDO:,.0f}€)")
print(f"  scenario 'parità di lordo': {FUND_NET_EQUALGROSS*100:.2f}% -> netto {FP_NETTO_EG:,.0f}€")
print(f"  aliquota di pareggio (indice base): {AL_PAREGGIO*100:.1f}%")
print(f"\nRISULTATO — parità di esborso netto, ETF {BASE_INDEX} {R_BASE*100:.2f}%")
for lab in ["23%","33%","43%"]:
    d = risultati[BASE_INDEX]["per_aliquota"][lab]
    print(f"  aliq {lab}: ETF netto {d['etf_netto']:,.0f}€  vs FP {FP_NETTO:,.0f}€  "
          f"=> delta {d['delta']:+,.0f}€ ({d['delta_pct']*100:+.1f}%)  vince {d['vince']}")
print("\n[ok] 5 grafici + summary.json ->", OUT)
