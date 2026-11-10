# Paper cut

Style ID: fx-paper-cut
Best for: A tactile explainer or collage

## Look
The person, cut out with a white sticker edge, stands on a collage of flat paper: a cream backdrop, a tilted kraft rectangle on one side and a yellow paper band across the lower half. Ransom-note letter tiles in mixed colours spell the headline above the head, then a purple wavy scribble draws in just above the hair.

## Specs
Preview is 540x960 (9:16) shown at 0.6x speed; numbers below are real speed at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: same tile size, headline two lines max, yellow band starts at 55% height. 1920x1080: tiles at 0.8x, headline on one line beside or above the head, kraft piece on the opposite side.
- Palette:
  - Backdrop cream #ECE8DC
  - Kraft piece #BEB395
  - Yellow band #E3C206
  - Tiles: purple #6C4FAE, white #F8F7F4, teal #00BBB6, black #0F0A0C, yellow #E3C206, red #D94349
  - Tile letters white on purple, red and black; black on white, teal and yellow
  - Scribble #5A46A8 with a 2 px dark offset line #171009
  - Sticker edge #FFFFFF
- Fonts: tile letters in a heavy geometric sans, uppercase. Default Montserrat Black (900) from Google Fonts. Fallback: "Archivo Black", "Arial Black", sans-serif.
- Sizes at 1080 wide: tiles about 84x80 px, letters 68 px, tile pitch 150 px (big gaps, it reads as spaced letters). For longer words use pitch = min(150, (W - 2 x margin - tile width) / (letters - 1)), and give a space half a pitch. Each tile rotated a random seeded -4 to +4 degrees. Sticker edge 10 px. Scribble stroke 6 px, a smooth wave with 9 points, about 40 px tall, spanning x 144 to 856.
- Layout: line 1 tiles at y 340 to 420, line 2 at y 488 to 568, both centred. Scribble sits at about y 680, just above the top of the hair. Kraft rectangle at the right, about x 630 to 1080, y 470 to 920, tilted about -5 degrees. Yellow band from y 980 down, with a torn, slightly slanted top edge. All paper edges are flat colour (no blur, very light texture at most).
- Timing: tiles pop in left to right, 2 frames apart. Each tile goes from scale 0.3 to 1 in about 4 frames with spring {damping: 9, stiffness: 180, mass: 0.6}, then holds still (no boiling in the preview). The scribble draws left to right on frames 16 to 31 (linear strokeDashoffset). Hold. Exit not shown: 8 frame fade or cut.

## Build recipe
Build paper pieces from seeded irregular SVG polygons. Add gentle texture without blurring text. If a subject cut-out is available, give it a separate white outline from its alpha mask. Otherwise use supplied objects or code-drawn paper shapes without requiring a portrait. Pop letter tiles in with small rotations. Measure the headline with measureText (or fitText) from @remotion/layout-utils so the tile rows never overflow the frame; split into two lines when needed. Use stepped poses for a stop-motion feel; vary only selected layers.

## Check
Do not crop hands or shoulders before cutting out. Keep texture secondary to readability. Make collage motion purposeful rather than shaking the whole frame.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
