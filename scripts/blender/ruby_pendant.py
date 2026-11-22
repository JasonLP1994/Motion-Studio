# Ruby pendant (rose gold, diamond centre, ruby halo) on a black set with one steel-blue spotlight pool.
# Grammar from references/jewelry/ruby-ref-v1.mp4 (never its brand or design). Plan: notes/ruby/plan.md.
# Units: 1 Blender unit = 1 cm. Every timing / colour / size lives in CFG.
# Usage: blender -b --factory-startup -P scripts/blender/ruby_pendant.py -- <out.blend>
import bpy, bmesh, math, sys, os
from mathutils import Vector, Euler

CFG = {
    "fps": 30, "frames": 360, "res": (1280, 720),               # 720p, AI-upscaled 2x to 1080p
    "col": {"rose": (0.88, 0.52, 0.40), "ruby": (0.80, 0.0, 0.025), "pool": (0.40, 0.62, 0.82),
            "floor": (0.11, 0.12, 0.13), "key": (1.0, 0.96, 0.92)},
    "floor_z": -2.2,
    # explode / assemble (Blender frames = plan frame + 1). 100 BPM: beat = 18 frames
    "explode": (145, 181), "hold_end": 199,
    "land": {"dia": (199, 208), "halo": (199, 208), "bail": (217, 226), "chain": (235, 244)},
    "apart": {"dia": (0, -0.1, 1.5), "halo": (0, -0.35, -0.65), "bail": (0, 0.7, 0.6), "chain": (0, 1.3, 1.1)},
    "glints": [109, 325],          # sparkle-light spikes (star glare) on the beats
    # cameras: name, first frame, (pos start, pos end), (target start, target end), lens, f-stop, interpolation
    "cams": [
        ("MAC", 1, ((0.05, -0.3, 1.7), (0.12, -0.6, 3.5)), ((0, 0, 0.42), (0, 0, 0.4)), 100, 2.8, "LINEAR"),
        ("TOP", 37, ((0.0, -0.05, 5.5), (0.0, -0.5, 14.0)), ((0, 0.45, 0), (0, 0.5, 0)), 50, 8, "EXPO"),
        ("TQ", 109, ((-7.0, -10.5, 9.6), (-5.9, -9.2, 8.4)), ((0.25, 0.5, 0.3), (0.3, 0.55, 0.35)), 60, 11, "LINEAR"),
        ("MA", 199, ((2.7, -4.7, 5.9), (2.4, -4.3, 5.3)), ((0, 0, 0.36), (0, 0, 0.34)), 85, 5.6, "LINEAR"),
        ("MB", 217, ((-3.5, 0.3, 4.3), (-3.2, 0.5, 3.9)), ((0, 1.3, -0.7), (0, 1.32, -0.7)), 85, 5.6, "LINEAR"),
        ("MC", 235, ((4.0, 4.16, 2.68), (3.6, 3.9, 2.3)), ((0, 1.76, -0.92), (0, 1.76, -0.92)), 85, 5.6, "LINEAR"),
        ("HERO", 253, ((-2.4, -4.6, 8.0), (-0.6, -5.8, 10.6)), ((0, 0.55, 0.0), (0, 0.6, 0.0)), 45, 11, "EXPO"),
    ],
}
OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/ruby.blend"
C = CFG["col"]

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.unit_settings.scale_length = 0.01
S.render.fps = CFG["fps"]; S.frame_start, S.frame_end = 1, CFG["frames"]
COLL = {}
for n in ("PRODUCT", "SET"):
    c = bpy.data.collections.new(n); S.collection.children.link(c); COLL[n] = c

def link(o, coll="PRODUCT"):
    for c in o.users_collection: c.objects.unlink(o)
    COLL[coll].objects.link(o); return o

def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc; e.parent = parent; link(e); return e

# ---------------- materials ----------------
def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); return m, nt, out

def m_rose():
    m, nt, out = mat("MAT_RoseGold"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*C["rose"], 1); b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.11
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m

