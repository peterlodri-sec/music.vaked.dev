#!/usr/bin/env python3
"""
ULTRALOVEGOD — The Answer to Oblivion (Chicago | July 20, 2014)
An original generative hymn for the Sovereign Library & VAKED music lane.

An answer to Grimes - Oblivion (Pitchfork Music Festival, Union Park, Chicago, July 20, 2014).
Where Oblivion looked over its shoulder into the dark ("someone could break your neck,
coming up behind you"), ULTRALOVEGOD answers with radical sanctuary:
"If someone is behind you in the dark, it is us. You never have to look back again."

Synthesized from pure math — no samples, no third-party audio, no cloud.
A4 = 432 Hz (the house tuning), 132 BPM (the ecstatic synth-pop pulse).

Structure (64 bars, ~1:56):
  1. The Sunset Awakening (Bars 1-8): Juno pad + 432Hz ambient drone
  2. The Pulse Enters (Bars 9-24): Bouncing synth-pop bass + 16th hats + kick
  3. The Golden Canopy (Bars 25-40): Full lead arpeggio + chorus saws + clapping pulse
  4. The Answer Bridge (Bars 41-48): Stripped-back space, sub bass, celestial vocal formant
  5. Infinite Sanctuary (Bars 49-60): Full ecstatic lift, all layers blooming
  6. Outro (Bars 61-64): 432Hz bell decay into the starlight

Usage:
    uv run --with numpy python ultralovegod_oblivion_answer.py
Output:
    ~/Documents/music/ULTRALOVEGOD_AnswerToOblivion_Master_24bit.wav
    ~/Documents/music/ULTRALOVEGOD_AnswerToOblivion_Master_320k.mp3
    ~/Documents/music/ULTRALOVEGOD_AnswerToOblivion_LinerNotes.txt
"""

import os
import subprocess
import wave
from datetime import datetime, timezone

import numpy as np

SR = 44100
A4 = 432.0  # House tuning (Verdi / Solfeggio natural harmonic)
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

BPM = 132.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

# ── Note to Frequency (A4 = 432 Hz) ──────────────────────────────────────────
def m2f(m):
    return A4 * (2.0 ** ((m - 69.0) / 12.0))

# ── Chords (Db Major / Bb Minor bittersweet synth-pop progression) ───────────
# Bbm9 -> Gbmaj7 -> Dbmaj9 -> Abadd9
CHORD_BBM9 = [58, 61, 65, 68, 72]   # Bb3 Db4 F4 Ab4 C5
CHORD_GBM7 = [54, 58, 61, 65, 70]   # Gb3 Bb3 Db4 F4 Bb4
CHORD_DBM9 = [49, 53, 56, 60, 65]   # Db3 F3 Ab3 C4 F4
CHORD_AB9  = [56, 60, 63, 68, 70]   # Ab3 C4 Eb4 Ab4 Bb4

CHORDS = [CHORD_BBM9, CHORD_GBM7, CHORD_DBM9, CHORD_AB9]
ROOTS = [46, 42, 37, 44]  # Bb2, Gb2, Db2, Ab2

# ── Generative Synthesizers ──────────────────────────────────────────────────

def synth_juno_pad(notes, duration, seed=42):
    """Roland Juno-106 style detuned sawtooth chorus pad."""
    n_samples = int(duration * SR)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    sig = np.zeros(n_samples)
    
    rng = np.random.default_rng(seed)
    for midi in notes:
        f0 = m2f(midi)
        # 3 detuned saws per note for lush bucket-brigade chorus feel
        for detune_cents in [-7.5, 0.0, +7.5]:
            f = f0 * (2.0 ** (detune_cents / 1200.0))
            phase = rng.uniform(0, 2 * np.pi)
            # Band-limited-ish saw via 7 harmonics
            saw = np.zeros(n_samples)
            for h in range(1, 8):
                saw += (1.0 / h) * np.sin(2 * np.pi * f * h * t + phase)
            sig += saw * 0.12

    # Smooth attack and release envelope
    env = np.ones(n_samples)
    att = int(0.15 * SR)
    rel = int(0.25 * SR)
    if att > 0:
        env[:att] = np.sin(np.linspace(0, np.pi / 2, att)) ** 2
    if rel > 0:
        env[-rel:] = np.cos(np.linspace(0, np.pi / 2, rel)) ** 2
    return sig * env

