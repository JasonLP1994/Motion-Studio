# Cut each Ferrari photo out with SAM 2 (image mode). Prompt = a box around the car (from the red
# paint mask, padded, extra at the bottom for tyres) + a few points on the paint. Keeps the best of
# SAM's 3 candidate masks. Saves <name>-cut.png (RGBA) and <name>-cutmask.png, plus a paper preview.
# Run with the project venv:  .object-separation/bin/python scripts/ferrari/sam_cutout.py <names...>
import sys, numpy as np, torch
from PIL import Image, ImageFilter
from transformers import Sam2Model, Sam2Processor
MODEL = "facebook/sam2.1-hiera-large"
proc = Sam2Processor.from_pretrained(MODEL); model = Sam2Model.from_pretrained(MODEL).eval()
for name in sys.argv[1:]:
    im = Image.open(f"public/ferrari/{name}.png").convert("RGB"); W, H = im.size
    paint = np.array(Image.open(f"public/ferrari/{name}-mask.png").convert("L").filter(ImageFilter.MinFilter(9))) > 128
    ys, xs = np.nonzero(paint)
    # robust bbox (ignore floor-reflection specks): 1st..99th percentile of paint pixels
    x0, x1 = np.percentile(xs, 0.5), np.percentile(xs, 99.5); y0, y1 = np.percentile(ys, 0.5), np.percentile(ys, 99.5)
    bw, bh = x1 - x0, y1 - y0
    box = [max(0, x0 - 0.05 * bw), max(0, y0 - 0.06 * bh), min(W - 1, x1 + 0.05 * bw), min(H - 1, y1 + 0.16 * bh)]
    rng = np.random.default_rng(1); pick = rng.choice(len(xs), 4, replace=False)
    pts = [[float(xs[i]), float(ys[i])] for i in pick]
    inputs = proc(images=im, input_boxes=[[box]], input_points=[[pts]], input_labels=[[[1] * len(pts)]], return_tensors="pt")
    with torch.inference_mode():
        out = model(**inputs, multimask_output=True)
    masks = proc.post_process_masks(out.pred_masks, inputs["original_sizes"])[0][0]  # (3, H, W)
    best = int(out.iou_scores[0, 0].argmax())
    m = masks[best].numpy().astype(np.uint8) * 255
    mask = Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.0))
    rgba = im.copy(); rgba.putalpha(mask)
    rgba.save(f"public/ferrari/{name}-cut.png"); mask.save(f"public/ferrari/{name}-cutmask.png")
    prev = Image.new("RGB", im.size, (238, 236, 231)); prev.paste(rgba, (0, 0), rgba); prev.save(f"public/ferrari/{name}-cut-check.png")
    print(name, "box", [int(v) for v in box], "scores", [round(float(s), 3) for s in out.iou_scores[0, 0]], "best", best)
