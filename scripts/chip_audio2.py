# NOVACHIP ident v2 sound, made from scratch in numpy (no samples). 216 frames at 24 fps (9 s).
# Shot 1 rising whoosh + pulse ticks, shot 2 swell on the energy ripple (f64), shot 3 impact + spark
# crackle when the lid locks (f140), shot 4 bright logo hit (f165) + shimmer during the light sweep.
import numpy as np, wave, sys
SR, FPS = 48000, 24
DUR = 216 / FPS
t = np.arange(int(SR * DUR)) / SR; out = np.zeros_like(t); rng = np.random.default_rng(11)
F = lambda f: f / FPS
def add(sig, at, g=1.0):
    i = int(at * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n] += sig[:n] * g
def band(d, lo, hi):
    n = rng.standard_normal(int(SR * d)); X = np.fft.rfft(n); f = np.fft.rfftfreq(len(n), 1 / SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(n))
# low drone bed under everything
ph = np.cumsum(np.full_like(t, 55.0)) / SR
out += (np.sin(2 * np.pi * ph) + 0.5 * np.sin(2 * np.pi * ph * 2.01)) * 0.08 * np.clip(t / 1.0, 0, 1) * np.where(t > F(200), np.exp(-(t - F(200)) * 2), 1)
# shot 1: whoosh rising (band-passed noise with rising centre) + pulse ticks
d = F(60); n = rng.standard_normal(int(SR * d)); X = np.fft.rfft(n); f = np.fft.rfftfreq(len(n), 1 / SR)
X *= np.exp(-((f - 900) / 1400) ** 2); w = np.fft.irfft(X, len(n)); tt = np.arange(len(w)) / SR
add(w * (tt / d) ** 1.6 * 2.5, 0)
for k in range(14):
    tt = np.arange(int(SR * 0.02)) / SR
    add(np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300) * 0.25, F(4 + k * 4))
# shot 2: swell on the ripple
tt = np.arange(int(SR * 1.6)) / SR
add(np.sin(2 * np.pi * (220 + 220 * tt) * tt) * np.sin(np.pi * tt / 1.6) * 0.3, F(64))
# shot 3: lid drop whoosh down, impact + spark crackle at lock (f140)
tt = np.arange(int(SR * (F(140) - F(118)))) / SR
add(band(len(tt) / SR, 300, 4000) * (tt / tt[-1]) ** 2 * 0.6, F(118))
tt = np.arange(int(SR * 1.4)) / SR
add(np.sin(2 * np.pi * (50 * np.exp(-tt * 4) + 32) * tt) * np.exp(-tt * 3) * 1.2, F(140))
add(band(0.3, 1500, 9000) * np.exp(-np.arange(int(SR * 0.3)) / SR * 14) * 0.5, F(140))
for k in range(40):
    tt = np.arange(int(SR * 0.012)) / SR
    add(band(0.012, 4000, 12000) * np.exp(-tt * 400) * rng.uniform(0.1, 0.4), F(140) + rng.uniform(0, 0.8))
# shot 4: logo hit (f165) + shimmer during the sweep (f168-198)
tt = np.arange(int(SR * 2.4)) / SR
add((np.sin(2 * np.pi * 880 * tt) + 0.6 * np.sin(2 * np.pi * 1320 * tt) + 0.4 * np.sin(2 * np.pi * 1760 * tt)) * np.exp(-tt * 1.6) * 0.18, F(165))
add(np.sin(2 * np.pi * (40 * np.exp(-tt * 3) + 30) * tt) * np.exp(-tt * 2.5) * 0.9, F(165))
d = F(198) - F(168); tt = np.arange(int(SR * d)) / SR
add(band(d, 6000, 14000) * np.sin(np.pi * tt / d) * 0.2, F(168))
out = np.tanh(out * 1.2) / np.tanh(1.2)
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((out / np.max(np.abs(out)) * 0.9 * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1])
