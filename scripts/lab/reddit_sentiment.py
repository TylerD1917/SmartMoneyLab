"""
Lab — Reddit Retail Sentiment (r/wallstreetbets).
Pipeline: unisce ApeWisdom (menzioni/upvote/crescita) + Tradestie (sentiment/commenti),
calcola un "Reddit Sentiment Score" composito, seleziona i top 5 (equipesati) e ne
traccia il valore vs S&P 500. Scrive public/tools/reddit-sentiment.json.

Cadenza: gira OGNI SETTIMANA. Ogni run aggiorna il VALORE del portafoglio (prezzi).
La SELEZIONE (squadra del mese) cambia solo al PRIMO run di un mese nuovo, quando
si rifà il fetch del sentiment e si ribilancia. Così: valore settimanale, squadra mensile.

Solo dati pubblici gratuiti senza chiave (ApeWisdom/Tradestie). Forward-only.
  python scripts/lab/reddit_sentiment.py            # produzione (runner)
  python scripts/lab/reddit_sentiment.py --dry-run  # test offline
"""
import os, json, argparse, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
OUT = os.path.join(ROOT, "public", "tools", "reddit-sentiment.json")
SUBREDDIT = "wallstreetbets"
BENCH_TICKER = "^GSPC"; BENCH_NAME = "S&P 500"
TOP_N = 5
MIN_MENTIONS = 10
WEIGHTS = {"sentiment": 0.30, "mentions": 0.25, "comments": 0.20, "growth": 0.15, "upvotes": 0.10}
ETF_TICKERS = {"SPY","QQQ","VOO","IVV","IWM","DIA","GLD","SLV","TLT","USO","UNG","XLE","XLF","XLK",
    "SOXL","SOXS","TQQQ","SQQQ","SPXL","SPXS","UVXY","VIX","SMH","SOXX","ARKK","VTI","SCHD","WEAT","CANE"}
ETF_NAME_HINTS = ("etf","fund","trust","shares","proshares","direxion","vaneck","ishares","spdr","invesco")

DRY_APE = {"NVDA":{"name":"NVIDIA","mentions":225,"upvotes":476,"mentions_24h_ago":82},
    "AVGO":{"name":"Broadcom","mentions":641,"upvotes":2602,"mentions_24h_ago":76},
    "PLTR":{"name":"Palantir","mentions":44,"upvotes":89,"mentions_24h_ago":20},
    "ASTS":{"name":"AST SpaceMobile","mentions":71,"upvotes":147,"mentions_24h_ago":62},
    "HOOD":{"name":"Robinhood","mentions":30,"upvotes":120,"mentions_24h_ago":11},
    "SOFI":{"name":"SoFi","mentions":25,"upvotes":90,"mentions_24h_ago":16},
    "TSLA":{"name":"Tesla","mentions":30,"upvotes":43,"mentions_24h_ago":21},
    "SPY":{"name":"SPDR S&P 500 ETF Trust","mentions":241,"upvotes":688,"mentions_24h_ago":337}}
DRY_TRAD = {"NVDA":{"sentiment_score":0.28,"no_of_comments":90,"sentiment":"Bullish"},
    "AVGO":{"sentiment_score":0.15,"no_of_comments":40,"sentiment":"Bullish"},
    "PLTR":{"sentiment_score":0.55,"no_of_comments":60,"sentiment":"Bullish"},
    "ASTS":{"sentiment_score":0.40,"no_of_comments":35,"sentiment":"Bullish"},
    "HOOD":{"sentiment_score":0.33,"no_of_comments":50,"sentiment":"Bullish"},
    "SOFI":{"sentiment_score":0.60,"no_of_comments":25,"sentiment":"Bullish"},
    "TSLA":{"sentiment_score":-0.10,"no_of_comments":80,"sentiment":"Bearish"},
    "SPY":{"sentiment_score":0.05,"no_of_comments":70,"sentiment":"Bullish"}}

# ---------------------------------------------------------------- FETCH
def fetch_apewisdom(pages=2):
    import urllib.request
    out = {}
    for pg in range(1, pages + 1):
        url = f"https://apewisdom.io/api/v1.0/filter/{SUBREDDIT}/page/{pg}"
        req = urllib.request.Request(url, headers={"User-Agent": "smartmoneylab-lab/1.0"})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        for r in data.get("results", []):
            out[r["ticker"]] = {"name": r.get("name", r["ticker"]),
                "mentions": int(r.get("mentions") or 0), "upvotes": int(r.get("upvotes") or 0),
                "mentions_24h_ago": (int(r["mentions_24h_ago"]) if r.get("mentions_24h_ago") else None)}
    return out

