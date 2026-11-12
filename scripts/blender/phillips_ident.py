# Phillips Digital ident (8 s, 1920x1080, 30 fps) built procedurally in Blender Cycles.
# Usage: blender -b --factory-startup -P scripts/blender/phillips_ident.py -- <out.blend> [preview|farm]
# Story: an old CRT TV flickers on with static -> the camera rushes in, the glass shatters -> we fly down a street
# of falling code -> glyphs swarm into PHILLIPS DIGITAL -> neon flickers on -> hard cut to black.
# Colours: phillipsdigital.net (forest-black, lime, cream). Plan: notes/philips-digital/plan.md
import bpy, bmesh, math, random, os, sys
from mathutils import Vector, Matrix, Quaternion, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = os.path.abspath(argv[0]) if argv else os.path.join(ROOT, "renders/farm/phillips-digital-v1/phillips-digital.blend")
MODE = argv[1] if len(argv) > 1 else "preview"

# ---------------- config: every word, colour and timing ----------------
CFG = {
    "fps": 30, "frames": 240, "words": ("PHILLIPS", "DIGITAL"),
    "font_text": os.path.join(ROOT, "public/fonts/LiberationMono-Bold.ttf"), "condense": 0.84,
    "atlas": os.path.join(ROOT, "public/philips/glyphs.png"),
    "col": {"black": "#050D06", "forest": "#0A1C0B", "forest2": "#10251C", "deep": "#0B241A", "lime": "#C9FA44", "lime2": "#D7FC70",
            "cream": "#F8F8F2", "sage": "#62716A", "sage2": "#C5D4C7",
            "green": "#3FAE3A", "green2": "#7FE04A"},  # in-between greens from forest to lime (code trails, circuits),
    # TV screen: (frame, power, open) keys; open = CRT vertical opening (power-on line -> full picture)
    "screen": [(1, 0, 0), (12, 1, 0.02), (14, 1, 0.25), (17, 1, 1), (30, 0, 1), (36, 1, 1), (58, 0, 1), (62, 1, 1), (96, 1, 1)],
    "code_bleed": (80, 100), "crack": (104, 108), "shatter": 108, "cut": 118,
    "swarm": (5.2, 0.45, 0.25, 0.5, 0.25),  # start s, left->right stagger s, random s, duration s, random duration s
    "neon_a": [(196, 1), (198, 0), (199, 1), (203, 0), (204, 1), (222, 0.15), (223, 1)],  # PHILLIPS
    "neon_b": [(200, 1), (201, 0), (203, 1), (206, 0), (207, 1), (224, 0.2), (225, 1)],  # DIGITAL
    "black": 232,
}
STATUE = {"model": os.path.join(ROOT, "public/models/theodoric-200k.stl"), "y": 70.0, "height": 9.0, "boot": (180, 214)}
FPS, N = CFG["fps"], CFG["frames"]
rnd = random.Random(7)
hexc = lambda h, a=1.0: tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (1, 3, 5)) + (a,)
C = {k: hexc(v) for k, v in CFG["col"].items()}
O = Vector((1000, 0, 0))  # the code world lives far from the TV room (camera clip hides each from the other)

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS

# ---------------- helpers ----------------
def keys(id_data, path, values, count=1, interp="LINEAR", frames=None):
    """values per frame (or per entry of frames); fast fcurve writing."""
    ad = id_data.animation_data or id_data.animation_data_create()
    if not ad.action: ad.action = bpy.data.actions.new(f"{id_data.name}_act")
    fr = frames or list(range(1, len(values) + 1))
    for i in range(count):
        fc = ad.action.fcurves.find(path, index=i) or ad.action.fcurves.new(path, index=i)
        fc.keyframe_points.add(len(values)); co = []
        for f, v in zip(fr, values): co += [f, float(v[i] if count > 1 else v)]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = interp
        fc.update()

def step_series(pairs, default=0.0):
    """[(frame, value), ...] held constant between keys -> one value per frame."""
    out, cur, k = [], default, 0
    for f in range(1, N + 1):
        while k < len(pairs) and pairs[k][0] <= f: cur = pairs[k][1]; k += 1
        out.append(cur)
    return out

class NT:
    """tiny node-tree builder"""
    def __init__(self, nt): self.nt = nt
    def n(self, kind, **kw):
        node = self.nt.nodes.new(kind)
        for k, v in kw.items(): setattr(node, k, v)
        return node
    def link(self, a, b): self.nt.links.new(a, b)
    def _in(self, node, i, x):
        if isinstance(x, (int, float)): node.inputs[i].default_value = x
        elif isinstance(x, tuple): node.inputs[i].default_value = x
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
        return node.outputs[0] if op not in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else node.outputs[1]
    def combine(self, x, y, z=0.0):
        node = self.n("ShaderNodeCombineXYZ")
        for i, a in enumerate([x, y, z]): self._in(node, i, a)
        return node.outputs[0]
    def sep(self, vec):
        node = self.n("ShaderNodeSeparateXYZ"); self._in(node, 0, vec); return node.outputs
    def wn(self, vec, dims="3D"):
        node = self.n("ShaderNodeTexWhiteNoise", noise_dimensions=dims); self._in(node, 0, vec); return node.outputs["Value"]
    def time(self):
        node = self.n("ShaderNodeValue"); d = node.outputs[0].driver_add("default_value").driver
        d.type = "SCRIPTED"; d.expression = f"frame / {FPS}"; return node.outputs[0]
    def keyed(self, name, series, interp="LINEAR"):
        node = self.n("ShaderNodeValue"); node.name = name; node.outputs[0].default_value = series[0]
        keys(self.nt, f'nodes["{name}"].outputs[0].default_value', series, 1, interp); return node.outputs[0]
    def ramp(self, fac, stops):
        r = self.n("ShaderNodeValToRGB"); els = r.color_ramp.elements
        while len(els) < len(stops): els.new(0.5)
        for e, (p, c) in zip(els, stops): e.position = p; e.color = c
        self._in(r, 0, fac); return r.outputs["Color"]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NT(m.node_tree)

ATLAS = bpy.data.images.load(CFG["atlas"]); ATLAS.colorspace_settings.name = "Non-Color"
def atlas_sample(T, cell_hash, local_uv):
    """glyph from the 16x16 atlas: cell from a 0..1 hash, local_uv (x, y) in 0..1"""
    gi = T.m("FLOOR", T.m("MULTIPLY", cell_hash, 255.99))
    cx = T.m("FLOORED_MODULO", gi, 16.0); cy = T.m("FLOOR", T.m("DIVIDE", gi, 16.0))
    lx, ly = local_uv
    u = T.m("DIVIDE", T.m("ADD", cx, T.m("ADD", T.m("MULTIPLY", lx, 0.86), 0.07)), 16.0)
    v = T.m("SUBTRACT", 1.0, T.m("DIVIDE", T.m("ADD", cy, T.m("SUBTRACT", 1.0, T.m("ADD", T.m("MULTIPLY", ly, 0.9), 0.05))), 16.0))
    tex = T.n("ShaderNodeTexImage", image=ATLAS, interpolation="Linear", extension="CLIP")
    T.link(T.combine(u, v), tex.inputs[0]); return tex.outputs["Color"]

def emission(T, color, strength):
    e = T.n("ShaderNodeEmission"); T._in(e, 0, color); T._in(e, 1, strength); return e.outputs[0]

