# -*- coding: utf-8 -*-
"""
Reel Instagram — la regola del 2 x duration + simulatore
========================================================

Non e' un chart race: qui non c'e' una serie storica che scorre, c'e' un
NUMERO che si sblocca. La struttura e' in quattro atti:

  1. gancio      il rendimento a scadenza di un ETF vero, e la domanda
  2. contatore   gli anni di detenzione salgono, la quota di casi azzeccati
                 sale con loro (dati veri, dal JSON del simulatore)
  3. rivelazione il massimo cade dove la teoria dice: 2 x duration
  4. strumento   il simulatore fa il conto per l'ETF di chi guarda

Ogni fotogramma viene ridisegnato da zero: il reel dura 18 secondi, sono
540 frame, e la figura e' fatta di una ventina di testi. Ridisegnare costa
meno che tenere in vita artisti con visibilita' alternata.

Uso:  python scripts/social/reel_regola_2x_duration.py
Out:  social/regola-2x-duration/reel_2x_duration.mp4
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.patches import FancyBboxPatch

W, H, DPI, FPS = 1080, 1920, 100, 60

# zoom appena percettibile sui testi che entrano: a 60 fps le dissolvenze
# secche si vedono, una scala che accompagna l'opacita' le ammorbidisce.
_SCALA = 1.0

BG = "#1e40af"          # royal blue delle slide SML
FG = "#ffffff"
SOFT = "#dbeafe"        # bianco bluastro, per i testi di servizio
AMBRA = "#fbbf24"
LIME = "#86efac"
VETRO = "#1d4ed8"       # blu piu' chiaro, per i pannelli

# Gamba scelta: l'area euro e' in euro (niente cambio da spiegare in 19
# secondi) e soprattutto il suo massimo storico cade a 14 anni contro i 14,2
# previsti dalla regola. Sulla gamba americana il massimo della stessa misura
# cade a 12 contro 13,5.
GAMBA = "euro-7-10"
METRICA = "entro2"              # entro2 = risultato entro 2 punti dal rendimento iniziale
SOGLIA = 90.0                   # oltre questa quota la barra passa al verde
ANNI_MIN, ANNI_MAX = 5, 14      # il contatore si ferma sul massimo storico

# Battute, in secondi
T_GANCIO = 3.2
T_CONTATORE = 7.8
T_RIVELAZIONE = 4.4
T_STRUMENTO = 3.6
DURATA = T_GANCIO + T_CONTATORE + T_RIVELAZIONE + T_STRUMENTO


def it(x, d=1):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def smooth(x):
    """Rampa 0->1 con partenza e arrivo morbidi."""
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def dentro(t, t0, t1, salita=0.35, discesa=0.35):
    """Opacita' di un elemento che compare a t0 e sparisce a t1."""
    if t < t0 or t > t1:
        return 0.0
    a = smooth((t - t0) / salita) if salita else 1.0
    b = smooth((t1 - t) / discesa) if discesa else 1.0
    return min(a, b)


def testo(fig, x, y, s, size, color=FG, alpha=1.0, weight="bold",
          ha="center", va="center", style="normal"):
    if alpha <= 0.01:
        return None
    return fig.text(x, y, s, ha=ha, va=va, color=color, fontsize=size * _SCALA,
                    fontweight=weight, alpha=min(alpha, 1.0), fontstyle=style,
                    family="DejaVu Sans")


def scala(entrata):
    """Da 0,985 a 1: il testo si assesta mentre compare."""
    global _SCALA
    _SCALA = 0.985 + 0.015 * smooth(entrata)


def pannello(fig, x, y, w, h, alpha, color=VETRO, bordo=None):
    if alpha <= 0.01:
        return
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.018",
                       transform=fig.transFigure, facecolor=color,
                       edgecolor=bordo or color, linewidth=2.5 if bordo else 0,
                       alpha=min(alpha, 1.0), zorder=0)
    fig.patches.append(p)


