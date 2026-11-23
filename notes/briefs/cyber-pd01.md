# Brief: PD-01 cyberpunk 3D motion piece

Status: brief done; next checkpoint = plan + three style frames.

| Item | Answer |
|---|---|
| Kind | 3D motion design, cyberpunk |
| Reference | references/cyber-helmet-ref.jpg (grammar only: black hard-surface helmet with hot-pink accents on an electric-blue page, technical HUD layout, model/serial callouts, barcodes, coordinates, Japanese micro-type, big angular masthead; NOT its name, text or design) |
| Hero model | "HelmetConcept" by foor1o (Sketchfab 83bdd9464ea4497bb687259afc4d8ae8, CC-BY 4.0, via Objaverse): angular helmet on an armoured collar |
| Purpose | Portfolio / showreel |
| Format | 16:9, 1920x1080, 10-15 s |
| Quality | Best: Cycles + OIDN + AI upscale + RIFE where smooth (notes/ai-enhance.md recipe), product lighting rules, camera rules |
| Masthead | PD-01 (Phillips Digital model 01); callouts in the same voice (SERIAL PD01-26A, MODEL 01 ...), copy to be approved |
| Colours | Electric blue page, hot pink accents, black helmet |
| Motion | Slow orbit + push-in; HUD draws on + glitch; visor lights up / panels open (power-on); macro detail shots before the reveal |
| Sound | Original synthwave/cyber score + SFX (power-up, HUD blips), -14 LUFS + silent copy |
| Ending | Phillips Digital logo (lime circle "p." from inputs/phillips-digital-logo.jpg) |
| Extras | Thumbnail / poster frame (default); credits where licences require (CC-BY helmet) |

## Draft structure (for the plan checkpoint)
0-4 s macro close-ups of panels, vents and labels in the dark as pink lights blink on (power-on) -> 4-8 s slow orbit/push-in
to the profile hero as the visor lights and the blue page floods in -> 8-11 s HUD draws on with glitches (PD-01 masthead,
callouts, barcodes, coordinates, micro-type) -> 11-13 s glitch to the Phillips Digital logo.
Skill stack: motion-art-direction, hard-surface (decals/panels), lighting (product rig), camera-cinematography (product-camera),
kinetic-typography (HUD), remotion-transitions (glitch), logo-animation, sound-effects, finishing (product_minimal / cover_punch).

## Look development (work/cyber/pd01.py, copy scripts/blender/pd01_helmet.py)
- Helmet recoloured in the shader from its own albedo: orange shell -> glossy black, dark parts -> gunmetal, small light-grey
  plates on the helmet (z > 0.4) -> emissive hot pink; collar stays charcoal. Coat 0.7 / 0.05 for the glossy black.
- Rendered on a TRANSPARENT background (scripts/denoise/oidn_render.py now keeps alpha) and composited over exact electric blue
  #1A2BFF in Remotion: AgX had softened the blue to cornflower. Reflections see a dim navy studio (world: Light Path camera/other).
- Lighting: product rig (key softbox + top strip, back-left cool strip, white side strip, pink back strip at a grazing angle for a
  rim only, top rim, glossy-invisible fill, black cards). Lesson: a strong pink light washed magenta over the whole black shell;
  pink belongs at grazing angles (rim) and on emissive accents.
- Look frames: notes/frames/pd01-look4.jpg. Next: cleaner black shell, HUD layout comp, style frames, camera plan.
- Shell clean-up: worn-paint blotches in the source albedo/roughness -> helmet gunmetal multiplier 0.06 and an even roughness 0.2 above the collar. Look: notes/frames/pd01-look5.jpg.

## v2 figure (user: "more hot pink on the material", "hoodie and helmet aren't together")
- Models: "Scifi Helmet" by sunix + "Hoodie" by Badboy17Aiden (both CC-BY 4.0). Script: scripts/blender/pd01_v2_figure.py.
- Paint from the helmet's own maps: work/cyber2/tex/mag.png (rear shell, from the metal map) = hot pink; seam.png (panel lines,
  labels, rivets, from the normal map) = glowing pink on black, black on the pink shell. Pink side modules + triangle decals modelled.
- Fit: hood deleted above the neckline; a collar is lofted from the neck opening up to the helmet's own bottom outline (helmet sits
  inside it), plus a pink-lined hood roll behind the neck. Sleeves rotated 28 deg down from the A-pose.
- Colour: Standard view, exposure -0.8, PINK linear (0.9, 0, 0.12): AgX turned hot pink pastel/salmon.
- Look: notes/frames/pd01-v2-look18.jpg. Dark front stripe fixed (look21): the hoodie model is an OPEN jacket with no body, so the
  inside of the back panel showed; a front panel is now lofted between the real front edges (+-0.2) with the pink zip on it.
  Fabric: dark navy albedo, low specular (black albedo read grey on the lit side and black on the front). Collar lining: the collar top now rolls outward into a thin hot-pink lip around the helmet base (look23).
- HUD layout draft: Remotion comp `PD01HUD` (src/pd01/, all copy in src/pd01/config.ts, DRAFT until the user approves).
  Still: work/cyber2/hud/hud_v2.png. Figure is the 720p look render scaled up (soft); the final needs a 1920x1080 render framed
  for this layout. The helmet still shows the model's own "H254" label (could swap for a PD-01 decal).