def principled(T, base, rough, metal=0.0, coat=0.0, coat_rough=0.03, spec=0.5):
    b = T.n("ShaderNodeBsdfPrincipled"); T._in(b, 0, base) if not isinstance(base, tuple) else None
    if isinstance(base, tuple): b.inputs["Base Color"].default_value = base
    b.inputs["Roughness"].default_value = rough if isinstance(rough, float) else 0.3
    if not isinstance(rough, float): T.link(rough, b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = metal; b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Specular IOR Level"].default_value = spec
    return b

def out(T, shader):
    o = T.n("ShaderNodeOutputMaterial"); T.link(shader, o.inputs["Surface"])

def add_shader(T, a, b):
    s = T.n("ShaderNodeAddShader"); T.link(a, s.inputs[0]); T.link(b, s.inputs[1]); return s.outputs[0]

def mix_shader(T, fac, a, b):
    s = T.n("ShaderNodeMixShader"); T._in(s, 0, fac); T.link(a, s.inputs[1]); T.link(b, s.inputs[2]); return s.outputs[0]

def obj_from_bm(name, bm, mat=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc
    if mat: me.materials.append(mat)
    return o

def box(name, size, loc, mat=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    return obj_from_bm(name, bm, mat, loc)

def area_light(name, loc, target, size, power, colour, visible=False, reflect=True):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = "RECTANGLE"; ld.size, ld.size_y = size; ld.energy = power; ld.color = colour[:3]
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); o.visible_camera = visible
    if not reflect: o.visible_glossy = False
    return o

# ---------------- TV screen material (power-on, static, rolling bar, code bleed, cracks) ----------------
def screen_material(name, portal=False):
    m, T = new_mat(name); t = T.time()
    uv = T.n("ShaderNodeTexCoord").outputs["UV"]; ux, uy, _ = T.sep(uv)
    if portal:  # the inside of the tube: a bright wall of falling lime code
        rowc = T.m("FLOOR", T.m("ADD", T.m("MULTIPLY", uy, 24.0), T.m("MULTIPLY", t, 14.0)))
        colc = T.m("FLOOR", T.m("MULTIPLY", ux, 32.0))
        g = atlas_sample(T, T.wn(T.combine(colc, rowc, T.m("FLOOR", T.m("MULTIPLY", t, 6.0))), "3D"),
                         (T.m("FRACT", T.m("MULTIPLY", ux, 32.0)), T.m("FRACT", T.m("ADD", T.m("MULTIPLY", uy, 24.0), T.m("MULTIPLY", t, 14.0)))))
        col = T.ramp(T.m("MULTIPLY", T.sep(g)[0], 0.95), [(0.0, C["black"]), (0.4, C["green"]), (0.75, C["lime"]), (1.0, C["cream"])])
        out(T, emission(T, col, 3.2)); return m
    power = T.keyed("power", step_series([(f, p) for f, p, _ in CFG["screen"]]), "CONSTANT")
    opn = T.keyed("open", step_series([(f, o) for f, _, o in CFG["screen"]], 0.0), "LINEAR")
    code = T.keyed("code", [min(1, max(0, (f - CFG["code_bleed"][0]) / (CFG["code_bleed"][1] - CFG["code_bleed"][0]))) for f in range(1, N + 1)])
    crack = T.keyed("crack", [min(1, max(0, (f - CFG["crack"][0]) / (CFG["crack"][1] - CFG["crack"][0]))) for f in range(1, N + 1)])
    frame_i = T.m("FLOOR", T.m("MULTIPLY", t, 30.0))
    stat = T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", ux, 300.0)), T.m("FLOOR", T.m("MULTIPLY", uy, 225.0)), frame_i))
    scan = T.m("ADD", 0.72, T.m("MULTIPLY", 0.28, T.m("SINE", T.m("MULTIPLY", uy, 1413.7))))
    rb = T.m("SUBTRACT", T.m("FRACT", T.m("SUBTRACT", uy, T.m("MULTIPLY", t, 0.55))), 0.5)
    roll = T.m("ADD", 1.0, T.m("MULTIPLY", 0.9, T.m("EXPONENT", T.m("MULTIPLY", T.m("MULTIPLY", rb, rb), -90.0))))
    img = T.m("MULTIPLY", T.m("MULTIPLY", stat, scan), roll)
    # code bleeding through the static (foreshadowing the inside)
    rowc = T.m("ADD", T.m("MULTIPLY", uy, 18.0), T.m("MULTIPLY", t, 9.0))
    g = atlas_sample(T, T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", ux, 24.0)), T.m("FLOOR", rowc), T.m("FLOOR", T.m("MULTIPLY", t, 5.0))), "3D"),
                     (T.m("FRACT", T.m("MULTIPLY", ux, 24.0)), T.m("FRACT", rowc)))
    img = T.m("ADD", T.m("MULTIPLY", img, T.m("SUBTRACT", 1.0, T.m("MULTIPLY", code, 0.55))), T.m("MULTIPLY", T.sep(g)[0], T.m("MULTIPLY", code, 1.4)))
    # CRT opening: |v - 0.5| < open / 2, brighter while it is a thin line
    dv = T.m("ABSOLUTE", T.m("SUBTRACT", uy, 0.5))
    mask = T.m("SUBTRACT", 1.0, T.m("GREATER_THAN", dv, T.m("MULTIPLY", opn, 0.5)))
    boost = T.m("ADD", 1.0, T.m("MULTIPLY", 2.5, T.m("SUBTRACT", 1.0, opn)))
    # vignette of the tube face
    r = T.v("LENGTH", T.v("SUBTRACT", uv, (0.5, 0.5, 0.0)))
    vig = T.m("SUBTRACT", 1.0, T.m("MULTIPLY", 0.75, T.m("POWER", T.m("MULTIPLY", r, 1.35), 2.2), clamp=True))
    lum = T.m("MULTIPLY", T.m("MULTIPLY", img, mask), T.m("MULTIPLY", vig, boost))
    col = T.ramp(T.m("MULTIPLY", img, 0.8), [(0.0, C["forest"]), (0.45, C["deep"]), (0.75, C["lime"]), (1.0, C["cream"])])
    strength = T.m("MULTIPLY", T.m("MULTIPLY", power, lum), 3.2)
    # cracks spread from the impact point just before the glass goes
    vor = T.n("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); vor.inputs["Scale"].default_value = 7.0; T.link(uv, vor.inputs["Vector"])
    line = T.m("LESS_THAN", vor.outputs["Distance"], 0.012)
    near = T.m("LESS_THAN", T.v("LENGTH", T.v("SUBTRACT", uv, (0.53, 0.55, 0.0))), T.m("MULTIPLY", crack, 0.8))
    crk = T.m("MULTIPLY", T.m("MULTIPLY", line, near), crack)
    e1 = emission(T, col, strength); e2 = emission(T, C["cream"], T.m("MULTIPLY", crk, 12.0))
    glass = principled(T, C["black"], 0.05, coat=1.0, coat_rough=0.02, spec=0.6).outputs[0]
    out(T, add_shader(T, add_shader(T, e1, e2), glass)); return m

M_SCREEN = screen_material("ph_screen"); M_PORTAL = screen_material("ph_portal", portal=True)

def simple_mat(name, base, rough, metal=0.0, coat=0.0):
    m, T = new_mat(name); out(T, principled(T, base, rough, metal, coat).outputs[0]); return m

def body_mat():
    m, T = new_mat("ph_tvbody"); pos = T.n("ShaderNodeTexCoord").outputs["Object"]
    wear = T.n("ShaderNodeTexNoise"); wear.inputs["Scale"].default_value = 18.0; wear.inputs["Detail"].default_value = 8; T.link(pos, wear.inputs["Vector"])
    b = principled(T, hexc("#0E1712"), T.m("ADD", 0.22, T.m("MULTIPLY", wear.outputs["Fac"], 0.35)), coat=0.7, coat_rough=0.12)
    bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08; T.link(wear.outputs["Fac"], bp.inputs["Height"]); T.link(bp.outputs[0], b.inputs["Normal"])
    out(T, b.outputs[0]); return m
M_BODY = body_mat()
def walnut_mat():
    # lacquered walnut: warped growth bands, fine grain, a glossy coat
    m, T = new_mat("ph_walnut"); pos = T.n("ShaderNodeTexCoord").outputs["Object"]
    wv = T.n("ShaderNodeTexWave", wave_type="RINGS"); wv.inputs["Scale"].default_value = 6.0; wv.inputs["Distortion"].default_value = 9.0; wv.inputs["Detail"].default_value = 4
    T.link(T.v("MULTIPLY", pos, (1.0, 1.0, 0.18)), wv.inputs["Vector"])
    grain = T.n("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 260.0; T.link(T.v("MULTIPLY", pos, (1.0, 1.0, 0.05)), grain.inputs["Vector"])
    col = T.ramp(T.m("ADD", T.m("MULTIPLY", wv.outputs["Fac"], 0.7), T.m("MULTIPLY", grain.outputs["Fac"], 0.3)), [(0.0, hexc("#1A0E07")), (0.55, hexc("#3E2414")), (1.0, hexc("#5A3620"))])
    b = principled(T, C["black"], 0.42, coat=1.0, coat_rough=0.06); T.link(col, b.inputs["Base Color"])
    bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.05; T.link(grain.outputs["Fac"], bp.inputs["Height"]); T.link(bp.outputs[0], b.inputs["Normal"])
    out(T, b.outputs[0]); return m
M_WALNUT = walnut_mat()
M_CREAM = simple_mat("ph_cream", hexc("#E6DFC8"), 0.32, coat=0.4)
M_CHROME = simple_mat("ph_chrome", hexc("#D8DDD8"), 0.08, metal=1.0)
M_BRASS = simple_mat("ph_brass", hexc("#C9A15A"), 0.22, metal=1.0)
def fabric_mat():
    m, T = new_mat("ph_fabric"); pos = T.n("ShaderNodeTexCoord").outputs["Object"]; px, py, pz = T.sep(pos)
    weave = T.m("MULTIPLY", T.m("ADD", 0.5, T.m("MULTIPLY", 0.5, T.m("SINE", T.m("MULTIPLY", px, 1400.0)))), T.m("ADD", 0.5, T.m("MULTIPLY", 0.5, T.m("SINE", T.m("MULTIPLY", pz, 1400.0)))))
    b = principled(T, hexc("#2B3A2E"), 0.9); bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4; T.link(weave, bp.inputs["Height"]); T.link(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Sheen Weight"].default_value = 0.6; out(T, b.outputs[0]); return m
M_FABRIC = fabric_mat()
def shard_mat():
    # real glass: clear and refractive, carrying a fading ghost of the picture
    m, T = new_mat("ph_shard"); t = T.time(); uv = T.n("ShaderNodeTexCoord").outputs["UV"]; ux, uy, _ = T.sep(uv)
    stat = T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", ux, 300.0)), T.m("FLOOR", T.m("MULTIPLY", uy, 225.0)), T.m("FLOOR", T.m("MULTIPLY", t, 30.0))))
    fade = T.keyed("ghost", [1.0 if f <= CFG["shatter"] else max(0.0, 1 - (f - CFG["shatter"]) / 4) for f in range(1, N + 1)])
    g = principled(T, (1, 1, 1, 1), 0.02, spec=0.5); g.inputs["Transmission Weight"].default_value = 1.0; g.inputs["IOR"].default_value = 1.52
    out(T, add_shader(T, g.outputs[0], emission(T, C["green2"], T.m("MULTIPLY", T.m("MULTIPLY", stat, fade), 0.5)))); return m
M_SHARD = shard_mat()
M_METAL = simple_mat("ph_metal", hexc("#8C978F"), 0.28, metal=1.0)
M_DARK = simple_mat("ph_dark", hexc("#030604"), 0.6)
M_TABLE = simple_mat("ph_table", hexc("#140F0B"), 0.5, coat=0.4)

def floor_mat(name, circuits):
    # wet black-green floor: patchy gloss; in the code world, circuit traces + a pulsing main trace
    m, T = new_mat(name); t = T.time()
    pos = T.n("ShaderNodeNewGeometry").outputs["Position"]
    nz = T.n("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6; T.link(pos, nz.inputs["Vector"])
    pud = T.n("ShaderNodeTexNoise"); pud.inputs["Scale"].default_value = 0.45 if circuits else 1.2; pud.inputs["Detail"].default_value = 4; T.link(pos, pud.inputs["Vector"])
    wet = T.m("MULTIPLY", T.m("SUBTRACT", pud.outputs["Fac"], 0.47), 14.0, clamp=True)            # 1 = standing water
    dry = T.m("ADD", 0.18, T.m("MULTIPLY", nz.outputs["Fac"], 0.35))
    rough = T.m("ADD", T.m("MULTIPLY", dry, T.m("SUBTRACT", 1.0, wet)), T.m("MULTIPLY", wet, 0.015))
    b = principled(T, C["black"], rough, spec=0.75)
    b.inputs["Base Color"].default_value = hexc("#06100A")
    rip = T.n("ShaderNodeTexNoise", noise_dimensions="4D"); rip.inputs["Scale"].default_value = 26.0; rip.inputs["Detail"].default_value = 2
    T.link(pos, rip.inputs["Vector"]); T.link(T.m("MULTIPLY", t, 0.8), rip.inputs["W"])
    grit = T.n("ShaderNodeTexNoise"); grit.inputs["Scale"].default_value = 140.0; T.link(pos, grit.inputs["Vector"])
    hgt = T.m("ADD", T.m("MULTIPLY", rip.outputs["Fac"], T.m("MULTIPLY", wet, 0.4)), T.m("MULTIPLY", grit.outputs["Fac"], T.m("SUBTRACT", 1.0, wet)))
    bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.01
    T.link(hgt, bp.inputs["Height"]); T.link(bp.outputs[0], b.inputs["Normal"])
    if not circuits: out(T, b.outputs[0]); return m
    px, py, _ = T.sep(pos)
    lp = T.combine(T.m("SUBTRACT", px, O.x), py)
    vor = T.n("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE", voronoi_dimensions="2D")
    vor.inputs["Scale"].default_value = 0.9; T.link(lp, vor.inputs["Vector"])
    trace = T.m("MULTIPLY", T.m("LESS_THAN", vor.outputs["Distance"], 0.018), 1.0)
    # right-angle traces: a coarse grid of lanes
    lanes = T.m("MAXIMUM", T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("FRACT", T.m("MULTIPLY", T.m("SUBTRACT", px, O.x), 1.3)), 0.5)), 0.012),
                T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("FRACT", T.m("MULTIPLY", py, 0.7)), 0.5)), 0.01))
    lanes = T.m("MULTIPLY", lanes, T.m("GREATER_THAN", T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", T.m("SUBTRACT", px, O.x), 0.65)), T.m("FLOOR", T.m("MULTIPLY", py, 0.35))), "2D"), 0.55))
    wig = T.m("MULTIPLY", T.m("SINE", T.m("MULTIPLY", py, 0.9)), 0.25)
    main = T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("SUBTRACT", px, O.x), wig)), 0.035)
    pulse = T.m("ADD", 0.5, T.m("MULTIPLY", 0.5, T.m("SINE", T.m("SUBTRACT", T.m("MULTIPLY", py, 1.4), T.m("MULTIPLY", t, 9.0)))))
    glow = T.m("ADD", T.m("ADD", T.m("MULTIPLY", trace, 0.35), T.m("MULTIPLY", lanes, 1.4)), T.m("MULTIPLY", main, T.m("ADD", 2.0, T.m("MULTIPLY", pulse, 6.0))))
    out(T, add_shader(T, b.outputs[0], emission(T, C["green2"], glow))); return m

