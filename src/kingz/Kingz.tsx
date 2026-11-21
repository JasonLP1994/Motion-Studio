import React from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { kingzConfig as K, P } from "./config";
import TRACK from "./track.json";

loadFont({ family: "PermanentMarker", url: staticFile("fonts/graffiti/PermanentMarker.woff2") });
loadFont({ family: "RubikWetPaint", url: staticFile("fonts/graffiti/RubikWetPaint.woff2") });
loadFont({ family: "Anton", url: staticFile("fonts/anton-latin-400-normal.woff2") });
loadFont({ family: "Inter", url: staticFile("fonts/inter-latin-800-normal.woff2"), weight: "800" });
loadFont({ family: "LiberationMono", url: staticFile("fonts/LiberationMono-Bold.ttf") });

const W = K.output.width;
const H = K.output.height;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};
const pad = (n: number) => String(n).padStart(5, "0");
type XY = [number, number];
const T = TRACK as unknown as { head: (XY | null)[]; hands: (XY | null)[]; robeL: (XY | null)[]; robeR: (XY | null)[]; bbox: ([number, number, number, number] | null)[]; face: ([number, number, number, number] | null)[] };

// Hand-drawn wobble: displacement whose noise re-seeds every few frames ("boil").
const Wobble: React.FC<{ f: number }> = ({ f }) => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="wob" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={2} seed={Math.floor(f / K.outline.boilEvery)} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={K.outline.wobble} />
    </filter>
    <filter id="toWhite"><feColorMatrix type="matrix" values="0 0 0 0 0.96  0 0 0 0 0.96  0 0 0 0 0.95  0 0 0 1 0" /></filter>
  </svg>
);

