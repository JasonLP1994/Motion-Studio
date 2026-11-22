# Product camera language (Blender) — learned on the phone case v2

## Rules
1. Constant-speed moves inside cut-together sequences (LINEAR interpolation on camera + target). Default Bezier ease-in/out
   parks the camera at every cut and the edit feels floaty; a slider / motion-control move keeps momentum through the cut.
2. Arcs, not straight lines. Orbit while dollying (camera parented to a pivot empty at the product, or 3+ keys on a curve):
   light travels across the edges and the depth reads. A straight pull-back looks like a zoom.
3. Counter-motion for parallax: if the product turns, orbit the camera the opposite way (same way cancels out).
4. Rack focus with a separate focus empty (camera DoF focus_object), pulled slowly from one detail to the next, held, then moved.
   Macro product work keeps the hero detail sharp; use shallow focus to guide, not to hide.
5. Speed ramp the reveal: expo ease-out (fast in, decelerating into the hold), then a slow linear drift so the last frame is alive.
6. Land moves on beats: decelerate onto the impact frame (the ring click), not past it.
7. Tiny NOISE F-curve modifier on macro camera location (strength ~0.003-0.004, scale ~45 frames) so close-ups breathe.
   Keep hero/reveal shots clean (no noise).
8. Lenses: 60-85 mm for details (compression, clean backgrounds), 50 mm for chases, 35-40 mm for the hero reveal.
9. Check framing at the start, middle and end of every move before a full render (Eevee half-res is enough).
10. Mystery-to-reveal structure: macros that don't show the whole object, then one wide reveal.

## Blender recipe
- `kp.interpolation = 'LINEAR'` for constant speed; `kp.interpolation = 'EXPO'; kp.easing = 'EASE_OUT'` for the ramp.
- Orbit: `PIV` empty at the product, camera `parent = PIV`, key PIV rotation_euler Z; camera Track-To a target empty.
- Rack focus: `cam.data.dof.focus_object = EMPTY_Focus`, key the empty's location.
- Noise: `fc.modifiers.new('NOISE')` on each location F-curve.
Implementation: `camera2()` in work/blender/case/case_v2.py (scripts/blender/phone_case_v2.py).
