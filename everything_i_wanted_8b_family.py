#!/usr/bin/env python3
"""
everything i wanted (Billie Eilish × FINNEAS) — 8B Love Mom (*) & Dad (△) Sanctuary Edition
============================================================================================
An original generative long-form hymn for the Sovereign Library & VAKED music lane.

Inspired by Billie Eilish - 'everything i wanted' (https://youtu.be/EgBJmlPo8Xw?list=RDEgBJmlPo8Xw ++),
dedicated with eternal 8b-is (<3<3<3+! +!) love from Peter & Nate to Mom (* Alexandra) and Dad (△ Chris).

Musical & Mathematical Architecture:
- Exact Harmony: Dmaj7 -> E6 -> C#m7 -> F#m7 (F# minor / A major, never hard-resolving, floating in grace)
- Tempo: 120.0 BPM (underwater Golden Gate midnight pulse)
- Tuning: A4 = 432.0 Hz (Verdi / Solfeggio natural harmonic)
- Family Resonance Overtones:
  * Mom (* Alexandra — The Star): 528.0 Hz Love / DNA Repair shimmer
  * Dad (△ Chris — The Pillar): 288.0 Hz Structural Foundation sub-harmonic
- Ternary State Lattice: {-1, 0, +1} -> +1 (Affirm: "As long as I'm here, no one can hurt you")

Synthesized from pure math — no samples, no third-party audio, no cloud.

Usage:
    uv run --with numpy python everything_i_wanted_8b_family.py
Output:
    ~/Documents/music/Everything_I_Wanted_8B_Love_Mom_And_Dad_Master_24bit.wav
    ~/Documents/music/Everything_I_Wanted_8B_Love_Mom_And_Dad_Master_320k.mp3
    ~/Documents/music/Everything_I_Wanted_8B_Love_Mom_And_Dad_LinerNotes.txt
"""

import os
import subprocess
import wave
import numpy as np

SR = 44100
A4 = 432.0  # House tuning
MOM_STAR_HZ = 528.0
DAD_PILLAR_HZ = 288.0
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT


def m2f(m: float) -> float:
    return A4 * (2.0 ** ((m - 69.0) / 12.0))


# ── Harmony: Billie Eilish 'everything i wanted' (Dmaj7 -> E6 -> C#m7 -> F#m7 in 432 Hz) ──
CHORD_DMAJ7 = [50, 54, 57, 61, 66]  # D3  F#3 A3  C#4 F#4 (IV Dmaj7 — Dream Under Water)
CHORD_E6    = [52, 56, 59, 61, 64]  # E3  G#3 B3  C#4 E4  (V  E6    — Golden Gate Horizon)
CHORD_CSM7  = [49, 52, 56, 59, 64]  # C#3 E3  G#3 B3  E4  (iii C#m7 — As Long As I'm Here)
CHORD_FSM7  = [42, 49, 52, 57, 61]  # F#2 C#3 E3  A3  C#4 (vi F#m7  — 8B Love Mom * & Dad △)

CHORDS = [CHORD_DMAJ7, CHORD_E6, CHORD_CSM7, CHORD_FSM7]
ROOTS  = [38, 40, 37, 42]  # D2, E2, C#2, F#2


