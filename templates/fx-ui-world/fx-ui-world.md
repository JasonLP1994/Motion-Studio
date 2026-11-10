# UI world

Style ID: fx-ui-world
Best for: A prompt demonstration

## Look
On a light grey page, the full-frame footage shrinks into a rounded 9:16 card in the lower part of the frame while a white prompt box sits above it. Once the card settles, the prompt types in with a blinking cursor. A purple round send button sits in the box corner.

## Specs
Preview is 540x960 (9:16) shown at 0.6x speed; numbers below are real speed at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: prompt box same width, video card shrinks to fit the remaining height (keep its aspect ratio). 1920x1080: prompt box 900 px wide centred at the top, card below it at 16:9 or 9:16 (match the footage), or box left and card right.
- Palette:
  - Page #E2E0DC with a soft vignette to #D2D1CF at the corners
  - Prompt box #F4F6F6, 2 px border #DCDCDC
  - Prompt text #1F1F22
  - Send button #6B50A3 with a white arrow #FFFFFF
  - Card shadow rgba(0,0,0,0.12)
- Fonts: prompt in a clean UI sans, semibold. Default Inter SemiBold (600) from Google Fonts. Fallback: system-ui, -apple-system, "Segoe UI", sans-serif.
- Sizes at 1080 wide: prompt box 900x190 px, radius 24 px, text 38 px with 36 px padding, cursor 3 px wide. Send button 60 px circle, 32 px in from the bottom right corner. Video card 734x1306 px, radius 32 px. Soft shadows 0 8px 24px.
- Layout: prompt box x 90 to 990, y 330 to 520. Video card centred, x 172 to 906, top at y 574 (54 px gap under the box), bottom 40 px from the frame edge.
- Timing: frame 0 shows the box over the full-frame footage. Footage shrinks into the card over 9 frames (Easing.out(Easing.cubic), no overshoot), corners rounding as it goes. Typing starts on frame 9 at about 1 character per frame (roughly 29 per second). Cursor blinks about twice a second while idle and is hidden once typing ends. The send button stays static in the preview. Hold.

## Build recipe
Use a coded prompt card, editable string, cursor and send state. Scale the entire clip into a card without changing its internal proportions. Shrink the footage into the card first, then type the key sentence over it (that is the order in the preview). Coordinate the transition with supplied narration or the agreed visual beat plan. A supplied still image can replace the video card.

## Check
Use a generic UI unless accurate app footage is provided. Keep prompt text readable. Fit the prompt with fitText/measureText from @remotion/layout-utils so it wraps inside the box and never overflows. Do not imply a simulated UI is a recording of the real app.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
