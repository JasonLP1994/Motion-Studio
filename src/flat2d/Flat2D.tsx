import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import { flatConfig as cfg } from "./config";

const W = cfg.output.width, H = cfg.output.height, CX = W / 2, CY = H / 2, FPS = cfg.output.fps;
const c = cfg.col, T = cfg.t, SC = cfg.screen;
const BLEED = { x: -1400, y: -1400, width: W + 2800, height: H + 2800 };
const P_S = { x: SC.x + SC.w / 2, y: SC.y + SC.h / 2 };
const K_S = W / SC.w;

const ease = (f: number, a: number, b: number, from = 0, to = 1, e = Easing.inOut(Easing.cubic)) =>
  interpolate(f, [a, b], [from, to], { easing: e, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
// draw a full scene shrunk into a portal centred on P at scale 1/K
const into = (P: { x: number; y: number }, K: number) => `translate(${P.x} ${P.y}) scale(${1 / K}) translate(${-CX} ${-CY})`;
// ---------------- 3D world (flat-shaded) ----------------
type V = [number, number, number];
const norm = (v: V): V => { const l = Math.hypot(...v); return [v[0] / l, v[1] / l, v[2] / l]; };
const LIGHT = norm(cfg.cam.light as V);
const rotY = (v: V, a: number): V => [v[0] * Math.cos(a) + v[2] * Math.sin(a), v[1], -v[0] * Math.sin(a) + v[2] * Math.cos(a)];
const rotX = (v: V, a: number): V => [v[0], v[1] * Math.cos(a) - v[2] * Math.sin(a), v[1] * Math.sin(a) + v[2] * Math.cos(a)];
const sub = (a: V, b: V): V => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a: V, b: V): V => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a: V, b: V) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const shade = (n: V) => { const v = dot(n, LIGHT); return v > 0.55 ? c.cream : v > 0.15 ? c.peach : v > -0.35 ? c.maroon : c.ink; };

const makeCam = (f: number) => {
  const yaw = interpolate(f, [0, cfg.output.durationInFrames], cfg.cam.yaw as [number, number]);
  const P = cfg.cam;
  const proj = (w: V): [number, number, number] => {
    let v = rotY(sub(w, [0, 1, 0]), yaw);
    v = rotX(v, -P.pitch);
    const z = v[2] + P.dist;
    return [P.cx + (P.focal * v[0]) / z, P.cy - (P.focal * v[1]) / z, z];
  };
  return proj;
};
const ptsStr = (ps: [number, number, number][]) => ps.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");

const CUBE_V: V[] = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]];
const CUBE_F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 4, 7, 3]];
const OCT_V: V[] = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
const OCT_F = [[0, 2, 4], [4, 2, 1], [1, 2, 5], [5, 2, 0], [4, 3, 0], [1, 3, 4], [5, 3, 1], [0, 3, 5]];

const Solid: React.FC<{ proj: ReturnType<typeof makeCam>; verts: V[]; faces: number[][]; pos: V; s: number; ry: number; rx: number }> = ({ proj, verts, faces, pos, s, ry, rx }) => {
  const wv = verts.map((v) => { const r = rotX(rotY(v, ry), rx); return [pos[0] + r[0] * s, pos[1] + r[1] * s, pos[2] + r[2] * s] as V; });
  const pv = wv.map(proj);
  const out = faces.map((fc, i) => {
    const n = norm(cross(sub(wv[fc[1]], wv[fc[0]]), sub(wv[fc[2]], wv[fc[0]])));
    const a = pv[fc[0]], b = pv[fc[1]], cc = pv[fc[2]];
    const area = (b[0] - a[0]) * (cc[1] - a[1]) - (b[1] - a[1]) * (cc[0] - a[0]);
    if (area <= 0) return null; // back face
    return <polygon key={i} points={ptsStr(fc.map((k) => pv[k]))} fill={shade(n)} stroke={c.ink} strokeWidth={1.5} strokeLinejoin="round" />;
  });
  return <g>{out}</g>;
};
const Shadow: React.FC<{ proj: ReturnType<typeof makeCam>; x: number; z: number; r: number }> = ({ proj, x, z, r }) => {
  const ps = Array.from({ length: 28 }, (_, i) => proj([x + Math.cos((i / 28) * 6.283) * r, 0, z + Math.sin((i / 28) * 6.283) * r * 0.85]));
  return <polygon points={ptsStr(ps)} fill={c.maroonDeep} />;
};
const popS = (f: number, at: number) => spring({ frame: f - at, fps: FPS, config: { damping: 11, stiffness: 160, mass: 0.7 } });

