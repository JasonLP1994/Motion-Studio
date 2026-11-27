"""Samurai intro v3 soundtrack (19.5 s, 30 fps): v1 sounds up to the helmet, then the katana draw (grip, slow-mo shing,
cut whoosh + stutter, follow-through, chiburi snap, blade hum, eye flare), flicker-out, hero hit and the glitch card.
Timed to scripts/blender/samurai_intro3.py. Based on the v1 soundtrack, fully synthesised and timed to scripts/blender/mech_samurai_intro2.py:
dark drone, electric crackles on each sword flicker, a rising hum as the glow sweeps up the katana, heavy light-switch
clunks with buzz stutters, whooshes on the section cuts, a swell as the eyes ignite, stutter + dropout before the
hero reveal, a deep impact and pad on the hero shot, then glitch zaps and a settle tone for the Phillips Digital card.
Writes a raw mix; loudness is set to about -14 LUFS by the finish script.
  tools/ai-venv/bin/python scripts/sound/samurai_intro3_sound.py <out_raw.wav>
"""
import sys, wave
import numpy as np

SR, FPS, NF = 48000, 30, 584
SH = 134                                                               # hero/end card moved later by the draw
N = int(SR * NF / FPS) + SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.RandomState(21)
SWORD_ON = [15, 24, 27, 41, 44, 61]                                   # frames the swords flick on (match CFG sword_glow)
BANGS = [136, 140, 144, 148]; BANG_FLICK = [0, 3, 6, 9, 13, 20]
PRE = [f + SH for f in (264, 267, 271, 275)]; HERO = 281 + SH; EYES = 260; CUTS = [171, 206, 241]
DRAW = dict(rustle=(266, 285), grip=285, slide=(288, 317), clear=317, cut=333, stutter=[334, 336], follow=(338, 345), snap=364, hum=364, flare=376)


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
n = int(f2t(361 + SH) * SR); t = np.arange(n) / SR
drone = 0.5 * np.sin(2 * np.pi * 41.2 * t) + 0.4 * np.sin(2 * np.pi * 41.7 * t + 1) + 0.25 * lp(rng.randn(n), 0.01) * 4
add(drone * shape(n, [(0, 0), (0.04, 0.8), (0.45, 1.0), (0.52, 0.7), (0.62, 1.0), (0.74, 1.1), (0.80, 0.4), (0.82, 1.1), (1, 0.6)]), 0, 0.35)

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
n = int((f2t(398) - f2t(150)) * SR); t = np.arange(n) / SR                   # steady hum while lit
add((np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)) * shape(n, [(0, 0), (0.03, 1), (0.97, 1), (1, 0)]), f2t(150), 0.03)

# section whooshes on cuts
for c in CUTS:
    m = int(0.5 * SR); x = rng.randn(m); k = np.linspace(0.04, 0.4, m); y = np.empty(m); acc = 0.0
    for i in range(m): acc += k[i] * (x[i] - acc); y[i] = acc
    add(y * np.sin(np.pi * np.arange(m) / m) ** 2, f2t(c) - 0.28, 0.28)

# eyes ignite: rising synth swell + bright chirp
n = int(0.9 * SR); t = np.arange(n) / SR; fr = 220 + 440 * (t / t[-1]) ** 2; ph = 2 * np.pi * np.cumsum(fr) / SR
add((np.sin(ph) + 0.4 * np.sin(1.5 * ph)) * shape(n, [(0, 0), (0.7, 1), (1, 0)]), f2t(EYES) - 0.6, 0.12)
add(tone(1320, 0.4, (1, 0.2)) * env(int(0.4 * SR), 0.001, 0.12), f2t(EYES), 0.1)


# ---------------- the katana draw (264-398) ----------------
def bp(x, k_lo, k_hi): return lp(x, k_hi) - lp(x, k_lo)
def whoosh(dur, k0, k1, peak=0.6):
    n = int(dur * SR); x = rng.randn(n); k = np.linspace(k0, k1, n); y = np.empty(n); acc = 0.0
    for i in range(n): acc += k[i] * (x[i] - acc); y[i] = acc
    return y * shape(n, [(0, 0), (peak, 1), (1, 0)]) ** 1.5
