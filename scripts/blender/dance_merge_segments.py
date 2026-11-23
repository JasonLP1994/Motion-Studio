# join several baked segment actions (from retarget.py runs) into one timeline on the first segment's file.
#   blender -b SEG1.blend -P merge_segments.py -- OUT.blend SEG2.blend SEG3.blend ...
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]; OUT, others = a[0], a[1:]
S = bpy.context.scene; rig = bpy.data.objects["rig"]; act = rig.animation_data.action
end = S.frame_end; segs = [(1, end, act.name)]
for path in others:
    with bpy.data.libraries.load(path) as (src, dst):
        dst.actions = [n for n in src.actions if n.startswith("BREAK_")]
    sa = dst.actions[0]; n = int(sa.frame_range[1] - sa.frame_range[0] + 1); off = end
    for fc in sa.fcurves:
        tfc = act.fcurves.find(fc.data_path, index=fc.array_index) or act.fcurves.new(fc.data_path, index=fc.array_index, action_group=fc.group.name if fc.group else "")
        for kp in fc.keyframe_points: tfc.keyframe_points.insert(kp.co.x + off, kp.co.y, options={'FAST'})
    segs.append((end + 1, end + n, sa.name)); end += n
for fc in act.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    fc.update()
S.frame_start, S.frame_end = 1, end
S["segments"] = str(segs)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("MERGED", segs)
