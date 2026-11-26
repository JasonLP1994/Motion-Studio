"""Horizontal-only slimming warp (Liquify-style) for one person.
Displacement depends on x mostly, so vertical background lines stay straight.

usage: python3 -I scripts/photo/slim_warp.py in.jpg out.jpg cx strength \
         left_in left_out right_in right_out "y:weight,y:weight,..."
"""
import sys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
cx, a = float(sys.argv[3]), float(sys.argv[4])
l_in, l_out, r_in, r_out = (float(v) for v in sys.argv[5:9])
prof = [tuple(float(p) for p in kv.split(':')) for kv in sys.argv[9].split(',')]
im = np.array(Image.open(src).convert('RGB'))
H, W, _ = im.shape


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


x = np.arange(W, dtype=np.float32)
dx = x - cx
wx = np.where(dx < 0, 1 - smooth((-dx - l_in) / (l_out - l_in)), 1 - smooth((dx - r_in) / (r_out - r_in)))
py, pw = zip(*prof)
vy = np.interp(np.arange(H), py, pw).astype(np.float32)

# sanity: the mapping must stay monotonic (no folding) at full strength
xs_full = x + dx * a * wx
assert np.diff(xs_full).min() > 0.25, 'warp folds: widen the falloff'

res = np.empty_like(im)
for y0 in range(0, H, 256):
    y1 = min(H, y0 + 256)
    xs = x[None, :] + (dx * a * wx)[None, :] * vy[y0:y1, None]
    xs = np.clip(xs, 0, W - 1.001)
    i0 = xs.astype(np.int32)
    f = (xs - i0)[..., None]
    rows = np.arange(y0, y1)[:, None]
    strip = im[rows, i0].astype(np.float32) * (1 - f) + im[rows, i0 + 1].astype(np.float32) * f
    res[y0:y1] = np.clip(strip + 0.5, 0, 255).astype(np.uint8)
Image.fromarray(res).save(out, quality=94, subsampling=0)
print('wrote', out, 'min slope %.2f' % np.diff(xs_full).min())
