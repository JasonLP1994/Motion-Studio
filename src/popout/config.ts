// POP OUT lyric video (personal, non-commercial). Every word, colour, font and timing lives here.
// Song: inputs/pop-out/pop-out.mp3 -> public/popout/track.wav (song 21.405 s..47.45 s, then an intro bar for the title card).
// Photos: inputs/pop-out/photo_1..8.jpg -> BiRefNet cut-outs -> halftone B&W public/popout/p1..8.png (scripts/popout/prep.py).
// Grammar (not content) from the user's example: poster collage, halftone cut-outs on flat discs/arcs/stripes, condensed type that builds letter by letter with a ghost, 3-5 frame panel moves, paper grain.
// Lyrics: the user's exact text (n-word censored at their request; 'plan' -> 'PLANE' at the user's correction). Word times: local Whisper (notes/frames/pop-out/transcript.json).

// Palette from the user's cover reference (references/pop-out/palette-vibe.jpg): navy night, icy blue, chrome silver, white.
export const C = { night: "#04070E", navy: "#0A1730", deep: "#11284A", blue: "#3D6AA3", ice: "#A9CBEE", silver: "#DCE2EA", white: "#F5F8FC" };

export const SONG_T0 = 21.405; // song time at video frame 0
export const FPS = 30;
export const BEAT = 60 / 84; // 84 BPM; one sung line = one bar
export const f = (songSec: number) => Math.round((songSec - SONG_T0) * FPS);

export type Line = {
  words: [string, number][]; // [word, song seconds when sung]
  hero: string; // giant word behind the person, built letter by letter
  photo: number; // public/popout/p<photo>.png
  bg: keyof typeof C; // ground colour
  heroColor: keyof typeof C;
  graphic: "party" | "robbery" | "heart" | "target" | "news" | "redact" | "bang" | "plane";
  side: "left" | "right"; // where the person stands
  heroW?: number; personH?: number; // per-line overrides (wide group photos need a narrower hero)
  big: number[]; // indices of the words that go huge + chrome (the camera punches in on them)
};

export const lines: Line[] = [
  { words: [["WE", 24.49], ["POP", 24.62], ["OUT", 24.82], ["AT", 25.02], ["YOUR", 25.15], ["PARTY,", 25.44], ["I'M", 25.96], ["WITH", 26.38], ["THE", 26.96], ["GANG", 27.1]],
    hero: "GANG", photo: 8, bg: "navy", heroColor: "silver", graphic: "party", side: "right", heroW: 860, personH: 860 , big: [5, 9] },
  { words: [["AND", 27.44], ["IT'S", 27.64], ["GON'", 27.96], ["BE", 28.17], ["A", 28.3], ["ROBBERY,", 28.36], ["SO", 28.97], ["TUCK", 29.1], ["YA", 29.36], ["CHAIN", 29.63]],
    hero: "ROBBERY", photo: 6, bg: "night", heroColor: "ice", graphic: "robbery", side: "left" , big: [5, 9] },
  { words: [["I'M", 30.28], ["A", 30.49], ["KILLER,", 30.56], ["GIRL,", 31.0], ["I'M", 31.43], ["SORRY,", 31.64], ["BUT", 32.2], ["I", 32.4], ["CAN'T", 32.46], ["CHANGE", 32.75]],
    hero: "SORRY", photo: 1, bg: "deep", heroColor: "silver", graphic: "heart", side: "right" , big: [2, 5, 9] },
  { words: [["WE", 33.12], ["AIN'T", 33.26], ["AIMIN'", 33.61], ["FOR", 34.03], ["YOUR", 34.24], ["BODY,", 34.52], ["SHOTS", 34.94], ["HITS", 35.31], ["YOUR", 35.5], ["BRAIN", 35.78]],
    hero: "AIMIN'", photo: 3, bg: "night", heroColor: "ice", graphic: "target", side: "left" , big: [5, 9] },
  { words: [["WE", 36.4], ["COME", 36.5], ["FROM", 36.71], ["POVERTY,", 36.92], ["MAN,", 37.4], ["WE", 37.66], ["AIN'T", 37.76], ["HAVE", 38.02], ["A", 38.23], ["THING", 38.28]],
    hero: "POVERTY", photo: 4, bg: "ice", heroColor: "navy", graphic: "news", side: "right" , big: [3, 9] },
  { words: [["IT'S", 38.8], ["A", 39.17], ["LOT", 39.24], ["OF", 39.46], ["ANIMOSITY,", 39.6], ["BUT", 40.41], ["THEY", 40.63], ["WON'T", 40.92], ["SAY", 41.21], ["MY", 41.43], ["NAME", 41.57]],
    hero: "MY NAME", photo: 2, bg: "navy", heroColor: "silver", graphic: "redact", side: "left" , big: [4, 10] },
  { words: [["THEM", 42.16], ["KILLERS", 42.35], ["ROCK", 42.69], ["WITH", 42.88], ["ME,", 43.07], ["LIL'", 43.25], ["N****,", 43.44], ["DON'T", 43.77], ["GET", 43.99], ["BANGED", 44.13]],
    hero: "BANGED", photo: 7, bg: "deep", heroColor: "ice", graphic: "bang", side: "right" , big: [1, 9] },
  { words: [["'CAUSE", 44.68], ["THEY'LL", 45.05], ["DO", 45.36], ["THE", 45.48], ["JOB", 45.73], ["FOR", 45.92], ["ME", 46.11], ["WHILE", 46.23], ["I", 46.54], ["HOP", 46.6], ["ON", 46.79], ["A", 46.91], ["PLANE", 47.1]],
    hero: "PLANE", photo: 5, bg: "navy", heroColor: "silver", graphic: "plane", side: "left" , big: [4, 12] },
];

export const popoutConfig = {
  width: 1920, height: 1080, fps: FPS,
  durationInFrames: Math.round(30.045 * FPS), // = track.wav length (song 26.045 s + 4 s card)
  intro: { title: "POP OUT", credit: "POLO G  FT. LIL TJAY", from: 0 }, // first line starts at f(24.49)
  endCard: { at: f(47.45), title: "POP OUT", sub: "POLO G  FT. LIL TJAY", logoAt: 60, // frames after the card starts
    logoMark: "logo/pd_circle.png", logoWord: "logo/pd_wordmark.png" }, // the real Phillips Digital logo files, unchanged
  fonts: { hero: "Anton", line: "Montserrat", detail: "SpecialElite", italic: "BarlowBI" },
  sizes: { hero: 520, line: 64, detail: 22, word: 92, bigWord: 190 },
  camera: { whip: 520, wordZoom: 1.3, bigZoom: 1.6, heroZoom: 1.2, tilt: 2.5, move: 7, pullOut: 14, minGap: 5 },
  letterEvery: 2, // frames per letter in the hero build
  wordPop: 4, // frames for a sung word to land
  ghost: { dx: 34, opacity: 0.35, blur: 6 },
  transition: 5, // frames for a line-to-line panel move
  // small "poster" copy (grammar from the example: tiny info blocks); the user's song, no other brands
  detail: ["POP OUT", "VOL. 1", "84 BPM", "LYRIC VIDEO", "NO. 0", "SIDE A"],
};
