"""Swap the print on a Printful white-tee mock-up for a new design.
Finds the old print, rebuilds the fabric under it (pyramid fill from the surrounding
fabric), upscales x4, then prints the new design into the fabric.

usage: python3 -I scripts/tshirt/swap_mockup.py <mockup.png> <design.png> <out.png> [scale] [bx0 by0 bx1 by1]
"""
import sys
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

MOCK, DES, OUT = sys.argv[1:4]
SCALE = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
im = Image.open(MOCK).convert('RGBA')
a = np.array(im).astype(np.float32)
rgb, al = a[..., :3], a[..., 3]
mx, mn = rgb.max(2), rgb.min(2)
sat = (mx - mn) / np.maximum(mx, 1)
H, W = al.shape
# print pixels: coloured or dark, in the central area of the frame
cand = ((sat > 0.22) | (mx < 110)) & (al > 200)
cand[:, :int(W * 0.18)] = False; cand[:, int(W * 0.82):] = False
if len(sys.argv) > 8:  # rough box around the old print (needed on model shots)
    bx0, by0, bx1, by1 = (int(v) for v in sys.argv[5:9])
    keep = np.zeros_like(cand); keep[by0:by1, bx0:bx1] = True; cand &= keep
ys, xs = np.nonzero(cand)
# robust bbox: the dense core of candidate pixels
x0, x1 = np.percentile(xs, [0.2, 99.8]); y0, y1 = np.percentile(ys, [0.2, 99.8])
pad = 26
x0, y0, x1, y1 = int(x0 - pad), int(y0 - pad), int(x1 + pad), int(y1 + pad)
box = np.zeros((H, W), bool)
box[y0:y1, x0:x1] = True
# only the old print's own pixels (+ margin) are rebuilt, so real fabric folds stay elsewhere
pm = Image.fromarray((cand & box).astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(31))
hole = (np.array(pm) > 0) & box


def pyramid_fill(img, known):
    if min(img.shape[:2]) < 4 or known.all():
        return img
    k = known[..., None].astype(np.float32)
    h, w = known.shape
    small = Image.fromarray((img * k).astype(np.float32).mean(2)).size  # noqa
    # downsample by 2 with mask-weighted averages
    def down(x):
        x = x[: h // 2 * 2, : w // 2 * 2]
        return x.reshape(h // 2, 2, w // 2, 2, *x.shape[2:]).sum((1, 3))
    s_img = down(img * k); s_k = down(k)
    s = s_img / np.maximum(s_k, 1e-6)
    filled = pyramid_fill(s, s_k[..., 0] > 0)
    up = np.repeat(np.repeat(filled, 2, 0), 2, 1)
    up = np.pad(up, ((0, h - up.shape[0]), (0, w - up.shape[1]), (0, 0)), mode='edge')
    up = np.array(Image.fromarray(np.clip(up, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)
    return np.where(known[..., None], img, up)


clean = pyramid_fill(rgb.copy(), ~hole)
soft = np.array(Image.fromarray(hole.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(4))).astype(np.float32)[..., None] / 255
rgb2 = rgb * (1 - soft) + clean * soft
noise = np.random.default_rng(1).normal(0, 1.6, rgb2.shape[:2])[..., None] * soft
rgb2 = np.clip(rgb2 + noise, 0, 255)

# upscale x4
sess = ort.InferenceSession('tools/models/esrgan/model.onnx', providers=['CPUExecutionProvider'])
nm = sess.get_inputs()[0].name
T, P = 128, 12
src = np.pad(rgb2 / 255, ((P, P + T), (P, P + T), (0, 0)), mode='reflect').astype(np.float32)
res = np.zeros((H * 4, W * 4, 3), np.float32)
core = T - 2 * P
for yy in range(0, H, core):
    for xx in range(0, W, core):
        r = sess.run(None, {nm: src[yy:yy + T, xx:xx + T].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
        ch, cw = min(core, H - yy), min(core, W - xx)
        res[yy * 4:(yy + ch) * 4, xx * 4:(xx + cw) * 4] = r[P * 4:(P + ch) * 4, P * 4:(P + cw) * 4]
big = (np.clip(res, 0, 1) * 255).astype(np.float32)
big_al = np.array(Image.fromarray(al.astype(np.uint8)).resize((W * 4, H * 4), Image.LANCZOS)).astype(np.float32)

# print the new design into the fabric
des = Image.open(DES)
des = des.crop(des.getchannel('A').getbbox())
bw = (x1 - x0 - 2 * pad + 20) * 4 * SCALE
des = des.resize((round(bw), round(des.height * bw / des.width)), Image.LANCZOS)
dx = int(((x0 + x1) / 2) * 4 - des.width / 2)
dy = int((y0 + pad) * 4 - (des.width * 0.02))
d = np.array(des).astype(np.float32)
hh, ww = d.shape[:2]
region = big[dy:dy + hh, dx:dx + ww]
fab = region.mean(2, keepdims=True) / 255
shade = np.clip(fab / max(np.percentile(fab, 90), 1e-3), 0.55, 1.05)  # fabric folds darken the ink
ink = d[..., :3] * shade
aa = d[..., 3:] / 255 * 0.985
big[dy:dy + hh, dx:dx + ww] = region * (1 - aa) + ink * aa
out = np.dstack([np.clip(big, 0, 255), big_al]).astype(np.uint8)
Image.fromarray(out).save(OUT)
print('wrote', OUT, 'old print box', (x0, y0, x1, y1))
