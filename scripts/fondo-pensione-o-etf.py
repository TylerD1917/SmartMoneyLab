"""
Fondo pensione (contribuzione volontaria deducibile) o ETF azionario globale?
Articolo SEO pilastro #5.

Il TFR e' gia' nel fondo pensione in ENTRAMBI gli scenari: si elide, quindi
modelliamo solo la contribuzione INCREMENTALE su 30 anni.

  Scenario 1 (FP)  : versa il massimo deducibile (5.300 EUR/anno, L. Bilancio 2026)
  Scenario 2 (ETF) : investe in ETF azionario globale l'equivalente ESBORSO NETTO
                     in tasca, cioe' 5.300 * (1 - aliquota marginale)

Confronto a PARITA' DI ESBORSO NETTO. Viene calcolata anche l'impostazione "A"
(esborso lordo, rimborso IRPEF non investito) usata per l'apertura dell'articolo.

Motore di rendimento: mediana dei CAGR da finestre mobili a 10 anni (passo mensile)
su MSCI World / ACWI / MSCI USA (proxy S&P 500), Gross TR USD, dic 2000 - apr 2026.
Stessa finestra per i tre indici -> mediane confrontabili.

Output: public/charts/fondo-pensione-o-etf/*.png + summary.json
"""
import os, json, itertools
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "public", "charts", "fondo-pensione-o-etf"); os.makedirs(OUT, exist_ok=True)

NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

def eur(v, _=None): return f"{v/1000:.0f}k€"          # per valori in euro
def kfmt(v, _=None): return f"{v:.0f}k€"               # per assi gia' espressi in migliaia
def it(x, d=1): return f"{x:.{d}f}".replace(".", ",")

# ------------------------------------------------------------------ 1. MOTORE
INDICI = {"MSCI World":"Developed Markets Large", "FTSE All-World":"ACWI", "S&P 500":"US Large"}
BASE_INDEX = "MSCI World"          # base case dichiarato
WHT   = 0.0040                     # gross -> net: ritenute alla fonte sui dividendi (comune ai 2 veicoli)
WIN   = 120                        # finestra mobile: 10 anni

panel = pd.read_csv(os.path.join(ROOT, "data", "processed", "returns_panel_wide.csv"))

motore = {}
for nome, col in INDICI.items():
    s = panel[["month", col]].dropna().reset_index(drop=True)
    v = s[col].values
    cagr = np.array([(v[i+WIN]/v[i])**(12/WIN) - 1 for i in range(len(v)-WIN)])
    motore[nome] = {
        "col": col, "n_mesi": len(v), "n_finestre": len(cagr),
        "periodo": [s.month.iloc[0], s.month.iloc[-1]],
        "ultima_partenza": s.month.iloc[len(cagr)-1],
        "cagr": cagr,
        "mediana": float(np.median(cagr)), "media": float(cagr.mean()),
        "min": float(cagr.min()), "max": float(cagr.max()),
        "p25": float(np.percentile(cagr,25)), "p75": float(np.percentile(cagr,75)),
        "r_netto_div": float(np.median(cagr) - WHT),   # rendimento comune ai due veicoli
    }

# le tre serie devono coprire la stessa finestra, altrimenti le mediane non sono confrontabili
_per = {tuple(m["periodo"]) for m in motore.values()}
_nf  = {m["n_finestre"] for m in motore.values()}
STESSA_FINESTRA = (len(_per) == 1 and len(_nf) == 1)
assert STESSA_FINESTRA, "ATTENZIONE: indici su periodi diversi, mediane non confrontabili"

# --------------------------------------------------------- 2. PARAMETRI FISCO
N          = 30           # anni di contribuzione
CAP        = 5300.0       # tetto deducibilita' 2026 (L. Bilancio 2026, era 5.164,57)
ISC_FP     = 0.0050       # costo comparto azionario, fondo negoziale (base case)
TAX_ANNUA  = 0.20         # imposta sostitutiva annua sui rendimenti del fondo pensione
AL_USCITA  = 0.105        # 15% - 0,3% per ogni anno oltre il 15esimo -> 30 anni = 10,5%
TER_ETF    = 0.0020       # TER ETF azionario globale UCITS ad accumulazione
BOLLO      = 0.0020       # imposta di bollo annua sul dossier titoli
CG_ETF     = 0.26         # capital gain alla vendita

