# Brief: playful pixel-art motion piece (2D)

Status: brief done, next checkpoint = plan + three style frames.

## Answers (project-brief checklist)
| Item | Answer | Source |
|---|---|---|
| Kind | 2D motion design | user message |
| Purpose | Portfolio / showreel | round 1 |
| Platform | YouTube / website, 16:9 (1920x1080) | round 1 |
| Length | 10-15 s | round 1 |
| Type of piece | Started as kinetic typography, then: "I actually want to do some visual designs too" -> mostly visuals, few words | rounds 1-3 |
| Words | Few; exact words not given yet (ask, or propose 2-3 options for approval) | open |
| Feeling | Playful | round 2 |
| Reference | references/pixel-poster-ref.jpg (user: "I'm liking this pixel art vibe") | upload |
| Colours | Claude suggests 2-3 palettes in the style frames | round 2 |
| Visual elements | Bouncy shapes + morphs; patterns + textures | round 3 |
| Motion | Springy squash & stretch; snappy cuts on the beat | round 3 |
| Sound | Original music + SFX, -14 LUFS, plus a silent copy | round 3 |
| Extra versions | No preference -> default: thumbnail / poster frame | round 4 (default) |
| End card | No preference -> default: shapes resolve into the PHILLIPS DIGITAL logo | round 4 (default) |
| Credits | No preference -> default: only where a licence needs it | round 4 (default) |

## Reference grammar (take the style only, never Nike's logo, words, product or layout copy)
Giant blocky pixel masthead across the top in one bold colour; hero object drawn as chunky flat-colour pixel art with black
outlines and stepped shading, floating with a pixel shadow; off-white page; small editorial text blocks, a barcode, a vertical tab;
big pixel type line at the bottom. Restricted palette, whole-pixel positions, no anti-aliasing.

## Direction (draft for the plan checkpoint)
- Studio template to build on: `templates/tm-pixel` (pixel grid, restricted palette, Pixelify Sans / Press Start 2P / Silkscreen,
  nearest-neighbour rendering, whole-pixel steps) + the reference's editorial poster layout.
- Playful squash & stretch on a pixel grid: animate on whole-pixel steps (stepped, "on twos"), overshoot and bounce in pixel units.
- Visuals lead: pixel blobs/shapes that morph and pop on the beat, pixel patterns (checks, stripes, dither) as transitions,
  a few words in chunky pixel type; ends with the shapes snapping into the PHILLIPS DIGITAL logo.
- Skill stack (draft): motion-art-direction, pixel-art-style, kinetic-typography (few words), beat-sync-editing, shot-composition,
  logo-animation (ending), sound-effects + original music, color-motion (palette). Finish: crisp (no grain blur on pixels).
- Pipeline: Remotion (2D, renders fast) at 1920x1080; no AI upscale (pixel art must stay nearest-neighbour); finishing kept to
  colour only (no grain, blur or CA on pixel edges).

## Open questions
1. The few words: user's exact words, or approve proposals.
2. Palette pick from the style frames.

## Approval checkpoints
1. Plan + skill stack + second-by-second timing. 2. Three style frames (with palette options). 3. Key-frame preview of the motion.
4. Final render: frame check, score /10, P0/P1/P2, deliver (never via GitHub).

## Build + v1 (user: Phillips Digital colours, shoe rotating, text typewrites on while it rotates, constant loop)
- Shoe: free "Sci-fi Sneaker" by erdemdagdelen (CC-BY 4.0, Objaverse), rendered in Blender as ID-coded tiny sprites
  (scripts/blender/pixel_sneaker_sprite.py: 24 angles, 200x150, camera roll -12 deg, inverted-hull outline) and repainted into the
  palette by scripts/pixel_palette.py (exact palette colours, Phillips Digital lime "p." badge drawn as a pixel glyph on the badge).
- Brand palette (from inputs/phillips-digital-logo.jpg): deep green page #0E1A0E, lime #CEFA43, white type, charcoal.
- Remotion comp `PixelSneaker` (src/pixel/): pixel masthead, shoe on whole-pixel steps (3 frames per angle = one turn per 3 s),
  editorial column, barcode, corner print, tab, MOTION DESIGN, twinkling pixel stars. Typewriter schedule in src/pixel/typing.json
  (types on with a blinking block cursor, holds, backspaces off).
- Seamless 12 s loop: 288 frames = 4 turns, 3 bobs, one type cycle; chiptune at 120 BPM (6 bars) with a click per letter
  (scripts/pixel_audio.py wraps tails around the loop point).
- No grain/lens/AI upscale (pixels stay crisp).

## Render checks
- v1 (renders/pixel-sneaker-loop-v1.mp4 + -silent): 12.0 s, 1920x1080, 24 fps. -14.1 LUFS, true peak -1.2 dB (first mix clipped:
  clicks too spiky; rebalanced the mix, then gain + limiter). Frames checked across the loop. Sound measured, not heard.
- Score 8.4/10: layout 8.5, timing 8.5, readability 8, polish 8.5. Weakest: the side tab box shows empty before its letters type;
  small-print copy is still placeholder (needs the user's words).
- Credit line for posts: "Sneaker model: Sci-fi Sneaker by erdemdagdelen (CC-BY 4.0)".
