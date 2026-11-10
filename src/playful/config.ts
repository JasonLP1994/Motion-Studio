// "Shape that never cuts": a playful 8 s sting. Every word, colour, timing and sound lives here.
// Frames at 30 fps (120 bpm = a beat every 15 frames).

export const playfulConfig = {
  output: { width: 1080, height: 1080, fps: 30, durationInFrames: 240 },
  words: ["MOTION", "STUDIO"], // the three O's are where the three balls land
  maxTextWidth: 860,
  font: { family: "Fredoka", file: "fonts/fredoka-latin-700-normal.woff2", weight: "700" },
  // Measured from the font (see src/playful/Calib.tsx): O width, height, stroke and centre, in em.
  oGlyph: { width: 0.69, height: 0.72, stroke: 0.185, centreFromTop: 0.5275 },
  lineGap: 0.9, // em between the two lines' tops

  colors: {
    sun: "#FFC93C", // first ground
    tomato: "#FF5A36", // the ball, then the second ground
    ink: "#1C1B22", // final ground
    cream: "#FFF4E4", // letters and the second ball
    mint: "#3DDC97",
    sky: "#5B8CFF",
    eyeWhite: "#FFFFFF",
    pupil: "#1C1B22",
  },
  ringColors: ["sun", "mint", "cream"] as const, // O in MOTI(O)N... order: first O, second O, STUDI(O)

  ball: { radius: 80, startY: 220, floorY: 700 },
  bounces: { hits: [12, 30, 40], heights: [300, 90], squash: [1, 0.6, 0.3] },
  launch: { crouch: 48, go: 54, apexY: 230, apex: 64, land: 72 },
  pill: { width: 340, height: 70, stretchAt: 84, floodAt: 90, floodDone: 102 },
  cream: { popAt: 100, radius: 70, crouch: 112, split: 116, smallRadius: 52, spread: 230, lands: [127, 130, 133] },
  toO: { start: 138, stagger: 3, duration: 18 },
  letters: { start: 158, stagger: 2 },
  inkFlood: { start: 186, duration: 12 },
  wink: 214,
  eyesInO: 1.4, // eye size inside the last O (1 = fills the hole edge to edge)

  // Sound effects (bundled CC0 library). frame = when the picture happens; offsetMs = the file's peak,
  // so each peak lands one frame after its picture.
  masterVolume: 1.0,
  sounds: [
    { frame: 12, file: "sfx/pop_kenney-interface-drop-001.ogg", volume: 0.9, peakMs: 0 },
    { frame: 30, file: "sfx/pop_kenney-interface-drop-002.ogg", volume: 0.6, peakMs: 0 },
    { frame: 40, file: "sfx/pop_kenney-interface-drop-003.ogg", volume: 0.4, peakMs: 0 },
    { frame: 54, file: "sfx/whoosh_fs-683101-quick-woosh.ogg", volume: 0.9, peakMs: 29 },
    { frame: 72, file: "sfx/kit_pop.ogg", volume: 0.8, peakMs: 3 },
    { frame: 88, file: "sfx/transition_fs-786514-swoosh-v2.ogg", volume: 0.6, peakMs: 2 },
    { frame: 100, file: "sfx/pop_fs-824189-pop-in-sfx.ogg", volume: 0.8, peakMs: 63 },
    { frame: 116, file: "sfx/ui-blip_kenney-digital-twotone1.ogg", volume: 0.5, peakMs: 14 },
    { frame: 127, file: "sfx/pop_kenney-interface-pluck-001.ogg", volume: 0.7, peakMs: 1 },
    { frame: 130, file: "sfx/pop_kenney-interface-pluck-002.ogg", volume: 0.7, peakMs: 1 },
    { frame: 133, file: "sfx/pop_kenney-interface-pluck-001.ogg", volume: 0.6, peakMs: 1 },
    { frame: 138, file: "sfx/whoosh_fs393811.ogg", volume: 0.6, peakMs: 36 },
    { frame: 160, file: "sfx/pop_kenney-interface-drop-001.ogg", volume: 0.45, peakMs: 0 },
    { frame: 172, file: "sfx/pop_kenney-interface-drop-002.ogg", volume: 0.45, peakMs: 0 },
    { frame: 186, file: "sfx/transition_fs-702773-swipe-wav.ogg", volume: 0.5, peakMs: 65 },
    { frame: 214, file: "sfx/pop_kenney-interface-pluck-002.ogg", volume: 0.45, peakMs: 1 },
  ],
};
