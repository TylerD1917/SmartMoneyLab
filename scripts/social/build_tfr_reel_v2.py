"""
SmartMoneyLab — Reel "Dove finisce il tuo TFR?" v2 (fluido + volatilita' realistica)
====================================================================================

Rigenera il reel dell'articolo "TFR in azienda o fondo pensione?" risolvendo i due
limiti della v1 (social/tfr-o-fondo-pensione/reel_animato.mp4):

1. ANIMAZIONE A SCATTI
   La v1 usava 30 punti annuali su 450 frame: 15 frame fermi per ogni gradino.
   Qui le curve sono ricostruite a PASSO MENSILE (360 punti) e il reel gira a
   60 fps con `smooth=True` in generate_reel(), che fa avanzare la punta della
   curva per frazioni di segmento e applica un easing smoothstep al progresso.

2. CURVA TFR PERFETTAMENTE LISCIA
   La v1 usava un tasso costante del 2,5% annuo (media COVIP 2016-2025).
   Qui la volatilita' del TFR in azienda deriva dalla FONTE CHE LA GENERA DAVVERO:
   la rivalutazione e' fissata per legge (art. 2120 c.c.) a

        r_t = 1,5% + 0,75 x inflazione_t

   quindi l'unica variabile e' l'inflazione, NON i mercati. Modelliamo l'inflazione
   FOI come processo AR(1) attorno alla media implicita nel 2,5% pubblicato, con
   deviazione standard dell'ordine di grandezza di quella storica italiana.
   Risultato: oscillazioni anno su anno reali ma contenute (sigma della
   rivalutazione ~1,1 pp), non rumore casuale arbitrario.

   Il comparto azionario riceve lo stesso trattamento ma con ampiezza da
   portafoglio azionario (sigma 10% annuo, rumore mensile).

VINCOLO EDITORIALE: i montanti finali NON devono cambiare rispetto a quanto
gia' pubblicato nell'articolo e nel carosello (97.562 / 147.642 lordi ->
81k / 141k netti). Dopo la simulazione stocastica facciamo quindi il PINNING:
una bisezione su uno shift costante applicato a tutti i tassi porta il montante
terminale esattamente sul valore target. La volatilita' e' forma della curva,
non cambia il risultato.

Output (affiancati agli originali, che NON vengono toccati):
  public/charts/tfr-o-fondo-pensione/equity_curves_reel_v2.csv
  social/tfr-o-fondo-pensione/reel_animato_v2.mp4

Uso:
  python scripts/social/build_tfr_reel_v2.py

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from generate_reel import generate_reel

ROOT = Path(__file__).resolve().parent.parent.parent
CHARTS = ROOT / "public" / "charts" / "tfr-o-fondo-pensione"
SOCIAL = ROOT / "social" / "tfr-o-fondo-pensione"

# ---------------------------------------------------------------- #
# Parametri della simulazione                                      #
# ---------------------------------------------------------------- #
ANNI = 30
MESI = ANNI * 12
START = "2026-01-31"
# Seed fisso per riproducibilita'. Scelto fra i primi 400 in modo che lo shift
# di pinning necessario a centrare i montanti pubblicati sia trascurabile
# (+0,003 pp sul TFR, +0,061 pp sull'azionario): cosi' le curve mantengono
# davvero le medie dichiarate nell'articolo (2,5% e 5% annuo) e il pinning non
# e' una correzione mascherata del rendimento medio.
SEED = 390

# --- TFR in azienda: rivalutazione di legge 1,5% + 75% inflazione --- #
TFR_BASE = 0.015                 # componente fissa di legge
TFR_INFL_SHARE = 0.75            # quota di inflazione riconosciuta
TFR_MEAN = 0.025                 # media pubblicata (COVIP 2016-2025, netta)
# Inflazione media implicita nel 2,5%: (0,025 - 0,015) / 0,75 = 1,33%
INFL_MEAN = (TFR_MEAN - TFR_BASE) / TFR_INFL_SHARE
INFL_SIGMA = 0.015               # dev. std annua FOI (ordine di grandezza storico IT)
INFL_PHI = 0.50                  # persistenza AR(1): l'inflazione non salta a caso

# --- Fondo pensione, comparto azionario --- #
EQ_MEAN = 0.050                  # rendimento medio annuo netto (COVIP, 10 anni)
EQ_SIGMA = 0.10                  # volatilita' annua di un comparto azionario diversificato


def _load_targets() -> dict:
    """Legge i montanti gia' pubblicati da summary.json: sono il vincolo."""
    summary = json.loads((CHARTS / "summary.json").read_text(encoding="utf-8"))
    return {
        "tfr_yr": float(summary["tfr_yr"]),
        "azienda": float(summary["montante_lordo"]["TFR in azienda"]),
        "azionario": float(summary["montante_lordo"]["Fondo azionario"]),
        "netto_azienda": float(summary["montante_netto"]["TFR in azienda"]),
        "netto_azionario": float(summary["montante_netto"]["Fondo azionario"]),
    }


def _accumulate(monthly_rates: np.ndarray, contrib_m: float) -> np.ndarray:
    """Montante mensile: ogni mese capitalizza e incassa la quota di TFR."""
    v = 0.0
    out = np.empty(len(monthly_rates))
    for i, r in enumerate(monthly_rates):
        v = v * (1.0 + r) + contrib_m
        out[i] = v
    return out


