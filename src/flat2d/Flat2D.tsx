import React, { useEffect, useState } from "react";
import { AbsoluteFill, Easing, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import { flatConfig as cfg } from "./config";
import { Ink } from "./brush";

const W = cfg.output.width, H = cfg.output.height, CX = W / 2, CY = H / 2;
const c = cfg.col, T = cfg.t, ST = cfg.street, IN = cfg.inside;
const BLEED = { x: -1400, y: -1400, width: W + 2800, height: H + 2800 };
const ease = (f: number, a: number, b: number, from = 0, to = 1, e = Easing.inOut(Easing.cubic)) =>
  interpolate(f, [a, b], [from, to], { easing: e, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
// draw a full scene shrunk into a portal centred on P at scale 1/K
const into = (P: { x: number; y: number }, K: number) => `translate(${P.x} ${P.y}) scale(${1 / K}) translate(${-CX} ${-CY})`;
const colOf = (k: string) => (c as unknown as Record<string, string>)[k];
const OUT = { stroke: c.ink, strokeWidth: c.outline, strokeLinejoin: "round" as const, strokeLinecap: "round" as const };

// ---------------- the man (back view, walking away from us), anime proportions ----------------
// origin = between his feet; at s = 1 he is ~490 px tall. Everything is curves: tapered limbs, a flared coat that swings.
const legPath = (hx: number, lift: number, kneeOut: number) => {
  const hip = { x: hx, y: -212 }, knee = { x: hx * 1.08 + kneeOut, y: -112 - lift * 0.45 }, ank = { x: hx * 1.1, y: -16 - lift };
  const w0 = 19, w1 = 13, w2 = 9;
  return `M${hip.x - w0} ${hip.y} Q${knee.x - w1 - 4} ${knee.y} ${ank.x - w2} ${ank.y} L${ank.x + w2} ${ank.y} Q${knee.x + w1 + 4} ${knee.y} ${hip.x + w0} ${hip.y} Z`;
};
const Man: React.FC<{ x: number; y: number; s: number; phase: number; walking: boolean }> = ({ x, y, s, phase, walking }) => {
  const sw = walking ? Math.sin(phase) : 0;
  const bob = walking ? -Math.abs(Math.cos(phase)) * 8 : 0;
  const lL = Math.max(0, sw) * 30, lR = Math.max(0, -sw) * 30; // the lifted foot rises and shows its sole
  const arm = sw * 16, hem = sw * 9, flare = walking ? Math.cos(phase * 2) * 4 : 0;
  const shoe = (hx: number, lift: number) => lift > 4
    ? <ellipse cx={hx * 1.1} cy={-12 - lift} rx={17} ry={11} fill={c.cream} />
    : <><path d={`M${hx * 1.1 - 20} -4 C${hx * 1.1 - 20} -22 ${hx * 1.1 + 20} -22 ${hx * 1.1 + 20} -4 Z`} fill={c.maroonDeep} stroke="none" /><Ink d={`M${hx * 1.1 - 20} -4 C${hx * 1.1 - 20} -22 ${hx * 1.1 + 20} -22 ${hx * 1.1 + 20} -4 Z`} w={10} /></>;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx={0} cy={4} rx={80} ry={12} fill={c.maroonDeep} opacity={0.45} stroke="none" />
      <g transform={`translate(0 ${bob})`}>
        {/* legs: the back leg first */}
        <><path d={legPath(-22, lL, -3)} fill={c.ink} stroke="none" /><Ink d={legPath(-22, lL, -3)} w={10} /></>
        <><path d={legPath(22, lR, 3)} fill={c.ink} stroke="none" /><Ink d={legPath(22, lR, 3)} w={10} /></>
        {shoe(-22, lL)}{shoe(22, lR)}
        {/* flared trench coat; the hem and tails swing with the stride */}
        <><path d={`M-60 -404 C-84 -400 -96 -384 -100 -352 L-106 -250 C-110 -214 ${-122 + hem} -184 ${-134 + hem} ${-152 + flare}
          C-90 ${-138 - flare} -40 -146 0 -142 C40 -146 90 ${-138 + flare} ${134 + hem} ${-152 - flare}
          C${122 + hem} -184 110 -214 106 -250 L100 -352 C96 -384 84 -400 60 -404 Z`} fill={c.maroon} stroke="none" /><Ink d={`M-60 -404 C-84 -400 -96 -384 -100 -352 L-106 -250 C-110 -214 ${-122 + hem} -184 ${-134 + hem} ${-152 + flare}
          C-90 ${-138 - flare} -40 -146 0 -142 C40 -146 90 ${-138 + flare} ${134 + hem} ${-152 - flare}
          C${122 + hem} -184 110 -214 106 -250 L100 -352 C96 -384 84 -400 60 -404 Z`} w={10} /></>
        <path d={`M-60 -404 C-84 -400 -96 -384 -100 -352 L-106 -250 C-110 -214 ${-122 + hem} -184 ${-134 + hem} ${-152 + flare}
          C-100 -144 -60 -146 -34 -144 C-40 -220 -44 -330 -30 -404 Z`} fill={c.tealDeep} stroke="none" />
        <Ink d={`M0 -300 C2 -240 ${hem * 0.4} -190 ${hem * 0.6} -142`} w={5.1} open />
        <Ink d={`M-52 -270 C-62 -220 ${-80 + hem * 0.6} -180 ${-92 + hem} -150`} w={4.2} open />
        <Ink d={`M56 -270 C66 -220 ${82 + hem * 0.6} -180 ${96 + hem} -152`} w={4.2} open />
        <><path d="M-104 -282 C-40 -272 40 -272 104 -282 L102 -262 C40 -252 -40 -252 -102 -262 Z" fill={c.ink} stroke="none" /><Ink d={`M-104 -282 C-40 -272 40 -272 104 -282 L102 -262 C40 -252 -40 -252 -102 -262 Z`} w={10} /></>
        {/* arms swing and bend at the elbow, tapering to the hands */}
        <><path d={`M-96 -384 C-118 -360 -120 -320 ${-116 + arm * 0.2} ${-290 + arm * 0.4} C${-114 + arm * 0.4} -256 ${-110 + arm * 0.6} -232 ${-104 + arm * 0.7} ${-212 + arm}
          L${-86 + arm * 0.7} ${-214 + arm} C${-90 + arm * 0.5} -240 -94 -268 -94 -296 C-92 -330 -86 -360 -80 -384 Z`} fill={c.tealDeep} stroke="none" /><Ink d={`M-96 -384 C-118 -360 -120 -320 ${-116 + arm * 0.2} ${-290 + arm * 0.4} C${-114 + arm * 0.4} -256 ${-110 + arm * 0.6} -232 ${-104 + arm * 0.7} ${-212 + arm}
          L${-86 + arm * 0.7} ${-214 + arm} C${-90 + arm * 0.5} -240 -94 -268 -94 -296 C-92 -330 -86 -360 -80 -384 Z`} w={10} /></>
        <><path d={`M96 -384 C118 -360 120 -320 ${116 - arm * 0.2} ${-290 - arm * 0.4} C${114 - arm * 0.4} -256 ${110 - arm * 0.6} -232 ${104 - arm * 0.7} ${-212 - arm}
          L${86 - arm * 0.7} ${-214 - arm} C${90 - arm * 0.5} -240 94 -268 94 -296 C92 -330 86 -360 80 -384 Z`} fill={c.maroon} stroke="none" /><Ink d={`M96 -384 C118 -360 120 -320 ${116 - arm * 0.2} ${-290 - arm * 0.4} C${114 - arm * 0.4} -256 ${110 - arm * 0.6} -232 ${104 - arm * 0.7} ${-212 - arm}
          L${86 - arm * 0.7} ${-214 - arm} C${90 - arm * 0.5} -240 94 -268 94 -296 C92 -330 86 -360 80 -384 Z`} w={10} /></>
        <ellipse cx={-95 + arm * 0.7} cy={-202 + arm} rx={11} ry={14} fill={c.skinShade} />
        <ellipse cx={95 - arm * 0.7} cy={-202 - arm} rx={11} ry={14} fill={c.skin} />
        {/* crossbody strap + rounded bag */}
        <path d="M58 -396 C20 -340 -30 -290 -74 -246" fill="none" stroke={c.cream} strokeWidth={8} />
        <><path d="M-118 -258 C-118 -268 -110 -272 -100 -272 L-50 -272 C-40 -272 -36 -266 -36 -256 L-38 -214 C-38 -204 -46 -200 -56 -200 L-100 -200 C-112 -200 -118 -206 -118 -216 Z" fill={c.redDeep} stroke="none" /><Ink d={`M-118 -258 C-118 -268 -110 -272 -100 -272 L-50 -272 C-40 -272 -36 -266 -36 -256 L-38 -214 C-38 -204 -46 -200 -56 -200 L-100 -200 C-112 -200 -118 -206 -118 -216 Z`} w={10} /></>
        <path d="M-108 -262 L-48 -262" stroke={c.cream} strokeWidth={4} />
        {/* popped chrome collar, nape, ears */}
        <><path d="M-50 -400 C-56 -428 -40 -440 -22 -436 L22 -436 C40 -440 56 -428 50 -400 C20 -392 -20 -392 -50 -400 Z" fill={c.peach} stroke="none" /><Ink d={`M-50 -400 C-56 -428 -40 -440 -22 -436 L22 -436 C40 -440 56 -428 50 -400 C20 -392 -20 -392 -50 -400 Z`} w={10} /></>
        <><path d="M-16 -436 C-16 -450 16 -450 16 -436 L14 -424 L-14 -424 Z" fill={c.skinShade} stroke="none" /><Ink d={`M-16 -436 C-16 -450 16 -450 16 -436 L14 -424 L-14 -424 Z`} w={10} /></>
        <ellipse cx={-40} cy={-470} rx={8} ry={13} fill={c.skinShade} />
        <ellipse cx={40} cy={-470} rx={8} ry={13} fill={c.skin} />
        {/* spiky anime hair from behind, with a blue sheen and a light rim */}
        <><path d="M-44 -452 C-56 -470 -52 -500 -40 -514 L-58 -522 C-40 -540 -20 -548 -6 -546 L-14 -566 C6 -556 22 -552 34 -540 L46 -552 C50 -534 54 -516 50 -500 L64 -500 C56 -484 50 -466 42 -450
          C34 -444 26 -452 20 -442 C12 -452 4 -440 -4 -446 C-12 -438 -22 -450 -28 -442 C-36 -450 -40 -444 -44 -452 Z" fill={c.ink} stroke="none" /><Ink d={`M-44 -452 C-56 -470 -52 -500 -40 -514 L-58 -522 C-40 -540 -20 -548 -6 -546 L-14 -566 C6 -556 22 -552 34 -540 L46 -552 C50 -534 54 -516 50 -500 L64 -500 C56 -484 50 -466 42 -450
          C34 -444 26 -452 20 -442 C12 -452 4 -440 -4 -446 C-12 -438 -22 -450 -28 -442 C-36 -450 -40 -444 -44 -452 Z`} w={10} /></>
        <path d="M-30 -520 C-20 -530 0 -536 16 -530 C4 -526 -10 -522 -24 -510 Z" fill={c.maroon} stroke="none" />
        <path d="M44 -540 C54 -520 54 -496 46 -470" fill="none" stroke={c.cream} strokeWidth={4} />
      </g>
    </g>
  );
};

// ---------------- a car (side view): sleek curves, wheel arches, glowing lights, speed lines ----------------
const Car: React.FC<{ x: number; y: number; len: number; col: string; dir: 1 | -1; s: number }> = ({ x, y, len, col, dir, s }) => {
  const k = len / 300;
  const body = colOf(col), shade = col === "ink" ? c.maroonDeep : col === "cream" ? c.peach : c.tealDeep;
  return (
    <g transform={`translate(${x} ${y}) scale(${dir * s * k} ${s})`}>
      <ellipse cx={150} cy={2} rx={160} ry={10} fill={c.maroonDeep} opacity={0.45} stroke="none" />
      {[0, 1, 2].map((i) => <path key={i} d={`M${-30 - i * 22} ${-90 + i * 26} L${-130 - i * 40} ${-90 + i * 26}`} stroke={c.cream} strokeWidth={4} opacity={0.8} />)}
      <><path d="M8 -30 C2 -52 18 -64 54 -70 C84 -104 118 -124 168 -124 C214 -124 242 -104 266 -76 C292 -72 304 -58 304 -40 L302 -30 Z" fill={body} stroke="none" /><Ink d={`M8 -30 C2 -52 18 -64 54 -70 C84 -104 118 -124 168 -124 C214 -124 242 -104 266 -76 C292 -72 304 -58 304 -40 L302 -30 Z`} w={8} /></>
      <><path d="M8 -30 C6 -42 10 -50 22 -54 L300 -54 C304 -46 304 -38 302 -30 Z" fill={shade} stroke="none" /><Ink d={`M8 -30 C6 -42 10 -50 22 -54 L300 -54 C304 -46 304 -38 302 -30 Z`} w={8} /></>
      <><path d="M78 -76 C102 -102 128 -114 160 -114 L160 -76 Z" fill={c.ink} stroke="none" /><Ink d={`M78 -76 C102 -102 128 -114 160 -114 L160 -76 Z`} w={8} /></>
      <><path d="M170 -114 C204 -114 226 -100 246 -76 L170 -76 Z" fill={c.ink} stroke="none" /><Ink d={`M170 -114 C204 -114 226 -100 246 -76 L170 -76 Z`} w={8} /></>
      <path d="M96 -88 C112 -102 130 -108 148 -108" fill="none" stroke={c.cream} strokeWidth={5} />
      <path d="M70 -66 C140 -72 220 -72 280 -64" fill="none" stroke={c.cream} strokeWidth={4} />
      <><path d="M284 -58 C296 -56 302 -52 302 -46 L286 -46 Z" fill={c.glow} stroke="none" /><Ink d={`M284 -58 C296 -56 302 -52 302 -46 L286 -46 Z`} w={8} /></>
      <path d="M302 -52 L340 -62 L340 -40 Z" fill={c.glow} opacity={0.55} stroke="none" />
      <><path d="M10 -56 L22 -56 L20 -44 L8 -44 Z" fill={c.redDeep} stroke="none" /><Ink d={`M10 -56 L22 -56 L20 -44 L8 -44 Z`} w={8} /></>
      {[70, 236].map((wx) => (
        <g key={wx}>
          <><path d={`M${wx - 36} -30 A 36 36 0 0 1 ${wx + 36} -30 Z`} fill={c.ink} stroke="none" /><Ink d={`M${wx - 36} -30 A 36 36 0 0 1 ${wx + 36} -30 Z`} w={8} /></>
          <circle cx={wx} cy={-24} r={27} fill={c.ink} />
          <circle cx={wx} cy={-24} r={12} fill={c.peach} />
          <circle cx={wx} cy={-24} r={4} fill={c.ink} />
        </g>
      ))}
    </g>
  );
};

// ---------------- the logo pieces (the real logo, cut into masks and recoloured) ----------------
const LogoPieces: React.FC<{ id: string; tag?: boolean }> = ({ id, tag = true }) => {
  const L = cfg.logo;
  const piece = (k: keyof typeof L) => {
    const p = L[k];
    return (
      <g key={k}>
        <mask id={`m${k}${id}`} maskUnits="userSpaceOnUse" x={p.x} y={p.y} width={p.w} height={p.h}>
          <image href={staticFile(p.src)} x={p.x} y={p.y} width={p.w} height={p.h} preserveAspectRatio="none" />
        </mask>
        <rect x={p.x} y={p.y} width={p.w} height={p.h} fill={p.col} mask={`url(#m${k}${id})`} />
      </g>
    );
  };
  return (
    <g>
      {/* the circle and the dot are vectors so they stay crisp at any zoom */}
      <circle cx={L.circle.x + L.circle.w / 2} cy={L.circle.y + L.circle.h / 2} r={L.circle.w / 2 - 1.5} fill={L.circle.col} stroke={c.ink} strokeWidth={9} />
      <path d={`M${L.circle.x + 66} ${L.circle.y + 128} A 140 140 0 0 1 ${L.circle.x + 146} ${L.circle.y + 52}`} fill="none" stroke={c.cream} strokeWidth={13} strokeLinecap="round" />
      {piece("p")}{piece("word")}{tag && piece("tag")}
      <circle cx={DOT.cx} cy={DOT.cy} r={DOT.r + 1.4} fill={L.p.col} />
    </g>
  );
};

const LogoCard: React.FC<{ inner?: React.ReactNode; reveal?: number; id?: string }> = ({ inner, reveal = 0, id = "l" }) => (
  <g>
    <rect {...BLEED} fill={cfg.cardBg} />
    <LogoPieces id={id} />
    <defs><clipPath id={`dot${id}`}><circle cx={DOT.cx} cy={DOT.cy} r={DOT.r + 1.4} /></clipPath></defs>
    {inner && reveal > 0 && <g clipPath={`url(#dot${id})`} opacity={reveal}>{inner}</g>}
  </g>
);

// ---------------- the street ----------------
const manOnStreet = (f: number) => {
  const [a, b] = T.walk, A = ST.manFrom, B = ST.manTo;
  const u = ease(f, a, b, 0, 1, Easing.inOut(Easing.sin));
  return { x: A.x + (B.x - A.x) * u, y: A.y + (B.y - A.y) * u, s: A.s + (B.s - A.s) * u, walking: f > a && f < b, phase: (f - a) * 0.36 };
};
const Street: React.FC<{ f: number; inner?: React.ReactNode; id: string }> = ({ f, inner, id }) => {
  const WN = ST.window, D = ST.door, [r0, r1] = ST.road;
  const man = manOnStreet(f);
  const walk = f >= T.walkSignal && f < T.walk[1] + 20;
  const open = ease(f, T.doorOpen[0], T.doorOpen[1]);
  // zebra crossing: stripes parallel to the kerb, narrowing towards the far side
  const zeb: React.ReactNode[] = [];
  for (let i = 0; i < 8; i++) {
    const y0 = r0 + ((r1 - r0) * i) / 8 + 6, y1 = r0 + ((r1 - r0) * (i + 0.55)) / 8 + 6;
    const hw = (y: number) => 120 + ((y - r0) / (r1 - r0)) * 60;
    const cx0 = 1180 + ((y0 - r0) / (r1 - r0)) * 30, cx1 = 1180 + ((y1 - r0) / (r1 - r0)) * 30;
    zeb.push(<path key={i} d={`M${cx0 - hw(y0)} ${y0} L${cx0 + hw(y0)} ${y0} L${cx1 + hw(y1)} ${y1} L${cx1 - hw(y1)} ${y1} Z`} fill={c.cream} />);
  }
  // draw order by baseline: far cars, near cars and the man sorted by how far down the frame they stand
  const items: { y: number; el: React.ReactNode }[] = [];
  ST.far.forEach(([x0, col, len], i) => items.push({ y: ST.lanes.far, el: <Car key={`f${i}`} x={x0 - ST.vFar * f + len} y={ST.lanes.far} len={len} col={col} dir={-1} s={0.82} /> }));
  ST.near.forEach(([x0, col, len], i) => items.push({ y: ST.lanes.near, el: <Car key={`n${i}`} x={x0 + ST.vNear * f} y={ST.lanes.near} len={len} col={col} dir={1} s={1} /> }));
  if (f < T.walk[1]) items.push({ y: man.y, el: <Man key="man" {...man} /> });
  items.sort((p, q) => p.y - q.y);
  return (
    <g>
      <rect {...BLEED} fill={c.red} />
      <g {...OUT}>
      <circle cx={1720} cy={130} r={140} fill={c.cream} />
      <circle cx={1720} cy={130} r={96} fill="none" stroke={c.redDeep} strokeWidth={10} />
      {/* neighbours */}
      <rect x={-1400} y={60} width={2040} height={560} fill={c.lips} />
      <rect x={580} y={60} width={60} height={560} fill={c.maroonDeep} />
      {[0, 1, 2, 3].map((r) => [0, 1, 2, 3].map((k) => <rect key={`l${r}${k}`} x={80 + k * 140} y={110 + r * 110} width={70} height={64} fill={c.redDeep} />))}
      <rect x={1500} y={20} width={1900} height={600} fill={c.maroon} />
      <rect x={1500} y={20} width={60} height={600} fill={c.tealDeep} />
      {[0, 1, 2, 3, 4].map((r) => [0, 1, 2].map((k) => <rect key={`r${r}${k}`} x={1560 + k * 130} y={70 + r * 104} width={64} height={60} fill={c.maroon} />))}
      {/* the agency: peach facade, ink sign band with the real logo, a glass shopfront (the portal) */}
      <rect x={640} y={40} width={860} height={580} fill={c.peach} />
      {[260, 600].map((y) => <line key={y} x1={640} y1={y + 10} x2={1500} y2={y + 10} stroke={c.ink} strokeWidth={3} />)}
      {[690, 1450].map((x) => <rect key={x} x={x - 14} y={250} width={28} height={370} fill={c.redDeep} />)}
      <path d="M1500 40 L1540 60 L1540 620 L1500 620 Z" fill={c.maroonDeep} />
      <rect x={680} y={92} width={780} height={150} fill={c.cream} />
      <g transform="translate(1070 168) scale(0.19) translate(-960 -549)"><LogoPieces id={`sign${id}`} tag={false} /></g>
      <rect x={WN.x - 14} y={WN.y - 14} width={WN.w + 28} height={WN.h + 18} fill={c.ink} />
      <defs><clipPath id={`win${id}`}><rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} /></clipPath></defs>
      <rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} fill={c.red} stroke="none" />
      {inner && <g clipPath={`url(#win${id})`} stroke="none">{inner}</g>}
      {/* glass door: frame, then the leaf swinging open */}
      <rect x={D.x} y={D.y} width={D.w} height={D.h} fill="none" stroke={c.ink} strokeWidth={8} />
      <rect x={D.x + D.w - 16} y={D.y + D.h / 2 - 20} width={6} height={40} fill={c.cream} />
      <path d={`M${D.x} ${D.y} L${D.x + D.w * (1 - open * 0.75)} ${D.y + open * 18} L${D.x + D.w * (1 - open * 0.75)} ${D.y + D.h - open * 10} L${D.x} ${D.y + D.h} Z`} fill={c.cream} opacity={0.18} stroke={c.ink} strokeWidth={6} />
      <rect x={WN.x - 14} y={WN.y + WN.h} width={WN.w + 28} height={10} fill={c.ink} />
      {/* curved scalloped awning over the shopfront */}
      <path d={`M${WN.x - 40} 252 C${WN.x + 200} 236 ${WN.x + 300} 236 ${WN.x + WN.w + 40} 252 L${WN.x + WN.w + 50} 286 ${[...Array(8)].map((_, i) => { const x1 = WN.x + WN.w + 50 - (i + 1) * ((WN.w + 100) / 8); return `A ${(WN.w + 100) / 16} 14 0 0 1 ${x1} 286`; }).join(" ")} Z`} fill={c.redDeep} />
      <path d={`M${WN.x - 30} 262 C${WN.x + 200} 248 ${WN.x + 300} 248 ${WN.x + WN.w + 30} 262`} fill="none" stroke={c.cream} strokeWidth={4} />
      {/* far pavement, road, zebra, lane marks, near pavement */}
      <rect x={-1400} y={ST.farWalk} width={4720} height={r0 - ST.farWalk + 2} fill={c.maroon} />
      <rect x={-1400} y={r0} width={4720} height={r1 - r0} fill={c.maroonDeep} />
      {[...Array(14)].map((_, i) => <rect key={i} x={-200 + i * 170} y={826} width={90} height={8} fill={c.peach} />)}
      {zeb}
      <rect x={-1400} y={r1} width={4720} height={1600} fill={c.maroon} />
      <rect x={-1400} y={r1} width={4720} height={12} fill={c.peach} />
      {/* curved street lamp */}
      <path d="M300 1050 L300 700 C300 640 330 610 390 606" fill="none" stroke={c.ink} strokeWidth={14} />
      <path d="M370 600 C380 586 420 586 430 600 L424 616 L376 616 Z" fill={c.ink} />
      <path d="M380 616 L420 616 C418 628 382 628 380 616 Z" fill={c.glow} />
      {/* crossing signal on the near pavement */}
      <rect x={1452} y={700} width={14} height={340} fill={c.ink} />
      <rect x={1420} y={640} width={78} height={110} rx={8} fill={c.ink} />
      <circle cx={1459} cy={670} r={20} fill={walk ? c.maroonDeep : c.lips} />
      <circle cx={1459} cy={720} r={20} fill={walk ? c.cream : c.maroonDeep} />
      {items.map((it) => it.el)}
      </g>
    </g>
  );
};