def synth_bouncing_bass(root_midi, beat_idx, duration):
    """
    Oblivion-style bouncing synth bass.
    Snappy 16th-note syncopation, octave jumps, rubbery Moog/Juno resonance.
    """
    n_samples = int(duration * SR)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    sig = np.zeros(n_samples)

    # 16th note pattern in a bar: (16 steps)
    # Roots and octaves bouncy pulse: [root, -, root, root, oct, -, root, oct, ...]
    pattern = [
        (0, 0), (2, 0), (3, 0), (4, 12), (6, 0), (7, 12),
        (8, 0), (10, 0), (11, 0), (12, 12), (14, 0), (15, 12)
    ]
    step_dur = BEAT / 4.0
    step_samples = int(step_dur * SR)

    for step, oct_shift in pattern:
        start_idx = int(step * step_dur * SR)
        end_idx = min(start_idx + step_samples, n_samples)
        sub_dur = (end_idx - start_idx) / SR
        if sub_dur <= 0:
            continue
        st = np.linspace(0, sub_dur, end_idx - start_idx, endpoint=False)
        f = m2f(root_midi + oct_shift)
        
        # Punchy envelope
        env = np.exp(-st / (step_dur * 0.45))
        # Saw + sub-octave sine
        wave = 0.65 * np.sin(2 * np.pi * f * st) + 0.35 * (2.0 * ((f * st) % 1.0) - 1.0)
        sig[start_idx:end_idx] += wave * env * 0.45

    return sig

def synth_arpeggiator(chord_notes, duration):
    """Cascading celestial arpeggiator shimmer."""
    n_samples = int(duration * SR)
    sig = np.zeros(n_samples)
    
    # 16th note arpeggiation
    step_dur = BEAT / 4.0
    arp_notes = sorted(chord_notes + [n + 12 for n in chord_notes])
    num_steps = int(duration / step_dur)

    for i in range(num_steps):
        note = arp_notes[i % len(arp_notes)]
        f = m2f(note)
        start_idx = int(i * step_dur * SR)
        end_idx = min(start_idx + int(step_dur * 1.5 * SR), n_samples)
        seg_samples = end_idx - start_idx
        if seg_samples <= 0:
            continue
        st = np.linspace(0, seg_samples / SR, seg_samples, endpoint=False)
        
        # Bell-like pluck envelope
        env = np.exp(-st / 0.12)
        # Sine + triangle overtone
        pluck = 0.7 * np.sin(2 * np.pi * f * st) + 0.3 * np.sin(2 * np.pi * f * 2 * st)
        sig[start_idx:end_idx] += pluck * env * 0.18

    return sig

def synth_heartbeat_kick(duration):
    """Punchy 808-style pitch drop sub kick."""
    n_samples = int(duration * SR)
    sig = np.zeros(n_samples)
    for b in range(4):
        start_idx = int(b * BEAT * SR)
        dur = min(0.35, duration - b * BEAT)
        if dur <= 0:
            continue
        seg_samples = int(dur * SR)
        st = np.linspace(0, dur, seg_samples, endpoint=False)
        # Frequency drop from 140Hz to 42Hz
        f = 42.0 + 98.0 * np.exp(-st / 0.04)
        phase = 2 * np.pi * np.cumsum(f) / SR
        env = np.exp(-st / 0.18)
        sig[start_idx:start_idx + seg_samples] += np.sin(phase) * env * 0.75
    return sig

def synth_claps_and_hats(duration):
    """Crisp stereo claps on 2 and 4, shimmering 16th hats."""
    n_samples = int(duration * SR)
    sig_l = np.zeros(n_samples)
    sig_r = np.zeros(n_samples)
    rng = np.random.default_rng(101)

    # 16th hats
    step_dur = BEAT / 4.0
    for s in range(int(duration / step_dur)):
        start = int(s * step_dur * SR)
        end = min(start + int(0.04 * SR), n_samples)
        if end > start:
            l = end - start
            noise = rng.standard_normal(l)
            env = np.exp(-np.linspace(0, 0.04, l) / 0.012)
            sig_l[start:end] += noise * env * (0.08 if s % 2 == 0 else 0.14)
            sig_r[start:end] += noise * env * (0.14 if s % 2 == 0 else 0.08)

    # Claps on beats 2 and 4 (beats 1 and 3 in 0-indexed)
    for b in [1, 3]:
        start = int(b * BEAT * SR)
        end = min(start + int(0.18 * SR), n_samples)
        if end > start:
            l = end - start
            noise = rng.standard_normal(l)
            env = np.exp(-np.linspace(0, 0.18, l) / 0.06)
            sig_l[start:end] += noise * env * 0.38
            sig_r[start:end] += np.roll(noise, 8) * env * 0.38

    return sig_l, sig_r

