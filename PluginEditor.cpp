#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"

using namespace juce;

//==============================================================================
TunaFonts::TunaFonts()
{
    monoTf = Typeface::createSystemTypefaceFor (BinaryData::IBMPlexMonoSemiBold_ttf, BinaryData::IBMPlexMonoSemiBold_ttfSize);
    sansTf = Typeface::createSystemTypefaceFor (BinaryData::IBMPlexSansSemiBold_ttf, BinaryData::IBMPlexSansSemiBold_ttfSize);
    popMed   = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    popBold  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    popLight = Typeface::createSystemTypefaceFor (BinaryData::PoppinsLight_ttf, BinaryData::PoppinsLight_ttfSize);
}
Font TunaFonts::mono (float h) const { return Font (FontOptions (monoTf).withHeight (h)); }
Font TunaFonts::sans (float h) const { return Font (FontOptions (sansTf).withHeight (h)); }

static float textWidth (const Font& f, const String& s) { return GlyphArrangement::getStringWidth (f, s); }

static String sign1 (float v)
{
    const float r = std::round (v * 10.0f) / 10.0f;
    return (r > 0 ? "+" : (r < 0 ? "-" : "")) + String (std::abs (r), 1);
}

static Path starPath (Point<float> c, float r)
{
    Path p;
    p.addStar (c, 5, r * 0.45f, r, 0.0f);
    return p;
}

static Path pencilPath (Rectangle<float> b)
{
    Path p;
    const float w = b.getWidth();
    p.startNewSubPath (b.getX() + w * 0.15f, b.getBottom() - w * 0.15f);
    p.lineTo (b.getX() + w * 0.15f, b.getBottom() - w * 0.38f);
    p.lineTo (b.getRight() - w * 0.30f, b.getY() + w * 0.08f);
    p.lineTo (b.getRight() - w * 0.08f, b.getY() + w * 0.30f);
    p.lineTo (b.getX() + w * 0.38f, b.getBottom() - w * 0.15f);
    p.closeSubPath();
    return p;
}

static Path checkPath (Rectangle<float> b)
{
    Path p;
    p.startNewSubPath (b.getX(), b.getCentreY());
    p.lineTo (b.getX() + b.getWidth() * 0.38f, b.getBottom());
    p.lineTo (b.getRight(), b.getY());
    return p;
}

static String instrumentTag (const tuna::Tuning& t)
{
    const String cat = String::fromUTF8 (t.category.c_str());
    const int n = (int) t.notes.size();
    if (t.user) return "P" + String (n);
    if (cat.startsWith ("BASSE")) return "B" + String (n);
    return "G" + String (n);
}

static String upperName (const tuna::Tuning& t, bool fr) { return String::fromUTF8 (tuna::displayName (t, fr).c_str()).toUpperCase(); }
static String tr (bool fr, const char* en, const char* frUtf8) { return String::fromUTF8 (fr ? frUtf8 : en); }


static Path triangle (Point<float> c, float w, float h, int dir)   // dir : -1 gauche, 1 droite, 2 bas
{
    Path p;
    if (dir == 2) p.addTriangle (c.x - w * 0.5f, c.y - h * 0.5f, c.x + w * 0.5f, c.y - h * 0.5f, c.x, c.y + h * 0.5f);
    else if (dir < 0) p.addTriangle (c.x + w * 0.5f, c.y - h * 0.5f, c.x + w * 0.5f, c.y + h * 0.5f, c.x - w * 0.5f, c.y);
    else p.addTriangle (c.x - w * 0.5f, c.y - h * 0.5f, c.x - w * 0.5f, c.y + h * 0.5f, c.x + w * 0.5f, c.y);
    return p;
}

//==============================================================================
// TunaDisplay — repère 1078 x 1345 unités (pixels du visuel), marges de 34
namespace scr
{
constexpr float X0 = 34.0f, X1 = 1044.0f;
constexpr float rowY = 30.0f, rowH = 62.0f;                  // rangée 1 : modes, référence, logo
constexpr float refX = 436.0f, refW = 250.0f;
constexpr float barY = 114.0f, barH = 84.0f;                 // rangée 2 : accordage
constexpr float sepY = 224.0f;
constexpr float areaTop = 246.0f, areaBot = 1275.0f;          // affichage du mode
constexpr float logoW = 300.0f, logoH = logoW * 295.0f / 2032.0f;
}

TunaDisplay::TunaDisplay (TunaEditor& e) : ed (e)
{
    setOpaque (false);
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::Chroma_Wordmark_White_svg, BinaryData::Chroma_Wordmark_White_svgSize)))
        wordmark = Drawable::createFromSVG (*xml);
    if (wordmark != nullptr) wordmark->replaceColour (Colours::white, tunacol::grey);   // même gris que STRING 6
}

Rectangle<float> TunaDisplay::tuningBar() const { return { scr::X0, scr::barY, scr::X1 - scr::X0, scr::barH }; }

Rectangle<float> TunaDisplay::zoneRect (int z)
{
    using namespace scr;
    switch (z)
    {
        case zMono:    return { X0, rowY, 112.0f, rowH };
        case zPoly:    return { X0 + 124.0f, rowY, 112.0f, rowH };
        case zStrobe:  return { X0 + 248.0f, rowY, 142.0f, rowH };
        case zRefDown: return { refX, rowY, 80.0f, rowH };
        case zRefMid:  return { refX + 80.0f, rowY, 90.0f, rowH };
        case zRefUp:   return { refX + 170.0f, rowY, 80.0f, rowH };
        case zPrev:    return { X0, barY, 92.0f, barH };
        case zDrop:    return { X0 + 92.0f, barY, X1 - X0 - 184.0f, barH };
        case zNext:    return { X1 - 92.0f, barY, 92.0f, barH };
        case zLogo:    return { X1 - logoW, rowY, logoW, rowH };
        default:       return {};
    }
}

int TunaDisplay::zoneAt (Point<float> p) const
{
    for (int z = zMono; z <= zNext; ++z)
        if (zoneRect (z).expanded (3.0f).contains (p)) return z;
    return zNone;
}

void TunaDisplay::mouseDown (const MouseEvent& e)
{
    const float s = getWidth() / kSW;
    const int z = zoneAt (e.position / s);
    if (e.mods.isPopupMenu())
    {
        // clic droit sur une commande de l'écran : MIDI Learn de cette commande en tête du menu
        const int learn = (z >= zMono && z <= zStrobe) ? 1
                        : (z >= zRefDown && z <= zRefUp) ? 4
                        : (z == zPrev) ? 3
                        : (z == zNext || z == zDrop) ? 2 : -1;
        ed.showContextMenu (learn);
        return;
    }
    switch (z)
    {
        case zMono: case zPoly: case zStrobe: ed.setParam ("mode", (float) (z - zMono)); break;
        case zRefDown: ed.stepRef (-1); break;
        case zRefUp:   ed.stepRef (1); break;
        case zPrev:    ed.stepTuning (-1); break;
        case zNext:    ed.stepTuning (1); break;
        case zDrop:    ed.openMenu(); break;
        default: break;
    }
}

void TunaDisplay::mouseDoubleClick (const MouseEvent& e)
{
    const float s = getWidth() / kSW;
    if (zoneAt (e.position / s) == zRefMid) { ed.setParam ("ref", 440.0f); ed.flash ("A4 = 440 Hz"); }
}

void TunaDisplay::mouseMove (const MouseEvent& e)
{
    const float s = getWidth() / kSW;
    const int z = zoneAt (e.position / s);
    if (z != hover) { hover = z; repaint(); }
    setMouseCursor (z != zNone && z != zRefMid ? MouseCursor::PointingHandCursor : MouseCursor::NormalCursor);
}

void TunaDisplay::mouseExit (const MouseEvent&) { if (hover != zNone) { hover = zNone; repaint(); } }

void TunaDisplay::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    const float s = getWidth() / kSW;
    const int z = zoneAt (e.position / s);
    wheelAccum += w.deltaY * (w.isReversed ? -1.0f : 1.0f);
    int d = 0;
    while (wheelAccum >= 0.12f)  { wheelAccum -= 0.12f; ++d; }
    while (wheelAccum <= -0.12f) { wheelAccum += 0.12f; --d; }
    if (d == 0) return;
    if (z >= zRefDown && z <= zRefUp) ed.stepRef (d);
    else if (z >= zMono && z <= zStrobe) ed.setParam ("mode", (float) jlimit (0, 2, ed.modeIndex() - d));
    else if (z >= zPrev && z <= zNext) ed.stepTuning (-d);
}

void TunaDisplay::paint (Graphics& g)
{
    const float s = getWidth() / kSW;
    g.addTransform (AffineTransform::scale (s));
    Path clip; clip.addRoundedRectangle (0.0f, 0.0f, kSW, kSH, art::screenRadius);
    g.reduceClipRegion (clip);

    const auto& sn = ed.snap;
    const int mode = ed.modeIndex();
    const bool autoMono = mode == 1 && sn.monoOffTuning && ! sn.anyStringActive;
    paintHeader (g, sn, mode, autoMono);
    if (mode == 0 || autoMono) paintMono (g, sn);
    else if (mode == 1)        paintPoly (g, sn);
    else                       paintStrobe (g, sn);

    // message temporaire (accordage, MIDI learn...)
    if (Time::getMillisecondCounterHiRes() * 0.001 < flashUntil && flashText.isNotEmpty())
    {
        const auto f = ed.fonts.mono (56.0f);
        const float w = jmin (990.0f, textWidth (f, flashText) + 100.0f);
        const bool twoLines = flashText.length() > 26;
        Rectangle<float> r (kSW * 0.5f - w * 0.5f, 560.0f, w, twoLines ? 190.0f : 130.0f);
        g.setColour (Colour (0xf0080a09));
        g.fillRoundedRectangle (r, 14.0f);
        g.setColour (tunacol::amber.withAlpha (0.7f));
        g.drawRoundedRectangle (r, 14.0f, 2.5f);
        g.setFont (f);
        g.setColour (tunacol::amber);
        g.drawFittedText (flashText, r.reduced (24.0f, 10.0f).toNearestInt(), Justification::centred, twoLines ? 2 : 1, 0.6f);
    }

    // reflet de la vitre
    ColourGradient glass (Colours::white.withAlpha (0.07f), 0, 0, Colours::white.withAlpha (0.0f), kSW * 0.45f, kSH * 0.45f, false);
    g.setGradientFill (glass);
    Path p;
    p.startNewSubPath (0, 0); p.lineTo (kSW * 0.62f, 0); p.lineTo (0, kSH * 0.55f); p.closeSubPath();
    g.fillPath (p);
}

