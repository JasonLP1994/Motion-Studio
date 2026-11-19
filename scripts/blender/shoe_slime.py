# SLIME SHOE ident (16:9, 1920x1080, 30 fps, 360 frames = 12 s) built procedurally in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/shoe_slime.py -- <out.blend> [preview|farm]
# Story: an original sneaker made of black "venom" slime warps and waves (a C4D-style displacer field sweeps through it),
# liquifies and bursts apart -> close-ups of each part being pulled back together by slime tendrils -> whole -> it SETS
# into a solid object -> a glowing wipe colours it into a black-and-white design -> hero orbit.
# Plan: notes/shoe-slime/plan.md. Grammar from references/shoe-slime/ (no reference brands or logos).
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import farm_prep
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.join(ROOT, "renders/farm/shoe-slime-v1/shoe-slime.blend")
MODE = argv[1] if len(argv) > 1 else "preview"

# ---------------- config: every colour and timing ----------------
CFG = {
    "fps": 30, "frames": 360, "res": (1920, 1080),
    "col": {"slime": "#030306", "solid": "#09090B", "white": "#EDECE8", "black": "#060607", "glow": "#3FB6FF",
            "floor": "#141416", "cyc": "#2A2B2F", "rim": "#7FC8FF"},
    "wave1": (4, 40),            # displacer field sweeps heel -> toe through the slime shoe
    "melt": (40, 62),            # the shoe sags and liquifies into a puddle
    "burst": (62, 76),           # the parts burst up and apart (slow motion), strands snap
    # each part is pulled back home by slime tendrils: (start, land)
    "assemble": {"outsole": (80, 106), "midsole": (84, 112), "upper": (126, 156), "heel": (170, 199),
                 "tongue": (210, 236), "laces": (220, 248)},
    "wave2": (256, 282),         # one last wave through the whole slime shoe
    "set": 285,                  # it SETS: wet slime -> hard satin solid (hit + camera jolt)
    "sweep": (290, 318),         # the wet slime DRAINS down off the set shoe (glowing curing edge) and stays only as the printed drips
    # edit: timeline markers bound to cameras
    "cuts": [(1, "wide"), (77, "sole"), (117, "toe"), (162, "heel"), (207, "laces"), (252, "hero")],
    # shot cameras: (first, last, pos start, pos end, look start, look end, lens mm, f-stop)
    "cams": {
        "wide":  (1, 76, (0.44, -0.44, 0.16), (0.39, -0.38, 0.135), (0.14, 0, 0.055), (0.14, 0, 0.060), 45, 9.0),
        "sole":  (77, 116, (0.37, -0.16, 0.036), (0.33, -0.13, 0.030), (0.18, 0, 0.022), (0.17, 0, 0.026), 40, 7.1),
        "toe":   (117, 161, (0.43, -0.17, 0.090), (0.38, -0.13, 0.080), (0.24, 0, 0.050), (0.24, 0, 0.052), 40, 7.1),
        "heel":  (162, 206, (-0.17, -0.15, 0.215), (-0.135, -0.12, 0.195), (0.06, 0, 0.060), (0.06, 0, 0.058), 35, 7.1),
        "laces": (207, 251, (0.38, -0.21, 0.205), (0.345, -0.18, 0.190), (0.155, 0, 0.082), (0.15, 0, 0.084), 40, 7.1),
    },
    # hero orbit around the shoe (cylindrical: frame, angle deg, radius m, height m, look-at height m); -90 = side view
    "hero": [(252, -150, 0.54, 0.120, 0.055), (285, -122, 0.50, 0.100, 0.055), (318, -74, 0.46, 0.080, 0.052), (360, -40, 0.50, 0.072, 0.060)],
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
HTAB = [(0, 0.104), (0.06, 0.112), (0.20, 0.113), (0.36, 0.104), (0.55, 0.083), (0.70, 0.065), (0.85, 0.050), (0.95, 0.039), (1.0, 0.031)]
NEXP = 2.35
def W(u):
    e = math.sqrt(max(0.0, 1 - (max(0.0, (0.07 - u) / 0.07)) ** 2)) * math.sqrt(max(0.0, 1 - (max(0.0, (u - 0.80) / 0.20)) ** 2.4))
    return crs(WTAB, u) * e
spring = lambda u: 0.021 * max(0.0, (u - 0.70) / 0.30) ** 2 + 0.004 * max(0.0, (0.10 - u) / 0.10) ** 2
zm = lambda u: 0.040 - 0.014 * u          # midsole top
cosu = lambda n, a=0.004, b=0.996: [a + (b - a) * (1 - math.cos(math.pi * i / (n - 1))) / 2 for i in range(n)]

def sect(u, phi, scale=1.0, lift=0.0):
    """a point on the upper: superellipse cross-section at u; phi -90..90 deg (in radians) from lateral bottom over the top"""
    zb = zm(u) - 0.004; ht = (crs(HTAB, u) - zb) * scale + lift
    s, c = math.sin(phi), math.cos(phi)
    z = zb + ht * abs(c) ** (2 / NEXP)
    w = W(u) * scale * (1 - 0.30 * ((z - zb) / max(ht, 1e-4)) ** 1.5)
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

def tube(bm, pts, r, seg=8, flat=1.0):
    rings = []
    for i, p in enumerate(pts):
        p = Vector(p); t = (Vector(pts[min(i + 1, len(pts) - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 1e-4: a = t.cross(Vector((0, 1, 0)))
        a.normalize(); b = t.cross(a)
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * j / seg) * a + flat * math.sin(2 * math.pi * j / seg) * b)) for j in range(seg)])
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
SWEEP = [lerp(0.16, -0.02, 0.5 * smooth(win(f, SW0, SW1)) + 0.5 * win(f, SW0, SW1)) for f in F]     # drain level (m): top of the shoe -> below the sole
GLOW = [smooth(win(f, SW0 - 2, SW0 + 3)) * (1 - smooth(win(f, SW1 - 3, SW1 + 2))) for f in F]
TIME = [f / FPS for f in F]
OPEN = [lerp(-0.03, 0.17, smooth(win(f, 8, 44))) for f in F]     # venom takes over: infection level climbs the clean shoe

DISP = {}
def skin(name, centroid, design, rough, design_bump=None):
    """venom slime -> hard satin solid (at SET) -> design colour behind the glowing wipe (SWEEP)"""
    m, T = new_mat(name)
    p = T.v("ADD", T.n("ShaderNodeTexCoord").outputs["Object"], tuple(centroid))
    sx, sy, sz = T.sep(p)
    # slime: near-black, a mirror-wet coat, slow flowing surface ripples
    nz = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); T.link(T.v("SCALE", p, scale=70.0), nz.inputs["Vector"])
    T.link(T.keyed(f"{name}_t", [t * 0.6 for t in TIME]), nz.inputs["W"]); nz.inputs["Detail"].default_value = 3; nz.inputs["Scale"].default_value = 1.0
    slime = bsdf(T, (0.003, 0.004, 0.012, 1), 0.03, Coat_Weight=1.0, Coat_Roughness=0.01, Specular_IOR_Level=0.7,
                 Sheen_Weight=0.45, Sheen_Roughness=0.3, Sheen_Tint=(0.25, 0.55, 1.0, 1),
                 Normal=bump(T, nz.outputs["Fac"], 0.22, 0.002))
    solid = bsdf(T, C["solid"], 0.30, Coat_Weight=0.35, Coat_Roughness=0.12)
    if callable(design) and getattr(design, "shader", False): des = design(T, sx, sy, sz)
    else:
        dcol = design if isinstance(design, tuple) else design(T, sx, sy, sz)
        dkw = {"Normal": design_bump(T, sx, sy, sz)} if design_bump else {}
        des = bsdf(T, dcol, rough, **dkw)
    s1 = T.mixs(T.m("MULTIPLY", T.keyed(f"{name}_solid", SOLID), 0.25), slime, solid)   # stays wet-looking after it sets
    sw = T.keyed(f"{name}_sweep", SWEEP)
    stn = T.n("ShaderNodeTexNoise"); T.link(T.combine(sx, sy, 0.0), stn.inputs["Vector"]); stn.inputs["Scale"].default_value = 55.0; stn.inputs["Detail"].default_value = 2
    front = T.m("ADD", sw, T.m("MULTIPLY", T.m("SUBTRACT", stn.outputs["Fac"], 0.5), 0.034))     # streaky front: slime lags in runs
    mdrain = T.m("MULTIPLY", T.m("SUBTRACT", sz, front), 400.0, clamp=True)
    ofront = T.m("SUBTRACT", T.keyed(f"{name}_open", OPEN), T.m("MULTIPLY", T.m("SUBTRACT", stn.outputs["Fac"], 0.5), 0.034))
    mask = T.m("MAXIMUM", mdrain, T.m("MULTIPLY", T.m("SUBTRACT", sz, ofront), 400.0, clamp=True))      # clean before the takeover, clean after the drain
    s2 = T.mixs(mask, s1, des)
    d = T.m("DIVIDE", T.m("SUBTRACT", sz, front), 0.0016)
    edge = T.m("MULTIPLY", T.m("EXPONENT", T.m("MULTIPLY", T.m("MULTIPLY", d, d), -1.0)), T.keyed(f"{name}_glow", GLOW))
    em = T.n("ShaderNodeEmission"); em.inputs["Color"].default_value = C["glow"]; T.link(T.m("MULTIPLY", edge, 7.0), em.inputs["Strength"])
    add = T.n("ShaderNodeAddShader"); T.link(s2, add.inputs[0]); T.link(em.outputs[0], add.inputs[1])
    o = T.n("ShaderNodeOutputMaterial"); T.link(add.outputs[0], o.inputs["Surface"])
    disp = DISP.pop("h", None)
    if disp is not None:     # raised panels, mesh depth and stitching become real geometry once the design appears
        dn = T.n("ShaderNodeDisplacement"); dn.inputs["Midlevel"].default_value = 0.0; dn.inputs["Scale"].default_value = 1.0
        T.link(T.m("MULTIPLY", disp, mask), dn.inputs["Height"]); T.link(dn.outputs[0], o.inputs["Displacement"])
        try: m.displacement_method = "BUMP"      # faked with the textured material (bump only): same look, much faster
        except AttributeError: m.cycles.displacement_method = "BUMP"
    return m

