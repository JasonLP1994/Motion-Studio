# PD-01 animation layer (run after pd01c.py builds the scene):
#   PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber3/pd01c.py -P work/cyber3/pd01_anim.py -- OUT.blend
# 13 s @ 24 fps = 312 frames. Shots switch by timeline markers:
#   1-36    CAM_MacroA  slow slide across the sleeve print (lights fade up)
#   37-72   CAM_MacroB  visor macro while the HUD flickers on (power-on)
#   73-312  CAM_Hero    orbit from behind the hood to the hero angle (EXPO ease-out, lands f168), slow creep during the HUD hold
# Light sweep: a glossy-only strip travels across the helmet f140-178.
import bpy, math, sys, os
from mathutils import Vector
S = bpy.context.scene; S.render.fps = 24; S.frame_start, S.frame_end = 1, 312
E = lambda k, d: float(os.environ.get(k, d))
out = sys.argv[sys.argv.index("--") + 1:][0] if "--" in sys.argv else None
helm = bpy.data.objects["SM_Helmet"]
from mathutils import Vector as _V
co = [helm.matrix_world @ v.co for v in helm.data.vertices]
HC = sum(co, _V()) / len(co)

def key_ease(obj_or_data, path, frame, value, interp='BEZIER', easing='AUTO', index=-1):
    setattr(obj_or_data, path, value) if index < 0 else getattr(obj_or_data, path).__setitem__(index, value)
    obj_or_data.keyframe_insert(path, frame=frame, index=index)
    ad = obj_or_data.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if int(kp.co.x) == frame: kp.interpolation = interp; kp.easing = easing
def new_cam(name, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); S.collection.objects.link(c); c.data.lens = lens
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = E("FSTOP", 2.8); return c
def track(cam, target):
    t = cam.constraints.new('TRACK_TO'); t.target = target; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'

# ---------------------------------------------------------------- macro A: sleeve print / quilting
tA = bpy.data.objects.new("EMPTY_CamTarget_MacroA", None); S.collection.objects.link(tA); tA.location = (-0.33, -0.05, 1.235)
cA = new_cam("CAM_MacroA", 85); track(cA, tA); cA.data.dof.focus_object = tA
key_ease(cA, "location", 1, Vector((-0.70, -0.30, 1.30)), 'LINEAR'); key_ease(cA, "location", 36, Vector((-0.70, -0.12, 1.27)), 'LINEAR')
key_ease(tA, "location", 1, Vector((-0.33, -0.10, 1.235)), 'LINEAR'); key_ease(tA, "location", 36, Vector((-0.33, -0.01, 1.235)), 'LINEAR')

# ---------------------------------------------------------------- macro B: visor HUD ring
tB = bpy.data.objects.new("EMPTY_CamTarget_MacroB", None); S.collection.objects.link(tB)
tB.location = HC + Vector((E("MB_TX", 0.06), E("MB_TY", -0.18), E("MB_TZ", -0.01)))
cB = new_cam("CAM_MacroB", 70); track(cB, tB); cB.data.dof.focus_object = tB
pB0 = HC + Vector((E("MB_X", -0.30), E("MB_Y", -0.75), E("MB_Z", 0.05))); pB1 = tB.location + (pB0 - tB.location) * 0.82
key_ease(cB, "location", 37, pB0, 'LINEAR'); key_ease(cB, "location", 72, pB1, 'LINEAR')

# ---------------------------------------------------------------- hero orbit: pivot at the helmet, camera on an arm
piv = bpy.data.objects.new("EMPTY_Orbit", None); S.collection.objects.link(piv); piv.location = HC
tH = bpy.data.objects.new("EMPTY_CamTarget_Hero", None); S.collection.objects.link(tH); tH.location = HC + Vector((0, 0, -0.04))
cH = new_cam("CAM_Hero", 50); cH.parent = piv; track(cH, tH); cH.data.dof.focus_object = tH; cH.data.dof.aperture_fstop = 5.6
a_end = math.atan2(-1.62, -0.86); a_start = a_end - math.radians(E("ORBIT_DEG", 115))
r_end = math.hypot(0.86, 1.62)
def arm(r, z): return Vector((r, 0, z))
cH.location = arm(r_end, -0.10)
key_ease(piv, "rotation_euler", 73, a_start, 'EXPO', 'EASE_OUT', index=2); key_ease(piv, "rotation_euler", 168, a_end, 'EXPO', 'EASE_OUT', index=2)
key_ease(piv, "rotation_euler", 312, a_end + math.radians(3), 'LINEAR', index=2)
key_ease(cH, "location", 73, arm(r_end * 1.45, 0.05), 'EXPO', 'EASE_OUT'); key_ease(cH, "location", 168, arm(r_end, -0.10), 'EXPO', 'EASE_OUT')
key_ease(cH, "location", 312, arm(r_end * 0.96, -0.10), 'LINEAR')
key_ease(cH.data, "shift_x", 73, 0.0, 'EXPO', 'EASE_OUT'); key_ease(cH.data, "shift_x", 168, -0.06, 'EXPO', 'EASE_OUT')
key_ease(cH.data, "shift_y", 73, 0.0, 'EXPO', 'EASE_OUT'); key_ease(cH.data, "shift_y", 168, 0.0, 'EXPO', 'EASE_OUT')

for f, c in ((1, cA), (37, cB), (73, cH)):
    m = S.timeline_markers.new(c.name, frame=f); m.camera = c
S.camera = cA

# ---------------------------------------------------------------- power-on: helmet emission flickers on f37-54
mat = helm.data.materials[0]; nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
src = bs.inputs["Emission Strength"].links[0].from_socket
pw = nt.nodes.new("ShaderNodeValue"); pw.name = "POWER"; mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
nt.links.new(src, mul.inputs[0]); nt.links.new(pw.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], bs.inputs["Emission Strength"])
dv = pw.outputs[0]
for f, v in ((1, 0.0), (40, 0.0), (42, 0.7), (43, 0.05), (46, 0.85), (47, 0.15), (50, 1.0), (52, 0.4), (54, 1.0)):
    dv.default_value = v; dv.keyframe_insert("default_value", frame=f)
for fc in nt.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------------------------------------------------------------- lights fade up in macro A (everything scaled by a ramp)
for o in S.objects:
    if o.type == 'LIGHT' and o.name.startswith("LGT_"):
        e = o.data.energy
        for f, k in ((1, 0.15), (30, 1.0)):
            o.data.energy = e * k; o.data.keyframe_insert("energy", frame=f)

# ---------------------------------------------------------------- light sweep across the helmet (glossy-only strip)
sw = bpy.data.objects.new("LGT_Sweep", bpy.data.lights.new("LGT_Sweep", 'AREA')); S.collection.objects.link(sw)
sw.data.shape = 'RECTANGLE'; sw.data.size = 0.08; sw.data.size_y = 2.5; sw.data.energy = 0.0; sw.visible_diffuse = False
col = bpy.data.collections.get("COL_Product")
try: sw.light_linking.receiver_collection = col
except AttributeError: pass
for f, e, x in ((139, 0, -1.6), (140, 520, -1.6), (178, 520, 1.2), (179, 0, 1.2)):
    sw.data.energy = e; sw.data.keyframe_insert("energy", frame=f)
    sw.location = HC + Vector((x, -1.4, 0.6)); sw.keyframe_insert("location", frame=f)
    sw.rotation_euler = (HC - sw.location).to_track_quat('-Z', 'Y').to_euler(); sw.keyframe_insert("rotation_euler", frame=f)
if out:
    bpy.ops.wm.save_as_mainfile(filepath=out); print("ANIM SAVED", out)
