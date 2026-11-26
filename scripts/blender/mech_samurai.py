"""Cyber-samurai mech reveal (10 s, 30 fps), Cycles. Licensed model ("Cyber Samurai" by duongminhkhoa231, CC-BY 4.0,
Sketchfab 26ccafaddb2745ceb56ae5cfc65bfed5 via Objaverse) restyled to the reference grammar: matte gunmetal armour,
thin glowing strips along the panel edges (Phillips lime), cold blue haze, out-of-focus city, low soft key, cool rims.
  blender -b -P scripts/blender/mech_samurai.py -- <model.glb> <out.blend>
Everything tweakable lives in CFG.
"""
import bpy, sys, math, random
from mathutils import Vector

CFG = dict(
    frames=300, fps=30, res=(1080, 1350),          # vertical 4:5 portrait like the reference
    lime=(0.62, 1.0, 0.02), strip_strength=10.0, edge_radius=0.006, edge_thresh=(0.13, 0.26),
    patch_scale=2.2, patch_cut=0.56,                       # which edges glow (noise patches): higher cut = fewer strips
    armour=(0.020, 0.022, 0.026), armour_tex=0.12, armour_rough=(0.42, 0.70), armour_metal=0.55,
    robe_dark=0.12,
    reveal=[(1, 0.9), (60, 0.9), (150, 2.35)], band=0.06, glow=[(1, 1.0), (158, 1.0), (160, 2.6), (166, 0.7), (170, 1.15), (300, 1.15)],
    visor=[(1, 0.0), (158, 0.0), (160, 2.5), (166, 0.6), (300, 0.7)],
    haze_density=0.05, haze_col=(0.30, 0.44, 0.62), back_energy=110, rim_energy=(900, 650), key_energy=140,
    rim_in=[(1, 0.0), (45, 1.0)],
    cam_lens=85, fstop=2.8,
    cam=[(1, (0.0, 1.64), 1.85, 14.0), (170, (0.0, 1.70), 1.55, 12.0), (300, (0.0, 1.71), 1.48, 9.0)],   # (frame, (x,z) target, dist, orbit deg): tight close-up, helmet top cropped
    cam_up=0.22, cam_shift_x=-0.26,                      # negative = subject sits on the right side of the frame                                          # camera a little above the target, looking slightly down
    exposure=0.0,
)
argv = sys.argv[sys.argv.index("--") + 1:]; SRC, OUT = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.render.engine = "CYCLES"; S.cycles.device = "CPU"
S.frame_start, S.frame_end = 1, CFG["frames"]; S.render.fps = CFG["fps"]
S.render.resolution_x, S.render.resolution_y = CFG["res"]; S.render.resolution_percentage = 100
S.cycles.samples = 64; S.cycles.use_denoising = False; S.cycles.max_bounces = 6; S.cycles.volume_step_rate = 6
S.cycles.transparent_max_bounces = 16
S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Medium High Contrast"; S.view_settings.exposure = CFG["exposure"]


def keys(owner, path, pts, idx=-1):
    for fr, v in pts:
        if idx >= 0: getattr(owner, path)[idx] = v; owner.keyframe_insert(path, index=idx, frame=fr)
        else: setattr(owner, path, v); owner.keyframe_insert(path, frame=fr)


def smooth_all(id_):
    ad = id_.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "AUTO"


# ---------------- model ----------------
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in S.objects if o.type == "MESH"]

