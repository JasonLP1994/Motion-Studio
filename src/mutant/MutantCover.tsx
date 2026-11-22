import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { fitText } from "@remotion/layout-utils";
import { P, mutantConfig as C } from "./config";

loadFont({ family: "BarlowCondBlack", url: staticFile("fonts/BarlowCondensed-BlackItalic.ttf"), weight: "900", style: "italic" });
loadFont({ family: "MontBlack", url: staticFile("fonts/montserrat-latin-900-italic.woff2"), weight: "900", style: "italic" });
loadFont({ family: "MontBlackUp", url: staticFile("fonts/montserrat-latin-900-normal.woff2"), weight: "900" });

const out = Easing.out(Easing.cubic);
const expo = Easing.out(Easing.exp);
const prog = (f: number, at: number, dur: number, e = out) =>
  interpolate(f, [at, at + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: e });
const ital: React.CSSProperties = { fontFamily: "MontBlack", fontStyle: "italic", fontWeight: 900, color: P.ink, lineHeight: 0.92 };

const Star: React.FC<{ x: number; y: number; r: number; rot?: number; s?: number }> = ({ x, y, r, rot = 0, s = 1 }) => (
  <path
    transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}
    d={`M0 ${-r} C${r * 0.12} ${-r * 0.12} ${r * 0.12} ${-r * 0.12} ${r} 0 C${r * 0.12} ${r * 0.12} ${r * 0.12} ${r * 0.12} 0 ${r} C${-r * 0.12} ${r * 0.12} ${-r * 0.12} ${r * 0.12} ${-r} 0 C${-r * 0.12} ${-r * 0.12} ${-r * 0.12} ${-r * 0.12} 0 ${-r}Z`}
    fill={P.ink}
  />
);

// seeded bar widths so the barcode is identical every render
const bars = (() => {
  let s = 7; const r = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  const out: { x: number; w: number }[] = []; let x = 0;
  while (x < C.barcode.w) { const w = 2 + Math.floor(r() * 4); out.push({ x, w }); x += w + 2 + Math.floor(r() * 4); }
  return out.filter((b) => b.x + b.w <= C.barcode.w);
})();

