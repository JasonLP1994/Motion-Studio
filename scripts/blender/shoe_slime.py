# SLIME SHOE ident (16:9, 1920x1080, 30 fps, 360 frames = 12 s) built procedurally in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/shoe_slime.py -- <out.blend> [preview|farm]
# Story: an original sneaker made of black "venom" slime warps and waves (a C4D-style displacer field sweeps through it),
# liquifies and bursts apart -> close-ups of each part being pulled back together by slime tendrils -> whole -> it SETS
# into a solid object -> a glowing wipe colours it into a black-and-white design -> hero orbit.
# Plan: notes/shoe-slime/plan.md. Grammar from references/shoe-slime/ (no reference brands or logos).
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import farm_prep
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.join(ROOT, "renders/farm/shoe-slime-v1/shoe-slime.blend")
MODE = argv[1] if len(argv) > 1 else "preview"

# ---------------- config: every colour and timing ----------------
CFG = {
    "fps": 30, "frames": 360, "res": (1920, 1080),
    "col": {"slime": "#030306", "solid": "#09090B", "white": "#EDECE8", "black": "#060607", "glow": "#FF6A12",
            "floor": "#141416", "cyc": "#2A2B2F", "rim": "#FF6A14"},
    "wave1": (4, 40),            # displacer field sweeps heel -> toe through the slime shoe
    "melt": (40, 62),            # the shoe sags and liquifies into a puddle
    "burst": (62, 76),           # the parts burst up and apart (slow motion), strands snap
    # each part is pulled back home by slime tendrils: (start, land)
    "assemble": {"outsole": (80, 106), "midsole": (84, 112), "upper": (126, 156), "heel": (170, 199),
                 "tongue": (210, 236), "laces": (220, 248)},
    "wave2": (256, 282),         # one last wave through the whole slime shoe
    "set": 285,                  # it SETS: wet slime -> hard satin solid (hit + camera jolt)
    "sweep": (293, 326),         # glowing wipe heel -> toe colours it black and white
    # edit: timeline markers bound to cameras
    "cuts": [(1, "wide"), (77, "sole"), (117, "toe"), (162, "heel"), (207, "laces"), (252, "hero")],
    # shot cameras: (first, last, pos start, pos end, look start, look end, lens mm, f-stop)
    "cams": {
        "wide":  (1, 76, (0.44, -0.44, 0.16), (0.39, -0.38, 0.135), (0.14, 0, 0.055), (0.14, 0, 0.060), 45, 9.0),
        "sole":  (77, 116, (0.37, -0.16, 0.036), (0.33, -0.13, 0.030), (0.18, 0, 0.022), (0.17, 0, 0.026), 40, 11.0),
        "toe":   (117, 161, (0.43, -0.17, 0.090), (0.38, -0.13, 0.080), (0.24, 0, 0.050), (0.24, 0, 0.052), 40, 11.0),
        "heel":  (162, 206, (-0.19, -0.17, 0.170), (-0.15, -0.135, 0.150), (0.06, 0, 0.070), (0.06, 0, 0.068), 35, 11.0),
        "laces": (207, 251, (0.36, -0.10, 0.255), (0.32, -0.075, 0.235), (0.15, 0, 0.090), (0.15, 0, 0.092), 35, 11.0),
    },
    # hero orbit around the shoe (cylindrical: frame, angle deg, radius m, height m, look-at height m); -90 = side view
    "hero": [(252, -142, 0.54, 0.135, 0.055), (285, -128, 0.52, 0.125, 0.055), (330, -88, 0.50, 0.105, 0.052), (360, -62, 0.49, 0.095, 0.052)],
}
FPS, N = CFG["fps"], CFG["frames"]
rnd = random.Random(11)
hexc = lambda h, a=1.0: tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (1, 3, 5)) + (a,)
C = {k: hexc(v) for k, v in CFG["col"].items()}
L = 0.30   # shoe length (m): heel at x=0, toe at x=L, lateral side faces -Y (the camera side)

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS
F = range(1, N + 1)

# ---------------- helpers ----------------
def keys(id_data, path, values, count=1, interp="LINEAR"):
    ad = id_data.animation_data or id_data.animation_data_create()
    if not ad.action: ad.action = bpy.data.actions.new(f"{id_data.name}_act")
    for i in range(count):
        fc = ad.action.fcurves.find(path, index=i) or ad.action.fcurves.new(path, index=i)
        fc.keyframe_points.add(len(values)); co = []
        for f, v in enumerate(values, 1): co += [f, float(v[i] if count > 1 else v)]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = interp
        fc.update()

clamp01 = lambda x: max(0.0, min(1.0, x))
def win(f, a, b): return clamp01((f - a) / max(1e-6, b - a))
smooth = lambda t: t * t * (3 - 2 * t)
ease_io = lambda t: 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
ease_out = lambda t: 1 - (1 - t) ** 3
ease_in = lambda t: t ** 3
lerp = lambda a, b, t: a + (b - a) * t
vlerp = lambda a, b, t: tuple(lerp(x, y, t) for x, y in zip(a, b))

