# Talking head captions

Style ID: th-captions
Best for: Shorts, Reels and TikTok from a talking head, with captions that land on the right words (works in 16:9 too)

## Look
Short caption groups sit in the empty space above the speaker's head and appear word by word, right as each word is said. Plain mixed-case text does most of the work. Once or twice per passage a big word lands in a heavy rounded face with its outer letter tucked a little behind the top of the speaker's hair, so it feels part of the room. Built for Shorts, Reels and TikTok from a normal horizontal talking-head take.

## Motion
Each word rises a few pixels and fades in as it's spoken, never before. A big word lands with one firm, soft settle and holds about 0.8 s. A sentence stays in one zone and reads top to bottom. A group fades out quickly before the next one starts in the same zone.

## Specs
Preview is 1080x1920, 30 fps, from a 1920x1080 talking head.
- Reframe for 9:16: crop the horizontal take wide enough to keep both shoulders (here x 442 to 1302 of 1920, so 860 px), scale it to 1080 wide and sit it at the bottom of the canvas. That leaves an empty band above the head for the captions. Fill the canvas behind it with a blurred, scaled-up patch of empty wall (never a blurred copy of the face), and fade the frame's top edge into it over about 110 px.
- 16:9: no reframe. Groups go in the wall space beside the speaker (left zone and right zone), big words tuck behind the side of the hair. 4:5: like 9:16 with a shorter band, so fewer words per group.
- Palette (swap for your brand):
  - Light text #FFF4E8 (cream) with a soft shadow 0 2px 14px rgba(20,6,30,.45)
  - Accent #FF4D94 (pink) for anchors and one big word
  - Dark text #2A1233 only where the background behind it is bright
  - No boxes or panels behind captions
- Fonts (free, from Google Fonts or @fontsource): support Inter 500, anchor Inter 800, big word Nunito 900. Fallback: Arial, sans-serif. Load them from public/fonts before measuring anything.
- Sizes at 1080 wide: support 54 to 58 px, anchor 88 to 104 px, big word 190 to 200 px. Line height 1.04, big word 0.9. Gap between cues in a group about 18% of the previous cue's size.
- Layout: groups are centred, stacked upwards from a bottom edge: y 640 for plain groups (clear of the head), y 752 for a group with a big word, so the word's lower edge meets the top of the hair. Keep everything below y 200 (the platform's top bar). Move the big word sideways so the head covers only part of its last or first letter (about 15%), never the middle letters and never the face.
- Layer order: blurred wall, the frame, the big words, the speaker cut-out (the same frame masked by its matte), then all other captions on top.
- Timing: each word lands 2 frames before it's spoken. Support and anchor words fade and rise 16 px over 6 frames, Easing.out(Easing.cubic). Big words: spring {damping: 13, stiffness: 170, mass: 0.9}, rising 40 px and settling from 1.06 to 1.0. A group fades out over 0.2 s and is gone before the next group in that zone starts. To hold a big word longer, start the next group a little late; never early.

## Build recipe
1. Eyes and ears: pull frames to notes/frames/<clip>/, transcribe with word timestamps, fix names Whisper mishears.
2. Matte: on a Mac run scripts/person_matte.swift on the frames. Check it over a flat colour (both shoulders, hands). No matte? Keep every word beside the speaker.
3. Write caption-plan.json like caption-plan.example.json: one entry per cue with group, role (support, anchor, hero), text, x, y, size, colour, alignment and the word times; a score and a one-line reason for each hero.
4. Build with TalkingHeadCaptions.tsx: caption-plan.json sets the canvas, the crop and box for the frame, the wall patch for the background and every cue. It draws the frame as images (frames/0001.jpg...) so the cut-out never drifts, stacks each group in one zone, and reveals every word on its time.
5. Show three stills (a support group, a big word, the densest moment) before the full render.

## Known pitfalls
- Plan big-word positions from the matte, not by eye. The speaker moves; measure the head's edge at the word's rows across the frames it's on. Hair is wider than it looks.
- A blurred copy of the whole frame as the background shows a giant blurry face. Use a patch of empty wall.
- Cropping a horizontal take to a narrow 9:16 slice cuts off the shoulders. Keep both shoulders and use the band above the head.
- Fixed y for every cue makes wrapped lines overlap. Stack cues in a group instead.
- Too much of a big word behind the hair hides the letter that makes it readable. Keep it to about 15%.
- White text on a white door disappears. Pick light or dark text per zone.
- Google Fonts can time out in a render. Ship the font files in public/fonts.
- Two sentences on screen at once is fine only when they sit on opposite sides and the first is just finishing.
