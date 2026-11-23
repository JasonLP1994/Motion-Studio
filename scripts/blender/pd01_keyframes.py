# render selected frames of the animation (camera from markers) at low quality for review
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]; S = bpy.context.scene
S.cycles.samples = int(a[1]); S.render.resolution_percentage = int(a[2])
for f in map(int, a[3].split(",")):
    S.frame_set(f)
    cam = None
    for m in sorted(S.timeline_markers, key=lambda m: m.frame):
        if m.frame <= f: cam = m.camera
    S.camera = cam; S.render.filepath = os.path.join(a[0], f"k_{f:04d}.png"); bpy.ops.render.render(write_still=True)
