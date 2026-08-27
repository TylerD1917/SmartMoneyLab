"""
Genera le immagini di anteprima social (Open Graph) per ogni articolo.

Perche': `og:image` puntava a /og-default.png, che non esiste. Risultato: nessuna
anteprima su X, LinkedIn, WhatsApp, Telegram. Qui generiamo una card brandizzata
1200x630 (il formato che tutte le piattaforme si aspettano) per ciascun post.

Sorgente del grafico dentro la card, in ordine di priorita':
  1. il campo `seoImage` del frontmatter, se punta a un PNG in public/
  2. il primo grafico NN_*.png della cartella public/charts/<simulationSlug>/
  3. nessuno -> card solo testo, comunque brandizzata

Output: public/og/<slug-del-post>.png  +  public/og-default.png (fallback globale)

Rilanciare dopo ogni nuovo articolo:  python3 scripts/make_og_images.py
"""
import os, re, glob
from PIL import Image, ImageDraw, ImageFont
import matplotlib

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
POSTS = os.path.join(ROOT, "src", "content", "posts")
PUBLIC = os.path.join(ROOT, "public")
OUT = os.path.join(PUBLIC, "og"); os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
INK   = (15, 23, 42)      # slate-950, sfondo
NAVY  = (30, 58, 138)     # blue-900, badge
GOLD  = (251, 191, 36)    # amber-400, accento
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)

FONTDIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONTDIR, name), size)

def frontmatter(path):
    """Parser minimale: bastano title, simulationSlug e seoImage."""
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m: return {}
    fm, out = m.group(1), {}
    for key in ("title", "simulationSlug", "seoImage", "draft"):
        k = re.search(rf'^{key}:\s*"?([^"\n]+?)"?\s*$', fm, re.M)
        if k: out[key] = k.group(1).strip()
    return out

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        test = f"{cur} {w_}".strip()
        if draw.textlength(test, font=fnt) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def card(title, chart_path, dest):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    # barra d'accento a sinistra
    d.rectangle([0, 0, 10, H], fill=GOLD)

    # badge SML + nome sito
    d.rounded_rectangle([56, 48, 104, 96], radius=10, fill=NAVY)
    d.text((80, 72), "SML", font=font(19), fill=WHITE, anchor="mm")
    d.text((118, 72), "SmartMoneyLab", font=font(26), fill=WHITE, anchor="lm")

    # se c'e' un grafico, occupa la meta' destra; il testo sta a sinistra
    text_w = 1000
    if chart_path and os.path.exists(chart_path):
        box_w, box_h = 500, 400
        ch = Image.open(chart_path).convert("RGB")
        ch.thumbnail((box_w, box_h), Image.LANCZOS)
        panel = Image.new("RGB", (ch.width + 24, ch.height + 24), WHITE)
        panel.paste(ch, (12, 12))
        img.paste(panel, (W - panel.width - 56, (H - panel.height) // 2 + 20))
        text_w = W - panel.width - 150

    fnt = font(46)
    lines = wrap(d, title, fnt, text_w)
    if len(lines) > 4:                      # titolo lungo: rimpicciolisci
        fnt = font(38); lines = wrap(d, title, fnt, text_w)[:5]
    y = 150 + max(0, (4 - len(lines)) * 14)
    for ln in lines:
        d.text((56, y), ln, font=fnt, fill=WHITE)
        y += int(fnt.size * 1.32)

    d.text((56, H - 74), "smartmoneylab.it", font=font(22, bold=False), fill=GOLD)
    d.text((56, H - 44), "Finanza personale e analisi quantitativa, senza hype.",
           font=font(19, bold=False), fill=MUTED)
    img.save(dest, "PNG", optimize=True)

def pick_chart(fm):
    if fm.get("seoImage", "").endswith(".png"):
        p = os.path.join(PUBLIC, fm["seoImage"].lstrip("/"))
        if os.path.exists(p): return p
    slug = fm.get("simulationSlug")
    if slug:
        found = sorted(glob.glob(os.path.join(PUBLIC, "charts", slug, "[0-9][0-9]_*.png")))
        if found: return found[0]
    return None

n_chart = n_plain = 0
for path in sorted(glob.glob(os.path.join(POSTS, "*.md")) + glob.glob(os.path.join(POSTS, "*.mdx"))):
    fm = frontmatter(path)
    if not fm.get("title"): continue
    slug = os.path.splitext(os.path.basename(path))[0]
    chart = pick_chart(fm)
    card(fm["title"], chart, os.path.join(OUT, f"{slug}.png"))
    n_chart += chart is not None; n_plain += chart is None
    print(f"  {slug:44s} {'grafico: ' + os.path.basename(chart) if chart else 'solo testo'}")

# fallback globale, usato dalle pagine che non sono articoli
card("Finanza personale e analisi quantitativa, senza hype.", None,
     os.path.join(PUBLIC, "og-default.png"))

print(f"\n[ok] {n_chart + n_plain} card in public/og/ ({n_chart} con grafico, {n_plain} solo testo)")
print("[ok] public/og-default.png")