// ---------------- inside the agency ----------------
const manInside = (f: number) => {
  const [a, b] = T.inside;
  // where he steps through the door, mapped from street coordinates into the interior (portal scale K_W)
  const s0 = manOnStreet(T.walk[1]);
  const A = { x: CX + (s0.x - P_W.x) * K_W, y: CY + (s0.y - P_W.y) * K_W, s: s0.s * K_W }, B = IN.manTo;
  const u = ease(f, a, b, 0, 1, Easing.out(Easing.quad));
  return { x: A.x + (B.x - A.x) * u, y: A.y + (B.y - A.y) * u, s: A.s + (B.s - A.s) * u, walking: f >= a && f < b - 8, phase: (f - T.walk[0]) * 0.36 };
};
// an anime-style designer in profile, seated at a desk, facing right (flip mirrors them)
const Seated: React.FC<{ x: number; flip?: boolean; f: number; ph: number; hair: string; hoodie: string; pony?: boolean }> = ({ x, flip, f, ph, hair, hoodie, pony }) => {
  const blink = ((f + ph * 37) % 96) < 4;
  const sway = Math.sin(f / 11 + ph) * 6, type = Math.sin(f / 2.6 + ph) * 2;
  return (
    <g transform={`translate(${x} 0) scale(${flip ? -1 : 1} 1)`}>
      {/* curved gaming chair */}
      <><path d="M-46 690 C-60 620 -58 520 -30 470 C-10 450 20 452 24 476 C30 540 30 620 26 690 Z" fill={c.ink} stroke="none" /><Ink d={`M-46 690 C-60 620 -58 520 -30 470 C-10 450 20 452 24 476 C30 540 30 620 26 690 Z`} w={7} /></>
      <path d="M-34 670 C-44 610 -42 540 -22 494" fill="none" stroke={c.redDeep} strokeWidth={6} />
      <><path d="M-40 690 L60 690 L52 712 L-34 712 Z" fill={c.ink} stroke="none" /><Ink d={`M-40 690 L60 690 L52 712 L-34 712 Z`} w={7} /></>
      <Ink d={`M8 712 L8 820 M-30 850 L46 850 M8 820 L-30 850 M8 820 L46 850`} w={13.6} open />
      {/* desk with a rounded edge + monitor */}
      <><path d="M-20 700 L300 700 C308 700 312 706 312 712 L-20 712 Z" fill={c.ink} stroke="none" /><Ink d={`M-20 700 L300 700 C308 700 312 706 312 712 L-20 712 Z`} w={7} /></>
      <><path d="M260 712 C262 760 262 820 258 870 L270 870 C274 820 274 760 272 712 Z" fill={c.ink} stroke="none" /><Ink d={`M260 712 C262 760 262 820 258 870 L270 870 C274 820 274 760 272 712 Z`} w={7} /></>
      <rect x={150} y={556} width={156} height={104} rx={14} fill={c.ink} />
      <rect x={160} y={566} width={136} height={84} rx={8} fill={c.maroonDeep} />
      <path d={`M172 ${630 - (Math.sin(f / 9 + ph) + 1) * 14} C200 590 236 640 284 ${600 + Math.sin(f / 7 + ph) * 10}`} fill="none" stroke={c.redDeep} strokeWidth={5} />
      <circle cx={196 + (Math.sin(f / 9 + ph) + 1) * 34} cy={600} r={9} fill={c.glow} />
      <><path d="M220 660 C222 676 222 690 218 700 L236 700 C232 690 232 676 234 660 Z" fill={c.ink} stroke="none" /><Ink d={`M220 660 C222 676 222 690 218 700 L236 700 C232 690 232 676 234 660 Z`} w={7} /></>
      {/* legs + hoodie body */}
      <><path d="M24 690 C70 686 112 690 126 704 C130 740 128 800 122 860 L104 860 C104 800 104 744 96 716 C70 712 40 714 24 712 Z" fill={c.ink} stroke="none" /><Ink d={`M24 690 C70 686 112 690 126 704 C130 740 128 800 122 860 L104 860 C104 800 104 744 96 716 C70 712 40 714 24 712 Z`} w={7} /></>
      <><path d="M-14 694 C-20 640 -16 580 6 546 C24 520 52 512 72 520 C92 528 100 552 102 590 L104 694 Z" fill={hoodie} stroke="none" /><Ink d={`M-14 694 C-20 640 -16 580 6 546 C24 520 52 512 72 520 C92 528 100 552 102 590 L104 694 Z`} w={7} /></>
      <Ink d={`M2 600 C10 640 14 670 16 694`} w={5.1} open />
      {/* arm to the keyboard, typing */}
      <><path d={`M60 560 C88 590 104 620 120 ${640 + type} L178 ${640 + type} C180 650 178 656 172 658 L112 ${662 + type} C92 640 70 610 46 584 Z`} fill={hoodie} stroke="none" /><Ink d={`M60 560 C88 590 104 620 120 ${640 + type} L178 ${640 + type} C180 650 178 656 172 658 L112 ${662 + type} C92 640 70 610 46 584 Z`} w={7} /></>
      <ellipse cx={180} cy={650 + type} rx={12} ry={9} fill={c.skin} />
      {/* neck + anime profile head: forehead, small nose, lips, pointed chin */}
      <><path d="M36 522 C40 506 56 500 64 506 L66 528 L40 534 Z" fill={c.skinShade} stroke="none" /><Ink d={`M36 522 C40 506 56 500 64 506 L66 528 L40 534 Z`} w={7} /></>
      <><path d="M26 452 C24 420 44 398 72 398 C96 398 110 414 112 434 C112 444 116 452 122 460 C118 464 114 466 112 468 C114 474 112 480 108 482 C110 488 106 494 100 496 C96 506 86 514 72 514 C52 514 30 496 26 470 Z" fill={c.skin} stroke="none" /><Ink d={`M26 452 C24 420 44 398 72 398 C96 398 110 414 112 434 C112 444 116 452 122 460 C118 464 114 466 112 468 C114 474 112 480 108 482 C110 488 106 494 100 496 C96 506 86 514 72 514 C52 514 30 496 26 470 Z`} w={7} /></>
      <path d="M100 496 C96 506 86 514 72 514 C80 506 84 498 86 490 Z" fill={c.skinShade} stroke="none" />
      {/* big anime eye (closes on a blink) */}
      {blink ? <Ink d={`M84 446 C90 450 98 450 104 446`} w={6.8} open /> : (
        <g>
          <><path d="M82 436 C88 428 100 428 106 434 L104 458 C96 462 88 460 84 452 Z" fill={c.cream} stroke="none" /><Ink d={`M82 436 C88 428 100 428 106 434 L104 458 C96 462 88 460 84 452 Z`} w={7} /></>
          <ellipse cx={96} cy={446} rx={7} ry={11} fill={c.maroon} />
          <circle cx={98} cy={441} r={3} fill={c.cream} stroke="none" />
          <Ink d={`M80 434 C90 424 102 424 110 432`} w={8.5} open />
        </g>
      )}
      <Ink d={`M86 422 C94 418 104 418 110 422`} w={5.1} open />
      <path d="M106 480 L114 480" stroke={c.redDeep} strokeWidth={3} />
      {/* hair: bangs + crown, with a ponytail that sways or a messy short cut */}
      {pony && <><path d={`M30 430 C0 440 ${-30 + sway} 480 ${-40 + sway * 1.6} 540 C${-20 + sway} 520 -4 490 20 462 Z`} fill={hair} stroke="none" /><Ink d={`M30 430 C0 440 ${-30 + sway} 480 ${-40 + sway * 1.6} 540 C${-20 + sway} 520 -4 490 20 462 Z`} w={7} /></>}
      <><path d={`M22 460 C10 410 40 382 78 384 C104 386 118 404 116 426 C108 418 100 414 92 418 C96 408 90 400 84 402 C82 414 72 420 60 420
        C${pony ? 50 : 56} 440 ${pony ? 44 : 40} 460 34 ${pony ? 486 : 496} C30 480 26 470 22 460 Z`} fill={hair} stroke="none" /><Ink d={`M22 460 C10 410 40 382 78 384 C104 386 118 404 116 426 C108 418 100 414 92 418 C96 408 90 400 84 402 C82 414 72 420 60 420
        C${pony ? 50 : 56} 440 ${pony ? 44 : 40} 460 34 ${pony ? 486 : 496} C30 480 26 470 22 460 Z`} w={7} /></>
      {!pony && <><path d="M40 392 L30 372 L54 386 L58 362 L72 384 L90 368 L88 390 Z" fill={hair} stroke="none" /><Ink d={`M40 392 L30 372 L54 386 L58 362 L72 384 L90 368 L88 390 Z`} w={7} /></>}
      <path d="M48 396 C60 390 76 388 92 392" fill="none" stroke={c.cream} strokeWidth={3} />
      {/* headphones */}
      <path d="M36 452 C30 400 70 372 104 396" fill="none" stroke={c.peach} strokeWidth={7} />
      <ellipse cx={48} cy={462} rx={16} ry={20} fill={c.maroon} />
    </g>
  );
};
const Interior: React.FC<{ f: number; inner?: React.ReactNode; id: string }> = ({ f, inner, id }) => {
  const S = IN.screen, man = manInside(f);
  return (
    <g>
      <rect {...BLEED} fill={c.red} />
      <g {...OUT}>
      <path d="M-1400 820 L3320 820 L3320 2480 L-1400 2480 Z" fill={c.maroonDeep} />
      {[...Array(9)].map((_, i) => <line key={i} x1={960} y1={820} x2={-1400 + i * 590} y2={2480} stroke={c.maroon} strokeWidth={4} />)}
      {/* a tall cream light shape from the shopfront behind us */}
      <path d="M1180 -100 L1660 -100 L1500 820 L1240 820 Z" fill={c.redDeep} />
      {/* pendant lamps */}
      {[380, 1540].map((x) => (
        <g key={x}>
          <rect x={x - 2} y={-100} width={4} height={200} fill={c.ink} />
          <path d={`M${x - 50} 150 L${x + 50} 150 L${x + 30} 100 L${x - 30} 100 Z`} fill={c.cream} />
        </g>
      ))}
      {/* the big wall screen (portal back to the logo) */}
      <rect x={S.x - 18} y={S.y - 18} width={S.w + 36} height={S.h + 36} rx={8} fill={c.ink} />
      <defs><clipPath id={`scr${id}`}><rect x={S.x} y={S.y} width={S.w} height={S.h} /></clipPath></defs>
      <rect x={S.x} y={S.y} width={S.w} height={S.h} fill={cfg.cardBg} stroke="none" />
      {inner && <g clipPath={`url(#scr${id})`} stroke="none">{inner}</g>}
      <Seated x={180} f={f} ph={0} hair={c.redDeep} hoodie={c.lips} pony />
      <Seated x={1740} flip f={f} ph={2} hair={c.ink} hoodie={c.maroon} />
      {/* plant */}
      <rect x={1270} y={740} width={70} height={80} fill={c.peach} />
      <path d="M1305 740 C1260 680 1250 620 1270 580 C1300 620 1306 680 1305 740 C1310 670 1330 620 1360 600 C1366 650 1340 700 1305 740 Z" fill={c.maroon} />
      {f >= T.walk[1] && <Man {...man} />}
      </g>
    </g>
  );
};

