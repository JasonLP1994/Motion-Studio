# Cut the green car out of inputs/green-car-top.png by colour (paint + tail lights), fill the
# windows/vents inside the outline, rotate it to point right, save RGBA + mask into public/car/.
import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw
src, outdir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
hsv = np.array(im.convert("HSV")).astype(int)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
green = (H > 35) & (H < 105) & (S > 80) & (V > 45)
red = ((H < 14) | (H > 238)) & (S > 110) & (V > 50)
m = Image.fromarray(((green | red) * 255).astype(np.uint8))
m = m.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(21))  # close gaps (vents, stalks)
# fill holes: flood the background from the border; everything not reached is car
f = m.copy(); ImageDraw.floodfill(f, (0, 0), 128); ImageDraw.floodfill(f, (f.width - 1, f.height - 1), 128)
a = np.array(f); car = (a != 128).astype(np.uint8) * 255
mask = Image.fromarray(car).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
rgba = im.copy(); rgba.putalpha(mask)
bbox = mask.getbbox(); pad = 12
bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
rgba = rgba.crop(bbox).rotate(90, expand=True)  # front was at the bottom -> now points right
mask = mask.crop(bbox).rotate(90, expand=True)
rgba.save(f"{outdir}/car.png"); mask.save(f"{outdir}/mask.png")
prev = Image.new("RGB", rgba.size, (128, 128, 128)); prev.paste(rgba, (0, 0), rgba)
prev.save(f"{outdir}/check-on-grey.png")
print("car", rgba.size, "bbox", bbox)