const World: React.FC<{ f: number; ui?: boolean; inner?: React.ReactNode; id?: string }> = ({ f, ui = true, inner, id = "w" }) => {
  const proj = makeCam(f);
  // floor + grid
  // infinite floor: the floor and the sky are the same deep red, so only the grid shows (no horizon line)
  const RF = 10;
  const grid: React.ReactNode[] = [];
  for (let i = -9; i <= 9; i++) {
    const h = Math.sqrt(RF * RF - i * i);
    const a = proj([i, 0, -h]), b = proj([i, 0, h]), d = proj([-h, 0, i]), e = proj([h, 0, i]);
    grid.push(<line key={`x${i}`} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={c.maroon} strokeWidth={2} />);
    grid.push(<line key={`z${i}`} x1={d[0]} y1={d[1]} x2={e[0]} y2={e[1]} stroke={c.maroon} strokeWidth={2} />);
  }
  // the cube the cursor drags into place
  const cu = T.cursor;
  const cubeX = ease(f, cu.grab, cu.drop, -4.4, -2.4, Easing.inOut(Easing.cubic));
  const cubeLift = f > cu.grab && f < cu.drop ? Math.sin(((f - cu.grab) / (cu.drop - cu.grab)) * Math.PI) * 0.7 : 0;
  const cubePos: V = [cubeX, 1.1 + cubeLift, 0.6];
  const items: { z: number; el: React.ReactNode }[] = [];
  const s1 = popS(f, T.pops[0]), s2 = popS(f, T.pops[1]), s3 = popS(f, T.pops[2]), s0 = popS(f, T.click);
  if (s0 > 0.01) items.push({ z: proj(cubePos)[2], el: <Solid key="cube" proj={proj} verts={CUBE_V} faces={CUBE_F} pos={cubePos} s={1.05 * s0} ry={f * 0.012 + 0.5} rx={0.25} /> });
  if (s1 > 0.01) items.push({ z: proj([2.4, 1.6, -0.4])[2], el: <Solid key="oct" proj={proj} verts={OCT_V} faces={OCT_F} pos={[2.4, 1.6, -0.4]} s={1.4 * s1} ry={f * 0.03} rx={0.3} /> });
  // sphere with a flat crescent shadow
  if (s3 > 0.01) {
    const sp = proj([0.2, 1.4, -3.4]); const r = (1.25 * cfg.cam.focal / sp[2]) * s3;
    items.push({ z: sp[2], el: (
      <g key="sph">
        <defs><clipPath id="sphc"><circle cx={sp[0]} cy={sp[1]} r={r} /></clipPath></defs>
        <circle cx={sp[0]} cy={sp[1]} r={r} fill={c.cream} />
        <circle cx={sp[0] + r * 0.45} cy={sp[1] + r * 0.35} r={r * 1.05} fill={c.peach} clipPath="url(#sphc)" />
        <circle cx={sp[0] + r * 0.85} cy={sp[1] + r * 0.7} r={r * 1.05} fill={c.maroon} clipPath="url(#sphc)" />
      </g>) });
  }
  // ring (a tilted 3D circle)
  if (s2 > 0.01) {
    const ps = Array.from({ length: 48 }, (_, i) => {
      const a = (i / 48) * 6.283; let v: V = [Math.cos(a) * 1.5 * s2, Math.sin(a) * 1.5 * s2, 0];
      v = rotY(rotX(v, 1.1), f * 0.02);
      return proj([v[0] - 0.6, v[1] + 3.1, v[2] + 1.6]);
    });
    items.push({ z: proj([-0.6, 3.1, 1.6])[2] - 2, el: <polygon key="ring" points={ptsStr(ps)} fill="none" stroke={c.peach} strokeWidth={16} strokeLinejoin="round" /> });
  }
  items.sort((a, b) => b.z - a.z);
  // keyframe curve with handles and a ball travelling along it
  const bez = (t: number, p: V[]): V => {
    const u = 1 - t;
    return [0, 1, 2].map((k) => u * u * u * p[0][k] + 3 * u * u * t * p[1][k] + 3 * u * t * t * p[2][k] + t * t * t * p[3][k]) as V;
  };
  const CP: V[] = [[-5, 0.4, 3.2], [-2.5, 4.2, 3.6], [2.5, -0.6, 3.0], [5, 2.8, 2.4]];
  const curve = Array.from({ length: 40 }, (_, i) => proj(bez(i / 39, CP)));
  const bt = ease(f, T.ball[0], T.ball[1], 0, 1, Easing.inOut(Easing.quad));
  const ball = proj(bez(bt, CP)); const br = 0.32 * cfg.cam.focal / ball[2];
  const hp = CP.map(proj);
  // cursor (screen space)
  const cp0 = proj([-4.4, 2.3, 0.6]), cp1 = proj([cubeX, 2.3 + cubeLift, 0.6]);
  const curX = f < cu.grab ? ease(f, cu.in, cu.grab, 1500, cp0[0], Easing.out(Easing.cubic)) : f < cu.drop ? cp1[0] : ease(f, cu.drop + 6, cu.out, cp1[0], 1700, Easing.in(Easing.cubic));
  const curY = f < cu.grab ? ease(f, cu.in, cu.grab, 900, cp0[1], Easing.out(Easing.cubic)) : f < cu.drop ? cp1[1] : ease(f, cu.drop + 6, cu.out, cp1[1], 1000, Easing.in(Easing.cubic));
  const curOn = f >= cu.in && f <= cu.out;
  const grabbing = f >= cu.grab && f <= cu.drop;
  // timeline strip with a playhead
  const ph = interpolate(f, [0, 450], [260, 1700]);
  return (
    <g>
      <rect {...BLEED} fill={c.redDeep} />
      <defs><clipPath id={`sun${id}`}><circle cx={SUN.cx} cy={SUN.cy} r={SUN.r} /></clipPath></defs>
      <circle cx={SUN.cx} cy={SUN.cy} r={SUN.r} fill={c.red} />
      {inner && <g clipPath={`url(#sun${id})`}>{inner}</g>}
      {grid}
      {s0 > 0.01 && <Shadow proj={proj} x={cubeX} z={0.6} r={(1.25 - cubeLift * 0.3) * s0} />}
      {s1 > 0.01 && <Shadow proj={proj} x={2.4} z={-0.4} r={1.1 * s1} />}
      {s3 > 0.01 && <Shadow proj={proj} x={0.2} z={-3.4} r={1.2 * s3} />}
      {s0 > 0.01 && (
        <g>
          <polyline points={ptsStr(curve)} fill="none" stroke={c.cream} strokeWidth={4} strokeDasharray="14 10" />
          <line x1={hp[0][0]} y1={hp[0][1]} x2={hp[1][0]} y2={hp[1][1]} stroke={c.peach} strokeWidth={3} />
          <line x1={hp[3][0]} y1={hp[3][1]} x2={hp[2][0]} y2={hp[2][1]} stroke={c.peach} strokeWidth={3} />
          {hp.map((p, i) => <rect key={i} x={p[0] - 9} y={p[1] - 9} width={18} height={18} fill={i % 3 === 0 ? c.cream : c.peach} stroke={c.ink} strokeWidth={3} />)}
        </g>
      )}
      {items.map((it) => it.el)}
      {s0 > 0.01 && <circle cx={ball[0]} cy={ball[1]} r={br * s0} fill={c.ink} />}
      {s0 > 0.01 && <circle cx={ball[0] - br * 0.3} cy={ball[1] - br * 0.3} r={br * 0.35 * s0} fill={c.cream} />}
      {ui && (
        <g>
          <rect x={BLEED.x} y={984} width={BLEED.width} height={1600} fill={c.ink} />
          <rect x={260} y={1028} width={1440} height={4} fill={c.maroon} />
          {[300, 520, 800, 1080, 1360, 1620].map((x) => <rect key={x} x={x - 9} y={1021} width={18} height={18} fill={x < ph ? c.cream : c.peach} transform={`rotate(45 ${x} 1030)`} />)}
          <rect x={ph - 2} y={996} width={4} height={70} fill={c.cream} />
          <path d={`M${ph - 12} 992 L${ph + 12} 992 L${ph} 1006 Z`} fill={c.cream} />
        </g>
      )}
      {ui && curOn && (
        <g transform={`translate(${curX} ${curY}) scale(${grabbing ? 0.9 : 1})`}>
          <path d="M0 0 L0 46 L12 35 L21 56 L30 52 L21 32 L37 32 Z" fill={c.cream} stroke={c.ink} strokeWidth={4} strokeLinejoin="round" />
        </g>
      )}
    </g>
  );
};

