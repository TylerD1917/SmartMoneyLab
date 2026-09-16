#!/usr/bin/env python3
"""Mark-to-market settimanale (settimane senza decisione): prezzi live, costo prestito, NAV.
Aggiorna anche i benchmark (ACWI, S&P 500) normalizzati al capitale iniziale."""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

def mark(cfg):
    meta, _ = ac.load_universe(cfg)
    today = dt.date.today().isoformat()
    mark_days = cfg["cadence"]["mark_days"]
    participants = [m["id"] for m in cfg["models"]] + (["random"] if cfg.get("random_control") else [])

    held = set()
    pfs = {}
    for mid in participants:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json"))
        if pf: pfs[mid] = pf; held |= set(pf["positions"].keys())

    bench = cfg["benchmarks"]
    prices = ac.yf_prices(held | set(bench.values()))

    for mid, pf in pfs.items():
        ac.charge_borrow(pf, prices, cfg, mark_days)
        nav = ac.equity(pf, prices)
        pf["history"].append({"date": today, "action": "mark", "nav": round(nav, 2)})
        ac.write_json(ac.state_path(cfg, f"portfolio_{mid}.json"), pf)
        ac.append_nav(cfg, mid, today, nav)
        print(f"[mark] {mid}: nav={nav:.0f}")

    # benchmark
    base = ac.read_json(ac.state_path(cfg, "benchmark_baseline.json"))
    if not base:
        base = {"capital": cfg["capital"], "prices": {k: prices.get(v) for k, v in bench.items()}}
        ac.write_json(ac.state_path(cfg, "benchmark_baseline.json"), base)
    for k, tk in bench.items():
        p = prices.get(tk); p0 = base["prices"].get(k)
        if p and p0:
            ac.append_nav(cfg, k, today, base["capital"] * p / p0)
            print(f"[mark] bench {k}: {base['capital']*p/p0:.0f}")

if __name__ == "__main__":
    mark(ac.load_config())
