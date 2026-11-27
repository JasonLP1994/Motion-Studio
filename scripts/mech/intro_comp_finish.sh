#!/usr/bin/env bash
# Samurai intro v2+: compositing + Steel Noir grade over the v1 look frames, rebuilt glitch end card, encode with sound.
#   bash scripts/mech/intro_comp_finish.sh v2
set -euo pipefail
V=${1:?version, e.g. v2}
LOOK=renders/frames/intro2-look-v1; COMP=renders/frames/intro2-comp-$V
LUT=luts/samurai-steel-noir.cube
SND=renders/frames/samurai-sound/samurai-sound-v1c.wav; OUT=renders/samurai-intro-$V.mp4
[ -e "$OUT" ] && { echo "refusing to overwrite $OUT"; exit 1; }
tools/ai-venv/bin/python scripts/mech/intro_comp.py "$LOOK" "$COMP" "$LUT"
[ -e "$COMP/f_0361.png" ] || tools/ai-venv/bin/python scripts/post/glitch_endcard.py "$COMP/f_0360.png" work/endcard/logo-src.png "$COMP" 361 90
ffmpeg -v error -framerate 30 -start_number 1 -i "$COMP/f_%04d.png" -i "$SND" -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "DONE $OUT"
