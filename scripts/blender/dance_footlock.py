# Foot locking (user: "dancing looks too loose, not realistic"): while a foot is on the floor it is pinned in place; the leg
# re-solves with analytic two-bone IK (hip fixed, knee kept in its own bend plane) to reach the pinned foot; 3-frame blends in
# and out of every plant. Runs after groundfix.py.   blender -b IN.blend -P work/dance/footlock.py -- OUT.blend
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene; r = bpy.data.objects["rig"]; N = S.frame_end
CUTS = [1, 97, 177, 273]; Z_ON = 0.055; MINLEN = 3; BLEND = 3
def seg_of(f): return max(i for i, c in enumerate(CUTS) if c <= f)
B = lambda n: r.pose.bones[n]
# 1) sample: toe world position per foot per frame
toe = {s: [] for s in "lr"}
for f in range(1, N + 1):
    S.frame_set(f)
    for s in "lr": toe[s].append(r.matrix_world @ B(f"toes_01.{s}").head)
# 2) contact spans (low toe), never across a cut
spans = {s: [] for s in "lr"}
for s in "lr":
    low = [t.z < Z_ON for t in toe[s]]; f = 0
    while f < N:
        if low[f]:
            g = f
            while g + 1 < N and low[g + 1] and seg_of(g + 2) == seg_of(f + 1): g += 1
            if g - f + 1 >= MINLEN: spans[s].append((f, g))
            f = g + 1
        else: f += 1
# 3) per-frame desired toe shift with blends
shift = {s: [Vector() for _ in range(N)] for s in "lr"}
for s in "lr":
    for f0, f1 in spans[s]:
        pts = [toe[s][k] for k in range(f0, f1 + 1)]
        lock = Vector((float(np.median([p.x for p in pts])), float(np.median([p.y for p in pts])), 0))
        for k in range(f0 - BLEND, f1 + BLEND + 1):
            if k < 0 or k >= N or seg_of(k + 1) != seg_of(f0 + 1): continue
            w = 1.0 if f0 <= k <= f1 else max(0.0, 1 - (f0 - k if k < f0 else k - f1) / (BLEND + 1))
            w = w * w * (3 - 2 * w)
            d = (lock - toe[s][k]); d.z = 0
            if w * d.length > shift[s][k].length: shift[s][k] = d * w
# 4) solve + key
def solve(H, K, A, A2):
    l1, l2 = (K - H).length, (A - K).length; v = A2 - H; d = min(v.length, (l1 + l2) * 0.999); d = max(d, abs(l1 - l2) + 1e-4)
    u = v.normalized(); A2 = H + u * d
    aa = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(0.0, l1 * l1 - aa * aa))
    p = (K - H) - u * (K - H).dot(u)
    p = p.normalized() if p.length > 1e-6 else Vector((0, -1, 0))
    return H + u * aa + p * h, A2
MWi = r.matrix_world.inverted()
moved = 0
for f in range(1, N + 1):
    S.frame_set(f)
    for s in "lr":
        d = shift[s][f - 1]
        if d.length < 1e-4: continue
        th, tt, ls, lt, ft, to = (B(f"thigh_stretch.{s}"), B(f"thigh_twist.{s}"), B(f"leg_stretch.{s}"), B(f"leg_twist.{s}"), B(f"foot.{s}"), B(f"toes_01.{s}"))
        H, K, A = th.head.copy(), ls.head.copy(), ft.head.copy()
        dA = MWi.to_3x3() @ d
        K2, A2 = solve(H, K, A, A + dA)
        R1 = (K - H).rotation_difference(K2 - H).to_matrix().to_4x4(); R2 = (A - K).rotation_difference(A2 - K2).to_matrix().to_4x4()
        def rot_about(pb, R, old_pivot, new_pivot):
            M = pb.matrix.copy(); hd = M.translation.copy()
            nh = new_pivot + (R.to_3x3() @ (hd - old_pivot))
            M2 = R @ Matrix.Translation(-hd) @ M; M2.translation = nh; return M2
        Mth = rot_about(th, R1, H, H); Mtt = rot_about(tt, R1, H, H)
        Mls = rot_about(ls, R2, K, K2); Mlt = rot_about(lt, R2, K, K2)
        off = A2 - A; Mft = ft.matrix.copy(); Mft.translation = Mft.translation + off; Mto = to.matrix.copy(); Mto.translation = Mto.translation + off
        for pb, M in ((th, Mth), (tt, Mtt), (ls, Mls), (lt, Mlt), (ft, Mft), (to, Mto)):
            pb.matrix = M; bpy.context.view_layer.update()
        for pb in (th, tt, ls, lt, ft, to):
            pb.keyframe_insert("location", frame=f); pb.keyframe_insert("rotation_quaternion", frame=f)
        moved += 1
print("FOOTLOCK spans", {s: len(spans[s]) for s in "lr"}, "frames adjusted", moved)
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("FOOTLOCK SAVED")
