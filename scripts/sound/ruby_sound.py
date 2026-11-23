"""Rubyred film sound (450 frames, 30 fps, 100 BPM = beat 0.6 s = 18 frames). Original music synthesised in numpy (glass bells,
warm pad, sub pulse) + a sound pass from the bundled CC0 library, timed to scripts/blender/ruby_pendant.py CFG and src/ruby/config.ts.
Normalise afterwards to about -14 LUFS (ffmpeg loudnorm, true peak -1.5).
Usage: python3 scripts/sound/ruby_sound.py <out.wav>
"""
import subprocess, sys, os, wave
import numpy as np
SR, FPS, NF = 48000, 30, 450
DUR = NF / FPS
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, ".claude/skills/sound-effects/sfx")
rng = np.random.default_rng(11)
T = lambda f: (f - 1) / FPS                        # Blender frame -> seconds
BEAT = 0.6
L = int((DUR + 1) * SR); mix = np.zeros((L, 2))

def add(sig, at, gain=1.0, pan=0.0):
    a = int(at * SR); sig = np.asarray(sig, float)
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    if a < 0: sig = sig[-a:]; a = 0
    b = min(L, a + len(sig)); mix[a:b] += sig[: b - a] * gain

def load(rel, speed=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(LIB, rel), "-f", "s16le", "-ac", "2", "-ar", str(int(SR / speed)), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(float) / 32768.0

def band(x, lo, hi):
    X = np.fft.rfft(x, axis=0); fr = np.fft.rfftfreq(len(x), 1 / SR); X[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(X, n=len(x), axis=0)

hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def bell(m, dur=2.4, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in ((1, 1, 1.6), (2.0, .35 * bright, 3), (2.76, .25 * bright, 5), (5.4, .12 * bright, 9)))
    return s * np.minimum(1, t / 0.003)
def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * hz(m) * (1 + d) * t + p) for m in ms for d, p in ((0, 0), (0.003, 1), (-0.004, 2)))
    s = band(s + 0.3 * band(rng.standard_normal(n), 200, 900) * 0.02, 60, 2400)
    return s * np.minimum(1, t / 0.8) * np.clip((dur - t) / 0.6, 0, 1)
def sub(dur, f0=55):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (f0 + 40 * np.exp(-t * 25)) * t) * np.exp(-t * 7) * np.minimum(1, t / 0.002)
def click(pitch=1.0):         # metal part locking home: bright ping + tick
    n = int(0.25 * SR); t = np.arange(n) / SR
    ping = sum(np.sin(2 * np.pi * f * pitch * t) * np.exp(-t * d) for f, d in ((3200, 30), (4870, 45), (7100, 60)))
    return ping * 0.5 + band(rng.standard_normal(n), 3000, 14000) * np.exp(-t * 400) * 0.8
def shimmer(dur=1.6, base=84):
    out = np.zeros(int(dur * SR))
    for k, m in enumerate((base, base + 7, base + 12, base + 16, base + 19)):
        b = bell(m, dur - k * 0.05, 0.6); a = int(k * 0.05 * SR); out[a:a + len(b)] += b * 0.5
    return out
def rattle(t0, t1, n_hits=60):  # chain links ticking on the floor, thinning out
    for k in range(n_hits):
        u = (k / n_hits) ** 1.6; at = t0 + (t1 - t0) * u
        add(click(rng.uniform(0.7, 1.4)) * (1 - u) ** 1.2, at, 0.18, rng.uniform(-0.6, 0.6))

# ---------------- music: A minor luxury, 100 BPM, bar = 2.4 s ----------------
CH = [(57, 60, 64, 71), (53, 57, 60, 64), (48, 55, 59, 64), (55, 59, 62, 66)]   # Am(add9 colour) / Fmaj7 / Cmaj7 / G
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
DROP_T, LAND_T, END_T, FLK_T, LOGO_T = T(289), T(301), T(325), T(379), T(397)
bar = 0
while bar * 2.4 < FLK_T:
    t0 = bar * 2.4; ch = CH[bar % 4]
    if not (DROP_T - 0.05 < t0 < END_T - 0.1):
        add(pad([m - 12 for m in ch[:3]], 2.6), t0, 0.05)
    for i, k in enumerate(ARP):                                         # bell arpeggio in eighths (0.3 s)
        at = t0 + i * 0.3
        if at >= FLK_T or (DROP_T - 0.3 < at < END_T): continue
        add(bell(ch[k] + 12, 1.6, 0.8), at, 0.05 + 0.03 * (i % 2 == 0), (-0.3, 0.3)[i % 2])
    bar += 1