// ---------------- Scene A: the designer at the desk ----------------
const Designer: React.FC<{ f: number; inner?: React.ReactNode; id?: string }> = ({ f, inner, id = "d" }) => {
  const click = f >= T.click && f < T.click + 5 ? 3 : 0; // the finger presses on the click
  return (
    <g>
      <defs>
        <pattern id="stripeA" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
          <rect width="26" height="26" fill={c.ink} /><rect width="7" height="26" fill={c.peach} />
        </pattern>
        <clipPath id={`screen${id}`}><rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} /></clipPath>
      </defs>
      <rect {...BLEED} fill={c.red} />
      {/* her big shadow on the wall, thrown by the monitor */}
      <path d="M1360 120 C1360 10 1450 -40 1560 -40 C1700 -40 1790 50 1790 170 L1800 520 C1760 545 1700 545 1660 520 L1640 600 L1720 640 C1800 700 1840 820 1860 1100 L1400 1100 C1400 900 1440 760 1500 700 L1440 520 Z" fill={c.redDeep} />
      {/* monitor */}
      <rect x={SC.x - 16} y={SC.y - 16} width={SC.w + 32} height={SC.h + 32} rx={10} fill={c.ink} />
      <rect x={SC.x} y={SC.y} width={SC.w} height={SC.h} fill={c.redDeep} />
      {inner && <g clipPath={`url(#screen${id})`}>{inner}</g>}
      <rect x={SC.x + SC.w / 2 - 24} y={SC.y + SC.h + 16} width={48} height={150} fill={c.ink} />
      <path d={`M${SC.x + SC.w / 2 - 120} 800 L${SC.x + SC.w / 2 + 120} 800 L${SC.x + SC.w / 2 + 90} 780 L${SC.x + SC.w / 2 - 90} 780 Z`} fill={c.ink} />
      {/* light from the screen pooling on the desk */}
      <path d={`M${SC.x - 40} 812 L${SC.x + SC.w + 120} 812 L${SC.x + SC.w + 260} 1100 L${SC.x - 180} 1100 Z`} fill={c.redDeep} />
      {/* her: sweater with stripes, neck, profile face lit by the screen, bob, glasses, earring */}
      <path d="M1170 1100 C1180 790 1240 660 1335 648 C1445 640 1545 700 1590 820 L1650 1100 Z" fill="url(#stripeA)" />
      <path d="M1312 540 L1300 660 L1392 660 L1386 520 Z" fill={c.maroonDeep} />
      <path d="M1212 300 L1206 362 C1197 382 1186 402 1170 424 C1180 434 1195 436 1201 444 C1196 458 1191 468 1197 476 C1190 484 1189 494 1199 502 C1197 518 1201 534 1216 548 C1242 564 1282 568 1312 558 L1332 600 L1386 600 L1394 440 L1384 300 Z" fill={c.maroon} />
      <path d="M1212 300 L1206 362 C1197 382 1186 402 1170 424 C1180 434 1195 436 1201 444 C1196 458 1191 468 1197 476 C1190 484 1189 494 1199 502 C1197 518 1201 534 1216 548 C1242 564 1272 567 1292 562 C1262 522 1256 472 1264 432 C1270 382 1252 332 1242 300 Z" fill={c.cream} />
      <path d="M1194 476 C1188 482 1188 494 1200 501 C1206 494 1206 484 1194 476 Z" fill={c.lips} />
      <path d="M1180 300 C1180 196 1262 146 1344 146 C1446 146 1508 218 1508 322 L1514 566 C1476 582 1434 582 1404 566 L1394 470 L1384 330 L1196 336 C1196 322 1186 312 1180 300 Z" fill={c.ink} />
      <path d="M1192 338 C1196 250 1262 186 1346 182 L1350 340 Z" fill={c.ink} />
      <ellipse cx={1234} cy={376} rx={20} ry={26} fill={c.red} stroke={c.ink} strokeWidth={8} />
      <path d="M1250 368 L1392 352" stroke={c.ink} strokeWidth={8} />
      <circle cx={1404} cy={606} r={26} fill="none" stroke={c.peach} strokeWidth={9} />
      {/* desk, keyboard, mug */}
      <rect x={BLEED.x} y={800} width={BLEED.width} height={18} fill={c.peach} />
      <rect x={BLEED.x} y={818} width={BLEED.width} height={1600} fill={c.ink} />
      <path d={`M${SC.x + 60} 798 L${SC.x + 420} 798 L${SC.x + 400} 784 L${SC.x + 80} 784 Z`} fill={c.maroon} />
      <rect x={210} y={712} width={74} height={88} rx={8} fill={c.cream} />
      <path d="M284 730 C318 730 318 784 284 784" fill="none" stroke={c.cream} strokeWidth={12} />
      <rect x={210} y={712} width={36} height={88} fill={c.peach} />
      {/* arm resting on the desk, hand on the mouse */}
      <path d="M1330 690 C1250 720 1160 760 1090 782 L1098 800 L1350 800 C1380 760 1370 710 1330 690 Z" fill="url(#stripeA)" />
      <ellipse cx={1066} cy={792 + click * 0.3} rx={30} ry={10} fill={c.peach} />
      <path d={`M1046 ${784 + click} C1050 ${764 + click} 1086 ${762 + click} 1100 ${780 + click} L1100 800 L1046 800 Z`} fill={c.maroon} />
    </g>
  );
};

