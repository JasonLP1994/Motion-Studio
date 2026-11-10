import React from "react";
import { AbsoluteFill } from "remotion";
import { TeachingGraphics } from "./TeachingGraphics";
import { teachingDemoCues, teachingDemoOutput, teachingTheme } from "./config";

// Illustrative skill preview. Not a real source transcript and contains no audio.
export const TeachingDemo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: teachingTheme.colors.bg }}>
    <AbsoluteFill
      style={{
        backgroundColor: teachingTheme.colors.charcoal,
        opacity: 0.48,
        left: 0,
        width: "32%",
        borderRight: "1px solid rgba(128, 184, 198, 0.13)",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: 75,
        top: 115,
        width: 450,
        color: teachingTheme.colors.white,
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <div style={{ fontSize: 32, letterSpacing: "0.14em", fontWeight: 800 }}>
        PHILLIPS ENGLISH
      </div>
      <div style={{ marginTop: 24, color: teachingTheme.colors.accent, fontSize: 23 }}>
        TEACHING GRAPHICS
      </div>
      <div style={{ marginTop: 28, fontSize: 26, lineHeight: 1.3, color: teachingTheme.colors.cream }}>
        Illustrative demo only.
      </div>
      <div style={{ marginTop: 12, fontSize: 20, lineHeight: 1.4, color: teachingTheme.colors.muted }}>
        Real edits use the words and timing from your lesson.
      </div>
    </div>
    <TeachingGraphics cues={teachingDemoCues} />
  </AbsoluteFill>
);

export const teachingDemoDurationInFrames =
  teachingDemoOutput.fps * teachingDemoOutput.durationInSeconds;
