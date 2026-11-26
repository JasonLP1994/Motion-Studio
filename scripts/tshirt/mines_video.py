"""CultureJacked "Back to the Mines" Etsy video: 10 s, silent, 1080x1350, 30 fps.
Dark mine: headlamp beam sweep with dust -> lamp on -> 2.5D parallax push with embers ->
pickaxe impact on MINES (shake, punch, rock dust) -> pull out -> light dims to loop.

usage: python3 -I scripts/tshirt/mines_video.py <art_light.png> <orig.png> <out.mp4> [stills]
"""
import sys, subprocess
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFilter

ART, ORIG, OUT = sys.argv[1:4]
STILLS = len(sys.argv) > 4 and sys.argv[4] == 'stills'
OW, OH, FPS, NT = 1080, 1350, 30, 300
F_ON, F_HIT = 66, 190
rng = np.random.default_rng(21)


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def bilinear(img, xs, ys):
    h, w = img.shape[:2]
    xs = np.clip(xs, 0, w - 1.001); ys = np.clip(ys, 0, h - 1.001)
    x0 = xs.astype(np.int32); y0 = ys.astype(np.int32)
    fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    return ((img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy)
            + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy)


# ---- plate + depth
art = Image.open(ART)
art = art.crop(art.getchannel('A').getbbox())
PW = 2000
art = art.resize((PW, round(art.height * PW / art.width)), Image.LANCZOS)
PH = art.height
BG = np.array([10, 8, 7], np.float32)
a = np.array(art).astype(np.float32)
al = a[..., 3:] / 255
plate = a[..., :3] * al + BG * (1 - al)
orig = Image.open(ORIG).convert('RGB')
sess = ort.InferenceSession('tools/models/depth/model.onnx', providers=['CPUExecutionProvider'])
x = np.array(orig.resize((518, 518), Image.BICUBIC)).astype(np.float32) / 255
x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
dep = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
dep = (dep - dep.min()) / (dep.max() - dep.min())
depth = np.array(Image.fromarray((dep * 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC)
                 .filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255 * al[..., 0]
PAD = 600
plate = np.concatenate([plate, np.ones((PH, PW, 1), np.float32)], axis=2)  # 4th channel = inside art
plate = np.pad(plate, ((PAD, PAD), (PAD, PAD), (0, 0)))
plate[..., :3][plate[..., 3] == 0] = BG
depth = np.pad(depth, PAD)
SX, SY = PW / orig.width, PH / orig.height


def P(x_, y_):
    return (x_ * SX + PAD, y_ * SY + PAD)


LAMP, LANTERN = P(488, 140), P(238, 330)
KEYS = [(0, P(514, 560), 1.12), (F_ON, P(500, 420), 1.18), (F_ON + 14, P(470, 140), 1.75),
        (120, P(480, 300), 2.05), (F_HIT - 4, P(520, 800), 1.55), (F_HIT + 10, P(520, 790), 1.62),
        (238, P(514, 562), 0.97), (NT, P(514, 560), 1.0)]


def cam(f):
    for (f0, c0, z0), (f1, c1, z1) in zip(KEYS, KEYS[1:]):
        if f <= f1:
            t = ease_io((f - f0) / (f1 - f0))
            return c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, z0 * (z1 / z0) ** t
    return KEYS[-1][1][0], KEYS[-1][1][1], KEYS[-1][2]


qy, qx = np.mgrid[0:OH, 0:OW].astype(np.float32)
BASE = OW * 0.96 / PW
VIG = (1 - 0.45 * (((qx - OW / 2) / OW) ** 2 + ((qy - OH / 2) / OH) ** 2) * 2.2)[..., None]
grain = [rng.normal(0, 6, (OH, OW)).astype(np.float32)[..., None] for _ in range(6)]
flick = np.clip(1 + 0.18 * np.sin(np.arange(NT) * 0.9) + rng.normal(0, 0.1, NT), 0.6, 1.4)

# particles in plate px
N_E = 140  # embers
emb = np.c_[rng.uniform(PAD, PAD + PW, N_E), rng.uniform(PAD, PAD + PH, N_E), rng.uniform(0.6, 2.2, N_E),
            rng.uniform(0, 6.28, N_E), rng.uniform(1.5, 4.5, N_E)]
N_D = 220  # dust motes
dust = np.c_[rng.uniform(PAD, PAD + PW, N_D), rng.uniform(PAD, PAD + PH, N_D), rng.uniform(0.6, 1.8, N_D),
             rng.uniform(0, 6.28, N_D)]
N_R = 90   # rock burst from the MINES impact
mx, my = P(520, 870)
ang = rng.uniform(np.pi * 0.95, np.pi * 2.05, N_R)
spd = rng.uniform(6, 26, N_R)
rocks = np.c_[np.full(N_R, mx) + rng.normal(0, 160, N_R), np.full(N_R, my), np.cos(ang) * spd, np.sin(ang) * spd,
              rng.uniform(2, 7, N_R)]


def beam_pos(f):
    t = f / F_ON
    path = [P(120, 760), P(330, 420), P(560, 260), P(780, 520), P(500, 300)]
    seg = min(int(t * 4), 3)
    tt = ease_io(t * 4 - seg)
    (x0, y0), (x1, y1) = path[seg], path[seg + 1]
    return x0 + (x1 - x0) * tt, y0 + (y1 - y0) * tt


def frame(f):
    cx, cy, z = cam(f)
    zz = BASE * z
    shake = np.zeros(2)
    if F_HIT <= f < F_HIT + 14:
        k = f - F_HIT
        shake = rng.normal(0, 22 * (1 - k / 14), 2)
        zz *= 1 + 0.10 * (1 - k / 14) ** 2
    t = f / NT
    par = np.array([np.sin(t * np.pi * 2) * 22, np.cos(t * np.pi * 1.4) * 10]) * (z / 1.4)
    sx = cx + (qx - OW / 2 - shake[0]) / zz
    sy = cy + (qy - OH / 2 - shake[1]) / zz
    dd = bilinear(depth[..., None], sx, sy)[..., 0]
    sx = sx - par[0] * (dd - 0.45) / zz * 2.2
    sy = sy - par[1] * (dd - 0.45) / zz * 2.2
    out = bilinear(plate, sx, sy)[..., :3]

    def to_screen(px, py):
        return OW / 2 + (px - cx) * zz + shake[0], OH / 2 + (py - cy) * zz + shake[1]

    # lighting: ambient + headlamp beam + lantern glow
    if f < F_ON:
        amb = 0.025
    elif f < F_ON + 8:
        amb = 0.04 + 0.96 * (f - F_ON) / 8
    elif f > NT - 16:
        amb = 1 - 0.9 * ease_io((f - (NT - 16)) / 16)
    else:
        amb = 1.0
    L = np.full((OH, OW), amb, np.float32)
    if f < F_ON + 8 or f > NT - 16:
        bx, by = beam_pos(f) if f < F_ON else LAMP
        ex, ey = to_screen(bx, by)
        r = 200 * zz / BASE / 1.15
        spot = np.exp(-(((qx - ex) ** 2 + (qy - ey) ** 2) / (2 * r * r)))
        L += spot * (1.0 if f < F_ON else 0.8) * (1 - amb)
    lx, ly = to_screen(*LANTERN)
    rl = 200 * zz / BASE
    L += 0.35 * flick[f] * np.exp(-(((qx - lx) ** 2 + (qy - ly) ** 2) / (2 * rl * rl))) * (1.3 - amb)
    out = out * L[..., None]
    warm = np.exp(-(((qx - lx) ** 2 + (qy - ly) ** 2) / (2 * (rl * 1.6) ** 2)))[..., None]
    out = out + warm * np.array([60, 30, 5]) * flick[f] * 0.5
    out = out * VIG + grain[f % 6]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')

    # particles
    glow = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    sharp = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    gd, sd = ImageDraw.Draw(glow), ImageDraw.Draw(sharp)
    if f >= F_ON - 6:
        for ex_, ey_, sp, ph, sz in emb:
            yy_ = (ey_ - f * sp * 3.2 - PAD) % PH + PAD
            xx_ = ex_ + np.sin(f * 0.06 + ph) * 24
            X, Y = to_screen(xx_, yy_)
            if -20 < X < OW + 20 and -20 < Y < OH + 20:
                s_ = sz * zz / BASE * 0.7
                flk = 0.6 + 0.4 * np.sin(f * 0.4 + ph)
                gd.ellipse([X - s_ * 3, Y - s_ * 3, X + s_ * 3, Y + s_ * 3], fill=(255, 120, 20, int(110 * flk)))
                sd.ellipse([X - s_, Y - s_, X + s_, Y + s_], fill=(255, 214, 120, int(255 * flk)))
    if f < F_ON + 20:
        bx, by = beam_pos(min(f, F_ON - 1))
        for dx_, dy_, sp, ph in dust:
            xx_ = dx_ + np.sin(f * 0.03 + ph) * 40 + f * sp * 0.6
            yy_ = dy_ + np.cos(f * 0.025 + ph) * 30
            d2 = (xx_ - bx) ** 2 + (yy_ - by) ** 2
            vis = np.exp(-d2 / (2 * 300 ** 2)) * (1 - max(0, f - F_ON) / 20)
            if vis > 0.05:
                X, Y = to_screen(xx_, yy_)
                s_ = 1.2 + sp
                sd.ellipse([X - s_, Y - s_, X + s_, Y + s_], fill=(255, 240, 210, int(200 * vis)))
    if f >= F_HIT:
        k = f - F_HIT
        for rx, ry, vx, vy, sz in rocks:
            px_, py_ = rx + vx * k * 2.2, ry + vy * k * 2.2 + 0.9 * (k * 2.2) ** 2 * 0.6
            X, Y = to_screen(px_, py_)
            fade = max(0, 1 - k / 34)
            if fade > 0:
                s_ = sz * zz / BASE * 0.8
                sd.ellipse([X - s_, Y - s_, X + s_, Y + s_], fill=(150, 130, 112, int(255 * fade)))
                gd.ellipse([X - s_ * 4, Y - s_ * 4, X + s_ * 4, Y + s_ * 4], fill=(120, 105, 90, int(70 * fade)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(sharp)
    for fs, strength, col in ((F_ON, 0.45, (255, 240, 205)), (F_HIT, 0.35, (255, 170, 80))):
        k = f - fs
        if 0 <= k < 6:
            img = Image.blend(img, Image.new('RGBA', (OW, OH), col + (255,)), strength * (1 - k / 6))
    return img


if STILLS:
    for f in (30, 80, 130, 192, 260):
        frame(f).convert('RGB').save(f'{OUT}_still_{f:03d}.jpg', quality=88)
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', '-an', OUT], stdin=subprocess.PIPE)
for f in range(NT):
    ff.stdin.write(frame(f).convert('RGB').tobytes())
ff.stdin.close(); ff.wait()
print('wrote', OUT)
