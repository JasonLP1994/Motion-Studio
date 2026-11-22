import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { flatConfig as cfg } from "./config";

const W = cfg.output.width, H = cfg.output.height, CX = W / 2, CY = H / 2;
const c = cfg.col, T = cfg.t, ST = cfg.street, IN = cfg.inside;
const BLEED = { x: -1400, y: -1400, width: W + 2800, height: H + 2800 };
const ease = (f: number, a: number, b: number, from = 0, to = 1, e = Easing.inOut(Easing.cubic)) =>
  interpolate(f, [a, b], [from, to], { easing: e, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
// draw a full scene shrunk into a portal centred on P at scale 1/K
const into = (P: { x: number; y: number }, K: number) => `translate(${P.x} ${P.y}) scale(${1 / K}) translate(${-CX} ${-CY})`;
const colOf = (k: string) => (c as Record<string, string>)[k];

// ---------------- the man (back view, walking away from us) ----------------
// origin = between his feet; at s = 1 he is ~460 px tall
const Man: React.FC<{ x: number; y: number; s: number; phase: number; walking: boolean }> = ({ x, y, s, phase, walking }) => {
  const sw = walking ? Math.sin(phase) : 0;
  const bob = walking ? -Math.abs(Math.cos(phase)) * 7 : 0;
  const lL = Math.max(0, sw) * 26, lR = Math.max(0, -sw) * 26; // the lifted foot rises (back view)
  const arm = sw * 14;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx={0} cy={4} rx={78} ry={12} fill={c.maroonDeep} opacity={0.55} />
      <g transform={`translate(0 ${bob})`}>
        {/* legs + shoes */}
        <rect x={-52} y={-190 - lL} width={40} height={180} fill={c.ink} />
        <rect x={12} y={-190 - lR} width={40} height={180} fill={c.ink} />
        <rect x={-56} y={-14 - lL} width={48} height={16} rx={6} fill={c.maroonDeep} />
        <rect x={8} y={-14 - lR} width={48} height={16} rx={6} fill={c.maroonDeep} />
        {/* long coat with a cream light edge on the right (light from the right, as negative space) */}
        <path d="M-74 -392 L74 -392 L96 -168 L-96 -168 Z" fill={c.ink} />
        <path d="M58 -392 L74 -392 L96 -168 L76 -168 Z" fill={c.cream} />
        <rect x={-4} y={-300} width={8} height={132} fill={c.maroonDeep} />
        {/* arms swing */}
        <path d={`M-74 -386 L-96 -386 L-110 ${-210 + arm} L-84 ${-210 + arm} Z`} fill={c.ink} />
        <path d={`M74 -386 L96 -386 L110 ${-210 - arm} L84 ${-210 - arm} Z`} fill={c.ink} />
        <circle cx={-97} cy={-200 + arm} r={13} fill={c.maroon} />
        <circle cx={97} cy={-200 - arm} r={13} fill={c.maroon} />
        {/* bag strap + messenger bag */}
        <path d="M60 -390 L-70 -230" stroke={c.peach} strokeWidth={9} />
        <rect x={-104} y={-252} width={66} height={56} rx={6} fill={c.peach} />
        {/* collar, neck, head from behind */}
        <rect x={-44} y={-412} width={88} height={26} rx={10} fill={c.peach} />
        <rect x={-18} y={-436} width={36} height={30} fill={c.maroon} />
        <circle cx={0} cy={-470} r={46} fill={c.ink} />
        <ellipse cx={-46} cy={-462} rx={8} ry={14} fill={c.maroon} />
        <ellipse cx={46} cy={-462} rx={8} ry={14} fill={c.cream} />
      </g>
    </g>
  );
};

// ---------------- a car (side view) ----------------
const Car: React.FC<{ x: number; y: number; len: number; col: string; dir: 1 | -1; s: number }> = ({ x, y, len, col, dir, s }) => {
  const k = len / 280;
  const body = colOf(col), glass = col === "ink" ? c.maroon : c.redDeep;
  return (
    <g transform={`translate(${x} ${y}) scale(${dir * s * k} ${s})`}>
      <ellipse cx={140} cy={2} rx={150} ry={10} fill={c.maroonDeep} opacity={0.5} />
      <path d="M0 -26 C0 -60 18 -72 50 -76 L84 -116 C92 -124 104 -128 118 -128 L196 -128 C212 -128 222 -122 230 -112 L256 -80 C272 -78 280 -66 280 -48 L280 -26 Z" fill={body} />
      <path d="M96 -112 L118 -118 L150 -118 L150 -80 L80 -80 Z" fill={glass} />
      <path d="M160 -118 L196 -118 C204 -118 210 -114 216 -106 L234 -80 L160 -80 Z" fill={glass} />
      <rect x={262} y={-70} width={16} height={10} rx={3} fill={c.cream} />
      {[64, 218].map((wx) => (
        <g key={wx}>
          <circle cx={wx} cy={-24} r={26} fill={c.ink} />
          <circle cx={wx} cy={-24} r={10} fill={c.peach} />
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
      <circle cx={L.circle.x + L.circle.w / 2} cy={L.circle.y + L.circle.h / 2} r={L.circle.w / 2 - 1.5} fill={L.circle.col} />
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
      <circle cx={1720} cy={130} r={140} fill={c.cream} />
      {/* neighbours */}
      <rect x={-1400} y={60} width={2040} height={560} fill={c.maroon} />
      {[0, 1, 2, 3].map((r) => [0, 1, 2, 3].map((k) => <rect key={`l${r}${k}`} x={80 + k * 140} y={110 + r * 110} width={70} height={64} fill={c.redDeep} />))}
      <rect x={1500} y={20} width={1900} height={600} fill={c.redDeep} />
      {[0, 1, 2, 3, 4].map((r) => [0, 1, 2].map((k) => <rect key={`r${r}${k}`} x={1560 + k * 130} y={70 + r * 104} width={64} height={60} fill={c.maroon} />))}
      {/* the agency: peach facade, ink sign band with the real logo, a glass shopfront (the portal) */}
      <rect x={640} y={40} width={860} height={580} fill={c.peach} />
      <path d="M1500 40 L1540 60 L1540 620 L1500 620 Z" fill={c.maroonDeep} />
      <rect x={680} y={92} width={780} height={150} fill={c.ink} />
      <g transform="translate(1070 168) scale(0.19) translate(-960 -549)"><LogoPieces id={`sign${id}`} tag={false} /></g>
      <rect x={WN.x - 14} y={WN.y - 14} width={WN.w + 28} height={WN.h + 18} fill={c.ink} />
      <defs><clipPath id={`win${id}`}><rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} /></clipPath></defs>
      <rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} fill={c.red} />
      {inner && <g clipPath={`url(#win${id})`}>{inner}</g>}
      {/* glass door: frame, then the leaf swinging open */}
      <rect x={D.x} y={D.y} width={D.w} height={D.h} fill="none" stroke={c.ink} strokeWidth={8} />
      <rect x={D.x + D.w - 16} y={D.y + D.h / 2 - 20} width={6} height={40} fill={c.cream} />
      <path d={`M${D.x} ${D.y} L${D.x + D.w * (1 - open * 0.75)} ${D.y + open * 18} L${D.x + D.w * (1 - open * 0.75)} ${D.y + D.h - open * 10} L${D.x} ${D.y + D.h} Z`} fill={c.cream} opacity={0.18} stroke={c.ink} strokeWidth={6} />
      <rect x={WN.x - 14} y={WN.y + WN.h} width={WN.w + 28} height={10} fill={c.ink} />
      {/* far pavement, road, zebra, lane marks, near pavement */}
      <rect x={-1400} y={ST.farWalk} width={4720} height={r0 - ST.farWalk + 2} fill={c.maroon} />
      <rect x={-1400} y={r0} width={4720} height={r1 - r0} fill={c.maroonDeep} />
      {[...Array(14)].map((_, i) => <rect key={i} x={-200 + i * 170} y={826} width={90} height={8} fill={c.peach} />)}
      {zeb}
      <rect x={-1400} y={r1} width={4720} height={1600} fill={c.maroon} />
      <rect x={-1400} y={r1} width={4720} height={12} fill={c.peach} />
      {/* crossing signal on the near pavement */}
      <rect x={1452} y={700} width={14} height={340} fill={c.ink} />
      <rect x={1420} y={640} width={78} height={110} rx={8} fill={c.ink} />
      <circle cx={1459} cy={670} r={20} fill={walk ? c.maroonDeep : c.lips} />
      <circle cx={1459} cy={720} r={20} fill={walk ? c.cream : c.maroonDeep} />
      {items.map((it) => it.el)}
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
const Seated: React.FC<{ x: number; flip?: boolean; f: number; ph: number }> = ({ x, flip, f, ph }) => (
  <g transform={`translate(${x} 0) scale(${flip ? -1 : 1} 1)`}>
    {/* desk + monitor (facing right) */}
    <rect x={-40} y={700} width={330} height={16} fill={c.ink} />
    <rect x={0} y={716} width={12} height={160} fill={c.ink} />
    <rect x={260} y={716} width={12} height={160} fill={c.ink} />
    <rect x={150} y={560} width={150} height={100} rx={6} fill={c.ink} />
    <rect x={160} y={570} width={130} height={80} fill={c.redDeep} />
    <rect x={180 + (Math.sin(f / 9 + ph) + 1) * 30} y={590} width={44} height={40} fill={c.peach} />
    <rect x={218} y={660} width={14} height={40} fill={c.ink} />
    {/* designer in profile, facing the monitor */}
    <rect x={40} y={700} width={20} height={170} fill={c.ink} />
    <path d="M-10 700 L80 700 L70 560 C66 530 40 520 20 524 C0 530 -10 560 -10 600 Z" fill={c.maroonDeep} />
    <path d="M58 530 C90 536 104 560 108 590 L94 596 C88 572 76 556 56 552 Z" fill={c.cream} />
    <circle cx={44} cy={486} r={38} fill={c.maroon} />
    <path d="M60 470 C84 476 88 500 80 520 C72 510 64 500 60 490 Z" fill={c.cream} />
    <path d="M10 470 C10 440 36 430 56 436 C70 440 78 452 78 462 L30 470 L30 520 C16 514 8 496 10 470 Z" fill={c.ink} />
    <path d="M74 640 L150 620 L150 632 L80 654 Z" fill={c.maroon} />
  </g>
);
const Interior: React.FC<{ f: number; inner?: React.ReactNode; id: string }> = ({ f, inner, id }) => {
  const S = IN.screen, man = manInside(f);
  return (
    <g>
      <rect {...BLEED} fill={c.red} />
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
      <rect x={S.x} y={S.y} width={S.w} height={S.h} fill={cfg.cardBg} />
      {inner && <g clipPath={`url(#scr${id})`}>{inner}</g>}
      <Seated x={180} f={f} ph={0} />
      <Seated x={1740} flip f={f} ph={2} />
      {/* plant */}
      <rect x={1270} y={740} width={70} height={80} fill={c.peach} />
      <path d="M1305 740 C1260 680 1250 620 1270 580 C1300 620 1306 680 1305 740 C1310 670 1330 620 1360 600 C1366 650 1340 700 1305 740 Z" fill={c.maroon} />
      {f >= T.walk[1] && <Man {...man} />}
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

export const Flat2D: React.FC = () => {
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
