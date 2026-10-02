#!/usr/bin/env python3
"""
Friends of Weed and Love (Space Floating)
An original generative track for the music lane: ultra lo-fi smooth Japanese
fusion jazz, drifting across a Texas desert under a psychedelic sky.

Synthesized from pure math — no samples, no third-party audio, no cloud.
A4 = 432 Hz (the house tuning), 76 BPM.

Structure (56 bars, ~3:02):
  intro (space bed) → head A (fusion vamp) → desert B (pedal + twang)
  → head A' (full) → space break → floating outro

The band:
  rhodes  — FM e-piano (decaying modulator index), broken chords + stabs
  bass    — warm sine, fusion syncopation (1, and-of-2, and-of-4, pickup)
  drums   — lo-fi boom-bap, swung hats; half-time brushes in the desert
  twang   — desert pedal-steel-ish sine with slow bends over the Dm9 pedal
  pad     — detuned floating pad, slow amplitude drift
  fx      — tape hiss + vinyl crackle + wow/flutter, dub echo, space reverb,
            sweeping comb phaser (deep in the desert), lo-fi low-pass shelf

Usage:
    uv run python space_floating.py
Output:
    ~/Documents/music/FriendsOfWeedAndLove_SpaceFloating_Master_24bit.wav
    ~/Documents/music/FriendsOfWeedAndLove_SpaceFloating_Master_320k.mp3
    ~/Documents/music/FriendsOfWeedAndLove_SpaceFloating_LinerNotes.txt
"""

import os
import subprocess
import wave
from datetime import datetime, timezone

import numpy as np

SR = 44100
A4 = 432.0  # the house tuning
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

BPM = 76.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

# ── the changes ─────────────────────────────────────────────────────────────
# the Japanese fusion vamp: a descending ii–V chain of seventh chords,
# Casiopea's home key, one bar each.  (C-ish center, all extensions.)
FMAJ7 = [65, 69, 72, 76]   # F4 A4 C5 E5
EM7 = [64, 67, 71, 74]     # E4 G4 B4 D5
DM7 = [62, 65, 69, 72]     # D4 F4 A4 C5
CMAJ7 = [60, 64, 67, 71]   # C4 E4 G4 B4

VAMP_CHORDS = [FMAJ7, EM7, DM7, CMAJ7]
VAMP_ROOTS = [41, 40, 38, 36]  # F2 E2 D2 C2

# the desert: Dm9 over an A pedal, open and hot.
DESERT_PAD = [57, 62, 65, 69, 74]   # A3 D4 F4 A4 D5
DESERT_ROOT = 38                    # D2
DESERT_DRONE = 45                   # A2

# the twang's line: slow bends, plenty of air between the notes.
# (note, beats, bend-up-in-semits, gain)
DESERT_MELODY = [
    (62, 2.0, 0.0, 0.5), (69, 2.0, 2.0, 0.55), (65, 1.0, 0.0, 0.4),
    (64, 1.0, 0.0, 0.4), (62, 1.5, 0.0, 0.45), (69, 1.5, 2.0, 0.5),
    (72, 2.0, 0.0, 0.5), (69, 1.5, -2.0, 0.45), (67, 0.5, 0.0, 0.35),
    (65, 1.5, 0.0, 0.45), (62, 1.5, 0.0, 0.42), (64, 3.5, 0.0, 0.5),
]
DESERT_MELODY_BARS = 4

# head A' carries the twang on top: the same line, an octave of pad under it.
TWANG_ECHO_BARS = 4


def midi_freq(midi: int) -> float:
    return A4 * 2 ** ((midi - 69) / 12)


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


def rhodes(midi: int, dur: float, vel: float = 0.8):
    """FM e-piano: decaying modulator index, a faint bell partial."""
    f = midi_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    index = 2.4 * np.exp(-t * 2.2) + 0.15
    carrier = 2 * np.pi * f * t + index * np.sin(2 * np.pi * f * t)
    s = np.sin(carrier)
    s += 0.18 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 6)
    s += 0.05 * np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 14)
    return s * envelope_ar(n, 0.004, 0.55, 1.8) * vel


