// Playful pixel-art sneaker (brief: notes/briefs/pixel-playful.md). Grammar from the user's pixel poster reference (giant pixel
// masthead, chunky pixel object with black outlines, editorial small print, barcode, side tab); words and logo are ours.
// Every word, colour, size and timing lives here. Sprites: public/pixel/<palette>/s_000.png ... (24-angle turntable).
import palettes from "../../scripts/pixel_palettes.json";

export const PX = 6; // one logical pixel = 6 screen pixels (320 x 180 logical grid at 1920 x 1080)
export const pixelConfig = {
  output: { width: 1920, height: 1080, fps: 24, durationInFrames: 288 },
  palettes: palettes as Record<string, { label: string; page: string; masthead: string; accent: string; ink: string }>,
  sprite: { angles: 24, stepFrames: 2, scale: 6, x: 386, y: 170, w: 200, h: 150, contentBottom: 130, contentX: [40, 167] }, // camera-rolled sprites (toe down)
  masthead: { text: "PHILLIPS", y: 22, size: 372, spacing: "-0.075em" },
  bottom: { text: "MOTION DESIGN", y: 968, size: 92 },
  side: { lines: ["PHILLIPS", "DIGITAL", "2026"], x: 72, y: 400 },
  blurb: ["PIXELS IN MOTION.", "BUILT FRAME BY FRAME", "IN THE STUDIO."], // placeholder copy: needs the user's OK
  tab: { letters: "PHIL", sub: "MOTION", x: 1800, y: 690 },
  corner: ["PLAY IN PIXELS", "MOVE DIFFERENT"], // top-right small print (placeholder copy: needs the user's OK)
};
