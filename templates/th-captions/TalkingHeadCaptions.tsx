// Talking head captions: designed captions on a talking-head clip, big words tucked behind the speaker.
// Works for 9:16 (this preview), 16:9 and 4:5: caption-plan.json sets the canvas, where the frame sits and every cue.
// Layers, bottom to top: blurred room (fills a tall canvas), the frame, the big words,
// the speaker cut out with their matte, then all other captions.
// Inputs in public/: frames/0001.jpg... (the clip as frames), mattes/0001.png... (white = person, same names),
// take.wav (the voice), caption-plan.json, fonts/. The cut-out is the same frame masked by its matte,
// so it can never drift out of sync with the video.
import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import plan from '../public/caption-plan.json';

type Word = {w: string; t: number};
type Cue = {id: string; group: string; start: number; end: number; text: string; role: 'support' | 'anchor' | 'hero';
  x: number; y?: number; bottom?: number; w?: number; dx?: number; size: number; color: string; align: 'left' | 'center' | 'right'; words: Word[]};
type Plan = {canvas: [number, number]; frame?: {crop: [number, number, number, number]; box: [number, number, number, number]}; background?: {crop: [number, number, number, number]}; cues: Cue[]};

const P = plan as unknown as Plan;
const [CW, CH] = P.canvas;
const SRC_W = 1920, SRC_H = 1080; // size of the frame files
const FRAMES = 425; // number of frame files in public/frames (change for your clip)
const FONT_CSS = `
@font-face{font-family:'Inter';font-weight:500;src:url(${staticFile('fonts/inter-latin-500-normal.woff2')}) format('woff2')}
@font-face{font-family:'Inter';font-weight:800;src:url(${staticFile('fonts/inter-latin-800-normal.woff2')}) format('woff2')}
@font-face{font-family:'Nunito';font-weight:900;src:url(${staticFile('fonts/nunito-latin-900-normal.woff2')}) format('woff2')}`;
const pad = (n: number) => String(n).padStart(4, '0');

// The frame (or its cut-out) cropped and scaled into the plan's box.
const FrameLayer: React.FC<{src: string; matte?: string; fadeTop?: number}> = ({src, matte, fadeTop}) => {
  const [cx, cy, cw] = P.frame?.crop ?? [0, 0, SRC_W, SRC_H];
  const [bx, by, bw, bh] = P.frame?.box ?? [0, 0, CW, CH];
  const s = bw / cw;
  const mask: any = matte ? {WebkitMaskImage: `url(${matte})`, maskImage: `url(${matte})`, WebkitMaskSize: '100% 100%', maskSize: '100% 100%', maskMode: 'luminance'} : {};
  const wrap: any = fadeTop ? {WebkitMaskImage: `linear-gradient(to bottom, transparent 0, black ${fadeTop}px)`, maskImage: `linear-gradient(to bottom, transparent 0, black ${fadeTop}px)`} : {};
  return <div style={{position: 'absolute', left: bx, top: by, width: bw, height: bh, overflow: 'hidden', ...wrap}}>
    <Img src={src} style={{position: 'absolute', left: -cx * s, top: -cy * s, width: SRC_W * s, height: SRC_H * s, ...mask}} />
  </div>;
};

// One group = one sentence: its cues stack in one zone. Both layers lay out the whole group and hide
// the cues that belong to the other layer, so big words and small captions line up exactly.
const Group: React.FC<{cues: Cue[]; layer: 'behind' | 'front'}> = ({cues, layer}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const t = f / fps, c0 = cues[0];
  const out = interpolate(t, [c0.end - 0.2, c0.end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (t < c0.start - 0.1 || out <= 0) return null;
  const w = c0.w ?? 560;
  const left = c0.align === 'left' ? c0.x : c0.align === 'right' ? c0.x - w : c0.x - w / 2;
  const vert: any = c0.bottom !== undefined ? {bottom: CH - c0.bottom} : {top: c0.y};
  return <div style={{position: 'absolute', left, width: w, ...vert, display: 'flex', flexDirection: 'column', opacity: out,
    alignItems: c0.align === 'left' ? 'flex-start' : c0.align === 'right' ? 'flex-end' : 'center'}}>
    {cues.map((c, k) => {
      const hero = c.role === 'hero', anchor = c.role === 'anchor';
      const mine = (layer === 'behind') === hero;
      const light = parseInt(c.color.slice(1, 3), 16) > 128;
      const shadow = hero ? 'none' : light ? '0 2px 14px rgba(20,6,30,.45)' : '0 1px 10px rgba(255,255,255,.55)';
      return <div key={c.id} style={{position: 'relative', left: c.dx ?? 0, visibility: mine ? 'visible' : 'hidden',
        marginTop: k === 0 ? 0 : Math.round(cues[k - 1].size * 0.18),
        fontFamily: hero ? 'Nunito' : 'Inter', fontWeight: hero ? 900 : anchor ? 800 : 500, fontSize: c.size, lineHeight: hero ? 0.9 : 1.04,
        letterSpacing: hero ? '-0.02em' : anchor ? '-0.015em' : '0', color: c.color, textShadow: shadow, textAlign: c.align, whiteSpace: hero ? 'nowrap' : 'normal'}}>
        {c.words.map((wd, i) => {
          const lf = f - Math.round(wd.t * fps) + 2; // land 2 frames before the word
          if (lf < 0) return <span key={i} style={{opacity: 0}}>{wd.w}{i < c.words.length - 1 ? ' ' : ''}</span>;
          const s = hero ? spring({frame: lf, fps, config: {damping: 13, stiffness: 170, mass: 0.9}}) : interpolate(lf, [0, 6], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          const y = hero ? interpolate(s, [0, 1], [40, 0]) : interpolate(s, [0, 1], [16, 0]);
          const sc = hero ? interpolate(s, [0, 1], [1.06, 1]) : 1;
          return <span key={i} style={{display: 'inline-block', opacity: Math.min(1, s * 1.4), transform: `translateY(${y}px) scale(${sc})`, transformOrigin: 'bottom'}}>{wd.w}{i < c.words.length - 1 ? ' ' : ''}</span>;
        })}</div>;
    })}
  </div>;
};

export const TalkingHeadCaptions: React.FC = () => {
  const f = useCurrentFrame();
  const n = pad(Math.min(f + 1, FRAMES));
  const groups = Object.values(P.cues.reduce((g: Record<string, Cue[]>, c) => ((g[c.group] ||= []).push(c), g), {}));
  const frame = staticFile(`frames/${n}.jpg`), matte = staticFile(`mattes/${n}.png`);
  const tall = !!P.frame && P.frame.box[1] > 0;
  return <AbsoluteFill style={{background: '#120a18', overflow: 'hidden'}}>
    <style>{FONT_CSS}</style>
    {P.background ? (() => { // an empty patch of wall, blurred and scaled up to fill the canvas behind the frame
      const [bx, by, bw] = P.background.crop, k = CW / bw * 1.15;
      return <Img src={frame} style={{position: 'absolute', left: -bx * k - CW * 0.075, top: -by * k - CH * 0.1, width: SRC_W * k, height: SRC_H * k, filter: 'blur(40px) brightness(.8)'}} />; })() : null}
    <FrameLayer src={frame} fadeTop={tall ? 110 : 0} />
    {groups.map((g) => <Group key={'b' + g[0].group} cues={g} layer="behind" />)}
    <FrameLayer src={frame} matte={matte} />
    {groups.map((g) => <Group key={'f' + g[0].group} cues={g} layer="front" />)}
    <Audio src={staticFile('take.wav')} />
  </AbsoluteFill>;
};
