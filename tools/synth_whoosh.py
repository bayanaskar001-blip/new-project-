# Новый «вжух» (swoosh): шум с плавающей полосой частот + движение слева направо
# python3 tools/synth_whoosh.py ПАПКА
import sys, numpy as np, wave
SR = 44100; out = sys.argv[1]; rng = np.random.default_rng(3)
def save(name, L, R):
    x = np.stack([L, R], 1); x = x / (np.abs(x).max() + 1e-9) * 0.9
    with wave.open(f"{out}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype("<i2").tobytes())
def whoosh(dur, f_lo, f_hi, peak=0.6, width=0.7, skew=1.0):
    n = int(dur * SR); N = 2048; H = 256; win = np.hanning(N)
    noise = rng.standard_normal(n + N); y = np.zeros(n + N); freqs = np.fft.rfftfreq(N, 1 / SR)
    for i in range(0, n, H):
        p = i / n
        # частота растёт к пику и спадает после
        k = np.sin(np.pi * min(p / peak, 1) / 2) if p < peak else np.cos(np.pi * (p - peak) / (1 - peak) / 2) ** skew
        fc = f_lo * (f_hi / f_lo) ** k
        g = np.exp(-0.5 * (np.log2(np.maximum(freqs, 20) / fc) / width) ** 2)
        y[i:i + N] += np.fft.irfft(np.fft.rfft(noise[i:i + N] * win) * g) * win
    y = y[:n]; t = np.arange(n) / n
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-((t - peak) / (1 - peak)) * 4.5))
    y *= env
    pan = np.clip(t * 1.3 - 0.15, 0, 1)  # слева направо
    return y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)
L, R = whoosh(0.42, 250, 4200, peak=0.62, width=0.55); save("whoosh", L, R)
L, R = whoosh(0.55, 180, 2600, peak=0.5, width=0.8)
# мягкий низкий «тук» в конце для карточек
n = len(L); t = np.arange(n) / SR; i0 = int(0.27 * SR)
thump = np.zeros(n); tt = t[: n - i0]; thump[i0:] = np.sin(2 * np.pi * (70 * tt - 60 * tt ** 2)) * np.exp(-tt / 0.08) * 0.5
save("whoosh_card", L + thump, R + thump)
print("ok")
