# Grillz on the user's Genesis 8 Male scene (inputs/grillz/model2/TSST.blend, cm units, separate tooth objects).
# The mouth frame comes from the teeth themselves (PCA: side / forward / up), each tooth row is measured in that frame (height,
# width, front arch), and "PHILLIPS" / "MOTION" are built as chunky gold letters with puffy emerald faces pressed onto the teeth.
# Warm low-key macro lighting after the user's references; scene clutter hidden, black world.
#   PYTHONPATH=tools/py312 blender -b inputs/grillz/model2/TSST.blend -P work/grillz2/grillz2.py -- save OUT.blend
import bpy, math, os, sys
import numpy as np
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
E = lambda k, d: float(os.environ.get(k, d))
R = "/home/user/Motion-Studio/"
S = bpy.context.scene
# ---- hide clutter and the duplicate (earlier silver) teeth
for o in bpy.data.objects:
    if o.name.startswith(("Grass", "Ground", "Rock", "Plane.00", "Sphere", "NurbsPath")) or o.type == 'LIGHT':
        o.hide_render = True; o.hide_viewport = True
TEETH = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith("Genesis8Male.0") and len(o.data.vertices) < 300]
DUP = [o for o in TEETH if int(o.name.split(".")[1]) >= 20]
for o in DUP: o.hide_render = True; o.hide_viewport = True
TEETH = [o for o in TEETH if o not in DUP]
if os.environ.get("MODE", "teeth") == "teeth":
    # the teeth that actually render in this file are the "GRILLS" collection (the "TEETH" set sits in the switched-off "xxx"
    # collection with a spare body): use the visible ones, so it's the model's own teeth in the shot
    TEETH = [o for o in bpy.data.collections["GRILLS"].objects if o.type == 'MESH']
    for o in TEETH: o.hide_render = False; o.hide_viewport = False
if os.environ.get("HIDE_BODY2", "0") == "1":
    b2 = bpy.data.objects.get("Genesis8Male.002")
    if b2: b2.hide_render = True
def wverts(o):
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    mw = np.array(o.matrix_world); return co @ mw[:3, :3].T + mw[:3, 3]
cent = np.array([wverts(o).mean(0) for o in TEETH]); C0 = cent.mean(0)
_, _, Vt = np.linalg.svd(cent - C0)
side, fwd, upv = Vt[0], Vt[1], Vt[2]
if upv[2] < 0: upv = -upv                                                   # up = towards world +Z (upper teeth are higher)
proj = (cent - C0) @ np.stack([side, fwd, upv], 1)
if np.polyfit(proj[:, 0], proj[:, 1], 2)[0] > 0: fwd = -fwd                 # arch bulges forward in the middle
if np.dot(np.cross(fwd, side), upv) < 0: side = -side                        # right-handed: X=forward, Y=side, Z=up
M = np.stack([fwd, side, upv], 1)                                            # local -> world rotation
def to_local(P): return (P - C0) @ M
_lc = to_local(cent)
# bite plane (z as a plane in forward/side), iterate once with the split; classify teeth by the side of the plane
A = np.stack([np.ones(len(_lc)), _lc[:, 0], _lc[:, 1]], 1); lab = _lc[:, 2] > np.median(_lc[:, 2])
for _ in range(3):
    cu, *_ = np.linalg.lstsq(A[lab], _lc[lab, 2], rcond=None); cl, *_ = np.linalg.lstsq(A[~lab], _lc[~lab, 2], rcond=None)
    lab = np.abs(_lc[:, 2] - A @ cu) < np.abs(_lc[:, 2] - A @ cl)
up_row = [o for o, l in zip(TEETH, lab) if l]; lo_row = [o for o, l in zip(TEETH, lab) if not l]
print("SPLIT upper", sorted(o.name[-3:] for o in up_row), "lower", sorted(o.name[-3:] for o in lo_row))
# ---- jaw drop: lower lip/chin/jaw skin + lower teeth move down along -up with a smooth falloff (no rig in this file)
DROP = E("JAW_DROP", 0.55)
if DROP > 0:
    body = bpy.data.objects["Genesis8Male.002"]
    co = np.empty(len(body.data.vertices) * 3); body.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    mw = np.array(body.matrix_world); wco = co @ mw[:3, :3].T + mw[:3, 3]; L_ = to_local(wco)
    bite = (np.mean([to_local(wverts(o)).min(0)[2] for o in up_row]) + np.mean([to_local(wverts(o)).max(0)[2] for o in lo_row])) / 2
    below = np.clip((bite + 0.1 - L_[:, 2]) / 0.6, 0, 1); below = below * below * (3 - 2 * below)
    r = np.sqrt(L_[:, 1] ** 2 + (L_[:, 2] - bite) ** 2 * 0.5); fall = np.clip(1 - (r - 2.0) / 4.0, 0, 1); fall = fall * fall * (3 - 2 * fall)
    near = (L_[:, 0] > -6) & (L_[:, 0] < 6)
    d = DROP * below * fall * near
    wco = wco - np.outer(d, upv)
    inv = np.linalg.inv(mw[:3, :3]); co = (wco - mw[:3, 3]) @ inv.T
    body.data.vertices.foreach_set("co", co.ravel()); body.data.update()
    for o in lo_row:
        mw_ = o.matrix_world.copy(); mw_.translation = mw_.translation - Vector((upv * DROP).tolist()); o.matrix_world = mw_
    bpy.context.view_layer.update()
