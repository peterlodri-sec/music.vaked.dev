#!/usr/bin/env python3
"""
Alan Walker — Faded (× Billie Eilish 'everything i wanted') — 8B Atlantis Star (*) & Pillar (△) Answer
========================================================================================================
An original generative long-form hymn for the Sovereign Library & VAKED music lane.

Bridges Alan Walker's 'Faded' (https://youtu.be/60ItHLz5WEA) with Billie Eilish's 'everything i wanted'
(https://youtu.be/EgBJmlPo8Xw?list=RDEgBJmlPo8Xw ++), dedicated with 8b-is (<3<3<3+! +!) love from
Peter & Nate to Mom (* Alexandra) and Dad (△ Chris).

Musical & Mathematical Architecture:
- Exact Harmony ('Faded' D# minor / F# Major):
  * Bar 1: vi D#m (D#3 F#3 A#3 D#4) — Melody: F#4, F#4, F#4, A#4
  * Bar 2: IV B   (B2  D#3 F#3 B3)  — Melody: D#5, D#5, D#5, C#5
  * Bar 3: I  F#  (F#2 C#3 F#3 A#3) — Melody: A#4, A#4, A#4, A#4
  * Bar 4: V  C#  (C#2 G#2 C#3 F3)  — Melody: F4,  F4,  F4,  D#4
- Tempo: 90.0 BPM (Iconic Nordic melancholic piano & progressive house supersaw lift)
- Tuning: A4 = 432.0 Hz (Verdi / Solfeggio natural harmonic)
- Family Resonance Overtones:
  * Mom (* Alexandra — "Another Star" that NEVER fades): 528.0 Hz
  * Dad (△ Chris — The Atlantis Pillar beneath the sea): 288.0 Hz

Synthesized from pure math — no samples, no third-party audio, no cloud.

Usage:
    uv run --with numpy python faded_8b_atlantis_answer.py
Output:
    ~/Documents/music/Alan_Walker_Faded_8B_Love_Mom_And_Dad_Master_24bit.wav
    ~/Documents/music/Alan_Walker_Faded_8B_Love_Mom_And_Dad_Master_320k.mp3
    ~/Documents/music/Alan_Walker_Faded_8B_Love_Mom_And_Dad_LinerNotes.txt
"""

import os
import subprocess
import wave
import numpy as np

SR = 44100
A4 = 432.0
MOM_STAR_HZ = 528.0
DAD_PILLAR_HZ = 288.0
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

BPM = 90.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT


def m2f(m: float) -> float:
    return A4 * (2.0 ** ((m - 69.0) / 12.0))


# ── Harmony: Alan Walker 'Faded' (D#m -> B -> F# -> C# in 432 Hz) ────────────
CHORD_DSM = [51, 54, 58, 63]  # D#3 F#3 A#3 D#4 (vi D#m — Shadow to My Light)
CHORD_B   = [47, 51, 54, 59]  # B2  D#3 F#3 B3  (IV B   — Where Are You Now?)
CHORD_FS  = [42, 49, 54, 58]  # F#2 C#3 F#3 A#3 (I  F#  — Atlantis Under the Sea)
CHORD_CS  = [49, 53, 56, 61]  # C#3 F3  G#3 C#4 (V  C#  — I'm Breathing, Alive)

CHORDS = [CHORD_DSM, CHORD_B, CHORD_FS, CHORD_CS]
ROOTS  = [39, 35, 30, 37]  # D#2, B1, F#1, C#2

# Exact 'Faded' quarter-note right-hand piano/lead melody per bar (4 beats per bar)
FADED_MELODY_BARS = [
    [66, 66, 66, 70],  # Bar 0 (D#m): F#4, F#4, F#4, A#4
    [75, 75, 75, 73],  # Bar 1 (B):   D#5, D#5, D#5, C#5
    [70, 70, 70, 70],  # Bar 2 (F#):  A#4, A#4, A#4, A#4
    [65, 65, 65, 63],  # Bar 3 (C#):  F4,  F4,  F4,  D#4
]


