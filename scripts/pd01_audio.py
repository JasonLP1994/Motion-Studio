# PD-01 soundtrack (original, numpy, no samples): 15 s synthwave score + SFX locked to the picture (24 fps, 360 frames).
# 120 BPM (beat = 0.5 s = 12 frames), A minor. Mystery 0-9 s (sub drone, pad swell, arp from 1.5 s, bass from 4.5 s), power-on
# crackles + hit (shot 4), HUD boot blips + key clicks (6-7.5 s), riser 7.5-9 s, reveal whoosh + sub drop + full DROP at 9 s
# (drums, saw bass, chords), neon buzz under the outline (11.6-12.6 s), glitch ticks on every cut, logo impact at 13.17 s and a
# final chord tail. Stereo. Usage: python3 scripts/pd01_audio.py OUT.wav   (then loudness to -14 LUFS with ffmpeg)
import sys, wave
import numpy as np
SR, DUR = 48000, 15.0
N = int(SR * DUR); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(11)
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * g * (1 - max(0, pan)); R[i:i + n] += sig[:n] * g * (1 + min(0, pan))
def tt(d): return np.arange(int(SR * d)) / SR
def env(d, a=0.005, r=0.2): x = tt(d); return np.minimum(1, x / a) * np.exp(-x / r)
def adsr(d, a, rl): x = tt(d); return np.minimum(1, x / a) * np.minimum(1, (d - x) / rl).clip(0, 1)
def saw(f, d, det=0.0):
    x = tt(d); s = 2 * ((x * f) % 1) - 1
    if det: s = 0.5 * s + 0.5 * (2 * ((x * f * (1 + det)) % 1) - 1)
    return s
def lp(sig, a):                       # one-pole low-pass
    out = np.empty_like(sig); y = 0.0
    for i, v in enumerate(sig): y += a * (v - y); out[i] = y
    return out
def lp_fast(sig, k=8):                # cheap moving-average low-pass for long tones
    return np.convolve(sig, np.ones(k) / k, mode='same')
nf = lambda m: 440 * 2 ** ((m - 69) / 12)
B = 0.5
# ---- 0-9 s mystery: sub drone + pad swell (Am - F - C - G over 9 s)
x = tt(DUR); add(np.sin(2 * np.pi * 55 * x) * np.minimum(1, x / 2.5) * (x < 9.05), 0, 0.22)
chords = [(0.0, [57, 60, 64]), (2.25, [53, 57, 60]), (4.5, [48, 52, 55]), (6.75, [55, 59, 62])]
for at, ch in chords:
    for i, m in enumerate(ch):
        s = lp_fast(saw(nf(m), 2.4, 0.004), 24) * adsr(2.4, 0.9, 0.8)
        add(s, at, 0.035 + 0.03 * (at / 9), pan=(i - 1) * 0.4)
# arp from 1.5 s (16ths, filtered, building)
arp = [69, 72, 76, 72, 81, 76, 72, 76]
for k in range(int((9.0 - 1.5) / (B / 4))):
    at = 1.5 + k * B / 4; m = arp[k % 8] - (5 if 2.25 <= at < 4.5 else 0) - (9 if 4.5 <= at < 6.75 else 0) - (2 if at >= 6.75 else 0)
    add(lp_fast(saw(nf(m), 0.12), 6) * env(0.12, 0.002, 0.05), at, 0.025 + 0.04 * (at - 1.5) / 7.5, pan=0.35 * np.sin(k))
# pulsing bass from 4.5 s (8ths)
roots = {4.5: 36, 6.75: 43}
for k in range(int((9.0 - 4.5) / (B / 2))):
    at = 4.5 + k * B / 2; r = 36 if at < 6.75 else 43
    add(lp_fast(saw(nf(r), 0.22), 30) * env(0.22, 0.003, 0.12), at, 0.13)
# ---- SFX: glitch ticks on every cut
def glitch(at, g=0.25):
    n = int(SR * 0.09); s = rng.standard_normal(n) * (np.arange(n) % 220 < 110) * env(0.09, 0.001, 0.03)
    add(s, at, g, pan=rng.uniform(-0.5, 0.5)); add(np.sin(2 * np.pi * 1800 * tt(0.04)) * env(0.04, 0.001, 0.01), at, g * 0.5)
for c in (1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.2, 11.4, 12.5): glitch(c)
# light-glint shimmer whoosh on the tubes (3.1-4.4 s)
d = 1.3; x = tt(d); add(lp_fast(rng.standard_normal(len(x)), 4) * np.sin(np.pi * x / d) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * x)), 3.1, 0.12, pan=0.0)
# power-on: whine 4.6-5.1, crackles on the flicker frames (114, 115, 118, 119, 124), hit on lock (f122 = 5.08 s)
d = 0.55; x = tt(d); add(np.sin(2 * np.pi * (300 + 1400 * (x / d) ** 2) * x) * (x / d) * 0.6, 4.55, 0.08)
for fr in (114, 115, 118, 119, 124):
    n = int(SR * 0.05); add(rng.standard_normal(n) * env(0.05, 0.001, 0.012) * (rng.random(n) > 0.6), fr / 24, 0.35, pan=rng.uniform(-0.4, 0.4))
