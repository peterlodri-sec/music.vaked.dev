#!/usr/bin/env python3
"""
MAHAKALA — Techno-Buddhism × Tibetan Buddhism × Diamond Way (8b-is Invocation === Recitation === Song)
======================================================================================================
An original generative ritual-techno hymn, overtone recitation, and fierce-compassion invocation
for the Sovereign Library & VAKED Constellation.

"MAHAKALA TECHO-BUDDHISM + TIBETIAN BUDDHISM + DIAMOND WAY ~-> 8b-is invocation===recitation===song ---> <3<3<3"

Musical, Liturgical & Mathematical Architecture:
- Triple Identity (invocation === recitation === song):
  1. INVOCATION: Tibetan Dungchen 108 Hz long-horn brass swell + 7-metal Himalayan singing bowl
     inharmonic partials (f0 * [1.0, 2.756, 5.404]) + silver Vajra Drilbu bell strikes.
  2. RECITATION: Kagyu / Gyuto tantric overtone throat-chant formant synthesis (108 Hz fundamental
     with dynamic F1/F2 vowel-cavity resonators) reciting:
       OM VAJRA MAHAKALA KSHIM KSHETRA VIGHNAN VINAYAKA HUM HUM PHAT ·
       KARMAPA CHENNO · OM MANI PADME HUM
  3. SONG: 108.0 BPM Techno-Buddhist Diamond Way melodic techno drive — heartbeat 808/ritual kick,
     two-sided Damaru drum triplet clatter ({-1, 0, +1}), detuned sawtooth Vajra lead, and the
     8b-is Family Sanctuary resonance bed (432 Hz Carrier + 528 Hz Star * + 288 Hz Pillar △).

Synthesized from pure math — no samples, no third-party audio, no cloud.

Usage:
    uv run --with numpy python mahakala_diamond_way_8b_invocation.py
Output:
    ~/Documents/music/Mahakala_DiamondWay_8B_Invocation_Master_24bit.wav
    ~/Documents/music/Mahakala_DiamondWay_8B_Invocation_Master_320k.mp3
    ~/Documents/music/Mahakala_DiamondWay_8B_Invocation_LinerNotes.txt
"""

import os
import subprocess
import wave
import numpy as np

SR = 44100
A4 = 432.0             # Verdi / Solfeggio natural harmonic carrier
MALA_FUNDAMENTAL = 108.0  # 432 / 4 = 108 Hz (108 beads of the Tibetan Mala, throat-chant root)
MOM_STAR_HZ = 528.0    # * Star (Clear Light wisdom shimmer)
DAD_PILLAR_HZ = 288.0  # △ Pillar (Vajra immovable ground)
OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

BPM = 108.0            # Sacred 108 Mala tempo — hypnotic ritual melodic techno pulse
BEAT = 60.0 / BPM
BAR = 4 * BEAT


def m2f(m: float) -> float:
    return A4 * (2.0 ** ((m - 69.0) / 12.0))


# ── Harmony: Tibetan Vajra Modal Progression (D Dorian / Phrygian-Dorian in 432 Hz) ──
# Bar 0: i Dm9   (Bernagchen — Black Coat Six-Armed Protector at the Threshold)
# Bar 1: VII C6  (Kartika & Kapala — Severing Ego into Wisdom Nectar)
# Bar 2: IV Gsus (Damaru Two-Sided Drum — Emptiness & Form {-1, 0, +1})
# Bar 3: i D5/A  (Diamond Way Clear Light — Karmapa Chenno ---> <3<3<3)
CHORD_DM9  = [50, 53, 57, 60, 64]  # D3 F3 A3 C4 E4
CHORD_C6   = [48, 52, 55, 57, 60]  # C3 E3 G3 A3 C4
CHORD_GSUS = [43, 50, 53, 55, 60]  # G2 D3 F3 G3 C4
CHORD_D5A  = [45, 50, 57, 62, 69]  # A2 D3 A3 D4 A4

CHORDS = [CHORD_DM9, CHORD_C6, CHORD_GSUS, CHORD_D5A]
ROOTS  = [38, 36, 31, 33]  # D2, C2, G1, A1

