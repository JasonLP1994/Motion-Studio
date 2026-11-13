"""Sound design for the Phillips Digital ident (8 s, 30 fps), timed to the same frame keys as
scripts/blender/phillips_ident.py (CFG). Synthesised layers (numpy) + CC0 hits from the bundled library
(.claude/skills/sound-effects/sfx). Output: a 48 kHz stereo WAV, then loudness-normalised to about -14 LUFS.

Usage: python3 scripts/sound/phillips_ident_sound.py <out.wav>
"""
import subprocess, sys, os, wave
import numpy as np

SR, FPS, N = 48000, 30, 240
DUR = N / FPS
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, ".claude/skills/sound-effects/sfx")
rng = np.random.default_rng(11)
t_of = lambda f: (f - 1) / FPS  # frame -> seconds (frame 1 = 0 s)

# same keys as CFG in phillips_ident.py
SCREEN = [(1, 0, 0), (12, 1, 0.02), (14, 1, 0.25), (17, 1, 1), (30, 0, 1), (36, 1, 1), (58, 0, 1), (62, 1, 1), (96, 1, 1)]
CODE_BLEED, CRACK, SHATTER, CUT = (80, 100), (104, 108), 108, 118
NEON_A = [(196, 1), (198, 0), (199, 1), (203, 0), (204, 1), (222, 0.15), (223, 1)]
NEON_B = [(200, 1), (201, 0), (203, 1), (206, 0), (207, 1), (224, 0.2), (225, 1)]
BLACK = 232

L = int(DUR * SR) + SR // 2
mix = np.zeros((L, 2))
tt = np.arange(L) / SR

def step_env(pairs, default=0.0, smooth_ms=4):
    env = np.full(L, default); cur = default; k = 0
    for f in range(1, N + 1):
        while k < len(pairs) and pairs[k][0] <= f: cur = pairs[k][1]; k += 1
        a, b = int(t_of(f) * SR), int(t_of(f + 1) * SR); env[a:b] = cur
    env[int(t_of(N + 1) * SR):] = cur
    w = max(1, int(smooth_ms * SR / 1000)); return np.convolve(env, np.ones(w) / w, mode="same")

def add(sig, at, gain=1.0, pan=0.0):
    a = int(at * SR); sig = np.asarray(sig)
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    b = min(L, a + len(sig)); mix[a:b] += sig[: b - a] * gain

def load(rel, speed=1.0):
    path = os.path.join(LIB, rel)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(int(SR / speed)), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768.0

def lowpass(x, hz):
    X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(len(x), 1 / SR); X[f > hz] = 0; return np.fft.irfft(X, n=len(x), axis=0)
def highpass(x, hz):
    X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(len(x), 1 / SR); X[f < hz] = 0; return np.fft.irfft(X, n=len(x), axis=0)
def bandpass(x, lo, hi): return highpass(lowpass(x, hi), lo)
def fade(n, a_ms=5, r_ms=30):
    e = np.ones(n); a, r = int(a_ms * SR / 1000), int(r_ms * SR / 1000)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e

cut_s, black_s = t_of(CUT), t_of(BLACK)
room = tt < cut_s                     # the TV room
world = (tt >= cut_s) & (tt < black_s)  # inside the code

