#!/bin/bash
# After-Effects-style finishing pass on a rendered frame folder with postfx (MIT, 0xBeycan/postfx, CPU): grade, halation,
# vignette, chromatic aberration, clarity, sharpening, per-frame moving grain. Usage:
#   bash scripts/finish/finish.sh IN_DIR OUT_DIR [THEME (name or scripts/finish/themes/*.yaml)] [STRENGTH 0..1.5]
set -e
cd "$(dirname "$0")/../.."
IN=$1; OUT=$2; THEME=${3:-scripts/finish/themes/product_premium.yaml}; STR=${4:-0.8}
PYTHONPATH=tools/finish-py python3 -m postfx run --input "$IN" --theme "$THEME" --strength "$STR" --out "$OUT" --format png --jobs 0
