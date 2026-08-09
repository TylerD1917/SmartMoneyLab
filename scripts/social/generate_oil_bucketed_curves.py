"""
Genera equity curves 'time-in-market bucketed' per il reel petrolio.

Idea narrativa: quattro portafogli fittizi, ognuno investe nell'S&P 500 total
return SOLO nei mesi in cui il WTI reale sta nella propria fascia di prezzo.
Fuori dal bucket il portafoglio resta fermo (nessun rendimento).

E' esplicitamente NON rigoroso perche' i quattro portafogli hanno tempo di
esposizione al mercato molto diverso (n=6 mesi per '<$40', n=109 per '>$100').
Serve unicamente come storytelling visivo per un reel Instagram.

Input:  public/charts/petrolio-e-mercati-azionari/monthly_panel.csv
Output: public/charts/petrolio-e-mercati-azionari/equity_curves_bucketed.csv

Colonne output (una per fascia livello reale WTI):
    date, bucket_lt40, bucket_40_70, bucket_70_100, bucket_gt100

Autore: SmartMoneyLab - 2026.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
IN_PATH = REPO_ROOT / "public" / "charts" / "petrolio-e-mercati-azionari" / "monthly_panel.csv"
OUT_PATH = REPO_ROOT / "public" / "charts" / "petrolio-e-mercati-azionari" / "equity_curves_bucketed.csv"

# Coerenza con i label del backtest (script petrolio-e-mercati-azionari.py)
BUCKET_TO_COL = {
    "<$40 (basso)":       "bucket_lt40",
    "$40-70 (normale)":   "bucket_40_70",
    "$70-100 (elevato)":  "bucket_70_100",
    ">$100 (shock)":      "bucket_gt100",
}


def main():
    df = pd.read_csv(IN_PATH, parse_dates=["date"]).set_index("date").sort_index()

    # Il monthly_panel.csv esporta gia' 'regime_A' come categoria
    if "regime_A" not in df.columns or "SP500_ret" not in df.columns:
        raise SystemExit(
            "monthly_panel.csv privo delle colonne attese "
            "(regime_A, SP500_ret). Rilancia scripts/petrolio-e-mercati-azionari.py."
        )

    n_start = 1.0
    curves = {col: pd.Series(index=df.index, dtype=float)
              for col in BUCKET_TO_COL.values()}
    running = {col: n_start for col in BUCKET_TO_COL.values()}

    for date, row in df.iterrows():
        bucket = row["regime_A"]
        ret = row["SP500_ret"]
        # Applica il rendimento SOLO al portafoglio corrispondente al bucket.
        # Gli altri portafogli restano fermi.
        target_col = BUCKET_TO_COL.get(bucket)
        if target_col is not None and pd.notna(ret):
            running[target_col] = running[target_col] * (1 + ret)
        # Snapshot per ognuno
        for col in BUCKET_TO_COL.values():
            curves[col].loc[date] = running[col]

    out = pd.DataFrame(curves)
    # Normalizzo tutte a 1.0 al primo mese (partono da uno, salgono da li)
    out.to_csv(OUT_PATH, index_label="date")

    print(f"[ok] Equity curves bucketed salvate in {OUT_PATH}")
    print(f"\nNAV finale per bucket (base=1):")
    for label, col in BUCKET_TO_COL.items():
        v = out[col].iloc[-1]
        pct = (v - 1) * 100
        n_months = int((df["regime_A"] == label).sum())
        print(f"  {label:<22} -> {v:.3f}  ({pct:+7.1f}%, tempo in mercato: {n_months} mesi)")


if __name__ == "__main__":
    main()
