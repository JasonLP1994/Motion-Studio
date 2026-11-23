# UV / blacklight look for the dance (user's reference): electric-blue seamless set, blue light (skin reads indigo),
# translucent glossy hot-pink vinyl jacket + hoodie with glowing edges, neon-lime UV paint on the face, indigo pants.
#   blender -b IN.blend -P work/dance/uv_look.py -- OUT.blend
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
S = bpy.context.scene
PINK, LIME, BLUE = (1.0, 0.0, 0.28), (0.1, 1.0, 0.04), (0.02, 0.16, 1.0)
E = lambda k, d: float(os.environ.get(k, d))

def bsdf(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
def insert_desat(m, sat, val):
    nt = m.node_tree; b = bsdf(m); inp = b.inputs["Base Color"]
    if not inp.links: return
    src = inp.links[0].from_socket; hs = nt.nodes.new("ShaderNodeHueSaturation")
    hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
    nt.links.new(src, hs.inputs["Color"]); nt.links.new(hs.outputs["Color"], inp)
    return hs
def edge_glow(m, col, strength):
    nt = m.node_tree; b = bsdf(m)
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; nt.links.new(lw.outputs["Facing"], pw.inputs[0]); pw.inputs[1].default_value = 2.2
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; nt.links.new(pw.outputs[0], mu.inputs[0]); mu.inputs[1].default_value = strength
    b.inputs["Emission Color"].default_value = (*col, 1); nt.links.new(mu.outputs[0], b.inputs["Emission Strength"])
def vinyl(m, col, trans, tint_tex=0.15):
    nt = m.node_tree; b = bsdf(m)
    for k in ("Base Color", "Roughness", "Metallic", "Alpha"):
        for l in list(b.inputs[k].links):
            if k != "Base Color": nt.links.remove(l)
    # keep a whisper of the original fabric detail (seams, ribbing) multiplied into the pink
    src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
    if src:
        bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(src, bw.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs["Factor"].default_value = tint_tex
        mx.inputs[6].default_value = (*col, 1); nt.links.new(bw.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    else: b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Metallic"].default_value = 0.0; b.inputs["Roughness"].default_value = 0.12
    b.inputs["Transmission Weight"].default_value = trans; b.inputs["IOR"].default_value = 1.45
    b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.04
    b.inputs["Subsurface Weight"].default_value = 0.0
    edge_glow(m, PINK, E("EDGE", 4.0))


# skin: desaturate so the blue light turns it indigo; a touch glossier
for o in (bpy.data.objects["CC_Base_Body"],):
    for m in o.data.materials:
        if m and m.name.startswith("Std_Skin"):
            hs = insert_desat(m, 0.1, E("SKIN_V", 0.45)); bsdf(m).inputs["Coat Weight"].default_value = 0.3
            if hs:
                t = m.node_tree.nodes.new("ShaderNodeMix"); t.data_type = 'RGBA'; t.blend_type = 'MULTIPLY'; t.inputs["Factor"].default_value = 1.0
                t.inputs[7].default_value = (0.35, 0.42, 1.0, 1); m.node_tree.links.new(hs.outputs["Color"], t.inputs[6]); m.node_tree.links.new(t.outputs[2], bsdf(m).inputs["Base Color"])
for m in bpy.data.objects["Buzz_Cut"].data.materials: insert_desat(m, 0.1, 0.6)
# neon-lime UV paint on the face (undeformed "Generated" coordinates follow the skin as it animates)
body = bpy.data.objects["CC_Base_Body"]
co = [v.co for v in body.data.vertices]; lo = Vector([min(c[i] for c in co) for i in range(3)]); hi = Vector([max(c[i] for c in co) for i in range(3)])
def gen(p): return Vector([(p[i] - lo[i]) / (hi[i] - lo[i]) for i in range(3)])
head = bpy.data.materials["Std_Skin_Head"]; nt = head.node_tree; b = bsdf(head)
H = hi.z - lo.z
face = [c for c in co if c.z > lo.z + H * 0.86]; nose = min(face, key=lambda c: c.y)
centre = gen(nose + Vector((E("PAINT_X", 0.045), E("PAINT_Y", 0.03), E("PAINT_Z", -0.045))))
SZ = Vector((0.03 / (hi.x - lo.x), 0.03 / (hi.y - lo.y), 0.06 / (hi.z - lo.z)))
# face paint: a crisp stencil (work/dance/paint/face_paint_stencil.png, 22 x 26 cm, origin at the nose tip) projected from the
# front in the undeformed "Generated" space (it follows the skin as he moves), limited to front-facing face skin by a vertex attribute
U = 1.0 / body.matrix_world.to_scale().x   # mesh units per metre (this CC body is in centimetres)
attr = body.data.attributes.get("lime_paint") or body.data.attributes.new("lime_paint", 'FLOAT', 'POINT')
vals = []
for v in body.data.vertices:
    p = v.co; f = 0.0
    if p.z > nose.z - 0.11 * U and abs(p.x - nose.x) < 0.09 * U and p.y < nose.y + 0.08 * U:
        f = max(0.0, min(1.0, (-v.normal.y + 0.05) / 0.35))
    vals.append(f)
attr.data.foreach_set("value", vals)
at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "lime_paint"
tc = nt.nodes.new("ShaderNodeTexCoord"); sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sx.inputs[0])
def lin(x, mul, add):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = 'MULTIPLY_ADD'; nt.links.new(x, n.inputs[0]); n.inputs[1].default_value = mul; n.inputs[2].default_value = add; return n.outputs[0]
# generated g -> mesh units: lo + g * size ; stencil u = (x - (nose.x - 0.11U)) / 0.22U ; v = (z - (nose.z - 0.14U)) / 0.26U
Wd, Ht = 0.22 * U, 0.26 * U
u = lin(sx.outputs["X"], (hi.x - lo.x) / Wd, (lo.x - (nose.x - 0.11 * U)) / Wd)
v = lin(sx.outputs["Z"], (hi.z - lo.z) / Ht, (lo.z - (nose.z - 0.14 * U)) / Ht)
cm = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u, cm.inputs[0]); nt.links.new(v, cm.inputs[1])
img = nt.nodes.new("ShaderNodeTexImage"); img.image = bpy.data.images.load("/home/user/Motion-Studio/work/dance/paint/face_paint_stencil.png", check_existing=True)
img.image.colorspace_settings.name = 'Non-Color'; img.extension = 'CLIP'; nt.links.new(cm.outputs[0], img.inputs["Vector"])
mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'; nt.links.new(img.outputs["Color"], mm.inputs[0]); nt.links.new(at.outputs["Fac"], mm.inputs[1])
class _M: pass
mask = _M(); mask.outputs = [mm.outputs[0]]
src = b.inputs["Base Color"].links[0].from_socket
mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; nt.links.new(mask.outputs[0], mx.inputs["Factor"]); nt.links.new(src, mx.inputs[6]); mx.inputs[7].default_value = (*LIME, 1)
nt.links.new(mx.outputs[2], b.inputs["Base Color"])
b.inputs["Emission Color"].default_value = (*LIME, 1)
em = nt.nodes.new("ShaderNodeMath"); em.operation = 'MULTIPLY'; nt.links.new(mask.outputs[0], em.inputs[0]); em.inputs[1].default_value = E("LIME_GLOW", 9.0)
for l in list(b.inputs["Emission Strength"].links): nt.links.remove(l)
nt.links.new(em.outputs[0], b.inputs["Emission Strength"])
# clothing
vinyl(bpy.data.objects["Jacket"].data.materials[0], PINK, E("JACKET_T", 0.55))
vinyl(bpy.data.objects["Vest"].data.materials[0], (1.0, 0.02, 0.4), E("HOODIE_T", 0.35), 0.3)
pm = bpy.data.objects["Chachi_Momma_Pants"].data.materials[0]; insert_desat(pm, 0.0, 0.35)
bp = bsdf(pm); bp.inputs["Coat Weight"].default_value = 0.6; bp.inputs["Coat Roughness"].default_value = 0.15
sm = bpy.data.objects["Sneaker"].data.materials[0]; insert_desat(sm, 0.0, 1.1); bs = bsdf(sm); bs.inputs["Coat Weight"].default_value = 0.8
edge_glow(sm, LIME, 0.8)
# set: electric-blue seamless cyc, blue world
cyc = bpy.data.objects["Plane.002"].data.materials[0]; cb = bsdf(cyc)
cb.inputs["Base Color"].default_value = (*BLUE, 1); cb.inputs["Roughness"].default_value = 0.7
cb.inputs["Emission Color"].default_value = (*BLUE, 1); cb.inputs["Emission Strength"].default_value = E("CYC_GLOW", 0.9)
bpy.data.objects["Plane.001"].hide_render = True
W = S.world; W.use_nodes = True; bg = W.node_tree.nodes.get("Background")
if bg: bg.inputs["Color"].default_value = (0.03, 0.1, 1.0, 1); bg.inputs["Strength"].default_value = 0.6
# lights: blue key + fill, hot-pink rims behind (vinyl edges), faint violet top
for o in [o for o in bpy.data.objects if o.type == 'LIGHT']: bpy.data.objects.remove(o)
def light(name, loc, energy, col, size, look=(0, 0, 1.0)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col; ld.size = size
    o = bpy.data.objects.new(name, ld); S.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
light("LGT_Key_Blue", (-2.6, -3.0, 2.8), E("KEY", 450), (0.25, 0.4, 1.0), 3.0)
light("LGT_Fill_Blue", (3.0, -2.5, 1.2), 350, (0.2, 0.35, 1.0), 3.0)
light("LGT_Rim_Pink", (2.2, 2.4, 2.2), E("RIM", 1800), (1.0, 0.03, 0.4), 1.5)
light("LGT_Front_Pink", (1.6, -2.6, 0.6), 250, (1.0, 0.05, 0.45), 2.0)
light("LGT_Rim_Pink2", (-2.4, 2.0, 1.5), 700, (1.0, 0.1, 0.6), 1.5)
light("LGT_Top_Violet", (0, 0.5, 4.5), 300, (0.5, 0.3, 1.0), 2.0)
S.render.engine = 'CYCLES'; S.cycles.samples = 32; S.cycles.use_denoising = False
S.view_settings.view_transform = 'Standard'; S.view_settings.exposure = E('EXPO', -0.4)
bpy.ops.wm.save_as_mainfile(filepath=a[0]); print("UV LOOK SAVED")