def crs(tab, u):
    xs = [p[0] for p in tab]; ys = [p[1] for p in tab]; u = min(max(u, xs[0]), xs[-1])
    i = next(k for k in range(len(xs) - 1) if u <= xs[k + 1]); t = (u - xs[i]) / (xs[i + 1] - xs[i])
    p0, p1, p2, p3 = ys[max(i - 1, 0)], ys[i], ys[i + 1], ys[min(i + 2, len(ys) - 1)]
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

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
    def v(self, op, a, b=None, scale=None):
        node = self.n("ShaderNodeVectorMath", operation=op)
        self._in(node, 0, a)
        if b is not None: self._in(node, 1, b)
        if scale is not None: self._in(node, 3, scale)
        return node.outputs[1] if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else node.outputs[0]
    def combine(self, x, y, z=0.0):
        node = self.n("ShaderNodeCombineXYZ")
        for i, a in enumerate([x, y, z]): self._in(node, i, a)
        return node.outputs[0]
    def sep(self, vec):
        node = self.n("ShaderNodeSeparateXYZ"); self._in(node, 0, vec); return node.outputs
    def keyed(self, name, series):
        node = self.n("ShaderNodeValue"); node.name = name; node.outputs[0].default_value = series[0]
        keys(self.nt, f'nodes["{name}"].outputs[0].default_value', series); return node.outputs[0]
    def mixc(self, fac, a, b):
        node = self.n("ShaderNodeMix", data_type="RGBA"); self._in(node, 0, fac); self._in(node, 6, a); self._in(node, 7, b)
        return node.outputs[2]
    def mixs(self, fac, a, b):
        node = self.n("ShaderNodeMixShader"); self._in(node, 0, fac); self.link(a, node.inputs[1]); self.link(b, node.inputs[2]); return node.outputs[0]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NT(m.node_tree)

def bsdf(T, base, rough, **kw):
    b = T.n("ShaderNodeBsdfPrincipled"); T._in(b, 0, base); T._in(b, b.inputs.find("Roughness"), rough)
    for k, v in kw.items(): T._in(b, b.inputs.find(k.replace("_", " ")), v)
    return b.outputs[0]

def out(T, surface, volume=None):
    o = T.n("ShaderNodeOutputMaterial")
    if surface is not None: T.link(surface, o.inputs["Surface"])
    if volume is not None: T.link(volume, o.inputs["Volume"])

def bump(T, height, strength, dist, normal=None):
    b = T.n("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    T.link(height, b.inputs["Height"])
    if normal is not None: T.link(normal, b.inputs["Normal"])
    return b.outputs[0]

def link_obj(name, me):
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); return o

def obj_from_bm(name, bm, mat=None, smooth_shade=True, centre=True):
    """mesh in shoe space; with centre=True the origin moves to the part's centroid (so it can spin in place)"""
    cen = Vector((0, 0, 0))
    if centre and bm.verts:
        for v in bm.verts: cen += v.co
        cen /= len(bm.verts)
        for v in bm.verts: v.co -= cen
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth_shade:
        for p in me.polygons: p.use_smooth = True
    o = link_obj(name, me); o.location = cen
    if mat: me.materials.append(mat)
    return o

# ---------------- the shoe shape (an original chunky runner) ----------------
WTAB = [(0, 0.030), (0.12, 0.035), (0.35, 0.037), (0.55, 0.043), (0.72, 0.049), (0.86, 0.046), (0.95, 0.038), (1.0, 0.030)]
HTAB = [(0, 0.114), (0.06, 0.124), (0.22, 0.128), (0.36, 0.114), (0.55, 0.088), (0.70, 0.071), (0.85, 0.056), (0.95, 0.046), (1.0, 0.040)]
NEXP = 2.8
def W(u):
    e = math.sqrt(max(0.0, 1 - (max(0.0, (0.07 - u) / 0.07)) ** 2)) * math.sqrt(max(0.0, 1 - (max(0.0, (u - 0.88) / 0.12)) ** 2))
    return crs(WTAB, u) * e
spring = lambda u: 0.020 * max(0.0, (u - 0.72) / 0.28) ** 2 + 0.004 * max(0.0, (0.10 - u) / 0.10) ** 2
zm = lambda u: 0.040 - 0.014 * u          # midsole top
cosu = lambda n, a=0.004, b=0.996: [a + (b - a) * (1 - math.cos(math.pi * i / (n - 1))) / 2 for i in range(n)]

def sect(u, phi, scale=1.0, lift=0.0):
    """a point on the upper: superellipse cross-section at u; phi -90..90 deg (in radians) from lateral bottom over the top"""
    zb = zm(u) - 0.004; ht = (crs(HTAB, u) - zb) * scale + lift
    s, c = math.sin(phi), math.cos(phi)
    z = zb + ht * abs(c) ** (2 / NEXP)
    w = W(u) * scale * (1 - 0.22 * (z - zb) / max(ht, 1e-4))
    y = -w * math.copysign(abs(s) ** (2 / NEXP), s)
    return (u * L, y, z + spring(u))

def slab(name, wfun, layers, mat, n=60):
    """sole slab: outline loops stacked bottom->top; layers [(z or f(u), inset)]"""
    us = cosu(n); bm = bmesh.new(); loops = []
    for zf, ins in layers:
        zv = (lambda u: zf(u)) if callable(zf) else (lambda u: zf)
        ring = [bm.verts.new((u * L, -max(0.0006, wfun(u) - ins), zv(u) + spring(u))) for u in us]
        ring += [bm.verts.new((u * L, max(0.0006, wfun(u) - ins), zv(u) + spring(u))) for u in reversed(us)]
        loops.append(ring)
    m = len(loops[0])
    for a, b in zip(loops, loops[1:]):
        for i in range(m): bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    bm.faces.new(list(reversed(loops[0]))); bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm, mat)

