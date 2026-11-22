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
    { text: "COMING", at: 70, out: 126, x: 600, y: 600, size: 250, font: "PermanentMarker", rot: -4 },
    { text: "FOR THE", at: 130, out: 176, x: 560, y: 440, size: 210, font: "PermanentMarker", rot: -5 },
    { text: "KINGZ", at: 190, out: 999, x: 960, y: 880, size: 330, font: "RubikWetPaint", rot: -3 }, // solid, in front, all letters readable
    { text: "KINGZ", at: 190, out: 999, x: 960, y: 470, size: 600, font: "RubikWetPaint", rot: -3, behind: true, outlineOnly: true }, // giant outline behind her for depth
  ],
  ghost: { dx: 16, dy: 13, stroke: 4 }, // words with outlineOnly draw just this outline // outline copy behind each word (poster grammar)
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

  // v3 effects (user: "strobe effects, rgb glitches and inverted scenes").
  fx: {
    // Full-frame flashes; a pattern steps one colour per frame ("none" = no flash that frame).
    strobes: [
      { at: 9, pattern: ["white"] },
      { at: 59, pattern: ["yellow", "black", "white"] },
      { at: 126, pattern: ["white", "black", "yellow"] },
      { at: 170, pattern: ["black", "none", "white", "none", "yellow", "none", "black", "none", "white", "none", "yellow", "none", "white", "none", "black"] },
      { at: 190, pattern: ["white", "white"] },
    ] as { at: number; pattern: ("white" | "black" | "yellow" | "none")[] }[],
    // RGB channel split + sideways jolt: [start, length] in frames.
    rgb: [[30, 5], [68, 5], [100, 5], [138, 5], [188, 7], [214, 5], [231, 6]] as [number, number][],
    rgbAmount: 26, jolt: 34,
    // Inverted (negative) footage: [start, end) in frames. Graphics switch to black ink while inverted.
    invert: [[80, 100], [148, 166], [200, 204], [208, 212], [222, 226]] as [number, number][],
    sfx: "car/sfx/kenney-interface-glitch-002.ogg", sfxVolume: 0.6,
  },

  // v4 speed ramps (user: "slow motion and speeding up"): [output frame, playback speed]. Speed eases
  // linearly between keys; the map is scaled so the whole clip still plays in 241 output frames.
  // Words, effects and music stay on output frames (the beat); footage + matte layers follow the map.
  speedKeys: [[0, 1], [45, 1], [55, 2.2], [85, 2.2], [95, 0.45], [125, 0.45], [132, 1.6], [146, 1.6], [152, 0.38], [196, 0.38], [204, 1], [241, 1]] as [number, number][],

  audio: { music: "statue/music.wav", volume: 1 },
};

// Output frame -> source frame (float), from the speed keys.
export const timeMap = (() => {
  const keys = kingzConfig.speedKeys;
  const n = kingzConfig.output.durationInFrames;
  const speed = (o: number) => {
    for (let i = 0; i < keys.length - 1; i++) {
      const [a, sa] = keys[i];
      const [b, sb] = keys[i + 1];
      if (o >= a && o <= b) return sa + ((o - a) / (b - a)) * (sb - sa);
    }
    return 1;
  };
  const src = [0];
  for (let o = 1; o < n; o++) src.push(src[o - 1] + speed(o - 0.5));
  const k = (n - 1) / src[n - 1];
  return src.map((v) => v * k);
})();
