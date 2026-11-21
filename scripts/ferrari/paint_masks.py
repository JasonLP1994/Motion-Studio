# Mask of the red paint in a full-frame car photo (for floods and pixel-letter clipping).
# usage: paint_masks.py <in.png> <out_mask.png>
import sys, numpy as np
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert("RGB")
hsv = np.array(im.convert("HSV")).astype(int)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
red = ((H < 16) | (H > 236)) & (S > 120) & (V > 40)
m = Image.fromarray((red * 255).astype(np.uint8))
m = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.2))
m.save(sys.argv[2]); print(sys.argv[2], round(float(red.mean()), 3))
