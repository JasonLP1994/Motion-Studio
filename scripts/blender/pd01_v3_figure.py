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
# close the open front: slide both front panels toward the centre line by the measured gap (wider at the flared collar)
ZG = [0.45, 0.6, 0.8, 1.0, 1.2, 1.3, 1.4, 1.48, 1.58]; GG = [0.0, 0.03, 0.068, 0.052, 0.055, 0.038, 0.033, 0.072, 0.09]
g = (np.interp(co[:, 2], ZG, GG) + 0.006) * E("CLOSE", 1.0)
front = np.clip((co[:, 1].mean() - 0.02 - co[:, 1]) / 0.06, 0, 1)
ax_ = np.abs(co[:, 0]); w = np.clip((0.30 - ax_) / 0.16, 0, 1); w = w * w * (3 - 2 * w)
co[:, 0] -= np.sign(co[:, 0]) * np.minimum(g * w * front, ax_)
setV(coat, co)
# smooth away the model's sculpted lumps (they read as abs) before adding clean quilting
bm = bmesh.new(); bm.from_mesh(coat.data)
tv = [v for v in bm.verts if v.co.z < 1.36]
for _ in range(int(E("SMOOTH_IT", 12))): bmesh.ops.smooth_vert(bm, verts=tv, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.to_mesh(coat.data); bm.free(); coat.data.update(); co = V(coat)
# quilted baffles: push the surface in along the normals at evenly spaced horizontal seams (real geometry, not just shading)
nrm = np.empty(len(coat.data.vertices) * 3); coat.data.vertices.foreach_get("normal", nrm); nrm = nrm.reshape(-1, 3)
PITCH, DEPTH = E("BAFFLE", 0.085), E("BAFFLE_D", 0.018)
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
        ztop = E("HOOD_SIDE_Z", 1.40) + E("HOOD_RISE", 0.24) * wb ** 1.3 + 0.014 * math.sin(a_ * 6 + 0.4) * wb   # wavy fabric edge
        z = 1.32 + (ztop - 1.32) * t
        r = 0.168 + 0.02 * wb + 0.055 * wb * math.sin(math.pi * min(t, 0.9) / 0.9 * 0.85) + 0.02 * t
        r += 0.045 * max(0.0, (t - 0.72) / 0.28) ** 1.5              # edge folds open (flat, not rolled) so the lining shows
        r += 0.008 * math.sin(a_ * 5 + 1.3) * t * wb                   # soft folds
        verts_.append((r * math.sin(a_), -r * math.cos(a_) + 0.03 * wb, z))
for i in range(NT_ - 1):
    for j in range(NA_ - 1):
        faces_.append((i * NA_ + j, i * NA_ + j + 1, (i + 1) * NA_ + j + 1, (i + 1) * NA_ + j))
hm_ = bpy.data.meshes.new("hood"); hm_.from_pydata(verts_, [], faces_)
hd = bpy.data.objects.new("SM_Hood", hm_); COL.objects.link(hd)
hv = V(hd)
setV(hd, hv); hd.data.polygons.foreach_set("use_smooth", [True] * len(hd.data.polygons))
sd = hd.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = 0.014; sd.offset = -1.0; sd.use_rim = True; sd.material_offset = 1; sd.material_offset_rim = 0   # thin fabric, navy edge
hd.modifiers.new("Sub", 'SUBSURF').levels = 2

# ---------------------------------------------------------------- helmet: width 0.40 m, neck ring seated inside the collar
helm = import_one(HELM, "SM_Helmet")
co = V(helm); s = E("HELM_W", 0.46) / (co[:, 0].max() - co[:, 0].min()); co *= s
b = co[co[:, 2] < co[:, 2].min() + 0.25 * s]
co -= [b[:, 0].mean(), b[:, 1].mean() + E("HELM_DY", 0.07), co[:, 2].min() - (1.50 - E("HELM_SINK", 0.07))]
th = math.radians(E("HELM_PITCH", 12)); piv = np.array([0.0, 0.0, co[:, 2].min()])
q = co - piv; y_, z_ = q[:, 1].copy(), q[:, 2].copy(); q[:, 1] = y_ * math.cos(th) - z_ * math.sin(th); q[:, 2] = y_ * math.sin(th) + z_ * math.cos(th)
co = q + piv; co[:, 2] += (1.50 - E("HELM_SINK", 0.07)) - co[:, 2].min()
setV(helm, co)
HC = Vector(co.mean(0)); HZ0, HZ1 = co[:, 2].min(), co[:, 2].max()

# ---------------------------------------------------------------- zip: pink tape down the centre front
cz = V(coat); fr = cz[(np.abs(cz[:, 0]) < 0.012) & (cz[:, 1] < cz[:, 1].mean())]
zpts = []
for z in np.linspace(0.62, 1.52, 46):
    sl = fr[np.abs(fr[:, 2] - z) < 0.012]
    if len(sl): zpts.append((0.0, sl[:, 1].min() - 0.006, z))
if len(zpts) > 4:
    cu = bpy.data.curves.new("zip", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.006; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(zpts) - 1)
    for i, q in enumerate(zpts): sp.points[i].co = (*q, 1)
    zo = bpy.data.objects.new("SM_Zip", cu); COL.objects.link(zo)
    zm = bpy.data.materials.new("MAT_ZipPink"); zm.use_nodes = True; zb = zm.node_tree.nodes["Principled BSDF"]
    zb.inputs["Base Color"].default_value = (*PINK, 1); zb.inputs["Roughness"].default_value = 0.35
    zb.inputs["Emission Color"].default_value = (*PINK, 1); zb.inputs["Emission Strength"].default_value = 0.3; cu.materials.append(zm)

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
teal = mnode(nt, 'MULTIPLY', mnode(nt, 'MULTIPLY', mnode(nt, 'MULTIPLY', band(nt, H_, 0.42, 0.62), mnode(nt, 'GREATER_THAN', S_, 0.22)), mnode(nt, 'LESS_THAN', V_, 0.62)), mnode(nt, 'SUBTRACT', 1.0, yellow))   # visor only (bluish grey paint was turning into mirror glass)
grey = mnode(nt, 'MULTIPLY', band(nt, V_, 0.16, 0.36), mnode(nt, 'LESS_THAN', S_, 0.18))
shell_black = (0.006, 0.006, 0.008, 1); gun = (0.010, 0.010, 0.013, 1); glass = (0.002, 0.002, 0.003, 1)
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
nt.links.new(mixf(nt, teal, 0.26, 0.03), bs.inputs["Roughness"])   # one even satin-gloss finish (worn spots made blotchy reflections)
bs.inputs["Coat Weight"].default_value = 0.5; bs.inputs["Coat Roughness"].default_value = 0.18
nm_ = bs.inputs["Normal"].links[0].from_node; nm_.inputs["Strength"].default_value = E("HELM_NORMAL", 0.25)

# puffer: black nylon outside, hot-pink lining where we see the inside (collar)
pm = bpy.data.materials.new("MAT_PufferNylon"); pm.use_nodes = True; pn = pm.node_tree; pb = pn.nodes["Principled BSDF"]
geo = pn.nodes.new("ShaderNodeNewGeometry")
sep = pn.nodes.new("ShaderNodeSeparateXYZ"); pn.links.new(geo.outputs["Position"], sep.inputs[0])
lining = mnode(pn, 'MULTIPLY', geo.outputs["Backfacing"], mnode(pn, 'GREATER_THAN', sep.outputs["Z"], 1.28))
pn.links.new(mix(pn, lining, (E("NAVY_R", 0.0035), E("NAVY_G", 0.0055), E("NAVY_B", 0.020), 1), (*PINK, 1)), pb.inputs["Base Color"])
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
# printed decals (in the fabric, follow the quilting): PD-01 on the near sleeve, the Phillips Digital "p." patch on the chest
def decal(nt, img_path, axis, centre, size, face_mask, flip_u=False):
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]; sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(pos, sx.inputs[0])
    ax_u, ax_v = (sx.outputs["Y"], sx.outputs["Z"]) if axis == 'X' else (sx.outputs["X"], sx.outputs["Z"])
    cu_, cv_ = centre; su, sv = size
    u = mnode(nt, 'ADD', mnode(nt, 'MULTIPLY', mnode(nt, 'SUBTRACT', ax_u, cu_), (-1.0 if flip_u else 1.0) / su), 0.5)
    v = mnode(nt, 'ADD', mnode(nt, 'MULTIPLY', mnode(nt, 'SUBTRACT', ax_v, cv_), 1.0 / sv), 0.5)
    u.node.use_clamp = False; v.node.use_clamp = False
    for n_ in (u.node.inputs[0].links[0].from_node, v.node.inputs[0].links[0].from_node): n_.use_clamp = False
    for n_ in (u.node.inputs[0].links[0].from_node.inputs[0].links[0].from_node, v.node.inputs[0].links[0].from_node.inputs[0].links[0].from_node): n_.use_clamp = False
    cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u, cmb.inputs[0]); nt.links.new(v, cmb.inputs[1])
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(img_path, check_existing=True); tx.extension = 'CLIP'
    nt.links.new(cmb.outputs[0], tx.inputs["Vector"])
    return tx.outputs["Color"], mnode(nt, 'MULTIPLY', tx.outputs["Alpha"], face_mask)
