# CHRISTMAS SNOW GLOBE (16:9, 1920x1080, 30 fps, 300 frames = a 10 s seamless loop) in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/snow_globe.py -- <out.blend> [preview|farm]
# A connected clay-toy mini town (flush rounded tiles, a winding icy path, a town square with the tree, three houses)
# in ONE blue colour family with a single warm accent, inside a glass snow globe on a soft snow mound. Snow drifts
# down, the lights twinkle, the camera sways. Everything loops seamlessly. Infinite soft pastel-blue backdrop.
# Plan: notes/snow-globe/plan.md. Style grammar from references/snow-globe/ (no copied content).
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

# ---------------- config: every colour, size, place and timing ----------------
CFG = {
    "fps": 30, "frames": 300, "res": (1920, 1080),
    "col": {   # one blue family + snow + ONE warm accent (glow/gold)
        "backdrop": "#C4DEF7", "world": "#DCEBFA",
        "tiles": ["#6FA9E6", "#86B8EC", "#5C99DD"], "tile_snow": "#EEF5FD", "path": "#7DB2EA", "plaza": "#94C1EE",
        "house": ["#4F88D6", "#6A9EE0", "#3F78C8"], "house_dark": "#355FA8", "roof_snow": "#F7FAFE", "door": "#3E6DB5",
        "base": "#3F78C8", "band": "#F4F8FD", "ground_snow": "#F2F7FD",
        "glow": "#FFC970", "gold": "#F2C14E", "snow": "#FFFFFF",
    },
    "blue_hue": 0.588, "blue_sat": 0.62,          # every prop colour is remapped onto this hue (HLS)
    "tile": 1.05, "gap": 0.03, "tile_base_h": 0.42, "prop_scale": 1.2,   # prop_scale: every house and prop on the tiles
    "tile_dh": {(-1, 1): 0.10, (0, 1): 0.04, (1, 1): 0.12, (-1, 0): 0.06, (0, 0): 0.0, (1, 0): 0.03,
                (-1, -1): 0.08, (0, -1): 0.0, (1, -1): 0.10},
    "snow_cap": 0.06,
    # the path: which tile edges each tile's path runs to (N = +y, S = -y, E = +x, W = -x); "*" = round town square
    "path": {(0, -1): "SN", (0, 0): "SNWE*", (0, 1): "S", (-1, 0): "E", (1, 0): "WN", (1, 1): "S"},
    "path_w": 0.30,
    # houses: (tile, offset, (w, d, h), roof height, colour index, facing deg (0 = door to -y), steeple)
    "houses": [((0, 1), (0.0, 0.10), (0.70, 0.56, 0.48), 0.38, 0, 0, False),
               ((-1, 0), (-0.10, 0.0), (0.62, 0.52, 0.42), 0.34, 1, 90, False),
               ((1, 1), (0.0, 0.12), (0.56, 0.60, 0.56), 0.36, 2, 0, True)],
    # props: (kit model, tile, offset on tile, rotation deg, scale, absolute rotation?)  (relative = turned to camera)
    "props": [
        ("tree-decorated-snow", (0, 0), (0.0, 0.02), 0, 0.62, False),
        ("present-a-cube", (0, 0), (-0.27, -0.27), 15, 0.55, False),
        ("present-b-round", (0, 0), (0.28, -0.26), -10, 0.5, False),
        ("tree-snow-a", (-1, 1), (-0.12, 0.12), 0, 0.72, False),
        ("tree-snow-b", (-1, 1), (0.25, -0.18), 30, 0.52, False),
        ("tree-snow-c", (-1, 1), (0.27, 0.3), 10, 0.38, False),
        ("snowman-hat", (-1, -1), (0.02, 0.0), 25, 0.56, False),
        ("snow-pile", (-1, -1), (0.25, 0.25), 0, 0.35, False),
        ("tree-snow-b", (1, -1), (0.26, 0.26), 0, 0.45, False),
        ("reindeer", (1, -1), (-0.15, -0.14), 30, 0.48, False),
        ("tree-snow-c", (1, -1), (-0.27, 0.3), 0, 0.34, False),
        ("lantern", (0, -1), (0.3, -0.12), 0, 0.42, False),
        ("candy-cane-red", (0, -1), (-0.3, 0.22), 30, 0.9, False),
        ("bench", (1, 0), (0.24, -0.22), -135, 0.42, True),
        ("lantern", (1, 0), (-0.3, 0.3), 0, 0.42, False),
        ("tree-snow-c", (-1, 0), (-0.32, 0.33), 0, 0.36, False),
        ("tree-snow-c", (0, 1), (0.36, -0.3), 0, 0.34, False),
        ("sled", (0, 1), (-0.3, -0.3), 40, 0.38, False),
        ("tree-snow-b", (1, 1), (0.32, -0.3), 0, 0.36, False),
    ],
    "floor_r": 2.45, "globe_r": 2.75, "glass": 0.035, "glass_card": 1.2,
    "mound": 0.20,                                   # snow mound height at the centre (m)
    "base_h": 1.25, "base_flare": 1.14,
    "view": ("Standard", "None"),
    "light": {"key": 2300, "fill": 700, "back": 700, "world": 0.55},
    "snow": {"count": 700, "size": (0.014, 0.032), "swirl": 0.10},
    # camera: orbit around the globe (azimuth deg, sway deg, elevation deg, lens mm, target z, distance)
    "cam": {"az": -62.0, "sway": 10.0, "el": 33.0, "lens": 70.0, "target_z": 1.1, "dist": 14.0, "fstop": 8.0}   # close like the reference: the town fills ~60% of the width,
}
FPS, N = CFG["fps"], CFG["frames"]
C = CFG["col"]

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = CFG["res"]
F = range(0, N + 2)            # key one frame either side so motion blur at the loop seam is continuous
T_OF = lambda f: (f - 1) / N   # loop phase: frame 1 -> 0, frame 301 -> 1 (= frame 1)
AZ = math.radians(CFG["cam"]["az"])
FACE = CFG["cam"]["az"] + 90   # rotation that turns a kit model (front = -y) towards the camera

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

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NT(m.node_tree)