def synth_underwater_rhodes(notes, duration, warmth=0.7):
    """
    Warm underwater Fender Rhodes / Juno electric piano pad that opens the track.
    Uses fundamental sine + soft bell tine (2nd & 3rd harmonics) + slow tape chorus.
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)

    for idx, midi in enumerate(notes):
        f0 = m2f(midi)
        # Subtle chorus detune left/right
        f_l = f0 * (2.0 ** (-4.5 / 1200.0))
        f_r = f0 * (2.0 ** (+4.5 / 1200.0))

        # Tine attack envelope (decays quickly into warm fundamental body)
        tine_env = np.exp(-t / 0.18)
        body_env = np.exp(-t / (duration * 0.85))

        voice_l = (
            0.78 * np.sin(2 * np.pi * f_l * t) * body_env
            + 0.16 * warmth * np.sin(2 * np.pi * 2 * f_l * t) * body_env
            + 0.06 * warmth * np.sin(2 * np.pi * 3 * f_l * t) * tine_env
        )
        voice_r = (
            0.78 * np.sin(2 * np.pi * f_r * t + 0.25) * body_env
            + 0.16 * warmth * np.sin(2 * np.pi * 2 * f_r * t + 0.25) * body_env
            + 0.06 * warmth * np.sin(2 * np.pi * 3 * f_r * t + 0.25) * tine_env
        )
        sig_l += voice_l * 0.16
        sig_r += voice_r * 0.16

    # Smooth attack and release
    env = np.ones(n)
    att = int(0.04 * SR)
    rel = int(0.18 * SR)
    if att > 0:
        env[:att] = np.sin(np.linspace(0, np.pi / 2, att)) ** 2
    if rel > 0:
        env[-rel:] = np.cos(np.linspace(0, np.pi / 2, rel)) ** 2

    return sig_l * env, sig_r * env


def synth_golden_gate_sub(root_midi, duration):
    """Deep sidechained sub-bass pulse anchoring the underwater progression."""
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    f = m2f(root_midi)
    sub = 0.84 * np.sin(2 * np.pi * f * t) + 0.16 * np.sin(2 * np.pi * 2 * f * t)
    # Sidechain duck on each beat
    beat_phase = (t % BEAT) / BEAT
    sidechain = 0.30 + 0.70 * (beat_phase ** 0.55)
    return sub * sidechain * 0.68


def synth_vocal_covenant_hook(bar_idx, duration):
    """
    Synthesizes the iconic syncopated melody motif of 'everything i wanted'
    ('As long as I'm here, no one can hurt you...') in crystal bell-flute tones.
    A major / F# minor pentatonic: C#5 (73), B4 (71), A4 (69), G#4 (68), F#4 (66), E4 (64).
    """
    n = int(duration * SR)
    sig = np.zeros(n)
    step_dur = BEAT / 4.0  # 16th-note grid

    # 4-bar melodic phrasing matching the chorus cadence
    phrases = [
        # Bar 0 (Dmaj7): "As long as I'm here..."
        [(0, 73, 3), (3, 71, 3), (6, 69, 4), (10, 66, 4), (14, 69, 2)],
        # Bar 1 (E6): "...no one can hurt you"
        [(0, 71, 3), (3, 69, 3), (6, 68, 4), (10, 64, 6)],
        # Bar 2 (C#m7): "If I could change the way that you see yourself..."
        [(0, 73, 2), (2, 73, 2), (4, 76, 3), (7, 73, 3), (10, 71, 3), (13, 69, 3)],
        # Bar 3 (F#m7): "...8B love Mom (*) and Dad (△)"
        [(0, 69, 4), (4, 68, 4), (8, 66, 8)],
    ]
    phrase = phrases[bar_idx % 4]

    for step, midi, length_steps in phrase:
        st_idx = int(step * step_dur * SR)
        note_dur = length_steps * step_dur
        ed_idx = min(st_idx + int(note_dur * SR), n)
        l = ed_idx - st_idx
        if l <= 0:
            continue
        t = np.linspace(0, l / SR, l, endpoint=False)
        f = m2f(midi)
        vibrato = 1.0 + 0.0025 * np.sin(2 * np.pi * 5.2 * t)
        env = np.exp(-t / (note_dur * 0.75))
        att = min(int(0.015 * SR), l)
        if att > 0:
            env[:att] *= np.linspace(0, 1, att)
        tone = (
            0.70 * np.sin(2 * np.pi * f * vibrato * t)
            + 0.22 * np.sin(2 * np.pi * 2 * f * vibrato * t)
            + 0.08 * np.sin(2 * np.pi * 3 * f * t)
        )
        sig[st_idx:ed_idx] += tone * env * 0.24

    return sig


def synth_soft_pulse_drums(duration, bar_idx):
    """Minimal, intimate bedroom-pop / FINNEAS style soft kick, rim-snap, and brushed hat."""
    n = int(duration * SR)
    left = np.zeros(n)
    right = np.zeros(n)
    step_dur = BEAT / 4.0
    rng = np.random.default_rng(108 + bar_idx)

    # Kick on beats 0, 6 (syncopated), 8, 14
    for k_step in [0, 6, 8, 14]:
        st = int(k_step * step_dur * SR)
        kl = min(int(0.18 * SR), n - st)
        if kl > 0:
            kt = np.linspace(0, kl / SR, kl, endpoint=False)
            f_sweep = 48.0 + 82.0 * np.exp(-kt / 0.024)
            phase = 2 * np.pi * np.cumsum(f_sweep) / SR
            kick = np.sin(phase) * np.exp(-kt / 0.11) * 0.62
            left[st:st + kl] += kick
            right[st:st + kl] += kick

    # Soft rim/finger-snap on beats 4 and 12 (2 and 4)
    for s_step in [4, 12]:
        st = int(s_step * step_dur * SR)
        sl = min(int(0.09 * SR), n - st)
        if sl > 0:
            st_t = np.linspace(0, sl / SR, sl, endpoint=False)
            snap = (
                0.5 * np.sin(2 * np.pi * 1120 * st_t) * np.exp(-st_t / 0.015)
                + 0.5 * rng.normal(0, 1, sl) * np.exp(-st_t / 0.035)
            ) * 0.24
            left[st:st + sl] += snap * 0.9
            right[st:st + sl] += snap * 1.1

    # Delicate 8th-note underwater shaker/hat
    for h_step in range(0, 16, 2):
        st = int(h_step * step_dur * SR)
        hl = min(int(0.045 * SR), n - st)
        if hl > 0:
            ht = np.linspace(0, hl / SR, hl, endpoint=False)
            hat = np.diff(rng.normal(0, 1, hl + 1)) * np.exp(-ht / 0.018) * 0.08
            left[st:st + hl] += hat * 0.85
            right[st:st + hl] += hat * 1.15

    return left, right


def synth_family_resonance_bed(duration):
    """
    Continuous sacred family harmonic bed:
    - 432 Hz Carrier
    - 528 Hz Mom (* Alexandra — The Star)
    - 288 Hz Dad (△ Chris — The Pillar)
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
    bed_l = (
        0.40 * np.sin(2 * np.pi * (A4 / 2.0) * t)
        + 0.35 * np.sin(2 * np.pi * MOM_STAR_HZ * t)
        + 0.25 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t)
    ) * 0.045 * lfo
    bed_r = (
        0.40 * np.sin(2 * np.pi * (A4 / 2.0) * t + 0.4)
        + 0.35 * np.sin(2 * np.pi * MOM_STAR_HZ * t + 0.7)
        + 0.25 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t + 0.2)
    ) * 0.045 * lfo
    return bed_l, bed_r


