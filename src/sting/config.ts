// Phillips English logo sting: every timing, size, colour and sound in one place.
// The logo pieces are the user's real logo (inputs/phillips-english-logo.jpg), lifted off its
// background by scripts/split-logo.py into public/logo/*.png. Positions are in logo-file pixels.
import pieces from "../../public/logo/pieces.json";

export const stingConfig = {
  output: { width: 1920, height: 1080, fps: 30, durationInFrames: 90 },
  pieces: pieces.pieces,
  logoBox: { x0: 294, y0: 272, x1: 968, y1: 1005 }, // union of all pieces (logo-file px)
  // Ink edges measured from the logo file: pieces are revealed from these lines.
  ink: { pe: { bottom: 660 }, phillips: { top: 762 }, english: { top: 899 } },
  logoHeightOnScreen: 640, // px at 1080p (about 59% of the frame height)
  colors: { bgCentre: "#141C26", bgEdge: "#0A0F15" }, // around the logo file's own #0F161E
  motionBlur: { shutterAngle: 180, samples: 10 },

  // Frames (30 fps). One technique: build-on from the bar.
  t: {
    barGrow: 0, // bar springs from a short stub to full width
    p: 8, // P rises from behind the bar's top edge
    e: 12,
    phillips: 18, // name drops from under the bar's bottom edge
    english: 22,
    land: 30, // everything settled: overshoot-and-settle lands on the impact peak
  },
  barStubWidth: 0.12, // share of the bar's width visible on frame 0 (first frame isn't empty)
  overshoot: 0.025, // whole-logo scale kick on the landing (1.025 -> 1.0)
  spring: { w: 0.42, z: 0.78 }, // rad/frame, damping ratio (0.7-0.85 reads premium)

  // Sound logo (bundled CC0 kit). frame = picture moment; peakMs = file's peak, so it lands 1 frame after.
  masterVolume: 1.0,
  sounds: [
    { frame: 22, file: "sfx/kit_whoosh.ogg", volume: 0.8, peakMs: 83 },
    { frame: 30, file: "sfx/kit_impact.ogg", volume: 1.0, peakMs: 57 },
  ],
};
