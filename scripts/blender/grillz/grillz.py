# Grillz on the user's lips model (Tripo AI "lips.glb"): "PHILLIPS" upper / "MOTION" lower as gold-backed emerald-enamel letters
# bent to the teeth arch; mouth opened a little; warm low-key macro lighting after the user's reference
# (inputs/grillz/speaking-test.mp4). Font: Ultra (Apache 2.0).
#   PYTHONPATH=tools/py312 blender -b --factory-startup -P work/grillz/grillz.py -- save OUT.blend
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
E = lambda k, d: float(os.environ.get(k, d))
R = "/home/user/Motion-Studio/"
bpy.ops.wm.read_factory_settings(use_empty=True); S = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=R + "inputs/grillz/lips_zip/source/lips.glb"); bpy.context.view_layer.update()
for o in list(S.objects):
    if o.type == 'MESH' and o.name == "Cube": bpy.data.objects.remove(o)
lips = next(o for o in S.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = lips; lips.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
lips.select_set(False)
# ---- open the mouth: upper half up, lower half down, smooth band through the mouth (corners stretch like a real open mouth)
OPEN = E("OPEN", 0.0)
co = np.empty(len(lips.data.vertices) * 3); lips.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
z = co[:, 2] + 0.012                                              # mouth centre sits a touch below z=0
t = np.clip(z / 0.05, -1, 1); w = t * (1.5 - 0.5 * t * t)         # smooth -1..1 across the opening
co[:, 2] += OPEN * w
lips.data.vertices.foreach_set("co", co.ravel()); lips.data.update()
# ---- lips: natural deep red, wet gloss
lm = lips.data.materials[0]; nt = lm.node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
src = bs.inputs["Base Color"].links[0].from_socket
hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = E("LIP_SAT", 0.95); hs.inputs["Value"].default_value = E("LIP_VAL", 0.48)
hs.inputs["Hue"].default_value = E("LIP_HUE", 0.49)
nt.links.new(src, hs.inputs["Color"]); nt.links.new(hs.outputs["Color"], bs.inputs["Base Color"])
for l in list(bs.inputs["Roughness"].links): nt.links.remove(l)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90.0; nz.inputs["Detail"].default_value = 8.0
mr = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(nz.outputs["Fac"], mr.inputs[0]); mr.inputs[3].default_value = 0.22; mr.inputs[4].default_value = 0.5
nt.links.new(mr.outputs[0], bs.inputs["Roughness"])
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.002; nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
if not bs.inputs["Normal"].links: nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
bs.inputs["Coat Weight"].default_value = E("LIP_COAT", 0.55); bs.inputs["Coat Roughness"].default_value = 0.12
bs.inputs["Subsurface Weight"].default_value = 0.15; bs.inputs["Subsurface Radius"].default_value = (0.02, 0.006, 0.004)
# ---- materials for the grillz
def gold():
    m = bpy.data.materials.new("MAT_Gold"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 0.68, 0.28, 1); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = E("GOLD_ROUGH", 0.16)
    b.inputs["Anisotropic"].default_value = 0.3; return m
def emerald():
    m = bpy.data.materials.new("MAT_EmeraldEnamel"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.inputs["Scale"].default_value = 7.0
    wv.inputs["Distortion"].default_value = 5.0; wv.inputs["Detail"].default_value = 2.0; nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0.002, 0.06, 0.012, 1); e[1].position = 1.0; e[1].color = (0.06, 0.55, 0.12, 1)
    mid = e.new(0.55); mid.color = (0.012, 0.22, 0.04, 1)
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.1; b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Specular IOR Level"].default_value = 0.7
    return m
GOLD, EMER = gold(), emerald()
FONT = bpy.data.fonts.load(R + "work/grillz/font/" + os.environ.get("FONT", "Corben-Bold.ttf"))
def make_word(text, z_mid, x_teeth, arch_k, y_span, name, tilt=0.0, height=None):
    """chunky inflated grill letters: thick gold body (fatter outline, rounded bevel) + puffy emerald face proud of it,
    backs pressed onto the teeth surface (x_teeth - arch_k*y^2), bent round the arch and following its curvature"""
    objs = []
    for layer, offset, extr, bev, cx, mat in (("gold", E("RIM", 0.03), 0.16, 0.035, 0.0, GOLD), ("face", E("FACE_OFF", -0.022), 0.03, E("PUFF", 0.04), 0.16, EMER)):
        cd = bpy.data.curves.new(f"{name}_{layer}", 'FONT'); cd.body = text; cd.font = FONT; cd.size = 1.0; cd.align_x = 'CENTER'; cd.align_y = 'CENTER'
        cd.offset = offset; cd.extrude = extr; cd.bevel_depth = bev; cd.bevel_resolution = 5; cd.space_character = E("TRACK", 1.1)
        ob = bpy.data.objects.new(f"{name}_{layer}", cd); S.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob.select_set(False)
        ob = bpy.context.view_layer.objects.active
        v = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", v); v = v.reshape(-1, 3)
        objs.append((ob, v, cx, mat))
    # common scale from the gold layer width
    gv = objs[0][1]; sc = y_span / (gv[:, 0].max() - gv[:, 0].min()); back = gv[:, 2].min()
    sz = (height / (gv[:, 1].max() - gv[:, 1].min())) if height else sc; ymid = (gv[:, 1].max() + gv[:, 1].min()) / 2
    out = []
    for ob, v, cx, mat in objs:
        # text space: x = along the word, y = up, z = depth (+z toward the viewer). shift face forward, back of gold to 0
        w = v.copy(); w[:, 2] += cx - back; w[:, 1] -= ymid
        w[:, 0] *= sc; w[:, 2] *= sc; w[:, 1] *= sz
        yy = w[:, 0]; up = w[:, 1]; dep = w[:, 2]
        # arch: position along the curve and rotate the depth axis to the local normal (letters wrap round the teeth)
        xs = x_teeth - arch_k * yy ** 2; nx, ny = 1.0, 2 * arch_k * yy; nl = np.sqrt(nx * nx + ny * ny); nx, ny = nx / nl, ny / nl
        X = xs + dep * nx; Y = yy + dep * ny
        Z = z_mid + up + tilt * dep                       # slight lean (teeth lean outward at the tips)
        ob.data.vertices.foreach_set("co", np.stack([X, Y, Z], 1).ravel()); ob.data.update()
        ob.data.materials.append(mat); ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
        ob.modifiers.new("WN", 'WEIGHTED_NORMAL') if False else None
        out.append(ob)
    return out
# rows sized to the measured teeth (OPEN=0): upper teeth z +0.018..+0.089 (front x = 0.280 - 1.51 y^2, y +-0.22),
# lower teeth z -0.063..-0.105 (front x = 0.228 - 2.4 y^2, y +-0.19). Letters hang a touch past the tips and tuck under the lips.
up = make_word("PHILLIPS", E("UP_Z", 0.052), E("UP_X", 0.280), E("UP_K", 1.51), E("UP_W", 0.44), "GR_Upper", -0.3, E("UP_H", 0.092))
lo = make_word("MOTION", E("LO_Z", -0.072), E("LO_X", 0.229), E("LO_K", 2.4), E("LO_W", 0.39), "GR_Lower", 0.3, E("LO_H", 0.082))
# ---- lighting: warm low-key macro (reference: dark falloff, warm key from upper left, hot rim on the right edge, gold glints)
W = bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True; W.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
def light(name, loc, energy, col, size, look=(0.3, 0, 0), shape='RECTANGLE', sy=None, diffuse=True):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col; ld.shape = shape; ld.size = size; ld.size_y = sy or size
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); o.visible_diffuse = diffuse; return o
light("LGT_Key_Warm", (1.8, 1.0, 1.1), E("KEY", 120), (1.0, 0.78, 0.58), 1.0)
light("LGT_Rim_Orange", (0.2, -1.4, 0.3), E("RIM_E", 60), (1.0, 0.55, 0.25), 0.4)
light("LGT_Glint_Strip", (1.6, 0.4, 0.6), E("GLINT", 70), (1.0, 0.9, 0.75), 1.2, sy=0.05, diffuse=False)
light("LGT_Glint_Top", (1.4, -0.3, 1.2), E("GLINT2", 50), (1.0, 0.85, 0.65), 0.9, sy=0.04, diffuse=False)
light("LGT_Glint_Low", (1.5, 0.6, -0.8), E("GLINT3", 35), (1.0, 0.75, 0.5), 0.9, sy=0.04, diffuse=False)
light("LGT_Fill_Low", (2.0, -0.6, -0.6), E("FILL", 6), (1.0, 0.7, 0.55), 1.5)
# ---- camera: macro, straight on, slight from the left, shallow focus on the letters
cam = bpy.data.objects.new("CAM_Macro", bpy.data.cameras.new("CAM_Macro")); S.collection.objects.link(cam); S.camera = cam
cam.data.lens = E("LENS", 85); cam.data.sensor_width = 36
cam.location = (E("CAM_X", 1.75), E("CAM_Y", 0.3), E("CAM_Z", -0.02))
tgt = Vector((0.25, 0, -0.02)); cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = E("FSTOP", 4.0); cam.data.dof.focus_distance = (Vector((0.29, 0, 0)) - cam.location).length
S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'; S.cycles.samples = 48; S.cycles.use_adaptive_sampling = True; S.cycles.use_denoising = False
S.cycles.glossy_bounces = 6; S.cycles.transmission_bounces = 4; S.cycles.sample_clamp_indirect = 4.0
S.render.resolution_x, S.render.resolution_y = 1920, 1080
S.view_settings.view_transform = 'AgX'
try: S.view_settings.look = 'AgX - Punchy'
except TypeError: pass
S.view_settings.exposure = E("EXPO", 0.0)
if a and a[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=a[1]); print("GRILLZ SAVED")
