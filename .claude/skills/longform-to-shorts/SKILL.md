---
name: longform-to-shorts
description: Select and edit 3-5 compelling vertical Shorts from an existing long-form Phillips English YouTube recording, using real word-level transcript timing, safe reframing, a per-video art direction and motion graphics that explain the lesson. Preserve the original content and deliver rendered clips plus source timecodes.
---

# Long-form YouTube → Shorts (Phillips English)

## What this skill does
Given an **already-recorded** long-form video, identify its best self-contained teaching moments and turn them into **finished 9:16 Shorts** without asking the presenter to film new material. It is an **editorial extraction skill**, not an invitation to write fictional quotes, reconstruct dialogue, change the subject or impose a uniform visual style.

Default for Phillips English: aim for **four strong Shorts per long-form recording**, supporting two long videos and eight Shorts per month. If the source contains fewer than four genuine, usable moments, report the shortage rather than inventing material or forcing weak clips. Follow the user's explicit requested count, length and art direction if different.

Read **CLAUDE.md**, **notes/checks.md**, **notes/craft.md**, and, as needed:
- **.claude/skills/short-form-video/SKILL.md** — hook, educational payoff, vertical pacing
- **.claude/skills/caption-animation/SKILL.md** — transcript-verified captions; avoid double-captioning
- **.claude/skills/shot-composition/SKILL.md** — reframe shot-by-shot
- **.claude/skills/motion-art-direction/SKILL.md** — select a different style for each video as directed
- **.claude/skills/motion-broll/SKILL.md** and **templates/** — optional genuinely useful animation treatments

## Source and transcription
1. Read the source file from `inputs/`; never edit, overwrite or relocate the original. Use `public/` copies for Remotion.
2. Inspect video frames (camera cuts, position, subtitles, signage and hands) and audio as instructed by `CLAUDE.md`. Record findings and source metadata (duration, fps, dimension).
3. Use the already-configured local Whisper workflow (`transcribe.mjs`) to extract **word timestamps**. Correct obvious names and specialised terminology, checking the recording; do not guess.
4. Keep source and output timebases separate. A cut map must name the exact source in/out and rendered out time. Transformed captions must follow the **rendered** edit, not the uncut original timeline.
5. Keep the original speaker and recorded speech. You may tighten pauses, remove repeated attempts and join contiguous phrases **only if the meaning and grammatical explanation remain accurate**.

## Select high-value moments
Scan the entire transcript and shortlist 6–10 candidates, then choose the strongest 4 by evidence:
- A common mistake → correction → memorable reason → useful example.
- A business meeting, negotiation or interview phrase with a concrete scenario.
- One pronunciation contrast that is demonstrated clearly on the recording.
- One surprising but accurate British English distinction, idiom or natural alternative.
- A self-contained challenge or question with its actual answer included.

**Reject** a moment that relies on unshown context, leaves out a caveat, contains an unresolved correction, makes a claim unsupported by the source, includes private student information, has problematic audio or cannot fit a useful teaching arc after trimming.

A Short should usually have **one core learning takeaway**, not four unrelated grammar points. Start with a recorded hook or a legitimate exact phrase drawn from the source; rearranging recorded speech to make a misleading promise is not allowed. Do not write new lines for the speaker. On-screen editorial headings may summarise accurate material and must not be presented as verbatim quotes.

## Selection report
Write `notes/shorts-plan.md` with a table:
`Short | title / one takeaway | source in-out(s) | source exact hook | payoff | expected output duration | planned graphics | aspect/crop risk | chosen style | confidence`

Also provide:
- Why each candidate will work as a standalone teaching clip.
- Any source sentence that cannot be removed without misrepresenting the explanation.
- One-sentence edit direction for each (e.g. high-energy Daily Duppy-inspired, editorial, podcast-clean, or a new reference-led look).
- One title/caption concept per clip (marketing text is separate from teacher's actual dialogue).

If the user previously chose a specific look for this video, **reuse it**; do not quietly reset to the same default cards. If each Short has its own authorised treatment, document them separately. If no art direction is specified, suggest 1–3 genuine options from the installed styles.

## Build
1. Create an explicit source-to-output edit decision list (EDL) per Short. Work frame-accurately with the source FPS and selected output FPS. Recompute transcript time offsets after cuts.
2. Target 1080×1920 by default. **Reframe per shot**: show a mobile crop test that preserves the face, hands, microphones and meaningful graphics; use clean layout extension / intelligent restacking when a simple central crop loses meaning. Never squash the video.
3. Build visual teaching cues from the transcript (only where they clarify the lesson), rendered in the **chosen art direction**. For a Daily Duppy-inspired Short, prefer the `duppy-hype` style and its expressive lyric captions rather than generic rounded cards.
4. Make captions word-accurate using source transcript mapped through the EDL, and do not place a second caption track on top of existing readable text. Check platform safe areas.
5. Keep the voice clear; preserve original audio and use sound effects or background music only when they improve the edit and the user has the rights. Follow workspace loudness and peak checks.
6. Deliver original-source master untouched; output each Short to `renders/` as a new version (`<topic>-short-01-v1.mp4`, etc.), plus editing project files and the EDL. Don't overwrite prior renders.

## Quality gates
Check three stills (opening hook, densest teaching moment, payoff) **per Short**, then sample frames around each cut and caption change, render a brief proof, and inspect the full output.

Score at least these categories out of 10: **English accuracy**, **clarity of the standalone payoff**, **word sync**, **visual art direction**, **phone readability**, **audio intelligibility**. Fix under-8 categories before final delivery. Use P0/P1/P2 severity to log defects and corrections.

Explicitly verify:
- No dropped negations, distorted corrections, chopped words or wrong sentence labels.
- Crops keep the presenter visible whenever their expressions support the lesson.
- High-energy visual styling never compromises the exact educational explanation.
- Captions correspond to the *final trimmed audio*, not the source.
- First frame works as a hook; no unwanted black frame; full teaching answer is included.
- No forced looping that makes the educational explanation incorrect.
- No branded third-party graphics copied from a reference, only an original expression of its motion language.

## Storage and file delivery: non-negotiable
- Render and keep every final MP4 and editable output **locally** in `renders/` or another ignored directory, never in GitHub or a GitHub-linked artifact system.
- Give the user finished **downloadable files directly through Claude** when the client supports attachments/downloads; when running locally on their computer, provide the exact finished-video paths on their machine. A GitHub URL is never a substitute for the rendered MP4.
- Never stage or commit input videos, rendered clips, caption exports, ZIP packages, extracted media, working footage, or full finished project archives. See `.gitignore` and `CLAUDE.md`.
- Existing source code and lightweight skill improvements may be committed only when the user authorises repository changes. Video deliverables never are.

## Handoff
Provide four named MP4s for direct download (or exact local paths on the user's machine) when four good segments exist, and a compact report mapping each to original timecodes, what was edited, visual style and any issue needing approval. Provide optional cover-frame/title suggestions. Publishing or scheduling remains separate and requires the user's approval.

**Invoke:** "Use longform-to-shorts on my latest Phillips English video. Find four strong teaching moments, keep each standalone and accurate, apply my chosen visual direction, and render four 1080×1920 Shorts with captions and motion graphics."
