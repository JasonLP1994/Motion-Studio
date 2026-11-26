"""CultureJacked print prep: ChatGPT art -> Printful-ready 4500x5400 300 DPI PNGs.

1. AI upscale x4 (Real-ESRGAN ONNX, tiled, CPU)
2. Hard alpha (no semi-transparent pixels: DTG prints them faded/speckled)
3. Replace a trademark logo on the mic flag with a generic "LIVE" flag
4. Centre on a 4500x5400 transparent canvas, 300 DPI
5. Black-shirt version: knock out near-pure black so the shirt shows through

usage: python3 -I scripts/tshirt/prep_print.py <in.png> <out_prefix>
"""
import sys
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 4500, 5400
# mic-flag front face in ORIGINAL pixel coords (TL, TR, BR, BL)
FLAG = [(357.3, 1006.0), (447.3, 1040.0), (402.7, 1122.7), (307.3, 1082.7)]
CREAM, RED, CHAR = (240, 228, 200), (214, 40, 40), (38, 36, 39)
FONT = 'public/fonts/anton-latin-400-normal.woff2'


def upscale(rgb):
    sess = ort.InferenceSession('tools/models/esrgan/model.onnx', providers=['CPUExecutionProvider'])
    name = sess.get_inputs()[0].name
    T, P = 128, 12  # tile, overlap pad
    h, w, _ = rgb.shape
    src = np.pad(rgb.astype(np.float32) / 255, ((P, P + T), (P, P + T), (0, 0)), mode='reflect')
    out = np.zeros((h * 4, w * 4, 3), np.float32)
    core = T - 2 * P
    for y in range(0, h, core):
        for x in range(0, w, core):
            tile = src[y:y + T, x:x + T].transpose(2, 0, 1)[None]
            res = sess.run(None, {name: tile})[0][0].transpose(1, 2, 0)
            ch, cw = min(core, h - y), min(core, w - x)
            out[y * 4:(y + ch) * 4, x * 4:(x + cw) * 4] = res[P * 4:(P + ch) * 4, P * 4:(P + cw) * 4]
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def replace_flag(img, s):
    poly = [(x * s, y * s) for x, y in FLAG]
    cx = sum(p[0] for p in poly) / 4
    cy = sum(p[1] for p in poly) / 4
    inset = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.86) for x, y in poly]
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).polygon(inset, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.5))
    rng = np.random.default_rng(3)
    face = np.full((img.size[1], img.size[0], 3), CHAR, np.float32)
    face += rng.normal(0, 9, face.shape[:2])[..., None]  # print grain
    face = Image.fromarray(np.clip(face, 0, 255).astype(np.uint8))
    img.paste(face, (0, 0), mask)
    # lettering, rotated to the face angle
    ang = np.degrees(np.arctan2(poly[1][1] - poly[0][1], poly[1][0] - poly[0][0]))
    side = np.hypot(poly[1][0] - poly[0][0], poly[1][1] - poly[0][1])
    font = ImageFont.truetype(FONT, int(side * 0.36))
    lay = Image.new('RGBA', (int(side * 1.4), int(side * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lw, lh = lay.size
    txt = 'LIVE'
    bb = d.textbbox((0, 0), txt, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    dot = th * 0.26
    gap = dot * 0.7
    x0 = (lw - (tw + dot * 2 + gap)) / 2
    y0 = (lh - th) / 2 - bb[1] - th * 0.12
    off = max(3, side * 0.03)
    d.text((x0 + dot * 2 + gap + off, y0 + off), txt, font=font, fill=RED)
    d.text((x0 + dot * 2 + gap, y0), txt, font=font, fill=CREAM)
    cyd = lh / 2 - th * 0.12
    d.ellipse([x0, cyd - dot, x0 + dot * 2, cyd + dot], fill=RED)
    d.text((lw / 2, lh / 2 + th * 0.58), 'No.10 TV', font=ImageFont.truetype(FONT, int(side * 0.13)), fill=CREAM, anchor='mt')
    lay = lay.rotate(-ang, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(lay, (int(cx - lw / 2), int(cy - lh / 2)))
    return img


src = Image.open(SRC).convert('RGBA')
arr = np.array(src)
alpha = arr[..., 3]
print('upscaling', src.size, '-> x4 ...', flush=True)
big = Image.fromarray(upscale(arr[..., :3])).convert('RGBA')
s = 4
a_big = Image.fromarray(alpha).resize(big.size, Image.LANCZOS)
a_big = np.where(np.array(a_big) >= 128, 255, 0).astype(np.uint8)
big.putalpha(Image.fromarray(a_big))
big = replace_flag(big, s)
big.putalpha(Image.fromarray(a_big))  # keep the hard outer alpha after drawing

# fit into 4500x5400, centred, small safety margin
scale = min((W - 120) / big.width, (H - 120) / big.height)
fit = big.resize((round(big.width * scale), round(big.height * scale)), Image.LANCZOS)
fa = np.array(fit)
fa[..., 3] = np.where(fa[..., 3] >= 128, 255, 0)
fit = Image.fromarray(fa)
canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
canvas.alpha_composite(fit, ((W - fit.width) // 2, (H - fit.height) // 2))
canvas.save(f'{OUT}_white-and-light-shirts.png', dpi=(300, 300), optimize=True)

# black-shirt version: near-black ink -> shirt shows through (softer print, same look)
c = np.array(canvas)
lum = c[..., :3].astype(np.int32).max(axis=2)
knock = (lum < 34) & (c[..., 3] == 255)
c[knock, 3] = 0
Image.fromarray(c).save(f'{OUT}_black-shirts.png', dpi=(300, 300), optimize=True)
print('done', canvas.size, 'art', fit.size, 'knocked out %.1f%%' % (knock.mean() * 100))
