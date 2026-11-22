# NOVACHIP ident v2 (placeholder brand). Four shots, 9 s at 24 fps (216 frames), Eevee on CPU.
# Skills applied (from .claude/skills): procedural-modeling (seeded circuit-board city built with bmesh),
# hard-surface (bevelled package, lid, chip towers), materials (copper traces, glossy PCB, brushed lid),
# vfx-fx (light pulses racing along traces, energy ripple across the die, spark burst),
# lighting (named key/fill/rim + coloured accents + volumetric haze), camera-cinematography (4 motivated
# moves, lens per shot, DOF, camera switching by markers), rendering/compositing (bloom, SSR, GTAO,
# motion blur, AgX), physics-sim (spark particles with gravity).
import bpy, bmesh, math, os, random, sys
from mathutils import Vector

OUT = os.environ.get("CHIP_OUT", "/home/user/Motion-Studio/work/blender/chip/frames2/")
RES = (1280, 720)
FPS, END = 24, 216
SHOT = {"fly": (1, 60), "crane": (61, 108), "assemble": (109, 156), "logo": (157, 216)}
CYAN, AMBER, WHITE = (0.0, 0.85, 1.0), (1.0, 0.55, 0.12), (0.92, 0.97, 1.0)
rng = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.render.fps, S.frame_start, S.frame_end = FPS, 1, END

# ---------------------------------------------------------------- helpers
def principled(name, base, rough=0.4, metal=0.0, emit=0.0, emit_col=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*(emit_col or base), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m

def frame_driver(sock, expr):
    d = sock.driver_add("default_value").driver
    d.type = 'SCRIPTED'; d.expression = expr  # simple expression: evaluated without Python auto-run

def mesh_obj(name, bm, mat, bevel=0.0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); S.collection.objects.link(o)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Bevel", 'BEVEL'); mod.width = bevel; mod.segments = 2; mod.limit_method = 'ANGLE'
    return o

def add_box(bm, cx, cy, z0, sx, sy, sz):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co.x = cx + v.co.x * sx; v.co.y = cy + v.co.y * sy; v.co.z = z0 + (v.co.z + 0.5) * sz

def add_cyl(bm, cx, cy, z0, r, h, seg=12):
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    for v in res["verts"]:
        v.co.x += cx; v.co.y += cy; v.co.z += z0 + h / 2

def key(obj, path, frame, value, interp='BEZIER'):
    setattr(obj, path, value); obj.keyframe_insert(path, frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if int(kp.co.x) == frame: kp.interpolation = interp

# ---------------------------------------------------------------- materials
m_pcb = principled("MAT_PCB", (0.006, 0.012, 0.016), rough=0.22)
m_body = principled("MAT_Component", (0.018, 0.02, 0.024), rough=0.35, metal=0.3)
m_metal = principled("MAT_CapMetal", (0.62, 0.64, 0.68), rough=0.25, metal=1.0)
m_pin = principled("MAT_Pin", (0.8, 0.6, 0.3), rough=0.22, metal=1.0)
m_led_c = principled("MAT_LED_Cyan", CYAN, emit=14, emit_col=CYAN)
m_led_a = principled("MAT_LED_Amber", AMBER, emit=10, emit_col=AMBER)
m_sub = principled("MAT_Substrate", (0.02, 0.05, 0.04), rough=0.3)
m_lid = principled("MAT_Lid", (0.72, 0.74, 0.78), rough=0.18, metal=1.0)
m_logo = principled("MAT_Logo", WHITE, rough=0.2, emit=0.0, emit_col=(0.75, 0.95, 1.0))
m_spark = principled("MAT_Spark", (1, 0.7, 0.3), emit=40, emit_col=(1.0, 0.75, 0.35))

def trace_material(name, axis):
    """Copper trace with cyan light pulses racing along it (wave bands, phase driven by frame)."""
    m = principled(name, (0.45, 0.22, 0.08), rough=0.3, metal=1.0)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = axis
    wv.inputs["Scale"].default_value = 0.35; wv.inputs["Distortion"].default_value = 0.0
    frame_driver(wv.inputs["Phase Offset"], "frame*0.42")
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1); ramp.color_ramp.elements[1].position = 0.93
    ramp.color_ramp.elements[1].color = (*CYAN, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 9.0
    return m
m_trace_x = trace_material("MAT_Trace_X", 'X')
m_trace_y = trace_material("MAT_Trace_Y", 'Y')

def core_material():
    """Die cores: an energy ripple ring expands from the centre during the crane shot."""
    m = principled("MAT_Core", (0.03, 0.04, 0.05), rough=0.15, metal=0.8)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
    t = nt.nodes.new("ShaderNodeValue"); frame_driver(t.outputs[0], "max(0,(frame-64))*0.075")
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 3.0
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; inv.use_clamp = True
    amp = nt.nodes.new("ShaderNodeMath"); amp.operation = 'MULTIPLY_ADD'; amp.inputs[1].default_value = 22.0; amp.inputs[2].default_value = 0.4
    nt.links.new(tc.outputs["Object"], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], sub.inputs[0]); nt.links.new(t.outputs[0], sub.inputs[1])
    nt.links.new(sub.outputs[0], ab.inputs[0]); nt.links.new(ab.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], inv.inputs[1]); nt.links.new(inv.outputs[0], amp.inputs[0])
    nt.links.new(amp.outputs[0], b.inputs["Emission Strength"])
    b.inputs["Emission Color"].default_value = (*CYAN, 1)
    return m
