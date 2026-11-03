# CHROMA (Studio Wiga) - notice PDF bilingue (partie anglaise complete, puis partie francaise complete).
# Usage : python3 tools/manual.py [fichier PDF de sortie]   (defaut : docs/CHROMA_Manual_EN-FR_v<VERSION>.pdf)
# Illustrations : tools/manual_assets/ (captures du rendu reel du plugin reprises de la notice 1.3.0 ; aucune ne montre
# le menu clic droit, elles restent justes). Les accordages d'usine sont lus directement dans Tunings.h.
# Polices : assets/fonts (Poppins, DejaVu Sans pour les symboles ★ ✎ ◄ ►).
# Pas d'historique des versions dans la notice (demande de l'utilisateur).
NAME = "CHROMA"
import re as _re, os as _os
VERSION = _re.search(r"project\(\w+ VERSION ([0-9.]+)", open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "CMakeLists.txt")).read()).group(1)   # version du plugin
TITLE = "CHROMA"
FOOTER = {"en": "CHROMA " + VERSION + " · Studio Wiga", "fr": "CHROMA " + VERSION + " · Studio Wiga"}
from reportlab.lib import colors
ACC = colors.HexColor("#E2733B")       # orange de la pedale
H1COL = colors.HexColor("#1B1D22"); H2COL = ACC
HCELLBG = colors.HexColor("#1B1D22"); HCELLTXT = colors.white
# ---------- mise en page commune (style maison Studio Wiga) ----------
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
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", NAME + "_Manual_EN-FR_v" + VERSION + ".pdf")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Dej", "DejaVuSans")):
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
def cover(t, cover_img, cover_w):
    return [Spacer(1, 2 * mm), P(t["lang"], "coverlang"), Spacer(1, 6 * mm), img(cover_img, cover_w), Spacer(1, 4 * mm),
            P(" ".join(TITLE), "cover"), Spacer(1, 2 * mm), P(t["sub"], "coversub"), Spacer(1, 1 * mm), P(t["ver"], "coverver"),
            Spacer(1, 7 * mm), img("logo_white.png", 46 * mm), NextPageTemplate("p"), PageBreak()]

