"""Samurai intro v3: the v2 intro (frames 1-263 reused as rendered) + a 5-cut katana draw before the hero reveal,
then lights flicker out and bang on for a new hero shot with the blade drawn. Built on the rigged intro scene with the
baked draw (renders/farm/mech/intro3-draw-v1.blend). New frames: 264-494 (end card 495-584 added in finishing).
  blender -b renders/farm/mech/intro3-draw-v1.blend -P scripts/blender/samurai_intro3.py -- <out.blend>
"""
import bpy, sys, math
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
S = bpy.context.scene; VL = bpy.context.view_layer
rig = bpy.data.objects["SamuraiRig"]
KAT_HILT_END = Vector((0.3315, -0.398, 1.4309)); KAT_TIP = Vector((0.1255, 0.6331, 0.5638))
LK = (KAT_HILT_END - KAT_TIP).length; AX0 = (KAT_HILT_END - KAT_TIP).normalized()
MOUTH = KAT_TIP + AX0 * (0.695 * LK); G0 = MOUTH + AX0 * 0.085; FACE = Vector((0.0, -0.10, 1.80))

CFG = dict(
    start=264, end=494,
    # edit frame -> draw animation frame (speed ramps: slow grip + slide, real-time cut and snap)
    timewarp=[(264, 10), (287, 28), (288, 28.3), (317, 44), (318, 44.2), (330, 48), (338, 56), (344, 58),
              (345, 58.3), (360, 64), (364, 67.5), (368, 70), (369, 70.3), (398, 100), (414, 116), (415, 117), (494, 196)],
    shots=[  # name, first frame, lens, fstop, focus, [(frame, cam pos, look at)], shake
        ("D1_HAND", 264, 55, 2.0, G0, [(264, G0 + Vector((0.34, -0.36, -0.10)), G0), (287, G0 + Vector((0.27, -0.29, -0.08)), G0)], 0.0015),
        ("D2_SLIDE", 288, 32, 2.8, None, [(288, MOUTH + Vector((0.30, -0.10, -0.18)), MOUTH + AX0 * 0.05),
                                          (317, MOUTH + Vector((0.34, -0.24, -0.08)), MOUTH + AX0 * 0.42)], 0.0015),
        ("D3_CUT", 318, 20, 4.0, Vector((0.0, -0.30, 1.35)), [(318, Vector((-0.34, -1.02, 0.28)), Vector((0.02, -0.20, 1.40))),
                                                              (344, Vector((-0.42, -0.98, 0.24)), Vector((0.02, -0.20, 1.44)))], 0.002),
        ("D4_SHOULDER", 345, 28, 2.8, Vector((-0.45, -0.30, 1.20)), [(345, Vector((-0.62, 0.62, 1.92)), Vector((-0.62, -0.80, 0.95))),
                                                                     (368, Vector((-0.70, 0.55, 1.88)), Vector((-0.66, -0.80, 0.92)))], 0.002),
        ("D5_HELMET", 369, 75, 2.0, FACE, [(369, Vector((-0.62, -1.32, 1.40)), FACE + Vector((0, 0.04, -0.06))),
                                           (414, Vector((-0.52, -1.18, 1.44)), FACE + Vector((0, 0.04, -0.05)))], 0.0012),
        ("HERO2", 415, 45, 2.8, FACE, [(415, Vector((0.40, -3.45, 1.58)), Vector((-0.10, 0.0, 1.44))),
                                       (494, Vector((0.28, -3.05, 1.60)), Vector((-0.08, 0.0, 1.47)))], 0.002),
    ],
    snap_jolt=(364, [(0.0, 0.0, 0.0), (0.022, -0.012, 0.010), (-0.012, 0.008, -0.006), (0.005, -0.003, 0.002), (0, 0, 0)]),
    cut_f=333, cut_stutter=[(0, 1.0), (1, 0.35), (2, 1.0), (3, 0.6), (5, 1.0)],
    # lights flicker out after the stance, then bang on for the hero (intro pattern shifted to the new hero frame)
    flicker=[(398, 1.0), (400, 0.15), (401, 1.0), (403, 0.0), (405, 0.7), (406, 0.0), (409, 1.0), (410, 0.1), (412, 0.0), (415, 1.15), (424, 1.0)],
    eye_flare=[(374, 1.0), (376, 1.7), (380, 1.0)],
    blade_glow=[(263, 1.0), (332, 1.0), (333, 1.8), (338, 1.0), (494, 1.05)],
    blade_light=[(263, 0.0), (300, 0.0), (312, 8.0), (494, 8.0)],
    motion_blur=0.5,
)


