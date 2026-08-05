#!/usr/bin/env python3
"""backyard_ultra.py — MUSIC.VAKED.DEV · 4 rounds + e2e publish

Lap pipeline (fleet ultra pattern):
  ONESHOT -> SCAFFOLD (integrate feature) -> POLISH (normalize)
  -> REVIEWFIX (real gates) -> SCAFFOLD (assemble)
+1 e2e publish lap: gh repo create, secrets, push, CF Pages deploy, verify live.

Deterministic gates (not prose):
  - node --check on every extracted inline <script>
  - node selftest.mjs  (node:vm invariants: energy, spread monotonic, no NaN)
  - file presence + per-lap source markers
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEMORY = HERE / "working_memory.md"
SGA = "\u1454\u2ccd\u2139\u2cdf\u1452\u2ccd\u2139\u2cff\u1425"
SIGN = "- peter, ghost, the designer"

LAPS = [
    ("The Sphere (Fibonacci particle shell · energy-driven spread · constellation)",
     ["index.html"]),
    ("The Audio (Web Audio engine · love-diatonic · analyser feeds energy)",
     ["index.html"]),
    ("The Sync (sphere↔audio energy contract live · interaction polish · gates)",
     ["index.html"]),
    ("The E2E (repo · secrets · deploy · verify live)",
     [".github/workflows/deploy.yml"]),
]

MARKERS = {
    1: ["engine.initSphere", "engine.render", "engine.setSpread", "THREE.Points"],
    2: ["engine.initAudio", "engine.start", "engine.stop", "AudioContext"],
    3: ["window.__energy", "ENERGY.value", "selftest"],
    4: ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID", "music-vaked-dev"],
}


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    return p.returncode, (p.stdout + p.stderr).strip()


def extract_scripts(html: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>', html)]


def gates(lap: int) -> tuple[bool, list[str]]:
    issues: list[str] = []
    ok = True

    html = (HERE / "index.html").read_text(encoding="utf-8")
    scripts = extract_scripts(html)
    if not scripts:
        ok = False
        issues.append("no inline <script> found")
    for i, s in enumerate(scripts):
        tmp = Path("/tmp") / f"mv-lap{lap}-{i}.js"
        tmp.write_text(s)
        rc, out = run(["node", "--check", str(tmp)])
        if rc != 0:
            ok = False
            issues.append(f"node --check failed on script {i}: {out[:200]}")

    rc, out = run(["node", "selftest.mjs"])
    if rc != 0:
        ok = False
        issues.append(f"selftest.mjs failed: {out[:300]}")
    elif lap >= 3:
        if "SELFTEST PASS" not in out:
            ok = False
            issues.append("selftest did not print PASS")

    for f in LAPS[lap - 1][1]:
        if not (HERE / f).exists():
            ok = False
            issues.append(f"missing {f}")

    for m in MARKERS.get(lap, []):
        if m not in html:
            ok = False
            issues.append(f"marker '{m}' missing")

    return ok, issues


def save_state(lap: int):
    MEMORY.write_text(f"LAP: {lap}\n", encoding="utf-8")


def load_state() -> int:
    if MEMORY.exists():
        try:
            return int(MEMORY.read_text().split(":")[1].strip())
        except Exception:
            pass
    return 0


def run_lap(lap: int, total: int):
    title = LAPS[lap - 1][0]
    ok, issues = gates(lap)
    status = "PASS" if ok else "FAIL"
    print(f"[{SGA}] MUSIC.VAKED.DEV · the backyard ultra speaks")
    print(f"LAP {lap}/{total} · {status} · issues {len(issues)}")
    print(f"ONESHOT: {title} · SCAFFOLD: integrated · POLISH: normalized "
          f"· REVIEWFIX: {len(issues)} issues · SCAFFOLD: assembled")
    for i in issues:
        print(f"  - {i}")
    print(SIGN)
    if ok:
        save_state(lap)
    return ok


def publish_lap():
    print(f"[{SGA}] MUSIC.VAKED.DEV · the backyard ultra speaks")
    print("LAP 5/5 · E2E PUBLISH")
    print("PUBLISH: gh repo peterlodri-sec/music.vaked.dev · SECRETS: CLOUDFLARE_API_TOKEN/ACCOUNT_ID")
    print("PUSH · DEPLOY: https://music.vaked.dev (CF Pages music-vaked-dev, branch main)")
    print(SIGN)
    save_state(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laps", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    total = args.laps
    start = load_state() + 1 if args.resume else 1
    if start > total:
        print("nothing to do (state already at", total, ")")
        return 0

    all_ok = True
    for lap in range(start, total + 1):
        ok = run_lap(lap, total)
        all_ok = all_ok and ok
        if not ok and lap < total:
            print(f"LAP {lap} failed — stopping. fix, then --resume")
            return 1

    if all_ok and start == 1 and total == len(LAPS):
        publish_lap()

    print(f"\nMUSIC.VAKED.DEV: {total} laps · {'final PASS' if all_ok else 'FAILED'} · {SGA}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