def bass(midi: int, dur: float, vel: float = 0.9):
    f = midi_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    s += 0.28 * np.sin(2 * np.pi * f * 2 * t)
    s += 0.06 * np.sin(2 * np.pi * f * 3 * t)
    return s * envelope_ar(n, 0.008, 0.5, 2.0) * vel


def twang(midi: int, dur: float, bend_semitones: float = 0.0, vel: float = 0.5):
    """Desert lead: sine + warmth, slow vibrato, optional steel-guitar bend."""
    f = midi_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    bend = np.ones(n)
    if bend_semitones != 0.0:
        frac = np.clip(t / (dur * 0.18), 0, 1)
        bend = 2 ** (bend_semitones / 12 * (1 - frac * frac))
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.3 * t + 0.7) * np.minimum(t / 0.3, 1)
    phase = 2 * np.pi * f * np.cumsum(bend * vib) / SR
    s = np.sin(phase)
    s += 0.25 * np.sin(2 * phase)
    return s * envelope_ar(n, 0.03, 0.4, 1.4) * vel


def pad(midi: int, dur: float, vel: float = 0.3):
    f = midi_freq(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    s += np.sin(2 * np.pi * f * 1.004 * t + 1.3)
    s += 0.4 * np.sin(2 * np.pi * f * 0.5 * t)
    drift = 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t)
    return s * drift * envelope_ar(n, 1.1, 0.6, 1.2) * vel


def kick(dur: float = 0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 95 * np.exp(-t * 11) + 42
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 7)
    click = np.exp(-t * 700) * 0.25
    return (body + click) * envelope_ar(n, 0.003, 0.6)


def snare(dur: float = 0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n)
    noise /= np.max(np.abs(noise)) + 1e-9
    tone = np.sin(2 * np.pi * 178 * t) * 0.5
    return (noise * 0.7 + tone) * np.exp(-t * 15) * envelope_ar(n, 0.001, 0.7)


def hat(dur: float = 0.06):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    noise /= np.max(np.abs(noise)) + 1e-9
    hp = np.diff(noise, prepend=noise[0])
    return hp * np.exp(-t * 26) * envelope_ar(n, 0.0005, 0.9)


