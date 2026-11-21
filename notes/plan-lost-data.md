# Lost Data → Phillips Digital (16:9, 8 s)

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

## Second by second (30 fps, 240 frames, 100 BPM: 8th = 9 f)
| Time | Frames | What you see |
|---|---|---|
| 0.0–0.3 s | 0–9 | Clean car; readout types in |
| 0.3–0.6 s | 9–18 | White dot-matrix "PD" on the bodywork, flickering |
| 1.2–1.5 s | 36–45 | Full-frame green strobe |
| 1.5–2.1 s | 45–63 | Pixel "P" eats the car in green → whole car floods green → pixel "D" |
| 2.1–2.7 s | 63–81 | Clean, pixel corner brackets |
| 2.7–3.0 s | 81–90 | PHILLIPS DIGITAL dot-matrix flash, alternating frames |
| 3.6–4.2 s | 108–126 | Scanline tear → green strobe with lines |
| 4.8–5.4 s | 144–162 | Pixel "H" + car flood + dot matrix |
| 5.4–5.7 s | 162–171 | Tear + strobe |
| 5.7–6.3 s | 171–189 | Car pixel-dissolves to black |
| 6.3–6.6 s | 189–198 | PHILLIPS DIGITAL glitches in (green pixel type) |
| 6.6–8.0 s | 198–240 | Holds still, "DATA RESTORED" readout |
