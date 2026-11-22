# Lens pass for rendered frames (CPU, numpy + OpenCV): anamorphic streaks off highlights (KinoStreak-style), pseudo lens
# ghosts (Chapman-style mirrored bright spots), drifting light leaks, radial chromatic aberration, optional barrel distortion.
# Techniques follow the classic real-time ones (KinoStreak, Chapman pseudo lens flare, FidelityFX Lens CA), written for frames.
# Runs BEFORE the finishing grade (scripts/finish/finish.sh), like glass in front of the sensor.
# Usage: PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py IN_DIR OUT_DIR [--preset product|minimal|cover|none] [overrides]
import sys, os, glob, re, argparse, math
import numpy as np, cv2

P = {
    "product": dict(threshold=0.94, streak=0.22, streak_len=0.12, streak_tint=(0.75, 0.85, 1.0), ghost=0.04, leak=0.03, ca=0.001, distort=0.0),
    "cover": dict(threshold=0.9, streak=0.18, streak_len=0.09, streak_tint=(0.9, 0.85, 1.0), ghost=0.0, leak=0.0, ca=0.0008, distort=0.0),
    "minimal": dict(threshold=0.97, streak=0.12, streak_len=0.1, streak_tint=(0.9, 0.95, 1.0), ghost=0.0, leak=0.0, ca=0.0, distort=0.0),
    "none": dict(threshold=1.0, streak=0.0, streak_len=0.1, streak_tint=(1, 1, 1), ghost=0.0, leak=0.0, ca=0.0, distort=0.0),
}
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--preset", default="product")
for k in ("threshold", "streak", "streak_len", "ghost", "leak", "ca", "distort"): ap.add_argument("--" + k, type=float)
ap.add_argument("--leak-colors", default="1.0,0.42,0.12;1.0,0.78,0.38"); ap.add_argument("--fps", type=float, default=24)
a = ap.parse_args(); cfg = dict(P[a.preset])
for k in ("threshold", "streak", "streak_len", "ghost", "leak", "ca", "distort"):
    if getattr(a, k) is not None: cfg[k] = getattr(a, k)
LEAKS = [tuple(float(x) for x in c.split(",")) for c in a.leak_colors.split(";")]

def to_lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def to_srgb(x): x = np.clip(x, 0, None); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def scale_about_centre(img, s):
    h, w = img.shape[:2]; M = np.float32([[s, 0, w / 2 * (1 - s)], [0, s, h / 2 * (1 - s)]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def process(rgb, frame_idx, peak=255.0):
    h, w = rgb.shape[:2]; lin = to_lin(rgb.astype(np.float32) / peak)
    lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    th = cfg["threshold"]; bright = lin * np.clip((lum - th) / max(1e-3, 1 - th), 0, 1)[..., None]
    add = np.zeros_like(lin)
    if cfg["streak"] > 0:                       # anamorphic streak: very wide horizontal blur of the highlights
        small = cv2.resize(bright, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        s1 = cv2.GaussianBlur(small, (0, 0), sigmaX=cfg["streak_len"] * w / 4, sigmaY=0.6)
        s2 = cv2.GaussianBlur(small, (0, 0), sigmaX=cfg["streak_len"] * w / 4 * 0.35, sigmaY=0.4)
        st = cv2.resize(s1 * 0.6 + s2 * 0.4, (w, h), interpolation=cv2.INTER_LINEAR)
        add += st * np.array(cfg["streak_tint"], np.float32) * cfg["streak"] * 6.0
    if cfg["ghost"] > 0:                        # lens ghosts: mirrored, rescaled, blurred, tinted copies of the highlights
        small = cv2.resize(bright, (w // 4, h // 4), interpolation=cv2.INTER_AREA); flip = small[::-1, ::-1]
        gsum = np.zeros_like(small)
        for s, tint in ((0.5, (1.0, 0.7, 0.4)), (-0.3, (0.5, 0.8, 1.0)), (0.9, (0.9, 0.6, 1.0)), (-0.7, (1.0, 0.9, 0.6))):
            g = scale_about_centre(flip if s > 0 else small, abs(s)); gsum += cv2.GaussianBlur(g, (0, 0), 3 + 6 * abs(s)) * np.array(tint, np.float32)
        add += cv2.resize(gsum, (w, h), interpolation=cv2.INTER_LINEAR) * cfg["ghost"] * 4.0
    out = lin + add
    if cfg["leak"] > 0:                         # light leaks: big soft warm blobs drifting slowly, screen-blended
        t = frame_idx / a.fps; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); leak = np.zeros_like(lin)
        for i, col in enumerate(LEAKS):
            cx = w * (0.05 + 0.25 * i + 0.12 * math.sin(t * 0.35 + i * 2.1)) if i % 2 == 0 else w * (0.95 - 0.12 * math.sin(t * 0.3 + i))
            cy = h * (0.2 + 0.15 * math.sin(t * 0.27 + i * 1.3)); r = 0.55 * max(w, h)
            fall = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)) * 3.0)
            leak += fall[..., None] * np.array(col, np.float32) * (0.75 + 0.25 * math.sin(t * 0.8 + i))
        out = 1 - (1 - np.clip(out, 0, 1)) * (1 - np.clip(leak * cfg["leak"], 0, 1)) + np.clip(out - 1, 0, None)
    if cfg["ca"] > 0:                           # radial chromatic aberration: red pushed out, blue pulled in, grows to the edges
        out = np.dstack([scale_about_centre(out[..., 0], 1 + cfg["ca"]), out[..., 1], scale_about_centre(out[..., 2], 1 - cfg["ca"])])
    if cfg["distort"] != 0:                     # gentle barrel distortion
        k = cfg["distort"]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        nx, ny = (xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2); r2 = nx * nx + ny * ny; f = 1 + k * r2
        out = cv2.remap(out, (nx * f * w / 2 + w / 2).astype(np.float32), (ny * f * h / 2 + h / 2).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (np.clip(to_srgb(out), 0, 1) * peak + 0.5).astype(np.uint16 if peak > 255 else np.uint8)

os.makedirs(a.out, exist_ok=True)
files = sorted(glob.glob(os.path.join(a.inp, "*.png"))) if os.path.isdir(a.inp) else [a.inp]
for i, f in enumerate(files):
    m = re.search(r"(\d+)\.png$", f); idx = int(m.group(1)) if m else i
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED); alpha = im[..., 3] if im.shape[2] == 4 else None
    peak = 65535.0 if im.dtype == np.uint16 else 255.0   # 16-bit PNGs (OIDN output) stay 16-bit
    rgb = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2RGB); res = cv2.cvtColor(process(rgb, idx, peak), cv2.COLOR_RGB2BGR)
    if alpha is not None: res = np.dstack([res, alpha])
    cv2.imwrite(os.path.join(a.out, os.path.basename(f)), res)
print(f"lensfx ({a.preset}) -> {len(files)} frames in {a.out}")