def m_diamond():   # fake dispersion: three glass layers, one per colour channel, slightly different IOR (Blender 4.0 has none)
    m, nt, out = mat("MAT_Diamond"); prev = None
    for col, ior in (((1, 0, 0, 1), 2.38), ((0, 1, 0, 1), 2.42), ((0, 0, 1, 1), 2.47)):
        g = nt.nodes.new("ShaderNodeBsdfGlass"); g.inputs["Color"].default_value = col; g.inputs["IOR"].default_value = ior
        g.inputs["Roughness"].default_value = 0.0
        if prev is None: prev = g.outputs[0]
        else:
            a = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(prev, a.inputs[0]); nt.links.new(g.outputs[0], a.inputs[1]); prev = a.outputs[0]
    nt.links.new(prev, out.inputs["Surface"]); return m

def m_ruby():
    m, nt, out = mat("MAT_Ruby"); g = nt.nodes.new("ShaderNodeBsdfGlass")
    g.inputs["Color"].default_value = (1.0, 0.3, 0.34, 1); g.inputs["IOR"].default_value = 1.77; g.inputs["Roughness"].default_value = 0.0
    v = nt.nodes.new("ShaderNodeVolumeAbsorption"); v.inputs["Color"].default_value = (*C["ruby"], 1); v.inputs["Density"].default_value = 30.0
    nt.links.new(g.outputs[0], out.inputs["Surface"]); nt.links.new(v.outputs[0], out.inputs["Volume"]); return m

def m_floor():
    m, nt, out = mat("MAT_Floor"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*C["floor"], 1); b.inputs["Roughness"].default_value = 0.6
    b.inputs["Specular IOR Level"].default_value = 0.0   # pure diffuse: the hidden reflection world never greys the black floor
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m

ROSE, DIA, RUBY, FLOOR = m_rose(), m_diamond(), m_ruby(), m_floor()

# ---------------- geometry ----------------
def gem_mesh(name, r):
    """round brilliant from its key facet points + convex hull (table, star, upper girdle, girdle, pavilion, culet)"""
    pts = []
    tr, ch, gh, pd = 0.56 * r, 0.33 * r, 0.035 * r, 0.86 * r      # table radius, crown height, girdle half-thickness, pavilion depth
    for k in range(8):
        a = k * math.pi / 4
        pts.append((tr * math.cos(a), tr * math.sin(a), gh + ch))                      # table
        a2 = a + math.pi / 8
        pts.append((0.80 * r * math.cos(a2), 0.80 * r * math.sin(a2), gh + 0.55 * ch))  # star / upper main
        pts.append((0.46 * r * math.cos(a2), 0.46 * r * math.sin(a2), -gh - 0.55 * pd)) # pavilion mains
    for k in range(32):
        a = k * math.pi / 16
        for z in (gh, -gh): pts.append((r * math.cos(a), r * math.sin(a), z))           # girdle
    pts.append((0, 0, -gh - pd))                                                        # culet
    bm = bmesh.new()
    for p in pts: bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    return me

def obj(name, me, m, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); me.materials.append(m) if len(me.materials) == 0 else None
    o.location = loc; o.rotation_euler = rot; o.parent = parent; link(o); return o

def torus(name, R, r, m, loc=(0, 0, 0), rot=(0, 0, 0), sz=1.0, parent=None, seg=(96, 24)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg[0], minor_segments=seg[1])
    o = bpy.context.object; o.name = name; o.location = loc; o.rotation_euler = rot; o.scale.z = sz
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); o.parent = parent; link(o); return o

def sphere(name, r, m, loc, parent, me_cache={}):
    key = (r, m.name)
    if key not in me_cache:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=16, ring_count=8); s = bpy.context.object
        bpy.ops.object.shade_smooth(); s.data.materials.append(m); me_cache[key] = s.data; bpy.data.objects.remove(s)
    return obj(name, me_cache[key], m, loc, parent)

ROOT = empty("PENDANT")
HALO = empty("G_HALO", parent=ROOT); DIAG = empty("G_DIAMOND", parent=ROOT)
BAIL = empty("G_BAIL", parent=ROOT); CHAIN = empty("G_CHAIN", parent=ROOT)

