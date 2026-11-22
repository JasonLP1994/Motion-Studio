# Finishing pass (the After Effects "touch-up" stage), free and local

Tool: postfx (MIT, github.com/0xBeycan/postfx), installed in ignored `tools/finish-py` (with opencv-python-headless, pyyaml).
Runs on CPU over a folder of frames: white balance, highlight roll-off, lift/gamma/gain, split-toning, tone curve, vibrance,
halation, chromatic aberration, vignette, clarity, sharpening, per-frame moving grain (seeded by filename), `.cube` LUTs.

    bash scripts/finish/finish.sh IN_DIR OUT_DIR [THEME] [STRENGTH]

House looks (scripts/finish/themes/):
- `product_premium.yaml` (0.8-0.9): glossy products — gentle warm halation, soft vignette, highlight roll-off, fine grain.
- `cover_punch.yaml` (0.8): graphic/editorial pieces with type — crisp, punchy, tiny CA, fine grain.
- Built-in film looks for references: `PYTHONPATH=tools/finish-py python3 -m postfx list` (Portra, Ektar, Cinestill, teal-orange,
  bleach bypass, noir...). `postfx sheet` makes a contact sheet of all looks on one frame.

Order in the pipeline: render -> (AI denoise) -> RIFE / retime -> AI upscale -> composite type (Remotion) -> FINISH -> encode + sound.
Finish after the type so grain and grade sit over everything, like an adjustment layer at the top of an After Effects comp.
Keep strength subtle; check a before/after still (notes/frames/finishing-test.jpg) before running a whole sequence.

Already available for other touch-ups: ffmpeg filters (lut3d, curves, eq, colorbalance, vignette, unsharp, deflicker, chromashift),
the Blender compositor (`compositing` skill: glare, lens distortion, colour balance on EXR passes), @remotion/effects in comps.
Skipped: Hance (FSL licence, not open source yet), paid plug-ins (ARRI Film Lab, Lazy Composer Pro).
