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
