# MUTANT-style moving cover (grammar only): chrome female head, violet liquid-chrome spikes and webbed
# membranes grow out of the skin, holes tear open in the webs, slow push-in while the chin lifts.
# Transparent background: the lime field and all type are composited in Remotion (src/mutant/).
# Head: "Female Head Realistic" by recofiv3 (Sketchfab, CC-BY 4.0, via Objaverse). Credit in public/models/CREDITS.md.
# Run: PYTHONPATH=tools/py312 blender -b --factory-startup -P work/mutant/mutant.py -- [still F F F] [half]
import bpy, sys, math, os
import numpy as np
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

ROOT = "/home/user/Motion-Studio/work/mutant/"
OUT = os.environ.get("MUT_OUT", ROOT + "frames/")
FPS, NF, RES = 24, 258, (1920, 1080)   # 3D runs to f258; the logo end card after it is pure Remotion
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

VIOLET = (0.34, 0.06, 1.0)
SILVER = (0.86, 0.86, 0.9)
LIME = (0.55, 0.92, 0.04)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.fps = FPS; S.frame_start = 1; S.frame_end = NF

def key(o, path, fr, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)

def drv(sock, expr):
    d = sock.driver_add("default_value").driver; d.type = 'SCRIPTED'; d.expression = expr

# ---------------------------------------------------------------- head
bpy.ops.import_scene.gltf(filepath=ROOT + "heads/e97fb74847454a269c4fbfba077aae2a.glb")
ms = [o for o in S.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
head = bpy.context.view_layer.objects.active; head.name = "SM_Head"
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(S.objects):
    if o != head: bpy.data.objects.remove(o)
co = np.empty(len(head.data.vertices) * 3); head.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
lo, hi = co.min(0), co.max(0); sc = 1.0 / (hi[2] - lo[2])
co = (co - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]) * sc     # height 1, neck base at z=0, face looks to -Y
lowz = co[:, 2] < 0.14                                                    # stretch the neck so its cut end sits below frame
co[lowz, 2] = 0.14 - (0.14 - co[lowz, 2]) * 2.5
head.data.vertices.foreach_set("co", co.ravel()); head.data.update()
import bmesh as _bm
_b = _bm.new(); _b.from_mesh(head.data); _nv = len(_b.verts)
_bm.ops.remove_doubles(_b, verts=_b.verts, dist=1e-5); print("MERGED", _nv, "->", len(_b.verts))
_b.to_mesh(head.data); _b.free()
head.data.polygons.foreach_set("use_smooth", [True] * len(head.data.polygons))
bpy.context.view_layer.objects.active = head
if head.data.has_custom_normals: bpy.ops.mesh.customdata_custom_splitnormals_clear()   # imported normals go stale after reshaping
head.data.materials.clear()
bvh = BVHTree.FromObject(head, bpy.context.evaluated_depsgraph_get())

RIG = bpy.data.objects.new("HEAD_RIG", None); S.collection.objects.link(RIG); RIG.location = (0, 0, 0.15)
head.parent = RIG; head.location = (0, 0, -0.15)
key(RIG, "rotation_euler", 1, (math.radians(-24), 0, math.radians(-16)))
key(RIG, "rotation_euler", 148, (math.radians(-30), 0, math.radians(-6)))
key(RIG, "rotation_euler", 205, (math.radians(-44), math.radians(-7), math.radians(4)))   # end: chin thrown right back, like the reference
key(RIG, "rotation_euler", NF, (math.radians(-46), math.radians(-8), math.radians(5)))

# ---------------------------------------------------------------- materials
def nodes_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]

m_head, nt, b = nodes_mat("MAT_ChromeSkin")
b.inputs["Base Color"].default_value = (0.6, 0.6, 0.64, 1); b.inputs["Metallic"].default_value = 1.0
b.inputs["Roughness"].default_value = 0.21
b.inputs["Coat Weight"].default_value = 0.6; b.inputs["Coat Roughness"].default_value = 0.04
head.data.materials.append(m_head)

