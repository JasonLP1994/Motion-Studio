---
name: phillips-english-teaching-graphics
description: Edit Phillips English lesson videos using transcript-led Remotion motion graphics for grammar corrections, pronunciation, vocabulary upgrades, job interviews and professional conversations. Use for talking-head lessons, YouTube explainers and Shorts. Preserve original footage and speech; choose only visuals that clarify the teaching.
---

# Phillips English Teaching Graphics

## Purpose
Transform an existing Phillips English teaching video into a clear, polished learning experience. This is an **editorial skill**, not a request to decorate a video. It selects **which educational concept merits a visual**, then uses existing Remotion tools to animate that concept in sync with the spoken lesson.

**Trigger:** Requests involving Phillips English educational videos, lecture edits, animated examples, sentence corrections, grammar, vocabulary, pronunciation, IELTS/aviation English, interviews, meetings, negotiations, or Business English. The user's instruction to "edit this lesson and add suitable motion graphics" is sufficient: inspect the content and select categories yourself.

Follow `CLAUDE.md`, `mia-motion-graphics/SKILL.md`, `notes/craft.md` and `notes/checks.md`. Their safety, approval, quality and file-preservation rules still apply. This skill supplies the **educational visual-selection system** and reusable component.

## Source of truth: the lesson
1. Identify the original footage in `inputs/` and leave it unchanged; copy only what Remotion needs to `public/`.
2. Inspect frames (including cuts) and record face, subtitles, room branding, safe empty space in `notes/shots.md`. Use the `CLAUDE.md` "eyes" workflow.
3. Extract audio with Remotion's FFmpeg and transcribe with local Whisper through `transcribe.mjs`. Do not ask for a paid transcription platform. Check ambiguous and specialised English-language words against the actual audio; do not invent transcript text.
4. Segment teaching into *claims and examples*: each candidate visual must have a supporting spoken quote/time range. Distinguish a student's actual mistake from a grammatically valid contextual alternative.
5. Start graphics **on the relevant spoken word** (typically 2–4 frames earlier), not at arbitrary intervals. Respect any user-provided transcript or exact wording.
6. Use original voice/audio, leave breathing room for the presenter's face, and make no jump cuts that change the meaning of a correction.

If only a script exists, build a design and provisional plan, but mark timings **unverified** until real word timings are available. Never present guessed timings as speech-synchronised.

## Choose the right graphic (not every line needs one)

| Spoken teaching event | Cue kind | Visual treatment | Educational requirement |
|---|---|---|---|
| A sentence is corrected, verb pattern or grammar rule explained | `correction` | Original phrase is crossed out; corrected phrase enters in teal; one short why | Do not label a valid alternative wrong. Display exact supplied/spoken wording. |
| Stress, syllables, phonemes, minimal pair, intonation | `pronunciation` | Large target word, stress pattern, optional verified IPA or syllable guidance | Use British English; confirm IPA before displaying; audio examples only if actually recorded. |
| Basic-to-precise vocabulary, collocations, idioms | `vocabulary` | Side-by-side word/phrase change, concise use/context | Preserve register and meaning; upgrades are context-dependent. |
| Job interview answer or professional presentation structure | `interview` | Question and progressive, numbered answer structure | Steps must match the spoken advice; no invented candidate results. |
| Meetings, negotiations, phone calls, professional dialogue | `conversation` | Speaker A/B conversation card, key phrase highlighted | Don't create quotations attributed to real speakers unless spoken; hypothetical examples are clearly labelled. |

**Additional topics** (IELTS, aviation, academic English): map them to the most suitable existing kind, only if the teaching idea genuinely fits. For a new concept, extend the discriminated union in `src/teaching/TeachingGraphics.tsx` rather than forcing the wrong visual.

### Density and editorial restraint
- Aim for **4–7 meaningful inserts per minute** for ordinary teaching; reduce to **2–4** when explanations are dense or the teacher's face carries the point. These are guidelines, not quotas.
- Give each idea time to read. One idea/card at a time. Avoid repeating the same original/correction after it is clear.
- Prefer a small side panel beside the presenter for phrases. Use a full-frame educational cutaway only when the whole comparison or diagram deserves it.
- Leave at least ~2 seconds of presenter-only footage between full-frame cutaways, unless a deliberate sequence makes this inappropriate.
- No floating logos, unrelated particles, generic business stock video, unnecessary swooshes, invented charts, fake example claims or captions covering the teacher's face.
- First sentence/hook should usually show the person, not a giant intro animation.

