import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing, random } from "remotion";
import { pd01Config as C } from "./config";
import { PD01HUD, HudStart } from "./PD01";

// PD-01 motion: 3D plates (public/pd01/seq/f_####.png, one per frame) + background story + HUD + glitches + logo end card.
const A = C.anim;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const s2f = (s: number) => Math.round(s * C.fps);

const Glitch: React.FC<{ at: number[]; children: React.ReactNode }> = ({ at, children }) => {
  const f = useCurrentFrame();
  const hit = at.find((t) => f >= s2f(t) && f < s2f(t) + A.glitchFrames);
  if (hit === undefined) return <>{children}</>;
  const k = f - s2f(hit); const slices = 7;
  return (
    <AbsoluteFill>
      {Array.from({ length: slices }).map((_, i) => {
        const dx = (random(`g${hit}-${k}-${i}`) - 0.5) * 120; const top = (i / slices) * 100;
        return (
          <AbsoluteFill key={i} style={{ clipPath: `inset(${top}% 0 ${100 - top - 100 / slices}% 0)`, transform: `translateX(${dx}px)` }}>
            <AbsoluteFill style={{ transform: "translateX(-8px)", mixBlendMode: "screen", filter: "drop-shadow(8px 0 0 rgba(255,26,140,0.8))" }}>{children}</AbsoluteFill>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

export const PD01Anim: React.FC<{ seq?: string }> = ({ seq = "pd01/seq" }) => {
  const f = useCurrentFrame();
  const flood = interpolate(f, [s2f(A.floodAt), s2f(A.floodAt) + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const endT = s2f(A.logoAt);
  const plateOut = interpolate(f, [endT, endT + 6], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoIn = interpolate(f, [endT + 4, endT + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const words = interpolate(f, [endT + 12, endT + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const frameNo = String(Math.min(f + 1, C.fps * C.durationInSeconds)).padStart(4, "0");
  const col = C.colors;
  return (
    <AbsoluteFill style={{ background: A.dark }}>
      {/* the electric-blue page floods in from the centre as the orbit starts */}
      <AbsoluteFill style={{ background: col.page, clipPath: `circle(${flood * 120}% at 56% 45%)` }} />
      <AbsoluteFill style={{ opacity: flood, background: `radial-gradient(ellipse 46% 60% at 56% 42%, ${col.glow} 0%, rgba(26,43,255,0) 70%)` }} />
      <AbsoluteFill style={{ opacity: flood, background: `radial-gradient(ellipse 85% 85% at 55% 45%, rgba(0,0,0,0) 55%, ${col.vignette} 100%)` }} />
      <Glitch at={A.glitches}>
        <AbsoluteFill style={{ opacity: plateOut }}>
          {f < endT + 8 && <Img src={staticFile(`${seq}/f_${frameNo}.png`)} style={{ width: 1920, height: 1080 }} />}
        </AbsoluteFill>
        <AbsoluteFill style={{ opacity: plateOut }}>
          <HudStart.Provider value={A.hudAt}><PD01HUD overlayOnly /></HudStart.Provider>
        </AbsoluteFill>
      </Glitch>
      {/* end card: the Phillips Digital logo */}
      {f >= endT && (
        <AbsoluteFill style={{ background: A.dark, opacity: logoIn, alignItems: "center", justifyContent: "center" }}>
          <Img src={staticFile("pd01/logo_circle.png")} style={{ width: 300, height: 300, transform: `scale(${0.6 + 0.4 * logoIn}) rotate(${(1 - logoIn) * -40}deg)`, marginBottom: 40 }} />
          <div style={{ clipPath: `inset(0 ${100 - words * 100}% 0 0)` }}><Img src={staticFile("pd01/logo_wordmark.png")} style={{ width: 620 }} /></div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
