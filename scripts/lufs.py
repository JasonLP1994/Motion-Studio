# Integrated loudness (ITU-R BS.1770-4, K-weighting + gating) and oversampled true peak, numpy only.  python3 scripts/lufs.py FILE.wav
import sys, wave
import numpy as np
def biquad(x, b, a):
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b; a1, a2 = a[1], a[2]
    for i in range(len(x)):
        v = b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2; x2, x1 = x1, x[i]; y2, y1 = y1, v; y[i] = v
    return y
def kw(fs):
    import math
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / fs); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416; a0 = 1 + K / Q + K * K
    b1 = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]; a1 = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    f0, Q = 38.13547087602444, 0.5003270373238773; K = math.tan(math.pi * f0 / fs); a0 = 1 + K / Q + K * K
    b2 = [1, -2, 1]; a2 = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return (b1, a1), (b2, a2)
w = wave.open(sys.argv[1]); fs = w.getframerate(); ch = w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch) / 32768.0
(b1, a1), (b2, a2) = kw(fs)
try:
    from scipy.signal import lfilter; f = lambda s, b, a: lfilter(b, a, s)
except ImportError: f = biquad
y = np.stack([f(f(x[:, c], b1, a1), b2, a2) for c in range(ch)], 1)
blk, hop = int(0.4 * fs), int(0.1 * fs)
z = np.array([(y[i:i + blk] ** 2).mean(0).sum() for i in range(0, len(y) - blk, hop)])
l = -0.691 + 10 * np.log10(z + 1e-12); z = z[l > -70]; l = l[l > -70]
rel = -0.691 + 10 * np.log10(z.mean()) - 10; I = -0.691 + 10 * np.log10(z[l > rel].mean())
n = len(x); X = np.fft.rfft(x, axis=0); Y = np.zeros((n * 2 + 1, ch), complex); Y[:len(X)] = X; up = np.fft.irfft(Y, n * 4, axis=0) * 4
print("I %.1f LUFS  TP %.1f dBTP" % (I, 20 * np.log10(np.abs(up).max())))
