#!/usr/bin/env python3
"""
Intro standard di brand (~5s), da generare UNA volta e riusare per tutti i video.
Sequenza: bianco -> "Smart" -> "Money" -> "Lab" (esplosione) -> linea che cresce -> tagline.
Output: social/_brand/intro_smartmoneylab.mp4 (silenzioso; la musica si aggiunge dopo).

    python scripts/video/intro.py
"""
import os, subprocess, math, random
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
W, H, FPS = 1920, 1080, 24
DUR = 5.0; N = int(DUR * FPS)
BG = (248, 250, 252); NAVY = (30, 58, 138); GOLD = (245, 175, 25); MUTED = (100, 116, 139)
FSERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FSANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SZ = 140
fbig = ImageFont.truetype(FSERIF, SZ); ftag = ImageFont.truetype(FSANS, 48)
def clamp(x, a=0, b=1): return max(a, min(b, x))
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def ob(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
tmp = Image.new("RGB", (10, 10)); dd = ImageDraw.Draw(tmp)
w_s = dd.textlength("Smart", font=fbig); w_m = dd.textlength("Money", font=fbig); w_l = dd.textlength("Lab", font=fbig)
total = w_s + w_m + w_l; CY = 520; x0 = W / 2 - total / 2
x_smart = x0; x_money = x0 + w_s; x_lab_c = x0 + w_s + w_m + w_l / 2
line_y = CY + 92; tag_y = CY + 168
rng = random.Random(7)
PART = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.7, 1.0)) for _ in range(20)]
def col(c, a): return tuple(int(c[i] * a + BG[i] * (1 - a)) for i in range(3))

def frame(t):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    aS = eo((t - 0.35) / 0.45)
    if aS > 0.02: d.text((x_smart, CY + int(18 * (1 - aS))), "Smart", font=fbig, fill=col(NAVY, aS), anchor="lm")
    aM = eo((t - 0.95) / 0.45)
    if aM > 0.02: d.text((x_money, CY + int(18 * (1 - aM))), "Money", font=fbig, fill=col(NAVY, aM), anchor="lm")
    te = t - 1.7
    if te > 0:
        pp = clamp(te / 0.45)
        for ang, sp in PART:
            r = pp * 150 * sp; pa = 1 - pp
            if pa > 0.03:
                px = x_lab_c + math.cos(ang) * r; py = CY + math.sin(ang) * r
                rad = max(1, int(8 * (1 - pp)))
                d.ellipse([px - rad, py - rad, px + rad, py + rad], fill=col(GOLD, pa))
        s = 1.0
        if te < 0.5: s = 1.7 - 0.7 * ob(te / 0.5)
        aL = clamp(te / 0.18)
        fl = ImageFont.truetype(FSERIF, max(8, int(SZ * s)))
        d.text((x_lab_c, CY), "Lab", font=fl, fill=col(GOLD, aL), anchor="mm")
    lw = eo((t - 2.4) / 0.7)
    if lw > 0.02:
        half = int(150 * lw); d.rectangle([W / 2 - half, line_y, W / 2 + half, line_y + 7], fill=GOLD)
    aT = eo((t - 3.3) / 0.7)
    if aT > 0.02:
        d.text((W / 2, tag_y), "Finanza personale e analisi quantitativa", font=ftag, fill=col(MUTED, aT), anchor="mm")
    if t < 0.35:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 1 - eo(t / 0.35))
    return img

def main():
    out_dir = os.path.join(ROOT, "social", "_brand"); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "intro_smartmoneylab.mp4")
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a", "-t", f"{DUR:.3f}",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(N): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("[ok]", out)

if __name__ == "__main__":
    main()
