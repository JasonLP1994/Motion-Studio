"""Cyber-samurai intro (12 s action + 3 s Phillips Digital glitch added in post), 16:9, Cycles.
Builds on the base scene from mech_samurai.py: darkness -> lime eyes -> lights bang on -> armour strips sweep on ->
hilt close-up -> lime energy blade grows out of the hilt with the camera riding it to the tip -> glint -> pull back to
the full-body hero shot. Writes <out>.blend plus <out>.tip.json (blade-tip screen positions for the glint in post).
  blender -b <base.blend> -P scripts/blender/mech_samurai_intro.py -- <out.blend>
"""
import bpy, sys, math, json
import numpy as np
from mathutils import Vector

CFG = dict(
    frames=360, res=(1920, 1080),
    eyes=[(1, 0.0), (38, 0.0), (40, 1.0), (42, 0.1), (45, 1.2), (47, 0.4), (50, 1.0), (360, 1.0)],
    bangs=dict(key=74, rim_L=80, rim_R=84, back_haze=88),             # lights switching on (frame)
    dark_haze=0.03, haze_scale=0.6,                                     # back light after the bang, x base level                                                    # back light level before the bangs (silhouette)
    reveal=[(1, -0.4), (92, -0.4), (130, 2.4)], glow=[(1, 1.0), (178, 1.0), (182, 1.8), (190, 1.1), (360, 1.1)],
    blade_len=1.0, blade_w=0.052, blade_dir=(0.55, -0.32, 0.77), grow=(180, 222), blade_col=(0.42, 1.0, 0.02), blade_emit=5.0,
    floor_z=None,
    shots=[("ECU_EYES", 1), ("CHEST", 71), ("HILT", 131), ("BLADE", 176), ("HERO", 241)],
)
OUT = sys.argv[sys.argv.index("--") + 1:][0]
S = bpy.context.scene; S.frame_start, S.frame_end = 1, CFG["frames"]
S.render.resolution_x, S.render.resolution_y = CFG["res"]


def keyset(owner, path, pts, interp="BEZIER"):
    ad = owner.id_data.animation_data if hasattr(owner, "id_data") else None
    for fr, v in pts: setattr(owner, path, v); owner.keyframe_insert(path, frame=fr)


def clear_anim(idb):
    if idb.animation_data: idb.animation_data_clear()


def ease(fcurves, kind="BEZIER"):
    for fc in fcurves:
        for k in fc.keyframe_points: k.interpolation = kind; k.easing = "AUTO"


# ---------------- strips / eyes retimed ----------------
g = bpy.data.node_groups["LimeStrips"]; clear_anim(g)
for name, pts in (("reveal", CFG["reveal"]), ("glow", CFG["glow"]), ("eyes", CFG["eyes"])):
    sock = g.nodes[name].outputs[0]
    for fr, v in pts: sock.default_value = v; sock.keyframe_insert("default_value", frame=fr)
for fc in g.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = "LINEAR" if "eyes" in fc.data_path else "BEZIER"

# ---------------- lights: dark, then bang on with a flicker ----------------
for name, f0 in CFG["bangs"].items():
    L = bpy.data.objects[name].data; full = L.energy if not L.animation_data else None
    if L.animation_data and L.animation_data.action:
        full = max(k.co[1] for fc in L.animation_data.action.fcurves for k in fc.keyframe_points)
    clear_anim(L); base = CFG["dark_haze"] * full if name == "back_haze" else 0.0
    if name == "back_haze": full *= CFG["haze_scale"]
    pts = [(1, base), (f0 - 1, base), (f0, full * 1.25), (f0 + 1, base), (f0 + 3, full * 0.9), (f0 + 4, full * 0.3), (f0 + 6, full)]
    for fr, v in pts: L.energy = v; L.keyframe_insert("energy", frame=fr)
    for fc in L.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = "CONSTANT"
vl = bpy.data.objects["visor"].data; clear_anim(vl)
for fr, v in [(1, 0.0), (39, 0.0), (40, 0.25), (42, 0.02), (45, 0.3), (50, 0.15)]: vl.energy = v; vl.keyframe_insert("energy", frame=fr)

# ---------------- model geometry landmarks ----------------
def world_verts(o):
    a = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); return (np.c_[a, np.ones(len(a))] @ M.T)[:, :3]