def grid(name, pts_fn, nu, nv, mat, keep=None):
    bm = bmesh.new(); vs = [[bm.verts.new(pts_fn(i, j)) for j in range(nv)] for i in range(nu)]
    for i in range(nu - 1):
        for j in range(nv - 1):
            if keep and not keep(i + 0.5, j + 0.5): continue
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm

def tube(bm, pts, r, seg=8):
    rings = []
    for i, p in enumerate(pts):
        p = Vector(p); t = (Vector(pts[min(i + 1, len(pts) - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 1e-4: a = t.cross(Vector((0, 1, 0)))
        a.normalize(); b = t.cross(a)
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * j / seg) * a + math.sin(2 * math.pi * j / seg) * b)) for j in range(seg)])
    for A, B in zip(rings, rings[1:]):
        for j in range(seg): bm.faces.new((A[j], A[(j + 1) % seg], B[(j + 1) % seg], B[j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])

def add_mods(o, solid=0.0, subd=2):
    if solid:
        s = o.modifiers.new("Solid", "SOLIDIFY"); s.thickness = solid; s.offset = -1; s.use_even_offset = True
    if subd:
        s = o.modifiers.new("Subd", "SUBSURF"); s.levels = 1; s.render_levels = subd

# ---------------- keyed shader values shared by every shoe material ----------------
SET, (SW0, SW1) = CFG["set"], CFG["sweep"]
SOLID = [smooth(win(f, SET - 1, SET + 3)) for f in F]
SWEEP = [lerp(-0.03, L + 0.03, ease_io(win(f, SW0, SW1))) for f in F]
GLOW = [smooth(win(f, SW0 - 2, SW0 + 3)) * (1 - smooth(win(f, SW1 - 3, SW1 + 2))) for f in F]
TIME = [f / FPS for f in F]

def skin(name, centroid, design, rough, design_bump=None):
    """venom slime -> hard satin solid (at SET) -> design colour behind the glowing wipe (SWEEP)"""
    m, T = new_mat(name)
    p = T.v("ADD", T.n("ShaderNodeTexCoord").outputs["Object"], tuple(centroid))
    sx, sy, sz = T.sep(p)
    # slime: near-black, a mirror-wet coat, slow flowing surface ripples
    nz = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); T.link(T.v("SCALE", p, scale=70.0), nz.inputs["Vector"])
    T.link(T.keyed(f"{name}_t", [t * 0.6 for t in TIME]), nz.inputs["W"]); nz.inputs["Detail"].default_value = 3; nz.inputs["Scale"].default_value = 1.0
    slime = bsdf(T, C["slime"], 0.03, Coat_Weight=1.0, Coat_Roughness=0.01, Specular_IOR_Level=0.7,
                 Normal=bump(T, nz.outputs["Fac"], 0.22, 0.002))
    solid = bsdf(T, C["solid"], 0.30, Coat_Weight=0.35, Coat_Roughness=0.12)
    if isinstance(design, tuple): dcol = design
    else: dcol = design(T, sx, sy, sz)
    dkw = {"Normal": design_bump(T, sx, sy, sz)} if design_bump else {}
    des = bsdf(T, dcol, rough, **dkw)
    s1 = T.mixs(T.keyed(f"{name}_solid", SOLID), slime, solid)
    sw = T.keyed(f"{name}_sweep", SWEEP)
    mask = T.m("MULTIPLY", T.m("SUBTRACT", sw, sx), 200.0, clamp=True)
    s2 = T.mixs(mask, s1, des)
    d = T.m("DIVIDE", T.m("SUBTRACT", sx, sw), 0.004)
    edge = T.m("MULTIPLY", T.m("EXPONENT", T.m("MULTIPLY", T.m("MULTIPLY", d, d), -1.0)), T.keyed(f"{name}_glow", GLOW))
    em = T.n("ShaderNodeEmission"); em.inputs["Color"].default_value = C["glow"]; T.link(T.m("MULTIPLY", edge, 9.0), em.inputs["Strength"])
    add = T.n("ShaderNodeAddShader"); T.link(s2, add.inputs[0]); T.link(em.outputs[0], add.inputs[1])
    out(T, add.outputs[0]); return m

def tread_bump(T, sx, sy, sz):
    wv = T.n("ShaderNodeTexWave", wave_type="BANDS"); T.link(T.combine(sx, T.m("MULTIPLY", sy, 0.6), 0.0), wv.inputs["Vector"])
    wv.inputs["Scale"].default_value = 140; wv.inputs["Distortion"].default_value = 2.0
    return bump(T, wv.outputs["Fac"], 0.5, 0.0015)
def groove_bump(T, sx, sy, sz):
    return bump(T, T.m("SINE", T.m("MULTIPLY", sz, 700.0)), 0.25, 0.0004)
def leather_bump(T, sx, sy, sz):
    vo = T.n("ShaderNodeTexVoronoi"); T.link(T.combine(sx, sy, sz), vo.inputs["Vector"]); vo.inputs["Scale"].default_value = 1400
    return bump(T, vo.outputs["Distance"], 0.12, 0.0003)

