# Material loop

Style ID: material-loop
Shown as: Material loop (ManvsMachine-inspired)
Best for: Brand idents, product reveals, logo stings, loops for social, backgrounds for a single bold word.

Grammar learned from ManvsMachine (London studio; Nike, Apple, Squarespace, Purple, B&O). Sourced from trade press, award entries and the studio's own pages:
- Abstract, metaphorical CG: Nike Air Max 2017 explores air and the negative space it occupies.
- An algorithmic structure drives every form and movement (iMac Pro, "Algorithmic Architecture").
- Forms move with a logic that feels biological, not mechanical.
- Material worlds are made for each subject (sand and powder textures for Squarespace).
- Sound built from the subject: recorded footsteps re-pitched into the melody and rhythm.
- A balance of tech and beauty.

The 2D translation below is mine. Take the grammar only: never copy their films, products or type.

## Look
- One abstract hero form on a bold, flat colour field. Nothing else in the frame.
- Tactile material: cylindrical shading (dark, light, mid, dark across each piece), soft drop shadows, a soft key light on the field (radial gradient, top left).
- Shallow depth of field: pieces "behind" are smaller, paler and slightly blurred.
- Type: one short word, heavy sans (Inter 800), tight tracking (-0.04em), dark on the colour field, revealed by a mask.

## Motion
- One rule, many copies: every rod follows the same sine rule with a phase offset by its angle, so waves travel around the form. Change `twists` for more waves.
- Seamless loop: all motion uses loop = frame / duration, so the last frame flows into the first.
- Beat accents: at every beat (bpm in config) the form squashes in 3 frames and eases back over 80% of the beat. With music, set the bpm to the track's; with sound design, put a hit on each accent.
- Word reveal: slides up out of a mask over 18 frames, Easing.out(cubic). No bounce.

## Specs
- 16:9 1920×1080, 30 fps, 6 s loop, 120 bpm (an accent every 15 frames).
- 56 rods on a ring of radius 250, seen at an angle (y × 0.55), rod length 150 ± 90, tilt ±32°.
- Palette: field #FF5B2E, fieldLight #FF8A5C, rod light #FFF4EA, mid #F2D7C6, dark #B0705A, shadow rgba(90,20,0,0.35), text #1B0C06.
- Sort pieces by depth every frame so near ones draw on top.

## Build
1. Copy MaterialLoop.tsx into src/ and register it (see src/Root.tsx).
2. Change the material through the palette (chrome: greys with a hard white highlight; clay: matte warm tones; glass: low opacity plus a white edge).
3. Change the form by changing the rule: positions on a ring, grid or spiral; length, tilt or scale driven by sin(phase).
4. For a product: arrange the rods around the product image (a cut-out PNG in public/), or let the rule build the product's silhouette.
5. For true materials and lighting (cloth, liquid, glass), use @remotion/three. Budget more time.

## Known pitfalls
- More than one idea in the frame breaks the look. One form, one word.
- A loop that doesn't wrap jumps once per cycle: never use frame directly, always the loop value.
- The word reveal plays once, so a looped copy pops the word every cycle. For a social loop, show the word from frame 0, or reveal it and hide it again inside the loop.
- Linear motion feels mechanical. Use sine phases and eased accents.
- A per-element CSS blur on many pieces slows renders: blur only the far pieces.
- Gradients that rotate with each piece make the light seem to move: shade across the width (cylindrical) so it reads as consistent.

## Copy prompt
See prompt.txt in this folder.
