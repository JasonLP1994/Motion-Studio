# v2: tangerine "oil" phone case reveal (9:16, 10 s, 24 fps = 240 frames). Real phone model, case built around it,
# Cycles + Intel Open Image Denoise (scripts/denoise/oidn_render.py), 720x1280 then AI 2x upscale (scripts/ai/upscale.py).
# Phone: "Apple iPhone 13 Pro Max" by DatSketch (Sketchfab, CC-BY 4.0, via Objaverse), Apple logo removed.
# Skills: hard-surface (rounded shell, lip, camera bump, booleans then remesh), procedural-modeling +
# geometry-nodes (grow-on sweep), materials/lookdev (lime metallic-plastic with clear coat, flakes and a
# fake oil-slick hue shift), lighting (product strips + softbox), camera-cinematography (4 shots, macro DOF),
# animation (ring swing-in with overshoot, hero turn), rendering (SSR, bloom, motion blur, AgX).
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.environ.get("CASE_OUT", "/home/user/Motion-Studio/work/blender/case/frames_v2/")
PHONE_GLB = "/home/user/Motion-Studio/work/phonemodels/4328dea00e47497dbeac73c556121bc9.glb"
RES = (720, 1280)
END = 240
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.fps = 24; S.frame_start, S.frame_end = 1, END
ORANGE = (1.0, 0.16, 0.0)          # tangerine oil
GOLD = (1.0, 0.42, 0.0)
GRAZE = (0.5, 0.02, 0.16)          # magenta-red at grazing angles
GLOW = (1.0, 0.62, 0.18)           # warm growth edge
TEAL = (0.004, 0.045, 0.055)       # petrol backdrop (complementary)

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
GROW_EXPR = "2.15*(min(1,max(0,(frame-4)/136))*min(1,max(0,(frame-4)/136))*(3-2*min(1,max(0,(frame-4)/136))))"   # growth clock T: frames 4-140
START = (0.355, -0.735, -0.042)   # one bottom corner (the reference starts from a corner chip)
BUMP_C = (0.172, 0.531)   # camera island centre in case space (measured from the phone model)
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
    # ONE growth front: arrival depends on x,y only, so the outer skin, the inner wall and the rim
    # at the same spot arrive together (no second line showing through the hollow case).
    # Points near the outline lead a little, bending the single front into the reference's U shape.
    is_bump = m('LESS_THAN', z, -0.047)
    sx = m('SUBTRACT', x, START[0]); sy = m('SUBTRACT', y, START[1])
    dxy = m('SQRT', m('ADD', m('MULTIPLY', sx, sx), m('MULTIPLY', sy, sy)))
    ex = m('SUBTRACT', 0.381, m('ABSOLUTE', x)); ey = m('SUBTRACT', 0.761, m('ABSOLUTE', y))
    rim = m('SUBTRACT', 1.0, m('DIVIDE', m('MINIMUM', ex, ey), 0.14), clamp=True)
    a_shell = m('SUBTRACT', m('MULTIPLY_ADD', dxy, 1.0, 0.12), m('MULTIPLY', m('MULTIPLY', rim, rim), 0.22))
    bx = m('SUBTRACT', x, BUMP_C[0]); by = m('SUBTRACT', y, BUMP_C[1])
    db = m('SQRT', m('ADD', m('MULTIPLY', bx, bx), m('MULTIPLY', by, by)))
    a_bump = m('MULTIPLY_ADD', db, 2.0, 1.84)
    base = m('ADD', m('MULTIPLY', m('SUBTRACT', 1.0, is_bump), a_shell), m('MULTIPLY', is_bump, a_bump))
    # torn edge: the same noise in both trees (same input, same settings) roughens the growth front
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 11.0; nz.inputs["Detail"].default_value = 3.0
    nz.inputs["Roughness"].default_value = 0.5; nt.links.new(pos, nz.inputs["Vector"])
    return m('ADD', base, m('MULTIPLY_ADD', nz.outputs["Fac"], 0.07, -0.035))

