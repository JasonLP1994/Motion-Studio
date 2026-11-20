# CHRISTMAS SNOW GLOBE (16:9, 1920x1080, 30 fps, 300 frames = a 10 s seamless loop) in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/snow_globe.py -- <out.blend> [preview|farm]
# A soft clay toy diorama (rounded tiles, oversized props) in ONE blue colour family with a single warm accent,
# inside a glass snow globe; snow drifts down, a little train laps the track, the camera sways. Loops seamlessly.
# Plan: notes/snow-globe/plan.md. Style grammar from the user's clay-tile reference (no copied content).
# Props: Kenney Holiday Kit (CC0) from inputs/models/kenney-holiday-kit/ (local only), rounded off and recoloured.
import bpy, bmesh, math, random, os, sys, colorsys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import farm_prep
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.join(ROOT, "renders/farm/snow-globe-v1/snow-globe.blend")
MODE = argv[1] if len(argv) > 1 else "preview"
KIT = os.path.join(ROOT, "inputs/models/kenney-holiday-kit/kit/Models/GLB format")

# ---------------- config: every colour, size and timing ----------------
CFG = {
    "fps": 30, "frames": 300, "res": (1920, 1080),
    "col": {   # one blue family + snow + ONE warm accent (glow/gold)
        "backdrop": "#A8CBEF", "floor": "#9EC4EC",
        "tiles": ["#6FA9E6", "#86B8EC", "#5C99DD"], "tile_snow": "#F4F8FD",
        "cabin": "#4F88D6", "cabin_dark": "#3A6CB8", "roof_snow": "#F7FAFE", "door": "#4A7CC0",
        "base": "#3F78C8", "band": "#F4F8FD", "ground_snow": "#E6F0FB", "rail": "#E9F1FA", "sleeper": "#5E93D1",
        "glow": "#FFC970", "gold": "#F2C14E", "snow": "#FFFFFF",
    },
    "blue_hue": 0.588, "blue_sat": 0.62,          # every prop colour is remapped onto this hue (HLS)
    "tile": 1.0, "gap": 0.07, "tile_base_h": 0.42, "tile_dh": [[0.10, 0.00, 0.14], [0.04, 0.12, 0.02], [0.00, 0.06, 0.10]],
    "snow_cap": 0.07, "snow_tiles": [(-1, 1), (1, 0), (0, -1)],   # only some tiles carry a snow cap, the rest show their blue top
    "floor_r": 2.9, "globe_r": 3.18, "glass_card": 1.4, "view": ("Standard", "None"), "glass": 0.035,
    "base_h": 1.35, "base_flare": 1.14,
    "ring_r": 2.5, "train_laps": 1,
    # props: (kit model, tile (i, j), offset on tile (x, y), rotation deg, scale)
    "props": [
        ("tree-snow-a", (-1, 1), (0.05, 0.05), 0, 0.92),
        ("tree-decorated-snow", (1, 1), (0.0, 0.05), 20, 0.82),
        ("tree-snow-b", (-1, 0), (0.0, 0.0), 40, 0.72),
        ("tree-snow-c", (1, 0), (0.18, 0.15), 10, 0.55),
        ("snowman-hat", (-1, -1), (0.0, 0.0), 25, 0.62),
        ("present-a-cube", (0, -1), (-0.18, 0.05), 15, 0.9),
        ("present-b-round", (0, -1), (0.2, -0.12), -10, 0.8),
        ("present-b-cube", (0, -1), (0.12, 0.25), 35, 0.6),
        ("lantern", (0, 0), (-0.25, -0.2), 30, 0.52),
        ("reindeer", (1, -1), (0.0, 0.0), 35, 0.62),
        ("candy-cane-red", (1, 0), (-0.22, -0.2), 30, 1.1),
        ("candy-cane-green", (0, 0), (0.25, 0.22), -20, 1.0),
        ("snow-pile", (0, 0), (0.1, -0.05), 0, 0.55),
    ],
    "train": [("train-locomotive", 0.0), ("train-wagon", 0.62), ("train-wagon-short", 1.12)],   # arc spacing (m)
    "cabin_tile": (0, 1),
    "snow": {"count": 800, "size": (0.022, 0.05), "swirl": 0.12},
    # camera: orbit around the globe (azimuth deg, sway deg, elevation deg, lens mm, target z, distance)
    "cam": {"az": -62.0, "sway": 12.0, "el": 22.0, "lens": 70.0, "target_z": 1.35, "dist": 27.5, "fstop": 5.6}, "prop_scale": 1.22,
}
FPS, N = CFG["fps"], CFG["frames"]
C = CFG["col"]

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = CFG["res"]
F = range(0, N + 2)            # key one frame either side so motion blur at the loop seam is continuous
T_OF = lambda f: (f - 1) / N   # loop phase: frame 1 -> 0, frame 301 -> 1 (= frame 1)

