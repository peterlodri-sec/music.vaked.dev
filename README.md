# music.vaked.dev — The Constellation Sound Node

> *An intergalactic cogito-ergo-sum TV. A screen that is powered but receives no input — a universal HDMI plug lying on the carpet floor — and so it broadcasts its own signal from within.*

Live URL: **[https://music.vaked.dev](https://music.vaked.dev)**

---

## ✦ Overview

`music.vaked.dev` is the living ambient sound node of the **vaked.dev constellation** — the front door to every surface is the hub at [koan.vaked.dev](https://koan.vaked.dev/). It serves as an iframe audio-reactive background layer across `art.vaked.dev` and other ecosystem surfaces.

### Key Features
- **3D WebGL Wireframe Icosahedron & Particle Sphere**: Self-generating Fibonacci particle shell and audio-reactive 3D wireframe Icosahedron mesh that expands and pulses in 60FPS WebGL.
- **Dual-Engine Audio Blend**: Live procedural Web Audio API synthesis (432Hz Drone & EP Vol. 1 Progressions) blended seamlessly with an interactive SoundCloud player.
- **Searchable SoundCloud Mini Player & Drawer**: Embedded SoundCloud Widget API with live search (@peterlodri & featured artist presets), track comments, and independent `SC VOL` volume controls.
- **Featured Artist Partner**: **[8bit-wraith](https://soundcloud.com/8bit-wraith)** (brother & inspiration) integrated with quick-preset player buttons.
- **24-Bit Lossless Master & Vinyl On-Demand**: Audio masters encoded in uncompressed 24-bit 96kHz/48kHz WAV format ready for 0 Ft upfront SoundCloud Vinyl On-Demand distribution.
- **Cross-Site Integration**: Embedded via `<iframe id="musicbg" src="https://music.vaked.dev/" ... style="mix-blend-mode:screen; opacity:0.3"></iframe>` across the constellation.

### Generative originals (synthesized from pure math — no samples, no cloud)

| Track | Script | Shape |
|---|---|---|
| **All My Favorite Colors — Dream Come True Version (D+++)** | `dream_colors.py` | 432 Hz · 88 BPM · verse/chorus/bridge · boom-bap with a swung hat |
| **Friends of Weed and Love (Space Floating)** | `space_floating.py` | 432 Hz · 76 BPM · ultra lo-fi Japanese fusion jazz × Texas desert space psychedelic · stereo, tape wobble, dub echo, sweeping phaser |
| **ULTRALOVEGOD — The Answer to Oblivion** | `ultralovegod_oblivion_answer.py` | 432 Hz · 132 BPM · Juno-106 chorus pad × bouncing bass × 528 Hz Guardian Bed |
| **Innerbloom (Live at The Hordern Pavilion) — Quant Signature** | `innerbloom_quant_signature.py` | 432 Hz · 122 BPM · Ebm9 → Bmaj7 → Gbmaj9 → Db9 · Tracy-Widom spectral rigidity filter bloom |
| **everything i wanted — 8B Love Mom (*) & Dad (△) Sanctuary Edition** | `everything_i_wanted_8b_family.py` | 432 Hz + 528 Hz (*) + 288 Hz (△) · 120 BPM · Dmaj7 → E6 → C#m7 → F#m7 · underwater Fender Rhodes & Golden Gate vocal covenant |
| **Faded — 8B Atlantis Star (*) & Pillar (△) Answer Edition** | `faded_8b_atlantis_answer.py` | 432 Hz + 528 Hz (*) + 288 Hz (△) · 90 BPM · D#m → B → F# → C# · Norwegian felt piano & 7-voice supersaw Atlantis answer |
| **MAHAKALA — Techno-Buddhism × Tibetan Buddhism × Diamond Way (8B Invocation === Recitation === Song)** | `mahakala_diamond_way_8b_invocation.py` | 432 Hz + 108 Hz Mala + 528 Hz (*) + 288 Hz (△) · 108 BPM · Dm9 → C6 → Gsus → D5/A · Tibetan Dungchen horn, 7-metal singing bowl, Kagyu throat-chant formants & Damaru Vajra techno |

Both render a 24-bit WAV master, a 320 kbps MP3, and liner notes into
`~/Documents/music/`, and land a row in `.dogfeed-music.jsonl`
(`node ledger-check.mjs` gates the ledger before push).

### The voice lane (neural — kokoro-tiny, not pure math)

| Track | Script | Voice |
|---|---|---|
| **The Love Runtime (Spoken Dedication)** | `voice_lane.py` | `bm_george` (the narrator mood), 82M Kokoro via `kokoro-speak` |

The runtime's own voice, spoken as an original. `voice_lane.py` drives
`kokoro-speak` (from the [`kokoro-tiny`](https://github.com/8b-is/kokoro-tiny)
binary) to synthesize the spoken dedication, then masters it to the house
spec (24-bit stereo 44.1 kHz) with ffmpeg — same output, same ledger row as
the pure-math lanes. Override the voice with `VOICE_LANE_VOICE` and the
binary path with `KOKORO_SPEAK`.

The 320 kbps master is served on-site as `assets/voice/the-love-runtime-spoken-dedication.mp3`
and surfaced by the **🎤 THE LOVE RUNTIME · SPOKEN** badge in the header —
tap it to hear the runtime speak.

---

## 🌌 Constellation Sister Sites (The Lovetta Lane)

- ✦ **[art.vaked.dev](https://art.vaked.dev)**
- ✦ **[vision-gallery (23)](https://art.vaked.dev/vision-gallery.html)**
- ✦ **[music.vaked.dev](https://music.vaked.dev)**
- ✦ **[quant-love](https://mlxquantlovefrom.com)**
- ✦ **[proposal.vaked.dev](https://proposal.vaked.dev)**
- ✦ **[pocoo.vaked.dev](https://pocoo.vaked.dev)**
- 👾 **[8bit-wraith on SoundCloud](https://soundcloud.com/8bit-wraith)** *(brother & inspiration)*

*the constellation · 0 + 1 · fine touch from within · vaked.dev*

## the ledger's cadence

`.dogfeed-music.jsonl` grows by design (one row per new track). The ledger is
committed on the session's push rhythm, not per-row: a perpetual-dirty
working tree is the ledger's honest state, and an auto-commit would
race the loop. If a row matters more than the rhythm, it already moved
to the HF bucket too.

- Schema: one JSON row per play — `ts` (UTC ISO 8601), `track`, `artist`,
  `lyrics` (lrclib synced text, capped at 2000 chars; empty when absent).
- Check: `node ledger-check.mjs` validates every row (schema, monotonic
  timestamps, caps) and prints the stats. The backyard ultra gates run it.
