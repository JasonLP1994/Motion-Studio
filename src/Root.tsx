import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { Test } from "./Test";
import { testConfig as c } from "./config";
import { Duppy, totalFrames } from "./duppy/Duppy";
import { duppyConfig as d } from "./duppy/config";
import { EpicScale, epicConfig } from "./styles/EpicScale";
import { MaterialLoop, materialConfig } from "./styles/MaterialLoop";
import { Intro } from "./intro/Intro";
import { introConfig as ic } from "./intro/config";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <Composition id="Test" component={Test} durationInFrames={c.fps * c.durationInSeconds} fps={c.fps} width={c.width} height={c.height} />
      <Composition id="Duppy" component={Duppy} durationInFrames={totalFrames} fps={d.output.fps} width={d.output.width} height={d.output.height} />
      <Composition id="EpicScale" component={EpicScale} durationInFrames={30 * epicConfig.durationInSeconds} fps={30} width={1920} height={1080} />
      <Composition id="MaterialLoop" component={MaterialLoop} durationInFrames={30 * materialConfig.durationInSeconds} fps={30} width={1920} height={1080} />
      <Composition id="Intro" component={Intro} durationInFrames={ic.output.fps * ic.output.durationInSeconds} fps={ic.output.fps} width={ic.output.width} height={ic.output.height} />
    </>
  );
};
