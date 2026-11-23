import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing, continueRender, delayRender } from "remotion";
import { rubyConfig as C, RubyColor } from "./config";

const col = (c: string) => C.colors[c as RubyColor];
const pad = (n: number) => String(n).padStart(C.frames.pad, "0");
const fontHandle = typeof window !== "undefined" ? delayRender("font") : 0;
if (typeof window !== "undefined") {
  new FontFace(C.font.family, `url(${staticFile(C.font.file)})`).load().then((f) => { document.fonts.add(f); continueRender(fontHandle); });
}
// deterministic jitter for the glitch (same every render)
const rnd = (i: number) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// two-tone art painted from its masks
const Preload: React.FC = () => (
  <>{["ruby/endpose", C.logo.file].flatMap((a) => ["dark", "light"].map((k) => (
    <Img key={a + k} src={staticFile(`${a}-${k}.png`)} style={{ position: "absolute", width: 1, height: 1, opacity: 0 }} />)))}</>
);
const TwoTone: React.FC<{ art: string; light: string; dark: string; style: React.CSSProperties }> = ({ art, light, dark, style }) => (
  <div style={{ position: "absolute", ...style }}>
    {(["dark", "light"] as const).map((k) => (
      <div key={k} style={{ position: "absolute", inset: 0, background: k === "dark" ? col(dark) : col(light),
        WebkitMaskImage: `url(${staticFile(`${art}-${k}.png`)})`, WebkitMaskSize: "100% 100%", maskImage: `url(${staticFile(`${art}-${k}.png`)})`, maskSize: "100% 100%" }} />
    ))}
  </div>
);

const Glitchy: React.FC<{ text: string; size: number; y: number; tracking: number; color: string; f: number; glitch: number; scale?: number; blend?: "screen" | "multiply" }> = ({ text, size, y, tracking, color, f, glitch, scale = 1, blend }) => {
  const g = glitch > 0 ? glitch : 0;
  const dx = g * (rnd(f) - 0.5) * 60, sl = g * (rnd(f + 9) - 0.5) * 30;
  const base: React.CSSProperties = { position: "absolute", left: 0, right: 0, top: y - size / 2, textAlign: "center", fontFamily: C.font.family,
    fontSize: size, lineHeight: 1, letterSpacing: tracking, transform: `scale(${scale}) skewX(${sl * 0.3}deg)` };
  return (
    <>
      {g > 0 && <div style={{ ...base, color: C.colors.red, transform: `${base.transform} translateX(${dx - 14 * g}px)`, mixBlendMode: blend ?? "screen", opacity: 0.9 }}>{text}</div>}
      {g > 0 && <div style={{ ...base, color: C.colors.cyan, transform: `${base.transform} translateX(${-dx + 14 * g}px)`, mixBlendMode: blend ?? "screen", opacity: 0.8 }}>{text}</div>}
      <div style={{ ...base, color, transform: `${base.transform} translateX(${dx * 0.3}px)`,
        clipPath: g > 0.5 && rnd(f + 3) > 0.5 ? `inset(${rnd(f + 4) * 60}% 0 ${rnd(f + 5) * 30}% 0)` : undefined }}>{text}</div>
    </>
  );
};

export const RubyFilm: React.FC = () => {
  const f = useCurrentFrame() + 1;                     // Blender frame numbers start at 1
  const { width: W, height: H } = C.output;
  const fs = C.flickerStart, fe = fs + C.flicker.length * C.flickerStep;

  if (f < fs) {
    const t = C.title, since = f - t.in;
    const vis = since >= 0 && !(since < t.glitchFrames && [1, 4, 5].includes(since));
    const slam = since >= 0 ? interpolate(since, [0, 6], [t.slam, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.exp) }) : 1;
    const glitch = since >= 0 ? interpolate(since, [0, t.glitchFrames, t.glitchFrames + 14], [1, 0.25, 0], { extrapolateRight: "clamp" }) : 0;
    return (
      <AbsoluteFill style={{ background: "black" }}>
        <Img src={staticFile(`${C.frames.dir}/f_${pad(Math.min(f, C.frames.last3d))}.png`)} style={{ width: W, height: H }} />
        {vis && <Glitchy text={C.word} size={t.size} y={t.y} tracking={t.tracking} color={col(t.color)} f={f} glitch={glitch} scale={slam} blend="multiply" />}
      </AbsoluteFill>
    );
  }
  if (f < fe) {
    const i = Math.floor((f - fs) / C.flickerStep), [bg, light, dark, art] = C.flicker[i];
    const L = C.logo;
    const style: React.CSSProperties = art === "endpose" ? { left: 0, top: 0, width: W, height: H }
      : { left: W / 2 - (L.startH * L.w / L.h) / 2, top: L.startY - L.startH / 2, width: L.startH * L.w / L.h, height: L.startH };
    return (
      <AbsoluteFill style={{ background: col(bg) }}>
        <Preload />
        <TwoTone art={art === "endpose" ? "ruby/endpose" : L.file} light={light} dark={dark} style={style} />
        <Glitchy text={C.word} size={C.title.size} y={C.title.y} tracking={C.title.tracking} color={bg === "white" ? C.colors.red : C.colors.white} f={f} glitch={0.6} />
      </AbsoluteFill>
    );
  }
  // settle: white background, red-and-white emblem shrinks up, the wordmark rises in under it
  const L = C.logo, k = interpolate(f - fe, [0, L.settle], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.exp) });
  const h = L.startH + (L.endH - L.startH) * k, w = h * L.w / L.h, cy = L.startY + (L.endY - L.startY) * k;
  const wm = C.wordmark, ws = f - wm.in;
  const wmK = interpolate(ws, [0, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.exp) });
  return (
    <AbsoluteFill style={{ background: C.colors.white }}>
      <Preload />
      <TwoTone art={L.file} light="white" dark="red" style={{ left: W / 2 - w / 2, top: cy - h / 2, width: w, height: h }} />
      {ws >= 0 && !(ws < 6 && [1, 3].includes(ws)) && (
        <div style={{ opacity: wmK, transform: `translateY(${(1 - wmK) * wm.rise}px)` }}>
          <Glitchy text={C.word} size={wm.size} y={wm.y} tracking={wm.tracking} color={C.colors.red} f={f} glitch={ws < 6 ? 0.5 : 0} />
        </div>
      )}
    </AbsoluteFill>
  );
};
