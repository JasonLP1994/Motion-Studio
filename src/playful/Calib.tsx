import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";
export const Calib: React.FC = () => {
  const [h] = useState(() => delayRender("font"));
  useEffect(() => { loadFont({ family: "Fredoka", url: staticFile("fonts/fredoka-latin-700-normal.woff2"), weight: "700" }).then(() => continueRender(h)); }, [h]);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <div style={{ position: "absolute", left: 100, top: 100, fontFamily: "Fredoka", fontWeight: 700, fontSize: 200, lineHeight: "200px", color: "#fff", whiteSpace: "nowrap" }}>HO</div>
    </AbsoluteFill>
  );
};
