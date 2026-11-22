// Moving magazine cover (grammar from the user's "MUTANT" poster reference: acid lime field, black heavy italic
// masthead behind a chrome head, violet liquid-chrome growths, HUD brackets, coordinates, barcode, stars, orbit
// ellipse). Words are ours. Every word, colour, size and timing lives here.
// 0-6.2 s: close-ups of the growing spikes only (no type). The cover type builds only on the reveal (f150+).
// 3D layer: work/mutant/mutant.py (Blender, transparent PNGs) -> public/mutant/frames/f_0001.png ...

export const P = { lime: "#C8FA14", limeDeep: "#A6E200", ink: "#0A0A0A", violet: "#7A35FF", glitchA: "#FF2BD6", glitchB: "#00E5FF" };

export const mutantConfig = {
  output: { width: 1920, height: 1080, fps: 24, durationInFrames: 240 },
  frames: { dir: "mutant/frames/f_", pad: 4, first: 1 },
  grade3d: "saturate(1.35) contrast(1.08)", // pop like the reference
  // text glitches in (bursts as elements arrive), flickers in the hold, then glitches out at f222 and stays out
  glitch: { bursts: [[150, 6], [158, 10], [176, 5], [184, 4], [198, 7], [209, 3], [216, 3]] as [number, number][], out: 222, outDur: 8 },

  topBar: { left: "PHILLIPS DIGITAL®", centre: "ART / MOTION / IDENTITY", right: "EST. 2026", at: 150 },
  masthead: { text: "PHILLIPS DIGITAL", at: 158, stagger: 2, y: 64, width: 1790, maxSize: 470 },
  blade: { at: 172, dur: 10 }, // long black diagonal stroke off the masthead (poster grammar)

  coverLines: { lines: ["THE SKIN", "IS THE", "SCREEN"], at: 176, stagger: 5, x: 72, y: 372, size: 62 },
  globe: { at: 180, dur: 20, x: 72, y: 600, w: 190, h: 76 },
  specimen: { label: "SPECIMEN", number: "Nº 001", at: 184, x: 72, y: 704 },
  coords: { lat: 51.5072, lon: 0.1276, at: 186, dur: 20, x: 72, y: 838 },
  barcode: { at: 192, x: 72, y: 912, w: 170, h: 58 },
  stars: { at: 196, x: 72, y: 1000 },

  hud: { at: 152, x: 1760, y: 380 },
  counters: { items: ["001", "002", "003", "004"], at: 182, x: 1848, y: 790, every: 12 },

  title: { lines: ["BEYOND", "FLESH"], at: 198, x: 1130, y: 760, size: 128 },
  orbit: { at: 204, dur: 16 },
  sparkle: { at: 212 },
  footer: { lines: ["OBJECT", "IN MOTION"], at: 214, x: 1848, y: 1010 },
};
