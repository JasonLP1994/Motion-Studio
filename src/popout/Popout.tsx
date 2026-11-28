// POP OUT lyric video. Words, colours, timings: ./config.ts. Assets: public/popout (scripts/popout/prep.py).
import React from "react";
import { AbsoluteFill, Audio, Easing, Img, interpolate, staticFile, useCurrentFrame, random } from "remotion";
import { loadFont } from "@remotion/fonts";
import { fitText } from "@remotion/layout-utils";
import { C, FPS, f, lines, popoutConfig as K, Line } from "./config";

loadFont({ family: "Anton", url: staticFile("fonts/anton-latin-400-normal.woff2") });
loadFont({ family: "Montserrat", url: staticFile("fonts/montserrat-latin-900-normal.woff2"), weight: "900" });
loadFont({ family: "SpecialElite", url: staticFile("fonts/SpecialElite-Regular.ttf") });

const W = K.width, H = K.height;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outExp = Easing.out(Easing.exp), io = Easing.inOut(Easing.quad), inC = Easing.in(Easing.cubic);
const CHROME = "linear-gradient(180deg,#FFFFFF 0%,#E6ECF3 30%,#8D99AB 49%,#F7FAFD 53%,#AEB8C6 72%,#5F6B7D 100%)";
const ICE = "linear-gradient(180deg,#F4FAFF 0%,#BFDDF8 40%,#6F9FD3 55%,#D8ECFF 75%,#8DB6E3 100%)";
const fill = (c: keyof typeof C) => (c === "silver" ? CHROME : c === "ice" ? ICE : C[c]);

