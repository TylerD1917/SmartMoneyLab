# -*- coding: utf-8 -*-
"""Smoke test HyperFrames: genera smoke-sml/index.html dai dati veri del reel
'quanto rendono gli ETF obbligazionari' (gamba USA 20+, rendimento annuo dei
10 anni successivi per mese di acquisto, 1980-2016)."""
import csv, json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CSV = os.path.join(ROOT, "social", "quanto-rendono-etf-obbligazionari", "reel_quando_compri.csv")
OUT = os.path.join(HERE, "smoke-sml", "index.html")

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
vals = [float(r["USA 20+"]) for r in rows]
dates = [r["Date"][:7] for r in rows]

# geometria del grafico (px nel frame 1920x1080)
X0, W = 200, 1480
Y_TOP, H = 430, 470          # da +20% (alto) a -4% (basso)
VMAX, VMIN = 20.0, -4.0
def px(i): return X0 + W * i / (len(vals) - 1)
def py(v): return Y_TOP + H * (VMAX - v) / (VMAX - VMIN)

pts = [(round(px(i), 1), round(py(v), 1)) for i, v in enumerate(vals)]
path = "M" + " L".join(f"{x},{y}" for x, y in pts)

i_peak = max(range(len(vals)), key=lambda i: vals[i])
i_end = len(vals) - 1
assert dates[i_peak] == "1981-09", dates[i_peak]
peak, end = vals[i_peak], vals[i_end]
it = lambda v: (f"{v:+.1f}".replace(".", ",").replace("-", "−")) + "%"

grid = ""
for g in (20, 15, 10, 5, 0, -4):
    y = py(g)
    cls = "zero" if g == 0 else "gl"
    lab = it(g).replace(",0", "")
    grid += f'<line class="{cls}" x1="{X0}" x2="{X0+W}" y1="{y}" y2="{y}"/>'
    if g != -4:
        grid += f'<text class="ax" x="{X0-18}" y="{y+8}" text-anchor="end">{lab}</text>'
for yr in (1980, 1990, 2000, 2010):
    i = (yr - 1980) * 12
    grid += f'<text class="ax" x="{px(i)}" y="{Y_TOP+H+44}" text-anchor="middle">{yr}</text>'

T_REV0, T_REV = 2.3, 5.4
# etichette nello spazio vuoto in alto, collegate al punto da una linea di richiamo
TP = (720, py(20.3)); TE = (1290, py(19.2))
lead = (f'<line id="lpeak" x1="{TP[0]}" y1="{TP[1]+58:.0f}" x2="{pts[i_peak][0]}" y2="{pts[i_peak][1]}"/>'
        f'<line id="lend" x1="{TE[0]+300}" y1="{TE[1]+118:.0f}" x2="{pts[i_end][0]}" y2="{pts[i_end][1]}"/>')                       # inizio e durata della rivelazione
t_peak = T_REV0 + T_REV * i_peak / i_end

html = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<script src="./gsap.min.js"></script>
<style>
  html,body{{margin:0;background:#f8fafc;}}
  #root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:#f8fafc;
        font-family:'Lato','Liberation Sans',sans-serif;color:#0f172a;}}
  .clip{{position:absolute;inset:0;}}
  #kicker{{position:absolute;left:200px;top:96px;font-size:26px;letter-spacing:.14em;
          font-weight:700;color:#b45309;text-transform:uppercase;}}
  #titlebox{{position:absolute;left:200px;top:140px;overflow:hidden;padding-bottom:8px;}}
  #title{{font-family:'Liberation Serif',serif;font-weight:700;font-size:76px;line-height:1.08;
         color:#1e3a8a;}}
  #rule{{position:absolute;left:200px;top:318px;width:240px;height:8px;background:#fbbf24;
        transform-origin:left center;border-radius:4px;}}
  #sub{{position:absolute;left:200px;top:346px;font-size:30px;color:#475569;}}
  svg{{position:absolute;left:0;top:0;}}
  .gl{{stroke:#cbd5e1;stroke-width:1.5;stroke-dasharray:6 8;}}
  .zero{{stroke:#94a3b8;stroke-width:2.5;}}
  .ax{{font-size:24px;fill:#64748b;font-family:'Lato',sans-serif;}}
  #leads line{{stroke:#1e3a8a;stroke-width:2.5;stroke-dasharray:3 6;}}
  #curve{{fill:none;stroke:#1e3a8a;stroke-width:6;stroke-linejoin:round;stroke-linecap:round;}}
  #reveal{{position:absolute;left:0;top:0;height:1080px;width:1920px;}}
  #dot{{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;
       background:#fbbf24;border:5px solid #1e3a8a;box-sizing:border-box;left:0;top:0;}}
  #year{{position:absolute;right:240px;top:150px;font-family:'Liberation Serif',serif;
        font-size:120px;font-weight:700;color:#e2e8f0;}}
  .tag{{position:absolute;background:#1e3a8a;color:#fff;border-radius:14px;padding:16px 24px;
       font-size:28px;line-height:1.25;box-shadow:0 10px 30px rgba(30,58,138,.25);}}
  .tag b{{color:#fbbf24;font-size:44px;display:block;}}
  #foot{{position:absolute;left:200px;bottom:44px;font-size:22px;color:#94a3b8;}}
  #brand{{position:absolute;right:200px;bottom:40px;font-size:26px;font-weight:700;color:#1e3a8a;}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="10"
     data-width="1920" data-height="1080">
  <div class="clip" data-start="0" data-duration="10">
    <div id="year">1980</div>
    <div id="kicker">Titoli di Stato USA a 20+ anni</div>
    <div id="titlebox"><div id="title">Stesso titolo, due date di acquisto</div></div>
    <div id="rule"></div>
    <div id="sub">Rendimento annuo dei dieci anni successivi, per mese di acquisto</div>
    <svg width="1920" height="1080" id="grid">{grid}</svg>
    <div id="reveal"><svg width="1920" height="1080"><path id="curve" d="{path}"/></svg></div>
    <svg width="1920" height="1080" id="leads">{lead}</svg>
    <div id="dot"></div>
    <div class="tag" id="tpeak" style="left:{TP[0]}px;top:{TP[1]:.0f}px">
      Compri nel settembre 1981<b>{it(peak)} l'anno</b></div>
    <div class="tag" id="tend" style="left:{TE[0]}px;top:{TE[1]:.0f}px">
      Compri a gennaio 2016<b>{it(end)} l'anno</b></div>
    <div id="foot">Elaborazione SmartMoneyLab su dati FRED. Rendimenti lordi, indice ricostruito.</div>
    <div id="brand">smartmoneylab.it</div>
  </div>
</div>
<script>
  const PTS = {json.dumps(pts)};
  const X0 = {X0}, W = {W};
  gsap.set("#kicker", {{opacity:0, y:20}});
  gsap.set("#title", {{yPercent:110}});
  gsap.set("#rule", {{scaleX:0}});
  gsap.set("#sub, #grid, #year, #foot, #brand, #reveal", {{opacity:0}});
  gsap.set("#dot", {{opacity:0, scale:0}});
  gsap.set("#tpeak, #tend", {{opacity:0, scale:0.7, y:20}});
  gsap.set("#lpeak, #lend", {{opacity:0}});

  const rev = {{w:0}};
  function head(w){{
    // punta continua: x esattamente sul bordo della rivelazione, y interpolata
    // fra i due punti vicini (niente scalino visibile sui tratti ripidi)
    const f = Math.min(PTS.length-1, Math.max(0, w / W * (PTS.length-1)));
    const k = Math.min(PTS.length-2, Math.floor(f)), t = f - k;
    const y = PTS[k][1] + (PTS[k+1][1] - PTS[k][1]) * t;
    // il tracciato si ricostruisce fino alla punta: niente maschera a x, che sui
    // tratti quasi verticali lascerebbe vedere il segmento oltre il pallino
    const xh = X0 + w;
    document.getElementById("curve").setAttribute("d",
      "M" + PTS.slice(0, k + 1).map(q => q[0] + "," + q[1]).join(" L") + " L" + xh + "," + y);
    document.getElementById("dot").style.left = xh + "px";
    document.getElementById("dot").style.top  = y + "px";
    document.getElementById("year").textContent = 1980 + Math.floor(k/12);
  }}
  head(0);

  const tl = gsap.timeline({{paused:true}});
  tl.to("#kicker", {{opacity:1, y:0, duration:.6, ease:"power2.out"}}, .2)
    .to("#title",  {{yPercent:0, duration:.9, ease:"power3.out"}}, .35)
    .to("#rule",   {{scaleX:1, duration:.6, ease:"power2.inOut"}}, 1.05)
    .to("#sub",    {{opacity:1, duration:.6}}, 1.35)
    .to("#grid, #year, #reveal", {{opacity:1, duration:.7}}, 1.7)
    .to("#dot",    {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {T_REV0-.25})
    .to(rev, {{w:W, duration:{T_REV}, ease:"none", onUpdate:()=>head(rev.w)}}, {T_REV0})
    .to("#tpeak",  {{opacity:1, scale:1, y:0, duration:.5, ease:"back.out(1.8)"}}, {t_peak:.2f})
    .to("#lpeak", {{opacity:1, duration:.4}}, {t_peak:.2f})
    .to("#lend", {{opacity:1, duration:.4}}, {T_REV0+T_REV:.2f})
    .to("#tend",   {{opacity:1, scale:1, y:0, duration:.5, ease:"back.out(1.8)"}}, {T_REV0+T_REV:.2f})
    .to("#foot, #brand", {{opacity:1, duration:.6}}, {T_REV0+T_REV+.4:.2f});
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open(OUT, "w", encoding="utf-8").write(html)
# GSAP in locale: il render non dipende dalla rete
shutil.copy(os.path.join(HERE, "node_modules", "gsap", "dist", "gsap.min.js"),
            os.path.join(HERE, "smoke-sml", "gsap.min.js"))
print(f"ok: {len(pts)} punti, picco {dates[i_peak]} {peak:.2f}%, fine {dates[i_end]} {end:.2f}%, t_picco {t_peak:.2f}s")
