import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { Test } from "./Test";
import { testConfig as c } from "./config";
import { Duppy, totalFrames } from "./duppy/Duppy";
import { duppyConfig as d } from "./duppy/config";
import { EpicScale, epicConfig } from "./styles/EpicScale";
import { MaterialLoop, materialConfig } from "./styles/MaterialLoop";
import { Intro } from "./intro/Intro";
import { Calib } from "./playful/Calib";
import { Playful } from "./playful/Playful";
import { playfulConfig as pc } from "./playful/config";
import { introConfig as ic } from "./intro/config";
import { LogoSting } from "./sting/LogoSting";
import { MoGraph } from "./c4d/MoGraph";
import { PaintedStatue } from "./statue/Statue";
import { statueConfig as stc } from "./statue/config";
import { c4dConfig as cc } from "./c4d/config";
import { stingConfig as sc } from "./sting/config";
import { IonadeSting } from "./ionade/Ionade";
import { ionadeConfig as ion } from "./ionade/config";
import { KineticSymbols } from "./kinetic/KineticSymbols";
import { kineticConfig as kc } from "./kinetic/config";
import { GraffitiFlip } from "./grunge/GraffitiFlip";
import { graffitiConfig as gc } from "./grunge/config";
import { LostData } from "./car/LostData";
import { carConfig as cc2 } from "./car/config";
import { RedGlitch } from "./ferrari/RedGlitch";
import { redConfig as rc } from "./ferrari/config";
import { Kingz } from "./kingz/Kingz";
import { kingzConfig as kz } from "./kingz/config";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <Composition id="Test" component={Test} durationInFrames={c.fps * c.durationInSeconds} fps={c.fps} width={c.width} height={c.height} />
      <Composition id="Duppy" component={Duppy} durationInFrames={totalFrames} fps={d.output.fps} width={d.output.width} height={d.output.height} />
      <Composition id="EpicScale" component={EpicScale} durationInFrames={30 * epicConfig.durationInSeconds} fps={30} width={1920} height={1080} />
      <Composition id="MaterialLoop" component={MaterialLoop} durationInFrames={30 * materialConfig.durationInSeconds} fps={30} width={1920} height={1080} />
      <Composition id="Intro" component={Intro} durationInFrames={ic.output.fps * ic.output.durationInSeconds} fps={ic.output.fps} width={ic.output.width} height={ic.output.height} />
      <Composition id="Calib" component={Calib} durationInFrames={1} fps={30} width={1080} height={1080} />
      <Composition id="Playful" component={Playful} durationInFrames={pc.output.durationInFrames} fps={pc.output.fps} width={pc.output.width} height={pc.output.height} />
      <Composition id="LogoSting" component={LogoSting} durationInFrames={sc.output.durationInFrames} fps={sc.output.fps} width={sc.output.width} height={sc.output.height} />
      <Composition id="C4DMoGraph" component={MoGraph} durationInFrames={cc.output.fps * cc.output.durationInSeconds} fps={cc.output.fps} width={cc.output.width} height={cc.output.height} />
      <Composition id="PaintedStatue" component={PaintedStatue} durationInFrames={stc.output.fps * stc.output.durationInSeconds} fps={stc.output.fps} width={stc.output.width} height={stc.output.height} />
      <Composition id="IonadeSting" component={IonadeSting} durationInFrames={ion.output.durationInFrames} fps={ion.output.fps} width={ion.output.width} height={ion.output.height} />
      <Composition id="KineticSymbols" component={KineticSymbols} durationInFrames={kc.output.durationInFrames} fps={kc.output.fps} width={kc.output.width} height={kc.output.height} />
      <Composition id="GraffitiFlip" component={GraffitiFlip} durationInFrames={gc.output.durationInFrames} fps={gc.output.fps} width={gc.output.width} height={gc.output.height} />
      <Composition id="LostData" component={LostData} durationInFrames={cc2.output.durationInFrames} fps={cc2.output.fps} width={cc2.output.width} height={cc2.output.height} />
      <Composition id="RedGlitch" component={RedGlitch} durationInFrames={rc.output.durationInFrames} fps={rc.output.fps} width={rc.output.width} height={rc.output.height} />
      <Composition id="Kingz" component={Kingz} durationInFrames={kz.output.durationInFrames} fps={kz.output.fps} width={kz.output.width} height={kz.output.height} />
    </>
  );
};
