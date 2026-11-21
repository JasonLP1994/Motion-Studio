# Red Glitch → Phillips Digital (Ferrari photos, 16:9, 19.2 s)

v2 (user: "white background", flat paper white): cars cut out with SAM 2 (`facebook/sam2.1-hiera-large`, image mode, box + paint points; `scripts/ferrari/sam_cutout.py` run with `.object-separation/bin/python`, `HF_HUB_DISABLE_XET=1`; `scripts/ferrari/keep_largest.py` drops floor-reflection specks). Paper #EEECE7 + faint grain; graphics in black ink, red accent; split = red/black silhouette misregistration; negative = B&W; dissolve fades to paper; red wordmark on paper.

Brief (user): a Ferrari version in the reference's own colours (red / black / white), "more crazy, more glitchy, more wild". Plus "node" frames like the user's Lost Data node still, saying FERRARI (text only; no maker logo added). Inputs: `inputs/ferrari-{top,side,front,toprear,wheel}.png` (user's images, untouched; derived files in ignored `public/ferrari/`).
Reference: `references/car-ref.mp4` (same file as LostData, checksum match) + the user's ASCII x dither stills + the node still.

## Skill stack
| Skill | Job | Why |
|---|---|---|
| motion-art-direction | Red / black / white only; every effect kept in palette | Reference colours |
| beat-sync-editing | 100 BPM, bursts on 8ths, zoom punch every 8th, montage on 16ths | "More wild" |
| shader-glsl-style glitch (CSS/SVG) | Red/white split, macroblock shuffle, pixel smears, B&W negative, tears, strobes, jitter bands every few frames | Glitch kit, denser |
| kinetic-typography | Pixel letters P-H-I-L-L-I-P-S, PHILLIPS DIGITAL flashes, wordmark, typed readouts | Words |
| shot-composition | Full-frame photos (cover; side photo fit to width) | Photos are already 16:9 studio shots |
| object-separation (colour key) | Red paint masks for the floods | Effects follow the bodywork |
| sound-effects | Harder original beat + rumble (code), bundled CC0 glitch sounds, -14 LUFS | Sound |

## Timeline (30 fps, 576 frames)
| Time | Frames | What |
|---|---|---|
| 0–2.7 s | 0–81 | Top view: split, PD dots, pixel P, shuffle, red strobe, paper pattern, flood, smear, negative, pixel H, tear |
| 2.7–3.9 s | 81–117 | Node frame: dimmed top view, white edge bars, NODE_1–5 red tags + wires, grey FERRARI block, code text |
| 3.9–6.6 s | 117–198 | Side |
| 6.6–9.3 s | 198–279 | Front three-quarter |
| 9.3–12.0 s | 279–360 | Top-rear |
| 12.0–14.1 s | 360–423 | Wheel close-up |
| 14.1–16.5 s | 423–495 | Rapid montage: a photo every 16th, each with a random glitch |
| 16.5–17.0 s | 495–510 | Pixel dissolve |
| 17.0–19.2 s | 510–576 | Red PHILLIPS DIGITAL wordmark glitches in and holds, "DATA RESTORED" |
