import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { carConfig as K, C, Ev } from "./config";

loadFont({ family: K.monoFont, url: staticFile("fonts/LiberationMono-Bold.ttf") });

const W = K.output.width;
const H = K.output.height;
const CW = K.car.w * K.car.scale;
const CH = K.car.h * K.car.scale;
const CX = (W - CW) / 2;
const CY = (H - CH) / 2 + K.car.y;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rnd = (n: number) => {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
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
const textCols = (text: string) => text.length * 6 - 1;

// Dot-matrix text centred at (cx, cy); rowShift lets glitches slide rows sideways.
const PixelText: React.FC<{ text: string; cell: number; cx: number; cy: number; ink: string; rowShift?: (r: number) => number; gap?: number }> = ({ text, cell, cx, cy, ink, rowShift, gap = 0.16 }) => {
  const w = textCols(text) * cell;
  const x0 = cx - w / 2;
  const y0 = cy - (7 * cell) / 2;
  return (
    <>
      {cellsOf(text).map(([c, r], i) => (
        <rect key={i} x={x0 + c * cell + (rowShift?.(r) ?? 0)} y={y0 + r * cell} width={cell * (1 - gap)} height={cell * (1 - gap)} fill={ink} />
      ))}
    </>
  );
};

// ---------- Car layers ----------
const CarImg: React.FC<{ src?: string; style?: React.CSSProperties }> = ({ src = K.car.src, style }) => (
  <Img src={staticFile(src)} style={{ position: "absolute", left: CX, top: CY, width: CW, height: CH, ...style }} />
);

const Shadow: React.FC = () => (
  <div style={{ position: "absolute", left: CX + CW * 0.04, top: CY + CH * 0.1, width: CW * 0.92, height: CH * 0.9, borderRadius: "40%", background: "rgba(0,0,0,0.55)", filter: "blur(38px)" }} />
);

// Anything drawn in here is clipped to the car's silhouette.
const InCar: React.FC<{ children: React.ReactNode; id: string }> = ({ children, id }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
    <defs>
      <mask id={`${id}-mask`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
        <image href={staticFile(K.car.mask)} x={CX} y={CY} width={CW} height={CH} preserveAspectRatio="none" />
      </mask>
      <pattern id={`${id}-dither`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.green} />
        <rect x={4} y={4} width={4} height={4} fill={C.green} />
      </pattern>
      <pattern id={`${id}-ditherK`} width={8} height={8} patternUnits="userSpaceOnUse">
        <rect width={4} height={4} fill={C.black} />
        <rect x={4} y={4} width={4} height={4} fill={C.black} />
      </pattern>
    </defs>
    <g mask={`url(#${id}-mask)`}>{children}</g>
  </svg>
);

// Big pixel letter eating the car in green (over a pixelated car).
const GlyphBurst: React.FC<{ ch: string; seed: number }> = ({ ch, seed }) => {
  const cell = CH / 7.4;
  const x0 = W / 2 - (5 * cell) / 2 + (rnd(seed) - 0.5) * 300;
  const y0 = CY + (CH - 7 * cell) / 2;
  const cells = cellsOf(ch);
  return (
    <>
      <CarImg src="car/mosaic_18.png" />
      <InCar id={`g${seed}`}>
        {cells.map(([c, r], i) => (
          <g key={i}>
            <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={C.black} />
            <rect x={x0 + c * cell} y={y0 + r * cell} width={cell + 1} height={cell + 1} fill={`url(#g${seed}-dither)`} opacity={rnd(i + seed) > 0.8 ? 0.9 : 0} />
          </g>
        ))}
      </InCar>
    </>
  );
};

const Flood: React.FC<{ seed: number }> = ({ seed }) => (
  <InCar id={`f${seed}`}>
    <rect width={W} height={H} fill={C.white} />
    <rect x={CX + CW * 0.55} width={CW} height={H} fill={`url(#f${seed}-ditherK)`} opacity={0.8} />
  </InCar>
);

const Strobe: React.FC<{ lines?: boolean; seed: number }> = ({ lines, seed }) => (
  <AbsoluteFill style={{ background: C.green }}>
    {lines && (
      <svg width={W} height={H}>
        {Array.from({ length: 60 }).map((_, i) => {
          const y = i * 18 + 6;
          const x = rnd(seed + i) * W * 0.5;
          return <rect key={i} x={x} y={y} width={W * (0.2 + rnd(seed + i + 70) * 0.8)} height={3} fill={C.black} opacity={0.85} />;
        })}
      </svg>
    )}
  </AbsoluteFill>
);

// Scanline tear: the frame sliced into strips that slide sideways, with white scan lines.
const Tear: React.FC<{ seed: number; t: number }> = ({ seed, t }) => {
  const strips = 36;
  const sh = H / strips;
  return (
    <AbsoluteFill style={{ background: C.black }}>
      {Array.from({ length: strips }).map((_, i) => {
        const big = rnd(seed * 7 + i) > 0.7;
        const dx = (rnd(seed * 13 + i + t * 3) - 0.5) * (big ? 900 : 120);
        return (
          <div key={i} style={{ position: "absolute", left: 0, top: i * sh, width: W, height: sh + 1, overflow: "hidden" }}>
            <div style={{ position: "absolute", left: dx, top: -i * sh, width: W, height: H, filter: "grayscale(1) contrast(1.6) brightness(0.8)" }}>
              <CarImg />
            </div>
            {rnd(seed + i * 3) > 0.55 && <div style={{ position: "absolute", left: rnd(i + seed) * W * 0.4, top: sh / 2, width: W * rnd(i * 5 + seed), height: 2, background: C.white }} />}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const Brackets: React.FC = () => {
  const s = K.pixel;
  const L = 5; // cells per arm
  const pts: [number, number, number, number][] = [
    [CX - 30, CY - 30, 1, 1],
    [CX + CW + 30, CY - 30, -1, 1],
    [CX - 30, CY + CH + 10, 1, -1],
    [CX + CW + 30, CY + CH + 10, -1, -1],
  ];
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {pts.map(([x, y, dx, dy], k) =>
        Array.from({ length: L }).flatMap((_, i) => [
          <rect key={`${k}h${i}`} x={x + dx * i * s - (dx < 0 ? s : 0)} y={y - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={dy > 0 ? C.white : C.black} />,
          <rect key={`${k}v${i}`} x={x - (dx < 0 ? s : 0)} y={y + dy * i * s - (dy < 0 ? s : 0)} width={s * 0.8} height={s * 0.8} fill={dy > 0 ? C.white : C.black} />,
        ]),
      )}
    </svg>
  );
};

const Readout: React.FC<{ text: string; from: number; f: number; corner: "tl" | "tr" | "bl" | "br" }> = ({ text, from, f, corner }) => {
  const shown = text.slice(0, Math.max(0, Math.floor((f - from) * 1.5)));
  const top = corner[0] === "t";
  const left = corner[1] === "l";
  return (
    <div
      style={{
        position: "absolute",
        [top ? "top" : "bottom"]: 48,
        [left ? "left" : "right"]: 56,
        fontFamily: K.monoFont,
        fontSize: 20,
        letterSpacing: "0.08em",
        color: top ? C.white : C.black,
        whiteSpace: "pre",
      }}
    >
      {shown}
      {f % 10 < 5 ? "█" : " "}
    </div>
  );
};

// ---------- Events ----------
const burstOn = (local: number) => K.flicker[local % K.flicker.length] === 1;

const EventLayer: React.FC<{ e: Ev; f: number; i: number }> = ({ e, f, i }) => {
  const local = f - e.at;
  if (e.kind !== "brackets" && !burstOn(local)) return null;
  switch (e.kind) {
    case "glyph":
      return <GlyphBurst ch={e.ch} seed={i + 1} />;
    case "flood":
      return <Flood seed={i + 1} />;
    case "strobe":
      return <Strobe lines={e.lines} seed={i + local} />;
    case "tear":
      return <Tear seed={i + 1} t={local} />;
    case "brackets":
      return <Brackets />;
    case "dots":
      return (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <PixelText text={e.text} cell={34} cx={W / 2 + 40} cy={CY + CH / 2} ink={C.white} />
        </svg>
      );
    case "brand":
      return (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          <PixelText text={K.words.brand} cell={16} cx={W / 2} cy={CY + CH / 2} ink={C.white} />
        </svg>
      );
  }
};

// ---------- End: dissolve, then the wordmark ----------
const Dissolve: React.FC<{ f: number }> = ({ f }) => {
  const D = K.dissolve;
  const p = (f - D.start) / (D.end - D.start);
  const stage = p < 0.2 ? 8 : p < 0.4 ? 16 : p < 0.6 ? 32 : 64;
  const drop = interpolate(p, [0.55, 1], [0, 1], clamp);
  const b = 64 * K.car.scale;
  const cols = Math.ceil(CW / b);
  const rows = Math.ceil(CH / b);
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <defs>
        <mask id="drop" maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          {Array.from({ length: rows * cols }).map((_, k) =>
            rnd(k * 3.7) >= drop ? <rect key={k} x={CX + (k % cols) * b} y={CY + Math.floor(k / cols) * b} width={b + 1} height={b + 1} fill="#fff" /> : null,
          )}
        </mask>
      </defs>
      <image href={staticFile(`car/mosaic_${stage}.png`)} x={CX} y={CY} width={CW} height={CH} mask="url(#drop)" preserveAspectRatio="none" />
    </svg>
  );
};

const EndMark: React.FC<{ f: number }> = ({ f }) => {
  const E = K.end;
  const t = f - E.start;
  const glitching = t < E.glitchFrames;
  if (glitching && !burstOn(t)) return null;
  const shift = (r: number) => (glitching ? (rnd(r * 11 + t * 5) - 0.5) * 120 * (rnd(r + t) > 0.5 ? 1 : 0) : 0);
  const restored = K.words.restored.slice(0, Math.max(0, Math.floor((f - E.restoredAt) * 1.2)));
  return (
    <>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <PixelText text="PHILLIPS" cell={E.pixel * 1.25} cx={W / 2} cy={H / 2 - 95} ink={glitching && t % 3 === 1 ? C.white : C.green} rowShift={shift} />
        <PixelText text="DIGITAL" cell={E.pixel * 1.25} cx={W / 2} cy={H / 2 + 95} ink={glitching && t % 3 === 1 ? C.white : C.green} rowShift={(r) => shift(r + 9)} />
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: H / 2 + 230, textAlign: "center", fontFamily: K.monoFont, fontSize: 22, letterSpacing: "0.3em", color: C.white }}>
        {restored}
      </div>
    </>
  );
};

export const LostData: React.FC = () => {
  const f = useCurrentFrame();
  const D = K.dissolve;
  const fade = interpolate(f, [D.start, D.end], [0, 1], clamp);
  const active = K.events.map((e, i) => ({ e, i })).filter(({ e }) => f >= e.at && f < e.at + e.len);
  const fullFrame = active.some(({ e }) => (e.kind === "strobe" || e.kind === "tear") && burstOn(f - e.at));
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.black} 0%, ${C.black} 22%, ${C.floor} 100%)` }}>
      {f < D.start && (
        <>
          <Shadow />
          <CarImg />
        </>
      )}
      {f >= D.start && f < D.end && <Dissolve f={f} />}
      <AbsoluteFill style={{ background: C.black, opacity: fade }} />
      {f < D.start && active.map(({ e, i }) => <EventLayer key={i} e={e} f={f} i={i} />)}
      {f < D.start && !fullFrame &&
        K.readouts.filter(([, a, b]) => f >= a && f < b).map(([ti, a, , corner]) => <Readout key={ti} text={K.words.readouts[ti]} from={a} f={f} corner={corner} />)}
      {f >= K.end.start && <EndMark f={f} />}

      <Audio src={staticFile(K.audio.music)} volume={K.audio.musicVolume} />
      {K.events.map((e, i) => {
        const list = K.audio.sfx[e.kind] ?? [];
        if (!list.length) return null;
        return (
          <Sequence key={i} from={e.at} durationInFrames={e.len + 3}>
            <Audio src={staticFile(list[i % list.length])} volume={K.audio.sfxVolume} />
          </Sequence>
        );
      })}
      <Sequence from={K.end.start} durationInFrames={50}>
        <Audio src={staticFile(K.audio.endHit)} volume={K.audio.endHitVolume} />
      </Sequence>
    </AbsoluteFill>
  );
};
