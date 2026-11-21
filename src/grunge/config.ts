// Graffiti Flip -> Phillips Digital. Every word, colour, font and timing lives here.
// Grammar from references/grunge-ref.mp4: 10 photocopy-grunge posters flipping every 16th note
// (4 frames at 112.5 BPM), same bold headline on each, one hand-drawn tag per poster.

export const P = {
  pink: "#E8318A",
  black: "#0B0B0B",
  white: "#F2F2F0",
  grey: "#BDBDBA",
};

export type Bg = "concrete" | "concreteDark" | "fence" | "black" | "pink" | "split";
export type Mark = "underline" | "scribble" | "star" | "arrow" | "circle" | "crown" | "zigzag" | "blob";

export type Poster = {
  bg: Bg;
  head: { ink: string; pos: "top" | "bottom" | "both" };
  tag?: { text: string; font: string; size: number; ink: string; rot: number; x: number; y: number; stroke?: number };
  marks?: { kind: Mark; x: number; y: number; w: number; h: number; ink: string; width?: number; rot?: number }[];
  seed: number;
};

export const graffitiConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 240 },
  bpm: 112.5, // 16th note = 4 frames exactly
  flipFrames: 4,
  flipsEnd: 160, // the poster loop runs until here, then the end card

  words: {
    headline: ["PHILLIPS", "DIGITAL"], // the exact words on every poster
    tag: "Phillips",
    corners: ["PHILLIPS DIGITAL®", "2026", "®", "{n}/10"], // {n} = poster number
  },
  fonts: {
    head: "Inter", headWeight: 800, headSize: 112, headLine: 0.9, headTracking: -0.02,
    corner: "Inter", cornerSize: 17,
    tagA: "SedgwickAveDisplay", tagB: "PermanentMarker", tagC: "RockSalt", tagD: "RubikWetPaint",
  },

  // x / y are offsets from the frame centre in px.
  posters: [
    { bg: "concrete", head: { ink: P.black, pos: "top" }, seed: 3,
      tag: { text: "Phillips", font: "SedgwickAveDisplay", size: 430, ink: P.black, rot: -7, x: 0, y: 90, stroke: 4 },
      marks: [{ kind: "underline", x: 40, y: 330, w: 820, h: 60, ink: P.black, width: 16 }] },
    { bg: "pink", head: { ink: P.black, pos: "top" }, seed: 5,
      tag: { text: "Phillips", font: "PermanentMarker", size: 330, ink: P.black, rot: -3, x: -40, y: 110 },
      marks: [{ kind: "crown", x: -420, y: -60, w: 190, h: 120, ink: P.black, width: 10, rot: -12 }, { kind: "star", x: 690, y: 300, w: 150, h: 150, ink: P.black, width: 9 }] },
    { bg: "fence", head: { ink: P.white, pos: "top" }, seed: 8,
      tag: { text: "Phillips", font: "RockSalt", size: 250, ink: P.white, rot: -4, x: 0, y: 120 },
      marks: [{ kind: "zigzag", x: 0, y: 360, w: 760, h: 40, ink: P.white, width: 10 }] },
    { bg: "black", head: { ink: P.white, pos: "both" }, seed: 11,
      marks: [{ kind: "blob", x: 0, y: 0, w: 900, h: 420, ink: P.white, width: 22 }, { kind: "circle", x: 0, y: 0, w: 120, h: 120, ink: P.pink, width: 8 }] },
    { bg: "black", head: { ink: P.pink, pos: "bottom" }, seed: 13,
      tag: { text: "PD", font: "RubikWetPaint", size: 560, ink: P.pink, rot: -9, x: -40, y: -110 },
      marks: [{ kind: "scribble", x: 560, y: -150, w: 260, h: 420, ink: P.pink, width: 14, rot: 8 }] },
    { bg: "pink", head: { ink: P.black, pos: "top" }, seed: 17,
      tag: { text: "Digital", font: "SedgwickAveDisplay", size: 400, ink: P.black, rot: 5, x: 20, y: 120, stroke: 3 },
      marks: [{ kind: "arrow", x: -640, y: 280, w: 260, h: 120, ink: P.black, width: 10, rot: -18 }] },
    { bg: "split", head: { ink: P.black, pos: "top" }, seed: 19,
      tag: { text: "PHILLIPS", font: "RubikWetPaint", size: 300, ink: P.black, rot: -2, x: 0, y: 110 },
      marks: [{ kind: "underline", x: -300, y: 380, w: 520, h: 40, ink: P.black, width: 26, rot: -8 }] },
    { bg: "concrete", head: { ink: P.black, pos: "top" }, seed: 23,
      tag: { text: "Phillips", font: "SedgwickAveDisplay", size: 470, ink: P.black, rot: -12, x: 30, y: 10, stroke: 6 },
      marks: [{ kind: "zigzag", x: 0, y: 330, w: 1100, h: 150, ink: P.black, width: 18 }] },
    { bg: "pink", head: { ink: P.black, pos: "bottom" }, seed: 29,
      tag: { text: "Phillips", font: "RockSalt", size: 270, ink: P.black, rot: -6, x: 0, y: -120 },
      marks: [{ kind: "star", x: -700, y: -330, w: 120, h: 120, ink: P.black, width: 8 }, { kind: "circle", x: 640, y: 200, w: 200, h: 140, ink: P.black, width: 8 }] },
    { bg: "concreteDark", head: { ink: P.white, pos: "top" }, seed: 31,
      tag: { text: "Digital", font: "PermanentMarker", size: 320, ink: P.white, rot: -5, x: 0, y: 120 },
      marks: [{ kind: "crown", x: 380, y: -40, w: 170, h: 110, ink: P.pink, width: 10, rot: 14 }] },
  ] as Poster[],

  // End card: pink, headline, the tag sprays on left to right, drips run, then hold.
  end: {
    bg: "pink" as Bg, seed: 41,
    headInk: P.black, headSize: 150, headY: 330, // headline centre offset (px below centre)
    tag: { text: "Phillips", font: "SedgwickAveDisplay", size: 520, ink: P.black, rot: -7, x: 0, y: -110, stroke: 5 },
    sprayStart: 162, sprayFrames: 32, sprayEdge: 6, // % width of the soft spray edge
    oversprayBlur: 14, oversprayOpacity: 0.28,
    drips: { start: 188, frames: 16, stagger: 2, list: [[-470, 120], [-170, 170], [40, 90], [260, 210], [500, 140]] as [number, number][] }, // drips: [x px from tag centre, length px]
    regAt: 204, // ® pops
  },

  grain: { opacity: 0.22 }, // photocopy grain over every frame

  audio: { mix: "grunge/mix.wav", volume: 1 },
};
