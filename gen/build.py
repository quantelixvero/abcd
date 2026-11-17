#!/usr/bin/env python3
"""
seadib profile README assets — "field log from the other side of the river"
Generates every hand-built animated SVG panel for the GitHub profile README.
All animation is SMIL (surives GitHub's camo proxy; no JS/CSS needed).
Run: python3 gen/build.py
"""
import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)

# ---------- palette : night river + one lantern ----------
GROUND  = "#060B18"   # night sky / page
PANEL   = "#0A1120"   # card surface
PANEL2  = "#0E1729"   # raised surface
LINE    = "#1C2B45"   # hairline
INK     = "#EAEFF7"   # full ink text
MUTED   = "#93A0B8"   # secondary text
DIM     = "#5B6B84"   # tertiary
AMBER   = "#FFB454"   # THE one accent (lantern)
AMBER_D = "#B5741F"   # deep amber
RIV3    = "#35739B"   # river light
RIV2    = "#225078"   # river mid
RIV1    = "#152F4B"   # river deep
MOON    = "#F7ECD4"

MONO = "'Cascadia Code','JetBrains Mono',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Helvetica,Arial,sans-serif"
BENG = "'Noto Sans Bengali','Nirmala UI','Bangla Sangam MN','Hind Siliguri',sans-serif"

# ---------- font tools ----------
def load_font(path, axes):
    f = TTFont(path)
    instantiateVariableFont(f, axes, inplace=True, updateFontNames=False)
    return f

FG = load_font(os.path.join(ROOT, "gen", "SpaceGrotesk.ttf"), {"wght": 700})

def outline(font, text, x, y, size, spacing=0.0, fill="#fff", opacity="1", extra=""):
    """Render text as vector paths (webfonts never load through camo)."""
    upem = font["head"].unitsPerEm
    s = size / upem
    cmap = font.getBestCmap(); hmtx = font["hmtx"]; gs = font.getGlyphSet()
    parts = []
    cx = float(x)
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            continue
        w = hmtx[gn][0]
        pen = SVGPathPen(gs)
        gs[gn].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path transform="translate({cx:.2f},{y}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
        cx += w * s + spacing
    width = cx - x
    return (f'<g fill="{fill}" opacity="{opacity}" {extra}>{"".join(parts)}</g>', width)

def tspan(text, x, y, size, fill, family=MONO, weight=400, spacing=0, opacity="1", extra=""):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" opacity="{opacity}"{ls} {extra}>{text}</text>')

def rise(delay, dur=1.4, dy="8"):
    """Staggered rise-in that never hides content: base state is visible,
    SMIL only adds the move (safe if SMIL is off/paused)."""
    fr = min(delay / dur, 0.85)
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 {dy};0 {dy};0 0" keyTimes="0;{fr:.3f};1" dur="{dur}s" begin="0s" '
            f'fill="freeze" calcMode="spline" keySplines="0 0 1 1;0.2 0.7 0.2 1"/>')

def wave_path(w, base_y, amp, period, phase, extend=True):
    step = period / 24.0
    pts = []
    x = 0.0
    total = w + period if extend else w
    while x <= total + 1e-6:
        pts.append((x, base_y + amp * math.sin(2 * math.pi * (x + phase) / period)))
        x += step
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(1, len(pts)):
        d += f"L{pts[i][0]:.1f},{pts[i][1]:.1f} "
    d += f"L{total},{base_y + 400} L0,{base_y + 400} Z"
    return d, period

svg_open = lambda w, h: (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
                         f'width="{w}" height="{h}" role="img">')

def save(name, body):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name, os.path.getsize(p), "bytes")

# =====================================================================
# 1. BANNER — night river, moon, ferry, outlined wordmark
# =====================================================================
W, H = 1600, 360
name, nw = outline(FG, "ABDULLAH AL ADIB", 0, 0, 104, spacing=3.0, fill=INK)
name_x = 88
name_w = nw

stars = []
import random
random.seed(7)
for i in range(30):
    sx = random.randint(20, W - 20)
    sy = random.randint(18, 240)
    r = random.choice([0.9, 1.1, 1.3, 1.6])
    dur = random.choice([2.6, 3.4, 4.2, 5.0])
    beg = round(random.uniform(0, dur), 2)
    stars.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#DDE6F5" opacity="0.25">'
                 f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{dur}s" '
                 f'begin="-{beg}s" repeatCount="indefinite"/></circle>')

