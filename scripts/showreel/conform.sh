#!/usr/bin/env bash
# Conform finished videos for a showreel: 1920x1080, 30 fps, no audio, into public/showreel/<name>.mp4.
# 16:9 sources are scaled to fill; other aspect ratios sit centred on a blurred, darkened fill of themselves.
#   bash scripts/showreel/conform.sh <video> [<video> ...]
set -euo pipefail
OUT=public/showreel; mkdir -p "$OUT"
for v in "$@"; do
  n=$(basename "${v%.*}" | sed 's/ (1)//; s/ /-/g'); o="$OUT/$n.mp4"
  [ -s "$o" ] && { echo "skip $n"; continue; }
  IFS=x read w h < <(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "$v" | head -1)
  ar=$(python3 -c "print(abs($w/$h-16/9)<0.02)")
  if [ "$ar" = "True" ]; then
    vf="scale=1920:1080:flags=lanczos,fps=30,format=yuv420p"
  else
    vf="split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:2,eq=brightness=-0.18:saturation=0.8[bg];[b]scale=-2:1080:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:0,fps=30,format=yuv420p"
  fi
  t=(); [ "$(python3 -c "print(float('$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")')>70)")" = "True" ] && t=(-t 70)
  ffmpeg -v error -i "$v" "${t[@]}" -an -filter_complex "$vf" -c:v libx264 -crf 17 -preset fast -g 15 "$o"
  echo "ok $n"
done
