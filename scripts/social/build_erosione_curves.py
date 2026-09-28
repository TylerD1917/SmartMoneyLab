# -*- coding: utf-8 -*-
"""Serie per il reel dell'articolo "Quanto rende davvero l'azionario al netto...".

Quattro curve sul MSCI World in euro, ultimi 20 anni, base 100: indice lordo,
poi i tre strati di erosione applicati uno sull'altro. L'imposta del 26% e'
calcolata come se si vendesse in quella data, cioe' esattamente il metodo
dell'articolo applicato a ogni possibile data di uscita.
"""
import importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "studio", ROOT / "scripts" / "rendimenti-netti-indici-azionari.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ANNI = 20
OUT = ROOT / "social" / "quanto-rende-azionario-netto-tasse-costi" / "curve_erosione.csv"

cpi, _ = m.build_cpi_it()
eurusd, _ = m.build_eurusd()
idx = m.build_indices(eurusd)["MSCI World"]

# finestra: gli ultimi 20 anni pieni
idx = idx.iloc[-(ANNI * 12 + 1):]
nav = m.etf_series(idx, m.ETF["MSCI World"], None, with_noise=False)

lordo = idx / idx.iloc[0]
netto_costi = nav / nav.iloc[0]
netto_tasse = 1.0 + (netto_costi - 1.0) * (1.0 - m.ALIQUOTA)
infl = cpi.reindex(netto_costi.index)
netto_reale = netto_tasse / (infl / infl.iloc[0])

df = pd.DataFrame({
    "Data": [str(p) for p in lordo.index],
    "lordo": (lordo * 100).values,
    "netto_costi": (netto_costi * 100).values,
    "netto_tasse": (netto_tasse * 100).values,
    "netto_reale": (netto_reale * 100).values,
})
df.to_csv(OUT, index=False)

print(f"periodo: {df.Data.iloc[0]} -> {df.Data.iloc[-1]}  ({len(df)-1} mesi)")
print(f"{'curva':<14}{'finale (base 100)':>20}{'variazione':>14}")
for c, lab in [("lordo", "indice lordo"), ("netto_costi", "meno costi"),
               ("netto_tasse", "meno 26%"), ("netto_reale", "meno inflazione")]:
    v = df[c].iloc[-1]
    print(f"{lab:<14}{v:>20.1f}{(v/100-1)*100:>13.1f}%")
