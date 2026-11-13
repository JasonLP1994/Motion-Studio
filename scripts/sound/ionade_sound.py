"""Sound design for the IONADE pour sting (200 frames at 30 fps), timed to the frame keys in
scripts/blender/ionade_pour.py (CFG) and src/ionade/config.ts. Synthesised in numpy (ice clinks, pour, fizz, slice thud,
can crack + hiss) plus CC0 whooshes/impact from the bundled library. Loudness-normalise afterwards to about -14 LUFS.

Usage: python3 scripts/sound/ionade_sound.py <out.wav>
"""
import subprocess, sys, os, wave
import numpy as np

SR, FPS, N = 48000, 30, 200
DUR = N / FPS
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, ".claude/skills/sound-effects/sfx")
rng = np.random.default_rng(3)
t_of = lambda f: (f - 1) / FPS

# same keys as the scene and the logo
ICE_LAND = [14, 23, 32, 41]  # printed by ionade_pour.py (ICE_LANDS): slow-motion fall
CAN_IN, POUR_A, POUR_B, CAN_OUT = 30, 44, 104, 118
SLICE_LAND = 126
SWIPE, LAND, FLASH = 132, 142, 146

L = int(DUR * SR) + SR
mix = np.zeros((L, 2))

def add(sig, at, gain=1.0, pan=0.0):
    a = int(at * SR); sig = np.asarray(sig)
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    if a < 0: sig = sig[-a:]; a = 0
    b = min(L, a + len(sig)); mix[a:b] += sig[: b - a] * gain

def load(rel, speed=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(LIB, rel), "-f", "s16le", "-ac", "2", "-ar", str(int(SR / speed)), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768.0

def band(x, lo, hi):
    X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, n=len(x), axis=0)

def env(n, a_ms, decay):
    t = np.arange(n) / SR; e = np.exp(-t * decay); a = max(1, int(a_ms * SR / 1000)); e[:a] *= np.linspace(0, 1, a); return e

# ---- ice: a glassy clink (inharmonic partials) + a knock on the glass floor, a smaller bounce clink after ----
def clink(scale=1.0, base=2300):
    n = int(0.5 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, (ratio, amp, dec) in enumerate([(1.0, 1.0, 18), (1.61, 0.7, 24), (2.27, 0.5, 30), (3.13, 0.35, 40), (4.4, 0.2, 55)]):
        s += amp * np.sin(2 * np.pi * base * ratio * rng.uniform(0.98, 1.02) * t + rng.uniform(0, 6)) * np.exp(-t * dec)
    s += band(rng.standard_normal(n), 2000, 12000) * env(n, 0.3, 300) * 0.8
    knock = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35) * 0.6
    return (s * 0.25 + knock) * scale
for k, f in enumerate(ICE_LAND):
    pan = rng.uniform(-0.2, 0.2)
    add(clink(1.0, rng.uniform(2000, 2800)), t_of(f), 0.5, pan)
    add(clink(0.45, rng.uniform(2600, 3400)), t_of(f) + 0.09, 0.4, pan)

# ---- the can sliding in and leaving ----
add(load("whoosh/fs-683101-quick-woosh.ogg"), t_of(CAN_IN) - 0.05, 0.25, 0.4)
add(load("whoosh/fs-683101-quick-woosh.ogg", 1.2), t_of(CAN_OUT) - 0.12, 0.18, 0.5)

# ---- the pour: noise through a resonance that climbs as the glass fills, with glugs ----
a, b = int(t_of(POUR_A) * SR), int((t_of(POUR_B) + 0.25) * SR); n = b - a
noise = rng.standard_normal(n); out = np.zeros(n); blk = 2048; hop = blk // 2; win = np.hanning(blk)
freqs = np.fft.rfftfreq(blk, 1 / SR)
for i in range(0, n - blk, hop):
    p = i / n; fc = 450 + 900 * p ** 0.8                      # pitch rises as the level rises
    shape = np.exp(-((freqs - fc) / (fc * 0.35)) ** 2) * 1.0 + np.exp(-((freqs - 2.6 * fc) / (fc * 0.6)) ** 2) * 0.5 + 0.08 * (freqs > 2500)
    out[i:i + blk] += np.fft.irfft(np.fft.rfft(noise[i:i + blk] * win) * shape, n=blk)
tt = np.arange(n) / SR
glug = 0.75 + 0.25 * np.sin(2 * np.pi * (9 + 4 * np.sin(2 * np.pi * 0.7 * tt)) * tt)
pe = np.minimum(1, tt / 0.05) * np.clip((n / SR - tt) / 0.25, 0, 1) * (1 - 0.3 * tt / (n / SR))
add(out * glug * pe, t_of(POUR_A), 0.55)

# ---- fizz: sparse bright crackle, building with the pour, a burst when the logo fires ----
def crackle(dur, rate_fn, gain):
    n = int(dur * SR); s = np.zeros(n); t = 0.0
    while True:
        t += rng.exponential(1.0 / max(1.0, rate_fn(t)))
        if t >= dur: break
        i = int(t * SR); m = int(rng.uniform(0.0006, 0.002) * SR)
        if i + m < n: s[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.3, 1.0)
    return band(s, 3000, 16000) * gain
fz_start = t_of(POUR_A + 4); fz = crackle(DUR - fz_start, lambda t: 40 + 900 * min(1, t / 2.0) * np.exp(-max(0, t - 2.2) / 2.5), 1.0)
add(np.stack([fz, np.roll(fz, 211)], 1), fz_start, 0.35)

# ---- the camera whips out from the low pour shot to the end shot (f106-128): a soft air whoosh ----
WHIP = 106
add(load("whoosh/fs-169867-swoosh.ogg", 0.85), t_of(WHIP) + 0.05, 0.3, -0.2)

# ---- the slice landing on the rim: a soft wet thud ----
n = int(0.25 * SR); t = np.arange(n) / SR
thud = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 30) + band(rng.standard_normal(n), 200, 1800) * env(n, 1, 45) * 0.5
add(thud, t_of(SLICE_LAND), 0.45, 0.25)

# ---- logo: can crack + hiss, the swipe whoosh, a soft low hit as it lands, a fizz burst on the flash ----
n = int(0.9 * SR); t = np.arange(n) / SR
crack = band(rng.standard_normal(n), 800, 14000) * env(n, 0.2, 220)
hiss = band(rng.standard_normal(n), 3500, 15000) * np.minimum(1, t / 0.015) * np.exp(-t * 3.2)
add(crack * 0.9 + hiss * 0.5, t_of(SWIPE) - 0.12, 0.7)
add(load("transition/fs-786514-swoosh-v2.ogg"), t_of(SWIPE) - 0.03, 0.6)
add(load("impact/fs-177242-cinematic-impact.ogg") * 0.6, t_of(LAND), 0.35)
burst = crackle(1.4, lambda t: 2500 * np.exp(-t * 2.2), 1.0)
add(np.stack([burst, np.roll(burst, 157)], 1), t_of(FLASH), 0.45)

mix = mix[: int(DUR * SR)]
fade = int(0.35 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= max(1e-9, np.abs(mix).max()) / 0.8
outp = sys.argv[1] if len(sys.argv) > 1 else "ionade_sound.wav"
with wave.open(outp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("wrote", outp, f"{DUR:.2f}s")
