# Pixel-art sneaker sprites: renders the free "Sci-fi Sneaker" (erdemdagdelen, CC-BY 4.0, via Objaverse) as tiny ID-coded
# frames: each part's colour ROLE goes in the red channel, a 3-step toon shade in green, and an inverted-hull outline is pure
# black. scripts/pixel_palette.py then repaints every pixel into a chosen palette (exact palette colours, no anti-aliasing),
# and Remotion scales the sprites up with hard square pixels.
# Run: PYTHONPATH=tools/py312 blender -b --factory-startup -P work/pixel/sneaker_sprite.py -- OUT_DIR ANGLES W H [TILT] [ROLL]
import bpy, sys, math, os
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT, N, W, H = args[0], int(args[1]), int(args[2]), int(args[3]); TILT = float(args[4]) if len(args) > 4 else 12.0
ROLL = float(args[5]) if len(args) > 5 else 0.0   # camera roll in degrees: tilts the shoe in frame (toe down) without leaving the pixel grid
GLB = "/home/user/Motion-Studio/work/shoes/31032bcf56a44166afbb4e73ee3d7051.glb"
ROLES = {  # material name -> colour role (0 is reserved for the outline)
    "Sock": 1, "SockAdditions": 2, "Curve": 3, "Sockbottom": 4, "Traces": 5,
    "Laces": 6, "Laceadditions": 6, "Neck": 7, "Neckaddition": 7, "NeckCylinders": 7, "Tail": 7,
    "Tongue": 2, "FokurLogo": 8, "SockBrand": 8,
}
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
ms = [o for o in S.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]; bpy.ops.object.join(); shoe = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(S.objects):
    if o != shoe: bpy.data.objects.remove(o)
# normalise: length 1 along Y, centred, sole at z=0
import numpy as np
co = np.empty(len(shoe.data.vertices) * 3); shoe.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
lo, hi = co.min(0), co.max(0); sc = 1.0 / (hi[1] - lo[1])
co = (co - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]) * sc
shoe.data.vertices.foreach_set("co", co.ravel()); shoe.data.update()
shoe.data.polygons.foreach_set("use_smooth", [True] * len(shoe.data.polygons))

def toon(name, role):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N_ = nt.nodes
    for n in list(N_):
        if n.type != 'OUTPUT_MATERIAL': N_.remove(n)
    dif = N_.new("ShaderNodeBsdfDiffuse"); s2r = N_.new("ShaderNodeShaderToRGB"); rp = N_.new("ShaderNodeValToRGB")
    rp.color_ramp.interpolation = 'CONSTANT'; e = rp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0, 0, 0, 1)          # shade 0 (shadow)
    e[1].position = 0.62; e[1].color = (1, 1, 1, 1)          # shade 2 (light)
    mid = e.new(0.22); mid.color = (0.5, 0.5, 0.5, 1)        # shade 1 (mid)
    cmb = N_.new("ShaderNodeCombineRGB"); cmb.inputs["R"].default_value = role / 10.0
    sep = N_.new("ShaderNodeSeparateRGB"); nt.links.new(rp.outputs["Color"], sep.inputs[0]); nt.links.new(sep.outputs["R"], cmb.inputs["G"])
    em = N_.new("ShaderNodeEmission"); nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs["Color"], rp.inputs["Fac"])
    nt.links.new(cmb.outputs[0], em.inputs["Color"]); nt.links.new(em.outputs[0], N_["Material Output"].inputs["Surface"])
    return m
for i, slot in enumerate(shoe.material_slots):
    base = slot.material.name.split(".")[0] if slot.material else ""
    slot.material = toon("ID_" + base, ROLES.get(base, 1))
# outline: inverted hull (solidify, flipped normals, back faces only) in pure black
ol = bpy.data.materials.new("ID_Outline"); ol.use_nodes = True; ol.use_backface_culling = True
olb = ol.node_tree.nodes["Principled BSDF"]; ol.node_tree.nodes.remove(olb)
oem = ol.node_tree.nodes.new("ShaderNodeEmission"); oem.inputs["Color"].default_value = (0, 0, 0, 1)
ol.node_tree.links.new(oem.outputs[0], ol.node_tree.nodes["Material Output"].inputs["Surface"])
shoe.data.materials.append(ol)
sol = shoe.modifiers.new("Outline", 'SOLIDIFY'); sol.thickness = 0.022; sol.offset = 1.0; sol.use_flip_normals = True
sol.material_offset = len(shoe.material_slots) - 1; sol.use_rim = False
for m in bpy.data.materials:
    if m.name.startswith("ID_") and m != ol: m.use_backface_culling = False

PIV = bpy.data.objects.new("PIV", None); S.collection.objects.link(PIV); shoe.parent = PIV
shoe.location = (0, 0, -0.25)
# light: one key from the upper front-left; no world light, so the 3 toon steps read cleanly
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN')); S.collection.objects.link(sun); sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
W_ = bpy.data.worlds.new("W"); S.world = W_; W_.use_nodes = True; W_.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); S.collection.objects.link(cam); S.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.32
cam.location = Vector((1.6, -1.6, 0.75)) ; cam.rotation_euler = (Vector((0, 0, 0.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
from mathutils import Matrix as _M
bpy.context.view_layer.update()   # matrix_world is stale until the depsgraph updates
cam.matrix_world = cam.matrix_world @ _M.Rotation(math.radians(ROLL), 4, 'Z')

S.render.engine = 'BLENDER_EEVEE'; S.eevee.taa_render_samples = 1; S.render.filter_size = 0.0
S.render.film_transparent = True; S.render.dither_intensity = 0.0
S.view_settings.view_transform = 'Standard'; S.view_settings.look = 'None'
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = W, H, 100
S.render.image_settings.file_format = 'PNG'; S.render.image_settings.color_mode = 'RGBA'; S.render.image_settings.color_depth = '8'
os.makedirs(OUT, exist_ok=True)
for k in range(N):
    PIV.rotation_euler = (math.radians(TILT), 0, 2 * math.pi * k / N)
    S.render.filepath = os.path.join(OUT, f"id_{k:03d}.png"); bpy.ops.render.render(write_still=True)
print("DONE", N)
