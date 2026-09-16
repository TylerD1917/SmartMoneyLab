#!/usr/bin/env python3
"""Scrive i JSON pubblici per la sezione /lab (classifica, posizioni, NAV, decisioni)."""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

def publish(cfg):
    meta, _ = ac.load_universe(cfg)
    packet = ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json")) or {"instruments": [], "as_of": None}
    prices = {i["ticker"]: i.get("price") for i in packet["instruments"]}
    as_of = packet.get("as_of")
    outdir = os.path.join(cfg["_root"], cfg["public_dir"])
    os.makedirs(outdir, exist_ok=True)

    models = [m["id"] for m in cfg["models"]]
    parts = models + (["random"] if cfg.get("random_control") else []) + list(cfg["benchmarks"].keys())

    nav_all = {p: ac.read_nav(cfg, p) for p in parts}
    board = []
    for p in parts:
        m = ac.metrics_from_nav(nav_all[p])
        last = nav_all[p][-1][1] if nav_all[p] else cfg["capital"]
        board.append({"id": p, "type": ("model" if p in models else ("control" if p == "random" else "benchmark")),
                      "nav": round(last, 2), **m})
    board.sort(key=lambda r: (r["ret_total"] if r["ret_total"] is not None else -9), reverse=True)

    positions = {}
    decisions = {}
    for mid in models:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json"))
        if pf:
            E = ac.equity(pf, prices)
            positions[mid] = {"cash": round(pf["cash"], 2), "equity": round(E, 2),
                "positions": [{"ticker": t, "qty": round(v["qty"], 2),
                    "px": prices.get(t), "weight": round(v["qty"]*prices.get(t, 0)/E, 4) if E else 0,
                    "side": "long" if v["qty"] > 0 else "short"} for t, v in pf["positions"].items()]}
        if as_of:
            d = ac.read_json(ac.state_path(cfg, "decisions", f"decision_{mid}_{as_of}.json"))
            if d: decisions[mid] = {"rationale": d.get("rationale", ""), "orders": d.get("orders", [])}

    ac.write_json(os.path.join(outdir, "arena.json"), {
        "as_of": as_of, "updated": dt.datetime.utcnow().isoformat(),
        "rules": {"capital": cfg["capital"], "max_positions": cfg["max_positions"],
                  "gross_cap": cfg["gross_exposure_cap"], "cadence_days": cfg["cadence"]["decision_days"],
                  "costs": cfg["costs"], "benchmarks": list(cfg["benchmarks"].keys())},
        "leaderboard": board, "positions": positions, "decisions": decisions,
        "nav": {p: nav_all[p] for p in parts},
        "disclaimer": "Esperimento tra modelli, non consulenza finanziaria. Il vincitore a breve termine è in gran parte fortuna."})
    print(f"[publish] arena.json -> {outdir} | classifica: " +
          ", ".join(f"{r['id']} {r['ret_total']}" for r in board))

if __name__ == "__main__":
    publish(ac.load_config())
