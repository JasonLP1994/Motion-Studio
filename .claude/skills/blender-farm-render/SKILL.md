---
name: blender-farm-render
description: Use when a 3D piece needs render-engine quality (path tracing) or the user asks to render on a render farm / "render it properly" / "in Blender". Builds the scene in Blender Cycles from this workspace's three.js scene code, checks it with low-res local renders, estimates the farm cost, and hands the user one packed, farm-ready .blend plus the beginner guide notes/render-farm.md. Never uploads, creates accounts or pays.
---

# Blender + render farm workflow

The user approved Blender Cycles as the look for hero 3D ("this looks better") and wants to render
future pieces on a paid farm themselves. Real-time WebGL output reads as "PS2 game" to them. The browser
path tracer can't run here (SwiftShader never finishes compiling it), so don't use it.

## Pipeline (all scripts in this repo)
1. **Scene state from the project's own code.** `scripts/pathtrace/stills.ts` rebuilds a moment from the
   Remotion piece's pure modules (e.g. `src/statue/fracture.ts` + `config.ts`). It runs with
   `node scripts/pathtrace/run.cjs <shot> 1 x.png "export=1&nodof=1"` and env `PT_OUT=<dir>`, which saves
   `<shot>.glb` and `<shot>.json` (camera, DOF), or a mask PNG for flat graphics such as carved text.
2. **Blender scene.** `blender -b --factory-startup -P scripts/blender/render_still.py -- <shot> <dir> <out.png> [spp]`
   imports the GLB, replaces the exported materials by name and sets up the scene:
   - materials: blood (vertex colour `Col`, SSS, coat), marble (SSS, veins, pores) and stone;
   - hidden area lights (`visible_camera = False`);
   - the camera from JSON (three.js Y-up converted to Blender Z-up);
   - Cycles with AgX tone mapping.
3. **Quick checks here:** `PCT=25` and 24-32 spp take seconds per shot. Look at every preview, and fix the
   lights or materials before any long render.
4. **Farm file:** `FARM_BLEND=renders/farm/<name>.blend` (optional `FARM_SAMPLES`) calls
   `scripts/blender/farm_prep.py`. That packs everything, sets GPU with CPU fallback, 128 spp, the
   OpenImageDenoise denoiser, 16-bit PNG frames to `//render/<name>_####` and the frame range, then saves.
   Reopen the file and render a tiny frame to prove it's self-contained. The local Ubuntu Blender
   4.0.2 has no OIDN, so turn the denoiser off for that local check only.
5. **Cost estimate:** time local frames at 512 spp without denoise, divide by about 4 for 128 spp plus
   denoise, then compute per-frame seconds × frames × 4 cores × 2.3 GHz ÷ 3600 = GHz-hours. Multiply by the
   farm rate (RebusFarm about 1.39¢/GHzh; GarageFarm $0.024 / 0.036 / 0.072 for Low / Medium / High). Give
   a range and say the farm's own quote is the real number.
6. **Hand-off:** send the .blend via SendUserFile, point the user to `notes/render-farm.md`, and state the
   Blender version, frame range and expected output names.
7. **Return:** frames come back to `inputs/farm/<name>/`. Encode the MP4 with system ffmpeg, mux the sound
   (-14 LUFS), check frames from the whole video, score it out of 10 and save it as a new version in
   `renders/`. Never commit `.blend` files, frames or videos.

## Rules
- Ask before installing anything outside this folder. Blender 4.0.2 and python3-numpy are installed via
  apt; downloading the official Blender build was blocked by the session's safety check.
- Never upload to a farm, create an account or pay. The user does those steps.
- Re-read `notes/checks.md` before every render.
