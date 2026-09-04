"""
Meglio un mutuo a TASSO FISSO o a TASSO VARIABILE? (mutuo casa 30 anni, Italia)
Articolo Tipo B — studio serio su domanda comune (gemello di fondo-pensione-o-etf).

Impianto concordato con Tyler (2026-09-04) — DOPPIO BINARIO:
  PARTE 1  Replay storico REALE (dati MIR contrattati 2003-2026): "chi ha acceso
           il mutuo nell'anno X ha fatto meglio fisso o variabile, FINORA?".
           Orizzonti realizzati/troncati (nessun mutuo euro ha ancora chiuso i 30y).
  PARTE 2  Monte Carlo su 30 anni COMPLETI via block-bootstrap dei tassi (era euro).
           Risponde: esiste sempre una scelta migliore? Da cosa dipende?
  CHIAVE   P(fisso costa meno) in funzione dello SPREAD INIZIALE (rata fissa - rata
           variabile all'accensione) = pendenza della curva = premio del fisso.

Metrica principale (decisa): INTERESSI TOTALI pagati (chi costa meno) + RATA MASSIMA
raggiunta dal variabile ("costo per dormire la notte"). Il fisso puo' perdere sul
costo ma vincere sul rischio-shock.

Meccanica: il variabile e' guidato dalla BCE (Euribor 3M ~ deposit rate); il fisso
dal mercato swap (Eurirs = attese BCE + premio a termine). La scelta e' una scommessa
CONTRO la curva forward.

NB MOTORE MONTE CARLO: block-bootstrap delle VARIAZIONI mensili di Euribor (blocchi
lunghi per preservare i cicli) con floor. E' il "nodo modellistico" ancora aperto:
coerente con la casa (bootstrap a blocchi), ma valutare reversione morbida se i
percorsi driftano troppo. Parametri in testa, facilmente sostituibili.

Baseline: LORDO, nominale (la rata e' nominale). Ammortamento francese.

Dati richiesti in data/mutuo-fisso-o-variabile/ (percentuali, es. 3.85):
  euribor3m.csv : date,euribor3m                 (mensile, dal 1999)
  eurirs.csv    : date,irs20,irs25,irs30         (mensile, dal ~1999; NaN ammessi)
  mir_mutui.csv : date,fisso,variabile           (MIR nuovi mutui casa: fisso=oltre
                                                   10y fixation, variabile=fino 1y;
                                                   mensile, dal 2003)
  bce_rates.csv : date,mro,deposit               (opzionale, solo narrativa/reel)
  date = YYYY-MM-DD o YYYY-MM (fine mese). Decimali con . o , (gestiti entrambi).

Uso:
  python scripts/mutuo-fisso-o-variabile.py --check     # solo copertura dati
  python scripts/mutuo-fisso-o-variabile.py             # simulazione completa

Output: public/charts/mutuo-fisso-o-variabile/*.png + summary.json
"""
import os, json, argparse
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
from matplotlib.patches import Patch

# ------------------------------------------------------------------ paths & stile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "mutuo-fisso-o-variabile")
OUT  = os.path.join(ROOT, "public", "charts", "mutuo-fisso-o-variabile"); os.makedirs(OUT, exist_ok=True)

NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; RED="#e11d48"; INK="#0f172a"; GREEN="#059669"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

def it(x, d=1): return f"{x:.{d}f}".replace(".", ",")
def eurk(v, _=None): return f"{v/1000:.0f}k€"
def eur0(v, _=None): return f"{v:,.0f}€".replace(",", ".")
def pct(v, _=None): return f"{v:.1f}%".replace(".", ",")

# ------------------------------------------------------------------ parametri mutuo & sim
L        = 200_000.0    # capitale (il rapporto interessi e' scale-invariant; la rata scala)
N_YEARS  = 30
N        = N_YEARS*12
RESET_M  = 3            # il variabile si ripara ogni 3 mesi (Euribor 3M)
IRS_COL  = "irs25"      # sottostante del fisso per la ricostruzione (fallback irs20/irs30)

