# Prepare a downloaded jewellery CAD model (glTF) for the ruby film: weld, split into loose parts, and sort the parts into
# CENTRE stone / PAVE stones / METAL, body vs bail (PAVE_BAIL / METAL_BAIL), and CHAIN, by shape and position, so each gets its own material and can explode apart.
# Model: "ChapelHills BluTourmPndt" by CADtrends (Sketchfab c091efb068624f228432cbfb7b21a0ec, CC-BY 4.0, via Objaverse).
# Usage: blender -b --factory-startup -P scripts/blender/ruby_model_prep.py -- <in.glb> <out.blend>
import bpy, bmesh, sys
from mathutils import Vector

IN, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.name == "Cube": bpy.data.objects.remove(o)
ms = [o for o in bpy.data.objects if o.type == "MESH"]
for o in bpy.context.scene.objects: o.select_set(o in ms)
bpy.context.view_layer.objects.active = ms[0]
bpy.ops.object.join(); J = bpy.context.object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new(); bm.from_mesh(J.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)          # split vertices make metal look faceted (checks.md)
bm.to_mesh(J.data); bm.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in bpy.data.objects if o.type == "MESH"]

def stats(o):
    b = bmesh.new(); b.from_mesh(o.data)
    vol = abs(b.calc_volume()); nv = len(b.verts)
    h = bmesh.new()
    for v in b.verts: h.verts.new(v.co)
    try: bmesh.ops.convex_hull(h, input=h.verts); hv = abs(h.calc_volume())
    except Exception: hv = 0
    bb = [Vector(c) for c in o.bound_box]; mn = Vector(map(min, zip(*bb))); mx = Vector(map(max, zip(*bb)))
    b.free(); h.free()
    return vol, hv, nv, (mn + mx) / 2, mx - mn

info = [(o, *stats(o)) for o in parts]
# stones: nearly convex (solid / hull > 0.9) and not tiny-thin
stones = [t for t in info if t[2] > 0 and t[1] / t[2] > 0.9 and min(t[5]) > 0.25]
centre = max(stones, key=lambda t: t[1]) if stones else None
zs = sorted(t[4].z for t in info)
# the pendant body's top: the highest stone; chain = metal parts clearly above it
top = max(t[4].z + t[5].z / 2 for t in stones) if stones else zs[len(zs) // 2]
BAIL_Y = -1.0   # model space (mm): body y > -1, bail y < -1, chain below -10 (measured, see notes/ruby/plan.md)
cols = {}
for n in ("CENTRE", "PAVE", "METAL", "PAVE_BAIL", "METAL_BAIL", "CHAIN"):
    c = bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c); cols[n] = c
for t in info:
    o = t[0]
    k = "CENTRE" if t is centre else "PAVE" if t in stones else ("CHAIN" if t[4].y < BAIL_Y - 8.0 and t[4].z > 17.5 else "METAL")
    if k in ("PAVE", "METAL") and t[4].y < BAIL_Y: k += "_BAIL"      # the bail hangs at -Y in the model's own space
    for c in o.users_collection: c.objects.unlink(o)
    cols[k].objects.link(o); o.name = k.lower()
for k, c in cols.items():
    print("GROUP", k, len(c.objects), "parts", sum(len(o.data.polygons) for o in c.objects), "faces")
if centre: print("CENTRE size", tuple(round(v, 2) for v in centre[5]), "at", tuple(round(v, 2) for v in centre[4]))
print("STONE top z", round(top, 2))
# join each group into one object (fast to render, easy to animate)
for k, c in cols.items():
    obs = list(c.objects)
    if not obs: continue
    for o in bpy.context.scene.objects: o.select_set(o in obs)
    bpy.context.view_layer.objects.active = obs[0]; bpy.ops.object.join(); bpy.context.object.name = k
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