void TunaDisplay::paintHeader (Graphics& g, const tuna::Snapshot& sn, int mode, bool autoMono)
{
    using namespace scr;
    const auto orange = tunacol::orange;
    // rangée 1 : MONO / POLY / STROBE (POLY reste allumé quand il bascule seul en MONO)
    static const char* names[3] = { "MONO", "POLY", "STROBE" };
    g.setFont (ed.fonts.mono (27.0f));
    for (int i = 0; i < 3; ++i)
    {
        const auto r = zoneRect (zMono + i).reduced (1.25f);
        const bool on = i == mode;
        const bool hov = hover == zMono + i;
        if (on) { g.setColour (orange.withAlpha (0.95f)); g.fillRoundedRectangle (r, 9.0f); }
        else if (hov) { g.setColour (orange.withAlpha (0.14f)); g.fillRoundedRectangle (r, 9.0f); }
        g.setColour (orange.withAlpha (on || hov ? 1.0f : (autoMono && i == 0 ? 0.85f : 0.55f)));
        g.drawRoundedRectangle (r, 9.0f, 2.5f);
        g.setColour (on ? Colour (0xff140c06) : orange);
        g.drawText (names[i], r, Justification::centred);
    }

    // référence A4 : ◄ A=440 ►
    {
        const Rectangle<float> r (refX + 1.25f, rowY + 1.25f, refW - 2.5f, rowH - 2.5f);
        if (hover >= zRefDown && hover <= zRefUp) { g.setColour (orange.withAlpha (0.08f)); g.fillRoundedRectangle (r, 9.0f); }
        g.setColour (orange.withAlpha (0.55f));
        g.drawRoundedRectangle (r, 9.0f, 2.5f);
        const float cy = rowY + rowH * 0.5f;
        g.setColour (orange.withAlpha (hover == zRefDown ? 1.0f : 0.85f));
        g.fillPath (triangle ({ refX + 33.0f, cy }, 17.0f, 20.0f, -1));
        g.setColour (orange.withAlpha (hover == zRefUp ? 1.0f : 0.85f));
        g.fillPath (triangle ({ refX + refW - 33.0f, cy }, 17.0f, 20.0f, 1));
        const int ref = (int) ed.proc.apvts.getRawParameterValue ("ref")->load();
        g.setColour (orange);
        g.setFont (ed.fonts.mono (31.0f));
        g.drawText ("A=" + String (ref), Rectangle<float> (refX + 50.0f, rowY, refW - 100.0f, rowH), Justification::centred);
    }

    // logo CHROMA (vectoriel) à droite
    if (wordmark != nullptr)
        wordmark->drawWithin (g, { X1 - logoW, rowY + (rowH - logoH) * 0.5f, logoW, logoH }, RectanglePlacement::centred, 0.75f);

    // rangée 2 : barre d'accordage ◄ | G6   DROP B ▼   6/81 | ►
    const auto& lib = ed.proc.library;
    const int idx = ed.proc.getTuningIndex();
    const auto& t = lib.get (idx);
    const bool green = mode == 1 && ! autoMono && sn.allInTune;
    const auto col = green ? tunacol::green : tunacol::amber;
    const auto bar = tuningBar().reduced (1.25f);
    g.setColour (col.withAlpha (hover == zDrop ? 0.14f : 0.07f));
    g.fillRoundedRectangle (bar, 11.0f);
    if (hover == zPrev || hover == zNext)
    {
        g.setColour (col.withAlpha (0.10f));
        g.fillRoundedRectangle (zoneRect (hover).reduced (5.0f), 8.0f);
    }
    g.setColour (col.withAlpha (green ? 0.85f : 0.6f));
    g.drawRoundedRectangle (bar, 11.0f, 2.5f);
    const float cy = barY + barH * 0.5f;
    g.setColour (col);
    g.fillPath (triangle ({ X0 + 44.0f, cy }, 22.0f, 26.0f, -1));
    g.fillPath (triangle ({ X1 - 44.0f, cy }, 22.0f, 26.0f, 1));
    g.setColour (col.withAlpha (0.3f));
    g.fillRect (X0 + 91.0f, barY + 14.0f, 2.0f, barH - 28.0f);
    g.fillRect (X1 - 93.0f, barY + 14.0f, 2.0f, barH - 28.0f);
    // étiquette instrument (G6, G7, B5...) et position dans la liste
    g.setFont (ed.fonts.mono (24.0f));
    g.setColour (col.withAlpha (0.6f));
    g.drawText (instrumentTag (t), Rectangle<float> (X0 + 116.0f, barY, 80.0f, barH), Justification::centredLeft);
    g.setFont (ed.fonts.mono (21.0f));
    g.setColour (col.withAlpha (0.55f));
    g.drawText (String (idx + 1) + "/" + String (lib.size()), Rectangle<float> (X1 - 116.0f - 110.0f, barY, 110.0f, barH), Justification::centredRight);
    // nom + triangle du menu
    const String nm = upperName (t, lib.french);
    const float maxW = (X1 - X0) - 2.0f * 230.0f;
    float fh = 46.0f;
    while (fh > 22.0f && textWidth (ed.fonts.mono (fh), nm) > maxW) fh -= 1.0f;
    const auto f = ed.fonts.mono (fh);
    const float nw = jmin (maxW, textWidth (f, nm)), triW = 22.0f, gap = 18.0f;
    const float x0 = (X0 + X1) * 0.5f - (nw + gap + triW) * 0.5f;
    g.setFont (f);
    g.setColour (col);
    g.drawText (nm, Rectangle<float> (x0, barY, nw + 2.0f, barH), Justification::centredLeft, true);
    if (green)
    {
        g.setColour (col.withAlpha (0.18f));
        g.drawText (nm, Rectangle<float> (x0, barY + 1.0f, nw + 2.0f, barH), Justification::centredLeft, true);
    }
    g.setColour (col);
    g.fillPath (triangle ({ x0 + nw + gap + triW * 0.5f, cy + 2.0f }, triW, 14.0f, 2));

    g.setColour (tunacol::amber.withAlpha (0.22f));
    g.fillRect (X0, sepY, X1 - X0, 2.0f);
}

static void drawSegment (Graphics& g, Rectangle<float> r, Colour c, bool lit)
{
    if (lit)
    {
        g.setColour (c.withAlpha (0.12f * c.getFloatAlpha())); g.fillRoundedRectangle (r.expanded (6.0f, 5.0f), 7.0f);
        g.setColour (c.withAlpha (0.25f * c.getFloatAlpha())); g.fillRoundedRectangle (r.expanded (3.0f, 2.5f), 5.0f);
        g.setColour (c); g.fillRoundedRectangle (r, 3.0f);
        g.setColour (Colours::white.withAlpha (0.35f * c.getFloatAlpha())); g.fillRoundedRectangle (r.reduced (r.getWidth() * 0.3f, r.getHeight() * 0.2f), 2.0f);
    }
    else { g.setColour (c); g.fillRoundedRectangle (r, 3.0f); }
}

