import React from "react";
import { AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { graffitiConfig as G, P, Bg, Mark, Poster } from "./config";

for (const w of [600, 800]) loadFont({ family: "Inter", url: staticFile(`fonts/inter-latin-${w}-normal.woff2`), weight: String(w) });
for (const f of ["SedgwickAveDisplay", "PermanentMarker", "RockSalt", "RubikWetPaint"]) {
  loadFont({ family: f, url: staticFile(`fonts/graffiti/${f}.woff2`) });
}

const W = G.output.width;
const H = G.output.height;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};

// ---------- Textures (all generated with SVG filters; no photos) ----------

const Concrete: React.FC<{ id: string; seed: number; dark?: boolean }> = ({ id, seed, dark }) => {
  // Map a noise value to concrete greys; dark = shadowed wall.
  const [lo, hi] = dark ? [0.05, 0.55] : [0.42, 0.95];
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <filter id={`${id}-c`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.004" numOctaves={4} seed={seed} result="big" />
          <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves={1} seed={seed + 1} result="fine" />
          <feTurbulence type="fractalNoise" baseFrequency="0.026" numOctaves={3} seed={seed + 2} result="spots" />
          <feColorMatrix in="big" type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1" result="bigG" />
          <feComponentTransfer in="bigG" result="bigC">
            <feFuncR type="linear" slope={1.7 * (hi - lo)} intercept={lo - 0.35 * (hi - lo)} />
            <feFuncG type="linear" slope={1.7 * (hi - lo)} intercept={lo - 0.35 * (hi - lo)} />
            <feFuncB type="linear" slope={1.7 * (hi - lo)} intercept={lo - 0.35 * (hi - lo)} />
          </feComponentTransfer>
          {/* fine dark speckle */}
          <feColorMatrix in="fine" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 0.62" result="fineA" />
          {/* sparse dark blotches: only the darkest tail of a soft noise */}
          <feColorMatrix in="spots" type="matrix" values="0 0 0 0 0.05  0 0 0 0 0.05  0 0 0 0 0.05  -18 0 0 0 5.7" result="spotsA" />
          <feComposite in="fineA" in2="bigC" operator="over" result="t1" />
          <feComposite in="spotsA" in2="t1" operator="over" />
        </filter>
        <linearGradient id={`${id}-v`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#000" stopOpacity={0} />
          <stop offset="1" stopColor="#000" stopOpacity={dark ? 0.5 : 0.38} />
        </linearGradient>
      </defs>
      <rect width={W} height={H} filter={`url(#${id}-c)`} />
      <rect width={W} height={H} fill={`url(#${id}-v)`} />
    </svg>
  );
};

// Chain-link fence over a dark grimy wall.
const Fence: React.FC<{ id: string; seed: number }> = ({ id, seed }) => {
  const cell = 78;
  const lines = [];
  for (let i = -30; i < 60; i++) {
    const x = i * cell;
    lines.push(<line key={`a${i}`} x1={x} y1={0} x2={x + H * 0.85} y2={H} />);
    lines.push(<line key={`b${i}`} x1={x} y1={0} x2={x - H * 0.85} y2={H} />);
  }
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <filter id={`${id}-w`} x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={2} seed={seed} result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale={10} />
        </filter>
      </defs>
      <Concrete id={`${id}-bg`} seed={seed + 4} dark />
      <g filter={`url(#${id}-w)`}>
        <g stroke="#0a0a0a" strokeWidth={9} opacity={0.7} transform="translate(5,6)">{lines}</g>
        <g stroke="#cfcfcb" strokeWidth={5}>{lines}</g>
      </g>
    </svg>
  );
};

const Background: React.FC<{ bg: Bg; seed: number; id: string }> = ({ bg, seed, id }) => {
  if (bg === "concrete") return <Concrete id={id} seed={seed} />;
  if (bg === "concreteDark") return <Concrete id={id} seed={seed} dark />;
  if (bg === "fence") return <Fence id={id} seed={seed} />;
  if (bg === "black") return <AbsoluteFill style={{ background: P.black }} />;
  if (bg === "pink") return <AbsoluteFill style={{ background: P.pink }} />;
  // split: grimy B&W wall on top, pink below (a torn poster edge)
  return (
    <AbsoluteFill>
      <Concrete id={id} seed={seed} dark />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <path d={tornEdge(seed, H * 0.48)} fill={P.pink} />
      </svg>
    </AbsoluteFill>
  );
};

const tornEdge = (seed: number, y: number) => {
  let d = `M0 ${y}`;
  for (let x = 0; x <= W; x += 24) d += ` L${x} ${y + (rnd(seed * 31 + x) - 0.5) * 16}`;
  return `${d} L${W} ${H} L0 ${H} Z`;
};

// Photocopy grain + dust over the whole frame (static, like a printed poster).
const Grain: React.FC = () => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: G.grain.opacity, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={1} seed={7} />
      <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.05" />
    </filter>
    <rect width={W} height={H} filter="url(#grain)" />
  </svg>
);

