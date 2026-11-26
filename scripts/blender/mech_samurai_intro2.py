"""Cyber-samurai intro v2 (12 s action + 3 s Phillips Digital glitch added in post), 16:9, Cycles.
Uses the model's OWN katana + short sword (no modelled blade):
  darkness, the swords flicker on/off in lime -> the camera follows the katana from its tip to the hilt as the glow
  sweeps along it -> lights bang on -> section-by-section close-ups (hand, shoulder, chest, helmet + eyes) while the
  armour strips sweep up -> hero close-up.
  blender -b <base.blend from mech_samurai.py> -P scripts/blender/mech_samurai_intro2.py -- <out.blend>
"""
import bpy, sys, math
import numpy as np
from mathutils import Vector

CFG = dict(
    frames=360, res=(1920, 1080),
    sword_col=(0.42, 1.0, 0.02), sword_strength=6.0, sword_fill=0.10,
    sword_glow=[(1, 0.0), (14, 0.0), (15, 1.0), (17, 0.0), (24, 1.0), (25, 0.15), (27, 1.0), (33, 0.0), (41, 1.0), (43, 0.3),
                (44, 1.0), (52, 1.0), (54, 0.0), (60, 0.0), (61, 1.0), (360, 1.0)],          # on/off flicker, then stays on
    sword_sweep=[(1, 1.2), (60, 1.2), (61, -0.05), (132, 1.08), (360, 1.08)],                # 0 = tip, 1 = hilt
    bangs=dict(key=136, rim_L=140, rim_R=144, back_haze=148), dark_haze=0.03, haze_scale=0.28,
    bang_flicker=[(0, 1.25), (1, 0.0), (3, 0.9), (4, 0.15), (6, 1.0), (8, 0.05), (9, 0.85), (12, 0.2), (13, 1.0), (19, 0.3), (20, 1.0)],
    prehero_flicker=[(264, 1.0), (266, 0.15), (267, 1.0), (269, 0.0), (271, 0.7), (272, 0.0), (275, 1.0), (276, 0.1), (278, 0.0), (281, 1.15), (290, 1.0)],
    haze_col=(0.17, 0.25, 0.37), city_emit=0.45, world=(0.002, 0.003, 0.006),
    rim_spread=50, rim_scale=0.2,                                                      # narrow rim beams so they skim the armour, not the backdrop
    reveal=[(1, -0.4), (135, -0.4), (136, 1.05), (162, 1.45), (198, 1.63), (236, 1.76), (262, 2.4)], glow=[(1, 1.0), (360, 1.1)],   # reveal: each section lights while on screen
    eyes=[(1, 0.0), (258, 0.0), (260, 1.0), (262, 0.1), (265, 1.2), (267, 0.4), (270, 1.0), (360, 1.0)],
    visor=[(1, 0.0), (259, 0.0), (260, 0.25), (262, 0.02), (265, 0.3), (270, 0.15)],
    shots=[("DARK", 1), ("SWORD", 61), ("HAND", 136), ("SHOULDER", 171), ("CHEST", 206), ("HELMET", 241), ("HERO", 281)],
)
OUT = sys.argv[sys.argv.index("--") + 1:][0]
S = bpy.context.scene; S.frame_start, S.frame_end = 1, CFG["frames"]
S.render.resolution_x, S.render.resolution_y = CFG["res"]


def clear_anim(idb):
    if idb.animation_data: idb.animation_data_clear()


def key_socket(sock, pts, interp="BEZIER"):
    for fr, v in pts: sock.default_value = v; sock.keyframe_insert("default_value", frame=fr)


def world_verts(o):
    a = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); return (np.c_[a, np.ones(len(a))] @ M.T)[:, :3]


# ---------------- strips / eyes retimed ----------------
g = bpy.data.node_groups["LimeStrips"]; clear_anim(g)
for name in ("reveal", "glow", "eyes"): key_socket(g.nodes[name].outputs[0], CFG[name])
for fc in g.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = "LINEAR" if "eyes" in fc.data_path else "BEZIER"