def upper_design(T, sx, sy, sz):
    """white upper with black flowing wave overlays (original) and a black toe bumper"""
    zl = T.m("ADD", 0.040, T.m("MULTIPLY", T.m("ADD", 0.040, T.m("MULTIPLY", T.m("SINE", T.m("ADD", T.m("MULTIPLY", sx, 26.0), 0.9)), 0.014)),
                                 T.m("SUBTRACT", 1.0, T.m("MULTIPLY", sx, 1.5))))
    wdt = T.m("ADD", 0.004, T.m("MULTIPLY", T.m("SUBTRACT", L, sx), 0.040))
    s1 = T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", sz, zl)), wdt)
    zl2 = T.m("ADD", zl, T.m("ADD", 0.020, T.m("MULTIPLY", T.m("SINE", T.m("ADD", T.m("MULTIPLY", sx, 34.0), 2.2)), 0.006)))
    s2 = T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", sz, zl2)), T.m("MULTIPLY", wdt, 0.35))
    toe = T.m("MULTIPLY", T.m("GREATER_THAN", sx, 0.262), T.m("LESS_THAN", sz, T.m("ADD", 0.040, T.m("MULTIPLY", T.m("SUBTRACT", sx, 0.262), 0.25))))
    collar = T.m("MULTIPLY", T.m("LESS_THAN", sx, 0.13), T.m("GREATER_THAN", sz, 0.106))
    mask = T.m("MINIMUM", 1.0, T.m("ADD", T.m("ADD", s1, s2), T.m("ADD", toe, collar)))
    upper_design.mask = mask
    return T.mixc(mask, C["white"], C["black"])
def upper_bump(T, sx, sy, sz):
    return bump(T, upper_design.mask, 0.6, 0.0006, normal=leather_bump(T, sx, sy, sz))
def tongue_design(T, sx, sy, sz):
    return T.mixc(T.m("GREATER_THAN", sz, 0.112), C["white"], C["black"])

# ---------------- build the parts ----------------
parts = {}
o = slab("outsole", lambda u: W(u) + 0.004, [(0.0, 0.004), (0.0015, 0.001), (0.004, 0.0), (0.0085, 0.0), (0.0095, 0.0015)], None)
parts["outsole"] = o
o = slab("midsole", lambda u: W(u) + 0.005, [(0.0085, 0.002), (0.010, 0.0), (lambda u: 0.5 * (0.010 + zm(u)), -0.0018),
                                              (lambda u: zm(u) - 0.002, 0.0), (lambda u: zm(u), 0.002)], None)
parts["midsole"] = o
NU, NV = 46, 30
U_UP = cosu(NU, 0.003, 0.997); PH = [-math.pi / 2 + math.pi * j / (NV - 1) for j in range(NV)]
open_tab = [(0.0, 0.0), (0.015, 0.55), (0.08, 0.80), (0.30, 0.80), (0.38, 0.50), (0.42, 0.24), (0.62, 0.20), (0.66, 0.0), (1.0, 0.0)]
def up_keep(i, j):
    u = lerp(U_UP[int(i)], U_UP[min(int(i) + 1, NU - 1)], 0.5); ph = lerp(PH[int(j)], PH[min(int(j) + 1, NV - 1)], 0.5)
    return not (0.012 < u < 0.66 and abs(ph) < crs(open_tab, u))
bm = grid("upper", lambda i, j: sect(U_UP[i], PH[j]), NU, NV, None, keep=up_keep)
parts["upper"] = obj_from_bm("upper", bm); add_mods(parts["upper"], 0.0028)
U_T = cosu(22, 0.33, 0.70); PT = [-0.42 + 0.84 * j / 11 for j in range(12)]
bm = grid("tongue", lambda i, j: (lambda p: (p[0], p[1], p[2] + 0.014 * max(0.0, (0.42 - U_T[i]) / 0.09)))(sect(U_T[i], PT[j], 0.975)), 22, 12, None)
parts["tongue"] = obj_from_bm("tongue", bm); add_mods(parts["tongue"], 0.004)
# heel counter: two side strips from the sole up to a sweeping top line, slightly proud of the upper
U_H = cosu(18, 0.002, 0.30)
def heel_pt(i, j, side):
    u = U_H[i]; zb = zm(u) - 0.004; ht = crs(HTAB, u) - zb
    frac = max(0.06, 0.66 * (1 - (u / 0.30) ** 1.4)); ph0 = math.acos(min(1.0, frac ** (NEXP / 2)))
    ph = side * (ph0 + (math.pi / 2 - ph0) * j / 7)
    return sect(u, ph, 1.035)
bmh = bmesh.new()
for side in (-1, 1):
    vs = [[bmh.verts.new(heel_pt(i, j, side)) for j in range(8)] for i in range(18)]
    for i in range(17):
        for j in range(7): bmh.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
tab = bmesh.ops.create_cube(bmh, size=1.0)["verts"]
for v in tab: v.co = Vector((v.co.x * 0.009 - 0.006 - 0.10 * (v.co.z + 0.5) * 0.04, v.co.y * 0.026, v.co.z * 0.042 + crs(HTAB, 0) + 0.008 + spring(0)))
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
parts["heel"] = obj_from_bm("heel", bmh); add_mods(parts["heel"], 0.003)
# laces: five criss-crossing cords over the tongue
bml = bmesh.new()
for k in range(5):
    ua, ub = 0.44 + 0.047 * k, 0.44 + 0.047 * k + 0.03
    if k % 2: ua, ub = ub, ua
    pts = []
    for s in range(11):
        t = s / 10; ph = lerp(-0.30, 0.30, t); u = lerp(ua, ub, t)
        x, y, z = sect(u, ph, 1.0); pts.append((x, y, z + 0.0045 + 0.0025 * math.sin(math.pi * t)))
    tube(bml, pts, 0.0019)
