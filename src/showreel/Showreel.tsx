// Phillips Digital showreel (84 s). The archive boots, teases dark work, cuts on the music's hits through all 30
// projects (tag + archive bar show which one and how far we are), breaks down, peaks, overloads, then the real logo.
import React from "react";
import { AbsoluteFill, Audio, Easing, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, continueRender, delayRender } from "remotion";
import { showreelConfig as C } from "./config";
import timeline from "./timeline.json";

type Clip = { project: string; file: string; n: number; name: string; disc: string; from: number; dur: number; srcIn: number; section: string; tag: boolean };
const T = timeline as unknown as { total: number; sections: Record<string, number>; clips: Clip[]; hits: number[] };
const W = C.output.width, H = C.output.height, K = C.colours;
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const rnd = (s: number) => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const mono = C.fonts.mono.family, head = C.fonts.head.family;

const fontHandle = delayRender("fonts");
Promise.all(Object.values(C.fonts).map((f) => new FontFace(f.family, `url(${staticFile(f.file)})`, { weight: f.weight }).load().then((ff) => document.fonts.add(ff))))
  .then(() => continueRender(fontHandle));

// first frame each project appears (for the archive bar)
const firstSeen: Record<number, number> = {};
for (const c of T.clips) if (firstSeen[c.n] === undefined || c.from < firstSeen[c.n]) firstSeen[c.n] = c.from;
// cuts that get a data tear
const tearAt = new Set<number>();
T.clips.filter((c) => c.section === "build").forEach((c, i) => { if (i % C.tearEvery === 0) tearAt.add(c.from); });
T.clips.filter((c) => ["break", "rebuild", "hero", "overload"].includes(c.section)).forEach((c) => tearAt.add(c.from));
const flashAt = [T.sections.drop, T.sections.peak, T.sections.hero];

const Video: React.FC<{ c: Clip; style?: React.CSSProperties }> = ({ c, style }) => (
  <OffthreadVideo src={staticFile(`showreel/${c.file}.mp4`)} trimBefore={c.srcIn} muted style={{ width: W, height: H, objectFit: "cover", ...style }} />
);

