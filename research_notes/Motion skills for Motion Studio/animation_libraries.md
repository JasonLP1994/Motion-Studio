# 2D Animation Libraries and Techniques: Agent Skills for a Remotion Studio

Research date: 2026-11-10. Read-only research: nothing was installed or run.

Method and access notes, for the report writer:
- GitHub's API (gh and api.github.com) was blocked in this session. Repo files, LICENSE files and file listings were read through the jsDelivr GitHub mirror (cdn.jsdelivr.net/gh/..., data.jsdelivr.com).
- Library licences and dates come from the npm registry (registry.npmjs.org).
- remotion.dev and motion.dev were blocked (DNS outside the allowed hosts). Remotion facts below come from the studio's installed `remotion-markup` skill (v4.0.542). Motion facts come from the ai-kit repo files and search snippets.
- "Last update" for skill repos is taken from CHANGELOG dates or copyright years where available. Exact last-commit dates could not be fetched (no GitHub API), so treat them as approximate.

## Candidate summary table

| # | Name | URL | Licence (how verified) | Last update | New capability | Runs in Remotion? | Footprint / risks | Rec. |
|---|---|---|---|---|---|---|---|---|
| 1 | `motion-design` (LottieFiles motion-design-skill) | https://github.com/lottiefiles/motion-design-skill | MIT (LICENSE file, "Copyright (c) 2025 LottieFiles"; SKILL.md frontmatter `license: MIT`) | v1.0.0; a directory lists "updated May 18, 2026" (secondary) | Library-agnostic motion principles: timing/easing tables, Disney principles for UI, choreography, emotion mapping, entrance/exit, multi-element, quality checklist | Docs only, so yes as guidance. Timings are UI milliseconds and must be converted to frames | 19 Markdown files, about 60 KB, no scripts. Only network use is a README image from lottie.host | **Maybe**: clean and safe, but it overlaps heavily with `motion-art-direction` and `notes/craft.md`. It is UI-oriented and not about Lottie files |
| 2 | `gsap-skills` (official GreenSock; 8 skills + llms.txt) | https://github.com/greensock/gsap-skills | Skill repo MIT (LICENSE, "Copyright (c) 2026 GreenSock"). The GSAP library itself is the "Standard 'no charge' license", not OSI (npm) | 2026 (copyright year). gsap 3.15.1 published 2026-11-04 | SplitText (kinetic type), DrawSVG (path drawing), MorphSVG (shape morph), MotionPath, CustomEase/Wiggle/Bounce, timelines | Not natively frame-driven. Usable only as a paused timeline seeked from `useCurrentFrame()` (inference, below) | 8 SKILL.md files (about 92 KB), plus example apps (Vite/React/Vue/Nuxt) and plugin manifests. No scripts in the skills. Adds an `npm install gsap` dependency | **Maybe** (cherry-pick `gsap-plugins` and `gsap-timeline`): strong SVG and text techniques, but the skills assume real-time playback and never mention Remotion. Proprietary library licence |
| 3 | `remotion-transitions` (ashad001) | https://github.com/ashad001/remotion-transitions | MIT (LICENSE, "Copyright (c) 2026 Ashad") | v1.0.0, 2026-03-12 (CHANGELOG). Single release | 6 custom `TransitionPresentation` transitions with full source (Striped Slam, Zoom Punch, Diagonal Reveal, Emerald Burst, Vertical Shutter, Glitch Slam), plus animation-math reference | **Yes, native**: driven by `presentationProgress`, with interpolate/spring | 5 Markdown files (about 27 KB) + plugin.json + skills-lock.json. No scripts | **Add**: the only Remotion-native transition pack found. Extends, does not duplicate, `remotion-markup/transitions.md`. Single-author and new, so review the code |
| 4 | `motion` skill (Motion AI Kit, official, motiondivision) | https://github.com/motiondivision/ai-kit (installed via `npx motion-ai`) | **Unverified**: no root LICENSE on jsDelivr, and package.json has no licence field. Search snippet says "free and open source (MIT)" | v7.0.1, 2026-10-15 (CHANGELOG) | Motion/Framer Motion best practices, docs search, CSS spring generation, transition editor, MotionScore audits | **No**: Motion (motion/react) animates on its own real-time clock. Remotion forbids CSS/timer-driven animation | Installer (npx) + hosted MCP servers (network). Audits, premium examples and saving need Motion+ (paid) or an account. Repo has node scripts (push-to-site.js etc.) | **Skip**: web-UI focused, network/MCP dependent, partly paid |
| 5 | `anime.js Best Practices` (davidosemwegie) | https://github.com/davidosemwegie/animejs-best-practices | MIT (LICENSE, "Copyright (c) 2025 Umbrellamode") | v1.3.0 (SKILL.md). Date unverified | anime.js v4 timelines, stagger, SVG (morph/draw), text, scroll | No: anime.js plays in real time (WAAPI-first per SKILL.md). Only seek-based use could work | SKILL.md + 5 references + example JS + an agent file. No install scripts | **Skip**: WAAPI-first guidance conflicts with Remotion rendering, and GSAP covers the same ideas better |
| 6 | `animejs` (bowtiedswan) | https://github.com/bowtiedswan/animejs-skills | **None found** (no LICENSE file, so all rights reserved by default) | Unverified | anime.js v4 incl. text splitting, SVG morphing | No (real-time) | Ships `install.sh` that curls files from raw.githubusercontent.com into ~/.claude/skills (outside the workspace) | **Skip**: no licence, plus a shell installer |
| 7 | `motion-dev-animations-skill` (199-biotechnologies) | https://github.com/199-biotechnologies/motion-dev-animations-skill | MIT (LICENSE, 2025) | Unverified (2025) | Motion for React/Vue/Svelte hover/scroll/parallax examples | No (web UI, real-time) | Includes `scripts/validate_motion_config.py`, and process docs (DEPLOYMENT_STATUS, VALIDATION_V3) | **Skip**: web-UI micro-interactions, not video |
| 8 | `claude-code-video-toolkit` (digitalsamba) | https://github.com/digitalsamba/claude-code-video-toolkit | MIT (LICENSE, 2024 Digital Samba) | Unverified | Remotion toolkit; search snippet says it imports custom transitions (glitch, light leak, clock wipe, checkerboard) | Remotion parts yes | 412 files. Bundles elevenlabs, qwen-edit, ltx2, acestep skills (paid APIs / GPU models), voice-clone commands, and its own `.claude/settings.json` | **Skip** as a pack: duplicates the official Remotion skills and pulls in paid services. At most, borrow transition ideas by reading |
| 9 | HyperFrames library skills: `gsap`, `animejs`, `lottie`, `waapi`, `css-animations`, `three`, `remotion-to-hyperframes` (heygen-com) | https://github.com/heygen-com/hyperframes (skills/) | Apache-2.0 (repo LICENSE) | Latest tag 0.9.31 (jsDelivr). Date unverified | Library recipes for HyperFrames' seek-driven HTML renderer | Needs the HyperFrames runtime. Techniques are conceptually close to Remotion's seek model | `skills/gsap/scripts/extract-audio-data.py` is executable. HyperFrames material contains `npx hyperframes` commands and a "usage beacon" line, which the studio's CLAUDE.md says never to run | **Skip** installing. The studio already holds HyperFrames craft references and stays on Remotion. Could not read these SKILL.md files (jsDelivr refused, repo too large) |
| 10 | Other community GSAP/Motion skills (mindrally, martinholovsky "JARVIS HUD", dylantarre animation-principles, affaan-m ECC motion-*, oakoss, secondsky) | Registry listings (see sources in Q2) | Unverified | Unverified | Generic GSAP/Motion guidance | Web real-time | Unknown | **Skip**: unofficial duplicates of #2/#4 |

