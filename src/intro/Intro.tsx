// Phillips English intro. One teal line carries the whole piece: it shoots out, underlines,
// swells into the wipe, drops under the next phrase, then becomes the bar of the logo.
// Everything is a pure function of the frame, so every render is identical.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import { loadFont } from "@remotion/fonts";
import { introConfig as C } from "./config";

const T = C.t;
const { white, teal } = C.colors;

// ---- motion helpers (spring step response and tracks) ----
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t: number, a: number, b: number) => clamp((t - a) / (b - a));
const easeIn = (x: number) => Math.pow(clamp(x), 3);
const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
function spring(t: number, w = 14, z = 0.82) {
  if (t <= 0) return 0;
  if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
}
// A value that springs to a new target at each key: [time, value, speed?, damping?]
const track = (v0: number, keys: [number, number, number?, number?][]) => (t: number) => {
  let v = v0, p = v0;
  for (const [tk, val, w, z] of keys) { v += (val - p) * spring(t - tk, w, z); p = val; }
  return v;
};

// ---- the line ----
const lineWidth = track(C.line.dotWidth, [
  [T.lineShoot, C.line.startWidth, 20, 0.9],
  [T.say - 0.04, C.phrase1.lineWidth, 16, 0.7],
  [T.blockUp, C.phrase2.blockWidth, 22, 0.9],
  [T.blockDown, C.phrase2.lineWidth, 18, 0.75],
  [T.every - 0.05, C.phrase3.lineWidth, 16, 0.75],
  [T.dayFill, C.phrase3.lineWidth + 90, 26, 0.5],
  [T.dayFill + 0.12, C.phrase3.lineWidth, 14, 0.8],
  [T.logoBar, C.logo.barWidth, 16, 0.72],
]);
const lineY = track(540, [
  [T.say - 0.04, C.phrase1.lineY, 16, 0.8],
  [T.every - 0.05, C.phrase3.lineY, 15, 0.8],
  [T.logoBar, C.logo.barY, 15, 0.8],
]);
const lineThick = track(C.line.thickness, [
  [T.blockUp, C.phrase2.blockHeight, 24, 0.92],
  [T.blockDown, C.line.thickness, 22, 0.95],
  [T.logoBar, C.logo.barThickness, 16, 0.75],
]);

const useFonts = () => {
  const [handle] = useState(() => delayRender("Loading fonts"));
  useEffect(() => {
    Promise.all([
      loadFont({ family: C.fonts.display, url: staticFile("fonts/montserrat-latin-900-normal.woff2"), weight: "900" }),
      loadFont({ family: C.fonts.logo, url: staticFile("fonts/inter-latin-800-normal.woff2"), weight: "800" }),
    ]).then(() => continueRender(handle));
  }, [handle]);
};

const display = (size: number): React.CSSProperties => ({ fontFamily: C.fonts.display, fontWeight: 900, fontSize: size, lineHeight: 1, letterSpacing: "-0.01em", whiteSpace: "nowrap" });