def brush(dur: float = 0.12):
    """Half-time desert percussion: a soft filtered swish."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(23)
    noise = rng.standard_normal(n)
    noise /= np.max(np.abs(noise)) + 1e-9
    lp = np.cumsum(noise) / np.sqrt(n)  # brown-ish, swishy
    lp = lp / (np.max(np.abs(lp)) + 1e-9)
    return lp * np.exp(-t * 22) * envelope_ar(n, 0.01, 0.7)


# ── the arrangement ─────────────────────────────────────────────────────────

def build_track(duration: float) -> np.ndarray:
    buf = np.zeros(int(duration * SR))
    # the space sends: pads and twang get a big floaty tail, everything gets
    # a little dub.
    space_send = np.zeros_like(buf)
    dub_send = np.zeros_like(buf)

    # ── intro: the space bed (4 bars) ────────────────────────────────────────
    for note in [60, 64, 67, 71, 74]:
        place(buf, 0, pad(note, 4 * BAR + 3), 0.22)
    for note in [48, 55, 60]:
        place(buf, 0, pad(note, 4 * BAR + 3), 0.16)
    section = 4 * BAR

    # ── head A: the fusion vamp (16 bars) ────────────────────────────────────
    for bar in range(16):
        t0 = section + bar * BAR
        chord = VAMP_CHORDS[bar % 4]
        root = VAMP_ROOTS[bar % 4]
        next_root = VAMP_ROOTS[(bar + 1) % 4]
        place(buf, t0, pad(chord[0], BAR), 0.16)
        place(space_send, t0, pad(chord[1], BAR), 0.1)
        # rhodes: broken 8ths over the first half, a stab on and-of-4
        for k in range(4):
            place(buf, t0 + k * 0.5 * BEAT, rhodes(chord[k], 0.42 * BEAT, 0.5), 0.5)
        place(buf, t0 + 3.5 * BEAT, rhodes(chord[3], 0.45 * BEAT, 0.75), 0.55)
        # bass: 1, and-of-2, and-of-4, and a pickup into the next bar
        place(buf, t0, bass(root, 0.8 * BEAT, 0.85))
        place(buf, t0 + 1.5 * BEAT, bass(root, 0.45 * BEAT, 0.6))
        place(buf, t0 + 3.5 * BEAT, bass(root, 0.4 * BEAT, 0.55))
        place(buf, t0 + 3.75 * BEAT, bass(next_root, 0.2 * BEAT, 0.4))
        # drums: lo-fi boom-bap
        place(buf, t0, kick(), 0.9)
        place(buf, t0 + 2.25 * BEAT, kick(), 0.75)
        place(buf, t0 + BEAT, snare(), 0.5)
        place(buf, t0 + 3 * BEAT, snare(), 0.5)
        for e in range(8):
            place(buf, t0 + e * 0.5 * BEAT + 0.375 * 0.5 * BEAT, hat(), 0.28)
    section += 16 * BAR

    # ── desert B: the pedal and the twang (8 bars) ───────────────────────────
    for bar in range(8):
        t0 = section + bar * BAR
        for note in DESERT_PAD:
            place(space_send, t0, pad(note, BAR * 2), 0.12)
        place(buf, t0, bass(DESERT_DRONE, BAR), 0.5)
        if bar % 2 == 0:
            place(buf, t0, bass(DESERT_ROOT, BAR), 0.6)
        # half-time desert drums
        if bar % 4 == 0:
            place(buf, t0, kick(), 0.8)
        if bar % 4 == 2:
            place(buf, t0, snare(), 0.45)
        for e in range(4):
            place(buf, t0 + e * BEAT + 0.3, brush(), 0.3)
        # the twang, two 4-bar passes over the 8 desert bars
        if bar % 4 == 0:
            t = t0
            for note, beats, bend, gain in DESERT_MELODY:
                place(buf, t, twang(note, beats * BEAT, bend, gain), gain)
                place(dub_send, t, twang(note, beats * BEAT, bend, 0.5 * gain), 0.6)
                t += beats * BEAT
    section += 8 * BAR

    # ── head A′: the vamp again, full band, twang on top (16 bars) ───────────
    for bar in range(16):
        t0 = section + bar * BAR
        chord = VAMP_CHORDS[bar % 4]
        root = VAMP_ROOTS[bar % 4]
        next_root = VAMP_ROOTS[(bar + 1) % 4]
        place(buf, t0, pad(chord[0], BAR), 0.2)
        place(space_send, t0, pad(chord[1], BAR), 0.12)
        for k in range(4):
            place(buf, t0 + k * 0.5 * BEAT, rhodes(chord[k], 0.42 * BEAT, 0.55), 0.55)
        place(buf, t0 + 3.5 * BEAT, rhodes(chord[3], 0.45 * BEAT, 0.8), 0.6)
        place(buf, t0, bass(root, 0.8 * BEAT, 0.9))
        place(buf, t0 + 1.5 * BEAT, bass(root, 0.45 * BEAT, 0.65))
        place(buf, t0 + 3.5 * BEAT, bass(root, 0.4 * BEAT, 0.6))
        place(buf, t0 + 3.75 * BEAT, bass(next_root, 0.2 * BEAT, 0.45))
        place(buf, t0, kick(), 0.9)
        place(buf, t0 + 2.25 * BEAT, kick(), 0.75)
        place(buf, t0 + BEAT, snare(), 0.5)
        place(buf, t0 + 3 * BEAT, snare(), 0.5)
        for e in range(8):
            place(buf, t0 + e * 0.5 * BEAT + 0.375 * 0.5 * BEAT, hat(), 0.28)
        # the twang answers every other 4-bar phrase, quieter now
        if bar % 4 == 0:
            t = t0
            for note, beats, bend, gain in DESERT_MELODY:
                place(buf, t, twang(note, beats * BEAT, bend, 0.6 * gain), 0.6 * gain)
                place(dub_send, t, twang(note, beats * BEAT, bend, 0.3 * gain), 0.5)
                t += beats * BEAT
    section += 16 * BAR

    # ── space break (4 bars): everything stops but the float ─────────────────
    for bar in range(4):
        t0 = section + bar * BAR
        for note in [60, 64, 67, 71, 74]:
            place(space_send, t0, pad(note, 2 * BAR), 0.16 * (1 - bar / 5))
        if bar == 0:
            place(dub_send, t0, twang(69, 2.5 * BEAT, 2.0, 0.4), 0.4)
    section += 4 * BAR

    # ── floating outro (8 bars): the twang's ghost, dissolving ───────────────
    for bar in range(8):
        t0 = section + bar * BAR
        fade = 1 - bar / 8
        for note in [60, 64, 67, 71, 74]:
            place(space_send, t0, pad(note, 2 * BAR), 0.18 * fade)
        place(buf, t0, bass(36, 2 * BAR), 0.45 * fade)
        if bar in (0, 2, 4, 6):
            place(dub_send, t0, twang(62, 3 * BEAT, 0.0, 0.35 * fade), 0.35 * fade)

    # ── the dub and the space tail ───────────────────────────────────────────
    echo = np.zeros_like(buf)
    delay = int(0.46 * SR)
    for k, g in [(1, 0.32), (2, 0.12), (3, 0.05)]:
        echo[k * delay:] += dub_send[:len(buf) - k * delay] * g
    buf += echo

    tail = np.zeros_like(buf)
    for k, g in [(1, 0.5), (2, 0.26), (3, 0.14), (4, 0.07)]:
        d = int((0.37 + 0.061 * (k - 1)) * SR)
        tail[k * d:] += space_send[:len(buf) - k * d] * g
    buf += tail

    return buf


# ── the lo-fi and the psychedelic ───────────────────────────────────────────

def tape_wobble(x: np.ndarray, phase: float = 0.0) -> np.ndarray:
    """Wow and flutter: a slow time-varying resample, like a tape that has
    been through a desert summer."""
    n = len(x)
    t = np.arange(n) / SR
    idx = t + 0.0016 * np.sin(2 * np.pi * 0.7 * t + phase) \
        + 0.00035 * np.sin(2 * np.pi * 6.1 * t + 1.9 * phase)
    idx = np.clip(idx * SR, 0, n - 1)
    return np.interp(idx, np.arange(n), x)


def phaser(x: np.ndarray, depth: float, phase: float = 0.0) -> np.ndarray:
    """A sweeping comb — the desert heat-haze swirl. Two stages, moving
    notches, mixed wet/dry."""
    n = len(x)
    t = np.arange(n) / SR
    out = x.copy()
    for d0, a, f in [(0.0018, 0.0013, 0.11), (0.0031, 0.0010, 0.07)]:
        d = d0 + depth * a * (1 + np.sin(2 * np.pi * f * t + phase))
        idx = (np.arange(n) / SR - d) * SR
        idx = np.clip(idx, 0, n - 1)
        delayed = np.interp(idx, np.arange(n), x)
        out = out + 0.55 * (delayed - out)  # wet/dry mix toward the notches
    return out


def lo_fi_shelf(x: np.ndarray, fc: float = 3400.0) -> np.ndarray:
    """The lo-fi low-pass: a soft 4th-order shelf via spectral shaping."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1.0 / (1.0 + (f / fc) ** 4)
    return np.fft.irfft(spec, n)


