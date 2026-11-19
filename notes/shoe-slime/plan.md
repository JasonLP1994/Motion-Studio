# SLIME SHOE ident: plan (v1)

**Brief (user):** a shoe that warps, waves and liquifies like a Cinema 4D effector, then becomes a whole object through
many close-ups from different angles of the shoe coming together, looking like Venom slime. Once whole it turns into a
solid object, then colours into a black-and-white shoe design. Backdrop like the reference (references/shoe-slime/).
**Answers:** original shoe built in Blender (no brand), 16:9 1920x1080, about 12 s (360 frames at 30 fps), shoe only
(no text), synthesised slime sound at about -14 LUFS.

## Grammar taken from the references (never their content or watermarks)
- ref-slime: jet-black goo, mirror-wet with sharp white highlights, thick ropes and necking strands.
- ref-backdrop: dark charcoal set with a lighter haze behind the subject, glossy dark floor with reflections,
  warm orange accents on edges. (The orange becomes rim light and the glowing colour wipe.)

## Skill stack
| Skill | Job | Why |
|---|---|---|
| motion-art-direction | one look: black venom slime on charcoal, warm orange rim, ends black & white | ties the stages together |
| blender-farm-render | Cycles scene, quick previews here, packed farm-ready .blend | path-traced wet reflections (checks.md) |
| shot-composition | 16:9 product framing, six shots, focus on the near surface | close-ups must read |
| beat-sync-editing | cuts on the landings (each part arriving), the SET hit, the wipe | cuts with a cause |
| particle-system / threejs-animation (as reference) | the displacer field, churn noise, tendrils and drips | C4D effector look in geometry nodes |
| color-motion | AgX Medium High Contrast; slime -> satin black -> black & white | colour change is the payoff |
| sound-effects | squelches, strand stretches and snaps, a hard "set" hit, a shimmer on the wipe; -14 LUFS | slime sound |

## Second by second (frames at 30 fps)
| Frames | Time | Shot / camera | What you see | Sound |
|---|---|---|---|---|
| 1-40 | 0-1.3 s | WIDE 3/4 front, slow push | the slime shoe; a displacer ripple field sweeps heel -> toe through it | low wet churn, a rising squelch |
| 40-62 | 1.3-2.1 s | WIDE | it sags and liquifies into a puddle, surface boiling | gloopy melt |
| 62-76 | 2.1-2.5 s | WIDE | the parts burst up and back in slow motion, strands stretch and snap | stretch + snaps |
| 77-116 | 2.6-3.9 s | SOLE close-up, low | tendrils pull the outsole (lands f106) and midsole (f112) in, the puddle is sucked up | suck + splat x2 |
| 117-161 | 3.9-5.4 s | TOE close-up | the upper descends on ropes of slime and seals onto the sole (f156) | squelch + splat |
| 162-206 | 5.4-6.9 s | HEEL close-up, behind 3/4 | the heel counter swings in and clamps (f199) | stretch + splat |
| 207-251 | 6.9-8.4 s | LACES from above | the tongue slides in (f236), the laces whip down over it (f248) | lace whips |
| 252-284 | 8.4-9.5 s | HERO orbit begins | the whole slime shoe, one last wave runs through it | swell |
| 285 | 9.5 s | HERO (jolt) | it SETS: wet slime -> hard satin black, the drips snap back | hard hit |
| 293-326 | 9.8-10.9 s | HERO orbit | a glowing orange line wipes heel -> toe, leaving the black & white design | shimmer + sizzle |
| 327-360 | 10.9-12 s | HERO orbit settles | hold on the finished shoe, floor reflection | tail |

## Build
- scripts/blender/shoe_slime.py: the whole scene (all timings, colours and cameras in its CFG block).
- Preview frames here (low samples, ffmpeg denoise), sound from scripts/sound/shoe_slime_sound.py, mux in ffmpeg.
- Farm: packed .blend in renders/farm/shoe-slime-v1/ (never GitHub), 128 spp + motion blur.

## Revisions after feedback (lighting, materials, logo)
- Lighting: the old key/fill/rim lights are gone. Now one emissive gradient softbox above the shoe (magenta → orange → yellow → cyan → blue, hidden from camera) makes a rainbow pool and reflections, plus one very dim omni (0.22 W) close to the shoe.
- Atmosphere: haze volume, ground mist (domain-warped noise) and drifting dust on a mottled concrete cyclorama.
- Shoe materials (procedural, texture depth faked with bump): breathable mesh vamp, perforations, grained leather toe cap and eyestay with double stitching, suede mudguard, speckled foam midsole, knit tongue with a woven label, metal eyelets, flat laces.
- Logo: an original "OOZE" mark (scripts/blender/assets/ooze_logo.svg), printed on both sides, the heel and the tongue label.
- Preview: 33% / 16 spp, denoised with ffmpeg nlmeans and scaled to 1080p. Farm build: 128 spp + OIDN + motion blur.
