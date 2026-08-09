"""
Parsa gli indici MSCI Gross TR USD mensili (data/raw/msci_*.xls) in un dataset tidy.
Output: data/processed/returns_panel_long.csv  (month, date, market, level)
        data/processed/returns_panel_wide.csv  (month x market, livelli indice)
I nomi mercato sono mappati sui nomi del CAPE panel dove esiste corrispondenza.
"""
import xlrd, glob, os, csv, datetime as dt

HERE = os.path.dirname(__file__)
RAW  = os.path.join(HERE, "..", "data", "raw")
PROC = os.path.join(HERE, "..", "data", "processed")

# file MSCI -> nome mercato canonico (allineato al CAPE panel dove possibile)
MAP = {
    "msci_usa": "US Large", "msci_japan": "Japan", "msci_germany": "Germany",
    "msci_france": "France", "msci_switzerland": "Switzerland", "msci_australia": "Australia",
    "msci_canada": "Canada", "msci_italy": "Italy", "msci_spain": "Spain",
    "msci_netherlands": "Netherlands", "msci_belgium": "Belgium", "MSCI_austria": "Austria",
    "msci_denmark": "Denmark", "msci_finland": "Finland", "msci_norway": "Norway", "msci_sweden": "Sweden",
    "msci_europe": "Europe", "msci_em": "Emerging Markets", "msci_asia_ex_JAPAN": "Asia ex Japan",
    "msci_world": "Developed Markets Large",   # MSCI World = mercati sviluppati
    "msci_brasil": "Brazil", "msci_china": "China", "msci_india": "India",
    "msci_Sudafrica": "South Africa", "msci_korea": "South Korea", "msci_taiwan": "Taiwan",
    "msci_indonesia": "Indonesia", "msci_thailand": "Thailand",
    "msci_Nordic": "Nordics",  # aggregato MSCI pronto
    # aggregati extra (referenza, non nel pooled): UK, EMU, EU, ACWI, EM Asia, World+USA
    "msci_UK": "United Kingdom", "msci_acwi": "ACWI", "msci_em_asia": "EM Asia",
}

def parse(path):
    wb = xlrd.open_workbook(path); sh = wb.sheet_by_index(0)
    out = []
    for r in range(sh.nrows):
        a = sh.cell_value(r, 0); b = sh.cell_value(r, 1) if sh.ncols > 1 else ""
        if isinstance(a, str) and "," in a and b not in ("", None):
            try:
                d = dt.datetime.strptime(a.strip(), "%b %d, %Y").date()
            except ValueError:
                continue
            try:
                lvl = float(str(b).replace(",", ""))
            except ValueError:
                continue
            out.append((d, lvl))
    return out

rows = []
for f in sorted(glob.glob(os.path.join(RAW, "msci_*.xls")) + glob.glob(os.path.join(RAW, "MSCI_*.xls"))):
    stem = os.path.basename(f)[:-4]
    if stem not in MAP:
        continue
    mkt = MAP[stem]
    for d, lvl in parse(f):
        rows.append((f"{d.year}-{d.month:02d}", d.isoformat(), mkt, lvl))

rows.sort(key=lambda x: (x[2], x[0]))
os.makedirs(PROC, exist_ok=True)
with open(os.path.join(PROC, "returns_panel_long.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["month", "date", "market", "level"]); w.writerows(rows)

# wide
months = sorted(set(r[0] for r in rows))
markets = sorted(set(r[2] for r in rows))
lvl = {(r[0], r[2]): r[3] for r in rows}
with open(os.path.join(PROC, "returns_panel_wide.csv"), "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["month"] + markets)
    for m in months:
        w.writerow([m] + [lvl.get((m, mk), "") for mk in markets])

print(f"Mercati: {len(markets)}")
print(f"Mesi: {len(months)}  ({months[0]} -> {months[-1]})")
print("Elenco mercati:", ", ".join(markets))
