import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { redConfig as K, C, Ev, Kind, Scene, timeline as TL } from "./config";
import EDGES from "./top-edges.json";

loadFont({ family: K.monoFont, url: staticFile("fonts/LiberationMono-Bold.ttf") });

const W = K.output.width;
const H = K.output.height;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};
const burstOn = (local: number) => K.flicker[local % K.flicker.length] === 1;
const img = (s: Scene, suffix = "") => `ferrari/${s.name}${suffix}.png`;
// Paper-white version (user): cars are SAM 2 cut-outs; pixelated versions come from the cut-outs too.
const cut = (s: Scene, suffix = "") => `ferrari/${s.name}-cut${suffix}.png`;
const BG = C.paper;
const INK = C.black;
const SHADOW = "drop-shadow(0 22px 26px rgba(0,0,0,0.35))";
const sceneByName = (n: string) => K.scenes.find((s) => s.name === n) as Scene;

type Box = { x: number; y: number; w: number; h: number };
const boxOf = (s: Scene): Box => {
  const k = s.fit === "cover" ? Math.max(W / s.w, H / s.h) : W / s.w;
  return { x: (W - s.w * k) / 2, y: (H - s.h * k) / 2, w: s.w * k, h: s.h * k };
};

// ---------- pixel font ----------
const FONT: Record<string, string[]> = {
  P: ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
  H: ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
  I: ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
  L: ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
  S: ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
  D: ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
  G: ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
  T: ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
  A: ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
  " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
};
const cellsOf = (text: string) => {
  const out: [number, number][] = [];
  text.split("").forEach((ch, k) => (FONT[ch] ?? FONT[" "]).forEach((row, r) => row.split("").forEach((b, c) => b === "1" && out.push([k * 6 + c, r]))));
  return out;
};
const PixelText: React.FC<{ text: string; cell: number; cx: number; cy: number; ink: string; rowShift?: (r: number) => number }> = ({ text, cell, cx, cy, ink, rowShift }) => {
  const x0 = cx - ((text.length * 6 - 1) * cell) / 2;
  const y0 = cy - (7 * cell) / 2;
  return (
    <>
      {cellsOf(text).map(([c, r], i) => (
        <rect key={i} x={x0 + c * cell + (rowShift?.(r) ?? 0)} y={y0 + r * cell} width={cell * 0.84} height={cell * 0.84} fill={ink} />
      ))}
    </>
  );
};

// ---------- base + effects ----------
const Photo: React.FC<{ src: string; b: Box; style?: React.CSSProperties }> = ({ src, b, style }) => (
  <Img src={staticFile(src)} style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, ...style }} />
);

// Channel filters for the RGB split (defined once, used through CSS filter: url(#...)).
const ChannelDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="chR"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="chG"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="chB"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" /></filter>
  </svg>
);

// Print-style misregistration split on paper: solid red and black silhouettes of the car, offset in
// opposite directions behind the untouched car, so only their edges show (stays red / black / white).
const Silhouette: React.FC<{ s: Scene; b: Box; color: string; dx: number; dy: number }> = ({ s, b, color, dx, dy }) => {
  const url = `url(${staticFile(cut(s))})`; // the cut-out's own alpha shapes the silhouette
  return (
    <div
      style={{
        position: "absolute", left: b.x + dx, top: b.y + dy, width: b.w, height: b.h, background: color,
        WebkitMaskImage: url, maskImage: url, WebkitMaskSize: "100% 100%", maskSize: "100% 100%",
      }}
    />
  );
};
const RGBSplit: React.FC<{ s: Scene; b: Box; seed: number }> = ({ s, b, seed }) => {
  const o = (k: number) => (rnd(seed + k * 3.1) > 0.5 ? 1 : -1) * (26 + rnd(seed + k) * 40); // always a visible offset
  return (
    <AbsoluteFill style={{ background: BG }}>
      <Silhouette s={s} b={b} color={C.red} dx={o(1)} dy={o(2) * 0.35} />
      <Silhouette s={s} b={b} color={INK} dx={-o(1) * 0.8} dy={-o(2) * 0.3} />
      <Photo src={cut(s)} b={b} />
    </AbsoluteFill>
  );
};

