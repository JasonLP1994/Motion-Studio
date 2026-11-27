"""Samurai combined edit soundtrack, built only from real recorded CC0 sounds in the sound-effects skill library
(.claude/skills/sound-effects/sfx). No synthesised tones. Each cue is aligned on its loudest point (or its end, for
risers) to an output frame of work/combined/picture (see scripts/mech/combined_edit.py for the frame map).
Processing only: pitch (resample), filters, reverb, fades. Writes a raw mix; loudness is set afterwards.
  tools/ai-venv/bin/python scripts/sound/samurai_combined_sound.py <out_raw.wav>
"""
import sys, subprocess, wave
import numpy as np
from scipy import signal

SR, FPS, NF = 48000, 30, 631
LIB = ".claude/skills/sound-effects/sfx/"
N = int(SR * NF / FPS) + SR * 3
MIX = np.zeros((N, 2)); rng = np.random.RandomState(11)

F = dict(
    amb="ambience/fs-426767-apartment-room-tone-wav.ogg",
    cin="impact/fs-177242-cinematic-impact.ogg", dram="impact/fs-222517-dramatic-hit.ogg", bay="impact/fs-347561-micheal-bay-hit.ogg",
    drum="impact/fs524817.ogg", punch0="impact/kenney-impact-impactpunch-heavy-000.ogg", punch1="impact/kenney-impact-impactpunch-heavy-001.ogg",
    soft0="impact/kenney-impact-impactsoft-heavy-000.ogg", soft1="impact/kenney-impact-impactsoft-heavy-001.ogg",
    lfx0="impact/kenney-sci-lowfrequency-explosion-000.ogg", lfx1="impact/kenney-sci-lowfrequency-explosion-001.ogg",
    scary1="riser/fs-396161-scary-hits-risers-001.ogg", scary2="riser/fs-396160-scary-hits-risers-002.ogg",
    rise_sub="riser/fs867126.ogg", rise_echo="riser/fs-464250-echo-chromatic-riser-wav.ogg", power1="riser/kenney-digital-powerup1.ogg",
    power2="riser/kenney-digital-powerup2.ogg",
    noise0="glitch/kenney-sci-computernoise-000.ogg", noise1="glitch/kenney-sci-computernoise-001.ogg", noise2="glitch/kenney-sci-computernoise-002.ogg",
    glitch="glitch/kenney-interface-glitch-002.ogg", touch="glitch/fs-144546-touchs-wav.ogg", holo="transition/fs-856168-cyberpunk-glitch-hologram-tran.ogg",
    chop="whoosh/fs-127197-fast-simple-chop-5-aif.ogg", sw1="whoosh/fs-169867-swoosh.ogg", sw2="whoosh/fs-264777-swoosh.ogg",
    quick="whoosh/fs-683101-quick-woosh.ogg", wh1="whoosh/fs393811.ogg", wh2="whoosh/fs810485.ogg", wh3="whoosh/fs830856.ogg",
    woosh="transition/fs-683096-woosh.ogg", swv2="transition/fs-786514-swoosh-v2.ogg", broom="transition/fs-816262-broomstick-whoosh-3-quiet-okm1.ogg",
    tri="ding/fs-349504-triangle-open-04.ogg", glass1="ding/kenney-interface-glass-001.ogg", glass2="ding/kenney-interface-glass-002.ogg",
    toggle="click/kenney-interface-toggle-002.ogg",
)
_cache = {}


def load(key):
    if key not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", LIB + F[key], "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        _cache[key] = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(float)
    return _cache[key].copy()


