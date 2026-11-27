"""Keyframed katana draw on the rigged samurai (renders/farm/mech/samurai-rig-v1.blend).
Everything is driven in world space and baked to keyframes per frame: upper-body twist/lean, head, sword slide out of
the scabbard (scabbard pulled back by the left hand), release arc, two-handed forward guard, breathing hold.
The right hand target is computed from the fist's own knuckle axis so the fist wraps the hilt; reach is checked per frame.
  blender -b renders/farm/mech/samurai-rig-v1.blend -P scripts/blender/samurai_draw.py -- <out.blend>
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix, Quaternion

ARGS = sys.argv[sys.argv.index("--") + 1:]; OUT = ARGS[0]
S = bpy.context.scene; VL = bpy.context.view_layer
rig = bpy.data.objects["SamuraiRig"]; P = rig.pose.bones; A = rig.data
KAT_HILT_END = Vector((0.3315, -0.398, 1.4309)); KAT_TIP = Vector((0.1255, 0.6331, 0.5638))
LK = (KAT_HILT_END - KAT_TIP).length; AX0 = (KAT_HILT_END - KAT_TIP).normalized()
E0 = (Vector((0, 0, 1)) - AX0 * AX0.z).normalized()
MOUTH_T = 0.695; MOUTH = KAT_TIP + AX0 * (MOUTH_T * LK)

CFG = dict(
    frames=120,
    grip_r=0.085, grip_l=0.30,                 # grip points above the scabbard mouth (m along the hilt)
    knuckle_sign=1.0, roll_r=0.0,              # flip/roll of the right fist on the hilt if it reads wrong
    twist=[(0, 0), (14, 0), (26, 18), (40, 32), (50, 12), (60, -8), (70, -10), (120, -9)],     # deg, + = right shoulder forward
    lean=[(0, 0), (14, 0), (26, 7), (40, 5), (52, 2), (62, 4), (120, 4)],
    head_pitch=[(0, 0), (10, 0), (22, 16), (38, 10), (50, -2), (60, 4), (120, 4)],  # + = look down
    head_yaw=[(0, 0), (10, 0), (22, 14), (40, 6), (54, 0), (120, 0)],
    reach=[(0, 0.0), (12, 0.0), (26, 1.0)],
    curl=[(0, 0.0), (19, 0.0), (27, 1.0)],                                          # right fingers close on the grab                                         # right hand to the hilt
    slide=[(0, 0.0), (27, 0.0), (44, 0.30)],                                        # sword out along the scabbard (m)
    scab=[(0, 0.0), (28, 0.0), (44, 0.18), (56, 0.06), (70, 0.0)],                  # scabbard pulled back (m)
    release_f=44,
    keys=[  # frame, blade direction, edge direction, wished right grip   (nuki cut -> follow-through -> chiburi low stance)
        (51, (0.55, -0.83, 0.05), (-1.0, -0.3, 0.0), (0.12, -0.40, 1.30)),
        (58, (-0.72, -0.68, 0.12), (-0.6, 0.6, 0.0), (-0.24, -0.38, 1.30)),
        (61, (-0.45, -0.55, 0.70), (-0.3, -0.3, -1.0), (-0.30, -0.30, 1.40)),
        (67, (-0.55, -0.42, -0.72), (-0.2, -0.6, -0.6), (-0.42, -0.24, 1.10)),
    ],
    arc_lift=0.04,
    settle=[(0, 0.0), (67, 0.0), (70, 1.0), (78, 0.0)],                             # small overshoot after landing
    left_join=[(0, 0.0)],
    breath_amp=1.2, breath_period=90,
)


def ease(x): return x * x * (3 - 2 * x)


def curve(keys, f):
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1: return v0 + (v1 - v0) * ease(min(1, max(0, (f - f0) / max(1e-6, f1 - f0))))
    return keys[-1][1]


def rigid(R, p_from, p_to):       # 4x4 rotation R (3x3) about p_from, then moved so p_from lands on p_to
    M = R.to_4x4(); M.translation = p_to - R @ p_from; return M


def islands_split(o, pred, name):
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
    co = np.array([v.co[:] for v in o.data.vertices]); mask = np.zeros(len(co), bool)
    for i in range(k):
        idx = lab == i
        if pred(co[idx]): mask |= idx
    bm.free()
    me2 = o.data.copy(); o2 = bpy.data.objects.new(name, me2); S.collection.objects.link(o2)
    for src, keep in ((me2, mask), (o.data, ~mask)):
        b = bmesh.new(); b.from_mesh(src); b.verts.ensure_lookup_table()
        bmesh.ops.delete(b, geom=[b.verts[i] for i in np.nonzero(~keep)[0]], context="VERTS"); b.to_mesh(src); b.free()
    return o2, int(mask.sum())


def bone_parent(o, bone):
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = bone
    pb = P[bone]; o.matrix_parent_inverse = (rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted()
    o.matrix_basis = Matrix.Identity(4)


# ---- scabbard control + split the katana scabbard from the second sword/cords
for pb in P: pb.matrix_basis = Matrix.Identity(4)
VL.objects.active = rig; bpy.ops.object.mode_set(mode="EDIT")
b = A.edit_bones.new("SCABBARD"); b.head = MOUTH; b.tail = MOUTH + AX0 * 0.1; b.parent = A.edit_bones["Hips"]; b.use_deform = False
bpy.ops.object.mode_set(mode="OBJECT"); VL.update()


def on_scabbard(p):
    c = Vector(p.mean(0)); t = (c - KAT_TIP).dot(AX0) / LK; perp = ((c - KAT_TIP) - AX0 * (t * LK)).length
    return t < MOUTH_T + 0.01 and perp < 0.05


o19 = bpy.data.objects["Object_19"]
mw = o19.matrix_world.copy(); o19.parent = None; o19.matrix_world = mw
bpy.ops.object.select_all(action="DESELECT"); o19.select_set(True); VL.objects.active = o19
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
scab, nsc = islands_split(o19, on_scabbard, "KatanaScabbard"); print("scabbard verts", nsc)
bone_parent(scab, "SCABBARD"); bone_parent(o19, "Hips")

# ---- fist geometry (rest, world): knuckle axis, palm->finger direction, hole centre
def side_pts(names, sel):
    out = []
    for n in names:
        o = bpy.data.objects[n]; co = np.array([v.co[:] for v in o.data.vertices]); out.append(co[sel(co)].mean(0))
    return [Vector(p) for p in out]


# closed-fist data measured by the rig script (finger bones curl around this hole)
hole_R = Vector(rig["fist_hole"]); ax = Vector(rig["fist_axis"]).normalized() * CFG["knuckle_sign"]
pf = Vector(rig["fist_palm_dir"]); pf = (pf - ax * pf.dot(ax)).normalized()
rest_frame_R = Matrix((ax, pf, ax.cross(pf))).transposed()
print("fist axis", tuple(round(v, 3) for v in ax), "palm dir", tuple(round(v, 3) for v in pf), "hole", tuple(round(v, 3) for v in hole_R))
FINGERS = [b.name for b in A.bones if b.name.startswith("RightHand") and b.name[-1] in "123" and b.name != "RightHand"]
KN_W = Vector(rig["fist_axis"]).normalized(); CURL_SIGN = rig["curl_sign"]; CURL_DEG = list(rig["curl_deg"])
finger_axis = {n: (A.bones[n].matrix_local.to_3x3().inverted() @ KN_W).normalized() for n in FINGERS}


hand_rest = {s: A.bones[h].matrix_local.copy() for s, h in (("R", "RightHand"), ("L", "LeftHand"))}
pole_rest = {s: A.bones[f"POLE_{s}"].matrix_local.copy() for s in ("R", "L")}
sword_rest = A.bones["SWORD"].matrix_local.copy(); scab_rest = A.bones["SCABBARD"].matrix_local.copy()
G0 = MOUTH + AX0 * CFG["grip_r"]; GL0 = MOUTH + AX0 * CFG["grip_l"]
left_hold0 = KAT_TIP + AX0 * (0.62 * LK)                                               # left hand on the scabbard

# grip transform at the grab (sword at rest): fist frame -> (axis along AX0, palm->fingers = -E0)
def grip_T(AX, E, G, roll=0.0):
    q = Quaternion(AX, math.radians(roll))
    tgt = Matrix(((AX), (q @ -E), AX.cross(q @ -E))).transposed()
    return rigid(tgt @ rest_frame_R.inverted(), hole_R, G)


T_grab = grip_T(AX0, E0, G0, CFG["roll_r"]); T_grab0 = T_grab
hand_rest_R0 = A.bones["RightHand"].matrix_local.copy(); hand_rest_L0 = A.bones["LeftHand"].matrix_local.copy()

# key sword poses: (blade direction, edge direction, wished right grip point); grips are solved for reach
def pose_R(blade, edge):
    AXk = -Vector(blade).normalized(); Ek = Vector(edge); Ek = (Ek - AXk * Ek.dot(AXk)).normalized()
    return Matrix((AXk, Ek, AXk.cross(Ek))).transposed() @ Matrix((AX0, E0, AX0.cross(E0))).transposed().inverted()


def chest_pose(fr):
    for pb in P: pb.matrix_basis = Matrix.Identity(4)
    VL.update()
    tw = math.radians(curve(CFG["twist"], fr)); ln = math.radians(curve(CFG["lean"], fr))
    for nm in ("Spine", "Spine1", "Spine2"):
        pb = P[nm]; piv = rig.matrix_world @ pb.head
        M = Matrix.Translation(piv) @ (Quaternion(Vector((1, 0, 0)), ln / 3) @ Quaternion(Vector((0, 0, 1)), tw / 3)).to_matrix().to_4x4() @ Matrix.Translation(-piv)
        pb.matrix = M @ pb.matrix; VL.update()


lenR = (Vector(A.bones["RightArm"].head_local) - Vector(A.bones["RightForeArm"].head_local)).length + (Vector(A.bones["RightForeArm"].head_local) - Vector(A.bones["RightHand"].head_local)).length
lenL = (Vector(A.bones["LeftArm"].head_local) - Vector(A.bones["LeftForeArm"].head_local)).length + (Vector(A.bones["LeftForeArm"].head_local) - Vector(A.bones["LeftHand"].head_local)).length


def solve_key(fr, R, want, both, lim=0.95, front_y=None):
    chest_pose(fr)
    shR = rig.matrix_world @ P["RightArm"].head; shL = rig.matrix_world @ P["LeftArm"].head
    best = None; want = Vector(want)
    for dx in np.linspace(-0.16, 0.16, 9):
        for dy in np.linspace(-0.16, 0.30, 24):
            for dz in np.linspace(-0.16, 0.16, 9):
                g = want + Vector((dx, dy, dz)); T = rigid(R, G0, g)
                rr = ((T @ T_grab0 @ hand_rest_R0).translation - shR).length / lenR
                rl = ((T @ Matrix.Translation(GL0 - left_hold0) @ hand_rest_L0).translation - shL).length / lenL if both else 0
                if rr > lim or rl > lim: continue
                if front_y is not None and (T @ GL0).y > front_y: continue          # pommel must stay in front of the body
                c = (g - want).length
                if best is None or c < best[0]: best = (c, g, rr, rl)
    if best is None: raise SystemExit(f"no reachable pose for key at frame {fr}")
    print(f"key f{fr}: grip", tuple(round(v, 3) for v in best[1]), "reach R %.2f L %.2f" % (best[2], best[3]))
    return rigid(R, G0, best[1])


# choose knuckle direction + roll of the fist around the hilt that the arm reaches best at the grab
chest_pose(27); shR27 = rig.matrix_world @ P["RightArm"].head; best_g = None
for sgn in (1.0, -1.0):
    axs = Vector(rig["fist_axis"]).normalized() * sgn
    rf = Matrix((axs, pf, axs.cross(pf))).transposed()
    for roll in range(0, 360, 10):
        q = Quaternion(AX0, math.radians(roll)); tgt = Matrix((AX0, q @ -E0, AX0.cross(q @ -E0))).transposed()
        Tg = rigid(tgt @ rf.inverted(), hole_R, G0)
        dd = ((Tg @ hand_rest_R0).translation - shR27).length / lenR
        if best_g is None or dd < best_g[0]: best_g = (dd, sgn, roll, Tg)
print("grab: knuckle sign %+d roll %d deg reach %.2f" % (best_g[1], best_g[2], best_g[0]))
T_grab = T_grab0 = best_g[3]
KEYS = [(fk, solve_key(fk, pose_R(bd_, ed_), gp, both=False, lim=0.93)) for fk, bd_, ed_, gp in CFG["keys"]]


def lerp_T(T1, T2, u, lift=0.0):
    q = T1.to_quaternion().slerp(T2.to_quaternion(), u)
    p = T1.translation.lerp(T2.translation, u) + Vector((0, 0, lift * math.sin(math.pi * u)))
    M = q.to_matrix().to_4x4(); M.translation = p; return M


def lerp_hand(T1, T2, u, rest, lift=0.0):
    M1, M2 = T1 @ rest, T2 @ rest
    q = M1.to_quaternion().slerp(M2.to_quaternion(), u)
    p = M1.translation.lerp(M2.translation, u) + Vector((0, 0, lift * math.sin(math.pi * u)))
    M = q.to_matrix().to_4x4(); M.translation = p; return M


def sword_T(f):
    T_slide = Matrix.Translation(AX0 * curve(CFG["slide"], f))
    f0, fN = CFG["release_f"], KEYS[-1][0]
    if f <= f0: return T_slide
    span = fN - f0; u = ease(min(1, (f - f0) / span))
    keys = [(0.0, T_slide)] + [(ease((fk - f0) / span), Tk) for fk, Tk in KEYS]
    for (ua, Ta), (ub, Tb) in zip(keys, keys[1:]):
        if u <= ub + 1e-9:
            k = (u - ua) / max(1e-9, ub - ua)
            q = Ta.to_quaternion().slerp(Tb.to_quaternion(), k)
            g = (Ta @ G0).lerp(Tb @ G0, k) + Vector((0, 0, CFG["arc_lift"] * math.sin(math.pi * k)))
            T = rigid(q.to_matrix(), G0, g); break
    st = curve(CFG["settle"], f)
    if st:
        g = T @ G0; T = rigid(Quaternion(Vector((0, 1, 0)), math.radians(-5 * st)).to_matrix(), g, g) @ T
    return T


def world_rot_about(pb, R, pivot):
    M = Matrix.Translation(pivot) @ R.to_4x4() @ Matrix.Translation(-pivot)
    pb.matrix = M @ pb.matrix; VL.update()


arm_len = {s: (Vector(A.bones[f"{n}Arm"].head_local) - Vector(A.bones[f"{n}ForeArm"].head_local)).length
           + (Vector(A.bones[f"{n}ForeArm"].head_local) - Vector(A.bones[f"{n}Hand"].head_local)).length
           for s, n in (("R", "Right"), ("L", "Left"))}
worst = {"R": 0, "L": 0}; log = {}
for pb in P: pb.rotation_mode = "QUATERNION"
if len(ARGS) > 1: CFG["frames"] = int(ARGS[1])          # longer bake = longer breathing hold
S.frame_start, S.frame_end = 1, CFG["frames"]
for f in range(1, CFG["frames"] + 1):
    fr = f - 1
    for pb in P: pb.matrix_basis = Matrix.Identity(4)
    VL.update()
    tw = math.radians(curve(CFG["twist"], fr)); ln = math.radians(curve(CFG["lean"], fr))
    br = math.radians(CFG["breath_amp"] * math.sin(2 * math.pi * fr / CFG["breath_period"])) * min(1, max(0, (fr - 60) / 20))
    for nm in ("Spine", "Spine1", "Spine2"):
        pb = P[nm]; piv = rig.matrix_world @ pb.head
        world_rot_about(pb, Quaternion(Vector((0, 0, 1)), tw / 3).to_matrix(), piv)
        world_rot_about(pb, Quaternion(Vector((1, 0, 0)), (ln + br) / 3).to_matrix(), piv)
    hd = P["Head"]; piv = rig.matrix_world @ hd.head
    world_rot_about(hd, Quaternion(Vector((0, 0, 1)), math.radians(curve(CFG["head_yaw"], fr)) - tw * 0.6).to_matrix(), piv)
    world_rot_about(hd, Quaternion(Vector((1, 0, 0)), math.radians(curve(CFG["head_pitch"], fr))).to_matrix(), piv)
    # sword + scabbard
    Tsw = sword_T(fr); P["SWORD"].matrix = Tsw @ sword_rest; VL.update()
    Tsc_local = Matrix.Translation(-AX0 * curve(CFG["scab"], fr))
    hips_now = P["Hips"].matrix @ A.bones["Hips"].matrix_local.inverted()
    P["SCABBARD"].matrix = hips_now @ Tsc_local @ scab_rest; VL.update()
    Tsc = hips_now @ Tsc_local
    # right hand: rest -> grab (reach), then rides the sword
    rch = curve(CFG["reach"], fr)
    M_R = (Tsw @ T_grab @ hand_rest["R"]) if rch >= 1 else lerp_hand(Matrix.Identity(4), T_grab, rch, hand_rest["R"], lift=0.05)
    P["IK_R"].matrix = M_R
    # left hand: rides the scabbard, then joins the hilt at the pommel grip
    lj = curve(CFG["left_join"], fr)
    T_Lsc = Tsc
    T_Lhilt = Tsw @ Matrix.Translation(GL0 - left_hold0)
    M_L = (T_Lsc @ hand_rest["L"]) if lj <= 0 else lerp_hand(T_Lsc, T_Lhilt, lj, hand_rest["L"], lift=0.04)
    P["IK_L"].matrix = M_L
    # fingers close around the hilt during the reach
    cu = curve(CFG["curl"], fr)
    for n in FINGERS:
        k = int(n[-1]) - 1
        P[n].rotation_quaternion = Quaternion(finger_axis[n], CURL_SIGN * math.radians(CURL_DEG[k]) * cu)
    # elbow poles ride the chest
    sp = P["Spine2"].matrix @ A.bones["Spine2"].matrix_local.inverted()
    for s in ("R", "L"): P[f"POLE_{s}"].matrix = sp @ pole_rest[s]
    VL.update()
    for s, sh in (("R", "RightArm"), ("L", "LeftArm")):
        d = (M_R if s == "R" else M_L).translation - (rig.matrix_world @ P[sh].head)
        worst[s] = max(worst[s], d.length / arm_len[s])
        if f % 4 == 1 or d.length / arm_len[s] > 1.0: log.setdefault(f, {})[s] = round(d.length / arm_len[s], 2)
    for pb in P:
        pb.keyframe_insert("location", frame=f); pb.keyframe_insert("rotation_quaternion", frame=f)
print(" ".join(f"{k}:{v.get('R','-')}/{v.get('L','-')}" for k, v in sorted(log.items())))
print("max reach used: R %.2f  L %.2f  (1.0 = arm straight)" % (worst["R"], worst["L"]))
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