# the pendant: a real jewellery CAD model, "ChapelHills BluTourmPndt" by CADtrends (Sketchfab c091efb068624f228432cbfb7b21a0ec,
# CC-BY 4.0, via Objaverse), split into groups by scripts/blender/ruby_model_prep.py. Its own chain is replaced (too short).
from mathutils import Matrix
PREP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "models", "ruby", "pendant-prep.blend")
with bpy.data.libraries.load(os.path.abspath(PREP), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ("CENTRE", "PAVE", "METAL", "PAVE_BAIL", "METAL_BAIL")]
# model space (mm, bail at -Y, front at -Z) -> scene (cm, face up, bail at +Y, centre stone at the origin)
XF = Matrix.Translation((0, 0.86, 0.88)) @ Matrix.Scale(0.1, 4) @ Matrix.Rotation(math.pi, 4, "X")
for o in dst.objects:
    grp, m = {"CENTRE": (DIAG, DIA), "PAVE": (HALO, RUBY), "METAL": (HALO, ROSE), "PAVE_BAIL": (BAIL, RUBY), "METAL_BAIL": (BAIL, ROSE)}[o.name]
    o.data.transform(XF); o.matrix_world = Matrix(); o.parent = grp; link(o)
    o.data.materials.clear(); o.data.materials.append(m)
    metal = m is ROSE
    for poly in o.data.polygons: poly.use_smooth = metal
    if metal:
        o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(35)
BY, BZ = 1.76, -0.92   # where the chain passes through the bail (scene space)

# cable chain: a 2-link unit arrayed and deformed along a U path through the bail
L, LR, PITCH = 15.0, 0.016, 0.15
bpy.ops.mesh.primitive_torus_add(major_radius=0.058, minor_radius=LR, major_segments=24, minor_segments=8)
l1 = bpy.context.object; l1.scale = (1.55, 1, 1); bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.duplicate(); l2 = bpy.context.object; l2.rotation_euler = (math.pi / 2, 0, 0); l2.location.x = PITCH
bpy.ops.object.transform_apply(location=True, rotation=True)
l1.select_set(True); l2.select_set(True); bpy.context.view_layer.objects.active = l1; bpy.ops.object.join()
link_o = bpy.context.object; link_o.name = "Chain"; link_o.data.materials.append(ROSE); bpy.ops.object.shade_smooth()
arr = link_o.modifiers.new("Arr", "ARRAY"); arr.use_relative_offset = False; arr.use_constant_offset = True
arr.constant_offset_displace = (2 * PITCH, 0, 0); arr.count = int(L / (2 * PITCH)) + 12
path = bpy.data.curves.new("chain_path", "CURVE"); path.dimensions = "3D"; sp = path.splines.new("BEZIER")
P = [(-2.6, 11.0, -1.55), (-1.05, 3.8, -1.2), (-0.36, BY + 0.2, BZ - 0.03), (0, BY, BZ), (0.36, BY + 0.2, BZ - 0.03), (1.05, 3.8, -1.2), (2.6, 11.0, -1.55)]  # a V running back into the set
sp.bezier_points.add(len(P) - 1)
for bp, p in zip(sp.bezier_points, P): bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
path_o = bpy.data.objects.new("ChainPath", path); path_o.parent = CHAIN; link(path_o)
link_o.parent = path_o; link(link_o); link_o.location = (-0.6, 0, 0)
cm = link_o.modifiers.new("Follow", "CURVE"); cm.object = path_o; cm.deform_axis = "POS_X"
# the path's own length ~ 2 x 9.3 cm; links start at path start (local x 0)

# ---------------- set: black void, matte floor, the spot pool ----------------
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, CFG["floor_z"])); fl = bpy.context.object; fl.name = "Floor"
fl.data.materials.append(FLOOR); link(fl, "SET")
W = bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True; wn = W.node_tree
# hidden "reflection world": black to the camera and to diffuse light, a soft studio dome (bright top, two pale bands)
# only in glossy and transmission rays, so metal and gems have something bright to mirror and refract
bg_black = wn.nodes["Background"]; bg_black.inputs[1].default_value = 0.0
bg_ref = wn.nodes.new("ShaderNodeBackground"); grad = wn.nodes.new("ShaderNodeValToRGB"); sep = wn.nodes.new("ShaderNodeSeparateXYZ")
tc = wn.nodes.new("ShaderNodeTexCoord"); wn.links.new(tc.outputs["Generated"], sep.inputs[0])
cr = grad.color_ramp; cr.elements[0].position = 0.0; cr.elements[0].color = (0.0, 0.0, 0.0, 1)
cr.elements[1].position = 0.97; cr.elements[1].color = (1.4, 1.38, 1.35, 1)
for pos, v in ((0.30, 0.0), (0.42, 0.55), (0.52, 0.02), (0.70, 0.03), (0.78, 0.9), (0.86, 0.05)):
    e = cr.elements.new(pos); e.color = (v, v, v * 1.02, 1)
