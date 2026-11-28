# Pop Out lyric video (personal, non-commercial)
- Song: Polo G ft. Lil Tjay "Pop Out" (user's mp3, local only). Section: first chorus, song 21.405-47.45 s + 4 s card (intro bar spliced in, no vocals) = 30.0 s.
- Format: 16:9, 1920x1080, 30 fps. Sound: the song, levelled to -14 LUFS (TP -1.5).
- Words: user's exact chorus text; n-word censored ("N****"); "plan" -> "PLANE" (user correction). Word times from local Whisper.
- Look: user art direction = poster-collage example (grammar: halftone cut-outs on flat discs/arcs/stripes, condensed type built
  letter by letter with a blurred ghost, fast panel moves) + palette/vibe from the user's cover reference (navy night, icy blue,
  chrome silver, white, dusty scratches, glowing halo arc, cut-out objects: diamond, dove, chrome). User: "do yours".
- Photos: user's 8 photos -> BiRefNet-lite cut-outs (MIT, ONNX, local; SAM 2 blocked: pytorch.org not reachable) -> cold duotone halftone.
- Lyric imagery: party confetti/sparkles, ice diamond + chain + "ROBBERY" tape, chrome heart cracking on "can't change" + dove,
  crosshair locking on "hits", newspaper "FROM POVERTY" + flying bills, classified file/redaction bars, BANG! burst + shake, plane on a
  dashed route + boarding pass (FROM: POVERTY TO: THE TOP).
- End: "POP OUT" chrome title card, then the real Phillips Digital logo (public/pd01/logo_circle.png + logo_wordmark_full.png, unchanged).
- Skill stack: motion-art-direction (one look from the two refs), kinetic-typography (letter build + ghost, sung-word pops),
  beat-sync-editing (84 BPM, one line per bar, beat-3 punch, cuts on line starts), shot-composition (16:9 person/open-side split),
  remotion-transitions (iris / wipe / split / rise per line), logo-animation (real logo end card), color-motion (duotone + chrome), finishing pass.
- Code: src/popout/{config.ts,Popout.tsx}; scripts/popout/{cutout.py,prep.py,build.sh}. Output: renders/popout-lyric-v1.mp4 (local only).
