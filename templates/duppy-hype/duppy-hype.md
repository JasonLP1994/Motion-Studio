# Duppy hype

Style ID: duppy-hype
Shown as: Duppy hype (freestyle-video energy)
Best for: Talking heads and performances that need hype: lyric-style captions word by word, giant slam words, jump cuts with punch-ins, flashes and shakes.

Grammar learned from GRM Daily's Daily Duppy freestyle series (minimalist single-performer framing, captions that follow the delivery, emphasised punchline words, inventive effect edits) plus common hype-edit practice. Take the grammar only: never use GRM Daily's name, logo or branding. Sources: press descriptions of the series (Music Week, Pilerats, Yahoo) and this project's first edit (renders/duppy-v2.mp4). No official style guide exists, so fonts and colours below are this template's choices.

## Look
- One person, stripped-back shot, kept as filmed. Light film grain and a soft dark vignette.
- Captions: heavy condensed uppercase (Anton), white with a thick black outline and a hard drop shadow, centred at the bottom. Chosen words in accent yellow.
- Slam words: the punchline word or phrase, huge, accent yellow (or red for "bad" words like MISTAKE), RGB split (red/cyan offset), black outline, tilted 1 to 2 degrees. Over the chest, never over the face.
- Lists: black blocks with a yellow number tile, stacked in clear space beside the speaker, newest block outlined in yellow.

## Motion
- Jump cuts: pauses longer than 0.45 s cut to 0.12 s of breath on each side. Every other cut is punched in 10% around the face, for rhythm.
- Captions: each word appears on its spoken word (2 frames early at most), rising 18 px and stretching up from the baseline over 4 frames. Hidden words keep their space so the line never shifts.
- Slam: each word lands as it's spoken, from 1.4× to 1× in 4 frames (Easing.in cubic), grows downward (transform-origin top) so it never passes over the face, then a 5% spring settle. First word: 2-frame white flash at 55% and a camera punch of +14% decaying over about 6 frames. Last word: shake ±16 px decaying over 9 frames.
- About one slam per point, at most 15 to 20% of caption groups.

## Specs
- 16:9 1920×1080, 30 fps (the source can be any size; it's cover-scaled with an offsetY).
- Fonts: Anton 400 (display), Inter 800 (body), both from @fontsource files copied into public/fonts. Load with @remotion/fonts behind delayRender before measuring.
- Sizes at 1080 tall: caption 92 px, anchor caption 120 px, slam max 330 px on one line, 185 px on two lines; caption baseline y 1000; slam centre y 810.
- Palette: white #FFFFFF, accent #FFE100, danger #FF2D2D, outline #0A0A0A.

## Build
1. Eyes and ears on the source (frames + audio.wav). Check for baked-in captions; ask for a clean version if there are any.
2. `node build-timeline.mjs <audio.wav> <cutStart> <cutEnd>` → src/duppy/timeline.json (kept segments + words). It transcribes each kept piece separately, because Whisper's timings from one long file drift by up to a second.
3. Write caption groups in config.ts (copy config.example.ts): exact words, 2 to 5 per group, roles line / anchor / hero, accent words, step numbers. Group word counts must add up to the timeline's words.
4. Render a first version, then `node refine-timing.mjs <render audio.wav>` to snap every word to its real onset (binary search with Whisper), and render again. Without this, captions can land up to 0.5 s early.
5. Three stills (a slam, the busiest moment, the end), then full render, then frames from the whole video.

## Known pitfalls
- Whisper token times drift around pauses and over long files. Never trust whole-file word times for captions; always refine (step 4).
- Whisper mishears short clips ("And third" → "I'm third"). Display text comes from config, so always use the words actually said.
- Scaling a word horizontally while it pops makes it collide with its neighbours. Pop vertically only, with a wider word gap (0.28em).
- A slam word scaled from its centre grows up over the face for a few frames. Grow downward.
- Centred lines re-centre as words are added unless hidden words keep their space.
- Find the cut's end with a test transcription of the last seconds: the word after the cut can sneak in.
- Remotion's own browser download is blocked in this cloud: use the system Chrome (already set in remotion.config.ts).

## Copy prompt
See prompt.txt in this folder.