// Constant low-level chaos: on ~45% of frames, 1-3 thin strips of the frame jump sideways.
const JitterBands: React.FC<{ s: Scene; b: Box; frame: number }> = ({ s, b, frame }) => {
  if (rnd(frame * 0.91) > 0.45) return null;
  const n = 1 + Math.floor(rnd(frame * 1.31) * 3);
  return (
    <>
      {Array.from({ length: n }).map((_, i) => {
        const k = frame * 7 + i;
        const y = rnd(k) * H;
        const h = 6 + rnd(k + 1) * 50;
        const dx = (rnd(k + 2) - 0.5) * 260;
        return (
          <div key={i} style={{ position: "absolute", left: 0, top: y, width: W, height: h, overflow: "hidden", background: BG }}>
            <Photo src={cut(s)} b={{ ...b, x: b.x + dx, y: b.y - y }} />
          </div>
        );
      })}
    </>
  );
};

const Shuffle: React.FC<{ s: Scene; b: Box; seed: number }> = ({ s, b, seed }) => {
  const bs = 120;
  const cols = Math.ceil(W / bs);
  const rows = Math.ceil(H / bs);
  const cells = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      const k = seed * 997 + r * 41 + c;
      if (rnd(k) > 0.38) continue;
      const dx = Math.round((rnd(k + 1) - 0.5) * 8) * bs;
      const dy = Math.round((rnd(k + 2) - 0.5) * 4) * bs;
      cells.push(
        <div key={k} style={{ position: "absolute", left: c * bs, top: r * bs, width: bs, height: bs, overflow: "hidden", background: BG }}>
          <Photo src={rnd(k + 3) > 0.75 ? cut(s, "-mosaic_16") : cut(s)} b={{ ...b, x: b.x - c * bs + dx, y: b.y - r * bs + dy }} />
        </div>,
      );
    }
  return <>{cells}</>;
};

// Horizontal pixel smears: a 1-px slice of the photo stretched into a streak.
const Smear: React.FC<{ s: Scene; b: Box; seed: number }> = ({ s, b, seed }) => (
  <>
    {Array.from({ length: 9 }).map((_, i) => {
      const k = seed * 53 + i;
      const y = rnd(k) * H;
      const bh = 8 + rnd(k + 1) * 70;
      const x0 = rnd(k + 2) * W * 0.7;
      const stretch = 260;
      return (
        <div key={i} style={{ position: "absolute", left: x0, top: y, width: W - x0, height: bh, overflow: "hidden" }}>
          <Img src={staticFile(cut(s))} style={{ position: "absolute", left: -(x0 - b.x) * stretch, top: b.y - y, width: b.w * stretch, height: b.h }} />
        </div>
      );
    })}
  </>
);

