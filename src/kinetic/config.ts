// Kinetic Symbols -> Phillips Digital Project. Every word, colour, size and timing lives here.
// Grammar from references/kt-ref.mp4: a count of giant cropped glyphs on a sideways-pushing strip,
// rotated-glyph walls, a multiply shade darkening every frame toward the bottom, then words that
// each get their own trick (scatter, weight pulse, heavy-italic typing).

const C = {
  blue: "#3346F2",
  pink: "#FBB8F2",
  cyan: "#0FA8E2",
  orange: "#FF5F0F",
  black: "#050505",
  grey: "#E4E4E6", // light-grey ink and background, shaded darker at the bottom
};

export type Panel =
  | { kind: "glyph"; ch: string; bg: string; ink: string; size: number; x: number; y: number; weight?: number }
  | { kind: "wall"; ch: string; bg: string; ink: string; cell: number; size: number; weight: number }
  | { kind: "scatter"; ch: string; bg: string; ink: string; size: number; count: number; stroke: number };

export const kineticConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 240 },
  bpm: 120, // 15 frames a beat; the strip moves on every eighth (7.5 f, rounded from the index)
  colors: C,

  // Multiply shade over every frame (the reference's darkening toward the bottom).
  shade: { from: 0.36, to: "#A6A6AC" },

  // 0-4 s: the strip. One panel per eighth; the camera whips sideways into each one.
  whipFrames: 4, // frames per sideways push (centred on the beat)
  glyphFont: "Inter",
  panels: [
    { kind: "glyph", ch: "1", bg: C.pink, ink: C.black, size: 2100, x: 120, y: 240 },
    { kind: "wall", ch: "2", bg: C.cyan, ink: C.grey, cell: 175, size: 210, weight: 500 },
    { kind: "glyph", ch: "3", bg: C.grey, ink: C.black, size: 2000, x: -60, y: 150 },
    { kind: "scatter", ch: "4", bg: C.blue, ink: C.grey, size: 300, count: 9, stroke: 9 },
    { kind: "glyph", ch: "5", bg: C.black, ink: C.orange, size: 2050, x: 40, y: 300 },
    { kind: "glyph", ch: "6", bg: C.black, ink: C.grey, size: 2000, x: 220, y: 330, weight: 400 },
    { kind: "glyph", ch: "7", bg: C.blue, ink: C.grey, size: 2100, x: 60, y: 220 },
    { kind: "wall", ch: "8", bg: C.cyan, ink: C.black, cell: 165, size: 200, weight: 600 },
    { kind: "glyph", ch: "9", bg: C.pink, ink: C.black, size: 2200, x: -80, y: 380 },
    { kind: "glyph", ch: "0", bg: C.grey, ink: C.black, size: 2100, x: 300, y: 120 },
    { kind: "glyph", ch: "#", bg: C.black, ink: C.grey, size: 1900, x: -40, y: 80 },
    { kind: "glyph", ch: "@", bg: C.grey, ink: C.blue, size: 1900, x: 260, y: 260 },
    { kind: "glyph", ch: "£", bg: C.cyan, ink: C.grey, size: 1900, x: -200, y: 140 },
    { kind: "glyph", ch: "%", bg: C.pink, ink: C.grey, size: 2000, x: 160, y: 120 },
    { kind: "glyph", ch: "&", bg: C.grey, ink: C.black, size: 1900, x: -120, y: 120, weight: 500 },
    { kind: "glyph", ch: "€", bg: C.black, ink: C.grey, size: 1900, x: 200, y: 100 },
  ] as Panel[],
  glyphWeight: 600,
  glyphPush: 0.07, // slow scale push across each panel's life

  // 4 s on: the name, each word with its own trick. Frames are absolute.
  name: {
    phillips: {
      text: "Phillips", start: 120, end: 150, bg: C.black, ink: C.grey,
      font: "Montserrat", weight: 500, size: 230,
      blackFrames: 3, // a beat of black before letters arrive (the reference's interstitials)
      letterGap: 1.5, // frames between letters popping in (random order)
      assembleAt: 19, assembleFrames: 9, // local frames: scattered letters fly into one line
      scatter: { x: 520, y: 280, sizeMin: 0.8, sizeMax: 2.2 },
    },
    digital: {
      text: "Digital", start: 150, end: 180, bg: C.pink, ink: C.black,
      font: "Inter", size: 168, rows: 5, lineHeight: 1.04,
      weights: [300, 500, 700, 900, 700, 500], stepFrames: 4, // each row's weight steps every 4 f
    },
    project: {
      text: "Project", start: 180, end: 199, bg: C.black, ink: C.grey,
      font: "Montserrat", weight: 900, italic: true, size: 250,
      framesPerLetter: 2, letterEnter: 4,
    },
    lockup: {
      start: 199, bg: C.grey, ink: C.black,
      // Each word keeps the style it was introduced in.
      lines: [
        { text: "Phillips", font: "Montserrat", weight: 500, italic: false, size: 205 },
        { text: "Digital", font: "Inter", weight: 900, italic: false, size: 205 },
        { text: "Project", font: "Montserrat", weight: 900, italic: true, size: 205 },
      ],
      lineHeight: 1.0,
      lineStagger: 2, enterFrames: 8, enterFrom: 1100, // lines push in from the right like the strip
    },
  },

  audio: {
    beat: "kinetic/beat.wav", beatVolume: 0.9,
    sfx: [
      { frame: 197, file: "sfx/kit_whoosh.ogg", volume: 0.6 },
      { frame: 210, file: "sfx/kit_impact.ogg", volume: 0.85 },
    ],
  },
};

export const eighth = (i: number) => Math.round((i * 15) / 2);
