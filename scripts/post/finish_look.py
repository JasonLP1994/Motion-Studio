"""Camera finishing pass for rendered frames (numpy, no smoothing): lens colour fringing towards the corners,
gentle vignette, warm halation glow around bright lights, and fine moving film grain.
Usage: tools/ai-venv/bin/python scripts/post/finish_look.py <in_dir_or_png> <out_dir> [--ca 1.0] [--vig 0.22] [--grain 0.018] [--hal 0.18]
Frames already in out_dir are skipped. Grain is seeded per file so it moves frame to frame but is repeatable.
"""
import argparse, glob, os, zlib
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--ca", type=float, default=1.0, help="colour fringing in pixels at the corners (1080p)")
ap.add_argument("--vig", type=float, default=0.22); ap.add_argument("--grain", type=float, default=0.018)
ap.add_argument("--hal", type=float, default=0.18)
ap.add_argument("--delete-src", action="store_true", help="remove each input frame once its output is saved (saves disk)")
a = ap.parse_args()
files = sorted(glob.glob(os.path.join(a.inp, "*.png"))) if os.path.isdir(a.inp) else [a.inp]
os.makedirs(a.out, exist_ok=True)


def radial_scale(ch, s, cx, cy):
    """Scale one channel about the centre by factor s (bilinear), for lateral chromatic aberration."""
    h, w = ch.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = cx + (xx - cx) / s; sy = cy + (yy - cy) / s
    x0 = np.clip(np.floor(sx).astype(int), 0, w - 2); y0 = np.clip(np.floor(sy).astype(int), 0, h - 2)
    fx = np.clip(sx - x0, 0, 1); fy = np.clip(sy - y0, 0, 1)
    return (ch[y0, x0] * (1 - fx) * (1 - fy) + ch[y0, x0 + 1] * fx * (1 - fy) + ch[y0 + 1, x0] * (1 - fx) * fy + ch[y0 + 1, x0 + 1] * fx * fy)


for i, f in enumerate(files):
    dst = os.path.join(a.out, os.path.basename(f))
    if os.path.exists(dst):
        if a.delete_src and os.path.isdir(a.inp): os.remove(f)
        continue
    im = Image.open(f).convert("RGB"); w, h = im.size
    x = np.asarray(im).astype(np.float32) / 255.0
    cx, cy = (w - 1) / 2, (h - 1) / 2; rmax = np.hypot(cx, cy)
    k = a.ca * (h / 1080.0) / rmax
    if k > 0:
        x[..., 0] = radial_scale(x[..., 0], 1 + k, cx, cy); x[..., 2] = radial_scale(x[..., 2], 1 - k, cx, cy)
    # halation: blur of the brightest parts, tinted warm, added back
    lum = x.mean(-1)
    bright = np.clip((lum - 0.7) / 0.3, 0, 1)[..., None] * x
    glow = np.asarray(Image.fromarray((np.clip(bright, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(h / 60))).astype(np.float32) / 255
    x = x + a.hal * glow * np.array([1.0, 0.75, 0.55])
    # vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); r = np.hypot((xx - cx) / cx, (yy - cy) / cy) / np.sqrt(2)
    x = x * (1 - a.vig * np.clip(r, 0, 1) ** 2.2)[..., None]
    # film grain: luminance-weighted, slightly soft, different per frame
    rng = np.random.default_rng(zlib.crc32(os.path.basename(f).encode()))
    g = rng.standard_normal((h, w)).astype(np.float32)
    g = np.asarray(Image.fromarray(((g * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 40 - 3.2
    x = x + a.grain * g[..., None] * (0.4 + 0.6 * np.sqrt(np.clip(x.mean(-1, keepdims=True), 0, 1)))
    Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)
    if a.delete_src and os.path.isdir(a.inp): os.remove(f)
    if i % 20 == 0: print(f"[{i + 1}/{len(files)}] {os.path.basename(f)}", flush=True)
print("finish look done:", a.out)