# ---------------------------------------------------------------- materials
def lime_oil(name, metal=0.85, rough=0.16, grow=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Coat IOR"].default_value = 1.6
    # oil-slick: facing ratio drives tangerine -> gold -> magenta at grazing angles
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (*ORANGE, 1)
    cr.elements[1].position = 0.8; cr.elements[1].color = (*GRAZE, 1)
    mid = cr.elements.new(0.45); mid.color = (*GOLD, 1)
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    # metallic flakes under the clear coat
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nz.inputs["Detail"].default_value = 1.0
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.025; bump.inputs["Distance"].default_value = 0.002
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
        band.inputs["To Min"].default_value = 0.0; band.inputs["To Max"].default_value = 14.0
        live = nt.nodes.new("ShaderNodeMath"); live.operation = 'LESS_THAN'; live.inputs[1].default_value = 2.12
        glow = nt.nodes.new("ShaderNodeMath"); glow.operation = 'MULTIPLY'
        nt.links.new(age.outputs[0], band.inputs["Value"]); nt.links.new(T.outputs[0], live.inputs[0])
        nt.links.new(band.outputs[0], glow.inputs[0]); nt.links.new(live.outputs[0], glow.inputs[1])
        nt.links.new(glow.outputs[0], b.inputs["Emission Strength"])
        b.inputs["Emission Color"].default_value = (*GLOW, 1)
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
BG_GREEN = TEAL
m_cyc = principled("MAT_Cyclorama", BG_GREEN, 0.95)
_cb = m_cyc.node_tree.nodes["Principled BSDF"]
_cb.inputs["Specular IOR Level"].default_value = 0.0
_cb.inputs["Emission Color"].default_value = (*BG_GREEN, 1); _cb.inputs["Emission Strength"].default_value = 0.35  # mostly self-lit = flat, seamless

# ---------------------------------------------------------------- product (local axes: X width, Y height, Z depth, back = -Z)
PROD = bpy.data.objects.new("PRODUCT", None); S.collection.objects.link(PROD)
PROD.location = (0, 0, 1.0); PROD.rotation_euler = (math.radians(90), 0, 0)   # back faces world +Y (towards camera)

PHONE = bpy.data.objects.new("PHONE_RIG", None); S.collection.objects.link(PHONE); PHONE.parent = PROD
_before = set(S.objects)
bpy.ops.import_scene.gltf(filepath=PHONE_GLB)
_new = [o for o in S.objects if o not in _before]
for o in _new:
    if "Apple Logo" in o.name: bpy.data.objects.remove(o, do_unlink=True)
_meshes = [o for o in S.objects if o not in _before and o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in _meshes: o.select_set(True)
bpy.context.view_layer.objects.active = _meshes[0]; bpy.ops.object.join()
phone = bpy.context.view_layer.objects.active; phone.name = "SM_Phone"
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in S.objects if o not in _before and o != phone]: bpy.data.objects.remove(o, do_unlink=True)
PS = 1.49                                   # phone half-width 0.2402 -> 0.358 (same size as before)
phone.parent = PHONE; phone.rotation_mode = "XYZ"; phone.scale = (PS, PS, PS); phone.rotation_euler = (math.radians(90), 0, math.radians(180))   # (x,y,z) -> (-x, z, y): back = -Z
# measurements (case space): body back z, glass front z, half sizes, corner radius from the frame outline
_co = [v.co for v in phone.data.vertices]
_hx = max(abs(c.x) for c in _co if abs(c.y) < 0.03 and abs(c.z) < 0.49 and abs(c.x) < 0.2405) * PS
_hy = 0.4953 * PS
_diag = max(abs(c.x) + abs(c.z) for c in _co if abs(c.x) < 0.2405) * PS
PR = max(0.06, min(0.2, (_hx + _hy - _diag) / (2 - math.sqrt(2))))
Z_BACK, Z_FRONT = -0.0175 * PS, 0.0254 * PS
bpy.ops.object.select_all(action='DESELECT')   # later transform_apply calls must not touch the phone
print("PHONE", round(_hx, 4), round(_hy, 4), "corner r", round(PR, 4), "z", round(Z_BACK, 4), round(Z_FRONT, 4))

# case shell: outer slab minus cavity minus front opening, plus camera bump with lens holes
CL, WALL, BACK, LIP = 0.003, 0.02, 0.016, 0.006
cx, cy = _hx + CL, _hy + CL                                         # cavity
z0 = Z_BACK - 0.002 - BACK; z1 = Z_FRONT + LIP                       # outer back plane, lip top
case = rounded_slab("SM_Case", cx + WALL, cy + WALL, z0, z1, PR + CL + WALL, edge=0.012)
boolean(case, rounded_slab("CUT_Cavity", cx, cy, Z_BACK - 0.002, z1 + 0.1, PR + CL))
boolean(case, rounded_slab("CUT_Lip", _hx - 0.012, _hy - 0.012, Z_FRONT - 0.003, 0.3, PR - 0.012))   # lip overhangs the screen edge
# camera: hole matched to the phone's camera island + a raised protective rim around it
IX0, IX1, IY0, IY1 = -0.0077 * -PS, 0.2234 * PS, 0.2347 * PS, 0.478 * PS
icx, icy, ihx, ihy = (IX0 + IX1) / 2, (IY0 + IY1) / 2, (IX1 - IX0) / 2, (IY1 - IY0) / 2
rim = rounded_slab("ADD_CamRim", ihx + 0.03, ihy + 0.03, -0.062, z0 + 0.002, 0.075, edge=0.008)
rim.location = (icx, icy, 0); bpy.context.view_layer.objects.active = rim; bpy.ops.object.transform_apply(location=True); boolean(case, rim, 'UNION')
hole = rounded_slab("CUT_CamHole", ihx + 0.008, ihy + 0.008, -0.2, Z_BACK + 0.01, 0.06)
hole.location = (icx, icy, 0); bpy.context.view_layer.objects.active = hole; bpy.ops.object.transform_apply(location=True); boolean(case, hole)
# buttons (volume/silent one side, power the other) and the charging port
for i, (sx, y0b, y1b) in enumerate(((-1, 0.0988 * PS, 0.2495 * PS), (1, 0.12 * PS, 0.31 * PS))):
    c = rounded_slab(f"CUT_Btn_{i}", 0.04, (y1b - y0b) / 2 + 0.01, Z_BACK + 0.008, Z_FRONT - 0.008, 0.01)
    c.location = (sx * (cx + WALL), (y0b + y1b) / 2, 0); bpy.context.view_layer.objects.active = c; bpy.ops.object.transform_apply(location=True); boolean(case, c)
c = rounded_slab("CUT_Port", 0.16, 0.04, Z_BACK + 0.006, Z_FRONT - 0.004, 0.015); c.location = (0, -(cy + WALL), 0)
bpy.context.view_layer.objects.active = c; bpy.ops.object.transform_apply(location=True); boolean(case, c)
case.data.use_auto_smooth = True; case.data.auto_smooth_angle = math.radians(35); smooth(case)   # crisp manufactured edges, no remesh
BUMP_C_CHECK = (icx, icy); print("BUMP centre", round(icx, 3), round(icy, 3))
case.data.materials.append(m_case)
# engraving: PHILLIPS / DIGITAL cut into the back in a typewriter ("analog") face, darker lime in the grooves
m_engrave = lime_oil("MAT_Engrave", metal=0.6, rough=0.45, grow=True)
er = m_engrave.node_tree.nodes["Color Ramp"].color_ramp
for el in er.elements: el.color = (el.color[0] * 0.18, el.color[1] * 0.18, el.color[2] * 0.18, 1)
font = bpy.data.fonts.load("/home/user/Motion-Studio/public/fonts/SpecialElite-Regular.ttf")
bpy.ops.object.text_add(location=(0, -0.42, z0 - 0.0015), rotation=(0, math.pi, 0))
eng = bpy.context.object; eng.name = "CUT_Engraving"
eng.data.body = "PHILLIPS\nDIGITAL"; eng.data.font = font; eng.data.size = 0.085
eng.data.align_x = 'CENTER'; eng.data.align_y = 'CENTER'; eng.data.space_line = 0.95; eng.data.extrude = 0.007
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
key(RING, "location", 1, (0.9, -0.6, -0.9)); key(RING, "location", 156, (0.9, -0.6, -0.9))
key(RING, "location", 168, (0, -0.08, z0 - 0.018)); key(RING, "location", 172, (0, -0.08, z0 - 0.01)); key(RING, "location", 176, (0, -0.08, z0 - 0.014))
key(RING, "rotation_euler", 156, (math.radians(80), math.radians(-40), math.radians(90)))
key(RING, "rotation_euler", 168, (math.radians(-6), 0, 0)); key(RING, "rotation_euler", 176, (0, 0, 0))

# phone: absent while the case builds, then slides in from the open front and seats at frame 104
key(PHONE, "location", 1, (0, 0, 1.4)); key(PHONE, "location", 144, (0, 0, 1.4))
key(PHONE, "location", 156, (0, 0, -0.004)); key(PHONE, "location", 160, (0, 0, 0.0))
for o in [PHONE] + list(PHONE.children):
    o.hide_render = True; o.keyframe_insert("hide_render", frame=143)
    o.hide_render = False; o.keyframe_insert("hide_render", frame=144)

# hero turn: the whole product rotates slowly in the last shot
key(PROD, "rotation_euler", 181, (math.radians(90), 0, math.radians(-28)))
key(PROD, "rotation_euler", 240, (math.radians(90), 0, math.radians(18)))
key(PROD, "rotation_euler", 1, (math.radians(90), 0, math.radians(-18)))
key(PROD, "rotation_euler", 176, (math.radians(90), 0, math.radians(-10)))

# ---------------------------------------------------------------- set + lights
bm = bmesh.new()                                     # cyclorama: floor curving up into a back wall
prof = [(0, y, 0) for y in (14, 6, 0.0)] + [(0, -4.0 * math.sin(a), 4.0 - 4.0 * math.cos(a)) for a in [i * math.pi / 2 / 16 for i in range(1, 17)]] + [(0, -4.0, 14)]
verts_a = [bm.verts.new((-20, y, z)) for (_, y, z) in prof]; verts_b = [bm.verts.new((20, y, z)) for (_, y, z) in prof]
for i in range(len(prof) - 1):
    bm.faces.new((verts_a[i], verts_a[i + 1], verts_b[i + 1], verts_b[i]))
me = bpy.data.meshes.new("SM_Cyclorama"); bm.to_mesh(me); bm.free()
cyc = bpy.data.objects.new("SM_Cyclorama", me); S.collection.objects.link(cyc); cyc.data.materials.append(m_cyc); smooth(cyc)

def light(name, loc, energy, size, size_y=None, col=(1, 1, 1), look=(0, 0, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc); Lg = bpy.context.object; Lg.name = name
    Lg.data.energy = energy; Lg.data.color = col; Lg.data.shape = 'RECTANGLE'; Lg.data.size = size; Lg.data.size_y = size_y or size
    d = Vector(look) - Vector(loc); Lg.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return Lg
# --- product lighting (see notes/product-lighting.md): light the REFLECTIONS. A gradient softbox panel gives the flat glossy back a
# smooth bright-to-dark sheen, grazing strips draw the edge highlights, black cards add contrast in the reflections, a weak fill
# keeps the form, a teal kick ties the case to the set. Product lights are light-linked to the product only; the backdrop gets
# its own soft pool, so neither washes the other out.
COL_P = bpy.data.collections.new("COL_ProductLit"); S.collection.children.link(COL_P)
for o in [case, ring, hinge, phone]: COL_P.objects.link(o)
COL_BG = bpy.data.collections.new("COL_Backdrop"); S.collection.children.link(COL_BG); COL_BG.objects.link(cyc)
def link_to(o, col):
    try: o.light_linking.receiver_collection = col
    except AttributeError: pass
def aim(o, look=(0, 0, 1.0)): o.rotation_euler = (Vector(look) - o.location).to_track_quat('-Z', 'Y').to_euler()
def card(name, loc, sx, sy, emit=0.0, gradient=False, look=(0, 0, 1.0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc); o = bpy.context.object; o.name = name; o.scale = (sx, sy, 1); aim(o, look)
    m = bpy.data.materials.new("MAT_" + name); m.use_nodes = True; nt = m.node_tree; N_ = nt.nodes
    for n in list(N_): 
        if n.type != 'OUTPUT_MATERIAL': N_.remove(n)
    em = N_.new("ShaderNodeEmission"); nt.links.new(em.outputs[0], N_["Material Output"].inputs["Surface"])
    if gradient:   # bright top edge fading to dark: the classic gradient-softbox reflection
        tc = N_.new("ShaderNodeTexCoord"); sp = N_.new("ShaderNodeSeparateXYZ"); mr = N_.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -0.5; mr.inputs["From Max"].default_value = 0.5; mr.inputs["To Min"].default_value = 0.0
        mr.inputs["To Max"].default_value = emit; pw = N_.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6
        nt.links.new(tc.outputs["Generated"], sp.inputs[0]); nt.links.new(sp.outputs["Y"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], pw.inputs[0]); nt.links.new(pw.outputs[0], em.inputs["Strength"])
    else:
        em.inputs["Strength"].default_value = emit
    if emit == 0.0: em.inputs["Color"].default_value = (0, 0, 0, 1)
    o.data.materials.append(m)
    o.visible_camera = False; o.visible_shadow = False        # seen only in reflections, never blocks light
    return o
# key = broad softbox + a thin brighter strip on its top edge: reads as a gradient sheen, and area lights sample cleanly (no blotches)
KEY = light("LGT_Key_Softbox", (0.4, 4.2, 2.7), 85, 2.6, 1.2, (1.0, 0.98, 0.95)); link_to(KEY, COL_P)
KEYT = light("LGT_Key_TopStrip", (0.4, 4.0, 3.45), 150, 2.6, 0.14, (1.0, 1.0, 1.0)); link_to(KEYT, COL_P)
NEG1 = card("LGT_NegFill_LowFront", (-0.5, 3.6, 0.15), 2.8, 1.2)                        # black card: dark band low in the back's reflection
NEG2 = card("LGT_NegFill_Right", (2.4, 1.6, 1.2), 1.6, 2.6)                             # black card: contrast on the right edge
L1 = light("LGT_Strip_Left_Grazing", (-2.0, -0.45, 1.15), 480, 0.18, 3.2, (1.0, 1.0, 1.0)); link_to(L1, COL_P)
L2 = light("LGT_Strip_Right_Grazing", (2.0, -0.3, 1.15), 380, 0.18, 3.2, (1.0, 0.98, 0.95)); link_to(L2, COL_P)
L3 = light("LGT_Rim_Top", (0, -1.4, 3.0), 260, 1.6, 0.22, (0.92, 0.96, 1.0)); link_to(L3, COL_P)
L4 = light("LGT_Fill_Soft", (2.6, 1.6, 0.9), 22, 2.0, 2.0, (1.0, 0.96, 0.92)); link_to(L4, COL_P)
L4.visible_glossy = False          # fill lifts the shading only: no hard rectangle in the glossy back
L5 = light("LGT_Kick_Teal", (-1.9, -0.7, 0.55), 160, 0.3, 2.0, (0.1, 0.75, 0.85))   # behind-left, grazing: a teal edge line, not a front reflection; link_to(L5, COL_P)
bpy.ops.object.light_add(type='SPOT', location=(0, -1.2, 4.2)); BGP = bpy.context.object; BGP.name = "LGT_Backdrop_Pool"
BGP.data.energy = 900; BGP.data.spot_size = math.radians(55); BGP.data.spot_blend = 1.0; BGP.data.color = (0.6, 0.95, 1.0)
aim(BGP, (0, -4.0, 1.6)); link_to(BGP, COL_BG)
W = bpy.data.worlds.new("WLD"); S.world = W; W.use_nodes = True
# studio gradient environment: bright overhead, dark below, so the clear coat carries a smooth oily reflection
wt = W.node_tree; bgn = wt.nodes["Background"]
wtc = wt.nodes.new("ShaderNodeTexCoord"); wsp = wt.nodes.new("ShaderNodeSeparateXYZ")
wmr = wt.nodes.new("ShaderNodeMapRange"); wmr.inputs["From Min"].default_value = -0.1; wmr.inputs["From Max"].default_value = 0.9
wramp = wt.nodes.new("ShaderNodeValToRGB")
wramp.color_ramp.elements[0].color = (0.003, 0.02, 0.025, 1); wramp.color_ramp.elements[1].color = (0.05, 0.16, 0.18, 1)
wt.links.new(wtc.outputs["Generated"], wsp.inputs[0]); wt.links.new(wsp.outputs["Z"], wmr.inputs["Value"])
wt.links.new(wmr.outputs["Result"], wramp.inputs["Fac"]); wt.links.new(wramp.outputs["Color"], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 0.3

# ---------------------------------------------------------------- cameras
def camera(name, lens, f0, f1, c0, c1, t0, t1, fstop=None):
    bpy.ops.object.camera_add(); c = bpy.context.object; c.name = name; c.data.lens = lens; c.data.clip_start = 0.01
    c.data.sensor_fit = 'VERTICAL'
    bpy.ops.object.empty_add(); t = bpy.context.object; t.name = "EMPTY_Target_" + name[4:]
    tr = c.constraints.new('TRACK_TO'); tr.target = t; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    key(c, "location", f0, c0); key(c, "location", f1, c1); key(t, "location", f0, t0); key(t, "location", f1, t1)
    if fstop: c.data.dof.use_dof = True; c.data.dof.focus_object = t; c.data.dof.aperture_fstop = fstop
    mk = S.timeline_markers.new(name, frame=f0); mk.camera = c; return c
# build is seen only in close-ups; the whole case is held back for the pull-back reveal at the end
# 0-5.8 s: mystery. Tight macros ride the growth front so the object can't be read; 5.8-7.5 s phone + ring; 7.5-10 s pull-back reveal
camera("CAM_Chip", 70, 1, 30, (0.95, 0.75, 0.12), (0.85, 0.66, 0.18), (0.33, 0.05, 0.27), (0.3, 0.05, 0.32), fstop=2.0)
camera("CAM_Rim", 50, 31, 66, (1.15, 0.85, 0.1), (1.05, 0.8, 0.78), (0.36, 0.0, 0.2), (0.34, 0.0, 0.78), fstop=2.8)
camera("CAM_Sweep", 50, 67, 102, (0.12, 0.3, 2.0), (-0.02, 0.26, 1.9), (0.1, 0.05, 1.0), (0.0, 0.05, 1.2), fstop=2.8)
camera("CAM_Bump", 60, 103, 140, (-0.42, 0.62, 1.12), (-0.24, 0.58, 1.22), (0.02, 0.06, 1.37), (0.04, 0.06, 1.4), fstop=2.8)   # oblique onto the rim corner (the cut-out is an open hole until the phone arrives)
camera("CAM_Ring", 60, 141, 180, (0.6, 1.6, 0.75), (0.3, 1.45, 0.85), (0, 0.06, 0.93), (0, 0.06, 0.93), fstop=2.8)
camera("CAM_Hero", 40, 181, 240, (0.25, 1.7, 0.85), (0.0, 3.1, 1.1), (0, 0, 0.95), (0, 0, 1.0), fstop=8.0)
S.camera = bpy.data.objects["CAM_Chip"]

# ---------------------------------------------------------------- render
S.render.engine = 'CYCLES'; cy_ = S.cycles
cy_.device = 'CPU'; cy_.samples = 48; cy_.use_denoising = False; cy_.use_adaptive_sampling = True; cy_.adaptive_threshold = 0.03
cy_.max_bounces = 8; cy_.transparent_max_bounces = 24; cy_.glossy_bounces = 4; cy_.transmission_bounces = 2; cy_.diffuse_bounces = 2
cy_.sample_clamp_indirect = 3.0; cy_.caustics_reflective = False; cy_.caustics_refractive = False
try: cy_.use_light_tree = True
except AttributeError: pass
S.render.use_motion_blur = True; S.render.motion_blur_shutter = 0.4
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = *RES, 100
try:
    S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Medium High Contrast"; S.view_settings.exposure = -0.05
except TypeError:
    S.view_settings.view_transform = "Filmic"; S.view_settings.look = "Medium High Contrast"
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
_rl = ct.nodes.new("CompositorNodeRLayers"); _gl = ct.nodes.new("CompositorNodeGlare"); _co_ = ct.nodes.new("CompositorNodeComposite")
_gl.glare_type = 'FOG_GLOW'; _gl.threshold = 10.0; _gl.mix = -0.2; _gl.quality = 'HIGH'; _gl.size = 7
ct.links.new(_rl.outputs["Image"], _gl.inputs["Image"]); ct.links.new(_gl.outputs["Image"], _co_.inputs["Image"])
if os.environ.get("CASE_ENGINE") == "EEVEE":      # fast option: same scene in Eevee (compositor glare still applies)
    S.render.engine = 'BLENDER_EEVEE'; e = S.eevee
    e.taa_render_samples = 48; e.use_ssr = True; e.use_ssr_halfres = False; e.use_gtao = True; e.gtao_distance = 0.15
    e.use_motion_blur = True; e.motion_blur_shutter = 0.4; e.use_soft_shadows = True; e.gi_cubemap_resolution = '1024'
    m_case.blend_method = 'CLIP'
if os.environ.get("NO_OVERWRITE"): S.render.use_overwrite = False; S.render.use_placeholder = False
S.render.image_settings.file_format = 'PNG'; os.makedirs(OUT, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if args and args[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=args[1]); print("SAVED", args[1])
elif args and args[0] == "still":
    for fr in [int(a) for a in args[1:]]:
        S.frame_set(fr)
        S.camera = [m for m in sorted(S.timeline_markers, key=lambda m: m.frame) if m.frame <= fr][-1].camera
        S.render.filepath = OUT + f"still_{fr:03d}.png"; bpy.ops.render.render(write_still=True)
else:
    S.render.filepath = OUT + "f_"; bpy.ops.render.render(animation=True)
print("DONE")
