# Breaking dance soundtrack (original, numpy, no samples): 18 s = 15.33 s dance (368 frames @ 24 fps) + 2.67 s logo card.
# 120 BPM boom-bap breakbeat (beat = 12 frames) with a funky bass line, vinyl-scratch stabs + impacts on every camera cut,
# "zoom" swells on the snap zooms (shot B, every beat 2.5-4.0 s), a riser into the crash zoom (13.6-14.0 s), a drop-out on the
# face push, then a big hit + chord on the logo (15.33 s). True-peak limited (oversampled) to about -14 LUFS.
# Usage: GAIN_DB=-12 python3 scripts/dance_audio.py OUT.wav
import sys, wave, os
import numpy as np
SR, DUR = 48000, 18.0
GAIN_DB = float(os.environ.get("GAIN_DB", "-12.0"))
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(23)
FPS = 24; B = 0.5
CUTS = [61, 97, 177, 273, 337]; LOGO = 368 / FPS
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * g * (1 - max(0, pan)); R[i:i + n] += sig[:n] * g * (1 + min(0, pan))
def tt(d): return np.arange(int(SR * d)) / SR
def env(d, a=0.002, r=0.1): x = tt(d); return np.minimum(1, x / a) * np.exp(-x / r)
def lpf(x, k): return np.convolve(x, np.ones(k) / k, mode='same')
nf = lambda m: 440 * 2 ** ((m - 69) / 12)
def kick(at, g=1.0): x = tt(0.35); add(np.sin(2 * np.pi * (150 * np.exp(-x * 30) + 45) * x) * np.exp(-x * 7), at, 0.9 * g)
def snare(at, g=1.0):
    x = tt(0.25); add((lpf(rng.standard_normal(len(x)), 2) * 0.8 + np.sin(2 * np.pi * 190 * x) * 0.4) * np.exp(-x * 16), at, 0.42 * g)
def hat(at, g=1.0, open_=False):
    d = 0.18 if open_ else 0.04; x = tt(d); s = rng.standard_normal(len(x)); s = s - lpf(s, 3)
    add(s * np.exp(-x * (14 if open_ else 70)), at, 0.12 * g, pan=0.25)
def bass(at, m, d=0.24):
    x = tt(d); s = np.sign(np.sin(2 * np.pi * nf(m) * x)) * 0.5 + np.sin(2 * np.pi * nf(m) * x) * 0.6
    add(lpf(s, 18) * env(d, 0.004, 0.16), at, 0.32)
def scratch(at, g=1.0):
    d = 0.22; x = tt(d); f = 600 + 900 * np.sin(2 * np.pi * 9 * x) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * rng.standard_normal(len(x)) * 0.3)
    add(lpf(s, 3) * env(d, 0.002, 0.08) * (np.sin(2 * np.pi * 18 * x) > -0.2), at, 0.22 * g, pan=-0.2)
def impact(at, g=1.0):
    x = tt(0.9); add(np.sin(2 * np.pi * (70 * np.exp(-x * 5) + 36) * x) * np.exp(-x * 3), at, 0.75 * g)
    add(lpf(rng.standard_normal(int(SR * 0.3)), 2) * env(0.3, 0.001, 0.06), at, 0.3 * g)
def swell(at, d, up=True, g=1.0):
    x = tt(d); s = lpf(rng.standard_normal(len(x)), 4); e = (x / d) ** 2 if up else np.exp(-x / (d / 3))
    add(s * e, at, 0.25 * g)
# ---- beat: boom-bap pattern per 2-bar phrase (16 eighths)
KP = [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1]          # kicks on eighths
SP = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1]          # snares (on 2 & 4, ghost at the end)
bassline = [40, 0, 40, 43, 0, 45, 0, 43, 40, 0, 47, 45, 43, 0, 38, 0]
end_dance = 368 / FPS
e8 = B / 2
for i in range(int(end_dance / e8)):
    at = i * e8; k = i % 16
    if 13.95 <= at < end_dance: continue                       # drop-out on the face push
    if at < 0.5: continue                                      # one-beat breath at the start
    if KP[k]: kick(at)
    if SP[k]: snare(at, 0.55 if k == 15 else 1.0)
    hat(at, 0.8 if k % 2 else 1.0, open_=(k == 7))
    if bassline[k] and at >= 2.0: bass(at, bassline[k])
# snap-zoom swells + extra kicks on each beat of shot B (frames 61-96)
for f in range(61, 97, 12): swell(f / FPS - 0.12, 0.12, True, 0.8); kick(f / FPS, 0.7)
# cuts: scratch stab + impact
for c in CUTS: scratch(c / FPS - 0.05); impact(c / FPS, 0.6)
# riser into the crash zoom, then the drop-out
swell(12.6, 1.05, True, 1.6)
x = tt(1.05); add(np.sin(2 * np.pi * (300 + 1500 * (x / 1.05) ** 2) * x) * (x / 1.05) * 0.3, 12.6, 0.4)
# face push: a held sub + heartbeat, then the logo hit
x = tt(1.33); add(np.sin(2 * np.pi * 41 * x) * np.minimum(1, x / 0.3), 14.0, 0.14)
for k in range(3): kick(14.1 + k * 0.42, 0.45)
impact(LOGO, 1.3); scratch(LOGO - 0.1, 1.2)
for i, m in enumerate([52, 59, 64, 67, 71]):
    x = tt(2.5); s = 2 * ((x * nf(m)) % 1) - 1; add(lpf(s, 14) * np.minimum(1, x / 0.02) * np.exp(-x / 1.4), LOGO, 0.07, pan=(i - 2) * 0.3)
fade = np.ones(N); fade[-int(SR * 0.5):] = np.linspace(1, 0, int(SR * 0.5)); L *= fade; R *= fade
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