def shader(fn): fn.shader = True; return fn
def mulc(T, col, fac):
    node = T.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); node.inputs[0].default_value = 1.0
    T._in(node, 6, col); T._in(node, 7, fac); return node.outputs[2]
def ao(T, col, amt=0.45):
    a = T.n("ShaderNodeAmbientOcclusion"); a.samples = 8; a.inputs["Distance"].default_value = 0.012
    return mulc(T, col, T.m("ADD", 1.0 - amt, T.m("MULTIPLY", a.outputs["AO"], amt)))
def vor(T, sx, sy, sz, scale, feature="F1"):
    v = T.n("ShaderNodeTexVoronoi", feature=feature); T.link(T.combine(sx, sy, sz), v.inputs["Vector"]); v.inputs["Scale"].default_value = scale
    return v.outputs["Distance"]
def nse(T, sx, sy, sz, scale, detail=4):
    n = T.n("ShaderNodeTexNoise"); T.link(T.combine(sx, sy, sz), n.inputs["Vector"]); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
    return n.outputs["Fac"]
def knit(T, sx, sy, sz, f=2600.0):
    """engineered knit: wavy wales x courses"""
    a = T.m("SINE", T.m("ADD", T.m("MULTIPLY", sx, f), T.m("MULTIPLY", T.m("SINE", T.m("MULTIPLY", sz, f)), 1.3)))
    b = T.m("SINE", T.m("MULTIPLY", T.m("ADD", sz, T.m("MULTIPLY", sy, 0.6)), f * 0.5))
    return T.m("MULTIPLY", T.m("ADD", a, 1.0), T.m("ADD", b, 1.4))
def smoothstep_n(T, x, w):   # 0..1 ramp of x over width w (x>0 -> 1)
    return T.m("DIVIDE", T.m("ADD", x, 0.0), w, clamp=True)
def htop_node(T, sx):
    fc = T.n("ShaderNodeFloatCurve"); cur = fc.mapping.curves[0]
    pts = [(i / 12, (crs(HTAB, i / 12) + spring(i / 12) - 0.02) / 0.13) for i in range(13)]
    while len(cur.points) < len(pts): cur.points.new(0.5, 0.5)
    for pt, (x, y) in zip(cur.points, pts): pt.location = (x, y)
    fc.mapping.update(); T.link(T.m("DIVIDE", sx, L, clamp=True), fc.inputs["Value"])
    return T.m("ADD", T.m("MULTIPLY", fc.outputs[0], 0.13), 0.02)

LOGO = os.path.join(HERE, "assets", "ooze_logo.png")   # original made-up brand mark (assets/ooze_logo.svg)
LOGO_IMG = bpy.data.images.load(LOGO); LOGO_ASPECT = 1600 / 520
def logo_alpha(T, sx, sy, sz, x0, z0, h):
    """planar side print of the logo (read correctly on both sides of the shoe)"""
    w = h * LOGO_ASPECT; u = T.m("DIVIDE", T.m("SUBTRACT", sx, x0), w); v = T.m("DIVIDE", T.m("SUBTRACT", sz, z0), h)
    side = T.m("GREATER_THAN", sy, 0.0)
    u = T.m("ADD", u, T.m("MULTIPLY", side, T.m("SUBTRACT", 1.0, T.m("MULTIPLY", u, 2.0))))
    tex = T.n("ShaderNodeTexImage"); tex.image = LOGO_IMG; tex.extension = "CLIP"; tex.interpolation = "Cubic"
    T.link(T.combine(u, v, 0.0), tex.inputs["Vector"])
    return T.m("MULTIPLY", tex.outputs["Alpha"], T.m("GREATER_THAN", T.m("ABSOLUTE", sy), 0.022))
def breathable(T, sx, sy, sz, scale=380.0):
    """engineered knit: V-stitch columns (chevron loops) with a brickwork grid of small open holes; returns (hole 0..1, height 0..1)"""
    f = scale * 2.4
    c = T.m("MULTIPLY", T.m("ADD", sx, T.m("MULTIPLY", sy, 0.35)), f)
    x = T.m("SUBTRACT", T.m("FRACT", c), 0.5)
    r = T.m("ADD", T.m("MULTIPLY", sz, f * 1.5), T.m("MULTIPLY", T.m("ABSOLUTE", x), 1.2))
    loop = T.m("MULTIPLY", T.m("ADD", 0.5, T.m("MULTIPLY", T.m("COSINE", T.m("MULTIPLY", r, 6.2832)), 0.5)),
               T.m("SQRT", T.m("SUBTRACT", 1.0, T.m("MULTIPLY", T.m("MULTIPLY", x, x), 4.0), clamp=True)))
    hc = T.m("DIVIDE", c, 3.0); hr = T.m("ADD", T.m("DIVIDE", T.m("MULTIPLY", sz, f * 1.5), 4.0), T.m("MULTIPLY", T.m("FLOOR", hc), 0.5))
    hx = T.m("SUBTRACT", T.m("FRACT", hc), 0.5); hy = T.m("SUBTRACT", T.m("FRACT", hr), 0.5)
    hd = T.m("SQRT", T.m("ADD", T.m("MULTIPLY", hx, hx), T.m("MULTIPLY", T.m("MULTIPLY", hy, hy), 0.56)))
    hole = T.m("SUBTRACT", 1.0, T.m("DIVIDE", T.m("SUBTRACT", hd, 0.15), 0.05, clamp=True))
    return hole, T.m("MULTIPLY", loop, T.m("SUBTRACT", 1.0, hole))

def lining(T, sx, sy, sz):
    return bsdf(T, (0.025, 0.025, 0.027, 1), 0.9, Sheen_Weight=0.6, Normal=bump(T, knit(T, sx, sy, sz, 3600.0), 0.3, 0.0002))
def backfacing(T): return T.n("ShaderNodeNewGeometry").outputs["Backfacing"]
def gauss(T, x, w): d = T.m("DIVIDE", x, w); return T.m("EXPONENT", T.m("MULTIPLY", T.m("MULTIPLY", d, d), -1.0))
def inside(T, sd, w=0.0003): return T.m("SUBTRACT", 0.5, T.m("DIVIDE", sd, w), clamp=True)

# signature design: a glossy black overlay that DRIPS down from the collar and eyestay over white knit (the slime, set solid)
DRIP_DESIGN = [(0.008, 0.006, 0.012), (0.024, 0.008, 0.021), (0.046, 0.006, 0.011), (0.064, 0.009, 0.017), (0.086, 0.006, 0.014),
               (0.101, 0.005, 0.007), (0.172, 0.006, 0.009), (0.188, 0.008, 0.010)]          # (x centre, half width, length) in m