# Monte Carlo
N_SIM    = 10_000
BLOCK    = 48           # blocchi di 48 mesi (4y) per il bootstrap: preserva i mini-cicli
FLOOR    = -0.005       # Euribor non scende sotto -0,5% (minimo storico era euro)
CAP_LVL  = 0.12         # sanity cap 12%
SEED     = 20260904
rng = np.random.default_rng(SEED)

# Surroga (rifinanziamento del fisso con un nuovo fisso se i tassi scendono).
# In Italia e' gratuita dal 2007 (L. Bersani). Modello semplice e dichiarato:
# ogni SURROGA_EVERY mesi, se il fisso di mercato oggi (~Euribor + premio medio storico
# del fisso sul breve) e' almeno SURROGA_THR sotto il tasso attualmente bloccato, ci si
# rifinanzia a quel tasso (rata ricalcolata su debito e termine residui). Opzione a senso
# unico: se i tassi salgono, si tiene il proprio fisso.
SURROGA_THR   = 0.0075  # conviene surrogare solo se si guadagna >= 0,75pp (attrito pratico)
SURROGA_EVERY = 12      # si valuta una volta l'anno (la surroga richiede tempo)

# ---------------------------------------- ingestione (export BCE grezzi o schema semplice)
# Riconosce sia i CSV scaricati dal portale BCE (colonne DATE, TIME PERIOD, <titolo (KEY)>)
# sia i file "canonici" (date, euribor3m, ...). Classifica ogni serie dalla KEY nell'header.
KEYMAP = [   # (sottostringa nell'header della colonna valore, nome canonico)
    ("A2C.F.R",  "variabile"),   # MIR IT: tasso variabile e fino a 1 anno
    ("A2C.P.R",  "fisso"),       # MIR IT: oltre 10 anni
    ("EURIBOR3M","euribor3m"),
    ("KR.DFR",   "deposit"),
    ("KR.MRR_FR","mro"),
    ("L40.CI",   "long_rate"),   # tasso a lungo termine per convergenza (~10y)
]
SIMPLE = {"euribor3m","fisso","variabile","deposit","mro","long_rate"}
FFILL  = {"deposit","mro","euribor3m","long_rate"}   # serie a passo > mensile: riempi in avanti

def _to_month_frac(dates, vals):
    d = pd.to_datetime(dates, errors="coerce")
    v = pd.to_numeric(pd.Series(vals).astype(str).str.replace("%","",regex=False)
                      .str.replace(",",".",regex=False), errors="coerce")
    s = pd.Series(v.values, index=d).dropna().sort_index()
    s.index = s.index.values.astype("datetime64[M]")   # aggancia a inizio mese
    return s.groupby(level=0).last()/100.0

def ingest():
    found, srcfreq = {}, {}
    for fn in sorted(os.listdir(DATA)):
        if not fn.lower().endswith(".csv"): continue
        try: raw = pd.read_csv(os.path.join(DATA, fn), dtype=str)
        except Exception: continue
        cols = list(raw.columns); low = [c.strip().lower() for c in cols]
        if "date" not in low: continue
        date_col = cols[low.index("date")]
        for vc in [c for c in cols if c.strip().lower() not in ("date","time period")]:
            name, h = None, vc.strip().lower()
            if h in SIMPLE: name = h
            else:
                for sub, nm in KEYMAP:
                    if sub.lower() in vc.lower(): name = nm; break
            if name is None or name in found: continue
            s = _to_month_frac(raw[date_col], raw[vc])
            if len(s) < 2: continue
            found[name] = s
            gap = np.median(np.diff(s.index.values).astype("timedelta64[D]").astype(int))
            srcfreq[name] = "mensile" if gap <= 40 else ("trimestrale" if gap <= 100 else "irregolare")
    if not found: raise SystemExit(f"Nessuna serie riconosciuta in {DATA}")
    lo = min(s.index.min() for s in found.values()); hi = max(s.index.max() for s in found.values())
    idx = pd.period_range(lo, hi, freq="M").to_timestamp()
    df = pd.DataFrame(index=idx)
    for nm, s in found.items():
        df[nm] = s.reindex(idx).ffill() if nm in FFILL else s.reindex(idx)
    df.attrs["srcfreq"] = srcfreq
    return df

