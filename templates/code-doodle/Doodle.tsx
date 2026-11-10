import React from 'react';
import {interpolate, useCurrentFrame, Easing} from 'remotion';

// A wax-crayon doodle drawn entirely in code (SVG paths, no image files, no image model).
// Beats: outlines draw on, colour scribbles in, blink, omelet flip, steam), restyled as
// children's-book wax crayon on toothy paper:
//  - one shared "paper tooth" noise (fixed to the paper) decides where wax sticks, for lines AND fills
//  - outlines: two jittered passes (thick waxy + thinner broken pass), ragged grainy edges, pressure varies
//  - fills: diagonal crayon strokes drawn stroke by stroke, gaps of paper, overlap = darker, slight bleed past the line
//  - lines "boil" on twos (wobble seed changes every 2 frames); the paper grain stays put
// All ids are prefixed "k" so this can sit next to another doodle on the same page.

const W = 1440, H = 810;
export const INK = '#3B2738';
export const cl = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
export const ease = Easing.inOut(Easing.quad);

export const hash = (s: string) => {let h = 2166136261; for (let i = 0; i < s.length; i++) {h ^= s.charCodeAt(i); h = Math.imul(h, 16777619);} return h >>> 0;};
export const rng = (seed: number) => {let a = seed || 1; return () => {a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296;};};

// back-and-forth crayon scribble covering a box, split into chunks of a few strokes so each chunk
// can have its own pressure (opacity). Strokes are not quite parallel and the turn-arounds are ragged.
export const scribble = (x0: number, y0: number, x1: number, y1: number, gap: number, ang: number, seed: number, per = 5) => {
  const r = rng(seed);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, hw = (x1 - x0) / 2, hh = (y1 - y0) / 2;
  const c = Math.cos(ang), s = Math.sin(ang);
  // only cover the box itself: extents of the box along the stroke (R) and across the strokes (T)
  const R = hw * Math.abs(c) + hh * Math.abs(s) + 6, T = hw * Math.abs(s) + hh * Math.abs(c) + 4;
  const P = (u: number, v: number) => `${(cx + u * c - v * s).toFixed(1)} ${(cy + u * s + v * c).toFixed(1)}`;
  const chunks: {d: string; o: number}[] = [];
  let cur: string[] = [], k = 0, last = '';
  for (let t = -T; t <= T; t += gap * (0.7 + r() * 0.6), k++) {
    const e1 = R * (0.9 + r() * 0.2), e2 = R * (0.9 + r() * 0.2);
    const j1 = (r() - 0.5) * gap * 1.1, j2 = (r() - 0.5) * gap * 1.1;
    const [u1, u2] = k % 2 ? [e1, -e2] : [-e1, e2];
    const a = P(u1, t + j1), b = P(u2, t + j2);
    cur.push((cur.length ? 'L' : 'M' + (last ? last + ' L' : '')) + a, 'L' + b);
    last = b;
    if (cur.length >= per * 2) {chunks.push({d: cur.join(' '), o: 0.55 + r() * 0.4}); cur = [];}
  }
  if (cur.length) chunks.push({d: cur.join(' '), o: 0.55 + r() * 0.4});
  return chunks;
};

// draws a scribble progressively (chunk by chunk, stroke by stroke) up to progress q
export const Scribble: React.FC<{box: [number, number, number, number]; gap: number; ang: number; seed: number; q: number; c: string; sw: number; o: number}> =
  ({box, gap, ang, seed, q, c, sw, o}) => {
    if (q <= 0) return null;
    const ch = scribble(box[0], box[1], box[2], box[3], gap, ang, seed), n = ch.length;
    return <>{ch.map((x, i) => {
      const v = Math.min(1, Math.max(0, q * n - i));
      return v > 0 ? <path key={i} d={x.d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - v} fill="none" stroke={c} strokeWidth={sw} strokeLinejoin="round" strokeLinecap="round" opacity={x.o * o} /> : null;
    })}</>;
  };

