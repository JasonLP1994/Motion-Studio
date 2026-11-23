# Rebuild only the cameras (and the moving glisten lights) of an already-built (and rigid-body-baked) ruby scene from CFG["cams"] in ruby_pendant.py,
# so camera changes don't need a full rebuild + re-bake. Optional: render low-res check frames.
# Usage: blender -b <in.blend> -P scripts/blender/ruby_recam.py -- <out.blend> [frames,comma,list out_dir pct spp]
import bpy, ast, os, sys
from mathutils import Vector
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ruby_pendant.py")
tree = ast.parse(open(SRC).read())
CFG = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CFG")
args = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene
for m in list(S.timeline_markers):
    if m.name.startswith("cut_"): S.timeline_markers.remove(m)
for c in CFG["cams"]:
    for n in (c[0], f"T_{c[0]}"):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    if bpy.data.cameras.get(c[0]): bpy.data.cameras.remove(bpy.data.cameras[c[0]])
def keyv(o, path, fv, interp="BEZIER", easing="AUTO"):
    for f, v in fv: setattr(o, path, v); o.keyframe_insert(path, frame=f)
    for fc in o.animation_data.action.fcurves:
        if fc.data_path == path:
            for kp in fc.keyframe_points: kp.interpolation = interp; kp.easing = easing
SET = bpy.data.collections["SET"]; PROD = bpy.data.collections["PRODUCT"]
for name, f0, (p0, p1), (t0, t1), lens, fstop, interp in CFG["cams"]:
    nxt = [c[1] for c in CFG["cams"] if c[1] > f0]; f1 = (min(nxt) - 1) if nxt else CFG["frames"]
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_start = 0.05; cd.clip_end = 2000
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(name, cd); SET.objects.link(cam)
    tgt = bpy.data.objects.new(f"T_{name}", None); PROD.objects.link(tgt)
    tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    cd.dof.focus_object = tgt
    keyv(cam, "location", [(f0, Vector(p0)), (f1, Vector(p1))], interp, "EASE_OUT")
    keyv(tgt, "location", [(f0, Vector(t0)), (f1, Vector(t1))], interp, "EASE_OUT")
    S.timeline_markers.new(f"cut_{name}", frame=f0).camera = cam
    if name == "MAC":
        keyv(tgt, "location", [(f0, Vector((0, -0.1, 0.7))), (f0 + 22, Vector(t0)), (f1, Vector(t1))], "BEZIER")
S.camera = bpy.data.objects["MAC"]
sys.path.insert(0, os.path.dirname(SRC)); import ruby_sweep; ruby_sweep.build(S, CFG); ruby_sweep.fix_gem_reflections(S, CFG); ruby_sweep.add_diamond_cards(S, CFG); ruby_sweep.add_slow_turns(S, CFG); ruby_sweep.white_studio(S, CFG); ruby_sweep.grade(S, CFG)   # moving glisten lights
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args[0]))
print("saved", args[0])
if len(args) >= 5:
    frames, out, pct, spp = [int(x) for x in args[1].split(",")], args[2], int(args[3]), int(args[4])
    os.makedirs(out, exist_ok=True)
    S.render.resolution_percentage = pct; S.cycles.samples = spp; S.cycles.use_denoising = False
    for f in frames:
        S.frame_set(f); S.render.filepath = os.path.abspath(f"{out}/c_{f:04d}.png"); bpy.ops.render.render(write_still=True)
        print("CHECK frame", f)
