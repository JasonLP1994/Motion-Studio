import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Easing, OffthreadVideo, Sequence, continueRender, delayRender,
  interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";
import { fitText } from "@remotion/layout-utils";
import { duppyConfig as C, Group } from "./config";
import timeline from "./timeline.json";

type Word = { text: string; start: number; end: number };
const FPS = C.output.fps;

// ---------- timing (all derived from the real recording) ----------
export const segments = (() => {
  let out = 0;
  return timeline.segments.map((s) => {
    const from = Math.round(s.from * FPS);
    const dur = Math.round((s.to - s.from) * FPS);
    const seg = { from, dur, outStart: out };
    out += dur;
    return seg;
  });
})();
export const totalFrames = segments.reduce((a, s) => a + s.dur, 0);

type TimedGroup = Group & { words: (Word & { display: string; f: number })[]; startF: number; endF: number; index: number };
const timedGroups: TimedGroup[] = (() => {
  const words = timeline.words as Word[];
  let k = 0;
  const groups = C.groups.map((g, index) => {
    const display = g.text.split(/\s+/);
    const ws = display.map((d) => {
      const w = words[k++];
      if (!w) throw new Error(`Caption group "${g.text}" has more words than the recording`);
      return { ...w, display: d, f: Math.max(0, Math.round(w.start * FPS) - C.captions.leadFrames) };
    });
    return { ...g, words: ws, startF: ws[0].f, endF: 0, index };
  });
  groups.forEach((g, i) => {
    const next = groups[i + 1];
    const lastEnd = Math.round(g.words[g.words.length - 1].end * FPS);
    const holdEnd = lastEnd + Math.round(1.0 * FPS);
    g.endF = next ? Math.min(next.startF, Math.max(holdEnd, g.startF + Math.round((g.role === "hero" ? C.hero.minHold : 0.6) * FPS))) : totalFrames;
    if (next && g.endF > next.startF) g.endF = next.startF;
  });
  return groups;
})();
const heroes = timedGroups.filter((g) => g.role === "hero");

// ---------- fonts ----------
const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender("Loading fonts"));
  useEffect(() => {
    Promise.all([
      loadFont({ family: C.fonts.display, url: staticFile("fonts/anton-latin-400-normal.woff2"), weight: "400" }),
      loadFont({ family: C.fonts.body, url: staticFile("fonts/inter-latin-800-normal.woff2"), weight: "800" }),
    ]).then(() => { setReady(true); continueRender(handle); });
  }, [handle]);
  return ready;
};

// ---------- camera: jump-cut punch-ins + hero punch and shake ----------
const useCamera = (frame: number) => {
  const segIndex = Math.max(0, segments.findIndex((s) => frame >= s.outStart && frame < s.outStart + s.dur));
  let zoom = segIndex % 2 === 1 ? C.video.jumpZoom : 1;
  let dx = 0, dy = 0;
  for (const h of heroes) {
    const first = frame - h.startF;
    if (first >= 0 && first < 30) zoom += C.hero.punchZoom * Math.exp(-first / 6);
    const lastWordF = h.words[h.words.length - 1].f;
    const s = frame - lastWordF;
    if (s >= 0 && s < C.hero.shakeFrames) {
      const a = C.hero.shakePx * (1 - s / C.hero.shakeFrames);
      dx += a * Math.sin(s * 2.7);
      dy += a * Math.cos(s * 3.3);
    }
  }
  return { zoom, dx, dy };
};