M_FLOOR_ROOM = floor_mat("ph_floor_room", False); M_FLOOR_CODE = floor_mat("ph_floor_code", True)

# ---------------- the TV room ----------------
def squircle(u, v, n=5.0):
    m = max(abs(u), abs(v))
    if m < 1e-9: return 0.0, 0.0
    ex, ey = u / m, v / m; s = (abs(ex) ** n + abs(ey) ** n) ** (1 / n)
    return ex / s * m, ey / s * m

TVZ = 0.0  # the set sits on the floor (the moody silhouette the user preferred)
SW, SH, SCX, SCZ, SY = 0.215, 0.162, -0.065, 0.25 + TVZ, -0.236  # screen half-size, centre, front plane (y)
def screen_point(u, v):
    x, z = squircle(u, v); r2 = min(1.0, max(abs(u), abs(v)) ** 2)
    return Vector((SCX + x * SW, SY - 0.022 * (1 - r2), SCZ + z * SH))

# cabinet with a recess where the tube is
cab = box("tv_cabinet", (0.64, 0.46, 0.47), (0, 0, 0.235 + TVZ), M_BODY)
bev = cab.modifiers.new("bevel", "BEVEL"); bev.width = 0.03; bev.segments = 5; bev.limit_method = "ANGLE"
bm = bmesh.new(); ring = []
for i in range(64):
    a = 2 * math.pi * i / 64; u, v = math.cos(a), math.sin(a); m_ = max(abs(u), abs(v)); u, v = u / m_ * 1.04, v / m_ * 1.04
    x, z = squircle(u, v); ring.append((SCX + x * SW, SCZ + z * SH))
f0 = [bm.verts.new((x, -0.3, z)) for x, z in ring]; f1 = [bm.verts.new((x, -0.05, z)) for x, z in ring]
bm.faces.new(f0); bm.faces.new(list(reversed(f1)))
for i in range(64): bm.faces.new([f0[i], f0[(i + 1) % 64], f1[(i + 1) % 64], f1[i]])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
cutter = obj_from_bm("tv_cutter", bm); cutter.hide_render = True; cutter.hide_viewport = True; cutter.display_type = "WIRE"
boo = cab.modifiers.new("recess", "BOOLEAN"); boo.operation = "DIFFERENCE"; boo.object = cutter; boo.solver = "EXACT"
# intact screen (curved squircle grid)
bm = bmesh.new(); G = 48; vs = {}
for j in range(G + 1):
    for i in range(G + 1):
        u, v = i / G * 2 - 1, j / G * 2 - 1; vs[i, j] = bm.verts.new(screen_point(u, v))
uvl = bm.loops.layers.uv.new("UVMap")
for j in range(G):
    for i in range(G):
        f = bm.faces.new([vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]])
        for lp, (a, b) in zip(f.loops, [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]): lp[uvl].uv = (a / G, b / G)
bmesh.ops.reverse_faces(bm, faces=bm.faces)
screen = obj_from_bm("tv_screen", bm, M_SCREEN)
for p in screen.data.polygons: p.use_smooth = True
# portal: the inside of the tube, revealed when the glass goes
bm = bmesh.new(); bm.loops.layers.uv.new("UVMap"); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0, calc_uvs=True)
for v in bm.verts: v.co = Vector((SCX + v.co.x * 0.26, -0.12, SCZ + v.co.y * 0.2))
bmesh.ops.reverse_faces(bm, faces=bm.faces)
portal = obj_from_bm("tv_portal", bm, M_PORTAL)
# knobs, grille, antenna
for k, z in enumerate((0.33, 0.25)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.03, location=(0.235, -0.235, z), rotation=(math.pi / 2, 0, 0), vertices=32)
    o = bpy.context.object; o.name = f"tv_knob{k}"; o.data.materials.append(M_METAL)
for k in range(7):
    box(f"tv_grille{k}", (0.09, 0.01, 0.006), (0.235, -0.232, 0.08 + k * 0.016), M_DARK)
for k, ang in enumerate((-0.5, 0.5)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.5, location=(0, 0.05, 0.47), vertices=12)
    o = bpy.context.object; o.name = f"tv_antenna{k}"; o.data.materials.append(M_METAL)
    o.rotation_euler = (0, ang, 0); o.location = (math.sin(ang) * 0.25, 0.05, 0.47 + math.cos(ang) * 0.25)