def build(sections, title):
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=18 * mm,
                          title=title, author="Studio Wiga")
    lang = {"v": "en"}
    def deco(c, d):
        c.saveState()
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1)
        c.setFont("PopL", 7); c.setFillColor(GREY)
        c.drawString(18 * mm, 10 * mm, FOOTER[lang["v"]])
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(d.page))
        c.restoreState()
    def cover_bg(c, d):
        c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1); c.restoreState()
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
    rows = [[(EN_CATS.get(cat, cat) if lang == "en" else cat), ""]]
    for c, n, notes in TUNINGS:
        if c == cat: rows.append([EN_NAMES.get(n, n) if lang == "en" else n, notes])
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
"en": dict(
 lang="ENGLISH", sub="Polyphonic tuner for guitar &amp; bass &nbsp;·&nbsp; Mono · Poly · Strobe &nbsp;·&nbsp; VST3",
 ver="User manual &nbsp;·&nbsp; version " + VERSION,
 intro_t="1. Introduction",
 intro="<b>CHROMA</b> is a VST3 tuner designed by Studio Wiga for guitar and bass, with the look of a real stompbox. Strum all your strings at once and see which ones are off (<b>POLY</b>), fine-tune one string with a large display (<b>MONO</b>) or with stroboscopic accuracy (<b>STROBE</b>). Its pedal format and polyphonic mode are inspired by the <b>TC Electronic PolyTune</b>. It was built from the ground up for very low tunings: G#0, F0, E0 and even D0 (about 18 Hz) are measured reliably. CHROMA was previously called Tuna.",
 does_t="What it does",
 does=["<b>Three modes</b>: MONO (large note + ±50 cent bar), POLY (all strings at once), STROBE (moving bands, ±0.1 cent).",
       "<b>Very low range</b>: about 16 Hz to 1.6 kHz; octave errors on weak fundamentals are detected and corrected.",
       "<b>82 factory tunings</b>: standard, drop and low metal tunings, open tunings, 7 and 8-string guitars, 4, 5 and 6-string basses.",
       "<b>Favourites and custom tunings</b> (up to 10 strings), shared by every instance.",
       "<b>Silent tuning</b>: TUNE / MUTE footswitch with a smooth mute. The tuner keeps working, muted or not.",
       "<b>MIDI Learn</b> on every control (right-click; no CC is assigned by default), Program Change = favourites."],
 does_note="The sound goes straight through (no latency, no colouring). A copy of the input is analysed in a separate thread, so tuning never costs anything on the audio thread.",
 inst_t="2. Installation",
 inst=["<b>Windows</b>: copy <b>Chroma.vst3</b> into <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
       "<b>macOS</b> (universal, Apple Silicon and Intel): copy <b>Chroma.vst3</b> into <b>~/Library/Audio/Plug-Ins/VST3/</b>, then run once in Terminal: <i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/Chroma.vst3</i>.",
       "<b>Reaper</b>: Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. The plug-in appears as <b>Chroma (Studio Wiga)</b>.",
       "If you had installed <b>Tuna.vst3</b> (or CHROMA.vst3 from version 1.1.0), delete it: CHROMA keeps the same internal ID so Reaper finds it in your existing projects, and your Tuna custom tunings and favourites are imported automatically."],
 ui_t="3. The interface",
 ui_cap="Every control drawn on the pedal is live. Numbers refer to the table below and to section 4.",
 ui_rows=[["No.", "Element", "Function"],
   ["1", "Mode name", "MONO, POLY or STROBE. Click: next mode."],
   ["2", "Tuning menu", "Selected tuning and its type (G6 = 6-string guitar, B5 = 5-string bass, P = custom). Click: opens the menu. Turns green when every string is in tune."],
   ["3", "Reference", "Pitch of A4 (430 to 450 Hz)."],
   ["4", "Display", "String rows (POLY), large note (MONO) or bands (STROBE). MIDI Learn and other messages appear here as a banner."],
   ["5", "Scale", "-50 / 0 / +50 cents."],
   ["6", "Mode LEDs", "Amber LED above the active mode."],
   ["7", "MODE", "3-position selector."],
   ["8", "TUNING", "Endless encoder: next / previous tuning; click opens the menu."],
   ["9", "◄ ►", "Previous / next tuning."],
   ["10", "REF", "Reference A4."],
   ["11", "MUTE LED", "Red = output muted."],
   ["12", "TUNE / MUTE", "Footswitch: mutes the output."],
   ["13 / 14", "INPUT / OUTPUT", "Input on the left, output on the right."]],
 ctl_t="4. Controls",
 ctl=[("MODE (7)", "3-position selector: MONO, POLY, STROBE. Drag, scroll or click (click = next mode). Clicking the mode name on the screen (1) does the same. CHROMA opens in <b>MONO</b>; saved projects keep their mode."),
      ("TUNING (8) and ◄ ► (9)", "Endless encoder: one notch (drag or scroll) = next / previous tuning, exactly like the arrows. A click on the knob, or on the tuning name (2), opens the tuning menu. The new tuning name is shown briefly on the screen."),
      ("REF (10)", "Pitch of A4 from 430 to 450 Hz in 1 Hz steps (drag or scroll); <b>double-click = 440 Hz</b>. All tunings follow it; the value is shown at the top right of the screen (3).")],
 menu_t="The tuning menu",
 menu="The menu opens over the screen in English; the small <b>FR</b> button in its header switches the screen menus to French (<b>EN</b> to go back), and the choice is remembered for every instance. It has three tabs:",
 menu_b=["<b>ALL</b>: every factory tuning, grouped by instrument, then your custom tunings.",
         "<b>★ FAVORITES</b>: the tunings you starred (click the star at the end of a line). Program Change selects them.",
         "<b>✎ CUSTOM</b>: your own tunings. <i>+ New tuning</i> copies the current one; the pencil edits a tuning."],
 menu_cap="ALL, FAVORITES and CUSTOM tabs.",
 cust_t="Custom tunings",
 cust=["In the editor, set the name, the number of strings (1 to 10), then each string with − / + (semitone) and « / » (octave). Frequencies follow the current reference. <b>Save</b>, <b>Delete</b> or <b>Cancel</b>.",
       "Custom tunings and favourites are stored in a file shared by all instances (right-click &gt; <i>Show tunings file</i>): <i>%APPDATA%\\Studio Wiga\\Chroma\\library.xml</i> on Windows, <i>~/Library/Application Support/Studio Wiga/Chroma/library.xml</i> on macOS. The selected tuning is also saved inside your project."],
 fs_t="5. Footswitch, LEDs and modes",
 fs_h="TUNE / MUTE footswitch",
 fs="A click on the footswitch mutes the output with a short, click-free fade; the red <b>MUTE</b> LED lights up. Click again to hear your guitar. The tuner keeps working, muted or not. The amber LED above MONO, POLY or STROBE shows the active mode.",
 poly_h="POLY - all strings at once",
 poly="Choose your tuning, strum all open strings firmly and let them ring. One row per string (highest at the top); the lit segment shows the deviation: left = flat, right = sharp, one segment = 4 cents. A string turns <b>green</b> within ±2 cents; when all strings are green, the tuning name turns green too.",
 poly_b=["Readings settle in about 0.3 s on guitar and 0.6 to 1 s on the lowest bass strings (one cycle of F0 lasts 46 ms).",
         "A string you did not play stays dim. After you stop playing, the last value stays on screen and slowly fades.",
         "If you play a single note that is not part of the tuning, the screen switches to the mono view by itself (header POLY&gt;MONO)."],
 mono_h="MONO - one string, large display",
 mono="Play one note: the screen shows its name and octave, the deviation in cents (to 0.1 cent), the frequency and, if the note belongs to the tuning, the string number (string 1 = highest). The value is marked ~ during the first moments (coarse estimate), then switches to the precise phase measurement. The thin white mark is the target; the smaller yellow cursor is the note you play and slides left when flat, right when sharp. Within ±1 cent the mark turns green.",
 strobe_h="STROBE - stroboscopic accuracy",
 strobe="The bands scroll at a speed proportional to the deviation, like a mechanical strobe tuner: scrolling right = sharp, left = flat. Tune until the bands stand still; they turn green within ±1 cent. Ideal for intonation and very precise tuning.",
 midi_t="6. MIDI",
 midi="Every control of the pedal can be driven from a MIDI footswitch or controller (for example an M-Vave Chocolate Plus). <b>No CC is assigned by default</b>: you choose the CC of each control with <b>MIDI Learn</b>.",
 learn_h="MIDI Learn",
 learn=["<b>Right-click a control</b> (MODE, TUNING, ◄ or ►, REF or the TUNE / MUTE footswitch) and choose <b>MIDI Learn: &lt;control&gt; (CC n / none)</b>. The TUNING knob offers its two directions: <i>Next tuning</i> and <i>Previous tuning</i>.",
        "The screen shows <b>MIDI LEARN: move a control for X</b>. Move a pedal or press a button on your controller: the first CC received is assigned (it does not act on the tuner) and the screen confirms <b>X = CC n</b> for 2 seconds.",
        "<b>Clear MIDI: &lt;control&gt;</b> removes the assignment; <b>Cancel MIDI learn</b> (or choosing the same Learn item again) stops waiting.",
        "A CC already used by another control is taken away from it, so one CC always drives one control.",
        "Right-click anywhere else &gt; <b>MIDI</b>: <i>Learn</i> for every control with its current CC (or <i>none</i>), <b>Clear all MIDI assignments</b>, the MIDI <b>Channel</b> (Omni or 1 to 16) and the footswitch type (latching or momentary pedal).",
        "Assignments are <b>saved with the project</b>. A project saved with an earlier version that still used the old factory CC numbers opens with no assignment; a project in which you had changed an assignment keeps its assignments."],
 midi_rows=[["Control", "Type"],
   ["TUNE / MUTE footswitch", "Footswitch. Latching (default): value ≥ 64 = mute, &lt; 64 = sound. Momentary: each press (≥ 64) toggles."],
   ["MODE", "3-position selector: 0-42 MONO, 43-85 POLY, 86-127 STROBE."],
   ["TUNING / ► - next tuning", "Trigger: each value ≥ 64 = next tuning."],
   ["TUNING / ◄ - previous tuning", "Trigger: each value ≥ 64 = previous tuning."],
   ["REF", "Continuous: 0-127 = 430-450 Hz."],
   ["Program Change", "Program n selects favourite n (program 0 = first favourite), or tuning n if there are no favourites. No learning needed."]],
 midi_note="Mute, Mode and Reference A4 are also host parameters: they can be automated or mapped from the DAW (Reaper: Param &gt; Learn).",
 win_t="7. Window",
 win=["Right-click anywhere (outside a control, or on the screen) &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b>, <b>100 %</b> (the current size is ticked); <i>(default)</i> is shown next to the default size. You can also drag the bottom-right corner (aspect ratio kept). The window can never be made smaller than 60 %.",
      "<b>Plugin size &gt; Default size (new windows)</b> chooses the size at which every new CHROMA window opens (60 % at first). This setting is common to all instances and saved on your computer (<i>settings.xml</i> in the Studio Wiga\\Chroma folder, next to the tunings file); the open window takes that size at once.",
      "Once you change the size of a window (menu or corner), that instance remembers its own size in the project, and this size takes priority over the default size when the project is reopened. An instance whose size was never changed opens at the default size.",
      "The same right-click menu holds <b>MIDI</b> (section 6), <b>Custom tunings...</b> (opens the CUSTOM tab) and <b>Show tunings file</b>. CHROMA has no separate status line: messages (new tuning, A4 = 440 Hz, MIDI Learn prompts and confirmations) appear as a banner on the screen."],
 pre_t="8. Factory tunings (presets)",
 pre="CHROMA's presets are its 82 factory tunings. Strings are listed from the lowest to the highest. Names are shown in English or French depending on the EN / FR button of the menu.",
 bass_t="Factory tunings: basses",
 tips_t="9. Tips",
 tips=["Place CHROMA <b>first</b> in the Reaper chain, before drives and before the amp sim (Two Notes Genome...), for the cleanest signal.",
       "Low 7-string tunings (drop G, G standard...): pluck firmly with the pick or thumb, near the neck pickup if possible: the fundamental is stronger.",
       "Let the string ring for one second: the first 50 ms (attack) are ignored and the reading gets more precise as the string rings.",
       "In POLY, mute the strings you are not tuning if they ring sympathetically.",
       "Open tunings with octave strings (Open D, DADGAD...): the higher octave string shares all its harmonics with the lower one; POLY shows the direction correctly, finish in MONO for the last cent.",
       "Learn the footswitch on a latching MIDI switch and use it as a silent-tuning pedal between songs."],
 tr_t="Troubleshooting",
 tr=[["Symptom", "Solution"],
     ["Nothing on screen", "Check the input level (the tuner reacts from about -66 dBFS) and that the track is armed / monitored."],
     ["Wrong octave", "Play the string a bit harder or closer to the neck; the octave test needs a few cycles of the fundamental."],
     ["A POLY row stays dim", "That string was not detected: strum again, or check that the selected tuning matches your instrument."],
     ["MIDI does nothing", "No CC is assigned by default: learn one (right-click the control &gt; MIDI Learn). Then check the MIDI channel (right-click &gt; MIDI &gt; Channel) and that the track receives MIDI from your controller."],
     ["Plug-in not listed", "Re-scan the plug-ins in the DAW; on macOS run the xattr command (section 2)."]],
 spec_t="10. Specifications",
 spec=[["Item", "Value"], ["Format", "VST3 - Windows 64-bit, macOS universal (Apple Silicon + Intel)"], ["Inspired by", "TC Electronic PolyTune"],
       ["Modes", "MONO, POLY, STROBE"], ["Range", "about 16 Hz (C0) to 1.6 kHz"],
       ["MONO / STROBE accuracy", "±0.1 cent on a sustained note (tested from D0 to E6)"],
       ["POLY accuracy", "±0.1-0.5 cent on strings with an isolated partial; ±1-3 cents on strings sharing all their harmonics (octaves)"],
       ["Settling time", "guitar about 0.3 s; low bass (F0, E0) about 0.8-1.2 s"], ["Reference", "A4 = 430 ... 450 Hz (440 Hz)"],
       ["Tunings", "82 factory tunings, favourites, custom tunings up to 10 strings"],
       ["Latency / sound", "none - the sound passes through untouched; smooth mute"], ["CPU", "about 4 % of one core (separate analysis thread)"],
       ["MIDI", "MIDI Learn on every control (no CC assigned by default), channel Omni / 1-16, latching or momentary footswitch, Program Change = favourites; saved with the project"],
       ["Window", "Plugin size 60 % / 75 % / 100 %, default size of new windows to choose (60 % at first), never smaller than 60 %; corner resize"],
       ["Windows stability", "anti-freeze v2: the audio thread never calls the host, window refresh driven by a timer with a watchdog"]]),
