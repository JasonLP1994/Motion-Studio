// Flat 2D "Phillips Digital" film (v5): ONE continuous zoom, seamless loop, red Favre-style palette.
// logo -> (the dot of the p.) -> a busy street: a man waits, crosses on the zebra and walks into the agency ->
// (the agency's glass shopfront) -> inside: he walks to the big wall screen -> (the screen shows the logo) -> logo.
// Every word, colour, timing and anchor lives here, so a change is one line.
export const flatConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 450 }, // 15 s, frame 449 flows into frame 0
  music: { bpm: 96 },

  col: {
    // v6 palette: cyberpunk mecha comic (grammar from the user's yellow robot poster): yellow ground, hot magenta,
    // teal / navy, lavender chrome, purple accents, heavy navy ink outlines. Token names kept so each role stays put.
    red: "#FFE01A", redDeep: "#FF2D95", maroon: "#2C8FB0", maroonDeep: "#1E2B57",
    ink: "#121733", peach: "#B9BCD6", cream: "#F4F1FF", lips: "#8A3CF0",
    yellowDeep: "#E9B400", tealDeep: "#1C6A8A", pinkDeep: "#C9157A", outline: 3,
    skin: "#FFD5BC", skinShade: "#F0A88E", glow: "#FFF6C8",
  },

  t: {
    arrive: [0, 125, 300],      // frames where the logo, the street and the agency interior each fill the frame at scale 1
    ease0: [40, 0.07],          // gentle start: by frame 40 only 7% of the logo zoom has happened, so the logo stays readable
    wave: { designer: [292, 346], man: [378, 436] }, // the right-hand designer waves as he walks in; he waves back at the screen
    revealDot: [1.25, 3.0],     // the street fades into the dot as the logo zooms from x1.25 to x3 (the dot is pure ink at rest)
    walkSignal: 146,            // the crossing light turns to "walk"
    walk: [150, 262],           // he crosses the street and reaches the glass door
    doorOpen: [244, 258],       // the glass door swings open as he arrives
    inside: [262, 372],         // he walks away from us towards the big screen, then stands and looks at it
  },

  // street geometry
  street: {
    window: { x: 700, y: 290, w: 480, h: 270 },  // the glass shopfront (exactly 16:9): portal into the interior
    door: { x: 1066, y: 330, w: 100, h: 230 },   // the glass door, inside the shopfront (on the man's path)
    farWalk: 560, road: [640, 930],               // far pavement top, road top / bottom
    lanes: { far: 762, near: 902 },               // car baselines
    manFrom: { x: 1250, y: 1062, s: 1 }, manTo: { x: 1116, y: 562, s: 0.45 }, // feet position + scale
    // cars: [start x, colour, length]; near lane drives right at 16 px/frame, far lane left at 13 px/frame,
    // scheduled so the zebra (x 1000-1400) is clear while he crosses each lane
    near: [[200, "peach", 280], [-1160, "cream", 290], [-2560, "ink", 270], [-3500, "peach", 300]] as [number, string, number][],
    far: [[2300, "ink", 240], [3400, "peach", 230], [4460, "cream", 250], [5600, "ink", 230]] as [number, string, number][],
    vNear: 16, vFar: 13,
  },

  // interior geometry
  inside: {
    screen: { x: 720, y: 200, w: 480, h: 270 }, // the big wall screen (16:9): portal back to the logo
    manTo: { x: 1010, y: 770, s: 0.55 },        // where he stops, below the screen
  },

  dot: { cx: 1038.65, cy: 452.3, r: 19.2 },     // the dot of the p. on the logo card: portal into the street
  cardBg: "#FFE01A",

  // logo pieces (masks cut from inputs/phillips-digital-logo-scene.jpg), placed on a 1920x1080 card
  logo: {
    circle: { src: "flat2d/pd-circle.png", x: 785, y: 243, w: 352, h: 352, col: "#FF2D95" },
    p: { src: "flat2d/pd-p-hd.png", x: 877, y: 366, w: 182, h: 170, col: "#121733" },
    word: { src: "flat2d/pd-word-hd.png", x: 565, y: 644, w: 793, h: 124, col: "#121733" },
    tag: { src: "flat2d/pd-tag-hd.png", x: 484, y: 830, w: 934, h: 25, col: "#C9157A" },
  },
};
export type FlatConfig = typeof flatConfig;