def clay_bsdf(T, base, rough=0.55, sss=0.12):
    """soft clay / vinyl toy: matte, faint sheen, a touch of subsurface glow"""
    b = T.n("ShaderNodeBsdfPrincipled")
    if isinstance(base, tuple): b.inputs["Base Color"].default_value = base
    else: T.link(base, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = sss
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
    key = (hexcol, rough)
    if key in MATS: return MATS[key]
    m, T = new_mat(f"clay_{hexcol}_{rough}")
    out(T, clay_bsdf(T, hexc(hexcol), rough).outputs[0]); MATS[key] = m; return m

def snow_mat():
    """soft powder snow: white, very matte, deep subsurface, fine grain bump"""
    if "snowmat" in MATS: return MATS["snowmat"]
    m, T = new_mat("snow_ground")
    b = clay_bsdf(T, hexc(C["ground_snow"]), 0.85, sss=0.35); b.inputs["Subsurface Radius"].default_value = (0.2, 0.25, 0.35)
    b.inputs["Sheen Weight"].default_value = 0.4
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60.0; nz.inputs["Detail"].default_value = 3.0
    bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.01
    T.link(nz.outputs["Fac"], bp.inputs["Height"]); T.link(bp.outputs["Normal"], b.inputs["Normal"])
    out(T, b.outputs[0]); MATS["snowmat"] = m; return m

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
    if mat: me.materials.append(mat)
    return link_obj(name, me)

def rbox(name, size, loc, mat, r=0.08, seg=5, rot=0.0):
    """rounded box (real bevelled geometry) - the clay tile look"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    r = min(r, 0.49 * min(size))
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; o.rotation_euler.z = math.radians(rot); return o

def prism(name, w, d, h, loc, mat, r=0.03):
    """gable roof block: triangle in X-Z, extruded along Y, edges rounded"""
    bm = bmesh.new()
    pts = [(-w / 2, 0), (w / 2, 0), (0, h)]
    vs = [bm.verts.new((x, y, z)) for y in (-d / 2, d / 2) for (x, z) in pts]
    bm.faces.new([vs[0], vs[1], vs[2]]); bm.faces.new([vs[5], vs[4], vs[3]])
    for a, b in ((0, 1), (1, 2), (2, 0)): bm.faces.new([vs[a], vs[a + 3], vs[b + 3], vs[b]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=4, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; return o

def pyramid(name, w, h, loc, mat, r=0.015):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=w * 0.7071, radius2=0.0, depth=h)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 4, 3, "Z"))
    bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=3, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; return o

def cyl(name, r, h, loc, mat, seg=96, bevel=0.0, flare=1.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r * flare, radius2=r, depth=h)
    if bevel: bmesh.ops.bevel(bm, geom=[e for e in bm.edges if abs(e.calc_face_angle(0)) > 0.5],
                              offset=bevel, segments=6, profile=0.5, affect="EDGES", clamp_overlap=True)
    o = obj_from_bm(name, bm, mat); o.location = loc; return o

def smooth_normals(o, angle=50):
    o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(angle)

def group(parts, pivot, rot_deg):
    """turn a set of parts about a vertical axis through pivot"""
    R = Matrix.Rotation(math.radians(rot_deg), 3, "Z")
    for p_ in parts:
        rel = R @ Vector((p_.location.x - pivot[0], p_.location.y - pivot[1], 0.0))
        p_.location = (pivot[0] + rel.x, pivot[1] + rel.y, p_.location.z); p_.rotation_euler.z += math.radians(rot_deg)

# ---------------- the snow mound inside the globe (smooth, rounded rim tucked into the glass) ----------------
FR, GR = CFG["floor_r"], CFG["globe_r"]
GC = math.sqrt(GR ** 2 - FR ** 2)                   # dome centre height: the dome meets z = 0 at radius FR
def mound_z(r, a=0.0):
    u = min(1.0, r / (FR - 0.01))
    z = 0.035 + (CFG["mound"] - 0.035) * (1 - u ** 3) ** 0.5           # soft dome with a rounded rim
    z += 0.012 * math.sin(3 * a + 1.3) * math.sin(math.pi * u) + 0.008 * math.sin(5 * a + r * 2.1) * math.sin(math.pi * u)
    return z
bm = bmesh.new(); SEG, RINGS = 160, 40
rings = []
centre = bm.verts.new((0, 0, mound_z(0)))
for k in range(1, RINGS + 1):
    r = (FR - 0.01) * (k / RINGS) ** 0.8
    rings.append([bm.verts.new((r * math.cos(2 * math.pi * s / SEG), r * math.sin(2 * math.pi * s / SEG), mound_z(r, 2 * math.pi * s / SEG))) for s in range(SEG)])
for s in range(SEG): bm.faces.new([centre, rings[0][s], rings[0][(s + 1) % SEG]])
for k in range(RINGS - 1):
    for s in range(SEG): bm.faces.new([rings[k][s], rings[k + 1][s], rings[k + 1][(s + 1) % SEG], rings[k][(s + 1) % SEG]])
bot = [bm.verts.new((v.co.x, v.co.y, -0.01)) for v in rings[-1]]          # short wall down to the base, hidden by the lip
for s in range(SEG): bm.faces.new([rings[-1][s], bot[s], bot[(s + 1) % SEG], rings[-1][(s + 1) % SEG]])
mound = obj_from_bm("snow_mound", bm, snow_mat())

# ---------------- tile grid: 3 x 3 flush rounded clay tiles, snow-capped, sunk a little into the mound ----------------
P = CFG["tile"] + CFG["gap"]
TOP = {}
for j in (-1, 0, 1):
    for i in (-1, 0, 1):
        h = CFG["tile_base_h"] + CFG["tile_dh"][(i, j)]
        col = C["tiles"][(i + j) % 3]
        x, y = i * P, j * P
        z0 = mound_z(math.hypot(x, y)) - 0.10                      # buried 10 cm: snow drifts around the tile feet
        rbox(f"tile_{i}_{j}", (CFG["tile"], CFG["tile"], h), (x, y, z0 + h / 2), clay(col), r=0.15, seg=6)
        cap = CFG["snow_cap"]
        rbox(f"tilesnow_{i}_{j}", (CFG["tile"] * 0.96, CFG["tile"] * 0.96, cap * 2), (x, y, z0 + h + cap * 0.4), snow_mat(), r=0.07)
        TOP[(i, j)] = (x, y, z0 + h + cap * 1.4)

# ---------------- the icy path: one connected route across the tiles ----------------
DIRS = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
PW = CFG["path_w"]
for (i, j), spec in CFG["path"].items():
    x, y, z = TOP[(i, j)]
    for d in spec:
        if d == "*":
            cyl(f"plaza_{i}_{j}", 0.40, 0.05, (x, y, z), clay(C["plaza"], 0.45), seg=64, bevel=0.02)
            continue
        dx, dy = DIRS[d]
        L = 0.5
        rbox(f"path_{i}_{j}_{d}", (L if dx else PW, PW if dx else L, 0.045), (x + dx * L / 2, y + dy * L / 2, z), clay(C["path"], 0.45), r=0.02)
    rbox(f"pathjoin_{i}_{j}", (PW, PW, 0.045), (x, y, z), clay(C["path"], 0.45), r=0.02)

# ---------------- houses (built in code, like the reference house) ----------------
glow = glow_mat("window_glow", C["glow"], 6.0)
def house(k, tile, off, size, roof_h, ci, face, steeple):
    x0, y0, z = TOP[tile]; x, y = x0 + off[0] * CFG["tile"], y0 + off[1] * CFG["tile"]; w, d, h = size; parts = []
    parts.append(rbox(f"h{k}_body", (w, d, h), (x, y, z + h / 2), clay(C["house"][ci]), r=0.05))
    parts.append(prism(f"h{k}_roof", w + 0.18, d + 0.14, roof_h, (x, y, z + h - 0.02), clay(C["roof_snow"], 0.65), r=0.04))
    fy = y - d / 2
    parts.append(rbox(f"h{k}_door", (0.17, 0.04, 0.26), (x, fy - 0.005, z + 0.13), clay(C["door"]), r=0.025))
    parts.append(rbox(f"h{k}_knob", (0.022, 0.02, 0.022), (x + 0.05, fy - 0.03, z + 0.13), clay(C["gold"], 0.35), r=0.01))
    for s, wx in enumerate((-w * 0.30, w * 0.30)):
        parts.append(rbox(f"h{k}_wf{s}", (0.14, 0.03, 0.14), (x + wx, fy - 0.004, z + h * 0.58), clay(C["roof_snow"], 0.6), r=0.02))
        parts.append(rbox(f"h{k}_w{s}", (0.10, 0.03, 0.10), (x + wx, fy - 0.012, z + h * 0.58), glow, r=0.015))
    parts.append(rbox(f"h{k}_gw", (0.075, 0.03, 0.075), (x, fy - 0.07, z + h + roof_h * 0.32), glow, r=0.033))
    if steeple:
        sw = 0.20
        parts.append(rbox(f"h{k}_tower", (sw, sw, 0.30), (x, fy + 0.02, z + h + roof_h * 0.5 + 0.12), clay(C["house"][ci]), r=0.03))
        parts.append(rbox(f"h{k}_bell", (0.07, 0.03, 0.09), (x, fy + 0.02 - sw / 2 - 0.005, z + h + roof_h * 0.5 + 0.16), glow, r=0.03))
        parts.append(pyramid(f"h{k}_spire", sw + 0.06, 0.30, (x, fy + 0.02, z + h + roof_h * 0.5 + 0.42), clay(C["roof_snow"], 0.65)))
        parts.append(rbox(f"h{k}_star", (0.05, 0.05, 0.05), (x, fy + 0.02, z + h + roof_h * 0.5 + 0.60), clay(C["gold"], 0.3), r=0.024))
    else:
        parts.append(rbox(f"h{k}_chim", (0.09, 0.09, 0.22), (x + w * 0.27, y + d * 0.15, z + h + 0.18), clay(C["house_dark"]), r=0.02))
        parts.append(rbox(f"h{k}_chimsnow", (0.12, 0.12, 0.035), (x + w * 0.27, y + d * 0.15, z + h + 0.30), clay(C["roof_snow"], 0.65), r=0.016))
    k_ = CFG["prop_scale"]          # grow the whole house about its footprint
    for p_ in parts:
        p_.location = (x + (p_.location.x - x) * k_, y + (p_.location.y - y) * k_, z + (p_.location.z - z) * k_); p_.scale = (k_,) * 3
    group(parts, (x, y), face)
    return parts
for k, hs in enumerate(CFG["houses"]): house(k, *hs)

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

def kit(name, loc, rot, scale):
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
    uv = me.uv_layers.active.data; cols, glows = [], []
    for p in me.polygons:   # per-face colour from the kit's colour swatch, remapped
        u = sum(uv[li].uv.x for li in p.loop_indices) / p.loop_total; v = sum(uv[li].uv.y for li in p.loop_indices) / p.loop_total
        px = min(CW - 1, max(0, int(u * CW))); py = min(CH - 1, max(0, int(v * CH))); k = (py * CW + px) * 4
        c, gl = remap(tuple(CPX[k:k + 3])); cols.append(c); glows.append(gl)
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER"); data = []
    for p, c in zip(me.polygons, cols):
        lc = tuple(srgb2lin(x) for x in c) + (1.0,)
        for _ in p.loop_indices: data += lc
    ca.data.foreach_set("color", data)
    ga = me.attributes.new("glow", "FLOAT", "FACE"); ga.data.foreach_set("value", glows)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True       # weld the flat-shaded faces, then round every edge off (clay toy)
    me.materials.clear(); me.materials.append(attr_mat())
    smooth_normals(o, 60)
    bv = o.modifiers.new("round", "BEVEL"); bv.width = 0.035; bv.segments = 3; bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(30); bv.profile = 0.6
    sd = o.modifiers.new("soft", "SUBSURF"); sd.levels = 1; sd.render_levels = 2
    o.name = name; o.location = loc; o.rotation_euler.z = math.radians(rot); o.scale = (scale,) * 3
    return o

for name, tile, off, rot, s, absolute in CFG["props"]:
    x, y, z = TOP[tile]
    kit(name, (x + off[0] * CFG["tile"], y + off[1] * CFG["tile"], z - 0.01), rot if absolute else rot + FACE, s * CFG["prop_scale"])

# ---------------- glass dome: a thin shell; light, shadows and the back wall stay clean ----------------
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=64, radius=GR)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -GC), plane_no=(0, 0, -1), clear_inner=False, clear_outer=True)
gm, T = new_mat("glass")
gl = T.n("ShaderNodeBsdfPrincipled"); gl.inputs["Base Color"].default_value = (0.97, 0.985, 1.0, 1)
gl.inputs["Roughness"].default_value = 0.02; gl.inputs["IOR"].default_value = 1.45; gl.inputs["Transmission Weight"].default_value = 1.0
tr = T.n("ShaderNodeBsdfTransparent")
lp = T.n("ShaderNodeLightPath")
back = T.m("GREATER_THAN", lp.outputs["Transmission Depth"], 1.5)         # the far wall, seen through the near wall: plain see-through
fac = T.m("MAXIMUM", T.m("MAXIMUM", lp.outputs["Is Shadow Ray"], lp.outputs["Is Diffuse Ray"]), back)
mix = T.n("ShaderNodeMixShader"); T.link(fac, mix.inputs[0]); T.link(gl.outputs[0], mix.inputs[1]); T.link(tr.outputs[0], mix.inputs[2])
out(T, mix.outputs[0])
dome = obj_from_bm("glass_dome", bm, gm); dome.location.z = GC
so = dome.modifiers.new("shell", "SOLIDIFY"); so.thickness = CFG["glass"]; so.offset = 1.0

# ---------------- base: a rounded lip that holds the glass, a flared drum and a white band ----------------
BH = CFG["base_h"]
lip = cyl("base_lip", FR + 0.10, 0.14, (0, 0, -0.065), clay(C["base"], 0.45), bevel=0.05)
base = cyl("base", FR + 0.22, BH, (0, 0, -0.13 - BH / 2), clay(C["base"], 0.45), bevel=0.10, flare=CFG["base_flare"])
band = cyl("base_band", FR + 0.30, 0.20, (0, 0, -0.13 - BH * 0.5), clay(C["band"], 0.5), bevel=0.06, flare=1.05)
for ob in (lip, base, band): smooth_normals(ob, 40)
GROUND = -0.13 - BH

# ---------------- snow inside the globe (geometry nodes, loops every 10 s) ----------------
SNOWMAT, Tm = new_mat("snowflake")
sb = clay_bsdf(Tm, hexc(C["snow"]), 0.6); sb.inputs["Subsurface Weight"].default_value = 0.4
em = Tm.n("ShaderNodeEmission"); em.inputs["Color"].default_value = hexc(C["snow"]); em.inputs["Strength"].default_value = 0.35
ad = Tm.n("ShaderNodeAddShader"); Tm.link(sb.outputs[0], ad.inputs[0]); Tm.link(em.outputs[0], ad.inputs[1]); out(Tm, ad.outputs[0])
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
    pts = T.n("GeometryNodePoints"); pts.inputs["Count"].default_value = S["count"]; T.link(T.combine(xx, yy, zz), pts.inputs["Position"])
    dz = T.m("SUBTRACT", zz, GC)        # fade the flake out near the glass and the snow (no popping)
    d = T.m("SQRT", T.m("ADD", T.m("ADD", T.m("MULTIPLY", xx, xx), T.m("MULTIPLY", yy, yy)), T.m("MULTIPLY", dz, dz)))
    f1 = T.m("DIVIDE", T.m("SUBTRACT", GR - 0.10, d), 0.30, clamp=True)
    f2 = T.m("DIVIDE", T.m("SUBTRACT", zz, CFG["mound"] + 0.05), 0.30, clamp=True)
    size = T.m("MULTIPLY", T.m("MULTIPLY", f1, f2), rnd(8, S["size"][0], S["size"][1]))
    ico = T.n("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 1.0; ico.inputs["Subdivisions"].default_value = 2
    inst = T.n("GeometryNodeInstanceOnPoints")
    T.link(pts.outputs[0], inst.inputs["Points"]); T.link(ico.outputs[0], inst.inputs["Instance"]); T.link(size, inst.inputs["Scale"])
    real = T.n("GeometryNodeRealizeInstances"); T.link(inst.outputs[0], real.inputs[0])
    sm = T.n("GeometryNodeSetMaterial"); T.link(real.outputs[0], sm.inputs["Geometry"]); sm.inputs["Material"].default_value = SNOWMAT
    shd = T.n("GeometryNodeSetShadeSmooth"); T.link(sm.outputs[0], shd.inputs[0])
    o_ = T.n("NodeGroupOutput"); T.link(shd.outputs[0], o_.inputs[0])
    return ng
snow = link_obj("snow", bpy.data.meshes.new("snow"))
snow.modifiers.new("snowfall", "NODES").node_group = snow_nodes()

# ---------------- twinkle: window glow + gold accents (periods divide the loop) ----------------
keys(bpy.data.materials["window_glow"].node_tree, 'nodes["Emission"].inputs[1].default_value',
     [6.0 * (0.88 + 0.12 * math.sin(2 * math.pi * 4 * T_OF(f)) ** 2) for f in F])
keys(MATS["clay_attr"].node_tree, 'nodes["gold_glow"].outputs[0].default_value',
     [1.2 + 1.0 * max(0.0, math.sin(2 * math.pi * 2 * T_OF(f))) ** 4 for f in F])

# ---------------- set: infinite soft pastel-blue backdrop (a huge sweep with a gentle curve), soft studio light ----------------
bm = bmesh.new(); W_, D_, Hh, Rc = 260.0, 120.0, 120.0, 45.0
prof = [(-D_, 0.0)] + [(Rc * math.sin(a), Rc - Rc * math.cos(a)) for a in [i * (math.pi / 2) / 24 for i in range(25)]] + [(Rc, Hh)]
rows = [[bm.verts.new((xx, py + 14.0, pz + GROUND)) for (py, pz) in prof] for xx in (-W_ / 2, W_ / 2)]
for k in range(len(prof) - 1): bm.faces.new([rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]])
cyc = obj_from_bm("cyclorama", bm, clay(C["backdrop"], 0.95))
cyc.rotation_euler.z = AZ + math.pi / 2           # the sweep curves up behind the globe as seen from the camera

def around(a_deg, r, z): a = AZ + math.radians(a_deg); return (r * math.cos(a), r * math.sin(a), z)
def area(name, loc, size, energy, col=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "AREA"); ld.size = size; ld.energy = energy; ld.color = col; ld.shape = "DISK"
    lo = link_obj(name, ld); lo.location = loc; lo.visible_camera = False; lo.visible_glossy = False; lo.visible_transmission = False
    lo.rotation_euler = (Vector((0, 0, GC * 0.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return lo
area("key", around(-45, 13, 15), 16.0, CFG["light"]["key"], (1.0, 0.98, 0.95))     # big soft top-left key: soft shadows like the reference
area("fill", around(60, 15, 4), 18.0, CFG["light"]["fill"], (0.88, 0.93, 1.0))
area("back", around(180, 14, 9), 12.0, CFG["light"]["back"], (0.93, 0.96, 1.0))

def reflect_card(name, a_deg, el_deg, dist, w, h, strength):
    """a soft glowing card seen ONLY in the glass reflections: one gentle studio sheen, feathered edges"""
    bm_ = bmesh.new(); bmesh.ops.create_grid(bm_, x_segments=1, y_segments=1, size=0.5)
    for v in bm_.verts: v.co.x *= w; v.co.y *= h
    m_, T_ = new_mat(name)
    tc = T_.n("ShaderNodeTexCoord"); g_ = T_.n("ShaderNodeTexGradient", gradient_type="QUADRATIC_SPHERE")
    mp = T_.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.0, 2.0, 1.0); mp.inputs["Location"].default_value = (-1.0, -1.0, 0.0)
    T_.link(tc.outputs["UV"], mp.inputs[0]); T_.link(mp.outputs[0], g_.inputs[0])
    fall = T_.m("POWER", g_.outputs["Fac"], 2.5)
    e_ = T_.n("ShaderNodeEmission"); T_.link(T_.m("MULTIPLY", fall, strength), e_.inputs["Strength"])
    tp = T_.n("ShaderNodeBsdfTransparent"); mx = T_.n("ShaderNodeMixShader")
    T_.link(fall, mx.inputs[0]); T_.link(tp.outputs[0], mx.inputs[1]); T_.link(e_.outputs[0], mx.inputs[2]); out(T_, mx.outputs[0])
    ob = obj_from_bm(name, bm_, m_, smooth=False); ob.data.uv_layers.new(name="UVMap")
    a = AZ + math.radians(a_deg); el = math.radians(el_deg)
    ob.location = (dist * math.cos(el) * math.cos(a), dist * math.cos(el) * math.sin(a), GC + dist * math.sin(el))
    ob.rotation_euler = (Vector((0, 0, GC)) - ob.location).to_track_quat("Z", "Y").to_euler()
    for k_ in ("visible_camera", "visible_diffuse", "visible_shadow", "visible_transmission", "visible_volume_scatter"): setattr(ob, k_, False)
    return ob
reflect_card("glass_card_top", -20, 80, 11, 6.0, 6.0, CFG["glass_card"])
reflect_card("glass_card_rim", 150, 25, 11, 5.0, 9.0, CFG["glass_card"] * 0.4)

wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
bgn = wd.node_tree.nodes["Background"]; bgn.inputs[0].default_value = hexc(C["world"]); bgn.inputs[1].default_value = CFG["light"]["world"]

# ---------------- camera: gentle sway around the globe (one sine cycle per loop) ----------------
cc = CFG["cam"]
cd = bpy.data.cameras.new("cam"); cd.lens = cc["lens"]; cd.sensor_width = 36; cd.clip_start = 0.1; cd.clip_end = 600
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