def cornice(fig, t, dati):
    """Disegna il fotogramma al tempo t. La figura arriva gia' pulita."""
    ytm, serie, duration = dati["ytm"], dati["serie"], dati["duration"]
    orizzonte = 2 * duration - 1 / 12

    # --- costanti di scena
    t1 = T_GANCIO
    t2 = t1 + T_CONTATORE
    t3 = t2 + T_RIVELAZIONE

    # ---------------------------------------------------------- 1. gancio
    if t < t1 + 0.4:
        a = dentro(t, 0, t1 + 0.4, 0.55, 0.45)
        scala(min(t / 0.55, 1.0))
        testo(fig, 0.5, 0.70, "Il tuo ETF obbligazionario dice", 34, SOFT, a, "normal")
        testo(fig, 0.5, 0.565, f"{it(ytm, 2)}%", 170, AMBRA, a)
        testo(fig, 0.5, 0.465, "rendimento a scadenza", 28, SOFT, a, "normal", style="italic")
        b = dentro(t, 1.5, t1 + 0.4, 0.5, 0.4)
        testo(fig, 0.5, 0.33, "Quando lo incassi", 44, FG, b)
        testo(fig, 0.5, 0.27, "davvero?", 44, AMBRA, b)

    # ------------------------------------------------------- 2. contatore
    if t1 - 0.1 < t < t2:
        a = dentro(t, t1 - 0.1, t2, 0.55, 0.4)
        scala(min((t - (t1 - 0.1)) / 0.55, 1.0))
        # avanzamento continuo fra gli anni interi
        q = smooth((t - (t1 + 0.5)) / (T_CONTATORE - 1.2)) if t > t1 + 0.5 else 0.0
        # la corsa arriva poco oltre l'ultimo anno, se no la cifra finale
        # resta a meta' strada fra il penultimo valore e il suo
        pos = ANNI_MIN + q * (ANNI_MAX - ANNI_MIN + 0.45)
        grezzo = int(np.floor(pos + 1e-9))
        anni = min(grezzo, ANNI_MAX)
        frazione = min(pos - grezzo, 1.0)
        i = min(max(anni - ANNI_MIN, 0), len(serie) - 1)
        prec = serie[max(i - 1, 0)]
        tween = smooth(min(frazione / 0.3, 1.0)) if i > 0 else 1.0
        val = prec + (serie[i] - prec) * tween
        colore = LIME if val >= SOGLIA else AMBRA

        testo(fig, 0.5, 0.875, f"{dati['etichetta']}, comprato al {it(ytm, 2)}%",
              26, SOFT, a, "normal")
        testo(fig, 0.5, 0.80, "SE LO TIENI", 30, SOFT, a)
        testo(fig, 0.5, 0.705, f"{anni} anni", 130, FG, a)

        testo(fig, 0.5, 0.565, "ci prende nel", 30, SOFT, a, "normal")
        testo(fig, 0.5, 0.465, f"{it(val)}%", 150, colore, a)
        testo(fig, 0.5, 0.355, "dei casi storici il risultato è finito", 24, SOFT, a, "normal")
        testo(fig, 0.5, 0.315, f"{dati['tolleranza']} da quel {it(ytm, 2)}%", 24, SOFT, a, "normal")

        # barra di avanzamento
        if a > 0.02:
            x0, y0, lung, alt = 0.12, 0.21, 0.76, 0.042
            pannello(fig, x0, y0, lung, alt, a * 0.22, "#ffffff")
            pannello(fig, x0, y0, lung * val / 100, alt, a, colore)
            # tacca della soglia: sopra il 60% la stima comincia a reggere
            soglia = FancyBboxPatch((x0 + lung * SOGLIA / 100 - 0.0018, y0 - 0.009), 0.0036,
                                    alt + 0.018, boxstyle="square,pad=0",
                                    transform=fig.transFigure, facecolor="#ffffff",
                                    edgecolor="none", alpha=min(a * 0.5, 1.0), zorder=1)
            fig.patches.append(soglia)

    # ----------------------------------------------------- 3. rivelazione
    if t2 <= t < t3:
        a = dentro(t, t2, t3, 0.55, 0.4)
        scala(min((t - t2) / 0.55, 1.0))
        testo(fig, 0.5, 0.86, "Il massimo storico cade a", 30, SOFT, a, "normal")
        testo(fig, 0.5, 0.775, f"{ANNI_MAX} anni", 90, LIME, a)

        b = dentro(t, t2 + 0.6, t3, 0.5, 0.45)
        testo(fig, 0.5, 0.645, "Non è un caso.", 46, FG, b)

        c = dentro(t, t2 + 1.2, t3, 0.5, 0.45)
        if c > 0.02:
            pannello(fig, 0.085, 0.40, 0.83, 0.175, c * 0.55, VETRO)
            testo(fig, 0.5, 0.535, "duration del fondo  ×  2", 26, SOFT, c, "normal")
            testo(fig, 0.5, 0.455, f"{it(duration)}  ×  2  =  {it(orizzonte)} anni",
                  46, AMBRA, c)

        d = dentro(t, t2 + 1.8, t3, 0.5, 0.45)
        testo(fig, 0.5, 0.315, "Un ETF obbligazionario mantiene", 32, FG, d, "normal")
        testo(fig, 0.5, 0.265, "la promessa al doppio", 32, FG, d, "normal")
        testo(fig, 0.5, 0.215, "della sua duration", 32, AMBRA, d)

    # ------------------------------------------------------- 4. strumento
    if t >= t3:
        a = dentro(t, t3, DURATA + 1, 0.55, 0.0)
        scala(min((t - t3) / 0.55, 1.0))
        testo(fig, 0.5, 0.86, "E il TUO ETF?", 52, FG, a)
        testo(fig, 0.5, 0.795, "duration e rendimento sono nella scheda del fondo", 24, SOFT, a, "normal")

        # mini grafico dell'affidabilita', come nello strumento
        b = dentro(t, t3 + 0.3, DURATA + 1, 0.6, 0.0)
        if b > 0.02:
            ax = fig.add_axes([0.13, 0.40, 0.74, 0.27])
            ax.set_facecolor(BG)
            for s in ax.spines.values():
                s.set_visible(False)
            ax.set_xticks([]); ax.set_yticks([])
            tutte = dati["serie_completa"]
            xs = np.arange(len(tutte))
            quota = smooth(min((t - (t3 + 0.3)) / 1.0, 1.0))
            colori = [LIME if v >= SOGLIA else AMBRA for v in tutte]
            ax.bar(xs, np.array(tutte) * quota, width=0.74, color=colori, alpha=b)
            ax.axvline(orizzonte - dati["anni_completi"][0], color=FG, alpha=b * 0.8,
                       linewidth=2.5, linestyle=(0, (5, 3)), ymin=0, ymax=0.70)
            ax.text(orizzonte - dati["anni_completi"][0], max(tutte) * 1.08,
                    "2 × duration", ha="center", va="bottom", color=FG,
                    fontsize=19, fontweight="bold", alpha=b)
            ax.set_xlim(-0.8, len(tutte) - 0.2)
            ax.set_ylim(0, max(tutte) * 1.42)
            for k, lab in ((0, "5 anni"), (len(tutte) - 1, "20 anni")):
                ax.text(k, -max(tutte) * 0.08, lab, ha="center", va="top",
                        color=SOFT, fontsize=19, alpha=b)
            fig.text(0.5, 0.695, "quanto è affidabile, anno per anno", ha="center",
                     va="center", color=SOFT, fontsize=22, alpha=b,
                     fontstyle="italic", family="DejaVu Sans")

        c = dentro(t, t3 + 1.0, DURATA + 1, 0.5, 0.0)
        if c > 0.02:
            pannello(fig, 0.17, 0.215, 0.66, 0.095, c, AMBRA)
            testo(fig, 0.5, 0.2625, "Simulatore gratuito", 38, "#1e3a8a", c)
        testo(fig, 0.5, 0.155, "link in bio", 30, SOFT, c, "normal", style="italic")

    # ------------------------------------------------------------- fissi
    globals()["_SCALA"] = 1.0
    fig.text(0.93, 0.955, "SML", ha="right", va="top", color=FG,
             fontsize=44, fontweight="bold", family="DejaVu Sans")
    fig.text(0.5, 0.035, "SmartMoneyLab  →  smartmoneylab.it", ha="center",
             va="bottom", color=SOFT, fontsize=18, fontstyle="italic",
             family="DejaVu Sans")


