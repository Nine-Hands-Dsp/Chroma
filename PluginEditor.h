#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include <juce_audio_processors/juce_audio_processors.h>
#include "PluginProcessor.h"
#include "NineHandsMenu.h"
#include "NineHandsWindow.h"

//==============================================================================
// Géométrie du visuel v2 (pixels de background.png : 1235 x 1800, pédale plein cadre)
// valeurs de tools/layout.json (repère plugin 617.5 x 900) x 2
namespace art
{
constexpr float W = 1235.0f, H = 1800.0f;
const juce::Rectangle<float> screen { 78.5f, 40.0f, 1078.0f, 1345.0f };   // vitre (contenu dessiné par TunaDisplay)
constexpr float screenRadius = 26.0f;
const juce::Point<float> led { 617.5f, 1428.0f };  constexpr float ledS = 52.5f;          // LED jaune (sprite led_on)
const juce::Rectangle<float> glowRect { 467.5f, 1278.0f, 300.0f, 300.0f };                // lumière de la LED sur la façade
const juce::Point<float> fs { 617.5f, 1590.0f };   constexpr float footR = 77.82f, fsS = 391.4f;   // footswitch (bouton / sprite)
const juce::Point<float> logo { 617.5f, 1742.0f }; constexpr float logoW = 380.0f;        // NINE HANDS | DSP
}

//==============================================================================
namespace tunacol
{
const juce::Colour orange   { 0xffe0662a };
const juce::Colour amber    { 0xffffb23a };
const juce::Colour amberDim { 0xff3a2808 };
const juce::Colour green    { 0xff5dff8a };
const juce::Colour greenDim { 0xff12351f };
const juce::Colour grey     { 0xffc9ced3 };
const juce::Colour panel    { 0xff0b0d0f };
const juce::Colour ledYellow{ 0xffffb824 };
}

struct TunaFonts
{
    TunaFonts();
    juce::Font mono (float h) const;
    juce::Font sans (float h) const;
    juce::Typeface::Ptr monoTf, sansTf, popMed, popBold, popLight;
};

class TunaEditor;

//==============================================================================
// Écran tactile : rangée MONO / POLY / STROBE + référence A=440 + logo CHROMA,
// barre d'accordage (flèches + menu déroulant), puis l'affichage du mode.
// Tout est dessiné dans un repère de 1078 x 1345 unités (pixels du visuel).
class TunaDisplay : public juce::Component
{
public:
    TunaDisplay (TunaEditor& e);
    void paint (juce::Graphics&) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    static constexpr float kSW = 1078.0f, kSH = 1345.0f;
    enum Zone { zNone = -1, zMono = 0, zPoly, zStrobe, zRefDown, zRefMid, zRefUp, zPrev, zDrop, zNext, zLogo };
    static juce::Rectangle<float> zoneRect (int z);
    int zoneAt (juce::Point<float> unitsPos) const;
    juce::Rectangle<float> tuningBar() const;
    float strobePhase = 0;
    juce::String flashText;
    double flashUntil = 0;
    int hover = zNone;

private:
    void paintHeader (juce::Graphics&, const tuna::Snapshot&, int mode, bool autoMono);
    void paintPoly (juce::Graphics&, const tuna::Snapshot&);
    void paintMono (juce::Graphics&, const tuna::Snapshot&);
    void paintStrobe (juce::Graphics&, const tuna::Snapshot&);
    TunaEditor& ed;
    std::unique_ptr<juce::Drawable> wordmark;
    float wheelAccum = 0;
};

//==============================================================================
// Petit bouton plat au style de l'écran
class ScreenButton : public juce::Component
{
public:
    ScreenButton (TunaEditor& e, juce::String t) : ed (e), text (std::move (t)) {}
    void paint (juce::Graphics&) override;
    void mouseUp (const juce::MouseEvent& e) override { if (e.mouseWasClicked() && onClick) onClick(); }
    void mouseEnter (const juce::MouseEvent&) override { repaint(); }
    void mouseExit (const juce::MouseEvent&) override { repaint(); }
    std::function<void()> onClick;
private:
    TunaEditor& ed;
public:
    juce::String text;
    bool primary = false;
};

//==============================================================================
// Menu déroulant des accordages (style écran ambre)
class TuningMenu : public juce::Component
{
public:
    TuningMenu (TunaEditor& e) : ed (e) {}
    void paint (juce::Graphics&) override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override { hoverRow = -1; repaint(); }
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;
    bool keyPressed (const juce::KeyPress&) override;

    void rebuild (bool scrollToSelection);
    int tab = 0;                  // 0 = tous, 1 = favoris, 2 = perso

private:
    struct Row { int kind; juce::String text; int index; };   // kind 0 = catégorie, 1 = accordage, 2 = "nouvel accordage"
    float u() const;              // pixels par unité "écran"
    float rowH (const Row& r) const { return r.kind == 0 ? 50.0f : 54.0f; }
    float contentHeight() const;
    float listTop() const { return 64.0f; }
    float listHeight() const;
    int rowAt (float yUnits) const;
    juce::Rectangle<float> tabRect (int t) const;
    juce::Rectangle<float> langRect() const;
    void clampScroll();

