# Render one PaintedStatue still in Blender Cycles (CPU path tracing).
# Usage: blender -b --factory-startup -P scripts/blender/render_still.py -- <shot> <export dir> <out.png> [samples]
# The scene comes from scripts/pathtrace/run.cjs ... "export=1": <shot>.glb (meshes, three.js Y-up) + <shot>.json
# (camera) or, for "rome", rome_mask.png (the video's letter mask). Materials here replace the exported ones by name.
import bpy, sys, json, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
SHOT, SRC, OUT = argv[0], argv[1], argv[2]
SAMPLES = int(argv[3]) if len(argv) > 3 else 256
meta = json.load(open(os.path.join(SRC, f"{SHOT}.json")))
from looks import b3, hexc, principled, noise, bump, mat_blood, mat_marble, mat_stone, area

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene

MATS = {"blood": lambda: mat_blood("bl_blood", True), "bloodFlat": lambda: mat_blood("bl_bloodFlat", False), "marble": lambda: mat_marble("bl_marble"), "marbleRaw": lambda: mat_marble("bl_marbleRaw", True), "stone": lambda: mat_stone("bl_stone")}

# ---------- scene ----------
if SHOT == "rome":
    img = bpy.data.images.load(os.path.join(SRC, "rome_mask.png")); img.colorspace_settings.name = "Non-Color"
    cx, cz = meta["romeCentre"]; w = meta["romeWidth"]; h = w * meta["romeAspect"]
    # carved grooves: a dense grid displaced down by the letter mask (V-cut walls from the mask's soft edge)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=1800, y_subdivisions=560, size=1, calc_uvs=True)
    g = bpy.context.object; g.name = "carving"; g.scale = (w, h, 1); g.location = (cx, -cz, 0); bpy.ops.object.transform_apply(scale=True)
    tex = bpy.data.textures.new("romeMask", "IMAGE"); tex.image = img; tex.extension = "CLIP"
    d = g.modifiers.new("carve", "DISPLACE"); d.texture = tex; d.texture_coords = "UV"; d.strength = -0.022; d.mid_level = 0.0
    g.data.materials.append(MATS["stone"]()); bpy.ops.object.shade_smooth()
    # the rest of the infinite floor: a big slab with a rectangular hole where the carving grid sits
    import bmesh
    me = bpy.data.meshes.new("floor"); bm = bmesh.new(); B = 30.0
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, -cz - h / 2, -cz + h / 2
    V = [bm.verts.new(p) for p in [(-B, -B, 0), (B, -B, 0), (B, B, 0), (-B, B, 0), (x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]]
    for q in [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]: bm.faces.new([V[i] for i in q])
    bm.to_mesh(me); fl = bpy.data.objects.new("floor", me); sc.collection.objects.link(fl); fl.data.materials.append(MATS["stone"]())
    # the blood: a liquid surface just under the stone, cut out by the mask; the groove walls hold it
    bpy.ops.mesh.primitive_plane_add(size=1, calc_uvs=True)
    bl = bpy.context.object; bl.name = "romeBlood"; bl.scale = (w, h, 1); bl.location = (cx, -cz, -0.0028); bpy.ops.object.transform_apply(scale=True)
    m = mat_blood("romeBlood", False); nt = m.node_tree; bs = nt.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = hexc("#8A0812"); bs.inputs["Subsurface Weight"].default_value = 0.6
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = img; ti.extension = "CLIP"
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.25; ramp.color_ramp.elements[1].position = 0.3
    nt.links.new(ti.outputs["Color"], ramp.inputs[0]); nt.links.new(ramp.outputs["Color"], bs.inputs["Alpha"])
    # meniscus: the surface curves up to the walls (bump from the mask's soft edge)
    bb = nt.nodes.new("ShaderNodeBump"); bb.inputs["Strength"].default_value = 0.6; bb.inputs["Distance"].default_value = 0.003; bb.invert = True
    nt.links.new(ti.outputs["Color"], bb.inputs["Height"]); nt.links.new(bb.outputs[0], bs.inputs["Normal"])
    m.blend_method = "HASHED"; bl.data.materials.append(m)
else:
    bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, f"{SHOT}.glb"))
    made = {}
    for o in list(bpy.context.scene.objects):
        if o.type != "MESH": continue
        for slot in o.material_slots:
            base = (slot.material.name if slot.material else "stone").split(".")[0]
            if base in MATS:
                if base not in made: made[base] = MATS[base]()
                slot.material = made[base]