def proc(x, rate=1.0, lp=None, hp=None, rev=0.0, rev_t=1.6, trim=None, fade=0.01, rev_only=False, decay=None):
    if trim: x = x[int(trim[0] * SR): int((trim[0] + trim[1]) * SR) if trim[1] else None]
    if decay:                                                          # natural fade from the hit (tames 4 s sustains)
        pk = np.argmax(np.abs(x).sum(1)); e = np.ones(len(x)); e[pk:] = np.exp(-np.arange(len(x) - pk) / (decay * SR)); x = x * e[:, None]
    if rate != 1.0: x = signal.resample(x, int(len(x) / rate))          # tape-style pitch: <1 lower and longer
    if lp: x = signal.sosfilt(signal.butter(4, lp, "low", fs=SR, output="sos"), x, axis=0)
    if hp: x = signal.sosfilt(signal.butter(2, hp, "high", fs=SR, output="sos"), x, axis=0)
    nf = min(len(x) // 2, int(fade * SR))
    if nf: x[-nf:] *= np.linspace(1, 0, nf)[:, None]
    if rev:
        n = int(rev_t * SR); ir = rng.randn(n, 2) * np.exp(-6.9 * np.arange(n) / n)[:, None]
        ir = signal.sosfilt(signal.butter(2, 5000, "low", fs=SR, output="sos"), ir, axis=0); ir /= np.sqrt((ir ** 2).sum(0))
        wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in range(2)], 1)
        x = np.vstack([x, np.zeros((n - 1, 2))]); x = (0 if rev_only else x) + wet * rev
    return x


def place(x, frame, db=0.0, pan=0.0, align="start"):
    t = (frame - 1) / FPS
    if align == "peak": t -= np.argmax(np.abs(x).sum(1)) / SR
    elif align == "end": t -= len(x) / SR
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(N, i + len(x)); g = 10 ** (db / 20)
    MIX[i:j, 0] += x[: j - i, 0] * g * np.sqrt(1 - pan); MIX[i:j, 1] += x[: j - i, 1] * g * np.sqrt(1 + pan)


def cue(key, frame, db=0.0, pan=0.0, align="start", **kw): place(proc(load(key), **kw), frame, db, pan, align)