gN = pn.nodes.new("ShaderNodeNewGeometry"); sN = pn.nodes.new("ShaderNodeSeparateXYZ"); pn.links.new(gN.outputs["Normal"], sN.inputs[0])
def soft_lt(x, a, b):     # 1 when x < a, fading to 0 at b (a < b)
    n_ = pn.nodes.new("ShaderNodeMapRange"); n_.interpolation_type = 'SMOOTHSTEP'; pn.links.new(x, n_.inputs[0])
    n_.inputs[1].default_value, n_.inputs[2].default_value, n_.inputs[3].default_value, n_.inputs[4].default_value = a, b, 1.0, 0.0
    return n_.outputs[0]
near_side = soft_lt(sN.outputs["X"], -0.12, 0.25); front_side = soft_lt(sN.outputs["Y"], -0.3, 0.1)
not_lining = mnode(pn, 'SUBTRACT', 1.0, lining)
DC = R + "decals/"
side_m = mnode(pn, 'MULTIPLY', near_side, not_lining); front_m = mnode(pn, 'MULTIPLY', front_side, not_lining)
PUFF = lambda k: (k + 0.5) * PITCH          # centre height of puff panel k (seams sit at k * PITCH)
# (image, projection axis, centre (u-axis, z), width m, mask, flip)  - small, technical print system like the reference
DECALS = [
    (DC + "decal_A.png", 'X', (E("PRINT_Y", -0.05), PUFF(14)), 0.128, side_m, True),      # sleeve PD-01 block, inside one puff panel
    (DC + "decal_C.png", 'X', (-0.10, PUFF(15)), 0.15, side_m, True),                        # micro spec text, next panel up
    (DC + "decal_D.png", 'X', (-0.06, PUFF(13)), 0.10, side_m, True),                        # spec block, panel below
    # (DC + "decal_B.png", ...) pink zip tab: smeared on the curved collar, off for now
    (R + "decal_logo_pink.png", 'Y', (E("LOGO_X", -0.085), PUFF(15)), 0.04, front_m, True),     # hot-pink p. patch
]
# lay each print flat on the surface like a sticker: project along the local surface normal (averaged around the spot), not a
# world axis, so the art isn't stretched where the sleeve curves; a thin slab test keeps it off layers behind
from mathutils.bvhtree import BVHTree
_bvh = BVHTree.FromPolygons([v.co.copy() for v in coat.data.vertices], [tuple(p_.vertices) for p_ in coat.data.polygons])
def surf_frame(axis, cu_, cz_):
    d = Vector((1, 0, 0)) if axis == 'X' else Vector((0, 1, 0)); nsum = Vector((0, 0, 0)); hitc = None
    for du in (-0.02, 0.0, 0.02):
        for dz in (-0.015, 0.0, 0.015):
            o = Vector((-1.0, cu_ + du, cz_ + dz)) if axis == 'X' else Vector((cu_ + du, -1.0, cz_ + dz))
            h = _bvh.ray_cast(o, d)
            if h[0] is None: continue
            n_ = h[1] if h[1].dot(d) < 0 else -h[1]; nsum += n_
            if du == 0 and dz == 0: hitc = h[0]
    N = nsum.normalized(); Vv = (Vector((0, 0, 1)) - N * N.z).normalized(); U = N.cross(Vv).normalized()
    return hitc, N, U, Vv
