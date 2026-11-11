// "Painted statue breaks apart" (cinematic v2): every colour, size, timing, light and camera value.
// Scan: "Portrait of a Man" (marble, about 150 BC). Scan by Oliver Laric, threedscans.com
// (stated as free to use without copyright restrictions). Decimated to 80k triangles by
// scripts/decimate-stl.mjs into public/models/bearded-man.stl. Times in seconds (frame / fps).

export const statueConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInSeconds: 10 },
  model: "models/bearded-man-200k.stl", // higher detail for macro shots

  statue: { height: 1.0, rotX: 0, rotY: Math.PI / 2 + 0.3, rotZ: Math.PI, plinth: { show: false, w: 0.52, h: 0, d: 0.46, bevel: 0.02 } }, // no plinth: the head stands on the floor (w/d = base footprint for the pool)

  colors: {
    background: "#0E0204", // deepest maroon (frame edges, below the horizon)
    fog: "#1C0407", // horizon + fog colour: the floor melts into this (infinite cove)
    haze: "#7A1A22", // glowing red haze behind the top light
    hazeHot: "#E89A9A", // hot pink core of the top light
    floor: "#160406", // dark maroon floor, close to the fog colour so it melts away
    marble: "#EDE6DA",
    vein: "#B6B0A8",
    plinth: "#E6E1D9",
    paint: "#7A0710", // deep crimson, thick and wet (Daredevil-intro grammar)
    crack: "#C0141E", // red liquid seeping into the cracks
    key: "#FFC2BC", // pinkish top light (Daredevil titles)
    rimA: "#FFB070", // warm amber rim, back left
    rimB: "#C4141C", // deep red rim, back right
  },

  // Story beats
  t: {
    lightsOn: [0.1, 1.4] as [number, number], // key light + beam fade in
    paintStart: 0.3,
    crackStart: 5.2,
    boom: 6.6,
    slowEnd: 9.0, // long, elegant slow motion between the break and here
    rampEnd: 9.6, // back to real speed by here
  },
  slowMo: 0.3, // playback rate during slow motion

  paint: {
    capDepth: 0.1,
    speed: 0.34,
    slowdown: 0.88,
    streaks: 8.0,
    thickness: 0.014, // painted surfaces are raised (thick, viscous liquid)
    floorReach: 3.6,
    poolMax: 0.8,
    poolGrow: 4.5,
    drops: 22, // falling paint drops
  },

  fracture: {
    pieces: 48,
    seed: "statue-01",
    cutFraction: 0.27,
    thickness: 0.05,
    crackWidth: 0.018, // glowing crack half-width at full spread
    tremor: 0.0025,
    explodeSpeed: [0.0, 0.12] as [number, number], // upward kick range at the boom
    gravity: 6.0,
    landMin: 0.35,
    landMax: 1.05,
    bounce: 0.2,
    splatRadius: [0.07, 0.17] as [number, number],
  },

  crackGlow: 0.12, // max emissive in the cracks (subtle: liquid seeping in, not lava)
  desaturate: 0.65,
  redTint: 0.7, // grade: blend toward a red monochrome ramp (maroon shadows, pink highlights)
  cove: { radius: 18, fogDensity: 0.16, floorFadeStart: 1.1, floorFadeEnd: 3.4, hazeDir: [0.0, 0.8, -1.0] as [number, number, number], hazeSize: 0.3 }, // grade: everything except red loses this much colour
  particles: { chips: 70, dust: 160, motes: 260, splashPerPiece: 10, splashPieces: 16 },

  light: {
    key: { position: [-1.2, 3.4, 1.9] as [number, number, number], intensity: 15 }, // omni key, above-front left, out of shot
    fill: { position: [1.8, 0.9, 2.2] as [number, number, number], intensity: 1.6 }, // soft omni fill, front right
    rimA: { position: [-2.2, 2.4, -2.6] as [number, number, number], intensity: 30 },
    rimB: { position: [2.4, 2.2, -2.2] as [number, number, number], intensity: 16 },
    env: 0.12,
    bounce: 0.9,
    exposure: 1.45,
    beam: 0.2, // light-shaft brightness
    beamFrom: [0.1, 4.6, -0.5] as [number, number, number], // top light shaft, falling almost straight down behind the head
  },

  post: {
    ao: { radius: 0.3, thickness: 1.0, blend: 1.0 },
    bloom: { strength: 0.22, radius: 0.5, threshold: 0.93, boomFlash: 0.0 },
    dof: { aperture: 0.0016, maxblur: 0.008 },
    grain: 0.045,
    topGlow: 0.0,
    smoke: { amount: 0.6, scale: 1.4, speed: 0.06, color: "#B03A44" }, // see-through smoke drifting near the lens (two parallax layers) // soft pink light bloom at the top of frame (screen-space haze)
    vignette: 0.42,
    reflector: { size: 1024, tint: "#7A7A80", floorOpacity: 0.9 },
  },

  // Three shots joined by short dips to black (Daredevil-intro editing): each drifts from pos0/look0 to pos1/look1.
  camera: {
    dip: 0.22, // seconds of fade either side of a cut
    shots: [
      { t0: 0.0, t1: 3.4, fov: 24, pos0: [0.32, 0.68, 1.02], look0: [0.03, 0.62, 0.2], pos1: [0.16, 0.6, 0.94], look1: [0.0, 0.56, 0.2] }, // macro: liquid over the brow and eye
      { t0: 3.4, t1: 6.4, fov: 27, pos0: [1.25, 0.46, 0.95], look0: [0, 0.5, 0], pos1: [1.0, 0.4, 1.45], look1: [0, 0.46, 0] }, // profile orbit: coated, cracks appear
      { t0: 6.4, t1: 10.0, fov: 32, pos0: [-0.7, 0.42, 2.3], look0: [0, 0.42, 0], pos1: [-1.6, 1.25, 4.4], look1: [0, 0.12, 0] }, // wide: slow-motion break into the pool
    ] as { t0: number; t1: number; fov: number; pos0: [number, number, number]; look0: [number, number, number]; pos1: [number, number, number]; look1: [number, number, number] }[],
    boomShake: 0.003,
  },
};
