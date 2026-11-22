import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { PX, pixelConfig as C } from "./config";

loadFont({ family: "Silkscreen", url: staticFile("fonts/Silkscreen-Bold.ttf"), weight: "700" });
loadFont({ family: "SilkscreenR", url: staticFile("fonts/Silkscreen-Regular.ttf"), weight: "400" });
loadFont({ family: "Pixelify", url: staticFile("fonts/PixelifySans.ttf"), weight: "700" });

const snap = (v: number) => Math.round(v / PX) * PX; // whole-pixel positions only

// typewriter: how many characters of an element are visible at frame f (types on, holds, backspaces off)
type El = { lines: string[]; start: number; fpc: number; erase: number; efpc: number };
const total = (e: El) => e.lines.join("").length;
const shown = (e: El, f: number) => {
  const n = total(e); if (f < e.start) return 0;
  const typed = Math.min(n, Math.floor((f - e.start) / e.fpc) + 1);
  if (f < e.erase) return typed;
  return Math.max(0, typed - Math.floor((f - e.erase) / e.efpc) - 1);
};
const typingNow = (e: El, f: number) => { const n = total(e), k = shown(e, f); return k > 0 && (k < n || (f >= e.start && f < e.start + n * e.fpc + 18) || f >= e.erase); };
// render an element's lines with untyped letters hidden (layout never shifts) and a blinking pixel block cursor
const Typed: React.FC<{ e: El; f: number; color: string; style?: React.CSSProperties; lineStyle?: React.CSSProperties }> = ({ e, f, color, style, lineStyle }) => {
  const k = shown(e, f); let used = 0; const cur = typingNow(e, f) && Math.floor(f / 6) % 2 === 0;
  return (<div style={style}>{e.lines.map((ln, li) => {
    const startIdx = used; used += ln.length;
    return (<div key={li} style={{ position: "relative", whiteSpace: "pre", ...lineStyle }}>{ln.split("").map((ch, ci) => {
      const idx = startIdx + ci, vis = idx < k, isCur = cur && idx === k - 1;
      return <span key={ci} style={{ color: vis ? color : "transparent", position: "relative" }}>{ch}{isCur && <span style={{ position: "absolute", left: "100%", top: "8%", width: "0.6em", height: "0.85em", background: color }} />}</span>;
    })}</div>);
  })}</div>);
};

// seeded barcode bars on the pixel grid
const bars = (() => { let s = 11; const r = () => ((s = (s * 9301 + 49297) % 233280) / 233280); const o: number[] = []; for (let i = 0; i < 26; i++) o.push(r() > 0.45 ? 1 : 0); return o; })();