void TunaDisplay::paintPoly (Graphics& g, const tuna::Snapshot& sn)
{
    using namespace scr;
    const int n = jmax (1, sn.numStrings);
    const float area = areaBot - areaTop;
    const float rowHt = jmin (200.0f, area / n);
    const float y0 = areaTop + (area - rowHt * n) * 0.5f;
    const float x0 = X0 + 150.0f, x1 = X1;
    const int segs = 25, mid = 12;
    const float pitch = (x1 - x0) / segs, segW = pitch * 0.62f;
    const float centreX = x0 + pitch * (mid + 0.5f);

    // repère central
    g.setColour (tunacol::green.withAlpha (0.13f));
    for (float y = y0; y < y0 + rowHt * n; y += 12.0f) g.fillRect (centreX - 1.0f, y, 2.0f, 5.0f);

    for (int row = 0; row < n; ++row)
    {
        const int idx = n - 1 - row;   // corde la plus aiguë en haut
        const auto& st = sn.strings[idx];
        const float cy = y0 + rowHt * (row + 0.5f);
        float alpha = 0.32f;
        if (st.measured) alpha = st.active ? 1.0f : jmap (jlimit (0.4f, 6.0f, st.age), 0.4f, 6.0f, 1.0f, 0.45f);
        const bool inTune = st.measured && std::abs (st.cents) <= (float) tuna::TunerEngine::kPolyInTune;
        const auto nameCol = (inTune ? tunacol::green : tunacol::amber).withAlpha (alpha);

        g.setFont (ed.fonts.mono (jmin (64.0f, rowHt * 0.62f)));
        g.setColour (nameCol);
        g.drawText (String (tuna::noteName (st.midi)), Rectangle<float> (X0, cy - rowHt * 0.5f, 146.0f, rowHt), Justification::centredLeft);

        const int lit = st.measured ? jlimit (0, segs - 1, mid + (int) std::lround (st.cents / 4.0f)) : -1;
        for (int k = 0; k < segs; ++k)
        {
            const float hh = rowHt * (k == mid ? 0.66f : 0.48f);
            Rectangle<float> r (x0 + pitch * k + (pitch - segW) * 0.5f, cy - hh * 0.5f, segW, hh);
            if (k == lit) drawSegment (g, r, (inTune ? tunacol::green : tunacol::amber).withAlpha (alpha), true);
            else if (lit >= 0 && ((k > mid && k < lit) || (k < mid && k > lit)))
                drawSegment (g, r, tunacol::amber.withAlpha (0.30f * alpha), false);
            else drawSegment (g, r, k == mid ? tunacol::greenDim : tunacol::amberDim, false);
        }
    }

    g.setFont (ed.fonts.mono (30.0f));
    g.setColour (tunacol::grey.withAlpha (0.75f));
    const float yl = kSH - 38.0f;
    g.drawText ("-50", Rectangle<float> (x0, yl - 20.0f, 120.0f, 40.0f), Justification::centredLeft);
    g.drawText ("0", Rectangle<float> (centreX - 60.0f, yl - 20.0f, 120.0f, 40.0f), Justification::centred);
    g.drawText ("+50", Rectangle<float> (x1 - 120.0f, yl - 20.0f, 120.0f, 40.0f), Justification::centredRight);
}

void TunaDisplay::paintMono (Graphics& g, const tuna::Snapshot& sn)
{
    using namespace scr;
    const bool has = sn.monoMidi >= 0 && (sn.monoActive || sn.monoAge < 2.0f);
    const float alpha = ! has ? 0.3f : (sn.monoActive ? 1.0f : jmap (jlimit (0.25f, 2.0f, sn.monoAge), 0.25f, 2.0f, 1.0f, 0.4f));
    const float c = has ? sn.monoCents : 0.0f;
    const bool inTune = has && sn.monoPrecise && std::abs (c) <= (float) tuna::TunerEngine::kMonoInTune;
    const auto col = (inTune ? tunacol::green : tunacol::amber).withAlpha (alpha);
    const float area = areaBot - areaTop;

    // grande note (lettre + altération en haut + octave en bas)
    const String pc = has ? String (tuna::pitchClassName (sn.monoMidi)) : String ("--");
    const String letter = has ? pc.substring (0, 1) : pc, acc = has ? pc.substring (1) : String();
    const String oct = has ? String (tuna::octaveOf (sn.monoMidi)) : String();
    const auto big = ed.fonts.mono (420.0f), small = ed.fonts.mono (140.0f);
    const float wL = textWidth (big, letter), wA = textWidth (small, acc), wO = textWidth (small, oct);
    const float total = wL + jmax (wA, wO) + 10.0f;
    const float x = kSW * 0.5f - total * 0.5f;
    const float ny = areaTop + area * 0.30f - 20.0f;      // note remontée de 20
    g.setFont (big);
    g.setColour (col.withAlpha (alpha * 0.18f));
    g.drawText (letter, Rectangle<float> (x - 4.0f, ny - 252.0f, wL + 8.0f, 500.0f), Justification::centredLeft);
    g.setColour (col);
    g.drawText (letter, Rectangle<float> (x, ny - 250.0f, wL + 8.0f, 500.0f), Justification::centredLeft);
    g.setFont (small);
    if (acc.isNotEmpty()) g.drawText (acc, Rectangle<float> (x + wL + 10.0f, ny - 190.0f, wA + 10.0f, 160.0f), Justification::centredLeft);
    g.drawText (oct, Rectangle<float> (x + wL + 10.0f, ny + 35.0f, wO + 10.0f, 160.0f), Justification::centredLeft);

    // barre +/- 50 cents : graduations fixes, repère central blanc (vert quand c'est juste)
    // et curseur jaune plus petit qui glisse avec la note jouée
    const int segs = 41, mid = 20;
    const float x0 = X0 + 10.0f, x1 = X1 - 10.0f, pitch = (x1 - x0) / segs, segW = pitch * 0.6f;
    const float cy = areaTop + area * 0.68f - 20.0f;      // barre et -50 / +50 remontées de 20
    for (int k = 0; k < segs; ++k)
    {
        if (k == mid) continue;
        const float hh = (k - mid) % 4 == 0 ? 100.0f : 70.0f;
        drawSegment (g, Rectangle<float> (x0 + pitch * k + (pitch - segW) * 0.5f, cy - hh * 0.5f, segW, hh), tunacol::amberDim, false);
    }
    const float markW = segW * 1.1f, markH = 220.0f;      // repère central
    const float curW = segW * 0.8f, curH = 164.0f;        // curseur jaune, plus petit que le repère
    const float centreX = x0 + pitch * (mid + 0.5f);
    const Rectangle<float> centre (centreX - markW * 0.5f, cy - markH * 0.5f, markW, markH);
    if (inTune) drawSegment (g, centre, tunacol::green.withAlpha (alpha), true);
    else
    {
        g.setColour (Colours::white.withAlpha (0.10f)); g.fillRoundedRectangle (centre.expanded (5.0f, 4.0f), 5.0f);
        g.setColour (Colours::white.withAlpha (has ? 0.95f : 0.55f)); g.fillRoundedRectangle (centre, 3.0f);
        if (has)
        {
            const float cc = jlimit (-50.0f, 50.0f, c);
            const float cx = centreX + cc / 2.5f * pitch;
            drawSegment (g, Rectangle<float> (cx - curW * 0.5f, cy - curH * 0.5f, curW, curH), tunacol::amber.withAlpha (alpha), true);
        }
    }
    g.setFont (ed.fonts.mono (30.0f));
    g.setColour (tunacol::grey.withAlpha (0.7f));
    g.drawText ("-50", Rectangle<float> (x0, cy + 125.0f, 120.0f, 40.0f), Justification::centredLeft);
    g.drawText ("+50", Rectangle<float> (x1 - 120.0f, cy + 125.0f, 120.0f, 40.0f), Justification::centredRight);

    // valeurs : écart, fréquence et corde posés sur la même ligne de pied
    const float base = kSH - 30.0f;
    g.setFont (ed.fonts.mono (96.0f));
    g.setColour (col);
    const String cents = has ? ((sn.monoPrecise ? String() : String ("~")) + sign1 (c) + " c") : String ("-- c");
    g.drawSingleLineText (cents, roundToInt (kSW * 0.5f), roundToInt (base), Justification::horizontallyCentred);
    g.setFont (ed.fonts.mono (32.0f));
    g.setColour (tunacol::grey.withAlpha (0.75f * jmax (0.4f, alpha)));
    if (has) g.drawSingleLineText (String (sn.monoHz, sn.monoHz < 100 ? 2 : 1) + " Hz", roundToInt (X0), roundToInt (base), Justification::left);
    // corde correspondante dans l'accordage choisi (corde 1 = la plus aiguë)
    if (has)
        for (int i = 0; i < sn.numStrings; ++i)
            if (sn.strings[i].midi == sn.monoMidi)
            {
                g.drawSingleLineText (tr (ed.proc.library.french, "STRING ", "CORDE ") + String (sn.numStrings - i), roundToInt (X1), roundToInt (base), Justification::right);
                break;
            }
}

void TunaDisplay::paintStrobe (Graphics& g, const tuna::Snapshot& sn)
{
    using namespace scr;
    const bool has = sn.monoMidi >= 0 && (sn.monoActive || sn.monoAge < 2.0f);
    const float alpha = ! has ? 0.3f : (sn.monoActive ? 1.0f : 0.45f);
    const float c = has ? sn.monoCents : 0.0f;
    const bool inTune = has && sn.monoPrecise && std::abs (c) <= (float) tuna::TunerEngine::kMonoInTune;
    const auto col = (inTune ? tunacol::green : tunacol::amber).withAlpha (alpha);

    // note + écart
    g.setFont (ed.fonts.mono (250.0f));
    g.setColour (col);
    const String nm = has ? String (tuna::noteName (sn.monoMidi)) : String ("--");
    g.drawText (nm, Rectangle<float> (X0, areaTop + 10.0f, 560.0f, 300.0f), Justification::centredLeft);
    g.setFont (ed.fonts.mono (100.0f));
    g.drawText (has ? sign1 (c) + " c" : String ("-- c"), Rectangle<float> (X1 - 460.0f, areaTop + 50.0f, 460.0f, 130.0f), Justification::centredRight);
    g.setFont (ed.fonts.mono (36.0f));
    g.setColour (tunacol::grey.withAlpha (0.75f * jmax (0.4f, alpha)));
    if (has) g.drawText (String (sn.monoHz, sn.monoHz < 100 ? 3 : 2) + " Hz", Rectangle<float> (X1 - 460.0f, areaTop + 185.0f, 460.0f, 60.0f), Justification::centredRight);

    // bandes stroboscopiques : chaque bande défile à une vitesse proportionnelle à l'écart
    const Rectangle<float> area (X0, 610.0f, X1 - X0, 560.0f);
    g.setColour (Colour (0xff0c0f0d));
    g.fillRoundedRectangle (area, 10.0f);
    {
        Graphics::ScopedSaveState ss (g);
        g.reduceClipRegion (area.toNearestInt());
        const float bandH[3] = { 210.0f, 160.0f, 120.0f };
        const float period[3] = { 200.0f, 100.0f, 50.0f };
        float y = area.getY() + 24.0f;
        for (int b = 0; b < 3; ++b)
        {
            const float P = period[b];
            float off = std::fmod (strobePhase * period[0] * (float) (1 << b), P);
            if (off < 0) off += P;
            for (float x = area.getX() - P + off; x < area.getRight(); x += P)
            {
                g.setColour (col.withAlpha (alpha * (0.78f - 0.14f * b)));
                g.fillRect (Rectangle<float> (x, y, P * 0.5f, bandH[b]));
            }
            y += bandH[b] + 12.0f;
        }
        g.setColour (Colours::black.withAlpha (0.55f));
        g.fillRect (area.getCentreX() - 4.0f, area.getY(), 8.0f, area.getHeight());
        g.setColour (Colours::white.withAlpha (0.35f));
        g.fillRect (area.getCentreX() - 1.5f, area.getY(), 3.0f, area.getHeight());
    }

    g.setFont (ed.fonts.mono (32.0f));
    g.setColour (tunacol::grey.withAlpha (0.7f));
    const bool fr = ed.proc.library.french;
    g.drawText (tr (fr, "< FLAT", "< GRAVE"), Rectangle<float> (X0, 1190.0f, 300.0f, 50.0f), Justification::centredLeft);
    g.drawText (tr (fr, "SHARP >", "AIGU >"), Rectangle<float> (X1 - 300.0f, 1190.0f, 300.0f, 50.0f), Justification::centredRight);
}