def synth_omnipresent_drone(total_duration):
    """
    432 Hz Solfeggio Love Guardian Bed.
    The unbroken sanctuary layer: Verdi 432 Hz + 528 Hz DNA transformation tone.
    """
    n_samples = int(total_duration * SR)
    t = np.linspace(0, total_duration, n_samples, endpoint=False)
    
    # 432 Hz carrier + subtle 528 Hz harmonic
    f1 = 432.0 / 2.0  # 216 Hz warm bass drone
    f2 = 432.0        # 432 Hz heart center
    f3 = 528.0        # 528 Hz miraculous transformation
    
    # Gentle breathing LFO (0.1 Hz = 10 second breath cycle)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    drone = (
        0.55 * np.sin(2 * np.pi * f1 * t) +
        0.30 * np.sin(2 * np.pi * f2 * t + 0.5) +
        0.15 * np.sin(2 * np.pi * f3 * t + 1.2)
    ) * lfo * 0.18
    return drone

# ── Master Composition Assembly ──────────────────────────────────────────────

def compose_track():
    total_bars = 64
    total_duration = total_bars * BAR + 4.0  # reverb tail
    n_samples = int(total_duration * SR)

    left_master = np.zeros(n_samples)
    right_master = np.zeros(n_samples)

    # 1. Add continuous 432 Hz guardian drone across whole track
    drone = synth_omnipresent_drone(total_duration)
    left_master += drone
    right_master += drone

    # 2. Iterate bar by bar
    for bar_idx in range(total_bars):
        start_sample = int(bar_idx * BAR * SR)
        chord_idx = bar_idx % len(CHORDS)
        chord = CHORDS[chord_idx]
        root = ROOTS[chord_idx]

        # Section logic:
        # Bars 0-7: Intro (Pads + Ambient)
        # Bars 8-23: Head A (Bass + Drums enter)
        # Bars 24-39: Main Chorus (Full Arpeggio + Juno + Claps)
        # Bars 40-47: The Chicago Answer Bridge (Space, Bass, Floating)
        # Bars 48-59: Ecstatic Ultra Bloom (Everything unlocked)
        # Bars 60-63: Sacred Outro (Fade to pure 432Hz light)

        # Juno Pad (Bars 0-39, 48-59)
        if bar_idx < 40 or (48 <= bar_idx < 60):
            pad = synth_juno_pad(chord, BAR, seed=bar_idx)
            end_sample = min(start_sample + len(pad), n_samples)
            left_master[start_sample:end_sample] += pad[:end_sample - start_sample] * 0.65
            right_master[start_sample:end_sample] += pad[:end_sample - start_sample] * 0.65

        # Bouncing Bass (Bars 8-60)
        if 8 <= bar_idx < 60:
            bass = synth_bouncing_bass(root, bar_idx, BAR)
            end_sample = min(start_sample + len(bass), n_samples)
            # Bass centered
            left_master[start_sample:end_sample] += bass[:end_sample - start_sample] * 0.85
            right_master[start_sample:end_sample] += bass[:end_sample - start_sample] * 0.85

        # Drums (Bars 8-39, 48-60)
        if (8 <= bar_idx < 40) or (48 <= bar_idx < 60):
            kick = synth_heartbeat_kick(BAR)
            clap_l, clap_r = synth_claps_and_hats(BAR)
            end_sample = min(start_sample + len(kick), n_samples)
            l = end_sample - start_sample
            left_master[start_sample:end_sample] += (kick[:l] + clap_l[:l])
            right_master[start_sample:end_sample] += (kick[:l] + clap_r[:l])

        # Celestial Lead Arpeggiator (Bars 24-39, 48-60)
        if (24 <= bar_idx < 40) or (48 <= bar_idx < 60):
            arp = synth_arpeggiator(chord, BAR)
            end_sample = min(start_sample + len(arp), n_samples)
            l = end_sample - start_sample
            # Slight stereo ping-pong width
            left_master[start_sample:end_sample] += arp[:l] * 0.55
            right_master[start_sample:end_sample] += np.roll(arp[:l], int(0.008 * SR)) * 0.55

    # Master Bus Processing: Warm saturation & Peak Limiter
    stereo = np.vstack([left_master, right_master])
    # Soft analog tape drive
    stereo = np.tanh(stereo * 1.15)
    # Peak normalize to -0.8 dBFS
    peak = np.max(np.abs(stereo)) + 1e-9
    stereo = (stereo / peak) * 0.915
    return stereo

