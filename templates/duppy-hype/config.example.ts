// Duppy-style edit: every word, colour, font and timing lives here.
// Caption text must match what was said. Each group takes the next N spoken words
// from timeline.json (N = number of words in `text`), so keep the word count the same
// when you fix a word. Times come from the real recording, never from the script.

export type Role = "line" | "anchor" | "hero";
export type Group = {
  text: string; // exact spoken words
  role?: Role; // line = word-by-word lyric caption, anchor = bigger caption, hero = full slam
  accent?: string[]; // words highlighted in the accent colour
  color?: "accent" | "danger"; // hero colour
  step?: 1 | 2 | 3; // shows that step block when the group starts
};

export const duppyConfig = {
  video: {
    src: "footage/interview.mov", // copy in public/ (original stays in inputs/)
    srcWidth: 1620,
    srcHeight: 1080,
    offsetY: -60, // px: shifts the cropped frame up/down
    focus: { x: 1050, y: 420 }, // zoom centre (roughly the face) in output pixels
    jumpZoom: 1.1, // every other cut is punched in this much
  },
  output: { width: 1920, height: 1080, fps: 30 },

  colors: {
    text: "#FFFFFF",
    accent: "#FFE100",
    danger: "#FF2D2D",
    outline: "#0A0A0A",
    blockBg: "#0A0A0A",
    blockNumber: "#FFE100",
    blockText: "#FFFFFF",
    flash: "#FFFFFF",
  },
  fonts: {
    display: "Anton", // heavy condensed, uppercase
    body: "Inter",
  },

  captions: {
    size: 92, // px, lyric line
    anchorSize: 120,
    y: 1000, // baseline of the caption line (px from top)
    popScale: 1.2, // words stretch up from the baseline this much as they land (height only, so they never touch)
    wordGap: "0.28em",
    leadFrames: 2, // words appear this many frames before they're spoken
    maxWidth: 1500,
  },
  hero: {
    maxSize: 330,
    twoLineMaxSize: 185, // two-line slams are smaller so they stay off the face
    maxWidth: 1500,
    centerY: 810, // over the chest, clear of the face
    slamFrom: 1.4, // slam words start this big
    slamFrames: 4,
    shakePx: 16,
    shakeFrames: 9,
    punchZoom: 0.14, // extra camera punch on a hero landing
    flashFrames: 2,
    flashOpacity: 0.55,
    minHold: 0.9, // seconds
  },
  steps: {
    x: 1400,
    y: 150,
    width: 470,
    rowHeight: 108,
    gap: 22,
    labels: { 1: "WHAT YOU'RE DOING", 2: "RELEVANT EXPERIENCE", 3: "WHY THIS POSITION" } as Record<number, string>,
  },
  grain: 0.07, // film grain strength (0 = off)

  groups: [
    { text: "So imagine" },
    { text: "you're sitting" },
    { text: "in a job interview" },
    { text: "and the interviewer asks you" },
    { text: "Tell me about yourself?", role: "hero", color: "accent" },
    { text: "Hmm", role: "anchor" },
    { text: "Now here's a" },
    { text: "mistake", role: "hero", color: "danger" },
    { text: "I hear quite often" },
    { text: "People start telling their" },
    { text: "entire life story", role: "hero", color: "danger" },
    { text: "But here's the thing", role: "anchor" },
    { text: "The interviewer doesn't need" },
    { text: "to know everything about you", accent: ["everything"] },
    { text: "They want to understand your" },
    { text: "professional background", role: "hero", color: "accent" },
    { text: "So here's a simple trick", role: "anchor", accent: ["simple", "trick"] },
    { text: "use these" },
    { text: "three steps", role: "hero", color: "accent" },
    { text: "First", role: "anchor", step: 1 },
    { text: "explain what you're currently doing" },
    { text: "second", role: "anchor", step: 2 },
    { text: "mention your relevant experience", accent: ["relevant"] },
    { text: "And third", role: "anchor", step: 3 },
    { text: "explain why you're interested" },
    { text: "in the position", accent: ["position"] },
  ] as Group[],
};
