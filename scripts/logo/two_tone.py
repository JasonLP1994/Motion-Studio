# Turn a transparent render into a flat two-tone logo (the "3D form becomes a stencil logo" grammar): two alpha masks,
# DARK (shadow shapes) and LIGHT (highlight shapes), so the composite can paint them any colours (white/black/red flicker).
# Usage: python3 scripts/logo/two_tone.py <in_rgba.png> <out_prefix> [threshold 0-1] [blur px] [width] [chunk width px] [outline px]
import sys
import numpy as np
from PIL import Image, ImageFilter
src, pre = sys.argv[1], sys.argv[2]
t = float(sys.argv[3]) if len(sys.argv) > 3 else 0.42
blur = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
W = int(sys.argv[5]) if len(sys.argv) > 5 else None
im = Image.open(src).convert("RGBA")
if W: im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
a = np.asarray(im.getchannel("A").filter(ImageFilter.GaussianBlur(blur * 0.6)), np.float32) / 255
rgb = np.asarray(im.convert("RGB").filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255
lum = rgb.max(axis=2) * 0.6 + rgb.mean(axis=2) * 0.4          # red stones count as mid-bright, so the halo keeps its beads
inside = a > 0.5
cut = np.quantile(lum[inside], t) if inside.any() else 0.5
light = inside & (lum >= cut)
# bold, chunky shapes (logo, not a photo): threshold at low resolution, upscale smooth, threshold again
CH = int(sys.argv[6]) if len(sys.argv) > 6 else 0
if CH:
    def chunk(m):
        s_ = Image.fromarray((m * 255).astype(np.uint8)); w, h = s_.size
        s_ = s_.resize((CH, round(h * CH / w)), Image.BOX).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
        return np.asarray(s_) > 127
    inside = chunk(inside); light = chunk(light) & inside
dark = inside & ~light
# outline ring: keeps the logo's edge when the light shapes sit on a background of the same colour
ring_px = int(sys.argv[7]) if len(sys.argv) > 7 else 0
if ring_px:
    sh = Image.fromarray((inside * 255).astype(np.uint8))
    er = np.asarray(sh.filter(ImageFilter.MinFilter(ring_px * 2 + 1))) > 127
    dark = dark | (inside & ~er); light = light & er
for name, m in (("dark", dark), ("light", light), ("shape", inside)):
    al = Image.fromarray((m * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.7))
    out = Image.new("RGBA", al.size, (255, 255, 255, 0)); out.putalpha(al); out.save(f"{pre}-{name}.png")   # CSS masks read alpha
print("saved", pre, "cut", round(float(cut), 3), "size", im.size)