// ---------- type ----------
type WordT = { text: string; at: number; out: number; x: number; y: number; size: number; font: string; rot: number; behind?: boolean; outlineOnly?: boolean };
const Word: React.FC<{ w: WordT; f: number }> = ({ w, f }) => {
  const t = f - w.at;
  if (t < 0 || f >= w.out || (f >= w.out - 2 && f % 2 === 0)) return null;
  const s = interpolate(t, [0, K.slamFrames], [1.45, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const base: React.CSSProperties = {
    position: "absolute", left: w.x, top: w.y, transform: `translate(-50%, -50%) rotate(${w.rot}deg) scale(${s})`,
    fontFamily: w.font, fontSize: w.size, lineHeight: 1, whiteSpace: "nowrap", letterSpacing: "0.01em",
  };
  if (w.outlineOnly) return <div style={{ ...base, color: "transparent", WebkitTextStroke: `${K.ghost.stroke + 2}px ${P.yellow}` }}>{w.text}</div>;
  return (
    <>
      <div style={{ ...base, left: w.x + K.ghost.dx, top: w.y + K.ghost.dy, color: "transparent", WebkitTextStroke: `${K.ghost.stroke}px ${P.yellow}` }}>{w.text}</div>
      <div style={{ ...base, color: P.yellow }}>{w.text}</div>
    </>
  );
};

const Tape: React.FC<{ b: (typeof K.tape.bands)[number]; f: number }> = ({ b, f }) => {
  const t = f - b.at;
  if (t < 0 || f >= b.out) return null;
  const inP = interpolate(t, [0, K.tape.wipe], [0, 100], clamp);
  const outP = interpolate(f, [b.out - K.tape.wipe, b.out], [0, 100], clamp);
  const text = K.tape.text.repeat(8);
  const shift = ((t * b.speed) % 900) - 900;
  return (
    <div style={{ position: "absolute", left: -200, width: W + 400, top: b.y, height: K.tape.height, transform: `rotate(${b.rot}deg)`, background: P.yellow, overflow: "hidden", clipPath: `inset(0 ${100 - inP}% 0 ${outP}%)`, boxShadow: "0 6px 18px rgba(0,0,0,0.5)" }}>
      <div style={{ position: "absolute", left: shift, top: (K.tape.height - K.tape.fontSize * 1.15) / 2, whiteSpace: "nowrap", fontFamily: "Anton", fontSize: K.tape.fontSize, lineHeight: 1.15, color: P.black, letterSpacing: "0.02em" }}>{text}</div>
    </div>
  );
};

// ---------- poster furniture ----------
const Barcode: React.FC<{ x: number; y: number; w: number; h: number; seed: number; vertical?: boolean }> = ({ x, y, w, h, seed, vertical }) => {
  const bars = [];
  let p = 0;
  const len = vertical ? h : w;
  for (let i = 0; p < len; i++) {
    const thick = 3 + Math.floor(rnd(seed + i) * 4) * 4;
    const gap = 4 + Math.floor(rnd(seed + i + 50) * 3) * 4;
    if (p + thick > len) break;
    bars.push(vertical ? <rect key={i} x={x} y={y + p} width={w} height={thick} fill={P.white} /> : <rect key={i} x={x + p} y={y} width={thick} height={h} fill={P.white} />);
    p += thick + gap;
  }
  return <>{bars}</>;
};

const Poster: React.FC<{ f: number }> = ({ f }) => {
  const Q = K.poster;
  const slide = interpolate(f, [Q.barcodesAt, Q.barcodesAt + 8], [1, 0], { ...clamp, easing: Easing.out(Easing.exp) });
  const chev = f >= Q.chevronsAt ? "<<<<" : "";
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <g transform={`translate(${-160 * slide} 0)`}><Barcode x={70} y={120} w={44} h={360} seed={3} vertical /><Barcode x={70} y={620} w={44} h={300} seed={9} vertical /></g>
      <g transform={`translate(${160 * slide} 0)`}><Barcode x={W - 114} y={160} w={44} h={420} seed={17} vertical /></g>
      {f >= Q.chevronsAt && (
        <>
          <text x={150} y={92} fill={P.white} fontFamily="Inter" fontWeight={800} fontSize={54} letterSpacing="-0.05em">{chev}</text>
          <text x={W - 330} y={H - 60} fill={P.white} fontFamily="Inter" fontWeight={800} fontSize={54} letterSpacing="-0.05em">{">>>>"}</text>
        </>
      )}
      {Q.xAt.map((a, i) => (f >= a ? (
        <text key={i} x={W - 250} y={300 + i * 150} fill={P.yellow} fontFamily="Inter" fontWeight={800} fontSize={170} textAnchor="middle">×</text>
      ) : null))}
      <Barcode x={150} y={H - 120} w={300} h={44} seed={31} />
      {Q.code.map((c, i) => (
        <text key={i} x={150} y={H - 160 - (Q.code.length - 1 - i) * 22} fill={P.white} fontFamily="LiberationMono" fontSize={16} letterSpacing="0.08em">{c}</text>
      ))}
    </svg>
  );
};

// ---------- matte-driven layers ----------
const Outline: React.FC<{ f: number }> = ({ f }) => {
  const O = K.outline;
  const reveal = interpolate(f, [0, O.drawFrames], [0, 100], clamp);
  const style: React.CSSProperties = { position: "absolute", left: 0, top: 0, width: W, height: H, clipPath: `inset(${100 - reveal}% 0 0 0)` };
  return (
    <>
      <Img src={staticFile(`statue/ring/${pad(f)}.png`)} style={{ ...style, left: O.shadow[0], top: O.shadow[1], filter: "url(#toWhite) url(#wob)", opacity: 0.9 }} />
      <Img src={staticFile(`statue/ring/${pad(f)}.png`)} style={{ ...style, filter: "url(#wob)" }} />
    </>
  );
};

const Nodes: React.FC<{ f: number }> = ({ f }) => {
  const N = K.nodes;
  if (f < N.at || f >= N.out) return null;
  const t = f - N.at;
  const bb = T.bbox[f];
  const pts = [T.head[f], T.hands[f], T.robeL[f], T.robeR[f], bb ? ([bb[2], (bb[1] + bb[3]) / 2] as XY) : null];
  const live = pts.map((p, i) => (p && t >= i * N.every && !(t === i * N.every + 1) ? p : null));
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {live.slice(0, -1).map((p, i) => {
        const q = live[i + 1];
        if (!p || !q) return null;
        const draw = interpolate(t, [(i + 1) * N.every, (i + 1) * N.every + N.wireFrames], [0, 1], clamp);
        const mx = (p[0] + q[0]) / 2 + (i % 2 ? -160 : 160);
        return <path key={i} d={`M${p[0]} ${p[1]} Q${mx} ${(p[1] + q[1]) / 2} ${q[0]} ${q[1]}`} fill="none" stroke={P.white} strokeWidth={2.5} pathLength={1} strokeDasharray={`${draw} 1`} />;
      })}
      {live.map((p, i) => (p ? (
        <g key={`n${i}`}>
          <rect x={p[0] - 8} y={p[1] - 8} width={16} height={16} fill={P.white} />
          <rect x={p[0] + 18} y={p[1] - 22} width={140} height={40} fill={P.yellow} />
          <text x={p[0] + 30} y={p[1] + 7} fill={P.black} fontFamily="Inter" fontWeight={800} fontSize={22}>{N.labels[i].slice(0, Math.max(0, Math.floor((t - i * N.every) * 2.5)))}</text>
        </g>
      ) : null))}
    </svg>
  );
};

