#!/bin/bash
# render one hero-frame option (env vars = camera) at half res and drop it into the HUD layout. Usage: opt.sh NAME
cd /home/user/Motion-Studio; N=$1
PYTHONPATH=tools/py312 blender -b --factory-startup -P work/cyber3/pd01c.py -- save work/cyber3/opt_$N.blend 2>&1 | grep -E "Error|Trace"
PYTHONPATH=tools/py312 nice blender -b work/cyber3/opt_$N.blend -P scripts/denoise/oidn_render.py -- --out work/cyber3/opt_$N --start 1 --end 1 --spp 16 --pct 50 > /dev/null 2>&1
python3 -c "
from PIL import Image
Image.open('work/cyber3/opt_$N/d_0001.png').resize((1920,1080),Image.LANCZOS).save('public/pd01/figure_opt.png')"
sed -i 's|figure: \"pd01/[^\"]*\"|figure: \"pd01/figure_opt.png\"|' src/pd01/config.ts
npx remotion still PD01HUD work/cyber3/hud_opt_$N.png --frame=80 > /dev/null 2>&1 && echo DONE $N
