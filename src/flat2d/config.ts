// Flat 2D endless-zoom portrait (grammar learned from a Malika Favre reference: flat vector, 5-colour palette,
// negative-space light, a seamless zoom through a reflection -> building -> window -> face). All scenes are original.
// Every word, colour, timing and anchor lives here, so a change is one line.
export const flatConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 450 }, // 15 s, loops: frame 450 = frame 0
  music: { bpm: 96 }, // 1 bar = 75 frames; every zoom lands on a bar line (150, 300, 450)

  col: {
    red: "#D3131B",      // ground
    redDeep: "#A30E14",  // shadow bands
    maroon: "#6B0A10",   // skin in shadow
    maroonDeep: "#4A070B",
    ink: "#170405",      // hair, frames, deepest shadow
    peach: "#F2A27E",    // facade, pattern lines
    cream: "#F6E6D0",    // light (negative space), sun, glints
    lips: "#E52A2F",
    window: "#BE1119",
  },

  // timeline (frames): hold, then a 45-frame zoom that lands on the bar
  t: {
    zoom: 45,
    push: 1.08, // slow push towards the next portal while holding
    A: [0, 150], B: [150, 300], C: [300, 450],
    glint: [52, 78],        // light sweep across the sunglasses
    birds: [168, 250],      // birds cross the dusk sky
    lights: [170, 186, 205, 224, 243], // hotel windows switch on (on the beats)
    glass: [318, 352],      // she raises her glass
    title: { in: 322, out: 392 },
    dissolve: 0.45,         // C->A: A fades in over the last 45% of the zoom
  },

  // portals (in their scene's own 1920x1080 coordinates)
  lensNear: { cx: 1215, cy: 478, rx: 112, ry: 80 }, // portal A->B
  lensFar: { cx: 992, cy: 478, rx: 90, ry: 72 },
  window: { x: 924, y: 562, w: 144, h: 81 },          // portal B->C, exactly 16:9
  head: { x: 1150, y: 340, s: 0.33 },                 // where scene A's head sits inside scene C (portal C->A)

  title: { text: "TITLE HERE", sub: "", font: "Cinzel", size: 92, x: 150, y: 470, color: "#F6E6D0" },
};
export type FlatConfig = typeof flatConfig;
