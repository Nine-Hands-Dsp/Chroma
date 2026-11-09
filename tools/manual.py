# Chroma (NINE HANDS | DSP) - notice PDF en francais uniquement, couverture noire « minimale » commune a toutes les notices.
# Usage : python3 tools/manual.py [fichier PDF de sortie]   (defaut : docs/Chroma_Notice_FR_v<VERSION>.pdf)
# Illustrations : tools/manual_assets/ (captures du rendu reel du plugin v2, outil de rendu Linux de l'editeur).
# Les accordages d'usine sont lus directement dans Tunings.h.
# Polices : assets/fonts (Poppins, DejaVu Sans pour les symboles ★ ✎ ◄ ►).
# Pas d'historique des versions dans la notice (demande de l'utilisateur).
NAME = "Chroma"
import re as _re, os as _os
VERSION = _re.search(r"project\(\w+ VERSION ([0-9.]+)", open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "CMakeLists.txt")).read()).group(1)   # version du plugin
TITLE = "CHROMA"
FOOTER = {"fr": "Chroma (NINE HANDS | DSP) · v" + VERSION}
from reportlab.lib import colors
ACC = colors.HexColor("#E0662A")       # orange de l'ecran (boutons de mode)
H1COL = colors.HexColor("#1B1D22"); H2COL = ACC
HCELLBG = colors.HexColor("#1B1D22"); HCELLTXT = colors.white
# ---------- mise en page commune (style maison NINE HANDS | DSP) ----------
import os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", NAME + "_Notice_FR_v" + VERSION + ".pdf")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("PopR", "Poppins-Regular"), ("Barlow", "BarlowCondensed-ExtraBold"), ("Dej", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))
addMapping("PopL", 0, 0, "PopL"); addMapping("PopL", 1, 0, "PopM"); addMapping("PopL", 0, 1, "PopL"); addMapping("PopL", 1, 1, "PopM")
addMapping("Pop", 0, 0, "Pop"); addMapping("Pop", 1, 0, "PopB"); addMapping("Pop", 0, 1, "Pop"); addMapping("Pop", 1, 1, "PopB")

DARK = colors.HexColor("#1B1D22"); GREY = colors.HexColor("#6B6F78"); LIGHT = colors.HexColor("#F4F1EC"); RULE = colors.HexColor("#DDD8D0")
SYMBOLS = "★✎◄►↔→⇄"   # absents de Poppins : DejaVu Sans

def sym(t):
    for c in SYMBOLS: t = t.replace(c, '<font name="Dej">' + c + '</font>')
    return t

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=17, leading=21, textColor=H1COL, spaceAfter=6, spaceBefore=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=11.5, leading=15, textColor=H2COL, spaceAfter=3, spaceBefore=7, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=4),
    "li": ParagraphStyle("li", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=2, leftIndent=9, bulletIndent=0),
    "note": ParagraphStyle("note", fontName="PopL", fontSize=8.4, leading=12, textColor=DARK, backColor=LIGHT, borderPadding=5, spaceBefore=4, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="PopL", fontSize=7.6, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="PopL", fontSize=7.9, leading=10.2, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=7.9, leading=10.2, textColor=DARK),
    "hcell": ParagraphStyle("hcell", fontName="PopM", fontSize=7.9, leading=10.2, textColor=HCELLTXT),
    "cover": ParagraphStyle("cover", fontName="PopM", fontSize=30, leading=36, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#B9B9B9"), alignment=TA_CENTER),
    "coverver": ParagraphStyle("coverver", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#DADADA"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=7.5, leading=10, textColor=ACC),
}
def P(t, s="p"): return Paragraph(sym(t), st[s])
def bullets(items): return [Paragraph(sym(i), st["li"], bulletText="•") for i in items]
def table(rows, widths, header=True, first_bold=False):
    data = []
    for r, row in enumerate(rows):
        data.append([P(c, "hcell" if (header and r == 0) else ("cellb" if (first_bold and k == 0) else "cell")) for k, c in enumerate(row)])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
             ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), HCELLBG), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    t.setStyle(TableStyle(style)); return t
