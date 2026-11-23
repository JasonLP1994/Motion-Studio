# PD-01 v2 (closer to the reference): faceted armour helmet "Scifi Helmet" by sunix (CC-BY 4.0, Objaverse 91034c2b...)
# with a glossy black visor, satin black panels, hot-pink accents; techwear hoodie "Hoodie" by Badboy17Aiden (CC-BY 4.0,
# Objaverse 6dca9cd8...) recoloured black with pink lining, sleeves bent down from the T-pose. Transparent render over electric
# blue (Remotion), product lighting rig, Cycles + OIDN.
# Run: PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber2/pd01b.py -- save OUT.blend | wb OUT.png
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector
R = "/home/user/Motion-Studio/work/cyber2/"
HELM, HOOD = R + "91034c2b2496474f9c87208070472782.glb", R + "6dca9cd855a8441881f0b324236cf325.glb"
PINK = (0.9, 0.0, 0.12)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.fps = 24

def import_join(path, name):
    before = set(S.objects); bpy.ops.import_scene.gltf(filepath=path)
    ms = [o for o in S.objects if o not in before and o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]; bpy.ops.object.join(); ob = bpy.context.view_layer.objects.active; ob.name = name
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in [o for o in S.objects if o not in before and o != ob]: bpy.data.objects.remove(o)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(ob.data); bm.free()
    ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
    bpy.ops.object.select_all(action='DESELECT'); return ob

def verts(ob):
    co = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", co); return co.reshape(-1, 3)
def set_verts(ob, co): ob.data.vertices.foreach_set("co", co.ravel()); ob.data.update()

# ---------------------------------------------------------------- hoodie: centre, sole of the hem at z=0, height 1.85 units, sleeves bent down
hood = import_join(HOOD, "SM_Hoodie")
co = verts(hood); lo, hi = co.min(0), co.max(0)
co = co - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]
SH_X, SH_Z = 0.27, 1.22                              # shoulder pivot; arms are already in an A-pose (~50 deg down)
for side in (1, -1):
    ax = co[:, 0] * side; w = np.clip((ax - SH_X) / 0.18, 0, 1); w = w * w * (3 - 2 * w)
    w = w * (co[:, 2] < SH_Z + 0.05)
    ang = -side * np.radians(28) * w                     # +28 deg more so the sleeves hang at the sides
    px, pz = co[:, 0] - side * SH_X, co[:, 2] - SH_Z
    co[:, 0] = np.where(w > 0, side * SH_X + px * np.cos(ang) - pz * np.sin(ang), co[:, 0])
    co[:, 2] = np.where(w > 0, SH_Z + px * np.sin(ang) + pz * np.cos(ang), co[:, 2])
