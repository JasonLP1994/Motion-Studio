# Build the whole PaintedStatue animation as a Blender (Cycles) scene and save it.
# Usage: blender -b --factory-startup -P scripts/blender/build_anim.py -- <export dir> <out.blend> [preview|farm]
# <export dir> comes from: ENTRY=anim PT_OUT=<dir> node scripts/pathtrace/run.cjs anim 1 x.png ""
#   pieces.glb, chips.glb, anim.json, floor/m_####.png, rome_mask.png
# The .blend expects floor/ next to it (relative path //floor/), so ship them together as a folder/ZIP.
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix, Euler, Quaternion
from looks import b3, hexc, principled, noise, bump, blood_into, marble_into, mat_blood, mat_stone, area

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = os.path.abspath(argv[0]), os.path.abspath(argv[1])
MODE = argv[2] if len(argv) > 2 else "preview"
A = json.load(open(os.path.join(SRC, "anim.json")))
FR = A["frameData"]; N = A["frames"]; FPS = A["fps"]
outdir = os.path.dirname(OUT); os.makedirs(outdir, exist_ok=True)
# floor maps + mask travel with the .blend
if os.path.abspath(os.path.join(outdir, "floor")) != os.path.join(SRC, "floor"):
    shutil.copytree(os.path.join(SRC, "floor"), os.path.join(outdir, "floor"), dirs_exist_ok=True)

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, N; sc.render.fps = FPS

C3 = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))  # three.js basis -> Blender basis
def rot3(rx, ry, rz):  # three.js Euler 'XYZ' (M = Rx Ry Rz) -> Blender quaternion
    m = Euler((rx, ry, rz), "ZYX").to_matrix()
    return (C3 @ m @ C3.inverted()).to_quaternion()

def keys(id_data, path, values, index_count, interp="LINEAR"):
    """values: list (per frame) of tuples length index_count; writes fcurves fast."""
    ad = id_data.animation_data or id_data.animation_data_create()
    if not ad.action: ad.action = bpy.data.actions.new(f"{id_data.name}_act")
    for i in range(index_count):
        fc = ad.action.fcurves.find(path, index=i) or ad.action.fcurves.new(path, index=i)
        fc.keyframe_points.add(len(values))
        co = []
        for f, v in enumerate(values): co += [f + 1, v[i] if index_count > 1 else v]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points: kp.interpolation = interp
        fc.update()

# ---------- materials ----------
def time_value(nt):
    v = nt.nodes.new("ShaderNodeValue"); v.name = "time"
    d = v.outputs[0].driver_add("default_value").driver; d.type = "SCRIPTED"; d.expression = f"(frame - 1) / {FPS}"  # simple expression: no Python needed
    return v

def keyed_value(nt, name, series):
    v = nt.nodes.new("ShaderNodeValue"); v.name = name; v.outputs[0].default_value = series[0]
    keys(nt, f'nodes["{name}"].outputs[0].default_value', series, 1, "LINEAR"); return v

DUST = [fd["dust"] for fd in FR]
def add_dissolve(m):
    # scene 3: the wind dissolves rubble left to right (same rule as the video: world x vs dust progress, per-cell noise)
    nt = m.node_tree; out = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")
    surf = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry"); snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = "SNAP"; snap.inputs[1].default_value = (1 / 420,) * 3
    nt.links.new(geo.outputs["Position"], snap.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; nt.links.new(snap.outputs[0], wn.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])
    # lhs = x*0.4 + 0.5 + (h-0.5)*0.35 ; rhs = dust*1.5 - 0.25 ; transparent where lhs < rhs
    def math(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate([a, b]):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    lhs = math("ADD", math("MULTIPLY_ADD" if False else "MULTIPLY", sep.outputs["X"], 0.4), math("ADD", math("MULTIPLY", math("SUBTRACT", wn.outputs["Value"], 0.5), 0.35), 0.5))
    dv = keyed_value(nt, "dust", DUST)
    rhs = math("SUBTRACT", math("MULTIPLY", dv.outputs[0], 1.5), 0.25)
    gone = math("MULTIPLY", math("LESS_THAN", lhs, rhs), math("GREATER_THAN", dv.outputs[0], 0.0))
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gone, mix.inputs[0]); nt.links.new(surf, mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])