# lime strip group: edge mask (bevel vs normal) x noise patches x reveal height, plus a hot band on the reveal front
g = bpy.data.node_groups.new("LimeStrips", "ShaderNodeTree")
g.interface.new_socket("Emission", in_out="OUTPUT", socket_type="NodeSocketColor")
g.interface.new_socket("Strength", in_out="OUTPUT", socket_type="NodeSocketFloat")
N = g.nodes; Lk = g.links.new
go = N.new("NodeGroupOutput")
bev = N.new("ShaderNodeBevel"); bev.samples = 8; bev.inputs["Radius"].default_value = CFG["edge_radius"]
geo = N.new("ShaderNodeNewGeometry")
dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; Lk(bev.outputs[0], dot.inputs[0]); Lk(geo.outputs["Normal"], dot.inputs[1])
edge = N.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 1 - CFG["edge_thresh"][0]; edge.inputs["From Max"].default_value = 1 - CFG["edge_thresh"][1]
Lk(dot.outputs["Value"], edge.inputs["Value"])
tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = CFG["patch_scale"]; nz.inputs["Detail"].default_value = 1.0
Lk(tc.outputs["Object"], nz.inputs["Vector"])
pc = N.new("ShaderNodeMapRange"); pc.inputs["From Min"].default_value = CFG["patch_cut"]; pc.inputs["From Max"].default_value = CFG["patch_cut"] + 0.02
Lk(nz.outputs["Fac"], pc.inputs["Value"])
sep = N.new("ShaderNodeSeparateXYZ"); Lk(geo.outputs["Position"], sep.inputs[0])
rv = N.new("ShaderNodeValue"); rv.name = rv.label = "reveal"
dz = N.new("ShaderNodeMath"); dz.operation = "SUBTRACT"; Lk(rv.outputs[0], dz.inputs[0]); Lk(sep.outputs["Z"], dz.inputs[1])   # >0 below the front
on = N.new("ShaderNodeMath"); on.operation = "GREATER_THAN"; on.inputs[1].default_value = 0.0; Lk(dz.outputs[0], on.inputs[0])
hb = N.new("ShaderNodeMapRange"); hb.inputs["From Min"].default_value = CFG["band"]; hb.inputs["From Max"].default_value = 0.0
hb.inputs["To Min"].default_value = 1.0; hb.inputs["To Max"].default_value = 5.0; Lk(dz.outputs[0], hb.inputs["Value"])
gl = N.new("ShaderNodeValue"); gl.name = gl.label = "glow"
m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; Lk(edge.outputs[0], m1.inputs[0]); Lk(pc.outputs[0], m1.inputs[1])
m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; Lk(m1.outputs[0], m2.inputs[0]); Lk(on.outputs[0], m2.inputs[1])
m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; Lk(m2.outputs[0], m3.inputs[0]); Lk(hb.outputs[0], m3.inputs[1])
m4 = N.new("ShaderNodeMath"); m4.operation = "MULTIPLY"; Lk(m3.outputs[0], m4.inputs[0]); Lk(gl.outputs[0], m4.inputs[1])
m5 = N.new("ShaderNodeMath"); m5.operation = "MULTIPLY"; m5.inputs[1].default_value = CFG["strip_strength"]; Lk(m4.outputs[0], m5.inputs[0])
col = N.new("ShaderNodeRGB"); col.outputs[0].default_value = (*CFG["lime"], 1)
Lk(col.outputs[0], go.inputs["Emission"]); Lk(m5.outputs[0], go.inputs["Strength"])
keys(rv.outputs[0], "default_value", CFG["reveal"]); keys(gl.outputs[0], "default_value", CFG["glow"])

