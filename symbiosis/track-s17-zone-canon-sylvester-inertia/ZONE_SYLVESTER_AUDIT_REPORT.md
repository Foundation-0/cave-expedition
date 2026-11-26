# AUDIT-114: Cross-Org Exact-Operator Unification (`zone-canon-v0`, Exact-$\mathbb{Q}$ Sylvester Inertia, and Typed Gate-Axiom Witnesses)

- **Track:** `track-s17-zone-canon-sylvester-inertia` (`AUDIT-114`)
- **Oracle Class:** `exact` (strictly pure-$\mathbb{Z}/\mathbb{Q}$ Python 3 standard library; `0` floats on trust paths; `0` bare `assert`s; `0` third-party dependencies; `0` shared implementation code with upstream repositories)
- **Honest Law-4 Novelty & Scope Classification:** **`N0` / `N1`**
  - **`N0` (Re-verified Known Mathematics & Prior Art):** Sylvester's law of inertia, Bunch–Kaufman $1\times 1$/$2\times 2$ block pivoting, Faddeev–LeVerrier/Descartes root counting, Weyl's inequalities, trace rank lower bounds (`R_A`, `R_B` = Alpoge–Furman Lemma 3.2, `R_G` = Knausgard Lemma 6.1, `R_opt` = `spectral-inertia#2` Theorem A1), low-rank adapter equivalence $\sigma_{\max}(BA)^2 \le s \iff Q(s) \succeq 0$, and non-convexity of the two-bar truss stability set (`aska-physical/fibral-rigidity#5`).
  - **`N1` (Exact Cross-Org Differential Proofs & Executable Witness Unification):**
    1. Exact algebraic set-difference and byte-divergence characterization between `siliconcordat/mde#8` (`zone-canon-v0`) and `Foundation-0/aletheia` (`v2.0 strict_io` / `v2.1 supervision_airlock`), including an exhaustive `0x00..0x7F` proof isolating `0x7F` (`DEL`) as the sole divergent ASCII code point.
    2. Complete pure-$\mathbb{Q}$ 4-region proof that `(9/10, 11/10)` in `fibral-rigidity#5`'s verified box `[7/10, 13/10] x [9/10, 15/10]` admits **zero** positive-definite equilibria anywhere in $\mathbb{R}^2$ (certifying both on-line roots `x = -1/10` `(1,0,1)` and `x = -109/100` `(1,1,0)`, empty `(1, +inf)` via `89/100 < 1`, and empty off-line region via $y^2 = 0$), paired with an exact rational non-convexity segment (`t = 1/3`) and matrix-space PSD convexity contrast (`(4/9, 2/9, 2/9, 1/9)`).
    3. Bijective spelling-morphism verification (`loom#7` `"p/1"` $\leftrightarrow$ `spectral-inertia#2` `"p"`) and honest cross-org audit confirming BOTH upstream repos handle zero-diagonal indefinite matrices cleanly via $2\times 2$ pivots.
    4. Executable typed counterexample suite formalizing 5 live cross-org gate failures (`warp#14`, `finite-state-proofs#5`, `fractals#58`, `loom#9`, `formal-claims-audit#19`) under `loom#9`'s Contracts `C1`–`C4` / AG-VBC Axioms `A1`–`A4`.

---

## 1. `OWN_TERMS_FIRST`: Exact Typed Operator Definitions

Before comparing across organizations, each operator is pinned strictly on its own formal domain:

