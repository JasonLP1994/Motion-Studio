# Checks

DO / DON'T lines from corrections. Read before every render.


## Phillips English creative direction
- DO: Honour the art direction and reference chosen for **each specific video**, including energetic Daily Duppy-inspired, cinematic or experimental styles.
- DON'T: Force every Phillips English lesson into teal cards, fixed typography, a fixed insert count or soft transitions. Each video gets its own style.

## Delivery
- DO: Send finished videos to the user in the chat (SendUserFile).
- DON'T: Commit or push any rendered or source video to GitHub. Videos stay out of the repo (see .gitignore).
- DON'T: Edit lessons with charcoal/teal side-panel teaching cards (the 'Tell me about yourself' teaching-graphics edit was rejected and the skill deleted).
- DO: Build every video edit as a skill stack chosen from the video's content and style (see `motion-stack`): several complementary skills layered under one art direction, listed in the plan. DON'T: Default to a single skill or template.
- DO: On every video upload, take a quick look, then show the motion-stack skill picker with the most relevant options marked (Recommended). DO: When the user says "add this skill too", work it into the current plan without redoing approved parts.
- DON'T: Make 3D pieces with a static camera in a dark void and flat painted-on effects (the first painted-statue pass was 'not epic').
- DO: Make 3D pieces cinematic: a designed camera move with shake on impacts, slow motion on the key moment, atmosphere (light shafts, haze, dust), floor reflections, bloom, depth of field, film grade, particles and volume on effects, plus sound design.
- DO: Infinite background in 3D: the backdrop, the fog and the floor's far colour are ONE flat colour, so the floor melts away with no horizon line (the C4D "infinite floor" trick).
- DON'T: Show the lights. No visible light shafts, glows, lens blobs or hotspots on the floor; use out-of-shot omni lights (C4D-style) so only their light on the subject is seen.
- DO: For the Daredevil-titles look: everything bathed in red monochrome (maroon shadows, pink highlights), atmospheric dark tones, soft haze, satin-wet liquid.
- DO: Add see-through smoke drifting near the lens (two parallax layers) for atmosphere in 3D pieces.
- DO: For wet/glossy reflections use an invisible softbox (rectAreaLight, out of shot) plus a clear-coat layer on the liquid only; never a visible light or a point-light hotspot.
- DO: Liquid reveals behave like liquid: show the empty form first, then the liquid flows in and fills it (rivulets, a moving fill front, a glossy leading edge); never make paint just fade away.
- DO: For heavy 3D renders on this CPU machine, pass --timeout=600000 (max-quality frames exceed Remotion's 30s default and the render fails).
- DON'T: settle for the real-time WebGL look on hero 3D pieces; the user reads it as "PS2 game". DO: aim for render-engine realism (bounce light, true reflections in liquid, motion blur, volumetric dust, white specular highlights not crushed by the red grade).
- DON'T: use three-gpu-pathtracer (WebGL) on this machine: with no GPU, SwiftShader never finishes compiling its shader (even a 320x180 test sat 10+ min). For path-traced output use a CPU renderer (Blender Cycles) instead.
- DO: for hero 3D stills/video use Blender Cycles (scripts/blender/render_still.py fed by scripts/pathtrace export): the user approved the look ("this looks better") over the Remotion/WebGL render.
- DO (3D, Blender): give scenes real atmosphere: volumetric haze that scatters the emissive/neon light, real light beams through it, and floating dust. Flat compositor mist is not enough (user: "we need more atmosphere").
- DO: make materials react to light: wet floors with mirror puddles and ripples, satin/coated panels, bump seams. Light with several small hidden raking lights so highlights run along edges. Big hidden area lights show as pale rectangles in glossy surfaces.
- DO: use an infinite floor (cyclorama: floor curving up into a back wall, matched to the world colour) when an object sits in a void, so there's no horizon line.
- DO: architecture/towers need bevelled edges, embossed detail (ledges, bands, fins, recessed seams), varied silhouettes (setbacks, prisms, chamfered or spire tops) and more surface for light. Plain boxes look cheap.
- DO: building facades as cupboard/drawer fronts: modules pushed out by different depths with dark gaps and the odd lit slot (user: "bring them out like cupboards and drawers"). A window grid drowns the 3D detail.
