#!/usr/bin/env python3
"""Test di regressione del motore NAV. Nessuna rete: i prezzi sono inventati.

Esistono per un guasto preciso. Il 2026-10-06 la Action e' andata a buon fine,
non ha segnalato nulla, e ha pubblicato tutti i modelli a 100.000 e +0,00% con
le curve sparite. La causa erano tre comportamenti del vecchio motore, e ognuno
di questi test ne fissa uno:

  - gli snapshot del primo segmento venivano scartati -> test_due_segmenti,
    test_tutta_la_storia_resta;
  - una riallocazione datata in un giorno non ancora chiuso azzerava la serie
    -> test_snapshot_futuro_non_azzera;
  - una serie vuota veniva pubblicata come 100.000 -> test_senza_snapshot_si_ferma
    e test_publish_rifiuta_storia_piu_corta.

  python scripts/arena/test_nav_daily.py
"""
import os
import sys
import json
import shutil
import tempfile
import datetime as dt

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.abspath(os.path.join(QUI, "..")))

import arena_core as ac
import nav_daily as nd

SESSIONI = ["2026-09-17", "2026-09-18", "2026-09-21", "2026-09-22", "2026-09-23"]
PREZZI = {                       # ticker -> prezzo per sessione
    "AAA": [100.0, 101.0, 102.0, 103.0, 104.0],
    "BBB": [50.0, 50.0, 50.0, 50.0, 50.0],
    "IVV": [600.0, 606.0, 612.0, 618.0, 624.0],
    "ACWI": [120.0, 121.2, 122.4, 123.6, 124.8],
}


class FakeRow(dict):
    def __getitem__(self, k):
        return dict.__getitem__(self, k)


class FakeClose:
    """Il minimo di un DataFrame che serve a nav_daily."""

    def __init__(self, sessioni, prezzi):
        self._d = list(sessioni)
        self._p = prezzi
        self.columns = list(prezzi)

    class _Giorno:
        def __init__(self, s): self.s = s
        def date(self): return dt.date.fromisoformat(self.s)

    class _Idx:
        def __init__(self, d): self._d = [FakeClose._Giorno(x) for x in d]
        def __iter__(self): return iter(self._d)
        def __len__(self): return len(self._d)
        def __getitem__(self, i): return self._d[i]

    @property
    def index(self):
        return FakeClose._Idx(self._d)

    @property
    def loc(self):
        p, d = self._p, self._d
        class L:
            def __getitem__(self, data):
                i = d.index(data)
                return FakeRow({t: v[i] for t, v in p.items()})
        return L()

    @property
    def empty(self):
        return not self._d


def cfg_tmp(root):
    return {"_root": root, "state_dir": "state", "public_dir": "public",
            "capital": 100000, "max_positions": 10, "gross_exposure_cap": 1.0,
            "cadence": {"decision_days": 14, "mark_days": 7},
            "costs": {"commission": 0.0005, "spread": 0.0005, "short_borrow_annual": 0.003},
            "benchmarks": {"SP500": "IVV", "ACWI": "ACWI"},
            "models": [{"id": "m1"}], "random_control": False,
            "universe_file": "universe.json"}


def scrivi_snapshot(cfg, mid, date, cash, posizioni):
    ac.write_json(nd.snap_path(cfg, mid, date),
                  {"date": date, "cash": cash,
                   "positions": {t: {"qty": q, "avg_price": None} for t, q in posizioni.items()}})


# ------------------------------------------------------------------ test
def test_un_segmento():
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        scrivi_snapshot(cfg, "m1", "2026-09-17", 50000.0, {"AAA": 500.0})
        ser = nd.serie_nav(nd.leggi_segmenti(cfg, "m1"), FakeClose(SESSIONI, PREZZI), {}, cfg)
        assert len(ser) == 5, ser
        assert abs(ser[0][1] - 100000.0) < 1e-6, ser[0]
        assert abs(ser[-1][1] - 102000.0) < 1e-6, ser[-1]   # 50.000 + 500*104