# ---------------- lights: dark, then bang on with a flicker ----------------
for name, f0 in CFG["bangs"].items():
    L = bpy.data.objects[name].data; full = L.energy
    if L.animation_data and L.animation_data.action:
        full = max(k.co[1] for fc in L.animation_data.action.fcurves for k in fc.keyframe_points)
    clear_anim(L); base = CFG["dark_haze"] * full if name == "back_haze" else 0.0
    if name == "back_haze": full *= CFG["haze_scale"]
    if name.startswith("rim"): full *= CFG["rim_scale"]
    pts = [(1, base), (f0 - 1, base)] + [(f0 + df, max(base, full * v)) for df, v in CFG["bang_flicker"]]
    pts += [(fr, max(base, full * v)) for fr, v in CFG["prehero_flicker"]]          # all lights stutter before the hero reveal
    for fr, v in pts: L.energy = v; L.keyframe_insert("energy", frame=fr)
    for fc in L.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "CONSTANT"
# moodier background: darker cooler haze, dim city windows, near-black world
hm = bpy.data.materials["haze"]; next(n for n in hm.node_tree.nodes if n.type == "PRINCIPLED_VOLUME").inputs["Color"].default_value = (*CFG["haze_col"], 1)
cm = bpy.data.materials["city"]; cm.node_tree.nodes["Math"].inputs[1].default_value = CFG["city_emit"]
S.world.node_tree.nodes["Background"].inputs[0].default_value = (*CFG["world"], 1)
for n in ("rim_L", "rim_R"): bpy.data.objects[n].data.spread = math.radians(CFG["rim_spread"]); bpy.data.objects[n].visible_camera = False
vl = bpy.data.objects["visor"].data; clear_anim(vl)
for fr, v in CFG["visor"]: vl.energy = v; vl.keyframe_insert("energy", frame=fr)

# ---------------- the model's own swords light up ----------------
kat = world_verts(bpy.data.objects["Object_19"]); c = kat - kat.mean(0)
ax = np.linalg.svd(c[::4], full_matrices=False)[2][0]
if ax @ np.array([0.14, -0.86, 0.49]) < 0: ax = -ax                                   # axis points tip -> hilt
proj = c @ ax; hilt = Vector(kat[np.argmax(proj)].tolist()); tip = Vector(kat[np.argmin(proj)].tolist())
p0, p1 = float(kat[np.argmin(proj)] @ ax), float(kat[np.argmax(proj)] @ ax)
print("katana tip", tip, "hilt", hilt)

