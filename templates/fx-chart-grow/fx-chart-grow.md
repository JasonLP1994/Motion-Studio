# Chart grow

Style ID: fx-chart-grow
Best for: A result, trend or comparison

## Look
A glowing yellow line draws across the empty space above the head, white dots pop on at each data point, and the final value pops in as a yellow label above the last point. No axes or grid in the preview, just the line.

## Specs
Preview is 540x960 (9:16) shown at 0.6x speed; numbers below are real speed at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: same sizes, chart sits in the band between the top margin and the head, a bit flatter (rise about 70% of the 9:16 version). 1920x1080: scale sizes by 0.75 and put the chart in the third beside the head, not over it.
- Palette:
  - Line core #FFF09A, with an outer glow #E5C407 (drop-shadow 0 0 10px at about 70% opacity)
  - Point dots: fill #FBFCEF, ring #E5C407
  - Result label: fill #E5C407 (close to brand yellow #F4D00A, use either), text #1A0F00
  - Label shadow: rgba(0,0,0,0.35)
- Fonts: label in a heavy rounded sans. Default Nunito Black (900) from Google Fonts, or Gilroy ExtraBold if you own it. Fallback: "Nunito", "Arial Rounded MT Bold", system-ui, sans-serif.
- Sizes at 1080 wide: line core 8 px plus glow, point dots 18 px across with a 4 px ring, label about 272x68 px, label text 40 px, label corner radius 12 px (a rounded rectangle, not a full pill), label shadow 0 6px 12px. Label tilted about -2 degrees.
- Layout: chart spans x 110 to 960 (10% side margins). Six points evenly spaced (about 170 px apart). The lowest points sit just above the top of the head (first point around y 860, last around y 380), so the line climbs away from the face. Label sits about 44 px above the last point, right edge lined up with it.
- Timing: line draws over 27 frames (strokeDashoffset, Easing.out(Easing.quad)). Each dot pops as the line reaches it (4 frames, scale 0 to 1, spring {damping: 12, stiffness: 200, mass: 0.6}). Label pops from scale 0.2 to 1 over 6 frames starting on frame 27 with the same spring (a little overshoot). Then hold. Exit is not shown in the preview: use an 8 frame fade with Easing.in(Easing.cubic).

## Build recipe
Ask for the user's data, labels and units, then store them as an array in config. If none are supplied, ask or use clearly marked illustrative values with the user's agreement. Map points to the chosen axis scale. Reveal an SVG line with dash offset and add point markers when reached. Animate the final result separately, leaving time to read it. Fit the label text with fitText/measureText from @remotion/layout-utils so it never overflows the frame.

## Check
Label illustrative data as a demo. Avoid inventing performance claims. Keep labels clear of the speaker; explain axis scale when it matters.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
