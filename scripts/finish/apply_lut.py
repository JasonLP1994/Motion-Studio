# Apply a .cube 3D LUT to every frame in a folder (trilinear, numpy + OpenCV). The bundled ffmpeg has no lut3d filter.
# Usage: PYTHONPATH=tools/finish-py python3 scripts/finish/apply_lut.py IN_DIR OUT_DIR LUT.cube [MIX 0..1]
import sys, os, numpy as np, cv2
from concurrent.futures import ThreadPoolExecutor
src, dst, lut_path = sys.argv[1:4]; mix = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
rows = [l.split() for l in open(lut_path) if l.strip() and (l[0].isdigit() or l[0] in "-.")]
n = round(len(rows) ** (1 / 3)); T = np.array(rows, np.float32).reshape(n, n, n, 3)  # [b][g][r]
os.makedirs(dst, exist_ok=True)
def one(name):
    out = os.path.join(dst, name)
    if os.path.exists(out): return
    im = cv2.imread(os.path.join(src, name), cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32) / 255 * (n - 1)
    i0 = np.clip(np.floor(im).astype(int), 0, n - 2); fr = im - i0; r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    fr_, fg, fb = fr[..., 0:1], fr[..., 1:2], fr[..., 2:3]; acc = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fb if db else 1 - fb) * (fg if dg else 1 - fg) * (fr_ if dr else 1 - fr_)
                acc = acc + w * T[b0 + db, g0 + dg, r0 + dr]
    o = im / (n - 1) * (1 - mix) + acc * mix
    cv2.imwrite(out, (np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1])
names = sorted(x for x in os.listdir(src) if x.endswith(".png"))
with ThreadPoolExecutor(os.cpu_count()) as ex: list(ex.map(one, names))
print("LUT", len(names), "->", dst)
