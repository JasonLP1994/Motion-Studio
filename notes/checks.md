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
- DO: keep the moody look for hero props: a dark silhouetted object in coloured haze, lit by its own glow, with wet reflections. The user preferred that to a product-lit, detailed retro TV ("this tv vibe looked better").
- DON'T let deep facade pieces (cantilevers, drawers) stick into the line of sight to the words: keep the street walls shallow in front of the text and check the last letters on a full-size frame.
- DO (product 3D, e.g. the slime shoe): the product must look real: real material textures (knit/mesh, leather with stitching, perforations, foam midsole, rubber tread, braided laces, metal eyelets), not flat painted bands. User: "the shoe needs to look like a shoe with shoe textures".
- DO: give product sets real atmosphere (layered haze, drifting smoke, dust, a soft halo behind the subject) and designed lighting (soft key, edge rims, top strip), with no light hotspots on the floor. User: "we need better atmosphere in the background ... the lighting could be improved".
- DO: keep product-set lighting dim and moody: low key light, the set falling into shadow, highlights only on edges. DON'T over-light so blacks turn grey and the haze goes milky. User: "we need dimmer lights not so bright".
- DO give product models real proportions (low collar, tapered toe, rounded cross-section) and a bold, on-concept design graphic; a plain boxy shape with flat panels "doesn't look good".
- DON'T let a bright softbox reflect off black design panels (they turn beige/gold): keep finished black materials low-reflectance; keep the rainbow reflections for the wet/slime phase.
- DO make "venom" slime a web of thin, dark, glossy, branching veins that crawl over the object and across the floor (the classic Blender venom-effect grammar), not just a smooth glossy coat; keep the veins inky (no big softbox reflections on them).
- DO light the slime shoe ident in dark blue and light blue (navy-to-ice softbox, deep blue backdrop glow, icy drain edge, cool grade); no rainbow or orange.
- DO start the slime shoe all white (triple white); the black-and-white design only appears once the slime drains off.
- DON'T hide Cycles noise with ffmpeg median/nlmeans smoothing (it smears, darkens and erases fine detail like veins). DO denoise with scripts/denoise/oidn_render.py (Intel OIDN with albedo + normal passes).
- DO keep dark leather parts a cool near-black (slight blue) under the blue lighting; neutral black read as brown/tan at the heel.
- DO keep the slime/tentacle section dark and moody (low softbox/wall light, edge highlights only); the lights flicker as the tentacles let go, then come up bright for the reveal.
- DO (snow globe / clay diorama): keep the whole scene in ONE colour family like the reference (blue: tiles, cabin, trees, base, backdrop), with snow white/icy and a single warm accent (window/lantern glow, small gold touches). User: "the same style on blue".
- DO (clay diorama / snow globe): frame close like the reference: the little world fills ~60% of the frame width, camera ~33 deg down; DON'T show the whole object small in the middle (user: "more zoomed in ... it seems too far away").
- DO (clay diorama): make materials read as playdough / soft plastic: satin roughness ~0.4, soft clear coat ~0.3, subsurface ~0.2 so rounded corners catch broad highlights and shadow sides stay colourful; let lights reach glossy rays (keep them out of glass with light linking). Props fully smooth (subdivision, no faceting). User: "the lighting hits the corners nicely ... they look more like clay playdough or plastic".
- DO (snow globe): push the material between plastic and playdough: glossier coat and tighter highlights than matte clay, but keep the soft subsurface. User: "slightly more reflection ... we can push it more".
- DO (snow globe): give the globe a soft back shadow on the floor like the reference tile shots.
- DO: make stars and flat ornaments chunky 3D shapes so they still read edge-on when the camera orbits.
- DON'T (clay diorama): light glossy toy materials with one huge soft key plus strong fill/sky: it flattens them and the plastic reflections disappear (user: "too bright ... you can't see the reflections"). DO: one smaller, brighter softbox (hidden from camera, light-linked out of the glass) above-right, low fill/sky, glossy coat ~1.0 / roughness ~0.07, and keep snow just below white (icy blue) so it doesn't clip.
- DO: When copying a reference video, study it at its FULL frame rate before building: detect the cut times from frame differences, view consecutive frames around cuts and inside shots, and measure the tempo. DON'T infer transitions or motion from a 2-4 fps contact sheet (the kinetic-type job guessed sideways pushes; the reference actually used hard cuts every half-beat with a slow move inside each shot, variable-weight morphs, bursting/rotating glyph patterns and beat-flashing colours). User: "watch the video I sent".
- DO (LostData car glitch): palette is green, black and yellow; WHITE is used only for the digital annotations (user: "add white annotations in, digital fashion, randomly"). No other white or light-grey graphics.
- DO (RedGlitch Ferrari): palette red, black, white (the reference's own); keep every effect in palette: negative flashes as black-and-white (never CSS invert on red, it turns cyan), split as red/white (no RGB green/blue fringes). User asked for "more crazy, more glitchy, more wild" than LostData.
- DO (RedGlitch Ferrari v2): flat paper-white background with SAM 2 cut-outs; graphics in black ink on paper, red as the accent.
- DO: when a word sits behind a rotoscoped subject, keep the identifying letters visible (move it, or put a solid copy in front with an outline copy behind). DON'T let type touch the frame edge (KINGZ v1 clipped C and F).
- DO: when footage is inverted (negative), switch yellow/white graphics to black ink so they stay readable on the light negative.
- DO (Blender product build-ons like the lime case reference): build the object from its own edges with a torn, noisy growth front (rims lead as strands, panels fill behind, details last); DON'T use a straight planar wipe, and don't show the contents (the phone) until the shell is built.
- DON'T give inner and outer surfaces of a hollow grow-on object different arrival clocks: the inner front shows through as a second glowing line. DO drive the growth from one position-based field so there is exactly one glowing front.
- DO keep a product's identity hidden during a build-on: tight macros that ride the growth front, and the full object only in the final pull-back reveal.
- DO merge vertices (remove doubles) on imported glTF/Objaverse meshes before shading: split vertices make chrome look faceted.
- DO on the Mutant cover: type glitches in, flickers, then glitches out and stays out; the last shot is the head alone, central.
- DO run every 3D render through the free local AI tools for the best look (notes/ai-enhance.md): Cycles + OIDN denoise where it's used, render 720p and AI-upscale (compact 2x; Real-ESRGAN for hero stills), RIFE in-betweens on smooth shots. Free tools only, never paid or cloud enhancers. RIFE never across cuts, glitch/strobe frames or beat hits.
- DO light glossy products by their reflections (gradient key + grazing edge strips + black cards + light-linked backdrop pool); never put a light or coloured accent in front of a big glossy face; fill with visible_glossy off. Guide: .claude/skills/lighting/references/product-lighting.md
