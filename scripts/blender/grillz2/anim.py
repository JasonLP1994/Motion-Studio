# Grillz animation (notes/briefs/grillz-anim.md). Exec'd at the end of grillz2.py when ANIM=1 (it reuses M, C0, fwd, side, upv,
# up_row, lo_row, L2W, to_local). The model has no rig, so a small one is built from computed weights:
#   head (pivot at the neck), jaw (hinge behind the teeth), lip corners L/R (grin). Teeth + PD letters ride the head/jaw bones.
# Four shots on a 120 BPM grid (1 beat = 12 frames at 24 fps), ending on the mouth: slow grin + light sweep across the PD.
import bpy, math
import numpy as np
from mathutils import Vector, Matrix, Euler
FPS = 24; NF = 240
S.render.fps = FPS; S.frame_start = 1; S.frame_end = NF
# ---- clean void: hide the leftover set (trees, ground) so it's the man on the magenta backdrop
for cn in ("SCENE", "SSS"):
    c = bpy.data.collections.get(cn)
    if c:
        for o in c.all_objects: o.hide_render = True
body = bpy.data.objects["Genesis8Male.002"]
V = wverts(body); Lc = to_local(V)
def sstep(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
x, y, z = Lc[:, 0], Lc[:, 1], Lc[:, 2]
# head: everything above the neck (local z is head-up; the neck base sits ~11 cm below the bite, ~5 cm behind it)
NECK = np.array([-5.0, 0.0, -11.0])
w_head = sstep((z - NECK[2]) / 7.0)
# jaw: below the bite, in front of the hinge, fading out down the throat
HINGE = np.array([-8.5, 0.0, 2.5])
w_jaw = sstep((0.2 - z) / 1.2) * sstep((x + 9.5) / 4.0) * sstep((z + 9.0) / 3.5) * sstep((7.5 - np.abs(y)) / 2.0)
# lip corners from the Lips material
li = [i for i, m in enumerate(body.data.materials) if m and m.name.startswith("Lips")][0]
lv = set()
for p in body.data.polygons:
    if p.material_index == li: lv.update(p.vertices)
lv = np.array(sorted(lv)); LL = Lc[lv]
cR = LL[np.argmin(LL[:, 1])]; cL = LL[np.argmax(LL[:, 1])]
def corner_w(c):
    d = np.linalg.norm((Lc - c) * np.array([1.4, 1.0, 1.2]), axis=1)
    return np.exp(-(d / 1.6) ** 2) * (x > c[0] - 3.0)
w_lL, w_lR = corner_w(cL), corner_w(cR)
print("ANIM corners", cL.round(2), cR.round(2), "jaw verts", int((w_jaw > 0.5).sum()))
# ---- armature
ad = bpy.data.armatures.new("RIG_Head"); arm = bpy.data.objects.new("RIG_Head", ad); S.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
def eb(name, h, t, zaxis, parent=None):
    b = ad.edit_bones.new(name); b.head = L2W(h); b.tail = L2W(t); b.align_roll(Vector(zaxis.tolist()))
    if parent: b.parent = ad.edit_bones[parent]
    return b
eb("head", NECK, NECK + np.array([0, 0, 10.0]), fwd)                    # Y=up, Z=fwd, X=side: nod=X, turn=Y, tilt=Z
eb("jaw", HINGE, np.array([1.0, 0, -3.0]), upv, "head")
eb("lip.L", cL, cL + np.array([1.0, 0, 0]), upv, "head")             # Y=fwd, Z=up, X=-side
eb("lip.R", cR, cR + np.array([1.0, 0, 0]), upv, "head")
bpy.ops.object.mode_set(mode='OBJECT')
# weights: normalise so head = remainder after jaw/lips (vertices with no head weight stay on the static body)
for n, w in (("head", w_head * (1 - np.clip(w_jaw + w_lL + w_lR, 0, 1))), ("jaw", w_head * w_jaw), ("lip.L", w_head * w_lL), ("lip.R", w_head * w_lR)):
    vg = body.vertex_groups.new(name=n)
    for i in np.nonzero(w > 1e-3)[0]: vg.add([int(i)], float(w[i]), 'REPLACE')
md = body.modifiers.new("Armature", 'ARMATURE'); md.object = arm
# teeth + letters ride the bones
def ride(o, bone):
    bpy.context.view_layer.update(); mw = o.matrix_world.copy(); o.parent = arm; o.parent_type = "BONE"; o.parent_bone = bone
    bpy.context.view_layer.update(); o.matrix_world = mw
for o in up_row: ride(o, "head")
for o in lo_row: ride(o, "jaw")
for o in bpy.data.objects:
    if o.name.startswith("PD_"): ride(o, "head")
# ---- focus target on the mouth (rides the head)
foc = bpy.data.objects.new("EMPTY_Focus", None); S.collection.objects.link(foc)
_pd = [o for o in bpy.data.objects if o.name.startswith("PD_") and o.name.endswith("_face")]
if _pd:
    _c = np.vstack([wverts(o) for o in _pd]).mean(0); foc.location = Vector(_c.tolist())
else: foc.location = L2W((MU["a"], 0, 0))
ride(foc, "head")
# ---- performance (frame, value) keys; everything eased
pb = arm.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
def key(bone, prop, idx, frames):
    p = pb[bone]
    for f, v in frames:
        getattr(p, prop)[idx] = v; p.keyframe_insert(prop, index=idx, frame=f)
D = math.radians
# head nod (X: + tips the face down toward the camera from his tilted-back pose)
key("head", "rotation_euler", 0, [(1, D(-4)), (30, D(14)), (48, D(10)), (60, D(4)), (96, D(8)), (108, D(-6)), (120, D(10)), (132, D(-4)), (144, D(8)), (170, D(12)), (240, D(14))])
# head turn (Y)
key("head", "rotation_euler", 1, [(1, D(-14)), (40, D(4)), (49, D(22)), (88, D(-6)), (97, D(-10)), (144, D(12)), (150, D(6)), (200, D(-3)), (240, D(-5))])
# head tilt (Z)
key("head", "rotation_euler", 2, [(1, D(8)), (48, D(-4)), (96, D(6)), (144, D(-8)), (190, D(4)), (240, D(6))])
# jaw: two snaps on the beats of shot 3, then closed for the grin (X: + opens; sign checked in style frames)
JS = E("JAW_SIGN", -1.0)
key("jaw", "rotation_euler", 0, [(1, 0), (97, 0), (103, D(12) * JS), (108, 0), (115, D(14) * JS), (120, 0), (127, D(10) * JS), (132, 0), (240, 0)])
# grin: corners back + up + out, slow ease from 170 to 204, held
for bn, sgn in (("lip.L", 1.0 if cL[1] > 0 else -1.0), ("lip.R", 1.0 if cR[1] > 0 else -1.0)):
    G = E("GRIN", 0.75)
    for idx, val in ((0, -sgn * 0.45 * G), (1, -0.35 * G), (2, 0.55 * G)):
        key(bn, "location", idx, [(1, 0), (168, 0), (204, val), (240, val * 1.05)])
for fc in arm.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
# tiny living drift on the head (breath)
for i, amp, fr in ((0, 0.8, 0.9), (2, 0.6, 1.3)):
    fc = arm.animation_data.action.fcurves.find('pose.bones["head"].rotation_euler', index=i)
    nm = fc.modifiers.new('NOISE'); nm.scale = 18 * fr; nm.strength = D(amp); nm.phase = i * 7
# ---- cameras: 4 shots bound with markers, positions in the mouth frame (cm)
def cam_obj(name, lens, fstop):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.5
    cd.dof.use_dof = True; cd.dof.focus_object = foc; cd.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, cd); S.collection.objects.link(o); return o
