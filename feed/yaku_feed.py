#!/usr/bin/env python3
"""YAKÜ Gutachten – Feed-Post-Generator (Instagram 1080×1350, 4:5).

Erzeugt aus einem Eintrag in feed/themen-feed.json fertige PNGs im festen YAKÜ-Look
(Creme/Navy/Gold, Fraunces/Inter/JetBrains Mono, Original-Logo, Linien-Auto mit Messkreis).

  python3 feed/yaku_feed.py <thema-id> [ausgabeordner]

Typen:
  einzelbild  – ein Bild: große Headline oben, Auto mit Messkreis + 3 Labels, Claim, CTA
  karussell   – 5 Slides: Cover (navy|cream) · 3 Inhalts-Slides · CTA-Slide
"""
import json, os, sys, re
from string import Template

HERE = os.path.dirname(os.path.abspath(__file__))
A = "../assets"  # relativ zu feed/out/<id>/

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
WA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'

BASE = Template("""<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
@font-face{font-family:"Fraunces";src:url($A/fonts/fraunces-var.woff2) format("woff2");font-weight:100 900;}
@font-face{font-family:"Inter";src:url($A/fonts/inter-var.woff2) format("woff2");font-weight:100 900;}
@font-face{font-family:"JBM";src:url($A/fonts/jbm-500.woff2) format("woff2");font-weight:500;}
:root{--navy:#071B3A;--gold:#D8A52C;--gold2:#E0B64D;--golddark:#856A2D;--cream:#F4F1EA;--blue:#1556C0;--slate:#4F5A69}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:Inter,sans-serif;color:var(--navy);-webkit-font-smoothing:antialiased;position:relative;background:var(--cream)}
.serif{font-family:Fraunces,serif;font-variation-settings:"SOFT" 0,"WONK" 0;font-weight:500}
.mono{font-family:JBM,monospace;font-weight:500;text-transform:uppercase}
.abs{position:absolute}
.cream{background:radial-gradient(900px 600px at 90% 0%,rgba(255,255,255,.7),rgba(255,255,255,0) 60%),var(--cream)}
.navy{background:radial-gradient(800px 520px at 50% 45%,rgba(21,86,192,.28),rgba(21,86,192,0) 70%),linear-gradient(180deg,#0A2348 0%,var(--navy) 55%,#061630 100%)}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(244,241,234,.10) 1.1px,transparent 1.2px);background-size:24px 24px;background-position:12px 12px;-webkit-mask-image:radial-gradient(700px 520px at 60% 55%,#000,transparent)}
.logo{overflow:hidden;position:absolute}
.logo img{position:absolute;width:480px;height:317px;transform-origin:0 0}
.eyebrow{display:flex;align-items:center;gap:18px;font-size:16px;letter-spacing:.24em;color:var(--golddark)}
.eyebrow i{display:block;width:56px;height:1.5px;background:var(--gold)}
.eyebrow.ondark{color:var(--gold2)}
.foot{position:absolute;left:76px;right:76px;bottom:56px;display:flex;justify-content:space-between;align-items:center;font-size:15px;letter-spacing:.22em;padding-top:22px;border-top:1px solid rgba(7,27,58,.14);color:#5E6877}
.foot.ondark{border-top-color:rgba(244,241,234,.16);color:rgba(244,241,234,.7)}
.foot .r{display:flex;align-items:center;gap:12px}
.foot svg{width:22px;height:22px}
.chip{display:inline-flex;align-items:center;gap:10px;height:40px;padding:0 16px;border:1px solid rgba(244,241,234,.22);border-radius:6px;font-size:14px;letter-spacing:.16em;color:rgba(244,241,234,.88)}
.chip i{width:7px;height:7px;border-radius:50%;background:var(--gold)}
.btn{display:inline-flex;align-items:center;gap:18px;height:84px;padding:0 34px 0 36px;border-radius:6px;background:var(--gold);color:var(--navy);font-weight:700;font-size:28px;letter-spacing:.06em;text-transform:uppercase;box-shadow:0 1px 0 rgba(255,255,255,.35) inset,0 14px 34px rgba(0,0,0,.28)}
.btn svg{width:30px;height:30px}
.url{font-size:34px;font-weight:600;color:#fff;letter-spacing:-.01em}
.channels{margin-top:8px;font-size:13px;letter-spacing:.2em;color:rgba(244,241,234,.72);display:flex;gap:14px;justify-content:flex-end;align-items:center}
.channels svg{width:16px;height:16px}
.goldline{position:absolute;left:0;top:0;width:1080px;height:3px;background:linear-gradient(90deg,var(--gold),var(--gold2) 60%,rgba(216,165,44,0))}
.fit{display:inline-block;white-space:nowrap}
</style></head><body>$body
<script>document.fonts.ready.then(()=>{document.querySelectorAll('[data-fit]').forEach(el=>{const max=+el.dataset.fit;let fs=parseFloat(getComputedStyle(el).fontSize);while(el.scrollWidth>max&&fs>40){fs-=2;el.style.fontSize=fs+'px'}});document.body.dataset.ready=1})</script></body></html>""")