Libraries behind the techniques (npm, verified 2026-11-10):
- `@remotion/paths` 4.0.542, MIT, published 2026-11-09.
- `@remotion/shapes` 4.0.542, MIT.
- `@remotion/transitions` 4.0.542, npm licence field "UNLICENSED" (it falls under the Remotion licence).
- `@remotion/lottie` 4.0.542, "SEE LICENSE IN LICENSE.md".
- `flubber` 0.4.2, MIT, last published 2018-03-01 (unmaintained).
- `gsap` 3.15.1, Standard no-charge licence, 2026-11-04.
- `animejs` 4.5.0, MIT, 2026-06-22.
- `motion` 14.12.0, MIT, 2026-11-10.
- `lottie-web` 5.13.0, MIT, 2025-05-21.
- `@lottiefiles/dotlottie-web` 0.82.1, MIT, 2026-11-02.

## Does LottieFiles publish an official agent skill ("motion-design")? What does it contain, and its licence?

### Takeaway
Yes. LottieFiles publishes `lottiefiles/motion-design-skill` (skill name `motion-design`, v1.0.0, MIT). It is a documentation-only, library-agnostic motion-principles skill and is not a Lottie-authoring tool. It is safe, but it largely duplicates what the studio already has (`motion-art-direction`, `notes/craft.md`). Lottie playback in Remotion is already covered by `remotion-markup/lottie.md`.

