# LAW-FORGE-009 — Measured Shannon entropy-cartridge and Stranger results

**Date:** November 5, 2026.

## Implementation outcomes

The new `motif.reason-cartridge.shannon-entropy.v1` implements *actual* binary Shannon entropy, rather than the `p(1-p)` binary disagreement/Gini score used by the prior `classical_entropy` method in LAW-FORGE-008. The source is version-pinned, observations remain exact, question proposals are typed and owner-executed, new synthetic responses make immutable updated cartridges, and changed source contracts HOLD. A strict local JSON-stdio gateway exposes **create / propose / ingest / predict / diagnose**.

The entropy cartridge reuses the existing `LAW-FORGE-008/learner.py` version-space and exact-memory engine and **does not import the hidden evaluator**. This is assimilation of established classical science, not original algorithm invention.

The `gap.py` proof engine can reduce a deliberately supplied inconsistent training evidence set for a four-input parity challenge to a mathematically checkable *minimal contradiction core* relative to the frozen 650-rule grammar. This proof is **relative to the limited library**, not a declaration of an unknown law.

## Development results — 10 authored source mechanisms × 2 seeds = 20 worlds

| Method | Independently review-eligible | HELD | Owner query-cost units | Covered heldout predictions | Wrong covered predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Portable Shannon entropy cartridge** | **6/20** | 14 | **119** | **1,536** | 0 |
| **Strong inherited 008 Gini/disagreement active learner** | **6/20** | 14 | **119** | **1,536** | 0 |
| Fixed owner-catalog inquiry | 7/20 | 13 | 480 | 1,615 | 0 |
| CART-like greedy decision tree | 5/20 | 15 | 480 | 1,118 | 0 |
| Exact lookup only | 0/20 | 20 | 480 | 0 | 0 |

## Separate evaluation — 10 authored mechanisms × five unused seeds = 50 worlds

| Method | Review-eligible | HELD | Owner query-cost units | Covered heldout predictions | Wrong covered predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Portable Shannon entropy cartridge** | **15/50** | 35 | **304** | **3,840** | 0 |
| **Strong inherited 008 Gini/disagreement learner** | **15/50** | 35 | **304** | **3,840** | 0 |
| Fixed owner-catalog inquiry | 16/50 | 34 | 1,200 | 3,667 | 0 |
| CART-like greedy decision tree | 14/50 | 36 | 1,200 | 3,082 | 0 |
| Exact lookup only | 0/50 | 50 | 1,200 | 0 | 0 |

The Shannon and Gini versions **tied across all reported measures** in both development and evaluation. The classical fixed-order policy admitted **one more world** in the frozen evaluation but used far more synthetic query units and covered fewer heldout configurations. The CART-like tree was less successful in this bounded challenge. Exact lookup correctly refused to extrapolate into disjoint heldout settings.

**`NO_METHOD_PROMOTION`**: there is no demonstrated advantage of real Shannon entropy over the inherited binary-disagreement/Gini learner in this small source suite. Nonetheless Shannon is now a **reusable portable, explicitly named classical skill** with evidence lineage, not just a mislabeled score.

## The Stranger test: important negative result

The three in-grammar source classes—single-bit, pairwise XOR, triple OR—are exactly the **15/50** cases where the entropy skill passed independent review. The other **35/50** cases were held, including conditional mux, four-way parity, four-input threshold, XOR of conjunctions, four-way AND, an inquiry/review shift and a context-dependent synthetic exception.

Neither Shannon entropy nor confidence in a single surviving program supplies evidence that the **true mechanism** is in the predeclared 650-rule hypothesis language. An independently reviewed contradiction blocks heldout predictions. Consequently **zero incorrect predictions among covered heldout cases must not be misreported as 100% correctness over 50 worlds**.

The automated active inquiry generated **zero training-detected grammar-gap certificates across all 50 final worlds**. This is a meaningful limitation: the classical selector stops once a single candidate remains, which can happen before enough contradictory evidence has been collected to refute an **out-of-grammar** actual source. A separate adversarial test demonstrated `gap.py` detects and checks a minimal contradictory witness core when sufficient owner observations are supplied; **the active chooser did not elicit such cores automatically**.

**Next exact scientific challenge:** after a candidate is identified, reserve a separate source-owned *falsification/audit budget* and compare it fairly against a classical control with the same audit budget. Measure whether an active chooser can generate a contradiction core *without* accidentally inventing certainty. Do not alter the current frozen results retrospectively.

## Scope and provenance

The input domain contains 4,096 twelve-bit settings. Each trial starts with four training observations, offers 128 query cards under a maximum 24-source-cost budget and keeps **192 independent review + 256 disjoint heldout test input configurations** unavailable during training. The worlds are **separately packaged but all human-authored by the research team**, not independently sourced external phenomena. The source's risk and query-cost tags are synthetic, and uniform weighting over surviving rules is not a calibrated physical probability.

No native ALEX, GRAFT, Dogram, CANNON, reLATTE or live Question Machine runtime was called. The executable `desk.py` is strictly local and proposal-only; portable packet checksums identify bytes, not the independent identity of a source owner, permission or historical truth. No automatic promotion, branch merge or deployment occurred.

**Verified successful dedicated GitHub Actions run:** [LAW-FORGE-009 Shannon Entropy Cartridge & Stranger, run #5](https://github.com/the-static-collective/MOTIF/actions/runs/42098998531) on tested source commit `5cd4323a920ac1bc09b1fc15a1871739f31b8511`. All **159 automated tests passed** across nine suites: 139 inherited LAW-FORGE-001..008 tests plus 20 new LAW-FORGE-009 adversarial tests. The benchmark, source-version-bound portable entropy cartridge and actual owner-execution-required question proposal are preserved in the [`law-forge-009-entropy-stranger-receipts` CI artifact](https://github.com/the-static-collective/MOTIF/actions/runs/42098998531/artifacts/13448029182), retained through December 5, 2026. An earlier CI attempt failed in the sample artifact step due to a standalone evaluator import-order path issue; that issue was corrected, and this later full workflow succeeded.
