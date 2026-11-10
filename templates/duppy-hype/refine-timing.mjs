// Finds where each word really starts in an edited video's audio, then saves it to timeline.json.
// For each word: trim the audio at time t and ask Whisper what the clip starts with.
// Binary-search the earliest t where the clip starts on this word (or a later one).
// Usage: node scripts/refine-timing.mjs <edited-audio.wav> [timeline.json]
import { execFileSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import { transcribe } from "@remotion/install-whisper-cpp";

const [audio, tlPath = "src/duppy/timeline.json"] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "rt-"));
const norm = (s) => s.toLowerCase().replace(/[^a-z']/g, "").replace(/'/g, "");
const cache = new Map();

const firstWords = async (t) => {
  const key = t.toFixed(3);
  if (cache.has(key)) return cache.get(key);
  const wav = path.join(tmp, "w.wav");
  execFileSync("npx", ["remotion", "ffmpeg", "-y", "-v", "error", "-ss", key, "-t", "1.3", "-i", audio,
    "-af", "adelay=300,apad=pad_dur=0.8", "-ar", "16000", "-ac", "1", wav]);
  const { transcription } = await transcribe({ inputPath: wav, whisperPath: path.resolve("whisper.cpp"), whisperCppVersion: "1.5.5",
    model: "base.en", tokenLevelTimestamps: true, printOutput: false, splitOnWord: true });
  const words = [];
  for (const seg of transcription) for (const tk of seg.tokens) {
    const x = norm(tk.text);
    if (!x || /^\[|^\(/.test(tk.text.trim())) continue;
    if (words.length && !tk.text.startsWith(" ")) words[words.length - 1] += x; else words.push(x);
  }
  cache.set(key, words);
  return words;
};

// Does a clip starting at t begin on word i or later?
const W = tl.words.map((w) => norm(w.text));
const startsAtOrAfter = async (t, i) => {
  const got = await firstWords(t);
  if (!got.length) return true; // silence/nothing left: we're past the word's onset
  const a = got[0], b = got[1];
  // Matches word i, i+1, i+2 -> at or after. Matches i-1 or i-2 -> before.
  for (const k of [i, i + 1, i + 2]) if (W[k] && (a === W[k] || a.startsWith(W[k]) && W[k].length > 2)) return true;
  for (const k of [i - 1, i - 2]) if (W[k] && a === W[k]) return false;
  // A fragment of the previous word, followed by this word -> still before.
  if (b && b === W[i]) return false;
  return true;
};

const fixed = [];
let prev = 0;
for (let i = 0; i < tl.words.length; i++) {
  const est = tl.words[i].start;
  let lo = Math.max(prev + 0.04, est - 0.25), hi = Math.min(tl.duration - 0.05, est + 1.0);
  if (i === 0 || !(await startsAtOrAfter(hi, i)) || (await startsAtOrAfter(lo, i) && i > 0 && lo > est)) {
    fixed.push(est); prev = est; continue;
  }
  if (await startsAtOrAfter(lo, i)) { fixed.push(Math.max(lo, est)); prev = fixed[i]; continue; }
  for (let k = 0; k < 6; k++) { const mid = (lo + hi) / 2; if (await startsAtOrAfter(mid, i)) hi = mid; else lo = mid; }
  const onset = Math.max(hi - 0.03, prev + 0.04); // a few hundredths back: the clip can start just after the attack
  fixed.push(onset);
  prev = onset;
  process.stdout.write(`${tl.words[i].text}: ${est.toFixed(2)} -> ${onset.toFixed(2)}  `);
}
fs.rmSync(tmp, { recursive: true, force: true });
tl.words.forEach((w, i) => { w.estimate = w.estimate ?? w.start; w.start = +fixed[i].toFixed(3); });
for (let i = 0; i < tl.words.length; i++) { const n = tl.words[i + 1]; if (n && tl.words[i].end > n.start) tl.words[i].end = n.start; if (tl.words[i].end <= tl.words[i].start) tl.words[i].end = +(tl.words[i].start + 0.15).toFixed(3); }
fs.writeFileSync(tlPath, JSON.stringify(tl, null, 1));
console.log("\nsaved", tlPath);
