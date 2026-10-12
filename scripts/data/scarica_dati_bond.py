# -*- coding: utf-8 -*-
"""
Scarica le serie che servono agli ETF obbligazionari sintetici e le salva in
data/Bonds/. Idempotente: rilanciandolo riscrive i file con i dati aggiornati.

Rendimenti (FRED, CSV diretto):
  DGS7   Treasury 7 anni, costant maturity, dal 1969-07
  DGS30  Treasury 30 anni, dal 1977-02 (serve a tappare il buco 1987-1993 del
         DGS20, quando il ventennale non veniva emesso)
  IRLTLT01EZM156N  area euro, rendimento governativo a lungo termine, dal 1970
  INTGSBITM193N    Italia, rendimento titoli di Stato, dal 1980 (fonte FMI)
  IRLTLT01ITM156N  Italia, OCSE, dal 1991: serve solo a prolungare la serie FMI

ETF reali (Yahoo, prezzi aggiustati = total return): ancore per verificare che
gli indici sintetici traccino la realta' nel periodo di sovrapposizione.
  TLT      iShares 20+ Year Treasury Bond, dal 2002
  SXRM.DE  iShares USD Treasury Bond 7-10yr, dal 2009
  SXRQ.DE  iShares Euro Government Bond 7-10yr, dal 2009
  IBGL.AS  iShares Euro Government Bond 15-30yr, dal 2008

  python scripts/data/scarica_dati_bond.py
"""
import io
import os
import time
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "data", "Bonds"))

FRED = {
    "DGS7_fred_1969.csv": "DGS7",
    "DGS30_fred_1977.csv": "DGS30",
    "EZ10Y_oecd_1970.csv": "IRLTLT01EZM156N",
    "IT10Y_imf_1980.csv": "INTGSBITM193N",
    "IT10Y_oecd_1991.csv": "IRLTLT01ITM156N",
}
ETF = {"TLT.csv": "TLT", "SXRM.csv": "SXRM.DE", "SXRQ.csv": "SXRQ.DE",
       "IBGL.csv": "IBGL.AS"}


def da_fred(serie: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}"
    with urllib.request.urlopen(url, timeout=60) as r:
        testo = r.read().decode("utf-8")
    df = pd.read_csv(io.StringIO(testo))
    df.columns = ["observation_date", serie]
    df[serie] = pd.to_numeric(df[serie], errors="coerce")
    return df.dropna(subset=[serie])


def da_yahoo(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    h = yf.Ticker(ticker).history(period="max", auto_adjust=True)
    if h.empty:
        raise RuntimeError(f"{ticker}: nessun dato")
    out = h[["Close"]].reset_index()
    out.columns = ["Date", "Close"]
    out["Date"] = pd.to_datetime(out["Date"]).dt.tz_localize(None).dt.date
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for nome, serie in FRED.items():
        df = da_fred(serie)
        df.to_csv(os.path.join(OUT, nome), index=False)
        print(f"  {nome:24s} {len(df):6d} oss  "
              f"{df.iloc[0, 0]} -> {df.iloc[-1, 0]}")
        time.sleep(1)
    for nome, ticker in ETF.items():
        try:
            df = da_yahoo(ticker)
            df.to_csv(os.path.join(OUT, nome), index=False)
            print(f"  {nome:24s} {len(df):6d} oss  "
                  f"{df['Date'].iloc[0]} -> {df['Date'].iloc[-1]}")
        except Exception as e:
            print(f"  {nome:24s} ERRORE {type(e).__name__}: {str(e)[:70]}")
        time.sleep(2)


if __name__ == "__main__":
    main()
