import React from "react";
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { kineticConfig as K, halfBeat, Shot } from "./config";

for (let w = 100; w <= 900; w += 100) {
  loadFont({ family: "Inter", url: staticFile(`fonts/inter-latin-${w}-normal.woff2`), weight: String(w) });
}
loadFont({ family: "Montserrat", url: staticFile("fonts/montserrat-latin-500-normal.woff2"), weight: "500" });
loadFont({ family: "Montserrat", url: staticFile("fonts/montserrat-latin-900-italic.woff2"), weight: "900", style: "italic" });

const W = K.output.width;
const H = K.output.height;
const outExp = Easing.out(Easing.exp);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Deterministic pseudo-random in [0,1).
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};
// Inter ships as 9 static weights, so a weight morph steps through them (about one per frame).
const weightAt = (a: number, b: number, p: number) => Math.round((a + (b - a) * p) / 100) * 100;

// Timeline in half-beats (all scenes read the absolute frame; none sit inside a Sequence).
const N = K.name;
const T = (() => {
  const shotsEnd = K.shots.length;
  const phillips = shotsEnd;
  const digital = phillips + N.phillips.halfBeats;
  const project = digital + N.digital.halfBeats;
  const lockup = project + N.project.halfBeats;
  const land = lockup + N.lockup.flashes.length;
  return { shotsEnd, phillips, digital, project, lockup, land };
})();
export const timeline = T;

// ---------- The count (hard cuts, one slow move per shot) ----------

const GlyphShot: React.FC<{ s: Extract<Shot, { kind: "glyph" }>; p: number }> = ({ s, p }) => {
  const m = s.move ?? {};
  const zoom = 1 + ((m.zoom ?? 1) - 1) * p;
  const px = (m.pan?.[0] ?? 0) * p;
  const py = (m.pan?.[1] ?? 0) * p;
  const w = m.weight ? weightAt(m.weight[0], m.weight[1], p) : s.weight ?? K.glyphWeight;
  return (
    <AbsoluteFill style={{ background: s.bg, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: W / 2 + s.x + px,
          top: H / 2 + s.y + py,
          transform: `translate(-50%, -50%) scale(${zoom}) rotate(${(m.rot ?? 0) * p}deg)`,
          fontFamily: K.glyphFont,
          fontWeight: w,
          fontSize: s.size,
          lineHeight: 1,
          letterSpacing: "-0.04em",
          color: s.ink,
        }}
      >
        {s.ch}
      </div>
    </AbsoluteFill>
  );
};

// Grid of the same glyph, every tile at its own random angle (the reference's 2s).
const WallShot: React.FC<{ s: Extract<Shot, { kind: "wall" }>; t: number; seed: number }> = ({ s, t, seed }) => {
  const cols = Math.ceil(W / s.cell) + 2;
  const rows = Math.ceil(H / s.cell) + 2;
  const tiles = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      const k = seed * 1000 + r * 50 + c;
      const ang = Math.floor(rnd(k) * 8) * 45 + (rnd(k + 7) - 0.5) * 30 + t * (rnd(k + 3) - 0.5) * 2;
      tiles.push(
        <div
          key={`${r}-${c}`}
          style={{
            position: "absolute",
            left: (c - 1) * s.cell + (r % 2) * (s.cell * 0.45) - t * 1.5,
            top: (r - 1) * s.cell * 0.92,
            width: s.cell,
            height: s.cell,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: K.glyphFont,
            fontWeight: s.weight,
            fontSize: s.size,
            lineHeight: 1,
            color: s.ink,
            transform: `rotate(${ang}deg)`,
          }}
        >
          {s.ch}
        </div>,
      );
    }
  return <AbsoluteFill style={{ background: s.bg, overflow: "hidden" }}>{tiles}</AbsoluteFill>;
};

