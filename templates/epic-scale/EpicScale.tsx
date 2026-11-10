// Epic scale: grammar learned from Beeple's 3D work, rebuilt as 2D layers in code.
// A tiny human against something colossal, deep atmospheric haze, god rays, a saturated dusk
// palette and a slow cinematic push-in with parallax. No images: everything is drawn here.
import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";

export const epicConfig = {
  title: "", // optional: small wide-tracked caption, e.g. "DAY ONE". Leave "" for none (Beeple's pieces rarely use text)
  durationInSeconds: 6,
  palette: {
    skyTop: "#0B1030",
    skyMid: "#5A1E5C",
    horizon: "#FF7A45",
    sun: "#FFD9A0",
    haze: "#FF9E7A",
    giant: "#120A1C",
    giantRim: "#FF5DA2",
    city: "#1A0F26",
    ground: "#0A0612",
    glow: "#7CF7FF", // neon accent
  },
  push: { from: 1.0, to: 1.09 }, // camera push-in over the whole shot
  dustCount: 70,
  seed: "epic-01",
};

const P = epicConfig.palette;

// Parallax: farther layers move less during the push.
const Layer: React.FC<{ depth: number; push: number; children: React.ReactNode; originY?: number }> = ({ depth, push, children, originY = 62 }) => (
  <AbsoluteFill style={{ transform: `scale(${1 + (push - 1) * depth})`, transformOrigin: `50% ${originY}%` }}>{children}</AbsoluteFill>
);

const City: React.FC<{ seed: string; y: number; h: number; color: string; count: number }> = ({ seed, y, h, color, count }) => {
  const rects = Array.from({ length: count }, (_, i) => {
    const w = 18 + random(`${seed}-w-${i}`) * 50;
    const hh = h * (0.25 + random(`${seed}-h-${i}`) ** 2 * 0.95);
    return { x: (i / count) * 1920 + random(`${seed}-x-${i}`) * 20 - 10, w, hh };
  });
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      {rects.map((r, i) => <rect key={i} x={r.x} y={y - r.hh} width={r.w} height={r.hh + 400} fill={color} />)}
    </svg>
  );
};

// The colossal figure: a kneeling stone-and-metal giant built from simple shapes, with a neon visor.
const Giant: React.FC<{ frame: number }> = ({ frame }) => {
  const visor = 0.75 + 0.25 * Math.sin(frame / 9);
  return (
    <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute" }}>
      <defs>
        <linearGradient id="rim" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor={P.giantRim} stopOpacity="0.55" />
          <stop offset="0.12" stopColor={P.giant} stopOpacity="1" />
          <stop offset="1" stopColor={P.giant} stopOpacity="1" />
        </linearGradient>
        <filter id="visorGlow" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="10" /></filter>
      </defs>
      {/* shoulders and torso, rising from the haze */}
      <path d="M560 1080 C 600 760, 760 660, 960 650 C 1160 660, 1320 760, 1360 1080 Z" fill="url(#rim)" />
      {/* head */}
      <path d="M842 640 C 830 470, 880 330, 960 320 C 1040 330, 1090 470, 1078 640 C 1040 680, 880 680, 842 640 Z" fill="url(#rim)" />
      {/* neon visor */}
      <rect x="880" y="470" width="160" height="16" rx="8" fill={P.glow} opacity={visor} filter="url(#visorGlow)" />
      <rect x="880" y="472" width="160" height="12" rx="6" fill={P.glow} opacity={visor} />
      {/* antenna spine for a sci-fi silhouette */}
      <rect x="954" y="230" width="12" height="100" fill={P.giant} />
      <circle cx="960" cy="226" r="7" fill={P.glow} opacity={0.6 + 0.4 * Math.sin(frame / 5)} />
    </svg>
  );
};

// God rays from behind the giant.
const Rays: React.FC<{ frame: number }> = ({ frame }) => (
  <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.32 }}>
    <div style={{ position: "absolute", left: 960 - 1400, top: 330 - 1400, width: 2800, height: 2800, borderRadius: "50%",
      background: `repeating-conic-gradient(from ${frame * 0.04}deg at 50% 50%, rgba(255,210,170,0.0) 0deg, rgba(255,210,170,0.22) 3deg, rgba(255,210,170,0.0) 7deg, rgba(255,210,170,0.0) 13deg)`,
      maskImage: "radial-gradient(circle at 50% 50%, black 0%, transparent 55%)", WebkitMaskImage: "radial-gradient(circle at 50% 50%, black 0%, transparent 55%)",
      filter: "blur(14px)" }} />
  </AbsoluteFill>
);

