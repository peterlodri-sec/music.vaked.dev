#!/usr/bin/env node
/*
  ledger-check.mjs — deterministic gate for .dogfeed-music.jsonl
  SPDX-License-Identifier: AGPL-3.0-only

  Validates every row of the dogfeed ledger before it is synced:
    * each line parses as a JSON object
    * exact schema: {ts, track, artist, lyrics} — nothing missing, nothing extra
    * ts is UTC ISO 8601 (…Z) and nondecreasing across the ledger
    * track / artist are non-empty strings
    * lyrics is a string of at most LYRIC_CAP chars (the lane's contract,
      see music-dogfeed.py), free of control characters besides \n and \t

  Usage: node ledger-check.mjs
  Exit 0 on pass (prints LEDGER PASS + stats), 1 on fail.
*/
import { readFileSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const LEDGER = resolve(HERE, ".dogfeed-music.jsonl");
const LYRIC_CAP = 2000; // keep in sync with music-dogfeed.py
const TS_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const CONTROL_RE = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/;

const problems = [];
const lines = readFileSync(LEDGER, "utf8")
  .split("\n")
  .map((l) => l.trimEnd())
  .filter((l) => l.length > 0);

const rows = [];
for (let i = 0; i < lines.length; i++) {
  const n = i + 1;
  let row;
  try {
    row = JSON.parse(lines[i]);
  } catch (e) {
    problems.push(`line ${n}: not valid JSON (${e.message})`);
    continue;
  }
  const keys = Object.keys(row).sort().join(",");
  if (keys !== "artist,lyrics,track,ts") {
    problems.push(`line ${n}: keys must be exactly ts/track/artist/lyrics — got [${keys}]`);
    continue;
  }
  if (typeof row.ts !== "string" || !TS_RE.test(row.ts) || Number.isNaN(Date.parse(row.ts))) {
    problems.push(`line ${n}: ts is not UTC ISO 8601 — ${JSON.stringify(row.ts)}`);
  }
  if (typeof row.track !== "string" || row.track.trim() === "") {
    problems.push(`line ${n}: empty track`);
  }
  if (typeof row.artist !== "string" || row.artist.trim() === "") {
    problems.push(`line ${n}: empty artist`);
  }
  if (typeof row.lyrics !== "string") {
    problems.push(`line ${n}: lyrics is not a string`);
  } else {
    if (row.lyrics.length > LYRIC_CAP) {
      problems.push(`line ${n}: lyrics ${row.lyrics.length} chars exceeds cap ${LYRIC_CAP}`);
    }
    if (CONTROL_RE.test(row.lyrics) || CONTROL_RE.test(row.track) || CONTROL_RE.test(row.artist)) {
      problems.push(`line ${n}: control characters in row`);
    }
  }
  rows.push({ n, ...row });
}

for (let i = 1; i < rows.length; i++) {
  if (rows[i].ts < rows[i - 1].ts) {
    problems.push(`ts goes backwards at line ${rows[i].n}: ${rows[i - 1].ts} → ${rows[i].ts}`);
  }
}

const artists = new Set(rows.map((r) => r.artist)).size;
const tracks = new Set(rows.map((r) => `${r.artist} — ${r.track}`)).size;
const withLyrics = rows.filter((r) => r.lyrics.length > 0).length;
const synced = rows.filter((r) => /^\[\d\d:\d\d\.\d\d\]/.test(r.lyrics)).length;
const bytes = statSync(LEDGER).size;
const kb = (bytes / 1024).toFixed(0);
const first = rows.length ? rows[0].ts : "—";
const last = rows.length ? rows[rows.length - 1].ts : "—";

if (problems.length > 0) {
  console.error(`LEDGER FAIL — ${problems.length} problem(s) in ${lines.length} row(s)`);
  for (const p of problems.slice(0, 10)) console.error(`  - ${p}`);
  if (problems.length > 10) console.error(`  …and ${problems.length - 10} more`);
  process.exit(1);
}

console.log(
  `LEDGER PASS — ${rows.length} rows · ${tracks} tracks · ${artists} artists · ` +
  `${withLyrics} with lyrics (${synced} synced) · ${kb} KB · ${first} → ${last}`
);
