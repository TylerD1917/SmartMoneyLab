#!/usr/bin/env python3
"""Serie mensili total return in EUR per il simulatore "prestito per investire".

Produce public/tools/prestito-investimento-serie.json: per ogni mattone una
serie di rendimenti mensili LORDI in euro. Il simulatore nel browser compone i
portafogli, applica l'erosione dei costi, costruisce le finestre mobili e fa la
matematica del prestito: qui dentro non entra nessun parametro dell'utente, solo
i dati.

Scelte dichiarate
-----------------
- Azionario: riusa build_eurusd() e build_indices() dello studio
  "rendimenti-netti-indici-azionari", quindi il simulatore e quell'articolo
  usano per costruzione le stesse serie e le stesse convenzioni (Nasdaq come
  indice di prezzo con dividendo figurato 0,75%/anno).
- Cambio: USD per 1 EUR dal 1969. Pre-euro e' il cambio IMPLICITO ricavato dal
  rapporto fra le due versioni valutarie dello stesso indice MSCI World, non il
  marco: il marco sottostimava di ~108 bps/anno i rendimenti in euro.
- Obbligazionario: Treasury 10Y constant maturity, total return ricostruito dai
  rendimenti mensili FRED col modello duration-based (Swinkels 2019), lo stesso
  dello studio "ha-senso-obbligazioni-portafoglio", POI convertito in euro.
  E' quindi una gamba obbligazionaria in dollari NON coperta dal cambio: non e'
  l'ETF obbligazionario EUR-hedged che molti tengono come parte difensiva, e il
  cambio aggiunge volatilita' proprio alla gamba che dovrebbe essere calma.
  Il JSON riporta anche la versione senza cambio, per misurare la differenza.
- Oro: prezzo mensile in dollari convertito in euro.
"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "public" / "tools" / "prestito-investimento-serie.json"


def _load(nome: str, file: str):
    spec = importlib.util.spec_from_file_location(nome, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def yields_dgs10() -> pd.Series:
    """Rendimenti mensili del Treasury 10Y. Locale se c'e', altrimenti FRED."""
    import urllib.request
    p = DATA / "Bonds" / "DGS10.csv"
    if not p.exists():
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
        req = urllib.request.Request(url, headers={"User-Agent": "smartmoneylab/1.0"})
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        print(f"[serie] DGS10 scaricato da FRED -> {p.relative_to(ROOT)}")
    df = pd.read_csv(p)
    dc = next(c for c in df.columns if c.lower() in ("observation_date", "date"))
    vc = next(c for c in df.columns if c != dc)
    df[dc] = pd.to_datetime(df[dc])
    s = pd.Series(pd.to_numeric(df[vc], errors="coerce").values,
                  index=pd.PeriodIndex(df[dc], freq="M")).dropna()
    return (s.groupby(level=0).last().sort_index() / 100.0)   # in frazione


def ust10y_total_return(y: pd.Series) -> pd.Series:
    """Modello duration-based: carry mensile + P&L da movimento dello yield."""
    n = 10
    yp = y.shift(1)
    dmod = (1.0 / yp) * (1.0 - 1.0 / (1.0 + yp) ** n)
    r = yp / 12.0 - dmod * (y - yp)
    return r.dropna()


def gold_eur(eurusd: pd.Series) -> pd.Series:
    df = pd.read_csv(DATA / "cache" / "gold_monthly.csv")
    idx = pd.PeriodIndex(pd.to_datetime(df["Date"]), freq="M")
    s = pd.Series(pd.to_numeric(df["Price"], errors="coerce").values, index=idx).dropna()
    s = s.groupby(level=0).last().sort_index()
    return (s / eurusd).dropna()


def to_returns(level: pd.Series) -> pd.Series:
    return level.pct_change().dropna()


def main() -> None:
    rn = _load("rn", "rendimenti-netti-indici-azionari.py")
    eurusd, meta_fx = rn.build_eurusd()
    print(f"[serie] cambio USD/EUR: {eurusd.index[0]} -> {eurusd.index[-1]}")

    idx = rn.build_indices(eurusd)                   # livelli in EUR
    blocchi: dict[str, pd.Series] = {
        "world":  to_returns(idx["MSCI World"]),
        "acwi":   to_returns(idx["MSCI ACWI IMI"]),
        "sp500":  to_returns(idx["S&P 500"]),
        "nasdaq": to_returns(idx["Nasdaq Composite"]),
        "oro":    to_returns(gold_eur(eurusd)),
    }

    # obbligazionario: total return in USD -> livello -> EUR -> rendimenti
    r_usd = ust10y_total_return(yields_dgs10())
    liv_usd = (1.0 + r_usd).cumprod() * 100.0
    blocchi["bond"] = to_returns((liv_usd / eurusd).dropna())
    blocchi["bond_usd"] = r_usd                      # per misurare l'effetto cambio

    out = {
        "generato": pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
        "valuta": "EUR",
        "tipo": "rendimenti mensili lordi total return",
        "note": {
            "cambio": "USD per 1 EUR; pre-1999 cambio implicito dal rapporto fra le "
                      "due versioni valutarie del MSCI World",
            "bond": "Treasury 10Y constant maturity, total return da modello "
                    "duration-based sui rendimenti FRED, convertito in euro e NON "
                    "coperto dal cambio",
            "nasdaq": "indice di prezzo con dividendo figurato 0,75%/anno",
        },
        "serie": {},
    }
    print("\n[serie] mattoni costruiti:")
    for k, s in blocchi.items():
        s = s.sort_index()
        out["serie"][k] = {"inizio": str(s.index[0]), "fine": str(s.index[-1]),
                           "n": int(len(s)),
                           "r": [round(float(x), 6) for x in s.values]}
        ann = (1.0 + s).prod() ** (12.0 / len(s)) - 1.0
        print(f"  {k:9s} {s.index[0]} -> {s.index[-1]}  {len(s):4d} mesi  "
              f"annualizzato {ann*100:+6.2f}%")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"\n[serie] scritto {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:.0f} KB)")

    # effetto del cambio sulla gamba obbligazionaria, misurato
    b_eur, b_usd = blocchi["bond"].align(blocchi["bond_usd"], join="inner")
    ann_e = (1 + b_eur).prod() ** (12 / len(b_eur)) - 1
    ann_u = (1 + b_usd).prod() ** (12 / len(b_usd)) - 1
    print(f"[serie] gamba obbligazionaria sul periodo comune ({len(b_eur)} mesi):")
    print(f"        in dollari   {ann_u*100:+.2f}%/anno, volatilita' {b_usd.std()*np.sqrt(12)*100:.1f}%")
    print(f"        in euro      {ann_e*100:+.2f}%/anno, volatilita' {b_eur.std()*np.sqrt(12)*100:.1f}%")


if __name__ == "__main__":
    main()
