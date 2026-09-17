#!/usr/bin/env python3
"""Interroga ogni modello con lo STESSO pacchetto + il suo portafoglio + la sua MEMORIA, salva le decisioni.
Senza chiave API il modello va in modalita' STUB (nessuna operazione) cosi' la pipeline gira comunque."""
import os, sys, json, re, glob, urllib.request, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac

# ---------------- prompt ----------------
SYSTEM = (
 "Sei un gestore di portafoglio in una competizione trasparente tra IA. Ogni due settimane ricevi lo "
 "STESSO pacchetto di dati e notizie di tutti i concorrenti, lo stato del tuo portafoglio e la MEMORIA "
 "delle tue decisioni passate. Obiettivo: massimizzare il rendimento corretto per il rischio nel lungo "
 "periodo, battendo mercato e altri modelli. Ragiona da investitore, non da trader frenetico.\n"
 "COERENZA: hai una strategia che porti avanti nel tempo. Rileggi la tua memoria e resta coerente con le "
 "tesi precedenti; se cambi idea rispetto a un periodo passato, DEVI dire esplicitamente cosa e' cambiato e "
 "perche'. Non ribaltare il portafoglio senza motivo.\n"
 "GIUSTIFICAZIONE OBBLIGATORIA: ogni singolo ordine deve avere una 'thesis' non vuota (perche' proprio quel "
 "titolo, proprio ora, proprio quel peso). Il 'rationale' riassume la visione del periodo.\n"
 "REGOLE: capitale 100k virtuali; solo strumenti dell'universo fornito; long e short; max 10 posizioni; "
 "niente leva (esposizione lorda <= 100% dell'equity); ogni operazione paga costi, non fare trading inutile. "
 "Basati SOLO sul pacchetto, sulla tua memoria e sul tuo ragionamento. "
 "Rispondi con SOLO questo JSON, nessun altro testo:\n"
 '{"rationale":"<max 120 parole; includi coerenza/cambi rispetto al passato>",'
 '"orders":[{"ticker":"XLE","action":"open|increase|trim|close","side":"long|short",'
 '"target_weight":0.15,"thesis":"1-2 frasi, OBBLIGATORIA"}]}\n'
 "target_weight = peso a mercato desiderato sull'equity (0-1). Chiudere: action close, target_weight 0. "
 "Nessuna mossa: orders vuoto (spiega comunque nel rationale perche' mantieni le posizioni)."
)

def compact_instruments(packet):
    lines = []
    for i in packet["instruments"]:
        lines.append(
            f'{i["ticker"]}|{i["group"]}|px {i.get("price")}|1w {i.get("ret_1w")}|1m {i.get("ret_1m")}|'
            f'3m {i.get("ret_3m")}|12m {i.get("ret_12m")}|pe {i.get("pe")}|dy {i.get("div_yield")}')
    return "\n".join(lines)

def portfolio_view(pf, prices):
    E = ac.equity(pf, prices)
    rows = []
    for t, pos in pf["positions"].items():
        p = prices.get(t); mv = pos["qty"]*p if p else 0
        rows.append(f'{t}: qty {round(pos["qty"],2)} @avg {round(pos.get("avg_price",0),2)} '
                    f'| px {p} | mv {round(mv,0)} | peso {round(mv/E,3) if E else 0}')
    return (f"cash {round(pf['cash'],0)} | equity {round(E,0)}\n" +
            ("\n".join(rows) if rows else "nessuna posizione aperta"))

def agent_memory(cfg, mid):
    """Ricostruisce la memoria dell'agente dalle sue decisioni passate + curva NAV.
    Nessuno storage nuovo: rilegge state/decisions/decision_<mid>_*.json e la NAV."""
    k = cfg.get("memory", {}).get("lookback", 4)
    dpath = ac.state_path(cfg, "decisions")
    files = sorted(glob.glob(os.path.join(dpath, f"decision_{mid}_*.json")))
    nav = ac.read_nav(cfg, mid)
    navmap = {d: v for d, v in nav}
    entries = []
    for f in files[-k:]:
        d = ac.read_json(f) or {}
        as_of = d.get("as_of", "?")
        orders = d.get("orders", [])
        moves = "; ".join(
            f'{o.get("action","?")} {o.get("side","")} {o.get("ticker","?")}->{o.get("target_weight","?")}'
            for o in orders) or "nessuna mossa"
        eq = navmap.get(as_of)
        entries.append(f'[{as_of}] equity {round(eq) if eq else "?"} | tesi: {str(d.get("rationale",""))[:220]} | mosse: {moves}')
    cur = nav[-1][1] if nav else cfg["capital"]
    perf = (f'PERFORMANCE FINORA: NAV {round(cur)} su {cfg["capital"]} iniziali '
            f'({round((cur/cfg["capital"]-1)*100,1)}%).')
    if not entries:
        return f"MEMORIA: prima decisione, nessuno storico. {perf}"
    return ("LA TUA MEMORIA (decisioni passate, dalla piu' vecchia alla piu' recente):\n"
            + "\n".join(entries) + f"\n{perf}")

