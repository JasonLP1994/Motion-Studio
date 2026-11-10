# Phillips English Teaching Graphics

A transcript-led editorial skill for Phillips English lessons. Designed for the existing Remotion workspace; does not need a paid AI video service.

**Use it in Claude Code:**
> Use the Phillips English teaching graphics skill to edit the video in inputs/. Transcribe it locally, choose graphics that illustrate the actual English teaching, keep the presenter visible, and render a polished 1080p MP4.

The five built-in visuals: sentence correction, pronunciation, vocabulary upgrade, interview structure and professional conversation. The Remotion overlay source is in `src/teaching/` and can be layered onto existing footage.

The instructions in `SKILL.md` are the workflow. `CLAUDE.md`, Mia's Motion Graphics skill, `notes/craft.md` and `notes/checks.md` remain authoritative.

**Review sample:** `npm run dev` and open the `PhillipsEnglishTeachingDemo` composition. The sample is explicitly illustrative; replace sample text and times with a real transcript for production.

**No extra packages:** Uses the repository's existing React, Remotion and Inter font dependencies.

## Art direction is always flexible
This skill analyses *what to illustrate* and when to show it; **you choose the look every time**. A Daily Duppy-inspired video should use `templates/duppy-hype/` and may use hard typography, punch-in cuts, bold colour and energetic pacing. Cinematic, experimental, playful and minimalist looks are equally valid. The sample card design is optional and accepts `design` overrides for palette/font/energy/layout; it is **not a global style requirement**. The skill never modifies the existing styles or templates.
