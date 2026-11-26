"""Real-ESRGAN x4plus upscale (tiled, CPU). Run from repo root with tools/esrgan/bin/python.
Setup: python3 -m venv tools/esrgan && tools/esrgan/bin/pip install spandrel pillow numpy; model in tools/esrgan/models/.
Usage: tools/esrgan/bin/python scripts/upscale/esrgan_upscale.py in.jpg out.png [final_width]"""
import sys
import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

src, dst = sys.argv[1], sys.argv[2]
final_w = int(sys.argv[3]) if len(sys.argv) > 3 else None
model = ModelLoader().load_from_file(
    "tools/esrgan/models/RealESRGAN_x4plus.pth").eval()
s = model.scale
torch.set_num_threads(4)

img = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
H, W, _ = img.shape
out = np.zeros((H * s, W * s, 3), np.float32)
wsum = np.zeros((H * s, W * s, 1), np.float32)
T, P = 256, 24  # tile, overlap
ys = list(range(0, max(H - T, 0) + 1, T - P)); ys[-1:] = [ys[-1]] if ys[-1] + T >= H else [ys[-1], H - T]
xs = list(range(0, max(W - T, 0) + 1, T - P)); xs[-1:] = [xs[-1]] if xs[-1] + T >= W else [xs[-1], W - T]
ramp = np.minimum(np.arange(T * s) + 1, np.arange(T * s)[::-1] + 1).astype(np.float32)
ramp = np.minimum(ramp / (P * s), 1.0)
win = (ramp[:, None] * ramp[None, :])[..., None]
n = 0
with torch.inference_mode():
    for y in ys:
        for x in xs:
            t = torch.from_numpy(img[y:y + T, x:x + T].transpose(2, 0, 1)[None].copy())
            r = model(t)[0].clamp(0, 1).numpy().transpose(1, 2, 0)
            out[y * s:(y + T) * s, x * s:(x + T) * s] += r * win
            wsum[y * s:(y + T) * s, x * s:(x + T) * s] += win
            n += 1
            print(f"tile {n}/{len(ys) * len(xs)}", flush=True)
out /= np.maximum(wsum, 1e-6)
res = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
if final_w:
    res = res.resize((final_w, round(final_w * H / W)), Image.LANCZOS)
res.save(dst)
print("saved", dst, res.size)
