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
# lowercase "p." from the Phillips Digital mark, 6 x 6 pixels (bowl, stem, full stop)
GLYPH = np.array([[1,1,1,1,0,0],
                  [1,0,0,1,0,0],
                  [1,0,0,1,0,0],
                  [1,1,1,1,0,1],
                  [1,0,0,0,0,0],
                  [1,0,0,0,0,0]], np.uint8)
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(os.path.join(inp, "id_*.png"))):
    a = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)
    role = np.clip(np.rint(lin(a[..., 0]) * 10), 0, 10).astype(int); shade = np.clip(np.rint(lin(a[..., 1]) * 2), 0, 2).astype(int)
    rgb = lut[role, shade]; rgb[role == 0] = ink
    alpha = (a[..., 3] > 127).astype(np.uint8) * 255
    if "logo" in pal:   # Phillips Digital badge: lime circle + black "p." drawn as a hand-placed pixel glyph on every badge blob
        import cv2
        mask = ((role == 8) & (alpha > 0)).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(mask, 8)
        lime = np.array(hx(pal["logo"]["circle"]), np.uint8); pink = np.array(hx(pal["logo"]["p"]), np.uint8)
        for k in range(1, n):
            x, y, w, h, area = st[k]
            if area < 6: continue
            rgb[lab == k] = lime
            G = GLYPH; gs = max(1, min((w - 2) // G.shape[1], (h - 2) // G.shape[0]))
            if gs >= 1 and w >= G.shape[1] + 2 and h >= G.shape[0] + 2:
                gx, gy = int(cen[k][0] - G.shape[1] * gs / 2), int(cen[k][1] - G.shape[0] * gs / 2)
                for (r, c) in zip(*np.nonzero(G)):
                    for dy in range(gs):
                        for dx in range(gs):
                            yy, xx = gy + r * gs + dy, gx + c * gs + dx
                            if 0 <= yy < rgb.shape[0] and 0 <= xx < rgb.shape[1] and lab[yy, xx] == k: rgb[yy, xx] = pink
    Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(os.path.join(out, os.path.basename(f).replace("id_", "s_")))
print("palette", name, "->", out)
