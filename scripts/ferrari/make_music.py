# Original, harder audio bed for RedGlitch, made from scratch in numpy (no samples):
# distorted 100 BPM beat with 16th hat rolls and bit-crushed stutter fills under the glitch bursts,
# an engine-style rumble that revs through the montage, cut dead at the wordmark.
import numpy as np, wave, sys
SR=48000; BPM=100; B=60/BPM; FPS=30
DUR=576/FPS; MONT=423/FPS; DROP=495/FPS; END=510/FPS
t=np.arange(int(SR*DUR))/SR; out=np.zeros_like(t); rng=np.random.default_rng(9)
def add(sig,at,g=1.0):
    i=int(at*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def band(d,lo,hi):
    n=rng.standard_normal(int(SR*d)); F=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR); F[(f<lo)|(f>hi)]=0
    return np.fft.irfft(F,len(n))
def kick():
    tt=np.arange(int(SR*0.4))/SR; f=42+150*np.exp(-tt*30); return np.tanh(3.5*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*6))
def snare():
    tt=np.arange(int(SR*0.22))/SR; return np.tanh(2*(band(0.22,900,8000)*np.exp(-tt*18)+np.sin(2*np.pi*180*tt)*np.exp(-tt*30)))
def hat(o=False):
    d=0.12 if o else 0.03; tt=np.arange(int(SR*d))/SR; return np.round(band(d,6000,15000)*np.exp(-tt*(22 if o else 130))*12)/12
for i in range(int(DROP/(B/4))):            # 16ths
    at=i*B/4; k=i%16
    if k in (0,6,10) or (at>MONT and k%4==0): add(kick(),at,0.9)
    if k in (4,12): add(snare(),at,0.75)
    add(hat(k==14),at,0.45 if k%2==0 else 0.25)
    if rng.random()<0.12:                    # stutter fill
        for r in range(4): add(hat(),at+r*B/16,0.35)
f0=np.where(t<MONT,36,36+(t-MONT)*45); f0=np.where(t>END,0,f0); ph=np.cumsum(f0)/SR
saw=lambda p:2*(p%1)-1
rum=(saw(ph)+saw(ph*1.013)+0.6*saw(ph*2.004))*(0.55+0.45*np.sin(2*np.pi*9*t))
F=np.fft.rfft(rum); fr=np.fft.rfftfreq(len(rum),1/SR); F[fr>300]=0; rum=np.fft.irfft(F,len(rum))
env=np.clip(t/0.3,0,1)*np.where(t>END,np.exp(-(t-END)*7),1)*np.where((t>MONT)&(t<END),1.7,1)
out+=rum*env*0.38
out=np.tanh(out*1.5)/np.tanh(1.5); out=np.round(out*1024)/1024; out/=np.max(np.abs(out))*1.12
with wave.open(sys.argv[1],"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
print("ok",sys.argv[1])