//==============================================================================
// ScreenButton
void ScreenButton::paint (Graphics& g)
{
    const auto b = getLocalBounds().toFloat().reduced (1.5f);
    const bool over = isMouseOver();
    g.setColour (tunacol::amber.withAlpha (primary ? (over ? 1.0f : 0.88f) : (over ? 0.16f : 0.06f)));
    g.fillRoundedRectangle (b, b.getHeight() * 0.18f);
    g.setColour (tunacol::amber.withAlpha (0.65f));
    g.drawRoundedRectangle (b, b.getHeight() * 0.18f, 1.5f);
    g.setColour (primary ? Colour (0xff14100a) : tunacol::amber);
    g.setFont (ed.fonts.mono (b.getHeight() * 0.42f));
    g.drawText (text, b, Justification::centred);
}

//==============================================================================
// TuningMenu
float TuningMenu::u() const { return getWidth() / 808.0f; }

float TuningMenu::contentHeight() const
{
    float h = 0;
    for (auto& r : rows) h += rowH (r);
    return h;
}
float TuningMenu::listHeight() const { return getHeight() / u() - listTop() - 12.0f; }

void TuningMenu::clampScroll() { scroll = jlimit (0.0f, jmax (0.0f, contentHeight() - listHeight()), scroll); }

Rectangle<float> TuningMenu::tabRect (int t) const
{
    const float w[3] = { 92.0f, 168.0f, 140.0f };
    float x = 808.0f - 18.0f;
    for (int i = 2; i >= t; --i) x -= w[i] + (i < 2 ? 6.0f : 0.0f);
    return { x, 10.0f, w[t], 42.0f };
}

Rectangle<float> TuningMenu::langRect() const { return { 236.0f, 13.0f, 56.0f, 36.0f }; }

void TuningMenu::rebuild (bool scrollToSelection)
{
    rows.clear();
    auto& lib = ed.proc.library;
    std::string lastCat;
    auto addItem = [&] (int i)
    {
        const auto& t = lib.get (i);
        if (t.category != lastCat) { rows.push_back ({ 0, String::fromUTF8 (tuna::displayCategory (t.category, lib.french).c_str()), -1 }); lastCat = t.category; }
        rows.push_back ({ 1, String::fromUTF8 (tuna::displayName (t, lib.french).c_str()), i });
    };
    if (tab == 0) for (int i = 0; i < lib.size(); ++i) addItem (i);
    else if (tab == 1)
    {
        const auto fav = lib.favouriteIndices();
        if (fav.empty()) rows.push_back ({ 0, tr (lib.french, "NO FAVORITES YET: CLICK THE STAR OF A TUNING", "AUCUN FAVORI : CLIQUEZ SUR L'ÉTOILE D'UN ACCORDAGE"), -1 });
        for (int i : fav) addItem (i);
    }
    else
    {
        rows.push_back ({ 2, tr (lib.french, "+  NEW TUNING (COPY OF THE CURRENT ONE)", "+  NOUVEL ACCORDAGE (COPIE DE L'ACTUEL)"), -1 });
        for (int i = 0; i < lib.size(); ++i) if (lib.isUser (i)) addItem (i);
    }
    if (scrollToSelection)
    {
        float y = 0;
        for (auto& r : rows)
        {
            if (r.kind == 1 && r.index == ed.proc.getTuningIndex()) { scroll = y - listHeight() * 0.4f; break; }
            y += rowH (r);
        }
    }
    clampScroll();
    repaint();
}

int TuningMenu::rowAt (float yUnits) const
{
    float y = listTop() - scroll;
    for (int i = 0; i < (int) rows.size(); ++i)
    {
        const float h = rowH (rows[(size_t) i]);
        if (yUnits >= y && yUnits < y + h) return i;
        y += h;
    }
    return -1;
}

void TuningMenu::paint (Graphics& g)
{
    const float k = u();
    g.addTransform (AffineTransform::scale (k));
    const float W = 808.0f, H = getHeight() / k;
    auto& lib = ed.proc.library;

    g.setColour (Colours::black.withAlpha (0.5f));
    g.fillRoundedRectangle (4, 8, W - 4, H - 8, 12.0f);
    g.setColour (tunacol::panel);
    g.fillRoundedRectangle (0, 0, W - 6, H - 6, 12.0f);
    const float PW = W - 6;
    g.setColour (tunacol::amber.withAlpha (0.08f));
    g.fillRoundedRectangle (1, 1, PW - 2, 58, 11.0f);
    g.setColour (tunacol::amber.withAlpha (0.3f));
    g.fillRect (0.0f, 60.0f, PW, 1.5f);
    g.setColour (tunacol::amber.withAlpha (0.55f));
    g.drawRoundedRectangle (0.75f, 0.75f, PW - 1.5f, H - 7.5f, 12.0f, 1.5f);

    g.setFont (ed.fonts.mono (27.0f).withExtraKerningFactor (0.1f));
    g.setColour (tunacol::amber);
    g.drawText (tr (lib.french, "TUNING", "ACCORDAGE"), Rectangle<float> (22, 6, 250, 50), Justification::centredLeft);
    // bouton de langue : affiche la langue vers laquelle on bascule
    {
        const auto lr = langRect();
        g.setColour (tunacol::amber.withAlpha (hoverLang ? 0.22f : 0.08f));
        g.fillRoundedRectangle (lr, 5.0f);
        g.setColour (tunacol::amber.withAlpha (0.7f));
        g.drawRoundedRectangle (lr, 5.0f, 1.5f);
        g.setFont (ed.fonts.mono (18.0f));
        g.setColour (tunacol::amber);
        g.drawText (lib.french ? "EN" : "FR", lr, Justification::centred);
    }

    const String tabNames[3] = { tr (lib.french, "ALL", "TOUS"), tr (lib.french, "FAVORITES", "FAVORIS"), tr (lib.french, "CUSTOM", "PERSO") };
    for (int t = 0; t < 3; ++t)
    {
        auto r = tabRect (t).translated (-6.0f, 0.0f);
        const bool on = tab == t;
        if (on) { g.setColour (tunacol::amber.withAlpha (0.15f)); g.fillRoundedRectangle (r, 6.0f); }
        const auto c = tunacol::amber.withAlpha (on ? 1.0f : 0.5f);
        g.setColour (c);
        float tx = r.getX() + 14;
        if (t == 1) { g.fillPath (starPath ({ tx + 9, r.getCentreY() }, 10.0f)); tx += 26; }
        if (t == 2) { g.fillPath (pencilPath ({ tx, r.getCentreY() - 10, 20, 20 })); tx += 28; }
        g.setFont (ed.fonts.mono (20.0f));
        g.drawText (tabNames[t], Rectangle<float> (tx, r.getY(), r.getRight() - tx - 8, r.getHeight()), Justification::centredLeft);
        if (on) g.fillRect (r.getX() + 10, r.getBottom() - 3, r.getWidth() - 20, 2.0f);
    }

    // liste
    Graphics::ScopedSaveState ss (g);
    g.reduceClipRegion (Rectangle<float> (2, listTop(), PW - 4, listHeight() + 6).toNearestInt());
    float y = listTop() - scroll;
    const int sel = ed.proc.getTuningIndex();
    for (int i = 0; i < (int) rows.size(); ++i)
    {
        const auto& r = rows[(size_t) i];
        const float h = rowH (r);
        if (y + h < listTop() || y > listTop() + listHeight() + 6) { y += h; continue; }
        if (r.kind == 0)
        {
            g.setFont (ed.fonts.mono (23.0f).withExtraKerningFactor (0.05f));
            g.setColour (Colour (0xff8a96a3));
            g.drawText (r.text, Rectangle<float> (22, y + 8, PW - 60, 32), Justification::centredLeft, true);
            g.setColour (Colour (0xff8a96a3).withAlpha (0.25f));
            g.fillRect (22.0f, y + h - 6, PW - 70, 1.0f);
        }
        else if (r.kind == 2)
        {
            Rectangle<float> rr (12, y + 4, PW - 50, h - 8);
            g.setColour (tunacol::amber.withAlpha (hoverRow == i ? 0.18f : 0.08f));
            g.fillRoundedRectangle (rr, 5.0f);
            g.setColour (tunacol::amber);
            g.setFont (ed.fonts.mono (21.0f));
            g.drawText (r.text, rr.reduced (14, 0), Justification::centredLeft);
        }
        else
        {
            const auto& t = lib.get (r.index);
            const bool isSel = r.index == sel;
            Rectangle<float> rr (10, y + 2, PW - 46, h - 4);
            if (isSel) { g.setColour (tunacol::amber); g.fillRoundedRectangle (rr, 5.0f); }
            else if (hoverRow == i) { g.setColour (tunacol::amber.withAlpha (0.12f)); g.fillRoundedRectangle (rr, 5.0f); }
            const auto txt = isSel ? Colour (0xff14100a) : tunacol::amber;
            g.setColour (txt);
            if (isSel) g.strokePath (checkPath ({ 22, y + h * 0.5f - 6, 14, 12 }), PathStrokeType (2.5f));
            g.setFont (ed.fonts.sans (29.0f));
            g.drawText (String::fromUTF8 (tuna::displayName (t, lib.french).c_str()), Rectangle<float> (46, y, 290, h), Justification::centredLeft, true);
            const float notesRight = PW - 46 - 50 - (t.user ? 46 : 0);
            const String nts (tuna::notesToString (t.notes));
            const float notesW = notesRight - 300.0f;
            float nf = 24.0f;
            while (nf > 17.0f && textWidth (ed.fonts.mono (nf), nts) > notesW) nf -= 0.5f;
            g.setFont (ed.fonts.mono (nf));
            g.setColour (txt.withAlpha (isSel ? 1.0f : 0.7f));
            g.drawText (nts, Rectangle<float> (300, y, notesW, h), Justification::centredRight, false);
            // crayon (perso) + étoile (favori)
            if (t.user)
            {
                g.setColour (txt.withAlpha (0.8f));
                g.fillPath (pencilPath ({ PW - 46 - 78, y + h * 0.5f - 10, 20, 20 }));
            }
            const auto star = starPath ({ PW - 46 - 26, y + h * 0.5f }, 11.0f);
            if (lib.isFavourite (r.index)) { g.setColour (isSel ? txt : tunacol::amber); g.fillPath (star); }
            else { g.setColour (txt.withAlpha (0.45f)); g.strokePath (star, PathStrokeType (1.5f)); }
        }
        y += h;
    }

    // barre de défilement
    const float ch = contentHeight(), lh = listHeight();
    if (ch > lh)
    {
        const float trackX = PW - 24, trackY = listTop() + 4, trackH = lh - 8;
        g.setColour (Colours::white.withAlpha (0.07f));
        g.fillRoundedRectangle (trackX, trackY, 7, trackH, 3.5f);
        const float th = jmax (40.0f, trackH * lh / ch);
        const float ty = trackY + (trackH - th) * (scroll / (ch - lh));
        g.setColour (tunacol::amber.withAlpha (0.7f));
        g.fillRoundedRectangle (trackX, ty, 7, th, 3.5f);
    }
}

