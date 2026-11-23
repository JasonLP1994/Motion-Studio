# OOZE shoe compositing pass (user: "use our compositing tools to bring it more to life"), per 1080p frame in numpy:
# smooth exposure lift over the dark middle (~4.5-10.5 s), open shadows, richer colour, gentle S-contrast, soft highlight bloom,
# subtle vignette, fine animated grain. Deterministic (grain seeded per frame).
# Usage: python3 scripts/grade/shoe_grade.py <in_dir f_NNNN.png> <out_dir> [first last]
import sys, os, glob
import numpy as np
from PIL import Image, ImageFilter
IN, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
G = {"lift": 0.30, "lift_in": (4.5, 5.5), "lift_out": (9.5, 10.5), "shadow": 0.012, "sat": 1.22, "contrast": 0.12,
     "bloom": 0.38, "bloom_from": 0.62, "bloom_px": 30, "vignette": 0.22, "grain": 0.008, "fps": 30}
files = sorted(glob.glob(os.path.join(IN, "f_*.png")))
if len(sys.argv) > 4: files = [f for f in files if int(sys.argv[3]) <= int(f[-8:-4]) <= int(sys.argv[4])]
H = W = None
for f in files:
    n = int(f[-8:-4]); t = (n - 1) / G["fps"]; dst = os.path.join(OUT, os.path.basename(f))
    if os.path.exists(dst): continue
    x = np.asarray(Image.open(f).convert("RGB"), np.float32) / 255
    if H is None:
        H, W = x.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
        r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.8 + ((yy - H / 2) / (H / 2)) ** 2
        vig = (1 - G["vignette"] * np.clip(r2 - 0.25, 0, None) / 1.55)[..., None].astype(np.float32)
    a0, a1 = G["lift_in"]; b0, b1 = G["lift_out"]
    k = np.clip((t - a0) / (a1 - a0), 0, 1) * np.clip((b1 - t) / (b1 - b0), 0, 1)
    k = k * k * (3 - 2 * k)                                         # smoothstep: never a visible jump
    x = np.power(np.clip(x, 0, 1), 1 / (1 + G["lift"] * k))         # exposure lift in the mids
    x = G["shadow"] + x * (1 - G["shadow"])                           # open the blacks a touch
    Y = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(Y + (x - Y) * G["sat"], 0, 1)                         # richer colour
    s = x * x * (3 - 2 * x); x = x + G["contrast"] * (s - x)          # gentle S-curve
    hi = np.clip((x - G["bloom_from"]) / (1 - G["bloom_from"]), 0, 1) * x
    small = Image.fromarray((hi * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(G["bloom_px"] / 4))
    bl = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255
    x = 1 - (1 - x) * (1 - G["bloom"] * bl)                          # screen the glow back in
    x = x * vig
    x = x + np.random.default_rng(n).normal(0, G["grain"], (H, W, 1)).astype(np.float32)
    Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)
print("graded", len(files), "->", OUT)
