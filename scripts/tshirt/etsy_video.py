"""CultureJacked Etsy listing video: 10 s, silent, 1080x1350, 30 fps.

Scene A: 2.5D parallax push across the artwork (depth from Depth Anything V2 small),
phone-camera REC frame, press flashes. Scene B: tee mock-ups black / navy / white.

usage: python3 -I scripts/tshirt/etsy_video.py <art_light.png> <art_black.png> <orig.png> <out.mp4> [stills]
"""
import sys, subprocess
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ART_LIGHT, ART_BLACK, ORIG, OUT = sys.argv[1:5]
STILLS = len(sys.argv) > 5 and sys.argv[5] == 'stills'
OW, OH, FPS = 1080, 1350, 30
NA = 168            # scene A frames (5.6 s)
NT = 300            # total (10 s)
CREAM, RED = (243, 230, 200), (214, 40, 40)
MONO = 'public/fonts/LiberationMono-Bold.ttf'
ANTON = 'public/fonts/anton-latin-400-normal.woff2'
rng = np.random.default_rng(11)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_io(t):  # stronger in-out
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def bilinear(img, xs, ys):
    h, w = img.shape[:2]
    xs = np.clip(xs, 0, w - 1.001)
    ys = np.clip(ys, 0, h - 1.001)
    x0 = xs.astype(np.int32); y0 = ys.astype(np.int32)
    fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# ---------- artwork plate + depth ----------
art = Image.open(ART_LIGHT)
bbox = art.getchannel('A').getbbox()
art = art.crop(bbox)
PW = 2000
art = art.resize((PW, round(art.height * PW / art.width)), Image.LANCZOS)
PH = art.height
bg = np.full((PH, PW, 3), 17, np.float32)
a = np.array(art).astype(np.float32)
alpha = a[..., 3:] / 255
plate = a[..., :3] * alpha + bg * (1 - alpha)