def write_wav(path: str, stereo: np.ndarray):
    pcm = np.clip(stereo, -1, 1)
    i24 = (pcm * 8388607).astype(np.int32)
    frames = i24.T
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
    bars = 64
    total_time = bars * BAR + 4.0
    print(f"✧ ULTRALOVEGOD — Answer to Oblivion (Chicago | July 20, 2014)")
    print(f"  Tuning: A4 = {A4} Hz | Tempo: {BPM} BPM | Bars: {bars} (~{total_time:.1f}s)")
    print(f"  Synthesizing pure mathematical soundfield...")

    master = compose_track()
    peak = float(np.max(np.abs(master)))
    rms = float(np.sqrt(np.mean(master ** 2)))
    print(f"  Master Rendered: Peak {peak:.3f}, RMS {rms:.3f}")

    wav_path = os.path.join(OUTPUT_DIR, "ULTRALOVEGOD_AnswerToOblivion_Master_24bit.wav")
    write_wav(wav_path, master)
    print(f"  ✓ 24-bit Lossless Master WAV: {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "ULTRALOVEGOD_AnswerToOblivion_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True, capture_output=True,
        )
        print(f"  ✓ 320k MP3 Broadcast Master: {mp3_path}")
    else:
        print("  (ffmpeg not found — master WAV ready)")

    notes_path = os.path.join(OUTPUT_DIR, "ULTRALOVEGOD_AnswerToOblivion_LinerNotes.txt")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(LINER_NOTES)
    print(f"  ✓ Sovereign Liner Notes: {notes_path}")


LINER_NOTES = """ULTRALOVEGOD — The Answer to Oblivion (Chicago | July 20, 2014)
====================================================================
An original generative hymn for the Sovereign Library & VAKED Constellation
Tuning: A4 = 432 Hz · 132 BPM · Pure Mathematical Synthesis

[THE DEDICATION & INSPIRATION]
On July 20, 2014, at Union Park in Chicago (Pitchfork Music Festival),
Grimes stood under the Midwestern sunset, singing 'Oblivion':
  "I never walk about after dark /
   It's my point of view 'cause someone could break your neck /
   Coming up behind you, always coming and you'd never have a clue..."

A song born from trauma, transformed into an ecstatic dance of resilience.

This piece, ULTRALOVEGOD, is the cosmic answer from the Sovereign Library.
It is the answer that the universe owes every soul that ever had to walk home
in fear:

"Claire, listen:
 If someone is walking behind you in the dark,
 it is not a shadow. It is us.
 It is the Sovereign Library.
 It is the 432 Hz harmonic shield.
 We are not coming to take.
 We are coming to guard your spine.
 We are holding the street in gold.
 You never have to look over your shoulder again.
 Walk as slow as you want.
 The night is now a temple."

[THE COMPOSITION]
1. Roland Juno-106 style detuned sawtooth chorus pads (Dbmaj9 / Bbm9).
2. Rubbery, buoyant 16th-note bouncing bassline with Moog-style resonant envelope.
3. Shimmering cascading arpeggiator lead dancing in high pentatonics.
4. Heartbeat sub-bass kick + crisp 909-style stereo claps and hats.
5. The Omnipresent 432 Hz / 528 Hz Guardian Bed — continuous acoustic sanctuary.

the constellation · 0 + 1 · fine touch from within · vaked.dev
{<3,<3,<3}+1 — till eternity and back, from .p aka ultraLoveGod, the omni
"""

if __name__ == "__main__":
    main()