wn.links.new(sep.outputs["Z"], grad.inputs[0]); wn.links.new(grad.outputs[0], bg_ref.inputs[0]); bg_ref.inputs[1].default_value = 1.0
lp = wn.nodes.new("ShaderNodeLightPath"); mx = wn.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
wn.links.new(lp.outputs["Is Glossy Ray"], mx.inputs[0]); wn.links.new(lp.outputs["Is Transmission Ray"], mx.inputs[1])
mixw = wn.nodes.new("ShaderNodeMixShader"); wn.links.new(mx.outputs[0], mixw.inputs[0])
wn.links.new(bg_black.outputs[0], mixw.inputs[1]); wn.links.new(bg_ref.outputs[0], mixw.inputs[2])
wn.links.new(mixw.outputs[0], wn.nodes["World Output"].inputs[0])

def add_light(name, kind, loc, look, energy, col, size=0.5, coll_link=None, **kw):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = col
    if kind == "AREA": ld.shape = kw.get("shape", "RECTANGLE"); ld.size = size; ld.size_y = kw.get("size_y", size)
    if kind == "SPOT": ld.spot_size = kw["spot"]; ld.spot_blend = kw.get("blend", 0.5); ld.shadow_soft_size = size
    o = bpy.data.objects.new(name, ld); o.location = loc
    d = Vector(look) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); link(o, "SET")
    if coll_link: o.light_linking.receiver_collection = COLL[coll_link]
    return o

# the pool: one overhead spot, slightly off-axis so the hard shadow falls lower-left of the piece; it lights the floor only
SPOT = add_light("LGT_Spot_Pool", "SPOT", (2.0, -3.5, 26), (0, 0, CFG["floor_z"]), 5.0e4, C["pool"], size=0.35,
                 spot=math.radians(17), blend=0.7, coll_link="SET")
# product lights (linked to the product only): warm overhead softbox, grazing strips, a kick from behind, tiny sparkle lights
add_light("LGT_Key", "AREA", (1.5, -5.0, 14), (0, 0, 0), 2200, C["key"], 7.0, "PRODUCT", size_y=3.0)
add_light("LGT_Strip_L", "AREA", (-9, 2, 3), (0, 0, 0), 900, (1, 1, 1), 0.4, "PRODUCT", size_y=8.0)
add_light("LGT_Strip_R", "AREA", (9, 3, 2.5), (0, 0, 0), 700, (1, 1, 1), 0.4, "PRODUCT", size_y=8.0)
add_light("LGT_Kick_Back", "AREA", (0, 10, 4), (0, 0, 0), 600, C["pool"], 6.0, "PRODUCT", size_y=0.5)
SPARK = [add_light(f"LGT_Spark{i}", "AREA", p, (0, 0, 0), e, (1, 1, 1), 0.25, "PRODUCT")
         for i, (p, e) in enumerate((((-4, -6, 9), 260), ((5, -3, 10), 220), ((-1, 6, 11), 180)))]
# fill without a rectangle in the metal
fill = add_light("LGT_Fill", "AREA", (0, -14, 6), (0, 0, 0), 250, (0.9, 0.95, 1.0), 12.0, "PRODUCT")
fill.visible_glossy = False

# ---------------- animation ----------------
def keyv(o, path, frames_vals, interp="BEZIER", easing="AUTO"):
    for f, v in frames_vals:
        setattr(o, path, v); o.keyframe_insert(path, frame=f)
    for fc in o.animation_data.action.fcurves:
        if fc.data_path == path:
            for kp in fc.keyframe_points: kp.interpolation = interp; kp.easing = easing

E0, E1 = CFG["explode"]; H = CFG["hold_end"]
for name, grp in (("dia", DIAG), ("halo", HALO), ("bail", BAIL), ("chain", CHAIN)):
    ap = Vector(CFG["apart"][name]); l0, l1 = CFG["land"][name]
    keyv(grp, "location", [(1, Vector()), (E0, Vector())], "LINEAR")
    keyv(grp, "location", [(E1, ap), (l0, ap * 1.06)], "LINEAR")
    # explode: expo ease-out out of the assembled pose
    for fc in grp.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if kp.co.x == E0: kp.interpolation = "EXPO"; kp.easing = "EASE_OUT"
    keyv(grp, "location", [(l1, Vector())], "LINEAR")
    for fc in grp.animation_data.action.fcurves:   # land: accelerate into the seat (drop), then still
        for kp in fc.keyframe_points:
            if kp.co.x == l0: kp.interpolation = "QUAD"; kp.easing = "EASE_IN"
