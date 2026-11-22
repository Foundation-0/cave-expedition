# Prior-work sources behind the labels

This file names the five sources that the labels in [`OUTSIDE_AUDIT.md`](OUTSIDE_AUDIT.md) and the reasons in [`rulings.json`](rulings.json) lean on. For each one it gives the title, venue, year, an identifier, the theorem, lemma or section that was used, and what was actually read. Where we could not name a source properly, or the text we read was a copy, it says so.

Each identifier was fetched on 2026-11-22 from its public page or from Crossref to check that it resolves to the stated title and authors. A page that refused an automated request is marked.

## 1. Borcea and Streinu, section 7

- **Title and venue.** C. S. Borcea and I. Streinu, "Periodic tilings and auxetic deployments", *Mathematics and Mechanics of Solids* 26(2), 199 to 216, 2021. Published online 24 August 2020.
- **Identifier.** DOI 10.1177/1081286520948116. Crossref returns this title, these authors, volume 26, issue 2, pages 199 to 216. The publisher page refused an automated request (HTTP 403), so the check rests on Crossref and on the repository records below.
- **What was used.** Section 7, "A glimpse into higher dimensions", on pages 15 and 16 of the 18-page copy we read, with its Figure 12 and the unnumbered Remark that gives the cycle `e1 -> e2 -> ... -> ed -> -e1 -> ... -> -ed -> e1`. The section describes a body-and-bar structure with two orbits of congruent regular cross-polytopes, connecting bars twice the edge length, and a folding motion imagined in dimension three. It gives no formula and no proof.
- **What was read, and from where.** The advocate read section 7 in full. The evaluator could not. The text read is a copy from the Wayback Machine, snapshot of 9 July 2024, of the Smith ScholarWorks file `viewcontent.cgi?article=1262&context=csc_facpubs`. It is the journal-formatted article. Smith ScholarWorks lists the paper under two records, `csc_facpubs/313` and `csc_facpubs/261`. Both resolve and carry the same title. We did not compare the copy with the publisher's own PDF.
- **What rests on it.** This is the only reason the `F_8` to `E_8` fold keeps `N2` (ruling folds-dn-e8 F1a). The label is medium confidence. Conway and Sloane's *Sphere Packings, Lattices and Groups* and the Fischer, Koch and Sowa papers were not read.

## 2. Knausgard, Lemma 6.1

- **Title and venue.** K. M. Knausgard, "More than 83.9% of the zeros of the Riemann zeta function are distinct and more than 67.35% are simple and on the critical line". A preprint, arXiv math.NT, submitted 6 October 2026. The arXiv page shows no journal reference.
- **Identifier.** arXiv:2610.08965v1. The page resolves with this title and the author name Knausgard, Kristian Muri.
- **What was used.** Lemma 6.1, "threshold with two levels": for `P` positive semidefinite, `Q` Hermitian with at most `p` positive eigenvalues, `A = P + Q` and real `t >= c`, `tr A^2 >= tr phi_c(P) + 2t (tr A - tr P) - t^2 p`. Lemma 2.1 is the case `t = c`. Lemma 2.1 cites Lemma 4 of the same author's arXiv:2609.33043, "More than 83.69% of the zeros of the Riemann zeta function are distinct".
- **What was read.** The advocate read Lemmas 2.1 and 6.1 and matched Lemma 6.1 to our family symbol by symbol (his `t` is our `C`, his `p` is our `b`). The first pass did not read the paper in full, and nobody on our side read the rest of it.
- **Related source.** L. Alpoge and R. Furman, "More than two thirds of the zeta zeros are simple and on the critical line", arXiv:2608.13637, version 2 read, submitted 13 August 2026. Lemma 3.2 (rank-trace inequality) and Remark 3.3 were read in full by the advocate. The heading of our copy words the title slightly differently from the arXiv listing. The listing is quoted here.

## 3. Baron, Matkowski and Nikodem 1994

