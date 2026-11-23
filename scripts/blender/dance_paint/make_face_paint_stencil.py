# UV "vein" face paint (user's reference): symmetric branching glow lines. Coordinates in cm from the nose tip
# (x = character's left, z = up). Stencil covers 22 x 26 cm: px = (x + 11) / 22 * W, py = (12 - z) / 26 * H.
from PIL import Image, ImageDraw
import math, sys
WS = float(sys.argv[1]) if len(sys.argv) > 1 else 1.7      # line-width scale
W, H, SS = 1024, 1210, 3
im = Image.new("L", (W * SS, H * SS), 0); d = ImageDraw.Draw(im)
def Q(x, z): return ((x + 11) / 22 * W * SS, (12 - z) / 26 * H * SS)
def cm(w): return w * WS / 22 * W * SS
def dot(c, r): d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)
def stroke(pts, w0, w1):
    n = len(pts) - 1
    dot(Q(*pts[0]), cm(w0) / 2)
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[i + 1]
        for k in range(8):
            t0, t1 = k / 8, (k + 1) / 8
            wob = lambda t: 0.06 * math.sin(7 * t + i)
            a = (x0 + (x1 - x0) * t0 + wob(t0), z0 + (z1 - z0) * t0); b = (x0 + (x1 - x0) * t1 + wob(t1), z0 + (z1 - z0) * t1)
            w = cm(w0 + (w1 - w0) * (i + t1) / n)
            d.line([Q(*a), Q(*b)], fill=255, width=int(w)); dot(Q(*b), w / 2)
for s in (1, -1):
    M = lambda pts: [(s * x, z) for x, z in pts]
    stroke(M([(2.9, 2.5), (3.1, 0.6), (3.4, -1.8), (3.5, -4.0), (3.0, -6.0), (2.4, -7.9)]), 0.55, 0.3)
    stroke(M([(6.6, 5.4), (6.5, 2.2), (5.7, -0.6), (3.5, -2.5)]), 0.35, 0.5)
    stroke(M([(3.5, -4.0), (5.0, -4.5), (5.7, -6.0), (4.3, -7.8)]), 0.45, 0.3)
    stroke(M([(1.1, 4.7), (1.35, 6.8), (2.6, 8.6), (3.9, 9.2)]), 0.5, 0.3)
    stroke(M([(1.35, 6.8), (0.95, 9.4), (1.5, 11.2)]), 0.4, 0.28)
d.rounded_rectangle([Q(-1.25, 3.6), Q(1.25, 3.0)], radius=int(cm(0.2)), fill=255)
dot(Q(0, 1.7), cm(0.22))
im = im.resize((W, H), Image.LANCZOS); im.save("work/dance/paint/face_paint_stencil.png"); print("stencil ok")