kat = world_verts(bpy.data.objects["Object_19"])
c = kat - kat.mean(0); ax = np.linalg.svd(c[::4], full_matrices=False)[2][0]
fwd = np.array([0.14, -0.86, 0.49]); ax = ax if ax @ fwd > 0 else -ax                # axis pointing to the hilt end (forward-up)
hilt = kat[np.argmax(c @ ax)]; hilt = Vector(hilt.tolist())
lo_z = min(float(world_verts(o)[:, 2].min()) for o in S.objects if o.type == "MESH" and o.name.startswith("Object_") and len(o.data.vertices))
print("hilt end", hilt, "floor", lo_z)

# ---------------- floor: wet dark concrete ----------------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 4, lo_z)); fl = bpy.context.object; fl.name = "floor"
fm = bpy.data.materials.new("wet_floor"); fm.use_nodes = True; fn = fm.node_tree; fb = fn.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.012, 0.014, 0.018, 1)
nz = fn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6
rr = fn.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.06; rr.inputs["To Max"].default_value = 0.45
fn.links.new(nz.outputs["Fac"], rr.inputs["Value"]); fn.links.new(rr.outputs[0], fb.inputs["Roughness"])
bm = fn.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.08; fn.links.new(nz.outputs["Fac"], bm.inputs["Height"]); fn.links.new(bm.outputs[0], fb.inputs["Normal"])
fl.data.materials.append(fm)

# ---------------- energy blade ----------------
L, Wd = CFG["blade_len"], CFG["blade_w"]; n = 48; verts = []; faces = []
for i in range(n + 1):
    t = i / n; y = t * L; bend = 0.075 * t * t                                          # gentle katana curve
    w = Wd * (1 - t ** 9) * (0.82 + 0.18 * (1 - t)) if t < 0.97 else Wd * 0.3 * (1 - t) / 0.03; th = 0.006 * (1 - t ** 4) + 0.001
    verts += [(-w / 2, y, bend), (w / 2, y, bend + w * 0.25), (0, y, bend + th), (0, y, bend - th)]
for i in range(n):
    a = i * 4; b = a + 4
    for j0, j1 in ((0, 2), (2, 1), (1, 3), (3, 0)): faces.append((a + j0, a + j1, b + j1, b + j0))
me = bpy.data.meshes.new("blade"); me.from_pydata(verts, [], faces); me.update()
bl = bpy.data.objects.new("blade", me); S.collection.objects.link(bl)
for p in me.polygons: p.use_smooth = True
d = Vector(CFG["blade_dir"]).normalized()
bl.location = hilt; bl.rotation_mode = "QUATERNION"; bl.rotation_quaternion = d.to_track_quat("Y", "Z")
bmat = bpy.data.materials.new("energy_blade"); bmat.use_nodes = True; bn = bmat.node_tree
for nd in list(bn.nodes):
    if nd.type != "OUTPUT_MATERIAL": bn.nodes.remove(nd)
em = bn.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*CFG["blade_col"], 1)
tcb = bn.nodes.new("ShaderNodeTexCoord"); sx = bn.nodes.new("ShaderNodeSeparateXYZ"); bn.links.new(tcb.outputs["Generated"], sx.inputs[0])
edge = bn.nodes.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.70; edge.inputs["From Max"].default_value = 1.0   # cutting edge = +x side
edge.inputs["To Min"].default_value = CFG["blade_emit"] * 0.45; edge.inputs["To Max"].default_value = CFG["blade_emit"] * 2.4
bn.links.new(sx.outputs["X"], edge.inputs["Value"]); bn.links.new(edge.outputs[0], em.inputs["Strength"])
bn.links.new(em.outputs[0], bn.nodes["Material Output"].inputs["Surface"]); me.materials.append(bmat)
g0, g1 = CFG["grow"]
for fr, sy in [(1, 0.001), (g0, 0.001), (g0 + 4, 0.18), (g1, 1.0)]:
    bl.scale = (1, sy, 1); bl.keyframe_insert("scale", frame=fr)
