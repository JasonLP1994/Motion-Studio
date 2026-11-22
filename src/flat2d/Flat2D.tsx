import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { flatConfig as cfg } from "./config";

loadFont({ family: "Cinzel", url: staticFile("fonts/Cinzel.ttf") });

const W = cfg.output.width, H = cfg.output.height, CX = W / 2, CY = H / 2;
const c = cfg.col;
const MAXD = 3; // recursion depth cap (A -> B -> C -> A ...)
const BLEED = { x: -1400, y: -1400, w: W + 2800, h: H + 2800 };

// ---------- camera: hold with a slow push on the portal, then zoom through it ----------
// screen position of portal point P moves from P to the frame centre while the scale goes 1 -> push -> K
const camera = (f: number, start: number, end: number, P: { x: number; y: number }, K: number) => {
  const zs = end - cfg.t.zoom;
  let z: number, g: number;
  if (f < zs) {
    z = interpolate(f, [start, zs], [1, cfg.t.push], { easing: Easing.inOut(Easing.quad), extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    g = 0;
  } else {
    const e = interpolate(f, [zs, end], [0, 1], { easing: Easing.inOut(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const l0 = Math.log(cfg.t.push), l1 = Math.log(K);
    z = Math.exp(l0 + (l1 - l0) * e);
    g = (Math.log(z) - l0) / (l1 - l0);
  }
  const sx = P.x + (CX - P.x) * g, sy = P.y + (CY - P.y) * g;
  return { z, tr: `translate(${sx} ${sy}) scale(${z}) translate(${-P.x} ${-P.y})`, zoomT: f < zs ? 0 : (f - zs) / cfg.t.zoom };
};
// draw a full scene shrunk into a portal centred on P at scale 1/K
const into = (P: { x: number; y: number }, K: number) => `translate(${P.x} ${P.y}) scale(${1 / K}) translate(${-CX} ${-CY})`;

const L = cfg.lensNear, LF = cfg.lensFar, WN = cfg.window, HD = cfg.head;
const K_A = Math.sqrt((CX / L.rx) ** 2 + (CY / L.ry) ** 2) * 1.02;
const K_F = Math.sqrt((CX / LF.rx) ** 2 + (CY / LF.ry) ** 2) * 1.02;
const K_B = W / WN.w;
const K_C = 1 / HD.s;
const P_A = { x: L.cx, y: L.cy }, P_F = { x: LF.cx, y: LF.cy };
const P_B = { x: WN.x + WN.w / 2, y: WN.y + WN.h / 2 };
const P_C = { x: HD.x, y: HD.y };

const ease = (f: number, a: number, b: number, from = 0, to = 1, e = Easing.inOut(Easing.cubic)) =>
  interpolate(f, [a, b], [from, to], { easing: e, extrapolateLeft: "clamp", extrapolateRight: "clamp" });

type SP = { f: number; d: number; id: string; live?: boolean };

// ---------- Scene A pieces: the head (reused, shrunk, inside scene C) ----------
const Head: React.FC<SP> = ({ f, d, id, live }) => {
  const sw = live ? Math.sin(Math.max(0, f - cfg.t.glint[0]) / 9) * Math.exp(-Math.max(0, f - cfg.t.glint[0]) / 40) * 6 : 0; // earring settles after the head catches the light
  const glOn = live && f >= cfg.t.glint[0] && f <= cfg.t.glint[1];
  const gl = glOn ? ease(f, cfg.t.glint[0], cfg.t.glint[1], -280, 460, Easing.inOut(Easing.quad)) : -999;
  return (
    <g>
      <defs>
        <pattern id={`stripe${id}`} width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
          <rect width="26" height="26" fill={c.ink} />
          <rect width="7" height="26" fill={c.peach} />
        </pattern>
        <clipPath id={`lensN${id}`}><ellipse cx={L.cx} cy={L.cy} rx={L.rx} ry={L.ry} /></clipPath>
        <clipPath id={`lensF${id}`}><ellipse cx={LF.cx} cy={LF.cy} rx={LF.rx} ry={LF.ry} /></clipPath>
        <clipPath id={`lenses${id}`}>
          <ellipse cx={L.cx} cy={L.cy} rx={L.rx} ry={L.ry} /><ellipse cx={LF.cx} cy={LF.cy} rx={LF.rx} ry={LF.ry} />
        </clipPath>
      </defs>
      {/* hair, back */}
      <path d="M770 330 C760 170 900 78 1100 70 C1330 62 1482 190 1492 380 L1502 772 C1440 792 1380 792 1330 772 L1330 560 L900 560 L882 772 C830 788 790 782 760 762 Z" fill={c.ink} />
      {/* neck + coat with pinstripe and a scalloped collar */}
      <path d="M1030 700 L1030 960 L1236 960 L1236 690 Z" fill={c.maroonDeep} />
      <path d="M1236 800 L1236 960 L1160 960 Z" fill={c.ink} opacity={0.55} />
      <path d="M540 1110 C600 965 760 905 905 892 L1032 884 L1132 968 L1246 884 L1380 892 C1525 905 1680 965 1730 1110 Z" fill={`url(#stripe${id})`} />
      <path d="M1032 884 L1132 968 L1246 884 L1300 890 L1132 1020 L980 890 Z" fill={c.ink} />
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <path key={i} d={`M${975 + i * 52} ${905 + Math.abs(i - 2.5) * 6} a26 26 0 0 0 52 0`} fill="none" stroke={c.peach} strokeWidth={7} />
      ))}
      {/* face in shadow, light falling from the right as negative space */}
      <path d="M905 360 C895 520 915 650 985 745 C1040 815 1120 842 1190 816 C1275 786 1325 680 1335 540 L1335 360 Z" fill={c.maroon} />
      <path d="M1210 556 C1282 556 1330 586 1335 600 C1328 702 1282 792 1196 816 C1168 770 1206 722 1186 672 C1170 632 1176 590 1210 556 Z" fill={c.cream} />
      <path d="M1062 520 C1042 590 1030 622 1046 642 C1062 652 1084 650 1100 640" fill="none" stroke={c.ink} strokeWidth={8} strokeLinecap="round" />
      <path d="M1008 700 C1040 680 1064 690 1080 698 C1100 686 1126 690 1142 703 C1110 714 1040 716 1008 700 Z" fill={c.lips} />
      <path d="M1014 703 C1050 738 1112 738 1140 705 C1102 714 1050 714 1014 703 Z" fill={c.lips} />
      <path d="M1010 701 C1050 712 1100 712 1142 703" fill="none" stroke={c.ink} strokeWidth={4} />
      {/* blunt fringe */}
      <path d="M876 362 C896 250 1000 188 1120 186 C1252 184 1342 250 1352 362 L1352 408 L872 408 Z" fill={c.ink} />
      {/* reflections in the sunglasses: scene B (the near lens is the portal) */}
      <g clipPath={`url(#lensN${id})`}>
        <ellipse cx={L.cx} cy={L.cy} rx={L.rx} ry={L.ry} fill={c.red} />
        {d < MAXD && <g transform={into(P_A, K_A)}><SceneB f={f} d={d + 1} id={`${id}n`} /></g>}
      </g>
      <g clipPath={`url(#lensF${id})`}>
        <ellipse cx={LF.cx} cy={LF.cy} rx={LF.rx} ry={LF.ry} fill={c.red} />
        {d < MAXD && <g transform={into(P_F, K_F)}><SceneB f={f} d={d + 2} id={`${id}f`} /></g>}
      </g>
      {glOn && (
        <g clipPath={`url(#lenses${id})`}>
          <path d={`M${1050 + gl} 380 L${1100 + gl} 380 L${1000 + gl} 580 L${950 + gl} 580 Z`} fill={c.cream} opacity={0.85} />
          <path d={`M${1120 + gl} 380 L${1135 + gl} 380 L${1035 + gl} 580 L${1020 + gl} 580 Z`} fill={c.cream} opacity={0.85} />
        </g>
      )}
      {/* cat-eye frames */}
      <ellipse cx={L.cx} cy={L.cy} rx={L.rx} ry={L.ry} fill="none" stroke={c.ink} strokeWidth={16} />
      <ellipse cx={LF.cx} cy={LF.cy} rx={LF.rx} ry={LF.ry} fill="none" stroke={c.ink} strokeWidth={14} />
      <path d="M1290 418 L1362 384 L1330 458 Z" fill={c.ink} />
      <path d="M912 436 L872 404 L900 470 Z" fill={c.ink} />
      <path d="M1080 470 C1092 452 1108 452 1104 470" fill="none" stroke={c.ink} strokeWidth={12} />
      <path d="M1327 470 L1352 470" stroke={c.ink} strokeWidth={10} />
      {/* earring */}
      <g transform={`rotate(${sw} 1440 772)`}>
        <line x1={1440} y1={772} x2={1440} y2={792} stroke={c.peach} strokeWidth={6} />
        <circle cx={1440} cy={826} r={34} fill="none" stroke={c.peach} strokeWidth={11} />
      </g>
    </g>
  );
};

const SceneA: React.FC<SP> = (p) => (
  <g>
    <rect {...BLEED} fill={c.red} />
    <rect x={BLEED.x} y={BLEED.y} width={330 - BLEED.x} height={BLEED.h} fill={c.redDeep} />
    <rect x={352} y={BLEED.y} width={14} height={BLEED.h} fill={c.ink} />
    <rect x={1740} y={BLEED.y} width={W + 2000} height={BLEED.h} fill={c.redDeep} />
    <Head {...p} />
  </g>
);

// ---------- Scene B: art-deco hotel at dusk ----------
const SceneB: React.FC<SP> = ({ f, d, id, live }) => {
  if (d > MAXD) return <rect {...BLEED} fill={c.red} />;
  const cols = [690, 770, 905, 1095, 1175];
  const rows = Array.from({ length: 16 }, (_, i) => 330 + i * 112);
  const lit = (k: number) => live && f >= cfg.t.lights[k % cfg.t.lights.length];
  const litSet: Record<string, number> = { "1-3": 0, "4-5": 1, "0-6": 2, "3-2": 3, "1-7": 4 };
  const bx = live ? ease(f, cfg.t.birds[0], cfg.t.birds[1], -200, 2100, (x) => x) : -500;
  return (
    <g>
      <defs><clipPath id={`win${id}`}><rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} /></clipPath></defs>
      <rect {...BLEED} fill={c.red} />
      <circle cx={1500} cy={330} r={165} fill={c.cream} />
      {/* tower: setbacks, spire, shadow side */}
      <rect x={942} y={10} width={36} height={100} fill={c.peach} />
      <rect x={820} y={100} width={280} height={80} fill={c.peach} />
      <path d="M1100 100 L1150 118 L1150 180 L1100 180 Z" fill={c.maroon} />
      <rect x={720} y={170} width={480} height={100} fill={c.peach} />
      <path d="M1200 170 L1270 192 L1270 270 L1200 270 Z" fill={c.maroon} />
      <rect x={640} y={260} width={640} height={2400} fill={c.peach} />
      <path d="M1280 260 L1410 300 L1410 2660 L1280 2660 Z" fill={c.maroon} />
      {[660, 850, 1070, 1260].map((x) => <rect key={x} x={x} y={280} width={10} height={2380} fill={c.maroonDeep} />)}
      {[100, 170, 260].map((y) => <rect key={y} x={y === 100 ? 820 : y === 170 ? 720 : 640} y={y} width={y === 100 ? 280 : y === 170 ? 480 : 640} height={8} fill={c.maroonDeep} />)}
      {rows.map((y, r) => cols.map((x, k) => {
        if (x + 70 > WN.x - 20 && x < WN.x + WN.w + 20 && y + 60 > WN.y - 30 && y < WN.y + WN.h + 30) return null;
        const key = `${k}-${r}`; const on = key in litSet && lit(litSet[key]);
        return (
          <g key={key}>
            <rect x={x} y={y} width={x === 905 ? 110 : 60} height={62} fill={on ? c.cream : c.window} />
            <rect x={x} y={y} width={x === 905 ? 110 : 60} height={12} fill={c.maroonDeep} />
          </g>
        );
      }))}
      {/* the portal window with a little balcony: scene C lives inside */}
      <rect x={WN.x - 12} y={WN.y - 12} width={WN.w + 24} height={WN.h + 24} fill={c.maroonDeep} />
      <g clipPath={`url(#win${id})`}>
        <rect x={WN.x} y={WN.y} width={WN.w} height={WN.h} fill={c.window} />
        {d < MAXD && <g transform={into(P_B, K_B)}><SceneC f={f} d={d + 1} id={`${id}c`} /></g>}
      </g>
      <rect x={WN.x - 26} y={WN.y + WN.h + 8} width={WN.w + 52} height={10} fill={c.ink} />
      {[0, 1, 2, 3, 4, 5, 6].map((i) => <rect key={i} x={WN.x - 20 + i * 31} y={WN.y + WN.h + 18} width={5} height={30} fill={c.ink} />)}
      <rect x={WN.x - 26} y={WN.y + WN.h + 46} width={WN.w + 52} height={8} fill={c.ink} />
      {/* street and a low wall in the foreground */}
      <rect x={BLEED.x} y={1010} width={BLEED.w} height={2400} fill={c.maroonDeep} />
      {/* birds */}
      {live && [0, 1, 2].map((i) => {
        const x = bx - i * 70, y = 210 + i * 34 + Math.sin((f + i * 7) / 4) * 4, w = Math.sin((f + i * 5) / 3) > 0 ? 14 : 4;
        return <path key={i} d={`M${x - 22} ${y - w} L${x} ${y} L${x + 22} ${y - w}`} fill="none" stroke={c.ink} strokeWidth={6} strokeLinejoin="round" />;
      })}
    </g>
  );
};

// ---------- Scene C: inside the window, she raises a glass ----------
const SceneC: React.FC<SP> = ({ f, d, id, live }) => {
  if (d > MAXD) return <rect {...BLEED} fill={c.window} />;
  const gy = live ? ease(f, cfg.t.glass[0], cfg.t.glass[1], 90, 0, Easing.bezier(0.33, 1, 0.68, 1)) : 0;
  const hs = `translate(${HD.x} ${HD.y}) scale(${HD.s}) translate(${-CX} ${-CY})`;
  return (
    <g>
      <rect {...BLEED} fill={c.red} />
      {/* a tall cream light pool on the back wall, the room's one light */}
      <path d="M1000 -100 L1500 -100 L1640 1300 L860 1300 Z" fill={c.redDeep} />
      {/* dress, then the shared head (identical to scene A, shrunk) */}
      <path d="M1022 520 C1000 640 960 820 930 1500 L1490 1500 C1460 820 1420 640 1398 520 Z" fill={c.ink} />
      <path d="M1200 540 L1270 540 L1236 640 Z" fill={c.maroonDeep} />
      <g transform={hs}><Head f={f} d={d} id={`${id}h`} /></g>
      {/* arm and cocktail glass */}
      <g transform={`translate(0 ${gy})`}>
        <path d="M1035 760 C1060 700 1090 650 1110 610 L1140 622 C1120 668 1096 720 1076 774 Z" fill={c.maroon} />
        <path d="M1062 512 L1158 512 L1110 566 Z" fill={c.lips} stroke={c.cream} strokeWidth={6} strokeLinejoin="round" />
        <line x1={1110} y1={566} x2={1110} y2={614} stroke={c.cream} strokeWidth={6} />
        <line x1={1088} y1={616} x2={1132} y2={616} stroke={c.cream} strokeWidth={6} strokeLinecap="round" />
        <circle cx={1128} cy={606} r={18} fill={c.maroon} />
      </g>
      {/* curtain on the right with peach folds */}
      <path d="M1640 -200 C1700 300 1660 700 1730 1400 L2600 1400 L2600 -200 Z" fill={c.maroonDeep} />
      {[0, 1, 2, 3].map((i) => <path key={i} d={`M${1720 + i * 60} -200 C${1770 + i * 60} 300 ${1730 + i * 60} 700 ${1800 + i * 60} 1400`} fill="none" stroke={c.peach} strokeWidth={6} />)}
      {/* window sill in the foreground */}
      <rect x={BLEED.x} y={980} width={BLEED.w} height={40} fill={c.ink} />
      <rect x={BLEED.x} y={1020} width={BLEED.w} height={2400} fill={c.peach} />
    </g>
  );
};

// ---------- the film ----------
export const Flat2D: React.FC = () => {
  const f = useCurrentFrame();
  const { A, B, C } = cfg.t;
  let content: React.ReactNode;
  if (f < A[1]) {
    const cam = camera(f, A[0], A[1], P_A, K_A);
    content = <g transform={cam.tr}><SceneA f={f} d={0} id="a" live /></g>;
  } else if (f < B[1]) {
    const cam = camera(f, B[0], B[1], P_B, K_B);
    content = <g transform={cam.tr}><SceneB f={f} d={0} id="b" live /></g>;
  } else {
    const cam = camera(f, C[0], C[1], P_C, K_C);
    const op = ease(cam.zoomT, 1 - cfg.t.dissolve, 1, 0, 1, Easing.inOut(Easing.quad));
    content = (
      <g transform={cam.tr}>
        <SceneC f={f} d={0} id="c" live />
        {op > 0 && <g opacity={op} transform={into(P_C, K_C)}><SceneA f={0} d={1} id="ca" /></g>}
      </g>
    );
  }
  const T = cfg.title, ti = cfg.t.title;
  const tIn = ease(f, ti.in, ti.in + 10, 0, 1, Easing.out(Easing.exp));
  const tOut = ease(f, ti.out, ti.out + 6, 1, 0, Easing.in(Easing.cubic));
  const tOp = Math.min(tIn, tOut);
  return (
    <AbsoluteFill style={{ backgroundColor: c.red }}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%">{content}</svg>
      {T.text && tOp > 0 && (
        <div style={{ position: "absolute", left: T.x, top: T.y, color: T.color, fontFamily: T.font, fontSize: T.size, letterSpacing: "0.12em", lineHeight: 1, opacity: tOp, filter: `blur(${(1 - tIn) * 6 + (1 - tOut) * 6}px)` }}>
          {T.text}
          {T.sub && <div style={{ fontSize: T.size * 0.32, letterSpacing: "0.4em", marginTop: 24 }}>{T.sub}</div>}
        </div>
      )}
    </AbsoluteFill>
  );
};