def check(df):
    def span(c):
        if c not in df.columns: return "MANCANTE"
        s = df[c].dropna()
        f = df.attrs.get("srcfreq",{}).get(c,"?")
        return f"{s.index.min():%Y-%m}..{s.index.max():%Y-%m} (n={len(s)}, {f})" if len(s) else "VUOTO"
    print("== COPERTURA DATI ==")
    for c in ["euribor3m","fisso","variabile","long_rate","deposit","mro"]:
        print(f"  {c:<10}:", span(c))
    miss = [c for c in ("euribor3m","fisso","variabile") if c not in df.columns or df[c].dropna().empty]
    if miss:
        print("\n>>> MANCANO serie ESSENZIALI:", ", ".join(miss))
        if "variabile" in miss:
            print("    scarica la serie VARIABILE: MIR.M.IT.B.A2C.F.R.A.2250.EUR.N")
    if df.attrs.get("srcfreq",{}).get("euribor3m")=="trimestrale":
        print("\n>>> ATTENZIONE: Euribor e' TRIMESTRALE (riempito in avanti a mese).")
        print("    Per un Monte Carlo pulito serve MENSILE: FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA (senza modifica 'Quarterly').")
    if {"fisso","variabile"} <= set(df.columns):
        g = (df["fisso"]-df["variabile"]).dropna()
        if len(g):
            print(f"\nspread MIR fisso-variabile: media {it(g.mean()*100,2)}pp, "
                  f"min {it(g.min()*100,2)}pp, max {it(g.max()*100,2)}pp, n={len(g)}")
            print("mesi con fisso<=variabile (curva piatta/invertita):",
                  int((g<=0).sum()), f"({it((g<=0).mean()*100,0)}%)")

# ------------------------------------------------------------------ ammortamento francese
def annuity(balance, r_m, k):
    """rata mensile per estinguere 'balance' in k mesi al tasso mensile r_m."""
    if k <= 0: return balance
    if abs(r_m) < 1e-12: return balance/k
    return balance * r_m / (1 - (1+r_m)**(-k))

def amortize(rate_path_annual, reset_m=1, term=None):
    """
    rate_path_annual: tasso ANNUO per ogni mese OSSERVATO.
    term: durata totale del mutuo in mesi (default = mesi osservati). La rata a
    ogni reset e' calcolata sul debito residuo e sul termine RESIDUO (term - t),
    cosi' un orizzonte troncato (osservati < term) rappresenta i primi mesi del
    piano trentennale, non un mutuo da estinguere nell'orizzonte breve.
    Ritorna (interessi_osservati, serie_rata, serie_interesse_mensile, mesi).
    """
    n = len(rate_path_annual); term = term or n
    bal = L; pay = None; tot_int = 0.0
    pays = np.zeros(n); ints = np.zeros(n)
    for t in range(n):
        r_m = rate_path_annual[t]/12.0
        if t % reset_m == 0 or pay is None:
            pay = annuity(bal, r_m, term - t)
        interest = bal * r_m
        principal = pay - interest
        if t == term-1 or principal > bal:  # ultima rata del piano
            principal = bal; pay = interest + principal
        bal -= principal
        tot_int += interest; pays[t]=pay; ints[t]=interest
        if bal <= 1e-6:
            pays=pays[:t+1]; ints=ints[:t+1]; break
    return tot_int, pays, ints, len(pays)

