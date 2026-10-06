#!/usr/bin/env python3
"""Scrive i JSON pubblici della sezione /lab (classifica, posizioni, NAV, decisioni).

Due regole, imparate dal guasto del 2026-10-06, quando la pagina ha pubblicato
tutti i modelli a 100.000 e +0,00% senza che niente segnalasse un errore:

  1. NON SI PUBBLICA UNA STORIA PIU' CORTA DI QUELLA GIA' ONLINE. Se una serie
     arriva vuota, o parte piu' tardi, o ha meno giorni di quella pubblicata,
     publish si ferma con un errore invece di sovrascrivere. La Action fallisce,
     il sito resta all'ultima versione buona e l'errore si vede.

  2. OGNI POSIZIONE HA LA SUA SPIEGAZIONE, anche se in questo periodo il modello
     non l'ha toccata. Prima la pagina mostrava solo gli ordini del periodo:
     alla prima allocazione coincidevano con il portafoglio, dalla seconda in
     poi le posizioni lasciate ferme restavano senza un perche'. La tesi viene
     riportata avanti dalla decisione in cui era stata scritta.
"""
import os
import sys
import json
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
import arena_core as ac
import nav_thin


# ---------------------------------------------------------------- tesi storiche
def storico_tesi(cfg, mid):
    """{ticker: {thesis, date, action, side}} dalla decisione piu' recente che
    ha parlato di quel ticker. Le decisioni si leggono in ordine di data, cosi'
    una tesi nuova sostituisce quella vecchia e una posizione mai piu' toccata
    conserva la motivazione con cui era stata aperta."""
    d = os.path.join(cfg["_root"], cfg["state_dir"], "decisions")
    if not os.path.isdir(d):
        return {}
    pre, out = f"decision_{mid}_", {}
    for fn in sorted(os.listdir(d)):          # nome = ..._YYYY-MM-DD.json -> ordine cronologico
        if not (fn.startswith(pre) and fn.endswith(".json")):
            continue
        dec = ac.read_json(os.path.join(d, fn)) or {}
        quando = dec.get("as_of") or fn[len(pre):-5]
        for o in dec.get("orders", []):
            if isinstance(o, dict) and o.get("ticker"):
                out[o["ticker"]] = {"thesis": o.get("thesis", ""), "date": quando,
                                    "action": o.get("action"), "side": o.get("side")}
    return out


# ---------------------------------------------------------------- guardrail
def _serie_pubblicata(outdir, parts):
    """Serie gia' online, lette dal CSV completo: {id: [date...]}"""
    path = os.path.join(outdir, "nav_daily.csv")
    if not os.path.exists(path):
        return {}
    righe = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    if len(righe) < 2:
        return {}
    cols = righe[0].split(",")
    out = {p: [] for p in parts if p in cols}
    for l in righe[1:]:
        c = l.split(",")
        for p in out:
            if c[cols.index(p)]:
                out[p].append(c[0])
    return out


def verifica_regressioni(nav_all, outdir, parts):
    """Si ferma se la nuova pubblicazione perderebbe storia."""
    problemi = []
    for p in parts:
        if not nav_all.get(p):
            problemi.append(f"{p}: serie VUOTA")
    vecchie = _serie_pubblicata(outdir, parts)
    for p, old in vecchie.items():
        new = [d for d, _ in nav_all.get(p, [])]
        if not old or not new:
            continue
        if new[0] > old[0]:
            problemi.append(f"{p}: ora parte dal {new[0]}, online partiva dal {old[0]}")
        if len(new) < len(old):
            problemi.append(f"{p}: {len(new)} giorni contro i {len(old)} gia' online")
    if problemi:
        sys.exit("[publish] PUBBLICAZIONE ANNULLATA, la storia si accorcerebbe:\n  - "
                 + "\n  - ".join(problemi)
                 + "\n  Gli snapshot in state/positions/ sono la fonte: controlla che "
                   "ci siano tutti e rilancia nav_daily.py.")


