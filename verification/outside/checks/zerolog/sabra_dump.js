// Usage: node sabra_dump.js <turbulence model path> '<json list of configs>'
// Each config: {run: {...overrides of RUNS.CI}, lambda?: number}. Prints per-block S2, F2, F3, F6, Sig, Pi, inj.
// Reads the model only; writes stdout only. Run by check_sampled_evaluator.py.
const T = require(process.argv[2]);
const cfgs = JSON.parse(process.argv[3]);
const out = [];
for (const c of cfgs) {
  T.SABRA.lambda = c.lambda !== undefined ? c.lambda : 2; // create() reads SABRA.lambda as its default at call time
  const base = Object.assign({}, T.RUNS.CI, c.run || {});
  const t0 = Date.now();
  const res = T.simulate(base);
  const nb = res.stats.nBlocks, N = res.stats.N;
  const blk = [...Array(nb).keys()].map(b => T.averages(res, [b]));
  out.push({ cfg: c, N, nb, finite: res.finite, secs: (Date.now() - t0) / 1000, lambda: res.model.lambda,
    k: Array.from(res.model.k).slice(2, N + 2), a: res.model.a, c: res.model.c,
    S2: blk.map(a => Array.from(a.S[1])), F2: blk.map(a => Array.from(a.F[1])), F3: blk.map(a => Array.from(a.F[2])),
    F6: blk.map(a => Array.from(a.F[5])), Sig: blk.map(a => Array.from(a.Sig)), Pi: blk.map(a => Array.from(a.Pi)),
    inj: blk.map(a => a.inj) });
}
console.log(JSON.stringify(out));
