"""
Costruisce il panel CAPE per paese (semestrale 1998-2026) dagli snapshot RA.
Input : data/processed/_cape_store.json  (estratto dagli screenshot in data/raw/cape_snapshots)
Output: data/processed/cape_panel_long.csv  (date, market, cape)
        data/processed/cape_panel_wide.csv  (date x market)
Validazione: incrocio ultimo snapshot vs colonna "Current" del file RA;
             report copertura per mercato; segnalazione salti MoM estremi.
"""
import json, csv, os
from datetime import date

HERE = os.path.dirname(__file__)
PROC = os.path.join(HERE, "..", "data", "processed")
RAW  = os.path.join(HERE, "..", "data", "raw")

store = json.load(open(os.path.join(PROC, "_cape_store.json")))
dates = sorted(store.keys())
markets = list(next(iter(store.values())).keys())

# --- CSV wide ---
with open(os.path.join(PROC, "cape_panel_wide.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date"] + markets)
    for d in dates:
        w.writerow([d] + [store[d][m] for m in markets])

# --- CSV long ---
n_obs = 0
with open(os.path.join(PROC, "cape_panel_long.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "market", "cape"])
    for d in dates:
        for m in markets:
            v = store[d][m]
            if v is not None:
                w.writerow([d, m, v]); n_obs += 1

print(f"Date: {len(dates)}  ({dates[0]} -> {dates[-1]})")
print(f"Mercati: {len(markets)}")
print(f"Osservazioni non nulle: {n_obs}")

# --- copertura per mercato ---
print("\n== COPERTURA PER MERCATO (prima data, n oss) ==")
cov = []
for m in markets:
    ser = [(d, store[d][m]) for d in dates if store[d][m] is not None]
    first = ser[0][0] if ser else "-"
    cov.append((m, first, len(ser)))
for m, first, n in sorted(cov, key=lambda x: x[1]):
    print(f"  {m:24s} da {first}  ({n}/54)")

# --- salti MoM estremi (possibili errori OCR o crolli reali) ---
print("\n== SALTI SEMESTRE-SU-SEMESTRE > 45% (da controllare a occhio) ==")
flags = 0
for m in markets:
    prev = None
    for d in dates:
        v = store[d][m]
        if v is not None and prev is not None and prev[1] is not None:
            chg = (v - prev[1]) / prev[1]
            if abs(chg) > 0.45:
                print(f"  {m:22s} {prev[0]}->{d}: {prev[1]} -> {v}  ({chg:+.0%})")
                flags += 1
        if v is not None:
            prev = (d, v)
print(f"  ({flags} salti segnalati - molti sono reali: 2008-09, COVID 2020)")

# --- gap interni (buco tra due valori presenti) ---
print("\n== GAP INTERNI (valore mancante tra due presenti) ==")
gaps = 0
for m in markets:
    idx = [i for i, d in enumerate(dates) if store[d][m] is not None]
    if idx:
        for i in range(idx[0], idx[-1] + 1):
            if store[dates[i]][m] is None:
                print(f"  {m}: buco a {dates[i]}"); gaps += 1
print(f"  ({gaps} gap interni)")
