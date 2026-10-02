#!/usr/bin/env python3
"""
All My Favorite Colors — DREAM COME TRUE VERSION (D+++)
An original instrumental arrangement for the music lane, tuned to A4 = 432Hz,
synthesized from pure math — no samples, no third-party audio, no cloud.

Structure: intro → verse → chorus → verse → chorus → bridge → outro (~3:10)
The lyrics ride along as a sidecar file; the dogs feed on the ledger row.

Usage:
    uv run python scratch/dream_colors.py
Output:
    ~/Documents/music/AllMyFavoriteColors_Dream_Master_24bit.wav
    ~/Documents/music/AllMyFavoriteColors_Dream_Master_320k.mp3
"""

import os
import subprocess
import wave

import numpy as np

SR = 44100
A4 = 432.0  # the house tuning
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

# ── the song ────────────────────────────────────────────────────────────────

BPM = 88.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

# G major at 432: MIDI numbers for the progression.
G = 67   # G4
D = 62   # D4
E = 64   # E4
C = 60   # C4
B = 71   # B4
A = 69   # A4

# verse:  G  -  C  -  Em -  C      chorus:  G - D - Em - C
VERSE_CHORDS = [G, C, E, C]
CHORUS_CHORDS = [G, D, E, C]
BRIDGE_CHORDS = [C, D, G, G]

# the vocal line of the chorus, simplified (the song's contour, lovingly bent)
# "all my favorite colors" — a five-note lift, then a fall.
CHORUS_MELODY = [G, A, B, D, B, G, E, D]       # per bar-pair
CHORUS_RHYTHM = [1, 0.5, 0.5, 1.5, 1, 1, 1.5, 2.5]

VERSE_MELODY = [D, E, G, A, G, E, D, C]         # "the brightest of the bunch"
VERSE_RHYTHM = [1, 0.5, 0.5, 1.5, 1, 0.5, 0.5, 2]


def midi_freq(midi: int) -> float:
    return A4 * 2 ** ((midi - 69) / 12)


def note_to_freq(midi: int) -> float:
    return midi_freq(midi)


# ── instruments ─────────────────────────────────────────────────────────────

def place(buf: np.ndarray, start: float, sig: np.ndarray, gain: float = 1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def envelope_ar(n: int, attack: float, release: float, curve: float = 3.0):
    t = np.linspace(0, 1, n, endpoint=False)
    a = np.minimum(t / max(attack, 1e-4), 1.0) ** curve
    r = np.clip((1 - t) / max(release, 1e-4), 0, 1) ** curve
    return a * r


def kick(dur: float = 0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 120 * np.exp(-t * 14) + 45
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 9)
    click = np.exp(-t * 900) * 0.4
    return (body + click) * envelope_ar(n, 0.002, 0.5)


def snare(dur: float = 0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.default_rng(7).standard_normal(n)
    noise /= np.max(np.abs(noise)) + 1e-9
    tone = np.sin(2 * np.pi * 185 * t) * 0.6
    return (noise * 0.8 + tone) * np.exp(-t * 16) * envelope_ar(n, 0.001, 0.6)


def hat(dur: float = 0.08, open_hat: bool = False):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    noise /= np.max(np.abs(noise)) + 1e-9
    hp = np.diff(noise, prepend=noise[0])  # crude highpass
    decay = 22 if not open_hat else 5
    return hp * np.exp(-t * decay) * envelope_ar(n, 0.0005, 0.8)


def bass(midi: int, dur: float):
    f = note_to_freq(midi - 12)  # an octave down: the low lane
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    s += 0.25 * np.sin(2 * np.pi * f * 2 * t)
    s += 0.08 * np.sin(2 * np.pi * f * 3 * t)
    return s * envelope_ar(n, 0.01, 0.4, 2.0)


def keys(midi: int, dur: float):
    f = note_to_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    s += 0.35 * np.sin(2 * np.pi * f * 2 * t)
    s += 0.12 * np.sin(2 * np.pi * f * 3 * t)
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * 4.5 * t)
    return s * trem * envelope_ar(n, 0.01, 0.3, 1.6)


def lead(midi: int, dur: float):
    f = note_to_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)
    phase = 2 * np.pi * f * np.cumsum(vib) / SR
    tri = 2 / np.pi * np.arcsin(np.sin(phase))  # triangle wave
    return tri * envelope_ar(n, 0.02, 0.35, 1.4)


