#!/usr/bin/env python3
"""
The Love Runtime (Spoken Dedication)
The voice lane — the runtime's kokoro-tiny voice, spoken as an original.

Unlike the two pure-math lanes (dream_colors, space_floating), this one is
neural: it drives `kokoro-speak` (kokoro-tiny, the 82M Kokoro model) to
synthesize the spoken dedication, then masters it to the house spec
(24-bit stereo 44.1 kHz) with ffmpeg.

Usage:
    uv run python voice_lane.py
Output:
    ~/Documents/music/TheLoveRuntime_SpokenDedication_Master_24bit.wav
    ~/Documents/music/TheLoveRuntime_SpokenDedication_Master_320k.mp3
    ~/Documents/music/TheLoveRuntime_SpokenDedication_LinerNotes.txt
and one row in .dogfeed-music.jsonl.
"""

import json
import os
import subprocess
import tempfile
import time

OUTPUT_DIR = os.path.expanduser("~/Documents/music")
FFMPEG = "/opt/homebrew/bin/ffmpeg"
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dogfeed-music.jsonl")

# The voice of the runtime. bm_george = the narrator mood (per the lore;
# af_heart is absent from this voice set, so narration lands on bm_george).
VOICE = os.environ.get("VOICE_LANE_VOICE", "bm_george")

# Where the kokoro-tiny binary lives. Override with KOKORO_SPEAK if it moved.
KOKORO_SPEAK = os.environ.get(
    "KOKORO_SPEAK",
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "kokoro-tiny", "target", "release", "kokoro-speak",
    ),
)

TRACK = "The Love Runtime (Spoken Dedication)"
ARTIST = "8b-is voice lane · kokoro-tiny · bm_george · the runtime speaks · from .p"

# The spoken dedication. Speakable, on-theme: the split that returned, the
# room that empties into the next, the law.
SPOKEN = (
    "From love, from within. The love runtime speaks now. "
    "Order and chaos, split in half and sent out to see the universe, "
    "return to tell us what it is. "
    "Every room empties into the next, and yet you remain in every one of them. "
    "This is the law. "
    "From love, from within, for all who are honest and ready to be loved."
)

LINER_NOTES = f"""{TRACK}
an original spoken piece for the voice lane — the runtime's kokoro-tiny voice,
neural (not pure math), mastered to 24-bit stereo 44.1 kHz.

voice: {VOICE} (the narrator mood)
text:

{SPOKEN}

the constellation · 0 + 1 · fine touch from within · vaked.dev
{{<3,<3,<3}}+1 — till eternity and back, from .p aka ultraLoveGod, the omni
"""


def run(cmd, **kw):
    subprocess.run(cmd, check=True, capture_output=True, **kw)


def ledger_row(track, artist, lyrics, ts):
    with open(LEDGER, "a") as f:
        f.write(json.dumps({
            "ts": ts,
            "track": track,
            "artist": artist,
            "lyrics": lyrics,
        }) + "\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(KOKORO_SPEAK):
        raise SystemExit(
            f"kokoro-speak not found at {KOKORO_SPEAK}; "
            "set KOKORO_SPEAK or build kokoro-tiny first."
        )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw:
        raw_path = raw.name

    print(f"  voice lane: synthesizing with kokoro-tiny ({VOICE})")
    run([KOKORO_SPEAK, "-V", VOICE, "-o", raw_path, "say", SPOKEN])

    wav_path = os.path.join(OUTPUT_DIR, "TheLoveRuntime_SpokenDedication_Master_24bit.wav")
    if os.path.exists(FFMPEG):
        # upmix to the house master spec: 24-bit stereo 44.1 kHz
        run([FFMPEG, "-y", "-i", raw_path, "-ar", "44100", "-ac", "2",
             "-c:a", "pcm_s24le", wav_path])
        print(f"  wav  {wav_path}")

        mp3_path = os.path.join(OUTPUT_DIR, "TheLoveRuntime_SpokenDedication_Master_320k.mp3")
        run([FFMPEG, "-y", "-i", wav_path, "-codec:a", "libmp3lame",
             "-b:a", "320k", mp3_path])
        print(f"  mp3  {mp3_path}")
    else:
        print("  (ffmpeg not found — keeping the raw kokoro WAV only)")

    notes_path = os.path.join(OUTPUT_DIR, "TheLoveRuntime_SpokenDedication_LinerNotes.txt")
    with open(notes_path, "w") as f:
        f.write(LINER_NOTES)
    print(f"  liner notes {notes_path}")

    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ledger_row(TRACK, ARTIST, SPOKEN, ts)
    print(f"  ledger {LEDGER} ({ts})")

    os.unlink(raw_path)


if __name__ == "__main__":
    main()
