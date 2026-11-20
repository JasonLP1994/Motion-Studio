"""Snow globe soundtrack: an original music-box waltz + sparkle chimes, a seamless 15 s loop.
3/4 time at 96 BPM -> 8 bars = 24 beats = exactly 15 s, so the loop repeats on the bar. Tails that run past 10 s wrap round to the
start (circular mix), so the join is inaudible. Synthesised here, no samples, no paid music.
Usage: python3 scripts/sound/snow_globe_sound.py <out.wav>   (then loudness-normalise, see the notes)
"""
import sys, wave
import numpy as np

SR, BPM, BEATS, BAR = 48000, 96, 24, 3
BEAT = 60.0 / BPM; DUR = BEAT * BEATS                      # 15.0 s
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

# melody (beat, note, length in beats) - original waltz in C major, 8 bars of 3/4:
# C | Am | F | G | C | Am | Dm G | C
MEL = [(0, "E5", 2), (2, "G5", 1),
       (3, "C6", 2), (5, "B5", 1),
       (6, "A5", 1.5), (7.5, "G5", .5), (8, "F5", 1),
       (9, "D5", 2), (11, "G5", 1),
       (12, "E5", 2), (14, "G5", 1),
       (15, "C6", 1), (16, "E6", 1), (17, "D6", 1),
       (18, "C6", 1), (19, "A5", 1), (20, "B5", 1),
       (21, "C6", 3)]
for b, n, ln in MEL:
    place(musicbox(hz(n), 1.6 + ln), b * BEAT + rng.uniform(0, 0.008), 0.55, rng.uniform(-0.15, 0.15))

# soft waltz accompaniment: low root on beat 1, two light chord notes on beats 2 and 3
CHORDS = [["C3", "E4", "G4"], ["A2", "C4", "E4"], ["F2", "A3", "C4"], ["G2", "B3", "D4"],
          ["C3", "E4", "G4"], ["A2", "C4", "E4"], ["D3", "F3", "B3"], ["C3", "E4", "G4"]]
for bar, ch in enumerate(CHORDS):
    b0 = bar * BAR
    place(musicbox(hz(ch[0]), 3.0, 0.4), b0 * BEAT, 0.32, 0.0)
    for k, n in ((1, ch[1]), (2, ch[2])):
        place(musicbox(hz(n), 1.6, 0.6), (b0 + k) * BEAT + rng.uniform(0, 0.006), 0.20, (-0.25, 0.25)[k - 1])
    for k, n in ((1, ch[2]), (2, ch[1])):
        place(musicbox(hz(n), 1.4, 0.5), (b0 + k) * BEAT + rng.uniform(0, 0.006), 0.10, (0.25, -0.25)[k - 1])

# sparkle chimes on the gold twinkles (they peak at 1/8 and 5/8 of the loop) + a light shimmer through the loop
for t0 in (DUR * 0.125, DUR * 0.625):
    for k, n in enumerate(("E7", "G7", "C8")):
        place(chime(hz(n)), t0 + k * 0.07, 0.10, (-0.4, 0.0, 0.4)[k])
for k in range(14):
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
