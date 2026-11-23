import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing, random } from "remotion";
import { pd01Config as C } from "./config";

// POV visor HUD: we're inside the helmet. Shadowed visor edges, curved scales, reticle, gauges, boot text.
// Boots on (flicker) at V.on, holds, and at V.off zooms past the camera and fades (pulling out of the helmet on the reveal).
const V = C.visor;
const col = C.colors;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const W = 1920, H = 1080, cx = 960, cy = 520;

const arcPath = (r: number, a0: number, a1: number) => {
  const p = (a: number) => `${cx + r * Math.cos(a)} ${cy + r * Math.sin(a)}`;
  return `M ${p(a0)} A ${r} ${r} 0 0 1 ${p(a1)}`;
};
const ticks = (r: number, a0: number, a1: number, n: number, len: number, every = 5) =>
  Array.from({ length: n + 1 }).map((_, i) => {
    const a = a0 + ((a1 - a0) * i) / n; const L = i % every === 0 ? len * 1.8 : len;
    return <line key={i} x1={cx + r * Math.cos(a)} y1={cy + r * Math.sin(a)} x2={cx + (r - L) * Math.cos(a)} y2={cy + (r - L) * Math.sin(a)} />;
  });

export const VisorHUD: React.FC = () => {
  const f = useCurrentFrame(); const t = f / C.fps;
  if (t < V.on || t > V.off + 0.6) return null;
  const k = t - V.on;
  // boot flicker, then steady
  const flick = k < 0.5 ? (random(`vf${f}`) > 0.45 ? 1 : 0.15) : 1;
  const boot = interpolate(k, [0, 0.9], [0, 1], { extrapolateRight: "clamp", easing: ease });
  const exit = interpolate(t, [V.off, V.off + 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  const scale = 1 + exit * 1.6; const alpha = flick * (1 - exit);
  const spin = (t * 18) % 360; const heading = 212 + Math.sin(t * 0.8) * 6;
  const lines = V.boot; const chars = Math.floor(interpolate(k, [0.3, 2.2], [0, lines.join("").length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  let left = chars;
  const typed = lines.map((ln) => { const s = ln.slice(0, Math.max(0, Math.min(ln.length, left))); left -= ln.length; return s; });
  const pink = col.pink, ink = "rgba(244,246,255,0.9)";
  return (
    <AbsoluteFill style={{ opacity: alpha, transform: `scale(${scale})`, transformOrigin: `${cx}px ${cy}px` }}>
      {/* shadowed visor edges: dark helmet interior with a soft visor-shaped opening */}
      <svg width={W} height={H} style={{ position: "absolute" }}>
        <defs>
          <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="90" /></filter>
          <mask id="opening">
            <rect width={W} height={H} fill="white" />
            <path filter="url(#soft)" fill="black" d={`M ${cx - 820} ${cy - 120} C ${cx - 700} ${cy - 420}, ${cx + 700} ${cy - 420}, ${cx + 820} ${cy - 120}
              L ${cx + 700} ${cy + 330} C ${cx + 420} ${cy + 470}, ${cx - 420} ${cy + 470}, ${cx - 700} ${cy + 330} Z`} />
          </mask>
          <radialGradient id="tint" cx="50%" cy="48%" r="60%"><stop offset="45%" stopColor="rgba(4,4,12,0)" /><stop offset="100%" stopColor="rgba(4,2,10,0.85)" /></radialGradient>
        </defs>
        <rect width={W} height={H} fill="url(#tint)" />
        <rect width={W} height={H} fill="rgba(2,2,8,0.94)" mask="url(#opening)" />
        {/* glass edge highlight */}
        <path d={`M ${cx - 760} ${cy - 150} C ${cx - 700} ${cy - 430}, ${cx + 700} ${cy - 430}, ${cx + 760} ${cy - 150}`} stroke="rgba(255,26,140,0.35)" strokeWidth={3} fill="none" filter="blur(2px)" />
      </svg>
      {/* scanlines */}
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 4px)", mixBlendMode: "screen" }} />
      <svg width={W} height={H} style={{ position: "absolute", clipPath: `circle(${boot * 75}% at ${cx}px ${cy}px)` }} stroke={ink} fill="none" strokeWidth={2}>
        {/* curved top scale + heading */}
        <path d={arcPath(450, -Math.PI * 0.72, -Math.PI * 0.28)} strokeWidth={2} />
        <g stroke={ink} strokeWidth={2}>{ticks(450, -Math.PI * 0.72, -Math.PI * 0.28, 40, 10)}</g>
        <polygon points={`${cx - 10},${cy - 475} ${cx + 10},${cy - 475} ${cx},${cy - 458}`} fill={pink} stroke="none" />
        <text x={cx} y={cy - 490} fill={pink} stroke="none" fontFamily="PDUI" fontSize={26} textAnchor="middle" letterSpacing="3">{`HDG ${heading.toFixed(0).padStart(3, "0")}`}</text>
        {/* bottom arc */}
        <path d={arcPath(470, Math.PI * 0.25, Math.PI * 0.75)} stroke="rgba(244,246,255,0.5)" />
        <g stroke="rgba(244,246,255,0.5)">{ticks(470, Math.PI * 0.25, Math.PI * 0.75, 24, 8, 4)}</g>
        {/* reticle */}
        <g transform={`rotate(${spin} ${cx} ${cy})`} stroke={pink} strokeWidth={3}>
          <path d={arcPath(120, -0.4, 0.4)} /><path d={arcPath(120, Math.PI - 0.4, Math.PI + 0.4)} />
          <path d={arcPath(120, Math.PI / 2 - 0.25, Math.PI / 2 + 0.25)} /><path d={arcPath(120, -Math.PI / 2 - 0.25, -Math.PI / 2 + 0.25)} />
        </g>
        <circle cx={cx} cy={cy} r={70} stroke="rgba(244,246,255,0.55)" strokeDasharray="4 10" />
        <line x1={cx - 40} y1={cy} x2={cx - 14} y2={cy} /><line x1={cx + 14} y1={cy} x2={cx + 40} y2={cy} />
        <line x1={cx} y1={cy - 40} x2={cx} y2={cy - 14} /><line x1={cx} y1={cy + 14} x2={cx} y2={cy + 40} />
        <circle cx={cx} cy={cy} r={4} fill={pink} stroke="none" />
        {/* left power gauge */}
        <g transform={`translate(${cx - 640} ${cy - 160})`}>
          <rect width={22} height={320} stroke="rgba(244,246,255,0.6)" />
          <rect x={4} y={320 - 312 * boot * 0.87} width={14} height={312 * boot * 0.87} fill={pink} stroke="none" />
          {Array.from({ length: 9 }).map((_, i) => <line key={i} x1={30} y1={i * 40} x2={44} y2={i * 40} stroke="rgba(244,246,255,0.6)" />)}
          <text x={56} y={14} fill={ink} stroke="none" fontFamily="PDUIMed" fontSize={20} letterSpacing="3">PWR</text>
          <text x={56} y={44} fill={pink} stroke="none" fontFamily="PDUI" fontSize={34}>{`${Math.round(boot * 87)}%`}</text>
        </g>
        {/* right ladder */}
        <g transform={`translate(${cx + 600} ${cy - 160})`} stroke="rgba(244,246,255,0.6)">
          {Array.from({ length: 11 }).map((_, i) => <line key={i} x1={0} y1={i * 32} x2={i % 5 === 0 ? 34 : 18} y2={i * 32} />)}
          <text x={-14} y={168} fill={ink} stroke="none" fontFamily="PDUIMed" fontSize={20} textAnchor="end" letterSpacing="3">SYNC</text>
          <text x={-14} y={198} fill={pink} stroke="none" fontFamily="PDUI" fontSize={30} textAnchor="end">{(24 + Math.floor(t * 3) % 7).toString().padStart(3, "0")}</text>
        </g>
      </svg>
      {/* boot text, bottom left inside the visor; Japanese tag bottom right */}
      <div style={{ position: "absolute", left: cx - 560, top: cy + 210, fontFamily: "PDUIMed", fontSize: 22, letterSpacing: "0.12em", color: ink, lineHeight: 1.5, whiteSpace: "pre" }}>
        {typed.map((s, i) => <div key={i} style={{ color: i === typed.length - 1 ? pink : ink }}>{s}{i === typed.findIndex((x, j) => x.length < lines[j].length) ? "█" : ""}</div>)}
      </div>
      <div style={{ position: "absolute", right: W - (cx + 560), top: cy + 250, fontFamily: "PDJP", fontSize: 26, color: pink, letterSpacing: "0.06em", opacity: boot }}>{V.jp}</div>
    </AbsoluteFill>
  );
};