for b in np.arange(T(109), DROP_T - 0.2, BEAT): add(sub(0.5), b, 0.22)   # sub pulse once the film opens up
for b in np.arange(END_T, FLK_T, BEAT): add(sub(0.5, 49), b, 0.28)        # bigger pulse under the end hero + title
add(pad([45, 52, 57, 60, 64], 4.0), END_T, 0.06)                         # warm swell into the final shot
# ---------------- sound pass ----------------
add(load("whoosh/fs-264777-swoosh.ogg", 0.7), T(1), 0.12)                # air as the macro opens
add(shimmer(1.6, 88), T(109) - 0.02, 0.10); add(load("transition/fs-786514-swoosh-v2.ogg", 1.2), T(109) - 0.12, 0.15)  # glint-flash cut
add(load("whoosh/fs-683101-quick-woosh.ogg", 0.8), T(145) - 0.05, 0.22); add(load("riser/fs-464250-echo-chromatic-riser-wav.ogg", 1.0)[: int(1.4 * SR)], T(146), 0.07)
for f, p in ((208, 1.0), (226, 0.9), (244, 1.1)): add(click(p), T(f), 0.35); add(sub(0.3, 70), T(f), 0.12)   # parts lock home
add(shimmer(1.2, 91), T(253), 0.06)                                       # match-move into the hero
add(load("riser/fs-174363-rewind.ogg", 1.3)[: int(0.4 * SR)] * np.linspace(0, 1, int(0.4 * SR))[:, None], T(281), 0.10)  # the tip before the drop
add(load("impact/kenney-impact-impactsoft-heavy-000.ogg"), LAND_T, 0.55); add(sub(0.8, 45), LAND_T, 0.4)   # the pendant lands
rattle(LAND_T - 0.1, T(322), 70)                                          # the chain pours down and settles
add(shimmer(1.6, 88), T(302), 0.09)                                       # landing glint
add(load("impact/fs-177242-cinematic-impact.ogg"), T(343), 0.45); add(load("glitch/kenney-interface-glitch-002.ogg"), T(343), 0.30)  # RUBYRED slam
add(shimmer(1.2, 93), T(343) + 0.1, 0.05)
glitches = ["glitch/kenney-sci-computernoise-000.ogg", "glitch/kenney-sci-computernoise-001.ogg", "glitch/kenney-sci-computernoise-002.ogg", "glitch/kenney-interface-glitch-002.ogg"]
for k, f in enumerate(range(379, 397, 2)):                               # the hard flicker: one digital stutter per state
    g = load(glitches[k % 4], 1.0 + 0.1 * (k % 3)); add(g[: int(0.065 * SR)], T(f), 0.30, (-0.4, 0.4)[k % 2])
add(load("impact/fs-347561-micheal-bay-hit.ogg"), LOGO_T, 0.42); add(sub(1.2, 41), LOGO_T, 0.45)   # logo lands
add(pad([45, 57, 60, 64, 71], 2.6), LOGO_T, 0.07); add(shimmer(2.2, 81), LOGO_T + 0.05, 0.12)
add(load("ding/fs-349504-triangle-open-04.ogg"), T(405), 0.16)          # wordmark
# master: gentle glue, fade out at the end
n = len(mix); t = np.arange(n) / SR; mix *= np.clip((DUR + 0.3 - t) / 0.6, 0, 1)[:, None]
mix = np.tanh(mix * 1.4) / 1.4
mix = mix[: int(DUR * SR)]
out = (mix / max(1e-9, np.abs(mix).max()) * 0.8 * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("saved", sys.argv[1], round(DUR, 2), "s")
