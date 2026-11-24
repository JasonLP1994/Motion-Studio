# Stage floor for the dance (user: "floating in a blue void"): glossy reflective deep-blue floor with contact shadows,
# a thin hot-pink neon ring set into it (the dance circle), the bright blue backdrop kept behind.
#   blender -b IN.blend -P work/dance/floor.py -- OUT.blend
import bpy, bmesh, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene
E = lambda k, d: float(os.environ.get(k, d))
PINK = (1.0, 0.0, 0.28)
# floor
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0.002)); fl = bpy.context.active_object; fl.name = "SM_StageFloor"
m = bpy.data.materials.new("MAT_StageFloor"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.004, 0.02, 0.22, 1); b.inputs["Roughness"].default_value = E("FLOOR_ROUGH", 0.14)
b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.05; b.inputs["Specular IOR Level"].default_value = 0.6
# subtle large-scale roughness variation so the reflections aren't a perfect mirror
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.8; nz.inputs["Detail"].default_value = 3
mr = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(nz.outputs["Fac"], mr.inputs[0])
mr.inputs[3].default_value = E("FLOOR_ROUGH", 0.14) * 0.6; mr.inputs[4].default_value = E("FLOOR_ROUGH", 0.14) * 1.6
nt.links.new(mr.outputs[0], b.inputs["Roughness"])
# fade the floor into the backdrop colour with distance (no hard horizon line)
tc = nt.nodes.new("ShaderNodeTexCoord"); vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = 'LENGTH'; nt.links.new(tc.outputs["Object"], vm.inputs[0])
fade = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(vm.outputs["Value"], fade.inputs[0]); fade.inputs[1].default_value = 4.0; fade.inputs[2].default_value = 12.0
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.02, 0.16, 1.0, 1); em.inputs["Strength"].default_value = 0.9
mx = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(fade.outputs[0], mx.inputs[0]); nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
out = nt.nodes["Material Output"]; nt.links.new(mx.outputs[0], out.inputs["Surface"])
fl.data.materials.append(m)
# neon dance circle
bpy.ops.mesh.primitive_torus_add(major_radius=E("RING_R", 2.2), minor_radius=0.012, major_segments=192, minor_segments=8, location=(0, 0, 0.012))
ring = bpy.context.active_object; ring.name = "SM_NeonRing"; ring.scale.z = 0.4
rm = bpy.data.materials.new("MAT_NeonRing"); rm.use_nodes = True; rn = rm.node_tree
for n in list(rn.nodes):
    if n.type != 'OUTPUT_MATERIAL': rn.nodes.remove(n)
re = rn.nodes.new("ShaderNodeEmission"); re.inputs["Color"].default_value = (*PINK, 1); re.inputs["Strength"].default_value = E("RING_GLOW", 12.0)
rn.links.new(re.outputs[0], rn.nodes["Material Output"].inputs["Surface"]); ring.data.materials.append(rm)
ring.visible_shadow = False
# the old cyc's floor glow washed out every contact shadow: keep its glow low (the new floor fades into blue on its own)
cyc = bpy.data.objects.get("Plane.002")
if cyc:
    cb = next(n for n in cyc.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); cb.inputs["Emission Strength"].default_value = E("CYC_GLOW", 0.6)
S.cycles.glossy_bounces = max(S.cycles.glossy_bounces, 4)
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("FLOOR SAVED")
# no light-panel squares in the glossy floor: lights stay lighting the dancer, but aren't seen in reflections
# (light linking: the floor is excluded from the character lights, so their panels don't appear in it; the vinyl keeps its shine)
cf = bpy.data.collections.new("COL_FloorExclude"); S.collection.children.link(cf); cf.objects.link(fl)
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.name.startswith(("LGT_Key", "LGT_Fill", "LGT_Rim", "LGT_Top", "LGT_Front")):
        o.light_linking.receiver_collection = cf
for co in cf.collection_objects: co.light_linking.link_state = 'EXCLUDE'

# replace the old cyc (its curve edge showed) with a world-coloured backdrop: the floor already fades into blue
if cyc: cyc.hide_render = True
W = S.world; bg = W.node_tree.nodes.get("Background")
if bg: bg.inputs["Color"].default_value = (0.02, 0.16, 1.0, 1); bg.inputs["Strength"].default_value = E("BG", 0.9)
# soft pink + blue reflection strips so the glossy floor still has shape in its reflections (glossy-only)
def strip(name, loc, col, e):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = 6.0; ld.size_y = 0.25; ld.energy = e; ld.color = col
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc; o.rotation_euler = (3.14159, 0, 0)
    o.visible_diffuse = False; return o
strip("LGT_FloorStrip_Pink", (0, 4.5, 3.0), (1.0, 0.05, 0.45), 300)
strip("LGT_FloorStrip_Blue", (0, -4.5, 3.0), (0.3, 0.5, 1.0), 200)
# contact shadow: a big soft overhead light that only lights the floor (light linking INCLUDE) and is invisible in reflections,
# so the dancer casts a soft shadow where he touches down, without the light-panel squares coming back
cs = bpy.data.collections.new("COL_FloorOnly"); S.collection.children.link(cs); cs.objects.link(fl)
ld = bpy.data.lights.new("LGT_ContactShadow", 'AREA'); ld.shape = 'DISK'; ld.size = E("SHADOW_SIZE", 1.4); ld.energy = E("SHADOW_E", 900); ld.color = (0.55, 0.65, 1.0)
lo = bpy.data.objects.new("LGT_ContactShadow", ld); S.collection.objects.link(lo); lo.location = (0, 0, 4.0)
lo.visible_glossy = False; lo.light_linking.receiver_collection = cs
for co in cs.collection_objects: co.light_linking.link_state = 'INCLUDE'
# follow the dancer's hips so the shadow pool stays under him
rig = bpy.data.objects["rig"]
for f in range(S.frame_start, S.frame_end + 1):
    S.frame_set(f); h = rig.matrix_world @ rig.pose.bones["root.x"].head
    lo.location = (h.x, h.y, 4.0); lo.keyframe_insert("location", frame=f)
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("FLOOR2 SAVED")
