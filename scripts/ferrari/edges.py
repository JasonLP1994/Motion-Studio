# Sample the top and bottom edges of the car in the top-down photo's paint mask (for the node frame).
# usage: edges.py <mask.png> <out.json> <step_px>
import sys, json, numpy as np
from PIL import Image, ImageFilter
m = Image.open(sys.argv[1]).convert("L").filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15))
a = np.array(m) > 128
step = int(sys.argv[3])
cols = np.nonzero(a.sum(0) > 40)[0]
x0, x1 = int(cols.min()), int(cols.max())
pts = []
for x in range(x0 + step, x1 - step, step):
    ys = np.nonzero(a[:, x])[0]
    if len(ys) > 40:
        pts.append([x, int(ys.min()), int(ys.max())])
json.dump({"size": [a.shape[1], a.shape[0]], "step": step, "edges": pts}, open(sys.argv[2], "w"))
print(len(pts), "columns", x0, x1)
