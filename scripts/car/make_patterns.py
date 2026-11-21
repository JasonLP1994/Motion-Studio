# "ASCII x dither" pattern versions of a cut-out car (grammar from the user's reference stills):
# the car rebuilt from blocks of 1-bit ordered dither, ASCII characters picked by brightness,
# checkerboard densities and solid accent blocks, some blocks spilling past the silhouette.
# Palette: green + yellow on black (the user's palette). Deterministic per seed.
# usage: make_patterns.py <car.png> <mask.png> <out_prefix> <screen_scale> <seed> [<seed> ...]
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, msk, prefix, scale = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
seeds = [int(s) for s in sys.argv[5:]]
GREEN, YELLOW, BLACK = (139, 209, 27), (255, 214, 10), (5, 5, 5)
car = Image.open(src).convert("RGBA"); mask = Image.open(msk).convert("L")
PAD = 0.12
W0, H0 = car.size
pw, ph = int(W0 * PAD), int(H0 * PAD)
W, H = W0 + 2 * pw, H0 + 2 * ph
lum = Image.new("L", (W, H), 0); lum.paste(car.convert("L"), (pw, ph))
m = Image.new("L", (W, H), 0); m.paste(mask, (pw, ph))
L = np.array(lum).astype(float) / 255.0
L = np.clip((L - 0.12) * 1.9, 0, 1)  # punchy contrast like a photocopy
M = np.array(m) > 128
Mspill = np.array(m.filter(ImageFilter.MaxFilter(int(40 / scale) | 1))) > 128
cell = max(8, int(round(24 / scale)))  # ~24 px cells on screen (readable characters)
block = cell * 4
COARSE = 3  # neighbouring blocks share a mode -> bigger stepped regions, like the reference
font = ImageFont.truetype("public/fonts/LiberationMono-Bold.ttf", int(cell * 1.15))
RAMP = " .:-=+x/#%@"
bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
for seed in seeds:
    rng = np.random.default_rng(seed)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    px = out.load()
    modes = ["dither", "ascii", "checker", "solid", "hole"]
    probs = [.36, .28, .24, .07, .05]
    gw, gh = W // (block * COARSE) + 2, H // (block * COARSE) + 2
    region = rng.choice(modes, size=(gh, gw), p=probs)
    region_ink = rng.random((gh, gw)) < 0.75
    for by in range(0, H, block):
        for bx in range(0, W, block):
            sub = M[by:by + block, bx:bx + block]; spill = Mspill[by:by + block, bx:bx + block]
            if not spill.any():
                continue
            cover = sub.mean() if sub.size else 0
            gy, gx = by // (block * COARSE), bx // (block * COARSE)
            mode = region[gy, gx] if rng.random() > 0.18 else rng.choice(modes, p=probs)
            ink = GREEN if (region_ink[gy, gx] if rng.random() > 0.15 else rng.random() < 0.5) else YELLOW
            x1, y1 = min(W, bx + block), min(H, by + block)
            if mode == "dither" or cover < 0.25:
                # 1-bit ordered dither of the photo, clipped to the car
                for y in range(by, y1, 2):
                    for x in range(bx, x1, 2):
                        if M[y, x]:
                            on = L[y, x] > bayer[(y // 2) % 4, (x // 2) % 4]
                            d.rectangle([x, y, x + 1, y + 1], fill=(GREEN if on else BLACK) + (255,))
                continue
            d.rectangle([bx, by, x1 - 1, y1 - 1], fill=BLACK + (255,))
            if mode == "ascii":
                for y in range(by, y1, cell):
                    for x in range(bx, x1, cell):
                        v = L[min(H - 1, y + cell // 2), min(W - 1, x + cell // 2)]
                        ch = RAMP[int(v * (len(RAMP) - 1))]
                        if ch != " ":
                            d.text((x, y - cell * 0.15), ch, font=font, fill=ink + (255,))
            elif mode == "checker":
                step = int(rng.choice([1, 1, 2]))
                s = max(2, cell // 2)
                for y in range(by, y1, s):
                    for x in range(bx, x1, s):
                        if ((x // s) + (y // s)) % (step + 1) == 0:
                            d.rectangle([x, y, x + s - 1, y + s - 1], fill=ink + (255,))
            elif mode == "solid":
                d.rectangle([bx, by, x1 - 1, y1 - 1], fill=ink + (255,))
                # a few dropped-out cells, like the reference's punched blocks
                for _ in range(int(rng.integers(2, 6))):
                    cx = bx + int(rng.integers(0, max(1, (x1 - bx) // cell))) * cell
                    cy = by + int(rng.integers(0, max(1, (y1 - by) // cell))) * cell
                    d.rectangle([cx, cy, cx + cell - 1, cy + cell - 1], fill=BLACK + (255,))
            # "hole" leaves the black block
    out.save(f"{prefix}pattern_{seed}.png")
print("ok", prefix, (W, H), "pad", (pw, ph), "cell", cell)
