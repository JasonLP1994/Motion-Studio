"""Snow globe soundtrack: an original music-box tune + sparkle chimes, a seamless 10 s loop.
96 BPM -> 16 beats = exactly 10 s, so the loop repeats on the bar. Tails that run past 10 s wrap round to the
start (circular mix), so the join is inaudible. Synthesised here, no samples, no paid music.
Usage: python3 scripts/sound/snow_globe_sound.py <out.wav>   (then loudness-normalise, see the notes)
"""
import sys, wave
import numpy as np

SR, BPM, BEATS = 48000, 96, 16
BEAT = 60.0 / BPM; DUR = BEAT * BEATS                      # 10.0 s
L = int(round(DUR * SR))
mix = np.zeros((L, 2))
rng = np.random.default_rng(11)

def hz(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    n, o = note[:-1], int(note[-1]); return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)

def place(sig, t, gain=1.0, pan=0.0):
    """add sig at time t, wrapping anything past the loop end back to the start"""
    a = int(round(t * SR)) % L
    st = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1) * gain
    n = len(st); end = a + n
    if end <= L: mix[a:end] += st
    else:
        k = L - a; mix[a:] += st[:k]; rest = st[k:]
        while len(rest):
            m = min(L, len(rest)); mix[:m] += rest[:m]; rest = rest[m:]

def musicbox(f, dur=2.2, bright=1.0):
    """a plucked steel comb: fundamental + slightly inharmonic overtones, fast attack, ringing decay"""
    t = np.arange(int(dur * SR)) / SR
    parts = [(1.0, 1.0, 2.2), (2.0, 0.35 * bright, 4.5), (3.01, 0.12 * bright, 7.0), (4.17, 0.08 * bright, 9.0), (5.43, 0.04 * bright, 12.0)]
    s = sum(a * np.sin(2 * np.pi * f * m * t + rng.uniform(0, 6.28)) * np.exp(-t * d) for m, a, d in parts)
    s *= np.minimum(1, t / 0.002)                          # 2 ms attack: the tine pluck
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.05
    return s + click

def chime(f, dur=2.8):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in ((1, 1, 1.6), (2.76, 0.45, 3.0), (5.40, 0.2, 5.0), (8.93, 0.08, 8.0)))
    return s * np.minimum(1, t / 0.004)

# melody (beat, note, length in beats) - original tune in C major over C | Am | F | G
MEL = [(0, "E5", 1), (1, "G5", 1), (2, "C6", 1.5), (3.5, "B5", .5),
       (4, "A5", 1), (5, "E5", 1), (6, "G5", 2),
       (8, "F5", 1), (9, "A5", 1), (10, "C6", 1), (11, "A5", 1),
       (12, "G5", 1), (13, "D5", .5), (13.5, "E5", .5), (14, "G5", 1), (15, "B4", 1)]
for b, n, ln in MEL:
    place(musicbox(hz(n), 1.6 + ln), b * BEAT + rng.uniform(0, 0.008), 0.55, rng.uniform(-0.15, 0.15))

# soft accompaniment: broken chords in eighths, lower and quieter
CHORDS = [["C4", "G4", "E4", "G4"], ["A3", "E4", "C4", "E4"], ["F3", "C4", "A3", "C4"], ["G3", "D4", "B3", "D4"]]
for bar, ch in enumerate(CHORDS):
    for k in range(8):
        n = ch[k % 4]
        place(musicbox(hz(n), 1.8, 0.6), (bar * 4 + k * 0.5) * BEAT + rng.uniform(0, 0.006), 0.20 if k % 2 else 0.26, -0.25 + 0.5 * (k % 2))
    place(musicbox(hz(ch[0][:-1] + str(int(ch[0][-1]) - 1)), 3.0, 0.4), bar * 4 * BEAT, 0.30, 0.0)   # low root on the bar

# sparkle chimes on the gold twinkles (peaks at 1.25 s and 6.25 s) + a light shimmer through the loop
for t0 in (1.25, 6.25):
    for k, n in enumerate(("E7", "G7", "C8")):
        place(chime(hz(n)), t0 + k * 0.07, 0.10, (-0.4, 0.0, 0.4)[k])
for k in range(10):
    place(chime(hz(rng.choice(["C7", "E7", "G7", "A7", "D7"])), 1.6), rng.uniform(0, DUR), 0.035, rng.uniform(-0.7, 0.7))

# small room reverb, applied circularly so the tail also wraps round the loop
ir_t = np.arange(int(1.6 * SR)) / SR
for ch in range(2):
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2); ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) * 6
    n = 1 << int(np.ceil(np.log2(L + len(ir))))
    wet = np.fft.irfft(np.fft.rfft(mix[:, ch], n) * np.fft.rfft(ir, n), n)
    wet = wet[:L] + np.pad(wet[L:L + len(ir)], (0, max(0, L - len(ir))))[:L]    # wrap the reverb tail
    mix[:, ch] = mix[:, ch] + wet * 0.8

mix /= np.max(np.abs(mix)) / 0.8
out = sys.argv[1] if len(sys.argv) > 1 else "snow_globe_sound.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"wrote {out} {L / SR:.2f}s")
