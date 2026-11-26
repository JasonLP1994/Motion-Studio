"""CultureJacked "Optimistical Delusion" Etsy video: 10 s, silent, 1080x1350, 30 fps.
Springy pop-in, sunglasses glint, 2.5D push with sparkles, champagne bubbles and a
cartoon money rain, DELUSION punch with sparkle burst, then the tee mock-ups.

usage: python3 -I scripts/tshirt/delusion_video.py <art_light.png> <orig.png> <mockup_dir> <out.mp4> [stills]
"""
import sys, subprocess
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ART, ORIG, MDIR, OUT = sys.argv[1:5]
STILLS = len(sys.argv) > 5 and sys.argv[5] == 'stills'
OW, OH, FPS, NT = 1080, 1350, 30, 300
NA, F_HIT = 180, 150
PINK, CREAM, GOLD = (236, 64, 122), (250, 236, 214), (255, 214, 110)
ANTON = 'public/fonts/anton-latin-400-normal.woff2'
rng = np.random.default_rng(8)


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def spring(t):  # 0 -> 1 with overshoot
    t = max(t, 0.0)
    return 1 - np.exp(-6 * t) * np.cos(9 * t)


def bilinear(img, xs, ys):
    h, w = img.shape[:2]
    xs = np.clip(xs, 0, w - 1.001); ys = np.clip(ys, 0, h - 1.001)
    x0 = xs.astype(np.int32); y0 = ys.astype(np.int32)
    fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    return ((img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy)
            + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy)


# ---- backdrop: deep plum with a soft pink glow
qy, qx = np.mgrid[0:OH, 0:OW].astype(np.float32)
glow = np.exp(-(((qx - OW / 2) / (OW * 0.55)) ** 2 + ((qy - OH * 0.45) / (OH * 0.5)) ** 2))[..., None]
BACK = np.array([34, 10, 26], np.float32) * (1 - glow) + np.array([120, 30, 72], np.float32) * glow

