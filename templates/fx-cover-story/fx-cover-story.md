# Cover story

Style ID: fx-cover-story
Best for: A moving carousel or editorial reveal

## Look
A huge off-white serif masthead across the middle of the frame, sitting behind the person's head, with a small issue line above it, a yellow sans cover line plus a white italic serif line at the left, and a small barcode at the right. Works on talking-head video as well as stills.

## Specs
Preview is 540x960 (9:16) shown at 0.6x speed; numbers below are real speed at 1080x1920, 30 fps. Ignore the washed-out last 1.2 s of the preview (end hold).
- Canvas: 1080x1920 base. 1080x1350: same type sizes, masthead just above the eyebrows. 1920x1080: masthead 70% of frame width, centred behind the head; cover lines and barcode move in to the sides of the head.
- Palette:
  - Masthead and issue line #FBF1F0 (off-white)
  - Cover line #E0C815 (or brand yellow #F4D00A)
  - Italic line and barcode #FFF6FA
  - No panels or backgrounds behind the type
- Fonts: masthead in a high-contrast Didone serif, default Playfair Display Bold (700) from Google Fonts, fallback "Bodoni Moda", Didot, Georgia, serif. Issue line and yellow cover line in Montserrat Bold (700), issue line uppercase. Italic line in Playfair Display Italic (400). Fallback sans: Arial, sans-serif.
- Sizes at 1080 wide: masthead cap height about 204 px (font about 290 px), fit to 986 px wide with fitText. Issue line 28 px, letter-spacing 0.02em. Cover line 48 px. Italic line 52 px. Barcode about 144x80 px of 2 to 4 px bars.
- Layout: masthead spans x 52 to 1038, top at y 728 (about 38% down), so the head covers the middle letters. Issue line baseline 120 px above the masthead, left text at x 84, date right-aligned to x 956. Cover lines left at x 40, starting 60 px below the masthead. Barcode right at x 856 to 1000, level with the cover lines. Keep cover lines over hair or background, never across the eyes.
- Layer order: background video, masthead, subject cut-out (mask), then issue line, cover lines and barcode on top.
- Timing: masthead fades in and rises 8 px over 6 frames from frame 2. Issue line fades in on frames 11 to 14, yellow cover line frame 19, italic line frame 23, barcode frame 25 (each a 3 to 4 frame fade, Easing.out(Easing.cubic)). Hold. Exit not shown: 8 frame fade.

## Build recipe
Use the supplied image and any available subject layer. No cut-out? Follow the Subject mask fallback in SKILL.md (masthead above the head), and never pretend a flat photo already has layers. Stack background, coded masthead, subject, then small cover lines. Animate the headline entrance and a restrained subject reveal separately. Use a high-contrast serif for the masthead, paired with a clean sans-serif for small copy. Fit the masthead with fitText/measureText from @remotion/layout-utils so it never overflows the frame.

## Check
Check hair and hand edges. Match the chosen style frame and use a free or licensed font. Do not put rasterised headline letters back into the image; keep them editable.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