# ---------------- helpers ----------------
def srgb2lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h, a=1.0):
    h = h.lstrip("#"); return tuple(srgb2lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)

def keys(id_data, path, values, count=1, frames=F, interp="LINEAR"):
    ad = id_data.animation_data or id_data.animation_data_create()
    if not ad.action: ad.action = bpy.data.actions.new(f"{id_data.name}_act")
    for i in range(count):
        fc = ad.action.fcurves.find(path, index=i) or ad.action.fcurves.new(path, index=i)
        fc.keyframe_points.add(len(values)); co = []
        for f, v in zip(frames, values): co += [f, float(v[i] if count > 1 else v)]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = interp
        fc.update()

class NT:
    def __init__(self, nt): self.nt = nt
    def n(self, kind, **kw):
        node = self.nt.nodes.new(kind)
        for k, v in kw.items(): setattr(node, k, v)
        return node
    def link(self, a, b): self.nt.links.new(a, b)
    def _in(self, node, i, x):
        if isinstance(x, (int, float, tuple)): node.inputs[i].default_value = x
        else: self.link(x, node.inputs[i])
    def m(self, op, a, b=None, c=None, clamp=False):
        node = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, x in enumerate([a, b, c]):
            if x is not None: self._in(node, i, x)
        return node.outputs[0]
    def combine(self, x, y, z=0.0):
        node = self.n("ShaderNodeCombineXYZ")
        for i, a in enumerate([x, y, z]): self._in(node, i, a)
        return node.outputs[0]
    def sep(self, vec):
        node = self.n("ShaderNodeSeparateXYZ"); self._in(node, 0, vec); return node.outputs

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NT(m.node_tree)

def clay_bsdf(T, base, rough=0.55):
    """soft clay / vinyl toy: matte, faint sheen, a touch of subsurface glow"""
    b = T.n("ShaderNodeBsdfPrincipled")
    if isinstance(base, tuple): b.inputs["Base Color"].default_value = base
    else: T.link(base, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.12
    b.inputs["Subsurface Radius"].default_value = (0.08, 0.10, 0.14)
    b.inputs["Subsurface Scale"].default_value = 0.05
    b.inputs["Sheen Weight"].default_value = 0.25
    b.inputs["Sheen Roughness"].default_value = 0.5
    b.inputs["Coat Weight"].default_value = 0.08
    b.inputs["Coat Roughness"].default_value = 0.35
    return b

def out(T, surf):
    o = T.n("ShaderNodeOutputMaterial"); T.link(surf, o.inputs["Surface"])

MATS = {}
def clay(hexcol, rough=0.55):
    if hexcol in MATS: return MATS[hexcol]
    m, T = new_mat(f"clay_{hexcol}")
    out(T, clay_bsdf(T, hexc(hexcol), rough).outputs[0]); MATS[hexcol] = m; return m

def glow_mat(name, hexcol, strength):
    m, T = new_mat(name)
    e = T.n("ShaderNodeEmission"); e.inputs["Color"].default_value = hexc(hexcol); e.inputs["Strength"].default_value = strength
    out(T, e.outputs[0]); return m

def link_obj(name, me):
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); return o

def obj_from_bm(name, bm, mat, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); return link_obj(name, me)