def measure(row):
    P = np.vstack([to_local(wverts(o)) for o in row])
    front = []
    for yb in np.linspace(P[:, 1].min(), P[:, 1].max(), 30):
        s_ = P[np.abs(P[:, 1] - yb) < 0.12]
        if len(s_): front.append((yb, s_[:, 0].max()))
    F = np.array(front); c2, c1, c0 = np.polyfit(F[:, 0], F[:, 1], 2)
    return dict(z0=float(P[:, 2].min()), z1=float(P[:, 2].max()), y0=float(P[:, 1].min()), y1=float(P[:, 1].max()), a=c0, b=c1, k=-c2)
MU, ML = measure(up_row), measure(lo_row)
print("ROWS upper", len(up_row), {k: round(v, 3) for k, v in MU.items()}, "| lower", len(lo_row), {k: round(v, 3) for k, v in ML.items()})
# ---- materials
def gold(name="MAT_Gold", rough=0.15):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 0.68, 0.28, 1); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = rough
    b.inputs["Anisotropic"].default_value = 0.3; return m
def emerald():
    m = bpy.data.materials.new("MAT_EmeraldEnamel"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.inputs["Scale"].default_value = 1.2
    wv.inputs["Distortion"].default_value = 5.0; wv.inputs["Detail"].default_value = 2.0; nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0.002, 0.06, 0.012, 1); e[1].position = 1.0; e[1].color = (0.06, 0.55, 0.12, 1)
    mid = e.new(0.55); mid.color = (0.012, 0.22, 0.04, 1)
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.1; b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Specular IOR Level"].default_value = 0.7; return m
GOLD, EMER = gold(), emerald()
PAL = os.environ.get("PALETTE", "punk")
MAGENTA, EBLUE, NYELLOW, NORANGE = (1.0, 0.02, 0.55), (0.02, 0.18, 1.0), (1.0, 0.92, 0.0), (1.0, 0.32, 0.0)
if PAL == "punk":
    gb = GOLD.node_tree.nodes["Principled BSDF"]; gb.inputs["Base Color"].default_value = (1.0, 0.45, 0.06, 1)      # orange-gold rims
    en = EMER.node_tree; cr = next(n for n in en.nodes if n.type == 'VALTORGB').color_ramp
    cr.elements[0].color = (0.9, 0.55, 0.0, 1); cr.elements[1].color = (1.0, 1.0, 0.15, 1); cr.elements[2].color = (1.0, 0.85, 0.0, 1)
    eb = en.nodes["Principled BSDF"]; eb.inputs["Emission Color"].default_value = (*NYELLOW, 1); eb.inputs["Emission Strength"].default_value = E("ENAMEL_GLOW", 0.25)
    def recolor(m, tint, val=0.9, sat=0.0):
        if not m or not m.use_nodes: return
        nt = m.node_tree; b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not b: return
        src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs["Factor"].default_value = 1.0
        if src:
            hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
            nt.links.new(src, hs.inputs["Color"]); nt.links.new(hs.outputs["Color"], mx.inputs[6])
        else: mx.inputs[6].default_value = (val, val, val, 1)
        mx.inputs[7].default_value = (*tint, 1); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
        b.inputs["Coat Weight"].default_value = 0.35; b.inputs["Coat Roughness"].default_value = 0.2
    body = bpy.data.objects["Genesis8Male.002"]
    for m in body.data.materials:
        n = m.name.split(".")[0] if m else ""
        if n in ("Teeth", "Mouth"): continue
        if n in ("Sclera", "Cornea", "EyeMoisture", "Pupils", "Irises"): continue
        recolor(m, (0.03, 0.16, 1.0) if n != "Lips" else (0.1, 0.06, 0.9), val=E('SKIN_V', 0.85) if n != "Lips" else 0.7)
    for m in bpy.data.objects["clth"].data.materials: recolor(m, NYELLOW, val=1.0)