void TuningMenu::mouseMove (const MouseEvent& e)
{
    const auto p = e.position / u();
    const int r = p.y >= listTop() ? rowAt (p.y) : -1;
    const bool hl = langRect().contains (p);
    if (r != hoverRow || hl != hoverLang) { hoverRow = r; hoverLang = hl; repaint(); }
}

void TuningMenu::mouseDown (const MouseEvent& e)
{
    const auto p = e.position / u();
    const float PW = 808.0f - 6.0f;
    draggingBar = false;
    if (langRect().contains (p))
    {
        ed.proc.library.setFrench (! ed.proc.library.french);
        rebuild (false);
        ed.repaint();
        return;
    }
    for (int t = 0; t < 3; ++t)
        if (tabRect (t).translated (-6.0f, 0.0f).contains (p)) { tab = t; scroll = 0; rebuild (t == 0); return; }
    if (p.y < listTop()) return;
    if (p.x > PW - 34 && contentHeight() > listHeight())
    {
        draggingBar = true; dragStartY = p.y; dragStartScroll = scroll;
        return;
    }
    const int ri = rowAt (p.y);
    if (ri < 0) return;
    const auto r = rows[(size_t) ri];
    auto& lib = ed.proc.library;
    if (r.kind == 2) { ed.openTuningEditor (-1); return; }
    if (r.kind != 1) return;
    if (p.x > PW - 46 - 50 && p.x < PW - 46)
    {
        lib.toggleFavourite (r.index);
        if (tab == 1) rebuild (false); else repaint();
        return;
    }
    if (lib.isUser (r.index) && p.x > PW - 46 - 88 && p.x <= PW - 46 - 50) { ed.openTuningEditor (r.index); return; }
    ed.proc.selectTuning (r.index);
    ed.closeMenu();
    ed.flash (upperName (lib.get (r.index), lib.french));
}

void TuningMenu::mouseDrag (const MouseEvent& e)
{
    if (! draggingBar) return;
    const float dy = e.position.y / u() - dragStartY;
    const float ch = contentHeight(), lh = listHeight();
    const float trackH = lh - 8, th = jmax (40.0f, trackH * lh / ch);
    scroll = dragStartScroll + dy * (ch - lh) / jmax (1.0f, trackH - th);
    clampScroll(); repaint();
}

void TuningMenu::mouseUp (const MouseEvent&) { draggingBar = false; }

void TuningMenu::mouseWheelMove (const MouseEvent&, const MouseWheelDetails& w)
{
    scroll -= w.deltaY * (w.isReversed ? -1.0f : 1.0f) * 260.0f;
    clampScroll(); repaint();
}

bool TuningMenu::keyPressed (const KeyPress& k)
{
    if (k == KeyPress::escapeKey) { ed.closeMenu(); return true; }
    if (k == KeyPress::upKey || k == KeyPress::downKey)
    {
        ed.proc.stepTuning (k == KeyPress::upKey ? -1 : 1);
        rebuild (true);
        return true;
    }
    if (k == KeyPress::returnKey) { ed.closeMenu(); return true; }
    return false;
}

//==============================================================================
// TuningEditorPanel
TuningEditorPanel::TuningEditorPanel (TunaEditor& e)
    : ed (e), save (e, "SAVE"), del (e, "DELETE"), cancel (e, "CANCEL")
{
    addAndMakeVisible (name);
    addAndMakeVisible (save); addAndMakeVisible (del); addAndMakeVisible (cancel);
    save.primary = true;
    name.setColour (TextEditor::backgroundColourId, Colour (0xff050605));
    name.setColour (TextEditor::textColourId, tunacol::amber);
    name.setColour (TextEditor::outlineColourId, tunacol::amber.withAlpha (0.45f));
    name.setColour (TextEditor::focusedOutlineColourId, tunacol::amber);
    name.setColour (TextEditor::highlightColourId, tunacol::amber.withAlpha (0.3f));
    name.setColour (TextEditor::highlightedTextColourId, tunacol::amber);
    name.setColour (CaretComponent::caretColourId, tunacol::amber);
    name.setInputRestrictions (32);

    cancel.onClick = [this] { ed.closeTuningEditor(); };
    del.onClick = [this]
    {
        if (editing < 0) return;
        const bool wasCurrent = ed.proc.getTuningIndex() == editing;
        ed.proc.library.removeUser (editing);
        if (wasCurrent) ed.proc.selectTuning (0); else ed.proc.refreshEngineTuning();
        ed.closeTuningEditor();
    };
    save.onClick = [this]
    {
        auto& lib = ed.proc.library;
        int idx = editing;
        if (idx >= 0) lib.updateUser (idx, name.getText(), notes);
        else idx = lib.addUser (name.getText(), notes);
        ed.proc.selectTuning (idx);
        ed.closeTuningEditor();
        ed.flash (upperName (lib.get (idx), lib.french));
    };
}

float TuningEditorPanel::u() const { return getWidth() / 808.0f; }

void TuningEditorPanel::open (int libraryIndex)
{
    auto& lib = ed.proc.library;
    editing = (libraryIndex >= 0 && lib.isUser (libraryIndex)) ? libraryIndex : -1;
    const auto& src = editing >= 0 ? lib.get (editing) : lib.get (ed.proc.getTuningIndex());
    notes = src.notes;
    const bool fr = lib.french;
    name.setText (editing >= 0 ? String::fromUTF8 (src.name.c_str())
                               : String::fromUTF8 (tuna::displayName (src, fr).c_str()) + (fr ? " perso" : " custom"), false);
    save.text = tr (fr, "SAVE", "ENREGISTRER");
    del.text = tr (fr, "DELETE", "SUPPRIMER");
    cancel.text = tr (fr, "CANCEL", "ANNULER");
    del.setVisible (editing >= 0);
    resized();
    repaint();
}

void TuningEditorPanel::resized()
{
    const float k = u();
    auto R = [k] (float x, float y, float w, float h) { return Rectangle<float> (x * k, y * k, w * k, h * k).toNearestInt(); };
    name.setBounds (R (150, 76, 620, 50));
    name.setFont (ed.fonts.sans (26.0f * k));
    name.setIndents ((int) (10 * k), (int) (9 * k));
    const float by = getHeight() / k - 96.0f;
    cancel.setBounds (R (24, by, 236, 64));
    del.setBounds (R (284, by, 236, 64));
    save.setBounds (R (544, by, 236, 64));
}

Rectangle<float> TuningEditorPanel::rowRect (int i) const
{
    const float H = getHeight() / u();
    const int n = jmax (1, (int) notes.size());
    const float step = jmin (58.0f, (H - 110.0f - 214.0f) / (float) n);
    return { 24.0f, 214.0f + i * step, 760.0f, step - 6.0f };
}

