// PD-01 HUD: every word, colour and timing in one place (copy is DRAFT, waiting for the user's approval).
export const pd01Config = {
  fps: 24, width: 1920, height: 1080, durationInSeconds: 15,
  colors: { page: "#1A2BFF", ink: "#F4F6FF", pink: "#FF1A8C", dark: "#0A0A14", line: "rgba(244,246,255,0.55)", glow: "rgba(110,130,255,0.55)", haze: "rgba(255,26,140,0.16)", vignette: "rgba(4,8,70,0.55)" },
  fonts: { display: "BarlowCondensed-BlackItalic.ttf", ui: "chakra-petch-latin-700-normal.woff2", uiMed: "chakra-petch-latin-500-normal.woff2", jp: "noto-sans-jp-japanese-700-normal.woff2" },
  figure: "pd01/figure_v3.png",
  figurePos: { left: 0, top: 0, height: 1080 },   // the 3D camera does the framing; the plate fills the frame
  copy: {
    masthead: "PD-01",
    tag: "PHILLIPS://DIGITAL",
    jpTitle: "モーションデザイン・システム",
    subTitle: "MOTION DESIGN SYSTEM",
    model: "01",
    serial: "PD01-26A-PINK",
    klass: "MOTION / 3D / TYPE",
    barcodeLabel: "PD01-26A-PINK",
    barcodeNum: "260126  011994  001",
    coords: ["53°38'51.0\"N", "1°46'48.0\"W"],
    issue: "26",
    issueSub: ["WINTER", "/ 2026"],
    edition: ["LIMITED", "EDITION"],
    traits: ["DESIGN", "ANIMATE", "DELIVER"],
    jpTop: "未来は、動きでつくる。",
    jpBottom: "未来をデザインする",
    protocol: ["// PINK PROTOCOL", "// FRAME BY FRAME", "// BUILT IN CODE"],
    ver: "2.6",
  },
  visor: { on: 6.0, off: 9.0, boot: ["PD-01 // VISOR SYSTEM BOOT", "OPTICS ........ OK", "NEURAL LINK ... OK", "PHILLIPS://DIGITAL ONLINE"], jp: "視覚システム起動" },
  anim: { dark: "#05060F", blue: "#4FD2FF", outlineAt: 11.6, logoSolid: 14, floodAt: 9.0, hudAt: 10.2, logoAt: 12.6, glitches: [1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.2, 11.4, 12.5], glitchFrames: 3 },
  // draw-on timing (seconds) for the HUD; used by the motion version later
  hud: { start: 0.0, stagger: 0.06, drawDur: 0.5 },
};
