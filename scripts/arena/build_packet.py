#!/usr/bin/env python3
"""Costruisce il pacchetto informativo identico per tutti i modelli (packet_<date>.json).
Gira dove yfinance funziona (GitHub Action / macchina di Tyler), NON nel sandbox cloud."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

MACRO = {
    "SPX": "^GSPC", "NDX": "^NDX", "RUT": "^RUT", "STOXX50": "^STOXX50E",
    "UST10Y": "^TNX", "UST13W": "^IRX", "VIX": "^VIX",
    "DXY": "DX-Y.NYB", "GOLD": "GC=F", "WTI": "CL=F", "BTC": "BTC-USD",
}
NEWS_SEEDS = ["AAPL", "MSFT", "NVDA", "AMZN", "JPM", "XOM", "IVV", "QQQ"]

def pct(a, b):
    return round(a / b - 1, 4) if (b and b != 0) else None

def build(cfg):
    import yfinance as yf
    import pandas as pd
    meta, tickers = ac.load_universe(cfg)
    tickers = sorted(tickers)
    today = dt.date.today().isoformat()

    # --- storico bulk per prezzi/rendimenti/52w/vol ---
    hist = yf.download(tickers, period="1y", interval="1d", auto_adjust=True,
                       progress=False, threads=True)
    close = hist["Close"]; vol = hist["Volume"]
    instruments = []
    for t in tickers:
        try:
            s = close[t].dropna()
            if len(s) < 5: continue
            last = float(s.iloc[-1])
            def back(days):
                if len(s) > days: return float(s.iloc[-1-days])
                return float(s.iloc[0])
            row = {"ticker": t, "class": meta[t]["class"], "group": meta[t]["group"],
                   "name": meta[t].get("name") or "",
                   "price": round(last, 2),
                   "ret_1w": pct(last, back(5)), "ret_1m": pct(last, back(21)),
                   "ret_3m": pct(last, back(63)), "ret_12m": pct(last, back(252)),
                   "range_52w": [round(float(s.min()), 2), round(float(s.max()), 2)]}
            try:
                v = vol[t].dropna(); row["avg_vol"] = int(v.tail(21).mean()) if len(v) else None
            except Exception:
                row["avg_vol"] = None
            instruments.append(row)
        except Exception as e:
            print("skip", t, e)

    # --- fondamentali best-effort (PE, div yield) solo per azioni/ETF ---
    for row in instruments:
        try:
            info = yf.Ticker(row["ticker"]).info
            row["pe"] = round(info["trailingPE"], 1) if info.get("trailingPE") else None
            dy = info.get("dividendYield")
            row["div_yield"] = round(dy, 4) if dy else None
        except Exception:
            row["pe"] = None; row["div_yield"] = None

    # --- macro ---
    macro = {}
    mh = yf.download(list(MACRO.values()), period="1mo", interval="1d",
                     auto_adjust=True, progress=False, threads=True)["Close"]
    for k, tk in MACRO.items():
        try:
            s = mh[tk].dropna()
            macro[k] = {"last": round(float(s.iloc[-1]), 2),
                        "ret_1w": pct(float(s.iloc[-1]), float(s.iloc[-6])) if len(s) > 6 else None}
        except Exception:
            macro[k] = {"last": None, "ret_1w": None}

    # --- notizie (yfinance .news, deduplicate) ---
    news = []; seen = set()
    for t in NEWS_SEEDS:
        try:
            for n in (yf.Ticker(t).news or [])[:6]:
                title = n.get("title") or n.get("content", {}).get("title")
                if not title or title in seen: continue
                seen.add(title)
                ts = n.get("providerPublishTime")
                date = dt.datetime.utcfromtimestamp(ts).date().isoformat() if ts else today
                news.append({"date": date, "source": n.get("publisher", ""),
                             "title": title, "url": n.get("link", ""),
                             "tickers": n.get("relatedTickers", [])})
                if len(news) >= cfg["news"]["max_headlines"]: break
        except Exception:
            pass
        if len(news) >= cfg["news"]["max_headlines"]: break

    packet = {"as_of": today, "generated": dt.datetime.utcnow().isoformat(),
              "macro": macro, "instruments": instruments, "news": news}
    path = ac.state_path(cfg, "packets", f"packet_{today}.json")
    ac.write_json(path, packet)
    ac.write_json(ac.state_path(cfg, "packets", "packet_latest.json"), packet)
    print(f"[packet] {len(instruments)} strumenti, {len(news)} notizie -> {path}")
    return packet

if __name__ == "__main__":
    build(ac.load_config())
