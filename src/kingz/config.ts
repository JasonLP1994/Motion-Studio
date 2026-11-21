// KINGZ: rotoscoped statue x streetwear graffiti. Every word, colour, font and timing lives here.
// Footage: inputs/statue-cathedral.mp4 (Vecteezy stock) -> public/statue/clip.mp4 (1080p working copy).
// Rotoscope (SAM 2) -> public/statue/cut (statue cut-out), public/statue/ring (outline), src/kingz/track.json.
// Grammar (not content) from the user's references: neon hand-drawn outline + crown/X-eyes/smile doodles,
// streetwear poster (angular brush type with outline ghost, caution tape, barcodes, XXX, chevrons), node tags.

export const P = { yellow: "#FFE600", black: "#070707", white: "#F4F4F2" };

export const kingzConfig = {
  output: { width: 1920, height: 1080, fps: 24, durationInFrames: 241 }, // matches the clip frame-for-frame
  bpm: 144, // 10 frames a beat at 24 fps
  grade: "grayscale(1) contrast(1.35) brightness(0.92)",

  // The saying (user's exact words), one slam per beat.
  words: [
    { text: "ARE", at: 10, out: 60, x: 330, y: 330, size: 230, font: "PermanentMarker", rot: -6 },
    { text: "YOU", at: 20, out: 60, x: 380, y: 560, size: 230, font: "PermanentMarker", rot: -3 },
    { text: "COMING", at: 70, out: 126, x: 960, y: 520, size: 300, font: "PermanentMarker", rot: -4, behind: true },
    { text: "FOR THE", at: 130, out: 176, x: 470, y: 440, size: 210, font: "PermanentMarker", rot: -5 },
    { text: "KINGZ", at: 190, out: 999, x: 960, y: 520, size: 520, font: "RubikWetPaint", rot: -3, behind: true },
  ],
  ghost: { dx: 16, dy: 13, stroke: 4 }, // outline copy behind each word (poster grammar)
  slamFrames: 4,
  shake: { frames: 5, px: 16 },

  tape: {
    text: "ARE YOU COMING FOR THE KINGZ  •  ",
    bands: [
      { at: 40, out: 76, y: 760, rot: -7, speed: 9 },
      { at: 140, out: 178, y: 300, rot: 6, speed: -11 },
    ],
    height: 74, fontSize: 52, wipe: 5,
  },

  outline: { drawFrames: 20, boilEvery: 3, wobble: 7, shadow: [11, 9] as [number, number] },

  nodes: { at: 80, out: 152, every: 4, wireFrames: 7, labels: ["NODE_1", "NODE_2", "NODE_3", "NODE_4", "NODE_5"] },

  face: { at: 178, every: 4, drawFrames: 6, stroke: 0.04 }, // stroke as a share of face width

  poster: {
    barcodesAt: 4, chevronsAt: 8, xAt: [130, 140, 150],
    code: ["KNGZ-001  //  ROTO 241F", "JN47B5WBGC  0x3F", "SAM2.1  CONF 0.98"],
  },

  audio: { music: "statue/music.wav", volume: 1 },
};