ALIQUOTE      = {"23%": 0.23, "33%": 0.33, "43%": 0.43}
AL_PRINCIPALI = ["23%", "33%"]     # i due profili mostrati affiancati per tutto l'articolo
COSTI_FP      = {"Fondo negoziale":0.0050, "Fondo aperto":0.0130, "PIP":0.0220}

def accumula(C, g, n=N):
    """Montante con versamento C a fine anno e crescita netta annua g."""
    v = 0.0
    for _ in range(n):
        v = v*(1+g) + C
    return v

def netto_etf(C, g, n=N):
    """ETF: nessuna tassa annua, 26% sulla plusvalenza alla vendita finale."""
    v = accumula(C, g, n)
    return v - CG_ETF*max(v - C*n, 0.0)

def netto_fp(C, g, n=N, al=AL_USCITA):
    """FP: tassa in uscita sulla BASE = contributi dedotti (i rendimenti sono gia' tassati)."""
    v = accumula(C, g, n)
    return v - al*C*n

def g_etf(r):  return r - TER_ETF - BOLLO
def g_fp(r, isc=ISC_FP): return (r - isc)*(1 - TAX_ANNUA)

# ------------------------------------------------- 3. RISULTATI PER INDICE/ALIQUOTA
risultati = {}
for nome, m in motore.items():
    r = m["r_netto_div"]
    fp_lordo = accumula(CAP, g_fp(r)); fp_netto = netto_fp(CAP, g_fp(r))
    blocco = {"r": r, "fp_lordo": fp_lordo, "fp_netto": fp_netto,
              "fp_tassa_uscita": AL_USCITA*CAP*N, "versato_fp": CAP*N, "per_aliquota": {}}
    for lab, t in ALIQUOTE.items():
        c_net    = CAP*(1-t)
        etf_l    = accumula(c_net, g_etf(r)); etf_n = netto_etf(c_net, g_etf(r))
        # impostazione A: esborso lordo 5.300 su entrambi, rimborso IRPEF tenuto liquido
        a_fp     = fp_netto + CAP*t*N
        a_etf    = netto_etf(CAP, g_etf(r))
        # impostazione B: esborso lordo 5.300 netti, rimborso reinvestito in ETF
        b_fp     = fp_netto + netto_etf(CAP*t, g_etf(r))
        blocco["per_aliquota"][lab] = {
            "aliquota": t, "esborso_netto_anno": c_net, "esborso_netto_tot": c_net*N,
            "etf_lordo": etf_l, "etf_netto": etf_n, "etf_tassa_cg": etf_l - etf_n,
            "delta": fp_netto - etf_n, "delta_pct": fp_netto/etf_n - 1,
            "A_fp_piu_cash": a_fp, "A_etf": a_etf, "A_delta": a_fp - a_etf,
            "B_fp_piu_sidecar": b_fp, "B_etf": a_etf, "B_delta": b_fp - a_etf,
        }
    risultati[nome] = blocco

R_BASE = motore[BASE_INDEX]["r_netto_div"]

# ------------------------------------------------- 4. SENSITIVITY COSTO x ALIQUOTA
sens = {}
for cl, isc in COSTI_FP.items():
    fp_n = netto_fp(CAP, g_fp(R_BASE, isc))
    sens[cl] = {"isc": isc, "fp_netto": fp_n, "per_aliquota": {}}
    for lab, t in ALIQUOTE.items():
        etf_n = netto_etf(CAP*(1-t), g_etf(R_BASE))
        sens[cl]["per_aliquota"][lab] = {"etf_netto": etf_n, "delta": fp_n - etf_n,
                                         "vince": "FP" if fp_n > etf_n else "ETF"}

# griglia fine per la heatmap + frontiera di indifferenza
isc_grid = np.linspace(0.001, 0.028, 61)
al_grid  = np.array([0.23, 0.28, 0.33, 0.38, 0.43])
heat = np.array([[netto_fp(CAP, g_fp(R_BASE, i)) - netto_etf(CAP*(1-t), g_etf(R_BASE))
                  for i in isc_grid] for t in al_grid])
