"""
Articolo di lancio "Portafogli a confronto" — grafico rendimenti (da leaderboard.json).
Bar chart orizzontale: rendimento annualizzato a 7 anni (EUR), tutti i portafogli,
colorati per categoria. Snapshot statico per l'articolo (il live è su /portafogli).
Output: public/charts/portafogli-famosi-a-confronto/01_classifica_7a.png
"""
import os, json
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
HERE=os.path.dirname(__file__); ROOT=os.path.join(HERE,"..")
OUT=os.path.join(ROOT,"public","charts","portafogli-famosi-a-confronto"); os.makedirs(OUT,exist_ok=True)
NAVY="#1e3a8a"; GOLD="#fbbf24"; GREY="#94a3b8"; INK="#0f172a"
plt.rcParams.update({"font.size":12,"axes.grid":True,"grid.color":"#e2e8f0","figure.dpi":160,
    "savefig.bbox":"tight","axes.spines.top":False,"axes.spines.right":False})

d=json.load(open(os.path.join(ROOT,"public","tools","leaderboard.json")))
COLCAT={"benchmark":GREY,"classico":NAVY,"autore":GOLD}
rows=[]
for p in d["portfolios"]:
    y=p["metrics"].get("y7")
    if not isinstance(y,(int,float)): continue
    nm=p["name"]+(f" · {p['variant']}" if p["variant"] else "")
    rows.append((nm,y,p["category"]))
rows.sort(key=lambda r:r[1])
names=[r[0] for r in rows]; vals=[r[1]*100 for r in rows]; cols=[COLCAT[r[2]] for r in rows]

fig,ax=plt.subplots(figsize=(10.5,7))
y=np.arange(len(names))
ax.barh(y,vals,color=cols,height=0.72)
for i,v in enumerate(vals):
    ax.text(v+0.2,i,f"{v:.1f}%".replace(".",","),va="center",fontsize=10,weight="bold",color=INK)
ax.set_yticks(y); ax.set_yticklabels(names,fontsize=10.5)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
ax.set_xlim(0,max(vals)*1.12)
ax.set_xlabel("Rendimento annualizzato, ultimi 7 anni (in euro)")
ax.set_title("Portafogli a confronto: quanto hanno reso davvero\n7 anni, in euro, ribilanciamento annuale",fontsize=13.5,weight="bold")
ax.legend(handles=[Patch(color=NAVY,label="Portafogli classici"),Patch(color=GOLD,label="D'autore e tematici"),Patch(color=GREY,label="Benchmark di mercato")],
          fontsize=9.5,loc="lower right",framealpha=0.95)
asof=max(p["metrics"].get("as_of","") for p in d["portfolios"])
fig.text(0.5,-0.02,f"Dati al {asof} · versione live e aggiornata: smartmoneylab.it/portafogli",ha="center",fontsize=9,color=GREY,style="italic")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"01_classifica_7a.png")); plt.close(fig)
print("ok ->",OUT)
for nm,v,c in reversed(rows): print(f"  {nm:36s} {v*100:5.1f}%  [{c}]")