def fetch_tradestie():
    import urllib.request
    req = urllib.request.Request("https://tradestie.com/api/v1/apps/reddit",
                                 headers={"User-Agent": "Mozilla/5.0 smartmoneylab-lab/1.0"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    return {r["ticker"]: {"sentiment_score": float(r.get("sentiment_score") or 0),
            "no_of_comments": int(r.get("no_of_comments") or 0), "sentiment": r.get("sentiment", "")} for r in data}

# ---------------------------------------------------------------- COMMENTO KIMI
def kimi_comment(month_closed, port_ret, bench_ret, kept, added, removed):
    """Genera un commento breve (2-3 frasi) sul mese appena chiuso via Kimi API.
    Ritorna None se manca la chiave o in caso di errore (il sito funziona comunque)."""
    key = os.environ.get("KIMI_API_KEY")
    if not key:
        return None
    import urllib.request
    base = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.ai/v1").rstrip("/")
    model = os.environ.get("KIMI_MODEL", "moonshot-v1-8k")
    diff = (port_ret - bench_ret)
    verdetto = "ha battuto" if diff > 0 else ("ha perso contro" if diff < 0 else "ha pareggiato con")
    prompt = (
        "Sei l'autore di SmartMoneyLab, blog italiano di finanza personale e analisi quantitativa. "
        "Tono sobrio, serio, niente hype, niente consigli operativi, italiano. Scrivi un commento di 2-3 frasi "
        "(max ~55 parole) sul mese appena concluso di un esperimento: un portafoglio equipesato dei 5 titoli col "
        "sentiment più alto su r/wallstreetbets, confrontato con l'S&P 500.\n\n"
        f"Dati del mese {month_closed}:\n"
        f"- rendimento portafoglio: {port_ret*100:+.1f}%\n"
        f"- rendimento S&P 500: {bench_ret*100:+.1f}% (il portafoglio {verdetto} l'indice per {abs(diff)*100:.1f} punti)\n"
        f"- titoli confermati: {', '.join(kept) or 'nessuno'}\n"
        f"- nuovi ingressi questo mese: {', '.join(added) or 'nessuno'}\n"
        f"- usciti: {', '.join(removed) or 'nessuno'}\n\n"
        "Commenta cosa è cambiato nella squadra e come è andata, senza dare raccomandazioni. Rispondi solo col commento."
    )
    body = json.dumps({"model": model, "temperature": 0.4,
        "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request(base + "/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=60))
        return res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[kimi] commento non generato: {e}")
        return None

# ---------------------------------------------------------------- SCORE
def is_etf(ticker, name):
    if ticker in ETF_TICKERS: return True
    n = (name or "").lower()
    return any(h in n for h in ETF_NAME_HINTS)

def build_ranking(ape, trad, prev_mentions):
    rows = []
    for tk, a in ape.items():
        t = trad.get(tk)
        if t is None or is_etf(tk, a["name"]) or a["mentions"] < MIN_MENTIONS:
            continue
        base = prev_mentions.get(tk) if prev_mentions else None
        if base and base > 0: growth = a["mentions"] / base - 1
        elif a["mentions_24h_ago"]: growth = a["mentions"] / a["mentions_24h_ago"] - 1
        else: growth = 0.0
        rows.append({"ticker": tk, "name": a["name"], "mentions": a["mentions"], "upvotes": max(a["upvotes"], 0),
            "comments": t["no_of_comments"], "sentiment_score": t["sentiment_score"], "growth": growth})
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df[df["sentiment_score"] > 0].copy()          # gate: solo bullish
    if df.empty: return df
    for k, col in {"sentiment":"sentiment_score","mentions":"mentions","comments":"comments",
                   "growth":"growth","upvotes":"upvotes"}.items():
        df[f"pct_{k}"] = df[col].rank(pct=True)
    df["score"] = sum(WEIGHTS[k] * df[f"pct_{k}"] for k in WEIGHTS)
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df

def ranking_json(rk):
    out = []
    for _, r in rk.head(10).iterrows():
        out.append({"rank": int(r["rank"]), "ticker": r["ticker"], "name": r["name"],
            "score": round(float(r["score"]), 3), "sentiment_score": round(float(r["sentiment_score"]), 2),
            "mentions": int(r["mentions"]), "comments": int(r["comments"]),
            "growth": round(float(r["growth"]), 3), "upvotes": int(r["upvotes"]),
            "components": {k: round(float(r[f"pct_{k}"]), 2) for k in WEIGHTS}})
    return out

# ---------------------------------------------------------------- PREZZI
def get_prices(tickers, dry_run):
    if dry_run:
        rng = np.random.default_rng(abs(hash(tuple(sorted(tickers)))) % (2**32))
        return {tk: float(50 + rng.uniform(-8, 8)) for tk in tickers}
    import yfinance as yf
    px = {}
    for tk in tickers:
        try:
            h = yf.Ticker(tk).history(period="5d")
            if len(h): px[tk] = float(h["Close"].iloc[-1])
        except Exception: pass
    return px

# ---------------------------------------------------------------- MAIN
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); args = ap.parse_args()
    today = dt.date.today().isoformat(); ym = today[:7]

    prev = json.load(open(OUT)) if os.path.exists(OUT) else {}
    port = prev.get("portfolio", {})
    prev_holdings = port.get("holdings", [])
    navreb = port.get("nav_at_rebalance", {"port": 100.0, "bench": 100.0})
    bench_basis = port.get("bench_basis")
    nav = port.get("nav", [])
    history = port.get("history", [])
    last_month = port.get("last_rebalance_month")
    prev_snap = prev.get("_mentions_snapshot", {})
    prev_navreb = dict(navreb)                         # NAV di partenza del periodo che si sta chiudendo
    prev_tickers = [h["ticker"] for h in prev_holdings]
    commento = prev.get("commento")                    # si aggiorna solo al ribilancio

    is_rebalance = (not prev_holdings) or (last_month != ym)

    ranking = None; snap = prev_snap
    new_tickers = [h["ticker"] for h in prev_holdings]
    if is_rebalance:
        ape, trad = (DRY_APE, DRY_TRAD) if args.dry_run else (fetch_apewisdom(), fetch_tradestie())
        rk = build_ranking(ape, trad, prev_snap)
        if rk.empty: raise SystemExit("Nessun ticker eleggibile.")
        new_tickers = list(rk.head(TOP_N)["ticker"])
        ranking = ranking_json(rk)
        snap = {tk: ape[tk]["mentions"] for tk in ape}

    # prezzi correnti (holding attuali + nuovi + benchmark)
    need = sorted(set(new_tickers) | {h["ticker"] for h in prev_holdings} | {BENCH_TICKER})
    prices = get_prices(need, args.dry_run)

    # valore corrente dai holding ATTUALI (prev), dalla base dell'ultimo ribilancio
    if prev_holdings and bench_basis:
        r = sum(h["weight"] * (prices[h["ticker"]] / h["basis_price"] - 1)
                for h in prev_holdings if prices.get(h["ticker"]) and h.get("basis_price"))
        bnow = prices.get(BENCH_TICKER); br = (bnow / bench_basis - 1) if bnow else 0.0
        cur_port = navreb["port"] * (1 + r); cur_bench = navreb["bench"] * (1 + br)
    else:
        cur_port, cur_bench = 100.0, 100.0

    # punto NAV (sostituisci se già presente per oggi)
    pt = {"d": today, "port": round(cur_port, 2), "bench": round(cur_bench, 2)}
    if nav and nav[-1]["d"] == today: nav[-1] = pt
    else: nav.append(pt)

    if is_rebalance:
        navreb = {"port": round(cur_port, 2), "bench": round(cur_bench, 2)}
        w = round(1.0 / TOP_N, 4)
        holdings = [{"ticker": tk, "weight": w, "basis_price": prices.get(tk)} for tk in new_tickers]
        bench_basis = prices.get(BENCH_TICKER)
        last_month = ym
        if not history or history[-1]["month"] != ym:
            history.append({"month": ym, "tickers": new_tickers})
        current = {"as_of": today, "selection": new_tickers, "ranking": ranking}
        # commento sul mese appena chiuso (solo se c'era già un periodo precedente)
        if prev_tickers and port.get("last_rebalance_month") and prev_navreb.get("port"):
            p_ret = cur_port / prev_navreb["port"] - 1
            b_ret = cur_bench / prev_navreb["bench"] - 1 if prev_navreb.get("bench") else 0.0
            prev_set, new_set = set(prev_tickers), set(new_tickers)
            c = kimi_comment(port.get("last_rebalance_month"), p_ret, b_ret,
                             [t for t in new_tickers if t in prev_set],
                             [t for t in new_tickers if t not in prev_set],
                             [t for t in prev_tickers if t not in new_set])
            if c:
                commento = c
    else:
        holdings = prev_holdings
        current = prev.get("current", {"as_of": today, "selection": new_tickers, "ranking": []})

    out = {"updated": today, "subreddit": SUBREDDIT, "currency": "USD", "benchmark": BENCH_NAME,
        "weighting": "equipesato (20% ciascuno)", "sources": ["ApeWisdom", "Tradestie"],
        "current": current,
        "commento": commento,
        "portfolio": {"holdings": holdings, "bench_basis": bench_basis, "nav_at_rebalance": navreb,
                      "last_rebalance_month": last_month, "nav": nav, "history": history},
        "_mentions_snapshot": snap}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"[{'RIBILANCIO' if is_rebalance else 'valore'}] {today}  port {cur_port:.2f}  bench {cur_bench:.2f}  "
          f"squadra {new_tickers}  (NAV punti: {len(nav)})")
    return out

if __name__ == "__main__":
    main()
