"""Glitch end card: the film's last frame glitches out, flickers, then the logo glitches in on its own background
colour and settles clean. Frames continue the film's numbering so they encode as one sequence.
Usage: tools/ai-venv/bin/python scripts/post/glitch_endcard.py <last_frame.png> <logo.png> <out_dir> <first_frame> [n_frames]
       [--bg auto] [--accent 198,255,0] [--accent2 31,59,255] [--logo-w 0.42]
--bg auto samples the logo's own corner colour, so the logo sits exactly as designed.
"""
import argparse, os, random
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("last"); ap.add_argument("logo"); ap.add_argument("out"); ap.add_argument("first", type=int); ap.add_argument("n", type=int, nargs="?", default=90)
ap.add_argument("--bg", default="auto"); ap.add_argument("--accent", default="198,255,0"); ap.add_argument("--accent2", default="31,59,255")
ap.add_argument("--logo-w", type=float, default=0.42)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
rng = random.Random(7); nrng = np.random.default_rng(7)
hero = np.asarray(Image.open(a.last).convert("RGB")).astype(np.float32)
H, W = hero.shape[:2]
logo = Image.open(a.logo).convert("RGB")
bg = np.array(logo.getpixel((3, 3)), np.float32) if a.bg == "auto" else np.array([int(v) for v in a.bg.split(",")], np.float32)
acc = np.array([int(v) for v in a.accent.split(",")], np.float32); acc2 = np.array([int(v) for v in a.accent2.split(",")], np.float32)
lw = int(W * a.logo_w); lh = int(logo.height * lw / logo.width)
lg = np.asarray(logo.resize((lw, lh), Image.LANCZOS)).astype(np.float32)
card = np.ones((H, W, 3), np.float32) * bg
y0, x0 = (H - lh) // 2, (W - lw) // 2
card[y0:y0 + lh, x0:x0 + lw] = lg


def rgb_split(img, d):
    out = img.copy(); d = int(d)
    if d: out[..., 0] = np.roll(img[..., 0], -d, axis=1); out[..., 2] = np.roll(img[..., 2], d, axis=1)
    return out


def slices(img, amount, count):
    out = img.copy()
    for _ in range(count):
        y = rng.randrange(0, H - 4); h = rng.randrange(4, max(5, int(H * 0.08)))
        out[y:y + h] = np.roll(out[y:y + h], int(rng.uniform(-1, 1) * amount * W), axis=1)
    return out


def blocks(img, count, cols):
    out = img.copy()
    for _ in range(count):
        bw, bh = rng.randrange(40, 380), rng.randrange(6, 60); x, y = rng.randrange(0, W - bw), rng.randrange(0, H - bh)
        out[y:y + bh, x:x + bw] = rng.choice(cols)
    return out


def scanlines(img, k):
    out = img.copy(); out[::3] *= (1 - k); return out


def grain(img, s=5.0):
    return img + nrng.standard_normal((H, W, 1)).astype(np.float32) * s


n = a.n; out_seq = []
for i in range(n):
    t = i / n
    if i < 12:                                     # glitch-out of the hero shot, ramping up
        k = (i + 1) / 12
        f = slices(rgb_split(hero, 4 + 30 * k), 0.08 * k, int(3 + 14 * k))
        f = blocks(f, int(2 + 10 * k), [acc, acc2, np.zeros(3), bg])
        f = scanlines(f, 0.35 * k)
        if i in (7, 10): f = f * 0.15
    elif i < 17:                                   # hard flicker: black / cream / inverted / accent
        f = [np.zeros((H, W, 3)), card * 0 + bg, 255 - hero, np.ones((H, W, 3)) * acc, np.zeros((H, W, 3))][i - 12].astype(np.float32)
    elif i < 36:                                   # logo glitches in, settling
        k = 1 - (i - 17) / 19
        f = slices(rgb_split(card, 22 * k), 0.05 * k, int(10 * k))
        if k > 0.4: f = blocks(f, int(6 * k), [acc, acc2, np.zeros(3)])
        if i in (19, 23): f = np.ones((H, W, 3), np.float32) * bg
        f = scanlines(f, 0.25 * k)
    elif 70 <= i < 73:                             # one small blip during the hold
        f = slices(rgb_split(card, 10), 0.02, 4)
    else:
        f = card
    f = grain(f, 4.0)
    Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(os.path.join(a.out, f"f_{a.first + i:04d}.png"))
print(f"end card frames {a.first}-{a.first + n - 1} -> {a.out}  (bg {bg.astype(int).tolist()})")
