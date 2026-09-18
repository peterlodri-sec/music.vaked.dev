#!/usr/bin/env python3
"""music-dogfeed.py — the constant bidirectional dogfeeding loop.

Every poll, the CURRENT Apple Music track (name · artist · E2E lyrics)
rides to ALL constellation surfaces at once:

  1. the site   — POST :8787/nowplaying   (music.vaked.dev's own webhook)
  2. the stream — the mapping-stream replay inbox (wa-stream/replay.txt)
  3. the ledger — a dogfeed row appended to .dogfeed-music.jsonl
  4. the hub    — optional HF upload of the feed when DOGFOOD=1

Only fires when the track CHANGES (a constant loop, not a spam loop).
Bidirectional: the site displays what the lane streams, and the lane
streams what the site plays.
"""
import json, os, subprocess, sys, time, urllib.request, urllib.parse

def nowplaying():
    """(track, artist) from Apple Music via osascript, or (None, None)."""
    try:
        out = subprocess.run(
            ["osascript", "-e",
             'tell application "Music" to {name, artist} of current track'],
            capture_output=True, text=True, timeout=8)
        if out.returncode != 0:
            return None, None
        parts = [p.strip() for p in out.stdout.split(", ")]
        return (parts[0], parts[1]) if len(parts) == 2 else (None, None)
    except Exception:
        return None, None

def lyrics(track, artist):
    try:
        q = urllib.parse.urlencode({"artist_name": artist, "track_name": track})
        with urllib.request.urlopen(
                f"https://lrclib.net/api/get?{q}", timeout=12) as r:
            d = json.loads(r.read().decode())
            return d.get("syncedLyrics") or d.get("plainLyrics") or ""
    except Exception:
        return ""

def post_nowplaying(track, artist, song_lyrics):
    try:
        secret = os.environ.get("WA_WEBHOOK_SECRET") or os.environ.get("WEBHOOK_SECRET") or ""
        req = urllib.request.Request(
            "http://localhost:8787/nowplaying",
            data=json.dumps({"session_id": "music", "track": track,
                             "artist": artist, "lyrics": song_lyrics[:2000]}).encode(),
            headers={"Content-Type": "application/json",
                     **({"x-wa-token": secret} if secret else {})}, method="POST")
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        print(f"  ! site: {e}")

def post_replay(track, artist, song_lyrics):
    line = (f"🎵 {track} — {artist}"
            + ("\n📜 " + song_lyrics[:400] if song_lyrics else ""))
    here = os.path.dirname(os.path.abspath(__file__))
    inbox = os.environ.get("REPLAY_FILE") or os.path.join(here, "..", "wa-stream", "replay.txt")
    try:
        with open(inbox, "a") as f:
            f.write(line.replace("\n", " ") + "\n")
    except Exception as e:
        print(f"  ! stream: {e}")

def ledger_row(track, artist, song_lyrics, ts):
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, ".dogfeed-music.jsonl")
    try:
        with open(p, "a") as f:
            f.write(json.dumps({"ts": ts, "track": track, "artist": artist,
                                "lyrics": song_lyrics[:2000]}) + "\n")
        if os.environ.get("DOGFOOD") == "1":
            subprocess.run(["hf", "upload", "PeetPedro/ultrawhale-dogfood-bucket",
                            p, f"music/{ts}.jsonl"], capture_output=True, timeout=120)
    except Exception as e:
        print(f"  ! ledger: {e}")

def main():
    once = "--once" in sys.argv
    poll = float(os.environ.get("POLL_SEC", "20"))
    last = None
    while True:
        track, artist = nowplaying()
        if track and (track, artist) != last:
            song_lyrics = lyrics(track, artist)
            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            print(f"🎵 {track} — {artist} · E2E lyrics: {'on' if song_lyrics else 'off'}")
            post_nowplaying(track, artist, song_lyrics)
            post_replay(track, artist, song_lyrics)
            ledger_row(track, artist, song_lyrics, ts)
            last = (track, artist)
        if once:
            break
        time.sleep(poll)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
