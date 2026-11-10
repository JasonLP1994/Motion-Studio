// Material loop: grammar learned from ManvsMachine, rebuilt in 2D code.
// One abstract form driven by a single algorithm (every rod follows the same rule with a phase offset),
// tactile shading and soft studio light on a bold flat colour field, motion accents locked to a beat,
// a seamless loop, and one clean word revealed with a mask.
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const materialConfig = {
  word: "MOVE", // one short word; "" for none
  durationInSeconds: 6, // the loop length: motion repeats exactly
  bpm: 120, // accents land on every beat
  rods: 56,
  twists: 3, // how many waves travel around the ring per loop
  palette: {
    field: "#FF5B2E", // bold flat background
    fieldLight: "#FF8A5C", // soft key light on the field
    rodLight: "#FFF4EA",
    rodMid: "#F2D7C6",
    rodDark: "#B0705A",
    shadow: "rgba(90,20,0,0.35)",
    text: "#1B0C06",
  },
};

const P = materialConfig.palette;

export const MaterialLoop: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const C = materialConfig;
  const loop = (frame % durationInFrames) / durationInFrames; // 0..1, seamless
  const beatFrames = (60 / C.bpm) * fps;
  const sinceBeat = frame % beatFrames;
  // Beat accent: a quick squash that eases back (anticipation is the previous beat's release).
  const accent = interpolate(sinceBeat, [0, 3, beatFrames * 0.8], [0, 1, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const cx = width / 2, cy = height / 2 + 10;
  const radius = 250 + accent * 10;

  const rods = Array.from({ length: C.rods }, (_, i) => {
    const a = (i / C.rods) * Math.PI * 2;
    const phase = loop * Math.PI * 2 * C.twists - a * C.twists; // same rule, offset per rod
    const len = 150 + 90 * Math.sin(phase) + accent * 18;
    const tilt = 32 * Math.cos(phase);
    const depth = (Math.sin(a + loop * Math.PI * 2) + 1) / 2; // fake 3D: rods "behind" are smaller and softer
    return { a, len, tilt, depth, i };
  }).sort((p, q) => p.depth - q.depth);

  const wordIn = interpolate(frame, [12, 30], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ background: P.field }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 38% 30%, ${P.fieldLight} 0%, transparent 60%)` }} />
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="tube" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor={P.rodDark} />
            <stop offset="0.35" stopColor={P.rodLight} />
            <stop offset="0.6" stopColor={P.rodMid} />
            <stop offset="1" stopColor={P.rodDark} />
          </linearGradient>
          <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="10" dy="16" stdDeviation="10" floodColor={P.shadow} />
          </filter>
        </defs>
        {rods.map((r) => {
          const x = cx + Math.cos(r.a) * radius * (0.9 + r.depth * 0.1);
          const y = cy + Math.sin(r.a) * radius * 0.55; // ring seen at an angle
          const w = 18 + r.depth * 10;
          const blur = (1 - r.depth) * 2.2; // shallow depth of field
          return (
            <g key={r.i} transform={`translate(${x} ${y}) rotate(${r.tilt})`} filter="url(#soft)" style={{ filter: blur > 0.4 ? `blur(${blur}px)` : undefined }} opacity={0.75 + r.depth * 0.25}>
              <rect x={-w / 2} y={-r.len} width={w} height={r.len} rx={w / 2} fill="url(#tube)" />
            </g>
          );
        })}
      </svg>
      {C.word ? (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 110, display: "flex", justifyContent: "center", overflow: "hidden", height: 120 }}>
          <div style={{ fontFamily: "Inter, Arial, sans-serif", fontWeight: 800, fontSize: 104, letterSpacing: "-0.04em", color: P.text, lineHeight: 1.1,
            transform: `translateY(${wordIn * 115}%)` }}>{C.word}</div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
