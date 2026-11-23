# soft karplus-strong arpeggio + pad, 96 bpm, royalty-free (synthesized)
import numpy as np, wave
SR=44100; DUR=52.0; bpm=96; beat=60/bpm
out=np.zeros(int(SR*DUR))
def ks(freq, dur, amp):
    n=int(SR*dur); p=int(SR/freq); buf=np.random.uniform(-1,1,p); y=np.zeros(n)
    for i in range(n):
        y[i]=buf[i%p]; buf[i%p]=0.996*0.5*(buf[i%p]+buf[(i+1)%p])
    return y*amp
def note(m): return 440*2**((m-69)/12)
chords=[[60,64,67,71],[57,60,64,67],[53,57,60,64],[55,59,62,67]]  # Cmaj7 Am7 Fmaj7 G
cache={}
t=0.0; bar=0
while t<DUR-1:
    ch=chords[bar%4]
    pattern=[ch[0],ch[2],ch[1],ch[3],ch[2]+12,ch[3],ch[1],ch[2]]
    for k,m in enumerate(pattern):
        st=int((t+k*beat/2)*SR)
        if m not in cache: cache[m]=ks(note(m),1.6,0.22)
        y=cache[m]; e=min(len(y),len(out)-st)
        if e>0: out[st:st+e]+=y[:e]
    # pad
    n=int(4*beat*SR); tt=np.arange(n)/SR; env=np.minimum(1,tt/0.6)*np.minimum(1,(4*beat-tt)/0.8)
    pad=sum(np.sin(2*np.pi*note(m-12)*tt)*0.05 for m in ch[:3])*env
    st=int(t*SR); e=min(n,len(out)-st); out[st:st+e]+=pad[:e]
    t+=4*beat; bar+=1
fade=int(2.5*SR); out[-fade:]*=np.linspace(1,0,fade)
out=out/np.abs(out).max()*0.9
w=wave.open("music.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
