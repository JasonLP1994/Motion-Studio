// Moving magazine cover (grammar from the user's "MUTANT" poster reference: acid lime field, black heavy italic
// masthead behind a chrome head, violet liquid-chrome growths, HUD brackets, coordinates, barcode, stars, orbit
// ellipse). Words are ours. Every word, colour, size and timing lives here.
// 3D layer: work/mutant/mutant.py (Blender, transparent PNGs) -> public/mutant/frames/f_0001.png ...

export const P = { lime: "#C9F23C", limeDeep: "#B4DE22", ink: "#0A0A0A", violet: "#7A35FF" };

export const mutantConfig = {
  output: { width: 1920, height: 1080, fps: 24, durationInFrames: 240 },
  frames: { dir: "mutant/frames/f_", pad: 4, first: 1 },

  topBar: { left: "PHILLIPS DIGITAL®", centre: "ART / MOTION / IDENTITY", right: "EST. 2026", at: 2 },
  masthead: { text: "PHILLIPS DIGITAL", at: 16, stagger: 2, y: 64, width: 1800, maxSize: 330 },
  blade: { at: 34, dur: 10 }, // long black diagonal stroke off the masthead (poster grammar)

  coverLines: { lines: ["THE SKIN", "IS THE", "SCREEN"], at: 46, stagger: 5, x: 72, y: 372, size: 62 },
  globe: { at: 62, dur: 22, x: 72, y: 600, w: 190, h: 76 },
  specimen: { label: "SPECIMEN", number: "Nº 001", at: 72, x: 72, y: 704 },
  coords: { lat: 51.5072, lon: 0.1276, at: 84, dur: 26, x: 72, y: 838 },
  barcode: { at: 96, x: 72, y: 912, w: 170, h: 58 },
  stars: { at: 104, x: 72, y: 1000 },

  hud: { at: 6, x: 1760, y: 380 },
  counters: { items: ["001", "002", "003", "004"], at: 76, x: 1848, y: 790, every: 12 },

  title: { lines: ["BEYOND", "FLESH"], at: 132, x: 1130, y: 760, size: 128 },
  orbit: { at: 140, dur: 18 },
  sparkle: { at: 152 },
  footer: { lines: ["OBJECT", "IN MOTION"], at: 162, x: 1848, y: 1010 },
};