const Haze: React.FC<{ y: number; h: number; speed: number; opacity: number; frame: number; color: string }> = ({ y, h, speed, opacity, frame, color }) => (
  <div style={{ position: "absolute", left: -400 + ((frame * speed) % 400), top: y, width: 2720, height: h, opacity, filter: "blur(40px)",
    background: `repeating-linear-gradient(90deg, ${color} 0px, transparent 260px, ${color} 520px)` }} />
);

const Dust: React.FC<{ frame: number; count: number; seed: string }> = ({ frame, count, seed }) => (
  <svg width={1920} height={1080} style={{ position: "absolute", mixBlendMode: "screen" }}>
    {Array.from({ length: count }, (_, i) => {
      const x = (random(`${seed}-dx-${i}`) * 2200 + frame * (0.3 + random(`${seed}-ds-${i}`) * 0.9)) % 2000 - 40;
      const y = random(`${seed}-dy-${i}`) * 1080 + Math.sin(frame / 25 + i) * 6;
      const r = 0.8 + random(`${seed}-dr-${i}`) * 2.4;
      return <circle key={i} cx={x} cy={y} r={r} fill={P.sun} opacity={0.15 + random(`${seed}-do-${i}`) * 0.5} />;
    })}
  </svg>
);

// A tiny person on a ridge: the scale reference that makes everything else feel huge.
const TinyHuman: React.FC = () => (
  <svg width={1920} height={1080} style={{ position: "absolute" }}>
    <g transform="translate(1180 905)">
      <circle cx="0" cy="-30" r="5" fill="#05030A" />
      <path d="M-5 -24 L5 -24 L6 -6 L3 12 L-3 12 L-6 -6 Z" fill="#05030A" />
      <line x1="-2" y1="12" x2="-3" y2="26" stroke="#05030A" strokeWidth="3" />
      <line x1="2" y1="12" x2="3" y2="26" stroke="#05030A" strokeWidth="3" />
    </g>
  </svg>
);

export const EpicScale: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const C = epicConfig;
  const push = interpolate(frame, [0, durationInFrames], [C.push.from, C.push.to], { easing: Easing.inOut(Easing.cubic) });
  const fadeIn = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const titleIn = interpolate(frame, [40, 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ background: P.skyTop, overflow: "hidden" }}>
      <AbsoluteFill style={{ opacity: fadeIn }}>
        {/* sky and sun: almost no parallax */}
        <Layer depth={0.2} push={push}>
          <AbsoluteFill style={{ background: `linear-gradient(180deg, ${P.skyTop} 0%, ${P.skyMid} 45%, ${P.horizon} 78%, ${P.haze} 100%)` }} />
          <div style={{ position: "absolute", left: 960 - 260, top: 330 - 260, width: 520, height: 520, borderRadius: "50%",
            background: `radial-gradient(circle, ${P.sun} 0%, ${P.sun}AA 25%, transparent 70%)` }} />
        </Layer>
        <Layer depth={0.35} push={push}><Rays frame={frame} /></Layer>
        {/* far city, swallowed by haze */}
        <Layer depth={0.45} push={push}>
          <City seed={`${C.seed}-far`} y={820} h={220} color={P.city} count={60} />
          <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 55%, ${P.haze}99 80%, ${P.haze}CC 100%)` }} />
        </Layer>
        {/* the giant */}
        <Layer depth={0.7} push={push}><Giant frame={frame} /></Layer>
        <Layer depth={0.75} push={push}>
          <Haze y={760} h={260} speed={0.6} opacity={0.55} frame={frame} color={`${P.haze}`} />
        </Layer>
        {/* near city and ridge */}
        <Layer depth={1.0} push={push}>
          <City seed={`${C.seed}-near`} y={960} h={160} color={P.ground} count={34} />
          <svg width={1920} height={1080} style={{ position: "absolute" }}>
            <path d="M0 1080 L0 960 C 400 930, 900 950, 1180 931 C 1400 925, 1700 960, 1920 950 L1920 1080 Z" fill={P.ground} />
          </svg>
          <TinyHuman />
        </Layer>
        <Layer depth={1.2} push={push}>
          <Haze y={900} h={240} speed={1.4} opacity={0.35} frame={frame} color={`${P.haze}`} />
          <Dust frame={frame} count={C.dustCount} seed={C.seed} />
        </Layer>
      </AbsoluteFill>
      {/* grade: vignette + cool shadows / warm highlights */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(5,2,15,0.75) 100%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(40,60,160,0.18), rgba(255,120,60,0.08))", mixBlendMode: "soft-light" }} />
      {C.title ? (
        <div style={{ position: "absolute", left: 96, bottom: 84, color: "#FFE9D6", fontFamily: "Inter, Arial, sans-serif", fontWeight: 600,
          fontSize: 28, letterSpacing: "0.5em", opacity: titleIn, transform: `translateY(${(1 - titleIn) * 12}px)` }}>{C.title}</div>
      ) : null}
    </AbsoluteFill>
  );
};