for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree; P = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if P is None: continue
    bc = P.inputs["Base Color"]; src = bc.links[0].from_socket if bc.links else None
    if m.name.startswith("Robe"):
        if src:
            mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
            mul.inputs[2].default_value = (CFG["robe_dark"],) * 3 + (1,); nt.links.new(src, mul.inputs[1]); nt.links.new(mul.outputs[0], bc)
        continue
    # armour: desaturate, darken to gunmetal, satin roughness, metal-ish; keep the texture's panel detail
    if src:
        hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 0.0; nt.links.new(src, hs.inputs["Color"])
        mix = nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "ADD"; mix.inputs[0].default_value = 1.0
        mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0; mul.inputs[2].default_value = (CFG["armour_tex"],) * 3 + (1,)
        nt.links.new(hs.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], mix.inputs[1]); mix.inputs[2].default_value = (*CFG["armour"], 1)
        nt.links.new(mix.outputs[0], bc)
    else: bc.default_value = (*CFG["armour"], 1)
    rr = P.inputs["Roughness"]
    if rr.links:
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = CFG["armour_rough"]
        nt.links.new(rr.links[0].from_socket, mr.inputs["Value"]); nt.links.new(mr.outputs[0], rr)
    else: rr.default_value = sum(CFG["armour_rough"]) / 2
    mt = P.inputs["Metallic"]
    for l in list(mt.links): nt.links.remove(l)
    mt.default_value = CFG["armour_metal"]
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = g
    nt.links.new(gn.outputs["Emission"], P.inputs["Emission Color"]); nt.links.new(gn.outputs["Strength"], P.inputs["Emission Strength"])
smooth_all(g)

# model bounds
lo = Vector((1e9,) * 3); hi = -lo
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
print("model bbox", lo, hi)

# ---------------- world, haze, city ----------------
W = bpy.data.worlds.new("night"); S.world = W; W.use_nodes = True
W.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.007, 0.012, 1); W.node_tree.nodes["Background"].inputs[1].default_value = 1.0

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 21.5, 9)); hz = bpy.context.object; hz.name = "haze"; hz.scale = (70, 40, 20)   # starts 1.5 m behind the model
hm = bpy.data.materials.new("haze"); hm.use_nodes = True; hn = hm.node_tree
hn.nodes.remove(hn.nodes["Principled BSDF"]); pv = hn.nodes.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (*CFG["haze_col"], 1); pv.inputs["Anisotropy"].default_value = 0.35
nzv = hn.nodes.new("ShaderNodeTexNoise"); nzv.inputs["Scale"].default_value = 0.35; nzv.inputs["Detail"].default_value = 3
dm = hn.nodes.new("ShaderNodeMapRange"); dm.inputs["To Min"].default_value = CFG["haze_density"] * 0.3; dm.inputs["To Max"].default_value = CFG["haze_density"] * 1.6
hn.links.new(nzv.outputs["Fac"], dm.inputs["Value"]); hn.links.new(dm.outputs[0], pv.inputs["Density"])
mp = hn.nodes.new("ShaderNodeMapping"); tcv = hn.nodes.new("ShaderNodeTexCoord"); hn.links.new(tcv.outputs["Object"], mp.inputs["Vector"]); hn.links.new(mp.outputs[0], nzv.inputs["Vector"])
keys(mp.inputs["Location"], "default_value", [(1, 0.0), (300, 0.08)], idx=0)                       # haze drifts sideways
hn.links.new(pv.outputs[0], hn.nodes["Material Output"].inputs["Volume"]); hz.data.materials.append(hm)

wm = bpy.data.materials.new("city"); wm.use_nodes = True; wn = wm.node_tree; wb = wn.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value = (0.02, 0.03, 0.045, 1); wb.inputs["Roughness"].default_value = 0.8
br = wn.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.25
br.inputs["Brick Width"].default_value = 1.4; br.inputs["Row Height"].default_value = 1.2; br.offset = 0.0
br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (0.0, 0.0, 0.0, 1); br.inputs["Mortar"].default_value = (0, 0, 0, 1)
tcw = wn.nodes.new("ShaderNodeTexCoord"); wn.links.new(tcw.outputs["Object"], br.inputs["Vector"])
wr = wn.nodes.new("ShaderNodeMath"); wr.operation = "MULTIPLY"; wr.inputs[1].default_value = 1.2; wn.links.new(br.outputs["Fac"], wr.inputs[0])
wn.links.new(wr.outputs[0], wb.inputs["Emission Strength"]); wb.inputs["Emission Color"].default_value = (0.45, 0.62, 0.85, 1)
rng = random.Random(5)
for i in range(46):
    x = rng.uniform(-26, 26); y = rng.uniform(24, 58); h = rng.uniform(10, 44); wdt = rng.uniform(1.2, 3.2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h / 2 - 2)); b = bpy.context.object; b.scale = (wdt, wdt * 0.8, h); b.data.materials.append(wm)

