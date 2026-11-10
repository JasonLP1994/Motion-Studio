# Code doodle

Best for: A hand-drawn character or scene when you have no artwork at all. Explainers, kids' content, cosy brand moments, paper and crayon looks.

New in the tutorial (chapter 3, 7:33): every line is SVG drawn by code. No image files, no image model.

## Look
- Children's-book wax crayon on toothy cream paper. Paper grain shows through everything.
- Thick waxy outlines in dark plum crayon, with grainy, broken edges and pressure that changes along the line. Not a clean pen line.
- Fills built from visible diagonal crayon strokes with gaps of paper between them, darker where strokes overlap and along the edges, slightly going outside the lines.
- Warm, fairly saturated crayon colours (peach, hot pink, sky blue, orange, golden yellow). White areas stay mostly paper with soft grey shading.
- Simple round characters: big head, dot or arc eyes, tiny nose, "w" mouth, whiskers.

## Motion
1. Outlines draw themselves on, background first, character last (about 2 s).
2. Crayon colours scribble in, left to right inside each shape (about 1.5 s).
3. The character comes alive with one small action (a blink, a flip, a wave), then idles with a gentle tail sway or steam.
4. Lines "boil" on twos: the wobble changes every 2 frames, like hand-drawn animation.

## Build
- Doodle.tsx in this folder is the full working example (Remotion, React, SVG). Reuse its `Shape` (outline draw-on plus crayon fill) and `Ln` (single stroke) helpers instead of starting from scratch.
- Draw each part as one closed SVG path. `Shape`, `Ln`, `CrayonLine` and `Scribble` are exported, so you can import them. The `d` prop is the clip length in frames. Give each `Shape` an outline window (a, b) and a fill window (fa, fb) in frames.
- One fixed paper-tooth noise decides where wax sticks, for lines and fills, so the grain stays put while the lines boil. The SVG filters are `kPaper` (paper grain), `kLine` (two jittered outline passes with ragged edges), `kWax` (stroke texture) and `kBleed` (colour slightly past the line).
- If it starts to look like flat vector art, check three things: paper showing between strokes, broken outline edges, and colour going a little outside the lines.
- Scale the timing to the voice line: the example slows its drawing up to 1.4x when the line is long.

### Starter scene
Copy Doodle.tsx into src/, then draw your own scene with its helpers. `CrayonDefs` holds the crayon filters and must be inside the same `<svg>`, or you get flat vector art with no wax.

```tsx
import {useCurrentFrame} from 'remotion';
import {CrayonDefs, PaperBg, Shape, Ln, W, H} from './Doodle';

export const MyDoodle: React.FC = () => {
  const f = useCurrentFrame();
  const boil = Math.floor(f / 2) % 3;
  return <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%">
    <CrayonDefs boil={boil} />
    <PaperBg />
    <Shape id="sun" d="M600 300 a120 120 0 1 0 1 0 Z" f={f} a={0} b={20} fa={30} fb={60} fill="#FFC81E" fill2="#F59A12" box={[480, 180, 720, 420]} />
    <Ln d="M560 520 Q600 560 640 520" f={f} a={20} b={30} />
  </svg>;
};
```

## Known pitfalls
- Keep shapes simple. Code-drawn characters take longer and cost more tokens than a generated image, so this suits a simplified look. For a refined character, generate it on OpenArt and animate it with another template.
- Leave a small overlap between head and body paths, or a gap shows between them.
- Check the top of hats and ears at 16:9: a scale-up can crop them.