# ================================================================== PARTE 1 — REPLAY REALE
def part1_historical(df):
    """Per ogni mese di accensione con MIR disponibile: fisso costante = mir_fisso;
    variabile = euribor3m + spread_v (spread_v costante dall'origine, reset 3m).
    Orizzonte = min(mesi disponibili fino a fine serie, 360). Realizzato/troncato."""
    e = df["euribor3m"]; f = df["fisso"]; v = df["variabile"]
    rows = []; curves = {}
    emblem = {2005, 2008, 2011, 2015, 2021}   # coorti emblematiche per i grafici
    months = df.index[(~f.isna()) & (~v.isna()) & (~e.isna())]
    for t0 in months:
        spread_v = v.loc[t0] - e.loc[t0]
        fixed_rate = f.loc[t0]
        fut = e.loc[t0:].iloc[:N]          # euribor futuro dall'origine
        h = len(fut)
        if h < 12: continue                # servono almeno 12 mesi realizzati
        var_path = fut.values + spread_v
        fix_path = np.full(h, fixed_rate)
        int_f,_,_,_ = amortize(fix_path, reset_m=N, term=N)      # fisso: nessun reset, termine 30y
        int_v,pv,_,_ = amortize(var_path, reset_m=RESET_M, term=N)  # variabile su piano 30y, osservo h mesi
        peak_v = float(np.max(pv)); pay_f = annuity(L, fixed_rate/12.0, N)
        rows.append({"orig":t0, "anno":t0.year, "mesi":h,
            "fixed_rate":fixed_rate, "start_var":v.loc[t0], "spread0":fixed_rate-v.loc[t0],
            "int_f":int_f, "int_v":int_v, "cheaper":"fisso" if int_f<int_v else "variabile",
            "peak_var":peak_v, "pay_f":pay_f, "peak_over_f":peak_v/pay_f-1})
        if t0.year in emblem and t0.month == 1:
            curves[t0.year] = {"pay_var":pv.tolist(), "pay_f":float(pay_f),
                               "fixed_rate":fixed_rate, "start_var":float(v.loc[t0])}
    df = pd.DataFrame(rows)
    return df, curves

# ================================================================== PARTE 2 — MONTE CARLO
def build_bootstrap_pool(df):
    """variazioni mensili storiche di Euribor 3M (era euro) come mattoni del bootstrap."""
    e = df["euribor3m"].dropna()
    d = e.diff().dropna().values
    return d, e

def sim_euribor_path(d_pool, start_level):
    """block-bootstrap delle variazioni in blocchi contigui, con floor e cap."""
    path = np.empty(N); lvl = start_level; k = 0
    L_pool = len(d_pool)
    while k < N:
        i = rng.integers(0, L_pool - BLOCK)
        blk = d_pool[i:i+BLOCK]
        for dv in blk:
            if k >= N: break
            lvl = min(max(lvl + dv, FLOOR), CAP_LVL)
            path[k] = lvl; k += 1
    return path

def amortize_surroga(eur_path, start_fixed, mean_gap, term=N):
    """Fisso con surroga: rifinanzia a un nuovo fisso quando conviene (>= SURROGA_THR).
    fisso_di_mercato(t) ~ Euribor(t) + mean_gap (premio medio storico del fisso sul breve).
    Ritorna (interessi_totali, rata_massima, n_surroghe)."""
    bal = L; cur = start_fixed; pay = annuity(bal, cur/12.0, term)
    tot = 0.0; peak = 0.0; n_sur = 0
    for t in range(term):
        if t > 0 and t % SURROGA_EVERY == 0:
            offered = eur_path[t] + mean_gap
            if offered <= cur - SURROGA_THR:
                cur = offered; pay = annuity(bal, cur/12.0, term - t); n_sur += 1
        r = cur/12.0; interest = bal*r; principal = pay - interest
        if t == term-1 or principal > bal: principal = bal; pay = interest + principal
        bal -= principal; tot += interest; peak = max(peak, pay)
        if bal <= 1e-6: break
    return tot, peak, n_sur

