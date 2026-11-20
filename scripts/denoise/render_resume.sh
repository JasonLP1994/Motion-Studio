#!/bin/bash
# Long local renders that survive interruptions: keeps calling oidn_render.py until every frame exists.
# oidn_render.py skips frames already saved, so re-running this just carries on.
# Usage (detached, logs to <out>/render.log):
#   setsid nohup bash scripts/denoise/render_resume.sh <file.blend> <out_dir> <start> <end> <pct> <spp> >/dev/null 2>&1 &
cd "$(dirname "$0")/../.."
BLEND=$1; OUT=$2; A=$3; B=$4; PCT=$5; SPP=$6
mkdir -p "$OUT"
echo $$ > "$OUT/runner.pid"
for try in $(seq 1 50); do
  missing=0
  for f in $(seq "$A" "$B"); do [ -f "$OUT/d_$(printf %04d "$f").png" ] || { missing=1; break; }; done
  [ $missing = 0 ] && { echo "ALL DONE $(date)" >> "$OUT/render.log"; exit 0; }
  echo "pass $try start $(date)" >> "$OUT/render.log"
  blender -b "$BLEND" -P scripts/denoise/oidn_render.py -- --out "$OUT" --start "$A" --end "$B" --pct "$PCT" --spp "$SPP" 2>&1 \
    | grep -E "OIDN frame|Traceback|Error" | grep -v "Not freed" >> "$OUT/render.log"
  sleep 5
done
