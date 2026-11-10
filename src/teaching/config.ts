import type { TeachingCue } from "./TeachingGraphics";

// Match the existing Phillips English intro at src/intro/config.ts.
export const teachingTheme = {
  colors: {
    bg: "#0A0E13",
    charcoal: "#1A232D",
    panel: "rgba(10, 18, 26, 0.94)",
    panelInset: "rgba(29, 43, 53, 0.94)",
    border: "rgba(128, 184, 198, 0.40)",
    accent: "#80B8C6",
    white: "#FFFFFF",
    cream: "#F4EFE6",
    muted: "#91A9B3",
    wrong: "#E88B84",
  },
};

// DEMONSTRATION ONLY: not transcribed from an actual student or source video.
// Replace each phrase and timing with exact, verified lesson content before production.
export const teachingDemoCues: TeachingCue[] = [
  {
    kind: "correction",
    startSeconds: 0,
    durationSeconds: 3.6,
    side: "full",
    original: "Let's discuss about the plan.",
    corrected: "Let's discuss the plan.",
    note: "Use discuss without about.",
  },
  {
    kind: "pronunciation",
    startSeconds: 3.6,
    durationSeconds: 3.6,
    side: "full",
    word: "present",
    stress: "PRE-sent (noun)  /  pre-SENT (verb)",
    tip: "The stress changes with the word's function.",
  },
  {
    kind: "vocabulary",
    startSeconds: 7.2,
    durationSeconds: 3.6,
    side: "full",
    basic: "very important",
    precise: "essential",
    context: "Use essential when something is necessary.",
  },
  {
    kind: "interview",
    startSeconds: 10.8,
    durationSeconds: 3.6,
    side: "full",
    question: "Tell me about yourself.",
    steps: ["Current role", "Relevant experience", "Why this position"],
  },
  {
    kind: "conversation",
    startSeconds: 14.4,
    durationSeconds: 4.2,
    side: "full",
    lines: [
      { speaker: "COLLEAGUE", text: "Could we clarify the deadline?" },
      { speaker: "YOU", text: "Certainly. Let's confirm the date." },
    ],
    tip: "A polite question followed by a clear action.",
  },
];

export const teachingDemoOutput = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInSeconds: 18.6,
};
