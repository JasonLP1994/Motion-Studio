# Pop Out lyric video assets -> public/popout/ : halftone B&W cut-outs, paper texture, spliced audio.
# Usage: tools/sam-py/bin/python scripts/popout/prep.py
import os, subprocess, wave, numpy as np
from PIL import Image, ImageFilter, ImageOps
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); O = f"{R}/public/popout"; os.makedirs(O, exist_ok=True)
rng = np.random.default_rng(3)
def halftone(g, pitch=5.0, ang=45):
    h, w = g.shape; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = np.radians(ang)
    u = (xx * np.cos(a) + yy * np.sin(a)) / pitch; v = (-xx * np.sin(a) + yy * np.cos(a)) / pitch
    d = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2) / 0.7071   # 0 centre .. 1 corner
    return (d > np.sqrt(np.clip(1 - g, 0, 1))).astype(np.float32)           # 1 = paper, 0 = ink dot
for i in range(1, 9):
    im = Image.open(f"{R}/work/popout/cut/photo_{i}.png"); bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox(); im = im.crop(bb)
    s = 1500 / im.height; im = im.resize((int(im.width * s), 1500), Image.LANCZOS)
    g = ImageOps.autocontrast(im.convert("RGB").convert("L"), cutoff=1.5)
    g = np.asarray(g).astype(np.float32) / 255; g = np.clip((g - 0.06) / 0.88, 0, 1) ** 0.9
    t = 0.55 * g + 0.45 * halftone(g) + rng.normal(0, 0.05, g.shape)          # photocopy: tone + dots + grain
    tt = np.clip(t, 0, 1)[..., None]   # cold duotone like the cover: navy shadows -> ice blue mids -> white highlights
    lo, mid, hi = np.array([6, 12, 26.]), np.array([96, 140, 196.]), np.array([240, 246, 252.])
    rgb = np.where(tt < 0.55, lo + (mid - lo) * (tt / 0.55), mid + (hi - mid) * ((tt - 0.55) / 0.45)).astype(np.uint8)
    out = Image.fromarray(rgb); out.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))); out.save(f"{O}/p{i}.png")
    print("p", i, out.size)
# dust: white specks + fine scratches over the navy (cover grammar), plus the old paper grain map
D = np.zeros((1080, 1920), np.float32)
for _ in range(2600):
    y, x = rng.integers(0, 1080), rng.integers(0, 1920); D[y, x] = rng.uniform(0.3, 1)
for _ in range(60):
    y, x = rng.integers(0, 1080), rng.integers(0, 1920); L = rng.integers(20, 140); a = rng.uniform(0, np.pi)
    for k in range(L):
        yy, xx = int(y + k * np.sin(a)), int(x + k * np.cos(a))
        if 0 <= yy < 1080 and 0 <= xx < 1920: D[yy, xx] = max(D[yy, xx], 0.35)
Di = Image.fromarray((np.clip(D, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
du = Image.new('RGBA', (1920, 1080), (235, 242, 255, 0)); du.putalpha(Di); du.save(f'{O}/dust.png')
# paper: cream with fibres, blotches and grain (tiled under everything at low opacity)
W, H = 1920, 1080; n = rng.normal(0, 1, (H // 4, W // 4)); bl = Image.fromarray(((n - n.min()) / (np.ptp(n)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
b = np.asarray(bl).astype(np.float32) / 255; g = rng.normal(0, 1, (H, W)) * 0.035 + (b - 0.5) * 0.18
Image.fromarray(np.clip(128 + g * 255, 0, 255).astype(np.uint8)).save(f"{O}/paper.png")
# audio: 21.405..47.45 of the song, then the matching beat position of an intro bar (no vocals) for the title card
T0, T1, CARD = 21.405, 47.45, 4.0; INTRO = 18.548 + (T1 - 47.119)   # card: title 2 s + Phillips Digital logo 2 s; INTRO = 18.548 + (T1 - 47.119)
tmp = f"{O}/../../work/popout/song48.wav"; os.makedirs(os.path.dirname(tmp), exist_ok=True)
subprocess.run(["npx", "remotion", "ffmpeg", "-y", "-loglevel", "error", "-i", f"{R}/inputs/pop-out/pop-out.mp3", "-ac", "2", "-ar", "48000", tmp], check=True, cwd=R)
w = wave.open(tmp); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2) / 32768.
a = x[int(T0 * sr):int(T1 * sr)].copy(); xf = int(0.12 * sr)
c = x[int(INTRO * sr) - xf:int((INTRO + CARD) * sr)].copy()
r = np.linspace(0, 1, xf)[:, None]; a[-xf:] = a[-xf:] * (1 - r) ** 0.5 + c[:xf] * r ** 0.5 * 1.6
c = c[xf:] * 1.6; f = np.ones(len(c)); f[-int(1.3 * sr):] = np.linspace(1, 0, int(1.3 * sr)) ** 2; c *= f[:, None]
y = np.concatenate([a, c]); y = y / max(1e-6, np.abs(y).max()) * 0.97 * 10 ** (-1.3 / 20)   # about -14 LUFS
with wave.open(f"{O}/track.wav", "wb") as o: o.setnchannels(2); o.setsampwidth(2); o.setframerate(sr); o.writeframes((y * 32767).astype(np.int16).tobytes())
print("audio", len(y) / sr, "s")