export const PixelSneaker: React.FC<{ palette?: string }> = ({ palette = C.palette }) => {
  const f = useCurrentFrame();
  const P = C.palettes[palette];
  const T = (P as { text?: string }).text ?? P.ink; // text colour (light on dark pages)
  const s = C.sprite;
  const angle = Math.floor(f / s.stepFrames) % s.angles;
  const bob = snap(Math.round(Math.sin((2 * Math.PI * f) / C.bobPeriod) * 2) * PX); // float on whole pixels, loops cleanly
  const TY = C.typing.elements as Record<string, El>;
  const pix: React.CSSProperties = { imageRendering: "pixelated", WebkitFontSmoothing: "none", fontSmooth: "never" } as React.CSSProperties;
  return (
    <AbsoluteFill style={{ background: P.page, ...pix }}>
      {/* giant pixel masthead */}
      <Typed e={TY.mast} f={f} color={P.masthead} style={{ position: "absolute", top: C.masthead.y, left: 0, width: 1920, textAlign: "center", fontFamily: "Silkscreen", fontWeight: 700, fontSize: C.masthead.size, lineHeight: 0.9, letterSpacing: C.masthead.spacing }} />
      {/* pixel shadow */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }} shapeRendering="crispEdges">
        {Array.from({ length: 9 }).map((_, i) => { const w = (120 - Math.abs(i - 4) * 18) * PX / 2; return <rect key={i} x={snap(s.x + s.w * s.scale / 2 - w / 2)} y={snap(s.y + s.h * s.scale - 30) + i * 0} width={snap(w)} height={PX} fill={P.ink} opacity={0} />; })}
        {(() => { const x0 = s.x + s.contentX[0] * s.scale, x1 = s.x + s.contentX[1] * s.scale, yb = s.y + s.contentBottom * s.scale + 2 * PX; return (<>
          <rect x={snap(x0 + 40)} y={snap(yb)} width={snap(x1 - x0 - 80)} height={PX * 3} fill={P.ink} opacity={0.9} />
          <rect x={snap(x0 + 100)} y={snap(yb) - PX} width={snap(x1 - x0 - 200)} height={PX} fill={P.ink} opacity={0.9} />
          <rect x={snap(x0 + 100)} y={snap(yb) + 3 * PX} width={snap(x1 - x0 - 200)} height={PX} fill={P.ink} opacity={0.9} /></>); })()}
      </svg>
      {/* the sneaker sprite, nearest-neighbour upscale */}
      <Img src={staticFile(`pixel/${palette}/s_${String(angle).padStart(3, "0")}.png`)} style={{ position: "absolute", left: snap(s.x), top: snap(s.y) + bob, width: s.w * s.scale, height: s.h * s.scale, imageRendering: "pixelated" }} />
      {/* left editorial column */}
      <Typed e={TY.side} f={f} color={T} style={{ position: "absolute", left: C.side.x, top: C.side.y, fontFamily: "Silkscreen", fontSize: 48, lineHeight: 0.95 }} />
      <svg width={300} height={90} style={{ position: "absolute", left: C.side.x, top: C.side.y + 190 }} shapeRendering="crispEdges">
        {bars.map((b, i) => b && i < Math.round(bars.length * shown(TY.side, f) / total(TY.side)) ? <rect key={i} x={i * PX * 1.5} y={0} width={PX} height={60} fill={T} /> : null)}
      </svg>
      <Typed e={TY.blurb} f={f} color={T} style={{ position: "absolute", left: C.side.x, top: C.side.y + 290, fontFamily: "SilkscreenR", fontSize: 24, lineHeight: 1.25 }} />
      {/* top-right small print */}
      <Typed e={TY.corner} f={f} color={T} style={{ position: "absolute", right: 72, top: 410, textAlign: "right", fontFamily: "Silkscreen", fontSize: 26, lineHeight: 1.15 }} lineStyle={{ marginBottom: 14 }} />
      {/* right vertical tab */}
      <div style={{ position: "absolute", left: C.tab.x, top: C.tab.y, width: 60, border: `${PX}px solid ${T}`, display: "flex", flexDirection: "column", alignItems: "center" }}>
        {C.tab.letters.split("").map((ch, i) => <div key={ch} style={{ fontFamily: "Silkscreen", fontSize: 36, color: i < shown(TY.tab, f) ? T : "transparent", lineHeight: 1.2 }}>{ch}</div>)}
        <div style={{ background: T, color: P.page, width: "100%", textAlign: "center", fontFamily: "SilkscreenR", fontSize: 14, padding: "8px 0" }}>{C.tab.sub.split("").map((ch, i) => <div key={i}>{ch}</div>)}</div>
      </div>
      {/* bottom pixel line */}
      <Typed e={TY.bottom} f={f} color={T} style={{ position: "absolute", top: C.bottom.y, left: 0, width: 1920, textAlign: "center", fontFamily: "Silkscreen", fontWeight: 700, fontSize: C.bottom.size }} />
      {/* playful pixel stars */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }} shapeRendering="crispEdges">
        {[[300, 330, 0], [1650, 600, 7], [1500, 880, 13]].map(([x, y, ph], k) => { const sc = 1 + (Math.floor((f + ph) / 6) % 2); return (
          <g key={k} transform={`translate(${snap(x)} ${snap(y)})`} fill={k === 1 ? P.masthead : P.accent}>
            <rect x={-PX * sc / 2} y={-PX * 3 * sc} width={PX * sc} height={PX * 6 * sc} /><rect x={-PX * 3 * sc} y={-PX * sc / 2} width={PX * 6 * sc} height={PX * sc} />
          </g>); })}
      </svg>
    </AbsoluteFill>
  );
};
