# PD-01 v3 (fresh start): "Space Helmet" by bluoppVR + "Puffy Jacket" by Enith2478 (both CC-BY 4.0, via Objaverse).
# Helmet repainted from its own textures (white shell -> glossy black, yellow -> hot pink, grey -> gunmetal, teal visor ->
# dark glass, emissive HUD -> pink); puffer recoloured black nylon with a hot-pink lining (inside faces). Transparent Cycles
# render, composited over electric blue in Remotion. Product lighting rig, hero camera from the reference framing.
# Run: PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber3/pd01c.py -- save OUT.blend
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector
R = "/home/user/Motion-Studio/work/cyber3/"
HELM, COAT = R + "7b095c71ce844118bf5fc9af2f3accd0.glb", R + "938a6482de1e4b00859d26f3bcaf1d90.glb"
PINK = (0.9, 0.0, 0.12)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
E = lambda k, d: float(os.environ.get(k, d))
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.fps = 24
COL = bpy.data.collections.new("COL_Product"); S.collection.children.link(COL)

def import_one(path, name):
    before = set(S.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in S.objects if o not in before]; ms = [o for o in new if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.name = name
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in new:
        if o != ob and o.name in bpy.data.objects: bpy.data.objects.remove(o)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    COL.objects.link(ob); return ob
def V(ob):
    co = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", co); return co.reshape(-1, 3)
def setV(ob, co): ob.data.vertices.foreach_set("co", co.ravel()); ob.data.update()

# ---------------------------------------------------------------- puffer: metres (shoulders ~0.6 m), collar centred on the Z axis
coat = import_one(COAT, "SM_Puffer")
co = V(coat) * 0.1
top = co[:, 2].max(); ring = co[co[:, 2] > top - 0.03]
co -= [ring[:, 0].mean(), ring[:, 1].mean(), top - 1.50]          # collar top at z = 1.50
# arms: A-pose (~45 deg) -> hang closer to the body, rotate about the shoulder
SH_X, SH_Z, ARM = E("SH_X", 0.17), E("SH_Z", 1.36), math.radians(E("ARM_DEG", 22))
for side in (1, -1):
    ax = co[:, 0] * side; w = np.clip((ax - SH_X) / 0.12, 0, 1); w = w * w * (3 - 2 * w) * (co[:, 2] < SH_Z + 0.04)
    ang = -side * ARM * w; px, pz = co[:, 0] - side * SH_X, co[:, 2] - SH_Z
    co[:, 0] = np.where(w > 0, side * SH_X + px * np.cos(ang) - pz * np.sin(ang), co[:, 0])
    co[:, 2] = np.where(w > 0, SH_Z + px * np.sin(ang) + pz * np.cos(ang), co[:, 2])
# big funnel collar: flare the stand collar outward toward the top so it wraps the helmet base and shows its pink lining
t = np.clip((co[:, 2] - 1.34) / 0.16, 0, 1); t = t * t * (3 - 2 * t); k = 1.0 + E("COLLAR_FLARE", 0.75) * t
co[:, 0] *= k; co[:, 1] = co[:, 1] * k
co[:, 2] += 0.04 * t
setV(coat, co)
# quilted baffles: push the surface in along the normals at evenly spaced horizontal seams (real geometry, not just shading)
nrm = np.empty(len(coat.data.vertices) * 3); coat.data.vertices.foreach_get("normal", nrm); nrm = nrm.reshape(-1, 3)
PITCH, DEPTH = E("BAFFLE", 0.085), E("BAFFLE_D", 0.012)
f = np.abs(np.sin(np.pi * co[:, 2] / PITCH)) ** 0.45 - 1.0           # 0 on the puff, -1 at the seam
f *= (co[:, 2] < 1.40)                                               # leave the collar smooth
setV(coat, co + nrm * (f * DEPTH)[:, None])
coat.data.polygons.foreach_set("use_smooth", [True] * len(coat.data.polygons))
coat.modifiers.new("Sub", 'SUBSURF').levels = 1


# ---------------------------------------------------------------- hood (down): a puffy scoop lying on the upper back behind the helmet,
# opening up and forward, black shell outside / hot-pink lining inside (the reference's main colour moment behind the head)
NA_, NT_ = 96, 20
A = np.linspace(E("HOOD_OPEN", 1.25), 2 * np.pi - E("HOOD_OPEN", 1.25), NA_); T = np.linspace(0, 1, NT_)
verts_, faces_ = [], []
for t in T:
    for a_ in A:
        wb = (1 - math.cos(a_)) / 2                                   # 0 at the front opening, 1 at the back
        ztop = E("HOOD_SIDE_Z", 1.40) + E("HOOD_RISE", 0.24) * wb ** 1.3
        z = 1.32 + (ztop - 1.32) * t
        r = 0.168 + 0.02 * wb + 0.055 * wb * math.sin(math.pi * min(t, 0.9) / 0.9 * 0.85) + 0.02 * t
        r += 0.03 * max(0.0, (t - 0.8) / 0.2) ** 2                    # rim rolls outward so the lining shows
        r += 0.008 * math.sin(a_ * 5 + 1.3) * t * wb                   # soft folds
        verts_.append((r * math.sin(a_), -r * math.cos(a_) + 0.03 * wb, z))
for i in range(NT_ - 1):
    for j in range(NA_ - 1):
        faces_.append((i * NA_ + j, i * NA_ + j + 1, (i + 1) * NA_ + j + 1, (i + 1) * NA_ + j))
hm_ = bpy.data.meshes.new("hood"); hm_.from_pydata(verts_, [], faces_)
hd = bpy.data.objects.new("SM_Hood", hm_); COL.objects.link(hd)
hv = V(hd)
setV(hd, hv); hd.data.polygons.foreach_set("use_smooth", [True] * len(hd.data.polygons))
sd = hd.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = 0.035; sd.offset = -1.0; sd.use_rim = True; sd.material_offset = 1; sd.material_offset_rim = 1
hd.modifiers.new("Sub", 'SUBSURF').levels = 2

# ---------------------------------------------------------------- helmet: width 0.40 m, neck ring seated inside the collar
helm = import_one(HELM, "SM_Helmet")
co = V(helm); s = E("HELM_W", 0.46) / (co[:, 0].max() - co[:, 0].min()); co *= s
b = co[co[:, 2] < co[:, 2].min() + 0.25 * s]
co -= [b[:, 0].mean(), b[:, 1].mean() + E("HELM_DY", 0.0), co[:, 2].min() - (1.50 - E("HELM_SINK", 0.07))]
th = math.radians(E("HELM_PITCH", 12)); piv = np.array([0.0, 0.0, co[:, 2].min()])
q = co - piv; y_, z_ = q[:, 1].copy(), q[:, 2].copy(); q[:, 1] = y_ * math.cos(th) - z_ * math.sin(th); q[:, 2] = y_ * math.sin(th) + z_ * math.cos(th)
co = q + piv; co[:, 2] += (1.50 - E("HELM_SINK", 0.07)) - co[:, 2].min()
setV(helm, co)
HC = Vector(co.mean(0)); HZ0, HZ1 = co[:, 2].min(), co[:, 2].max()

# ---------------------------------------------------------------- materials
def mnode(nt, op, a, b_=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = True
    for i, v in enumerate((a, b_)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]
def mix(nt, fac, a, b_):
    x = nt.nodes.new("ShaderNodeMix"); x.data_type = 'RGBA'; nt.links.new(fac, x.inputs["Factor"])
    for sock, v in ((6, a), (7, b_)):
        if isinstance(v, tuple): x.inputs[sock].default_value = v
        else: nt.links.new(v, x.inputs[sock])
    return x.outputs[2]
def mixf(nt, fac, a, b_):
    x = nt.nodes.new("ShaderNodeMix"); x.data_type = 'FLOAT'; nt.links.new(fac, x.inputs["Factor"])
    for sock, v in ((2, a), (3, b_)):
        if isinstance(v, (int, float)): x.inputs[sock].default_value = v
        else: nt.links.new(v, x.inputs[sock])
    return x.outputs[0]
def band(nt, x, lo, hi, soft=0.03):      # smooth 0..1 inside [lo, hi]
    a = nt.nodes.new("ShaderNodeMapRange"); a.interpolation_type = 'SMOOTHSTEP'; nt.links.new(x, a.inputs[0])
    a.inputs[1].default_value, a.inputs[2].default_value = lo - soft, lo + soft
    c = nt.nodes.new("ShaderNodeMapRange"); c.interpolation_type = 'SMOOTHSTEP'; nt.links.new(x, c.inputs[0])
    c.inputs[1].default_value, c.inputs[2].default_value = hi + soft, hi - soft
    return mnode(nt, 'MULTIPLY', a.outputs[0], c.outputs[0])

hm = helm.data.materials[0]; nt = hm.node_tree; bs = nt.nodes["Principled BSDF"]
alb = bs.inputs["Base Color"].links[0].from_socket; emi = bs.inputs["Emission Color"].links[0].from_socket
hsv = nt.nodes.new("ShaderNodeSeparateHSV"); nt.links.new(alb, hsv.inputs[0]); H_, S_, V_ = hsv.outputs["H"], hsv.outputs["S"], hsv.outputs["V"]
yellow = mnode(nt, 'MULTIPLY', mnode(nt, 'MULTIPLY', band(nt, H_, 0.09, 0.19), mnode(nt, 'GREATER_THAN', S_, 0.35)), mnode(nt, 'GREATER_THAN', V_, 0.38))
teal = mnode(nt, 'MULTIPLY', mnode(nt, 'MULTIPLY', band(nt, H_, 0.42, 0.62), mnode(nt, 'GREATER_THAN', S_, 0.12)), mnode(nt, 'SUBTRACT', 1.0, yellow))
grey = mnode(nt, 'MULTIPLY', band(nt, V_, 0.16, 0.36), mnode(nt, 'LESS_THAN', S_, 0.18))
shell_black = (0.006, 0.006, 0.008, 1); gun = (0.035, 0.036, 0.042, 1); glass = (0.002, 0.002, 0.003, 1)
col = shell_black
col = mix(nt, grey, col, gun)
col = mix(nt, teal, col, glass)
col = mix(nt, yellow, col, (*PINK, 1))
nt.links.new(col, bs.inputs["Base Color"])
# emissive HUD bits -> hot pink glow (brightness from the original emission map)
ebw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(emi, ebw.inputs[0])
nt.links.new(mix(nt, mnode(nt, 'GREATER_THAN', yellow, 0.5), (*PINK, 1), (*PINK, 1)), bs.inputs["Emission Color"])
nt.links.new(mnode(nt, 'ADD', mnode(nt, 'MULTIPLY', ebw.outputs[0], 6.0), mnode(nt, 'MULTIPLY', yellow, 0.25)), bs.inputs["Emission Strength"])
for k in ("Metallic", "Roughness"):
    for l in list(bs.inputs[k].links): nt.links.remove(l)
bs.inputs["Metallic"].default_value = 0.0
nt.links.new(mixf(nt, teal, mixf(nt, grey, 0.24, 0.38), 0.03), bs.inputs["Roughness"])
bs.inputs["Coat Weight"].default_value = 0.6; bs.inputs["Coat Roughness"].default_value = 0.12
nm_ = bs.inputs["Normal"].links[0].from_node; nm_.inputs["Strength"].default_value = 0.4

# puffer: black nylon outside, hot-pink lining where we see the inside (collar)
pm = bpy.data.materials.new("MAT_PufferNylon"); pm.use_nodes = True; pn = pm.node_tree; pb = pn.nodes["Principled BSDF"]
geo = pn.nodes.new("ShaderNodeNewGeometry")
sep = pn.nodes.new("ShaderNodeSeparateXYZ"); pn.links.new(geo.outputs["Position"], sep.inputs[0])
lining = mnode(pn, 'MULTIPLY', geo.outputs["Backfacing"], mnode(pn, 'GREATER_THAN', sep.outputs["Z"], 1.28))
pn.links.new(mix(pn, lining, (0.0025, 0.003, 0.006, 1), (*PINK, 1)), pb.inputs["Base Color"])
pn.links.new(mixf(pn, lining, 0.62, 0.55), pb.inputs["Roughness"])
zq = mnode(pn, 'MULTIPLY', sep.outputs["Z"], 2 * math.pi / 0.085)
sn = pn.nodes.new("ShaderNodeMath"); sn.operation = 'SINE'; pn.links.new(zq, sn.inputs[0])
ab = pn.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'; pn.links.new(sn.outputs[0], ab.inputs[0])
pw = pn.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pn.links.new(ab.outputs[0], pw.inputs[0]); pw.inputs[1].default_value = 0.35
nz = pn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14.0; nz.inputs["Detail"].default_value = 3.0
hgt = mnode(pn, 'ADD', pw.outputs[0], mnode(pn, 'MULTIPLY', nz.outputs["Fac"], 0.25))
bp = pn.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.2; bp.inputs["Distance"].default_value = 0.012
pn.links.new(hgt, bp.inputs["Height"]); pn.links.new(bp.outputs["Normal"], pb.inputs["Normal"])
pb.inputs["Specular IOR Level"].default_value = 0.12
pb.inputs["Emission Color"].default_value = (*PINK, 1); pn.links.new(mixf(pn, lining, 0.0, 0.12), pb.inputs["Emission Strength"])
coat.data.materials.clear(); coat.data.materials.append(pm)
hmat = pm.copy(); hmat.name = "MAT_HoodNylon"
for n in hmat.node_tree.nodes:
    if n.type == 'MATH' and n.operation == 'GREATER_THAN' and abs(n.inputs[1].default_value - 1.28) < 1e-6: n.inputs[1].default_value = -10.0
hd.data.materials.append(hmat)
lin = bpy.data.materials.new("MAT_PinkLining"); lin.use_nodes = True; lb = lin.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = (*PINK, 1); lb.inputs["Roughness"].default_value = 0.5; lb.inputs["Sheen Weight"].default_value = 0.4
lb.inputs["Emission Color"].default_value = (*PINK, 1); lb.inputs["Emission Strength"].default_value = 0.18
hd.data.materials.append(lin)

# ---------------------------------------------------------------- lights: product rig, linked to the figure only
def light(name, loc, energy, sx, sy, col_=(1, 1, 1), look=None, glossy=True, diffuse=True):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col_; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look or HC) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    o.visible_glossy = glossy; o.visible_diffuse = diffuse
    try: o.light_linking.receiver_collection = COL
    except AttributeError: pass
    return o
FZ = HC.z
light("LGT_Key_Softbox", (-2.2, -1.8, FZ + 1.1), 260, 2.4, 1.2)
light("LGT_Key_TopStrip", (-2.0, -1.4, FZ + 1.8), 220, 2.4, 0.14)
light("LGT_Strip_Back", (1.0, 2.2, FZ), 450, 0.15, 3.0, (0.8, 0.88, 1.0))
light("LGT_Strip_Pink", (2.2, 0.4, FZ - 0.2), 220, 0.12, 3.0, PINK)
light("LGT_Rim_Top", (0.5, 1.2, FZ + 1.8), 260, 1.4, 0.2, (0.9, 0.92, 1.0))
light("LGT_Front_Fill", (-0.6, -2.6, FZ - 0.5), 200, 1.8, 1.4, glossy=False)
light("LGT_Visor_Streak", (-1.2, -2.4, FZ + 0.7), 120, 2.2, 0.06, diffuse=False)
W = bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True
W.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.025, 0.16, 1); W.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5

