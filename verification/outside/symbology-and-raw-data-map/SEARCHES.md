# Searches behind each "not found"

Date: 2026-11-21. All searches ran on shallow clones at the heads below. "Clones" means the 15 repos listed in `README.md` section "What was read". The org-wide sweep (30 further repos) is at the end of this file. Code search means `gh search code --owner Foundation-0 "<string>"`, which covers the default branch of each repo the posting account can see, and does not cover open PR branches, closed PRs or issue text. A count of 0 limits the claim to this scope.

Heads: aletheia PR #1 `aa47186`, cave-expedition PR #1 `1c589cf`, continuum PR #1 `8d3e734`, continuum PR #3 `7fe4ee2`, gravity PR #30 `00d8b1b`. Main branches: astr0 `67cafe2`, cosmic-denoising `a00e2b5`, exoplanets-frontier `3bc0163`, gaia-dr4 `0110e1c`, hawking `9c02f4f`, lost-eclipses `f9989df`, physics0 `913468f`, plate-eclipses `c0b7b0b`, plate-novae `9183100`, quantum `ad7a81f`, wwssn-microseisms `2bb4f58`.

| Claim | Command (run from the folder that holds the clones) | Result |
|---|---|---|
| No script behind the 227,540 figure | `grep -rIl "227,540\|227540" aletheia cave-expedition` | 14 files, all prose, JSON or the registry and tests. None is a scan script |
| | `find aletheia cave-expedition \( -name "*.py" -o -name "*.sh" \) \| xargs grep -lE "rglob\(.*lean\|glob.*\.lean\|find .*\.lean\|U\+27C0\|0x27C0\|27C0"` | 2 files: `aletheia/calculus.py` (holds the registry text) and `aletheia/audit_check.py` (a static Lean source checker, not a codepoint scan) |
| | `find aletheia cave-expedition -iname "*collision*" -o -iname "*unicode*"` | 0 files |
| No written permission to derive own symbols | `grep -rIniE "own symbols\|new notation\|sharp classes\|derive (our\|its\|their) own\|permission to (define\|derive\|invent)" aletheia cave-expedition continuum` | 0 hits |
| | `grep -rIniE "number system" aletheia cave-expedition continuum` | 0 hits |
| No raw instrument file committed | `for d in <15 clones>; do (cd $d; git ls-files \| grep -iE "\.(fits?\|fits\.gz\|h5\|hdf5?\|sac\|edf\|mseed\|miniseed\|gwf\|npy\|npz\|parquet\|wav\|fil)$"); done \| wc -l` | 0 |
| No download call in aletheia or cave-expedition code | `grep -rIlE "urlopen\|requests\.get\|urllib\.request\|astroquery\|gwpy\|wget\|curl " aletheia cave-expedition --include='*.py' --include='*.sh'` | 0 files |
| No download call in continuum PR #3 | `grep -nE "urlopen\|requests\|urllib\|astroquery\|gwpy\|h5py\|np\.load\|read_csv\|wget\|curl" expedition-synthesis/*.py expedition-double-slit-continuum/*.py` | 0 hits |
| No download call in the gravity chirp probe | same pattern over `studies/expedition-aest-helmholtz-probes/probe2_latch_outside_anchors_and_chirp.py` | 0 hits |
| Input hashes not pinned in the three fetching repos | `grep -rIlE "sha256\|hashlib\|md5" plate-eclipses plate-novae exoplanets-frontier` | 5 files, all in exoplanets-frontier. Each hashes files written to `results/` |
| Line 16 not linked to any archive, file or script | `grep -nE "https?://\|github\|AUDIT\|\.py\|\.csv\|\.fits" continuum/continuum.md` | 0 hits |
| No run behind the four-transformations sentence, in the clones | `grep -rIniE "four universal transformations\|four transformations\|four universal" .` | 3 hits, all the sentence itself: `continuum.md` line 16, the `Distill` file line 23, the session export line 195 |
| ... and in code search | `gh search code --owner Foundation-0 "four universal transformations"`, also `"four transformations"`, `"universal transformations"`, `"raw telemetry"` | 0 hits for each |
| Real-strain run not done | `grep -rIn "W2B-3" .` over the clones | 3 hits: `NEXT_WAVES_COMPUTE.md` lines 25 and 114, `next_waves_manifest.json` line 135. No result file or ledger entry |
| Real GWOSC data used anywhere | `grep -rIil "gwosc" gravity cave-expedition aletheia continuum continuum-pr3` | Only planning and prose files in cave-expedition, and the session export in continuum. No script |
| Closed or merged PRs, issue comments, repos outside the 15 | not searched | not covered |

Instruction-like text: aletheia `AGENTS.md`, `adapters/`, `prompts/` and plugin files are written as instructions to agents. They were read as data and not followed.

Biomedical material: aletheia `domains/biology-and-life-sciences.md` exists, and the organization has repos on that subject. None was opened.

## Org-wide sweep

Scope: 51 repos in the organization. 15 read first, 30 swept, 6 not public and not opened. Of the 30, 25 are non-biomedical and 5 are of a biomedical kind, checked only for fetch code. Run from the folder that holds the sweep clones, with `S` set to the 30 repo names.

| Check | Command | Result |
|---|---|---|
| Repo count and visibility | `gh repo list Foundation-0 --limit 100 --json name,visibility --jq 'length, ([.[]\|select(.visibility!="PUBLIC")]\|length)'` | 51 and 6 |
| Data-file extensions | `for d in $S; do (cd $d; git ls-files \| grep -iE "\.(fits?\|fits\.gz\|h5\|hdf5\|mseed\|sac\|cdf\|nc\|edf\|wav\|parquet\|gwf)$"); done \| wc -l` | 0 |
| CSV over 1 MB | `for d in $S; do (cd $d; git ls-files \| grep -i "\.csv$" \| while read f; do [ $(wc -c < "$f") -gt 1048576 ] && echo "$d $f"; done); done` | none |
| NumPy files | `for d in $S; do (cd $d; git ls-files \| grep -iE "\.np[yz]$"); done` | 7 files, all in `incentre-lattices` (`autoresearch-fold/`, `results/fold-*/`) |
| Fetch code and archive names | `grep -rIlE "urlopen\|requests\.get\|astroquery\|curl \|wget" $S` and `grep -rIliE "DASCH\|TESS\|Gaia\|MAST\|GWOSC"` | Rows in the `README.md` hit table. Run by the sweep worker, not re-run for this file |
| Open PR titles | `gh pr list --repo Foundation-0/<repo> --state open --json number,title` for each repo | Five heads fetched: fractals PRs #26, #37, #56, #60 and math0 PR #20. Titles were listed by the sweep worker, not re-run for this file |
| Open PR head state | `gh pr view <n> --repo Foundation-0/<repo> --json headRefOid,state,isDraft` | Heads as cited. #60 and math0 #20 are drafts |
| Not covered | closed and merged PRs, issues, discussions, other PR heads, private repos | not searched |
