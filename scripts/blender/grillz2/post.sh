#!/bin/bash
# post pipeline for the grillz animation: AI 2x upscale (720p -> 1080p) -> lens pass -> finishing grade -> encode (+ silent copy)
set -e; cd /home/user/Motion-Studio; V=${1:-v1}; W=work/grillz2
PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py $W/final1 $W/up1 1920 1080 --model fast --skip-existing
PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py $W/up1 $W/lens1 --preset cover --leak-colors "1.0,0.1,0.6;1.0,0.85,0.1"
bash scripts/finish/finish.sh $W/lens1 $W/fin1 scripts/finish/themes/cover_punch.yaml 0.8
F=$(ls $W/fin1/*.png | head -1); PAT=$(dirname $F)/$(basename $F | sed -E 's/[0-9]{4}\.png$/%04d.png/')
npx remotion ffmpeg -n -loglevel error -framerate 24 -i "$PAT" -i audio/grillz/grillz-anim-v1.wav -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart renders/grillz-anim-$V.mp4
npx remotion ffmpeg -n -loglevel error -framerate 24 -i "$PAT" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart renders/grillz-anim-$V-silent.mp4
ls -la renders/grillz-anim-$V*.mp4