1. **Canonical-JSON Hashing Operators ($C_{\mathrm{zone}}, C_{\mathrm{v21}}$):**
   - `zone-canon-v0` (`siliconcordat/mde#8 @ 3c8e5a26`): domain $\mathcal{D}_{\mathrm{zone}}$ forbids floats, `-0`, integers with $|n| > 2^{53}-1$ (or tokens $> 40$ chars), `NaN`/`Infinity`, duplicate keys, non-string dict keys, and lone UTF-16 surrogates (`U+D800..U+DFFF`); sorts object keys by Unicode code point; emits raw UTF-8 (including `0x7F`), escaping only `"`, `\`, `\b\f\n\r\t`, and `< 0x20` as lowercase `\u00xx`.
   - `aletheia v2.0 strict_io(allow_float=False)` + `v2.1 supervision_airlock.canonical_json_bytes`: domain $\mathcal{D}_{\mathrm{v21}}$ forbids floats, `NaN`/`Infinity`, duplicate keys, and non-string dict keys, but accepts `-0` (parsed to `0`), arbitrary unbounded `int`, and lone UTF-16 surrogates; emits ASCII JSON (`ensure_ascii=True`).
2. **Exact-$\mathbb{Q}$ Symmetric Sylvester Inertia & Parametric Stability Operators:**
   - Congruence operator: given $M \in \mathbb{Q}^{n \times n}_{\mathrm{sym}}$, $P M P^\top = L D L^\top$ with permutation $P$, unit lower-triangular $L$, and non-overlapping symmetric $1\times 1$/$2\times 2$ block-diagonal $D$. Independently cross-checked by Faddeev–LeVerrier characteristic polynomial + exact Descartes' rule of signs + Cayley–Hamilton residual check $p(M) = 0$.
   - Two-bar truss operator (`fibral-rigidity#5 @ 4753275f`, pins $(-1,0),(1,0)$, $EA=1$): maps $(L_1, L_2) \in \mathbb{Q}_{>0}^2$ to its exact raw on-line Hessian ($L_1 + L_2 \le 2$) or Sylvester-congruent off-line Hessian $\mathrm{diag}(1, 1/y)\, H_{\mathrm{raw}}\, \mathrm{diag}(1, 1/y)$ ($L_1 + L_2 > 2, |L_1 - L_2| < 2$).
   - Trace rank lower bounds (`loom#7 @ 64c797d3` §3, `spectral-inertia#2 @ ef1a77db` Theorem A1) and low-rank adapter spectral equivalence $Q(s) = s G_B - G_B G_A G_B \succeq 0 \iff s I - B G_A B^\top \succeq 0$ (`loom#7` §5).
3. **Typed Fail-Closed Gate Operators (`loom#9 @ b2c5c33a` Contracts `C1`–`C4` / AG-VBC Axioms `A1`–`A4`):**
   - Every gate maps raw inputs strictly to accept or typed `Audit114Error` without silent type coercion (`E2`), omission opt-out (`E1`/`R1`/`R2`), domain-inversion false accepts (`C2`), or unhandled runtime crashes (`C1` Clauses 3–4).

---

## 2. Pinned Upstream Receipts (Read-Only Snapshots)

| Upstream PR | Pinned Head SHA | Key File | File SHA-256 |
| --- | --- | --- | --- |
| `siliconcordat/mde#8` | `3c8e5a267b570b6e5b0b2c2febe61700631cddfb` | `vectors/zone-canon-v0.json` | `725358287e66cd9a9773afee832a292f3ac965c3fe8544375ff6a755d555bd24` |
| `siliconcordat/loom#7` | `64c797d30da167db74df7196685c45db3dd22797` | `scripts/inertia_cert.py` | `f1b188f120a8b01aa6ff9e4b36dab42897e107964fa6328b2a5a8ac46fcafede` |
| `siliconcordat/loom#9` | `b2c5c33a3dbd486cbad0c6524391fc5cfc2400f8` | `scripts/gatecheck.py` | `cddaa58665890770f5b7be3ad582a783ee527c4de1898e4529e548d65f493ca3` |
| `siliconcordat/warp#14` | `ef7c292d7beba0eddebaba418488d66fc836f964` | `src/warp_modeld/cli.py` | `50dde4f311cad688811acbeed6d2e794c4cf4450f8a6c4dd5ab21efcbc24195e` |
| `Foundation-0/spectral-inertia#2` | `ef1a77db5924aa958b45c8affbb2424dcb1d9e2b` | `spectral_inertia/dual_oracle.py` | `78d5d1ccc6226a2a0340671290234817e17d5d52d51495216a7e61339ee3b8e8` |
| `aska-physical/fibral-rigidity#5` | `4753275f65c2999a9e10357025fc129b584d5c74` | `length_box.py` | `c6afbb367dc5e8fdb5981ee3035a4304d156a96e23a539cd7513212fa3dd0bb9` |
| `Foundation-0/finite-state-proofs#5` | `dd810d4078e9b3969a9ed9c2abf272bbbbf69015` | `square/verify.py` | `e6a29e44d78e7b8be2f76065c1aa62234e67c7cc2b2d785351e09413acf7d60f` |
| `Foundation-0/fractals#58` | `934e30c33d9d28903f73f12480db52bc80cddf90` | `scaling-check/check.mjs` | `30eb375c6f331fa246d95f399e2e37446e52d8389101421f385ff93fdfe69ad2` |
| `Foundation-0/formal-claims-audit#19` | `f9f3e4307cbbb17fa62ff339fa01eb6e3fcb25d0` | `scripts/check_verdicts.py` | `44ebb34710d67bcbfb751e564cbae5aaf0a7911c1be3ba12cdbcbecd955f1815` |

