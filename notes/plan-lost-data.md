# Lost Data → Phillips Digital (16:9, 16 s, 4 scenes)

v2 changes (user): palette green / black / yellow only; three more photos cut out (`inputs/green-car-side.png`, `-rear`, `-front` → `scripts/car/cutout_ground.py`, ground line drops the floor reflections and refills tyres/diffuser) used as scenes; length 16 s.

Picks: Words = PHILLIPS DIGITAL + small data readouts · Format = 16:9, car turned to point right · Background = reference-style gradient (car cut out) · Polish = glitch beat + SFX, engine-style rumble.
Inputs: `inputs/green-car-top.png` (user's photo, untouched). Cut-out by colour key: `scripts/car/cutout.py` → `public/car/car.png` + `mask.png`.
Reference: `references/car-ref.mp4` (screen recording of a "lost data" glitch piece). Measured at full frame rate: an 8.6 s loop; a still top-down car on a black→light-grey gradient; glitch bursts of 3–8 frames every 0.5–1.3 s (~103 BPM) that flicker on/off with the clean frame: blocky pixel glyphs eating the car in the accent colour with dither, whole car flooded with the accent colour, white dot-matrix symbols on the bodywork, a 1-frame brand flash, full-frame accent strobes, white scanline tears, tiny data readouts and pixel corner brackets. Grammar only; no reference words, logos or car.
Note: the car maker's badge stays as photographed; no maker logo or name is added.

## Skill stack
| Skill | Job | Why |
|---|---|---|
| motion-art-direction | Black / white / acid-green accent (the car's own green) on a black→grey gradient | Reference grammar, recoloured to the car |
| shot-composition | Car turned to point right, ~70% frame width, centred, soft floor shadow | 16:9 from a square vertical photo |
| object-separation (colour-key route) | Car silhouette mask for the fill/glyph effects | Effects follow the real car shape (no SAM install needed) |
| kinetic-typography | Pixel dot-matrix PHILLIPS DIGITAL flash + end wordmark, typed readouts | Words pick |
| beat-sync-editing | Every burst starts on an 8th at 100 BPM (9 frames) | Reference cadence |
| shader-glsl-style glitch (CSS/SVG) | Mosaic pixelation, scanline tears, dither, strobes | The glitch kit |
| sound-effects | Original glitch beat + engine-style rumble made in code, bundled CC0 glitch sounds on bursts, -14 LUFS | Sound picks |

## Second by second (v2: 30 fps, 480 frames, 100 BPM, 8th = 9 f)
| Time | Frames | Scene | Bursts |
|---|---|---|---|
| 0.0–3.6 s | 0–108 | Top view | PD dots, green strobe, pixel P, yellow flood, brackets, pixel H, tear into the cut |
| 3.6–7.2 s | 108–216 | Side profile | pixel I, PHILLIPS DIGITAL flash, yellow strobe + lines, pixel L, flood, PD dots, tear |
| 7.2–10.2 s | 216–306 | Rear | pixel L, green strobe, brackets, pixel I, brand flash, tear |
| 10.2–12.9 s | 306–387 | Front close-up (full frame) | pixel P, flood, yellow strobe + lines, pixel S, PD dots |
| 12.9–13.5 s | 387–405 | Front pixel-dissolves to black | |
| 13.5–16.0 s | 405–480 | PHILLIPS DIGITAL green pixel wordmark glitches in, holds; "DATA RESTORED" in yellow | low boom |
The pixel letters across the scenes spell P-H-I-L-L-I-P-S.
v3: white digital annotations (callouts with coordinates, reticles, dimension lines, + clusters), 8 per scene at seeded-random points and half-beat times, spaced >= 220 px apart, hidden during strobes and tears.
v4: ASCII x dither pattern frames (grammar from the user's 3 reference stills): scripts/car/make_patterns.py rebuilds each view from stepped regions of 1-bit ordered dither, ASCII by brightness, checkerboards and solid blocks (green/yellow on black); 2-3 per scene as 'pattern' (car swaps to its pattern) or 'patternZoom' (full-frame punch-in on a crop).

## v1 render check (renders/lost-data-v1.mp4)
- 16.0 s, 1920x1080, 30 fps. Frames checked across the whole video (3 fps sheet): all 4 scenes, every burst type, pattern swaps and punch-ins, dissolve, wordmark hold.
- Loudness -14.0 LUFS, peak -1.8 dBFS (measured gain + limiter on the premaster). End boom placed at frame 405 (13.50 s) in code; the rumble's wobble makes its onset hard to isolate by measurement. Measured, not heard.
- Score 8.4/10: layout 8.5, timing 8.5, readability 8, polish 8.5. Weakest: "DATA RESTORED" under the wordmark is small; the yellow flood is a flat fill.
