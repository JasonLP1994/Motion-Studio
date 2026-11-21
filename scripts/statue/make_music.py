# Original dark trap bed for KINGZ, made from scratch in numpy (no samples). 144 BPM = 10 frames/beat at 24 fps.
# 808 kick/bass, half-time snare, hat rolls; spray hiss as the outline and face marks draw on;
# riser + gap into the KINGZ hit (frame 190), long 808 tail.
import numpy as np, wave, sys
SR=48000; FPS=24; BPM=144; B=60/BPM; DUR=241/FPS
t=np.arange(int(SR*DUR))/SR; out=np.zeros_like(t); rng=np.random.default_rng(21)
F=lambda f: f/FPS
def add(sig,at,g=1.0):
    i=int(at*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def band(d,lo,hi):
    n=rng.standard_normal(int(SR*d)); X=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR); X[(f<lo)|(f>hi)]=0
    return np.fft.irfft(X,len(n))
def k808(d=0.9,f0=48):
    tt=np.arange(int(SR*d))/SR; f=f0+90*np.exp(-tt*40); return np.tanh(2.8*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*(2.2/d)))
def snare():
    tt=np.arange(int(SR*0.3))/SR; return np.tanh(2*(band(0.3,1200,9000)*np.exp(-tt*14)+np.sin(2*np.pi*200*tt)*np.exp(-tt*28)*0.8))
def hat():
    tt=np.arange(int(SR*0.035))/SR; return band(0.035,7000,15000)*np.exp(-tt*120)*0.6
HIT=F(190); GAP=F(185)
for i in range(int(GAP/(B/2))):                  # 8ths
    at=i*B/2; k=i%16
    if k in (0,5,11): add(k808(),at,0.85)
    if k in (4,12): add(snare(),at,0.7)
    add(hat(),at,0.5)
    if k in (7,15):                              # trap hat rolls (triplet 32nds)
        for r in range(1,4): add(hat(),at+r*B/6,0.4)
def hiss(a,b,g):
    d=b-a; h=band(d,2500,11000); tt=np.arange(len(h))/SR
    add(h*np.minimum(1,tt/0.03)*np.minimum(1,(d-tt)/0.06)*(0.8+0.2*np.sin(2*np.pi*6*tt)),a,g)
hiss(F(0),F(20),0.35); hiss(F(180),F(200),0.3)
tt=np.arange(int(SR*(HIT-F(165))))/SR; riser=band(len(tt)/SR,800,9000)*(tt/tt[-1])**2*0.5; add(riser,F(165))
add(k808(2.0,44),HIT,1.2); add(snare(),HIT,0.9)
tail=np.arange(int(SR*(DUR-HIT-0.5)))/SR
for i in range(0,int((DUR-HIT-0.6)/(B/2))):      # sparse hats under the hold
    add(hat(),HIT+B/2*(i+1),0.3*(1-i/12))
out=np.tanh(out*1.4)/np.tanh(1.4); out/=np.max(np.abs(out))*1.12
with wave.open(sys.argv[1],"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
print("ok",sys.argv[1])
