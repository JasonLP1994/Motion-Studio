#!/bin/bash
# Assemble the Mutant cover once the 3D layer (258 frames) and the full-size logo mark are done:
# copy frames into public/, render the Remotion composition to frames, finishing pass (postfx cover_punch), encode, mux the soundtrack at -14 LUFS, make a silent copy, contact sheet.
set -e
cd /home/user/Motion-Studio
V=${1:-v1}
[ "$(ls work/mutant/frames/f_*.png | wc -l)" -ge 258 ] || { echo "3D not finished"; exit 1; }
mkdir -p public/mutant/frames && cp work/mutant/frames/f_*.png public/mutant/frames/
[ -f public/mutant/logo-mark.png ] || python3 scripts/mutant_logo.py work/mutant/frames/logo_pass.png public/mutant/logo-mark.png
python3 scripts/mutant_audio.py public/mutant/mutant.wav
rm -rf work/mutant/comp work/mutant/comp_lens work/mutant/comp_fin
npx remotion render MutantCover work/mutant/comp --sequence --image-format=png --overwrite --log=error      # composited frames
PYTHONPATH=tools/finish-py python3 scripts/finish/lensfx.py work/mutant/comp work/mutant/comp_lens --preset cover            # lens pass
for i in $(seq 249 287); do cp work/mutant/comp/element-$i.png work/mutant/comp_lens/element-$i.png; done   # no streaks on the logo end card
bash scripts/finish/finish.sh work/mutant/comp_lens work/mutant/comp_fin scripts/finish/themes/cover_punch.yaml 0.8   # finishing pass over everything
ffmpeg -v error -y -framerate 24 -pattern_type glob -i 'work/mutant/comp_fin/*.png' -vf format=yuv420p -c:v libx264 -crf 16 -preset slow -movflags +faststart renders/mutant-cover-$V-silent.mp4
LUFS=$(ffmpeg -nostats -i public/mutant/mutant.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
GAIN=$(python3 -c "print(round(-14-($LUFS),2))")
ffmpeg -v error -y -i renders/mutant-cover-$V-silent.mp4 -i public/mutant/mutant.wav -af "volume=${GAIN}dB,alimiter=limit=0.89:level=false" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest renders/mutant-cover-$V.mp4
ffmpeg -nostats -i renders/mutant-cover-$V.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
mkdir -p notes/frames/mutant-cover-$V && ffmpeg -v error -y -i renders/mutant-cover-$V.mp4 -vf "fps=1.5,scale=480:-1,tile=6x3" -frames:v 1 notes/frames/mutant-cover-$V/contact.jpg
echo "ASSEMBLED renders/mutant-cover-$V.mp4"
