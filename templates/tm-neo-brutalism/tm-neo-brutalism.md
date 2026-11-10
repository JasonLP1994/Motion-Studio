# Slam blocks

Style ID: tm-neo-brutalism
Best for: Announcements & punchy headlines

## Look
Bold type, flat colour, thick black borders and hard offset shadows, each block slightly tilted, stacked on a cream dotted-grid page (or over footage). One block lands per spoken beat, or per planned visual beat when silent; reserve the biggest landing (and the only shake) for the final message.

## Specs
Preview is 540x960 (9:16), 60 fps, real speed, standalone with no footage. Numbers below are at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: same type sizes, tighter gaps (32 px), fewer blocks on screen. 1920x1080: sizes x0.8, blocks in a left or right column (about 45% of the width) or a 2-column grid.
- Palette:
  - Page #F6F4F0 with grey dots #D8D4CC (3 px dots on a 48 px grid)
  - Purple #7B52B0, yellow #F4CF08, black #1A1917, white block #FBFAF7
  - Borders and shadows #1A1917; the black block gets a purple shadow #7B52B0
  - Text: yellow on purple, black on yellow and white, white on black
- Fonts: heavy geometric sans, uppercase for headline blocks. Default Montserrat ExtraBold (800) from Google Fonts, or Gilroy ExtraBold if you own it. Fallback: "Archivo Black", "Arial Black", sans-serif. Caption block in Montserrat Bold (700), sentence case.
- Sizes at 1080 wide: borders 6 px, hard shadows 12 px down and right (no blur), corner radius 0. Number tile about 320x340 px with a 230 px numeral. Small word block (FREE) about 550x240 px, text 180 px. Main block about 900x350 px, two lines at 125 px. Caption block about 650x140 px, text 50 px. Hero block about 900x310 px, two lines at 135 px. Speech-bubble icon about 190x170 px. Tilts between -3 and +3 degrees, alternating.
- Layout: stack fills x 60 to 970 (about 6% margins), from about y 260 to y 1540, gaps 40 to 60 px. Text padded at least 40 px inside each block.
- Timing (30 fps): landings in the preview at frames 12, 21, 30, 54 and 117 (hero), icon at 135. Normal block: starts at 1.6x scale with 6 extra degrees of tilt, slams to rest in 4 frames (Easing.in(Easing.cubic)), then settles with a small overshoot over 6 frames (spring {damping: 10, stiffness: 220, mass: 0.6}). Hero block: holds huge (fills the width) for about 4 frames, slams in 1 to 2 frames, then shakes about plus or minus 16 px, decaying over about 8 frames. Icon pops from 0 to 1 scale over 4 frames with the same spring. Hold.

## Build recipe
Build blocks as HTML/SVG with editable text. Start at 6 px borders and 12 px hard shadows on a 1080-wide canvas, then scale with output size. Fit each block's text with fitText/measureText from @remotion/layout-utils so headlines never overflow their block or the frame. Use yellow, purple, cream and black. Derive movement from the frame, with a short overshoot and settle. Shake only on the hero landing.

## Check
Keep the first frame useful. Do not give every word equal emphasis. When narration is supplied, match blocks to its actual timing. For silent work, use the agreed beat plan.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