def mat_statue():
    # marble skin that the blood sheet flows over: each vertex knows when the blood reaches it (paintT0 -> paintT1)
    m = bpy.data.materials.new("bl_statue"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bm = nt.nodes.new("ShaderNodeBsdfPrincipled"); marble_into(nt, bm, False)
    bb = nt.nodes.new("ShaderNodeBsdfPrincipled"); ripple = blood_into(nt, bb, False)
    a0 = nt.nodes.new("ShaderNodeAttribute"); a0.attribute_name = "_PAINTT0"; a1 = nt.nodes.new("ShaderNodeAttribute"); a1.attribute_name = "_PAINTT1"
    tv = time_value(nt)
    # mask = smoothstep(t0, t1, time) via (time - t0) / max(t1 - t0, 1e-3)
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; nt.links.new(tv.outputs[0], sub.inputs[0]); nt.links.new(a0.outputs["Fac"], sub.inputs[1])
    wd = nt.nodes.new("ShaderNodeMath"); wd.operation = "SUBTRACT"; nt.links.new(a1.outputs["Fac"], wd.inputs[0]); nt.links.new(a0.outputs["Fac"], wd.inputs[1])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; mx.inputs[1].default_value = 0.002; nt.links.new(wd.outputs[0], mx.inputs[0])
    dv = nt.nodes.new("ShaderNodeMath"); dv.operation = "DIVIDE"; nt.links.new(sub.outputs[0], dv.inputs[0]); nt.links.new(mx.outputs[0], dv.inputs[1])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type = "SMOOTHSTEP"; nt.links.new(dv.outputs[0], mr.inputs["Value"])
    mask = mr.outputs["Result"]
    # thin edge = bright crimson, full coat = near-black red
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = hexc("#9A0A10"); ramp.color_ramp.elements[1].color = hexc("#3A0206")
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 1.0
    nt.links.new(mask, ramp.inputs[0]); nt.links.new(ramp.outputs["Color"], bb.inputs["Base Color"])
    # a raised, rounded bead where the sheet ends (bump from the mask), on top of the blood's ripples
    bead = nt.nodes.new("ShaderNodeBump"); bead.inputs["Strength"].default_value = 0.5; bead.inputs["Distance"].default_value = 0.004
    nt.links.new(mask, bead.inputs["Height"]); nt.links.new(ripple.outputs[0], bead.inputs["Normal"]); nt.links.new(bead.outputs[0], bb.inputs["Normal"])
    gate = nt.nodes.new("ShaderNodeMath"); gate.operation = "GREATER_THAN"; gate.inputs[1].default_value = 0.02; nt.links.new(mask, gate.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(gate.outputs[0], mix.inputs[0])
    nt.links.new(bm.outputs[0], mix.inputs[1]); nt.links.new(bb.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    add_dissolve(m); return m

def mat_inside():
    m = bpy.data.materials.new("bl_inside"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); marble_into(nt, bs, True)
    nt.links.new(bs.outputs[0], out.inputs["Surface"]); add_dissolve(m); return m

M_STATUE, M_INSIDE = mat_statue(), mat_inside()
M_BLOOD = mat_blood("bl_bloodFlat", False); M_STONE = mat_stone("bl_stone")

# ---------- statue pieces: solid chunks (Solidify gives clean insides), keyed from the video's flight ----------
bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, "pieces.glb"))
names = ["stump"] + [f"piece_{i:02d}" for i in range(len(FR[0]["pieces"]))]
for nm in names:
    o = bpy.data.objects[nm]; o.parent = None
    o.data.materials.clear(); o.data.materials.append(M_STATUE); o.data.materials.append(M_INSIDE)
    sol = o.modifiers.new("solid", "SOLIDIFY"); sol.thickness = 0.045; sol.offset = -1.0; sol.use_rim = True; sol.material_offset = 1; sol.material_offset_rim = 1
    sol.use_even_offset = False; sol.use_quality_normals = True
    o.rotation_mode = "QUATERNION"
for o in [x for x in bpy.data.objects if x.type == "EMPTY"]: bpy.data.objects.remove(o)
for i, nm in enumerate(names[1:]):
    o = bpy.data.objects[nm]
    keys(o, "location", [tuple(b3(fd["pieces"][i][:3])) for fd in FR], 3)
    keys(o, "rotation_quaternion", [tuple(rot3(*fd["pieces"][i][3:6])) for fd in FR], 4)

# chips: tiny blood / marble shards
bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, "chips.glb"))
for o in [x for x in bpy.data.objects if x.type == "EMPTY"]: bpy.data.objects.remove(o)
chips = sorted([o for o in bpy.data.objects if o.name.startswith("chip_")], key=lambda o: o.name)
for i, o in enumerate(chips):
    blood = o.material_slots[0].material and o.material_slots[0].material.name.startswith("chipBlood")
    o.data.materials.clear(); o.data.materials.append(M_BLOOD if blood else M_INSIDE); o.parent = None; o.rotation_mode = "QUATERNION"
    keys(o, "location", [tuple(b3(fd["chips"][i][:3])) for fd in FR], 3)
    keys(o, "rotation_quaternion", [tuple(rot3(fd["chips"][i][3], fd["chips"][i][4], 0)) for fd in FR], 4)
    keys(o, "scale", [(fd["chips"][i][5],) * 3 for fd in FR], 3, "CONSTANT")

