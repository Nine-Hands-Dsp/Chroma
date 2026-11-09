"""
CHROMA (NINE HANDS | DSP) - visuel v2 du plugin, entierement synthetise (pedale simple, 1235 x 1800 px).

- Boitier : peinture grise texturee « hammertone / ridee » comme la pedale d'origine (vermiculures en relief,
  points clairs, aretes usees qui laissent voir l'alu), arete arrondie, une seule lumiere en haut a gauche.
- Grand ecran (4/5 de la largeur du boitier) : cadre metal + verre sombre ; le contenu est dessine par le plugin.
- Pieces photo du kit NINE HANDS | DSP (assets/kit, photos fournies par l'utilisateur) : embases jack
  (OUT a gauche, IN a droite), LED rouge de bypass, footswitch.
- Textes (CHROMA, POLYPHONIC TUNER, INPUT / OUTPUT) et logo NINE HANDS | DSP : vectoriels, dessines par le plugin
  (ici seulement pour l'apercu, par Chromium).

Repere = pixels de l'image finale (1235 x 1800) ; calcul a 2 px par unite (2470 x 3600, « 4K »).
Sorties : background.png (1235 x 1800 RGBA), background@2x.png (2470 x 3600), led_on.png, glow_red.png,
fs_refl.png, Layout.h, tools/layout.json, design/preview.png (+ design/preview_4k_detail.png).
"""
import os, sys, math, json, subprocess, io, base64
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import photo_controls as PC

AS = 2
OW, OH = 1235, 1800
W, H = OW * AS, OH * AS
L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

