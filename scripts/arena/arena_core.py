#!/usr/bin/env python3
"""Core condiviso dell'AI Investing Arena: config, ledger, costi, vincoli, metriche, dati."""
import os, json, math, datetime as dt

EPS = 1e-6

# ---------------- paths & io ----------------
def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", ".."))

def load_config(root=None):
    root = root or repo_root()
    cfg = json.load(open(os.path.join(root, "scripts", "arena", "config.json")))
    cfg["_root"] = root
    return cfg

def load_universe(cfg):
    u = json.load(open(os.path.join(cfg["_root"], cfg["universe_file"])))
    meta = {i["ticker"]: i for i in u["instruments"]}
    return meta, set(meta)

def state_path(cfg, *parts):
    p = os.path.join(cfg["_root"], cfg["state_dir"], *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p

def read_json(path, default=None):
    return json.load(open(path)) if os.path.exists(path) else default

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), ensure_ascii=False, indent=1)

# ---------------- portfolio ----------------
def portfolio_new(cfg, model_id):
    return {"model": model_id, "cash": float(cfg["capital"]),
            "positions": {}, "history": [],
            "created": dt.date.today().isoformat()}

def equity(pf, prices):
    """Valore totale = cash + Σ qty*prezzo (short = qty negativa)."""
    v = pf["cash"]
    for t, pos in pf["positions"].items():
        p = prices.get(t)
        if p: v += pos["qty"] * p
    return v

def gross_exposure(pf, prices):
    g = 0.0
    for t, pos in pf["positions"].items():
        p = prices.get(t)
        if p: g += abs(pos["qty"] * p)
    return g

def _trade(pf, t, delta_qty, price, cost_rate):
    """Esegue un delta di quantità (signed) a 'price' con costo su nozionale."""
    if abs(delta_qty) < EPS or not price:
        return
    notional = delta_qty * price
    pf["cash"] -= notional                      # compri: cash giù; vendi/short: cash su
    pf["cash"] -= abs(notional) * cost_rate      # costo (commissione+spread)
    pos = pf["positions"].get(t, {"qty": 0.0, "avg_price": price})
    old_qty = pos["qty"]; new_qty = old_qty + delta_qty
    # avg_price: media pesata se si aumenta nella stessa direzione, altrimenti reset
    if old_qty == 0 or (old_qty > 0) == (delta_qty > 0):
        denom = abs(new_qty) if abs(new_qty) > EPS else 1.0
        pos["avg_price"] = (abs(old_qty) * pos.get("avg_price", price) + abs(delta_qty) * price) / (abs(old_qty) + abs(delta_qty)) if (abs(old_qty)+abs(delta_qty))>EPS else price
    else:
        if abs(delta_qty) > abs(old_qty):        # flip di direzione
            pos["avg_price"] = price
    pos["qty"] = new_qty
    if abs(new_qty) < EPS:
        pf["positions"].pop(t, None)
    else:
        pf["positions"][t] = pos

def apply_decision(pf, decision, prices, universe, cfg):
    """Applica gli ordini (target_weight) con validazione vincoli. Ritorna (ok, log[])."""
    log = []
    costs = cfg["costs"]; cost_rate = costs["commission"] + costs["spread"]
    E = equity(pf, prices)
    if E <= 0:
        return False, ["equity <= 0, salto"]
    # 1) desired qty map: parte dalle posizioni correnti
    desired = {t: pos["qty"] for t, pos in pf["positions"].items()}
    for o in decision.get("orders", []):
        t = o.get("ticker"); side = o.get("side", "long"); w = o.get("target_weight", 0.0)
        action = o.get("action", "open")
        if t not in universe:
            log.append(f"scartato {t}: fuori universo"); continue
        if side not in ("long", "short"):
            log.append(f"scartato {t}: side non valido"); continue
        p = prices.get(t)
        if not p:
            log.append(f"scartato {t}: prezzo mancante"); continue
        if action == "close" or w <= 0:
            desired[t] = 0.0; continue
        if w > 1.0:
            log.append(f"{t}: target_weight {w}>1 clampato a 1"); w = 1.0
        sign = 1.0 if side == "long" else -1.0
        desired[t] = sign * w * E / p
    # 2) vincolo numero posizioni
    open_cnt = sum(1 for q in desired.values() if abs(q) > EPS)
    if open_cnt > cfg["max_positions"]:
        return False, log + [f"RIFIUTATA: {open_cnt} posizioni > max {cfg['max_positions']} (portafoglio invariato)"]
    # 3) vincolo esposizione lorda (scala se necessario)
    gross = sum(abs(q * prices[t]) for t, q in desired.items() if prices.get(t))
    cap = cfg["gross_exposure_cap"] * E
    if gross > cap + EPS and gross > 0:
        f = cap / gross
        desired = {t: q * f for t, q in desired.items()}
        log.append(f"esposizione lorda {gross:.0f}>cap {cap:.0f}: scalata di {f:.3f}")
    # 4) esegui i delta
    for t, target_q in desired.items():
        cur = pf["positions"].get(t, {"qty": 0.0})["qty"]
        _trade(pf, t, target_q - cur, prices.get(t), cost_rate)
    return True, log

