# IONADE pour sting (9:16, 1080x1920, 30 fps, 200 frames) built procedurally in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/ionade_pour.py -- <out.blend> [preview|farm]
# Story: ice drops into a fluted glass -> an IONADE can pours orange soda -> foam, bubbles, the ice floats ->
# an orange slice lands on the rim. The logo swipe is added afterwards in Remotion (src/ionade/), so the logo's brand
# colours stay exact. Plan: notes/ionade/plan.md. Grammar from references/ionade/ (no reference brands).
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.join(ROOT, "renders/farm/ionade-v1/ionade.blend")
MODE = argv[1] if len(argv) > 1 else "preview"

# ---------------- config: every colour and timing ----------------
CFG = {
    "fps": 30, "frames": 200, "res": (1080, 1920),
    "logo": os.path.join(ROOT, "public/ionade/logo.png"),
    "col": {"orange": "#FA6108", "navy": "#0B2E7A", "cream": "#FBF5ED", "wall": "#F2650F", "soda": "#FF7410",
            "oak": "#5A3A1E", "oak2": "#2E1C0E", "marble": "#EDEBE7", "vein": "#9A9A9C",
            "tred": "#8E1A1F", "tnavy": "#1B2A55", "tgreen": "#1E4733", "tline": "#D9B44A", "peel": "#F26A0A", "flesh": "#FF7A0E"},
    "ice_drop": [2, 11, 20, 29],              # frame each cube is released (slow-motion fall, ~10-12 frames)
    "can": (30, 44, 104, 118),                # can enters, pour starts, pour ends, can gone
    "fill": (46, 104, 0.0125, 0.128),         # level rises from frame a to b, z from-to (metres)
    "slice": (116, 126),                      # orange slice released, lands
    # camera spline (cylindrical around the glass): (frame, angle deg, radius m, height m, look-at height m)
    # starts close above the rim looking down at the ice, spirals down and around the glass (from the left, clear of
    # the can), stays low and close through the pour, then pulls out to the front end shot with headroom for the logo
    "cam_path": [(1, -170, 0.150, 0.200, 0.150), (34, -150, 0.155, 0.140, 0.090), (70, -128, 0.160, 0.100, 0.080),
                 (104, -110, 0.200, 0.075, 0.095), (146, -90, 0.500, 0.195, 0.128), (200, -90, 0.488, 0.193, 0.128)],
}
FPS, N = CFG["fps"], CFG["frames"]
rnd = random.Random(5)
hexc = lambda h, a=1.0: tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (1, 3, 5)) + (a,)
C = {k: hexc(v) for k, v in CFG["col"].items()}

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS

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
    def keyed(self, name, series, interp="LINEAR"):
        node = self.n("ShaderNodeValue"); node.name = name; node.outputs[0].default_value = series[0]
        keys(self.nt, f'nodes["{name}"].outputs[0].default_value', series, 1, interp); return node.outputs[0]
    def ramp(self, fac, stops):
        r = self.n("ShaderNodeValToRGB"); els = r.color_ramp.elements
        while len(els) < len(stops): els.new(0.5)
        for e, (p, c) in zip(els, stops): e.position = p; e.color = c
        self._in(r, 0, fac); return r.outputs["Color"]
    def mixc(self, fac, a, b):
        node = self.n("ShaderNodeMix", data_type="RGBA"); self._in(node, 0, fac); self._in(node, 6, a); self._in(node, 7, b)
        return node.outputs[2]
    def coord(self, kind="Object"): return self.n("ShaderNodeTexCoord").outputs[kind]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NT(m.node_tree)

def bsdf(T, base, rough, **kw):
    b = T.n("ShaderNodeBsdfPrincipled"); T._in(b, 0, base)
    T._in(b, b.inputs.find("Roughness"), rough)
    for k, v in kw.items(): T._in(b, b.inputs.find(k.replace("_", " ")), v)
    return b

def out(T, surface, volume=None, disp=None):
    o = T.n("ShaderNodeOutputMaterial"); T.link(surface, o.inputs["Surface"])
    if volume is not None: T.link(volume, o.inputs["Volume"])
    return o

