# music.vaked.dev

An intergalactic cogito-ergo-sum TV. A screen that is powered but receives
no input — a universal HDMI plug lying on the carpet floor — and so it
broadcasts its own signal from within.

A self-generating constellation (Three.js particle sphere) synced to a
procedural Web Audio engine. No samples, no assets, no backend. Every note
and every star is computed in the browser.

## Concept

- **SPREAD SPHERE ALL** — a sphere of particles that spreads into a
  constellation as the music's energy rises; at rest it still breathes at an
  idle baseline (a powered screen is never truly silent).
- **INTO LOVE** — the music is a generative love-progression: soft pads, a
  slow melody, a warm bass, all produced live from a seeded voice.
- **0 + 1** — the engine is a two-voice binary heart: an LFO and an analyser
  agree on the energy that drives the sphere.

## Build / run

Static site, zero build step. Open `index.html` in a browser, or:

```bash
python3 -m http.server 8080
# → http://localhost:8080
```

## Gates

```bash
node selftest.mjs   # node:vm gate — energy invariant, spread monotonic, no NaN
```

`node --check` on the extracted inline scripts + the `vm` selftest above are
the project's deterministic checks.

## Deploy

Push-to-deploy: `.github/workflows/deploy.yml` uploads `_site/` to the
Cloudflare Pages project `music-vaked-dev` (branch `main`), which serves
`https://music.vaked.dev/`.

AGPL-3.0. Source: https://github.com/peterlodri-sec/music.vaked.dev
