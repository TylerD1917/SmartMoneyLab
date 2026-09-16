#!/usr/bin/env python3
"""Driver dell'arena.
  python scripts/arena/run_period.py init      # crea i portafogli iniziali
  python scripts/arena/run_period.py decision  # build_packet -> run_agents -> settle -> publish (ogni 2 settimane)
  python scripts/arena/run_period.py weekly     # mark -> publish (settimane senza decisione)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

def main():
    cfg = ac.load_config()
    mode = sys.argv[1] if len(sys.argv) > 1 else "decision"
    if mode == "init":
        for m in cfg["models"] + ([{"id": "random"}] if cfg.get("random_control") else []):
            path = ac.state_path(cfg, f"portfolio_{m['id']}.json")
            if not os.path.exists(path):
                ac.write_json(path, ac.portfolio_new(cfg, m["id"]))
                print("creato", path)
            else:
                print("esiste già", path)
        return
    import datetime as dt
    marker = ac.state_path(cfg, "last_decision.txt")
    def run_decision():
        import build_packet, run_agents, settle, publish
        build_packet.build(cfg); run_agents.run(cfg); settle.settle(cfg); publish.publish(cfg)
        open(marker, "w").write(dt.date.today().isoformat())
    def run_weekly():
        import mark, publish
        mark.mark(cfg); publish.publish(cfg)

    if mode == "auto":
        # da lanciare ogni settimana: decide da solo se è periodo di decisione (>= decision_days) o solo MTM
        last = open(marker).read().strip() if os.path.exists(marker) else None
        due = True
        if last:
            days = (dt.date.today() - dt.date.fromisoformat(last)).days
            due = days >= cfg["cadence"]["decision_days"]
        (run_decision if due else run_weekly)()
        print(f"[auto] {'decisione' if due else 'solo mark'} (ultima decisione: {last})")
    elif mode == "decision":
        run_decision()
    elif mode == "weekly":
        run_weekly()
    else:
        sys.exit("mode: init | decision | weekly | auto")

if __name__ == "__main__":
    main()