# river waves (three layers, seamless loop = translate by exactly one period)
def wave_layer(y, amp, period, color, op, dur, phase=0):
    d, p = wave_path(W, y, amp, period, phase)
    return (f'<path d="{d}" fill="{color}" opacity="{op}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{-p} 0" dur="{dur}s" repeatCount="indefinite"/></path>')

waves = (wave_layer(296, 7, 160, RIV3, "0.45", "17s", phase=40)
         + wave_layer(308, 9, 200, RIV2, "0.75", "12s", phase=130)
         + wave_layer(322, 8, 240, RIV1, "1.0", "9s", phase=20))

# moon + halo + reflection
moon = f'''
<circle cx="1318" cy="86" r="30" fill="{MOON}"/>
<circle cx="1318" cy="86" r="30" fill="none" stroke="{MOON}" stroke-opacity="0.25" stroke-width="10">
  <animate attributeName="r" values="30;44" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="stroke-opacity" values="0.28;0" dur="5s" repeatCount="indefinite"/>
</circle>
<g fill="{MOON}" opacity="0.35">
  <rect x="1306" y="316" width="24" height="3" rx="1.5">
    <animate attributeName="opacity" values="0.1;0.5;0.1" dur="4s" repeatCount="indefinite"/></rect>
  <rect x="1312" y="330" width="12" height="3" rx="1.5">
    <animate attributeName="opacity" values="0.4;0.1;0.4" dur="4s" repeatCount="indefinite"/></rect>
</g>
<text x="1318" y="152" text-anchor="middle" font-family="{BENG}" font-size="42" fill="{AMBER}" opacity="0.95">আদিব</text>
'''

# ferry silhouette with lantern, crossing the river
ferry = f'''
<g>
  <animateMotion dur="52s" repeatCount="indefinite" path="M-160,0 L1760,0" rotate="0"/>
  <g transform="translate(0,-2)">
    <animateTransform attributeName="transform" type="translate" additive="sum"
      values="0 0;0 2.6;0 0" dur="3.2s" repeatCount="indefinite" calcMode="spline"
      keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>
  </g>
  <g transform="translate(0,296)">
    <path d="M0,0 L74,0 L64,12 L10,12 Z" fill="#05080F"/>
    <rect x="20" y="-12" width="30" height="12" rx="2" fill="#05080F"/>
    <line x1="35" y1="-12" x2="35" y2="-26" stroke="#05080F" stroke-width="2.5"/>
    <circle cx="35" cy="-28" r="3.2" fill="{AMBER}">
      <animate attributeName="opacity" values="1;0.55;1" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="35" cy="-28" r="8" fill="{AMBER}" opacity="0.25">
      <animate attributeName="r" values="6;11;6" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.3;0.08;0.3" dur="2.4s" repeatCount="indefinite"/>
    </circle>
  </g>
</g>
'''

# shine sweep over the wordmark
shine = f'''
<mask id="nmask"><g transform="translate({name_x},168)">{name.replace('fill="#fff"','')}</g></mask>
'''
# name paths must be white inside mask; rebuild with white fill
name_white, _ = outline(FG, "ABDULLAH AL ADIB", 0, 0, 104, spacing=3.0, fill="#fff")
shine = f'''
<mask id="nmask"><g transform="translate({name_x},168)">{name_white}</g></mask>
<g mask="url(#nmask)">
  <rect x="-320" y="40" width="260" height="190" fill="url(#shineGrad)" opacity="0.5">
    <animateTransform attributeName="transform" type="translate"
      values="0 0;{name_w + 700} 0;{name_w + 700} 0" keyTimes="0;0.32;1" dur="7s" repeatCount="indefinite"/>
  </rect>
</g>
'''

