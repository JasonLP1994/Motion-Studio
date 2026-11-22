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
