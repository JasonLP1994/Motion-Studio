# Checklist

Style ID: fx-checklist
Best for: Steps and short instructions

## Look
A compact dark card in the empty space above the head, with a small grey "MIA MEOW · EDIT RUN" header and short medium-size task rows. Each row starts dimmed with a grey circle, then snaps to a teal tick and white text, one at a time.

## Specs
Preview is 540x960 (9:16) shown at 0.6x speed; numbers below are real speed at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: same card size, top edge about 200 px from the top. 1920x1080: same px sizes, card in the clear third beside the head.
- Palette:
  - Card #15121A, 2 px rim #3A3346, hard shadow below rgba(0,0,0,0.45)
  - Header text #75707A
  - Pending row: circle #393240, text #B2ACB9
  - Done row: circle #0AB5B7, check mark #15121A, text #FFFFFF
- Fonts: rows in a clean geometric sans, semibold. Default Inter SemiBold (600) from Google Fonts. Header in Montserrat Bold (700), uppercase, letter-spacing 0.04em. Fallback: system-ui, "Segoe UI", Arial, sans-serif.
- Sizes at 1080 wide: card 756 px wide (sized to the longest row plus padding), 36 px side padding, 28 px top padding. Header 24 px. Row text 44 px, row pitch 90 px. Circles 52 px across, 28 px gap to the text. Corner radius 24 px. Shadow 0 8px 0 (hard) plus 0 12px 24px soft.
- Layout: card centred horizontally (162 px margins), top edge at y 334, bottom edge clear of the hair by at least 40 px. Never cover the face.
- Timing: card fades in and rises 8 px over 6 frames (spring {damping: 14, stiffness: 140, mass: 0.8}). Ticks land on frames 13, 22 and 32 (about 9 frames apart, or on the spoken step). Each tick snaps in 2 frames (scale 0.6 to 1) and the row text goes from grey to white on the same frame. Hold to the end. Exit is not shown in the preview: fade out over 8 frames with Easing.in(Easing.cubic).

## Build recipe
Use a separate row component for each step. Keep row text editable. Reveal a check mark only as the relevant step is spoken or completed. Place the card in clear space above or beside the subject, or on a standalone background when no person is supplied; adapt to the footage instead of cropping the person to fit it.

## Check
Make the card fit the longest line: measure rows with measureText from @remotion/layout-utils. Keep rows short (about 3 words). Leave enough reading time per row. Keep hands and face visible.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