a, b = DRAW["rustle"]; n = int((f2t(b) - f2t(a)) * SR); add(bp(rng.randn(n), 0.05, 0.35) * shape(n, [(0, 0), (0.6, 1), (1, 0.2)]), f2t(a), 0.10, pan=-0.2)
m = int(0.14 * SR); tm = np.arange(m) / SR
add(np.sin(2 * np.pi * 170 * tm) * env(m, 0.0005, 0.025) + 0.6 * bp(rng.randn(m), 0.2, 0.9) * env(m, 0.0003, 0.008), f2t(DRAW["grip"]), 0.5, pan=0.25)
a, b = DRAW["slide"]; n = int((f2t(b) - f2t(a)) * SR); t = np.arange(n) / SR      # slow-mo shing: lower, longer partials
scrape = bp(rng.randn(n), 0.10, 0.75) * shape(n, [(0, 0), (0.15, 0.6), (0.85, 1.0), (1, 0.9)])
part = sum(amp * np.sin(2 * np.pi * f * (1 + 0.05 * t / t[-1]) * t) for f, amp in ((1650, 1.0), (2620, 0.6), (4010, 0.35), (5450, 0.2)))
add(scrape * 0.7 + part * 0.25 * shape(n, [(0, 0), (0.3, 0.4), (1, 1)]), f2t(a), 0.34, pan=0.2)
m = int(2.0 * SR); tm = np.arange(m) / SR
add(sum(amp * np.sin(2 * np.pi * f * tm) * np.exp(-tm / dec) for f, amp, dec in ((2210, 1.0, 0.7), (3510, 0.6, 0.45), (5370, 0.4, 0.3), (8020, 0.2, 0.18))), f2t(DRAW["clear"]), 0.2, pan=0.1)
add(whoosh(0.5, 0.02, 0.5, peak=0.64), f2t(DRAW["cut"]) - 0.32, 0.6, pan=-0.3)
m = int(1.2 * SR); tm = np.arange(m) / SR                                           # impact thump under the cut
add(np.tanh(1.5 * np.sin(2 * np.pi * (40 + 70 * np.exp(-tm / 0.05)) * tm) * env(m, 0.001, 0.35)), f2t(DRAW["cut"]), 0.55)
for f in DRAW["stutter"]:
    m = int(0.08 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * 100 * tm)) * lp(rng.randn(m), 0.5) * env(m, 0.001, 0.03), f2t(f), 0.2, pan=rng.uniform(-0.4, 0.4))
a, b = DRAW["follow"]; add(whoosh(f2t(b) - f2t(a) + 0.15, 0.03, 0.3, peak=0.5), f2t(a), 0.3, pan=-0.5)
add(whoosh(0.22, 0.05, 0.7, peak=0.85), f2t(DRAW["snap"]) - 0.19, 0.45, pan=-0.4)
m = int(0.25 * SR); tm = np.arange(m) / SR
add(np.tanh(3 * (bp(rng.randn(m), 0.1, 0.95) * env(m, 0.0003, 0.012) + 0.5 * np.sin(2 * np.pi * 95 * tm) * env(m, 0.001, 0.06))), f2t(DRAW["snap"]), 0.6, pan=-0.3)
n = int((f2t(HERO + 80) - f2t(DRAW["hum"])) * SR); t = np.arange(n) / SR              # blade hum (ducks in the dropout)
hum = (np.sin(2 * np.pi * 110 * t) + 0.4 * np.sin(2 * np.pi * 220.7 * t) + 0.2 * np.sin(2 * np.pi * 331 * t)) * (1 + 0.15 * np.sin(2 * np.pi * 5.3 * t))
add(hum * shape(n, [(0, 0), (0.08, 0.8), (1, 1.0)]), f2t(DRAW["hum"]), 0.05, pan=-0.2)
n = int(0.6 * SR); t = np.arange(n) / SR; fr = 300 + 600 * (t / t[-1]) ** 2; ph = 2 * np.pi * np.cumsum(fr) / SR
add((np.sin(ph) + 0.4 * np.sin(1.5 * ph)) * shape(n, [(0, 0), (0.8, 1), (1, 0)]), f2t(DRAW["flare"]) - 0.5, 0.1)

# pre-hero stutters, then a dropout and the big hit
for f in PRE:
    m = int(0.09 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * 100 * tm)) * lp(rng.randn(m), 0.5) * env(m, 0.001, 0.04), f2t(f), 0.2, pan=rng.uniform(-0.5, 0.5))
gap = slice(int(f2t(278 + SH) * SR), int(f2t(HERO) * SR)); L[gap] *= 0.15; R[gap] *= 0.15
m = int(3.0 * SR); tm = np.arange(m) / SR
boom = np.sin(2 * np.pi * (32 + 60 * np.exp(-tm / 0.12)) * tm) * env(m, 0.001, 1.1)
crack = lp(rng.randn(m), 0.6) * env(m, 0.0005, 0.06)
add(np.tanh(1.6 * (boom + 0.7 * crack)), f2t(HERO), 1.0)
n = int((f2t(361 + SH) - f2t(HERO)) * SR); t = np.arange(n) / SR                  # hero pad (minor chord), swells
pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((110, 130.8, 164.8, 220)))
add(pad * shape(n, [(0, 0), (0.15, 0.8), (0.9, 1.0), (1, 0.3)]), f2t(HERO), 0.06)

# glitch end card (361-450): zaps on the glitch frames, settle tone, small blip at 411
for f in [x + SH for x in list(range(361, 373, 2)) + [374, 376, 380, 384]]:
    m = int(0.05 * SR); tm = np.arange(m) / SR
    add(np.sign(np.sin(2 * np.pi * rng.uniform(300, 1800) * tm)) * env(m, 0.0005, 0.02), f2t(f), 0.22, pan=rng.uniform(-0.6, 0.6))
add(tone(880, 1.4, (1, 0.25, 0.1)) * env(int(1.4 * SR), 0.004, 0.5), f2t(378 + SH), 0.1)
add(np.sign(np.sin(2 * np.pi * 1200 * np.arange(int(0.06 * SR)) / SR)) * env(int(0.06 * SR), 0.0005, 0.02), f2t(411 + SH), 0.12)

mix = np.stack([L, R], 1)[: int(SR * NF / FPS)]
mix /= max(1e-6, np.abs(mix).max()) / 0.7
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("saved", sys.argv[1])
