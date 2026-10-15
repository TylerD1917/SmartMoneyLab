# -*- coding: utf-8 -*-
"""Dati per il reel 'vuoi proteggerti dal petrolio? non comprarlo'.

Crescita di un dollaro dall'aprile 2005 nel settore azionario energy e in un
indice di materie prime investibile (Bloomberg Commodity piu' collaterale in
T-bill). Il mercato azionario resta fuori dal reel: a +900% schiaccerebbe le
due curve che il reel deve far confrontare.

Uso:  python scripts/social/dati_reel_energy.py
Out:  social/settore-energy-proxy-materie-prime/reel_energy_vs_commodity.csv
"""
import importlib.util, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STUDIO = os.path.join(ROOT, "scripts", "settore-energy-proxy-materie-prime.py")
OUT = os.path.join(ROOT, "social", "settore-energy-proxy-materie-prime",
                   "reel_energy_vs_commodity.csv")

spec = importlib.util.spec_from_file_location("studio", STUDIO)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)

energy, mkt, rf = M.dati_french()
bcom, dbc, _ = M.dati_commodity(rf)
k = energy.index.intersection(bcom.index)
df = pd.DataFrame({"Settore energy": (1 + energy[k]).cumprod(),
                   "Materie prime": (1 + bcom[k]).cumprod()})
# Riga seme a 1,00 il mese prima: il reel mostra la variazione rispetto al PRIMO
# punto del CSV, quindi senza seme il primo mese sparirebbe dal conto e la
# percentuale finale uscirebbe gonfiata (era +445% invece di +414%).
seme = pd.DataFrame({c: [1.0] for c in df.columns}, index=[k[0] - 1])
df = pd.concat([seme, df]).sort_index()
df.index = df.index.to_timestamp(how="end").normalize()
df.index.name = "Date"
df.round(4).to_csv(OUT)
print(f"{len(df)} mesi, {df.index[0].date()} -> {df.index[-1].date()}")
print(df.tail(1).to_string())
print("scritto", OUT)
