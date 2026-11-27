"""Samurai katana-draw shot (5 s, 16:9) from the rigged + animated samurai (renders/farm/mech/samurai-draw-v2.blend).
Moody intro lighting, a lime light riding the blade, a light stutter on the cut, eyes ignite on the final stance,
slow low push-in from the front-left with a little handheld drift, motion blur.
  blender -b renders/farm/mech/samurai-draw-v2.blend -P scripts/blender/samurai_draw_shot.py -- <out.blend>
"""
import bpy, sys, math
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
CFG = dict(
    frames=150, lead=20, res=(1920, 1080),
    haze_col=(0.13, 0.19, 0.29), city_emit=0.22, world=(0.002, 0.003, 0.006), haze_scale=0.20, rim_scale=0.2, rim_spread=50,
    cut_flicker=[(70, 1.0), (71, 0.35), (72, 1.0), (73, 0.6), (75, 1.0)],              # key light stutter on the cut
    eyes=[(1, 0.0), (110, 0.0), (112, 1.0), (114, 0.1), (117, 1.2), (119, 0.4), (122, 1.0), (150, 1.0)],
    visor=[(1, 0.0), (111, 0.0), (112, 0.25), (114, 0.02), (117, 0.3), (122, 0.15)],
    blade_glow=[(1, 1.0), (70, 1.0), (71, 1.8), (76, 1.0), (150, 1.05)],
    blade_light=[(1, 0.0), (56, 0.0), (66, 9.0), (150, 9.0)],
    cam=[(1, (2.55, -3.45, 1.02), (0.02, 0.0, 1.16)), (150, (1.95, -2.70, 1.10), (-0.08, -0.08, 1.24))],
    lens=35, fstop=2.8, focus=(0.0, -0.12, 1.40), shake=0.004,
    motion_blur=0.5,
)
S = bpy.context.scene; VL = bpy.context.view_layer
rig = bpy.data.objects["SamuraiRig"]


def clear_anim(idb):
    if idb.animation_data: idb.animation_data_clear()


def key_val(sock, pts, interp="BEZIER"):
    for f, v in pts: sock.default_value = v; sock.keyframe_insert("default_value", frame=f)


# ---- timing: shift the baked draw by the lead-in
for fc in rig.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.co.x += CFG["lead"]; k.handle_left.x += CFG["lead"]; k.handle_right.x += CFG["lead"]
S.frame_start, S.frame_end = 1, CFG["frames"]; S.render.fps = 30
S.render.resolution_x, S.render.resolution_y = CFG["res"]; S.render.resolution_percentage = 100

# ---- lights: steady moody setup (intro's dim background), key stutters on the cut
for name in ("key", "back_haze", "rim_L", "rim_R"):
    L = bpy.data.objects[name].data; full = L.energy
    if L.animation_data and L.animation_data.action:
        full = max(k.co[1] for fc in L.animation_data.action.fcurves for k in fc.keyframe_points)
    clear_anim(L)
    if name == "back_haze": full *= CFG["haze_scale"]
    if name.startswith("rim"): full *= CFG["rim_scale"]; L.spread = math.radians(CFG["rim_spread"]); bpy.data.objects[name].visible_camera = False
    pts = [(1, full)] + ([(f, full * v) for f, v in CFG["cut_flicker"]] if name == "key" else [])
    for f, v in pts: L.energy = v; L.keyframe_insert("energy", frame=f)
    for fc in L.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "CONSTANT"
hm = bpy.data.materials["haze"]; next(n for n in hm.node_tree.nodes if n.type == "PRINCIPLED_VOLUME").inputs["Color"].default_value = (*CFG["haze_col"], 1)
cn = bpy.data.materials["city"].node_tree.nodes; cn["Math"].inputs[1].default_value = CFG["city_emit"]
cn["Principled BSDF"].inputs["Base Color"].default_value = (0.008, 0.011, 0.017, 1); cn["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15
S.world.node_tree.nodes["Background"].inputs[0].default_value = (*CFG["world"], 1)

# ---- strips fully lit, eyes ignite on the stance; visor light follows the head
g = bpy.data.node_groups["LimeStrips"]; clear_anim(g)
g.nodes["reveal"].outputs[0].default_value = 2.4; g.nodes["glow"].outputs[0].default_value = 1.0
key_val(g.nodes["eyes"].outputs[0], CFG["eyes"])
vis = bpy.data.objects["visor"]; clear_anim(vis.data)
for f, v in CFG["visor"]: vis.data.energy = v; vis.data.keyframe_insert("energy", frame=f)
mw = vis.matrix_world.copy(); vis.parent = rig; vis.parent_type = "BONE"; vis.parent_bone = "Head"
pb = rig.pose.bones["Head"]; vis.matrix_parent_inverse = (rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted(); vis.matrix_basis = mw

# ---- blade: edge glow pulse + a lime light riding the blade
bt = bpy.data.materials["BladeSteel"].node_tree; key_val(bt.nodes["blade_glow"].outputs[0], CFG["blade_glow"])
KAT_HILT_END = Vector((0.3315, -0.398, 1.4309)); KAT_TIP = Vector((0.1255, 0.6331, 0.5638)); AX0 = (KAT_HILT_END - KAT_TIP).normalized()
bl = bpy.data.objects.new("blade_light", bpy.data.lights.new("blade_light", "POINT")); S.collection.objects.link(bl)
bl.data.color = (0.62, 1.0, 0.02); bl.data.shadow_soft_size = 0.05; bl.visible_camera = False
bl.location = KAT_TIP + AX0 * ((KAT_HILT_END - KAT_TIP).length * 0.40)
bmw = bl.matrix_world.copy(); bl.parent = rig; bl.parent_type = "BONE"; bl.parent_bone = "SWORD"
pb = rig.pose.bones["SWORD"]; bl.matrix_parent_inverse = (rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))).inverted(); bl.matrix_basis = bmw
for f, v in CFG["blade_light"]: bl.data.energy = v; bl.data.keyframe_insert("energy", frame=f)

# ---- camera: slow low push-in, handheld drift, DOF on the chest
cd = bpy.data.cameras.new("DrawCam"); cam = bpy.data.objects.new("DrawCam", cd); S.collection.objects.link(cam)
cd.lens = CFG["lens"]; cd.dof.use_dof = True; cd.dof.aperture_fstop = CFG["fstop"]
foc = bpy.data.objects.new("draw_focus", None); S.collection.objects.link(foc); foc.location = CFG["focus"]; cd.dof.focus_object = foc
tgt = bpy.data.objects.new("draw_target", None); S.collection.objects.link(tgt)
tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
for f, loc, look in CFG["cam"]:
    cam.location = loc; cam.keyframe_insert("location", frame=f); tgt.location = look; tgt.keyframe_insert("location", frame=f)
for ob in (cam, tgt):
    for fc in ob.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
for i, fc in enumerate(cam.animation_data.action.fcurves):
    m = fc.modifiers.new("NOISE"); m.scale = 45; m.strength = CFG["shake"]; m.phase = 3.1 * i
for m in list(S.timeline_markers): S.timeline_markers.remove(m)
S.camera = cam
S.render.use_motion_blur = True; S.render.motion_blur_shutter = CFG["motion_blur"]
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
