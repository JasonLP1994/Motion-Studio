"""Phillips Digital flat 2D film: original music (synthesised here, no samples) + a measured effects pass, a seamless 15 s loop.
96 BPM, 4/4: 6 bars = 24 beats = exactly 15 s, so the music repeats on the bar. Tails past 15 s wrap round to the start
(circular mix), so the loop join is inaudible. Effects are CC0 files from .claude/skills/sound-effects/sfx (see LICENSES.md).
Each effect peaks one frame after its picture. Output is loudness-matched to -14 LUFS with true peak below -1 dBTP.
Usage: python3 scripts/sound/flat2d_sound.py <out.wav>
"""
import subprocess, sys, wave
import numpy as np

SR, BPM, FPS = 48000, 96, 30
BEAT = 60.0 / BPM; DUR = BEAT * 24; L = int(round(DUR * SR))
mix = np.zeros((L, 2)); music = np.zeros((L, 2))
rng = np.random.default_rng(7)
SFX = ".claude/skills/sound-effects/sfx/"

def place(buf, sig, t, gain=1.0, pan=0.0):
    st = sig if sig.ndim == 2 else np.stack([sig, sig], 1)
    st = st * np.array([1 - max(0, pan), 1 + min(0, pan)]) * gain
    a = int(round(t * SR)) % L
    while len(st):
        n = min(L - a, len(st)); buf[a:a + n] += st[:n]; st = st[n:]; a = 0

def hz(n): return 440.0 * 2 ** ((n - 69) / 12)
def env(n, a, r): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / r)

# ---------------- music ----------------
# A minor, moody: Am7 | Fmaj7 | Cmaj7 | G6 | Am7 | Fmaj7 (midi notes)
CH = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 59, 64], [55, 59, 62, 64], [57, 60, 64, 67], [53, 57, 60, 64]]
ROOT = [33, 29, 36, 31, 33, 29]
bar = BEAT * 4
for b, ch in enumerate(CH):
    t0 = b * bar
    # warm pad: a few soft harmonics, slow swell
    n = int(bar * SR * 1.15); t = np.arange(n) / SR
    pad = sum(sum(a * np.sin(2 * np.pi * hz(m) * k * t * (1 + d)) for k, a in ((1, 1), (2, 0.25), (3, 0.08))) for m in ch for d in (-0.002, 0.002))
    pad *= np.minimum(1, t / 0.5) * np.minimum(1, (n / SR - t) / 0.4) / 10
    place(music, pad, t0, 0.32)
    # sub bass: root on 1, the "and" of 2, and 4
    for bt, ln in ((0, 1.2), (1.5, 0.45), (3, 0.8)):
        nn = int(ln * BEAT * SR); tt = np.arange(nn) / SR
        s = np.sin(2 * np.pi * hz(ROOT[b]) * tt) + 0.3 * np.sin(2 * np.pi * hz(ROOT[b]) * 2 * tt)
        place(music, s * np.minimum(1, tt / 0.01) * np.minimum(1, (nn / SR - tt) / 0.05), t0 + bt * BEAT, 0.42)
    # plucked arpeggio, 8ths, an octave up, with a soft echo (the "designing" sparkle) - not in bar 6's logo half
    for k in range(8):
        if b == 5 and k >= 4: break
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        nn = int(0.6 * SR); tt = np.arange(nn) / SR
        s = (np.sin(2 * np.pi * hz(m) * tt) + 0.4 * np.sin(2 * np.pi * hz(m) * 2.01 * tt)) * env(nn, 0.003, 0.16)
        pan = (-0.35, 0.35)[k % 2]
        place(music, s, t0 + k * BEAT / 2, 0.16, pan)
        place(music, s, t0 + k * BEAT / 2 + BEAT * 0.75, 0.06, -pan)