// Outlined glyphs burst out of a tight cluster, spinning (the reference's 4s).
const BurstShot: React.FC<{ s: Extract<Shot, { kind: "burst" }>; p: number; seed: number }> = ({ s, p, seed }) => {
  const e = Easing.out(Easing.cubic)(p);
  return (
    <AbsoluteFill style={{ background: s.bg, overflow: "hidden" }}>
      {Array.from({ length: s.count }).map((_, i) => {
        const k = seed * 100 + i;
        const a = (i / s.count) * Math.PI * 2 + (rnd(k) - 0.5) * 0.5;
        const r = interpolate(e, [0, 1], [30 + rnd(k + 1) * 40, 260 + rnd(k + 2) * 520]);
        const ang = rnd(k + 3) * 360 + e * (rnd(k + 4) > 0.5 ? 140 : -140);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: W / 2 + Math.cos(a) * r * 1.5,
              top: H / 2 + Math.sin(a) * r * 0.75,
              transform: `translate(-50%, -50%) rotate(${ang}deg) scale(${0.7 + rnd(k + 5) * 0.5})`,
              fontFamily: K.glyphFont,
              fontWeight: 300,
              fontSize: s.size,
              lineHeight: 1,
              color: "transparent",
              WebkitTextStroke: `${s.stroke}px ${s.ink}`,
            }}
          >
            {s.ch}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Concentric rings of the glyph, each turned along its ring; the whole pattern rotates (the 8s).
const RingsShot: React.FC<{ s: Extract<Shot, { kind: "rings" }>; t: number }> = ({ s, t }) => {
  const items = [];
  const radii = [0, 170, 340, 510, 680, 850, 1020];
  for (let ri = 0; ri < radii.length; ri++) {
    const R = radii[ri];
    const n = ri === 0 ? 1 : Math.round((2 * Math.PI * R) / (s.size * 1.15));
    for (let j = 0; j < n; j++) {
      const a = (j / n) * 360 + ri * 13 + t * s.spin * (ri % 2 ? 1 : -1);
      items.push(
        <div
          key={`${ri}-${j}`}
          style={{
            position: "absolute",
            left: W / 2,
            top: H / 2,
            transform: `rotate(${a}deg) translateY(${-R}px) rotate(90deg) translate(-50%, -50%)`,
            transformOrigin: "0 0",
            fontFamily: K.glyphFont,
            fontWeight: s.weight,
            fontSize: s.size,
            lineHeight: 1,
            color: s.ink,
          }}
        >
          {s.ch}
        </div>,
      );
    }
  }
  return <AbsoluteFill style={{ background: s.bg, overflow: "hidden" }}>{items}</AbsoluteFill>;
};

const Count: React.FC<{ f: number }> = ({ f }) => {
  const i = K.shots.findIndex((_, k) => f >= halfBeat(k) && f < halfBeat(k + 1));
  if (i < 0) return null;
  const s = K.shots[i];
  const a = halfBeat(i);
  const len = halfBeat(i + 1) - a;
  const t = f - a;
  const p = t / len;
  return (
    <>
      {s.kind === "glyph" && <GlyphShot s={s} p={p} />}
      {s.kind === "wall" && <WallShot s={s} t={t} seed={i} />}
      {s.kind === "burst" && <BurstShot s={s} p={p} seed={i} />}
      {s.kind === "rings" && <RingsShot s={s} t={t} />}
    </>
  );
};

// ---------- The name ----------

// "Phillips" (the reference's "Machine"): letters pop in big and scattered, P first,
// then gather into a line that keeps playful heights and sizes.
const PhillipsScene: React.FC<{ f: number }> = ({ f }) => {
  const P = N.phillips;
  const t = f - halfBeat(T.phillips);
  const letters = P.text.split("");
  const order = [0, ...letters.map((_, i) => i).slice(1).sort((a, b) => rnd(a + 71) - rnd(b + 71))];
  const asm = interpolate(t, [P.assembleAt, P.assembleAt + P.assembleFrames], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const q = 1 - asm;
  return (
    <AbsoluteFill style={{ background: P.bg, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", alignItems: "center", fontFamily: P.font, fontWeight: P.weight, fontSize: P.size, lineHeight: 1, color: P.ink }}>
        {letters.map((ch, i) => {
          const appear = P.blackFrames + order.indexOf(i) * P.letterGap;
          const sx = (rnd(i * 3 + 5) * 2 - 1) * P.scatter.x;
          const sy = (rnd(i * 5 + 2) * 2 - 1) * P.scatter.y;
          const ss = P.scatter.sizeMin + rnd(i + 37) * (P.scatter.sizeMax - P.scatter.sizeMin);
          const ry = (rnd(i + 51) * 2 - 1) * P.rest.y * P.size;
          const rs = P.rest.sizeMin + rnd(i + 63) * (P.rest.sizeMax - P.rest.sizeMin);
          const y = ry + (sy - ry) * q;
          const sc = rs + (ss - rs) * q;
          return (
            <span key={i} style={{ display: "inline-block", opacity: t >= appear ? 1 : 0, transform: `translate(${sx * q}px, ${y}px) scale(${sc})` }}>
              {ch}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// "Digital" (the reference's "Analogue"): rows of the word swelling smoothly thin <-> heavy.
const DigitalScene: React.FC<{ f: number }> = ({ f }) => {
  const D = N.digital;
  const t = f - halfBeat(T.digital);
  return (
    <AbsoluteFill style={{ background: D.bg, alignItems: "center", justifyContent: "center" }}>
      {Array.from({ length: D.rows }).map((_, r) => {
        const v = 0.5 + 0.5 * Math.sin(t * D.swellSpeed + r * D.rowPhase);
        return (
          <div key={r} style={{ fontFamily: D.font, fontWeight: weightAt(100, 900, v), fontSize: D.size, lineHeight: D.lineHeight, letterSpacing: "-0.02em", color: D.ink }}>
            {D.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// "Project" (the reference's "Razor"): heavy italic typed letter by letter.
const ProjectScene: React.FC<{ f: number }> = ({ f }) => {
  const R = N.project;
  const t = f - halfBeat(T.project);
  return (
    <AbsoluteFill style={{ background: R.bg, alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", fontFamily: R.font, fontWeight: R.weight, fontStyle: "italic", fontSize: R.size, lineHeight: 1, color: R.ink }}>
        {R.text.split("").map((ch, i) => {
          const s = i * R.framesPerLetter;
          const p = interpolate(t, [s, s + R.letterEnter], [0, 1], { ...clamp, easing: outExp });
          return (
            <span key={i} style={{ display: "inline-block", opacity: t >= s ? 1 : 0, transform: `translateX(${(1 - p) * 60}px) scaleX(${1 + (1 - p) * 0.6})`, transformOrigin: "left center" }}>
              {ch}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Lockup (the reference's "Gosh"): colours flash on every half-beat with echo copies behind,
// then the echoes fold in and it lands, dead still.
const Lockup: React.FC<{ f: number }> = ({ f }) => {
  const L = N.lockup;
  const flashIdx = L.flashes.findIndex((_, k) => f >= halfBeat(T.lockup + k) && f < halfBeat(T.lockup + k + 1));
  const landF = halfBeat(T.land);
  const look = flashIdx >= 0 ? L.flashes[flashIdx] : { ...L.final, echo: L.final.ink };
  const fold = interpolate(f, [landF, landF + L.settleFrames], [1, 0], { ...clamp, easing: outExp });
  const block = (key: string, style: React.CSSProperties) => (
    <AbsoluteFill key={key} style={{ alignItems: "center", justifyContent: "center", ...style }}>
      {L.lines.map((ln, i) => (
        <div key={i} style={{ fontFamily: ln.font, fontWeight: ln.weight, fontStyle: ln.italic ? "italic" : "normal", fontSize: ln.size, lineHeight: L.lineHeight, letterSpacing: "-0.03em" }}>
          {ln.text}
        </div>
      ))}
    </AbsoluteFill>
  );
  return (
    <AbsoluteFill style={{ background: look.bg }}>
      {fold > 0.001 &&
        Array.from({ length: L.echo.copies })
          .map((_, k) => L.echo.copies - k)
          .map((k) =>
            block(`e${k}`, {
              color: look.echo,
              WebkitTextStroke: `${L.echo.stroke}px ${look.bg}`,
              paintOrder: "stroke fill",
              transform: `translate(${L.echo.step[0] * k * fold}px, ${L.echo.step[1] * k * fold}px)`,
            }),
          )}
      {block("main", { color: look.ink, WebkitTextStroke: fold > 0.001 ? `${L.echo.stroke}px ${look.bg}` : undefined, paintOrder: "stroke fill" })}
    </AbsoluteFill>
  );
};

// Multiply shade: every frame darkens toward the bottom, like the reference.
const Shade: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `linear-gradient(180deg, #FFFFFF 0%, #FFFFFF ${K.shade.from * 100}%, ${K.shade.to} 100%)`,
      mixBlendMode: "multiply",
      pointerEvents: "none",
    }}
  />
);

const Scenes: React.FC = () => {
  const f = useCurrentFrame();
  const at = (i: number) => halfBeat(i);
  return (
    <AbsoluteFill>
      {f < at(T.shotsEnd) && <Count f={f} />}
      {f >= at(T.phillips) && f < at(T.digital) && <PhillipsScene f={f} />}
      {f >= at(T.digital) && f < at(T.project) && <DigitalScene f={f} />}
      {f >= at(T.project) && f < at(T.lockup) && <ProjectScene f={f} />}
      {f >= at(T.lockup) && <Lockup f={f} />}
      <Shade />
    </AbsoluteFill>
  );
};

export const KineticSymbols: React.FC = () => (
  <AbsoluteFill style={{ background: K.colors.black }}>
    <Scenes />
    <Audio src={staticFile(K.audio.beat)} volume={K.audio.beatVolume} />
    {/* One impact as the lockup lands (peak about a frame after the picture). */}
    <Sequence from={halfBeat(T.land) - 1}>
      <Audio src={staticFile(K.audio.landSfx)} volume={K.audio.landVolume} />
    </Sequence>
  </AbsoluteFill>
);
