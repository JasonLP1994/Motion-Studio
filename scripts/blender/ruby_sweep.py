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
