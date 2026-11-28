"""Survey a set of finished videos for an edit: 8 evenly spaced frames each, cut count, mean brightness and how
much lime/brand colour is on screen. Writes contact sheets (4 videos per sheet) and survey.json for planning.
  tools/ai-venv/bin/python scripts/showreel/survey.py <out_dir> <video> [<video> ...]
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw

OUT, VIDS = sys.argv[1], sys.argv[2:]
os.makedirs(OUT, exist_ok=True)
TW, TH, NS = 320, 180, 8


def probe(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True)
    return float(r.stdout.strip())


def frames(v, w=160, h=90):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps=6,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


info, tiles = [], []
for v in VIDS:
    name = os.path.splitext(os.path.basename(v))[0]; dur = probe(v); f = frames(v).astype(float)
    g = f.mean(3); d = np.abs(np.diff(g, axis=0)).mean((1, 2)); cuts = int((d > 25).sum())
    r, gr, b = f[..., 0], f[..., 1], f[..., 2]
    lime = float(((gr > 150) & (r > 110) & (b < 90) & (gr > b + 80)).mean())
    row = Image.new("RGB", (TW * NS, TH + 22), (20, 20, 20)); dr = ImageDraw.Draw(row)
    for i in range(NS):
        t = dur * (i + 0.5) / NS
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", "-vf", f"scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == TW * TH * 3: row.paste(Image.frombytes("RGB", (TW, TH), raw), (i * TW, 22))
        dr.text((i * TW + 4, 24), f"{t:.1f}s", fill=(255, 255, 0))
    dr.text((4, 4), f"{name}   {dur:.1f}s   cuts~{cuts}   bright {g.mean():.0f}   lime {lime*100:.1f}%", fill=(255, 255, 255))
    tiles.append(row); info.append(dict(name=name, path=v, dur=round(dur, 2), cuts=cuts, bright=round(float(g.mean()), 1), lime=round(lime, 4),
                                        energy=[round(float(x), 1) for x in np.convolve(d, np.ones(6) / 6, "same")[::6]]))
for k in range(0, len(tiles), 4):
    grp = tiles[k:k + 4]; sh = Image.new("RGB", (grp[0].width, sum(t.height for t in grp)))
    y = 0
    for t in grp: sh.paste(t, (0, y)); y += t.height
    sh.save(f"{OUT}/sheet_{k // 4:02d}.jpg", quality=82)
json.dump(info, open(f"{OUT}/survey.json", "w"), indent=1)
print(f"{len(info)} videos -> {OUT}")