def _pin_terminal(build_rates, contrib_m: float, target: float) -> tuple[np.ndarray, float]:
    """
    Trova per bisezione lo shift costante `c` sui tassi tale che il montante
    finale coincida col valore pubblicato. Preserva la FORMA della volatilita':
    sposta tutti i tassi della stessa quantita', non ne riscala le deviazioni.
    """
    lo, hi = -0.05, 0.05
    for _ in range(200):
        mid = (lo + hi) / 2.0
        term = _accumulate(build_rates(mid), contrib_m)[-1]
        if term < target:
            lo = mid
        else:
            hi = mid
    c = (lo + hi) / 2.0
    return _accumulate(build_rates(c), contrib_m), c


def build_curves() -> tuple[pd.DataFrame, dict]:
    targets = _load_targets()
    contrib_m = targets["tfr_yr"] / 12.0
    rng = np.random.default_rng(SEED)

    # ---- TFR in azienda: inflazione AR(1) -> rivalutazione di legge ---- #
    # sigma dello shock calibrato perche' la varianza NON condizionata dell'AR(1)
    # sia quella storica: sigma_eps = sigma * sqrt(1 - phi^2).
    eps_sigma = INFL_SIGMA * np.sqrt(1.0 - INFL_PHI ** 2)
    infl = np.empty(ANNI)
    prev = INFL_MEAN
    for y in range(ANNI):
        prev = INFL_MEAN + INFL_PHI * (prev - INFL_MEAN) + rng.normal(0.0, eps_sigma)
        infl[y] = prev
    tfr_annual_raw = TFR_BASE + TFR_INFL_SHARE * infl

    def tfr_rates(shift: float) -> np.ndarray:
        # la rivalutazione non puo' essere negativa: floor a 0
        annual = np.maximum(tfr_annual_raw + shift, 0.0)
        # il tasso annuo si distribuisce sui 12 mesi (variazione anno su anno,
        # niente tremolio infra-annuale: e' un indice, non un mercato)
        return np.repeat((1.0 + annual) ** (1.0 / 12.0) - 1.0, 12)

    azienda, c_tfr = _pin_terminal(tfr_rates, contrib_m, targets["azienda"])
    tfr_annual_final = np.maximum(tfr_annual_raw + c_tfr, 0.0)

    # ---- Fondo azionario: rumore mensile iid ---- #
    eq_shocks = rng.normal(0.0, EQ_SIGMA / np.sqrt(12.0), MESI)

    def eq_rates(shift: float) -> np.ndarray:
        mu_m = (1.0 + EQ_MEAN + shift) ** (1.0 / 12.0) - 1.0
        return mu_m + eq_shocks

    azionario, c_eq = _pin_terminal(eq_rates, contrib_m, targets["azionario"])

    idx = pd.date_range(START, periods=MESI, freq="ME")
    df = pd.DataFrame({"azienda": azienda, "azionario": azionario}, index=idx)
    df.index.name = "date"

    diag = {
        "targets": targets,
        "shift_tfr_pp": c_tfr * 100,
        "shift_eq_pp": c_eq * 100,
        "tfr_rate_min": tfr_annual_final.min() * 100,
        "tfr_rate_max": tfr_annual_final.max() * 100,
        "tfr_rate_mean": tfr_annual_final.mean() * 100,
        "tfr_rate_std": tfr_annual_final.std(ddof=1) * 100,
        "eq_annual_std": (EQ_SIGMA * 100),
    }
    return df, diag


def main() -> None:
    df, diag = build_curves()
    csv_path = CHARTS / "equity_curves_reel_v2.csv"
    df.to_csv(csv_path)

    t = diag["targets"]
    print("--- Diagnostica curve v2 ---")
    print(f"TFR: rivalutazione annua  media {diag['tfr_rate_mean']:.2f}%  "
          f"std {diag['tfr_rate_std']:.2f} pp  range {diag['tfr_rate_min']:.2f}%-"
          f"{diag['tfr_rate_max']:.2f}%  (shift pinning {diag['shift_tfr_pp']:+.3f} pp)")
    print(f"Azionario: sigma {diag['eq_annual_std']:.0f}% annuo  "
          f"(shift pinning {diag['shift_eq_pp']:+.3f} pp)")
    print(f"Montante finale azienda   {df['azienda'].iloc[-1]:,.2f} "
          f"(target {t['azienda']:,.2f})")
    print(f"Montante finale azionario {df['azionario'].iloc[-1]:,.2f} "
          f"(target {t['azionario']:,.2f})")
    print(f"CSV -> {csv_path}")

    out = generate_reel(
        csv_path=csv_path,
        out_path=SOCIAL / "reel_animato_v2.mp4",
        columns=["azienda", "azionario"],
        labels=["TFR in azienda", "TFR nel fondo (azionario)"],
        title="Dove finisce il tuo TFR?",
        subtitle="Stesso versamento, 30 anni di lavoro",
        duration_seconds=15,
        log_scale=False,
        elapsed=True,
        fps=60,
        smooth=True,
    )
    print(f"Reel -> {out}")


if __name__ == "__main__":
    main()
