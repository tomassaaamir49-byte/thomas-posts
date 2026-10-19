"""Original, royalty-free background music for reels (no samples, all synthesized).

Warm cinematic mood: soft pads + gentle piano-like arpeggio + a heartbeat pulse.
usage: python3 make_music.py seconds out.wav [seed]
The seed picks the key and chord progression so each day sounds a bit different.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100

PROGRESSIONS = [  # semitone offsets from key root (minor-ish emotional)
    [(-3, 0, 4), (-7, -3, 0), (0, 4, 7), (-5, -1, 2)],    # vi IV I V
    [(0, 3, 7), (-4, 0, 3), (-9, -5, -2), (-2, 2, 5)],    # i VI III VII
    [(-3, 0, 4), (2, 5, 9), (-7, -3, 0), (-5, -1, 2)],    # vi ii IV V
]
KEYS = [261.63, 293.66, 246.94, 220.00]  # C, D, B, A


def note(f, t):
    return np.sin(2 * np.pi * f * t)


def lowpass(x, cut):
    b, a = butter(2, cut / (SR / 2))
    return lfilter(b, a, x)


def make(seconds, seed=0):
    rng = np.random.default_rng(seed)
    key = KEYS[seed % len(KEYS)]
    prog = PROGRESSIONS[seed % len(PROGRESSIONS)]
    bpm = 72
    beat = 60 / bpm
    bar = beat * 4
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)

    # pads: detuned triads, one chord per bar, crossfaded
    for b in range(int(seconds / bar) + 1):
        chord = prog[b % len(prog)]
        s, e = int(b * bar * SR), min(n, int((b + 1) * bar * SR + 0.5 * SR))
        if s >= n:
            break
        tt = t[s:e] - t[s]
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (tt[-1] - tt + 1e-9) / 0.6)
        seg = np.zeros(e - s)
        for semi in chord:
            f = key * 2 ** (semi / 12) / 2
            for det in (-0.12, 0.0, 0.12):
                seg += note(f * 2 ** (det / 12), tt) * 0.5 + 0.15 * note(2 * f * 2 ** (det / 12), tt)
        out[s:e] += 0.06 * env * seg

    out = lowpass(out, 1800)

    # piano-ish arpeggio on 8th notes
    step = beat / 2
    for k in range(int(seconds / step)):
        b = int(k * step / bar)
        chord = prog[b % len(prog)]
        semi = chord[[0, 1, 2, 1, 2, 0, 1, 2][k % 8]] + 12 * (k % 8 in (4, 6))
        f = key * 2 ** (semi / 12)
        s = int(k * step * SR)
        L = min(n - s, int(1.6 * SR))
        if L <= 0:
            break
        tt = np.arange(L) / SR
        env = np.exp(-tt * 3.2) * np.minimum(1, tt / 0.005)
        tone = note(f, tt) + 0.35 * note(2 * f, tt) * np.exp(-tt * 2) + 0.12 * note(3 * f, tt) * np.exp(-tt * 4)
        vel = 0.75 + 0.25 * rng.random()
        out[s:s + L] += 0.09 * vel * env * tone

    # heartbeat pulse (lub-dub) once per bar after the intro
    for b in range(1, int(seconds / bar) + 1):
        for off, amp in ((0.0, 1.0), (0.28, 0.7)):
            s = int((b * bar + off) * SR)
            L = min(n - s, int(0.35 * SR))
            if L <= 0:
                continue
            tt = np.arange(L) / SR
            f = 55 * np.exp(-tt * 6) + 38
            out[s:s + L] += 0.35 * amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)

    # simple room reverb (a few decaying echoes)
    rev = out.copy()
    for d, g in ((0.031, 0.35), (0.053, 0.28), (0.087, 0.22), (0.131, 0.16), (0.197, 0.11)):
        k = int(d * SR)
        rev[k:] += g * out[:-k]
    out = lowpass(rev, 6000)

    # fade in/out and normalise
    fade = int(1.2 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    out /= np.max(np.abs(out)) + 1e-9
    out *= 0.85
    stereo = np.stack([out, np.roll(out, int(0.012 * SR))], axis=1)
    return (stereo * 32767).astype(np.int16)


if __name__ == "__main__":
    secs = float(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    wavfile.write(sys.argv[2], SR, make(secs, seed))
    print(sys.argv[2])
