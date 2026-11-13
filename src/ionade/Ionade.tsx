import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { ionadeConfig as c } from "./config";

const pad = (n: number, d: number) => String(n).padStart(d, "0");
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// logo x (centre) per frame: flies in from the left on a long ease-out with a small overshoot, then holds dead still
const logoX = (f: number) =>
  interpolate(f, [c.swipe.start, c.swipe.land], [-c.logoBox.width, c.logoBox.cx], { ...clamp, easing: Easing.out(Easing.back(1.3)) });
const bandX = (f: number) =>
  interpolate(f, [c.swipe.start - 2, c.swipe.bandOut], [-1500, c.output.width + 1500], { ...clamp, easing: Easing.inOut(Easing.cubic) });

export const IonadeSting: React.FC = () => {
  const f = useCurrentFrame();
  const { width: W, height: H } = c.output;
  const src = staticFile(`${c.frames.dir}/${c.frames.prefix}${pad(f + c.frames.first, c.frames.digits)}.png`);

  const lx = logoX(f), lv = Math.abs(lx - logoX(f - 1));            // px per frame -> horizontal motion blur
  const bx = bandX(f), bv = Math.abs(bx - bandX(f - 1));
  const lw = c.logoBox.width, lh = lw / c.logo.aspect;
  const logoOn = f >= c.swipe.start;
  const sweep = interpolate(f, [c.flash.at, c.flash.at + c.flash.length], [-0.4, 1.4], clamp);
  const pop = interpolate(f, [c.flash.at, c.flash.at + 2, c.flash.at + 8], [1, 1.35, 1], clamp);
  const scrim = interpolate(f, [c.scrim.from, c.scrim.to], [0, c.scrim.opacity], clamp);

  return (
    <AbsoluteFill style={{ backgroundColor: c.colours.orange }}>
      <Img src={src} style={{ width: W, height: H, objectFit: "cover" }} />
      {/* directional blur filters (x only), sized by speed */}
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="blurLogo" x="-50%" y="-10%" width="200%" height="120%"><feGaussianBlur stdDeviation={`${Math.min(40, lv * 0.35)} 0`} /></filter>
        <filter id="blurBand" x="-20%" y="-10%" width="140%" height="120%"><feGaussianBlur stdDeviation={`${Math.min(60, bv * 0.3)} 0`} /></filter>
      </svg>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${c.colours.navy} 0%, rgba(11,46,122,0) 62%)`, opacity: scrim }} />
      {/* the band: navy with orange and cream edges, slanted like the logo banner */}
      {f >= c.swipe.start - 2 && f <= c.swipe.bandOut && (
        <div style={{
          position: "absolute", left: bx - 1300, top: c.logoBox.cy - c.swipe.bandHeight / 2, width: 2600, height: c.swipe.bandHeight,
          transform: `rotate(${c.swipe.angleDeg}deg) skewX(-18deg)`, filter: "url(#blurBand)",
          background: `linear-gradient(180deg, ${c.colours.cream} 0 10px, ${c.colours.orange} 10px 34px, ${c.colours.navy} 34px calc(100% - 34px), ${c.colours.orange} calc(100% - 34px) calc(100% - 10px), ${c.colours.cream} calc(100% - 10px))`,
        }} />
      )}
      {logoOn && (
        <div style={{ position: "absolute", left: lx - lw / 2, top: c.logoBox.cy - lh / 2, width: lw, height: lh, filter: `url(#blurLogo) brightness(${pop}) drop-shadow(0 18px 30px rgba(11,46,122,0.45))` }}>
          <Img src={staticFile(c.logo.file)} style={{ width: lw, height: lh }} />
          {/* light sweep across the logo, masked to its shape */}
          <div style={{
            position: "absolute", inset: 0, opacity: sweep > -0.4 && sweep < 1.4 ? 1 : 0,
            background: `linear-gradient(105deg, rgba(255,255,255,0) ${(sweep - 0.12) * 100}%, rgba(255,255,255,0.85) ${sweep * 100}%, rgba(255,255,255,0) ${(sweep + 0.12) * 100}%)`,
            WebkitMaskImage: `url(${staticFile(c.logo.file)})`, WebkitMaskSize: "100% 100%", maskImage: `url(${staticFile(c.logo.file)})`, maskSize: "100% 100%",
            mixBlendMode: "screen",
          }} />
        </div>
      )}
    </AbsoluteFill>
  );
};