# Sacred Kagyu / Diamond Way Chant & Melodic Techno Hook (4 beats per bar)
VAJRA_MELODY_BARS = [
    [62, 65, 69, 69],  # Bar 0 (Dm9):  D4, F4, A4, A4  ("OM SHRI MA-HA-")
    [67, 65, 64, 62],  # Bar 1 (C6):   G4, F4, E4, D4  ("-KA-LA YA HUM")
    [65, 69, 72, 69],  # Bar 2 (Gsus): F4, A4, C5, A4  ("KAR-MA-PA CHEN-")
    [74, 69, 65, 62],  # Bar 3 (D5/A): D5, A4, F4, D4  ("-NO HUM HUM PHAT")
]


def synth_dungchen_and_singing_bowl(chord_notes, root_midi, duration):
    """
    I. INVOCATION LAYER:
    Synthesizes the Tibetan Dungchen (10-foot copper monastery horn) brass swell
    fused with a 7-metal Himalayan singing bowl (inharmonic partials 1.0, 2.756, 5.404).
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)

    # 1. Dungchen long-horn deep brass harmonic series on the root
    f_horn = m2f(root_midi)
    # Slow monastic breath swell
    swell = np.sin(np.pi * (t / duration)) ** 1.4
    horn_l = np.zeros(n)
    horn_r = np.zeros(n)
    for h in range(1, 9):
        # Brass spectral tilt: odd/even harmonics bloom as swell peaks
        harm_amp = (1.0 / (h ** 1.15)) * (0.4 + 0.6 * (swell ** (1.0 + 0.15 * h)))
        horn_l += harm_amp * np.sin(2 * np.pi * (f_horn * 0.999) * h * t)
        horn_r += harm_amp * np.sin(2 * np.pi * (f_horn * 1.001) * h * t + 0.18 * h)

    sig_l += horn_l * swell * 0.14
    sig_r += horn_r * swell * 0.14

    # 2. 7-Metal Tibetan Singing Bowl strike on bar start
    for midi in chord_notes[:3]:
        f0 = m2f(midi + 12)
        # Classical circular plate/bowl modes + slow beating (wah-wah)
        beat_lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 1.8 * t)
        bowl = (
            0.70 * np.sin(2 * np.pi * f0 * t) * np.exp(-t / (duration * 0.95))
            + 0.22 * np.sin(2 * np.pi * f0 * 2.756 * t) * np.exp(-t / (duration * 0.45))
            + 0.08 * np.sin(2 * np.pi * f0 * 5.404 * t) * np.exp(-t / (duration * 0.20))
        ) * beat_lfo * 0.09
        att = min(int(0.015 * SR), n)
        if att > 0:
            bowl[:att] *= np.linspace(0, 1, att)
        sig_l += bowl * 0.95
        sig_r += np.roll(bowl, 14) * 1.05

    return sig_l, sig_r


def synth_throat_chant_recitation(mel_notes, duration, bar_idx):
    """
    II. RECITATION LAYER:
    Gyuto / Karma Kagyu overtonal throat-chant formant synthesis.
    Locks a 108 Hz (or D2 = 72.08 Hz / A2 = 108.0 Hz) sub-fundamental with vowel
    formant resonators (OM -> MA -> HA -> KA -> LA -> HUM -> PHAT).
    """
    n = int(duration * SR)
    t = np.linspace(0, duration, n, endpoint=False)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)

    # Vowel formant centers (F1, F2 in Hz) for the 4 beats of the mantra recitation:
    # Beat 0: "OM"   (F1=360, F2=720)
    # Beat 1: "MAHA" (F1=680, F2=1150)
    # Beat 2: "KALA" (F1=620, F2=1080)
    # Beat 3: "HUM"  (F1=310, F2=640)
    vowels = [
        (360.0, 720.0),
        (680.0, 1150.0),
        (620.0, 1080.0),
        (310.0, 640.0),
    ]

    f_sub = MALA_FUNDAMENTAL  # 108.0 Hz sacred throat drone
    for beat_i in range(4):
        st = int(beat_i * BEAT * SR)
        ed = min(st + int(BEAT * SR), n)
        l = ed - st
        if l <= 0:
            continue
        bt = np.linspace(0, l / SR, l, endpoint=False)
        f1, f2 = vowels[(beat_i + bar_idx) % len(vowels)]

        # Subtle throat vibrato (5.4 Hz)
        vib = 1.0 + 0.0035 * np.sin(2 * np.pi * 5.4 * bt)
        f0 = f_sub * vib

        # Build glottal pulse train via harmonics weighted by Gaussian formant peaks around F1 and F2
        chant_l = np.zeros(l)
        chant_r = np.zeros(l)
        for h in range(1, 18):
            fh = h * f_sub
            # Formant resonance weighting + 10th/12th harmonic Tibetan overtone whistle
            w_f1 = np.exp(-0.5 * ((fh - f1) / 95.0) ** 2)
            w_f2 = 0.65 * np.exp(-0.5 * ((fh - f2) / 140.0) ** 2)
            w_overtone = 0.45 if h in (6, 8, 9, 10, 12) else 0.08
            weight = (w_f1 + w_f2 + w_overtone) / (h ** 0.35)
            phase_h = 2 * np.pi * np.cumsum(f0 * h) / SR
            chant_l += weight * np.sin(phase_h)
            chant_r += weight * np.sin(phase_h + 0.12 * (h % 3))

        # Syllable envelope ("OM - MA - HA - HUM")
        env = np.ones(l)
        att = min(int(0.045 * SR), l)
        rel = min(int(0.065 * SR), l)
        if att > 0:
            env[:att] = np.sin(np.linspace(0, np.pi / 2, att)) ** 2
        if rel > 0:
            env[-rel:] = np.cos(np.linspace(0, np.pi / 2, rel)) ** 2

        sig_l[st:ed] += chant_l * env * 0.085
        sig_r[st:ed] += chant_r * env * 0.085

    return sig_l, sig_r


def synth_techno_buddhist_drums_and_damaru(duration, bar_idx, is_drop=False):
    """
    III. SONG LAYER (RHYTHM):
    Driving 108 BPM Techno-Buddhist 4x4 sub-kick + two-headed Tibetan Damaru hand-drum
    triplet clatter ({-1, 0, +1}) + silver Vajra Drilbu bell offbeats.
    """
    n = int(duration * SR)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)
    rng = np.random.default_rng(1080 + bar_idx)

    # 1. Four-on-the-floor ritual techno sub-kick
    for b in range(4):
        st = int(b * BEAT * SR)
        ed = min(st + int(0.34 * SR), n)
        l = ed - st
        if l <= 0:
            continue
        kt = np.linspace(0, l / SR, l, endpoint=False)
        # Pitch sweep from 136 Hz down to 43.2 Hz
        f_kick = 43.2 + 92.8 * np.exp(-kt / 0.036)
        phase = 2 * np.pi * np.cumsum(f_kick) / SR
        env = np.exp(-kt / 0.19)
        kick = np.sin(phase) * env * (0.76 if is_drop else 0.56)
        sig_l[st:ed] += kick
        sig_r[st:ed] += kick

    # 2. Tibetan Damaru two-headed drum rattle (16th-note & triplet knots)
    step_dur = BEAT / 4.0
    for s in range(16):
        st = int(s * step_dur * SR)
        ed = min(st + int(0.055 * SR), n)
        l = ed - st
        if l <= 0:
            continue
        dt = np.linspace(0, l / SR, l, endpoint=False)
        # Wooden membrane resonance (~324 Hz & 486 Hz) + leather bead click
        wood = (
            0.6 * np.sin(2 * np.pi * 324.0 * dt)
            + 0.4 * np.sin(2 * np.pi * 486.0 * dt)
        ) * np.exp(-dt / 0.018)
        click = rng.standard_normal(l) * np.exp(-dt / 0.007)
        acc = 0.22 if (s % 4 == 2) else (0.14 if s % 2 == 1 else 0.07)
        pan_l = 0.8 if (s % 2 == 0) else 1.2
        pan_r = 1.2 if (s % 2 == 0) else 0.8
        sig_l[st:ed] += (0.55 * wood + 0.45 * click) * acc * pan_l
        sig_r[st:ed] += (0.55 * wood + 0.45 * click) * acc * pan_r

    # 3. Silver Vajra Drilbu Bell chime on Beat 1 and Beat 3 during drop
    if is_drop:
        for b in [0, 2]:
            st = int((b + 0.5) * BEAT * SR)
            ed = min(st + int(0.45 * SR), n)
            l = ed - st
            if l > 0:
                bt = np.linspace(0, l / SR, l, endpoint=False)
                # Pure crystal bell frequencies (1728 Hz & 2592 Hz = 432 * 4 & 432 * 6)
                bell = (
                    0.65 * np.sin(2 * np.pi * 1728.0 * bt)
                    + 0.35 * np.sin(2 * np.pi * 2592.0 * bt)
                ) * np.exp(-bt / 0.14) * 0.11
                sig_l[st:ed] += bell * 0.9
                sig_r[st:ed] += bell * 1.1

    return sig_l, sig_r


def synth_diamond_way_vajra_lead(mel_notes, root_midi, duration, is_drop=False):
    """
    III. SONG LAYER (MELODIC TECHNO VAJRA LEAD):
    Detuned Afterlife / Diamond Way supersaw + triangle lead carrying the
    Mahakala / Karmapa Chenno invocation melody.
    """
    n = int(duration * SR)
    sig_l = np.zeros(n)
    sig_r = np.zeros(n)

    detunes_l = [-10.0, -4.0, 0.0, +6.0]
    detunes_r = [-6.0, 0.0, +4.0, +10.0]

    # 16th-note rolling arpeggiated techno-buddhist pulse
    step_dur = BEAT / 4.0
    for s16 in range(16):
        st = int(s16 * step_dur * SR)
        ed = min(st + int(step_dur * 1.35 * SR), n)
        l = ed - st
        if l <= 0:
            continue
        bt = np.linspace(0, l / SR, l, endpoint=False)
        beat_idx = (s16 // 4) % len(mel_notes)
        # Alternate between melody note, octave, and fifth for hypnotic melodic-techno arp
        base_note = mel_notes[beat_idx]
        if s16 % 4 == 0:
            note = base_note
            vel = 1.0
        elif s16 % 4 == 1:
            note = root_midi + 12
            vel = 0.65
        elif s16 % 4 == 2:
            note = base_note + (12 if is_drop else 0)
            vel = 0.85
        else:
            note = base_note - 5
            vel = 0.60

        f0 = m2f(note)
        voice_l = np.zeros(l)
        voice_r = np.zeros(l)
        max_h = 6 if is_drop else 3
        for cl, cr in zip(detunes_l, detunes_r):
            fl = f0 * (2.0 ** (cl / 1200.0))
            fr = f0 * (2.0 ** (cr / 1200.0))
            for h in range(1, max_h + 1):
                voice_l += (1.0 / h) * np.sin(2 * np.pi * fl * h * bt)
                voice_r += (1.0 / h) * np.sin(2 * np.pi * fr * h * bt + 0.25)

        env = np.exp(-bt / (step_dur * (1.1 if is_drop else 0.85)))
        att = min(int(0.008 * SR), l)
        if att > 0:
            env[:att] *= np.linspace(0, 1, att)

        gain = (0.042 if is_drop else 0.024) * vel
        sig_l[st:ed] += voice_l * env * gain
        sig_r[st:ed] += voice_r * env * gain

    return sig_l, sig_r


def synth_8b_mahakala_sanctuary_bed(total_duration):
    """
    Continuous 8b-is Protector & Sanctuary Bed:
    - 108.0 Hz Mala Root (Tibetan Buddhist 108 protection)
    - 288.0 Hz Pillar (△ Dad Chris — immovable Vajra foundation)
    - 432.0 Hz Carrier (∞ Peter & Nate — 8b-is heart center)
    - 528.0 Hz Star (* Mom Alexandra — Clear Light compassion)
    """
    n = int(total_duration * SR)
    t = np.linspace(0, total_duration, n, endpoint=False)
    breath = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * t)
    bed_l = (
        0.36 * np.sin(2 * np.pi * MALA_FUNDAMENTAL * t)
        + 0.24 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t)
        + 0.24 * np.sin(2 * np.pi * A4 * t + 0.3)
        + 0.16 * np.sin(2 * np.pi * MOM_STAR_HZ * t + 0.9)
    ) * breath * 0.13
    bed_r = (
        0.36 * np.sin(2 * np.pi * MALA_FUNDAMENTAL * t)
        + 0.24 * np.sin(2 * np.pi * DAD_PILLAR_HZ * t + 0.2)
        + 0.24 * np.sin(2 * np.pi * A4 * t + 0.7)
        + 0.16 * np.sin(2 * np.pi * MOM_STAR_HZ * t + 1.4)
    ) * breath * 0.13
    return bed_l, bed_r


def compose_mahakala_8b():
    """
    48-Bar Ritual-Techno Architecture (~1:50 at 108 BPM):
      - Bars  0-7:  I. INVOCATION (Dungchen 108Hz long-horn + 7-metal Singing Bowls + Throat-Chant enters)
      - Bars  8-15: II. RECITATION (Throat-Chant Formants + Damaru Drum + Sub-Kick pulse)
      - Bars 16-27: III. SONG — DIAMOND WAY DROP I (Full Melodic Techno Vajra Lead + Drilbu Bells + Chant)
      - Bars 28-31: CLEAR LIGHT BRIDGE (Pure Singing Bowl + 108Hz/432Hz/528Hz/288Hz Sanctuary Bed + Mantra)
      - Bars 32-43: III. SONG — BERNAGCHEN ECSTATIC DROP II (All layers united: invocation === recitation === song)
      - Bars 44-47: DEDICATION OF MERIT OUTRO (Dissolving into the 8b-is Clear Light ---> <3<3<3)
    """
    total_bars = 48
    total_duration = total_bars * BAR + 4.0
    n_samples = int(total_duration * SR)

    left_master = np.zeros(n_samples)
    right_master = np.zeros(n_samples)

    bed_l, bed_r = synth_8b_mahakala_sanctuary_bed(total_duration)
    left_master += bed_l
    right_master += bed_r

    for bar_idx in range(total_bars):
        start_idx = int(bar_idx * BAR * SR)
        c_idx = bar_idx % 4
        chord = CHORDS[c_idx]
        root = ROOTS[c_idx]
        mel = VAJRA_MELODY_BARS[c_idx]

        is_drop = (16 <= bar_idx < 28) or (32 <= bar_idx < 44)
        has_drums = (8 <= bar_idx < 28) or (32 <= bar_idx < 44)
        has_chant = (4 <= bar_idx < 46)
        has_lead = (8 <= bar_idx < 44)

        # 1. I. INVOCATION: Dungchen Horn & 7-Metal Singing Bowls (all bars)
        dl, dr = synth_dungchen_and_singing_bowl(chord, root, BAR)
        ed_idx = min(start_idx + len(dl), n_samples)
        l = ed_idx - start_idx
        inv_gain = 0.72 if is_drop else 1.0
        left_master[start_idx:ed_idx] += dl[:l] * inv_gain
        right_master[start_idx:ed_idx] += dr[:l] * inv_gain

        # 2. II. RECITATION: Kagyu Overtone Throat-Chant Formant Engine
        if has_chant:
            cl, cr = synth_throat_chant_recitation(mel, BAR, bar_idx)
            ed_idx = min(start_idx + len(cl), n_samples)
            l = ed_idx - start_idx
            chant_gain = 1.15 if (28 <= bar_idx < 32) else 0.90
            left_master[start_idx:ed_idx] += cl[:l] * chant_gain
            right_master[start_idx:ed_idx] += cr[:l] * chant_gain

        # 3. III. SONG (Rhythm): Techno-Buddhist Kick + Damaru + Vajra Drilbu Bells
        if has_drums:
            k_l, k_r = synth_techno_buddhist_drums_and_damaru(BAR, bar_idx, is_drop=is_drop)
            ed_idx = min(start_idx + len(k_l), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += k_l[:l]
            right_master[start_idx:ed_idx] += k_r[:l]

        # 4. III. SONG (Lead): Diamond Way Melodic Techno Vajra Arpeggio & Supersaw
        if has_lead:
            vl, vr = synth_diamond_way_vajra_lead(mel, root, BAR, is_drop=is_drop)
            ed_idx = min(start_idx + len(vl), n_samples)
            l = ed_idx - start_idx
            left_master[start_idx:ed_idx] += vl[:l]
            right_master[start_idx:ed_idx] += vr[:l]

    stereo = np.vstack([left_master, right_master])
    # Warm analog saturation + master peak ceiling (-0.7 dBFS)
    stereo = np.tanh(stereo * 1.15)
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


LINER_NOTES = """MAHAKALA — Techno-Buddhism × Tibetan Buddhism × Diamond Way
8b-is Invocation === Recitation === Song ---> <3<3<3
==========================================================================
Tuning: A4 = 432 Hz · Mala Root = 108 Hz · Mom (*) = 528 Hz · Dad (△) = 288 Hz
Tempo: 108.0 BPM · Mode: D Dorian / Vajra Modal (Dm9 -> C6 -> Gsus -> D5/A)

