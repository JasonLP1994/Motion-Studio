# Post-production, audio and data motion skills for a Remotion studio

Scope note: research done 2026-11-10, read only. The GitHub API was not enabled for this session, and remotion.dev was blocked by the network. Repo facts come from public GitHub pages via WebFetch. Those pages showed licence, stars and commit counts but **no last-commit dates**, so "last update" is unverified for every repo unless stated. Several facts come only from skill-registry aggregators (skills.sh, skillselion, claudemarket, etc.); these are marked as aggregator-sourced. Star counts on aggregators sometimes conflict with GitHub.

Studio already has: Remotion official skills, Bart's motion pack (motion-broll, object-separation, explainer x3, sound-effects), iart-ai skills (short-form-video, caption-animation, motion-art-direction, shot-composition), longform-to-shorts, HyperFrames craft refs (incl. data and music guides).

## Are there agent skills for colour grading or LUTs that work with ffmpeg/Remotion output?

### Takeaway
Yes. Several community skills cover ffmpeg `lut3d` with .cube files, applied after a Remotion render as an ffmpeg pass. The best-provenanced option is **color-motion** from iart-ai/motion-design-skills (MIT). The studio already trusts that pack, and color-motion is documentation-style. **ffmpeg-color-grading-chromakey** (josiahsiegel, MIT) is the most concrete ffmpeg LUT recipe skill.

