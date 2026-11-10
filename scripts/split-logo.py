# Lift flat-colour logo pieces off a solid background into transparent PNGs, keeping
# anti-aliased edges. alpha = projection of (pixel - bg) onto (pieceColour - bg).
# Usage: python3 -I scripts/split-logo.py <logo.jpg> <outdir>
import json, sys
import numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(float)
bg = np.array([15.0, 22.0, 30.0])
pieces = {  # name: (x0, y0, x1, y1) in logo pixels, measured from the file; colour
    "p": ((300, 272, 637, 667), (254, 254, 254)),
    "e": ((637, 272, 954, 667), (130, 188, 199)),
    "bar": ((486, 698, 767, 722), (130, 188, 199)),
    "phillips": ((294, 754, 968, 882), (254, 254, 254)),
    "english": ((329, 891, 927, 1005), (254, 254, 254)),
}
meta = {"source": src, "size": [im.shape[1], im.shape[0]], "background": "#0F161E", "pieces": {}}
for name, ((x0, y0, x1, y1), colour) in pieces.items():
    c = np.array(colour, float)
    crop = im[y0:y1, x0:x1]
    v = c - bg
    a = np.clip(((crop - bg) * v).sum(2) / (v * v).sum(), 0, 1)
    # JPEG noise makes solid interiors read as 0.9-0.99: remap so interiors are fully solid and the bg stays fully clear.
    a = np.clip((a - 0.04) / 0.86, 0, 1)
    # P and E sit 16 px apart (P ends x=628, E starts x=645), so the crop boundary at x=637 separates them.
    rgba = np.dstack([np.broadcast_to(c, crop.shape), a * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(f"{out}/{name}.png")
    meta["pieces"][name] = {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "colour": "#%02X%02X%02X" % tuple(colour)}
json.dump(meta, open(f"{out}/pieces.json", "w"), indent=1)
# Rebuild check: composite every piece over the background and compare with the original.
canvas = np.broadcast_to(bg, im.shape).copy()
for name, p in meta["pieces"].items():
    rgba = np.asarray(Image.open(f"{out}/{name}.png")).astype(float)
    a = rgba[..., 3:4] / 255
    sl = canvas[p["y"]:p["y"] + p["h"], p["x"]:p["x"] + p["w"]]
    sl[:] = sl * (1 - a) + rgba[..., :3] * a
diff = np.abs(canvas - im).mean(2)
print("rebuild mean error %.2f / 255, 99th pct %.1f, max %.0f" % (diff.mean(), np.percentile(diff, 99), diff.max()))
Image.fromarray(canvas.astype(np.uint8)).save(f"{out}/rebuild-check.png")
