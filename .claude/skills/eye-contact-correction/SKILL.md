---
name: eye-contact-correction
description: Correct a slight downward teleprompter eyeline in existing Phillips English talking-head footage. Use a local offline, reversible gaze adjustment before Motion Studio motion graphics, then verify eye realism and lip-sync. MacBook Neo support is unverified until a real test.
---

# Eye-contact correction — Phillips English

## When to use
Use when Jason has recorded a talking-head YouTube lesson, TikTok/Reel/Short, or Preply video and his eyes point **slightly below the webcam** because the teleprompter sits beneath it. This is optional finishing work, **not** a reason to change his existing teleprompter, camera, or microphone. Do not use on every clip automatically.

Read `CLAUDE.md` and, for editing jobs, `.claude/skills/motion-stack/SKILL.md` before proceeding. Stack this **before** `longform-to-shorts`, captions, compositing and final export. Eye correction changes the person, not the camera background.

## Important status / provenance
This skill provides an **integration recipe and a working invocation wrapper**, not a preinstalled model. It uses the optional offline gaze pass from the third-party MIT project [Powderhond/teleprompter](https://github.com/Powderhond/teleprompter), specifically `skills/teleprompter/scripts/gaze-pass.mjs`. That pass decodes frames with FFmpeg, detects landmarks through MediaPipe in a headless browser, geometrically nudges the iris, and makes a separate MP4. It is **not generative gaze correction** and is limited by eye/lid geometry. Credit the upstream author and retain their license if copying or modifying their code.

The upstream author states it was developed/tested on Windows; macOS, including the **MacBook Neo A18 Pro**, is **not confirmed**. Never promise it works, or say an output was successfully corrected, until it has run and passed playback/visual checks on the user's actual Mac. It may be slow, introduce artifacts or fail. There is no NVIDIA requirement for this chosen approach.

## Working layout
- Source footage: `inputs/` or an explicitly supplied local path; **never overwrite or relocate the original**.
- Third-party dependency (only after user approval): `tools/teleprompter/`, an ignored local directory; never vendor downloaded binaries, models, node_modules or video into Git.
- Finished and test files: `renders/` (ignored by Git). Use versioned names, such as `renders/lesson-gaze-test-v1.mp4` and `renders/lesson-gaze-v2.mp4`.
- Script: `.claude/skills/eye-contact-correction/scripts/run.sh` from the Motion Studio repository.

## Start with a safe dependency check
From the Motion Studio root:

```bash
bash .claude/skills/eye-contact-correction/scripts/run.sh --check
```

This only reports dependencies; it does **not** install anything. Requirements for the upstream offline pass are: Node.js, FFmpeg/ffprobe, an upstream checkout, `playwright` with a Chromium browser, and the upstream MediaPipe model assets. Review the output. **Ask permission before cloning, installing anything or downloading models**, especially outside the repo. Respect existing Motion Studio tooling; never overwrite its dependencies. The suggested first-time setup, **only after approval**, is:

```bash
git clone https://github.com/Powderhond/teleprompter.git tools/teleprompter
cd tools/teleprompter
npm install
npx playwright install chromium
node skills/teleprompter/scripts/fetch-models.mjs
cd ../..
```

FFmpeg must also be available; if missing, explain options and request approval before installing. Review upstream code/changes before executing them. For a repeatable environment, record the tested upstream commit SHA in local notes; do not silently upgrade the upstream checkout.

## Process a **short test first**
1. Inspect source video/frame rate, camera angle and audio. Ensure eyes/face are clearly visible. Make an isolated 10–15 second **local** test extract with FFmpeg if the full recording is long; keep the original intact.
2. Run the check. If dependencies are missing or the Mac fails to run it, report the blocker—do not claim correction occurred.
3. Apply subtle correction (start around 0.35–0.5 strength; the upper limit can look false). Example:

```bash
bash .claude/skills/eye-contact-correction/scripts/run.sh \
  --in "renders/lesson-test-input.mp4" \
  --out "renders/lesson-gaze-test-v1.mp4" \
  --strength 0.4
```

The wrapper invokes the upstream offline pass, not an AI model invented in this skill. Set `MOTION_EYE_TOOL_PATH` if the approved upstream checkout lives elsewhere. It refuses to overwrite an existing output.

4. Compare original and corrected footage **frame-by-frame** at normal size and 100% zoom: gaze looks at lens, eyelids/iris/eyelashes stable, normal blinks, no warped or floating pupils, no jitter, no face deformation. Listen for audio sync and check source/output duration. Use original if the correction is less natural.
5. Ask Jason whether the small improvement is worth it. Only then apply to longer footage; preserve versioned originals, exports, and metadata. This step can be skipped altogether if the camera eyeline already looks natural.
6. Proceed with the existing Motion Studio stack (cutting, backgrounds, art direction, captions, audio, longform-to-shorts), and verify the final render separately.

## Safety and quality
- **No footage or renders on GitHub**, GitHub issues/releases, external cloud sites, or paid services. Keep exports local or deliver via Claude's normal download mechanism.
- Do not execute `setup.sh`, upstream auto-installers, or scripts fetched from the internet without inspecting them and getting approval.
- Do not change or replace the source file, alter skin/face identity, or overcorrect the eyes. Do not invent a new gaze direction on footage where the eyes are occluded.
- Match final audio and frame rate; if audio is missing, sync drifts, or artifacting appears, reject the processed version.
- This is a *local post-production skill*, not a live webcam effect or a camera-driver replacement.
- Never claim a completed Mac test until the command really runs on the MacBook Neo with actual footage.

## User-facing next step
Once Claude has the local Motion Studio project, ask Jason to provide a **10–15-second clip filmed while reading the current teleprompter**. Run `--check`, request approval for any installation, then show the original/corrected comparison. No need to purchase a physical teleprompter unless this test fails.