// ---------------- one continuous zoom through the three portals ----------------
const DOT = cfg.dot;
const HALF_DIAG = Math.hypot(CX, CY);
const P_W = { x: ST.window.x + ST.window.w / 2, y: ST.window.y + ST.window.h / 2 }, K_W = W / ST.window.w;
const P_S = { x: IN.screen.x + IN.screen.w / 2, y: IN.screen.y + IN.screen.h / 2 }, K_S = W / IN.screen.w;
const PORTALS = [
  { P: { x: DOT.cx, y: DOT.cy }, K: (HALF_DIAG / (DOT.r + 1.4)) * 1.02 }, // logo -> street
  { P: P_W, K: K_W },                                                      // street -> interior
  { P: P_S, K: K_S },                                                      // interior -> logo
];
const LN = PORTALS.map((p) => Math.log(p.K));
const CUM = [0, LN[0], LN[0] + LN[1], LN[0] + LN[1] + LN[2]];
const DUR = cfg.output.durationInFrames;
// knots (frame, log-zoom) with a periodic monotone cubic: smooth, never stops, end speed = start speed (no loop bump)
const KT = [...T.arrive, DUR], KL = CUM;
const sec = [0, 1, 2].map((i) => (KL[i + 1] - KL[i]) / (KT[i + 1] - KT[i]));
const hm = (a: number, b: number) => (2 * a * b) / (a + b);
const SL = [hm(sec[2], sec[0]), hm(sec[0], sec[1]), hm(sec[1], sec[2]), hm(sec[2], sec[0])];
const logZoom = (f: number) => {
  let i = 0; while (i < 2 && f >= KT[i + 1]) i++;
  const h = KT[i + 1] - KT[i], u = (f - KT[i]) / h;
  const h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
  return h00 * KL[i] + h10 * h * SL[i] + h01 * KL[i + 1] + h11 * h * SL[i + 1];
};

