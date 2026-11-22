# Lime "oil" phone case reveal (9:16, 10 s, 24 fps = 240 frames), Eevee on CPU.
# Skills: hard-surface (rounded shell, lip, camera bump, booleans then remesh), procedural-modeling +
# geometry-nodes (grow-on sweep), materials/lookdev (lime metallic-plastic with clear coat, flakes and a
# fake oil-slick hue shift), lighting (product strips + softbox), camera-cinematography (4 shots, macro DOF),
# animation (ring swing-in with overshoot, hero turn), rendering (SSR, bloom, motion blur, AgX).
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.environ.get("CASE_OUT", "/home/user/Motion-Studio/work/blender/case/frames/")
RES = (720, 1280)
END = 240
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.fps = 24; S.frame_start, S.frame_end = 1, END
LIME = (0.16, 0.48, 0.0)

def drv(sock, expr):
    d = sock.driver_add("default_value").driver; d.type = 'SCRIPTED'; d.expression = expr

def key(o, path, fr, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)

def rounded_slab(name, hx, hy, z0, z1, r, edge=0.0, seg=10):
    """Rounded-rectangle prism: corners rounded with radius r, optional small bevel on the faces' edges."""
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 2 * hx; v.co.y *= 2 * hy; v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    vert_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-6]
    bmesh.ops.bevel(bm, geom=vert_edges, offset=r, segments=seg, affect='EDGES', profile=0.5)
    if edge:
        others = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6]
        bmesh.ops.bevel(bm, geom=others, offset=edge, segments=3, affect='EDGES', profile=0.5)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); S.collection.objects.link(o); return o

