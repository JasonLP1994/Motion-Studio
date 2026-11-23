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