def vdot(nt, a_, vec):
    n_ = nt.nodes.new("ShaderNodeVectorMath"); n_.operation = 'DOT_PRODUCT'; nt.links.new(a_, n_.inputs[0]); n_.inputs[1].default_value = vec
    return n_.outputs["Value"]
gp = pn.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
cur = pb.inputs["Base Color"].links[0].from_socket; amax = None
SCALE = E("PRINT_SCALE", 0.85)
for img, axis, cen, wdt, msk, flp in DECALS:
    C_, N_, U_, V_ = surf_frame(axis, *cen)
    if C_ is None: print("DECAL MISS", img); continue
    if flp: U_ = -U_
    im_ = bpy.data.images.load(img, check_existing=True); asp = im_.size[1] / im_.size[0]; w_ = wdt * SCALE; h_ = w_ * asp
    # wrap around the body along the seam: u = arc length around a vertical axis behind the spot (radius ~ local curvature),
    # v = height (the seams are constant height), so text lines run parallel to the quilting and nothing stretches
    Rr = E("WRAP_R", 0.24); nxy = Vector((N_.x, N_.y, 0)).normalized(); ctr = C_ - nxy * Rr
    th0 = math.atan2(C_.y - ctr.y, C_.x - ctr.x); tang = Vector((-math.sin(th0), math.cos(th0), 0))
    sgn = 1.0 if Vector((U_.x, U_.y, 0)).dot(tang) > 0 else -1.0
    sp_ = pn.nodes.new("ShaderNodeSeparateXYZ"); pn.links.new(gp, sp_.inputs[0])
    dx = mnode(pn, 'SUBTRACT', sp_.outputs["X"], ctr.x); dy = mnode(pn, 'SUBTRACT', sp_.outputs["Y"], ctr.y)
    for n_ in (dx.node, dy.node): n_.use_clamp = False
    at = pn.nodes.new("ShaderNodeMath"); at.operation = 'ARCTAN2'; pn.links.new(dy, at.inputs[0]); pn.links.new(dx, at.inputs[1])
    dth = pn.nodes.new("ShaderNodeMath"); dth.operation = 'SUBTRACT'; pn.links.new(at.outputs[0], dth.inputs[0]); dth.inputs[1].default_value = th0
    u = pn.nodes.new("ShaderNodeMath"); u.operation = 'MULTIPLY_ADD'; pn.links.new(dth.outputs[0], u.inputs[0]); u.inputs[1].default_value = sgn * Rr / w_; u.inputs[2].default_value = 0.5
    v = pn.nodes.new("ShaderNodeMath"); v.operation = 'MULTIPLY_ADD'; pn.links.new(sp_.outputs["Z"], v.inputs[0]); v.inputs[1].default_value = 1 / h_; v.inputs[2].default_value = 0.5 - C_.z / h_
    cmb = pn.nodes.new("ShaderNodeCombineXYZ"); pn.links.new(u.outputs[0], cmb.inputs[0]); pn.links.new(v.outputs[0], cmb.inputs[1])
    tx = pn.nodes.new("ShaderNodeTexImage"); tx.image = im_; tx.extension = 'CLIP'; pn.links.new(cmb.outputs[0], tx.inputs["Vector"])
    rr = pn.nodes.new("ShaderNodeVectorMath"); rr.operation = 'LENGTH'
    cxy = pn.nodes.new("ShaderNodeCombineXYZ"); pn.links.new(dx, cxy.inputs[0]); pn.links.new(dy, cxy.inputs[1]); pn.links.new(cxy.outputs[0], rr.inputs[0])
    dev = pn.nodes.new("ShaderNodeMath"); dev.operation = 'SUBTRACT'; pn.links.new(rr.outputs["Value"], dev.inputs[0]); dev.inputs[1].default_value = Rr
    ab_ = pn.nodes.new("ShaderNodeMath"); ab_.operation = 'ABSOLUTE'; pn.links.new(dev.outputs[0], ab_.inputs[0])
    slab = mnode(pn, 'LESS_THAN', ab_.outputs[0], 0.05)
    da_ = mnode(pn, 'MULTIPLY', mnode(pn, 'MULTIPLY', tx.outputs["Alpha"], msk), slab)
    cur = mix(pn, da_, cur, tx.outputs["Color"]); amax = da_ if amax is None else mnode(pn, 'MAXIMUM', amax, da_)
