# Ruby pendant: plan (v1)

Picks (22 Nov): mode = auto + my picks; words = none; visuals = 3D (Blender Cycles) + shader/particle sparkle; polish = beat-synced
cuts, sound effects, custom transitions; no logo. Piece = **pendant necklace, rose gold, diamond centre, ruby halo**.
Format 16:9 1920x1080, 12 s (360 frames, 30 fps). Feeling: quiet luxury, like the reference.
Reference: references/jewelry/ruby-ref-v1.mp4 (screen recording of a diamond-stud ad; only 0-12.7 s is the film). Grammar only:
black void + one overhead spotlight making a soft pale steel-blue oval pool, a hard dark shadow of the piece in the pool,
cool crisp specular sparkle, macro -> top-down pull-back -> tilt to 3/4 -> exploded view -> macro reassembly -> hero.
Never their brand, logo, or their exact stud design.

## Skill stack
| Skill | Job in this video | Why |
|---|---|---|
| motion-art-direction | One look: black void, steel-blue pool, warm rose gold + blood-red rubies against cool light, white diamond fire | reference + the user's ruby/rose-gold choice |
| lighting (product-lighting) | Light the reflections: overhead spot for the pool + hard shadow (light-linked to the floor), small softboxes and grazing strips for the metal, black cards for contrast, tiny hard lights for gem sparkle | glossy metal + gems |
| camera-cinematography (product-camera) | Macro -> reveal structure, constant-speed moves through cuts, arcs not straight pulls, rack focus, expo ease-out on the reveal, moves land on beats | reference's camera grammar |
| shot-composition | 16:9 framing: pendant on the right third in the exploded view (diagonal), centred for top-down and hero | user chose landscape (the reference is vertical: re-composed, not cropped) |
| blender-farm-render + AI recipe | Cycles + OIDN, 1280x720 -> compact AI 2x upscale, RIFE only inside smooth shots | user rule: Cycles, fastest best-quality recipe |
| beat-sync-editing | 100 BPM grid (beat = 18 frames, bar = 72): every cut, click and glint on a beat | music-led |
| shader/particle (compositor glare + glint sprites) | Star-streak glints on diamond/ruby highlights at beat moments; fine floating dust in the spot beam | reference's twinkles |
| remotion-transitions (custom, 2 kinds) | (1) glint-flash cut: a star glint blooms to a white flash and the cut happens at its peak; (2) match-move cut (the shape continues across the cut) | user ticked custom transitions; luxury restraint = 2 kinds max |
| sound-effects | Original synthesised music (soft piano/bell pad, sub pulse), soft metal clicks as parts lock, shimmer on glints, air whoosh on the explode, -14 LUFS | user ticked sound effects |

## The piece (built in Blender, all original)
- Centre: round brilliant **diamond** (57 facets, ~6 mm), 4 rose-gold claw prongs on a basket.
- **Ruby halo**: 16 small round rubies pave-set in a rose-gold halo frame with beads between stones (milgrain edge).
- **Bail**: rose-gold loop with a row of 3 tiny diamonds, hinged on a jump ring at the top of the halo.
- **Chain**: fine rose-gold cable chain (instanced links on a curve).
- Materials: rose gold (metallic, roughness 0.12, colour ~#E8A48A); diamond = 3 glass layers IOR 2.40/2.42/2.45 tinted R/G/B (fake
  dispersion; Blender 4.0 has none); ruby = glass IOR 1.77 + deep red absorption (#9B0020 -> #E0103A rim).

## Second by second (100 BPM: beat = 18 frames)
| Frames | Time | Shot / camera | What you see | Sound |
|---|---|---|---|---|
| 0-36 | 0-1.2 s | MACRO, 100 mm, f/2 | extreme close on the diamond's table, red ruby bokeh at the edges; rack focus from soft to sharp; slow pull back | soft bell + air |
| 36-108 | 1.2-3.6 s | TOP-DOWN pull-back + slow arc (counter-rotate 15 deg) | the whole pendant head lands in the steel-blue pool, its hard shadow below; expo ease-out into a drift | pad swells |
| 108 | 3.6 s | glint | star glint on the diamond (beat), **glint-flash cut** | shimmer |
| 108-144 | 3.6-4.8 s | 3/4 view, 60 mm | pendant on its chain, tilted; light runs across the halo as the camera arcs | |
| 144-198 | 4.8-6.6 s | EXPLODE (same 3/4 camera, slow push) | parts float apart on a diagonal: chain lifts, bail rises, diamond lifts out of its prongs, halo frame drops; each part casts its own shadow | whoosh, then airy hold |
| 198 / 216 / 234 | 6.6 / 7.2 / 7.8 s | MACRO cuts on beats (85 mm, noise breathing) | (a) diamond drops into the prongs, claws close - click; (b) bail swings onto the jump ring - click; (c) chain threads through the bail | three metal clicks |
| 252-324 | 8.4-10.8 s | HERO: match-move cut to front 3/4, 45 mm, arc + pull-back | assembled pendant hangs on its chain in the pool, slight sway, shadow on the floor, rubies glowing | music resolves |
| 324 | 10.8 s | final glint | diamond fire flash | shimmer |
| 324-360 | 10.8-12 s | drift | slow linear drift so the last frame is alive | tail |

## Render plan
- Cycles, gem-specific settings: transmission bounces 12 (gems die at 2), glossy 6, clamp indirect 5, caustics off, light tree on,
  adaptive 0.03, ~64 spp + OIDN. 1280x720 then compact AI 2x upscale to 1920x1080.
- RIFE only inside smooth moves (pull-back, explode drift, hero arc); real frames for cuts, clicks and glints.
- The shoe render finishes ~08:30 UTC 23 Nov; the ruby full render starts after it (one render at a time). Stills render now at low priority.