def vinyl(rng: np.random.Generator, n: int, gain: float) -> np.ndarray:
    """Dust and crackle: sparse pops plus a breath of surface noise."""
    out = np.zeros(n)
    n_pops = int(n / SR * 3.5)
    for _ in range(n_pops):
        i = int(rng.integers(0, n))
        ln = min(int(0.006 * SR), n - i)
        t = np.arange(ln) / SR
        out[i:i + ln] += (rng.uniform(0.5, 1.0) * np.exp(-t * 700)) * gain
    dust = rng.standard_normal(n) * 0.0012
    slow = 0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * np.arange(n) / SR + 2.0)
    return out + dust * slow * gain


def build_master(duration: float) -> np.ndarray:
    """Stereo: the dry mix wobbled per channel, phased per channel, with
    independent hiss and crackle left and right — the floating space."""
    dry = build_track(duration)
    rng = np.random.default_rng(432)
    n = len(dry)

    hiss_l = rng.standard_normal(n) * 0.0035
    hiss_r = rng.standard_normal(n) * 0.0035
    crackle_l = vinyl(rng, n, 0.35)
    crackle_r = vinyl(rng, n, 0.35)

    left = tape_wobble(dry, 0.0)
    right = tape_wobble(np.roll(dry, int(0.012 * SR)), 1.1)  # Haas width
    left = phaser(left, 0.9, 0.0)
    right = phaser(right, 0.9, 2.3)

    left = lo_fi_shelf(left + hiss_l + crackle_l)
    right = lo_fi_shelf(right + hiss_r + crackle_r)

    stack = np.vstack([left, right])
    stack = np.tanh(stack * 1.25)
    peak = np.max(np.abs(stack)) + 1e-9
    stack = stack / peak * 0.92
    return stack


