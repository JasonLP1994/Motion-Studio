#!/bin/bash
# final render: 720p (67%), 48 spp + OIDN, all 240 frames, resumable (skips frames already rendered)
cd /home/user/Motion-Studio; OUT=work/grillz2/final1; mkdir -p $OUT
todo=$(for f in $(seq 1 240); do [ -s $OUT/d_$(printf %04d $f).png ] || echo -n "$f,"; done); todo=${todo%,}
[ -z "$todo" ] && { echo ALLDONE; exit 0; }
PYTHONPATH=tools/py312 nice blender -b work/grillz2/anim.blend -P scripts/denoise/oidn_render.py -- --out $OUT --start 1 --end 240 --frames $todo --spp 48 --pct 67 --persistent > work/grillz2/final1.log 2>&1
ls $OUT/*.png | wc -l
