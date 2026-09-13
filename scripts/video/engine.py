#!/usr/bin/env python3
"""
SmartMoneyLab — motore video "faceless" data-viz (config-driven, riusabile).

Non si usa direttamente: lo chiama build_video.py. Ogni articolo con un video ha
una config in configs/<slug>.py (opt-in: nessuna config = nessun video).

Tipi di scena supportati (campo "type"):
  cover          - title card d'apertura (+ sparkline fisso/variabile opzionale)
  chart_side     - grafico reale a sinistra + annotazioni a destra (no overlay!)
  stats          - grandi numeri (con count-up) + inset grafico opzionale
  risk_bars      - stat % + barre "shock" (a -> b, +X%)
  transform_chart- "A% -> B%" (count-up) poi crossfade su un grafico
  rates_today    - due chip tasso a confronto + badge + riga count-up + CTA
  outro          - card brand finale (logo, tagline, handle, disclaimer)

Regola d'oro imparata sul campo: MAI sovrapporre testo ai grafici dell'articolo
(hanno gia' titolo+legenda) -> per i grafici usa sempre chart_side / inset.
"""
import os, math, json, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 24

# ---------------- brand ----------------
PAL = {
    "bg": (248, 250, 252), "ink": (23, 37, 64), "muted": (100, 116, 139),
    "navy": (30, 58, 138), "gold": (245, 175, 25), "amber": (202, 110, 10),
    "card": (255, 255, 255), "line": (226, 232, 240), "white": (255, 255, 255),
}
TAGLINE = "Finanza personale e analisi quantitativa"
HANDLE = "@smartmoneylab_it"
DISCLAIMER = "Contenuto informativo, non consulenza finanziaria."
FSERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FSANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FSANSB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
def C(name):
    return PAL.get(name, name) if isinstance(name, str) else tuple(name)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def ob(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def mix(c, a, bg=None):
    bg = bg or PAL["bg"]
    return tuple(int(c[i] * a + bg[i] * (1 - a)) for i in range(3))
def T(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)
def wrap(d, s, font, maxw):
    words = s.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines
def eur(n):
    s = f"{abs(int(round(n))):,}".replace(",", ".")
    return ("−" if n < 0 else "") + s + " €"

_ic = {}
def chart_fit(path, bw, bh):
    k = (path, bw, bh)
    if k in _ic: return _ic[k]
    im = Image.open(path).convert("RGB")
    r = min(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    _ic[k] = im; return im
def card(d, x, y, w, h, r=22, fill=None, border=None, bw=2):
    fill = fill or PAL["card"]; border = border or PAL["line"]
    d.rounded_rectangle([x + 4, y + 7, x + w + 4, y + h + 7], radius=r, fill=(230, 234, 240))
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=border, width=bw)
def paste_chart(img, path, x, y, w, h, alpha=1.0):
    ch = chart_fit(path, w - 40, h - 40)
    px = x + (w - ch.width) // 2; py = y + (h - ch.height) // 2
    if alpha >= 1.0: img.paste(ch, (px, py))
    else:
        base = img.crop((px, py, px + ch.width, py + ch.height))
        img.paste(Image.blend(base, ch, alpha), (px, py))

# ---------------- header/footer/captions ----------------
def frame_base(sid, gt, gtot):
    img = Image.new("RGB", (W, H), PAL["bg"]); d = ImageDraw.Draw(img)
    T(d, (160, 72), "SmartMoney", F(FSANSB, 34), PAL["navy"], "lm")
    wl = d.textlength("SmartMoney", font=F(FSANSB, 34))
    T(d, (160 + wl, 72), "Lab", F(FSANSB, 34), PAL["gold"], "lm")
    d.rectangle([160, 104, 300, 108], fill=PAL["gold"])
    if sid != "outro":
        pw, px, py = 1600, 160, 1024
        d.rounded_rectangle([px, py, px + pw, py + 8], radius=4, fill=PAL["line"])
        d.rounded_rectangle([px, py, px + int(pw * clamp(gt / gtot)), py + 8], radius=4, fill=PAL["navy"])
    return img, d

def caption(d, chunks, t, dur):
    if not chunks: return
    wts = [max(8, len(c)) for c in chunks]; tot = sum(wts); acc = 0; segs = []
    for c, w in zip(chunks, wts):
        a = acc / tot * dur; acc += w; b = acc / tot * dur; segs.append((a, b, c))
    cur, local, seglen = segs[-1][2], 1, 1
    for a, b, c in segs:
        if a <= t < b: cur, local, seglen = c, t - a, b - a; break
    fade = clamp(local / 0.35)
    if seglen - local <= 0.5: fade *= clamp((seglen - local) / 0.35) + 0.0
    al = int(255 * clamp(fade))
    if al < 6: return
    f = F(FSANSB, 40); lines = wrap(d, cur, f, W - 360); y = 904
    d.rectangle([160, y - 6, 230, y], fill=mix(PAL["gold"], al / 255))
    for i, ln in enumerate(lines):
        T(d, (160, y + 14 + i * 50), ln, f, mix(PAL["ink"], al / 255), "la")

# ---------------- scene renderers ----------------
def sc_cover(img, d, sc, t, dur):
    CX = W // 2
    a = eo(t / 0.8)
    f = F(FSERIF, 132)
    T(d, (CX, 300), sc["title"], f, mix(PAL["navy"], a), "mm")
    sp = sc.get("spark")
    if sp:
        x0, x1 = 560, 1360; prog = eo(clamp((t - 0.6) / 2.6))
        yf = 470
        T(d, (x0 - 30, yf), sp["top"], F(FSANSB, 34), PAL["navy"], "rm")
        xe = x0 + int((x1 - x0) * prog)
        if xe > x0: d.line([(x0, yf), (xe, yf)], fill=PAL["navy"], width=8)
        d.ellipse([xe - 9, yf - 9, xe + 9, yf + 9], fill=PAL["navy"])
        T(d, (x1 + 30, yf), sp["top_note"], F(FSANS, 30), PAL["muted"], "lm")
        yv = 600
        T(d, (x0 - 30, yv), sp["bot"], F(FSANSB, 34), PAL["amber"], "rm")
        pts = [(x0 + i, yv - 38 * math.sin(i / 70.0)) for i in range(0, int((x1 - x0) * prog) + 1, 6)]
        if len(pts) > 1: d.line(pts, fill=PAL["gold"], width=8, joint="curve")
        if pts: d.ellipse([pts[-1][0] - 9, pts[-1][1] - 9, pts[-1][0] + 9, pts[-1][1] + 9], fill=PAL["amber"])
        T(d, (x1 + 30, yv), sp["bot_note"], F(FSANS, 30), PAL["muted"], "lm")
    chip = sc.get("chip")
    if chip:
        ca = eo(clamp((t - 4.5) / 1.0))
        if ca > 0.02:
            T(d, (CX, 700), chip, F(FSANSB, 32), mix(PAL["navy"], ca), "mm")
    return img

def sc_chart_side(img, d, sc, t, dur):
    cx, cy, cw, chh = 140, 205, 1075, 580
    card(d, cx, cy, cw, chh)
    paste_chart(img, sc["chart"], cx, cy, cw, chh, alpha=eo(clamp(t / 0.8)))
    d = ImageDraw.Draw(img); rx = 1285
    T(d, (rx, 250), sc["title"], F(FSERIF, 56), PAL["ink"], "la")
    for an in sc.get("annos", []):
        a = eo((t - an.get("at", 0.6)) / 0.8)
        if a > 0.02:
            col = mix(C(an.get("c", "ink")), a)
            note = an.get("note")
            T(d, (rx, an.get("y", 356)), an["t"], F(FSANSB, an.get("size", 36)), col, "la")
            if note:
                T(d, (rx, an.get("y", 356) + 54), note, F(FSANS, 33), PAL["muted"], "la")
    box = sc.get("box")
    if box:
        a = eo((t - box.get("at", 2.2)) / 1.0)
        if a > 0.3:
            bx, by, bw2, bh2 = rx, box.get("y", 545), 500, 210
            d.rounded_rectangle([bx, by, bx + bw2, by + bh2], radius=16, fill=(239, 244, 255), outline=(191, 210, 255), width=2)
            T(d, (bx + 30, by + 28), box["kicker"], F(FSANSB, 34), PAL["amber"], "la")
            for i, ln in enumerate(box["lines"]):
                T(d, (bx + 30, by + 86 + i * 44), ln, F(FSANS, 33), PAL["ink"], "la")
    bn = sc.get("bignum")
    if bn:
        a = eo((t - bn.get("at", 2.4)) / 0.8)
        if a > 0.02:
            s = int(116 * a)
            T(d, (rx, bn.get("y", 624)), bn["t"], F(FSERIF, max(10, s)), C(bn.get("c", "amber")), "la")
            if a > 0.6 and bn.get("note"):
                T(d, (rx, bn.get("y", 624) + 152), bn["note"], F(FSANS, 30), PAL["muted"], "la")
    return img

def sc_stats(img, d, sc, t, dur):
    T(d, (160, 220), sc["heading"], F(FSERIF, 52), PAL["ink"], "la")
    y = 360
    for it in sc["items"]:
        at = it.get("at", 0.6)
        if "countup" in it:
            cu = eo((t - at) / 1.4); val = it["countup"] * cu
            txt = eur(val) if it.get("fmt") == "eur" else str(int(round(val)))
            T(d, (200, y + 20), txt, F(FSERIF, 120), C(it.get("c", "amber")), "lm")
            T(d, (200, y + 150), it["note"], F(FSANS, 38), PAL["muted"], "la")
        else:
            T(d, (200, y + 20), it["big"], F(FSERIF, 160), C(it.get("c", "navy")), "lm")
            if it.get("suffix"):
                bw = d.textlength(it["big"], font=F(FSERIF, 160))
                T(d, (200 + bw + 20, y), it["suffix"], F(FSANSB, 64), C(it.get("c", "navy")), "lm")
            T(d, (200, y + 150), it["note"], F(FSANS, 38), PAL["muted"], "la")
        y += 300
    if sc.get("inset"):
        cx, cy, cw, chh = 1080, 300, 760, 460
        card(d, cx, cy, cw, chh)
        paste_chart(img, sc["inset"], cx, cy, cw, chh, alpha=eo(clamp((t - 0.5) / 1.0)))
    return img

def sc_risk_bars(img, d, sc, t, dur):
    T(d, (160, 220), sc["heading"], F(FSERIF, 52), PAL["ink"], "la")
    cu = eo(clamp((t - 0.5) / 1.2)); v = int(sc["pct"] * cu)
    T(d, (200, 300), f"{v}%", F(FSERIF, 150), PAL["navy"], "la")
    for i, ln in enumerate(sc.get("pct_note", [])):
        T(d, (210, 470 + i * 46), ln, F(FSANS, 36), PAL["muted"], "la")
    if sc.get("highlight"):
        T(d, (210, 600), sc["highlight"], F(FSANSB, 38), PAL["amber"], "la")
    b = sc["bars"]; bx, by, bw = 1120, 760, 150; base = by; maxh = 430
    gp = eo(clamp((t - 1.0) / 1.6))
    h1 = int(maxh * (b["a"] / b["b"])); h2 = int(maxh * gp)
    d.rectangle([bx, base - h1, bx + bw, base], fill=PAL["gold"])
    T(d, (bx + bw // 2, base - h1 - 30), f"{b['a']:,}".replace(",", ".") + " €", F(FSANSB, 34), PAL["amber"], "mm")
    T(d, (bx + bw // 2, base + 30), b["a_label"], F(FSANS, 30), PAL["muted"], "mm")
    bx2 = bx + 300
    d.rectangle([bx2, base - h2, bx2 + bw, base], fill=PAL["amber"])
    if gp > 0.15:
        T(d, (bx2 + bw // 2, base - h2 - 30), f"{b['b']:,}".replace(",", ".") + " €", F(FSANSB, 34), PAL["amber"], "mm")
    T(d, (bx2 + bw // 2, base + 30), b["b_label"], F(FSANS, 30), PAL["muted"], "mm")
    if gp > 0.6:
        T(d, ((bx + bx2) // 2 + bw // 2, base - maxh - 20), b["pct"], F(FSERIF, 70), PAL["amber"], "mm")
    if b.get("title"):
        T(d, (bx + 150, 220), b["title"], F(FSANS, 30), PAL["muted"], "mm")
    return img

def sc_transform_chart(img, d, sc, t, dur):
    CX = W // 2; half = dur * sc.get("split", 0.52)
    if t < half + 0.4:
        T(d, (160, 220), sc["heading"], F(FSERIF, 52), PAL["ink"], "la")
        T(d, (300, 470), sc["from"], F(FSERIF, 150), PAL["muted"], "mm")
        T(d, (300, 600), sc["from_note"], F(FSANS, 34), PAL["muted"], "mm")
        T(d, (560, 470), "→", F(FSANSB, 110), PAL["navy"], "mm")
        fv = int(sc["from"].strip("%")); tv = int(sc["to"].strip("%"))
        cu = eo(clamp((t - 0.8) / 1.6)); v = int(fv + (tv - fv) * cu)
        T(d, (850, 470), f"{v}%", F(FSERIF, 150), PAL["navy"], "mm")
        T(d, (850, 600), sc["to_note"], F(FSANS, 34), PAL["navy"], "mm")
        T(d, (575, 700), sc["footer"], F(FSANSB, 36), PAL["ink"], "mm")
    else:
        tb = t - half
        cx, cy, cw, chh = 340, 200, 1240, 560
        card(d, cx, cy, cw, chh)
        paste_chart(img, sc["chart"], cx, cy, cw, chh, alpha=eo(clamp(tb / 0.6)))
        d = ImageDraw.Draw(img)
        T(d, (CX, 790), sc["chart_caption"], F(FSANSB, 34), PAL["ink"], "mm")
    return img

def sc_rates_today(img, d, sc, t, dur):
    CX = W // 2
    T(d, (CX, 210), sc["heading"], F(FSERIF, 60), PAL["ink"], "mm")
    w1, g, yy, hh = 560, 80, 300, 250
    x1 = CX - w1 - g // 2; x2 = CX + g // 2
    card(d, x1, yy, w1, hh, fill=(239, 244, 255), border=(191, 210, 255))
    T(d, (x1 + w1 // 2, yy + 70), sc["left"]["label"], F(FSANSB, 40), PAL["navy"], "mm")
    T(d, (x1 + w1 // 2, yy + 160), sc["left"]["val"], F(FSERIF, 96), PAL["navy"], "mm")
    card(d, x2, yy, w1, hh, fill=(255, 247, 235), border=(253, 220, 170))
    T(d, (x2 + w1 // 2, yy + 70), sc["right"]["label"], F(FSANSB, 40), PAL["amber"], "mm")
    T(d, (x2 + w1 // 2, yy + 160), sc["right"]["val"], F(FSERIF, 96), PAL["amber"], "mm")
    ab = eo(clamp((t - 0.8) / 0.8))
    if ab > 0.02:
        T(d, (CX, 620), sc["badge"], F(FSANSB, 44), mix(PAL["ink"], ab), "mm")
    lc = sc.get("line_countup")
    if lc:
        cu = eo(clamp((t - 1.6) / 1.4)); v = int(lc["pct"] * cu)
        T(d, (CX, 720), lc["tpl"].format(v=v), F(FSANS, 40), PAL["muted"], "mm")
    if sc.get("cta"):
        ac = eo(clamp((t - 2.6) / 1.0))
        if ac > 0.02:
            bx, by = CX - 440, 800
            d.rounded_rectangle([bx, by, bx + 880, by + 64], radius=32, fill=PAL["navy"])
            T(d, (CX, by + 32), sc["cta"], F(FSANSB, 30), PAL["white"], "mm")
    return img

def sc_outro(img, d, sc, t, dur):
    CX = W // 2; a = eo(clamp(t / 0.7))
    T(d, (CX, 430), "SmartMoney", F(FSERIF, 120), mix(PAL["navy"], a), "mm")
    wl = d.textlength("SmartMoney", font=F(FSERIF, 120))
    T(d, (CX + wl / 2, 430), "Lab", F(FSERIF, 120), PAL["gold"], "lm")
    d.rectangle([CX - 120, 510, CX + 120, 516], fill=PAL["gold"])
    T(d, (CX, 585), TAGLINE, F(FSANS, 44), PAL["muted"], "mm")
    T(d, (CX, 670), HANDLE, F(FSANSB, 40), PAL["navy"], "mm")
    T(d, (CX, 900), DISCLAIMER, F(FSANS, 28), PAL["muted"], "mm")
    return img

RENDERERS = {
    "cover": sc_cover, "chart_side": sc_chart_side, "stats": sc_stats,
    "risk_bars": sc_risk_bars, "transform_chart": sc_transform_chart,
    "rates_today": sc_rates_today, "outro": sc_outro,
}

def render_frame(sc, t, dur, gt, gtot):
    sid = "outro" if sc["type"] == "outro" else sc.get("_sid", "s")
    img, d = frame_base(sid, gt, gtot)
    img = RENDERERS[sc["type"]](img, d, sc, t, dur)
    d = ImageDraw.Draw(img)
    caption(d, sc.get("captions", []), t, dur)
    if t < 0.3:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 1 - eo(t / 0.3))
    return img

def build(config, durations, audio_dir, out_path, charts_dir):
    """Renderizza tutte le scene e assembla in out_path (video + voiceover per scena)."""
    scenes = config["scenes"]
    # risolvi i percorsi grafici e assegna id
    for i, sc in enumerate(scenes):
        sc["_sid"] = f"s{i+1}"
        for key in ("chart", "inset"):
            if sc.get(key) and not os.path.isabs(sc[key]):
                sc[key] = os.path.join(charts_dir, sc[key])
    gstart = {}; acc = 0
    for sc in scenes:
        gstart[sc["_sid"]] = acc; acc += durations[sc["_sid"]]
    gtot = acc
    tmp = os.path.join(audio_dir, "_scenes"); os.makedirs(tmp, exist_ok=True)
    parts = []
    for sc in scenes:
        sid = sc["_sid"]; dur = durations[sid]; N = int(round(dur * FPS)); vdur = N / FPS
        outp = os.path.join(tmp, f"{sid}.mp4")
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "pipe:0", "-i", os.path.join(audio_dir, f"{sid}.mp3"),
               "-map", "0:v", "-map", "1:a", "-af", "apad", "-t", f"{vdur:.3f}",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
               "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for i in range(N):
            t = i / FPS
            p.stdin.write(render_frame(sc, t, vdur, gstart[sid] + t, gtot).tobytes())
        p.stdin.close(); p.wait(); parts.append(outp)
    listf = os.path.join(tmp, "concat.txt")
    with open(listf, "w") as f:
        for pth in parts: f.write(f"file '{pth}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path
