# Pixelated (mosaic) versions of the cut-out car for the glyph bursts and the dissolve.
import sys
from PIL import Image
src, outdir = sys.argv[1], sys.argv[2]
car = Image.open(src).convert("RGBA")
for b in (8, 16, 18, 32, 64):
    small = car.resize((max(1, car.width // b), max(1, car.height // b)), Image.BOX)
    r, g, bl, a = small.split()
    a = a.point(lambda v: 255 if v > 110 else 0)
    small = Image.merge("RGBA", (r, g, bl, a))
    small.resize(car.size, Image.NEAREST).save(f"{outdir}/mosaic_{b}.png")
print("ok")