banner = f'''{svg_open(W, H)}
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#04070F"/><stop offset="0.62" stop-color="#081020"/>
    <stop offset="1" stop-color="#0B1526"/>
  </linearGradient>
  <linearGradient id="shineGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.05 0"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{''.join(stars)}
{moon}
{waves}
{ferry}
<g transform="translate({name_x},168)">{name}</g>
{shine}
{tspan("SEADIB  ·  FIELD LOG NO. 001", name_x, 74, 15, AMBER, spacing=4)}
{tspan("aspiring software engineer — building the web from the other side of the river", name_x, 216, 20, MUTED, family=SANS)}
{tspan("HATIYA ISLAND 22°40′N 91°00′E   →   DHAKA 23°48′N 90°24′E   ·   DHAKA COLLEGE   ·   HSC 2027 · SCIENCE", name_x, 250, 13, DIM)}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.55"/>
</svg>'''
save("banner.svg", banner)

# =====================================================================
# 2. DIVIDER — sliding tide + one lantern
# =====================================================================
W2, H2 = 1600, 90
def dwave(y, amp, period, color, op, dur, phase=0):
    d, p = wave_path(W2, y, amp, period, phase)
    return (f'<path d="{d}" fill="{color}" opacity="{op}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{p} 0" dur="{dur}s" repeatCount="indefinite"/></path>')
divider = f'''{svg_open(W2, H2)}
<defs><filter id="gl2"><feGaussianBlur stdDeviation="3"/></filter></defs>
{''.join([dwave(40,5,150,RIV3,"0.35","13s",phase=10),
          dwave(52,6,190,RIV2,"0.6","10s",phase=90),
          dwave(64,5,230,RIV1,"1.0","7s",phase=150)])}
<g transform="translate(800,30)">
  <circle r="4" fill="{AMBER}">
    <animate attributeName="opacity" values="1;0.4;1" dur="2.8s" repeatCount="indefinite"/></circle>
  <circle r="10" fill="{AMBER}" opacity="0.3" filter="url(#gl2)">
    <animate attributeName="r" values="7;12;7" dur="2.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.35;0.08;0.35" dur="2.8s" repeatCount="indefinite"/></circle>
  <animateMotion dur="18s" repeatCount="indefinite" path="M-700,10 C-350,-14 350,14 700,10"/>
</g>
</svg>'''
save("divider.svg", divider)

# =====================================================================
# 3. STATUS — field log card
# =====================================================================
W3, H3 = 780, 430
rows = [
    ("FROM",     "Hatiya Island, Noakhali  →  Dhaka College"),
    ("STUDY",    "HSC 2027 · Science — Phy · Chem · Math · Eng · Stats"),
    ("BUILDING", "agentic-sync · DrX Voice Typing · dchall"),
    ("FIXING",   "physics, slowly — one page a day"),
    ("TARGET",   "Golden A+  →  BUET CSE"),
]
row_svg = []
for i, (k, v) in enumerate(rows):
    y = 148 + i * 46
    row_svg.append(f'<g>{rise(0.2 + i * 0.12)}'
                   f'{tspan(k, 44, y, 13, AMBER, spacing=2.5)}'
                   f'{tspan(v, 210, y, 17, INK, family=SANS)}</g>')
status = f'''{svg_open(W3, H3)}
<defs><filter id="gl3"><feGaussianBlur stdDeviation="4"/></filter></defs>
<rect x="1" y="1" width="{W3-2}" height="{H3-2}" rx="18" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
<rect x="1" y="1" width="5" height="{H3-2}" rx="2.5" fill="{AMBER}"/>
{tspan("FIELD LOG — CURRENTLY", 44, 56, 14, AMBER, spacing=3.5)}
{tspan("SNAPSHOT · 17 NOV 2026", W3-44, 56, 12, DIM, spacing=1.5, extra='text-anchor="end"')}
<line x1="44" y1="82" x2="{W3-44}" y2="82" stroke="{LINE}" stroke-width="1"/>
{''.join(row_svg)}
<g>
  <circle cx="56" cy="{H3-40}" r="5" fill="{AMBER}">
    <animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>
  <circle cx="56" cy="{H3-40}" r="11" fill="{AMBER}" opacity="0.25" filter="url(#gl3)">
    <animate attributeName="r" values="8;13;8" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.3;0.06;0.3" dur="1.8s" repeatCount="indefinite"/></circle>
  {tspan("LEARNING EVERY SINGLE DAY", 76, H3-35, 13, MUTED, spacing=2.5)}
  {tspan("seadib", W3-44, H3-35, 13, DIM, extra='text-anchor="end"')}
</g>
</svg>'''
save("status.svg", status)

