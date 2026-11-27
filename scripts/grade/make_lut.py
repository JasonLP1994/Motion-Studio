"""Original 3D LUTs (.cube) built in numpy, plus a numpy applier (trilinear) so grades never go through ffmpeg colour filters.
Make:   tools/ai-venv/bin/python scripts/grade/make_lut.py neon-night luts/suno-neon-night.cube [--size 33]
Apply (in Python):  from make_lut import load_cube, apply_cube; out = apply_cube(img_float01, load_cube(path))
The .cube files also load in CapCut, Premiere (Lumetri > Creative > Look) and DaVinci Resolve.
Presets:
  neon-night  deep blue-teal shadows, lime/green pushed and brighter, warm lamp highlights, gentle S-curve.
  steel-noir  cold steel greys, blue-steel shadows, lime emissives pushed clean, firm contrast (samurai intro).
"""
import argparse, os
import numpy as np


def _hue_weight(h, centre, width):
    d = np.abs(((h - centre + 0.5) % 1.0) - 0.5); return np.clip(1 - d / width, 0, 1)


def neon_night(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mx, mn = rgb.max(-1), rgb.min(-1); sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # hue (0..1)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    h = np.where(mx - mn < 1e-6, 0, h)
    out = rgb.copy()
    # saturation: global +12%, lime/green +35% and a little brighter (the piece), blues +15%
    lime = _hue_weight(h, 0.22, 0.10) * np.clip(sat * 2, 0, 1)
    blue = _hue_weight(h, 0.64, 0.10); warm = _hue_weight(h, 0.05, 0.08)
    s_gain = 1.03 + 0.38 * lime + 0.18 * blue - 0.18 * warm          # lime + blue up, orange bricks down
    out = lum[..., None] + (out - lum[..., None]) * s_gain[..., None]
    out = out * (1 + 0.10 * lime)[..., None]
    # split tone: shadows to blue-teal, highlights warm
    sh = np.clip(1 - lum / 0.55, 0, 1) ** 1.3; mid = np.clip(1 - np.abs(lum - 0.4) / 0.3, 0, 1); hi = np.clip((lum - 0.65) / 0.35, 0, 1) ** 1.2
    out = out + sh[..., None] * np.array([-0.022, 0.020, 0.070]) + mid[..., None] * np.array([-0.018, 0.004, 0.022]) \
        + hi[..., None] * np.array([0.035, 0.012, -0.025])
    # S-curve (contrast) around 0.42 with soft toe, black point kept just above 0 so shadows stay blue not crushed
    x = np.clip(out, 0, 1)
    x = 0.42 + (x - 0.42) * 1.10
    x = np.where(x < 0.42, 0.42 * (np.clip(x, 0, None) / 0.42) ** 1.12, x)
    x = np.where(x > 0.42, 1 - 0.58 * ((1 - np.clip(x, None, 1)) / 0.58) ** 1.08, x)   # soft shoulder
    x = x * 0.985 + 0.012
    return np.clip(x, 0, 1)


def steel_noir(rgb):
    """Cold steel noir for dark armour + lime emissives: neutral-cool greys, blue-steel shadows, lime pushed clean."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mx, mn = rgb.max(-1), rgb.min(-1); sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    h = np.where(mx - mn < 1e-6, 0, h)
    lime = _hue_weight(h, 0.22, 0.11) * np.clip(sat * 2.5, 0, 1)
    s_gain = 0.80 + 0.55 * lime                                          # everything but the lime goes steely
    out = lum[..., None] + (rgb - lum[..., None]) * s_gain[..., None]
    out = out + lime[..., None] * np.array([-0.02, 0.03, -0.03]) * np.clip(lum * 2, 0, 1)[..., None]   # lime cleaner, less yellow
    sh = np.clip(1 - lum / 0.45, 0, 1) ** 1.4; mid = np.clip(1 - np.abs(lum - 0.4) / 0.3, 0, 1); hi = np.clip((lum - 0.7) / 0.3, 0, 1)
    nl = 1 - lime[..., None]
    out = out + nl * (sh[..., None] * np.array([-0.012, 0.004, 0.030]) + mid[..., None] * np.array([-0.012, -0.002, 0.014])
                      + hi[..., None] * np.array([-0.010, 0.0, 0.012]))
    x = np.clip(out, 0, 1)
    x = 0.40 + (x - 0.40) * 1.16
    x = np.where(x < 0.40, 0.40 * (np.clip(x, 0, None) / 0.40) ** 1.10, x)
    x = np.where(x > 0.40, 1 - 0.60 * ((1 - np.clip(x, None, 1)) / 0.60) ** 1.10, x)
    x = x * 0.988 + np.array([0.006, 0.008, 0.014])                       # blacks sit on a faint blue, not grey
    return np.clip(x, 0, 1)


PRESETS = {"neon-night": neon_night, "steel-noir": steel_noir}


def write_cube(path, fn, n=33, title="LUT"):
    g = np.linspace(0, 1, n, dtype=np.float32)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")          # .cube order: red changes fastest
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = fn(rgb)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for v in out: f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")


def load_cube(path):
    n = None; rows = []
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith("#"): continue
        if t[0] == "LUT_3D_SIZE": n = int(t[1]); continue
        if t[0] in ("TITLE", "DOMAIN_MIN", "DOMAIN_MAX"): continue
        rows.append([float(v) for v in t[:3]])
    return np.array(rows, np.float32).reshape(n, n, n, 3)    # [b][g][r]


def apply_cube(img, lut):
    """img float32 HxWx3 in 0..1 -> graded, trilinear."""
    n = lut.shape[0]; x = np.clip(img, 0, 1) * (n - 1)
    i0 = np.minimum(np.floor(x).astype(np.int32), n - 2); f = x - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]; fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    def L(db, dg, dr): return lut[b0 + db, g0 + dg, r0 + dr]
    c00 = L(0, 0, 0) * (1 - fr) + L(0, 0, 1) * fr; c01 = L(0, 1, 0) * (1 - fr) + L(0, 1, 1) * fr
    c10 = L(1, 0, 0) * (1 - fr) + L(1, 0, 1) * fr; c11 = L(1, 1, 0) * (1 - fr) + L(1, 1, 1) * fr
    c0 = c00 * (1 - fg) + c01 * fg; c1 = c10 * (1 - fg) + c11 * fg
    return c0 * (1 - fb) + c1 * fb


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("preset", choices=PRESETS); ap.add_argument("out"); ap.add_argument("--size", type=int, default=33)
    a = ap.parse_args(); write_cube(a.out, PRESETS[a.preset], a.size, a.preset); print("LUT ->", a.out)
