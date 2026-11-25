#!/bin/bash
# Rebuild the free image-to-3D tool (TripoSR, MIT licence) inside this project. Everything lands in git-ignored tools/.
#   bash scripts/ai/setup_triposr.sh
# Needs: tools/ai-venv (the AI toolkit, CPU PyTorch) and ~2 GB free disk (model ~1.6 GB).
set -e; cd "$(dirname "$0")/../.."
PY=tools/ai-venv/bin/python
[ -d tools/triposr ] || git clone --depth 1 https://github.com/VAST-AI-Research/TripoSR.git tools/triposr
$PY -m pip install -q omegaconf transformers trimesh huggingface-hub PyMCubes imageio
$PY - <<'EOF'
import re
# 1) torchmcubes needs compiling: use prebuilt PyMCubes
p='tools/triposr/tsr/models/isosurface.py'; s=open(p).read()
if 'Motion Studio patch' not in s:
    s=s.replace("from torchmcubes import marching_cubes\n",'''# Motion Studio patch: torchmcubes needs compiling; use the prebuilt PyMCubes (CPU) instead.
import mcubes


def marching_cubes(level, threshold):
    v, f = mcubes.marching_cubes(level.cpu().numpy().astype(np.float64), threshold)
    # torchmcubes returns vertices as (z, y, x); the caller swaps them back
    v = torch.from_numpy(v[:, [2, 1, 0]].astype(np.float32))
    f = torch.from_numpy(f.astype(np.int64))
    return v, f
'''); open(p,'w').write(s)
# 2) rembg optional
p='tools/triposr/tsr/utils.py'; s=open(p).read()
if 'Motion Studio patch' not in s:
    s=s.replace("\nimport rembg\n","\ntry:  # Motion Studio patch: rembg is optional (plain-background cut is used without it)\n    import rembg\nexcept ImportError:\n    rembg = None\n"); open(p,'w').write(s)
# 3) newer transformers renamed ViT layers: remap checkpoint names on load
p='tools/triposr/tsr/system.py'; s=open(p).read()
if 'Motion Studio patch' not in s:
    s=s.replace('''        ckpt = torch.load(weight_path, map_location="cpu")
        model.load_state_dict(ckpt)''','''        ckpt = torch.load(weight_path, map_location="cpu")
        # Motion Studio patch: newer transformers renamed ViT layers; map the checkpoint's old names to the new ones.
        want = set(model.state_dict().keys())
        if not set(ckpt.keys()) <= want:
            import re
            ren = [("attention.attention.query", "attention.q_proj"), ("attention.attention.key", "attention.k_proj"),
                   ("attention.attention.value", "attention.v_proj"), ("attention.output.dense", "attention.o_proj"),
                   ("intermediate.dense", "mlp.fc1"), ("output.dense", "mlp.fc2")]
            fixed = {}
            for k, v in ckpt.items():
                nk = k
                if k not in want and ".encoder.layer." in k:
                    nk = re.sub(r"\\.encoder\\.layer\\.(\\d+)\\.", r".layers.\\1.", k)
                    for a, b in ren:
                        nk = nk.replace(a, b)
                fixed[nk] = v
            ckpt = fixed
        model.load_state_dict(ckpt)'''); open(p,'w').write(s)
print("patches ok")
EOF
HF_HOME=$PWD/tools/hf-cache HF_HUB_DISABLE_TELEMETRY=1 $PY -c "
from huggingface_hub import hf_hub_download
for f in ['config.yaml','model.ckpt']: hf_hub_download('stabilityai/TripoSR', f)
from transformers import ViTConfig; ViTConfig.from_pretrained('facebook/dino-vitb16'); print('model ok')"
echo "TripoSR ready: tools/ai-venv/bin/python scripts/ai/image_to_3d.py <image> <out.glb>"