# ---------- camera ----------
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
pos, look, up = b3(meta["pos"]), b3(meta["look"]), b3(meta["up"])
z = (pos - look).normalized(); x = up.cross(z).normalized(); y = z.cross(x)
cam.matrix_world = Matrix(((x.x, y.x, z.x, pos.x), (x.y, y.y, z.y, pos.y), (x.z, y.z, z.z, pos.z), (0, 0, 0, 1)))
cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 24; cam_d.angle_y = math.radians(meta["fov"]); cam_d.clip_start = 0.01
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = meta["focus"]
cam_d.dof.aperture_fstop = {"macro": 1.4, "break": 2.2, "rome": 2.8}[SHOT]; cam_d.dof.aperture_blades = 7

# ---------- lights: out of shot, never seen directly (C4D omni/softbox style) ----------
LK = float(os.environ.get("LIGHT", "1.0"))
if SHOT == "rome":
    # bird's-eye: low raking lights from the sides, so the stone stays dark and the liquid in the grooves catches the light
    rc = (meta["romeCentre"][0], 0, meta["romeCentre"][1])
    area("rakeL", (-2.2, 0.55, 1.1), rc, (1.6, 0.6), 150 * LK, "#FFC9C2")
    area("rakeR", (2.0, 0.7, 0.4), rc, (1.2, 0.5), 90 * LK, "#FF5A5A")
    area("rakeF", (0.3, 0.45, 3.4), rc, (2.0, 0.4), 60 * LK, "#FFE0DA")
    st = bpy.data.materials.get("bl_stone")
    if st: rr = [n for n in st.node_tree.nodes if n.bl_idname == "ShaderNodeMapRange"][0]; rr.inputs["To Min"].default_value = 0.55; rr.inputs["To Max"].default_value = 0.85
if SHOT != "rome": area("key", (-1.5, 1.9, 2.4), (0, 0.45, 0.2), (1.4, 1.0), 130 * LK, "#FFC9C2")
if SHOT != "rome": area("softbox", (1.6, 1.9, -0.6), (0, 0.5, 0), (1.6, 0.5), 170 * LK, "#FFE8E2")
if SHOT != "rome": area("rim", (2.4, 2.2, -2.2), (0, 0.4, 0), (1.2, 0.6), 140 * LK, "#E0262E")
if SHOT != "rome": area("top", (0.1, 4.0, -0.5), (0, 0, 0), (1.2, 1.2), 25 * LK, "#FF9A9A")

# world: dark maroon cove; a little red ambient so shadows are not dead black
wd = bpy.data.worlds.new("cove"); sc.world = wd; wd.use_nodes = True
bgn = wd.node_tree.nodes["Background"]; bgn.inputs["Color"].default_value = hexc("#1C0407"); bgn.inputs["Strength"].default_value = 0.35

# ---------- render ----------
sc.render.engine = "CYCLES"; cy = sc.cycles; cy.device = "CPU"
cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.008
import _cycles
cy.use_denoising = bool(getattr(_cycles, "with_openimagedenoise", False))
if cy.use_denoising: cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 12; cy.glossy_bounces = 8; cy.transmission_bounces = 8; cy.diffuse_bounces = 4
cy.sample_clamp_indirect = 8.0; cy.blur_glossy = 0.5
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080; sc.render.resolution_percentage = int(os.environ.get("PCT", "100"))
sc.render.threads_mode = "AUTO"; sc.render.use_persistent_data = False
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = float(os.environ.get("EXP", "-0.2"))
sc.render.image_settings.file_format = "PNG"; sc.render.filepath = OUT
FARM = os.environ.get("FARM_BLEND")  # save a farm-ready .blend instead of rendering here
if FARM:
    import farm_prep
    farm_prep.prepare(sc, FARM, samples=int(os.environ.get("FARM_SAMPLES", "128")), frames=(1, 1), name=SHOT)
else:
    print(f"RENDER {SHOT}: {SAMPLES} spp, denoise={cy.use_denoising}, objects={len(sc.objects)}", flush=True)
    bpy.ops.render.render(write_still=True)
    print("SAVED", OUT, flush=True)