def cyclorama(name, mat, width=14.0, front=-8.0, back=2.2, radius=1.8, height=7.0, seg=48):
    """infinite floor: floor (z=0) from 'front' to the cove, a quarter-circle cove of 'radius', then a wall up to 'height'"""
    prof = [(front, 0.0), (back - radius, 0.0)]
    for i in range(1, seg + 1):
        a = (math.pi / 2) * i / seg; prof.append((back - radius + math.sin(a) * radius, radius - math.cos(a) * radius))
    prof.append((back, height))
    bm = bmesh.new(); xs = [-width / 2, width / 2]; rows = []
    for y, z in prof: rows.append([bm.verts.new((x, y, z)) for x in xs])
    for a, b in zip(rows, rows[1:]): bm.faces.new([a[0], a[1], b[1], b[0]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(name, bm, mat)
    for p_ in o.data.polygons: p_.use_smooth = True
    sub = o.modifiers.new("subd", "SUBSURF"); sub.levels = 1; sub.render_levels = 2; sub.subdivision_type = "SIMPLE"
    return o
cyclorama("room_cyc", M_FLOOR_ROOM)
area_light("room_rim", (-0.9, 0.9, 0.9), (0, 0, 0.3), (0.5, 0.5), 14, C["lime"])
area_light("room_fill", (0.8, -1.6, 1.8), (0, 0, 0.2), (1.5, 1.5), 6, C["sage2"])

# glass shards: a Voronoi split of the screen, each a thin slab that flies at the camera
def clip(poly, a, b):
    """keep the half-plane closer to a than to b"""
    mid = (a + b) / 2; n = b - a; res = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        dp, dq = (p - mid).dot(n), (q - mid).dot(n)
        if dp <= 0: res.append(p)
        if (dp < 0) != (dq < 0):
            t = dp / (dp - dq); res.append(p + (q - p) * t)
    return res
from mathutils import Vector as V2
seeds = [V2((rnd.uniform(-1, 1), rnd.uniform(-1, 1))) for _ in range(22)] + [V2((0.12 + rnd.gauss(0, 0.25), 0.1 + rnd.gauss(0, 0.25))) for _ in range(20)]
seeds = [V2((max(-0.99, min(0.99, s.x)), max(-0.99, min(0.99, s.y)))) for s in seeds]
impact = screen_point(0.12, 0.1)
shards = []
for si, s in enumerate(seeds):
    poly = [V2((-1, -1)), V2((1, -1)), V2((1, 1)), V2((-1, 1))]
    for t2 in seeds:
        if t2 is not s and poly: poly = clip(poly, s, t2)
    if len(poly) < 3: continue
    dense = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        for k in range(4): dense.append(p + (q - p) * (k / 4))
    pts = [screen_point(p.x, p.y) for p in dense]; cen = sum(pts, Vector()) / len(pts)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    fr = [bm.verts.new(p - cen) for p in pts]; bk = [bm.verts.new(p - cen + Vector((0, 0.005, 0))) for p in pts]
    ff = bm.faces.new(list(reversed(fr)))
    for lp in ff.loops:
        i = fr.index(lp.vert); lp[uvl].uv = ((dense[i].x + 1) / 2, (dense[i].y + 1) / 2)
    bm.faces.new(bk)
    for i in range(len(fr)): bm.faces.new([fr[i], fr[(i + 1) % len(fr)], bk[(i + 1) % len(fr)], bk[i]])
    o = obj_from_bm(f"shard_{si:02d}", bm, M_SHARD, cen); o.rotation_mode = "QUATERNION"; shards.append(o)

S0 = CFG["shatter"]
for o in shards:
    c0 = o.location.copy(); radial = (c0 - impact); radial.y = 0
    vel = radial.normalized() * rnd.uniform(0.6, 2.2) + Vector((0, -rnd.uniform(1.5, 4.0), rnd.uniform(-0.1, 0.6)))
    axis = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized(); w = rnd.uniform(4, 14)
    locs, rots = [], []
    for f in range(1, N + 1):
        tau = max(0.0, (f - S0) / FPS)
        locs.append(tuple(c0 + vel * tau + Vector((0, 0, -2.5 * tau * tau)))); rots.append(tuple(Quaternion(axis, w * tau)))
    keys(o, "location", locs, 3); keys(o, "rotation_quaternion", rots, 4)
    vis = [f >= S0 for f in range(1, N + 1)]
    keys(o, "hide_render", [not x for x in vis], 1, "CONSTANT"); keys(o, "hide_viewport", [not x for x in vis], 1, "CONSTANT")
keys(screen, "hide_render", [f >= S0 for f in range(1, N + 1)], 1, "CONSTANT")

# ---------------- the code world ----------------
def rain_material():
    m, T = new_mat("ph_rain"); t = T.time()
    uv = T.n("ShaderNodeTexCoord").outputs["UV"]; ux, uy, _ = T.sep(uv)
    info = T.n("ShaderNodeObjectInfo"); r1 = info.outputs["Random"]
    rows = T.n("ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="rows").outputs["Fac"]
    r2 = T.m("FRACT", T.m("MULTIPLY", r1, 97.31)); r3 = T.m("FRACT", T.m("MULTIPLY", r1, 13.7))
    speed = T.m("ADD", 9.0, T.m("MULTIPLY", r2, 22.0)); trail = T.m("ADD", 8.0, T.m("MULTIPLY", r3, 26.0))
    cyc = T.m("ADD", rows, trail)
    head = T.m("SUBTRACT", rows, T.m("MULTIPLY", T.m("FRACT", T.m("ADD", T.m("DIVIDE", T.m("MULTIPLY", t, speed), cyc), r1)), cyc))
    row = T.m("FLOOR", uy); d = T.m("SUBTRACT", row, T.m("FLOOR", head))
    inten = T.m("MULTIPLY", T.m("GREATER_THAN", d, -0.5), T.m("EXPONENT", T.m("DIVIDE", T.m("MULTIPLY", d, -1.0), trail)))
    isHead = T.m("LESS_THAN", T.m("ABSOLUTE", d), 0.5)
    h = T.wn(T.combine(row, T.m("MULTIPLY", r1, 137.0), T.m("FLOOR", T.m("ADD", T.m("MULTIPLY", t, T.m("ADD", 2.0, T.m("MULTIPLY", r3, 5.0))), T.m("MULTIPLY", T.wn(T.combine(row, r1), "2D"), 3.0)))))
    g = T.sep(atlas_sample(T, h, (ux, T.m("FRACT", uy))))[0]
    col = T.ramp(T.m("ADD", T.m("MULTIPLY", inten, 0.75), T.m("MULTIPLY", isHead, 0.3)), [(0.0, C["deep"]), (0.35, C["green"]), (0.75, C["green2"]), (0.92, C["lime"]), (1.0, C["cream"])])
    strength = T.m("ADD", T.m("MULTIPLY", inten, 3.0), T.m("MULTIPLY", isHead, 6.0))
    alpha = T.m("MULTIPLY", g, T.m("MINIMUM", 1.0, T.m("ADD", T.m("MULTIPLY", inten, 1.3), 0.04)))
    tr = T.n("ShaderNodeBsdfTransparent").outputs[0]
    out(T, mix_shader(T, alpha, tr, emission(T, col, strength))); m.blend_method = "HASHED"; return m
M_RAIN = rain_material()

def strip(name, x, y, z0, height, width=0.16):
    rows = max(8, int(height / width))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    a = bm.verts.new((-width / 2, 0, 0)); b = bm.verts.new((width / 2, 0, 0)); c = bm.verts.new((width / 2, 0, rows * width)); d = bm.verts.new((-width / 2, 0, rows * width))
    f = bm.faces.new([a, b, c, d])
    for lp, uvv in zip(f.loops, [(0, 0), (1, 0), (1, rows), (0, rows)]): lp[uvl].uv = uvv
    o = obj_from_bm(name, bm, M_RAIN, O + Vector((x, y, z0))); o["rows"] = float(rows); o.visible_shadow = False
    return o
k = 0
for _ in range(260):
    x = rnd.uniform(-11, 11)
    if abs(x) < 0.7: continue
    strip(f"rain_{k:03d}", x, rnd.uniform(-1, 70), rnd.uniform(-1, 6), rnd.uniform(6, 30)); k += 1
for _ in range(60):  # dense curtain where we arrive from the screen
    x = rnd.uniform(-3, 3)
    if abs(x) < 0.35: continue
    strip(f"rain_{k:03d}", x, rnd.uniform(-1.5, 8), rnd.uniform(-2, 2), rnd.uniform(4, 12), 0.12); k += 1

def tower_material():
    m, T = new_mat("ph_tower")
    p = T.n("ShaderNodeTexCoord").outputs["Object"]; px, py, pz = T.sep(p)
    cell = T.combine(T.m("FLOOR", T.m("MULTIPLY", px, 5.0)), T.m("FLOOR", T.m("MULTIPLY", py, 5.0)), T.m("FLOOR", T.m("MULTIPLY", pz, 3.5)))
    lit = T.m("GREATER_THAN", T.wn(cell), 0.9)
    fz = T.m("FRACT", T.m("MULTIPLY", pz, 3.5)); fh = T.m("FRACT", T.m("MULTIPLY", T.m("ADD", px, py), 5.0))
    win = T.m("MULTIPLY", T.m("MULTIPLY", T.m("GREATER_THAN", fz, 0.25), T.m("LESS_THAN", fz, 0.7)), T.m("MULTIPLY", T.m("GREATER_THAN", fh, 0.2), T.m("LESS_THAN", fh, 0.75)))
    br = T.n("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.012; br.offset = 0.0
    br.inputs["Brick Width"].default_value = 1.4; br.inputs["Row Height"].default_value = 0.9; T.link(T.combine(T.m("ADD", px, py), pz), br.inputs["Vector"])
    pr = T.n("ShaderNodeTexNoise"); pr.inputs["Scale"].default_value = 0.8; T.link(p, pr.inputs["Vector"])
    trough = T.m("ADD", 0.28, T.m("MULTIPLY", pr.outputs["Fac"], 0.25))
    b = principled(T, hexc("#18301F"), trough, metal=0.2, coat=0.45, coat_rough=0.1, spec=0.7)
    tb = T.n("ShaderNodeBump"); tb.inputs["Strength"].default_value = 0.6; tb.inputs["Distance"].default_value = 0.02; tb.invert = True
    T.link(br.outputs["Fac"], tb.inputs["Height"]); T.link(tb.outputs[0], b.inputs["Normal"])
    out(T, add_shader(T, b.outputs[0], emission(T, T.ramp(T.wn(cell), [(0.0, C["green"]), (0.7, C["green2"]), (1.0, C["lime"])]), T.m("MULTIPLY", T.m("MULTIPLY", lit, win), 0.0)))); return m
M_TOWER = tower_material()
m_, T_ = new_mat("ph_edge"); out(T_, emission(T_, C["green2"], 3.0)); M_EDGE = m_
# ---------------- the city: a C4D-style cloner with random + noise effectors (geometry nodes) ----------------
def vnoise2(x, y):
    """smooth 2D value noise 0..1 (deterministic)"""
    def h(i, j): return (math.sin(i * 127.1 + j * 311.7) * 43758.5453) % 1.0
    i, j = math.floor(x), math.floor(y); fx, fy = x - i, y - j; fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a_, b_, c_, d_ = h(i, j), h(i + 1, j), h(i, j + 1), h(i + 1, j + 1)
    return a_ + (b_ - a_) * fx + (c_ - a_) * fy + (a_ - b_ - c_ + d_) * fx * fy

def tower_variant(name, base, rough, metal, coat, aniso=0.0, circuit=False):
    m, T = new_mat(name); p_ = T.n("ShaderNodeTexCoord").outputs["Object"]
    pr = T.n("ShaderNodeTexNoise"); pr.inputs["Scale"].default_value = 3.0; T.link(p_, pr.inputs["Vector"])
    b = principled(T, hexc(base), T.m("ADD", rough, T.m("MULTIPLY", pr.outputs["Fac"], 0.12)), metal=metal, coat=coat, coat_rough=0.06, spec=0.7)
    b.inputs["Anisotropic"].default_value = aniso
    bp = T.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; T.link(pr.outputs["Fac"], bp.inputs["Height"]); T.link(bp.outputs[0], b.inputs["Normal"])
    shader = b.outputs[0]
    if circuit:  # thin glowing traces etched into the faces
        px, py, pz = T.sep(p_)
        lanes = T.m("MAXIMUM", T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("FRACT", T.m("MULTIPLY", T.m("ADD", px, py), 6.0)), 0.5)), 0.02),
                    T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("FRACT", T.m("MULTIPLY", pz, 9.0)), 0.5)), 0.015))
        on = T.m("GREATER_THAN", T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", T.m("ADD", px, py), 3.0)), T.m("FLOOR", T.m("MULTIPLY", pz, 4.0)))), 0.6)
        shader = add_shader(T, shader, emission(T, C["green2"], T.m("MULTIPLY", T.m("MULTIPLY", lanes, on), 2.2)))
    out(T, shader); return m
MATS_CITY = {
    "satin": tower_variant("ph_city_satin", "#18301F", 0.3, 0.2, 0.45),
    "glass": tower_variant("ph_city_glass", "#040806", 0.03, 0.0, 1.0),
    "concrete": tower_variant("ph_city_concrete", "#2A3A30", 0.75, 0.0, 0.0),
    "metal": tower_variant("ph_city_metal", "#7E8C82", 0.32, 1.0, 0.0, aniso=0.6),
    "circuit": tower_variant("ph_city_circuit", "#08120C", 0.2, 0.3, 0.6, circuit=True),
}
mg_, TG_ = new_mat("ph_city_glow"); out(TG_, add_shader(TG_, principled(TG_, hexc("#0C1A10"), 0.2, coat=1.0).outputs[0], emission(TG_, C["green2"], 1.4))); MATS_CITY["glow"] = mg_

def src_shape(name, mat, shape="cube", bevel=0.035):
    bm = bmesh.new()
    if shape == "cube": bmesh.ops.create_cube(bm, size=1.0)
    else: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.5, radius2=0.5, depth=1.0)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, affect="EDGES", profile=0.5)
    for f in bm.faces: f.smooth = False
    o = obj_from_bm(name, bm, mat, (0, 0, -500)); o.hide_render = True; o.hide_viewport = True
    return o

