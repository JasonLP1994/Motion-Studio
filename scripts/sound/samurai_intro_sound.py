"""Samurai intro soundtrack (15 s, 30 fps), fully synthesised and timed to scripts/blender/mech_samurai_intro2.py:
dark drone, electric crackles on each sword flicker, a rising hum as the glow sweeps up the katana, heavy light-switch
clunks with buzz stutters, whooshes on the section cuts, a swell as the eyes ignite, stutter + dropout before the
hero reveal, a deep impact and pad on the hero shot, then glitch zaps and a settle tone for the Phillips Digital card.
Writes a raw mix; loudness is set to about -14 LUFS by the finish script.
  tools/ai-venv/bin/python scripts/sound/samurai_intro_sound.py <out_raw.wav>
"""
import sys, wave
import numpy as np

SR, FPS, NF = 48000, 30, 450
N = int(SR * NF / FPS) + SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.RandomState(21)
SWORD_ON = [15, 24, 27, 41, 44, 61]                                   # frames the swords flick on (match CFG sword_glow)
BANGS = [136, 140, 144, 148]; BANG_FLICK = [0, 3, 6, 9, 13, 20]
PRE = [264, 267, 271, 275]; HERO = 281; EYES = 260; CUTS = [171, 206, 241]


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
def tone(f, d, harm=(1, 0.5, 0.25)):
    t = np.arange(int(d * SR)) / SR; return sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm))

# dark drone under the action (two detuned lows + filtered noise), fades into the hero pad
n = int(f2t(361) * SR); t = np.arange(n) / SR
drone = 0.5 * np.sin(2 * np.pi * 41.2 * t) + 0.4 * np.sin(2 * np.pi * 41.7 * t + 1) + 0.25 * lp(rng.randn(n), 0.01) * 4
add(drone * shape(n, [(0, 0), (0.06, 0.8), (0.7, 1.0), (0.77, 0.4), (0.78, 1.1), (1, 0.6)]), 0, 0.35)

# sword flicker crackles: short electric zaps + low thunk
for f in SWORD_ON:
    m = int(0.18 * SR); tm = np.arange(m) / SR; x = rng.randn(m)
    zap = (x - lp(x, 0.4)) * env(m, 0.0005, 0.04) + 0.5 * np.sign(np.sin(2 * np.pi * 120 * tm)) * env(m, 0.001, 0.05)
    add(zap, f2t(f), 0.35, pan=0.3); add(tone(70, 0.3) * env(int(0.3 * SR), 0.002, 0.08), f2t(f), 0.25)

# glow sweep up the katana: rising hum + shimmer, locks on at 132
n = int((f2t(133) - f2t(61)) * SR); t = np.arange(n) / SR
fr = np.linspace(90, 360, n); ph = 2 * np.pi * np.cumsum(fr) / SR
hum = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * shape(n, [(0, 0), (0.15, 0.6), (0.95, 1.0), (1, 0.8)])
add(hum, f2t(61), 0.18, pan=0.25)
m = int(0.6 * SR); add(tone(720, 0.6, (1, 0.3)) * env(m, 0.002, 0.25), f2t(132), 0.12)

# lights bang on: heavy clunk + mains buzz stutters
for b in BANGS:
    m = int(0.5 * SR); tm = np.arange(m) / SR
    clunk = np.sin(2 * np.pi * (55 + 90 * np.exp(-tm / 0.02)) * tm) * env(m, 0.001, 0.12) + 0.6 * lp(rng.randn(m), 0.3) * env(m, 0.0005, 0.03)
    add(clunk, f2t(b), 0.7, pan=rng.uniform(-0.5, 0.5))
    for df in BANG_FLICK[1:]:
        m2 = int(0.07 * SR); tm2 = np.arange(m2) / SR
        add(np.sign(np.sin(2 * np.pi * 100 * tm2)) * lp(rng.randn(m2), 0.5) * env(m2, 0.001, 0.03), f2t(b + df), 0.12, pan=rng.uniform(-0.4, 0.4))
n = int((f2t(264) - f2t(150)) * SR); t = np.arange(n) / SR                   # steady hum while lit
add((np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)) * shape(n, [(0, 0), (0.05, 1), (0.95, 1), (1, 0)]), f2t(150), 0.03)

# section whooshes on cuts
for c in CUTS:
    m = int(0.5 * SR); x = rng.randn(m); k = np.linspace(0.04, 0.4, m); y = np.empty(m); acc = 0.0
    for i in range(m): acc += k[i] * (x[i] - acc); y[i] = acc
    add(y * np.sin(np.pi * np.arange(m) / m) ** 2, f2t(c) - 0.28, 0.28)

# eyes ignite: rising synth swell + bright chirp
n = int(0.9 * SR); t = np.arange(n) / SR; fr = 220 + 440 * (t / t[-1]) ** 2; ph = 2 * np.pi * np.cumsum(fr) / SR
add((np.sin(ph) + 0.4 * np.sin(1.5 * ph)) * shape(n, [(0, 0), (0.7, 1), (1, 0)]), f2t(EYES) - 0.6, 0.12)
add(tone(1320, 0.4, (1, 0.2)) * env(int(0.4 * SR), 0.001, 0.12), f2t(EYES), 0.1)

# pre-hero stutters, then a dropout and the big hit
for f in PRE:
    m = int(0.09 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * 100 * tm)) * lp(rng.randn(m), 0.5) * env(m, 0.001, 0.04), f2t(f), 0.2, pan=rng.uniform(-0.5, 0.5))
gap = slice(int(f2t(278) * SR), int(f2t(HERO) * SR)); L[gap] *= 0.15; R[gap] *= 0.15
m = int(3.0 * SR); tm = np.arange(m) / SR
boom = np.sin(2 * np.pi * (32 + 60 * np.exp(-tm / 0.12)) * tm) * env(m, 0.001, 1.1)
crack = lp(rng.randn(m), 0.6) * env(m, 0.0005, 0.06)
add(np.tanh(1.6 * (boom + 0.7 * crack)), f2t(HERO), 1.0)
n = int((f2t(361) - f2t(HERO)) * SR); t = np.arange(n) / SR                  # hero pad (minor chord), swells
pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((110, 130.8, 164.8, 220)))
add(pad * shape(n, [(0, 0), (0.15, 0.8), (0.9, 1.0), (1, 0.3)]), f2t(HERO), 0.06)

# glitch end card (361-450): zaps on the glitch frames, settle tone, small blip at 411
for f in list(range(361, 373, 2)) + [374, 376, 380, 384]:
    m = int(0.05 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * rng.uniform(300, 1800) * tm)) * env(m, 0.0005, 0.02), f2t(f), 0.22, pan=rng.uniform(-0.6, 0.6))
add(tone(880, 1.4, (1, 0.25, 0.1)) * env(int(1.4 * SR), 0.004, 0.5), f2t(378), 0.1)
add(np.sign(np.sin(2 * np.pi * 1200 * np.arange(int(0.06 * SR)) / SR)) * env(int(0.06 * SR), 0.0005, 0.02), f2t(411), 0.12)

mix = np.stack([L, R], 1)[: int(SR * NF / FPS)]
mix /= max(1e-6, np.abs(mix).max()) / 0.7
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("saved", sys.argv[1])
