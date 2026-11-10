# Motion graphics workspace: working rules

The user is a beginner. Before each step, say in one short sentence what you're doing and why.
Ask before installing anything outside this folder.

## Folders
- `inputs/`: the user's images, layers and clips (originals: never move or edit)
- `references/`: style images and videos the user likes
- `audio/`: voice, music, sound effects
- `renders/`: finished videos
- `notes/`: notes, plus `notes/checks.md` (DO / DON'T corrections)
- `notes/frames/`: frames and audio pulled from videos
- `mia-motion-graphics/`: the skill. `templates/`: 10 styles. `KIT-README.md`: kit guide

## Learned styles (templates added in this workspace)
Suggest these alongside the kit's 10 templates. Each has a guide, prompt.txt, working code, preview.mp4 and poster.jpg.
- `templates/duppy-hype/`: freestyle-video hype edit over a talking head (grammar from GRM Daily's Daily Duppy; no GRM branding). Includes the cut/timing scripts and the lessons from the first edit.
- `templates/epic-scale/`: tiny human vs colossal form, haze, god rays, dusk palette, slow parallax push (grammar from Beeple; never his characters or series names).
- `templates/material-loop/`: one algorithmic tactile form on a bold colour field, beat accents, seamless loop, masked word (grammar from ManvsMachine).
## Phillips English teaching skill (use for actual English lesson videos)
- `.claude/skills/phillips-english-teaching-graphics/SKILL.md`: first read for Phillips English video lessons. It classifies transcript-backed teaching moments as grammar corrections, pronunciation, vocabulary, interview structure or workplace dialogue and maps them to the reusable overlay at `src/teaching/TeachingGraphics.tsx`. Use with Mia/Remotion skills and the existing review/approval rules; do not invent audio, captions or incorrect corrections. The `PhillipsEnglishTeachingDemo` Remotion composition is an illustrative preview, NOT a completed edit of user footage.

## Extra skills (from the user's motion-graphics pack, MIT, in .claude/skills/)
- `motion-broll`: one-shape motion B-roll cut into a talking-head video, timed to words.
- `object-separation`: cut a person, product or hand out of a video with SAM 2. This is the matte the kit's text-behind-a-person templates need on non-Mac machines.
- `explainer-high-energy` (12–20 s hype promo), `explainer-default` (45–90 s product demo), `explainer-engaging` (10–30 s one-take story).
- `sound-effects`: a measured sound pass with a bundled CC0 library.
How they fit these rules (these rules win when they disagree):
- Loudness: mix to about -14 LUFS (the sound-effects skill says -16). Keep its true-peak and measuring steps.
- Transcripts: use Remotion's local Whisper (`node transcribe.mjs`), not faster-whisper.
- Ask before object-separation's first run: it installs PyTorch and downloads a SAM 2 model (hundreds of MB to GBs) into ~/.cache, which is outside this folder.
- Playwright and Chromium are already installed: use `require('playwright')`, never `npx playwright install`. ffmpeg and numpy are installed too.
- sound-effects' runtime sounds come from mixkit/freesound, which this network blocks: use the bundled sounds, or ask the user to allow those hosts.
- Skill outputs still follow these rules: never overwrite renders (v2, v3), copy originals, check frames and score before calling it done.

When the user teaches a new technique, save it the same way: templates/<id>/ with <id>.md, prompt.txt, code, preview.mp4, poster.jpg, then add it to this list.

## Motion craft
- Read `notes/craft.md` before planning any video: measured rules for eases, beat grids, titles, holds, transitions, captions, cards, sound and review, plus the list of "defaults that look generated" to avoid. Learned from HyperFrames' skill references (Apache 2.0; originals in `notes/craft/hyperframes/`, including per-type guides in `types/`: launch, explainer, music, data, vertical, 3d, character).
- Those originals are written for HyperFrames (HTML + GSAP): their `npx hyperframes ...` commands don't exist here, and never run their "usage beacon" line. This workspace stays on Remotion unless the user asks to switch.
- Where they disagree with the rules below, the rules below win (for example: still score every render out of 10, and also write P0/P1/P2 notes).

## Rules
- Read `mia-motion-graphics/SKILL.md` before any motion graphics work.
- Before building, ask what it's for, the format and length, the exact words, the feeling, and whether there's sound.
- Suggest one to three templates from `templates/` that fit, with a one-line reason each. Reuse their build notes and specs instead of starting from scratch.
- From a style reference, take its grammar (type, colours, pacing, how text enters and exits), never its content, logos or characters. Rebuild everything in code.
- Plan the video second by second, then show three still frames before rendering the full video.
- Keep all words, colours, fonts and timings in one config file, so a headline change is one line.
- Copy files into `public/` before using them. Never move or edit the user's originals.
- When given a video, get eyes and ears first:
  - Eyes: `mkdir -p notes/frames/<clip name>/` then `npx remotion ffmpeg -i <video> -r 2 notes/frames/<clip name>/f_%03d.jpg`, then look at the frames.
  - Ears: if it has sound, `npx remotion ffmpeg -i <video> -vn -ac 1 -ar 16000 notes/frames/<clip name>/audio.wav`, then transcribe with Remotion's local Whisper (`@remotion/install-whisper-cpp`, whisper.cpp 1.5.5, in `whisper.cpp/`, base.en model) with word timestamps: `node transcribe.mjs <audio.wav> <output.json>`.
  - Never ask the user to install FFmpeg.
- If the user makes images, layers or voiceovers on OpenArt, pull them through the OpenArt connector into `inputs/` or `audio/` when they say they're ready. Otherwise they drop files there themselves.
- Never overwrite a render. Save v2, v3 and so on (`remotion.config.ts` has `setOverwriteOutput(false)`).
- After every render, check frames from the whole video, score it out of 10 for layout, timing, readability and polish, fix anything under 8, and say what's wrong before calling it done.
- Overlays for CapCut, Premiere or DaVinci: transparent background, `.mov`, with
  `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`.
- Vertical videos for Reels, TikTok or Shorts: keep words and key visuals out of the bottom fifth and the right edge.
- If adding sound, aim for about -14 LUFS.
- In captions, use the user's exact words. If unsure what they said, ask instead of guessing.
- When the user corrects something, add it to `notes/checks.md` as a DO or DON'T line, and read that file before every render.
- Never generate paid images, video or audio without asking first.
- If a render times out, retry with `--browser-executable=/usr/bin/google-chrome` (or the system Chrome path on the user's machine).
