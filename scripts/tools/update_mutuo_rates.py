"""Aggiorna public/tools/mutuo-rates.json con gli ultimi tassi dalla BCE (API REST
gratuita, https://data-api.ecb.europa.eu). Fisso e variabile = tassi MIR sui nuovi
mutui casa in Italia; Euribor 3M. Nessuna chiave/costo. Eseguire manualmente o via
GitHub Action mensile; poi commit del JSON (come cape-lookup.json).

Uso: python scripts/tools/update_mutuo_rates.py
"""
import json, os, sys, urllib.request, io, csv, datetime

BASE = "https://data-api.ecb.europa.eu/service/data"
SERIES = {
    "fisso":     "MIR/M.IT.B.A2C.P.R.A.2250.EUR.N",   # nuovo mutuo casa, fisso (oltre 10y)
    "variabile": "MIR/M.IT.B.A2C.F.R.A.2250.EUR.N",   # nuovo mutuo casa, variabile (fino 1y)
    "euribor":   "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA", # Euribor 3M mensile
}
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "public", "tools", "mutuo-rates.json")

def last_obs(path):
    url = f"{BASE}/{path}?lastNObservations=1&format=csvdata"
    req = urllib.request.Request(url, headers={"User-Agent": "SmartMoneyLab/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(text)))
    head, data = rows[0], rows[-1]
    ti, vi = head.index("TIME_PERIOD"), head.index("OBS_VALUE")
    return data[ti], round(float(data[vi]), 3)

def main():
    out = {"meta": {"source": "BCE / ECB Data Portal (data-api.ecb.europa.eu)",
                    "series": SERIES,
                    "updated": datetime.date.today().isoformat()}}
    for name, path in SERIES.items():
        try:
            period, val = last_obs(path)
            out[name] = {"pct": val, "period": period}
        except Exception as e:
            print(f"[warn] {name}: {e}", file=sys.stderr)
    # spread commerciale del variabile sull'Euribor (per far evolvere il variabile sotto stress)
    if "variabile" in out and "euribor" in out:
        out["spread_variabile"] = round(out["variabile"]["pct"] - out["euribor"]["pct"], 3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("OK ->", os.path.normpath(OUT))
    print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
