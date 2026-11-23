# Dance camera shots (cut by timeline markers), each following the dancer's smoothed hips:
#   A  f1-60    floor-level 20 mm wide, low dolly-in            (footwork)
#   B  f61-96   50 mm close tracking the feet                    (footwork detail)
#   C  f97-176  straight overhead, slow rotation                 (handstand kicks)
#   D  f177-272 worm's eye: 16 mm on the floor looking up        (flips)
#   E  f273-336 3/4 orbit at chest height                        (helicopter)
#   F  f337-368 85 mm push-in on the face (glowing eyes)         (freeze)
#   blender -b IN.blend -P work/dance/cams.py -- OUT.blend
import bpy, sys, math
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene; rig = bpy.data.objects["rig"]
N = S.frame_end
hip, head, feet = {}, {}, {}
for f in range(1, N + 1):
    S.frame_set(f); P = lambda b: rig.matrix_world @ rig.pose.bones[b].head
    hip[f] = P("root.x"); head[f] = P("head.x"); feet[f] = (P("foot.l") + P("foot.r")) / 2
def smooth(d, f, r, lo, hi):
    w = [d[k] for k in range(max(lo, f - r), min(hi, f + r) + 1)]; return sum(w, Vector()) / len(w)
def ease(t): return t * t * (3 - 2 * t)
def make(name, lens, f0, f1, place):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); S.collection.objects.link(c); c.data.lens = lens; c.data.clip_start = 0.02
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 4.0
    for f in range(f0, f1 + 1):
        t = (f - f0) / max(1, f1 - f0)
        loc, tgt, roll = place(f, t)
        c.location = loc; q = (tgt - loc).to_track_quat('-Z', 'Y')
        c.rotation_euler = (q @ Matrix.Rotation(math.radians(roll), 4, 'Z').to_quaternion()).to_euler()
        c.data.dof.focus_distance = (tgt - loc).length
        c.keyframe_insert("location", frame=f); c.keyframe_insert("rotation_euler", frame=f); c.data.keyframe_insert("dof.focus_distance", frame=f)
    m = S.timeline_markers.new(name, frame=f0); m.camera = c
    return c
def A(f, t):
    h = smooth(hip, f, 10, 1, 60); d = 2.6 - 0.9 * ease(t); ang = math.radians(-60 + 18 * t)
    return h * Vector((1, 1, 0)) + Vector((math.cos(ang) * d, math.sin(ang) * d, 0.22)), Vector((h.x, h.y, 0.75)), 0
def B(f, t):
    p = smooth(feet, f, 3, 61, 96); ang = math.radians(-35 + 25 * t); z = max(0.1, p.z)
    return Vector((p.x + math.cos(ang) * 1.5, p.y + math.sin(ang) * 1.5, z * 0.6 + 0.15)), Vector((p.x, p.y, z)), -6
def C(f, t):
    h = smooth(hip, f, 12, 97, 176); ang = math.radians(20 + 70 * ease(t))
    loc = Vector((h.x + 0.01, h.y, 3.9 - 0.5 * t)); up = Matrix.Rotation(ang, 3, 'Z') @ Vector((0, 1, 0))
    return loc, Vector((h.x, h.y, 0.6)), 0
def D(f, t):
    h = smooth(hip, f, 8, 177, 272); ang = math.radians(-100 + 30 * t)
    return Vector((h.x + math.cos(ang) * 0.75, h.y + math.sin(ang) * 0.75, 0.06)), Vector((h.x, h.y, 0.95)), 8
def E(f, t):
    h = smooth(hip, f, 10, 273, 336); ang = math.radians(-120 + 75 * ease(t)); d = 2.4
    return Vector((h.x + math.cos(ang) * d, h.y + math.sin(ang) * d, 0.95)), Vector((h.x, h.y, max(0.35, h.z * 0.8))), 0
def F(f, t):
    hd = smooth(head, f, 6, 337, 368); h = smooth(hip, f, 6, 337, 368)
    dirv = (hd - h); dirv.z = 0
    side = dirv.normalized().cross(Vector((0, 0, 1))) if dirv.length > 1e-3 else Vector((1, 0, 0))
    d = 1.7 - 0.5 * ease(t); off = (Vector((0, -1, -0.25)) + side * 0.2).normalized()
    return hd + off * d, hd + Vector((0, 0, 0.02)), 0
make("CAM_A_FloorWide", 20, 1, 60, A)
make("CAM_B_Feet", 50, 61, 96, B)
cc = make("CAM_C_Overhead", 24, 97, 176, C)
# overhead roll: rotate the overhead camera about its view axis over the shot
for f in range(97, 177):
    t = (f - 97) / 79; S.frame_set(f)
    cc.rotation_euler = (Matrix.Rotation(math.radians(30 + 70 * ease(t)), 4, 'Z') @ cc.matrix_world.to_3x3().to_4x4()).to_euler() if False else cc.rotation_euler
    cc.rotation_euler.z = math.radians(30 + 70 * ease(t)); cc.rotation_euler.x = 0.0; cc.rotation_euler.y = 0.0
    cc.keyframe_insert("rotation_euler", frame=f)
make("CAM_D_WormsEye", 16, 177, 272, D)
make("CAM_E_Orbit", 35, 273, 336, E)
make("CAM_F_FacePush", 70, 337, 368, F)
for c in [o for o in bpy.data.objects if o.name.startswith("CAM_")]:
    if c.animation_data:
        for fc in c.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
S.camera = bpy.data.objects["CAM_A_FloorWide"]
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("CAMS SAVED", N)
