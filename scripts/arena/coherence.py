#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer di coerenza delle decisioni dell'arena.

PERCHE' ESISTE
--------------
Il 2026-09-17 un modello ha aperto EDV (Treasury a duration lunga) con side=long
scrivendo come tesi "SHORT duration lunga: ... gli zero-coupon lunghi restano il
segmento piu' vulnerabile". Il rationale dello stesso documento elencava EDV fra
le coperture short, La pipeline ha eseguito l'ordine alla lettera.
L'esposizione dichiarata ("Gross 83%, net ~70%") NON e' una prova: con EDV long il
net e' 73%, con EDV short 57%, e il 70% dichiarato torna solo leggendo "net" come
"il lato long dopo le coperture". Per questo il controllo 2 resta un indizio.

COSA FA E COSA NON FA
---------------------
Questo modulo RILEVA contraddizioni interne a una decisione. Non le corregge mai:
l'esperimento ha valore solo se le scelte restano dei modelli. Chi lo usa
(run_agents) puo' al massimo ri-sottoporre la contraddizione al modello stesso e
poi eseguire qualunque cosa risponda, lasciando il flag nel log pubblico.

I QUATTRO CONTROLLI, dal piu' forte al piu' debole
--------------------------------------------------
1. attesa_vs_side   - il campo 'attesa' (rialzo|ribasso) contraddice 'side'.
                      Deterministico, zero ambiguita'.
2. esposizione      - il gross/net dichiarato nel rationale non torna con gli
                      ordini. Indizio soltanto: "net" e' ambiguo (long-short
                      oppure solo-long), quindi mai 'hard'. Se una sola inversione
                      riconcilia la cifra, il flag dice quale ordine.
3. rationale_vs_side- il rationale nomina il ticker con una direzione opposta a
                      quella dell'ordine.
4. tesi             - la tesi dell'ordine usa un marcatore di direzione esplicito
                      (SHORT/long/ribassista...) opposto al side, oppure un
                      lessico interamente ribassista su una posizione long.

Severita': 'hard' = contraddizione dimostrata; 'soft' = indizio, da guardare.
Solo 'hard' innesca la ri-domanda.
"""
import json, os, re, sys, unicodedata

TOLLERANZA_NET = 2.5   # punti percentuali di scarto ammessi sul net dichiarato

# ---------------------------------------------------------------- lessico
RIALZO = {"rialzo", "rialzista", "su", "up", "sale", "salira"}
RIBASSO = {"ribasso", "ribassista", "giu", "down", "scende", "scendera"}

# marcatori di direzione espliciti dentro il testo libero
RE_SHORT = re.compile(r"\b(short|shortare|shortiamo|vendere allo scoperto|ribassista|scoperto)\b", re.I)
RE_LONG  = re.compile(r"\b(long|comprare|accumulare|rialzista)\b", re.I)
# negazioni: "non shortare qui", "niente long su...", "evito di comprare"
RE_NEGAZIONE = re.compile(r"\b(non|niente|nessun[ao]?|senza|evit[oa]\w*(?:\s+di)?|mai|anziche|invece di)\s*$", re.I)


def _direzione(testo, inizio=0, fine=None):
    """(giu, su): c'e' un marcatore short / long nel testo, NON negato.
    'Non shortare qui' non e' una tesi short."""
    t = str(testo or "")[inizio:fine if fine is not None else len(str(testo or ""))]
    def trova(rx):
        for m in rx.finditer(t):
            # le 18 battute prima del marcatore: se finiscono con una negazione, non conta
            if RE_NEGAZIONE.search(t[max(0, m.start() - 18):m.start()]):
                continue
            return True
        return False
    return trova(RE_SHORT), trova(RE_LONG)

# lessico di tono: usato solo come indizio (soft)
TONO_GIU = ["vulnerabil", "penalizza", "de-rating", "derating", "ribass", "crollo", "crolla",
            "sottoperform", "scende", "scendera", "soffre", "soffrira", "eroso", "a rischio",
            "sopravvalutat", "bolla", "momentum rotto", "rotto", "deludera"]
