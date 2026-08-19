"""
SmartMoneyLab - Generatore di caroselli Instagram (PNG 1080x1350)
==================================================================

Trasforma un file di contenuto (JSON) in slide PNG pronte per Instagram,
nello stile-brand SmartMoneyLab: sfondo navy #1e3a8a, logo SML in alto a
destra, footer, accento oro #fbbf24 su numeri e concetti chiave.

Filosofia (decisa con Tyler 2026-08-06 dopo analisi dei caroselli Canva):
- UN numero/concetto protagonista per slide, non paragrafi fitti.
- Testo allineato a sinistra, mai giustificato. Auto-a-capo automatico.
- Grafici veri incorniciati in card bianca.
- Italiano semplice, pochi tecnicismi/anglismi.
- Oro per far risaltare la frase-chiave.
- Ogni tanto una slide-numero a sfondo CHIARO per spezzare il ritmo.
- Lunghezza 6-8 slide.

Tipi di slide supportati (campo "type"):
  cover        - copertina: titolo (ultima riga in oro) + sottotitolo
  number       - numero gigante su navy + riquadro frase-chiave
  number_light - come number ma sfondo chiaro (per spezzare il ritmo)
  chart        - grafico PNG incorniciato in card bianca + didascalia
  compare      - due numeri a contrasto + frase punchline
  bullets      - titolo + elenco puntato breve
  cta          - chiusura: titolo + 3 righe + pulsante "Link in bio"

USO:
  1. Scrivi social/<slug>/carosello_spec.json (vedi esempio in fondo).
  2. python scripts/social/generate_carousel.py --slug <slug>
  3. I PNG numerati finiscono in social/<slug>/carosello/01.png, 02.png, ...

Dipendenze: pip install cairosvg pillow
Autore: SmartMoneyLab - 2026.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from xml.sax.saxutils import escape

import cairosvg
from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent

# -------- palette brand: SOLO bianco, blu, oro --------
NAVY = "#1e3a8a"
NAVY_BOX = "#172554"
AMBER = "#fbbf24"        # oro (usato su sfondo navy, dove ha buon contrasto)
WHITE = "#ffffff"
FOOTER_WHITE = "#eef2ff"  # bianco acceso per il footer (non "trasparente")
MUTE = "#c7d2fe"         # azzurrino tenue su navy (famiglia blu)
LIGHT = "#f8fafc"
SLATE = "#334155"
GREY_NUM = "#6b7fb8"     # numero "secondario" nel confronto (blu desaturato)

W, H = 1080, 1350
MARGIN = 80
CONTENT_W = W - 2 * MARGIN

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_FAMILY = "DejaVu Sans"

_font_cache: dict = {}


def _font(bold: bool, size: int):
    key = (bold, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _font_cache[key]


def wrap(text: str, size: int, bold: bool, max_w: int = CONTENT_W) -> list[str]:
    """Auto-a-capo: spezza il testo in righe che stanno entro max_w px."""
    font = _font(bold, size)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def T(x, y, s, size, fill, bold=False, anchor="start", italic=False):
    style = f' font-style="italic"' if italic else ""
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT_FAMILY}" font-size="{size}" '
            f'fill="{fill}"{weight}{style} text-anchor="{anchor}">{escape(s)}</text>')


def logo(dark_bg=True):
    c = WHITE if dark_bg else NAVY
    return T(W - MARGIN, 108, "SML", 52, c, bold=True, anchor="end")


def footer(dark_bg=True):
    c = FOOTER_WHITE if dark_bg else NAVY
    return (f'<text x="{W/2}" y="1300" font-family="{FONT_FAMILY}" font-size="26" '
            f'fill="{c}" font-style="italic" text-anchor="middle">'
            f'SmartMoneyLab  →  smartmoneylab.it</text>')


def dots(current: int, total: int, light: bool):
    """Pallini di avanzamento in alto a sinistra: primi `current` pieni."""
    r, gap, y = 9, 32, 96
    x0 = MARGIN + r
    filled = NAVY if light else AMBER
    stroke = NAVY if light else WHITE
    out = []
    for i in range(total):
        cx = x0 + i * gap
        if i < current:
            out.append(f'<circle cx="{cx}" cy="{y}" r="{r}" fill="{filled}"/>')
        else:
            out.append(f'<circle cx="{cx}" cy="{y}" r="{r}" fill="none" '
                       f'stroke="{stroke}" stroke-width="2.5" opacity="0.55"/>')
    return "".join(out)


def bg(color):
    return f'<rect width="{W}" height="{H}" fill="{color}"/>'


def _lines_block(lines, x, y0, size, fill, bold=False, lh=None):
    lh = lh or int(size * 1.25)
    out = []
    for i, ln in enumerate(lines):
        out.append(T(x, y0 + i * lh, ln, size, fill, bold=bold))
    return "".join(out), y0 + len(lines) * lh


# -------------------------------------------------------------------- #
# Renderer per tipo                                                    #
# -------------------------------------------------------------------- #
def render_cover(s):
    title = s["title"] if isinstance(s["title"], list) else wrap(s["title"], 80, True)
    accent = set(s.get("accent_lines", [len(title) - 1]))
    parts = [bg(NAVY), logo(), footer()]
    y = 560 - (len(title) - 2) * 45
    for i, ln in enumerate(title):
        parts.append(T(MARGIN, y, ln, 80, AMBER if i in accent else WHITE, bold=True))
        y += 100
    parts.append(f'<rect x="{MARGIN}" y="{y-42}" width="130" height="9" fill="{AMBER}"/>')
    if s.get("subtitle"):
        sub = wrap(s["subtitle"], 38, False)
        blk, _ = _lines_block(sub, MARGIN, y + 70, 38, MUTE)
        parts.append(blk)
    return "".join(parts)


def render_number(s, light=False):
    # Palette coerente: su sfondo chiaro il numero e' BLU (l'oro su bianco
    # non ha contrasto). La frase-chiave sta comunque in un riquadro navy,
    # dove l'oro risalta. Nessun arancio.
    bgc = LIGHT if light else NAVY
    kicker_c = NAVY if light else MUTE
    num_c = NAVY if light else AMBER
    note_c = SLATE if light else WHITE
    parts = [bg(bgc), logo(dark_bg=not light), footer(dark_bg=not light)]
    if light:
        parts.append(f'<rect x="0" y="0" width="16" height="{H}" fill="{AMBER}"/>')  # barra oro
    y = 330
    if s.get("kicker"):
        kl = wrap(s["kicker"], 46, False)
        blk, y = _lines_block(kl, MARGIN, y, 46, kicker_c)
        parts.append(blk)
        y += 40
    parts.append(T(MARGIN - 10, y + 250, s["number"], 300, num_c, bold=True))
    y += 340
    if s.get("note"):
        parts.append(T(MARGIN, y, s["note"], 40, note_c))
        y += 70
    if s.get("box"):
        box = s["box"] if isinstance(s["box"], list) else wrap(s["box"], 40, True)
        boxh = 60 + len(box) * 55
        by = 1120 - boxh
        # riquadro navy sempre (anche su slide chiara): l'oro ci sta bene sopra
        parts.append(f'<rect x="{MARGIN}" y="{by}" width="{CONTENT_W}" height="{boxh}" rx="24" fill="{NAVY_BOX}"/>')
        ty = by + 62
        accent = set(s.get("box_accent", [len(box) - 1]))
        for i, ln in enumerate(box):
            col = AMBER if i in accent else WHITE
            parts.append(T(MARGIN + 40, ty, ln, 40, col, bold=True))
            ty += 55
    return "".join(parts)


def render_chart(s):
    parts = [bg(NAVY), logo(), footer()]
    title = s["title"] if isinstance(s["title"], list) else wrap(s["title"], 52, True)
    blk, y = _lines_block(title, MARGIN, 220, 52, WHITE, bold=True)
    parts.append(blk)
    y += 20
    card_y, card_h = y, 1080 - y - (80 if s.get("caption") else 0)
    parts.append(f'<rect x="70" y="{card_y}" width="940" height="{card_h}" rx="20" fill="{WHITE}"/>')
    chart_path = ROOT / s["chart"]
    b64 = base64.b64encode(chart_path.read_bytes()).decode()
    parts.append(f'<image x="90" y="{card_y+20}" width="900" height="{card_h-40}" '
                 f'href="data:image/png;base64,{b64}" preserveAspectRatio="xMidYMid meet"/>')
    if s.get("caption"):
        parts.append(T(MARGIN, card_y + card_h + 55, s["caption"], 38, AMBER))
    return "".join(parts)


def render_compare(s):
    parts = [bg(NAVY), logo(), footer()]
    y = 330
    if s.get("kicker"):
        parts.append(T(MARGIN, y, s["kicker"], 44, MUTE))
        y += 210
    L, R = s["left"], s["right"]
    parts.append(T(MARGIN, y, L["num"], 150, WHITE, bold=True))
    parts.append(T(560, y, R["num"], 150, GREY_NUM, bold=True))
    parts.append(T(MARGIN, y + 60, L["label"], 34, MUTE))
    parts.append(T(560, y + 60, R["label"], 34, MUTE))
    ly = y + 160
    parts.append(f'<line x1="{MARGIN}" y1="{ly}" x2="{W-MARGIN}" y2="{ly}" stroke="#3b4d80" stroke-width="2"/>')
    punch = s["punch"] if isinstance(s["punch"], list) else wrap(s["punch"], 56, True)
    accent = set(s.get("punch_accent", [0]))
    py = ly + 140
    for i, ln in enumerate(punch):
        parts.append(T(MARGIN, py, ln, 56, AMBER if i in accent else WHITE, bold=True))
        py += 75
    return "".join(parts)


def render_bullets(s):
    parts = [bg(NAVY), logo(), footer()]
    title = s["title"] if isinstance(s["title"], list) else wrap(s["title"], 52, True)
    blk, y = _lines_block(title, MARGIN, 240, 52, WHITE, bold=True)
    parts.append(blk)
    y += 70
    for b in s["bullets"]:
        blines = wrap(b, 40, False, CONTENT_W - 50)
        parts.append(T(MARGIN, y, "•", 40, AMBER, bold=True))
        for j, ln in enumerate(blines):
            parts.append(T(MARGIN + 50, y, ln, 40, MUTE))
            y += 55
        y += 20
    return "".join(parts)


def render_cta(s):
    parts = [bg(NAVY), logo(), footer()]
    title = s["title"] if isinstance(s["title"], list) else wrap(s["title"], 60, True)
    blk, y = _lines_block(title, MARGIN, 440 - (len(title) - 2) * 40, 60, WHITE, bold=True)
    parts.append(blk)
    y += 70
    for b in s.get("bullets", []):
        parts.append(T(MARGIN, y, "•  " + b, 40, MUTE))
        y += 65
    y += 60
    btn = s.get("button", "Link in bio →")
    bw = _font(True, 38).getlength(btn) + 80
    parts.append(f'<rect x="{MARGIN}" y="{y}" width="{bw}" height="90" rx="45" fill="{AMBER}"/>')
    parts.append(T(MARGIN + bw / 2, y + 58, btn, 38, NAVY, bold=True, anchor="middle"))
    if s.get("handle"):
        parts.append(T(MARGIN, y + 180, s["handle"], 30, MUTE, italic=True))
    return "".join(parts)


RENDERERS = {
    "cover": render_cover,
    "number": lambda s: render_number(s, light=False),
    "number_light": lambda s: render_number(s, light=True),
    "chart": render_chart,
    "compare": render_compare,
    "bullets": render_bullets,
    "cta": render_cta,
}


def build(slug: str):
    spec_path = ROOT / "social" / slug / "carosello_spec.json"
    if not spec_path.exists():
        raise SystemExit(f"Manca lo spec: {spec_path}")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = ROOT / "social" / slug / "carosello"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(spec["slides"])
    for i, s in enumerate(spec["slides"], start=1):
        body = RENDERERS[s["type"]](s)
        prog = dots(i, total, light=(s["type"] == "number_light"))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">' \
              + body + prog + "</svg>"
        out = out_dir / f"{i:02d}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out),
                         output_width=W, output_height=H)
        print(f"  [{i:02d}] {s['type']:<13} -> {out.name}")
    print(f"\n[ok] {len(spec['slides'])} slide in {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="slug articolo (cartella in social/)")
    build(ap.parse_args().slug)


if __name__ == "__main__":
    main()