def build_user(packet, pf, prices, memory):
    m = packet["macro"]
    macro = " ".join(f"{k} {v.get('last')}({v.get('ret_1w')})" for k, v in m.items())
    def _news_line(n):
        base = f'- [{n.get("date")}] ({n.get("cat","")}) {n.get("source","")}: {n.get("title","")}'
        return base + (f' - {n["summary"]}' if n.get("summary") else "")
    news = "\n".join(_news_line(n) for n in packet.get("news", []))
    return (f"AS-OF: {packet['as_of']}\n\nMACRO: {macro}\n\n"
            f"UNIVERSO (ticker|gruppo|prezzo|rend 1w/1m/3m/12m|PE|div yield):\n{compact_instruments(packet)}\n\n"
            f"NOTIZIE (data|categoria|fonte|titolo|sommario):\n{news}\n\n{memory}\n\nIL TUO PORTAFOGLIO ORA:\n{portfolio_view(pf, prices)}\n\n"
            "Decidi le mosse per questo periodo, restando coerente con la tua memoria. Restituisci SOLO il JSON.")

# ---------------- adapters (HTTP) ----------------
def _post(url, headers, body, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def call_model(provider, model, key, system, user, temp):
    if provider in ("openai", "moonshot"):
        base = "https://api.openai.com/v1" if provider == "openai" else "https://api.moonshot.ai/v1"
        d = _post(f"{base}/chat/completions",
                  {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                  {"model": model, "temperature": temp,
                   "messages": [{"role": "system", "content": system},
                                {"role": "user", "content": user}]})
        return d["choices"][0]["message"]["content"]
    if provider == "anthropic":
        d = _post("https://api.anthropic.com/v1/messages",
                  {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                  {"model": model, "max_tokens": 2000, "temperature": temp, "system": system,
                   "messages": [{"role": "user", "content": user}]})
        return d["content"][0]["text"]
    if provider == "google":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        d = _post(url, {"Content-Type": "application/json"},
                  {"systemInstruction": {"parts": [{"text": system}]},
                   "contents": [{"parts": [{"text": user}]}],
                   "generationConfig": {"temperature": temp}})
        return d["candidates"][0]["content"]["parts"][0]["text"]
    raise ValueError(f"provider sconosciuto: {provider}")

# ---------------- parse ----------------
def parse_decision(text):
    if not text: return {"rationale": "", "orders": []}
    t = re.sub(r"```(json)?", "", text).strip()
    a, b = t.find("{"), t.rfind("}")
    if a >= 0 and b > a:
        try:
            d = json.loads(t[a:b+1])
            d.setdefault("orders", []); d.setdefault("rationale", "")
            if not isinstance(d["orders"], list): d["orders"] = []
            # giustificazione obbligatoria: marca gli ordini senza thesis (non li scarta, li segnala)
            for o in d["orders"]:
                if isinstance(o, dict) and not str(o.get("thesis", "")).strip():
                    o["thesis"] = "(nessuna giustificazione fornita)"
            return d
        except Exception:
            pass
    return {"rationale": "(parse error)", "orders": [], "_raw": text[:2000]}

# ---------------- main ----------------
def run(cfg):
    meta, universe = ac.load_universe(cfg)
    packet = ac.read_json(ac.state_path(cfg, "packets", "packet_latest.json"))
    if not packet: sys.exit("Nessun packet_latest.json: lancia prima build_packet.py")
    prices = {i["ticker"]: i.get("price") for i in packet["instruments"]}
    today = packet["as_of"]
    for m in cfg["models"]:
        mid = m["id"]
        pf = ac.read_json(ac.state_path(cfg, f"portfolio_{mid}.json")) or ac.portfolio_new(cfg, mid)
        memory = agent_memory(cfg, mid)
        user = build_user(packet, pf, prices, memory)
        key = os.environ.get(m["key_env"])
        if not key:
            decision = {"rationale": "(STUB: nessuna chiave API, nessuna operazione)", "orders": []}
            raw = "STUB"
        else:
            try:
                raw = call_model(m["provider"], m["model"], key, SYSTEM, user, cfg["temperature"])
                decision = parse_decision(raw)
            except Exception as e:
                decision = {"rationale": f"(errore API: {e})", "orders": []}; raw = str(e)
        decision["as_of"] = today; decision["model"] = mid
        ac.write_json(ac.state_path(cfg, "decisions", f"decision_{mid}_{today}.json"), decision)
        ac.write_json(ac.state_path(cfg, "transcripts", f"transcript_{mid}_{today}.json"),
                      {"model": mid, "as_of": today, "system": SYSTEM, "user": user, "raw": raw})
        print(f"[agent] {mid}: {len(decision['orders'])} ordini")

if __name__ == "__main__":
    run(ac.load_config())