# ---------- floor: infinite stone, the liquid map per frame, ROME carved at the cut and filled ----------
mp = A["map"]; cx, cz = A["rome"]["centre"]; w = A["rome"]["width"]; h = w * 0.3125
import bmesh
def quad_floor(name, holes):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); B = 30.0
    x0, x1, y0, y1 = holes
    V = [bm.verts.new(p) for p in [(-B, -B, 0), (B, -B, 0), (B, B, 0), (-B, B, 0), (x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]]
    for qd in [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]: bm.faces.new([V[i] for i in qd])
    bm.to_mesh(me); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(M_STONE); return o
hole = (cx - w / 2, cx + w / 2, -cz - h / 2, -cz + h / 2)
quad_floor("floor", hole)
img = bpy.data.images.load(os.path.join(SRC, "rome_mask.png")); img.colorspace_settings.name = "Non-Color"
# before the cut: a plain patch; from the cut (frame of carveFrom): the carved grid
bpy.ops.mesh.primitive_plane_add(size=1); patch = bpy.context.object; patch.name = "floorPatch"; patch.scale = (w, h, 1); patch.location = (cx, -cz, 0); patch.data.materials.append(M_STONE)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=1400, y_subdivisions=440, size=1, calc_uvs=True)
carve = bpy.context.object; carve.name = "carving"; carve.scale = (w, h, 1); carve.location = (cx, -cz, 0); bpy.ops.object.transform_apply(scale=True)
tex = bpy.data.textures.new("romeMask", "IMAGE"); tex.image = img; tex.extension = "CLIP"
d = carve.modifiers.new("carve", "DISPLACE"); d.texture = tex; d.texture_coords = "UV"; d.strength = -0.022; d.mid_level = 0.0
carve.data.materials.append(M_STONE); bpy.ops.object.shade_smooth()
CARVE = [fd["carve"] for fd in FR]
for o, vis in ((patch, [0 if c else 1 for c in CARVE]), (carve, CARVE)):
    keys(o, "hide_render", [not v for v in vis], 1, "CONSTANT"); keys(o, "hide_viewport", [not v for v in vis], 1, "CONSTANT")

# the liquid on the floor: pool + splats + rivulets from the per-frame map (alpha), rounded edge (bump)
bpy.ops.mesh.primitive_plane_add(size=1, calc_uvs=True)
pool = bpy.context.object; pool.name = "poolLiquid"
pool.scale = (mp["x1"] - mp["x0"], mp["z1"] - mp["z0"], 1); pool.location = ((mp["x0"] + mp["x1"]) / 2, -(mp["z0"] + mp["z1"]) / 2, 0.0012); bpy.ops.object.transform_apply(scale=True)
pm = mat_blood("bl_pool", False); nt = pm.node_tree; bs = nt.nodes["Principled BSDF"]
seq = bpy.data.images.load(os.path.join(outdir, "floor", "m_0001.png")); seq.source = "SEQUENCE"; seq.colorspace_settings.name = "Non-Color"
seq.filepath = "//floor/m_0001.png"
ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = seq; ti.extension = "CLIP"; ti.interpolation = "Cubic"
ti.image_user.frame_duration = N; ti.image_user.frame_start = 1; ti.image_user.frame_offset = 0; ti.image_user.use_auto_refresh = True
cut = nt.nodes.new("ShaderNodeMapRange"); cut.inputs["From Min"].default_value = 0.35; cut.inputs["From Max"].default_value = 0.55
nt.links.new(ti.outputs["Color"], cut.inputs["Value"]); nt.links.new(cut.outputs["Result"], bs.inputs["Alpha"])
pb = nt.nodes.new("ShaderNodeBump"); pb.inputs["Strength"].default_value = 0.6; pb.inputs["Distance"].default_value = 0.004
nt.links.new(ti.outputs["Color"], pb.inputs["Height"]); old = bs.inputs["Normal"].links[0].from_socket; nt.links.new(old, pb.inputs["Normal"]); nt.links.new(pb.outputs[0], bs.inputs["Normal"])
pm.blend_method = "HASHED"; pool.data.materials.append(pm)

