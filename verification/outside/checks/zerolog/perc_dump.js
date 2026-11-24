// Usage: node perc_dump.js <critical model path> '<json list of seeds>'. Prints spanning-cluster mass (value, jackknife err) per L per seed.
const C = require(process.argv[2]);
const seeds = JSON.parse(process.argv[3]);
const out = seeds.map(s => { const r = C.studyPercolation(s); return { seed: s, Ls: r.Ls, span: r.span.map(x => [x.value, x.err]) }; });
console.log(JSON.stringify(out));