FONT = bpy.data.fonts.load(R + "work/grillz/font/" + os.environ.get("FONT", "Corben-Bold.ttf"))
Mw = Matrix(((M[0, 0], M[0, 1], M[0, 2], C0[0]), (M[1, 0], M[1, 1], M[1, 2], C0[1]), (M[2, 0], M[2, 1], M[2, 2], C0[2]), (0, 0, 0, 1)))
def make_word(text, row, name, wfrac, height, overhang, upper, tilt):
    width = (row["y1"] - row["y0"]) * wfrac; ymid = (row["y0"] + row["y1"]) / 2
    tip = row["z0"] if upper else row["z1"]                      # tooth tips (bite edge)
    zmid = (tip - overhang + height / 2) if upper else (tip + overhang - height / 2)
    objs = []
    for layer, offset, extr, bev, cx, mat in (("gold", E("RIM", 0.03), 0.16, 0.035, 0.0, GOLD), ("face", E("FACE_OFF", -0.022), 0.03, E("PUFF", 0.04), 0.16, EMER)):
        cd = bpy.data.curves.new(f"{name}_{layer}", 'FONT'); cd.body = text; cd.font = FONT; cd.size = 1.0; cd.align_x = 'CENTER'; cd.align_y = 'CENTER'
        cd.offset = offset; cd.extrude = extr; cd.bevel_depth = bev; cd.bevel_resolution = 5; cd.space_character = E("TRACK", 1.0)
        ob = bpy.data.objects.new(f"{name}_{layer}", cd); S.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob.select_set(False)
        ob = bpy.context.view_layer.objects.active
        v = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", v); objs.append((ob, v.reshape(-1, 3), cx, mat))
    gv = objs[0][1]; sc = width / (gv[:, 0].max() - gv[:, 0].min()); sz = height / (gv[:, 1].max() - gv[:, 1].min())
    back = gv[:, 2].min(); vm = (gv[:, 1].max() + gv[:, 1].min()) / 2; dsc = sc * E("DEPTH", 1.0)
    out = []
    for ob, v, cx, mat in objs:
        w = v.copy(); w[:, 2] += cx - back; w[:, 1] -= vm
        yy = ymid + w[:, 0] * sc; up = w[:, 1] * sz; dep = w[:, 2] * dsc
        xs = row["a"] + row["b"] * yy - row["k"] * yy ** 2 + E("PRESS", -0.02)      # back of the letters on the measured front surface
        dx = -(row["b"] - 2 * row["k"] * yy); nl = np.sqrt(1 + dx * dx); nx, ny = 1 / nl, -dx / nl
        X = xs + dep * nx; Y = yy + dep * ny; Z = zmid + up + tilt * dep
        L = np.stack([X, Y, Z], 1); Wd = L @ M.T + C0
        ob.data.vertices.foreach_set("co", Wd.ravel()); ob.data.update()
        ob.data.materials.append(mat); ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons)); out.append(ob)
    return out
MODE = os.environ.get("MODE", "teeth")                     # user: "use the original teeth ... just initials PD"
if MODE == "words":
    make_word("PHILLIPS", MU, "GR_Upper", E("UP_WF", 0.82), E("UP_H", 0.95), E("OVER", 0.08), True, -0.25)
    make_word("MOTION", ML, "GR_Lower", E("LO_WF", 0.7), E("LO_H", 0.9), E("OVER", 0.08), False, 0.25)
# ---- light + camera in the mouth frame (units: cm)
W = S.world or bpy.data.worlds.new("W"); S.world = W; W.use_nodes = True
bg = W.node_tree.nodes.get("Background")
for l in list(W.node_tree.links): W.node_tree.links.remove(l)
bg.inputs["Color"].default_value = (*MAGENTA, 1) if PAL == 'punk' else (0, 0, 0, 1); bg.inputs["Strength"].default_value = E('BG_E', 1.0) if PAL == 'punk' else 0.0
W.node_tree.links.new(bg.outputs[0], W.node_tree.nodes["World Output"].inputs["Surface"])
if PAL == 'punk' and os.environ.get("MODE", "teeth") == "teeth":
    # magenta only where the camera sees the backdrop; reflections see a warm dark studio so the gold reads as gold
    wn = W.node_tree; lp = wn.nodes.new("ShaderNodeLightPath"); b2 = wn.nodes.new("ShaderNodeBackground")
    b2.inputs["Color"].default_value = (1.0, 0.75, 0.45, 1); b2.inputs["Strength"].default_value = E("REFL_E", 0.25)
    ms = wn.nodes.new("ShaderNodeMixShader"); wn.links.new(lp.outputs["Is Camera Ray"], ms.inputs[0])
    wn.links.new(b2.outputs[0], ms.inputs[1]); wn.links.new(bg.outputs[0], ms.inputs[2])
    wn.links.new(ms.outputs[0], wn.nodes["World Output"].inputs["Surface"])
