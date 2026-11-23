# Brief: stylised character breaking (motion-capture dance), 3D

Status: brief done; next = find a free rigged stylised character + free breaking mocap, retarget test, then three style frames.

| Item | Answer |
|---|---|
| Kind | 3D character animation driven by motion capture |
| Reference | references/dance-ref.mov (frames: notes/frames/dance-ref/). Grammar only: toy-like stylised streetwear character, oversized cap + glasses, puffer jacket with bold graphics, chunky trainers; seamless orange studio cyc, soft warm key + bounce, shallow DoF, low camera. NOT the character itself |
| Purpose / platform | Portfolio, YouTube 16:9 1920x1080 |
| Length / quality | 10-15 s, Option A (every frame rendered, motion blur, ~1 min/frame, Cycles + OIDN + fast AI upscale) |
| Character | Free rigged stylised model (CC0/CC-BY, credited), restyled |
| Motion | Free mocap library, breaking / power moves, retargeted in Blender |
| Colours | Like the reference: warm orange seamless set, pastel-blue outfit, hot-pink graphics |
| Camera | Low angle slow push/orbit + beat-synced cuts and close-ups (feet, hands, face) + speed ramps on power moves |
| Sound | Original breakbeat timed to the moves, -14 LUFS (true-peak limiter), silent copy |
| Ending | Phillips Digital logo |
| Credits | Model + mocap licences listed |

## Checkpoints
1. Model + mocap picks (preview sheet). 2. Retarget test (does the dance read on the character). 3. Three style frames.
4. Shot plan second by second + low-res timing preview. 5. Final render, frame check, score, deliver (never GitHub).

## Update: character + art direction (user)
- Character: the user's own "Realistic man.blend" (Google Drive, 435 MB; inputs/dance/realistic_man.blend, git-ignored):
  Character Creator body, Auto-Rig Pro skeleton ("rig", 537 bones) + Faceit face rig; varsity jacket, hoodie, vest, zip cargo
  pants, high-tops, buzz cut. Mocap: CMU subject 85 breakdance takes (free use), retargeted by work/dance/retarget.py
  (world-rotation transfer onto ARP deform bones, FK on his bone lengths, hips scaled by leg length 0.836, floor clamp).
- NEW look (user's UV/blacklight reference, replaces the orange set): saturated electric-blue seamless world; skin reads deep
  blue/indigo under blue light; translucent glossy hot-pink/magenta vinyl outerwear with glowing pink edges; glowing pink
  drawstrings; neon-lime UV paint accents (face splash, small marks); soft, wet highlights; no other hues.
- Look dev v4 (scripts/blender/dance_uv_look.py): Standard view -0.4 EV (AgX turned neon pink lavender); skin desaturated x indigo
  multiply; jacket + hoodie translucent pink vinyl (transmission, coat, fresnel pink edge glow); indigo glossy pants; lime UV paint
  as a vertex attribute on the face (the CC body mesh is in centimetres: scale offsets by 1/matrix scale); electric-blue cyc with
  glow; blue key/fill + hot-pink rims. Frames: work/dance/uvlook_v4.jpg. Retarget fixes: ARP root bone points down (align hips on
  world up); twist bones posed after their parent bone. oidn_render.py now adds a compositor when a scene has none.
- Face paint v2: UV vein pattern from the user's reference, stencil scripts/blender/dance_paint/make_face_paint_stencil.py (cm from the nose tip, symmetric), projected in Generated space, front-facing vertex mask. Check: work/dance/facepaint_v2.jpg.
- Eyes: hollow/twisted eyes in motion = ARP face aim targets (eye.L/.R) stayed in world space; retarget now re-parents face
  constraint targets onto head.x. UV contact lenses: Std_Eye_L/R replaced with a radial UV ramp (eyeball UV centred 0.5, iris
  radius ~0.25), glowing lime iris + dark pupil; cornea = clear glass. (Colour-ramp gotcha: elements re-sort when positions
  change; set them in two passes.) Check: work/dance/eyes_fix5.jpg.

## Edit + cameras v1
Segments (CMU 85, 24 fps): s1 fancy footwork f100-195, s2 handstand kicks f110-189, s3 break + flips f240-335, s4 helicopter
f105-200 -> 368 frames (15.3 s), joined by scripts/blender/dance_merge_segments.py (cuts hide the jumps). Cameras
scripts/blender/dance_cams.py, all following the smoothed hips: A floor-level 20 mm dolly-in, B feet 50 mm, C overhead rotating,
D worm's eye 16 mm, E 3/4 orbit, F 70 mm push to the face/eyes. Board: work/dance/camera_board_v2.jpg.
