#!/bin/bash
# build the animated scene + render chosen frames:  anim_look.sh NAME FRAMES(comma) [SPP] [PCT]
cd /home/user/Motion-Studio; N=$1; FR=$2; SPP=${3:-16}; PCT=${4:-40}
export ANIM=1 L_Z=${L_Z:-0.3} L_H=${L_H:-0.42} L_W=${L_W:-0.66} REFL_E=${REFL_E:-0.5} JAW_DROP=0
PYTHONPATH=tools/py312 blender -b inputs/grillz/model2/TSST.blend -P work/grillz2/grillz2.py -- save work/grillz2/anim.blend 2>&1 | grep -E "ANIM|SAVED|Error|Trace|line [0-9]"
rm -rf work/grillz2/$N; PYTHONPATH=tools/py312 nice blender -b work/grillz2/anim.blend -P scripts/denoise/oidn_render.py -- --out work/grillz2/$N --start 1 --end 240 --frames $FR --spp $SPP --pct $PCT > work/grillz2/$N.log 2>&1
ls work/grillz2/$N | head -20; echo DONE
