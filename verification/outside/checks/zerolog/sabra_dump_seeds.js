// Dump per-block S2 (plain <|u_n|^2>) and F2 (flux-based) for the team's CI Sabra run, one line of JSON.
// Usage: node sabra_dump_seeds.js <path to turbulence/model.js> <seed,seed,...> [b]  (c = -1 - b, a = 1)
'use strict';
const T = require(process.argv[2]);
const seeds = process.argv[3].split(',').map(Number);
const bArg = process.argv[4] === undefined ? null : Number(process.argv[4]);
const extra = bArg === null ? {} : { a: 1, b: bArg, c: -1 - bArg };
const out = {};
for (const seed of seeds) {
  const res = T.simulate({ ...T.RUNS.CI, ...extra, seed });
  const nb = res.stats.nBlocks, N = res.stats.N;
  const all = T.averages(res);
  const blk = [...Array(nb).keys()].map(b => T.averages(res, [b]));
  out[seed] = {
    N, nb, finite: res.finite,
    S2: Array.from(all.S[1]), F2: Array.from(all.F[1]),
    S2b: blk.map(a => Array.from(a.S[1])), F2b: blk.map(a => Array.from(a.F[1])),
  };
}
console.log(JSON.stringify(out));
