# From download to working project

1. Make an empty project folder and open it in the Claude desktop app, Code tab (Opus 5.5). Pick Accept edits.
2. Add the Remotion plugin: Customize, Plugins, Discover, search "remotion", Add.
3. Paste the prompt below. It installs what's missing, unzips this kit, builds your folders and rules, and renders a test.

## Setup prompt

```text
Set up a motion graphics workspace for me in this folder. I'm a beginner, so before each step tell me in one short sentence what you're doing and why. Ask me before you install anything outside this folder.

1. Check which computer I'm on. Check that Node.js 20.19 or newer is installed (node -v). If it isn't, install the current LTS version for me: on Windows with winget (winget install OpenJS.NodeJS.LTS), on a Mac with Homebrew if I have it, otherwise the official LTS installer from https://nodejs.org/en/download. On Windows, also check Git for Windows (git --version) and install it if it's missing (winget install Git.Git). On a Mac, check the Xcode Command Line Tools (xcode-select -p) and if they're missing, run xcode-select --install and tell me to click Install in the window that pops up (the local Whisper needs them). Tell me before each install. If an install needs my password, give me the exact command to paste into the Terminal app myself, because you can't type it for me. If an install needs a new terminal, tell me to reopen Claude Code, then check again.

2. Create a Remotion project in this folder with the official starter: npx create-video@latest --yes --blank . (if the folder isn't empty, scaffold into a temporary subfolder, move everything up, and set the name in package.json to this folder's name). In remotion.config.ts, set Config.setOverwriteOutput(false) so a render never replaces an older one. Check that the Remotion plugin is active. If it isn't, run: npx remotion skills add

3. Find the kit I downloaded: look in my Downloads folder for mia-motion-graphics-kit (it may have a number added, or already be unzipped). If there are several, show me their names and dates so I can choose. If you can't reach Downloads, tell me how to give you access, or I'll move the ZIP into this folder. Unzip it here without overwriting anything. You should now see mia-motion-graphics/ (the skill), templates/ (10 styles) and KIT-README.md.

4. Make these folders: inputs (my images, layers and clips), references (style images and videos I like), audio (voice, music, sound effects), renders (finished videos), notes, notes/frames. Then show me the whole folder as a simple tree.

5. Create CLAUDE.md with these working rules and follow them in every chat here:
   - Read mia-motion-graphics/SKILL.md before any motion graphics work.
   - Before building, ask me what it's for, the format and length, the exact words, the feeling, and whether there's sound.
   - Suggest one to three templates from templates/ that fit, with a one-line reason each. Reuse their build notes and specs instead of starting from scratch.
   - From a style reference, take its grammar (type, colours, pacing, how text enters and exits), never its content, logos or characters. Rebuild everything in code.
   - Plan the video second by second, then show me three still frames before rendering the full video.
   - Keep all words, colours, fonts and timings in one config file, so a headline change is one line.
   - Copy files into public/ before using them. Never move or edit my originals.
   - When I give you a video, give yourself eyes and ears first. Eyes: make a folder notes/frames/<clip name>/ and pull frames into it with npx remotion ffmpeg -i <video> -r 2 notes/frames/<clip name>/f_%03d.jpg, then look at them. Ears: if it has sound, pull the audio (npx remotion ffmpeg -i <video> -vn -ac 1 -ar 16000 notes/frames/<clip name>/audio.wav) and transcribe it with Remotion's local Whisper (@remotion/install-whisper-cpp) with word timestamps. Never ask me to install FFmpeg.
   - If I make images, layers or voiceovers on OpenArt, pull them through the OpenArt connector into inputs/ or audio/ when I say they're ready. Otherwise I'll drop files there myself.
   - Never overwrite a render. Save v2, v3 and so on.
   - After every render, check frames from the whole video, score it out of 10 for layout, timing, readability and polish, fix anything under 8, and tell me what's wrong before you say it's done.
   - If I ask for an overlay to use in CapCut, Premiere or DaVinci, render it with a transparent background: --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png, as a .mov.
   - For vertical videos made for Reels, TikTok or Shorts, keep words and key visuals out of the bottom fifth and the right edge, where the app's buttons and caption sit.
   - If you add sound, aim for about -14 LUFS so it isn't quieter or louder than other videos in the feed.
   - In captions, use my exact words. If you're not sure what I said, ask me instead of guessing.
   - When I correct something, add it to notes/checks.md as a DO or DON'T line and read that file before every render.
   - Never generate paid images, video or audio without asking me first.

6. Ask me if I want to connect OpenArt (optional). If yes, walk me through it: Customize, Connectors, add a custom connector named OpenArt with the URL https://mcp.openart.ai/mcp, then Connect and sign in (no API key needed). Test it by listing my recent OpenArt creations.

7. Make a 3 second test video that says "Ready" on a pink background and render it to renders/test.mp4. Test your eyes: pull one frame from it and tell me what you see. Test your ears: set up the local Whisper with whisper.cpp version 1.5.5 (ask me before downloading the model, the base English one is enough) and transcribe mia-motion-graphics/sample-voice.wav, then show me the words with their timings. Then start the preview (npm run dev) in the background so it doesn't block you, and give me the link to Remotion Studio.

If the test render times out, try again and point Remotion at my system Chrome with --browser-executable. When you're done, tell me in a few lines what's set up and what to try first.
```