// ---------------- the logo card (pieces masked from the real logo, recoloured to the palette) ----------------
const LogoCard: React.FC<{ inner?: React.ReactNode; reveal?: number; id?: string }> = ({ inner, reveal = 0, id = "l" }) => {
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
      <rect {...BLEED} fill={cfg.cardBg} />
      {/* the circle and the dot are drawn as vectors so they stay crisp at any zoom */}
      <circle cx={L.circle.x + L.circle.w / 2} cy={L.circle.y + L.circle.h / 2} r={L.circle.w / 2 - 1.5} fill={L.circle.col} />
      {piece("p")}{piece("word")}{piece("tag")}
      <circle cx={DOT.cx} cy={DOT.cy} r={DOT.r + 1.4} fill={L.p.col} />
      <defs><clipPath id={`dot${id}`}><circle cx={DOT.cx} cy={DOT.cy} r={DOT.r + 1.4} /></clipPath></defs>
      {inner && reveal > 0 && <g clipPath={`url(#dot${id})`} opacity={reveal}>{inner}</g>}
    </g>
  );
};

// ---------------- one continuous zoom through the three portals ----------------
const DOT = cfg.dot, SUN = cfg.sun;
const HALF_DIAG = Math.hypot(CX, CY);
const PORTALS = [
  { P: { x: DOT.cx, y: DOT.cy }, K: (HALF_DIAG / (DOT.r + 1.4)) * 1.02 },  // logo -> designer
  { P: P_S, K: K_S },                                               // designer -> 3D world
  { P: { x: SUN.cx, y: SUN.cy }, K: (HALF_DIAG / SUN.r) * 1.02 },  // 3D world -> logo
];
const LN = PORTALS.map((p) => Math.log(p.K));
const CUM = [0, LN[0], LN[0] + LN[1], LN[0] + LN[1] + LN[2]];
const DUR = cfg.output.durationInFrames;
// knots (frame, log-zoom) with a periodic monotone cubic (Fritsch-Butland slopes): C1-smooth, never stops, and the
// speed at frame 449 matches the speed at frame 0, so the loop has no bump
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

// draw scene k with the next scenes nested inside its portal (depth-capped: deeper scenes are too small to see)
const Scene: React.FC<{ k: number; f: number; depth: number; reveal?: number }> = ({ k, f, depth, reveal = 0 }) => {
  const nextK = (k + 1) % 3, P = PORTALS[k];
  const inner = depth < 2 ? <g transform={into(P.P, P.K)}><Scene k={nextK} f={f} depth={depth + 1} /></g> : undefined;
  const id = `${k}_${depth}`;
  if (k === 0) return <LogoCard inner={inner} reveal={depth === 0 ? reveal : 0} id={id} />;
  if (k === 1) return <Designer f={f} inner={inner} id={id} />;
  return <World f={f} inner={inner} id={id} ui />;
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