### Cited Findings
- The repo LICENSE is MIT, "Copyright (c) 2025 LottieFiles". The SKILL.md frontmatter says `license: MIT`, `author: LottieFiles`, `version: "1.0.0"` — [LICENSE via jsDelivr](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/LICENSE); [SKILL.md](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/skills/motion-design/SKILL.md)
- Contents: SKILL.md (12.6 KB) plus `director/` (choreography, context-adaptation, core-philosophy, decision-framework, disney-principles, emotion-mapping, motion-personality, narrative-structure), `patterns/` (ambient-continuous, entrance-exit, multi-element, state-feedback) and `reference/` (property-selection, quality-checklist, timing-easing-tables, troubleshooting). That is 19 Markdown files, no scripts — [jsDelivr file listing](https://data.jsdelivr.com/v1/packages/gh/lottiefiles/motion-design-skill@main?structure=flat)
- Its description reads: "Works with CSS, Framer Motion, GSAP, Lottie, Spring, or any animation system". It targets "UI animations (buttons, cards, modals, page transitions)", micro-interactions and loading states — [SKILL.md](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/skills/motion-design/SKILL.md)
- Example rules: a "1/3 Rule (distance): No motion travels more than 1/3 of screen without a keyframe change". The timing table runs from "Tooltip 80-120ms" to "Page transition 400-600ms" and "Dramatic reveal 600-1200ms". Distance-duration scaling goes from 50px=0.8x to full screen=1.8-2.0x. Exit is 65-75% of entrance — [SKILL.md](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/skills/motion-design/SKILL.md); [timing-easing-tables.md](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/skills/motion-design/reference/timing-easing-tables.md)
- Install is `npx skills add LottieFiles/motion-design-skill`, and the README claims support for "40+ agents" — [README](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/README.md)
- A scan of all files found no curl/fetch/telemetry/API-key references. The only remote URL is the README logo on lottie.host — [README](https://cdn.jsdelivr.net/gh/lottiefiles/motion-design-skill@main/README.md)
- A registry lists about 6.7k installs, about 877 stars, updated May 18, 2026. Counts differ across sites — [search results incl. skills directories](https://skillselion.com/skills/lottiefiles/motion-design-skill/motion-design)
- The studio's `remotion-markup` skill already includes `lottie.md` ("Using Lottie Animations in Remotion", `@remotion/lottie` with `delayRender`/`continueRender`) and `transitions.md` (TransitionSeries, fade/slide/wipe, custom presentations, light-leak overlays) — local file `/home/user/.claude/skills/remotion-markup/` (v4.0.542)
- The studio's `motion-art-direction` skill already defines "motion personality" presets and mentions orchestrating gsap/lottie skills — local `/home/user/.claude/skills/motion-art-direction/SKILL.md`

### Inferences
- "Motion design" here means motion principles, not Lottie JSON creation. The studio gains no new Lottie capability from it.
- Its millisecond tables are tuned for UI feedback. For video titles and holds they would need converting to frames and lengthening. `notes/craft.md` (HyperFrames-derived, video-specific) is probably the better source, so the recommendation is maybe and low priority. If added, its `entrance-exit.md` and `multi-element.md` (stagger/choreography) are the most transferable parts.

### Gaps
- No exact last-commit date: the GitHub API was blocked, and only the secondary "May 18, 2026" figure exists.
- I found no official LottieFiles skill for authoring or editing Lottie/dotLottie files, and no LottieFiles MCP. One search did not surface one, but that does not prove none exists.

## Are there GSAP or anime.js / Motion agent skills, and do their techniques translate to Remotion's frame-based model?

### Takeaway
Yes. There are official GSAP skills (greensock/gsap-skills, MIT skill text) and an official Motion AI Kit (motiondivision/ai-kit, with an MCP server and paid Motion+ features). anime.js has only community skills. None is written for frame-driven rendering. Only GSAP translates cleanly, by building a paused timeline and seeking it to `frame / fps` on every frame. Motion and anime.js are real-time/WAAPI engines and conflict with Remotion's "no CSS/timer animation" rule.

### Cited Findings
- The greensock/gsap-skills LICENSE is MIT, "Copyright (c) 2026 GreenSock". Skills: gsap-core (14.8 KB), gsap-timeline, gsap-plugins (21.6 KB), gsap-scrolltrigger, gsap-utils, gsap-react, gsap-performance, gsap-frameworks, plus `skills/llms.txt`, Claude/Cursor plugin manifests and example apps — [LICENSE](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/LICENSE); [file listing](https://data.jsdelivr.com/v1/packages/gh/greensock/gsap-skills@main?structure=flat)
- Install options: `/plugin marketplace add greensock/gsap-skills`, `npx skills add https://github.com/greensock/gsap-skills --skill gsap-core`, or copying into `~/.claude/skills/` — [README](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/README.md)
- The README says "GSAP is 100% free — including every plugin… SplitText, MorphSVG, etc. are free for everyone, including commercial use… no Club membership, no .npmrc / auth token" — [README](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/README.md)
- The gsap npm licence is "Standard 'no charge' license: https://gsap.com/standard-license" (not MIT), latest 3.15.1 published 2026-11-04 — [npm registry](https://registry.npmjs.org/gsap)
- gsap-plugins documents SplitText ("Splits an element's text into characters, words, and/or lines… for staggered or per-unit animation"; "SplitText does not support SVG `<text>`"), DrawSVG (animates the visible stroke segment, e.g. `drawSVG: "0% 100%"`; "Only affects stroke (not fill)") and MorphSVG ("Start and end shapes do not need the same number of points"; `shapeIndex`, `type: "rotational"`; `convertToPath`) — [gsap-plugins SKILL.md](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/skills/gsap-plugins/SKILL.md)
- gsap-timeline documents `paused: true` ("create paused; call .play() to start"), and gsap-core shows `tween.progress(0.5)`. Neither file mentions Remotion, seeking per frame, or rendering — [gsap-timeline](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/skills/gsap-timeline/SKILL.md); [gsap-core](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/skills/gsap-core/SKILL.md)
- Remotion's rule, from the installed skill: "Drive animations using useCurrentFrame() and interpolate(). CSS transition or animation will not render correctly… Tailwind animation class will not render correctly" — local `/home/user/.claude/skills/remotion-markup/SKILL.md`
- The Motion AI Kit `motion` skill covers "Motion (prev Framer Motion) and CSS animation… documentation and example search, CSS spring and bounce generation, MotionScore… audits… visual transition editor". "Audits are a Motion+ capability". "A Motion account (free): saving a transition. Run the Motion+ MCP server, signed in". The CHANGELOG has 7.0.1 at 2026-10-15 and 7.0.0 at 2026-07-28 ("Transition editor as MCP App. Documentation search now open to everyone") — [SKILL.md](https://cdn.jsdelivr.net/gh/motiondivision/ai-kit@main/plugins/motion/skills/motion/SKILL.md); [CHANGELOG](https://cdn.jsdelivr.net/gh/motiondivision/ai-kit@main/CHANGELOG.md)
- Per motion.dev search snippets, the AI Kit installs with `npx motion-ai` and adds a free MCP server that searches docs. The installer and /motion skill are described as "free and open source (MIT)". Motion+ adds spring generation, audits and premium source via `npx motion-ai --plus` and a hosted MCP server. However, the repo has no root LICENSE on jsDelivr and package.json has no licence field — [motion.dev/docs/ai-kit (search result)](https://motion.dev/docs/ai-kit); [package.json](https://cdn.jsdelivr.net/gh/motiondivision/ai-kit@main/package.json)
- `motion` 14.12.0 is MIT on npm (published 2026-11-10) — [npm](https://registry.npmjs.org/motion)
- anime.js community skills:
  - davidosemwegie/animejs-best-practices: MIT (2025 Umbrellamode), v1.3.0, "CRITICAL: WAAPI-First Approach" — [SKILL.md](https://cdn.jsdelivr.net/gh/davidosemwegie/animejs-best-practices@main/SKILL.md); [LICENSE](https://cdn.jsdelivr.net/gh/davidosemwegie/animejs-best-practices@main/LICENSE)
  - bowtiedswan/animejs-skills: no LICENSE, and ships `install.sh` that downloads from raw.githubusercontent.com into `$HOME/.claude/skills` — [install.sh](https://cdn.jsdelivr.net/gh/bowtiedswan/animejs-skills@main/install.sh)
- animejs 4.5.0 is MIT, published 2026-06-22 — [npm](https://registry.npmjs.org/animejs)
- HyperFrames ships library skills named animejs, css-animations, gsap, lottie, three, waapi, remotion-to-hyperframes (and others) under Apache-2.0. Its gsap skill includes `scripts/extract-audio-data.py`. One listing says its anime.js skill advises GSAP for complex scene sequencing — [jsDelivr listing](https://data.jsdelivr.com/v1/packages/gh/heygen-com/hyperframes@main?structure=flat); [LICENSE](https://cdn.jsdelivr.net/gh/heygen-com/hyperframes@main/LICENSE); [claudemarket listing](https://www.claudemarket.ai/skills/heygen-com/hyperframes/animejs)
- Unofficial GSAP skills (martinholovsky JARVIS-HUD, mindrally, bbeierle12, dylantarre) also exist in registries — [playbooks.com](https://playbooks.com/skills/martinholovsky/claude-skills-generator/gsap); [agent-skills.md](https://agent-skills.md/skills/dylantarre/animation-principles/gsap-greensock)

### Inferences
- **GSAP to Remotion translation (inference, not documented in the skill):**
  1. Build the timeline once with `paused: true`, with no autoplay, ScrollTrigger, ticker or `.play()`.
  2. On every render, call `tl.seek(frame / fps)` (or `tl.progress(...)`) inside a component that reads `useCurrentFrame()`.
  3. DOM-mutating plugins (SplitText, MorphSVG, DrawSVG) need refs and must be created once per mount.
  4. Each frame is rendered in a fresh or parallel tab, so state must be fully derivable from the seek position.
  This needs a local verification render before it becomes a studio rule. The studio's CLAUDE.md favours pure Remotion. Cheaper Remotion-native alternatives exist for most cases: `@remotion/paths` for drawing/morphing, and per-word/char splitting with `interpolate`/`spring` for kinetic type.
- The GSAP skill's real value for this studio is its technique catalogue (SplitText masks/lines, DrawSVG segment model, MorphSVG `shapeIndex`, CustomWiggle/Bounce eases). Those ideas can be re-implemented with `interpolate`. Adding the whole 8-skill pack would mostly load irrelevant web topics (ScrollTrigger, React hooks, Nuxt, performance for 60 fps browsers).
- GSAP's "Standard no-charge" licence is proprietary but free. Flag it if the studio wants only OSI-licensed dependencies.
- The Motion AI Kit is the riskiest option: it is an npx installer, uses hosted MCP servers (network), has account-gated features and an unclear repo licence, and Motion's springs run on real time. Motion's spring maths duplicates Remotion's built-in `spring()`.
- anime.js offers nothing GSAP or native Remotion doesn't, and the main skill's WAAPI-first stance would actively mislead an agent working in Remotion.

### Gaps
- I could not fetch Remotion's own docs on third-party animation libraries (remotion.dev was blocked), so I could not confirm whether Remotion officially documents a GSAP or anime.js seek pattern.
- I could not read the HyperFrames gsap/animejs/lottie SKILL.md contents (jsDelivr refused the files; the repo is likely over its size limit). It is unconfirmed whether they contain usage-beacon lines; the studio CLAUDE.md says HyperFrames material includes one.
- I could not verify the Motion AI Kit licence from a LICENSE file.

## Are there kinetic typography, SVG morph, or transition-pack skills or Remotion community packages with agent-skill docs?

### Takeaway
- **Transitions:** one good Remotion-native candidate, `ashad001/remotion-transitions` (MIT, docs-only, 6 custom TransitionPresentations).
- **SVG morph/path drawing:** no dedicated skill found. The best route is Remotion's own MIT `@remotion/paths` (or flubber for unequal shapes), written up as a local studio note, since the installed skills never mention it.
- **Kinetic typography:** no dedicated skill found. Existing coverage is `explainer-high-energy` (kinetic typography), `caption-animation`, and remotion-markup's text-highlights/measuring-text. GSAP SplitText guidance is the best external technique reference.

### Cited Findings
- `ashad001/remotion-transitions`:
  - MIT ("Copyright (c) 2026 Ashad"), v1.0.0 released 2026-03-12.
  - Transitions: Striped Slam, Zoom Punch, Diagonal Reveal, Emerald Burst, Vertical Shutter, Glitch Slam.
  - References: custom-transition-pattern.md, transition-catalog.md (14 KB of full source, plus a "Full Scene Sequence (Reel Pattern)"), animation-math.md.
  [LICENSE](https://cdn.jsdelivr.net/gh/ashad001/remotion-transitions@main/LICENSE); [CHANGELOG](https://cdn.jsdelivr.net/gh/ashad001/remotion-transitions@main/CHANGELOG.md); [transition-catalog.md](https://cdn.jsdelivr.net/gh/ashad001/remotion-transitions@main/references/transition-catalog.md)
- Its golden rules: "Never use CSS transitions/animations — all motion via interpolate() / spring() driven by presentationProgress". "Never use useCurrentFrame() inside a transition component". "Create instances outside components at module level". Pair with `linearTiming` or `springTiming` — [SKILL.md](https://cdn.jsdelivr.net/gh/ashad001/remotion-transitions@main/SKILL.md)
- It says it uses "the same pattern used in Fyltr's Instagram Reel campaign". Listed on skills.sh, first seen Mar 11, 2026 — [SKILL.md](https://cdn.jsdelivr.net/gh/ashad001/remotion-transitions@main/SKILL.md); [skills.sh](https://www.skills.sh/ashad001/remotion-transitions/remotion-transitions)
- A different skills.cat entry with the same name (delphinereverse794/remotion-transitions) covers glitch/striped transitions. Its provenance is unclear, possibly a copy — [skills.cat](https://skills.cat/skills/delphinereverse794/remotion-transitions)
- The installed `remotion-markup/transitions.md` already covers TransitionSeries, `fade`, custom presentation scaffolding and light-leak overlays. `remotion-markup` also lists `evolve()`, `pixelDissolve()`, `venetianBlinds()`, `radialProgressivePixelate()` effects, and has `light-leaks.md`, `text-highlights.md`, `measuring-text.md` — local `/home/user/.claude/skills/remotion-markup/`
- A grep of all installed skills for `evolvePath`, `interpolatePath`, `@remotion/paths`, `@remotion/shapes` and `flubber` found **no matches** — local search of `/home/user/.claude/skills`
- `@remotion/paths` 4.0.542 (MIT, 2026-11-09) and `@remotion/shapes` 4.0.542 (MIT) are current. `@remotion/transitions` depends on both — [npm @remotion/paths](https://registry.npmjs.org/@remotion%2Fpaths); [npm @remotion/transitions](https://registry.npmjs.org/@remotion%2Ftransitions)
- `flubber` 0.4.2 is MIT, last published 2018-03-01, with dependencies d3-array, d3-polygon, earcut, svg-path-properties, svgpath, topojson-client — [npm](https://registry.npmjs.org/flubber)
- `digitalsamba/claude-code-video-toolkit` (MIT, 412 files) contains Remotion skills plus elevenlabs, qwen-edit, ltx2, acestep and voice-clone tooling. Search snippets say it imports custom transitions (glitch, light leak, clock wipe, checkerboard) — [LICENSE](https://cdn.jsdelivr.net/gh/digitalsamba/claude-code-video-toolkit@main/LICENSE); [file listing](https://data.jsdelivr.com/v1/packages/gh/digitalsamba/claude-code-video-toolkit@main?structure=flat); [skills.sh](https://skills.sh/digitalsamba/claude-code-video-toolkit/remotion)
- `hugobowne/remotion-video` is described as covering "motion grammar, kinetic typography, character moments, and measurable self-review". jsDelivr could not resolve a `main` branch, so its licence and contents are unverified — [TypingMind listing](https://www.typingmind.com/skills/hugobowne-remotion-video)
- Searches for a dedicated "kinetic typography" agent skill returned none. The closest leads are bowtiedswan's anime.js text splitting and GSAP SplitText — [search results incl. vibeindex](https://www.vibeindex.ai/skills/bowtiedswan/animejs-skills/animejs); [gsap-plugins](https://cdn.jsdelivr.net/gh/greensock/gsap-skills@main/skills/gsap-plugins/SKILL.md)

### Inferences
- Adding `remotion-transitions` gives the studio a ready catalogue of high-energy, beat-friendly transitions that suit `explainer-high-energy` and the `duppy-hype` template. Its "Emerald Burst" and accent colours should be moved into the studio's one-config-file pattern.
- `@remotion/paths` (from training knowledge, not fetched: `evolvePath()` for stroke draw-on, `interpolatePath()` for morphing between compatible paths, `getLength`/`getPointAtLength` for motion along a path) is the frame-native equivalent of DrawSVG/MorphSVG/MotionPath. Flubber's `interpolate(a, b)(t)` is a pure function, so it is frame-safe and handles shapes with different point counts, but it is unmaintained since 2018. Writing a short studio note or template (`templates/svg-draw-morph/`) is safer than adopting a third-party skill.
- Kinetic typography is best served by a studio-authored template that combines word timings from Whisper, per-word/char splits, and `spring()`, taking split/mask ideas from GSAP SplitText. A third-party skill would mostly overlap `explainer-high-energy` and `caption-animation`.

### Gaps
- I could not confirm `@remotion/paths` API names from remotion.dev (blocked). They are from training knowledge and should be checked with the `remotion-docs` skill.
- I could not confirm hugobowne/remotion-video's licence or files, or digitalsamba's transition source files.
- I found no Remotion community npm package with agent-skill docs dedicated to kinetic text or SVG morphing.

## Which are documentation-only (safe) versus ones that run code or call paid services?

### Takeaway
- **Docs-only, permissive:** LottieFiles motion-design (MIT), the gsap-skills SKILL.md files (MIT; example apps are inert), ashad001 remotion-transitions (MIT), davidosemwegie anime.js (MIT).
- **Run code or touch the network/paid services:** Motion AI Kit (npx installer, hosted MCP, Motion+ paid tier), bowtiedswan (install.sh curl, no licence), 199-biotechnologies (Python validator), digitalsamba toolkit (ElevenLabs and other paid/GPU services), HyperFrames gsap (Python script, plus the CLI and beacon the studio forbids).

### Cited Findings
- LottieFiles motion-design: 19 .md files plus LICENSE/README/.gitignore, no scripts — [listing](https://data.jsdelivr.com/v1/packages/gh/lottiefiles/motion-design-skill@main?structure=flat)
- gsap-skills: the skills are SKILL.md only. The repo also has `examples/` with package.json/vite configs, plus `.claude-plugin` and `.cursor-plugin` manifests — [listing](https://data.jsdelivr.com/v1/packages/gh/greensock/gsap-skills@main?structure=flat)
- remotion-transitions: SKILL.md, 3 references, CHANGELOG, plugin.json, skills-lock.json, no scripts — [listing](https://data.jsdelivr.com/v1/packages/gh/ashad001/remotion-transitions@main?structure=flat)
- Motion AI Kit: the repo contains `scripts/generate-changelog-csv.js`, `scripts/push-to-site.js`, `scripts/validate-template.mjs`. The skill refers to a Motion+ MCP server and account sign-in — [listing](https://data.jsdelivr.com/v1/packages/gh/motiondivision/ai-kit@main?structure=flat); [SKILL.md](https://cdn.jsdelivr.net/gh/motiondivision/ai-kit@main/plugins/motion/skills/motion/SKILL.md)
- bowtiedswan: `install.sh` with `REPO_BASE="https://raw.githubusercontent.com/BowTiedSwan/animejs-skills/main"` writes to `$HOME/.claude/skills/animejs` — [install.sh](https://cdn.jsdelivr.net/gh/bowtiedswan/animejs-skills@main/install.sh)
- 199-biotechnologies: `scripts/validate_motion_config.py` and a JSON schema — [listing](https://data.jsdelivr.com/v1/packages/gh/199-biotechnologies/motion-dev-animations-skill@main?structure=flat)
- digitalsamba: `.claude/skills/elevenlabs`, `qwen-edit`, `ltx2`, `acestep`, and commands `generate-voiceover.md`, `voice-clone.md`, plus its own `.claude/settings.json` — [listing](https://data.jsdelivr.com/v1/packages/gh/digitalsamba/claude-code-video-toolkit@main?structure=flat)
- HyperFrames: `skills/gsap/scripts/extract-audio-data.py` — [listing](https://data.jsdelivr.com/v1/packages/gh/heygen-com/hyperframes@main?structure=flat)
- A keyword scan (curl, fetch(, beacon, telemetry, analytics, api key) over the downloaded LottieFiles, GSAP and ashad001 files found only install commands and documentation links. There were no beacons or runtime network calls — local scan of files fetched from jsDelivr

### Inferences
- Recommended order for the studio:
  1. **Add** `remotion-transitions` (native, MIT, docs-only).
  2. **Maybe** cherry-pick `gsap-plugins` + `gsap-timeline` as reference material, only with a studio note on the paused-timeline/seek pattern and the GSAP licence caveat.
  3. **Maybe** LottieFiles `motion-design` as a secondary principles reference (low priority because of overlap).
  4. **Skip** the Motion AI Kit, all anime.js skills, 199-biotechnologies, digitalsamba, and HyperFrames library skills.
  5. **Fill the gaps** for SVG draw/morph (`@remotion/paths`, flubber) and kinetic typography with studio-authored templates rather than third-party skills.
- Installing via `npx skills add` or `/plugin marketplace add` runs an installer and may write outside the workspace (~/.claude/skills). Under the studio's "ask before installing anything outside this folder" rule, copying the Markdown into `.claude/skills/` by hand is the conservative route.

### Gaps
- No skill repo was audited for transitive changes after the dates noted. Pin a commit if adopting.
- The Motion AI Kit's runtime network behaviour (what the MCP server sends) was not inspected beyond SKILL.md.
