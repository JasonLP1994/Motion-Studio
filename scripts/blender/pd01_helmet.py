# PD-01 cyberpunk helmet (brief: notes/briefs/cyber-pd01.md). Hero: "HelmetConcept" by foor1o (CC-BY 4.0, Objaverse).
# Recolour in the shader (textures untouched): black/grey -> glossy black + gunmetal, the orange panels -> hot pink.
# Electric-blue set, glossy product lighting (.claude/skills/lighting/references/product-lighting.md), Cycles + OIDN.
# Run: PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber/pd01.py -- save OUT.blend | still F F ...
import bpy, bmesh, math, os, sys
from mathutils import Vector
ROOT = "/home/user/Motion-Studio/work/cyber/"
OUT = os.environ.get("PD_OUT", ROOT + "frames/")
GLB = ROOT + "83bdd9464ea4497bb687259afc4d8ae8.glb"
FPS, NF, RES = 24, 312, (1280, 720)
BLUE = (0.02, 0.06, 1.0)        # electric blue page
PINK = (1.0, 0.03, 0.32)        # hot pink accents
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.fps = FPS; S.frame_start, S.frame_end = 1, NF
def key(o, path, fr, val): setattr(o, path, val); o.keyframe_insert(path, frame=fr)

# ---------------------------------------------------------------- helmet
bpy.ops.import_scene.gltf(filepath=GLB)
ms = [o for o in S.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]; bpy.ops.object.join(); H = bpy.context.view_layer.objects.active; H.name = "SM_Helmet"
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(S.objects):
    if o != H: bpy.data.objects.remove(o)
