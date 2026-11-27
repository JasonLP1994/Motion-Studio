#!/bin/bash
# Finish samurai intro v3: new draw + hero frames (264-494) get RIFE in-betweens, AI upscale and the camera look, then
# join v2's look frames 1-263, run the compositing + Steel Noir pass (scripts/mech/comp/intro3.json), add the glitch
# end card (495-584) and encode with the v3 soundtrack. Never overwrites: bash scripts/mech/intro3_finish.sh v3
set -e; cd "$(dirname "$0")/../.."
V=${1:-v3}; SRC=renders/frames/intro3-full-v1; SEQ=renders/frames/intro3-seq-v1; UP=renders/frames/intro3-up-v1
OLD=renders/frames/intro2-look-v1; LOOK=renders/frames/intro3-look-v1; COMP=renders/frames/intro3-comp-$V
SND=renders/frames/samurai-sound/samurai-sound-v3.wav; OUT=renders/samurai-intro-$V.mp4
[ -e "$OUT" ] && { echo "exists: $OUT"; exit 1; }
if [ ! -e "$LOOK/f_0494.png" ]; then
  mkdir -p "$SEQ" "$UP"
  for f in "$SRC"/d_*.png; do n=$(basename "$f" .png); [ -e "$SEQ/f_${n#d_}.png" ] || ln "$f" "$SEQ/f_${n#d_}.png"; done
  PYTHONPATH=tools/rife tools/ai-venv/bin/python scripts/ai/interpolate.py --fill "$SEQ" --threads 4
  echo "sequence: $(ls "$SEQ" | wc -l) frames"
  tools/ai-venv/bin/python scripts/ai/upscale.py "$SEQ" "$UP" 1920 1080 --model fast --threads 4 --skip-existing
  rm -rf "$SEQ"
  tools/ai-venv/bin/python scripts/post/finish_look.py "$UP" "$LOOK" --delete-src --vig 0.30
fi
for i in $(seq 1 263); do f=$(printf "f_%04d.png" $i); [ -e "$LOOK/$f" ] || ln "$OLD/$f" "$LOOK/$f"; done
COMP_CFG=scripts/mech/comp/intro3.json tools/ai-venv/bin/python scripts/mech/intro_comp.py "$LOOK" "$COMP" luts/samurai-steel-noir.cube
[ -e "$COMP/f_0495.png" ] || tools/ai-venv/bin/python scripts/post/glitch_endcard.py "$COMP/f_0494.png" work/endcard/logo-src.png "$COMP" 495 90
ffmpeg -v error -framerate 30 -start_number 1 -i "$COMP/f_%04d.png" -i "$SND" -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "DONE $OUT"
