# Motion Studio video quality helpers

These lightweight scripts support the installed short-form/caption skills.

- `bash scripts/contact-sheet.sh renders/check.png notes/frames/first.png notes/frames/mid.png notes/frames/last.png` — combine stills into a single contact sheet, so editing can be checked as one set.
- `bash scripts/probe-mp4.sh renders/example.mp4 1080x1920 30` — report actual codec, fps, duration, dimensions and fail if resolution or fps differ from expectations.

**Run with `bash`**, because files created through the GitHub Contents API may not have the executable bit set. These scripts use the system `ffmpeg`/`ffprobe` and do not contact any server, install packages, modify original footage or require API credits.

Source: `iart-ai/tiktok-video-skills/scripts/`, MIT. See `scripts/IMPORTED-HELPERS-LICENSE` and `.claude/skills/IMPORTED-SKILLS.md`.

These helpers inspect existing assets; they are not a substitute for inspecting the real video and audio before sign-off.