def part2_montecarlo(df):
    d_pool, e = build_bootstrap_pool(df)
    lvl_hist = e.values                                   # livelli Euribor storici
    sv = (df["variabile"] - df["euribor3m"]).dropna().values   # spread commerciale del variabile
    gap = (df["fisso"] - df["variabile"]).dropna().values      # gap (premio) del fisso all'origine
    mean_gap = float((df["fisso"] - df["euribor3m"]).dropna().mean())  # premio medio fisso su Euribor
    res = {"fisso_wins":0, "surroga_wins":0, "gap_cost":[], "gap_cost_sur":[],
           "spread0":[], "level0":[], "peak_over_f":[], "win":[], "win_sur":[], "n_surroghe":[]}
    for _ in range(N_SIM):
        start_level = float(rng.choice(lvl_hist))
        spread_v    = float(rng.choice(sv))
        gap_fisso   = float(rng.choice(gap))
        start_var   = start_level + spread_v
        fixed_rate  = start_var + gap_fisso
        eur_path    = sim_euribor_path(d_pool, start_level)
        var_path    = eur_path + spread_v
        int_f,_,_,_ = amortize(np.full(N, fixed_rate), reset_m=N, term=N)
        int_v,pv,_,_= amortize(var_path, reset_m=RESET_M, term=N)
        int_fs, _, n_sur = amortize_surroga(eur_path, fixed_rate, mean_gap, term=N)
        pay_f = annuity(L, fixed_rate/12.0, N); peak_v = float(np.max(pv))
        res["fisso_wins"]   += int(int_f  < int_v)
        res["surroga_wins"] += int(int_fs < int_v)
        res["gap_cost"].append(int_v - int_f)
        res["gap_cost_sur"].append(int_v - int_fs)
        res["spread0"].append(gap_fisso); res["level0"].append(start_level)
        res["peak_over_f"].append(peak_v/pay_f - 1)
        res["win"].append(int(int_f < int_v)); res["win_sur"].append(int(int_fs < int_v))
        res["n_surroghe"].append(n_sur)
    for kk in ("gap_cost","gap_cost_sur","spread0","level0","peak_over_f","win","win_sur","n_surroghe"):
        res[kk] = np.array(res[kk])
    res["p_fisso"]   = res["fisso_wins"]/N_SIM
    res["p_surroga"] = res["surroga_wins"]/N_SIM
    res["mean_gap"]  = mean_gap
    return res

# ================================================================== GRAFICI
def chart_context(df):
    fig, ax = plt.subplots(figsize=(10,5.2))
    ax.plot(df.index, df["euribor3m"]*100, color=NAVY, lw=2, label="Euribor 3M (base variabile)")
    if "long_rate" in df.columns and df["long_rate"].notna().any():
        ax.plot(df.index, df["long_rate"]*100, color=GOLD, lw=2, label="Tasso a lungo termine 10Y (mercato)")
    if "fisso" in df.columns:
        ax.plot(df.index, df["fisso"]*100, color=RED, lw=1.6, ls="--", label="Tasso fisso contrattato (MIR)")
    if "variabile" in df.columns:
        ax.plot(df.index, df["variabile"]*100, color=GREEN, lw=1.6, ls="--", label="Tasso variabile contrattato (MIR)")
    ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(frameon=False, fontsize=10)
    ax.set_title("I due sottostanti: BCE/Euribor (variabile) vs mercato a lungo termine (fisso)")
    fig.savefig(os.path.join(OUT,"context_rates.png")); plt.close(fig)

def chart_cohorts(curves):
    if not curves: return
    fig, ax = plt.subplots(figsize=(10,5.2))
    cols = {2005:GREY,2008:GREEN,2011:INK,2015:NAVY,2021:RED}
    for yr, c in sorted(curves.items()):
        pv = np.array(c["pay_var"]); x = np.arange(len(pv))/12
        ax.plot(x, pv, color=cols.get(yr,NAVY), lw=2, label=f"Variabile acceso {yr}")
        ax.hlines(c["pay_f"], 0, x[-1], color=cols.get(yr,NAVY), lw=1, ls=":", alpha=.7)
    ax.set_xlabel("Anni dall'accensione"); ax.yaxis.set_major_formatter(FuncFormatter(eur0))
    ax.set_title("Rata del variabile per coorte (linea tratteggiata = rata fissa equivalente)")
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(os.path.join(OUT,"cohorts_payment.png")); plt.close(fig)