parts["laces"] = obj_from_bm("laces", bml); add_mods(parts["laces"], 0.0, 1)
for nm in ("outsole", "midsole"): add_mods(parts[nm], 0.0)

DESIGN = {"outsole": (C["black"], 0.6, tread_bump), "midsole": (C["white"], 0.42, groove_bump),
          "upper": (upper_design, 0.5, upper_bump), "heel": (C["black"], 0.45, leather_bump),
          "tongue": (tongue_design, 0.55, leather_bump), "laces": (C["black"], 0.6, None)}
for nm, o in parts.items():
    d, r, b = DESIGN[nm]; o.data.materials.append(skin(f"skin_{nm}", o.location, d, r, b))

# ---------------- the C4D-style warp: one geometry-nodes group on every slime object ----------------
ng = bpy.data.node_groups.new("SlimeWarp", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
for nm in ["Amp", "Sag", "Wave", "Field", "Seed", "Freq", "Ox", "Oy", "Oz"]:
    ng.interface.new_socket(nm, in_out="INPUT", socket_type="NodeSocketFloat")
IDS = {it.name: it.identifier for it in ng.interface.items_tree if getattr(it, "in_out", None) == "INPUT"}
G = NT(ng); gi = G.n("NodeGroupInput"); go = G.n("NodeGroupOutput")
pos = G.n("GeometryNodeInputPosition").outputs[0]; nrm = G.n("GeometryNodeInputNormal").outputs[0]
secs = G.n("GeometryNodeInputSceneTime").outputs["Seconds"]
X, Y, Z = G.sep(pos); xs, ys, zs = G.m("ADD", X, gi.outputs["Ox"]), G.m("ADD", Y, gi.outputs["Oy"]), G.m("ADD", Z, gi.outputs["Oz"])
shoe_p = G.combine(xs, ys, zs)
nz = G.n("ShaderNodeTexNoise", noise_dimensions="4D"); G.link(G.v("SCALE", shoe_p, scale=gi.outputs["Freq"]), nz.inputs["Vector"])
G.link(G.m("MULTIPLY_ADD", secs, 0.9, gi.outputs["Seed"]), nz.inputs["W"]); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 1.5
churn = G.v("SCALE", G.v("SUBTRACT", nz.outputs["Color"], (0.5, 0.5, 0.5)), scale=G.m("MULTIPLY", gi.outputs["Amp"], 2.0))
d = G.m("DIVIDE", G.m("SUBTRACT", xs, gi.outputs["Field"]), 0.05)
band = G.m("EXPONENT", G.m("MULTIPLY", G.m("MULTIPLY", d, d), -1.0))
ripple = G.m("ADD", 0.55, G.m("MULTIPLY", 0.45, G.m("SINE", G.m("SUBTRACT", G.m("MULTIPLY", xs, 90.0), G.m("MULTIPLY", secs, 14.0)))))
wave = G.v("SCALE", nrm, scale=G.m("MULTIPLY", G.m("MULTIPLY", band, ripple), gi.outputs["Wave"]))
low = G.m("SUBTRACT", 1.0, G.m("DIVIDE", zs, 0.12), clamp=True)
sag = G.combine(G.m("MULTIPLY", G.m("SUBTRACT", xs, 0.15), G.m("MULTIPLY", gi.outputs["Sag"], G.m("MULTIPLY", low, 0.35))),
                G.m("MULTIPLY", ys, G.m("MULTIPLY", gi.outputs["Sag"], G.m("MULTIPLY", low, 1.1))),
                G.m("MULTIPLY", zs, G.m("MULTIPLY", gi.outputs["Sag"], -0.88)))
sp = G.n("GeometryNodeSetPosition")
G.link(gi.outputs["Geometry"], sp.inputs["Geometry"]); G.link(G.v("ADD", G.v("ADD", churn, wave), sag), sp.inputs["Offset"])
G.link(sp.outputs[0], go.inputs[0])

def warp(o, seed, home_centroid):
    md = o.modifiers.new("Warp", "NODES"); md.node_group = ng
    for k, v in {"Seed": seed, "Freq": 36.0, "Ox": home_centroid[0], "Oy": home_centroid[1], "Oz": home_centroid[2]}.items(): md[IDS[k]] = float(v)
    return md

# ---------------- motion: melt, burst, tendril-pulled assembly ----------------
(W10, W11), (M0, M1), (B0, B1), (W20, W21) = CFG["wave1"], CFG["melt"], CFG["burst"], CFG["wave2"]
# parts burst up and BACK (+Y, away from every camera) so they never cross the lens, then fly in from behind/above
SCATTER = {"outsole": ((0.00, 0.04, 0.030), (0.25, -0.10, 0.20)), "midsole": ((-0.01, 0.07, 0.070), (-0.30, 0.15, -0.20)),
           "upper": ((0.02, 0.09, 0.130), (0.15, 0.30, 0.35)), "heel": ((-0.09, 0.08, 0.100), (0.45, -0.30, 0.25)),
           "tongue": ((0.09, 0.12, 0.150), (-0.35, 0.25, 0.40)), "laces": ((0.05, 0.14, 0.170), (0.30, 0.40, -0.35))}
FIELD = [lerp(-0.06, L + 0.06, ease_io(win(f, W10, W11))) if f <= W11 + 5 else lerp(-0.06, L + 0.06, ease_io(win(f, W20, W21))) for f in F]
WAVEA = [0.011 * math.sin(math.pi * win(f, W10, W11)) ** 0.5 + 0.008 * math.sin(math.pi * win(f, W20, W21)) ** 0.5 for f in F]
SAG = [0.55 * ease_in(win(f, M0, M1)) * (1 - ease_out(win(f, B0, B0 + 9))) for f in F]
XF = {}   # per part, per frame: (loc, rot)

for idx, (nm, o) in enumerate(parts.items()):
    home = tuple(o.location); off, rot = SCATTER[nm]; a0, a1 = CFG["assemble"][nm]
    scat = tuple(h + d for h, d in zip(home, off)); drift = (rnd.uniform(-1, 1) * 0.0002, rnd.uniform(-1, 1) * 0.0002, 0.0002)
    def floating(f):
        t = f - B1
        return (tuple(s + dv * t + 0.003 * math.sin(f * 0.11 + idx + k) for k, (s, dv) in enumerate(zip(scat, drift))),
                tuple(r + 0.004 * t * (1 if k % 2 else -1) for k, r in enumerate(rot)))
    locs, rots, amps = [], [], []
    for f in F:
        if f <= B0: l, r = home, (0, 0, 0)
        elif f <= B1: t = ease_out(win(f, B0, B1)); l, r = vlerp(home, scat, t), vlerp((0, 0, 0), rot, t)
        elif f <= a0: l, r = floating(f)
        elif f <= a1:
            fl, fr = floating(a0); t = ease_in(win(f, a0, a1)) * 0.35 + ease_io(win(f, a0, a1)) * 0.65
            l, r = vlerp(fl, home, t), vlerp(fr, (0, 0, 0), t)
        else:
            fl, _ = floating(a0); dv = Vector(home) - Vector(fl); dv = dv.normalized() if dv.length else dv; k = f - a1
            j = 0.006 * math.exp(-k / 3.0) * math.sin(k * 1.4) if f < SET else 0.0
            l, r = tuple(Vector(home) + dv * j), (0, 0, 0)
        locs.append(l); rots.append(r)
        # amplitude of the churn: calm slime, wild while melted, a splat on landing, frozen once set
        base = 0.0022
        a = base + 0.012 * smooth(win(f, M0 - 4, M1)) * (1 - win(f, B1, B1 + 20)) + 0.004 * (B1 < f < a1)
        if f >= a1: a += 0.009 * math.exp(-(f - a1) / 5.0)
        a *= 1 - smooth(win(f, SET - 1, SET + 2))
        amps.append(a)
    keys(o, "location", locs, 3); keys(o, "rotation_euler", rots, 3)
    md = warp(o, seed=idx * 3.7, home_centroid=home)
    keys(o, f'modifiers["Warp"]["{IDS["Amp"]}"]', amps); keys(o, f'modifiers["Warp"]["{IDS["Sag"]}"]', SAG)
    keys(o, f'modifiers["Warp"]["{IDS["Wave"]}"]', WAVEA); keys(o, f'modifiers["Warp"]["{IDS["Field"]}"]', FIELD)
    XF[nm] = (locs, rots, home)

# ---------------- slime extras: puddle, drips, tendrils ----------------
slime_mat = skin("skin_slime", (0, 0, 0), C["black"], 0.5)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=24, radius=1.0)
for v in bm.verts: v.co = Vector((v.co.x * 0.19, v.co.y * 0.085, max(-0.2, v.co.z) * 0.007))
pud = obj_from_bm("puddle", bm, slime_mat, centre=False); pud.location = (0.15, 0, 0.0); add_mods(pud, 0.0, 1)
md = warp(pud, 9.0, (0.15, 0, 0)); md[IDS["Freq"]] = 28.0
PS = [smooth(win(f, M0 - 6, M1)) * (1 - smooth(win(f, 84, 112))) for f in F]
keys(pud, "scale", [(max(1e-3, s), max(1e-3, s), max(1e-3, s)) for s in PS], 3)
keys(pud, f'modifiers["Warp"]["{IDS["Amp"]}"]', [0.004 + 0.004 * win(f, M0, M1) for f in F])