orig = Image.open(ORIG).convert('RGB')
sess = ort.InferenceSession('tools/models/depth/model.onnx', providers=['CPUExecutionProvider'])
x = np.array(orig.resize((518, 518), Image.BICUBIC)).astype(np.float32) / 255
x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
dep = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
dep = (dep - dep.min()) / (dep.max() - dep.min())
depth = Image.fromarray((dep * 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
depth = np.array(depth).astype(np.float32) / 255
depth = depth * alpha[..., 0]  # empty space sits at the back
PAD = 500
plate = np.pad(plate, ((PAD, PAD), (PAD, PAD), (0, 0)), constant_values=17)
depth = np.pad(depth, PAD)
OSX, OSY = PW / orig.width, PH / orig.height  # original px -> plate px


def P(x, y):
    return (x * OSX + PAD, y * OSY + PAD)


# camera keyframes: (frame, centre in plate px, zoom where 1 = plate width fills 0.96 of output)
KEYS = [
    (0, P(607, 330), 1.22),
    (40, P(607, 345), 1.2),
    (140, P(500, 560), 2.05),
    (150, P(505, 575), 2.08),
    (166, P(607, 650), 0.98),
]


def cam(f):
    for (f0, c0, z0), (f1, c1, z1) in zip(KEYS, KEYS[1:]):
        if f <= f1:
            t = ease_io((f - f0) / (f1 - f0))
            return (c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, z0 * (z1 / z0) ** t)
    return KEYS[-1][1][0], KEYS[-1][1][1], KEYS[-1][2]


qy, qx = np.mgrid[0:OH, 0:OW].astype(np.float32)
BASE = OW * 0.96 / PW
grain = [rng.normal(0, 7, (OH, OW)).astype(np.float32)[..., None] for _ in range(6)]
FLASHES = {28: P(165, 410), 62: P(965, 585), 96: P(1020, 950), 122: P(240, 1050), 146: P(160, 410)}


def star(draw, cx, cy, r, n=10, col=(255, 250, 235)):
    pts = []
    for i in range(n * 2):
        ang = i * np.pi / n + 0.3
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((cx + np.cos(ang) * rr, cy + np.sin(ang) * rr))
    draw.polygon(pts, fill=col)


fmono = ImageFont.truetype(MONO, 30)
fanton = ImageFont.truetype(ANTON, 54)


def rec_overlay(img, f):
    d = ImageDraw.Draw(img)
    m, L, w = 46, 70, 6
    for (x, y, sx, sy) in [(m, m, 1, 1), (OW - m, m, -1, 1), (m, OH - m, 1, -1), (OW - m, OH - m, -1, -1)]:
        d.line([(x, y), (x + L * sx, y)], fill=CREAM, width=w)
        d.line([(x, y), (x, y + L * sy)], fill=CREAM, width=w)
    if (f // 15) % 2 == 0:
        d.ellipse([m + 30, m + 30, m + 58, m + 58], fill=RED)
    d.text((m + 72, m + 28), 'REC', font=fmono, fill=CREAM)
    s = f / FPS
    d.text((OW - m - 30, m + 28), f'00:00:{int(s):02d}:{f % FPS:02d}', font=fmono, fill=CREAM, anchor='ra')
    bx, by = OW - m - 120, OH - m - 62  # battery
    d.rectangle([bx, by, bx + 80, by + 34], outline=CREAM, width=4)
    d.rectangle([bx + 80, by + 10, bx + 88, by + 24], fill=CREAM)
    d.rectangle([bx + 8, by + 8, bx + 46, by + 26], fill=RED)
    d.text((m + 30, OH - m - 64), 'LIVE FROM No.10', font=fmono, fill=CREAM)
    cx, cy = OW / 2, OH / 2  # focus cross
    d.line([(cx - 22, cy), (cx + 22, cy)], fill=CREAM + (0,), width=0)
    return img


def scene_a(f):
    cx, cy, z = cam(f)
    zz = BASE * z
    t = f / NA
    par = np.array([np.sin(t * np.pi * 1.2) * 26, np.cos(t * np.pi) * 12]) * (z / 1.5)
    sx = cx + (qx - OW / 2) / zz
    sy = cy + (qy - OH / 2) / zz
    dd = bilinear(depth[..., None], sx, sy)[..., 0]
    sx = sx - par[0] * (dd - 0.45) / zz * 2.2
    sy = sy - par[1] * (dd - 0.45) / zz * 2.2
    # depth-zoom: near things grow a touch more as we push in
    k = (z - 1) * 0.05
    sx = cx + (sx - cx) * (1 - k * dd)
    sy = cy + (sy - cy) * (1 - k * dd)
    out = bilinear(plate, sx, sy)
    # vignette + grain
    out = out * VIG + grain[f % 6]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
    # flashes
    lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    flash_white = 0.0
    for ff, (px, py) in FLASHES.items():
        k2 = f - ff
        if 0 <= k2 < 6:
            fx = OW / 2 + (px - cx) * zz
            fy = OH / 2 + (py - cy) * zz
            r = [190, 240, 200, 150, 90, 40][k2] * min(1.4, z / 1.4)
            star(d, fx, fy, r)
            star(d, fx, fy, r * 0.45, col=(255, 255, 255))
            flash_white = max(flash_white, [0.5, 0.28, 0.14, 0.06, 0.02, 0][k2])
    img.alpha_composite(lay)
    if flash_white:
        img = Image.blend(img, Image.new('RGBA', (OW, OH), (255, 252, 240, 255)), flash_white)
    return rec_overlay(img, f)


yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
VIG = (1 - 0.38 * (((xx - OW / 2) / OW) ** 2 + ((yy - OH / 2) / OH) ** 2) * 2.2)[..., None]

# ---------- tee mock-ups (drawn at 2x, design printed into the fabric) ----------
S = 2


def tee(colour, design_path):
    W2, H2 = OW * S, OH * S
    pts = [(440, 190), (252, 236), (40, 452), (150, 562), (258, 470), (266, 1188), (814, 1188),
           (822, 470), (930, 562), (1040, 452), (828, 236), (640, 190)]
    neck = [(640, 190), (615, 232), (575, 260), (540, 266), (505, 260), (465, 232), (440, 190)]
    poly = [(x * S, y * S) for x, y in pts + neck[1:]]
    mask = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    base = np.array(colour, np.float32)
    lum = np.zeros((H2, W2), np.float32)
    # soft key light from top-left, folds, cotton grain
    yy2, xx2 = np.mgrid[0:H2, 0:W2].astype(np.float32)
    lum += 0.10 * (1 - ((xx2 - W2 * 0.35) ** 2 + (yy2 - H2 * 0.3) ** 2) ** 0.5 / (W2 * 0.9))
    fold = Image.new('L', (W2, H2), 128)
    fd = ImageDraw.Draw(fold)
    r2 = np.random.default_rng(5)
    for _ in range(9):
        x0 = r2.uniform(280, 800) * S; y0 = r2.uniform(500, 1100) * S
        fd.line([(x0, y0), (x0 + r2.uniform(-90, 90) * S, y0 + r2.uniform(80, 220) * S)],
                fill=int(r2.choice([95, 165])), width=int(r2.uniform(16, 40) * S))
    for sx_ in (1, -1):  # sleeve creases
        cx_ = 540 + sx_ * 300
        fd.line([(cx_ * S, 300 * S), ((540 + sx_ * 395) * S, 520 * S)], fill=100, width=24 * S)
    fold = np.array(fold.filter(ImageFilter.GaussianBlur(28 * S))).astype(np.float32) / 128 - 1
    lum += fold * 0.16
    lum += r2.normal(0, 0.025, lum.shape)
    shade = 1 + lum[..., None]
    fab = np.clip(base * shade + (lum[..., None] * 40 if sum(colour) < 120 else 0), 0, 255)
    fab_img = Image.fromarray(fab.astype(np.uint8)).convert('RGBA')
    # seams + collar rib
    sd = ImageDraw.Draw(fab_img)
    seam = tuple(int(c * 0.72) for c in colour) if sum(colour) > 120 else tuple(min(255, c + 28) for c in colour)
    sd.line([(x * S, y * S) for x, y in neck], fill=seam, width=7 * S, joint='curve')
    sd.line([(x * S, y * S + 26 * S) for x, y in neck[1:-1]], fill=seam, width=2 * S)
    sd.line([(252 * S, 236 * S), (258 * S, 470 * S)], fill=seam, width=3 * S)
    sd.line([(828 * S, 236 * S), (822 * S, 470 * S)], fill=seam, width=3 * S)
    sd.line([(128 * S, 540 * S), (238 * S, 448 * S)], fill=seam, width=2 * S)
    sd.line([(952 * S, 540 * S), (842 * S, 448 * S)], fill=seam, width=2 * S)
    sd.line([(266 * S, 1162 * S), (814 * S, 1162 * S)], fill=seam, width=2 * S)
    # print the design
    des = Image.open(design_path)
    des = des.crop(des.getchannel('A').getbbox())
    dw = 440 * S
    des = des.resize((dw, round(des.height * dw / des.width)), Image.LANCZOS)
    dx, dy = 540 * S - dw // 2, 318 * S
    dl = np.array(des).astype(np.float32)
    patch = lum[dy:dy + des.height, dx:dx + dw][..., None]
    dl[..., :3] = np.clip(dl[..., :3] * (0.9 + patch * 0.9), 0, 255)  # ink follows the fabric
    dl[..., 3] *= 0.96
    fab_img.alpha_composite(Image.fromarray(dl.astype(np.uint8)), (dx, dy))
    # studio backdrop + soft shadow
    bgc = np.zeros((H2, W2, 3), np.float32)
    g = (yy2 / H2)[..., None]
    bgc[:] = np.array([200, 193, 182]) * (1 - g) + np.array([168, 160, 149]) * g
    bgc *= (1 - 0.25 * (((xx2 - W2 / 2) / W2) ** 2 + ((yy2 - H2 / 2) / H2) ** 2) * 2)[..., None]
    out = Image.fromarray(bgc.astype(np.uint8)).convert('RGBA')
    sh = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    sh.paste((40, 34, 30, 120), (14 * S, 22 * S), mask)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26 * S)))
    out.paste(fab_img, (0, 0), mask)
    return out


