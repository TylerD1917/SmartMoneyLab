#!/usr/bin/env python3
# Pad ambient soffuso originale (drone Am add9), stereo, molto morbido.
import numpy as np, sys, wave
sr=44100
DUR=float(sys.argv[1]) if len(sys.argv)>1 else 200.0
n=int(sr*DUR); t=np.arange(n)/sr

# accordo caldo, La minore add9 (voci gravi -> evita frequenze acute fastidiose)
freqs=[110.0,164.81,220.0,261.63,329.63]      # A2 E3 A3 C4 E4
weights=[1.0,0.7,0.8,0.55,0.45]

def voice(f,detune,phase):
    # 2 sinusoidi leggermente scordate + 2a armonica debole
    s =np.sin(2*np.pi*(f)*t+phase)
    s+=np.sin(2*np.pi*(f+detune)*t+phase*1.3)
    s+=0.25*np.sin(2*np.pi*(2*f)*t+phase*0.7)
    return s

def chan(seed):
    rng=np.random.default_rng(seed); out=np.zeros(n)
    for f,w in zip(freqs,weights):
        out+=w*voice(f, rng.uniform(0.15,0.35), rng.uniform(0,2*np.pi))
    return out

L=chan(1); R=chan(2)
# LFO di volume lento (respiro) ~ periodo 14s, tra 0.55 e 1.0
lfo=0.775+0.225*np.sin(2*np.pi*t/14.0 - np.pi/2)
L*=lfo; R*=lfo
# lowpass one-pole (ammorbidisce)
def lp(x,a=0.015):
    y=np.empty_like(x); acc=0.0
    # filtro leggero vettoriale approssimato con cumulata esponenziale
    b=1-a
    # implementazione iterativa in blocchi per non essere lentissima
    y[0]=x[0]
    for i in range(1,len(x)):
        acc=b*acc + a*x[i]; y[i]=acc
    return y
# usa scipy-free IIR ma iterativo e' lento su 200s*44100 -> usiamo filtro FIR moving-average via convoluzione
def smooth(x,win=220):
    k=np.ones(win)/win
    return np.convolve(x,k,mode="same")
L=smooth(L); R=smooth(R)
# fade in 2.5s / out 3.5s + normalizza
env=np.ones(n)
fi=int(2.5*sr); fo=int(3.5*sr)
env[:fi]=np.linspace(0,1,fi); env[-fo:]=np.linspace(1,0,fo)
L*=env; R*=env
peak=max(np.max(np.abs(L)),np.max(np.abs(R)),1e-9)
L=(L/peak)*0.5; R=(R/peak)*0.5     # headroom; il livello finale lo mette ffmpeg
st=np.stack([L,R],axis=1)
pcm=(st*32767).astype(np.int16)
with wave.open("music.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
print("music.wav done", round(DUR,1),"s")
