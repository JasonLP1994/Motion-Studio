# Motion graphics workspace: working rules

The user is a beginner. Before each step, say in one short sentence what you're doing and why.
Ask before installing anything outside this folder.

## Finished-video delivery — STRICT: local/Claude download, never GitHub
- **GitHub is only for source code, skills, instructions and reusable design templates, not finished videos or user footage.** Do not upload, commit, push, attach to a GitHub issue/PR, create a GitHub Release/Action artifact for, or otherwise store final MP4/MOV/video files in the repository.
- Work entirely in the current local project or Claude's working environment. Put final, versioned MP4 exports in `renders/` (or another ignored local folder), and return the **actual finished file directly to the user via Claude's download/file mechanism** when available. When using Claude Code on the user's Mac, give the explicit local file path since it is already on their machine; when using a remote/cloud session, provide a direct downloadable attachment or the UI's download route, **not a GitHub link**.
- Do not say "finished" until the file exists, playback has been reviewed, and the output is verified. If direct file attachment/download is unavailable in the environment, say so and give the local result path and a safe manual retrieval method.
- Source media, extracted audio, transcripts, renders, caption outputs, proxies, and ZIP deliverables are **local artifacts**. Keep them ignored, and never override the media exclusions in `.gitignore`. Preserve originals and keep versions (`v1`, `v2`) for revisions.
- A few existing small `templates/*/preview.mp4` assets and intro/sample audio files pre-date this rule and remain part of the current style-kit history; **do not add any new video previews to GitHub**. Never delete existing preview assets without user approval.
- No automatic upload to other services or paid storage. Sending or scheduling content outside this local handoff requires the user's explicit approval.

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
## Specialist video-production skills (Claude Code; choose per task)
- `.claude/skills/longform-to-shorts/SKILL.md`: when asked to repurpose long-form **Phillips English YouTube footage**, select up to four genuine self-contained teaching segments, use transcript-mapped edit decisions, reframe to 9:16, add relevant graphics and render versioned Shorts. Never invent quotes; never schedule posts without approval.
- `.claude/skills/short-form-video/SKILL.md`: hook and retention-oriented vertical editing. Use only where the user wants Shorts/Reels/TikToks; it is not a mandate to cut every few seconds.
- `.claude/skills/caption-animation/SKILL.md`: word-timed active captions and exports. Use local Whisper, existing `th-captions` resources and original edited dialogue; do not install a separate transcription service.
- `.claude/skills/motion-art-direction/SKILL.md`: define a distinct visual treatment per video from the user's approved references, not a global brand-wide animation preset. **User art direction always wins over named personality defaults.**
- `.claude/skills/shot-composition/SKILL.md`: frame subjects, camera movement, negative space and format-specific safe zones; re-compose for vertical rather than squashing a wide recording.
- All four imported skills are MIT-licensed; see `.claude/skills/IMPORTED-SKILLS.md` and each skill's local LICENSE. These are **documentation/reference skills**; nothing was installed or executed just by adding them.
- **Routing:** a normal lesson edit → the user's chosen template or art direction (read `mia-motion-graphics/SKILL.md` and `notes/craft.md`); existing long-form to Shorts → longform-to-shorts, short-form-video, caption-animation, shot-composition as needed; art-direction or style request → motion-art-direction. Use only relevant skills, never stack every style into one video.

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