// A word that drops in with a fast blur and a small overshoot.
const DropWord: React.FC<{ t: number; at: number; color: string; children: string }> = ({ t, at, color, children }) => {
  const s = spring(t - at, 20, 0.62);
  const blur = (1 - seg(t, at, at + 0.14)) * 18;
  return (
    <span style={{ display: "inline-block", color, opacity: seg(t, at, at + 0.06), transform: `translateY(${(1 - s) * -90}px) scaleY(${1 + (1 - s) * 0.25})`,
      filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>{children}</span>
  );
};

// Phrase box: bottom edge sits on the line, and it clips, so words can sink behind the line.
const OnLine: React.FC<{ y: number; gap: number; children: React.ReactNode; height: number }> = ({ y, gap, children, height }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: y - gap - height, height, overflow: "hidden", display: "flex", justifyContent: "center", alignItems: "flex-end" }}>{children}</div>
);

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const W = C.output.width;

  const y = lineY(t), w = Math.max(0, lineWidth(t)), th = Math.max(2, lineThick(t));
  const dotPulse = t < T.lineShoot ? 1 + 0.6 * Math.sin((t / T.lineShoot) * Math.PI) : 1;

  // phrase 1: SAY IT (hidden once the block covers it)
  const p1 = t < T.blockSwap;
  // phrase 2: OUT LOUD, revealed as the block drops; sinks behind the line on exit
  const p2 = t >= T.blockSwap && t < T.every;
  const p2Sink = easeIn(seg(t, T.phrase2Out, T.every)) * 110;
  // phrase 3: EVERY DAY.
  const p3 = t >= T.every && t < T.logoBar + 0.1;
  const p3Sink = easeIn(seg(t, T.phrase3Out, T.logoBar + 0.05)) * 110;
  const outlineDraw = easeInOut(seg(t, T.dayOutline, T.dayFill));
  const filled = t >= T.dayFill;
  const punch = filled ? 1 + 0.07 * (1 - spring(t - T.dayFill, 22, 0.55)) : 1;
  const echo = seg(t, T.dayFill, T.dayFill + 0.45);
  // logo
  const logoOn = t >= T.logoBar;
  const rise = (at: number) => (1 - spring(t - at, 17, 0.78)) * 105; // % translate inside a clip box
  const L = C.logo;
  const sheen = seg(t, T.sheen, T.sheen + 0.5);

  const dayText: React.CSSProperties = { ...display(C.phrase3.bigSize), letterSpacing: "-0.02em" };
  return (
    <AbsoluteFill>
      {p1 ? (
        <OnLine y={C.phrase1.lineY} gap={C.line.gap} height={300}>
          <div style={{ ...display(C.phrase1.size), display: "flex", gap: "0.2em" }}>
            <DropWord t={t} at={T.say} color={white}>{C.phrase1.white}</DropWord>
            <DropWord t={t} at={T.it} color={teal}>{C.phrase1.teal}</DropWord>
          </div>
        </OnLine>
      ) : null}
      {p2 ? (
        <OnLine y={C.phrase2.lineY} gap={C.line.gap} height={300}>
          <div style={{ ...display(C.phrase2.size), display: "flex", gap: "0.2em", transform: `translateY(${p2Sink}%)` }}>
            <span style={{ color: white }}>{C.phrase2.white}</span>
            <span style={{ color: teal }}>{C.phrase2.teal}</span>
          </div>
        </OnLine>
      ) : null}
      {p3 ? (
        <OnLine y={C.phrase3.lineY} gap={C.line.gap} height={520}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `translateY(${p3Sink}%)` }}>
            <div style={{ ...display(C.phrase3.smallSize), color: teal, letterSpacing: "0.42em", marginRight: "-0.42em", marginBottom: 14, display: "flex" }}>
              {C.phrase3.small.split("").map((ch, i) => {
                const a = T.every + i * 0.04;
                return <span key={i} style={{ opacity: seg(t, a, a + 0.08), transform: `translateY(${(1 - spring(t - a, 20, 0.7)) * 26}px)`, display: "inline-block" }}>{ch}</span>;
              })}
            </div>
            <div style={{ position: "relative", transform: `scale(${punch})`, transformOrigin: "50% 100%" }}>
              {/* outline that draws itself, then an echo that expands away on the hit */}
              <div style={{ ...dayText, color: C.colors.bgCentre, WebkitTextStroke: `6px ${white}`, paintOrder: "stroke fill", opacity: filled || t < T.dayOutline ? 0 : 1,
                WebkitMaskImage: `linear-gradient(90deg, black ${outlineDraw * 106 - 6}%, transparent ${outlineDraw * 106}%)`,
                maskImage: `linear-gradient(90deg, black ${outlineDraw * 106 - 6}%, transparent ${outlineDraw * 106}%)` }}>{C.phrase3.big}</div>
              {filled && echo < 1 ? (
                <div style={{ ...dayText, position: "absolute", left: 0, top: 0, color: "transparent", WebkitTextStroke: `2px ${teal}`, opacity: (1 - echo) * 0.8,
                  transform: `scale(${1 + echo * 0.16})`, transformOrigin: "50% 60%" }}>{C.phrase3.big}</div>
              ) : null}
              {filled ? <div style={{ ...dayText, position: "absolute", left: 0, top: 0, color: white }}>{C.phrase3.big}</div> : null}
            </div>
          </div>
        </OnLine>
      ) : null}

      {logoOn ? (
        <>
          {/* monogram rises from behind the bar */}
          <div style={{ position: "absolute", left: 0, right: 0, top: L.monoBottom - 420, height: 420 + 34, overflow: "hidden", display: "flex", justifyContent: "center", alignItems: "flex-start" }}>
            <div style={{ fontFamily: C.fonts.logo, fontWeight: 800, fontSize: L.monoSize, lineHeight: "420px", height: 420, letterSpacing: "-0.035em", display: "flex", marginTop: 28 }}>
              <span style={{ color: white, display: "inline-block", transform: `translateY(${rise(T.p)}%)` }}>{L.p}</span>
              <span style={{ color: teal, display: "inline-block", transform: `translateY(${rise(T.e)}%)` }}>{L.e}</span>
            </div>
          </div>
          {/* name drops out from under the bar */}
          {[{ s: L.line1, at: T.name1 }, { s: L.line2, at: T.name2 }].map((n, i) => (
            <div key={i} style={{ position: "absolute", left: 0, right: 0, top: L.nameTop + i * L.nameLineHeight, height: L.nameLineHeight, overflow: "hidden", display: "flex", justifyContent: "center" }}>
              <div style={{ fontFamily: C.fonts.logo, fontWeight: 800, fontSize: L.nameSize, lineHeight: `${L.nameLineHeight}px`, color: white, letterSpacing: "0.005em",
                transform: `translateY(${-rise(n.at)}%)` }}>{n.s}</div>
            </div>
          ))}
        </>
      ) : null}

      {/* the line (always on top; it is also the wipe block and the logo bar) */}
      <div style={{ position: "absolute", left: W / 2 - (w * dotPulse) / 2, top: y - th + (t < T.say ? th / 2 : 0), width: w * dotPulse, height: th * (t < T.lineShoot ? 2 : 1),
        background: teal, borderRadius: t < T.lineShoot ? 6 : 0, overflow: "hidden" }}>
        {sheen > 0 && sheen < 1 ? (
          <div style={{ position: "absolute", top: 0, bottom: 0, width: 90, left: `${-40 + sheen * 140}%`, background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent)", transform: "skewX(-20deg)" }} />
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const Intro: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: C.colors.bgEdge }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 75% 70% at 50% 50%, ${C.colors.bgCentre} 0%, ${C.colors.bgEdge} 100%)` }} />
      <CameraMotionBlur shutterAngle={C.motionBlur.shutterAngle} samples={C.motionBlur.samples}>
        <Scene />
      </CameraMotionBlur>
      <Audio src={staticFile(C.music)} />
    </AbsoluteFill>
  );
};
