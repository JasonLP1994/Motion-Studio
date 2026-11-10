// "Shape that never cuts": one ball carries the whole film. It bounces, splats into a pill, floods the
// screen, pops out a new ball, splits into three, and the three become the O's of the title.
// Every frame is a pure function of the frame number.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Sequence, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { measureText } from "@remotion/layout-utils";
import { playfulConfig as C } from "./config";

const col = C.colors;
const W = C.output.width, H = C.output.height;

// ---- helpers ----
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (f: number, a: number, b: number) => clamp((f - a) / (b - a));
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const easeIn = (x: number) => Math.pow(clamp(x), 3);
const easeOutQ = (x: number) => 1 - Math.pow(1 - clamp(x), 2);
const easeInQ = (x: number) => Math.pow(clamp(x), 2);
const easeInOut = (x: number) => ((x = clamp(x)), x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
// spring step response in frames: w = rad/frame, z = damping ratio (0.45-0.6 playful)
function spring(f: number, w = 0.5, z = 0.5) {
  if (f <= 0) return 0;
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * f) * (Math.cos(wd * f) + ((z * w) / wd) * Math.sin(wd * f));
}
// a squash wobble after an impact: positive = squashed
const wobble = (f: number, amp: number) => (f < 0 ? 0 : amp * Math.exp(-0.32 * f) * Math.cos(0.85 * f));

// ---- eyes (character acting is allowed: blink and a wink) ----
const Eyes: React.FC<{ cx: number; cy: number; r: number; f: number; look?: number; blinkAt?: number[] }> = ({ cx, cy, r, f, look = 0, blinkAt = [] }) => {
  let open = 1;
  for (const b of blinkAt) { const t = f - b; if (t >= 0 && t < 6) open = Math.min(open, Math.abs(t - 3) / 3); }
  const er = r * 0.24, gap = r * 0.36;
  return (
    <g>
      {[-1, 1].map((s) => (
        <g key={s} transform={`translate(${cx + s * gap} ${cy - r * 0.12}) scale(1 ${Math.max(0.08, open)})`}>
          <circle r={er} fill={col.eyeWhite} />
          <circle cx={look * er * 0.35} cy={er * 0.15} r={er * 0.5} fill={col.pupil} />
        </g>
      ))}
    </g>
  );
};

const useFont = () => {
  const [ready, setReady] = useState(false);
  const [h] = useState(() => delayRender("font"));
  useEffect(() => {
    loadFont({ family: C.font.family, url: staticFile(C.font.file), weight: C.font.weight }).then(() => { setReady(true); continueRender(h); });
  }, [h]);
  return ready;
};

// Title layout from real measurements, so the balls land exactly where the O's sit.
const layoutTitle = () => {
  const m = (text: string, size: number) => measureText({ text, fontFamily: C.font.family, fontWeight: C.font.weight, fontSize: size }).width;
  const widest = Math.max(...C.words.map((w) => m(w, 100)));
  const size = Math.min(230, Math.floor((C.maxTextWidth / widest) * 100));
  const blockH = size * C.lineGap + size * C.oGlyph.height;
  const top0 = H / 2 - blockH / 2 - size * (C.oGlyph.centreFromTop - C.oGlyph.height / 2);
  const letters: { ch: string; x: number; y: number; w: number; line: number; isO: boolean; cx: number; cy: number }[] = [];
  C.words.forEach((word, line) => {
    const total = m(word, size);
    const x0 = W / 2 - total / 2;
    const y = top0 + line * size * C.lineGap;
    for (let i = 0; i < word.length; i++) {
      const before = m(word.slice(0, i), size);
      const w = m(word[i], size);
      letters.push({ ch: word[i], x: x0 + before, y, w, line, isO: word[i] === "O", cx: x0 + before + w / 2, cy: y + size * C.oGlyph.centreFromTop });
    }
  });
  return { size, letters, os: letters.filter((l) => l.isO) };
};