void TuningEditorPanel::paint (Graphics& g)
{
    const float k = u();
    g.addTransform (AffineTransform::scale (k));
    const float W = 808.0f, H = getHeight() / k;
    g.setColour (Colours::black.withAlpha (0.5f));
    g.fillRoundedRectangle (4, 8, W - 4, H - 8, 12.0f);
    const float PW = W - 6;
    g.setColour (tunacol::panel);
    g.fillRoundedRectangle (0, 0, PW, H - 6, 12.0f);
    g.setColour (tunacol::amber.withAlpha (0.55f));
    g.drawRoundedRectangle (0.75f, 0.75f, PW - 1.5f, H - 7.5f, 12.0f, 1.5f);

    g.setFont (ed.fonts.mono (24.0f).withExtraKerningFactor (0.1f));
    g.setColour (tunacol::amber);
    const bool fr = ed.proc.library.french;
    g.drawText (editing >= 0 ? tr (fr, "EDIT TUNING", "MODIFIER L'ACCORDAGE") : tr (fr, "NEW TUNING", "NOUVEL ACCORDAGE"), Rectangle<float> (24, 10, 600, 50), Justification::centredLeft);
    g.setColour (tunacol::amber.withAlpha (0.3f));
    g.fillRect (0.0f, 60.0f, PW, 1.5f);

    g.setFont (ed.fonts.mono (22.0f));
    g.setColour (Colour (0xff8a96a3));
    g.drawText (tr (fr, "NAME", "NOM"), Rectangle<float> (24, 76, 120, 50), Justification::centredLeft);
    g.drawText (tr (fr, "STRINGS", "CORDES"), Rectangle<float> (24, 146, 120, 50), Justification::centredLeft);

    auto btn = [&] (Rectangle<float> r, const String& t)
    {
        g.setColour (tunacol::amber.withAlpha (0.08f));
        g.fillRoundedRectangle (r, 6.0f);
        g.setColour (tunacol::amber.withAlpha (0.6f));
        g.drawRoundedRectangle (r, 6.0f, 1.5f);
        g.setColour (tunacol::amber);
        g.setFont (ed.fonts.mono (r.getHeight() * 0.55f));
        g.drawText (t, r, Justification::centred);
    };
    btn ({ 150, 148, 52, 46 }, "-");
    g.setFont (ed.fonts.mono (30.0f));
    g.setColour (tunacol::amber);
    g.drawText (String ((int) notes.size()), Rectangle<float> (206, 146, 70, 50), Justification::centred);
    btn ({ 280, 148, 52, 46 }, "+");
    g.setFont (ed.fonts.mono (18.0f));
    g.setColour (Colour (0xff8a96a3));
    g.drawText (tr (fr, "« » = OCTAVE   - + = SEMITONE", "« » = OCTAVE   - + = DEMI-TON"), Rectangle<float> (360, 146, 420, 50), Justification::centredRight);

    const int n = (int) notes.size();
    const int ref = (int) ed.proc.apvts.getRawParameterValue ("ref")->load();
    for (int i = 0; i < n; ++i)
    {
        const int idx = n - 1 - i;
        const auto r = rowRect (i);
        g.setColour (tunacol::amber.withAlpha (i % 2 ? 0.03f : 0.06f));
        g.fillRoundedRectangle (r, 5.0f);
        g.setFont (ed.fonts.mono (21.0f));
        g.setColour (Colour (0xff8a96a3));
        g.drawText (tr (fr, "STRING ", "CORDE ") + String (i + 1), Rectangle<float> (r.getX() + 14, r.getY(), 150, r.getHeight()), Justification::centredLeft);
        const float bh = jmin (44.0f, r.getHeight() - 4.0f), by = r.getCentreY() - bh * 0.5f;
        btn ({ 196, by, 56, bh }, String::fromUTF8 ("«"));
        btn ({ 260, by, 56, bh }, "-");
        g.setFont (ed.fonts.mono (jmin (32.0f, r.getHeight() * 0.7f)));
        g.setColour (tunacol::amber);
        g.drawText (String (tuna::noteName (notes[(size_t) idx])), Rectangle<float> (322, r.getY(), 140, r.getHeight()), Justification::centred);
        btn ({ 468, by, 56, bh }, "+");
        btn ({ 532, by, 56, bh }, String::fromUTF8 ("»"));
        g.setFont (ed.fonts.mono (20.0f));
        g.setColour (tunacol::grey.withAlpha (0.65f));
        g.drawText (String (tuna::midiToHz (notes[(size_t) idx], ref), 2) + " Hz", Rectangle<float> (596, r.getY(), 176, r.getHeight()), Justification::centredRight);
    }
}

void TuningEditorPanel::mouseDown (const MouseEvent& e)
{
    const auto p = e.position / u();
    auto hit = [&p] (Rectangle<float> r) { return r.contains (p); };
    if (hit ({ 150, 148, 52, 46 }) && notes.size() > 1) notes.pop_back();
    else if (hit ({ 280, 148, 52, 46 }) && notes.size() < (size_t) tuna::kMaxStrings)
        notes.push_back (jmin (88, (notes.empty() ? 40 : notes.back() + 5)));
    else
    {
        const int n = (int) notes.size();
        for (int i = 0; i < n; ++i)
        {
            const auto r = rowRect (i);
            auto& nt = notes[(size_t) (n - 1 - i)];
            const float bh = jmin (44.0f, r.getHeight() - 4.0f), by = r.getCentreY() - bh * 0.5f;
            if (hit ({ 196, by, 56, bh })) nt -= 12;
            else if (hit ({ 260, by, 56, bh })) nt -= 1;
            else if (hit ({ 468, by, 56, bh })) nt += 1;
            else if (hit ({ 532, by, 56, bh })) nt += 12;
            else continue;
            nt = jlimit (12, 88, nt);   // C0 .. E6
        }
    }
    repaint();
}

//==============================================================================
// TunaEditor
void TunaEditor::Foot::paint (Graphics& g)
{
    const auto b = getLocalBounds().toFloat();
    // reflet de la LED jaune sur le flanc du footswitch, en fondu avec la LED
    if (ledLevel > 0.003f && reflection.isValid())
    {
        g.setOpacity (ledLevel);
        g.drawImage (reflection, b);
        g.setOpacity (1.0f);
    }
    if (down)
    {
        // bouton assombri tant qu'on appuie (disque noir à 25 %)
        const float r = b.getWidth() * (art::footR / art::fsS) * 0.98f;
        const auto c = b.getCentre();
        g.setColour (Colours::black.withAlpha (0.25f));
        g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
    }
}

TunaEditor::TunaEditor (TunaProcessor& p)
    : AudioProcessorEditor (&p), proc (p)
{
    background = ImageCache::getFromMemory (BinaryData::background_png, BinaryData::background_pngSize);
    glow       = ImageCache::getFromMemory (BinaryData::glow_yellow_png, BinaryData::glow_yellow_pngSize);
    ledOn      = ImageCache::getFromMemory (BinaryData::led_on_png, BinaryData::led_on_pngSize);
    fsRefl     = ImageCache::getFromMemory (BinaryData::fs_refl_png, BinaryData::fs_refl_pngSize);
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogo_svg, BinaryData::NineHandsLogo_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    menuLnf.reg = fonts.popLight; menuLnf.med = fonts.popMed; menuLnf.bold = fonts.popBold;
    setLookAndFeel (&menuLnf);             // menus clic droit (et sous-menus) au design d'Octopus

    addAndMakeVisible (display);
    addAndMakeVisible (foot);
    addChildComponent (dismiss);
    addChildComponent (menu);
    addChildComponent (tuningEditor);
    menu.setWantsKeyboardFocus (true);
    foot.setMouseCursor (MouseCursor::PointingHandCursor);
    foot.reflection = fsRefl;

    // footswitch : TUNE / MUTE (bascule dès l'appui, comme Echoflex)
    foot.onPress = [this] { setParam ("mute", isMuted() ? 0.0f : 1.0f); };
    foot.onRight = [this] { showFootMenu(); };
    dismiss.onClick = [this] { closeTuningEditor(); closeMenu(); };

    // taille : jamais plus petite que la taille par défaut, proportions de la pédale (1235 x 1800)
    const double aspect = (double) art::W / (double) art::H;
    setResizable (true, true);
    setResizeLimits (roundToInt (tunaui::heightDefault * aspect), tunaui::heightDefault,
                     roundToInt (tunaui::heightMax * aspect), tunaui::heightMax);
    getConstrainer()->setFixedAspectRatio (aspect);
    setOpaque (true);                      // anti-gel : l'hôte ne redessine jamais ce qui est derrière la fenêtre
    // taille d'ouverture : celle enregistrée pour cette instance (projet) si elle existe,
    // sinon celle choisie dans le menu « Default size (new windows) »
    const int saved = proc.uiHeight.load();
    const int h0 = saved > 0 ? jlimit (tunaui::heightDefault, tunaui::heightMax, saved)
                             : sizeHeight (WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes));
    openHeight = h0;
    setSize (roundToInt (h0 * aspect), h0);
    rebuildCaches();

    snap = proc.getSnapshot();
    ledLevel = isMuted() ? 1.0f : 0.0f;
    foot.ledLevel = ledLevel;
    lastTime = Time::getMillisecondCounterHiRes() * 0.001;
    updateTimerRate();
}

TunaEditor::~TunaEditor()
{
    stopTimer();
    setLookAndFeel (nullptr);
}

