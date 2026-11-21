import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { carConfig as K, C, Ev, Scene, timeline as TL } from "./config";

loadFont({ family: K.monoFont, url: staticFile("fonts/LiberationMono-Bold.ttf") });

const W = K.output.width;
const H = K.output.height;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
};

// On-screen box of a scene's car.
type Box = { x: number; y: number; w: number; h: number };
const boxOf = (s: Scene): Box => {
  const k = s.fit.width ? s.fit.width / s.w : (s.fit.height ?? s.h) / s.h;
  const w = s.w * k;
  const h = s.h * k;
  return { x: (W - w) / 2 + s.x, y: (H - h) / 2 + s.y, w, h };
};

// ---------- 5x7 pixel font (only the letters this piece uses) ----------
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
  text.split("").forEach((ch, k) => {
    (FONT[ch] ?? FONT[" "]).forEach((row, r) => row.split("").forEach((b, c) => b === "1" && out.push([k * 6 + c, r])));
  });
  return out;
};

const PixelText: React.FC<{ text: string; cell: number; cx: number; cy: number; ink: string; rowShift?: (r: number) => number }> = ({ text, cell, cx, cy, ink, rowShift }) => {
  const w = (text.length * 6 - 1) * cell;
  const x0 = cx - w / 2;
  const y0 = cy - (7 * cell) / 2;
  return (
    <>
      {cellsOf(text).map(([c, r], i) => (
        <rect key={i} x={x0 + c * cell + (rowShift?.(r) ?? 0)} y={y0 + r * cell} width={cell * 0.84} height={cell * 0.84} fill={ink} />
      ))}
    </>
  );
};

// ---------- Car layers ----------
const CarImg: React.FC<{ src: string; b: Box; style?: React.CSSProperties }> = ({ src, b, style }) => (
  <Img src={staticFile(src)} style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, ...style }} />
);

const Shadow: React.FC<{ s: Scene; b: Box }> = ({ s, b }) => {
  if (s.shadow === "none") return null;
  if (s.shadow === "top")
    return <div style={{ position: "absolute", left: b.x + b.w * 0.04, top: b.y + b.h * 0.1, width: b.w * 0.92, height: b.h * 0.9, borderRadius: "40%", background: "rgba(0,0,0,0.6)", filter: "blur(38px)" }} />;
  // floor: a flat contact shadow under the wheels
  return <div style={{ position: "absolute", left: b.x + b.w * 0.03, top: b.y + b.h - 26, width: b.w * 0.94, height: 46, borderRadius: "50%", background: "rgba(0,0,0,0.85)", filter: "blur(16px)" }} />;
};