// broken crayon line: dash pattern (pathLength 1000) that is visible up to p*1000, with small skips
export const brokenDash = (p: number, seed: number, dash: [number, number], skip: [number, number]) => {
  const r = rng(seed), lim = p * 1000, a: number[] = [];
  let s = 0;
  while (s < lim) {
    const d = Math.min(dash[0] + r() * (dash[1] - dash[0]), lim - s); a.push(d); s += d;
    if (s >= lim) break;
    const g = skip[0] + r() * (skip[1] - skip[0]); a.push(g); s += g;
  }
  if (a.length % 2 === 0) a.push(0);
  a.push(2000);
  return a.map((v) => v.toFixed(1)).join(' ');
};

// crayon outline: thick waxy pass + thinner, offset, broken second pass (like going over the line twice)
export const CrayonLine: React.FC<{id: string; d: string; p: number; w: number; c: string}> = ({id, d, p, w, c}) => {
  if (p <= 0) return null;
  const sd = hash(id);
  return <g filter="url(#kLine)">
    <path d={d} pathLength={1000} strokeDasharray={brokenDash(p, sd, [120, 420], [4, 18])} fill="none" stroke={c} strokeWidth={w * 1.45} strokeLinecap="round" strokeLinejoin="round" />
    <path d={d} transform="translate(1.6 -1.2)" pathLength={1000} strokeDasharray={brokenDash(Math.max(0, p * 1.08 - 0.08), sd + 9, [40, 160], [10, 60])} fill="none" stroke={c} strokeWidth={w * 0.75} strokeLinecap="round" strokeLinejoin="round" opacity={0.8} />
  </g>;
};

// a shape: outline drawn on over [a,b], crayon colour scribbled in over [fa,fb]
export const Shape: React.FC<{id: string; d: string; f: number; a: number; b: number; fa: number; fb: number; fill?: string; fill2?: string; box: [number, number, number, number]; w?: number; ang?: number; gap?: number; noLine?: boolean}> =
  ({id, d, f, a, b, fa, fb, fill, fill2, box, w = 5, ang = 0.6, gap = 9, noLine}) => {
    const p = interpolate(f, [a, b], [0, 1], {...cl, easing: ease});
    const q = interpolate(f, [fa, fb], [0, 1], cl);
    const q2 = interpolate(f, [fa + (fb - fa) * 0.35, fb + 4], [0, 1], cl);
    const [x0, y0, x1, y1] = box;
    const sd = hash(id), g = gap * 0.85;
    const lower: [number, number, number, number] = [x0, y0 + (y1 - y0) * 0.55, x1, y1];
    return <g>
      {fill && q > 0 && <>
        <mask id={'km' + id} maskUnits="userSpaceOnUse" x={x0 - 40} y={y0 - 40} width={x1 - x0 + 80} height={y1 - y0 + 80}>
          <path d={d} fill="#fff" stroke="#fff" strokeWidth={Math.min(11, gap * 1.1)} strokeLinejoin="round" filter="url(#kBleed)" />
        </mask>
        <g mask={`url(#km${id})`}>
          <g filter="url(#kWax)">
            {/* base layer: diagonal strokes, laid down stroke by stroke, pressure varies chunk to chunk */}
            <Scribble box={box} gap={g} ang={ang} seed={sd} q={q} c={fill!} sw={g * 0.9} o={1} />
            {/* a few extra strokes at a slightly different angle: uneven coverage, darker where they overlap */}
            <Scribble box={box} gap={g * 2.6} ang={ang + 0.22} seed={sd + 1} q={q2} c={fill!} sw={g * 0.8} o={0.7} />
            {/* edges pressed harder, like colouring around the inside of the line first */}
            <path d={d} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - q} fill="none" stroke={fill2 || fill} strokeWidth={Math.min(16, gap * 1.6)} strokeLinejoin="round" opacity={0.55} />
            {/* shading on the lower part, same direction as the hand */}
            {fill2 && <Scribble box={lower} gap={g * 1.25} ang={ang + 0.12} seed={sd + 2} q={q2} c={fill2} sw={g * 0.85} o={0.75} />}
          </g>
        </g>
      </>}
      {!noLine && <CrayonLine id={id} d={d} p={p} w={w} c={INK} />}
    </g>;
  };