sg = bpy.data.node_groups.new("SwordGlow", "ShaderNodeTree")
sg.interface.new_socket("Strength", in_out="OUTPUT", socket_type="NodeSocketFloat")
N = sg.nodes; Lk = sg.links.new; go = N.new("NodeGroupOutput")
geo = N.new("ShaderNodeNewGeometry"); bev = N.new("ShaderNodeBevel"); bev.samples = 8; bev.inputs["Radius"].default_value = 0.004
dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; Lk(bev.outputs[0], dot.inputs[0]); Lk(geo.outputs["Normal"], dot.inputs[1])
edge = N.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.94; edge.inputs["From Max"].default_value = 0.80
edge.inputs["To Min"].default_value = CFG["sword_fill"]; edge.inputs["To Max"].default_value = 1.0; Lk(dot.outputs["Value"], edge.inputs["Value"])
axv = N.new("ShaderNodeVectorMath"); axv.operation = "DOT_PRODUCT"; Lk(geo.outputs["Position"], axv.inputs[0]); axv.inputs[1].default_value = tuple(float(v) for v in ax)
pos = N.new("ShaderNodeMapRange"); pos.inputs["From Min"].default_value = p0; pos.inputs["From Max"].default_value = p1; pos.clamp = False
Lk(axv.outputs["Value"], pos.inputs["Value"])                                           # 0 at the tip, 1 at the hilt
sw = N.new("ShaderNodeValue"); sw.name = sw.label = "sweep"; gl = N.new("ShaderNodeValue"); gl.name = gl.label = "glow"
dif = N.new("ShaderNodeMath"); dif.operation = "SUBTRACT"; Lk(sw.outputs[0], dif.inputs[0]); Lk(pos.outputs[0], dif.inputs[1])
on = N.new("ShaderNodeMapRange"); on.inputs["From Min"].default_value = 0.0; on.inputs["From Max"].default_value = 0.03; Lk(dif.outputs[0], on.inputs["Value"])
hot = N.new("ShaderNodeMapRange"); hot.inputs["From Min"].default_value = 0.08; hot.inputs["From Max"].default_value = 0.0
hot.inputs["To Min"].default_value = 1.0; hot.inputs["To Max"].default_value = 3.5; Lk(dif.outputs[0], hot.inputs["Value"])   # hot front on the sweep
m = [N.new("ShaderNodeMath") for _ in range(4)]
for x in m: x.operation = "MULTIPLY"
Lk(edge.outputs[0], m[0].inputs[0]); Lk(on.outputs[0], m[0].inputs[1]); Lk(m[0].outputs[0], m[1].inputs[0]); Lk(hot.outputs[0], m[1].inputs[1])
Lk(m[1].outputs[0], m[2].inputs[0]); Lk(gl.outputs[0], m[2].inputs[1]); Lk(m[2].outputs[0], m[3].inputs[0]); m[3].inputs[1].default_value = CFG["sword_strength"]
Lk(m[3].outputs[0], go.inputs["Strength"])
key_socket(sw.outputs[0], CFG["sword_sweep"]); key_socket(gl.outputs[0], CFG["sword_glow"])
for fc in sg.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = "CONSTANT" if "glow" in fc.data_path else "BEZIER"

for nm in ("Object_19", "Object_20"):
    o = bpy.data.objects[nm]; mat = o.data.materials[0].copy(); mat.name = "sword_" + nm; o.data.materials[0] = mat
    nt = mat.node_tree; P = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    es = P.inputs["Emission Strength"]; src = es.links[0].from_socket if es.links else None
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = sg
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    if src: nt.links.new(src, add.inputs[0])
    nt.links.new(gn.outputs["Strength"], add.inputs[1]); nt.links.new(add.outputs[0], es)
    if not P.inputs["Emission Color"].links: P.inputs["Emission Color"].default_value = (*CFG["sword_col"], 1)
sl = bpy.data.lights.new("sword_light", "AREA"); sl.shape = "RECTANGLE"; sl.size = 1.2; sl.size_y = 0.05; sl.color = CFG["sword_col"]
slo = bpy.data.objects.new("sword_light", sl); S.collection.objects.link(slo)
mid = (hilt + tip) / 2; slo.location = mid + Vector((0.08, -0.05, 0.08)); slo.rotation_mode = "QUATERNION"
slo.rotation_quaternion = (hilt - tip).normalized().to_track_quat("X", "Z")
for fr, v in CFG["sword_glow"]: sl.energy = 14 * v; sl.keyframe_insert("energy", frame=fr)
for fc in sl.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = "CONSTANT"

# ---------------- floor (for wide moments) ----------------
lo_z = min(float(world_verts(o)[:, 2].min()) for o in S.objects if o.type == "MESH" and o.name.startswith("Object_") and len(o.data.vertices))
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 4, lo_z)); fl = bpy.context.object; fl.name = "floor"
fm = bpy.data.materials.new("wet_floor"); fm.use_nodes = True; fn = fm.node_tree; fb = fn.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.012, 0.014, 0.018, 1); fb.inputs["Roughness"].default_value = 0.2; fl.data.materials.append(fm)

# ---------------- cameras + cuts ----------------
old = S.camera
def make_cam(name, lens, fstop, focus_pt):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, cd); S.collection.objects.link(o)
    fe = bpy.data.objects.new(name + "_focus", None); S.collection.objects.link(fe); fe.location = focus_pt; cd.dof.focus_object = fe
    return o, fe
