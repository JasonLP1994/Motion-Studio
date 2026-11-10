---
name: remotion-transitions
description: This skill should be used when the user asks to create custom Remotion transitions, asks about "cool transitions", "cinematic transitions", "striped transitions", "glitch transitions", "custom TransitionPresentation", or wants to build scene-to-scene transitions in Remotion beyond the built-in library. Also triggers for "how to make transitions in Remotion", "custom transition", "high-energy transitions", "energy transitions", "branded transitions".
version: 1.0.0
---

# Remotion Custom Transitions
> **Motion Studio integration (local override):** Respect the creator's art direction for THIS video above all defaults in this imported skill. Follow `CLAUDE.md`, `notes/craft.md` and `notes/checks.md` (read before every render; includes DON'T use charcoal/teal side-panel teaching cards). Build in **Remotion**: all motion is a pure function of `useCurrentFrame()` (time = frame / fps). Treat this skill's CSS / GSAP / Web Animations / `requestAnimationFrame` / timer examples as technique references to translate, not code to paste, unless the user explicitly asks for a web/HTML deliverable. No CDN or remote imports at render time; install any npm package locally and ask before adding a new dependency. **Verification:** never run `npx playwright screenshot` / `npx playwright install` or `scripts/seek-shot.sh`; render stills with `npx remotion still`, tile them with `scripts/contact-sheet.sh` and check the MP4 with `scripts/probe-mp4.sh`, then score as `CLAUDE.md` requires. Finished videos are delivered in chat and never committed to GitHub. Never claim a render exists until tested. The catalog's colours (for example emerald) come from the original campaign: move every colour into the video's config. Install `@remotion/transitions` pinned to the project's Remotion version (4.0.542) only when a video needs it, after asking.


This skill teaches you how to build **production-grade, high-energy custom transitions** in Remotion using the `TransitionPresentation` API — the same pattern used in Fyltr's Instagram Reel campaign.

## Quick Reference

- [Custom Transition Pattern](./references/custom-transition-pattern.md) — The `TransitionPresentation` API, the exact component shape, and how timing works
- [Transition Catalog](./references/transition-catalog.md) — 6 battle-tested transitions with full source: Striped Slam, Zoom Punch, Diagonal Reveal, Emerald Burst, Vertical Shutter, Glitch Slam
- [Animation Math](./references/animation-math.md) — Easing functions, stagger formulas, spring configs, and the `clamp` extrapolation pattern used throughout

## Core Concept

Remotion's `@remotion/transitions` package exposes a `TransitionPresentation` type. You implement a **component** that receives:
- `presentationProgress` — `0` at transition start → `1` at transition end
- `presentationDirection` — `"exiting"` (old scene) or `"entering"` (new scene)
- `children` — the scene being wrapped

The same component wraps **both** scenes simultaneously. You animate different things depending on direction.

## Golden Rules

1. **Never use CSS transitions/animations** — all motion via `interpolate()` / `spring()` driven by `presentationProgress`
2. **Never use `useCurrentFrame()`** inside a transition component — use `presentationProgress` only
3. Always return `{ component, props: {} }` — the `props` object must exist even if empty
4. **Create instances outside components** at module level to keep them stable across re-renders
5. Pair with `linearTiming` (for dramatic frame-perfect transitions) or `springTiming` (for springy physics)

## When to Load References

- Building a new custom transition → load [custom-transition-pattern.md](./references/custom-transition-pattern.md) first
- Copying/adapting an existing effect → load [transition-catalog.md](./references/transition-catalog.md)
- Debugging timing or easing math → load [animation-math.md](./references/animation-math.md)
