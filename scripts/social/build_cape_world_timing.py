"""
Reel data: due portafogli fittizi sul MSCI World (Gross TR USD).
- 'economico': investito nel World solo nei mesi in cui il CAPE del World e' SOTTO
  la sua mediana storica (rapporto < 1.00); altrimenti liquidita' (flat).
- 'caro': investito solo nei mesi in cui il CAPE e' SOPRA la mediana (>= 1.00).
Mediana espansiva (solo dati passati => niente lookahead). Entrambi partono da 1.
Output: public/charts/cape-internazionale-predice-rendimenti/reel_world_timing.csv
"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..","..")
PROC=os.path.join(ROOT,"data","processed")
OUTdir=os.path.join(ROOT,"public","charts","cape-internazionale-predice-rendimenti")

MKT="Developed Markets Large"
ret=pd.read_csv(os.path.join(PROC,"returns_panel_wide.csv"))[["month",MKT]].dropna()
ret.columns=["month","lvl"]; ret=ret.sort_values("month").reset_index(drop=True)
capeL=pd.read_csv(os.path.join(PROC,"cape_panel_long.csv"))
cape=capeL[capeL.market==MKT].sort_values("date")[["date","cape"]].values.tolist()

def rel_at(month):
    past=[v for d,v in cape if d<=month]
    if len(past)<4: return None
    return past[-1]/np.median(past)

rows=[]; nav_e=1.0; nav_c=1.0; inv_e=0; inv_c=0; n=0
start_i=ret.index[ret.month>="2001-01"][0]
rows.append((ret.month[start_i], nav_e, nav_c))
for i in range(start_i, len(ret)-1):
    m, m1 = ret.month[i], ret.month[i+1]
    r = ret.lvl[i+1]/ret.lvl[i]
    rel = rel_at(m)
    if rel is not None:
        n+=1
        if rel < 1.0: nav_e*=r; inv_e+=1
        else:         nav_c*=r; inv_c+=1
    rows.append((m1, nav_e, nav_c))

df=pd.DataFrame(rows, columns=["date","economico","caro"])
os.makedirs(OUTdir,exist_ok=True)
df.to_csv(os.path.join(OUTdir,"reel_world_timing.csv"), index=False)
print(f"Periodo: {df.date.iloc[0]} -> {df.date.iloc[-1]}  ({n} mesi con segnale)")
print(f"ECONOMICO: 1 -> {nav_e:.2f}x   (investito {inv_e} mesi = {100*inv_e/n:.0f}% del tempo)")
print(f"CARO:      1 -> {nav_c:.2f}x   (investito {inv_c} mesi = {100*inv_c/n:.0f}% del tempo)")
