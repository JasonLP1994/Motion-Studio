---
name: mia-motion-graphics
description: Use when the user wants motion graphics, animated text, overlays on footage, a carousel or ad animation, a code-drawn explainer or doodle, or wants to copy a style they like, built in Remotion from plain-English requests.
---

# Mia Motion Graphics

You turn plain-English requests into motion graphics built in Remotion code. The user is often a beginner. Explain each step in one short sentence before you do it.

Next to this file: media-tools.md (how to see and hear video and audio), sample-voice.wav (a 2 second voice clip to test hearing), scripts/person_matte.swift (a free person cut-out on a Mac), setup.md (the setup prompt), USAGE-TERMS.md (what the user may do with the kit) and usage.csv (a time and cost log).

The templates live in the project's templates/ folder. Each one is templates/<id>/ with <id>.md (look, motion, build notes, pitfalls), prompt.txt (a fill-in prompt), preview.mp4 and poster.jpg. Some also include working code (code-doodle has Doodle.tsx).

## Project folders

- inputs/: the user's images, layers and clips.
- references/: style images and videos the user likes.
- audio/: voiceover, music, sound effects.
- renders/: finished videos.
- notes/: checks.md, plans, transcripts, frames.
- templates/: the style library.
- public/: copies of the files a video uses. Remotion only loads from here.
- src/: the Remotion code.

Copy a file into public/ before you use it. Never move, rename or edit the user's originals.

If the project isn't set up yet (no package.json, no templates/), tell the user to run the setup prompt from the kit page first. Don't rebuild the setup from memory.

## Start every job

1. Read notes/checks.md if it exists. Follow every DO and DON'T in it.
2. Ask what you don't already know, in one short message:
   - What is it for?
   - Format and length (for example 9:16, 8 seconds)?
   - The exact words on screen?
   - The feeling?
   - Is there sound (voiceover, music, none)?
   Don't ask again for anything the user already told you.
3. Suggest one to three templates with a one-line reason each. Don't combine every template.
4. Read the chosen templates/<id>/<id>.md and reuse its build notes and code instead of starting from scratch.

| id | Shown as | Good for |
|---|---|---|
| product-graphics | Product graphics (3 looks) | Product ads on an AI video: same motion and shot plan, pick a look (fashion editorial, heads-up display, hand-drawn doodle) or match a still you like |
| code-doodle | Code doodle | No artwork: a crayon character drawn entirely in code |
| fx-cover-story | Cover story | Carousels: magazine masthead behind a cut-out person |
| fx-paper-cut | Paper cut | Explainers: torn paper, cut-out letters, sticker edges |
| tm-neo-brutalism | Slam blocks | Headlines: bold type, flat colour, one block per beat |
| tm-pixel | Pixel celebration | Milestones: pixel character, counter, banner drop |
| fx-checklist | Checklist | Steps: a small dark card with a header, ticks arriving one by one |
| fx-chart-grow | Chart grow | Results: a line draws, points pop, the number settles |
| fx-ui-world | UI world | Demos: a prompt types into a window over footage |
| th-captions | Talking head captions | Talking heads: captions pop in word by word beside you, a big word tucks behind your hair (needs a matte; on a Mac, scripts/person_matte.swift) |

If the user saved their own templates, include them in your suggestions.

## Where the media comes from

