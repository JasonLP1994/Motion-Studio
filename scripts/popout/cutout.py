# Person cut-out for stills with BiRefNet-lite (MIT, ONNX, local). Usage: tools/sam-py/bin/python scripts/popout/cutout.py OUTDIR IMG...
# Writes OUTDIR/<name>.png (RGBA, original colour) and <name>_mask.png.
import sys, os, numpy as np, onnxruntime as ort
from PIL import Image
M = os.path.join(os.path.dirname(__file__), "../../tools/ai-models/birefnet/model.onnx")
s = ort.InferenceSession(M, providers=["CPUExecutionProvider"]); inp = s.get_inputs()[0].name
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for p in sys.argv[2:]:
    im = Image.open(p).convert("RGB"); W, H = im.size
    x = np.asarray(im.resize((1024, 1024), Image.BICUBIC)).astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    y = s.run(None, {inp: x.transpose(2, 0, 1)[None].astype(np.float32)})[-1][0, 0]
    y = 1 / (1 + np.exp(-y)) if y.min() < 0 or y.max() > 1 else y
    m = Image.fromarray((np.clip(y, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    n = os.path.splitext(os.path.basename(p))[0]
    rgba = im.copy(); rgba.putalpha(m); rgba.save(f"{out}/{n}.png"); m.save(f"{out}/{n}_mask.png")
    print(n, W, H, "cover", round(float(np.asarray(m).mean() / 255), 2))
