# Flat 2D endless-zoom portrait: plan (v1)

Picks (skill picker, 22 Nov): build = code-drawn shapes (Remotion SVG); mode = auto stack; words = kinetic title (exact words: ASK);
polish = beat-synced zooms + sound effects; logo = none; subject = original fashion portrait; format = 16:9, 15 s, 30 fps.
Reference: references/flat2d-ref-v1.mp4 (Malika Favre post, screen recording). Grammar only: flat 5-colour palette
(red / maroon / ink / peach / cream), light as negative space, pattern on clothes, endless zoom through a reflection and a window.
Never her character, the theatre or her compositions.

## Skill stack
| Skill | Job in this video | Why |
|---|---|---|
| motion-art-direction | One look: 5 flat colours, negative-space light, no gradients/outlines, restrained secondary motion | style reference supplied |
| shot-composition | 16:9 framing per scene, portal points, title in the left negative space of scene C | landscape format |
| remotion-transitions (custom) | Portal zoom-through (lens -> hotel, window -> room), match-zoom dissolve (her head -> portrait) | the reference's core transition |
| beat-sync-editing | Every zoom lands on a bar line at 96 BPM (frames 150, 300, 450); hotel lights switch on on the beats | music-led loop |
| kinetic-typography | One title, per-word blur-in, dead still, blur-out before the zoom | user ticked "kinetic title" |
| color-motion | Palette tokens in config; scenes stay in one red family | grammar |
| sound-effects | Original synthesised noir-lounge loop + soft whooshes on the zooms, a clink on the glass, -14 LUFS | user ticked sound effects |

## Timeline (450 frames, loops: 450 = 0)
| Frames | Scene | Motion |
|---|---|---|
| 0-105 | A portrait, hotel reflected in her sunglasses | slow push on the lens (1 -> 1.08); light sweep across the lenses 52-78; earring settles |
| 105-150 | zoom through the near lens (x10.9, ease in-out cubic on a log scale) | lands on bar 3 |
| 150-255 | B art-deco hotel at dusk, cream sun | push on the lit window; birds cross; windows light up on beats |
| 255-300 | zoom through the window (x13.3) | lands on bar 5 |
| 300-405 | C she stands in the window with a cocktail | raises the glass 318-352; TITLE 322-392 (left) |
| 405-450 | zoom into her head (x3), portrait dissolves in over the last 45% | lands on frame 0 = seamless loop |

Render speed: ~3 frames/s here (61 frames in 20 s while the shoe renders), so the full 15 s takes about 2-3 minutes.

## v2 (22 Nov): user's new direction
"a person designing something on their PC in a 3D motion world and then it zooms out back to the person. And the logo Phillips
digital with the same colour palette as the reference." Logo: inputs/phillips-digital-logo-scene.jpg (user's file), cut into
recolourable masks in public/flat2d/ (circle, p., wordmark, services line) -> cream circle, ink p., cream wordmark, peach line.
| Frames | Shot |
|---|---|
| 0-75 | designer at the desk, screen-lit profile (cream negative space), big wall shadow; she clicks (beat 3); push 1 -> 1.06 |
| 75-113 | zoom into the monitor (x3.3), lands on beat 6 |
| 113-263 | flat-shaded 3D world (real projection, palette shading, infinite floor): shapes pop on beats 6-8, her cursor drags the cube, a ball rides a keyframe curve, timeline playhead |
| 263-300 | zoom back out to the designer, lands on the bar |
| 338-352 | the screen's deep red floods the frame (iris from the monitor) |
| 350-450 | logo builds: circle springs, p. rotates in, wordmark rises, services line blurs in; holds |
Bugs fixed: BLEED rects used w/h (never drew); 3D pitch sign; back-face culling; light moved to the camera side.
