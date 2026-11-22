# Blender setup (this cloud workspace)

- Blender 4.0.2 installed from the Ubuntu repository (`/usr/bin/blender`). System graphics libs added (libegl1, libgl1, libglu1-mesa, ...).
- Headless rendering works: `blender -b --factory-startup -P script.py`. EGL warnings in the log are harmless.
- No Blender MCP connector exists in the registry, so the 94 skills in `.claude/skills/` (blender-*, lighting, rendering, etc.) run as written guidance. Claude drives Blender directly with Python scripts through the shell.
- No GPU: Eevee previews are fine; Cycles is CPU-only and slow. Keep blockouts small (480x270 previews).
- Fast-render plan (pending): Blender blockout → control passes (depth, normal, mask) → AI video-to-video service (not chosen yet; ask before any paid job) → graphics, type, effects and sound in Remotion.
- Test: `work/blender/test_scene.py` rendered `work/blender/test.png` OK.