### Cited Findings
- **color-motion** (iart-ai/motion-design-skills): "Palettes, gradients, OKLCH/Lab interpolation, grading, and render color management". The repo is MIT with 218 stars and 21 commits, and has `skills/`, `scripts/` and `.claude-plugin/` folders. Whether each skill is docs-only could not be confirmed from the page. — [GitHub iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- **ffmpeg-color-grading-chromakey** (josiahsiegel/claude-plugin-marketplace): covers chroma key, LUT application (`lut3d` with .cube and .3dl), curves and HDR/SDR. It is listed as MIT and was the most-installed of the colour skills, with about 65 installs per skills.sh. — aggregator: [agent-skills.md listing](https://agent-skills.md/skills/josiahsiegel/claude-plugin-marketplace/ffmpeg-color-grading-chromakey), [skillselion listing](https://skillselion.com/skills/josiahsiegel/claude-plugin-marketplace/ffmpeg-color-grading-chromakey)
- The josiahsiegel marketplace repo is MIT with 61 stars and 115 commits. Its ffmpeg content lives in an **ffmpeg-master** meta-bundle ("encoding, effects, platform deployment, Python integrations, and social-video workflows"). The repo has `scripts/` and `.claude/commands`, contents not shown, and no commit date was visible. — [GitHub josiahsiegel/claude-plugin-marketplace](https://github.com/josiahsiegel/claude-plugin-marketplace)
- **claude-video-edit** (agricidaniel/claude-video): a general ffmpeg editing skill that includes `lut3d` .cube grading, plus a blended-intensity variant mixing the graded and original video. It also covers trims, concat, crop, overlays, PiP, green screen, stabilisation and blur. It is small (about 23 stars); licence unverified. — aggregator: [skillselion](https://skillselion.com/skills/agricidaniel/claude-video/claude-video-edit)
- **color-grade** (diegosouzapw/awesome-omni-skill): generates .cube LUTs aimed at DaVinci Resolve and Premiere. It creates LUTs rather than applying them; licence unverified. — aggregator: [openskillindex](https://openskillindex.com/skills/diegosouzapw-awesome-omni-skill-color-grade)
- **editor** (oyi77/1ai-skills): a broad ffmpeg post-production skill whose LUT section uses `lut3d` at 50% intensity blend; licence unverified. — aggregator: [skillsdirectory](https://www.skillsdirectory.com/skills/oyi77-editor)
- **color-grade-ai** (isaacrowntree): a SKILL.md exists on jsDelivr, but its contents and licence were not verified. — [jsDelivr SKILL.md](https://cdn.jsdelivr.net/gh/isaacrowntree/color-grade-ai@main/SKILL.md)

### Inferences
- Applying a LUT is a single ffmpeg filter (`lut3d=file.cube`) after the Remotion render, and ffmpeg is already installed. A short docs-style recipe in `notes/` or a small custom skill may beat installing a large third-party bundle.
- Recommendations:
  - color-motion: **add**. MIT, same trusted pack, covers grading theory and render colour management.
  - ffmpeg-color-grading-chromakey: **maybe**. MIT, concrete recipes, but it ships inside a large marketplace with scripts. Copy only the one skill folder after reading it.
  - claude-video-edit: **maybe**, as a reference only. Licence unverified and it overlaps the ffmpeg skills.
  - color-grade (LUT generator): **skip**. Its output targets DaVinci and Premiere.

### Gaps
- Last-update dates and LICENSE files of the individual skill folders could not be checked, because the GitHub API was blocked.
- No skill found that grades inside Remotion (for example CSS/WebGL LUT shaders on a composition). All found skills are ffmpeg post-passes.

## Are there audio-reactive / music-visualiser / beat-sync agent skills, especially for Remotion?

### Takeaway
Remotion's own `@remotion/media-utils` APIs (`visualizeAudio`, `useWindowedAudioData`, `visualizeAudioWaveform`) are the building blocks. There is no dedicated, well-established Remotion beat-detection skill. The closest options are **beat-sync-editing** (iart-ai, MIT; editing rhythm, not audio-driven animation) and a few small Remotion skills with beat references. The studio's sound-effects skill already checks beat grids against kicks, so overlap is high.

### Cited Findings
- `visualizeAudio()` (in `@remotion/media-utils`) returns an amplitude array. `numberOfSamples` must be a power of two, and low frequencies (bass) sit at the left of the array, so index 0 is the usual bass and beat read. — [Remotion docs: visualize-audio](https://www.remotion.dev/docs/visualize-audio) (via search snippet; site blocked from direct fetch)
- `useWindowedAudioData()` loads only the audio around the current frame. It is recommended for long audio, returns `audioData` and `dataOffsetInSeconds` (to be passed to `visualizeAudio`), and supports all Mediabunny formats. — [Remotion docs: use-windowed-audio-data](https://www.remotion.dev/docs/use-windowed-audio-data)
- `visualizeAudioWaveform` is also in media-utils. — [Remotion docs](https://www.remotion.dev/docs/media-utils/visualize-audio-waveform)
- Remotion has an official prompt-gallery entry for a 32-bar spectrum visualiser synced to an mp3 in `public/`. — [Remotion prompts: audio-spectrum-visualizer](https://www.remotion.dev/prompts/audio-spectrum-visualizer)
- No dedicated beat-detection API was found in the docs search. Beat detection would mean thresholding the low band yourself. — [Remotion docs: audio-visualization](https://www.remotion.dev/docs/audio-visualization)
- **beat-sync-editing** (iart-ai/motion-design-skills, MIT): "Editing rhythm, transitions, retiming, and speed ramps cut to the beat". It covers editing to music, not audio-driven animation. — [GitHub iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- **remotion-beautiful-videos** (norahe0304-art/remotion-video-skill): includes an audio reference covering beat sync, voiceover ducking and audio layers. Licence and install count unverified. — aggregator: [skills.sh](https://skills.sh/norahe0304-art/remotion-video-skill/remotion-beautiful-videos)
- **stopmotion-video** (kosta4a): Remotion-based. It copies `beat.ts` and `transitions.tsx` into `src/` and sets a TEMPO constant. Licence unverified. — aggregator: [ui-skills](https://www.ui-skills.com/skills/kosta4a/stopmotion-video)
- **audio-reactive** (bbeierle12/skill-mcp-claude): maps audio analysis to visuals (smoothing, beat response, frequency mapping) but uses Tone.js, not Remotion. — aggregator: [playbooks](https://playbooks.com/skills/bbeierle12/skill-mcp-claude/audio-reactive)
- "Music to Video Generator" on mcpmarket uses a "deterministic beat grid analyzer" and sub-agents. The target runtime was not stated, and the repo and licence were not identified. — aggregator: [mcpmarket](https://mcpmarket.com/tools/skills/music-to-video-generator-1)

### Inferences
- The highest-value, lowest-risk move may be a custom docs-only skill or template note wrapping `visualizeAudio` and `useWindowedAudioData`. It would include a bass-threshold beat helper and pull in grid checks from the existing sound-effects skill. Third-party options are thin and unverified.
- Recommendations:
  - beat-sync-editing: **add**. MIT, same pack, complements sound-effects with editing-rhythm craft.
  - remotion-beautiful-videos and stopmotion-video: **maybe**. Read them for the beat.ts pattern, but licences are unverified and installs are low.
  - audio-reactive (Tone.js): **skip**. Wrong runtime.

### Gaps
- Could not read the remotion.dev pages directly (host blocked). The API details above come from search snippets.
- No Remotion-specific onset or BPM detection skill was found.

## Are there After Effects / expressions agent skills worth having even though the studio renders with Remotion?

### Takeaway
Two kinds exist. Execution skills drive a live After Effects install, such as **aedev-tools/adobe-agent-skills** (Apache-2.0, macOS-only, runs ExtendScript) and the MCP-AE server. Documentation skills include iart-ai's **after-effects** (MIT, expressions, rigging, export recipes). The execution skills are useless without AE. The docs skill is a maybe: useful only for translating AE references or handing off to editors.

### Cited Findings
- **aedev-tools/adobe-agent-skills**: Apache-2.0 with 117 stars and 18 commits. It includes a `skills/after-effects` skill covering layers, keyframes, expressions, effects, comps, rendering and batch operations, with 34 built-in scripts and query scripts. It is macOS only ("Windows support coming soon"), requires After Effects, and needs the AE preference "Allow Scripts to Write Files and Access Network". No telemetry is described. — [GitHub aedev-tools/adobe-agent-skills](https://github.com/aedev-tools/adobe-agent-skills)
- Aggregators describe it as generating `.jsx` and executing via osascript, with undo groups wrapping mutations. — aggregator: [search summary of skills.sh / skills.cat listings](https://skills.sh/aedev-tools/skills/after-effects)
- **after-effects** (iart-ai/motion-design-skills, MIT): "AE expressions, rigging, export recipes, performance triage, and project hygiene". — [GitHub iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- **TerminalSkills/skills after-effects**: covers ExtendScript, CEP panels, expressions, the aerender CLI and template automation. The aggregator lists Apache-2.0; unverified on GitHub. — aggregator: [typingmind listing](https://www.typingmind.com/skills/terminalskills-after-effects)
- **davidcasan/MCP-AE**: an MCP server for After Effects that bundles a Claude Code skill. — aggregator: [glama](https://images.glama.ai/mcp/servers/davidcasan/MCP-AE)

### Inferences
- The studio has no AE and stays on Remotion, so execution skills add nothing but risk (executable scripts, AE network permission).
- Recommendations:
  - aedev-tools/adobe-agent-skills: **skip**. It needs AE on macOS and runs scripts.
  - MCP-AE: **skip**. Needs AE.
  - iart-ai after-effects: **maybe**. MIT and same pack. Only useful if the user receives AE projects or expression-heavy references to rebuild in Remotion.
  - TerminalSkills after-effects: **skip**. It duplicates the iart-ai skill and the licence is unverified.

### Gaps
- Could not confirm whether the iart-ai after-effects skill folder contains scripts or is docs only.

## Are there data-visualisation animation or logo-animation skills with strong craft guidance?

### Takeaway
For logos, **logo-animation** (iart-ai, MIT) is the natural docs-style fit. **diffusionstudio/lottie** (text-to-lottie, MIT, about 5.7k stars) is the strongest Lottie generator. Lottie output can be played in Remotion via `@remotion/lottie`, but that is not confirmed by the repo. For data viz, many D3 skills exist, but they target interactive web charts. Only "data-viz-commercials" explicitly targets animated data videos with Remotion and D3. The studio's HyperFrames data guide and the installed `dataviz` skill already overlap.

### Cited Findings
- **logo-animation** (iart-ai/motion-design-skills, MIT): "Logo reveals, stingers, splash screens, and loaders for web, video, and app". The same pack also has **motion-background** (mesh gradients, shader auroras, particles, loops) and **animation-principles**. Kinetic typography and data animation are separate iart-ai packs (`kinetic-typography-skills`, `data-animation-skills`). — [GitHub iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- **diffusionstudio/lottie**: MIT, 5.7k stars, 93 commits. It is an "open-source framework for generating production ready Lottie animations" for Claude Code and Codex, writing `public/projects/<project>/<scene>/lottie.json`. It also has `scripts/` and a Vite player, with no paid services listed. Remotion is not mentioned. Its web example loads lottie-web from unpkg. — [GitHub diffusionstudio/lottie](https://github.com/diffusionstudio/lottie)
- A June 2026 guide says text-to-lottie teaches the Lottie JSON dialect accepted by Skia's Skottie renderer. — [mcp.directory guide](https://mcp.directory/blog/claude-text-to-lottie-skill-guide)
- **Wiggle** (talknerdytome-labs/wiggle-claude-skill): turns PNG, SVG or JPG logos into Lottie animations (fade, bounce, pulse, rotate, wiggle, waveform) rendered as GIF or MP4. It has 45 stars and 3 commits, with Python plus `requirements.txt` and `scripts/`. Its licence is in LICENSE.txt, type not shown, so unverified. — [GitHub wiggle-claude-skill](https://github.com/talknerdytome-labs/wiggle-claude-skill)
- **brand-motion-agent-skill** (poudelaman4): a "brand-safe logo animation" skill; licence unverified. — aggregator: [mcpservers.org](https://mcpservers.org/servers/poudelaman4/brand-motion-agent-skill)
- **data-viz-commercials**: triggers on animated charts, Remotion data videos and D3 animation. It advises Remotion for batch-personalised data videos and Motion Canvas for VO-synced explainers. Repo and licence were not identified. — aggregator: [claudskills.com](https://claudskills.com/skills/data-viz-commercials/SKILL.md)
- **d3-visualization** (nexu-io/open-design): covers bar, line, map, force, Sankey, treemap, sunburst, choropleth, scroll and animation techniques. It is web and interactive focused, not Remotion. — aggregator: [skills.sh](https://skills.sh/nexu-io/open-design/d3-visualization)
- **data-visualization** (dylantarre/animation-principles): applies animation principles to charts and dashboards; not tied to D3 or Remotion. — aggregator: [agent-skills.md](https://agent-skills.md/skills/dylantarre/animation-principles/data-visualization)
- Other D3 skills: `d3-viz` (davila7 on Smithery; calesthio) and `lyndonkl/claude d3-visualization` (with animated transitions). — aggregator: [Smithery d3-viz](https://smithery.ai/skills/davila7/d3-viz), [agent-skills.md lyndonkl](https://agent-skills.md/skills/lyndonkl/claude/d3-visualization)

### Inferences
- D3 in Remotion means computing scales and layouts with d3 and driving them by `useCurrentFrame()`, not d3 transitions. Web D3 skills teach the wrong timing model, which is why they are skips or maybes.
- Recommendations:
  - logo-animation: **add**. MIT, same pack, covers stings and reveals with video delivery.
  - motion-background: **maybe**. Useful for loops; overlaps the material-loop template.
  - diffusionstudio/lottie: **maybe**. Strong and popular, MIT. Adds a Lottie asset path (playable via `@remotion/lottie`, a Remotion package), but it runs a Vite player and scripts, and Remotion compatibility is untested.
  - Wiggle: **skip**. Licence unverified, Python deps, tiny.
  - data-viz-commercials: **maybe**. Craft fit is good, but the source repo and licence are unknown.
  - Web D3 skills: **skip**. The HyperFrames data guide and the installed `dataviz` skill already cover chart craft.
  - iart-ai `data-animation-skills` pack: **worth a follow-up check**. Not verified here.

### Gaps
- The iart-ai `data-animation-skills` and `kinetic-typography-skills` packs were not examined.
- Not verified whether diffusionstudio Lottie output renders correctly in `@remotion/lottie`.

## Which are documentation-only versus ones that run code or call paid services? (plus ffmpeg automation and screen-recording skills)

### Takeaway
The iart-ai pack is the closest to documentation-style, though its repo has a `scripts/` folder. Most ffmpeg skills are "generate ffmpeg commands" docs. The big toolkits (digitalsamba, openmontage, HeyGen) and most screen-recorder skills run code, and several need paid accounts or are macOS-only.

### Cited Findings
- **digitalsamba/claude-code-video-toolkit**: MIT, about 2.5k stars, 511 commits. It is Remotion-based, with skills for remotion, elevenlabs, ffmpeg, playwright-recording, video-design, qwen-edit, ideogram4, acestep, ltx2, parody-short, moviepy and runpod, plus about 22 Python CLI tools (incl. `qc`, `sync_check`, `contact_sheet`, `youtube_upload`). It uses paid or cloud services: ElevenLabs, Modal, RunPod, YouTube API, Cloudflare R2 and Ideogram. — [GitHub digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit)
- **heygen-com/skills**: MIT with 544 stars, but it now holds only heygen-avatar, heygen-video and heygen-translate, all of which need a HeyGen account (API billing or plan credits). The old video-edit and other v1 skills moved to `heygen-com/skills-legacy`. `scripts/update-check.sh` contacts raw.githubusercontent.com (opt-in). — [GitHub heygen-com/skills](https://github.com/heygen-com/skills)
- Note: aggregators still list `heygen-com/skills/video-edit` ("runs ffmpeg and ffprobe directly, no wrapper scripts"), which is now legacy. — aggregator: [skills.sh](https://skills.sh/heygen-com/skills/video-edit)
- **calesthio/openmontage**: a large agentic video production system with its own ffmpeg and video-edit skills. One aggregator lists about 43k stars, which is unverified and looks implausibly high. Licence unverified. — aggregator: [vibeindex](https://www.vibeindex.ai/skills/calesthio/openmontage/ffmpeg)
- **madappgang/claude-code ffmpeg-core**: trimming, conversion, scaling and optimisation; FFmpeg 5.0+ recommended. Licence unverified. — aggregator: [agent-skills.md](https://agent-skills.md/skills/madappgang/claude-code/ffmpeg-core)
- **ffmpeg-video-editor** (bryanwhl, also published as openclaw): natural language to ffmpeg commands (cut, trim, convert, compress, aspect, audio extract). — [jsDelivr SKILL.md](https://cdn.jsdelivr.net/gh/bryanwhl/ffmpeg-video-editor@main/SKILL.md); aggregator: [Smithery](https://smithery.ai/skills/openclaw/ffmpeg-video-editor)
- **video-processing-editing** (erichowens/some_claude_skills): ffmpeg automated editing pipelines. — aggregator: [skills.sh](https://skills.sh/erichowens/some_claude_skills/video-processing-editing)
- Screen-recording and demo skills:
  - **smart-screen-recorder** (abhattacherjee): macOS. It records screen and cursor, uses AI vision for zoom scripts, and does voiceover. — aggregator: [claudemarket](https://claudemarket.ai/plugins/abhattacherjee-claude-code-skills/smart-screen-recorder)
  - **Desktop Recorder** (MobAI-App): macOS. A JSON screenplay drives a synthetic cursor, click ripples, follow-cursor zoom and captions. — aggregator: [skillselion](https://skillselion.com/skills/MobAI-App/desktop-recorder-skill/desktop-recorder)
  - **screencli**: a browser recorder with zoom, highlights and cursor, output to MP4 or GIF. — [screencli skill page](https://screencli.pages.dev/skill.html)
  - **Tella Auto Capture**, **Slideshot** and **DemoBites Agentic Recorder**: hosted or commercial services via MCP. — [Tella](https://www.tella.com/auto-capture/record-web-app-demo-from-claude-code.md), [DemoBites](https://www.demobites.com/docs/bites/agentic-recorder)
  - **recordly** (tdimino/claude-code-minoan) and **screenstudio-alt**: auto-zoom and cursor post-processing. — aggregator: [skills.sh recordly](https://www.skills.sh/tdimino/claude-code-minoan/recordly)

### Inferences
- digitalsamba's **playwright-recording** skill fits this studio, which already has Playwright and Chromium. But it sits in a toolkit full of paid-service skills, so read it standalone and copy only that folder: **maybe**.
- digitalsamba's `qc`, `sync_check` and `contact_sheet` tools match the studio's "check frames and score" rule. They are worth reading as reference, not installing wholesale.
- Remaining recommendations:
  - Rest of digitalsamba toolkit: **skip**. Paid APIs, and it duplicates the Remotion skills.
  - heygen-com/skills: **skip**. Paid avatar service, and the editing skills are legacy.
  - openmontage: **skip**. Huge system with unverified licence and stars.
  - Generic ffmpeg skills (ffmpeg-core, ffmpeg-video-editor, video-processing-editing): **maybe at most**. The studio's CLAUDE.md and existing skills already cover ffmpeg frame and audio extraction and loudness. Pick one MIT-verified option only if reframing or concat recipes are needed.
  - macOS screen recorders and hosted demo services: **skip**. Wrong OS, or paid and hosted.
  - screencli: **maybe**. Browser-based, but licence and runtime unverified.
- Overlaps with existing kit:
  - Loudness and SFX are already covered by sound-effects.
  - Caption and short-form overlap with iart-ai and Remotion captions.
  - The iart-ai shot-composition and motion-art-direction skills already installed come from the same `iart-ai/motion-design-skills` repo. Adding color-motion, beat-sync-editing, logo-animation and (optionally) after-effects completes that pack, with no new provenance risk.

### Gaps
- Licences of most aggregator-only skills (openmontage, ffmpeg-core, ffmpeg-video-editor, recorders, data-viz-commercials) are unverified.
- No last-commit dates verified for any repo. Maintenance status cannot be flagged with confidence. Wiggle (3 commits) and adobe-agent-skills (18 commits) look low-activity.
- No dedicated loudness-normalisation skill was evaluated beyond what sound-effects already provides.