// ---------- shared pieces
const Dust: React.FC<{ o?: number }> = ({ o = 0.55 }) => {
  const fr = useCurrentFrame(); const s = Math.floor(fr / 2);           // re-roll the dust every 2 frames (film feel)
  return (<AbsoluteFill style={{ pointerEvents: "none" }}>
    <Img src={staticFile("popout/dust.png")} style={{ position: "absolute", width: W * 1.2, height: H * 1.2, left: -random(`dx${s}`) * W * 0.2, top: -random(`dy${s}`) * H * 0.2, opacity: o, transform: `scale(${random(`fl${s}`) > 0.5 ? -1 : 1},1)` }} />
    <Img src={staticFile("popout/paper.png")} style={{ position: "absolute", inset: 0, width: W, height: H, mixBlendMode: "overlay", opacity: 0.5 }} />
  </AbsoluteFill>);
};
const Halo: React.FC<{ x: number; y: number; r: number; o?: number }> = ({ x, y, r, o = 1 }) => (
  <div style={{ position: "absolute", left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: "50%", opacity: o,
    background: `radial-gradient(circle, transparent 58%, rgba(169,203,238,0.10) 66%, rgba(220,236,255,0.38) 70.5%, rgba(169,203,238,0.10) 75%, transparent 82%)`, filter: "blur(2px)" }} />
);
const Detail: React.FC<{ x: number; y: number; t: string; a?: "left" | "right"; c?: string; size?: number }> = ({ x, y, t, a = "left", c = C.silver, size = K.sizes.detail }) => (
  <div style={{ position: "absolute", top: y, [a]: x, fontFamily: "SpecialElite", fontSize: size, color: c, opacity: 0.75, letterSpacing: 1, whiteSpace: "pre", textAlign: a } as React.CSSProperties}>{t}</div>
);
// big type that builds one letter every K.letterEvery frames, with a blurred ghost sliding in behind (example grammar)
const Build: React.FC<{ text: string; at: number; size: number; x: number; y: number; color: keyof typeof C; w?: number; ghost?: boolean }> = ({ text, at, size, x, y, color, w, ghost = true }) => {
  const fr = useCurrentFrame(); const n = Math.max(0, Math.min(text.length, Math.floor((fr - at) / K.letterEvery) + 1));
  if (fr < at) return null;
  const fs = w ? Math.min(size, fitText({ text, withinWidth: w, fontFamily: "Anton" }).fontSize) : size;
  const gx = interpolate(fr - at, [0, text.length * K.letterEvery + 6], [K.ghost.dx * 4, K.ghost.dx], { ...clamp, easing: outExp });
  const style: React.CSSProperties = { position: "absolute", left: x, top: y, transform: "translate(-50%,-50%)", fontFamily: "Anton", fontSize: fs, lineHeight: 0.86, whiteSpace: "pre", letterSpacing: -fs * 0.01 };
  const paint = (c: keyof typeof C): React.CSSProperties => c === "silver" || c === "ice"
    ? { backgroundImage: fill(c), WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", filter: "drop-shadow(0 6px 0 rgba(4,7,14,0.55)) drop-shadow(0 0 24px rgba(169,203,238,0.35))" }
    : { color: C[c] };
  return (<>
    {ghost && <div style={{ ...style, left: x + gx, color: C.ice, opacity: K.ghost.opacity, filter: `blur(${K.ghost.blur}px)` }}>{text.slice(0, Math.min(text.length, n + 1))}</div>}
    <div style={{ ...style, ...paint(color) }}>{text.slice(0, n)}<span style={{ opacity: 0 }}>{text.slice(n)}</span></div>
  </>);
};
const Person: React.FC<{ n: number; side: "left" | "right"; s: number; e: number; h?: number }> = ({ n, side, s, e, h = 1010 }) => {
  const fr = useCurrentFrame();
  const enter = interpolate(fr, [s - K.transition, s + 3], [1, 0], { ...clamp, easing: outExp });
  const push = interpolate(fr, [s, e], [1, 1.05], clamp);
  const dir = side === "left" ? -1 : 1;
  return (<div style={{ position: "absolute", bottom: -10, [side]: side === "left" ? 40 : 30, height: h, transformOrigin: "50% 100%",
    transform: `translateX(${dir * enter * 420}px) scale(${push})`, filter: `blur(${enter * 14}px) drop-shadow(${-dir * 18}px 10px 0 rgba(4,7,14,0.6)) drop-shadow(0 0 30px rgba(169,203,238,0.18))` } as React.CSSProperties}>
    <Img src={staticFile(`popout/p${n}.png`)} style={{ height: "100%" }} />
  </div>);
};
// the sung line: words land as they are sung; the word being sung is ice blue
const Lyric: React.FC<{ L: Line; x: number; y: number; w: number; align: "left" | "right"; dark: boolean }> = ({ L, x, y, w, align, dark }) => {
  const fr = useCurrentFrame();
  return (<div style={{ position: "absolute", left: x, top: y, width: w, display: "flex", flexWrap: "wrap", justifyContent: align === "left" ? "flex-start" : "flex-end", gap: "6px 18px" }}>
    {L.words.map(([t, at], i) => {
      const a = f(at), nx = i + 1 < L.words.length ? f(L.words[i + 1][1]) : a + 12;
      const p = interpolate(fr, [a, a + K.wordPop], [0, 1], { ...clamp, easing: outExp });
      const live = fr >= a && fr < Math.max(nx, a + 6);
      return (<span key={i} style={{ fontFamily: "Montserrat", fontWeight: 900, fontSize: K.sizes.line, lineHeight: 1.04, letterSpacing: -1,
        color: live ? (dark ? C.blue : C.ice) : dark ? C.navy : C.white, opacity: p, display: "inline-block",
        transform: `translateY(${(1 - p) * 26}px) scale(${1 + (1 - p) * 0.25})`, textShadow: dark ? "none" : "0 4px 0 rgba(4,7,14,0.6)" }}>{t}</span>);
    })}
  </div>);
};

// ---------- lyric graphics (drawn in code, palette only)
const Sparkle: React.FC<{ x: number; y: number; s: number; o: number }> = ({ x, y, s, o }) => (
  <svg style={{ position: "absolute", left: x - s, top: y - s, opacity: o }} width={s * 2} height={s * 2} viewBox="-1 -1 2 2">
    <path d="M0,-1 C0.08,-0.08 0.08,-0.08 1,0 C0.08,0.08 0.08,0.08 0,1 C-0.08,0.08 -0.08,0.08 -1,0 C-0.08,-0.08 -0.08,-0.08 0,-1Z" fill={C.white} />
  </svg>);
const Diamond: React.FC<{ x: number; y: number; s: number; rot: number }> = ({ x, y, s, rot }) => (
  <svg style={{ position: "absolute", left: x - s, top: y - s * 0.8, transform: `rotate(${rot}deg)`, filter: "drop-shadow(0 0 30px rgba(169,203,238,0.55))" }} width={s * 2} height={s * 1.7} viewBox="0 0 200 170">
    <polygon points="40,10 160,10 200,55 100,170 0,55" fill="#BFDDF8" />
    <polygon points="40,10 70,55 0,55" fill="#E9F4FF" /><polygon points="160,10 130,55 200,55" fill="#7FAEE0" />
    <polygon points="40,10 160,10 130,55 70,55" fill="#F6FBFF" /><polygon points="70,55 130,55 100,170" fill="#9CC4EE" />
    <polygon points="0,55 70,55 100,170" fill="#6E9ED6" /><polygon points="130,55 200,55 100,170" fill="#4F7FBF" />
    <polyline points="40,10 100,55 160,10 M100,55 100,170" stroke="#FFFFFF" strokeOpacity={0.5} strokeWidth={1.5} fill="none" />
  </svg>);
const Chain: React.FC<{ y: number; prog: number; rot: number }> = ({ y, prog, rot }) => (
  <svg style={{ position: "absolute", left: -40, top: y, transform: `rotate(${rot}deg)`, transformOrigin: "0 0" }} width={W + 200} height={90}>
    <defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="0.5" stopColor="#7E8A9C" /><stop offset="1" stopColor="#E9EEF4" /></linearGradient></defs>
    {Array.from({ length: 28 }).map((_, i) => i / 28 <= prog && (i % 2 === 0
      ? <rect key={i} x={i * 74} y={18} width={96} height={52} rx={26} fill="none" stroke="url(#cg)" strokeWidth={14} />
      : <rect key={i} x={i * 74 + 10} y={36} width={76} height={16} rx={8} fill="url(#cg)" />))}
  </svg>);
const Band: React.FC<{ text: string; y: number; rot: number; fr: number; light?: boolean }> = ({ text, y, rot, fr, light }) => (
  <div style={{ position: "absolute", left: -200, top: y, width: W + 400, height: 70, background: light ? C.silver : C.night, transform: `rotate(${rot}deg)`, overflow: "hidden", borderTop: `3px solid ${C.ice}`, borderBottom: `3px solid ${C.ice}` }}>
    <div style={{ whiteSpace: "pre", fontFamily: "Anton", fontSize: 50, lineHeight: "70px", color: light ? C.navy : C.ice, transform: `translateX(${-(fr * 9) % 900}px)` }}>{(text + "   ✦   ").repeat(12)}</div>
  </div>);
const Heart: React.FC<{ x: number; y: number; s: number; split: number }> = ({ x, y, s, split }) => {
  const P = "M100,170 C40,120 0,90 0,50 C0,20 25,0 52,0 C75,0 92,14 100,32 C108,14 125,0 148,0 C175,0 200,20 200,50 C200,90 160,120 100,170Z";
  const half = (side: number) => (
    <svg key={side} style={{ position: "absolute", left: x - s + side * split * 40, top: y - s * 0.85 + split * 30, transform: `rotate(${side * split * 14}deg)`, filter: "drop-shadow(0 0 26px rgba(169,203,238,0.5))" }} width={s * 2} height={s * 1.7} viewBox="0 0 200 170">
      <defs><linearGradient id={`hg${side}`} x1="0" y1="0" x2="0.4" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="0.45" stopColor="#8995A8" /><stop offset="0.55" stopColor="#F2F6FA" /><stop offset="1" stopColor="#4E5A6C" /></linearGradient>
        <clipPath id={`hc${side}`}><polygon points={side < 0 ? "0,0 100,0 92,40 110,70 88,100 106,130 100,170 0,170" : "100,0 200,0 200,170 100,170 106,130 88,100 110,70 92,40"} /></clipPath></defs>
      <path d={P} fill={`url(#hg${side})`} clipPath={`url(#hc${side})`} />
    </svg>);
  return <>{half(-1)}{half(1)}</>;
};
const Crosshair: React.FC<{ x: number; y: number; r: number; o: number; spin: number }> = ({ x, y, r, o, spin }) => (
  <svg style={{ position: "absolute", left: x - r, top: y - r, opacity: o, transform: `rotate(${spin}deg)` }} width={r * 2} height={r * 2} viewBox="-100 -100 200 200">
    <circle r={92} fill="none" stroke={C.ice} strokeWidth={3} /><circle r={60} fill="none" stroke={C.ice} strokeWidth={2} strokeDasharray="8 8" /><circle r={6} fill={C.white} />
    {[0, 90, 180, 270].map((a) => <line key={a} x1={0} y1={-100} x2={0} y2={-70} stroke={C.white} strokeWidth={4} transform={`rotate(${a})`} />)}
  </svg>);
const Dove: React.FC<{ x: number; y: number; s: number; flap: number; o?: number }> = ({ x, y, s, flap, o = 1 }) => (
  <svg style={{ position: "absolute", left: x - s, top: y - s, opacity: o, filter: "blur(0.6px) drop-shadow(0 0 22px rgba(255,255,255,0.45))" }} width={s * 2} height={s * 2} viewBox="-100 -100 200 200">
    <g fill={C.white}>
      <path d={`M-10,10 C-40,${-30 - flap * 40} -80,${-50 - flap * 30} -96,${-70 - flap * 10} C-70,-20 -50,10 -20,22Z`} />
      <path d={`M5,8 C30,${-40 - flap * 40} 60,${-70 - flap * 20} 90,${-88 + flap * 10} C70,-30 45,8 18,22Z`} opacity={0.9} />
      <ellipse cx={0} cy={22} rx={38} ry={16} /><circle cx={40} cy={10} r={11} /><path d="M50,8 L64,12 L50,15Z" /><path d="M-36,22 L-80,40 L-70,22 L-84,12Z" />
    </g>
  </svg>);
const Plane: React.FC<{ x: number; y: number; s: number; rot: number }> = ({ x, y, s, rot }) => (
  <svg style={{ position: "absolute", left: x - s, top: y - s, transform: `rotate(${rot}deg)`, filter: "drop-shadow(0 0 18px rgba(169,203,238,0.6))" }} width={s * 2} height={s * 2} viewBox="-100 -100 200 200">
    <defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="0.5" stopColor="#97A3B5" /><stop offset="1" stopColor="#E3E9F0" /></linearGradient></defs>
    <path d="M95,0 C90,-8 70,-9 40,-8 L-8,-60 L-26,-60 L4,-8 L-50,-6 L-68,-28 L-80,-28 L-70,0 L-80,28 L-68,28 L-50,6 L4,8 L-26,60 L-8,60 L40,8 C70,9 90,8 95,0Z" fill="url(#pg)" />
  </svg>);
const Ticket: React.FC<{ x: number; y: number; rot: number; p: number }> = ({ x, y, rot, p }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 520, height: 210, transformOrigin: "100% 0", transform: `rotate(${rot}deg) scale(0.85) translateY(${(1 - p) * -300}px)`, opacity: p, background: C.silver, borderRadius: 10, boxShadow: "0 18px 0 rgba(4,7,14,0.5)", fontFamily: "SpecialElite", color: C.navy, padding: "18px 26px", boxSizing: "border-box" }}>
    <div style={{ fontFamily: "Anton", fontSize: 40, letterSpacing: 2 }}>BOARDING PASS</div>
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 24, marginTop: 10 }}><span>FROM: POVERTY</span><span>TO: THE TOP</span></div>
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 24, marginTop: 6 }}><span>GATE 13</span><span>SEAT 1A</span><span>FLIGHT PO-84</span></div>
    <div style={{ position: "absolute", right: 26, bottom: 16, display: "flex", gap: 3 }}>{Array.from({ length: 30 }).map((_, i) => <div key={i} style={{ width: random(`b${i}`) > 0.5 ? 4 : 2, height: 34, background: C.navy }} />)}</div>
  </div>);
