#!/usr/bin/env python3
"""Applica le decisioni al prezzo del pacchetto, addebita i costi, aggiorna i portafogli e la NAV.
Include il portafoglio di controllo CASUALE (stessi costi) come misura della fortuna."""
import os, sys, json, random, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac
import nav_daily as nd

def random_decision(universe_meta, prices, n, cfg, seed):
    rng = random.Random(seed)
    pool = [t for t in universe_meta if prices.get(t)]
    picks = rng.sample(pool, min(n, len(pool)))
    w = cfg["gross_exposure_cap"] / len(picks)
    return {"rationale": "controllo casuale", "orders":
            [{"ticker": t, "action": "open",
              "side": rng.choice(["long", "short"]), "target_weight": round(w, 4)} for t in picks]}

def settle(cfg):
    meta, universe = ac.load_universe(cfg)
    packet = ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json"))
    if not packet: sys.exit("Nessun packet_latest.json")
    prices = {i["ticker"]: i.get("price") for i in packet["instruments"]}
    today = packet["as_of"]; mark_days = cfg["cadence"]["mark_days"]

    participants = [m["id"] for m in cfg["models"]]
    if cfg.get("random_control"): participants.append("random")

    for mid in participants:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json")) or ac.portfolio_new(cfg, mid)
        if mid == "random":
            decision = random_decision(meta, prices, cfg["max_positions"], cfg, seed=today)
        else:
            decision = ac.read_json(ac.state_path(cfg, "decisions", f"decision_{mid}_{today}.json")) \
                       or {"orders": []}
        ok, log = ac.apply_decision(pf, decision, prices, universe, cfg)
        # Il costo di prestito NON si addebita qui: nav_daily lo accumula pro-rata
        # die. Addebitare 7 giorni nel momento in cui la posizione viene aperta
        # significherebbe pagare interessi su giorni non ancora trascorsi.
        fee = 0.0
        nav = ac.equity(pf, prices)
        pf["history"].append({"date": today, "action": "settle", "ok": ok,
                              "n_orders": len(decision.get("orders", [])), "borrow_fee": round(fee, 2),
                              "nav": round(nav, 2), "log": log})
        ac.write_json(ac.state_path(cfg, f"portfolio_{mid}.json"), pf)
        ac.append_nav(cfg, mid, today, nav)
        # Snapshot del segmento: fotografa cassa e quantita' subito dopo l'esecuzione.
        # E' cio' che permette di ricostruire il NAV giornaliero anche mesi dopo,
        # quando le posizioni saranno state sostituite piu' volte.
        nd.write_snapshot(cfg, mid, today, pf)
        print(f"[settle] {mid}: ok={ok} nav={nav:.0f} {'; '.join(log) if log else ''}")

if __name__ == "__main__":
    settle(ac.load_config())
