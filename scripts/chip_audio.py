# NOVACHIP ident sound, made from scratch in numpy: a rising filtered pad under the power-on sweep,
# a tick per trace ignition, and a sub impact on the logo reveal (frame 70 = 2.92 s at 24 fps).
import numpy as np, wave, sys
SR = 48000; DUR = 120 / 24
t = np.arange(int(SR * DUR)) / SR; out = np.zeros_like(t)
rng = np.random.default_rng(3)
def add(sig, at, g=1.0):
    i = int(at * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n] += sig[:n] * g
# pad: detuned saws rising from 110 Hz, low-passed by a rising cutoff (simple one-pole)
f = 110 * (1 + 0.6 * np.clip(t / 2.9, 0, 1) ** 2)
ph = np.cumsum(f) / SR
saw = lambda p: 2 * (p % 1) - 1
pad = saw(ph) + saw(ph * 1.007) + saw(ph * 0.994)
a = np.exp(-1 / (SR * 0.02 + 1e-9) * 0)  # placeholder to keep shape clear
y = np.zeros_like(pad); c = 0.0
for i in range(len(pad)):
    cut = 0.02 + 0.5 * min(1, t[i] / 2.9)
    c += cut * (pad[i] - c)
    y[i] = c
env = np.clip(t / 0.8, 0, 1) * np.where(t > 3.2, np.exp(-(t - 3.2) * 2.0), 1)
out += y * env * 0.22
# ticks as the sweep reaches each trace (18 traces across frames 24-60)
for k in range(18):
    at = (24 + k * 36 / 18) / 24
    tt = np.arange(int(SR * 0.03)) / SR
    add(rng.standard_normal(len(tt)) * np.exp(-tt * 260) * 0.5, at)
# logo reveal impact: sub boom + noise hit
tt = np.arange(int(SR * 1.2)) / SR
boom = np.sin(2 * np.pi * (48 * np.exp(-tt * 3) + 28) * tt) * np.exp(-tt * 3.2) * 1.0
add(boom, 70 / 24)
tn = np.arange(int(SR * 0.25)) / SR
add(rng.standard_normal(len(tn)) * np.exp(-tn * 22) * 0.35, 70 / 24)
out = np.tanh(out * 1.2) / np.tanh(1.2)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out / np.max(np.abs(out)) * 0.9 * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1])