def rbox(name, size, loc, mat, r=0.08, seg=5, rot=0.0):
    """rounded box (real bevelled geometry) - the clay tile look"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    r = min(r, 0.49 * min(size))
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; o.rotation_euler.z = math.radians(rot); return o

def prism(name, w, d, h, loc, mat, r=0.03, rot=0.0):
    """gable roof block: triangle in X-Z, extruded along Y, edges rounded"""
    bm = bmesh.new()
    pts = [(-w / 2, 0), (w / 2, 0), (0, h)]
    vs = [bm.verts.new((x, y, z)) for y in (-d / 2, d / 2) for (x, z) in pts]
    bm.faces.new([vs[0], vs[1], vs[2]]); bm.faces.new([vs[5], vs[4], vs[3]])
    for a, b in ((0, 1), (1, 2), (2, 0)): bm.faces.new([vs[a], vs[a + 3], vs[b + 3], vs[b]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=4, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; o.rotation_euler.z = math.radians(rot); return o

def cyl(name, r, h, loc, mat, seg=96, bevel=0.0, flare=1.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r * flare, radius2=r, depth=h)
    if bevel: bmesh.ops.bevel(bm, geom=[e for e in bm.edges if not e.is_manifold or abs(e.calc_face_angle(0)) > 0.5],
                              offset=bevel, segments=6, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; return o

def smooth_normals(o, angle=50):
    o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(angle)

# ---------------- tile grid (3 x 3 rounded clay tiles with snow caps) ----------------
P = CFG["tile"] + CFG["gap"]
TOP = {}
for j in (-1, 0, 1):
    for i in (-1, 0, 1):
        h = CFG["tile_base_h"] + CFG["tile_dh"][1 - j][i + 1]
        col = CFG["col"]["tiles"][(i + j) % 3]
        x, y = i * P, j * P
        rbox(f"tile_{i}_{j}", (CFG["tile"], CFG["tile"], h), (x, y, h / 2 + 0.10), clay(col), r=0.15, seg=6)
        cap = CFG["snow_cap"]
        if (i, j) in CFG["snow_tiles"]:
            rbox(f"tilesnow_{i}_{j}", (CFG["tile"] * 0.94, CFG["tile"] * 0.94, cap * 2), (x, y, 0.10 + h + cap * 0.35), clay(C["tile_snow"], 0.7), r=0.06)
            TOP[(i, j)] = (x, y, 0.10 + h + cap * 1.35)
        else:
            TOP[(i, j)] = (x, y, 0.10 + h)

# ---------------- clay cabin (built in code, like the reference house) ----------------
def cabin(tile):
    x, y, z = TOP[tile]; w, d, h = 0.62, 0.50, 0.42; rot = 8
    body = rbox("cabin_body", (w, d, h), (x, y, z + h / 2), clay(C["cabin"]), r=0.06)
    roof = prism("cabin_roof", w + 0.22, d + 0.16, 0.34, (x, y, z + h - 0.02), clay(C["roof_snow"], 0.65), r=0.045)
    chim = rbox("cabin_chimney", (0.10, 0.10, 0.24), (x + 0.16, y + 0.08, z + h + 0.22), clay(C["cabin_dark"]), r=0.025)
    cap = rbox("cabin_chimney_snow", (0.13, 0.13, 0.04), (x + 0.16, y + 0.08, z + h + 0.345), clay(C["roof_snow"], 0.65), r=0.018)
    door = rbox("cabin_door", (0.15, 0.04, 0.24), (x, y - d / 2 - 0.005, z + 0.12), clay(C["door"]), r=0.02)
    knob = rbox("cabin_knob", (0.025, 0.02, 0.025), (x + 0.045, y - d / 2 - 0.03, z + 0.12), clay(C["gold"], 0.35), r=0.01)
    glow = glow_mat("window_glow", C["glow"], 6.0)
    parts = [body, roof, chim, cap, door, knob]
    for k, wx in enumerate((-0.19, 0.19)):
        frame = rbox(f"cabin_win_frame{k}", (0.13, 0.03, 0.13), (x + wx, y - d / 2 - 0.004, z + 0.25), clay(C["roof_snow"], 0.6), r=0.02)
        pane = rbox(f"cabin_win{k}", (0.095, 0.03, 0.095), (x + wx, y - d / 2 - 0.012, z + 0.25), glow, r=0.015)
        parts += [frame, pane]
    # gable round window
    gw = rbox("cabin_gable_win", (0.08, 0.03, 0.08), (x, y - d / 2 - 0.07, z + h + 0.11), glow, r=0.035)
    parts.append(gw)
    R = Matrix.Rotation(math.radians(rot), 3, "Z")
    for p_ in parts:   # rotate the whole cabin about the tile centre
        k_ = CFG["prop_scale"]; rel = R @ Vector((p_.location.x - x, p_.location.y - y, 0.0)) * k_
        p_.location = (x + rel.x, y + rel.y, z + (p_.location.z - z) * k_); p_.rotation_euler.z += math.radians(rot); p_.scale = (k_,) * 3
    return parts
CABIN = cabin(CFG["cabin_tile"])

# ---------------- Kenney props: import, round off, recolour onto the blue family ----------------
cm_img = bpy.data.images.load(os.path.join(KIT, "Textures", "colormap.png"), check_existing=True)
CW, CH = cm_img.size; CPX = list(cm_img.pixels)    # sRGB-encoded byte image -> values are display (sRGB) 0..1

def remap(rgb):
    """map a kit colour onto the one blue family; keep whites as snow; yellows/oranges = the one warm accent"""
    r, g, b = rgb; h, l, s = colorsys.rgb_to_hls(r, g, b); Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if s < 0.18 and Y > 0.78: return colorsys.hls_to_rgb(CFG["blue_hue"], min(0.97, 0.88 + 0.1 * Y), 0.55), 0.0     # snow
    if 0.07 < h < 0.17 and s > 0.45 and l > 0.35: return (0.95, 0.76, 0.31), 1.0                                      # gold accent (glows a little)
    L = 0.30 + 0.62 * Y ** 0.85
    hh = CFG["blue_hue"] + 0.025 * math.sin(2 * math.pi * h)
    return colorsys.hls_to_rgb(hh, L, CFG["blue_sat"] * (0.6 + 0.4 * min(1, s * 1.5))), 0.0

def attr_mat():
    if "clay_attr" in MATS: return MATS["clay_attr"]
    m, T = new_mat("clay_attr")
    a = T.n("ShaderNodeAttribute", attribute_name="Col")
    g = T.n("ShaderNodeAttribute", attribute_name="glow")
    b = clay_bsdf(T, a.outputs["Color"])
    e = T.n("ShaderNodeEmission"); e.inputs["Color"].default_value = hexc(C["glow"])
    st = T.n("ShaderNodeValue"); st.name = "gold_glow"; st.outputs[0].default_value = 1.5
    T.link(T.m("MULTIPLY", g.outputs["Fac"], st.outputs[0]), e.inputs["Strength"])
    add = T.n("ShaderNodeAddShader"); T.link(b.outputs[0], add.inputs[0]); T.link(e.outputs[0], add.inputs[1])
    out(T, add.outputs[0]); MATS["clay_attr"] = m; return m

def kit(name, loc, rot, scale, label=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(KIT, name + ".glb"))
    new = [o for o in bpy.data.objects if o not in before]
    new_names = [o.name for o in new]
    meshes = [o for o in new if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    if len(meshes) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    for nm in new_names:
        e = bpy.data.objects.get(nm)
        if e is not None and nm != o.name: bpy.data.objects.remove(e, do_unlink=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = o.data
    # per-face colour from the kit's colour swatch, remapped
    uv = me.uv_layers.active.data; cols, glows = [], []
    for p in me.polygons:
        u = sum(uv[li].uv.x for li in p.loop_indices) / p.loop_total; v = sum(uv[li].uv.y for li in p.loop_indices) / p.loop_total
        px = min(CW - 1, max(0, int(u * CW))); py = min(CH - 1, max(0, int(v * CH))); k = (py * CW + px) * 4
        c, gl = remap(tuple(CPX[k:k + 3])); cols.append(c); glows.append(gl)
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER"); data = []
    for p, c in zip(me.polygons, cols):
        lc = tuple(srgb2lin(x) for x in c) + (1.0,)
        for _ in p.loop_indices: data += lc
    ca.data.foreach_set("color", data)
    ga = me.attributes.new("glow", "FLOAT", "FACE"); ga.data.foreach_set("value", glows)
    # weld the flat-shaded faces, then round every edge off (clay toy)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.clear(); me.materials.append(attr_mat())
    smooth_normals(o, 60)
    bv = o.modifiers.new("round", "BEVEL"); bv.width = 0.035; bv.segments = 3; bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(30)
    bv.harden_normals = False; bv.profile = 0.6
    sd = o.modifiers.new("soft", "SUBSURF"); sd.levels = 1; sd.render_levels = 2
    o.name = label or name
    o.location = loc; o.rotation_euler.z = math.radians(rot); o.scale = (scale,) * 3
    return o

PROPS = []
for name, tile, off, rot, s in CFG["props"]:
    x, y, z = TOP[tile]
    PROPS.append(kit(name, (x + off[0], y + off[1], z - 0.01), rot + CFG["cam"]["az"] + 90, s * CFG["prop_scale"]))
gg = MATS["clay_attr"].node_tree.nodes["gold_glow"]

# ---------------- globe: snowy floor, ring track, glass dome, base ----------------
FR, GR = CFG["floor_r"], CFG["globe_r"]
GC = math.sqrt(GR ** 2 - FR ** 2)                       # dome centre height so it meets the floor at radius FR
# snowy floor disc with soft lumps
bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=128, radius=FR - 0.01)
bmesh.ops.triangulate(bm, faces=bm.faces)
for _ in range(4): bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
rnd = random.Random(3)
bumps = [(rnd.uniform(-FR, FR), rnd.uniform(-FR, FR), rnd.uniform(0.25, 0.7), rnd.uniform(0.02, 0.07)) for _ in range(40)]
for v in bm.verts:
    rr = math.hypot(v.co.x, v.co.y); edge = max(0.0, 1 - rr / FR)
    zz = 0.10 * min(1.0, edge * 6)
    for bx, by, br, bh in bumps: zz += bh * math.exp(-((v.co.x - bx) ** 2 + (v.co.y - by) ** 2) / (br * br)) * min(1, edge * 4)
    v.co.z = zz
floor = obj_from_bm("globe_floor", bm, clay(C["ground_snow"], 0.75))

# ring track: two rails + sleepers
RR = CFG["ring_r"]
for k, dr in enumerate((-0.085, 0.085)):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, segments=192, radius=RR + dr)
    me = bpy.data.meshes.new(f"rail{k}"); bm.to_mesh(me); bm.free()
    cu_o = link_obj(f"rail{k}", me); cu_o.location.z = 0.13
    sk = cu_o.modifiers.new("skin", "SKIN")
    for sv in me.skin_vertices[0].data: sv.radius = (0.018, 0.018)
    ss = cu_o.modifiers.new("s", "SUBSURF"); ss.levels = 1; ss.render_levels = 2
    me.materials.append(clay(C["rail"], 0.35))
    for p in me.polygons: p.use_smooth = True
for k in range(40):
    a = 2 * math.pi * k / 40
    rbox(f"sleeper{k}", (0.07, 0.26, 0.035), (RR * math.cos(a), RR * math.sin(a), 0.11), clay(C["sleeper"]), r=0.015, rot=math.degrees(a))

# glass dome: thin shell, refracts for the camera but lets light and shadow through (no dark interior)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=64, radius=GR)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -GC), plane_no=(0, 0, -1), clear_inner=False, clear_outer=True)
gm, T = new_mat("glass")
gl = T.n("ShaderNodeBsdfPrincipled"); gl.inputs["Base Color"].default_value = (0.97, 0.985, 1.0, 1)
gl.inputs["Roughness"].default_value = 0.02; gl.inputs["IOR"].default_value = 1.45; gl.inputs["Transmission Weight"].default_value = 1.0
tr = T.n("ShaderNodeBsdfTransparent")
lp = T.n("ShaderNodeLightPath")
fac = T.m("MAXIMUM", lp.outputs["Is Shadow Ray"], lp.outputs["Is Diffuse Ray"])
mix = T.n("ShaderNodeMixShader"); T.link(fac, mix.inputs[0]); T.link(gl.outputs[0], mix.inputs[1]); T.link(tr.outputs[0], mix.inputs[2])
out(T, mix.outputs[0])
dome = obj_from_bm("glass_dome", bm, gm); dome.location.z = GC
so = dome.modifiers.new("shell", "SOLIDIFY"); so.thickness = CFG["glass"]; so.offset = 1.0

# base: flared rounded drum + a white band
BH = CFG["base_h"]
base = cyl("base", FR + 0.22, BH, (0, 0, -BH / 2 + 0.06), clay(C["base"], 0.45), bevel=0.10, flare=CFG["base_flare"])
band = cyl("base_band", FR + 0.22 * 1.0 + 0.10, 0.22, (0, 0, -BH * 0.52 + 0.06), clay(C["band"], 0.5), bevel=0.06, flare=1.05)
lip = cyl("base_lip", FR + 0.06, 0.12, (0, 0, 0.02), clay(C["base"], 0.45), bevel=0.05)
for ob in (base, band, lip): smooth_normals(ob, 40)
GROUND = -BH + 0.06

# ---------------- the train: one lap per loop ----------------
TRAIN = []
for name, arc in CFG["train"]:
    t = kit(name, (0, 0, 0), 0, 0.85, label=name)
    TRAIN.append((t, arc / RR))
for t, da in TRAIN:
    locs, rots = [], []
    for f in F:
        a = 2 * math.pi * CFG["train_laps"] * T_OF(f) - da
        locs.append((RR * math.cos(a), RR * math.sin(a), 0.135)); rots.append(a + math.pi)   # nose along the direction of travel
    keys(t, "location", locs, 3); keys(t, "rotation_euler", [(0, 0, r) for r in rots], 3)

# ---------------- snow inside the globe (geometry nodes, loops every 10 s) ----------------
def snow_nodes():
    ng = bpy.data.node_groups.new("snowfall", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    T = NT(ng); S = CFG["snow"]
    idx = T.n("GeometryNodeInputIndex").outputs[0]
    def rnd(seed, lo=0.0, hi=1.0):
        r = T.n("FunctionNodeRandomValue", data_type="FLOAT"); r.inputs[2].default_value = lo; r.inputs[3].default_value = hi
        T.link(idx, r.inputs["ID"]); r.inputs["Seed"].default_value = seed; return r.outputs[1]
    st = T.n("GeometryNodeInputSceneTime").outputs["Frame"]
    t = T.m("DIVIDE", T.m("SUBTRACT", st, 1.0), float(N))                       # 0..1 over the loop
    H = 2 * GR; zmin = GC - GR
    x0, y0, z0 = rnd(1, -GR, GR), rnd(2, -GR, GR), rnd(3, 0.0, H)
    k = T.m("ADD", T.m("FLOOR", rnd(4, 0.0, 1.999)), 1.0)                         # falls 1 or 2 globe-heights per loop
    zz = T.m("SUBTRACT", z0, T.m("MULTIPLY", T.m("MULTIPLY", k, H), t))
    zz = T.m("ADD", T.m("SUBTRACT", zz, T.m("MULTIPLY", H, T.m("FLOOR", T.m("DIVIDE", zz, H)))), zmin)
    ph = T.m("MULTIPLY", T.m("ADD", T.m("MULTIPLY", t, T.m("ADD", T.m("FLOOR", rnd(5, 0.0, 1.999)), 1.0)), rnd(6)), 2 * math.pi)
    sw = rnd(7, 0.3, 1.0)
    xx = T.m("ADD", x0, T.m("MULTIPLY", T.m("SINE", ph), T.m("MULTIPLY", sw, S["swirl"])))
    yy = T.m("ADD", y0, T.m("MULTIPLY", T.m("COSINE", ph), T.m("MULTIPLY", sw, S["swirl"])))
    pos = T.combine(xx, yy, zz)
    pts = T.n("GeometryNodePoints"); pts.inputs["Count"].default_value = S["count"]; T.link(pos, pts.inputs["Position"])
    # fade the flake out near the glass and the floor (no popping)
    dx, dy, dz = xx, yy, T.m("SUBTRACT", zz, GC)
    d = T.m("SQRT", T.m("ADD", T.m("ADD", T.m("MULTIPLY", dx, dx), T.m("MULTIPLY", dy, dy)), T.m("MULTIPLY", dz, dz)))
    f1 = T.m("DIVIDE", T.m("SUBTRACT", GR - 0.12, d), 0.35, clamp=True)
    f2 = T.m("DIVIDE", T.m("SUBTRACT", zz, 0.25), 0.35, clamp=True)
    size = T.m("MULTIPLY", T.m("MULTIPLY", f1, f2), rnd(8, S["size"][0], S["size"][1]))
    ico = T.n("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 1.0; ico.inputs["Subdivisions"].default_value = 2
    inst = T.n("GeometryNodeInstanceOnPoints")
    T.link(pts.outputs[0], inst.inputs["Points"]); T.link(ico.outputs[0], inst.inputs["Instance"])
    T.link(size, inst.inputs["Scale"])
    real = T.n("GeometryNodeRealizeInstances"); T.link(inst.outputs[0], real.inputs[0])
    sm = T.n("GeometryNodeSetMaterial"); T.link(real.outputs[0], sm.inputs["Geometry"])
    sm.inputs["Material"].default_value = SNOWMAT
    shd = T.n("GeometryNodeSetShadeSmooth"); T.link(sm.outputs[0], shd.inputs[0])
    o_ = T.n("NodeGroupOutput"); T.link(shd.outputs[0], o_.inputs[0])
    return ng
SNOWMAT, Tm = new_mat("snowflake")
sb = clay_bsdf(Tm, hexc(C["snow"]), 0.6); sb.inputs["Subsurface Weight"].default_value = 0.4
em = Tm.n("ShaderNodeEmission"); em.inputs["Color"].default_value = hexc(C["snow"]); em.inputs["Strength"].default_value = 0.35
ad = Tm.n("ShaderNodeAddShader"); Tm.link(sb.outputs[0], ad.inputs[0]); Tm.link(em.outputs[0], ad.inputs[1]); out(Tm, ad.outputs[0])
snow_me = bpy.data.meshes.new("snow"); snow = link_obj("snow", snow_me)
gn = snow.modifiers.new("snowfall", "NODES"); gn.node_group = snow_nodes()

# ---------------- twinkle: window glow + gold accents (periods divide the loop) ----------------
keys(bpy.data.materials["window_glow"].node_tree, 'nodes["Emission"].inputs[1].default_value',
     [6.0 * (0.88 + 0.12 * math.sin(2 * math.pi * 4 * T_OF(f)) ** 2) for f in F])
keys(MATS["clay_attr"].node_tree, 'nodes["gold_glow"].outputs[0].default_value',
     [1.2 + 1.0 * max(0.0, math.sin(2 * math.pi * 2 * T_OF(f))) ** 4 for f in F])

# ---------------- set: soft powder-blue cyclorama, soft lights ----------------
bm = bmesh.new(); W_, D_, Hh, Rc = 80.0, 40.0, 30.0, 10.0
prof = [(-D_, 0.0)] + [(Rc * math.sin(a) + 0.0, Rc - Rc * math.cos(a)) for a in [i * (math.pi / 2) / 16 for i in range(17)]] + [(Rc, Hh)]
rows = []
for xx in (-W_ / 2, W_ / 2):
    rows.append([bm.verts.new((xx, py + 8.0, pz + GROUND)) for (py, pz) in prof])
for k in range(len(prof) - 1): bm.faces.new([rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]])
cyc = obj_from_bm("cyclorama", bm, clay(C["backdrop"], 0.9))
cs = cyc.modifiers.new("s", "SUBSURF"); cs.levels = 1; cs.render_levels = 2
cyc.rotation_euler.z = math.radians(CFG["cam"]["az"] + 90)   # the curve sits behind the globe as seen from the camera

def area(name, loc, size, energy, col=(1, 1, 1), glossy=False):
    ld = bpy.data.lights.new(name, "AREA"); ld.size = size; ld.energy = energy; ld.color = col; ld.shape = "RECTANGLE"; ld.size_y = size * 0.6
    lo = link_obj(name, ld); lo.location = loc; lo.visible_camera = False; lo.visible_glossy = glossy
    d = Vector((0, 0, GC * 0.6)) - Vector(loc); lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return lo
az = math.radians(CFG["cam"]["az"])
def around(a_deg, r, z): a = az + math.radians(a_deg); return (r * math.cos(a), r * math.sin(a), z)
area("key", around(-40, 14, 12), 7.0, 2600, (1.0, 0.97, 0.93))
area("fill", around(70, 14, 5), 10.0, 900, (0.86, 0.92, 1.0))
area("rim", around(170, 12, 11), 6.0, 1800, (0.92, 0.96, 1.0))
area("top", (0, 0, 16), 6.0, 700)

# soft studio highlight on the glass: a glowing card seen ONLY in reflections, with feathered edges (no hard boxes)
def reflect_card(name, a_deg, el_deg, dist, w, h, strength):
    bm_ = bmesh.new(); bmesh.ops.create_grid(bm_, x_segments=1, y_segments=1, size=0.5)
    for v in bm_.verts: v.co.x *= w; v.co.y *= h
    m_, T_ = new_mat(name)
    tc = T_.n("ShaderNodeTexCoord"); g_ = T_.n("ShaderNodeTexGradient", gradient_type="QUADRATIC_SPHERE")
    mp = T_.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.0, 2.0, 1.0); mp.inputs["Location"].default_value = (-1.0, -1.0, 0.0)
    T_.link(tc.outputs["UV"], mp.inputs[0]); T_.link(mp.outputs[0], g_.inputs[0])
    e_ = T_.n("ShaderNodeEmission"); e_.inputs["Color"].default_value = (1, 1, 1, 1)
    fall = T_.m("POWER", g_.outputs["Fac"], 2.5)      # very soft feathered edge
    T_.link(T_.m("MULTIPLY", fall, strength), e_.inputs["Strength"])
    tp = T_.n("ShaderNodeBsdfTransparent"); mx = T_.n("ShaderNodeMixShader")
    T_.link(fall, mx.inputs[0]); T_.link(tp.outputs[0], mx.inputs[1]); T_.link(e_.outputs[0], mx.inputs[2]); out(T_, mx.outputs[0])
    ob = obj_from_bm(name, bm_, m_, smooth=False)
    me_ = ob.data; me_.uv_layers.new(name="UVMap")
    a = az + math.radians(a_deg); el = math.radians(el_deg)
    ob.location = (dist * math.cos(el) * math.cos(a), dist * math.cos(el) * math.sin(a), GC + dist * math.sin(el))
    ob.rotation_euler = (Vector((0, 0, GC)) - ob.location).to_track_quat("Z", "Y").to_euler()
    ob.visible_camera = False; ob.visible_diffuse = False; ob.visible_shadow = False; ob.visible_transmission = False; ob.visible_volume_scatter = False
    return ob
reflect_card("glass_card_key", -32, 42, 11, 10.0, 5.0, CFG["glass_card"])
reflect_card("glass_card_rim", 150, 25, 11, 5.0, 9.0, CFG["glass_card"] * 0.4)

wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
bgn = wd.node_tree.nodes["Background"]; bgn.inputs[0].default_value = hexc("#CFE3F7"); bgn.inputs[1].default_value = 0.45

# ---------------- camera: gentle sway around the globe (one sine cycle per loop) ----------------
cc = CFG["cam"]
cd = bpy.data.cameras.new("cam"); cd.lens = cc["lens"]; cd.sensor_width = 36; cd.clip_start = 0.1; cd.clip_end = 300
cam = link_obj("cam", cd); sc.camera = cam
tgt = link_obj("cam_target", None); tgt.location = (0, 0, cc["target_z"])
tr_ = cam.constraints.new("TRACK_TO"); tr_.target = tgt; tr_.track_axis = "TRACK_NEGATIVE_Z"; tr_.up_axis = "UP_Y"
cd.dof.use_dof = True; cd.dof.focus_object = tgt; cd.dof.aperture_fstop = cc["fstop"]
pos = []
for f in F:
    a = math.radians(cc["az"] + cc["sway"] * math.sin(2 * math.pi * T_OF(f))); el = math.radians(cc["el"])
    pos.append((cc["dist"] * math.cos(el) * math.cos(a), cc["dist"] * math.cos(el) * math.sin(a), cc["target_z"] + cc["dist"] * math.sin(el)))
keys(cam, "location", pos, 3)

# ---------------- render settings ----------------
sc.render.engine = "CYCLES"; cy = sc.cycles
cy.max_bounces = 12; cy.diffuse_bounces = 4; cy.glossy_bounces = 6; cy.transmission_bounces = 10; cy.transparent_max_bounces = 16
cy.volume_bounces = 0; cy.caustics_reflective = False; cy.caustics_refractive = False; cy.sample_clamp_indirect = 6.0
cy.use_animated_seed = True
if MODE == "preview":
    cy.max_bounces = 8; cy.diffuse_bounces = 2; cy.glossy_bounces = 3
sc.view_settings.view_transform = CFG["view"][0]
try: sc.view_settings.look = CFG["view"][1]
except TypeError: pass
sc.render.film_transparent = False
sc.use_nodes = True; ct = sc.node_tree
for n_ in list(ct.nodes): ct.nodes.remove(n_)
rl_ = ct.nodes.new("CompositorNodeRLayers"); gl_ = ct.nodes.new("CompositorNodeGlare"); co_ = ct.nodes.new("CompositorNodeComposite")
gl_.glare_type = "FOG_GLOW"; gl_.threshold = 1.0; gl_.mix = -0.8; gl_.quality = "MEDIUM"; gl_.size = 7   # soft halo on the warm windows only
ct.links.new(rl_.outputs["Image"], gl_.inputs["Image"]); ct.links.new(gl_.outputs["Image"], co_.inputs["Image"])
farm_prep.prepare(sc, OUT, samples=128 if MODE == "farm" else 48, frames=(1, N), name="snow_globe", fps=FPS, motion_blur=(MODE == "farm"))
