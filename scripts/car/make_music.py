# Original audio bed for LostData, made from scratch in numpy (no samples):
# a tight 100 BPM glitch beat (kick, clap, bit-crushed hats) over an engine-style rumble
# (a low detuned saw idle that revs up into the dissolve), stopping as the wordmark lands.
import numpy as np, wave, sys
SR=48000; BPM=100; DUR=8.0; B=60/BPM
t=np.arange(int(SR*DUR))/SR; out=np.zeros_like(t); rng=np.random.default_rng(5)
def add(sig,at,g=1.0):
    i=int(at*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def band(d,lo,hi):
    n=rng.standard_normal(int(SR*d)); F=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR); F[(f<lo)|(f>hi)]=0
    return np.fft.irfft(F,len(n))
def kick():
    tt=np.arange(int(SR*0.35))/SR; f=45+130*np.exp(-tt*32); return np.tanh(2.2*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*8))
def clap():
    tt=np.arange(int(SR*0.2))/SR; return band(0.2,1000,6000)*np.exp(-tt*20)
def hat():
    tt=np.arange(int(SR*0.03))/SR; h=band(0.03,6000,15000)*np.exp(-tt*120); return np.round(h*16)/16
END=189/30; DROP=171/30
for i in range(int(DROP/(B/2))):        # 8ths until the dissolve
    at=i*B/2; k=i%8
    if k in (0,3,6): add(kick(),at,0.9)
    if k in (2,6): add(clap(),at,0.6)
    add(hat(),at+B/4,0.35)
# engine-style rumble: detuned low saws with a slow wobble, revving up into the dissolve
f0=np.where(t<DROP,38,38+(t-DROP)*60); f0=np.where(t>END,0,f0)
ph=np.cumsum(f0)/SR
saw=lambda p:2*(p%1)-1
rum=(saw(ph)+saw(ph*1.012)+0.5*saw(ph*2.003))*(0.55+0.45*np.sin(2*np.pi*7*t))
F=np.fft.rfft(rum); fr=np.fft.rfftfreq(len(rum),1/SR); F[fr>260]=0; rum=np.fft.irfft(F,len(rum))
env=np.clip(t/0.4,0,1)*np.where(t>END,np.exp(-(t-END)*6),1)*np.where((t>DROP)&(t<END),1.6,1)
out+=rum*env*0.35
out=np.tanh(out*1.2)/np.tanh(1.2); out/=np.max(np.abs(out))*1.12
with wave.open(sys.argv[1],"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
print("ok",sys.argv[1])
