#!/usr/bin/env bash
# Optional offline gaze correction using Powderhond/teleprompter.
# No automatic downloads, installs, overwrites or media uploads.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
UPSTREAM="${MOTION_EYE_TOOL_PATH:-$ROOT/tools/teleprompter}"
PASS="$UPSTREAM/skills/teleprompter/scripts/gaze-pass.mjs"
MODEL="$UPSTREAM/skills/teleprompter/scripts/vendor/models/face_landmarker.task"
INPUT=""
OUTPUT=""
STRENGTH="0.4"
MODE="run"

usage() {
  cat <<'HELP'
Motion Studio eye-contact correction (experimental on macOS/A18 Pro)
Usage:
  bash .claude/skills/eye-contact-correction/scripts/run.sh --check
  bash .claude/skills/eye-contact-correction/scripts/run.sh --in INPUT.mp4 [--out OUTPUT.mp4] [--strength 0.4]

Reads footage unchanged. Exports an independent MP4 to ignored renders/ by default.
First test with a 10-15 second clip. Nothing is uploaded or installed automatically.
Prerequisite upstream checkout: tools/teleprompter (override via MOTION_EYE_TOOL_PATH).
HELP
}

check_dependencies() {
  local missing=0
  for cmd in node ffmpeg ffprobe; do
    if command -v "$cmd" >/dev/null 2>&1; then
      printf 'OK: %s\n' "$cmd"
    else
      printf 'MISSING: %s\n' "$cmd"
      missing=1
    fi
  done
  if [[ -f "$PASS" ]]; then
    printf 'OK: upstream gaze pass at %s\n' "$PASS"
  else
    printf 'MISSING: upstream gaze pass at %s\n' "$PASS"
    missing=1
  fi
  if [[ -f "$UPSTREAM/node_modules/playwright/package.json" ]]; then
    printf 'OK: local Playwright dependency\n'
  else
    printf 'MISSING: Playwright in upstream checkout\n'
    missing=1
  fi
  if [[ -f "$MODEL" ]]; then
    printf 'OK: local MediaPipe face model\n'
  else
    printf 'MISSING: local MediaPipe face model\n'
    missing=1
  fi
  if [[ "$missing" -ne 0 ]]; then
    printf '\nReview SKILL.md and ask permission before installing/downloading anything.\n' >&2
    return 1
  fi
  printf '\nPrerequisite files present. Chromium and actual Mac compatibility must still be tested.\n'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE="check"; shift ;;
    --in) [[ $# -ge 2 ]] || { echo 'Missing --in value' >&2; exit 2; }; INPUT="$2"; shift 2 ;;
    --out) [[ $# -ge 2 ]] || { echo 'Missing --out value' >&2; exit 2; }; OUTPUT="$2"; shift 2 ;;
    --strength) [[ $# -ge 2 ]] || { echo 'Missing --strength value' >&2; exit 2; }; STRENGTH="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$MODE" == "check" ]]; then
  check_dependencies
  exit $?
fi
[[ -n "$INPUT" ]] || { echo 'Missing --in INPUT' >&2; usage >&2; exit 2; }
[[ -f "$INPUT" ]] || { printf 'Input file not found: %s\n' "$INPUT" >&2; exit 2; }
command -v node >/dev/null 2>&1 || { echo 'Node.js is required' >&2; exit 2; }
node -e 'let x=Number(process.argv[1]); if (!Number.isFinite(x)||x<0||x>1) process.exit(1)' "$STRENGTH" || { echo '--strength must be between 0 and 1' >&2; exit 2; }
if [[ -z "$OUTPUT" ]]; then
  name="$(basename "$INPUT")"
  name="${name%.*}"
  OUTPUT="$ROOT/renders/${name}-gaze-v1.mp4"
fi
[[ "$INPUT" != "$OUTPUT" ]] || { echo 'Output must differ from input' >&2; exit 2; }
[[ ! -e "$OUTPUT" ]] || { printf 'Refusing to overwrite existing file: %s\n' "$OUTPUT" >&2; exit 2; }

check_dependencies
mkdir -p "$(dirname "$OUTPUT")"
printf '\nCorrecting a local copy with strength %s. The original remains unchanged.\n' "$STRENGTH"
node "$PASS" --in "$INPUT" --out "$OUTPUT" --strength "$STRENGTH"
[[ -s "$OUTPUT" ]] || { echo 'The gaze pass did not produce a nonempty output' >&2; exit 1; }
printf '\nCreated: %s\nReview normal playback, eyes, blinks, duration, and audio sync before accepting.\n' "$OUTPUT"
