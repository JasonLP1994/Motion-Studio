# KINGZ: rotoscoped statue × streetwear graffiti (16:9, 10 s)

Picks: palette acid yellow + black + white · 16:9, full 10 s · matte used for: neon outline that tracks her, KINGZ behind her, face marks on the push-in, node labels on her · dark trap beat + SFX (+ silent copy).
Words (user, exact): "Are you coming for the KINGZ" → ARE YOU / COMING / FOR THE / KINGZ.
Footage: `inputs/statue-cathedral.mp4` (Vecteezy stock, 2560x1440, 24 fps, 10.04 s, no audio; untouched). Working copy `public/statue/clip.mp4` (1080p). Camera circles a praying stone statue, she turns, then a push-in on a cracked, smiling face (from ~7 s).
References (grammar only): chrome bear with lime neon hand-drawn outline, crown, X eyes, smile doodle, drips and an offset colour shadow; "No One Cares" streetwear poster (angular yellow brush type with outline ghost, caution-tape bands of repeated text, barcodes, XXX marks, chevrons, label boxes); the node still (yellow NODE tags, curved wires).

## Rotoscope
SAM 2 video mode (`facebook/sam2.1-hiera-large`, CPU), `scripts/statue_roto.py`: statue on all 241 frames (4 positive + 2 negative clicks on frame 0); her face from frame 169 (close-up). Masks in ignored `work/statue/`. Layers built from them: statue cut-out (so type sits behind her), outline ring, per-frame anchors (head, hands, robe, face box) for the node tags and face marks.

## Skill stack
| Skill | Job | Why |
|---|---|---|
| object-separation | SAM 2 statue + face mattes | Rotoscope pick |
| motion-art-direction | Yellow / black / white; footage graded to high-contrast B&W | Palette pick + references |
| kinetic-typography | ARE YOU / COMING / FOR THE / KINGZ slams, outline ghost, tape text | The saying |
| shot-composition | Type placed in the empty side of each framing; KINGZ behind her | Matte + framing |
| beat-sync-editing | 144 BPM = 10 frames a beat at 24 fps; every word on a beat | Trap beat |
| sound-effects | Original trap beat (code), spray hiss on graffiti, hit on KINGZ, -14 LUFS | Sound pick |

## Second by second (24 fps, 241 frames, beat = 10 f)
| Time | Frames | Footage | Graphics |
|---|---|---|---|
| 0.0–2.5 s | 0–60 | Front, praying | Neon outline draws on around her; barcodes + chevrons slide in; ARE (f10) YOU (f20) slam left |
| 1.7–2.9 s | 40–70 | | Tape band 1 sweeps across with the phrase repeated |
| 2.9–5.4 s | 70–130 | She turns side/back | COMING (f70) right; NODE_1–5 tags pinned to head, hands, robe, wired together |
| 5.4–7.1 s | 130–170 | Turns back to camera | FOR THE (f130); XXX marks pop on beats; tape band 2 crosses the other way |
| 7.0–10.0 s | 169–241 | Push-in, smile | Crown, X eyes and smile doodle drawn onto her face (tracked); KINGZ slams behind her (f190) with outline ghost + drips; hold |
