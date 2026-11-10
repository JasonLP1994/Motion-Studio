import React from "react";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import "@fontsource/inter/400.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import { teachingTheme as T } from "./config";

// These are OPTIONAL presentation defaults, not fixed art direction.
// For a distinctive Daily Duppy-style, cinematic, or other full visual treatment,
// choose the appropriate Motion Studio template instead of forcing these cards.
export type TeachingDesign = {
  palette?: Partial<typeof T.colors>;
  fontFamily?: string;
  layout?: "left" | "right" | "full";
  energy?: "calm" | "bold";
};

type Shared = {
  startSeconds: number;
  durationSeconds: number;
  side?: "left" | "right" | "full";
};

export type TeachingCue =
  | (Shared & { kind: "correction"; original: string; corrected: string; note?: string })
  | (Shared & { kind: "pronunciation"; word: string; stress: string; ipa?: string; tip?: string })
  | (Shared & { kind: "vocabulary"; basic: string; precise: string; context?: string })
  | (Shared & { kind: "interview"; question: string; steps: string[] })
  | (Shared & { kind: "conversation"; lines: { speaker: string; text: string }[]; tip?: string });

const cueTitle: Record<TeachingCue["kind"], string> = {
  correction: "GRAMMAR & ACCURACY",
  pronunciation: "PRONUNCIATION",
  vocabulary: "BETTER VOCABULARY",
  interview: "INTERVIEW ENGLISH",
  conversation: "PROFESSIONAL ENGLISH",
};

const limit = (v: number, low: number, high: number) => Math.max(low, Math.min(high, v));

const Reveal: React.FC<{
  at: number;
  frame: number;
  scale: number;
  children: React.ReactNode;
}> = ({ at, frame, scale, children }) => {
  const value = interpolate(frame, [at, at + 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        opacity: value,
        transform: "translateY(" + Math.round((1 - value) * 18 * scale) + "px)",
      }}
    >
      {children}
    </div>
  );
};

