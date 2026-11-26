"""Natural portrait enhance: crop/frame, AI upscale (2x net, Real-ESRGAN blended with
Lanczos so skin keeps real texture), gentle grade (lift shadows, warmth, vibrance,
clarity, soft vignette). Never reshapes faces or bodies.

usage: python3 -I scripts/photo/enhance_portrait.py in.jpg out.jpg x0 y0 x1 y1
"""
import sys
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
box = tuple(int(v) for v in sys.argv[3:7])
im = Image.open(src).convert('RGB').crop(box)
W, H = im.size


def esrgan(rgb):
    sess = ort.InferenceSession('tools/models/esrgan/model.onnx', providers=['CPUExecutionProvider'])
    name = sess.get_inputs()[0].name
    T, P = 128, 12
    h, w, _ = rgb.shape
    srcp = np.pad(rgb.astype(np.float32) / 255, ((P, P + T), (P, P + T), (0, 0)), mode='reflect')
    res = np.zeros((h * 4, w * 4, 3), np.float32)
    core = T - 2 * P
    for y in range(0, h, core):
        for x in range(0, w, core):
            r = sess.run(None, {name: srcp[y:y + T, x:x + T].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            ch, cw = min(core, h - y), min(core, w - x)
            res[y * 4:(y + ch) * 4, x * 4:(x + cw) * 4] = r[P * 4:(P + ch) * 4, P * 4:(P + cw) * 4]
    return np.clip(res, 0, 1)


half = np.array(im.resize((W // 2, H // 2), Image.LANCZOS))
ai = esrgan(half)                                   # 2x of the crop
OW, OH = ai.shape[1], ai.shape[0]
lan = np.array(im.resize((OW, OH), Image.LANCZOS)).astype(np.float32) / 255
x = ai * 0.55 + lan * 0.45

# grade
x[..., 0] *= 1.025; x[..., 2] *= 0.975              # a touch warmer
lum = x.mean(axis=2, keepdims=True)
x = x + 0.10 * (1 - lum) ** 2 * lum * 4             # lift shadows
x = np.clip(x, 0, 1)
x = x + 0.06 * np.sin((x - 0.5) * np.pi) * 0.5      # gentle S contrast
mx, mn = x.max(axis=2, keepdims=True), x.min(axis=2, keepdims=True)
sat = (mx - mn)
x = lum + (x - lum) * (1 + 0.18 * (1 - np.clip(sat * 2, 0, 1)))  # vibrance
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
v = 1 - 0.16 * (((xx - OW / 2) / OW) ** 2 + ((yy - OH * 0.45) / OH) ** 2) * 2.4
x = np.clip(x * v[..., None], 0, 1)
img = Image.fromarray((x * 255 + 0.5).astype(np.uint8))
img = img.filter(ImageFilter.UnsharpMask(radius=30, percent=12, threshold=3))  # clarity
img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))  # detail
img.save(out, quality=94, subsampling=0)
print('wrote', out, img.size)
