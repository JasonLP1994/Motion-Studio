# Pixelated (mosaic) versions of a cut-out car for the glyph bursts and the dissolve.
# usage: mosaics.py <car.png> <out_prefix>   ->  <out_prefix>mosaic_<b>.png
import sys
from PIL import Image
src, prefix = sys.argv[1], sys.argv[2]
car = Image.open(src).convert("RGBA")
for b in (8, 16, 18, 32, 64):
    small = car.resize((max(1, car.width // b), max(1, car.height // b)), Image.BOX)
    r, g, bl, a = small.split()
    a = a.point(lambda v: 255 if v > 110 else 0)
    Image.merge("RGBA", (r, g, bl, a)).resize(car.size, Image.NEAREST).save(f"{prefix}mosaic_{b}.png")
print("ok", prefix)