// ---------- Hand-drawn marker marks ----------

const markPath = (kind: Mark, w: number, h: number, seed: number): string => {
  const j = (k: number, a = 1) => (rnd(seed * 17 + k) - 0.5) * a;
  switch (kind) {
    case "underline":
      return `M${-w / 2} ${j(1, h)} Q${-w / 6} ${h / 2 + j(2, h)} ${w / 8} ${j(3, h / 2)} T${w / 2} ${-h / 3 + j(4, h)}`;
    case "zigzag": {
      let d = `M${-w / 2} 0`;
      const n = 14;
      for (let i = 1; i <= n; i++) d += ` L${-w / 2 + (w * i) / n + j(i, 20)} ${(i % 2 ? -h / 2 : h / 2) + j(i + 50, h * 0.4)}`;
      return d;
    }
    case "scribble": {
      let d = `M${j(0, w)} ${-h / 2}`;
      for (let i = 1; i < 12; i++) d += ` Q${(i % 2 ? w / 2 : -w / 2) + j(i, 40)} ${-h / 2 + (h * (i - 0.5)) / 11} ${j(i + 9, w * 0.5)} ${-h / 2 + (h * i) / 11}`;
      return d;
    }
    case "star": {
      let d = "";
      for (let i = 0; i <= 5; i++) {
        const a = -Math.PI / 2 + ((i * 2) % 5) * ((2 * Math.PI) / 5);
        d += `${i ? " L" : "M"}${(Math.cos(a) * w) / 2 + j(i, 14)} ${(Math.sin(a) * h) / 2 + j(i + 7, 14)}`;
      }
      return d;
    }
    case "arrow":
      return `M${-w / 2} ${h / 3} Q${-w / 8} ${-h / 2} ${w / 2} ${-h / 6} M${w / 2 - 50} ${-h / 2 + 4} L${w / 2} ${-h / 6} L${w / 2 - 60} ${h / 6}`;
    case "circle": {
      let d = "";
      for (let i = 0; i <= 28; i++) {
        const a = (i / 22) * Math.PI * 2;
        const r = 1 + j(i, 0.12);
        d += `${i ? " L" : "M"}${((Math.cos(a) * w) / 2) * r} ${((Math.sin(a) * h) / 2) * r}`;
      }
      return d;
    }
    case "crown":
      return `M${-w / 2} ${h / 2} L${-w / 2 + j(1, 10)} ${-h / 4} L${-w / 4} ${h / 8} L${j(2, 10)} ${-h / 2} L${w / 4} ${h / 8} L${w / 2 + j(3, 10)} ${-h / 4} L${w / 2} ${h / 2} Z`;
    case "blob": {
      // Dense hatched fill, like a white-out "bombing" scribble.
      let d = "";
      const rows = 26;
      for (let i = 0; i < rows; i++) {
        const y = -h / 2 + (h * i) / (rows - 1);
        const half = (w / 2) * Math.sqrt(Math.max(0, 1 - Math.pow((2 * y) / h, 2))) * (0.85 + j(i, 0.3));
        d += `${i ? " L" : "M"}${(i % 2 ? half : -half) + j(i + 3, 30)} ${y + j(i + 5, 10)}`;
      }
      return d;
    }
  }
};

const Marks: React.FC<{ marks: NonNullable<Poster["marks"]>; id: string; seed: number }> = ({ marks, id, seed }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
    <defs>
      <filter id={`${id}-m`} x="-10%" y="-10%" width="120%" height="120%">
        <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves={2} seed={seed} result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale={6} />
      </filter>
    </defs>
    <g filter={`url(#${id}-m)`} fill="none" strokeLinecap="round" strokeLinejoin="round">
      {marks.map((m, i) => (
        <path
          key={i}
          d={markPath(m.kind, m.w, m.h, seed + i)}
          stroke={m.ink}
          strokeWidth={m.width ?? 10}
          transform={`translate(${W / 2 + m.x} ${H / 2 + m.y}) rotate(${m.rot ?? 0})`}
        />
      ))}
    </g>
  </svg>
);

// ---------- Type ----------

const Headline: React.FC<{ ink: string; y: number; size?: number }> = ({ ink, y, size = G.fonts.headSize }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      right: 0,
      top: H / 2 + y,
      transform: "translateY(-50%)",
      textAlign: "center",
      fontFamily: G.fonts.head,
      fontWeight: G.fonts.headWeight,
      fontSize: size,
      lineHeight: G.fonts.headLine,
      letterSpacing: `${G.fonts.headTracking}em`,
      color: ink,
    }}
  >
    {G.words.headline.map((l) => (
      <div key={l}>{l}</div>
    ))}
  </div>
);

