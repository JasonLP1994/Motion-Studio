"""Render a quick 3-angle check sheet of a 3D model (GLB/OBJ) in Blender Cycles, colours from vertex colours.
Usage: blender -b --factory-startup -P scripts/ai/preview_3d.py -- <model.glb> <out.png> [samples]
"""
import bpy, sys, math, mathutils, os
a = sys.argv[sys.argv.index("--") + 1:]
src, out = a[0], a[1]; spp = int(a[2]) if len(a) > 2 else 32
bpy.ops.wm.read_factory_settings(use_empty=True)
if src.lower().endswith(".obj"):
    bpy.ops.wm.obj_import(filepath=src)
else:
    bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
# colour from vertex colours
mat = bpy.data.materials.new("VCOL"); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
ca = nt.nodes.new("ShaderNodeVertexColor")
nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.6
for o in objs:
    if o.data.color_attributes:
        ca.layer_name = o.data.color_attributes[0].name
    o.data.materials.clear(); o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
# frame the model
pts = [o.matrix_world @ mathutils.Vector(c) for o in objs for c in o.bound_box]
lo = mathutils.Vector([min(p[i] for p in pts) for i in range(3)]); hi = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
ctr = (lo + hi) / 2; size = max(hi - lo)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = spp; sc.cycles.device = "CPU"; sc.cycles.use_denoising = False
sc.render.resolution_x = sc.render.resolution_y = 512
sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.82, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
key = bpy.data.objects.new("Key", bpy.data.lights.new("Key", "AREA")); key.data.energy = 300 * size * size; key.data.size = size
key.location = ctr + mathutils.Vector((size * 1.5, -size * 1.5, size * 2)); sc.collection.objects.link(key)
key.rotation_euler = (ctr - key.location).to_track_quat("-Z", "Y").to_euler()
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); cam.data.lens = 50; sc.collection.objects.link(cam); sc.camera = cam
tiles = []
base, ext = os.path.splitext(out)
for i, ang in enumerate((-30, 60, 150)):
    r = size * 2.4; t = math.radians(ang)
    cam.location = ctr + mathutils.Vector((math.sin(t) * r, -math.cos(t) * r, size * 0.8))
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{base}_{i}{ext}"; bpy.ops.render.render(write_still=True); tiles.append(sc.render.filepath)
print("TILES", " ".join(tiles))
