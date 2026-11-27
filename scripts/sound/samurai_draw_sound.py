"""Samurai katana-draw shot soundtrack (5 s, 30 fps), synthesised and timed to scripts/blender/samurai_draw_shot.py
(draw keys + 20-frame lead): drone, cloth rustle on the reach, grip click, metallic 'shing' as the blade slides out
and rings free, whoosh on the cut + light-stutter crackle, follow-through whoosh, chiburi snap, blade energy hum,
eyes-ignite swell with a low hit. Writes a raw mix; loudness is set to about -14 LUFS afterwards.
  tools/ai-venv/bin/python scripts/sound/samurai_draw_sound.py <out_raw.wav>
"""
import sys, wave
import numpy as np

SR, FPS, NF = 48000, 30, 150
N = int(SR * NF / FPS) + SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.RandomState(7)
EV = dict(reach=(33, 46), grip=46, slide=(47, 64), clear=64, cut=71, stutter=[71, 73], follow=(76, 81), snap=87, hum=87, eyes=112)


def f2t(f): return (f - 1) / FPS
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain; L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, k):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
def shape(n, pts):
    xs, ys = zip(*pts); return np.interp(np.linspace(0, 1, n), xs, ys)
def bp(x, k_lo, k_hi):            # crude band-pass: lp(high) - lp(low)
    return lp(x, k_hi) - lp(x, k_lo)
def whoosh(dur, k0, k1, peak=0.6):
    n = int(dur * SR); x = rng.randn(n); k = np.linspace(k0, k1, n); y = np.empty(n); acc = 0.0
    for i in range(n): acc += k[i] * (x[i] - acc); y[i] = acc
    return y * shape(n, [(0, 0), (peak, 1), (1, 0)]) ** 1.5


# drone + dark air under everything
n = int(f2t(NF + 1) * SR); t = np.arange(n) / SR
drone = 0.5 * np.sin(2 * np.pi * 36.7 * t) + 0.35 * np.sin(2 * np.pi * 37.2 * t + 1) + 0.6 * lp(rng.randn(n), 0.008)
add(drone * shape(n, [(0, 0), (0.08, 0.8), (0.42, 0.9), (0.47, 0.5), (0.75, 1.0), (1, 0.8)]), 0, 0.30)

# cloth rustle on the reach, grip click
a, b = EV["reach"]; n = int((f2t(b) - f2t(a)) * SR); add(bp(rng.randn(n), 0.05, 0.35) * shape(n, [(0, 0), (0.5, 1), (1, 0.2)]), f2t(a), 0.10, pan=-0.2)
m = int(0.12 * SR); tm = np.arange(m) / SR
add((np.sin(2 * np.pi * 180 * tm) * env(m, 0.0005, 0.02) + 0.6 * bp(rng.randn(m), 0.2, 0.9) * env(m, 0.0003, 0.008)), f2t(EV["grip"]), 0.45, pan=0.25)

# the 'shing': rising metallic scrape (band-passed noise + inharmonic partials), ringing free at the clear
a, b = EV["slide"]; n = int((f2t(b) - f2t(a)) * SR); t = np.arange(n) / SR
scrape = bp(rng.randn(n), 0.15, 0.85) * shape(n, [(0, 0), (0.15, 0.6), (0.85, 1.0), (1, 0.9)])
part = sum(amp * np.sin(2 * np.pi * f * (1 + 0.04 * t / t[-1]) * t) for f, amp in ((2150, 1.0), (3420, 0.6), (5230, 0.35), (7110, 0.2)))
add(scrape * 0.7 + part * 0.25 * shape(n, [(0, 0), (0.3, 0.4), (1, 1)]), f2t(a), 0.32, pan=0.2)
m = int(1.6 * SR); tm = np.arange(m) / SR
ring = sum(amp * np.sin(2 * np.pi * f * tm) * np.exp(-tm / dec) for f, amp, dec in ((2210, 1.0, 0.55), (3510, 0.6, 0.38), (5370, 0.4, 0.25), (8020, 0.2, 0.15)))
add(ring, f2t(EV["clear"]), 0.18, pan=0.1)

# cut whoosh (peaks on the cut frame) + light stutter crackle
add(whoosh(0.45, 0.02, 0.5, peak=0.62), f2t(EV["cut"]) - 0.28, 0.55, pan=-0.3)
for f in EV["stutter"]:
    m = int(0.08 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * 100 * tm)) * lp(rng.randn(m), 0.5) * env(m, 0.001, 0.03), f2t(f), 0.18, pan=rng.uniform(-0.4, 0.4))

# follow-through + chiburi snap
a, b = EV["follow"]; add(whoosh(f2t(b) - f2t(a) + 0.15, 0.03, 0.3, peak=0.5), f2t(a), 0.30, pan=-0.5)
add(whoosh(0.22, 0.05, 0.7, peak=0.85), f2t(EV["snap"]) - 0.19, 0.45, pan=-0.4)
m = int(0.25 * SR); tm = np.arange(m) / SR
add(np.tanh(3 * (bp(rng.randn(m), 0.1, 0.95) * env(m, 0.0003, 0.012) + 0.5 * np.sin(2 * np.pi * 95 * tm) * env(m, 0.001, 0.06))), f2t(EV["snap"]), 0.55, pan=-0.3)

# blade energy hum while holding
n = int((f2t(NF + 1) - f2t(EV["hum"])) * SR); t = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 110 * t) + 0.4 * np.sin(2 * np.pi * 220.7 * t) + 0.2 * np.sin(2 * np.pi * 331 * t)) * (1 + 0.15 * np.sin(2 * np.pi * 5.3 * t))
add(hum * shape(n, [(0, 0), (0.12, 0.8), (1, 1.0)]), f2t(EV["hum"]), 0.05, pan=-0.2)

# eyes ignite: swell into a low hit + bright chirp
n = int(0.8 * SR); t = np.arange(n) / SR; fr = 180 + 520 * (t / t[-1]) ** 2; ph = 2 * np.pi * np.cumsum(fr) / SR
add((np.sin(ph) + 0.4 * np.sin(1.5 * ph)) * shape(n, [(0, 0), (0.8, 1), (1, 0)]), f2t(EV["eyes"]) - 0.75, 0.13)
m = int(2.2 * SR); tm = np.arange(m) / SR
boom = np.sin(2 * np.pi * (34 + 50 * np.exp(-tm / 0.10)) * tm) * env(m, 0.001, 0.8)
add(np.tanh(1.4 * boom), f2t(EV["eyes"]), 0.75)
m = int(0.4 * SR); tm = np.arange(m) / SR
add(np.sin(2 * np.pi * 1480 * tm) * env(m, 0.001, 0.12) + 0.3 * np.sin(2 * np.pi * 2960 * tm) * env(m, 0.001, 0.08), f2t(EV["eyes"]), 0.08)

mix = np.stack([L, R], 1)[: int(SR * NF / FPS)]
mix /= max(1e-6, np.abs(mix).max()) / 0.7
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("saved", sys.argv[1])
