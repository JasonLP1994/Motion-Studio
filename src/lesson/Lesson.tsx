// Phillips English lesson edit: the original take (uncut, trimmed at both ends) with
// transcript-timed teaching cards from src/teaching/TeachingGraphics.tsx.
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { TeachingGraphics } from "../teaching/TeachingGraphics";
import { lessonConfig as C } from "./config";

export const lessonFrames = Math.round((C.trim.end - C.trim.start) * C.output.fps);

export const Lesson: React.FC = () => {
  const scale = C.output.width / C.video.srcWidth;
  // Cue times are written in source seconds (straight from the transcript); shift them to the edit.
  const cues = C.cues.map((c) => ({ ...c, startSeconds: c.startSeconds - C.trim.start }));
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <OffthreadVideo
        src={staticFile(C.video.src)}
        trimBefore={Math.round(C.trim.start * C.output.fps)}
        style={{ position: "absolute", left: 0, top: C.video.offsetY, width: C.video.srcWidth * scale, height: C.video.srcHeight * scale }}
      />
      <TeachingGraphics cues={cues} design={C.design} />
    </AbsoluteFill>
  );
};
