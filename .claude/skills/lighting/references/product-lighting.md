# Product lighting for glossy objects (Blender Cycles) — learned on the phone case v2

Core rule: on a glossy product you light the REFLECTIONS. A flat glossy face is a mirror of whatever is in front of it,
so every light (and every dark card) is designed by where it shows up in the surface.

## Rig (what worked)
| Element | Setup | Why |
|---|---|---|
| Key | Broad area softbox in front/above (2.6 x 1.2 m, modest power) + a thin brighter strip on its top edge | Reads as a smooth gradient sheen across the flat back. Area lights sample cleanly; big emissive gradient planes looked blotchy at 48 spp after denoising |
| Edge strips | Tall thin area lights (0.18 x 3.2 m) BEHIND-left/right at grazing angles | Crisp highlight lines along the rounded sides: defines the silhouette and lifts it off the backdrop |
| Rim top | Thin wide strip above-behind | Top edge line |
| Fill | Large, weak (~1/8 of key), and `visible_glossy = False` | Lifts the shading without a hard rectangle in the glossy surface |
| Accent kick (colour) | Thin strip behind, grazing (never in front of a glossy face) | A coloured edge line that ties product to set. In front it became a huge pale patch in the reflection |
| Negative fill | Black emission-0 planes, `visible_camera = False`, `visible_shadow = False` | Dark bands in the reflection: contrast and richer colour on glossy surfaces |
| Backdrop | Its own soft spot "pool" behind the product PLUS a wide soft wash over the floor, both light-linked to the backdrop only; product lights light-linked to the product only; keep some self-glow on the set | Gentle vignette that focuses the eye while the set keeps its colour. Lesson: with only a small pool the floor and every close-up went black (product lights no longer reach the set once linked) |

Light linking (Cycles, Blender 4.0+): `light_obj.light_linking.receiver_collection = collection`.

## Process
1. Start with the key alone, check the reflection shape on the biggest glossy face, then add strips, then cards, then fill.
2. If a hot patch appears and you can't tell where it comes from: render tiny frames with one light hidden at a time (24 spp,
   35 %): the culprit is the frame where it disappears. (Here: the accent light, not the key or fill.)
3. Keep values under clipping (AgX, small negative exposure), check at the hero angle AND the close-ups: rotating products move
   reflections, so judge the end pose too.
4. Avoid noisy emitters at low samples; prefer area lights, clamp indirect.