CAR = open(os.path.join(HERE, "assets", "car.svg"), encoding="utf-8").read()
CAR_CLEAN = re.sub(r'<!-- leader \+ legend -->.*?(?=\n  </svg>)', '', CAR, flags=re.S) \
    .replace('<svg class="car" viewBox="0 0 1080 420"', '<svg class="car" viewBox="0 70 1080 310"')

# Symbole im Messkreis (Mittelpunkt 812/960)
ICONS = {
  "check": '<path d="M752 962 L796 1006 L878 916" fill="none" stroke="#E0B64D" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
  "euro":  '<text x="812" y="1004" text-anchor="middle" font-family="Fraunces" font-size="150" font-weight="500" fill="{ink}">€</text>',
  "frage": '<text x="812" y="1010" text-anchor="middle" font-family="Fraunces" font-size="160" font-weight="500" fill="{ink}">?</text>',
  "uhr":   '<g fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"><circle cx="812" cy="960" r="58"/><path d="M812 925 V962 L840 980"/></g>',
  "pin":   '<g fill="none" stroke="{ink}" stroke-width="7" stroke-linejoin="round"><path d="M812 1022 s-50-46-50-86 a50 50 0 0 1 100 0 c0 40-50 86-50 86z"/><circle cx="812" cy="936" r="17"/></g>',
  "dokument": '<g fill="none" stroke="{ink}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"><path d="M778 896 h50 l28 28 v100 h-78 z"/><path d="M828 896 v28 h28"/><path d="M796 962 h42 M796 986 h42"/></g>',
  "auge":  '<g fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M748 960 q64-70 128 0 q-64 70-128 0z"/><circle cx="812" cy="960" r="20"/></g>',
  "liste": '<g fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"><path d="M792 922 h56 M792 960 h56 M792 998 h56"/><circle cx="770" cy="922" r="4"/><circle cx="770" cy="960" r="4"/><circle cx="770" cy="998" r="4"/></g>',
}

def logo(x, y, scale):
    w, h = round(436 * scale), round(222 * scale)
    return (f'<div class="logo" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<img src="{A}/logo.svg" alt="YAKÜ Gutachten" '
            f'style="transform:scale({scale});left:{-22*scale}px;top:{-48*scale}px"></div>')

def foot(n, total, dark=False, left="YAKÜ Gutachten"):
    cls = "foot mono ondark" if dark else "foot mono"
    return f'<div class="{cls}"><span>{left}</span><span class="r">{n:02d} / {total:02d}&nbsp;&nbsp;{ARROW}</span></div>'

