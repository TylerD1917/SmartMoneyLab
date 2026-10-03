#!/usr/bin/env python3
"""Scrive i JSON pubblici per la sezione /lab (classifica, posizioni, NAV, decisioni)."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import arena_core as ac
import nav_thin

def publish(cfg):
    meta, _ = ac.load_universe(cfg)
    packet = ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json")) or {"instruments": [], "as_of": None}
    prices = {i["ticker"]: i.get("price") for i in packet["instruments"]}
    as_of = packet.get("as_of")
    outdir = os.path.join(cfg["_root"], cfg["public_dir"])
    os.makedirs(outdir, exist_ok=True)

    models = [m["id"] for m in cfg["models"]]
    parts = models + (["random"] if cfg.get("random_control") else []) + list(cfg["benchmarks"].keys())

    nav_all = {p: ac.read_nav(cfg, p) for p in parts}   # giornaliero, completo

    # date delle riallocazioni: vanno conservate nel grafico ridotto
    tieni = set()
    for mid in models:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json")) or {}
        tieni |= {h["date"] for h in pf.get("history", []) if h.get("action") == "settle"}
    board = []
    for p in parts:
        m = ac.metrics_from_nav(nav_all[p])
        last = nav_all[p][-1][1] if nav_all[p] else cfg["capital"]
        m["ret_total"] = round(last / cfg["capital"] - 1, 4)   # rendimento dal capitale iniziale
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
                    "side": "long" if v["qty"] > 0 else "short",
                    "name": meta.get(t, {}).get("name", "")} for t, v in pf["positions"].items()]}
        if as_of:
            d = ac.read_json(ac.state_path(cfg, "decisions", f"decision_{mid}_{as_of}.json"))
            if d:
                decisions[mid] = {"rationale": d.get("rationale", ""),
                    "orders": [dict(o, name=meta.get(o.get("ticker"), {}).get("name", "")) for o in d.get("orders", []) if isinstance(o, dict)]}
                # Esito del controllo di coerenza, se presente: la decisione viene
                # sempre eseguita come il modello l'ha scritta, ma se resta
                # contraddittoria dopo la ri-domanda il flag e' pubblico.
                c = d.get("coherence") or {}
                dopo = c.get("dopo") or {}
                if dopo.get("severity") in ("hard", "soft"):
                    decisions[mid]["coherence"] = {
                        "severity": dopo.get("severity"),
                        "ri_domanda": bool(c.get("ri_domanda")),
                        "flags": [{"ticker": f.get("ticker"), "check": f.get("check"),
                                   "severity": f.get("severity"), "detail": f.get("detail")}
                                  for f in dopo.get("flags", [])]}

    ac.write_json(os.path.join(outdir, "arena.json"), {
        "as_of": as_of, "updated": dt.datetime.utcnow().isoformat(),
        "rules": {"capital": cfg["capital"], "max_positions": cfg["max_positions"],
                  "gross_cap": cfg["gross_exposure_cap"], "cadence_days": cfg["cadence"]["decision_days"],
                  "costs": cfg["costs"], "benchmarks": list(cfg["benchmarks"].keys())},
        "leaderboard": board, "positions": positions, "decisions": decisions,
        # Il grafico riceve la serie ridotta (vedi scripts/nav_thin.py); le metriche
        # in leaderboard sono gia' state calcolate sulla serie giornaliera completa,
        # che resta scaricabile in CSV.
        "nav": {p: nav_thin.thin_pairs(nav_all[p], tieni=tieni) for p in parts},
        "nav_risoluzione": (f"giornaliera negli ultimi {nav_thin.GIORNI_PIENI} giorni, "
                            f"poi settimanale e, oltre {nav_thin.ANNI_SETTIMANALI} anni, mensile"),
        "nav_csv": "/tools/arena/nav_daily.csv",
        "disclaimer": "Esperimento tra modelli, non consulenza finanziaria. Il vincitore a breve termine è in gran parte fortuna."})
    # serie giornaliera completa scaricabile: il grafico e' ridotto, il dato pieno no
    tutte = sorted({d for ser in nav_all.values() for d, _ in ser})
    idx = {p: dict(nav_all[p]) for p in parts}
    with open(os.path.join(outdir, "nav_daily.csv"), "w", encoding="utf-8") as f:
        f.write("date," + ",".join(parts) + "\n")
        for d in tutte:
            f.write(d + "," + ",".join(("" if idx[p].get(d) is None else f"{idx[p][d]:.2f}")
                                       for p in parts) + "\n")

    # Controllo di codifica: i rationale dei modelli sono in italiano e il browser
    # legge questo JSON come UTF-8. Se qualcuno lo riscrive con la codifica di
    # sistema (su Windows cp1252) la pagina /lab si rompe in silenzio.
    try:
        json.load(open(os.path.join(outdir, "arena.json"), encoding="utf-8"))
    except UnicodeDecodeError as e:
        sys.exit(f"[publish] arena.json non e' UTF-8 valido: {e}")

    print(f"[publish] arena.json -> {outdir} | classifica: " +
          ", ".join(f"{r['id']} {r['ret_total']}" for r in board))

if __name__ == "__main__":
    publish(ac.load_config())