# ISC di pareggio per ciascuna aliquota (oltre quel costo vince l'ETF)
isc_pareggio = {}
for t in al_grid:
    target = netto_etf(CAP*(1-t), g_etf(R_BASE))
    lo, hi = 0.0, 0.06
    for _ in range(80):
        mid = (lo+hi)/2
        if netto_fp(CAP, g_fp(R_BASE, mid)) > target: lo = mid
        else: hi = mid
    isc_pareggio[f"{t:.0%}"] = float((lo+hi)/2)

# ---------------------------------------------------- 5. WATERFALL (base index)
def waterfall(t):
    """Scomposizione ETF netto -> FP netto. Ricostruisce esattamente il delta."""
    c_net = CAP*(1-t)
    s0 = netto_etf(c_net, g_etf(R_BASE))                  # ETF netto (baseline)
    s1 = netto_etf(CAP,   g_etf(R_BASE))                  # + leva della deduzione
    s2 = netto_etf(CAP,   R_BASE - ISC_FP)                # - costi prodotto, + niente bollo
    s3 = netto_etf(CAP,   g_fp(R_BASE))                   # - imposta annua 20%
    s4 = netto_fp (CAP,   g_fp(R_BASE))                   # - tassa uscita 10,5% invece di 26%
    return {"ETF netto": s0,
            "Leva della deduzione": s1-s0,
            "Costi prodotto e bollo": s2-s1,
            "Imposta annua 20%": s3-s2,
            "Tassa finale 10,5% vs 26%": s4-s3,
            "FP netto": s4}

wf = {lab: waterfall(ALIQUOTE[lab]) for lab in AL_PRINCIPALI}

# ================================================================= GRAFICI
COL_IDX = {"MSCI World":NAVY, "FTSE All-World":GOLD, "S&P 500":RED}

# --- 01 distribuzione dei CAGR rolling 10 anni -------------------------------
fig, (ax, axb) = plt.subplots(1, 2, figsize=(12.6,5.4), gridspec_kw={"width_ratios":[1.6,1]})
for nome, m in motore.items():
    ax.hist(m["cagr"]*100, bins=26, alpha=0.45, color=COL_IDX[nome], label=nome)
    ax.axvline(m["mediana"]*100, color=COL_IDX[nome], lw=2.2, ls="--")
ax.set_xlabel("CAGR dei 10 anni successivi"); ax.set_ylabel("Numero di finestre")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}%"))
nfin = motore[BASE_INDEX]["n_finestre"]; per = motore[BASE_INDEX]["periodo"]
ax.set_title(f"{nfin} finestre mobili a 10 anni ({per[0]} → {per[1]})\ntratteggio = mediana", fontsize=12, weight="bold")
ax.legend(fontsize=10)
nomi = list(motore)
x = np.arange(len(nomi)); w = 0.38
b1 = axb.bar(x-w/2, [motore[n]["mediana"]*100 for n in nomi], w, color=[COL_IDX[n] for n in nomi], label="Mediana")
b2 = axb.bar(x+w/2, [motore[n]["media"]*100 for n in nomi], w, color=GREY, label="Media")
for bars in (b1,b2):
    for b in bars:
        axb.text(b.get_x()+b.get_width()/2, b.get_height()+0.12, it(b.get_height()), ha="center", fontsize=9.5)