const Corners: React.FC<{ ink: string; n: number }> = ({ ink, n }) => {
  const c = G.words.corners.map((s) => s.replace("{n}", String(n).padStart(2, "0")));
  const st: React.CSSProperties = { position: "absolute", fontFamily: G.fonts.corner, fontWeight: 600, fontSize: G.fonts.cornerSize, letterSpacing: "0.06em", color: ink };
  return (
    <>
      <div style={{ ...st, left: 44, top: 36 }}>{c[0]}</div>
      <div style={{ ...st, right: 44, top: 36 }}>{c[1]}</div>
      <div style={{ ...st, left: 44, bottom: 36 }}>{c[2]}</div>
      <div style={{ ...st, right: 44, bottom: 36 }}>{c[3]}</div>
    </>
  );
};

const Tag: React.FC<{ t: NonNullable<Poster["tag"]>; style?: React.CSSProperties }> = ({ t, style }) => (
  <div
    style={{
      position: "absolute",
      left: W / 2 + t.x,
      top: H / 2 + t.y,
      transform: `translate(-50%, -50%) rotate(${t.rot}deg)`,
      fontFamily: t.font,
      fontSize: t.size,
      lineHeight: 1,
      whiteSpace: "nowrap",
      color: t.ink,
      WebkitTextStroke: t.stroke ? `${t.stroke}px ${t.ink}` : undefined,
      ...style,
    }}
  >
    {t.text}
  </div>
);

const headY = (pos: "top" | "bottom") => (pos === "top" ? -330 : 330);

const PosterView: React.FC<{ p: Poster; n: number }> = ({ p, n }) => {
  const id = `p${n}`;
  const cornerInk = p.bg === "pink" || p.bg === "concrete" ? P.black : P.white;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Background bg={p.bg} seed={p.seed} id={id} />
      {p.head.pos === "both" ? (
        <>
          <Headline ink={p.head.ink} y={-330} />
          <Headline ink={p.head.ink} y={330} />
        </>
      ) : (
        <Headline ink={p.head.ink} y={headY(p.head.pos)} />
      )}
      {p.marks && <Marks marks={p.marks} id={id} seed={p.seed} />}
      {p.tag && <Tag t={p.tag} />}
      <Corners ink={cornerInk} n={n} />
    </AbsoluteFill>
  );
};

// ---------- End card: the tag sprays on ----------

const EndCard: React.FC<{ f: number }> = ({ f }) => {
  const E = G.end;
  const p = interpolate(f, [E.sprayStart, E.sprayStart + E.sprayFrames], [0, 1], { ...clamp, easing: Easing.inOut(Easing.sin) });
  const edge = E.sprayEdge;
  const at = -edge + p * (100 + 2 * edge); // reveal front, in % of the tag's width
  const mask = `linear-gradient(90deg, #000 ${at - edge}%, transparent ${at}%)`;
  const maskMist = `linear-gradient(90deg, #000 ${at}%, transparent ${at + edge * 1.6}%)`;
  const reg = interpolate(f, [E.regAt, E.regAt + 5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) });
  const D = E.drips;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Background bg={E.bg} seed={E.seed} id="end" />
      <Headline ink={E.headInk} y={E.headY} size={E.headSize} />
      {/* overspray mist runs slightly ahead of the paint */}
      <Tag t={E.tag} style={{ filter: `blur(${E.oversprayBlur}px)`, opacity: E.oversprayOpacity, WebkitMaskImage: maskMist, maskImage: maskMist }} />
      <Tag t={E.tag} style={{ WebkitMaskImage: mask, maskImage: mask }} />
      {/* drips run down from the paint once it is on */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <g transform={`translate(${W / 2 + E.tag.x} ${H / 2 + E.tag.y}) rotate(${E.tag.rot})`}>
          {D.list.map(([x, len], i) => {
            const s = D.start + i * D.stagger;
            const g = interpolate(f, [s, s + D.frames], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) });
            if (g <= 0) return null;
            const y0 = E.tag.size * 0.1;
            return (
              <g key={i} fill={E.tag.ink}>
                <rect x={x - 7} y={y0} width={14} height={len * g} rx={7} />
                <circle cx={x} cy={y0 + len * g} r={11} />
              </g>
            );
          })}
        </g>
      </svg>
      <div
        style={{
          position: "absolute",
          left: W / 2 + 560,
          top: H / 2 - 250,
          transform: `translate(-50%, -50%) scale(${reg})`,
          fontFamily: G.fonts.head,
          fontWeight: 800,
          fontSize: 64,
          color: P.black,
        }}
      >
        ®
      </div>
      <Corners ink={P.black} n={10} />
    </AbsoluteFill>
  );
};

export const GraffitiFlip: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.floor(f / G.flipFrames) % G.posters.length;
  return (
    <AbsoluteFill style={{ background: P.black }}>
      {f < G.flipsEnd ? <PosterView p={G.posters[n]} n={n + 1} /> : <EndCard f={f} />}
      <Grain />
      <Audio src={staticFile(G.audio.mix)} volume={G.audio.volume} />
    </AbsoluteFill>
  );
};
