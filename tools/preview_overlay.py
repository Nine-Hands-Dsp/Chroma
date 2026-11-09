"""
CHROMA v2 - apercu : calque vectoriel (textes, logo, contenu de l'ecran) rendu par Chromium a 2470 x 3600,
pose sur le fond genere par make_art.py. Ce calque montre ce que dessinera le plugin.
Usage : python3 tools/preview_overlay.py [poly|mono|strobe]
"""
import os, sys, json, base64
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LY = json.load(open(os.path.join(HERE, 'layout.json')))
K = 2.0                                                   # layout.json est en unites du plugin (image / 2)
def u(v): return v * K                                     # -> pixels de l'image finale 1235 x 1800
MODE = sys.argv[1] if len(sys.argv) > 1 else 'poly'
uri = lambda p: 'file://' + os.path.abspath(p)
FONTS = f"""
@font-face {{ font-family: PopB; src: url({uri(ROOT + '/assets/fonts/Poppins-Bold.ttf')}); }}
@font-face {{ font-family: PopM; src: url({uri(ROOT + '/assets/fonts/Poppins-Medium.ttf')}); }}
@font-face {{ font-family: PopL; src: url({uri(ROOT + '/assets/fonts/Poppins-Light.ttf')}); }}
@font-face {{ font-family: Plex; src: url({uri(ROOT + '/IBMPlexMono-SemiBold.ttf')}); }}
"""
AMBER, AMB_DIM, GREEN, GRN_DIM, ORANGE, GREY = '#ffb23a', '#3a2808', '#5dff8a', '#12351f', '#e0662a', '#c9ced3'

gx, gy, gw, gh = [u(v) for v in LY['glass']]
cx = u(LY['title'][0])
s = []
# ---- serigraphie
for key, txt, rot in ():   # plus de textes INPUT / OUTPUT
    x, y = u(LY[key][0]), u(LY[key][1])
    s.append(f'<text x="{x}" y="{y}" transform="rotate({rot} {x} {y})" font-family="PopM" font-size="27" letter-spacing="6" fill="#dfe2e5" text-anchor="middle" dominant-baseline="central">{txt}</text>')
logo = open(os.path.join(ROOT, 'assets', 'NineHandsLogo.svg')).read()
if os.environ.get('CHROMA_FINISH') == 'gloss_white': logo = logo.replace('#FFFFFF', '#000000').replace('#ffffff', '#000000')
lw = u(LY['logo'][2]); lh = lw * 244 / 2602
lx, ly = u(LY['logo'][0]) - lw / 2, u(LY['logo'][1]) - lh / 2
s.append(f'<image href="data:image/svg+xml;base64,{base64.b64encode(logo.encode()).decode()}" x="{lx}" y="{ly}" width="{lw}" height="{lh}" opacity="0.88"/>')

# ---- contenu de l'ecran
g = []
pad = 34
X0, X1 = gx + pad, gx + gw - pad
# rangee 1 : selecteur de mode (remplace le potard MODE) + reference (remplace REF)
modes = ['MONO', 'POLY', 'STROBE']; act = modes.index(MODE.upper())
bx, by, bw_, bh = X0, gy + 30, 112, 62
for i, m in enumerate(modes):
    w_ = bw_ + (30 if m == 'STROBE' else 0)
    on = i == act
    g.append(f'<rect x="{bx}" y="{by}" width="{w_}" height="{bh}" rx="9" fill="{ORANGE if on else "none"}" fill-opacity="{0.95 if on else 0}" stroke="{ORANGE}" stroke-opacity="{1 if on else 0.55}" stroke-width="2.5"/>')
    g.append(f'<text x="{bx + w_ / 2}" y="{by + bh / 2 + 1}" font-family="Plex" font-size="27" fill="{"#140c06" if on else ORANGE}" text-anchor="middle" dominant-baseline="central">{m}</text>')
    bx += w_ + 12
