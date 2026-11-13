// IONADE pour sting: the logo swipe over the Blender frames. Every timing, colour and position lives here.
// Frames come from scripts/blender/ionade_pour.py (preview here, or the farm render), copied to public/ionade/frames/.
export const ionadeConfig = {
  output: { width: 1080, height: 1920, fps: 30, durationInFrames: 200 },
  frames: { dir: "ionade/frames", prefix: "p_", digits: 4, first: 1 },
  logo: { file: "ionade/logo.png", aspect: 2628 / 2104 },
  colours: { orange: "#FA6108", navy: "#0B2E7A", cream: "#FBF5ED" },
  // the swipe: a slanted navy band (the logo's own banner angle) whips across, carrying the logo in from the left
  swipe: {
    start: 132,          // band enters
    land: 142,           // logo lands (spring settles just after)
    bandOut: 152,        // band has left on the right
    angleDeg: -8,        // slant of the band, matching the IONADE banner
    bandHeight: 520,     // px
  },
  flash: { at: 146, length: 12 },             // light sweep across the logo when the bolt "fires"
  logoBox: { cx: 512, cy: 430, width: 780 },  // landed position; kept left of the right-edge UI and above the bottom fifth
  scrim: { from: 132, to: 146, opacity: 0 }, // off: navy over the orange wall muddied it to brown
};