def L2W(p): return Vector((np.array(p) @ M.T + C0).tolist())
FC = L2W((MU["a"], 0, 0))
def light(name, lp, energy, col, size, sy=None, diffuse=True):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col; ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = sy or size
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = L2W(lp)
    o.rotation_euler = (FC - o.location).to_track_quat('-Z', 'Y').to_euler(); o.visible_diffuse = diffuse; return o
K = E("LIGHT_E", 70.0)
if PAL == "punk":
    light("LGT_Key_BlueWhite", (60, 30, 35), 900 * K, (0.75, 0.85, 1.0), 25)
    light("LGT_Rim_Magenta_L", (-10, 55, 15), 900 * K, MAGENTA, 18)
    light("LGT_Rim_Magenta_R", (-10, -55, 10), 700 * K, MAGENTA, 18)
    light("LGT_Kick_Yellow", (40, -45, -20), 350 * K, NYELLOW, 12)
    light("LGT_Glint_Strip", (55, 10, 20), 450 * K, (1.0, 0.95, 0.85), 40, sy=1.5, diffuse=False)
    light("LGT_Glint_Top", (45, -10, 45), 300 * K, (1.0, 0.9, 0.7), 30, sy=1.2, diffuse=False)
else:
    light("LGT_Key_Warm", (60, 35, 40), 900 * K, (1.0, 0.78, 0.58), 35)
    light("LGT_Rim_Orange", (5, -50, 10), 500 * K, (1.0, 0.55, 0.25), 15)
    light("LGT_Glint_Strip", (55, 15, 20), 450 * K, (1.0, 0.9, 0.75), 40, sy=1.5, diffuse=False)
    light("LGT_Glint_Top", (45, -10, 45), 300 * K, (1.0, 0.85, 0.65), 30, sy=1.2, diffuse=False)
    light("LGT_Fill_Low", (60, -20, -25), 60 * K, (1.0, 0.7, 0.55), 50)
