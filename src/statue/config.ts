// "Painted statue breaks apart": every colour, size, timing, light and camera value lives here.
// Scan: "Portrait of a Man" (marble, about 150 BC). Scan by Oliver Laric, threedscans.com
// (stated as free to use without copyright restrictions). Decimated to 80k triangles by
// scripts/decimate-stl.mjs into public/models/bearded-man.stl. Times in seconds (frame / fps).

export const statueConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInSeconds: 10 },
  model: "models/bearded-man.stl",

  statue: { height: 1.0, rotX: 0, rotY: Math.PI / 2 + 0.3, rotZ: Math.PI, plinth: { w: 0.86, h: 1.15, d: 0.86 } },

  colors: {
    background: "#0D0D10",
    floor: "#1C1B1E",
    marble: "#ECE8E1",
    vein: "#B9B4AD",
    plinth: "#E3DED6",
    paint: "#FF2E88", // hot pink, glossy
    rim: "#7FA7FF",
  },

  paint: {
    start: 0.6, // pour begins on the crown
    capDepth: 0.08, // how far the solid cap covers the crown
    speed: 0.5, // units/s the drip front travels at first
    slowdown: 0.75, // exponent < 1: drips slow as they run
    streaks: 11.0, // streak frequency around the statue
    floorReach: 3.6, // seconds: paint reaches the floor and starts pooling
    poolMax: 0.9, // final pool reach beyond the plinth edge
    poolGrow: 4.2, // seconds to reach most of poolMax
  },

  fracture: {
    pieces: 48,
    seed: "statue-01",
    cutFraction: 0.27,
    thickness: 0.05, // solid stone pieces (statue height = 1) // bottom share of the bust that stays on the plinth as a ruined stump
    crackStart: 4.4,
    crackGap: 0.012, // hairline separation while cracking
    breakStart: 4.9,
    breakEnd: 8.2, // last piece released
    gravity: 6.0, // units/s^2 (slow, weighty)
    landMin: 0.75, // landing distance from the plinth axis
    landMax: 1.9,
    bounce: 0.22,
    splatRadius: [0.07, 0.16] as [number, number],
  },

  light: {
    key: { position: [-2.2, 4.6, 2.6] as [number, number, number], intensity: 60, angle: 0.55, penumbra: 0.75 },
    rim: { position: [1.8, 3.2, -3.2] as [number, number, number], intensity: 26 },
    env: 0.18,
    bounce: 1.3, // pink floor bounce (GI look) at full pool size
    exposure: 1.0,
  },

  ao: { radius: 0.35, distanceFallOff: 1.0, thickness: 1.0, blend: 1.0 },

  camera: {
    fov: 26,
    from: { pos: [0.55, 1.75, 4.1] as [number, number, number], look: [0, 1.62, 0] as [number, number, number] },
    to: { pos: [1.35, 1.35, 5.6] as [number, number, number], look: [0.1, 1.0, 0] as [number, number, number] },
  },
};
