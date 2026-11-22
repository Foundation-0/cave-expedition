# The eight glyphs of the Aletheia calculus

Source: `aletheia/aletheia/calculus.py` (2079 lines, version 1.3) at Foundation-0/aletheia PR #1, head `aa471867b21a0645c3290dea55c46b9732765ae9`. The module docstring lists the eight glyphs at lines 9 to 16. Each glyph has a registry entry (definition text in the `exact_semantics` field) and a function whose docstring states the formula. A glyph is read as adding something beyond its standard construct only if its definition contains a rule, input or output that the construct does not have.

| Glyph | Code name | Standard construct | Registry line, function line | Adds something beyond the construct? |
|---|---|---|---|---|
| ⧄ | OP-01 `schur_pushforward` | Schur complement with the Moore-Penrose pseudoinverse | 133, 762 | No |
| ⧅ | OP-02 `dark_mode_shadow` | Kernel of a matrix block, plus the cross-block map restricted to that kernel and its rank. The definition is a tuple of these standard objects | 160, 781 | No |
| ⦷ | OP-03 `holonomy_unmask` | Difference of two Schur complements (boundary response maps) of a signed and an unsigned graph Laplacian | 188, 800 | No new construct. It adds a restriction: sign flips must lie off the boundary (line 806) |
| ⟠ | OP-04 `observer_equalizer` | Reynolds average over a finite group, or the constant term of a regulated sum | 216, 827 | No new rule. One glyph covers these two different constructs. The regulated-sum case is limited to k=1 (line 865) |
| ⧇ | OP-05 `cohom_obstruction` | Harmonic energy divided by total energy of a graph 1-cochain (Hodge decomposition) | 243, 875 | No. The value for the zero cochain is set to 0 by convention (lines 881 to 882) |
| ⦺ | OP-06 `krein_inertia` | Sylvester inertia, the counts (n_+, n_0, n_-) of positive, zero and negative eigenvalues | 270, 898 | No |
| ⩩ | OP-07 `exact_null_equiv` | Equality of exact rationals, matrices or integer triples | 297, 904 | No. It adds a restriction: floating-point input raises an error |
| ⫩ | OP-08 `r5_refusal_gate` | Mutation testing from software engineering: a test passes if it accepts the target and rejects every mutant | 325, 919 | Yes, in one part. The output is a pair (pass flag, kill ratio), and the kill ratio is a rational in [0, 1] (line 324, and `GateResult.kill_ratio` at lines 754 and 930). The pass condition needs ratio 1 |

Checks on the table:

- Seven of the eight glyphs have no part of their definition that the named construct lacks, apart from the input restrictions noted.
- ⫩ is the only glyph with a graded output. ⟠ and ⫩ are the two whose constructs come from outside linear algebra.
- A lexer, parser and evaluator exist (`tokenize` line 961, `Parser` line 1023, `eval_expr` line 1236). Inputs are exact rationals, integer matrices, weighted graphs and cocycles.
- No function in the module reads a file or a measured series. Search: `grep -nE "open\(|read_text|read_bytes|csv|json\.load|np\.load" aletheia/calculus.py` gave no hits. The only `float(` calls are at lines 1748 to 1754, inside the C5 comparison against floating point.
- The team's own text gives the same account of the purpose: "the same eight exact algebraic operations recur with no standard collision-free notation" (`THEORY.md` line 86).
