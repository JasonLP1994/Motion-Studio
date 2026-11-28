// Phillips Digital showreel: every word, colour, font and timing in one place.
// Shot order and cut frames live in timeline.json (made by scripts/showreel/make_timeline.py from the music's hits).
export const showreelConfig = {
  output: { width: 1920, height: 1080, fps: 30 },
  music: "showreel/skinned.mp3",
  colours: { lime: "#C7F944", cream: "#F4EFE3", ink: "#12201A", white: "#F2F2EE", dim: "rgba(242,242,238,0.38)", black: "#050606" },
  fonts: {
    head: { family: "InterX", file: "fonts/inter-latin-800-normal.woff2", weight: "800" },
    mono: { family: "MonoX", file: "fonts/LiberationMono-Bold.ttf", weight: "700" },
  },
  boot: {
    lines: [
      { at: 10, text: "> PHILLIPS DIGITAL // ARCHIVE" },
      { at: 48, text: "> loading 30 projects" },
      { at: 118, text: "> signal found" },
    ],
    charsPerFrame: 1.6,
    countFrom: 72, countTo: 116,              // 00 -> 30 counter, archive ticks light grey as they load
    glitchFrom: 142,
  },
  tag: { x: 80, bottom: 128, numSize: 24, nameSize: 40, discSize: 22, minFrames: 18, slideFrames: 7 },
  bar: { x: 80, right: 80, bottom: 62, h: 5, gap: 6, litH: 12 },
  // per-section look: slow push-in amount over a shot, and a grade
  look: {
    signal: { push: 0.06, filter: "saturate(0.55) brightness(0.82) contrast(1.12)" },
    build: { push: 0.035, filter: "none" },
    break: { push: 0.05, filter: "saturate(0.7) brightness(0.88) contrast(1.08)" },
    rebuild: { push: 0.04, filter: "contrast(1.15)" },
    peak: { push: 0.02, filter: "contrast(1.06)" },
    hero: { push: 0.03, filter: "contrast(1.05)" },
    overload: { push: 0.0, filter: "contrast(1.25) saturate(1.2) brightness(0.55)" },
  } as Record<string, { push: number; filter: string }>,
  tearEvery: 4,          // every Nth build cut gets a 3-frame data tear; every peak cut on a big hit too
  tearFrames: 3,
  flashFrames: 3,        // white flash on the drop and the peak
  vignette: 0.42,
  overloadText: "ARCHIVE COMPLETE // 30/30",
  logo: {
    image: "logo/phillips-digital-logo-alpha.png", imgW: 992, imgH: 568, scale: 1.45, centreY: 470,
    circle: { x0: 40, y0: 148, x1: 258, y1: 418, at: 8 },          // frames after the logo section starts
    line1: { x0: 312, y0: 86, x1: 760, y1: 248, at: 15 },
    line2: { x0: 312, y0: 322, x1: 700, y1: 490, at: 21 },
    tagline: { text: "We build worlds", at: 40, size: 50, y: 860, wordGap: 2 },
    sub: { text: "SHOWREEL 2026", at: 58, size: 22, y: 940 },
  },
  sfx: { boot: "sfx/ui-blip_kenney-digital-twotone1.ogg", logo: "sfx/kit_impact.ogg" },
};