def chart_mc_cost(res):
    g = res["gap_cost"]/1000  # migliaia di euro, var - fisso (>0 => fisso ha risparmiato)
    fig, ax = plt.subplots(figsize=(10,5.2))
    ax.hist(g, bins=60, color=NAVY, alpha=.85)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("Interessi variabile − fisso su 30 anni (migliaia €)  ·  >0 = il fisso costa meno")
    ax.set_title(f"Chi costa meno su 30 anni? Fisso piu' economico nel {it(res['p_fisso']*100,0)}% degli scenari")
    fig.savefig(os.path.join(OUT,"mc_cost_distribution.png")); plt.close(fig)

def _bin_winrate(s, win, bins_pp):
    idx = np.digitize(s, bins_pp); xs=[]; ys=[]
    for b in range(1,len(bins_pp)):
        m = idx==b
        if m.sum()>=30:
            xs.append((bins_pp[b-1]+bins_pp[b])/2); ys.append(win[m].mean()*100)
    return xs, ys

def chart_pfisso_vs_spread(res, premio_oggi=None):
    s = res["spread0"]*100
    bins_pp = np.array([-1.0,-0.25,0,0.25,0.5,0.75,1.0,1.5,2.0,3.0])
    xs, y_plain = _bin_winrate(s, res["win"], bins_pp)
    _,  y_sur   = _bin_winrate(s, res["win_sur"], bins_pp)
    fig, ax = plt.subplots(figsize=(10,5.4))
    ax.plot(xs, y_sur,   "-o", color=GREEN, lw=2.5, mfc=GREEN, mec=GREEN, ms=6, label="Fisso con surroga")
    ax.plot(xs, y_plain, "-o", color=GOLD,  lw=2.5, mfc=NAVY,  mec=NAVY,  ms=7, label="Fisso senza surroga")
    ax.axhline(50, color=GREY, lw=1, ls="--")
    if premio_oggi is not None:
        ax.axvline(premio_oggi*100, color=RED, lw=1.6, ls="--")
        ax.text(premio_oggi*100, 4, f" oggi ({it(premio_oggi*100,2)}pp)", color=RED, fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(pct)); ax.legend(frameon=False, fontsize=10)
    ax.set_ylim(0,100); ax.set_xlabel("Premio iniziale del fisso = rata fissa − variabile all'accensione (punti %)")
    ax.set_ylabel("Scenari in cui il fisso costa meno del variabile")
    ax.set_title("Il fattore che decide: piu' e' caro il fisso all'inizio, meno conviene")
    fig.savefig(os.path.join(OUT,"mc_pfisso_vs_spread.png")); plt.close(fig)

def chart_peak(res):
    p = res["peak_over_f"]*100
    fig, ax = plt.subplots(figsize=(10,5.2))
    ax.hist(p, bins=60, color=RED, alpha=.8)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("Rata massima del variabile vs rata fissa (%)  ·  0 = mai sopra il fisso")
    ax.set_title("Il 'costo per dormire la notte': quanto puo' salire la rata variabile")
    fig.savefig(os.path.join(OUT,"mc_peak_payment.png")); plt.close(fig)

