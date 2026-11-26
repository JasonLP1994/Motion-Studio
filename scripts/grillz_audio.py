# Grillz animation soundtrack (notes/briefs/grillz-anim.md): 10 s, 120 BPM dark trap made in numpy (808 sub, clap, rolling hats,
# minor bell motif), plus bundled CC0 sfx from .claude/skills/sound-effects/sfx: whoosh into every camera cut (frames 49, 97, 145),
# a tooth clack on each jaw snap (103, 115, 127), a glass "ting" + shimmer on the glint across the PD (206-226), drop-out for the
# grin (from 168) and a final hit. True-peak limited (oversampled) to about -14 LUFS.
# Usage: GAIN_DB=-12 python3 scripts/grillz_audio.py OUT.wav
import sys, wave, os, subprocess, tempfile
import numpy as np
SR, DUR, FPS = 48000, 10.0, 24
GAIN_DB = float(os.environ.get("GAIN_DB", "-12.0"))
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(7)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(ROOT, ".claude/skills/sound-effects/sfx")
def add(sig, at, g=1.0, pan=0.0):
    if sig.ndim == 2: l, r = sig[:, 0], sig[:, 1]
    else: l = r = sig
    i = int(at * SR); n = min(len(l), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += l[:n] * g * (1 - max(0, pan)); R[i:i + n] += r[:n] * g * (1 + min(0, pan))
def tt(d): return np.arange(int(SR * d)) / SR
def env(d, a=0.002, r=0.1): x = tt(d); return np.minimum(1, x / a) * np.exp(-x / r)
def lpf(x, k): return np.convolve(x, np.ones(k) / k, mode='same')
nf = lambda m: 440 * 2 ** ((m - 69) / 12)
TMP = tempfile.mkdtemp()
def load(rel):
    out = os.path.join(TMP, os.path.basename(rel) + ".wav")
    subprocess.run(["npx", "remotion", "ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(SFX, rel), "-ac", "2", "-ar", str(SR), out],
                   check=True, cwd=ROOT)
    with wave.open(out) as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2) / 32768.0
    return a / max(1e-6, np.abs(a).max())
WHOOSH = load("whoosh/fs-169867-swoosh.ogg"); CLACK = load("tick/fs384187.ogg")
TING = load("ding/kenney-interface-glass-001.ogg"); TRI = load("ding/fs-349504-triangle-open-04.ogg")
HIT = load("impact/fs-347561-micheal-bay-hit.ogg")
# ---- synth voices
def k808(at, m=33, d=0.9, g=1.0):
    x = tt(d); f = nf(m) * (1 + 2.5 * np.exp(-x * 40)); s = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR))
    add(s * np.minimum(1, x / 0.003) * np.exp(-x / (d * 0.45)), at, 0.55 * g)
def clap(at, g=1.0):
    x = tt(0.3); n = rng.standard_normal(len(x)); n = n - lpf(n, 6)
    e = sum(np.exp(-np.maximum(0, x - o) * 60) * (x >= o) for o in (0, 0.011, 0.022)) / 3 + np.exp(-x * 14) * 0.6
    add(n * e, at, 0.38 * g)
def hat(at, g=1.0, open_=False):
    d = 0.16 if open_ else 0.035; x = tt(d); s = rng.standard_normal(len(x)); s = s - lpf(s, 3)
    add(s * np.exp(-x * (16 if open_ else 90)), at, 0.11 * g, pan=0.3)
def bell(at, m, g=1.0, d=1.2):
    x = tt(d); s = np.sin(2 * np.pi * nf(m) * x) + 0.4 * np.sin(2 * np.pi * nf(m) * 2.76 * x) * np.exp(-x * 6)
    add(s * env(d, 0.003, 0.45), at, 0.09 * g, pan=-0.25)
B = 0.5; e16 = B / 4
CUTS = [49, 97, 145]; SNAPS = [103, 115, 127]; GRIN = 168; GLINT = 206
# 808 line per 2-bar phrase (beats): root A1, minor feel
LINE = [(0, 33), (1.5, 33), (2.75, 36), (4, 31), (5.5, 31), (6.5, 28)]
MOTIF = [(0, 69), (0.75, 72), (1.5, 76), (2.5, 74), (4, 69), (4.75, 72), (5.5, 79), (6.5, 77)]
end_beat = GRIN / FPS
t0 = 0.5                                                          # a half-beat breath before the drop
for ph in range(0, 6):
    base = t0 + ph * 8 * B
    for b, m in LINE:
        at = base + b * B
        if at < end_beat: k808(at, m)
    for b, m in MOTIF:
        at = base + b * B
        if at < end_beat + 1: bell(at, m, 0.9 if ph else 0.6)
    for b in (2, 6):
        at = base + b * B
        if at < end_beat: clap(at)
    for i in range(32):
        at = base + i * e16 * 2
        if at >= end_beat: break
        roll = (i % 8 == 7) and ph % 2 == 1
        if roll:
            for r_ in range(4): hat(at + r_ * e16 / 2, 0.7)       # trap roll
        else: hat(at, 1.0 if i % 2 == 0 else 0.6, open_=(i % 16 == 14))
# cuts: whoosh leads into the cut, small sub hit on it
for c in CUTS:
    at = c / FPS; add(WHOOSH, max(0, at - min(0.35, len(WHOOSH) / SR * 0.6)), 0.45); k808(at, 28, 0.5, 0.7)
# jaw snaps: tooth clack at each close
for f in SNAPS: add(CLACK, (f + 5) / FPS, 0.55, pan=0.1)
# grin: drop-out, a low swelling sub + reversed shimmer into the glint
x = tt(1.6); add(np.sin(2 * np.pi * 41 * x) * np.minimum(1, x / 0.4) * np.exp(-x / 2.5), GRIN / FPS, 0.18)
sh = lpf(rng.standard_normal(int(SR * 1.3)), 2); sh = sh - lpf(sh, 8); add(sh * (np.linspace(0, 1, len(sh)) ** 3), GLINT / FPS - 1.3, 0.12)
add(TING, GLINT / FPS + 0.15, 0.7, pan=-0.15); add(TRI, GLINT / FPS + 0.2, 0.35, pan=0.2)
bell(GLINT / FPS + 0.2, 81, 1.2, 2.5); bell(GLINT / FPS + 0.2, 88, 0.6, 2.5)
# last beat: hit + 808 on the final hold
add(HIT, 228 / FPS, 0.6); k808(228 / FPS, 33, 1.4, 1.1)
fade = np.ones(N); fade[-int(SR * 0.4):] = np.linspace(1, 0, int(SR * 0.4)); L *= fade; R *= fade
st = np.stack([L, R], 1)
def upsample4(x):
    n = len(x); X = np.fft.rfft(x); Y = np.zeros(n * 2 + 1, complex); Y[:len(X)] = X
    return np.fft.irfft(Y, n * 4) * 4
def limit(st, ceil):
    pk = np.maximum(np.abs(upsample4(st[:, 0])), np.abs(upsample4(st[:, 1]))).reshape(-1, 4).max(1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    la = int(0.003 * SR); g = np.minimum.reduce([np.roll(g, -k) for k in range(la)])
    rel = np.exp(-1 / (0.06 * SR)); out = np.empty_like(g); y = 1.0
    for i, v in enumerate(g): y = v if v < y else v + (y - v) * rel; out[i] = y
    return st * out[:, None]
st = st / np.sqrt((st ** 2).mean()) * 10 ** (GAIN_DB / 20)
for _ in range(2): st = limit(st, 10 ** (-2.2 / 20))
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1], DUR, "s")
