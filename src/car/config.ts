// Lost Data -> Phillips Digital. Every word, colour, size, event and sound lives here.
// Grammar from references/car-ref.mp4: a still top-down car on a black->grey gradient, hit by
// short flickering glitch bursts on the beat (pixel glyphs, colour flood, dot matrix, brand flash,
// strobes, scanline tears, data readouts), here recoloured to the car's own acid green.

export const C = {
  green: "#8BD11B", // accent = the car's paint
  greenDeep: "#3E6B06",
  white: "#F4F4F2",
  black: "#050505",
  floor: "#C9C9C6", // bottom of the gradient
};

export type Ev =
  | { kind: "dots"; at: number; len: number; text: string }
  | { kind: "strobe"; at: number; len: number; lines?: boolean }
  | { kind: "glyph"; at: number; len: number; ch: string }
  | { kind: "flood"; at: number; len: number }
  | { kind: "brand"; at: number; len: number }
  | { kind: "tear"; at: number; len: number }
  | { kind: "brackets"; at: number; len: number };

export const carConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 240 },
  bpm: 100, // 8th note = 9 frames
  car: { src: "car/car.png", mask: "car/mask.png", w: 1205, h: 711, scale: 1.1, y: 30 },
  words: {
    brand: "PHILLIPS DIGITAL",
    readouts: ["PHILLIPS DIGITAL // FILE 07", "DATA INTEGRITY COMPROMISED", "SECTOR 0x3F LOST", "RECOVERING ... 41%"],
    restored: "DATA RESTORED",
  },
  monoFont: "LiberationMono",
  pixel: 14, // dot-matrix cell size (px)
  mosaic: 18, // pixelation block size during glyph bursts (px)

  // Events, in frames. Bursts flicker: on/off per `flicker` pattern.
  flicker: [1, 1, 0, 1, 1, 0, 1, 1, 1], // frame-by-frame on/off within a burst
  events: [
    { kind: "dots", at: 9, len: 9, text: "PD" },
    { kind: "strobe", at: 36, len: 9 },
    { kind: "glyph", at: 45, len: 9, ch: "P" },
    { kind: "flood", at: 54, len: 4 },
    { kind: "glyph", at: 58, len: 5, ch: "D" },
    { kind: "brackets", at: 63, len: 18 },
    { kind: "brand", at: 81, len: 9 },
    { kind: "tear", at: 108, len: 9 },
    { kind: "strobe", at: 117, len: 9, lines: true },
    { kind: "glyph", at: 144, len: 5, ch: "H" },
    { kind: "flood", at: 149, len: 4 },
    { kind: "dots", at: 153, len: 9, text: "PD" },
    { kind: "tear", at: 162, len: 5 },
    { kind: "strobe", at: 167, len: 4 },
  ] as Ev[],

  // Readouts: [text index, from, to, corner]
  readouts: [
    [0, 2, 171, "tl"],
    [1, 40, 120, "br"],
    [2, 90, 171, "tr"],
    [3, 100, 171, "bl"],
  ] as [number, number, number, "tl" | "tr" | "bl" | "br"][],

  dissolve: { start: 171, end: 189 }, // car pixelates and drops out to black
  end: { start: 189, glitchFrames: 9, pixel: 18, restoredAt: 204 },

  audio: {
    music: "car/music.wav", musicVolume: 0.85,
    // sound per event kind (rotated takes), trimmed to the burst length
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
