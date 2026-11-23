# Retarget CMU breaking mocap (UE-mannequin skeleton, from codepawl/cmu-mocap-glb) onto the user's Auto-Rig Pro character.
# Bakes world-space rotations onto the ARP deform bones (their control constraints are removed) with forward kinematics on
# the character's own bone lengths; hip motion scaled by leg length; feet kept above the floor.
#   blender -b inputs/dance/realistic_man.blend -P work/dance/retarget.py -- MOCAP.glb F0 F1 OUT.blend
import bpy, sys, math
from mathutils import Matrix, Vector, Quaternion
a = sys.argv[sys.argv.index("--") + 1:]
SRC_FILE, F0, F1, OUT = a[0], int(a[1]), int(a[2]), a[3]
S = bpy.context.scene; S.render.fps = 24
tgt = bpy.data.objects["rig"]
# face rig fix: eye/lid aim targets live in world space and get left behind when the head moves (hollow, twisted eyes);
# re-parent every face constraint target that is not already under head.x onto head.x (keeping its offset)
def under(b, name):
    while b:
        if b.name == name: return True
        b = b.parent
    return False
face = [pb for pb in tgt.pose.bones if under(pb, "ORG-face")]
targets = set()
for pb in face:
    for c in pb.constraints:
        st = getattr(c, "subtarget", "")
        if st and getattr(c, "target", None) == tgt and st in tgt.data.bones and not under(tgt.data.bones[st], "head.x"): targets.add(st)
bpy.context.view_layer.objects.active = tgt; tgt.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
for st in targets: tgt.data.edit_bones[st].parent = tgt.data.edit_bones["head.x"]
bpy.ops.object.mode_set(mode='OBJECT'); print("FACE TARGETS REPARENTED", sorted(targets))
before = set(S.objects); bpy.ops.import_scene.gltf(filepath=SRC_FILE)
new = [o for o in S.objects if o not in before]
src = [o for o in new if o.type == 'ARMATURE'][0]
for o in new:
    if o.type == 'MESH': o.hide_render = True; o.hide_viewport = True
src.location.x += 3.0   # out of the way (world offset is removed below)

# target logical hierarchy: (target bone, source bone, logical parent target bone)
L = []
for s, t in (("pelvis", "root.x"),):
    L.append((t, s, None))
L += [("spine_01.x", "spine_01", "root.x"), ("spine_02.x", "spine_02", "spine_01.x"), ("spine_03.x", "spine_03", "spine_02.x"),
      ("neck.x", "neck_01", "spine_03.x"), ("head.x", "Head", "neck.x")]
for sd, ts in (("l", "l"), ("r", "r")):
    L += [(f"shoulder.{ts}", f"clavicle_{sd}", "spine_03.x"), (f"arm_stretch.{ts}", f"upperarm_{sd}", f"shoulder.{ts}"),
          (f"c_arm_twist_offset.{ts}", f"upperarm_{sd}", f"shoulder.{ts}"),
          (f"forearm_stretch.{ts}", f"lowerarm_{sd}", f"arm_stretch.{ts}"), (f"forearm_twist.{ts}", f"lowerarm_{sd}", f"forearm_stretch.{ts}"),
          (f"hand.{ts}", f"hand_{sd}", f"forearm_stretch.{ts}"),
          (f"thigh_stretch.{ts}", f"thigh_{sd}", "root.x"), (f"thigh_twist.{ts}", f"thigh_{sd}", "root.x"),
          (f"leg_stretch.{ts}", f"calf_{sd}", f"thigh_stretch.{ts}"), (f"leg_twist.{ts}", f"calf_{sd}", f"leg_stretch.{ts}"),
          (f"foot.{ts}", f"foot_{sd}", f"leg_stretch.{ts}"), (f"toes_01.{ts}", f"ball_{sd}", f"foot.{ts}")]
L = [x for x in L if x[0] in tgt.data.bones and x[1] in src.data.bones]
TB = {t: tgt.data.bones[t] for t, _, _ in L}
MWt, MWs = tgt.matrix_world, src.matrix_world

def rest(arm, b): return (arm.matrix_world @ b.matrix_local)
def frame(dirv, fwd):   # orthonormal frame: Y = bone direction, Z ~ character forward
    y = dirv.normalized(); z = (fwd - y * fwd.dot(y))
    if z.length < 1e-4: z = Vector((0, 0, 1)) - y * y.z
    z.normalize(); x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_quaternion()