def interp(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1: return y0 + (y1 - y0) * (x - x0) / max(1e-9, x1 - x0)
    return pts[-1][1]


def bone_parent(o, bone):
    mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = "BONE"; o.parent_bone = bone
    pb = rig.pose.bones[bone]; o.matrix_parent_inverse = (rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted()
    o.matrix_basis = mw


# ---- 1. re-time the baked draw onto the edit timeline (rest pose before the draw)
S.frame_set(1); VL.update()
old = rig.animation_data.action; new = bpy.data.actions.new("Intro3Draw")
for fc in old.fcurves:
    nf = new.fcurves.new(fc.data_path, index=fc.array_index, action_group=fc.group.name if fc.group else "")
    pts = [(1, fc.evaluate(1)), (CFG["start"] - 1, fc.evaluate(1))]
    pts += [(e, fc.evaluate(interp(CFG["timewarp"], e))) for e in range(CFG["start"], CFG["end"] + 1)]
    nf.keyframe_points.add(len(pts))
    for k, (x, y) in zip(nf.keyframe_points, pts): k.co = (x, y); k.interpolation = "LINEAR"
rig.animation_data.action = new

# ---- 2. lights: on through the draw, stutter on the cut, flicker out, bang on for the hero
for name in ("key", "back_haze", "rim_L", "rim_R"):
    L = bpy.data.objects[name].data; fc = L.animation_data.action.fcurves.find("energy")
    full = fc.evaluate(CFG["start"] - 1); base = fc.evaluate(1)
    for i in range(len(fc.keyframe_points) - 1, -1, -1):
        if fc.keyframe_points[i].co.x >= CFG["start"]: fc.keyframe_points.remove(fc.keyframe_points[i])
    pts = [(CFG["start"], full)]
    if name == "key": pts += [(CFG["cut_f"] + d, full * v) for d, v in CFG["cut_stutter"]]
    pts += [(f, max(base, full * v)) for f, v in CFG["flicker"]]
    for f, v in pts: L.energy = v; L.keyframe_insert("energy", frame=f)
    for k in fc.keyframe_points: k.interpolation = "CONSTANT"

# ---- 3. eyes flare in the helmet close-up; visor light rides the head; sword glow + its light ride the sword
g = bpy.data.node_groups["LimeStrips"]; ef = next(fc for fc in g.animation_data.action.fcurves if 'eyes' in fc.data_path)
for f, v in CFG["eye_flare"]: ef.keyframe_points.insert(f, v).interpolation = "LINEAR"
bone_parent(bpy.data.objects["visor"], "Head")
if "sword_light" in bpy.data.objects: bone_parent(bpy.data.objects["sword_light"], "SWORD")
sg = bpy.data.node_groups.get("SwordGlow")
if sg:                                                     # keep the whole katana lit once it moves (sweep fully on)
    sock = sg.nodes["sweep"].outputs[0]
    sock.default_value = 1.08; sock.keyframe_insert("default_value", frame=CFG["start"] - 1)
    sock.default_value = 10.0; sock.keyframe_insert("default_value", frame=CFG["start"])
bt = bpy.data.materials["BladeSteel"].node_tree
for f, v in CFG["blade_glow"]: bt.nodes["blade_glow"].outputs[0].default_value = v; bt.nodes["blade_glow"].outputs[0].keyframe_insert("default_value", frame=f)
bl = bpy.data.objects.new("blade_light", bpy.data.lights.new("blade_light", "POINT")); S.collection.objects.link(bl)
bl.data.color = (0.62, 1.0, 0.02); bl.data.shadow_soft_size = 0.05; bl.visible_camera = False
bl.location = KAT_TIP + AX0 * (LK * 0.40); bone_parent(bl, "SWORD")
for f, v in CFG["blade_light"]: bl.data.energy = v; bl.data.keyframe_insert("energy", frame=f)

# ---- 4. cameras + markers
for m in [m for m in S.timeline_markers if m.frame >= CFG["start"]]: S.timeline_markers.remove(m)
for name, f0, lens, fst, focus, keys, shake in CFG["shots"]:
    cd = bpy.data.cameras.new(name); cam = bpy.data.objects.new(name, cd); S.collection.objects.link(cam)
    cd.lens = lens; cd.dof.use_dof = True; cd.dof.aperture_fstop = fst; cd.clip_start = 0.02
    tgt = bpy.data.objects.new(name + "_aim", None); S.collection.objects.link(tgt)
    tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    if focus is None: cd.dof.focus_object = tgt
    else:
        fo = bpy.data.objects.new(name + "_focus", None); S.collection.objects.link(fo); fo.location = focus; cd.dof.focus_object = fo
    for f, pos, look in keys:
        cam.location = pos; cam.keyframe_insert("location", frame=f); tgt.location = look; tgt.keyframe_insert("location", frame=f)
    for ob in (cam, tgt):
        for fc in ob.animation_data.action.fcurves:
            for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
    if name == "D4_SHOULDER":                                # camera jolt on the chiburi snap
        fj, offs = CFG["snap_jolt"]; base_fc = cam.animation_data.action.fcurves
        for i, o in enumerate(offs):
            f = fj + i
            for ax in range(3):
                fc = base_fc.find("location", index=ax); fc.keyframe_points.insert(f, fc.evaluate(f) + o[ax]).interpolation = "LINEAR"
    for i, fc in enumerate(cam.animation_data.action.fcurves):
        m = fc.modifiers.new("NOISE"); m.scale = 40; m.strength = shake; m.phase = 2.3 * i + f0
    S.timeline_markers.new(name, frame=f0).camera = cam

S.frame_start, S.frame_end = CFG["start"], CFG["end"]
S.render.use_motion_blur = True; S.render.motion_blur_shutter = CFG["motion_blur"]
S.frame_set(CFG["start"])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