---

## 3. Pillar 1 Results: `zone-canon-v0` vs `aletheia v2.0/v2.1` Differential Oracle

- **`mde#8` Golden Vector Certification:** **`17/17`** (`7/7` accept byte+SHA exact; `10/10` reject blocked) certified by standalone `zone_sylvester_oracle.canonicalize_zone_canon_v0`.
- **Exact Domain Set-Difference ($\mathcal{D}_{\mathrm{v21}} \setminus \mathcal{D}_{\mathrm{zone}}$):**
  - On `mde#8`'s 10 reject vectors, `aletheia v2.0 strict_io(allow_float=False)` + `v2.1` **accepts 3** (`negative_zero`, `integer_2_pow_53`, `integer_above_u64`) and rejects the other 7 (5 floats, `duplicate_key`, `nan_token`).
  - Beyond `mde#8`, `aletheia v2.1` also accepts `-2^53` (`{"n":-9007199254740992}`) and **lone UTF-16 surrogates** (`{"s":"\ud800"}` $\mapsto$ `b'{"s":"\\ud800"}'`), whereas `zone-canon-v0` rejects both.
- **Exact Byte/Hash Divergence on Shared Domain:**
  - `3/7` `mde#8` accept vectors yield **different SHA-256 hashes** under `aletheia v2.1` (`ensure_ascii=True`) vs `zone-canon-v0` (raw UTF-8): `non_ascii_raw_utf8`, `astral_key_sorts_after_ffff`, and `control_chars_escaped` (because `0x7F` DEL is emitted raw `b'\x7f'` in `zone-canon-v0` vs `b'\\u007f'` in Python `ensure_ascii=True`).
  - Exhaustive sweep of all `128` ASCII code points `0x00..0x7F` proves `ascii_0_127_divergent_codepoints == [127]` (`DEL` is the unique ASCII divergence!).
- **Shared Invariants:** Both reject non-string dict keys (`{1:"a"}`, `{True:"a"}` — unlike raw `json.dumps`), and neither performs NFC/NFD Unicode normalization (`{"\u00e9":1,"e\u0301":2}` is accepted as two distinct keys by both).

---

## 4. Pillar 2 Results: Exact-$\mathbb{Q}$ Sylvester Inertia, Truss Box & `loom#7` Bounds

