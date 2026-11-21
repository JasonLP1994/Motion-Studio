# Christmas snow globe: plan (v2: blue palette, building stills)

Brief from the user: a mini Christmas diorama in the style of their reference (soft clay toy tiles), inside a
snow globe, snow falling. Wide 16:9, 10 s seamless loop, no words, music box + sparkles. Blender Cycles; final
on the farm (user's choice), previews here.

## Style taken from the reference (grammar only, no copied content)
- Chunky rounded square tiles (about 12% corner radius, small gaps), raised by different heights, 2x2 / 3x3 grid.
- Soft clay / vinyl-toy material: matte, faint sheen, slight subsurface glow, no hard edges anywhere.
- Big readable props, slightly oversized versus the tiles (a toy, not a real scene).
- Isometric-ish three-quarter view, about 35 deg down, long lens (low perspective).
- One pastel colour family per scene, a flat matching backdrop, soft shadows, no dark corners.

## Christmas version
- Palette (user: "the same style in blue"): ONE blue family like the reference scenes are one colour each.
  backdrop #BFD9F2 -> #D9E9F8 soft gradient; tiles #8DBDEB / #A9CFF2 / #6FA6DD (varied blues); cabin #5E93D1 with
  white snowy roof; pines #3F78C2 / #5A92D6 / #7FB0E6; snowman, snow #F4F8FD with icy-blue shade #DCE9F7;
  presents and train in blues and white; base #4A7FC4 with a white band. ONE warm accent only (like the yellow
  tile / path in the references): window + lantern glow #FFD27A and a few small gold touches #F2C14E.
  Colours, roughness and sizes live in one config block in the scene script.
- Inside the globe on a 3x3 grid of rounded snow tiles (heights vary 0-12%):
  log cabin with snowy roof, glowing windows and chimney; three snowy pines (one decorated); snowman;
  presents; candy canes; lantern; a little train on a ring track round the tiles.
- Models: Kenney Holiday Kit (CC0, inputs/models/kenney-holiday-kit/, local only), rounded off in Blender
  (bevel + subdivision) and re-materialed with one shared clay shader. Tiles, globe, base, snow: built in code.
- Globe: thin clear glass sphere (soft reflections, no caustics) on a rounded blue base with a white band.

## The 10 s loop (300 frames at 30 fps; frame 301 = frame 1)
| Time | What you see | Motion |
|---|---|---|
| 0-10 s | The globe fills ~70% of the frame height, centred slightly low; soft backdrop | Camera sways around the globe ±12 deg (one sine cycle in 10 s), so it loops |
| 0-10 s | Snow drifts down inside the globe, slow and swirly | Each flake falls a whole number of globe-heights in 10 s and wraps, so the loop is seamless |
| 0-10 s | The train goes once round the ring track | Exactly 1 lap in 10 s |
| 0-10 s | Window glow and tree lights twinkle softly; chimney puff | Periods of 2.5 s / 5 s (divide 10 s) |
| 0-10 s | A few sparkles glint on the glass | Timed to music-box notes |

## Sound
An original music-box melody synthesised in code (no paid music), 96 BPM = exactly 4 bars in 10 s, so it loops.
Soft sparkle chimes on the glints, a quiet train chug. Mixed to about -14 LUFS, true peak below -1 dBTP.

## Delivery
3 stills for approval -> 2-3 s motion proof -> full 10 s preview (lower quality here) -> packed farm .blend
(1920x1080, frames 1-300). Renders and models never go to GitHub.

## Note
The shoe HQ render is using this machine's CPU until about 22 Nov. Test stills for this project slow it a little.

## Update (21 Nov): current state and render queue
- Now: 15 s seamless loop (450 frames at 30 fps), camera orbits 360 deg once per loop, connected blue clay town, no train,
  one hidden softbox above-right (plastic highlights), shadow sun on the floor only (soft back shadow), colour grade in
  config (+15% saturation on blues). Soundtrack: renders/audio/snow-globe-sound-v3.wav (original waltz, 15.0 s, -14 LUFS).
- Queue (user, 21 Nov): 1) finish the 3 max-quality stills v5 (globe-hq5.blend, frames 1/151/301, 100% / 128 spp);
  2) render the FULL loop "highest possible but quickest": time a few frames at 100% with low spp + OIDN + --persistent,
     pick the best quality that finishes in a sensible time, run with scripts/denoise/render_resume.sh as TRACKED
     background tasks (2 h each, chained) into renders/frames/snow-globe-full-v1/, then mux the sound -> renders/snow-globe-full-v1.mp4,
     check the loop seam, score, send;
  3) then resume the shoe: bash scripts/denoise/render_resume.sh renders/farm/shoe-slime-v5/shoe-slime.blend renders/frames/shoe-slime-local-hq-v1 1 600 50 32
- 21 Nov 03:27 UTC: stills v5 done (~38 min/frame at 128 spp; sent). Speed test: 100% / 16 spp + OIDN = ~5 min/frame and
  visually matches 128 spp (mean diff <1/255; reflections a touch softer). --persistent saved almost nothing.
  FULL render running at 100% / 16 spp into renders/frames/snow-globe-full-v1 (ETA ~37 h, about 23 Nov 16:00 UTC), shoe after.
