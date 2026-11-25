---
name: image-to-3d
description: Turn a photo or picture of one object into a textured 3D model (GLB) for free, on this machine's CPU, with TripoSR (MIT licence, by Tripo AI and Stability AI). Then check it in Blender and use it as a prop or hero object in a Cycles scene. Use when someone wants to turn an image into a 3D model or object, make a 3D prop from a photo, or asks for something like Tripo, Luma Genie or Meshy without paying.
---

# Image to 3D (free, local)

One picture of one object becomes a 3D model with colours, in about 30 seconds on CPU. Nothing is uploaded and nothing is paid.
Model: TripoSR (github.com/VAST-AI-Research/TripoSR, MIT licence: free for personal and commercial use).

## Before you start
- Explain the plan to the user and wait for an OK before changing files (user rule).
- Check it's installed: `ls tools/triposr tools/hf-cache`. If missing, ask first, then run `bash scripts/ai/setup_triposr.sh` (installs into the git-ignored `tools/`, downloads about 1.6 GB, needs about 2 GB free: check `df -h /`).
- Copy the user's picture into `inputs/` (never edit the original).

## What makes a good picture
- One object, the whole object in frame, nothing cut off at the edges.
- Plain background (wall, sheet, table top), or a PNG with a transparent background.
- A three-quarter view works best (you can see the front and one side). The back is always guessed.
- Works well: shoes, products, bottles, toys, furniture, spray cans, food, simple characters.
- Works badly: flat artwork (graffiti, logos, posters), text, thin wires, glass, scenes with many objects, people (use real modelling instead).
- For flat artwork like a graffiti piece, trace and extrude it in Blender instead (see `scripts/suno/`).

## Make the model
```bash
tools/ai-venv/bin/python scripts/ai/image_to_3d.py inputs/<picture> work/image-to-3d/<name>-v1.glb
```
- `--res 256` mesh detail (try 320 for more detail, slower). `--fg 0.85` how much of the frame the object fills.
- Background: it uses the PNG's transparency if there is some, otherwise a plain-background cut (rembg is not installed, to save disk; if the cut is messy, cut the object out first, e.g. with object-separation on a still).
- It saves `<name>-v1-input.png` (what the model actually saw). Look at it: if the cut-out is wrong, fix the cut, not the model.
- Never overwrite: v1, v2, v3.

## Check it before using it
```bash
blender -b --factory-startup -P scripts/ai/preview_3d.py -- work/image-to-3d/<name>-v1.glb work/image-to-3d/check/<name>.png 48
```
Renders 3 angles (`_0`, `_1`, `_2`). Put the input next to them and look: upright? right shape? colours OK? holes? Show the user this sheet before building a scene with it.

## Use it in a Blender scene
- Import: `bpy.ops.import_scene.gltf(filepath=...)`. It arrives upright (Z up), roughly 1 unit across: scale to real size.
- Colours are vertex colours: material with a Color Attribute node into Base Color (see `preview_3d.py`). Add roughness and a little bump so it doesn't look plasticky.
- Smooth shading, then optionally a Decimate modifier (ratio 0.3 to 0.5) for faster renders.
- Best as a prop or mid-ground object. In extreme close-ups the soft detail and guessed back show: keep hero close-ups on real or licensed models.
- Render in Cycles as usual. Denoise previews with `scripts/denoise/oidn_render.py`.

## Honest limits
- Quality is below the paid Tripo website: softer detail, muted colours, the back is invented.
- One object per run. For a set of props, run it once per picture.
- Output is a mesh with vertex colours, not a UV texture map.

## Files
- `scripts/ai/image_to_3d.py`: picture to GLB/OBJ (upright, colours corrected for glTF).
- `scripts/ai/preview_3d.py`: 3-angle Cycles check sheet.
- `scripts/ai/setup_triposr.sh`: rebuilds the tool (clone, 3 small compatibility patches, model download).
- Models, inputs, check sheets and renders are local only: never commit them to GitHub.