// Crown, X eyes and smile doodle drawn onto her face in the close-up (follows the tracked face box).
const FaceMarks: React.FC<{ f: number }> = ({ f }) => {
  const F = K.face;
  const box = T.face[f];
  if (f < F.at || !box) return null;
  const [x0, y0, x1, y1] = box;
  const w = x1 - x0, h = y1 - y0;
  const X = (u: number) => x0 + u * w, Y = (v: number) => y0 + v * h;
  const sw = Math.max(6, w * F.stroke);
  const d = (i: number) => interpolate(f, [F.at + i * F.every, F.at + i * F.every + F.drawFrames], [0, 1], clamp);
  const st = (i: number) => ({ fill: "none", stroke: P.yellow, strokeWidth: sw, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, pathLength: 1, strokeDasharray: `${d(i)} 1` });
  const ex = (cx: number, cy: number, r: number) => `M${X(cx) - r} ${Y(cy) - r} L${X(cx) + r} ${Y(cy) + r} M${X(cx) + r} ${Y(cy) - r} L${X(cx) - r} ${Y(cy) + r}`;
  const r = w * 0.09;
  const crown = `M${X(0.2)} ${Y(-0.08)} L${X(0.2)} ${Y(-0.32)} L${X(0.35)} ${Y(-0.18)} L${X(0.5)} ${Y(-0.38)} L${X(0.65)} ${Y(-0.18)} L${X(0.8)} ${Y(-0.32)} L${X(0.8)} ${Y(-0.08)} Z`;
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0, filter: "url(#wob)" }}>
      <path d={crown} {...st(0)} />
      {d(0) >= 1 && [0.2, 0.5, 0.8].map((u, i) => <circle key={i} cx={X(u)} cy={Y(i === 1 ? -0.38 : -0.32) - sw} r={sw * 0.9} fill={P.yellow} />)}
      <path d={ex(0.33, 0.42, r)} {...st(1)} />
      <path d={ex(0.67, 0.42, r)} {...st(2)} />
      <path d={`M${X(0.28)} ${Y(0.7)} Q${X(0.5)} ${Y(0.9)} ${X(0.74)} ${Y(0.66)} M${X(0.66)} ${Y(0.64)} L${X(0.75)} ${Y(0.65)} L${X(0.73)} ${Y(0.75)}`} {...st(3)} />
    </svg>
  );
};

// Faint film grain.
const Grain: React.FC<{ f: number }> = ({ f }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.12, mixBlendMode: "overlay", pointerEvents: "none" }}>
    <filter id="gr" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" seed={f % 7} /></filter>
    <rect width={W} height={H} filter="url(#gr)" />
  </svg>
);

export const Kingz: React.FC = () => {
  const f = useCurrentFrame();
  const S = K.shake;
  const lastSlam = Math.max(...K.words.map((w) => (f >= w.at ? w.at : -99)));
  const shaking = f - lastSlam < S.frames;
  const sx = shaking ? (rnd(f * 1.7) - 0.5) * 2 * S.px : 0;
  const sy = shaking ? (rnd(f * 2.9) - 0.5) * 2 * S.px : 0;
  return (
    <AbsoluteFill style={{ background: P.black }}>
      <Wobble f={f} />
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px)` }}>
        <OffthreadVideo src={staticFile("statue/clip.mp4")} style={{ width: W, height: H, filter: K.grade }} muted />
        {(K.words as WordT[]).filter((w) => w.behind).map((w, i) => <Word key={`b${i}`} w={w} f={f} />)}
        <Img src={staticFile(`statue/cut/${pad(f)}.webp`)} style={{ position: "absolute", left: 0, top: 0, width: W, height: H, filter: K.grade }} />
        <Outline f={f} />
        <FaceMarks f={f} />
        <Nodes f={f} />
        {K.tape.bands.map((b, i) => <Tape key={i} b={b} f={f} />)}
        {(K.words as WordT[]).filter((w) => !w.behind).map((w, i) => <Word key={`f${i}`} w={w} f={f} />)}
        <Poster f={f} />
      </AbsoluteFill>
      <Grain f={f} />
      <Audio src={staticFile(K.audio.music)} volume={K.audio.volume} />
    </AbsoluteFill>
  );
};