// one shot: slow push-in, section grade, and a data tear (sliced, RGB-split copies) for its first frames
const Shot: React.FC<{ c: Clip }> = ({ c }) => {
  const f = useCurrentFrame();
  const look = C.look[c.section] ?? C.look.build;
  const s = 1 + look.push * interpolate(f, [0, c.dur], [0, 1], { easing: Easing.inOut(Easing.quad) });
  const tear = tearAt.has(c.from) && f < C.tearFrames ? 1 - f / C.tearFrames : 0;
  const bands = 7;
  return (
    <AbsoluteFill style={{ filter: look.filter, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${s})` }}>
        {tear > 0 ? (
          <>
            {Array.from({ length: bands }, (_, i) => {
              const y0 = (i / bands) * 100, y1 = ((i + 1) / bands) * 100;
              const dx = (rnd(c.from * 13 + i * 7 + f) - 0.5) * 220 * tear;
              return (
                <AbsoluteFill key={i} style={{ clipPath: `inset(${y0}% 0 ${100 - y1}% 0)`, transform: `translateX(${dx}px)` }}>
                  <Video c={c} />
                </AbsoluteFill>
              );
            })}
            <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.55 * tear, transform: `translateX(${18 * tear}px)` }}>
              <Video c={c} style={{ filter: "sepia(1) saturate(6) hue-rotate(-50deg)" }} />
            </AbsoluteFill>
            <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.55 * tear, transform: `translateX(${-18 * tear}px)` }}>
              <Video c={c} style={{ filter: "sepia(1) saturate(6) hue-rotate(140deg)" }} />
            </AbsoluteFill>
          </>
        ) : (
          <Video c={c} />
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// typed terminal line
const Typed: React.FC<{ text: string; at: number; y: number; f: number; colour: string }> = ({ text, at, y, f, colour }) => {
  const n = Math.floor(clamp((f - at) * C.boot.charsPerFrame, 0, text.length));
  if (f < at) return null;
  return <div style={{ position: "absolute", left: 160, top: y, fontFamily: mono, fontSize: 40, color: colour, whiteSpace: "pre" }}>{text.slice(0, n)}</div>;
};

const Boot: React.FC = () => {
  const f = useCurrentFrame(), B = C.boot;
  const count = Math.round(interpolate(f, [B.countFrom, B.countTo], [0, 30], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const last = B.lines.filter((l) => f >= l.at).pop();
  const lineIdx = last ? B.lines.indexOf(last) : 0;
  const cursorX = 160 + (last ? Math.min(last.text.length, (f - last.at) * B.charsPerFrame) : 0) * 24;
  const blink = Math.floor(f / 8) % 2 === 0;
  const g = f >= B.glitchFrom ? (f - B.glitchFrom + 1) / (150 - B.glitchFrom) : 0;
  return (
    <AbsoluteFill style={{ background: K.black, transform: g ? `translateX(${(rnd(f) - 0.5) * 60 * g}px)` : undefined, opacity: g ? 1 - g * 0.6 : 1 }}>
      {B.lines.map((l, i) => <Typed key={i} text={l.text} at={l.at} y={400 + i * 72} f={f} colour={i === 2 ? K.lime : K.white} />)}
      {f >= B.countFrom && (
        <div style={{ position: "absolute", left: 160 + 24 * 23, top: 400 + 72, fontFamily: mono, fontSize: 40, color: K.lime }}>
          [{String(count).padStart(2, "0")}/30]
        </div>
      )}
      {blink && <div style={{ position: "absolute", left: cursorX + 6, top: 404 + lineIdx * 72, width: 22, height: 40, background: K.lime }} />}
    </AbsoluteFill>
  );
};

// project tag: number, name, discipline; slides up out of a mask, then holds still
const Tag: React.FC<{ c: Clip }> = ({ c }) => {
  const f = useCurrentFrame(), G = C.tag;
  const k = interpolate(f, [0, G.slideFrames], [1, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.exp) });
  const out = interpolate(f, [c.dur - 3, c.dur], [1, 0], { extrapolateLeft: "clamp" });
  const row = (child: React.ReactNode, delay: number, h: number) => (
    <div style={{ overflow: "hidden", height: h }}>
      <div style={{ transform: `translateY(${interpolate(f - delay, [0, G.slideFrames], [h, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.exp) })}px)` }}>{child}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: G.x, bottom: G.bottom, opacity: out * (1 - 0 * k), textShadow: "0 2px 18px rgba(0,0,0,0.65)" }}>
      {row(<span style={{ fontFamily: mono, fontSize: G.numSize, color: K.lime }}>{String(c.n).padStart(2, "0")} / 30</span>, 0, G.numSize * 1.3)}
      {row(<span style={{ fontFamily: head, fontSize: G.nameSize, color: K.white, letterSpacing: 1 }}>{c.name}</span>, 2, G.nameSize * 1.25)}
      {row(<span style={{ fontFamily: mono, fontSize: G.discSize, color: "rgba(242,242,238,0.75)", letterSpacing: 3 }}>{c.disc}</span>, 4, G.discSize * 1.4)}
    </div>
  );
};

// archive bar: 30 ticks; grey once loaded (boot), lime once shown, the current one tall
const ArchiveBar: React.FC<{ f: number; current: number | null }> = ({ f, current }) => {
  const Bc = C.bar, n = 30, w = (W - Bc.x - Bc.right - Bc.gap * (n - 1)) / n;
  const loaded = Math.round(interpolate(f, [C.boot.countFrom, C.boot.countTo], [0, 30], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  return (
    <>
      {Array.from({ length: n }, (_, i) => {
        const num = i + 1, seen = firstSeen[num] !== undefined && f >= firstSeen[num];
        const cur = current === num, h = cur ? Bc.litH : Bc.h;
        const bg = seen ? K.lime : i < loaded ? K.dim : "rgba(242,242,238,0.10)";
        return <div key={i} style={{ position: "absolute", left: Bc.x + i * (w + Bc.gap), bottom: Bc.bottom, width: w, height: h, background: bg, opacity: seen && !cur ? 0.7 : 1 }} />;
      })}
    </>
  );
};

const Logo: React.FC = () => {
  const f = useCurrentFrame(), L = C.logo;
  const s = L.scale, ox = W / 2 - (L.imgW * s) / 2, oy = L.centreY - (L.imgH * s) / 2;
  const piece = (p: { x0: number; y0: number; x1: number; y1: number }, style: React.CSSProperties, inner?: React.CSSProperties) => (
    <div style={{ position: "absolute", left: ox + p.x0 * s, top: oy + p.y0 * s, width: (p.x1 - p.x0) * s, height: (p.y1 - p.y0) * s, overflow: "hidden", ...style }}>
      <Img src={staticFile(L.image)} style={{ position: "absolute", left: -p.x0 * s, top: -p.y0 * s, width: L.imgW * s, height: L.imgH * s, ...inner }} />
    </div>
  );
  // circle: damped spring scale-in with a small turn
  const t = Math.max(0, f - L.circle.at), z = 0.62, w0 = 0.42, wd = w0 * Math.sqrt(1 - z * z);
  const sp = f < L.circle.at ? 0 : 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + ((z * w0) / wd) * Math.sin(wd * t));
  const wipe = (at: number) => interpolate(f, [at, at + 10], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.exp) });
  const words = L.tagline.text.split(" ");
  return (
    <AbsoluteFill style={{ background: K.cream }}>
      {piece(L.circle, { transform: `scale(${sp}) rotate(${(1 - sp) * -25}deg)`, transformOrigin: "50% 50%" })}
      {piece(L.line1, { clipPath: `inset(0 ${100 - wipe(L.line1.at)}% 0 0)` })}
      {piece(L.line2, { clipPath: `inset(0 ${100 - wipe(L.line2.at)}% 0 0)` })}
      <div style={{ position: "absolute", top: L.tagline.y, width: W, textAlign: "center", fontFamily: head, fontSize: L.tagline.size, color: K.ink }}>
        {words.map((wd2, i) => {
          const at = L.tagline.at + i * L.tagline.wordGap, k = clamp((f - at) / 4);
          return <span key={i} style={{ display: "inline-block", marginRight: 16, opacity: k, filter: `blur(${(1 - k) * 6}px)` }}>{wd2}</span>;
        })}
      </div>
      <div style={{ position: "absolute", top: L.sub.y, width: W, textAlign: "center", fontFamily: mono, fontSize: L.sub.size, letterSpacing: 8, color: "rgba(18,32,26,0.6)", opacity: clamp((f - L.sub.at) / 8) }}>{L.sub.text}</div>
    </AbsoluteFill>
  );
};

export const Showreel: React.FC = () => {
  const f = useCurrentFrame();
  const S = T.sections;
  const cur = T.clips.find((c) => f >= c.from && f < c.from + c.dur);
  const flash = Math.max(0, ...flashAt.map((a) => (f >= a && f < a + C.flashFrames ? 1 - (f - a) / C.flashFrames : 0)));
  const overloadTxt = f >= S.overload + 60 && f < S.logo - 8;
  return (
    <AbsoluteFill style={{ background: K.black }}>
      <Audio src={staticFile(C.music)} />
      <Sequence durationInFrames={150}><Boot /></Sequence>
      {T.clips.map((c, i) => (
        <Sequence key={i} from={c.from} durationInFrames={c.dur}>
          <Shot c={c} />
        </Sequence>
      ))}
      {/* vignette over the footage */}
      {f >= S.signal && f < S.logo && <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,${C.vignette}) 100%)` }} />}
      {/* project tags */}
      {T.clips.filter((c) => c.tag && c.dur >= C.tag.minFrames).map((c, i) => (
        <Sequence key={`t${i}`} from={c.from} durationInFrames={c.dur}><Tag c={c} /></Sequence>
      ))}
      {f < S.logo && <ArchiveBar f={f} current={cur ? cur.n : null} />}
      {overloadTxt && (
        <div style={{ position: "absolute", top: H / 2 - 40, width: W, textAlign: "center", fontFamily: mono, fontSize: 64, color: K.lime,
          transform: `translateX(${(rnd(f * 3) - 0.5) * 40}px)`, textShadow: `6px 0 rgba(255,0,80,0.7), -6px 0 rgba(0,255,255,0.7)` }}>{C.overloadText}</div>
      )}
      {flash > 0 && <AbsoluteFill style={{ background: "white", opacity: flash * 0.85 }} />}
      <Sequence from={S.logo} durationInFrames={T.total - S.logo}><Logo /></Sequence>
      <Sequence from={S.logo + C.logo.circle.at - 2} durationInFrames={90}><Audio src={staticFile(C.sfx.logo)} volume={0.5} /></Sequence>
      {C.boot.lines.map((l, i) => (
        <Sequence key={`b${i}`} from={l.at} durationInFrames={20}><Audio src={staticFile(C.sfx.boot)} volume={0.25} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const showreelTotal = T.total;
