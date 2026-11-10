# Motion-Studio
Motion design for my videos

A Remotion workspace set up for making motion graphics by chatting with Claude.

## What's inside
- `CLAUDE.md`: the working rules Claude follows in every chat here.
- `templates/`: 13 styles: the 10 from Mia's Motion Graphics Kit, plus 3 learned ones (`duppy-hype`, `epic-scale`, `material-loop`). Each has a guide, a fill-in prompt, code, a preview and a poster.
- `mia-motion-graphics/`: the kit's skill (`SKILL.md`), media tools and terms.
- `.claude/skills/`: Remotion skills, plus the motion-graphics pack (motion B-roll, object separation, three explainer styles, sound effects).
- **Phillips English teaching graphics:** `.claude/skills/phillips-english-teaching-graphics/SKILL.md` routes spoken teaching to five accurate animation types. Reusable Remotion overlays live in `src/teaching/`; open the `PhillipsEnglishTeachingDemo` composition to preview illustrative cues.
- `notes/craft.md`: motion craft rules (eases, beat grids, titles, transitions, captions, sound, review), learned from HyperFrames' references in `notes/craft/hyperframes/`.
- `src/`: the code: the Phillips English intro (`src/intro/`), the Duppy-style edit (`src/duppy/`) and the style demos (`src/styles/`).
- `scripts/`: cut-and-timing tools for talking-head edits. `transcribe.mjs`: local Whisper transcription with word timings.

## Folders for your files (not stored in this repo)
`inputs/` (clips, images), `references/` (styles you like), `audio/`, `renders/` (finished videos). Videos stay out of Git to keep the repo small.

## Getting started
```
npm ci
npm run dev
```
Whisper (for transcription) is rebuilt by the cloud environment's setup script, or by asking Claude.
