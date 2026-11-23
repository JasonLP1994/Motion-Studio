# Moving "glisten" lights for the ruby film: small, very bright point lights that slowly orbit the pendant for the whole film, so
# highlights travel across the facets and the stones keep twinkling (not only on the beat glints). Light-linked to the product only
# (they never light the floor or show in the pool). Settings live in CFG["sweep"] in ruby_pendant.py.
import bpy, math
from mathutils import Vector

def build(S, CFG):
    sw = CFG["sweep"]
    for o in [o for o in bpy.data.objects if o.name.startswith("LGT_Sweep")]:
        bpy.data.objects.remove(o, do_unlink=True)
    SET = bpy.data.collections["SET"]; PROD = bpy.data.collections["PRODUCT"]
    n = CFG["frames"]
    for i, (radius, height, revs, phase, energy) in enumerate(sw["lights"]):
        ld = bpy.data.lights.new(f"LGT_Sweep{i}", "POINT"); ld.energy = energy; ld.color = sw["color"]
        ld.shadow_soft_size = sw["size"]
        o = bpy.data.objects.new(f"LGT_Sweep{i}", ld); SET.objects.link(o)
        o.light_linking.receiver_collection = PROD
        o.visible_camera = False
        for f in range(1, n + 2, 6):          # keys every 6 frames, linear between -> smooth constant orbit
            a = math.radians(phase) + 2 * math.pi * revs * (f - 1) / n
            z = height + 1.5 * math.sin(a * 2 + i)            # gentle bob so lights cross facets at changing angles
            o.location = Vector((radius * math.cos(a), radius * math.sin(a), z)); o.keyframe_insert("location", frame=f)
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    # more of the highlights get the star glare
    for nd in (S.node_tree.nodes if S.node_tree else []):
        if nd.type == "GLARE": nd.threshold = sw["glare_threshold"]

def fix_gem_reflections(S, CFG):
    """Diamonds went dark grey from low cameras: light refracted through the stone exits downward into the black floor and the
    hidden dome was black below the horizon. Fix: the floor is invisible to TRANSMISSION rays only (camera, shadows, metal
    reflections unchanged) and the dome mirrors into the lower half (abs(Z)) with an extra soft band near the horizon."""
    fl = bpy.data.objects.get("Floor")
    if fl: fl.visible_transmission = False
    wn = S.world.node_tree
    sep = next(n for n in wn.nodes if n.type == "SEPXYZ"); grad = next(n for n in wn.nodes if n.type == "VALTORGB")
    if not any(n.type == "MATH" and n.operation == "ABSOLUTE" for n in wn.nodes):
        ab = wn.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
        wn.links.new(sep.outputs["Z"], ab.inputs[0]); wn.links.new(ab.outputs[0], grad.inputs[0])
        cr = grad.color_ramp
        for pos, v in CFG["sweep"].get("horizon_bands", ()):
            e = cr.elements.new(pos); e.color = (v, v, v * 1.02, 1)

def add_diamond_cards(S, CFG):
    """Step-cut stones are a hall of mirrors: they only read white if there is something white around them to mirror. Photographers
    use white cards; here they are soft area lights light-linked to the centre diamond only and hidden from the camera."""
    for o in [o for o in bpy.data.objects if o.name.startswith("LGT_Card")]: bpy.data.objects.remove(o, do_unlink=True)
    dia = [o for o in bpy.data.objects if o.type == "MESH" and any(s.material and s.material.name.startswith("MAT_Diamond") for s in o.material_slots)]
    dc = bpy.data.collections.get("GEM_DIAMOND") or bpy.data.collections.new("GEM_DIAMOND")   # receiver set, not in the scene
    for o in dia:
        if o.name not in dc.objects: dc.objects.link(o)
    SET = bpy.data.collections["SET"]
    for i, (az, dist, h, sx, sy, watts) in enumerate(CFG["sweep"]["cards"]):
        ld = bpy.data.lights.new(f"LGT_Card{i}", "AREA"); ld.shape = "RECTANGLE"; ld.size = sx; ld.size_y = sy
        ld.energy = watts; ld.color = (1.0, 0.99, 0.97)
        o = bpy.data.objects.new(f"LGT_Card{i}", ld); SET.objects.link(o)
        a = math.radians(az); o.location = Vector((dist * math.cos(a), dist * math.sin(a), h))
        o.rotation_euler = (Vector((0, 0, -0.6)) - o.location).to_track_quat("-Z", "Y").to_euler()
        o.light_linking.receiver_collection = dc; o.visible_camera = False
    print("diamond cards:", len(CFG["sweep"]["cards"]), "for", [o.name for o in dia])

def add_slow_turns(S, CFG):
    """Very slight, slow turns (a few degrees over seconds) so facets roll through the light: the whole pendant, plus the floating
    diamond in the exploded view. Added as DELTA rotations on top of the existing animation and back to zero before the
    rigid-body drop, so the baked dynamics stay valid."""
    def keys(o, table):
        if o.animation_data and o.animation_data.action:
            for fc in [fc for fc in o.animation_data.action.fcurves if fc.data_path == "delta_rotation_euler"]:
                o.animation_data.action.fcurves.remove(fc)
        for f, deg in table:
            o.delta_rotation_euler = [math.radians(d) for d in deg]; o.keyframe_insert("delta_rotation_euler", frame=f)
        for fc in o.animation_data.action.fcurves:
            if fc.data_path == "delta_rotation_euler":
                for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    t = CFG["turns"]
    keys(bpy.data.objects["PENDANT"], t["pendant"])
    keys(bpy.data.objects["G_DIAMOND"], t["diamond"])

def white_studio(S, CFG):
    """User: "change the background of the main scene to white or off white". Off-white infinity studio: the camera sees an
    off-white world, the floor turns off-white, the overhead spot turns warm white (soft pool + the piece's shadow stay)."""
    st = CFG.get("studio")
    if not st or not st.get("on"): return
    wn = S.world.node_tree
    bg = wn.nodes["Background"]                      # what the camera (and diffuse light) sees: was black
    bg.inputs[0].default_value = (*st["bg"], 1); bg.inputs[1].default_value = st["bg_strength"]
    fl = bpy.data.objects["Floor"]; b = fl.active_material.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*st["floor"], 1)
    sp = bpy.data.objects.get("LGT_Spot_Pool")
    if sp: sp.data.color = st["pool"]; sp.data.energy = st["pool_energy"]; sp.data.spot_size = math.radians(st["pool_deg"])

def grade(S, CFG):
    """User: "we could have more saturation". AgX desaturates bright colours, so: a punchier AgX look + a saturation lift in the
    compositor (after the glare), with the off-white studio kept near neutral by a small value lift only."""
    g = CFG.get("grade")
    if not g: return
    try: S.view_settings.look = g["look"]
    except TypeError: pass
    ct = S.node_tree
    for n in [n for n in ct.nodes if n.name == "GRADE_SAT"]: ct.nodes.remove(n)
    gl = next(n for n in ct.nodes if n.type == "GLARE"); co = next(n for n in ct.nodes if n.type == "COMPOSITE")
    hs = ct.nodes.new("CompositorNodeHueSat"); hs.name = "GRADE_SAT"
    hs.inputs["Saturation"].default_value = g["saturation"]; hs.inputs["Value"].default_value = g.get("value", 1.0)
    ct.links.new(gl.outputs["Image"], hs.inputs["Image"]); ct.links.new(hs.outputs["Image"], co.inputs["Image"])
