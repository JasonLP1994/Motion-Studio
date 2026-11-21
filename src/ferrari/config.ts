// Red Glitch -> Phillips Digital. Every word, colour, scene, event and sound lives here.
// Same grammar as LostData (references/car-ref.mp4) but in the reference's own red / black / white,
// on full-frame photos, and much wilder: stacked bursts, RGB split, macroblock shuffle, pixel smears,
// negative flashes, beat zoom punches with shake, a rapid-cut montage and paper ASCII x dither frames.

export const C = {
  red: "#E81E1E",
  black: "#050505",
  white: "#F4F4F2",
  paper: "#EEECE7",
};

export type Kind =
  | "glyph" | "flood" | "strobe" | "tear" | "dots" | "brand" | "brackets"
  | "pattern" | "patternZoom" | "rgb" | "shuffle" | "smear" | "invert";
export type Ev = { kind: Kind; at: number; len: number; ch?: string; text?: string; ink?: "red" | "white" | "black"; lines?: boolean; v?: number; zoom?: number; fx?: number; fy?: number };

export type Scene = {
  name: string; // public/ferrari/<name>.png (+ -mask, -mosaic_<b>, -pattern_<v>)
  w: number; h: number;
  fit: "cover" | "width";
  len: number; // in 8ths (9 frames)
  readout: string;
  events: Ev[];
  nodes?: boolean; // the "node network" frame (dimmed car, edge bars, NODE tags, wires, name block)
};

const S = (n: number) => n * 9;