cam = S.camera
cam.animation_data_clear(); cam.data.animation_data_clear(); cam.constraints.clear() if hasattr(cam, "constraints") else None
cam.parent = None
cam.location = L2W((E("CAM_F", 22.0), E("CAM_S", 3.0), E("CAM_U", 0.0)))
tgt = L2W((MU["a"] - 0.3, 0, (MU["z0"] + ML["z1"]) / 2))
up_w = Vector(upv.tolist())
fwdc = (tgt - cam.location).normalized(); right = fwdc.cross(up_w).normalized(); upc = right.cross(fwdc)
cam.rotation_euler = Matrix((right, upc, -fwdc)).transposed().to_euler()
cam.data.lens = E("LENS", 70); cam.data.sensor_width = 36; cam.data.clip_start = 0.5; cam.data.shift_x = cam.data.shift_y = 0
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = E("FSTOP", 5.6); cam.data.dof.focus_distance = (tgt - cam.location).length
S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'; S.cycles.samples = 48; S.cycles.use_adaptive_sampling = True; S.cycles.use_denoising = False
S.cycles.glossy_bounces = 6; S.cycles.sample_clamp_indirect = 4.0
S.render.resolution_x, S.render.resolution_y, S.render.resolution_percentage = 1920, 1080, 100; S.render.film_transparent = False
S.view_settings.view_transform = 'Standard' if PAL == 'punk' else 'AgX'
try: S.view_settings.look = 'Medium High Contrast' if PAL == 'punk' else 'AgX - Punchy'
except TypeError: pass
S.view_settings.exposure = E("EXPO", 0.0)
# ---- teeth mode: the model's own teeth become polished gold caps; "P" and "D" are sculpted onto the two front teeth,
# every letter vertex ray-projected onto the tooth's real front surface so the letters follow its curve
if MODE == "teeth":
    from mathutils.bvhtree import BVHTree
    tg = bpy.data.materials.new("MAT_GoldCap"); tg.use_nodes = True; tb = tg.node_tree.nodes["Principled BSDF"]
    tb.inputs["Base Color"].default_value = (1.0, 0.66, 0.24, 1); tb.inputs["Metallic"].default_value = 1.0
    tb.inputs["Roughness"].default_value = E("CAP_ROUGH", 0.1); tb.inputs["Anisotropic"].default_value = 0.2
    for o in TEETH:
        o.data.materials.clear(); o.data.materials.append(tg)
        o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons)); o.data.update()
    en = bpy.data.materials.new("MAT_LetterEnamel"); en.use_nodes = True; eb = en.node_tree.nodes["Principled BSDF"]
    eb.inputs["Base Color"].default_value = (*EBLUE, 1); eb.inputs["Roughness"].default_value = 0.08
    eb.inputs["Coat Weight"].default_value = 1.0; eb.inputs["Coat Roughness"].default_value = 0.02
    eb.inputs["Emission Color"].default_value = (*EBLUE, 1); eb.inputs["Emission Strength"].default_value = E("LETTER_GLOW", 0.15)
    cen = sorted(up_row, key=lambda o: abs(to_local(wverts(o)).mean(0)[1]))[:2]
    rw = np.array(right)                                         # camera right in world: the viewer's left tooth gets "P"
    cen.sort(key=lambda o: float(wverts(o).mean(0) @ rw))
    for ch, o in zip(os.environ.get("INITIALS", "PD"), cen):
        wv = wverts(o); lv = to_local(wv)
        bvh = BVHTree.FromPolygons([Vector(p) for p in wv.tolist()], [tuple(p.vertices) for p in o.data.polygons])
        front = lv[lv[:, 0] > np.percentile(lv[:, 0], 60)]
        ty, tz0, tz1 = (front[:, 1].min() + front[:, 1].max()) / 2, lv[:, 2].min(), lv[:, 2].max()
        tw, th = front[:, 1].max() - front[:, 1].min(), tz1 - tz0
        lw, lh = tw * E("L_W", 0.62), th * E("L_H", 0.5); lz = tz0 + th * E("L_Z", 0.42)
        for layer, offset, extr, bev, lift, mat in (("rim", E("L_RIM", 0.03), 0.02, 0.012, 0.0, tg), ("face", -0.01, 0.01, E("L_PUFF", 0.02), 0.022, en)):
            cd = bpy.data.curves.new(f"PD_{ch}_{layer}", 'FONT'); cd.body = ch; cd.font = FONT; cd.size = 1.0
            cd.align_x = 'CENTER'; cd.align_y = 'CENTER'; cd.offset = offset; cd.extrude = extr; cd.bevel_depth = bev; cd.bevel_resolution = 4
            ob = bpy.data.objects.new(f"PD_{ch}_{layer}", cd); S.collection.objects.link(ob)
            bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob.select_set(False)
            ob = bpy.context.view_layer.objects.active
            v = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", v); v = v.reshape(-1, 3)
            if layer == "rim": ref = (v[:, 0].min(), v[:, 0].max(), v[:, 1].min(), v[:, 1].max(), v[:, 2].min())
            sx, sy = lw / (ref[1] - ref[0]), lh / (ref[3] - ref[2]); s_ = min(sx, sy)
            yy = ty + (v[:, 0] - (ref[0] + ref[1]) / 2) * s_; zz = lz + (v[:, 1] - (ref[2] + ref[3]) / 2) * s_
            dep = (v[:, 2] - ref[4]) * E("L_DEPTH", 0.5) + lift - 0.005
            out = np.empty_like(v); fwd_w = Vector(fwd.tolist())
            hits = []
            for i in range(len(v)):
                start = Vector((np.array([lv[:, 0].max() + 2.0, yy[i], zz[i]]) @ M.T + C0).tolist())
                h = bvh.ray_cast(start, -fwd_w, 5.0); hits.append(h[0])
            okx = [to_local(np.array(h))[0] for h in hits if h is not None]; xfb = float(np.median(okx)) if okx else float(lv[:, 0].max())
            for i, h in enumerate(hits):
                xs = to_local(np.array(h))[0] if h is not None else xfb
                out[i] = np.array([xs + dep[i], yy[i], zz[i]]) @ M.T + C0
            ob.data.vertices.foreach_set("co", out.ravel()); ob.data.update(); ob.data.materials.append(mat)
            ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
        print("LETTER", ch, "on", o.name, "tooth w %.3f h %.3f" % (tw, th))
if a and a[0] == "save":
    bpy.ops.wm.save_as_mainfile(filepath=a[1]); print("GRILLZ2 SAVED")