# ---------------- lights ----------------
def area(name, loc, rot, size, energy, color):
    L = bpy.data.lights.new(name, "AREA"); L.size = size; L.energy = energy; L.color = color
    o = bpy.data.objects.new(name, L); S.collection.objects.link(o); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]; return o, L
cz = (lo.z + hi.z) / 2
_, kL = area("key", (-1.6, -2.4, 2.9), (55, 0, -32), 1.2, CFG["key_energy"], (0.85, 0.9, 1.0))
_, bL = area("back_haze", (0.4, 8.0, 1.2), (-90, 0, 0), 8.0, CFG["back_energy"], (0.55, 0.72, 1.0))
_, r1 = area("rim_L", (-1.7, 1.6, 2.4), (65, 0, -135), 0.8, CFG["rim_energy"][0], (0.6, 0.78, 1.0))
_, r2 = area("rim_R", (1.8, 1.5, 2.2), (65, 0, 135), 0.8, CFG["rim_energy"][1], (0.75, 0.85, 1.0))
for L, e in ((bL, CFG["back_energy"]), (r1, CFG["rim_energy"][0]), (r2, CFG["rim_energy"][1])):
    keys(L, "energy", [(f, e * v) for f, v in CFG["rim_in"]]); smooth_all(L)
vl = bpy.data.lights.new("visor", "POINT"); vl.color = CFG["lime"]; vl.shadow_soft_size = 0.05
vo = bpy.data.objects.new("visor", vl); S.collection.objects.link(vo); vo.location = (0.0, -0.20, 1.82)
keys(vl, "energy", CFG["visor"]); smooth_all(vl)

# ---------------- camera ----------------
cam = bpy.data.cameras.new("cam"); cam.lens = CFG["cam_lens"]; cam.shift_x = CFG["cam_shift_x"]; cam.dof.use_dof = True; cam.dof.aperture_fstop = CFG["fstop"]
co = bpy.data.objects.new("cam", cam); S.collection.objects.link(co); S.camera = co
fe = bpy.data.objects.new("focus", None); S.collection.objects.link(fe); cam.dof.focus_object = fe
for fr, (tx, tz), dist, orb in CFG["cam"]:
    a = math.radians(orb); t = Vector((tx, 0.05, tz))
    co.location = t + Vector((math.sin(a) * dist, -math.cos(a) * dist, CFG["cam_up"])); co.rotation_euler = (t - co.location).to_track_quat("-Z", "Y").to_euler()
    co.keyframe_insert("location", frame=fr); co.keyframe_insert("rotation_euler", frame=fr)
    fe.location = Vector((0.0, -0.08, 1.84)); fe.keyframe_insert("location", frame=fr)   # focus locked on the visor
for ob in (co, fe):
    for fc in ob.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "AUTO"
for fc in co.animation_data.action.fcurves:                                          # faint handheld breathing
    m = fc.modifiers.new("NOISE"); m.scale = 60; m.strength = 0.004 if fc.data_path == "location" else 0.0015; m.phase = fc.array_index * 7

# ---------------- compositor: bloom for the strips ----------------
S.use_nodes = True; ct = S.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers"); gz = ct.nodes.new("CompositorNodeGlare"); cp = ct.nodes.new("CompositorNodeComposite")
gz.glare_type = "FOG_GLOW"; gz.quality = "HIGH"; gz.threshold = 0.9; gz.size = 8; gz.mix = -0.72
ct.links.new(rl.outputs["Image"], gz.inputs["Image"]); ct.links.new(gz.outputs["Image"], cp.inputs["Image"])

bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=False)
print("saved", OUT)
