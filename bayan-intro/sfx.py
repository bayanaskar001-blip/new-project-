"""Synthesized (royalty-free) sound effects for the animation events."""
import numpy as np, wave
SR = 44100
rng = np.random.default_rng(7)

def _env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)

def pop(pitch=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = (950 * np.exp(-t * 28) + 260) * pitch
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.028)
    y[:60] += rng.uniform(-1, 1, 60) * np.linspace(0.5, 0, 60)
    return y * 0.55

def whoosh(dur=0.32):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    # moving one-pole lowpass (sweep up) -> airy swoosh
    cut = 0.04 + 0.5 * np.sin(np.pi * t / dur) ** 2
    y = np.zeros(n); acc = 0.0
    for i in range(n):
        acc += cut[i] * (noise[i] - acc); y[i] = acc
    y -= np.convolve(y, np.ones(40) / 40, "same")          # remove rumble
    return y * np.sin(np.pi * t / dur) ** 2 * 1.4

def swish():
    n = int(0.14 * SR)
    y = rng.uniform(-1, 1, n); y = np.diff(y, prepend=0) * 0.5
    return y * _env(n, 0.01, 0.04) * 0.5

def boom():
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 9) + 48
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.003, 0.18)
    y[:400] += rng.uniform(-1, 1, 400) * np.linspace(0.6, 0, 400)
    return np.tanh(y * 1.6) * 0.8

def chime():
    n = int(1.6 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, (f, d) in enumerate([(1046.5, 0.0), (1568.0, 0.12), (2093.0, 0.24)]):
        s = int(d * SR); tt = t[: n - s]
        y[s:] += (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt)) * np.exp(-tt / 0.45) * 0.3
    return y

def build(events, total, path):
    out = np.zeros(int((total + 2) * SR))
    gains = {"pop": 0.32, "whoosh": 0.22, "swish": 0.22, "boom": 0.5, "chime": 0.35}
    last = {}
    for kind, t0 in sorted(events, key=lambda e: e[1]):
        if t0 - last.get(kind, -9) < 0.07: continue           # avoid machine-gun stacking
        last[kind] = t0
        y = {"pop": lambda: pop(rng.uniform(0.85, 1.2)), "whoosh": whoosh, "swish": swish,
             "boom": boom, "chime": chime}[kind]() * gains[kind]
        s = int(max(t0, 0) * SR); e = min(len(out), s + len(y)); out[s:e] += y[: e - s]
    out = np.clip(out, -1, 1)
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