m_core = core_material()

# ---------------------------------------------------------------- the board: a procedural circuit city
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); pcb = bpy.context.object; pcb.name = "SM_PCB"
pcb.data.materials.append(m_pcb)

LANE, N, CLEAR = 1.0, 15, 3.4          # lane spacing, half-count, keep-out around the chip
bx, by = bmesh.new(), bmesh.new()
for k in range(-N, N + 1):
    add_box(bx, 0, k * LANE, 0.0, 2 * N * LANE, 0.06, 0.012)   # traces along X
    add_box(by, k * LANE, 0, 0.0, 0.06, 2 * N * LANE, 0.012)   # traces along Y
mesh_obj("SM_Traces_X", bx, m_trace_x); mesh_obj("SM_Traces_Y", by, m_trace_y)

bb, bm_cap, bled_c, bled_a = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
for i in range(-N, N):
    for j in range(-N, N):
        cx, cy = (i + 0.5) * LANE, (j + 0.5) * LANE
        if abs(cx) < CLEAR and abs(cy) < CLEAR:
            continue
        d = math.hypot(cx, cy)
        r = rng.random()
        if r < 0.12:
            continue
        elif r < 0.42:                                   # resistor array
            for q in range(rng.randint(2, 4)):
                add_box(bb, cx - 0.25 + q * 0.17, cy + rng.uniform(-0.15, 0.15), 0.0, 0.1, 0.32, 0.07)
        elif r < 0.62:                                   # capacitor cluster
            for q in range(rng.randint(1, 3)):
                ox, oy = rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2)
                h = rng.uniform(0.25, 0.55)
                add_cyl(bb, cx + ox, cy + oy, 0.0, 0.11, h)
                add_cyl(bm_cap, cx + ox, cy + oy, h, 0.112, 0.02)
        elif r < 0.85:                                   # small IC with pins
            s = rng.uniform(0.45, 0.7)
            add_box(bb, cx, cy, 0.0, s, s, 0.09)
            if rng.random() < 0.5:
                add_box(bled_c if rng.random() < 0.7 else bled_a, cx + s * 0.35, cy + s * 0.35, 0.09, 0.05, 0.05, 0.015)
        else:                                            # chip tower (taller further from centre)
            h = 0.4 + min(1.6, d * 0.08) * rng.uniform(0.6, 1.2)
            add_box(bb, cx, cy, 0.0, 0.62, 0.62, h)
            add_box(bb, cx, cy, h, 0.42, 0.42, 0.12)
            add_box(bled_c, cx, cy - 0.311, h * 0.5, 0.3, 0.004, 0.02)
mesh_obj("SM_Components", bb, m_body, bevel=0.012)
mesh_obj("SM_CapTops", bm_cap, m_metal)
mesh_obj("SM_LEDs_Cyan", bled_c, m_led_c)
mesh_obj("SM_LEDs_Amber", bled_a, m_led_a)

# ---------------------------------------------------------------- the chip (hard-surface)
b = bmesh.new(); add_box(b, 0, 0, 0.0, 5.6, 5.6, 0.22); sub = mesh_obj("SM_Substrate", b, m_sub, bevel=0.03)
b = bmesh.new()
for side in range(4):                                   # gold pins round the substrate
    for q in range(16):
        t = -2.4 + q * 0.32
        if side == 0: add_box(b, 2.92, t, 0.0, 0.25, 0.1, 0.04)
        if side == 1: add_box(b, -2.92, t, 0.0, 0.25, 0.1, 0.04)
        if side == 2: add_box(b, t, 2.92, 0.0, 0.1, 0.25, 0.04)
        if side == 3: add_box(b, t, -2.92, 0.0, 0.1, 0.25, 0.04)
