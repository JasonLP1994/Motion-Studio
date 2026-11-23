# Dance logo end card: 64 frames (2.67 s) on the render's blue, hot-pink "p." circle springs in with a pink glow, the
# "phillips digital" wordmark (cut from a copy of inputs/phillips-digital-logo.jpg) wipes on. Usage: python3 scripts/dance_endcard.py OUTDIR
from PIL import Image, ImageFilter, ImageDraw
import math, os, sys
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
bgc = (31, 93, 216); W, H = 1920, 1080
logo = Image.open("public/pd01/logo_circle_pink.png").convert("RGBA"); word = Image.open("work/dance/logo_wordmark_full.png").convert("RGBA")
def spring(t): return 1 - math.exp(-7 * t) * math.cos(11 * t) if t > 0 else 0
for f in range(64):
    t = f / 24; im = Image.new("RGBA", (W, H), (*bgc, 255))
    size = int(330 * max(0.001, spring(t)))
    if size > 4:
        a = Image.new("L", (size + 220, size + 220), 0); ImageDraw.Draw(a).ellipse((110, 110, size + 110, size + 110), fill=int(190 * min(1, t * 3)))
        a = a.filter(ImageFilter.GaussianBlur(48)); glow = Image.new("RGBA", a.size, (255, 60, 170, 255)); glow.putalpha(a)
        im.alpha_composite(glow, (W // 2 - size // 2 - 110, H // 2 - 90 - size // 2 - 110))
        lg = logo.resize((size, size), Image.LANCZOS).rotate(-30 * (1 - min(1, t * 2.5)), resample=Image.BICUBIC)
        im.alpha_composite(lg, (W // 2 - size // 2, H // 2 - 90 - size // 2))
    wt = min(1, max(0, (t - 0.45) / 0.45)); wt = wt * wt * (3 - 2 * wt)
    if wt > 0:
        ww = 760; wd = word.resize((ww, int(word.size[1] * ww / word.size[0])), Image.LANCZOS)
        im.alpha_composite(wd.crop((0, 0, max(1, int(ww * wt)), wd.size[1])), (W // 2 - ww // 2, H // 2 + 120))
    im.convert("RGB").save(f"{out}/e_{f + 1:04d}.png")
print("endcard ok")
