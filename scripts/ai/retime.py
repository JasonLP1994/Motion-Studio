# Speed-ramp a rendered frame sequence: slow motion via RIFE in-betweens (no extra 3D rendering), fast sections blend the
# frames they skip (natural motion blur, the frame-blending idea behind f0e/blur, Smoothie, Teres), ramps smoothed inside a shot, hard speed changes allowed at cuts, and never interpolates across a cut.
# Speed plan JSON: {"cuts": [31, 67, ...], "segments": [[src_start, src_end, speed], ...], "ramp": 6}
#   segments are in source frames (start inclusive, end exclusive), speed 0.5 = half speed (slow-mo), 2 = double speed.
# Usage: PYTHONPATH=tools/ai-py:tools/rife .object-separation/bin/python scripts/ai/retime.py IN_DIR OUT_DIR PLAN.json
#        (IN_DIR holds f_0001.png ...; writes OUT_DIR/f_0001.png ... and OUT_DIR/timemap.json for the sound)
import sys, os, json, math, shutil
import numpy as np, torch, torch.nn.functional as F
from PIL import Image
from rife_arch import IFNet

inp, out, plan_p = sys.argv[1], sys.argv[2], sys.argv[3]
plan = json.load(open(plan_p)); cuts = set(plan["cuts"]); ramp = plan.get("ramp", 6)
segs = plan["segments"]; src_last = segs[-1][1] - 1
torch.set_num_threads(int(os.environ.get("THREADS", "4")))
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
net = IFNet(arch_ver="4.7"); net.load_state_dict(torch.load(os.path.join(root, "tools/ai-models/rife49.pth"), map_location="cpu", weights_only=False)); net.eval()

def raw_speed(s):
    for a, b, v in segs:
        if a <= s < b: return v
    return segs[-1][2]
def shot_start(s):  # first frame of the shot containing s
    st = min(f for f, *_ in segs)
    for c in sorted(cuts):
        if c <= s: st = c
    return st
def speed(s):  # average the speed over a small window, but never across a cut (cuts may jump)
    lo, hi = shot_start(s), min([c for c in cuts if c > s] + [src_last + 1])
    xs = [x for x in np.linspace(s - ramp / 2, s + ramp / 2, 9) if lo <= x < hi]
    return float(np.mean([raw_speed(x) for x in xs])) if xs else raw_speed(s)

# build the output -> source time map
times, s = [], float(segs[0][0])
while s <= src_last + 1e-6:
    times.append(s); s += speed(s)

def load(k): return np.asarray(Image.open(os.path.join(inp, f"f_{k:04d}.png")).convert("RGBA"))
def tens(a): return torch.from_numpy(a.copy()).permute(2, 0, 1)[None].float() / 255.0
def mid(A, B, t):
    _, _, h, w = A.shape; ph, pw = (64 - h % 64) % 64, (64 - w % 64) % 64
    with torch.inference_mode():
        o = net(F.pad(A, (0, pw, 0, ph), mode="replicate"), F.pad(B, (0, pw, 0, ph), mode="replicate"), timestep=t, scale_list=[8, 4, 2, 1], training=False, fastmode=True, ensemble=False)
    o = o[0] if isinstance(o, (list, tuple)) else o
    return o[:, :, :h, :w]

os.makedirs(out, exist_ok=True); done = 0
for i, s in enumerate(times, 1):
    dst = os.path.join(out, f"f_{i:04d}.png")
    if os.path.exists(dst): continue
    k0 = int(math.floor(s)); fr = s - k0
    sp = speed(s)
    if sp > 1.15:   # fast section: blend the source frames this output frame "covers" = natural motion blur (shutter open)
        lo, hi = shot_start(s), min([c for c in cuts if c > s] + [src_last + 1]) - 1
        ks = [k for k in range(int(math.ceil(s - sp / 2)), int(math.floor(s + sp / 2)) + 1) if lo <= k <= hi] or [int(round(s))]
        frames = [load(k).astype(np.float32) for k in ks]
        samples = list(frames)
        for fa, fb in zip(frames, frames[1:]):      # RIFE midpoints make the blur continuous instead of stepped copies
            m = mid(tens(fa[..., :3].astype(np.uint8)), tens(fb[..., :3].astype(np.uint8)), 0.5)[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255
            samples.append(np.dstack([m, (fa[..., 3] + fb[..., 3]) / 2]))
        acc = np.mean(samples, axis=0)
        Image.fromarray((acc + 0.5).astype(np.uint8), "RGBA").save(dst); done += 1; continue
    if fr < 0.04 or k0 + 1 > src_last or (k0 + 1) in cuts or fr > 0.96:   # near a real frame, at the end, or the next frame is across a cut
        k = k0 if (fr <= 0.5 or (k0 + 1) in cuts or k0 + 1 > src_last) else k0 + 1
        shutil.copyfile(os.path.join(inp, f"f_{k:04d}.png"), dst)
    else:
        A, B = load(k0), load(k0 + 1)
        rgb = mid(tens(A[..., :3]), tens(B[..., :3]), fr)
        Image.fromarray((rgb[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)).save(dst)
    done += 1
json.dump({"fps": 24, "out_frames": len(times), "src_times": times}, open(os.path.join(out, "timemap.json"), "w"))
print(f"retimed {len(times)} output frames from source {segs[0][0]}-{src_last} ({done} written)")