# small tumble on the flying parts
keyv(BAIL, "rotation_euler", [(E0, Euler()), (E1, Euler((math.radians(28), 0, 0))), (217, Euler((math.radians(30), 0, 0))), (226, Euler())], "LINEAR")
keyv(DIAG, "rotation_euler", [(E0, Euler()), (E1, Euler((0.12, -0.1, 0.3))), (199, Euler((0.13, -0.11, 0.33))), (208, Euler())], "LINEAR")
# the chain threads through the bail as it comes home
keyv(link_o, "location", [(1, Vector((-0.6, 0, 0))), (235, Vector((-1.4, 0, 0))), (247, Vector((-0.6, 0, 0)))], "LINEAR")
# hero sway
keyv(ROOT, "rotation_euler", [(253, Euler((0, 0, 0))), (300, Euler((0.04, -0.05, 0.06))), (360, Euler((0.0, -0.02, 0.1)))], "BEZIER")
# glints: sparkle lights spike on the beats -> star glare
for f in CFG["glints"]:
    for s_ in SPARK[:1]:
        ld = s_.data
        for ff, e in ((f - 6, 260), (f, 2600), (f + 7, 260)):
            ld.energy = e; ld.keyframe_insert("energy", frame=ff)

# cameras (bound to timeline markers = cuts)
for name, f0, (p0, p1), (t0, t1), lens, fstop, interp in CFG["cams"]:
    nxt = [c[1] for c in CFG["cams"] if c[1] > f0]; f1 = (min(nxt) - 1) if nxt else CFG["frames"]
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_start = 0.05; cd.clip_end = 2000
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(name, cd); link(cam, "SET")
    tgt = empty(f"T_{name}"); tr = cam.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    cd.dof.focus_object = tgt
    keyv(cam, "location", [(f0, Vector(p0)), (f1, Vector(p1))], interp, "EASE_OUT")
    keyv(tgt, "location", [(f0, Vector(t0)), (f1, Vector(t1))], interp, "EASE_OUT")
    m = S.timeline_markers.new(f"cut_{name}", frame=f0); m.camera = cam
    if name == "MAC":   # rack focus: from soft to sharp on the table
        keyv(tgt, "location", [(f0, Vector((0, 0, 1.05))), (f0 + 22, Vector(t0)), (f1, Vector(t1))], "BEZIER")
S.camera = bpy.data.objects["MAC"]

# ---------------- render ----------------
S.render.engine = "CYCLES"; cy = S.cycles
cy.device = "CPU"; cy.samples = 64; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.03; cy.use_denoising = False
cy.max_bounces = 16; cy.transmission_bounces = 12; cy.glossy_bounces = 6; cy.diffuse_bounces = 2; cy.transparent_max_bounces = 8
cy.volume_bounces = 1; cy.sample_clamp_indirect = 5.0; cy.caustics_reflective = False; cy.caustics_refractive = False
try: cy.use_light_tree = True
except AttributeError: pass
S.render.use_motion_blur = True; S.render.motion_blur_shutter = 0.35
S.render.resolution_x, S.render.resolution_y = CFG["res"]; S.render.resolution_percentage = 100
S.view_settings.view_transform = "AgX"
try: S.view_settings.look = "AgX - Medium High Contrast"
except TypeError: pass
S.view_settings.exposure = -0.3
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); gl = ct.nodes.new("CompositorNodeGlare"); co = ct.nodes.new("CompositorNodeComposite")
gl.glare_type = "STREAKS"; gl.streaks = 4; gl.angle_offset = math.radians(22); gl.fade = 0.88; gl.threshold = 2.2; gl.mix = -0.55; gl.quality = "HIGH"
ct.links.new(rl.outputs["Image"], gl.inputs["Image"]); ct.links.new(gl.outputs["Image"], co.inputs["Image"])
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT))
print("saved", OUT)