// a stroke only (whiskers, steam, details)
export const Ln: React.FC<{d: string; f: number; a: number; b: number; w?: number; c?: string}> = ({d, f, a, b, w = 4, c = INK}) => {
  const p = interpolate(f, [a, b], [0, 1], {...cl, easing: ease});
  return <CrayonLine id={d.slice(0, 24)} d={d} p={p} w={w} c={c} />;
};

// Put <CrayonDefs boil={...}/> inside any <svg> that uses Shape, Ln or CrayonLine: it holds the crayon filters
// (kLine, kWax, kBleed, kPaper). boil = Math.floor(frame / 2) % 3 makes the lines boil on twos.
export const CrayonDefs: React.FC<{boil: number}> = ({boil}) => {
  // paper tooth: one fixed noise field shared by every crayon mark (wax only sticks to the high points)
  const tooth = <>
    <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves={3} seed={7} result="t" />
    <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.2 0 0 0 -0.6" result="tA" />
  </>;
  return <>
    <defs>
      {/* outlines: wobble (boils on twos) + ragged grain edge + paper tooth + pressure variation */}
      <filter id="kLine" x="-8%" y="-8%" width="116%" height="116%" colorInterpolationFilters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves={2} seed={boil + 1} result="lo" />
        <feDisplacementMap in="SourceGraphic" in2="lo" scale={5} xChannelSelector="R" yChannelSelector="G" result="wob" />
        <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves={1} seed={boil + 11} result="hi" />
        <feDisplacementMap in="wob" in2="hi" scale={4} xChannelSelector="R" yChannelSelector="G" result="rag" />
        <feGaussianBlur in="rag" stdDeviation={1} result="soft" />
        {tooth}
        <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves={1} seed={3} result="pr" />
        <feColorMatrix in="pr" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.6 0 0 0 -0.8" result="prA" />
        <feComposite in="soft" in2="tA" operator="arithmetic" k2={1.5} k3={1.05} k4={-1.08} result="m0" />
        <feComposite in="m0" in2="prA" operator="arithmetic" k2={1} k3={0.5} k4={0} result="m1" />
        <feComponentTransfer in="m1" result="m"><feFuncA type="linear" slope={2.6} intercept={-0.35} /></feComponentTransfer>
        <feColorMatrix in="rag" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 30 0" result="solid" />
        <feComposite in="solid" in2="m" operator="in" />
      </filter>
      {/* fills: stroke alpha (overlaps are denser) against the same paper tooth */}
      <filter id="kWax" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
        {tooth}
        <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves={2} seed={boil + 4} result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale={3} xChannelSelector="R" yChannelSelector="G" result="src" />
        <feGaussianBlur in="src" stdDeviation={1.1} result="soft" />
        <feComposite in="soft" in2="tA" operator="arithmetic" k2={1.45} k3={1.25} k4={-1.25} result="m0" />
        <feComponentTransfer in="m0" result="m"><feFuncA type="linear" slope={2.6} intercept={-0.1} /></feComponentTransfer>
        <feColorMatrix in="src" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1.35 0" result="solid" />
        <feComposite in="solid" in2="m" operator="in" />
      </filter>
      {/* colouring slightly outside the lines */}
      <filter id="kBleed" x="-10%" y="-10%" width="120%" height="120%">
        <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves={2} seed={21} result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale={13} xChannelSelector="R" yChannelSelector="G" />
      </filter>
      {/* toothy paper: fine grain + soft mottling */}
      <filter id="kPaper" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves={3} seed={7} result="g" />
        <feColorMatrix in="g" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.25  -0.9 0 0 0 0.44" result="grain" />
        <feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves={2} seed={4} result="b" />
        <feColorMatrix in="b" type="matrix" values="0 0 0 0 0.75  0 0 0 0 0.6  0 0 0 0 0.4  0.25 0 0 0 -0.1" result="blot" />
        <feMerge><feMergeNode in="blot" /><feMergeNode in="grain" /></feMerge>
      </filter>
    </defs>
  </>;
};

// Cream paper with grain. Draw it first, behind everything.
export const PaperBg: React.FC = () => <>
  <rect width={W} height={H} fill="#FBF4E4" />
  <rect width={W} height={H} filter="url(#kPaper)" />
</>;