def topline_z(u):
    a = crs(open_tab, u); return sect(max(u, 0.02), a)[2] if a > 0.02 else sect(u, 0.0)[2]
def curve_node(T, sx, fn, n=24):
    """float curve of fn(u) (heights in m) along the shoe, sampled at n points"""
    fc = T.n("ShaderNodeFloatCurve"); cur = fc.mapping.curves[0]
    pts = [(i / (n - 1), (fn(i / (n - 1)) - 0.02) / 0.13) for i in range(n)]
    while len(cur.points) < len(pts): cur.points.new(0.5, 0.5)
    for pt, (x, y) in zip(cur.points, pts): pt.location = (x, y)
    fc.mapping.update(); T.link(T.m("DIVIDE", sx, L, clamp=True), fc.inputs["Value"])
    return T.m("ADD", T.m("MULTIPLY", fc.outputs[0], 0.13), 0.02)

@shader
def upper_shader(T, sx, sy, sz):
    base = curve_node(T, sx, lambda u: topline_z(min(u, 0.75)) - (0.012 if u < 0.36 else 0.016))
    drop = None
    for c, w, ln in DRIP_DESIGN:
        t = T.m("DIVIDE", T.m("SUBTRACT", sx, c), w)
        d = T.m("MULTIPLY", T.m("SQRT", T.m("SUBTRACT", 1.0, T.m("MULTIPLY", t, t), clamp=True)), ln)
        drop = d if drop is None else T.m("MAXIMUM", drop, d)
    dripline = T.m("SUBTRACT", base, drop)
    sd_d = T.m("MAXIMUM", T.m("SUBTRACT", dripline, sz), T.m("SUBTRACT", T.m("SUBTRACT", sx, 0.200), T.m("MULTIPLY", T.m("SUBTRACT", sz, 0.070), 0.8)))
    zline = T.m("ADD", T.m("ADD", 0.040, T.m("MULTIPLY", T.m("EXPONENT", T.m("MULTIPLY", sx, -8.0)), 0.010)),
                T.m("MULTIPLY", T.m("DIVIDE", T.m("SUBTRACT", sx, 0.255), 0.045, clamp=True), 0.009))   # rises round the toe
    sd_a = T.m("SUBTRACT", sz, zline)                                                                  # suede bumper all round
    sd = T.m("MINIMUM", sd_a, sd_d)
    mask = inside(T, sd); gloss = inside(T, sd_d); suede = T.m("MULTIPLY", inside(T, sd_a), T.m("SUBTRACT", 1.0, gloss))
    raised = T.m("DIVIDE", T.m("MULTIPLY", sd, -1.0), 0.0008, clamp=True)
    dash = T.m("GREATER_THAN", T.m("SINE", T.m("MULTIPLY", T.m("ADD", T.m("MULTIPLY", sx, 0.8), sz), 2600.0)), 0.15)
    stitch = T.m("MULTIPLY", T.m("MULTIPLY", T.m("ADD", gauss(T, T.m("ADD", sd_a, 0.0012), 0.0002), gauss(T, T.m("ADD", sd_a, 0.0024), 0.0002)), dash),
                 T.m("SUBTRACT", 1.0, gloss))
    zone = T.m("MULTIPLY", T.m("MULTIPLY", T.m("GREATER_THAN", sx, 0.205), T.m("LESS_THAN", sx, 0.262)), T.m("GREATER_THAN", sz, 0.046))
    holes = T.m("MULTIPLY", T.m("LESS_THAN", vor(T, sx, sy, sz, 650.0), 0.2), T.m("MULTIPLY", zone, T.m("SUBTRACT", 1.0, mask)))
    cz = T.m("MULTIPLY", T.m("MULTIPLY", T.m("GREATER_THAN", sx, 0.19), T.m("LESS_THAN", sx, 0.25)), T.m("GREATER_THAN", sz, 0.042))
    crease = T.m("MULTIPLY", T.m("POWER", T.m("ABSOLUTE", T.m("SINE", T.m("ADD", T.m("MULTIPLY", sx, 420.0),
                 T.m("MULTIPLY", nse(T, sx, T.m("MULTIPLY", sy, 3.0), sz, 40.0, 2), 9.0)))), 8.0), cz)
    sds = T.m("SUBTRACT", sx, T.m("ADD", 0.232, T.m("MULTIPLY", T.m("SUBTRACT", sz, 0.05), 0.35)))         # vamp seam: groove + two stitch rows
    dash2 = T.m("GREATER_THAN", T.m("SINE", T.m("MULTIPLY", sz, 2600.0)), 0.1)
    seam = T.m("MULTIPLY", T.m("ADD", gauss(T, sds, 0.00035), T.m("MULTIPLY", gauss(T, T.m("SUBTRACT", T.m("ABSOLUTE", sds), 0.0013), 0.00018), dash2)),
                T.m("MULTIPLY", T.m("SUBTRACT", 1.0, mask), T.m("GREATER_THAN", sz, 0.044)))
    mhole, mh = breathable(T, sx, sy, sz)
    logo = T.m("MULTIPLY", logo_alpha(T, sx, sy, sz, 0.113, 0.0478, 0.0138), T.m("SUBTRACT", 1.0, mask))
    fuzz = nse(T, sx, sy, sz, 2600.0, 2); orange = nse(T, sx, sy, sz, 900.0, 3)
    DISP["h"] = T.m("ADD", T.m("ADD", T.m("MULTIPLY", raised, 0.0011), T.m("MULTIPLY", logo, 0.00050)),
                    T.m("ADD", T.m("MULTIPLY", T.m("MULTIPLY", mh, 0.00032), T.m("SUBTRACT", 1.0, mask)),
                        T.m("ADD", T.m("MULTIPLY", holes, -0.00035), T.m("ADD", T.m("MULTIPLY", stitch, -0.00012), T.m("ADD", T.m("MULTIPLY", crease, -0.0006), T.m("MULTIPLY", seam, -0.00045))))))
    micro = T.m("ADD", T.m("ADD", T.m("MULTIPLY", orange, T.m("MULTIPLY", gloss, 0.06)), T.m("MULTIPLY", fuzz, T.m("MULTIPLY", suede, 0.5))),
                T.m("MULTIPLY", knit(T, sx, sy, sz, 5200.0), T.m("MULTIPLY", T.m("SUBTRACT", 1.0, mask), 0.05)))
    nrm = bump(T, micro, 0.5, 0.00015)
    var = T.m("ADD", 0.90, T.m("MULTIPLY", nse(T, sx, sy, sz, 300.0), 0.10))
    under = T.m("MULTIPLY", T.m("SUBTRACT", 1.0, T.m("MULTIPLY", mhole, 0.62)), T.m("ADD", 0.80, T.m("MULTIPLY", mh, 0.20)))   # yarn shading
    white = ao(T, mulc(T, (0.86, 0.85, 0.82, 1), T.m("MULTIPLY", T.m("MULTIPLY", var, under), T.m("SUBTRACT", 1.0, T.m("MULTIPLY", holes, 0.75)))), 0.6)
    knit_b = bsdf(T, white, 0.85, Sheen_Weight=1.0, Sheen_Roughness=0.6, Normal=nrm)
    thread = (0.80, 0.80, 0.78, 1)
    scol = ao(T, T.mixc(stitch, T.mixc(fuzz, (0.005, 0.005, 0.006, 1), (0.014, 0.014, 0.015, 1)), thread), 0.4)
    suede_b = bsdf(T, scol, 0.95, Sheen_Weight=0.35, Sheen_Roughness=0.3, Normal=nrm)
    patent = bsdf(T, ao(T, (0.004, 0.004, 0.005, 1), 0.3), 0.45, Specular_IOR_Level=0.03, Sheen_Weight=0.25, Sheen_Roughness=0.4, Normal=nrm)   # satin black drips (low reflectance so it stays black under the softbox)
    printed = bsdf(T, (0.008, 0.008, 0.009, 1), 0.28, Coat_Weight=0.3, Coat_Roughness=0.2, Normal=nrm)
    rim = T.m("MULTIPLY", gauss(T, T.m("ADD", sd_d, 0.00045), 0.00030), gloss)          # a wet bead along every drip edge
    wet = bsdf(T, (0.004, 0.004, 0.005, 1), 0.06, Coat_Weight=1.0, Coat_Roughness=0.02, Normal=nrm)
    sh = T.mixs(mask, knit_b, T.mixs(suede, T.mixs(rim, patent, wet), suede_b))
    return T.mixs(backfacing(T), T.mixs(logo, sh, printed), lining(T, sx, sy, sz))

