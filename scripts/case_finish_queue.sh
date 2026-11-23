#!/bin/bash
# Resume the phone case v2 queue from the AI upscale step (render, RIFE fill and retime already done). Resumable.
cd /home/user/Motion-Studio
PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py work/blender/case/v2_retimed work/blender/case/v2_up 1080 1920 --model fast --threads 4 --skip-existing >> work/blender/case/v2_up.log 2>&1
PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py work/blender/case/v2_up work/blender/case/v2_lens --preset minimal >> work/blender/case/v2_finish.log 2>&1
bash scripts/finish/finish.sh work/blender/case/v2_lens work/blender/case/v2_final scripts/finish/themes/product_minimal.yaml 1.0 >> work/blender/case/v2_finish.log 2>&1
echo "case v2 finish done $(ls work/blender/case/v2_final/*.png | wc -l)" >> work/master_queue.status