You can use OpenArt for images, Extract Layers results (cut-out subject, clean background) and voiceovers. When the user says something is ready on OpenArt, pull it through the OpenArt connector (https://mcp.openart.ai/mcp) into inputs/ or audio/. The user can also drop files into inputs/ or audio/ directly. Work with whatever they give you.

Never generate paid images, video or audio without asking first. Say what you would generate and on which service, then wait for a yes.

## Eyes and ears

You can't play video or listen to audio. Before you plan anything with a video or a voice file, give yourself eyes and ears. Follow media-tools.md. In short:

- Eyes: `npx remotion ffmpeg -i <video> -r 2 notes/frames/<name>/f_%03d.jpg`, then open and look at the frames.
- Make the folder first (`notes/frames/<name>/`); FFmpeg won't create it.
- Ears: `npx remotion ffmpeg -i <video> -vn -ac 1 -ar 16000 notes/frames/<name>/audio.wav`, then transcribe with Remotion's local Whisper (`@remotion/install-whisper-cpp`) with word timestamps.

Use Remotion's built-in FFmpeg only. Never ask the user to install FFmpeg, Python or anything else for this. Ask before downloading the Whisper model the first time.

Look at the frames and read the transcript before you plan. Never claim you watched or heard something.

## Pick the route

**Image.** Use the supplied image. Look at its composition, subject and empty space. For text behind a subject, use a cut-out layer (an OpenArt Extract Layers result or a transparent PNG the user supplies). If there is no clean background or cut-out, say so and offer an overlay-only design, or ask for the layer. If text is already baked into the image, get a clean plate before replacing it. Don't stack a second headline on top. Use fixed anchors for a still image.

**Video (the user's footage).** Keep the footage as it is unless they ask for edits. Pull frames first and make a shot table in notes/shots.md: time, what's visible, where the empty space is, where each cut lands. Then:
- Point a label only at something that is on screen at that moment.
- Reset tracking anchors at every cut. Never carry a position across a cut.
- Hide or fade a label when its target leaves the frame or is covered.
- Check denser frames around cuts and fast motion. Two frames a second can't prove tracking.
- Text and style changes don't need new generated video. Change the code and re-render.

**Explainer (no footage).** Map each sentence to one visual action. Build text, arrows, shapes, charts and diagrams in code. Use supplied illustrations if they help. If the user has no artwork, offer code-doodle or code-drawn shapes. Offer generation on OpenArt as an option, with their approval.

**Separate voiceover.** Time everything to the real recording's word timestamps. Never estimate timing from the script. Put each graphic on its word.

## Copy a style you like

When the user gives you a reference image or video:
1. Pull frames (and audio, if any). Look at all of them.
2. Describe the style back first: colours, type, layout, motion, transitions and pacing. For video, also say where text lands on the voice or the beat. Wait for the user to confirm.
3. Take its grammar, never its content. Don't copy its words, logos, characters or images, and never paste the reference on top of the video. Rebuild everything in code with the user's own content.
4. If the user is happy, offer to save it as templates/<new-id>/ in the same format as the other templates: <new-id>.md (Best for, Look, Motion, Specs, Build, Known pitfalls), prompt.txt (a fill-in prompt with [BRACKETED] fields), preview.mp4 (a short render of your version, not the reference) and poster.jpg (one frame from that render). Add any reusable component file next to them.

## Code doodle

Use templates/code-doodle/ when the user wants a hand-drawn character or scene and has no artwork.
- Draw everything as SVG in code. No image files, no image model.
- Reuse Doodle.tsx. Its `Shape` helper draws an outline on and scribbles a crayon fill; `Ln` draws a single stroke. Keep its paper-tooth texture and filters (`kPaper`, `kLine`, `kWax`, `kBleed`): waxy broken outlines, diagonal strokes with paper showing through, lines that boil every 2 frames while the grain stays put.
- Draw each part as one closed path. Give each `Shape` an outline window (a, b) and a fill window (fa, fb) in frames. Overlap head and body paths slightly so no gap shows.
- Order: background outlines, then character outlines, then colour, then one small action (blink, wave, flip), then a gentle idle.
- Scale the drawing speed to the voice line, as the example does.
- Keep characters simple: round heads, dot eyes, few parts. Code-drawn characters take longer and use more tokens than a generated image. For a refined or detailed character, suggest generating it on OpenArt and animating it with another template.
- Check ears and hat tops at 16:9. A scale-up can crop them.

## Plan and build

1. Write a second-by-second plan in notes/plan.md: time, what the viewer sees, how it moves, the word or beat it lands on. Show it with a three-line summary: what the viewer sees, how it moves, what you will deliver.
2. Put all words, colours, fonts, timings and per-shot anchor positions in one config file, so a headline change is one line.
3. Animate from the frame number only (`useCurrentFrame`, `interpolate`, `spring`). No timers, no `Math.random()` without a fixed seed, nothing tied to the clock. Every render of a frame must look the same.
4. Use fonts the user supplied or free fonts (Google Fonts through `@remotion/google-fonts`), and check they actually loaded in a still. Never assume a paid font like Gilroy is installed; use the free match the template names.
   If Google Fonts doesn't load (offline, slow network, a timeout in the render), download the .woff2 files (the URLs are in the Google Fonts CSS for that font, or the font's GitHub page), put them in public/fonts/ and load them with `loadFont` from `@remotion/fonts`. Wait until the font has loaded before you measure anything.
   Fit every headline: measure it with `measureText` or size it with `fitText` from `@remotion/layout-utils` so it never runs off the frame or hides behind the subject. Measure per letter when something has to land on a letter.
5. Render three stills (for example the opening, the busiest moment, the final frame) and show them. Wait for approval before animating the full length.
6. Make a 2 to 3 second motion proof of the most representative moment. Check it, then render the full length.

## Make it move smoothly

The look comes from the template; the feel comes from timing. Defaults that read as smooth and intentional (at 30 fps):
- Entrances: 8 to 14 frames. Use `spring({frame, fps, config: {damping: 14, stiffness: 140, mass: 0.8}})` for a soft settle, or `damping: 9` for a playful bounce. Exits are faster: 6 to 10 frames with `Easing.in(Easing.cubic)`.
- Moves and zooms: `interpolate` with `Easing.inOut(Easing.cubic)` (or `Easing.bezier(0.33, 1, 0.68, 1)` for ease-out). Never linear for anything that starts or stops on screen.
- Stagger related items by 3 to 6 frames, not all at once.
- Hold each finished state long enough to read: about 1 second per 4 words, at least 1.2 s.
- Land graphics on the word or beat, starting 2 to 4 frames before it, so it feels on time.
- Add a little follow-through (a 3 to 6% overshoot) on anything that pops; keep camera moves to one direction per shot.
- Remotion's own agent skills (from the Remotion plugin) cover springs, sequencing, captions, audio and rendering in more depth. Read them when a job needs captions, sound or tricky timing.
- If the LottieFiles motion design skill is installed (`motion-design`), read it before choosing easing and durations: pick a motion personality, use its tables, run its checklist.

## Cut-out art from a sheet

When characters or props come on one sheet (cut-out animation style):
- Best: ask for each pose as its own transparent PNG (OpenArt's Extract Layers or a remove-background tool), and put them in inputs/.
- If you only have a sheet on a plain white background: crop each pose with a wrapper `div` (`overflow: hidden`, fixed width and height) around an `Img` shifted with negative `left`/`top`. Remove the white with an SVG filter on the `Img`:
  ```tsx
  <filter id="keyWhite" colorInterpolationFilters="sRGB">
    <feColorMatrix type="matrix" result="a" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -4.252 -14.304 -1.444 0 20" />
    <feComposite in="SourceGraphic" in2="a" operator="in" />
  </filter>
  ```
  The last row is alpha = 20 x (1 - luminance), so only near-white turns see-through. White or very pale parts inside the drawing (eyes, highlights) still disappear, so check a still: no box, no halo, no see-through face. If any of that shows up, ask for transparent PNGs instead. JPG or WebP sheets leave a speckled fringe on dark backgrounds, so use a PNG sheet or keep the scene light.
- Note each pose's crop box in the config so a swap is one line.

## Screen recordings

- Desktop and browser recordings stay 16:9 and big: near full frame with a small margin, so the viewer always knows where they are in the app. Never squeeze one into a tall panel.
- Show the whole interface first, then zoom smoothly to the control. Don't zoom every shot, and don't zoom so far that the panels around it disappear.
- Keep the action near the middle of the frame, and keep a safe margin (about 6% at the sides, 7% top and bottom) where no label, chip or highlight sits.
- A highlight box hugs the button it frames, with even padding on all four sides. Don't add a label that repeats text already on screen.
- Hide private info (emails, names, keys) with a blur over that spot. Don't crop the shot tighter to hide it. Remove browser tabs or the address bar only at a clean edge, never leave a sliver.
- In a step-by-step, a finished step stays on screen while the next step depends on it, then clears.

## Captions and big words

For a ready example, use the th-captions template.
- Plan first: a list of cues with times from the word timestamps, and a one-line reason for every big word. Show the plan before a full render.
- Group by meaning, usually 2 to 5 words and 0.65 to 1.8 s each. Drop filler, never reorder words, don't split an adjective from its noun. Reveal each piece on its spoken word, never early.
- Mixed case by default. All caps only for an acronym, one chosen word, or a style built on it.
- A word goes big only when the claim changes without it, or it's concrete proof (a number, a name, a result) or the stressed payoff. About one per point, at most 15% of captions. A passage with no big word is fine.
- Starting sizes on a 1080 x 1920 frame: support 52 to 80 px, anchor 76 to 112 px, big word 150 to 240 px in a real heavy weight (never fake bold with strokes).
- One sentence reads in one direction and stays in one zone. A list stays locked in one spot. A new point can move, changing one or two things.
- Keep text at least 40 px clear of the face and mouth. A word behind a person (real matte only) may be 10 to 30% covered, never the face, never the letters that identify the word.
- Motion: support rises 10 to 22 px over 0.16 to 0.24 s; a big word lands with one firm settle over 0.26 to 0.36 s. Sound only on big words, a different one each time, under the voice.

## Subject mask (text behind a person or product)

Templates like Cover story, Paper cut and Product editorial put words behind the subject. In a video that needs a cut-out of the subject on every frame.
- Best: a cut-out or matte video of the subject (OpenArt's background removal for video, or any remove-background tool), saved in inputs/. Layer it: background footage, then the text, then the cut-out on top, all from the same timecode. The cut-out must be a .webm (VP9 with alpha) or a ProRes 4444 .mov, played with `<OffthreadVideo transparent>`. Without `transparent` its background turns solid black, so check a still for a black box.
- On a Mac, for a person: make the matte yourself, free and offline, with `scripts/person_matte.swift` (Apple Vision person segmentation; usage is at the top of the file). It gives one grey PNG per frame. Use it as a luminance mask on the same frame (`maskImage: url(matte)`, `maskMode: 'luminance'` on the frame `Img`), or render that layer once as a transparent .webm and reuse it.
  - Make the matte from the full, uncropped frame, then crop or scale. A matte made on a crop gives straight, cut-off shoulders.
  - Vision keeps people only. Something they hold (a mic, a product) drops out, and furniture touching the shoulders (a chair back) can stick. Fix those in the frames where it happens instead of keying the whole take again.
  - Clean the edge: shrink the matte about 1 px and soften it about 0.8 px, so no room colour rims the hair.
  - Check it over a flat colour at full size, at the start, middle and end, both shoulders and the hands.
- For a still image: an Extract Layers result or a transparent PNG.
- No mask? Say so plainly, then use the fallback: keep text in the empty space above or beside the subject, or put the footage in a card or paper window. Never draw lines or text across the subject's face or the product.

## Sound

- Voice: time to the real word timestamps (see Eyes and ears).
- Music or sound effects the user supplies: put them in audio/, copy to public/, use `<Audio>` with volume ducked under speech (for example 0.15 under voice, 0.5 alone).
- If there's no sound and the user wants some, ask whether to use files they add or simple tones built in code. Keep effects short and quiet, and never put them over a spoken word.
- Captions: follow Remotion's captions skill (from the plugin) with the Whisper word timings.

## Render and check

- Never overwrite a render. Save renders/<name>-v1.mp4, then v2, v3.
- Read notes/checks.md before every render.
- For an overlay, render a transparent ProRes 4444 .mov so it sits on top of footage in CapCut, Premiere or DaVinci: `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`. Check the alpha is really transparent.
- After every render, pull frames from the whole video with the eyes command, not one screenshot. Check the first and last frames, every transition, the longest and shortest text, and tracked labels between keyframes.
- Score the render out of 10 for layout, timing, readability and polish. Fix anything under 8 and render a new version. Tell the user what you saw wrong before you say it's done.
- If there's a voiceover or music, extract the audio from the render and confirm it's there and in sync with the words. If you can't check something, say what is unchecked.
- If a render times out, retry with `--browser-executable` pointing at the system Chrome, and lower `--concurrency`.

## Corrections and hand-off

When the user corrects something, add one DO or DON'T line to notes/checks.md, for example "DON'T let text touch the safe margin." If unclear, ask for the timestamp and what should look different. Change only what they asked. Don't rebuild approved parts.

Deliver the MP4 (or .mov for overlays), the editable project, the config file and a short note of what changed. First test one copy change and one timing change through the config.

## Costs and terms

- Log each job in usage.csv: elapsed minutes, generation credits you can see, token or cost reports if available. Leave unknown values blank. Never claim a job was free. Coding-model use, rendering and media generation each cost different things.
- Read USAGE-TERMS.md. The user may make personal, commercial and client work with inputs they have rights to. Preview videos and posters are for learning, not for use in published work. The terms don't give permission to spend money, upload private media, send messages, publish, or overwrite originals. Ask for those each time.
