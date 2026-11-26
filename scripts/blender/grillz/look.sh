#!/bin/bash
# quick look: build -> Cycles + OIDN. Usage: work/grillz/look.sh NAME [SPP] [PCT]
cd /home/user/Motion-Studio; N=$1; SPP=${2:-24}; PCT=${3:-50}
PYTHONPATH=tools/py312 blender -b --factory-startup -P work/grillz/grillz.py -- save work/grillz/grillz.blend 2>&1 | grep -E "SAVED|Error|Trace|line [0-9]"
rm -rf work/grillz/$N; PYTHONPATH=tools/py312 nice blender -b work/grillz/grillz.blend -P scripts/denoise/oidn_render.py -- --out work/grillz/$N --start 1 --end 1 --spp $SPP --pct $PCT > work/grillz/$N.log 2>&1
ls work/grillz/$N/d_0001.png && echo DONE