rx1 = X1
g.append(f'<rect x="{rx1 - 250}" y="{by}" width="250" height="{bh}" rx="9" fill="none" stroke="{ORANGE}" stroke-opacity="0.55" stroke-width="2.5"/>')
g.append(f'<text x="{rx1 - 225}" y="{by + bh / 2 + 1}" font-family="Plex" font-size="26" fill="{ORANGE}" dominant-baseline="central">&#9664;</text>')
g.append(f'<text x="{rx1 - 125}" y="{by + bh / 2 + 1}" font-family="Plex" font-size="31" fill="{ORANGE}" text-anchor="middle" dominant-baseline="central">A=440</text>')
g.append(f'<text x="{rx1 - 25}" y="{by + bh / 2 + 1}" font-family="Plex" font-size="26" fill="{ORANGE}" text-anchor="end" dominant-baseline="central">&#9654;</text>')
# rangee 2 : accordage (remplace le potard TUNING) : fleches + menu deroulant
ty = by + bh + 22; th = 84
tuned = MODE == 'poly'
tc = AMBER
g.append(f'<rect x="{X0}" y="{ty}" width="{X1 - X0}" height="{th}" rx="11" fill="{tc}" fill-opacity="0.07" stroke="{tc}" stroke-opacity="0.6" stroke-width="2.5"/>')
g.append(f'<text x="{X0 + 34}" y="{ty + th / 2 + 1}" font-family="Plex" font-size="34" fill="{tc}" dominant-baseline="central">&#9664;</text>')
g.append(f'<text x="{X1 - 34}" y="{ty + th / 2 + 1}" font-family="Plex" font-size="34" fill="{tc}" text-anchor="end" dominant-baseline="central">&#9654;</text>')
g.append(f'<line x1="{X0 + 92}" y1="{ty + 14}" x2="{X0 + 92}" y2="{ty + th - 14}" stroke="{tc}" stroke-opacity="0.3" stroke-width="2"/>')
g.append(f'<line x1="{X1 - 92}" y1="{ty + 14}" x2="{X1 - 92}" y2="{ty + th - 14}" stroke="{tc}" stroke-opacity="0.3" stroke-width="2"/>')
g.append(f'<text x="{X0 + 116}" y="{ty + th / 2 + 1}" font-family="Plex" font-size="24" fill="{tc}" fill-opacity="0.6" dominant-baseline="central">G6</text>')
g.append(f'<text x="{(X0 + X1) / 2 + 6}" y="{ty + th / 2 + 1}" font-family="Plex" font-size="46" fill="{tc}" text-anchor="middle" dominant-baseline="central">DROP B &#9662;</text>')
g.append(f'<text x="{X1 - 116}" y="{ty + th / 2 + 1}" font-family="Plex" font-size="21" fill="{tc}" fill-opacity="0.55" text-anchor="end" dominant-baseline="central">6/81</text>')
top = ty + th + 26
g.append(f'<rect x="{X0}" y="{top}" width="{X1 - X0}" height="2" fill="{AMBER}" fill-opacity="0.22"/>')

