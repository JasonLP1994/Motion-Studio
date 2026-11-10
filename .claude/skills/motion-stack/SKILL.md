---
name: motion-stack
description: Use whenever the user uploads or points to a video to edit, or asks for a video to be made "better", "more polished", "with motion graphics", "like a pro edit", or for several deliverables from one source. Reads the video's content and style, then chooses and STACKS several complementary Motion Studio skills (art direction, framing, cutting, type, graphics, transitions, 3D/shader accents, colour, sound) into one coherent edit, instead of using a single skill. Outputs a visible "skill stack" in the plan.
---

# Motion stack: choose skills from the content, then stack them

The studio's look comes from **skill stacking**: several techniques layered on one video, each doing one job well, all tied together by one art direction. Never default to a single skill or template. Read the video first, then build the stack from what it actually contains.

Always follow `CLAUDE.md`, `notes/checks.md` (read before every render) and `notes/craft.md`. The user's direction for THIS video wins over everything below.

## 0. Skill picker (show on every upload, user rule)
When a video is uploaded or pointed to, first take a **quick look** (a frame contact sheet and the transcript, step 1's eyes and ears), then show ONE `AskUserQuestion` card with these four questions. **Mark the options most relevant to this video's content and style with "(Recommended)"** in their labels and put them first in each list (in `Mode`, `Auto stack (Recommended)` stays first). Give each recommendation a short reason in its description (e.g. "you list three steps at 0:28"). The user can confirm, change, or type in "Other". Skip only what the user already specified in their message.

1. **"How should I choose the skills for this video?"** (single choice, header `Mode`)
   - `Auto stack (Recommended)`: I read the video and choose the whole stack myself (sections 1-4).
   - `Auto + my picks`: I choose, but always include whatever you tick below.
   - `Only my picks`: use just what you tick below (plus framing and the quality checks).
2. **"Words on screen?"** (multi-select, header `Words`)
   - `Kinetic captions` (`kinetic-typography` / `caption-animation`), `Duppy slam words` (`duppy-hype` grammar), `Clean subtitles` (`caption-animation`, calm), `No on-screen text`.
3. **"Visuals and wow moments?"** (multi-select, header `Visuals`)
   - `Images, emojis, icons` (from `inputs/`, emoji font/Twemoji, icon sets), `Motion b-roll cutaways` (`motion-broll`), `3D / C4D moment` (`threejs-*`, `particle-system`, `C4DMoGraph`), `Shader / particle moment` (`shader-art-coding`, `shader-glsl`, `particle-system`).
4. **"Polish?"** (multi-select, header `Polish`)
   - `Beat-synced cuts` (`beat-sync-editing`), `Custom transitions` (`remotion-transitions`), `Logo sting intro/outro` (`logo-animation`, `src/sting/`), `Sound effects` (`sound-effects`, -14 LUFS).

### Adding skills at any time ("add this skill too")
The user can add a skill or effect at any point: in the first message, in the picker's "Other" box, after the plan, after the stills, or after a render ("add kinetic type too", "throw in a 3D moment", "use the glitch transition"). Then:
1. Name the skill(s) it maps to and **where** it will go in this video (time ranges, which layer), in one or two lines.
2. Fit it into the existing stack under the same art direction: adjust or replace overlapping layers rather than piling two systems on one job (e.g. swap caption styles, don't double them).
3. Keep everything already approved; only re-plan the affected seconds. Show new stills for the changed moments only.
4. Re-render as a new version (never overwrite), re-run the checks, and say what changed.
If the requested skill isn't installed, say so and offer the closest installed option or to add it (research report: `reports/`).

Rules: ticked items are commitments (include them unless they would break a rule in `notes/checks.md`, and then say why). Unticked items in `Auto` modes may still be added if the content calls for them. Format, length and feeling are asked in the usual `CLAUDE.md` brief only if still unknown (keep it to one more card at most). Record the picks at the top of the job's plan.

## 1. Read the video (eyes and ears first)
- Frames (dense around cuts and gestures), transcript with word timings (local Whisper, `scripts/transcribe-chunks.mjs`), music tempo/beat grid if there is music, burned-in text, faces and safe space (`notes/shots.md`).
- Write down the **content signals** below before choosing anything.

## 2. Content signals -> skills (pick every row that applies)

| Signal in the video | Stack these | Job in the edit |
|---|---|---|
| Any edit (always) | `motion-art-direction` + `shot-composition` | One look (palette, type, energy) and framing/safe zones for each format |
| Talking head / lesson | `caption-animation` or `kinetic-typography`, `motion-broll` | Words on screen on the spoken word; cutaways that show what's described |
| A key phrase, punchline, number or rule | `kinetic-typography` (hero words), `duppy-hype` slam grammar for high energy | Make the teaching point land |
| Steps, lists, comparisons, mistakes vs fixes | `kinetic-typography` builds, kit templates (`fx-checklist`, `tm-neo-brutalism`, `fx-chart-grow`) | Structure the idea visually (never the rejected teal side-panel cards) |
| Music or a strong rhythm | `beat-sync-editing` (+ the `sound-effects` beat-grid check) | Cuts, reveals and transitions on the beat |
| Scene or topic changes | `remotion-transitions` | Transitions with a cause (see `notes/craft.md`), 3-5 kinds max |
| Brand moments (open/close, sign-off) | `logo-animation` (the real logo: `public/logo/` pieces, `src/sting/`) | Intro/outro sting, end card |
| Objects, products, places, emotions mentioned | the user's images in `inputs/`, emoji/icons, cut-outs (`object-separation` asks first) | Bring the thing being talked about on screen |
| A "wow" beat (the main idea, a reveal, a milestone) | 3D (`threejs-*`, `particle-system`, the `C4DMoGraph` scene) or shaders (`shader-art-coding`, `shader-glsl`) | One premium accent moment, not wall-to-wall |
| Mood, look consistency, mixed footage | `color-motion` | Palette, grade, colour transitions |
| Any sound design | `sound-effects` | Hits tied to visible actions, levelled to about -14 LUFS |
| Vertical deliverable / Shorts | `short-form-video`, `longform-to-shorts` | Hook, retention, 9:16 safe zones |
| A style reference supplied | `motion-art-direction` + the matching learned template (`duppy-hype`, `epic-scale`, `material-loop`, kit styles) | Take the grammar, never the content |

A typical stack has **4-8 skills**. Fewer only when the content is genuinely simple; more only when each extra layer clearly earns its place.

## 3. Stack in layers (bottom to top)
1. **Look**: art direction + colour (one palette, one type system, one energy level).
2. **Structure**: framing, cut rhythm (speech-led or beat-led), pacing.
3. **Words**: captions / kinetic type on the spoken words.
4. **Visuals**: b-roll, images, emojis, icons, diagrams for what's being said.
5. **Accents**: transitions, one or two 3D/shader/particle "wow" beats, logo sting.
6. **Sound**: hits on visible actions, music ducked under speech.

## 4. Coherence rules (stacking without chaos)
- **One art direction ties every layer**: shared palette, fonts and motion personality (eases, springs) across all skills used.
- **Every layer serves the content**: each skill in the stack must answer "what does the viewer understand or feel better because of this?" Drop any that don't.
- **Density follows energy**: a calm lesson stacks gently (captions, b-roll, one accent); a hype edit stacks densely (slam type, beat cuts, emoji pops, 3D burst).
- **Hierarchy**: one hero element on screen at a time; secondary layers travel less and start later (`notes/craft.md`).
- **Accents are rare**: 3D/shader/particle moments mark the 1-3 most important beats, not every sentence.
- **Never stack two systems doing the same job** (two caption styles, two transition families fighting).
- Speech, faces and the user's exact words stay sacred: no graphics over the face, captions verbatim.

## 5. Show the stack in the plan
Before building, put a **Skill stack** table at the top of the plan (`notes/plan.md` or the job's plan file) and in the message:

| Skill | What it does in this video | Why (the content signal) |
|---|---|---|

Then the usual workflow: second-by-second plan, three stills, render, frame check across the whole video, score out of 10 (fix anything under 8), deliver the MP4 in chat. Videos never go to GitHub.