# =====================================================================
# 4. ROUTE — the crossing, Hatiya -> Dhaka
# =====================================================================
W4, H4 = 780, 430
route = f'''{svg_open(W4, H4)}
<defs>
  <filter id="gl4"><feGaussianBlur stdDeviation="3"/></filter>
  <path id="rte" d="M120,250 C300,150 480,330 660,230" fill="none"/>
</defs>
<rect x="1" y="1" width="{W4-2}" height="{H4-2}" rx="18" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
{tspan("THE CROSSING — HATIYA → DHAKA", 44, 56, 14, AMBER, spacing=3.5)}
{tspan("CHAIRMAN GHAT · NALCHIRA · MAIJDEE", W4-44, 56, 11, DIM, spacing=1.5, extra='text-anchor="end"')}
<line x1="44" y1="82" x2="{W4-44}" y2="82" stroke="{LINE}" stroke-width="1"/>
<use href="#rte" stroke="{LINE}" stroke-width="2" fill="none"/>
<use href="#rte" stroke="{AMBER}" stroke-width="2" fill="none" stroke-dasharray="6 10" stroke-linecap="round">
  <animate attributeName="stroke-dashoffset" values="0;-160" dur="6s" repeatCount="indefinite"/></use>
<g>
  <circle cx="120" cy="250" r="7" fill="{AMBER}"/>
  <circle cx="120" cy="250" r="14" fill="none" stroke="{AMBER}" stroke-opacity="0.4" stroke-width="1.5">
    <animate attributeName="r" values="9;18" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.5;0" dur="2.6s" repeatCount="indefinite"/></circle>
  {tspan("HATIYA ISLAND", 120, 290, 15, INK, family=SANS, weight=600, extra='text-anchor="middle"')}
  {tspan("22°40′N · 91°00′E", 120, 310, 11, DIM, extra='text-anchor="middle"')}
</g>
<g>
  <circle cx="660" cy="230" r="7" fill="{AMBER}"/>
  <circle cx="660" cy="230" r="14" fill="none" stroke="{AMBER}" stroke-opacity="0.4" stroke-width="1.5">
    <animate attributeName="r" values="9;18" dur="2.6s" begin="1.3s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.5;0" dur="2.6s" begin="1.3s" repeatCount="indefinite"/></circle>
  {tspan("DHAKA", 660, 270, 15, INK, family=SANS, weight=600, extra='text-anchor="middle"')}
  {tspan("23°48′N · 90°24′E", 660, 290, 11, DIM, extra='text-anchor="middle"')}
</g>
<g>
  <animateMotion dur="16s" repeatCount="indefinite" rotate="auto">
    <mpath href="#rte"/>
  </animateMotion>
  <g transform="scale(0.9)">
    <path d="M0,0 L26,0 L22,6 L4,6 Z" fill="{AMBER}"/>
    <rect x="7" y="-6" width="10" height="6" rx="1" fill="{AMBER}"/>
    <line x1="12" y1="-6" x2="12" y2="-13" stroke="{AMBER}" stroke-width="1.6"/>
    <circle cx="12" cy="-15" r="2.2" fill="{AMBER}">
      <animate attributeName="opacity" values="1;0.4;1" dur="1.6s" repeatCount="indefinite"/></circle>
  </g>
</g>
<g>{rise(0.9)}
  {tspan("the estuary in front, the code behind — every line written since crossed this gap", 44, 386, 14, MUTED, family=SANS)}
</g>
<g>{rise(1.1)}
  {tspan("HATIYA → DHAKA · EST. 2009", W4-44, 386, 11, DIM, extra='text-anchor="end"')}
</g>
</svg>'''
save("route.svg", route)