set_verts(hood, co)
# hood down: delete the hood above the neckline (the reference has a high collar, not a raised hood)
bm = bmesh.new(); bm.from_mesh(hood.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1.27], context='VERTS'); bm.to_mesh(hood.data); bm.free()
bm = bmesh.new(); bm.from_mesh(hood.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(hood.data); bm.free()
co = verts(hood)
NECK = 1.25
nk = co[(co[:, 2] > NECK - 0.06) & (co[:, 2] < NECK + 0.02)]
NCX, NCY = float(nk[:, 0].mean()), float(nk[:, 1].mean())   # centre of the neck opening
HOOD_TOP = NECK


# ---------------------------------------------------------------- helmet: face to -Y (front was -X), height 0.62, sit in the hood
helm = import_join(HELM, "SM_Helmet")
co = verts(helm); lo, hi = co.min(0), co.max(0); c = (lo + hi) / 2
co = co - c; co = np.stack([co[:, 1], -co[:, 0], co[:, 2]], 1)          # rotate +90 deg about Z: front -X -> -Y
sc = 0.58 / (hi[2] - lo[2]); co *= sc
co += [NCX, NCY - 0.07, NECK + 0.27]
set_verts(helm, co)
# ---------------------------------------------------------------- collar fitted to the helmet: loft from the neck opening up to the
# helmet's own bottom outline, so the helmet sits down inside it (black shell, hot-pink lining, rolled lip, higher at the back)
hz0 = co[:, 2].min(); base = co[co[:, 2] < hz0 + 0.05]
NA = 64; angs = np.linspace(0, 2 * np.pi, NA, endpoint=False)
rel = base[:, :2] - [NCX, NCY - 0.07]; th = np.arctan2(rel[:, 1], rel[:, 0]); rr = np.hypot(rel[:, 0], rel[:, 1])
top_r = np.array([rr[np.abs((th - a + np.pi) % (2 * np.pi) - np.pi) < 0.12].max() if np.any(np.abs((th - a + np.pi) % (2 * np.pi) - np.pi) < 0.12) else 0.2 for a in angs])
top_r = np.convolve(np.r_[top_r[-3:], top_r, top_r[:3]], np.ones(7) / 7, 'same')[3:-3] + 0.025
rings = []
for k, t in enumerate(np.linspace(0, 1, 9)):
    ring = []
    for a, tr in zip(angs, top_r):
        back = max(0.0, math.sin(a))                     # +Y = back of the neck
        rb = 0.19 * (1.0 - 0.08 * back)                  # neck opening radius
        ease = t * t * (3 - 2 * t)
        r = rb + (tr - rb) * ease + 0.035 * math.sin(math.pi * t)       # puffy bulge
        cx = NCX; cy = NCY + (-0.07) * ease
        z = (NECK - 0.05) + t * (hz0 + 0.07 + 0.09 * back - (NECK - 0.05))
        ring.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    rings.append(ring)
vs = [v for r in rings for v in r]
fs = [(i * NA + j, i * NA + (j + 1) % NA, (i + 1) * NA + (j + 1) % NA, (i + 1) * NA + j) for i in range(len(rings) - 1) for j in range(NA)]
cm = bpy.data.meshes.new("collar"); cm.from_pydata(vs, [], fs); cm.polygons.foreach_set("use_smooth", [True] * len(fs))
col_ = bpy.data.objects.new("SM_Collar", cm); S.collection.objects.link(col_)
sd = col_.modifiers.new("Thick", 'SOLIDIFY'); sd.thickness = 0.03; sd.offset = 0.0; sd.material_offset = 1; sd.use_rim = True; sd.material_offset_rim = 1
col_.modifiers.new("Sub", 'SUBSURF').levels = 2
# hood folded down behind the neck: a fat roll, black outside / pink inside
bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.07, major_segments=48, minor_segments=16, location=(NCX, NCY + 0.06, NECK + 0.02))
roll = bpy.context.active_object; roll.name = "SM_HoodRoll"; roll.scale = (1.05, 0.85, 0.7)
bm = bmesh.new(); bm.from_mesh(roll.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.02], context='VERTS'); bm.to_mesh(roll.data); bm.free()
roll.rotation_euler = (math.radians(-18), 0, 0); bpy.ops.object.shade_smooth()

