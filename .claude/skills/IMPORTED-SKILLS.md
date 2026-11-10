# Imported and custom motion/video skills — provenance

These skill documents were added to Motion Studio for Claude Code use. They **extend** the existing Remotion/Mia motion workflows and do not install new runtimes, services or paid APIs.

## Imported open-source skills

| Local path | Source | Upstream file |
|---|---|---|
| `.claude/skills/short-form-video/` | [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | `skills/short-form-video/` |
| `.claude/skills/caption-animation/` | [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | `skills/caption-animation/` |
| `.claude/skills/motion-art-direction/` | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `skills/motion-art-direction/` |
| `.claude/skills/shot-composition/` | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `skills/shot-composition/` |
| `.claude/skills/beat-sync-editing/` | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `skills/beat-sync-editing/` |
| `.claude/skills/logo-animation/` | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `skills/logo-animation/` |
| `.claude/skills/color-motion/` | [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `skills/color-motion/` |
| `.claude/skills/kinetic-typography/` | [iart-ai/kinetic-typography-skills](https://github.com/iart-ai/kinetic-typography-skills) | `skills/kinetic-typography/` |
| `.claude/skills/remotion-transitions/` | [ashad001/remotion-transitions](https://github.com/ashad001/remotion-transitions) | repo root (`SKILL.md`, `references/`, `CHANGELOG.md`) |

Source branches: `main`. Inspected source revisions:
- `iart-ai/tiktok-video-skills` — `2a775336b5a638cbf8a61dbd785f9a1b649be016`
- `iart-ai/motion-design-skills` — `3c129f769d90a1328c209c386492333c9ac62312`
- `iart-ai/kinetic-typography-skills` — `fccc94bd325d824235ee9e715e65abde57b6513a`
- `ashad001/remotion-transitions` — `2bf15881f1f9d74e4b76979cd0846aefffc9962c` (v1.0.0, MIT, © 2026 Ashad)

Added 2026-11-10 from the "Motion skills for Motion Studio" research report (`reports/`): beat-sync-editing, logo-animation, color-motion, kinetic-typography, remotion-transitions. Only the skill folders were copied (Markdown + LICENSE). The upstream repo-root helper scripts were **not** imported: `seek-shot.sh` runs `npx playwright` (which downloads its own Chromium, against workspace rules), and `contact-sheet.sh` / `probe-mp4.sh` already exist in `scripts/`. Tracking parameters were removed from iart.ai footer links; each SKILL.md has a Motion Studio integration note at the top.

Both repos publish under **MIT**. The original copyright/permission text is retained in each imported skill's `LICENSE`. Each skill includes a clearly marked **Motion Studio integration** note near its heading. The Short-form skill also has unverified "algorithm guarantee" statistics removed: editorial decisions should use actual channel analytics rather than unsupported platform thresholds.

The upstream docs sometimes refer to packages or scripts not installed in this workspace (for example `@remotion/captions` or standalone sample compositions). These are **examples, not instructions to install or execute immediately**. Reuse the repository's existing local Whisper transcription, Remotion, fonts and `th-captions` component where suitable; request approval for any new dependency. Reference examples are source materials only and not independently tested workflows.

**Licensing note:** these adaptations retain upstream MIT licence notices and acknowledgements. They do not automatically import external binaries, fonts, media, styles or runtimes.

## Custom skill

- `.claude/skills/longform-to-shorts/SKILL.md`: Motion Studio-specific orchestration designed for Phillips English. Takes existing long-form recordings, selects four genuine teaching moments, re-edits them to 9:16 while preserving exact meaning, chooses visuals based on each video's art direction, and produces versioned MP4 deliverables.

## Priority and compatibility

For any project, apply (in descending priority):

1. The **user's chosen art direction and exact instructions** for this video.
2. Verified source footage/audio/transcript, correction accuracy and legally usable media.
3. `CLAUDE.md` and `notes/checks.md` safety/quality/preservation rules.
4. Appropriate specialist skill(s) from this directory.
5. Any defaults embedded in imported skill documents.

Do not override a user's Daily Duppy-inspired or experimental direction with generic minimalist or corporate defaults. Do not force every long-form video into Shorts; invoke the extraction workflow only when asked. Preserve all source assets. No automatic posting or expense.

## Maintenance

These are pinned copies, not auto-updating dependencies. Review upstream changes before copying new versions; retain licence and re-apply Motion Studio compatibility notes. A skill file being present does **not** mean its described code examples have been executed or its output rendered.