def carica(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    g = [x for x in j["gambe"] if x["id"] == GAMBA][0]
    per_anno = {o["anni"]: o[METRICA] for o in g["orizzonti"]}
    anni = sorted(per_anno)
    # duration al rendimento di riferimento, con la stessa formula dello studio
    y = g["rendimento"]["valore"] / 100
    m = g["scadenza_modellata"]

    def prezzo(yy):
        n = round(m * 2); c = y / 2 * 100
        return sum(c / (1 + yy / 2) ** i for i in range(1, n + 1)) + 100 / (1 + yy / 2) ** n

    h = 1e-5
    d = (prezzo(y - h) - prezzo(y + h)) / (2 * h) / prezzo(y)
    return {
        "etichetta": g["nome"].replace(" anni", ""),
        "tolleranza": "entro 2 punti" if METRICA == "entro2" else "entro 1 punto",
        "ytm": g["rendimento"]["valore"],
        "duration": d,
        "serie": [per_anno[a] for a in range(ANNI_MIN, ANNI_MAX + 1)],
        "serie_completa": [per_anno[a] for a in anni],
        "anni_completi": anni,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "public", "tools", "etf-obbligazionari-rendimenti.json"))
    ap.add_argument("--out", default="reel_2x_duration.mp4")
    ap.add_argument("--anteprime", default="", help="secondi separati da virgola: salva PNG e basta")
    a = ap.parse_args()

    dati = carica(a.json)
    print(f"[reel] ytm {dati['ytm']}  duration {dati['duration']:.2f}  "
          f"2D {2 * dati['duration'] - 1/12:.1f}  serie {dati['serie']}")

    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)

    def disegna(t):
        fig.clear()
        fig.patches.clear()
        fig.set_facecolor(BG)
        cornice(fig, t, dati)

    if a.anteprime:
        for s in [float(x) for x in a.anteprime.split(",")]:
            disegna(s)
            # le anteprime finiscono accanto al video, non nella radice del repo
            nome = os.path.join(os.path.dirname(os.path.abspath(a.out)) or ".",
                                f"anteprima_{s:0.1f}.png")
            fig.savefig(nome, facecolor=BG, pad_inches=0)
            print("  anteprima", s)
        return

    n = int(DURATA * FPS)
    writer = animation.FFMpegWriter(
        fps=FPS, bitrate=5200, metadata={"artist": "SmartMoneyLab"},
        extra_args=["-pix_fmt", "yuv420p"])
    with writer.saving(fig, a.out, DPI):
        for k in range(n):
            disegna(k / FPS)
            writer.grab_frame(facecolor=BG, pad_inches=0)
            if k % 60 == 0:
                print(f"  frame {k}/{n}")
    print(f"[reel] fatto: {a.out}  "
          f"{os.path.getsize(a.out) / 1024 / 1024:.1f} MB, {DURATA:.1f}s")


if __name__ == "__main__":
    main()
