"""
Download del dataset per lo studio sulle correlazioni tra asset class.

Scarica da Yahoo Finance i prezzi mensili (Adj Close, total return per gli
ETF; front-month per i futures; spot per Bitcoin) di 31 asset in USD, e li
salva in un unico CSV wide + i singoli file.

Da lanciare in LOCALE (yfinance ha bisogno di rete, bloccata nel sandbox):

    pip install --upgrade yfinance pandas
    python scripts/download_correlation_data.py

IMPORTANTE: aggiorna yfinance prima di lanciare. Una versione vecchia, con
`start` ma senza `end`, scarica per errore un solo mese (bug noto). Questo
script passa SEMPRE un `end` esplicito e scarica ticker-per-ticker con
gestione degli errori, per evitare il problema.

Output:
    data/cache/correlation_universe_monthly.csv   (wide: Date + una colonna per asset)
    data/cache/corr_<slug>.csv                    (singoli, per debug)

Convenzioni:
    - ETF azionari/obbligazionari: auto_adjust=True -> Adj Close = total return.
    - Futures materie prime (=F): front-month, prezzo.
    - Bitcoin: spot BTC-USD.
    - Frequenza: fine mese (ultimo valore del mese).

Autore: SmartMoneyLab - 2026.
"""
from __future__ import annotations
from pathlib import Path
import sys
import time

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    sys.exit("Manca yfinance/pandas. Esegui: pip install --upgrade yfinance pandas")

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

# ticker Yahoo -> (slug file, nome leggibile, categoria)
UNIVERSE = {
    # --- Beni rifugio / materie prime (6) ---
    "BTC-USD": ("btc",      "Bitcoin",              "rifugio"),
    "GC=F":    ("gold",     "Oro",                  "rifugio"),
    "SI=F":    ("silver",   "Argento",              "rifugio"),
    "HG=F":    ("copper",   "Rame",                 "rifugio"),
    "CL=F":    ("oil",      "Petrolio (WTI)",       "rifugio"),
    "TLT":     ("tlt",      "Treasury USA 20+",     "rifugio"),
    # --- Settoriali (10) ---
    "QQQ":     ("nasdaq",   "Nasdaq 100",           "settore"),
    "XLE":     ("energy",   "Energy",               "settore"),
    "XLV":     ("health",   "Healthcare",           "settore"),
    "XLF":     ("financial","Financials",           "settore"),
    "IVE":     ("value",    "Value (S&P500)",       "settore"),
    "XLP":     ("staples",  "Consumer Staples",     "settore"),
    "IWM":     ("smallcap", "Small Cap (Russell 2000)", "settore"),
    "VNQ":     ("reit",     "Real Estate (REIT)",   "settore"),
    "ITA":     ("defense",  "Difesa & Aerospazio",  "settore"),
    "SOXX":    ("semi",     "Semiconduttori",       "settore"),
    # --- Geografici (10) ---
    "SPY":     ("usa",      "USA (S&P 500)",        "geo"),
    "URTH":    ("world_etf","MSCI World (ETF)",     "geo"),
    "ACWI":    ("acwi_etf", "ACWI (ETF)",           "geo"),
    "EEM":     ("em",       "Mercati Emergenti",    "geo"),
    "VGK":     ("europe",   "Europa",               "geo"),
    "EWG":     ("germany",  "Germania",             "geo"),
    "EWU":     ("uk",       "Regno Unito",          "geo"),
    "FXI":     ("china",    "Cina",                 "geo"),
    "EWJ":     ("japan",    "Giappone",             "geo"),
    "ILF":     ("latam",    "America Latina",       "geo"),
    # --- Bonus geografici (5) ---
    "EWY":     ("korea",    "Corea del Sud",        "bonus"),
    "EWA":     ("australia","Australia",            "bonus"),
    "EPI":     ("india",    "India",                "bonus"),
    "EWC":     ("canada",   "Canada",               "bonus"),
    "EWT":     ("taiwan",   "Taiwan",               "bonus"),
}

START = "1993-01-01"


def fetch_one(ticker: str, end: str, retries: int = 3) -> pd.Series | None:
    """Scarica un singolo ticker, Adj Close mensile. None se fallisce."""
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(ticker, start=START, end=end, auto_adjust=True,
                             progress=False, threads=False)
            if df is None or df.empty:
                raise ValueError("dataframe vuoto")
            close = df["Close"]
            if isinstance(close, pd.DataFrame):   # a volte multi-col
                close = close.iloc[:, 0]
            monthly = close.resample("ME").last().dropna()
            if len(monthly) < 2:
                raise ValueError(f"solo {len(monthly)} punti mensili")
            return monthly
        except Exception as e:
            print(f"    tentativo {attempt}/{retries} fallito ({e})")
            time.sleep(1.5 * attempt)
    return None


def main():
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    print(f"[dl] scarico {len(UNIVERSE)} ticker, {START} -> {end}, uno per uno...")

    series = {}
    failed = []
    for tk, (slug, nome, cat) in UNIVERSE.items():
        s = fetch_one(tk, end)
        if s is None:
            print(f"  [X] {tk:<9} {nome:<26} FALLITO")
            failed.append(tk)
            continue
        s.name = nome
        s.to_csv(CACHE / f"corr_{slug}.csv", header=["adjclose"])
        series[nome] = s
        print(f"  [ok] {tk:<9} {nome:<26} {s.index[0].date()} -> {s.index[-1].date()} ({len(s)} mesi)")

    if not series:
        sys.exit("\nNessun ticker scaricato. Aggiorna yfinance: pip install --upgrade yfinance")

    wide = pd.DataFrame(series).sort_index()
    out = CACHE / "correlation_universe_monthly.csv"
    wide.to_csv(out, index_label="date")
    print(f"\n[ok] salvato {out}  ({wide.shape[0]} righe, {wide.shape[1]} asset)")

    if failed:
        print(f"\n[!] ticker falliti ({len(failed)}): {', '.join(failed)}")
        print("    Riprova a rilanciare (spesso Yahoo risponde al secondo giro),")
        print("    oppure segnalali: ho fallback per oro/petrolio dai file gia' in cache.")


if __name__ == "__main__":
    main()