// d = how long the clip is, in frames (for example 174 at 30 fps). Longer lines draw up to 1.4x slower.
// Reuse the exported helpers (Shape, Ln, CrayonLine, Scribble) to draw your own scene.
export {W, H};
export const Doodle: React.FC<{d: number}> = ({d}) => {
  const fr = useCurrentFrame();
  // the drawing slows down a little (up to 1.4x) for a longer voice line; long lines get a second flip
  const k = Math.min(Math.max(d / 174, 1), 1.4), f = fr / k;
  const boil = Math.floor(fr / 2) % 3;                 // hand-drawn line boil, on twos
  const sway = f > 70 ? Math.sin((f - 70) / 9) * 6 : 0;
  const blink = (f > 118 && f < 124) || (d > 260 && fr > d - 100 && fr < d - 94);
  const flip = interpolate(f, [128, 150], [0, 1], cl); // omelet up and over
  const flip2 = d > 260 ? interpolate(fr, [d - 62, d - 40], [0, 1], cl) : 0;
  const oy = -Math.sin(flip * Math.PI) * 120 - Math.sin(flip2 * Math.PI) * 120, orot = (flip + flip2) * 180;
  const happy = f >= 150;
  const steam = f > 104 ? Math.sin(f / 6) * 5 : 0;
  const catX = 560, catY = 470;
  return <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{display: 'block'}}>
    <CrayonDefs boil={boil} />
    <PaperBg />
    <g transform="translate(720 515) scale(1.22) translate(-720 -470)">

    {/* kitchen: wall tiles, counter, window */}
    <Shape id="win" d="M960 150 h200 v170 h-200 Z" f={f} a={4} b={22} fa={60} fb={88} fill="#7EC4EC" fill2="#4FA3DA" box={[960, 150, 1160, 320]} w={4} />
    <Ln d="M1060 152 V318 M962 235 H1158" f={f} a={18} b={30} w={3.5} />
    <Shape id="counter" d="M60 640 Q720 628 1380 642 L1380 700 Q720 690 60 702 Z" f={f} a={2} b={24} fa={56} fb={92} fill="#EE9F5C" fill2="#C9733C" box={[60, 628, 1380, 702]} gap={11} ang={0.35} />
    <Ln d="M300 170 h56 v56 h-56 Z M372 200 h56 v56 h-56 Z M280 270 h56 v56 h-56 Z" f={f} a={10} b={34} w={3.5} c="#D98FAE" />

    {/* stove + pan (pan is held by the cat) */}
    <g transform={`translate(0 ${happy ? Math.sin((f - 150) / 3) * 2 : 0})`}>
      <Shape id="pan" d="M800 520 Q880 560 960 520 Q965 548 940 560 Q880 584 820 560 Q796 548 800 520 Z" f={f} a={26} b={44} fa={74} fb={96} fill="#4C4860" fill2="#2E2A3C" box={[796, 515, 966, 585]} gap={8} />
      <Ln d="M800 528 Q760 535 700 548" f={f} a={30} b={42} w={8} c="#8A5233" />
    </g>
    <g transform={`translate(880 ${520 + oy}) rotate(${orot})`}>
      <Shape id="omelet" d="M-55 0 Q-50 -26 0 -28 Q50 -26 55 0 Q30 10 0 10 Q-30 10 -55 0 Z" f={f} a={40} b={54} fa={84} fb={104} fill="#FFC81E" fill2="#F59A12" box={[-58, -30, 58, 12]} gap={7} />
    </g>
    {f > 104 && <Ln d={`M860 ${470 + steam} q12 -18 0 -36 q-12 -18 0 -36 M900 ${462 - steam} q12 -18 0 -36 q-12 -18 0 -36`} f={f} a={104} b={118} w={3.5} c="#9C8FB0" />}

    {/* the cat */}
    <g transform={`translate(${catX} ${catY})`}>
      <g transform={`rotate(${sway} -90 120)`}>
        <Shape id="tail" d="M-90 120 Q-190 110 -200 30 Q-205 -10 -175 -20 Q-160 -5 -170 25 Q-170 80 -95 92 Z" f={f} a={20} b={36} fa={70} fb={90} fill="#FFD9A0" fill2="#F2B36E" box={[-210, -25, -85, 125]} />
      </g>
      <Shape id="body" d="M-125 170 Q-135 40 -80 -20 Q0 -78 80 -20 Q140 40 128 170 Q0 186 -125 170 Z" f={f} a={8} b={30} fa={62} fb={90} fill="#FFD9A0" fill2="#F2B36E" box={[-140, -60, 140, 185]} />
      <Shape id="apron" d="M-60 30 Q0 20 60 30 L75 160 Q0 175 -75 160 Z" f={f} a={22} b={38} fa={78} fb={98} fill="#F36F9C" fill2="#D9487C" box={[-78, 18, 78, 172]} w={4} />
      <Shape id="arm" d="M60 40 Q110 50 140 70 Q150 85 136 92 Q100 80 55 75 Z" f={f} a={30} b={42} fa={80} fb={96} fill="#FFD9A0" fill2="#F2B36E" box={[50, 35, 155, 95]} w={4.5} gap={7} />
      <Shape id="head" d="M-120 -120 Q-125 -200 -60 -225 L-85 -290 L-15 -240 Q0 -243 15 -240 L85 -290 L60 -225 Q125 -200 120 -120 Q115 -55 0 -50 Q-115 -55 -120 -120 Z" f={f} a={0} b={26} fa={58} fb={86} fill="#FFD9A0" fill2="#F2B36E" box={[-128, -292, 128, -48]} w={5.5} />
      <Shape id="earL" d="M-78 -268 L-60 -232 L-40 -240 Z" f={f} a={24} b={30} fa={84} fb={92} fill="#F36F9C" box={[-80, -270, -38, -230]} noLine gap={6} />
      <Shape id="earR" d="M78 -268 L60 -232 L40 -240 Z" f={f} a={24} b={30} fa={84} fb={92} fill="#F36F9C" box={[38, -270, 80, -230]} noLine gap={6} />
      <Shape id="hat" d="M-55 -238 L-50 -290 Q-95 -300 -85 -345 Q-70 -385 -25 -368 Q-10 -405 30 -390 Q70 -400 82 -360 Q105 -330 60 -292 L55 -238 Q0 -230 -55 -238 Z" f={f} a={12} b={34} fa={66} fb={88} fill="#FFFFFF" fill2="#DDD7CE" box={[-100, -405, 108, -230]} />
      <Ln d="M-52 -262 Q0 -252 52 -262" f={f} a={32} b={40} w={3.5} />
      <Shape id="chL" d="M-80 -110 a20 13 0 1 0 1 0 Z" f={f} a={0} b={1} fa={96} fb={104} fill="#FF7FA3" box={[-102, -112, -58, -84]} noLine gap={6} />
      <Shape id="chR" d="M80 -110 a20 13 0 1 0 1 0 Z" f={f} a={0} b={1} fa={96} fb={104} fill="#FF7FA3" box={[58, -112, 102, -84]} noLine gap={6} />
      {blink || happy
        ? <Ln d={happy ? 'M-62 -140 q16 -18 32 0 M30 -140 q16 -18 32 0' : 'M-62 -138 h30 M32 -138 h30'} f={f} a={0} b={1} w={5} />
        : <>
          <Shape id="eyL" d="M-46 -158 a13 17 0 1 0 1 0 Z" f={f} a={34} b={42} fa={40} fb={48} fill={INK} box={[-60, -160, -32, -122]} gap={5} w={4} />
          <Shape id="eyR" d="M46 -158 a13 17 0 1 0 1 0 Z" f={f} a={36} b={44} fa={42} fb={50} fill={INK} box={[32, -160, 60, -122]} gap={5} w={4} />
        </>}
      <Shape id="nose" d="M-9 -112 h18 l-9 10 Z" f={f} a={40} b={46} fa={46} fb={52} fill="#EE5F8C" box={[-11, -114, 11, -100]} gap={4} w={3.5} />
      <Ln d={happy ? 'M-20 -98 q10 22 20 0 q10 22 20 0' : 'M-18 -96 q9 10 18 0 q9 10 18 0'} f={f} a={44} b={52} w={4} />
      <Ln d="M-70 -105 l-60 -8 M-70 -95 l-58 6 M70 -105 l60 -8 M70 -95 l58 6" f={f} a={48} b={60} w={3} />
    </g>
  </g></svg>;
};