bl.hide_render = True; bl.keyframe_insert("hide_render", frame=g0 - 1); bl.hide_render = False; bl.keyframe_insert("hide_render", frame=g0)
for fc in bl.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_OUT"
bll = bpy.data.lights.new("blade_light", "POINT"); bll.color = CFG["blade_col"]; bll.shadow_soft_size = 0.3
blo = bpy.data.objects.new("blade_light", bll); S.collection.objects.link(blo); blo.location = hilt + d * (L * 0.5)
for fr, e in [(1, 0), (g0, 0), (g0 + 6, 25), (g1, 60), (360, 55)]: bll.energy = e; bll.keyframe_insert("energy", frame=fr)
tip = hilt + d * L

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
def handheld(o, s=0.003):
    for fc in o.animation_data.action.fcurves:
        k = fc.keyframe_points
        for kk in k: kk.interpolation = "BEZIER"; kk.easing = "AUTO"
        m = fc.modifiers.new("NOISE"); m.scale = 45; m.strength = s if fc.data_path == "location" else s * 0.4; m.phase = fc.array_index * 11 + len(o.name)

face = Vector((0.0, -0.08, 1.82))
c1, f1 = make_cam("ECU_EYES", 100, 2.8, face)
aim(c1, face + Vector((0.18, -1.35, 0.03)), face, 1); aim(c1, face + Vector((0.12, -1.05, 0.02)), face, 70); handheld(c1, 0.002)
chest = Vector((0.04, -0.06, 1.48))
c2, f2 = make_cam("CHEST", 40, 2.8, chest + Vector((0, -0.1, 0)))
aim(c2, chest + Vector((0.62, -0.78, -0.18)), chest + Vector((0.05, 0, 0.05)), 71); aim(c2, chest + Vector((-0.38, -0.86, -0.08)), chest + Vector((-0.02, 0, 0.12)), 130); handheld(c2)
c3, f3 = make_cam("HILT", 85, 2.2, hilt)
aim(c3, hilt + Vector((0.72, -0.62, 0.10)), hilt, 131); aim(c3, hilt + Vector((0.58, -0.55, 0.06)), hilt + d * 0.05, 175); handheld(c3, 0.002)
c4, f4 = make_cam("BLADE", 32, 2.8, hilt)
side = d.cross(Vector((0, 0, 1))).normalized(); off = Vector((0.38, -0.78, -0.12))    # in front, so the armour sits behind the blade
for k, fr in enumerate(range(176, 241, 4)):
    t = min(1.0, max(0.0, (fr - g0) / (g1 - g0))); t = 1 - (1 - t) ** 2.2
    p = hilt + d * (L * (0.12 + 0.88 * t) - 0.18)
    aim(c4, p + off, p + d * 0.06, fr); f4.location = p + d * 0.14; f4.keyframe_insert("location", frame=fr)
handheld(c4, 0.0025)
c5, f5 = make_cam("HERO", 50, 4.0, Vector((0.05, -0.1, 1.2)))
aim(c5, tip + side * -0.32 + Vector((0, -0.18, 0.04)), tip, 241); aim(c5, tip + side * -0.30 + Vector((0, -0.2, 0.03)), tip, 268)
aim(c5, Vector((0.9, -5.4, 0.55)), Vector((0.1, 0.0, 1.1)), 318); aim(c5, Vector((0.6, -5.0, 0.5)), Vector((0.1, 0.0, 1.12)), 360)
f5.location = tip; f5.keyframe_insert("location", frame=241); f5.keyframe_insert("location", frame=268)
f5.location = Vector((0.05, -0.1, 1.2)); f5.keyframe_insert("location", frame=318)
handheld(c5, 0.0025)
for nm, fr in CFG["shots"]:
    mk = S.timeline_markers.new(nm, frame=fr); mk.camera = bpy.data.objects[nm]
if old: bpy.data.objects.remove(old, do_unlink=True)
S.camera = bpy.data.objects["ECU_EYES"]

# ---------------- blade-tip screen positions for the glint (post) ----------------
from bpy_extras.object_utils import world_to_camera_view
tips = {}
for fr in range(236, 281):
    S.frame_set(fr); camo = [m.camera for m in sorted(S.timeline_markers, key=lambda m: m.frame) if m.frame <= fr][-1]
    tp = bl.matrix_world @ Vector((0, L, 0.045))
    v = world_to_camera_view(S, camo, tp); tips[fr] = [v.x, 1 - v.y, v.z]
json.dump(tips, open(OUT.replace(".blend", ".tip.json"), "w"))
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=False); print("saved", OUT)
