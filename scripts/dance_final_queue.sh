#!/bin/bash
# Dance final render queue (resumable): Cycles 32 spp + motion blur at 720p, OIDN -> fast AI upscale to 1080p -> lens pass.
cd /home/user/Motion-Studio; D=work/dance/final
PYTHONPATH=tools/py312 blender -b work/dance/dance_final.blend -P scripts/denoise/oidn_render.py -- \
  --out $D/frames --start 1 --end 368 --spp 32 --persistent >> $D/render.log 2>&1
n=$(ls $D/frames/d_*.png 2>/dev/null | wc -l); [ "$n" -ge 368 ] || { echo "render $n/368" > $D/status; exit 1; }
mkdir -p $D/seq && for p in $D/frames/d_*.png; do b=$(basename $p); [ -e "$D/seq/f_${b#d_}" ] || cp "$p" "$D/seq/f_${b#d_}"; done
PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py $D/seq $D/up 1920 1080 --model fast --threads 4 --skip-existing >> $D/up.log 2>&1
[ "$(ls $D/lens 2>/dev/null | wc -l)" -ge 368 ] || PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py $D/up $D/lens --preset minimal >> $D/lens.log 2>&1
echo "done $(ls $D/lens | wc -l)" > $D/status