def teardrop():
    bm = bmesh.new(); rings = []; seg = 12
    prof = [(0.0, 0.30)] + [(t, (0.30 + 0.70 * t / 0.8)) for t in (0.2, 0.4, 0.6, 0.8)] + [(0.8 + 0.2 * s, math.sqrt(max(0, 1 - s * s))) for s in (0.4, 0.7, 0.9, 1.0)]
    for t, r in prof:
        rings.append([bm.verts.new((0.0028 * r * math.cos(2 * math.pi * j / seg), 0.0028 * r * math.sin(2 * math.pi * j / seg), -t)) for j in range(seg)])
    for A, B in zip(rings, rings[1:]):
        for j in range(seg): bm.faces.new((A[j], A[(j + 1) % seg], B[(j + 1) % seg], B[j]))
    bm.faces.new(rings[0][::-1]); bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    return bm
DRIPS = [("midsole", 0.08, -1), ("midsole", 0.20, -1), ("midsole", 0.27, 1), ("outsole", 0.12, -1), ("outsole", 0.24, 1),
         ("upper", 0.95, -1), ("heel", 0.05, -1), ("laces", 0.5, -1), ("midsole", 0.04, 1), ("outsole", 0.29, -1)]
for k, (nm, u, side) in enumerate(DRIPS):
    par = parts[nm]; home = Vector(XF[nm][2])
    if nm in ("midsole", "outsole"): p = Vector((u * L, side * (W(u) + 0.003), (0.004 if nm == "outsole" else 0.012) + spring(u)))
    elif nm == "upper": p = Vector((u * L, side * W(u) * 0.8, 0.028 + spring(u)))
    elif nm == "heel": p = Vector((0.004, side * 0.012, crs(HTAB, 0) - 0.01))
    else: p = Vector(sect(0.53, -0.30)) + Vector((0, 0, 0.002))
    dr = obj_from_bm(f"drip{k}", teardrop(), slime_mat, centre=False); dr.parent = par; dr.location = p - home
    ph = rnd.uniform(0, 6); L0 = rnd.uniform(0.010, 0.022)
    vals = []
    for f in F:
        ln = L0 * (0.55 + 0.45 * math.sin(f * 0.12 + ph)) * (1 + 0.6 * smooth(win(f, M0, M1)))
        if f >= SET: ln *= 1 - smooth(win(f, SET + 3, SET + 12))   # frozen at the hit, then retracts into the shell
        vals.append((1, 1, max(0.02, ln / 0.01) if ln > 1e-4 else 0.001))
    keys(dr, "scale", vals, 3)

