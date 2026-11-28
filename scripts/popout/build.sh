#!/bin/bash
# Pop Out lyric video: render frames -> finishing pass (no lens pass: big type) -> encode with the track. Never overwrites.
# Usage: bash scripts/popout/build.sh v1
set -e; cd "$(dirname "$0")/../.."; V=${1:-v1}; D=work/popout/$V
mkdir -p $D
[ "$(ls $D/raw 2>/dev/null | wc -l)" -ge 901 ] || npx remotion render src/index.ts Popout $D/raw --sequence --image-format=png --concurrency=4 --log=error
bash scripts/finish/finish.sh $D/raw $D/fin scripts/finish/themes/product_premium.yaml 0.5
F=$(ls $D/fin | head -1); EXT=${F##*.}; PAT=$(echo "$F" | sed -E 's/[0-9]+\.'$EXT'$/%0'$(echo "$F" | sed -E 's/.*[^0-9]([0-9]+)\.'$EXT'$/\1/' | wc -c | awk '{print $1-1}')'d.'$EXT'/')
npx remotion ffmpeg -n -loglevel error -framerate 30 -start_number $(echo "$F" | sed -E 's/.*[^0-9]0*([0-9]+)\.'$EXT'$/\1/') -i "$D/fin/$PAT" -i public/popout/track.wav \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart renders/popout-lyric-$V.mp4
echo DONE renders/popout-lyric-$V.mp4