FWD = Vector((0, -1, 0))
Fs, Ft, Rt0, Rs0q = {}, {}, {}, {}
for t, s, p in L:
    bs, bt = src.data.bones[s], tgt.data.bones[t]
    ds = (MWs @ bs.tail_local) - (MWs @ bs.head_local); dt = (MWt @ bt.tail_local) - (MWt @ bt.head_local)
    if t == 'root.x': ds = dt = Vector((0, 0, 1))      # hips: ARP's root points down, the mannequin pelvis up -> align on world up
    Fs[t] = frame(ds, FWD); Ft[t] = frame(dt, FWD)
    Rt0[t] = rest(tgt, bt).to_quaternion(); Rs0q[t] = rest(src, bs).to_quaternion()
# head offsets relative to the logical parent, in the parent's rest frame
OFF = {}
for t, s, p in L:
    if p: OFF[t] = Rt0[p].inverted() @ ((MWt @ TB[t].head_local) - (MWt @ TB[p].head_local))
# leg-length scale for hip translation
ls = (src.data.bones["thigh_l"].head_local - src.data.bones["foot_l"].head_local).length
lt = (tgt.data.bones["thigh_stretch.l"].head_local - tgt.data.bones["foot.l"].head_local).length
SC = lt / ls
src_hip0 = MWs @ src.data.bones["pelvis"].head_local
S.frame_set(F0); _p0 = MWs @ src.pose.bones["pelvis"].head; src_hip0 = Vector((_p0.x, _p0.y, src_hip0.z))   # centre the clip on the set
tgt_hip0 = MWt @ TB["root.x"].head_local

# free the deform bones from their ARP control constraints
for t in TB:
    pb = tgt.pose.bones[t]
    for c in list(pb.constraints): pb.constraints.remove(c)
    pb.rotation_mode = 'QUATERNION'
# speed: no mesh evaluation while baking
mute = []
for o in bpy.data.objects:
    for m in getattr(o, "modifiers", []):
        if m.show_viewport: mute.append(m); m.show_viewport = False
tgt.animation_data_create(); act = bpy.data.actions.new("BREAK_" + SRC_FILE.split("/")[-1][:-4]); tgt.animation_data.action = act
order = [x[0] for x in L]
depth = {}
for t, s, p in L: depth[t] = 0 if p is None else depth[p] + 1
levels = sorted(set(depth.values()))
src_act = src.animation_data.action
results = {}
for f in range(F0, F1 + 1):
    S.frame_set(f)
    R, H = {}, {}
    for t, s, p in L:
        Rs = (MWs @ src.pose.bones[s].matrix).to_quaternion()
        D = Rs @ Rs0q[t].inverted()
        R[t] = D @ Fs[t] @ Ft[t].inverted() @ Rt0[t]
    for t, s, p in L:
        if p is None:
            sh = MWs @ src.pose.bones["pelvis"].head
            H[t] = Vector((SC * (sh.x - src_hip0.x) + tgt_hip0.x, SC * (sh.y - src_hip0.y) + tgt_hip0.y, SC * sh.z + (tgt_hip0.z - SC * src_hip0.z)))
    for t, s, p in L:
        if p is not None: H[t] = H[p] + R[p] @ OFF[t]
    # keep feet/toes/hands on or above the floor (z = 0)
    lowest = min(min((H[t] + R[t] @ Vector((0, TB[t].length, 0))).z, H[t].z) for t in H if t.startswith(("toes_01", "foot", "hand")))
    if lowest < 0.01:
        for t in H: H[t] = H[t] + Vector((0, 0, 0.01 - lowest))
    results[f] = (R, H)
# write keys level by level (children of deform bones need their parents posed first)
for f in range(F0, F1 + 1):
    S.frame_set(f)
    R, H = results[f]
    for lv in levels:
        for t in [x for x in order if depth[x] == lv]:
            pb = tgt.pose.bones[t]
            M = Matrix.Translation(MWt.inverted() @ H[t]) @ (MWt.to_quaternion().inverted() @ R[t]).to_matrix().to_4x4()
            pb.matrix = M
        bpy.context.view_layer.update()
    for t in order:
        pb = tgt.pose.bones[t]
        pb.keyframe_insert("location", frame=f - F0 + 1); pb.keyframe_insert("rotation_quaternion", frame=f - F0 + 1)
for m in mute: m.show_viewport = True
for o in new: bpy.data.objects.remove(o, do_unlink=True)
S.frame_start, S.frame_end = 1, F1 - F0 + 1
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RETARGET SAVED", OUT, F1 - F0 + 1, "frames, leg scale", round(SC, 3))
