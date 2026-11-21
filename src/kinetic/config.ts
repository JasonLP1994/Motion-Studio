// Kinetic Symbols -> Phillips English. Every word, colour, size and timing lives here.
// Grammar from references/kt-ref.mp4 (giant cropped glyphs, colour->grey fields, quarter-second cuts).
import pieces from "../../public/logo/pieces.json";

const C = {
  blue: "#3346F2",
  pink: "#FBB8F2",
  cyan: "#12A6DE",
  orange: "#FF5F0F",
  black: "#0A0A0A",
  grey: "#E6E6E8",
  white: "#F4F4F5",
  navy: "#0F161E", // logo file background
  teal: "#82BCC7", // logo accent
};

export type Enter = "scale" | "slideL" | "slideR" | "slideU" | "rot";

export const kineticConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 240 },
  bpm: 120, // 15 frames per beat, 7.5 per eighth (always computed from the index, then rounded)
  colors: C,
  font: "Inter",
  // Background = colour on top fading to grey at the bottom (fadeStart..100%), like the reference.
  fadeStart: 0.42,

  // 0.0-1.5 s: giant glyphs, one per eighth. x/y = glyph centre offset from frame centre (px), size in px.
  glyphs: [
    { ch: "7", bg: C.blue, fade: true, ink: C.grey, size: 1650, x: 120, y: 60, rot: 0, enter: "scale" as Enter },
    { ch: "#", bg: C.grey, fade: false, ink: C.black, size: 1500, x: -260, y: 40, rot: 0, enter: "slideR" as Enter },
    { ch: "@", bg: C.grey, fade: false, ink: C.blue, size: 1550, x: 300, y: -30, rot: -8, enter: "rot" as Enter },
    { ch: "&", bg: C.orange, fade: true, ink: C.black, size: 1500, x: -180, y: 30, rot: 0, enter: "slideU" as Enter },
    { ch: "9", bg: C.pink, fade: true, ink: C.black, size: 1750, x: 380, y: 140, rot: 0, enter: "slideL" as Enter },
    { ch: "?", bg: C.black, fade: false, ink: C.white, size: 1600, x: -340, y: 20, rot: 6, enter: "rot" as Enter },
  ],
  glyphEnterFrames: 6,

  // 1.5-2.5 s: wall of outlined glyphs.
  wall1: { ch: "8", bg: C.cyan, ink: C.black, cell: 300, fontSize: 330, stroke: 12, flipAtFrame: 15, speed: [3.2, 1.6] },
  // 2.5-3.5 s: rows alternating thin/heavy, shifting one row per eighth.
  stack: { rows: ["#&@%?!*", "&@%?!*#", "@%?!*#&", "%?!*#&@", "?!*#&@%", "!*#&@%?"], bg: C.black, ink: C.white, fontSize: 172, lineHeight: 1.0, tracking: 0.14, weights: [300, 900] },
  // 3.5-4.0 s: sliced glyphs (3 bands slide in from alternating sides and lock).
  slices: [
    { ch: "%", bg: C.orange, fade: true, ink: C.black, size: 1500, x: 60, y: 30, offsets: [-520, 640, -380] },
    { ch: "§", bg: C.pink, fade: true, ink: C.black, size: 1450, x: -40, y: 20, offsets: [600, -480, 420] },
  ],
  sliceEnterFrames: 6,
  // 4.0-4.5 s: wall of spinning asterisks.
  wall2: { ch: "*", bg: C.blue, ink: C.white, cell: 280, fontSize: 440, spinPerBeat: 90 },

  // Section starts in eighths (7.5 frames each).
  sections: { glyphs: 0, wall1: 6, stack: 10, slices: 14, wall2: 16, p: 18, e: 19, pull: 20 },

  // 4.5 s on: the real logo (public/logo pieces, positions in logo-file px).
  logo: {
    pieces: pieces.pieces,
    box: { x0: 294, y0: 272, x1: 968, y1: 1005 },
    heightOnScreen: 640,
    zoomOnGlyph: 3.4, // camera zoom while the giant P / E fill the frame
    pullFrames: 18,
    barStart: 160, barFrames: 9,
    // Letter columns measured from the PNG alpha (px inside each wordmark PNG).
    phillipsCols: [[8, 96], [111, 205], [223, 252], [269, 344], [354, 428], [442, 470], [486, 573], [580, 666]],
    englishCols: [[8, 83], [98, 187], [199, 291], [305, 371], [383, 408], [417, 497], [507, 591]],
    lettersStart: 162, // PHILLIPS
    englishDelay: 5,
    letterStagger: 1.5,
    letterFrames: 11,
    scatter: { x: 520, y: 300, rot: 50, scaleMin: 0.5, scaleMax: 1.9 },
  },

  motionBlur: { shutterAngle: 180, samples: 8 },

  audio: {
    beat: "kinetic/beat.wav", beatVolume: 0.9,
    sfx: [
      { frame: 149, file: "sfx/kit_whoosh.ogg", volume: 0.7 },
      { frame: 186, file: "sfx/kit_impact.ogg", volume: 0.9 },
    ],
  },
};

export const eighth = (i: number) => Math.round((i * 15) / 2);
