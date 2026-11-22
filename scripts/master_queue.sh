#!/bin/bash
# Resumable master render queue (run as a tracked background task; relaunch after each 2 h limit, every step skips finished work).
# 1) Mutant 3D -> 2) Mutant logo pass -> 3) Phone case v2 (Cycles + OIDN, 145 real frames) -> 4) RIFE fill -> 5) speed-ramp retime -> 6) AI upscale -> 7) lens pass -> 8) finishing pass (postfx).
cd /home/user/Motion-Studio
while pgrep -f "blender.*mutant/mutant.py" >/dev/null; do sleep 30; done
if [ "$(ls work/mutant/frames/f_*.png 2>/dev/null | wc -l)" -lt 258 ]; then
  NO_OVERWRITE=1 PYTHONPATH=tools/py312 blender -b --factory-startup -P work/mutant/mutant.py >> work/mutant/render.log 2>&1
fi
[ "$(ls work/mutant/frames/f_*.png | wc -l)" -ge 258 ] || exit 1
if [ ! -f work/mutant/frames/logo_pass_full.done ]; then
  PYTHONPATH=tools/py312 blender -b --factory-startup -P work/mutant/mutant.py -- logo > work/mutant/logo.log 2>&1 \
    && python3 scripts/mutant_logo.py work/mutant/frames/logo_pass.png public/mutant/logo-mark.png && touch work/mutant/frames/logo_pass_full.done
fi
echo "mutant 3D + logo done" > work/master_queue.status
PYTHONPATH=tools/py312 blender -b work/blender/case/case_v2_final.blend -P scripts/denoise/oidn_render.py -- \
  --out work/blender/case/v2_frames --start 1 --end 240 --frames "$(cat work/blender/case/v2_frames.txt)" --persistent >> work/blender/case/v2_render.log 2>&1
n=$(ls work/blender/case/v2_frames/d_*.png | wc -l); [ "$n" -ge 145 ] || exit 1
mkdir -p work/blender/case/v2_seq && for p in work/blender/case/v2_frames/d_*.png; do b=$(basename $p); cp -n "$p" "work/blender/case/v2_seq/f_${b#d_}"; done
PYTHONPATH=tools/ai-py:tools/rife .object-separation/bin/python scripts/ai/interpolate.py --fill work/blender/case/v2_seq --threads 4 >> work/blender/case/v2_rife.log 2>&1
PYTHONPATH=tools/ai-py:tools/rife THREADS=4 .object-separation/bin/python scripts/ai/retime.py work/blender/case/v2_seq work/blender/case/v2_retimed work/blender/case/v2_retime.json >> work/blender/case/v2_retime.log 2>&1
PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py work/blender/case/v2_retimed work/blender/case/v2_up 1080 1920 --model fast --threads 4 --skip-existing >> work/blender/case/v2_up.log 2>&1
PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py work/blender/case/v2_up work/blender/case/v2_lens --preset product >> work/blender/case/v2_finish.log 2>&1
bash scripts/finish/finish.sh work/blender/case/v2_lens work/blender/case/v2_final scripts/finish/themes/product_premium.yaml 0.9 >> work/blender/case/v2_finish.log 2>&1
echo "case v2 done $(ls work/blender/case/v2_up/*.png | wc -l)" >> work/master_queue.status
