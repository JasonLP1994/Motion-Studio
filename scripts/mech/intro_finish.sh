#!/bin/bash
# Finish the samurai intro once the real Cycles frames exist (fast recipe): link real frames into a sequence, RIFE-fill
# the in-betweens, compact AI upscale to 1920x1080, camera finishing look, Phillips Digital glitch end card (frames
# 361-450), then encode with the -14 LUFS soundtrack. Never overwrites: bash scripts/mech/intro_finish.sh v1
set -e; cd "$(dirname "$0")/../.."
V=${1:-v1}; SRC=renders/frames/intro2-full-v1; SEQ=renders/frames/intro2-seq-v1; UP=renders/frames/intro2-up-v1; LOOK=renders/frames/intro2-look-v1
SND=renders/frames/samurai-sound/samurai-sound-v1c.wav; OUT=renders/samurai-intro-$V.mp4
[ -e "$OUT" ] && { echo "exists: $OUT"; exit 1; }
mkdir -p "$SEQ" "$UP"
for f in "$SRC"/d_*.png; do n=$(basename "$f" .png); [ -e "$SEQ/f_${n#d_}.png" ] || ln "$f" "$SEQ/f_${n#d_}.png"; done
PYTHONPATH=tools/rife tools/ai-venv/bin/python scripts/ai/interpolate.py --fill "$SEQ" --threads 4
echo "sequence: $(ls "$SEQ" | wc -l) frames"
tools/ai-venv/bin/python scripts/ai/upscale.py "$SEQ" "$UP" 1920 1080 --model fast --threads 4 --skip-existing
rm -rf "$SEQ"
tools/ai-venv/bin/python scripts/post/finish_look.py "$UP" "$LOOK" --delete-src --vig 0.30
[ -e "$LOOK/f_0361.png" ] || tools/ai-venv/bin/python scripts/post/glitch_endcard.py "$LOOK/f_0360.png" work/endcard/logo-src.png "$LOOK" 361 90
ffmpeg -v error -framerate 30 -start_number 1 -i "$LOOK/f_%04d.png" -i "$SND" -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "DONE $OUT"