const Newspaper: React.FC<{ x: number; y: number; rot: number; p: number }> = ({ x, y, rot, p }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 600, height: 700, transform: `rotate(${rot}deg) scale(${0.9 + p * 0.1})`, opacity: p, background: "#E7ECF2", boxShadow: "0 22px 0 rgba(4,7,14,0.45)", color: C.navy, padding: 30, boxSizing: "border-box", clipPath: "polygon(0 2%,8% 0,22% 1.5%,37% 0,55% 1%,70% 0,86% 1.5%,100% 0,99% 30%,100% 62%,98.5% 100%,80% 98.5%,60% 100%,42% 98.6%,20% 100%,0 99%,1.4% 60%)" }}>
    <div style={{ fontFamily: "SpecialElite", fontSize: 20, borderBottom: `3px solid ${C.navy}`, paddingBottom: 6 }}>THE DAILY BLOCK  ·  VOL. 84  ·  50¢</div>
    <div style={{ fontFamily: "Anton", fontSize: 96, lineHeight: 0.95, marginTop: 12 }}>FROM<br />POVERTY</div>
    <div style={{ fontFamily: "SpecialElite", fontSize: 26, marginTop: 8 }}>"We ain't have a thing"</div>
    {Array.from({ length: 14 }).map((_, i) => <div key={i} style={{ height: 9, marginTop: 13, width: `${60 + random(`n${i}`) * 40}%`, background: C.navy, opacity: 0.35 }} />)}
  </div>);