def violet_chrome(name, holes):
    m, nt, b = nodes_mat(name); N, L = nt.nodes, nt.links
    b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.07
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.42
    ramp = N.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.elements[0].position = 0.1; cr.elements[0].color = (0.4, 0.04, 1.0, 1)
    cr.elements[1].position = 0.7; cr.elements[1].color = (*SILVER, 1)
    L.new(lw.outputs["Facing"], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Emission Color"].default_value = (*VIOLET, 1); b.inputs["Emission Strength"].default_value = 0.14
    if holes:
        # round holes tear open inside the webs (never on the rims): Voronoi F1 < radius * interior mask
        tc = N.new("ShaderNodeTexCoord"); vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 9.0
        L.new(tc.outputs["Object"], vo.inputs["Vector"])
        uv = N.new("ShaderNodeUVMap"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(uv.outputs["UV"], sp.inputs[0])
        def m_(op, a, bb=None):
            n = N.new("ShaderNodeMath"); n.operation = op
            for i, v in enumerate((a, bb)):
                if v is None: continue
                if isinstance(v, (int, float)): n.inputs[i].default_value = v
                else: L.new(v, n.inputs[i])
            return n.outputs[0]
        mask = m_('MULTIPLY', m_('SINE', m_('MULTIPLY', sp.outputs["X"], math.pi)), m_('SINE', m_('MULTIPLY', sp.outputs["Y"], math.pi * 0.95)))
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.12; mr.inputs["From Max"].default_value = 0.5
        L.new(mask, mr.inputs["Value"])
        R = N.new("ShaderNodeValue"); drv(R.outputs[0], "min(1,max(0,(frame-100)/80))*0.34")
        thr = m_('MULTIPLY', mr.outputs["Result"], R.outputs[0])
        alpha = m_('GREATER_THAN', vo.outputs["Distance"], thr)
        L.new(alpha, b.inputs["Alpha"])
        m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
    return m

m_web = violet_chrome("MAT_VioletWeb", True)
m_spike = violet_chrome("MAT_VioletSpike", False)

# ---------------------------------------------------------------- spikes + webs (rebuilt every frame)
def anchor(az, el, ctr):
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    loc, nor, _, _ = bvh.ray_cast(Vector(ctr) + d * 2.0, -d)
    if loc is None: raise RuntimeError(f"no hit {az},{el}")
    if nor.dot(d) < 0: nor = -nor
    return np.array(loc), np.array(nor)

HEADC, NECKC = (0, 0.02, 0.62), (0, 0.06, 0.24)
# Bands of web drape over the skin (adjacent anchors), spikes run along the skin and then curl off.
# (cluster, azimuth, elevation, centre, length, outward sweep, base radius, start frame)
SPEC = [
    # A: diagonal band from the left forehead, over the right eye, down the right cheek to the jaw
    ("A", 34, 52, HEADC, 0.62, (0.5, 0.1, 1), 0.020, 40), ("A", 6, 34, HEADC, 0.55, (0.2, -0.3, 1), 0.019, 14),
    ("A", -18, 14, HEADC, 0.68, (-1, -0.3, 0.55), 0.021, 4), ("A", -38, -6, HEADC, 0.72, (-1, -0.35, 0.05), 0.022, 34),
    ("A", -52, -30, HEADC, 0.60, (-0.9, -0.2, -0.6), 0.020, 46),
    # B: crown
    ("B", -40, 70, HEADC, 0.55, (-0.7, 0.2, 1), 0.018, 66), ("B", 10, 80, HEADC, 0.62, (0.1, 0.3, 1), 0.019, 72),
    ("B", 70, 58, HEADC, 0.5, (1, 0.3, 0.7), 0.018, 80),
    # C: left ear, down the neck, across the throat
    ("C", 72, 18, HEADC, 0.6, (1, 0.1, 0.4), 0.019, 96), ("C", 80, -12, HEADC, 0.66, (1, 0.2, -0.2), 0.020, 104),
    ("C", 55, 20, NECKC, 0.62, (1, -0.1, -0.8), 0.020, 110), ("C", 15, 8, NECKC, 0.6, (0.35, -0.3, -1), 0.021, 116),
    ("C", -30, 6, NECKC, 0.58, (-0.8, -0.25, -0.8), 0.019, 124),
]
SP = []
for i, (cl, az, el, ctr, Ln, sw, r0, t0) in enumerate(SPEC):
    A, n = anchor(az, el, ctr); w = np.array(sw, float); w /= np.linalg.norm(w)
    tdir = w - n * w.dot(n); tdir /= np.linalg.norm(tdir); bdir = np.cross(n, tdir)
    SP.append(dict(cl=cl, A=A, n=n, t=tdir, b=bdir, L=Ln, r0=r0, t0=t0, seed=i * 7.31, curl=((i * 37) % 7 - 3) / 3))
WEBS = [(i, i + 1) for i in range(len(SP) - 1) if SP[i]["cl"] == SP[i + 1]["cl"]]

NS, NR, NU, NW = 30, 10, 20, 26        # spike samples, ring verts, web columns, web rows
GROW = 48                              # frames for one spike to reach full length

def growth(sp, f):
    x = min(1.0, max(0.0, (f - sp["t0"]) / GROW))
    return 1 - (1 - x) ** 3

def centre(sp, s, f):
    """Spike centreline at parameters s (array), with a slow liquid wobble."""
    # starts tangent to the skin, lifts off with s^2, and curls sideways like a liquid tendril
    P = sp["A"] + sp["L"] * (np.outer(s, sp["t"]) + np.outer(0.62 * s ** 2.2 + 0.03 * s, sp["n"])
                             + np.outer(0.16 * sp["curl"] * np.sin(np.pi * s), sp["b"]))
    t = f / FPS
    wob = np.array([[noise.noise(Vector((sp["seed"] + k, t * 0.45, si * 1.7))) for k in range(3)] for si in s])
    return P + wob * (0.035 * s)[:, None]

def hug(P, off):
    """Keep points outside the skin: anything closer than `off` is pushed out along the surface normal."""
    out = P.copy()
    for k, p in enumerate(P):
        loc, nor, _, _ = bvh.find_nearest(Vector(p))
        if loc is None: continue
        d = Vector(p) - loc
        if d.dot(nor) < off: out[k] = np.array(loc + nor * off)
    return out

def tube(P, radii, verts, faces):
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
    ref = np.array([0, 0, 1.0]) if abs(T[0][2]) < 0.9 else np.array([1.0, 0, 0])
    base = len(verts); ang = np.linspace(0, 2 * math.pi, NR, endpoint=False)
    for k in range(len(P)):
        u = np.cross(T[k], ref); u /= np.linalg.norm(u) + 1e-9; v = np.cross(T[k], u)
        for a in ang: verts.append(P[k] + radii[k] * (math.cos(a) * u + math.sin(a) * v))
    for k in range(len(P) - 1):
        for j in range(NR):
            a, b2 = base + k * NR + j, base + k * NR + (j + 1) % NR
            faces.append((a, b2, b2 + NR, a + NR))
    tip = len(verts); verts.append(P[-1] + (P[-1] - P[-2]) * 0.5)
    last = base + (len(P) - 1) * NR
    for j in range(NR): faces.append((last + j, last + (j + 1) % NR, tip))

def set_mesh(me, verts, faces, uvs=None):
    me.clear_geometry(); me.from_pydata([tuple(v) for v in verts], [], faces)
    if uvs is not None:
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", np.array([uvs[vi] for p in me.polygons for vi in p.vertices], float).ravel())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.update()

def build(scene, *_):
    f = scene.frame_current_final
    sv, sf, wv, wf, wuv = [], [], [], [], []
    G = [growth(sp, f) for sp in SP]
    curves = []
    for sp, g in zip(SP, G):
        srel = np.linspace(0, 1, NS); s = srel * max(g, 0.002)
        P = centre(sp, s, f); curves.append(P)
        r = sp["r0"] * (1 - srel) ** 1.4 * (0.4 + 0.6 * g) + 0.03 * np.exp(-srel * 9) * min(1, g * 3)
        tube(P, r, sv, sf)
    for (i, j) in WEBS:
        a, b2 = SP[i], SP[j]; gi, gj = G[i], G[j]
        u = np.linspace(0, 1, NU); srow = np.linspace(0, 1, NW)
        base = len(wv); rim = []
        for si in srow:
            e = 1 - 0.52 * np.sin(np.pi * u) ** 0.9                    # scalloped free edge between the tips
            Pi = centre(a, si * e * max(gi, 0.002), f); Pj = centre(b2, si * e * max(gj, 0.002), f)
            nav = (a["n"] + b2["n"]); nav /= np.linalg.norm(nav)
            row = (1 - u)[:, None] * Pi + u[:, None] * Pj + np.outer(0.03 * np.sin(np.pi * u) * np.sin(np.pi * si), nav)
            row = hug(row, 0.012)
            for k in range(NU): wv.append(row[k]); wuv.append((u[k], si))
            if si == 1.0: rim = row
        for r_ in range(NW - 1):
            for k in range(NU - 1):
                p0 = base + r_ * NU + k; wf.append((p0, p0 + 1, p0 + NU + 1, p0 + NU))
        # thick liquid rim along the free edge (tapers into the spikes)
        tube(np.array(rim), 0.0065 * np.sin(np.pi * u) ** 0.35 * min(1, min(gi, gj) * 2) + 0.0005, sv, sf)
    set_mesh(SPIKES.data, sv, sf); set_mesh(WEB.data, wv, wf, wuv)

def mk(name, mat):
    me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); S.collection.objects.link(o)
    o.parent = RIG; o.location = (0, 0, -0.15); me.materials.append(mat); return o
SPIKES = mk("SM_Spikes", m_spike); WEB = mk("SM_Webs", m_web)
so = WEB.modifiers.new("Thick", 'SOLIDIFY'); so.thickness = 0.006; so.offset = 0
for o in (SPIKES, WEB):
    ss = o.modifiers.new("Smooth", 'SUBSURF'); ss.levels = 1; ss.render_levels = 1
bpy.app.handlers.frame_change_pre.append(build)

# ---------------------------------------------------------------- world: studio reflections only (film is transparent)
W = bpy.data.worlds.new("World"); S.world = W; W.use_nodes = True; wt = W.node_tree; WN, WL = wt.nodes, wt.links
bg = WN["Background"]; tc = WN.new("ShaderNodeTexCoord")
def wsum(prev, col, w):
    sc_ = WN.new("ShaderNodeVectorMath"); sc_.operation = 'SCALE'; sc_.inputs[0].default_value = col
    WL.new(w, sc_.inputs["Scale"])
    if prev is None: return sc_.outputs[0]
    ad = WN.new("ShaderNodeVectorMath"); ad.operation = 'ADD'; WL.new(prev, ad.inputs[0]); WL.new(sc_.outputs[0], ad.inputs[1])
    return ad.outputs[0]
def lobe(dirv, lo_, hi_, gain):
    nd = WN.new("ShaderNodeVectorMath"); nd.operation = 'NORMALIZE'; WL.new(tc.outputs["Generated"], nd.inputs[0])
    dt = WN.new("ShaderNodeVectorMath"); dt.operation = 'DOT_PRODUCT'; WL.new(nd.outputs[0], dt.inputs[0])
    v = Vector(dirv).normalized(); dt.inputs[1].default_value = v
    mr = WN.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = lo_; mr.inputs["From Max"].default_value = hi_
    mr.inputs["To Max"].default_value = gain; WL.new(dt.outputs["Value"], mr.inputs["Value"]); return mr.outputs["Result"]
one = WN.new("ShaderNodeValue"); one.outputs[0].default_value = 1.0
acc = wsum(None, (0.025, 0.025, 0.03), one.outputs[0])                       # dark studio
acc = wsum(acc, (1, 1, 1), lobe((-0.55, -0.6, 0.6), 0.82, 0.95, 9.0))         # key softbox, front-left-up
acc = wsum(acc, (1, 1, 1), lobe((1, -0.15, 0.15), 0.9, 0.97, 5.0))            # tall strip, right
acc = wsum(acc, (0.9, 0.95, 1), lobe((0, 0.2, 1), 0.6, 1.0, 1.2))            # soft top
acc = wsum(acc, LIME, lobe((0, -0.3, -1), 0.2, 0.7, 2.6))                   # lime bounce from below (the field)
acc = wsum(acc, VIOLET, lobe((-1, 0.35, -0.1), 0.7, 0.92, 3.5))              # violet card, left
WL.new(acc, bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0

def area(name, loc, energy, size, col):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = col
    ld.shadow_buffer_bias = 0.25   # no stepped shadow edges on the head's coarser triangles
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
area("L_Key", (-2.2, -2.6, 2.4), 350, 1.6, (1, 1, 1))
area("L_Rim", (2.0, 1.8, 1.6), 450, 1.0, (0.75, 0.55, 1.0))
area("L_Under", (0.3, -2.0, -0.8), 120, 1.5, LIME)

# ---------------------------------------------------------------- cameras
# 0-6.2 s: close-ups that ride the tips of growing spikes (cameras live in the head rig, keyed from the real
# spike curves, so they follow the tip). 6.2-10 s: pull back to the reference's low angle under the chin.
def rig_local(p): return Vector(tuple(p)) - Vector((0, 0, 0.15))
def make_cam(name, lens, fstop, parent=None):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); S.collection.objects.link(c)
    c.data.lens = lens; c.data.clip_start = 0.005
    t = bpy.data.objects.new(name + "_T", None); S.collection.objects.link(t)
    if parent: c.parent = parent; t.parent = parent
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    if fstop: c.data.dof.use_dof = True; c.data.dof.focus_object = t; c.data.dof.aperture_fstop = fstop
    return c, t
def follow(name, f0, f1, k, lens, D, side, fstop=4.0):
    """Hovers about half a head off the skin beside the spike's root, looking at the middle of the growing spike,
    so the chrome skin fills the frame behind it and the tip shoots across; drifts outward as it grows."""
    c, t = make_cam(name, lens, fstop, RIG); sp = SP[k]
    frs = list(range(f0, f1, 6)) + [f1]
    for fr in frs:
        g = growth(sp, fr); u = (fr - f0) / max(1, f1 - f0)
        mid = centre(sp, np.array([max(g, 0.06) * 0.5]), fr)[0]
        pos = sp["A"] + sp["n"] * D + sp["b"] * side + sp["t"] * sp["L"] * (0.05 + 0.3 * u)
        key(t, "location", fr, rig_local(mid)); key(c, "location", fr, rig_local(pos))
    S.timeline_markers.new(name, frame=f0).camera = c
follow("CAM_Eye", 1, 36, 2, 45, 0.42, 0.18)          # strand emerging over the eye
follow("CAM_Cheek", 37, 72, 3, 45, 0.45, -0.22)      # spike curling off the cheek
follow("CAM_Crown", 73, 108, 6, 40, 0.5, 0.25)       # crown spikes
follow("CAM_Neck", 109, 148, 11, 45, 0.45, 0.22)     # webs on the neck, holes tearing open
hero, ht = make_cam("CAM_Hero", 40, 9.0)
key(hero, "location", 149, (0.5, -0.75, 0.42)); key(ht, "location", 149, (0.05, 0.2, 0.6))
key(hero, "location", 205, (0.03, -1.2, 0.16)); key(ht, "location", 205, (0.0, 0.28, 0.68))
key(hero, "location", 222, (0.025, -1.23, 0.155)); key(ht, "location", 222, (0.0, 0.285, 0.68))
key(hero, "location", NF, (-0.04, -1.0, 0.14)); key(ht, "location", NF, (-0.06, 0.27, 0.69))   # text glitches out: push in, head central
S.timeline_markers.new("CAM_Hero", frame=149).camera = hero
# end shot (cut hidden in the type glitch-out): straight on to the face, head centred, slow push. Lives in the head rig so it
# stays square to the face whatever the pose.
endc, endt = make_cam("CAM_End", 50, 8.0, RIG)
key(endc, "location", 226, rig_local((0, -3.1, 0.55))); key(endt, "location", 226, rig_local((0, 0, 0.55)))
key(endc, "location", 249, rig_local((0, -2.9, 0.55))); key(endt, "location", 249, rig_local((0, 0, 0.55)))
key(endc, "location", NF, rig_local((0, -4.8, 0.6))); key(endt, "location", NF, rig_local((0, 0, 0.6)))   # pulls back during the B/W flicker: whole form centred
S.timeline_markers.new("CAM_End", frame=226).camera = endc
S.camera = bpy.data.objects["CAM_Eye"]

# ---------------------------------------------------------------- render
S.render.engine = 'BLENDER_EEVEE'; e = S.eevee
e.taa_render_samples = 32; e.use_ssr = True; e.use_gtao = True; e.gtao_distance = 0.2
e.use_motion_blur = True; e.motion_blur_shutter = 0.45; e.use_soft_shadows = True
e.gi_cubemap_resolution = '1024'; e.use_bloom = False
S.render.film_transparent = True; S.render.use_lock_interface = True
S.render.resolution_x, S.render.resolution_y = RES; S.render.resolution_percentage = 50 if "half" in args else 100
for vt, lk in (("AgX", "AgX - Punchy"), ("AgX", "Punchy"), ("Filmic", "High Contrast")):
    try: S.view_settings.view_transform = vt; S.view_settings.look = lk; break
    except TypeError: continue
if os.environ.get("NO_OVERWRITE"): S.render.use_overwrite = False; S.render.use_placeholder = False
S.render.image_settings.file_format = 'PNG'; S.render.image_settings.color_mode = 'RGBA'
os.makedirs(OUT, exist_ok=True)
if args and args[0] == "still":
    for fr in [int(a) for a in args[1:] if a.isdigit()]:
        S.frame_set(fr); S.camera = [mk for mk in sorted(S.timeline_markers, key=lambda mk: mk.frame) if mk.frame <= fr][-1].camera
        S.render.filepath = OUT + f"still_{fr:03d}.png"; bpy.ops.render.render(write_still=True)
else:
    S.render.filepath = OUT + "f_"; bpy.ops.render.render(animation=True)
print("DONE")
