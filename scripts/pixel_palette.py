# Repaint ID-coded pixel sprites (work/pixel/sneaker_sprite.py) into a palette: every pixel becomes an exact palette colour.
# Red channel = colour role (linear value / 10), green = toon shade (0 / 0.5 / 1 linear), black = outline.
# Usage: python3 scripts/pixel_palette.py IN_DIR OUT_DIR PALETTES.json PALETTE_NAME
import sys, os, glob, json
import numpy as np
from PIL import Image
inp, out, pal_file, name = sys.argv[1:5]
pal = json.load(open(pal_file))[name]
def hx(h): h = h.lstrip("#"); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
def lin(v): v = v / 255.0; return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
lut = np.zeros((11, 3, 3), np.uint8)
for role, shades in pal["roles"].items():
    for s, c in enumerate(shades): lut[int(role), s] = hx(c)
ink = np.array(hx(pal["ink"]), np.uint8)
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(os.path.join(inp, "id_*.png"))):
    a = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)
    role = np.clip(np.rint(lin(a[..., 0]) * 10), 0, 10).astype(int); shade = np.clip(np.rint(lin(a[..., 1]) * 2), 0, 2).astype(int)
    rgb = lut[role, shade]; rgb[role == 0] = ink
    alpha = (a[..., 3] > 127).astype(np.uint8) * 255
    Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(os.path.join(out, os.path.basename(f).replace("id_", "s_")))
print("palette", name, "->", out)
