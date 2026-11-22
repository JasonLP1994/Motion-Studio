# Mutant moving cover sound, made from scratch in numpy (no samples). 288 frames at 24 fps (12 s), stereo.
# 0-6.2 s close-ups: dark sub pulse, a liquid-metal stretch on every spike start, whooshes on the shot cuts
# (f37/73/109), wet pops as holes tear (f100-180). f149 reveal: riser into the masthead hit (f158), 120 BPM
# fashion-tech kick + hats, digital glitch bursts exactly on the type glitches, big slam on BEYOND FLESH (f198),
# glitch-out f222-230 then the beat drops away to a shimmering chrome tail under the head-alone end shot.
import numpy as np, wave, sys
SR, FPS, N = 48000, 24, 288
t = np.arange(int(SR * N / FPS)) / SR
L = np.zeros_like(t); R = np.zeros_like(t); rng = np.random.default_rng(23)
F = lambda f: f / FPS
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), len(t) - i)
    if n > 0:
        L[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 - pan)); R[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 + pan))
def band(n, lo, hi):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)
def tt(d): return np.arange(int(SR * d)) / SR

# dark drone under the close-ups (F#1 + C#2, slow beating), ducks out at the reveal
d = tt(F(152)); env = np.clip(d / 1.0, 0, 1) * np.clip((F(152) - d) / 0.3, 0, 1)
drone = (np.sin(2 * np.pi * 46.25 * d) + 0.6 * np.sin(2 * np.pi * 69.3 * d + 0.4 * np.sin(2 * np.pi * 0.3 * d))) * env
add(drone, 0, 0.32)
# heartbeat sub pulses during the close-ups (half-time of the 120 BPM grid: every 24 frames)
for fr in range(6, 149, 24):
    x = tt(0.4); add(np.sin(2 * np.pi * (70 * np.exp(-x * 14) + 38) * x) * np.exp(-x * 8), F(fr), 0.6)
# liquid-metal stretch on each spike start: resonant glide up with a metallic ring
for k, fr in enumerate([4, 14, 34, 40, 46, 66, 72, 80, 96, 104, 110, 116, 124]):
    x = tt(1.1); f0 = 180 + 40 * (k % 4); fq = f0 * (1 + 1.6 * (1 - np.exp(-x * 3)))
    ph = 2 * np.pi * np.cumsum(fq) / SR
    sig = (np.sin(ph) + 0.4 * np.sin(2.76 * ph) + 0.25 * np.sin(5.4 * ph)) * (1 - np.exp(-x * 25)) * np.exp(-x * 2.6)
    add(sig, F(fr), 0.10, ((k * 37) % 9 - 4) / 5)
# whooshes into each shot cut
for fr in (37, 73, 109, 149):
    x = tt(0.45); add(band(len(x), 300, 7000) * (x / 0.45) ** 2.5, F(fr) - 0.45, 0.35, 0.3 if fr % 2 else -0.3)
# wet pops as the holes tear open
for k in range(26):
    fr = 100 + k * 3 + rng.integers(0, 3); x = tt(0.07)
    add(np.sin(2 * np.pi * (900 + 600 * rng.random()) * x * (1 - x * 6)) * np.exp(-x * 60), F(fr), 0.12, rng.uniform(-0.7, 0.7))
# riser into the reveal, masthead hit f158
x = tt(F(158) - F(128)); add(band(len(x), 500, 10000) * (x / x[-1]) ** 3, F(128), 0.4)
x = tt(1.6); add(np.sin(2 * np.pi * (55 * np.exp(-x * 5) + 34) * x) * np.exp(-x * 2.2), F(158), 1.0)
add(band(len(tt(0.25)), 2000, 12000) * np.exp(-tt(0.25) * 18), F(158), 0.5)
# 120 BPM beat from the reveal until the glitch-out (12 frames a beat)
for fr in range(158, 222, 12):
    x = tt(0.35); add(np.sin(2 * np.pi * (110 * np.exp(-x * 30) + 45) * x) * np.exp(-x * 9), F(fr), 0.8)   # kick
    add(band(len(tt(0.04)), 7000, 14000) * np.exp(-tt(0.04) * 90), F(fr + 6), 0.25, 0.4)                 # off-beat hat
for fr in range(170, 222, 24):
    add(band(len(tt(0.18)), 900, 6000) * np.exp(-tt(0.18) * 22), F(fr), 0.45, -0.2)                      # clap on 2 and 4
# bass line under the cover (F# minor root/fifth), stops at the glitch-out
for i, fr in enumerate(range(158, 222, 6)):
    x = tt(F(6)); f0 = [46.25, 46.25, 69.3, 46.25, 55.0, 46.25, 69.3, 61.7][i % 8]
    add(np.tanh(3 * np.sin(2 * np.pi * f0 * x)) * np.exp(-x * 6), F(fr), 0.22)
# digital glitch bursts on the type glitches (bit-crushed noise + stutter)
def glitch(fr, frames, g):
    x = tt(F(frames)); n = band(len(x), 800, 12000)
    step = 40 + rng.integers(0, 120); n = np.repeat(n[::step], step)[:len(x)]                             # sample-and-hold crunch
    gate = (np.floor(x * (30 + rng.integers(0, 40))) % 2)                                                 # stutter
    add(np.sign(n) * np.abs(n) ** 0.5 * gate * 0.5, F(fr), g, rng.uniform(-0.6, 0.6))
for fr, d in [(150, 6), (158, 10), (176, 5), (184, 4), (198, 7), (209, 3), (216, 3)]: glitch(fr, d, 0.35)
glitch(222, 8, 0.6)
# BEYOND FLESH slam f198
x = tt(1.8); add(np.sin(2 * np.pi * (48 * np.exp(-x * 4) + 32) * x) * np.exp(-x * 1.8), F(198), 1.0)
add(band(len(tt(0.4)), 1500, 9000) * np.exp(-tt(0.4) * 10), F(198), 0.5)
# head alone (straight on): shimmering chrome bed (F# major add9), cut dead by the black-and-white glitch
x = tt(F(249) - F(230))
for f0, g, p in [(185, 0.12, -0.3), (233.1, 0.1, 0.3), (277.2, 0.1, -0.1), (370, 0.07, 0.2), (415.3, 0.05, -0.4)]:
    add(np.sin(2 * np.pi * f0 * x + 0.3 * np.sin(2 * np.pi * 5.5 * x)) * (1 - np.exp(-x * 6)), F(230), g, p)
add(band(len(x), 6000, 15000) * (1 - np.exp(-x * 4)), F(230), 0.06)
# black-and-white glitch f249-258: heavy crunch, then the logo hit f258 (sub + bright ping) and a clean tail to 12 s
glitch(249, 9, 0.75)
x = tt(12 - F(258))
add(np.sin(2 * np.pi * (52 * np.exp(-x * 5) + 33) * x) * np.exp(-x * 1.6), F(258), 1.0)
for f0, g in [(1480, 0.12), (2220, 0.07), (2960, 0.04)]: add(np.sin(2 * np.pi * f0 * x) * np.exp(-x * 2.2), F(258), g)
add(np.sin(2 * np.pi * 92.5 * x) * (1 - np.exp(-x * 3)) * np.exp(-x * 0.9), F(258), 0.18)
fade = np.clip((12 - t) / 0.35, 0, 1); L *= fade; R *= fade
st = np.tanh(np.stack([L, R], 1) * 1.15) / np.tanh(1.15); st = st / np.abs(st).max() * 0.9
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1])