def bump(T, height, strength, dist):
    b = T.n("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    T.link(height, b.inputs["Height"]); return b.outputs[0]

def shadow_pass(T, shader, colour=(1, 1, 1, 1)):
    """light passes straight through clear things for shadow rays (lights the ice, foam and slice behind glass, no caustics)"""
    lp = T.n("ShaderNodeLightPath"); tr = T.n("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = colour
    mx = T.n("ShaderNodeMixShader"); T.link(lp.outputs["Is Shadow Ray"], mx.inputs[0]); T.link(shader, mx.inputs[1]); T.link(tr.outputs[0], mx.inputs[2])
    return mx.outputs[0]

def obj_from_bm(name, bm, mat=None, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
        me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(50)
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc
    if mat: me.materials.append(mat)
    return o

def revolve(name, profile, seg, mat=None, rfun=None, uv=False):
    """profile: [(z, r, kind)] bottom->top; kind 'r' = ribbed ring. Caps where r == 0."""
    bm = bmesh.new(); rings = []
    for z, r, kind in profile:
        if r == 0: rings.append([bm.verts.new((0, 0, z))]); continue
        ring = []
        for i in range(seg):
            th = 2 * math.pi * i / seg; rr = rfun(r, th) if (kind == "r" and rfun) else r
            ring.append(bm.verts.new((rr * math.cos(th), rr * math.sin(th), z)))
        rings.append(ring)
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    zs = [p[0] for p in profile]; z0, z1 = min(zs), max(zs)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 or len(b) == 1:
            c, ring = (a[0], b) if len(a) == 1 else (b[0], a)
            for i in range(seg):
                f = bm.faces.new((c, ring[i], ring[(i + 1) % seg]) if len(a) == 1 else (ring[(i + 1) % seg], ring[i], c))
            continue
        for i in range(seg):
            j = (i + 1) % seg; f = bm.faces.new((a[i], a[j], b[j], b[i]))
            if uvl:
                for lp, (k, v) in zip(f.loops, [(i, a[i]), (i + 1, a[j]), (i + 1, b[j]), (i, b[i])]):
                    lp[uvl].uv = (k / seg, (v.co.z - z0) / (z1 - z0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, mat)

def area(name, loc, target, size, power, colour=(1, 1, 1), camera=False, glossy=True):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = "RECTANGLE"; ld.size, ld.size_y = size; ld.energy = power; ld.color = colour[:3]
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); o.visible_camera = camera
    o.visible_glossy = glossy; return o

ease_io = lambda x: (lambda t: t * t * (3 - 2 * t))(max(0.0, min(1.0, x)))
ease_out = lambda x: 1 - (1 - max(0.0, min(1.0, x))) ** 3
ease_in = lambda x: max(0.0, min(1.0, x)) ** 2
F = range(1, N + 1)

# fill level per frame (fast at first, slowing as it tops up)
fa, fb, z_lo, z_hi = CFG["fill"]
LEVEL = [z_lo + (z_hi - z_lo) * (1 - (1 - max(0, min(1, (f - fa) / (fb - fa)))) ** 1.7) for f in F]

# ---------------- materials ----------------
def glass_mat():
    m, T = new_mat("glass"); oc = T.coord()
    lev = T.keyed("level", LEVEL)
    # condensation: a field of small beads, denser below the cold liquid line
    vor = T.n("ShaderNodeTexVoronoi", feature="SMOOTH_F1"); vor.inputs["Scale"].default_value = 260.0; vor.inputs["Randomness"].default_value = 1.0
    T.link(oc, vor.inputs["Vector"])
    bead = T.m("POWER", T.m("SUBTRACT", 1.0, T.m("MULTIPLY", vor.outputs["Distance"], 2.6), clamp=True), 0.5)
    cl = T.n("ShaderNodeTexNoise"); cl.inputs["Scale"].default_value = 60.0; T.link(oc, cl.inputs["Vector"])
    z = T.sep(oc)[2]
    below = T.m("SUBTRACT", 1.0, T.m("SMOOTH_MIN", 1.0, T.m("MULTIPLY", T.m("MAXIMUM", T.m("SUBTRACT", z, T.m("ADD", lev, 0.004)), 0.0), 90.0), 0.1), clamp=True)
    dens = T.m("ADD", 0.04, T.m("MULTIPLY", below, 0.28))  # clear while empty, beads where the cold soda is
    cover = T.m("GREATER_THAN", cl.outputs["Fac"], T.m("SUBTRACT", 1.0, dens))
    h = T.m("MULTIPLY", bead, cover)
    b = bsdf(T, (1, 1, 1, 1), 0.0, Transmission_Weight=1.0, IOR=1.5)
    T.link(bump(T, h, 0.25, 0.0008), b.inputs["Normal"])
    out(T, shadow_pass(T, b.outputs[0])); return m

def soda_mat(name, volume=True):
    m, T = new_mat(name)
    b = bsdf(T, hexc("#FFA834"), 0.0, Transmission_Weight=1.0, IOR=1.34)
    vol = None
    if volume:
        a = T.n("ShaderNodeVolumeAbsorption"); a.inputs["Color"].default_value = hexc("#FFC24A"); a.inputs["Density"].default_value = 10.0
        vol = a.outputs[0]
    out(T, shadow_pass(T, b.outputs[0], hexc("#FFC060")), vol); return m

def stream_mat():
    m, T = new_mat("stream"); oc = T.coord(); z = T.sep(T.coord("Object"))[2]
    head = T.keyed("head", HEAD); tail = T.keyed("tail", TAIL); lev = T.keyed("lev", [l - 0.003 for l in LV])
    vis = T.m("MULTIPLY", T.m("LESS_THAN", z, tail), T.m("GREATER_THAN", z, T.m("MAXIMUM", head, lev)))
    # ropy surface: noise sliding down the stream
    tv = T.n("ShaderNodeValue"); d = tv.outputs[0].driver_add("default_value").driver; d.type = "SCRIPTED"; d.expression = f"frame / {FPS}"
    pos = T.combine(T.m("MULTIPLY", T.sep(oc)[0], 1.0), T.sep(oc)[1], T.m("ADD", z, T.m("MULTIPLY", tv.outputs[0], 1.2)))
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140.0; nz.inputs["Detail"].default_value = 3.0; T.link(pos, nz.inputs["Vector"])
    b = bsdf(T, C["soda"], 0.0, Transmission_Weight=1.0, IOR=1.34)
    T.link(bump(T, nz.outputs["Fac"], 0.5, 0.0008), b.inputs["Normal"])
    tr = T.n("ShaderNodeBsdfTransparent")
    mx = T.n("ShaderNodeMixShader"); T.link(vis, mx.inputs[0]); T.link(tr.outputs[0], mx.inputs[1]); T.link(b.outputs[0], mx.inputs[2])
    out(T, mx.outputs[0]); return m

def ice_mat():
    m, T = new_mat("ice"); oc = T.coord()
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90.0; nz.inputs["Detail"].default_value = 6.0; T.link(oc, nz.inputs["Vector"])
    # clear ice with a frosted skin and a milky core so it reads against the bright orange
    b = bsdf(T, (1, 1, 1, 1), 0.10, Transmission_Weight=1.0, Coat_Weight=0.5, Coat_Roughness=0.02)
    # ice bends light like ice in air, much less once the soda surrounds it (Cycles can't nest IORs)
    T.link(T.keyed("ice_ior", [1.31 - 0.12 * max(0.0, min(1.0, (f - fa) / 14)) for f in F]), b.inputs["IOR"])
    T.link(bump(T, nz.outputs["Fac"], 0.5, 0.0008), b.inputs["Normal"])
    frost = bsdf(T, (0.92, 0.95, 1.0, 1), 0.5, Subsurface_Weight=1.0, Subsurface_Radius=(0.004, 0.004, 0.005))
    edge = T.n("ShaderNodeLayerWeight"); edge.inputs["Blend"].default_value = 0.25
    mx = T.n("ShaderNodeMixShader"); T.link(T.m("MULTIPLY", edge.outputs["Facing"], 0.9), mx.inputs[0]); T.link(b.outputs[0], mx.inputs[1]); T.link(frost.outputs[0], mx.inputs[2])
    out(T, shadow_pass(T, mx.outputs[0], (0.9, 0.9, 0.9, 1))); return m

def bubble_mat():
    m, T = new_mat("bubble"); b = bsdf(T, (1, 1, 1, 1), 0.0, Transmission_Weight=1.0, IOR=0.75); out(T, shadow_pass(T, b.outputs[0])); return m

def foam_mat():
    m, T = new_mat("foam"); oc = T.coord()
    amt = T.keyed("foam", FOAM)
    vor = T.n("ShaderNodeTexVoronoi", feature="SMOOTH_F1"); vor.inputs["Scale"].default_value = 700.0; T.link(oc, vor.inputs["Vector"])
    b = bsdf(T, hexc("#FFE6C8"), 0.45)
    T.link(bump(T, vor.outputs["Distance"], 0.8, 0.0006), b.inputs["Normal"])
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 150.0; T.link(oc, nz.inputs["Vector"])
    a = T.m("GREATER_THAN", T.m("ADD", nz.outputs["Fac"], T.m("MULTIPLY", amt, 0.9)), 0.95)
    a = T.m("MULTIPLY", a, T.m("GREATER_THAN", amt, 0.02))
    tr = T.n("ShaderNodeBsdfTransparent")
    mx = T.n("ShaderNodeMixShader"); T.link(a, mx.inputs[0]); T.link(tr.outputs[0], mx.inputs[1]); T.link(b.outputs[0], mx.inputs[2])
    out(T, mx.outputs[0]); return m

def marble_mat():
    m, T = new_mat("marble"); oc = T.coord()
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 8.0; T.link(oc, nz.inputs["Vector"])
    wv = T.n("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 4.0; wv.inputs["Distortion"].default_value = 14.0; wv.inputs["Detail"].default_value = 6.0
    T.link(oc, wv.inputs["Vector"])
    vein = T.m("POWER", T.m("SUBTRACT", 1.0, wv.outputs["Fac"]), 7.0)
    col = T.mixc(T.m("MULTIPLY", vein, 0.85), C["marble"], C["vein"])
    b = bsdf(T, col, 0.16, Coat_Weight=0.4, Coat_Roughness=0.08)
    out(T, b.outputs[0]); return m

def oak_mat():
    m, T = new_mat("oak"); oc = T.coord()
    wv = T.n("ShaderNodeTexWave", wave_type="RINGS"); wv.inputs["Scale"].default_value = 18.0; wv.inputs["Distortion"].default_value = 6.0; wv.inputs["Detail"].default_value = 4.0
    mp = T.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 6.0, 1.0); T.link(oc, mp.inputs["Vector"]); T.link(mp.outputs[0], wv.inputs["Vector"])
    col = T.mixc(wv.outputs["Fac"], C["oak2"], C["oak"])
    b = bsdf(T, col, 0.45, Coat_Weight=0.3, Coat_Roughness=0.2)
    T.link(bump(T, wv.outputs["Fac"], 0.15, 0.0005), b.inputs["Normal"])
    out(T, b.outputs[0]); return m

def wall_mat():
    m, T = new_mat("wall"); b = bsdf(T, C["wall"], 0.85); out(T, b.outputs[0]); return m

def tartan_mat():
    m, T = new_mat("tartan"); uv = T.coord("UV"); u, v, _ = T.sep(uv)
    def bands(x):
        f = T.m("FRACT", T.m("MULTIPLY", x, 9.0))
        c = T.ramp(f, [(0.0, C["tnavy"]), (0.22, C["tgreen"]), (0.44, C["tred"]), (0.86, C["tline"]), (0.89, C["tred"])])
        T.nt.nodes[-1].color_ramp.interpolation = "CONSTANT"; return c
    twill = T.m("GREATER_THAN", T.m("SINE", T.m("MULTIPLY", T.m("ADD", u, v), 1400.0)), 0.0)
    col = T.mixc(twill, bands(u), bands(v))
    b = bsdf(T, col, 0.9, Sheen_Weight=0.5, Sheen_Roughness=0.4)
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; T.link(uv, nz.inputs["Vector"])
    T.link(bump(T, nz.outputs["Fac"], 0.4, 0.0005), b.inputs["Normal"])
    out(T, b.outputs[0]); return m

LOGO = bpy.data.images.load(CFG["logo"]); LOGO_ASPECT = LOGO.size[0] / LOGO.size[1]
def can_mat(name):
    m, T = new_mat(name); u, v, _ = T.sep(T.coord("UV"))
    label = T.m("MULTIPLY", T.m("GREATER_THAN", v, 0.09), T.m("LESS_THAN", v, 0.88))
    # logo on the front of the label (u = 0.75 faces -Y when the can stands upright)
    circ, hgt = 2 * math.pi * 0.033, 0.122; lh = 0.062; lw = lh * LOGO_ASPECT
    lu = T.m("ADD", T.m("DIVIDE", T.m("SUBTRACT", u, 0.75), lw / circ), 0.5)
    lv = T.m("ADD", T.m("DIVIDE", T.m("SUBTRACT", v, 0.5), lh / hgt), 0.5)
    tex = T.n("ShaderNodeTexImage", image=LOGO, extension="CLIP"); T.link(T.combine(lu, lv), tex.inputs[0])
    stripe = T.m("MULTIPLY", T.m("GREATER_THAN", v, 0.12), T.m("LESS_THAN", v, 0.16))
    stripe = T.m("MAXIMUM", stripe, T.m("MULTIPLY", T.m("GREATER_THAN", v, 0.81), T.m("LESS_THAN", v, 0.85)))
    lab = T.mixc(stripe, C["orange"], C["navy"])
    lab = T.mixc(tex.outputs["Alpha"], lab, tex.outputs["Color"])
    paint = bsdf(T, lab, 0.28, Coat_Weight=0.6, Coat_Roughness=0.1)
    alu = bsdf(T, hexc("#C9CCD1"), 0.22, Metallic=1.0)
    mx = T.n("ShaderNodeMixShader"); T.link(label, mx.inputs[0]); T.link(alu.outputs[0], mx.inputs[1]); T.link(paint.outputs[0], mx.inputs[2])
    out(T, mx.outputs[0]); return m

def slice_mat():
    m, T = new_mat("slice"); x, y, z = T.sep(T.coord())
    R = 0.032; r = T.m("DIVIDE", T.m("SQRT", T.m("ADD", T.m("MULTIPLY", x, x), T.m("MULTIPLY", z, z))), R)
    ang = T.m("ARCTAN2", z, x)
    seg = T.m("ABSOLUTE", T.m("SINE", T.m("MULTIPLY", ang, 5.0)))
    membrane = T.m("LESS_THAN", seg, T.m("ADD", 0.025, T.m("MULTIPLY", T.m("SUBTRACT", 1.0, r), 0.04)))
    core = T.m("LESS_THAN", r, 0.07)
    pith = T.m("MAXIMUM", T.m("MAXIMUM", T.m("MULTIPLY", T.m("GREATER_THAN", r, 0.89), T.m("LESS_THAN", r, 0.94)), membrane), core)
    peel = T.m("GREATER_THAN", r, 0.94)
    vor = T.n("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 520.0; vor.inputs["Randomness"].default_value = 1.0
    mp = T.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 2.6); T.link(T.coord(), mp.inputs["Vector"]); T.link(mp.outputs[0], vor.inputs["Vector"])
    col = T.mixc(T.m("POWER", vor.outputs["Distance"], 2.0), C["flesh"], hexc("#FFB347"))
    col = T.mixc(pith, col, hexc("#FFF0D8")); col = T.mixc(peel, col, C["peel"])
    b = bsdf(T, col, 0.12, Subsurface_Weight=0.15, Subsurface_Radius=(0.006, 0.0025, 0.0008), Coat_Weight=1.0, Coat_Roughness=0.02)
    T.link(bump(T, T.m("MULTIPLY", vor.outputs["Distance"], T.m("SUBTRACT", 1.0, pith)), 1.0, 0.0012), b.inputs["Normal"])
    out(T, b.outputs[0]); return m

# ---------------- set: marble counter, orange wall, coaster, tartan ----------------
M_MARBLE, M_WALL, M_OAK = marble_mat(), wall_mat(), oak_mat()
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); counter = obj_from_bm("counter", bm, M_MARBLE, smooth=False)
counter.scale = (2.4, 1.6, 1.0); counter.location = (0, -0.4, 0)
# a curved orange backdrop all the way round, so the orbiting camera always has orange behind the glass
wall = revolve("wall", [(-0.01, 0.62, "s"), (0.9, 0.62, "s")], 128, M_WALL)

def rounded_box(name, half, rad, res, mat, jitter=0.0, seed=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=res, use_grid_fill=True)
    rr = random.Random(seed)
    for v in bm.verts:
        p = Vector((v.co.x * half[0], v.co.y * half[1], v.co.z * half[2]))
        q = Vector([max(-h + rad, min(h - rad, c)) for c, h in zip(p, half)])
        d = p - q; v.co = q + (d.normalized() * rad if d.length > 1e-9 else d)
        if jitter: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * jitter
    return obj_from_bm(name, bm, mat)

coaster = rounded_box("coaster", (0.056, 0.056, 0.003), 0.0025, 6, M_OAK); coaster.location = (0, 0, 0.003); coaster.rotation_euler = (0, 0, math.radians(8))
COASTER_TOP = 0.006

bm = bmesh.new(); bm.loops.layers.uv.new("UVMap"); bmesh.ops.create_grid(bm, x_segments=60, y_segments=44, size=0.5, calc_uvs=True)
for v in bm.verts:
    v.co.z = 0.004 * math.sin(v.co.x * 28 + v.co.y * 9) * math.sin(v.co.y * 21) + 0.0048 + 0.006 * max(0.0, v.co.x + v.co.y) ** 2
cloth = obj_from_bm("tartan", bm, tartan_mat()); cloth.scale = (0.30, 0.22, 1.0); cloth.location = (-0.15, -0.14, 0.0); cloth.rotation_euler = (0, 0, math.radians(28))

# ---------------- the glass: fluted highball with a stepped foot ----------------
H, RO, RI, NRIB = 0.150, 0.0352, 0.0322, 36
rib = lambda r, th: r + 0.0011 * abs(math.sin(NRIB * th / 2)) ** 0.5
G = [(0.0, 0.0, "s"), (0.0, 0.0300, "s"), (0.0015, 0.0312, "s"), (0.016, 0.0318, "s"), (0.0175, 0.0336, "s"), (0.0195, 0.0341, "r"),
     (H - 0.004, 0.0341, "r"), (H - 0.0015, 0.0341, "s"), (H, 0.0335, "s"), (H - 0.0004, RI + 0.0003, "s"), (H - 0.002, RI, "s"),
     (0.0135, RI, "s"), (0.0118, RI - 0.0025, "s"), (0.0112, 0.0, "s")]
glass = revolve("glass", G, NRIB * 6, glass_mat(), rib); glass.location = (0, 0, COASTER_TOP)
BASE_IN = COASTER_TOP + 0.0118  # inner floor (world z)

# ---------------- liquid, foam, bubbles ----------------
M_SODA = soda_mat("soda")
lq = revolve("liquid", [(0.0, 0.0, "s"), (0.0, RI - 0.0028, "s"), (0.0015, RI - 0.0004, "s"), (1.0, RI - 0.0004, "s"), (1.0, 0.0, "s")], 96, M_SODA)
lq.location = (0, 0, BASE_IN - 0.0006)
LV = [l + COASTER_TOP for l in LEVEL]  # world level
keys(lq, "scale", [(1, 1, max(0.0004, lv - lq.location.z)) for lv in LV], 3)
keys(lq, "hide_render", [lv - BASE_IN < 0.0015 for lv in LV], 1, "CONSTANT")

FOAM = [0.0 if f < fa + 2 else min(1.0, (f - fa - 2) / 10) if f < CFG["can"][2] else max(0.25, 1 - (f - CFG["can"][2]) / 40) for f in F]
foam = revolve("foam", [(0.0, 0.0, "s"), (0.0, RI - 0.0005, "s"), (0.004, RI - 0.0006, "s"), (0.006, RI - 0.006, "s"), (0.0065, 0.0, "s")], 96, foam_mat())
keys(foam, "location", [(0, 0, lv - 0.0008) for lv in LV], 3)
keys(foam, "scale", [(1, 1, 0.3 + 0.7 * fo) for fo in FOAM], 3)
keys(foam, "hide_render", [fo < 0.02 for fo in FOAM], 1, "CONSTANT")

def bubbles():
    me = bpy.data.meshes.new("bubbles"); pts, z0, sp, sz, cling = [], [], [], [], []
    for i in range(500):
        c = i < 150
        r = (RI - 0.0009) if c else (RI - 0.002) * math.sqrt(rnd.random()); th = rnd.uniform(0, 2 * math.pi)
        pts.append((r * math.cos(th), r * math.sin(th), 0.0)); z0.append(rnd.random()); sp.append(rnd.uniform(0.12, 0.45))
        sz.append(rnd.uniform(0.00025, 0.0007) if c else rnd.uniform(0.0002, 0.0006)); cling.append(1.0 if c else 0.0)
    me.from_pydata(pts, [], [])
    for nm, data in (("z0", z0), ("speed", sp), ("size", sz), ("cling", cling)):
        me.attributes.new(nm, "FLOAT", "POINT").data.foreach_set("value", data)
    o = bpy.data.objects.new("bubbles", me); sc.collection.objects.link(o)
    ng = bpy.data.node_groups.new("bubbles", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    lev_s = ng.interface.new_socket("Level", in_out="INPUT", socket_type="NodeSocketFloat")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    T = NT(ng); gi = T.n("NodeGroupInput"); go = T.n("NodeGroupOutput")
    def attr(nm): a = T.n("GeometryNodeInputNamedAttribute", data_type="FLOAT"); a.inputs["Name"].default_value = nm; return a.outputs["Attribute"]
    t = T.n("GeometryNodeInputSceneTime").outputs["Seconds"]
    span = T.m("MAXIMUM", T.m("SUBTRACT", gi.outputs["Level"], BASE_IN + 0.003), 0.0)
    rise = T.m("FRACT", T.m("ADD", attr("z0"), T.m("MULTIPLY", t, attr("speed"))))
    zf = T.m("ADD", T.m("MULTIPLY", attr("cling"), attr("z0")), T.m("MULTIPLY", T.m("SUBTRACT", 1.0, attr("cling")), rise))
    zc = T.m("ADD", BASE_IN + 0.0015, T.m("MULTIPLY", zf, T.m("SUBTRACT", z_hi + COASTER_TOP - BASE_IN, 0.0)))
    # free bubbles span the current liquid; clinging ones sit at fixed heights and appear once the liquid covers them
    zfree = T.m("ADD", BASE_IN + 0.0015, T.m("MULTIPLY", rise, span))
    z = T.m("ADD", T.m("MULTIPLY", attr("cling"), zc), T.m("MULTIPLY", T.m("SUBTRACT", 1.0, attr("cling")), zfree))
    pos = T.n("GeometryNodeInputPosition").outputs[0]; px, py, _ = T.sep(pos)
    sp_ = T.n("GeometryNodeSetPosition"); T.link(gi.outputs["Geometry"], sp_.inputs["Geometry"]); T.link(T.combine(px, py, z), sp_.inputs["Position"])
    gone = T.m("MAXIMUM", T.m("GREATER_THAN", z, T.m("SUBTRACT", gi.outputs["Level"], 0.0012)), T.m("LESS_THAN", span, 0.004))
    dl = T.n("GeometryNodeDeleteGeometry", domain="POINT"); T.link(sp_.outputs[0], dl.inputs["Geometry"]); T.link(gone, dl.inputs["Selection"])
    ico = T.n("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 1.0; ico.inputs["Subdivisions"].default_value = 2
    inst = T.n("GeometryNodeInstanceOnPoints"); T.link(dl.outputs[0], inst.inputs["Points"]); T.link(ico.outputs["Mesh"], inst.inputs["Instance"])
    T.link(attr("size"), inst.inputs["Scale"])
    smat = T.n("GeometryNodeSetMaterial"); smat.inputs["Material"].default_value = bubble_mat(); T.link(inst.outputs[0], smat.inputs["Geometry"])
    T.link(smat.outputs[0], go.inputs["Geometry"])
    mod = o.modifiers.new("bubbles", "NODES"); mod.node_group = ng
    keys(o, f'modifiers["bubbles"]["{lev_s.identifier}"]', LV)
    return o
bubbles()

# ---------------- ice: four rounded cubes dropped in, then floating on the rising liquid ----------------
M_ICE = ice_mat(); ICE_LANDS = []
# two layers: the first two cubes sit low, the last two float with their tops out of the soda
REST = [((0.008, 0.009), 0.013, (0.12, -0.05, 0.4)), ((-0.010, -0.008), 0.013, (-0.08, 0.1, 1.1)),
        ((-0.009, 0.008), 0.038, (0.3, 0.2, 2.0)), ((0.010, -0.006), 0.038, (-0.25, 0.15, 0.7))]
FLOAT = [0.031, 0.031, 0.0062, 0.0068]  # how far each cube's centre floats below the surface
for k, (rel, ((x, y), zr, rot)) in enumerate(zip(CFG["ice_drop"], REST)):
    ice = rounded_box(f"ice_{k}", (0.0125, 0.0125, 0.0115), 0.0035, 8, M_ICE, jitter=0.0004, seed=k)
    z_rest = BASE_IN + zr; z0 = 0.25; g = 2.6; locs, rots = [], []  # slow motion: a quarter of real gravity
    t_fall = math.sqrt(2 * (z0 - z_rest) / g)
    for f in F:
        t = (f - rel) / FPS
        if t < 0: z = z0 + 0.2; frot = 1.0
        elif t < t_fall: z = z0 - 0.5 * g * t * t; frot = 1 - t / t_fall
        else:
            tb = t - t_fall; z = z_rest + 0.006 * abs(math.sin(tb * 22)) * math.exp(-tb * 14); frot = 0.0
        z = max(z, LV[f - 1] - FLOAT[k]) if t >= t_fall else z   # floats as the level rises
        bob = 0.0006 * math.sin(f * 0.21 + k) * (LV[f - 1] > z_rest)
        locs.append((x, y, z + bob)); rots.append((rot[0] + frot * 2.2, rot[1] - frot * 1.6, rot[2] + frot * 3.0))
    keys(ice, "location", locs, 3); keys(ice, "rotation_euler", rots, 3); ICE_LANDS.append(round(rel + t_fall * FPS))

# ---------------- the pouring can and the stream ----------------
CAN = [(0.0, 0.0, "s"), (0.0, 0.0255, "s"), (0.004, 0.0315, "s"), (0.010, 0.033, "s"), (0.108, 0.033, "s"), (0.118, 0.0285, "s"),
       (0.1215, 0.0272, "s"), (0.1222, 0.0262, "s"), (0.1195, 0.0255, "s"), (0.1195, 0.0, "s")]
def make_can(name): return revolve(name, CAN, 96, can_mat(f"{name}_mat"), uv=True)
can = make_can("can_pour")
MOUTH = Vector((0.010, -0.002, 0.236)); LIP = Vector((-0.0262, 0.0, 0.1222))
c0, c1, c2, c3 = CFG["can"]
locs, rots = [], []
for f in F:
    if f < c1: k = ease_out((f - c0) / (c1 - c0))
    elif f <= c2: k = 1.0
    else: k = 1 - ease_in((f - c2) / (c3 - c2))
    beta = math.radians(-40 + (-118 + 40) * k - 6 * math.sin(max(0, min(1, (f - c1) / (c2 - c1))) * math.pi) * (c1 <= f <= c2))
    R = Matrix.Rotation(beta, 4, "Y")  # tilting about Y keeps the logo side (u = 0.75, -Y) facing the camera
    off = Vector((0.12, 0.02, 0.16)) * (1 - k)
    loc = MOUTH + off - (R.to_3x3() @ LIP)  # the lowest point of the lip sits on the stream
    locs.append(tuple(loc)); rots.append(tuple(R.to_euler()))
keys(can, "location", locs, 3); keys(can, "rotation_euler", rots, 3)

HEAD = [MOUTH.z + 0.01 - ease_in((f - c1) / 4) * (MOUTH.z - BASE_IN + 0.02) for f in F]
TAIL = [MOUTH.z + 0.02 - ease_in((f - c2) / 5) * (MOUTH.z - BASE_IN + 0.03) if f > c2 else MOUTH.z + 0.05 for f in F]
bm = bmesh.new(); RINGS, SEG = 70, 14; zt, zb = MOUTH.z, BASE_IN - 0.002; prev = None; rings = []
for i in range(RINGS):
    s = i / (RINGS - 1); z = zt - (zt - zb) * s
    cx = MOUTH.x - 0.006 * math.sqrt(s); cy = MOUTH.y + 0.002 * s
    r = 0.0043 - 0.0013 * math.sqrt(s)
    rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * j / SEG) * (1 + 0.08 * math.sin(s * 40 + j)), cy + r * math.sin(2 * math.pi * j / SEG), z)) for j in range(SEG)])