const Bill: React.FC<{ x: number; y: number; rot: number }> = ({ x, y, rot }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 190, height: 82, transform: `rotate(${rot}deg)`, background: C.silver, border: `4px solid ${C.blue}`, borderRadius: 4, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Anton", fontSize: 46, color: C.navy, boxShadow: "0 8px 0 rgba(4,7,14,0.45)" }}>$100</div>);
const Burst: React.FC<{ x: number; y: number; s: number; p: number }> = ({ x, y, s, p }) => {
  const pts = Array.from({ length: 24 }).map((_, i) => { const a = (i / 24) * Math.PI * 2, r = i % 2 ? 0.62 : 1; return `${Math.cos(a) * r * 100},${Math.sin(a) * r * 100}`; }).join(" ");
  return (<div style={{ position: "absolute", left: x - s, top: y - s, width: s * 2, height: s * 2, transform: `scale(${p}) rotate(${-8 + (1 - p) * 30}deg)` }}>
    <svg width={s * 2} height={s * 2} viewBox="-110 -110 220 220" style={{ position: "absolute" }}><polygon points={pts} fill={C.white} stroke={C.ice} strokeWidth={8} /></svg>
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Anton", fontSize: s * 0.55, color: C.navy, transform: "rotate(-6deg)" }}>BANG!</div>
  </div>);
};

const Graphic: React.FC<{ L: Line; s: number; e: number; heroX: number; heroY: number }> = ({ L, s, e, heroX, heroY }) => {
  const fr = useCurrentFrame(); const t = fr - s; const len = e - s;
  const p = (a: number, d = 8) => interpolate(t, [a, a + d], [0, 1], { ...clamp, easing: outExp });
  const opp = L.side === "left" ? W * 0.72 : W * 0.28; // the open side, away from the person
  switch (L.graphic) {
    case "party": return (<>{Array.from({ length: 34 }).map((_, i) => { const x0 = random(`px${i}`) * W, sp = 6 + random(`ps${i}`) * 10, y = -60 + ((t * sp + random(`py${i}`) * H) % (H + 120));
      return t > 2 ? <div key={i} style={{ position: "absolute", left: x0 + Math.sin(t / 9 + i) * 30, top: y, width: 14, height: 30, background: i % 3 ? C.silver : C.ice, transform: `rotate(${t * 7 + i * 40}deg)`, opacity: 0.85 }} /> : null; })}
      {[0, 1, 2, 3, 4, 5].map((i) => <Sparkle key={i} x={random(`sx${i}`) * W} y={120 + random(`sy${i}`) * 500} s={22 + random(`ss${i}`) * 26} o={Math.max(0, Math.sin((t + i * 7) / 5))} />)}
      <Detail x={80} y={70} a={L.side === "left" ? "right" : "left"} t={"TONIGHT  ·  ALL NIGHT\nTHE GANG IS OUTSIDE"} size={26} /></>);
    case "robbery": return (<><Diamond x={opp + 360} y={215 + Math.sin(t / 12) * 10} s={95 * p(0, 10)} rot={-12 + t * 0.15} />
      <Chain y={760} prog={p(18, 30)} rot={-4} /><Band text="ROBBERY  ·  TUCK YA CHAIN" y={110} rot={3} fr={fr} /></>);
    case "heart": return (<><Heart x={opp} y={360} s={190 * p(0, 8)} split={interpolate(t, [f(32.46) - s, f(32.46) - s + 8], [0, 1], { ...clamp, easing: outExp })} />
      <Dove x={W * 0.5 + interpolate(t, [10, len], [-700, 700])} y={180 - t * 0.6} s={90} flap={Math.sin(t / 2.2)} o={0.9} /></>);
    case "target": { const lock = p(f(35.31) - s, 6); return (<>
      <Crosshair x={heroX + (1 - lock) * 260} y={heroY + (1 - lock) * -140} r={240 - lock * 60} o={p(0, 6)} spin={(1 - lock) * 90} />
      <Detail x={80} y={70} a={L.side === "left" ? "right" : "left"} t={"TARGET LOCKED\nRANGE 84M  ·  WIND 0"} size={26} c={C.ice} /></>); }
    case "news": return (<><Newspaper x={opp - 300} y={150} rot={-5} p={p(0, 8)} />
      {Array.from({ length: 7 }).map((_, i) => t > 20 + i * 3 && <Bill key={i} x={random(`bx${i}`) * W * 0.9} y={-120 + (t - 20 - i * 3) * (14 + random(`bv${i}`) * 8)} rot={random(`br${i}`) * 60 - 30 + t * 2} />)}</>);
    case "redact": return (<>{[0, 1, 2, 3, 4].map((i) => <div key={i} style={{ position: "absolute", left: opp - 60, top: 150 + i * 18, height: 10, width: 420 * p(i * 2, 6) * (0.6 + random(`r${i}`) * 0.4), background: i % 2 ? C.night : C.silver, opacity: 0.9 }} />)}
      <Detail x={80} y={70} a={L.side === "left" ? "right" : "left"} t={"FILE NO. 0006  ·  CLASSIFIED\nNAME: ██████████"} size={26} /></>);
    case "bang": { const b = f(44.13) - s; return (<><Burst x={opp} y={330} s={210} p={interpolate(t, [b - 2, b + 5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) })} />
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => <div key={i} style={{ position: "absolute", left: opp, top: 330, width: 260, height: 6, background: C.ice, transformOrigin: "0 50%", transform: `rotate(${i * 45 + 20}deg) translateX(${200 + (t - b) * 18}px)`, opacity: t >= b && t < b + 12 ? 1 - (t - b) / 12 : 0 }} />)}</>); }
    case "plane": { const k = interpolate(t, [0, len], [0, 1], clamp); const px = interpolate(k, [0, 1], [W * 0.3, W * 1.05]), py = 420 - Math.sin(k * Math.PI * 0.9) * 260;
      return (<><svg width={W} height={H} style={{ position: "absolute" }}><path d={`M ${W * 0.3} 420 Q ${W * 0.68} -100 ${W * 1.05} 380`} fill="none" stroke={C.ice} strokeWidth={4} strokeDasharray="14 14" opacity={0.7} /></svg>
        <Plane x={px} y={py} s={110} rot={-24 + k * 40} /><Ticket x={W - 600} y={40} rot={4} p={p(12, 10)} /></>); }
  }
};

