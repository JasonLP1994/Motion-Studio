# Product graphics (3 looks)

Style ID: product-graphics
Best for: Product ads and launch clips: graphics on top of an AI video or product footage

## What this is
One way of working, three looks. The motion and the shot plan stay the same: graphics arrive a few frames after each cut, labels point at real features, a title sets the shot, everything resets at the next cut. Only the visual skin changes. Pick a look, or decide the finished look first with a still (make one frame of your clip in each art style, pick the one you like, then hand Claude the clip plus that still).

## Shared motion and build
- Inspect every shot, make new time-stamped anchors for this footage and point labels only at features that are visible. Never reuse coordinates from another clip.
- Graphics start about 9 frames after each cut and cut with the shot. Reveal one main callout at a time.
- Keep the product unobstructed. Never put text across the product itself.
- Fit every title and label with fitText/measureText from @remotion/layout-utils.
- Put copy, fonts, colours, timings and anchors in one config, so a headline change is one line (that is what makes A/B tests cheap).
- Don't invent technical data. Check frames at the start, middle and end of every shot.

## Look: Fashion editorial

Oversized fashion-editorial typography, a refined serif headline paired with small sans-serif details, restrained leader lines and generous negative space. Where a valid subject mask exists, place the large headline behind the product. Use a clear feature headline for each relevant beat. A small italic serif tagline in capitals sits bottom right and thin white flowing lines sweep behind the product.

### Specs
Preview is 1280x720 (16:9), 24 fps, real speed. Sizes below are at 1080 px wide; multiply by 1.78 for 1920x1080. Timings are in frames at 30 fps.
- Canvas: 16:9 base. 1080x1920: masthead stacked on two lines at the top (fit to the width), product in the middle, labels above and below it. 1080x1350: masthead one line, fit to the width, labels at the sides.
- Palette:
  - Masthead #9A6A68 (dusty rose, with a fine grain texture at low opacity)
  - Italic tagline and label titles #956E6E
  - Feature headline #5A4243
  - Small captions #8B7573
  - Flowing lines #FFFFFF at 60 to 80% opacity
  - Leader lines #5A4243 at 1 px, with a 6 px dot at the feature end
- Fonts (free on Google Fonts): masthead and tagline in a condensed high-contrast serif, default Instrument Serif (tagline in Instrument Serif Italic), fallback "Bodoni Moda", Didot, Georgia, serif. Feature headlines and labels in Montserrat Bold (700), uppercase. Captions in Montserrat Medium (500), uppercase, letter-spacing 0.3em.
- Sizes at 1080 wide: masthead cap height about 210 px (font about 300 px), fit to 84% of the width. Tagline about 60 px, with a 1 px rule about 150 px long on its left. Close-up feature headline 34 px on two lines, caption 12 px. End-card label titles 20 px, letter-spacing 0.2em, with 15 px captions under them.
- Layout: masthead centred at the top (about 35 px from the top edge) and behind the product through a subject mask. Tagline bottom right inside a 4% margin. Close-up headlines top left in a 5% margin, leader line from under the caption to the feature. End card: one label block left, one right, in negative space beside the product. Two bundles of 6 to 8 thin flowing lines sweep in from the left and right edges behind the product.
- Timing: masthead fades in over 9 frames starting about 9 frames after the cut. Flowing lines draw in over about 24 frames. Tagline wipes on left to right over about 18 frames, word by word. Close-up headlines: each line fades and rises 10 px over 6 frames, 4 frames apart, caption after, then the leader line draws over 10 frames. End card labels follow the same pattern about 0.3 s apart. An optional soft light glint with a few sparkles sweeps across the named feature in close-ups. Everything cuts with the shot.

### Build notes for this look
Use the supplied product image or clip. If a style reference is provided, match it; otherwise propose a static editorial design in code first. Rebuild the type in code. Fit the masthead with fitText/measureText from @remotion/layout-utils so it never overflows the frame. Use a subject mask only where text goes behind the product. Keep labels in negative space, and reset anchors at cuts. Label the actual features the user names, only when visible. Do not assume the product is footwear. Match the approved font and colour treatment.

## Look: Heads-up display

A soft, premium heads-up display over the supplied product image or video: dark mauve translucent label panels with a pink accent bar, readable feature labels, thin white leader lines ending in small crosshair targets, plus-sign registration marks and faint thin arcs around the product, and a light condensed title. It is HUD interface styling in the product's own colours, not a neon gaming look and not gameplay footage.

### Specs
Preview is 1280x720 (16:9), 24 fps, real speed. Sizes below are at 1080 px wide; multiply by 1.78 for 1920x1080. Timings are in frames at 30 fps.
- Canvas: 16:9 base. 1080x1920 and 1080x1350: same px sizes, title at the top, labels stacked above and below the product with longer leader lines, nothing in the bottom 20% of 9:16.
- Palette:
  - Panels #5D5257 at about 90% opacity, 3 px left accent bar #FC9DB4 on feature panels
  - Panel text #F7EEEF, panel caption #FC9DB4 (pink, letter-spaced)
  - Title: first word #FBF3EE, second word #A7747A
  - Subtitle #655757, its flanking rules 1 px #655757
  - Leader lines, targets, plus marks and arcs #FFFFFF at 70 to 90% opacity