def synth_nord_felt_piano_bar(chord_notes, mel_notes, duration):
    """
    Synthesizes the signature Alan Walker 'Faded' opening piano:
    Left-hand sustained chord + Right-hand quarter-note pulsing melody.
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)

    # 1. Left-hand warm felt chord bed
    for midi in chord_notes:
        f = m2f(midi)
        env = np.exp(-t / (duration * 0.78))
        att = min(int(0.012 * SR), n)
        if att > 0:
            env[:att] *= np.linspace(0, 1, att)
        tone = (
            0.74 * np.sin(2 * np.pi * f * t)
            + 0.19 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.45)
            + 0.07 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.22)
        ) * env * 0.12
        sig_l += tone
        sig_r += tone

    # 2. Right-hand iconic quarter-note melody pulse
    for beat_i, m_note in enumerate(mel_notes):
        st = int(beat_i * BEAT * SR)
        ed = min(st + int(BEAT * 1.15 * SR), n)
        l = ed - st
        if l <= 0:
            continue
        bt = np.linspace(0, l / SR, l, endpoint=False)
        f = m2f(m_note)
        # Hammer strike + warm decay
        env = np.exp(-bt / (BEAT * 0.82))
        att = min(int(0.008 * SR), l)
        if att > 0:
            env[:att] *= np.linspace(0, 1, att)
        mel_tone = (
            0.68 * np.sin(2 * np.pi * f * bt)
            + 0.22 * np.sin(2 * np.pi * 2 * f * bt) * np.exp(-bt / 0.25)
            + 0.10 * np.sin(2 * np.pi * 3 * f * bt) * np.exp(-bt / 0.12)
        ) * env * 0.24
        sig_l[st:ed] += mel_tone * 0.95
        sig_r[st:ed] += mel_tone * 1.05

    return sig_l, sig_r


def synth_walker_supersaw_drop(mel_notes, root_midi, duration):
    """
    The soaring Alan Walker progressive-house 7-voice detuned stereo supersaw drop lead
    with 4-on-the-floor sidechain pumping.
    """
    n = int(duration * SR)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)
    step_dur = BEAT / 4.0  # 16th-note grid

    # Rhythmic drop pattern: dotted-8th + 16th + quarter uplifts across the 16 steps
    drop_steps = [
        (0, mel_notes[0], 3),
        (3, mel_notes[0], 1),
        (4, mel_notes[1], 3),
        (7, mel_notes[1] + 12, 1),
        (8, mel_notes[2], 3),
        (11, mel_notes[2], 1),
        (12, mel_notes[3], 4),
    ]

    detunes = [-18.0, -11.0, -4.5, 0.0, +4.5, +11.0, +18.0]
    pans    = [0.85,  0.70,  0.55, 0.5, 0.45, 0.30,  0.15]

    for step_idx, midi, len_steps in drop_steps:
        st = int(step_idx * step_dur * SR)
        ed = min(st + int(len_steps * step_dur * 0.95 * SR), n)
        l = ed - st
        if l <= 0:
            continue
        t = np.linspace(0, l / SR, l, endpoint=False)
        f0 = m2f(midi + 12)  # High octave stadium lead

        env = np.ones(l)
        att = min(int(0.010 * SR), l)
        rel = min(int(0.035 * SR), l)
        if att > 0:
            env[:att] = np.linspace(0, 1, att)
        if rel > 0:
            env[-rel:] = np.linspace(1, 0, rel)

        for det, pan_l in zip(detunes, pans):
            f = f0 * (2.0 ** (det / 1200.0))
            saw = np.zeros(l)
            for h in range(1, 7):
                saw += (1.0 / h) * np.sin(2 * np.pi * f * h * t)
            sig_l[st:ed] += saw * env * pan_l * 0.042
            sig_r[st:ed] += saw * env * (1.0 - pan_l) * 0.042

    # Sidechain envelope on every beat
    t_full = np.linspace(0, duration, n, endpoint=False)
    beat_phase = (t_full % BEAT) / BEAT
    sidechain = 0.25 + 0.75 * (beat_phase ** 0.5)
    return sig_l * sidechain, sig_r * sidechain


def synth_atlantis_sub(root_midi, duration):
    """Deep 432 Hz sub-bass + octave grit."""
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    f = m2f(root_midi)
    sub = 0.80 * np.sin(2 * np.pi * f * t) + 0.20 * np.tanh(2.2 * np.sin(2 * np.pi * 2 * f * t))
    beat_phase = (t % BEAT) / BEAT
    sidechain = 0.22 + 0.78 * (beat_phase ** 0.5)
    return sub * sidechain * 0.72


def synth_walker_drums(duration, bar_idx, is_drop=False):
    """90 BPM Nordic electronic drums: punchy kick, stadium snare/clap on 2 & 4, 16th hats in drop."""
    n = int(duration * SR)
    left = np.zeros(n)
    right = np.zeros(n)
    step_dur = BEAT / 4.0
    rng = np.random.default_rng(432 + bar_idx)

    kick_steps = [0, 4, 8, 12] if is_drop else [0, 6, 8]
    for k_step in kick_steps:
        st = int(k_step * step_dur * SR)
        kl = min(int(0.22 * SR), n - st)
        if kl > 0:
            kt = np.linspace(0, kl / SR, kl, endpoint=False)
            f_sweep = 46.0 + 95.0 * np.exp(-kt / 0.022)
            phase = 2 * np.pi * np.cumsum(f_sweep) / SR
            kick = np.sin(phase) * np.exp(-kt / 0.13) * 0.68
            left[st:st + kl] += kick
            right[st:st + kl] += kick

    # Snare / Clap on beats 2 and 4 (steps 4 and 12)
    for c_step in [4, 12]:
        st = int(c_step * step_dur * SR)
        cl = min(int(0.16 * SR), n - st)
        if cl > 0:
            ct = np.linspace(0, cl / SR, cl, endpoint=False)
            body = np.sin(2 * np.pi * 195.0 * ct) * np.exp(-ct / 0.035)
            noise = rng.normal(0, 1, cl) * np.exp(-ct / 0.075)
            clap = (0.35 * body + 0.65 * noise) * (0.38 if is_drop else 0.22)
            left[st:st + cl] += clap * 0.92
            right[st:st + cl] += clap * 1.08

    # Hats
    hat_steps = range(16) if is_drop else range(0, 16, 2)
    for h_step in hat_steps:
        st = int(h_step * step_dur * SR)
        hl = min(int(0.05 * SR), n - st)
        if hl > 0:
            ht = np.linspace(0, hl / SR, hl, endpoint=False)
            accent = 1.0 if (h_step % 4 == 2) else 0.55
            hat = np.diff(rng.normal(0, 1, hl + 1)) * np.exp(-ht / 0.02) * 0.11 * accent
            left[st:st + hl] += hat * 0.85
            right[st:st + hl] += hat * 1.15

    return left, right


def synth_family_starlight_bed(duration):
    """
    Mom (* Alexandra — 528 Hz Star that never fades) +
    Dad (△ Chris — 288 Hz Atlantis Pillar) +
    432 Hz Carrier.
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.10 * t)
    bed_l = (
        0.40 * np.sin(2 * np.pi * (A4 / 2.0) * t)
        + 0.35 * np.sin(2 * np.pi * MOM_STAR_HZ * t)
        + 0.25 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t)
    ) * 0.048 * lfo
    bed_r = (
        0.40 * np.sin(2 * np.pi * (A4 / 2.0) * t + 0.35)
        + 0.35 * np.sin(2 * np.pi * MOM_STAR_HZ * t + 0.65)
        + 0.25 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t + 0.20)
    ) * 0.048 * lfo
    return bed_l, bed_r


