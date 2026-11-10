import { execFileSync } from "child_process";
import path from "path";
import fs from "fs";
import { transcribe } from "@remotion/install-whisper-cpp";
const audio = process.argv[2];
const tl = JSON.parse(fs.readFileSync(process.argv[3], "utf8")).words;
const idx = process.argv[4].split(",").map(Number);
const wav = "/tmp/claude-0/-home-user/40291a47-56b9-5b5a-8f67-497a5ea6f4b7/scratchpad/v.wav";
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
const heard = async (t) => {
  execFileSync("npx", ["remotion", "ffmpeg", "-y", "-v", "error", "-ss", t.toFixed(3), "-t", "1.1", "-i", audio, "-af", "adelay=300,apad=pad_dur=0.8", "-ar", "16000", "-ac", "1", wav]);
  const { transcription } = await transcribe({ inputPath: wav, whisperPath: path.resolve("whisper.cpp"), whisperCppVersion: "1.5.5", model: "base.en", tokenLevelTimestamps: true, printOutput: false, splitOnWord: true });
  return transcription.map((s) => s.text).join(" ").trim().split(/\s+/).slice(0, 4).join(" ");
};
for (const i of idx) {
  const w = tl[i];
  const OFF = Number(process.env.OFF ?? 0.2);
  const at = await heard(w.start), before = await heard(w.start - OFF);
  const first = norm(at.split(" ")[0] || "");
  const ok = first && (norm(w.text).startsWith(first) || first.startsWith(norm(w.text).slice(0, 3)));
  console.log(`${String(i).padStart(3)} ${w.text.padEnd(12)} @${w.start.toFixed(2)}  from here: "${at}"  | ${OFF}s earlier: "${before}"  ${ok ? "OK" : "CHECK"}`);
}