- Fonts (free on Google Fonts): title and close-up headlines in a condensed sans. Default Oswald (title Light 300, headlines SemiBold 600). Labels and captions in Montserrat SemiBold (600), uppercase, letter-spacing 0.15 to 0.3em. Fallback: "Arial Narrow", Arial, sans-serif.
- Sizes at 1080 wide: title cap height about 68 px (font about 95 px), letter-spacing 0.15em. Subtitle 14 px, letter-spacing 0.4em, with 80 px rules either side. End-card label panels about 215x32 px with 12 px text. Close-up feature panel about 548x84 px, headline 36 px, caption 12 px. Leader lines 1 px. Targets 18 px circles with a centre dot and a crosshair. Plus marks 22 px. Arcs 1 px. No corner radius on panels.
- Layout: title centred at the top, about 30 px from the edge. Plus marks near the four corners, inset about 7%. Two big faint arcs hug the left and right of the product. Panels sit in negative space at the frame sides (inside a 1.5% edge margin), each with an elbow leader line to a target on the named feature. Close-ups: one panel, bottom right, leader to the feature.
- Timing: graphics start about 9 frames after each cut. Title fades in over 6 frames, subtitle and rules about 8 frames later, arcs and plus marks fade in over about 15 frames. Panels slide 16 px in from the outer edge and fade over 6 frames, about 10 frames apart; each leader line draws over 8 frames after its panel, then the target pops (4 frames). Close-up panel: headline first, caption 6 frames later. Everything cuts with the shot.

### Build notes for this look
Inspect every shot, create new time-stamped anchors for this footage and align callouts to visible features. Use a tracked plane only when perspective supports it. Hide graphics when their target is occluded. Build new anchor positions for each new input; never reuse coordinates from a different clip. Reveal panels progressively and make one main callout readable at a time. Fit the title and panel text with fitText/measureText from @remotion/layout-utils so nothing overflows its panel or the frame. Keep the product unobstructed. For still images use fixed anchors; for video reset tracking at cuts. Do not invent technical measurements or game statistics.

## Look: Hand-drawn doodle

Rough charcoal brush lettering for the product name and tagline, feature notes in white handwriting on torn charcoal tape labels, thin white hand-drawn arrows, rose underline strokes and small rose stars that guide attention to the product. Everything boils slightly like hand animation.

### Specs
Preview is 1280x720 (16:9), 24 fps, real speed. Sizes below are at 1080 px wide; multiply by 1.78 for 1920x1080. Timings are in frames at 30 fps.
- Canvas: 16:9 base. 1080x1920 and 1080x1350: keep the same px sizes, title across the top in two lines if needed, labels stacked left and right of the product, nothing in the bottom 20% of 9:16 (platform UI).
- Palette:
  - Brush lettering and label tape #302B2A
  - Label text and arrows #FCF8F5
  - Rose underlines and stars #C77986
  - No background changes, the doodles sit on the footage
- Fonts (all free on Google Fonts): title and signature in a rough brush marker, default Permanent Marker, fallback "Rock Salt", cursive. Label text in a casual handwriting, default Kalam Bold (700), fallback "Caveat Brush", cursive. Lowercase small words like "on" drop to about 40% size.
- Sizes at 1080 wide: title cap height about 100 px (font about 130 px). Signature ("CLOUD FLOW" style, bottom right) 32 px. Labels about 195x60 px rough rectangles with ragged edges, slightly rotated (-3 to +3 degrees), text 27 px. Arrows 2.5 px stroke with a small open arrowhead. Rose underlines 4 px, a little tapered. Stars about 34 px, 2 px rose outline.
- Layout: title top centre about 40 px from the top, signature bottom right inside a 5% margin. Labels in the empty space at the left and right of the product, with the arrow tip ending just short of the named feature. Keep the product itself clear.
- Timing: graphics start about 9 frames after each cut. Title fades in word by word, 3 frames apart, each a 4 frame fade (about 14 frames for the whole title). Underline draws 6 frames, starting about 12 frames after the title. Arrows draw on over 12 to 15 frames. Labels pop in over 5 frames (scale 0.8 to 1, spring {damping: 12, stiffness: 160, mass: 0.7}), their arrow starts 6 frames later. Stars pop in last. Boil: change the seeded wobble every 4 frames (about 8 per second). Everything cuts away with the shot.

### Build notes for this look
Use the supplied image or clip. Match a supplied reference or propose a hand-drawn design in code first. Build editable handwriting-style text, SVG arrows and stars. Fit the title with fitText/measureText from @remotion/layout-utils so it never overflows the frame. Use seeded stepped line variations, about eight per second as a starting point, for a doodle-boil feel. Anchor decorations to visible features, keep the main subject unobstructed and reset at cuts in video; use fixed anchors for a still image.
