# Original 120 BPM beat for KineticSymbols, made from scratch in numpy (no samples).
import numpy as np, wave, sys
SR=48000; BPM=120; DUR=8.0; beat=60/BPM
t=np.arange(int(SR*DUR))/SR; out=np.zeros_like(t)
rng=np.random.default_rng(7)
def add(sig,at,g=1.0):
    i=int(at*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def kick(d=0.35):
    tt=np.arange(int(SR*d))/SR; f=45+110*np.exp(-tt*28)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)
def hat(d=0.05):
    n=rng.standard_normal(int(SR*d)); n=np.diff(n,prepend=0)
    return n*np.exp(-np.arange(len(n))/SR*80)*0.25
def clap(d=0.18):
    n=rng.standard_normal(int(SR*d)); env=np.exp(-np.arange(len(n))/SR*22)
    for k in (0.0,0.011,0.022): env+=0.6*np.exp(-np.clip(np.arange(len(n))/SR-k,0,None)*120)*(np.arange(len(n))/SR>=k)
    return n*env*0.22
def bass(freq,d):
    tt=np.arange(int(SR*d))/SR; s=np.tanh(2.2*np.sin(2*np.pi*freq*tt))
    return s*np.minimum(1,tt*200)*np.exp(-tt*3.5)*0.35
drums_end=9*2*beat/2  # 4.5 s = eighth 18 (logo starts)
notes=[55.0,55.0,65.41,49.0]
for i in range(int(drums_end/beat)):
    at=i*beat; add(kick(),at,0.9)
    if i%2==1: add(clap(),at)
    add(bass(notes[(i//2)%4],beat*0.9),at)
for j in range(int(drums_end/(beat/2))):
    add(hat(),j*beat/2+beat/4,0.8 if j%2 else 0.5)
# P, D, P hits (4.5, 4.75, 5.0 s), then air until the name lands at 6.35 s.
add(kick(),4.5,1.0); add(kick(),4.75,1.0); add(kick(),5.0,1.0)
tt=np.arange(int(SR*2.2))/SR
boom=np.sin(2*np.pi*41*tt)*np.exp(-tt*1.6)*0.8
add(boom,6.35)
out=np.tanh(out*1.2)/np.tanh(1.2)
out/=np.max(np.abs(out))*1.12
pcm=(out*32767).astype(np.int16)
with wave.open(sys.argv[1],"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok",sys.argv[1])
