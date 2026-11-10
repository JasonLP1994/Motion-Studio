import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { testConfig as c } from "./config";

export const Test: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12 } });
  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: c.background, justifyContent: "center", alignItems: "center" }}>
      <div style={{ color: c.textColor, fontFamily: c.fontFamily, fontSize: c.fontSize, fontWeight: 800, opacity, transform: `scale(${0.8 + 0.2 * pop})` }}>
        {c.text}
      </div>
    </AbsoluteFill>
  );
};