# ---------------------------------------------------------------- materials
TEX = R + "tex/"   # masks made from the model's own maps: mag.png = rear shell (metal map), seam.png = panel lines/labels/rivets (normal map)
def recolour_helmet(mat):
    nt = mat.node_tree; N, L = nt.nodes, nt.links; b = N["Principled BSDF"]
    src_img = next(n for n in N if n.type == 'TEX_IMAGE')
    uv = src_img.inputs["Vector"].links[0].from_socket if src_img.inputs["Vector"].links else None
    def tex(fn):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(TEX + fn, check_existing=True); t.image.colorspace_settings.name = 'Non-Color'
        if uv: L.new(uv, t.inputs["Vector"])
        return t.outputs["Color"]
    albedo = next(l.from_socket for l in b.inputs["Base Color"].links)
    hsv = N.new("ShaderNodeSeparateHSV"); L.new(albedo, hsv.inputs[0])
    def m(op, a, c_=None):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = True
        for i, v in enumerate((a, c_)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    shell = tex("mag.png"); seam = tex("seam.png")
    shell = m('GREATER_THAN', N.new("ShaderNodeRGBToBW").outputs[0] if False else shell, 0.5)
    seam = m('GREATER_THAN', seam, 0.5)
    # base: satin black with a hint of the plate variation (gunmetal on the lighter plates)
    g = m('ADD', m('MULTIPLY', hsv.outputs["V"], 0.06), 0.006)
    blk = N.new("ShaderNodeCombineRGB")
    for ch, mul in (("R", 1.0), ("G", 1.0), ("B", 1.15)): L.new(m('MULTIPLY', g, mul), blk.inputs[ch])
    def mix(fac, a_, b_):
        x = N.new("ShaderNodeMix"); x.data_type = 'RGBA'; L.new(fac, x.inputs["Factor"])
        for sock, v in ((6, a_), (7, b_)):
            if isinstance(v, tuple): x.inputs[sock].default_value = v
            else: L.new(v, x.inputs[sock])
        return x.outputs[2]
    col = mix(shell, blk.outputs[0], (*PINK, 1))                           # rear shell -> hot pink
    col = mix(m('MULTIPLY', seam, m('SUBTRACT', 1.0, shell)), col, (*PINK, 1))   # seams/labels/rivets on black -> pink
    col = mix(m('MULTIPLY', seam, shell), col, (0.01, 0.01, 0.012, 1))      # seams on the pink shell -> black lines
    L.new(col, b.inputs["Base Color"]); L.new(col, b.inputs["Emission Color"])
    L.new(m('ADD', m('MULTIPLY', m('MULTIPLY', seam, m('SUBTRACT', 1.0, shell)), 1.6), m('MULTIPLY', shell, 0.0)), b.inputs["Emission Strength"])
    for l in list(b.inputs["Roughness"].links): L.remove(l)
    for l in list(b.inputs["Metallic"].links): L.remove(l)
    b.inputs["Metallic"].default_value = 0.0
    L.new(m('ADD', 0.22, m('MULTIPLY', shell, 0.12)), b.inputs["Roughness"])
    b.inputs["Coat Weight"].default_value = 0.6; b.inputs["Coat Roughness"].default_value = 0.06
for mat in helm.data.materials:
    if mat and mat.use_nodes: recolour_helmet(mat)
# visor: front-facing faces of the helmet's front third -> glossy black glass
vis = bpy.data.materials.new("MAT_Visor"); vis.use_nodes = True; vb = vis.node_tree.nodes["Principled BSDF"]
vb.inputs["Base Color"].default_value = (0.002, 0.002, 0.004, 1); vb.inputs["Metallic"].default_value = 0.0; vb.inputs["Roughness"].default_value = 0.02
vb.inputs["Coat Weight"].default_value = 1.0; vb.inputs["Coat Roughness"].default_value = 0.0; vb.inputs["Specular IOR Level"].default_value = 0.8
helm.data.materials.append(vis); vi = len(helm.data.materials) - 1
hco = verts(helm); ymin, ymax = hco[:, 1].min(), hco[:, 1].max(); zmin, zmax = hco[:, 2].min(), hco[:, 2].max()
for p in helm.data.polygons:
    cy, cz = p.center.y, p.center.z
    if p.normal.y < -0.55 and cy < ymin + (ymax - ymin) * 0.32 and zmin + (zmax - zmin) * 0.18 < cz < zmin + (zmax - zmin) * 0.82:
        p.material_index = vi
# hot-pink panels by region (the merged mesh has no separate plates): rear neck guard + a side module each side
pk = bpy.data.materials.new("MAT_PinkPanel"); pk.use_nodes = True; pb = pk.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = (*PINK, 1); pb.inputs["Roughness"].default_value = 0.3; pb.inputs["Coat Weight"].default_value = 0.4
pb.inputs["Emission Color"].default_value = (*PINK, 1); pb.inputs["Emission Strength"].default_value = 0.25
helm.data.materials.append(pk); pi = len(helm.data.materials) - 1
H = lambda f: zmin + (zmax - zmin) * f
Yr = lambda f: ymin + (ymax - ymin) * f
for p in helm.data.polygons:
    x, y, z = p.center
    rear = y > Yr(0.80) and z < H(0.42) and p.normal.y > 0.2
    side = abs(x) > 0.15 and Yr(0.30) < y < Yr(0.48) and H(0.36) < z < H(0.50) and abs(p.normal.x) > 0.6
    pass
def flat(name, col, rough, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = emit
    return m
fab = flat("MAT_Techwear", (0.0012, 0.0012, 0.002), 0.8); fab.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15; lin = flat("MAT_PinkLining", PINK, 0.5, 0.15)
hood.data.materials.clear(); hood.data.materials.append(fab); hood.data.materials.append(lin)
hood.data.polygons.foreach_set("material_index", [0] * len(hood.data.polygons))
col_.data.materials.append(fab); col_.data.materials.append(lin)
roll.data.materials.append(fab); roll.data.materials.append(lin)
rc = Vector((0, 0, 0))
for p_ in roll.data.polygons:      # faces of the tube that look up/inward toward the neck -> pink lining
    v_ = p_.center; ring_dir = Vector((v_.x, v_.y, 0)).normalized()
    if p_.normal.z > 0.35 or p_.normal.dot(ring_dir) < -0.3: p_.material_index = 1
ss = hood.modifiers.new('Sub', 'SUBSURF'); ss.levels = ss.render_levels = 1
RIG = bpy.data.objects.new("FIGURE_RIG", None); S.collection.objects.link(RIG)
for o in (hood, helm, col_, roll): o.parent = RIG

# ---------------------------------------------------------------- lights (product rig) + world for reflections
COL_P = bpy.data.collections.new("COL_Product"); S.collection.children.link(COL_P); COL_P.objects.link(hood); COL_P.objects.link(helm)
for o in (hood, helm, col_, roll):
    for c in list(o.users_collection):
        if c != COL_P: c.objects.unlink(o)
COL_P.objects.link(col_); COL_P.objects.link(roll)
def link(o):
    try: o.light_linking.receiver_collection = COL_P
    except AttributeError: pass
def light(name, loc, energy, sx, sy, col=(1, 1, 1), look=(0, 0, 1.9)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); link(o); return o
FZ = NECK + 0.3
light("LGT_Key_Softbox", (-2.4, -1.6, FZ + 1.2), 380, 2.4, 1.2, look=(0, 0, FZ))
light("LGT_Key_TopStrip", (-2.2, -1.4, FZ + 1.9), 200, 2.4, 0.14, look=(0, 0, FZ))
light("LGT_Strip_Back", (1.2, 2.2, FZ), 420, 0.15, 3.0, (0.8, 0.88, 1.0), look=(0, 0, FZ))
light("LGT_Strip_Pink", (2.2, 0.6, FZ - 0.2), 160, 0.12, 3.0, PINK, look=(0, 0, FZ))
light("LGT_Rim_Top", (0.6, 1.2, FZ + 1.8), 260, 1.4, 0.2, (0.9, 0.92, 1.0), look=(0, 0, FZ))
ch_ = light("LGT_Front_Chest", (-1.6, -2.4, FZ - 0.5), 450, 1.6, 1.0, look=(0, -0.2, FZ - 0.7)); ch_.visible_glossy = False
f = light("LGT_Fill", (-1.8, -2.4, FZ - 0.6), 40, 2.4, 2.4, look=(0, 0, FZ)); f.visible_glossy = False
W = bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True; W.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.025, 0.16, 1)
W.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6


# ---------------------------------------------------------------- hard-surface accents (modelled, so edges stay clean)
def box(name, loc, dims, mat, rot=(0, 0, 0), bev=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.active_object; o.name = name; o.scale = dims
    bpy.ops.object.transform_apply(scale=True); b = o.modifiers.new("Bev", 'BEVEL'); b.width = bev; b.segments = 3
    o.data.materials.append(mat); o.parent = RIG; COL_P.objects.link(o); S.collection.objects.unlink(o); bpy.ops.object.shade_smooth(); return o
from mathutils.bvhtree import BVHTree
_hv = [v.co.copy() for v in helm.data.vertices]; BVH = BVHTree.FromPolygons(_hv, [tuple(p.vertices) for p in helm.data.polygons])
def ray_x(y, z, side):     # surface point on the helmet side at (y, z) (own BVH: Object.ray_cast was stale here)
    loc, nor, _, _ = BVH.ray_cast(Vector((side * 1.0, y, z)), Vector((-side, 0, 0)))
    if loc is None: return None, None
    if nor.x * side < 0: nor = -nor
    return loc, nor
bpy.context.view_layer.update()   # ray_cast needs the evaluated mesh
gm = flat("MAT_Gunmetal", (0.03, 0.03, 0.035), 0.35)
for side in (1, -1):
    loc, nor = ray_x(-0.10, NECK + 0.17, side)
    if loc is not None:
        box(f"SM_SideModule_{side}", loc + nor * 0.02, (0.03, 0.05, 0.11), pk, rot=(0, 0, 0))
        box(f"SM_SideLight_{side}", loc + nor * 0.034 + Vector((0, 0, -0.035)), (0.006, 0.03, 0.008), flat("MAT_BlueLED", (0.25, 0.5, 1.0), 0.2, 6.0))
    loc, nor = ray_x(0.06, NECK + 0.30, side)
    if loc is not None:
        tri = bpy.data.meshes.new("tri"); r = 0.035
        tri.from_pydata([(0, -r, r * 0.6), (0, r, r * 0.6), (0, 0, -r)], [], [(0, 1, 2)])
        t = bpy.data.objects.new(f"SM_TriDecal_{side}", tri); COL_P.objects.link(t); t.parent = RIG; t.data.materials.append(pk)
        t.location = loc + nor * 0.004; t.rotation_euler = nor.to_track_quat('X', 'Z').to_euler() if side > 0 else (-nor).to_track_quat('X', 'Z').to_euler()
        sd2 = t.modifiers.new("S", 'SOLIDIFY'); sd2.thickness = 0.003
# closed front: the jacket is open with nobody inside, so loft a front panel between the two front edges
rows = []
for z in np.linspace(0.02, NECK + 0.03, 36):
    row = []
    for x in np.linspace(-0.16, 0.16, 9):
        hit, loc, nor, _ = hood.ray_cast(Vector((x, -2.0, z)), Vector((0, 1, 0)))
        row.append(loc.y if hit else None)
    ys = [v for v in (row[0], row[-1]) if v is not None]
    if not ys: continue
    yf = min(ys) - 0.004
    rows.append([(x, yf - 0.025 * math.cos(x / 0.16 * math.pi / 2), z) for x in np.linspace(-0.16, 0.16, 9)])
if len(rows) > 2:
    vs = [v for r in rows for v in r]; nc = len(rows[0])
    fs = [(i * nc + j, i * nc + j + 1, (i + 1) * nc + j + 1, (i + 1) * nc + j) for i in range(len(rows) - 1) for j in range(nc - 1)]
    pm = bpy.data.meshes.new("front"); pm.from_pydata(vs, [], fs); pm.polygons.foreach_set("use_smooth", [True] * len(fs))
    fp = bpy.data.objects.new("SM_FrontPanel", pm); COL_P.objects.link(fp); fp.parent = RIG; pm.materials.append(fab)
    fp.modifiers.new("Sub", 'SUBSURF').levels = 1
    bpy.context.view_layer.update()
# zip trim on the jacket: a pink tape following the front surface, slightly off-centre (asymmetric techwear zip)
pts = [Vector(((r[3][0] + r[4][0]) / 2, (r[3][1] + r[4][1]) / 2 - 0.006, r[3][2])) for r in rows]
if len(pts) > 4:
    cu = bpy.data.curves.new("zip", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.008; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, q in enumerate(pts): sp.points[i].co = (*q, 1)
    zo = bpy.data.objects.new("SM_ZipTrim", cu); COL_P.objects.link(zo); zo.parent = RIG; cu.materials.append(pk)

# sleeve print: PD-01 (white) + PHILLIPS DIGITAL (pink), shrink-wrapped onto the near sleeve
wh = flat("MAT_PrintWhite", (0.85, 0.86, 0.9), 0.6)
def sleeve_text(body, size, z, mat, y0=0.0, font="/home/user/Motion-Studio/public/fonts/BarlowCondensed-BlackItalic.ttf"):
    cd = bpy.data.curves.new("txt", 'FONT'); cd.body = body; cd.size = size; cd.align_x = 'CENTER'; cd.font = bpy.data.fonts.load(font, check_existing=True)
    t = bpy.data.objects.new("SM_Print_" + body[:6], cd); COL_P.objects.link(t)
    t.location = (-0.6, y0, z); t.rotation_euler = (math.radians(90), 0, math.radians(-90))
    bpy.context.view_layer.objects.active = t; t.select_set(True); bpy.ops.object.convert(target='MESH'); t.select_set(False)
    t.data.materials.append(mat); t.parent = RIG
    sw = t.modifiers.new("Wrap", 'SHRINKWRAP'); sw.target = hood; sw.wrap_method = 'PROJECT'; sw.use_project_x = True; sw.use_negative_direction = True; sw.use_positive_direction = True; sw.offset = 0.004
    sd3 = t.modifiers.new("S", 'SOLIDIFY'); sd3.thickness = 0.002
    return t
sleeve_text("PD-01", 0.12, 0.98, wh, y0=0.0)
sleeve_text("PHILLIPS DIGITAL", 0.04, 0.92, pk, y0=0.0)
# fabric weave + soft wrinkles (bump only)
nt = fab.node_tree; fb = nt.nodes["Principled BSDF"]
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 4.0
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.0; wv.inputs["Distortion"].default_value = 1.0
ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'; nt.links.new(nz.outputs["Fac"], ad.inputs[0]); nt.links.new(wv.outputs["Fac"], ad.inputs[1])
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.01
nt.links.new(ad.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], fb.inputs["Normal"])


# visor streak: a thin strip only the glass reflects
v_ = light("LGT_Visor_Streak", (-1.0, -2.6, FZ + 0.6), 90, 2.0, 0.06, look=(0, -0.2, FZ)); v_.visible_diffuse = False
cam = bpy.data.objects.new("CAM_Profile", bpy.data.cameras.new("CAM_Profile")); S.collection.objects.link(cam); S.camera = cam
cam.data.lens = 50; tgt = bpy.data.objects.new("CAM_T", None); S.collection.objects.link(tgt)
tgt.location = (0, -0.05, FZ - 0.32); cam.location = (-2.9, -0.75, FZ - 0.15); cam.data.shift_x = -0.08
tr = cam.constraints.new('TRACK_TO'); tr.target = tgt; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

S.render.engine = 'CYCLES'; cy = S.cycles; cy.device = 'CPU'; cy.samples = 48; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03
cy.use_denoising = False; cy.diffuse_bounces = 2; cy.glossy_bounces = 4; cy.transmission_bounces = 2; cy.sample_clamp_indirect = 3.0
S.render.resolution_x, S.render.resolution_y = 1280, 720; S.render.film_transparent = True
S.view_settings.view_transform = "Standard"; S.view_settings.exposure = -0.8
try: S.view_settings.look = "None"
except TypeError: pass
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); co_ = ct.nodes.new("CompositorNodeComposite"); ct.links.new(rl.outputs["Image"], co_.inputs["Image"])
if args and args[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=args[1]); print("SAVED")
elif args and args[0] == "wb":
    S.render.engine = 'BLENDER_WORKBENCH'; S.display.shading.light = 'STUDIO'; S.display.shading.color_type = 'MATERIAL'; S.render.film_transparent = False
    S.render.filepath = args[1]; bpy.ops.render.render(write_still=True); print("WB")
