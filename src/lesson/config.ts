// "Tell me about yourself" lesson: every card's words, timing and layout in one place.
// Times are SOURCE seconds from the local Whisper transcript, with each card's anchor word
// pinned to its real onset (scripts/refine-timing.mjs). On-screen text quotes the spoken words.
import type { TeachingCue, TeachingDesign } from "../teaching/TeachingGraphics";

const A = {
  // Anchor word onsets in source seconds: chunked Whisper times checked against where each pause ends
  // (scripts/verify-anchors.mjs). Where unsure, a time is late rather than early.
  tell: 6.16, // "Tell me about yourself"
  mistake: 10.47, // "Now here's a mistake"
  entire: 13.3, // "telling their entire life story" (card quotes the whole phrase, so it starts on "telling")
  professional: 23.71, // "your professional background" (starts on "your")
  use: 28.3, // "Use these three steps"
  first: 30.2, second: 33.99, third: 38.41, explainWhy: 40.5,
  forExample: 44.78, imCurrently: 45.82, andIve: 48.75, iReally: 52.08,
  see: 58.45, clear: 60.75, professional2: 62.0, relevant: 65.4,
  how: 70.2, letMeKnow: 73.32,
};

export const lessonConfig = {
  output: { width: 1920, height: 1080, fps: 30 },
  video: { src: "footage/interview.mov", srcWidth: 1620, srcHeight: 1080, offsetY: -60 },
  trim: { start: 0.4, end: 79.8 }, // speech 0.56-79.6; after 79.8 the presenter stops the recording
  loudness: { targetLufs: -14, truePeak: -1.5 }, // applied after render (source is about -35 LUFS)
  design: { layout: "left", cardWidthRatio: 0.34, cardTopRatio: 0.085, cardMarginRatio: 0.0, leadFrames: 3,
    palette: { panel: "rgba(10, 18, 26, 0.985)" } } as TeachingDesign, // cards cover the wall sign fully; nearly opaque so it doesn't ghost through
  anchors: A,

  cues: [
    { kind: "prompt", title: "THE INTERVIEW QUESTION", side: "left",
      startSeconds: A.tell - 0.1, durationSeconds: 3.6,
      question: "“Tell me about yourself.”" },
    { kind: "contrast", side: "left",
      startSeconds: A.entire - 0.1, durationSeconds: A.professional + 3.2 - (A.entire - 0.1),
      avoidLabel: "AVOID", avoid: "Telling your entire life story",
      betterLabel: "THEY WANT", better: "Your professional background",
      betterAtSeconds: A.professional - (A.entire - 0.1) },
    { kind: "interview", title: "A SIMPLE TRICK: THREE STEPS", side: "left",
      startSeconds: A.use - 0.1, durationSeconds: 44.5 - (A.use - 0.1),
      question: "“Tell me about yourself.”",
      steps: ["Explain what you’re currently doing", "Mention your relevant experience", "Explain why you’re interested in the position"],
      stepTimes: [A.first, A.second, A.third].map((t) => t - (A.use - 0.1)) },
    { kind: "example", side: "left",
      startSeconds: A.forExample - 0.1, durationSeconds: 57.9 - (A.forExample - 0.1),
      note: "Example answer from the lesson",
      lines: [
        { label: "01  CURRENT ROLE", text: "I’m currently working in customer service.", atSeconds: A.imCurrently - (A.forExample - 0.1) },
        { label: "02  EXPERIENCE", text: "I’ve spent the last three years helping clients solve problems.", atSeconds: A.andIve - (A.forExample - 0.1) },
        { label: "03  WHY THIS JOB", text: "I really enjoy communicating with people, which is why I’m interested in this position.", atSeconds: A.iReally - (A.forExample - 0.1) },
      ] },
    { kind: "keypoints", side: "left",
      startSeconds: A.see - 0.1, durationSeconds: 67.2 - (A.see - 0.1),
      lead: "See the difference?",
      items: [
        { text: "Clear", atSeconds: A.clear - (A.see - 0.1) },
        { text: "Professional", atSeconds: A.professional2 - (A.see - 0.1) },
        { text: "Relevant to the job", atSeconds: A.relevant - (A.see - 0.1) },
      ] },
    { kind: "prompt", side: "left",
      startSeconds: A.how - 0.1, durationSeconds: 79.6 - (A.how - 0.1),
      question: "How would you introduce yourself in a job interview?",
      action: "Let me know in the comments", actionAtSeconds: A.letMeKnow - (A.how - 0.1) },
  ] as TeachingCue[],
};
