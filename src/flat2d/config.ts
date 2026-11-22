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

  // Infinite loop: frame 449 flows into frame 0, and the logo is both the start and the end.
  t: {
    push: 1.06,                       // slow push towards the screen while holding
    logoOut: beat(2),                 // 38: the logo steps away
    unflood: [beat(2) + 8, beat(3) + 6],   // 46 -> 62: the deep red shrinks back into the monitor, revealing the designer
    boot: beat(4),                    // 75: the 3D app wakes on her screen (sun + grid)
    click: beat(5),                   // 94: she clicks and the cube pops in
    zoomIn: [beat(6), beat(8)],       // 113 -> 150: into the monitor, lands on the bar
    pops: [beat(8), beat(9), beat(10)],    // octahedron, ring, sphere pop in on the beats
    cursor: { in: beat(9), grab: beat(10), drop: beat(12), out: beat(13) }, // her cursor drags the cube into place
    ball: [beat(8), beat(15)],        // the ball rides the keyframe curve
    zoomOut: [beat(14), beat(16)],    // 263 -> 300: back out to the designer, lands on the bar
    flood: [beat(19), beat(19) + 14], // 356: the screen's deep red floods the frame
    logo: { circle: beat(19) + 12, p: beat(19) + 20, word: beat(20) + 10, tag: beat(21) + 4 }, // then holds through the loop point
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