# ---- plate + depth
art = Image.open(ART)
art = art.crop(art.getchannel('A').getbbox())
PW = 2000
art = art.resize((PW, round(art.height * PW / art.width)), Image.LANCZOS)
PH = art.height
a = np.array(art).astype(np.float32)
plate = np.dstack([a[..., :3] * (a[..., 3:] / 255), a[..., 3:] / 255])  # premultiplied + alpha
orig = Image.open(ORIG).convert('RGB')
sess = ort.InferenceSession('tools/models/depth/model.onnx', providers=['CPUExecutionProvider'])
x = np.array(orig.resize((518, 518), Image.BICUBIC)).astype(np.float32) / 255
x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
dep = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
dep = (dep - dep.min()) / (dep.max() - dep.min())
depth = np.array(Image.fromarray((dep * 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC)
                 .filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255 * plate[..., 3]
PAD = 700
plate = np.pad(plate, ((PAD, PAD), (PAD, PAD), (0, 0)))
depth = np.pad(depth, PAD)
SX, SY = PW / orig.width, PH / orig.height


def P(x_, y_):
    return (x_ * SX + PAD, y_ * SY + PAD)


KEYS = [(0, P(514, 560), 1.0), (40, P(514, 540), 1.05), (62, P(520, 110), 1.7), (120, P(515, 300), 2.15),
        (F_HIT - 6, P(520, 760), 1.6), (F_HIT + 6, P(520, 750), 1.66), (176, P(514, 560), 0.98), (NA, P(514, 560), 0.98)]


def cam(f):
    for (f0, c0, z0), (f1, c1, z1) in zip(KEYS, KEYS[1:]):
        if f <= f1:
            t = ease_io((f - f0) / (f1 - f0))
            return c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, z0 * (z1 / z0) ** t
    return KEYS[-1][1][0], KEYS[-1][1][1], KEYS[-1][2]


BASE = OW * 0.94 / PW
SPARKLES = [P(290, 222), P(732, 182), P(66, 466), P(905, 372), P(790, 240), P(500, 1000), P(560, 905), P(250, 600)]
GLASS = P(205, 360)
LENS = (P(470, 250), P(600, 255))

# money rain: one bill sprite, many falling copies
BILL = Image.new('RGBA', (120, 54), (0, 0, 0, 0))
bd = ImageDraw.Draw(BILL)
bd.rounded_rectangle([1, 1, 118, 52], 6, fill=(150, 196, 140, 255), outline=(40, 70, 40, 255), width=3)
bd.rounded_rectangle([10, 9, 109, 44], 4, outline=(60, 100, 60, 255), width=2)
bd.ellipse([44, 12, 76, 42], fill=(110, 160, 100, 255), outline=(40, 70, 40, 255), width=2)
bd.text((60, 27), '$', font=ImageFont.truetype(ANTON, 26), fill=(30, 60, 30, 255), anchor='mm')
N_B = 26
bills = np.c_[rng.uniform(-60, OW + 60, N_B), rng.uniform(-OH, 0, N_B), rng.uniform(3, 7, N_B),
              rng.uniform(0, 6.28, N_B), rng.uniform(0.85, 1.6, N_B)]
N_Q = 40  # champagne bubbles
bub = np.c_[rng.uniform(-40, 40, N_Q), rng.uniform(0, 1, N_Q), rng.uniform(0.6, 1.4, N_Q), rng.uniform(3, 8, N_Q)]
N_C = 70  # sparkle burst on DELUSION
cang = rng.uniform(0, 6.28, N_C); cspd = rng.uniform(10, 34, N_C)
ccol = [PINK, GOLD, CREAM, (255, 140, 190)]


def star4(d, cx, cy, r, col, a_=255):
    pts = [(cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy), (cx + r * 0.22, cy + r * 0.22),
           (cx, cy + r), (cx - r * 0.22, cy + r * 0.22), (cx - r, cy), (cx - r * 0.22, cy - r * 0.22)]
    d.polygon(pts, fill=col[:3] + (int(a_),))


def money(img, f, density=1.0, sides=False):
    for i, (bx, by, sp, ph, sc) in enumerate(bills):
        if i / N_B > density:
            continue
        if sides and 230 < bx < 850:  # keep the printed design clear
            continue
        y = (by + f * sp * 3.2) % (OH + 300) - 150
        xx = bx + np.sin(f * 0.07 + ph) * 50
        rot = np.sin(f * 0.09 + ph) * 40 + ph * 30
        flip = abs(np.cos(f * 0.11 + ph)) * 0.7 + 0.3  # flutter
        sp_ = BILL.resize((max(8, int(120 * sc)), max(4, int(54 * sc * flip))), Image.BICUBIC).rotate(rot, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(sp_, (int(xx - sp_.width / 2), int(y - sp_.height / 2)))


def scene_a(f):
    cx, cy, z = cam(f)
    zz = BASE * z
    pop = spring(f / 22) if f < 40 else 1.0
    zz *= 0.55 + 0.45 * pop
    if F_HIT <= f < F_HIT + 10:
        zz *= 1 + 0.12 * (1 - (f - F_HIT) / 10) ** 2
    t = f / NA
    par = np.array([np.sin(t * np.pi * 2) * 20, np.cos(t * np.pi * 1.6) * 10]) * (z / 1.4)
    sx = cx + (qx - OW / 2) / zz
    sy = cy + (qy - OH / 2) / zz
    dd = bilinear(depth[..., None], sx, sy)[..., 0]
    sx = sx - par[0] * (dd - 0.45) / zz * 2.2
    sy = sy - par[1] * (dd - 0.45) / zz * 2.2
    s = bilinear(plate, sx, sy)
    out = s[..., :3] + BACK * (1 - s[..., 3:])
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')

    def scr(px, py):
        return OW / 2 + (px - cx) * zz, OH / 2 + (py - cy) * zz

    lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    gl = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    d, g = ImageDraw.Draw(lay), ImageDraw.Draw(gl)
    k_ = zz / BASE
    # twinkles
    for i, (px, py) in enumerate(SPARKLES):
        tw = max(0.0, np.sin(f * 0.22 + i * 1.7))
        if tw > 0.05:
            X, Y = scr(px, py)
            r = (18 + 26 * tw) * k_ * 0.8
            star4(g, X, Y, r * 1.6, GOLD, 120 * tw)
            star4(d, X, Y, r, (255, 250, 230), 255 * tw)
    # sunglasses glint (sweep at f 26-44)
    if 26 <= f < 46:
        tt = (f - 26) / 20
        for j, (lx, ly) in enumerate(LENS):
            X, Y = scr(lx + (tt - 0.5) * 120 * SX, ly)
            a_ = np.sin(np.pi * tt) * 255
            star4(g, X, Y, 70 * k_, (255, 255, 255), a_ * 0.5)
            star4(d, X, Y, 38 * k_, (255, 255, 255), a_)
    # champagne bubbles
    if f >= 50:
        gx, gy = GLASS
        for bx, ph, sp, sz in bub:
            prog = (ph + (f - 50) * 0.012 * sp) % 1
            X, Y = scr(gx + bx * SX, gy - prog * 260 * SY)
            r = sz * k_ * 0.6
            d.ellipse([X - r, Y - r, X + r, Y + r], outline=(255, 248, 220, int(220 * (1 - prog))), width=max(1, int(r * 0.35)))
    # DELUSION sparkle burst
    if F_HIT <= f < F_HIT + 26:
        kk = f - F_HIT
        X0, Y0 = scr(*P(520, 760))
        for i in range(N_C):
            dist = cspd[i] * kk * 1.6 * k_ * 0.6
            X, Y = X0 + np.cos(cang[i]) * dist, Y0 + np.sin(cang[i]) * dist * 0.8 + kk * kk * 0.5
            star4(d, X, Y, (14 - kk * 0.4) * k_ * 0.6, ccol[i % 4], 255 * (1 - kk / 26))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
    img.alpha_composite(lay)
    if f >= 52:
        money(img, f - 52, density=min(1.0, (f - 52) / 40))
    for fs, st, col in ((0, 0.0, CREAM), (F_HIT, 0.4, (255, 150, 200))):
        kk = f - fs
        if st and 0 <= kk < 6:
            img = Image.blend(img, Image.new('RGBA', (OW, OH), col + (255,)), st * (1 - kk / 6))
    return img


# ---- scene B: tee mock-ups
MOCKS = ['v4_seated.png', 'v4_woman.png', 'v4_flatlay.png', 'v4_product.png']
SEG = [0, 30, 60, 90]
MIMG = None
fanton = ImageFont.truetype(ANTON, 50)


def studio(W2, H2):
    yy2, xx2 = np.mgrid[0:H2, 0:W2].astype(np.float32)
    gg = (yy2 / H2)[..., None]
    b = np.array([246, 214, 224]) * (1 - gg) + np.array([226, 182, 198]) * gg  # blush pink studio
    return Image.fromarray(b.astype(np.uint8)).convert('RGBA')


def plate_b(name, mode):
    up = Image.open(f'{MDIR}/{name}')
    W2, H2 = OW * 2, OH * 2
    bgp = studio(W2, H2)
    sc = max(W2 / up.width, H2 / up.height) if mode == 'cover' else min(W2 / up.width, H2 / up.height) * 1.02
    r = up.resize((round(up.width * sc), round(up.height * sc)), Image.LANCZOS)
    bgp.alpha_composite(r, ((W2 - r.width) // 2, (H2 - r.height) // 2))
    return bgp


def scene_b(f):
    global MIMG
    if MIMG is None:
        MIMG = [plate_b(m, 'contain' if 'product' in m else 'cover') for m in MOCKS]
    k = f - NA
    idx = max(i for i, st in enumerate(SEG) if k >= st)
    seg_len = (SEG + [NT - NA])[idx + 1] - SEG[idx]
    t = (k - SEG[idx]) / seg_len
    z = 1.0 + 0.06 * ease_io(t)
    src = MIMG[idx]
    W2, H2 = src.size
    cw, ch = W2 / z, H2 / z
    x0, y0 = (W2 - cw) / 2, (H2 - ch) / 2
    img = src.transform((OW, OH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
    money(img, f, density=0.8, sides=True)
    if k >= SEG[1] + 4:
        a_ = int(255 * ease_io((k - SEG[1] - 4) / 8))
        lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([OW / 2 - 300, 1218, OW / 2 + 300, 1300], 40, fill=PINK + (a_,))
        ld.text((OW / 2, 1260), 'DELULU IS THE SOLULU', font=fanton, fill=CREAM + (a_,), anchor='mm')
        star4(ld, OW / 2 - 330, 1240, 22, GOLD, a_); star4(ld, OW / 2 + 330, 1282, 18, GOLD, a_)
        img.alpha_composite(lay)
    for st in SEG:
        kk = k - st
        if 0 <= kk < 5:
            img = Image.blend(img, Image.new('RGBA', (OW, OH), (255, 236, 244, 255)), [0.9, 0.55, 0.28, 0.1, 0.03][kk])
    return img


def frame(f):
    return scene_a(f) if f < NA else scene_b(f)


if STILLS:
    for f in (12, 36, 100, 154, 200, 250):
        frame(f).convert('RGB').save(f'{OUT}_still_{f:03d}.jpg', quality=88)
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', '-an', OUT], stdin=subprocess.PIPE)
for f in range(NT):
    ff.stdin.write(frame(f).convert('RGB').tobytes())
ff.stdin.close(); ff.wait()
print('wrote', OUT)
