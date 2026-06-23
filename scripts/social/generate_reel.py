"""
SmartMoneyLab — Generatore di reel animati per Instagram
=========================================================

Genera un reel verticale 9:16 (1080×1920) animato a partire da un CSV di
equity curve. Le curve crescono frame-by-frame da sinistra a destra,
con titolo, etichette finali e watermark SmartMoneyLab.

Pensato come template riusabile su tutti gli articoli del blog (Tipo A
"test di strategia", Tipo B "curiosità data-driven", Tipo C "test di
portafogli reali"). Ogni articolo produce un equity_curves_*.csv:
puntando questo script al CSV giusto otteniamo il reel in pochi secondi.

Dipendenze:
- matplotlib (per FuncAnimation)
- pandas (per leggere il CSV)
- ffmpeg installato sul sistema (per export MP4)
  Windows: winget install ffmpeg  oppure  https://www.gyan.dev/ffmpeg/builds/
  Mac:     brew install ffmpeg
  Linux:   apt install ffmpeg
- Fallback automatico a GIF tramite Pillow se ffmpeg non e' disponibile.

Uso da linea di comando:
  python scripts/social/generate_reel.py \\
    --csv public/charts/<slug>/equity_curves_full.csv \\
    --slug <slug> \\
    --title "Una strategia LEAPS batte il mercato?" \\
    --columns leaps_nav,bh_nav \\
    --labels "Strategia LEAPS,Buy & Hold S&P 500" \\
    --duration 15

Uso programmatico (vedi la sezione __main__ dello script):
  from generate_reel import generate_reel
  generate_reel(
      csv_path="public/charts/strategia-leaps-vs-buy-and-hold/equity_curve_full.csv",
      out_path="social/strategia-leaps-vs-buy-and-hold/reel_animato.mp4",
      columns=["leaps_nav", "bh_nav"],
      labels=["Strategia LEAPS 70/30", "Buy & Hold S&P 500"],
      title="Una strategia LEAPS batte il mercato?",
      subtitle="49 anni di backtest, 1977-2025",
      duration_seconds=15,
  )

Autore: SmartMoneyLab — 2026.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

# Reel Instagram: 9:16 verticale @ 30fps
WIDTH_PX = 1080
HEIGHT_PX = 1920
FPS = 30
DPI = 100  # 10.8 x 19.2 inches @ 100 dpi = 1080 x 1920

# Palette SmartMoneyLab — versione per BG royal blue (slide IG SML)
# Tutti i colori scelti per garantire buon contrasto su royal blue
# #1e40af, evitando ROSSO (semantica "perdita" in finanza) e NERO
# (contrasto insufficiente). Il navy SML #1e3a8a sparirebbe sullo sfondo
# blu, quindi NON usarlo come colore curva nel reel.
# Palette estesa a 8 colori (decisione 2026-06-14) per supportare
# articoli con molte curve simultanee.
COLORS = [
    "#fbbf24",   # ambra brillante (strategia / portafoglio testato)
    "#ffffff",   # bianco (benchmark principale)
    "#86efac",   # verde lime
    "#fda4af",   # rosa
    "#fde047",   # giallo limone (piu' freddo dell'ambra)
    "#c4b5fd",   # lavanda (viola chiaro)
    "#fb923c",   # arancione acceso (Tailwind orange-400)
    "#9a3412",   # marrone bruciato (Tailwind orange-800, terra di Siena)
]

# Background royal blue tipico delle slide SmartMoneyLab
BG_COLOR = "#1e40af"        # royal blue (Tailwind blue-800)
FG_COLOR = "#ffffff"        # bianco puro
GRID_COLOR = "#ffffff"      # bianco con alpha basso (vedi sotto)
GRID_ALPHA = 0.15
WATERMARK_COLOR = "#dbeafe"  # bianco molto leggermente bluastro
LOGO_COLOR = "#ffffff"


def _format_eur(value: float) -> str:
    """Formatta un valore in euro 'pretty'."""
    if abs(value) >= 1_000_000:
        return f"€{value/1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"€{value/1_000:.0f}k"
    return f"€{value:.0f}"


def generate_reel(
    csv_path: str | Path,
    out_path: str | Path,
    columns: list[str],
    labels: list[str],
    title: str,
    subtitle: str = "",
    duration_seconds: int = 15,
    log_scale: bool = True,
    initial_capital: float | None = None,
    from_returns: bool = False,
    return_seed_value: float = 1000.0,
) -> Path:
    """
    Genera un reel animato MP4 (o GIF fallback) dal CSV.

    Parametri:
      csv_path:         path al CSV equity curve (prima colonna = Date)
      out_path:         path output (.mp4 o .gif)
      columns:          lista colonne del CSV da animare
      labels:           label da mostrare in legenda (stessa lunghezza di columns)
      title:            titolo principale del reel (1 riga)
      subtitle:         sottotitolo opzionale (1 riga, sotto titolo)
      duration_seconds: durata target del reel (default 15s)
      log_scale:        scala log su asse Y (default True, raccomandato per equity)
      initial_capital:  capitale iniziale per il "ticker numerico" (None = lo deduce)

    Restituisce il path effettivo del file generato.
    """
    csv_path = Path(csv_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if len(columns) != len(labels):
        raise ValueError("columns e labels devono avere stessa lunghezza")
    if len(columns) > len(COLORS):
        raise ValueError(f"Massimo {len(COLORS)} curve supportate")

    # ---- Carico il CSV ---- #
    df = pd.read_csv(csv_path, parse_dates=[0], index_col=0)
    df = df[columns].dropna()
    if len(df) == 0:
        raise ValueError("CSV vuoto dopo dropna sulle colonne richieste")

    # Se le colonne contengono rendimenti periodali (es. mensili) invece
    # di NAV cumulati, le converto cumulando da return_seed_value.
    if from_returns:
        nav = (1 + df).cumprod() * return_seed_value
        # Inserisco una riga "zero" coi seed iniziali per partire dal seed
        seed_row = pd.DataFrame({c: [return_seed_value] for c in df.columns},
                                 index=[df.index[0] - pd.DateOffset(months=1)])
        df = pd.concat([seed_row, nav]).sort_index()

    if initial_capital is None:
        initial_capital = float(df.iloc[0].max())

    # ---- Setup figura ---- #
    fig = plt.figure(figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI), dpi=DPI,
                      facecolor=BG_COLOR)
    # Forzo le dimensioni esatte per evitare arrotondamenti che cambiano
    # il rapporto 9:16 quando matplotlib genera i frame.
    fig.set_size_inches(WIDTH_PX / DPI, HEIGHT_PX / DPI, forward=True)
    # Layout: titolo in alto, grafico al centro, watermark in basso.
    # Lascio piu' margine a destra (era 5%, ora 14%) per ospitare le
    # etichette dei valori finali animati che seguono ogni curva.
    ax = fig.add_axes([0.10, 0.22, 0.76, 0.50])
    ax.set_facecolor(BG_COLOR)

    # Logo "SML" in alto a destra (come slide IG)
    fig.text(0.93, 0.96, "SML", ha="right", va="top",
             color=LOGO_COLOR, fontsize=44, fontweight="bold",
             family="DejaVu Sans")

    # Titolo + sottotitolo (testi statici)
    fig.text(0.5, 0.85, title, ha="center", va="top",
             color=FG_COLOR, fontsize=30, fontweight="bold",
             wrap=True)
    if subtitle:
        fig.text(0.5, 0.79, subtitle, ha="center", va="top",
                 color=WATERMARK_COLOR, fontsize=18, fontstyle="italic")

    # Watermark in basso, stile italic come la slide IG
    fig.text(0.5, 0.03, "SmartMoneyLab  →  smartmoneylab.pages.dev",
             ha="center", va="bottom", color=WATERMARK_COLOR,
             fontsize=15, fontstyle="italic")

    # Asse
    if log_scale:
        ax.set_yscale("log")
    ax.set_xlim(df.index[0], df.index[-1])
    # Margini Y piu' ampi (era 0.7/1.4, ora 0.55/1.8) per dare aria
    # alle etichette finali in alto e al pavimento in basso.
    y_min = max(df[columns].min().min() * 0.55, 1e-6)
    y_max = df[columns].max().max() * 1.8
    ax.set_ylim(y_min, y_max)
    ax.tick_params(colors=FG_COLOR, labelsize=13)
    for spine_name, spine in ax.spines.items():
        spine.set_visible(spine_name in ("left", "bottom"))
        spine.set_color(WATERMARK_COLOR)
        spine.set_alpha(0.7)
    ax.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.7,
            alpha=GRID_ALPHA)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _format_eur(v)))

    # Linee (vuote inizialmente). Spessore ridotto a 3.0 (era 4.5) per
    # un look piu' pulito sui 49 anni di dati.
    lines = []
    end_labels = []
    for i, col in enumerate(columns):
        line, = ax.plot([], [], color=COLORS[i], lw=3.0,
                        solid_capstyle="round", solid_joinstyle="round")
        lines.append(line)
        # Etichetta animata alla fine della curva (mostra NAV corrente)
        txt = ax.text(0, 0, "", color=COLORS[i], fontsize=15, fontweight="bold",
                      ha="left", va="center")
        end_labels.append(txt)

    # Legenda statica in basso al grafico
    handles = [plt.Line2D([], [], color=COLORS[i], lw=5, label=labels[i])
               for i in range(len(columns))]
    legend = ax.legend(handles=handles, loc="upper left",
                        facecolor=BG_COLOR, edgecolor=WATERMARK_COLOR,
                        labelcolor=FG_COLOR, fontsize=16, framealpha=0.0)
    for txt in legend.get_texts():
        txt.set_color(FG_COLOR)
    legend.get_frame().set_linewidth(0)

    # Anno corrente (sotto al sottotitolo, centrato sopra al grafico)
    year_txt = fig.text(0.5, 0.755, "", ha="center", va="top",
                         color=WATERMARK_COLOR, fontsize=22, fontweight="bold")

    # ---- Animation logic ---- #
    n_points = len(df)
    n_frames = duration_seconds * FPS
    # easing: un piccolo "intro" fermo + crescita lineare + "outro" fermo
    intro_frames = int(FPS * 0.5)
    outro_frames = int(FPS * 1.5)
    growth_frames = n_frames - intro_frames - outro_frames

    def points_at_frame(f: int) -> int:
        if f < intro_frames:
            return 1
        if f >= intro_frames + growth_frames:
            return n_points
        progress = (f - intro_frames) / growth_frames
        return max(1, int(progress * n_points))

    def animate(frame: int):
        k = points_at_frame(frame)
        x = df.index[:k]
        for i, col in enumerate(columns):
            y = df[col].values[:k]
            lines[i].set_data(x, y)
            # Etichetta al punto finale
            if len(y) > 0:
                end_labels[i].set_position((x[-1], y[-1]))
                end_labels[i].set_text(f"  {_format_eur(y[-1])}")
        # Anno corrente
        if len(x) > 0:
            year_txt.set_text(str(pd.Timestamp(x[-1]).year))
        return lines + end_labels + [year_txt]

    print(f"[reel] Generazione {n_frames} frame ({duration_seconds}s @ {FPS}fps)…")
    anim = animation.FuncAnimation(
        fig, animate, frames=n_frames, interval=1000 / FPS, blit=False,
    )

    # ---- Export ---- #
    ffmpeg_available = shutil.which("ffmpeg") is not None
    # savefig_kwargs forza dimensioni esatte 9:16 senza crop automatici
    # di matplotlib (bbox_inches='tight' implicito altrimenti puo' sballare
    # il rapporto del video finale).
    savefig_kwargs = {
        "facecolor": BG_COLOR,
        "bbox_inches": None,
        "pad_inches": 0,
    }

    if out_path.suffix.lower() == ".mp4" and ffmpeg_available:
        writer = animation.FFMpegWriter(
            fps=FPS, bitrate=4500,
            metadata={"artist": "SmartMoneyLab", "title": title},
            extra_args=["-pix_fmt", "yuv420p"],  # compat IG
        )
        print(f"[reel] Export MP4 via ffmpeg -> {out_path}")
        anim.save(str(out_path), writer=writer, dpi=DPI,
                  savefig_kwargs=savefig_kwargs)
    else:
        if out_path.suffix.lower() == ".mp4":
            print("[reel] ffmpeg non trovato, fallback a GIF (file piu' grande)")
            out_path = out_path.with_suffix(".gif")
        print(f"[reel] Export GIF via Pillow -> {out_path}")
        writer = animation.PillowWriter(fps=FPS)
        anim.save(str(out_path), writer=writer, dpi=DPI,
                  savefig_kwargs=savefig_kwargs)

    plt.close(fig)
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"[reel] Done. Size: {size_mb:.1f} MB")
    return out_path


# -------------------------------------------------------------------- #
# CLI                                                                  #
# -------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True, help="CSV equity curve")
    parser.add_argument("--slug", required=True,
                        help="Slug articolo, usato per il path output")
    parser.add_argument("--title", required=True, help="Titolo principale")
    parser.add_argument("--subtitle", default="", help="Sottotitolo opzionale")
    parser.add_argument("--columns", required=True,
                        help="Colonne del CSV, separate da virgola")
    parser.add_argument("--labels", required=True,
                        help="Label legenda, separate da virgola")
    parser.add_argument("--duration", type=int, default=15,
                        help="Durata in secondi (default 15)")
    parser.add_argument("--no-log", action="store_true",
                        help="Disabilita scala log Y")
    parser.add_argument("--from-returns", action="store_true",
                        help="Le colonne del CSV contengono rendimenti periodali, "
                             "non NAV cumulati. Lo script cumula partendo da "
                             "--seed (default 1000).")
    parser.add_argument("--seed", type=float, default=1000.0,
                        help="Valore iniziale del NAV cumulato (default 1000)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    out_dir = repo_root / "social" / args.slug
    out_path = out_dir / "reel_animato.mp4"

    generate_reel(
        csv_path=args.csv,
        out_path=out_path,
        columns=args.columns.split(","),
        labels=args.labels.split(","),
        title=args.title,
        subtitle=args.subtitle,
        duration_seconds=args.duration,
        log_scale=not args.no_log,
        from_returns=args.from_returns,
        return_seed_value=args.seed,
    )


if __name__ == "__main__":
    main()
