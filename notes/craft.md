# Motion craft rules (read before planning any video)

Learned from HyperFrames' skill references (HeyGen, Apache 2.0; originals in `notes/craft/hyperframes/`), which were measured frame by frame from finished films. Translated here for Remotion. A reference the user gives, or a brand's own look, wins over any default below.

## Moves and eases
- A fast move takes 0.3–0.6 s (9–18 frames at 30 fps). One move is one tween.
- Ease by role: arrivals land on a long tail (`Easing.out(Easing.exp)` or quart), camera moves and colour floods ease both ways (`Easing.inOut(Easing.quad)`), exits and zoom-throughs accelerate (`Easing.in(Easing.cubic)`). The same ease-out at 0.5 s on everything is what makes a film feel generated. Linear only for rotation and progress.
- Arrive slow, leave clean: exits are 40–50% shorter than entrances, and are one smooth motion.
- Springs by damping ratio: 1.0 no bounce, 0.7–0.85 premium, 0.4–0.6 playful, under 0.3 cartoon. Position and size may bounce; opacity and colour never.
- Overlap: the next element starts when the previous is 30–50% done. Stagger: letters 1 frame, words 60–120 ms, list items 40–80 ms.
- Secondary moves travel 50–70% as far as the hero move and start 100–200 ms after it. One hero move per shot.
- Motion blur peaks at the fastest frame: 6–12 px on text-sized things, 15–20 px full-frame. In Remotion: `@remotion/motion-blur` (`CameraMotionBlur`, already installed).

## Beat grid
- Frames per beat = fps × 60 / BPM. Compute each beat from its index and round it; never add a rounded beat repeatedly (it drifts).
- Cut on the beat, change the layout on the bar (every 4 beats). Land the payoff on a strong beat.

## Titles and holds
- A landed title is dead still. Motion moves to the next element, the camera or the background. No drifting, breathing or slow scaling titles.
- Vary entrances in one film: per-word blur-in (6 px → 0 in 0.13 s, 0.067 s apart, no slide), per-word grey → ink, whole-line blur-in, per-letter for a name, behind the subject, slot-machine word.
- Hold a line 0.5 s + 0.3 s per word; the last line at least 2 s. Exit with a 0.13–0.25 s blur-out and fade.
- Size: titles 4–9% of frame height; quiet lines 2.5–4%; hero words fill 60–90% of the width. One accent-colour word, and it must carry meaning.
- Text meant to be read: at least 28 px at 1080. Too many words: cut words, never shrink type.

## Rhythm
- Something new every 2–4 s. Montages cut every 0.13–0.8 s; a demo holds one framing 7–10 s while the UI acts.
- Hold 0.3–0.75 s before the payoff. The first frame must not be empty (it's the thumbnail).
- More than 3 s with nothing changing is a dead stretch.

## Transitions with a cause
Use 3–5 kinds per film, each caused by something on screen. At most a third of scene changes are hard cuts.
- Zoom through a button; object grows into the next world (0.65 s); morph one container into the next (0.2 s with horizontal blur); carry an object across; colour flood (0.4 s); whip (0.13–0.3 s smear); iris from the click; dip cut (darken 40% for 3 frames, then cut); blur swap on one stage.
- Cut at the fastest frame of a move, with matching direction and speed on both sides.

## Captions
- Groups: 2–3 words high energy, 3–5 conversational, 4–6 calm. Break at a sentence end, a pause of 150 ms or more, or the word limit. One group visible at a time.
- A group opens at or before its first word and closes at or after its last. Not at exactly 0 s: start 0.1–0.3 s in.
- Match transcript words to caption words by position, not text. Whisper invents words over silence: drop words that start inside a final silence.
- Landscape: 80–120 px from the bottom. Portrait: 600–700 px from the bottom. Never over the face.
- Fade the group or its words, not both. Over busy footage use a scrim sized to the text, never a full-width bar.
- Word behind a person: best 30–55% covered. Measure against the matte over the caption's own time window; heads move.

## Cards over a talking head
- Lower third: bottom 30%. Side panel: right 42% (landscape), bottom 40% (portrait).
- Cards fade in 0.4 s, out 0.35 s. A static card goes dead after about 8 s.
- Density: one card per 6–8 s under a minute; 8–12 s up to 3 minutes.
- Glass over bright footage goes white on white: put a dark scrim behind it.

## Sound
- A film over about 15 s that tells something gets music and a few effects, unless the user wants silence.
- Few and exact effects, each with a cause on screen: click on a real click, whoosh on a cut or fast card, tick on typing, pop on a badge or number, one riser into impact per film.
- Place a sound so its peak lands one frame after its picture. Hits sit 3–6 dB over the music. Rotate takes of a repeated sound.
- Music under a voice: about 0.14 volume. Peaks at −1 dBTP or lower. Loudness: this workspace's rule is about −14 LUFS.
- I can't hear: say "measured, not heard" in the delivery note.

## The spec: numbers, not adjectives
Before building, turn every adjective into a number (in `notes/plan.md`): ground colour and texture %, type face + weight + px + tracking, eases by role, durations in frames, one line per shot (frame range, hero move, what's read, sound, hand-off).
- premium → a material with numbers; modern → a camera move and a type system; clean → a grid, margins and one accent word per shot; dynamic → cuts on the beat; playful → springs at 0.45–0.6; cinematic → a lens, a key light, 6% vignette.
- The hero of a shot fills at least 40% of the frame. A small object in an empty frame is never a shot.

## Defaults that look generated (avoid unless the brand or reference uses them)
- A dark void with small things floating in the middle; glow, bloom, neon, lens flares, particles as decoration.
- Purple or blue gradients, mesh gradients, glass cards.
- Everything centred; everything fading in at once; every element fading and sliding up; every scene entering the same way.
- Text that moves while it's read; titles drifting after landing; a slow creeping scale on a title.
- Breathing, floating or pulsing loops standing in for motion; bounce on UI; click rings.
- Corner brackets, HUD readouts and frame borders as decoration; the same whoosh on every cut.

## Review (on top of this workspace's scoring rule)
- Describe each key frame in one sentence as a stranger would. Anything you'd have to explain is a top-priority fix.
- Check: does it read as what it is, does the subject separate from the ground, framing and contact, timing as a first-time viewer, readable at phone width (360 px).
- Write each problem as `t=4.2s · where · problem → exact change`, ranked P0 (breaks the read), P1 (weakens), P2 (polish). Fix P0s first: text, then timing, then detail.
- A film that feels busy: remove a third of the motion.
- Delivery note: creative calls made, what was measured versus only looked at, the weakest shot, what nobody checked.

## Copying a reference video
- Read consecutive frames around every cut, entrance and exit; sheets a quarter second apart miss 1–3 frame timing, blur and flashes.
- Size text from its ink; find caption switch frames from the pixels in the caption band.
- A logo is the real file, never drawn by hand.