TONO_SU  = ["beneficia", "beneficera", "sottovalutat", "a sconto", "momentum positivo",
            "sovraperform", "crescita", "cresce", "cedola", "dividendo", "pricing power",
            "qualita", "difensiv", "protegge", "carry"]


def _piatto(s):
    """minuscolo senza accenti: il lessico deve funzionare su 'qualita'' e 'qualità'."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _atteso_side(attesa):
    a = _piatto(attesa).strip()
    if a in RIALZO: return "long"
    if a in RIBASSO: return "short"
    return None


def _flag(i, o, check, severity, detail):
    return {"order_index": i, "ticker": o.get("ticker", "?"), "side": o.get("side", "?"),
            "check": check, "severity": severity, "detail": detail}


# ---------------------------------------------------------------- 1. attesa
def _chk_attesa(orders):
    out = []
    for i, o in enumerate(orders):
        if not isinstance(o, dict) or not o.get("attesa"):
            continue
        atteso = _atteso_side(o["attesa"])
        side = str(o.get("side", "")).lower()
        if atteso and side and atteso != side:
            out.append(_flag(i, o, "attesa_vs_side", "hard",
                             f'attesa "{o["attesa"]}" implica side {atteso}, l\'ordine dice {side}'))
    return out


# ---------------------------------------------------------------- 2. esposizione
def _net_gross(orders, flip=None):
    """Ritorna (net, gross, lungo) in punti percentuali:
    net = long - short, gross = somma dei pesi, lungo = solo il lato long.
    flip = indice di un ordine di cui invertire il side."""
    net = gross = lungo = 0.0
    for i, o in enumerate(orders):
        try: w = abs(float(o.get("target_weight") or 0))
        except (TypeError, ValueError): w = 0.0
        if str(o.get("action", "")).lower() == "close":
            continue
        side = str(o.get("side", "long")).lower()
        if i == flip:
            side = "short" if side == "long" else "long"
        gross += w
        if side == "short":
            net -= w
        else:
            net += w; lungo += w
    return net * 100, gross * 100, lungo * 100


def _dichiarato(rationale):
    t = _piatto(rationale)
    def grab(*parole):
        for p in parole:
            m = re.search(p + r"[^0-9%\-]{0,12}(-?\d{1,3}(?:[.,]\d)?)\s*%", t)
            if m:
                try: return float(m.group(1).replace(",", "."))
                except ValueError: pass
        return None
    return grab("net", "netta", "netto"), grab("gross", "lorda", "lordo", "esposizione lorda")


def _chk_esposizione(decision, orders):
    """Confronta il gross/net dichiarato nel rationale con gli ordini.

    ATTENZIONE: "net" e' ambiguo. Qualcuno lo usa come long-short, qualcuno come
    "quanto resta sul lato long dopo le coperture" (= long). Proviamo entrambe le
    convenzioni e non alziamo MAI questo controllo a 'hard': e' un odore, non una
    prova. Se una sola inversione riconcilia la cifra, almeno diciamo quale ordine.
    """
    out = []
    net_dic, gross_dic = _dichiarato(decision.get("rationale", ""))
    if net_dic is None and gross_dic is None:
        return out
    net, gross, lungo = _net_gross(orders)
    if gross_dic is not None and abs(gross - gross_dic) > TOLLERANZA_NET:
        out.append({"order_index": None, "ticker": None, "side": None, "check": "esposizione_gross",
                    "severity": "soft",
                    "detail": f"gross dichiarato {gross_dic}%, calcolato dagli ordini {round(gross,1)}%"})
    if net_dic is None:
        return out
    def scarto(valori): return min(abs(v - net_dic) for v in valori)
    if scarto((net, lungo)) <= TOLLERANZA_NET:
        return out
    candidati = []
    for i, o in enumerate(orders):
        if str(o.get("action", "")).lower() == "close":
            continue
        n_f, _, l_f = _net_gross(orders, flip=i)
        if scarto((n_f, l_f)) <= TOLLERANZA_NET:
            candidati.append((i, o, n_f, l_f))
    base = (f"esposizione dichiarata {net_dic}%, dagli ordini risulta "
            f"{round(net,1)}% (long-short) o {round(lungo,1)}% (solo long)")
    if len(candidati) == 1:
        i, o, n_f, l_f = candidati[0]
        altro = "short" if str(o.get("side", "long")).lower() == "long" else "long"
        out.append(_flag(i, o, "esposizione", "soft",
                         f"{base}; torna se {o.get('ticker')} e' {altro} "
                         f"({round(n_f,1)}% / {round(l_f,1)}%)"))
    elif candidati:
        out.append({"order_index": None, "ticker": None, "side": None, "check": "esposizione",
                    "severity": "soft",
                    "detail": f"{base}; {len(candidati)} ordini la riconcilierebbero, nessuno univoco"})
    else:
        out.append({"order_index": None, "ticker": None, "side": None, "check": "esposizione",
                    "severity": "soft", "detail": base})
    return out


# ---------------------------------------------------------------- 3. rationale
def _proposizioni(testo):
    """Spezza il rationale in proposizioni. Una direzione vale per il ticker solo se
    sta nella SUA proposizione: in "carry a duration zero (USFR) e due coperture:
    short duration lunga (EDV)" lo short e' di EDV, non di USFR."""
    pezzi = re.split(r"[;.:\n]|\s+e\s+|,\s*(?=(?:con|senza|piu'|oltre|mentre)\b)", testo)
    return [x.strip() for x in pezzi if x and x.strip()]


