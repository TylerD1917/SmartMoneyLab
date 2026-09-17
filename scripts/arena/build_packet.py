#!/usr/bin/env python3
"""Costruisce il pacchetto informativo identico per tutti i modelli (packet_<date>.json).
Gira dove yfinance funziona (GitHub Action / macchina di Tyler), NON nel sandbox cloud.
Notizie: feed RSS curati (economia, politica, banche centrali, geopolitica) + yfinance."""
import os, sys, json, re, html, urllib.request, datetime as dt
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

MACRO = {
    "SPX": "^GSPC", "NDX": "^NDX", "RUT": "^RUT", "STOXX50": "^STOXX50E",
    "UST10Y": "^TNX", "UST13W": "^IRX", "VIX": "^VIX",
    "DXY": "DX-Y.NYB", "GOLD": "GC=F", "WTI": "CL=F", "BTC": "BTC-USD",
}

def pct(a, b):
    return round(a / b - 1, 4) if (b and b != 0) else None

# ---------------- notizie: RSS/Atom con stdlib (nessuna dipendenza nuova) ----------------
def _clean(s, n=220):
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", s)          # via i tag HTML
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:n]

def _parse_date(s):
    if not s: return None
    s = s.strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    try:
        return dt.datetime.fromisoformat(s[:19]).date().isoformat()
    except Exception:
        return None

def fetch_feed(url, source, cat, limit, timeout=15):
    """Ritorna una lista di notizie da un feed RSS 2.0 o Atom. Resiliente: se fallisce, lista vuota."""
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SmartMoneyLab arena)"})
        raw = urllib.request.urlopen(req, timeout=timeout).read()
        root = ET.fromstring(raw)
    except Exception as e:
        print(f"  [news] KO {source}: {str(e)[:80]}")
        return out
    ns = {"a": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    items = root.findall(".//item")
    if items:                                 # RSS 2.0
        for it in items[:limit]:
            title = (it.findtext("title") or "").strip()
            if not title: continue
            out.append({"date": _parse_date(it.findtext("pubDate") or it.findtext("dc:date", namespaces=ns)),
                        "source": source, "cat": cat, "title": _clean(title, 240),
                        "summary": _clean(it.findtext("description") or ""),
                        "url": (it.findtext("link") or "").strip()})
    else:                                     # Atom
        for it in root.findall(".//a:entry", ns)[:limit]:
            title = (it.findtext("a:title", default="", namespaces=ns) or "").strip()
            if not title: continue
            le = it.find("a:link", ns)
            out.append({"date": _parse_date(it.findtext("a:updated", default="", namespaces=ns)
                                            or it.findtext("a:published", default="", namespaces=ns)),
                        "source": source, "cat": cat, "title": _clean(title, 240),
                        "summary": _clean(it.findtext("a:summary", default="", namespaces=ns)
                                          or it.findtext("a:content", default="", namespaces=ns)),
                        "url": le.get("href") if le is not None else ""})
    print(f"  [news] OK {source}: {len(out)}")
    return out

def gather_news(cfg, yf, today):
    ncfg = cfg["news"]
    per_feed = ncfg.get("per_feed", 6); max_h = ncfg.get("max_headlines", 40)
    news = []; seen = set()
    def add(item):
        key = re.sub(r"\W+", "", (item.get("title") or "").lower())[:80]
        if not item.get("title") or key in seen: return
        seen.add(key); news.append(item)
    print("[news] feed RSS:")
    for f in ncfg.get("feeds", []):
        for it in fetch_feed(f["url"], f.get("name", f["url"]), f.get("cat", ""), per_feed):
            add(it)
    # integrazione: yfinance news taggate ai megacap (finanza/mercato)
    for t in ncfg.get("yfinance_seeds", []):
        try:
            for n in (yf.Ticker(t).news or [])[:4]:
                title = n.get("title") or (n.get("content") or {}).get("title")
                if not title: continue
                ts = n.get("providerPublishTime")
                date = dt.datetime.utcfromtimestamp(ts).date().isoformat() if ts else today
                add({"date": date, "source": n.get("publisher", "Yahoo"), "cat": "mercati",
                     "title": title, "summary": "", "url": n.get("link", "")})
        except Exception:
            pass
    news.sort(key=lambda x: x.get("date") or "", reverse=True)
    news = news[:max_h]
    by_cat = {}
    for n in news: by_cat[n.get("cat", "")] = by_cat.get(n.get("cat", ""), 0) + 1
    print(f"[news] totale {len(news)} titoli | per categoria: {by_cat}")
    return news

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

    # --- fondamentali best-effort (PE, div yield) ---
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

    # --- notizie ---
    news = gather_news(cfg, yf, today)

    packet = {"as_of": today, "generated": dt.datetime.utcnow().isoformat(),
              "macro": macro, "instruments": instruments, "news": news}
    path = ac.state_path(cfg, "packets", f"packet_{today}.json")
    ac.write_json(path, packet)
    ac.write_json(ac.state_path(cfg, "packets", "packet_latest.json"), packet)
    print(f"[packet] {len(instruments)} strumenti, {len(news)} notizie -> {path}")
    return packet

if __name__ == "__main__":
    build(ac.load_config())
