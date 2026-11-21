# Original audio for GraffitiFlip, made from scratch in numpy (no samples):
# dusty boom-bap at 112.5 BPM under the poster flips, a spray-can rattle into the end card,
# spray hiss during the write-on, one hit as the drips land, vinyl crackle tail.
import numpy as np, wave, sys
SR=48000; BPM=112.5; DUR=8.0; S16=60/BPM/4
t=np.arange(int(SR*DUR))/SR; out=np.zeros_like(t); rng=np.random.default_rng(11)
def add(sig,at,g=1.0):
    i=int(at*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def bandnoise(d,lo,hi):
    n=rng.standard_normal(int(SR*d)); F=np.fft.rfft(n); f=np.fft.rfftfreq(len(n),1/SR)
    F[(f<lo)|(f>hi)]=0; return np.fft.irfft(F,len(n))
def kick():
    tt=np.arange(int(SR*0.4))/SR; f=48+120*np.exp(-tt*30)
    return np.tanh(2.5*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7))
def snare():
    tt=np.arange(int(SR*0.25))/SR
    return (bandnoise(0.25,900,7000)*0.9*np.exp(-tt*16)+np.sin(2*np.pi*190*tt)*np.exp(-tt*25)*0.6)
def hat(open_=False):
    d=0.12 if open_ else 0.04; tt=np.arange(int(SR*d))/SR
    return bandnoise(d,7000,14000)*np.exp(-tt*(25 if open_ else 90))*0.5
FLIP_END=160/30; HIT=192/30; SPRAY=(162/30, 194/30)
# beat: kick on 16ths 0,7,10 ; snare 4,12 ; hats on 8ths (open on 14)
for s in range(int(FLIP_END/S16)):
    at=s*S16; k=s%16
    if k in (0,7,10): add(kick(),at,0.9)
    if k in (4,12): add(snare(),at,0.8)
    if k%2==0: add(hat(k==14),at,0.55 if k%4==0 else 0.4)
# can rattle (ball clicks) over the last 0.55 s of the flips
c=FLIP_END-0.55
for i in range(12):
    tt=np.arange(int(SR*0.05))/SR
    click=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*a) for f,a in ((2650,160),(4150,220),(6100,300)))
    click=click*0.35+bandnoise(0.05,2000,9000)*np.exp(-tt*200)*0.6
    add(click,c+i*0.044+(0.012 if i%2 else 0),0.7)
# spray hiss across the write-on
d=SPRAY[1]-SPRAY[0]; hs=bandnoise(d,2500,11000); tt=np.arange(len(hs))/SR
env=np.minimum(1,tt/0.03)*np.minimum(1,(d-tt)/0.08)*(0.85+0.15*np.sin(2*np.pi*5.3*tt))
add(hs*env,SPRAY[0],0.75)
# hit as drips land
add(kick(),HIT,1.0); add(snare(),HIT,0.9)
# vinyl crackle everywhere, low hum floor
for i in range(int(DUR*28)):
    add(bandnoise(0.004,1500,9000)*rng.uniform(0.05,0.25),rng.uniform(0,DUR))
out+=bandnoise(DUR,200,2500)[:len(out)]*0.012
# dirt: gentle saturation + 12-bit crush on the drums bus
out=np.tanh(out*1.3)/np.tanh(1.3); out=np.round(out*2048)/2048
out/=np.max(np.abs(out))*1.12
with wave.open(sys.argv[1],"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
print("ok",sys.argv[1])