// ---------- one line = one bar
const transitionClip = (i: number, q: number) => { // q 0..1 reveal of the incoming line
  const k = i % 4;
  if (k === 0) return `circle(${q * 120}% at 50% 50%)`;
  if (k === 1) return `inset(0 0 0 ${(1 - q) * 100}%)`;
  if (k === 2) return `polygon(0 0, ${q * 100}% 0, ${q * 100}% 50%, 100% 50%, 100% 100%, ${(1 - q) * 100}% 100%, ${(1 - q) * 100}% 50%, 0 50%)`;
  return `inset(${(1 - q) * 100}% 0 0 0)`;
};
const LineScene: React.FC<{ L: Line; i: number; s: number; e: number }> = ({ L, i, s, e }) => {
  const fr = useCurrentFrame();
  const q = interpolate(fr, [s - K.transition, s], [0, 1], { ...clamp, easing: io });
  const light = L.bg === "ice";
  const heroX = L.side === "left" ? W * 0.655 : W * 0.345, heroY = H * 0.42;
  // mid-line beat punch (beat 3 of the bar): a 4-frame scale kick
  const beat3 = s + Math.round(2 * (60 / 84) * FPS) - 7;
  const kick = interpolate(fr, [beat3, beat3 + 2, beat3 + 6], [0, 1, 0], clamp);
  const shake = L.graphic === "bang" ? (fr >= f(44.13) && fr < f(44.13) + 8 ? (random(`sh${fr}`) - 0.5) * 26 : 0) : 0;
  const lyricW = 900, lyricX = L.side === "left" ? W - lyricW - 90 : 90;
  return (<AbsoluteFill style={{ clipPath: q < 1 ? transitionClip(i, q) : undefined }}>
    <AbsoluteFill style={{ background: C[L.bg], transform: `scale(${1 + kick * 0.035}) translate(${shake}px, ${shake * 0.4}px)` }}>
      <Halo x={heroX + (L.side === "left" ? 200 : -200)} y={H * 0.5} r={620} o={light ? 0.6 : 1} />
      <div style={{ position: "absolute", left: L.side === "left" ? -260 : W - 700, top: 180, width: 960, height: 960, borderRadius: "50%", background: light ? "#C9DFF5" : C.deep, opacity: light ? 0.9 : 0.75 }} />
      <svg width={W} height={H} style={{ position: "absolute", opacity: 0.22 }}>
        <defs><pattern id={`hatch${i}`} width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="18" stroke={light ? C.navy : C.silver} strokeWidth="3" /></pattern></defs>
        <rect x={L.side === "left" ? W - 520 : 0} y={0} width={520} height={260} fill={`url(#hatch${i})`} />
      </svg>
      <Build text={L.hero} at={s - 2} size={K.sizes.hero} x={heroX} y={heroY} color={L.heroColor} w={1060} />
      <Graphic L={L} s={s} e={e} heroX={heroX} heroY={heroY} />
      <Person n={L.photo} side={L.side} s={s} e={e} h={L.photo === 4 ? 900 : L.photo === 6 ? 980 : 1020} />
      <div style={{ position: "absolute", left: lyricX - 30, top: 730, width: lyricW + 60, height: 6, background: light ? C.navy : C.ice, transformOrigin: L.side === "left" ? "100% 50%" : "0 50%", transform: `scaleX(${interpolate(fr, [s, s + 10], [0, 1], { ...clamp, easing: outExp })})` }} />
      <Lyric L={L} x={lyricX} y={760} w={lyricW} align={L.side === "left" ? "right" : "left"} dark={light} />
      <Detail x={80} y={H - 60} t={`0${i + 1} / 08`} a={L.side === "left" ? "right" : "left"} c={light ? C.navy : C.silver} />
      <Detail x={80} y={H - 60} t={"POP OUT  ·  SIDE A"} a={L.side === "left" ? "left" : "right"} c={light ? C.navy : C.silver} />
    </AbsoluteFill>
  </AbsoluteFill>);
};

