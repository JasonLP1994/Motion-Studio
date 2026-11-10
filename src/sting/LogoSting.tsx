// Phillips English logo sting (3 s). The real logo, split into pieces, builds on from its bar:
// the bar grows, P and E rise from behind its top edge, the name drops from under its bottom edge,
// and the whole mark settles on the impact. Then it holds dead still.
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import { stingConfig as C } from "./config";

const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
function spring(f: number, w = C.spring.w, z = C.spring.z) {
  if (f <= 0) return 0;
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * f) * (Math.cos(wd * f) + ((z * w) / wd) * Math.sin(wd * f));
}

type PieceName = keyof typeof C.pieces;
const box = C.logoBox;
const scale = C.logoHeightOnScreen / (box.y1 - box.y0);
const W = C.output.width, H = C.output.height;
// logo-file px -> screen px (logo centred in frame)
const sx = (x: number) => W / 2 + (x - (box.x0 + box.x1) / 2) * scale;
const sy = (y: number) => H / 2 + (y - (box.y0 + box.y1) / 2) * scale;

const bar = C.pieces.bar;
const barTop = sy(bar.y + 6); // visible top edge of the bar stroke (6 px of soft edge in the crop)
const barBottom = sy(bar.y + bar.h - 6);

// A piece shown through a window that ends at the bar: "up" pieces rise out of the bar's top edge,
// "down" pieces drop out of its bottom edge.
// edge: the window edge (screen px) the piece emerges from; defaults to the bar's matching edge.
const Piece: React.FC<{ name: PieceName; at: number; dir: "up" | "down"; frame: number; edge?: number }> = ({ name, at, dir, frame, edge }) => {
  const p = C.pieces[name];
  const left = sx(p.x), top = sy(p.y), w = p.w * scale, h = p.h * scale;
  const k = spring(frame - at);
  const e = edge ?? (dir === "up" ? barTop : barBottom);
  const travel = dir === "up" ? e - top : top + h - e; // distance to hide fully behind the edge
  const offset = (1 - k) * travel * (dir === "up" ? 1 : -1);
  const clip = dir === "up"
    ? { left: 0, top: 0, width: W, height: e }
    : { left: 0, top: e, width: W, height: H - e };
  if (frame < at) return null;
  return (
    <div style={{ position: "absolute", ...clip, overflow: "hidden" }}>
      <Img src={staticFile(`logo/${name}.png`)} style={{ position: "absolute", left, top: top - clip.top + offset, width: w, height: h }} />
    </div>
  );
};

const Mark: React.FC = () => {
  const frame = useCurrentFrame();
  const T = C.t;
  const grow = C.barStubWidth + (1 - C.barStubWidth) * spring(frame - T.barGrow, 0.5, 0.9);
  const kick = frame >= T.land ? 1 + C.overshoot * Math.exp(-0.45 * (frame - T.land)) * Math.cos(0.5 * (frame - T.land)) : 1;
  const bw = bar.w * scale;
  return (
    <AbsoluteFill style={{ transform: `scale(${kick})`, transformOrigin: `${W / 2}px ${barTop}px` }}>
      {/* Each piece is revealed from its own edge (ink baseline / ink top), so the mask line never shows */}
      <Piece name="p" at={T.p} dir="up" frame={frame} edge={sy(C.ink.pe.bottom)} />
      <Piece name="e" at={T.e} dir="up" frame={frame} edge={sy(C.ink.pe.bottom)} />
      <Piece name="phillips" at={T.phillips} dir="down" frame={frame} edge={sy(C.ink.phillips.top)} />
      <Piece name="english" at={T.english} dir="down" frame={frame} edge={sy(C.ink.english.top)} />
      {/* the bar: the real bar image, revealed from its centre outward */}
      <div style={{ position: "absolute", left: sx(bar.x) + (bw * (1 - grow)) / 2, top: sy(bar.y), width: bw * clamp(grow, 0, 1.2), height: bar.h * scale, overflow: "hidden" }}>
        <Img src={staticFile("logo/bar.png")} style={{ position: "absolute", left: -(bw * (1 - grow)) / 2, top: 0, width: bw, height: bar.h * scale }} />
      </div>
    </AbsoluteFill>
  );
};

export const LogoSting: React.FC = () => {
  const fps = C.output.fps;
  return (
    <AbsoluteFill style={{ background: C.colors.bgEdge }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 70% at 50% 50%, ${C.colors.bgCentre} 0%, ${C.colors.bgEdge} 100%)` }} />
      <CameraMotionBlur shutterAngle={C.motionBlur.shutterAngle} samples={C.motionBlur.samples}>
        <Mark />
      </CameraMotionBlur>
      {C.sounds.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.frame + 1 - (s.peakMs / 1000) * fps))} durationInFrames={fps}>
          <Audio src={staticFile(s.file)} volume={s.volume * C.masterVolume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
