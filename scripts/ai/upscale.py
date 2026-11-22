# AI upscale rendered frames with Real-ESRGAN (BSD-3, xinntao) via spandrel, on CPU. Alpha is resized separately
# (Lanczos) so transparent Blender renders keep their cut-out. Render small, upscale here instead of a plain resize.
# Setup: tools/ai-py (spandrel, einops) + tools/ai-models/RealESRGAN_x2.pth / RealESRGAN_x4plus.pth; PyTorch from .object-separation.
# Usage: PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py IN_DIR OUT_DIR WIDTH HEIGHT [--model fast|x2|x4]  (fast = compact 2x, CC-BY 4.0 Philip Hofmann) [--threads N]
import sys, os, glob, time, argparse
import numpy as np, torch
from PIL import Image
from spandrel import ModelLoader

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("w", type=int); ap.add_argument("h", type=int)
ap.add_argument("--model", default="x2"); ap.add_argument("--threads", type=int, default=3); ap.add_argument("--tile", type=int, default=512)
ap.add_argument("--skip-existing", action="store_true")
a = ap.parse_args()
torch.set_num_threads(a.threads)
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(root, "tools/ai-models", {"x2": "RealESRGAN_x2.pth", "x4": "RealESRGAN_x4plus.pth", "fast": "2xNomosUni_compact.safetensors"}[a.model])
model = ModelLoader().load_from_file(path).eval(); scale = model.scale
os.makedirs(a.out, exist_ok=True)

def run(rgb):  # tiled inference with overlap so CPU memory stays small
    x = torch.from_numpy(rgb).permute(2, 0, 1)[None].float() / 255.0
    _, _, H, W = x.shape; t, pad = a.tile, 16
    out = torch.zeros(1, 3, H * scale, W * scale)
    with torch.inference_mode():
        for y0 in range(0, H, t):
            for x0 in range(0, W, t):
                ya, yb, xa, xb = max(0, y0 - pad), min(H, y0 + t + pad), max(0, x0 - pad), min(W, x0 + t + pad)
                o = model(x[:, :, ya:yb, xa:xb])
                oy, ox = (y0 - ya) * scale, (x0 - xa) * scale
                hh, ww = (min(y0 + t, H) - y0) * scale, (min(x0 + t, W) - x0) * scale
                out[:, :, y0 * scale:y0 * scale + hh, x0 * scale:x0 * scale + ww] = o[:, :, oy:oy + hh, ox:ox + ww]
    return (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)

files = sorted(glob.glob(os.path.join(a.inp, "*.png"))) if os.path.isdir(a.inp) else [a.inp]
for i, f in enumerate(files):
    dst = os.path.join(a.out, os.path.basename(f))
    if a.skip_existing and os.path.exists(dst): continue
    t0 = time.time(); im = Image.open(f); has_a = im.mode in ("RGBA", "LA")
    rgb = np.asarray(im.convert("RGB"))
    up = Image.fromarray(run(rgb)).resize((a.w, a.h), Image.LANCZOS)
    if has_a: up.putalpha(im.getchannel("A").resize((a.w, a.h), Image.LANCZOS))
    up.save(dst); print(f"[{i + 1}/{len(files)}] {os.path.basename(f)} {time.time() - t0:.1f}s", flush=True)