const Record: React.FC<{ x: number; y: number; r: number; spin: number }> = ({ x, y, r, spin }) => (
  <svg style={{ position: "absolute", left: x - r, top: y - r, transform: `rotate(${spin}deg)`, filter: "drop-shadow(0 0 40px rgba(169,203,238,0.35))" }} width={r * 2} height={r * 2} viewBox="-100 -100 200 200">
    <defs><radialGradient id="vg"><stop offset="0.3" stopColor="#0E1A30" /><stop offset="1" stopColor="#03060C" /></radialGradient>
      <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="0.5" stopColor="#8D99AB" /><stop offset="1" stopColor="#E6ECF3" /></linearGradient></defs>
    <circle r={100} fill="url(#vg)" />
    {Array.from({ length: 16 }).map((_, i) => <circle key={i} r={40 + i * 3.6} fill="none" stroke="#7FA6D6" strokeOpacity={0.12 + (i % 3) * 0.05} strokeWidth={0.6} />)}
    <path d="M-70,-70 A99,99 0 0,1 30,-95" stroke="#FFFFFF" strokeOpacity={0.35} strokeWidth={6} fill="none" />
    <circle r={34} fill="url(#lg)" /><text y={-4} textAnchor="middle" fontFamily="Anton" fontSize={16} fill={C.navy}>POP OUT</text>
    <text y={12} textAnchor="middle" fontFamily="SpecialElite" fontSize={6} fill={C.navy}>SIDE A · 84 BPM</text><circle r={3} fill={C.night} />
  </svg>);