# ------------------------------------------------------------------ geometrie (pixels de l'image finale)
JACK_LEN = 212.0
_j = PC.jack_sprite(JACK_LEN, AS, 1)
JACK_PROT = math.floor(_j[1] * AS) / AS
PX0, PW = JACK_PROT, OW - 2 * JACK_PROT
PY0, PH, PR = 0.0, float(OH), 62.0
CX = PX0 + PW / 2
TITLE_Y, SUB_Y = 0.0, 0.0                              # plus de titre (v2 : ecran maximal)
IO_X = 36.0                                           # centre des textes INPUT / OUTPUT depuis le bord du boitier
SX0 = PX0 + 34.0                                      # ecran sans cadre, le plus grand possible (plus de textes INPUT / OUTPUT)
SCREEN = (SX0, 40.0, OW - 2 * SX0, 1345.0)
BEZEL = 0.0
GLASS = SCREEN
JACK_Y = 1110.0
LED = (CX, 1428.0); LED_LENS = 21.0
FS = (CX, 1590.0); FS_FLATS = 206.0
LOGO_C, LOGO_W = (CX, 1742.0), 380.0

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def noise(scale, seed):
    r = np.random.default_rng(seed)
    n = r.standard_normal((H // scale + 3, W // scale + 3)).astype(np.float32)
    return cv2.resize(n, (W + 3 * scale, H + 3 * scale), interpolation=cv2.INTER_CUBIC)[:H, :W]

def over(dst, rgba, x0, y0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0)
    ex, ey = min(w, W - X0), min(h, H - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

print('boitier...')
sd = rrect_sd(UX, UY, PX0, PY0, PW, PH, PR)
body = np.clip(0.5 - sd * AS, 0, 1)

# ---- relief : arete arrondie + peinture ridee (vermiculures) comme la pedale d'origine
EDGE = 11.0
d_in = np.clip(-sd, 0, None)
hgt = np.where(d_in < EDGE, np.sqrt(np.clip(EDGE ** 2 - (EDGE - d_in) ** 2, 0, None)), EDGE).astype(np.float32)
n1 = cv2.GaussianBlur(noise(9, 1), (0, 0), 4.0)
n2 = cv2.GaussianBlur(noise(16, 2), (0, 0), 7.0)
n3 = cv2.GaussianBlur(noise(4, 12), (0, 0), 2.0)
s1, s2, s3 = n1.std(), n2.std(), n3.std()
ridge = 0.75 * np.exp(-(n1 / (0.16 * s1)) ** 2) + 0.55 * np.exp(-(n2 / (0.14 * s2)) ** 2) + 0.25 * np.exp(-(n3 / (0.2 * s3)) ** 2)
ridge = cv2.GaussianBlur(ridge.astype(np.float32), (0, 0), 1.0)
wrink = ridge * 1.1 * np.clip((d_in - EDGE + 2) / 4, 0, 1)          # pas de vermiculures sur l'arete
H_all = hgt + wrink
gy, gx = np.gradient(H_all, 1.0 / AS)
nrm = np.dstack([-gx, -gy, np.ones_like(H_all)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ndl = np.clip(nrm @ L, 0, 1); ndh = np.clip(nrm @ HV, 0, 1)
paint = np.array([34.0, 34.5, 33.0])
encl = paint * (0.55 + 0.75 * ndl)[..., None] + (26 * ndh ** 30 + 9 * ndh ** 5)[..., None]
# lumiere d'ensemble : un peu plus claire en haut a gauche, comme sur la photo d'origine
glob = 1.0 + 0.16 * np.exp(-(((UX - 250) / 700) ** 2 + ((UY - 300) / 900) ** 2)) - 0.10 * np.clip((UY - 1100) / 700, 0, 1)
encl *= glob[..., None]
# points clairs (poussiere de peinture) et grain fin
rng = np.random.default_rng(7)
spk = (rng.random((H, W)) > 0.99992).astype(np.float32)
spk = cv2.GaussianBlur(spk, (0, 0), 0.8) * 6.0
encl += (np.clip(spk, 0, 1) * 80)[..., None]
encl += (rng.standard_normal((H, W)).astype(np.float32) * 2.2)[..., None]
# usure des aretes : l'alu apparait par endroits sur l'arete arrondie
wear_n = cv2.GaussianBlur(noise(2, 9), (0, 0), 0.8) + 0.7 * noise(24, 10)
edge_zone = np.clip(1 - np.abs(d_in - EDGE * 0.45) / (EDGE * 0.7), 0, 1)
wear = np.clip((wear_n - 1.55) * 3.0, 0, 1) * edge_zone
metal = (120 + 70 * ndl + 40 * ndh ** 8)[..., None] * np.array([1.0, 1.0, 0.98])
encl = encl * (1 - wear[..., None]) + metal * wear[..., None]
img = encl * body[..., None]

# ---- ecran : cadre metal brosse + verre sombre en creux
print('ecran...')
sx, sy, sw, sh = SCREEN
sd_o = rrect_sd(UX, UY, sx, sy, sw, sh, 26.0)
sd_i = rrect_sd(UX, UY, *GLASS, 26.0)
# ombre du creux autour du cadre (le cadre est encastre dans la facade)
ring_out = np.clip(0.5 - sd_o * AS, 0, 1)
occ = cv2.GaussianBlur(ring_out, (0, 0), 5 * AS) * (1 - ring_out)
img *= (1 - 0.30 * occ * body)[..., None]
# pas de cadre : le verre affleure la facade (fin joint sombre + petit reflet sur l'arete basse)
edge_lo = np.clip(1 - np.abs(sd_o + 1.0) / 1.6, 0, 1)
img *= (1 - 0.6 * edge_lo * body)[..., None]
# verre : noir avec ombre interne (le contenu est dessine par le plugin)
gmask = np.clip(0.5 - sd_i * AS, 0, 1)
inner = cv2.GaussianBlur((sd_i > -1).astype(np.float32), (0, 0), 7 * AS)
glass = (np.full((H, W), 6.0) * (1 - 0.6 * inner))[..., None] * np.array([1.0, 1.08, 1.04])
img = img * (1 - gmask[..., None]) + glass * gmask[..., None]
# petit liseré lumineux sur l'arête basse droite du verre (côté opposé à la lumière : la lumière qui traverse
# le verre ressort sur le chanfrein bas / droit). Direction : normale sortante du bord, comparée au bas-droite.
gyx, gxx = np.gradient(sd_i, 1.0 / AS)
gn = np.hypot(gxx, gyx) + 1e-6
facing = np.clip((gxx * 0.62 + gyx * 0.78) / gn, 0, 1) ** 1.6          # bord tourné vers le bas-droite
rim = np.clip(1 - np.abs(sd_i + 1.6) / 1.4, 0, 1)                      # fine bande juste à l'intérieur du verre
rim_soft = cv2.GaussianBlur(rim, (0, 0), 1.2) * 0.5
hl = (rim * 0.85 + rim_soft) * facing
img += (hl * 150)[..., None] * np.array([0.92, 0.96, 1.0])

# ---- occlusion autour de la LED et du footswitch
def occlusion(mask, strength=1.0):
    contact = cv2.GaussianBlur(mask, (0, 0), 3.0 * AS)
    soft = cv2.GaussianBlur(mask, (0, 0), 14.0 * AS)
    o = np.clip(contact * 0.55 + soft * 0.9, 0, 0.5) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]

print('LED, footswitch, jacks...')
# LED : bague chromee (rendu) + lentille photo
RING_R = LED_LENS * 1.07                               # LED jaune sans bague metal (seulement son joint sombre)
dl = np.hypot(UX - LED[0], UY - LED[1])
ring_m = np.clip((RING_R - dl) * AS, 0, 1) * np.clip((dl - LED_LENS * 0.98) * AS, 0, 1)
occlusion(np.clip((RING_R - dl) * AS, 0, 1), 0.6)
tr = np.clip((dl - LED_LENS) / (RING_R - LED_LENS), 0, 1)
zr = np.sin(tr * math.pi) * 1.0
nx = np.where(dl > 0, (UX - LED[0]) / np.maximum(dl, 1e-3), 0) * np.cos(tr * math.pi)
ny = np.where(dl > 0, (UY - LED[1]) / np.maximum(dl, 1e-3), 0) * np.cos(tr * math.pi)
nl = np.dstack([-nx * 0.9, -ny * 0.9, 0.35 + zr]); nl /= np.linalg.norm(nl, axis=2, keepdims=True)
dd = np.clip(nl @ L, 0, 1); hh = np.clip(nl @ HV, 0, 1)
chrome = (40 + 120 * dd + 140 * hh ** 30 + 25 * hh ** 4)[..., None] * np.array([0.98, 0.99, 1.0])
LD, LDON, LS = PC.led_sprites(LED_LENS, AS, colour='yellow')
over(img, LD, (LED[0] - LS / 2) * AS, (LED[1] - LS / 2) * AS)

# footswitch (photo du kit)
FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS, refl_colour=(255.0, 190.0, 50.0))
FSREFL[..., 3] = (FSREFL[..., 3].astype(np.float32) * 0.35).astype(np.uint8)   # reflet discret
_fa = np.zeros((H, W), np.float32); _n = FSPR.shape[0]
_x0 = int(round((FS[0] - FS_W / 2) * AS)); _y0 = int(round((FS[1] - FS_W / 2) * AS))
_fa[_y0:_y0 + _n, _x0:_x0 + _n] = np.clip((FSPR[..., 3] / 255.0 - 0.86) / 0.14, 0, 1)
occlusion(_fa)
over(img, FSPR, _x0, _y0)

# embases jack (photo du kit) : OUT a gauche, IN a droite ; transparent autour
alpha = body.copy()
for side in (-1, 1):
    j, jw_u, jh_u = PC.jack_sprite(JACK_LEN, AS, side)
    jh, jw = j.shape[:2]
    x0 = int(round((PX0 * AS - jw) if side < 0 else ((PX0 + PW) * AS)))
    y0 = int(round(JACK_Y * AS - jh / 2))
    occm = np.zeros((H, W), np.float32)
    occm[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    o = np.clip(cv2.GaussianBlur(occm, (0, 0), 3.0 * AS) * 0.9 + cv2.GaussianBlur(occm, (0, 0), 18.0 * AS) * 1.6, 0, 0.62)
    img *= (1.0 - o * (0.25 if side > 0 else 0.12) * body)[..., None]
    over(img, j, x0, y0)
    ja = np.zeros((H, W), np.float32); ja[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
    alpha = np.maximum(alpha, ja)

# ------------------------------------------------------------------ sauvegarde
print('sauvegarde...')
os.makedirs(os.path.join(ROOT, 'design'), exist_ok=True)
rgba2 = np.dstack([np.clip(img, 0, 255), alpha * 255]).astype(np.uint8)
Image.fromarray(rgba2, 'RGBA').save(os.path.join(ROOT, 'background@2x.png'), optimize=True)
def down(a):
    pm = a.astype(np.float32); pm[..., :3] *= pm[..., 3:4] / 255.0
    s = cv2.resize(pm, (OW, OH), interpolation=cv2.INTER_AREA)
    aa = np.maximum(s[..., 3:4], 1e-3)
    s[..., :3] = np.where(s[..., 3:4] > 0.5, s[..., :3] * 255.0 / aa, 0)
    return np.clip(s, 0, 255).astype(np.uint8)
Image.fromarray(down(rgba2), 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)
Image.fromarray(np.clip(LDON, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'led_on.png'))
Image.fromarray(FSREFL, 'RGBA').save(os.path.join(ROOT, 'fs_refl.png'))

# halo de la LED sur la facade (calque alpha)
GR = 150.0
def glow(c, fn):
    x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS)
    size = round(2 * GR * AS)
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
    h1, h2 = 14.0, 50.0
    E = 1.1 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.176 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
    E *= np.clip((GR - d) / 40.0, 0, 1); E[d < RING_R] = 0
    col = np.array([1.0, 0.72, 0.14])
    lum = reg.mean(2, keepdims=True)
    lit = reg + (reg * 2.2 + 12.0 * np.clip(lum / 40.0, 0.3, 1.6)) * E[..., None] * col
    add = lit - reg
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    out = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(os.path.join(ROOT, fn))
    return out.astype(np.float32), (x0p / AS, y0p / AS, size / AS, size / AS)
GLOW, GLR = glow(LED, 'glow_yellow.png')

layout = {"frame": [OW / 2, OH / 2], "screen": [SCREEN[0] / 2, SCREEN[1] / 2, SCREEN[2] / 2, SCREEN[3] / 2],
          "glass": [g / 2 for g in GLASS], "led": [LED[0] / 2, LED[1] / 2], "ledS": LS / 2, "glow": [g / 2 for g in GLR],
          "fs": [FS[0] / 2, FS[1] / 2], "footR": FS_BTN / 2, "fsS": FS_W / 2, "jackY": JACK_Y / 2,
          "box": [PX0 / 2, PY0 / 2, PW / 2, PH / 2], "title": [CX / 2, TITLE_Y / 2], "sub": [CX / 2, SUB_Y / 2],
          "logo": [LOGO_C[0] / 2, LOGO_C[1] / 2, LOGO_W / 2],
          "ioOut": [(PX0 + IO_X) / 2, JACK_Y / 2], "ioIn": [(PX0 + PW - IO_X) / 2, JACK_Y / 2]}
json.dump(layout, open(os.path.join(HERE, 'layout.json'), 'w'), indent=1)

# ------------------------------------------------------------------ apercu : LED allumee + calque vectoriel (Chromium)
prev = img.copy()
over(prev, GLOW, GLR[0] * AS, GLR[1] * AS)
over(prev, LDON, (LED[0] - LS / 2) * AS, (LED[1] - LS / 2) * AS)
over(prev, FSREFL.astype(np.float32), (FS[0] - FS_W / 2) * AS, (FS[1] - FS_W / 2) * AS)
Image.fromarray(np.dstack([np.clip(prev, 0, 255), alpha * 255]).astype(np.uint8), 'RGBA').save('/tmp/claude-0/chroma_prev_base.png')
print(json.dumps(layout))
