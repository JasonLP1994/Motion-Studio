// Accurate word timings for a whole clip, without cutting anything.
// Splits the audio at natural pauses, transcribes each piece with local Whisper
// (short pieces time much better than one long file), and maps times back to the source.
// Usage: node scripts/transcribe-chunks.mjs <audio.wav> <out.json> [start] [end]
import { execFileSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import { transcribe } from "@remotion/install-whisper-cpp";

const [audio, outPath, startS = "0", endS = "1e9"] = process.argv.slice(2);
const START = Number(startS), END = Number(endS);
const log = execFileSync("sh", ["-c", `npx remotion ffmpeg -v info -i "$0" -af silencedetect=noise=-45dB:d=0.25 -f null - 2>&1`, audio], { encoding: "utf8" });
const sil = []; let s0 = null;
for (const l of log.split("\n")) {
  const a = l.match(/silence_start: ([\d.]+)/); if (a) s0 = Number(a[1]);
  const b = l.match(/silence_end: ([\d.]+)/); if (b && s0 !== null) { sil.push([s0, Number(b[1])]); s0 = null; }
}
const dur = Number(execFileSync("npx", ["remotion", "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio], { encoding: "utf8" }).trim());
const end = Math.min(END, dur);
// Speech islands between silences; merge islands closer than 0.15 s.
const chunks = []; let cur = START;
for (const [a, b] of sil) {
  if (b <= START || a >= end) continue;
  const mid = (a + b) / 2;
  if (mid - cur > 0.4) chunks.push([cur, mid]);
  cur = mid;
}
if (end - cur > 0.3) chunks.push([cur, end]);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "tc-"));
const words = [];
const junk = (t) => !t || /^\[|^\(|^_|^<|^[-–—]+$|^[.,?!"\])]+$/.test(t) || ["BL", "ANK", "AUD", "IO"].includes(t);
for (const [i, [a, b]] of chunks.entries()) {
  const wav = path.join(tmp, `c${i}.wav`);
  execFileSync("npx", ["remotion", "ffmpeg", "-y", "-v", "error", "-ss", String(a), "-t", String(b - a), "-i", audio, "-af", "apad=pad_dur=0.6", "-ar", "16000", "-ac", "1", wav]);
  const { transcription } = await transcribe({ inputPath: wav, whisperPath: path.resolve("whisper.cpp"), whisperCppVersion: "1.5.5",
    model: "base.en", tokenLevelTimestamps: true, printOutput: false, splitOnWord: true });
  for (const seg of transcription) for (const tk of seg.tokens) {
    const txt = tk.text.trim();
    if (junk(txt)) continue;
    const st = tk.offsets.from / 1000, en = tk.offsets.to / 1000;
    if (st > b - a) continue;
    const last = words[words.length - 1];
    if (last && last.chunk === i && (/^['’]/.test(txt) || !tk.text.startsWith(" "))) { last.text += txt; last.end = +(a + en).toFixed(3); continue; }
    words.push({ text: txt, chunk: i, start: +(a + st).toFixed(3), end: +(a + Math.min(en, b - a)).toFixed(3) });
  }
}
fs.rmSync(tmp, { recursive: true, force: true });
fs.writeFileSync(outPath, JSON.stringify({ source: audio, chunks, words }, null, 1));
console.log(`chunks: ${chunks.length}, words: ${words.length}`);
let line = "";
for (const w of words) { line += `${w.text}@${w.start.toFixed(2)} `; if (/[.?!]$/.test(w.text)) { console.log(line); line = ""; } }
if (line) console.log(line);