def aim(o, f, pos, tgt, roll):
    p = L2W(pos); t = L2W(tgt); fw = (t - p).normalized(); up = Vector(upv.tolist())
    r = fw.cross(up).normalized(); u = r.cross(fw)
    R = Matrix((r, u, -fw)).transposed() @ Matrix.Rotation(math.radians(roll), 3, 'Z')
    o.location = p; o.rotation_euler = R.to_euler(); o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", frame=f)
def lens(o, f, mm): o.data.lens = mm; o.data.keyframe_insert("lens", frame=f)
SIDE = E("CAM_SIDE", -1.0)            # +1 = his right / clean side of the neck (flip if the neck gap shows)
# 1) worm's-eye dutch, wide, slow push up the chin as he looks down at us
c1 = cam_obj("CAM_01_WormDutch", 18, 4.0)
aim(c1, 1, (40, 14 * SIDE, -38), (0, 0, -2), -24); aim(c1, 48, (28, 9 * SIDE, -26), (0, 0, -1), -16)
# 2) long-lens profile with a whip-in: camera snaps in from a pan, then a slow slide
c2 = cam_obj("CAM_02_ProfileTele", 135, 2.8)
aim(c2, 49, (40, 150 * SIDE, 30), (0, -20 * SIDE, 0), 10); aim(c2, 53, (55, 140 * SIDE, 8), (-3, 0, 1), 4); aim(c2, 96, (75, 125 * SIDE, 4), (-3, 0, 1), 0)
# 3) top-down canted orbit while the jaw snaps
c3 = cam_obj("CAM_03_TopOrbit", 35, 4.0)
aim(c3, 97, (24, 18 * SIDE, 16), (0, 0, -1), 30); aim(c3, 144, (30, 0, 12), (0, 0, -1), -18)
# 4) 3/4 push from the face into the mouth: grin + glint, ends on the mouth
c4 = cam_obj("CAM_04_MouthPush", 60, 4.0)
S4 = E("CAM4_SIDE", 1.0)
aim(c4, 145, (55, 30 * S4, 6), (-1, 0, 2), 8); aim(c4, 176, (30, 12 * S4, 2), (0, 0, 0), 3); aim(c4, 240, (E("END_D", 20.0), 3 * S4, -2), (0, 0, -0.3), 0)
lens(c4, 145, 60); lens(c4, 240, 85)
for o in (c1, c2, c3, c4):
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
    if o.data.animation_data:
        for fc in o.data.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
