# Turn the Blender logo pass of the last frame (two-tone stencil render: `mutant.py -- logo`) into a flat 2D logo mark:
# solid white silhouette (spikes, webs, holes come through as cut-outs) with the darkest creases (face features,
# web folds) cut back out in black, cleaned of speckle. Output is full-frame and pixel-aligned with the 3D frame,
# so the head can freeze into the mark without a jump. Usage: python3 scripts/mutant_logo.py work/mutant/frames/logo_pass.png public/mutant/logo-mark.png
import sys
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
if im.size != (1920, 1080):
    im = im.resize((1920, 1080), Image.LANCZOS)
a = np.asarray(im).astype(np.float32) / 255.0
alpha = a[..., 3]
lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

sil = alpha > 0.5
detail = (lum < 0.5) & sil                                    # dark creases become black cut-outs
mask = sil & ~detail

m = Image.fromarray((mask * 255).astype(np.uint8))
m = m.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))   # de-speckle, close pinholes
m = m.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 127 else 0)                             # smooth edges, re-threshold
m = m.filter(ImageFilter.GaussianBlur(0.6))                                                                      # light anti-alias

rgba = np.zeros((1080, 1920, 4), np.uint8); rgba[..., :3] = 255; rgba[..., 3] = np.asarray(m)
Image.fromarray(rgba).save(out)
ys, xs = np.nonzero(np.asarray(m) > 127)
print("ok", out, "bbox", xs.min(), ys.min(), xs.max(), ys.max())