export const redConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 576 }, // 19.2 s: scenes 423 f + montage 72 + dissolve 15 + wordmark 66
  bpm: 100,
  words: { brand: "PHILLIPS DIGITAL", file: "PHILLIPS DIGITAL // FILE 08", view: "VIEW {n}/06", restored: "DATA RESTORED" },
  monoFont: "LiberationMono",
  pixel: 14,
  flicker: [1, 1, 0, 1, 0, 1, 1, 0, 1], // wilder flicker than LostData
  punch: { every: 9, amount: 0.07, frames: 5, shake: 14 }, // zoom punch on every 8th + shake during bursts

  scenes: [
    {
      name: "top", w: 1448, h: 1086, fit: "cover", len: 9, readout: "DATA INTEGRITY COMPROMISED",
      events: [
        { kind: "rgb", at: 0, len: 6 },
        { kind: "dots", at: S(1), len: 9, text: "PD" },
        { kind: "glyph", at: S(2), len: 9, ch: "P" },
        { kind: "shuffle", at: S(3), len: 5 },
        { kind: "strobe", at: S(4), len: 6, ink: "red" },
        { kind: "pattern", at: S(5), len: 5, v: 1 },
        { kind: "flood", at: S(6), len: 4 },
        { kind: "smear", at: S(6) + 4, len: 5 },
        { kind: "invert", at: S(7), len: 2 },
        { kind: "glyph", at: S(7) + 2, len: 6, ch: "H" },
        { kind: "tear", at: S(8) + 3, len: 6 },
      ],
    },
    {
      name: "top", w: 1448, h: 1086, fit: "cover", len: 4, readout: "NODE MAP // 5 LINKED", nodes: true,
      events: [
        { kind: "rgb", at: 0, len: 3 },
        { kind: "smear", at: 22, len: 3 },
        { kind: "invert", at: 31, len: 2 },
      ],
    },
    {
      name: "side", w: 2021, h: 778, fit: "width", len: 9, readout: "SECTOR 0x3F LOST",
      events: [
        { kind: "smear", at: 0, len: 6 },
        { kind: "brand", at: S(1), len: 7 },
        { kind: "rgb", at: S(1) + 7, len: 6 },
        { kind: "glyph", at: S(2) + 4, len: 7, ch: "I" },
        { kind: "patternZoom", at: S(3) + 4, len: 4, v: 2, zoom: 2.6, fx: 0.42, fy: 0.5 },
        { kind: "strobe", at: S(4) + 2, len: 6, ink: "white", lines: true },
        { kind: "shuffle", at: S(5), len: 6 },
        { kind: "glyph", at: S(6), len: 6, ch: "L" },
        { kind: "flood", at: S(6) + 6, len: 3 },
        { kind: "invert", at: S(7), len: 2 },
        { kind: "pattern", at: S(7) + 3, len: 5, v: 1 },
        { kind: "tear", at: S(8) + 3, len: 6 },
      ],
    },
    {
      name: "front", w: 1672, h: 941, fit: "cover", len: 9, readout: "RECOVERING ... 12%",
      events: [
        { kind: "rgb", at: 0, len: 8 },
        { kind: "glyph", at: S(1), len: 8, ch: "L" },
        { kind: "brackets", at: S(1), len: 18 },
        { kind: "smear", at: S(2), len: 5 },
        { kind: "strobe", at: S(3), len: 5, ink: "red", lines: true },
        { kind: "pattern", at: S(3) + 5, len: 5, v: 2 },
        { kind: "shuffle", at: S(4) + 4, len: 6 },
        { kind: "glyph", at: S(5) + 4, len: 6, ch: "I" },
        { kind: "brand", at: S(6) + 4, len: 6 },
        { kind: "invert", at: S(7) + 2, len: 2 },
        { kind: "flood", at: S(7) + 5, len: 4 },
        { kind: "tear", at: S(8) + 3, len: 6 },
      ],
    },
    {
      name: "toprear", w: 1672, h: 941, fit: "cover", len: 9, readout: "RECOVERING ... 41%",
      events: [
        { kind: "shuffle", at: 0, len: 6 },
        { kind: "patternZoom", at: S(1), len: 4, v: 1, zoom: 2.4, fx: 0.62, fy: 0.62 },
        { kind: "glyph", at: S(1) + 5, len: 7, ch: "P" },
        { kind: "rgb", at: S(2) + 5, len: 6 },
        { kind: "dots", at: S(3) + 5, len: 8, text: "PD" },
        { kind: "strobe", at: S(4) + 5, len: 5, ink: "white" },
        { kind: "smear", at: S(5) + 4, len: 6 },
        { kind: "pattern", at: S(6) + 3, len: 6, v: 2 },
        { kind: "glyph", at: S(7) + 1, len: 7, ch: "S" },
        { kind: "tear", at: S(8) + 3, len: 6 },
      ],
    },
    {
      name: "wheel", w: 1672, h: 941, fit: "cover", len: 7, readout: "RECOVERING ... 87%",
      events: [
        { kind: "rgb", at: 0, len: 7 },
        { kind: "flood", at: S(1), len: 4 },
        { kind: "patternZoom", at: S(1) + 5, len: 4, v: 2, zoom: 2.2, fx: 0.3, fy: 0.62 },
        { kind: "smear", at: S(2) + 4, len: 6 },
        { kind: "invert", at: S(3) + 3, len: 2 },
        { kind: "shuffle", at: S(4), len: 6 },
        { kind: "strobe", at: S(5), len: 6, ink: "red", lines: true },
        { kind: "pattern", at: S(6), len: 6, v: 1 },
      ],
    },
  ] as Scene[],

  // Rapid montage after the scenes: one photo per 16th (4-5 frames) with a random glitch stacked on.
  montage: { len: 8, order: ["top", "front", "side", "wheel", "toprear"], kinds: ["rgb", "shuffle", "pattern", "smear", "invert", "flood", "strobe", "tear"] as Kind[] },

  // Node network frame (grammar from the user's "Lost Data" node still), in red / black / white.
  nodes: {
    name: "FERRARI", // the user asked for the car's name here (text only, no maker logo)
    labels: ["NODE_1", "NODE_2", "NODE_3", "NODE_4", "NODE_5"],
    picks: [0.12, 0.3, 0.5, 0.7, 0.9], // where along the car each node sits (0 = front)
    sides: ["top", "bottom", "top", "bottom", "top"] as ("top" | "bottom")[],
    nodeEvery: 3, wireFrames: 8, dim: 0.28,
    code: [
      ["FERRARI_LD08", "", "[STATUS]   NET", "DATA:  6597", "TOKEN-84-34  152", "-25.7  23.42  EXPLOIT-20", "DATA-48   975"],
      ["Spec:  0.62", "ROOT", "SUBJECT  NODE", "LOCK 166-85  [5404] >>", "Freq:  7.7 MHz", "DRIVE-90", "", "function readLoad(module) {", "  let raw = module.load ?? 0;", "  return isNaN(raw) ? 0 : raw;", "}"],
    ],
  },

  dissolveFrames: 15,
  end: { glitchFrames: 12, pixel: 22, restoredDelay: 15 },

  annotations: {
    perScene: 9, life: [10, 24] as [number, number], lineFrames: 2,
    kinds: ["callout", "callout", "reticle", "dimension", "cross", "callout"] as const,
    labels: ["NODE_0x3F", "SCAN 23%", "REF 08-R", "LAYER 05", "CRC ERR", "DESYNC", "MESH 4096", "Ø 20.0", "VTX 2211", "FRAME {f}", "OVERFLOW"],
    fontSize: 21, stroke: 3, minGap: 200,
  },

  audio: {
    music: "ferrari/music.wav", musicVolume: 0.85,
    sfx: {
      dots: ["car/sfx/kenney-interface-glitch-002.ogg"],
      strobe: ["car/sfx/kenney-sci-computernoise-000.ogg", "car/sfx/kenney-sci-computernoise-001.ogg"],
      glyph: ["car/sfx/fs-144546-touchs-wav.ogg"],
      flood: ["car/sfx/kenney-interface-glitch-002.ogg"],
      brand: ["car/sfx/fs-416777-digital-typing-wav.ogg"],
      tear: ["car/sfx/fs-402451-fast-forward.ogg"],
      patternZoom: ["car/sfx/kenney-sci-computernoise-001.ogg"],
      shuffle: ["car/sfx/kenney-interface-glitch-002.ogg"],
      invert: ["car/sfx/kenney-interface-glitch-002.ogg"],
    } as Record<string, string[]>,
    sfxVolume: 0.5,
    endHit: "car/sfx/kenney-sci-lowfrequency-explosion-000.ogg", endHitVolume: 0.75,
  },
};

export const timeline = (() => {
  let t = 0;
  const starts = redConfig.scenes.map((s) => {
    const a = t;
    t += S(s.len);
    return a;
  });
  const montage = t;
  const dissolve = montage + S(redConfig.montage.len);
  const end = dissolve + redConfig.dissolveFrames;
  return { starts, montage, dissolve, end };
})();
