"""Rig the Cyber Samurai inside the lit base scene (renders/farm/mech/mech-v11.blend) without Mixamo:
- skeleton with Mixamo bone names on measured joints, IK hand targets + elbow poles, a SWORD control bone
- katana hilt/guard split off the scabbard (by position along the katana axis) and a fitted steel blade built inside
  the scabbard (lime edge glow), both bone-parented to SWORD; scabbard + second sword parented to Hips
- weights: small hard pieces (armour plates, fingers, helmet) ride rigidly on one bone; cloth/body islands get smooth
  distance weights with region limits (sleeves -> arm chain, trousers -> hips/legs) + Laplacian smoothing
- lime strip pattern re-pinned to a stored rest-position attribute so it doesn't slide when parts move
  blender -b renders/farm/mech/mech-v11.blend -P scripts/blender/samurai_rig.py -- <out.blend>
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
KAT_HILT_END = np.array([0.3315, -0.398, 1.4309]); KAT_TIP = np.array([0.1255, 0.6331, 0.5638])
CFG = dict(
    mouth_t=0.695,            # scabbard mouth along katana axis (0 tip .. 1 hilt end); hilt pieces sit above it
    blade=dict(t0=0.04, t1=0.70, width=0.030, thick=0.0075, sori=0.012, kissaki=0.06, rings=72),
    rigid_extent=0.22, rigid_max_verts=2500,
    smooth_iters=12, power=4.0,
    curl_deg=(25, 85, 60),     # right-hand grip curl at knuckle, middle and tip joints
)
BONES = {  # name: (head, tail, parent)   world coords, character faces -Y, character right = -X
    "Hips": ((0, 0.05, 0.98), (0, 0.05, 1.10), None),
    "Spine": ((0, 0.05, 1.10), (0, 0.06, 1.25), "Hips"),
    "Spine1": ((0, 0.06, 1.25), (0, 0.07, 1.40), "Spine"),
    "Spine2": ((0, 0.07, 1.40), (0, 0.06, 1.53), "Spine1"),
    "Neck": ((0, 0.06, 1.53), (0, 0.03, 1.70), "Spine2"),
    "Head": ((0, 0.03, 1.70), (0, 0.03, 1.92), "Neck"),
    "LeftShoulder": ((0.05, 0.07, 1.50), (0.19, 0.08, 1.56), "Spine2"),
    "LeftArm": ((0.19, 0.08, 1.56), (0.29, 0.24, 1.38), "LeftShoulder"),
    "LeftForeArm": ((0.29, 0.24, 1.38), (0.26, 0.09, 1.21), "LeftArm"),
    "LeftHand": ((0.26, 0.09, 1.21), (0.25, 0.02, 1.12), "LeftForeArm"),
    "RightShoulder": ((-0.05, 0.07, 1.50), (-0.19, 0.08, 1.56), "Spine2"),
    "RightArm": ((-0.19, 0.08, 1.56), (-0.33, 0.05, 1.32), "RightShoulder"),
    "RightForeArm": ((-0.33, 0.05, 1.32), (-0.46, -0.17, 1.29), "RightArm"),
    "RightHand": ((-0.46, -0.17, 1.29), (-0.47, -0.29, 1.35), "RightForeArm"),
    "LeftUpLeg": ((0.10, 0.05, 0.97), (0.21, 0.03, 0.50), "Hips"),
    "LeftLeg": ((0.21, 0.03, 0.50), (0.28, 0.09, -0.10), "LeftUpLeg"),
    "LeftFoot": ((0.28, 0.09, -0.10), (0.30, -0.08, -0.20), "LeftLeg"),
    "LeftToeBase": ((0.30, -0.08, -0.20), (0.31, -0.20, -0.21), "LeftFoot"),
    "RightUpLeg": ((-0.10, 0.05, 0.97), (-0.21, 0.03, 0.50), "Hips"),
    "RightLeg": ((-0.21, 0.03, 0.50), (-0.28, 0.09, -0.10), "RightUpLeg"),
    "RightFoot": ((-0.28, 0.09, -0.10), (-0.30, -0.08, -0.20), "RightLeg"),
    "RightToeBase": ((-0.30, -0.08, -0.20), (-0.31, -0.20, -0.21), "RightFoot"),
}
ARM_R = ["RightShoulder", "RightArm", "RightForeArm", "RightHand", "Spine2"]
ARM_L = ["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand", "Spine2"]
LEGS = ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]
TORSO = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "LeftShoulder", "RightShoulder", "LeftArm", "RightArm"]

S = bpy.context.scene; VL = bpy.context.view_layer
L = float(np.linalg.norm(KAT_HILT_END - KAT_TIP)); AX = (KAT_HILT_END - KAT_TIP) / L
names = [f"Object_{i}" for i in range(2, 21) if i != 4]
meshes = [bpy.data.objects[n] for n in names if n in bpy.data.objects]

# ---- 1. rest attribute (original local coords = what the shader's Object coords were), then flatten transforms
for o in meshes:
    me = o.data
    if "rest" not in me.attributes:
        a = me.attributes.new("rest", "FLOAT_VECTOR", "POINT")
        a.data.foreach_set("vector", np.array([v.co[:] for v in me.vertices], np.float32).ravel())
for o in meshes:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
VL.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
g = bpy.data.node_groups.get("LimeStrips")
if g:
    tc = next((n for n in g.nodes if n.bl_idname == "ShaderNodeTexCoord"), None)
    if tc:
        at = g.nodes.new("ShaderNodeAttribute"); at.attribute_name = "rest"; at.attribute_type = "GEOMETRY"
        for l in list(tc.outputs["Object"].links): g.links.new(at.outputs["Vector"], l.to_socket)
        print("LimeStrips pattern pinned to rest attribute")


# ---- 2. islands helper
def islands(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    lab = -np.ones(len(bm.verts), np.int32); k = 0
    for v in bm.verts:
        if lab[v.index] >= 0: continue
        st = [v]; lab[v.index] = k
        while st:
            x = st.pop()
            for e in x.link_edges:
                y = e.other_vert(x)
                if lab[y.index] < 0: lab[y.index] = k; st.append(y)
        k += 1
    edges = np.array([(e.verts[0].index, e.verts[1].index) for e in bm.edges], np.int32).reshape(-1, 2)
    bm.free(); return lab, k, edges


def coords(o):
    return np.array([v.co[:] for v in o.data.vertices])


def separate(o, mask, new_name):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    me2 = o.data.copy(); o2 = bpy.data.objects.new(new_name, me2); S.collection.objects.link(o2)
    bm2 = bmesh.new(); bm2.from_mesh(me2); bm2.verts.ensure_lookup_table()
    bmesh.ops.delete(bm2, geom=[bm2.verts[i] for i in np.nonzero(~mask)[0]], context="VERTS"); bm2.to_mesh(me2); bm2.free()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.nonzero(mask)[0]], context="VERTS"); bm.to_mesh(o.data); bm.free()
    return o2


# ---- 3. split katana hilt/guard off Object_19 and Object_20 (island centroid above the mouth and on the axis)
hilt_parts = []
for n in ("Object_19", "Object_20"):
    o = bpy.data.objects[n]; co = coords(o); lab, k, _ = islands(o); mask = np.zeros(len(co), bool)
    for i in range(k):
        idx = lab == i; c = co[idx].mean(0); t = (c - KAT_TIP) @ AX / L
        perp = np.linalg.norm((c - KAT_TIP) - t * L * AX)
        if t >= CFG["mouth_t"] and perp < 0.05: mask |= idx
    if mask.any():
        hilt_parts.append(separate(o, mask, f"KatanaHilt_{n[-2:]}")); print(f"{n}: {mask.sum()} verts -> hilt")
for o in hilt_parts:
    o.data.materials.clear()
    for m in bpy.data.objects["Object_19"].data.materials: o.data.materials.append(m)

# ---- 4. fitted blade inside the scabbard
B = CFG["blade"]
up = np.array([0, 0, 1.0]); E = up - (up @ AX) * AX; E /= np.linalg.norm(E)            # edge faces up (worn edge-up)
Bn = np.cross(AX, E)
verts, faces, edge_attr = [], [], []
n = B["rings"]
for i in range(n):
    s = i / (n - 1); t = B["t0"] + (B["t1"] - B["t0"]) * s
    c = KAT_TIP + t * L * AX - E * B["sori"] * math.sin(math.pi * s) * 0.0 - E * B["sori"] * (1 - s) ** 2   # gentle curve toward the tip
    lenm = (t - B["t0"]) * L
    taper = 1.0 if lenm > B["kissaki"] else max(0.0, lenm / B["kissaki"])
    w = B["width"] * (0.82 + 0.18 * s); th = B["thick"] * (0.75 + 0.25 * s)
    back = c - E * w / 2; edge = c - E * w / 2 + E * w * taper; ridge = c - E * w / 2 + E * w * 0.35 * max(taper, 0.3)
    for p, ea in ((back, 0.0), (ridge + Bn * th / 2 * max(taper, 0.15), 0.0), (edge, 1.0), (ridge - Bn * th / 2 * max(taper, 0.15), 0.0)):
        verts.append(tuple(p)); edge_attr.append(ea)
for i in range(n - 1):
    for j in range(4):
        a, b = i * 4 + j, i * 4 + (j + 1) % 4; faces.append((a, b, b + 4, a + 4))
faces.append(tuple(range((n - 1) * 4, n * 4))[::-1]); faces.append((0, 1, 2, 3))
me = bpy.data.meshes.new("KatanaBlade"); me.from_pydata(verts, [], faces); me.update()
for p in me.polygons: p.use_smooth = False
at = me.attributes.new("edge", "FLOAT", "POINT"); at.data.foreach_set("value", np.array(edge_attr, np.float32))
blade = bpy.data.objects.new("KatanaBlade", me); S.collection.objects.link(blade)
bm_ = bpy.data.materials.new("BladeSteel"); bm_.use_nodes = True; nt = bm_.node_tree; P = nt.nodes["Principled BSDF"]
P.inputs["Base Color"].default_value = (0.50, 0.53, 0.57, 1); P.inputs["Metallic"].default_value = 1.0; P.inputs["Roughness"].default_value = 0.13
ea = nt.nodes.new("ShaderNodeAttribute"); ea.attribute_name = "edge"
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 1.0
nt.links.new(ea.outputs["Fac"], mr.inputs["Value"])
bg = nt.nodes.new("ShaderNodeValue"); bg.name = bg.label = "blade_glow"; bg.outputs[0].default_value = 1.0
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; nt.links.new(mr.outputs[0], mul.inputs[0]); nt.links.new(bg.outputs[0], mul.inputs[1])
mul2 = nt.nodes.new("ShaderNodeMath"); mul2.operation = "MULTIPLY"; mul2.inputs[1].default_value = 8.0; nt.links.new(mul.outputs[0], mul2.inputs[0])
P.inputs["Emission Color"].default_value = (0.62, 1.0, 0.02, 1); nt.links.new(mul2.outputs[0], P.inputs["Emission Strength"])
me.materials.append(bm_)

# ---- 5. armature
amt = bpy.data.armatures.new("SamuraiRig"); rig = bpy.data.objects.new("SamuraiRig", amt); S.collection.objects.link(rig)
amt.display_type = "STICK"; VL.objects.active = rig
bpy.ops.object.select_all(action="DESELECT"); rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = amt.edit_bones
for nm, (h, t, par) in BONES.items():
    b = eb.new(nm); b.head = h; b.tail = t
for nm, (h, t, par) in BONES.items():
    if par: eb[nm].parent = eb[par]; eb[nm].use_connect = False
mouth = KAT_TIP + CFG["mouth_t"] * L * AX
b = eb.new("SWORD"); b.head = tuple(mouth); b.tail = tuple(mouth + AX * 0.15); b.use_deform = False
for side, hand in (("R", "RightHand"), ("L", "LeftHand")):
    t = eb.new(f"IK_{side}"); t.head = eb[hand].head.copy(); t.tail = eb[hand].tail.copy(); t.roll = eb[hand].roll; t.use_deform = False
    fa = eb["RightForeArm" if side == "R" else "LeftForeArm"]
    p = eb.new(f"POLE_{side}"); p.head = fa.head + Vector((0.25 if side == "L" else -0.25, 0.30, -0.05)); p.tail = p.head + Vector((0, 0, 0.05)); p.use_deform = False
# right-hand finger bones (3 per finger) from the measured finger lines; curl direction = toward the wrist
FINGER_OBJ = ["Object_10", "Object_11", "Object_12", "Object_9"]          # inner -> outer along the knuckle line
FNAMES = ["Index", "Middle", "Ring", "Pinky"]
wrist_R = np.array(BONES["RightHand"][0])
fingers = {}
for on, fn in zip(FINGER_OBJ, FNAMES):
    co = coords(bpy.data.objects[on]); r = co[co[:, 0] < -0.30]; c = r.mean(0); ax_ = np.linalg.svd(r - c)[2][0]; t_ = (r - c) @ ax_
    b0, t0 = c + ax_ * t_.min(), c + ax_ * t_.max()
    if np.linalg.norm(t0 - wrist_R) < np.linalg.norm(b0 - wrist_R): b0, t0 = t0, b0
    fingers[fn] = (on, b0, t0)
kn = fingers["Pinky"][1] - fingers["Index"][1]; KN = kn / np.linalg.norm(kn)


def rot(v, axis, ang):                       # Rodrigues
    axis = axis / np.linalg.norm(axis); return v * math.cos(ang) + np.cross(axis, v) * math.sin(ang) + axis * (axis @ v) * (1 - math.cos(ang))


tipF = fingers["Middle"][2] - fingers["Middle"][1]
CURL_SIGN = 1.0 if np.linalg.norm(fingers["Middle"][1] + rot(tipF, KN, 0.6) - wrist_R) < np.linalg.norm(fingers["Middle"][2] - wrist_R) else -1.0
CURL = [math.radians(a) for a in CFG["curl_deg"]]
loop_pts = []
for fn in FNAMES:
    on, b0, t0 = fingers[fn]; L_ = np.linalg.norm(t0 - b0); d_ = (t0 - b0) / L_
    J = [b0, b0 + d_ * L_ * 0.45, b0 + d_ * L_ * 0.75, t0]
    for k in range(3):
        bb = eb.new(f"RightHand{fn}{k + 1}"); bb.head = tuple(J[k]); bb.tail = tuple(J[k + 1]); bb.use_deform = True
        bb.parent = eb["RightHand"] if k == 0 else eb[f"RightHand{fn}{k}"]
    # curled loop (for the fist hole): rotate successive segments
    p = J[0].copy(); dirv = d_.copy(); pts = [p.copy()]; acc = 0.0
    for k, frac in enumerate((0.45, 0.30, 0.25)):
        acc += CURL[k] * CURL_SIGN; seg = rot(dirv, KN, acc) * L_ * frac; p = p + seg; pts.append(p.copy())
    palm_pt = J[0] + (wrist_R - J[0]) * 0.35
    loop_pts += pts + [palm_pt]
    fingers[fn] = (on, b0, t0, J)
hole = np.mean(loop_pts, 0)
BONES_FINGER = [f"RightHand{fn}{k + 1}" for fn in FNAMES for k in range(3)]
bpy.ops.object.mode_set(mode="POSE")
for side in ("R", "L"):
    fa = rig.pose.bones["RightForeArm" if side == "R" else "LeftForeArm"]
    c = fa.constraints.new("IK"); c.target = rig; c.subtarget = f"IK_{side}"; c.pole_target = rig; c.pole_subtarget = f"POLE_{side}"
    c.chain_count = 2; c.pole_angle = math.radians(-90)
    h = rig.pose.bones["RightHand" if side == "R" else "LeftHand"]
    cr = h.constraints.new("COPY_ROTATION"); cr.target = rig; cr.subtarget = f"IK_{side}"
bpy.ops.object.mode_set(mode="OBJECT")
# calibrate pole angles so the IK arms sit exactly in the rest pose (no flip when IK takes over)
for side, fa_n in (("R", "RightForeArm"), ("L", "LeftForeArm")):
    c = rig.pose.bones[fa_n].constraints["IK"]; rest_elbow = Vector(BONES[fa_n][0]); best = (1e9, 0)
    for ang in range(-180, 180, 2):
        c.pole_angle = math.radians(ang); VL.update()
        dev = (rig.matrix_world @ rig.pose.bones[fa_n].head - rest_elbow).length
        if dev < best[0]: best = (dev, ang)
    c.pole_angle = math.radians(best[1]); print(f"pole {side}: {best[1]} deg, elbow error {best[0]*1000:.1f} mm")
VL.update()

# ---- 6. weights
deform = [nm for nm in BONES]
heads = np.array([BONES[nm][0] for nm in deform], float); tails = np.array([BONES[nm][1] for nm in deform], float)
deform_all = deform + BONES_FINGER


def seg_dist(P):
    v = tails - heads; w = P[:, None, :] - heads[None]
    t = np.clip((w * v[None]).sum(-1) / (v * v).sum(-1)[None], 0, 1)
    return np.linalg.norm(w - t[..., None] * v[None], axis=-1)


def weights(P, allowed=None):
    d = seg_dist(P)
    if allowed is not None:
        mask = np.array([nm in allowed for nm in deform]); d[:, ~mask] = 1e3
    w = 1.0 / (d + 0.01) ** CFG["power"]
    top = np.argsort(-w, 1)[:, :3]; keep = np.zeros_like(w, bool); np.put_along_axis(keep, top, True, 1); w = w * keep
    return w / w.sum(1, keepdims=True)


def smooth(w, edges, nv, iters, fixed=None):
    for _ in range(iters):
        acc = np.zeros_like(w); cnt = np.zeros(nv)
        np.add.at(acc, edges[:, 0], w[edges[:, 1]]); np.add.at(acc, edges[:, 1], w[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1); np.add.at(cnt, edges[:, 1], 1)
        nw = np.where(cnt[:, None] > 0, 0.5 * w + 0.5 * acc / np.maximum(cnt, 1)[:, None], w)
        w = nw / nw.sum(1, keepdims=True)
    return w


rigid_n = soft_n = 0
for o in meshes:
    co = coords(o); lab, k, edges = islands(o); W = np.zeros((len(co), len(deform_all))); ND = len(deform)
    soft = np.zeros(len(co), bool)
    for i in range(k):
        idx = lab == i; p = co[idx]; ext = (p.max(0) - p.min(0)).max(); c = p.mean(0)
        allowed = None
        if o.name == "Object_3":                     # jacket: sleeves follow the arm only, body follows the torso
            allowed = ARM_R if c[0] < -0.17 else ARM_L if c[0] > 0.17 else TORSO
        if o.name == "Object_2":
            allowed = LEGS
        if o.name in FINGER_OBJ and c[0] < -0.30:
            fn = FNAMES[FINGER_OBJ.index(o.name)]; _, b0, t0, J = fingers[fn]; L_ = np.linalg.norm(t0 - b0)
            sp = (c - b0) @ ((t0 - b0) / L_) / L_; k = 0 if sp < 0.45 else 1 if sp < 0.75 else 2
            W[idx, deform_all.index(f"RightHand{fn}{k + 1}")] = 1.0; rigid_n += 1; continue
        if ext < CFG["rigid_extent"] and idx.sum() < CFG["rigid_max_verts"] and o.name not in ("Object_2", "Object_3"):
            W[idx, np.argmax(weights(c[None], allowed)[0])] = 1.0; rigid_n += 1
        else:
            W[idx, :ND] = weights(p, allowed); soft[idx] = True; soft_n += 1
    if soft.any():
        Ws = smooth(W, edges, len(co), CFG["smooth_iters"]); W[soft] = Ws[soft]
    for j, nm in enumerate(deform_all):
        nz = np.nonzero(W[:, j] > 1e-3)[0]
        if len(nz) == 0: continue
        vg = o.vertex_groups.new(name=nm)
        for vi in nz: vg.add([int(vi)], float(W[vi, j]), "REPLACE")
    o.parent = rig; o.matrix_parent_inverse = rig.matrix_world.inverted()
    md = o.modifiers.new("Armature", "ARMATURE"); md.object = rig
    if len(o.modifiers) > 1:
        with bpy.context.temp_override(object=o, active_object=o):
            bpy.ops.object.modifier_move_to_index(modifier="Armature", index=0)
print(f"weights: {rigid_n} rigid pieces, {soft_n} soft islands")


def bone_parent(o, bone):
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = bone
    pb = rig.pose.bones[bone]; o.matrix_parent_inverse = (rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted()


VL.update()
for o in hilt_parts + [blade]: bone_parent(o, "SWORD")
for nm in ("Object_19", "Object_20"):                    # scabbards, second sword, cords: no armature, ride the hips
    o = bpy.data.objects[nm]
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
    for md in [m for m in o.modifiers if m.type == "ARMATURE"]: o.modifiers.remove(md)
    o.parent = None; bone_parent(o, "Hips")
# sword-glow material copies from the intro (if present) stay on the hilt; blade has its own edge glow
print("rig objects:", [o.name for o in hilt_parts], "blade verts", len(me.vertices))
rig["fist_hole"] = [float(v) for v in hole]; rig["fist_axis"] = [float(v) for v in KN]
rig["fist_palm_dir"] = [float(v) for v in (np.mean([fingers[fn][2] for fn in FNAMES], 0) - np.mean([fingers[fn][1] for fn in FNAMES], 0))]
rig["curl_sign"] = CURL_SIGN; rig["curl_deg"] = list(CFG["curl_deg"])
print("fist hole", np.round(hole, 3), "curl sign", CURL_SIGN)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