# ---------------------------------------------------------------- publish
def publish(cfg):
    meta, _ = ac.load_universe(cfg)
    packet = ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json")) \
        or {"instruments": [], "as_of": None}
    prices = {i["ticker"]: i.get("price") for i in packet["instruments"]}
    as_of = packet.get("as_of")
    outdir = os.path.join(cfg["_root"], cfg["public_dir"])
    os.makedirs(outdir, exist_ok=True)

    models = [m["id"] for m in cfg["models"]]
    parts = models + (["random"] if cfg.get("random_control") else []) + list(cfg["benchmarks"].keys())

    nav_all = {p: ac.read_nav(cfg, p) for p in parts}
    verifica_regressioni(nav_all, outdir, parts)

    tieni = set()                      # le date di riallocazione restano nel grafico ridotto
    for mid in models:
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json")) or {}
        tieni |= {h["date"] for h in pf.get("history", []) if h.get("action") == "settle"}

    board = []
    for p in parts:
        m = ac.metrics_from_nav(nav_all[p])
        last = nav_all[p][-1][1]
        m["ret_total"] = round(last / cfg["capital"] - 1, 4)
        board.append({"id": p,
                      "type": ("model" if p in models else ("control" if p == "random" else "benchmark")),
                      "nav": round(last, 2), **m})
    board.sort(key=lambda r: (r["ret_total"] if r["ret_total"] is not None else -9), reverse=True)

    positions, decisions = {}, {}
    for mid in models:
        tesi = storico_tesi(cfg, mid)
        dec = ac.read_json(ac.state_path(cfg, "decisions", f"decision_{mid}_{as_of}.json")) if as_of else None
        mossi = {o["ticker"] for o in (dec or {}).get("orders", [])
                 if isinstance(o, dict) and o.get("ticker")}

        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json"))
        if pf:
            E = ac.equity(pf, prices)
            righe = []
            for t, v in pf["positions"].items():
                voce = tesi.get(t, {})
                righe.append({
                    "ticker": t, "qty": round(v["qty"], 2), "px": prices.get(t),
                    "weight": round(v["qty"] * prices.get(t, 0) / E, 4) if E else 0,
                    "side": "long" if v["qty"] > 0 else "short",
                    "name": meta.get(t, {}).get("name", ""),
                    # perche' questa posizione e' in portafoglio, anche se il
                    # modello non l'ha toccata in questo periodo
                    "thesis": voce.get("thesis", ""),
                    "dal": voce.get("date"),
                    "mossa": "di questo periodo" if t in mossi else "invariata"})
            positions[mid] = {"cash": round(pf["cash"], 2), "equity": round(E, 2),
                              "positions": righe}

        if dec:
            decisions[mid] = {
                "rationale": dec.get("rationale", ""),
                "orders": [dict(o, name=meta.get(o.get("ticker"), {}).get("name", ""))
                           for o in dec.get("orders", []) if isinstance(o, dict)]}
            # esito del controllo di coerenza: la decisione viene sempre eseguita
            # come il modello l'ha scritta, ma se resta contraddittoria dopo la
            # ri-domanda il flag e' pubblico
            c = dec.get("coherence") or {}
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
        "ultima_sessione": max(d for d, _ in nav_all[parts[0]]),
        "rules": {"capital": cfg["capital"], "max_positions": cfg["max_positions"],
                  "gross_cap": cfg["gross_exposure_cap"],
                  "cadence_days": cfg["cadence"]["decision_days"],
                  "costs": cfg["costs"], "benchmarks": list(cfg["benchmarks"].keys())},
        "leaderboard": board, "positions": positions, "decisions": decisions,
        "nav": {p: nav_thin.thin_pairs(nav_all[p], tieni=tieni) for p in parts},
        "nav_risoluzione": (f"giornaliera negli ultimi {nav_thin.GIORNI_PIENI} giorni, "
                            f"poi settimanale e, oltre {nav_thin.ANNI_SETTIMANALI} anni, mensile"),
        "nav_csv": "/tools/arena/nav_daily.csv",
        "disclaimer": "Esperimento tra modelli, non consulenza finanziaria. "
                      "Il vincitore a breve termine è in gran parte fortuna."})

    tutte = sorted({d for ser in nav_all.values() for d, _ in ser})
    idx = {p: dict(nav_all[p]) for p in parts}
    with open(os.path.join(outdir, "nav_daily.csv"), "w", encoding="utf-8") as f:
        f.write("date," + ",".join(parts) + "\n")
        for d in tutte:
            f.write(d + "," + ",".join(("" if idx[p].get(d) is None else f"{idx[p][d]:.2f}")
                                       for p in parts) + "\n")

    # i rationale sono in italiano e il browser legge questo JSON come UTF-8:
    # se qualcuno lo riscrive con la codifica di sistema la pagina si rompe in silenzio
    try:
        json.load(open(os.path.join(outdir, "arena.json"), encoding="utf-8"))
    except UnicodeDecodeError as e:
        sys.exit(f"[publish] arena.json non e' UTF-8 valido: {e}")

    print(f"[publish] arena.json -> {outdir}\n[publish] classifica: "
          + ", ".join(f"{r['id']} {r['ret_total']:+.2%}" for r in board))


if __name__ == "__main__":
    publish(ac.load_config())
