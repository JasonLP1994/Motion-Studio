import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, Easing } from "remotion";
import { pd01Config as C } from "./config";

const fontFace = `
@font-face { font-family: PDDisplay; src: url(${staticFile("fonts/" + C.fonts.display)}); }
@font-face { font-family: PDUI; src: url(${staticFile("fonts/" + C.fonts.ui)}); }
@font-face { font-family: PDUIMed; src: url(${staticFile("fonts/" + C.fonts.uiMed)}); }
@font-face { font-family: PDJP; src: url(${staticFile("fonts/" + C.fonts.jp)}); }`;
const col = C.colors;
const ease = Easing.bezier(0.16, 1, 0.3, 1);

// each HUD element reveals with a short wipe; i = order index
const useReveal = (i: number) => {
  const f = useCurrentFrame();
  const t0 = (C.hud.start + i * C.hud.stagger) * C.fps;
  return interpolate(f, [t0, t0 + C.hud.drawDur * C.fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
};
const Wipe: React.FC<{ i: number; style?: React.CSSProperties; children: React.ReactNode }> = ({ i, style, children }) => {
  const p = useReveal(i);
  return <div style={{ position: "absolute", clipPath: `inset(0 ${100 - p * 100}% 0 0)`, ...style }}>{children}</div>;
};
const T: React.FC<{ size: number; color?: string; font?: string; ls?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ size, color = col.ink, font = "PDUI", ls = 0.08, children, style }) => (
  <div style={{ fontFamily: font, fontSize: size, color, letterSpacing: `${ls}em`, lineHeight: 1.15, whiteSpace: "pre", ...style }}>{children}</div>
);
const Bracket: React.FC<{ x: number; y: number; w: number; h: number; i: number }> = ({ x, y, w, h, i }) => {
  const p = useReveal(i); const L = 18;
  const s: React.CSSProperties = { position: "absolute", width: L * p, height: L * p, borderColor: col.line, borderStyle: "solid", borderWidth: 0 };
  return (<>
    <div style={{ ...s, left: x, top: y, borderLeftWidth: 2, borderTopWidth: 2 }} />
    <div style={{ ...s, left: x + w - L * p, top: y + h - L * p, borderRightWidth: 2, borderBottomWidth: 2 }} />
  </>);
};
const Barcode: React.FC<{ w: number; h: number; seed: number }> = ({ w, h, seed }) => {
  const bars: React.ReactNode[] = []; let x = 0, k = seed;
  while (x < w) { k = (k * 9301 + 49297) % 233280; const bw = 2 + (k % 4) * 2; if ((k >> 3) % 3 !== 0) bars.push(<div key={x} style={{ position: "absolute", left: x, top: 0, width: bw, height: h, background: col.pink }} />); x += bw + 3; }
  return <div style={{ position: "relative", width: w, height: h }}>{bars}</div>;
};
const Slashes: React.FC<{ n: number; color?: string; size?: number }> = ({ n, color = col.pink, size = 30 }) => (
  <div style={{ display: "flex", gap: size * 0.18 }}>{Array.from({ length: n }).map((_, i) => <div key={i} style={{ width: size * 0.16, height: size, background: color, transform: "skewX(-30deg)" }} />)}</div>
);

export const PD01HUD: React.FC = () => {
  const { copy: c } = C;
  return (
    <AbsoluteFill style={{ background: col.page }}>
      <style>{fontFace}</style>
      {/* figure: big, lower right, cropped by the frame edge like the reference */}
      <Img src={staticFile(C.figure)} style={{ position: "absolute", height: 1500, left: C.figurePos.left, top: C.figurePos.top }} />

      {/* masthead */}
      <Wipe i={0} style={{ left: 70, top: 10 }}><T size={300} font="PDDisplay" ls={0.0} style={{ lineHeight: 1 }}>{c.masthead}</T></Wipe>
      <Wipe i={2} style={{ left: 78, top: 322 }}><T size={34} color={col.pink} ls={0.12}>{c.tag}</T></Wipe>
      <Wipe i={3} style={{ left: 78, top: 384 }}><div style={{ border: `2px solid ${col.ink}`, padding: "6px 14px" }}><T size={24} font="PDJP" ls={0.06}>{c.jpTitle}</T></div></Wipe>
      <Wipe i={4} style={{ left: 78, top: 438 }}><T size={20} font="PDUIMed" ls={0.14}>{c.subTitle}</T></Wipe>

      {/* left column: model / serial / class */}
      <Bracket x={70} y={500} w={220} h={150} i={5} />
      <Wipe i={5} style={{ left: 92, top: 512 }}><T size={22} font="PDUIMed">MODEL</T></Wipe>
      <Wipe i={6} style={{ left: 88, top: 540 }}><T size={96} color={col.pink} ls={0}>{c.model}</T></Wipe>
      <Wipe i={7} style={{ left: 92, top: 660 }}><T size={20} font="PDUIMed">{`SERIAL:\n${c.serial}\n\nCLASS:\n${c.klass}`}</T></Wipe>
      <Wipe i={8} style={{ left: 92, top: 820 }}><div style={{ border: `2px solid ${col.line}`, padding: 16, display: "flex", flexDirection: "column", gap: 12 }}><Slashes n={5} color={col.ink} size={40} /><T size={30} color={col.pink}>PHILLIPS</T></div></Wipe>
      <Wipe i={9} style={{ left: 92, top: 990 }}><T size={16} font="PDUIMed" ls={0.12} style={{ opacity: 0.85 }}>{c.protocol.join("    ")}</T></Wipe>

      {/* right column: tagline, barcode, coords, issue, traits */}
      <Wipe i={1} style={{ right: 70, top: 34 }}><div style={{ display: "flex", alignItems: "center", gap: 16 }}><div style={{ width: 70, height: 2, background: col.ink }} /><T size={24} font="PDJP" ls={0.04}>{c.jpTop}</T><T size={30}>+</T></div></Wipe>
      <Wipe i={4} style={{ right: 70, top: 96 }}><div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
        <div style={{ display: "flex", gap: 40, alignItems: "center" }}><T size={20} color={col.pink}>{c.barcodeLabel}</T><Slashes n={4} size={18} /></div>
        <Barcode w={320} h={110} seed={7} />
        <T size={22} color={col.pink} ls={0.18}>{c.barcodeNum}</T>
      </div></Wipe>
      <Wipe i={6} style={{ right: 70, top: 330 }}><div style={{ display: "flex", gap: 22, alignItems: "center" }}>
        <div style={{ width: 40, height: 40, border: `2px solid ${col.ink}`, borderRadius: 20, position: "relative" }}><div style={{ position: "absolute", left: 18, top: -8, width: 2, height: 54, background: col.ink }} /><div style={{ position: "absolute", top: 18, left: -8, height: 2, width: 54, background: col.ink }} /></div>
        <T size={18} font="PDUIMed">{c.coords.join("\n")}</T></div></Wipe>
      <Bracket x={1640} y={430} w={210} h={300} i={7} />
      <Wipe i={7} style={{ left: 1662, top: 446 }}><T size={22} font="PDUIMed">ISSUE</T></Wipe>
      <Wipe i={8} style={{ left: 1658, top: 472 }}><T size={86} color={col.pink} ls={0}>{c.issue}</T></Wipe>
      <Wipe i={9} style={{ left: 1662, top: 580 }}><T size={18} font="PDUIMed">{c.issueSub.join("\n")}</T></Wipe>
      <Wipe i={10} style={{ left: 1662, top: 650 }}><div style={{ display: "flex", flexDirection: "column", gap: 10 }}><Slashes n={4} color={col.ink} size={16} /><T size={18} font="PDUIMed">{c.edition.join("\n")}</T></div></Wipe>
      <Wipe i={11} style={{ left: 1662, top: 790 }}><div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {c.traits.map((t, k) => <div key={t} style={{ display: "flex", gap: 14, alignItems: "center" }}><div style={{ width: 20, height: 20, border: `2px solid ${k === 0 ? col.pink : col.ink}`, transform: "rotate(45deg)" }} /><T size={20} font="PDUIMed">{t}</T></div>)}
      </div></Wipe>
      <Wipe i={12} style={{ right: 70, bottom: 54 }}><div style={{ textAlign: "right" }}><T size={26} font="PDJP" color={col.pink} ls={0.04}>{c.jpBottom}</T><T size={16} font="PDUIMed" style={{ marginTop: 6 }}>{`VER. ${c.ver}`}</T></div></Wipe>
    </AbsoluteFill>
  );
};
