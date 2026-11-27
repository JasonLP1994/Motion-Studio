"""Prepare a GLB character for Mixamo auto-rigging: drop props/strays, stand it on the floor at the origin facing -Y,
apply transforms, join into one mesh, export FBX with embedded textures. Props are saved separately (same world
placement, same floor offset) so they can be pinned to the hand bone after the Mixamo download.
  blender -b -P scripts/blender/prep_mixamo.py -- <in.glb> <out.fbx> <props_out.glb> [--props Object_19,Object_20] [--drop Object_4]
"""
import bpy, sys, mathutils

a = sys.argv[sys.argv.index("--") + 1:]
src, out_fbx, out_props = a[:3]
opt = dict(zip(a[3::2], a[4::2]))
PROPS = opt.get("--props", "Object_19,Object_20").split(",")
DROP = opt.get("--drop", "Object_4").split(",")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for n in DROP:
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]

# floor offset from the body (not the props), centre X/Y on the body
body = [o for o in meshes if o.name not in PROPS]
pts = [o.matrix_world @ mathutils.Vector(c) for o in body for c in o.bound_box]
zmin = min(p.z for p in pts); cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2; cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
off = mathutils.Vector((-cx, -cy, -zmin))

# unparent everything with world transforms kept, then shift and apply
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in list(bpy.context.scene.objects):
    if o.type != "MESH": bpy.data.objects.remove(o, do_unlink=True)
for o in meshes:
    o.location += off
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# props -> their own GLB
bpy.ops.object.select_all(action="DESELECT")
props = [o for o in meshes if o.name in PROPS]
for o in props: o.select_set(True)
if props:
    bpy.ops.export_scene.gltf(filepath=out_props, use_selection=True, export_format="GLB")
    for o in props: bpy.data.objects.remove(o, do_unlink=True)

# body -> one mesh -> FBX
body = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in body: o.select_set(True)
bpy.context.view_layer.objects.active = body[0]
bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active; obj.name = "Samurai"
d = obj.dimensions
print(f"body: {len(obj.data.vertices)} verts, {len(obj.data.materials)} materials, size {d.x:.2f} x {d.y:.2f} x {d.z:.2f} m, floor offset {tuple(round(v, 4) for v in off)}")
bpy.ops.export_scene.fbx(filepath=out_fbx, use_selection=True, object_types={"MESH"}, apply_scale_options="FBX_SCALE_ALL",
                         path_mode="COPY", embed_textures=True, add_leaf_bones=False, bake_anim=False)
print("saved", out_fbx, "and", out_props)
