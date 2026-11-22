// Flat 2D "Phillips Digital" film (v2). Grammar learned from a Malika Favre reference: flat vector, a 5-colour red palette,
// light as negative space, a seamless zoom through a portal. Story: a designer at their PC -> zoom into the screen ->
// a 3D motion world (flat-shaded) -> zoom back out to the designer -> the screen floods the frame -> Phillips Digital logo.
// Every word, colour, timing and anchor lives here, so a change is one line.
const fps = 30, bpm = 96;
const beat = (n: number) => Math.round((n * fps * 60) / bpm); // frame of beat n (never accumulate rounded beats)

export const flatConfig = {
  output: { width: 1920, height: 1080, fps, durationInFrames: 450 }, // 15 s
  music: { bpm },

  col: {
    red: "#D3131B", redDeep: "#A30E14", maroon: "#6B0A10", maroonDeep: "#4A070B",
    ink: "#170405", peach: "#F2A27E", cream: "#F6E6D0", lips: "#E52A2F",
  },

  t: {
    push: 1.06,                       // slow push towards the screen while holding
    zoomIn: [beat(4), beat(6)],       // 75 -> 113: into the monitor, lands on beat 6
    zoomOut: [beat(14), beat(16)],    // 263 -> 300: back out to the designer, lands on the bar
    click: beat(3),                   // she clicks the mouse (the cue that starts the zoom)
    cursor: { in: beat(7), grab: beat(8), drop: beat(10), out: beat(12) }, // her cursor drags the cube into place
    pops: [beat(6), beat(7), beat(8)],     // octahedron, ring, sphere pop in on the beats
    flood: [beat(18), beat(18) + 14],      // 338: the screen's red floods the frame
    logo: { circle: beat(18) + 12, p: beat(18) + 20, word: beat(19) + 10, tag: beat(20) + 6 },
  },

  screen: { x: 410, y: 240, w: 576, h: 324 }, // the monitor screen (exactly 16:9): the portal into the 3D world

  // 3D world camera: slow orbit across the whole film (radians), so the monitor and the full-screen view agree
  cam: { yaw: [-0.45, 0.5], pitch: 0.5, dist: 12, focal: 950, cx: 960, cy: 620, light: [-0.55, 0.75, -0.5] },

  // logo pieces (masks cut from inputs/phillips-digital-logo-scene.jpg), placed on a 1920x1080 card
  logo: {
    circle: { src: "flat2d/pd-circle.png", x: 785, y: 243, w: 352, h: 352, col: "#F6E6D0" },
    p: { src: "flat2d/pd-p.png", x: 877, y: 366, w: 182, h: 170, col: "#170405" },
    word: { src: "flat2d/pd-word.png", x: 565, y: 644, w: 793, h: 124, col: "#F6E6D0" },
    tag: { src: "flat2d/pd-tag.png", x: 484, y: 830, w: 934, h: 25, col: "#F2A27E" },
  },
};
export type FlatConfig = typeof flatConfig;