def test_due_segmenti():
    """Il primo segmento NON deve sparire quando ne arriva un secondo."""
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        scrivi_snapshot(cfg, "m1", "2026-09-17", 50000.0, {"AAA": 500.0})
        scrivi_snapshot(cfg, "m1", "2026-09-22", 101500.0, {"BBB": 10.0})
        ser = nd.serie_nav(nd.leggi_segmenti(cfg, "m1"), FakeClose(SESSIONI, PREZZI), {}, cfg)
        date = [d for d, _ in ser]
        assert date == SESSIONI, date
        assert abs(dict(ser)["2026-09-18"] - 100500.0) < 1e-6      # primo segmento
        assert abs(dict(ser)["2026-09-22"] - 102000.0) < 1e-6      # secondo


def test_snapshot_futuro_non_azzera():
    """Il guasto del 2026-10-06: riallocazione decisa prima della chiusura."""
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        scrivi_snapshot(cfg, "m1", "2026-09-17", 50000.0, {"AAA": 500.0})
        scrivi_snapshot(cfg, "m1", "2026-09-24", 90000.0, {"BBB": 100.0})   # oltre l'ultima sessione
        ser = nd.serie_nav(nd.leggi_segmenti(cfg, "m1"), FakeClose(SESSIONI, PREZZI), {}, cfg)
        assert len(ser) == 5, f"la curva si e' interrotta: {ser}"
        assert abs(ser[-1][1] - 102000.0) < 1e-6, ser[-1]


def test_tutta_la_storia_resta():
    """Anche con l'etichetta "_bootstrap" di una versione vecchia dello script."""
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        ac.write_json(nd.snap_path(cfg, "m1", "2026-09-17"),
                      {"date": "2026-09-17", "cash": 50000.0, "_bootstrap": True,
                       "positions": {"AAA": {"qty": 500.0}}})
        scrivi_snapshot(cfg, "m1", "2026-09-22", 101500.0, {"BBB": 10.0})
        segs = nd.leggi_segmenti(cfg, "m1")
        assert [s["date"] for s in segs] == ["2026-09-17", "2026-09-22"], segs


def test_dividendi_e_borrow():
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        scrivi_snapshot(cfg, "m1", "2026-09-17", 150000.0, {"AAA": -500.0})   # short
        divs = {"AAA": {"2026-09-18": 2.0}}
        ser = nd.serie_nav(nd.leggi_segmenti(cfg, "m1"), FakeClose(SESSIONI, PREZZI), divs, cfg)
        d1 = dict(ser)["2026-09-18"]
        atteso = 150000.0 - (500 * 100 * 0.003 * 1 / 365) - 1000.0 - 500 * 101.0
        assert abs(d1 - atteso) < 1e-6, (d1, atteso)


def test_senza_snapshot_si_ferma():
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        try:
            nd.rebuild(cfg, write=False)
        except SystemExit as e:
            assert "snapshot" in str(e), e
            return
        raise AssertionError("rebuild doveva fermarsi senza snapshot")


def test_publish_rifiuta_storia_piu_corta():
    import publish
    with tempfile.TemporaryDirectory() as root:
        cfg = cfg_tmp(root)
        out = os.path.join(root, "public")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "nav_daily.csv"), "w", encoding="utf-8") as f:
            f.write("date,m1,SP500,ACWI\n")
            for d in SESSIONI:
                f.write(f"{d},100000.00,100000.00,100000.00\n")
        corta = {"m1": [(SESSIONI[-1], 100000.0)],
                 "SP500": [(d, 100000.0) for d in SESSIONI],
                 "ACWI": [(d, 100000.0) for d in SESSIONI]}
        try:
            publish.verifica_regressioni(corta, out, ["m1", "SP500", "ACWI"])
        except SystemExit as e:
            assert "ANNULLATA" in str(e) and "m1" in str(e), e
            return
        raise AssertionError("publish doveva rifiutare una storia piu' corta")


def test_publish_rifiuta_serie_vuota():
    import publish
    with tempfile.TemporaryDirectory() as root:
        try:
            publish.verifica_regressioni({"m1": []}, root, ["m1"])
        except SystemExit as e:
            assert "VUOTA" in str(e), e
            return
        raise AssertionError("publish doveva rifiutare una serie vuota")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} test superati.")
