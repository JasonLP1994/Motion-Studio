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

## v2 structure (user: "cinematic close-ups following the growing spikes; text only readable at the end; end shot = the reference's angle")
| Time | Frames | Shot | Type |
|---|---|---|---|
| 0–1.5 s | 1–36 | CAM_Eye: hovers off the skin, a strand grows out over the eye and shoots across frame | none |
| 1.5–3 s | 37–72 | CAM_Cheek: spike curling off the cheek | none |
| 3–4.5 s | 73–108 | CAM_Crown: crown spikes | none |
| 4.5–6.2 s | 109–148 | CAM_Neck: neck webs, holes tearing open | none |
| 6.2–8.5 s | 149–205 | CAM_Hero pulls back to a low angle under the chin (head thrown back -44°), last spikes finish | top bar, HUD, masthead slices up, blade, cover lines, globe, specimen, coords, barcode, stars, counters |
| 8.5–10 s | 205–240 | hold, slow drift | BEYOND / FLESH slam, orbit, sparkle, footer; final frame = the cover |
Close-up cameras live in the head rig and are keyed from the real spike curves (they follow the growth). Spike start frames re-timed per shot.
Fixes: imported head had every vertex split (1,184,766 -> 201,377 after merge) which made the chrome look faceted; neck stretched so its cut
end stays below frame; area-light shadow bias; masthead size cap raised once the condensed font loaded (fills 1790 px); blade starts at the
masthead baseline. Stills: notes/frames/mutant-stills-v2.jpg (f54 / f174 / f229).

## v3 (user: "more saturation, pop like the reference"; "text glitches in and out, glitches out at the end and stays out, head central for the end shot")
- Saturation: webs pushed to a deeper violet (ramp 0.4/0.04/1.0, more violet coverage, emission 0.14), stronger lime bounce and violet card
  in the reflections, field #C8FA14, 3D layer graded saturate(1.35) contrast(1.08) in Remotion (`grade3d` in config).
- Glitch: both type layers (masthead/blade behind the head, everything in front) run through <Glitch>: RGB-split drop shadows
  (#FF2BD6 / #00E5FF), 7 sliced bands that jump sideways, random blink-off. Bursts as elements arrive (f150, 158, 176, 184, 198) and two
  flickers in the hold (f209, 216); glitch-out f222-230, then the type is gone for good.
- End: CAM_Hero pushes in from f222 to f240 and re-aims so the face lands in the centre; final frame is the chrome head alone.
- Stills: notes/frames/mutant-stills-v3.jpg (f212 hold / f224 glitch-out / f239 final, half-size 3D).

## v4 (user: end shot straight on, head central, "not looking through the nose"; then glitch to black-and-white solids and a small PHILLIPS DIGITAL logo)
Now 12 s (288 frames). 3D renders to f258.
| Time | Frames | Shot |
|---|---|---|
| 9.25–9.4 s | 222–226 | type glitches out (cut hidden inside it) |
| 9.4–10.4 s | 226–249 | CAM_End: lives in the head rig, straight on to the face, head centred, slow push |
| 10.4–10.75 s | 249–258 | head glitches into flat black-and-white solids (threshold / inverted / colour frames in a fixed rhythm, sliced bands) |
| 10.75–12 s | 258–288 | black end card: small logo glitches in (orbit ellipse + 4-point star mark, PHILLIPS DIGITAL in Barlow Condensed Black Italic, rule + ART / MOTION / IDENTITY), holds |
Sound extended: heavy glitch on the B/W flicker, logo hit (sub + bright ping) with a clean tail.
Stills: notes/frames/mutant-end-v3.jpg.
- Ending zoom-out: CAM_End pulls back (-2.9 to -4.8) during the B/W flicker so the whole spike form sits centred before the logo card; slice jumps halved. Still: notes/frames/mutant-bw-v2.jpg