# drums: drop out under the logo build (bar 6 second half) and stay light in bar 1 (logo hold / reveal)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 45 + 75 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def clap():
    n = int(0.22 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    x = np.convolve(x, [1, -1], "same") * np.exp(-t * 22); return x * 0.5
def hat():
    n = int(0.05 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    return np.convolve(x, [1, -2, 1], "same") * np.exp(-t * 90) * 0.25
for b in range(6):
    t0 = b * bar
    for q in range(4):
        tq = t0 + q * BEAT
        logo_half = b == 5 and q >= 1
        if logo_half: continue
        if q in (0, 2) and b > 0: place(music, kick(), tq, 0.55)
        if q in (1, 3) and b > 0: place(music, clap(), tq, 0.32, 0.1)
        for e in range(2): place(music, hat(), tq + e * BEAT / 2, 0.5 if b > 0 else 0.3, 0.3)

# ---------------- effects (CC0 bundle) ----------------
def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", SFX + path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(float)
def at_peak(path, frame, db, pan=0.0, rev=False):
    s = load(path)
    if rev: s = s[::-1]
    pk = int(np.argmax(np.abs(s).sum(1)))
    place(mix, s, (frame + 1) / FPS - pk / SR, 10 ** (db / 20), pan)

cues = [  # (file, frame the picture happens, level dB, pan)
    ("transition/fs-786514-swoosh-v2.ogg", 42, -16, 0.0),        # logo steps away
    ("kit/whoosh.ogg", 58, -13, -0.2),                          # deep red shrinks into the monitor
    ("../../../../public/sfx/ui-blip_kenney-digital-twotone1.ogg", 76, -18, -0.3),  # the app wakes
    ("kit/click.ogg", 94, -12, 0.25),                           # she clicks
    ("pop/kenney-interface-pluck-001.ogg", 96, -17, -0.2),      # cube pops in on the screen
    ("../../../../public/sfx/whoosh_fs393811.ogg", 149, -12, 0.0),  # zoom into the monitor
    ("pop/kenney-interface-drop-002.ogg", 152, -15, 0.3),       # octahedron
    ("pop/kenney-interface-pluck-002.ogg", 171, -16, -0.1),     # ring
    ("pop/fs-824189-pop-in-sfx.ogg", 190, -16, 0.1),            # sphere
    ("tick/fs384187.ogg", 188, -18, -0.3),                      # cursor grabs the cube
    ("pop/kenney-interface-drop-003.ogg", 226, -15, -0.3),      # cube set down
    ("../../../../public/sfx/whoosh_fs-683101-quick-woosh.ogg", 299, -12, 0.0),  # zoom back out
    ("../../../../public/sfx/transition_fs-702773-swipe-wav.ogg", 366, -14, 0.0),  # the screen floods the frame
    ("impact/kenney-impact-impactsoft-heavy-000.ogg", 369, -9, 0.0),  # logo circle lands
    ("kit/pop.ogg", 378, -15, 0.15),                            # the p. spins in
    ("transition/fs-816262-broomstick-whoosh-3-quiet-okm1.ogg", 388, -17, 0.0),  # wordmark rises
    ("ding/kenney-interface-glass-001.ogg", 400, -20, 0.2),     # services line
]
for f, fr, db, pan in cues: at_peak(f, fr, db, pan)

out = music * 0.5 + mix
# measure loudness with ffmpeg, then gain to -14 LUFS and soft-limit peaks
def write(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
out /= np.max(np.abs(out)) / 0.5
tmp = "/tmp/flat2d_tmp.wav"; write(tmp, out)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in m.splitlines() if l.strip().startswith("I:")][-1].split()[1])
out *= 10 ** ((-14 - I) / 20)
lim = 0.85; out = np.where(np.abs(out) > lim, np.sign(out) * (lim + (1 - lim) * np.tanh((np.abs(out) - lim) / (1 - lim))), out)
write(sys.argv[1] if len(sys.argv) > 1 else "flat2d_sound.wav", out)
print("measured", I, "LUFS before gain; wrote", L / SR, "s")