def seg(x, y, w, h, col, lit):
    if lit:
        return (f'<rect x="{x - 6}" y="{y - 5}" width="{w + 12}" height="{h + 10}" rx="7" fill="{col}" fill-opacity="0.12"/>'
                f'<rect x="{x - 3}" y="{y - 2.5}" width="{w + 6}" height="{h + 5}" rx="5" fill="{col}" fill-opacity="0.25"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{col}"/>'
                f'<rect x="{x + w * 0.3}" y="{y + h * 0.2}" width="{w * 0.4}" height="{h * 0.6}" rx="2" fill="#fff" fill-opacity="0.35"/>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{col}"/>'

area_top, area_bot = top + 22, gy + gh - 70
if MODE == 'poly':
    notes = [('C#4', 0.4, True), ('G#3', -6.0, True), ('E3', 0.0, True), ('B2', 9.0, True), ('F#2', -1.2, True), ('B1', -17.0, True)]
    n = len(notes); rowH = (area_bot - area_top) / n
    sx0, sx1 = X0 + 150, X1
    segs, mid = 25, 12; pitch = (sx1 - sx0) / segs; sw_ = pitch * 0.62
    cxm = sx0 + pitch * (mid + 0.5)
    for i, (nm, c, act_) in enumerate(notes):
        cy = area_top + rowH * (i + 0.5)
        ok = abs(c) <= 2
        col = GREEN if ok else AMBER
        g.append(f'<text x="{X0}" y="{cy + 2}" font-family="Plex" font-size="{min(64, rowH * 0.62):.0f}" fill="{col}" dominant-baseline="central">{nm}</text>')
        lit = max(0, min(segs - 1, mid + round(c / 4)))
        for k in range(segs):
            hh = rowH * (0.66 if k == mid else 0.48)
            x = sx0 + pitch * k + (pitch - sw_) / 2
            if k == lit: g.append(seg(x, cy - hh / 2, sw_, hh, col, True))
            elif (mid < k < lit) or (lit < k < mid): g.append(seg(x, cy - hh / 2, sw_, hh, AMBER + '4d', False))
            else: g.append(seg(x, cy - hh / 2, sw_, hh, GRN_DIM if k == mid else AMB_DIM, False))
    yl = gy + gh - 38
    for t, x, a in (('-50', sx0, 'start'), ('0', cxm, 'middle'), ('+50', sx1, 'end')):
        g.append(f'<text x="{x}" y="{yl}" font-family="Plex" font-size="30" fill="{GREY}" fill-opacity="0.75" text-anchor="{a}" dominant-baseline="central">{t}</text>')
else:
    c = -11.1
    g.append(f'<text x="{(X0 + X1) / 2 - 30}" y="{area_top + (area_bot - area_top) * 0.30}" font-family="Plex" font-size="420" fill="{AMBER}" text-anchor="middle" dominant-baseline="central">E</text>')
    g.append(f'<text x="{(X0 + X1) / 2 + 135}" y="{area_top + (area_bot - area_top) * 0.30 + 115}" font-family="Plex" font-size="140" fill="{AMBER}" dominant-baseline="central">2</text>')
    segs, mid = 41, 20; sx0, sx1 = X0 + 10, X1 - 10; pitch = (sx1 - sx0) / segs; sw_ = pitch * 0.6; cyb = area_top + (area_bot - area_top) * 0.68
    for k in range(segs):
        if k == mid: continue
        hh = 100 if (k - mid) % 4 == 0 else 70
        g.append(seg(sx0 + pitch * k + (pitch - sw_) / 2, cyb - hh / 2, sw_, hh, AMB_DIM, False))
    cxm = sx0 + pitch * (mid + 0.5)
    mw, mh, cw_, ch_ = sw_ * 1.1, 220, sw_ * 0.8, 164
    g.append(f'<rect x="{cxm - mw / 2}" y="{cyb - mh / 2}" width="{mw}" height="{mh}" rx="3" fill="#fff" fill-opacity="0.95"/>')
    cx2 = cxm + c / 2.5 * pitch
    g.append(seg(cx2 - cw_ / 2, cyb - ch_ / 2, cw_, ch_, AMBER, True))
    g.append(f'<text x="{sx0}" y="{cyb + 145}" font-family="Plex" font-size="30" fill="{GREY}" fill-opacity="0.7" dominant-baseline="central">-50</text>')
    g.append(f'<text x="{sx1}" y="{cyb + 145}" font-family="Plex" font-size="30" fill="{GREY}" fill-opacity="0.7" text-anchor="end" dominant-baseline="central">+50</text>')
    g.append(f'<text x="{(X0 + X1) / 2}" y="{gy + gh - 62}" font-family="Plex" font-size="96" fill="{AMBER}" text-anchor="middle" dominant-baseline="central">-11.1 c</text>')
    g.append(f'<text x="{X0}" y="{gy + gh - 62}" font-family="Plex" font-size="32" fill="{GREY}" fill-opacity="0.75" dominant-baseline="central">81.88 Hz</text>')
    g.append(f'<text x="{X1}" y="{gy + gh - 62}" font-family="Plex" font-size="32" fill="{GREY}" fill-opacity="0.75" text-anchor="end" dominant-baseline="central">STRING 6</text>')
# reflet du verre
g.append(f'<path d="M{gx},{gy} L{gx + gw * 0.62},{gy} L{gx},{gy + gh * 0.55} Z" fill="url(#gl)"/>')
s.append(f'<clipPath id="gc"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="26"/></clipPath><g clip-path="url(#gc)">' + ''.join(g) + '</g>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2470" height="3600" viewBox="0 0 1235 1800">
<defs><style>{FONTS}</style><linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
{''.join(s)}</svg>'''
html = f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}</style></head><body>{svg}</body></html>'
hp = '/tmp/claude-0/chroma_overlay.html'; open(hp, 'w').write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 2470, 'height': 3600})
    pg.goto('file://' + hp); pg.wait_for_timeout(500)
    pg.screenshot(path='/tmp/claude-0/chroma_overlay.png', omit_background=True); b.close()
FIN = os.environ.get('CHROMA_FINISH', 'wrinkle')
base = Image.open(f'/tmp/claude-0/chroma_prev_base_{FIN}.png').convert('RGBA')
ov = Image.open('/tmp/claude-0/chroma_overlay.png').convert('RGBA')
base.alpha_composite(ov)
os.makedirs(os.path.join(ROOT, 'design'), exist_ok=True)
base.save(os.path.join(ROOT, 'design', f'preview_4k_{MODE}{"" if FIN == "wrinkle" else "_" + FIN}.png'))
base.resize((1235, 1800), Image.LANCZOS).save(os.path.join(ROOT, 'design', f'preview_{MODE}{"" if FIN == "wrinkle" else "_" + FIN}.png'))
print('ok')
