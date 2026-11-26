#!/bin/bash
cd /home/user/Motion-Studio; N=$1; SPP=${2:-24}; PCT=${3:-50}
PYTHONPATH=tools/py312 blender -b inputs/grillz/model2/TSST.blend -P work/grillz2/grillz2.py -- save work/grillz2/grillz2.blend 2>&1 | grep -E "ROWS|SAVED|Error|Trace|line [0-9]"
rm -rf work/grillz2/$N; PYTHONPATH=tools/py312 nice blender -b work/grillz2/grillz2.blend -P scripts/denoise/oidn_render.py -- --out work/grillz2/$N --start 1 --end 1 --spp $SPP --pct $PCT > work/grillz2/$N.log 2>&1
ls work/grillz2/$N/d_0001.png && echo DONE
