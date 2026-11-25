"""Image -> textured 3D model with TripoSR (MIT, VAST-AI-Research/TripoSR), CPU-friendly.

Usage:
  tools/ai-venv/bin/python scripts/ai/image_to_3d.py <image> <out.glb|.obj> [--res 256] [--fg 0.85] [--no-remove-bg]

- Best input: one object, whole object in frame, plain background (or a PNG with transparency).
- Background removal: uses the PNG's own transparency if it has some; otherwise rembg if installed;
  otherwise a simple "remove the border colour" cut that works on plain backgrounds.
- Output keeps colours as vertex colours (Blender: Color Attribute node). Never overwrites.
- Model files live in tools/hf-cache (inside the project, git-ignored).
"""
import argparse, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("HF_HOME", str(ROOT / "tools" / "hf-cache"))
os.environ.setdefault("U2NET_HOME", str(ROOT / "tools" / "u2net"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
sys.path.insert(0, str(ROOT / "tools" / "triposr"))

import numpy as np
import torch
from PIL import Image, ImageFilter


def border_cut(img: Image.Image, tol: float = 38.0) -> Image.Image:
    """Plain-background cut: pixels close to the median border colour become transparent."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(-1))
    mask = Image.fromarray(((dist > tol) * 255).astype(np.uint8))
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1))
    out = img.convert("RGB").copy(); out.putalpha(mask)
    return out


def cut_out(img: Image.Image) -> Image.Image:
    if img.mode == "RGBA" and np.asarray(img)[..., 3].min() < 250:
        return img
    try:
        import rembg
        return rembg.remove(img, session=rembg.new_session())
    except ImportError:
        print("rembg not installed: using plain-background cut")
        return border_cut(img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("out")
    ap.add_argument("--res", type=int, default=256, help="mesh detail (marching cubes resolution)")
    ap.add_argument("--fg", type=float, default=0.85, help="how much of the frame the object fills")
    ap.add_argument("--no-remove-bg", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"exists, not overwriting: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(a.threads)

    from tsr.system import TSR
    from tsr.utils import resize_foreground

    t = time.time()
    model = TSR.from_pretrained("stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt")
    model.renderer.set_chunk_size(8192)
    print(f"model loaded {time.time()-t:.0f}s")

    img = Image.open(a.image)
    if a.no_remove_bg:
        img = img.convert("RGB")
    else:
        img = resize_foreground(cut_out(img), a.fg)
        arr = np.asarray(img).astype(np.float32) / 255.0
        arr = arr[..., :3] * arr[..., 3:4] + (1 - arr[..., 3:4]) * 0.5   # grey background, as TripoSR expects
        img = Image.fromarray((arr * 255).astype(np.uint8))
    prep = out.with_name(out.stem + "-input.png"); img.save(prep)

    t = time.time()
    with torch.no_grad():
        codes = model([img], device="cpu")
        mesh = model.extract_mesh(codes, True, resolution=a.res)[0]
    # Stand it upright: TripoSR's up is +Z, glTF/OBJ convention is +Y up (Blender converts on import).
    mesh.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float))
    if out.suffix.lower() in (".glb", ".gltf"):
        # glTF vertex colours are linear; TripoSR gives sRGB, so convert or they look washed out.
        c = mesh.visual.vertex_colors.astype(np.float64) / 255.0
        rgb = c[:, :3]
        lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
        c[:, :3] = lin
        mesh.visual.vertex_colors = (np.clip(c, 0, 1) * 255).round().astype(np.uint8)
    mesh.export(str(out))
    print(f"saved {out} ({len(mesh.vertices)} verts, {len(mesh.faces)} faces) in {time.time()-t:.0f}s; input used: {prep}")


if __name__ == "__main__":
    main()