M = 'inputs/culturejacked/mockups/unisex-classic-tee-white-'
MOCKS = [(M + 'front-2-6b0839f8b16b8.png', 'cover'), (M + 'front-6b0839f8b4912.png', 'cover'),
         (M + 'front-2-6b0839f8b116c.png', 'cover'), (M + 'front-6b0839f8b1967.png', 'contain')]
SEG = [0, 30, 60, 90]  # scene-B frame where each mock-up starts
MIMG = None


def studio(W2, H2):
    yy2, xx2 = np.mgrid[0:H2, 0:W2].astype(np.float32)
    g = (yy2 / H2)[..., None]
    b = np.array([214, 207, 196]) * (1 - g) + np.array([178, 170, 158]) * g
    b *= (1 - 0.22 * (((xx2 - W2 / 2) / W2) ** 2 + ((yy2 - H2 / 2) / H2) ** 2) * 2)[..., None]
    return Image.fromarray(b.astype(np.uint8)).convert('RGBA')


def up4(path):
    sess = ort.InferenceSession('tools/models/esrgan/model.onnx', providers=['CPUExecutionProvider'])
    name = sess.get_inputs()[0].name
    im = Image.open(path).convert('RGBA')
    rgb = np.array(im)[..., :3]
    T, Pd = 128, 12
    h, w, _ = rgb.shape
    srcp = np.pad(rgb.astype(np.float32) / 255, ((Pd, Pd + T), (Pd, Pd + T), (0, 0)), mode='reflect')
    res = np.zeros((h * 4, w * 4, 3), np.float32)
    core = T - 2 * Pd
    for y in range(0, h, core):
        for x in range(0, w, core):
            r = sess.run(None, {name: srcp[y:y + T, x:x + T].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            ch, cw = min(core, h - y), min(core, w - x)
            res[y * 4:(y + ch) * 4, x * 4:(x + cw) * 4] = r[Pd * 4:(Pd + ch) * 4, Pd * 4:(Pd + cw) * 4]
    out = Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)).convert('RGBA')
    out.putalpha(im.getchannel('A').resize(out.size, Image.LANCZOS))
    return out


