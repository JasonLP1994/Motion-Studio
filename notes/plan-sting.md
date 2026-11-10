# Plan: Phillips English logo sting (3 s, 1920×1080, 30 fps, intro/outro)

Brief: video intro/outro, 3 s, confident and clean, one sound-logo hit.
Logo: the user's real file `inputs/phillips-english-logo.jpg`, split by `scripts/split-logo.py` into P, E, bar, PHILLIPS, ENGLISH (transparent PNGs in `public/logo/`; rebuild matches the original within JPEG noise). Never redrawn.
Technique (one): build-on from the bar. Background: soft radial around the logo file's own #0F161E. Logo 640 px tall (59% of frame).

| Frames | Time | What happens |
|---|---|---|
| 0 | 0.00 | Short teal bar stub at centre (first frame isn't empty) |
| 0–10 | 0.00–0.33 | Bar springs to full width (real bar image, revealed from its centre) |
| 8 / 12 | 0.27 / 0.40 | P, then E, rise from behind the bar's top edge (spring, damping 0.78) |
| 18 / 22 | 0.60 / 0.73 | PHILLIPS drops from under the bar; ENGLISH from under PHILLIPS (no overlap) |
| 30 | 1.00 | All landed: whole-logo 2.5% overshoot-and-settle on the impact peak |
| 30–90 | 1.00–3.00 | Dead still hold (2 s) |

Sound (bundled CC0 kit): whoosh peaking 1 frame after frame 22, soft impact peaking 1 frame after frame 30. Level to about −14 LUFS after render.
Motion blur on every move (6 samples).
