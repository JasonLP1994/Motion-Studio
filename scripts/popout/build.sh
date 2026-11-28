#!/bin/bash
# Pop Out lyric video: render frames -> light lens pass (no ghosts; big type) -> ice_chrome finish -> Ice Chrome LUT -> encode.
# Never overwrites. Usage: bash scripts/popout/build.sh v4
set -e; cd "$(dirname "$0")/../.."; V=${1:-v4}; D=work/popout/$V
mkdir -p $D
[ "$(ls $D/raw 2>/dev/null | wc -l)" -ge 901 ] || npx remotion render src/index.ts Popout $D/raw --sequence --image-format=png --concurrency=4 --log=error
[ "$(ls $D/lens 2>/dev/null | wc -l)" -ge 901 ] || PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py $D/raw $D/lens --preset cover --streak 0.06 --ghost 0 --leak 0.12 --leak-colors "0.55,0.75,1.0;0.85,0.92,1.0" --fps 30
[ "$(ls $D/fin 2>/dev/null | wc -l)" -ge 901 ] || bash scripts/finish/finish.sh $D/lens $D/fin scripts/finish/themes/ice_chrome.yaml 0.8
PYTHONPATH=tools/finish-py python3 scripts/finish/apply_lut.py $D/fin $D/lut scripts/finish/luts/ice_chrome.cube 0.85
npx remotion ffmpeg -n -loglevel error -framerate 30 -start_number 0 -i "$D/lut/element-%03d.png" -i public/popout/track.wav \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart renders/popout-lyric-$V.mp4
echo DONE renders/popout-lyric-$V.mp4
