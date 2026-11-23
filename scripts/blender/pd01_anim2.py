# PD-01 animation v2 (user: extreme close-ups, reveal only at the very end). Run after pd01c.py:
#   PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber3/pd01c.py -P work/cyber3/pd01_anim2.py -- OUT.blend
# 15 s @ 24 fps = 360 frames. Six 1.5 s extreme close-ups (shallow focus, slow linear drift), then the reveal pull-out.
import bpy, math, sys, os
from mathutils import Vector
S = bpy.context.scene; S.render.fps = 24; S.frame_start, S.frame_end = 1, 360
E = lambda k, d: float(os.environ.get(k, d))
out = sys.argv[sys.argv.index("--") + 1:][0] if "--" in sys.argv else None
HC = Vector((0.0, -0.07, 1.627))
V = Vector

def kf(obj, path, frame, value, interp='LINEAR', easing='AUTO', index=-1):
    if index < 0: setattr(obj, path, value)
    else: getattr(obj, path)[index] = value
    obj.keyframe_insert(path, frame=frame, index=index)
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if int(round(kp.co.x)) == frame: kp.interpolation = interp; kp.easing = easing
def shot(name, f0, f1, cam0, cam1, tgt0, tgt1, lens, fstop=2.8):
    c = bpy.data.objects.new("CAM_" + name, bpy.data.cameras.new("CAM_" + name)); S.collection.objects.link(c); c.data.lens = lens
    c.data.clip_start = 0.005
    t = bpy.data.objects.new("EMPTY_CamTarget_" + name, None); S.collection.objects.link(t)
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop; c.data.dof.focus_object = t
    kf(c, "location", f0, V(cam0)); kf(c, "location", f1, V(cam1)); kf(t, "location", f0, V(tgt0)); kf(t, "location", f1, V(tgt1))
    m = S.timeline_markers.new(c.name, frame=f0); m.camera = c
    return c, t

# --- the six extreme close-ups (positions found from the model's geometry; frames 1-216)
SH = [
    # name        frames     camera start            camera end              target start            target end              lens
    ("ECU_Seam",   1,  36, (-0.46, -0.16, 1.205), (-0.46, -0.04, 1.200), (-0.33, -0.10, 1.192), (-0.33, 0.00, 1.192), 100),
    ("ECU_Print",  37,  72, (-0.62, -0.14, 1.255), (-0.58, -0.08, 1.245), (-0.33, -0.08, 1.233), (-0.33, -0.04, 1.233), 100),
    ("ECU_Tubes",  73, 108, (-0.44, -0.24, 1.680), (-0.42, -0.14, 1.660), (-0.18, -0.03, 1.585), (-0.18, 0.01, 1.575), 85),
    ("ECU_Visor", 109, 144, HC + V((-0.20, -0.50, 0.03)), HC + V((-0.16, -0.42, 0.02)), HC + V((0.06, -0.19, -0.01)), HC + V((0.06, -0.19, -0.01)), 85),
    ("ECU_Chin",  145, 180, HC + V((-0.26, -0.50, -0.12)), HC + V((-0.22, -0.44, -0.14)), HC + V((0.00, -0.21, -0.17)), HC + V((0.00, -0.21, -0.17)), 100),
    ("ECU_Emblem",181, 216, HC + V((-0.18, -0.50, 0.26)), HC + V((-0.12, -0.46, 0.24)), HC + V((0.03, -0.16, 0.16)), HC + V((0.04, -0.16, 0.16)), 100),
]
for name, f0, f1, c0, c1, t0, t1, lens in SH: shot(name, f0, f1, c0, c1, t0, t1, lens)

