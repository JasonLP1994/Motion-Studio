"""Samurai intro (and other samurai shots via COMP_CFG=<json>): compositing + grade pass over the finished look frames (1-360).
Lime halation, anamorphic streaks, light-bang flashes, hero impact (flash + punch + shockwave), section-cut hits,
dust in the light, Steel Noir LUT, optional letterbox. All timings live in CFG.
  tools/ai-venv/bin/python scripts/mech/intro_comp.py <in_dir> <out_dir> <lut.cube> [frame ...]   (no frames = all 1-360)
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "grade"))
from make_lut import load_cube, apply_cube

CFG = dict(
    frames=360,
    halation=dict(strength=0.55, radius=28, tint=(0.70, 1.0, 0.20)),
    streak=dict(thresh=0.75, strength=0.30, tint=(0.75, 0.95, 1.0)),
    bangs=[136, 140, 144, 148], bang_flash=[(0, 0.22), (1, 0.10), (2, 0.03), (3, 0.0)],
    hero=dict(f=281, flash=[(280, 0.0), (281, 0.55), (282, 0.28), (283, 0.10), (286, 0.0)],
              punch=[(280, 1.0), (281, 1.06), (284, 1.035), (292, 1.01), (302, 1.0)],
              wave_frames=14, wave_amp=12.0, wave_width=60.0, centre=(0.50, 0.30)),
    cuts=[171, 206, 241], cut_span=3, cut_ca=10, cut_punch=1.03,
    dust=dict(t0=136, t1=361, n=500, col=(0.80, 0.88, 1.0), alpha=0.35),
    lut_mix=1.0,
    letterbox=None,            # e.g. 2.2 for 2.2:1 bars; None = full frame
)
if os.environ.get("COMP_CFG"):                 # per-shot overrides (JSON file), e.g. renders for other samurai shots
    import json; CFG.update(json.load(open(os.environ["COMP_CFG"])))


def env(fr, pts):
    xs, ys = zip(*pts); return float(np.interp(fr, xs, ys))


def remap(img, sx, sy):
    h, w = img.shape[:2]
    x0 = np.clip(np.floor(sx).astype(np.int32), 0, w - 2); y0 = np.clip(np.floor(sy).astype(np.int32), 0, h - 2)
    fx = np.clip(sx - x0, 0, 1)[..., None]; fy = np.clip(sy - y0, 0, 1)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def small(a, w, h):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255


def hblur(a, k, passes=3):
    for _ in range(passes):
        c = np.cumsum(np.pad(a, ((0, 0), (k + 1, k), (0, 0)), mode="edge"), axis=1)
        a = (c[:, 2 * k + 1:] - c[:, :-2 * k - 1]) / (2 * k + 1)
    return a


def halation(x):
    s = CFG["halation"]; h, w = x.shape[:2]
    m = np.clip((x[..., 1] - x[..., 2] - 0.25) * 2.0, 0, 1) * np.clip(x[..., 1] * 1.4 - 0.3, 0, 1)   # lime areas
    sm = Image.fromarray((m * 255).astype(np.uint8)).resize((w // 4, h // 4), Image.BILINEAR)
    g = np.asarray(sm.filter(ImageFilter.GaussianBlur(s["radius"] / 4)).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
    g2 = np.asarray(sm.filter(ImageFilter.GaussianBlur(s["radius"])).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
    k = float(np.clip(1 - (m.mean() - 0.02) / 0.10, 0.15, 1))                # big lime areas (sword close-ups) glow less
    glow = (g * 0.6 + g2 * 0.9)[..., None] * np.array(s["tint"], np.float32) * s["strength"] * k
    return 1 - (1 - np.clip(x, 0, 1)) * (1 - np.clip(glow, 0, 1))


def streaks(x):
    s = CFG["streak"]; h, w = x.shape[:2]
    sm = small(x, w // 4, h // 4); lum = sm.max(-1, keepdims=True)
    lime = np.clip((sm[..., 1:2] - sm[..., 2:3] - 0.3) * 3, 0, 1)            # only lime emissives (eyes, strips) streak
    m = np.clip((lum - s["thresh"]) / (1 - s["thresh"]), 0, 1) ** 2 * lime
    st = hblur(m, 80) * 2.4 + hblur(m, 20) * 1.0
    st = small(st[..., 0], w, h)[..., None]
    return x + s["strength"] * st * np.array(s["tint"], np.float32)


def geom(x, fr):
    H = CFG["hero"]; h, w = x.shape[:2]
    s = env(fr, H["punch"]); cx, cy = H["centre"][0] * w, H["centre"][1] * h
    for c in CFG["cuts"]:                                   # small settle-in push on each section cut
        if 0 <= fr - c < CFG["cut_span"] + 3:
            s *= 1 + (CFG["cut_punch"] - 1) * (1 - (fr - c) / (CFG["cut_span"] + 3)); cx, cy = w / 2, h / 2
    wt = fr - H["f"]; wave = 0 <= wt < H["wave_frames"]
    if s == 1.0 and not wave: return x
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = cx + (xx - cx) / s; sy = cy + (yy - cy) / s
    if not wave: return remap(x, sx, sy)
    dx, dy = xx - cx, yy - cy; r = np.hypot(dx, dy) + 1e-3
    R = (wt + 1) / H["wave_frames"] * math.hypot(w, h) * 0.8
    amp = H["wave_amp"] * (1 - wt / H["wave_frames"]) ** 1.5
    ring = np.exp(-((r - R) / H["wave_width"]) ** 2) * amp
    sx = sx - dx / r * ring; sy = sy - dy / r * ring
    out = remap(x, sx, sy); sh = ring / max(amp, 1e-3) * 3
    out[..., 0] = remap(x[..., 0:1], sx - dx / r * sh, sy - dy / r * sh)[..., 0]
    out[..., 2] = remap(x[..., 2:3], sx + dx / r * sh, sy + dy / r * sh)[..., 0]
    return out


def cut_ca(x, fr):
    for c in CFG["cuts"]:
        d = fr - c
        if 0 <= d < CFG["cut_span"]:
            k = 1 - d / CFG["cut_span"]; sh = max(1, int(CFG["cut_ca"] * k)); out = x.copy()
            out[..., 0] = np.roll(x[..., 0], -sh, axis=1); out[..., 2] = np.roll(x[..., 2], sh, axis=1)
            return out
    return x


_dust = None
def dust(x, fr):
    D = CFG["dust"]
    if not (D["t0"] <= fr < D["t1"]): return x
    global _dust
    h, w = x.shape[:2]
    if _dust is None:
        r = np.random.default_rng(7); n = D["n"]
        _dust = dict(x=r.uniform(0, 1, n), y=r.uniform(0, 1, n), vx=r.uniform(-0.0008, 0.0008, n), vy=r.uniform(-0.0012, -0.0002, n),
                     ph=r.uniform(0, 6.28, n), size=np.where(r.random(n) < 0.12, r.uniform(10, 26, n), r.uniform(1.0, 2.6, n)),
                     a=r.uniform(0.3, 1.0, n))
    m = _dust; t = fr - D["t0"]
    lay = Image.new("L", (w, h), 0); big = Image.new("L", (w // 4, h // 4), 0)
    d, db = ImageDraw.Draw(lay), ImageDraw.Draw(big)
    fade = min(1, t / 10)
    px = ((m["x"] + m["vx"] * t + 0.004 * np.sin(m["ph"] + t * 0.05)) % 1) * w
    py = ((m["y"] + m["vy"] * t) % 1) * h
    tw = 0.6 + 0.4 * np.sin(m["ph"] * 3 + t * 0.21)
    for i in range(len(px)):
        v = int(255 * m["a"][i] * tw[i] * fade); s = m["size"][i]
        if s > 6: db.ellipse([px[i] / 4 - s / 4, py[i] / 4 - s / 4, px[i] / 4 + s / 4, py[i] / 4 + s / 4], fill=int(v * 0.35))
        else: d.ellipse([px[i] - s, py[i] - s, px[i] + s, py[i] + s], fill=v)
    a = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32) / 255
    b = np.asarray(big.filter(ImageFilter.GaussianBlur(2.0)).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
    lit = np.clip(small(x.mean(-1), w // 8, h // 8) * 6, 0.15, 1)                     # specks show more where there is light
    lit = small(lit, w, h)
    a = (np.clip(a + b, 0, 1) * lit)[..., None] * D["alpha"]
    return x + a * np.array(D["col"], np.float32)


def flash(x, fr):
    f = env(fr, CFG["hero"]["flash"])
    for b in CFG["bangs"]:
        if 0 <= fr - b <= 3: f = max(f, env(fr - b, CFG["bang_flash"]))
    return x if f <= 0 else x + (1 - x) * f


def letterbox(x):
    r = CFG["letterbox"]
    if not r: return x
    h, w = x.shape[:2]; bar = int(round((h - w / r) / 2))
    x[:bar] = 0; x[h - bar:] = 0
    return x


def comp(src, dst, lut, fr):
    x = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
    x = geom(x, fr)
    x = halation(x)
    x = streaks(x)
    x = dust(x, fr)
    g = apply_cube(np.clip(x, 0, 1), lut); x = x + CFG["lut_mix"] * (g - x)
    x = cut_ca(x, fr)
    x = flash(x, fr)
    x = letterbox(np.clip(x, 0, 1))
    Image.fromarray((x * 255 + 0.5).astype(np.uint8)).save(dst)


if __name__ == "__main__":
    inp, out, lutp = sys.argv[1:4]; frames = [int(v) for v in sys.argv[4:]] or list(range(1, CFG["frames"] + 1))
    os.makedirs(out, exist_ok=True); lut = load_cube(lutp)
    for k, fr in enumerate(frames):
        dst = os.path.join(out, f"f_{fr:04d}.png")
        if os.path.exists(dst) and len(sys.argv) == 4: continue
        comp(os.path.join(inp, f"f_{fr:04d}.png"), dst, lut, fr)
        if k % 25 == 0: print(f"[{k + 1}/{len(frames)}] f_{fr:04d}", flush=True)
    print("comp done ->", out)
