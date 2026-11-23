# Clean straight-down render of the assembled pendant (no chain, transparent background) used to build the two-tone Rubyred logo.
# Usage: blender -b <scene.blend> -P scripts/blender/ruby_logo_source.py -- <out.png> [frame] [stone]   (stone: only the centre stone's shape)
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]; S = bpy.context.scene
S.frame_set(int(a[1]) if len(a) > 1 else 280)
for m in list(S.timeline_markers): S.timeline_markers.remove(m)      # markers would switch back to the film's cameras
for o in bpy.data.objects:
    if o.name.startswith(("Chain", "Floor")): o.hide_render = True
    if o.name.startswith("Chain"): o.animation_data_clear()             # keyed hide_render would bring the chain back
if len(a) > 2 and a[2] == "stone":     # mask of the centre stone only (white, flat) -> clean stone shape in the logo
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name != "CENTRE": o.hide_render = True
    m = bpy.data.materials.new("FLAT"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); o_ = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o_.inputs[0])
    bpy.data.objects["CENTRE"].data.materials.clear(); bpy.data.objects["CENTRE"].data.materials.append(m)
cd = bpy.data.cameras.new("LOGO"); cd.type = "ORTHO"; cd.ortho_scale = 3.3
cam = bpy.data.objects.new("LOGO", cd); S.collection.objects.link(cam); cam.location = (0, 0.25, 20); cam.rotation_euler = (0, 0, 0)
S.camera = cam
S.render.film_transparent = True; S.render.resolution_x, S.render.resolution_y = 1000, 1300; S.render.resolution_percentage = 100
S.cycles.samples = 48; S.render.use_motion_blur = False
S.render.filepath = os.path.abspath(a[0]); bpy.ops.render.render(write_still=True); print("logo source", a[0])