int TunaEditor::modeIndex() const { return jlimit (0, 2, (int) std::lround (proc.apvts.getRawParameterValue ("mode")->load())); }
bool TunaEditor::isMuted() const { return proc.apvts.getRawParameterValue ("mute")->load() > 0.5f; }

void TunaEditor::setParam (const char* id, float plain)
{
    if (auto* prm = proc.apvts.getParameter (id))
    {
        prm->beginChangeGesture();
        prm->setValueNotifyingHost (prm->convertTo0to1 (plain));
        prm->endChangeGesture();
    }
}

void TunaEditor::stepTuning (int d)
{
    proc.stepTuning (d);
    flash (upperName (proc.library.get (proc.getTuningIndex()), proc.library.french));
    if (menu.isVisible()) menu.rebuild (true);
    display.repaint();
}

void TunaEditor::stepRef (int d)
{
    const int r = jlimit (430, 450, (int) proc.apvts.getRawParameterValue ("ref")->load() + d);
    setParam ("ref", (float) r);
    display.repaint();
}

Rectangle<int> TunaEditor::scaled (Rectangle<float> r) const
{
    const float s = scale();
    return Rectangle<float> (r.getX() * s, r.getY() * s, r.getWidth() * s, r.getHeight() * s).toNearestInt();
}

Rectangle<float> TunaEditor::menuArea() const
{
    // panneau large (toute la largeur de la pédale) sous la barre d'accordage, pour rester lisible à la taille par défaut
    const float top = art::screen.getY() + TunaDisplay::zoneRect (TunaDisplay::zNext).getBottom() + 12.0f;
    return { 20.0f, top, art::W - 40.0f, art::H - 20.0f - top };
}

//==============================================================================
// Anti-gel de la fenêtre (Windows) : JUCE 8 dessine par défaut avec Direct2D (carte graphique).
// Avec certains pilotes (Intel notamment) la fenêtre du plugin cesse de se rafraîchir alors que
// le DAW continue de tourner. Le moteur logiciel est stable partout et largement assez rapide ici.
//
// Anti-gel v2 (NINE HANDS | DSP) :
//  1. moteur de rendu logiciel forcé sur Windows, appliqué à chaque nouvelle fenêtre hôte (peer)
//     et revérifié toutes les secondes, jamais en boucle ;
//  2. aucun calcul lourd dans paint() : le fond mis à l'échelle est refait par le timer seulement,
//     après stabilisation de la taille ou quand l'échelle d'affichage change (au plus toutes les 250 ms) ;
//  3. chien de garde : si un redessin demandé n'est pas arrivé au bout de 1,5 s alors que la fenêtre
//     est visible, le moteur de rendu est réappliqué et toute la fenêtre est redessinée ;
//  4. côté audio : aucun appel à l'hôte depuis le thread audio (voir PluginProcessor).
void TunaEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw)
            peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void TunaEditor::parentHierarchyChanged() { useSoftwareRenderer(); }
void TunaEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

void TunaEditor::askRepaint (Rectangle<int> r)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (r);
}

float TunaEditor::physicalScale() const
{
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

// fond et lumière de la LED déjà à la taille de la fenêtre (pixels physiques) :
// appelé par le constructeur et le timer, jamais par paint()
void TunaEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;

    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    bgScaled = (pw >= background.getWidth()) ? background : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    const int gpx = roundToInt (art::glowRect.getWidth() * scale() * sc);
    glowScaled = (gpx >= glow.getWidth() || gpx <= 0) ? glow : glow.rescaled (gpx, gpx, Graphics::highResamplingQuality);
    repaint();
}

// Cadence de l'affichage : 30 i/s suffisent en MONO / POLY (le moteur publie ses mesures 25 fois
// par seconde, les segments sont discrets). En STROBE on garde 60 i/s : à 30 i/s la bande fine
// semblerait s'arrêter puis tourner à l'envers près de la justesse (effet « roue de diligence »).
void TunaEditor::updateTimerRate()
{
    const int hz = modeIndex() == 2 ? 60 : 30;
    if (hz != timerHz) { timerHz = hz; startTimerHz (hz); }
}

void TunaEditor::resized()
{
    // anti-gel : jamais de setSize ici (mise à l'échelle Windows 125 / 150 % : l'hôte arrondit les tailles) ;
    // les limites du constrainer suffisent, sinon boucle de redimensionnement avec l'hôte
    // taille de cette instance enregistrée seulement si elle a été changée (sinon : taille par défaut choisie)
    if (proc.uiHeight.load() > 0 || (openHeight > 0 && std::abs (getHeight() - openHeight) > 2))
        proc.uiHeight.store (jlimit (tunaui::heightDefault, tunaui::heightMax, getHeight()));

    display.setBounds (scaled (art::screen));
    foot.setBounds (scaled (Rectangle<float> (art::fsS, art::fsS).withCentre (art::fs)));
    dismiss.setBounds (getLocalBounds());
    menu.setBounds (scaled (menuArea()));
    tuningEditor.setBounds (scaled (menuArea()));
    resizeSettle = 4;              // les caches seront refaits par le timer quand la taille ne bouge plus
}

int TunaEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { tunaui::heightDefault, tunaui::height75, tunaui::height100 };
    return h[jlimit (0, numSizes - 1, idx)];
}

void TunaEditor::setWindowHeight (int h)
{
    h = jlimit (tunaui::heightDefault, tunaui::heightMax, h);
    setSize (roundToInt ((double) h * art::W / art::H), h);
}

void TunaEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (13, 13, 14));       // derrière les zones transparentes (autour des jacks)
    // anti-gel : aucun rescale ici, on dessine le cache existant (ou l'original en attendant le timer)
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid())
        g.drawImage (bg, getLocalBounds().toFloat());

    const float s = scale();
    Graphics::ScopedSaveState ss (g);
    g.addTransform (AffineTransform::scale (s));
    g.setImageResamplingQuality (Graphics::highResamplingQuality);

    // LED jaune : la façade reçoit sa lumière (calque alpha précalculé), lentille allumée, léger halo
    if (ledLevel > 0.003f)
    {
        const Image& gl = glowScaled.isValid() ? glowScaled : glow;
        if (gl.isValid()) { g.setOpacity (ledLevel); g.drawImage (gl, art::glowRect); }
        const float hs = art::ledS * 0.5f;
        if (ledOn.isValid()) { g.setOpacity (ledLevel); g.drawImage (ledOn, { art::led.x - hs, art::led.y - hs, hs * 2.0f, hs * 2.0f }); }
        g.setOpacity (1.0f);
        const float hr = 40.0f;
        ColourGradient halo (tunacol::ledYellow.withAlpha (0.30f * ledLevel), art::led.x, art::led.y,
                             tunacol::ledYellow.withAlpha (0.0f), art::led.x + hr, art::led.y, true);
        halo.addColour (0.4, tunacol::ledYellow.withAlpha (0.08f * ledLevel));
        g.setGradientFill (halo);
        g.fillEllipse (art::led.x - hr, art::led.y - hr, hr * 2.0f, hr * 2.0f);
    }

    // logo NINE HANDS | DSP (vectoriel)
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = art::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { art::logo.x - w * 0.5f, art::logo.y - h * 0.5f, w, h }, RectanglePlacement::centred, 0.88f);
    }
}

void TunaEditor::mouseDown (const MouseEvent& e)
{
    if (e.mods.isPopupMenu()) showContextMenu();
}

void TunaEditor::addMidiLearnSection (PopupMenu& m, int learnIdx)
{
    if (learnIdx < 0) return;
    const int lt = proc.learnTarget.load();
    auto ccText = [this] (int i) { const int cc = proc.ccMap[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("none"); };
    // barre d'accordage : ses deux sens, accordage suivant et précédent
    const int first = learnIdx == 2 ? 2 : learnIdx, last = learnIdx == 2 ? 3 : learnIdx;
    for (int i = first; i <= last; ++i)
    {
        const String name = TunaProcessor::learnDef (i).name;
        m.addItem (1000 + i, "MIDI Learn: " + name + " (" + ccText (i) + ")", true, lt == i);
        m.addItem (1100 + i, "Clear MIDI: " + name, proc.ccMap[i].load() >= 0);
    }
    if (lt >= 0) m.addItem (1200, "Cancel MIDI learn");
    m.addSeparator();
}

bool TunaEditor::handleMidiLearnItem (int r)
{
    if (r >= 1000 && r < 1000 + TunaProcessor::numLearn)
    {
        if (proc.learnTarget.load() == r - 1000) { proc.learnTarget.store (-1); flash ("MIDI LEARN CANCELLED"); }   // re-cliquer annule
        else proc.learnTarget.store (r - 1000);
    }
    else if (r >= 1100 && r < 1100 + TunaProcessor::numLearn)
    {
        proc.ccMap[r - 1100].store (-1);
        flash (String (TunaProcessor::learnDef (r - 1100).name).toUpperCase() + " : MIDI CLEARED");
    }
    else if (r == 1200) { proc.learnTarget.store (-1); flash ("MIDI LEARN CANCELLED"); }
    else if (r == 1201) { proc.learnTarget.store (-1); proc.clearMidiMap(); flash ("MIDI CLEARED"); }
    else return false;
    return true;
}

void TunaEditor::showFootMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    addMidiLearnSection (m, 0);
    m.addSectionHeader ("Footswitch MUTE (MIDI)");
    const bool mom = proc.apvts.getRawParameterValue ("ccmomentary")->load() > 0.5f;
    m.addItem (2, "Latching pedal (127 = mute, 0 = on)", true, ! mom);
    m.addItem (3, "Momentary pedal (each press toggles)", true, mom);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),          // toujours là où l'on clique
        [safe = Component::SafePointer<TunaEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            if (safe->handleMidiLearnItem (r)) return;
            if (r == 2 || r == 3)
                if (auto* prm = safe->proc.apvts.getParameter ("ccmomentary")) prm->setValueNotifyingHost (r == 3 ? 1.0f : 0.0f);
        });
}

