# fast solid-shaded motion check: fixed 3/4 camera that follows the hips (smoothed), floor visible
import bpy, sys
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; S = bpy.context.scene; rig = bpy.data.objects["rig"]
S.render.engine = 'BLENDER_WORKBENCH'; S.display.shading.light = 'STUDIO'; S.display.shading.color_type = 'MATERIAL'
S.display.shading.show_shadows = True; S.display.shading.show_cavity = True
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 960, 540, 100; S.render.film_transparent = False
for o in bpy.data.objects:
    if o.name.startswith(('WGT', 'cs_', 'bone_shape', 'facial_landmarks', 'Plane.001')): o.hide_render = True
bpy.ops.mesh.primitive_plane_add(size=30); fl = bpy.context.active_object
m = bpy.data.materials.new("chk"); m.diffuse_color = (0.35, 0.37, 0.42, 1); fl.data.materials.append(m)
cam = S.camera; cam.animation_data_clear(); cam.data.animation_data_clear(); cam.data.lens = 28
hips = []
for f in range(1, S.frame_end + 1): S.frame_set(f); hips.append(rig.matrix_world @ rig.pose.bones["root.x"].head)
import os; os.makedirs(a[0], exist_ok=True)
for i in range(S.frame_end):
    w = hips[max(0, i - 15):i + 16]; c = sum(w, Vector()) / len(w); c.z = 0.7
    S.frame_set(i + 1); cam.location = c + Vector((2.4, -3.3, 0.7)); cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    S.render.filepath = f"{a[0]}/f_{i + 1:04d}.png"; bpy.ops.render.render(write_still=True)
