import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing, random } from "remotion";
import { pd01Config as C } from "./config";
import { PD01HUD, HudStart } from "./PD01";
import { VisorHUD } from "./VisorHUD";

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
          {f >= s2f(A.outlineAt) && f < endT + 8 && (() => {
            const k = f - s2f(A.outlineAt); const on = k % 5 !== 3 && (random(`ol${f}`) > 0.15 || k > 10);
            const c1 = (Math.floor(k / 2) % 2 === 0) ? col.pink : A.blue; const c2 = c1 === col.pink ? A.blue : col.pink;
            const w = 6 + Math.min(k, 18) * 0.35; const split = (random(`os${f}`) - 0.5) * 10;
            const ring = (c: string) => `drop-shadow(${w}px 0 0 ${c}) drop-shadow(-${w}px 0 0 ${c}) drop-shadow(0 ${w}px 0 ${c}) drop-shadow(0 -${w}px 0 ${c}) drop-shadow(0 0 22px ${c})`;
            const src = staticFile(`${seq}/f_${frameNo}.png`);
            return on ? (<>
              <Img src={src} style={{ position: "absolute", width: 1920, height: 1080, filter: `brightness(0) ${ring(c2)}`, transform: `translateX(${split}px)`, opacity: 0.9 }} />
              <Img src={src} style={{ position: "absolute", width: 1920, height: 1080, filter: `brightness(0) ${ring(c1)}` }} />
              <Img src={src} style={{ position: "absolute", width: 1920, height: 1080 }} />
            </>) : null;
          })()}
        </AbsoluteFill>
        <AbsoluteFill style={{ opacity: plateOut }}>
          <HudStart.Provider value={A.hudAt}><PD01HUD overlayOnly /></HudStart.Provider>
        </AbsoluteFill>
      </Glitch>
      <Glitch at={A.glitches}><VisorHUD /></Glitch>
      {/* end card: logo outline flickers pink/blue, then snaps solid pink with a flash; wordmark settles from an RGB split */}
      {f >= endT && (() => {
        const k = f - endT; const solidAt = A.logoSolid;
        const solid = k >= solidAt; const flash = solid ? interpolate(k, [solidAt, solidAt + 6], [0.85, 0], { extrapolateRight: "clamp" }) : 0;
        const on = solid || k < 3 || random(`lo${f}`) > 0.3; const cA = Math.floor(k / 2) % 2 === 0 ? col.pink : A.blue; const cB = cA === col.pink ? A.blue : col.pink;
        const sc = solid ? 1 + 0.06 * Math.exp(-(k - solidAt) / 4) : 0.96 + 0.04 * (k / solidAt);
        const wk = Math.max(0, k - solidAt - 2); const wordIn = interpolate(wk, [0, 10], [0, 1], { extrapolateRight: "clamp", easing: ease });
        const split = (1 - wordIn) * 14;
        return (
          <AbsoluteFill style={{ background: A.dark, opacity: logoIn, alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "relative", width: 300, height: 300, marginBottom: 40, transform: `scale(${sc})` }}>
              {!solid && on && (<svg width={300} height={300} style={{ position: "absolute", overflow: "visible" }}>
                <circle cx={150 + 4} cy={150} r={146} fill="none" stroke={cB} strokeWidth={4} opacity={0.8} style={{ filter: `drop-shadow(0 0 10px ${cB})` }} />
                <circle cx={150} cy={150} r={146} fill="none" stroke={cA} strokeWidth={5} style={{ filter: `drop-shadow(0 0 14px ${cA})` }} />
              </svg>)}
              {solid && <Img src={staticFile("pd01/logo_circle_pink.png")} style={{ width: 300, height: 300, filter: `drop-shadow(0 0 ${30 * flash + 8}px ${col.pink})` }} />}
            </div>
            <div style={{ position: "relative", opacity: wordIn > 0 ? 1 : 0 }}>
              <Img src={staticFile("pd01/logo_wordmark.png")} style={{ position: "absolute", width: 620, left: -split, filter: "drop-shadow(0 0 0 #FF1A8C) brightness(0.9) sepia(1) hue-rotate(290deg) saturate(8)", opacity: 0.7 * (1 - wordIn), mixBlendMode: "screen" }} />
              <Img src={staticFile("pd01/logo_wordmark.png")} style={{ position: "absolute", width: 620, left: split, filter: "sepia(1) hue-rotate(190deg) saturate(8)", opacity: 0.7 * (1 - wordIn), mixBlendMode: "screen" }} />
              <Img src={staticFile("pd01/logo_wordmark.png")} style={{ width: 620, clipPath: `inset(0 ${100 - wordIn * 100}% 0 0)` }} />
            </div>
            <AbsoluteFill style={{ background: "white", opacity: flash * 0.35, pointerEvents: "none" }} />
          </AbsoluteFill>
        );
      })()}
    </AbsoluteFill>
  );
};