# ---------------- bed: room tone dropped two octaves = dark hall air, under everything
amb = proc(load("amb"), rate=0.25, lp=700)
bed = np.vstack([amb] * (N // len(amb) + 1))[:N]
env = np.interp(np.arange(N) / SR * FPS + 1, [1, 20, 136, 140, 264, 300, 311, 457, 461, 462, 470, 631, 660],
                [0, 0.7, 0.7, 1.0, 1.0, 0.8, 0.45, 0.45, 0.0, 0.0, 1.0, 0.9, 0.0])
MIX += bed * env[:, None] * 10 ** (-17 / 20)

# ---------------- intro: swords flicker on, glow sweeps up the katana, lights bang on, cuts, eyes
for k, (f, key) in enumerate([(15, "noise0"), (24, "noise1"), (27, "glitch"), (41, "noise2"), (44, "glitch"), (61, "noise0")]):
    cue(key, f, -18, pan=(-0.3, 0.3)[k % 2], trim=(0, 0.30), fade=0.06, hp=300)
for f, key in [(15, "soft0"), (41, "soft1"), (61, "soft0")]: cue(key, f, -15, align="peak", rate=0.75, rev=0.25)
cue("rise_echo", 132, -6, align="end", trim=(3.4, None), fade=0.005, rev=0.3)   # builds all the way to the lock-on
cue("rise_sub", 120, -14, align="peak", rev=0.3)
cue("lfx0", 136, -10, align="peak", decay=0.6); cue("punch0", 136, -12, align="peak", rev=0.3)
cue("punch1", 140, -14, align="peak", pan=-0.2, rev=0.3); cue("soft0", 144, -14, align="peak", pan=0.2, rev=0.3)
cue("punch0", 148, -12, align="peak", rate=0.85, rev=0.4)
for f in (141, 145, 152, 156): cue("glitch", f, -21, pan=rng.uniform(-0.5, 0.5), trim=(0, 0.12), hp=500)
for f, key in [(171, "woosh"), (206, "swv2"), (241, "wh2")]: cue(key, f, -11, align="peak", pan=-0.2)
cue("power2", 263, -17, align="end", rate=0.6, lp=4000, rev=0.4)

# ---------------- standoff (264-310): heavy hit, then a riser that cuts dead into the hand close-up
cue("dram", 264, -7, align="peak", rev=0.45, rev_t=2.2, decay=0.7); cue("lfx1", 264, -10, align="peak", decay=0.6)
cue("scary1", 311, -10, align="end", trim=(0, 2.95), fade=0.005)       # trimmed at its peak, cuts dead on the hand

# ---------------- the draw
cue("broom", 313, -20, rate=0.55, lp=3000, pan=-0.2)                     # armour shifts as the hand reaches
cue("toggle", 332, -11, rate=0.55, pan=0.2, rev=0.2); cue("soft1", 332, -17, rate=1.3, align="peak")   # grip
cue("chop", 335, -6, rate=0.40, hp=800, pan=0.2, rev=0.3)                # slow-mo slide: stretched metal scrape
cue("tri", 341, -9, rate=0.75, hp=1500, rev=0.4)                        # blade starting to ring in the scabbard
cue("sw1", 364, -2, align="end", rate=0.45, hp=900, fade=0.005)         # slowed swoosh rising into the ring
cue("tri", 364, -9, rate=1.25, hp=1200, rev=0.5, rev_t=2.5, align="peak")  # rings free at the mouth
cue("glass2", 364, -16, rate=0.8, rev=0.5, align="peak", pan=0.25)
cue("quick", 380, -9, align="peak", pan=-0.3)                            # the swing
cue("bay", 380, -11, align="peak", rev=0.35, trim=(1.45, None), decay=0.35); cue("cin", 380, -12, align="peak", trim=(0.9, None), decay=0.3)
for f in (381, 383): cue("noise1", f, -15, trim=(0, 0.10), hp=400, pan=rng.uniform(-0.5, 0.5))   # lights stutter
cue("sw2", 385, -12, pan=-0.5)                                           # follow-through
cue("chop", 411, -9, align="peak", pan=-0.4); cue("punch1", 411, -12, align="peak", rate=1.3)    # chiburi snap
cue("power1", 423, -16, align="peak", rate=0.7, rev=0.5)                 # eye flare
cue("glass1", 423, -20, rate=0.6, rev=0.6, align="peak")
cue("scary2", 457, -13, align="end", trim=(0, 3.25), fade=0.005)        # build to the reveal, cut dead into the dropout
for f, key in [(448, "touch"), (452, "noise2"), (456, "touch")]:         # zaps on the sheathed-stance glimpses
    cue(key, f, -13, trim=(0, 0.14), hp=300, pan=rng.uniform(-0.4, 0.4), fade=0.03)

# ---------------- hero: the biggest hit
cue("lfx1", 462, -4, align="peak", decay=1.2); cue("bay", 462, 0, align="peak", trim=(1.45, None), decay=1.0, rev=0.5, rev_t=2.8)
cue("cin", 462, -5, align="peak", trim=(0.9, None), decay=0.8)
cue("rise_echo", 480, -30, rate=0.5, lp=2000, rev=0.6, trim=(0, 3.0), fade=1.5)   # low shimmer under the hold

# ---------------- glitch out + end card
cue("holo", 544, -9, pan=0.1)
for f in (549, 552): cue("noise0", f, -14, trim=(0, 0.10), hp=400)
cue("soft0", 555, -10, align="peak", rev=0.3)
cue("tri", 560, -14, rate=1.0, hp=800, rev=0.5, align="peak")              # logo settle

# ---------------- dropout before the reveal: near-silence for the 5 frames before the hero hit
MIX[int((457 - 1) / FPS * SR): int((461.5 - 1) / FPS * SR)] *= 0.08

# ---------------- write (peak-normalised; loudness and limiting are set afterwards)
mix = MIX[: int(SR * NF / FPS) + SR // 2]
mix = mix / np.abs(mix).max() * 0.7
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("saved", sys.argv[1], f"{len(mix) / SR:.2f}s")
