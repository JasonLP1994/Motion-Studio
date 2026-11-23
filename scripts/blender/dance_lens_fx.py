# Focal-length play on the dance cameras (run after cams.py):
#   A dolly zoom (60 -> 18 mm while the camera moves in, subject size held) | B snap zooms on the beat (35 <-> 85 mm)
#   C slow zoom 24 -> 40 mm | D ultra-wide 12 mm | E crash zoom 35 -> 90 mm in the last 10 frames | F 135 mm + focus pull
#   blender -b IN.blend -P work/dance/lens_fx.py -- OUT.blend
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene; rig = bpy.data.objects["rig"]
BEAT = 12   # 120 BPM at 24 fps
def ease(t): return t * t * (3 - 2 * t)
def keylens(cam, f, mm):
    cam.data.lens = mm; cam.data.keyframe_insert("lens", frame=f)
def hip(f): S.frame_set(f); return rig.matrix_world @ rig.pose.bones["root.x"].head
def head(f): S.frame_set(f); return rig.matrix_world @ rig.pose.bones["head.x"].head
def cam(n): return bpy.data.objects[n]
# A: dolly zoom. Re-key the camera distance from 4.2 m to 1.25 m and the lens proportionally (subject size held)
A = cam("CAM_A_FloorWide"); A.animation_data_clear(); A.data.animation_data_clear()
for f in range(1, 61):
    t = ease((f - 1) / 59); h = hip(f); d = 4.2 - 2.95 * t; ang = math.radians(-60 + 18 * (f - 1) / 59)
    A.location = Vector((h.x, h.y, 0)) + Vector((math.cos(ang) * d, math.sin(ang) * d, 0.22)); tgt = Vector((h.x, h.y, 0.75))
    A.rotation_euler = (tgt - A.location).to_track_quat('-Z', 'Y').to_euler()
    A.keyframe_insert("location", frame=f); A.keyframe_insert("rotation_euler", frame=f)
    keylens(A, f, 60.0 * d / 4.2 * (18 / (60 * 1.25 / 4.2)) ** t if False else 60.0 * (d / 4.2))
    A.data.dof.focus_distance = (tgt - A.location).length; A.data.keyframe_insert("dof.focus_distance", frame=f)
# B: snap zooms on each beat (2-frame snap in, ease back out)
B = cam("CAM_B_Feet")
for f in range(61, 97):
    k = (f - 61) % BEAT
    mm = 85 if k < 2 else 85 - (85 - 35) * ease(min(1, (k - 2) / 6))
    keylens(B, f, mm)
# C: slow push of the lens
C = cam("CAM_C_Overhead")
for f in range(97, 177): keylens(C, f, 24 + 16 * ease((f - 97) / 79))
# D: ultra-wide, pulled a little closer so he stays big
D = cam("CAM_D_WormsEye")
for f in range(177, 273): keylens(D, f, 12)
# E: crash zoom in the last 10 frames of the orbit
E = cam("CAM_E_Orbit")
for f in range(273, 337):
    t = max(0.0, (f - 326) / 10); keylens(E, f, 35 + 55 * (t ** 2.2))
# F: long lens compression from further back + focus pull hood edge -> eyes
F = cam("CAM_F_FacePush"); F.animation_data_clear(); F.data.animation_data_clear()
for f in range(337, 369):
    t = ease((f - 337) / 31); hd = head(f); off = Vector((0.15, -1, -0.2)).normalized(); d = 3.6 - 0.6 * t
    F.location = hd + off * d; F.rotation_euler = (hd - F.location).to_track_quat('-Z', 'Y').to_euler()
    F.keyframe_insert("location", frame=f); F.keyframe_insert("rotation_euler", frame=f); keylens(F, f, 135)
    F.data.dof.aperture_fstop = 2.0; F.data.dof.focus_distance = (d - 0.18) + 0.18 * min(1, t * 1.6)
    F.data.keyframe_insert("dof.focus_distance", frame=f)
for c in [o for o in bpy.data.objects if o.name.startswith("CAM_")]:
    for ad in (c.animation_data, c.data.animation_data):
        if ad and ad.action:
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("LENS SAVED")