void TunaEditor::showContextMenu (int learnIdx)
{
    // Plugin size : taille de cette fenêtre + taille par défaut des nouvelles fenêtres (comme Octopus)
    PopupMenu size, defSize;
    const int h = getHeight();
    const char* sizeNames[numSizes] = { "60 %", "75 %", "100 %" };
    const int def = WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes);
    for (int i = 0; i < numSizes; ++i)
    {
        size.addItem (101 + i, String (sizeNames[i]) + (i == def ? "  (default)" : ""), true, std::abs (h - sizeHeight (i)) < 8);
        defSize.addItem (120 + i, sizeNames[i], true, i == def);
    }
    size.addSeparator();
    size.addSubMenu ("Default size (new windows)", defSize);

    PopupMenu midi, chan;
    const int ch = (int) proc.apvts.getRawParameterValue ("midichan")->load();
    chan.addItem (300, "Omni", true, ch == 0);
    for (int c = 1; c <= 16; ++c) chan.addItem (300 + c, String (c), true, ch == c);
    midi.addSubMenu ("MIDI channel", chan);
    midi.addSeparator();
    for (int i = 0; i < TunaProcessor::numLearn; ++i)
    {
        const int cc = proc.ccMap[i].load();
        midi.addItem (1000 + i, "Learn: " + String (TunaProcessor::learnDef (i).name) + " (" + (cc >= 0 ? "CC " + String (cc) : String ("none")) + ")",
                      true, proc.learnTarget.load() == i);
    }
    midi.addSeparator();
    if (proc.learnTarget.load() >= 0) midi.addItem (1200, "Cancel MIDI learn");
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    const bool mom = proc.apvts.getRawParameterValue ("ccmomentary")->load() > 0.5f;
    midi.addItem (210, "Footswitch: latching pedal", true, ! mom);
    midi.addItem (211, "Footswitch: momentary pedal", true, mom);
    midi.addItem (-1, "Program Change n = favourite n (or tuning n)", false, false);

    PopupMenu m;
    addMidiLearnSection (m, learnIdx);
    m.addSubMenu ("Plugin size", size);
    m.addSubMenu ("MIDI", midi);
    m.addSeparator();
    m.addItem (401, "Custom tunings...");
    m.addItem (402, "Show tunings file");
    m.addSeparator();
    m.addItem (999, "Chroma tuner v" + String (JucePlugin_VersionString) + " - NINE HANDS | DSP", false);

    m.setLookAndFeel (&menuLnf);
    m.showMenuAsync (PopupMenu::Options().withMousePosition(),          // menu clic droit : toujours là où l'on clique
        [safe = Component::SafePointer<TunaEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            auto& pr = ed.proc;
            if (r >= 101 && r < 101 + numSizes) ed.setWindowHeight (sizeHeight (r - 101));
            else if (r >= 120 && r < 120 + numSizes)
            {
                WigaWindowSize::setDefaultIndex (JucePlugin_Name, r - 120);   // toutes les nouvelles fenêtres de ce plugin
                ed.setWindowHeight (sizeHeight (r - 120));                    // et cette fenêtre tout de suite
            }
            else if (ed.handleMidiLearnItem (r)) {}
            else if (r == 210 || r == 211) { if (auto* p = pr.apvts.getParameter ("ccmomentary")) p->setValueNotifyingHost (r == 211 ? 1.0f : 0.0f); }
            else if (r >= 300 && r <= 316) { if (auto* p = pr.apvts.getParameter ("midichan")) p->setValueNotifyingHost (p->convertTo0to1 ((float) (r - 300))); }
            else if (r == 401) { ed.openMenu(); ed.menu.tab = 2; ed.menu.rebuild (false); }
            else if (r == 402)
            {
                auto f = TuningLibrary::file();
                if (f.existsAsFile()) f.revealToUser();
                else { f.getParentDirectory().createDirectory(); f.getParentDirectory().revealToUser(); }
            }
        });
}

void TunaEditor::openMenu()
{
    closeTuningEditor();
    proc.library.reload();
    proc.refreshEngineTuning();
    dismiss.setVisible (true);
    dismiss.toFront (false);
    menu.setBounds (scaled (menuArea()));
    menu.setVisible (true);
    menu.toFront (true);
    menu.rebuild (true);
    menu.grabKeyboardFocus();
}

void TunaEditor::closeMenu()
{
    menu.setVisible (false);
    if (! tuningEditor.isVisible()) dismiss.setVisible (false);
}

void TunaEditor::openTuningEditor (int libraryIndex)
{
    menu.setVisible (false);
    dismiss.setVisible (true);
    dismiss.toFront (false);
    tuningEditor.setBounds (scaled (menuArea()));
    tuningEditor.open (libraryIndex);
    tuningEditor.setVisible (true);
    tuningEditor.toFront (true);
}

void TunaEditor::closeTuningEditor()
{
    tuningEditor.setVisible (false);
    if (! menu.isVisible()) dismiss.setVisible (false);
}

void TunaEditor::flash (const String& text)
{
    display.flashText = text;
    display.flashUntil = Time::getMillisecondCounterHiRes() * 0.001 + 1.1;
    display.repaint();
}

void TunaEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes() * 0.001;
    const float dt = (float) jlimit (0.0, 0.1, now - lastTime);
    lastTime = now;
    snap = proc.getSnapshot();

    // moteur logiciel : seulement si la fenêtre hôte a changé, ou au plus une fois par seconde
    const double nowMs = now * 1000.0;
    if (getPeer() != lastPeer || nowMs - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = nowMs; useSoftwareRenderer(); }

    // caches : reconstruits ici seulement (jamais dans paint)
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && nowMs - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = nowMs;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }

    // chien de garde : un redessin demandé n'arrive pas -> on relance le moteur de rendu et on redessine tout
    if (repaintAskedMs > 0.0 && isShowing() && nowMs - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0;
        lastPeer = nullptr;
        useSoftwareRenderer();
        repaint();
    }

    // stroboscope : 1 cent = un quart de période par seconde (bande du haut)
    if (snap.monoMidi >= 0 && (snap.monoActive || snap.monoAge < 0.3f))
        display.strobePhase += dt * jlimit (-6.0f, 6.0f, snap.monoCents * 0.25f);

    // MIDI learn terminé ?
    const int learn = proc.learnTarget.load();
    const int learned = proc.lastLearned.exchange (-1);
    if (learned >= 0)
    {
        display.flashText = String (TunaProcessor::learnDef (learned).name) + " = CC " + String (proc.ccMap[learned].load());
        display.flashUntil = now + 2.0;
    }
    else if (learn >= 0)
    {
        display.flashText = "MIDI LEARN: move a control for " + String (TunaProcessor::learnDef (learn).name);
        display.flashUntil = now + 0.2;
    }
    lastLearn = learn;

    // LED jaune (MUTE) en fondu, comme Echoflex
    {
        const bool on = isMuted();
        ledLevel += ((on ? 1.0f : 0.0f) - ledLevel) * (on ? 0.45f : 0.28f);
        if (ledLevel < 0.003f) ledLevel = 0.0f;
        if (ledLevel > 0.997f) ledLevel = 1.0f;
        if (std::abs (ledLevel - drawnLed) > 0.004f)
        {
            drawnLed = ledLevel;
            foot.ledLevel = ledLevel;
            askRepaint (scaled (art::glowRect).getUnion (foot.getBounds()));
        }
    }

    // l'écran n'est redessiné que si ce qu'il affiche a changé (valeurs arrondies à ce qui est visible)
    {
        uint64_t h = 1469598103934665603ull;
        auto mix = [&h] (int64_t v) { h ^= (uint64_t) v; h *= 1099511628211ull; };
        mix (modeIndex()); mix (proc.getTuningIndex()); mix (proc.library.french ? 1 : 0); mix (proc.library.size());
        mix ((int) proc.apvts.getRawParameterValue ("ref")->load());
        mix (snap.allInTune); mix (snap.monoOffTuning); mix (snap.anyStringActive); mix (snap.numStrings);
        for (int i = 0; i < snap.numStrings; ++i)
        {
            const auto& st = snap.strings[i];
            mix (st.midi); mix (st.measured); mix (st.active);
            mix ((int64_t) std::lround (st.cents * 4.0f));
            mix (st.active ? 0 : (int64_t) std::lround (jlimit (0.0f, 7.0f, st.age) * 8.0f));
        }
        mix (snap.monoMidi); mix (snap.monoActive); mix (snap.monoPrecise);
        mix ((int64_t) std::lround (snap.monoCents * 10.0f));
        mix ((int64_t) std::lround (snap.monoHz * 100.0f));
        mix (snap.monoActive ? 0 : (int64_t) std::lround (jlimit (0.0f, 3.0f, snap.monoAge) * 10.0f));
        if (modeIndex() == 2) mix ((int64_t) std::lround (display.strobePhase * 400.0f));
        const bool flashOn = now < display.flashUntil;
        mix (flashOn); if (flashOn) mix (display.flashText.hashCode64());
        if (h != lastDisplaySig) { lastDisplaySig = h; askRepaint (display.getBounds()); }
    }

    const int m = modeIndex();
    if (m != lastMode) { lastMode = m; askRepaint (display.getBounds()); }
    updateTimerRate();
}