axb.set_xticks(x); axb.set_xticklabels([n.replace(" ","\n") for n in nomi], fontsize=9.5)
axb.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}%"))
axb.set_title("Mediana vs media\n(stessa finestra per i tre indici)", fontsize=11.5, weight="bold")
axb.legend(fontsize=9.5)
fig.suptitle("Il motore di rendimento: cosa hanno reso davvero gli indici globali", fontsize=13.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_rolling_10y.png")); plt.close(fig)

# --- 02 montanti a confronto, i due profili affiancati -----------------------
fig, axes = plt.subplots(1, 2, figsize=(12.8,5.6), sharey=True)
for ax, lab in zip(axes, AL_PRINCIPALI):
    d = risultati[BASE_INDEX]["per_aliquota"][lab]
    fp_l = risultati[BASE_INDEX]["fp_lordo"]; fp_n = risultati[BASE_INDEX]["fp_netto"]
    vals_l = [fp_l, d["etf_lordo"]]; vals_n = [fp_n, d["etf_netto"]]
    xx = np.arange(2)
    ax.bar(xx, [v/1000 for v in vals_l], 0.52, color=GREY, label="Lordo (prima delle tasse finali)")
    ax.bar(xx, [v/1000 for v in vals_n], 0.52, color=[NAVY, GOLD], label="Netto in tasca")
    for i,(l,n) in enumerate(zip(vals_l, vals_n)):
        ax.text(i, n/1000-12, eur(n), ha="center", va="top", color="white", fontsize=11.5, weight="bold")
        ax.text(i, l/1000+6, eur(l), ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(xx); ax.set_xticklabels(["Fondo pensione\n5.300€/anno", "ETF globale\n"+f"{d['esborso_netto_anno']:,.0f}€/anno".replace(",",".")], fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(kfmt))
    ax.set_ylim(0, 560)
    ax.set_title(f"Aliquota marginale {lab}\nesborso netto identico: {d['esborso_netto_tot']/1000:.0f}k€ in 30 anni",
                 fontsize=11.5, weight="bold")
    ax.annotate(f"{'+' if d['delta']>0 else ''}{d['delta']/1000:.0f}k€  ({d['delta_pct']*100:+.0f}%)".replace(".",","),
                xy=(0.5, max(vals_l)/1000*0.42), ha="center", fontsize=13, weight="bold",
                color=GREEN if d["delta"]>0 else RED)
axes[0].set_ylabel("Valore dopo 30 anni")
axes[0].legend(fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 0.99), framealpha=0.95)
fig.suptitle("A parità di esborso netto, dopo 30 anni: fondo pensione contro ETF globale\n"
             f"(motore: {BASE_INDEX}, {it(R_BASE*100,2)}% annuo netto ritenute — fondo negoziale, ISC 0,50%)",
             fontsize=13, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"02_montanti.png")); plt.close(fig)

# --- 03 waterfall: da dove nasce la differenza -------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13.2,5.8), sharey=True)
for ax, lab in zip(axes, AL_PRINCIPALI):
    w_ = wf[lab]; keys = list(w_)
    steps  = keys[1:-1]
    start  = w_["ETF netto"]; end = w_["FP netto"]
    SHORT = {"Leva della deduzione":"Leva della\ndeduzione",
             "Costi prodotto e bollo":"Costi\ne bollo",
             "Imposta annua 20%":"Imposta\nannua 20%",
             "Tassa finale 10,5% vs 26%":"Tassa finale\n10,5% vs 26%"}
    labels = ["ETF\nnetto"] + [SHORT[k] for k in steps] + ["Fondo\npensione"]
    run = start; xs = []; heights=[]; bottoms=[]; colors=[]
    xs.append(0); heights.append(start/1000); bottoms.append(0); colors.append(GOLD)
    for i,k in enumerate(steps, start=1):
        v = w_[k]
        bottoms.append(min(run, run+v)/1000); heights.append(abs(v)/1000)
        colors.append(GREEN if v>0 else RED); xs.append(i); run += v
    xs.append(len(steps)+1); heights.append(end/1000); bottoms.append(0); colors.append(NAVY)
    ax.bar(xs, heights, 0.6, bottom=bottoms, color=colors)
    run = start
    for i,k in enumerate(steps, start=1):
        v = w_[k]; ax.text(i, max(run, run+v)/1000+7, f"{v/1000:+.0f}k".replace(".",","),
                           ha="center", fontsize=10, weight="bold", color=GREEN if v>0 else RED); run += v
    ax.text(0, start/1000+7, eur(start), ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.text(len(steps)+1, end/1000+7, eur(end), ha="center", fontsize=10.5, weight="bold", color=INK)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(kfmt)); ax.set_ylim(0, max(heights)*1.34)
    ax.set_title(f"Aliquota marginale {lab}", fontsize=12, weight="bold")
axes[0].set_ylabel("Valore netto dopo 30 anni")
axes[0].legend(handles=[Patch(color=GREEN,label="A favore del fondo"), Patch(color=RED,label="A sfavore del fondo")],
               fontsize=9.5, loc="upper left")
fig.suptitle("Da dove nasce la differenza: la deduzione paga, l'imposta annua del 20% costa",
             fontsize=13.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"03_waterfall.png")); plt.close(fig)