def marker(cx, cy, r, inner, color="#E0B64D"):
    o = r + 22
    return f'''<svg class="abs" style="left:{cx-o-30}px;top:{cy-o-30}px" width="{2*o+60}" height="{2*o+60}" viewBox="{cx-o-30} {cy-o-30} {2*o+60} {2*o+60}">
 <g fill="none" stroke="{color}">
  <circle cx="{cx}" cy="{cy}" r="{r}" stroke-width="2.4"/>
  <circle cx="{cx}" cy="{cy}" r="{o}" stroke-width="1.2" stroke-opacity=".55" stroke-dasharray="2 7"/>
  <line x1="{cx}" y1="{cy-o-4}" x2="{cx}" y2="{cy-o-18}" stroke-width="2.4"/>
  <line x1="{cx}" y1="{cy+o+4}" x2="{cx}" y2="{cy+o+18}" stroke-width="2.4"/>
  <line x1="{cx-o-4}" y1="{cy}" x2="{cx-o-18}" y2="{cy}" stroke-width="2.4"/>
  <line x1="{cx+o+4}" y1="{cy}" x2="{cx+o+18}" y2="{cy}" stroke-width="2.4"/>
 </g>{inner}</svg>'''

def esc(s):
    return s.replace("&", "&amp;").replace("&amp;nbsp;", "&nbsp;")

DISCLAIMER = "Allgemeine Information · keine Rechtsberatung"

# ------------------------------------------------------------------ Bausteine
def cover(c, total):
    icon = ICONS.get(c.get("icon", "check"), ICONS["check"])
    if c.get("stil", "navy") == "navy":
        icon = icon.replace("{ink}", "#F4F1EA")
        return f'''<div class="abs navy" style="inset:0"></div><div class="dots"></div>
<div class="abs" style="left:76px;top:0;width:300px;height:176px;background:var(--cream);border-radius:0 0 10px 10px;box-shadow:0 18px 40px rgba(0,0,0,.25)"></div>
{logo(104, 30, .56)}
<div class="abs eyebrow mono ondark" style="left:76px;top:292px"><i></i>{esc(c["eyebrow"])}</div>
<h1 class="abs serif" style="left:70px;top:340px;font-size:{c.get("fs",146)}px;line-height:.98;letter-spacing:-.04em;color:var(--cream)"><span class="fit" data-fit="930">{esc(c["zeile1"])}</span><br><span class="fit" data-fit="930" style="color:var(--gold2)">{esc(c["zeile2"])}</span></h1>
<p class="abs" style="left:78px;top:676px;width:560px;font-size:34px;line-height:1.38;color:rgba(244,241,234,.86)">{esc(c["sub"])}</p>
{marker(812, 960, 120, icon)}
{foot(1, total, dark=True, left="Wischen für mehr")}'''
    icon = icon.replace("{ink}", "#071B3A").replace('stroke="#E0B64D"', 'stroke="#B88A1F"')
    return f'''<div class="abs cream" style="inset:0"></div>
{logo(76, 58, .55)}
<div class="abs eyebrow mono" style="left:76px;top:292px"><i></i>{esc(c["eyebrow"])}</div>
<h1 class="abs serif" style="left:70px;top:340px;font-size:{c.get("fs",146)}px;line-height:.98;letter-spacing:-.04em;color:var(--navy)"><span class="fit" data-fit="930">{esc(c["zeile1"])}</span><br><span class="fit" data-fit="930" style="color:var(--blue)">{esc(c["zeile2"])}</span></h1>
<p class="abs" style="left:78px;top:676px;width:560px;font-size:34px;line-height:1.38;color:var(--slate)">{esc(c["sub"])}</p>
{marker(812, 960, 120, icon, color="#B88A1F")}
{foot(1, total, left="Wischen für mehr")}'''