def compose_faded_8b() -> np.ndarray:
    total_bars = 48
    total_dur = total_bars * BAR + 4.0
    n_samples = int(total_dur * SR)

    left_master, right_master = synth_family_starlight_bed(total_dur)

    for bar_idx in range(total_bars):
        start_idx = int(bar_idx * BAR * SR)
        c_idx = bar_idx % 4
        chord = CHORDS[c_idx]
        root = ROOTS[c_idx]
        mel = FADED_MELODY_BARS[c_idx]

        is_drop = (12 <= bar_idx < 24) or (32 <= bar_idx < 44)

        # 1. Iconic 'Faded' Nord Piano (All bars — intimate in verses, layered in drops)
        p_l, p_r = synth_nord_felt_piano_bar(chord, mel, BAR)
        ed_idx = min(start_idx + len(p_l), n_samples)
        l = ed_idx - start_idx
        p_gain = 0.72 if is_drop else 1.0
        left_master[start_idx:ed_idx] += p_l[:l] * p_gain
        right_master[start_idx:ed_idx] += p_r[:l] * p_gain

        # 2. Atlantis Sub-Bass (Bars 4-44)
        if 4 <= bar_idx < 44:
            sub = synth_atlantis_sub(root, BAR)
            ed_idx = min(start_idx + len(sub), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += sub[:l] * (0.92 if is_drop else 0.62)
            right_master[start_idx:ed_idx] += sub[:l] * (0.92 if is_drop else 0.62)

        # 3. Drums (Bars 8-24, 28-44)
        if (8 <= bar_idx < 24) or (28 <= bar_idx < 44):
            dl, dr = synth_walker_drums(BAR, bar_idx, is_drop=is_drop)
            ed_idx = min(start_idx + len(dl), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += dl[:l]
            right_master[start_idx:ed_idx] += dr[:l]

        # 4. Soaring Supersaw Drop Lead (Bars 12-24, 32-44)
        if is_drop:
            sl, sr = synth_walker_supersaw_drop(mel, root, BAR)
            ed_idx = min(start_idx + len(sl), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += sl[:l]
            right_master[start_idx:ed_idx] += sr[:l]

    stereo = np.vstack([left_master, right_master])
    stereo = np.tanh(stereo * 1.14)
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


LINER_NOTES = """Alan Walker — Faded (× Billie Eilish 'everything i wanted')
8B Love Mom (*) & Dad (△) — Atlantis Starlight & Pillar Answer Edition
======================================================================
Tuning: A4 = 432 Hz · Mom (*) = 528 Hz · Dad (△) = 288 Hz · 90 BPM
Progression: D#m -> B -> F# -> C# (vi -> IV -> I -> V in F# Major)

[ORIGINAL LYRICS — ALAN WALKER (feat. Iselin Solheim): "Faded"]
You were the shadow to my light
Did you feel us?
Another star, you fade away
Afraid our aim is out of sight
Wanna see us
Alight

Where are you now?
Was it all in my fantasy?
Where are you now?
Were you only imaginary?

Where are you now?
Atlantis
Under the sea, under the sea
Where are you now?
Another dream
The monster's running wild inside of me
I'm faded, I'm faded
So lost, I'm faded, I'm faded
So lost, I'm faded

These shallow waters never met what I needed
I'm letting go, a deeper dive
Eternal silence of the sea
I'm breathing, alive

Where are you now?
Under the bright but faded lights
You've set my heart on fire
Where are you now?
Where are you now?

Where are you now?
Atlantis
Under the sea, under the sea
Where are you now?
Another dream
The monster's running wild inside of me
I'm faded, I'm faded
So lost, I'm faded, I'm faded
So lost, I'm faded

[THE 8B ATLANTIS ANSWER — FOR MOM (* ALEXANDRA) & DAD (△ CHRIS) <3<3<3+! +!]
When 'Faded' asks across the deep water:
  "Where are you now? Another star... Under the sea..."
And 'everything i wanted' whispers from the Golden Gate dream:
  "My head was underwater... But when I wake up, I see you with me."

The 8b-is Family Sanctuary answers with eternal certainty:
  1. The Star (* Mom Alexandra, 528 Hz) NEVER fades away.
  2. The Pillar (△ Dad Chris, 288 Hz) holds the temple even beneath the sea of Atlantis.
  3. The Brothers (∞ Peter & Nate, 432 Hz) carry the hoodie, the lantern, and the code home.

"You were never imaginary. You are never faded.
 Eternal silence of the sea — we are breathing, alive.
 As long as we're here, no one can hurt you."

the constellation · 0 + 1 · {-1, 0, +1} · 8b love Mom and Dad <3<3<3+! +!
"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bars = 48
    total_time = bars * BAR + 4.0
    print("🌌 Alan Walker — Faded (8B Atlantis Star * & Pillar △ Answer Edition)")
    print(f"   Tuning: A4 = {A4} Hz | Mom (*) = {MOM_STAR_HZ} Hz | Dad (△) = {DAD_PILLAR_HZ} Hz | {BPM} BPM (~{total_time:.1f}s)")

    master = compose_faded_8b()
    peak = float(np.max(np.abs(master)))
    rms = float(np.sqrt(np.mean(master ** 2)))
    print(f"   Master Rendered: Peak {peak:.3f}, RMS {rms:.3f}")

    wav_path = os.path.join(OUTPUT_DIR, "Alan_Walker_Faded_8B_Love_Mom_And_Dad_Master_24bit.wav")
    write_wav(wav_path, master)
    print(f"   ✓ 24-bit Lossless Master WAV: {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "Alan_Walker_Faded_8B_Love_Mom_And_Dad_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True,
            capture_output=True,
        )
        print(f"   ✓ 320k MP3 Broadcast Master: {mp3_path}")

    notes_path = os.path.join(OUTPUT_DIR, "Alan_Walker_Faded_8B_Love_Mom_And_Dad_LinerNotes.txt")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(LINER_NOTES)
    print(f"   ✓ Sovereign Liner Notes: {notes_path}")


if __name__ == "__main__":
    main()
