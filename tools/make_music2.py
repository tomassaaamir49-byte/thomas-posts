"""Second original music style: modern, light, beat-driven (lo-fi pluck + soft kick/hat + sub bass).

Royalty-free (all synthesized). usage: python3 make_music2.py seconds out.wav [seed]
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
KEYS = [220.0, 246.94, 196.0, 261.63]
PROGS = [[0, -4, 3, -2], [0, 5, -3, -5], [0, -5, -2, 3]]  # minor-ish loops


def lp(x, c):
    b, a = butter(2, c / (SR / 2))
    return lfilter(b, a, x)


def hp(x, c):
    b, a = butter(2, c / (SR / 2), "high")
    return lfilter(b, a, x)


def make(seconds, seed=0):
    rng = np.random.default_rng(seed)
    key, prog = KEYS[seed % len(KEYS)], PROGS[seed % len(PROGS)]
    bpm = 96
    beat = 60 / bpm
    bar = 4 * beat
    n = int(seconds * SR)
    out = np.zeros(n)

    def add(sig, start):
        s = int(start * SR)
        if s >= n:
            return
        e = min(n, s + len(sig))
        out[s:e] += sig[: e - s]

    # kick on 1 and 3, softer on the "and" of 4 every other bar
    tk = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 9)
    # hats: filtered noise
    th = np.arange(int(0.06 * SR)) / SR
    hat = hp(rng.standard_normal(len(th)), 7000) * np.exp(-th * 70)
    # snare-ish clap on 2 and 4
    tc = np.arange(int(0.2 * SR)) / SR
    clap = hp(rng.standard_normal(len(tc)), 1500) * np.exp(-tc * 25)

    nb = int(seconds / beat) + 1
    for b in range(nb):
        t0 = b * beat
        if t0 < 1.5:  # short intro: pluck only
            continue
        if b % 4 in (0, 2):
            add(0.9 * kick, t0)
        if b % 4 in (1, 3):
            add(0.22 * clap, t0)
        add(0.10 * hat, t0 + beat / 2)
        add(0.05 * hat, t0)

    # pluck arpeggio (16th-ish) + sub bass per bar
    step = beat / 2
    for k in range(int(seconds / step)):
        t0 = k * step
        root = prog[int(t0 / bar) % len(prog)]
        chord = [root, root + 3, root + 7, root + 10]
        semi = chord[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
        f = key * 2 ** (semi / 12)
        L = int(0.5 * SR)
        tt = np.arange(L) / SR
        env = np.exp(-tt * 9) * np.minimum(1, tt / 0.003)
        tone = np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 + np.sin(2 * np.pi * f * tt)
        add(0.07 * lp(tone, 2500) * env * (0.8 + 0.2 * rng.random()), t0)
    for b in range(int(seconds / bar) + 1):
        t0 = b * bar
        if t0 < 1.5:
            continue
        f = key * 2 ** (prog[b % len(prog)] / 12) / 4
        L = int(bar * SR)
        tt = np.arange(L) / SR
        env = np.minimum(1, tt / 0.02) * np.exp(-tt * 0.6)
        add(0.25 * np.sin(2 * np.pi * f * tt) * env, t0)

    fade = int(1.0 * SR)
    out[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    out[-fade:] *= np.linspace(1, 0, fade)
    out /= np.max(np.abs(out)) + 1e-9
    out *= 0.85
    st = np.stack([out, np.roll(out, int(0.008 * SR))], axis=1)
    return (st * 32767).astype(np.int16)


if __name__ == "__main__":
    secs = float(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    wavfile.write(sys.argv[2], SR, make(secs, seed))
    print(sys.argv[2])