@shader
def collar_shader(T, sx, sy, sz):
    nrm = bump(T, knit(T, sx, sy, sz, 3400.0), 0.35, 0.0003)
    return bsdf(T, ao(T, (0.012, 0.012, 0.013, 1)), 0.85, Sheen_Weight=1.0, Sheen_Roughness=0.35, Normal=nrm)

@shader
def tongue_shader(T, sx, sy, sz):
    band = T.m("GREATER_THAN", sz, 0.118)
    hole, mh = breathable(T, sx, sy, sz, 460.0)
    lw = 0.030; lh = lw / LOGO_ASPECT                       # woven label: logo projected across the tongue (front view)
    tex = T.n("ShaderNodeTexImage"); tex.image = LOGO_IMG; tex.extension = "CLIP"
    T.link(T.combine(T.m("DIVIDE", T.m("ADD", sy, lw / 2), lw), T.m("DIVIDE", T.m("SUBTRACT", sz, 0.1205), lh), 0.0), tex.inputs["Vector"])
    lab = T.m("MULTIPLY", tex.outputs["Alpha"], band)
    DISP["h"] = T.m("ADD", T.m("MULTIPLY", T.m("MULTIPLY", mh, 0.00028), T.m("SUBTRACT", 1.0, band)), T.m("ADD", T.m("MULTIPLY", band, 0.0006), T.m("MULTIPLY", lab, 0.0001)))
    nrm = bump(T, T.m("ADD", knit(T, sx, sy, sz, 5000.0), T.m("MULTIPLY", T.m("SINE", T.m("MULTIPLY", sy, 9000.0)), band)), 0.25, 0.0001)
    k = bsdf(T, ao(T, mulc(T, (0.86, 0.85, 0.82, 1), T.m("SUBTRACT", 1.0, T.m("MULTIPLY", hole, 0.6))), 0.6), 0.85, Sheen_Weight=1.0, Sheen_Roughness=0.6, Normal=nrm)
    l = bsdf(T, ao(T, T.mixc(lab, (0.012, 0.012, 0.013, 1), (0.82, 0.82, 0.80, 1))), 0.7, Sheen_Weight=0.8, Normal=nrm)   # woven, not plastic
    return T.mixs(backfacing(T), T.mixs(band, k, l), lining(T, sx, sy, sz))

@shader
def midsole_shader(T, sx, sy, sz):
    """moulded foam: fine pores, flowing sculpted ribs, a sharper rib at the heel"""
    zg = T.m("ADD", T.m("ADD", 0.0215, T.m("MULTIPLY", T.m("SINE", T.m("ADD", T.m("MULTIPLY", sx, 21.0), 0.9)), 0.0045)),
             T.m("MULTIPLY", T.m("DIVIDE", T.m("SUBTRACT", sx, 0.22), 0.08, clamp=True), 0.010))          # one flowing sculpted groove
    pod = T.m("MULTIPLY", gauss(T, T.m("SUBTRACT", sz, T.m("SUBTRACT", 0.031, T.m("MULTIPLY", sx, 0.05))), 0.0010), T.m("LESS_THAN", sx, 0.12))
    rib = T.m("SUBTRACT", 1.0, T.m("ADD", gauss(T, T.m("SUBTRACT", sz, zg), 0.0013), T.m("MULTIPLY", pod, 0.6)))
    pores = vor(T, sx, sy, sz, 5000.0)
    nrm = bump(T, T.m("ADD", T.m("MULTIPLY", rib, 0.6), T.m("MULTIPLY", pores, 0.08)), 0.7, 0.0008)
    spk = nse(T, sx, sy, sz, 900.0, 0)
    dark = T.m("GREATER_THAN", spk, 0.70); lite = T.m("LESS_THAN", spk, 0.30)
    base = mulc(T, (0.80, 0.79, 0.76, 1), T.m("ADD", 0.94, T.m("MULTIPLY", nse(T, sx, sy, sz, 120.0), 0.06)))
    col = ao(T, T.mixc(T.m("MULTIPLY", dark, 0.85), T.mixc(T.m("MULTIPLY", lite, 0.5), base, (0.9, 0.9, 0.88, 1)), (0.06, 0.06, 0.065, 1)), 0.5)
    return bsdf(T, col, 0.66, Sheen_Weight=0.2, Normal=nrm)

@shader
def outsole_shader(T, sx, sy, sz):
    lugs = T.m("LESS_THAN", vor(T, sx, sy, T.m("MULTIPLY", sz, 0.2), 230.0, "DISTANCE_TO_EDGE"), 0.06)
    side = T.m("GREATER_THAN", T.m("SINE", T.m("MULTIPLY", T.m("ADD", sx, T.m("MULTIPLY", sz, 0.4)), 520.0)), 0.55)
    nrm = bump(T, T.m("ADD", T.m("MULTIPLY", lugs, -1.0), T.m("MULTIPLY", side, -0.6)), 0.9, 0.0012)
    return bsdf(T, ao(T, (0.010, 0.010, 0.011, 1), 0.5), T.m("ADD", 0.72, T.m("MULTIPLY", nse(T, sx, sy, sz, 400.0), 0.15)), Sheen_Weight=0.2, Normal=nrm)

@shader
def heel_shader(T, sx, sy, sz):
    peb = vor(T, sx, sy, sz, 1300.0)
    logo = logo_alpha(T, sx, sy, sz, 0.005, 0.0495, 0.0090)
    nrm = bump(T, T.m("ADD", T.m("MULTIPLY", peb, 0.3), T.m("MULTIPLY", logo, 0.6)), 0.6, 0.0004)
    leather = bsdf(T, ao(T, C["black"]), T.m("ADD", 0.32, T.m("MULTIPLY", peb, 0.15)), Coat_Weight=0.25, Coat_Roughness=0.25, Normal=nrm)
    DISP["h"] = T.m("MULTIPLY", logo, 0.00022)
    return T.mixs(backfacing(T), T.mixs(logo, leather, bsdf(T, (0.80, 0.80, 0.78, 1), 0.35, Coat_Weight=0.3, Normal=nrm)), lining(T, sx, sy, sz))

@shader
def tab_shader(T, sx, sy, sz):
    nrm = bump(T, T.m("SINE", T.m("MULTIPLY", T.m("ADD", sx, sz), 2800.0)), 0.5, 0.0003)
    return bsdf(T, ao(T, (0.02, 0.02, 0.022, 1)), 0.7, Sheen_Weight=0.8, Normal=nrm)

@shader
def lace_shader(T, sx, sy, sz):
    b1 = T.m("SINE", T.m("MULTIPLY", T.m("ADD", T.m("ADD", sx, sy), sz), 4200.0))
    b2 = T.m("SINE", T.m("MULTIPLY", T.m("SUBTRACT", T.m("ADD", sx, sz), sy), 4200.0))
    nrm = bump(T, T.m("MULTIPLY", b1, b2), 0.6, 0.0003)
    return bsdf(T, ao(T, (0.80, 0.80, 0.78, 1), 0.5), 0.78, Sheen_Weight=0.8, Sheen_Roughness=0.4, Normal=nrm)   # white laces over the black overlay

@shader
def eyelet_shader(T, sx, sy, sz):
    return bsdf(T, (0.30, 0.30, 0.32, 1), 0.26, Metallic=1.0)

# ---------------- build the parts ----------------
parts = {}
wrap = lambda u: 0.0085 + 0.011 * max(0.0, (u - 0.86) / 0.14) ** 1.5 + 0.007 * max(0.0, (0.07 - u) / 0.07) ** 1.5
o = slab("outsole", lambda u: W(u) + 0.0058, [(0.0, 0.004), (0.0015, 0.001), (0.004, 0.0), (wrap, 0.0), (lambda u: wrap(u) + 0.001, 0.0016)], None)
parts["outsole"] = o
o = slab("midsole", lambda u: W(u) + 0.005, [(0.0085, 0.002), (0.010, 0.0), (lambda u: 0.5 * (0.010 + zm(u)), -0.0018),
                                              (lambda u: zm(u) - 0.002, 0.0), (lambda u: zm(u), 0.002)], None)
parts["midsole"] = o
NU, NV = 80, 52
U_UP = cosu(NU, 0.003, 0.997); PH = [-math.pi / 2 + math.pi * j / (NV - 1) for j in range(NV)]
open_tab = [(0.0, 0.0), (0.015, 0.62), (0.08, 0.98), (0.28, 0.98), (0.38, 0.52), (0.42, 0.24), (0.62, 0.20), (0.66, 0.0), (1.0, 0.0)]
def up_keep(i, j):
    u = lerp(U_UP[int(i)], U_UP[min(int(i) + 1, NU - 1)], 0.5); ph = lerp(PH[int(j)], PH[min(int(j) + 1, NV - 1)], 0.5)
    return not (0.012 < u < 0.66 and abs(ph) < crs(open_tab, u))
