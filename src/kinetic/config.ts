// Kinetic Symbols -> Phillips Digital Project. Every word, colour, size and timing lives here.
// Grammar measured frame by frame from references/kt-ref.mp4 (see notes/plan-kinetic-symbols.md):
// hard cuts every half-beat at ~115 BPM, one slow move inside each shot (drift, pan, zoom, weight
// morph), bursting 4s, rotating rings of 8s, a multiply shade darkening every frame toward the
// bottom, then words that each get their own trick, ending on beat-flashing colours with echoes.

const C = {
  blue: "#3346F2",
  pink: "#FBB8F2",
  cyan: "#0FA8E2",
  orange: "#FF5F0F",
  black: "#050505",
  grey: "#E4E4E6", // light-grey ink and background, shaded darker at the bottom
};

// A move happens across the whole shot: pan in px, zoom factor, weight morph (Inter 100-900).
export type Move = { pan?: [number, number]; zoom?: number; weight?: [number, number]; rot?: number };

export type Shot =
  | { kind: "glyph"; ch: string; bg: string; ink: string; size: number; x: number; y: number; weight?: number; move?: Move }
  | { kind: "wall"; ch: string; bg: string; ink: string; cell: number; size: number; weight: number }
  | { kind: "burst"; ch: string; bg: string; ink: string; size: number; count: number; stroke: number }
  | { kind: "rings"; ch: string; bg: string; ink: string; size: number; weight: number; spin: number };

export const kineticConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 270 },
  bpm: 115, // measured from the reference's cut rhythm: a cut every half-beat (~0.26 s)
  colors: C,

  // Multiply shade over every frame (the reference's darkening toward the bottom).
  shade: { from: 0.36, to: "#A6A6AC" },

  // 0-4.2 s: the count, one shot per half-beat, hard cuts.
  glyphFont: "Inter",
  glyphWeight: 600,
  shots: [
    { kind: "glyph", ch: "1", bg: C.pink, ink: C.black, size: 2100, x: 120, y: 240, weight: 700 },
    { kind: "wall", ch: "2", bg: C.cyan, ink: C.grey, cell: 175, size: 210, weight: 500 },
    { kind: "glyph", ch: "3", bg: C.grey, ink: C.black, size: 2000, x: -60, y: 150, weight: 500 },
    { kind: "burst", ch: "4", bg: C.blue, ink: C.grey, size: 300, count: 12, stroke: 9 },
    { kind: "glyph", ch: "5", bg: C.black, ink: C.orange, size: 2050, x: 40, y: 300, weight: 800 },
    { kind: "glyph", ch: "6", bg: C.black, ink: C.grey, size: 1700, x: 220, y: 300, move: { zoom: 1.25, weight: [200, 500] } },
    { kind: "glyph", ch: "7", bg: C.blue, ink: C.grey, size: 2100, x: 60, y: 220 },
    { kind: "rings", ch: "8", bg: C.cyan, ink: C.black, size: 150, weight: 600, spin: 1.1 },
    { kind: "glyph", ch: "9", bg: C.pink, ink: C.black, size: 2200, x: -80, y: 380, move: { pan: [-90, -70], rot: -3 } },
    { kind: "glyph", ch: "0", bg: C.grey, ink: C.black, size: 2100, x: 380, y: 120, move: { pan: [-260, 0], weight: [300, 900] } },
    { kind: "glyph", ch: "#", bg: C.grey, ink: C.black, size: 1900, x: 200, y: 80, move: { pan: [-420, 0] } },
    { kind: "glyph", ch: "@", bg: C.grey, ink: C.blue, size: 1900, x: 260, y: 260, move: { zoom: 1.08 } },
    { kind: "glyph", ch: "£", bg: C.cyan, ink: C.grey, size: 1900, x: 0, y: 140, move: { pan: [-300, 0] } },
    { kind: "glyph", ch: "%", bg: C.pink, ink: C.grey, size: 2000, x: 60, y: 160, move: { pan: [-200, -120] } },
    { kind: "glyph", ch: "&", bg: C.grey, ink: C.black, size: 1900, x: -120, y: 120, weight: 400 },
    { kind: "glyph", ch: "€", bg: C.black, ink: C.grey, size: 1900, x: 200, y: 100, move: { weight: [100, 700] } },
  ] as Shot[],

  // The name: each word gets the trick of one reference word. Lengths are in half-beats.
  name: {
    phillips: {
      text: "Phillips", halfBeats: 3, bg: C.black, ink: C.grey,
      font: "Montserrat", weight: 500, size: 230,
      blackFrames: 2, letterGap: 1.5,
      assembleAt: 12, assembleFrames: 8,
      scatter: { x: 520, y: 280, sizeMin: 0.8, sizeMax: 2.2 },
      // Like the reference's "Machine", letters settle at playful heights and sizes.
      rest: { y: 0.14, sizeMin: 0.8, sizeMax: 1.2 },
    },
    digital: {
      text: "Digital", halfBeats: 3, bg: C.pink, ink: C.black,
      font: "Inter", size: 168, rows: 5, lineHeight: 1.04,
      swellSpeed: 0.42, rowPhase: 1.15, // smooth weight swell 100-900, offset row by row
    },
    project: {
      text: "Project", halfBeats: 2, bg: C.black, ink: C.grey,
      font: "Montserrat", weight: 900, size: 250,
      framesPerLetter: 2, letterEnter: 4,
    },
    lockup: {
      // Each word keeps the style it was introduced in.
      lines: [
        { text: "Phillips", font: "Montserrat", weight: 500, italic: false, size: 205 },
        { text: "Digital", font: "Inter", weight: 900, italic: false, size: 205 },
        { text: "Project", font: "Montserrat", weight: 900, italic: true, size: 205 },
      ],
      lineHeight: 1.0,
      // "Gosh" grammar: the colours flash on every half-beat, echo copies sit behind, then it lands.
      flashes: [
        { bg: C.black, ink: C.grey, echo: C.grey },
        { bg: C.blue, ink: C.grey, echo: C.grey },
        { bg: C.pink, ink: C.black, echo: C.black },
        { bg: C.orange, ink: C.grey, echo: C.grey },
      ],
      final: { bg: C.grey, ink: C.black },
      echo: { copies: 3, step: [24, 22], stroke: 16 }, // solid stacked copies, separated by a background-colour outline
      settleFrames: 6,
    },
  },

  audio: {
    beat: "kinetic/beat.wav", beatVolume: 0.9,
    landSfx: "sfx/kit_impact.ogg", landVolume: 0.5,
  },
};

export const halfBeat = (i: number) => Math.round((i * 30 * 60) / kineticConfig.bpm / 2);