# ================================================================== MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="solo copertura dati")
    args = ap.parse_args()
    df = ingest()
    if args.check:
        check(df); return
    for c in ("euribor3m","fisso","variabile"):
        if c not in df.columns or df[c].dropna().empty:
            raise SystemExit(f"Manca la serie essenziale '{c}'. Lancia --check per il dettaglio.")

    df1, curves = part1_historical(df)
    res = part2_montecarlo(df)

    # --- DOVE SIAMO OGGI: ultimo mese con fisso e variabile ---
    both = df[["fisso","variabile"]].dropna()
    t_oggi = both.index[-1]
    fisso_oggi, var_oggi = float(both["fisso"].iloc[-1]), float(both["variabile"].iloc[-1])
    premio_oggi = fisso_oggi - var_oggi
    # P modellata al premio odierno (interpolazione delle curve binnate)
    bins_pp = np.array([-1.0,-0.25,0,0.25,0.5,0.75,1.0,1.5,2.0,3.0]); s = res["spread0"]*100
    xs, yp = _bin_winrate(s, res["win"], bins_pp); _, ysu = _bin_winrate(s, res["win_sur"], bins_pp)
    p_fisso_oggi   = float(np.interp(premio_oggi*100, xs, yp)/100)
    p_surroga_oggi = float(np.interp(premio_oggi*100, xs, ysu)/100)

    chart_context(df)
    chart_cohorts(curves)
    chart_mc_cost(res)
    chart_pfisso_vs_spread(res, premio_oggi=premio_oggi)
    chart_peak(res)

    # riepilogo per coorte (replay reale)
    coh = (df1.groupby("anno")
              .agg(n=("mesi","size"), mesi=("mesi","max"),
                   fixed_rate=("fixed_rate","mean"), start_var=("start_var","mean"),
                   int_f=("int_f","mean"), int_v=("int_v","mean"),
                   quota_fisso_cheaper=("cheaper", lambda s:(s=="fisso").mean()),
                   peak_over_f=("peak_over_f","mean")).reset_index())
    coh.to_csv(os.path.join(OUT,"coorti_reali.csv"), index=False)

    summary = {
        "params": {"L":L, "anni":N_YEARS, "reset_m":RESET_M, "n_sim":N_SIM,
                   "block":BLOCK, "floor":FLOOR},
        "srcfreq": df.attrs.get("srcfreq",{}),
        "copertura": {
            "euribor": [str(df["euribor3m"].dropna().index.min().date()),
                        str(df["euribor3m"].dropna().index.max().date())],
            "mir":     [str(df["fisso"].dropna().index.min().date()),
                        str(df["fisso"].dropna().index.max().date())]},
        "parte1_replay": {
            "n_coorti_mesi": int(df1["mesi"].count()),
            "quota_accensioni_fisso_piu_economico_finora": float((df1["cheaper"]=="fisso").mean()),
            "coorti": coh.round(4).to_dict(orient="records")},
        "parte2_montecarlo": {
            "p_fisso_costa_meno": res["p_fisso"],
            "mediana_gap_var_meno_fisso_eur": float(np.median(res["gap_cost"])),
            "p_rata_var_supera_fisso": float((res["peak_over_f"]>0).mean()),
            "p_rata_var_oltre_30pct_sopra_fisso": float((res["peak_over_f"]>0.30).mean()),
            "spread0_pp": {"media": float(res["spread0"].mean()*100),
                            "min": float(res["spread0"].min()*100),
                            "max": float(res["spread0"].max()*100)}},
        "surroga": {
            "regola": {"soglia_pp": SURROGA_THR*100, "valuta_ogni_mesi": SURROGA_EVERY,
                       "fisso_mercato": "Euribor + premio medio storico",
                       "premio_medio_pp": round(res["mean_gap"]*100,2)},
            "p_fisso_surroga_costa_meno": res["p_surroga"],
            "mediana_gap_var_meno_surroga_eur": float(np.median(res["gap_cost_sur"])),
            "surroghe_medie_per_mutuo": float(res["n_surroghe"].mean())},
        "oggi": {
            "mese": str(t_oggi.date()), "fisso_pct": round(fisso_oggi*100,2),
            "variabile_pct": round(var_oggi*100,2), "premio_pp": round(premio_oggi*100,2),
            "p_fisso_costa_meno_a_questo_premio": round(p_fisso_oggi,3),
            "p_fisso_surroga_costa_meno_a_questo_premio": round(p_surroga_oggi,3)}}
    with open(os.path.join(OUT,"summary.json"),"w",encoding="utf-8") as fp:
        json.dump(summary, fp, ensure_ascii=False, indent=2)
    print("OK. Grafici + summary.json in", OUT)
    print(f"P(fisso costa meno) = {it(res['p_fisso']*100,1)}%  |  con surroga = {it(res['p_surroga']*100,1)}%")
    print(f"OGGI ({t_oggi.date()}): fisso {it(fisso_oggi*100,2)}% - variabile {it(var_oggi*100,2)}% "
          f"= premio {it(premio_oggi*100,2)}pp -> storicamente fisso vince {it(p_fisso_oggi*100,0)}% "
          f"(con surroga {it(p_surroga_oggi*100,0)}%)")

if __name__ == "__main__":
    main()