def mock_plate(path, mode):
    up = up4(path)  # 4000x4000
    W2, H2 = OW * 2, OH * 2
    bgp = studio(W2, H2)
    if mode == 'cover':
        sc = max(W2 / up.width, H2 / up.height)
    else:
        sc = min(W2 / up.width, H2 / up.height) * 1.02
    r = up.resize((round(up.width * sc), round(up.height * sc)), Image.LANCZOS)
    bgp.alpha_composite(r, ((W2 - r.width) // 2, (H2 - r.height) // 2))
    return bgp


def scene_b(f):
    global MIMG
    if MIMG is None:
        MIMG = [mock_plate(p_, m_) for p_, m_ in MOCKS]
    k = f - NA
    idx = max(i for i, st in enumerate(SEG) if k >= st)
    seg_len = (SEG + [NT - NA])[idx + 1] - SEG[idx]
    t = (k - SEG[idx]) / seg_len
    z = 1.0 + 0.06 * ease(t)
    src = MIMG[idx]
    W2, H2 = src.size
    cw, ch = W2 / z, H2 / z
    x0, y0 = (W2 - cw) / 2, (H2 - ch) / 2
    img = src.transform((OW, OH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
    if k >= SEG[1] + 4:
        a_ = int(255 * ease((k - SEG[1] - 4) / 8))
        lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([OW / 2 - 270, 1222, OW / 2 + 270, 1300], 12, fill=(17, 17, 19, int(a_ * 0.9)))
        ld.text((OW / 2, 1262), 'UNISEX CLASSIC TEE', font=fanton, fill=CREAM[:3] + (a_,), anchor='mm')
        img.alpha_composite(lay)
    for st in SEG:
        kk = k - st
        if 0 <= kk < 5:
            img = Image.blend(img, Image.new('RGBA', (OW, OH), (255, 252, 240, 255)), [0.9, 0.55, 0.28, 0.1, 0.03][kk])
    return img


def frame(f):
    return scene_a(f) if f < NA else scene_b(f)


if STILLS:
    for f in (10, 120, 175, 205, 235, 290):
        frame(f).convert('RGB').save(f'{OUT}_still_{f:03d}.jpg', quality=88)
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                       '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', OUT], stdin=subprocess.PIPE)
for f in range(NT):
    ff.stdin.write(frame(f).convert('RGB').tobytes())
    if f % 30 == 0:
        print('frame', f, flush=True)
ff.stdin.close(); ff.wait()
print('wrote', OUT)
