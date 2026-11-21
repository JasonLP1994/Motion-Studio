// Lost Data -> Phillips Digital. Every word, colour, size, scene, event and sound lives here.
// Grammar from references/car-ref.mp4: a still car on a dark gradient, hit by short flickering
// glitch bursts on the beat (pixel glyphs, colour flood, dot matrix, brand flash, strobes,
// scanline tears, data readouts). Palette (user): green, black and yellow only.

export const C = {
  green: "#8BD11B", // the car's paint
  yellow: "#FFD60A",
  black: "#050505",
  floor: "#22231F", // bottom of the background gradient (near-black)
  white: "#F5F5F2", // ONLY for the digital annotations
};

export type Ev =
  | { kind: "dots"; at: number; len: number; text: string }
  | { kind: "strobe"; at: number; len: number; lines?: boolean; ink?: "green" | "yellow" }
  | { kind: "glyph"; at: number; len: number; ch: string }
  | { kind: "flood"; at: number; len: number }
  | { kind: "brand"; at: number; len: number }
  | { kind: "tear"; at: number; len: number }
  | { kind: "brackets"; at: number; len: number };

export type Scene = {
  name: string;
  src: string; mask: string; mosaic: string; // mosaic prefix: `${mosaic}mosaic_<b>.png`
  w: number; h: number; // cut-out size in px
  fit: { width?: number; height?: number }; // on-screen size (one of them)
  x: number; y: number; // centre offset from frame centre
  shadow: "top" | "floor" | "none";
  len: number; // in 8ths (9 frames)
  events: Ev[]; // `at` in frames from the scene start
  readout: string; // bottom-right status line
};

const S = (n: number) => n * 9; // 8ths -> frames

export const carConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 480 },
  bpm: 100, // 8th note = 9 frames
  words: {
    brand: "PHILLIPS DIGITAL",
    file: "PHILLIPS DIGITAL // FILE 07",
    view: "VIEW {n}/04",
    restored: "DATA RESTORED",
  },
  monoFont: "LiberationMono",
  pixel: 14,
  flicker: [1, 1, 0, 1, 1, 0, 1, 1, 1], // frame-by-frame on/off inside a burst

  scenes: [
    {
      name: "top", src: "car/car.png", mask: "car/mask.png", mosaic: "car/", w: 1205, h: 711,
      fit: { width: 1325 }, x: 0, y: 30, shadow: "top", len: 12, readout: "DATA INTEGRITY COMPROMISED",
      events: [
        { kind: "dots", at: S(1), len: 9, text: "PD" },
        { kind: "strobe", at: S(4), len: 9, ink: "green" },
        { kind: "glyph", at: S(5), len: 9, ch: "P" },
        { kind: "flood", at: S(6), len: 4 },
        { kind: "brackets", at: S(7), len: 18 },
        { kind: "glyph", at: S(9), len: 9, ch: "H" },
        { kind: "tear", at: S(11) + 4, len: 5 },
      ],
    },
    {
      name: "side", src: "car/side.png", mask: "car/side-mask.png", mosaic: "car/side-", w: 1342, h: 365,
      fit: { width: 1700 }, x: 0, y: 110, shadow: "floor", len: 12, readout: "SECTOR 0x3F LOST",
      events: [
        { kind: "glyph", at: S(1), len: 9, ch: "I" },
        { kind: "brand", at: S(3), len: 9 },
        { kind: "strobe", at: S(5), len: 9, ink: "yellow", lines: true },
        { kind: "glyph", at: S(7), len: 5, ch: "L" },
        { kind: "flood", at: S(7) + 5, len: 4 },
        { kind: "dots", at: S(9), len: 9, text: "PD" },
        { kind: "tear", at: S(11) + 4, len: 5 },
      ],
    },
    {
      name: "rear", src: "car/rear.png", mask: "car/rear-mask.png", mosaic: "car/rear-", w: 1112, h: 652,
      fit: { height: 800 }, x: 0, y: 60, shadow: "floor", len: 10, readout: "RECOVERING ... 41%",
      events: [
        { kind: "glyph", at: S(1), len: 9, ch: "L" },
        { kind: "strobe", at: S(3), len: 9, ink: "green" },
        { kind: "brackets", at: S(4), len: 18 },
        { kind: "glyph", at: S(6), len: 9, ch: "I" },
        { kind: "brand", at: S(8), len: 9 },
        { kind: "tear", at: S(9) + 4, len: 5 },
      ],
    },
    {
      name: "front", src: "car/front.png", mask: "car/front-mask.png", mosaic: "car/front-", w: 1448, h: 967,
      fit: { width: 1920 }, x: 0, y: 60, shadow: "none", len: 9, readout: "RECOVERING ... 87%",
      events: [
        { kind: "glyph", at: S(1), len: 9, ch: "P" },
        { kind: "flood", at: S(3), len: 4 },
        { kind: "strobe", at: S(4), len: 9, ink: "yellow", lines: true },
        { kind: "glyph", at: S(6), len: 9, ch: "S" },
        { kind: "dots", at: S(8), len: 9, text: "PD" },
      ],
    },
  ] as Scene[],

  // White digital annotations, placed at seeded-random points on each car, on the beat.
  annotations: {
    perScene: 8,
    life: [14, 32] as [number, number], // frames on screen
    lineFrames: 3, // leader line draws on
    kinds: ["callout", "callout", "reticle", "dimension", "cross", "callout"] as const,
    labels: ["NODE_0x3F", "SCAN 87%", "REF 07-A", "LAYER 03", "CRC ERR", "SYNC", "MESH 2048", "Ø 21.4", "VTX 1129", "FRAME {f}"],
    fontSize: 21,
    stroke: 3,
    minGap: 220, // px: skip an annotation that would crowd one already on screen
  },

  dissolveFrames: 18, // after the last scene: the car pixelates and drops out
  end: { glitchFrames: 9, pixel: 22, restoredDelay: 15 },

  audio: {
    music: "car/music.wav", musicVolume: 0.85,
    sfx: {
      dots: ["car/sfx/kenney-interface-glitch-002.ogg"],
      strobe: ["car/sfx/kenney-sci-computernoise-000.ogg", "car/sfx/kenney-sci-computernoise-001.ogg"],
      glyph: ["car/sfx/fs-144546-touchs-wav.ogg"],
      flood: ["car/sfx/kenney-interface-glitch-002.ogg"],
      brand: ["car/sfx/fs-416777-digital-typing-wav.ogg"],
      tear: ["car/sfx/fs-402451-fast-forward.ogg"],
      brackets: [],
    } as Record<string, string[]>,
    sfxVolume: 0.55,
    endHit: "car/sfx/kenney-sci-lowfrequency-explosion-000.ogg", endHitVolume: 0.7,
  },
};

// Scene start frames, the dissolve and the wordmark, all derived from the lengths above.
export const timeline = (() => {
  let t = 0;
  const starts = carConfig.scenes.map((s) => {
    const a = t;
    t += S(s.len);
    return a;
  });
  const dissolve = t;
  const end = dissolve + carConfig.dissolveFrames;
  return { starts, dissolve, end };
})();
