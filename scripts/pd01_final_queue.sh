#!/bin/bash
# PD-01 final render queue (resumable; relaunch after each 2 h limit). 1) Cycles 720p 24 spp + OIDN, 217 frames (every other
# frame on slow shots; every frame around cuts, the power-on flicker and the reveal) -> 2) RIFE fill (never across cuts: both
# sides of each cut are rendered) -> 3) AI upscale 1920x1080 (keeps alpha) -> 4) lens pass on the plates -> public/pd01/seq_final
cd /home/user/Motion-Studio; D=work/cyber3/final
PYTHONPATH=tools/py312 blender -b work/cyber3/pd01_final.blend -P scripts/denoise/oidn_render.py -- \
  --out $D/frames --start 1 --end 360 --frames "$(cat work/cyber3/final_frames.txt)" --spp 24 --pct 67 --persistent >> $D/render.log 2>&1
n=$(ls $D/frames/d_*.png | wc -l); [ "$n" -ge 217 ] || { echo "render $n/217" > $D/status; exit 1; }
mkdir -p $D/seq && for p in $D/frames/d_*.png; do b=$(basename $p); cp -n "$p" "$D/seq/f_${b#d_}" 2>/dev/null; done
[ "$(ls $D/seq | wc -l)" -ge 360 ] || PYTHONPATH=tools/ai-py:tools/rife .object-separation/bin/python scripts/ai/interpolate.py --fill $D/seq --threads 4 >> $D/rife.log 2>&1
PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py $D/seq $D/up 1920 1080 --model fast --threads 4 --skip-existing >> $D/up.log 2>&1
[ "$(ls $D/lens 2>/dev/null | wc -l)" -ge 360 ] || PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py $D/up $D/lens --preset minimal >> $D/lens.log 2>&1
echo "done $(ls $D/lens | wc -l)" > $D/status
