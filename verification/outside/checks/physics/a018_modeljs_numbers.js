// Independent reproduction of the model.js numbers behind AUDIT-018.
//
// Backs: VERDICTS section 1 row "16x16 Lindblad reduction (018)", the part that
// says the model.js numbers reproduce: lump lifetime 2.41e-14 s at 1e-22 eV,
// 1.42e21 s at 3e-19 eV, the crossover masses 2.83e-20 eV (lifetime equals the
// lump time) and 1.34e-19 eV (lifetime equals the age of the universe), and the
// slope of exactly 10 in log rate against log mass.
//
// It calls the model's own crowd() and rates() (the horizon term) for a lump of
// mass mLump with gap lam and b = 8.18 kpc, then judges the results against the
// reported values. Pure arithmetic, no random numbers, no network.
//
// Needs: node; the file witness-map/model.js from a clone of Foundation-0/fractals
//        (draft pull request 59).
// Run:   node a018_modeljs_numbers.js /path/to/fractals/witness-map/model.js
//        (or set FRACTALS_MODEL_JS to that path)
// Time:  under one second.
// Exit:  0 only if every check holds.
"use strict";
const fs = require("fs");
const path = require("path");

const NAME = "a018_modeljs_numbers";
const modelPath = process.argv[2] || process.env.FRACTALS_MODEL_JS || "";
if (!modelPath || !fs.existsSync(modelPath)) {
  console.error("Pass the path of witness-map/model.js from a Foundation-0/fractals clone as the first argument or set FRACTALS_MODEL_JS.");
  process.exit(2);
}
const WM = require(path.resolve(modelPath));
const C = WM.C, b = 8.18 * C.kpc, BH = { M: WM.BH_M, b };

function lumpRow(meV) {
  const SUN = WM.CROWDS[0];
  const h = { ...SUN, m: meV * C.eV };
  const cr = WM.crowd(h);
  const r = WM.rates({ m: cr.mLump, dark: true }, WM.ENVS.intergalactic, cr.lam, BH);
  return { meV, N: cr.perLump, lam_pc: cr.lam / (C.kpc / 1e3), tLump: cr.tLump, tauBH: r.tau, W: r.W, bhNote: r.bhNote };
}
function solve(f) {
  let lo = Math.log(1e-23), hi = Math.log(1e-17);
  for (let i = 0; i < 200; i++) { const mid = (lo + hi) / 2; if (f(Math.exp(mid)) < 0) lo = mid; else hi = mid; }
  return Math.exp((lo + hi) / 2);
}

const fails = [];
let count = 0;
function check(cond, msg) { count += 1; if (!cond) fails.push(msg); }
function near(x, want, rel) { return Math.abs(x - want) <= rel * Math.abs(want); }

const rows = [1e-22, 3e-19, 1e-21, 1e-20].map(lumpRow);
const mStarLump = solve(m => { const r = lumpRow(m); return Math.log(r.tauBH / r.tLump); });
const mStarAge = solve(m => Math.log(lumpRow(m).tauBH / WM.AGE));
const a = lumpRow(1e-22), c = lumpRow(1e-21);
const slope = Math.log10(a.tauBH / c.tauBH) * -1;

check(near(rows[0].tauBH, 2.41e-14, 0.005), "lifetime at 1e-22 eV is not 2.41e-14 s");
check(near(rows[1].tauBH, 1.42e21, 0.005), "lifetime at 3e-19 eV is not 1.42e21 s");
check(near(mStarLump, 2.83e-20, 0.005), "crossover with the lump time is not 2.83e-20 eV");
check(near(mStarAge, 1.34e-19, 0.005), "crossover with the age is not 1.34e-19 eV");
check(Math.abs(slope - 10) < 1e-9, "slope in log rate against log mass is not exactly 10");
check(rows.every(r => r.bhNote === null), "the model attached a note to a lump row");

if (process.argv.includes("--verbose")) console.log(JSON.stringify({ rows, mStarLump, mStarAge, slope }, null, 1));
if (fails.length) {
  console.log(`RESULT ${NAME}: FAIL ${fails.length} of ${count} checks: ${fails.slice(0, 4).join("; ")}`);
  process.exit(1);
}
console.log(`RESULT ${NAME}: PASS ${count} of ${count} checks; tau ${rows[0].tauBH.toExponential(2)} s and ${rows[1].tauBH.toExponential(2)} s, ` +
  `m* ${mStarLump.toExponential(2)} eV and ${mStarAge.toExponential(2)} eV, slope ${slope.toFixed(6)}`);