x = tt(0.9); add((np.sin(2 * np.pi * 110 * x) + 0.5 * np.sin(2 * np.pi * 220 * x)) * env(0.9, 0.002, 0.25), 122 / 24, 0.3)
# HUD boot: blips 6.0-6.5, key clicks while the boot text types (~0.3-2.2 s after 6.0)
for k, at in enumerate((6.0, 6.12, 6.24, 6.42)):
    add(np.sin(2 * np.pi * (1200 + 300 * k) * tt(0.06)) * env(0.06, 0.001, 0.02), at, 0.1, pan=0.3)
for k in range(64):
    at = 6.3 + k * (1.9 / 64); add(rng.standard_normal(int(SR * 0.01)) * env(0.01, 0.0005, 0.003), at, 0.07, pan=-0.2)
# riser 7.5-9.0 (noise + rising tone), cut dead at the reveal
d = 1.5; x = tt(d); rise = (x / d) ** 2
add((lp_fast(rng.standard_normal(len(x)), 3) * 0.6 + np.sin(2 * np.pi * (200 + 1800 * rise) * x) * 0.3) * rise, 7.5, 0.22)
# ---- 9.0 s REVEAL: whoosh + sub drop, then the DROP (drums + saw bass + chords) to 12.6 s
d = 0.8; x = tt(d); add(lp_fast(rng.standard_normal(len(x)), 6) * np.exp(-x * 4), 9.0, 0.35)
x = tt(1.4); add(np.sin(2 * np.pi * (90 * np.exp(-x * 3) + 32) * x) * np.exp(-x * 1.5), 9.0, 0.6)
drop_chords = [(9.0, [57, 60, 64, 69]), (10.0, [53, 57, 60, 65]), (11.0, [48, 52, 55, 60]), (12.0, [55, 59, 62, 67])]
for at, ch in drop_chords:
    for i, m in enumerate(ch): add(lp_fast(saw(nf(m), 1.0, 0.006), 10) * adsr(1.0, 0.02, 0.3), at, 0.085, pan=(i - 1.5) * 0.3)
    r = ch[0] - 24
    for k in range(4): add(lp_fast(saw(nf(r), 0.24, 0.01), 12) * env(0.24, 0.003, 0.15), at + k * 0.25, 0.34)
for k in range(int((12.6 - 9.0) / B)):
    at = 9.0 + k * B
    x = tt(0.25); add(np.sin(2 * np.pi * (140 * np.exp(-x * 35) + 48) * x) * np.exp(-x * 9), at, 0.95)              # kick
    if k % 2 == 1: add(rng.standard_normal(int(SR * 0.18)) * env(0.18, 0.001, 0.06), at, 0.32)                       # snare
    for h in (0.25, 0.75): add(rng.standard_normal(int(SR * 0.03)) * env(0.03, 0.0005, 0.008), at + h * B, 0.06, pan=0.3)
# drop lead arp
lead = [81, 84, 88, 84, 86, 84, 81, 79]
for k in range(int((12.5 - 9.0) / (B / 2))):
    add(saw(nf(lead[k % 8]), 0.2) * env(0.2, 0.003, 0.09), 9.0 + k * B / 2, 0.05, pan=0.4 * np.sin(k * 1.3))
# neon buzz under the outline flicker (11.6-12.6 s), gated by the flicker
d = 1.0; x = tt(d); gate = (np.sin(2 * np.pi * 9 * x) > -0.3).astype(float)
add(np.sign(np.sin(2 * np.pi * 120 * x)) * 0.5 * gate * np.minimum(1, x / 0.3), 11.6, 0.07)
# ---- end card: tick flicker on the ring, impact on the snap (f316 = 13.17 s), final chord tail
for k in range(6): add(np.sin(2 * np.pi * 2400 * tt(0.02)) * env(0.02, 0.0005, 0.006), 12.6 + k * 0.09, 0.06, pan=rng.uniform(-0.5, 0.5))
x = tt(1.5); add(np.sin(2 * np.pi * (70 * np.exp(-x * 4) + 38) * x) * np.exp(-x * 2.2), 316 / 24, 0.75)
add(lp_fast(rng.standard_normal(int(SR * 0.4)), 3) * env(0.4, 0.001, 0.08), 316 / 24, 0.3)
for i, m in enumerate([45, 57, 64, 69, 72]):
    add(lp_fast(saw(nf(m), 1.8, 0.005), 16) * adsr(1.8, 0.05, 1.2), 316 / 24, 0.05, pan=(i - 2) * 0.3)
# fade the last 0.4 s
fade = np.ones(N); fade[-int(SR * 0.4):] = np.linspace(1, 0, int(SR * 0.4)); L *= fade; R *= fade
st = np.stack([L, R], 1); st = np.tanh(st * 2.2) / np.tanh(2.2); st = st / np.abs(st).max() * 0.8
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1], DUR, "s")
