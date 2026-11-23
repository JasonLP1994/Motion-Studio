#!/bin/bash
# Finish the Rubyred film once the real Cycles frames exist (renders/frames/ruby-full-v12/d_NNNN.png):
# 1) copy to a sequence, 2) RIFE-fill the in-betweens (cut frames are real on both sides, so nothing blends across a cut),
# 3) compact AI upscale 1280x720 -> 1920x1080 into public/ruby/frames/f_NNNN.png, 4) Remotion RubyFilm (3D + logo ending),
# 5) mux the -14 LUFS soundtrack. Never overwrites: pass the version, e.g. bash scripts/ruby_finish.sh v1
set -e; cd "$(dirname "$0")/.."
V=${1:-v1}; SRC=renders/frames/ruby-full-v14; SEQ=renders/frames/ruby-seq-v14; UP=public/ruby/frames
OUT=renders/rubyred-film-$V.mp4; [ -e "$OUT" ] && { echo "exists: $OUT"; exit 1; }
mkdir -p "$SEQ" "$UP"
for f in "$SRC"/d_*.png; do n=$(basename "$f" .png); [ -e "$SEQ/f_${n#d_}.png" ] || cp "$f" "$SEQ/f_${n#d_}.png"; done
PYTHONPATH=tools/rife tools/ai-venv/bin/python scripts/ai/interpolate.py --fill "$SEQ" --threads 4
echo "sequence: $(ls "$SEQ" | wc -l) frames"
tools/ai-venv/bin/python scripts/ai/upscale.py "$SEQ" "$UP" 1920 1080 --model fast --threads 4 --skip-existing
npx remotion render src/index.ts RubyFilm "renders/frames/rubyred-film-$V-silent.mp4" --codec=h264 --crf=16 --log=error
ffmpeg -v error -i "renders/frames/rubyred-film-$V-silent.mp4" -i renders/frames/ruby-sound/ruby-sound-v2.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 320k -shortest "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "DONE $OUT"
