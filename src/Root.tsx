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
import { Flat2D } from "./flat2d/Flat2D";
import { PopZoom } from "./popzoom/PopZoom";
import { popConfig as pzc } from "./popzoom/config";
import { flatConfig as fc } from "./flat2d/config";
import { RubyFilm } from "./ruby/RubyFilm";
import { rubyConfig as rc } from "./ruby/config";
import { Showreel, showreelTotal } from "./showreel/Showreel";

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
      <Composition id="PopZoom" component={PopZoom} durationInFrames={pzc.output.durationInFrames} fps={pzc.output.fps} width={pzc.output.width} height={pzc.output.height} />
      <Composition id="RubyFilm" component={RubyFilm} durationInFrames={rc.output.durationInFrames} fps={rc.output.fps} width={rc.output.width} height={rc.output.height} />
      <Composition id="Flat2D" component={Flat2D} durationInFrames={fc.output.durationInFrames} fps={fc.output.fps} width={fc.output.width} height={fc.output.height} />
      <Composition id="Showreel" component={Showreel} durationInFrames={showreelTotal} fps={30} width={1920} height={1080} />
      <Composition id="IonadeSting" component={IonadeSting} durationInFrames={ion.output.durationInFrames} fps={ion.output.fps} width={ion.output.width} height={ion.output.height} />
    </>
  );
};