def world_pt(nm, f, local):
    locs, rots, home = XF[nm]; return Vector(locs[f - 1]) + Euler(rots[f - 1]).to_matrix() @ Vector(local)

def strand(name, nm, local, f_on, f_off, target, r0, snap=None):
    """a slime tendril from a point on a part (moving) to a fixed target; necks in the middle; snaps or merges"""
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.001; cu.bevel_resolution = 3; cu.use_fill_caps = True
    K = 9; sp = cu.splines.new("NURBS"); sp.points.add(K - 1); sp.order_u = 4; sp.use_endpoint_u = True
    o = link_obj(name, cu); o.data.materials.append(slime_mat)
    cos = [[] for _ in range(K)]; rads = [[] for _ in range(K)]
    T = Vector(target)
    for f in F:
        A = world_pt(nm, f, local); ln = (A - T).length
        on = win(f, f_on - 3, f_on + 2) * (1 - win(f, f_off, f_off + 4))
        sn = win(f, snap, snap + 4) if snap else 0.0
        thick = r0 * min(1.6, (0.03 / max(ln, 0.004)) ** 0.5) * on
        for i in range(K):
            s = i / (K - 1); P = T.lerp(A, s)
            P.z -= 0.25 * ln * math.sin(math.pi * s) * (0.6 + 1.2 * sn)
            neck = 0.35 + 0.65 * abs(2 * s - 1) ** 1.4
            r = thick * neck * (1 - sn * (1 - abs(2 * s - 1) ** 0.4))
            cos[i].append((P.x, P.y, P.z, 1.0)); rads[i].append(max(0.0, r))
    for i in range(K):
        keys(cu, f"splines[0].points[{i}].co", cos[i], 4); keys(cu, f"splines[0].points[{i}].radius", rads[i])

for nm, o in parts.items():
    me = o.data; home = Vector(XF[nm][2]); a0, a1 = CFG["assemble"][nm]
    verts = [v.co.copy() for v in me.vertices]
    low = sorted(verts, key=lambda c: c.z)[: max(8, len(verts) // 5)]
    picks = rnd.sample(low, 3) + rnd.sample(verts, 1)
    for k, lp in enumerate(picks):
        tgt = home + lp
        strand(f"burst_{nm}{k}", nm, lp, B0 + 1, B1 + 8, tgt + Vector((0, 0, -0.004)), 2.4, snap=B0 + 9 + k * 2)
        strand(f"pull_{nm}{k}", nm, lp, a0 - 6, a1, tgt, 2.8)

# ---------------- set: dark charcoal cyclorama, glossy floor, haze, hidden lights ----------------
bm = bmesh.new(); prof = [(-4.0, 0.0), (1.0, 0.0)] + [(1.0 + 1.2 * math.sin(a), 1.2 - 1.2 * math.cos(a)) for a in [math.pi / 2 * k / 10 for k in range(1, 11)]] + [(2.2, 3.0)]
rowA = [bm.verts.new((-4.0, y, z)) for y, z in prof]; rowB = [bm.verts.new((4.0, y, z)) for y, z in prof]
for i in range(len(prof) - 1): bm.faces.new((rowA[i], rowA[i + 1], rowB[i + 1], rowB[i]))
cm, T = new_mat("cyc")
co = T.n("ShaderNodeTexCoord").outputs["Object"]; cx, cy, cz = T.sep(co)
isfloor = T.m("SUBTRACT", 1.0, T.m("DIVIDE", cz, 0.45), clamp=True)
nzf = T.n("ShaderNodeTexNoise"); T.link(co, nzf.inputs["Vector"]); nzf.inputs["Scale"].default_value = 14
rough = T.m("ADD", 0.12, T.m("MULTIPLY", nzf.outputs["Fac"], 0.16))
floor = bsdf(T, C["floor"], rough, Specular_IOR_Level=0.6)
wall = bsdf(T, C["cyc"], 0.8)
out(T, T.mixs(isfloor, wall, floor))
cyc = obj_from_bm("cyclorama", bm, cm, centre=False)
for p in cyc.data.polygons: p.use_smooth = True
add_mods(cyc, 0.0, 2)

vm, T = new_mat("haze")
co = T.n("ShaderNodeTexCoord").outputs["Object"]
nzv = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); T.link(T.v("SCALE", co, scale=2.2), nzv.inputs["Vector"])
T.link(T.keyed("haze_t", [t * 0.08 for t in TIME]), nzv.inputs["W"]); nzv.inputs["Detail"].default_value = 3
dens = T.m("ADD", 0.010, T.m("MULTIPLY", T.m("POWER", nzv.outputs["Fac"], 4.0), 0.6))
vol = T.n("ShaderNodeVolumePrincipled"); T.link(dens, vol.inputs["Density"]); vol.inputs["Color"].default_value = (0.8, 0.8, 0.82, 1)
out(T, None, vol.outputs[0])
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
hz = obj_from_bm("haze", bm, vm, smooth_shade=False, centre=False); hz.scale = (3.0, 3.4, 1.4); hz.location = (0.15, 0.4, 0.6)

def area(name, loc, target, size, power, colour=(1, 1, 1), shape="RECTANGLE", size_y=None, glossy=True):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = shape; ld.size = size; ld.size_y = size_y or size; ld.energy = power; ld.color = colour
    lo = link_obj(name, ld); lo.location = loc
    lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    lo.visible_camera = False   # never show the lights themselves
    if not glossy: lo.visible_glossy = False
    return lo
CEN = (0.15, 0.0, 0.06); rim = C["rim"][:3]
area("key", (-0.02, -0.40, 0.44), CEN, 0.22, 9.0, (1.0, 0.97, 0.94), size_y=0.10)
area("top_strip", (0.15, 0.02, 0.36), (0.15, 0.0, 0.0), 0.50, 5.0, size_y=0.035)
area("rim_l", (-0.24, 0.26, 0.20), CEN, 0.03, 6.0, rim, size_y=0.26)
area("rim_r", (0.54, 0.26, 0.20), CEN, 0.03, 6.0, rim, size_y=0.26)
area("kick", (0.25, -0.50, 0.03), CEN, 0.12, 1.4, (0.85, 0.9, 1.0), size_y=0.03)
area("wall_glow", (0.15, 1.0, 0.25), (0.15, 2.2, 1.0), 1.2, 70.0, (0.95, 0.95, 1.0), glossy=False)
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
wd.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.010, 0.012, 1); wd.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# ---------------- cameras: one per shot, cut by timeline markers ----------------
cams = {}
def make_cam(name, lens, fstop):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.005
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    co = link_obj(name, cd); tg = link_obj(name + "_look", None); tg.empty_display_size = 0.01
    tc = co.constraints.new("TRACK_TO"); tc.target = tg; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cd.dof.focus_object = tg; cams[name] = co; return co, tg