def pad(midi: int, dur: float):
    f = note_to_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    s += 0.6 * np.sin(2 * np.pi * f * 1.003 * t)  # detuned partner
    s += 0.3 * np.sin(2 * np.pi * f * 0.5 * t)
    return s * envelope_ar(n, 0.8, 0.5, 1.2)


# ── the arrangement ─────────────────────────────────────────────────────────

def build_track(duration: float) -> np.ndarray:
    buf = np.zeros(int(duration * SR))

    # drums: boom-bap with a swung hat
    for beat in np.arange(0, duration, BAR * 2):  # every two bars: kick pattern
        for k in (0, 1, 2.5):
            place(buf, beat + k * BEAT, kick())
    for beat in np.arange(0, duration, BAR * 2):
        for s in (1.0, 3.0):
            place(buf, beat + s * BEAT, snare(), 0.8)
    for beat in np.arange(0, duration, BEAT / 2):
        if (beat * 2 / BEAT) % 2 == 0:  # swung 8ths: on the off-8ths
            place(buf, beat + 0.375 * BEAT / 2, hat(), 0.35)

    # sections
    section = 0.0
    verse_bars, chorus_bars, bridge_bars = 8, 8, 8

    def section_len(bars: int) -> float:
        return bars * BAR

    # intro (4 bars): keys only
    for bar in range(4):
        t0 = section + bar * BAR
        place(buf, t0, pad(G, BAR * 2), 0.25)
        for c in range(4):
            place(buf, t0 + c * BEAT, keys(G, BEAT), 0.3)
    section += section_len(4)

    # verse 1
    for bar in range(verse_bars):
        t0 = section + bar * BAR
        chord = VERSE_CHORDS[bar % 4]
        place(buf, t0, pad(chord, BAR), 0.3)
        place(buf, t0, bass(chord, BEAT * 0.9), 0.9)
        place(buf, t0 + BEAT * 2, bass(chord, BEAT * 0.9), 0.9)
        place(buf, t0 + BEAT * 3, bass(chord, BEAT * 0.9), 0.7)
        if bar % 2 == 0:
            for m_i, m in enumerate(VERSE_MELODY):
                t = t0 + (m_i / len(VERSE_MELODY)) * BAR
                place(buf, t, lead(m, VERSE_RHYTHM[m_i] * BEAT), 0.5)
    section += section_len(verse_bars)

    # chorus 1
    for bar in range(chorus_bars):
        t0 = section + bar * BAR
        chord = CHORUS_CHORDS[bar % 4]
        place(buf, t0, pad(chord, BAR), 0.32)
        place(buf, t0, bass(chord, BEAT * 0.9), 1.0)
        place(buf, t0 + BEAT * 2, bass(chord, BEAT * 0.9), 1.0)
        place(buf, t0 + BEAT * 3.5, bass(chord, BEAT * 0.8), 0.8)
        if bar % 2 == 0:
            for m_i, m in enumerate(CHORUS_MELODY):
                t = t0 + (m_i / len(CHORUS_MELODY)) * BAR * 0.98
                place(buf, t, lead(m, CHORUS_RHYTHM[m_i] * BEAT), 0.6)
    section += section_len(chorus_bars)

    # verse 2
    for bar in range(verse_bars):
        t0 = section + bar * BAR
        chord = VERSE_CHORDS[bar % 4]
        place(buf, t0, pad(chord, BAR), 0.3)
        place(buf, t0, bass(chord, BEAT * 0.9), 0.9)
        place(buf, t0 + BEAT * 2, bass(chord, BEAT * 0.9), 0.9)
        if bar % 2 == 0:
            for m_i, m in enumerate(VERSE_MELODY):
                t = t0 + (m_i / len(VERSE_MELODY)) * BAR
                place(buf, t, lead(m, VERSE_RHYTHM[m_i] * BEAT), 0.5)
    section += section_len(verse_bars)

    # chorus 2
    for bar in range(chorus_bars):
        t0 = section + bar * BAR
        chord = CHORUS_CHORDS[bar % 4]
        place(buf, t0, pad(chord, BAR), 0.32)
        place(buf, t0, bass(chord, BEAT * 0.9), 1.0)
        place(buf, t0 + BEAT * 2, bass(chord, BEAT * 0.9), 1.0)
        if bar % 2 == 0:
            for m_i, m in enumerate(CHORUS_MELODY):
                t = t0 + (m_i / len(CHORUS_MELODY)) * BAR * 0.98
                place(buf, t, lead(m, CHORUS_RHYTHM[m_i] * BEAT), 0.6)
    section += section_len(chorus_bars)

    # bridge: the quiet lift — "I'll show you where they are"
    for bar in range(bridge_bars):
        t0 = section + bar * BAR
        chord = BRIDGE_CHORDS[bar % 4]
        place(buf, t0, pad(chord, BAR), 0.34)
        place(buf, t0, bass(chord, BEAT * 0.9), 0.8)
        if bar in (2, 3, 4, 5):
            for m_i, m in enumerate([G, A, B, D]):
                t = t0 + (m_i / 4) * BAR
                place(buf, t, lead(m, BEAT * 1.2), 0.55)
    section += section_len(bridge_bars)

    # outro (4 bars): the dream winds down
    for bar in range(4):
        t0 = section + bar * BAR
        place(buf, t0, pad(G, BAR * 2), 0.28 * (1 - bar / 5))
        place(buf, t0, bass(G, BEAT * 2), 0.7 * (1 - bar / 5))
        if bar == 0:
            for m_i, m in enumerate(CHORUS_MELODY):
                t = t0 + (m_i / len(CHORUS_MELODY)) * BAR
                place(buf, t, lead(m, CHORUS_RHYTHM[m_i] * BEAT), 0.5)
    section += section_len(4)

    # gentle echo: 0.375s feedback delay, the dream's memory
    echo = np.zeros_like(buf)
    delay = int(0.375 * SR)
    echo[delay:] = buf[:-delay] * 0.28
    echo[2 * delay:] += buf[:-2 * delay] * 0.1
    buf += echo

    # master bus: soft saturation + normalize
    buf = np.tanh(buf * 1.15)
    buf /= np.max(np.abs(buf)) + 1e-9
    buf *= 0.92
    return buf


