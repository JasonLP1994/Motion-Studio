# Lime phone case sound, made from scratch in numpy (no samples). 240 frames at 24 fps (10 s), stereo.
# 0-5.8 s mystery: dark pad that slowly opens + electric sizzle that follows the growth speed + sub pulses
# and a riser; f140 the riser sucks out; f144-160 phone slide whoosh, seat thud f160; ring click f172;
# f181 reveal hit (sub drop + bright chord) with a shimmer tail to the end.
import numpy as np, wave, sys
SR, FPS, N = 48000, 24, 240
t = np.arange(int(SR * N / FPS)) / SR
L = np.zeros_like(t); R = np.zeros_like(t); rng = np.random.default_rng(7)
F = lambda f: f / FPS
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), len(t) - i)
    if n > 0:
        L[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 - pan)); R[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 + pan))
def band(n, lo, hi):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)
def lp(x, a):  # one-pole low-pass with a per-sample coefficient (0..1)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
grow_u = np.clip((t * FPS - 4) / 136, 0, 1); speed = 6 * grow_u * (1 - grow_u)   # derivative of the growth smoothstep
myst = t < F(140)
# dark pad: detuned saws on A1 + E2, low-pass opens as the shell grows
saw = lambda f: 2 * ((t * f) % 1) - 1
pad = saw(55) + saw(55.3) + 0.7 * saw(82.4) + 0.7 * saw(82.1)
pad = lp(pad, 0.004 + 0.03 * grow_u ** 2) * np.clip(t / 1.2, 0, 1) * np.where(myst, 1, np.exp(-(t - F(140)) * 6))
add(pad, 0, 0.35, -0.2); add(np.roll(pad, 240), 0, 0.35, 0.2)
# sizzle: crackle grains whose density and loudness follow the growth speed (the glowing front)
for k in range(1400):
    at = rng.uniform(F(2), F(140)); s = speed[int(at * SR)]
    if rng.random() > 0.15 + 0.85 * s / 1.5: continue
    n = int(SR * rng.uniform(0.004, 0.02)); tt = np.arange(n) / SR
    add(band(n, 2500, 11000) * np.exp(-tt * rng.uniform(150, 500)), at, rng.uniform(0.05, 0.22) * (0.3 + s), rng.uniform(-0.8, 0.8))
# electric hum that swells with the growth
add(np.sin(2 * np.pi * 110 * t + 0.6 * np.sin(2 * np.pi * 220 * t)) * speed / 1.5 * myst, 0, 0.06)
# sub pulses (heartbeat), speeding up through the mystery
beat = 0.0; bt = F(12)
while bt < F(136):
    tt = np.arange(int(SR * 0.35)) / SR
    add(np.sin(2 * np.pi * (60 * np.exp(-tt * 12) + 42) * tt) * np.exp(-tt * 9), bt, 0.55)
    bt += 0.75 - 0.4 * (bt / F(136))
# riser into f140, then a hard suck-out
d = F(140) - F(92); tt = np.arange(int(SR * d)) / SR
add(band(len(tt), 400, 9000) * (tt / d) ** 3, F(92), 0.5)
add(np.sin(2 * np.pi * np.cumsum(180 + 900 * (tt / d) ** 2) / SR) * (tt / d) ** 2, F(92), 0.08)
# phone slide whoosh f144-160 + seat thud f160
d = F(160) - F(144); tt = np.arange(int(SR * d)) / SR
add(band(len(tt), 200, 3000) * np.sin(np.pi * tt / d) ** 2, F(144), 0.45, 0.3)
tt = np.arange(int(SR * 0.4)) / SR
add(np.sin(2 * np.pi * (90 * np.exp(-tt * 20) + 55) * tt) * np.exp(-tt * 14), F(160), 0.6)
# ring click f172 (metal snap + tiny ring)
tt = np.arange(int(SR * 0.6)) / SR
add(band(len(tt), 3000, 14000) * np.exp(-tt * 120), F(172), 0.6)
add((np.sin(2 * np.pi * 2350 * tt) + 0.5 * np.sin(2 * np.pi * 3710 * tt)) * np.exp(-tt * 9), F(172), 0.12)
# reveal f181: sub drop + bright chord (A major, lime-bright) + shimmer tail
tt = np.arange(int(SR * (10 - F(181)))) / SR
add(np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-tt * 3)) / SR) * np.exp(-tt * 1.1), F(181), 0.9)
for f0, g, p in [(220, 0.18, -0.3), (277.2, 0.14, 0.3), (329.6, 0.14, -0.1), (440, 0.1, 0.1), (659.3, 0.06, 0.4)]:
    add((np.sin(2 * np.pi * f0 * tt) + 0.3 * np.sin(2 * np.pi * f0 * 2.002 * tt)) * (1 - np.exp(-tt * 30)) * np.exp(-tt * 0.55), F(181), g, p)
add(band(len(tt), 7000, 15000) * np.exp(-tt * 0.9) * (1 - np.exp(-tt * 8)), F(181), 0.12, 0.5)
add(band(len(tt), 7000, 15000) * np.exp(-tt * 0.9) * (1 - np.exp(-tt * 8)), F(181), 0.12, -0.5)
fade = np.clip((10 - t) / 0.6, 0, 1); L *= fade; R *= fade
st = np.tanh(np.stack([L, R], 1) * 1.1) / np.tanh(1.1); st = st / np.abs(st).max() * 0.9
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1])
