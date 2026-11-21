# Paper-style "ASCII x dither" frames of a full-frame car photo (grammar from the user's ASCII x
# dither reference stills): white paper, the car rebuilt in stepped regions of black 1-bit dither
# (red where the paint is), black/red ASCII by brightness, checkerboards and solid red blocks.
# usage: make_patterns_paper.py <photo.png> <paint_mask.png> <out_prefix> <screen_scale> <seed>...
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, msk, prefix, scale = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
seeds = [int(s) for s in sys.argv[5:]]
RED, BLACK, PAPER = (226, 18, 24), (12, 12, 12), (238, 236, 231)
im = Image.open(src).convert("RGB"); W, H = im.size
L = np.clip((np.array(im.convert("L")).astype(float) / 255 - 0.05) * 2.3, 0, 1)
paint = np.array(Image.open(msk).convert("L")) > 128
near = np.array(Image.open(msk).convert("L").filter(ImageFilter.MaxFilter(int(90 / scale) | 1))) > 128
cell = max(8, int(round(26 / scale))); block = cell * 4; COARSE = 3
font = ImageFont.truetype("public/fonts/LiberationMono-Bold.ttf", int(cell * 1.15))
RAMP = "@%#x/+=-:. "  # dark -> light (ink on paper)
bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
modes = ["dither", "ascii", "checker", "solid", "hole"]; probs = [.38, .26, .2, .1, .06]
for seed in seeds:
    rng = np.random.default_rng(seed)
    out = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(out)
    # paper grain
    g = (rng.random((H, W)) * 14).astype(np.uint8)
    out = Image.fromarray(np.clip(np.array(out).astype(int) - g[..., None], 0, 255).astype(np.uint8)); d = ImageDraw.Draw(out)
    gw, gh = W // (block * COARSE) + 2, H // (block * COARSE) + 2
    region = rng.choice(modes, size=(gh, gw), p=probs); red_ink = rng.random((gh, gw)) < 0.45
    for by in range(0, H, block):
        for bx in range(0, W, block):
            if not near[by:by + block, bx:bx + block].any():
                continue
            gy, gx = by // (block * COARSE), bx // (block * COARSE)
            mode = region[gy, gx] if rng.random() > 0.18 else rng.choice(modes, p=probs)
            ink = RED if (red_ink[gy, gx] if rng.random() > 0.15 else rng.random() < 0.5) else BLACK
            x1, y1 = min(W, bx + block), min(H, by + block)
            if mode == "dither":
                for y in range(by, y1, 2):
                    for x in range(bx, x1, 2):
                        if L[y, x] < bayer[(y // 2) % 4, (x // 2) % 4]:  # dark -> ink
                            d.rectangle([x, y, x + 1, y + 1], fill=RED if paint[y, x] and L[y, x] > 0.18 else BLACK)
            elif mode == "ascii":
                for y in range(by, y1, cell):
                    for x in range(bx, x1, cell):
                        v = L[min(H - 1, y + cell // 2), min(W - 1, x + cell // 2)]
                        ch = RAMP[int(v * (len(RAMP) - 1))]
                        if ch != " ":
                            d.text((x, y - cell * 0.15), ch, font=font, fill=ink)
            elif mode == "checker":
                s = max(2, cell // 2); step = int(rng.choice([1, 1, 2]))
                for y in range(by, y1, s):
                    for x in range(bx, x1, s):
                        if ((x // s) + (y // s)) % (step + 1) == 0:
                            d.rectangle([x, y, x + s - 1, y + s - 1], fill=ink)
            elif mode == "solid":
                d.rectangle([bx, by, x1 - 1, y1 - 1], fill=RED)
                for _ in range(int(rng.integers(2, 6))):
                    cx = bx + int(rng.integers(0, max(1, (x1 - bx) // cell))) * cell
                    cy = by + int(rng.integers(0, max(1, (y1 - by) // cell))) * cell
                    d.rectangle([cx, cy, cx + cell - 1, cy + cell - 1], fill=PAPER)
            else:
                d.rectangle([bx, by, x1 - 1, y1 - 1], fill=BLACK)
    out.save(f"{prefix}pattern_{seed}.png")
print("ok", prefix, (W, H), "cell", cell)