// Anything drawn in here is clipped to the car's silhouette.
const InCar: React.FC<{ children: React.ReactNode; id: string; s: Scene; b: Box }> = ({ children, id, s, b }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
    <defs>
      <mask id={`${id}-mask`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
        <image href={staticFile(s.mask)} x={b.x} y={b.y} width={b.w} height={b.h} preserveAspectRatio="none" />
      </mask>
      <pattern id={`${id}-dY`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.yellow} />
        <rect x={4} y={4} width={4} height={4} fill={C.yellow} />
      </pattern>
      <pattern id={`${id}-dK`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.black} />
        <rect x={4} y={4} width={4} height={4} fill={C.black} />
      </pattern>
    </defs>
    <g mask={`url(#${id}-mask)`}>{children}</g>
  </svg>
);

// Big pixel letter eating the car in black (yellow dither), over a pixelated car.
const GlyphBurst: React.FC<{ ch: string; seed: number; s: Scene; b: Box }> = ({ ch, seed, s, b }) => {
  const cell = Math.min(b.h, H) / 7.4;
  const x0 = W / 2 - (5 * cell) / 2 + (rnd(seed) - 0.5) * Math.min(400, b.w * 0.3);
  const y0 = Math.max(b.y, 0) + (Math.min(b.h, H) - 7 * cell) / 2;
  return (
    <>
      <CarImg src={`${s.mosaic}mosaic_18.png`} b={b} />
      <InCar id={`g${seed}`} s={s} b={b}>
        {cellsOf(ch).map(([c, r], i) => (
          <g key={i}>
            <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={C.black} />
            <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={`url(#g${seed}-dY)`} opacity={rnd(i + seed) > 0.8 ? 0.9 : 0} />
          </g>
        ))}
      </InCar>
    </>
  );
};

const Flood: React.FC<{ seed: number; s: Scene; b: Box }> = ({ seed, s, b }) => (
  <InCar id={`f${seed}`} s={s} b={b}>
    <rect width={W} height={H} fill={C.yellow} />
    <rect x={b.x + b.w * 0.55} width={W} height={H} fill={`url(#f${seed}-dK)`} opacity={0.85} />
  </InCar>
);

const Strobe: React.FC<{ lines?: boolean; seed: number; ink: string }> = ({ lines, seed, ink }) => (
  <AbsoluteFill style={{ background: ink }}>
    {lines && (
      <svg width={W} height={H}>
        {Array.from({ length: 60 }).map((_, i) => (
          <rect key={i} x={rnd(seed + i) * W * 0.5} y={i * 18 + 6} width={W * (0.2 + rnd(seed + i + 70) * 0.8)} height={3} fill={C.black} opacity={0.85} />
        ))}
      </svg>
    )}
  </AbsoluteFill>
);

// Scanline tear: the frame sliced into strips that slide sideways, with yellow scan lines.
const Tear: React.FC<{ seed: number; t: number; s: Scene; b: Box }> = ({ seed, t, s, b }) => {
  const strips = 36;
  const sh = H / strips;
  return (
    <AbsoluteFill style={{ background: C.black }}>
      {Array.from({ length: strips }).map((_, i) => {
        const big = rnd(seed * 7 + i) > 0.7;
        const dx = (rnd(seed * 13 + i + t * 3) - 0.5) * (big ? 900 : 120);
        return (
          <div key={i} style={{ position: "absolute", left: 0, top: i * sh, width: W, height: sh + 1, overflow: "hidden" }}>
            <div style={{ position: "absolute", left: dx, top: -i * sh, width: W, height: H, filter: "brightness(0.8) contrast(1.3)" }}>
              <CarImg src={s.src} b={b} />
            </div>
            {rnd(seed + i * 3) > 0.55 && <div style={{ position: "absolute", left: rnd(i + seed) * W * 0.4, top: sh / 2, width: W * rnd(i * 5 + seed), height: 2, background: C.yellow }} />}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const Brackets: React.FC<{ b: Box }> = ({ b }) => {
  const s = K.pixel;
  const L = 5;
  const x0 = Math.max(40, b.x - 30);
  const x1 = Math.min(W - 40, b.x + b.w + 30);
  const y0 = Math.max(40, b.y - 30);
  const y1 = Math.min(H - 40, b.y + b.h + 10);
  const pts: [number, number, number, number][] = [
    [x0, y0, 1, 1],
    [x1, y0, -1, 1],
    [x0, y1, 1, -1],
    [x1, y1, -1, -1],
  ];
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {pts.map(([x, y, dx, dy], k) =>
        Array.from({ length: L }).flatMap((_, i) => [
          <rect key={`${k}h${i}`} x={x + dx * i * s - (dx < 0 ? s : 0)} y={y - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={C.yellow} />,
          <rect key={`${k}v${i}`} x={x - (dx < 0 ? s : 0)} y={y + dy * i * s - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={C.yellow} />,
        ]),
      )}
    </svg>
  );
};

const Readout: React.FC<{ text: string; t: number; corner: "tl" | "tr" | "br" }> = ({ text, t, corner }) => {
  const shown = text.slice(0, Math.max(0, Math.floor(t * 1.5)));
  return (
    <div
      style={{
        position: "absolute",
        [corner[0] === "t" ? "top" : "bottom"]: 46,
        [corner[1] === "l" ? "left" : "right"]: 56,
        fontFamily: K.monoFont,
        fontSize: 20,
        letterSpacing: "0.08em",
        color: C.yellow,
        whiteSpace: "pre",
        textShadow: "0 0 6px rgba(0,0,0,0.9)",
      }}
    >
      {shown}
      {t % 10 < 5 ? "█" : " "}
    </div>
  );
};

// ---------- Events ----------
const burstOn = (local: number) => K.flicker[local % K.flicker.length] === 1;

const EventLayer: React.FC<{ e: Ev; t: number; i: number; s: Scene; b: Box }> = ({ e, t, i, s, b }) => {
  const local = t - e.at;
  if (e.kind !== "brackets" && !burstOn(local)) return null;
  switch (e.kind) {
    case "glyph":
      return <GlyphBurst ch={e.ch} seed={i + 1} s={s} b={b} />;
    case "flood":
      return <Flood seed={i + 1} s={s} b={b} />;
    case "strobe":
      return <Strobe lines={e.lines} seed={i + local} ink={e.ink === "yellow" ? C.yellow : C.green} />;
    case "tear":
      return <Tear seed={i + 1} t={local} s={s} b={b} />;
    case "brackets":
      return <Brackets b={b} />;
    case "dots":
      return (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <PixelText text={e.text} cell={Math.min(34, b.h / 9)} cx={W / 2 + 40} cy={b.y + b.h / 2} ink={C.yellow} />
        </svg>
      );
    case "brand":
      return (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <PixelText text={K.words.brand} cell={16} cx={W / 2} cy={Math.min(b.y + b.h / 2, H / 2 + 120)} ink={C.yellow} />
        </svg>
      );
  }
};

const SceneView: React.FC<{ s: Scene; n: number; t: number }> = ({ s, n, t }) => {
  const b = boxOf(s);
  const active = s.events.map((e, i) => ({ e, i: n * 100 + i })).filter(({ e }) => t >= e.at && t < e.at + e.len);
  const fullFrame = active.some(({ e, i }) => (e.kind === "strobe" || e.kind === "tear") && burstOn(t - e.at) && i >= 0);
  return (
    <>
      <Shadow s={s} b={b} />
      <CarImg src={s.src} b={b} />
      {active.map(({ e, i }) => (
        <EventLayer key={i} e={e} t={t} i={i} s={s} b={b} />
      ))}
      {!fullFrame && (
        <>
          <Readout text={K.words.file} t={t} corner="tl" />
          <Readout text={K.words.view.replace("{n}", String(n + 1).padStart(2, "0"))} t={t - 4} corner="tr" />
          <Readout text={s.readout} t={t - 12} corner="br" />
        </>
      )}
    </>
  );
};

// ---------- End: dissolve, then the wordmark ----------
const Dissolve: React.FC<{ f: number }> = ({ f }) => {
  const s = K.scenes[K.scenes.length - 1];
  const b = boxOf(s);
  const p = (f - TL.dissolve) / K.dissolveFrames;
  const stage = p < 0.2 ? 8 : p < 0.4 ? 16 : p < 0.6 ? 32 : 64;
  const drop = interpolate(p, [0.55, 1], [0, 1], clamp);
  const bs = 64 * (b.w / s.w);
  const cols = Math.ceil(b.w / bs);
  const rows = Math.ceil(b.h / bs);
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <mask id="drop" maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          {Array.from({ length: rows * cols }).map((_, k) =>
            rnd(k * 3.7) >= drop ? <rect key={k} x={b.x + (k % cols) * bs} y={b.y + Math.floor(k / cols) * bs} width={bs + 1} height={bs + 1} fill="#fff" /> : null,
          )}
        </mask>
      </defs>
      <image href={staticFile(`${s.mosaic}mosaic_${stage}.png`)} x={b.x} y={b.y} width={b.w} height={b.h} mask="url(#drop)" preserveAspectRatio="none" />
    </svg>
  );
};

const EndMark: React.FC<{ f: number }> = ({ f }) => {
  const E = K.end;
  const t = f - TL.end;
  const glitching = t < E.glitchFrames;
  if (glitching && !burstOn(t)) return null;
  const shift = (r: number) => (glitching ? (rnd(r * 11 + t * 5) - 0.5) * 120 * (rnd(r + t) > 0.5 ? 1 : 0) : 0);
  const ink = glitching && t % 3 === 1 ? C.yellow : C.green;
  const restored = K.words.restored.slice(0, Math.max(0, Math.floor((t - E.restoredDelay) * 1.2)));
  return (
    <>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <PixelText text="PHILLIPS" cell={E.pixel} cx={W / 2} cy={H / 2 - 95} ink={ink} rowShift={shift} />
        <PixelText text="DIGITAL" cell={E.pixel} cx={W / 2} cy={H / 2 + 95} ink={ink} rowShift={(r) => shift(r + 9)} />
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: H / 2 + 235, textAlign: "center", fontFamily: K.monoFont, fontSize: 22, letterSpacing: "0.3em", color: C.yellow }}>
        {restored}
      </div>
    </>
  );
};

export const LostData: React.FC = () => {
  const f = useCurrentFrame();
  const n = TL.starts.findIndex((a, k) => f >= a && (k === TL.starts.length - 1 ? f < TL.dissolve : f < TL.starts[k + 1]));
  const fade = interpolate(f, [TL.dissolve, TL.end], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.black} 0%, ${C.black} 30%, ${C.floor} 100%)` }}>
      {n >= 0 && <SceneView s={K.scenes[n]} n={n} t={f - TL.starts[n]} />}
      {f >= TL.dissolve && f < TL.end && <Dissolve f={f} />}
      {f >= TL.dissolve && <AbsoluteFill style={{ background: C.black, opacity: fade }} />}
      {f >= TL.end && <EndMark f={f} />}

      <Audio src={staticFile(K.audio.music)} volume={K.audio.musicVolume} />
      {K.scenes.flatMap((s, si) =>
        s.events.map((e, i) => {
          const list = K.audio.sfx[e.kind] ?? [];
          if (!list.length) return null;
          return (
            <Sequence key={`${si}-${i}`} from={TL.starts[si] + e.at} durationInFrames={e.len + 3}>
              <Audio src={staticFile(list[(si + i) % list.length])} volume={K.audio.sfxVolume} />
            </Sequence>
          );
        }),
      )}
      <Sequence from={TL.end} durationInFrames={50}>
        <Audio src={staticFile(K.audio.endHit)} volume={K.audio.endHitVolume} />
      </Sequence>
    </AbsoluteFill>
  );
};
