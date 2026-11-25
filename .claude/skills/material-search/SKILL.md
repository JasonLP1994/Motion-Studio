---
name: material-search
description: Find, download and install free PBR materials (brick, concrete, metal, wood, ground, fabric, plaster and more) from ambientCG, which is CC0 (free for any use, no sign-up, no credit), then wire them into a Blender Cycles scene with colour, normal, roughness and height maps. Use when a 3D surface looks too clean, flat or "CG", when the user asks for a real texture or material, or names a texture site.
---

# Material search (free PBR textures)

Real photographed materials make 3D look real. ambientCG is reachable from this workspace and is **CC0**: free for personal and commercial use, no account, no attribution needed.

## Before you start
- Explain the plan to the user and wait for an OK before changing files (user rule).
- Check free disk space (`df -h /`): a 2K set is about 15-20 MB, a 4K set about 60-100 MB.
- Other sites (CGAxis, Poliigon, Textures.com...) are usually blocked here and need an account. Then the user downloads the ZIP on their computer and sends it (chat attachment or Google Drive); unzip it into `tools/textures/<name>/` the same way. Check that site's licence first. Never sign up, log in or pay for the user.

## 1. Search
```bash
tools/ai-venv/bin/python scripts/textures/ambientcg.py search "damaged bricks" --limit 12
```
Try several words: the material, its state (worn, dirty, painted, cracked), and synonyms (plaster, stucco, render, concrete).

## 2. Download and compare
```bash
tools/ai-venv/bin/python scripts/textures/ambientcg.py get Bricks097 PaintedBricks002 --res 2K-JPG
tools/ai-venv/bin/python scripts/textures/ambientcg.py sheet work/<project>/texture-choices.jpg Bricks097 PaintedBricks002
```
Look at the sheet (and show the user) before choosing. Use `--res 4K-JPG` only for hero close-ups.
Installs to `tools/textures/<ID>/` (git-ignored) with `LICENSE.txt`, plus maps: `_Color`, `_NormalGL`, `_Roughness`, `_Displacement`, `_AmbientOcclusion`.

## 3. Use it in Blender (Cycles)
- **Colour:** Image Texture (sRGB) into Base Color. Multiply grime, streaks or ground dirt on top so it is not one repeating tile.
- **Normal:** `_NormalGL` (not DX), Non-Color, into a Normal Map node.
- **Roughness:** Non-Color, through a Map Range to keep it in a believable range.
- **Height:** `_Displacement` (Non-Color) into a Bump node (with the Normal Map plugged into its Normal input), plus a little high-frequency noise for grit. True displacement needs a subdivided mesh: only for close-ups.
- **Scale:** map with world coordinates (e.g. X/Z for a wall) so decals and paint on that surface line up with the same bricks. Pick the tile size from the real object size (bricks about 6-7 cm per course).
- **Paint and decals on the surface** (graffiti, posters, tags) should reuse the same normal and height maps, so the paint sits in the grooves instead of looking like a sticker.
- Worked example: `wall_tex()` and `wall_bump()` in `scripts/blender/suno_wall.py` (local-only script).

## 4. Check
Render a quick still with the fast recipe (small render + `scripts/denoise/oidn_render.py` + `scripts/ai/upscale.py`) and look for visible tiling, wrong scale and over-strong bump before using it in a long render.

## Files
- `scripts/textures/ambientcg.py`: search / get / sheet.
- Textures are local only (`tools/textures/`, git-ignored): never commit them.
