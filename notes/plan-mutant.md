# Moving cover: "PHILLIPS DIGITAL" (grammar from the user's MUTANT poster), 16:9, 10 s, 24 fps

Picks (user): 16:9 10 s · masthead PHILLIPS DIGITAL (cover lines written by Claude, for approval) · free female head scan · original soundtrack.
Reference: `references/mutant-poster.jpg`. Taken: acid lime field, black heavy italic masthead behind a chrome head, violet liquid-chrome
spikes and webs with round holes, HUD brackets/crosshair, coordinates, barcode, 4-point stars, numbered counters, orbit ellipse around
an italic title. Not taken: its words, logo, the face itself.

Head: "Female Head Realistic" by recofiv3, CC-BY 4.0, via Objaverse (Hugging Face). Credit in public/models/CREDITS.md.

## Build
- 3D: `work/mutant/mutant.py` (copy `scripts/blender/mutant_cover.py`). Blender Eevee, transparent PNGs. Chrome skin; 13 violet-chrome
  spikes that start flat on the skin and curl off (real geometry rebuilt every frame by a frame handler, constant topology for motion
  blur), webs between neighbouring spikes hug the skin (BVH push-out) with scalloped free edges and a thick liquid rim; holes tear open
  (Voronoi alpha) from f58. Studio reflections come from a procedural world (key softbox, strip, lime bounce, violet card).
  Needs numpy for Blender's Python: `PYTHONPATH=tools/py312` (pip --target, ignored).
- 2D: `src/mutant/` (config.ts + MutantCover.tsx), composition `MutantCover`. Masthead + blade behind the head, everything else on top.

## Second by second (24 fps)
| Time | Frames | 3D | Type |
|---|---|---|---|
| 0–0.7 s | 0–16 | chrome head, chin lifting, first strands on the forehead | top bar draws from the centre, HUD brackets snap |
| 0.7–2 s | 16–48 | spikes grow out of forehead, eye, crown | PHILLIPS DIGITAL letters slice up (2 f stagger), blade cuts down |
| 2–4.5 s | 48–110 | cheek, ear and neck spikes, webs drape | THE SKIN / IS THE / SCREEN, globe draws on, SPECIMEN Nº 001 scrambles, coordinates roll, barcode, stars, counters |
| 4.5–6.7 s | 110–160 | holes tear open in the webs | BEYOND / FLESH slams (f132), orbit ellipse draws, sparkle star pops |
| 6.7–10 s | 160–240 | slow push and turn continue, webs ripple | footer, counters cycle, stars twinkle; final frame = the cover |

## Checks
- Stills v1 (f30/110/200): notes/frames/mutant-stills-v1.jpg. Fixed after: neck spikes made a shelf across the mouth (re-aimed down
  the throat); coordinate roll stopped short of its value (expo easing never reaches 1 → cubic).
