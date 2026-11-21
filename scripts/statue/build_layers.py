# Build render layers from the SAM 2 masks (work/statue/mask, work/statue/face):
#  public/statue/cut/NNNNN.webp   statue cut-out, 1920x1080 RGBA (type can sit behind her)
#  public/statue/ring/NNNNN.png   yellow outline ring just outside her silhouette, 960x540 RGBA
#  src/kingz/track.json          per-frame anchors (head, hands, robe L/R, face box), smoothed, in 1920x1080 px
import glob, json, os, subprocess, numpy as np
from PIL import Image, ImageFilter
os.makedirs("work/statue/hd", exist_ok=True); os.makedirs("public/statue/cut", exist_ok=True); os.makedirs("public/statue/ring", exist_ok=True); os.makedirs("src/kingz", exist_ok=True)
if not os.path.exists("work/statue/hd/f_00001.jpg"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "public/statue/clip.mp4", "-q:v", "2", "work/statue/hd/f_%05d.jpg"], check=True)
masks = sorted(glob.glob("work/statue/mask/*.png")); N = len(masks)
YEL = (255, 230, 0)
track = []
for i, mp in enumerate(masks):
    m = Image.open(mp).convert("L")                      # 960x540
    a = np.array(m) > 128
    # cut-out
    hd = Image.open(f"work/statue/hd/f_{i + 1:05d}.jpg").convert("RGB")
    alpha = m.resize((1920, 1080), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.6))
    cut = hd.copy(); cut.putalpha(alpha); cut.save(f"public/statue/cut/{i:05d}.webp", quality=90, method=4)
    # ring: band between two dilations (sits a little outside her edge, like a loose hand-drawn line)
    outer = np.array(m.filter(ImageFilter.MaxFilter(23))) > 128
    inner = np.array(m.filter(ImageFilter.MaxFilter(15))) > 128
    ring = (outer & ~inner)
    rg = np.zeros((540, 960, 4), np.uint8); rg[ring] = YEL + (255,)
    Image.fromarray(rg).filter(ImageFilter.GaussianBlur(0.6)).save(f"public/statue/ring/{i:05d}.png")
    # anchors (in 960 space, converted to 1920 below)
    ys, xs = np.nonzero(a)
    if len(ys) == 0:
        track.append(None); continue
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max(); h = y1 - y0
    def band(f0, f1):
        sel = (ys >= y0 + f0 * h) & (ys <= y0 + f1 * h)
        return xs[sel], ys[sel]
    hx, hy = band(0.0, 0.08); mx, my = band(0.42, 0.55); rx, ry = band(0.72, 0.8)
    fr = {"bbox": [int(x0), int(y0), int(x1), int(y1)],
          "head": [float(hx.mean()), float(hy.mean())], "hands": [float(mx.mean()), float(my.mean())],
          "robeL": [float(rx.min()), float(ry.mean())], "robeR": [float(rx.max()), float(ry.mean())]}
    fp = f"work/statue/face/{i:05d}.png"
    if os.path.exists(fp):
        fa = np.array(Image.open(fp).convert("L")) > 128
        fy, fx = np.nonzero(fa)
        if len(fy) > 50: fr["face"] = [int(fx.min()), int(fy.min()), int(fx.max()), int(fy.max())]
    track.append(fr)
# fill gaps, smooth (5-frame moving average), scale to 1920x1080
keys = ["head", "hands", "robeL", "robeR"]
def smooth(vals, r=2):
    out = []
    for i in range(len(vals)):
        win = [v for v in vals[max(0, i - r):i + r + 1] if v is not None]
        out.append([sum(c) / len(win) for c in zip(*win)] if win else None)
    return out
res = []
for k in keys + ["bbox", "face"]:
    vals = smooth([fr.get(k) if fr else None for fr in track])
    res.append((k, [[round(c * 2, 1) for c in v] if v else None for v in vals]))
out = {"frames": N, "size": [1920, 1080], **{k: v for k, v in res}}
json.dump(out, open("src/kingz/track.json", "w"))
print("frames", N, "face frames", sum(1 for v in out["face"] if v))