def img(name, width=None, height=None):
    path = name if os.path.isabs(name) else os.path.join(ASSETS, name)
    im = Image.open(path)
    if width is None: width = height * im.width / im.height
    if height is None: height = width * im.height / im.width
    return RLImage(path, width=width, height=height)
def side(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
                           ("LEFTPADDING", (1, 0), (1, 0), 10)]))
    return t

W = A4[0] - 36 * mm
COVER_SUB = "Accordeur polyphonique"          # mention courte : type d'effet seulement
PEDAL_H, PEDAL_TOP, NAME_TOP, SUB_TOP, LOGO_W, LOGO_BOTTOM, LANG_TOP, BAND_H = 82, 84, 194, 208, 38, 22, 18, 3   # mm

def cover_pedal_image():
    """Pedale detouree (canal alpha de background.png) sur sol noir : leger reflet + halo tres doux de la couleur d'accent."""
    import numpy as np
    ped = Image.open(os.path.join(ASSETS, "cover_pedal.png")).convert("RGBA")
    w, h = ped.size; mx, my, refl = int(w * 0.45), int(h * 0.12), int(h * 0.28)
    W2, H2 = w + 2 * mx, h + my + refl + int(h * 0.05)
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
    cx, cy = W2 / 2, my + h * 0.55
    d = np.hypot((xx - cx) / (W2 * 0.5), (yy - cy) / (H2 * 0.5))
    halo = np.clip(1 - d, 0, 1) ** 2.2 * 0.16
    acc = np.array([0xE0, 0x66, 0x2A], np.float32)
    base = np.zeros((H2, W2, 3), np.float32) + halo[..., None] * acc
    canvas = Image.fromarray(base.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    r = ped.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, w, refl))
    ra = np.array(r).astype(np.float32); fade = np.linspace(0.22, 0, refl)[:, None]
    ra[..., 3] *= fade; canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (mx, my + h + 2))
    canvas.alpha_composite(ped, (mx, my))
    p = "/tmp/claude-0/chroma_cover_pedal.jpg"; canvas.convert("RGB").save(p, quality=93)
    return p, (W2, H2), (mx, my, w, h)

def cover(t, cover_img=None, cover_w=None):
    return [Spacer(1, 1), NextPageTemplate("p"), PageBreak()]

def draw_cover(c):
    PW, PH = A4
    c.setFillColor(colors.black); c.rect(0, 0, PW, PH, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, PW, BAND_H * mm, stroke=0, fill=1)
    def centred(txt, font, size, top_mm, col, track):
        cap = pdfmetrics.getFont(font).face.ascent / 1000.0 * size * 0.70 / 0.93 if False else size * 0.70
        w = pdfmetrics.stringWidth(txt, font, size) + track * (len(txt) - 1)
        to = c.beginText(); to.setFont(font, size); to.setFillColor(col); to.setCharSpace(track)
        to.setTextOrigin((PW - w) / 2, PH - top_mm * mm - cap); to.textOut(txt); c.drawText(to)
    centred("FRANÇAIS", "PopM", 8.5, LANG_TOP, colors.HexColor("#F2A27E"), 1.0)
    path, (W2, H2), (mx, my, w, h) = cover_pedal_image()
    k = PEDAL_H * mm / h
    x0 = (PW - W2 * k) / 2; ytop = PH - PEDAL_TOP * mm + my * k
    c.drawImage(path, x0, ytop - H2 * k, W2 * k, H2 * k)
    centred(NAME.upper(), "Barlow", 30, NAME_TOP, colors.white, 15)
    centred(COVER_SUB, "PopR", 10, SUB_TOP, colors.HexColor("#BDC4B8"), 1.5)
    lg = os.path.join(ASSETS, "logo_white.png"); im = Image.open(lg)
    lw = LOGO_W * mm; lh = lw * im.height / im.width
    c.drawImage(lg, (PW - lw) / 2, LOGO_BOTTOM * mm, lw, lh, mask="auto")