bm = grid("upper", lambda i, j: sect(U_UP[i], PH[j]), NU, NV, None, keep=up_keep)
before = set(bm.faces)
cpath = [sect(u, -crs(open_tab, u) * 0.96) for u in [0.40 - 0.385 * k / 24 for k in range(25)]] + \
        [sect(u, crs(open_tab, u) * 0.96) for u in [0.015 + 0.385 * k / 24 for k in range(1, 25)]]
tube(bm, [(x, y, z + 0.0016) for x, y, z in cpath], 0.0068, 12)        # padded collar (puffy)
for f in bm.faces:
    if f not in before: f.material_index = 1
parts["upper"] = obj_from_bm("upper", bm); add_mods(parts["upper"], 0.0028)
U_T = cosu(22, 0.33, 0.70); PT = [-0.42 + 0.84 * j / 11 for j in range(12)]
bm = grid("tongue", lambda i, j: (lambda p: (p[0], p[1], p[2] + 0.014 * max(0.0, (0.42 - U_T[i]) / 0.09)))(sect(U_T[i], PT[j], 0.975)), 22, 12, None)
parts["tongue"] = obj_from_bm("tongue", bm); add_mods(parts["tongue"], 0.004)
# heel counter: two side strips from the sole up to a sweeping top line, slightly proud of the upper
U_H = cosu(18, 0.002, 0.18)
def heel_pt(i, j, side):
    u = U_H[i]; zb = zm(u) - 0.004; ht = crs(HTAB, u) - zb
    frac = max(0.06, 0.70 * (1 - (u / 0.18) ** 2.2)); ph0 = math.acos(min(1.0, frac ** (NEXP / 2)))
    ph = side * (ph0 + (math.pi / 2 - ph0) * j / 7)
    return sect(u, ph, 1.035)
bmh = bmesh.new()
for side in (-1, 1):
    vs = [[bmh.verts.new(heel_pt(i, j, side)) for j in range(8)] for i in range(18)]
    for i in range(17):
        for j in range(7): bmh.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
bf, bv = set(bmh.faces), set(bmh.verts); h0 = crs(HTAB, 0) + spring(0)
loop = [(-0.0015 + 0.0050 * math.cos(math.radians(a)) - 0.25 * (0.009 * math.sin(math.radians(a))), 0.0,
         h0 + 0.004 + 0.009 * math.sin(math.radians(a))) for a in range(-80, 265, 15)]
loop = [(loop[0][0], 0.0, h0 - 0.012)] + loop + [(loop[-1][0], 0.0, h0 - 0.012)]
tube(bmh, loop, 0.0011, 8)
for v in bmh.verts:
    if v not in bv: v.co.y *= 5.0          # flatten into a thin fabric tab
for f in bmh.faces:
    if f not in bf: f.material_index = 1
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
parts["heel"] = obj_from_bm("heel", bmh); add_mods(parts["heel"], 0.003); parts["heel"].modifiers["Solid"].use_even_offset = False  # even offset spikes the thin strap
# laces: five criss-crossing cords over the tongue
bml = bmesh.new()
for k in range(5):
    ua, ub = 0.44 + 0.047 * k, 0.44 + 0.047 * k + 0.03
    if k % 2: ua, ub = ub, ua
    pts = []
    for s in range(11):
        t = s / 10; ph = lerp(-0.30, 0.30, t); u = lerp(ua, ub, t)
        x, y, z = sect(u, ph, 1.0); pts.append((x, y, z + 0.0006 + 0.0048 * math.sin(math.pi * t) ** 0.5))   # sinks into each eyelet
    tube(bml, pts, 0.0027, 10, flat=0.38)
for side in (-1, 1):                      # loose lace ends from the top eyelets, hanging over the side
    c0 = Vector(sect(0.44, side * 0.30)); out_ = Vector((0, side * 1.0, 0)); pts = []
    for s_ in range(12):
        t = s_ / 11; pts.append(tuple(c0 + Vector((-0.012 * t + 0.004 * math.sin(3 * t), 0, 0.0035 * math.sin(math.pi * min(1, t * 1.6)) - 0.040 * t ** 1.6)) + out_ * (0.008 + 0.030 * t ** 0.6)))
    tube(bml, pts, 0.0027, 10, flat=0.38)
bf = set(bml.faces)
for side in (-1, 1):                      # plastic aglets on the lace ends (metal slot)
    c0 = Vector(sect(0.44, side * 0.30)); out_ = Vector((0, side * 1.0, 0))
    e = [tuple(c0 + Vector((-0.012 * t + 0.004 * math.sin(3 * t), 0, 0.0035 * math.sin(math.pi * min(1, t * 1.6)) - 0.040 * t ** 1.6)) + out_ * (0.008 + 0.030 * t ** 0.6)) for t in (0.93, 1.0, 1.06)]
    tube(bml, e, 0.0016, 10)
for k in range(5):
    for u in (0.44 + 0.047 * k, 0.44 + 0.047 * k + 0.03):
        for ph in (-0.30, 0.30):
            c = Vector(sect(u, ph)); du = Vector(sect(u + 0.004, ph)) - Vector(sect(u - 0.004, ph))
            dp = Vector(sect(u, ph + 0.02)) - Vector(sect(u, ph - 0.02)); n = du.cross(dp).normalized()
            if n.z < 0: n = -n
            a = du.normalized(); b2 = n.cross(a)
            ring = [tuple(c + n * 0.0009 + 0.0027 * (math.cos(2 * math.pi * i / 14) * a + math.sin(2 * math.pi * i / 14) * b2)) for i in range(15)]
            tube(bml, ring, 0.0007, 6)
for f in bml.faces:
    if f not in bf: f.material_index = 1
parts["laces"] = obj_from_bm("laces", bml); add_mods(parts["laces"], 0.0, 1)
for nm in ("outsole", "midsole"): add_mods(parts[nm], 0.0)

DESIGN = {"outsole": [outsole_shader], "midsole": [midsole_shader], "upper": [upper_shader, collar_shader],
          "heel": [heel_shader, tab_shader], "tongue": [tongue_shader], "laces": [lace_shader, eyelet_shader]}
for nm, o in parts.items():
    for k, d in enumerate(DESIGN[nm]): o.data.materials.append(skin(f"skin_{nm}{k}", o.location, d, 0.5))

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
AMPS, SEEDS = {}, {}

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
    XF[nm] = (locs, rots, home); AMPS[nm] = amps; SEEDS[nm] = idx * 3.7

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
    lnf = lambda f: L0 * (0.55 + 0.45 * math.sin(f * 0.12 + ph)) * (1 + 0.6 * smooth(win(f, M0, M1)))
    for f in F:
        ln = lnf(f) * smooth(win(f, 30, 46))
        if f >= SET: ln = lnf(SET) * (1 + 0.5 * smooth(win(f, SW0, SW1 - 6))) * (1 - smooth(win(f, SW1 - 5, SW1 + 3)))   # frozen at the hit, stretch as the slime drains, then let go
        vals.append((1, 1, max(0.02, ln / 0.01) if ln > 1e-4 else 0.001))
    keys(dr, "scale", vals, 3)

def world_pt(nm, f, local):
    locs, rots, home = XF[nm]; return Vector(locs[f - 1]) + Euler(rots[f - 1]).to_matrix() @ Vector(local)