const CueCard: React.FC<{ cue: TeachingCue; lengthFrames: number; design: TeachingDesign }> = ({ cue, lengthFrames, design }) => {
  const colors = { ...T.colors, ...design.palette };
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const portrait = height > width;
  const scale = portrait ? limit(width / 1080, 0.78, 1.08) : limit(width / 1920, 0.5, 1.2);
  const side = cue.side ?? design.layout ?? (portrait ? "full" : "right");
  const cardWidth = Math.round(width * (side === "full" ? 0.82 : 0.405));
  const x =
    side === "left"
      ? Math.round(width * 0.055)
      : side === "right"
        ? width - cardWidth - Math.round(width * 0.055)
        : Math.round((width - cardWidth) / 2);
  const y = Math.round(height * (portrait ? 0.145 : 0.18));
  const arrival = spring({
    frame: Math.max(0, frame),
    fps,
    config: { damping: 17, stiffness: 145, mass: 0.9 },
  });
  const exitStart = Math.max(0, lengthFrames - 9);
  const exit = interpolate(frame, [exitStart, Math.max(exitStart + 1, lengthFrames)], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  const fs = (n: number) => Math.round(n * scale);
  const label: React.CSSProperties = {
    color: colors.accent,
    fontSize: fs(17),
    letterSpacing: "0.12em",
    fontWeight: 800,
    marginBottom: fs(9),
  };
  const phrase: React.CSSProperties = {
    fontSize: fs(43),
    lineHeight: 1.13,
    fontWeight: 800,
    overflowWrap: "anywhere",
  };
  const secondary: React.CSSProperties = {
    color: colors.cream,
    fontSize: fs(23),
    lineHeight: 1.32,
    overflowWrap: "anywhere",
  };
  const block: React.CSSProperties = {
    background: colors.panelInset,
    padding: fs(20),
    borderRadius: fs(12),
    marginTop: fs(15),
  };

  let content: React.ReactNode;
  switch (cue.kind) {
    case "correction":
      content = (
        <>
          <Reveal frame={frame} scale={scale} at={6}>
            <div style={block}>
              <div style={{ ...label, color: colors.wrong }}>ORIGINAL</div>
              <div style={{ ...phrase, color: colors.wrong, textDecoration: "line-through", textDecorationThickness: fs(3) }}>
                {cue.original}
              </div>
            </div>
          </Reveal>
          <Reveal frame={frame} scale={scale} at={14}>
            <div style={block}>
              <div style={label}>SAY INSTEAD</div>
              <div style={{ ...phrase, color: colors.accent }}>{cue.corrected}</div>
            </div>
          </Reveal>
          {cue.note ? (
            <Reveal frame={frame} scale={scale} at={22}>
              <div style={{ ...secondary, marginTop: fs(18) }}>{cue.note}</div>
            </Reveal>
          ) : null}
        </>
      );
      break;
    case "pronunciation":
      content = (
        <>
          <Reveal frame={frame} scale={scale} at={5}>
            <div style={{ ...phrase, fontSize: fs(61), color: colors.white, marginTop: fs(18) }}>{cue.word}</div>
          </Reveal>
          <Reveal frame={frame} scale={scale} at={13}>
            <div style={{ ...block, ...phrase, color: colors.accent }}>{cue.stress}</div>
          </Reveal>
          {cue.ipa ? (
            <Reveal frame={frame} scale={scale} at={20}>
              <div style={{ ...secondary, marginTop: fs(15) }}>IPA: {cue.ipa}</div>
            </Reveal>
          ) : null}
          {cue.tip ? (
            <Reveal frame={frame} scale={scale} at={24}>
              <div style={{ ...secondary, marginTop: fs(16) }}>{cue.tip}</div>
            </Reveal>
          ) : null}
        </>
      );
      break;
    case "vocabulary":
      content = (
        <>
          <Reveal frame={frame} scale={scale} at={6}>
            <div style={{ ...label, marginTop: fs(21), color: colors.muted }}>SIMPLE</div>
            <div style={{ ...phrase, color: colors.cream }}>{cue.basic}</div>
          </Reveal>
          <Reveal frame={frame} scale={scale} at={13}>
            <div style={{ ...label, marginTop: fs(21) }}>MORE PRECISE</div>
            <div style={{ ...phrase, color: colors.accent }}>{cue.precise}</div>
          </Reveal>
          {cue.context ? (
            <Reveal frame={frame} scale={scale} at={21}>
              <div style={{ ...secondary, marginTop: fs(20) }}>{cue.context}</div>
            </Reveal>
          ) : null}
        </>
      );
      break;
    case "interview":
      content = (
        <>
          <Reveal frame={frame} scale={scale} at={5}>
            <div style={{ ...phrase, fontSize: fs(37), marginTop: fs(16), color: colors.white }}>
              {cue.question}
            </div>
          </Reveal>
          {cue.steps.slice(0, 4).map((step, i) => (
            <Reveal key={i} frame={frame} scale={scale} at={14 + i * 8}>
              <div style={{ ...block, display: "flex", alignItems: "center", gap: fs(14), marginTop: fs(10) }}>
                <span style={{ ...phrase, fontSize: fs(30), color: colors.accent }}>{String(i + 1).padStart(2, "0")}</span>
                <span style={{ ...secondary, color: colors.white, fontWeight: 700 }}>{step}</span>
              </div>
            </Reveal>
          ))}
        </>
      );
      break;
    case "conversation":
      content = (
        <>
          {cue.lines.slice(0, 3).map((line, i) => (
            <Reveal key={i} frame={frame} scale={scale} at={6 + i * 12}>
              <div style={{ ...block, borderLeft: fs(4) + "px solid " + (i % 2 === 0 ? colors.accent : colors.muted) }}>
                <div style={label}>{line.speaker}</div>
                <div style={{ ...secondary, color: colors.white, fontSize: fs(30), fontWeight: 700 }}>{line.text}</div>
              </div>
            </Reveal>
          ))}
          {cue.tip ? (
            <Reveal frame={frame} scale={scale} at={32}>
              <div style={{ ...secondary, marginTop: fs(15) }}>{cue.tip}</div>
            </Reveal>
          ) : null}
        </>
      );
      break;
  }

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: cardWidth,
          maxHeight: Math.round(height * (portrait ? 0.56 : 0.69)),
          overflow: "hidden",
          boxSizing: "border-box",
          backgroundColor: colors.panel,
          color: colors.white,
          border: "1px solid " + colors.border,
          borderRadius: fs(design.energy === "bold" ? 3 : 22),
          padding: fs(33),
          boxShadow: "0 24px 60px rgba(0,0,0,0.36)",
          fontFamily: design.fontFamily ?? "Inter, Arial, sans-serif",
          opacity: exit * limit(arrival, 0, 1),
          transform: "translateY(" + Math.round((1 - arrival) * 28 * scale) + "px)",
        }}
      >
        <div style={{ display: "flex", gap: fs(14), alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ ...label, marginBottom: 0, color: colors.white }}>PHILLIPS ENGLISH</div>
          <div style={{ width: fs(34), height: fs(5), backgroundColor: colors.accent }} />
        </div>
        <div style={{ ...label, marginTop: fs(26) }}>{cueTitle[cue.kind]}</div>
        {content}
      </div>
    </AbsoluteFill>
  );
};

/**
 * Transparent overlay: place above the source footage inside an AbsoluteFill.
 * All times are in seconds and must be verified against real word timestamps
 * for a production lesson. Choose the side after inspecting the footage.
 */
export const TeachingGraphics: React.FC<{ cues: TeachingCue[]; design?: TeachingDesign }> = ({ cues, design = {} }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent", pointerEvents: "none" }}>
      {cues.map((cue, i) => {
        const duration = Math.max(1, Math.round(cue.durationSeconds * fps));
        return (
          <Sequence key={i} from={Math.max(0, Math.round(cue.startSeconds * fps))} durationInFrames={duration}>
            <CueCard cue={cue} lengthFrames={duration} design={design} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
