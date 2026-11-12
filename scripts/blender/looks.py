# Shared Blender looks for the PaintedStatue pieces: blood, marble, stone materials + hidden area lights.
# Used by render_still.py (stills) and build_anim.py (animation) so both look identical.
import bpy
from mathutils import Vector

b3 = lambda v: Vector((v[0], -v[2], v[1]))  # three.js (Y-up) -> Blender (Z-up)
hexc = lambda h, a=1.0: tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (1, 3, 5)) + (a,)

# ---------- materials ----------
def principled(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs["Surface"]); return m, nt, bs

def noise(nt, scale, detail=6, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
    geo = nt.nodes.get("WorldPos") or nt.nodes.new("ShaderNodeNewGeometry"); geo.name = "WorldPos"; nt.links.new(geo.outputs["Position"], n.inputs["Vector"])  # same scale on every object
    return n

def bump(nt, bs, height_socket, strength, dist=0.002):
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    nt.links.new(height_socket, b.inputs["Height"]); nt.links.new(b.outputs[0], bs.inputs["Normal"]); return b

def mat_blood(name, vertex_colours):
    m, nt, bs = principled(name); blood_into(nt, bs, vertex_colours); return m

def blood_into(nt, bs, vertex_colours=False):
    # blood: dark red body, near-black where thick, crimson where thin; light scatters a little inside; glassy wet coat
    if vertex_colours:
        a = nt.nodes.new("ShaderNodeVertexColor"); a.layer_name = "Col"; nt.links.new(a.outputs["Color"], bs.inputs["Base Color"])
    else:
        bs.inputs["Base Color"].default_value = hexc("#4A0206")
    bs.inputs["Roughness"].default_value = 0.035
    bs.inputs["IOR"].default_value = 1.36
    bs.inputs["Subsurface Weight"].default_value = 0.35
    bs.inputs["Subsurface Radius"].default_value = (1.0, 0.06, 0.03)
    bs.inputs["Subsurface Scale"].default_value = 0.004
    bs.inputs["Coat Weight"].default_value = 1.0; bs.inputs["Coat Roughness"].default_value = 0.01; bs.inputs["Coat IOR"].default_value = 1.4
    n = noise(nt, 140, 2, 0.5); return bump(nt, bs, n.outputs["Fac"], 0.04, 0.0005)  # faint surface tension ripples

def mat_marble(name, raw=False):
    m, nt, bs = principled(name); marble_into(nt, bs, raw); return m

def marble_into(nt, bs, raw=False):
    # veins: warped noise -> thin grey lines over warm white
    n = noise(nt, 2.5, 8, 0.6); w = nt.nodes.new("ShaderNodeMath"); w.operation = "SINE"
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 22.0
    nt.links.new(n.outputs["Fac"], mul.inputs[0]); nt.links.new(mul.outputs[0], w.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[1].position = 0.12
    ramp.color_ramp.elements[0].color = hexc("#B9B2A8"); ramp.color_ramp.elements[1].color = hexc("#D9D1C4" if raw else "#EDE6DA")
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(w.outputs[0], ab.inputs[0]); nt.links.new(ab.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.72 if raw else 0.3
    bs.inputs["Subsurface Weight"].default_value = 0.5 if not raw else 0.35
    bs.inputs["Subsurface Radius"].default_value = (1.0, 0.75, 0.55); bs.inputs["Subsurface Scale"].default_value = 0.02
    if not raw: bs.inputs["Coat Weight"].default_value = 0.15; bs.inputs["Coat Roughness"].default_value = 0.3
    pores = noise(nt, 900 if not raw else 260, 4, 0.7); return bump(nt, bs, pores.outputs["Fac"], 0.12 if not raw else 0.45, 0.001)

def mat_stone(name):
    # dark maroon polished stone: mottled colour, patchy gloss, fine grain
    m, nt, bs = principled(name)
    n = noise(nt, 3.0, 8, 0.6); ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexc("#080102"); ramp.color_ramp.elements[1].color = hexc("#1A0507")
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.7
    nt.links.new(n.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    r = noise(nt, 6.0, 4, 0.5); rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.32; rr.inputs["To Max"].default_value = 0.7
    nt.links.new(r.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], bs.inputs["Roughness"])
    bs.inputs["Specular IOR Level"].default_value = 0.3
    g = noise(nt, 400, 3, 0.6); bump(nt, bs, g.outputs["Fac"], 0.05, 0.0005)
    return m


def area(name, p3, target3, size, power, colour):
    ld = bpy.data.lights.new(name, "AREA"); ld.shape = "RECTANGLE"; ld.size, ld.size_y = size; ld.energy = power; ld.color = hexc(colour)[:3]
    o = bpy.data.objects.new(name, ld); bpy.context.scene.collection.objects.link(o); o.location = b3(p3)
    d = (b3(target3) - o.location); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); o.visible_camera = False
    return o
