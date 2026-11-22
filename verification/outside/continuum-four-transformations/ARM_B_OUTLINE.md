# Arm B outline: does the best fixed description always leave a structured remainder?

Status: outline only. This is not a pre-registration. It sketches how the project's working hypothesis could be pre-registered later, using the same files, nets and controls as `PREREG.md`.

The hypothesis says that reality is a continuum and that fixed classes and structures always miss part of it. A measurable form: for a rich raw series, the best description from any fixed, finite model class leaves a remainder that is not noise.
"Not noise" means that the remainder has structure that recurs in data the model never saw, that the structure is absent in surrogates and in generated series of known finite order, and that it does not vanish as the model class grows.

Sketch of a plan:

1. A ladder of fixed descriptions, each richer than the last, fixed in advance. For example: spectrum and value distribution (the IAAFT class), then Markov models on ordinal patterns of order d = 3, 4, 5, 6, then the same with longer memory. Each rung is fitted on fit data only.
2. The remainder score at each rung is the held-out gain in prediction (log-loss per sample, compared with the rung below) on verdict data.
3. Under the hypothesis, held-out gain stays above the null at every rung the data can support. Under the alternative, it falls to the null level after some finite rung.
4. Controls. Generated series of known finite order must show the gain reaching the null at their true order. Generated long-memory series must keep a gain. IAAFT surrogates of the real series must show no gain above the first rung.
5. The finite-sample trap (anti-pattern CS-09 in the method). With finite data every ladder ends, because high rungs cannot be estimated. So the claim that can be tested is "a remainder survives up to the highest rung the data support". The highest supported rung must be fixed in advance from sample size alone, for example the largest d with at least 50 windows per pattern on average.
Note added with Amendment 1: on one 4,096-sample segment that rule allows order 4 at most (order 5 needs 6,000 windows), and order-6 transitions need 216,000 windows against 131,072 in 32 pooled segments. Whether rungs are fitted per segment or on pooled segments must be fixed in Arm B's own pre-registration.
6. Nets and sameness as in `PREREG.md`: the remainder must survive changes of sampling rate, quantization, window and instrument, and its profile across rungs can be tested for sameness between instruments with the same transfer test.

A result where the remainder vanishes at a finite rung in a calibrated instrument would count against the hypothesis at that scope. A surviving remainder would show only that these model classes are not enough, not that no fixed structure could be.

Note added with Amendment 1: Aletheia version 2.0.0 (a branch under review) requires a remainder test of this kind to project both training and unseen series orthogonally onto the complement of each model in a nested ladder (OTF-TIGHT-02), so that a structured remainder is not confused with plain misspecification of one model. Arm B's own pre-registration will use that form.