for f, o in ((1, c1), (49, c2), (97, c3), (145, c4)):
    mk = S.timeline_markers.new(o.name, frame=f); mk.camera = o
S.camera = c1
# the mouth push keeps the mouth centred while the head moves (track the focus empty; small roll kept via up axis)
tc_ = c4.constraints.new('TRACK_TO'); tc_.target = foc; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
# ---- glint: a thin bright strip sweeps across the front teeth (glossy only) 206 -> 226, plus letter glow pulse
gl = bpy.data.lights.new("LGT_Glint_Sweep", 'AREA'); gl.shape = 'RECTANGLE'; gl.size = 0.6; gl.size_y = 30; gl.color = (1, 0.95, 0.8)
go = bpy.data.objects.new("LGT_Glint_Sweep", gl); S.collection.objects.link(go); go.visible_diffuse = False
def gpos(f, ys, e):
    p = L2W((14, ys, 4)); go.location = p; go.rotation_euler = (L2W((0, ys * 0.2, 0)) - p).to_track_quat('-Z', 'Y').to_euler()
    gl.energy = e; go.keyframe_insert("location", frame=f); go.keyframe_insert("rotation_euler", frame=f); gl.keyframe_insert("energy", frame=f)
K_ = E("LIGHT_E", 70.0)
gpos(1, -14, 0); gpos(204, -14, 0); gpos(206, -9, 260 * K_); gpos(226, 9, 260 * K_); gpos(228, 14, 0); gpos(240, 14, 0)
en = bpy.data.materials.get("MAT_LetterEnamel")
if en:
    es = en.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, v in ((1, 0.15), (204, 0.15), (214, 1.2), (232, 0.35), (240, 0.35)):
        es.default_value = v; es.keyframe_insert("default_value", frame=f)
S.render.use_motion_blur = True; S.render.motion_blur_shutter = 0.5
print("ANIM BUILT", NF)
