import React from "react";
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { kineticConfig as K, eighth, Panel } from "./config";

for (const w of [300, 500, 600, 700, 800, 900]) {
  loadFont({ family: "Inter", url: staticFile(`fonts/inter-latin-${w}-normal.woff2`), weight: String(w) });
}
loadFont({ family: "Montserrat", url: staticFile("fonts/montserrat-latin-500-normal.woff2"), weight: "500" });
loadFont({ family: "Montserrat", url: staticFile("fonts/montserrat-latin-900-italic.woff2"), weight: "900", style: "italic" });

const W = K.output.width;
const H = K.output.height;
const outExp = Easing.out(Easing.exp);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Deterministic pseudo-random in [0,1).
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};

// All scenes read the absolute frame (scene starts live in config), so none sit inside a Sequence.

// ---------- The strip (0-4 s) ----------

const GlyphPanel: React.FC<{ p: Extract<Panel, { kind: "glyph" }>; t: number }> = ({ p, t }) => {
  const push = 1 + K.glyphPush * interpolate(t, [0, 12], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  return (
    <AbsoluteFill style={{ background: p.bg, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: W / 2 + p.x,
          top: H / 2 + p.y,
          transform: `translate(-50%, -50%) scale(${push})`,
          fontFamily: K.glyphFont,
          fontWeight: p.weight ?? K.glyphWeight,
          fontSize: p.size,
          lineHeight: 1,
          letterSpacing: "-0.04em",
          color: p.ink,
        }}
      >
        {p.ch}
      </div>
    </AbsoluteFill>
  );
};

// Grid of the same glyph, every tile at its own random angle (the reference's 2 and 8 walls).
const WallPanel: React.FC<{ p: Extract<Panel, { kind: "wall" }>; t: number; seed: number }> = ({ p, t, seed }) => {
  const cols = Math.ceil(W / p.cell) + 2;
  const rows = Math.ceil(H / p.cell) + 2;
  const drift = t * 2.5;
  const tiles = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      const k = seed * 1000 + r * 50 + c;
      const ang = Math.floor(rnd(k) * 8) * 45 + (rnd(k + 7) - 0.5) * 30;
      tiles.push(
        <div
          key={`${r}-${c}`}
          style={{
            position: "absolute",
            left: (c - 1) * p.cell + (r % 2) * (p.cell * 0.45) - drift,
            top: (r - 1) * p.cell * 0.92,
            width: p.cell,
            height: p.cell,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: K.glyphFont,
            fontWeight: p.weight,
            fontSize: p.size,
            lineHeight: 1,
            color: p.ink,
            transform: `rotate(${ang + t * (rnd(k + 3) - 0.5) * 3}deg)`,
          }}
        >
          {p.ch}
        </div>,
      );
    }
  return <AbsoluteFill style={{ background: p.bg, overflow: "hidden" }}>{tiles}</AbsoluteFill>;
};

// A few big outlined glyphs tumbling (the reference's 4s).
const ScatterPanel: React.FC<{ p: Extract<Panel, { kind: "scatter" }>; t: number; seed: number }> = ({ p, t, seed }) => (
  <AbsoluteFill style={{ background: p.bg, overflow: "hidden" }}>
    {Array.from({ length: p.count }).map((_, i) => {
      const k = seed * 100 + i;
      const col = i % 5;
      const row = Math.floor(i / 5);
      const x = ((col + 0.5) / 5) * W + (rnd(k) - 0.5) * 160 + (row % 2) * 150;
      const y = (row === 0 ? 0.3 : 0.72) * H + (rnd(k + 1) - 0.5) * 140;
      const ang = rnd(k + 2) * 360 + t * (rnd(k + 4) > 0.5 ? 9 : -9);
      return (
        <div
          key={i}
          style={{
            position: "absolute",
            left: x,
            top: y,
            transform: `translate(-50%, -50%) rotate(${ang}deg) scale(${0.75 + rnd(k + 5) * 0.5})`,
            fontFamily: K.glyphFont,
            fontWeight: 300,
            fontSize: p.size,
            lineHeight: 1,
            color: "transparent",
            WebkitTextStroke: `${p.stroke}px ${p.ink}`,
          }}
        >
          {p.ch}
        </div>
      );
    })}
  </AbsoluteFill>
);