# --- reveal: starts tight on the visor, fast pull-out with an EXPO ease-out to the approved hero frame (lands f245), slow creep after
a_end = math.atan2(-1.62, -0.86); r_end = math.hypot(0.86, 1.62)
piv = bpy.data.objects.new("EMPTY_Orbit", None); S.collection.objects.link(piv); piv.location = HC
tH = bpy.data.objects.new("EMPTY_CamTarget_Hero", None); S.collection.objects.link(tH)
cH = bpy.data.objects.new("CAM_Reveal", bpy.data.cameras.new("CAM_Reveal")); S.collection.objects.link(cH); cH.parent = piv; cH.data.lens = 50
tr = cH.constraints.new('TRACK_TO'); tr.target = tH; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
cH.data.dof.use_dof = True; cH.data.dof.aperture_fstop = 4.0; cH.data.dof.focus_object = tH
kf(piv, "rotation_euler", 217, a_end - math.radians(25), 'EXPO', 'EASE_OUT', 2); kf(piv, "rotation_euler", 245, a_end, 'EXPO', 'EASE_OUT', 2)
kf(piv, "rotation_euler", 360, a_end + math.radians(3), 'LINEAR', 'AUTO', 2)
kf(cH, "location", 217, V((0.42, 0, 0.0)), 'EXPO', 'EASE_OUT'); kf(cH, "location", 245, V((r_end, 0, -0.10)), 'EXPO', 'EASE_OUT')
kf(cH, "location", 360, V((r_end * 0.95, 0, -0.10)), 'LINEAR')
kf(tH, "location", 217, HC + V((0.04, -0.12, 0.0)), 'EXPO', 'EASE_OUT'); kf(tH, "location", 245, HC + V((0, 0, -0.04)), 'EXPO', 'EASE_OUT')
kf(cH.data, "shift_x", 217, 0.0, 'EXPO', 'EASE_OUT'); kf(cH.data, "shift_x", 245, -0.06, 'EXPO', 'EASE_OUT')
m = S.timeline_markers.new("CAM_Reveal", frame=217); m.camera = cH
S.camera = bpy.data.objects["CAM_ECU_Seam"]

# --- power-on: helmet HUD/seams flicker on during the visor close-up (f112-128); dark before
helm = bpy.data.objects["SM_Helmet"]; nt = helm.data.materials[0].node_tree; bs = nt.nodes["Principled BSDF"]
src = bs.inputs["Emission Strength"].links[0].from_socket
pw = nt.nodes.new("ShaderNodeValue"); pw.name = "POWER"; mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
nt.links.new(src, mul.inputs[0]); nt.links.new(pw.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], bs.inputs["Emission Strength"])
for f, v in ((1, 0.0), (112, 0.0), (114, 0.7), (115, 0.05), (118, 0.9), (119, 0.15), (122, 1.0), (124, 0.35), (127, 1.0)):
    pw.outputs[0].default_value = v; pw.outputs[0].keyframe_insert("default_value", frame=f)
for fc in nt.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
# the tubes shot gets its own glint: a glossy-only strip sweeping across (f75-105); a second sweep on the reveal (f246-280)
sw = bpy.data.objects.new("LGT_Sweep", bpy.data.lights.new("LGT_Sweep", 'AREA')); S.collection.objects.link(sw)
sw.data.shape = 'RECTANGLE'; sw.data.size = 0.06; sw.data.size_y = 2.0; sw.visible_diffuse = False
try: sw.light_linking.receiver_collection = bpy.data.collections["COL_Product"]
except (AttributeError, KeyError): pass
for f, e, p in ((74, 0, (-0.9, 1.0, 1.9)), (75, 300, (-0.9, 1.0, 1.9)), (105, 300, (0.9, 1.0, 1.9)), (106, 0, (0.9, 1.0, 1.9)),
                (245, 0, (-1.6, -1.6, 2.2)), (246, 450, (-1.6, -1.6, 2.2)), (280, 450, (1.2, -1.6, 2.2)), (281, 0, (1.2, -1.6, 2.2))):
    sw.data.energy = e; sw.data.keyframe_insert("energy", frame=f)
    sw.location = p; sw.keyframe_insert("location", frame=f)
    sw.rotation_euler = (HC - V(p)).to_track_quat('-Z', 'Y').to_euler(); sw.keyframe_insert("rotation_euler", frame=f)
for fc in sw.data.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
if out:
    bpy.ops.wm.save_as_mainfile(filepath=out); print("ANIM2 SAVED", out)