"fr": dict(
 lang="FRANÇAIS", sub="Accordeur polyphonique guitare &amp; basse &nbsp;·&nbsp; Mono · Poly · Strobe &nbsp;·&nbsp; VST3",
 ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 intro_t="1. Présentation",
 intro="<b>CHROMA</b> est un accordeur VST3 conçu par Studio Wiga pour guitare et basse, avec l'allure d'une vraie pédale. Grattez toutes les cordes d'un coup et voyez celles qui sont fausses (<b>POLY</b>), affinez une corde sur un grand affichage (<b>MONO</b>) ou avec la précision d'un stroboscope (<b>STROBE</b>). Son format pédale et son mode polyphonique s'inspirent du <b>TC Electronic PolyTune</b>. Il a été pensé dès le départ pour les accordages très graves : Sol#0, Fa0, Mi0 et même Ré0 (environ 18 Hz) sont mesurés de façon fiable. CHROMA s'appelait auparavant Tuna.",
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
       "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. Le plugin apparaît sous le nom <b>Chroma (Studio Wiga)</b>.",
       "Si vous aviez installé <b>Tuna.vst3</b> (ou CHROMA.vst3 de la version 1.1.0), supprimez-le : CHROMA garde le même identifiant interne pour que Reaper le retrouve dans vos projets, et vos accordages perso et favoris de Tuna sont repris automatiquement."],
 ui_t="3. L'interface",
 ui_cap="Chaque commande dessinée sur la pédale est active. Les numéros renvoient au tableau ci-dessous et à la section 4.",
 ui_rows=[["N°", "Élément", "Fonction"],
   ["1", "Nom du mode", "MONO, POLY ou STROBE. Clic : mode suivant."],
   ["2", "Menu des accordages", "Accordage choisi et son type (G6 = guitare 6 cordes, B5 = basse 5 cordes, P = perso). Clic : ouvre le menu. Passe au vert quand toutes les cordes sont justes."],
   ["3", "Référence", "Hauteur du La4 (430 à 450 Hz)."],
   ["4", "Affichage", "Lignes des cordes (POLY), grande note (MONO) ou bandes (STROBE). Les messages (MIDI Learn, etc.) s'y affichent en bandeau."],
   ["5", "Échelle", "-50 / 0 / +50 cents."],
   ["6", "LED des modes", "LED ambre au-dessus du mode actif."],
   ["7", "MODE", "Sélecteur 3 positions."],
   ["8", "TUNING", "Encodeur sans fin : accordage suivant / précédent ; clic = menu."],
   ["9", "◄ ►", "Accordage précédent / suivant."],
   ["10", "REF", "Référence La4."],
   ["11", "LED MUTE", "Rouge = sortie coupée."],
   ["12", "TUNE / MUTE", "Footswitch : coupe la sortie."],
   ["13 / 14", "INPUT / OUTPUT", "Entrée à gauche, sortie à droite."]],
 ctl_t="4. Les commandes",
 ctl=[("MODE (7)", "Sélecteur 3 positions : MONO, POLY, STROBE. Glisser, molette ou clic (clic = mode suivant). Cliquer sur le nom du mode à l'écran (1) fait de même. CHROMA s'ouvre en <b>MONO</b> ; les projets enregistrés gardent leur mode."),
      ("TUNING (8) et ◄ ► (9)", "Encodeur sans fin : un cran (glisser ou molette) = accordage suivant / précédent, comme les flèches. Un clic sur le potard, ou sur le nom de l'accordage (2), ouvre le menu des accordages. Le nom du nouvel accordage s'affiche brièvement."),
      ("REF (10)", "Hauteur du La4 de 430 à 450 Hz par pas de 1 Hz (glisser ou molette) ; <b>double-clic = 440 Hz</b>. Tous les accordages la suivent ; la valeur est affichée en haut à droite de l'écran (3).")],
 menu_t="Le menu des accordages",
 menu="Le menu s'ouvre sur l'écran en anglais ; le petit bouton <b>FR</b> de son en-tête passe les menus de l'écran en français (<b>EN</b> pour revenir), choix mémorisé pour toutes les instances. Il a trois onglets :",
 menu_b=["<b>ALL</b> : tous les accordages d'usine, groupés par instrument, puis vos accordages perso.",
         "<b>★ FAVORITES</b> : les accordages marqués d'une étoile (clic sur l'étoile en bout de ligne). Le Program Change les sélectionne.",
         "<b>✎ CUSTOM</b> : vos propres accordages. <i>+ New tuning</i> copie l'accordage courant ; le crayon modifie un accordage."],
 menu_cap="Onglets ALL, FAVORITES et CUSTOM.",
 cust_t="Accordages perso",
 cust=["Dans l'éditeur, réglez le nom, le nombre de cordes (1 à 10), puis chaque corde avec − / + (demi-ton) et « / » (octave). Les fréquences suivent la référence courante. <b>Save</b>, <b>Delete</b> ou <b>Cancel</b>.",
       "Accordages perso et favoris sont stockés dans un fichier commun à toutes les instances (clic droit &gt; <i>Show tunings file</i>) : <i>%APPDATA%\\Studio Wiga\\Chroma\\library.xml</i> sous Windows, <i>~/Library/Application Support/Studio Wiga/Chroma/library.xml</i> sous macOS. L'accordage choisi est aussi enregistré dans le projet."],
 fs_t="5. Footswitch, LED et modes",
 fs_h="Footswitch TUNE / MUTE",
 fs="Un clic sur le footswitch coupe la sortie avec un fondu court, sans clic ; la LED rouge <b>MUTE</b> s'allume. Recliquez pour réentendre la guitare. L'accordeur fonctionne toujours, coupé ou non. La LED ambre au-dessus de MONO, POLY ou STROBE indique le mode actif.",
 poly_h="POLY - toutes les cordes d'un coup",
 poly="Choisissez l'accordage, grattez franchement toutes les cordes à vide et laissez-les sonner. Une ligne par corde (la plus aiguë en haut) ; le segment allumé montre l'écart : à gauche = trop bas, à droite = trop haut, un segment = 4 cents. Une corde passe au <b>vert</b> à ±2 cents ; quand toutes sont vertes, le nom de l'accordage passe au vert aussi.",
 poly_b=["La mesure se stabilise en 0,3 s environ à la guitare et 0,6 à 1 s sur les cordes de basse les plus graves (un cycle de Fa0 dure 46 ms).",
         "Une corde non jouée reste sombre. Quand vous arrêtez de jouer, la dernière valeur reste affichée puis s'estompe lentement.",
         "Si vous jouez une seule note qui n'appartient pas à l'accordage, l'écran passe tout seul en vue mono (en-tête POLY&gt;MONO)."],
 mono_h="MONO - une corde, grand affichage",
 mono="Jouez une note : l'écran affiche son nom et son octave, l'écart en cents (au 0,1 cent), la fréquence et, si la note appartient à l'accordage, le numéro de corde (corde 1 = la plus aiguë). La valeur est marquée ~ au tout début (estimation grossière), puis passe à la mesure de phase précise. Le fin repère blanc est la cible ; le petit curseur jaune est la note jouée et glisse à gauche si elle est basse, à droite si elle est haute. À ±1 cent le repère passe au vert.",
 strobe_h="STROBE - précision stroboscopique",
 strobe="Les bandes défilent à une vitesse proportionnelle à l'écart, comme un accordeur stroboscopique mécanique : défilement à droite = trop haut, à gauche = trop bas. Accordez jusqu'à ce que les bandes s'arrêtent ; elles passent au vert à ±1 cent. Idéal pour le réglage de l'intonation et l'accordage très précis.",
 midi_t="6. MIDI",
 midi="Chaque commande de la pédale peut être pilotée par un pédalier ou un contrôleur MIDI (par exemple une M-Vave Chocolate Plus). <b>Aucun CC n'est assigné par défaut</b> : vous choisissez le CC de chaque commande avec le <b>MIDI Learn</b>.",
 learn_h="MIDI Learn",
 learn=["<b>Clic droit sur une commande</b> (MODE, TUNING, ◄ ou ►, REF ou le footswitch TUNE / MUTE) puis <b>MIDI Learn: &lt;commande&gt; (CC n / none)</b>. Le potard TUNING propose ses deux sens : <i>Next tuning</i> et <i>Previous tuning</i>.",
        "L'écran affiche <b>MIDI LEARN: move a control for X</b>. Bougez une pédale ou appuyez sur un bouton du contrôleur : le premier CC reçu est assigné (il n'agit pas sur l'accordeur) et l'écran confirme <b>X = CC n</b> pendant 2 secondes.",
        "<b>Clear MIDI: &lt;commande&gt;</b> supprime l'assignation ; <b>Cancel MIDI learn</b> (ou rechoisir le même Learn) arrête l'attente.",
        "Un CC déjà utilisé par une autre commande lui est retiré : un CC pilote toujours une seule commande.",
        "Clic droit ailleurs &gt; <b>MIDI</b> : <i>Learn</i> de chaque commande avec son CC actuel (ou <i>none</i>), <b>Clear all MIDI assignments</b>, le canal MIDI (<b>Channel</b> : Omni ou 1 à 16) et le type de footswitch (pédale à accrochage ou momentanée).",
        "Les assignations sont <b>enregistrées avec le projet</b>. Un projet enregistré avec une version précédente qui utilisait encore les anciens numéros de CC d'usine s'ouvre sans aucune assignation ; un projet où vous aviez changé une assignation garde ses assignations."],
 midi_rows=[["Commande", "Type"],
   ["Footswitch TUNE / MUTE", "Footswitch. À accrochage (défaut) : valeur ≥ 64 = coupé, &lt; 64 = son. Momentané : chaque appui (≥ 64) bascule."],
   ["MODE", "Sélecteur 3 positions : 0-42 MONO, 43-85 POLY, 86-127 STROBE."],
   ["TUNING / ► - accordage suivant", "Déclencheur : chaque valeur ≥ 64 = accordage suivant."],
   ["TUNING / ◄ - accordage précédent", "Déclencheur : chaque valeur ≥ 64 = accordage précédent."],
   ["REF", "Continu : 0-127 = 430-450 Hz."],
   ["Program Change", "Le programme n choisit le favori n (programme 0 = premier favori), ou l'accordage n s'il n'y a pas de favoris. Aucun apprentissage nécessaire."]],
 midi_note="Mute, Mode et Reference A4 sont aussi des paramètres de l'hôte : automatisables ou assignables depuis le DAW (Reaper : Param &gt; Learn).",
 win_t="7. Fenêtre",
 win=["Clic droit n'importe où (hors commande, ou sur l'écran) &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b>, <b>100 %</b> (la taille actuelle est cochée) ; <i>(default)</i> est indiqué à côté de la taille par défaut. Vous pouvez aussi tirer le coin inférieur droit (proportions conservées). La fenêtre ne peut jamais être plus petite que 60 %.",
      "<b>Plugin size &gt; Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres de CHROMA (60 % au départ). Ce réglage est commun à toutes les instances et enregistré sur l'ordinateur (<i>settings.xml</i> dans le dossier Studio Wiga\\Chroma, à côté du fichier des accordages) ; la fenêtre ouverte prend aussi cette taille tout de suite.",
      "Dès que vous changez la taille d'une fenêtre (menu ou coin), cette instance mémorise sa propre taille dans le projet, et cette taille reste prioritaire sur la taille par défaut à la réouverture du projet. Une instance dont la taille n'a jamais été changée s'ouvre à la taille par défaut.",
      "Le même menu contient <b>MIDI</b> (section 6), <b>Custom tunings...</b> (ouvre l'onglet CUSTOM) et <b>Show tunings file</b>. CHROMA n'a pas de ligne d'état séparée : les messages (nouvel accordage, A4 = 440 Hz, invites et confirmations du MIDI Learn) s'affichent en bandeau sur l'écran."],
 pre_t="8. Accordages d'usine (presets)",
 pre="Les presets de CHROMA sont ses 82 accordages d'usine. Les cordes sont listées de la plus grave à la plus aiguë. Les noms s'affichent en anglais ou en français selon le bouton EN / FR du menu.",
 bass_t="Accordages d'usine : basses",
 tips_t="9. Conseils",
 tips=["Placez CHROMA <b>en premier</b> dans la chaîne Reaper, avant les saturations et avant la simulation d'ampli (Two Notes Genome...), pour le signal le plus propre.",
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
     ["Le MIDI ne fait rien", "Aucun CC n'est assigné par défaut : apprenez-en un (clic droit sur la commande &gt; MIDI Learn). Vérifiez ensuite le canal MIDI (clic droit &gt; MIDI &gt; Channel) et que la piste reçoit le MIDI du contrôleur."],
     ["Plugin absent", "Re-scannez les plug-ins dans le DAW ; sous macOS lancez la commande xattr (section 2)."]],
 spec_t="10. Caractéristiques techniques",
 spec=[["Élément", "Valeur"], ["Format", "VST3 - Windows 64 bits, macOS universel (Apple Silicon + Intel)"], ["Inspiré de", "TC Electronic PolyTune"],
       ["Modes", "MONO, POLY, STROBE"], ["Plage", "environ 16 Hz (Do0) à 1,6 kHz"],
       ["Précision MONO / STROBE", "±0,1 cent sur une note tenue (testé de Ré0 à Mi6)"],
       ["Précision POLY", "±0,1-0,5 cent sur les cordes à partiel isolé ; ±1-3 cents sur les cordes partageant toutes leurs harmoniques (octaves)"],
       ["Temps de stabilisation", "guitare environ 0,3 s ; basse grave (Fa0, Mi0) environ 0,8-1,2 s"], ["Référence", "A4 = 430 ... 450 Hz (440 Hz)"],
       ["Accordages", "82 accordages d'usine, favoris, accordages perso jusqu'à 10 cordes"],
       ["Latence / son", "aucune - le son passe sans modification ; coupure douce"], ["CPU", "environ 4 % d'un cœur (thread d'analyse séparé)"],
       ["MIDI", "MIDI Learn sur chaque commande (aucun CC assigné par défaut), canal Omni / 1-16, footswitch à accrochage ou momentané, Program Change = favoris ; enregistré avec le projet"],
       ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais plus petite que 60 % ; redimensionnement par le coin"],
       ["Stabilité Windows", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement de la fenêtre piloté par un timer avec chien de garde"]]),
}

def section(lang):
    t = T[lang]; f = cover(t, "cover.jpg", 78 * mm)
    f += [P(t["intro_t"], "h1"), P(t["intro"]), P(t["does_t"], "h2")] + bullets(t["does"]) + [P(t["does_note"], "note")]
    f += [P(t["inst_t"], "h1")] + bullets(t["inst"]) + [PageBreak()]
    f += [P(t["ui_t"], "h1"), img("annotated.jpg", height=100 * mm), P(t["ui_cap"], "small"),
          table(t["ui_rows"], [15 * mm, 30 * mm, W - 45 * mm], first_bold=False), PageBreak()]
    f += [P(t["ctl_t"], "h1")]
    for h, x in t["ctl"]: f += [P(h, "h2"), P(x)]
    f += [P(t["menu_t"], "h2"), P(t["menu"])] + bullets(t["menu_b"])
    tabs = Table([[img("menu_all.png", (W - 8) / 3), img("menu_favorites.png", (W - 8) / 3), img("menu_custom.png", (W - 8) / 3)]],
                 colWidths=[W / 3] * 3)
    tabs.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)]))
    f += [Spacer(1, 2 * mm), tabs, P(t["menu_cap"], "small")]
    f += [side(img("tuning_editor.png", 52 * mm), [P(t["cust_t"], "h2")] + [P(x) for x in t["cust"]], 56 * mm), PageBreak()]
    f += [P(t["fs_t"], "h1"), P(t["fs_h"], "h2"), P(t["fs"])]
    f += [side(img("poly.png", 62 * mm), [P(t["poly_h"], "h2"), P(t["poly"])], 66 * mm)] + bullets(t["poly_b"])
    f += [side(img("mono.png", 62 * mm), [P(t["mono_h"], "h2"), P(t["mono"])], 66 * mm)]
    f += [side(img("strobe.png", 62 * mm), [P(t["strobe_h"], "h2"), P(t["strobe"])], 66 * mm), PageBreak()]
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

build([("en", section("en")), ("fr", section("fr"))], "CHROMA " + VERSION + " - User manual / Notice")
