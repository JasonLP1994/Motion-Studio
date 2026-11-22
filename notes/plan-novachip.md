# NOVACHIP ident (placeholder brand), Blender, 16:9, 9 s

v1 (single chip, one orbit) was rejected as "boring / very basic". v2 is built to show off the new Blender skills:
`scripts/blender/novachip_ident.py` (copy of `work/blender/chip/ident2.py`), Eevee on CPU, 1280x720, 24 fps, 216 frames.

| Shot | Frames | What | Skills |
|---|---|---|---|
| Fly | 1–60 | Camera skims down a glowing lane of a seeded procedural circuit-board city (resistors, capacitors, ICs, towers), cyan pulses race along copper traces, haze, DOF, motion blur | procedural-modeling, materials, vfx-fx, camera-cinematography |
| Crane | 61–108 | Crane up reveals the die (144 cores) as an energy ripple ring expands from the centre | lighting, materials (driver-animated shader) |
| Assemble | 109–156 | Heat-spreader lid spins down and locks at f140 with a small overshoot; spark particles with gravity | hard-surface, physics-sim |
| Logo | 157–216 | NOVACHIP + "BUILT AT THE SPEED OF LIGHT" light up on the brushed lid; an area-light sweep crosses it; bloom | lookdev, compositing, rendering |

Look: near-black PCB, copper traces, cyan + amber accents, AgX Punchy, bloom, SSR, GTAO, volumetric world haze.
Sound: `scripts/chip_audio2.py` (numpy, original): whoosh + ticks, ripple swell, lock impact + spark crackle, logo hit + shimmer.
Name and tagline are placeholders: change `logo.data.body` / `tag.data.body`.

## Render checks
- v2 (renders/novachip-v2.mp4 + -silent): 9.0 s, 1920x1080 (Lanczos upscale from 1280x720), 24 fps. -14.0 LUFS, peak -2.0 dBFS. Lid-lock impact measured at 5.84 s vs picture 5.83 s (f140). Frames checked across the whole video. Measured, not heard.
- Score 8.4/10: layout 8.5, timing 8.5, readability 8.5, polish 8. Weakest: the first second has large near-black foreground blocks filling the frame edges; tagline is small at phone size.