# --- 04 heatmap costo del fondo x aliquota ----------------------------------
fig, ax = plt.subplots(figsize=(11.4,4.8))
lim = np.abs(heat).max()/1000
im = ax.imshow(heat/1000, aspect="auto", cmap="RdYlGn", vmin=-lim, vmax=lim, origin="lower",
               extent=[isc_grid[0]*100, isc_grid[-1]*100, -0.5, len(al_grid)-0.5])
cs = ax.contour(isc_grid*100, np.arange(len(al_grid)), heat/1000, levels=[0], colors=INK, linewidths=2.4)
ax.clabel(cs, fmt={0:" pareggio "}, fontsize=10)
ax.set_yticks(np.arange(len(al_grid))); ax.set_yticklabels([f"{t:.0%}" for t in al_grid])
ax.set_ylabel("Aliquota marginale IRPEF"); ax.set_xlabel("Costo annuo del fondo pensione (ISC)")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_: it(v,1)+"%"))
ax.grid(False)
for cl, isc in COSTI_FP.items():
    ax.axvline(isc*100, color=INK, lw=1.1, ls=":")
    ax.text(isc*100, len(al_grid)-0.42, " "+cl, rotation=90, va="top", fontsize=9, color=INK)
cb = fig.colorbar(im, ax=ax); cb.set_label("Vantaggio del fondo\nsull'ETF (k€ netti)", fontsize=10)
ax.set_title("Il verdetto si ribalta: con un prodotto caro e un'aliquota bassa vince l'ETF\n"
             f"(motore: {BASE_INDEX}; verde = vince il fondo, rosso = vince l'ETF)", fontsize=12.5, weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"04_heatmap_costo_aliquota.png")); plt.close(fig)

# --- 05 robustezza: stesso esercizio con i tre indici ------------------------
fig, ax = plt.subplots(figsize=(10.6,5.2))
xx = np.arange(len(AL_PRINCIPALI)+1); labs = AL_PRINCIPALI+["43%"]; w = 0.26
for j, nome in enumerate(nomi):
    vals = [risultati[nome]["per_aliquota"][l]["delta"]/1000 for l in labs]
    b = ax.bar(xx + (j-1)*w, vals, w, color=COL_IDX[nome], label=f"{nome} ({it(motore[nome]['mediana']*100,2)}%)")
    for r_ in b:
        ax.text(r_.get_x()+r_.get_width()/2, r_.get_height()+2.5, f"{r_.get_height():.0f}", ha="center", fontsize=9)
ax.set_xticks(xx); ax.set_xticklabels([f"Aliquota {l}" for l in labs])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0f}k€"))
ax.set_ylabel("Vantaggio netto del fondo pensione")
ax.axhline(0, color=INK, lw=1)
ax.set_title("Robustezza: cambiare indice non cambia il verdetto, cambiare aliquota sì\n"
             "(fondo negoziale, ISC 0,50%; in parentesi la mediana rolling 10 anni)", fontsize=12.5, weight="bold")
ax.legend(fontsize=10, title="Motore di rendimento", title_fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"05_robustezza_indici.png")); plt.close(fig)

# ================================================================= SUMMARY
summary = {
    "metodo": {
        "finestra_anni": 10, "passo": "mensile", "stessa_finestra_per_tutti_gli_indici": bool(STESSA_FINESTRA),
        "ritenuta_dividendi_gross_to_net": WHT, "indice_base_case": BASE_INDEX,
        "impostazione_confronto": "parita' di esborso netto in tasca",
        "nota_TFR": "il TFR e' gia' nel fondo in entrambi gli scenari: si elide, modellata solo la contribuzione incrementale",
        "nota_scaglioni": "si assume RAL tale che l'intero versamento di 5.300 EUR sia dedotto all'aliquota marginale indicata",
    },
    "motore": {n: {k: (v if not isinstance(v, np.ndarray) else None) for k,v in m.items() if k != "cagr"}
               for n, m in motore.items()},
    "parametri": {"anni":N, "tetto_deducibile":CAP, "isc_fondo_negoziale":ISC_FP,
                  "imposta_annua_fondo":TAX_ANNUA, "aliquota_uscita_30anni":AL_USCITA,
                  "ter_etf":TER_ETF, "bollo":BOLLO, "capital_gain_etf":CG_ETF,
                  "costi_fondo_varianti":COSTI_FP, "aliquote":ALIQUOTE},
    "risultati": risultati,
    "sensitivity_costo_fondo": sens,
    "isc_di_pareggio": isc_pareggio,
    "waterfall": wf,
}
json.dump(summary, open(os.path.join(OUT,"summary.json"),"w"), indent=2, ensure_ascii=False, default=float)