def strand(name, nm, local, f_on, f_off, target, r0, snap=None, K=9, beads=0):
    """a slime tendril from a point on a part (moving) to a fixed target; necks in the middle; snaps or merges"""
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.001; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new("NURBS"); sp.points.add(K - 1); sp.order_u = 4; sp.use_endpoint_u = True
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
            sd_ = (A - T).cross(Vector((0, 0, 1))); sd_ = sd_.normalized() if sd_.length > 1e-6 else Vector((1, 0, 0))
            P += sd_ * 0.10 * ln * math.sin(math.pi * s) * math.sin(s * math.pi * 2.5 + f * 0.22 + (hash(name) % 100) * 0.1) * on   # writhes like a tentacle
            P.z -= 0.25 * ln * math.sin(math.pi * s) * (0.6 + 1.2 * sn)
            neck = 0.35 + 0.65 * abs(2 * s - 1) ** 1.4
            r = thick * neck * (1 - sn * (1 - abs(2 * s - 1) ** 0.4))
            if beads: r *= 1 + 1.1 * max(0.0, math.sin(math.pi * s * beads * 2 + f * 0.05)) ** 8 * (0.2 < s < 0.8)   # slime beading
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
    hp = rnd.choice(low); fp = home + hp; fp = Vector((fp.x + rnd.uniform(-0.05, 0.05), fp.y - 0.06, 0.004))
    strand(f"hero_{nm}", nm, hp, a0 - 10, a1 + 1, fp, 5.5, K=13)          # a thick tentacle from the floor hauls the part in
    for k, lp in enumerate(rnd.sample(verts, 5)):                       # extra thin, beaded threads
        strand(f"thread_{nm}{k}", nm, lp, a0 - 4 + k, a1 - 1, home + lp + Vector((rnd.uniform(-0.01, 0.01), 0, -0.002)), 1.1, K=17, beads=3)