const Strip: React.FC<{ f: number }> = ({ f }) => {
  const n = K.panels.length;
  // Camera position in panels: whip into panel i around its beat.
  let cam = 0;
  for (let i = 1; i < n; i++) {
    const s = eighth(i);
    cam += interpolate(f, [s - K.whipFrames / 2, s + K.whipFrames / 2], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  }
  const lo = Math.max(0, Math.floor(cam));
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {[lo, lo + 1].filter((i) => i < n).map((i) => {
        const p = K.panels[i];
        const t = f - eighth(i);
        return (
          <AbsoluteFill key={i} style={{ transform: `translateX(${(i - cam) * W}px)` }}>
            {p.kind === "glyph" && <GlyphPanel p={p} t={t} />}
            {p.kind === "wall" && <WallPanel p={p} t={t} seed={i} />}
            {p.kind === "scatter" && <ScatterPanel p={p} t={t} seed={i} />}
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- The name (4-8 s) ----------

// "Phillips": letters pop in at random sizes and places in random order, then fly into one line.
const PhillipsScene: React.FC<{ f: number }> = ({ f }) => {
  const P = K.name.phillips;
  const t = f - P.start;
  const letters = P.text.split("");
  // First letter first (like the reference's M), the rest in random order.
  const order = [0, ...letters.map((_, i) => i).slice(1).sort((a, b) => rnd(a + 71) - rnd(b + 71))];
  const asm = interpolate(t, [P.assembleAt, P.assembleAt + P.assembleFrames], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const q = 1 - asm;
  return (
    <AbsoluteFill style={{ background: P.bg, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", fontFamily: P.font, fontWeight: P.weight, fontSize: P.size, lineHeight: 1, color: P.ink }}>
        {letters.map((ch, i) => {
          const appear = P.blackFrames + order.indexOf(i) * P.letterGap;
          const sx = (rnd(i * 3 + 5) * 2 - 1) * P.scatter.x;
          const sy = (rnd(i * 5 + 2) * 2 - 1) * P.scatter.y;
          const ss = P.scatter.sizeMin + rnd(i + 37) * (P.scatter.sizeMax - P.scatter.sizeMin);
          return (
            <span key={i} style={{ display: "inline-block", opacity: t >= appear ? 1 : 0, transform: `translate(${sx * q}px, ${sy * q}px) scale(${1 + (ss - 1) * q})` }}>
              {ch}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// "Digital": rows of the word, each row stepping through weights (the reference's Analogue stack).
const DigitalScene: React.FC<{ f: number }> = ({ f }) => {
  const D = K.name.digital;
  const step = Math.floor((f - D.start) / D.stepFrames);
  return (
    <AbsoluteFill style={{ background: D.bg, alignItems: "center", justifyContent: "center" }}>
      {Array.from({ length: D.rows }).map((_, r) => (
        <div key={r} style={{ fontFamily: D.font, fontWeight: D.weights[(r * 2 + step) % D.weights.length], fontSize: D.size, lineHeight: D.lineHeight, letterSpacing: "-0.02em", color: D.ink }}>
          {D.text}
        </div>
      ))}
    </AbsoluteFill>
  );
};

// "Project": heavy italic typed letter by letter, each letter snapping in (the reference's Razor).
const ProjectScene: React.FC<{ f: number }> = ({ f }) => {
  const R = K.name.project;
  const t = f - R.start;
  return (
    <AbsoluteFill style={{ background: R.bg, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", fontFamily: R.font, fontWeight: R.weight, fontStyle: "italic", fontSize: R.size, lineHeight: 1, color: R.ink }}>
        {R.text.split("").map((ch, i) => {
          const s = i * R.framesPerLetter;
          const p = interpolate(t, [s, s + R.letterEnter], [0, 1], { ...clamp, easing: outExp });
          return (
            <span key={i} style={{ display: "inline-block", opacity: t >= s ? 1 : 0, transform: `translateX(${(1 - p) * 60}px) scaleX(${1 + (1 - p) * 0.6})`, transformOrigin: "left center" }}>
              {ch}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Lockup: the three words, each in the style it was introduced in, pushed in from the right.
const Lockup: React.FC<{ f: number }> = ({ f }) => {
  const L = K.name.lockup;
  const t = f - L.start;
  return (
    <AbsoluteFill style={{ background: L.bg, alignItems: "center", justifyContent: "center" }}>
      {L.lines.map((ln, i) => {
        const s = i * L.lineStagger;
        const p = interpolate(t, [s, s + L.enterFrames], [0, 1], { ...clamp, easing: outExp });
        return (
          <div
            key={i}
            style={{
              fontFamily: ln.font,
              fontWeight: ln.weight,
              fontStyle: ln.italic ? "italic" : "normal",
              fontSize: ln.size,
              lineHeight: L.lineHeight,
              letterSpacing: "-0.03em",
              color: L.ink,
              transform: `translateX(${(1 - p) * L.enterFrom}px)`,
            }}
          >
            {ln.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Multiply shade: every frame darkens toward the bottom, like the reference.
const Shade: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `linear-gradient(180deg, #FFFFFF 0%, #FFFFFF ${K.shade.from * 100}%, ${K.shade.to} 100%)`,
      mixBlendMode: "multiply",
      pointerEvents: "none",
    }}
  />
);

const Scenes: React.FC = () => {
  const f = useCurrentFrame();
  const N = K.name;
  const stripEnd = eighth(K.panels.length);
  const inRange = (a: number, b: number) => f >= a && f < b;
  return (
    <AbsoluteFill>
      {f < stripEnd && <Strip f={f} />}
      {inRange(N.phillips.start, N.phillips.end) && <PhillipsScene f={f} />}
      {inRange(N.digital.start, N.digital.end) && <DigitalScene f={f} />}
      {inRange(N.project.start, N.project.end) && <ProjectScene f={f} />}
      {f >= N.lockup.start && <Lockup f={f} />}
      <Shade />
    </AbsoluteFill>
  );
};

export const KineticSymbols: React.FC = () => (
  <AbsoluteFill style={{ background: K.colors.black }}>
    <Scenes />
    <Audio src={staticFile(K.audio.beat)} volume={K.audio.beatVolume} />
    {K.audio.sfx.map((s, i) => (
      <Sequence key={i} from={s.frame}>
        <Audio src={staticFile(s.file)} volume={s.volume} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
