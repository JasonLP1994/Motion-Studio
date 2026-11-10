// Usage: node transcribe.mjs <16kHz mono wav> [output.json]
import path from "path";
import fs from "fs";
import { transcribe, toCaptions } from "@remotion/install-whisper-cpp";

const input = process.argv[2];
if (!input) throw new Error("Usage: node transcribe.mjs <16kHz mono wav> [output.json]");
const whisperCppOutput = await transcribe({
  inputPath: path.resolve(input),
  whisperPath: path.join(process.cwd(), "whisper.cpp"),
  whisperCppVersion: "1.5.5",
  model: "base.en",
  tokenLevelTimestamps: true,
  printOutput: false,
});
const { captions } = toCaptions({ whisperCppOutput });
for (const c of captions) {
  console.log(`${(c.startMs / 1000).toFixed(2)}s - ${(c.endMs / 1000).toFixed(2)}s  ${c.text.trim()}`);
}
if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(captions, null, 2));