# ---------------------------------------------------------------- hero camera (reference framing: low 28 mm, helmet big, centre-right)
cam = bpy.data.objects.new("CAM_Hero", bpy.data.cameras.new("CAM_Hero")); S.collection.objects.link(cam); S.camera = cam
tgt = bpy.data.objects.new("CAM_T", None); S.collection.objects.link(tgt); tgt.location = HC + Vector((0, 0, -0.04))
cam.location = HC + Vector((E("CAM_X", -1.6), E("CAM_Y", -0.85), E("CAM_Z", -0.12)))
cam.data.lens = E("LENS", 40); cam.data.shift_x = E("SHIFT_X", -0.06); cam.data.shift_y = E("SHIFT_Y", -0.045)
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

S.render.engine = 'CYCLES'; cy = S.cycles; cy.device = 'CPU'; cy.samples = 48; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03
cy.use_denoising = False; cy.diffuse_bounces = 2; cy.glossy_bounces = 4; cy.transmission_bounces = 2; cy.sample_clamp_indirect = 3.0
S.render.resolution_x, S.render.resolution_y = 1920, 1080; S.render.film_transparent = True
S.view_settings.view_transform = "Standard"; S.view_settings.exposure = -0.8
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); cpo = ct.nodes.new("CompositorNodeComposite"); ct.links.new(rl.outputs["Image"], cpo.inputs["Image"])
if args and args[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=args[1]); print("SAVED", tuple(round(v, 3) for v in HC), round(HZ0, 3), round(HZ1, 3))