def _chk_rationale(decision, orders):
    """Il rationale nomina il ticker con una direzione opposta a quella dell'ordine."""
    out = []
    raw = str(decision.get("rationale", "") or "")
    if not raw:
        return out
    prop = _proposizioni(raw)
    for i, o in enumerate(orders):
        t = str(o.get("ticker", "")).strip()
        side = str(o.get("side", "")).lower()
        if not t or not side or str(o.get("action", "")).lower() == "close":
            continue
        for frase in prop:
            if not re.search(r"\b" + re.escape(t) + r"\b", frase):
                continue
            giu, su = _direzione(frase)
            if side == "long" and giu and not su:
                out.append(_flag(i, o, "rationale_vs_side", "hard",
                                 f'il rationale descrive {t} come short: "{frase}"'))
                break
            if side == "short" and su and not giu:
                out.append(_flag(i, o, "rationale_vs_side", "hard",
                                 f'il rationale descrive {t} come long: "{frase}"'))
                break
    return out


# ---------------------------------------------------------------- 4. tesi
def _chk_tesi(orders):
    out = []
    for i, o in enumerate(orders):
        if not isinstance(o, dict) or str(o.get("action", "")).lower() == "close":
            continue
        tesi = str(o.get("thesis", "") or "")
        side = str(o.get("side", "")).lower()
        if not tesi or not side:
            continue
        # 4a. marcatore esplicito e enfatico: SHORT/LONG in maiuscolo, o in apertura di tesi
        testa = tesi[:40]
        giu_testa, su_testa = _direzione(testa)
        maiusc_giu = bool(re.search(r"\bSHORT\b", tesi)) and not RE_NEGAZIONE.search(
            tesi[max(0, tesi.find("SHORT") - 18):tesi.find("SHORT")])
        maiusc_su = bool(re.search(r"\bLONG\b", tesi)) and not RE_NEGAZIONE.search(
            tesi[max(0, tesi.find("LONG") - 18):tesi.find("LONG")])
        enfatico_giu = maiusc_giu or giu_testa
        enfatico_su  = maiusc_su or su_testa
        if side == "long" and enfatico_giu and not enfatico_su:
            out.append(_flag(i, o, "tesi_vs_side", "hard",
                             f'la tesi di un ordine long apre con una direzione short: "{testa.strip()}..."'))
            continue
        if side == "short" and enfatico_su and not enfatico_giu:
            out.append(_flag(i, o, "tesi_vs_side", "hard",
                             f'la tesi di un ordine short apre con una direzione long: "{testa.strip()}..."'))
            continue
        # 4b. tono: indizio, non prova
        p = _piatto(tesi)
        giu = sum(1 for w in TONO_GIU if w in p)
        su = sum(1 for w in TONO_SU if w in p)
        if side == "long" and giu >= 2 and su == 0:
            out.append(_flag(i, o, "tono_tesi", "soft",
                             f"tesi interamente ribassista ({giu} marcatori) su una posizione long"))
        elif side == "short" and su >= 2 and giu == 0:
            out.append(_flag(i, o, "tono_tesi", "soft",
                             f"tesi interamente rialzista ({su} marcatori) su una posizione short"))
    return out


