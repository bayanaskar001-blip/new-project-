# Генерирует фоновую музыку и звуковые эффекты (без авторских прав)
# python3 tools/synth_audio.py ПАПКА [длительность_сек] [bpm]
import sys, numpy as np, wave
SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 26; BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 124
rng = np.random.default_rng(7)
def t(n): return np.arange(int(n * SR)) / SR
def env(n, a=0.002, d=0.2):
    x = t(n); return np.minimum(x / a, 1) * np.exp(-x / d)
def save(name, x):
    x = np.asarray(x)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = np.tanh(x * 1.2) / np.tanh(1.2); x = x / (np.abs(x).max() + 1e-9) * 0.89
    with wave.open(f"{out}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype("<i2").tobytes())
def lp(x, k):  # простой фильтр низких частот
    y = np.copy(x)
    for _ in range(k): y = np.convolve(y, np.ones(5) / 5, "same")
    return y
def kick():
    x = t(0.45); f = 45 + 120 * np.exp(-x / 0.04); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(0.45, 0.001, 0.16) + 0.3 * rng.standard_normal(len(x)) * env(0.45, 0.0005, 0.004)
def clap():
    n = rng.standard_normal(int(0.3 * SR)); e = env(0.3, 0.001, 0.07)
    for d in (0.01, 0.02):
        i = int(d * SR); e2 = env(0.3, 0.001, 0.01)[: len(e) - i]; e[i:i + len(e2)] += e2 * 0.6
    return (n - lp(n, 3)) * e * 0.7
def hat(o=False):
    n = rng.standard_normal(int(0.25 * SR)); h = n - lp(n, 2)
    return h * env(0.25, 0.0005, 0.09 if o else 0.018) * 0.35
def note(fr, n, wavef="saw", d=0.3):
    x = t(n)
    if wavef == "saw": s = sum(np.sin(2 * np.pi * fr * k * x) / k for k in range(1, 9))
    else: s = np.sin(2 * np.pi * fr * x)
    return s * env(n, 0.005, d)
beat = 60 / BPM; N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
def add(buf, x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if i < N: buf[i:j] += x[: j - i] * g
def both(x, at, g=1.0, pan=0.0):
    add(L, x, at, g * (1 - max(pan, 0))); add(R, x, at, g * (1 + min(pan, 0)))
# аккорды Am – F – C – G
roots = [55.0, 43.65, 65.41, 49.0]
chords = [[220, 261.63, 329.63], [174.61, 220, 261.63], [261.63, 329.63, 392], [196, 246.94, 293.66]]
DROP = 2.0  # момент «удара» (логотип)
bar = 4 * beat; nbar = int(DUR / bar) + 1
for b in range(nbar):
    c = b % 4; t0 = b * bar
    pad = sum(note(f, bar, "saw", 1.2) for f in chords[c]); pad = lp(pad, 6) * 0.10
    both(pad, t0, 1, 0.3); both(pad, t0 + 0.012, 1, -0.3)
    for s in range(16):
        ts = t0 + s * beat / 4
        if ts < DROP or ts > DUR - 0.6: continue
        if s % 4 == 0: both(kick(), ts, 0.95)
        if s in (4, 12): both(clap(), ts, 0.55)
        both(hat(s % 4 == 2), ts, 0.5 if s % 2 else 0.3, 0.4 if s % 2 else -0.4)
        if s in (0, 3, 6, 8, 10, 14):  # бас
            both(lp(note(roots[c], beat * 0.9, "saw", 0.25), 4) * 0.5, ts)
        if s in (2, 7, 10, 13):  # арпеджио
            both(lp(note(chords[c][s % 3] * 2, beat / 2, "saw", 0.08), 2) * 0.10, ts, 1, 0.5 if s % 2 else -0.5)
mus = np.stack([L, R], 1)
fade = int(0.8 * SR); mus[-fade:] *= np.linspace(1, 0, fade)[:, None]
save("music", mus)
# эффекты
w = rng.standard_normal(int(0.5 * SR)); e = np.sin(np.linspace(0, np.pi, len(w))) ** 2
save("whoosh", (lp(w, 2) - lp(w, 12)) * e)
r = rng.standard_normal(int(1.8 * SR)); e = np.linspace(0, 1, len(r)) ** 2
save("riser", (r - lp(r, 2)) * e * 0.6 + note(220, 1.8, "sin", 9) * np.linspace(0, 1, len(r)) * 0.2)
x = t(1.4); f = 30 + 90 * np.exp(-x / 0.08)
save("impact", np.sin(2 * np.pi * np.cumsum(f) / SR) * env(1.4, 0.001, 0.5) + lp(rng.standard_normal(len(x)), 3) * env(1.4, 0.001, 0.12))
save("pop", note(880, 0.12, "sin", 0.03) + note(1320, 0.12, "sin", 0.02) * 0.5)
coin = np.concatenate([note(988, 0.08, "sin", 0.05), note(1319, 0.5, "sin", 0.18)])
save("coin", coin)
print("ok")
