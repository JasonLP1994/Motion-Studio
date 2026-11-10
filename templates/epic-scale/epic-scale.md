# Epic scale

Style ID: epic-scale
Shown as: Epic scale (Beeple-inspired)
Best for: Openers, title cards, music visuals, a dramatic backdrop behind a headline or a product.

Grammar learned from Beeple (Mike Winkelmann). He builds scenes in Cinema 4D, renders in Octane, and in his words does little post: colour correction, atmosphere and sky replacement in Photoshop. His film Manifest Destiny was cloner and instance-driven crowds with no compositing, straight from Cinema 4D and Octane with one colour grade (Maxon, CGW, Befores & Afters). Style write-ups describe massive scale, vibrant colour and a surreal, otherwise-worldly atmosphere around tech and society themes (Midlibrary, artnet). The traits below beyond that are my own reading of his work. Take the grammar only: never copy his characters, celebrity caricatures, compositions or series names (no "Everydays").

## Look
- Scale contrast is the whole idea: one tiny human (a few px tall) against something colossal: a giant figure, a monolith, a machine, a product.
- Deep atmosphere: haze swallows the far layers, so depth reads through value, not detail. Silhouettes over texture.
- Saturated cinematic dusk: deep navy top, magenta middle, hot orange horizon; one neon accent (cyan) on the giant.
- Light from behind: a glowing sun or halo behind the giant, soft god rays, rim light on its edge.
- Grade: cool shadows, warm highlights, heavy vignette. Very little or no text.

## Motion
- One slow camera move per shot: a push-in from 1.0 to about 1.09 over the whole shot, Easing.inOut(cubic).
- Parallax: every layer scales by its depth (sky 0.2, giant 0.7, foreground 1.0 to 1.2), so the push feels 3D.
- Life in the details only: drifting haze bands, dust motes, a pulsing visor or antenna light. The giant itself stays still: stillness reads as massive.
- Fade in from black over about 0.6 s. Optional title: wide-tracked caps, fades up after 1.3 s.

## Specs
- 16:9 1920×1080, 30 fps, 6 s (loops well as a backdrop).
- Palette: skyTop #0B1030, skyMid #5A1E5C, horizon #FF7A45, sun #FFD9A0, haze #FF9E7A, giant #120A1C, rim #FF5DA2, neon #7CF7FF.
- Layer order: sky + sun, rays (screen, 0.32 opacity, blurred 14 px), far city + haze gradient, giant, mid haze, near city + ridge + tiny human, near haze + dust, vignette, grade.
- Tiny human about 55 px tall at 1080, standing on the ridge line, offset from centre.

## Build
1. Copy EpicScale.tsx into src/ and register it (see src/Root.tsx). Everything is SVG and CSS: no images, no 3D engine.
2. Change the story by swapping the giant (an SVG path) and the palette in epicConfig. Keep the tiny human.
3. Use `random(seed)` for cities and dust so every render is identical.
4. For real 3D (camera orbit, true lighting), use @remotion/three with simple low-poly forms and fog. Budget more time and render cost.
5. Over a user's photo: put the photo as the far layer, add haze, a halo and parallax on top. Ask for a cut-out (OpenArt Extract Layers) to put haze between the subject and the background.

## Known pitfalls
- Hard, regular god rays look like a cartoon sunburst. Keep them faint, blurred and masked to a radius.
- Detail in the far distance kills depth. Push far layers into the haze colour.
- Without the tiny human, the giant just looks like a big shape.
- Big blurs on full-frame layers slow renders. Keep blur layers few.
- 2D can't fully imitate a 3D render: say so to the user and offer the @remotion/three route for hero shots.

## Copy prompt
See prompt.txt in this folder.