def content(s, n, total, dark, disclaimer):
    bg = '<div class="abs navy" style="inset:0"></div><div class="dots"></div>' if dark else '<div class="abs cream" style="inset:0"></div>'
    ink = "var(--cream)" if dark else "var(--navy)"
    em = "var(--gold2)" if dark else "var(--blue)"
    supc = "rgba(244,241,234,.8)" if dark else "var(--slate)"
    num = "var(--gold2)" if dark else "var(--gold)"
    text = esc(s["text"]).replace("<em>", f'<em style="font-style:normal;color:{em}">')
    return f'''{bg}
<div class="abs mono" style="left:76px;top:70px;font-size:15px;letter-spacing:.24em;color:{'rgba(244,241,234,.6)' if dark else '#5E6877'}">YAKÜ Gutachten</div>
<div class="abs" style="left:76px;right:76px;top:130px;bottom:140px;display:flex;flex-direction:column;justify-content:center">
  <div class="serif" style="margin-left:-8px;font-size:220px;line-height:.9;letter-spacing:-.04em;color:{num};font-weight:400">{n-1:02d}</div>
  <div class="eyebrow mono {'ondark' if dark else ''}" style="margin-top:44px"><i></i>{esc(s["kicker"])}</div>
  <p class="serif" style="margin-top:30px;margin-left:-4px;width:930px;font-size:{s.get("fs",76)}px;line-height:1.07;letter-spacing:-.03em;color:{ink}">{text}</p>
  <div style="margin-top:48px;width:64px;height:2px;background:{num}"></div>
  <p style="margin-top:30px;width:860px;font-size:33px;line-height:1.45;color:{supc}">{esc(s["support"])}</p>
</div>
{foot(n, total, dark=dark, left=DISCLAIMER if disclaimer else "YAKÜ Gutachten")}'''

def cta(c, n, total):
    return f'''<div class="abs cream" style="left:0;top:0;width:1080px;height:620px"></div>
{logo(76, 56, .55)}
<div class="abs eyebrow mono" style="right:76px;top:92px"><i></i>Persönlich für Sie da</div>
<h2 class="abs serif" style="left:70px;top:236px;font-size:{c.get("fs",112)}px;line-height:1;letter-spacing:-.04em"><span class="fit" data-fit="930">{esc(c["zeile1"])}</span><br><span class="fit" data-fit="930" style="color:var(--blue)">{esc(c["zeile2"])}</span></h2>
<p class="abs" style="left:78px;top:486px;width:930px;font-size:32px;line-height:1.4;color:var(--slate)">{esc(c["sub"])}</p>
<div class="abs navy" style="left:0;top:620px;width:1080px;height:730px;overflow:hidden">
  <div class="dots"></div><div class="goldline"></div>
  <div class="abs" style="left:76px;top:40px;display:flex;gap:12px"><div class="chip mono"><i></i>München &amp; Umgebung</div><div class="chip mono"><i></i>Termin in 24–48 h</div></div>
  <div class="abs" style="left:0;top:96px;width:1080px;height:310px">{CAR_CLEAN.replace('class="car"', 'class="car" style="width:1080px;height:310px"')}</div>
  <div class="abs serif" style="left:76px;top:434px;font-size:46px;letter-spacing:-.025em;color:var(--cream)">Ihr Schaden. <span style="color:var(--gold2)">Klar bewertet.</span></div>
  <div class="abs" style="left:76px;right:76px;top:520px;display:flex;align-items:flex-end;justify-content:space-between">
    <div class="btn">Jetzt Schaden melden {ARROW}</div>
    <div style="text-align:right"><div class="url">yaku-gutachten.de</div>
      <div class="channels mono">{WA}WhatsApp <span style="opacity:.5">·</span> {PHONE}24/7</div></div>
  </div>
  <div class="abs mono" style="left:76px;right:76px;bottom:28px;display:flex;justify-content:space-between;font-size:13px;letter-spacing:.22em;color:rgba(244,241,234,.55)"><span>Link im Profil</span><span>{n:02d} / {total:02d}</span></div>
</div>'''