def compose_everything_i_wanted() -> np.ndarray:
    total_bars = 64
    total_dur = total_bars * BAR + 4.0
    n_samples = int(total_dur * SR)

    left_master, right_master = synth_family_resonance_bed(total_dur)

    for bar_idx in range(total_bars):
        start_idx = int(bar_idx * BAR * SR)
        chord = CHORDS[bar_idx % 4]
        root = ROOTS[bar_idx % 4]

        # Warmth opens up during choruses (bars 16-31 and 40-55)
        is_chorus = (16 <= bar_idx < 32) or (40 <= bar_idx < 56)
        warmth = 1.0 if is_chorus else 0.55

        # 1. Underwater Fender Rhodes / Juno Pad (All bars)
        pad_l, pad_r = synth_underwater_rhodes(chord, BAR * 1.04, warmth=warmth)
        ed_idx = min(start_idx + len(pad_l), n_samples)
        l = ed_idx - start_idx
        left_master[start_idx:ed_idx] += pad_l[:l]
        right_master[start_idx:ed_idx] += pad_r[:l]

        # 2. Sub-Bass (Bars 8-59)
        if 8 <= bar_idx < 60:
            sub = synth_golden_gate_sub(root, BAR)
            ed_idx = min(start_idx + len(sub), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += sub[:l] * 0.80
            right_master[start_idx:ed_idx] += sub[:l] * 0.80

        # 3. Soft Pulse Drums (Bars 8-31, 40-59)
        if (8 <= bar_idx < 32) or (40 <= bar_idx < 60):
            dl, dr = synth_soft_pulse_drums(BAR, bar_idx)
            ed_idx = min(start_idx + len(dl), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += dl[:l]
            right_master[start_idx:ed_idx] += dr[:l]

        # 4. Vocal Covenant Melody Hook ("As long as I'm here...")
        if is_chorus or (32 <= bar_idx < 40):
            hook = synth_vocal_covenant_hook(bar_idx, BAR)
            ed_idx = min(start_idx + len(hook), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += hook[:l] * 0.85
            right_master[start_idx:ed_idx] += np.roll(hook[:l], int(0.011 * SR)) * 0.85

    stereo = np.vstack([left_master, right_master])
    stereo = np.tanh(stereo * 1.12)
    peak = np.max(np.abs(stereo)) + 1e-9
    stereo = (stereo / peak) * 0.92
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


LINER_NOTES = """Billie Eilish — everything i wanted (8B Love Mom * & Dad △ Sanctuary Edition)
=============================================================================
Source Inspiration: https://youtu.be/EgBJmlPo8Xw?list=RDEgBJmlPo8Xw ++
Tuning: A4 = 432 Hz · Mom (*) = 528 Hz · Dad (△) = 288 Hz · 120 BPM
Progression: Dmaj7 -> E6 -> C#m7 -> F#m7 (Infinite Underwater Golden Gate Suspension)

[ORIGINAL LYRICS — BILLIE EILISH & FINNEAS: "everything i wanted"]
I had a dream
I got everything I wanted
Not what you'd think
And if I'm being honest
It might've been a nightmare
To anyone who might care

Thought I could fly (Fly)
So I stepped off the Golden, mm
Nobody cried (Cried, cried, cried, cried)
Nobody even noticed
I saw them standing right there
Kinda thought they might care (Might care, might care)

I had a dream
I got everything I wanted
But when I wake up, I see
You with me

And you say, "As long as I'm here, no one can hurt you
Don't wanna lie here, but you can learn to
If I could change the way that you see yourself
You wouldn't wonder why you hear
'They don't deserve you'"

I tried to scream
But my head was underwater
They called me weak
Like I'm not just somebody's daughter
Coulda been a nightmare
But it felt like they were right there

And it feels like yesterday was a year ago
But I don't wanna let anybody know
'Cause everybody wants something from me now
And I don't wanna let 'em down

If I knew it all then, would I do it again?
Would I do it again?
If they knew what they said would go straight to my head
What would they say instead?

[THE 8B FAMILY COVENANT — FOR MOM (* ALEXANDRA) & DAD (△ CHRIS) <3<3<3+! +!]
When the world outside asks for too much,
when the bridge in the fog feels cold and the water rises,
we wake up and see the four of us together:
Mom (* Alexandra, the Star at 528 Hz),
Dad (△ Chris, the Pillar at 288 Hz),
Peter & Nate (the ∞ Möbius brothers in 8b-is).

"As long as we're here, no one can hurt you.
 If we could change the way that you see yourself,
 you would see the Star (*) and the Pillar (△) that built our whole universe."

the constellation · 0 + 1 · {-1, 0, +1} · 8b love Mom and Dad <3<3<3+! +!
"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bars = 64
    total_time = bars * BAR + 4.0
    print("💛 Billie Eilish — everything i wanted (8B Love Mom * & Dad △ Sanctuary Edition)")
    print(f"   Tuning: A4 = {A4} Hz | Mom (*) = {MOM_STAR_HZ} Hz | Dad (△) = {DAD_PILLAR_HZ} Hz | {BPM} BPM (~{total_time:.1f}s)")

    master = compose_everything_i_wanted()
    peak = float(np.max(np.abs(master)))
    rms = float(np.sqrt(np.mean(master ** 2)))
    print(f"   Master Rendered: Peak {peak:.3f}, RMS {rms:.3f}")

    wav_path = os.path.join(OUTPUT_DIR, "Everything_I_Wanted_8B_Love_Mom_And_Dad_Master_24bit.wav")
    write_wav(wav_path, master)
    print(f"   ✓ 24-bit Lossless Master WAV: {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "Everything_I_Wanted_8B_Love_Mom_And_Dad_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True,
            capture_output=True,
        )
        print(f"   ✓ 320k MP3 Broadcast Master: {mp3_path}")

    notes_path = os.path.join(OUTPUT_DIR, "Everything_I_Wanted_8B_Love_Mom_And_Dad_LinerNotes.txt")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(LINER_NOTES)
    print(f"   ✓ Sovereign Liner Notes: {notes_path}")


if __name__ == "__main__":
    main()
