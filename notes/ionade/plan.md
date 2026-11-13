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
| 1-44 | 0-1.5 s | Close-up at the rim: ice cubes fall in slow motion (released f2, f11, f20, f29; land f14, f23, f32, f41); the camera follows them down the glass | a clink per cube |
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

## Camera (v2, user request)
"A camera on a spline that goes from the top to bottom of the glass and rotates, starting on a close-up of the ice falling in,
to the end shot." CFG["cam_path"] in ionade_pour.py: a Catmull-Rom spline around the glass from the left (clear of the pouring can):
close at the rim (f1) -> down the glass following the ice (f34) -> low and close through the pour, the soda rising past the lens
(f70-104) -> pulls out to the front end shot (f146), settled for the logo. A curved orange backdrop wraps the whole set so every
angle has orange behind the glass. Ice falls at a quarter of real gravity (slow motion) so it reads.

## Edit (v3, user request: "use 2 cameras from different angles to cut in and out scenes of the pour")
Camera A = the spline; camera B = two pour angles. Timeline markers bound to cameras do the cuts (farms honour them):
| Frames | Camera | Shot |
|---|---|---|
| 1-45 | A | close at the rim, slow-motion ice, following it down the glass |
| 46-63 | B | the IONADE can lip: the glossy orange stream peeling off down into the glass (jolt as it hits) |
| 64-83 | A | low and close: the soda and foam rising past the lens |
| 84-99 | B | top-down into the glass: the stream plunging past the floating ice into a ring of foam |
| 100-200 | A | holds low, then whips out (f106-128) to the end shot; a small push as the logo lands (f142); 2.6 deg roll through the orbit |
