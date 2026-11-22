# AI in-between frames with RIFE 4.9 (Practical-RIFE weights; network code tools/rife/rife_arch.py, MIT, Fannovel16), on CPU.
# Render every other frame of a slow, smooth shot, then fill the gaps here (halves render time). Not for hard cuts or
# frame-exact glitches. Alpha is interpolated too (RGB and A passed as two 3-channel images).
# Usage: PYTHONPATH=tools/ai-py:tools/rife .object-separation/bin/python scripts/ai/interpolate.py A.png B.png OUT.png [--t 0.5]
#    or: ... interpolate.py --fill DIR   (fills every missing f_NNNN.png between existing neighbours in DIR)
import sys, os, re, glob, argparse, time
import numpy as np, torch, torch.nn.functional as F
from PIL import Image
from rife_arch import IFNet

ap = argparse.ArgumentParser(); ap.add_argument("a", nargs="?"); ap.add_argument("b", nargs="?"); ap.add_argument("o", nargs="?")
ap.add_argument("--t", type=float, default=0.5); ap.add_argument("--fill"); ap.add_argument("--threads", type=int, default=3)
args = ap.parse_args(); torch.set_num_threads(args.threads)
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
net = IFNet(arch_ver="4.7"); net.load_state_dict(torch.load(os.path.join(root, "tools/ai-models/rife49.pth"), map_location="cpu", weights_only=False)); net.eval()

def tens(arr): return torch.from_numpy(arr).permute(2, 0, 1)[None].float() / 255.0
def mid(A, B, t):
    _, _, h, w = A.shape; ph, pw = (64 - h % 64) % 64, (64 - w % 64) % 64
    A2, B2 = F.pad(A, (0, pw, 0, ph), mode="replicate"), F.pad(B, (0, pw, 0, ph), mode="replicate")
    with torch.inference_mode():
        out = net(A2, B2, timestep=t, scale_list=[8, 4, 2, 1], training=False, fastmode=True, ensemble=False)
    out = out[0] if isinstance(out, (list, tuple)) else out
    return out[:, :, :h, :w]
def interp(pa, pb, po, t):
    ia, ib = Image.open(pa), Image.open(pb); rgba = ia.mode == "RGBA"
    A, B = np.asarray(ia.convert("RGBA" if rgba else "RGB")), np.asarray(ib.convert("RGBA" if rgba else "RGB"))
    rgb = mid(tens(A[..., :3]), tens(B[..., :3]), t)
    out = (rgb[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)
    if rgba:
        al = mid(tens(np.repeat(A[..., 3:], 3, 2)), tens(np.repeat(B[..., 3:], 3, 2)), t)
        out = np.dstack([out, (al[0, 0].clamp(0, 1).numpy() * 255 + 0.5).astype(np.uint8)])
    Image.fromarray(out).save(po)

if args.fill:
    have = {int(re.search(r"(\d+)\.png$", p).group(1)): p for p in glob.glob(os.path.join(args.fill, "f_*.png"))}
    ks = sorted(have)
    for k0, k1 in zip(ks, ks[1:]):
        for k in range(k0 + 1, k1):
            t0 = time.time(); dst = os.path.join(args.fill, f"f_{k:04d}.png")
            interp(have[k0], have[k1], dst, (k - k0) / (k1 - k0)); print(f"f_{k:04d} {time.time() - t0:.1f}s", flush=True)
else:
    interp(args.a, args.b, args.o, args.t)
