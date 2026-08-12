"""
Reel data (FORWARD, percorsi STORICI REALI del MSCI World Gross TR):
- 'economico': 1 investito nel World a gennaio 2009 (CAPE 0.55x la sua mediana => molto
   economico), crescita reale nei 10 anni successivi.
- 'caro': 1 investito nel World a gennaio 2001 (CAPE 1.51x la mediana => molto caro),
   crescita reale nei 10 anni successivi.
Percorsi veri (con le loro oscillazioni), allineati per "anni trascorsi" (--elapsed).
Output: public/charts/cape-internazionale-predice-rendimenti/reel_forward.csv
"""
import pandas as pd, numpy as np, os
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..","..")
PROC=os.path.join(ROOT,"data","processed")
OUTdir=os.path.join(ROOT,"public","charts","cape-internazionale-predice-rendimenti")

MKT="Developed Markets Large"
ret=pd.read_csv(os.path.join(PROC,"returns_panel_wide.csv"))[["month",MKT]].dropna().reset_index(drop=True)
months=list(ret.month); lvl=list(ret[MKT])
def path(start, n=120):
    i0=months.index(start)
    base=lvl[i0]
    return [lvl[i0+k]/base for k in range(n+1)]

eco=path("2009-01")   # economico: rel 0.55
car=path("2001-01")   # caro: rel 1.51
dates=pd.date_range("2000-01-31", periods=len(eco), freq="ME")   # date fittizie: contano gli anni trascorsi
df=pd.DataFrame({"date":dates,"economico":eco,"caro":car})
os.makedirs(OUTdir,exist_ok=True)
df.to_csv(os.path.join(OUTdir,"reel_forward.csv"),index=False)
print(f"ECONOMICO (World 2009): 1 -> {eco[-1]:.2f}x  (+{(eco[-1]-1)*100:.0f}%) in 10 anni")
print(f"CARO      (World 2001): 1 -> {car[-1]:.2f}x  (+{(car[-1]-1)*100:.0f}%) in 10 anni")