const Scene: React.FC<{ ready: boolean }> = ({ ready }) => {
  const f = useCurrentFrame();
  const R = C.ball.radius, floor = C.ball.floorY;
  const L = C.launch, P = C.pill, K = C.cream, B = C.bounces;

  // ---- phase 1-2: the tomato ball ----
  let by = floor, sq = 0, stretch = 0;
  const [h1, h2, h3] = B.hits;
  if (f < h1) { by = lerp(C.ball.startY, floor, easeInQ(f / h1)); stretch = 0.22 * (f / h1); }
  else if (f < h2) { const s = (f - h1) / (h2 - h1); by = floor - 4 * B.heights[0] * s * (1 - s); stretch = 0.18 * Math.abs(1 - 2 * s); }
  else if (f < h3) { const s = (f - h2) / (h3 - h2); by = floor - 4 * B.heights[1] * s * (1 - s); stretch = 0.08 * Math.abs(1 - 2 * s); }
  sq += wobble(f - h1, B.squash[0]) + wobble(f - h2, B.squash[1]) + wobble(f - h3, B.squash[2]);
  // crouch, launch, land
  if (f >= L.crouch && f < L.go) sq += 0.85 * easeOutQ(seg(f, L.crouch, L.go));
  if (f >= L.go && f < L.apex) { by = lerp(floor, L.apexY, easeOutQ(seg(f, L.go, L.apex))); stretch = 0.3 * (1 - seg(f, L.go, L.apex)); }
  else if (f >= L.apex && f < L.land) { by = lerp(L.apexY, floor, easeInQ(seg(f, L.apex, L.land))); stretch = 0.3 * seg(f, L.apex, L.land); }
  const airborne = f < h3 && f !== h1 && f !== h2;
  const sx = 1 + 0.32 * sq - (airborne || (f >= L.go && f < L.land) ? stretch * 0.5 : 0);
  const sy = 1 - 0.36 * sq + (airborne || (f >= L.go && f < L.land) ? stretch : 0);

  // ---- phase 3: splat into a pill, which floods the screen ----
  const splat = f >= L.land;
  const pw0 = lerp(2 * R, P.width, spring(f - L.land, 0.55, 0.45));
  const ph0 = lerp(2 * R, P.height, spring(f - L.land, 0.55, 0.45));
  const pw = lerp(pw0, W * 1.4, easeIn(seg(f, P.stretchAt, P.stretchAt + 8)));
  const ph = lerp(ph0, H * 1.3, easeInOut(seg(f, P.floodAt, P.floodDone)));
  const pcy = lerp(floor + R - ph0 / 2, H / 2, easeInOut(seg(f, P.floodAt, P.floodDone)));
  const flooded = f >= P.floodDone;

  // ---- phase 4: the cream ball pops out and splits ----
  const creamOn = f >= K.popAt;
  const creamScale = spring(f - K.popAt, 0.6, 0.42);
  const crouch = f >= K.crouch && f < K.split ? 0.7 * easeOutQ(seg(f, K.crouch, K.split)) : 0;
  const split = f >= K.split;

  // three balls: left, middle (with eyes), right
  const T = C.toO;
  const lay = ready ? layoutTitle() : null;
  const ballState = (i: number) => {
    // i: 0 left, 1 middle, 2 right; lands at K.lands[order]
    const dir = [-1, 0, 1][i];
    const land = [K.lands[2], K.lands[1], K.lands[0]][i];
    const r0 = i === 1 ? K.radius : K.smallRadius;
    const groundY = H / 2 + 120;
    let x = W / 2, y = H / 2, r = i === 1 ? K.radius * creamScale : 0, wob = 0;
    if (split) {
      const s = seg(f, K.split, land);
      x = W / 2 + dir * K.spread * easeOutQ(s);
      const apex = i === 1 ? 140 : 190;
      const startY = H / 2, endY = groundY - r0;
      y = lerp(startY, endY, s) - 4 * apex * s * (1 - s);
      r = lerp(i === 1 ? K.radius : K.smallRadius * 0.6, r0, Math.min(1, s * 3));
      wob = wobble(f - land, 0.7);
    } else if (i === 1) {
      wob = crouch;
    }
    // fly to the O
    let ring = 0, rx = r, ry = r, colorKey: string = i === 1 ? "cream" : i === 0 ? "sun" : "mint";
    if (lay) {
      const target = lay.os[[0, 2, 1][i]]; // left -> first O, middle -> STUDI(O), right -> second O
      const st = T.start + [0, 6, 3][i] * 1;
      const s = easeInOut(seg(f, st, st + T.duration));
      if (f >= st) {
        const sx0 = x, sy0 = y;
        x = lerp(sx0, target.cx, s);
        y = lerp(sy0, target.cy, s) - 4 * 90 * s * (1 - s);
        const S = lay.size;
        const ox = (C.oGlyph.width / 2) * S, oy = (C.oGlyph.height / 2) * S;
        rx = lerp(r, ox, s); ry = lerp(r, oy, s);
        ring = seg(f, st + T.duration - 8, st + T.duration);
        wob = wobble(f - (st + T.duration), 0.35);
      }
      colorKey = C.ringColors[[0, 2, 1][i]];
    }
    return { x, y, rx: rx * (1 + 0.3 * wob), ry: ry * (1 - 0.32 * wob), ring, colorKey, wob };
  };

  return (
    <AbsoluteFill style={{ background: flooded ? col.tomato : col.sun }}>
      {/* the final ground floods in from the last O */}
      {lay && f >= C.inkFlood.start ? (
        <AbsoluteFill style={{ background: col.ink, clipPath: `circle(${easeInOut(seg(f, C.inkFlood.start, C.inkFlood.start + C.inkFlood.duration)) * 1600}px at ${lay.os[2].cx}px ${lay.os[2].cy}px)` }} />
      ) : null}
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {/* contact shadow for the bouncing ball */}
        {!splat ? (
          <ellipse cx={W / 2} cy={floor + R + 6} rx={R * (1.1 - 0.5 * clamp((floor - by) / 500))} ry={12} fill="rgba(0,0,0,0.14)" />
        ) : null}
        {!splat ? (
          <g transform={`translate(${W / 2} ${by + R}) scale(${sx} ${sy}) translate(0 ${-R})`}>
            <circle r={R} fill={col.tomato} />
            <Eyes cx={0} cy={0} r={R} f={f} blinkAt={[44]} look={f > 54 ? 0 : 0.6} />
          </g>
        ) : !flooded ? (
          <g>
            <rect x={W / 2 - pw / 2} y={pcy - ph / 2} width={pw} height={ph} rx={Math.min(ph / 2, pw / 2, f >= P.floodAt ? 40 : 999)} fill={col.tomato} />
            {f < P.stretchAt ? <Eyes cx={W / 2} cy={pcy} r={R * 0.7} f={f} blinkAt={[L.land - 3]} /> : null}
          </g>
        ) : null}

        {/* cream ball, then three balls flying to the O's and becoming rings */}
        {creamOn && !split ? (
          <g transform={`translate(${W / 2} ${H / 2}) scale(${1 + 0.3 * crouch} ${1 - 0.3 * crouch})`}>
            <circle r={K.radius * creamScale} fill={col.cream} />
            {creamScale > 0.6 ? <Eyes cx={0} cy={0} r={K.radius} f={f} blinkAt={[106]} /> : null}
          </g>
        ) : null}
        {split
          ? [0, 1, 2].map((i) => {
              const b = ballState(i);
              const S = lay ? lay.size : 200;
              const strokeW = lerp(Math.max(b.rx, b.ry) * 2, C.oGlyph.stroke * S, b.ring);
              const fill = (col as Record<string, string>)[b.colorKey];
              return (
                <g key={i}>
                  {b.ring <= 0 ? (
                    <ellipse cx={b.x} cy={b.y} rx={b.rx} ry={b.ry} fill={fill} />
                  ) : (
                    <ellipse cx={b.x} cy={b.y} rx={Math.max(0.1, b.rx - strokeW / 2)} ry={Math.max(0.1, b.ry - strokeW / 2)} fill="none" stroke={fill} strokeWidth={strokeW} />
                  )}
                  {i === 1 ? (
                    <Eyes cx={b.x} cy={b.y + (b.ring > 0.5 ? b.ry * 0.12 : 0)} r={lerp(K.radius, (C.oGlyph.width / 2 - C.oGlyph.stroke) * S * C.eyesInO, b.ring)} f={f}
                      blinkAt={[C.wink, C.wink + 9]} look={f > C.wink + 14 ? -0.7 : 0} />
                  ) : null}
                </g>
              );
            })
          : null}
      </svg>

      {/* the other letters spring out around the O's */}
      {lay
        ? lay.letters.map((l, idx) => {
            if (l.isO) return null;
            const near = Math.min(...lay.os.map((o) => Math.hypot(o.cx - l.cx, o.cy - l.cy)));
            const delay = C.letters.start + Math.round(near / 120) * C.letters.stagger + (idx % 2);
            const t = f - delay;
            if (t < 0) return null;
            const s = spring(t, 0.55, 0.5);
            const rot = (idx % 2 ? 14 : -14) * (1 - s);
            return (
              <div key={idx} style={{ position: "absolute", left: l.x, top: l.y, width: l.w, height: lay.size, fontFamily: C.font.family, fontWeight: 700, fontSize: lay.size,
                lineHeight: `${lay.size}px`, color: col.cream, textAlign: "center", opacity: clamp(t / 3), transform: `translateY(${(1 - s) * 30}px) scale(${s}) rotate(${rot}deg)`,
                transformOrigin: "50% 70%", whiteSpace: "nowrap" }}>{l.ch}</div>
            );
          })
        : null}
    </AbsoluteFill>
  );
};

export const Playful: React.FC = () => {
  const ready = useFont();
  const fps = C.output.fps;
  return (
    <AbsoluteFill>
      <Scene ready={ready} />
      {C.sounds.map((s, i) => {
        const start = Math.max(0, Math.round(s.frame + 1 - (s.peakMs / 1000) * fps));
        return (
          <Sequence key={i} from={start} durationInFrames={Math.round(fps * 1.2)}>
            <Audio src={staticFile(s.file)} volume={s.volume * C.masterVolume} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