    TunaEditor& ed;
    std::vector<Row> rows;
    float scroll = 0;
    int hoverRow = -1;
    bool hoverLang = false;
    bool draggingBar = false;
    float dragStartY = 0, dragStartScroll = 0;
};

//==============================================================================
// Éditeur d'accordage perso
class TuningEditorPanel : public juce::Component
{
public:
    TuningEditorPanel (TunaEditor& e);
    void paint (juce::Graphics&) override;
    void resized() override;
    void mouseDown (const juce::MouseEvent&) override;
    void open (int libraryIndex);   // -1 = nouveau (copie de l'accordage actif)

private:
    float u() const;
    juce::Rectangle<float> rowRect (int i) const;     // i = 0 : corde la plus aiguë
    TunaEditor& ed;
    int editing = -1;
    std::vector<int> notes;
    juce::TextEditor name;
    ScreenButton save, del, cancel;
};

//==============================================================================
class TunaEditor : public juce::AudioProcessorEditor,
                   private juce::Timer
{
public:
    explicit TunaEditor (TunaProcessor&);
    ~TunaEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;
    void mouseDown (const juce::MouseEvent&) override;

    TunaProcessor& proc;
    TunaFonts fonts;
    tuna::Snapshot snap;
    int  modeIndex() const;
    bool isMuted() const;
    float scale() const { return (float) getWidth() / art::W; }

    void setParam (const char* id, float plain);
    void stepTuning (int d);
    void stepRef (int d);
    void openMenu();
    void closeMenu();
    void openTuningEditor (int libraryIndex);
    void closeTuningEditor();
    void flash (const juce::String& text);
    void setWindowHeight (int h);
    static constexpr int numSizes = 3;           // 60 % (défaut d'origine) / 75 % / 100 %
    static int sizeHeight (int idx);
    void showContextMenu (int learnIdx = -1);     // learnIdx >= 0 : clic droit sur une commande (MIDI Learn en tête du menu)
    void showFootMenu();
    juce::PopupMenu buildContextMenu (int learnIdx = -1);   // menu clic droit (aussi pour l'outil de controle des menus)
    NineHandsWindow::HostLock hostLock;          // fenetre du DAW : jamais sous 60 %, jamais au-dela de 150 %
    float glowAmt() const { return (float) glowPc / 100.0f; }
    int glowPc = 100;
    double lastGlowCheckMs = 0.0;
    void addMidiLearnSection (juce::PopupMenu& m, int learnIdx);
    bool handleMidiLearnItem (int r);             // true si r était un élément MIDI Learn
    void updateKnobAngles() {}                    // (v1) gardé pour les outils de rendu

private:
    void timerCallback() override;
    void visibilityChanged() override;
    void useSoftwareRenderer();
    void updateTimerRate();
    int timerHz = 0;              // cadence actuelle du timer de l'éditeur (30 ou 60 en STROBE)
    uint64_t lastDisplaySig = 0;  // empreinte de ce que montre l'écran (redessin seulement si elle change)
    juce::Image bgScaled, glowScaled;   // caches à la taille de la fenêtre (refaits par le timer seulement)
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f;
    int resizeSettle = 0;
    int openHeight = 0;           // hauteur d'ouverture de la fenêtre (taille par défaut ou taille de l'instance)
    void rebuildCaches (float scale = 0.0f);
    float physicalScale() const;
    // anti-gel v2 : suivi de la fenêtre hôte, de l'échelle et des redessins
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;
    void askRepaint (juce::Rectangle<int> r);
    juce::Rectangle<int> scaled (juce::Rectangle<float> r) const;
    juce::Rectangle<float> menuArea() const;

    juce::Image background, glow, ledOn, fsRefl;
    std::unique_ptr<juce::Drawable> logo;
    NineHandsMenu::MenuLnf menuLnf;           // menus clic droit au design d'Octopus
    float ledLevel = 0.0f, drawnLed = -1.0f;

    TunaDisplay display { *this };
    struct Foot : juce::Component
    {
        std::function<void()> onPress, onRight;
        bool down = false;
        float ledLevel = 0.0f;
        juce::Image reflection;
        bool hitTest (int x, int y) override
        {
            return juce::Point<float> ((float) x, (float) y).getDistanceFrom (getLocalBounds().toFloat().getCentre())
                   <= (float) getWidth() * (art::footR * 1.35f / art::fsS);
        }
        void paint (juce::Graphics&) override;
        void mouseDown (const juce::MouseEvent& e) override { if (e.mods.isPopupMenu()) { if (onRight) onRight(); return; } down = true; if (onPress) onPress(); repaint(); }
        void mouseUp (const juce::MouseEvent& e) override { if (e.mods.isPopupMenu()) return; down = false; repaint(); }
    } foot;
    struct Dismiss : juce::Component { std::function<void()> onClick; void mouseDown (const juce::MouseEvent&) override { if (onClick) onClick(); } } dismiss;

public:
    TuningMenu menu { *this };
    TuningEditorPanel tuningEditor { *this };

private:
    double lastTime = 0;
    int lastMode = -1;
    int lastLearn = -1;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TunaEditor)
};
