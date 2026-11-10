// Cinema 4D-style MoGraph demo: every colour, size, timing and camera value lives here.
// Times in seconds; everything is computed from frame / fps (deterministic, no running clock).

export const c4dConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInSeconds: 8 },

  palette: {
    backdrop: "#E4D9CF", // seamless studio sweep (warm, a touch darker so white clay separates)
    clayLow: "#F6F0EA", // resting cubes
    clayMid: "#B9A7FF", // lavender as they rise
    clayHigh: "#FFAE94", // peach at full height
    sphere: "#2F47FF", // glossy cobalt effector
  },

  grid: { count: 11, spacing: 0.75, size: 0.62, radius: 0.09, baseHeight: 0.22, maxRise: 1.05 },

  sphere: {
    radius: 0.55,
    dropFrom: 4.2,
    land: 0.6, // seconds: first contact
    bounce: { height: 0.35, until: 0.95 },
    rollStart: 0.95,
    rollEnd: 5.6, // comes to rest at centre
    // Catmull-Rom path on the floor (x, z): corner -> S-curve -> centre
    path: [
      [-3.7, -3.7],
      [2.6, -2.9],
      [-2.6, 0.4],
      [2.7, 2.6],
      [0, 0],
    ] as [number, number][],
  },

  // bow wave: a ring of cubes rises around the sphere (ring radius/width), cubes underneath pressed down
  // ringFade: after the sphere stops, the ring sinks back over this many seconds (the press stays: it rests in a dent)
  effector: { ringRadius: 1.2, ringWidth: 0.45, press: 0.4, lag: 0.06, ringFade: 0.7 },
  spring: { omega: 14, damping: 0.42, window: 0.9 }, // delay-effector feel: rad/s, damping ratio, history (s)

  ripple: { start: 5.6, speed: 4.2, width: 0.55, decay: 0.9, amount: 1.0 },

  camera: {
    fov: 28,
    distance: 12.8,
    height: 8.4,
    orbitFrom: 28, // degrees around the grid
    orbitTo: 62,
    orbitEnd: 6.6, // eases to a stop, then holds
    lookAt: [0, 0.2, 0.4] as [number, number, number],
  },

  light: { key: [5, 10, 6] as [number, number, number], keyIntensity: 4.0, ambient: 0.1, envIntensity: 0.22, exposure: 0.95 },
};
