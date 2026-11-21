# Keep only the largest connected piece of each SAM cut-out mask (drops floating floor-reflection specks).
# usage: keep_largest.py <names...>   (rewrites public/ferrari/<name>-cut.png / -cutmask.png / -cut-check.png)
import sys, numpy as np
from collections import deque
from PIL import Image, ImageFilter
for name in sys.argv[1:]:
    mask = Image.open(f"public/ferrari/{name}-cutmask.png").convert("L")
    W, H = mask.size; s = 4
    small = np.array(mask.resize((W // s, H // s), Image.BILINEAR)) > 128
    lab = np.zeros(small.shape, int); best, best_n, cur = 0, 0, 0
    for y0, x0 in zip(*np.nonzero(small)):
        if lab[y0, x0]: continue
        cur += 1; n = 0; q = deque([(y0, x0)]); lab[y0, x0] = cur
        while q:
            y, x = q.popleft(); n += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < small.shape[0] and 0 <= xx < small.shape[1] and small[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur; q.append((yy, xx))
        if n > best_n: best, best_n = cur, n
    keep = Image.fromarray(((lab == best) * 255).astype(np.uint8)).resize((W, H), Image.NEAREST).filter(ImageFilter.MaxFilter(9))
    m = np.minimum(np.array(mask), np.array(keep))
    mask = Image.fromarray(m.astype(np.uint8))
    im = Image.open(f"public/ferrari/{name}.png").convert("RGB"); rgba = im.copy(); rgba.putalpha(mask)
    rgba.save(f"public/ferrari/{name}-cut.png"); mask.save(f"public/ferrari/{name}-cutmask.png")
    prev = Image.new("RGB", im.size, (238, 236, 231)); prev.paste(rgba, (0, 0), rgba); prev.save(f"public/ferrari/{name}-cut-check.png")
    print(name, "pieces", cur, "kept", best_n * s * s, "px")