export const MutantCover: React.FC = () => {
  const f = useCurrentFrame();
  const W = C.output.width;

  // ---- masthead: letters slice up out of a mask, staggered
  const m = C.masthead;
  const { fontSize: mSize } = fitText({ text: m.text, withinWidth: m.width, fontFamily: "BarlowCondBlack", fontWeight: "900" });
  const mastSize = Math.min(mSize, m.maxSize);
  const bladeTop = m.y + mastSize * 0.8; // the blade drops from the masthead's baseline

  // ---- top bar
  const tb = prog(f, C.topBar.at, 10, expo);

  // ---- coordinates roll up to their value
  const cp = prog(f, C.coords.at, C.coords.dur, Easing.out(Easing.cubic));
  const lat = (C.coords.lat * cp).toFixed(4), lon = (C.coords.lon * cp).toFixed(4);

  // ---- specimen number scramble then land
  const sp = C.specimen; const spOn = f >= sp.at;
  const scr = f < sp.at + 14 ? `Nº ${String(Math.floor(((f * 7919) % 997))).padStart(3, "0")}` : sp.number;

  // ---- title slam + orbit + sparkle
  const t = C.title; const tp = prog(f, t.at, 6, expo);
  const op = prog(f, C.orbit.at, C.orbit.dur, Easing.inOut(Easing.cubic));
  const spk = prog(f, C.sparkle.at, 8, Easing.out(Easing.back(2)));

  const blade = prog(f, C.blade.at, C.blade.dur, expo);
  const g = prog(f, C.globe.at, C.globe.dur, Easing.inOut(Easing.cubic));
  const hud = prog(f, C.hud.at, 8, Easing.out(Easing.back(1.6)));
  const frameNo = Math.min(C.output.durationInFrames, f + C.frames.first);

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 55% 45%, ${P.lime} 55%, ${P.limeDeep} 100%)` }}>
      {/* masthead + blade sit behind the head */}
      <div style={{ position: "absolute", top: m.y, left: 0, width: W, display: "flex", justifyContent: "center" }}>
        {m.text.split("").map((ch, i) => {
          const p = prog(f, m.at + i * m.stagger, 9, expo);
          return (
            <span key={i} style={{ display: "inline-block", overflow: "hidden", paddingRight: ch === " " ? 0 : 6, marginRight: -6 }}>
              <span style={{ display: "inline-block", fontFamily: "BarlowCondBlack", fontStyle: "italic", fontWeight: 900, fontSize: mastSize, lineHeight: 0.86, color: P.ink, letterSpacing: "-0.01em", transform: `translateY(${(1 - p) * 105}%) skewX(${(1 - p) * -12}deg)`, whiteSpace: "pre" }}>
                {ch}
              </span>
            </span>
          );
        })}
      </div>
      <svg width={W} height={1080} style={{ position: "absolute", inset: 0 }}>
        <clipPath id="bladeClip"><rect x={0} y={0} width={W} height={bladeTop + blade * (1080 - bladeTop)} /></clipPath>
        <polygon clipPath="url(#bladeClip)" points={`1640,${bladeTop - 10} 1722,${bladeTop - 10} 1262,1080 1228,1080`} fill={P.ink} />
      </svg>

      {/* the chrome head with its growths (Blender, transparent) */}
      <Img src={staticFile(`${C.frames.dir}${String(frameNo).padStart(C.frames.pad, "0")}.png`)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />

      {/* top bar */}
      <div style={{ position: "absolute", top: 18, left: 72, right: 72, height: 30, display: "flex", alignItems: "center", gap: 22, opacity: tb }}>
        <span style={{ ...ital, fontSize: 22 }}>{C.topBar.left}</span>
        <div style={{ flex: 1, height: 5, background: P.ink, transform: `scaleX(${tb})`, transformOrigin: "right" }} />
        <span style={{ ...ital, fontSize: 22 }}>{C.topBar.centre}</span>
        <div style={{ flex: 1, height: 5, background: P.ink, transform: `scaleX(${tb})`, transformOrigin: "left" }} />
        <span style={{ ...ital, fontSize: 22 }}>{C.topBar.right}</span>
      </div>

      {/* left column */}
      <div style={{ position: "absolute", left: C.coverLines.x, top: C.coverLines.y }}>
        {C.coverLines.lines.map((l, i) => {
          const p = prog(f, C.coverLines.at + i * C.coverLines.stagger, 8, expo);
          return <div key={l} style={{ ...ital, fontSize: C.coverLines.size, opacity: p, transform: `translateX(${(1 - p) * -60}px)` }}>{l}</div>;
        })}
      </div>
      <svg width={W} height={1080} style={{ position: "absolute", inset: 0 }} fill="none" stroke={P.ink} strokeWidth={2.6}>
        {(() => {
          const { x, y, w, h } = C.globe; const cx = x + w / 2, cy = y + h / 2; const turn = f * 0.035;
          const dash = (_len: number) => ({ strokeDasharray: 1, strokeDashoffset: 1 - g });
          return (
            <g opacity={g > 0 ? 1 : 0}>
              <ellipse pathLength={1} cx={cx} cy={cy} rx={w / 2} ry={h / 2} style={dash(500)} />
              {[0, 1, 2].map((k) => <ellipse key={k} pathLength={1} cx={cx} cy={cy} rx={Math.abs(Math.cos(turn + (k * Math.PI) / 3)) * w / 2} ry={h / 2} style={dash(300)} />)}
              {[-0.5, 0, 0.5].map((k) => { const yy = cy + (k * h) / 1.4; const half = (w / 2) * Math.sqrt(1 - (k / 0.7) ** 2 * 0.5); return <line key={k} pathLength={1} x1={cx - half} y1={yy} x2={cx + half} y2={yy} style={dash(200)} />; })}
            </g>
          );
        })()}
      </svg>
      {spOn && (
        <div style={{ position: "absolute", left: sp.x, top: sp.y, opacity: prog(f, sp.at, 4) }}>
          <div style={{ ...ital, fontSize: 30 }}>{sp.label}</div>
          <div style={{ ...ital, fontSize: 74, letterSpacing: "-0.02em" }}>{scr}</div>
        </div>
      )}
      {f >= C.coords.at && (
        <div style={{ position: "absolute", left: C.coords.x, top: C.coords.y, fontFamily: "MontBlackUp", fontWeight: 900, fontSize: 27, color: P.ink, lineHeight: 1.15 }}>
          <div>{lat}° N</div><div>{lon}° W</div>
        </div>
      )}
      <svg width={W} height={1080} style={{ position: "absolute", inset: 0 }}>
        <clipPath id="bc"><rect x={C.barcode.x} y={C.barcode.y} width={C.barcode.w * prog(f, C.barcode.at, 8, expo)} height={C.barcode.h} /></clipPath>
        <g clipPath="url(#bc)">{bars.map((b, i) => <rect key={i} x={C.barcode.x + b.x} y={C.barcode.y} width={b.w} height={C.barcode.h} fill={P.ink} />)}</g>
        {[0, 1, 2].map((k) => { const p = prog(f, C.stars.at + k * 4, 7, Easing.out(Easing.back(2.2))); const tw = 1 + 0.12 * Math.sin((f + k * 9) * 0.25); return p > 0 ? <Star key={k} x={C.stars.x + 22 + k * 52} y={C.stars.y} r={24} s={p * tw} rot={(1 - p) * 90} /> : null; })}

        {/* right HUD: crosshair, corner brackets, rule */}
        <g stroke={P.ink} strokeWidth={4} fill="none" opacity={Math.min(1, hud * 1.5)} transform={`translate(${C.hud.x} ${C.hud.y}) scale(${0.6 + 0.4 * hud})`}>
          <path d="M42 0 V40 M22 20 H62" />
          <path d="M0 78 V58 H20 M64 58 H84 V78 M0 132 V152 H20 M64 152 H84 V132" />
        </g>
        <line x1={C.hud.x + 84} y1={570} x2={C.hud.x + 84} y2={570 + 190 * prog(f, C.hud.at + 6, 16, expo)} stroke={P.ink} strokeWidth={4} />

        {/* orbit ellipse + sparkle around the title */}
        <g transform={`rotate(-11 ${t.x + 330} ${t.y + 70})`}>
          <ellipse cx={t.x + 330} cy={t.y + 70} rx={440} ry={150} fill="none" stroke={P.ink} strokeWidth={3.5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - op} />
        </g>
        {spk > 0 && <Star x={t.x + 520} y={t.y - 108} r={46} s={spk * (1 + 0.08 * Math.sin(f * 0.3))} rot={(1 - spk) * 120} />}
      </svg>

      {/* counters */}
      <div style={{ position: "absolute", right: W - C.counters.x, top: C.counters.y, textAlign: "right" }}>
        {C.counters.items.map((it, i) => {
          const p = prog(f, C.counters.at + i * 3, 6, expo);
          const active = f > C.counters.at + 20 && Math.floor((f - C.counters.at) / C.counters.every) % C.counters.items.length === i;
          return (
            <div key={it} style={{ fontFamily: "MontBlackUp", fontWeight: 900, fontSize: 30, lineHeight: 1.18, opacity: p, color: active ? P.lime : P.ink, background: active ? P.ink : "transparent", padding: "0 6px", display: "block" }}>{it}</div>
          );
        })}
      </div>

      {/* title slam, in front of the head */}
      <div style={{ position: "absolute", left: t.x, top: t.y, opacity: tp, transform: `scale(${1.22 - 0.22 * tp}) skewX(-8deg)`, transformOrigin: "40% 50%" }}>
        {t.lines.map((l, i) => <div key={l} style={{ ...ital, fontSize: t.size, marginLeft: i * 70, letterSpacing: "-0.02em" }}>{l}</div>)}
      </div>

      {/* footer */}
      <div style={{ position: "absolute", right: W - C.footer.x, top: C.footer.y - 30, display: "flex", alignItems: "center", gap: 18, opacity: prog(f, C.footer.at, 8) }}>
        <div style={{ width: 110 * prog(f, C.footer.at, 12, expo), height: 4, background: P.ink }} />
        <div style={{ ...ital, fontSize: 28, textAlign: "right", lineHeight: 1 }}>{C.footer.lines.map((l) => <div key={l}>{l}</div>)}</div>
      </div>
    </AbsoluteFill>
  );
};
