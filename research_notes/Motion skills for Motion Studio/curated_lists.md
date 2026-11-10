# Curated lists, registries and marketplaces of agent skills: motion graphics and video candidates (as of 2026-11-10)

Method note: read-only research. Licences were checked by reading each repo's LICENSE file from raw.githubusercontent.com. The GitHub API, github.com HTML pages (via curl) and skills.sh were blocked from this session (skills.sh returned ENOTFOUND, so it would need to be allowed in network settings). For that reason, last-update dates are only known where a GitHub org page loaded through WebFetch or the README states a date. Everything else says "date unverified". Nothing was installed or run.

## What are the best-maintained curated lists/registries of agent skills as of late 2026, and which motion/video skills do they include?

### Takeaway
The four main GitHub lists are hesreallyhim/awesome-claude-code, VoltAgent/awesome-agent-skills, travisvn/awesome-claude-skills and ComposioHQ/awesome-claude-skills. All of them vet lightly, mostly with star thresholds and form bots, and none audit security. The motion/video entries they list are mostly paid generation APIs (fal, Sora, MiniMax, Runway) or packs the studio already has. The most useful new leads from the lists are iart-ai/motion-skills, video-shotcraft, capcut-cli, showreel, the official GSAP skills and HyperFrames.

### Cited Findings
**How each list vets entries**
- hesreallyhim/awesome-claude-code: recommendations are made only through an issue form, and "the bot is a mechanical form-validator, it does not review the quality of the recommended resource". The maintainer says "there is no formal submission/review process at the moment". One criterion is "at least 100 stars", and requiring "any form of signup or payment" is called a blocker. Recommendations must be made by humans. The list is CC-style licensed ("Awesome Claude Code © 2026 by hesreallyhim"). — [CONTRIBUTING.md](https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/CONTRIBUTING.md)
- travisvn/awesome-claude-skills: requires "social proof". PRs for skills under 10 stars are "closed automatically". It rejects "SaaS Wrappers" (skills that exist only to call a commercial API or paid subscription) and teaser/upsell content, and does not accept PRs submitted with AI assistance. — [CONTRIBUTING.md](https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main/CONTRIBUTING.md)
- VoltAgent/awesome-agent-skills (MIT): "We review all submissions and may decline skills that don't meet the quality bar". The skill "must have real community usage… Brand new skills… are not accepted". Descriptions are 10 words or fewer. Official vendor skills link out to officialskills.sh. — [CONTRIBUTING.md](https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/main/CONTRIBUTING.md), [README](https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/main/README.md)
- ComposioHQ/awesome-claude-skills: a vendor-run list (no LICENSE file found). Many entries are Composio's own app-automation skills, such as TikTok Automation and YouTube Automation (uploads, channel management). Its motion/video entries are Slack GIF Creator, Video Downloader, youtube-transcript and Pixelbin-Media-Generation (an "85+ API portfolio"). — [README](https://raw.githubusercontent.com/ComposioHQ/awesome-claude-skills/master/README.md)
- skills.sh, the registry behind `npx skills add` (vercel-labs/skills CLI, MIT): could not be reached from this session. HyperFrames notes that "`skills add` resolves the skills.sh registry blob, which can lag `main` by hours". — [HyperFrames README](https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md); CLI licence MIT per [vercel-labs/skills LICENSE](https://raw.githubusercontent.com/vercel-labs/skills/main/LICENSE)
- Third-party directories (claudemarketplaces.com, claudeskills.info, skills.cat, openskillindex.com, agent-skills.md, skillsdirectory.com, tessl.io) mirror GitHub skills. Search results showed no evidence of audits on these sites. — [search listing e.g. claudeskills.info best video skills](https://claudeskills.info/best/video-skills/), [claudemarketplaces](https://claudemarketplaces.com/skills/dylantarre/animation-principles/video-motion-graphics)

**Motion/video entries found in each list**
- hesreallyhim/awesome-claude-code: `motion-skills` (iart-ai, ~50 skills / 14 packs); `Vox director skill` (Alisa0808); `showreel` (HeyRenan: screenshots, flow GIFs/MP4s, terminal recordings); `capcut-cli` (edit CapCut/JianYing projects); `Molecular Animation` (Blender over MCP); `Flue` (drives Premiere, Blender and others by script); `blender-kiln`. — [README](https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/README.md)
- VoltAgent/awesome-agent-skills: `remotion-dev/remotion` (official, already in the studio); `google-labs-code/remotion` (walkthrough videos from Stitch designs); `heygen-com/hyperframes`; `greensock/gsap-*` (official GSAP skills); `anthropics/slack-gif-creator`. Paid/API-bound entries: `openai/sora`, `fal-ai-community/fal-generate`, `fal-kling-o3`, `fal-lip-sync`, `fal-video-edit`, `fal-upscale`, `MiniMax-AI/cli`, `MiniMax-AI/gif-sticker-maker`, `veniceai/venice-video`, `degausai/wonda`, `taisly/agent` (publishing). Also `flutter/flutter-animating-apps` and `vercel-labs/react-view-transitions` (UI animation, not video). — [README](https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/main/README.md)
- travisvn/awesome-claude-skills: `slack-gif-creator` and `frontend-slides` (animation-rich HTML decks). Its "Video Tutorials" section is "coming soon". — [README](https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main/README.md)
- anthropics/skills: creative skills such as slack-gif-creator. "Many skills in this repo are open source (Apache 2.0)". No dedicated video skill appears in the README. — [README](https://raw.githubusercontent.com/anthropics/skills/main/README.md)
- anthropics/claude-plugins-official (Apache-2.0 LICENSE): its marketplace.json lists `hyperframes` ("Write HTML, render video… captions, voiceovers, audio-reactive visuals, and website-to-video capture"), Runway (video/image/audio generation through the Runway API, needs a Runway account) and Together AI (includes video generation, paid API). — [marketplace.json](https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json)

**Candidate table: list-sourced and creator skills (not iart-ai or HyperFrames; those are covered below)**

| Name | Repo | Licence (verified from LICENSE) | Last update | New capability | Runtime | Footprint / risks | Rec |
|---|---|---|---|---|---|---|---|
| video-shotcraft | [Vincentwei1021/video-shotcraft](https://raw.githubusercontent.com/Vincentwei1021/video-shotcraft/main/README.md) | Apache-2.0 (code/docs); Freesound audio under each file's own licence, CC BY credit needed | README says "2026-10 · Shot library refresh" (124 cards / 150 shots); 2026-09 Motion Workbench; 2026-08 JianYing export | Library of tuned shot/motion recipes for product promos: captures real pages, storyboards, cuts to beat, sound design, frame checks, JianYing (CapCut CN) export | Remotion | Downloads from Freesound (blocked on this network); README notes Remotion's paid company licence; "No API key is needed"; ships CLI scripts | **Add (top pick)**: a Remotion-native shot library the studio lacks. Read scripts first and use only bundled or own audio |
| claude-code-video-toolkit | [digitalsamba/claude-code-video-toolkit](https://raw.githubusercontent.com/digitalsamba/claude-code-video-toolkit/main/README.md) | MIT | date unverified | Full workspace: script, voiceover, music, visuals, render. Templates (release notes, parody-short), Manim skill | Remotion + Python (`uv sync`), moviepy | ElevenLabs (paid) optional, self-hosted Qwen3-TTS optional, VOICEPEAK paid; "No API keys needed" for the base path; heavy clone | **Maybe**: take individual templates/skills, don't adopt the whole workspace |
| text-to-lottie | [diffusionstudio/lottie](https://raw.githubusercontent.com/diffusionstudio/lottie/main/README.md) | MIT text (the LICENSE has no title line but is word-for-word MIT; © 2026 Diffusion Studio Inc.) | date unverified | Generates production Lottie JSON from SVG/prompts with an included Skia Skottie player | Its own player; Lottie output can be played in Remotion via @remotion/lottie (inference) | Sets up a player workspace (npm deps); no API keys mentioned | **Maybe/Add**: new output format (Lottie) for app/web handoff |
| motion-design-skill | [LottieFiles/motion-design-skill](https://raw.githubusercontent.com/LottieFiles/motion-design-skill/main/README.md) | MIT | date unverified | Philosophy-first motion direction: 8-step checklist, personality archetypes, duration/easing tables, choreography | Any (doc-only) | Docs only; no keys | **Maybe**: UI-focused and largely overlaps motion-art-direction and HyperFrames craft notes |
| gsap-skills (official) | [greensock/gsap-skills](https://raw.githubusercontent.com/greensock/gsap-skills/main/README.md) | MIT | date unverified | Correct GSAP: timelines, ScrollTrigger, plugins (all now free after Webflow acquisition) | GSAP/web; not idiomatic in Remotion (frame-driven) | Docs. README tells agents to "recommend GSAP" by default (promotional steering) | **Skip** for a Remotion studio; **Maybe** if HyperFrames is ever adopted |
| showreel | [HeyRenan/showreel](https://raw.githubusercontent.com/HeyRenan/showreel/main/README.md) | MIT | date unverified | Annotated screenshots, flow GIFs/MP4s, terminal captures from URL + CSS selectors, pixel-verified | Own headless Chromium | "No credentials, no telemetry"; one-time Playwright + ~90MB Chromium download (conflicts with the studio rule: never `npx playwright install`) | **Maybe**: product-UI capture for demos; check that it can use the installed Playwright |
| capcut-cli | [renezander030/capcut-cli](https://raw.githubusercontent.com/renezander030/capcut-cli/master/README.md) | MIT | date unverified | Writes editable CapCut/JianYing drafts (silence-aware cuts, styled captions) | Node ≥18, zero deps; optional Whisper/FFmpeg | Global npm install; `ANTHROPIC_API_KEY` only for `translate`; no server/upload | **Maybe**: handoff to CapCut, which the studio already targets for overlays |
| Vox Director | [Alisa0808/vox-director](https://raw.githubusercontent.com/Alisa0808/vox-director/main/README.md) | MIT | date unverified | Vox-style paper-collage explainer end to end | Atlas Cloud API + ffmpeg | Requires `ATLASCLOUD_API_KEY` (paid); UTM affiliate links | **Skip**: paid API |
| OpenMontage | [calesthio/OpenMontage](https://raw.githubusercontent.com/calesthio/OpenMontage/main/README.md) | AGPL-3.0 | date unverified | Agentic video pipelines; works with zero API keys; real-footage documentaries | Python pipeline | Copyleft; optional Google GenAI/fal.ai keys | **Skip**: AGPL licence and a separate runtime |
| animation-principles (144 skills) | [dylantarre/animation-principles](https://raw.githubusercontent.com/dylantarre/animation-principles/main/README.md) | MIT | date unverified | Disney 12 principles × 12 contexts | Doc-only | 144 skills means trigger noise | **Skip**: bloat; one principles skill is enough |
| Claude Design Skillstack | [freshtechbro/claudedesignskills](https://raw.githubusercontent.com/freshtechbro/claudedesignskills/main/README.md) | MIT | date unverified | Three.js, GSAP, R3F, Lottie, plus "authoring-motion" bundle (Blender, Spline, Rive, Substance 3D) | Web/3D tools | Plugins include scripts and agents; third-party, not vendor-made | **Skip** (web-focused); maybe mine its Rive/Spline notes |
| slack-gif-creator | [anthropics/skills](https://raw.githubusercontent.com/anthropics/skills/main/README.md) | Apache-2.0 per README for "many skills" (per-skill licence unverified) | date unverified | Size-constrained animated GIF export with validators | Python | Low | **Maybe**: GIF export helper |
| Motion Canvas skills | [videozero/skills](https://raw.githubusercontent.com/videozero/skills/main/README.md) | Apache-2.0 | date unverified | Motion Canvas reference (18 docs), editor-control HTTP API, animation-basics | Motion Canvas (different runtime) | Third-party, not from the Motion Canvas project | **Skip** unless switching runtime |

### Inferences
- No list does security or telemetry review. Star thresholds (10 for travisvn, 100 for hesreallyhim) and "community usage" (VoltAgent) are the only filters. travisvn's "no SaaS wrappers" rule is the closest match to the studio's no-paid-services preference.
- VoltAgent is the broadest index of official vendor skills. hesreallyhim has the most recent creator-built video tools. ComposioHQ is vendor-curated and mostly promotes Composio integrations.
- Most video entries on these lists are paid generative APIs (fal, Sora, MiniMax, Runway, Together, Atlas Cloud), so they fail the studio's constraints.

### Gaps
- skills.sh could not be reached (DNS blocked), so install counts, ranking method and any vetting or telemetry policy of the registry or the `npx skills` CLI are unverified.
- Last-commit dates for non-iart-ai repos are unverified because github.com and the GitHub API were blocked. Only video-shotcraft has dates, from its own README.
- No security audit of scripts was done. Each candidate's `scripts/` folder should be read before adoption.

## What other skills exist in the iart-ai motion-design-skills and tiktok-video-skills repos (and the wider iart-ai collection)?

### Takeaway
Besides the four the studio has, motion-design-skills adds seven (animation-principles, color-motion, after-effects, beat-sync-editing, remotion-video, logo-animation, motion-background). tiktok-video-skills adds countdown-video and lower-thirds. The wider iart-ai org (MIT throughout) has about 20 more packs. The strongest picks are documentation-style skills with no keys. Two packs (talking-head, generative-illustration) need paid APIs.

### Cited Findings
- motion-design-skills (MIT, 218 stars, updated Jun 22, 2026) contains: animation-principles (timing, easing, 12 principles), color-motion (palettes, OKLCH/Lab interpolation, grading, render colour management), shot-composition (have), motion-art-direction (have), after-effects (expressions, rigging, export), beat-sync-editing (cut to the beat, transitions, retiming, speed ramps), remotion-video (data-driven Remotion, one MP4 per CSV row), logo-animation (reveals, stingers, loaders), motion-background (mesh gradients, shader auroras, particles, loops). — [README](https://raw.githubusercontent.com/iart-ai/motion-design-skills/main/README.md); dates/stars — [iart-ai org](https://github.com/orgs/iart-ai/repositories)
- tiktok-video-skills (MIT, 21 stars, updated Jun 22, 2026) contains: short-form-video (have), caption-animation (have), countdown-video (frame-accurate, drift-free timers with digit flip/roll), lower-thirds (branded name/role lower thirds templated across a roster). — [README](https://raw.githubusercontent.com/iart-ai/tiktok-video-skills/main/README.md)
- READMEs funnel to the paid iart.ai agent ("The full agent runs at iart.ai", UTM links). I found no telemetry in the READMEs. A sample SKILL.md (kinetic-typography) ships helper scripts (`scripts/seek-shot.sh`, `scripts/contact-sheet.sh`) for screenshots and contact sheets. — [motion-design README](https://raw.githubusercontent.com/iart-ai/motion-design-skills/main/README.md), [kinetic-typography SKILL.md](https://raw.githubusercontent.com/iart-ai/kinetic-typography-skills/main/skills/kinetic-typography/SKILL.md)
- Other iart-ai packs (all with MIT LICENSE files) and their skills, from each README; dates and stars from the org page:
  - kinetic-typography-skills (24★, Jun 22): kinetic-typography (char/word/line staggers, split-text, variable-font weight, text on path, lyric cards; CSS, GSAP, Framer Motion, Remotion). — [README](https://raw.githubusercontent.com/iart-ai/kinetic-typography-skills/main/README.md)
  - data-animation-skills (18★): chart-animation (bar-chart race, line reveal, count-ups, batch across CSVs), animated-infographic, presentation-video (deck to narrated video). — [README](https://raw.githubusercontent.com/iart-ai/data-animation-skills/main/README.md)
  - explainer-video-skills (93★): explainer-video, wrapped-video (Spotify-Wrapped-style personalised 9:16 from a data table), diagram-animation, whiteboard-animation (stroke-by-stroke draw-on), isometric-animation. — [README](https://raw.githubusercontent.com/iart-ai/explainer-video-skills/main/README.md)
  - youtube-video-skills (6★): audiogram (captioned waveform video), youtube-intro-outro (3–5 s sting, 20 s end screen respecting YouTube clickable zones). — [README](https://raw.githubusercontent.com/iart-ai/youtube-video-skills/main/README.md)
  - ad-video-skills (20★): ad-creative-video (CSV to N variants across placements), launch-video, testimonial-video (quote reveals, star ratings). — [README](https://raw.githubusercontent.com/iart-ai/ad-video-skills/main/README.md)
  - ecommerce-video-skills (16★): product-demo-video (device frames, synthetic cursor, zoom-to-region), promo-video (price strike-through, promo code, countdown), photo-slideshow (Ken Burns, beat-synced). — [README](https://raw.githubusercontent.com/iart-ai/ecommerce-video-skills/main/README.md)
  - text-message-video-skills (7★): text-message-animation (iMessage/WhatsApp bubbles, typing indicators, from script/CSV). — [README](https://raw.githubusercontent.com/iart-ai/text-message-video-skills/main/README.md)
  - map-animation-skills (25★): map-animation (Google Earth Studio to AE, or GeoJSON/SVG maps). — [README](https://raw.githubusercontent.com/iart-ai/map-animation-skills/main/README.md)
  - web-animation-skills (88★): gsap-web, 60fps-animation, page-transition-animation, accessible-animation, micro-interaction, glassmorphism, svg-animation, lottie-animation, ascii-animation. — [README](https://raw.githubusercontent.com/iart-ai/web-animation-skills/main/README.md)
  - webgl-animation-skills (53★): shader-glsl, threejs-animation, particle-system. — [README](https://raw.githubusercontent.com/iart-ai/webgl-animation-skills/main/README.md)
  - manim-skills (18★): manim (Manim CE, LaTeX equation morphs, render to MP4/GIF). — [README](https://raw.githubusercontent.com/iart-ai/manim-skills/main/README.md)
  - freelance-motion-skills (7★): creative-brief, motion-pricing, client-revisions, video-delivery-specs (per-platform specs, cutdown matrix, QC checklist), brand-motion-guidelines. — [README](https://raw.githubusercontent.com/iart-ai/freelance-motion-skills/main/README.md)
  - Newer repos not in the 14-pack README list: motion-skills hub (1.3k★, Oct 25, 2026), talking-head-skills (Oct 25, 2026), b-roll-skills (Oct 17, 2026), javascript-animation-skills (59★, Sep 30, 2026), lower-thirds-skills (Sep 30, 2026), generative-illustration-skills (Jun 30, 2026), awesome-motion-skills (Jun 22). — [iart-ai org](https://github.com/orgs/iart-ai/repositories)
  - talking-head-skills: "Bring your own fal and ElevenLabs API keys"; AI presenter costs about $0.30 per clip. — [README](https://raw.githubusercontent.com/iart-ai/talking-head-skills/main/README.md)
  - b-roll-skills: talking-head-b-roll (transcribe, plan each line, build on a transparent canvas page, render MP4 + alpha layer); local whisper.cpp or ElevenLabs Scribe. — [README](https://raw.githubusercontent.com/iart-ai/b-roll-skills/main/README.md)
  - javascript-animation-skills: javascript-animation (short films computed on HTML canvas, hand-drawn ink/picture-book drawing library) + soundtrack (music written in Web Audio, rendered offline to WAV); "zero image assets, zero API keys"; setup mentions `npx playwright install chromium`. — [README](https://raw.githubusercontent.com/iart-ai/javascript-animation-skills/main/README.md)
  - lower-thirds-skills: standalone lower-thirds with a render script for WebM alpha, ProRes 4444, green-screen MP4, OBS mode; "No API keys". — [README](https://raw.githubusercontent.com/iart-ai/lower-thirds-skills/main/README.md)
  - generative-illustration-skills: AI-generated sprite assets + music, needs an API key (optional `REPLICATE_API_KEY`). — [README](https://raw.githubusercontent.com/iart-ai/generative-illustration-skills/main/README.md)

**Recommendations for iart-ai (all MIT, no telemetry seen, doc-style plus optional helper scripts)**

| Skill | Rec | Reason |
|---|---|---|
| beat-sync-editing | **Add** | Cut rhythm, retiming, speed ramps; complements the sound-effects beat grid |
| logo-animation | **Add** | Logo reveals and stingers are not covered by current templates |
| kinetic-typography | **Add** | Deep type-motion craft with Remotion recipes |
| color-motion | **Add** | OKLCH interpolation, grading and render colour management are new |
| motion-background | **Add** | Looping backgrounds (mesh, aurora, particles) |
| countdown-video, lower-thirds (tiktok pack) | **Add** (pick the tiktok version *or* lower-thirds-skills, not both) | lower-thirds-skills adds a ProRes 4444/WebM alpha render path that fits the studio's overlay rule, but needs Playwright (use the installed copy) |
| diagram-animation, whiteboard-animation, isometric-animation, wrapped-video | **Add/Maybe** | New explainer looks; explainer-video itself overlaps explainer-default |
| chart-animation, animated-infographic | **Maybe** | Data video; check whether its Remotion recipes overlap remotion-markup |
| audiogram, youtube-intro-outro, testimonial-video, photo-slideshow, promo-video, text-message-animation | **Maybe** | Niche formats; add on demand |
| video-delivery-specs, brand-motion-guidelines, creative-brief | **Maybe** | Useful for a beginner's delivery QC; non-rendering |
| javascript-animation + soundtrack | **Maybe** | Canvas runtime, not Remotion. Web Audio soundtrack is new. Its `npx playwright install` step breaks the studio rule |
| shader-glsl, particle-system, threejs-animation | **Maybe** | Usable with @remotion/three (inference); advanced |
| manim | **Maybe/Skip** | Needs a Python + Manim + LaTeX runtime install outside the folder |
| animation-principles | **Skip/Maybe** | Overlaps craft.md and motion-art-direction |
| remotion-video, launch-video, product-demo-video, explainer-video | **Skip** | Duplicate the official Remotion skills and explainer-high-energy/default |
| b-roll-skills | **Skip** | Duplicates motion-broll |
| map-animation | **Skip** | Remotion maps is already installed |
| after-effects, web-animation pack (gsap-web, micro-interaction, glassmorphism, page transitions, 60fps, accessible) | **Skip** | Not video/Remotion work |
| talking-head-skills, generative-illustration-skills | **Skip** | Paid fal/ElevenLabs/Replicate APIs |

### Inferences
- iart-ai's packs are marketing funnels for iart.ai, but the skills read as standalone documentation with helper scripts. The paid dependencies are limited to two clearly labelled packs.
- Most of the 14 packs had their last update on the same day (Jun 22, 2026), which looks like a bulk sync. The hub and the newer canvas-based packs are where active work is (Sep–Oct 2026).

### Gaps
- I only read the SKILL.md for kinetic-typography. Network calls inside the other skills' helper scripts are unverified.
- The awesome-motion-skills README had no skill table, so its contents are unknown.

## What other skills does the HeyGen HyperFrames repo publish?

### Takeaway
HyperFrames (Apache-2.0) publishes 9 skills: hyperframes, hyperframes-cli, hyperframes-registry, media-use, reverse-any-video (Pro), style-sampling (Pro), figma, slideshow and remotion-to-hyperframes. It also has 6 repo-internal skills that are not installed by default. They all assume the HyperFrames runtime (HTML+GSAP, Node 22, the `hyperframes` CLI), so none should be added to a Remotion studio. The craft references the studio already took are the useful part.

### Cited Findings
- Core set: `/hyperframes` (render contract and references), `/hyperframes-cli`, `/hyperframes-registry` ("About 450 ready-made blocks… transitions, overlays, titles, kinetic type, captions, charts, maps, 3D, camera moves"), `/media-use` ("music, sound effects, images… voiceover, avatar and generated video… with HeyGen or free local tools"), `/reverse-any-video` ("HyperFrames Pro"), `/style-sampling` (five styles, "HyperFrames Pro"). On demand: `/figma`, `/slideshow` (navigable deck, not MP4), `/remotion-to-hyperframes` (migrates Remotion/Motion Canvas/Lottie into HyperFrames). "The six repo-internal skills under `.claude/skills` / `.agents/skills` are excluded by default." — [HyperFrames README](https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md)
- The skills folder on main lists exactly these 9 folders. — [skills tree](https://github.com/heygen-com/hyperframes/tree/main/skills)
- Licence Apache-2.0 (LICENSE file). Requirements: Node.js 22+, FFmpeg. Studio app is free, and its "Pro plan adds HeyGen's top video, image, voice and music models". README links carry UTM tracking. — [README](https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md)
- HyperFrames is also listed in Anthropic's official plugin marketplace. — [claude-plugins-official marketplace.json](https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json)

### Inferences
- hyperframes-registry (450 blocks) could be a design reference for Remotion rebuilds, but using its blocks directly needs the HyperFrames runtime. Recommendation: **skip** installing anything. media-use and the Pro skills bring HeyGen paid tiers, and the studio's CLAUDE.md already flags the usage beacon.

### Gaps
- I did not read the 6 repo-internal skills' names or the usage-beacon code path in this pass. Repo star count and last-commit date are unverified.

## Are there notable motion/video skills from studios, tool vendors (Rive, Spline, Jitter, Cavalry, Motion Canvas, Revideo) or individual creators?

### Takeaway
Of the listed vendors, only LottieFiles (motion-design-skill) and GreenSock (gsap-skills) publish official skills, both MIT. I found no official skills from Rive, Spline, Jitter, Cavalry, Motion Canvas or Revideo. What exists for them is third-party (videozero for Motion Canvas, freshtechbro for Rive/Spline). Diffusion Studio's text-to-lottie and the creator-built video-shotcraft are the strongest non-vendor finds.

### Cited Findings
- LottieFiles/motion-design-skill: MIT, "Universal motion design principles… implementation-agnostic". — [README](https://raw.githubusercontent.com/LottieFiles/motion-design-skill/main/README.md)
- greensock/gsap-skills: MIT, "Official AI skills for GSAP". — [README](https://raw.githubusercontent.com/greensock/gsap-skills/main/README.md)
- Motion Canvas: videozero/skills (Apache-2.0) is third-party, with motion-canvas, motion-canvas-agent and animation-basics skills. — [README](https://raw.githubusercontent.com/videozero/skills/main/README.md). A web search turned up no official Motion Canvas, Rive or Revideo skill, and "nothing for Revideo at all". — [search results incl. skills.sh/videozero](https://skills.sh/videozero/skills/motion-canvas), [rive-interactive (third-party)](https://www.skills.sh/freshtechbro/claudedesignskills/rive-interactive)
- Rive/Spline/Blender appear only inside the third-party freshtechbro "authoring-motion" bundle. — [README](https://raw.githubusercontent.com/freshtechbro/claudedesignskills/main/README.md)
- Remotion's own skills repo has no LICENSE file at the root, and includes a `/remotion-license` skill pointing to where to buy a licence. — [remotion-dev/skills README](https://raw.githubusercontent.com/remotion-dev/skills/main/README.md)
- Other creator video skills seen in directories but not verified: inkeep motion-video-skill, blitzreels-motion-graphics, video-talkcraft (video-shotcraft's narration sibling). — [skills.lc inkeep](https://www.skills.lc/inkeep/team-skills/inkeep-team-skills-plugins-gtm-skills-motion-video-skill-md), [playbooks blitzreels](https://playbooks.com/skills/blitzreels/agent-skills/blitzreels-motion-graphics), [video-shotcraft README](https://raw.githubusercontent.com/Vincentwei1021/video-shotcraft/main/README.md)

### Inferences
- Shortlist for a Remotion studio, by priority: (1) video-shotcraft (Apache-2.0, Remotion, active Oct 2026); (2) iart-ai beat-sync-editing, logo-animation, kinetic-typography, color-motion, motion-background, lower-thirds/countdown (MIT, docs); (3) text-to-lottie (MIT, new Lottie output); (4) capcut-cli (MIT, CapCut handoff). Everything else is maybe or skip.

### Gaps
- Jitter and Cavalry: no skills found at all, either official or community.
- video-talkcraft, blitzreels and inkeep skills: licences and contents unverified.