# drops falling off the parts as they fly in, splashing flat on the floor
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.0024)
drop_me = bpy.data.meshes.new("drop"); bm.to_mesh(drop_me); bm.free()
for p_ in drop_me.polygons: p_.use_smooth = True
drop_me.materials.append(slime_mat)
for nm, o in parts.items():
    a0, a1 = CFG["assemble"][nm]; verts = [v.co.copy() for v in o.data.vertices]
    low = sorted(verts, key=lambda c: c.z)[: max(8, len(verts) // 6)]
    for k in range(3):
        rel = int(a0 + (a1 - a0) * (0.15 + 0.25 * k)); P0 = world_pt(nm, rel, rnd.choice(low))
        if P0.z < 0.02: continue
        d = link_obj(f"drop_{nm}{k}", drop_me); g = 2.6; t_hit = math.sqrt(2 * (P0.z - 0.0012) / g) * FPS
        locs, scs = [], []
        for f in F:
            t = (f - rel) / FPS
            if f < rel: locs.append(tuple(P0)); scs.append((0.001,) * 3)
            elif f - rel < t_hit:
                locs.append((P0.x, P0.y, P0.z - 0.5 * g * t * t)); st_ = 1 + 0.5 * min(1, t * 3); scs.append((1 / st_ ** 0.5, 1 / st_ ** 0.5, st_))
            else:
                k2 = f - rel - t_hit; spread = 1 + 2.6 * (1 - math.exp(-k2 / 2.0)); fade = 1 - smooth(win(k2, 6, 16))
                locs.append((P0.x, P0.y, 0.0006)); scs.append((max(0.001, spread * fade), max(0.001, spread * fade), max(0.001, 0.22 * fade)))
        keys(d, "location", locs, 3); keys(d, "scale", scs, 3)

# ---------------- VENOM: a web of thin, glossy, branching veins (grammar of the classic "venom effect") ----------------
# floor veins surge in from the dark and climb the shoe; a vein web covers every part (and melts / flies with it);
# at the drain the veins slide back down off the shoe and retreat into the floor.
vm_, T = new_mat("venom")
vco = T.n("ShaderNodeTexCoord").outputs["Object"]; vn = T.n("ShaderNodeTexNoise"); T.link(vco, vn.inputs["Vector"]); vn.inputs["Scale"].default_value = 900.0
out(T, bsdf(T, (0.002, 0.0025, 0.005, 1), 0.06, Coat_Weight=1.0, Coat_Roughness=0.008, Specular_IOR_Level=0.25, Normal=bump(T, vn.outputs["Fac"], 0.25, 0.0002)))
VEIN_R = 0.0016
def vein_curve(name, splines, depth, parent=None):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = depth; cu.bevel_resolution = 2
    cu.use_fill_caps = True; cu.bevel_factor_mapping_end = "SPLINE"; cu.bevel_factor_mapping_start = "SPLINE"
    for pts in splines:
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1); sp.use_smooth = True
        for p_, (co_, r_) in zip(sp.points, pts): p_.co = (co_.x, co_.y, co_.z, 1.0); p_.radius = max(0.05, r_)
    o = link_obj(name, cu); cu.materials.append(vm_)
    if parent is not None: o.parent = parent
    return o

def surface_veins(part, count, steps, step, climb, seed):
    me = part.data; vs = [v.co.copy() for v in me.vertices]
    bvh = BVHTree.FromPolygons(vs, [tuple(p_.vertices) for p_ in me.polygons])
    zl = sorted(c.z for c in vs)[len(vs) // 5]; lows = [c for c in vs if c.z <= zl]
    rg = random.Random(seed); splines = []
    def walk(p, d, n, r0, depth=0):
        pts = []
        for i in range(n):
            loc, nrm, _, _ = bvh.find_nearest(p)
            if loc is None: break
            nrm = nrm.normalized(); pts.append((loc + nrm * 0.0008, r0 * (1 - 0.85 * i / max(1, n - 1))))
            t = d - nrm * d.dot(nrm); t = t.normalized() if t.length > 1e-6 else nrm.orthogonal().normalized()
            side = nrm.cross(t)
            d = (t + side * rg.uniform(-0.6, 0.6) + Vector((0, 0, climb))).normalized(); p = loc + d * step
            if depth < 2 and i > 2 and n - i > 5 and rg.random() < 0.14:
                walk(loc, (d + side * rg.choice((-1, 1)) * 1.1).normalized(), int((n - i) * 0.65), pts[-1][1] * 0.75, depth + 1)
        if len(pts) >= 3: splines.append(pts)
    for k in range(count):
        st0 = rg.choice(lows) if rg.random() < 0.75 else rg.choice(vs)
        walk(st0, Vector((rg.uniform(-1, 1), rg.uniform(-1, 1), 0.5)).normalized(), steps, 1.0)
    return splines

def floor_veins(count, seed):
    rg = random.Random(seed); splines = []
    def trail(p, tgt, r_out, r_in, wob=0.5):
        pts = []; head = (tgt - p).normalized(); n0 = max(4, int((tgt - p).length / 0.007))
        for i in range(n0 * 3):
            to = tgt - p
            if to.length < 0.006: break
            head = head * 0.72 + to.normalized() * 0.28 + Vector((rg.uniform(-1, 1), rg.uniform(-1, 1), 0)) * wob * 0.5
            head.z = 0; head.normalize(); r = lerp(r_out, r_in, min(1.0, i / n0))
            pts.append((Vector((p.x, p.y, VEIN_R * 1.4 * r * 0.8)), r)); p = p + head * 0.007
        pts.append((Vector((tgt.x, tgt.y, VEIN_R * 1.4 * r_in * 0.8)), r_in)); return pts
    for k in range(count):
        u = rg.uniform(0.03, 0.97); side = rg.choice((-1, 1)); tgt = Vector((u * L, side * (W(u) + 0.006), 0.0))
        ang = math.atan2(side * 1.0, (u - 0.5) * 1.6) + rg.uniform(-0.7, 0.7); dist = rg.uniform(0.14, 0.60)
        start = tgt + Vector((math.cos(ang), math.sin(ang), 0)) * dist
        trunk = trail(start, tgt, 0.25, 1.0)
        trunk.append((Vector((tgt.x, tgt.y - side * 0.003, 0.010 + spring(u))), 0.7))      # climbs onto the sole
        splines.append(trunk)
        for b in range(rg.randint(1, 3)):                                                     # branches feeding into the trunk
            j = rg.randint(len(trunk) // 4, max(len(trunk) // 4 + 1, len(trunk) - 4)); jp = trunk[j][0]
            a2 = ang + rg.choice((-1, 1)) * rg.uniform(0.5, 1.3); bs = Vector((jp.x, jp.y, 0)) + Vector((math.cos(a2), math.sin(a2), 0)) * rg.uniform(0.04, 0.14)
            splines.append(trail(bs, Vector((jp.x, jp.y, 0)), 0.15, trunk[j][1] * 0.6, 0.8))
    return splines

def warp_like(o, nm):
    md = warp(o, SEEDS[nm], XF[nm][2])
    keys(o, f'modifiers["Warp"]["{IDS["Amp"]}"]', AMPS[nm]); keys(o, f'modifiers["Warp"]["{IDS["Sag"]}"]', SAG)
    keys(o, f'modifiers["Warp"]["{IDS["Wave"]}"]', WAVEA); keys(o, f'modifiers["Warp"]["{IDS["Field"]}"]', FIELD)

VEINS = {"upper": (78, 30, 0.0042, 0.22), "midsole": (40, 24, 0.0040, 0.12), "outsole": (22, 18, 0.0040, 0.1),
         "heel": (18, 18, 0.0035, 0.3), "tongue": (16, 18, 0.0035, 0.5)}
for gi_, (nm, (cnt, stp, sz_, clb)) in enumerate(VEINS.items()):
    spl = surface_veins(parts[nm], cnt, stp, sz_, clb, 100 + gi_)
    for h in range(2):
        o = vein_curve(f"veins_{nm}{h}", spl[h::2], VEIN_R, parts[nm]); warp_like(o, nm)
        g0 = 10 + 8 * h + 3 * gi_
        keys(o.data, "bevel_factor_end", [ease_out(win(f, g0, g0 + 30)) * (1 - ease_in(win(f, SW0 - 4 + 3 * h, SW0 + 16 + 3 * h))) for f in F])
        keys(o.data, "bevel_depth", [VEIN_R * (1 + 0.14 * math.sin(f * 0.33 + gi_ + h * 1.7) * (f < SET)) for f in F])   # alive: veins pulse
fl = floor_veins(110, 7)
for h in range(3):
    o = vein_curve(f"veins_floor{h}", fl[h::3], VEIN_R * 1.4)
    md = warp(o, 40.0 + h, (0, 0, 0)); md[IDS["Freq"]] = 22.0; md[IDS["Amp"]] = 0.0010     # slow writhing
    g0 = 1 + 4 * h
    keys(o.data, "bevel_factor_end", [ease_out(win(f, g0, g0 + 24)) * (1 - ease_io(win(f, SW0 + 2 + 2 * h, SW1 + 4))) for f in F])

# ---------------- set: dark charcoal cyclorama, glossy floor, haze, hidden lights ----------------
bm = bmesh.new(); prof = [(-4.0, 0.0), (1.0, 0.0)] + [(1.0 + 1.2 * math.sin(a), 1.2 - 1.2 * math.cos(a)) for a in [math.pi / 2 * k / 10 for k in range(1, 11)]] + [(2.2, 3.0)]
rowA = [bm.verts.new((-4.0, y, z)) for y, z in prof]; rowB = [bm.verts.new((4.0, y, z)) for y, z in prof]
for i in range(len(prof) - 1): bm.faces.new((rowA[i], rowA[i + 1], rowB[i + 1], rowB[i]))
cm, T = new_mat("cyc")
co = T.n("ShaderNodeTexCoord").outputs["Object"]; cx, cy, cz = T.sep(co)
isfloor = T.m("SUBTRACT", 1.0, T.m("DIVIDE", cz, 0.45), clamp=True)
nzf = T.n("ShaderNodeTexNoise"); T.link(co, nzf.inputs["Vector"]); nzf.inputs["Scale"].default_value = 14
rough = T.m("ADD", 0.17, T.m("MULTIPLY", nzf.outputs["Fac"], 0.12))
far = T.m("DIVIDE", T.m("SUBTRACT", T.v("LENGTH", T.v("SUBTRACT", T.combine(cx, cy, 0.0), (0.15, 0.0, 0.0))), 0.20), 0.25, clamp=True)
rough = T.m("ADD", rough, T.m("MULTIPLY", far, 0.35))   # glossy right under the shoe, softer further out   # semi-polished: a soft reflection under the shoe, no hard softbox blotches
mott = T.n("ShaderNodeTexNoise"); T.link(co, mott.inputs["Vector"]); mott.inputs["Scale"].default_value = 3.0; mott.inputs["Detail"].default_value = 8
fine = T.n("ShaderNodeTexNoise"); T.link(co, fine.inputs["Vector"]); fine.inputs["Scale"].default_value = 160; fine.inputs["Detail"].default_value = 6
fcol = T.mixc(T.m("MULTIPLY", mott.outputs["Fac"], 1.0), (0.004, 0.004, 0.005, 1), (0.016, 0.016, 0.018, 1))
floor = bsdf(T, fcol, rough, Specular_IOR_Level=0.6, Normal=bump(T, fine.outputs["Fac"], 0.08, 0.002))
wcol = T.mixc(mott.outputs["Fac"], (0.016, 0.016, 0.018, 1), (0.034, 0.034, 0.038, 1))
wall = bsdf(T, wcol, 0.85, Normal=bump(T, fine.outputs["Fac"], 0.2, 0.004))
out(T, T.mixs(isfloor, wall, floor))
cyc = obj_from_bm("cyclorama", bm, cm, centre=False)
for p in cyc.data.polygons: p.use_smooth = True
add_mods(cyc, 0.0, 2)

vm, T = new_mat("haze")
co = T.n("ShaderNodeTexCoord").outputs["Object"]
nzv = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); T.link(T.v("SCALE", co, scale=2.2), nzv.inputs["Vector"])
T.link(T.keyed("haze_t", [t * 0.08 for t in TIME]), nzv.inputs["W"]); nzv.inputs["Detail"].default_value = 3
dens = T.m("ADD", 0.006, T.m("MULTIPLY", T.m("POWER", nzv.outputs["Fac"], 4.0), 0.5))
vol = T.n("ShaderNodeVolumePrincipled"); T.link(dens, vol.inputs["Density"]); vol.inputs["Color"].default_value = (0.8, 0.8, 0.82, 1)
out(T, None, vol.outputs[0])
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
hz = obj_from_bm("haze", bm, vm, smooth_shade=False, centre=False); hz.scale = (3.0, 3.4, 1.4); hz.location = (0.15, 0.4, 0.6)
# ground mist: drifting smoke hugging the floor around the shoe, thinning with height
gm, T = new_mat("mist")
co = T.n("ShaderNodeTexCoord").outputs["Object"]; mx_, my_, mz_ = T.sep(co)
wn = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); T.link(T.v("SCALE", co, scale=3.0), wn.inputs["Vector"])
T.link(T.keyed("mist_t", [0.3 + t * 0.05 for t in TIME]), wn.inputs["W"]); wn.inputs["Detail"].default_value = 2
nzm = T.n("ShaderNodeTexNoise", noise_dimensions="4D")
T.link(T.v("ADD", T.v("MULTIPLY", T.v("ADD", co, T.combine(T.keyed("mist_dx", [t * 0.035 for t in TIME]), 0.0, 0.0)), (5.0, 7.0, 3.0)),
           T.v("SCALE", wn.outputs["Color"], scale=1.6)), nzm.inputs["Vector"])
T.link(T.keyed("mist_w", [t * 0.06 for t in TIME]), nzm.inputs["W"]); nzm.inputs["Detail"].default_value = 4
fall = T.m("POWER", T.m("SUBTRACT", 0.5, mz_, clamp=True), 2.0)
mdens = T.m("MULTIPLY", T.m("MULTIPLY", T.m("POWER", T.m("SUBTRACT", nzm.outputs["Fac"], 0.47, clamp=True), 1.8), 8.0), fall)
mvol = T.n("ShaderNodeVolumePrincipled"); T.link(mdens, mvol.inputs["Density"]); mvol.inputs["Color"].default_value = (0.85, 0.85, 0.87, 1)
out(T, None, mvol.outputs[0])
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
mist = obj_from_bm("mist", bm, gm, smooth_shade=False, centre=False); mist.scale = (1.6, 1.2, 0.10); mist.location = (0.15, 0.25, 0.05)
# dust: tiny specks drifting slowly through the light
dm, T = new_mat("dust"); out(T, bsdf(T, (0.8, 0.8, 0.8, 1), 0.5, Emission_Color=(0.75, 0.88, 1.0, 1), Emission_Strength=0.6))
me = bpy.data.meshes.new("dust_pts"); rd = random.Random(4)
me.from_pydata([(rd.uniform(-0.25, 0.55), rd.uniform(-0.40, 0.55), rd.uniform(0.005, 0.32)) for _ in range(500)], [], [])
dust = link_obj("dust", me)
dg = bpy.data.node_groups.new("Dust", "GeometryNodeTree")
dg.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"); dg.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
D = NT(dg); di = D.n("NodeGroupInput"); do = D.n("NodeGroupOutput")
dpos = D.n("GeometryNodeInputPosition").outputs[0]; dsec = D.n("GeometryNodeInputSceneTime").outputs["Seconds"]
dn = D.n("ShaderNodeTexNoise", noise_dimensions="4D"); D.link(D.v("SCALE", dpos, scale=6.0), dn.inputs["Vector"]); D.link(D.m("MULTIPLY", dsec, 0.05), dn.inputs["W"])
doff = D.v("ADD", D.v("SCALE", D.v("SUBTRACT", dn.outputs["Color"], (0.5, 0.5, 0.5)), scale=0.05), D.combine(0.0, 0.0, D.m("MULTIPLY", dsec, 0.004)))
dsp = D.n("GeometryNodeSetPosition"); D.link(di.outputs[0], dsp.inputs["Geometry"]); D.link(doff, dsp.inputs["Offset"])
ico = D.n("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 0.00035; ico.inputs["Subdivisions"].default_value = 1
iop = D.n("GeometryNodeInstanceOnPoints"); D.link(dsp.outputs[0], iop.inputs["Points"]); D.link(ico.outputs[0], iop.inputs["Instance"])
rv = D.n("FunctionNodeRandomValue"); rv.inputs[2].default_value = 0.4; rv.inputs[3].default_value = 1.6; D.link(rv.outputs[1], iop.inputs["Scale"])
sm = D.n("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = dm; D.link(iop.outputs[0], sm.inputs["Geometry"]); D.link(sm.outputs[0], do.inputs[0])
dust.modifiers.new("Dust", "NODES").node_group = dg

def area(name, loc, target, size, power, colour=(1, 1, 1), shape="RECTANGLE", size_y=None, glossy=True):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = shape; ld.size = size; ld.size_y = size_y or size; ld.energy = power; ld.color = colour
    lo = link_obj(name, ld); lo.location = loc
    lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    lo.visible_camera = False   # never show the lights themselves
    if not glossy: lo.visible_glossy = False
    return lo
CEN = (0.15, 0.0, 0.06); rim = C["rim"][:3]
# lighting (user reference): ONE colour-gradient softbox right above the shoe (magenta -> orange -> yellow -> cyan),
# casting a coloured pool and the shoe's shadow on the floor and rainbow reflections in the slime, plus ONE very dim omni
sbm, T = new_mat("softbox")
g = T.n("ShaderNodeTexCoord").outputs["Generated"]; gx, gy, gz = T.sep(g)
grad = T.m("ADD", T.m("MULTIPLY", gx, 0.85), T.m("MULTIPLY", gy, 0.15))
r = T.n("ShaderNodeValToRGB"); els = r.color_ramp.elements
els[0].position, els[0].color = 0.0, (0.010, 0.030, 0.38, 1); els[1].position, els[1].color = 1.0, (0.62, 0.88, 1.0, 1)   # dark blue -> light blue
for pos_, col_ in [(0.35, (0.03, 0.14, 0.85, 1)), (0.68, (0.20, 0.55, 1.0, 1))]:
    e = els.new(pos_); e.color = col_
T.link(grad, r.inputs["Fac"])
em = T.n("ShaderNodeEmission"); T.link(r.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = CFG.get("softbox_strength", 16.0)
out(T, em.outputs[0])
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
for v in bm.verts: v.co.x *= 0.50; v.co.y *= 0.36
bmesh.ops.reverse_faces(bm, faces=bm.faces[:])          # emit downwards
sbox = obj_from_bm("softbox", bm, sbm, smooth_shade=False, centre=False); sbox.location = (0.15, -0.03, 0.26)
sbox.visible_camera = False; sbox.visible_shadow = False
od = bpy.data.lights.new("omni", "POINT"); od.energy = 0.22; od.shadow_soft_size = 0.008; od.color = (0.75, 0.88, 1.0)
oo = link_obj("omni", od); oo.location = (0.25, -0.13, 0.12); oo.visible_camera = False
keys(od, "energy", [0.22 + 0.25 * smooth(win(f, SW1 - 6, SW1 + 10)) for f in F])                      # cleaner, brighter white at the end
_ec = lambda f: smooth(win(f, SW1 - 6, SW1 + 10))
keys(od, "color", [(lerp(0.75, 0.95, _ec(f)), lerp(0.88, 0.97, _ec(f)), 1.0) for f in F], 3)
# a faint cool rim from behind so the black slime and the finished silhouette separate from the dark set
rl = area("rim", (0.10, 0.50, 0.22), (0.15, 0.0, 0.05), 0.35, CFG.get("rim_power", 3.0), (0.45, 0.75, 1.0), size_y=0.12)
# product-shoot strip: a long thin highlight running along the side (reflection only, adds no light to the set)
st = area("strip", (0.15, -0.42, 0.16), (0.15, 0.0, 0.05), 0.70, 7.0, (0.85, 0.93, 1.0), size_y=0.025)
st.visible_diffuse = False; st.visible_volume_scatter = False
# a warm glow pooled on the backdrop far behind the shoe (like the orange reference), never on the shoe
bg = area("wall_glow", (0.15, 0.75, 0.02), (0.15, 1.6, 0.55), 0.6, 12.0, (0.04, 0.16, 1.0), size_y=0.3)
bg.visible_glossy = False; bg.visible_volume_scatter = False
# light linking: the strip only lights the shoe and its slime (no floor blotches); the glow only lights the wall
def recv(name, objs):
    col = bpy.data.collections.new(name)
    for o_ in objs: col.objects.link(o_)
    return col
SET_OBJS = {"cyclorama", "haze", "mist", "dust", "softbox"}
shoe_objs = [o_ for o_ in sc.objects if o_.type in ("MESH", "CURVE") and o_.name not in SET_OBJS]
st.light_linking.receiver_collection = recv("strip_receivers", shoe_objs)
bg.light_linking.receiver_collection = recv("glow_receivers", [cyc])
GL0, GL1 = 332, 352     # the glint: a light-blue bar of light sweeps toe -> heel across the finished shoe as the logo lands
gli = area("glint", (0.5, -0.30, 0.13), (0.15, 0.0, 0.05), 0.030, 0.0, (0.55, 0.82, 1.0), size_y=0.40)
gli.visible_volume_scatter = False
gli.light_linking.receiver_collection = recv("glint_receivers", [parts[n_] for n_ in parts])
keys(gli, "location", [(lerp(0.55, -0.25, ease_io(win(f, GL0, GL1))), -0.30, 0.13) for f in F], 3)
keys(gli.data, "energy", [3.5 * math.sin(math.pi * win(f, GL0, GL1)) ** 0.6 for f in F])
ht = area("heat", (0.15, 0.10, 0.07), (0.15, 0.32, 0.0), 0.34, 2.6, (0.35, 0.70, 1.0), size_y=0.12); ht.visible_glossy = False
ht.light_linking.receiver_collection = bg.light_linking.receiver_collection
# veins stay inky: the big softbox doesn't light or reflect in them (only rim/strip/omni give thin highlights)
sbox.light_linking.receiver_collection = recv("softbox_receivers", [o_ for o_ in sc.objects if o_.type in ("MESH", "CURVE") and not o_.name.startswith("veins_") and o_.name != "softbox"])
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
    rack = (lambda f: 1.0) if name == "wide" else (lambda f: 0.70 + 0.30 * smooth(win(f, f0 + 4, f0 + 20)))   # rack focus: threads -> part
    keys(co.data, "dof.focus_distance", [(Vector(p) - Vector(l)).length * rack(f) - 0.035 for f, p, l in zip(F, P, Lk)])

co, tg = make_cam("hero", 45, 6.3)
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
if MODE == "preview":    # lean settings for local previews only (the farm file keeps full quality)
    cy.max_bounces = 6; cy.glossy_bounces = 4; cy.diffuse_bounces = 2; cy.transmission_bounces = 2; cy.volume_bounces = 0
    for o in bpy.data.objects:
        for md in o.modifiers:
            if md.type == "SUBSURF": md.render_levels = min(md.render_levels, 1)
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.volume_step_rate = 8.0 if MODE == "preview" else 1.0
cy.use_light_tree = True; cy.use_animated_seed = True; cy.sample_clamp_indirect = 8.0
sc.use_nodes = True; cnt = sc.node_tree; cnt.nodes.clear()
rl_ = cnt.nodes.new("CompositorNodeRLayers"); gl = cnt.nodes.new("CompositorNodeGlare"); cmp_ = cnt.nodes.new("CompositorNodeComposite")
gl.glare_type = "FOG_GLOW"; gl.quality = "MEDIUM"; gl.threshold = 1.2; gl.size = 7; gl.mix = -0.75
cnt.links.new(rl_.outputs["Image"], gl.inputs["Image"]); cnt.links.new(gl.outputs["Image"], cmp_.inputs["Image"])
sc.render.use_compositing = True
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except TypeError: pass
farm_prep.prepare(sc, OUT, samples=128 if MODE == "farm" else 48, frames=(1, N), name="shoe_slime", fps=FPS, motion_blur=(MODE == "farm"))
