---
name: project-brief
description: Use at the START of every new creative piece (motion piece, video, 3D render, still artwork, poster, logo, ident, product shot), before planning or building anything. Runs the professional brief checklist with the user in a few short AskUserQuestion rounds (recommended options marked), saves the answers to notes/briefs/<project>.md, and lists the approval checkpoints. User rule: always ask this checklist for new work.
---

# Project brief: the professional checklist (user rule)

Every new piece starts here. Ask before planning, research or building. Keep it quick: 3-4 `AskUserQuestion` rounds of up to
4 questions each, multiple choice with the best option first and marked "(Recommended)" plus a one-line reason, and the user can
always type "Other". Skip any question the user's message already answered, and say which ones you filled in from it.
Never ask more than needed for this kind of piece (a still artwork skips sound, timing and cut-downs).

## Round 1: purpose and output
1. **What is it for?** (`Purpose`): brand/advert, social post, portfolio/showreel, client pitch, personal art, title/ident/logo.
2. **Where will it live?** (`Platform`, multi): Instagram/TikTok/Reels (9:16), feed (4:5 or 1:1), YouTube/website (16:9),
   print/poster, presentation.
3. **Length / size** (`Length`): 6 s bumper, 10-15 s, 30 s, 60 s+, still image (give the print size or pixels).
4. **Deadline vs quality** (`Quality`): best quality (Cycles + full AI pipeline, slower), balanced, fastest preview.

## Round 2: message and look
1. **Exact words on screen** (`Words`): title, tagline, call to action, handle or URL, or none. Use their exact wording.
2. **Feeling** (`Feeling`, multi): premium/luxury, bold/hype, calm/minimal, playful, dark/moody, futuristic, retro/analog.
3. **References** (`References`): they upload images or videos (into `references/`), name a style, or "you suggest".
   Take grammar only (type, colour, pacing, camera), never content, logos or characters.
4. **Colours and brand** (`Colours`): brand colours/fonts/logo file, a palette they name, or "you choose" (suggest 2-3).

## Round 3: craft
1. **Subject and assets** (`Assets`): their own files (inputs/), a free licensed model or scan (state the licence and credit
   line), built from scratch, or stock footage they supply.
2. **Camera and motion** (`Motion`, multi): close-up macro, orbit reveal, slow cinematic, fast cuts/hype, speed ramps
   (slow-mo + fast), static/locked off, hand-held energy.
3. **Lighting and finish** (`Finish`): clean premium (minimal finish), cinematic/moody, graphic/editorial (crisp), film/analog.
4. **Sound** (`Sound`): original soundtrack + SFX at -14 LUFS (plus a silent copy), their music or voiceover, silent.

## Round 4: delivery (motion pieces; trim for stills)
1. **Deliverables** (`Deliver`, multi): main master, extra aspect ratios (reframed), 6 s / 15 s cut-downs, seamless loop,
   thumbnail/poster frame, transparent ProRes 4444 overlay, ProRes master.
2. **End card** (`End card`): logo + handle/URL, logo only, none.
3. **Captions / accessibility** (`Captions`): burned-in captions, SRT file, none (only when there is speech).
4. **Credits needed** (`Credits`): auto (list every model/font/sound licence), none.

## After the questions
- Write `notes/briefs/<project>.md`: every answer, what you inferred, open questions, the chosen skill stack, the render
  pipeline (`notes/ai-enhance.md` recipe, `notes/finishing.md`), licences/credits, and the deliverables list.
- Show a one-screen summary to the user and these **approval checkpoints** (don't skip them):
  1. Plan + skill stack + second-by-second timing.
  2. Three still frames (style frames) before any long render.
  3. Camera/framing check (start, middle, end of each move) for 3D.
  4. Short low-res preview or key frames of the motion before the final render.
  5. Final render: frame check across the whole piece, score out of 10, P0/P1/P2 notes, then deliver (never via GitHub).
- Commit the brief (it is text, not media).

## Quality bar (check before calling anything finished)
Readable type (contrast, size, safe zones for the platform), intentional framing, motivated camera moves, lighting that
flatters the material, consistent colour, no artefacts (noise, banding, popping, fireflies), sound synced and levelled,
correct length and specs per platform, credits complete, versions saved (v1, v2; never overwrite).
