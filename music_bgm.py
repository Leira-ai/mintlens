"""Compose the MintLens demo BGM — a real little instrumental loop, not a drone.

Style: calm tech-product underscore at 100 BPM. Am–F–C–G progression, two bars
per chord: sustained harmonic pads, a round sine bass on beats 1 and 3, a
Karplus-Strong plucked melody in A-minor pentatonic, and whisper-quiet noise
hats on the offbeats. Synthesized with numpy (system python3 has it; the
project venv does not need it — run with `python3 music_bgm.py [seconds] [out]`).
Master is soft-clipped and peak-normalized so it is clearly audible on a
phone speaker while staying background-appropriate.
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 100.0
BEAT = 60.0 / BPM  # 0.6 s
BAR = 4 * BEAT      # 2.4 s
CHORD_SPAN = 2 * BAR  # 4.8 s per chord

# (pad midi tones, bass midi, melody [(eighth_idx_in_span, midi, gain), ...])
# Span = 16 eighth-notes (2 bars). Chord tones + pentatonic passing tones.
CHORDS = [
    (  # Am
        [57, 60, 64],
        45,
        [(0, 69, 0.9), (2, 72, 0.7), (4, 76, 0.85), (7, 74, 0.6),
         (8, 72, 0.75), (10, 69, 0.7), (12, 67, 0.65), (14, 69, 0.6)],
    ),
    (  # F
        [53, 57, 60],
        41,
        [(0, 69, 0.85), (2, 72, 0.7), (4, 77, 0.8), (7, 76, 0.55),
         (8, 72, 0.7), (10, 69, 0.75), (12, 65, 0.6), (14, 67, 0.55)],
    ),
    (  # C
        [48, 52, 55],
        36 + 12,
        [(0, 72, 0.9), (2, 76, 0.75), (4, 79, 0.85), (7, 76, 0.6),
         (8, 74, 0.65), (10, 72, 0.7), (12, 69, 0.6), (14, 67, 0.6)],
    ),
    (  # G
        [55, 59, 62],
        43,
        [(0, 67, 0.85), (2, 71, 0.7), (4, 74, 0.85), (7, 76, 0.55),
         (8, 74, 0.7), (10, 71, 0.65), (12, 69, 0.6), (14, 67, 0.6)],
    ),
]


def midi_f(m: int) -> float:
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def pluck(freq: float, dur: float, gain: float) -> np.ndarray:
    """Karplus-Strong plucked string."""
    n = max(2, int(SR / freq))
    total = int(dur * SR)
    rng = np.random.default_rng(int(freq * 10))
    buf = rng.uniform(-1.0, 1.0, n)
    out = np.zeros(total)
    idx = 0
    for i in range(total):
        cur = buf[idx]
        out[i] = cur
        nxt = buf[(idx + 1) % n]
        buf[idx] = 0.996 * 0.5 * (cur + nxt)
        idx = (idx + 1) % n
    return out * gain


def pad_tone(freq: float, dur: float, gain: float) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(1.0, t / 0.5) * np.minimum(1.0, (dur - t) / 0.8).clip(0, 1)
    wave_ = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    return wave_ * env * gain


def bass_hit(freq: float, dur: float = 0.55, gain: float = 0.5) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 6.0)
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * env * gain


def hat(dur: float = 0.04, gain: float = 0.05) -> np.ndarray:
    rng = np.random.default_rng(7)
    noise = rng.uniform(-1.0, 1.0, int(dur * SR))
    hp = np.diff(np.concatenate([[0.0], noise]))  # crude high-pass
    return hp * np.exp(-np.arange(len(hp)) / (0.012 * SR)) * gain


def add(mix: np.ndarray, seg: np.ndarray, start_s: float) -> None:
    s = int(start_s * SR)
    e = min(len(mix), s + len(seg))
    if e > s:
        mix[s:e] += seg[: e - s]


def compose(total_s: float) -> np.ndarray:
    mix = np.zeros(int((total_s + 1.0) * SR))
    span_idx = 0
    t0 = 0.0
    while t0 < total_s:
        tones, bass_m, melody = CHORDS[span_idx % len(CHORDS)]
        for m in tones:
            add(mix, pad_tone(midi_f(m), CHORD_SPAN + 0.8, 0.055), t0)
        # bass on beats 1 and 3 of each bar in the span
        for b in range(4):
            add(mix, bass_hit(midi_f(bass_m)), t0 + b * BAR + (0 if b % 2 == 0 else 0))
            add(mix, bass_hit(midi_f(bass_m)), t0 + b * BAR + 2 * BEAT)
        eighth = BEAT / 2.0
        for e_idx, m, g in melody:
            add(mix, pluck(midi_f(m), 1.1, 0.32 * g), t0 + e_idx * eighth)
        for e_idx in range(1, 16, 2):  # offbeat hats
            add(mix, hat(), t0 + e_idx * eighth)
        t0 += CHORD_SPAN
        span_idx += 1
    mix = np.tanh(mix * 1.15)
    peak = np.max(np.abs(mix)) or 1.0
    mix = mix / peak * 0.9
    n = int(total_s * SR)
    mix = mix[:n]
    fade_in = int(1.2 * SR)
    fade_out = int(2.5 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)
    return mix


def main() -> None:
    total = float(sys.argv[1]) if len(sys.argv) > 1 else 74.0
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("bgm_music.wav")
    audio = compose(total)
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out} ({total:.0f}s, peak-normalized)")


if __name__ == "__main__":
    main()
