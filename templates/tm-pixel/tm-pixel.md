# Pixel celebration

Style ID: tm-pixel
Best for: An unlock, milestone or playful result

## Look
A side-scrolling pixel world (sky, clouds, purple hills, teal grass, purple brick ground). A small white pixel cat runs while the world scrolls past, collecting floating coins; a coin counter in the top-left box ticks up ("0/3" to "3/3"). On the last coin a purple banner drops into place, then an optional brand badge (the preview uses a teal pixel cat-logo) dissolves in with sparkles.

## Specs
Preview is 540x960 (9:16), 60 fps, real speed. Numbers below are at 1080x1920, 30 fps.
- Canvas: 1080x1920 base. 1080x1350: crop sky, keep ground at the bottom 30%, banner just under the counter. 1920x1080: same pixel scale, wider scroll, banner centred in the top half.
- Pixel grid: 1 logical pixel = 12 px at 1080 wide (a 90-pixel-wide world). Whole-pixel positions only, imageRendering: pixelated, no anti-aliasing.
- Palette (restricted):
  - Sky #7CC7F1, clouds and cat #F6F4F0
  - Hills and bricks #7B51B2 (brick mortar lines #F6F4F0 and #1A1418)
  - Grass, badge #00C2CA
  - Coins, banner second line, flash #F5D000
  - Outlines #1A1418, counter box #F6F4F2
- Fonts: chunky pixel font. Default Pixelify Sans Bold (700) from Google Fonts, fallback "Press Start 2P", "Silkscreen", monospace. Render text on the same pixel grid (whole-pixel sizes, no smoothing).
- Sizes at 1080 wide: counter box about 360x150 px with a 6 px outline, coin icon 60 px, counter text 64 px. Banner about 980x390 px, purple with a 6 px dark outline and yellow and teal corner pixels; "NEW STYLE" white 120 px, "UNLOCKED" yellow 120 px, both with a 12 px dark drop shadow. Cat about 240x180 px. Coins about 36x48 px. Badge about 580x300 px.
- Layout: counter top left at (76, 254). Banner centred, top at about y 410. Badge centred under the banner. Ground (grass line) at about y 1440, bricks below it. Cat runs in the left-centre third; the world scrolls right to left.
- Timing (30 fps): world scrolls at a constant speed. Run cycle steps between poses about every 4 frames, a jump pose for some coins. Pickups in the preview at about frames 66, 117 and 147: the coin flies up and sparkles on the pickup frame, the counter changes on that same frame, and the counter box border flashes yellow for about 6 frames. Banner drops from above the frame over 6 frames (frames 159 to 165) in whole-pixel steps with a one-step bounce. Badge dissolves in pixel by pixel over about 20 frames (frames 189 to 210) with a few sparkle pixels. Hold.

## Build recipe
Draw original sprites on a small logical grid and upscale with nearest-neighbour rendering. Use a restricted palette and whole-pixel positions. Step between run/jump poses; trigger each counter change on the actual pickup frame. Finish with a readable banner. Fit the banner text with fitText/measureText from @remotion/layout-utils (then snap to the pixel grid) so it never overflows the banner or the frame.

## Check
Do not use motion blur or fractional sprite scaling. Test that the character silhouette reads. Use a user-supplied character or an original code-drawn sprite. Only add a logo badge the user supplies or approves. Ask for the milestone and counter values rather than inventing a real achievement.

## Format and timing
Adapt the layout to the requested aspect ratio, not a stretched preset. Keep essential content inside the target platform's safe area. Use the real narration or supplied timestamps, and keep words, colours, fonts and timing in config.

## Copy prompt
See prompt.txt in this folder. Replace bracketed fields with your inputs; use NONE where an optional item does not apply.
