"""
SmartMoneyLab — Download dati per "portafoglio-personale" (Tipo C — test di portafogli reali)
=============================================================================================

Scarica tramite yfinance tutti i ticker necessari per:
  1. Il backtest a lungo storico (rolling 5y/10y/20y) usando PROXY storici
  2. Il confronto NAV reale degli ETF UCITS dal lancio (per il "controllo 5y")
  3. La simulazione Monte Carlo (usa i proxy del backtest 20y)

Salva ogni ticker come CSV in data/cache/yf_<slug>.csv con colonne:
  Date, Open, High, Low, Close, AdjClose, Volume

Note importanti:
- "AdjClose" su yfinance riflette il Total Return (dividendi reinvestiti) per le
  azioni/ETF US. Per i ticker UCITS Acc il NAV stesso e' gia' total return (le
  cedole vengono accumulate dentro), quindi Close e AdjClose dovrebbero
  coincidere o quasi.
- Per BTC-USD AdjClose = Close (no dividendi).

Dipendenze: yfinance, pandas.
Installazione: pip install yfinance pandas

Esecuzione:
  python scripts/download_portfolio_data.py

Tempo: ~1-3 minuti totali, dipende dalla connessione.

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yfinance as yf

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

START = "1990-01-01"  # alcuni ticker partono dopo, yfinance gestisce
END = "2025-12-31"

# -------------------------------------------------------------------- #
# Mappa: ticker yfinance -> slug del file CSV in cache                 #
# -------------------------------------------------------------------- #
# Gruppo A — PROXY a lungo storico per il backtest serio (20y)
PROXY_TICKERS = {
    # Azionario USA (anche se gia' abbiamo yahoo_gspc, scarichiamo Adj Close TR)
    "^GSPC":   "proxy_sp500",            # S&P 500 price (TR via Shiller in altro file)
    "SPY":     "proxy_spy",              # SPY ETF Adj Close = TR, dal 1993

    # Azionariato Globale: useremo SWDA.L (UCITS, dal 2009) per la parte recente
    # e SPY come proxy semplificato per il pre-2009 (alta correlazione)
    "URTH":    "proxy_urth_world",       # iShares MSCI World ETF, dal 2012

    # Mercati Emergenti
    "EEM":     "proxy_eem_em",           # iShares MSCI EM, dal 2003

    # Oro: scarico Adj Close giornaliero come complemento al gold_monthly gia in cache
    "GLD":     "proxy_gld_gold",         # SPDR Gold Shares, dal 2004

    # Small Cap (proxy US — alta correlazione col World Small Cap)
    "IWM":     "proxy_iwm_smallcap",     # iShares Russell 2000, dal 2000
    "^RUT":    "proxy_rut_russell2000",  # Russell 2000 Index, dal 1987

    # Nasdaq 100 (gia' abbiamo qqq_qld_daily, riscaricoamo Adj Close)
    "QQQ":     "proxy_qqq_nasdaq100",    # Invesco QQQ, dal 1999
    "^NDX":    "proxy_ndx_nasdaq100",    # Nasdaq 100 index, dal 1985

    # Bitcoin
    "BTC-USD": "proxy_btc_bitcoin",      # Bitcoin daily, dal 2014

    # Healthcare (proxy US — Tyler conferma per maggiore storicita')
    "XLV":     "proxy_xlv_healthcare",   # Health Care Select Sector SPDR, dal 1998

    # Europa
    "VGK":     "proxy_vgk_europe",       # Vanguard FTSE Europe, dal 2005
    "IEV":     "proxy_iev_europe_old",   # iShares Europe ETF, dal 2000 (backup pre-2005)

    # Asia ex Japan
    "AAXJ":    "proxy_aaxj_asia_exjp",   # iShares MSCI All Country Asia ex Japan, dal 2008

    # Energia tradizionale
    "XLE":     "proxy_xle_energy",       # Energy Select Sector SPDR, dal 1998

    # Clean Energy
    "ICLN":    "proxy_icln_clean",       # iShares Global Clean Energy, dal 2008

    # Uranium / Nucleare
    "URA":     "proxy_ura_uranium",      # Global X Uranium, dal 2010

    # Sleeve difensive aggiunte per l'articolo "Quale sleeve difensiva..."
    "XLP":     "proxy_xlp_staples",      # Consumer Staples Select Sector SPDR, dal 1998
    "XLU":     "proxy_xlu_utilities",    # Utilities Select Sector SPDR, dal 1998
    "USMV":    "proxy_usmv_minvol",      # iShares MSCI USA Min Volatility, dal 2011
    "QUAL":    "proxy_qual_quality",     # iShares MSCI USA Quality Factor, dal 2013
}

# Gruppo B — ETF UCITS REALI nel portafoglio di Tyler
# Servono per il "confronto NAV reale" sul periodo recente (5y)
# I ticker Yahoo per .MI (Milano) e .DE (XETRA) vanno come segue
UCITS_TICKERS = {
    # Oro
    "PPFB.DE":  "ucits_ppfb_gold",                  # iShares Physical Gold ETC (XETRA)
    # USA
    "A500.MI":  "ucits_a500_amundi_sp500",          # Amundi S&P 500 Swap (Milano)
    # Globale
    "SWDA.MI":  "ucits_swda_ishares_world",         # iShares Core MSCI World (Milano)
    # EM
    "XMME.MI":  "ucits_xmme_xtrackers_em",          # Xtrackers MSCI EM (Milano)
    # Small Cap
    "CBUG.DE":  "ucits_cbug_world_smallcap",        # iShares MSCI World Small Cap (XETRA)
    # Nasdaq
    "LYMS.DE":  "ucits_lyms_amundi_nasdaq",         # Amundi Nasdaq 100 Swap (XETRA)
    # Bitcoin
    "FBTC.DE":  "ucits_fbtc_fidelity_btc",          # Fidelity Physical Bitcoin (XETRA)
    # Disruptive Tech
    "UNIC.MI":  "ucits_unic_amundi_disruptive",     # Amundi MSCI Disruptive Tech (Milano)
    # Automation & Robotics
    "RBOT.MI":  "ucits_rbot_ishares_robotics",      # iShares Automation & Robotics (Milano)
    # Healthcare
    "XDWH.MI":  "ucits_xdwh_xtrackers_health",      # Xtrackers MSCI World Health Care (Milano)
    # Europa
    "XMEU.MI":  "ucits_xmeu_xtrackers_europe",      # Xtrackers MSCI Europe (Milano)
    # Asia
    "AASI.MI":  "ucits_aasi_amundi_asia",           # Amundi MSCI EM Asia (Milano)
    # Energia trad
    "XDW0.MI":  "ucits_xdw0_xtrackers_energy",      # Xtrackers MSCI World Energy (Milano)
    # Nucleare
    "NUCL.MI":  "ucits_nucl_vaneck_uranium",        # VanEck Uranium and Nuclear Tech (Milano)
    # Clean Energy
    "EMOVE.MI": "ucits_emove_finecoam_clean",       # Fineco AM MarketVector Clean Energy (Milano)
}


def download_one(ticker: str, slug: str, retries: int = 3) -> bool:
    """Scarica un singolo ticker e salva il CSV. Restituisce True se OK."""
    out_path = CACHE_DIR / f"yf_{slug}.csv"
    if out_path.exists() and out_path.stat().st_size > 1000:
        print(f"[cache OK] {ticker:14s} -> {out_path.name}")
        return True

    for attempt in range(1, retries + 1):
        try:
            print(f"[download {attempt}/{retries}] {ticker:14s} ...", end=" ", flush=True)
            data = yf.download(
                ticker, start=START, end=END,
                progress=False, auto_adjust=False,
                threads=False,
            )
            if data.empty:
                print("VUOTO")
                time.sleep(2)
                continue
            # Flatten multi-index columns (yfinance >=0.2.40 a volte le mette)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data.index = pd.DatetimeIndex(data.index).tz_localize(None)
            data.index.name = "Date"
            # Rinomina la colonna "Adj Close" come "AdjClose" per compat con i nostri loader
            cols = {c: c.replace(" ", "") for c in data.columns}
            data = data.rename(columns=cols)
            data.to_csv(out_path)
            n_rows = len(data)
            first = data.index[0].date()
            last = data.index[-1].date()
            print(f"OK ({n_rows} righe, {first} -> {last})")
            return True
        except Exception as exc:
            print(f"ERROR: {exc}")
            time.sleep(2 ** attempt)
    return False


def main():
    print("=== Download dati portafoglio-personale ===\n")
    print("Gruppo A — PROXY a lungo storico (per backtest 20y e Monte Carlo)\n")
    failed_a = []
    for ticker, slug in PROXY_TICKERS.items():
        if not download_one(ticker, slug):
            failed_a.append(ticker)

    print("\nGruppo B — ETF UCITS reali (per confronto NAV reale recente)\n")
    failed_b = []
    for ticker, slug in UCITS_TICKERS.items():
        if not download_one(ticker, slug):
            failed_b.append(ticker)

    print("\n=== Riepilogo ===")
    print(f"PROXY scaricati OK: {len(PROXY_TICKERS) - len(failed_a)}/{len(PROXY_TICKERS)}")
    if failed_a:
        print(f"  FALLITI: {failed_a}")
    print(f"UCITS scaricati OK: {len(UCITS_TICKERS) - len(failed_b)}/{len(UCITS_TICKERS)}")
    if failed_b:
        print(f"  FALLITI: {failed_b}")
        print("  (per i UCITS falliti puoi scaricare manualmente i CSV da")
        print("   borsaitaliana.it o justetf.com → Storico → Excel)")

    print("\nDone.")


if __name__ == "__main__":
    main()