const InPaint: React.FC<{ children: React.ReactNode; id: string; s: Scene; b: Box }> = ({ children, id, s, b }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
    <defs>
      <mask id={`${id}-m`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
        <image href={staticFile(img(s, "-mask"))} x={b.x} y={b.y} width={b.w} height={b.h} preserveAspectRatio="none" />
      </mask>
      <pattern id={`${id}-dR`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.red} />
        <rect x={4} y={4} width={4} height={4} fill={C.red} />
      </pattern>
      <pattern id={`${id}-dK`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.black} />
        <rect x={4} y={4} width={4} height={4} fill={C.black} />
      </pattern>
    </defs>
    <g mask={`url(#${id}-m)`}>{children}</g>
  </svg>
);

// Big pixel letter in white with red dither, over a pixelated frame.
const Glyph: React.FC<{ ch: string; s: Scene; b: Box; seed: number }> = ({ ch, s, b, seed }) => {
  const cell = H / 7.6;
  const x0 = W / 2 - (5 * cell) / 2 + (rnd(seed) - 0.5) * 700;
  const y0 = (H - 7 * cell) / 2;
  return (
    <>
      <Photo src={cut(s, "-mosaic_18")} b={b} />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <pattern id={`gd${seed}`} width={8} height={8} patternUnits="userSpaceOnUse">
            <rect width={4} height={4} fill={C.red} />
            <rect x={4} y={4} width={4} height={4} fill={C.red} />
          </pattern>
        </defs>
        {cellsOf(ch).map(([c, r], i) => (
          <g key={i}>
            <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={INK} />
            {rnd(i + seed) > 0.7 && <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={`url(#gd${seed})`} />}
          </g>
        ))}
      </svg>
    </>
  );
};

const Flood: React.FC<{ s: Scene; b: Box; seed: number }> = ({ s, b, seed }) => (
  <InPaint id={`f${seed}`} s={s} b={b}>
    <rect width={W} height={H} fill={C.white} />
    <rect x={W * (0.3 + rnd(seed) * 0.4)} width={W} height={H} fill={`url(#f${seed}-dK)`} opacity={0.9} />
  </InPaint>
);

const Strobe: React.FC<{ ink: string; lines?: boolean; seed: number }> = ({ ink, lines, seed }) => (
  <AbsoluteFill style={{ background: ink }}>
    {lines && (
      <svg width={W} height={H}>
        {Array.from({ length: 60 }).map((_, i) => (
          <rect key={i} x={rnd(seed + i) * W * 0.5} y={i * 18 + 6} width={W * (0.2 + rnd(seed + i + 70) * 0.8)} height={3} fill={ink === C.red ? C.black : C.red} opacity={0.9} />
        ))}
      </svg>
    )}
  </AbsoluteFill>
);

const Tear: React.FC<{ s: Scene; b: Box; seed: number; t: number }> = ({ s, b, seed, t }) => {
  const strips = 40;
  const sh = H / strips;
  return (
    <AbsoluteFill style={{ background: BG }}>
      {Array.from({ length: strips }).map((_, i) => {
        const big = rnd(seed * 7 + i) > 0.6;
        const dx = (rnd(seed * 13 + i + t * 3) - 0.5) * (big ? 1100 : 160);
        return (
          <div key={i} style={{ position: "absolute", left: 0, top: i * sh, width: W, height: sh + 1, overflow: "hidden" }}>
            <div style={{ position: "absolute", left: dx, top: -i * sh, width: W, height: H }}>
              <Photo src={cut(s)} b={b} />
            </div>
            {rnd(seed + i * 3) > 0.5 && <div style={{ position: "absolute", left: rnd(i + seed) * W * 0.4, top: sh / 2, width: W * rnd(i * 5 + seed), height: 2, background: INK }} />}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const PatternFull: React.FC<{ s: Scene; b: Box; v: number; zoom?: number; fx?: number; fy?: number }> = ({ s, b, v, zoom = 1, fx = 0.5, fy = 0.5 }) => {
  const w = b.w * zoom;
  const h = b.h * zoom;
  const box = zoom === 1 ? b : { x: W / 2 - fx * w, y: H / 2 - fy * h, w, h };
  return (
    <AbsoluteFill style={{ background: C.paper, overflow: "hidden" }}>
      <Photo src={img(s, `-pattern_${v}`)} b={box} style={{ imageRendering: "pixelated" }} />
    </AbsoluteFill>
  );
};

const Brackets: React.FC = () => {
  const s = K.pixel;
  const pts: [number, number, number, number][] = [[60, 60, 1, 1], [W - 60, 60, -1, 1], [60, H - 60, 1, -1], [W - 60, H - 60, -1, -1]];
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {pts.map(([x, y, dx, dy], k) =>
        Array.from({ length: 6 }).flatMap((_, i) => [
          <rect key={`${k}h${i}`} x={x + dx * i * s - (dx < 0 ? s : 0)} y={y - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={INK} />,
          <rect key={`${k}v${i}`} x={x - (dx < 0 ? s : 0)} y={y + dy * i * s - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={INK} />,
        ]),
      )}
    </svg>
  );
};

const Readout: React.FC<{ text: string; t: number; corner: "tl" | "tr" | "br" }> = ({ text, t, corner }) => (
  <div
    style={{
      position: "absolute",
      [corner[0] === "t" ? "top" : "bottom"]: 46,
      [corner[1] === "l" ? "left" : "right"]: 56,
      fontFamily: K.monoFont,
      fontSize: 20,
      letterSpacing: "0.08em",
      color: INK,
      whiteSpace: "pre",
    }}
  >
    {text.slice(0, Math.max(0, Math.floor(t * 1.5)))}
    {t % 10 < 5 ? "█" : " "}
  </div>
);

// ---------- white digital annotations ----------
type Anno = { kind: string; at: number; life: number; x: number; y: number; dir: number; label: string; seed: number };
const annosFor = (len: number, n: number): Anno[] => {
  const A = K.annotations;
  const all = Array.from({ length: A.perScene }).map((_, k) => {
    const r = (j: number) => rnd(n * 977 + k * 31 + j);
    const x = 160 + r(1) * (W - 320);
    const y = 170 + r(2) * (H - 340);
    return { kind: A.kinds[Math.floor(r(3) * A.kinds.length)], at: 9 * Math.floor(r(4) * (len - 1)) + (k % 3 === 0 ? 4 : 0), life: Math.round(A.life[0] + r(5) * (A.life[1] - A.life[0])), x, y, dir: x < W / 2 ? -1 : 1, label: A.labels[Math.floor(r(6) * A.labels.length)], seed: n * 100 + k };
  });
  const kept: Anno[] = [];
  for (const a of all) if (!kept.some((o) => a.at < o.at + o.life && o.at < a.at + a.life && Math.hypot(a.x - o.x, a.y - o.y) < A.minGap)) kept.push(a);
  return kept;
};
const coord = (v: number) => String(Math.round(v)).padStart(4, "0");
const AnnoView: React.FC<{ a: Anno; t: number; frame: number }> = ({ a, t, frame }) => {
  const A = K.annotations;
  const local = t - a.at;
  if (local < 0 || local >= a.life || local === 1 || local === a.life - 2) return null;
  const draw = Math.min(1, (local + 1) / A.lineFrames);
  const typed = (txt: string, d = 0) => txt.slice(0, Math.max(0, Math.floor((local - d) * 2.4)));
  const label = a.label.replace("{f}", String(frame).padStart(4, "0"));
  const st = { stroke: INK, strokeWidth: A.stroke, fill: "none" } as const;
  const txt = (x: number, y: number, v: string, anchor: "start" | "end" | "middle", size = A.fontSize) => (
    <text x={x} y={y} fill={INK} fontFamily={K.monoFont} fontSize={size} letterSpacing="0.06em" textAnchor={anchor}>{v}</text>
  );
  if (a.kind === "callout") {
    const ex = a.x + a.dir * 80, ey = a.y - 80, hx = ex + a.dir * 210;
    return (
      <g>
        <rect x={a.x - 8} y={a.y - 8} width={16} height={16} {...st} />
        <path d={`M${a.x} ${a.y} L${ex} ${ey} L${hx} ${ey}`} {...st} pathLength={1} strokeDasharray={`${draw} 1`} />
        {draw >= 1 && txt(hx, ey - 12, typed(label), a.dir > 0 ? "end" : "start")}
        {draw >= 1 && txt(hx, ey + 28, typed(`X${coord(a.x)} Y${coord(a.y)}`, 3), a.dir > 0 ? "end" : "start", A.fontSize - 3)}
      </g>
    );
  }
  if (a.kind === "reticle") {
    const r = 40 + 16 * draw;
    return (
      <g>
        <circle cx={a.x} cy={a.y} r={r} {...st} />
        {[0, 90, 180, 270].map((d) => {
          const c = Math.cos((d * Math.PI) / 180), s2 = Math.sin((d * Math.PI) / 180);
          return <line key={d} x1={a.x + c * (r - 10)} y1={a.y + s2 * (r - 10)} x2={a.x + c * (r + 12)} y2={a.y + s2 * (r + 12)} {...st} />;
        })}
        <rect x={a.x - 2} y={a.y - 2} width={4} height={4} fill={INK} />
        {txt(a.x + r + 18, a.y + 5, typed(`TRK ${label}`), "start")}
      </g>
    );
  }
  if (a.kind === "dimension") {
    const len = 180 + rnd(a.seed + 9) * 220;
    const x0 = Math.max(80, Math.min(W - 80 - len, a.x - len / 2));
    return (
      <g>
        <line x1={x0} y1={a.y - 10} x2={x0} y2={a.y + 10} {...st} />
        <line x1={x0} y1={a.y} x2={x0 + len * draw} y2={a.y} {...st} />
        {draw >= 1 && <line x1={x0 + len} y1={a.y - 10} x2={x0 + len} y2={a.y + 10} {...st} />}
        {draw >= 1 && txt(x0 + len / 2, a.y - 14, typed(`${Math.round(len)} PX`), "middle")}
      </g>
    );
  }
  return (
    <g>
      {[0, 1, 2].map((i) => (
        <g key={i} opacity={local > i ? 1 : 0}>
          <line x1={a.x + i * 44 - 12} y1={a.y} x2={a.x + i * 44 + 12} y2={a.y} {...st} />
          <line x1={a.x + i * 44} y1={a.y - 12} x2={a.x + i * 44} y2={a.y + 12} {...st} />
        </g>
      ))}
      {txt(a.x - 12, a.y + 40, typed(`${coord(a.x)}.${coord(a.y)}`, 2), "start", A.fontSize - 3)}
    </g>
  );
};

// ---------- Node network frame ----------
const NodesLayer: React.FC<{ s: Scene; b: Box; t: number }> = ({ s, b, t }) => {
  const N = K.nodes;
  const k = b.w / s.w;
  const X = (x: number) => b.x + x * k;
  const Y = (y: number) => b.y + y * k;
  const E = EDGES.edges as [number, number, number][];
  const step = EDGES.step * k;
  const reveal = interpolate(t, [0, 8], [0, 1], clamp);
  const cy = Y((E.reduce((a, e) => a + e[1] + e[2], 0) / E.length) / 2);
  const cx = X((E[0][0] + E[E.length - 1][0]) / 2);
  const bars = E.flatMap(([x, yt, yb], i) => {
    if (i / E.length > reveal) return [];
    const out = [];
    for (const side of [0, 1]) {
      const r = rnd(i * 7 + side * 131);
      if (r < 0.25) continue;
      const h = 16 + rnd(i * 3 + side * 17) * 54;
      const fill = r > 0.85 ? "#8A8A8A" : INK;
      out.push(<rect key={`${i}-${side}`} x={X(x) - step / 2} y={side ? Y(yb) - h : Y(yt)} width={step * 0.92} height={h} fill={fill} />);
    }
    return out;
  });
  const pts = N.picks.map((p, i) => {
    const e = E[Math.round(p * (E.length - 1))];
    return { x: X(e[0]), y: N.sides[i] === "top" ? Y(e[1]) + 10 : Y(e[2]) - 10, side: N.sides[i] };
  });
  const showName = t >= 6 && !(t === 7 || t === 9);
  const codeLines = (lines: string[], d: number) => lines.slice(0, Math.max(0, Math.floor((t - d) / 1.2)));
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {bars}
      {pts.slice(0, -1).map((p, i) => {
        const q = pts[i + 1];
        const start = (i + 1) * N.nodeEvery + 4;
        const draw = interpolate(t, [start, start + N.wireFrames], [0, 1], clamp);
        if (draw <= 0) return null;
        const d = `M${p.x} ${p.y} C${p.x + 160} ${cy + (i % 2 ? -140 : 140)} ${q.x - 160} ${cy + (i % 2 ? 140 : -140)} ${q.x} ${q.y}`;
        return <path key={i} d={d} fill="none" stroke={INK} strokeWidth={2.5} pathLength={1} strokeDasharray={`${draw} 1`} opacity={0.9} />;
      })}
      {showName && (
        <g>
          <rect x={cx - 330} y={cy - 70} width={660} height={140} fill="#8A8A8A" />
          <text x={cx} y={cy + 38} textAnchor="middle" fill={C.white} fontFamily={K.monoFont} fontSize={104} letterSpacing="0.12em">
            {N.name}
          </text>
        </g>
      )}
      {pts.map((p, i) => {
        const at = i * N.nodeEvery + 4;
        if (t < at || t === at + 1) return null;
        const ly = p.side === "top" ? p.y - 64 : p.y + 24;
        return (
          <g key={`n${i}`}>
            <rect x={p.x - 9} y={p.y - 9} width={18} height={18} fill={INK} />
            <line x1={p.x} y1={p.y} x2={p.x + 22} y2={ly + 20} stroke={INK} strokeWidth={2} />
            <rect x={p.x + 22} y={ly} width={150} height={40} fill={C.red} />
            <text x={p.x + 34} y={ly + 28} fill={C.white} fontFamily={K.monoFont} fontSize={24}>
              {N.labels[i].slice(0, Math.max(0, Math.floor((t - at) * 2.5)))}
            </text>
          </g>
        );
      })}
      {N.code.map((lines, j) => (
        <text key={`c${j}`} fill={INK} fontFamily={K.monoFont} fontSize={17} opacity={0.92}>
          {codeLines(lines, 6 + j * 8).map((ln, i) => (
            <tspan key={i} x={j === 0 ? W - 520 : W - 560} y={(j === 0 ? 150 : 700) + i * 24}>
              {ln}
            </tspan>
          ))}
        </text>
      ))}
    </svg>
  );
};

// ---------- one shot (a scene, or a montage slot) ----------
const FULL: Kind[] = ["strobe", "tear", "patternZoom", "rgb", "pattern"];

const Shot: React.FC<{ s: Scene; t: number; events: Ev[]; n: number; frame: number; annoLen: number; showUi: boolean }> = ({ s, t, events, n, frame, annoLen, showUi }) => {
  const b = boxOf(s);
  const active = events.map((e, i) => ({ e, i: n * 100 + i })).filter(({ e }) => t >= e.at && t < e.at + e.len && (e.kind === "brackets" || burstOn(t - e.at)));
  const has = (k: Kind) => active.find(({ e }) => e.kind === k);
  const full = active.some(({ e }) => FULL.includes(e.kind));
  const inverted = !!has("invert");
  // zoom punch on every 8th, shake while anything is bursting
  const P = K.punch;
  const sinceBeat = frame % P.every;
  const punch = 1 + P.amount * interpolate(sinceBeat, [0, P.frames], [1, 0], clamp);
  const shake = active.length ? P.shake : 0;
  const sx = (rnd(frame * 1.7) - 0.5) * 2 * shake;
  const sy = (rnd(frame * 2.3) - 0.5) * 2 * shake;
  const layer = (e: Ev, i: number) => {
    const local = t - e.at;
    switch (e.kind) {
      case "glyph": return <Glyph key={i} ch={e.ch ?? "P"} s={s} b={b} seed={i + 1} />;
      case "flood": return <Flood key={i} s={s} b={b} seed={i + 1} />;
      case "shuffle": return <Shuffle key={i} s={s} b={b} seed={i + 1 + local} />;
      case "smear": return <Smear key={i} s={s} b={b} seed={i + 1 + local} />;
      case "rgb": return <RGBSplit key={i} s={s} b={b} seed={i * 7 + local} />;
      case "strobe": return <Strobe key={i} ink={e.ink === "white" ? C.white : e.ink === "black" ? C.black : C.red} lines={e.lines} seed={i + local} />;
      case "tear": return <Tear key={i} s={s} b={b} seed={i + 1} t={local} />;
      case "pattern": return <PatternFull key={i} s={s} b={b} v={e.v ?? 1} />;
      case "patternZoom": return <PatternFull key={i} s={s} b={b} v={e.v ?? 1} zoom={e.zoom} fx={e.fx} fy={e.fy} />;
      case "brackets": return <Brackets key={i} />;
      case "dots": return <svg key={i} width={W} height={H} style={{ position: "absolute", inset: 0 }}><PixelText text={e.text ?? "PD"} cell={40} cx={W / 2} cy={H / 2} ink={INK} /></svg>;
      case "brand": return <svg key={i} width={W} height={H} style={{ position: "absolute", inset: 0 }}><PixelText text={K.words.brand} cell={20} cx={W / 2} cy={H / 2} ink={C.red} /></svg>;
      default: return null;
    }
  };
  return (
    <AbsoluteFill style={{ filter: inverted ? "grayscale(1) invert(1) contrast(1.5)" : undefined }}>
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px) scale(${punch})` }}>
        <AbsoluteFill style={{ background: BG }} />
        <Photo src={cut(s)} b={b} style={{ filter: SHADOW }} />
        {!s.nodes && !full && <JitterBands s={s} b={b} frame={frame} />}
        {s.nodes && <NodesLayer s={s} b={b} t={t} />}
        {active.map(({ e, i }) => layer(e, i))}
      </AbsoluteFill>
      {showUi && !full && (
        <>
          {!s.nodes && (
            <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
              {annosFor(annoLen, n).map((a, i) => <AnnoView key={i} a={a} t={t} frame={frame} />)}
            </svg>
          )}
          <Readout text={K.words.file} t={t} corner="tl" />
          <Readout text={K.words.view.replace("{n}", String(n + 1).padStart(2, "0"))} t={t - 4} corner="tr" />
          <Readout text={s.readout} t={t - 12} corner="br" />
        </>
      )}
    </AbsoluteFill>
  );
};

// Montage: one photo per 16th with a random glitch stacked on each slot.
const montageSlots = (() => {
  const M = K.montage;
  const total = M.len * 9;
  const slots: { at: number; len: number; scene: Scene; ev: Ev }[] = [];
  for (let k = 0, a = 0; a < total; k++) {
    const next = Math.round((k + 1) * 4.5);
    const kind = M.kinds[Math.floor(rnd(k * 19 + 5) * M.kinds.length)];
    slots.push({ at: a, len: next - a, scene: sceneByName(M.order[k % M.order.length]), ev: { kind, at: 0, len: next - a, v: 1 + (k % 2), ink: k % 2 ? "black" : "red", lines: true } });
    a = next;
  }
  return slots;
})();

// ---------- end ----------
const Dissolve: React.FC<{ f: number }> = ({ f }) => {
  const s = montageSlots[montageSlots.length - 1].scene;
  const b = boxOf(s);
  const p = (f - TL.dissolve) / K.dissolveFrames;
  const stage = p < 0.25 ? 16 : p < 0.5 ? 32 : 64;
  const drop = interpolate(p, [0.4, 1], [0, 1], clamp);
  const bs = 96;
  const cols = Math.ceil(W / bs), rows = Math.ceil(H / bs);
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <mask id="drop" maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          {Array.from({ length: rows * cols }).map((_, k) => (rnd(k * 3.7) >= drop ? <rect key={k} x={(k % cols) * bs} y={Math.floor(k / cols) * bs} width={bs + 1} height={bs + 1} fill="#fff" /> : null))}
        </mask>
      </defs>
      <image href={staticFile(cut(s, `-mosaic_${stage}`))} x={b.x} y={b.y} width={b.w} height={b.h} mask="url(#drop)" preserveAspectRatio="none" />
    </svg>
  );
};

const EndMark: React.FC<{ f: number }> = ({ f }) => {
  const E = K.end;
  const t = f - TL.end;
  const glitching = t < E.glitchFrames;
  if (glitching && !burstOn(t)) return null;
  const shift = (r: number) => (glitching ? (rnd(r * 11 + t * 5) - 0.5) * 160 * (rnd(r + t) > 0.45 ? 1 : 0) : 0);
  const ink = glitching && t % 3 === 1 ? INK : C.red;
  return (
    <>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <PixelText text="PHILLIPS" cell={E.pixel} cx={W / 2} cy={H / 2 - 95} ink={ink} rowShift={shift} />
        <PixelText text="DIGITAL" cell={E.pixel} cx={W / 2} cy={H / 2 + 95} ink={ink} rowShift={(r) => shift(r + 9)} />
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: H / 2 + 235, textAlign: "center", fontFamily: K.monoFont, fontSize: 26, letterSpacing: "0.3em", color: INK }}>
        {K.words.restored.slice(0, Math.max(0, Math.floor((t - E.restoredDelay) * 1.2)))}
      </div>
    </>
  );
};

// Faint paper grain over everything (static, like printed stock).
const PaperGrain: React.FC = () => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.16, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id="grainP" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1} seed={3} />
      <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.2 0 0 0 0.9" />
    </filter>
    <rect width={W} height={H} filter="url(#grainP)" />
  </svg>
);

export const RedGlitch: React.FC = () => {
  const f = useCurrentFrame();
  const n = TL.starts.findIndex((a, k) => f >= a && f < (k === TL.starts.length - 1 ? TL.montage : TL.starts[k + 1]));
  const slot = f >= TL.montage && f < TL.dissolve ? montageSlots.find((sl) => f - TL.montage >= sl.at && f - TL.montage < sl.at + sl.len) : undefined;
  const fade = interpolate(f, [TL.dissolve, TL.end], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: BG }}>
      <ChannelDefs />
      {n >= 0 && <Shot s={K.scenes[n]} t={f - TL.starts[n]} events={K.scenes[n].events} n={n} frame={f} annoLen={K.scenes[n].len} showUi />}
      {slot && <Shot s={slot.scene} t={f - TL.montage - slot.at} events={[slot.ev]} n={9} frame={f} annoLen={1} showUi={false} />}
      {f >= TL.dissolve && f < TL.end && <Dissolve f={f} />}
      {f >= TL.dissolve && <AbsoluteFill style={{ background: BG, opacity: fade }} />}
      <PaperGrain />
      {f >= TL.end && <EndMark f={f} />}

      <Audio src={staticFile(K.audio.music)} volume={K.audio.musicVolume} />
      {K.scenes.flatMap((s, si) =>
        s.events.map((e, i) => {
          const list = K.audio.sfx[e.kind] ?? [];
          if (!list.length) return null;
          return (
            <Sequence key={`${si}-${i}`} from={TL.starts[si] + e.at} durationInFrames={e.len + 2}>
              <Audio src={staticFile(list[(si + i) % list.length])} volume={K.audio.sfxVolume} />
            </Sequence>
          );
        }),
      )}
      <Sequence from={TL.montage} durationInFrames={TL.dissolve - TL.montage}>
        <Audio src={staticFile("car/sfx/kenney-sci-computernoise-000.ogg")} volume={0.45} />
      </Sequence>
      <Sequence from={TL.end} durationInFrames={60}>
        <Audio src={staticFile(K.audio.endHit)} volume={K.audio.endHitVolume} />
      </Sequence>
    </AbsoluteFill>
  );
};
