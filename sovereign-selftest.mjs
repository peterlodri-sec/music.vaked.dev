#!/usr/bin/env node
/*
  sovereign-selftest.mjs — the Sovereign Library's corridor.
  SPDX-License-Identifier: AGPL-3.0-only

  vm-runs sovereign-sdk.js with stubbed localStorage/document and asserts:
    * get/set/clear roundtrip
    * token normalization (no doubled "Sovereign" prefix)
    * the auth header shape
    * format gating (64-byte Ed25519 shell, short/garbage/empty rejected)
    * the badge updates BOTH directions (unlock markup, locked fallback)
  Exit 0 on pass, 1 on fail.
*/
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const HERE = dirname(fileURLToPath(import.meta.url));
const code = readFileSync(resolve(HERE, 'sovereign-sdk.js'), 'utf8');

const store = new Map();
let badgeHTML = '';
const style = {
  borderColor: '', color: '',
};
const sandbox = {
  localStorage: {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => { store.set(k, String(v)); },
    removeItem: (k) => { store.delete(k); }
  },
  document: {
    addEventListener: () => {},
    getElementById: (id) => (id === 'lovetta-sovereign-badge' ? {
      style,
      set innerHTML(v) { badgeHTML = v; },
      get innerHTML() { return badgeHTML; },
      addEventListener: () => {}
    } : null)
  },
  alert: () => {},
  prompt: () => null
};
sandbox.Buffer = Buffer;
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: 'sovereign-sdk.js' });
const S = sandbox.SovereignSDK;

let pass = 0, fail = 0;
const ok = (name, cond) => { cond ? pass++ : fail++; console.log((cond ? '  ok  ' : '  FAIL ') + name); };

const fat = Buffer.alloc(80).toString('base64');      // 80 bytes — the 64+ shell
const thin = Buffer.alloc(40).toString('base64');     // 40 bytes — below the shell

ok('starts locked with no token', S.getToken() === '');
ok('setToken stores the trimmed token', S.setToken('  abcd1234  ') === true && S.getToken() === 'abcd1234');
ok('setToken normalizes the Sovereign prefix', S.setToken('Sovereign abcdef') === true && S.getToken() === 'abcdef');
ok('auth header never doubles the prefix', S.getToken() === 'abcdef' && S.getAuthHeader().Authorization === 'Sovereign abcdef');
ok('empty auth header when locked', (S.clearToken(), Object.keys(S.getAuthHeader()).length === 0));
ok('format gate: 64+ byte token passes', S.verifyFormat(fat) === true);
ok('format gate: short token rejected', S.verifyFormat(thin) === false);
ok('format gate: garbage rejected', S.verifyFormat('not-base64!!!') === false);
ok('format gate: empty rejected', S.verifyFormat('') === false && S.verifyFormat(null) === false);
ok('setToken rejects non-strings', S.setToken(123) === false && S.setToken('   ') === false);
ok('isUnlocked follows the stored token', (S.setToken(fat), S.isUnlocked() === true));
ok('clearToken locks again', (S.clearToken(), S.isUnlocked() === false));
ok('badge unlocks with markup', (S.setToken(fat), S.updateBadgeUI(), badgeHTML.includes('SOVEREIGN GOD MODE')));
ok('badge locks back to the plain name', (S.clearToken(), S.updateBadgeUI(), badgeHTML.includes('SOVEREIGN') && !badgeHTML.includes('GOD MODE')));

console.log(`\nsovereign selftest: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);