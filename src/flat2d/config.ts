// Flat 2D "Phillips Digital" film (v2). Grammar learned from a Malika Favre reference: flat vector, a 5-colour red palette,
// light as negative space, a seamless zoom through a portal. Story: a designer at their PC -> zoom into the screen ->
// a 3D motion world (flat-shaded) -> zoom back out to the designer -> the screen floods the frame -> Phillips Digital logo.
// Every word, colour, timing and anchor lives here, so a change is one line.
const fps = 30, bpm = 96;

export const flatConfig = {
  output: { width: 1920, height: 1080, fps, durationInFrames: 450 }, // 15 s
  music: { bpm },

  col: {
    red: "#D3131B", redDeep: "#A30E14", maroon: "#6B0A10", maroonDeep: "#4A070B",
    ink: "#170405", peach: "#F2A27E", cream: "#F6E6D0", lips: "#E52A2F",
  },

  // ONE continuous zoom, like the reference: logo -> (the dot of the p.) -> designer -> (her monitor) -> 3D world ->
  // (the red sun, which holds the logo) -> logo. The camera never stops; frame 449 flows into frame 0.
  t: {
    arrive: [0, 150, 272],        // frames where the logo, the designer and the 3D world each fill the frame at scale 1
    click: 165,                    // she clicks; the cube pops in on her screen
    pops: [205, 222, 240],         // octahedron, ring, sphere pop in (on the beats)
    cursor: { in: 232, grab: 250, drop: 296, out: 330 }, // her cursor drags the cube into place
    ball: [200, 420],              // the ball rides the keyframe curve
    revealDot: [1.25, 3.0],        // the designer fades into the dot as the logo zooms from x1.25 to x3 (dot is pure ink at rest)
  },

  screen: { x: 410, y: 240, w: 576, h: 324 }, // the monitor screen (exactly 16:9): the portal into the 3D world
  dot: { cx: 1038.65, cy: 452.3, r: 19.2 },     // the dot of the p. on the logo card: the portal into the designer's room
  sun: { cx: 1480, cy: 230, r: 150 },           // the sun in the 3D world: the portal back to the logo
  cardBg: "#D3131B",

  // 3D world camera: slow orbit across the whole film (radians), so the monitor and the full-screen view agree
  cam: { yaw: [-0.45, 0.5], pitch: 0.5, dist: 12, focal: 950, cx: 960, cy: 620, light: [-0.55, 0.75, -0.5] },

  // logo pieces (masks cut from inputs/phillips-digital-logo-scene.jpg), placed on a 1920x1080 card
  logo: {
    circle: { src: "flat2d/pd-circle.png", x: 785, y: 243, w: 352, h: 352, col: "#F6E6D0" },
    p: { src: "flat2d/pd-p-hd.png", x: 877, y: 366, w: 182, h: 170, col: "#170405" },
    word: { src: "flat2d/pd-word-hd.png", x: 565, y: 644, w: 793, h: 124, col: "#F6E6D0" },
    tag: { src: "flat2d/pd-tag-hd.png", x: 484, y: 830, w: 934, h: 25, col: "#F2A27E" },
  },
};
export type FlatConfig = typeof flatConfig;
