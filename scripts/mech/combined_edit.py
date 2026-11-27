"""Samurai intro combined edit: v2 (sheathed standoff) + v3 (draw + drawn hero) cut into one sequence.
Picture only (silent); the soundtrack is built separately to the output frame numbers.
  python scripts/mech/combined_edit.py <out_silent.mp4>
Segments are (source, first frame, last frame), 1-based and inclusive, in source-video frame numbers.
"""
import subprocess, sys, os

SRC = {"v2": "renders/samurai-intro-v2.mp4", "v3": "renders/samurai-intro-v3.mp4"}
SEGMENTS = [
    ("v3", 1, 263),      # shared intro
    ("v2", 290, 336),    # standoff: sword still sheathed (after v2's light bang)
    ("v3", 264, 400),    # the draw: hand, slide, cut, snap, helmet + start of the flicker-out
    ("v2", 337, 337),    # flicker glimpse of the sheathed stance
    ("v3", 402, 404),
    ("v2", 338, 338),    # glimpse
    ("v3", 406, 408),
    ("v2", 339, 339),    # glimpse
    ("v3", 410, 584),    # bang on: drawn hero + end card
]
CRF = 16

out = sys.argv[1]
if os.path.exists(out): sys.exit(f"refusing to overwrite {out}")
parts, n = [], 0
for i, (s, a, b) in enumerate(SEGMENTS):
    idx = 0 if s == "v2" else 1
    parts.append(f"[{idx}:v]trim=start_frame={a - 1}:end_frame={b},setpts=PTS-STARTPTS[s{i}]"); n += b - a + 1
fc = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(len(SEGMENTS))) + f"concat=n={len(SEGMENTS)}:v=1:a=0,settb=1/30,setpts=N[v]"
subprocess.run(["ffmpeg", "-v", "error", "-i", SRC["v2"], "-i", SRC["v3"], "-filter_complex", fc, "-map", "[v]",
                "-c:v", "libx264", "-crf", str(CRF), "-preset", "slow", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough", "-video_track_timescale", "15360", out], check=True)
print(f"saved {out}: {n} frames ({n / 30:.2f} s)")
# frame map for the sound pass
pos = 1
for s, a, b in SEGMENTS:
    print(f"  out {pos:4d}-{pos + b - a:4d}  <- {s} {a}-{b}"); pos += b - a + 1
