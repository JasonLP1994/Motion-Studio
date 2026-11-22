#!/bin/bash
# Assemble the Mutant cover once the 3D layer (258 frames) and the full-size logo mark are done:
# copy frames into public/, render the Remotion composition, mux the soundtrack at -14 LUFS, make a silent copy, contact sheet.
set -e
cd /home/user/Motion-Studio
V=${1:-v1}
[ "$(ls work/mutant/frames/f_*.png | wc -l)" -ge 258 ] || { echo "3D not finished"; exit 1; }
mkdir -p public/mutant/frames && cp work/mutant/frames/f_*.png public/mutant/frames/
[ -f public/mutant/logo-mark.png ] || python3 scripts/mutant_logo.py work/mutant/frames/logo_pass.png public/mutant/logo-mark.png
python3 scripts/mutant_audio.py public/mutant/mutant.wav
npx remotion render MutantCover renders/mutant-cover-$V-silent.mp4 --codec=h264 --crf=16 --log=error
LUFS=$(ffmpeg -nostats -i public/mutant/mutant.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
GAIN=$(python3 -c "print(round(-14-($LUFS),2))")
ffmpeg -v error -y -i renders/mutant-cover-$V-silent.mp4 -i public/mutant/mutant.wav -af "volume=${GAIN}dB,alimiter=limit=0.89:level=false" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest renders/mutant-cover-$V.mp4
ffmpeg -nostats -i renders/mutant-cover-$V.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
mkdir -p notes/frames/mutant-cover-$V && ffmpeg -v error -y -i renders/mutant-cover-$V.mp4 -vf "fps=1.5,scale=480:-1,tile=6x3" -frames:v 1 notes/frames/mutant-cover-$V/contact.jpg
echo "ASSEMBLED renders/mutant-cover-$V.mp4"