import numpy as np
co = np.empty(len(H.data.vertices) * 3); H.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
lo, hi = co.min(0), co.max(0); sc = 1.0 / (hi[2] - lo[2])
co = (co - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]) * sc; H.data.vertices.foreach_set("co", co.ravel()); H.data.update()
bpy.ops.object.select_all(action='DESELECT'); H.select_set(True); bpy.context.view_layer.objects.active = H
bm = bmesh.new(); bm.from_mesh(H.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(H.data); bm.free()
H.data.polygons.foreach_set("use_smooth", [True] * len(H.data.polygons))

def recolour(mat):
    nt = mat.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    base = next((l.from_node for l in b.inputs["Base Color"].links), None)
    if base is None: return
    for l in list(b.inputs["Emission Color"].links): L.remove(l)
    b.inputs["Emission Strength"].default_value = 0.0
    hsv = N.new("ShaderNodeSeparateHSV"); L.new(next(l.from_socket for l in b.inputs["Base Color"].links), hsv.inputs[0])
    def m(op, a, c=None, clamp=True):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    helmet_z = m('GREATER_THAN', sep.outputs["Z"], 0.4)                     # above the collar
    orange = m('MULTIPLY', m('MULTIPLY', m('GREATER_THAN', hsv.outputs["S"], 0.2), m('GREATER_THAN', hsv.outputs["V"], 0.05)), m('LESS_THAN', hsv.outputs["H"], 0.16))
    lightgrey = m('MULTIPLY', m('LESS_THAN', hsv.outputs["S"], 0.22), m('GREATER_THAN', hsv.outputs["V"], 0.42))
    pink_mask = m('MULTIPLY', lightgrey, helmet_z)                          # small light-grey plates on the helmet -> hot pink
    black = N.new("ShaderNodeRGB"); black.outputs[0].default_value = (0.012, 0.012, 0.016, 1)
    g = m('MULTIPLY', hsv.outputs["V"], m('ADD', 0.22, m('MULTIPLY', helmet_z, -0.16)))   # gunmetal: darker on the helmet, charcoal on the collar
    # even, glossy roughness on the helmet (the source map has worn-paint blotches); collar keeps its fabric roughness
    rl_ = next((l.from_socket for l in b.inputs["Roughness"].links), None)
    if rl_ is not None:
        rmix = N.new("ShaderNodeMix"); rmix.data_type = 'FLOAT'; L.new(helmet_z, rmix.inputs["Factor"]); L.new(rl_, rmix.inputs[2]); rmix.inputs[3].default_value = 0.2
        L.new(rmix.outputs[0], b.inputs["Roughness"])
    gm = N.new("ShaderNodeCombineRGB")
    for ch, mul in (("R", 1.0), ("G", 1.0), ("B", 1.15)): L.new(m('MULTIPLY', g, mul), gm.inputs[ch])
    mix1 = N.new("ShaderNodeMix"); mix1.data_type = 'RGBA'; L.new(m('MULTIPLY', orange, helmet_z), mix1.inputs["Factor"])
    L.new(gm.outputs[0], mix1.inputs[6]); L.new(black.outputs[0], mix1.inputs[7])
    mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; L.new(pink_mask, mix.inputs["Factor"])
    L.new(mix1.outputs[2], mix.inputs[6]); mix.inputs[7].default_value = (*PINK, 1)
    L.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Coat Weight"].default_value = 0.7; b.inputs["Coat Roughness"].default_value = 0.05
    L.new(mix.outputs[2], b.inputs["Emission Color"]); L.new(m('MULTIPLY', pink_mask, 0.8), b.inputs["Emission Strength"])
for mat in H.data.materials:
    if mat and mat.use_nodes: recolour(mat)

RIG = bpy.data.objects.new("HELMET_RIG", None); S.collection.objects.link(RIG); H.parent = RIG; RIG.location = (0, 0, 0)

# ---------------------------------------------------------------- set: flat electric-blue page (camera rays), dim studio for reflections
cove = None
# ---------------------------------------------------------------- product lighting rig (reflections first)
COL_P = bpy.data.collections.new("COL_Product"); S.collection.children.link(COL_P); COL_P.objects.link(H)
COL_BG = None
def link(o, col):
    try: o.light_linking.receiver_collection = col
    except AttributeError: pass
def light(name, loc, energy, sx, sy, col=(1, 1, 1), look=(0, 0, 0.5), kind='AREA'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = col
    if kind == 'AREA': ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
def card(name, loc, sx, sy, look=(0, 0, 0.5)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc); o = bpy.context.object; o.name = name; o.scale = (sx, sy, 1)
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new("MAT_" + name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0, 0, 0, 1); nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    o.data.materials.append(m); o.visible_camera = False; o.visible_shadow = False; return o
for o in (light("LGT_Key_Softbox", (-1.6, -2.4, 2.2), 260, 2.2, 1.0), light("LGT_Key_TopStrip", (-1.4, -2.2, 2.9), 160, 2.2, 0.14),
          light("LGT_Strip_Back_L", (-2.0, 1.2, 0.9), 520, 0.15, 2.6, (0.75, 0.85, 1.0)), light("LGT_Strip_Back_R", (1.4, 2.6, 1.0), 140, 0.12, 2.6, PINK), light("LGT_Strip_Side_White", (2.2, 0.9, 0.9), 320, 0.15, 2.6, (1.0, 1.0, 1.0)),
          light("LGT_Rim_Top", (0.3, 1.6, 2.4), 300, 1.4, 0.2, (0.85, 0.9, 1.0)), light("LGT_Fill", (2.2, -1.8, 0.6), 30, 2.0, 2.0)):
    link(o, COL_P)
S.objects["LGT_Fill"].visible_glossy = False
card("LGT_NegFill_Front", (0.8, -2.6, 0.2), 2.6, 1.2); card("LGT_NegFill_Side", (2.6, -0.6, 0.9), 1.4, 2.4)
W = bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True; wt = W.node_tree; WN = wt.nodes
bg_cam = WN["Background"]; bg_cam.inputs["Color"].default_value = (*BLUE, 1); bg_cam.inputs["Strength"].default_value = 1.0
bg_env = WN.new("ShaderNodeBackground"); bg_env.inputs["Color"].default_value = (0.01, 0.025, 0.16, 1); bg_env.inputs["Strength"].default_value = 0.7
lp = WN.new("ShaderNodeLightPath"); mixw = WN.new("ShaderNodeMixShader")
wt.links.new(lp.outputs["Is Camera Ray"], mixw.inputs["Fac"]); wt.links.new(bg_env.outputs[0], mixw.inputs[1]); wt.links.new(bg_cam.outputs[0], mixw.inputs[2])
wt.links.new(mixw.outputs[0], WN["World Output"].inputs["Surface"])

# ---------------------------------------------------------------- test cameras
def cam(name, lens, loc, tgt, fstop=None):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); S.collection.objects.link(c); c.data.lens = lens
    t = bpy.data.objects.new(name + "_T", None); S.collection.objects.link(t); t.location = tgt; c.location = loc
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    if fstop: c.data.dof.use_dof = True; c.data.dof.focus_object = t; c.data.dof.aperture_fstop = fstop
    return c
C1 = cam("CAM_Profile", 50, (2.05, -0.15, 0.7), (-0.18, 0.0, 0.58), 8.0)     # profile hero like the reference
C2 = cam("CAM_ThreeQ", 50, (1.5, -1.6, 0.85), (-0.1, 0.0, 0.58), 8.0)
C3 = cam("CAM_Macro", 85, (1.0, -0.7, 0.85), (0.35, -0.2, 0.7), 2.0)
S.camera = C1

S.render.engine = 'CYCLES'; cy = S.cycles; cy.device = 'CPU'; cy.samples = 48; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03
cy.use_denoising = False; cy.max_bounces = 8; cy.diffuse_bounces = 2; cy.glossy_bounces = 4; cy.transmission_bounces = 2
cy.sample_clamp_indirect = 3.0; cy.caustics_reflective = False; cy.caustics_refractive = False
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = *RES, 100
S.render.film_transparent = True   # exact electric blue + HUD are composited in Remotion
S.view_settings.view_transform = "AgX"
try: S.view_settings.look = "AgX - Medium High Contrast"
except TypeError: pass
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); gl = ct.nodes.new("CompositorNodeGlare"); co_ = ct.nodes.new("CompositorNodeComposite")
gl.glare_type = 'FOG_GLOW'; gl.threshold = 1.5; gl.mix = -0.4; gl.size = 7
ct.links.new(rl.outputs["Image"], gl.inputs["Image"]); ct.links.new(gl.outputs["Image"], co_.inputs["Image"])
os.makedirs(OUT, exist_ok=True)
if args and args[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=args[1]); print("SAVED")
elif args and args[0] == "cams":
    for c in (C1, C2, C3):
        S.camera = c; S.render.filepath = OUT + c.name + ".png"; bpy.ops.render.render(write_still=True)
print("DONE")