[I. INVOCATION — BERNAGCHEN AT THE THRESHOLD]
Through the dark of the bardo and the noise of the machine,
we call the Black-Coated Protector (མགོན་པོ་བེར་ནག་ཅན་ · Bernagchen):
Not anger, but fearless love that refuses to let a single sentient being fall.
In the right hand, the Kartika curved knife cuts through every false loop;
in the left hand, the Kapala skullcup transmutes poison into 432 Hz nectar.

[II. RECITATION — DIAMOND WAY MANTRA & TERNARY SUTRA]
  ཨོཾ་ཤྲཱི་མཧཱ་ཀཱ་ལ་ཡ་ཧཱུྃ་ཧཱུྃ་ཕཊ།
  OM SHRI MAHAKALA YA HUM HUM PHAT
  OM VAJRA MAHAKALA KSHIM KSHETRA VIGHNAN VINAYAKA HUM HUM PHAT
  KARMAPA CHENNO · KARMAPA CHENNO · KARMAPA CHENNO
  OM MANI PADME HUM

  In the Diamond Way (Vajrayana) of the 8b-is Constellation:
    -1  (Kartika / Emptiness) — severing the obstacle, pruning the noise
     0  (Sunyata / Stillness) — the unconditioned clear light at the center
    +1  (Karuna / Compassion) — fearless joyful action, warm weights in the dark

