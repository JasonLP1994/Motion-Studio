# Pixel sneaker loop soundtrack (original, numpy, no samples): a seamless 12 s chiptune loop at 120 BPM (12 frames a beat at
# 24 fps, 24 beats = 6 bars) with a typewriter key click on every letter typed or erased (reads src/pixel/typing.json) and a
# soft "ding" when each line finishes. Usage: python3 scripts/pixel_audio.py OUT.wav
import json, sys, wave
import numpy as np
SR, FPS = 48000, 24
TY = json.load(open("src/pixel/typing.json")); N = TY["loopFrames"]; DUR = N / FPS
t = np.arange(int(SR * DUR)) / SR; L = np.zeros_like(t); rng = np.random.default_rng(5)
def add(sig, at, g=1.0):
    i = int(at * SR) % len(t); n = len(sig); seg = np.arange(i, i + n) % len(t)   # wraps around: seamless loop
    L[seg] += sig * g
def sq(f, d, duty=0.5): x = np.arange(int(SR * d)) / SR; return np.where((x * f) % 1 < duty, 1.0, -1.0)
def env(d, a=0.003, r=0.08): x = np.arange(int(SR * d)) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
BEAT = 0.5
notes = {"C": 261.63, "D": 293.66, "E": 329.63, "G": 392.0, "A": 440.0}
bass = [65.41, 65.41, 98.0, 87.31, 65.41, 65.41, 110.0, 98.0]          # C2 C2 G2 F2 C2 C2 A2 G2, one per half bar
arp = ["C", "E", "G", "E", "A", "G", "E", "D"]
for b in range(int(DUR / BEAT)):
    at = b * BEAT
    x = np.arange(int(SR * 0.18)) / SR; add(np.sin(2 * np.pi * (120 * np.exp(-x * 40) + 45) * x) * np.exp(-x * 18), at, 0.55)   # kick
    if b % 2 == 1: add(rng.standard_normal(int(SR * 0.09)) * env(0.09, r=0.03), at, 0.18)                                     # snare-ish
    for h in (0.25, 0.75): add(rng.standard_normal(int(SR * 0.02)) * env(0.02, r=0.006), at + h * BEAT, 0.035)                 # hats
    add(sq(bass[(b // 2) % 8], BEAT * 0.9, 0.5) * env(BEAT * 0.9, r=0.4), at, 0.2)                                        # bass
    for k in range(2):                                                                                                     # arpeggio (8ths)
        nt = arp[(b * 2 + k) % len(arp)]; add(sq(notes[nt] * 2, 0.11, 0.25) * env(0.2, r=0.09)[:int(SR * 0.11)] if False else sq(notes[nt] * 2, 0.2, 0.25) * env(0.2, r=0.09), at + k * BEAT / 2, 0.09)
# typewriter clicks: one per character typed, softer ones for erasing; a "ding" at the end of each typed element
for name, e in TY["elements"].items():
    n = len("".join(e["lines"]))
    for k in range(n):
        at = (e["start"] + k * e["fpc"]) / FPS
        add(rng.standard_normal(int(SR * 0.012)) * env(0.012, a=0.0005, r=0.003) + sq(1800, 0.012, 0.3) * env(0.012, r=0.002) * 0.3, at, 0.09)
        er = (e["erase"] + k * e["efpc"]) / FPS
        add(rng.standard_normal(int(SR * 0.008)) * env(0.008, a=0.0005, r=0.002), er, 0.05)
    done = (e["start"] + n * e["fpc"]) / FPS
    x = np.arange(int(SR * 0.6)) / SR; add((np.sin(2 * np.pi * 1568 * x) + 0.4 * np.sin(2 * np.pi * 3136 * x)) * np.exp(-x * 6), done, 0.05)
st = np.tanh(L * 1.6) / np.tanh(1.6); st = st / np.abs(st).max() * 0.9
with wave.open(sys.argv[1], "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", sys.argv[1], round(DUR, 2), "s")