## Phillips English visual identity
The **existing working intro** at `src/intro/config.ts` is the colour reference:
- Background `#0A0E13`, charcoal `#1A232D`
- Accent **teal** `#80B8C6`; body text white `#FFFFFF`, warm secondary `#F4EFE6`
- Correct form = teal, original form = muted coral `#E88B84` (informative, not aggressive red)
- Use Inter/Montserrat already installed; avoid introducing new fonts or a conflicting gold/pink/yellow identity.
- Soft 8–14 frame entrances, 6–10 frame exits; stable text when landed; no constant floating or pulsing.
- In 16:9 default to a verified side panel, not the speaker's face or existing signage. In 9:16 use the upper readable area and avoid the platform's bottom fifth and right-edge controls.
- This skill does not overwrite the existing `Duppy`, `Intro` or other creative templates; use stronger styles only where the lesson calls for them.

## Implement with the reusable Remotion component
Files:
- `src/teaching/TeachingGraphics.tsx`: a transparent Remotion overlay component driven by typed `TeachingCue[]`.
- `src/teaching/config.ts`: palette, production-safe cue examples and timing in one place.
- `src/teaching/TeachingDemo.tsx`: a sample reel demonstrating the five types, with **illustrative** text and timings (NOT a transcript).

Use `<TeachingGraphics cues={...} />` as a layer over the source footage in the actual composition. Each cue has `kind`, `startSeconds`, `durationSeconds`, optional `side` ('left'|'right'|'full'), and type-specific text.

For actual lessons, replace the demo cues with transcript-verified lines and real timings. Keep 1 cue per distinct idea and place its panel on the side checked in `notes/shots.md`. Do not claim an overlay is finished until rendered against the footage, inspected and listened to.

## The production loop
1. Read `notes/checks.md`, `notes/craft.md`, this skill and the relevant existing Remotion skill.
2. Create `notes/teaching-plan.md` with columns: **in/out**, **spoken exact words**, **kind**, **on-screen text**, **layout/safe region**, **entrance on word**, **why this helps**.
3. Explain the visual concept briefly. Follow `CLAUDE.md` approval rules for new styles/large renders; avoid repeating answers the user already supplied.
4. Build cues from transcript, copy input into `public/`, compose footage + overlays + original audio. Use existing Remotion composition / render tools; do not re-encode audio separately unless editing requires it.
5. Show 3 still frames: most detailed correction, a pronunciation/dialogue or structure panel, and one crowded teaching frame. Check they don't hide face/website/subtitles.
6. Render a short motion proof and then the full video after approval as required by `CLAUDE.md`.
7. Inspect frames through the full edit, check spelling/meaning/phonetics and word sync. Score **accuracy, readability, timing, layout and polish** out of 10; fix any score under 8. Record P0/P1/P2 defects and fixes.
8. Deliver non-overwritten versioned MP4, an editable composition and a timing/edit manifest. If user wants separately compositable overlays, output alpha ProRes 4444 as documented in `CLAUDE.md`.

## Quality gate specific to English teaching
- **Accuracy:** Are the correction, grammatical rule, stress and register right in British English? If not confident, do not publish the graphic.
- **Verbatim vs example:** Transcript quotations are exact; invented illustrative examples must be visibly distinct from quotes and not attributed to students or clients.
- **Timing:** Each cue lands as the relevant words are said; no graphics ahead of the explanation that spoil the teaching point.
- **Accessibility:** Legible at 360px mobile preview; sufficient contrast; no more than one dense comparison simultaneously.
- **Coverage:** All important teachable moments that benefit from diagrams are illustrated, but explanation-only and personal moments may stay on the presenter.
- **Render:** Playback audio present, no lost final syllables, no cropped typography, no duplicate captions, no accidental mute, no overlay behind the face without a real matte.
- **Delivery:** State exactly what was rendered/tested, never imply a render exists if only code or a plan exists.

## Invoke
User can say: **"Use the Phillips English teaching graphics skill to edit this video. Follow the actual transcript, keep me visible, and deliver the finished 1080p MP4."**

For Shorts: **"Use the Phillips English teaching graphics skill to cut 4 YouTube Shorts from this lesson with transcript-matched examples; keep the source unchanged."**

These are instructions for Claude Code in this repository, not separate tools or paid services.
