# Cut a car out of a studio photo with a shiny floor: colour-key the paint/lights above a ground
# line (so floor reflections are ignored), then fill each column solid from the car's top edge down
# to the ground (brings back black tyres, diffuser and trim). Saves RGBA + mask + a check image.
import sys, numpy as np
from PIL import Image, ImageFilter
src, out, ground = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert("RGB")
hsv = np.array(im.convert("HSV")).astype(int)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
key = (((H > 35) & (H < 105) & (S > 80) & (V > 45)) | (((H < 14) | (H > 238)) & (S > 110) & (V > 60)))
key[ground:, :] = False
m = Image.fromarray((key * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15))
k = np.array(m) > 128
# drop specks: columns need a decent run of paint to count
tops = np.full(k.shape[1], ground)
for x in range(k.shape[1]):
    ys = np.nonzero(k[:, x])[0]
    if len(ys) > 25:
        tops[x] = ys[0]
# smooth the top edge: a running median removes glare slivers narrower than ~10 px, keeps mirrors
r = 10
tops = np.array([np.median(tops[max(0, x - r):x + r + 1]) for x in range(len(tops))]).astype(int)
car = np.zeros_like(k)
for x in range(k.shape[1]):
    if tops[x] < ground:
        car[tops[x]:ground, x] = True
mask = Image.fromarray((car * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.4))
rgba = im.copy(); rgba.putalpha(mask)
bb = mask.getbbox(); rgba = rgba.crop(bb); mask = mask.crop(bb)
rgba.save(f"{out}.png"); mask.save(f"{out}-mask.png")
prev = Image.new("RGB", rgba.size, (128, 128, 128)); prev.paste(rgba, (0, 0), rgba); prev.save(f"{out}-check.png")
print(out, rgba.size, bb)
