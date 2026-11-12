# Make the open Blender scene ready for a cloud render farm (GarageFarm, RebusFarm, Fox, ...), then save it.
# Used by render_still.py (FARM_BLEND=...) and any future scene builder:  farm_prep.prepare(scene, path, ...)
# What farms need: one self-contained .blend (all images packed), Cycles settings that work on their GPUs or CPUs,
# the denoiser on (their Blender builds include OpenImageDenoise), a relative output path and the frame range.
import bpy, os

def prepare(sc, path, samples=128, frames=(1, 1), name="render", fps=30, motion_blur=False):
    cy = sc.cycles
    sc.render.engine = "CYCLES"
    cy.device = "GPU"                  # farms with GPUs use it; CPU farms fall back automatically
    cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.01
    cy.use_denoising = True
    try: cy.denoiser = "OPENIMAGEDENOISE"   # present in official/farm builds even if this local build lacks it
    except TypeError: pass
    sc.render.use_motion_blur = motion_blur; sc.render.motion_blur_shutter = 0.5
    sc.frame_start, sc.frame_end = frames; sc.render.fps = fps
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    sc.render.filepath = f"//render/{name}_"   # farms write frames next to the file: render/<name>_0001.png
    sc.render.use_file_extension = True; sc.render.use_overwrite = False; sc.render.use_placeholder = False
    bpy.ops.file.pack_all()                     # textures, masks: everything inside the one file
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path), compress=True, relative_remap=True)
    size = os.path.getsize(path) / 1e6
    print(f"FARM FILE {path}: {size:.1f} MB, frames {frames[0]}-{frames[1]}, {samples} spp + denoise, Blender {bpy.app.version_string}", flush=True)