# ---------------------------------------------------------------- audit
def audit(decision):
    orders = [o for o in decision.get("orders", []) if isinstance(o, dict)]
    flags = (_chk_attesa(orders) + _chk_esposizione(decision, orders)
             + _chk_rationale(decision, orders) + _chk_tesi(orders))
    # un ordine con una contraddizione hard non ha bisogno anche del flag soft
    hard_idx = {f["order_index"] for f in flags if f["severity"] == "hard"}
    flags = [f for f in flags
             if f["severity"] == "hard" or f["order_index"] not in hard_idx]
    sev = "hard" if any(f["severity"] == "hard" for f in flags) else ("soft" if flags else "clean")
    return {"as_of": decision.get("as_of"), "model": decision.get("model"),
            "severity": sev, "n_flags": len(flags), "flags": flags}


def challenge(rapporto):
    """Il messaggio di ri-domanda. Cita la contraddizione e NON suggerisce la direzione
    giusta: chiede al modello di riemettere il JSON decidendo lui."""
    righe = []
    for f in rapporto["flags"]:
        if f["severity"] != "hard":
            continue
        t = f["ticker"] or "portafoglio"
        righe.append(f"- {t}: {f['detail']}")
    return (
        "CONTROLLO DI COERENZA. Prima di eseguire, il sistema ha rilevato che la tua decisione "
        "e' internamente contraddittoria:\n" + "\n".join(righe) + "\n\n"
        "Non ti sto dicendo quale direzione sia quella giusta: puo' essere sbagliato il side, "
        "oppure la tesi, oppure l'esposizione che hai dichiarato. Rileggi la tua decisione e "
        "riemettila per intero, nello stesso formato JSON, correggendo cio' che non torna. "
        "Se invece la ritieni corretta come l'hai scritta, riemettila identica e spiega nel "
        "rationale perche' non e' una contraddizione. Rispondi con SOLO il JSON."
    )


# ---------------------------------------------------------------- CLI
def _stampa(rapporto, path=""):
    simbolo = {"hard": "X", "soft": "~", "clean": "."}[rapporto["severity"]]
    print(f'[{simbolo}] {rapporto.get("model")} {rapporto.get("as_of")} '
          f'-> {rapporto["severity"]} ({rapporto["n_flags"]} flag) {path}')
    for f in rapporto["flags"]:
        marca = "HARD" if f["severity"] == "hard" else "soft"
        print(f'      {marca:4} [{f["check"]}] {f["ticker"] or "-"} {f["side"] or ""}: {f["detail"]}')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: coherence.py <decision.json> [altri.json ...]   (anche glob della shell)")
    peggio = "clean"
    for p in sys.argv[1:]:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        r = audit(d)
        _stampa(r, os.path.basename(p))
        if r["severity"] == "hard" or (r["severity"] == "soft" and peggio == "clean"):
            peggio = r["severity"]
    sys.exit(1 if peggio == "hard" else 0)
