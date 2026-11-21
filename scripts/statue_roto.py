# Rotoscope the statue (all frames) and her face (close-up frames) with SAM 2 video mode, following
# .claude/skills/object-separation (chunks of 60 frames, each seeded by the previous chunk's last mask).
# Frames: work/statue/f_00001.jpg ... (960x540, from inputs/statue-cathedral.mp4). Masks -> work/statue/{mask,face}/
# Run: HF_HUB_DISABLE_XET=1 .object-separation/bin/python scripts/statue_roto.py
import os, glob, time, numpy as np, torch
from PIL import Image
from transformers import Sam2VideoModel, Sam2VideoProcessor
MODEL = "facebook/sam2.1-hiera-large"
model = Sam2VideoModel.from_pretrained(MODEL).eval(); proc = Sam2VideoProcessor.from_pretrained(MODEL)
files = sorted(glob.glob("work/statue/f_*.jpg")); N = len(files)
def frames(a, b): return [np.array(Image.open(files[i]).convert("RGB")) for i in range(a, b + 1)]
def chunk(fr, points=None, labels=None, mask=None):
    H, W = fr[0].shape[:2]
    s = proc.init_video_session(video=fr, inference_device="cpu", video_storage_device="cpu", inference_state_device="cpu", dtype=torch.float32)
    if mask is None:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1, input_points=[[points]], input_labels=[[labels]])
    else:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1, input_masks=mask.astype(np.uint8))
    res = {}
    with torch.inference_mode():
        model(inference_session=s, frame_idx=0)
        for o in model.propagate_in_video_iterator(s, start_frame_idx=0):
            m = proc.post_process_masks([o.pred_masks], original_sizes=[[H, W]], binarize=True)[0]
            res[o.frame_idx] = m.squeeze().cpu().numpy().astype(bool)
    return res
def run(name, start, end, pts, lbl, ch=60):
    os.makedirs(f"work/statue/{name}", exist_ok=True); a, seed = start, None; t0 = time.time()
    while a < end:
        b = min(end, a + ch); fr = frames(a, b)
        r = chunk(fr, points=pts, labels=lbl) if seed is None else chunk(fr, mask=seed)
        for k, m in r.items():
            Image.fromarray(m.astype(np.uint8) * 255).save(f"work/statue/{name}/{a + k:05d}.png")
        seed, a = r[len(fr) - 1], b
        print(name, "frames", b + 1, "/", end + 1, f"{time.time() - t0:.0f}s", flush=True)
run("mask", 0, N - 1, [[480, 100], [490, 300], [420, 450], [560, 420], [200, 300], [760, 300]], [1, 1, 1, 1, 0, 0])
run("face", 169, N - 1, [[450, 180], [470, 140], [545, 140]], [1, 1, 0])
print("done")