def cloner(name, source, pts, scale, rot=None, nrm=None, base=None, amp=None):
    """points + per-point scale/rotation; optional animated 'drawer' push along nrm: d = base + amp * noise(pos, time)"""
    me = bpy.data.meshes.new(name); me.vertices.add(len(pts)); me.vertices.foreach_set("co", [c for p_ in pts for c in p_])
    def attr(nm, data, kind):
        at = me.attributes.new(nm, kind, "POINT"); at.data.foreach_set("vector" if kind == "FLOAT_VECTOR" else "value", [c for t in data for c in t] if kind == "FLOAT_VECTOR" else data)
    attr("scl", scale, "FLOAT_VECTOR"); attr("rot", rot or [0.0] * len(pts), "FLOAT")
    anim = nrm is not None
    if anim: attr("nrm", nrm, "FLOAT_VECTOR"); attr("base", base, "FLOAT"); attr("amp", amp, "FLOAT")
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    ng = bpy.data.node_groups.new(f"{name}_gn", "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    G = NT(ng); gi = G.n("NodeGroupInput"); go = G.n("NodeGroupOutput")
    def named(nm, dt):
        n_ = G.n("GeometryNodeInputNamedAttribute", data_type=dt); n_.inputs["Name"].default_value = nm; return n_.outputs["Attribute"]
    geo = gi.outputs[0]; scl = named("scl", "FLOAT_VECTOR")
    if anim:
        t = G.n("GeometryNodeInputSceneTime").outputs["Seconds"]
        pos = G.n("GeometryNodeInputPosition").outputs[0]
        nz = G.n("ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 1.0
        G.link(pos, nz.inputs["Vector"]); G.link(G.m("MULTIPLY", t, 0.45), nz.inputs["W"])
        d = G.m("MAXIMUM", G.m("ADD", named("base", "FLOAT"), G.m("MULTIPLY", named("amp", "FLOAT"), G.m("MULTIPLY", G.m("SUBTRACT", nz.outputs["Fac"], 0.5), 3.0))), 0.03)
        n_ = named("nrm", "FLOAT_VECTOR"); an = G.v("ABSOLUTE", n_)
        scl = G.v("ADD", G.v("MULTIPLY", scl, G.v("SUBTRACT", (1.0, 1.0, 1.0), an)), G.v("SCALE", an, scale=d))
        sp = G.n("GeometryNodeSetPosition"); G.link(geo, sp.inputs["Geometry"]); G.link(G.v("SCALE", n_, scale=G.m("MULTIPLY", d, 0.5)), sp.inputs["Offset"]); geo = sp.outputs[0]
    oi = G.n("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = source
    iop = G.n("GeometryNodeInstanceOnPoints"); G.link(geo, iop.inputs["Points"]); G.link(oi.outputs["Geometry"], iop.inputs["Instance"])
    G.link(scl, iop.inputs["Scale"]); G.link(G.combine(0.0, 0.0, named("rot", "FLOAT")), iop.inputs["Rotation"])
    G.link(iop.outputs[0], go.inputs[0])
    o.modifiers.new("cloner", "NODES").node_group = ng; o.visible_shadow = True
    return o

SRC = {k: src_shape(f"src_{k}", m_) for k, m_ in MATS_CITY.items()}
SRC_OCTA = {k: src_shape(f"srco_{k}", MATS_CITY[k], "octa") for k in ("satin", "glass", "metal")}
blocks = {k: ([], [], []) for k in list(SRC) + [f"o_{k}" for k in SRC_OCTA]}
drawer = {k: ([], [], [], [], [], []) for k in ("satin", "metal", "concrete", "glass", "glow")}
def add_block(key, cx, cy, z0, w, d, h, rot=0.0):
    pts, scl, rots = blocks[key]; pts.append((cx, cy, z0 + h / 2)); scl.append((w, d, h)); rots.append(rot)
def add_drawers(origin, u, n, width, z0, z1, style):
    """rectangles across a wall; each becomes a clone that the noise effector slides in and out along n"""
    up = Vector((0, 0, 1)); z = z0
    while z < z1 - 0.3:
        rh = min(z1 - z, rnd.choice(style["rows"])); x = 0.0
        while x < width - 0.2:
            cw = min(width - x, rnd.choice(style["cols"]))
            if rnd.random() < style["fill"]:
                key = "glow" if (rnd.random() < 0.07 and cw <= 1.0 and rh <= 1.2) else style["mat"]
                P_, S_, R_, N_, B_, A_ = drawer[key]; g = 0.05
                c = origin + u * (x + cw / 2) + up * (z - z0 + rh / 2)
                P_.append(tuple(c)); S_.append((abs(u.x) * (cw - g) + abs(n.x), abs(u.y) * (cw - g) + abs(n.y), rh - g)); R_.append(0.0)
                N_.append(tuple(n)); B_.append(rnd.choice(style["depths"])); A_.append(style["amp"] if rnd.random() < style["moving"] else 0.0)
            x += cw
        z += rh
STYLES = [  # facade styles: drawers, slats, louvres, big cantilevers
    {"rows": [0.5, 0.8, 1.2, 1.6], "cols": [0.5, 0.7, 1.0, 1.4], "fill": 0.85, "depths": [0.08, 0.15, 0.3, 0.55], "amp": 0.35, "moving": 0.5, "mat": "satin"},
    {"rows": [6.0, 9.0], "cols": [0.25, 0.35], "fill": 0.9, "depths": [0.3, 0.5], "amp": 0.15, "moving": 0.3, "mat": "metal"},          # vertical slats
    {"rows": [0.35, 0.45], "cols": [3.0, 5.0], "fill": 0.9, "depths": [0.25, 0.4], "amp": 0.2, "moving": 0.4, "mat": "concrete"},       # horizontal louvres
    {"rows": [2.0, 3.0, 4.0], "cols": [1.5, 2.0], "fill": 0.45, "depths": [0.8, 1.4, 2.2], "amp": 0.6, "moving": 0.6, "mat": "glass"},  # cantilevered boxes
]
CELL = 1.9
for side in (-1, 1):
    for col in range(8):
        for row in range(int(90 / CELL)):
            cx = O.x + side * (5.0 + col * CELL); cy = -8 + row * CELL
            if rnd.random() < 0.1: continue                                            # plazas / gaps
            hn = vnoise2((cx - O.x) * 0.09 + side * 9, cy * 0.07)                       # noise effector: skyline clusters
            h = 2.5 + 46 * (hn ** 2.2) * rnd.uniform(0.55, 1.25) * (0.55 if col == 0 else 1.0) + col * 1.2
            w, d = CELL * rnd.uniform(0.62, 0.96), CELL * rnd.uniform(0.62, 0.96)
            mk = rnd.choices(["satin", "glass", "concrete", "metal", "circuit"], [0.32, 0.24, 0.18, 0.12, 0.14])[0]
            if col >= 1 and rnd.random() < 0.12 and mk in SRC_OCTA: add_block(f"o_{mk}", cx, cy, 0, min(w, d), min(w, d), h, rnd.uniform(0, 1))
            else: add_block(mk, cx + rnd.uniform(-0.12, 0.12), cy + rnd.uniform(-0.12, 0.12), 0, w, d, h, rnd.choice([0.0, 0.0, math.pi / 2]) if col else 0.0)
            if rnd.random() < 0.3 and h > 6:                                                # stacked / jenga block on top
                add_block(rnd.choice(["satin", "glass", "metal"]), cx + rnd.uniform(-0.4, 0.4), cy + rnd.uniform(-0.4, 0.4), h, w * rnd.uniform(0.4, 0.8), d * rnd.uniform(0.4, 0.8), rnd.uniform(2, 9), rnd.uniform(0, 0.8))
            if rnd.random() < 0.08:                                                         # a glowing light bar on a corner
                add_block("glow", cx - side * w / 2, cy - d / 2, 0, 0.05, 0.05, h * rnd.uniform(0.5, 0.95))
            if col == 0:                                                                    # street wall: a cloned facade on it
                st = rnd.choice(STYLES)
                add_drawers(Vector((cx - side * w / 2, cy - d / 2, 0.0)), Vector((0, 1, 0)), Vector((-side, 0, 0)), d, 0.4, h, st)
                add_drawers(Vector((cx - w / 2, cy - d / 2, 0.0)), Vector((1, 0, 0)), Vector((0, -1, 0)), w, 0.4, h, st)
for key, (pts, scl, rots) in blocks.items():
    if pts: cloner(f"city_{key}", SRC_OCTA[key[2:]] if key.startswith("o_") else SRC[key], pts, scl, rots)
for key, (P_, S_, R_, N_, B_, A_) in drawer.items():
    if P_: cloner(f"facade_{key}", SRC[key], P_, S_, R_, N_, B_, A_)
log_counts = {k: len(v[0]) for k, v in blocks.items()}; print("CITY", log_counts, {k: len(v[0]) for k, v in drawer.items()}, flush=True)
bpy.ops.mesh.primitive_plane_add(size=1, location=O + Vector((0, 35, 0))); cf = bpy.context.object; cf.name = "code_floor"; cf.scale = (60, 120, 1); cf.data.materials.append(M_FLOOR_CODE)
# light shaft at the end of the street
m_, T_ = new_mat("ph_shaft")
lw = T_.n("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
shaftK = T_.keyed("shaftK", [0.22 if f < 190 else max(0.06, 0.22 - (f - 190) * 0.016) for f in range(1, N + 1)])
fac = T_.m("MULTIPLY", T_.m("POWER", T_.m("SUBTRACT", 1.0, lw.outputs["Facing"]), 3.0), shaftK)
out(T_, mix_shader(T_, fac, T_.n("ShaderNodeBsdfTransparent").outputs[0], emission(T_, C["green2"], 3.0))); m_.blend_method = "HASHED"; M_SHAFT = m_
bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=90, location=O + Vector((0, STATUE["y"] + 3.5, 40)), vertices=64); sh = bpy.context.object; sh.name = "shaft"; sh.data.materials.append(M_SHAFT); sh.visible_shadow = False

# ---------------- PHILLIPS DIGITAL: swarm, then neon ----------------
FONT = bpy.data.fonts.load(CFG["font_text"])
TEXT_Y, TEXT_Z, TARGET_W = 50.0, 3.0, 6.0  # world metres across "PHILLIPS DIGITAL" (about 70% of frame at the end)
def neon_mat(name, series):
    m, T = new_mat(name); s = T.keyed("neon", series, "CONSTANT")
    tube = principled(T, hexc("#1A2A1E"), 0.18, coat=1.0).outputs[0]
    core = emission(T, C["cream"], T.m("MULTIPLY", s, 7.0))
    out(T, add_shader(T, tube, core)); return m
def make_word(i, word, size):
    cu = bpy.data.curves.new(f"word_{i}", "FONT"); cu.body = word; cu.font = FONT; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.extrude = 0.03; cu.bevel_depth = 0.008; cu.bevel_resolution = 3
    ob = bpy.data.objects.new(f"word_{i}", cu); sc.collection.objects.link(ob); ob.rotation_euler = (math.pi / 2, 0, 0); ob.scale = (CFG["condense"], 1, 1.1)
    return ob
probe = make_word(9, CFG["words"][0] + " " + CFG["words"][1], 1.0); bpy.context.view_layer.update()
pw = max(v[0] for v in probe.bound_box) - min(v[0] for v in probe.bound_box)  # local width at size 1
bpy.data.objects.remove(probe, do_unlink=True)
SIZE = TARGET_W / (pw * CFG["condense"])
nchar = len(CFG["words"][0]) + 1 + len(CFG["words"][1]); cell = TARGET_W / nchar  # monospace: one cell per character
words = []
for wi, word in enumerate(CFG["words"]):
    start = 0 if wi == 0 else len(CFG["words"][0]) + 1
    cxw = (start + len(word) / 2) * cell - TARGET_W / 2
    ob = make_word(wi, word, SIZE); ob.location = O + Vector((cxw, TEXT_Y, TEXT_Z))
    keys(ob, "hide_render", [f < 192 for f in range(1, N + 1)], 1, "CONSTANT"); keys(ob, "hide_viewport", [f < 192 for f in range(1, N + 1)], 1, "CONSTANT")
    series = step_series(CFG["neon_a"] if wi == 0 else CFG["neon_b"])
    series = [v if f < CFG["black"] else 0 for f, v in zip(range(1, N + 1), series)]
    ob.data.materials.append(neon_mat(f"ph_neon_{wi}", series)); words.append((ob, series))
    # a light at each word so the neon lights the wet floor
    L = area_light(f"neon_light_{wi}", O + Vector((cxw, TEXT_Y - 0.6, TEXT_Z - 0.2)), O + Vector((cxw, TEXT_Y - 6, 0)), (len(word) * cell, 0.4), 0, C["lime2"])
    keys(L.data, "energy", [v * 320 for v in series], 1, "CONSTANT")

# sample the letters' front faces for the swarm targets
sc.frame_set(200); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
tris = []
for ob, _ in words:
    me = ob.evaluated_get(dg).to_mesh(); mw = ob.matrix_world
    for p in me.polygons:
        n = (mw.to_3x3() @ p.normal).normalized()
        if n.y > -0.9: continue
        vs_ = [mw @ me.vertices[i].co for i in p.vertices]
        for i in range(1, len(vs_) - 1):
            a, b, c = vs_[0], vs_[i], vs_[i + 1]; tris.append((a, b, c, ((b - a).cross(c - a)).length / 2))
    ob.evaluated_get(dg).to_mesh_clear()
sc.frame_set(1); tot = sum(t[3] for t in tris); NPART = 2200
pts = []
for _ in range(NPART):
    r = rnd.uniform(0, tot)
    for a, b, c, ar in tris:
        r -= ar
        if r <= 0: break
    u, v = rnd.random(), rnd.random()
    if u + v > 1: u, v = 1 - u, 1 - v
    pts.append(a + (b - a) * u + (c - a) * v + Vector((0, -0.05, 0)))
xs = [p.x for p in pts]; x0, x1 = min(xs), max(xs)
st0, stg, srnd, sdur, sdr = CFG["swarm"]
bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
delta_l, delay_l, dur_l, arc_l = [], [], [], []
q = 0.075
for p in pts:
    start = O + Vector((rnd.uniform(-7, 7), rnd.uniform(44, 60), rnd.uniform(0.5, 12)))
    delay = st0 + stg * (p.x - x0) / (x1 - x0) + rnd.uniform(0, srnd); dur = sdur + rnd.uniform(0, sdr)
    arc = Vector((rnd.uniform(-1, 1), rnd.uniform(-1.5, 0.5), rnd.uniform(0.3, 1.8)))
    gi = rnd.randrange(256); cx_, cy_ = gi % 16, gi // 16
    corners = [Vector((-q / 2, 0, -q / 2)), Vector((q / 2, 0, -q / 2)), Vector((q / 2, 0, q / 2)), Vector((-q / 2, 0, q / 2))]
    vv = [bm.verts.new(p + c) for c in corners]; f = bm.faces.new(vv)
    for lp, (a, b) in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]): lp[uvl].uv = ((cx_ + 0.07 + a * 0.86) / 16, 1 - (cy_ + 0.95 - b * 0.9) / 16)
    for _v in vv: delta_l.append(tuple(start - p)); delay_l.append(delay); dur_l.append(dur); arc_l.append(tuple(arc))
m_, T_ = new_mat("ph_swarm")
uvn = T_.n("ShaderNodeUVMap"); tex = T_.n("ShaderNodeTexImage", image=ATLAS, extension="CLIP"); T_.link(uvn.outputs[0], tex.inputs[0])
fade = T_.keyed("swarmFade", [1.0 if f < 200 else max(0.0, 1 - (f - 200) / 12) for f in range(1, N + 1)])
alpha = T_.m("MULTIPLY", T_.sep(tex.outputs["Color"])[0], fade)
out(T_, mix_shader(T_, alpha, T_.n("ShaderNodeBsdfTransparent").outputs[0], emission(T_, C["green2"], 3.5))); m_.blend_method = "HASHED"; M_SWARM = m_
sw = obj_from_bm("swarm", bm, M_SWARM); sw.visible_shadow = False
me = sw.data
for name, data, kind in (("delta", delta_l, "FLOAT_VECTOR"), ("arc", arc_l, "FLOAT_VECTOR"), ("delay", delay_l, "FLOAT"), ("dur", dur_l, "FLOAT")):
    at = me.attributes.new(name, kind, "POINT")
    flat = [c for t in data for c in t] if kind == "FLOAT_VECTOR" else data
    at.data.foreach_set("vector" if kind == "FLOAT_VECTOR" else "value", flat)
# geometry nodes: each glyph flies from the rain to its letter (smoothstep), bowing along an arc
ng = bpy.data.node_groups.new("ph_swarm_fly", "GeometryNodeTree")
ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
G_ = NT(ng); gin = G_.n("NodeGroupInput"); gout = G_.n("NodeGroupOutput")
stime = G_.n("GeometryNodeInputSceneTime")
def named(nm, dt):
    n_ = G_.n("GeometryNodeInputNamedAttribute", data_type=dt); n_.inputs["Name"].default_value = nm; return n_.outputs["Attribute"]
dl, du = named("delay", "FLOAT"), named("dur", "FLOAT")
mr = G_.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", clamp=True)
G_.link(stime.outputs["Seconds"], mr.inputs["Value"]); G_.link(dl, mr.inputs["From Min"]); G_.link(G_.m("ADD", dl, du), mr.inputs["From Max"])
k_ = mr.outputs["Result"]
off = G_.v("ADD", G_.v("SCALE", named("delta", "FLOAT_VECTOR"), scale=G_.m("SUBTRACT", 1.0, k_)),
           G_.v("SCALE", named("arc", "FLOAT_VECTOR"), scale=G_.m("SINE", G_.m("MULTIPLY", k_, math.pi))))
spn = G_.n("GeometryNodeSetPosition"); G_.link(gin.outputs[0], spn.inputs["Geometry"]); G_.link(off, spn.inputs["Offset"]); G_.link(spn.outputs[0], gout.inputs[0])
sw.modifiers.new("fly", "NODES").node_group = ng

# ---------------- a distant statue at the end of the street ----------------
# "Theodoric the Great" (Court Church, Innsbruck), scan by Oliver Laric, threedscans.com (free to use without copyright
# restrictions), decimated to 200k triangles in public/models. Dark obsidian chrome, gold in the crevices, faint green
# circuits that boot up as the neon ignites. Small in frame: a silhouette in the beam, behind the words.
bpy.ops.wm.stl_import(filepath=STATUE["model"]); stat = bpy.context.selected_objects[0]; stat.name = "statue"
stat.matrix_world = Matrix.Identity(4)
for poly in stat.data.polygons: poly.use_smooth = True
def statue_mat():
    m, T = new_mat("ph_statue"); obj = T.n("ShaderNodeTexCoord").outputs["Object"]; px, py, pz = T.sep(obj)
    boot = T.keyed("boot", [min(1.0, max(0.0, (f - STATUE["boot"][0]) / (STATUE["boot"][1] - STATUE["boot"][0]))) for f in range(1, N + 1)])
    ao = T.n("ShaderNodeAmbientOcclusion", samples=8, only_local=True); ao.inputs["Distance"].default_value = 0.4
    chrome = principled(T, hexc("#060A07"), 0.12, metal=1.0, coat=0.8, coat_rough=0.05)
    gold = principled(T, hexc("#A87C2A"), 0.3, metal=1.0)
    cav = T.m("POWER", T.m("SUBTRACT", 1.0, ao.outputs["AO"], clamp=True), 1.4)
    skin = mix_shader(T, T.m("MULTIPLY", cav, 1.6, clamp=True), chrome.outputs[0], gold.outputs[0])
    hz = T.m("LESS_THAN", T.m("ABSOLUTE", T.m("SUBTRACT", T.m("FRACT", T.m("MULTIPLY", pz, 70.0)), 0.5)), 0.03)
    seg = T.m("GREATER_THAN", T.wn(T.combine(T.m("FLOOR", T.m("MULTIPLY", px, 25.0)), T.m("FLOOR", T.m("MULTIPLY", pz, 35.0)), 5.0)), 0.7)
    reveal = T.m("LESS_THAN", pz, T.m("MULTIPLY", boot, 1.05))
    em = emission(T, C["green2"], T.m("MULTIPLY", T.m("MULTIPLY", T.m("MULTIPLY", hz, seg), reveal), 3.0))
    out(T, add_shader(T, skin, em)); return m
stat.data.materials.append(statue_mat())
stat.scale = (STATUE["height"],) * 3; stat.location = O + Vector((0, STATUE["y"], 0))
sc_ = O + Vector((0, STATUE["y"], STATUE["height"] * 0.55))
area_light("statue_rim_l", O + Vector((-4.0, STATUE["y"] + 3.0, 6.0)), sc_, (0.8, 5.0), 2200, C["green2"])
area_light("statue_rim_r", O + Vector((4.0, STATUE["y"] + 3.0, 6.0)), sc_, (0.8, 5.0), 2200, C["green2"])
area_light("statue_top", O + Vector((0, STATUE["y"] - 4.0, 14.0)), sc_, (3.0, 1.5), 900, C["cream"])

# ---------------- atmosphere: real haze, a real beam, raking lights, floating dust ----------------
def volume_box(name, lo, hi, density, colour, aniso):
    c = (Vector(lo) + Vector(hi)) / 2; sz = Vector(hi) - Vector(lo)
    o = box(name, tuple(sz), tuple(c)); m, T = new_mat(f"ph_{name}")
    pv = T.n("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = colour; pv.inputs["Density"].default_value = density; pv.inputs["Anisotropy"].default_value = aniso
    o_ = T.n("ShaderNodeOutputMaterial"); T.link(pv.outputs[0], o_.inputs["Volume"]); o.data.materials.append(m); o.visible_shadow = False
    return o
volume_box("haze_street", O + Vector((-16, -10, 0.01)), O + Vector((16, TEXT_Y + 1.0, 26)), 0.006, hexc("#C8DCC0"), 0.6)
volume_box("haze_far", O + Vector((-16, TEXT_Y + 1.02, 0.01)), O + Vector((16, 82, 26)), 0.003, hexc("#C8DCC0"), 0.6)
volume_box("haze_room", (-2.2, -3.2, 0.005), (2.2, 2.1, 2.4), 0.022, hexc("#E6EEE4"), 0.6)
def spot(name, loc, target, power, colour, size_deg, blend, radius=0.3):
    ld = bpy.data.lights.new(name, "SPOT"); ld.energy = power; ld.color = colour[:3]; ld.spot_size = math.radians(size_deg); ld.spot_blend = blend; ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
beam = spot("beam", O + Vector((0, STATUE["y"], 30)), O + Vector((0, STATUE["y"], 0)), 90000, C["green2"], 9, 0.6, 0.6)   # the light shaft through the haze
keys(beam.data, "energy", [40000 if f < 190 else max(14000, 40000 - (f - 190) * 1800) for f in range(1, N + 1)], 1)
# small, bright, hidden lights: crisp highlights run along bevels, ledges and fins (no big pale reflections)
for k, (lx, ly, lz, ty, col, pw) in enumerate([(-2.5, 8, 9, 14, "sage2", 260), (2.5, 16, 7, 22, "lime", 200), (-2.0, 26, 12, 32, "green2", 260),
                                               (2.2, 34, 10, 40, "sage2", 240), (-2.4, 44, 8, 50, "lime", 200), (0.0, 30, 22, 36, "cream", 300)]):
    area_light(f"rake_{k}", O + Vector((lx, ly, lz)), O + Vector((-lx * 2.6, ty, lz * 0.5)), (0.6, 0.35), pw * 4, C[col])
    area_light(f"rakeM_{k}", O + Vector((-lx, ly + 2, lz + 3)), O + Vector((lx * 2.6, ty + 2, lz * 0.6)), (0.6, 0.35), pw * 3.2, C[col])
area_light("back_glow", O + Vector((0, 60, 4.5)), O + Vector((0, 40, 2.5)), (10.0, 4.0), 700, C["green2"], reflect=False)  # behind the words: rim + glowing air
area_light("screen_spill", (SCX, -0.5, SCZ), (SCX, -2.0, SCZ), (0.42, 0.32), 0, C["lime"])                            # helps the screen's cone show in the room haze
spill = bpy.data.objects["screen_spill"].data
keys(spill, "energy", [p * 6 for p in step_series([(f, p) for f, p, _ in CFG["screen"]])][:CFG["shatter"]] + [0] * (N - CFG["shatter"]), 1, "CONSTANT")
def dust(name, lo, hi, count, size, mat, drift):
    bm = bmesh.new()
    for _ in range(count):
        c = Vector((rnd.uniform(lo[0], hi[0]), rnd.uniform(lo[1], hi[1]), rnd.uniform(lo[2], hi[2])))
        r = size * rnd.uniform(0.5, 1.4); vs_ = [bm.verts.new(c + Vector(d) * r) for d in ((1, 0, -0.7), (-1, 0, -0.7), (0, 1, 0.7), (0, -1, 0.7))]
        for f_ in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)): bm.faces.new([vs_[i] for i in f_])
    o = obj_from_bm(name, bm, mat); o.visible_shadow = False
    keys(o, "location", [tuple(Vector(drift) * (f / FPS)) for f in range(1, N + 1)], 3); return o