def write_wav(path: str, stereo: np.ndarray):
    pcm = np.clip(stereo, -1, 1)
    i24 = (pcm * 8388607).astype(np.int32)
    frames = i24.T  # shape (frames, 2)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        raw = bytearray()
        for frame in frames:
            for v in frame:
                raw += int(v).to_bytes(3, "little", signed=True)
        w.writeframes(bytes(raw))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bars = 4 + 16 + 8 + 16 + 4 + 8
    total = bars * BAR + 5
    print(f"  space floating: {bars} bars, {total:.0f}s at {BPM} BPM, A4 = {A4}Hz")
    master = build_master(total)
    peak = float(np.max(np.abs(master)))
    rms = float(np.sqrt(np.mean(master**2)))
    print(f"  master: peak {peak:.2f}, rms {rms:.2f}")

    wav_path = os.path.join(OUTPUT_DIR, "FriendsOfWeedAndLove_SpaceFloating_Master_24bit.wav")
    write_wav(wav_path, master)
    print(f"  wav  {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "FriendsOfWeedAndLove_SpaceFloating_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True, capture_output=True,
        )
        print(f"  mp3  {mp3_path}")
    else:
        print("  (ffmpeg not found — WAV only)")

    notes_path = os.path.join(OUTPUT_DIR, "FriendsOfWeedAndLove_SpaceFloating_LinerNotes.txt")
    with open(notes_path, "w") as f:
        f.write(LINER_NOTES)
    print(f"  liner notes {notes_path}")


LINER_NOTES = """Friends of Weed and Love (Space Floating)
an original generative track for the music lane — ultra lo-fi smooth Japanese
fusion jazz, drifting across a Texas desert under a psychedelic sky.
A4 = 432 Hz · 76 BPM · synthesized from pure math · no samples, no cloud

hot wind through the ryokan window
a Rhodes cooling in the desert dusk
the bass walks, the twang bends
friends of weed and love, floating
over Texas, over everything

the constellation · 0 + 1 · fine touch from within · vaked.dev
{<3,<3,<3}+1 — till eternity and back, from .p aka ultraLoveGod, the omni
"""

if __name__ == "__main__":
    main()