mesh_obj("SM_ChipPins", b, m_pin)
b = bmesh.new()
for i in range(12):
    for j in range(12):                                 # 144 cores on the die
        add_box(b, -1.65 + i * 0.3, -1.65 + j * 0.3, 0.22, 0.26, 0.26, 0.06 + 0.04 * ((i * 7 + j * 3) % 3))
cores = mesh_obj("SM_DieCores", b, m_core, bevel=0.008)

# lid (heat spreader) + logo + tagline, parented so they fly in together
b = bmesh.new(); add_box(b, 0, 0, 0.0, 4.4, 4.4, 0.22); lid = mesh_obj("SM_Lid", b, m_lid, bevel=0.06)
bpy.ops.object.text_add(location=(0, 0.25, 0.225)); logo = bpy.context.object; logo.name = "SM_Logo"
logo.data.body = "NOVACHIP"; logo.data.size = 0.62; logo.data.align_x = 'CENTER'; logo.data.align_y = 'CENTER'
logo.data.extrude = 0.015; logo.data.materials.append(m_logo); logo.parent = lid
bpy.ops.object.text_add(location=(0, -0.55, 0.225)); tag = bpy.context.object; tag.name = "SM_Tagline"
tag.data.body = "BUILT AT THE SPEED OF LIGHT"; tag.data.size = 0.16; tag.data.align_x = 'CENTER'; tag.data.align_y = 'CENTER'
tag.data.extrude = 0.004; tag.data.materials.append(m_logo); tag.parent = lid
# logo emission ramps on after the lid locks
lb = m_logo.node_tree.nodes["Principled BSDF"]
frame_driver(lb.inputs["Emission Strength"], "min(1,max(0,(frame-165)/14))*6")

# assembly: lid hovers high, then drops and locks at frame 142 (ease-out), with a tiny overshoot
key(lid, "location", 1, (0, 0, 6.0))
key(lid, "location", 118, (0, 0, 6.0))
key(lid, "location", 140, (0, 0, 0.27))
key(lid, "location", 143, (0, 0, 0.31))
key(lid, "location", 147, (0, 0, 0.29))
key(lid, "rotation_euler", 118, (0, 0, math.radians(-25)))
key(lid, "rotation_euler", 140, (0, 0, 0))

# sparks when the lid locks (physics: particles with gravity)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.02, location=(0, 0, -50))
spark = bpy.context.object; spark.name = "SM_SparkInstance"; spark.data.materials.append(m_spark)
b = bmesh.new()
for side in range(4):
    a = side * math.pi / 2
    v = bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=2.2)["verts"]
    for vv in v:
        vv.co.z = 0.3
emitter = mesh_obj("FX_SparkEmitter", b, m_spark)
emitter.hide_render = True
ps = emitter.modifiers.new("Sparks", 'PARTICLE_SYSTEM').particle_system.settings
ps.count, ps.frame_start, ps.frame_end, ps.lifetime = 450, 140, 146, 22
ps.emit_from = 'FACE'; ps.normal_factor = 1.5; ps.factor_random = 3.0; ps.effector_weights.gravity = 1.0
ps.render_type = 'OBJECT'; ps.instance_object = spark; ps.particle_size = 1.0; ps.size_random = 0.6
emitter.show_instancer_for_render = False

# ---------------------------------------------------------------- lighting + atmosphere
def light(name, typ, loc, energy, col=(1, 1, 1), size=1.0, rot=None, spot=None):
    bpy.ops.object.light_add(type=typ, location=loc)
    L = bpy.context.object; L.name = name; L.data.energy = energy; L.data.color = col
    if typ == 'AREA': L.data.size = size
    if typ == 'SPOT' and spot: L.data.spot_size = spot
    if rot: L.rotation_euler = rot
    L.data.use_shadow = True
    return L
light("LGT_Key_Main", 'AREA', (6, -8, 10), 2600, (1, 0.96, 0.92), size=6, rot=(math.radians(40), 0, math.radians(35)))
light("LGT_Fill_Soft", 'AREA', (-9, -4, 6), 500, (0.6, 0.8, 1.0), size=8, rot=(math.radians(55), 0, math.radians(-60)))
light("LGT_Rim_Back", 'AREA', (0, 10, 5), 3000, CYAN, size=5, rot=(math.radians(-60), 0, 0))
light("LGT_Accent_Amber", 'POINT', (-7, 3, 1.2), 400, AMBER)
light("LGT_Accent_Cyan", 'POINT', (8, -2, 1.0), 500, CYAN)
sweep = light("LGT_Sweep_Lid", 'AREA', (-6, 0, 3), 0, (1, 1, 1), size=0.4, rot=(0, 0, 0))
sweep.data.shape = 'RECTANGLE'; sweep.data.size_y = 9.0
key(sweep, "location", 168, (-6, -1.0, 2.6)); key(sweep, "location", 198, (6, -1.0, 2.6))
sweep.data.energy = 0; sweep.data.keyframe_insert("energy", frame=166)
sweep.data.energy = 1800; sweep.data.keyframe_insert("energy", frame=172)
sweep.data.keyframe_insert("energy", frame=194)
sweep.data.energy = 0; sweep.data.keyframe_insert("energy", frame=200)