def einzelbild(e):
    l1, l2, l3 = [esc(x).upper() for x in e["labels"]]
    car = CAR.replace("{L1}", l1).replace("{L2}", l2).replace("{L3}", l3) \
             .replace('<svg class="car"', '<svg class="car" style="position:absolute;left:0;top:26px;width:1080px;height:420px"')
    return f'''<div class="abs cream" style="left:0;top:0;width:1080px;height:660px"></div>
{logo(76, 46, .5)}
<div class="abs eyebrow mono" style="right:76px;top:96px"><i></i>{esc(e.get("eyebrow","Kfz-Sachverständige · München"))}</div>
<div class="abs" style="left:66px;right:60px;top:170px;height:466px;display:flex;flex-direction:column;justify-content:flex-end">
  <h1 class="serif"><span class="fit" data-fit="940" style="font-size:{e.get("fs1",262)}px;line-height:.9;letter-spacing:-.045em;color:var(--navy)">{esc(e["zeile1"])}</span></h1>
  <h2 class="serif" style="margin-top:24px;margin-left:10px"><span class="fit" data-fit="930" style="font-size:{e.get("fs2",96)}px;line-height:1;letter-spacing:-.035em;color:var(--blue)">{esc(e["zeile2"])}</span></h2>
  <p style="margin-top:34px;margin-left:12px;font-size:28px;line-height:1.42;color:#4F5A69">{esc(e["sub1"])}<br><b style="color:var(--navy);font-weight:600">{esc(e["sub2"])}</b></p>
</div>
<div class="abs navy" style="left:0;top:660px;width:1080px;height:690px;overflow:hidden">
  <div class="dots"></div><div class="goldline"></div>
  <div class="abs" style="left:76px;top:36px;display:flex;gap:12px"><div class="chip mono"><i></i>München &amp; Umgebung</div><div class="chip mono"><i></i>Termin in 24–48 h</div></div>
  {car}
  <div class="abs serif" style="left:76px;top:472px;font-size:50px;letter-spacing:-.025em;color:var(--cream)">Ihr Schaden. <span style="color:var(--gold2)">Klar bewertet.</span></div>
  <div class="abs" style="left:76px;right:76px;top:556px;display:flex;align-items:flex-end;justify-content:space-between">
    <div class="btn">Jetzt Schaden melden {ARROW}</div>
    <div style="text-align:right"><div class="url">yaku-gutachten.de</div>
      <div class="channels mono">{WA}WhatsApp <span style="opacity:.5">·</span> {PHONE}24/7</div></div>
  </div>
</div>'''

# ------------------------------------------------------------------ Ausgabe
def build_pages(t):
    pages = []
    if t["typ"] == "einzelbild":
        pages.append(einzelbild(t["bild"]))
    elif t["typ"] == "karussell":
        k = t["karussell"]; total = 2 + len(k["slides"])
        pages.append(cover(k["cover"], total))
        for i, s in enumerate(k["slides"]):
            dark = (i % 2 == 1)  # creme · navy · creme
            pages.append(content(s, i + 2, total, dark, k.get("disclaimer", False)))
        pages.append(cta(k["cta"], total, total))
    else:
        raise SystemExit("Unbekannter Typ: " + t["typ"])
    return pages

def render(t, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    rel = os.path.relpath(os.path.join(HERE, "assets"), outdir)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for i, body in enumerate(build_pages(t), 1):
            html = os.path.join(outdir, f"{i:02d}.html")
            open(html, "w", encoding="utf-8").write(BASE.substitute(A=rel, body=body.replace(A + "/", rel + "/")))
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
            pg.goto("file://" + os.path.abspath(html))
            pg.wait_for_selector("body[data-ready]", timeout=15000)
            pg.wait_for_timeout(300)
            hi = os.path.join(outdir, f"{i:02d}_hi.png")
            pg.screenshot(path=hi); pg.close()
            png = os.path.join(outdir, f"{i:02d}.png")
            Image.open(hi).convert("RGB").resize((1080, 1350), Image.LANCZOS).save(png, optimize=True)
            os.remove(hi)
            files.append(png)
        b.close()
    return files

def contact_sheet(files, out):
    from PIL import Image
    ims = [Image.open(f) for f in files]
    W, H = 432, 540
    sheet = Image.new("RGB", (W * len(ims) + 10 * (len(ims) - 1), H), "white")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((W, H), Image.LANCZOS), (k * (W + 10), 0))
    sheet.save(out)
    return out

if __name__ == "__main__":
    tid = sys.argv[1]
    data = json.load(open(os.path.join(HERE, "themen-feed.json"), encoding="utf-8"))
    t = next(x for x in data["themen"] if x["id"] == tid)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "out", tid)
    files = render(t, out)
    print("\n".join(files))
    print("SHEET", contact_sheet(files, os.path.join(out, "vorschau.png")))