def build(sections, title):
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=18 * mm,
                          title=title, author="NINE HANDS | DSP")
    lang = {"v": "fr"}
    def deco(c, d):
        c.saveState()
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1)
        c.setFont("PopL", 7); c.setFillColor(GREY)
        c.drawString(18 * mm, 10 * mm, FOOTER[lang["v"]])
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(d.page))
        c.restoreState()
    def cover_bg(c, d):
        c.saveState(); draw_cover(c); c.restoreState()
    class SetLang(Spacer):
        def __init__(self, l): Spacer.__init__(self, 0, 0); self.l = l
        def draw(self): lang["v"] = self.l
    fr = lambda: Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[fr()], onPage=cover_bg), PageTemplate(id="p", frames=[fr()], onPage=deco)])
    story = []
    for i, (l, flow) in enumerate(sections):
        if i: story += [NextPageTemplate("cover"), PageBreak()]
        story += [SetLang(l)] + flow
    doc.build(story)
    print(OUT)
# ---------- contenu de la notice CHROMA (vérifié contre PluginEditor.cpp / PluginProcessor.cpp / Tunings.h) ----------
import re

def factory_tunings():
    """Accordages d'usine lus dans Tunings.h (catégorie, nom FR, notes), avec les noms anglais de displayName()."""
    src = open(os.path.join(ROOT, "Tunings.h"), encoding="utf-8").read()
    cats = dict(re.findall(r'const char\* (\w+) = "([^"]+)";', src))
    rows = [(cats[c], n, notes) for c, n, notes in re.findall(r'add \((\w+),\s*"([^"]+)",\s*"([^"]+)"\)', src)]
    en_names = dict(re.findall(r'\{ "([^"]+)", "([^"]+)" \}', src.split("displayName")[1].split("displayCategory")[0]))
    en_cats = dict(re.findall(r'\{ "([^"]+)", "([^"]+)" \}', src.split("displayCategory")[1]))
    return rows, en_names, en_cats

TUNINGS, EN_NAMES, EN_CATS = factory_tunings()
assert len(TUNINGS) == 82, len(TUNINGS)

def tuning_block(cat, lang):
    rows = [[cat, ""]]
    for c, n, notes in TUNINGS:
        if c == cat: rows.append([n, notes])
    t = table(rows, [27 * mm, W / 2 - 30 * mm])
    t.setStyle(TableStyle([("SPAN", (0, 0), (1, 0))]))
    return t

def two_cols(a, b):
    t = Table([[a, b]], colWidths=[W / 2, W / 2])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    return t

CATS = []
for c, _, _ in TUNINGS:
    if c not in CATS: CATS.append(c)
G6, OPEN, G7, G8, B4, B5, B6 = CATS