# ---- TV room ----
tone = load("ambience/fs-426767-apartment-room-tone-wav.ogg")
tone = np.tile(tone, (int(np.ceil(L / len(tone))), 1))[:L]
mix += tone * (room[:, None] * 0.35)
hum = sum(np.sin(2 * np.pi * 50 * k * tt) / k for k in (1, 2, 3, 5)) * 0.06 + np.sin(2 * np.pi * 15734 * tt) * 0.004  # mains hum + flyback whine
hum_env = np.clip((tt - 0.2) / 0.8, 0, 1) * room
mix += (hum * hum_env)[:, None]
power = step_env([(f, p) for f, p, _ in SCREEN]); opn = step_env([(f, o) for f, _, o in SCREEN], smooth_ms=30)
noise = rng.standard_normal(L)
static = bandpass(noise, 900, 9000) * 0.22 + bandpass(rng.standard_normal(L), 120, 900) * 0.08
roll = 1 + 0.35 * np.sin(2 * np.pi * 0.55 * tt)                                  # the rolling bar breathes in the static
st_env = power * (0.4 + 0.6 * opn) * roll * room
mix += np.stack([static * st_env, np.roll(static, 37) * st_env], 1)
# power-on: a low thunk + relay click
thunk = np.sin(2 * np.pi * 55 * tt[: SR // 3]) * np.exp(-tt[: SR // 3] * 14) * 0.9
add(thunk, t_of(12), 0.8); add(load("kit/click.ogg"), t_of(12) - 0.01, 0.6)
for f in (30, 58): add(load("kit/tick.ogg"), t_of(f), 0.35)                       # pops as the picture drops out
for f in (36, 62): add(load("kit/click.ogg"), t_of(f), 0.3)
# code bleeding through: computer chatter
add(load("glitch/kenney-sci-computernoise-001.ogg"), t_of(CODE_BLEED[0]), 0.45, -0.3)
add(load("glitch/kenney-sci-computernoise-002.ogg"), t_of(CODE_BLEED[0] + 12), 0.4, 0.3)
# the rush at the screen
rise = load("riser/fs-396161-scary-hits-risers-001.ogg")
rise = rise[-int((cut_s - t_of(96) + 0.05) * SR):]                                # its tail lands on the cut
add(rise * fade(len(rise), 200, 10)[:, None], t_of(96), 0.7)
# cracks: sharp ticks spreading
for k in range(7):
    n = int(0.03 * SR); c = highpass(rng.standard_normal(n), 2500) * np.exp(-np.arange(n) / SR * 160)
    add(c, t_of(CRACK[0]) + k * 0.018 + rng.uniform(0, 0.01), 0.55, rng.uniform(-0.5, 0.5))
# glass smash: a noise burst + hundreds of bright tinkles + a body impact
n = int(1.2 * SR); burst = highpass(rng.standard_normal(n), 1800) * np.exp(-np.arange(n) / SR * 7)
add(np.stack([burst, np.roll(burst, 61)], 1), t_of(SHATTER), 0.55)
for k in range(260):
    at = t_of(SHATTER) + abs(rng.normal(0, 0.18)); fr = rng.uniform(2800, 9500); dur = rng.uniform(0.04, 0.22); m = int(dur * SR)
    tk = np.sin(2 * np.pi * fr * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * rng.uniform(25, 60))
    add(tk, at, rng.uniform(0.04, 0.12), rng.uniform(-0.9, 0.9))
add(load("impact/fs-177242-cinematic-impact.ogg"), t_of(SHATTER), 0.55)
# ---- the cut into the code ----
add(load("transition/fs-683096-woosh.ogg"), cut_s - 0.18, 0.8)
add(load("transition/fs-856168-cyberpunk-glitch-hologram-tran.ogg"), cut_s - 0.05, 0.5)
# ---- inside the code ----
sub = np.sin(2 * np.pi * 41 * tt) * 0.13 + np.sin(2 * np.pi * 61.5 * tt) * 0.05
air = lowpass(rng.standard_normal(L), 400) * 0.15
w_env = np.clip((tt - cut_s) / 0.3, 0, 1) * world
mix += ((sub + air) * w_env)[:, None]
data = load("typing/fs-416777-digital-typing-wav.ogg", speed=1.6)
data = np.tile(data, (int(np.ceil((black_s - cut_s) * SR / len(data))) + 1, 1))[: int((black_s - cut_s) * SR)]
add(highpass(data, 1500) * 0.5, cut_s, 0.22)                                            # glyphs ticking in the rain
# the swarm gathering into the words
sw = load("typing/fs-511418-data-reveal-sound.ogg", speed=1.2)
add(sw * fade(len(sw), 300, 200)[:, None], t_of(160), 0.55)
r2 = load("riser/fs-464250-echo-chromatic-riser-wav.ogg"); r2 = r2[: int((t_of(196) - t_of(165)) * SR)]
add(r2 * fade(len(r2), 400, 30)[:, None], t_of(165), 0.45)
# ---- neon: a click on each ignition, a 100 Hz buzz while lit ----
neon = np.maximum(step_env(NEON_A, smooth_ms=3), step_env(NEON_B, smooth_ms=3)) * (tt < black_s)
buzz = (np.sign(np.sin(2 * np.pi * 100 * tt)) * 0.5 + np.sin(2 * np.pi * 200 * tt) * 0.3) * 0.05
buzz = lowpass(buzz, 3500)
mix += (buzz * neon)[:, None]
for f, v in NEON_A + NEON_B:
    if v >= 0.9 and f < BLACK: add(load("kit/click.ogg"), t_of(f), 0.5, rng.uniform(-0.3, 0.3))
add(load("impact/fs-222517-dramatic-hit.ogg"), t_of(196), 0.5)                         # the name lands
# ---- the hard cut to black: a sub thump, then silence ----
th = np.sin(2 * np.pi * 38 * tt[: SR // 2]) * np.exp(-tt[: SR // 2] * 9)
add(th, black_s, 0.9)
mix[int(black_s * SR):int(black_s * SR) + int(0.5 * SR)] = mix[int(black_s * SR):int(black_s * SR) + int(0.5 * SR)] * 0  # cut everything
add(th, black_s, 0.9)                                                                    # only the thump rings into the black
mix = mix[: int(DUR * SR)]
mix /= max(1e-9, np.abs(mix).max()) / 0.8
out = sys.argv[1] if len(sys.argv) > 1 else "ident_sound.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{DUR:.2f}s")