const Intro: React.FC<{ e: number }> = ({ e }) => {
  const fr = useCurrentFrame();
  const yeah = f(23.69);
  const flash = interpolate(fr, [yeah, yeah + 1, yeah + 6], [0, 0.5, 0], clamp);
  const rx = interpolate(fr, [0, 14], [W * 0.75, W * 0.66], { ...clamp, easing: outExp });
  return (<AbsoluteFill style={{ background: C.night }}>
    <Halo x={W * 0.6} y={H * 0.5} r={640} />
    <Record x={rx} y={H * 0.5} r={430} spin={fr * 4} />
    <Diamond x={W * 0.86} y={210} s={interpolate(fr, [24, 34], [0, 120], { ...clamp, easing: outExp })} rot={14} />
    <Dove x={interpolate(fr, [0, e], [-150, W * 0.55])} y={260 - fr * 0.8} s={110} flap={Math.sin(fr / 2.4)} />
    <Build text={K.intro.title} at={8} size={340} x={W * 0.34} y={H * 0.48} color="silver" />
    {fr > 40 && <Detail x={160} y={H * 0.48 + 190} t={K.intro.credit} size={36} c={C.ice} />}
    <Detail x={80} y={70} t={"LYRIC VIDEO  ·  NO. 01\nSIDE A  ·  84 BPM"} size={26} />
    <AbsoluteFill style={{ background: C.white, opacity: flash }} />
  </AbsoluteFill>);
};
const EndCard: React.FC<{ s: number }> = ({ s }) => {
  const fr = useCurrentFrame(); const t = fr - s; const lt = t - K.endCard.logoAt;
  const q = interpolate(t, [-K.transition, 0], [0, 1], { ...clamp, easing: io });
  const out = interpolate(fr, [K.durationInFrames - 14, K.durationInFrames - 1], [0, 1], { ...clamp, easing: inC });
  const go = interpolate(lt, [-6, 0], [0, 1], { ...clamp, easing: inC });          // title exits (accelerating, blur)
  const shrink = interpolate(lt, [-4, 10], [1, 0.62], { ...clamp, easing: io });   // record pulls back for the logo
  const mark = interpolate(lt, [2, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
  const word = interpolate(lt, [10, 20], [0, 1], { ...clamp, easing: outExp });
  const cy = H * 0.44;
  return (<AbsoluteFill style={{ clipPath: q < 1 ? `circle(${q * 120}% at 50% 50%)` : undefined, background: C.night }}>
    <Halo x={W / 2} y={cy} r={700 * shrink} />
    <Record x={W / 2} y={cy} r={380 * shrink} spin={fr * 2.5} />
    <Diamond x={W * 0.2} y={260} s={120} rot={-14} /><Dove x={W * 0.8} y={240} s={120} flap={Math.sin(fr / 2.4)} />
    <div style={{ position: "absolute", inset: 0, opacity: 1 - go, filter: `blur(${go * 16}px)`, transform: `scale(${1 + go * 0.15})` }}>
      <Build text={K.endCard.title} at={s + 2} size={330} x={W / 2} y={H * 0.48} color="silver" />
      {t > 18 && <div style={{ position: "absolute", left: 0, width: W, top: H * 0.48 + 190, textAlign: "center", fontFamily: "SpecialElite", fontSize: 40, color: C.ice, letterSpacing: 2 }}>{K.endCard.sub}</div>}
    </div>
    {lt >= 0 && <Img src={staticFile(K.endCard.logoMark)} style={{ position: "absolute", left: W / 2 - 120, top: cy - 120, width: 240, height: 240, transform: `scale(${mark})`, filter: "drop-shadow(0 0 30px rgba(169,203,238,0.35))" }} />}
    {lt >= 0 && <Img src={staticFile(K.endCard.logoWord)} style={{ position: "absolute", left: W / 2 - 330, top: cy + 300, width: 660, opacity: word, transform: `translateY(${(1 - word) * 30}px)` }} />}
    <AbsoluteFill style={{ background: C.night, opacity: out }} />
  </AbsoluteFill>);
};
export const Popout: React.FC = () => {
  const fr = useCurrentFrame();
  const starts = lines.map((L) => f(L.words[0][1]));
  const card = K.endCard.at;
  return (<AbsoluteFill style={{ background: C.night }}>
    <Audio src={staticFile("popout/track.wav")} />
    {fr < starts[0] && <Intro e={starts[0]} />}
    {lines.map((L, i) => { const s = starts[i], e = i + 1 < lines.length ? starts[i + 1] : card;
      return fr >= s - K.transition && fr < e ? <LineScene key={i} L={L} i={i} s={s} e={e} /> : null; })}
    {fr >= card - K.transition && <EndCard s={card} />}
    <Dust o={0.5} />
    <AbsoluteFill style={{ boxShadow: "inset 0 0 260px rgba(0,0,0,0.65)", pointerEvents: "none" }} />
  </AbsoluteFill>);
};