# =====================================================================
# 5. STACK — chips with raking light
# =====================================================================
W5, H5 = 1240, 340
groups = [
    ("WRITE", ["HTML5", "CSS3", "JAVASCRIPT", "C"]),
    ("SHIPS WITH", ["GIT", "GITHUB", "NETLIFY", "VS CODE"]),
    ("LEARNING", ["PYTHON", "BACKEND", "AUTOMATION", "AI AGENTS"]),
]
chip_h, chip_y0, row_h = 44, 96, 78
chip_svg = []
mask_parts = []
for gi, (label, chips) in enumerate(groups):
    y = chip_y0 + gi * row_h
    chip_svg.append(tspan(label, 44, y + 29, 13, AMBER, spacing=3))
    cx = 220
    for ci, c in enumerate(chips):
        tw = len(c) * 9.6 + 40   # mono 15px approx advance
        begin = 0.15 + gi * 0.12 + ci * 0.08
        chip_svg.append(
            f'<g>{rise(begin)}'
            f'<rect x="{cx}" y="{y}" width="{tw}" height="{chip_h}" rx="10" fill="{PANEL2}" stroke="{LINE}" stroke-width="1.2"/>'
            + tspan(c, cx + tw/2, y + 28, 15, INK, extra='text-anchor="middle"')
            + '</g>')
        mask_parts.append(f'<rect x="{cx}" y="{y}" width="{tw}" height="{chip_h}" rx="10"/>')
        cx += tw + 18
mask_id = "chipmask"
stack = f'''{svg_open(W5, H5)}
<defs>
  <linearGradient id="rake" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.16"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="{mask_id}">{"".join(mask_parts)}</mask>
</defs>
<rect x="1" y="1" width="{W5-2}" height="{H5-2}" rx="18" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
{tspan("WHAT I WORK WITH", 44, 52, 14, AMBER, spacing=3.5)}
{tspan("HONEST LEVELS — HTML5 90 · CSS3 75 · JS 60 · C 40", W5-44, 52, 11, DIM, spacing=1.5, extra='text-anchor="end"')}
<line x1="44" y1="74" x2="{W5-44}" y2="74" stroke="{LINE}" stroke-width="1"/>
{''.join(chip_svg)}
<g mask="url(#{mask_id})">
  <rect x="-300" y="60" width="220" height="240" fill="url(#rake)">
    <animateTransform attributeName="transform" type="translate"
      values="0 0;{W5 + 500} 0;{W5 + 500} 0" keyTimes="0;0.4;1" dur="8s" repeatCount="indefinite"/>
  </rect>
</g>
</svg>'''
save("stack.svg", stack)

# =====================================================================
# 6. FOOTER — sign-off
# =====================================================================
W6, H6 = 1600, 190
seadib, sw = outline(FG, "SEADIB", 0, 0, 56, spacing=8.0, fill=AMBER)
seadib_w = sw
sx = (W6 - seadib_w) / 2
seadib_white, _ = outline(FG, "SEADIB", 0, 0, 56, spacing=8.0, fill="#fff")
footer = f'''{svg_open(W6, H6)}
<defs>
  <linearGradient id="fgr" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0A1120"/><stop offset="1" stop-color="#04070F"/>
  </linearGradient>
  <linearGradient id="fshine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.8"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="fmask"><g transform="translate({sx},116)">{seadib_white}</g></mask>
  <filter id="gl6"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<rect width="{W6}" height="{H6}" fill="url(#fgr)"/>
<circle cx="{W6/2}" cy="44" r="3.5" fill="{AMBER}">
  <animate attributeName="opacity" values="1;0.3;1" dur="2.6s" repeatCount="indefinite"/></circle>
<circle cx="{W6/2}" cy="44" r="9" fill="{AMBER}" opacity="0.25" filter="url(#gl6)">
  <animate attributeName="r" values="6;12;6" dur="2.6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0.3;0.06;0.3" dur="2.6s" repeatCount="indefinite"/></circle>
<g transform="translate({sx},118)">{seadib}</g>
<g mask="url(#fmask)">
  <rect x="-260" y="40" width="200" height="120" fill="url(#fshine)" opacity="0.55">
    <animateTransform attributeName="transform" type="translate"
      values="0 0;{seadib_w + 560} 0;{seadib_w + 560} 0" keyTimes="0;0.3;1" dur="6s" repeatCount="indefinite"/>
  </rect>
</g>
<text x="{W6/2}" y="158" text-anchor="middle" font-family="{BENG}" font-size="20" fill="{MUTED}">ধন্যবাদ পড়ার জন্য</text>
{tspan("MADE BY HAND IN DHAKA · ADI.PRO.BD · © 2026", W6/2, 176, 11, DIM, spacing=2, extra='text-anchor="middle"')}
</svg>'''
save("footer.svg", footer)

print("done.")
