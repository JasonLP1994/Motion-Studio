"""Sound design for the SLIME SHOE ident (360 frames at 30 fps), timed to CFG in scripts/blender/shoe_slime.py.
Synthesised in numpy (wet churn, squelches, gloopy melt, strand stretches and snaps, splats, lace whips, shimmer)
plus CC0 hits/whooshes from the bundled library. Loudness-normalise afterwards to about -14 LUFS.

Usage: python3 scripts/sound/shoe_slime_sound.py <out.wav>
"""
import subprocess, sys, os, wave
import numpy as np

SR, FPS, N = 48000, 30, 360
DUR = N / FPS
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, ".claude/skills/sound-effects/sfx")
rng = np.random.default_rng(7)
t_of = lambda f: (f - 1) / FPS

# same keys as the scene
WAVE1, MELT, BURST = (4, 40), (40, 62), (62, 76)
SNAPS = [71, 73, 75, 77]
LANDS = {"outsole": (80, 106), "midsole": (84, 112), "upper": (126, 156), "heel": (170, 199), "tongue": (210, 236), "laces": (220, 248)}
WAVE2, SET, SWEEP = (256, 282), 285, (290, 318)
CUTS = [77, 117, 162, 207, 252]

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

def formant(noise, fc_curve, q=0.25, blk=1024):
    """noise through a moving resonance (fc per sample) -> wet, vocal slime textures"""
    n = len(noise); out = np.zeros(n); hop = blk // 2; win = np.hanning(blk); freqs = np.fft.rfftfreq(blk, 1 / SR)
    for i in range(0, n - blk, hop):
        fc = fc_curve[i + blk // 2]
        shape = np.exp(-((freqs - fc) / (fc * q)) ** 2) + 0.4 * np.exp(-((freqs - 2.3 * fc) / (fc * q * 1.5)) ** 2)
        out[i:i + blk] += np.fft.irfft(np.fft.rfft(noise[i:i + blk] * win) * shape, n=blk)
    return out

def glorp(dur=0.18, f0=260, f1=90):
    """one wet bubble: a resonant pitch drop with a soft click start"""
    n = int(dur * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * np.minimum(1, t / 0.004)
    return s + band(rng.standard_normal(n), 300, 3000) * np.exp(-t * 60) * 0.25

def squelch(dur, lo, hi, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    fc = lo + (hi - lo) * (0.5 - 0.5 * np.cos(np.pi * t / dur)) * (1 + 0.15 * np.sin(2 * np.pi * 7 * t))
    s = formant(rng.standard_normal(n), fc, 0.18)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7 * (0.7 + 0.3 * np.sin(2 * np.pi * 11 * t))
    return s * env * gain

def splat(scale=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 16)
    wet = band(rng.standard_normal(n), 250, 4500) * np.exp(-t * 30) * np.minimum(1, t / 0.002)
    return (thump * 0.9 + wet * 0.6 + np.pad(glorp(0.15, 340, 120), (int(0.03 * SR), n))[:n] * 0.5) * scale

def stretch(dur):
    """a strand pulling thin: a rising narrow resonance plus an elastic creak"""
    n = int(dur * SR); t = np.arange(n) / SR
    s = formant(rng.standard_normal(n), 300 + 1500 * (t / dur) ** 1.5, 0.08)
    creak = np.sin(2 * np.pi * np.cumsum(180 + 320 * t / dur + 15 * np.sin(2 * np.pi * 23 * t)) / SR) * 0.25
    return (s + creak) * np.minimum(1, t / 0.05) * np.clip((dur - t) / 0.03, 0, 1)

def snap():
    n = int(0.12 * SR); t = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * np.cumsum(300 + 1400 * np.exp(-t * 60)) / SR) * np.exp(-t * 35)
    return chirp * 0.6 + band(rng.standard_normal(n), 2000, 12000) * np.exp(-t * 200) * 0.5

# ---- 0-2.1 s: wet churn bed under the warp and melt ----
a, b = t_of(1), t_of(BURST[0])
n = int((b - a) * SR); t = np.arange(n) / SR
fc = 220 + 160 * np.sin(2 * np.pi * 0.6 * t) + 120 * np.sin(2 * np.pi * 1.7 * t + 1)
bed = formant(rng.standard_normal(n), np.maximum(80, fc), 0.3) * np.minimum(1, t / 0.4) * (0.6 + 0.4 * np.clip((t - 1.3) / 0.8, 0, 1))
add(bed, a, 0.35)
add(squelch(t_of(WAVE1[1]) - t_of(WAVE1[0]), 250, 900), t_of(WAVE1[0]), 0.5, -0.2)       # the ripple field
for k in range(14):                                                                         # gloopy melt bubbles
    add(glorp(rng.uniform(0.12, 0.25), rng.uniform(180, 420), rng.uniform(60, 120)), rng.uniform(t_of(MELT[0]), t_of(MELT[1])), 0.45, rng.uniform(-0.5, 0.5))
add(squelch(0.7, 500, 140), t_of(MELT[0]) + 0.1, 0.5)                                       # the sag

# ---- 2.1-2.5 s: burst, strands stretch and snap ----
add(load("whoosh/fs-264777-swoosh.ogg", 0.8), t_of(BURST[0]) - 0.03, 0.35)
add(splat(0.8), t_of(BURST[0]), 0.6)
add(stretch(t_of(SNAPS[0]) - t_of(BURST[0])), t_of(BURST[0]), 0.4, 0.2)
for k, f in enumerate(SNAPS): add(snap(), t_of(f), 0.45, (-0.4, 0.3, -0.1, 0.5)[k])

# ---- 2.6-8.4 s: each part sucked in on tendrils, a splat as it lands ----
for k, (nm, (a0, a1)) in enumerate(LANDS.items()):
    dur = t_of(a1) - t_of(a0)
    add(squelch(dur, 180, 700 + 120 * k), t_of(a0), 0.32, (-0.3, 0.3, 0.0, -0.4, 0.2, 0.4)[k])
    add(splat(1.0 if nm not in ("laces", "tongue") else 0.7), t_of(a1), 0.7)
for f in (224, 232, 240):                                                                    # lace whips
    add(load("whoosh/fs-683101-quick-woosh.ogg", 1.25), t_of(f), 0.22, 0.3)
add(band(rng.standard_normal(int(0.6 * SR)), 200, 1200) * np.linspace(1, 0, int(0.6 * SR)) ** 2, t_of(84), 0.15)  # puddle sucked up

# ---- 8.4-9.5 s: last wave, then it SETS (hard hit) ----
add(squelch(t_of(WAVE2[1]) - t_of(WAVE2[0]), 200, 1100), t_of(WAVE2[0]), 0.45)
add(load("riser/fs-685256-riser-sound-effect-short-wav.ogg"), t_of(SET) - 0.9, 0.18)
add(load("impact/fs-222517-dramatic-hit.ogg"), t_of(SET), 0.55)
n = int(0.5 * SR); t = np.arange(n) / SR
add(band(rng.standard_normal(n), 1500, 9000) * np.exp(-t * 40) + np.sin(2 * np.pi * 55 * t) * np.exp(-t * 6) * 0.8, t_of(SET), 0.55)  # crack + sub
for k in range(5): add(snap(), t_of(SET + 4 + k * 1.6), 0.2, rng.uniform(-0.5, 0.5))         # drips snapping back

# ---- 9.6-10.6 s: the slime drains off (curing glow edge): sizzle, slide, shimmer ----
a, b = t_of(SWEEP[0]), t_of(SWEEP[1]); n = int((b - a + 0.4) * SR); t = np.arange(n) / SR
siz = formant(rng.standard_normal(n), 2500 + 4500 * np.clip(t / (b - a), 0, 1), 0.3) * np.sin(np.pi * np.clip(t / (b - a + 0.4), 0, 1)) ** 0.8
shim = sum(np.sin(2 * np.pi * f0 * t) * np.exp(-t * 2.2) for f0 in (1320, 1980, 2640, 3520)) * 0.08
add(siz + shim, a, 0.35, 0.0)
add(load("transition/fs-786514-swoosh-v2.ogg", 1.1), a - 0.05, 0.3)
add(load("ding/kenney-interface-glass-002.ogg", 0.8), b, 0.25)
add(squelch(b - a, 900, 160), a, 0.40)                                                       # the slime sliding down off the shoe
for k in range(6): add(glorp(rng.uniform(0.10, 0.18), rng.uniform(260, 420), rng.uniform(80, 130)), b - 0.15 + k * 0.05, 0.22, rng.uniform(-0.5, 0.5))  # drips letting go
add(load("whoosh/fs-683101-quick-woosh.ogg", 0.7), t_of(330) - 0.1, 0.18)                    # end logo in

# ---- cinematic bed: a dark bass pulse under everything (ducks at the hit), a wet hiss as the veins crawl ----
n = int(DUR * SR); t = np.arange(n) / SR
pulse = (0.55 + 0.45 * np.exp(-((t * 1.15) % 1.0) * 6)) * np.minimum(1, t / 0.8)            # slow heartbeat swell
drone = (np.sin(2 * np.pi * 43 * t) + 0.5 * np.sin(2 * np.pi * 64.5 * t + 0.3 * np.sin(2 * np.pi * 0.2 * t))) * pulse
duck = 1 - 0.7 * np.exp(-np.clip(t - t_of(SET), 0, None) * 3) * (t > t_of(SET))
drone *= duck * np.clip((DUR - t) / 1.5, 0, 1) * (1 - 0.6 * np.clip((t - t_of(SWEEP[1])) / 0.8, 0, 1))
add(drone, 0.0, 0.22)
def hiss(a0, a1, rise=True):
    m = int((a1 - a0) * SR); tt = np.arange(m) / SR; u = tt / (a1 - a0)
    crawl = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * (9 + 7 * u) * tt))
    env = np.sin(np.pi * np.clip(u, 0, 1)) ** 0.8
    return band(rng.standard_normal(m), 2500, 9000) * crawl * env
add(hiss(0.0, t_of(48)), 0.0, 0.10, -0.2)                                                  # veins surge in and climb
add(hiss(t_of(SWEEP[0]) - 0.1, t_of(SWEEP[1]) + 0.3), t_of(SWEEP[0]) - 0.1, 0.08, 0.2)    # veins slide off
add(load("transition/fs-786514-swoosh-v2.ogg", 1.4), t_of(332), 0.12)                     # the glint
add(load("ding/kenney-interface-glass-002.ogg", 1.25), t_of(346), 0.14, 0.2)
mix = mix[: int(DUR * SR)]
fade = int(0.6 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= max(1e-9, np.abs(mix).max()) / 0.8
outp = sys.argv[1] if len(sys.argv) > 1 else "shoe_slime_sound.wav"
with wave.open(outp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("wrote", outp, f"{DUR:.2f}s")