for a, b in zip(rings, rings[1:]):
    for j in range(SEG): bm.faces.new((a[j], a[(j + 1) % SEG], b[(j + 1) % SEG], b[j]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
stream = obj_from_bm("stream", bm, stream_mat())

# splash droplets at the impact point while pouring
M_DROP = soda_mat("drop", volume=False)
for k in range(26):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0); d = obj_from_bm(f"drop_{k}", bm, M_DROP)
    birth = rnd.randint(c1 + 2, c2 - 6); life = rnd.randint(5, 9); vx, vy, vz = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(0.25, 0.55)
    sz = rnd.uniform(0.0006, 0.0016); locs, scl = [], []
    for f in F:
        t = (f - birth) / FPS; lv = LV[min(N - 1, max(0, birth - 1))]
        alive = 0 <= f - birth <= life
        locs.append((MOUTH.x - 0.005 + vx * t, MOUTH.y + vy * t, lv + vz * t - 4.9 * t * t)); scl.append((sz,) * 3 if alive else (0.00001,) * 3)
    keys(d, "location", locs, 3); keys(d, "scale", scl, 3, "CONSTANT")

# ---------------- the orange slice dropping onto the rim ----------------
bm = bmesh.new(); SR = 0.032; arc = [bm.verts.new((SR * math.cos(math.pi * i / 40), 0.0, SR * math.sin(math.pi * i / 40))) for i in range(41)]
face = bm.faces.new(arc); ext = bmesh.ops.extrude_face_region(bm, geom=[face])
for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co.y += 0.009
bmesh.ops.translate(bm, verts=bm.verts[:], vec=(0, -0.0045, 0)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
osl = obj_from_bm("orange_slice", bm, slice_mat(), smooth=False)
bv = osl.modifiers.new("bevel", "BEVEL"); bv.width = 0.0015; bv.segments = 3
ANG = math.radians(-58)  # where on the rim (front-right as seen by the camera)
rim = Vector((0.0338 * math.cos(ANG), 0.0338 * math.sin(ANG), COASTER_TOP + H - 0.019))
base_rot = Euler((0, 0, ANG + math.pi / 2)); s0, s1 = CFG["slice"]; locs, rots = [], []
for f in F:
    if f < s0: p = rim + Vector((0.0, 0.0, 0.25)); spin = 1.0
    elif f < s1: k = ease_in((f - s0) / (s1 - s0)); p = rim + Vector((0, 0, 0.25 * (1 - k))); spin = 1 - k
    else: tb = (f - s1) / FPS; p = rim + Vector((0, 0, 0.004 * abs(math.sin(tb * 20)) * math.exp(-tb * 12))); spin = 0.0
    locs.append(tuple(p)); rots.append((base_rot.x + spin * 0.9, base_rot.y + spin * 0.5 + math.radians(-8), base_rot.z + spin * 0.6))
keys(osl, "location", locs, 3); keys(osl, "rotation_euler", rots, 3)

# ---------------- background cans on a marble slab (soft, out of focus) ----------------
slab = rounded_box("slab", (0.11, 0.07, 0.006), 0.002, 4, M_MARBLE); slab.location = (-0.13, 0.22, 0.006)
for i, (x, y, rz) in enumerate([(-0.155, 0.235, 11), (-0.085, 0.205, 6)]):
    cb = make_can(f"can_back_{i}"); cb.location = (x, y, 0.012); cb.rotation_euler = (0, 0, math.radians(rz))

# ---------------- camera: a spline around and down the glass (Catmull-Rom through CFG["cam_path"]) ----------------
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 24.0; cam_d.lens = 45.0; cam_d.clip_start = 0.005
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 3.2; cam_d.dof.aperture_blades = 7  # close-ups need a little more depth
KP = CFG["cam_path"]
def spline(f):
    """smooth through the keys: Catmull-Rom on each channel, eased in time between keys so it glides, never stops dead mid-path"""
    f = max(KP[0][0], min(KP[-1][0], f))
    i = max(0, min(len(KP) - 2, next(k for k in range(len(KP) - 1) if KP[k + 1][0] >= f)))
    p = [KP[max(0, i - 1)], KP[i], KP[i + 1], KP[min(len(KP) - 1, i + 2)]]
    u = (f - p[1][0]) / (p[2][0] - p[1][0])
    out = []
    for c in range(1, 5):
        a, b, cc, d = (q[c] for q in p)
        m1 = (cc - a) / 2 * (p[2][0] - p[1][0]) / max(1, p[2][0] - p[0][0]) * 2
        m2 = (d - b) / 2 * (p[2][0] - p[1][0]) / max(1, p[3][0] - p[1][0]) * 2
        if i == len(KP) - 2: m2 = 0.0                 # arrive at the end shot with no velocity
        if i == 0: m1 = (cc - b) * 0.6                 # already drifting on frame 1
        h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
        out.append(h00 * b + h10 * m1 + h01 * cc + h11 * m2)
    return out
locs, rots, focus = [], [], []
lands = ICE_LANDS
for f in F:
    ang, rad, hz, lz = spline(f); a = math.radians(ang)
    p = Vector((rad * math.cos(a), rad * math.sin(a), hz)); look = Vector((0.0, 0.0, lz))
    sh = sum(0.0007 * math.exp(-(f - L) * 0.6) * math.sin((f - L) * 2.4) for L in lands if f >= L)  # a nudge on each ice landing
    p = p + Vector((0, 0, sh)); d = look - p
    locs.append(tuple(p)); rots.append(tuple(d.to_track_quat("-Z", "Y").to_euler())); focus.append(max(0.05, d.length - 0.02))
keys(cam, "location", locs, 3); keys(cam, "rotation_euler", rots, 3); keys(cam_d, "dof.focus_distance", focus)
# Euler flips would spin the camera: make the rotation curves continuous
for fc in cam.animation_data.action.fcurves:
    if fc.data_path == "rotation_euler":
        pts = fc.keyframe_points; prev = pts[0].co[1]
        for kp in pts:
            v = kp.co[1]
            while v - prev > math.pi: v -= 2 * math.pi
            while v - prev < -math.pi: v += 2 * math.pi
            kp.co[1] = v; prev = v
        fc.update()

# ---------------- light: warm key left, strips behind for glass edges, a glow behind the liquid ----------------
area("key", (-0.45, -0.35, 0.42), (0, 0, 0.08), (0.45, 0.6), 3.4, hexc("#FFF1E0"))
area("fill", (0.40, -0.38, 0.2), (0, 0, 0.08), (0.4, 0.4), 0.85, hexc("#FFE2C8"))
area("strip_l", (-0.22, 0.20, 0.10), (0, 0, 0.08), (0.03, 0.45), 1.2, (1, 1, 1))
area("strip_r", (0.22, 0.20, 0.10), (0, 0, 0.08), (0.03, 0.45), 1.2, (1, 1, 1))
area("wall_wash", (0.0, -0.1, 0.55), (0.0, 0.40, 0.25), (0.8, 0.4), 4.8, hexc("#FFE9D6"), glossy=False)
area("wall_wash_l", (0.0, 0.05, 0.55), (-0.6, -0.15, 0.2), (0.6, 0.3), 3.0, hexc("#FFE9D6"), glossy=False)
area("top", (0.0, -0.05, 0.6), (0, 0, 0.1), (0.25, 0.25), 0.7, (1, 1, 1))
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
wd.node_tree.nodes["Background"].inputs["Color"].default_value = hexc("#F4A060"); wd.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.03

# ---------------- render ----------------
sc.render.engine = "CYCLES"; cy = sc.cycles
cy.max_bounces = 24; cy.transmission_bounces = 24; cy.glossy_bounces = 8; cy.diffuse_bounces = 3; cy.transparent_max_bounces = 16
cy.volume_bounces = 1; cy.sample_clamp_indirect = 6.0; cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
sc.render.resolution_x, sc.render.resolution_y = CFG["res"]; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = 0.0
import farm_prep
print("ICE_LANDS", ICE_LANDS, flush=True)
farm_prep.prepare(sc, OUT, samples=128 if MODE == "farm" else 64, frames=(1, N), name="ionade", fps=FPS, motion_blur=(MODE == "farm"))
