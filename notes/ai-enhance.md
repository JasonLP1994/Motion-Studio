# AI render enhancement (free, local, CPU)

Installed (all in git-ignored `tools/`, nothing outside this folder): run with the project's PyTorch from `.object-separation/`.

| Tool | Job | Command | Speed here (CPU, shared) |
|---|---|---|---|
| Intel Open Image Denoise (Apache-2.0) | Denoise path-traced (Cycles) renders, so Cycles can run at few samples | `PYTHONPATH=tools/py312 blender -b FILE.blend -P scripts/denoise/oidn_render.py -- --out DIR --start N --end M --spp 96` (setup: `bash scripts/denoise/setup_oidn.sh`; Blender needs the numpy in tools/py312) | seconds per frame |
| Compact 2x upscaler "2xNomosUni_compact" (Philip Hofmann, CC-BY 4.0) | Render at 720p, AI-upscale to 1080p (keeps depth-of-field blur) | `PYTHONPATH=tools/ai-py .object-separation/bin/python scripts/ai/upscale.py IN_DIR OUT_DIR 1920 1080 --model fast` | ~13 s/frame |
| Real-ESRGAN x2 / x4plus (BSD-3, xinntao) | Highest-quality upscale (stills, hero frames, 4K) | same script, `--model x2` or `--model x4` | ~70 s/frame |
| RIFE 4.9 (MIT; network code tools/rife/rife_arch.py from Fannovel16/ComfyUI-Frame-Interpolation) | Render every other frame of a slow shot, AI-fill the in-betweens (halves render time) | `PYTHONPATH=tools/ai-py:tools/rife .object-separation/bin/python scripts/ai/interpolate.py --fill FRAMES_DIR` | ~5.5 s/frame |

Tested on the lime case (frame 220): the compact upscale is visibly crisper than a Lanczos resize and nearly matches Real-ESRGAN x2;
the RIFE in-between of 219/221 matched the real rendered 220 at 34.2 dB PSNR (practically identical).

Rules of use
- Upscale: Blender alpha is kept (resized separately). Upscale before compositing type (type is drawn at full size in Remotion anyway).
- RIFE: only within one continuous shot with smooth motion. Never across a cut, a strobe/glitch frame, or a frame that must land exactly
  on a beat; render those frames for real. Check the in-betweens at full frame rate.
- Faster product pipeline: Cycles at ~64 samples + OIDN, rendered at 720p on even frames only -> RIFE fill -> compact 2x upscale.
- Credits for posts that use them aren't required for outputs, but keep the model credits in `public/models/CREDITS.md`.
Weights: tools/ai-models/ (RealESRGAN_x2.pth and RealESRGAN_x4plus.pth via Hugging Face mirrors of the official release,
rife49.pth, 2xNomosUni_compact.safetensors). Python packages: tools/ai-py (spandrel 0.4.2, einops).

## Default recipe: best quality in the fastest time (user rule)
1. Cycles at ~48 samples (adaptive, threshold 0.03) + OIDN denoise. Clamp indirect 3 (no fireflies), diffuse 2 / glossy 4 /
   transmission 2 bounces, caustics off, light tree on, persistent data on for sequences.
2. Render 720p (or 50-67%) and AI-upscale to the delivery size with `--model fast` (Real-ESRGAN only for hero stills).
3. Smooth shots: render every other frame, RIFE fills the rest. Always render for real: the first and last frame of every shot,
   frames either side of a cut, glitch/strobe frames, hits (clicks, impacts) and fast moves.
4. One render at a time on this machine (two at once each run at half speed). Long renders as tracked background tasks.
5. Engine: always Cycles (user rule: best result). Eevee only if the user asks for it.
Measured: lime case v2 at 720p, 96 spp took ~3.3-5 min/frame while sharing the CPU with another render.

## Setup in a fresh container (done 22 Nov in the Motion Studio /home/user container; all inside ignored tools/)
- `python3 -m venv tools/ai-venv`, then with `--no-cache-dir`: `torch` and `torchvision` from https://download.pytorch.org/whl/cpu
  (torchvision must come from the same CPU index, or spandrel fails with "torchvision::nms does not exist"), plus `numpy pillow spandrel==0.4.2 einops`.
- `tools/rife/rife_arch.py`: raw from Fannovel16/ComfyUI-Frame-Interpolation `vfi_models/rife/rife_arch.py`; replace its
  `from comfy.model_management import get_torch_device` line with a CPU stand-in.
- Weights in `tools/ai-models/`: `rife49.pth` (github.com/Fannovel16/ComfyUI-Frame-Interpolation/releases/download/models/rife49.pth),
  `2xNomosUni_compact.safetensors` (github.com/Phhofm/models/releases/download/2xNomosUni_compact_multijpg_ldl/...safetensors).
- Run: `PYTHONPATH=tools/rife tools/ai-venv/bin/python scripts/ai/interpolate.py ...` and `tools/ai-venv/bin/python scripts/ai/upscale.py ...`.
- Long Blender sequences on a frame list: `FRAMES=<file with a comma list> bash scripts/denoise/render_resume.sh ...` (oidn_render.py `--frames`).

## Shoe slime HQ (22 Nov): switched mid-render to this recipe
Frames 1-206 rendered for real (960x540, 32 spp + OIDN). From 207: every other frame, plus both sides of every cut
(128, 195, 270, 345, 420), the SET hit 470-480 and the last frames; RIFE fills the rest; all 600 AI-upscaled to 1080p.
Same Cycles settings as frames 1-206 so the look doesn't change mid-film (user: "Cycles is better look").
Test on real frames: RIFE 27-31 dB PSNR on churning slime (34 dB on the phone case), visually identical except the thinnest
strands slightly softer; frame-to-frame motion as even as the real sequence (no stutter). ~4 s per in-between, ~10 s per upscale.
