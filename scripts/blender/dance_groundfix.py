# Ground contact fix (user: "the dancer just hovers above the floor"). For every frame, compare the original mocap
# performer's lowest mesh point (on the floor = contact) with our character's real lowest point (sneaker soles, hands, hood,
# clothes, evaluated meshes), and move the whole rig up/down so his lowest point sits on the floor at every contact
# (airborne frames keep the performer's height, scaled). Lightly smoothed so it never jitters.
#   blender -b MERGED.blend -P work/dance/groundfix.py -- OUT.blend
import bpy, sys
import numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene; rig = bpy.data.objects["rig"]
SEGS = [("85_04-fancyfootwork", 100, 195), ("85_05-handstandkicks", 110, 189),
        ("85_14-breaksequencewithflips", 240, 335), ("85_08-helicopter", 105, 200)]
SC = 0.836; CONTACT = 0.03
# 1) performer's lowest point per output frame
src_min = []
for name, f0, f1 in SEGS:
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f"/home/user/Motion-Studio/work/dance/mocap/{name}.glb")
    new = [o for o in bpy.data.objects if o not in before]; m = next(o for o in new if o.type == 'MESH' and o.name.startswith("SuperHero"))
    for f in range(f0, f1 + 1):
        S.frame_set(f); e = m.evaluated_get(bpy.context.evaluated_depsgraph_get())
        co = np.empty(len(e.data.vertices) * 3); e.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        mw = np.array(e.matrix_world); src_min.append(float((co @ mw[:3, :3].T + mw[:3, 3])[:, 2].min()))
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
for act in list(bpy.data.actions):
    if act.users == 0: bpy.data.actions.remove(act)
N = S.frame_end; assert len(src_min) == N, (len(src_min), N)
# 2) character's lowest point per frame
MESH = [o for o in bpy.data.objects if o.type == 'MESH' and o.name in ("Sneaker", "CC_Base_Body", "Jacket", "Vest", "Chachi_Momma_Pants", "Buzz_Cut")]
rig.animation_data_create()
tgt_min = []
for f in range(1, N + 1):
    S.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); lo = 1e9
    for o in MESH:
        e = o.evaluated_get(dg); co = np.empty(len(e.data.vertices) * 3); e.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        mw = np.array(e.matrix_world); lo = min(lo, float((co @ mw[:3, :3].T + mw[:3, 3])[:, 2].min()))
    tgt_min.append(lo)
src_min, tgt_min = np.array(src_min), np.array(tgt_min)
want = np.where(src_min < CONTACT, 0.0, (src_min - CONTACT) * SC)       # contact -> sole on the floor; airborne -> scaled height
delta = want - tgt_min
# 3) smooth inside each segment (median 3 then a light box 3), keep the cuts sharp
out = delta.copy(); s = 0
for name, f0, f1 in SEGS:
    n = f1 - f0 + 1; d = delta[s:s + n]
    med = np.array([np.median(d[max(0, i - 1):i + 2]) for i in range(n)])
    out[s:s + n] = np.array([med[max(0, i - 1):i + 2].mean() for i in range(n)]); s += n
z0 = rig.location.z
for f in range(1, N + 1):
    rig.location.z = z0 + out[f - 1]; rig.keyframe_insert("location", index=2, frame=f)
for fc in rig.animation_data.action.fcurves:
    if fc.data_path == "location":
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
print("GROUND", "before: mean hover %.3f max %.3f | correction range %.3f..%.3f" % (np.mean(np.maximum(tgt_min[src_min < CONTACT], 0)), tgt_min[src_min < CONTACT].max(), out.min(), out.max()))
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("GROUNDFIX SAVED", N)