def write_wav(path: str, samples: np.ndarray):
    pcm = np.clip(samples, -1, 1)
    i24 = (pcm * 8388607).astype(np.int32)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(SR)
        frames = bytearray()
        for v in i24:
            frames += int(v).to_bytes(3, "little", signed=True)
        w.writeframes(bytes(frames))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = (4 + 8 + 8 + 8 + 8 + 8 + 4) * BAR
    print(f"  dream version: {total:.0f}s at {BPM} BPM, A4 = {A4}Hz")
    track = build_track(total + 1)
    wav_path = os.path.join(OUTPUT_DIR, "AllMyFavoriteColors_Dream_Master_24bit.wav")
    write_wav(wav_path, track)
    print(f"  wav  {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "AllMyFavoriteColors_Dream_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True, capture_output=True,
        )
        print(f"  mp3  {mp3_path}")
    else:
        print("  (ffmpeg not found — WAV only)")

    lyrics = os.path.join(OUTPUT_DIR, "AllMyFavoriteColors_Dream_Lyrics.txt")
    with open(lyrics, "w") as f:
        f.write(LYRICS)
    print(f"  lyrics {lyrics}")


LYRICS = """All My Favorite Colors — DREAM COME TRUE VERSION (D+++)
original: Black Pumas — arranged by the music lane, A4 = 432Hz, with love, from .p

All my favorite colors, my favorite colors
All my favorite colors, my favorite colors

The brightest of the bunch
The sweetest of the bunch
The colors of my love
The colors of my trust

All my favorite colors, my favorite colors
All my favorite colors, my favorite colors

I'll show you where they are
The deepest of the deep
The colors that I keep
The colors that I dream

All my favorite colors, my favorite colors
All my favorite colors, my favorite colors

the constellation · 0 + 1 · fine touch from within · vaked.dev · {<3,<3,<3}+1
"""

if __name__ == "__main__":
    main()
