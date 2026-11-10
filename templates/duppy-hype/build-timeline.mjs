// Builds src/duppy/timeline.json: which parts of the source video to keep (pauses shortened)
// and every spoken word re-timed to the edited video.
// Usage: node scripts/build-timeline.mjs <audio.wav> <cutStart> <cutEnd>
import { execFileSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import { transcribe } from "@remotion/install-whisper-cpp";

const [audio, cutStartS, cutEndS] = process.argv.slice(2);
const CUT_START = Number(cutStartS), CUT_END = Number(cutEndS);
const MAX_PAUSE = 0.45; // pauses longer than this get shortened
const PAD = 0.12; // seconds of breath kept on each side of a shortened pause

// 1. Find silences with Remotion's FFmpeg.
const out = execFileSync("sh", ["-c", `npx remotion ffmpeg -v info -i "$0" -af silencedetect=noise=-45dB:d=0.12 -f null - 2>&1`, audio], { encoding: "utf8" });
const silences = [];
let s0 = null;
for (const line of out.split("\n")) {
  const a = line.match(/silence_start: ([\d.]+)/); if (a) s0 = Number(a[1]);
  const b = line.match(/silence_end: ([\d.]+)/); if (b && s0 !== null) { silences.push([s0, Number(b[1])]); s0 = null; }
}

// 2. Keep segments: the cut range minus the middle of every long pause.
const segments = [];
let cursor = CUT_START;
for (const [a, b] of silences) {
  if (b <= CUT_START || a >= CUT_END) continue;
  if (b - a <= MAX_PAUSE) continue;
  const cutFrom = Math.max(a + PAD, CUT_START), cutTo = Math.min(b - PAD, CUT_END);
  if (cutTo - cutFrom <= 0.05) continue;
  if (cutFrom > cursor) segments.push([cursor, cutFrom]);
  cursor = Math.max(cursor, cutTo);
}
if (cursor < CUT_END) segments.push([cursor, CUT_END]);
let t = 0;
const segs = segments.map(([from, to]) => { const s = { from: +from.toFixed(3), to: +to.toFixed(3), outStart: +t.toFixed(3) }; t += to - from; return s; });
const duration = +t.toFixed(3);

// 3. Words: transcribe each kept piece on its own (short clips time much better than one long file).
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "tl-"));
const outWords = [];
for (const [i, s] of segs.entries()) {
  const wav = path.join(tmp, `seg${i}.wav`);
  execFileSync("npx", ["remotion", "ffmpeg", "-y", "-v", "error", "-ss", String(s.from), "-t", String(s.to - s.from), "-i", audio, "-af", "apad=pad_dur=0.6", "-ar", "16000", "-ac", "1", wav]);
  const { transcription } = await transcribe({ inputPath: wav, whisperPath: path.resolve("whisper.cpp"), whisperCppVersion: "1.5.5",
    model: "base.en", tokenLevelTimestamps: true, printOutput: false, splitOnWord: true });
  for (const seg of transcription) for (const tk of seg.tokens) {
    const txt = tk.text.trim();
    if (!txt || /^\[|^\(|^_|^<|^[-–—]+$|^[.,?!"\]\)]+$/.test(txt) || txt === "BL" || txt === "ANK" || txt === "AUD" || txt === "IO") continue;
    const st = tk.offsets.from / 1000, en = tk.offsets.to / 1000;
    if (st > s.to - s.from) continue;
    const last = outWords[outWords.length - 1];
    if (last && (/^['’]/.test(txt) || (!tk.text.startsWith(" ") && last.seg === i))) { last.text += txt; last.end = +(s.outStart + en).toFixed(3); continue; }
    outWords.push({ text: txt.replace(/^"|"$/g, ""), seg: i, start: +(s.outStart + st).toFixed(3), end: +(s.outStart + Math.min(en, s.to - s.from)).toFixed(3) });
  }
}
fs.rmSync(tmp, { recursive: true, force: true });
fs.writeFileSync("src/duppy/timeline.json", JSON.stringify({ duration, segments: segs, words: outWords }, null, 1));
console.log(`segments: ${segs.length}, duration: ${duration}s (from ${(CUT_END - CUT_START).toFixed(2)}s), words: ${outWords.length}`);
console.log(outWords.map((w, i) => `${i}:${w.text}@${w.start.toFixed(2)}`).join(" "));
