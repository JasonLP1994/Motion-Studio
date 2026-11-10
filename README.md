# Motion-Studio
Motion design for my videos

A Remotion workspace set up for making motion graphics by chatting with Claude.

## What's inside
- `CLAUDE.md`: the working rules Claude follows in every chat here.
- `templates/`: 13 styles: the 10 from Mia's Motion Graphics Kit, plus 3 learned ones (`duppy-hype`, `epic-scale`, `material-loop`). Each has a guide, a fill-in prompt, code, a preview and a poster.
- `mia-motion-graphics/`: the kit's skill (`SKILL.md`), media tools and terms.
- `.claude/skills/`: Remotion skills, plus the motion-graphics pack (motion B-roll, object separation, three explainer styles, sound effects).
- `notes/craft.md`: motion craft rules (eases, beat grids, titles, transitions, captions, sound, review), learned from HyperFrames' references in `notes/craft/hyperframes/`.
- `src/`: the code: the Phillips English intro (`src/intro/`), the Duppy-style edit (`src/duppy/`) and the style demos (`src/styles/`).
- `scripts/`: cut-and-timing tools for talking-head edits. `transcribe.mjs`: local Whisper transcription with word timings.
- **New video specialist skills:** `.claude/skills/longform-to-shorts/` (four Shorts from one existing video); `short-form-video/` (vertical storytelling); `caption-animation/` (word-synchronised captions); `motion-art-direction/` (per-video creative treatment); and `shot-composition/` (framing / aspect ratios).
- **Motion craft skills (added from the research report):** `beat-sync-editing/` (cutting to the beat), `logo-animation/` (logo reveals and stings), `color-motion/` (palettes, colour blends, grading), `kinetic-typography/` (moving type) and `remotion-transitions/` (six custom Remotion transitions). Provenance and licences: `.claude/skills/IMPORTED-SKILLS.md`.
- **Shaders and 3D skills:** `shader-art-coding`, `shader-glsl`, `threejs-animation`, `particle-system` and seven `threejs-*` reference skills (fundamentals, geometry, materials, lighting, loaders, postprocessing, react-three-fiber), all adapted to Remotion's frame-based rendering.
- Imported skills are adapted MIT-licensed source references; provenance and retained licences: [`.claude/skills/IMPORTED-SKILLS.md`](.claude/skills/IMPORTED-SKILLS.md). No new dependencies or paid platforms were added.


## Folders for your files (not stored in this repo)
`inputs/` (clips, images), `references/` (styles you like), `audio/`, `renders/` (finished videos). Videos stay out of Git to keep the repo small.

## Getting started
```
npm ci
npm run dev
```
Whisper (for transcription) is rebuilt by the cloud environment's setup script, or by asking Claude.

## From long-form to four Shorts

Record **one** Phillips English long-form YouTube lesson, then ask Claude Code:
> Use the longform-to-shorts skill on the video in inputs/. Find four genuine standalone teaching moments, keep my exact spoken explanations, choose motion graphics that support the point, and render four 9:16 Shorts. Keep my chosen art direction (which can differ from video to video). Do not overwrite anything.

The source video stays intact; the skill uses local word-timed transcription and the existing Remotion workspace. Its four-Shorts goal is a planning default, not a reason to invent filler. Art direction remains completely flexible, including Daily Duppy-inspired edits, cinematic looks, experimental motion and clean educational explainers.


## Download the finished video directly from Claude — do not use GitHub for exports

**GitHub is the Motion Studio code-and-skills library, not video storage.** Input clips, speech, transcripts, rendered MP4s, Shorts, caption files and ZIP deliverables must stay in ignored local working folders. Claude Code renders into `renders/` and hands back the finished file directly: use the Claude file download in a cloud session, or open the local rendered MP4 on your computer when using Claude Code locally. **Never publish the finished videos to GitHub or link GitHub as the delivery method.**

The `.gitignore` excludes common media formats and render/export directories. Some *pre-existing* small style-template preview MP4s and sample audio are already tracked in the repository; these are demo assets, not your completed lesson videos, and were not removed. New preview videos should also remain local.

