"""Render frames with Cycles and clean them with Intel Open Image Denoise (OIDN).

Why: this Blender build has no built-in denoiser, so low-sample renders look grainy.
This script renders the noisy image plus two helper passes (albedo = surface colour,
normal = surface direction), runs OIDN on them, then applies the scene's own colour
look (view transform + compositor glare) and saves a PNG per frame.

Setup (once): bash scripts/denoise/setup_oidn.sh
Usage:
  blender -b <file.blend> -P scripts/denoise/oidn_render.py -- \
      --out <dir> --start 300 --end 300 [--frames 1,3,5] [--pct 33] [--spp 16] [--keep-exr]
Frames that already exist in <dir> are skipped, so a stopped run can resume.
"""
import argparse
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--start", type=int, required=True)
ap.add_argument("--end", type=int, required=True)
ap.add_argument("--pct", type=int, default=None)
ap.add_argument("--spp", type=int, default=None)
ap.add_argument("--keep-exr", action="store_true")
ap.add_argument("--frames", default=None, help="comma list of frames to render instead of start..end (e.g. every other frame for RIFE)")
ap.add_argument("--persistent", action="store_true", help="keep static scene data between frames (faster sequences)")
args = ap.parse_args(argv)

OUT = os.path.abspath(args.out)
EXR = os.path.join(OUT, "exr")
os.makedirs(EXR, exist_ok=True)

sc = bpy.context.scene
if args.pct:
    sc.render.resolution_percentage = args.pct
if args.spp:
    sc.cycles.samples = args.spp
if args.persistent:
    sc.render.use_persistent_data = True
sc.cycles.device = "CPU"
sc.cycles.use_denoising = False
vl = sc.view_layers[0]
vl.cycles.denoising_store_passes = True  # gives "Denoising Albedo" / "Denoising Normal"

# ---- compositor: keep the scene's glare settings, then write raw passes instead ----
tree = sc.node_tree
glare_src = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeGlare"), None)
GLARE = None
if glare_src:
    GLARE = {k: getattr(glare_src, k) for k in
             ("glare_type", "threshold", "mix", "quality", "size")}
for n in list(tree.nodes):
    tree.nodes.remove(n)
rl = tree.nodes.new("CompositorNodeRLayers")
comp = tree.nodes.new("CompositorNodeComposite")
tree.links.new(rl.outputs["Image"], comp.inputs["Image"])
fo = tree.nodes.new("CompositorNodeOutputFile")
fo.base_path = EXR
fo.format.file_format = "OPEN_EXR"
fo.format.color_depth = "32"
fo.format.exr_codec = "ZIP"
fo.file_slots.clear()
for slot, sock in (("color_", "Image"), ("albedo_", "Denoising Albedo"),
                   ("normal_", "Denoising Normal")):
    fo.file_slots.new(slot)
    tree.links.new(rl.outputs[sock], fo.inputs[slot])

# ---- a tiny "post" scene: denoised EXR -> glare -> scene colour look -> PNG ----
post = bpy.data.scenes.new("oidn_post")
post.render.engine = "BLENDER_WORKBENCH"
post.camera = sc.camera
post.render.resolution_x = sc.render.resolution_x
post.render.resolution_y = sc.render.resolution_y
post.render.resolution_percentage = sc.render.resolution_percentage
post.render.image_settings.file_format = "PNG"
post.render.image_settings.color_depth = "16"
TRANSPARENT = sc.render.film_transparent          # keep alpha for overlays (composited later, e.g. in Remotion)
post.render.film_transparent = TRANSPARENT
if TRANSPARENT: post.render.image_settings.color_mode = "RGBA"
for k in ("view_transform", "look", "exposure", "gamma"):
    setattr(post.view_settings, k, getattr(sc.view_settings, k))
post.display_settings.display_device = sc.display_settings.display_device
post.use_nodes = True
pt = post.node_tree
for n in list(pt.nodes):
    pt.nodes.remove(n)
img_node = pt.nodes.new("CompositorNodeImage")
pcomp = pt.nodes.new("CompositorNodeComposite"); pcomp.use_alpha = True
if GLARE:
    gl = pt.nodes.new("CompositorNodeGlare")
    for k, v in GLARE.items():
        setattr(gl, k, v)
    pt.links.new(img_node.outputs["Image"], gl.inputs["Image"])
    pt.links.new(gl.outputs["Image"], pcomp.inputs["Image"])
else:
    pt.links.new(img_node.outputs["Image"], pcomp.inputs["Image"])

# ---- OIDN runs in a separate system-Python process (oidn_denoise.py) ----
# Loading OIDN inside Blender crashes (its bundled TBB clashes with Blender's).
import subprocess  # noqa: E402
DENOISER = os.path.join(HERE, "oidn_denoise.py")


def load_rgb(path):
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return np.ascontiguousarray(px.reshape(h, w, 4)[:, :, :3]), w, h


def load_alpha(path):
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return np.ascontiguousarray(px.reshape(h, w, 4)[:, :, 3:4])


def denoise(color, albedo, normal, w, h):
    base = os.path.join(EXR, "tmp_")
    np.save(base + "color.npy", color)
    np.save(base + "albedo.npy", albedo)
    np.save(base + "normal.npy", normal)
    subprocess.run(["python3", "-I", DENOISER, base], check=True)
    out = np.load(base + "out.npy").astype(np.float32)
    for k in ("color", "albedo", "normal", "out"):
        os.remove(base + k + ".npy")
    return out


def float_image(rgb, w, h, alpha=None):
    """In-memory linear float image (saving it to EXR first made Blender apply an
    sRGB conversion, which washed the frame out)."""
    im = bpy.data.images.new("dn", w, h, alpha=True, float_buffer=True)
    im.colorspace_settings.name = "Linear Rec.709"
    rgba = np.concatenate([rgb, alpha if alpha is not None else np.ones((h, w, 1), np.float32)], axis=2)
    im.pixels.foreach_set(rgba.ravel())
    return im


FRAMES = [int(x) for x in args.frames.split(",")] if args.frames else range(args.start, args.end + 1)
for f in FRAMES:
    png = os.path.join(OUT, f"d_{f:04d}.png")
    if os.path.exists(png):
        continue
    sc.frame_set(f)
    bpy.ops.render.render(write_still=False, scene=sc.name)
    c, w, h = load_rgb(os.path.join(EXR, f"color_{f:04d}.exr"))
    a, _, _ = load_rgb(os.path.join(EXR, f"albedo_{f:04d}.exr"))
    nrm, _, _ = load_rgb(os.path.join(EXR, f"normal_{f:04d}.exr"))
    dn = denoise(c, a, nrm, w, h)
    alpha = load_alpha(os.path.join(EXR, f"color_{f:04d}.exr")) if TRANSPARENT else None
    im = float_image(dn, w, h, alpha)
    img_node.image = im
    post.frame_set(f)
    post.render.filepath = png
    bpy.ops.render.render(write_still=True, scene=post.name)
    bpy.data.images.remove(im)
    if not args.keep_exr:
        for p in ("color_", "albedo_", "normal_"):
            try:
                os.remove(os.path.join(EXR, f"{p}{f:04d}.exr"))
            except FileNotFoundError:
                pass
    print(f"OIDN frame {f} done -> {png}", flush=True)
