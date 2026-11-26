# measure the teeth after the mouth-open shift: teeth = white texels on the front-facing mouth faces; per row fit x = a - k*y^2,
# z span (tips / gum line), y span
import bpy, os, sys, numpy as np
from mathutils import Vector
S = bpy.context.scene
lips = next(o for o in S.objects if o.type == 'MESH' and not o.name.startswith("GR_"))
me = lips.data; mw = lips.matrix_world
m = me.materials[0]; b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
img = None
for n in m.node_tree.nodes:
    if n.type == 'TEX_IMAGE' and n.image and n.image.name.endswith("_0"): img = n.image
W, H = img.size; px = np.array(img.pixels[:]).reshape(H, W, 4)
uv = np.empty(len(me.loops) * 2); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
pts = []
for p in me.polygons:
    c = mw @ p.center; n = (mw.to_3x3() @ p.normal).normalized()
    if abs(c.y) < 0.32 and -0.2 < c.z < 0.2 and n.x > 0.35 and c.x > 0.05:
        u, v = uv[p.loop_indices].mean(0); col = px[int(np.clip(v, 0, 1) * (H - 1)), int(np.clip(u, 0, 1) * (W - 1)), :3]
        mx, mn = col.max(), col.min()
        if mx > 0.5 and (mx - mn) / (mx + 1e-6) < 0.3: pts.append((c.x, c.y, c.z))
P = np.array(pts); print("TEETH faces", len(P))
P = P[(P[:, 0] > 0.12) & (np.abs(P[:, 1]) < 0.26) & (np.abs(P[:, 2]) < 0.16)]
for zb in np.arange(-0.16, 0.16, 0.01):
    s_ = P[(P[:, 2] >= zb) & (P[:, 2] < zb + 0.01) & (np.abs(P[:, 1]) < 0.1)]
    if len(s_): print("ZBIN %+.2f n=%4d xmax %.3f" % (zb, len(s_), s_[:, 0].max()))
zc = np.median(P[:, 2]); 
# split rows at the biggest z gap near the middle
zs = np.sort(P[:, 2]); gaps = np.diff(zs); mid = (zs > zs[0] + 0.02) & (zs < zs[-1] - 0.02)
i = np.argmax(np.where(mid[:-1], gaps, 0)); cut = (zs[i] + zs[i + 1]) / 2; print("BITE cut z", round(cut, 4), "gap", round(gaps[i], 4))
for name, sel in (("UPPER", P[:, 2] > cut), ("LOWER", P[:, 2] <= cut)):
    Q = P[sel]; A = np.stack([np.ones(len(Q)), -Q[:, 1] ** 2], 1); (a0, k), *_ = np.linalg.lstsq(A, Q[:, 0], rcond=None)
    # front-most surface: fit to the upper 30% in x for each y bin
    front = []
    for yb in np.linspace(Q[:, 1].min(), Q[:, 1].max(), 25):
        s = Q[np.abs(Q[:, 1] - yb) < 0.012]
        if len(s): front.append((yb, s[:, 0].max()))
    F = np.array(front); A2 = np.stack([np.ones(len(F)), -F[:, 0] ** 2], 1); (fa, fk), *_ = np.linalg.lstsq(A2, F[:, 1], rcond=None)
    print(name, "z %.4f..%.4f  y %.4f..%.4f  front x = %.4f - %.3f*y^2  (n=%d)" % (np.percentile(Q[:, 2], 2), np.percentile(Q[:, 2], 98), np.percentile(Q[:, 1], 2), np.percentile(Q[:, 1], 98), fa, fk, len(Q)))