def charge_borrow(pf, prices, cfg, days):
    """Addebita il costo di prestito sugli short, pro-rata sui giorni."""
    rate = cfg["costs"]["short_borrow_annual"] * days / 365.0
    fee = 0.0
    for t, pos in pf["positions"].items():
        p = prices.get(t)
        if p and pos["qty"] < 0:
            fee += abs(pos["qty"] * p) * rate
    pf["cash"] -= fee
    return fee

# ---------------- NAV series ----------------
def nav_file(cfg, key):
    return state_path(cfg, "nav", f"{key}.csv")

def append_nav(cfg, key, date, nav):
    path = nav_file(cfg, key)
    lines = []
    if os.path.exists(path):
        lines = [l for l in open(path).read().splitlines() if l and not l.startswith("date")]
    lines = [l for l in lines if not l.startswith(date + ",")]   # niente doppioni stessa data
    lines.append(f"{date},{round(float(nav), 2)}")
    with open(path, "w") as f:
        f.write("date,nav\n" + "\n".join(lines) + "\n")

def read_nav(cfg, key):
    path = nav_file(cfg, key)
    if not os.path.exists(path): return []
    out = []
    for l in open(path).read().splitlines():
        if not l or l.startswith("date"): continue
        d, v = l.split(","); out.append((d, float(v)))
    return out

# ---------------- metriche ----------------
def metrics_from_nav(nav_series):
    """nav_series: lista di (date_str, nav). Ritorna dict metriche (settimanale)."""
    vals = [v for _, v in nav_series]
    if len(vals) < 2:
        return {"ret_total": 0.0, "vol_ann": None, "max_dd": 0.0, "sharpe": None}
    rets = [vals[i] / vals[i-1] - 1 for i in range(1, len(vals)) if vals[i-1] > 0]
    ret_total = vals[-1] / vals[0] - 1
    peak = vals[0]; mdd = 0.0
    for v in vals:
        peak = max(peak, v); mdd = min(mdd, v/peak - 1)
    vol = None; sharpe = None
    if len(rets) >= 2:
        mean = sum(rets)/len(rets)
        var = sum((r-mean)**2 for r in rets)/(len(rets)-1)
        sd = math.sqrt(var)
        vol = sd * math.sqrt(52)                      # annualizzata (dati settimanali)
        sharpe = (mean*52)/vol if vol > 0 else None
    return {"ret_total": round(ret_total,4),
            "vol_ann": round(vol,4) if vol is not None else None,
            "max_dd": round(mdd,4),
            "sharpe": round(sharpe,3) if sharpe is not None else None}

# ---------------- dati (yfinance, gira su Action) ----------------
def yf_prices(tickers):
    """Ultimo prezzo di chiusura per una lista di ticker. {ticker: price}."""
    import yfinance as yf
    out = {}
    data = yf.download(list(tickers), period="5d", interval="1d",
                       auto_adjust=True, progress=False, threads=True)
    close = data["Close"] if "Close" in data else data
    for t in tickers:
        try:
            s = close[t].dropna() if hasattr(close, "columns") and t in close.columns else close.dropna()
            if len(s): out[t] = float(s.iloc[-1])
        except Exception:
            pass
    return out
