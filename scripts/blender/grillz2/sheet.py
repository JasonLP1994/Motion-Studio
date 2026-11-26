import sys, glob
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; fs = sorted(glob.glob(d + "/d_*.png")); ims = [Image.open(f).convert("RGB") for f in fs]
w, h = ims[0].size; cols = 3; rows = (len(ims) + cols - 1) // cols; o = Image.new("RGB", (w * cols, h * rows))
for i, (f, im) in enumerate(zip(fs, ims)):
    o.paste(im, ((i % cols) * w, (i // cols) * h)); ImageDraw.Draw(o).text(((i % cols) * w + 8, (i // cols) * h + 8), f[-8:-4], fill=(255, 255, 0))
o.save(out)
