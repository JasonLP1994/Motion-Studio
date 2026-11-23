// Ruby pendant film: Blender Cycles 3D (frames 1-378) + the Rubyred logo ending. Every word, colour and timing here.
// Ending grammar from references/jewelry/mutant-cover-ref-v1.mp4: bold condensed headline slams in with an RGB-split glitch,
// the 3D form turns into a flat two-tone stencil logo, hard colour flicker, then the emblem + wordmark. Logo built from our
// own pendant render (scripts/logo/two_tone.py). 100 BPM: beat = 18 frames.
export const rubyConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 450 },
  frames: { dir: "ruby/frames", last3d: 378, pad: 4 },        // public/ruby/frames/f_0001.png ... (upscaled 1080p 3D frames)
  word: "RUBYRED",
  font: { file: "fonts/anton-latin-400-normal.woff2", family: "RubyAnton" },
  colors: { red: "#C8102E", white: "#FFFFFF", black: "#000000", cyan: "#00E5FF" },
  title: { in: 343, size: 300, y: 190, tracking: 6, slam: 1.14, glitchFrames: 10, color: "red" },   // red: the set is off-white now
  // 3D -> stencil -> flicker (2 frames per state): [background, light shapes, dark shapes, which art]
  flickerStart: 379, flickerStep: 2,
  flicker: [
    ["black", "white", "black", "endpose"], ["white", "black", "white", "endpose"], ["red", "white", "red", "endpose"],
    ["black", "white", "black", "endpose"], ["white", "white", "red", "logo"], ["red", "red", "white", "logo"],
    ["black", "black", "white", "logo"], ["white", "white", "red", "logo"], ["red", "red", "white", "logo"],
  ],
  logo: { file: "ruby/logo", w: 900, h: 1170, startH: 700, startY: 610, endH: 560, endY: 400, settle: 24 },
  wordmark: { in: 405, size: 150, y: 820, tracking: 26, rise: 40 },
};
export type RubyColor = keyof typeof rubyConfig.colors;
