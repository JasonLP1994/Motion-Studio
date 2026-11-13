# IONADE pour sting: plan (v1)

**Brief (user):** a glass with ice and orange liquid being poured into it, framed and styled like the three drink references
(references/ionade/), then a brand logo swipe across at the end with a "quench thirst" sound, IONADE.
**Logo:** inputs/ionade-logo.svg (user file, auto-traced). Cut-out PNG with the outer cream removed: public/ionade/logo.png.
**Defaults (stated to the user, no objection):** 9:16 1080x1920, about 6.7 s (200 frames at 30 fps), Blender Cycles,
stylised pour (no fluid sim), synthesised sound (ice clinks, pour, fizz, can hiss, whoosh), about -14 LUFS.

## Grammar taken from the references (never their brands)
- Tall fluted highball on a square dark-oak coaster, white marble counter, saturated orange backdrop, a tartan cloth
  in the bottom-left corner, product cans soft in the background (here: plain cans wearing the IONADE logo).
- Camera just above the rim, looking slightly down, about 45 mm on a vertical frame; glass fills ~50% of the height.
- Warm soft key from the left, narrow strip lights behind the glass for edge highlights, liquid glowing from behind.
- Condensation beads on the glass, ice clear with cloudy cores, orange slice on the rim.

## Skill stack
| Skill | Job | Why |
|---|---|---|
| motion-art-direction | one look: bright warm product shot, orange/navy/cream from the logo | ties 3D and logo together |
| shot-composition | 9:16 framing, glass centred low, logo in the upper-middle, nothing in the bottom fifth or right edge | Reels/TikTok safe zones |
| blender-farm-render | Cycles scene, quick preview here, packed farm-ready .blend | user wants render-engine quality |
| color-motion | brand palette (#FA6108 orange, #0B2E7A navy, #FBF5ED cream), AgX grade | logo colours stay exact |
| logo-animation | the real logo file swipes in on a slanted orange band, bolt flash, dead-still hold | brand reveal |
| sound-effects | measured synthesised pass: clinks, pour, fizz, crack-hiss, whoosh, -14 LUFS | "quench thirst" sound |

## Second by second (frames at 30 fps)
| Frames | Time | What you see | Sound |
|---|---|---|---|
| 1-34 | 0-1.1 s | Empty fluted glass; ice cubes drop in from above one by one (f2, f10, f17, f24) and settle with a small bounce; slow push-in | a clink per cube |
| 30-44 | 1.0-1.5 s | An IONADE can tilts in from the top right | can slide |
| 44-104 | 1.5-3.5 s | The orange stream hits, the level rises, foam and bubbles climb, the ice lifts as it floats | pour + rising fizz |
| 104-118 | 3.5-3.9 s | The stream's tail falls, the can leaves | pour tail |
| 118-132 | 3.9-4.4 s | An orange slice drops onto the rim and settles | soft thud |
| 132-142 | 4.4-4.7 s | A slanted orange band whips across, carrying the logo in from the left | can crack + hiss + whoosh |
| 142-150 | 4.7-5.0 s | The logo lands with a small overshoot, the bolt flashes | fizz burst |
| 150-200 | 5.0-6.7 s | The logo holds dead still over the drink; the drink keeps fizzing behind | fizz tail |

## Build
- scripts/blender/ionade_pour.py: the 3D scene (all timings/colours in its CFG block). Renders silent frames.
- Remotion composition `IonadeSting` (src/ionade/): the frames as background + the logo swipe; config in src/ionade/config.ts.
- scripts/sound/ionade_sound.py: the sound, same frame keys.
- Check three stills (f20 ice, f80 pour, f170 logo) before the full preview.