const Scene: React.FC<{ k: number; f: number; depth: number; reveal?: number }> = ({ k, f, depth, reveal = 0 }) => {
  const P = PORTALS[k];
  const inner = depth < 2 ? <g transform={into(P.P, P.K)}><Scene k={(k + 1) % 3} f={f} depth={depth + 1} /></g> : undefined;
  const id = `${k}_${depth}`;
  if (k === 0) return <LogoCard inner={inner} reveal={depth === 0 ? reveal : 0} id={id} />;
  if (k === 1) return <Street f={f} inner={inner} id={id} />;
  return <Interior f={f} inner={inner} id={id} />;
};

// hold every frame until the logo mask images have loaded and decoded (otherwise the first frame can miss them)
const useLogoImages = () => {
  const [handle] = useState(() => delayRender("logo masks"));
  useEffect(() => {
    const srcs = Object.values(cfg.logo).map((p) => staticFile(p.src));
    Promise.all(srcs.map((src) => { const im = new Image(); im.src = src; return im.decode().catch(() => undefined); }))
      .then(() => continueRender(handle));
  }, [handle]);
};

export const Flat2D: React.FC = () => {
  useLogoImages();
  const f = useCurrentFrame();
  const L = logZoom(f) % CUM[3];
  let k = 0; while (k < 2 && L >= CUM[k + 1]) k++;
  const lz = L - CUM[k], z = Math.exp(lz), g = lz / LN[k], P = PORTALS[k].P;
  const sx = P.x + (CX - P.x) * g, sy = P.y + (CY - P.y) * g;
  const tr = `translate(${sx} ${sy}) scale(${z}) translate(${-P.x} ${-P.y})`;
  const reveal = k === 0 ? interpolate(z, T.revealDot as [number, number], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: c.red }}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%">
        <g transform={tr}><Scene k={k} f={f} depth={0} reveal={reveal} /></g>
      </svg>
    </AbsoluteFill>
  );
};