# the liquid in the letters: fills top to bottom with a wavy front (same rule as the video), glossy meniscus
bpy.ops.mesh.primitive_plane_add(size=1, calc_uvs=True)
rb = bpy.context.object; rb.name = "romeLiquid"; rb.scale = (w, h, 1); rb.location = (cx, -cz, -0.0028); bpy.ops.object.transform_apply(scale=True)
rm = mat_blood("bl_romeLiquid", False); nt = rm.node_tree; bs = nt.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = hexc("#7A0610"); bs.inputs["Subsurface Weight"].default_value = 0.6
mt = nt.nodes.new("ShaderNodeTexImage"); mt.image = img; mt.extension = "CLIP"
inl = nt.nodes.new("ShaderNodeMapRange"); inl.inputs["From Min"].default_value = 0.25; inl.inputs["From Max"].default_value = 0.3; nt.links.new(mt.outputs["Color"], inl.inputs["Value"])
uv = nt.nodes.new("ShaderNodeTexCoord"); sepu = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(uv.outputs["UV"], sepu.inputs[0])
fill = keyed_value(nt, "fill", [fd["fill"] for fd in FR])
nz = noise(nt, 7.0, 4, 0.5)
def m_(op, a, b):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    for i, x in enumerate([a, b]):
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: nt.links.new(x, n.inputs[i])
    return n.outputs[0]
qy = m_("SUBTRACT", 1.0, sepu.outputs["Y"])                                   # 0 = top of the word
front = m_("ADD", m_("SUBTRACT", m_("MULTIPLY", fill.outputs[0], 1.3), 0.15), m_("MULTIPLY", m_("SUBTRACT", nz.outputs["Fac"], 0.5), 0.18))
filled = m_("LESS_THAN", qy, front)
alpha = m_("MULTIPLY", inl.outputs["Result"], filled)
nt.links.new(alpha, bs.inputs["Alpha"])
men = m_("SUBTRACT", front, qy)                                              # the leading edge bulges (meniscus)
mb = nt.nodes.new("ShaderNodeBump"); mb.inputs["Strength"].default_value = 0.5; mb.inputs["Distance"].default_value = 0.002
mclamp = nt.nodes.new("ShaderNodeMapRange"); mclamp.inputs["From Min"].default_value = 0.0; mclamp.inputs["From Max"].default_value = 0.05; nt.links.new(men, mclamp.inputs["Value"])
nt.links.new(mclamp.outputs["Result"], mb.inputs["Height"]); old = bs.inputs["Normal"].links[0].from_socket; nt.links.new(old, mb.inputs["Normal"]); nt.links.new(mb.outputs[0], bs.inputs["Normal"])
rm.blend_method = "HASHED"; rb.data.materials.append(rm)
keys(rb, "hide_render", [not c for c in CARVE], 1, "CONSTANT")

# ---------- camera, keyed every frame (cuts are just jumps) ----------
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_mode = "QUATERNION"; cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 24; cam_d.clip_start = 0.01
cam_d.dof.use_dof = True; cam_d.dof.aperture_blades = 7
locs, rots, lens, focus, fst = [], [], [], [], []
for fd in FR:
    c = fd["cam"]; pos, look, up = b3(c["pos"]), b3(c["look"]), b3(c["up"])
    z = (pos - look).normalized(); x = up.cross(z).normalized(); y = z.cross(x)
    m = Matrix(((x.x, y.x, z.x), (x.y, y.y, z.y), (x.z, y.z, z.z)))
    q = m.to_quaternion()
    if rots and q.dot(Quaternion(rots[-1])) < 0: q = -q
    locs.append(tuple(pos)); rots.append(tuple(q)); lens.append(12 / math.tan(math.radians(c["fov"]) / 2)); focus.append(c["focus"]); fst.append(c["fstop"])
