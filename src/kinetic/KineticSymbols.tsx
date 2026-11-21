import React from "react";
import { AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { CameraMotionBlur } from "@remotion/motion-blur";
import { kineticConfig as K, eighth, Enter } from "./config";

for (const w of [300, 600, 900]) {
  loadFont({ family: K.font, url: staticFile(`fonts/inter-latin-${w}-normal.woff2`), weight: String(w) });
}

const W = K.output.width;
const H = K.output.height;
const outExp = Easing.out(Easing.exp);

const field = (bg: string, fade: boolean) =>
  fade
    ? `linear-gradient(180deg, ${bg} 0%, ${bg} ${K.fadeStart * 100}%, ${K.colors.grey} 100%)`
    : bg;

// Deterministic pseudo-random in [0,1).
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};

const Glyph: React.FC<{ ch: string; ink: string; size: number; x: number; y: number; weight?: number; style?: React.CSSProperties }> = ({ ch, ink, size, x, y, weight = 900, style }) => (
  <div
    style={{
      position: "absolute",
      left: W / 2 + x,
      top: H / 2 + y,
      transform: "translate(-50%, -50%)",
      fontFamily: K.font,
      fontWeight: weight,
      fontSize: size,
      lineHeight: 1,
      color: ink,
      letterSpacing: "-0.03em",
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {ch}
  </div>
);

// One giant glyph that snaps in, then holds dead still.
const GlyphShot: React.FC<{ g: (typeof K.glyphs)[number] }> = ({ g }) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, K.glyphEnterFrames], [0, 1], { extrapolateRight: "clamp", easing: outExp });
  const q = 1 - p;
  const moves: Record<Enter, string> = {
    scale: `scale(${1 + 0.35 * q})`,
    slideL: `translateX(${-700 * q}px)`,
    slideR: `translateX(${700 * q}px)`,
    slideU: `translateY(${600 * q}px)`,
    rot: `rotate(${-38 * q}deg) scale(${1 + 0.15 * q})`,
  };
  return (
    <AbsoluteFill style={{ background: field(g.bg, g.fade), overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: moves[g.enter] }}>
        <Glyph ch={g.ch} ink={g.ink} size={g.size} x={g.x} y={g.y} style={{ rotate: `${g.rot}deg` }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Wall of outlined glyphs: scrolls diagonally, every tile flips 90 deg on the beat.
const Wall1: React.FC = () => {
  const f = useCurrentFrame();
  const w = K.wall1;
  const flip = interpolate(f, [w.flipAtFrame - 2, w.flipAtFrame + 5], [0, 90], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const ox = (f * w.speed[0]) % w.cell;
  const oy = (f * w.speed[1]) % w.cell;
  const cols = Math.ceil(W / w.cell) + 2;
  const rows = Math.ceil(H / w.cell) + 2;
  const tiles = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      tiles.push(
        <div
          key={`${r}-${c}`}
          style={{
            position: "absolute",
            left: (c - 1) * w.cell + ox + (r % 2) * (w.cell / 2),
            top: (r - 1) * w.cell + oy,
            width: w.cell,
            height: w.cell,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: K.font,
            fontWeight: 900,
            fontSize: w.fontSize,
            lineHeight: 1,
            color: "transparent",
            WebkitTextStroke: `${w.stroke}px ${w.ink}`,
            transform: `rotate(${flip + (r + c) % 2 * 180}deg)`,
          }}
        >
          {w.ch}
        </div>,
      );
    }
  return <AbsoluteFill style={{ background: field(w.bg, true), overflow: "hidden" }}>{tiles}</AbsoluteFill>;
};

// Rows of symbols alternating thin/heavy, the pattern stepping one row per eighth.
const Stack: React.FC = () => {
  const f = useCurrentFrame();
  const s = K.stack;
  const step = Math.floor((f * 2) / 15);
  return (
    <AbsoluteFill style={{ background: s.bg, alignItems: "center", justifyContent: "center" }}>
      {s.rows.map((row, i) => (
        <div
          key={i}
          style={{
            fontFamily: K.font,
            fontWeight: s.weights[(i + step) % s.weights.length],
            fontSize: s.fontSize,
            lineHeight: s.lineHeight,
            letterSpacing: `${s.tracking}em`,
            color: s.ink,
          }}
        >
          {row}
        </div>
      ))}
    </AbsoluteFill>
  );
};

// A giant glyph in three horizontal bands that slide in from alternating sides and lock.
const SliceShot: React.FC<{ s: (typeof K.slices)[number] }> = ({ s }) => {
  const f = useCurrentFrame();
  const bands = s.offsets.length;
  return (
    <AbsoluteFill style={{ background: field(s.bg, s.fade), overflow: "hidden" }}>
      {s.offsets.map((off, i) => {
        const p = interpolate(f, [i, i + K.sliceEnterFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: outExp });
        const top = (i / bands) * 100;
        const bottom = 100 - ((i + 1) / bands) * 100;
        return (
          <AbsoluteFill key={i} style={{ clipPath: `inset(${top}% 0 ${bottom}% 0)`, transform: `translateX(${off * (1 - p)}px)` }}>
            <Glyph ch={s.ch} ink={s.ink} size={s.size} x={s.x} y={s.y} />
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

// Wall of spinning asterisks; each row spins the other way.
const Wall2: React.FC = () => {
  const f = useCurrentFrame();
  const w = K.wall2;
  const cols = Math.ceil(W / w.cell) + 1;
  const rows = Math.ceil(H / w.cell) + 1;
  const tiles = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      // Spin in steps: each beat a quick 90 deg turn that settles.
      const beat = Math.floor(f / 15);
      const local = interpolate(f % 15, [0, 6], [0, 1], { extrapolateRight: "clamp", easing: outExp });
      const ang = (beat + local) * w.spinPerBeat * (r % 2 ? -1 : 1);
      tiles.push(
        <div
          key={`${r}-${c}`}
          style={{
            position: "absolute",
            left: c * w.cell + (r % 2) * (w.cell / 2) - w.cell / 2,
            top: r * w.cell - w.cell / 4,
            width: w.cell,
            height: w.cell,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: K.font,
            fontWeight: 900,
            fontSize: w.fontSize,
            lineHeight: 1,
            color: w.ink,
            transform: `rotate(${ang}deg)`,
          }}
        >
          <span style={{ transform: "translateY(18%)" }}>{w.ch}</span>
        </div>,
      );
    }
  return <AbsoluteFill style={{ background: field(w.bg, true), overflow: "hidden" }}>{tiles}</AbsoluteFill>;
};

// One wordmark letter, cut from the real logo PNG by its measured column.
const Letter: React.FC<{ src: string; col: number[]; pngH: number; seed: number; start: number }> = ({ src, col, pngH, seed, start }) => {
  const f = useCurrentFrame();
  const L = K.logo;
  const p = interpolate(f, [start, start + L.letterFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: outExp });
  const q = 1 - p;
  const sx = (rnd(seed) * 2 - 1) * L.scatter.x;
  const sy = (rnd(seed + 9) * 2 - 1) * L.scatter.y;
  const sr = (rnd(seed + 17) * 2 - 1) * L.scatter.rot;
  const ss = L.scatter.scaleMin + rnd(seed + 23) * (L.scatter.scaleMax - L.scatter.scaleMin);
  const vis = f >= start ? 1 : 0;
  const pad = 4;
  const w = col[1] - col[0] + pad * 2;
  return (
    <div
      style={{
        position: "absolute",
        left: col[0] - pad,
        top: 0,
        width: w,
        height: pngH,
        overflow: "hidden",
        opacity: vis,
        transform: `translate(${sx * q}px, ${sy * q}px) rotate(${sr * q}deg) scale(${1 + (ss - 1) * q})`,
      }}
    >
      <Img src={staticFile(src)} style={{ position: "absolute", left: -(col[0] - pad), top: 0 }} />
    </div>
  );
};

// The real logo: giant P, giant E, camera pull-out, bar grows, letters assemble.
const Logo: React.FC = () => {
  const f = useCurrentFrame(); // absolute frame (rendered outside any Sequence)
  const L = K.logo;
  const P = L.pieces;
  const s0 = L.heightOnScreen / (L.box.y1 - L.box.y0);
  const boxCx = (L.box.x0 + L.box.x1) / 2;
  const boxCy = (L.box.y0 + L.box.y1) / 2;
  const tE = eighth(K.sections.e);
  const tPull = eighth(K.sections.pull);

  const centre = (k: "p" | "e") => ({ x: P[k].x + P[k].w / 2, y: P[k].y + P[k].h / 2 });
  const pull = interpolate(f, [tPull, tPull + L.pullFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: outExp });
  const focus = f < tE ? centre("p") : centre("e");
  const zoom = interpolate(pull, [0, 1], [L.zoomOnGlyph, 1]);
  const fx = interpolate(pull, [0, 1], [focus.x, boxCx]);
  const fy = interpolate(pull, [0, 1], [focus.y, boxCy]);
  const scale = s0 * zoom;

  const showP = f < tE || f >= tPull;
  const showE = f >= tE;
  const bar = interpolate(f, [L.barStart, L.barStart + L.barFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: outExp });

  const piece = (k: keyof typeof P, child: React.ReactNode, style?: React.CSSProperties) => (
    <div style={{ position: "absolute", left: P[k].x, top: P[k].y, width: P[k].w, height: P[k].h, ...style }}>{child}</div>
  );

  return (
    <AbsoluteFill style={{ background: K.colors.navy, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: W / 2,
          top: H / 2,
          width: 0,
          height: 0,
          transform: `scale(${scale}) translate(${-fx}px, ${-fy}px)`,
          transformOrigin: "0 0",
        }}
      >
        {showP && piece("p", <Img src={staticFile("logo/p.png")} />)}
        {showE && piece("e", <Img src={staticFile("logo/e.png")} />)}
        {piece("bar", <Img src={staticFile("logo/bar.png")} />, { transform: `scaleX(${bar})`, opacity: bar > 0 ? 1 : 0 })}
        {piece(
          "phillips",
          L.phillipsCols.map((c, i) => (
            <Letter key={i} src="logo/phillips.png" col={c} pngH={P.phillips.h} seed={i + 1} start={L.lettersStart + i * L.letterStagger} />
          )),
        )}
        {piece(
          "english",
          L.englishCols.map((c, i) => (
            <Letter key={i} src="logo/english.png" col={c} pngH={P.english.h} seed={i + 40} start={L.lettersStart + L.englishDelay + i * L.letterStagger} />
          )),
        )}
      </div>
    </AbsoluteFill>
  );
};

export const KineticSymbols: React.FC = () => {
  const S = K.sections;
  const frame = useCurrentFrame();
  const tLogo = eighth(S.p);
  return (
    <AbsoluteFill style={{ background: K.colors.navy }}>
      <CameraMotionBlur shutterAngle={K.motionBlur.shutterAngle} samples={K.motionBlur.samples}>
        <AbsoluteFill>
          {K.glyphs.map((g, i) => (
            <Sequence key={i} from={eighth(S.glyphs + i)} durationInFrames={eighth(S.glyphs + i + 1) - eighth(S.glyphs + i)}>
              <GlyphShot g={g} />
            </Sequence>
          ))}
          <Sequence from={eighth(S.wall1)} durationInFrames={eighth(S.stack) - eighth(S.wall1)}>
            <Wall1 />
          </Sequence>
          <Sequence from={eighth(S.stack)} durationInFrames={eighth(S.slices) - eighth(S.stack)}>
            <Stack />
          </Sequence>
          {K.slices.map((s, i) => (
            <Sequence key={i} from={eighth(S.slices + i)} durationInFrames={eighth(S.slices + i + 1) - eighth(S.slices + i)}>
              <SliceShot s={s} />
            </Sequence>
          ))}
          <Sequence from={eighth(S.wall2)} durationInFrames={eighth(S.p) - eighth(S.wall2)}>
            <Wall2 />
          </Sequence>
          {/* Logo reads absolute frames, so it is gated here instead of wrapped in a Sequence. */}
          {frame >= tLogo ? <Logo /> : null}
        </AbsoluteFill>
      </CameraMotionBlur>
      <Audio src={staticFile(K.audio.beat)} volume={K.audio.beatVolume} />
      {K.audio.sfx.map((s, i) => (
        <Sequence key={i} from={s.frame}>
          <Audio src={staticFile(s.file)} volume={s.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