W = bpy.data.worlds.new("WLD_Night"); S.world = W; W.use_nodes = True
nt = W.node_tree; nt.nodes["Background"].inputs[0].default_value = (0.002, 0.004, 0.006, 1)
vol = nt.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.009
vol.inputs["Color"].default_value = (0.7, 0.85, 1.0, 1)
nt.links.new(vol.outputs[0], nt.nodes["World Output"].inputs["Volume"])

# ---------------------------------------------------------------- cameras (one motivated move each)
def camera(name, lens, fstop=None, focus=None):
    bpy.ops.object.camera_add(); c = bpy.context.object; c.name = name; c.data.lens = lens
    c.data.clip_start = 0.02
    bpy.ops.object.empty_add(); t = bpy.context.object; t.name = "EMPTY_CamTarget_" + name[4:]
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    if fstop:
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop; c.data.dof.focus_object = focus or t
    return c, t
c1, t1 = camera("CAM_Fly", 22, fstop=1.6)            # skimming macro, shallow focus
key(c1, "location", 1, (-14.5, 0.0, 0.85)); key(c1, "location", 60, (-5.4, 0.0, 1.15))
key(t1, "location", 1, (-10.5, 0.0, 0.15)); key(t1, "location", 60, (-1.0, 0.0, 0.3))
c2, t2 = camera("CAM_Crane", 28, fstop=4.0)          # crane up to reveal the die megastructure
key(c2, "location", 61, (-3.9, -4.3, 0.7)); key(c2, "location", 108, (-6.5, -8.0, 5.8))
key(t2, "location", 61, (0, 0, 0.3)); key(t2, "location", 108, (0, 0, 0.2))
c3, t3 = camera("CAM_Assemble", 40, fstop=5.6)       # three-quarter push-in as the lid drops
key(c3, "location", 109, (7.5, -8.5, 5.5)); key(c3, "location", 156, (5.6, -6.3, 4.0))
key(t3, "location", 109, (0, 0, 0.6)); key(t3, "location", 156, (0, 0, 0.35))
c4, t4 = camera("CAM_Logo", 45, fstop=8.0)           # high angle on the logo, slow push
key(c4, "location", 157, (0, -6.6, 7.6)); key(c4, "location", 216, (0, -5.4, 6.4))
key(t4, "location", 157, (0, 0.1, 0.3)); key(t4, "location", 216, (0, 0.05, 0.3))
for (name, (a, _)), cam in zip(SHOT.items(), (c1, c2, c3, c4)):
    mk = S.timeline_markers.new(name, frame=a); mk.camera = cam
S.camera = c1

# ---------------------------------------------------------------- render settings
S.render.engine = 'BLENDER_EEVEE'
e = S.eevee
e.taa_render_samples = 24
e.use_bloom = True; e.bloom_threshold = 0.9; e.bloom_intensity = 0.06; e.bloom_radius = 5.0
e.use_ssr = True; e.use_ssr_refraction = False; e.use_gtao = True; e.gtao_distance = 0.4
e.use_motion_blur = True; e.motion_blur_shutter = 0.5
e.use_volumetric_shadows = True; e.volumetric_tile_size = '16'; e.volumetric_end = 40
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = *RES, 100
for vt, look in (("AgX", "AgX - Punchy"), ("Filmic", "High Contrast")):
    try:
        S.view_settings.view_transform = vt
        try: S.view_settings.look = look
        except TypeError: pass
        break
    except TypeError:
        continue
S.render.image_settings.file_format = 'PNG'
os.makedirs(OUT, exist_ok=True)

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if args and args[0] == "still":
    for fr in [int(a) for a in args[1:]]:
        S.frame_set(fr)
        cams = [m for m in sorted(S.timeline_markers, key=lambda m: m.frame) if m.frame <= fr]
        S.camera = cams[-1].camera
        S.render.filepath = OUT + f"still_{fr:03d}.png"
        bpy.ops.render.render(write_still=True)
else:
    S.render.filepath = OUT + "f_"
    bpy.ops.render.render(animation=True)
print("DONE")
