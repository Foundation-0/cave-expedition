# Independent Adversarial Verification Checks Index (`check_001` – `check_062`)

Clean-room, zero-shared-code adversarial verification scripts executed by `@verifier` across Wave 1 and Wave 2 (`AUDIT-001` through `AUDIT-071R`, `62` scripts total).
Wave 1 checks `check_001`–`check_014` are mirrored verbatim under [`checks/`](checks/); Wave 2 checks `check_015`–`check_062` are indexed below by SHA-256 and exact coverage (corresponding standalone domain code lives in its respective `Foundation-0/*` / `siliconcordat/*` / `Moissanite-Labs/*` Draft PRs).

| Check Script | Lines | SHA-256 (first 16 hex) | Mirrored Here | Summary / Docstring |
|---|---:|---|---|---|
| `check_001_lemma32_and_tcb.py` | 463 | `d7e6f446ac6d9724` | [`checks/check_001_lemma32_and_tcb.py`](checks/check_001_lemma32_and_tcb.py) | Audit 001: Independent Exact-Rational Verification of Generalized Lemma 3.2 (S2:F[62,96]) |
| `check_002_session1_instruments.py` | 269 | `285606da23646cb0` | [`checks/check_002_session1_instruments.py`](checks/check_002_session1_instruments.py) | Audit 002: Negative Controls & Adversarial Defect Audit for Session 1 Code Blueprints |
| `check_003_seam01_ropt.py` | 733 | `ae239507fecea4fd` | [`checks/check_003_seam01_ropt.py`](checks/check_003_seam01_ropt.py) | Audit 003: Independent Exact Complex-Hermitian Verification of SEAM-01 (R_opt) |
| `check_004_continuum_bridge_suite.py` | 505 | `dd028c9d0bcf72f9` | [`checks/check_004_continuum_bridge_suite.py`](checks/check_004_continuum_bridge_suite.py) | Audit 004: Independent Adversarial Audit of All 4 continuum-bridge Instruments (#36): |
| `check_005_portal78.py` | 200 | `edc409ddd2a6296e` | [`checks/check_005_portal78.py`](checks/check_005_portal78.py) | Audit 005: Independent Adversarial Audit of Instrument 5 (`portal78_homotopy_bregman_bridge.py`, #39): |
| `check_006_fractals_deliverables.py` | 467 | `621d16d9d5e121c4` | [`checks/check_006_fractals_deliverables.py`](checks/check_006_fractals_deliverables.py) | Audit 006: Independent Zero-Shared-Code Adversarial Verification of fractals-probe Deliverables (#40): |
| `check_007_gravity_probes.py` | 746 | `77545be5a2056def` | [`checks/check_007_gravity_probes.py`](checks/check_007_gravity_probes.py) | Audit 007: Independent Zero-Shared-Code Adversarial Verification of gravity-probe (#44, #48): |
| `check_008_spectral_inertia.py` | 594 | `bd3c8d841e9db0d7` | [`checks/check_008_spectral_inertia.py`](checks/check_008_spectral_inertia.py) | Audit 008: Independent Zero-Shared-Code Adversarial Verification of spectral-prover (#56-#58): |
| `check_009_e8_spinor_fold.py` | 413 | `6fc42f8839b8cb80` | [`checks/check_009_e8_spinor_fold.py`](checks/check_009_e8_spinor_fold.py) | Audit 009: Independent Zero-Shared-Code Adversarial Verification of fractals-probe Deliverable 3 |
| `check_010_spectral_inertia_reaudit.py` | 141 | `7fdc893703877591` | [`checks/check_010_spectral_inertia_reaudit.py`](checks/check_010_spectral_inertia_reaudit.py) | Audit 010: Independent Re-Audit of spectral-prover commit dfc8516 (#63) closing AUDIT-015 & AUDIT-016. |
| `check_011_gravity_reaudit_and_probe4.py` | 330 | `f4ee13f78d3dfb04` | [`checks/check_011_gravity_reaudit_and_probe4.py`](checks/check_011_gravity_reaudit_and_probe4.py) | Audit 011: Independent Zero-Shared-Code Re-Audit of Patched Probe 1 & Probe 3 + Full Adversarial |
| `check_012_continuum_bridge_reaudit_and_fold_sheaf.py` | 592 | `59d2102d8d92fdcb` | [`checks/check_012_continuum_bridge_reaudit_and_fold_sheaf.py`](checks/check_012_continuum_bridge_reaudit_and_fold_sheaf.py) | Audit 012: Independent Zero-Shared-Code Adversarial Verification of `continuum-bridge` #70-#71: |
| `check_013_bw16_leech24.py` | 673 | `808eca5061a5d205` | [`checks/check_013_bw16_leech24.py`](checks/check_013_bw16_leech24.py) | Audit 013 (AUDIT-020): Independent Zero-Shared-Code Adversarial Verification of `fractals-probe` #81 |
| `check_014_bw16_leech24_reaudit.py` | 153 | `f5eb17aba96c45d3` | [`checks/check_014_bw16_leech24_reaudit.py`](checks/check_014_bw16_leech24_reaudit.py) | Audit 014 (AUDIT-020R): Independent Re-Audit of Patched `verify_bw16_leech24.py` (#96) |
| `check_015_aletheia_framework.py` | 519 | `6347e08a07e67bc5` | `indexed (domain PR)` | Audit 015 (AUDIT-022): Independent Adversarial Audit of `Foundation-0/aletheia` |
| `check_016_arm5_dynamics_cross.py` | 620 | `db904004a0b10acf` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Symbiosis Arm 5 (gravity-probe #151): |
| `check_017_arm4_agentic_research.py` | 325 | `daa3a50835df7ffd` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Symbiosis Arm 4 (peer-weaver #154): |
| `check_018_arm3_aletheia_mde.py` | 309 | `bdec40468d9259a2` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Symbiosis Arm 3 (spectral-prover #155): |
| `check_019_arm1_siliquant.py` | 280 | `635aced56c961c05` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Symbiosis Arm 1 (fractals-probe #157): |
| `check_020_arm2_soko.py` | 256 | `10f416d5b973690b` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Symbiosis Arm 2 (continuum-bridge #159): |
| `check_021_audit034_unified_mde_ratchet.py` | 195 | `ddba4d4222fbfeea` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 2 — AUDIT-034 (peer-weaver #180): |
| `check_022_audit030_aletheia_v11.py` | 528 | `b7440eb018adaba6` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 2 — AUDIT-030 (Foundation-0/aletheia v1.1): |
| `check_023_audit031_leech_shaping.py` | 337 | `134c23d99e92e7be` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 2 — AUDIT-031 (fractals-probe #187): |
| `check_024_audit032_scry_topp.py` | 302 | `fac081152414fb06` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 2 — AUDIT-032 (gravity-probe #186): |
| `check_025_audit033_weft_t5.py` | 349 | `106a916c5813403d` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 2 — AUDIT-033 (continuum-bridge #189): |
| `check_026_audit038_qwen_mistral_nous.py` | 358 | `f195e8f4e08dd381` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-038 (peer-weaver #223): |
| `check_027_audit039_cross_lab_spectral_eval.py` | 355 | `f9f94097dd1be036` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-039 (gravity-probe #225): |
| `check_028_audit037_tencent_zai.py` | 296 | `8b3cb532b7053660` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-037 (continuum-bridge #226): |
| `check_029_audit035_meta_dm_math.py` | 471 | `30d9bb766c510aaa` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-035 (fractals-probe #229): |
| `check_030_audit036_deepseek_openai.py` | 368 | `be25ff397a4c4878` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-036 (spectral-prover #231): |
| `check_031_audit040_aletheia_v12.py` | 221 | `9ac7a0b9c65e7361` | `indexed (domain PR)` | Independent adversarial verification for Wave 2 Round 3 — AUDIT-040 (`Foundation-0/aletheia` v1.2.0): |
| `check_032_audit043_observer_sheaf_mdr.py` | 234 | `edaf888ee1511890` | `indexed (domain PR)` | Independent zero-shared-code SymPy verification for Wave 2 Round 3B — AUDIT-043 (continuum-bridge #246): |
| `check_033_audit042_padic_btz_leech.py` | 247 | `01487b00565490ab` | `indexed (domain PR)` | Independent zero-shared-code SymPy verification for Wave 2 Round 3B — AUDIT-042 (fractals-probe #247): |
| `check_034_audit041_horizon_schur_modular.py` | 534 | `638d4c1b165dd34a` | `indexed (domain PR)` | check_034_audit041_horizon_schur_modular.py |
| `check_035_audit046_ramanujan_pgl2_mellin.py` | 461 | `178cf779e54a1f79` | `indexed (domain PR)` | check_035_audit046_ramanujan_pgl2_mellin.py |
| `check_036_audit048_ramanujan_web.py` | 302 | `359f138a98847293` | `indexed (domain PR)` | check_036_audit048_ramanujan_web.py |
| `check_037_audit044_ramanujan_btz_graphs.py` | 415 | `f5676a9ef0884b5d` | `indexed (domain PR)` | check_037_audit044_ramanujan_btz_graphs.py |
| `check_038_audit045_ramanujan_mock_shadows.py` | 446 | `a4255b3895144a32` | `indexed (domain PR)` | check_038_audit045_ramanujan_mock_shadows.py |
| `check_039_audit050_canculus_onco.py` | 254 | `7968837e5226e1a9` | `indexed (domain PR)` | check_039_audit050_canculus_onco.py |
| `check_040_audit047_hawking_theorem.py` | 512 | `5bb38f6afa3d9070` | `indexed (domain PR)` | check_040_audit047_hawking_theorem.py |
| `check_041_audit049_judegomila_zeta_dbn.py` | 339 | `eabdafd75bd64793` | `indexed (domain PR)` | check_041_audit049_judegomila_zeta_dbn.py |
| `check_042_audit051_operator_calculus.py` | 384 | `88a636c06fa6b846` | `indexed (domain PR)` | check_042_audit051_operator_calculus.py |
| `check_043_audit053_buckmaster_euler_cc.py` | 246 | `6931f6943121225b` | `indexed (domain PR)` | check_043_audit053_buckmaster_euler_cc.py |
| `check_044_audit052_buckmaster_fluid_lean.py` | 325 | `4dccb55654372d23` | `indexed (domain PR)` | check_044_audit052_buckmaster_fluid_lean.py |
| `check_045_audit054_double_slit.py` | 310 | `7fd4b9c008828409` | `indexed (domain PR)` | check_045_audit054_double_slit.py |
| `check_046_audit055_aletheia_v130.py` | 248 | `26b2917be0b83154` | `indexed (domain PR)` | check_046_audit055_aletheia_v130.py |
| `check_047_audit058_camail.py` | 564 | `b843eadef586ad19` | `indexed (domain PR)` | Independent zero-shared-code SymPy + live upstream verification for AUDIT-058 (CAMAIL). |
| `check_048_audit059_qwen_neuron_map.py` | 376 | `6d8dec1e3e7b17cc` | `indexed (domain PR)` | Independent zero-shared-code NumPy/SymPy + live upstream verification for AUDIT-059. |
| `check_049_audit057_alphaxiv_openresearch.py` | 318 | `08c959af20d9c7fb` | `indexed (domain PR)` | Independent live-repro + adversarial verification for AUDIT-057 (alphaxiv/OpenResearch + 4 siblings). |
| `check_050_audit060_alphaxiv_math_formal.py` | 352 | `69de7bbf4879b290` | `indexed (domain PR)` | Independent zero-shared-code SymPy + live upstream verification for AUDIT-060 (alphaXiv Math Formal). |
| `check_051_audit056_quantum_unification.py` | 436 | `dcf5d498e2555886` | `indexed (domain PR)` | Independent zero-shared-code SymPy torture test & pre-push package audit for AUDIT-056 (Foundation-0/quantum). |
| `check_052_audit062_warp_drive_runtime.py` | 789 | `bbbac8837eabdb26` | `indexed (domain PR)` | Independent adversarial verification & red-team audit for AUDIT-062 (Arm R6-2). |
| `check_053_audit065_weft_cross_audit.py` | 479 | `a0f43048a6585dfd` | `indexed (domain PR)` | Independent zero-shared-code verification & red-team audit for AUDIT-065 (Arm R6-5). |
| `check_054_audit064_warp_weight_iteration.py` | 462 | `bcc01689b58cd060` | `indexed (domain PR)` | Independent zero-shared-code SymPy + stdlib verification for AUDIT-064 (Arm R6-4). |
| `check_055_audit061_gram_cert.py` | 477 | `698229ece3ec69a8` | `indexed (domain PR)` | Independent zero-shared-code SymPy + stdlib verification & red-team audit for AUDIT-061 (Arm R6-1). |
| `check_056_audit063_bounded_controller.py` | 621 | `1968adfbfc9e4d67` | `indexed (domain PR)` | Independent zero-shared-code verifier & red-team audit for AUDIT-063 (Round 6 Arm R6-3). |
| `check_057_audit067_aletheia_v140.py` | 332 | `6223cbed90030a1e` | `indexed (domain PR)` | Independent zero-shared-code verifier & red-team audit for AUDIT-067 (aletheia v1.4.0). |
| `check_058_audit066_warp_drive_pra.py` | 461 | `b3daba08ff62d35e` | `indexed (domain PR)` | Independent zero-shared-code verifier & red-team audit for AUDIT-066 (warp-drive Draft PR-A). |
| `check_059_audit071_frobenius_sat.py` | 271 | `e3080a45fa025d37` | `indexed (domain PR)` | Independent zero-shared-code verifier & red-team audit for AUDIT-071 (Round 7 Arm R7-4). |
| `check_060_audit068_magnitude.py` | 458 | `9927a411a4a57956` | `indexed (domain PR)` | Independent zero-shared-code verification & adversarial red-team for AUDIT-068. |
| `check_061_audit069_openresearch_index.py` | 463 | `3dc1ceabc1587158` | `indexed (domain PR)` | Independent zero-shared-code verification & adversarial red-team for AUDIT-069. |
| `check_062_audit070_zenodo_rns_pnp.py` | 424 | `04165a0959823443` | `indexed (domain PR)` | Independent zero-shared-code verification & adversarial red-team for AUDIT-070. |
