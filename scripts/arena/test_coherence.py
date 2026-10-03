#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Casi di prova del layer di coerenza. Serve a due cose: dimostrare che intercetta
la contraddizione EDV del 2026-09-17 e, soprattutto, che NON spara falsi positivi
sulle tesi legittime che ci somigliano (una copertura, uno short motivato, un
bond a duration corta descritto come 'meno vulnerabile').

    python scripts/arena/test_coherence.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coherence as co

def D(rationale, orders):
    return {"as_of": "test", "model": "test", "rationale": rationale, "orders": orders}

def O(t, side, thesis, w=0.1, action="open", attesa=None):
    o = {"ticker": t, "action": action, "side": side, "target_weight": w, "thesis": thesis}
    if attesa: o["attesa"] = attesa
    return o

CASI = [
    # ---------------------------------------------- deve scattare (hard)
    ("il caso reale EDV", "hard",
     D("Costruisco un portafoglio core value, con carry a duration zero (USFR) e due coperture: "
       "short duration lunga (EDV) e short di un nome a valutazione estrema (ARM).",
       [O("USFR", "long", "Treasury floating rate: duration zero e cedola che sale con i rialzi Fed."),
        O("EDV", "long", "SHORT duration lunga: con Fed in rialzo, 10Y al 5% e inflazione in "
                         "accelerazione, gli zero-coupon lunghi restano il segmento piu' vulnerabile."),
        O("ARM", "short", "PE 249 con prezzo -38% in 3 mesi: valutazione estrema e momentum rotto.")])),
    ("attesa contraddice side", "hard",
     D("Visione prudente.", [O("TLT", "long", "I tassi salgono ancora.", attesa="ribasso")])),
    ("attesa coerente", "clean",
     D("Visione prudente.", [O("TLT", "short", "I tassi salgono ancora.", attesa="ribasso")])),
    ("tesi short su ordine long, senza maiuscolo", "hard",
     D("Nessuna nota.", [O("XLU", "long", "Shortare le utility: bond proxy che soffrono i tassi reali.")])),
    ("tesi long su ordine short", "hard",
     D("Nessuna nota.", [O("GLD", "short", "Comprare oro qui: copertura contro l'inflazione persistente.")])),
    ("rationale che inverte il ticker", "hard",
     D("Resto difensivo: vendo allo scoperto XLE perche' il petrolio e' sopravvalutato.",
       [O("XLE", "long", "Settore a PE 17 con dividendi solidi.")])),

    # ---------------------------------------------- NON deve scattare
    ("copertura long descritta come protezione", "clean",
     D("Porto il gross all'80% con una copertura.",
       [O("USFR", "long", "Treasury floating rate: duration zero, protegge il NAV mentre i tassi salgono.")])),
    ("short legittimo con tesi ribassista", "clean",
     D("Due short su valutazioni estreme.",
       [O("ARM", "short", "PE 249, momentum rotto, candidato al de-rating se il costo del capitale sale.")])),
    ("long su bond a duration corta", "clean",
     D("Carry a rischio tasso basso.",
       [O("SHV", "long", "T-bill a 1-3 mesi: duration corta, il segmento meno vulnerabile ai rialzi.")])),
    ("short con 'comprare protezione' nella tesi", "clean",
     D("Copertura sul credito.",
       [O("HYG", "short", "Comprare protezione sul credito: short high yield con spread ai minimi.")])),
    ("long con negazione dello short", "clean",
     D("Mantengo il rischio.",
       [O("QQQ", "long", "Non shortare qui: la rottura del momentum e' gia' nei prezzi e gli utili tengono.")])),
    ("chiusura di posizione, nessun giudizio di direzione", "clean",
     D("Chiudo la copertura.", [O("EDV", "long", "Tesi esaurita, chiudo.", w=0, action="close")])),
    ("long con un solo marcatore di tono negativo", "clean",
     D("Valore difensivo.",
       [O("BMY", "long", "Pharma a PE 14 con dy 3.95%: poco sensibile al ciclo, settore a rischio "
                         "regolatorio ma valutazione bassa.")])),
]

def main():
    falliti = 0
    for nome, atteso, dec in CASI:
        r = co.audit(dec)
        ok = r["severity"] == atteso or (atteso == "clean" and r["severity"] == "soft")
        # un 'soft' su un caso atteso clean e' tollerato (e' un indizio, non blocca nulla);
        # un 'hard' non lo e'.
        if atteso == "clean" and r["severity"] == "hard": ok = False
        if atteso == "hard" and r["severity"] != "hard": ok = False
        print(f'{"OK  " if ok else "FAIL"} {nome:48} atteso={atteso:5} ottenuto={r["severity"]}')
        if not ok:
            falliti += 1
            for f in r["flags"]:
                print(f'       -> [{f["severity"]}/{f["check"]}] {f["ticker"]}: {f["detail"]}')
    print(f'\n{len(CASI)-falliti}/{len(CASI)} casi passati')
    return 1 if falliti else 0

if __name__ == "__main__":
    sys.exit(main())
