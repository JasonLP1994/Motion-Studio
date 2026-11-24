# relaxed b-boy hands: curl the ARP finger controls into loose fists (thumb tucked), keyed for the whole edit
#   blender -b IN.blend -P work/dance/hands.py -- OUT.blend [AXIS] [SIGN]
import bpy, sys, math
a = sys.argv[sys.argv.index("--") + 1:]; AX = a[1] if len(a) > 1 else 'X'; SG = float(a[2]) if len(a) > 2 else 1.0
S = bpy.context.scene; r = bpy.data.objects["rig"]; N = S.frame_end
CURL = {1: 55, 2: 75, 3: 55}; SPREAD = {"index": 1.0, "middle": 1.05, "ring": 1.1, "pinky": 1.15}
for sd in ("l", "r"):
    for fg, k in SPREAD.items():
        for j in (1, 2, 3):
            pb = r.pose.bones.get(f"c_{fg}{j}.{sd}")
            if not pb: continue
            pb.rotation_mode = 'XYZ'; e = [0.0, 0.0, 0.0]; e["XYZ".index(AX)] = SG * math.radians(CURL[j] * k)
            pb.rotation_euler = e
            for f in (1, N): pb.keyframe_insert("rotation_euler", frame=f)
    for j, ang in ((1, 15), (2, 30), (3, 30)):
        pb = r.pose.bones.get(f"c_thumb{j}.{sd}")
        if not pb: continue
        pb.rotation_mode = 'XYZ'; e = [0.0, 0.0, 0.0]; e[0] = math.radians(ang * 0.6); e[2] = math.radians(ang * (1 if sd == 'l' else -1)); pb.rotation_euler = e
        for f in (1, N): pb.keyframe_insert("rotation_euler", frame=f)
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("HANDS SAVED", AX, SG)