keys(cam, "location", locs, 3); keys(cam, "rotation_quaternion", rots, 4)
keys(cam_d, "lens", lens, 1); keys(cam_d, "dof.focus_distance", focus, 1); keys(cam_d, "dof.aperture_fstop", fst, 1)

# ---------- lights: head lights for scene 1, low raking lights once the camera is over the floor ----------
CARVED = [bool(c) for c in CARVE]
def keyed_light(o, base, on):
    keys(o.data, "energy", [base if v else 0.0 for v in on], 1, "CONSTANT")
head = [not c for c in CARVED]
keyed_light(area("key", (-1.5, 1.9, 2.4), (0, 0.45, 0.2), (1.4, 1.0), 130, "#FFC9C2"), 130, head)
keyed_light(area("softbox", (1.6, 1.9, -0.6), (0, 0.5, 0), (1.6, 0.5), 170, "#FFE8E2"), 170, head)
keyed_light(area("rim", (2.4, 2.2, -2.2), (0, 0.4, 0), (1.2, 0.6), 140, "#E0262E"), 140, head)
keyed_light(area("top", (0.1, 4.0, -0.5), (0, 0, 0), (1.2, 1.2), 25, "#FF9A9A"), 25, head)
rc = (cx, 0, cz)
keyed_light(area("rakeL", (-2.2, 0.55, 1.1), rc, (1.6, 0.6), 150, "#FFC9C2"), 150, CARVED)
keyed_light(area("rakeR", (2.0, 0.7, 0.4), rc, (1.2, 0.5), 90, "#FF5A5A"), 90, CARVED)
keyed_light(area("rakeF", (0.3, 0.45, 3.4), rc, (2.0, 0.4), 60, "#FFE0DA"), 60, CARVED)

wd = bpy.data.worlds.new("cove"); sc.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = hexc("#1C0407"); bg.inputs["Strength"].default_value = 0.35

# ---------- compositor: dips to black and the final fade ----------
sc.use_nodes = True; ct = sc.node_tree; ct.nodes.clear()
rl = ct.nodes.new("CompositorNodeRLayers"); comp = ct.nodes.new("CompositorNodeComposite")
mix = ct.nodes.new("CompositorNodeMixRGB"); mix.name = "fade"; mix.blend_type = "MULTIPLY"; mix.inputs[2].default_value = (0, 0, 0, 1)
ct.links.new(rl.outputs["Image"], mix.inputs[1]); ct.links.new(mix.outputs[0], comp.inputs["Image"])
keys(ct, 'nodes["fade"].inputs[0].default_value', [1 - fd["fade"] for fd in FR], 1)
viewer = ct.nodes.new("CompositorNodeViewer"); ct.links.new(mix.outputs[0], viewer.inputs[0])

# ---------- render settings ----------
cy = sc.cycles; sc.render.engine = "CYCLES"
cy.max_bounces = 12; cy.glossy_bounces = 8; cy.transmission_bounces = 8; cy.diffuse_bounces = 4; cy.sample_clamp_indirect = 8.0; cy.blur_glossy = 0.5
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = -0.2
sc.render.film_transparent = False
import farm_prep
if MODE == "farm":
    farm_prep.prepare(sc, OUT, samples=128, frames=(1, N), name="painted_statue", fps=FPS, motion_blur=True)
else:
    # preview (and for opening on a Mac): GPU if there is one, the denoiser on, fewer samples
    cy.device = "GPU"; cy.samples = 64; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    try: cy.denoiser = "OPENIMAGEDENOISE"
    except TypeError: pass
    sc.render.resolution_percentage = 100; sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = "//render/painted_statue_"
    bpy.ops.file.pack_all() if False else None  # the mask stays external too: keeps the file small; folder ships together
    img.filepath = "//rome_mask.png"; shutil.copy(os.path.join(SRC, "rome_mask.png"), os.path.join(outdir, "rome_mask.png"))
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True, relative_remap=True)
    print(f"SAVED {OUT} ({os.path.getsize(OUT) / 1e6:.1f} MB), {N} frames", flush=True)