# ================================================================= STDOUT
print("="*82)
print("MOTORE — finestre mobili 10 anni (Gross TR USD, S&P 500 = proxy MSCI USA)")
for n, m in motore.items():
    print(f"  {n:15s} {m['periodo'][0]}→{m['periodo'][1]}  {m['n_finestre']} finestre  "
          f"mediana {m['mediana']*100:5.2f}%  media {m['media']*100:5.2f}%  "
          f"[{m['min']*100:.2f}% … {m['max']*100:.2f}%]  → netto ritenute {m['r_netto_div']*100:.2f}%")
print(f"  stessa finestra per i tre indici: {STESSA_FINESTRA}")

print("\n" + "="*82)
print(f"RISULTATO PRINCIPALE — parità di esborso netto, motore {BASE_INDEX}, ISC 0,50%")
b = risultati[BASE_INDEX]
print(f"  FP: versa 5.300€/anno → lordo {b['fp_lordo']:,.0f}€ − tassa uscita {b['fp_tassa_uscita']:,.0f}€ "
      f"= NETTO {b['fp_netto']:,.0f}€")
for lab in ["23%","33%","43%"]:
    d = b["per_aliquota"][lab]
    print(f"  aliq {lab}: esborso netto {d['esborso_netto_anno']:,.0f}€/anno ({d['esborso_netto_tot']/1000:.0f}k tot) → "
          f"ETF lordo {d['etf_lordo']:,.0f}€ − CG {d['etf_tassa_cg']:,.0f}€ = NETTO {d['etf_netto']:,.0f}€"
          f"   ⇒ delta {d['delta']:+,.0f}€ ({d['delta_pct']*100:+.1f}%)")

print("\n" + "="*82)
print("APERTURA POLEMICA — impostazione A (esborso lordo, rimborso IRPEF NON investito)")
for lab in AL_PRINCIPALI:
    d = b["per_aliquota"][lab]
    print(f"  aliq {lab}: FP {b['fp_netto']:,.0f}€ + cash {CAP*ALIQUOTE[lab]*N:,.0f}€ = {d['A_fp_piu_cash']:,.0f}€"
          f"   vs ETF 5.300€/anno = {d['A_etf']:,.0f}€   ⇒ {d['A_delta']:+,.0f}€")
print("IMPOSTAZIONE B (rimborso reinvestito) — verifica: stesso delta di C")
for lab in AL_PRINCIPALI:
    d = b["per_aliquota"][lab]
    print(f"  aliq {lab}: B delta {d['B_delta']:+,.0f}€   vs   C delta {d['delta']:+,.0f}€   "
          f"(differenza {abs(d['B_delta']-d['delta']):.4f}€)")

print("\n" + "="*82)
print("SENSITIVITY COSTO DEL FONDO × ALIQUOTA (motore base)")
print(f"  {'':18s} {'ISC':>6s}  " + "  ".join(f"{l:>18s}" for l in ALIQUOTE))
for cl, s in sens.items():
    row = f"  {cl:18s} {s['isc']*100:5.2f}%  "
    for lab in ALIQUOTE:
        p = s["per_aliquota"][lab]
        row += f"{p['delta']:+10,.0f}€ [{p['vince']:3s}]  "
    print(row)
print("  ISC di pareggio (oltre → vince l'ETF): " +
      "  ".join(f"{k}→{v*100:.2f}%" for k,v in isc_pareggio.items()))

print("\n" + "="*82)
print("WATERFALL (riconciliazione)")
for lab in AL_PRINCIPALI:
    w_ = wf[lab]
    print(f"  aliquota {lab}:")
    for k, v in w_.items():
        print(f"     {k:32s} {v:+12,.0f}€")
    chk = w_["ETF netto"] + sum(w_[k] for k in list(w_)[1:-1]) - w_["FP netto"]
    print(f"     {'→ residuo di riconciliazione':32s} {chk:+12,.4f}€")

print("\n[ok] 5 grafici + summary.json →", OUT)