T = {
"fr": dict(
 lang="FRANÇAIS", sub="Accordeur polyphonique guitare &amp; basse &nbsp;·&nbsp; Mono · Poly · Strobe &nbsp;·&nbsp; VST3",
 ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 intro_t="1. Présentation",
 intro="<b>CHROMA</b> est un accordeur VST3 conçu par NINE HANDS | DSP pour guitare et basse, avec l'allure d'une vraie pédale : boîtier noir en peinture froissée, grand écran tactile, LED jaune et footswitch. Grattez toutes les cordes d'un coup et voyez celles qui sont fausses (<b>POLY</b>), affinez une corde sur un grand affichage (<b>MONO</b>) ou avec la précision d'un stroboscope (<b>STROBE</b>). Son format pédale et son mode polyphonique s'inspirent du <b>TC Electronic PolyTune</b>. Il a été pensé dès le départ pour les accordages très graves : Sol#0, Fa0, Mi0 et même Ré0 (environ 18 Hz) sont mesurés de façon fiable. CHROMA s'appelait auparavant Tuna.",
 does_t="Ce qu'il fait",
 does=["<b>Trois modes</b> : MONO (grande note + barre ±50 cents), POLY (toutes les cordes d'un coup), STROBE (bandes mobiles, ±0,1 cent).",
       "<b>Très grave</b> : d'environ 16 Hz à 1,6 kHz ; les erreurs d'octave sur les fondamentales faibles sont détectées et corrigées.",
       "<b>82 accordages d'usine</b> : standard, drop et accordages métal graves, open tunings, guitares 7 et 8 cordes, basses 4, 5 et 6 cordes.",
       "<b>Favoris et accordages perso</b> (jusqu'à 10 cordes), communs à toutes les instances.",
       "<b>Accordage silencieux</b> : footswitch TUNE / MUTE avec coupure douce. L'accordeur fonctionne toujours, coupé ou non.",
       "<b>MIDI Learn</b> sur chaque commande (clic droit ; aucun CC assigné par défaut), Program Change = favoris."],
 does_note="Le son passe directement (aucune latence, aucune coloration). Une copie de l'entrée est analysée dans un thread séparé : l'accordage ne coûte rien au thread audio.",
 inst_t="2. Installation",
 inst=["<b>Windows</b> : copiez <b>Chroma.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
       "<b>macOS</b> (universel, Apple Silicon et Intel) : copiez <b>Chroma.vst3</b> dans <b>~/Library/Audio/Plug-Ins/VST3/</b>, puis lancez une fois dans le Terminal : <i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Chroma.vst3</i>.",
       "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. Le plugin apparaît sous le nom <b>Chroma (NINE HANDS | DSP)</b>.",
       "Si vous aviez installé <b>Tuna.vst3</b> (ou CHROMA.vst3 de la version 1.1.0), supprimez-le : CHROMA garde le même identifiant interne pour que Reaper le retrouve dans vos projets, et vos accordages perso et favoris de Tuna sont repris automatiquement."],
 ui_t="3. L'interface",
 ui_cap="Tout se règle directement sur l'écran tactile : il n'y a plus de potards. Les numéros renvoient au tableau ci-dessous et à la section 4.",
 ui_rows=[["N°", "Élément", "Fonction"],
   ["1", "MONO · POLY · STROBE", "Boutons de mode : le mode actif est allumé en orange. Clic = choisit le mode."],
   ["2", "◄ A=440 ►", "Référence du La4 (430 à 450 Hz) : flèches, molette ; double-clic sur la valeur = 440 Hz."],
   ["3", "◄", "Accordage précédent."],
   ["4", "Barre d'accordage", "Accordage choisi, son type (G6 = guitare 6 cordes, B5 = basse 5 cordes, P = perso) et sa position dans la liste. Clic au centre : ouvre le menu des accordages. Passe au vert quand toutes les cordes sont justes."],
   ["5", "►", "Accordage suivant."],
   ["6", "Affichage", "Lignes des cordes (POLY), grande note (MONO) ou bandes (STROBE). Les messages (nouvel accordage, MIDI Learn...) s'y affichent en bandeau."],
   ["7", "Échelle", "-50 / 0 / +50 cents."],
   ["8", "LED", "Jaune = sortie coupée (MUTE)."],
   ["9", "TUNE / MUTE", "Footswitch : coupe la sortie."],
   ["10 / 11", "OUT / IN", "Sortie à gauche, entrée à droite (vues sur les tranches de la pédale)."]],
 ctl_t="4. Les commandes",
 ctl=[("Boutons de mode (1)", "Trois boutons en haut de l'écran : <b>MONO</b>, <b>POLY</b>, <b>STROBE</b>. Un clic choisit le mode, la molette au-dessus des boutons passe au mode voisin. CHROMA s'ouvre en <b>MONO</b> ; les projets enregistrés gardent leur mode."),
      ("Référence ◄ A=440 ► (2)", "Hauteur du La4 de 430 à 450 Hz par pas de 1 Hz : clic sur ◄ ou ►, ou molette sur la case. <b>Double-clic sur la valeur = 440 Hz</b>. Tous les accordages la suivent."),
      ("Barre d'accordage (3, 4, 5)", "◄ et ► (ou la molette sur la barre) passent à l'accordage précédent / suivant ; le nom du nouvel accordage s'affiche brièvement. Un clic au centre de la barre ouvre le menu des accordages. À gauche, le type d'instrument (G6, G7, B5, P...) ; à droite, la position dans la liste (par exemple 8/82). Le logo CHROMA, en haut à droite, n'est pas une commande.")],
 menu_t="Le menu des accordages",
 menu="Le menu s'ouvre sur l'écran en anglais ; le petit bouton <b>FR</b> de son en-tête passe les menus de l'écran en français (<b>EN</b> pour revenir), choix mémorisé pour toutes les instances. Il a trois onglets :",
 menu_b=["<b>ALL</b> : tous les accordages d'usine, groupés par instrument, puis vos accordages perso.",
         "<b>★ FAVORITES</b> : les accordages marqués d'une étoile (clic sur l'étoile en bout de ligne). Le Program Change les sélectionne.",
         "<b>✎ CUSTOM</b> : vos propres accordages. <i>+ New tuning</i> copie l'accordage courant ; le crayon modifie un accordage."],
 menu_cap="Onglets ALL, FAVORITES et CUSTOM.",
 cust_t="Accordages perso",
 cust=["Dans l'éditeur, réglez le nom, le nombre de cordes (1 à 10), puis chaque corde avec − / + (demi-ton) et « / » (octave). Les fréquences suivent la référence courante. <b>Save</b>, <b>Delete</b> ou <b>Cancel</b>.",
       "Accordages perso et favoris sont stockés dans un fichier commun à toutes les instances (clic droit &gt; <i>Show tunings file</i>) : <i>%APPDATA%\\NINE HANDS | DSP\\Chroma\\library.xml</i> sous Windows, <i>~/Library/Application Support/NINE HANDS | DSP/Chroma/library.xml</i> sous macOS. L'accordage choisi est aussi enregistré dans le projet."],
 fs_t="5. Footswitch, LED et modes",
 fs_h="Footswitch TUNE / MUTE",
 fs="Un clic sur le footswitch coupe la sortie avec un fondu court, sans clic ; la <b>LED jaune</b> s'allume (en fondu). Recliquez pour réentendre la guitare. L'accordeur fonctionne toujours, coupé ou non. Le mode actif se lit sur les boutons en haut de l'écran.",
 poly_h="POLY - toutes les cordes d'un coup",
 poly="Choisissez l'accordage, grattez franchement toutes les cordes à vide et laissez-les sonner. Une ligne par corde (la plus aiguë en haut) ; le segment allumé montre l'écart : à gauche = trop bas, à droite = trop haut, un segment = 4 cents. Une corde passe au <b>vert</b> à ±2 cents ; quand toutes sont vertes, la barre d'accordage passe au vert aussi.",
 poly_b=["La mesure se stabilise en 0,3 s environ à la guitare et 0,6 à 1 s sur les cordes de basse les plus graves (un cycle de Fa0 dure 46 ms).",
         "Une corde non jouée reste sombre. Quand vous arrêtez de jouer, la dernière valeur reste affichée puis s'estompe lentement.",
         "Si vous jouez une seule note qui n'appartient pas à l'accordage, l'écran passe tout seul en vue mono (le bouton POLY reste allumé)."],
 mono_h="MONO - une corde, grand affichage",
 mono="Jouez une note : l'écran affiche son nom et son octave, l'écart en cents (au 0,1 cent), la fréquence et, si la note appartient à l'accordage, le numéro de corde (corde 1 = la plus aiguë). La valeur est marquée ~ au tout début (estimation grossière), puis passe à la mesure de phase précise. Le fin repère blanc est la cible ; le petit curseur jaune est la note jouée et glisse à gauche si elle est basse, à droite si elle est haute. À ±1 cent le repère passe au vert.",
 strobe_h="STROBE - précision stroboscopique",
 strobe="Les bandes défilent à une vitesse proportionnelle à l'écart, comme un accordeur stroboscopique mécanique : défilement à droite = trop haut, à gauche = trop bas. Accordez jusqu'à ce que les bandes s'arrêtent ; elles passent au vert à ±1 cent. Idéal pour le réglage de l'intonation et l'accordage très précis.",
 midi_t="6. MIDI",
 midi="Chaque commande de la pédale peut être pilotée par un pédalier ou un contrôleur MIDI (par exemple une M-Vave Chocolate Plus). <b>Aucun CC n'est assigné par défaut</b> : vous choisissez le CC de chaque commande avec le <b>MIDI Learn</b>.",
 learn_h="MIDI Learn",
 learn=["<b>Clic droit sur une commande</b> (un bouton de mode, la case de référence, ◄ ou ► de la barre d'accordage, ou le footswitch TUNE / MUTE) puis <b>MIDI Learn: &lt;commande&gt; (CC n / none)</b>. Un clic droit au centre de la barre d'accordage propose ses deux sens : <i>Next tuning</i> et <i>Previous tuning</i>.",
        "L'écran affiche <b>MIDI LEARN: move a control for X</b>. Bougez une pédale ou appuyez sur un bouton du contrôleur : le premier CC reçu est assigné (il n'agit pas sur l'accordeur) et l'écran confirme <b>X = CC n</b> pendant 2 secondes.",
        "<b>Clear MIDI: &lt;commande&gt;</b> supprime l'assignation ; <b>Cancel MIDI learn</b> (ou rechoisir le même Learn) arrête l'attente.",
        "Un CC déjà utilisé par une autre commande lui est retiré : un CC pilote toujours une seule commande.",
        "Clic droit ailleurs &gt; <b>MIDI</b> : <i>Learn</i> de chaque commande avec son CC actuel (ou <i>none</i>), <b>Clear all MIDI assignments</b>, le canal MIDI (<b>MIDI channel</b> : Omni ou 1 à 16) et le type de footswitch (pédale à accrochage ou momentanée).",
        "Les assignations sont <b>enregistrées avec le projet</b>. Un projet enregistré avec une version précédente qui utilisait encore les anciens numéros de CC d'usine s'ouvre sans aucune assignation ; un projet où vous aviez changé une assignation garde ses assignations."],
 midi_rows=[["Commande", "Type"],
   ["Footswitch TUNE / MUTE", "Footswitch. À accrochage (défaut) : valeur ≥ 64 = coupé, &lt; 64 = son. Momentané : chaque appui (≥ 64) bascule."],
   ["Mode", "Sélecteur 3 positions : 0-42 MONO, 43-85 POLY, 86-127 STROBE."],
   ["► - accordage suivant", "Déclencheur : chaque valeur ≥ 64 = accordage suivant."],
   ["◄ - accordage précédent", "Déclencheur : chaque valeur ≥ 64 = accordage précédent."],
   ["Référence A4", "Continu : 0-127 = 430-450 Hz."],
   ["Program Change", "Le programme n choisit le favori n (programme 0 = premier favori), ou l'accordage n s'il n'y a pas de favoris. Aucun apprentissage nécessaire."]],
 midi_note="Mute, Mode et Reference A4 sont aussi des paramètres de l'hôte : automatisables ou assignables depuis le DAW (Reaper : Param &gt; Learn).",
 win_t="7. Fenêtre",
 win=["Clic droit n'importe où (hors commande) &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b>, <b>100 %</b> (la taille actuelle est cochée) ; <i>(default)</i> est indiqué à côté de la taille par défaut. Vous pouvez aussi tirer le coin inférieur droit (proportions conservées). La fenêtre ne peut jamais être plus petite que 60 %.",
      "<b>Plugin size &gt; Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de CHROMA (60 % au départ). Ce réglage est commun à toutes les instances et enregistré sur l'ordinateur (<i>settings.xml</i> dans le dossier NINE HANDS | DSP\\Chroma, à côté du fichier des accordages) ; la fenêtre ouverte prend aussi cette taille tout de suite.",
      "Dès que vous changez la taille d'une fenêtre (menu ou coin), cette instance mémorise sa propre taille dans le projet, et cette taille reste prioritaire sur la taille par défaut à la réouverture du projet.",
      "Les menus clic droit (fond sombre, icônes, coche bleue, comme dans Octopus) s'ouvrent toujours à l'endroit du clic. Le même menu contient <b>MIDI</b> (section 6), <b>Custom tunings...</b> (ouvre l'onglet CUSTOM) et <b>Show tunings file</b>. CHROMA n'a pas de ligne d'état séparée : les messages (nouvel accordage, invites et confirmations du MIDI Learn) s'affichent en bandeau sur l'écran."],
 pre_t="8. Accordages d'usine (presets)",
 pre="Les presets de CHROMA sont ses 82 accordages d'usine. Les cordes sont listées de la plus grave à la plus aiguë. Les noms s'affichent en anglais ou en français selon le bouton EN / FR du menu.",
 bass_t="Accordages d'usine : basses",
 tips_t="9. Conseils",
 tips=["Placez CHROMA <b>en premier</b> dans la chaîne Reaper, avant les saturations et avant la simulation d'ampli (Ampire, Impulse...), pour le signal le plus propre.",
       "Accordages graves de 7 cordes (drop G, Sol standard...) : attaquez franchement au médiator ou au pouce, près du micro manche si possible : la fondamentale est plus forte.",
       "Laissez sonner la corde une seconde : les 50 premières ms (attaque) sont ignorées et la mesure s'affine tant que la corde sonne.",
       "En POLY, étouffez les cordes que vous n'accordez pas si elles sonnent par sympathie.",
       "Open tunings avec cordes à l'octave (Open D, DADGAD...) : la corde à l'octave partage toutes ses harmoniques avec la grave ; POLY indique le bon sens, finissez en MONO pour le dernier cent.",
       "Apprenez au footswitch un switch MIDI à accrochage et servez-vous-en comme pédale d'accordage silencieux entre les morceaux."],
 tr_t="Dépannage",
 tr=[["Symptôme", "Solution"],
     ["Rien à l'écran", "Vérifiez le niveau d'entrée (l'accordeur réagit dès -66 dBFS environ) et que la piste est armée / en écoute."],
     ["Mauvaise octave", "Jouez un peu plus fort ou plus près du manche ; le test d'octave a besoin de quelques cycles de la fondamentale."],
     ["Une ligne POLY reste sombre", "Cette corde n'a pas été détectée : regrattez, ou vérifiez que l'accordage choisi correspond à l'instrument."],
     ["Le MIDI ne fait rien", "Aucun CC n'est assigné par défaut : apprenez-en un (clic droit sur la commande &gt; MIDI Learn). Vérifiez ensuite le canal MIDI (clic droit &gt; MIDI &gt; MIDI channel) et que la piste reçoit le MIDI du contrôleur."],
     ["Plugin absent", "Re-scannez les plug-ins dans le DAW ; sous macOS lancez la commande xattr (section 2)."]],
 spec_t="10. Caractéristiques techniques",
 spec=[["Élément", "Valeur"], ["Format", "VST3 - Windows 64 bits, macOS universel (Apple Silicon + Intel)"], ["Inspiré de", "TC Electronic PolyTune"], ["Interface", "pédale plein cadre, écran tactile (modes, référence, accordages), LED jaune, footswitch TUNE / MUTE"],
       ["Modes", "MONO, POLY, STROBE"], ["Plage", "environ 16 Hz (Do0) à 1,6 kHz"],
       ["Précision MONO / STROBE", "±0,1 cent sur une note tenue (testé de Ré0 à Mi6)"],
       ["Précision POLY", "±0,1-0,5 cent sur les cordes à partiel isolé ; ±1-3 cents sur les cordes partageant toutes leurs harmoniques (octaves)"],
       ["Temps de stabilisation", "guitare environ 0,3 s ; basse grave (Fa0, Mi0) environ 0,8-1,2 s"], ["Référence", "A4 = 430 ... 450 Hz (440 Hz)"],
       ["Accordages", "82 accordages d'usine, favoris, accordages perso jusqu'à 10 cordes"],
       ["Latence / son", "aucune - le son passe sans modification ; coupure douce"], ["CPU", "environ 4 % d'un cœur (thread d'analyse séparé)"],
       ["MIDI", "MIDI Learn sur chaque commande (aucun CC assigné par défaut), canal Omni / 1-16, footswitch à accrochage ou momentané, Program Change = favoris ; enregistré avec le projet"],
       ["Fenêtre", "Plugin size 60 % / 75 % / 100 % (60 % = 338 x 493 px), taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais plus petite que 60 % ; redimensionnement par le coin"],
       ["Stabilité Windows", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement de la fenêtre piloté par un timer avec chien de garde"]]),
}

def section(lang):
    t = T[lang]; f = cover(t)
    f += [P(t["intro_t"], "h1"), P(t["intro"]), P(t["does_t"], "h2")] + bullets(t["does"]) + [P(t["does_note"], "note")]
    f += [P(t["inst_t"], "h1")] + bullets(t["inst"]) + [PageBreak()]
    f += [P(t["ui_t"], "h1"), P(t["ui_cap"]), Spacer(1, 2 * mm),
          side(img("annotated.jpg", 82 * mm), table(t["ui_rows"], [11 * mm, 25 * mm, W - 86 * mm - 36 * mm]), 86 * mm), PageBreak()]
    f += [P(t["ctl_t"], "h1")]
    for h, x in t["ctl"]: f += [P(h, "h2"), P(x)]
    f += [P(t["menu_t"], "h2"), P(t["menu"])] + bullets(t["menu_b"])
    tabs = Table([[img("menu_all.png", (W - 8) / 3), img("menu_favorites.png", (W - 8) / 3), img("menu_custom.png", (W - 8) / 3)]],
                 colWidths=[W / 3] * 3)
    tabs.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)]))
    f += [Spacer(1, 2 * mm), tabs, P(t["menu_cap"], "small")]
    f += [side(img("tuning_editor.png", 52 * mm), [P(t["cust_t"], "h2")] + [P(x) for x in t["cust"]], 56 * mm), PageBreak()]
    f += [P(t["fs_t"], "h1"), P(t["fs_h"], "h2"), P(t["fs"])]
    f += [side(img("poly.png", 50 * mm), [P(t["poly_h"], "h2"), P(t["poly"])], 54 * mm)] + bullets(t["poly_b"])
    f += [side(img("mono.png", 50 * mm), [P(t["mono_h"], "h2"), P(t["mono"])], 54 * mm)]
    f += [side(img("strobe.png", 50 * mm), [P(t["strobe_h"], "h2"), P(t["strobe"])], 54 * mm), PageBreak()]
    f += [P(t["midi_t"], "h1"), P(t["midi"]), P(t["learn_h"], "h2")] + bullets(t["learn"])
    f += [Spacer(1, 2 * mm), KeepTogether(table(t["midi_rows"], [52 * mm, W - 52 * mm], first_bold=True)), P(t["midi_note"], "note")]
    f += [KeepTogether([P(t["win_t"], "h1"), P(t["win"][0])])] + [P(x) for x in t["win"][1:]] + [PageBreak()]
    f += [P(t["pre_t"], "h1"), P(t["pre"])]
    f += [two_cols([tuning_block(G6, lang), Spacer(1, 3 * mm), tuning_block(G7, lang)],
                   [tuning_block(OPEN, lang), Spacer(1, 3 * mm), tuning_block(G8, lang)]), PageBreak()]
    f += [P(t["bass_t"], "h1"), two_cols([tuning_block(B4, lang), Spacer(1, 3 * mm), tuning_block(B6, lang)], [tuning_block(B5, lang)]), PageBreak()]
    f += [P(t["tips_t"], "h1")] + bullets(t["tips"])
    f += [KeepTogether([P(t["tr_t"], "h2"), table(t["tr"], [40 * mm, W - 40 * mm], first_bold=True)]), PageBreak()]
    f += [KeepTogether([P(t["spec_t"], "h1"), table(t["spec"], [40 * mm, W - 40 * mm], first_bold=True)])]
    return f

build([("fr", section("fr"))], "Chroma " + VERSION + " - Notice")