mdust, TD = new_mat("ph_dust"); out(TD, add_shader(TD, principled(TD, hexc("#E8F0DC"), 0.9).outputs[0], emission(TD, C["green2"], 0.15))); M_DUST = mdust
dust("dust_room", (-1.2, -2.4, 0.05), (1.2, 0.2, 1.5), 900, 0.0018, M_DUST, (0.004, 0.0, 0.012))
dust("dust_street", O + Vector((-8, -2, 0.2)), O + Vector((8, 56, 12)), 4000, 0.012, M_DUST, (0.05, 0.0, 0.08))

# ---------------- camera ----------------
def ease_io(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ease_in(x): x = max(0.0, min(1.0, x)); return x ** 2.6
def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
SC = Vector((SCX, SY, SCZ))
def cam_at(f):
    """position, look-at, lens (mm), focus distance, f-stop for frame f"""
    if f < CFG["cut"]:
        a, b = Vector((0.5, -2.2, 0.38)), Vector((0.12, -1.25, 0.3))
        if f <= 96:
            p = a.lerp(b, ease_io((f - 1) / 95)); look = Vector((-0.02, -0.2, 0.25)).lerp(SC, ease_io((f - 1) / 95))
        else:
            k = ease_in((f - 96) / (CFG["cut"] - 96)); p = b.lerp(Vector((SCX, -0.16, SCZ)), k); look = SC + Vector((0, 1, 0))
        return p, look, 40.0, max(0.05, (p - SC).length), 2.8
    k = (f - CFG["cut"]) / (170 - CFG["cut"])
    if f <= 170:
        p = O + Vector((0, -2.0, 1.3)).lerp(Vector((0, 38.0, 2.6)), ease_out(k)); look = p + Vector((0, 10, 0.25 + 0.2 * (1 - k)))
        return p, look, 28.0, 20.0, 5.6
    k = (f - 170) / (CFG["black"] - 170)
    p = O + Vector((0, 38.0, 2.6)).lerp(Vector((0, 42.6, 2.85)), ease_io(k)); look = O + Vector((0, TEXT_Y, TEXT_Z))
    return p, look, 30.0, (look - p).length, 3.5
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_mode = "QUATERNION"; cam_d.clip_start = 0.01; cam_d.clip_end = 200; cam_d.sensor_width = 36
cam_d.dof.use_dof = True; cam_d.dof.aperture_blades = 7
L_, R_, LE, FO, FS = [], [], [], [], []
for f in range(1, N + 1):
    p, look, lens, foc, fs = cam_at(f)
    z = (p - look).normalized(); x = Vector((0, 0, 1)).cross(z).normalized(); y_ = z.cross(x)
    q_ = Matrix(((x.x, y_.x, z.x), (x.y, y_.y, z.y), (x.z, y_.z, z.z))).to_quaternion()
    if R_ and q_.dot(Quaternion(R_[-1])) < 0: q_ = -q_
    L_.append(tuple(p)); R_.append(tuple(q_)); LE.append(lens); FO.append(foc); FS.append(fs)
keys(cam, "location", L_, 3); keys(cam, "rotation_quaternion", R_, 4)
keys(cam_d, "lens", LE, 1); keys(cam_d, "dof.focus_distance", FO, 1); keys(cam_d, "dof.aperture_fstop", FS, 1)
for fc in cam.animation_data.action.fcurves:  # the cut is a jump, not a slide
    for kp in fc.keyframe_points:
        if int(kp.co[0]) in (CFG["cut"] - 1, CFG["cut"]): kp.interpolation = "CONSTANT"

# ---------------- world, haze, glow, flash and the cut to black ----------------
wd = bpy.data.worlds.new("void"); sc.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = hexc("#06100A"); bg.inputs["Strength"].default_value = 0.04
wd.mist_settings.start = 6.0; wd.mist_settings.depth = 70.0; wd.mist_settings.falloff = "QUADRATIC"
vl = sc.view_layers[0]; vl.use_pass_mist = True
sc.use_nodes = True; ct = sc.node_tree; ct.nodes.clear(); CT = NT(ct)
rl = CT.n("CompositorNodeRLayers")
haze = CT.n("CompositorNodeMixRGB", blend_type="SCREEN"); haze.inputs[2].default_value = hexc("#1C5A2E")
hz = CT.n("CompositorNodeMath", operation="MULTIPLY"); hz.name = "hazeK"; hz.inputs[1].default_value = 0.0
keys(ct, 'nodes["hazeK"].inputs[1].default_value', [0.0 if f < CFG["cut"] else 0.12 for f in range(1, N + 1)], 1, "CONSTANT")
ct.links.new(rl.outputs["Mist"], hz.inputs[0]); ct.links.new(hz.outputs[0], haze.inputs[0]); ct.links.new(rl.outputs["Image"], haze.inputs[1])
glare = CT.n("CompositorNodeGlare", glare_type="FOG_GLOW", quality="HIGH", size=8, threshold=0.9, mix=0.0)
ct.links.new(haze.outputs[0], glare.inputs[0])
expo = CT.n("CompositorNodeExposure"); expo.name = "flash"; ct.links.new(glare.outputs[0], expo.inputs[0])
cut = CFG["cut"]
flash = [{cut - 2: 1.2, cut - 1: 2.2, cut: 2.6, cut + 1: 2.0, cut + 2: 1.3, cut + 3: 0.8, cut + 4: 0.45, cut + 5: 0.2}.get(f, 0.0) for f in range(1, N + 1)]
keys(ct, 'nodes["flash"].inputs[1].default_value', flash, 1)
fade = CT.n("CompositorNodeMixRGB", blend_type="MULTIPLY"); fade.name = "fade"; fade.inputs[2].default_value = (0, 0, 0, 1)
ct.links.new(expo.outputs[0], fade.inputs[1])
keys(ct, 'nodes["fade"].inputs[0].default_value', [1.0 if f >= CFG["black"] else max(0.0, 1 - (f - 1) / 6) for f in range(1, N + 1)], 1, "CONSTANT")
cb = CT.n("CompositorNodeColorBalance", correction_method="LIFT_GAMMA_GAIN")
cb.lift = (1.0, 1.0, 1.0); cb.gamma = (1.0, 1.0, 1.0); cb.gain = (1.0, 1.0, 1.0)   # neutral: the original look   # pull the yellow out, keep blacks clean
hs = CT.n("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = 1.0; hs.inputs["Hue"].default_value = 0.5
ct.links.new(fade.outputs[0], cb.inputs[1]); ct.links.new(cb.outputs[0], hs.inputs["Image"])
comp = CT.n("CompositorNodeComposite"); ct.links.new(hs.outputs[0], comp.inputs["Image"])
view = CT.n("CompositorNodeViewer"); ct.links.new(hs.outputs[0], view.inputs[0])

# ---------------- render settings + save ----------------
cy = sc.cycles; sc.render.engine = "CYCLES"
cy.max_bounces = 10; cy.glossy_bounces = 6; cy.transmission_bounces = 6; cy.transparent_max_bounces = 32; cy.diffuse_bounces = 3
cy.sample_clamp_indirect = 6.0; cy.blur_glossy = 0.6; cy.volume_bounces = 1; cy.volume_step_rate = 1.0; cy.volume_max_steps = 256
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = 0.0
os.makedirs(os.path.dirname(OUT), exist_ok=True)
import farm_prep
farm_prep.prepare(sc, OUT, samples=128 if MODE == "farm" else 64, frames=(1, N), name="phillips_digital", fps=FPS, motion_blur=(MODE == "farm"))
