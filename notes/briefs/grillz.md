# Grillz still (user: "make these grillz on this model", "really over the teeth like grills", "exactly like the references")
- Model: user's lips (Tripo AI export, inputs/grillz/lips.zip). References: inputs/grillz/speaking-test.mp4 + two stills
  (puffy enamel letters with gold rims fixed ON the teeth, rows meeting at the bite, warm low-key macro light).
- scripts/blender/grillz/measure_teeth.py finds the teeth (white texels on front-facing mouth faces) and fits each row:
  upper z +0.018..+0.089 (OPEN=0), front x = 0.280 - 1.51 y^2; lower z -0.063..-0.105, front x = 0.229 - 2.4 y^2.
- scripts/blender/grillz/grillz.py: each word is a thick gold body (Corben Bold, OFL; outline offset + round bevel) with a puffy
  emerald face proud of it, stretched to the measured tooth height, backs pressed onto the measured front surface, wrapped
  round the arch (depth along the local normal). Warm key + orange rim + glint strips, 85 mm f/4, AgX Punchy, black world.
- Final settings: UP_W=0.375 LO_W=0.33 TRACK=1.0 (defaults otherwise). renders/grillz-still-v1.png (Cycles 96 spp + OIDN, ~5 min).
- Lessons: flat text in front of the teeth reads as a caption. Grillz must cover the teeth gum-to-tip, follow the measured arch,
  have real depth and a rounded puffy face; keep the gold outline thin enough that counters stay open.