pn.links.new(cur, pb.inputs["Base Color"]); sa = amax; la = amax
rough_in = pb.inputs["Roughness"].links[0].from_socket
pn.links.new(mixf(pn, mnode(pn, 'MAXIMUM', sa, la), rough_in, 0.42), pb.inputs["Roughness"])     # plastisol ink is a touch shinier
coat.data.materials.clear(); coat.data.materials.append(pm)
hmat = pm.copy(); hmat.name = "MAT_HoodNylon"
for n in hmat.node_tree.nodes:
    if n.type == 'MATH' and n.operation == 'GREATER_THAN' and abs(n.inputs[1].default_value - 1.28) < 1e-6: n.inputs[1].default_value = -10.0
hd.data.materials.append(hmat)
lin = bpy.data.materials.new("MAT_PinkLining"); lin.use_nodes = True; lb = lin.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = (*PINK, 1); lb.inputs["Roughness"].default_value = 0.65; lb.inputs["Sheen Weight"].default_value = 0.3
lb.inputs["Emission Color"].default_value = (*PINK, 1); lb.inputs["Emission Strength"].default_value = 0.05
hd.data.materials.append(lin)

# ---------------------------------------------------------------- sleeve print: PD-01 (white) + PHILLIPS DIGITAL (pink) on the near upper arm
from mathutils.bvhtree import BVHTree
coat_bvh = BVHTree.FromPolygons([v.co.copy() for v in coat.data.vertices], [tuple(p.vertices) for p in coat.data.polygons])
def flatm(name, rgb, rough, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b_ = m.node_tree.nodes["Principled BSDF"]
    b_.inputs["Base Color"].default_value = (*rgb, 1); b_.inputs["Roughness"].default_value = rough
    if emit: b_.inputs["Emission Color"].default_value = (*rgb, 1); b_.inputs["Emission Strength"].default_value = emit
    return m
FONT = "/home/user/Motion-Studio/public/fonts/BarlowCondensed-BlackItalic.ttf"
def sleeve_text(body, size, z, y0, mat, font=FONT):
    hit = coat_bvh.ray_cast(Vector((-1.0, y0, z)), Vector((1, 0, 0)))
    if hit[0] is None: print("PRINT MISS", body); return None
    cd = bpy.data.curves.new("txt", 'FONT'); cd.body = body; cd.size = size; cd.align_x = 'CENTER'; cd.align_y = 'CENTER'
    cd.font = bpy.data.fonts.load(font, check_existing=True)
    t = bpy.data.objects.new("SM_Print_" + body[:6], cd); COL.objects.link(t)
    t.location = hit[0] + Vector((-0.03, 0, 0)); t.rotation_euler = (math.radians(90), math.radians(E("PRINT_TILT", -12)), math.radians(-90))
    bpy.context.view_layer.objects.active = t; t.select_set(True); bpy.ops.object.convert(target='MESH'); t.select_set(False)
    t.data.materials.append(mat)
    sw = t.modifiers.new("Wrap", 'SHRINKWRAP'); sw.target = coat; sw.wrap_method = 'PROJECT'; sw.use_project_x = True
    sw.use_negative_direction = True; sw.use_positive_direction = True; sw.offset = 0.003
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(t.evaluated_get(dg)); t.modifiers.clear(); t.data = me
    return t

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
light("LGT_Key_Softbox", (-2.2, -1.8, FZ + 1.1), 200, 2.4, 1.2)
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
