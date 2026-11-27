#!/bin/bash
# Finish the samurai katana-draw shot once the real Cycles frames exist (fast recipe): link real frames, RIFE-fill the
# in-betweens, AI upscale to 1920x1080, camera look, compositing + Steel Noir LUT (scripts/mech/comp/draw-shot.json),
# then encode with the -14 LUFS soundtrack. Never overwrites: bash scripts/mech/draw_finish.sh v1
set -e; cd "$(dirname "$0")/../.."
V=${1:-v1}; SRC=renders/frames/draw-full-v1; SEQ=renders/frames/draw-seq-v1; UP=renders/frames/draw-up-v1
LOOK=renders/frames/draw-look-v1; COMP=renders/frames/draw-comp-$V
SND=renders/frames/samurai-draw-sound/draw-sound-v1b.wav; OUT=renders/samurai-draw-$V.mp4
[ -e "$OUT" ] && { echo "exists: $OUT"; exit 1; }
if [ ! -e "$LOOK/f_0150.png" ]; then
  mkdir -p "$SEQ" "$UP"
  for f in "$SRC"/d_*.png; do n=$(basename "$f" .png); [ -e "$SEQ/f_${n#d_}.png" ] || ln "$f" "$SEQ/f_${n#d_}.png"; done
  PYTHONPATH=tools/rife tools/ai-venv/bin/python scripts/ai/interpolate.py --fill "$SEQ" --threads 4
  echo "sequence: $(ls "$SEQ" | wc -l) frames"
  tools/ai-venv/bin/python scripts/ai/upscale.py "$SEQ" "$UP" 1920 1080 --model fast --threads 4 --skip-existing
  rm -rf "$SEQ"
  tools/ai-venv/bin/python scripts/post/finish_look.py "$UP" "$LOOK" --delete-src --vig 0.30
fi
COMP_CFG=scripts/mech/comp/draw-shot.json tools/ai-venv/bin/python scripts/mech/intro_comp.py "$LOOK" "$COMP" luts/samurai-steel-noir.cube
ffmpeg -v error -framerate 30 -start_number 1 -i "$COMP/f_%04d.png" -i "$SND" -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "DONE $OUT"