- **Title and venue.** K. Baron, J. Matkowski and K. Nikodem, "A sandwich with convexity", *Mathematica Pannonica* 5(1), 139 to 144, 1994.
- **Identifier.** EuDML `urn:eudml:doc:223256` (https://eudml.org/doc/223256), zbMATH Zbl 0803.39011. The EuDML page resolves with this title, these authors and these pages.
- **What was used.** The convex separation theorem, taken for a convex subset `D` of a real vector space and functions `f, g : D -> R`: a convex separator exists if and only if `f(sum t_k x_k) <= sum t_k g(x_k)` for all finite convex combinations, and if the space has finite dimension `m`, combinations of at most `m + 1` points suffice. We have no theorem number for it.
- **What was read.** Not the paper. EuDML holds no full text, and the full-text link it gives refused our automated request (HTTP 403). The advocate also found no copy at the EMIS mirror.
- **Where the statement came from.** It was read as quoted in the introduction of M. Bessenyei, D. Cs. Kertesz and R. L. Lovas, "A sandwich with segment convexity", arXiv:2009.13400v1, 28 September 2020 (the page resolves). There the theorem is called "Theorem" without a number, and its inequality is displayed as (1) of that paper, not of the 1994 one.
- **What follows from this.** The four-ray test for four points is a corollary of the quoted statement after a short padding or convex-minorant step. It is not the literal statement. Theorem B of AUDIT-010 sits at `N0` as a reading of a quoted theorem. Nobody read the 1994 proof.

## 4. L'vov and co-authors 1998

- **Title and venue.** V. S. L'vov, E. Podivilov, A. Pomyalov, I. Procaccia and D. Vandembroucq. The arXiv preprint is titled "An optimal shell model of turbulence". The journal version is titled "Improved shell model of turbulence", *Physical Review E* 58, 1811 to 1822, 1998.
- **Identifier.** arXiv:chao-dyn/9803025 (resolves, and lists DOI 10.1103/PhysRevE.58.1811). Crossref confirms the DOI, the journal title, volume 58 and pages 1811 to 1822.
- **What was read.** Version 2 of the preprint, dated 9 April 1998 and marked "in press", in full. We did not compare it with the journal text, so the equation numbers below are those of the preprint and may differ in print.
- **What was used.**
  - Equation (16) gives the third-order structure function of the GOY shell model and shows period-two oscillations when `c/a < 0`. They come from a non-zero flux of the second invariant. Equations (17) and (20) give the forcing under which that flux vanishes and the oscillations disappear.
  - Equations (29) to (31) and the text around them say the Sabra model has only diagonal second-order correlations and one third-order function coupling three consecutive shells, while GOY has correlations between shells separated by multiples of three. This is the basis for "Sabra has no period-3 mechanism by construction".
- **What rests on it.** The sentence in section 3 of `OUTSIDE_AUDIT.md` about period 3, and the ruling zerolog F4.

## 5. Greene, and the restricted least squares sources actually read

The earlier text of our audit and one ruling pointed to "Greene, Econometric Analysis". Nobody on our side read that book. That citation is withdrawn. What was read is below.

- **Greene's lecture slides.** W. Greene, "Econometrics I, Part 5: Regression Algebra and Fit, Restricted Least Squares", lecture slides, Stern School of Business, New York University, 36 slides, PDF dated 25 July 2017.
  - Slide 5-33 gives the restricted solution `b* = b - (X'X)^-1 R' [R (X'X)^-1 R']^-1 (Rb - q)`.
  - Slide 5-34 names `Rb - q` the discrepancy vector.
  - We hold the PDF but did not record the address it came from, so we cannot give an identifier that resolves. Anyone who wants to check it should search for the title.
- **The notes that carry the residual-sum formula.** "Restricted LS", two pages of lecture notes dated 27 November 2018, at https://ruc-econ.github.io/Lecture_Notes/PG_econometrics/Restricted_LS.pdf. The file names no author. The address resolves and returns the PDF.
  - Page 2 displays `RSS_r = RSS_ur + (R b - r)' [R (X'X)^-1 R']^-1 (R b - r)`, which is the formula the ruling twoloop-stack F1 matches symbol by symbol. The formula has no equation number.
- Both documents above were read in full.
- **What follows from this.** The identity is restricted least squares, which is standard, and the two documents above are enough to check the match. Any citation of the textbook should wait until someone reads it.

## Sources used for a label but not read in full

These appear in `OUTSIDE_AUDIT.md` and are named here so nobody takes them as checked. Conway and Sloane's *Sphere Packings, Lattices and Groups* and the Fischer, Koch and Sowa papers on lattice and framework motions were not read. A search in the jitterbug, lattice-deformation and framework literature is a bounded search, and a missing match is weak evidence.

The first-pass evaluator's reading folder for the sandwich theorem held a review, F. C. Mitroi-Symeonidis, "Convexity and sandwich theorems", *European Journal of Research in Applied Sciences* 1(1), 9 to 11, 2015. We did not check its identifier.