def cyl(name, x, y, z0, z1, r, seg=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    o = bpy.context.object; o.name = name; return o

def boolean(target, cutter, op='DIFFERENCE'):
    m = target.modifiers.new("B_" + cutter.name, 'BOOLEAN'); m.object = cutter; m.operation = op; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target; bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def smooth(o):
    for p in o.data.polygons: p.use_smooth = True

# ---------------------------------------------------------------- growth field (shared by shader + geometry nodes)
# Arrival time A(p) for each point of the case, in "growth units": the back spreads out from the bottom
# centre, then the side walls rise, then the front lip, and the camera bump forms last as its own piece.
GROW_EXPR = "2.55*(min(1,max(0,(frame-4)/80))*min(1,max(0,(frame-4)/80))*(3-2*min(1,max(0,(frame-4)/80))))"   # growth clock T: frames 4-84
START = (0.0, -0.74, -0.053)
def arrival(nt, pos):
    def m(op, a, b=None, c=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(pos, sep.inputs[0])
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    dv = nt.nodes.new("ShaderNodeVectorMath"); dv.operation = 'DISTANCE'; dv.inputs[1].default_value = START
    nt.links.new(pos, dv.inputs[0]); d = dv.outputs["Value"]
    is_bump = m('LESS_THAN', z, -0.063)
    is_lip = m('GREATER_THAN', z, 0.04)
    is_backz = m('LESS_THAN', z, -0.04)
    is_back = m('MULTIPLY', is_backz, m('SUBTRACT', 1.0, is_bump))
    is_side = m('SUBTRACT', m('SUBTRACT', 1.0, is_backz), is_lip, clamp=True)
    a_back = m('MULTIPLY_ADD', d, 1.0, 0.08)
    a_side = m('ADD', m('MULTIPLY', d, 0.92), m('MULTIPLY', m('ADD', z, 0.04), 1.2))
    a_lip = m('MULTIPLY_ADD', d, 0.95, 0.16)
    bx = m('SUBTRACT', x, -0.19); by = m('SUBTRACT', y, 0.55)
    db = m('SQRT', m('ADD', m('MULTIPLY', bx, bx), m('MULTIPLY', by, by)))
    a_bump = m('MULTIPLY_ADD', db, 2.0, 2.05)
    base = m('ADD', m('ADD', m('MULTIPLY', is_back, a_back), m('MULTIPLY', is_side, a_side)),
             m('ADD', m('MULTIPLY', is_lip, a_lip), m('MULTIPLY', is_bump, a_bump)))
    # torn edge: the same noise in both trees (same input, same settings) roughens the growth front
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 0.0
    nz.inputs["Roughness"].default_value = 0.5; nt.links.new(pos, nz.inputs["Vector"])
    return m('ADD', base, m('MULTIPLY_ADD', nz.outputs["Fac"], 0.05, -0.025))

# ---------------------------------------------------------------- materials
def lime_oil(name, metal=0.85, rough=0.18, grow=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Coat IOR"].default_value = 1.6
    # fake oil-slick: facing ratio drives lime -> acid yellow -> teal at grazing angles
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (*LIME, 1)
    cr.elements[1].position = 0.78; cr.elements[1].color = (0.0, 0.25, 0.18, 1)
    mid = cr.elements.new(0.45); mid.color = (0.62, 0.66, 0.0, 1)
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    # metallic flakes under the clear coat
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nz.inputs["Detail"].default_value = 1.0
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.002
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    if grow:
        # grow-on: alpha cut where the growth clock has not reached this point yet, thin glowing lime edge
        at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = 'GEOMETRY'; at.attribute_name = "rest"
        A = arrival(nt, at.outputs["Vector"])
        T = nt.nodes.new("ShaderNodeValue"); drv(T.outputs[0], GROW_EXPR)
        age = nt.nodes.new("ShaderNodeMath"); age.operation = 'SUBTRACT'
        nt.links.new(T.outputs[0], age.inputs[0]); nt.links.new(A, age.inputs[1])
        vis = nt.nodes.new("ShaderNodeMath"); vis.operation = 'GREATER_THAN'; vis.inputs[1].default_value = 0.0
        nt.links.new(age.outputs[0], vis.inputs[0]); nt.links.new(vis.outputs[0], b.inputs["Alpha"])
        band = nt.nodes.new("ShaderNodeMapRange"); band.clamp = True
        band.inputs["From Min"].default_value = 0.022; band.inputs["From Max"].default_value = 0.0
        band.inputs["To Min"].default_value = 0.0; band.inputs["To Max"].default_value = 26.0
        live = nt.nodes.new("ShaderNodeMath"); live.operation = 'LESS_THAN'; live.inputs[1].default_value = 2.48
        glow = nt.nodes.new("ShaderNodeMath"); glow.operation = 'MULTIPLY'
        nt.links.new(age.outputs[0], band.inputs["Value"]); nt.links.new(T.outputs[0], live.inputs[0])
        nt.links.new(band.outputs[0], glow.inputs[0]); nt.links.new(live.outputs[0], glow.inputs[1])
        nt.links.new(glow.outputs[0], b.inputs["Emission Strength"])
        b.inputs["Emission Color"].default_value = (0.55, 1.0, 0.05, 1)
        m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'; m.alpha_threshold = 0.5
    return m
m_case = lime_oil("MAT_LimeOil", grow=True)
m_ring = lime_oil("MAT_LimeRing", metal=0.95, rough=0.1)
def principled(name, col, rough, metal=0.0, coat=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["Coat Weight"].default_value = coat
    if emit: b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = emit
    return m
m_glass = principled("MAT_PhoneGlass", (0.005, 0.006, 0.008), 0.05, coat=1.0)
m_frame = principled("MAT_PhoneFrame", (0.08, 0.085, 0.09), 0.25, metal=1.0)
m_lens = principled("MAT_Lens", (0.0, 0.0, 0.0), 0.02, coat=1.0)
m_lensring = principled("MAT_LensRing", (0.6, 0.62, 0.65), 0.2, metal=1.0)
m_cyc = principled("MAT_Cyclorama", (0.004, 0.016, 0.001), 0.9)
m_cyc.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.08   # matte: stop it mirroring the bright environment

# ---------------------------------------------------------------- product (local axes: X width, Y height, Z depth, back = -Z)
PROD = bpy.data.objects.new("PRODUCT", None); S.collection.objects.link(PROD)
PROD.location = (0, 0, 1.0); PROD.rotation_euler = (math.radians(90), 0, 0)   # back faces world +Y (towards camera)

PHONE = bpy.data.objects.new("PHONE_RIG", None); S.collection.objects.link(PHONE); PHONE.parent = PROD
phone = rounded_slab("SM_Phone", 0.358, 0.738, -0.04, 0.04, 0.105, edge=0.012)
phone.data.materials.append(m_glass); phone.data.materials.append(m_frame); smooth(phone); phone.parent = PHONE
LENSES = [(-0.25, 0.6), (-0.13, 0.6), (-0.19, 0.49)]
for i, (lx, ly) in enumerate(LENSES):
    lr = cyl(f"SM_LensRing_{i}", lx, ly, -0.065, -0.04, 0.05); lr.data.materials.append(m_lensring); smooth(lr); lr.parent = PHONE
    le = cyl(f"SM_Lens_{i}", lx, ly, -0.067, -0.05, 0.038); le.data.materials.append(m_lens); smooth(le); le.parent = PHONE

# case shell: outer slab minus cavity minus front opening, plus camera bump with lens holes
case = rounded_slab("SM_Case", 0.385, 0.765, -0.058, 0.058, 0.125, edge=0.032)
boolean(case, rounded_slab("CUT_Cavity", 0.362, 0.742, -0.04, 0.045, 0.108))
boolean(case, rounded_slab("CUT_Opening", 0.338, 0.718, 0.0, 0.2, 0.092))
bump_ = rounded_slab("ADD_Bump", 0.155, 0.155, -0.074, -0.05, 0.065, edge=0.012)
bump_.location = (-0.19, 0.55, 0); bpy.context.view_layer.objects.active = bump_; bpy.ops.object.transform_apply(location=True)
boolean(case, bump_, 'UNION')
for i, (lx, ly) in enumerate(LENSES):
    boolean(case, cyl(f"CUT_Lens_{i}", lx, ly, -0.2, -0.03, 0.055))
for i, by in enumerate((0.32, 0.18)):          # side button cut-outs
    c = rounded_slab(f"CUT_Btn_{i}", 0.03, 0.05, -0.012, 0.022, 0.012); c.location = (0.395, by, 0)
    bpy.context.view_layer.objects.active = c; bpy.ops.object.transform_apply(location=True); boolean(case, c)
rm = case.modifiers.new("Remesh", 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.0035; rm.use_smooth_shade = True
bpy.context.view_layer.objects.active = case; bpy.ops.object.modifier_apply(modifier="Remesh")
sm = case.modifiers.new("Smooth", 'SMOOTH'); sm.factor = 0.6; sm.iterations = 6   # soften voxel steps before the engraving
bpy.ops.object.modifier_apply(modifier="Smooth")
case.data.materials.append(m_case)
# engraving: PHILLIPS / DIGITAL cut into the back in a typewriter ("analog") face, darker lime in the grooves
m_engrave = lime_oil("MAT_Engrave", metal=0.6, rough=0.45, grow=True)
er = m_engrave.node_tree.nodes["Color Ramp"].color_ramp
for el in er.elements: el.color = (el.color[0] * 0.35, el.color[1] * 0.35, el.color[2] * 0.35, 1)
font = bpy.data.fonts.load("/home/user/Motion-Studio/public/fonts/SpecialElite-Regular.ttf")
bpy.ops.object.text_add(location=(0, -0.45, -0.059), rotation=(0, math.pi, 0))
eng = bpy.context.object; eng.name = "CUT_Engraving"
eng.data.body = "PHILLIPS\nDIGITAL"; eng.data.font = font; eng.data.size = 0.085
eng.data.align_x = 'CENTER'; eng.data.align_y = 'CENTER'; eng.data.space_line = 0.95; eng.data.extrude = 0.006
eng.data.materials.append(m_engrave)
bpy.context.view_layer.objects.active = eng; bpy.ops.object.convert(target='MESH')
bm_e = case.modifiers.new("B_Engrave", 'BOOLEAN'); bm_e.object = eng; bm_e.operation = 'DIFFERENCE'; bm_e.solver = 'EXACT'
bm_e.material_mode = 'TRANSFER'
bpy.context.view_layer.objects.active = case; bpy.ops.object.modifier_apply(modifier="B_Engrave")
bpy.data.objects.remove(eng, do_unlink=True)
case.parent = PROD

# grow-on curl: store each point's rest position (the shader cuts with it), then lift the freshly grown
# band near the front outwards along its normal so the edge peels up and settles flat as it grows
gn = bpy.data.node_groups.new("GN_GrowCurl", 'GeometryNodeTree')
gn.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
gn.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
N = gn.nodes; L = gn.links
gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
pos = N.new("GeometryNodeInputPosition"); nrm = N.new("GeometryNodeInputNormal")
store = N.new("GeometryNodeStoreNamedAttribute"); store.data_type = 'FLOAT_VECTOR'; store.domain = 'POINT'
store.inputs["Name"].default_value = "rest"
vin = [sk for sk in store.inputs if sk.name == "Value" and sk.type == 'VECTOR'][0]
L.new(gi.outputs[0], store.inputs["Geometry"]); L.new(pos.outputs[0], vin)
A = arrival(gn, pos.outputs[0])
T = N.new("ShaderNodeValue"); drv(T.outputs[0], GROW_EXPR)
age = N.new("ShaderNodeMath"); age.operation = 'SUBTRACT'; L.new(T.outputs[0], age.inputs[0]); L.new(A, age.inputs[1])
f = N.new("ShaderNodeMath"); f.operation = 'MULTIPLY_ADD'; f.use_clamp = True; f.inputs[1].default_value = -1 / 0.2; f.inputs[2].default_value = 1.0
L.new(age.outputs[0], f.inputs[0])                       # 1 at the front, 0 once the band is 0.16 behind it
f2 = N.new("ShaderNodeMath"); f2.operation = 'POWER'; f2.inputs[1].default_value = 2.0; L.new(f.outputs[0], f2.inputs[0])
amt = N.new("ShaderNodeMath"); amt.operation = 'MULTIPLY'; amt.inputs[1].default_value = 0.022; L.new(f2.outputs[0], amt.inputs[0])
off = N.new("ShaderNodeVectorMath"); off.operation = 'SCALE'; L.new(nrm.outputs[0], off.inputs[0]); L.new(amt.outputs[0], off.inputs["Scale"])
setp = N.new("GeometryNodeSetPosition"); L.new(store.outputs[0], setp.inputs["Geometry"]); L.new(off.outputs[0], setp.inputs["Offset"])
L.new(setp.outputs[0], go.inputs[0])
case.modifiers.new("GrowCurl", 'NODES').node_group = gn

# MagSafe ring (torus + hinge) swings in and clicks at frame 108
bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.014, major_segments=96, minor_segments=16)
ring = bpy.context.object; ring.name = "SM_MagRing"; ring.data.materials.append(m_ring); smooth(ring)
RING = bpy.data.objects.new("RING_PIVOT", None); S.collection.objects.link(RING); RING.parent = PROD
ring.parent = RING
hinge = rounded_slab("SM_RingHinge", 0.035, 0.02, -0.01, 0.01, 0.01); hinge.location = (0, -0.18, 0)
hinge.data.materials.append(m_ring); smooth(hinge); hinge.parent = RING
key(RING, "location", 1, (0.9, -0.6, -0.9)); key(RING, "location", 86, (0.9, -0.6, -0.9))
key(RING, "location", 104, (0, -0.08, -0.077)); key(RING, "location", 108, (0, -0.08, -0.069)); key(RING, "location", 112, (0, -0.08, -0.073))
key(RING, "rotation_euler", 86, (math.radians(80), math.radians(-40), math.radians(90)))
key(RING, "rotation_euler", 104, (math.radians(-6), 0, 0)); key(RING, "rotation_euler", 112, (0, 0, 0))

# phone: absent while the case builds, then slides in from the open front and seats at frame 104
key(PHONE, "location", 1, (0, 0, 1.4)); key(PHONE, "location", 88, (0, 0, 1.4))
key(PHONE, "location", 102, (0, 0, -0.004)); key(PHONE, "location", 106, (0, 0, 0.0))
for o in [PHONE] + list(PHONE.children):
    o.hide_render = True; o.keyframe_insert("hide_render", frame=87)
    o.hide_render = False; o.keyframe_insert("hide_render", frame=88)

# hero turn: the whole product rotates slowly in the last shot
key(PROD, "rotation_euler", 169, (math.radians(90), 0, math.radians(-28)))
key(PROD, "rotation_euler", 240, (math.radians(90), 0, math.radians(18)))
key(PROD, "rotation_euler", 1, (math.radians(90), 0, math.radians(-18)))
key(PROD, "rotation_euler", 168, (math.radians(90), 0, math.radians(-10)))

# ---------------------------------------------------------------- set + lights
bm = bmesh.new()                                     # cyclorama: floor curving up into a back wall
prof = [(0, y, 0) for y in (8, 4, 1.5)] + [(0, -1.5 - 1.5 * math.sin(a), 1.5 - 1.5 * math.cos(a)) for a in [i * math.pi / 2 / 10 for i in range(1, 11)]] + [(0, -3.0, 8)]
verts_a = [bm.verts.new((-12, y, z)) for (_, y, z) in prof]; verts_b = [bm.verts.new((12, y, z)) for (_, y, z) in prof]
for i in range(len(prof) - 1):
    bm.faces.new((verts_a[i], verts_a[i + 1], verts_b[i + 1], verts_b[i]))
me = bpy.data.meshes.new("SM_Cyclorama"); bm.to_mesh(me); bm.free()
cyc = bpy.data.objects.new("SM_Cyclorama", me); S.collection.objects.link(cyc); cyc.data.materials.append(m_cyc); smooth(cyc)

def light(name, loc, energy, size, size_y=None, col=(1, 1, 1), look=(0, 0, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc); Lg = bpy.context.object; Lg.name = name
    Lg.data.energy = energy; Lg.data.color = col; Lg.data.shape = 'RECTANGLE'; Lg.data.size = size; Lg.data.size_y = size_y or size
    d = Vector(look) - Vector(loc); Lg.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return Lg
light("LGT_Key_Softbox", (0.4, 3.0, 3.4), 300, 2.2, 1.4, (1.0, 0.98, 0.95))
light("LGT_Strip_Left", (-2.2, 1.2, 1.1), 320, 0.25, 3.2, (0.95, 1.0, 0.9))
light("LGT_Strip_Right", (2.2, 1.0, 1.1), 320, 0.25, 3.2, (0.95, 1.0, 0.9))
light("LGT_Rim_Top", (0, -1.2, 3.2), 300, 1.6, 0.4, (0.85, 1.0, 0.6))
light("LGT_Accent_Lime", (-1.5, -1.5, 0.4), 80, 1.5, 1.5, (0.5, 1.0, 0.1))
W = bpy.data.worlds.new("WLD"); S.world = W; W.use_nodes = True
# studio gradient environment: bright overhead, dark below, so the clear coat carries a smooth oily reflection
wt = W.node_tree; bgn = wt.nodes["Background"]
wtc = wt.nodes.new("ShaderNodeTexCoord"); wsp = wt.nodes.new("ShaderNodeSeparateXYZ")
wmr = wt.nodes.new("ShaderNodeMapRange"); wmr.inputs["From Min"].default_value = -0.1; wmr.inputs["From Max"].default_value = 0.9
wramp = wt.nodes.new("ShaderNodeValToRGB")
wramp.color_ramp.elements[0].color = (0.0, 0.01, 0.0, 1); wramp.color_ramp.elements[1].color = (0.3, 0.4, 0.26, 1)
wt.links.new(wtc.outputs["Generated"], wsp.inputs[0]); wt.links.new(wsp.outputs["Z"], wmr.inputs["Value"])
wt.links.new(wmr.outputs["Result"], wramp.inputs["Fac"]); wt.links.new(wramp.outputs["Color"], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 0.45

# ---------------------------------------------------------------- cameras
def camera(name, lens, f0, f1, c0, c1, t0, t1, fstop=None):
    bpy.ops.object.camera_add(); c = bpy.context.object; c.name = name; c.data.lens = lens; c.data.clip_start = 0.01
    c.data.sensor_fit = 'VERTICAL'
    bpy.ops.object.empty_add(); t = bpy.context.object; t.name = "EMPTY_Target_" + name[4:]
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    key(c, "location", f0, c0); key(c, "location", f1, c1); key(t, "location", f0, t0); key(t, "location", f1, t1)
    if fstop: c.data.dof.use_dof = True; c.data.dof.focus_object = t; c.data.dof.aperture_fstop = fstop
    mk = S.timeline_markers.new(name, frame=f0); mk.camera = c; return c
camera("CAM_Grow", 35, 1, 84, (1.5, 3.5, 1.7), (0.7, 3.2, 1.3), (0, 0, 1.02), (0, 0, 1.0), fstop=5.6)
camera("CAM_Ring", 60, 85, 120, (0.6, 1.6, 0.75), (0.3, 1.45, 0.85), (0, 0.06, 0.93), (0, 0.06, 0.93), fstop=2.8)
camera("CAM_Bump", 70, 121, 144, (0.1, 0.95, 1.85), (-0.15, 0.88, 1.75), (-0.19, 0.06, 1.55), (-0.19, 0.06, 1.55), fstop=2.4)
camera("CAM_Edge", 70, 145, 168, (1.15, 0.75, 1.05), (1.05, 0.95, 1.35), (0.38, 0.0, 1.2), (0.38, 0.0, 1.3), fstop=2.8)
camera("CAM_Hero", 40, 169, 240, (0.0, 3.7, 1.15), (0.0, 3.35, 1.1), (0, 0, 1.0), (0, 0, 1.0), fstop=8.0)
S.camera = bpy.data.objects["CAM_Grow"]

# ---------------------------------------------------------------- render
S.render.engine = 'BLENDER_EEVEE'; e = S.eevee
e.taa_render_samples = 32; e.use_ssr = True; e.use_gtao = True; e.gtao_distance = 0.15
e.use_bloom = True; e.bloom_threshold = 1.2; e.bloom_intensity = 0.03
e.use_motion_blur = True; e.motion_blur_shutter = 0.4; e.use_soft_shadows = True
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = *RES, 100
try:
    S.view_settings.view_transform = "Standard"; S.view_settings.look = "Medium High Contrast"; S.view_settings.exposure = -0.35
except TypeError:
    pass
S.render.image_settings.file_format = 'PNG'; os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if args and args[0] == "still":
    for fr in [int(a) for a in args[1:]]:
        S.frame_set(fr)
        S.camera = [m for m in sorted(S.timeline_markers, key=lambda m: m.frame) if m.frame <= fr][-1].camera
        S.render.filepath = OUT + f"still_{fr:03d}.png"; bpy.ops.render.render(write_still=True)
else:
    S.render.filepath = OUT + "f_"; bpy.ops.render.render(animation=True)
print("DONE")