### 4.1 Zero-Diagonal Indefinite Matrices & Upstream Audit
- Our independent Bunch–Kaufman certifier (`bunch_kaufman_factor_q` / `verify_pldl_certificate_q`) and independent Faddeev–Descartes oracle agree `100%` on $Z_2 = \begin{pmatrix}0&1\\1&0\end{pmatrix}$ `(1,1,0)`, $Z_3 = \mathrm{diag}(0, Z_2)$ `(1,1,1)`, $Z_4$ (4-node path) `(2,2,0)`, and all 5 rows of the $2\times 2$ block inertia table (`det < 0`, `det > 0` with `tr > 0`/`< 0`, `det == 0` with `tr > 0`/`< 0`).
- **Honest Cross-Org Finding:** **BOTH** `siliconcordat/loom#7 @ 64c797d3` (`verify_inertia.py` + `inertia_cert.py`) AND `Foundation-0/spectral-inertia#2 @ ef1a77db` (`dual_oracle.py`) **handle zero-diagonal indefinite matrices cleanly via exact $2\times 2$ block pivots** (returning `(1,1,0)`, `(1,1,1)`, `(2,2,0)`). (`loom#7`'s `margin_cert.py` restricts $D$ to diagonal, which is sound for PSD shifts $M - \lambda I \succeq 0$.)
- **Law-2b Transformational Steelman on Format Incompatibility:** Direct cross-feeding of raw `loom#7` and `spectral-inertia#2` certificates fails `100%` of the time solely due to rational spelling (`"0/1"` vs `"0"`). Applying the exact bijective morphism `translate_pldl_dialect` (`T_rat`) restores **`100%` cross-dialect verification agreement** without touching the underlying algebraic certificate!

### 4.2 `aska-physical/fibral-rigidity#5` Two-Bar Truss Box
- **Verified Exact Parameter Box (`fibral-rigidity#5/length_box.py:6`):** **`[7/10, 13/10] x [9/10, 15/10]`** (note: `15/10 = 3/2`, NOT `11/10`; `(9/10, 11/10)` is the interior singular point!).
- **All 4 Corners Certified Strictly PD `(2, 0, 0)`:** `(7/10, 9/10)`, `(7/10, 3/2)`, `(13/10, 9/10)`, `(13/10, 3/2)`.
- **Complete 4-Region Pure-$\mathbb{Q}$ Proof That `(9/10, 11/10)` Has ZERO PD Equilibria in $\mathbb{R}^2$:**
  1. Between pins $x \in (-1, 1)$: unique root $x = -1/10$, $H = \mathrm{diag}(200/99, 0)$, inertia **`(1, 0, 1)`** (degenerate!).
  2. Left of left pin $x < -1$: unique root $x = -109/100$ (zero force residual), $H = \mathrm{diag}(200/99, -2000/209)$, inertia **`(1, 1, 0)`** (saddle!).
  3. Right of right pin $x > 1$: candidate axial root $x = 89/100 < 1 \implies$ **`0` roots** in $(1, +\infty)$.
  4. Off-line $y \ne 0$: $y^2 = ((L_1+L_2)^2 - 4)(4 - (L_1-L_2)^2)/16 = 0 \implies$ **`0` off-line roots**.
- **Non-Convexity & Non-Affineness Certificate:** $p_0 = (7/10, 9/10)$ `(2,0,0)` and $p_1 = (13/10, 3/2)$ `(2,0,0)` satisfy $\frac{2}{3} p_0 + \frac{1}{3} p_1 = (9/10, 11/10) \notin \mathcal{S}$, whereas the barycentric convex combination of corner Hessians $\frac{4}{9} H(c_1) + \frac{2}{9} H(c_2) + \frac{2}{9} H(c_3) + \frac{1}{9} H(c_4)$ is strictly PD **`(2, 0, 0)`**. Near-flat `(9/10, 11/10 + 10^-9)` is exact **`(2, 0, 0)`**.

### 4.3 `loom#7` Trace Rank Bounds & Low-Rank Adapter Spectral Bounds
- Verified $R_A \le R_G \le R_{\mathrm{opt}} \le \operatorname{rank}(P_1)$ and $R_B \le R_G$, exact algebraic differences $R_B - R_A = 2t - 3b$, $R_G - R_B = (t-2b)^2/b$, $R_G - R_A = (t-b)^2/b$, all 3 tightness witnesses (`c=0, 2, 4`), low/high sharpness witnesses attaining $R_{\mathrm{opt}} = r = 2$, and forged-$b$ negative control ($b_{\mathrm{fake}} = 0 \implies R_{\mathrm{opt}} = 27/11 > 2$).
- Verified low-rank adapter spectral equivalence $Q(s) \succeq 0 \iff s I - B G_A B^\top \succeq 0$ for both full-rank and rank-deficient (singular $G_B$) adapters plus all 5 forgery cases ($B \mapsto 8 B$, $64 s$).

---

## 5. Pillar 3 Results: Typed Fail-Closed Gate-Axiom Witness Suite

| Witness ID | Upstream Source PR | Violated `loom#9` / AG-VBC Axioms | Leaky Defect Reproduced | Hardened Operator Result |
| --- | --- | --- | --- | --- |
| `W1_WARP14_NULL_TO_FALSE` | `siliconcordat/warp#14 @ ef7c292d` | `C1` Clauses 2–3, `R2`/`R3`, `A1` | `None`/`0`/`""`/`[]`/`{}` $\mapsto$ `False` (5 silent opt-outs); `"false"` $\mapsto$ `True` | `6/6` rejected (`INVALID_BOOL_TYPE`) |
| `W2_FSP5_BOOL_AS_INT` | `Foundation-0/finite-state-proofs#5 @ dd810d40` | `C1` Clause 3, `R3`, `A3` | `isinstance(False/True, int)` accepts both | `3/3` (`False`, `True`, `-1`) rejected |
| `W3_FRACTALS58_ZERO_OVER_ZERO_SCALE` | `Foundation-0/fractals#58 @ 934e30c3` | `C2` Exact Soundness, `C1` Clause 1, `A3` | `x=[2,2]` falsely passes `[100,100]`; `x=[4,2]` falsely fails `[1,3]` | `2/2` rejected (`FRACTALS58_NON_INCREASING_SCALE`) |
| `W4_LOOM9_LEAF_MUTANTS_CRASH` | `siliconcordat/loom#9 @ b2c5c33a` | `C1` Clauses 3–4, `R3`/`R4` | `"1/0"` (`ZeroDivisionError`), `"1/"+"9"*5000` (`ValueError`), `"1"+"0"*400+"/1"` (`OverflowError`) | `3/3` handled safely (`0` crashes, `0` floats) |
| `W5_FCA19_EMPTY_GLOB_VACUOUS_PASS` | `Foundation-0/formal-claims-audit#19 @ f9f3e430` | `C1` Clause 2, `R1`, `A1`/`A4` | `all(...)` on `[]` returns `True` vacuously | Rejected (`FCA19_EMPTY_VERDICTS`) |

---

## 6. Verification & Hardening Receipts (`AUDIT-114R`)

- **4-Mode Isolated `-I` Standalone Parity (`-I -B`, `-I -O -B`, `-I -B -W error`, `PYTHONHASHSEED=42 -I -B`):**
  - `zone_sylvester_certificate.json` SHA-256: `190ceeae4f1c00707e2fca42a5286669371dcdfd447debc04e1d911644ff297e`
  - `payload_sha256`: `2408efb094056730a05757b32a6ba3249ef424d74bf321315f1bedd280639279`
  - `certificate_sha256` (unterminated canonical bytes): `465b4a3b46d44856305e264ef6befdb0a111653c85d296434688e5a1de86919c`
  - `--check zone_sylvester_certificate.json`: `OK` across all 4 modes; `test_zone_sylvester_r5.py`: `6/6 OK` across all 4 modes.
- **Live `aletheia v2.0.0 mutate --max-mutants 0 --add-cwd` (`-I -O -B`):**
  - `zone_sylvester_oracle.py`: **`94/94` (`100.0%`) KILLED**, `0` survived, `truncated=False`.
  - `zone_sylvester_audit.py`: **`14/14` (`100.0%`) KILLED**, `0` survived, `truncated=False`.
  - **Combined:** **`108/108` (`100.0%`) KILLED**, `0` survived.
- **Exhaustive AST `BoolOp` (`and` $\leftrightarrow$ `or`) Sweep (`-I -O -B`):**
  - `zone_sylvester_oracle.py`: **`34/34` (`100.0%`) KILLED**, `0` survived.
  - `zone_sylvester_audit.py`: **`2/2` (`100.0%`) KILLED**, `0` survived.
  - **Combined:** **`36/36` (`100.0%`) KILLED**, `0` survived.
- **Static & Safety Hygiene (`aletheia v2.0.0 audit-check --strict-ancestors --safety-scan`):** `PASS` (`5` files, `3` `.py`, `1` `.json`, `0` bare asserts, `0` leaks, `0` CRLF, `0` `__pycache__`, `0` safety findings).
- **`AUDIT-114R` Hardening Summary (`S17-BUG-01..06` + Zone-B Closure):**
  1. `S17-BUG-01` (`d_block_inertia_q`): Enforces strict non-empty square `list`/`tuple` (`<= MAX_MATRIX_DIM`), `type(entry) is Fraction`, and symmetry `D[i][j] == D[j][i]` before band/block analysis.
  2. `S17-BUG-02` (`block_2x2_inertia_q`): Enforces strict `type(a) is Fraction and type(b) is Fraction and type(c) is Fraction` (blocks `float`, `NaN`, `bool`, `int`, `None`, `str`).
  3. `S17-BUG-03` (`verify_pldl_certificate_q` & `verify_certificate_dict`): Rejects non-`str` dict keys (`CERT_NON_STRING_KEY`) before any `sorted(...)` call.
  4. `S17-BUG-04` (`verify_certificate_dict` / CLI `--check`): Compares `hmac.compare_digest(computed_sha, expected["payload_sha256"])` over canonical `v2.1` bytes instead of Python `==`, blocking re-signed `bool`-as-`int` (`True == 1` / `False == 0`) forgeries.
  5. `S17-BUG-05` (`_check_max_depth` & iterative `_check_exact_v21_obj`): Enforces iterative `MAX_JSON_DEPTH = 64` across all 4 parsers/encoders (`parse_zone_canon_v0`, `parse_aletheia_strict_nofloat`, `encode_zone_canon_v0`, `canonical_json_bytes_v21`) plus `MAX_V21_INT_BITS = 14000` (`V21_INT_TOO_LARGE`) — cleanly blocking depth-`65`/`1200` JSON inputs, cyclic object graphs, and `10**5000` integers with typed `Audit114Error` (`0` `RecursionError` / `ValueError`), alongside strict 64-lowercase-ASCII-hex checking (`INVALID_PAYLOAD_SHA`) before `hmac.compare_digest`.
  6. `S17-BUG-06` (`UPSTREAM_PINS["Foundation-0/formal-claims-audit#19"]`): Pinned to exact `scripts/check_verdicts.py` SHA-256 `44ebb34710d67bcbfb751e564cbae5aaf0a7911c1be3ba12cdbcbecd955f1815` at `f9f3e4307cbbb17fa62ff339fa01eb6e3fcb25d0`.
  7. `S17-BUG-07` (`AUDIT-114R3`, `zone_sylvester_oracle.py` `require_strict_int` / `_parse_zone_int` / `_encode_zone_val`): Replaced untrusted `{val}`/`{n}` decimal formatting in error messages with `bit_length()`, preventing raw Python `ValueError` (4,300-digit limit) on `encode_zone_canon_v0(±10**5000)` and `require_strict_int(±10**5000, ...)`.

### Reproduce
```bash
for flags in "-I -B" "-I -O -B" "-I -B -W error"; do
  python3 $flags zone_sylvester_audit.py --check zone_sylvester_certificate.json
  python3 $flags test_zone_sylvester_r5.py
done
PYTHONHASHSEED=42 python3 -I -B zone_sylvester_audit.py --standalone --json | sha256sum
```