def jolt(f, at, amp=0.0025):
    k = f - at
    return 0.0 if k < 0 else amp * math.exp(-k / 2.5) * math.sin(k * 2.1)

for name, (f0, f1, p0, p1, l0, l1, lens, fs) in CFG["cams"].items():
    co, tg = make_cam(name, lens, fs)
    lands = [a1 for nm, (a0, a1) in CFG["assemble"].items() if f0 <= a1 <= f1]
    P, Lk = [], []
    for f in F:
        t = ease_io(win(f, f0, f1)); p = list(vlerp(p0, p1, t)); l = list(vlerp(l0, l1, t))
        for a in lands: p[2] += jolt(f, a, 0.0018); p[0] += jolt(f, a + 1, 0.0010)
        P.append(p); Lk.append(l)
    keys(co, "location", P, 3); keys(tg, "location", Lk, 3)
    co.data.dof.focus_object = None
    keys(co.data, "dof.focus_distance", [(Vector(p) - Vector(l)).length - 0.035 for p, l in zip(P, Lk)])

co, tg = make_cam("hero", 45, 9.0)
hk = CFG["hero"]; P, Lk = [], []
def hero_at(f):
    for (fa, *a), (fb, *b) in zip(hk, hk[1:]):
        if f <= fb:
            t = win(f, fa, fb); t = ease_io(t) if fa != hk[0][0] else ease_out(t) * 0.5 + t * 0.5
            return [lerp(x, y, t) for x, y in zip(a, b)]
    return hk[-1][1:]
for f in F:
    ang, rad, hgt, lh = hero_at(max(f, hk[0][0]))
    th = math.radians(ang); p = [CEN[0] + rad * math.cos(th), rad * math.sin(th), hgt]
    p[2] += jolt(f, SET, 0.004); p[0] += jolt(f, SET + 1, 0.002)
    P.append(p); Lk.append([CEN[0], 0.0, lh])
keys(co, "location", P, 3); keys(tg, "location", Lk, 3)
co.data.dof.focus_object = None
keys(co.data, "dof.focus_distance", [(Vector(p) - Vector(l)).length - 0.04 for p, l in zip(P, Lk)])
for fr, name in CFG["cuts"]:
    mk = sc.timeline_markers.new(f"cut_{name}_{fr}", frame=fr); mk.camera = cams[name]
sc.camera = cams["wide"]

# ---------------- render ----------------
sc.render.resolution_x, sc.render.resolution_y = CFG["res"]; sc.render.resolution_percentage = 100
cy = sc.cycles; cy.max_bounces = 12; cy.glossy_bounces = 8; cy.transmission_bounces = 4; cy.volume_bounces = 1
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.volume_step_rate = 4.0 if MODE == "preview" else 1.0
cy.use_light_tree = True; cy.sample_clamp_indirect = 8.0
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except TypeError: pass
farm_prep.prepare(sc, OUT, samples=128 if MODE == "farm" else 48, frames=(1, N), name="shoe_slime", fps=FPS, motion_blur=(MODE == "farm"))
