# Eyes and ears

You can see images but you can't play video or hear audio. This file gives you eyes (frames) and ears (a timed transcript) using only what Remotion already ships: its built-in FFmpeg and its local Whisper.

Rules:
- Use `npx remotion ffmpeg`. Never ask the user to install FFmpeg, Python, faster-whisper or anything else for this.
- Run commands from the project folder. Replace the example names with the real files.
- Keep originals untouched. Write all outputs under notes/ (frames, transcripts, plans).
- Never claim you watched or heard something. Say "from the frames" or "from the transcript", and say what you couldn't check.

## What to inspect, by input

| Input | Eyes | Ears |
|---|---|---|
| Image only | Open the image. Note size, subject, empty space, any baked-in text | None |
| Silent video | Frames across the whole clip, denser around cuts and fast motion | None. Don't invent dialogue |
| Video with speech | Frames | Extract audio, transcribe with word timestamps |
| Image or video plus a separate voiceover | Frames or the image | Transcribe the voiceover file itself. Never estimate timing from the script |
| Music, no speech | Frames if there's video | Don't make up a transcript. Note where the music hits or changes if the user wants beat timing |
| A style reference video | Frames | Transcribe if it has a voice. Note where text lands on words or beats |

## Eyes: pull frames

Two frames a second across the whole video:

```
npx remotion ffmpeg -i inputs/clip.mp4 -r 2 notes/frames/clip/f_%03d.jpg
```

Use `-r 2`, not an fps filter. The built-in FFmpeg doesn't have the fps filter. Make the folder first.

f_001 is at about 0.0 s, and each next frame is 0.5 s later. Frame n sits at roughly (n - 1) / 2 seconds.

To check basic facts (duration, size, frame rate, whether there's an audio stream), run `npx remotion ffmpeg -i inputs/clip.mp4` with no output. It prints the stream info, then stops with an error about the missing output file. That error is expected.

Then open the frames and actually look at them. Extraction succeeding is not the same as inspecting.

### Look closer at one moment

One frame at an exact time:

```
npx remotion ffmpeg -ss 4.25 -i inputs/clip.mp4 -frames:v 1 notes/frames/clip/at_4.25.jpg
```

Denser frames over a short stretch (here 2 seconds from 4.0 s, ten a second):

```
npx remotion ffmpeg -ss 4 -t 2 -i inputs/clip.mp4 -r 10 notes/frames/clip/dense_%03d.jpg
```

Use these around cuts, fast motion, hands and anything a label will track. Two frames a second can't prove tracking is right.

### Shot table

For the user's footage, write notes/shots.md:

```
Time | Shot | What's visible | Empty space | Covered or leaving frame | Cut?
```

Only point a label at something visible at that time. Reset anchors at every cut. Hide a label when its target leaves or is covered.

## Ears: audio and transcript

Skip this for images and silent clips. If you're not sure a clip has sound, check the stream info first. An audio stream can still be music or silence.

### 1. Extract the audio

```
npx remotion ffmpeg -i inputs/clip.mp4 -vn -ac 1 -ar 16000 notes/frames/clip/audio.wav
```

This makes a mono 16 kHz WAV, the format Whisper expects. For a voiceover that's already an audio file, run the same command on it. Never overwrite an existing file; pick a new name.

### 2. Set up Remotion's local Whisper (first time only)

Use `@remotion/install-whisper-cpp`. It runs on the user's computer, works on Mac and Windows, and needs no API key and no Python.

- Install the package in the project, then use it to install whisper.cpp inside the project folder.
- Ask the user before downloading a model. Say it's a one-time download of a few hundred MB. The base English model (base.en) is enough for English. Use whisper.cpp version 1.5.5, the version in Remotion's own example. Whisper's transcribe step can leave a tmp.json in the project root; move it into notes/. Drop bracket tokens like [BLANK_AUDIO] or [Music] from the transcript before you use the word timings. Use a multilingual model for other languages.
- The Remotion plugin's captions guidance and Remotion's docs show the current function names. Follow those instead of guessing.

Test it once on a short clip (about 2 to 10 seconds) of real speech. Cut one with:

```
npx remotion ffmpeg -i inputs/clip.mp4 -t 10 -vn -ac 1 -ar 16000 notes/frames/clip/test.wav
```

Show the user the text and timestamps. Until this test passes, call transcription untested.

### 3. Transcribe with word timestamps

Transcribe the WAV with word-level (token-level) timestamps turned on. Save the result as notes/transcript-<name>.json with each segment's start, end and text, and each word's start and end.

Then read it:
- Check names, brands and unclear words. Mark anything uncertain. Whisper's timings are good estimates, not perfect.
- If the user gave an approved script, compare it with the transcript and use the script's spelling with the transcript's timing.
- If the video is cut or trimmed, map source times to output times before placing graphics.
- If the speaker gives editing instructions in the recording, keep those apart from the narration. Don't cut them unless asked.

## Connect what's seen with what's said

Write notes/beats.md:

```
Time | What's said or what happens | Visible subject | Graphic | Template / effect | Anchor | Unsure?
```

Pick effects by meaning and composition, not keywords. A list can become a checklist, a measured trend a chart, a product detail a tracked label. Don't put an effect on every word or switch styles every sentence. Put each graphic on its word.

Show the user this plan before building.

## Check the finished render

Use the same tools on your own output:
- Pull frames from the whole render with `-r 2`, plus dense frames around transitions and tracked labels.
- Extract the render's audio and confirm the voice or music is there and lines up with the words. Transcribe it again if timing matters.
- Say clearly what you checked from frames, what from the transcript, and what remains unchecked.
