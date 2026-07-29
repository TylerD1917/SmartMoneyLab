"""
Genera le curve 'forward 10 anni' da tre punti di partenza emblematici per
il reel CAPE. Ogni curva mostra la crescita reale di 1 euro nei 10 anni
SUCCESSIVI a un investimento fatto quando il CAPE era a un certo livello.

A differenza del bucketed 'time-in-market' (che per il CAPE mostrerebbe i
rendimenti CONTEMPORANEI al regime, contraddicendo la tesi dell'articolo),
questa versione mostra i rendimenti FORWARD: e' coerente col messaggio
'CAPE alto -> rendimenti futuri bassi'.

Date scelte:
  1982-07  CAPE ~7   (economico)   -> 10y reale +279%
  1995-01  CAPE ~20  (equo)        -> 10y reale +141%
  2000-01  CAPE ~44  (carissimo)   -> 10y reale  -27%

Output: public/charts/shiller-cape-predice-rendimenti/equity_curves_forward_reel.csv
Colonne: elapsed_date (asse sintetico mensile), cheap, fair, expensive
Le curve sono NAV reale cumulato (base 1.0 alla partenza).

Autore: SmartMoneyLab - 2026.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PANEL = REPO_ROOT / "public" / "charts" / "shiller-cape-predice-rendimenti" / "monthly_panel.csv"
OUT = REPO_ROOT / "public" / "charts" / "shiller-cape-predice-rendimenti" / "equity_curves_forward_reel.csv"

STARTS = {
    "cheap":     "1982-07-31",   # CAPE ~7
    "fair":      "1995-01-31",   # CAPE ~20
    "expensive": "2000-01-31",   # CAPE ~44
}
HORIZON_YEARS = 10
RETCOL = "tr_real"


def main():
    p = pd.read_csv(PANEL, parse_dates=["date"]).set_index("date").sort_index()
    paths = {}
    for key, sd in STARTS.items():
        d0 = pd.Timestamp(sd)
        window = p.loc[d0:d0 + pd.DateOffset(years=HORIZON_YEARS), RETCOL].dropna()
        nav = (1 + window).cumprod()
        nav = nav / nav.iloc[0]  # base 1.0
        # includo il punto iniziale a 1.0
        paths[key] = [1.0] + nav.tolist()

    n = min(len(v) for v in paths.values())
    paths = {k: v[:n] for k, v in paths.items()}

    # asse sintetico mensile (serve solo perche' generate_reel legge una
    # colonna data; con --elapsed il contatore mostra gli anni trascorsi)
    idx = pd.date_range("2000-01-31", periods=n, freq="ME")
    df = pd.DataFrame(paths, index=idx)
    df.to_csv(OUT, index_label="elapsed_date")
    print(f"[ok] {OUT}")
    print(f"  punti: {n} (0 -> {HORIZON_YEARS} anni)")
    for k in STARTS:
        print(f"  {k:<10} NAV finale reale: {df[k].iloc[-1]:.2f} ({(df[k].iloc[-1]-1)*100:+.0f}%)")


if __name__ == "__main__":
    main()
