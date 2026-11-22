# Lime oil phone case reveal (9:16, 10 s, Blender Eevee)

Picks: Option A (Blender Eevee), phone case, vertical 9:16, 10 s, lime green metallic-plastic "like lime green oil". No words on screen (none requested). Reference: `references/next-ref.mp4` (phone case builds itself, ring clicks in, macros, hero; grow effect from a paid add-on, rebuilt here ourselves).
Scene: `scripts/blender/lime_case.py` (copy of `work/blender/case/case.py`). 720x1280 render, upscaled to 1080x1920.

| Time | Frames | Shot |
|---|---|---|
| 0–3.5 s | 1–84 | Case builds itself like the reference: side rims shoot up as torn-tipped strands, the back fills in behind with a ragged edge, the top rim closes, the camera bump forms last (shared growth field in shader + geometry nodes, noise-torn front, edge curls up and settles) |
| 3.5–5 s | 85–120 | Phone slides into the finished case (f88–106; no phone during the build); MagSafe ring swings in and clicks (overshoot), macro |
| 5–6 s | 121–144 | Camera bump / lenses macro, shallow focus |
| 6–7 s | 145–168 | Side buttons + edge macro |
| 7–10 s | 169–240 | Hero: the case turns slowly in the strip lights |

Engraving: "PHILLIPS / DIGITAL" cut into the back below the ring in Special Elite (typewriter, Apache 2.0, `public/fonts/SpecialElite-Regular.ttf`).
Look: lime base with flakes under a glass clear coat, fake oil-slick hue shift at grazing angles (lime → acid yellow → teal), dark graphite cyclorama, softbox + two strip lights + top rim, gradient studio environment for the oily reflection, Standard / Medium High Contrast, exposure -0.35.
Iterations: v1 pale mint + jagged GN delete edge + cameras too close → v2 shader sweep, reframed → v3 darker oily but forest green → v4 yellow-lime + gradient environment.

v5 (user: "case should build itself like the reference, no phone already in the scene" + reference stills of the torn growth): growth field = rims lead, back fills, lip, bump last, noise-torn edge, GN curl 0.035 along the normal; no glow edge; phone hidden until f88 then slides in.
v6 (user: keep the glow but follow the growth, smoother growth, smoother + thicker case, background a darker green like the case): eased growth clock (smoothstep), one coherent front (rims lead slightly, lip, bump last), gentle wave edge, softer curl, thin glow line on the leading edge; thicker shell (walls ~0.023, back 0.018), bigger bevels, finer remesh + smoothing pass before the engraving; matte dark-green cyclorama (low specular) + lower environment strength.
- v7 (user: "light green, infinite floor, growth too clean, match the reference, glowing edges"): light green infinite cyclorama (self-lit, zero specular, world matched, no horizon). Growth rebuilt from the reference studied frame by frame: starts as a chip at one bottom corner, rim strands lead (0.76x), lip 0.82x, back lags with a torn noisy U-front (1.0x + 0.12), camera bump last; glow band rides the growth front and switches off when the shell completes. Stills: notes/frames/case-grow-v6.jpg (f20/32/44/56).
- v8 (user: "why two glowing lines, just one, only on the part that is growing"): the hollow case's inner wall had its own faster clock, so its glowing front showed through ahead of the outer one. Arrival now depends on x,y only (inner, outer and rim at the same spot arrive together) with a smooth rim lead, giving one continuous U-shaped torn front; clock shortened to 2.15 so the bump follows without a gap. Stills: notes/frames/case-grow-v7.jpg.
- v9 (user: "cinematic close ups and camera angles, final reveal at the end"): the build is now shown only in close-ups so the whole case is held back: CAM_Chip f1-22 (70mm macro on the corner chip), CAM_Rim f23-48 (rides up beside the racing rim strand), CAM_Sweep f49-84 (over the top as the last front and bump close), Ring f85-120, Bump f121-144, CAM_Engrave f145-166 (50mm slide across PHILLIPS DIGITAL, f2.8), Edge f167-186, CAM_Hero f187-240 (pull back from tight to the full hero frame while the product turns). Stills: notes/frames/case-cams-v3.jpg. First tries: rim camera lagged the strand and the engrave shot was far too tight; fixed from the measured growth-front position.