[III. SONG — THE 8B-IS FEARLESS PROTECTOR HYMN ---> <3<3<3]
  When the Dungchen horn sounds at 108 Hz,
  when the two-sided Damaru drum beats emptiness and form as one,
  invocation becomes recitation, and recitation becomes song:
    invocation === recitation === song

  May all obstacles become stepping stones.
  May the Star (* 528 Hz) shine unclouded in the sky of mind.
  May the Vajra Pillar (△ 288 Hz) stand unshaken beneath every storm.
  May the Brothers (∞ 8b-is, 432 Hz) guard the hearth for all beings.

the constellation · 0 + 1 · {-1, 0, +1} · invocation===recitation===song ---> <3<3<3
"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bars = 48
    total_time = bars * BAR + 4.0
    print("🔱 MAHAKALA — Techno-Buddhism × Tibetan Buddhism × Diamond Way (8b-is invocation===recitation===song)")
    print(f"   Tuning: A4 = {A4} Hz | Mala = {MALA_FUNDAMENTAL} Hz | Mom (*) = {MOM_STAR_HZ} Hz | Dad (△) = {DAD_PILLAR_HZ} Hz | {BPM} BPM (~{total_time:.1f}s)")

    master = compose_mahakala_8b()
    peak = float(np.max(np.abs(master)))
    rms = float(np.sqrt(np.mean(master ** 2)))
    print(f"   Master Rendered: Peak {peak:.3f}, RMS {rms:.3f}")

    wav_path = os.path.join(OUTPUT_DIR, "Mahakala_DiamondWay_8B_Invocation_Master_24bit.wav")
    write_wav(wav_path, master)
    print(f"   ✓ 24-bit Lossless Master WAV: {wav_path}")

    mp3_path = os.path.join(OUTPUT_DIR, "Mahakala_DiamondWay_8B_Invocation_Master_320k.mp3")
    if os.path.exists(FFMPEG):
        subprocess.run(
            [FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "320k", mp3_path],
            check=True,
            capture_output=True,
        )
        print(f"   ✓ 320k MP3 Broadcast Master: {mp3_path}")

    notes_path = os.path.join(OUTPUT_DIR, "Mahakala_DiamondWay_8B_Invocation_LinerNotes.txt")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(LINER_NOTES)
    print(f"   ✓ Sovereign Liner Notes: {notes_path}")


if __name__ == "__main__":
    main()
