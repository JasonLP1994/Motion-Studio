// Phillips English intro: every word, colour, size and beat time lives here.
// Times are in seconds and sit on the music's beat grid (about 150 bpm, a beat every 0.4 s).

export const introConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInSeconds: 8 },
  music: "audio/pe-intro-music.wav", // copy in public/ (taken from the user's own intro)
  motionBlur: { shutterAngle: 180, samples: 8 },

  colors: {
    bgCentre: "#1A232D",
    bgEdge: "#0A0E13",
    white: "#FFFFFF",
    teal: "#80B8C6",
  },
  fonts: { display: "Montserrat", logo: "Inter" },

  // The line: the one element that never cuts.
  line: { thickness: 5, dotWidth: 90, startWidth: 1500, gap: 12 }, // gap = space between words and the line

  phrase1: { white: "SAY", teal: "IT", size: 210, lineY: 668, lineWidth: 680 },
  phrase2: { white: "OUT", teal: "LOUD", size: 210, lineY: 668, lineWidth: 1144, blockWidth: 1250, blockHeight: 262 },
  phrase3: { small: "EVERY", big: "DAY.", smallSize: 62, bigSize: 330, lineY: 800, lineWidth: 640 },
  logo: {
    p: "P", e: "E", monoSize: 500, monoBottom: 572,
    barY: 620, barWidth: 264, barThickness: 16,
    line1: "PHILLIPS", line2: "ENGLISH", nameSize: 118, nameTop: 668, nameLineHeight: 118,
  },

  t: {
    lineShoot: 0.19, // first hit: the line shoots out from a dot
    say: 0.77,
    it: 1.17,
    blockUp: 1.97, // the line swells into a block and covers phrase 1
    blockSwap: 2.2, // words swap behind the block
    blockDown: 2.37, // the block drops back to a line: OUT LOUD is there
    phrase2Out: 3.05,
    every: 3.17,
    dayOutline: 3.4,
    dayFill: 3.97, // big hit in the music
    phrase3Out: 4.62,
    logoBar: 4.77, // the line becomes the logo bar
    p: 5.17,
    e: 5.37,
    name1: 5.57,
    name2: 5.97, // lands by about 6.2s, then the logo holds dead still for the last 2 seconds
    sheen: 6.76,
  },
};