const Footage: React.FC = () => {
  const frame = useCurrentFrame();
  const { zoom, dx, dy } = useCamera(frame);
  const scale = C.output.width / C.video.srcWidth;
  const { x, y } = C.video.focus;
  return (
    <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px)`, overflow: "hidden" }}>
      <AbsoluteFill style={{ transformOrigin: `${x}px ${y}px`, transform: `scale(${zoom})` }}>
        {segments.map((s, i) => (
          <Sequence key={i} from={s.outStart} durationInFrames={s.dur}>
            <OffthreadVideo
              src={staticFile(C.video.src)}
              trimBefore={s.from}
              style={{ position: "absolute", left: 0, top: C.video.offsetY, width: C.video.srcWidth * scale, height: C.video.srcHeight * scale }}
            />
          </Sequence>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- lyric captions ----------
const outline = (px: number) => ({
  WebkitTextStroke: `${px}px ${C.colors.outline}`,
  paintOrder: "stroke fill" as const,
});

const Caption: React.FC<{ g: TimedGroup }> = ({ g }) => {
  const frame = useCurrentFrame();
  const size = g.role === "anchor" ? C.captions.anchorSize : C.captions.size;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: C.captions.y - size, display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth: C.captions.maxWidth, textAlign: "center", fontFamily: C.fonts.display, fontSize: size, lineHeight: 1.05,
        textTransform: "uppercase", letterSpacing: "0.01em" }}>
        {g.words.map((w, i) => {
          const t = frame - w.f;
          // Unspoken words keep their space (hidden), so the line never shifts sideways.
          const shown = t >= 0;
          const pop = shown ? interpolate(t, [0, 4], [C.captions.popScale, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : 1;
          const rise = shown ? interpolate(t, [0, 4], [18, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : 0;
          const isAccent = (g.accent ?? []).some((a) => w.display.toLowerCase().replace(/[^a-z']/g, "") === a.toLowerCase());
          return (
            <span key={i} style={{ display: "inline-block", marginRight: C.captions.wordGap, transform: `translateY(${rise}px) scaleY(${pop})`,
              transformOrigin: "50% 100%", visibility: shown ? "visible" : "hidden", opacity: shown ? Math.min(1, (t + 1) / 3) : 0,
              color: isAccent ? C.colors.accent : C.colors.text, ...outline(size * 0.12),
              textShadow: `0 ${size * 0.08}px 0 ${C.colors.outline}` }}>
              {w.display}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// ---------- hero slam words ----------
const splitLines = (text: string) => {
  const words = text.split(/\s+/);
  if (text.length <= 14 || words.length < 2) return [words];
  let best = 1, bestDiff = Infinity;
  for (let i = 1; i < words.length; i++) {
    const d = Math.abs(words.slice(0, i).join(" ").length - words.slice(i).join(" ").length);
    if (d < bestDiff) { bestDiff = d; best = i; }
  }
  return [words.slice(0, best), words.slice(best)];
};

const Hero: React.FC<{ g: TimedGroup; ready: boolean }> = ({ g, ready }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lines = splitLines(g.text.toUpperCase());
  const longest = lines.map((l) => l.join(" ")).sort((a, b) => b.length - a.length)[0];
  const cap = lines.length > 1 ? C.hero.twoLineMaxSize : C.hero.maxSize;
  const size = ready ? Math.min(cap, fitText({ text: longest, withinWidth: C.hero.maxWidth, fontFamily: C.fonts.display, fontWeight: "400" }).fontSize) : cap;
  const color = g.color === "danger" ? C.colors.danger : C.colors.accent;
  const exit = interpolate(frame, [g.endF - 5, g.endF], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  let wi = 0;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: C.hero.centerY, transform: "translateY(-50%)", display: "flex", flexDirection: "column",
      alignItems: "center", opacity: exit, fontFamily: C.fonts.display, fontSize: size, lineHeight: 0.98, textTransform: "uppercase" }}>
      {lines.map((line, li) => (
        <div key={li} style={{ display: "flex", gap: "0.18em" }}>
          {line.map((word) => {
            const w = g.words[wi++];
            const t = frame - w.f;
            if (t < 0) return <span key={wi} style={{ visibility: "hidden" }}>{word}</span>;
            const slam = interpolate(t, [0, C.hero.slamFrames], [C.hero.slamFrom, 1], { extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
            const settle = t >= C.hero.slamFrames ? 1 + 0.05 * (1 - spring({ frame: t - C.hero.slamFrames, fps, config: { damping: 10, stiffness: 220, mass: 0.6 } })) : 1;
            const split = interpolate(t, [0, 8], [16, 5], { extrapolateRight: "clamp" });
            const tilt = interpolate(t, [0, C.hero.slamFrames], [li % 2 ? 6 : -6, li % 2 ? 1 : -1.5], { extrapolateRight: "clamp" });
            return (
              <span key={wi} style={{ display: "inline-block", color, transform: `scale(${slam * settle}) rotate(${tilt}deg)`,
                transformOrigin: "50% 0%", // grows downward, away from the face
                ...outline(size * 0.07),
                textShadow: `${-split}px 0 rgba(255,0,70,0.75), ${split}px 0 rgba(0,225,255,0.75), 0 ${size * 0.05}px 0 ${C.colors.outline}` }}>
                {word}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ---------- three-step blocks ----------
const Steps: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const S = C.steps;
  const shown = timedGroups.filter((g) => g.step && frame >= g.startF);
  const newest = shown.length ? shown[shown.length - 1].step : 0;
  return (
    <>
      {shown.map((g) => {
        const t = frame - g.startF;
        const s = spring({ frame: t, fps, config: { damping: 11, stiffness: 200, mass: 0.7 } });
        const n = g.step!;
        const tilt = n % 2 ? -2 : 1.5;
        return (
          <div key={n} style={{ position: "absolute", left: S.x, top: S.y + (n - 1) * (S.rowHeight + S.gap), width: S.width, height: S.rowHeight,
            display: "flex", alignItems: "center", background: C.colors.blockBg, border: `5px solid ${n === newest ? C.colors.accent : "#2A2A2A"}`,
            boxShadow: `10px 10px 0 ${n === newest ? C.colors.accent : "rgba(0,0,0,0.6)"}`,
            transform: `translateX(${(1 - s) * 140}px) scale(${1.25 - 0.25 * s}) rotate(${tilt + (1 - s) * 8}deg)`, opacity: Math.min(1, t / 3) }}>
            <div style={{ width: S.rowHeight - 10, height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
              background: C.colors.blockNumber, color: C.colors.blockBg, fontFamily: C.fonts.display, fontSize: 64 }}>
              {String(n).padStart(2, "0")}
            </div>
            <div style={{ flex: 1, padding: "0 20px", color: C.colors.blockText, fontFamily: C.fonts.display, fontSize: 40, lineHeight: 1, textTransform: "uppercase" }}>
              {S.labels[n]}
            </div>
          </div>
        );
      })}
    </>
  );
};

// ---------- flash + grain ----------
const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const on = heroes.some((h) => frame - h.startF >= 0 && frame - h.startF < C.hero.flashFrames);
  return on ? <AbsoluteFill style={{ background: C.colors.flash, opacity: C.hero.flashOpacity }} /> : null;
};

const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  if (!C.grain) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 55% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)" }} />
      <svg width="100%" height="100%" style={{ opacity: C.grain, mixBlendMode: "overlay" }}>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={frame % 8} /></filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

export const Duppy: React.FC = () => {
  const frame = useCurrentFrame();
  const ready = useFonts();
  const current = timedGroups.filter((g) => frame >= g.startF && frame < g.endF);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Footage />
      <Grain />
      <Steps />
      {current.map((g) => (g.role === "hero" ? <Hero key={g.index} g={g} ready={ready} /> : <Caption key={g.index} g={g} />))}
      <Flash />
    </AbsoluteFill>
  );
};