def aim(o, pos, tgt, fr):
    o.location = pos; o.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    o.keyframe_insert("location", frame=fr); o.keyframe_insert("rotation_euler", frame=fr)
def handheld(o, s=0.0025):
    for fc in o.animation_data.action.fcurves:
        for kk in fc.keyframe_points: kk.interpolation = "BEZIER"; kk.easing = "AUTO"
        mo = fc.modifiers.new("NOISE"); mo.scale = 45; mo.strength = s if fc.data_path == "location" else s * 0.4; mo.phase = fc.array_index * 11 + len(o.name)

V = lambda *a: Vector(a)
face = V(0.0, -0.08, 1.82); handR = V(-0.455, -0.30, 1.34); shL = V(0.44, -0.04, 1.62); chest = V(0.0, -0.13, 1.42)
# 1 DARK: the swords flicker on/off in darkness (3/4 view of the hip)
c, f = make_cam("DARK", 50, 2.8, (hilt + tip) / 2)
aim(c, mid + V(1.35, -1.05, 0.35), mid, 1); aim(c, mid + V(1.20, -0.92, 0.30), mid, 60); handheld(c, 0.0015)
# 2 SWORD: follow the katana from its tip to the hilt as the glow sweeps
c, f = make_cam("SWORD", 35, 2.4, tip)
side = Vector(ax.tolist()).cross(V(0, 0, 1)).normalized()
if side.x < 0: side = -side                                                              # stay on the outside of the body
for fr in range(61, 136, 5):
    t = min(1.0, max(0.0, (fr - 61) / 71)); t = t * t * (3 - 2 * t)
    p = tip.lerp(hilt, min(1.0, t * 0.95 + 0.02)); q = tip.lerp(hilt, min(1.06, t * 0.95 + 0.14))
    aim(c, p + side * 0.30 + V(0, 0, 0.14), q, fr); f.location = q; f.keyframe_insert("location", frame=fr)
handheld(c, 0.002)
# 3 HAND (right hand, fingers light up as the strips sweep)
c, f = make_cam("HAND", 85, 2.4, handR)
aim(c, handR + V(-0.55, -0.80, 0.10), handR, 136); aim(c, handR + V(-0.38, -0.86, 0.14), handR, 170); handheld(c, 0.002)
# 4 SHOULDER (left shoulder plates, slow slide up)
c, f = make_cam("SHOULDER", 85, 2.8, shL)
aim(c, shL + V(0.95, -0.55, -0.05), shL, 171); aim(c, shL + V(0.78, -0.78, 0.10), shL + V(-0.05, 0, 0.02), 205); handheld(c, 0.002)
# 5 CHEST (low angle sliding across the chest)
c, f = make_cam("CHEST", 50, 2.8, chest)
aim(c, chest + V(0.42, -0.70, -0.20), chest + V(0, 0, 0.04), 206); aim(c, chest + V(-0.36, -0.74, -0.12), chest + V(0, 0, 0.08), 240); handheld(c)
# 6 HELMET (profile -> front as the eyes ignite)
c, f = make_cam("HELMET", 85, 2.8, face)
aim(c, face + V(-0.95, -0.62, 0.05), face, 241); aim(c, face + V(-0.35, -1.05, 0.02), face, 280); handheld(c, 0.002)
# 7 HERO close-up: chest-up, nearly frontal, slow push
c, f = make_cam("HERO", 70, 2.8, face)
aim(c, V(0.35, -2.75, 1.86), V(0.05, 0, 1.58), 281); aim(c, V(0.22, -2.30, 1.84), V(0.03, 0, 1.60), 360); handheld(c, 0.002)
for nm, fr in CFG["shots"]:
    mk = S.timeline_markers.new(nm, frame=fr); mk.camera = bpy.data.objects[nm]
if old: bpy.data.objects.remove(old, do_unlink=True)
S.camera = bpy.data.objects["DARK"]
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=False); print("saved", OUT)
